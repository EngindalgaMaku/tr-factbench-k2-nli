#!/usr/bin/env python3
"""
80_ap6_fetch_sources.py
AP6: downloads the approved public source documents, stores raw HTML/PDF
bytes for provenance, extracts plain text, and writes a source manifest
(URL, access timestamp, SHA-256, licence note).

Output: data/ap6/sources/{raw,text}/ and data/ap6/sources/source_manifest.csv
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import truststore
from bs4 import BeautifulSoup

# Use the OS certificate store: some Turkish gov sites serve incomplete chains
# that Windows completes via AIA; certificate verification stays ON.
truststore.inject_into_ssl()

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ap6" / "sources"
UA = {"User-Agent": "Mozilla/5.0 (research; TR-FactBench AP6 source collection)"}

LIC_LAW = "Legislation text; outside copyright under FSEK art. 31"
LIC_GOV = "Public government web page; reused for non-commercial research with attribution"
LIC_ORG = "Public institutional web page; reused for non-commercial research with attribution"


def mevzuat(no: int, tur: int = 1) -> str:
    return f"https://www.mevzuat.gov.tr/anasayfa/MevzuatFihristDetayIframe?MevzuatTur={tur}&MevzuatNo={no}&MevzuatTertip=5"


SOURCES = [
    # id, domain, title, url, licence
    ("H1", "legal", "5199 sayılı Hayvanları Koruma Kanunu", mevzuat(5199), LIC_LAW),
    ("H2", "legal", "2918 sayılı Karayolları Trafik Kanunu", mevzuat(2918), LIC_LAW),
    ("H3", "legal", "634 sayılı Kat Mülkiyeti Kanunu", mevzuat(634), LIC_LAW),
    ("H4", "legal", "5326 sayılı Kabahatler Kanunu", mevzuat(5326), LIC_LAW),
    ("H5", "legal", "6098 sayılı Türk Borçlar Kanunu", mevzuat(6098), LIC_LAW),
    ("F1", "finance", "DASK Sıkça Sorulan Sorular", "https://www.dask.gov.tr/tr/sikca-sorulan-sorular", LIC_GOV),
    ("F2a", "finance", "TMSF Mevduat Sigortacılığı SSS", "https://www.tmsf.org.tr/tr/Tmsf/Finansman/mevduat.sss.guncel", LIC_GOV),
    ("F3", "finance", "SPK Kitle Fonlaması Tebliği (III-35/A.2)", mevzuat(39017, tur=9), LIC_LAW),
    ("F4", "finance", "Findeks Sıkça Sorulan Sorular", "https://www.findeks.com/sikca-sorulan-sorular", LIC_ORG),
    ("F5", "finance", "Finansal Tüketicilerden Alınacak Ücretlere İlişkin Usul ve Esaslar Hakkında Tebliğ (2020/7)", mevzuat(34343, tur=9), LIC_LAW),
    ("T1a", "medical", "Kırım Kongo Kanamalı Ateşi / Uyarı ve Önlemler", "https://www.saglik.gov.tr/TR-55309/kirim-kongo-kanamali-atesi--uyari-ve-onlemler.html", LIC_GOV),
    ("T1b", "medical", "HSGM Kırım Kongo Kanamalı Ateşi (KKKA)", "https://hsgm.saglik.gov.tr/tr/zoonotik-ve-vektorel-hastaliklar/kkka.html", LIC_GOV),
    ("T2", "medical", "Aşırı Sıcaklardan Korunma", "https://www.saglik.gov.tr/TR-61703/asiri-sicaklardan-korunma.html", LIC_GOV),
    ("T3", "medical", "Fibromiyalji", "https://bursailkercelikcanftr.saglik.gov.tr/TR-527700/fibromiyalji.html", LIC_GOV),
    ("T4", "medical", "Varis Nedir?", "https://kosuyolueah.saglik.gov.tr/TR,493489/varis-nedir.html", LIC_GOV),
    ("T5", "medical", "Sedef Hastalığı İle İlgili Merak Ettikleriniz", "https://bucadh.saglik.gov.tr/TR-639776/doc-dr-fatma-asli-hapa-sedef-hastaligi-ile-ilgili-merak-ettikleriniz.html", LIC_GOV),
]


# Manual trimming. Each source maps to a list of (start, end) segments that are
# kept; None means file start / file end. Used for (i) boilerplate removal on
# FAQ pages and (ii) restricting very long laws to pre-declared sections so the
# legal corpus is comparable in size to the other domains (AP6 protocol, sec. 3).
CLEAN_MARKERS = {
    "F1": [("DASK Nedir?", "Lorem ipsum dolor.")],
    "F2a": [("Mevduat Sigortacılığı Hakkında Sıkça Sorulan Sorular", None)],
    "F4": [("Findeks'e nasıl üye olurum?", "Aradığınız bilgiye ulaşamadıysanız")],
    # 2918 KTK: title block + Part 5 (driver licences, art. 35-45) + art. 118 (penalty points)
    "H2": [(None, "\nBİRİNCİ KISIM"), ("\nBEŞİNCİ KISIM", "\nALTINCI KISIM"),
           ("Ceza puanı uygulaması, puanlama", "\nONUNCU KISIM")],
    # 6098 TBK: title block + suretyship (art. 581-603, up to Part 16)
    "H5": [(None, "\nBİRİNCİ KISIM"), ("Kefalet Sözleşmesi", "\nONALTINCI BÖLÜM")],
}


def _find(text: str, marker: str, sid: str) -> int:
    if text.count(marker) != 1:
        raise ValueError(f"{sid}: marker must occur exactly once: {marker!r}")
    return text.index(marker)


def clean_text(sid: str, text: str) -> str:
    # Re-join soft-wrapped lines first (headings such as "ALTINCI\nKISIM" are
    # split in the HTML); paragraphs are separated by blank lines.
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text)]
    text = "\n\n".join(p for p in paras if p)
    segments = CLEAN_MARKERS.get(sid)
    if segments:
        parts = []
        for start, end in segments:
            # Start markers must be unique; an end marker is its first occurrence after the start.
            i = _find(text, start, sid) if start else 0
            j = text.find(end, i + 1) if end else len(text)
            if j < 0:
                raise ValueError(f"{sid}: end marker not found after start: {end!r}")
            parts.append(text[i:j].strip())
        text = "\n\n".join(parts)
    return text


def decode_html(html: bytes) -> str:
    # saglik.gov.tr CMS serves windows-1254 without a usable HTTP charset.
    head = html[:4000].decode("ascii", "ignore").lower()
    m = re.search(r"charset=[\"']?([a-z0-9_-]+)", head)
    for enc in ([m.group(1)] if m else []) + ["utf-8", "windows-1254"]:
        try:
            return html.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return html.decode("utf-8", "replace")


def extract_text(html: bytes) -> str:
    soup = BeautifulSoup(decode_html(html), "html.parser")
    # saglik.gov.tr pages keep the article in #div_print; elsewhere use the whole page.
    main_block = soup.select_one("#div_print")
    if main_block is not None:
        soup = main_block
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "form"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines()]
    out, blank = [], 0
    for line in lines:
        if line:
            out.append(line)
            blank = 0
        elif blank == 0:
            out.append("")
            blank = 1
    return "\n".join(out).strip()


def main() -> None:
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    (OUT / "text").mkdir(parents=True, exist_ok=True)
    rows = []
    for sid, domain, title, url, lic in SOURCES:
        if not url:
            print(f"[SKIP] {sid}: URL not set")
            continue
        try:
            resp = requests.get(url, headers=UA, timeout=60)
            status, raw = resp.status_code, resp.content
        except requests.RequestException as exc:
            print(f"[ERR] {sid}: {type(exc).__name__}: {exc}")
            status, raw = f"error:{type(exc).__name__}", b""
        raw_path = OUT / "raw" / f"{sid}.html"
        raw_path.write_bytes(raw)
        text = clean_text(sid, extract_text(raw)) if status == 200 else ""
        (OUT / "text" / f"{sid}.txt").write_text(text, encoding="utf-8", newline="\n")
        words = len(text.split())
        rows.append({
            "source_id": sid, "domain": domain, "title": title, "url": url,
            "accessed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "http_status": status, "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "text_words": words, "clean_segments": " ; ".join(f"{a or '<start>'} -> {b or '<end>'}" for a, b in CLEAN_MARKERS.get(sid, [])),
            "licence_note": lic,
        })
        print(f"[{status}] {sid:4s} {domain:8s} words={words:6d}  {title}")
    with (OUT / "source_manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
