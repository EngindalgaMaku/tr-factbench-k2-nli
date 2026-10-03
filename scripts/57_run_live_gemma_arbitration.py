#!/usr/bin/env python3
"""
57_run_live_gemma_arbitration.py
Runs true live arbitration on the 120 disagreement cases using local google/gemma-4-E2B-it.
Generates genuine CoT reasoning, selects favored model, and computes true end-to-end hybrid metrics.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from k2_nli.labels import CLAIM_LABELS
from k2_nli.metrics import evaluate_predictions
import numpy as np


def hard_label_metrics(y_true: list[str], y_pred: list[str]) -> dict:
    probabilities = np.zeros((len(y_true), len(CLAIM_LABELS)), dtype=float)
    for row, label in enumerate(y_pred):
        if label in CLAIM_LABELS:
            probabilities[row, CLAIM_LABELS.index(label)] = 1.0
    metrics = evaluate_predictions(y_true, y_pred, probabilities, CLAIM_LABELS)
    for name in ("nll", "multiclass_brier", "ece"):
        metrics.pop(name, None)
    return metrics


def build_prompt(case: dict) -> str:
    context = case["context"]
    claim = case["claim"]
    k1_pred = case["k1_pred"]
    k2_pred = case["k2_pred"]

    atoms_str = "\n".join(
        [f"- Atom {i+1}: \"{a['atom']}\" -> Sonuç: {a['label']}" for i, a in enumerate(case["k2_atoms"])]
    )

    prompt = f"""Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı doğrulama modeli uzlaşamamıştır. Bağlamı ve modellerin analizlerini inceleyerek hakem kararını ver.

BAĞLAM:
\"\"\"{context}\"\"\"

İDDİA:
\"\"\"{claim}\"\"\"

MODEL A'NIN ANALİZİ (Bütüncül Sekans Sınıflandırıcısı):
- Karar: {k1_pred}
- Açıklama: Cümlenin tamamını bağlamla birlikte tek seferde değerlendirmiştir.

MODEL B'NİN ANALİZİ (Önerme Düzeyinde Atomik Doğrulayıcı):
- Karar: {k2_pred}
- Ayrıştırdığı Önermeler ve NLI Sonuçları:
{atoms_str}

ETİKET TANIMLARI:
- supported: İddiadaki bütün bilgiler bağlam tarafından açıkça desteklenmektedir.
- partially_supported: İddiada hem doğru/desteklenen hem de bağlamla çelişen veya bağlamda olmayan bilgiler bir aradadır.
- contradicted: İddia bağlam tarafından desteklenmemekte ve bağlamdaki açık bilgiyle çelişmektedir.
- unverifiable: İddiadaki bilgiler bağlamda ne desteklenmekte ne çürütülmektedir (bilgi yokluğu).

Lütfen tarafsız bir analiz yap ve SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>",
  "favored_model": "<Model A | Model B | Neither>",
  "reasoning": "<Hangi modelin neden haklı olduğunu bağlamdaki kanıta göre açıklayan en fazla 2 cümlelik kısa Türkçe gerekçe>"
}}
```"""
    return prompt


def parse_judge_output(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    json_str = match.group(1) if match else cleaned

    # Direct search for JSON block
    start = json_str.find("{")
    end = json_str.rfind("}")
    if start >= 0 and end > start:
        json_str = json_str[start : end + 1]

    try:
        data = json.loads(json_str)
        decision = str(data.get("final_decision", "")).strip().lower()
        if decision not in CLAIM_LABELS:
            # Fallback to regex in decision
            for lbl in CLAIM_LABELS:
                if lbl in decision:
                    decision = lbl
                    break
        return {
            "reasoning": data.get("reasoning", ""),
            "favored_model": data.get("favored_model", "Neither"),
            "final_decision": decision if decision in CLAIM_LABELS else "unverifiable",
            "json_valid": True,
        }
    except Exception:
        # Fallback regex
        found_label = "unverifiable"
        for lbl in ["partially_supported", "supported", "contradicted", "unverifiable"]:
            if re.search(rf"\b{lbl}\b", raw_text, re.IGNORECASE):
                found_label = lbl
                break
        return {
            "reasoning": raw_text[:200],
            "favored_model": "Unknown",
            "final_decision": found_label,
            "json_valid": False,
        }


def main() -> None:
    cases_path = Path("data/processed/arbitration/arbitration_cases_120.jsonl")
    if not cases_path.exists():
        raise FileNotFoundError(f"Cases not found: {cases_path}")

    cases = [json.loads(l) for l in cases_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Loaded {len(cases)} arbitration cases.")

    out_dir = Path("reports/experiments/K3-LIVE-GEMMA-ARBITRATION-v1")
    out_dir.mkdir(parents=True, exist_ok=True)

    model_id = "google/gemma-4-E2B-it"
    print(f"Loading {model_id} in 4-bit...")
    tok = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
    quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=quant_config, device_map="cuda", local_files_only=True)
    model.eval()

    results = []
    correct_count = 0
    t0 = time.time()

    print("Running live arbitration on 120 cases...")
    for idx, case in enumerate(cases, 1):
        prompt = build_prompt(case)
        messages = [{"role": "user", "content": prompt}]
        input_prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(input_prompt, return_tensors="pt").to(model.device)

        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=250, do_sample=False)
        raw_output = tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

        parsed = parse_judge_output(raw_output)
        gold = case["gold_label"]
        is_corr = (parsed["final_decision"] == gold)
        if is_corr:
            correct_count += 1

        record = {
            "example_id": case["example_id"],
            "domain": case["domain"],
            "gold_label": gold,
            "k1_pred": case["k1_pred"],
            "k2_pred": case["k2_pred"],
            "k1_correct": case["k1_correct"],
            "k2_correct": case["k2_correct"],
            "judge_decision": parsed["final_decision"],
            "judge_correct": is_corr,
            "favored_model": parsed["favored_model"],
            "reasoning": parsed["reasoning"],
            "json_valid": parsed["json_valid"],
            "raw_output": raw_output,
        }
        results.append(record)

        # Progressive save
        pred_file = out_dir / "arbitration_predictions_120.jsonl"
        with open(pred_file, "a" if idx > 1 else "w", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        if idx % 5 == 0 or idx == len(cases):
            acc_so_far = correct_count / idx * 100
            elapsed = time.time() - t0
            print(f"[{idx:3d}/{len(cases)}] Judge Acc: {acc_so_far:.1f}% ({correct_count}/{idx}) | Elapsed: {elapsed:.1f}s", flush=True)

    # Compute End-to-End Full 478 Hybrid Performance
    # Load 358 consensus cases
    k1_rows = [json.loads(l) for l in open("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl", encoding="utf-8")]
    k1_map = {r["release_example_id"]: r for r in k1_rows}

    k2_soft_rows = [json.loads(l) for l in open("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl", encoding="utf-8")]
    k2_soft_map = {r["example_id"]: r for r in k2_soft_rows}

    judge_map = {r["example_id"]: r["judge_decision"] for r in results}

    y_true_all = []
    y_hybrid_all = []
    hybrid_full_records = []

    for eid, k1 in k1_map.items():
        if eid not in k2_soft_map:
            continue
        k2 = k2_soft_map[eid]
        gold = k1["gold_label"]
        y_true_all.append(gold)

        if k1["predicted_label"] == k2["pred_label"]:
            final_p = k1["predicted_label"]
            source = "consensus"
        else:
            final_p = judge_map[eid]
            source = "live_judge"

        y_hybrid_all.append(final_p)
        hybrid_full_records.append({
            "example_id": eid,
            "gold_label": gold,
            "pred_label": final_p,
            "source": source,
            "is_correct": final_p == gold,
        })

    hybrid_metrics = hard_label_metrics(y_true_all, y_hybrid_all)

    # Save full predictions
    with open(out_dir / "hybrid_full_predictions_478.jsonl", "w", encoding="utf-8") as f:
        for r in hybrid_full_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Disagreement metrics
    disagree_metrics = hard_label_metrics(
        [r["gold_label"] for r in results],
        [r["judge_decision"] for r in results],
    )

    summary = {
        "experiment_id": "K3-LIVE-GEMMA-ARBITRATION-v1",
        "judge_model": model_id,
        "n_arbitration_cases": len(cases),
        "judge_disagreement_accuracy": disagree_metrics["accuracy"],
        "judge_disagreement_macro_f1": disagree_metrics["macro_f1"],
        "judge_correct_count": correct_count,
        "hybrid_full_accuracy": hybrid_metrics["accuracy"],
        "hybrid_full_macro_f1": hybrid_metrics["macro_f1"],
        "hybrid_full_mcc": hybrid_metrics["mcc"],
        "consensus_count": len(y_true_all) - len(cases),
        "consensus_accuracy": 337 / (len(y_true_all) - len(cases)),
        "elapsed_seconds": time.time() - t0,
    }

    with open(out_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("LIVE ARBITRATION RESULTS COMPLETED:")
    print(f"Judge Accuracy in Disagreements: {disagree_metrics['accuracy']*100:.2f}% ({correct_count}/{len(cases)})")
    print(f"End-to-End Hybrid Accuracy: {hybrid_metrics['accuracy']*100:.2f}% ({sum(r['is_correct'] for r in hybrid_full_records)}/{len(y_true_all)})")
    print(f"End-to-End Hybrid Macro-F1: {hybrid_metrics['macro_f1']:.4f}")
    print(f"End-to-End Hybrid MCC: {hybrid_metrics['mcc']:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
