#!/usr/bin/env python3
"""
141_findver_translation_review.py
Assembles one FinDVer translation batch and builds the researcher's review workbook (K-024).

Inputs per batch (data/findver/batches/):
  batch_XX_text.json    {"paragraphs": {evidence_id: Turkish text}, "claims": {claim_id: Turkish text}}
  batch_XX_tables.json  {"tables": {evidence_id: {source segment: Turkish segment}}}
Tables are not retyped: every text cell / text line of the source table is replaced by its Turkish segment,
so the "|" structure and every number stay byte-identical to the source.

Checks: every evidence element and claim of the batch is translated; every text segment of a table has a
translation; digit sequences match between source and Turkish (paragraphs, assembled tables, claims).

Output: data/findver/batches/batch_XX.json (assembled), data/findver/review/batch_XX_kontrol.xlsx
        (never overwritten; _v2, _v3 … instead)
Usage: python scripts/141_findver_translation_review.py 1 [--check]   (--check: print warnings only, no files)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
FV = ROOT / "data" / "findver"
LETTERS = re.compile(r"[A-Za-z]{2,}")


def digits(text: str) -> Counter:
    return Counter(re.findall(r"\d+", text))


def assemble_table(src: str, seg: dict[str, str]) -> tuple[str, list[str]]:
    missing, out = [], []
    for line in src.split("\n"):
        if line.lstrip().startswith("|"):
            cells = []
            for cell in line.split("|"):
                s = cell.strip()
                if LETTERS.search(s):
                    if s in seg:
                        cell = cell.replace(s, seg[s], 1)
                    else:
                        missing.append(s)
                cells.append(cell)
            out.append("|".join(cells))
        else:
            s = line.strip()
            if LETTERS.search(s):
                if s in seg:
                    line = line.replace(s, seg[s], 1)
                else:
                    missing.append(s)
            out.append(line)
    return "\n".join(out), missing


def digit_warn(src: str, tr: str, label: str) -> list[str]:
    if digits(src) == digits(tr):
        return []
    a, b = digits(src), digits(tr)
    return [f"{label}: sayılar farklı — kaynakta fazla {sorted((a - b).elements())}, çeviride fazla {sorted((b - a).elements())}"]


def main() -> None:
    n = int(sys.argv[1])
    src = json.loads((FV / "findver_source.json").read_text(encoding="utf-8"))
    plan = json.loads((FV / "batch_plan.json").read_text(encoding="utf-8"))["batches"][n - 1]
    text = json.loads((FV / "batches" / f"batch_{n:02d}_text.json").read_text(encoding="utf-8"))
    tables = json.loads((FV / "batches" / f"batch_{n:02d}_tables.json").read_text(encoding="utf-8"))["tables"]
    ev = {e["evidence_id"]: e for e in src["evidence"]}
    claims = [c for c in src["claims"] if c["report"] in plan]
    needed = list(dict.fromkeys(k for c in claims for k in c["evidence"]))

    evidence_tr, warn_ev = {}, {}
    for k in needed:
        e, w = ev[k], []
        if e["type"] == "table":
            tr, missing = assemble_table(e["text"], tables.get(k, {}))
            w += [f"tabloda çevrilmemiş parça: {m[:60]}" for m in missing]
        else:
            tr = text["paragraphs"].get(k, "")
            if not tr.strip():
                w.append("çeviri yok")
        w += digit_warn(e["text"], tr, "kanıt")
        evidence_tr[k] = tr
        warn_ev[k] = w

    check_only = "--check" in sys.argv
    out = {"batch": n, "evidence": evidence_tr,
           "claims": {c["claim_id"]: text["claims"].get(c["claim_id"], "") for c in claims}}
    if not check_only:
        (FV / "batches" / f"batch_{n:02d}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    wb = Workbook()
    ws = wb.active
    ws.title = f"parti_{n:02d}"
    ws.append(["İddia no", "Rapor", "Kaynak iddia", "Türkçe iddia", "Kanıt (kaynak)", "Kanıt (Türkçe)",
               "Otomatik uyarı", "Sorun / not"])
    seen, n_warn = {}, 0
    for c in claims:
        tr_claim = out["claims"][c["claim_id"]]
        warn = ["iddia: çeviri yok"] if not tr_claim.strip() else digit_warn(c["statement"], tr_claim, "iddia")
        src_parts, tr_parts = [], []
        for k in c["evidence"]:
            label = f"[{ev[k]['type']} {k.split('#')[1]}]"
            if k in seen:
                src_parts.append(f"{label} (aynı kanıt: {seen[k]})")
                tr_parts.append(f"{label} (aynı kanıt: {seen[k]})")
            else:
                seen[k] = c["claim_id"]
                src_parts.append(f"{label}\n{ev[k]['text']}")
                tr_parts.append(f"{label}\n{evidence_tr[k]}")
                warn += [f"{label} {w}" for w in warn_ev[k]]
        n_warn += bool(warn)
        ws.append([c["claim_id"], c["report"].removesuffix(".json"), c["statement"], tr_claim,
                   "\n\n".join(src_parts)[:32000], "\n\n".join(tr_parts)[:32000], "\n".join(warn), ""])
        if warn and check_only:
            print(c["claim_id"], "|", " || ".join(warn))
        if warn:
            ws.cell(ws.max_row, 7).fill = PatternFill("solid", fgColor="FFE699")
    for col, w in zip("ABCDEFGH", (18, 22, 45, 45, 60, 60, 35, 25)):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "C2"
    if check_only:
        print(f"check: {len(claims)} iddia, {len(needed)} kanıt; uyarılı satır {n_warn}")
        return
    rev = FV / "review"
    rev.mkdir(exist_ok=True)
    path = rev / f"batch_{n:02d}_kontrol.xlsx"
    k = 2
    while path.exists():
        path = rev / f"batch_{n:02d}_kontrol_v{k}.xlsx"
        k += 1
    wb.save(path)
    extra = set(text["paragraphs"]) - set(needed)
    print(f"{path.name}: {len(claims)} iddia, {len(needed)} kanıt; uyarılı satır {n_warn}"
          + (f"; partide fazladan paragraf {sorted(extra)}" if extra else ""))


if __name__ == "__main__":
    main()
