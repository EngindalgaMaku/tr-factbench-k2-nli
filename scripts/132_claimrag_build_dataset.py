#!/usr/bin/env python3
"""
132_claimrag_build_dataset.py
ClaimRAG-LAW legal slice (K-021): merges the Turkish translation with the expert labels into one
verifier input file, in the same row format as the RAGBench medical slice (scripts/112), so the
frozen K1/K2/V4/LLM-baseline tools run unchanged.

Label scheme: the expert's NLI label per claim. Entailment -> supported, Neutral -> unverifiable,
Contradiction -> contradicted, so `gold_label` is a real 3-class label inside the project's 4-class
scheme (partially_supported never occurs). `gold_binary`: supported vs unsupported (Neutral+Contradiction).

Context windows for K2 (512-token limit, K-022): a context whose tokens plus a claim fit in 512 is one
window; a longer one (GDPR-C15, GDPR-C21) is cut at paragraph boundaries into consecutive windows of at
most WINDOW_TOKENS tokens. K1 keeps the full context (truncated, reported separately, as in K-018).

Output: data/claimrag_law/build/claimrag_tr_law_claims.jsonl, claimrag_tr_law_labels.jsonl, manifest.json
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
LAW = ROOT / "data" / "claimrag_law"
OUT = LAW / "build"
NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
FULL_LIMIT = 450        # context tokens; leaves room for the claim within 512
WINDOW_TOKENS = 400
GOLD4 = {"Entailment": "supported", "Neutral": "unverifiable", "Contradiction": "contradicted"}
GENERATOR = "gpt-4-0613"


def windows_for(text: str, tok) -> list[str]:
    n = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
    if n(text) <= FULL_LIMIT:
        return [text]
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out, cur = [], ""
    for p in paras:
        cand = f"{cur}\n\n{p}" if cur else p
        if cur and n(cand) > WINDOW_TOKENS:
            out.append(cur)
            cur = p
        else:
            cur = cand
    if cur:
        out.append(cur)
    too_long = [w for w in out if n(w) > FULL_LIMIT]
    if too_long:
        raise SystemExit(f"a single paragraph exceeds {FULL_LIMIT} tokens: {too_long[0][:80]}")
    return out


def main() -> None:
    tok = AutoTokenizer.from_pretrained(NLI_MODEL)
    tr = {"chunks": {}, "queries": {}, "claims": {}}
    for path in sorted((LAW / "batches").glob("batch_0[0-9].json")):
        b = json.loads(path.read_text(encoding="utf-8"))
        for k in tr:
            tr[k].update(b[k])
    src = json.loads((LAW / "law_source.json").read_text(encoding="utf-8"))
    labels = {json.loads(l)["claim_id"]: json.loads(l)
              for l in (LAW / "law_labels_DO_NOT_SHOW_TRANSLATOR.jsonl").open(encoding="utf-8")}
    win = {cid: windows_for(text, tok) for cid, text in tr["chunks"].items()}

    claims, label_rows = [], []
    for q in src["queries"]:
        context = tr["chunks"][q["chunk_id"]]
        for pos, c in enumerate(q["claims"], start=1):
            lab = labels[c["claim_id"]]
            claims.append({
                "example_id": c["claim_id"], "release_example_id": c["claim_id"],
                "domain": "legal", "part": q["part"], "question_id": q["query_id"], "model": GENERATOR,
                "chunk_id": q["chunk_id"], "context": context, "question": tr["queries"][q["query_id"]],
                "claim": tr["claims"][c["claim_id"]],
                "gold_binary": lab["binary"], "gold_label": GOLD4[lab["label"]],
                "label_scheme": "claimrag_expert_nli3", "label_status": "HUMAN_EXPERT_SINGLE_ANNOTATOR",
                "position": pos, "n_sentences": len(q["claims"]), "context_words": len(context.split()),
                "context_windows": win[q["chunk_id"]],
            })
            label_rows.append({"example_id": c["claim_id"], "question_id": q["query_id"], "part": q["part"],
                               "expert_label": lab["label"], "gold_binary": lab["binary"],
                               "source_triple": c["triple"], "gt_answer_source": lab["gt_answer_source"]})

    OUT.mkdir(parents=True, exist_ok=True)
    names = ["claimrag_tr_law_claims.jsonl", "claimrag_tr_law_labels.jsonl"]
    for name, rows in zip(names, [claims, label_rows]):
        with (OUT / name).open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    multi = {k: len(v) for k, v in win.items() if len(v) > 1}
    manifest = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_dataset": "ClaimRAG-LAW (Das, Abualhaija & Bianculli, 2026), *-CLAIM-LAW.json, CC BY 4.0",
        "parts": dict(Counter(c["part"] for c in claims)),
        "translation": "Claude, rule-based, researcher-reviewed in 4 batches (K-021); source EN (GDPR) and FR (CIVIL)",
        "labels": "single legal expert, NLI 3-class; Neutral and Contradiction = unsupported",
        "n_questions": len(src["queries"]), "n_claims": len(claims), "n_contexts": len(tr["chunks"]),
        "gold_label": dict(Counter(c["gold_label"] for c in claims)),
        "gold_binary": dict(Counter(c["gold_binary"] for c in claims)),
        "unsupported_rate": round(sum(c["gold_binary"] == "unsupported" for c in claims) / len(claims), 4),
        "windowed_contexts": multi,
        "claims_on_windowed_contexts": sum(1 for c in claims if len(c["context_windows"]) > 1),
        "dropped": "6 queries with empty evidence; claims marked Incorrect / unlabeled / Doesn't Make Sense (K-021)",
        "sha256": {n: hashlib.sha256((OUT / n).read_bytes()).hexdigest() for n in names},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
