#!/usr/bin/env python3
"""
150_paired_system_tests.py
Paired significance tests between systems on the three AP6 v2 slices (K-027).

For each slice (medical / legal / finance) and each planned comparison
  P0 - K1, P0 - K2, PA - P0, Gemma26B - PA
the difference in F1 (unsupported class) and in accuracy is estimated with a paired cluster bootstrap
(clusters = questions / reports; 10,000 resamples, seed 42; both systems scored on the same resample).
Reported: point difference, 95% percentile interval, two-sided bootstrap p (2 x the smaller tail share),
Holm-adjusted p within slice and metric (4 comparisons), and the exact McNemar test on the binary decisions
(sentence level, ignores clustering; supporting check only). Rows where either system has no prediction
are dropped for that comparison (medical: 1 K2 atomiser failure).

Input:  <build>/predictions/system_predictions.jsonl (scripts/120)
Output: docs/ap6v2_paired_tests.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parent.parent
SLICES = {
    "medical": ROOT / "data" / "ragbench" / "medical" / "build",
    "legal": ROOT / "data" / "claimrag_law" / "build",
    "finance": ROOT / "data" / "findver" / "build",
}
PAIRS = [("hybrid_P0", "k1"), ("hybrid_P0", "k2"), ("hybrid_PA", "hybrid_P0"), ("gemma26b_zero_shot", "hybrid_PA")]
NAMES = {"k1": "K1", "k2": "K2", "hybrid_P0": "P0", "hybrid_PA": "PA", "gemma26b_zero_shot": "Gemma26B"}
N_BOOT, SEED = 10000, 42


def f1(p: np.ndarray, y: np.ndarray) -> float:
    tp = int((p & y).sum()); fp = int((p & ~y).sum()); fn = int((~p & y).sum())
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def holm(ps: list[float]) -> list[float]:
    order = np.argsort(ps)
    adj, running = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def main() -> None:
    out = {"method": f"paired cluster bootstrap ({N_BOOT} resamples, seed {SEED}), 95% percentile; "
                     "two-sided bootstrap p; Holm within slice x metric; exact McNemar (sentence level)",
           "slices": {}}
    for name, build in SLICES.items():
        rows = [json.loads(l) for l in (build / "predictions" / "system_predictions.jsonl").open(encoding="utf-8")]
        rng = np.random.default_rng(SEED)
        clusters = sorted({r["question_id"] for r in rows})
        draws = [rng.choice(len(clusters), len(clusters)) for _ in range(N_BOOT)]
        res = []
        for a, b in PAIRS:
            keep = [r for r in rows if r[a] is not None and r[b] is not None]
            y = np.array([r["gold_binary"] == "unsupported" for r in keep])
            pa = np.array([r[a] != "supported" for r in keep])
            pb = np.array([r[b] != "supported" for r in keep])
            by_c = defaultdict(list)
            for i, r in enumerate(keep):
                by_c[r["question_id"]].append(i)
            d_f1, d_acc = [], []
            for q in draws:
                idx = np.concatenate([by_c[clusters[j]] for j in q if clusters[j] in by_c])
                yy = y[idx]
                d_f1.append(f1(pa[idx], yy) - f1(pb[idx], yy))
                d_acc.append(float(((pa[idx] == yy).mean()) - ((pb[idx] == yy).mean())))
            only_a = int(((pa == y) & (pb != y)).sum())
            only_b = int(((pb == y) & (pa != y)).sum())
            entry = {"comparison": f"{NAMES[a]} - {NAMES[b]}", "n": len(keep)}
            for metric, point, dist in (("f1", f1(pa, y) - f1(pb, y), d_f1),
                                        ("accuracy", float((pa == y).mean() - (pb == y).mean()), d_acc)):
                dist = np.array(dist)
                p = min(1.0, 2 * min(float((dist <= 0).mean()), float((dist >= 0).mean())))
                entry[metric] = {"diff": round(point, 4),
                                 "ci95": [round(float(np.percentile(dist, 2.5)), 4), round(float(np.percentile(dist, 97.5)), 4)],
                                 "p_boot": round(p, 4)}
            entry["mcnemar"] = {"only_first_correct": only_a, "only_second_correct": only_b,
                                "p_exact": round(binomtest(min(only_a, only_b), only_a + only_b, 0.5).pvalue, 4)
                                if only_a + only_b else None}
            res.append(entry)
        for metric in ("f1", "accuracy"):
            for e, p in zip(res, holm([e[metric]["p_boot"] for e in res])):
                e[metric]["p_holm"] = round(p, 4)
        out["slices"][name] = {"n_rows": len(rows), "n_clusters": len(clusters), "comparisons": res}

    path = ROOT / "docs" / "ap6v2_paired_tests.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, s in out["slices"].items():
        print(f"\n== {name}  (n={s['n_rows']}, kümeler={s['n_clusters']})")
        print(f"{'karşılaştırma':18} {'ΔF1':>7} {'[95% GA]':>18} {'p_holm':>7} | {'ΔDoğruluk':>9} {'[95% GA]':>18} {'p_holm':>7} | McNemar")
        for e in s["comparisons"]:
            f, a, m = e["f1"], e["accuracy"], e["mcnemar"]
            print(f"{e['comparison']:18} {f['diff']:+7.3f} {str(f['ci95']):>18} {f['p_holm']:7.3f} | "
                  f"{a['diff']:+9.3f} {str(a['ci95']):>18} {a['p_holm']:7.3f} | "
                  f"{m['only_first_correct']}/{m['only_second_correct']} p={m['p_exact']}")


if __name__ == "__main__":
    main()
