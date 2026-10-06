#!/usr/bin/env python3
"""
78_simulate_consensus_routing.py
Offline (zero-API) simulation of selective consensus routing on Gold-480.

The base hybrid sends only K1 != K2 cases to the judge (V4). This script asks:
if some K1 == K2 (consensus) cases were ALSO sent to a judge, how many errors
would be fixed vs. broken per extra API call? Existing judge predictions are reused:
  - blind Gemma-4-26B zero-shot (sees no K1/K2 output) for all 480 examples,
  - informed Llama-3.3-70B consensus run (sees that both models agreed; V1-era prompt).

Also measures whether K1 confidence separates consensus errors (AUROC).

DESIGN ANALYSIS ONLY: rules were chosen after inspecting Gold-480 errors.
Frozen policies for the held-out test: configs/frozen/K3_ROUTING_POLICIES_v1.json

Output: reports/K3_CONSENSUS_ROUTING_SIMULATION.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = ROOT.parent / "tr-factbench-v0.1.0-preview" / "data" / "evaluation" / "gold_v1.0"
EXP = ROOT / "reports" / "experiments"
PS_C = ("partially_supported", "contradicted")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def domain_of(example_id: str) -> str:
    # Gold-480 is ordered in domain blocks (see generate_gold480_gemma_atoms.get_domain).
    n = int(example_id.rsplit("_", 1)[-1])
    return "finance" if n <= 160 else ("legal" if n <= 320 else "medical")


def main() -> None:
    gold = {r["release_example_id"]: r["gold_label"] for r in read_jsonl(GOLD_DIR / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")}
    k1_rows = read_jsonl(GOLD_DIR / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")
    k1 = {r["release_example_id"]: r["predicted_label"] for r in k1_rows}
    conf = {r["release_example_id"]: max(r["probabilities"].values()) for r in k1_rows}
    k2 = {(r.get("release_example_id") or r["example_id"]): r["pred_label"] for r in read_jsonl(
        EXP / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
        / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")}
    v4 = {r["example_id"]: r["judge_decision"] for r in read_jsonl(
        EXP / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")}
    judges = {
        "blind Gemma-4-26B zero-shot": {r["example_id"]: r["judge_pred"] for r in read_jsonl(
            EXP / "K3-HYBRID-ARBITRATION-GOLD480-v1" / "artifacts"
            / "hybrid_predictions__google_gemma-4-26b-a4b-it__zero_shot.jsonl")},
        "informed Llama-3.3-70B (V1-era prompt)": {r["example_id"]: r["judge_decision"] for r in read_jsonl(
            EXP / "K3-CONSENSUS-LLAMA70B-EVAL-358" / "consensus_judge_predictions_358.jsonl")},
    }

    ids = list(gold)
    consensus = [i for i in ids if k1[i] == k2[i]]
    disagreement = [i for i in ids if k1[i] != k2[i]]
    base_correct = sum((k1[i] if i in consensus else v4[i]) == gold[i] for i in ids)
    n = len(ids)

    errors = [k1[i] != gold[i] for i in consensus]
    auroc = roc_auc_score(errors, [-conf[i] for i in consensus])
    err_conf = sorted(conf[i] for i in consensus if k1[i] != gold[i])
    high_conf_errors = sum(c >= 0.96 for c in err_conf)

    policies = [
        ("All consensus cases", lambda i: True),
        ("PA: agreed label PS or C", lambda i: k1[i] in PS_C),
        ("Agreed label PS", lambda i: k1[i] == "partially_supported"),
        ("Agreed label C", lambda i: k1[i] == "contradicted"),
        ("Medical only", lambda i: domain_of(i) == "medical"),
        ("PB: medical and agreed label PS or C", lambda i: domain_of(i) == "medical" and k1[i] in PS_C),
        ("K1 confidence < 0.99", lambda i: conf[i] < 0.99),
        ("K1 confidence < 0.95", lambda i: conf[i] < 0.95),
    ]

    lines = [
        "# K3 uzlaşma yönlendirme simülasyonu (Gold-480, tasarım analizi)",
        "",
        "Uyarı: Kurallar Gold-480 hataları incelendikten sonra seçilmiştir; bu tablo held-out sonuç değildir.",
        "Dondurulmuş kurallar: `configs/frozen/K3_ROUTING_POLICIES_v1.json` (AP6'da bir kez test edilecek).",
        "",
        f"Üretim: `python scripts/78_simulate_consensus_routing.py` · sıfır API çağrısı (mevcut tahminler yeniden kullanılır).",
        "",
        "## K1 güveni uzlaşma hatalarını ayırt ediyor mu?",
        "",
        f"- Uzlaşma vakası: {len(consensus)}, uzlaşma hatası: {sum(errors)}",
        f"- AUROC (düşük güven → hata): {auroc:.3f}",
        f"- Güveni ≥ 0.96 olan uzlaşma hatası: {high_conf_errors}/{len(err_conf)}",
        f"- Hata güvenleri: {', '.join(f'{c:.3f}' for c in err_conf)}",
        "",
        "## Yönlendirme kuralları",
        "",
        f"Temel hibrit (yalnız uyuşmazlıklar, V4): {base_correct}/{n} = {base_correct / n:.4f}, "
        f"çağrı {len(disagreement)} ({len(disagreement) / n:.1%}).",
        "",
        "| Uzlaşma kontrol hakemi | Kural | Ek çağrı | Toplam çağrı oranı | Düzelen | Bozulan | Net | Doğruluk | Ek çağrı başına net |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for judge_name, judge in judges.items():
        for name, route in policies:
            routed = [i for i in consensus if route(i) and i in judge]
            fixed = sum(judge[i] == gold[i] and k1[i] != gold[i] for i in routed)
            broken = sum(judge[i] != gold[i] and k1[i] == gold[i] for i in routed)
            acc = (base_correct + fixed - broken) / n
            per_call = (fixed - broken) / len(routed) if routed else float("nan")
            lines.append(
                f"| {judge_name} | {name} | {len(routed)} | {(len(disagreement) + len(routed)) / n:.1%} | "
                f"{fixed} | {broken} | {fixed - broken:+d} | {acc:.4f} | {per_call:+.3f} |"
            )
    lines.append("")

    out = ROOT / "reports" / "K3_CONSENSUS_ROUTING_SIMULATION.md"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
