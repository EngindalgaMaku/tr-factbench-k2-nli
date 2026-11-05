#!/usr/bin/env python3
"""
173_dev_v4_judge.py
===================
Frozen V4 judge on the DEV960 and DEV600 disagreement sets (scripts/170).

Purpose: the V4 prompt was developed on the 123 Gold-480 disagreements (57 -> 110 correct),
so its Gold accuracy may be optimistic. This run measures the same frozen judge on
disagreements it has never seen, from the same distribution.

Frozen settings: prompt and parser are imported unchanged from
scripts/75_run_predicate_aware_debiased_arbitration.py (V4); model
meta-llama/llama-3.3-70b-instruct, temperature 0, top_p 1, max_tokens 400, via OpenRouter.
Differences from the Gold run: TLS verification is on; the serving provider and usage are recorded.

Caveats: K1 was selected on DEV, so K1 is right more often on DEV disagreements than on Gold;
DEV labels are single-annotator provisional labels.

Usage:
  python scripts/173_dev_v4_judge.py --limit 3     # pilot
  python scripts/173_dev_v4_judge.py               # full run (resumes)
  python scripts/173_dev_v4_judge.py --report-only
Output: reports/experiments/DEV-V4-JUDGE-v1/
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
from collections import Counter
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # verify TLS against the Windows certificate store (no verify=False)

import requests  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
ARB = ROOT / "data" / "processed" / "arbitration"
OUT = ROOT / "reports" / "experiments" / "DEV-V4-JUDGE-v1"
GOLD_V4 = ROOT / "reports/experiments/K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1/arbitration_predictions_123.jsonl"
SPLITS = ["dev960", "dev600"]

_spec = importlib.util.spec_from_file_location("v4", ROOT / "scripts" / "75_run_predicate_aware_debiased_arbitration.py")
v4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v4)


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def call(prompt: str, key: str, retries: int = 6) -> dict:
    payload = {"model": v4.MODEL_ID, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.0, "top_p": 1.0, "max_tokens": 400, "stream": False}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
               "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
               "X-OpenRouter-Title": "TR-FactBench DEV V4 judge"}
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(v4.ENDPOINT, headers=headers, json=payload, timeout=120)
            if r.status_code == 200 and r.json().get("choices"):
                return r.json()
            print(f"  retry {attempt}: HTTP {r.status_code} {r.text[:150]}")
        except requests.exceptions.RequestException as e:
            print(f"  retry {attempt}: {e}")
        time.sleep(2 ** attempt)
    raise RuntimeError("max retries exceeded")


def stratum(c: dict) -> str:
    if c["k1_pred"] == c["gold_label"]:
        return "k1_right"
    if c["k2_pred"] == c["gold_label"]:
        return "k2_right"
    return "both_wrong"


def run(limit: int | None) -> None:
    for env in (ROOT.parent / "tr-factbench-v0.1.0-preview" / ".env", ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            load_dotenv(env)
            break
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not found")
    OUT.mkdir(parents=True, exist_ok=True)
    done_calls = 0
    for split in SPLITS:
        cases = read_jsonl(ARB / f"dev_{split}_disagreement_cases.jsonl")
        pred_file = OUT / f"predictions_{split}.jsonl"
        done = {r["example_id"] for r in read_jsonl(pred_file)}
        for i, c in enumerate(cases, 1):
            if c["example_id"] in done:
                continue
            if limit is not None and done_calls >= limit:
                return
            if c["k2_pred"] is None:  # atomizer failure: research pipeline would also route; K2 label shown as unknown
                c = {**c, "k2_pred": "unverifiable"}
            resp = call(v4.build_predicate_prompt(c), key)
            raw = resp["choices"][0].get("message", {}).get("content", "").strip()
            parsed = v4.parse_judge_output(raw)
            usage = resp.get("usage", {})
            rec = {"example_id": c["example_id"], "split": split, "domain": c.get("domain"),
                   "gold_label": c["gold_label"], "k1_pred": c["k1_pred"], "k2_pred": c["k2_pred"],
                   "k1_confidence": c.get("k1_confidence"), "stratum": stratum(c),
                   "judge_decision": parsed["final_decision"], "judge_correct": parsed["final_decision"] == c["gold_label"],
                   "favored_model": parsed["favored_model"], "parse_note": parsed["reasoning"] if parsed["reasoning"] in ("Parse failure.", "JSON parse fallback used.") else "",
                   "finish_reason": resp["choices"][0].get("finish_reason"), "provider": resp.get("provider"),
                   "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                   "cost": usage.get("cost"), "raw_output": raw}
            with open(pred_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            done_calls += 1
            print(f"[{split} {i:03d}/{len(cases)}] {rec['stratum']:<10} gold {rec['gold_label']:<19} judge {rec['judge_decision']:<19} "
                  f"{'OK' if rec['judge_correct'] else 'WRONG'}  {rec['provider']}  ${rec['cost']}")
            time.sleep(0.3)


def mcnemar(a: list[bool], b: list[bool]) -> dict:
    x = sum(p and not q for p, q in zip(a, b))
    y = sum(q and not p for p, q in zip(a, b))
    return {"only_first": x, "only_second": y, "p_exact": round(float(binomtest(x, x + y, 0.5).pvalue), 4) if x + y else 1.0}


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    jc = [r["judge_correct"] for r in rows]
    k1c = [r["k1_pred"] == r["gold_label"] for r in rows]
    k2c = [r["k2_pred"] == r["gold_label"] for r in rows]
    s = {"n": n, "judge_correct": sum(jc), "judge_acc": round(sum(jc) / n, 4),
         "k1_correct": sum(k1c), "k2_correct": sum(k2c),
         "oracle": sum(a or b for a, b in zip(k1c, k2c)),
         "judge_vs_k1": mcnemar(jc, k1c), "by_stratum": {}}
    for st in ("k1_right", "k2_right", "both_wrong"):
        sub = [r for r in rows if r["stratum"] == st]
        s["by_stratum"][st] = {"n": len(sub), "judge_correct": sum(r["judge_correct"] for r in sub),
                               "acc": round(sum(r["judge_correct"] for r in sub) / len(sub), 4) if sub else None}
    return s


def report() -> None:
    res = {}
    allrows = []
    for split in SPLITS:
        rows = read_jsonl(OUT / f"predictions_{split}.jsonl")
        if not rows:
            continue
        allrows += rows
        res[split] = summarise(rows)
        agree_err = len(read_jsonl(ARB / f"dev_{split}_agreement_errors.jsonl"))
        n_total = {"dev960": 960, "dev600": 600}[split]
        if len(rows) == len(read_jsonl(ARB / f"dev_{split}_disagreement_cases.jsonl")):
            # hybrid P0 accuracy: agreements (correct unless agreement error) + judge on disagreements
            agree_ok = n_total - len(rows) - agree_err
            res[split]["p0_acc"] = round((agree_ok + res[split]["judge_correct"]) / n_total, 4)
            res[split]["k1_acc_all"] = round((agree_ok + res[split]["k1_correct"]) / n_total, 4)
    gold = read_jsonl(GOLD_V4)
    for r in gold:
        r["stratum"] = stratum(r)
        r["judge_correct"] = r["judge_decision"] == r["gold_label"]
    res["gold480_reference"] = summarise(gold)
    if allrows:
        res["dev_union"] = summarise(allrows)
        res["dev_usage"] = {"calls": len(allrows), "cost_usd": round(sum(r["cost"] or 0 for r in allrows), 4),
                            "providers": dict(Counter(r["provider"] for r in allrows)),
                            "finish_length": sum(r["finish_reason"] == "length" for r in allrows),
                            "parse_notes": dict(Counter(r["parse_note"] for r in allrows if r["parse_note"]))}
    (OUT / "report.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Frozen V4 judge on DEV disagreements", "",
             "| Set | n | judge correct | judge acc | K1 right | K2 right | oracle | judge on K1-right / K2-right / both-wrong |",
             "|---|---:|---:|---:|---:|---:|---:|---|"]
    for k, s in res.items():
        if k == "dev_usage":
            continue
        b = s["by_stratum"]
        lines.append(f"| {k} | {s['n']} | {s['judge_correct']} | {s['judge_acc']} | {s['k1_correct']} | {s['k2_correct']} | {s['oracle']} | "
                     + " / ".join(f"{b[x]['judge_correct']}/{b[x]['n']}" for x in ("k1_right", "k2_right", "both_wrong")) + " |")
    for k in SPLITS:
        if k in res and "p0_acc" in res[k]:
            lines.append(f"\n{k}: P0 acc {res[k]['p0_acc']} vs K1 acc {res[k]['k1_acc_all']}; judge vs K1 on disagreements {res[k]['judge_vs_k1']}")
    if "dev_usage" in res:
        lines.append(f"\nUsage: {res['dev_usage']}")
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    if not a.report_only:
        run(a.limit)
    report()
