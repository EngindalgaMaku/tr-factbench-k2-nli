from __future__ import annotations

NLI_LABELS = ("entailment", "neutral", "contradiction")
CLAIM_LABELS = ("supported", "partially_supported", "contradicted", "unverifiable")

CLAIM_TO_NLI3 = {
    "supported": "entailment",
    "contradicted": "contradiction",
    "unverifiable": "neutral",
    "partially_supported": None,
}

LEGACY_CLAIM_TO_NLI3 = {
    "unsupported": "neutral",
    "insufficient_information": "neutral",
}


def claim_to_nli3(label: str) -> str | None:
    normalized = label.strip().lower()
    if normalized in CLAIM_TO_NLI3:
        return CLAIM_TO_NLI3[normalized]
    if normalized in LEGACY_CLAIM_TO_NLI3:
        return LEGACY_CLAIM_TO_NLI3[normalized]
    raise ValueError(f"Unknown claim label: {label!r}")


def normalize_nli_label(label: str) -> str:
    value = label.strip().lower()
    if "entail" in value:
        return "entailment"
    if "neutral" in value:
        return "neutral"
    if "contradict" in value:
        return "contradiction"
    raise ValueError(f"Cannot normalize NLI label: {label!r}")
