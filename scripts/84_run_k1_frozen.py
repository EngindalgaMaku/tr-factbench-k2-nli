#!/usr/bin/env python3
"""
84_run_k1_frozen.py
Runs the frozen K1 verifier (H1_DROP10_S45, ELECTRA-TR LoRA) exactly as in the
Gold-480 evaluation: same adapter, base revision, input format and max_length,
all read from gold_v1.0/verifier_hold/VERIFIER_CONFIG_v1.0.json.

  --reproduce-gold   re-score Gold-480 and require label-identical output to the
                     frozen PREDICTIONS_v1.0.jsonl (proves the frozen K1 is used)
  --input FILE       score any JSONL with example_id/context/question/claim

Output: JSONL with example_id, predicted_label, probabilities.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
HOLD = TFB / "data" / "evaluation" / "gold_v1.0" / "verifier_hold"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def load_k1(cfg: dict, device: str):
    adapter = TFB / cfg["adapter_path_relative"]
    tok = AutoTokenizer.from_pretrained(str(adapter), local_files_only=True)
    base = AutoModelForSequenceClassification.from_pretrained(
        cfg["base_model"], revision=cfg["base_model_revision"], num_labels=len(cfg["label_mapping"]),
        ignore_mismatched_sizes=True)
    model = PeftModel.from_pretrained(base, str(adapter)).to(device).eval()
    return tok, model


def score(rows: list[dict], cfg: dict, tok, model, device: str) -> list[dict]:
    fmt, id2label = cfg["input_format"], {int(k): v for k, v in cfg["label_mapping"].items()}
    out = []
    for r in rows:
        text_a = fmt["text_a"].format(context=r["context"].strip())
        text_b = fmt["text_b"].format(question=r.get("question", "").strip(), claim=r["claim"].strip())
        enc = tok(text_a, text_b, max_length=cfg["max_length"], truncation=True, return_tensors="pt").to(device)
        with torch.no_grad():
            probs = torch.softmax(model(**enc).logits, dim=-1).squeeze(0).cpu().tolist()
        n_tokens = len(tok(text_a, text_b)["input_ids"])
        out.append({"example_id": r["example_id"], "predicted_label": id2label[int(max(range(len(probs)), key=probs.__getitem__))],
                    "probabilities": {id2label[i]: round(p, 6) for i, p in enumerate(probs)},
                    "input_tokens": n_tokens, "truncated": n_tokens > cfg["max_length"]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reproduce-gold", action="store_true")
    ap.add_argument("--input")
    ap.add_argument("--output")
    args = ap.parse_args()

    cfg = json.loads((HOLD / "VERIFIER_CONFIG_v1.0.json").read_text(encoding="utf-8"))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok, model = load_k1(cfg, device)

    if args.reproduce_gold:
        gold = read_jsonl(TFB / "data" / "evaluation" / "gold_v1.0" / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")
        rows = [{"example_id": g["release_example_id"], **g} for g in gold]
        preds = score(rows, cfg, tok, model, device)
        frozen = {r["release_example_id"]: r["predicted_label"] for r in read_jsonl(HOLD / "PREDICTIONS_v1.0.jsonl")}
        diff = [p["example_id"] for p in preds if p["predicted_label"] != frozen[p["example_id"]]]
        print(f"K1 reproduction on Gold-480: {len(preds) - len(diff)}/{len(preds)} labels identical; differing: {diff[:10]}")
        if diff:
            raise SystemExit("K1 reproduction FAILED — not the frozen K1 configuration")
        return

    rows = read_jsonl(Path(args.input))
    preds = score(rows, cfg, tok, model, device)
    with Path(args.output).open("w", encoding="utf-8", newline="\n") as f:
        for p in preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"K1 scored {len(preds)} rows; truncated inputs: {sum(p['truncated'] for p in preds)}")


if __name__ == "__main__":
    main()
