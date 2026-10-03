#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_gold480_gemma_atoms.py
Runs the fine-tuned Gemma-4 QLoRA atomizer on the official 480 held-out gold test set
(TR-FactBench_controlled480_GOLD_v1.0.jsonl).
Produces K2 input format with atomic decomposition, exactly matching K1's test evaluation set.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add atomizer/v2 to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "atomizer" / "v2"))

from atomizer_runtime import LocalAtomizer, AtomizerOutput


def get_domain(release_example_id: str) -> str:
    try:
        num = int(release_example_id.rsplit("_", 1)[-1])
        if num <= 160:
            return "finance"
        elif num <= 320:
            return "legal"
        else:
            return "medical"
    except Exception:
        return "general"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decompose 480 held-out gold test claims into atomic propositions using Gemma-4 QLoRA."
    )
    parser.add_argument(
        "--gold-input",
        default=str(
            REPO_ROOT
            / "tr-factbench-v0.1.0-preview"
            / "data"
            / "evaluation"
            / "gold_v1.0"
            / "gold"
            / "TR-FactBench_controlled480_GOLD_v1.0.jsonl"
        ),
        help="Path to the official 480 gold test JSONL",
    )
    parser.add_argument(
        "--adapter-path",
        default=str(REPO_ROOT / "atomizer" / "v2" / "outputs" / "google_gemma_4_e2b_it_final_adapter"),
        help="Path to Gemma-4 QLoRA adapter",
    )
    parser.add_argument(
        "--base-model",
        default="google/gemma-4-E2B-it",
        help="Base model name or path in HuggingFace cache",
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "k2_nli" / "data" / "processed" / "atom_level" / "gemma_predicted_gold480"),
        help="Output directory for K2-ready dataset",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=180,
        help="Max generation tokens for atomizer",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gold_path = Path(args.gold_input)
    if not gold_path.exists():
        raise FileNotFoundError(f"Gold input not found: {gold_path}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "k2_input.jsonl"
    stats_file = out_dir / "atomization_summary.json"

    print("=" * 70)
    print("K2 PIPELINE: GEMMA-4 QLoRA ATOMIZATION ON 480 GOLD TEST EXAMPLES")
    print("=" * 70)
    print(f"Input Gold Set : {gold_path}")
    print(f"Adapter Path   : {args.adapter_path}")
    print(f"Output File    : {out_file}")

    # Read gold records
    gold_records = []
    with open(gold_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                gold_records.append(json.loads(line))
    total_records = len(gold_records)
    print(f"Loaded {total_records} gold test claims.")

    # Check for existing completed records to support resume
    completed_ids = set()
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        obj = json.loads(line)
                        completed_ids.add(obj["example_id"])
                    except Exception:
                        pass
        print(f"Resuming: {len(completed_ids)} records already processed.")

    # Initialize LocalAtomizer
    print("\nLoading Gemma-4 QLoRA Atomizer onto GPU...")
    start_init = time.time()
    atomizer = LocalAtomizer(
        adapter_path=args.adapter_path,
        base_model=args.base_model,
        max_new_tokens=args.max_new_tokens,
    )
    print(f"Atomizer loaded in {time.time() - start_init:.2f} seconds.")

    # Process claims
    print("\nStarting inference across 480 claims...")
    start_infer = time.time()
    n_success = 0
    n_fail = 0
    n_atoms_total = 0

    mode = "a" if completed_ids else "w"
    with open(out_file, mode, encoding="utf-8") as out_f:
        for idx, item in enumerate(gold_records, 1):
            ex_id = item.get("release_example_id") or item.get("example_id") or f"ex_{idx:04d}"
            if ex_id in completed_ids:
                continue

            claim = item["claim"].strip()
            context = item["context"].strip()
            gold_label = item["gold_label"].strip()
            question = item.get("question", "")
            domain = item.get("domain") or get_domain(ex_id)

            t0 = time.time()
            try:
                result: AtomizerOutput = atomizer.predict(claim)
                atoms = result.atoms or []
                is_valid = bool(result.json_valid and atoms)
            except Exception as e:
                atoms = []
                is_valid = False

            if is_valid:
                n_success += 1
                n_atoms_total += len(atoms)
            else:
                n_fail += 1

            k2_record = {
                "example_id": ex_id,
                "source_example_id": ex_id,
                "domain": domain,
                "gold_label": gold_label,
                "context": context,
                "question": question,
                "claim": claim,
                "pred_atoms": atoms,
                "json_valid": is_valid,
                "atom_count_correct": is_valid and (len(atoms) >= 1),
            }

            out_f.write(json.dumps(k2_record, ensure_ascii=False) + "\n")
            out_f.flush()

            if idx % 25 == 0 or idx == total_records:
                elapsed = time.time() - start_infer
                speed = idx / elapsed if elapsed > 0 else 0
                print(
                    f"[{idx:03d}/{total_records}] Elapsed: {elapsed:.1f}s | "
                    f"Speed: {speed:.2f} claims/s | Valid: {n_success} | Failures: {n_fail} | "
                    f"Avg atoms: {(n_atoms_total / max(1, n_success)):.2f}"
                )

    total_time = time.time() - start_infer
    summary = {
        "dataset": "TR-FactBench_controlled480_GOLD_v1.0",
        "total_claims": total_records,
        "successfully_atomized": n_success,
        "failed_atomization": n_fail,
        "coverage": n_success / total_records if total_records else 0,
        "total_atoms_produced": n_atoms_total,
        "mean_atoms_per_valid_claim": n_atoms_total / max(1, n_success),
        "total_inference_time_sec": total_time,
        "claims_per_second": total_records / total_time if total_time > 0 else 0,
    }

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("ATOMIZATION COMPLETED SUCCESSFULLY!")
    print(f"Output File: {out_file}")
    print(f"Summary    : {json.dumps(summary, indent=2)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
