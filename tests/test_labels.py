import pytest

from k2_nli.labels import claim_to_nli3


def test_claim_mapping():
    assert claim_to_nli3("supported") == "entailment"
    assert claim_to_nli3("contradicted") == "contradiction"
    assert claim_to_nli3("unverifiable") == "neutral"
    assert claim_to_nli3("partially_supported") is None


def test_unknown_claim_label_fails():
    with pytest.raises(ValueError):
        claim_to_nli3("unknown")
