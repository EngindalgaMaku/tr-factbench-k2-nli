#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from k2_nli.hybrid_arbitration import build_hybrid_arbitration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Component 3 Hybrid Arbitration experiment between K1, K2, and candidate LLM judges."
    )
    parser.add_argument("--config", required=True, help="Hybrid arbitration JSON config")
    parser.add_argument("--project-root", default=".", help="Repository root")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = build_hybrid_arbitration(
        Path(args.config), Path(args.project_root).resolve()
    )
    print(f"Hybrid arbitration report written to: {output_dir}")


if __name__ == "__main__":
    main()
