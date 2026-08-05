from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .io import read_jsonl, stable_text_hash
from .labels import CLAIM_LABELS


def _required_text(item: dict[str, Any], field: str, example_id: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or empty {field!r} for {example_id}")
    return value.strip()


def normalize_atoms(raw_atoms: Any, example_id: str) -> list[dict[str, str]]:
    if not isinstance(raw_atoms, list) or not raw_atoms:
        raise ValueError(f"Invalid or empty atoms list for {example_id}")

    atoms: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for position, raw_atom in enumerate(raw_atoms, start=1):
        if isinstance(raw_atom, str):
            text = raw_atom.strip()
            atom_id = f"{example_id}__a{position}"
        elif isinstance(raw_atom, dict):
            text = str(raw_atom.get("text", "")).strip()
            atom_id = str(raw_atom.get("atom_id") or f"{example_id}__a{position}").strip()
        else:
            raise ValueError(
                f"Atom {position} for {example_id} must be a string or object, got {type(raw_atom).__name__}"
            )
        if not text:
            raise ValueError(f"Empty atom text at position {position} for {example_id}")
        if not atom_id:
            raise ValueError(f"Empty atom_id at position {position} for {example_id}")
        if atom_id in seen_ids:
            raise ValueError(f"Duplicate atom_id {atom_id!r} for {example_id}")
        seen_ids.add(atom_id)
        atoms.append({"atom_id": atom_id, "text": text})
    return atoms


def normalize_combined_record(item: dict[str, Any]) -> dict[str, Any]:
    example_id = _required_text(item, "example_id", "<unknown>")
    gold_label = str(item.get("gold_label") or item.get("claim_gold_label") or "").strip().lower()
    if gold_label not in CLAIM_LABELS:
        raise ValueError(f"Unknown or missing gold label {gold_label!r} for {example_id}")

    record = {
        "example_id": example_id,
        "context_id": str(item.get("context_id", "")).strip(),
        "domain": str(item.get("domain", "")).strip(),
        "context": _required_text(item, "context", example_id),
        "question": str(item.get("question", "")),
        "claim": _required_text(item, "claim", example_id),
        "gold_label": gold_label,
        "atoms": normalize_atoms(item.get("atoms"), example_id),
        "atomization_id": item.get("atomization_id"),
        "atomization_status": item.get("atomization_status"),
        "atomization_notes": item.get("atomization_notes"),
        "atomization_version": item.get("atomization_version") or item.get("atomizer_version"),
    }
    return record


def load_combined_atom_dataset(path: str | Path) -> list[dict[str, Any]]:
    records = [normalize_combined_record(item) for item in read_jsonl(path)]
    if not records:
        raise ValueError(f"No records found in {path}")
    ids = [item["example_id"] for item in records]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate example_id values in {path}: {duplicates[:10]}")
    return records


def load_separate_atom_dataset(
    data_path: str | Path,
    atoms_path: str | Path,
) -> list[dict[str, Any]]:
    claims = {item["example_id"]: item for item in read_jsonl(data_path)}
    atom_records = {item["example_id"]: item for item in read_jsonl(atoms_path)}
    if set(claims) != set(atom_records):
        missing_atoms = sorted(set(claims) - set(atom_records))[:10]
        extra_atoms = sorted(set(atom_records) - set(claims))[:10]
        raise ValueError(
            f"Claim/atom ID mismatch. missing_atoms={missing_atoms}, extra_atoms={extra_atoms}"
        )

    combined: list[dict[str, Any]] = []
    for example_id in sorted(claims):
        claim = claims[example_id]
        atom_item = atom_records[example_id]
        expected_hash = stable_text_hash(str(claim["claim"]))
        if atom_item.get("claim_hash") and atom_item["claim_hash"] != expected_hash:
            raise ValueError(f"Claim hash mismatch for {example_id}")
        merged = dict(claim)
        merged["atoms"] = atom_item.get("atoms")
        merged["atomization_id"] = atom_item.get("atomization_id")
        merged["atomization_status"] = atom_item.get("atomization_status")
        merged["atomization_notes"] = atom_item.get("atomization_notes")
        merged["atomization_version"] = atom_item.get("atomization_version") or atom_item.get("atomizer_version")
        combined.append(normalize_combined_record(merged))
    return combined
