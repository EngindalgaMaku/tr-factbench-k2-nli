#!/usr/bin/env python3
"""
93_gold480_domain_ci.py  (2026-11-10, jüri ön incelemesi sonrası; KARAR_KAYDI #78)
Gold-480 alan bazında Macro-F1 için %95 güven aralıkları (Şekil 4.5 / Bölüm 4.6.1; sonradan eklenen betimsel analiz).

Girdiler ve sistem tanımları scripts/92_gold480_results_bundle.py ile birebir aynıdır (aynı dosyalar, aynı kurallar).
Yöntem: her alan içinde bağlam grubu düzeyinde bootstrap (alan başına 40 grup), 10.000 tekrar, seed 42,
yüzdelik aralık. Macro-F1 dört sınıf üzerinden, sıfır bölmede 0 (sklearn zero_division=0 ile aynı).
Çıktı: reports/GOLD480_DOMAIN_CI.{md,json}
"""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
GOLD_DIR = TFB / "data" / "evaluation" / "gold_v1.0"
EXP = ROOT / "reports" / "experiments"
LLM = TFB / "results" / "llm_baselines" / "gold_v1.0"
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
ROUTE = {"partially_supported", "contradicted"}
N_BOOT = 10_000


def read_jsonl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

def eid(r):
    return r.get("release_example_id") or r["example_id"]

def domain_of(i):
    n = int(i.rsplit("_", 1)[-1]); return "finance" if n <= 160 else ("legal" if n <= 320 else "medical")

def mf1(y, p):
    s = 0.0
    for l in LABELS:
        tp = sum(a == l and b == l for a, b in zip(y, p)); fp = sum(a != l and b == l for a, b in zip(y, p))
        fn = sum(a == l and b != l for a, b in zip(y, p))
        s += 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
    return s / len(LABELS)


def main():
    gold_rows = read_jsonl(GOLD_DIR / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")
    ids = [eid(r) for r in gold_rows]; gold = {eid(r): r["gold_label"] for r in gold_rows}
    group = {eid(r): r["context"] for r in gold_rows}
    k1 = {eid(r): r["predicted_label"] for r in read_jsonl(GOLD_DIR / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")}
    agg = EXP / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
    k2 = {eid(r): r["pred_label"] for r in read_jsonl(agg / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")}
    v4 = {r["example_id"]: r["judge_decision"] for r in read_jsonl(EXP / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")}
    llm = lambda m, mode: {eid(r): r["predicted_label"] for r in read_jsonl(LLM / m / mode / "predictions.jsonl")}
    gz = llm("google_gemma-4-26b-a4b-it", "zero_shot"); g8 = llm("openai_gpt-4.1-mini", "few_shot_8")
    p0v4 = {i: k1[i] if k1[i] == k2[i] else v4[i] for i in ids}
    systems = {
        "K1": k1, "K2 (olasılık ortalaması)": k2,
        "Hibrit, kör Gemma hakemi": {i: k1[i] if k1[i] == k2[i] else gz[i] for i in ids},
        "Hibrit, V4 hakemi": p0v4,
        "PB": {i: gz[i] if (k1[i] == k2[i] and k1[i] in ROUTE and domain_of(i) == "medical") else p0v4[i] for i in ids},
        "Gemma-4-26B (sıfır örnekli)": gz, "GPT-4.1-mini (8 örnekli)": g8,
    }
    out = {"method": f"within-domain context-group bootstrap, {N_BOOT}, seed 42, percentile 95%", "domains": {}}
    lines = ["# Gold-480 alan bazında Macro-F1 ve %95 GA (betik 93)", "", out["method"], "",
             "| Sistem | Finans | Hukuk | Sağlık |", "|---|---|---|---|"]
    rows = {s: [] for s in systems}
    for d in ("finance", "legal", "medical"):
        dids = [i for i in ids if domain_of(i) == d]
        groups = sorted({group[i] for i in dids}); mem = {g: [i for i in dids if group[i] == g] for g in groups}
        rng = random.Random(42)
        boots = [[i for g in (rng.choice(groups) for _ in groups) for i in mem[g]] for _ in range(N_BOOT)]
        out["domains"][d] = {"n": len(dids), "groups": len(groups), "systems": {}}
        for s, pred in systems.items():
            f = mf1([gold[i] for i in dids], [pred[i] for i in dids])
            bs = sorted(mf1([gold[i] for i in b], [pred[i] for i in b]) for b in boots)
            lo, hi = bs[int(0.025 * N_BOOT)], bs[int(0.975 * N_BOOT) - 1]
            out["domains"][d]["systems"][s] = {"macro_f1": round(f, 4), "ci95": [round(lo, 4), round(hi, 4)]}
            rows[s].append(f"{f:.3f} [{lo:.3f}; {hi:.3f}]")
    for s, r in rows.items():
        lines.append(f"| {s} | " + " | ".join(r) + " |")
    (ROOT / "reports" / "GOLD480_DOMAIN_CI.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports" / "GOLD480_DOMAIN_CI.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
