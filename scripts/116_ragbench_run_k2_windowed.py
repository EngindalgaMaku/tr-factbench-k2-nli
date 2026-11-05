#!/usr/bin/env python3
"""
116_ragbench_run_k2_windowed.py
K2 on the Turkish RAGBench medical slice with per-document windowing (decision K-017).

Identical to the frozen K2 path (scripts/45_run_k2_from_gemma_atoms.py) except for
the premise: every Gemma atom is scored against each source-document window
separately instead of the full context, using the same model, the same
run_pair_inference (same label normalisation) and the same atom aggregation as the
frozen K2 used in Gold-480 and AP6 v1 (soft_prob_avg, k2_nli.aggregation_ablation).

Per-atom window rule: entailment if any window entails; otherwise contradiction if
any window contradicts; otherwise neutral. (For the binary score only "any window
entails" matters; the contradiction step keeps the 4-class output meaningful.)

Atomiser failures get no K2 prediction (as in AP6 v1); the hybrid falls back to K1.

Usage: python scripts/116_ragbench_run_k2_windowed.py [--build DIR --claims FILE]
(defaults: the RAGBench medical build; the ClaimRAG-LAW legal slice uses the same code, K-022)
Output: data/ragbench/medical/build/predictions/k2_windowed.jsonl (+ k2_windowed_atoms.jsonl, manifest)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from k2_nli.aggregation_ablation import aggregate_soft_prob
from k2_nli.gemma_data import load_gemma_predicted_dataset
from k2_nli.io import sha256_file
from k2_nli.modeling import InferenceConfig, run_pair_inference

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "data" / "ragbench" / "medical" / "build"
MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"   # frozen K2 model
MAX_LENGTH = 512
BATCH = 8


def window_rule(outs: list[dict]) -> dict:
    for label in ("entailment", "contradiction"):
        hits = [o for o in outs if o["pred_label"] == label]
        if hits:
            key = "prob_entailment" if label == "entailment" else "prob_contradiction"
            return max(hits, key=lambda o: o[key])
    return max(outs, key=lambda o: o["prob_neutral"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(BUILD))
    ap.add_argument("--claims", default="ragbench_tr_medical_claims.jsonl")
    args = ap.parse_args()
    build = Path(args.build).resolve()
    out_dir = build / "predictions"
    atoms_path = build / "atoms" / "k2_input.jsonl"
    claims_path = build / args.claims
    records = load_gemma_predicted_dataset(str(atoms_path))
    windows = {json.loads(l)["example_id"]: json.loads(l)["context_windows"]
               for l in claims_path.open(encoding="utf-8")}
    ready = [r for r in records if r["pipeline_ready"]]

    premises, hypotheses, index = [], [], []
    for r in ready:
        for a_pos, atom in enumerate(r["atoms"]):
            for w_pos, window in enumerate(windows[r["example_id"]]):
                premises.append(window)
                hypotheses.append(atom["text"])
                index.append((r["example_id"], a_pos, w_pos, atom["text"]))
    preds, meta = run_pair_inference(premises, hypotheses,
                                     InferenceConfig(MODEL_ID, BATCH, MAX_LENGTH, None))

    per_atom: dict[tuple[str, int], list[dict]] = {}
    texts: dict[tuple[str, int], str] = {}
    for (ex, a_pos, w_pos, text), p in zip(index, preds):
        per_atom.setdefault((ex, a_pos), []).append({**p, "window": w_pos})
        texts[(ex, a_pos)] = text

    out_dir.mkdir(parents=True, exist_ok=True)
    claim_rows, atom_rows = [], []
    for r in records:
        if not r["pipeline_ready"]:
            claim_rows.append({"example_id": r["example_id"], "k2": None, "k2_binary": None,
                               "status": "atomizer_failure", "failure_reason": r["failure_reason"]})
            continue
        chosen = []
        for a_pos in range(len(r["atoms"])):
            best = window_rule(per_atom[(r["example_id"], a_pos)])
            chosen.append(best)
            atom_rows.append({"example_id": r["example_id"], "atom_index": a_pos,
                              "atom": texts[(r["example_id"], a_pos)], "best_window": best["window"],
                              "pred_label": best["pred_label"],
                              "window_labels": [o["pred_label"] for o in per_atom[(r["example_id"], a_pos)]]})
        label = aggregate_soft_prob(chosen)   # chosen windows carry the NLI probabilities
        claim_rows.append({"example_id": r["example_id"], "k2": label,
                           "k2_binary": "supported" if label == "supported" else "unsupported",
                           "n_atoms": len(chosen), "status": "scored"})

    for name, rows in [("k2_windowed.jsonl", claim_rows), ("k2_windowed_atoms.jsonl", atom_rows)]:
        with (out_dir / name).open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decision": "K-017 per-document windowing",
        "model_id": MODEL_ID, "max_length": MAX_LENGTH,
        "window_rule": "entailment if any window entails; else contradiction if any contradicts; else neutral",
        "aggregation": "soft_prob_avg (frozen K2 rule)",
        "atoms_input": str(atoms_path.relative_to(ROOT)), "atoms_sha256": sha256_file(atoms_path),
        "claims_sha256": sha256_file(claims_path),
        "n_claims": len(records), "n_scored": len(ready), "n_atomizer_failures": len(records) - len(ready),
        "n_pairs": meta["n_pairs"], "n_truncated_pairs": meta["n_truncated_pairs"],
        "elapsed_seconds": round(meta["elapsed_seconds"], 1),
    }
    (out_dir / "k2_windowed_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
