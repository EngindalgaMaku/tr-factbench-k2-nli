#!/usr/bin/env python3
"""
112_ragbench_build_dataset.py
RAGBench medical slice (K-012): merges the Turkish translation with RAGBench's
labels into one verifier input file, in the same row format the K1/K2/hybrid and
LLM-baseline tools already use for AP6.

Label scheme (important): RAGBench's label is BINARY per response sentence —
supported, or listed in `unsupported_keys`. It is not the project's 4-class
scheme, so `gold_binary` carries the real label and `gold_label` is only a
tool-compatibility field (unsupported -> "unverifiable"). Any 4-class metric
printed on this file is meaningless; predictions must be collapsed to binary
before scoring. Labels are GPT-4 "silver" labels (K-011).

Key normalisation: GPT-4 wrote some sentence keys with a trailing period
("a." instead of "a"); keys are normalised on both sides (K-015).

Output: data/ragbench/medical/build/ragbench_tr_medical_claims.jsonl  (verifier input)
        data/ragbench/medical/build/ragbench_tr_medical_labels.jsonl  (labels + rationales, not for prompts)
        data/ragbench/medical/build/manifest.json
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MED = ROOT / "data" / "ragbench" / "medical"
OUT = MED / "build"
SPECIAL_SUPPORT = {"general", "supported_without_sentence", "well_known_fact", "numerical_reasoning"}
SHORT = {"claude-3-haiku-20240307": "claude3haiku", "gpt-3.5-turbo-0125": "gpt35turbo"}


def norm(key: str) -> str:
    return key.rstrip(".").strip()


def main() -> None:
    translations = {}
    for path in sorted((MED / "batches").glob("batch_*.json")):
        translations.update(json.loads(path.read_text(encoding="utf-8"))["items"])
    labels = [json.loads(l) for l in (MED / "pmq75_labels_DO_NOT_SHOW_TRANSLATOR.jsonl").open(encoding="utf-8")]
    source = {json.loads(l)["item_id"]: json.loads(l)
              for l in (MED / "pmq75_source_en.jsonl").open(encoding="utf-8")}

    claims, label_rows, skipped = [], [], []
    for d in sorted(labels, key=lambda r: (r["item_id"], r["model"])):
        item = translations.get(d["item_id"])
        if item is None:
            skipped.append(d["item_id"])
            continue
        # Context: document sentences in source order, one document per paragraph.
        docs: dict[str, list[str]] = {}
        for key, text in item["documents"].items():
            docs.setdefault(key[0], []).append(text)
        windows = [" ".join(v) for v in docs.values()]   # one window per source document
        context = "\n\n".join(windows)

        unsupported = {norm(k) for k in d["unsupported_keys"]}
        support = {norm(s["response_sentence_key"]): s for s in d["sentence_support"]}
        sentences = item["responses"][d["model"]]
        for position, (key, claim) in enumerate(sentences.items(), start=1):
            s = support.get(key, {})
            keys = [norm(k) for k in (s.get("supporting_sentence_keys") or [])]
            is_unsupported = key in unsupported
            example_id = f"{d['item_id']}__{SHORT[d['model']]}__{key}"
            claims.append({
                "example_id": example_id, "release_example_id": example_id,
                "domain": "medical", "question_id": d["item_id"], "model": d["model"],
                "context": context, "question": item["question"], "claim": claim,
                "gold_binary": "unsupported" if is_unsupported else "supported",
                "gold_label": "unverifiable" if is_unsupported else "supported",
                "label_scheme": "ragbench_binary_mapped",
                "label_status": "SILVER_GPT4_BINARY — 4 sınıflı metrik geçersizdir",
                "position": position, "n_sentences": len(sentences),
                "context_words": len(context.split()),
                # K2 (mDeBERTa) has a 512-token limit: 422/809 full contexts exceed it,
                # while every single document stays under 362 tokens. Runners that cannot
                # take the full context score each window and keep the strongest support.
                "context_windows": windows,
            })
            label_rows.append({
                "example_id": example_id, "ragbench_id": d["ragbench_id"],
                "question_id": d["item_id"], "model": d["model"], "sentence_key": key,
                "gold_binary": "unsupported" if is_unsupported else "supported",
                "response_adherence_score": bool(d["adherence_score"]),
                "annotating_model": d["annotating_model"],
                "supporting_sentence_keys": [k for k in keys if k not in SPECIAL_SUPPORT],
                "special_support_values": [k for k in keys if k in SPECIAL_SUPPORT],
                "fully_supported_raw": s.get("fully_supported"),
                "gpt4_explanation_en": s.get("explanation"),
                "has_support_record": key in support,
            })

    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in [("ragbench_tr_medical_claims.jsonl", claims),
                       ("ragbench_tr_medical_labels.jsonl", label_rows)]:
        with (OUT / name).open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    words = [c["context_words"] for c in claims]
    manifest = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_dataset": "RAGBench (Friel et al., 2024), pubmedqa test split, CC BY 4.0",
        "slice": "75 questions sampled with seed 42, both model responses per question",
        "translation": "Claude, sentence-aligned, rule-based, researcher-reviewed per batch (K-012)",
        "labels": "RAGBench GPT-4 silver labels, unchanged (K-011); binary per response sentence",
        "n_items_translated": len(translations),
        "n_items_skipped": sorted(set(skipped)),
        "n_responses": len({c['question_id'] + c['model'] for c in claims}),
        "n_claims": len(claims),
        "gold_binary": dict(Counter(c["gold_binary"] for c in claims)),
        "unsupported_rate": round(sum(c["gold_binary"] == "unsupported" for c in claims) / len(claims), 4),
        "claims_without_support_record": sum(1 for r in label_rows if not r["has_support_record"]),
        "rows_with_special_support": sum(1 for r in label_rows if r["special_support_values"]),
        "context_words": {"mean": round(sum(words) / len(words), 1), "min": min(words), "max": max(words)},
        "context_windows_per_claim": 5,
        "mdeberta_tokens": {"full_context_over_512": 422, "window_over_512": 0, "max_window_tokens": 362},
        "sha256": {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
                   for name in ["ragbench_tr_medical_claims.jsonl", "ragbench_tr_medical_labels.jsonl"]},
        "known_data_quality_notes": "K-015: trailing-dot keys normalised; 5 fully_supported=False rows outside "
                                    "unsupported_keys; one rationale/label mismatch (PMQ-021 a)",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
