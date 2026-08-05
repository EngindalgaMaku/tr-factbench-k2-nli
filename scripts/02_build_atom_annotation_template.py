#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

from k2_nli.io import read_jsonl, write_jsonl


def balanced_sample(records: list[dict], per_domain_label: int, seed: int) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in records:
        groups[(str(item["domain"]), str(item["gold_label"]))].append(item)
    selected = []
    for key, items in sorted(groups.items()):
        rng = random.Random(f"{seed}:{key[0]}:{key[1]}")
        candidates = sorted(items, key=lambda x: x["example_id"])
        rng.shuffle(candidates)
        if len(candidates) < per_domain_label:
            raise ValueError(f"Not enough examples in stratum {key}: {len(candidates)}")
        selected.extend(candidates[:per_domain_label])
    return sorted(selected, key=lambda x: (x["domain"], x["gold_label"], x["example_id"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/reviewed/claim_level/dev_stress.jsonl")
    parser.add_argument("--output", default="data/annotation_templates/atom_gold_round1_240.csv")
    parser.add_argument("--manifest", default="data/annotation_templates/atom_gold_round1_240.jsonl")
    parser.add_argument("--per-domain-label", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-atoms", type=int, default=5)
    args = parser.parse_args()

    records = read_jsonl(args.input)
    selected = balanced_sample(records, args.per_domain_label, args.seed)
    write_jsonl(args.manifest, selected)
    fields = [
        "example_id", "context_id", "domain", "context", "question", "claim",
        "claim_gold_label", "existing_atom_count", "gold_atom_count"
    ]
    for index in range(1, args.max_atoms + 1):
        fields.extend([f"gold_atom_{index}", f"gold_atom_{index}_nli"])
    fields.extend([
        "decomposition_complete", "faithful_to_claim", "annotation_status",
        "annotator_id", "review_notes"
    ])
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in selected:
            row = {
                "example_id": item["example_id"],
                "context_id": item["context_id"],
                "domain": item["domain"],
                "context": item["context"],
                "question": item["question"],
                "claim": item["claim"],
                "claim_gold_label": item["gold_label"],
                "existing_atom_count": item.get("atom_count", ""),
                "annotation_status": "pending",
            }
            writer.writerow(row)
    print(f"Wrote {len(selected)} examples to {path}")


if __name__ == "__main__":
    main()
