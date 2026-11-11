#!/usr/bin/env python3
"""
152_balanced_metrics.py  (2026-11-10, jüri ön incelemesi sonrası; KARAR_KAYDI #73)
AP6 v2 kesitlerinde sınıf dengesizliğinden etkilenmeyen ek ölçütler (sonradan eklenen betimsel analiz).

Her kesit ve sistem için: doğruluk, desteklenmeyen sınıf F1, dengeli doğruluk (duyarlılık ile özgüllüğün
ortalaması), Matthews korelasyon katsayısı (MCC). Taban çizgileri: bütün birimleri desteklenmeyen işaretleyen
(F1 taban çizgisi) ve bütün birimleri çoğunluk sınıfına atayan (doğruluk taban çizgisi). Tıp kesiti ayrıca
iki noktayla biten içerik taşımayan giriş cümleleri hariç (n = 723) hesaplanır. Sistem kararları
değiştirilmez; girdi scripts/120'nin system_predictions.jsonl dosyalarıdır.

Çıktı: docs/ap6v2_balanced_metrics.json
"""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLICES = {
    "medical": (ROOT / "data/ragbench/medical/build", "ragbench_tr_medical_claims.jsonl"),
    "legal": (ROOT / "data/claimrag_law/build", "claimrag_tr_law_claims.jsonl"),
    "finance": (ROOT / "data/findver/build", None),
}
SYSTEMS = ["k1", "k2", "hybrid_P0", "hybrid_PA", "gemma26b_zero_shot"]


def metrics(pairs):
    tp = sum(p and t for p, t in pairs); fp = sum(p and not t for p, t in pairs)
    fn = sum((not p) and t for p, t in pairs); tn = len(pairs) - tp - fp - fn
    tpr = tp / (tp + fn) if tp + fn else 0.0; tnr = tn / (tn + fp) if tn + fp else 0.0
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return {"n": len(pairs), "accuracy": round((tp + tn) / len(pairs), 4),
            "f1_unsupported": round(2 * tp / (2 * tp + fp + fn), 4) if tp else 0.0,
            "balanced_accuracy": round((tpr + tnr) / 2, 4),
            "mcc": round((tp * tn - fp * fn) / den, 4) if den else 0.0}


def block(rows):
    y = [r["gold_binary"] == "unsupported" for r in rows]
    n, pos = len(y), sum(y)
    out = {"n": n, "n_unsupported": pos, "unsupported_rate": round(pos / n, 4),
           "baseline_all_unsupported": metrics([(True, t) for t in y]),
           "baseline_majority": {"class": "unsupported" if pos > n - pos else "supported",
                                 "accuracy": round(max(pos, n - pos) / n, 4)},
           "systems": {}}
    for s in SYSTEMS:
        out["systems"][s] = metrics([(r[s] != "supported", t) for r, t in zip(rows, y) if r[s] is not None])
    return out


def main():
    res = {"note": "post hoc descriptive metrics; system decisions unchanged", "slices": {}}
    for name, (build, claims) in SLICES.items():
        rows = [json.loads(l) for l in (build / "predictions/system_predictions.jsonl").open(encoding="utf-8")]
        res["slices"][name] = block(rows)
        if name == "medical":
            cl = {json.loads(l)["example_id"]: json.loads(l)["claim"] for l in (build / claims).open(encoding="utf-8")}
            res["slices"]["medical_no_intro"] = block([r for r in rows if not cl[r["example_id"]].strip().endswith(":")])
    path = ROOT / "docs/ap6v2_balanced_metrics.json"
    path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in res["slices"].items():
        print(f"\n== {k} n={v['n']} çoğunluk={v['baseline_majority']}")
        for s, m in v["systems"].items():
            print(f"  {s:20} acc={m['accuracy']:.3f} f1={m['f1_unsupported']:.3f} dd={m['balanced_accuracy']:.3f} mcc={m['mcc']:.3f}")


if __name__ == "__main__":
    main()
