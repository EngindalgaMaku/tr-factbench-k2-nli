from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from .labels import CLAIM_LABELS
from .metrics import evaluate_predictions


def build_pipeline_metrics(
    all_records: list[dict[str, Any]],
    scored_outputs: list[dict[str, Any]],
    atom_outputs: list[dict[str, Any]],
    model_metadata: dict[str, Any],
    dataset_summary: dict[str, Any],
) -> dict[str, Any]:
    if not scored_outputs:
        raise ValueError("No valid Gemma atomizations are available for NLI evaluation")

    probabilities = np.zeros((len(scored_outputs), len(CLAIM_LABELS)), dtype=float)
    for row, item in enumerate(scored_outputs):
        probabilities[row, CLAIM_LABELS.index(item["pred_label"])] = 1.0
    metrics = evaluate_predictions(
        [item["gold_label"] for item in scored_outputs],
        [item["pred_label"] for item in scored_outputs],
        probabilities,
        CLAIM_LABELS,
    )
    metrics.pop("nll", None)
    metrics.pop("multiclass_brier", None)
    metrics.pop("ece", None)

    n_total = len(all_records)
    n_scored = len(scored_outputs)
    n_correct = sum(bool(item["is_correct"]) for item in scored_outputs)
    atom_counts = [int(item["n_atoms"]) for item in scored_outputs]
    metrics["evaluation_scope"] = "valid_atomizations_only"
    metrics["strict_end_to_end"] = {
        "n_input_claims": n_total,
        "n_scored_claims": n_scored,
        "n_atomizer_failures": n_total - n_scored,
        "coverage": n_scored / n_total if n_total else 0.0,
        "n_correct_scored_claims": n_correct,
        "accuracy_failures_counted_as_incorrect": n_correct / n_total if n_total else 0.0,
        "macro_f1": None,
        "macro_f1_note": (
            "Strict Macro-F1 is not reported because atomizer failures are abstentions rather than "
            "one of the four claim labels. Adding an arbitrary fallback label would distort the result."
        ),
    }
    metrics["pipeline_summary"] = {
        **dataset_summary,
        "n_scored_claims": n_scored,
        "n_atoms": len(atom_outputs),
        "mean_atoms_per_scored_claim": sum(atom_counts) / n_scored,
        "min_atoms_per_scored_claim": min(atom_counts),
        "max_atoms_per_scored_claim": max(atom_counts),
        "pred_label_counts": dict(Counter(item["pred_label"] for item in scored_outputs)),
        "atom_pred_label_counts": dict(Counter(item["pred_label"] for item in atom_outputs)),
    }
    metrics["model_metadata"] = model_metadata
    return metrics
