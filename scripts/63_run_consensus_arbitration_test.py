#!/usr/bin/env python3
"""
63_run_consensus_arbitration_test.py
Empirical evaluation of the Meta-Judge (Llama-3.3-70B-Instruct) on the 358 Consensus Cases
where Component 1 (K1) and Component 2 (K2) already agree.

Scientific Objective (Advisor's Directive):
Empirically test rather than theoretically assume:
1. Did the judge fix any of the 21 consensus errors (Error Recovery)?
2. Did the judge overrule/break any of the 337 correct consensus cases (Regression)?
3. What is the net performance of Pure Full Arbitration (all 478 cases judged by LLM)
   vs Cascading Hybrid Pipeline (routing only 120 disagreements to LLM)?
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

# Identical 4 gold-independent precedent rulings from train split (exact match with Script 61)
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


def build_fewshot_prompt(case: dict[str, Any]) -> str:
    context = case["context"]
    claim = case["claim"]
    k1_pred = case["k1_pred"]
    k2_pred = case["k2_pred"]

    atoms_str = "\n".join(
        [f"- Atom {i+1}: \"{a['atom']}\" -> Sonuç: {a['label']}" for i, a in enumerate(case["k2_atoms"])]
    )

    prompt = f"""Sen, iki farklı yapay zeka modelinin kararını denetleyen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki modelin de analizini incele ve nihai hakem kararını ver.

{FEWSHOT_PRECEDENTS}

--------------------------------------------------
ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
\"\"\"{context}\"\"\"

İDDİA:
\"\"\"{claim}\"\"\"

MODEL A'NIN ANALİZİ (Bileşen 1: Doğrudan Doğrulayıcı):
- Karar: {k1_pred}
- Açıklama: Cümlenin tamamını bağlamla birlikte tek seferde değerlendirmiştir.

MODEL B'NİN ANALİZİ (Bileşen 2: Atomik NLI Doğrulayıcı):
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
  "reasoning": "<Neden bu karara vardığını bağlamdaki kanıta göre açıklayan en fazla 2 cümlelik kısa Türkçe gerekçe>"
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
        "X-OpenRouter-Title": "TR-FactBench Consensus Arbitration Test (358 cases)",
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 300,
        "stream": False,
    }

    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    t0 = time.time()
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=90, verify=False)
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to process")
    args = parser.parse_args()

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
    print(f"Target Judge Model: {MODEL_ID} (Evaluating 358 Consensus Cases)")

    cases_path = Path("data/processed/arbitration/consensus_cases_358.jsonl")
    if not cases_path.exists():
        cases_path = Path("k2_nli/data/processed/arbitration/consensus_cases_358.jsonl")

    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        cases = cases[:args.limit]
    print(f"Loaded {len(cases)} consensus cases.")

    out_dir = Path("reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358")
    if not out_dir.parent.exists():
        out_dir = Path("k2_nli/reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358")
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_file = out_dir / "consensus_judge_predictions_358.jsonl"
    raw_resp_file = out_dir / "raw_responses_358.jsonl"

    existing_preds: dict[str, dict[str, Any]] = {}
    if pred_file.exists():
        for line in pred_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                existing_preds[item["example_id"]] = item
        if existing_preds:
            print(f"Resuming run: Found {len(existing_preds)} already completed consensus cases.")

    results: list[dict[str, Any]] = []
    t_start = time.time()

    print(f"\nStarting OpenRouter Consensus Meta-Arbitration Loop on {len(cases)} Cases...")
    for idx, case in enumerate(cases, 1):
        eid = case["example_id"]
        gold = case["gold_label"]
        initial_correct = case["k1_correct"]  # since k1_pred == k2_pred

        if eid in existing_preds:
            rec = existing_preds[eid]
            results.append(rec)
            continue

        prompt = build_fewshot_prompt(case)
        resp_json, lat = call_openrouter(prompt, api_key)

        usage = resp_json.get("usage", {})
        choice = resp_json.get("choices", [{}])[0]
        raw_output = choice.get("message", {}).get("content", "").strip()

        parsed = parse_judge_output(raw_output)
        judge_correct = (parsed["final_decision"] == gold)

        # Categorize impact:
        # 1. Maintained Correct: initially correct and judge correct
        # 2. Regressed (Bozulan): initially correct, but judge wrong
        # 3. Recovered (Düzeltilen): initially wrong, but judge correct
        # 4. Maintained Wrong: initially wrong and judge wrong
        if initial_correct and judge_correct:
            impact = "maintained_correct"
        elif initial_correct and not judge_correct:
            impact = "regressed_broken"
        elif not initial_correct and judge_correct:
            impact = "recovered_fixed"
        else:
            impact = "maintained_wrong"

        rec = {
            "example_id": eid,
            "domain": case["domain"],
            "gold_label": gold,
            "consensus_pred": case["k1_pred"],
            "consensus_correct": initial_correct,
            "judge_decision": parsed["final_decision"],
            "judge_correct": judge_correct,
            "impact": impact,
            "favored_model": parsed["favored_model"],
            "reasoning": parsed["reasoning"],
            "json_valid": parsed["json_valid"],
            "latency_sec": round(lat, 2),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        }
        results.append(rec)

        with open(pred_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        raw_record = {"example_id": eid, "raw_response": raw_output}
        with open(raw_resp_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(raw_record, ensure_ascii=False) + "\n")

        status_sym = "[FIXED!]" if impact == "recovered_fixed" else ("[BROKE!]" if impact == "regressed_broken" else "[OK]")
        print(f"[{idx:03d}/{len(cases):03d}] {eid} | Gold: {gold:19s} | Cons: {case['k1_pred']:19s} | Judge: {parsed['final_decision']:19s} | {status_sym}")

    total_time = time.time() - t_start
    print(f"\nProcessing finished in {total_time:.1f}s.")

    # Empirical Summary Analysis
    n_total = len(results)
    n_init_correct = sum(1 for r in results if r["consensus_correct"])
    n_init_wrong = sum(1 for r in results if not r["consensus_correct"])
    
    n_judge_correct = sum(1 for r in results if r["judge_correct"])
    n_recovered = sum(1 for r in results if r["impact"] == "recovered_fixed")
    n_regressed = sum(1 for r in results if r["impact"] == "regressed_broken")
    n_maintained_corr = sum(1 for r in results if r["impact"] == "maintained_correct")
    n_maintained_wrong = sum(1 for r in results if r["impact"] == "maintained_wrong")

    init_acc = n_init_correct / n_total
    judge_acc = n_judge_correct / n_total

    summary = {
        "n_consensus_cases": n_total,
        "initial_consensus_accuracy": round(init_acc, 4),
        "initial_correct_count": n_init_correct,
        "initial_error_count": n_init_wrong,
        "judge_accuracy_on_consensus": round(judge_acc, 4),
        "judge_correct_count": n_judge_correct,
        "breakdown": {
            "recovered_fixed (Düzeltilen Hatalar)": {
                "count": n_recovered,
                "recovery_rate_pct": round(n_recovered / n_init_wrong * 100, 2) if n_init_wrong else 0,
            },
            "regressed_broken (Bozulan Doğrular)": {
                "count": n_regressed,
                "regression_rate_pct": round(n_regressed / n_init_correct * 100, 2) if n_init_correct else 0,
            },
            "maintained_correct": n_maintained_corr,
            "maintained_wrong": n_maintained_wrong,
        },
        "net_gain_or_loss": n_recovered - n_regressed,
    }

    summary_file = out_dir / "consensus_arbitration_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 60)
    print("EMPIRICAL BREAKDOWN ON 358 CONSENSUS CASES:")
    print("=" * 60)
    print(f"Toplam Uzlaşma Vakası: {n_total}")
    print(f"Başlangıç Uzlaşma Doğruluğu: {n_init_correct}/{n_total} (%{init_acc*100:.2f})")
    print(f"Hakemin Uzlaşma Doğruluğu  : {n_judge_correct}/{n_total} (%{judge_acc*100:.2f})")
    print("-" * 60)
    print(f"DÜZELTİLEN HATALAR (Recovery) : {n_recovered} / {n_init_wrong} (%{summary['breakdown']['recovered_fixed (Düzeltilen Hatalar)']['recovery_rate_pct']} başarı)")
    print(f"BOZULAN DOĞRULAR (Regression) : {n_regressed} / {n_init_correct} (%{summary['breakdown']['regressed_broken (Bozulan Doğrular)']['regression_rate_pct']} kayıp)")
    print(f"NET ETKİ (Net Payoff)         : {summary['net_gain_or_loss']} vaka")
    print("=" * 60)


if __name__ == "__main__":
    main()
