import pytest

from k2_nli.aggregation import aggregate_atom_labels


def test_supported():
    assert aggregate_atom_labels(["entailment", "entailment"]) == "supported"


def test_partially_supported():
    assert aggregate_atom_labels(["entailment", "neutral"]) == "partially_supported"
    assert aggregate_atom_labels(["entailment", "contradiction"]) == "partially_supported"


def test_contradicted():
    assert aggregate_atom_labels(["neutral", "contradiction"]) == "contradicted"
    assert aggregate_atom_labels(["contradiction", "contradiction"]) == "contradicted"


def test_unverifiable():
    assert aggregate_atom_labels(["neutral", "neutral"]) == "unverifiable"


def test_empty_fails():
    with pytest.raises(ValueError):
        aggregate_atom_labels([])
