from __future__ import annotations

from .labels import NLI_LABELS


def aggregate_atom_labels(labels: list[str]) -> str:
    if not labels:
        raise ValueError("At least one atom label is required")
    normalized = [x.strip().lower() for x in labels]
    unknown = set(normalized) - set(NLI_LABELS)
    if unknown:
        raise ValueError(f"Unknown atom labels: {sorted(unknown)}")
    if all(x == "entailment" for x in normalized):
        return "supported"
    if "entailment" in normalized:
        return "partially_supported"
    if "contradiction" in normalized:
        return "contradicted"
    return "unverifiable"
