#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from k2_nli.gemma_reporting import build_gemma_pipeline_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build tables, SVG figures, and a Markdown report for a Gemma-predicted atom K2 run."
    )
    parser.add_argument("--config", required=True, help="Experiment JSON configuration file")
    parser.add_argument("--project-root", default=".", help="Repository root")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = build_gemma_pipeline_report(
        Path(args.config).resolve(), Path(args.project_root).resolve()
    )
    print(f"Gemma pipeline report written to: {output_dir}")


if __name__ == "__main__":
    main()
