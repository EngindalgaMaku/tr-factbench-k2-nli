#!/usr/bin/env python3
"""
130_claimrag_prepare_sources.py
Prepares the ClaimRAG-LAW claim-verification data (Das et al. 2026; SNTSVV/ClaimRAG-LAW, CC BY 4.0)
for Turkish translation (K-021).

Only the self-contained *-CLAIM-LAW.json files are used (their query ids do not line up with the
*-RAG-LAW.json files). Queries whose evidence chunk is empty in the release are dropped (labels cannot be checked).
A claim is kept when the expert marked it Correct and gave an NLI label
(Entailment / Neutral / Contradiction); empty labels and "Doesn't Make Sense" are dropped, as in the paper.

Translation units: each distinct evidence chunk once, each query, each kept claim (an SPO triple that
the translator renders as one Turkish sentence). GPT-4 reference answers are not translated (the
systems never see them); they stay in the label file as metadata.

Output: data/claimrag_law/law_source.json          (shown to the translator, no labels)
        data/claimrag_law/law_labels_DO_NOT_SHOW_TRANSLATOR.jsonl
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAW = ROOT / "data" / "claimrag_law"
KEEP = {"Entailment", "Neutral", "Contradiction"}
PART = {"GDPR": ("gdpr", "en"), "CIVIL": ("civil", "fr")}


def main() -> None:
    chunks: dict[str, dict] = {}
    labels, queries = [], []
    dropped = 0
    empty: list[str] = []
    for src, (part, lang) in PART.items():
        for item in json.loads((LAW / "raw" / f"{src}-CLAIM-LAW.json").read_text(encoding="utf-8")):
            text = item["relevant_chunk"].strip()
            if not text:                                  # evidence missing in the release: cannot be scored
                empty.append(f"{part.upper()}-Q{item['query_id']:03d}")
                continue
            key = (part, " ".join(text.split()))
            if key not in chunks:
                chunks[key] = {"chunk_id": f"{part.upper()}-C{sum(c['part'] == part for c in chunks.values()) + 1:02d}",
                               "part": part, "lang": lang, "text": text}
            qid = f"{part.upper()}-Q{item['query_id']:03d}"
            kept = []
            for i, c in enumerate(item["claims"], 1):
                if c["claim_correctness"] != "Correct" or c["claim_entailment"] not in KEEP:
                    dropped += 1
                    continue
                cid = f"{qid}-{i:02d}"
                kept.append({"claim_id": cid, "triple": c["claim"]})
                labels.append({"claim_id": cid, "query_id": qid, "part": part, "label": c["claim_entailment"],
                               "binary": "supported" if c["claim_entailment"] == "Entailment" else "unsupported",
                               "gt_answer_source": item["gt_answer"]})
            if kept:
                queries.append({"query_id": qid, "part": part, "lang": lang, "chunk_id": chunks[key]["chunk_id"],
                                "query": item["query"], "claims": kept})
    used = {q["chunk_id"] for q in queries}
    out = {"chunks": [c for c in chunks.values() if c["chunk_id"] in used], "queries": queries}
    (LAW / "law_source.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    with (LAW / "law_labels_DO_NOT_SHOW_TRANSLATOR.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in labels:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    for part in ("gdpr", "civil"):
        q = [x for x in queries if x["part"] == part]
        lab = [x for x in labels if x["part"] == part]
        print(part, "chunks", sum(c["part"] == part for c in out["chunks"]), "queries", len(q), "claims", len(lab),
              "unsupported", sum(x["binary"] == "unsupported" for x in lab),
              "chunk words", sum(len(c["text"].split()) for c in out["chunks"] if c["part"] == part))
    print("dropped claims", dropped, "| queries with empty evidence (dropped):", empty)


if __name__ == "__main__":
    main()
