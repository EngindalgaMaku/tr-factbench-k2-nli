from __future__ import annotations

import json

import pytest

from k2_nli.atom_data import load_combined_atom_dataset, normalize_atoms


def test_normalize_atoms_accepts_objects_and_strings() -> None:
    atoms = normalize_atoms(
        [
            {"atom_id": "ex__a1", "text": "Birinci önerme."},
            "İkinci önerme.",
        ],
        "ex",
    )
    assert atoms == [
        {"atom_id": "ex__a1", "text": "Birinci önerme."},
        {"atom_id": "ex__a2", "text": "İkinci önerme."},
    ]


def test_load_combined_atom_dataset(tmp_path) -> None:
    path = tmp_path / "atoms.jsonl"
    record = {
        "example_id": "ex1",
        "context_id": "ctx1",
        "domain": "legal",
        "context": "Bir bağlam.",
        "claim": "İki önerme vardır.",
        "gold_label": "supported",
        "atoms": [{"atom_id": "ex1__a1", "text": "Bir önerme vardır."}],
        "atomization_version": "assistant_draft_v1",
    }
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = load_combined_atom_dataset(path)
    assert rows[0]["example_id"] == "ex1"
    assert rows[0]["atoms"][0]["text"] == "Bir önerme vardır."


def test_duplicate_example_ids_are_rejected(tmp_path) -> None:
    path = tmp_path / "atoms.jsonl"
    record = {
        "example_id": "ex1",
        "context": "Bağlam.",
        "claim": "Claim.",
        "gold_label": "supported",
        "atoms": ["Atom."],
    }
    path.write_text(
        json.dumps(record, ensure_ascii=False) + "\n" + json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate example_id"):
        load_combined_atom_dataset(path)
