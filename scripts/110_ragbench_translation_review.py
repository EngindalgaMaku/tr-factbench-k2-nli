#!/usr/bin/env python3
"""
110_ragbench_translation_review.py
RAGBench medical slice (K-012): checks a translation batch against the English
source and writes a review workbook for the researcher.

Checks per sentence: every source key has a translation (and no extra keys);
the digits/numbers in the English and Turkish sentence are the same multiset;
negation cue counts are reported for a quick eye-check. Labels are not read.

Usage: python scripts/110_ragbench_translation_review.py 1
Output: data/ragbench/medical/review/batch_01_kontrol.xlsx
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
MED = ROOT / "data" / "ragbench" / "medical"
NUM = re.compile(r"\d+(?:[.,]\d+)?")
# List numbers glued to the end of response sentences by RAGBench's splitter ("... 1.") are dropped in Turkish (rule 5).
TRAIL_ENUM = re.compile(r"\s+\d+\.$")
NEG_EN = re.compile(r"\b(not|no|neither|nor|without|none|never|cannot)\b|n't", re.I)
NEG_TR = re.compile(r"(değil|yok|olmayan|olmadı|olmadığ|olmaz|madı|medi|mamış|memiş|maz\b|mez\b|mıyor|miyor|muyor|müyor|sız\b|siz\b|suz\b|süz\b|bulunmamak|hiçbir)", re.I)


def numbers(text: str) -> list[str]:
    return sorted(n.replace(",", ".") for n in NUM.findall(text))


def same_numbers(en: str, tr: str, is_response: bool) -> bool:
    """Equal number multisets; for response sentences a trailing list number in the
    English sentence may be missing from the Turkish one (it is dropped, rule 5)."""
    if numbers(en) == numbers(tr):
        return True
    return is_response and bool(TRAIL_ENUM.search(en)) and numbers(TRAIL_ENUM.sub("", en)) == numbers(tr)


def main(batch_no: int) -> None:
    batch = json.loads((MED / "batches" / f"batch_{batch_no:02d}.json").read_text(encoding="utf-8"))
    source = {json.loads(l)["item_id"]: json.loads(l) for l in (MED / "pmq75_source_en.jsonl").open(encoding="utf-8")}
    rows, problems = [], []
    for item_id, tr in batch["items"].items():
        src = source[item_id]
        rows.append((item_id, "soru", "-", src["question_en"], tr["question"]))
        en_docs = {s["key"]: s["en"] for doc in src["documents"] for s in doc}
        parts = [("belge", en_docs, tr["documents"])]
        parts += [(f"yanıt · {m}", {s["key"]: s["en"] for s in sents}, tr["responses"][m])
                  for m, sents in src["responses"].items()]
        for part, en_map, tr_map in parts:
            if set(en_map) != set(tr_map):
                problems.append(f"{item_id} {part}: anahtar uyuşmazlığı {sorted(set(en_map) ^ set(tr_map))}")
            for key, en in en_map.items():
                rows.append((item_id, part, key, en, tr_map.get(key, "")))

    wb = Workbook()
    ws = wb.active
    ws.title = f"Parti {batch_no:02d}"
    ws.append(["Madde", "Bölüm", "Anahtar", "İngilizce", "Türkçe", "Sayılar aynı mı?", "Olumsuzluk (EN/TR)",
               "KONTROL", "Düzeltme / not"])
    thin = Side(style="thin", color="BBBBBB")
    for item_id, part, key, en, tr in rows:
        same = same_numbers(en, tr, part.startswith("yanıt"))
        if not same:
            problems.append(f"{item_id} {part} {key}: sayılar farklı {numbers(en)} / {numbers(tr)}")
        neg = f"{len(NEG_EN.findall(en))}/{len(NEG_TR.findall(tr))}"
        ws.append([item_id, part, key, en, tr, "evet" if same else "HAYIR", neg, "", ""])
        r = ws.max_row
        for c in ws[r]:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if part.startswith("yanıt"):
            for c in ws[r][:5]:
                c.fill = PatternFill("solid", fgColor="FFF2CC")
        if not same:
            ws.cell(r, 6).fill = PatternFill("solid", fgColor="F4B084")
    for col, width in zip("ABCDEFGHI", [10, 26, 8, 60, 60, 10, 10, 12, 30]):
        ws.column_dimensions[col].width = width
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="C00000" if c.column >= 8 else "305496")
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = ws.dimensions
    dv = DataValidation(type="list", formula1='"uygun,düzeltilmeli"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"H2:H{ws.max_row}")

    out = MED / "review" / f"batch_{batch_no:02d}_kontrol.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite a workbook the researcher may already have marked.
    version = 2
    while out.exists():
        out = MED / "review" / f"batch_{batch_no:02d}_kontrol_v{version}.xlsx"
        version += 1
    wb.save(out)
    print(f"{len(rows)} satır -> {out}")
    print("Sorun yok." if not problems else "\n".join(problems))


if __name__ == "__main__":
    main(int(sys.argv[1]))
