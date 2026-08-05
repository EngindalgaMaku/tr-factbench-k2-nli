from __future__ import annotations

import json
from pathlib import Path

from k2_nli.gemma_reporting import build_gemma_pipeline_report


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def test_build_gemma_pipeline_report(tmp_path):
    run_id = "test_run"
    run_dir = tmp_path / "runs" / run_id
    metrics = {
        "evaluation_scope": "valid_atomizations_only",
        "n_examples": 1,
        "labels": ["supported", "partially_supported", "contradicted", "unverifiable"],
        "accuracy": 1.0,
        "macro_f1": 0.25,
        "weighted_f1": 1.0,
        "mcc": 0.0,
        "classification_report": {
            "supported": {"precision": 1.0, "recall": 1.0, "f1-score": 1.0, "support": 1.0},
            "partially_supported": {"precision": 0.0, "recall": 0.0, "f1-score": 0.0, "support": 0.0},
            "contradicted": {"precision": 0.0, "recall": 0.0, "f1-score": 0.0, "support": 0.0},
            "unverifiable": {"precision": 0.0, "recall": 0.0, "f1-score": 0.0, "support": 0.0},
        },
        "confusion_matrix": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        "strict_end_to_end": {
            "n_input_claims": 2,
            "n_scored_claims": 1,
            "n_atomizer_failures": 1,
            "coverage": 0.5,
            "accuracy_failures_counted_as_incorrect": 0.5,
        },
        "pipeline_summary": {
            "n_atoms": 1,
            "atom_pred_label_counts": {"entailment": 1},
        },
        "model_metadata": {
            "model_id": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
            "n_truncated_pairs": 0,
            "pairs_per_second": 10.0,
            "peak_gpu_memory_bytes": 1,
            "model_revision": "rev",
        },
    }
    _write_json(run_dir / "metrics.json", metrics)
    _write_json(run_dir / "manifest.json", {"arguments": {"input": "data/input.jsonl", "model": "model", "run_id": run_id}})
    scored = [{
        "example_id": "ex1", "source_example_id": "src1", "domain": "legal",
        "gold_label": "supported", "pred_label": "supported", "is_correct": True,
        "pipeline_status": "scored", "n_atoms": 1, "json_valid": True,
        "atom_count_correct": True,
    }]
    failure = [{
        "example_id": "ex2", "source_example_id": "src2", "domain": "legal",
        "gold_label": "supported", "pred_label": None, "is_correct": False,
        "pipeline_status": "atomizer_failure", "failure_reason": "invalid_atomizer_json",
        "n_atoms": 0, "json_valid": False, "atom_count_correct": False, "claim": "claim",
    }]
    _write_jsonl(run_dir / "predictions.jsonl", [*scored, *failure])
    _write_jsonl(run_dir / "scored_predictions.jsonl", scored)
    _write_jsonl(run_dir / "atom_predictions.jsonl", [{"pred_label": "entailment"}])
    _write_jsonl(run_dir / "atomizer_failures.jsonl", failure)

    config_path = tmp_path / "configs" / "experiments" / "experiment.json"
    _write_json(config_path, {
        "experiment_id": "TEST-GEMMA",
        "title": "Test",
        "run_id": run_id,
        "runs_dir": "runs",
        "reports_dir": "reports/experiments",
        "registry_path": "docs/EXPERIMENTS.md",
    })

    output = build_gemma_pipeline_report(config_path, tmp_path)
    assert (output / "README.md").exists()
    assert (output / "tables" / "pipeline_metrics.csv").exists()
    assert (output / "figures" / "pipeline_scores.svg").exists()
    assert "TEST-GEMMA" in (tmp_path / "docs" / "EXPERIMENTS.md").read_text(encoding="utf-8")
