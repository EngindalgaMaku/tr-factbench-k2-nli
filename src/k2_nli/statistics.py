from __future__ import annotations

import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import f1_score


def paired_bootstrap_macro_f1_difference(
    y_true: list[str],
    pred_a: list[str],
    pred_b: list[str],
    labels: list[str],
    n_samples: int = 2000,
    seed: int = 42,
) -> dict:
    if not (len(y_true) == len(pred_a) == len(pred_b)):
        raise ValueError("Paired arrays must have equal length")
    rng = np.random.default_rng(seed)
    n = len(y_true)
    differences = np.empty(n_samples, dtype=float)
    true = np.asarray(y_true)
    a = np.asarray(pred_a)
    b = np.asarray(pred_b)
    for index in range(n_samples):
        sample = rng.integers(0, n, size=n)
        f1_a = f1_score(true[sample], a[sample], labels=labels, average="macro", zero_division=0)
        f1_b = f1_score(true[sample], b[sample], labels=labels, average="macro", zero_division=0)
        differences[index] = f1_a - f1_b
    point = f1_score(true, a, labels=labels, average="macro", zero_division=0) - f1_score(
        true, b, labels=labels, average="macro", zero_division=0
    )
    low, high = np.quantile(differences, [0.025, 0.975])
    return {"difference": float(point), "ci95": [float(low), float(high)]}


def exact_mcnemar(y_true: list[str], pred_a: list[str], pred_b: list[str]) -> dict:
    if not (len(y_true) == len(pred_a) == len(pred_b)):
        raise ValueError("Paired arrays must have equal length")
    b = sum(a == gold and c != gold for gold, a, c in zip(y_true, pred_a, pred_b))
    c = sum(a != gold and c == gold for gold, a, c in zip(y_true, pred_a, pred_b))
    discordant = b + c
    p_value = 1.0 if discordant == 0 else float(binomtest(min(b, c), discordant, 0.5).pvalue)
    return {"a_correct_b_wrong": b, "a_wrong_b_correct": c, "p_value": p_value}
