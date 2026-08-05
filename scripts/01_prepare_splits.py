#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from k2_nli.io import read_jsonl, write_jsonl
from k2_nli.labels import claim_to_nli3
from k2_nli.run_utils import write_json
from k2_nli.splitting import split_general_by_context


def to_nli3(records: list[dict]) -> list[dict]:
    output = []
    for item in records:
        nli_label = claim_to_nli3(str(item["gold_label"]))
        if nli_label is None:
            continue
        output.append({
            **item,
            "premise": item["context"],
            "hypothesis": item["claim"],
            "nli_label": nli_label,
        })
    return output


def summarize(records: list[dict]) -> dict:
    return {
        "n_examples": len(records),
        "n_contexts": len({x["context_id"] for x in records}),
        "labels": dict(Counter(x["gold_label"] for x in records)),
        "domains": dict(Counter(x["domain"] for x in records)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--general", default="data/reviewed/claim_level/dev_general.jsonl")
    parser.add_argument("--stress", default="data/reviewed/claim_level/dev_stress.jsonl")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    general = read_jsonl(args.general)
    stress = read_jsonl(args.stress)
    splits = split_general_by_context(general, seed=args.seed)

    report = {"seed": args.seed, "splits": {}}
    for split_name, records in splits.items():
        full_path = output_dir / f"general_{split_name}_claim4.jsonl"
        nli_path = output_dir / f"general_{split_name}_nli3.jsonl"
        write_jsonl(full_path, records)
        nli_records = to_nli3(records)
        write_jsonl(nli_path, nli_records)
        report["splits"][split_name] = {
            "claim4": summarize(records),
            "nli3": summarize(nli_records),
            "claim4_path": str(full_path),
            "nli3_path": str(nli_path),
        }

    stress_records = [{**item, "k2_split": "stress_eval"} for item in stress]
    write_jsonl(output_dir / "stress_eval_claim4.jsonl", stress_records)
    stress_nli3 = to_nli3(stress_records)
    write_jsonl(output_dir / "stress_eval_nli3.jsonl", stress_nli3)
    report["stress_eval"] = {
        "claim4": summarize(stress_records),
        "nli3": summarize(stress_nli3),
    }
    write_json(output_dir / "split_manifest.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
