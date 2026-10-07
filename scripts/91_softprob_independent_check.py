#!/usr/bin/env python3
"""Soft-prob toplulaştırma kuralının Gold-480 dışında sınanması (2026-10-07).

Soft-prob kuralı Gold-480 üzerinde seçildi (K2-AGG-ABLATION-GOLD480-v1). Bu betik, aynı kuralı
Gold-480 ile örtüşmeyen 200 iddialık pilot kümede (legacy test960'tan, sınıf başına 50; önermeler
asistan taslağı) kayıtlı NLI çıktıları üzerinden yeniden hesaplar ve düz kuralla karşılaştırır.
Yeni çıkarım yapılmaz. Bootstrap: 5.000 tekrar, seed 42, iddia düzeyinde.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from k2_nli.aggregation_ablation import aggregate_flat, aggregate_soft_prob  # noqa: E402

LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
RUNS = {"pilot200": ROOT / "runs" / "K2-ATOM-ASSISTED-ZS-PILOT-v1.1__mdeberta_base_2mil7",
        "gold480": ROOT / "runs" / "K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7"}


def read(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def mf1(y, p) -> float:
    return f1_score(y, p, labels=LABELS, average="macro")


def main() -> None:
    lines = ["# Soft-prob toplulaştırma: Gold-480 dışı sınama", "",
             "| Küme | n | Düz kural | Soft-prob | Fark | %95 GA (bootstrap) | Değişen iddia | Yalnız soft doğru / yalnız düz doğru |",
             "|---|---:|---:|---:|---:|---|---:|---|"]
    for name, run in RUNS.items():
        atoms = read(run / "atom_predictions.jsonl")
        gold = {r["example_id"]: r["gold_label"] for r in read(run / "predictions.jsonl")}
        g: dict[str, list] = {}
        for a in atoms:
            g.setdefault(a["example_id"], []).append(a)
        ids = sorted(g)
        y = [gold[i] for i in ids]
        flat = [aggregate_flat([a["pred_label"] for a in g[i]]) for i in ids]
        soft = [aggregate_soft_prob(g[i]) for i in ids]
        rng = random.Random(42)
        d = []
        for _ in range(5000):
            ix = [rng.randrange(len(ids)) for _ in ids]
            yy = [y[k] for k in ix]
            d.append(mf1(yy, [soft[k] for k in ix]) - mf1(yy, [flat[k] for k in ix]))
        d.sort()
        b = sum(s == t and f != t for s, f, t in zip(soft, flat, y))
        c = sum(s != t and f == t for s, f, t in zip(soft, flat, y))
        lines.append(f"| {name} | {len(ids)} | {mf1(y, flat):.4f} | {mf1(y, soft):.4f} | {mf1(y, soft) - mf1(y, flat):+.4f} | "
                     f"[{d[125]:+.4f}, {d[4875]:+.4f}] | {sum(f != s for f, s in zip(flat, soft))} | {b} / {c} |")
    out = ROOT / "reports" / "K2_SOFTPROB_INDEPENDENT_CHECK.md"
    lines += ["", "Pilot kümesi Gold-480 ile iddia düzeyinde örtüşmez (0/200). Pilotta önermeler Gemma atomizerinden değil, asistan taslağından gelir."]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
