#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from k2_nli.io import read_jsonl, write_jsonl
from k2_nli.labels import NLI_LABELS
from k2_nli.metrics import evaluate_predictions
from k2_nli.modeling import InferenceConfig, run_pair_inference
from k2_nli.run_utils import base_manifest, create_run_directory, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    records = read_jsonl(args.data)
    required = {"premise", "hypothesis", "nli_label"}
    for index, item in enumerate(records, start=1):
        missing = required - set(item)
        if missing:
            raise ValueError(f"Row {index} missing {sorted(missing)}")

    run_dir = create_run_directory(args.runs_dir, args.run_id)
    config = InferenceConfig(
        model_id=args.model,
        batch_size=args.batch_size,
        max_length=args.max_length,
        device=args.device,
    )
    predictions, model_metadata = run_pair_inference(
        [x["premise"] for x in records],
        [x["hypothesis"] for x in records],
        config,
    )
    output_records = []
    for item, prediction in zip(records, predictions):
        output_records.append({
            "example_id": item["example_id"],
            "context_id": item["context_id"],
            "domain": item["domain"],
            "k2_split": item.get("k2_split"),
            "gold_label": item["nli_label"],
            "claim_gold_label": item.get("gold_label"),
            "context_chars": len(item["premise"]),
            "hypothesis_chars": len(item["hypothesis"]),
            **prediction,
        })
    write_jsonl(run_dir / "predictions.jsonl", output_records)

    probability_matrix = np.array([
        [x["prob_entailment"], x["prob_neutral"], x["prob_contradiction"]]
        for x in output_records
    ])
    metrics = evaluate_predictions(
        [x["gold_label"] for x in output_records],
        [x["pred_label"] for x in output_records],
        probability_matrix,
        NLI_LABELS,
    )
    metrics["model_metadata"] = model_metadata
    write_json(run_dir / "metrics.json", metrics)
    manifest = base_manifest(args.data, vars(args))
    manifest["model_metadata"] = model_metadata
    write_json(run_dir / "manifest.json", manifest)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
