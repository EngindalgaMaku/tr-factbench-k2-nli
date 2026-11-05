#!/usr/bin/env python3
"""
172_dev_component_diagnostics.py
================================
Frequency and cost of the component failure patterns noted in the Gold-480 case review
(vaka_inceleme/INCELEME_NOTLARI_VE_MIMARI_BULGULAR.md), measured on DEV960 and DEV600
(and on Gold-480 for reference). No API calls; inputs are only read.

Patterns (automatic proxies):
  P1 atomizer under-split : gold partially_supported but a single atom (K2 cannot output partial)
  P2 anaphoric atom       : an atom after the first starts with a reference word (bu, söz konusu, aynı, ...)
  P3 short atom           : an atom with <= 4 words (over-split proxy)
  P4 weak entailment      : an atom labelled entailment with P(E) < 0.65
  P5 sub-half entailment  : an atom labelled entailment with P(E) < 0.50 (argmax paradox)
  K1-S restrictive adverb : claim contains yalnız / yalnızca / sadece / ancak ... ile / only-type words;
                            K1's rate of predicting contradicted and its precision
For each pattern: number of claims, K2 accuracy with / without the pattern, and how many of
the K2 errors carry it. Also K2 error directions (gold -> predicted).

Output: reports/experiments/DEV-COMPONENT-DIAGNOSTICS-v1/report.json and report.md
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from k2_nli.aggregation_ablation import aggregate_soft_prob  # noqa: E402

TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
OUT = ROOT / "reports" / "experiments" / "DEV-COMPONENT-DIAGNOSTICS-v1"
SETS = {
    "dev960": (ROOT / "runs/K2-PIPE-PRED-DEV960-v1__mdeberta_base_2mil7/predictions.jsonl",
               TFB / "runs/ablations/H1_DROP10_S45_ABLATION_full/predictions_DEV960-GEN.jsonl", "example_id"),
    "dev600": (ROOT / "runs/K2-PIPE-PRED-DEV600-v1__mdeberta_base_2mil7/predictions.jsonl",
               TFB / "runs/ablations/H1_DROP10_S45_ABLATION_full/predictions_DEV600-STR.jsonl", "example_id"),
    "gold480": (ROOT / "runs/K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7/predictions.jsonl",
                TFB / "data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl", "release_example_id"),
}
ANAPHOR = re.compile(r"^\s*(bu|bunlar|bunun|bunu|buna|bundan|şu|o|söz konusu|aynı|ilgili|anılan|belirtilen|sözü edilen)\b", re.I)
RESTRICT = re.compile(r"\b(yalnız|yalnızca|sadece|salt|ancak)\b", re.I)


def tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def patterns(r: dict) -> set[str]:
    atoms = r.get("atoms") or []
    out = set()
    if r["gold_label"] == "partially_supported" and len(atoms) == 1:
        out.add("P1_undersplit_partial")
    if any(a.get("atom_index", k) > 0 and ANAPHOR.match(tr_lower(a["atom"])) for k, a in enumerate(atoms)):
        out.add("P2_anaphoric_atom")
    if any(len(a["atom"].split()) <= 4 for a in atoms):
        out.add("P3_short_atom")
    if any(a["pred_label"] == "entailment" and a["prob_entailment"] < 0.65 for a in atoms):
        out.add("P4_weak_entailment")
    if any(a["pred_label"] == "entailment" and a["prob_entailment"] < 0.50 for a in atoms):
        out.add("P5_subhalf_entailment")
    return out


def analyse(name: str, k2_path: Path, k1_path: Path, k1_id: str) -> dict:
    k2 = read_jsonl(k2_path)
    k1 = {r[k1_id]: r for r in read_jsonl(k1_path)}
    rows = []
    for r in k2:
        pred = aggregate_soft_prob(r["atoms"]) if r.get("atoms") else None
        rows.append({"gold": r["gold_label"], "k2": pred, "k1": k1[r["example_id"]]["predicted_label"],
                     "pats": patterns(r), "restrict": bool(RESTRICT.search(tr_lower(r["claim"]))),
                     "n_atoms": len(r.get("atoms") or [])})
    n = len(rows)
    k2_err = [x for x in rows if x["k2"] != x["gold"]]
    res = {"n": n, "k2_acc": round(1 - len(k2_err) / n, 4), "k2_errors": len(k2_err), "patterns": {}}
    for p in ["P1_undersplit_partial", "P2_anaphoric_atom", "P3_short_atom", "P4_weak_entailment", "P5_subhalf_entailment"]:
        w = [x for x in rows if p in x["pats"]]
        wo = [x for x in rows if p not in x["pats"]]
        acc = lambda s: round(sum(x["k2"] == x["gold"] for x in s) / len(s), 4) if s else None
        res["patterns"][p] = {"claims": len(w), "k2_acc_with": acc(w), "k2_acc_without": acc(wo),
                              "share_of_k2_errors": round(sum(p in x["pats"] for x in k2_err) / max(1, len(k2_err)), 4),
                              "k1_acc_with": round(sum(x["k1"] == x["gold"] for x in w) / len(w), 4) if w else None}
    rs = [x for x in rows if x["restrict"]]
    nr = [x for x in rows if not x["restrict"]]
    def k1c(s):
        pc = [x for x in s if x["k1"] == "contradicted"]
        return {"claims": len(s), "k1_pred_contradicted_rate": round(len(pc) / len(s), 4) if s else None,
                "k1_contradicted_precision": round(sum(x["gold"] == "contradicted" for x in pc) / len(pc), 4) if pc else None,
                "gold_contradicted_rate": round(sum(x["gold"] == "contradicted" for x in s) / len(s), 4) if s else None}
    res["K1_restrictive_adverb"] = {"with": k1c(rs), "without": k1c(nr)}
    res["k2_error_directions"] = {f"{g} -> {p}": c for (g, p), c in Counter((x["gold"], x["k2"]) for x in k2_err).most_common()}
    res["k2_acc_by_atoms"] = {}
    for k in sorted({x["n_atoms"] for x in rows}):
        s = [x for x in rows if x["n_atoms"] == k]
        res["k2_acc_by_atoms"][str(k)] = {"claims": len(s), "k2_acc": round(sum(x["k2"] == x["gold"] for x in s) / len(s), 4)}
    return res


def main() -> None:
    report = {name: analyse(name, *paths) for name, paths in SETS.items()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Component failure patterns on DEV (and Gold-480 for reference)", ""]
    pats = list(report["dev960"]["patterns"])
    lines += ["| Pattern | " + " | ".join(f"{s}: claims / K2 acc with / without / share of K2 errors" for s in report) + " |",
              "|---|" + "---|" * len(report)]
    for p in pats:
        cells = []
        for s in report:
            d = report[s]["patterns"][p]
            cells.append(f"{d['claims']} / {d['k2_acc_with']} / {d['k2_acc_without']} / {d['share_of_k2_errors']}")
        lines.append(f"| {p} | " + " | ".join(cells) + " |")
    lines += ["", "K1 restrictive adverb (with / without): " + "; ".join(
        f"{s}: pred-C rate {report[s]['K1_restrictive_adverb']['with']['k1_pred_contradicted_rate']} / {report[s]['K1_restrictive_adverb']['without']['k1_pred_contradicted_rate']}, "
        f"precision {report[s]['K1_restrictive_adverb']['with']['k1_contradicted_precision']} / {report[s]['K1_restrictive_adverb']['without']['k1_contradicted_precision']}, "
        f"n {report[s]['K1_restrictive_adverb']['with']['claims']}" for s in report), ""]
    for s in report:
        lines.append(f"{s} K2 error directions: " + ", ".join(f"{k} {v}" for k, v in list(report[s]["k2_error_directions"].items())[:6]))
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
