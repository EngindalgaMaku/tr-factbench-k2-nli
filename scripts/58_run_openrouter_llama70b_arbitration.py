#!/usr/bin/env python3
"""
58_run_openrouter_llama70b_arbitration.py
Runs true live LLM arbitration on the 120 disagreement cases using
Llama-3.3-70B-Instruct via OpenRouter API.
Evaluates:
  1. Component 3 Judge performance on 120 disagreement cases.
  2. Full End-to-End Hybrid Pipeline performance on all 478 held-out Gold test cases.
  3. Paired statistical significance (McNemar test) against K1, K2, and Gemma-2B.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import requests
from dotenv import load_dotenv

# Ensure k2_nli package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from k2_nli.labels import CLAIM_LABELS
from k2_nli.metrics import evaluate_predictions

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "meta-llama/llama-3.3-70b-instruct"


def hard_label_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    probabilities = np.zeros((len(y_true), len(CLAIM_LABELS)), dtype=float)
    for row, label in enumerate(y_pred):
        if label in CLAIM_LABELS:
            probabilities[row, CLAIM_LABELS.index(label)] = 1.0
    metrics = evaluate_predictions(y_true, y_pred, probabilities, CLAIM_LABELS)
    for name in ("nll", "multiclass_brier", "ece"):
        metrics.pop(name, None)
    return metrics


def calculate_mcnemar(y_true: list[str], y_pred_a: list[str], y_pred_b: list[str]) -> dict[str, Any]:
    """Calculate exact / continuity-corrected McNemar test between Model A and Model B."""
    from scipy.stats import binomtest
    b = 0  # A correct, B wrong
    c = 0  # A wrong, B correct
    for yt, ya, yb in zip(y_true, y_pred_a, y_pred_b):
        a_corr = (ya == yt)
        b_corr = (yb == yt)
        if a_corr and not b_corr:
            b += 1
        elif not a_corr and b_corr:
            c += 1

    total_discordant = b + c
    if total_discordant == 0:
        return {"b": b, "c": c, "p_value": 1.0, "significant_005": False}

    # Two-sided exact binomial test on discordant pairs
    res = binomtest(b, n=total_discordant, p=0.5, alternative="two-sided")
    p_val = float(res.pvalue)

    # Chi-square with Edwards continuity correction
    chi2 = (abs(b - c) - 1.0) ** 2 / total_discordant if total_discordant > 0 else 0.0

    return {
        "b_model_a_only": b,
        "c_model_b_only": c,
        "total_discordant": total_discordant,
        "chi2_continuity": chi2,
        "p_value_exact": p_val,
        "significant_005": p_val < 0.05,
    }


def build_prompt(case: dict[str, Any]) -> str:
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


def parse_judge_output(raw_text: str) -> dict[str, Any]:
    cleaned = raw_text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    json_str = match.group(1) if match else cleaned

    start = json_str.find("{")
    end = json_str.rfind("}")
    if start >= 0 and end > start:
        json_str = json_str[start : end + 1]

    try:
        data = json.loads(json_str)
        decision = str(data.get("final_decision", "")).strip().lower()
        if decision not in CLAIM_LABELS:
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


def call_openrouter(
    prompt: str,
    api_key: str,
    max_retries: int = 5,
    backoff_factor: float = 2.0,
) -> tuple[dict[str, Any], float]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
        "X-OpenRouter-Title": "TR-FactBench Hybrid Arbitration Judge",
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 300,
        "stream": False,
    }

    t0 = time.time()
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=90)
            if resp.status_code == 200:
                elapsed = time.time() - t0
                return resp.json(), elapsed
            elif resp.status_code in (429, 500, 502, 503, 504):
                sleep_s = backoff_factor ** attempt
                print(f"[OpenRouter HTTP {resp.status_code}] Retrying in {sleep_s:.1f}s (Attempt {attempt}/{max_retries})...")
                time.sleep(sleep_s)
            else:
                resp.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries:
                raise RuntimeError(f"OpenRouter failed after {max_retries} attempts: {e}") from e
            sleep_s = backoff_factor ** attempt
            print(f"[Request Error: {e}] Retrying in {sleep_s:.1f}s...")
            time.sleep(sleep_s)

    raise RuntimeError("OpenRouter unexpected termination")


def main() -> None:
    # 1. Load API key
    env_paths = [
        Path("tr-factbench-v0.1.0-preview/.env"),
        Path("../tr-factbench-v0.1.0-preview/.env"),
        Path(".env"),
        Path("../.env"),
    ]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(ep)
            break

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY could not be found in environment or .env files!")

    print(f"Loaded OpenRouter API Key (prefix: {api_key[:12]}...)")
    print(f"Target Judge Model: {MODEL_ID}")

    # 2. Load cases
    cases_path = Path("k2_nli/data/processed/arbitration/arbitration_cases_120.jsonl")
    if not cases_path.exists():
        cases_path = Path("data/processed/arbitration/arbitration_cases_120.jsonl")
    if not cases_path.exists():
        raise FileNotFoundError(f"Cases not found: {cases_path}")

    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(cases)} arbitration disagreement cases.")

    out_dir = Path("k2_nli/reports/experiments/K3-LIVE-LLAMA70B-ARBITRATION-v1")
    if not out_dir.parent.parent.exists():
        out_dir = Path("reports/experiments/K3-LIVE-LLAMA70B-ARBITRATION-v1")
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_file = out_dir / "arbitration_predictions_120.jsonl"
    raw_resp_file = out_dir / "raw_responses_120.jsonl"

    # Check for existing completed records to allow resuming
    existing_preds: dict[str, dict[str, Any]] = {}
    if pred_file.exists():
        for line in pred_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                existing_preds[item["example_id"]] = item
        if existing_preds:
            print(f"Resuming run: Found {len(existing_preds)} already completed arbitration cases.")

    results: list[dict[str, Any]] = []
    correct_count = 0
    total_tokens_prompt = 0
    total_tokens_completion = 0
    t_start = time.time()

    print("\nStarting OpenRouter Llama-3.3-70B Arbitration Loop...")
    for idx, case in enumerate(cases, 1):
        eid = case["example_id"]
        gold = case["gold_label"]

        if eid in existing_preds:
            rec = existing_preds[eid]
            results.append(rec)
            if rec["judge_correct"]:
                correct_count += 1
            continue

        prompt = build_prompt(case)
        resp_json, lat = call_openrouter(prompt, api_key)

        usage = resp_json.get("usage", {})
        p_tokens = usage.get("prompt_tokens", 0)
        c_tokens = usage.get("completion_tokens", 0)
        total_tokens_prompt += p_tokens
        total_tokens_completion += c_tokens

        choice = resp_json.get("choices", [{}])[0]
        raw_output = choice.get("message", {}).get("content", "").strip()

        parsed = parse_judge_output(raw_output)
        is_corr = (parsed["final_decision"] == gold)
        if is_corr:
            correct_count += 1

        rec = {
            "example_id": eid,
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
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "latency_seconds": round(lat, 3),
            "raw_output": raw_output,
        }
        results.append(rec)

        # Progressively save
        with open(pred_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        with open(raw_resp_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"example_id": eid, "response": resp_json}, ensure_ascii=False) + "\n")

        acc_so_far = correct_count / len(results) * 100
        elapsed = time.time() - t_start
        print(f"[{len(results):3d}/{len(cases)}] Judge Decision: {parsed['final_decision']:<19} | Gold: {gold:<19} | Favors: {parsed['favored_model']:<8} | Acc: {acc_so_far:.1f}% ({correct_count}/{len(results)}) | Lat: {lat:.2f}s", flush=True)

        # Respect API rate limits gracefully
        time.sleep(0.15)

    print("\nArbitration phase on 120 disagreements finished!")
    disagree_metrics = hard_label_metrics(
        [r["gold_label"] for r in results],
        [r["judge_decision"] for r in results],
    )

    # 3. Load 358 consensus cases to assemble Full 478 End-to-End Hybrid
    k1_candidates = [
        Path("tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl"),
        Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl"),
    ]
    k1_path = next(p for p in k1_candidates if p.exists())
    k1_rows = [json.loads(line) for line in k1_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    k1_map = {r["release_example_id"]: r for r in k1_rows}

    k2_candidates = [
        Path("k2_nli/reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl"),
        Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl"),
    ]
    k2_path = next(p for p in k2_candidates if p.exists())
    k2_rows = [json.loads(line) for line in k2_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    k2_map = {r["example_id"]: r for r in k2_rows}

    judge_map = {r["example_id"]: r for r in results}

    y_true_all: list[str] = []
    y_k1_all: list[str] = []
    y_k2_all: list[str] = []
    y_hybrid_all: list[str] = []
    hybrid_full_records: list[dict[str, Any]] = []

    for eid, k1 in k1_map.items():
        if eid not in k2_map:
            continue
        k2 = k2_map[eid]
        gold = k1["gold_label"]
        y_true_all.append(gold)
        y_k1_all.append(k1["predicted_label"])
        y_k2_all.append(k2["pred_label"])

        if k1["predicted_label"] == k2["pred_label"]:
            final_p = k1["predicted_label"]
            source = "consensus"
            reasoning = "K1 ve K2 modelleri doğrudan tam uzlaşmaya varmıştır."
            favored = "Consensus"
        else:
            j_rec = judge_map[eid]
            final_p = j_rec["judge_decision"]
            source = "llama70b_judge"
            reasoning = j_rec["reasoning"]
            favored = j_rec["favored_model"]

        y_hybrid_all.append(final_p)
        hybrid_full_records.append({
            "example_id": eid,
            "gold_label": gold,
            "k1_pred": k1["predicted_label"],
            "k2_pred": k2["pred_label"],
            "pred_label": final_p,
            "source": source,
            "favored_model": favored,
            "reasoning": reasoning,
            "is_correct": final_p == gold,
        })

    # Save full 478 hybrid predictions
    with open(out_dir / "hybrid_full_predictions_478.jsonl", "w", encoding="utf-8") as f:
        for r in hybrid_full_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    hybrid_metrics = hard_label_metrics(y_true_all, y_hybrid_all)
    k1_metrics = hard_label_metrics(y_true_all, y_k1_all)
    k2_metrics = hard_label_metrics(y_true_all, y_k2_all)

    # Statistical significance: McNemar test
    mcnemar_vs_k1 = calculate_mcnemar(y_true_all, y_hybrid_all, y_k1_all)
    mcnemar_vs_k2 = calculate_mcnemar(y_true_all, y_hybrid_all, y_k2_all)

    # Load Gemma-2B results for comparison if available
    gemma_metrics_path = Path("reports/experiments/K3-LIVE-GEMMA-ARBITRATION-v1/hybrid_full_predictions_478.jsonl")
    if not gemma_metrics_path.exists():
        gemma_metrics_path = Path("k2_nli/reports/experiments/K3-LIVE-GEMMA-ARBITRATION-v1/hybrid_full_predictions_478.jsonl")

    mcnemar_vs_gemma = {}
    gemma_metrics = None
    if gemma_metrics_path.exists():
        gemma_rows = [json.loads(line) for line in gemma_metrics_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        gemma_by_id = {r["example_id"]: r["pred_label"] for r in gemma_rows}
        hyb_ids = [r["example_id"] for r in hybrid_full_records]
        if all(e in gemma_by_id for e in hyb_ids):
            y_gemma_all = [gemma_by_id[e] for e in hyb_ids]  # aligned strictly by example_id
            mcnemar_vs_gemma = calculate_mcnemar(y_true_all, y_hybrid_all, y_gemma_all)
            gemma_metrics = hard_label_metrics(y_true_all, y_gemma_all)

    # Breakdown of favored models
    favored_counts = {
        "Model A": sum(1 for r in results if r["favored_model"] == "Model A"),
        "Model B": sum(1 for r in results if r["favored_model"] == "Model B"),
        "Neither": sum(1 for r in results if r["favored_model"] in ("Neither", "Unknown")),
    }

    total_tokens_prompt = sum(r.get("prompt_tokens", 0) for r in results)
    total_tokens_completion = sum(r.get("completion_tokens", 0) for r in results)
    total_latency_seconds = sum(r.get("latency_seconds", 0) for r in results)
    # Actual billed cost as reported by OpenRouter in usage.cost (no assumed price table)
    actual_cost = 0.0
    if raw_resp_file.exists():
        for line in raw_resp_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                actual_cost += float((json.loads(line)["response"].get("usage") or {}).get("cost", 0) or 0)

    consensus_records = [r for r in hybrid_full_records if r["source"] == "consensus"]
    consensus_correct = sum(1 for r in consensus_records if r["is_correct"])

    summary = {
        "experiment_id": "K3-LIVE-LLAMA70B-ARBITRATION-v1",
        "judge_model": MODEL_ID,
        "n_arbitration_cases": len(cases),
        "judge_correct_count": correct_count,
        "judge_disagreement_accuracy": round(disagree_metrics["accuracy"], 4),
        "judge_disagreement_macro_f1": round(disagree_metrics["macro_f1"], 4),
        "json_valid_count": sum(1 for r in results if r["json_valid"]),
        "favored_model_distribution": favored_counts,
        "consensus_cases_count": len(consensus_records),
        "consensus_correct": consensus_correct,
        "consensus_accuracy": round(consensus_correct / len(consensus_records), 4),
        "hybrid_end_to_end": {
            "total_examples": len(y_true_all),
            "correct_examples": sum(1 for r in hybrid_full_records if r["is_correct"]),
            "accuracy": round(hybrid_metrics["accuracy"], 4),
            "macro_recall": round(hybrid_metrics["classification_report"]["macro avg"]["recall"], 4),
            "macro_precision": round(hybrid_metrics["classification_report"]["macro avg"]["precision"], 4),
            "macro_f1": round(hybrid_metrics["macro_f1"], 4),
            "mcc": round(hybrid_metrics["mcc"], 4),
            "confusion_matrix": hybrid_metrics.get("confusion_matrix", []),
        },
        "baselines_comparison": {
            "k1_electra_macro_f1": round(k1_metrics["macro_f1"], 4),
            "k1_electra_accuracy": round(k1_metrics["accuracy"], 4),
            "k1_electra_mcc": round(k1_metrics["mcc"], 4),
            "k2_soft_macro_f1": round(k2_metrics["macro_f1"], 4),
            "k2_soft_accuracy": round(k2_metrics["accuracy"], 4),
            "k2_soft_mcc": round(k2_metrics["mcc"], 4),
            "gemma_2b_hybrid_acc": round(gemma_metrics["accuracy"], 4) if gemma_metrics else None,
            "gemma_2b_hybrid_macro_f1": round(gemma_metrics["macro_f1"], 4) if gemma_metrics else None,
            "gemma_2b_hybrid_mcc": round(gemma_metrics["mcc"], 4) if gemma_metrics else None,
        },
        "mcnemar_tests": {
            "hybrid_vs_k1": mcnemar_vs_k1,
            "hybrid_vs_k2": mcnemar_vs_k2,
            "hybrid_vs_gemma_2b": mcnemar_vs_gemma,
        },
        "total_tokens_prompt": total_tokens_prompt,
        "total_tokens_completion": total_tokens_completion,
        "actual_cost_usd_openrouter": round(actual_cost, 6),
        "total_inference_seconds": round(total_latency_seconds, 2),
        "avg_latency_per_case_seconds": round(total_latency_seconds / len(cases), 2),
    }

    with open(out_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    gm = summary["baselines_comparison"]
    gemma_row = (
        f"| Hibrit + Gemma-4-E2B-it (bilgilendirilmiş meta-hakem, yerel) | %{gm['gemma_2b_hybrid_acc']*100:.2f} | "
        f"{gm['gemma_2b_hybrid_macro_f1']:.4f} | {gm['gemma_2b_hybrid_mcc']:.4f} | K1/K2 kararlarını gören 2B hakem |"
        if gm["gemma_2b_hybrid_acc"] is not None else "| Hibrit + Gemma-4-E2B-it | - | - | - | dosya bulunamadı |"
    )
    n_all = len(y_true_all)
    oracle_correct = consensus_correct + sum(1 for r in results if r["k1_correct"] or r["k2_correct"])
    report_md = f"""# K3-LIVE-LLAMA70B-ARBITRATION-v1 Raporu

**Model:** `{MODEL_ID}` (OpenRouter API, temperature=0)  
**Tasarım:** Bilgilendirilmiş meta-hakem (hakem K1 ve K2 kararlarını + K2 atom NLI dökümünü görür)  
**Tarih:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Veri Kümesi:** TR-FactBench Gold 480 ({n_all} geçerli test örneği; 2 örnek atomizer hatası nedeniyle dışarıda)  

---

## 1. Hakem Başarımı (120 Ayrışma Örneğinde)

- **Doğru Karar:** {correct_count} / {len(cases)} (**%{disagree_metrics['accuracy']*100:.2f}**)
- **Hakem Macro-F1:** {disagree_metrics['macro_f1']:.4f}
- **Geçerli JSON:** {summary['json_valid_count']} / {len(cases)}
- **Beyan edilen `favored_model` dağılımı:** Model A (K1): {favored_counts['Model A']}, Model B (K2): {favored_counts['Model B']}, Neither/Unknown: {favored_counts['Neither']}

---

## 2. Uçtan Uca Hibrit Sistem Başarımı ({n_all} Örnek)

| Model / Sistem | Doğruluk | Macro-F1 | MCC | Açıklama |
|---|---|---|---|---|
| K1 (ELECTRA-TR) | %{k1_metrics['accuracy']*100:.2f} | {k1_metrics['macro_f1']:.4f} | {k1_metrics['mcc']:.4f} | Bütüncül sınıflandırıcı |
| K2 (Gemma-4 atomizer + mDeBERTa, soft-prob) | %{k2_metrics['accuracy']*100:.2f} | {k2_metrics['macro_f1']:.4f} | {k2_metrics['mcc']:.4f} | Atomik NLI |
{gemma_row}
| **Hibrit + Llama-3.3-70B (bilgilendirilmiş meta-hakem)** | **%{hybrid_metrics['accuracy']*100:.2f} ({summary['hybrid_end_to_end']['correct_examples']}/{n_all})** | **{hybrid_metrics['macro_f1']:.4f}** | **{hybrid_metrics['mcc']:.4f}** | 70B hakem |
| *Oracle tavanı* | *%{oracle_correct/n_all*100:.2f} ({oracle_correct}/{n_all})* | - | - | K1 veya K2 doğruysa doğru sayılır |

---

## 3. İstatistiksel Anlamlılık (Exact McNemar, örnek kimliğine göre eşlenmiş)

| Karşılaştırma | Yalnız Hibrit doğru | Yalnız karşı taraf doğru | p (exact) |
|---|---:|---:|---:|
| Hibrit vs K1 | {mcnemar_vs_k1.get('b_model_a_only', 0)} | {mcnemar_vs_k1.get('c_model_b_only', 0)} | {mcnemar_vs_k1.get('p_value_exact', 1.0):.4f} |
| Hibrit vs K2 | {mcnemar_vs_k2.get('b_model_a_only', 0)} | {mcnemar_vs_k2.get('c_model_b_only', 0)} | {mcnemar_vs_k2.get('p_value_exact', 1.0):.4f} |
| Hibrit(Llama-70B) vs Hibrit(Gemma-E2B) | {mcnemar_vs_gemma.get('b_model_a_only', 0)} | {mcnemar_vs_gemma.get('c_model_b_only', 0)} | {mcnemar_vs_gemma.get('p_value_exact', 1.0):.4f} |

---

## 4. Kaynak ve Maliyet

- Prompt token: {total_tokens_prompt:,} | Tamamlama token: {total_tokens_completion:,}
- **Gerçek faturalanan maliyet (OpenRouter `usage.cost`):** ${summary['actual_cost_usd_openrouter']:.4f} USD
- Toplam istek süresi: {summary['total_inference_seconds']} sn (ortalama {summary['avg_latency_per_case_seconds']} sn/örnek)

---

## 5. Yorum (bkz. `reports/experiments/AUDIT-K2-K3-v1/README.md`)

Bu bilgilendirilmiş meta-hakem tasarımı, aynı 120 örnekte **kör (blind) LLM hakem** tasarımının
(resmi TR-FactBench sistem istemi + 8-shot) gerisinde kalmıştır. Ana hata kaynağı, hakemin
`contradicted` etiketini aşırı üretmesidir (gold kısmi-destek örneklerinin çoğu `contradicted`
olarak etiketlenmiştir). Bu desen aynı modelin kör zero-shot çıktısında da görüldüğünden, düşüşün
temel nedeni K1/K2 bilgisinin gösterilmesinden çok, zero-shot ayarı ve istemdeki etiket tanımlarının
resmi tanımlardan sapmasıdır.
"""

    with open(out_dir / "REPORT_K3_LIVE_LLAMA70B.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n" + "=" * 70)
    print("LIVE LLAMA-3.3-70B ARBITRATION EXPERIMENT COMPLETED!")
    print(f"Judge Accuracy in Disagreements: {disagree_metrics['accuracy']*100:.2f}% ({correct_count}/{len(cases)})")
    print(f"End-to-End Hybrid Accuracy: {hybrid_metrics['accuracy']*100:.2f}% ({sum(r['is_correct'] for r in hybrid_full_records)}/{len(y_true_all)})")
    print(f"End-to-End Hybrid Macro-F1: {hybrid_metrics['macro_f1']:.4f}")
    print(f"End-to-End Hybrid MCC: {hybrid_metrics['mcc']:.4f}")
    print(f"Report saved to: {out_dir / 'REPORT_K3_LIVE_LLAMA70B.md'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
