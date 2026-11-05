#!/usr/bin/env python3
"""
131_claimrag_translation_review.py
Builds the researcher's review workbook for one ClaimRAG-LAW translation batch (K-021).

One row per query: source and Turkish query, evidence (shown in full only at the first query that uses
it in the batch) and the claims as "source triple -> Turkish sentence" lines. Automatic checks are run
first and written into the "Otomatik uyarı" column, so the researcher reads the Turkish text and marks
only rows with a problem in "Sorun / not".

Checks: every chunk/query/claim of the batch is translated; digit sequences match between source and
translation; glossary terms present in the source have their fixed Turkish rendering.

Usage: python scripts/131_claimrag_translation_review.py 1
Output: data/claimrag_law/review/batch_XX_kontrol.xlsx (never overwritten; _v2, _v3 … instead)
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
LAW = ROOT / "data" / "claimrag_law"

# source pattern (lower-case regex) -> required Turkish substring (lower-case)
GLOSSARY = [
    (r"\bdata controller|\bcontroller", "veri sorumlu"),
    (r"\bprocessor\b", "veri işleyen"),
    (r"\bdata subject", "ilgili kişi"),
    (r"\bfree movement", "serbest dolaşım"),
    (r"\bfree flow", "serbest akış"),
    (r"\bprivacy", "gizlili"),
    (r"\bparental responsibility", "ebeveyn sorumluluğu"),
    (r"\bsupervisory authorit", "denetim makam"),
    (r"\bnatural person", "gerçek kişi"),
    (r"\bmember state", "üye devlet"),
    (r"\bconsent", "rıza"),
]


def digits(text: str) -> Counter:
    return Counter(re.findall(r"\d+", text))


def tr_lower(text: str) -> str:
    return text.replace("İ", "i").replace("I", "ı").lower()


def term_issues(src: str, tr: str) -> list[str]:
    s, t = src.lower(), tr_lower(tr)
    return [f"terim: '{want}' yok" for pat, want in GLOSSARY if re.search(pat, s) and want not in t]


def check(src: str, tr: str | None, label: str) -> list[str]:
    if not tr or not tr.strip():
        return [f"{label}: çeviri yok"]
    out = []
    if digits(src) != digits(tr):
        out.append(f"{label}: sayılar farklı {sorted(digits(src).elements())} / {sorted(digits(tr).elements())}")
    out += [f"{label}: {m}" for m in term_issues(src, tr)]
    return out


def main() -> None:
    n = int(sys.argv[1])
    src = json.loads((LAW / "law_source.json").read_text(encoding="utf-8"))
    batch = json.loads((LAW / "batches" / f"batch_{n:02d}.json").read_text(encoding="utf-8"))
    chunks = {c["chunk_id"]: c for c in src["chunks"]}
    # evidence translated in an earlier batch is reused, not translated again
    chunk_tr = {}
    for k in range(1, n + 1):
        f = LAW / "batches" / f"batch_{k:02d}.json"
        if f.exists():
            chunk_tr.update(json.loads(f.read_text(encoding="utf-8"))["chunks"])
    queries = [q for q in src["queries"] if q["query_id"] in batch["queries"]]
    missing_q = set(batch["queries"]) - {q["query_id"] for q in src["queries"]}
    if missing_q:
        raise SystemExit(f"unknown query ids in batch: {sorted(missing_q)}")

    wb = Workbook()
    ws = wb.active
    ws.title = f"parti_{n:02d}"
    head = ["Soru no", "Kaynak soru", "Türkçe soru", "Bağlam (kaynak)", "Bağlam (Türkçe)",
            "İddialar: kaynak → Türkçe", "Otomatik uyarı", "Sorun / not"]
    ws.append(head)
    seen, n_warn, n_claims = {}, 0, 0
    for q in queries:
        cid = q["chunk_id"]
        warn = check(q["query"], batch["queries"].get(q["query_id"]), "soru")
        if cid in seen:
            ctx_src, ctx_tr = f"(aynı bağlam: {seen[cid]})", f"(aynı bağlam: {seen[cid]})"
        else:
            seen[cid] = q["query_id"]
            ctx_src, ctx_tr = chunks[cid]["text"], chunk_tr.get(cid, "")
            if cid not in batch["chunks"] and ctx_tr:
                ctx_tr = "(önceki partide çevrildi)\n" + ctx_tr
            warn += check(ctx_src, chunk_tr.get(cid, ""), "bağlam")
        lines = []
        for i, c in enumerate(q["claims"], 1):
            tr = batch["claims"].get(c["claim_id"])
            triple = " | ".join(c["triple"])
            warn += check(triple, tr, f"iddia {c['claim_id'][-2:]}")
            lines.append(f"{c['claim_id'][-2:]}. {triple}\n    → {tr or '—'}")
            n_claims += 1
        n_warn += bool(warn)
        ws.append([q["query_id"], q["query"], batch["queries"].get(q["query_id"], ""), ctx_src, ctx_tr,
                   "\n".join(lines), "\n".join(warn), ""])
        if warn:
            ws.cell(ws.max_row, 7).fill = PatternFill("solid", fgColor="FFE699")

    for col, w in zip("ABCDEFGH", (12, 40, 40, 45, 45, 70, 30, 25)):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "C2"

    out_dir = LAW / "review"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"batch_{n:02d}_kontrol.xlsx"
    k = 2
    while out.exists():
        out = out_dir / f"batch_{n:02d}_kontrol_v{k}.xlsx"
        k += 1
    wb.save(out)
    extra = (set(batch["claims"]) - {c["claim_id"] for q in queries for c in q["claims"]}) | \
            (set(batch["chunks"]) - {q["chunk_id"] for q in queries})
    print(f"{out.name}: {len(queries)} soru, {len(seen)} bağlam, {n_claims} iddia; uyarılı satır {n_warn}"
          + (f"; partide fazladan anahtar {sorted(extra)}" if extra else ""))


if __name__ == "__main__":
    main()
