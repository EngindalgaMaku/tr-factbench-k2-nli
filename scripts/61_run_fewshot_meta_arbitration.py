#!/usr/bin/env python3
"""
61_run_fewshot_meta_arbitration.py
Runs Informed Few-Shot Meta-Arbitration on the 120 disagreement cases using
Llama-3.3-70B-Instruct via OpenRouter API.
Integrates 4 real precedent rulings from train split to educate the judge
on taxonomy boundaries (especially partially_supported vs contradicted).
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

# 4 Gold-independent precedent rulings from train split
FEWSHOT_PRECEDENTS = """EMSAL KARARLAR (ÖNCEKİ MAHKEME İÇTİHATLARI):

[EMSAL 1 - İki parçalı doğru iddia]
BAĞLAM: "Alışverişlerde işyeri bir FAST-TR Karekod oluşturabilir. Müşteri bu karekodu mobil bankacılık uygulamasından okutarak FAST ödemesini başlatır."
İDDİA: "Alışverişte müşteri, işyerinin oluşturduğu karekodu mobil uygulamasından okutarak FAST ödemesi başlatabilir."
MODEL A'NIN KARARI: supported
MODEL B'NİN KARARI: supported (Atom 1: "işyeri karekod oluşturabilir" -> entailed, Atom 2: "müşteri ödeme başlatabilir" -> entailed)
HAKEM KARARI:
```json
{
  "final_decision": "supported",
  "favored_model": "Model B",
  "reasoning": "İddiadaki her iki önerme de bağlam tarafından doğrudan ve açıkça desteklenmektedir. Her iki model de isabetli karar vermiştir."
}
```

[EMSAL 2 - Kısmi Destek Kuralı: En az bir doğru + en az bir bağlam dışı/çelişkili parça]
BAĞLAM: "KOAH'ta kronik öksürük balgamlı veya balgamsız olabilir. Hastalığın alevlenme dönemlerinde balgamın sarı-yeşil renge dönmesi mümkündür."
İDDİA: "Sarı-yeşil balgam alevlenmede görülebilir, bu renk değişikliği zatürre tanısını kesinleştirir."
MODEL A'NIN KARARI: contradicted (Gerekçe: Zatürre tanısı bağlamda yoktur, yanlıştır)
MODEL B'NİN KARARI: partially_supported (Atom 1: "Sarı-yeşil balgam alevlenmede görülebilir" -> entailed, Atom 2: "Zatürre tanısını kesinleştirir" -> not_in_context)
HAKEM KARARI:
```json
{
  "final_decision": "partially_supported",
  "favored_model": "Model B",
  "reasoning": "DİKKAT: İddiada doğru bir bilgi (balgam rengi) ile bağlamda olmayan bir bilgi (zatürre) bir aradadır. Tanım gereği bu vaka ASLA contradicted olamaz; doğru parça içerdiği için partially_supported olmalıdır. Model B haklıdır."
}
```

[EMSAL 3 - Tam Çelişki Kuralı: Sıfır destek + en az bir doğrudan zıtlık]
BAĞLAM: "Ödeme İste servisinde farklı kullanım modelleri bulunur. Modeller, talebin kabul edilebileceği tarih ile ödemenin beklendiği tarihe göre değişebilir."
İDDİA: "Ödeme İste servisinde tarihe göre değişmeyen tek bir kullanım modeli vardır."
MODEL A'NIN KARARI: contradicted (Gerekçe: Bağlam farklı modeller olduğunu söylüyor)
MODEL B'NİN KARARI: partially_supported (Atom 1: "Ödeme iste servisi vardır" -> entailed, Atom 2: "Tek bir model vardır" -> contradicted)
HAKEM KARARI:
```json
{
  "final_decision": "contradicted",
  "favored_model": "Model A",
  "reasoning": "İddianın ana hükmü bağlamdaki 'farklı modeller vardır' bilgisiyle doğrudan zıttır. Model B'nin iddiayı zoraki parçalayarak destek çıkarması hatalıdır; iddiada doğrulanabilir bir destek yoktur. Model A haklıdır."
}
```

[EMSAL 4 - Bilgi Yokluğu / Doğrulanamazlık]
BAĞLAM: "FAST sistemi 8 Ocak 2021 tarihinde işletime alınmıştır. Ödeme talimatları saniyeler içinde sonuçlanabilir."
İDDİA: "FAST bildirimi alan taraf tamamlanan ödemeyi bir saat içinde geri çevirebilir."
MODEL A'NIN KARARI: contradicted
MODEL B'NİN KARARI: unverifiable (Atom: "tamamlanan ödemeyi geri çevirebilir" -> not_in_context)
HAKEM KARARI:
```json
{
  "final_decision": "unverifiable",
  "favored_model": "Model B",
  "reasoning": "Bağlam ödemenin geri çevrilip çevrilemeyeceğine dair hiçbir bilgi içermemektedir. Çelişki yoktur, sadece bilgi eksikliği vardır. Bu nedenle karar unverifiable olmalıdır. Model B haklıdır."
}
```
"""


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
    from scipy.stats import binomtest
    b = 0
    c = 0
    for yt, ya, yb in zip(y_true, y_pred_a, y_pred_b):
        a_corr = (ya == yt)
        b_corr = (yb == yt)
        if a_corr and not b_corr:
            b += 1
        elif not a_corr and b_corr:
            c += 1

    total_discordant = b + c
    if total_discordant == 0:
        return {"b": b, "c": c, "p_value_exact": 1.0, "significant_005": False}

    res = binomtest(min(b, c), total_discordant, p=0.5, alternative="two-sided")
    p_val = float(res.pvalue)

    return {
        "b_model_a_only": b,
        "c_model_b_only": c,
        "total_discordant": total_discordant,
        "p_value_exact": p_val,
        "significant_005": p_val < 0.05,
    }


def build_fewshot_prompt(case: dict[str, Any]) -> str:
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

{FEWSHOT_PRECEDENTS}

--------------------------------------------------
ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

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

ETİKET KURALLARI VE DİKKAT EDİLECEK HUSUSLAR:
1. supported: İddiadaki BÜTÜN bilgiler bağlam tarafından açıkça doğrulanmaktadır.
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir bilgi yer alıyorsa bu etiket ZORUNLUDUR. Sakın sırf yanlış parça var diye contradicted seçme!
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda iddiaya dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

Lütfen yukarıdaki emsal kararları ve kuralları dikkate alarak SADECE aşağıdaki JSON formatında çıktı üret:
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
        "X-OpenRouter-Title": "TR-FactBench FewShot Meta-Arbitration Judge",
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
        raise ValueError("OPENROUTER_API_KEY could not be found!")

    print(f"Loaded OpenRouter API Key (prefix: {api_key[:12]}...)")
    print(f"Target Judge Model: {MODEL_ID} (Few-Shot Informed Meta-Judge)")

    cases_path = Path("data/processed/arbitration/arbitration_cases_120.jsonl")
    if not cases_path.exists():
        cases_path = Path("k2_nli/data/processed/arbitration/arbitration_cases_120.jsonl")

    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(cases)} arbitration disagreement cases.")

    out_dir = Path("reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1")
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_file = out_dir / "arbitration_predictions_120.jsonl"
    raw_resp_file = out_dir / "raw_responses_120.jsonl"

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
    t_start = time.time()

    print("\nStarting OpenRouter Few-Shot Meta-Arbitration Loop on 120 Cases...")
    for idx, case in enumerate(cases, 1):
        eid = case["example_id"]
        gold = case["gold_label"]

        if eid in existing_preds:
            rec = existing_preds[eid]
            results.append(rec)
            if rec["judge_correct"]:
                correct_count += 1
            continue

        prompt = build_fewshot_prompt(case)
        resp_json, lat = call_openrouter(prompt, api_key)

        usage = resp_json.get("usage", {})
        p_tokens = usage.get("prompt_tokens", 0)
        c_tokens = usage.get("completion_tokens", 0)

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

        with open(pred_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        with open(raw_resp_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"example_id": eid, "response": resp_json}, ensure_ascii=False) + "\n")

        acc_so_far = correct_count / len(results) * 100
        print(f"[{len(results):3d}/{len(cases)}] Decision: {parsed['final_decision']:<19} | Gold: {gold:<19} | Favors: {parsed['favored_model']:<8} | Acc: {acc_so_far:.1f}% ({correct_count}/{len(results)}) | Lat: {lat:.2f}s", flush=True)

        time.sleep(0.15)

    print("\nFew-Shot Meta-Arbitration phase on 120 disagreements finished!")
    disagree_metrics = hard_label_metrics(
        [r["gold_label"] for r in results],
        [r["judge_decision"] for r in results],
    )

    # Load 358 consensus cases to assemble Full 478 End-to-End Hybrid
    k1_candidates = [
        Path("tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl"),
        Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl"),
    ]
    k1_path = next(p for p in k1_candidates if p.exists())
    k1_rows = [json.loads(line) for line in k1_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    k1_map = {r["release_example_id"]: r for r in k1_rows}

    k2_candidates = [
        Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl"),
        Path("k2_nli/reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl"),
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
            source = "llama70b_fewshot_judge"
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

    with open(out_dir / "hybrid_full_predictions_478.jsonl", "w", encoding="utf-8") as f:
        for r in hybrid_full_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    hybrid_metrics = hard_label_metrics(y_true_all, y_hybrid_all)
    k1_metrics = hard_label_metrics(y_true_all, y_k1_all)
    k2_metrics = hard_label_metrics(y_true_all, y_k2_all)

    mcnemar_vs_k1 = calculate_mcnemar(y_true_all, y_hybrid_all, y_k1_all)
    mcnemar_vs_k2 = calculate_mcnemar(y_true_all, y_hybrid_all, y_k2_all)

    # Actual cost calculation
    actual_cost = 0.0
    if raw_resp_file.exists():
        for line in raw_resp_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                actual_cost += float((json.loads(line)["response"].get("usage") or {}).get("cost", 0) or 0)

    favored_counts = {
        "Model A": sum(1 for r in results if r["favored_model"] == "Model A"),
        "Model B": sum(1 for r in results if r["favored_model"] == "Model B"),
        "Neither": sum(1 for r in results if r["favored_model"] in ("Neither", "Unknown")),
    }

    consensus_records = [r for r in hybrid_full_records if r["source"] == "consensus"]
    consensus_correct = sum(1 for r in consensus_records if r["is_correct"])

    summary = {
        "experiment_id": "K3-FEWSHOT-LLAMA70B-ARBITRATION-v1",
        "judge_model": MODEL_ID,
        "n_arbitration_cases": len(cases),
        "judge_correct_count": correct_count,
        "judge_disagreement_accuracy": round(disagree_metrics["accuracy"], 4),
        "judge_disagreement_macro_f1": round(disagree_metrics["macro_f1"], 4),
        "favored_model_distribution": favored_counts,
        "consensus_cases_count": len(consensus_records),
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
            "k2_soft_macro_f1": round(k2_metrics["macro_f1"], 4),
            "k2_soft_accuracy": round(k2_metrics["accuracy"], 4),
            "zero_shot_meta_acc": 0.4750,
            "zero_shot_meta_macro_f1": 0.4579,
        },
        "mcnemar_tests": {
            "hybrid_vs_k1": mcnemar_vs_k1,
            "hybrid_vs_k2": mcnemar_vs_k2,
        },
        "actual_cost_usd_openrouter": round(actual_cost, 6),
        "total_inference_seconds": round(sum(r.get("latency_seconds", 0) for r in results), 2),
    }

    with open(out_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("FEW-SHOT INFORMED LLAMA-3.3-70B ARBITRATION EXPERIMENT COMPLETED!")
    print(f"Judge Accuracy in Disagreements: {disagree_metrics['accuracy']*100:.2f}% ({correct_count}/{len(cases)})")
    print(f"End-to-End Hybrid Accuracy: {hybrid_metrics['accuracy']*100:.2f}% ({sum(r['is_correct'] for r in hybrid_full_records)}/{len(y_true_all)})")
    print(f"End-to-End Hybrid Macro-F1: {hybrid_metrics['macro_f1']:.4f}")
    print(f"End-to-End Hybrid MCC: {hybrid_metrics['mcc']:.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
