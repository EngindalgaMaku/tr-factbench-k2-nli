import numpy as np

from k2_nli.labels import NLI_LABELS
from k2_nli.metrics import evaluate_predictions


def test_perfect_metrics():
    labels = list(NLI_LABELS)
    y_true = labels
    y_pred = labels
    probabilities = np.eye(3)
    result = evaluate_predictions(y_true, y_pred, probabilities, labels)
    assert result["accuracy"] == 1.0
    assert result["macro_f1"] == 1.0
    assert result["confusion_matrix"] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
