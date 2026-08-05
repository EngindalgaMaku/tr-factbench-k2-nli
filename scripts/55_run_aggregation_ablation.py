#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from k2_nli.aggregation_ablation import build_aggregation_ablation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reuse saved atom predictions to compare flat, contradiction-priority, "
            "and sentence-grouped claim aggregation."
        )
    )
    parser.add_argument("--config", required=True, help="Aggregation ablation JSON config")
    parser.add_argument("--project-root", default=".", help="Repository root")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = build_aggregation_ablation(
        Path(args.config), Path(args.project_root).resolve()
    )
    print(f"Aggregation ablation report written to: {output_dir}")


if __name__ == "__main__":
    main()
