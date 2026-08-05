#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from k2_nli.io import read_jsonl
from k2_nli.labels import NLI_LABELS
from k2_nli.run_utils import write_json
from k2_nli.statistics import exact_mcnemar, paired_bootstrap_macro_f1_difference


def load_run(path: str) -> dict[str, dict]:
    records = read_jsonl(Path(path) / "predictions.jsonl")
    return {x["example_id"]: x for x in records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-a", required=True)
    parser.add_argument("--run-b", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    a = load_run(args.run_a)
    b = load_run(args.run_b)
    ids = sorted(set(a) & set(b))
    if len(ids) != len(a) or len(ids) != len(b):
        raise ValueError("Runs do not contain exactly the same example IDs")
    y_true = [a[i]["gold_label"] for i in ids]
    if any(b[i]["gold_label"] != a[i]["gold_label"] for i in ids):
        raise ValueError("Gold labels differ between runs")
    pred_a = [a[i]["pred_label"] for i in ids]
    pred_b = [b[i]["pred_label"] for i in ids]
    output = {
        "run_a": args.run_a,
        "run_b": args.run_b,
        "n_examples": len(ids),
        "paired_bootstrap": paired_bootstrap_macro_f1_difference(
            y_true, pred_a, pred_b, list(NLI_LABELS), args.bootstrap_samples, args.seed
        ),
        "mcnemar": exact_mcnemar(y_true, pred_a, pred_b),
    }
    write_json(args.output, output)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
