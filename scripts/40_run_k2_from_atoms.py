#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from k2_nli.aggregation import aggregate_atom_labels
from k2_nli.io import read_jsonl, stable_text_hash, write_jsonl
from k2_nli.labels import CLAIM_LABELS
from k2_nli.metrics import evaluate_predictions
from k2_nli.modeling import InferenceConfig, run_pair_inference
from k2_nli.run_utils import base_manifest, create_run_directory, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Claim JSONL with context and gold_label")
    parser.add_argument("--atoms", required=True, help="Precomputed atom JSONL")
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    claims = {x["example_id"]: x for x in read_jsonl(args.data)}
    atom_records = {x["example_id"]: x for x in read_jsonl(args.atoms)}
    if set(claims) != set(atom_records):
        missing_atoms = sorted(set(claims) - set(atom_records))[:10]
        extra_atoms = sorted(set(atom_records) - set(claims))[:10]
        raise ValueError(f"Claim/atom ID mismatch. missing_atoms={missing_atoms}, extra_atoms={extra_atoms}")

    premises: list[str] = []
    hypotheses: list[str] = []
    atom_index: list[tuple[str, int]] = []
    for example_id in sorted(claims):
        claim = claims[example_id]
        atom_item = atom_records[example_id]
        expected_hash = stable_text_hash(str(claim["claim"]))
        if atom_item.get("claim_hash") and atom_item["claim_hash"] != expected_hash:
            raise ValueError(f"Claim hash mismatch for {example_id}")
        atoms = atom_item.get("atoms")
        if not isinstance(atoms, list) or not atoms or not all(isinstance(x, str) and x.strip() for x in atoms):
            raise ValueError(f"Invalid atoms for {example_id}")
        for atom_position, atom in enumerate(atoms):
            premises.append(str(claim["context"]))
            hypotheses.append(atom.strip())
            atom_index.append((example_id, atom_position))

    predictions, model_metadata = run_pair_inference(
        premises,
        hypotheses,
        InferenceConfig(args.model, args.batch_size, args.max_length, args.device),
    )
    by_example: dict[str, list[dict]] = {key: [] for key in claims}
    for (example_id, atom_position), hypothesis, prediction in zip(atom_index, hypotheses, predictions):
        by_example[example_id].append({
            "atom_index": atom_position,
            "atom": hypothesis,
            **prediction,
        })

    outputs = []
    for example_id in sorted(claims):
        claim = claims[example_id]
        atom_predictions = sorted(by_example[example_id], key=lambda x: x["atom_index"])
        pred_claim = aggregate_atom_labels([x["pred_label"] for x in atom_predictions])
        outputs.append({
            "example_id": example_id,
            "context_id": claim["context_id"],
            "domain": claim["domain"],
            "gold_label": claim["gold_label"],
            "pred_label": pred_claim,
            "n_atoms": len(atom_predictions),
            "atoms": atom_predictions,
            "atomizer_version": atom_records[example_id].get("atomizer_version"),
        })

    run_dir = create_run_directory(args.runs_dir, args.run_id)
    write_jsonl(run_dir / "predictions.jsonl", outputs)
    # Claim aggregation is deterministic over hard atom labels; one-hot probabilities are used only
    # so the shared metric function can compute classification metrics. Calibration metrics are omitted.
    prob = np.zeros((len(outputs), len(CLAIM_LABELS)), dtype=float)
    for row, item in enumerate(outputs):
        prob[row, CLAIM_LABELS.index(item["pred_label"])] = 1.0
    metrics = evaluate_predictions(
        [x["gold_label"] for x in outputs],
        [x["pred_label"] for x in outputs],
        prob,
        CLAIM_LABELS,
    )
    metrics.pop("nll", None)
    metrics.pop("multiclass_brier", None)
    metrics.pop("ece", None)
    metrics["model_metadata"] = model_metadata
    write_json(run_dir / "metrics.json", metrics)
    manifest = base_manifest(args.data, vars(args))
    manifest["atoms_path"] = str(Path(args.atoms).resolve())
    manifest["model_metadata"] = model_metadata
    write_json(run_dir / "manifest.json", manifest)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
