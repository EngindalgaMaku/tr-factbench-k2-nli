#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/processed/general_model_selection_nli3.jsonl")
    parser.add_argument("--models", default="configs/models.json")
    parser.add_argument("--suite-id", default="K2-10-selection-v1")
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", default=None)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    config = json.loads(Path(args.models).read_text(encoding="utf-8"))
    models = config.get("models", [])
    if not models:
        raise SystemExit("No models found in registry")

    for model in models:
        run_id = f"{args.suite_id}__{model['short_name']}"
        run_path = Path(args.runs_dir) / run_id
        if args.resume and (run_path / "metrics.json").exists():
            print(f"SKIP {run_id}: completed")
            continue
        command = [
            sys.executable,
            "scripts/10_run_zero_shot.py",
            "--data", args.data,
            "--model", model["model_id"],
            "--run-id", run_id,
            "--runs-dir", args.runs_dir,
            "--batch-size", str(args.batch_size),
            "--max-length", str(args.max_length),
        ]
        if args.device:
            command.extend(["--device", args.device])
        print("RUN", " ".join(command))
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
