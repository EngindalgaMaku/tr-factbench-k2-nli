#!/usr/bin/env python3
"""
170_build_dev_disagreement_set.py
=================================
Development disagreement set for hybrid pipeline work (no API calls).

Gold-480 has already been used to develop the V4 judge prompt and the PA rule, so further
judge or routing changes must be developed on the development sets and only tested once
on Gold-480. This script builds that development material with the frozen components:

  1. K2 NLI on the frozen-atomizer outputs of DEV960 and DEV600
     (scripts/45_run_k2_from_gemma_atoms.py, mDeBERTa-v3 2mil7, same settings as Gold-480),
     unless the run already exists;
  2. soft-prob aggregation (k2_nli.aggregation_ablation.aggregate_soft_prob, as on Gold-480);
  3. join with the final K1 verifier (H1_DROP10_S45) predictions on the reviewed
     development files (tr-factbench runs/ablations/H1_DROP10_S45_ABLATION_full);
  4. write K1 != K2 cases in the arbitration_cases_123.jsonl format, plus the K1/K2
     agreement errors, and a summary report.

Inputs are only read. Outputs:
  data/processed/arbitration/dev_{split}_disagreement_cases.jsonl
  data/processed/arbitration/dev_{split}_agreement_errors.jsonl
  reports/experiments/DEV-DISAGREEMENT-SET-v1/summary.json and summary.md

Usage: python scripts/170_build_dev_disagreement_set.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # k2_nli/
sys.path.insert(0, str(ROOT / "src"))
from k2_nli.aggregation_ablation import aggregate_soft_prob  # noqa: E402

TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
SPLITS = {
    "dev960": {"atoms": "gemma_predicted_dev960", "k1": "predictions_DEV960-GEN.jsonl", "n": 960},
    "dev600": {"atoms": "gemma_predicted_dev600", "k1": "predictions_DEV600-STR.jsonl", "n": 600},
}
K1_DIR = TFB / "runs" / "ablations" / "H1_DROP10_S45_ABLATION_full"
ARB_DIR = ROOT / "data" / "processed" / "arbitration"
OUT = ROOT / "reports" / "experiments" / "DEV-DISAGREEMENT-SET-v1"
CONF_BINS = [(0.0, 0.8), (0.8, 0.9), (0.9, 0.99), (0.99, 1.01)]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def macro_f1(y: list[str], p: list[str]) -> float:
    f = []
    for lab in LABELS:
        tp = sum(a == lab and b == lab for a, b in zip(y, p))
        fp = sum(a != lab and b == lab for a, b in zip(y, p))
        fn = sum(a == lab and b != lab for a, b in zip(y, p))
        f.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return sum(f) / len(f)


def run_nli(split: str, cfg: dict) -> Path:
    run_id = f"K2-PIPE-PRED-{split.upper()}-v1__mdeberta_base_2mil7"
    run_dir = ROOT / "runs" / run_id
    if (run_dir / "predictions.jsonl").exists():
        print(f"[{split}] NLI run exists: {run_id}")
        return run_dir
    atoms_file = ROOT / "data" / "processed" / "atom_level" / cfg["atoms"] / "k2_input.jsonl"
    n = len(read_jsonl(atoms_file))
    if n != cfg["n"]:
        raise SystemExit(f"[{split}] atomization incomplete: {n}/{cfg['n']} records in {atoms_file}")
    print(f"[{split}] running NLI ({n} claims) -> {run_id}")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "45_run_k2_from_gemma_atoms.py"),
                    "--input", str(atoms_file), "--model", NLI_MODEL, "--run-id", run_id,
                    "--runs-dir", str(ROOT / "runs")], check=True, cwd=ROOT)
    return run_dir


def build(split: str, cfg: dict) -> dict:
    run_dir = run_nli(split, cfg)
    k2_rows = {r["example_id"]: r for r in read_jsonl(run_dir / "predictions.jsonl")}
    k1_rows = {r["example_id"]: r for r in read_jsonl(K1_DIR / cfg["k1"])}
    assert set(k1_rows) == set(k2_rows), f"{split}: id mismatch K1/K2"

    cases, agree_err, recs = [], [], []
    for eid, k2r in k2_rows.items():
        k1r = k1_rows[eid]
        gold = k2r["gold_label"]
        assert gold == k1r["gold_label"], f"{eid}: gold mismatch"
        atoms = k2r.get("atoms") or []
        k2_pred = aggregate_soft_prob(atoms) if atoms else None  # atomizer failure -> abstain
        k1_pred = k1r["predicted_label"]
        k1_conf = max(k1r["probabilities"].values())
        rec = {"id": eid, "domain": k2r.get("domain"), "gold": gold, "k1": k1_pred, "k2": k2_pred,
               "k1_conf": k1_conf, "n_atoms": len(atoms)}
        recs.append(rec)
        row = {"example_id": eid, "domain": k2r.get("domain"), "context": k2r["context"],
               "question": k2r.get("question", ""), "claim": k2r["claim"], "gold_label": gold,
               "k1_pred": k1_pred, "k1_correct": str(k1_pred == gold), "k1_confidence": round(k1_conf, 6),
               "k1_probabilities": k1r["probabilities"],
               "k2_pred": k2_pred, "k2_correct": str(k2_pred == gold),
               "k2_atoms": [{"atom": a["atom"], "label": a["pred_label"]} for a in atoms],
               "k2_atom_probs": [{"E": round(a["prob_entailment"], 6), "N": round(a["prob_neutral"], 6),
                                  "C": round(a["prob_contradiction"], 6)} for a in atoms]}
        if k2_pred is None or k1_pred != k2_pred:
            cases.append(row)
        elif k1_pred != gold:
            agree_err.append(row)

    ARB_DIR.mkdir(parents=True, exist_ok=True)
    for name, rows in [(f"dev_{split}_disagreement_cases.jsonl", cases), (f"dev_{split}_agreement_errors.jsonl", agree_err)]:
        (ARB_DIR / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    valid = [r for r in recs if r["k2"] is not None]
    y = [r["gold"] for r in recs]
    dis = [r for r in valid if r["k1"] != r["k2"]]
    agr = [r for r in valid if r["k1"] == r["k2"]]
    s = {
        "n": len(recs),
        "atomizer_failures": len(recs) - len(valid),
        "k1": {"acc": round(sum(r["k1"] == r["gold"] for r in recs) / len(recs), 4),
               "macro_f1": round(macro_f1(y, [r["k1"] for r in recs]), 4)},
        "k2": {"acc": round(sum(r["k2"] == r["gold"] for r in recs) / len(recs), 4),
               "macro_f1": round(macro_f1(y, [r["k2"] or "none" for r in recs]), 4)},
        "agreement": {"n": len(agr), "correct": sum(r["k1"] == r["gold"] for r in agr),
                      "errors": len(agr) - sum(r["k1"] == r["gold"] for r in agr),
                      "errors_by_shared_label": dict(Counter(r["k1"] for r in agr if r["k1"] != r["gold"]))},
        "disagreement": {"n": len(dis),
                         "k1_right": sum(r["k1"] == r["gold"] for r in dis),
                         "k2_right": sum(r["k2"] == r["gold"] for r in dis),
                         "both_wrong": sum(r["k1"] != r["gold"] and r["k2"] != r["gold"] for r in dis),
                         "by_domain": {}, "by_k1_confidence": {}, "pairs": {}},
        "oracle_acc": round(sum((r["k1"] == r["gold"]) or (r["k2"] == r["gold"]) for r in recs) / len(recs), 4),
    }
    by_dom = defaultdict(list)
    for r in dis:
        by_dom[r["domain"]].append(r)
    for d, rs in sorted(by_dom.items()):
        s["disagreement"]["by_domain"][d] = {"n": len(rs), "k1_right": sum(r["k1"] == r["gold"] for r in rs),
                                             "k2_right": sum(r["k2"] == r["gold"] for r in rs)}
    for lo, hi in CONF_BINS:
        rs = [r for r in dis if lo <= r["k1_conf"] < hi]
        s["disagreement"]["by_k1_confidence"][f"[{lo:.2f},{min(hi, 1.0):.2f})"] = {
            "n": len(rs), "k1_right": sum(r["k1"] == r["gold"] for r in rs),
            "k2_right": sum(r["k2"] == r["gold"] for r in rs)}
    s["disagreement"]["pairs"] = {f"{a} | {b}": n for (a, b), n in Counter((r["k1"], r["k2"]) for r in dis).most_common()}
    return s


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {split: build(split, cfg) for split, cfg in SPLITS.items()}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# DEV disagreement set (frozen K1, frozen atomizer + K2 soft-prob)", ""]
    for split, s in summary.items():
        d = s["disagreement"]
        lines += [f"## {split} (n={s['n']}, atomizer failures {s['atomizer_failures']})", "",
                  f"- K1 acc {s['k1']['acc']}, Macro-F1 {s['k1']['macro_f1']}; K2 acc {s['k2']['acc']}, Macro-F1 {s['k2']['macro_f1']}; oracle acc {s['oracle_acc']}",
                  f"- Agreement {s['agreement']['n']} (errors {s['agreement']['errors']}: {s['agreement']['errors_by_shared_label']})",
                  f"- Disagreement {d['n']}: K1 right {d['k1_right']}, K2 right {d['k2_right']}, both wrong {d['both_wrong']}",
                  "- By K1 confidence: " + "; ".join(f"{k} n={v['n']} K1 {v['k1_right']} K2 {v['k2_right']}" for k, v in d["by_k1_confidence"].items()),
                  "- By domain: " + "; ".join(f"{k} n={v['n']} K1 {v['k1_right']} K2 {v['k2_right']}" for k, v in d["by_domain"].items()),
                  ""]
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
