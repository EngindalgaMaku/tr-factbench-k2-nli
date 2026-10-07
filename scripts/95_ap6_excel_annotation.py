#!/usr/bin/env python3
"""
95_ap6_excel_annotation.py — AP6 etiketlemesi için Excel çalışma kitabı üretir ve doldurulan kitabı geri okur.

  python scripts/95_ap6_excel_annotation.py export [--annotator A]
      data/ap6/annotation/excel/AP6_etiketleme_<A>.xlsx dosyasını üretir. Daha önce kaydedilmiş etiketler
      (labels_<A>.jsonl, her madde için son kayıt) önceden doldurulur. Dosya zaten varsa üzerine yazmaz.

  python scripts/95_ap6_excel_annotation.py import [--annotator A] [--dry-run]
      Excel'deki etiketleri doğrular ve yalnızca değişen ya da yeni maddeleri labels_<A>.jsonl dosyasına ekler
      (dosya yalnızca eklemeyle büyür; her madde için son kayıt geçerlidir — web arayüzüyle aynı kural).

Körlük: Kitapta yalnızca items_<A>.jsonl alanları (soru, yanıt, hedef cümle, bağlam, alan) bulunur.
Sistem tahmini, otomatik çekimserlik işareti ve seçilme nedeni yoktur (protokol §7).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
ANN = ROOT / "data" / "ap6" / "annotation"
XL_DIR = ANN / "excel"

LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
ERRORS = {"ilişki uydurma": "relation_fabrication", "sayı / tarih": "number_date", "kapsam": "scope",
          "olumsuzluk": "negation", "bilgi ekleme": "added_information", "diğer": "other"}
ERRORS_INV = {v: k for k, v in ERRORS.items()}
ABST = {"evet": "yes", "hayır": "no"}
ABST_INV = {v: k for k, v in ABST.items()}
DOMAIN_TR = {"finance": "finans", "legal": "hukuk", "medical": "sağlık"}

HEADERS = ["Sıra", "Madde", "Alan", "Soru", "Yanıt (hedef cümle kırmızı)", "Hedef cümle", "Kaynak metin (bağlam)",
           "1) Çekimser mi?", "2) Etiket", "3) Hata türü", "Not", "Durum"]
COL = {h: i + 1 for i, h in enumerate(HEADERS)}

KILAVUZ = [
    ("AP6 etiketleme — Excel ile çalışma", True),
    ("", False),
    ("Her satır bir yanıt cümlesidir. Yalnızca H–K sütunlarını doldurun; diğer sütunları değiştirmeyin.", False),
    ("Satırlar bilerek karışık sıradadır; aynı yanıtın cümleleri farklı yerlerde gelir.", False),
    ("", False),
    ("1) Çekimser mi?  (H sütunu)", True),
    ("evet  — Cümle YALNIZCA kaynakta bir bilginin bulunmadığını söylüyor. Etiket ve hata türü boş kalır.", False),
    ("hayır — Cümle bir bilgi aktarıyor. \"Kaynaklarda şu hüküm yer alıyor\" gibi cümleler de bu gruptadır.", False),
    ("Hem bilgi hem çekimserlik içeren karışık cümleler 'hayır' olarak işaretlenir ve normal etiketlenir.", False),
    ("", False),
    ("2) Etiket  (I sütunu — cümlenin söyledikleri, verilen kaynağa göre)", True),
    ("supported            — Cümlenin bütün önermeleri kaynakta destekleniyor.", False),
    ("partially_supported  — En az bir önerme destekleniyor, en az biri kaynakta yok ya da kaynakla çelişiyor.", False),
    ("contradicted         — Hiçbir önerme desteklenmiyor ve en az biri kaynakla açıkça çelişiyor.", False),
    ("unverifiable         — Önermeler kaynakta yok ya da kaynak karar vermeye yetmiyor; açık çelişki yok.", False),
    ("Genel bilgiye göre doğru olsa bile kaynakta dayanağı olmayan bilgi desteklenmiş sayılmaz.", False),
    ("", False),
    ("3) Hata türü  (J sütunu — yalnızca etiket supported DEĞİLSE)", True),
    ("ilişki uydurma, sayı / tarih, kapsam, olumsuzluk, bilgi ekleme, diğer", False),
    ("", False),
    ("Göndermeler", True),
    ("\"Bu düzenlemeler\", \"bu süre\" gibi ifadeleri E sütunundaki yanıtın tamamına bakarak çözün;", False),
    ("cümlenin söylediğini kaynakla karşılaştırarak etiketleyin.", False),
    ("", False),
    ("Kaydetme", True),
    ("Excel'i sık sık kaydedin. Bitirince ya da ara verdiğinizde Claude'a haber verin; etiketler", False),
    ("'import' komutuyla doğrulanıp labels_A.jsonl dosyasına aktarılır. Web arayüzünü aynı anda kullanmayın.", False),
    ("L sütunu (Durum) satır tamamlanınca 'tamam' olur; satır yeşile döner.", False),
]


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def latest_labels(annotator: str) -> dict[str, dict]:
    out = {}
    for r in read_jsonl(ANN / f"labels_{annotator}.jsonl"):
        out[r["item_id"]] = r
    return out


def export(annotator: str) -> None:
    items = read_jsonl(ANN / f"items_{annotator}.jsonl")
    labels = latest_labels(annotator)
    XL_DIR.mkdir(parents=True, exist_ok=True)
    out = XL_DIR / f"AP6_etiketleme_{annotator}.xlsx"
    if out.exists():
        sys.exit(f"{out} zaten var; üzerine yazılmadı. Önce 'import' çalıştırın, sonra dosyayı kaldırıp yeniden üretin.")

    wb = Workbook()
    ws = wb.active
    ws.title = "Etiketleme"
    ws.append(HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.fill = PatternFill("solid", fgColor="DDE6F0")
    widths = {"Sıra": 6, "Madde": 10, "Alan": 8, "Soru": 28, "Yanıt (hedef cümle kırmızı)": 60, "Hedef cümle": 38,
              "Kaynak metin (bağlam)": 80, "1) Çekimser mi?": 11, "2) Etiket": 20, "3) Hata türü": 15, "Not": 24,
              "Durum": 8}
    for h, w in widths.items():
        ws.column_dimensions[ws.cell(1, COL[h]).column_letter].width = w

    red = InlineFont(b=True, color="C00000")
    top = Alignment(wrap_text=True, vertical="top")
    for i, it in enumerate(items, start=2):
        rich = CellRichText()
        if it["answer_before"]:
            rich.append(it["answer_before"] + " ")
        rich.append(TextBlock(red, it["sentence"]))
        if it["answer_after"]:
            rich.append(" " + it["answer_after"])
        lab = labels.get(it["item_id"], {})
        row = [i - 1, it["item_id"], DOMAIN_TR.get(it["domain"], it["domain"]), it["question"], None,
               it["sentence"], it["context"],
               ABST_INV.get(lab.get("abstention"), None), lab.get("label"),
               ERRORS_INV.get(lab.get("error_type"), None), lab.get("note") or None, None]
        ws.append(row)
        ws.cell(i, COL["Yanıt (hedef cümle kırmızı)"]).value = rich
        h, k, j, e = (ws.cell(i, COL[x]).coordinate for x in ("1) Çekimser mi?", "2) Etiket", "3) Hata türü", "Durum"))
        ws.cell(i, COL["Durum"]).value = (f'=IF({h}="evet","tamam",IF(AND({h}="hayır",{k}<>"",'
                                           f'OR({k}="supported",{j}<>"")),"tamam",""))')
        for c in ws[i]:
            c.alignment = top
        ws.cell(i, COL["Hedef cümle"]).font = Font(bold=True, color="C00000")
        est = max(len(it["context"]) / 95, (len(it["answer_before"]) + len(it["sentence"]) + len(it["answer_after"])) / 70)
        ws.row_dimensions[i].height = min(409, max(60, 15 * (est + 2)))

    n = len(items) + 1
    dv_a = DataValidation(type="list", formula1='"evet,hayır"', allow_blank=True)
    dv_l = DataValidation(type="list", formula1='"' + ",".join(LABELS) + '"', allow_blank=True)
    dv_e = DataValidation(type="list", formula1='"' + ",".join(ERRORS) + '"', allow_blank=True)
    for dv, h in ((dv_a, "1) Çekimser mi?"), (dv_l, "2) Etiket"), (dv_e, "3) Hata türü")):
        dv.error, dv.errorTitle, dv.showErrorMessage = "Listeden bir değer seçin.", "Geçersiz değer", True
        ws.add_data_validation(dv)
        L = ws.cell(1, COL[h]).column_letter
        dv.add(f"{L}2:{L}{n}")
        for r in range(2, n + 1):
            ws.cell(r, COL[h]).fill = PatternFill("solid", fgColor="FFF8E1")
    durum = ws.cell(1, COL["Durum"]).column_letter
    ws.conditional_formatting.add(f"A2:{durum}{n}", FormulaRule(formula=[f'${durum}2="tamam"'],
                                                                fill=PatternFill("solid", fgColor="E3F1E6")))
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{durum}{n}"

    g = wb.create_sheet("Kılavuz")
    g.column_dimensions["A"].width = 110
    for text, bold in KILAVUZ:
        g.append([text])
        g.cell(g.max_row, 1).font = Font(bold=bold, size=12 if bold else 11)
    g.append([""])
    g.append([f"Toplam madde: {len(items)} · önceden kaydedilmiş: {sum(1 for it in items if it['item_id'] in labels)}"])
    wb.save(out)
    print(f"Excel: {out}  ({len(items)} madde, {len(labels)} önceden dolu)")


def import_(annotator: str, dry: bool) -> None:
    path = XL_DIR / f"AP6_etiketleme_{annotator}.xlsx"
    ws = load_workbook(path, read_only=True)["Etiketleme"]
    head = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    assert head[:len(HEADERS)] == HEADERS, "Başlık satırı değişmiş; dosya bu betikle üretilmiş olmalı."
    item_ids = {it["item_id"] for it in read_jsonl(ANN / f"items_{annotator}.jsonl")}
    prev = latest_labels(annotator)
    new, problems, done = [], [], 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        iid = row[COL["Madde"] - 1]
        a = (row[COL["1) Çekimser mi?"] - 1] or "").strip().lower()
        lab = (row[COL["2) Etiket"] - 1] or "").strip() or None
        err = (row[COL["3) Hata türü"] - 1] or "").strip() or None
        note = (row[COL["Not"] - 1] or "")
        note = str(note).strip()
        if not iid or (not a and not lab and not err and not note):
            continue
        if iid not in item_ids:
            problems.append(f"{iid}: bilinmeyen madde"); continue
        if a not in ABST:
            problems.append(f"{iid}: çekimser sütunu boş ya da geçersiz ({a!r})"); continue
        rec = {"item_id": iid, "abstention": ABST[a]}
        if rec["abstention"] == "yes":
            if lab or err:
                problems.append(f"{iid}: çekimser 'evet' iken etiket/hata türü dolu — etiket yok sayıldı")
            rec.update(label=None, error_type=None)
        else:
            if lab not in LABELS:
                problems.append(f"{iid}: etiket boş ya da geçersiz ({lab!r})"); continue
            e = ERRORS.get(err) if err else None
            if err and e is None:
                problems.append(f"{iid}: hata türü geçersiz ({err!r})"); continue
            if lab == "supported":
                e = None
            elif e is None:
                problems.append(f"{iid}: hata türü boş (etiket {lab}) — boş olarak kaydedildi")
            rec.update(label=lab, error_type=e)
        rec["note"] = note
        done += 1
        p = prev.get(iid)
        if p and all(p.get(k) == rec.get(k) for k in ("abstention", "label", "error_type", "note")):
            continue
        rec.update(annotator=annotator, saved_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   source="excel")
        new.append(rec)
    for p in problems:
        print("UYARI:", p)
    print(f"Excel'de tamamlanmış {done} madde; labels_{annotator}.jsonl dosyasına eklenecek yeni/değişen kayıt: {len(new)}")
    if new and not dry:
        with (ANN / f"labels_{annotator}.jsonl").open("a", encoding="utf-8", newline="\n") as f:
            for r in new:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Toplam etiketli madde: {len(latest_labels(annotator))} / {len(item_ids)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "import"])
    ap.add_argument("--annotator", default="A")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    export(a.annotator) if a.cmd == "export" else import_(a.annotator, a.dry_run)


if __name__ == "__main__":
    main()
