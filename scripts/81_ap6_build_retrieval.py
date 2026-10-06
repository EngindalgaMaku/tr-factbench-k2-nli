#!/usr/bin/env python3
"""
81_ap6_build_retrieval.py
AP6 step 2: paragraph-aware chunking (~70 words) of the frozen source texts,
dense retrieval with intfloat/multilingual-e5-large (top-3, within the question's
domain), and a set-up sanity check (is the evidence document among the top-3 chunks?).

The retriever is part of the RAG *environment*, not the system under test; no
retriever comparison is performed (AP6 protocol, sec. 4).

Output: data/ap6/rag/chunks.jsonl, data/ap6/rag/retrieval_top3.jsonl,
        data/ap6/rag/retrieval_sanity.json
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "ap6" / "sources"
QUESTIONS = ROOT / "data" / "ap6" / "questions" / "questions_v1.0.jsonl"
OUT = ROOT / "data" / "ap6" / "rag"
MODEL_ID = "intfloat/multilingual-e5-large"
MAX_WORDS = 70  # 85 exceeded mDeBERTa's 512-token limit for 37/60 contexts (Turkish ~2.2 tok/word)
TOP_K = 3


def split_sentences(paragraph: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?;:])\s+", paragraph) if s]


def chunk_document(text: str) -> list[str]:
    """Greedy packing of paragraphs into chunks of <= MAX_WORDS words; a paragraph
    longer than MAX_WORDS is split at sentence boundaries (a single over-long
    sentence becomes its own chunk)."""
    units: list[str] = []
    for para in (p.strip() for p in text.split("\n\n")):
        if not para:
            continue
        if len(para.split()) <= MAX_WORDS:
            units.append(para)
        else:
            units.extend(split_sentences(para))
    chunks, current = [], []
    for unit in units:
        if current and len(" ".join(current + [unit]).split()) > MAX_WORDS:
            chunks.append(" ".join(current))
            current = []
        current.append(unit)
    if current:
        chunks.append(" ".join(current))
    return chunks


def embed(texts: list[str], tok, model, device: str, batch: int = 16) -> np.ndarray:
    vecs = []
    for i in range(0, len(texts), batch):
        enc = tok(texts[i:i + batch], padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model(**enc).last_hidden_state
        mask = enc["attention_mask"].unsqueeze(-1).float()
        pooled = (out * mask).sum(1) / mask.sum(1)
        vecs.append(torch.nn.functional.normalize(pooled, dim=-1).cpu().numpy())
    return np.vstack(vecs)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = list(csv.DictReader((SRC / "source_manifest.csv").open(encoding="utf-8")))
    chunks = []
    for row in manifest:
        text = (SRC / "text" / f"{row['source_id']}.txt").read_text(encoding="utf-8")
        for j, c in enumerate(chunk_document(text)):
            chunks.append({"chunk_id": f"{row['source_id']}-{j:03d}", "source_id": row["source_id"],
                           "domain": row["domain"], "text": c, "words": len(c.split())})
    with (OUT / "chunks.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModel.from_pretrained(MODEL_ID).to(device).eval()
    chunk_vecs = embed([f"passage: {c['text']}" for c in chunks], tok, model, device)

    questions = [json.loads(line) for line in QUESTIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    q_vecs = embed([f"query: {q['question']}" for q in questions], tok, model, device)

    results, hits = [], []
    for q, qv in zip(questions, q_vecs):
        idx = [i for i, c in enumerate(chunks) if c["domain"] == q["domain"]]
        sims = chunk_vecs[idx] @ qv
        top = [idx[i] for i in np.argsort(-sims)[:TOP_K]]
        top_chunks = [chunks[i] for i in top]
        evidence_docs = {s.split()[0] for s in q["evidence_source"].split(";")}
        hit = any(c["source_id"] in evidence_docs for c in top_chunks)
        hits.append(hit)
        context = "\n\n".join(c["text"] for c in top_chunks)
        results.append({"question_id": q["question_id"], "domain": q["domain"], "type": q["type"],
                        "question": q["question"], "chunk_ids": [c["chunk_id"] for c in top_chunks],
                        "scores": [round(float(chunk_vecs[i] @ qv), 4) for i in top],
                        "context": context, "context_words": len(context.split()),
                        "evidence_doc_in_top3": hit})
    with (OUT / "retrieval_top3.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_domain = {}
    for r in results:
        by_domain.setdefault(r["domain"], []).append(r["evidence_doc_in_top3"])
    sanity = {
        "model": MODEL_ID, "max_words_per_chunk": MAX_WORDS, "top_k": TOP_K, "n_chunks": len(chunks),
        "chunks_by_domain": {d: sum(c["domain"] == d for c in chunks) for d in by_domain},
        "hit_at_3_overall": round(sum(hits) / len(hits), 4),
        "hit_at_3_by_domain": {d: round(sum(v) / len(v), 4) for d, v in by_domain.items()},
        "max_context_words": max(r["context_words"] for r in results),
        "mean_context_words": round(sum(r["context_words"] for r in results) / len(results), 1),
    }
    (OUT / "retrieval_sanity.json").write_text(json.dumps(sanity, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sanity, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
