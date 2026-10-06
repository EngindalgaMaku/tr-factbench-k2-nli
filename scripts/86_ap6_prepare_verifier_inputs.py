#!/usr/bin/env python3
"""
86_ap6_prepare_verifier_inputs.py
AP6 step 5: builds one verifier input row per answer sentence:
  example_id = sentence_id, context = the 3 retrieved chunks the LLM saw
  (joined by blank lines, same text without the [n] numbering), question, claim = sentence.

The official K2/LLM-baseline tools require a valid `gold_label` field. AP6 has no
human labels at this stage, so a fixed placeholder is written and every row is
marked `label_status="UNLABELED_PLACEHOLDER"`. Any metrics those tools print on
this file are meaningless and must not be reported.

Output: data/ap6/verifier/ap6_claims.jsonl
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AP6 = ROOT / "data" / "ap6"
PLACEHOLDER = "unverifiable"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    chunks = {c["chunk_id"]: c["text"] for c in read_jsonl(AP6 / "rag" / "chunks.jsonl")}
    retrieval = {r["question_id"]: r for r in read_jsonl(AP6 / "rag" / "retrieval_top3.jsonl")}
    sentences = read_jsonl(AP6 / "generation" / "sentences.jsonl")
    out_dir = AP6 / "verifier"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "ap6_claims.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for s in sentences:
            r = retrieval[s["question_id"]]
            row = {"example_id": s["sentence_id"], "release_example_id": s["sentence_id"],
                   "domain": s["domain"], "question_id": s["question_id"], "model": s["model"],
                   "context": "\n\n".join(chunks[c] for c in r["chunk_ids"]),
                   "question": r["question"], "claim": s["sentence"],
                   "gold_label": PLACEHOLDER, "label_status": "UNLABELED_PLACEHOLDER",
                   "abstention": s["abstention"], "back_reference": s["back_reference"]}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(sentences)} verifier rows")


if __name__ == "__main__":
    main()
