#!/usr/bin/env python3
"""
100_ap6v2_fetch_sources.py
AP6 v2 (decision K-007): source documents.

- Legal (H1-H5), finance (F1-F5) and the kept medical pages (T1a, T1b, T2) are
  copied from the frozen AP6 v1 collection (same raw bytes, same SHA-256), so
  their text is not re-downloaded and cannot drift.
- The hospital pages T3-T5 are dropped; new official Ministry of Health pages
  are downloaded (raw HTML/PDF kept for provenance) and their text extracted.

This step only collects; main-content trimming markers for the new pages are
decided after the raw pages have been inspected (CLEAN_MARKERS below).

Output: data/ap6v2/sources/{raw,text}/ and data/ap6v2/sources/source_manifest.csv
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / "data" / "ap6" / "sources"
OUT = ROOT / "data" / "ap6v2" / "sources"

# Re-use the v1 HTML extraction and cleaning code unchanged.
_spec = importlib.util.spec_from_file_location("v1fetch", ROOT / "scripts" / "80_ap6_fetch_sources.py")
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

KEEP_FROM_V1 = ["H1", "H2", "H3", "H4", "H5", "F1", "F2a", "F3", "F4", "F5", "T1a", "T1b", "T2"]

NEW_SOURCES = [
    # id, domain, title, url, licence
    ("T6a", "medical", "Aşı Portalı – Kuduz", "https://asi.saglik.gov.tr/asi-ile-oenlenebilir-hastaliklar/kuduz.html", v1.LIC_GOV),
    ("T6b", "medical", "HSGM Kuduz Sıkça Sorulan Sorular (PDF)", "https://hsgm.saglik.gov.tr/depo/birimler/zoonotik-ve-vektorel-hastaliklar-db/Sikca_Sorulan_Sorular/Kuduz.pdf", v1.LIC_GOV),
    # T7: the HTML page "Tuz ve Sağlık" returned 404 on 2026-10-11; the HSGM salt brochure (2021) is used instead.
    ("T7", "medical", "HSGM – Tuz ve Tuz Kullanımı (broşür, 2021)", "https://hsgm.saglik.gov.tr/depo/birimler/saglikli-beslenme-ve-hareketli-hayat-db/Dokumanlar/Brosurler/Tuz_sorular_brosur_12_04_2021.pdf", v1.LIC_GOV),
    ("T8", "medical", "HSGM – Hipertansiyon", "https://hsgm.saglik.gov.tr/tr/kronik-hastaliklar/bobrek-hastaliklari/hipertansiyon.html", v1.LIC_GOV),
    ("T9a", "medical", "Aşı Portalı – Mevsimsel Grip", "https://asi.saglik.gov.tr/asi-ile-oenlenebilir-hastaliklar/mevsimsel-grip.html", v1.LIC_GOV),
    # T9b (grip.saglik.gov.tr SSS) returned 404 on 2026-10-11 and was dropped.
    ("T10a", "medical", "Aşı Portalı – Tetanos", "https://asi.saglik.gov.tr/asi-ile-oenlenebilir-hastaliklar/tetanos.html", v1.LIC_GOV),
    ("T10b", "medical", "Aşı Portalı – Erişkin Aşılama", "https://asi.saglik.gov.tr/kimlere-asi-yapilir/eriskin-asilama.html", v1.LIC_GOV),
    ("T11", "medical", "Aşı Portalı – Kızamık", "https://asi.saglik.gov.tr/asi-ile-oenlenebilir-hastaliklar/kizamik.html", v1.LIC_GOV),
    ("T12", "medical", "HSGM – Fiziksel Aktivite", "https://hsgm.saglik.gov.tr/tr/fiziksel-aktivite.html", v1.LIC_GOV),
]

# Main-content boundaries, set after inspecting the raw pages (2026-10-11).
# The text strictly between the two markers is kept (both markers excluded);
# None means file start / file end. Each marker must occur exactly once.
PORTAL_HEAD = "TÜRKİYE CUMHURİYETİ SAĞLIK BAKANLIĞI AŞI PORTALI"   # asi.saglik.gov.tr header
PORTAL_FOOT = "Copyright © 2025 Halk Sağlığı Genel Müdürlüğü"       # asi.saglik.gov.tr footer
HSGM_FOOT = "Ana Sayfa Başkanlığımız"                                # hsgm.saglik.gov.tr footer menu
CLEAN_MARKERS: dict[str, tuple[str | None, str | None]] = {
    "T6a": (PORTAL_HEAD, PORTAL_FOOT),
    "T9a": (PORTAL_HEAD, PORTAL_FOOT),
    "T10a": (PORTAL_HEAD, PORTAL_FOOT),
    "T10b": ("Hangi Yaşta Kimlere Aşı Yapılır?", PORTAL_FOOT),
    "T11": (PORTAL_HEAD, PORTAL_FOOT),
    "T8": ("Romatoid Artrit Ailevi Akdeniz", HSGM_FOOT),   # end of the left-hand disease menu
    "T12": ("\nEnglish\n", HSGM_FOOT),
}


def pdf_text(raw: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw))
    return "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)


def trim(sid: str, text: str) -> str:
    start, end = CLEAN_MARKERS.get(sid, (None, None))
    for marker in (start, end):
        if marker and text.count(marker) != 1:
            raise ValueError(f"{sid}: marker must occur exactly once: {marker!r}")
    i = text.index(start) + len(start) if start else 0
    if start and "\n\n" in text[i:]:          # skip the rest of the marker's paragraph
        i = text.index("\n\n", i)
    j = text.index(end) if end else len(text)
    paras = [" ".join(p.split()) for p in text[i:j].split("\n\n")]
    # Drop empty paragraphs and bare page numbers left by PDF extraction.
    return "\n\n".join(p for p in paras if p and not p.isdigit())


def main() -> None:
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    (OUT / "text").mkdir(parents=True, exist_ok=True)
    rows = []

    v1_rows = {r["source_id"]: r for r in csv.DictReader((V1 / "source_manifest.csv").open(encoding="utf-8"))}
    for sid in KEEP_FROM_V1:
        shutil.copy2(V1 / "raw" / f"{sid}.html", OUT / "raw" / f"{sid}.html")
        shutil.copy2(V1 / "text" / f"{sid}.txt", OUT / "text" / f"{sid}.txt")
        row = dict(v1_rows[sid])
        row["origin"] = "copied from AP6 v1 (frozen)"
        rows.append(row)
        print(f"[v1 ] {sid:4s} {row['domain']:8s} words={int(row['text_words']):6d}  {row['title']}")

    # saglik.gov.tr hosts time out intermittently: pages already downloaded with
    # HTTP 200 are kept (raw bytes and access time), only the rest are retried.
    old_path = OUT / "source_manifest.csv"
    old_rows = {r["source_id"]: r for r in csv.DictReader(old_path.open(encoding="utf-8"))} if old_path.exists() else {}
    for sid, domain, title, url, lic in NEW_SOURCES:
        is_pdf = url.lower().endswith(".pdf")
        raw_path = OUT / "raw" / f"{sid}.{'pdf' if is_pdf else 'html'}"
        prev = old_rows.get(sid)
        if prev and prev["http_status"] == "200" and raw_path.exists():
            status, raw, accessed = 200, raw_path.read_bytes(), prev["accessed_utc"]
        else:
            accessed = datetime.now(timezone.utc).isoformat(timespec="seconds")
            for attempt in range(3):
                try:
                    resp = requests.get(url, headers=v1.UA, timeout=90)
                    status, raw = resp.status_code, resp.content
                    break
                except requests.RequestException as exc:
                    print(f"[ERR] {sid} attempt {attempt + 1}: {type(exc).__name__}")
                    status, raw = f"error:{type(exc).__name__}", b""
                    time.sleep(10)
            raw_path.write_bytes(raw)
        text = ""
        if status == 200:
            # v1.clean_text without markers only normalises whitespace into paragraphs.
            text = trim(sid, v1.clean_text(sid, pdf_text(raw) if is_pdf else v1.extract_text(raw)))
        (OUT / "text" / f"{sid}.txt").write_text(text, encoding="utf-8", newline="\n")
        words = len(text.split())
        rows.append({
            "source_id": sid, "domain": domain, "title": title, "url": url,
            "accessed_utc": accessed,
            "http_status": status, "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "text_words": words,
            "clean_segments": " -> ".join(m or "<start/end>" for m in CLEAN_MARKERS.get(sid, (None, None))),
            "licence_note": lic, "origin": "downloaded for AP6 v2",
        })
        print(f"[{status}] {sid:4s} {domain:8s} words={words:6d}  {title}")

    with (OUT / "source_manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[-1].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
