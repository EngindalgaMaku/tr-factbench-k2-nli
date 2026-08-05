#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from k2_nli.experiment_reporting import build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Git-friendly experiment report from one or more K2 run directories."
    )
    parser.add_argument("--config", required=True, help="Experiment JSON configuration file")
    parser.add_argument("--project-root", default=".", help="Repository root")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = build_report(Path(args.config), Path(args.project_root).resolve())
    print(f"Experiment report written to: {output_dir}")


if __name__ == "__main__":
    main()
