#!/usr/bin/env python3
"""
100_k2_calibrated_aggregation.py
================================
Hibrit v2 / Faz 1 — K2 Kalibre Edilmiş Kümeleme (Bulgu #5, #5A, #9).

Kural (soft_prob_avg'ye iki ekleme):
  1) Zayıf entailment düşürme: argmax'ı entailment olan bir atomun P(E) < tau_e ise
     atom, N ve C arasından büyük olana düşürülür (P(E)<0.50 argmax paradoksu dahil).
  2) Çelişki önceliği: Hiç entailment atomu kalmamışsa ve en az bir atomda
     P(C) >= tau_c ise iddia 'contradicted' olur (Soft-Prob ortalaması N'ye kaymasın).
  Geri kalan durumlarda mevcut soft_prob_avg mantığı aynen uygulanır.

Sızıntı protokolü (HIBRIT_V2_METODOLOJI_VE_YOL_HARITASI.md):
  - Eşikler YALNIZCA DEV-1 (K2-ATOM-ASSISTED-ZS-PILOT-v1.1, 200 dengeli örnek) üzerinde seçilir.
  - DEV-2 (ATOMIZERTEST) ikinci kontrol, Gold-480 yalnızca dondurulmuş eşiklerle raporlanır.
  - Natural RAG-413 bu betikte hiç okunmaz.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from scipy.stats import binomtest  # noqa: E402
from sklearn.metrics import accuracy_score, f1_score  # noqa: E402

from k2_nli.aggregation_ablation import aggregate_flat, aggregate_soft_prob  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent  # k2_nli/
PROJ = ROOT.parent
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
RUNS = {
    "DEV1_pilot200": "K2-ATOM-ASSISTED-ZS-PILOT-v1.1__mdeberta_base_2mil7",
    "DEV2_atomizertest": "K2-PIPE-PRED-ZS-ATOMIZERTEST-v1__mdeberta_base_2mil7",
    "GOLD480": "K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7",
}
OUT = ROOT / "reports" / "experiments" / "HIBRIT-V2-K2-CALIBRATED-AGG-v1"


def load(run: str) -> list[dict]:
    d = ROOT / "runs" / run
    p = d / "scored_predictions.jsonl"
    p = p if p.exists() else d / "predictions.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if r.get("atoms")]


def effective_label(a: dict, tau_e: float) -> str:
    pe, pn, pc = (float(a.get(k, 0.0)) for k in ("prob_entailment", "prob_neutral", "prob_contradiction"))
    lbl = str(a.get("pred_label", "")).strip().lower()
    if lbl == "entailment" and pe < tau_e:
        return "contradiction" if pc > pn else "neutral"
    return lbl


def aggregate_calibrated(atoms: list[dict], tau_e: float, tau_c: float | None) -> str:
    labels = [effective_label(a, tau_e) for a in atoms]
    if all(l == "entailment" for l in labels):
        return "supported"
    if "entailment" in labels:
        return "partially_supported"
    if tau_c is not None and any(float(a.get("prob_contradiction", 0.0)) >= tau_c for a in atoms):
        return "contradicted"
    n = max(len(atoms), 1)
    p_e = sum(float(a.get("prob_entailment", 0.0)) for a in atoms) / n
    p_n = sum(float(a.get("prob_neutral", 0.0)) for a in atoms) / n
    p_c = sum(float(a.get("prob_contradiction", 0.0)) for a in atoms) / n
    if p_c > max(p_e, p_n):
        return "contradicted"
    if p_n > max(p_e, p_c):
        return "unverifiable"
    return aggregate_flat(labels)


def metrics(y, pred) -> dict:
    return {
        "acc": round(accuracy_score(y, pred), 4),
        "macro_f1": round(f1_score(y, pred, labels=LABELS, average="macro", zero_division=0), 4),
    }


def mcnemar(y, base, new) -> dict:
    no = sum(n == g and b != g for g, b, n in zip(y, base, new))
    bo = sum(b == g and n != g for g, b, n in zip(y, base, new))
    p = 1.0 if no + bo == 0 else float(binomtest(min(no, bo), no + bo, 0.5).pvalue)
    return {"new_only_correct": no, "base_only_correct": bo, "mcnemar_p": round(p, 5)}


def main() -> None:
    data = {k: load(v) for k, v in RUNS.items()}

    # --- 1) Eşik seçimi: yalnızca DEV-1 ---
    dev = data["DEV1_pilot200"]
    y_dev = [r["gold_label"] for r in dev]
    grid_e = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    grid_c = [None, 0.60, 0.70, 0.80, 0.90]
    search = []
    for te, tc in itertools.product(grid_e, grid_c):
        pred = [aggregate_calibrated(r["atoms"], te, tc) for r in dev]
        search.append({"tau_e": te, "tau_c": tc, **metrics(y_dev, pred)})
    # Seçim: en yüksek DEV-1 Macro-F1; eşitlikte daha muhafazakâr (küçük tau_e, tau_c=None tercih)
    best = max(search, key=lambda s: (s["macro_f1"], -s["tau_e"], s["tau_c"] is None))
    te, tc = best["tau_e"], best["tau_c"]

    # --- 2) Dondurulmuş eşiklerle tüm kümelerde rapor ---
    report = {"selected_on": "DEV1_pilot200", "tau_e": te, "tau_c": tc, "grid_search_dev1": search, "sets": {}}
    gold_rows_out = []
    for name, rows in data.items():
        y = [r["gold_label"] for r in rows]
        base = [aggregate_soft_prob(r["atoms"]) for r in rows]
        new = [aggregate_calibrated(r["atoms"], te, tc) for r in rows]
        # Bileşen ablasyonu: yalnızca kural 1 / yalnızca kural 2
        only_e = [aggregate_calibrated(r["atoms"], te, None) for r in rows]
        only_c = [aggregate_calibrated(r["atoms"], 0.0, tc) for r in rows] if tc else base
        report["sets"][name] = {
            "n": len(rows),
            "soft_prob_avg (v1)": metrics(y, base),
            "calibrated (v2)": metrics(y, new),
            "ablation_only_weak_entailment_demotion": metrics(y, only_e),
            "ablation_only_contradiction_priority": metrics(y, only_c),
            "changed": sum(a != b for a, b in zip(base, new)),
            **mcnemar(y, base, new),
        }
        if name == "GOLD480":
            for r, b, n in zip(rows, base, new):
                gold_rows_out.append({"example_id": r["example_id"], "gold_label": r["gold_label"],
                                      "k2_v1": b, "k2_v2": n})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    with (OUT / "gold480_k2_v1_vs_v2.jsonl").open("w", encoding="utf-8") as f:
        for r in gold_rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Seçilen eşikler (DEV-1): tau_e={te}, tau_c={tc}  | DEV-1 Macro-F1={best['macro_f1']}")
    print("\nDEV-1 ızgara (ilk 8, Macro-F1'e göre):")
    for s in sorted(search, key=lambda s: -s["macro_f1"])[:8]:
        print(f"  tau_e={s['tau_e']:.2f} tau_c={s['tau_c']}  acc={s['acc']}  F1={s['macro_f1']}")
    for name, s in report["sets"].items():
        print(f"\n== {name} (n={s['n']})")
        for k in ("soft_prob_avg (v1)", "calibrated (v2)", "ablation_only_weak_entailment_demotion",
                  "ablation_only_contradiction_priority"):
            print(f"  {k:42s} acc={s[k]['acc']}  F1={s[k]['macro_f1']}")
        print(f"  değişen={s['changed']}  yeni-doğru={s['new_only_correct']}  "
              f"eski-doğru={s['base_only_correct']}  McNemar p={s['mcnemar_p']}")


if __name__ == "__main__":
    main()
