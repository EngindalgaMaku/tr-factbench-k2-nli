#!/usr/bin/env python3
"""
98_gold480_binary_posthoc.py — SONRADAN (post-hoc) BETİMSEL ANALİZ, yazar onayıyla (2026-10-08).

AP6'nın ikili ölçütleri (yanlış alarm, kesinlik, duyarlılık, F1; halüsinasyon = supported değil) Gold-480'de, AP6'da
değerlendirilen sistemlerin aynı yapılandırmalarıyla hesaplanır. Amaç yalnızca iki değerlendirmeyi aynı ölçüyle yan yana
koymaktır (tez 4.10). Yeni model çalıştırılmaz; tahminler betik 92'nin kullandığı dondurulmuş dosyalardır.
Sistemler: K1; K2 soft-prob; hibrit P0 (Llama-70B V4 hakemi); PA ve PB (kör Gemma-4-26B uzlaşma denetimi);
tek başına Gemma-4-26B örneksiz; tek başına GPT-4.1-mini 8 örnek.
GA: bağlam grubu bootstrap (10.000, seed 42; betik 92 ile aynı birim).
Çıktı: reports/GOLD480_BINARY_POSTHOC.{md,json}
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
GOLD_DIR = TFB / "data" / "evaluation" / "gold_v1.0"
EXP = ROOT / "reports" / "experiments"
LLM = TFB / "results" / "llm_baselines" / "gold_v1.0"
ROUTE = {"partially_supported", "contradicted"}
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]


def rj(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def eid(r: dict) -> str:
    return r.get("release_example_id") or r["example_id"]


def binary(ids, gold, pred) -> dict:
    tp = fp = fn = tn = 0
    for i in ids:
        y, s = gold[i] != "supported", pred[i] != "supported"
        tp += y and s; fp += (not y) and s; fn += y and not s; tn += (not y) and not s
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn) if tp + fn else float("nan")
    return {"false_alarm": fp / (fp + tn), "precision": p, "recall": r, "f1": 2 * p * r / (p + r) if tp else 0.0,
            "accuracy_4class": sum(pred[i] == gold[i] for i in ids) / len(ids)}


def main() -> None:
    rows = rj(GOLD_DIR / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")
    ids = [eid(r) for r in rows]
    gold = {eid(r): r["gold_label"] for r in rows}
    group = {eid(r): r["context"] for r in rows}
    dom = lambda i: "finance" if int(i.rsplit("_", 1)[-1]) <= 160 else ("legal" if int(i.rsplit("_", 1)[-1]) <= 320 else "medical")
    k1 = {eid(r): r["predicted_label"] for r in rj(GOLD_DIR / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")}
    agg = EXP / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
    k2 = {eid(r): r["pred_label"] for r in rj(agg / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")}
    v4 = {r["example_id"]: r["judge_decision"] for r in rj(EXP / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")}
    gz = {eid(r): r["predicted_label"] for r in rj(LLM / "google_gemma-4-26b-a4b-it" / "zero_shot" / "predictions.jsonl")}
    g8 = {eid(r): r["predicted_label"] for r in rj(LLM / "openai_gpt-4.1-mini" / "few_shot_8" / "predictions.jsonl")}
    p0 = {i: k1[i] if k1[i] == k2[i] else v4[i] for i in ids}
    pa = {i: gz[i] if (k1[i] == k2[i] and k1[i] in ROUTE) else p0[i] for i in ids}
    pb = {i: gz[i] if (k1[i] == k2[i] and k1[i] in ROUTE and dom(i) == "medical") else p0[i] for i in ids}
    systems = {"k1": k1, "k2": k2, "hybrid_P0": p0, "hybrid_PA": pa, "hybrid_PB": pb,
               "gemma26b_zero_shot": gz, "gpt41mini_few_shot_8": g8}
    groups = sorted(set(group.values()))
    members = {g: [i for i in ids if group[i] == g] for g in groups}
    rng = random.Random(42)
    boots = [[i for g in (rng.choice(groups) for _ in groups) for i in members[g]] for _ in range(10_000)]
    out = {"n": len(ids), "base_rate_unsupported": sum(gold[i] != "supported" for i in ids) / len(ids),
           "note": "post-hoc, descriptive; same systems as AP6", "systems": {}}
    for s, pred in systems.items():
        rec = binary(ids, gold, pred)
        for k in ("false_alarm", "precision", "recall", "f1"):
            v = sorted(binary(b, gold, pred)[k] for b in boots)
            rec[k + "_ci"] = [v[250], v[9749]]
        out["systems"][s] = rec
    dis = sum(k1[i] != k2[i] for i in ids)
    cons_route = sum(k1[i] == k2[i] and k1[i] in ROUTE for i in ids)
    cons_med = sum(k1[i] == k2[i] and k1[i] in ROUTE and dom(i) == "medical" for i in ids)
    out["llm_call_rate"] = {"P0": dis / len(ids), "PA": (dis + cons_route) / len(ids), "PB": (dis + cons_med) / len(ids)}
    rep = ROOT / "reports"
    (rep / "GOLD480_BINARY_POSTHOC.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    L = ["# Gold-480 — ikili ölçütler (SONRADAN, betimsel; betik 98)", "",
         f"n = {len(ids)}; supported dışı oranı {out['base_rate_unsupported']:.3f}. GA: bağlam grubu bootstrap (10.000, seed 42).", "",
         "| Sistem | Yanlış alarm | Kesinlik | Duyarlılık | F1 | 4 sınıf doğruluk |", "|---|---|---|---|---|---:|"]
    for s, r in out["systems"].items():
        c = lambda k: f"{r[k]:.3f} [{r[k + '_ci'][0]:.3f}, {r[k + '_ci'][1]:.3f}]"
        L.append(f"| {s} | {c('false_alarm')} | {c('precision')} | {c('recall')} | {c('f1')} | {r['accuracy_4class']:.3f} |")
    cr = out["llm_call_rate"]
    L += ["", f"Büyük dil modeli çağrı oranı: P0 {cr['P0']:.3f} · PA {cr['PA']:.3f} · PB {cr['PB']:.3f}"]
    (rep / "GOLD480_BINARY_POSTHOC.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
