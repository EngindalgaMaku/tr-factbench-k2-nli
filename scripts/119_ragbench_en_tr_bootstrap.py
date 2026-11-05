#!/usr/bin/env python3
"""
119_ragbench_en_tr_bootstrap.py
Confidence intervals for the English vs Turkish NLI comparison (K-019).

Sentences of the same question share a context and the two answers to it, so they are
not independent. The bootstrap therefore resamples QUESTIONS (cluster bootstrap, 74
clusters), takes all sentences of each drawn question, and recomputes both languages on
the same resample (paired). Reported: 95% percentile intervals for F1 and AUROC per
language and for the difference TR - EN, plus the share of resamples in which TR > EN.

As a second, sentence-level check the exact McNemar test is run on the binary decisions
(it ignores clustering, so it is only a supporting check).

Input:  data/ragbench/medical/build/en_tr_nli_scores.jsonl (from scripts/118)
Output: data/ragbench/medical/build/en_tr_bootstrap.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "data" / "ragbench" / "medical" / "build"
N_BOOT = 10000
SEED = 42


def f1(pred: np.ndarray, y: np.ndarray) -> float:
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def main() -> None:
    rows = [json.loads(l) for l in (BUILD / "en_tr_nli_scores.jsonl").open(encoding="utf-8")]
    by_q: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        by_q[r["question_id"]].append(i)
    questions = sorted(by_q)
    y = np.array([1 if r["gold"] == "unsupported" else 0 for r in rows])
    pe = np.array([r["en_pred_unsupported"] for r in rows])
    pt = np.array([r["tr_pred_unsupported"] for r in rows])
    se = np.array([r["en_score"] for r in rows])
    st = np.array([r["tr_score"] for r in rows])

    point = {"en_f1": f1(pe, y), "tr_f1": f1(pt, y),
             "en_auroc": roc_auc_score(y, se), "tr_auroc": roc_auc_score(y, st)}

    rng = np.random.default_rng(SEED)
    draws = defaultdict(list)
    skipped = 0
    for _ in range(N_BOOT):
        qs = rng.choice(len(questions), len(questions), replace=True)
        idx = np.concatenate([by_q[questions[q]] for q in qs])
        yy = y[idx]
        if yy.min() == yy.max():          # AUROC undefined without both classes
            skipped += 1
            continue
        ef, tf = f1(pe[idx], yy), f1(pt[idx], yy)
        ea, ta = roc_auc_score(yy, se[idx]), roc_auc_score(yy, st[idx])
        for k, v in (("en_f1", ef), ("tr_f1", tf), ("diff_f1", tf - ef),
                     ("en_auroc", ea), ("tr_auroc", ta), ("diff_auroc", ta - ea)):
            draws[k].append(v)

    ci = lambda k: [round(float(np.percentile(draws[k], 2.5)), 4), round(float(np.percentile(draws[k], 97.5)), 4)]
    b = int(((pe == 1) & (pt == 0)).sum())   # EN says unsupported, TR says supported
    c = int(((pe == 0) & (pt == 1)).sum())   # TR says unsupported, EN says supported
    result = {
        "method": f"paired cluster bootstrap over questions ({len(questions)} clusters, {N_BOOT} resamples, seed {SEED}); "
                  "95% percentile intervals",
        "n_sentences": len(rows), "n_questions": len(questions), "resamples_skipped": skipped,
        "english": {"f1": round(point["en_f1"], 4), "f1_ci95": ci("en_f1"),
                    "auroc": round(point["en_auroc"], 4), "auroc_ci95": ci("en_auroc")},
        "turkish": {"f1": round(point["tr_f1"], 4), "f1_ci95": ci("tr_f1"),
                    "auroc": round(point["tr_auroc"], 4), "auroc_ci95": ci("tr_auroc")},
        "difference_tr_minus_en": {
            "f1": round(point["tr_f1"] - point["en_f1"], 4), "f1_ci95": ci("diff_f1"),
            "auroc": round(point["tr_auroc"] - point["en_auroc"], 4), "auroc_ci95": ci("diff_auroc"),
            "share_resamples_tr_better_auroc": round(float(np.mean(np.array(draws["diff_auroc"]) > 0)), 4),
        },
        "mcnemar_binary_decisions": {"en_only_unsupported": b, "tr_only_unsupported": c,
                                     "p_exact": round(binomtest(min(b, c), b + c, 0.5).pvalue, 4) if b + c else None,
                                     "note": "sentence-level, ignores clustering; supporting check only"},
    }
    (BUILD / "en_tr_bootstrap.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
