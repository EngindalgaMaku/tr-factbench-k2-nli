from k2_nli.aggregation_ablation import (
    aggregate_contradiction_priority,
    aggregate_flat,
    aggregate_sentence_grouped,
    align_atoms_to_sentences,
    exact_mcnemar,
    split_claim_sentences,
)


def atom(atom_id: str, text: str, label: str) -> dict:
    return {"atom_id": atom_id, "atom": text, "pred_label": label}


def test_flat_prioritizes_any_entailment_over_contradiction():
    assert aggregate_flat(["entailment", "contradiction"]) == "partially_supported"


def test_contradiction_priority_changes_mixed_entailment_contradiction():
    assert aggregate_contradiction_priority(["entailment", "contradiction"]) == "contradicted"


def test_sentence_grouped_makes_false_conjunction_contradicted():
    claim = "Daraltıcı para politikası para arzını azaltır ve enflasyonu yükseltir."
    atoms = [
        atom("a1", "Daraltıcı para politikası para arzını azaltır.", "entailment"),
        atom("a2", "Daraltıcı para politikası enflasyonu yükseltir.", "contradiction"),
    ]
    label, groups = aggregate_sentence_grouped(claim, atoms)
    assert label == "contradicted"
    assert len(groups) == 1
    assert groups[0]["group_label"] == "contradicted"


def test_sentence_grouped_preserves_partial_across_two_sentences():
    claim = "Tedavi ateşi düşürür. Tedavi hastalığı tamamen önler."
    atoms = [
        atom("a1", "Tedavi ateşi düşürür.", "entailment"),
        atom("a2", "Tedavi hastalığı tamamen önler.", "contradiction"),
    ]
    label, groups = aggregate_sentence_grouped(claim, atoms)
    assert label == "partially_supported"
    assert [group["group_label"] for group in groups] == ["supported", "contradicted"]


def test_sentence_alignment_uses_lexical_overlap():
    claim = "Fon emri aynı gün alınır. Takas iki iş günü sonra tamamlanır."
    atoms = [
        atom("a1", "Takas iki iş günü sonra tamamlanır.", "entailment"),
        atom("a2", "Fon emri aynı gün alınır.", "entailment"),
    ]
    assert split_claim_sentences(claim) == [
        "Fon emri aynı gün alınır.",
        "Takas iki iş günü sonra tamamlanır.",
    ]
    assert align_atoms_to_sentences(claim, atoms) == [1, 0]


def test_exact_mcnemar_counts_direction():
    result = exact_mcnemar(
        [True, True, False, False, True],
        [True, False, True, False, True],
    )
    assert result["flat_only_correct"] == 1
    assert result["alternative_only_correct"] == 1
    assert result["discordant"] == 2
    assert result["exact_p_value"] == 1.0
