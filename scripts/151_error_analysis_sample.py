#!/usr/bin/env python3
"""
151_error_analysis_sample.py
Draws the error-analysis sample for K-028: false alarms of the final system (Hybrid PA) -- gold "supported",
PA "unsupported" -- 10 per slice, seed 42, and writes them with full context, all system outputs and the V4
judge rationale to docs/ap6v2_error_sample.jsonl (for reading and coding; categories fixed in K-028).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLICES = {
    "medical": ("data/ragbench/medical/build", "ragbench_tr_medical_claims.jsonl"),
    "legal": ("data/claimrag_law/build", "claimrag_tr_law_claims.jsonl"),
    "finance": ("data/findver/build", "findver_tr_finance_claims.jsonl"),
}
PER_SLICE, SEED = 10, 42


def main() -> None:
    out = []
    for name, (build, claims_file) in SLICES.items():
        b = ROOT / build
        claims = {json.loads(l)["example_id"]: json.loads(l) for l in (b / claims_file).open(encoding="utf-8")}
        preds = [json.loads(l) for l in (b / "predictions" / "system_predictions.jsonl").open(encoding="utf-8")]
        judge = {json.loads(l)["example_id"]: json.loads(l) for l in (b / "predictions" / "v4_judge.jsonl").open(encoding="utf-8")}
        fa = [p for p in preds if p["gold_binary"] == "supported" and p["hybrid_PA"] != "supported"]
        pick = sorted(random.Random(SEED).sample(fa, PER_SLICE), key=lambda p: p["example_id"])
        for p in pick:
            c = claims[p["example_id"]]
            out.append({"slice": name, "example_id": p["example_id"], "n_false_alarms_in_slice": len(fa),
                        "question": c["question"], "claim": c["claim"], "context": c["context"],
                        "gold": c["gold_label"], "k1": p["k1"], "k1_truncated": p["k1_truncated"], "k2": p["k2"],
                        "route": p["route"], "v4_judge": p["v4_judge"], "gemma": p["gemma26b_zero_shot"],
                        "hybrid_PA": p["hybrid_PA"],
                        "judge_reasoning": judge.get(p["example_id"], {}).get("reasoning")})
    path = ROOT / "docs" / "ap6v2_error_sample.jsonl"
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(path, len(out), {s: out[[r["slice"] for r in out].index(s)]["n_false_alarms_in_slice"] for s in SLICES})


if __name__ == "__main__":
    main()
