#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from k2_nli.run_utils import write_json
from k2_nli.validation import validate_claim_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir", default="data/reviewed/claim_level", help="Directory containing JSONL files"
    )
    parser.add_argument("--output", default="data/manifests/dataset_audit.json")
    args = parser.parse_args()

    paths = sorted(Path(args.data_dir).glob("*.jsonl"))
    if not paths:
        raise SystemExit(f"No JSONL files found in {args.data_dir}")
    reports = [validate_claim_dataset(path) for path in paths]
    output = {"datasets": reports, "total_errors": sum(x["n_errors"] for x in reports)}
    write_json(args.output, output)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if output["total_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
