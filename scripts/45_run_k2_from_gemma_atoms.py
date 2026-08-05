#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from k2_nli.aggregation import aggregate_atom_labels
from k2_nli.gemma_data import load_gemma_predicted_dataset, summarize_gemma_dataset
from k2_nli.gemma_pipeline import build_pipeline_metrics
from k2_nli.io import sha256_file, write_jsonl
from k2_nli.modeling import InferenceConfig, run_pair_inference
from k2_nli.run_utils import base_manifest, create_run_directory, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run zero-shot NLI over Gemma-predicted atoms, preserve atomizer failures as "
            "abstentions, and aggregate valid atom decisions to four claim labels."
        )
    )
    parser.add_argument("--input", required=True, help="JSONL containing context, claim, gold_label and pred_atoms")
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_gemma_predicted_dataset(args.input)
    dataset_summary = summarize_gemma_dataset(records)
    ready_records = [item for item in records if item["pipeline_ready"]]
    failure_records = [item for item in records if not item["pipeline_ready"]]
    if not ready_records:
        raise ValueError("No valid Gemma-predicted atoms were found")

    premises: list[str] = []
    hypotheses: list[str] = []
    atom_index: list[tuple[str, int, str]] = []
    ready_by_id = {item["example_id"]: item for item in ready_records}
    for item in ready_records:
        for atom_position, atom in enumerate(item["atoms"]):
            premises.append(item["context"])
            hypotheses.append(atom["text"])
            atom_index.append((item["example_id"], atom_position, atom["atom_id"]))

    predictions, model_metadata = run_pair_inference(
        premises,
        hypotheses,
        InferenceConfig(args.model, args.batch_size, args.max_length, args.device),
    )

    by_example: dict[str, list[dict]] = {key: [] for key in ready_by_id}
    atom_outputs: list[dict] = []
    for (example_id, atom_position, atom_id), hypothesis, prediction in zip(
        atom_index, hypotheses, predictions
    ):
        atom_output = {
            "example_id": example_id,
            "source_example_id": ready_by_id[example_id]["source_example_id"],
            "atom_id": atom_id,
            "atom_index": atom_position,
            "atom": hypothesis,
            **prediction,
        }
        by_example[example_id].append(atom_output)
        atom_outputs.append(atom_output)

    scored_outputs: list[dict] = []
    scored_by_id: dict[str, dict] = {}
    for item in ready_records:
        example_id = item["example_id"]
        atom_predictions = sorted(by_example[example_id], key=lambda row: row["atom_index"])
        pred_claim = aggregate_atom_labels([row["pred_label"] for row in atom_predictions])
        output = {
            "example_id": example_id,
            "source_example_id": item["source_example_id"],
            "context_id": item["context_id"],
            "domain": item["domain"],
            "question": item["question"],
            "context": item["context"],
            "claim": item["claim"],
            "gold_label": item["gold_label"],
            "pred_label": pred_claim,
            "is_correct": pred_claim == item["gold_label"],
            "pipeline_status": "scored",
            "failure_reason": None,
            "n_atoms": len(atom_predictions),
            "atoms": atom_predictions,
            "json_valid": item["json_valid"],
            "atom_count_correct": item["atom_count_correct"],
            "atomization_id": item["atomization_id"],
            "atomization_status": item["atomization_status"],
            "atomization_notes": item["atomization_notes"],
            "atomization_version": item["atomization_version"],
        }
        scored_outputs.append(output)
        scored_by_id[example_id] = output

    failures: list[dict] = []
    failure_by_id: dict[str, dict] = {}
    for item in failure_records:
        output = {
            "example_id": item["example_id"],
            "source_example_id": item["source_example_id"],
            "context_id": item["context_id"],
            "domain": item["domain"],
            "question": item["question"],
            "context": item["context"],
            "claim": item["claim"],
            "gold_label": item["gold_label"],
            "pred_label": None,
            "is_correct": False,
            "pipeline_status": "atomizer_failure",
            "failure_reason": item["failure_reason"],
            "n_atoms": 0,
            "atoms": [],
            "json_valid": item["json_valid"],
            "atom_count_correct": item["atom_count_correct"],
            "atomization_id": item["atomization_id"],
            "atomization_status": item["atomization_status"],
            "atomization_notes": item["atomization_notes"],
            "atomization_version": item["atomization_version"],
        }
        failures.append(output)
        failure_by_id[item["example_id"]] = output

    all_outputs = [
        scored_by_id.get(item["example_id"]) or failure_by_id[item["example_id"]]
        for item in records
    ]

    run_dir = create_run_directory(args.runs_dir, args.run_id)
    write_jsonl(run_dir / "predictions.jsonl", all_outputs)
    write_jsonl(run_dir / "scored_predictions.jsonl", scored_outputs)
    write_jsonl(run_dir / "atom_predictions.jsonl", atom_outputs)
    write_jsonl(run_dir / "atomizer_failures.jsonl", failures)

    metrics = build_pipeline_metrics(
        records,
        scored_outputs,
        atom_outputs,
        model_metadata,
        dataset_summary,
    )
    write_json(run_dir / "metrics.json", metrics)

    manifest = base_manifest(args.input, vars(args))
    manifest.update({
        "input_mode": "gemma_pred_atoms_jsonl",
        "input_path": str(Path(args.input).resolve()),
        "input_sha256": sha256_file(args.input),
        "evaluation_scope": "four-class metrics on valid atomizations; strict accuracy counts failures as incorrect",
        "atomizer_failure_policy": "abstain; do not assign an arbitrary four-class fallback label",
        "model_metadata": model_metadata,
    })
    write_json(run_dir / "manifest.json", manifest)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
