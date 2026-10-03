#!/usr/bin/env python3
"""
59_audit_k2_k3.py
Independent integrity audit of K2 / K3 results.
Every number is recomputed from raw prediction files, joined strictly by example_id.
No hardcoded metric values. Run from the k2_nli/ directory.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef

LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
TFB = Path("../tr-factbench-v0.1.0-preview")
GOLD = TFB / "data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl"
K1 = TFB / "data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl"
LLM = TFB / "results/llm_baselines/gold_v1.0"
AGG = Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts")
K2_SOFT = AGG / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl"
K2_FLAT = AGG / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__flat.jsonl"
CASES = Path("data/processed/arbitration/arbitration_cases_120.jsonl")
LIVE_GEMMA = Path("reports/experiments/K3-LIVE-GEMMA-ARBITRATION-v1/arbitration_predictions_120.jsonl")
LIVE_LLAMA = Path("reports/experiments/K3-LIVE-LLAMA70B-ARBITRATION-v1/arbitration_predictions_120.jsonl")


def rj(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def m(y, p) -> dict:
    return {
        "n": len(y),
        "correct": int(sum(a == b for a, b in zip(y, p))),
        "acc": round(accuracy_score(y, p), 4),
        "macro_f1": round(f1_score(y, p, labels=LABELS, average="macro", zero_division=0), 4),
        "mcc": round(matthews_corrcoef(y, p), 4),
    }


def mcnemar(y, a, b) -> dict:
    ao = sum(x == g and z != g for g, x, z in zip(y, a, b))
    bo = sum(x != g and z == g for g, x, z in zip(y, a, b))
    n = ao + bo
    p = 1.0 if n == 0 else float(binomtest(min(ao, bo), n, 0.5).pvalue)
    return {"a_only": ao, "b_only": bo, "p_exact": round(p, 5)}


def llm_map(model_dir: str, mode: str) -> dict[str, str] | None:
    path = LLM / model_dir / mode / "predictions.jsonl"
    if not path.exists():
        return None
    out = {}
    for r in rj(path):
        lab = r.get("predicted_label") or r.get("label")
        out[r["example_id"]] = lab
    return out


def main() -> None:
    report: dict = {"issues": []}
    issue = report["issues"].append

    gold = {r["release_example_id"]: r for r in rj(GOLD)}
    k1 = {r["release_example_id"]: r for r in rj(K1)}
    k2s = {r["example_id"]: r for r in rj(K2_SOFT)}
    k2f = {r["example_id"]: r for r in rj(K2_FLAT)} if K2_FLAT.exists() else {}
    report["sizes"] = {"gold": len(gold), "k1": len(k1), "k2_soft": len(k2s), "k2_flat": len(k2f)}

    gold_label_field = next(k for k in ("gold_label", "label", "final_label") if k in next(iter(gold.values())))
    # 1. Gold-label consistency between K1 file and official gold file
    mism = [e for e in k1 if e in gold and k1[e]["gold_label"] != gold[e][gold_label_field]]
    report["k1_vs_gold_label_mismatch"] = len(mism)
    if mism:
        issue(f"K1 file gold_label differs from official gold for {len(mism)} examples")
    k2_gold_mism = [e for e in k2s if e in gold and k2s[e].get("gold_label") not in (None, gold[e][gold_label_field])]
    report["k2_vs_gold_label_mismatch"] = len(k2_gold_mism)

    ids = sorted(e for e in gold if e in k1 and e in k2s)
    missing = sorted(set(gold) - set(ids))
    report["common_ids"] = len(ids)
    report["excluded_ids"] = missing
    y = [gold[e][gold_label_field] for e in ids]
    p1 = [k1[e]["predicted_label"] for e in ids]
    p2 = [k2s[e]["pred_label"] for e in ids]
    report["K1_478"] = m(y, p1)
    report["K2_soft_478"] = m(y, p2)
    if k2f:
        pf = [k2f[e]["pred_label"] for e in ids]
        report["K2_flat_478"] = m(y, pf)
        report["K2_soft_vs_flat_mcnemar"] = mcnemar(y, p2, pf)
        report["soft_vs_flat_changed_preds"] = sum(a != b for a, b in zip(p2, pf))
    # K1 on all 480 (fair: K1 does not need atomizer)
    all_ids = sorted(e for e in gold if e in k1)
    report["K1_480"] = m([gold[e][gold_label_field] for e in all_ids], [k1[e]["predicted_label"] for e in all_ids])

    # 2. Consensus / disagreement
    cons = [i for i, e in enumerate(ids) if p1[i] == p2[i]]
    dis = [i for i, e in enumerate(ids) if p1[i] != p2[i]]
    dis_ids = [ids[i] for i in dis]
    report["consensus"] = {"n": len(cons), "correct": sum(p1[i] == y[i] for i in cons)}
    report["disagreement"] = {
        "n": len(dis),
        "k1_correct": sum(p1[i] == y[i] for i in dis),
        "k2_correct": sum(p2[i] == y[i] for i in dis),
        "both_wrong": sum(p1[i] != y[i] and p2[i] != y[i] for i in dis),
    }
    report["oracle"] = report["consensus"]["correct"] + report["disagreement"]["k1_correct"] + report["disagreement"]["k2_correct"]

    # 3. Arbitration case file integrity
    cases = {c["example_id"]: c for c in rj(CASES)}
    report["cases_file"] = {"n": len(cases), "same_ids_as_disagreement": set(cases) == set(dis_ids)}
    if set(cases) != set(dis_ids):
        issue("arbitration_cases_120 IDs differ from recomputed disagreement set")
    bad = [e for e, c in cases.items() if c["gold_label"] != gold[e][gold_label_field]
           or c["k1_pred"] != k1[e]["predicted_label"] or c["k2_pred"] != k2s[e]["pred_label"]]
    report["cases_field_mismatch"] = len(bad)
    leak_keys = [k for k in next(iter(cases.values())) if k not in ("example_id", "context", "claim", "k1_pred", "k2_pred", "k2_atoms")]
    report["cases_extra_fields_(not_in_prompt)"] = leak_keys

    # 4. Judges on the 120 disagreement cases + end-to-end
    judges: dict[str, dict[str, str]] = {}
    FEWSHOT_LLAMA = Path("reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1/arbitration_predictions_120.jsonl")
    for name, path in (
        ("live_meta_gemma4_e2b", LIVE_GEMMA),
        ("live_meta_llama70b", LIVE_LLAMA),
        ("live_fewshot_meta_llama70b", FEWSHOT_LLAMA),
    ):
        if path.exists():
            rows = rj(path)
            ids_rows = [r["example_id"] for r in rows]
            if len(ids_rows) != len(set(ids_rows)):
                issue(f"{name}: duplicate example_ids ({len(ids_rows)} rows, {len(set(ids_rows))} unique)")
            judges[name] = {r["example_id"]: r["judge_decision"] for r in rows}
            report[f"{name}_json_valid"] = sum(bool(r.get("json_valid")) for r in rows)
            report[f"{name}_favored"] = dict(Counter(r.get("favored_model") for r in rows))
    for d in ("meta-llama_llama-3.3-70b-instruct", "google_gemma-4-26b-a4b-it", "openai_gpt-4.1-mini", "qwen_qwen-2.5-72b-instruct"):
        for mode in ("zero_shot", "few_shot_8"):
            mp = llm_map(d, mode)
            if mp and all(e in mp for e in ids):
                judges[f"blind_{d}__{mode}"] = mp

    yd = [y[i] for i in dis]
    p1d = [p1[i] for i in dis]
    p2d = [p2[i] for i in dis]
    jr = {}
    hybrids = {}
    for name, mp in judges.items():
        if not all(e in mp for e in dis_ids):
            issue(f"{name}: missing some disagreement ids")
            continue
        jd = [mp[e] for e in dis_ids]
        hyb = [p1[i] if p1[i] == p2[i] else mp[ids[i]] for i in range(len(ids))]
        hybrids[name] = hyb
        third = sum(j not in (a, b) for j, a, b in zip(jd, p1d, p2d))
        third_ok = sum(j not in (a, b) and j == g for j, a, b, g in zip(jd, p1d, p2d, yd))
        entry = {
            "disagreement": m(yd, jd),
            "picked_k1": sum(j == a for j, a in zip(jd, p1d)),
            "picked_k2": sum(j == b for j, b in zip(jd, p2d)),
            "picked_third_label": third,
            "third_label_correct": third_ok,
            "pred_distribution": dict(Counter(jd)),
            "end_to_end_478": m(y, hyb),
            "mcnemar_vs_K1": mcnemar(y, hyb, p1),
            "mcnemar_vs_K2": mcnemar(y, hyb, p2),
        }
        if not name.startswith("live_"):
            entry["standalone_478"] = m(y, [mp[e] for e in ids])
            entry["hybrid_vs_standalone_mcnemar"] = mcnemar(y, hyb, [mp[e] for e in ids])
        jr[name] = entry
    report["judges"] = jr
    report["gold_distribution_in_disagreement"] = dict(Counter(yd))

    # 5. Paired: blind vs informed (same model, same 120)
    a, b = "blind_meta-llama_llama-3.3-70b-instruct__zero_shot", "live_meta_llama70b"
    if a in judges and b in judges:
        report["llama_blind_zs_vs_informed_on_120"] = mcnemar(yd, [judges[a][e] for e in dis_ids], [judges[b][e] for e in dis_ids])
    # Persuasion check: when live llama favoured a model, was that model right?
    if LIVE_LLAMA.exists():
        rows = {r["example_id"]: r for r in rj(LIVE_LLAMA)}
        fav = Counter()
        for e in dis_ids:
            r = rows[e]
            f = r.get("favored_model")
            key = f"{f}|k1_ok={r['k1_correct']}|k2_ok={r['k2_correct']}|judge_ok={r['judge_correct']}"
            fav[key] += 1
        report["live_llama_favored_breakdown"] = dict(sorted(fav.items()))
        # Does the favoured_model label agree with the decision actually chosen?
        incons = sum(1 for e in dis_ids if (rows[e]["favored_model"] == "Model A" and rows[e]["judge_decision"] != rows[e]["k1_pred"])
                     or (rows[e]["favored_model"] == "Model B" and rows[e]["judge_decision"] != rows[e]["k2_pred"]))
        report["live_llama_favored_vs_decision_inconsistent"] = incons

    # 6. Robustness: (a) K2 flat instead of soft, (b) full 480 with K1 fallback for atomizer failures,
    #    (c) mean over all blind judges (avoids picking the best judge on the test set)
    rob = {}
    blind = {k: v for k, v in judges.items() if k.startswith("blind_")}
    if k2f:
        pf = [k2f[e]["pred_label"] for e in ids]
        for name, mp in blind.items():
            hyb = [p1[i] if p1[i] == pf[i] else mp[ids[i]] for i in range(len(ids))]
            rob.setdefault("k2_flat_hybrid", {})[name] = {**m(y, hyb), "llm_calls": sum(p1[i] != pf[i] for i in range(len(ids)))}
    y480 = [gold[e][gold_label_field] for e in all_ids]
    for name, mp in judges.items():
        if not all(e in mp for e in dis_ids):
            continue
        hyb480 = []
        for e in all_ids:
            a = k1[e]["predicted_label"]
            if e not in k2s:
                hyb480.append(a)  # atomizer failure -> fall back to K1 (no LLM call)
            else:
                b = k2s[e]["pred_label"]
                hyb480.append(a if a == b else mp[e])
        rob.setdefault("full_480_k1_fallback", {})[name] = m(y480, hyb480)
    accs = [jr[k]["end_to_end_478"]["acc"] for k in jr if k.startswith("blind_")]
    f1s = [jr[k]["end_to_end_478"]["macro_f1"] for k in jr if k.startswith("blind_")]
    if accs:
        rob["blind_judges_mean_478"] = {"n_configs": len(accs), "mean_acc": round(sum(accs) / len(accs), 4),
                                        "min_acc": min(accs), "max_acc": max(accs),
                                        "mean_macro_f1": round(sum(f1s) / len(f1s), 4)}
    report["robustness"] = rob
    if LIVE_LLAMA.exists():
        report["live_llama_actual_cost_usd_from_openrouter_usage"] = round(sum(
            (r["response"].get("usage") or {}).get("cost", 0) or 0
            for r in rj(LIVE_LLAMA.parent / "raw_responses_120.jsonl")), 6)

    out = Path("reports/experiments/AUDIT-K2-K3-v1")
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
