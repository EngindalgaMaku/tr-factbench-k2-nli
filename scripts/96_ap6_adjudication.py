#!/usr/bin/env python3
"""
96_ap6_adjudication.py — A ile B arasındaki uyuşmazlıklar için uzlaşma kaydı.

  python scripts/96_ap6_adjudication.py export
      data/ap6/annotation/excel/AP6_uzlasma.xlsx dosyasını üretir: her uyuşmazlık için soru, yanıt, hedef cümle, kaynak,
      A ve B etiketleri. Çekimser sınırındaki uyuşmazlıklarda kılavuzun yazılı kuralı önceden yazılır ("kural gereği").
      Sistem tahmini içermez.

  python scripts/96_ap6_adjudication.py import [--dry-run]
      Uzlaşılan etiketleri okur; reports/AP6_ADJUDICATION_v1.{md,jsonl} kaydını yazar. Uzlaşılan etiket A'nınkinden farklıysa
      labels_A.jsonl dosyasına source="adjudication" ile yeni kayıt ekler (eski kayıt silinmez). B'nin etiketleri değişmez;
      uyum (κ) uzlaşmadan önceki etiketlerle raporlanır (reports/AP6_IAA_v1.md).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
ANN = ROOT / "data" / "ap6" / "annotation"
XL = ANN / "excel" / "AP6_uzlasma.xlsx"
REP = ROOT / "reports"
CHOICES = ["çekimser", "supported", "partially_supported", "contradicted", "unverifiable"]
HEAD = ["Madde", "Soru", "Yanıt (hedef cümle kırmızı)", "Kaynak metin", "A", "B",
        "Uzlaşılan etiket", "Hata türü (supported değilse)", "Gerekçe", "Karar biçimi"]
ERRORS = {"ilişki uydurma": "relation_fabrication", "sayı / tarih": "number_date", "kapsam": "scope",
          "olumsuzluk": "negation", "bilgi ekleme": "added_information", "diğer": "other"}
ERRORS_INV = {v: k for k, v in ERRORS.items()}


def latest(p: Path) -> dict:
    d = {}
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            d[r["item_id"]] = r
    return d


def five(r: dict) -> str:
    return "çekimser" if r["abstention"] == "yes" else r["label"]


def export() -> None:
    A, B = latest(ANN / "labels_A.jsonl"), latest(ANN / "labels_B.jsonl")
    items = {json.loads(l)["item_id"]: json.loads(l)
             for l in (ANN / "items_B.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    wb = Workbook()
    ws = wb.active
    ws.title = "Uzlaşma"
    ws.append(HEAD)
    for c in ws[1]:
        c.font, c.fill = Font(bold=True), PatternFill("solid", fgColor="DDE6F0")
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for col, w in zip("ABCDEFGHIJ", [10, 28, 60, 80, 16, 16, 20, 16, 40, 14]):
        ws.column_dimensions[col].width = w
    red = InlineFont(b=True, color="C00000")
    n = 0
    for iid, it in items.items():
        a, b = five(A[iid]), five(B[iid])
        if a == b:
            continue
        n += 1
        rich = CellRichText()
        if it["answer_before"]:
            rich.append(it["answer_before"] + " ")
        rich.append(TextBlock(red, it["sentence"]))
        if it["answer_after"]:
            rich.append(" " + it["answer_after"])
        boundary = "çekimser" in (a, b)
        ws.append([iid, it["question"], None, it["context"], a, b, None, None, None,
                   "kural gereği" if boundary else "tartışma"])
        r = ws.max_row
        ws.cell(r, 3).value = rich
        if boundary:
            ws.cell(r, 9).value = ("Kılavuz: yalnızca kaynakta bilginin bulunmadığını söyleyen cümle çekimserdir; "
                                   "bilgi de içeren karışık cümle normal etiketlenir.")
        for c in ws[r]:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = min(409, max(90, 15 * (len(it["context"]) / 95 + 2)))
        for col in "GHI":
            ws[f"{col}{r}"].fill = PatternFill("solid", fgColor="FFF8E1")
    dv = DataValidation(type="list", formula1='"' + ",".join(CHOICES) + '"', allow_blank=True)
    de = DataValidation(type="list", formula1='"' + ",".join(ERRORS) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    ws.add_data_validation(de)
    dv.add(f"G2:G{n + 1}")
    de.add(f"H2:H{n + 1}")
    ws.freeze_panes = "B2"
    g = wb.create_sheet("Açıklama")
    for line in [
        "Uzlaşma — Anotatör A ve B birlikte doldurur. Sistem tahminleri bu aşamada da görülmez.",
        "G: uzlaşılan etiket; H: etiket supported veya çekimser değilse hata türü; I: kısa gerekçe (her satır için zorunlu).",
        "'Karar biçimi' = kural gereği olan satırlarda kılavuzun yazılı çekimser kuralını uygulayın.",
        "'tartışma' olan satırlarda kaynak metne birlikte bakıp karar verin; iki taraftan biri de olabilir, üçüncü bir etiket de.",
        "Uzlaşma sonucu A'nın etiketi değişirse eski kayıt silinmez; yeni kayıt 'adjudication' olarak eklenir.",
        "Uyum (κ) uzlaşmadan önceki etiketlerle raporlanır.",
    ]:
        g.append([line])
    g.column_dimensions["A"].width = 120
    XL.parent.mkdir(parents=True, exist_ok=True)
    wb.save(XL)
    print(f"Uzlaşma dosyası: {XL} ({n} uyuşmazlık)")


def import_(dry: bool) -> None:
    A = latest(ANN / "labels_A.jsonl")
    ws = load_workbook(XL, read_only=True)["Uzlaşma"]
    recs, new, problems = [], [], []
    for row in ws.iter_rows(min_row=2, values_only=True):
        iid, a, b, final, err, why, mode = row[0], row[4], row[5], row[6], row[7], row[8], row[9]
        if not iid:
            continue
        if final not in CHOICES or not (why or "").strip():
            problems.append(f"{iid}: uzlaşılan etiket veya gerekçe eksik")
            continue
        e = ERRORS.get(err) if err else None
        if final in ("supported", "çekimser"):
            e = None
        recs.append({"item_id": iid, "A": a, "B": b, "final": final, "error_type": e, "reason": why.strip(),
                     "mode": mode, "winner": "A" if final == a else ("B" if final == b else "üçüncü")})
        if final != five(A[iid]):
            new.append({"item_id": iid, "abstention": "yes" if final == "çekimser" else "no",
                        "label": None if final == "çekimser" else final, "error_type": e,
                        "note": f"Uzlaşma: {why.strip()}", "annotator": "A",
                        "saved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "source": "adjudication"})
    for p in problems:
        print("UYARI:", p)
    print(f"{len(recs)} karar okundu; A'nın etiketinin değiştiği madde: {len(new)}")
    if dry or problems:
        return
    (REP / "AP6_ADJUDICATION_v1.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    lines = ["# AP6 — Uzlaşma kaydı v1", "", "| Madde | A | B | Uzlaşılan | Lehine | Karar biçimi | Gerekçe |",
             "|---|---|---|---|---|---|---|"]
    lines += [f"| {r['item_id']} | {r['A']} | {r['B']} | {r['final']} | {r['winner']} | {r['mode']} | {r['reason']} |"
              for r in recs]
    (REP / "AP6_ADJUDICATION_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (ANN / "labels_A.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("Kayıt yazıldı: reports/AP6_ADJUDICATION_v1.{md,jsonl}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "import"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    export() if a.cmd == "export" else import_(a.dry_run)
