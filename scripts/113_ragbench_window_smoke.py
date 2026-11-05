#!/usr/bin/env python3
"""
113_ragbench_window_smoke.py
Smoke test for the open decision K-017: does per-document windowing change K2's
NLI verdict compared with feeding the full (truncated) context?

It runs the frozen K2 NLI model on a small sample of claims twice:
  A) premise = full context, truncated at max_length (what happens today)
  B) premise = each source document separately, keeping the strongest support
     (entailment > neutral > contradiction, by entailment probability)
and prints both verdicts next to RAGBench's silver label.

This isolates the windowing question: it feeds the claim sentence directly as the
hypothesis and skips the Gemma atomiser, so the labels here are NLI verdicts, not
full K2 claim labels. Nothing is written to runs/.

Usage: python scripts/113_ragbench_window_smoke.py [--n 10] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
CLAIMS = ROOT / "data" / "ragbench" / "medical" / "build" / "ragbench_tr_medical_claims.jsonl"
MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"   # frozen K2 model
MAX_LENGTH = 512
ORDER = {"entailment": 0, "neutral": 1, "contradiction": 2}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--batch-size", type=int, default=8)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rows = [json.loads(l) for l in CLAIMS.open(encoding="utf-8")]
    rng = np.random.default_rng(args.seed)
    # Half unsupported, half supported, so both error directions are visible.
    unsupported = [r for r in rows if r["gold_binary"] == "unsupported"]
    supported = [r for r in rows if r["gold_binary"] == "supported"]
    half = args.n // 2
    pick = [unsupported[i] for i in rng.choice(len(unsupported), half, replace=False)]
    pick += [supported[i] for i in rng.choice(len(supported), args.n - half, replace=False)]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    id2label = {i: l.lower() for i, l in model.config.id2label.items()}

    def infer(premises: list[str], hypotheses: list[str]) -> list[dict]:
        out = []
        for start in range(0, len(premises), args.batch_size):
            enc = tokenizer(premises[start:start + args.batch_size],
                            hypotheses[start:start + args.batch_size],
                            truncation=True, max_length=MAX_LENGTH,
                            padding=True, return_tensors="pt").to(device)
            with torch.no_grad():
                probs = torch.softmax(model(**enc).logits, dim=-1).cpu().numpy()
            for row in probs:
                scores = {id2label[i]: float(v) for i, v in enumerate(row)}
                out.append({"label": max(scores, key=scores.get), "scores": scores})
        return out

    full = infer([r["context"] for r in pick], [r["claim"] for r in pick])

    flat_p, flat_h, owner = [], [], []
    for i, r in enumerate(pick):
        for w in r["context_windows"]:
            flat_p.append(w)
            flat_h.append(r["claim"])
            owner.append(i)
    win_raw = infer(flat_p, flat_h)
    per_claim: list[list[dict]] = [[] for _ in pick]
    for i, out in zip(owner, win_raw):
        per_claim[i].append(out)
    windowed = [max(outs, key=lambda o: (-ORDER[o["label"]], o["scores"]["entailment"]))
                for outs in per_claim]

    truncated = sum(len(tokenizer(r["context"], r["claim"])["input_ids"]) > MAX_LENGTH for r in pick)
    print(f"model: {MODEL_ID}  | cihaz: {device} | örneklem: {len(pick)} "
          f"(kesilen tam bağlam: {truncated})\n")
    header = f"{'örnek':28} {'gerçek':12} {'A tam bağlam':16} {'B pencereleme':16} fark"
    print(header + "\n" + "-" * len(header))
    changed = 0
    for r, a, b in zip(pick, full, windowed):
        diff = "" if a["label"] == b["label"] else "DEĞİŞTİ"
        changed += bool(diff)
        print(f"{r['example_id']:28} {r['gold_binary']:12} "
              f"{a['label'] + f' {a['scores']['entailment']:.2f}':16} "
              f"{b['label'] + f' {b['scores']['entailment']:.2f}':16} {diff}")
    agree = lambda outs: sum(
        (o["label"] == "entailment") == (r["gold_binary"] == "supported")
        for o, r in zip(outs, pick))
    print(f"\nNLI kararı değişen satır: {changed}/{len(pick)}")
    print(f"entailment=destekleniyor varsayımıyla gerçek etiketle uyum — "
          f"A: {agree(full)}/{len(pick)}, B: {agree(windowed)}/{len(pick)}")
    print("\nNot: bu test Gemma atomlaştırıcısını atlar; çıktılar K2'nin nihai iddia etiketi değil, NLI kararıdır.")


if __name__ == "__main__":
    main()
