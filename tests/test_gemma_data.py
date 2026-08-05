from __future__ import annotations

import json

from k2_nli.gemma_data import load_gemma_predicted_dataset, summarize_gemma_dataset


def _write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def test_load_gemma_dataset_preserves_valid_and_failed_records(tmp_path):
    path = tmp_path / "gemma.jsonl"
    _write_jsonl(path, [
        {
            "example_id": "ex1",
            "source_example_id": "src1",
            "domain": "legal",
            "gold_label": "partially_supported",
            "context": "Bağlam.",
            "claim": "Birleşik iddia.",
            "pred_atoms": ["İlk atom", "İkinci atom"],
            "json_valid": True,
            "atom_count_correct": True,
        },
        {
            "example_id": "ex2",
            "source_example_id": "src2",
            "domain": "medical",
            "gold_label": "supported",
            "context": "Başka bağlam.",
            "claim": "Başka iddia.",
            "pred_atoms": [],
            "json_valid": False,
            "atom_count_correct": False,
        },
    ])

    records = load_gemma_predicted_dataset(path)
    assert records[0]["pipeline_ready"] is True
    assert [atom["text"] for atom in records[0]["atoms"]] == ["İlk atom", "İkinci atom"]
    assert records[1]["pipeline_ready"] is False
    assert records[1]["failure_reason"] == "invalid_atomizer_json"
    assert records[1]["atoms"] == []

    summary = summarize_gemma_dataset(records)
    assert summary["n_input_claims"] == 2
    assert summary["n_pipeline_ready"] == 1
    assert summary["n_atomizer_failures"] == 1
    assert summary["n_predicted_atoms"] == 2
    assert summary["failure_gold_label_counts"] == {"supported": 1}


def test_atom_count_mismatch_does_not_exclude_valid_prediction(tmp_path):
    path = tmp_path / "gemma.jsonl"
    _write_jsonl(path, [{
        "example_id": "ex1",
        "source_example_id": "src1",
        "domain": "finance",
        "gold_label": "supported",
        "context": "Bağlam.",
        "claim": "İddia.",
        "pred_atoms": ["Kullanılabilir atom"],
        "json_valid": True,
        "atom_count_correct": False,
    }])
    record = load_gemma_predicted_dataset(path)[0]
    assert record["pipeline_ready"] is True
    assert record["atom_count_correct"] is False
