from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .io import read_jsonl, sha256_file
from .labels import CLAIM_LABELS

REQUIRED_CLAIM_FIELDS = {
    "example_id", "context_id", "domain", "context", "question", "claim", "gold_label"
}


def validate_claim_dataset(path: str | Path) -> dict[str, Any]:
    records = read_jsonl(path)
    errors: list[str] = []
    warnings: list[str] = []
    example_ids: set[str] = set()
    context_to_labels: dict[str, list[str]] = defaultdict(list)

    for index, item in enumerate(records, start=1):
        missing = REQUIRED_CLAIM_FIELDS - set(item)
        if missing:
            errors.append(f"row {index}: missing fields {sorted(missing)}")
            continue
        ex_id = str(item["example_id"])
        if ex_id in example_ids:
            errors.append(f"duplicate example_id: {ex_id}")
        example_ids.add(ex_id)
        label = str(item["gold_label"]).strip().lower()
        if label not in CLAIM_LABELS:
            errors.append(f"row {index}: unsupported gold_label={label!r}")
        for field in ("context_id", "domain", "context", "question", "claim"):
            if not str(item[field]).strip():
                errors.append(f"row {index}: blank {field}")
        context_to_labels[str(item["context_id"])].append(label)

    incomplete_contexts = {
        context_id: labels
        for context_id, labels in context_to_labels.items()
        if set(labels) != set(CLAIM_LABELS) or len(labels) != 4
    }
    if incomplete_contexts:
        warnings.append(
            f"{len(incomplete_contexts)} context groups do not contain exactly one example per claim label"
        )

    label_counts = Counter(str(x.get("gold_label", "")) for x in records)
    domain_counts = Counter(str(x.get("domain", "")) for x in records)
    status_counts = Counter(str(x.get("annotation_status", "missing")) for x in records)

    return {
        "path": str(Path(path).resolve()),
        "sha256": sha256_file(path),
        "n_examples": len(records),
        "n_contexts": len(context_to_labels),
        "n_unique_claims": len({str(x.get("claim", "")) for x in records}),
        "label_counts": dict(sorted(label_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "annotation_status_counts": dict(sorted(status_counts.items())),
        "n_errors": len(errors),
        "n_warnings": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }
