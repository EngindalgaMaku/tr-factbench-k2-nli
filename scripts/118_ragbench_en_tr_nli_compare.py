#!/usr/bin/env python3
"""
118_ragbench_en_tr_nli_compare.py
Translation-effect check on the RAGBench medical slice: the frozen K2 NLI model
(mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) is run on the ORIGINAL ENGLISH and on
the TURKISH translation under identical conditions, so any gap is due to language /
translation, not to pipeline differences.

Identical conditions for both languages:
  - same 809 response sentences (the 74 translated questions; PMQ-053 excluded in both),
  - same RAGBench silver labels (keys normalised, K-015),
  - hypothesis = the response sentence itself (no Gemma atomiser: it is trained on
    Turkish, so English atoms would not be comparable),
  - premise = each source document as its own window (K-017), strongest support kept.

Reported per language: binary metrics on the unsupported class (entailment -> supported)
and AUROC with score = 1 - max entailment probability over windows (higher = more
likely unsupported), the threshold-free metric RAGBench reports.

Output: data/ragbench/medical/build/en_tr_nli_compare.json, en_tr_nli_scores.jsonl (per sentence)
"""
from __future__ import annotations

import json
from pathlib import Path

import torch
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
MED = ROOT / "data" / "ragbench" / "medical"
BUILD = MED / "build"
MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
MAX_LENGTH = 512
BATCH = 16
SHORT = {"claude-3-haiku-20240307": "claude3haiku", "gpt-3.5-turbo-0125": "gpt35turbo"}


def english_rows(example_ids: set[str]) -> dict[str, dict]:
    rows = {}
    for line in (MED / "pmq75_source_en.jsonl").open(encoding="utf-8"):
        item = json.loads(line)
        docs: dict[str, list[str]] = {}
        for doc in item["documents"]:
            for s in doc:
                docs.setdefault(s["key"][0], []).append(s["en"])
        windows = [" ".join(v) for v in docs.values()]
        for model, sents in item["responses"].items():
            for s in sents:
                eid = f"{item['item_id']}__{SHORT[model]}__{s['key']}"
                if eid in example_ids:
                    rows[eid] = {"claim": s["en"], "windows": windows}
    return rows


def main() -> None:
    tr_rows = {json.loads(l)["example_id"]: json.loads(l)
               for l in (BUILD / "ragbench_tr_medical_claims.jsonl").open(encoding="utf-8")}
    gold = {eid: r["gold_binary"] for eid, r in tr_rows.items()}
    en_rows = english_rows(set(tr_rows))
    missing = set(tr_rows) - set(en_rows)
    if missing:
        raise SystemExit(f"English rows missing for {len(missing)} ids, e.g. {sorted(missing)[:3]}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    id2label = {i: l.lower() for i, l in model.config.id2label.items()}
    ent = [i for i, l in id2label.items() if l == "entailment"][0]

    def run(language: str, data: dict[str, dict]) -> dict:
        ids = sorted(data)
        prem, hyp, owner = [], [], []
        for eid in ids:
            for w in data[eid]["windows"]:
                prem.append(w)
                hyp.append(data[eid]["claim"])
                owner.append(eid)
        best = {eid: {"p_ent": 0.0, "label": "neutral"} for eid in ids}
        truncated = 0
        for start in range(0, len(prem), BATCH):
            p, h = prem[start:start + BATCH], hyp[start:start + BATCH]
            truncated += sum(len(tokenizer(a, b)["input_ids"]) > MAX_LENGTH for a, b in zip(p, h))
            enc = tokenizer(p, h, truncation="only_first", max_length=MAX_LENGTH,
                            padding=True, return_tensors="pt").to(device)
            with torch.no_grad():
                probs = torch.softmax(model(**enc).logits, dim=-1).cpu().numpy()
            for eid, row in zip(owner[start:start + BATCH], probs):
                label = id2label[int(row.argmax())]
                if row[ent] > best[eid]["p_ent"]:
                    best[eid]["p_ent"] = float(row[ent])
                if label == "entailment":
                    best[eid]["label"] = "entailment"
        y = [1 if gold[e] == "unsupported" else 0 for e in ids]
        pred = [0 if best[e]["label"] == "entailment" else 1 for e in ids]
        tp = sum(a and b for a, b in zip(pred, y)); fp = sum(a and not b for a, b in zip(pred, y))
        fn = sum((not a) and b for a, b in zip(pred, y)); tn = len(y) - tp - fp - fn
        P = tp / (tp + fp) if tp + fp else 0.0
        R = tp / (tp + fn) if tp + fn else 0.0
        return {"language": language, "n": len(ids), "truncated_pairs": truncated,
                "f1": round(2 * P * R / (P + R), 4) if P + R else 0.0,
                "precision": round(P, 4), "recall": round(R, 4),
                "false_alarm_rate": round(fp / (fp + tn), 4), "accuracy": round((tp + tn) / len(y), 4),
                "auroc": round(roc_auc_score(y, [1 - best[e]["p_ent"] for e in ids]), 4),
                "predicted_unsupported": sum(pred),
                "_pred": dict(zip(ids, pred)),
                "_score": {e: 1 - best[e]["p_ent"] for e in ids}}

    en = run("en", en_rows)
    tr = run("tr", {eid: {"claim": r["claim"], "windows": r["context_windows"]} for eid, r in tr_rows.items()})
    agree = sum(en["_pred"][e] == tr["_pred"][e] for e in tr_rows)
    result = {
        "model": MODEL_ID, "setup": "claim as hypothesis, per-document windows, no atomiser, silver labels",
        "gold": {"unsupported": sum(v == "unsupported" for v in gold.values()), "n": len(gold)},
        "trivial_all_unsupported_f1": round(2 * (sum(v == "unsupported" for v in gold.values()) / len(gold))
                                            / (1 + sum(v == "unsupported" for v in gold.values()) / len(gold)), 4),
        "english": {k: v for k, v in en.items() if not k.startswith("_")},
        "turkish": {k: v for k, v in tr.items() if not k.startswith("_")},
        "same_binary_decision_en_vs_tr": f"{agree}/{len(tr_rows)}",
        "reference": "RAGBench (Friel et al. 2024) Table 3, PubMedQA, English, AUROC: fine-tuned DeBERTa 0.80, "
                     "TruLens 0.62, RAGAS 0.54, GPT-3.5 judge 0.51 (full test split; not the same subset)",
    }
    # Per-sentence scores for the bootstrap (scripts/119): score = 1 - max entailment probability.
    with (BUILD / "en_tr_nli_scores.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for e in sorted(tr_rows):
            f.write(json.dumps({"example_id": e, "question_id": tr_rows[e]["question_id"], "gold": gold[e],
                                "en_pred_unsupported": en["_pred"][e], "tr_pred_unsupported": tr["_pred"][e],
                                "en_score": round(en["_score"][e], 6), "tr_score": round(tr["_score"][e], 6)}) + "\n")
    (BUILD / "en_tr_nli_compare.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
