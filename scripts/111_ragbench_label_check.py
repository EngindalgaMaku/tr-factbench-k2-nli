#!/usr/bin/env python3
"""
111_ragbench_label_check.py
RAGBench medical slice (K-012): builds the post-translation label check workbook.

For each response sentence it puts the Turkish sentence next to RAGBench's GPT-4
label, the GPT-4 rationale and the cited supporting document sentences in Turkish,
so the researcher can judge whether the label still holds for the Turkish text.
Rationales stay in English (K-012: they are not translated).

Rows: every unsupported sentence, every sentence whose `fully_supported` is False,
and a random sample of supported sentences (seed 42, size set by SUPPORTED_SAMPLE).

Usage: python scripts/111_ragbench_label_check.py
Output: data/ragbench/medical/review/etiket_kontrol.xlsx
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
MED = ROOT / "data" / "ragbench" / "medical"
SUPPORTED_SAMPLE = 100
SPECIAL = {"general", "supported_without_sentence", "well_known_fact", "numerical_reasoning"}


def load_translations() -> dict:
    items = {}
    for path in sorted((MED / "batches").glob("batch_*.json")):
        items.update(json.loads(path.read_text(encoding="utf-8"))["items"])
    return items


def main() -> None:
    tr = load_translations()
    labels = [json.loads(l) for l in (MED / "pmq75_labels_DO_NOT_SHOW_TRANSLATOR.jsonl").open(encoding="utf-8")]

    rows = []
    for d in labels:
        item = tr.get(d["item_id"])
        if item is None:          # not translated yet (PMQ-053)
            continue
        unsupported = set(d["unsupported_keys"])
        for s in d["sentence_support"]:
            key = s["response_sentence_key"]
            sentence = item["responses"][d["model"]].get(key)
            if sentence is None:
                continue
            keys = s["supporting_sentence_keys"] or []
            evidence = "\n".join(
                f"[{k}] {item['documents'][k]}" if k in item["documents"]
                else f"[{k}] — (özel değer)" if k in SPECIAL else f"[{k}] — (bulunamadı)"
                for k in keys
            )
            label = "desteklenmiyor" if key in unsupported else "destekleniyor"
            if not keys:
                evidence = ("— (RAGBench desteklenmeyen cümleler için kanıt göstermez; "
                            "yandaki bağlamın tamamına bakın)" if key in unsupported
                            else "— (kanıt cümlesi gösterilmemiş)")
            context = "\n".join(f"[{k}] {v}" for k, v in item["documents"].items())
            rows.append({
                "group": "desteklenmiyor" if key in unsupported
                else "fully_supported=False" if s["fully_supported"] is False else "destekleniyor",
                "item": d["item_id"], "model": d["model"], "key": key,
                "question": item["question"], "sentence": sentence, "evidence": evidence,
                "context": context,
                "label": label, "fully_supported": str(s["fully_supported"]),
                "explanation": s["explanation"],
            })

    flagged = [r for r in rows if r["group"] != "destekleniyor"]
    supported = [r for r in rows if r["group"] == "destekleniyor"]
    random.Random(42).shuffle(supported)
    selected = flagged + sorted(supported[:SUPPORTED_SAMPLE], key=lambda r: (r["item"], r["model"], r["key"]))

    wb = Workbook()
    ws = wb.active
    ws.title = "Etiket kontrolü"
    ws.append(["Grup", "Madde", "Model", "Anahtar", "Soru", "Yanıt cümlesi (TR)",
               "Gösterilen kanıt cümleleri (TR)", "Bağlamın tamamı (TR)", "RAGBench etiketi",
               "fully_supported", "GPT-4 gerekçesi (EN)", "KONTROL: etiket geçerli mi?", "Not"])
    thin = Side(style="thin", color="BBBBBB")
    fills = {"desteklenmiyor": "FCE4D6", "fully_supported=False": "FFF2CC", "destekleniyor": "E2EFDA"}
    for r in selected:
        ws.append([r["group"], r["item"], r["model"], r["key"], r["question"], r["sentence"],
                   r["evidence"], r["context"], r["label"], r["fully_supported"],
                   r["explanation"], "", ""])
        row = ws.max_row
        for c in ws[row]:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        for c in ws[row][:4]:
            c.fill = PatternFill("solid", fgColor=fills[r["group"]])
        ws.row_dimensions[row].height = 200
    for col, width in zip("ABCDEFGHIJKLM", [20, 10, 22, 8, 38, 55, 50, 70, 15, 13, 55, 16, 30]):
        ws.column_dimensions[col].width = width
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="C00000" if c.column >= 12 else "305496")
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.freeze_panes = "E2"
    ws.auto_filter.ref = ws.dimensions
    dv = DataValidation(type="list", formula1='"geçerli,geçersiz,şüpheli"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"L2:L{ws.max_row}")

    info = wb.create_sheet("Açıklama")
    for line in [
        "RAGBench tıp kesiti — çeviri sonrası etiket kontrolü",
        "",
        "Soru: RAGBench'in GPT-4 etiketi, cümlenin Türkçesi için hâlâ geçerli mi?",
        "L sütununu (geçerli / geçersiz / şüpheli) ve gerekirse M sütununu doldurun.",
        "",
        "Gruplar:",
        "desteklenmiyor — RAGBench bu cümleyi desteklenmeyen olarak işaretlemiş (unsupported_keys).",
        "fully_supported=False — desteklenmeyen listesinde değil, ama cümle kaydında fully_supported alanı False.",
        "destekleniyor — rastgele seçilmiş örneklem (seed 42).",
        "",
        "Notlar:",
        "GPT-4 gerekçeleri İngilizce bırakıldı (karar K-012: gerekçeler çevrilmez).",
        "Kanıt cümleleri, GPT-4'ün gösterdiği belge anahtarlarının Türkçe karşılıklarıdır.",
        "Desteklenmeyen cümlelerde RAGBench kanıt göstermez; bu satırlarda 'Bağlamın tamamı' sütununa bakın:",
        "soru şudur — bu cümlenin söylediği şey bağlamdaki belge cümlelerinden herhangi birinde var mı?",
        "Bağlam sütunu, modele verilen belge cümlelerinin tamamıdır (anahtarlarıyla birlikte).",
        "'general' ve 'supported_without_sentence' RAGBench'in özel değerleridir; belge cümlesine karşılık gelmez.",
        "PMQ-053 çevirisi tamamlanmadığı için bu dosyada yok (karar K-013).",
    ]:
        info.append([line])
    info.column_dimensions["A"].width = 120
    info["A1"].font = Font(bold=True, size=13)
    wb.move_sheet("Açıklama", offset=-1)

    out = MED / "review" / "etiket_kontrol.xlsx"
    version = 2
    while out.exists():
        out = MED / "review" / f"etiket_kontrol_v{version}.xlsx"
        version += 1
    wb.save(out)
    counts = {g: sum(1 for r in selected if r["group"] == g) for g in fills}
    print(f"{len(selected)} satır -> {out}")
    print("gruplar:", counts, "| toplam yanıt cümlesi:", len(rows))


if __name__ == "__main__":
    main()
