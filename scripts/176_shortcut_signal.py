#!/usr/bin/env python3
"""
176_shortcut_signal.py
======================
Does a "K1 shortcut" flag predict K1 errors on K1 != K2 disagreements? (vaka_inceleme Bulgu #3; no API calls)

Pre-declared definition (written before looking at results):
  S = K1's no-context prediction equals its full-input prediction, the full-input prediction is NOT
      'unverifiable' (without context 'unverifiable' is the expected answer, not a shortcut), and the
      no-context confidence is >= 0.65 (threshold from Bulgu #3).
Questions, on the disagreement sets:
  (1) K1 error rate with S vs without S (among disagreements where K1 does not say 'unverifiable');
  (2) frozen V4 judge accuracy with S vs without S, and how often the judge followed a wrong K1 when S held.
DEV960 + DEV600 are analysed first; Gold-480 is evaluated once with the same definition.
Inputs: K1 no-context predictions from the same checkpoint as the full-input predictions
  (tr-factbench runs/ablations/H1_DROP10_S45_ABLATION_claim_only = context empty, question + claim kept;
   GOLD480_CONTEXT_ABLATION_v1/predictions_claim_only.jsonl), DEV disagreement sets (scripts/170),
  DEV V4 judge outputs (scripts/173), Gold V4 judge outputs (scripts/75).
Output: reports/experiments/SHORTCUT-SIGNAL-v1/report.json and report.md
"""
from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
ABL = TFB / "runs/ablations"
OUT = ROOT / "reports/experiments/SHORTCUT-SIGNAL-v1"
TAU = 0.65


def rj(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def load(split: str):
    if split == "gold480":
        noctx = {r["example_id"]: r for r in rj(ABL / "GOLD480_CONTEXT_ABLATION_v1/predictions_claim_only.jsonl")}
        cases = rj(ROOT / "data/processed/arbitration/arbitration_cases_123.jsonl")
        full = {r["example_id"]: r for r in rj(ABL / "GOLD480_CONTEXT_ABLATION_v1/predictions_full.jsonl")}
        judge = {r["example_id"]: r["judge_decision"] for r in rj(ROOT / "reports/experiments/K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1/arbitration_predictions_123.jsonl")}
    else:
        f = {"dev960": "DEV960-GEN", "dev600": "DEV600-STR"}[split]
        noctx = {r["example_id"]: r for r in rj(ABL / f"H1_DROP10_S45_ABLATION_claim_only/predictions_{f}.jsonl")}
        full = {r["example_id"]: r for r in rj(ABL / f"H1_DROP10_S45_ABLATION_full/predictions_{f}.jsonl")}
        cases = rj(ROOT / f"data/processed/arbitration/dev_{split}_disagreement_cases.jsonl")
        judge = {r["example_id"]: r["judge_decision"] for r in rj(ROOT / f"reports/experiments/DEV-V4-JUDGE-v1/predictions_{split}.jsonl")}
    rows = []
    for c in cases:
        eid = c["example_id"]
        k1 = full[eid]["predicted_label"]
        assert k1 == c["k1_pred"], (split, eid)
        nc = noctx[eid]
        s = nc["predicted_label"] == k1 and k1 != "unverifiable" and max(nc["probabilities"].values()) >= TAU
        rows.append({"gold": c["gold_label"], "k1": k1, "k2": c["k2_pred"], "judge": judge[eid], "S": s})
    return rows


def summarise(rows):
    elig = [r for r in rows if r["k1"] != "unverifiable"]
    def block(sub):
        n = len(sub)
        k1_wrong = sum(r["k1"] != r["gold"] for r in sub)
        j_ok = sum(r["judge"] == r["gold"] for r in sub)
        followed_wrong_k1 = sum(r["judge"] == r["k1"] and r["k1"] != r["gold"] for r in sub)
        return {"n": n, "k1_wrong": k1_wrong, "k1_error_rate": round(k1_wrong / n, 3) if n else None,
                "judge_correct": j_ok, "judge_acc": round(j_ok / n, 3) if n else None,
                "judge_followed_wrong_k1": followed_wrong_k1}
    a, b = [r for r in elig if r["S"]], [r for r in elig if not r["S"]]
    out = {"disagreements": len(rows), "eligible_k1_not_unverifiable": len(elig), "with_S": block(a), "without_S": block(b)}
    if a and b:
        table = [[out["with_S"]["k1_wrong"], len(a) - out["with_S"]["k1_wrong"]], [out["without_S"]["k1_wrong"], len(b) - out["without_S"]["k1_wrong"]]]
        out["fisher_k1_error_S_vs_notS"] = {"odds_ratio": round(float(fisher_exact(table)[0]), 3), "p": round(float(fisher_exact(table)[1]), 4)}
    return out


def main():
    rep = {}
    dev = load("dev960") + load("dev600")
    rep["dev_union"] = summarise(dev)
    rep["dev960"] = summarise(load("dev960"))
    rep["dev600"] = summarise(load("dev600"))
    rep["gold480_once"] = summarise(load("gold480"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# K1 shortcut flag on disagreements (no API)", "", f"S: no-context prediction = full prediction, full != unverifiable, no-context confidence >= {TAU}", "",
             "| Set | eligible | S: n / K1 error rate / judge acc / judge followed wrong K1 | not S: n / K1 error rate / judge acc / followed wrong K1 | Fisher OR, p |", "|---|---:|---|---|---|"]
    for k, s in rep.items():
        a, b = s["with_S"], s["without_S"]
        f = s.get("fisher_k1_error_S_vs_notS", {})
        lines.append(f"| {k} | {s['eligible_k1_not_unverifiable']} | {a['n']} / {a['k1_error_rate']} / {a['judge_acc']} / {a['judge_followed_wrong_k1']} | {b['n']} / {b['k1_error_rate']} / {b['judge_acc']} / {b['judge_followed_wrong_k1']} | {f.get('odds_ratio')}, {f.get('p')} |")
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
