#!/usr/bin/env python3
"""
60_validate_softprob_on_dev.py
Post-hoc validation: soft_prob_avg was introduced and first measured on Gold 480.
This script checks whether the flat -> soft_prob_avg gain also holds on the two
development runs that never touched the gold set:
  - K2-ATOM-ASSISTED-ZS-PILOT-v1.1 (200 examples, human-assisted atoms)
  - K2-PIPE-PRED-ZS-ATOMIZERTEST-v1 (Gemma-predicted atoms, atomizer test split)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from scipy.stats import binomtest  # noqa: E402
from sklearn.metrics import accuracy_score, f1_score  # noqa: E402

from k2_nli.aggregation_ablation import aggregate_flat, aggregate_soft_prob  # noqa: E402

LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
RUNS = [
    "K2-ATOM-ASSISTED-ZS-PILOT-v1.1__mdeberta_base_2mil7",
    "K2-PIPE-PRED-ZS-ATOMIZERTEST-v1__mdeberta_base_2mil7",
]

out = {}
for run in RUNS:
    p = f"runs/{run}/scored_predictions.jsonl"
    p = p if os.path.exists(p) else f"runs/{run}/predictions.jsonl"
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r.get("atoms")]
    y = [r["gold_label"] for r in rows]
    flat = [aggregate_flat([a["pred_label"] for a in r["atoms"]]) for r in rows]
    soft = [aggregate_soft_prob(r["atoms"]) for r in rows]
    so = sum(s == g and f != g for g, f, s in zip(y, flat, soft))
    fo = sum(f == g and s != g for g, f, s in zip(y, flat, soft))
    pval = 1.0 if so + fo == 0 else binomtest(min(so, fo), so + fo, 0.5).pvalue
    out[run] = {
        "n": len(rows),
        "flat_acc": round(accuracy_score(y, flat), 4),
        "flat_macro_f1": round(f1_score(y, flat, labels=LABELS, average="macro", zero_division=0), 4),
        "soft_acc": round(accuracy_score(y, soft), 4),
        "soft_macro_f1": round(f1_score(y, soft, labels=LABELS, average="macro", zero_division=0), 4),
        "changed": sum(a != b for a, b in zip(flat, soft)),
        "soft_only_correct": so,
        "flat_only_correct": fo,
        "mcnemar_p_exact": round(float(pval), 5),
    }

Path("reports/experiments/AUDIT-K2-K3-v1").mkdir(parents=True, exist_ok=True)
Path("reports/experiments/AUDIT-K2-K3-v1/softprob_dev_validation.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
