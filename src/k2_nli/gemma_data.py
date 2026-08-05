from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .atom_data import normalize_atoms
from .io import read_jsonl
from .labels import CLAIM_LABELS

ADAPTER_VERSION = "gemma_pred_atoms_v1"


def _required_text(item: dict[str, Any], field: str, example_id: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or empty {field!r} for {example_id}")
    return value.strip()


def normalize_gemma_record(item: dict[str, Any]) -> dict[str, Any]:
    example_id = _required_text(item, "example_id", "<unknown>")
    gold_label = str(item.get("gold_label") or "").strip().lower()
    if gold_label not in CLAIM_LABELS:
        raise ValueError(f"Unknown or missing gold label {gold_label!r} for {example_id}")

    json_valid = item.get("json_valid")
    if not isinstance(json_valid, bool):
        raise ValueError(f"json_valid must be boolean for {example_id}")
    atom_count_correct = item.get("atom_count_correct")
    if not isinstance(atom_count_correct, bool):
        raise ValueError(f"atom_count_correct must be boolean for {example_id}")

    pred_atoms = item.get("pred_atoms")
    failure_reason: str | None = None
    atoms: list[dict[str, str]] = []
    if not json_valid:
        failure_reason = "invalid_atomizer_json"
    elif not isinstance(pred_atoms, list):
        failure_reason = "pred_atoms_not_list"
    elif not pred_atoms:
        failure_reason = "empty_pred_atoms"
    else:
        try:
            atoms = normalize_atoms(pred_atoms, example_id)
        except ValueError:
            failure_reason = "malformed_pred_atoms"

    return {
        "example_id": example_id,
        "source_example_id": str(item.get("source_example_id") or "").strip(),
        "context_id": str(item.get("context_id") or item.get("source_example_id") or "").strip(),
        "domain": str(item.get("domain") or "").strip(),
        "context": _required_text(item, "context", example_id),
        "question": str(item.get("question") or ""),
        "claim": _required_text(item, "claim", example_id),
        "gold_label": gold_label,
        "atoms": atoms,
        "json_valid": json_valid,
        "atom_count_correct": atom_count_correct,
        "pipeline_ready": failure_reason is None,
        "failure_reason": failure_reason,
        "atomization_id": f"{ADAPTER_VERSION}:{example_id}",
        "atomization_status": "gemma_predicted_valid" if failure_reason is None else "gemma_generation_failure",
        "atomization_notes": None if failure_reason is None else failure_reason,
        "atomization_version": ADAPTER_VERSION,
    }


def load_gemma_predicted_dataset(path: str | Path) -> list[dict[str, Any]]:
    records = [normalize_gemma_record(item) for item in read_jsonl(path)]
    if not records:
        raise ValueError(f"No records found in {path}")
    ids = [item["example_id"] for item in records]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate example_id values in {path}: {duplicates[:10]}")
    return records


def summarize_gemma_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    ready = [item for item in records if item["pipeline_ready"]]
    failures = [item for item in records if not item["pipeline_ready"]]
    return {
        "adapter_version": ADAPTER_VERSION,
        "n_input_claims": len(records),
        "n_pipeline_ready": len(ready),
        "n_atomizer_failures": len(failures),
        "atomizer_coverage": len(ready) / len(records) if records else 0.0,
        "n_predicted_atoms": sum(len(item["atoms"]) for item in ready),
        "gold_label_counts": dict(Counter(item["gold_label"] for item in records)),
        "scored_gold_label_counts": dict(Counter(item["gold_label"] for item in ready)),
        "failure_gold_label_counts": dict(Counter(item["gold_label"] for item in failures)),
        "domain_counts": dict(Counter(item["domain"] or "unspecified" for item in records)),
        "failure_reason_counts": dict(Counter(item["failure_reason"] for item in failures)),
        "json_valid_counts": dict(Counter(str(item["json_valid"]).lower() for item in records)),
        "atom_count_correct_counts": dict(
            Counter(str(item["atom_count_correct"]).lower() for item in records)
        ),
    }
