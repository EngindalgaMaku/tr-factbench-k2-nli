#!/usr/bin/env python3
"""
74_run_debiased_neutral_atoms_arbitration.py
Ablation Experiment: Debiased Neutral Atoms Meta-Arbitration
Isolates Proposition Extraction (Gemma Atomizer) as Component 0.
Masks intermediate NLI labels from Model B so the Judge sees neutral atomic propositions
without being poisoned or swayed by downstream classification biases.

Input: data/processed/arbitration/arbitration_cases_123.jsonl
Target Judge: meta-llama/llama-3.3-70b-instruct
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
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure k2_nli package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from k2_nli.labels import CLAIM_LABELS
from k2_nli.metrics import evaluate_predictions

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "meta-llama/llama-3.3-70b-instruct"

# Precedents adapted to neutral atomic propositions format (no intermediate NLI labels)
FEWSHOT_PRECEDENTS = """EMSAL KARARLAR (ÖNCEKİ MAHKEME İÇTİHATLARI):

[EMSAL 1 - İki parçalı doğru iddia]
BAĞLAM: "Alışverişlerde işyeri bir FAST-TR Karekod oluşturabilir. Müşteri bu karekodu mobil bankacılık uygulamasından okutarak FAST ödemesini başlatır."
İDDİA: "Alışverişte müşteri, işyerinin oluşturduğu karekodu mobil uygulamasından okutarak FAST ödemesi başlatabilir."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "işyeri karekod oluşturabilir"
2. "müşteri mobil uygulamadan karekodu okutarak FAST ödemesi başlatabilir"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): supported
- Model B (Atomik Analiz): supported
HAKEM KARARI:
```json
{
  "reasoning": "İddiadaki her iki önerme de bağlam tarafından doğrudan ve açıkça desteklenmektedir. Her iki model de isabetli karar vermiştir.",
  "favored_model": "Model B",
  "final_decision": "supported"
}
```

[EMSAL 2 - Kısmi Destek Kuralı: En az bir doğru + en az bir bağlam dışı/çelişkili parça]
BAĞLAM: "KOAH'ta kronik öksürük balgamlı veya balgamsız olabilir. Hastalığın alevlenme dönemlerinde balgamın sarı-yeşil renge dönmesi mümkündür."
İDDİA: "Sarı-yeşil balgam alevlenmede görülebilir, bu renk değişikliği zatürre tanısını kesinleştirir."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "Sarı-yeşil balgam alevlenmede görülebilir"
2. "bu renk değişikliği zatürre tanısını kesinleştirir"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "DİKKAT: İddiada doğru bir bilgi (balgam rengi) ile bağlamda olmayan bir bilgi (zatürre) bir aradadır. Tanım gereği bu vaka ASLA contradicted olamaz; doğru parça içerdiği için partially_supported olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "partially_supported"
}
```

[EMSAL 3 - Tam Çelişki Kuralı: Sıfır destek + en az bir doğrudan zıtlık]
BAĞLAM: "Ödeme İste servisinde farklı kullanım modelleri bulunur. Modeller, talebin kabul edilebileceği tarih ile ödemenin beklendiği tarihe göre değişebilir."
İDDİA: "Ödeme İste servisinde tarihe göre değişmeyen tek bir kullanım modeli vardır."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "Ödeme İste servisi vardır"
2. "tarihe göre değişmeyen tek bir kullanım modeli vardır"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "İddianın temel iddiası 'tek bir model olduğu' yönündedir ve bu bilgi bağlamla taban tabana zıttır. Giriş ifadesi bağımsız bir olgu değil, zıt önermenin taşıyıcısıdır. Model A'nın contradicted kararı doğrudur.",
  "favored_model": "Model A",
  "final_decision": "contradicted"
}
```

[EMSAL 4 - Bilgi Yokluğu / Doğrulanamazlık]
BAĞLAM: "FAST sistemi 8 Ocak 2021 tarihinde işletime alınmıştır. Ödeme talimatları saniyeler içinde sonuçlanabilir."
İDDİA: "FAST bildirimi alan taraf tamamlanan ödemeyi bir saat içinde geri çevirebilir."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "FAST bildirimi alan taraf tamamlanan ödemeyi bir saat içinde geri çevirebilir"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): unverifiable
HAKEM KARARI:
```json
{
  "reasoning": "Bağlam ödemenin geri çevrilip çevrilemeyeceğine dair hiçbir bilgi içermemektedir. Çelişki yoktur, sadece bilgi eksikliği vardır. Bu nedenle karar unverifiable olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "unverifiable"
}
```
"""


def build_debiased_prompt(case: dict[str, Any]) -> str:
    context = case["context"]
    claim = case["claim"]
    k1_pred = case["k1_pred"]
    k2_pred = case["k2_pred"]

    # Neutral atomic propositions without NLI labels
    atoms_list = case.get("k2_atoms", [])
    if atoms_list:
        atoms_str = "\n".join(
            [f"{i+1}. \"{a.get('atom', a.get('claim_atom', ''))}\"" for i, a in enumerate(atoms_list)]
        )
    else:
        atoms_str = f"1. \"{claim}\""

    prompt = f"""Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı bilirkişi modeli uzlaşamamıştır. İddianın bağımsız olarak ayrıştırılmış atomik önermelerini ve bilirkişi modellerinin kararlarını inceleyerek hakem kararını ver.

{FEWSHOT_PRECEDENTS}

--------------------------------------------------
ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
\"\"\"{context}\"\"\"

İDDİA:
\"\"\"{claim}\"\"\"

İDDİANIN ATOMİK ÖNERMELERİ (Ön İnceleme - Bağımsız Ayrıştırıcı Tarafından Bölünmüş Yapıtaşları):
{atoms_str}

BİLİRKİŞİ MODELLERİNİN DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): {k1_pred}
  (İddianın tüm bağlam içindeki mantıksal kapsamını tek seferde değerlendirmiştir.)
- Model B (Atomik Analiz): {k2_pred}
  (Yukarıdaki atomik önermelerin her birini tekil olarak test ederek bu sonuca varmıştır.)

ETİKET KURALLARI VE DİKKAT EDİLECEK HUSUSLAR:
1. supported: İddiadaki BÜTÜN önermeler bağlam tarafından açıkça doğrulanmaktadır.
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir önerme yer alıyorsa bu etiket ZORUNLUDUR.
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda önermelere dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

Lütfen ÖNCE bağlamdaki kanıtı ve ayrıştırılmış önermeleri adım adım düşünerek analiz et, ARDINDAN kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Önce bağlamdaki kanıtı ve önermeleri tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
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
            found = False
            for lbl in CLAIM_LABELS:
                if lbl in decision:
                    decision = lbl
                    found = True
                    break
            if not found:
                decision = "unverifiable"

        return {
            "reasoning": str(data.get("reasoning", "")),
            "favored_model": str(data.get("favored_model", "Neither")),
            "final_decision": decision,
        }
    except Exception:
        # Fallback keyword extraction
        lowered = cleaned.lower()
        for lbl in ["partially_supported", "unverifiable", "contradicted", "supported"]:
            if f'"{lbl}"' in lowered or f"'{lbl}'" in lowered:
                return {
                    "reasoning": "JSON parse failed, regex fallback used.",
                    "favored_model": "Neither",
                    "final_decision": lbl,
                }
        return {
            "reasoning": "Complete parse failure.",
            "favored_model": "Neither",
            "final_decision": "unverifiable",
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
        "X-OpenRouter-Title": "TR-FactBench Debiased Neutral Atoms Arbitration",
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 400,
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
                print(f"[Retry {attempt}] HTTP {resp.status_code}. Sleeping {sleep_s:.1f}s...")
                time.sleep(sleep_s)
            else:
                resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise e
            sleep_s = backoff_factor ** attempt
            print(f"[Retry {attempt}] Connection error: {e}. Sleeping {sleep_s:.1f}s...")
            time.sleep(sleep_s)
    raise RuntimeError("Max retries exceeded.")


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
    print(f"Target Judge Model: {MODEL_ID} (Debiased Neutral Atoms Meta-Judge)")

    cases_path = Path("data/processed/arbitration/arbitration_cases_123.jsonl")
    if not cases_path.exists():
        cases_path = Path("k2_nli/data/processed/arbitration/arbitration_cases_123.jsonl")

    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(cases)} arbitration cases.")

    out_dir = Path("reports/experiments/K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1")
    if not out_dir.parent.exists():
        out_dir = Path("k2_nli/reports/experiments/K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1")
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_file = out_dir / "arbitration_predictions_123.jsonl"
    raw_resp_file = out_dir / "raw_responses_123.jsonl"

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

    print(f"\nStarting OpenRouter Debiased Neutral Atoms Arbitration Loop on {len(cases)} Cases...")
    for idx, case in enumerate(cases, 1):
        eid = case["example_id"]
        gold = case["gold_label"]

        if eid in existing_preds:
            rec = existing_preds[eid]
            results.append(rec)
            if rec["judge_correct"]:
                correct_count += 1
            continue

        prompt = build_debiased_prompt(case)
        resp_json, lat = call_openrouter(prompt, api_key)

        choice = resp_json.get("choices", [{}])[0]
        raw_output = choice.get("message", {}).get("content", "").strip()

        parsed = parse_judge_output(raw_output)
        is_corr = (parsed["final_decision"] == gold)
        if is_corr:
            correct_count += 1

        rec = {
            "example_id": eid,
            "domain": case.get("domain", "general"),
            "gold_label": gold,
            "k1_pred": case["k1_pred"],
            "k1_correct": case["k1_correct"],
            "k2_pred": case["k2_pred"],
            "k2_correct": case["k2_correct"],
            "judge_decision": parsed["final_decision"],
            "judge_correct": is_corr,
            "favored_model": parsed["favored_model"],
            "reasoning": parsed["reasoning"],
            "latency_seconds": round(lat, 2),
            "raw_output": raw_output,
        }
        results.append(rec)

        # Append incrementally
        with open(pred_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        with open(raw_resp_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"example_id": eid, "response": resp_json}, ensure_ascii=False) + "\n")

        acc_so_far = correct_count / len(results) * 100
        print(
            f"[{idx:03d}/{len(cases):03d}] {eid} | Gold: {gold:<19} | Judge: {parsed['final_decision']:<19} | "
            f"Favors: {parsed['favored_model']:<7} | [{'CORRECT' if is_corr else 'WRONG':7s}] (Running: {correct_count}/{len(results)} - {acc_so_far:.1f}%)"
        )
        time.sleep(0.3)  # Gentle rate limit

    total_time = time.time() - t_start
    print(f"\nProcessing finished in {total_time:.1f}s.")

    y_true = [r["gold_label"] for r in results]
    y_pred = [r["judge_decision"] for r in results]
    metrics = evaluate_predictions(y_true, y_pred)

    print("\n" + "=" * 60)
    print(f"DEBIASED NEUTRAL ATOMS JUDGE ACCURACY ON 123 CASES: {metrics['accuracy']*100:.2f}% ({correct_count}/{len(cases)})")
    print(f"Macro-F1: {metrics['macro_f1']:.4f}")
    print("=" * 60)

    # Save summary
    summary = {
        "experiment_id": "K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1",
        "judge_model": MODEL_ID,
        "n_cases": len(cases),
        "correct": correct_count,
        "accuracy": round(metrics["accuracy"], 4),
        "macro_f1": round(metrics["macro_f1"], 4),
        "total_time_seconds": round(total_time, 2),
    }
    with open(out_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
