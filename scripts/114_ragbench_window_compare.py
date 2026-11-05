#!/usr/bin/env python3
"""
114_ragbench_window_compare.py
Decision K-017, full comparison: runs the frozen K2 NLI model over the whole
Turkish RAGBench medical slice twice and reports binary agreement with the
silver labels.

  A) premise = full context, truncated at 512 tokens (today's behaviour)
  B) premise = each source document separately, strongest support kept

Binary mapping: entailment -> supported, otherwise -> unsupported. Metrics are
reported for the "unsupported" (hallucination) class, as in AP6 v1.

As in the smoke test this feeds the claim sentence directly as the hypothesis and
skips the Gemma atomiser, so these are NLI verdicts, not full K2 claim labels.
Nothing is written to runs/; the comparison is saved next to the dataset.

Usage: python scripts/114_ragbench_window_compare.py
Output: data/ragbench/medical/build/window_compare.json
"""
from __future__ import annotations

import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "data" / "ragbench" / "medical" / "build"
MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
MAX_LENGTH = 512
BATCH = 16
ORDER = {"entailment": 0, "neutral": 1, "contradiction": 2}


def scores_for(model, tokenizer, device, id2label, premises, hypotheses) -> list[dict]:
    out = []
    for start in range(0, len(premises), BATCH):
        enc = tokenizer(premises[start:start + BATCH], hypotheses[start:start + BATCH],
                        truncation=True, max_length=MAX_LENGTH, padding=True,
                        return_tensors="pt").to(device)
        with torch.no_grad():
            probs = torch.softmax(model(**enc).logits, dim=-1).cpu().numpy()
        for row in probs:
            s = {id2label[i]: float(v) for i, v in enumerate(row)}
            out.append({"label": max(s, key=s.get), "entailment": s["entailment"]})
    return out


def metrics(pred: list[str], gold: list[str]) -> dict:
    tp = sum(p == "unsupported" and g == "unsupported" for p, g in zip(pred, gold))
    fp = sum(p == "unsupported" and g == "supported" for p, g in zip(pred, gold))
    fn = sum(p == "supported" and g == "unsupported" for p, g in zip(pred, gold))
    tn = sum(p == "supported" and g == "supported" for p, g in zip(pred, gold))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "false_alarm_rate": round(fp / (fp + tn), 4) if fp + tn else 0.0,
            "accuracy": round((tp + tn) / len(gold), 4)}


def main() -> None:
    rows = [json.loads(l) for l in (BUILD / "ragbench_tr_medical_claims.jsonl").open(encoding="utf-8")]
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    id2label = {i: l.lower() for i, l in model.config.id2label.items()}
    run = lambda p, h: scores_for(model, tokenizer, device, id2label, p, h)

    full = run([r["context"] for r in rows], [r["claim"] for r in rows])

    flat_p, flat_h, owner = [], [], []
    for i, r in enumerate(rows):
        for w in r["context_windows"]:
            flat_p.append(w)
            flat_h.append(r["claim"])
            owner.append(i)
    raw = run(flat_p, flat_h)
    per_claim: list[list[dict]] = [[] for _ in rows]
    for i, out in zip(owner, raw):
        per_claim[i].append(out)
    windowed = [max(outs, key=lambda o: (-ORDER[o["label"]], o["entailment"])) for outs in per_claim]

    gold = [r["gold_binary"] for r in rows]
    to_binary = lambda outs: ["supported" if o["label"] == "entailment" else "unsupported" for o in outs]
    pred_a, pred_b = to_binary(full), to_binary(windowed)
    truncated = sum(len(tokenizer(r["context"], r["claim"])["input_ids"]) > MAX_LENGTH for r in rows)

    result = {
        "model": MODEL_ID, "device": device, "n_claims": len(rows),
        "gold": {"unsupported": gold.count("unsupported"), "supported": gold.count("supported")},
        "truncated_full_contexts": truncated,
        "A_full_context_truncated": metrics(pred_a, gold),
        "B_per_document_windows": metrics(pred_b, gold),
        "verdict_changed": sum(a != b for a, b in zip(pred_a, pred_b)),
        "changed_toward_gold": sum(a != b and b == g for a, b, g in zip(pred_a, pred_b, gold)),
        "changed_away_from_gold": sum(a != b and a == g for a, b, g in zip(pred_a, pred_b, gold)),
        "note": "NLI verdicts without the Gemma atomiser; not final K2 claim labels. "
                "Silver labels (GPT-4); binary scoring on the unsupported class.",
    }
    # Where the two disagree, is the claim one of the soft 'general' support rows?
    labels = {r["example_id"]: r for r in
              (json.loads(l) for l in (BUILD / "ragbench_tr_medical_labels.jsonl").open(encoding="utf-8"))}
    changed = [r["example_id"] for r, a, b in zip(rows, pred_a, pred_b) if a != b]
    result["changed_rows_with_special_support"] = sum(
        bool(labels[e]["special_support_values"]) for e in changed)
    result["changed_examples"] = changed[:40]

    (BUILD / "window_compare.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "changed_examples"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
