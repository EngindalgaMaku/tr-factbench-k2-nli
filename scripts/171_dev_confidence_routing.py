#!/usr/bin/env python3
"""
171_dev_confidence_routing.py
=============================
Confidence-based routing for K1 != K2 disagreements, selected on DEV only (no API calls).

Pre-declared protocol (written before looking at any result):
  Rule family L(tau): on a disagreement, take K2's label if K1's top softmax probability
  is below tau, otherwise K1's label (no judge).
  tau is chosen on the union of the DEV960 and DEV600 disagreement sets (scripts/170) by
  accuracy on those disagreements; ties go to the smaller tau. tau = 0 means "always K1",
  tau > 1 means "always K2".
  Gold-480 is then evaluated once with the selected tau:
    (1) K1 alone, (2) L(tau*), (3) frozen hybrid P0 (V4 judge on every disagreement),
    (4) P0 + tau*: disagreements with K1 confidence < tau* take K2 directly, the rest go to
        the V4 judge (the archived V4 decisions are reused; no new calls).
  Exact McNemar tests compare (2) and (4) with (3) on the 480 claims.

Inputs are only read. Output: reports/experiments/DEV-CONF-ROUTING-v1/report.json and report.md
"""
from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
ARB = ROOT / "data" / "processed" / "arbitration"
OUT = ROOT / "reports" / "experiments" / "DEV-CONF-ROUTING-v1"
GRID = [0.0, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 0.999, 1.01]


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def route(case: dict, tau: float) -> str:
    return case["k2_pred"] if case["k1_conf"] < tau else case["k1_pred"]


def mcnemar(a: list[bool], b: list[bool]) -> dict:
    only_a = sum(x and not y for x, y in zip(a, b))
    only_b = sum(y and not x for x, y in zip(a, b))
    n = only_a + only_b
    p = binomtest(only_a, n, 0.5).pvalue if n else 1.0
    return {"only_first_correct": only_a, "only_second_correct": only_b, "p_exact": round(float(p), 4)}


def main() -> None:
    dev = {}
    for split in ("dev960", "dev600"):
        rows = read_jsonl(ARB / f"dev_{split}_disagreement_cases.jsonl")
        dev[split] = [{"k1_pred": r["k1_pred"], "k2_pred": r["k2_pred"], "gold": r["gold_label"],
                       "k1_conf": r["k1_confidence"]} for r in rows]
    union = dev["dev960"] + dev["dev600"]

    search = []
    for tau in GRID:
        row = {"tau": tau}
        for name, cases in [("union", union), ("dev960", dev["dev960"]), ("dev600", dev["dev600"])]:
            row[name] = sum(route(c, tau) == c["gold"] for c in cases)
        search.append(row)
    best = max(search, key=lambda r: (r["union"], -r["tau"]))
    tau = best["tau"]

    # Gold-480, evaluated once with the selected tau
    k1 = {r["release_example_id"]: r for r in read_jsonl(TFB / "data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl")}
    arb = {r["example_id"]: r for r in read_jsonl(ARB / "arbitration_cases_123.jsonl")}
    v4 = {r["example_id"]: r for r in read_jsonl(ROOT / "reports/experiments/K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1/arbitration_predictions_123.jsonl")}
    ids = sorted(k1)
    gold = {i: k1[i]["gold_label"] for i in ids}
    conf = {i: max(k1[i]["probabilities"].values()) for i in ids}
    systems = {"K1": {}, "L_tau": {}, "P0": {}, "P0_tau": {}}
    calls = {"P0": 0, "P0_tau": 0}
    for i in ids:
        p1 = k1[i]["predicted_label"]
        systems["K1"][i] = p1
        if i not in arb:  # agreement: K1 == K2
            for s in ("L_tau", "P0", "P0_tau"):
                systems[s][i] = p1
            continue
        p2 = arb[i]["k2_pred"]
        systems["L_tau"][i] = p2 if conf[i] < tau else p1
        systems["P0"][i] = v4[i]["judge_decision"]
        calls["P0"] += 1
        if conf[i] < tau:
            systems["P0_tau"][i] = p2
        else:
            systems["P0_tau"][i] = v4[i]["judge_decision"]
            calls["P0_tau"] += 1
    correct = {s: [systems[s][i] == gold[i] for i in ids] for s in systems}
    gold_res = {s: {"correct": sum(c), "acc": round(sum(c) / len(ids), 4)} for s, c in correct.items()}
    gold_res["P0"]["judge_calls"] = calls["P0"]
    gold_res["P0_tau"]["judge_calls"] = calls["P0_tau"]
    tests = {"L_tau_vs_K1": mcnemar(correct["L_tau"], correct["K1"]),
             "L_tau_vs_P0": mcnemar(correct["L_tau"], correct["P0"]),
             "P0_tau_vs_P0": mcnemar(correct["P0_tau"], correct["P0"])}
    n_low = sum(1 for i in arb if conf[i] < tau)

    report = {"protocol": "tau selected on DEV960+DEV600 disagreements by accuracy (ties -> smaller tau); Gold-480 evaluated once",
              "dev_sizes": {k: len(v) for k, v in dev.items()}, "grid_search": search, "selected_tau": tau,
              "gold480": gold_res, "gold480_tests": tests, "gold_disagreements_below_tau": n_low}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Confidence routing selected on DEV (no API calls)", "",
             f"DEV disagreements: DEV960 {len(dev['dev960'])}, DEV600 {len(dev['dev600'])}.", "",
             "| tau | union | DEV960 | DEV600 |", "|---:|---:|---:|---:|"]
    lines += [f"| {r['tau']} | {r['union']} | {r['dev960']} | {r['dev600']} |" for r in search]
    lines += ["", f"Selected tau = {tau} (Gold disagreements below tau: {n_low}/123)", "",
              "| Gold-480 system | correct | acc | judge calls |", "|---|---:|---:|---:|"]
    lines += [f"| {s} | {r['correct']} | {r['acc']} | {r.get('judge_calls', 0)} |" for s, r in gold_res.items()]
    lines += ["", f"McNemar L_tau vs K1: {tests['L_tau_vs_K1']}", f"McNemar L_tau vs P0: {tests['L_tau_vs_P0']}", f"McNemar P0_tau vs P0: {tests['P0_tau_vs_P0']}"]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
