#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import pandas as pd

from k2_nli.io import read_jsonl
from k2_nli.labels import NLI_LABELS
from k2_nli.statistics import exact_mcnemar, paired_bootstrap_macro_f1_difference


def holm_adjust(p_values: list[float]) -> list[float]:
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [1.0] * m
    running = 0.0
    for rank, index in enumerate(order):
        value = min(1.0, (m - rank) * p_values[index])
        running = max(running, value)
        adjusted[index] = running
    return adjusted


def load_run(path: Path) -> dict[str, dict]:
    return {x["example_id"]: x for x in read_jsonl(path / "predictions.jsonl")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--output-dir", default="reports/tables")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_paths = [Path(x) for x in args.runs]
    run_data = {path.name: load_run(path) for path in run_paths}
    names = sorted(run_data)
    rows = []
    for name_a, name_b in itertools.combinations(names, 2):
        a = run_data[name_a]
        b = run_data[name_b]
        ids = sorted(set(a) & set(b))
        if len(ids) != len(a) or len(ids) != len(b):
            raise ValueError(f"Run ID mismatch: {name_a} vs {name_b}")
        y_true = [a[i]["gold_label"] for i in ids]
        if any(b[i]["gold_label"] != a[i]["gold_label"] for i in ids):
            raise ValueError(f"Gold label mismatch: {name_a} vs {name_b}")
        pred_a = [a[i]["pred_label"] for i in ids]
        pred_b = [b[i]["pred_label"] for i in ids]
        bootstrap = paired_bootstrap_macro_f1_difference(
            y_true, pred_a, pred_b, list(NLI_LABELS), args.bootstrap_samples, args.seed
        )
        mcnemar = exact_mcnemar(y_true, pred_a, pred_b)
        rows.append({
            "run_a": name_a,
            "run_b": name_b,
            "n_examples": len(ids),
            "macro_f1_difference_a_minus_b": bootstrap["difference"],
            "difference_ci95_low": bootstrap["ci95"][0],
            "difference_ci95_high": bootstrap["ci95"][1],
            "mcnemar_a_correct_b_wrong": mcnemar["a_correct_b_wrong"],
            "mcnemar_a_wrong_b_correct": mcnemar["a_wrong_b_correct"],
            "mcnemar_p": mcnemar["p_value"],
        })
    adjusted = holm_adjust([row["mcnemar_p"] for row in rows])
    for row, p_adjusted in zip(rows, adjusted):
        row["mcnemar_p_holm"] = p_adjusted

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output / "pairwise_model_comparisons.csv", index=False)
    (output / "pairwise_model_comparisons.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
