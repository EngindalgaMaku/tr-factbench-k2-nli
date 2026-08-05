from __future__ import annotations

import json
from pathlib import Path

from k2_nli.experiment_reporting import build_report


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def make_run(root: Path, run_id: str, model_id: str, prediction: str) -> None:
    run = root / "runs" / run_id
    metrics = {
        "accuracy": 1.0 if prediction == "supported" else 0.0,
        "macro_f1": 1.0 if prediction == "supported" else 0.0,
        "weighted_f1": 1.0 if prediction == "supported" else 0.0,
        "mcc": 1.0 if prediction == "supported" else 0.0,
        "classification_report": {
            label: {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1.0}
            for label in ["supported", "partially_supported", "contradicted", "unverifiable"]
        },
        "confusion_matrix": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        "pipeline_summary": {
            "n_claims": 1,
            "n_atoms": 2,
            "mean_atoms_per_claim": 2.0,
            "atom_pred_label_counts": {"entailment": 1, "neutral": 1, "contradiction": 0},
            "atomization_status_counts": {"assistant_draft_high": 1},
        },
        "model_metadata": {
            "model_id": model_id,
            "n_truncated_pairs": 0,
            "pairs_per_second": 10.0,
            "peak_gpu_memory_bytes": 100,
            "model_revision": "abc",
        },
    }
    write_json(run / "metrics.json", metrics)
    write_json(run / "manifest.json", {"run_id": run_id})
    write_jsonl(run / "predictions.jsonl", [{
        "example_id": "e1",
        "context_id": "c1",
        "domain": "finance",
        "claim": "claim",
        "gold_label": "supported",
        "pred_label": prediction,
        "is_correct": prediction == "supported",
        "n_atoms": 2,
        "atomization_status": "assistant_draft_high",
    }])


def test_build_report(tmp_path: Path) -> None:
    make_run(tmp_path, "run_a", "model-a", "supported")
    make_run(tmp_path, "run_b", "model-b", "unverifiable")
    config = {
        "experiment_id": "exp-1",
        "run_ids": ["run_a", "run_b"],
        "notes": ["note"],
        "limitations": ["limitation"],
        "next_steps": ["next"],
    }
    config_path = tmp_path / "configs" / "exp.json"
    write_json(config_path, config)
    output = build_report(config_path, tmp_path)
    assert (output / "README.md").exists()
    assert (output / "report_manifest.json").exists()
    assert (output / "figures" / "model_comparison.svg").exists()
    assert (output / "tables" / "model_metrics.csv").exists()
    assert (tmp_path / "docs" / "EXPERIMENTS.md").exists()
