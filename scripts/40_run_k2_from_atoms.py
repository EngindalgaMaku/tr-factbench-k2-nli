#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from k2_nli.aggregation import aggregate_atom_labels
from k2_nli.atom_data import load_combined_atom_dataset, load_separate_atom_dataset
from k2_nli.io import sha256_file, write_jsonl
from k2_nli.labels import CLAIM_LABELS
from k2_nli.metrics import evaluate_predictions
from k2_nli.modeling import InferenceConfig, run_pair_inference
from k2_nli.run_utils import base_manifest, create_run_directory, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run atom-level zero-shot NLI and aggregate atom decisions to four claim labels."
    )
    parser.add_argument(
        "--input",
        help="Combined JSONL containing context, claim, gold_label and atoms. Preferred mode.",
    )
    parser.add_argument("--data", help="Legacy claim JSONL used together with --atoms")
    parser.add_argument("--atoms", help="Legacy precomputed atom JSONL used together with --data")
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    if args.input:
        if args.data or args.atoms:
            parser.error("Use either --input or the legacy --data/--atoms pair, not both.")
    elif not (args.data and args.atoms):
        parser.error("Provide --input, or provide both --data and --atoms.")
    return args


def main() -> None:
    args = parse_args()
    if args.input:
        records = load_combined_atom_dataset(args.input)
        manifest_source = args.input
    else:
        records = load_separate_atom_dataset(args.data, args.atoms)
        manifest_source = args.data

    premises: list[str] = []
    hypotheses: list[str] = []
    atom_index: list[tuple[str, int, str]] = []
    records_by_id = {item["example_id"]: item for item in records}

    for item in records:
        for atom_position, atom in enumerate(item["atoms"]):
            premises.append(item["context"])
            hypotheses.append(atom["text"])
            atom_index.append((item["example_id"], atom_position, atom["atom_id"]))

    predictions, model_metadata = run_pair_inference(
        premises,
        hypotheses,
        InferenceConfig(args.model, args.batch_size, args.max_length, args.device),
    )

    by_example: dict[str, list[dict]] = {key: [] for key in records_by_id}
    flat_atom_outputs: list[dict] = []
    for (example_id, atom_position, atom_id), hypothesis, prediction in zip(
        atom_index, hypotheses, predictions
    ):
        atom_output = {
            "example_id": example_id,
            "atom_id": atom_id,
            "atom_index": atom_position,
            "atom": hypothesis,
            **prediction,
        }
        by_example[example_id].append(atom_output)
        flat_atom_outputs.append(atom_output)

    outputs = []
    for item in records:
        example_id = item["example_id"]
        atom_predictions = sorted(by_example[example_id], key=lambda x: x["atom_index"])
        pred_claim = aggregate_atom_labels([x["pred_label"] for x in atom_predictions])
        outputs.append({
            "example_id": example_id,
            "context_id": item["context_id"],
            "domain": item["domain"],
            "question": item["question"],
            "claim": item["claim"],
            "gold_label": item["gold_label"],
            "pred_label": pred_claim,
            "is_correct": pred_claim == item["gold_label"],
            "n_atoms": len(atom_predictions),
            "atoms": atom_predictions,
            "atomization_id": item.get("atomization_id"),
            "atomization_status": item.get("atomization_status"),
            "atomization_notes": item.get("atomization_notes"),
            "atomization_version": item.get("atomization_version"),
        })

    run_dir = create_run_directory(args.runs_dir, args.run_id)
    write_jsonl(run_dir / "predictions.jsonl", outputs)
    write_jsonl(run_dir / "atom_predictions.jsonl", flat_atom_outputs)

    # Claim aggregation is deterministic over hard atom labels. One-hot claim probabilities are
    # used only to reuse the shared classification metric function; calibration metrics are omitted.
    probabilities = np.zeros((len(outputs), len(CLAIM_LABELS)), dtype=float)
    for row, item in enumerate(outputs):
        probabilities[row, CLAIM_LABELS.index(item["pred_label"])] = 1.0
    metrics = evaluate_predictions(
        [x["gold_label"] for x in outputs],
        [x["pred_label"] for x in outputs],
        probabilities,
        CLAIM_LABELS,
    )
    metrics.pop("nll", None)
    metrics.pop("multiclass_brier", None)
    metrics.pop("ece", None)
    metrics["pipeline_summary"] = {
        "n_claims": len(outputs),
        "n_atoms": len(flat_atom_outputs),
        "mean_atoms_per_claim": len(flat_atom_outputs) / len(outputs),
        "min_atoms_per_claim": min(x["n_atoms"] for x in outputs),
        "max_atoms_per_claim": max(x["n_atoms"] for x in outputs),
        "gold_label_counts": dict(Counter(x["gold_label"] for x in outputs)),
        "pred_label_counts": dict(Counter(x["pred_label"] for x in outputs)),
        "atom_pred_label_counts": dict(Counter(x["pred_label"] for x in flat_atom_outputs)),
        "atomization_status_counts": dict(
            Counter(str(x.get("atomization_status") or "unspecified") for x in outputs)
        ),
    }
    metrics["model_metadata"] = model_metadata
    write_json(run_dir / "metrics.json", metrics)

    manifest = base_manifest(manifest_source, vars(args))
    if args.input:
        manifest["input_mode"] = "combined_atom_jsonl"
        manifest["atom_input_path"] = str(Path(args.input).resolve())
        manifest["atom_input_sha256"] = sha256_file(args.input)
    else:
        manifest["input_mode"] = "separate_claim_and_atom_jsonl"
        manifest["atoms_path"] = str(Path(args.atoms).resolve())
        manifest["atoms_sha256"] = sha256_file(args.atoms)
    manifest["model_metadata"] = model_metadata
    write_json(run_dir / "manifest.json", manifest)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
