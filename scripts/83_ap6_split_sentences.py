#!/usr/bin/env python3
"""
83_ap6_split_sentences.py
AP6 step 4: split generated answers into sentence-level claims (the unit of
verification and annotation). Markdown emphasis/list markers are removed;
the wording of the text is not changed.

Rules (fixed before looking at the answers):
  * split after . ! ? when followed by whitespace and an upper-case letter or digit;
  * do not split after common Turkish abbreviations (md., vb., vs., örn., bkz., Dr., Prof., No.)
    or inside numbers (2,5 / 1.200.000);
  * a fragment of fewer than 3 words is merged into the previous sentence;
  * sentences that only state that the sources lack information are flagged
    `abstention=True` (handling decided in the protocol, not here).

Output: data/ap6/generation/sentences.jsonl
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "data" / "ap6" / "generation"

ABBREVIATIONS = ("md.", "vb.", "vs.", "örn.", "bkz.", "Dr.", "Prof.", "No.", "s.", "yy.", "Op.", "Uz.")
SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ0-9\"“(])")
ABSTENTION_RE = re.compile(
    r"(kaynak(lar)?(da|ta)|metin(ler)?de|verilen bilgiler(de)?)[^.]*"
    r"(yer almamaktadır|bulunmamaktadır|belirtilmemiştir|yer verilmemiştir|bilgi (yoktur|bulunmuyor|verilmemiştir)|"
    r"açıklanmamıştır|değinilmemiştir|detaylandırılmamıştır|mevcut değildir)",
    re.IGNORECASE,
)


def strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return " ".join(text.split())


def split_sentences(text: str) -> list[str]:
    parts = SPLIT_RE.split(text)
    merged: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if merged and (merged[-1].endswith(ABBREVIATIONS) or len(part.split()) < 3):
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return merged


def main() -> None:
    answers = [json.loads(line) for line in (GEN / "answers.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    out = []
    for a in answers:
        model_tag = a["model_requested"].split("/")[-1]
        for k, sent in enumerate(split_sentences(strip_markdown(a["answer"])), 1):
            out.append({
                "sentence_id": f"{a['question_id']}__{model_tag}__s{k:02d}",
                "question_id": a["question_id"], "domain": a["domain"], "question_type": a["type"],
                "model": a["model_requested"], "position": k, "sentence": sent,
                "abstention": bool(ABSTENTION_RE.search(sent)),
                "answer_finish_reason": a["finish_reason"],
            })
    with (GEN / "sentences.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for s in out:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    n_abs = sum(s["abstention"] for s in out)
    print(f"answers={len(answers)} sentences={len(out)} abstention_flagged={n_abs}")


if __name__ == "__main__":
    main()
