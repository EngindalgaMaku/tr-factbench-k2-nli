from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .labels import NLI_LABELS, normalize_nli_label


@dataclass(frozen=True)
class InferenceConfig:
    model_id: str
    batch_size: int = 8
    max_length: int = 512
    device: str | None = None
    trust_remote_code: bool = False


def _resolve_id_to_label(model) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for raw_id, raw_label in model.config.id2label.items():
        try:
            mapping[int(raw_id)] = normalize_nli_label(str(raw_label))
        except ValueError as exc:
            raise ValueError(
                f"Model {model.config.name_or_path!r} has non-semantic id2label={model.config.id2label}. "
                "Add an explicit verified label map before running the experiment."
            ) from exc
    if set(mapping.values()) != set(NLI_LABELS):
        raise ValueError(f"Unexpected model label mapping: {mapping}")
    return mapping


def run_pair_inference(
    premises: list[str],
    hypotheses: list[str],
    config: InferenceConfig,
) -> tuple[list[dict], dict]:
    if len(premises) != len(hypotheses):
        raise ValueError("Premises and hypotheses must have equal length")
    device = config.device or ("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, trust_remote_code=config.trust_remote_code
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        config.model_id, trust_remote_code=config.trust_remote_code
    ).to(device)
    model.eval()
    id_to_label = _resolve_id_to_label(model)
    canonical_to_model_id = {label: index for index, label in id_to_label.items()}

    predictions: list[dict] = []
    truncated_pairs = 0
    started = time.perf_counter()
    peak_memory = 0
    if device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()

    for start in range(0, len(premises), config.batch_size):
        batch_p = premises[start:start + config.batch_size]
        batch_h = hypotheses[start:start + config.batch_size]
        raw_pairs = tokenizer(
            batch_p,
            batch_h,
            padding=False,
            truncation=False,
            add_special_tokens=True,
        )["input_ids"]
        raw_hypotheses = tokenizer(
            batch_h,
            padding=False,
            truncation=False,
            add_special_tokens=False,
        )["input_ids"]
        batch_truncated = [len(ids) > config.max_length for ids in raw_pairs]
        truncated_pairs += sum(batch_truncated)
        if any(len(ids) + 4 >= config.max_length for ids in raw_hypotheses):
            raise ValueError(
                "At least one hypothesis is too long to preserve under truncation='only_first'."
            )
        # Atom/claim hypothesis is always preserved. Only the evidence premise may be shortened.
        encoded = tokenizer(
            batch_p,
            batch_h,
            padding=True,
            truncation="only_first",
            max_length=config.max_length,
            return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.inference_mode():
            logits = model(**encoded).logits
            probabilities = torch.softmax(logits, dim=-1).detach().cpu().numpy()
        for local_index, row in enumerate(probabilities):
            canonical = np.array([
                row[canonical_to_model_id["entailment"]],
                row[canonical_to_model_id["neutral"]],
                row[canonical_to_model_id["contradiction"]],
            ], dtype=float)
            canonical = canonical / canonical.sum()
            pred_index = int(canonical.argmax())
            predictions.append({
                "pred_label": NLI_LABELS[pred_index],
                "prob_entailment": float(canonical[0]),
                "prob_neutral": float(canonical[1]),
                "prob_contradiction": float(canonical[2]),
                "confidence": float(canonical.max()),
                "was_truncated": bool(batch_truncated[local_index]),
                "pair_tokens_untruncated": int(len(raw_pairs[local_index])),
                "hypothesis_tokens": int(len(raw_hypotheses[local_index])),
            })

    if device.startswith("cuda"):
        peak_memory = int(torch.cuda.max_memory_allocated())
    elapsed = time.perf_counter() - started
    metadata = {
        "model_id": config.model_id,
        "model_revision": getattr(model.config, "_commit_hash", None),
        "tokenizer_revision": getattr(tokenizer, "_commit_hash", None),
        "device": device,
        "batch_size": config.batch_size,
        "max_length": config.max_length,
        "truncation": "only_first",
        "n_pairs": len(premises),
        "n_truncated_pairs": truncated_pairs,
        "elapsed_seconds": elapsed,
        "pairs_per_second": len(premises) / elapsed if elapsed else None,
        "peak_gpu_memory_bytes": peak_memory,
        "model_id2label": {str(k): v for k, v in id_to_label.items()},
    }
    return predictions, metadata
