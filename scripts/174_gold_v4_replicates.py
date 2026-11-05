#!/usr/bin/env python3
"""
174_gold_v4_replicates.py
=========================
Run-to-run noise of the frozen V4 judge: two fresh replicates on the 123 Gold-480
disagreements (same prompt, parser, model and settings as scripts/75; calls via scripts/173).

Compared with the archived V4 run (K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1): accuracy per
replicate, decisions that change between runs, and the implied hybrid P0 accuracy on Gold-480
(357 agreements, 337 correct, are fixed). Gives the noise floor for prompt comparisons
(V4 110 vs V4.1 108 vs V5 91).

Usage: python scripts/174_gold_v4_replicates.py [--report-only]
Output: reports/experiments/GOLD-V4-REPLICATES-v1/
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "experiments" / "GOLD-V4-REPLICATES-v1"
CASES = ROOT / "data/processed/arbitration/arbitration_cases_123.jsonl"
ORIG = ROOT / "reports/experiments/K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1/arbitration_predictions_123.jsonl"
AGREE_CORRECT, N_GOLD = 337, 480
REPS = ["rep1", "rep2"]

_spec = importlib.util.spec_from_file_location("s173", ROOT / "scripts" / "173_dev_v4_judge.py")
s173 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s173)
v4 = s173.v4
read_jsonl = s173.read_jsonl


def run() -> None:
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent / "tr-factbench-v0.1.0-preview" / ".env")
    key = os.environ["OPENROUTER_API_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    cases = read_jsonl(CASES)
    for rep in REPS:
        f = OUT / f"predictions_{rep}.jsonl"
        done = {r["example_id"] for r in read_jsonl(f)}
        for i, c in enumerate(cases, 1):
            if c["example_id"] in done:
                continue
            resp = s173.call(v4.build_predicate_prompt(c), key)
            raw = resp["choices"][0].get("message", {}).get("content", "").strip()
            p = v4.parse_judge_output(raw)
            usage = resp.get("usage", {})
            rec = {"example_id": c["example_id"], "gold_label": c["gold_label"], "judge_decision": p["final_decision"],
                   "judge_correct": p["final_decision"] == c["gold_label"],
                   "parse_note": p["reasoning"] if p["reasoning"] in ("Parse failure.", "JSON parse fallback used.") else "",
                   "finish_reason": resp["choices"][0].get("finish_reason"), "provider": resp.get("provider"),
                   "cost": usage.get("cost"), "raw_output": raw}
            with open(f, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[{rep} {i:03d}/123] {rec['judge_decision']:<19} {'OK' if rec['judge_correct'] else 'WRONG'} {rec['provider']}", flush=True)
            time.sleep(0.3)


def report() -> None:
    runs = {"original": {r["example_id"]: r["judge_decision"] for r in read_jsonl(ORIG)}}
    meta = {}
    for rep in REPS:
        rows = read_jsonl(OUT / f"predictions_{rep}.jsonl")
        if len(rows) == 123:
            runs[rep] = {r["example_id"]: r["judge_decision"] for r in rows}
            meta[rep] = {"cost_usd": round(sum(r["cost"] or 0 for r in rows), 4),
                         "providers": dict(Counter(r["provider"] for r in rows)),
                         "finish_length": sum(r["finish_reason"] == "length" for r in rows),
                         "parse_notes": dict(Counter(r["parse_note"] for r in rows if r["parse_note"]))}
    gold = {r["example_id"]: r["gold_label"] for r in read_jsonl(CASES)}
    ids = sorted(gold)
    res = {"per_run": {}, "pairwise_changed": {}, "meta": meta}
    for name, d in runs.items():
        c = sum(d[i] == gold[i] for i in ids)
        res["per_run"][name] = {"judge_correct": c, "judge_acc": round(c / 123, 4),
                                "p0_correct": AGREE_CORRECT + c, "p0_acc": round((AGREE_CORRECT + c) / N_GOLD, 4)}
    names = list(runs)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            x, y = names[a], names[b]
            ch = [i for i in ids if runs[x][i] != runs[y][i]]
            res["pairwise_changed"][f"{x} vs {y}"] = {"changed": len(ch),
                                                    "changed_correctness": sum((runs[x][i] == gold[i]) != (runs[y][i] == gold[i]) for i in ch)}
    unstable = [i for i in ids if len({runs[n][i] for n in runs}) > 1]
    res["unstable_cases"] = len(unstable)
    res["majority_vote"] = None
    if len(runs) == 3:
        mv = {i: Counter(runs[n][i] for n in runs).most_common(1)[0][0] for i in ids}
        res["majority_vote"] = sum(mv[i] == gold[i] for i in ids)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-only", action="store_true")
    if not ap.parse_args().report_only:
        run()
    report()
