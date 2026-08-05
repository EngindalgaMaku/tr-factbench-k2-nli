#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from k2_nli.aggregation import aggregate_atom_labels
from k2_nli.io import write_jsonl
from k2_nli.labels import NLI_LABELS


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "evet", "tamam", "complete"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--errors", default=None)
    parser.add_argument("--max-atoms", type=int, default=5)
    args = parser.parse_args()

    valid = []
    errors = []
    with Path(args.input).open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            ex_id = row.get("example_id", "").strip()
            status = row.get("annotation_status", "").strip().lower()
            if status not in {"complete", "completed", "reviewed", "adjudicated"}:
                errors.append({"row": row_number, "example_id": ex_id, "error": "annotation_not_complete"})
                continue
            try:
                atom_count = int(row.get("gold_atom_count", ""))
            except ValueError:
                errors.append({"row": row_number, "example_id": ex_id, "error": "invalid_gold_atom_count"})
                continue
            if not 1 <= atom_count <= args.max_atoms:
                errors.append({"row": row_number, "example_id": ex_id, "error": "gold_atom_count_out_of_range"})
                continue
            atoms = []
            row_errors = []
            for index in range(1, atom_count + 1):
                text = row.get(f"gold_atom_{index}", "").strip()
                label = row.get(f"gold_atom_{index}_nli", "").strip().lower()
                if not text:
                    row_errors.append(f"missing_atom_{index}")
                if label not in NLI_LABELS:
                    row_errors.append(f"invalid_atom_{index}_nli={label!r}")
                atoms.append({"atom_id": f"{ex_id}_a{index}", "text": text, "gold_nli": label})
            if not truthy(row.get("decomposition_complete", "")):
                row_errors.append("decomposition_not_marked_complete")
            if not truthy(row.get("faithful_to_claim", "")):
                row_errors.append("decomposition_not_marked_faithful")
            if row_errors:
                errors.append({"row": row_number, "example_id": ex_id, "error": ";".join(row_errors)})
                continue
            aggregated = aggregate_atom_labels([x["gold_nli"] for x in atoms])
            claim_gold = row.get("claim_gold_label", "").strip().lower()
            if aggregated != claim_gold:
                errors.append({
                    "row": row_number,
                    "example_id": ex_id,
                    "error": f"atom_aggregation={aggregated} differs from claim_gold={claim_gold}",
                })
                continue
            valid.append({
                "example_id": ex_id,
                "context_id": row.get("context_id", "").strip(),
                "domain": row.get("domain", "").strip(),
                "context": row.get("context", ""),
                "question": row.get("question", ""),
                "claim": row.get("claim", ""),
                "claim_gold_label": claim_gold,
                "annotator_id": row.get("annotator_id", "").strip(),
                "review_notes": row.get("review_notes", "").strip(),
                "atoms": atoms,
            })

    write_jsonl(args.output, valid)
    error_path = Path(args.errors) if args.errors else Path(args.output).with_suffix(".errors.json")
    error_path.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"n_valid": len(valid), "n_errors": len(errors), "errors_path": str(error_path)}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
