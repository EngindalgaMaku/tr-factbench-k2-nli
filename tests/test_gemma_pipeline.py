from __future__ import annotations

from k2_nli.gemma_pipeline import build_pipeline_metrics


def test_strict_accuracy_counts_atomizer_failure_as_incorrect():
    records = [
        {"example_id": "ex1"},
        {"example_id": "ex2"},
        {"example_id": "ex3"},
    ]
    scored = [
        {
            "example_id": "ex1",
            "gold_label": "supported",
            "pred_label": "supported",
            "is_correct": True,
            "n_atoms": 1,
        },
        {
            "example_id": "ex2",
            "gold_label": "contradicted",
            "pred_label": "unverifiable",
            "is_correct": False,
            "n_atoms": 2,
        },
    ]
    atom_outputs = [
        {"pred_label": "entailment"},
        {"pred_label": "neutral"},
        {"pred_label": "neutral"},
    ]
    dataset_summary = {
        "n_input_claims": 3,
        "n_pipeline_ready": 2,
        "n_atomizer_failures": 1,
        "atomizer_coverage": 2 / 3,
    }
    metrics = build_pipeline_metrics(
        records,
        scored,
        atom_outputs,
        {"model_id": "dummy"},
        dataset_summary,
    )
    assert metrics["accuracy"] == 0.5
    assert metrics["strict_end_to_end"]["accuracy_failures_counted_as_incorrect"] == 1 / 3
    assert metrics["strict_end_to_end"]["macro_f1"] is None
    assert metrics["pipeline_summary"]["n_atoms"] == 3
