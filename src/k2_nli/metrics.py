from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    matthews_corrcoef,
)


def expected_calibration_error(
    y_true: Sequence[str],
    probabilities: np.ndarray,
    labels: Sequence[str],
    n_bins: int = 15,
) -> float:
    label_to_index = {label: index for index, label in enumerate(labels)}
    true_index = np.array([label_to_index[x] for x in y_true])
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    correct = (prediction == true_index).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (confidence > low) & (confidence <= high)
        if not mask.any():
            continue
        ece += mask.mean() * abs(correct[mask].mean() - confidence[mask].mean())
    return float(ece)


def multiclass_brier(
    y_true: Sequence[str], probabilities: np.ndarray, labels: Sequence[str]
) -> float:
    label_to_index = {label: index for index, label in enumerate(labels)}
    targets = np.zeros_like(probabilities, dtype=float)
    for row, label in enumerate(y_true):
        targets[row, label_to_index[label]] = 1.0
    return float(np.mean(np.sum((probabilities - targets) ** 2, axis=1)))


def evaluate_predictions(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    probabilities: np.ndarray,
    labels: Sequence[str],
    ece_bins: int = 15,
) -> dict:
    if len(y_true) == 0:
        raise ValueError("No examples to evaluate")
    if probabilities.shape != (len(y_true), len(labels)):
        raise ValueError("Probability matrix has an incompatible shape")
    report = classification_report(
        y_true,
        y_pred,
        labels=list(labels),
        target_names=list(labels),
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=list(labels))
    return {
        "n_examples": len(y_true),
        "labels": list(labels),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "weighted_f1": float(report["weighted avg"]["f1-score"]),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "nll": float(-np.mean(np.log(np.clip(
            probabilities[np.arange(len(y_true)), np.array([{label: i for i, label in enumerate(labels)}[x] for x in y_true])],
            1e-12,
            1.0,
        )))),
        "multiclass_brier": multiclass_brier(y_true, probabilities, labels),
        "ece": expected_calibration_error(y_true, probabilities, labels, ece_bins),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }
