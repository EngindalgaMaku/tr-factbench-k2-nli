from __future__ import annotations

import random
from collections import defaultdict


def split_general_by_context(
    records: list[dict],
    seed: int = 42,
    selection_per_domain: int = 54,
    calibration_per_domain: int = 13,
) -> dict[str, list[dict]]:
    context_domain: dict[str, str] = {}
    contexts_by_domain: dict[str, list[str]] = defaultdict(list)
    for item in records:
        context_id = str(item["context_id"])
        domain = str(item["domain"])
        if context_id in context_domain and context_domain[context_id] != domain:
            raise ValueError(f"Context {context_id} appears in multiple domains")
        if context_id not in context_domain:
            context_domain[context_id] = domain
            contexts_by_domain[domain].append(context_id)

    assignments: dict[str, str] = {}
    for domain, context_ids in sorted(contexts_by_domain.items()):
        ids = sorted(context_ids)
        random.Random(f"{seed}:{domain}").shuffle(ids)
        required = selection_per_domain + calibration_per_domain
        if len(ids) < required:
            raise ValueError(f"Not enough contexts for domain {domain}: {len(ids)} < {required}")
        for context_id in ids[:selection_per_domain]:
            assignments[context_id] = "model_selection"
        start = selection_per_domain
        stop = start + calibration_per_domain
        for context_id in ids[start:stop]:
            assignments[context_id] = "calibration"
        for context_id in ids[stop:]:
            assignments[context_id] = "internal_eval"

    result = {"model_selection": [], "calibration": [], "internal_eval": []}
    for item in records:
        split_name = assignments[str(item["context_id"])]
        result[split_name].append({**item, "k2_split": split_name})
    return result
