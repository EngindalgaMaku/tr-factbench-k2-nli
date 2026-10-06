#!/usr/bin/env python3
"""
85_reproduce_k2_gold.py
Proves that the AP6 run uses the frozen K2 pipeline:
  (1) NLI + soft-prob aggregation: re-runs the official runner
      (scripts/45_run_k2_from_gemma_atoms.py) on the frozen Gold-480 atoms into a
      scratch runs dir and compares atom labels and soft-prob claim labels with the
      frozen K2-PIPE-PRED-GOLD480-v1 / K2-AGG-ABLATION-GOLD480-v1 artifacts;
  (2) atomizer: re-atomizes a fixed sample of Gold-480 claims with the frozen
      Gemma-4 QLoRA adapter (same settings as generate_gold480_gemma_atoms.py)
      and reports exact-match of the atom lists.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "atomizer" / "v2"))

from k2_nli.aggregation_ablation import aggregate_soft_prob  # noqa: E402

GOLD_ATOMS = ROOT / "data" / "processed" / "atom_level" / "gemma_predicted_gold480" / "k2_input.jsonl"
FROZEN_RUN = ROOT / "runs" / "K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7"
FROZEN_SOFT = (ROOT / "reports" / "experiments" / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
               / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")
SCRATCH = ROOT / "scratch" / "repro_runs"
RUN_ID = "REPRO-K2-NLI-GOLD480"
ATOMIZER_SAMPLE = 24


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def group_atoms(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["example_id"], []).append(r)
    return out


def main() -> None:
    # (1) NLI + aggregation
    run_dir = SCRATCH / RUN_ID
    if not run_dir.exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "45_run_k2_from_gemma_atoms.py"),
                        "--input", str(GOLD_ATOMS), "--model", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
                        "--run-id", RUN_ID, "--runs-dir", str(SCRATCH)], check=True, cwd=ROOT)
    new_atoms = read_jsonl(run_dir / "atom_predictions.jsonl")
    old_atoms = read_jsonl(FROZEN_RUN / "atom_predictions.jsonl")
    old_by_id = {a["atom_id"]: a for a in old_atoms}
    same_label = sum(old_by_id[a["atom_id"]]["pred_label"] == a["pred_label"] for a in new_atoms)
    max_prob_diff = max(abs(old_by_id[a["atom_id"]]["prob_entailment"] - a["prob_entailment"]) for a in new_atoms)
    new_soft = {eid: aggregate_soft_prob(atoms) for eid, atoms in group_atoms(new_atoms).items()}
    frozen_soft = {(r.get("release_example_id") or r["example_id"]): r["pred_label"] for r in read_jsonl(FROZEN_SOFT)}
    soft_same = sum(new_soft.get(eid) == lab for eid, lab in frozen_soft.items())
    print(f"[NLI] atoms {len(new_atoms)} vs frozen {len(old_atoms)}; identical atom labels {same_label}/{len(new_atoms)}; "
          f"max |dP(entail)| = {max_prob_diff:.2e}")
    print(f"[AGG] soft-prob claim labels identical {soft_same}/{len(frozen_soft)}")

    # (2) atomizer determinism on a fixed sample (every 20th Gold claim)
    from atomizer_runtime import LocalAtomizer
    gold_inputs = read_jsonl(GOLD_ATOMS)
    sample = gold_inputs[::20][:ATOMIZER_SAMPLE]
    atomizer = LocalAtomizer(adapter_path=str(ROOT.parent / "atomizer" / "v2" / "outputs" / "google_gemma_4_e2b_it_final_adapter"),
                             base_model="google/gemma-4-E2B-it", max_new_tokens=180)
    exact = 0
    mismatches = []
    for rec in sample:
        atoms = atomizer.predict(rec["claim"]).atoms or []
        if atoms == rec["pred_atoms"]:
            exact += 1
        else:
            mismatches.append({"example_id": rec["example_id"], "frozen": rec["pred_atoms"], "rerun": atoms})
    print(f"[ATOMIZER] exact atom-list match {exact}/{len(sample)}")
    (SCRATCH / "atomizer_repro_mismatches.json").write_text(json.dumps(mismatches, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
