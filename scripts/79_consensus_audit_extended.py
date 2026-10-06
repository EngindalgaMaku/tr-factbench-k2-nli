#!/usr/bin/env python3
"""
79_consensus_audit_extended.py
Extended cost-benefit analysis of auditing K1==K2 (consensus) decisions on Gold-480
(zero API cost: reuses existing blind-judge predictions for all 480 examples).

For every blind judge variant available in K3-HYBRID-ARBITRATION-GOLD480-v1 and every
routing policy, reports: extra judge calls, fixed / broken consensus decisions, net
change, net per extra call, accuracy, and a paired bootstrap 95% CI for the net change.
Also reports the same per domain (finance / legal / medical).

Disagreements are always resolved by the V4 judge (as in the base hybrid).
DESIGN ANALYSIS on Gold-480 — policies were not fixed in advance of seeing these data.

Output: reports/K3_CONSENSUS_AUDIT_EXTENDED.md, reports/K3_CONSENSUS_AUDIT_EXTENDED.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = ROOT.parent / "tr-factbench-v0.1.0-preview" / "data" / "evaluation" / "gold_v1.0"
EXP = ROOT / "reports" / "experiments"
PS_C = ("partially_supported", "contradicted")
N_BOOT = 5000


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def domain_of(example_id: str) -> str:
    n = int(example_id.rsplit("_", 1)[-1])
    return "finance" if n <= 160 else ("legal" if n <= 320 else "medical")


def main() -> None:
    gold = {r["release_example_id"]: r["gold_label"] for r in read_jsonl(GOLD_DIR / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")}
    k1 = {r["release_example_id"]: r["predicted_label"] for r in read_jsonl(GOLD_DIR / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")}
    k2 = {(r.get("release_example_id") or r["example_id"]): r["pred_label"] for r in read_jsonl(
        EXP / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts" / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")}
    v4 = {r["example_id"]: r["judge_decision"] for r in read_jsonl(
        EXP / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")}
    judges = {}
    for p in sorted((EXP / "K3-HYBRID-ARBITRATION-GOLD480-v1" / "artifacts").glob("hybrid_predictions__*.jsonl")):
        name = p.stem.replace("hybrid_predictions__", "")
        judges[name] = {r["example_id"]: r["judge_pred"] for r in read_jsonl(p)}

    ids = sorted(gold)
    base = {i: (k1[i] if k1[i] == k2[i] else v4[i]) for i in ids}
    consensus = [i for i in ids if k1[i] == k2[i]]
    n_dis = len(ids) - len(consensus)
    policies = {
        "all_consensus": lambda i: True,
        "PA_label_PS_or_C": lambda i: k1[i] in PS_C,
        "PB_medical_and_PS_or_C": lambda i: domain_of(i) == "medical" and k1[i] in PS_C,
        "medical_only": lambda i: domain_of(i) == "medical",
    }
    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, len(ids), size=(N_BOOT, len(ids)))
    results = []
    for jname, judge in judges.items():
        for pname, route in policies.items():
            routed = {i for i in consensus if route(i)}
            # per-example delta: +1 fixed, -1 broken, 0 otherwise
            delta = np.array([(1 if judge[i] == gold[i] and base[i] != gold[i] else -1 if judge[i] != gold[i] and base[i] == gold[i] else 0)
                              if i in routed else 0 for i in ids])
            boots = delta[boot_idx].sum(axis=1)
            lo, hi = np.percentile(boots, [2.5, 97.5])
            row = {"judge": jname, "policy": pname, "extra_calls": len(routed),
                   "total_call_rate": round((n_dis + len(routed)) / len(ids), 4),
                   "fixed": int((delta == 1).sum()), "broken": int((delta == -1).sum()), "net": int(delta.sum()),
                   "net_ci95": [int(lo), int(hi)], "net_per_call": round(delta.sum() / len(routed), 4) if routed else None,
                   "accuracy": round((sum(base[i] == gold[i] for i in ids) + delta.sum()) / len(ids), 4),
                   "by_domain": {}}
            for d in ("finance", "legal", "medical"):
                dmask = np.array([domain_of(i) == d for i in ids])
                row["by_domain"][d] = {"fixed": int(((delta == 1) & dmask).sum()), "broken": int(((delta == -1) & dmask).sum())}
            results.append(row)

    base_acc = sum(base[i] == gold[i] for i in ids) / len(ids)
    (ROOT / "reports" / "K3_CONSENSUS_AUDIT_EXTENDED.json").write_text(
        json.dumps({"base_accuracy": base_acc, "n_consensus": len(consensus), "n_disagreement": n_dis, "results": results},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Uzlaşma denetimi: genişletilmiş fayda–maliyet analizi (Gold-480, tasarım analizi)", "",
             f"Temel hibrit (uyuşmazlıkta V4 hakemi): doğruluk {base_acc:.4f}; uzlaşma {len(consensus)}, uyuşmazlık {n_dis}.",
             "Uzlaşma denetiminde kör hakemlerin (K1/K2 çıktısını görmeyen) mevcut Gold-480 tahminleri kullanıldı; API maliyeti yok.",
             "Net değişim için %95 güven aralığı: örnek düzeyinde eşleştirilmiş bootstrap (5000 tekrar).", "",
             "| Hakem | Kural | Ek çağrı | Toplam çağrı oranı | Düzelen | Bozulan | Net [%95 GA] | Çağrı başına net | Doğruluk |",
             "|---|---|---:|---:|---:|---:|---|---:|---:|"]
    for r in results:
        lines.append(f"| {r['judge']} | {r['policy']} | {r['extra_calls']} | {r['total_call_rate']:.1%} | {r['fixed']} | {r['broken']} | "
                     f"{r['net']:+d} [{r['net_ci95'][0]:+d}, {r['net_ci95'][1]:+d}] | {r['net_per_call'] if r['net_per_call'] is not None else '-'} | {r['accuracy']:.4f} |")
    lines += ["", "## Alan kırılımı (düzelen / bozulan)", "", "| Hakem | Kural | Finans | Hukuk | Tıp |", "|---|---|---|---|---|"]
    for r in results:
        bd = r["by_domain"]
        lines.append(f"| {r['judge']} | {r['policy']} | {bd['finance']['fixed']}/{bd['finance']['broken']} | "
                     f"{bd['legal']['fixed']}/{bd['legal']['broken']} | {bd['medical']['fixed']}/{bd['medical']['broken']} |")
    lines.append("")
    (ROOT / "reports" / "K3_CONSENSUS_AUDIT_EXTENDED.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
