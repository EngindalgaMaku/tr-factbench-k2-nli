#!/usr/bin/env python3
"""
175_dev_pa_rule.py
==================
Independent check of the PA consensus-audit rule on DEV960 and DEV600 (no API calls).

PA was designed on the Gold-480 agreement errors: when K1 and K2 agree on partially_supported
or contradicted, the blind zero-shot Gemma-4-26B decision replaces the agreed label.
Here the frozen rule is applied to DEV:
  disagreements -> frozen V4 judge decision (scripts/173, DEV-V4-JUDGE-v1)
  agreements on partially_supported / contradicted -> archived Gemma-4-26B zero-shot prediction
  other agreements -> agreed label

Gemma predictions: tr-factbench results/llm_baselines/{dev_general,dev_stress}/gemma_4_26b_moe_free/zero_shot
(same model, system prompt sha d13df74e..., temperature 0 as on Gold). They were made on the
legacy (pre-review) DEV files with a different id scheme, so records are matched on
normalised claim + context text. Unmatched routed records keep the agreed label and are counted.

Output: reports/experiments/DEV-PA-RULE-v1/report.json and report.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from k2_nli.aggregation_ablation import aggregate_soft_prob  # noqa: E402

TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
OUT = ROOT / "reports" / "experiments" / "DEV-PA-RULE-v1"
ROUTE = {"partially_supported", "contradicted"}
SETS = {
    "dev960": ("K2-PIPE-PRED-DEV960-v1__mdeberta_base_2mil7", "predictions_DEV960-GEN.jsonl", "dev_general"),
    "dev600": ("K2-PIPE-PRED-DEV600-v1__mdeberta_base_2mil7", "predictions_DEV600-STR.jsonl", "dev_stress"),
}


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def mcnemar(a: list[bool], b: list[bool]) -> dict:
    x = sum(p and not q for p, q in zip(a, b))
    y = sum(q and not p for p, q in zip(a, b))
    return {"only_first": x, "only_second": y, "p_exact": round(float(binomtest(x, x + y, 0.5).pvalue), 4) if x + y else 1.0}


def analyse(split: str, k2_run: str, k1_file: str, llm_set: str) -> dict:
    k2 = read_jsonl(ROOT / "runs" / k2_run / "predictions.jsonl")
    k1 = {r["example_id"]: r for r in read_jsonl(TFB / "runs/ablations/H1_DROP10_S45_ABLATION_full" / k1_file)}
    judge = {r["example_id"]: r["judge_decision"] for r in read_jsonl(ROOT / "reports/experiments/DEV-V4-JUDGE-v1" / f"predictions_{split}.jsonl")}
    legacy = {r["example_id"]: r for r in read_jsonl(TFB / "data/evaluation/legacy_experiment_version" / f"{llm_set}.jsonl")}
    gemma = {}
    for r in read_jsonl(TFB / "results/llm_baselines" / llm_set / "gemma_4_26b_moe_free/zero_shot/predictions.jsonl"):
        src = legacy[r["example_id"]]
        gemma[(norm(src["claim"]), norm(src["context"])[:300])] = r["predicted_label"]

    rows, unmatched, routed = [], 0, 0
    for r in k2:
        g = r["gold_label"]
        p1 = k1[r["example_id"]]["predicted_label"]
        p2 = aggregate_soft_prob(r["atoms"]) if r.get("atoms") else None
        gm = gemma.get((norm(r["claim"]), norm(r["context"])[:300]))
        if p2 is None or p1 != p2:
            p0 = pa = judge[r["example_id"]]
        else:
            p0 = pa = p1
            if p1 in ROUTE:
                routed += 1
                if gm is None:
                    unmatched += 1
                else:
                    pa = gm
        rows.append({"gold": g, "k1": p1, "p0": p0, "pa": pa, "gemma": gm, "domain": r.get("domain"),
                     "agree_routed": p2 == p1 and p1 in ROUTE})
    n = len(rows)
    acc = lambda k: round(sum(x[k] == x["gold"] for x in rows) / n, 4)
    gm_rows = [x for x in rows if x["gemma"] is not None]
    rt = [x for x in rows if x["agree_routed"] and x["gemma"] is not None]
    res = {"n": n, "gemma_matched": len(gm_rows), "routed_agreements": routed, "routed_unmatched": unmatched,
           "acc": {"K1": acc("k1"), "P0": acc("p0"), "PA": acc("pa"),
                   "gemma_zero_shot_all": round(sum(x["gemma"] == x["gold"] for x in gm_rows) / len(gm_rows), 4)},
           "pa_on_routed": {"n": len(rt), "agreed_label_correct": sum(x["p0"] == x["gold"] for x in rt),
                            "gemma_correct": sum(x["pa"] == x["gold"] for x in rt),
                            "fixed": sum(x["p0"] != x["gold"] and x["pa"] == x["gold"] for x in rt),
                            "broken": sum(x["p0"] == x["gold"] and x["pa"] != x["gold"] for x in rt)},
           "PA_vs_P0": mcnemar([x["pa"] == x["gold"] for x in rows], [x["p0"] == x["gold"] for x in rows]),
           "by_domain": {}}
    n_dis = len(judge)
    res["llm_call_share"] = {"P0": round(n_dis / n, 4), "PA": round((n_dis + routed) / n, 4)}
    for d in sorted({x["domain"] for x in rows}):
        s = [x for x in rows if x["domain"] == d and x["agree_routed"] and x["gemma"] is not None]
        res["by_domain"][d] = {"routed": len(s), "fixed": sum(x["p0"] != x["gold"] and x["pa"] == x["gold"] for x in s),
                               "broken": sum(x["p0"] == x["gold"] and x["pa"] != x["gold"] for x in s)}
    return res


def main() -> None:
    rep = {s: analyse(s, *a) for s, a in SETS.items()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# PA rule on DEV (frozen rule, archived Gemma-4-26B zero-shot, no API calls)", ""]
    for s, r in rep.items():
        p = r["pa_on_routed"]
        lines += [f"## {s} (n={r['n']}, Gemma matched {r['gemma_matched']}, routed agreements {r['routed_agreements']}, unmatched {r['routed_unmatched']})",
                  f"- acc: {r['acc']}",
                  f"- routed: agreed label correct {p['agreed_label_correct']}/{p['n']}, Gemma correct {p['gemma_correct']}/{p['n']}, fixed {p['fixed']}, broken {p['broken']}",
                  f"- PA vs P0: {r['PA_vs_P0']}; LLM call share {r['llm_call_share']}",
                  f"- by domain (fixed/broken): " + "; ".join(f"{d} {v['fixed']}/{v['broken']} of {v['routed']}" for d, v in r["by_domain"].items()), ""]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
