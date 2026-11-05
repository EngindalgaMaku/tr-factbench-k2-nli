#!/usr/bin/env python3
"""
160_run_k3_v5_meta_arbitration.py
Hibrit v2 Component 3 (K3 V5) Meta-Arbitration Runner

Incorporates findings from 143-case comprehensive audit:
- Bulgu #4: Balanced 8-Shot Precedents (Symmetric class priors).
- Bulgu #5B: K2 atom-level softmax probability vectors & borderline [50-65%] alerts.
- Bulgu #6: Premise collapse & dependent clause rule.
- Bulgu #8: K1 softmax confidence & entropy signals (warning when confidence < 80%).
- Bulgu #9: Contradiction priority (1 Contradiction + 1 Unverifiable != partially_supported).
- Bulgu #11: Robust JSON regex fallback parser & passive/active voice equivalence.
- Bulgu #12: Modifier / Adjective Hallucination awareness.
- Bulgu #13: Temporal & quantitative paraphrase equivalence (15 dk == çeyrek saat).

Target Model: meta-llama/llama-3.3-70b-instruct via OpenRouter API
Output: k2_nli/reports/experiments/K3-V5-META-ARBITRATION-LLAMA70B-v1/
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

K3_V5_PRECEDENTS = """EMSAL KARARLAR (ÖNCEKİ İÇTİHATLAR):

[EMSAL 1 - Tam Destek: Bütün Önermeler Açıkça Doğrulanıyor]
BAĞLAM: "Alışverişlerde işyeri bir FAST-TR Karekod oluşturabilir. Müşteri bu karekodu mobil bankacılık uygulamasından okutarak FAST ödemesini başlatır."
İDDİA: "Alışverişte müşteri, işyerinin oluşturduğu karekodu mobil uygulamasından okutarak FAST ödemesi başlatabilir."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): supported (Güven: %99.8)
- Model B (Atomik): supported
  1. "işyeri karekod oluşturabilir" -> entailment [E: %98.4, N: %1.2, C: %0.4]
  2. "müşteri mobil uygulamadan karekodu okutarak FAST ödemesi başlatabilir" -> entailment [E: %99.1, N: %0.7, C: %0.2]
HAKEM KARARI:
```json
{
  "reasoning": "İddiadaki her iki eylem de bağlam tarafından doğrudan ve eksiksiz desteklenmektedir. Her iki model de isabetlidir.",
  "favored_model": "Model B",
  "final_decision": "supported"
}
```

[EMSAL 2 - Kısmi Destek: 1 Doğru Parça + 1 Bağlam Dışı Parça]
BAĞLAM: "KOAH'ta kronik öksürük balgamlı veya balgamsız olabilir. Hastalığın alevlenme dönemlerinde balgamın sarı-yeşil renge dönmesi mümkündür."
İDDİA: "Sarı-yeşil balgam alevlenmede görülebilir, bu renk değişikliği zatürre tanısını kesinleştirir."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): contradicted (Güven: %62.4 - DÜŞÜK GÜVEN UYARISI)
- Model B (Atomik): partially_supported
  1. "Sarı-yeşil balgam alevlenmede görülebilir" -> entailment [E: %96.5, N: %3.1, C: %0.4]
  2. "bu renk değişikliği zatürre tanısını kesinleştirir" -> neutral [E: %0.2, N: %99.1, C: %0.7]
HAKEM KARARI:
```json
{
  "reasoning": "İddiada doğrulanmış bir olgu (balgam rengi) ile bağlamda geçmeyen bir iddia (zatürre) bir aradadır. İddia doğru parça içerdiği için ASLA contradicted veya unverifiable olamaz; doğru karar partially_supported olmalıdır. Model A düşük güvenle yanılmıştır.",
  "favored_model": "Model B",
  "final_decision": "partially_supported"
}
```

[EMSAL 3 - Kısmi Destek: 1 Doğru Parça + 1 Çelişen Parça]
BAĞLAM: "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir. Göz hareket ettikçe elektrotlar arasındaki potansiyel fark değişir."
İDDİA: "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir. Kayıt işlemi göz hareketinden bağımsız sabit bir potansiyeli ölçer."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): contradicted (Güven: %91.0)
- Model B (Atomik): partially_supported
  1. "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir" -> entailment [E: %98.7, N: %1.0, C: %0.3]
  2. "Kayıt işlemi göz hareketinden bağımsız sabit bir potansiyeli ölçer" -> contradiction [E: %0.5, N: %2.1, C: %97.4]
HAKEM KARARI:
```json
{
  "reasoning": "İddianın ilk cümlesi bağlamca harfiyen doğrulanmakta, ikinci cümlesi ise bağlamdaki potansiyel değişimiyle çelişmektedir. İddiada açıkça doğrulanmış bir parça var olduğundan karar contradicted değil, partially_supported olmalıdır.",
  "favored_model": "Model B",
  "final_decision": "partially_supported"
}
```

[EMSAL 4 - Tam Çelişki: Doğrulanan Sıfır Parça + Doğrudan Zıtlık]
BAĞLAM: "Ödeme İste servisinde farklı kullanım modelleri bulunur. Modeller tarihe göre değişebilir."
İDDİA: "Ödeme İste servisinde tarihe göre değişmeyen tek bir kullanım modeli vardır."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): contradicted (Güven: %95.8)
- Model B (Atomik): partially_supported
  1. "Ödeme İste servisi vardır" -> entailment [E: %54.2, N: %43.0, C: %2.8 - SINIRDA EŞLEŞME UYARISI]
  2. "tarihe göre değişmeyen tek bir kullanım modeli vardır" -> contradiction [E: %0.8, N: %3.1, C: %96.1]
HAKEM KARARI:
```json
{
  "reasoning": "İddianın özü 'tek model olduğu'dur ve bağlamla taban tabana zıttır. Model B'nin 'servis vardır' önermesi düşük güvenli (%54.2) yüzeysel kelime benzerliğidir, bağımsız bir bilgi değildir. Desteklenen bağımsız olgu bulunmadığından karar contradicted'dır. Model A haklıdır.",
  "favored_model": "Model A",
  "final_decision": "contradicted"
}
```

[EMSAL 5 - Çelişki Önceliği Kuralı: 1 Çelişki + 1 Doğrulanamayan (SIFIR Destek)]
BAĞLAM: "Rüçhan hakkı kullanım süresi en az 15, en çok 60 gündür. Kuponlar Pay Piyasasında işlem görür."
İDDİA: "Rüçhan hakkı kullanım süresi en az 90 gündür. Kuponlar tezgahüstü piyasada işlem görür."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): contradicted (Güven: %89.5)
- Model B (Atomik): partially_supported
  1. "Rüçhan hakkı süresi en az 90 gündür" -> contradiction [E: %0.1, N: %1.2, C: %98.7]
  2. "Kuponlar tezgahüstü piyasada işlem görür" -> neutral [E: %2.1, N: %96.4, C: %1.5]
HAKEM KARARI:
```json
{
  "reasoning": "DİKKAT: İddiada 1 Çelişki ve 1 Bilgi Yokluğu (Neutral) vardır; bağlamca DESTEKLENEN HİÇBİR BİLGİ YOKTUR. Desteklenen hiçbir parça yokken bir iddia ASLA partially_supported olamaz. Karar kesinlikle contradicted'dır. Model A haklıdır.",
  "favored_model": "Model A",
  "final_decision": "contradicted"
}
```

[EMSAL 6 - Bilgi Yokluğu: Semantik Yüklem Doğrulanmaması]
BAĞLAM: "FAST sistemi 8 Ocak 2021 tarihinde işletime alınmıştır. Talimatlar anlık sonuçlanır."
İDDİA: "FAST bildirimi alan taraf tamamlanan ödemeyi bir saat içinde geri çevirebilir."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): contradicted (Güven: %71.2 - DÜŞÜK GÜVEN UYARISI)
- Model B (Atomik): unverifiable
  1. "FAST bildirimi alan taraf ödemeyi bir saat içinde geri çevirebilir" -> neutral [E: %1.1, N: %97.2, C: %1.7]
HAKEM KARARI:
```json
{
  "reasoning": "FAST kavramı bağlamda geçse de 'ödemenin geri çevrilmesi' eylemine dair bağlamda hiçbir bilgi yoktur. Çelişki değil bilgi yokluğu söz konusudur. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "unverifiable"
}
```

[EMSAL 7 - Bilgi Yokluğu: Niteleyici / Sıfat Halüsinasyonu]
BAĞLAM: "Marka iptal talebinde emanet tutarı Merkez Bankasında açılacak vadeli veya vadesiz bir hesapta tutulur."
İDDİA: "Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): partially_supported (Güven: %76.0 - DÜŞÜK GÜVEN UYARISI)
- Model B (Atomik): supported
  1. "emanet tutarı getirili ayrı bir hesapta tutulur" -> entailment [E: %57.3, N: %41.0, C: %1.7 - SINIRDA EŞLEŞME UYARISI]
HAKEM KARARI:
```json
{
  "reasoning": "İddiadaki 'getirili ayrı bir' niteleyicisi bağlamda bulunmamaktadır. Model B yüzeysel kelime benzerliğinden dolayı sınırda güvenle (%57.3) desteklemiş olsa da niteleyici doğrulanmadığı için iddia unverifiable'dır.",
  "favored_model": "Neither",
  "final_decision": "unverifiable"
}
```

[EMSAL 8 - Anlamsal ve Çatı Eşdeğerliği: Edilgen / Etken Yapılar ve Eşanlamlılar]
BAĞLAM: "İnternet abonelik fesih bildiriminin ulaşmasından itibaren abonelik en geç yedi gün içinde sona erdirilir."
İDDİA: "İşletmeci fesih bildiriminden sonra feshi en geç yedi gün içinde tamamlar."
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül): supported (Güven: %96.3)
- Model B (Atomik): partially_supported
  1. "işletmeci feshi en geç yedi gün içinde tamamlar" -> neutral [E: %34.1, N: %64.2, C: %1.7]
HAKEM KARARI:
```json
{
  "reasoning": "Abonelik mevzuatında feshin 'sona erdirilmesi' yükümlülüğü zaten işletmeciye aittir. Cümlenin edilgen kurulmuş olması anlam farkı veya bilgi eksikliği yaratmaz. İddia bağlam tarafından tam desteklenmektedir. Model A haklıdır.",
  "favored_model": "Model A",
  "final_decision": "supported"
}
```
"""


def build_k3_v5_prompt(
    case: dict[str, Any],
    k1_data: dict[str, Any],
    atoms: list[dict[str, Any]],
) -> str:
    eid = case["example_id"]
    context = case["context"]
    claim = case["claim"]
    k1_pred = case["k1_pred"]
    k2_pred = case["k2_pred"]

    # Model A details
    k1_probs = k1_data.get("probabilities", {})
    k1_conf = max(k1_probs.values()) * 100 if k1_probs else 0.0
    k1_warn = " [DİKKAT: DÜŞÜK GÜVEN UYARISI (<%80)]" if k1_conf < 80.0 else ""
    prob_str = f"[S: %{k1_probs.get('supported', 0.0)*100:.1f}, PS: %{k1_probs.get('partially_supported', 0.0)*100:.1f}, C: %{k1_probs.get('contradicted', 0.0)*100:.1f}, U: %{k1_probs.get('unverifiable', 0.0)*100:.1f}]"

    # Model B atoms
    atom_lines = []
    for i, a in enumerate(atoms):
        lbl = a["pred_label"]
        pe = a["prob_entailment"] * 100
        pn = a["prob_neutral"] * 100
        pc = a["prob_contradiction"] * 100
        warn = ""
        if lbl == "entailment" and 50.0 <= pe <= 65.0:
            warn = " [DİKKAT: SINIRDA GÜVEN - Kelime Benzerliği Riski]"
        atom_lines.append(f'  {i+1}. "{a["atom"]}" -> {lbl} [E: %{pe:.1f}, N: %{pn:.1f}, C: %{pc:.1f}]{warn}')

    atoms_str = "\n".join(atom_lines) if atom_lines else f'  1. "{claim}" -> {k2_pred}'

    prompt = f"""Sen, iki farklı yapay zeka modelinin uyuşmazlığını çözen kıdemli ve tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı bilirkişi modeli uzlaşamamıştır. Modellerin analizlerini, güven oranlarını ve iddiayı oluşturan atomik parçaları inceleyerek gerekçeli hakem kararını ver.

{K3_V5_PRECEDENTS}

--------------------------------------------------
ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
\"\"\"{context}\"\"\"

İDDİA:
\"\"\"{claim}\"\"\"

BİLİRKİŞİ MODELLERİNİN DETAYLI ANALİZLERİ:

MODEL A (Bütüncül Dizi Doğrulayıcısı):
- Karar: {k1_pred}
- Model Güven Skoru: %{k1_conf:.1f}{k1_warn}
- Sınıf Dağılımı: {prob_str}
  (İddianın tüm bağlam içindeki bütüncül mantıksal kapsamını değerlendirmiştir.)

MODEL B (Önerme Düzeyinde Atomik Doğrulayıcı):
- Karar: {k2_pred}
- İddianın Atomik Önermeleri ve NLI Olasılık Dağılımları:
{atoms_str}
  (İddiayı bağımsız alt önermelere bölerek her birini NLI modeliyle test etmiştir.)

HAKEM İLKELERİ VE ÖZEL DEĞERLENDİRME KURALLARI:
1. GÜVEN SİNYALİ KURALI: Model A'nın güven skoru <%80 ise, bu modelin karmaşık veya çok parçalı iddialarda yanılma riski çok yüksektir (%88). Bu durumda atomik parçaların kanıtlarına öncelik ver.
2. SINIRDA EŞLEŞME UYARISI: Model B'de Entailment olasılığı %50-%65 arasında olan önermeler, NLI modelinin kelime benzerliğinden (lexical overlap) etkilenmiş olabileceğini gösterir. Bu önermenin bağlamdaki tam yüklemini ve eylemini bizzat doğrula.
3. KISMİ DESTEK VE ÇELİŞKİ ÖNCELİĞİ:
   - İddiada bağlamın doğruladığı en az bir gerçek olgu/eylem varken, ek olarak bağlamda olmayan veya çelişen başka bir parça yer alıyorsa karar KESİNLİKLE partially_supported olmalıdır (asla contradicted veya unverifiable değil).
   - İddiada çelişen en az bir parça varken doğrulanmayan (bilgi yokluğu) başka parçalar varsa ve DESTEKLENEN HİÇBİR PARÇA YOKSA, karar KESİNLİKLE contradicted olmalıdır (asla partially_supported değil).
4. NİTELEYİCİ VE AYRINTI DİKKATİ: İddiada yer alan ek niteleyiciler, sıfatlar veya kısıtlamalar bağlamda yoksa ("PDF dosyası ile", "getirili ayrı bir", vb.), bağlamın ana eylemi benzese dahi bu niteleyici doğrulanmış sayılamaz.
5. ANLAMSAL VE ÇATI EŞDEĞERLİĞİ: "15 dakika = çeyrek saat", "abonelik sona erdirilir = işletmeci aboneliği sona erdirir" gibi etken/edilgen veya eşanlamlı ifadeleri tam desteklenmiş kabul et.

Lütfen bağlamdaki kanıtı adım adım analiz ederek kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Bağlamdaki kanıtı, modellerin güven sinyallerini ve önermelerin eylemlerini değerlendiren en fazla 2 cümlelik net Türkçe gerekçe>",
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
            for lbl in CLAIM_LABELS:
                if lbl in decision:
                    decision = lbl
                    break
            else:
                decision = "unverifiable"

        return {
            "reasoning": str(data.get("reasoning", "")),
            "favored_model": str(data.get("favored_model", "Neither")),
            "final_decision": decision,
            "json_valid": True,
        }
    except Exception:
        lowered = cleaned.lower()
        found = "unverifiable"
        for lbl in ["partially_supported", "unverifiable", "contradicted", "supported"]:
            if f'"{lbl}"' in lowered or f"'{lbl}'" in lowered or f": {lbl}" in lowered:
                found = lbl
                break
        return {
            "reasoning": cleaned[:300],
            "favored_model": "Neither",
            "final_decision": found,
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
        "X-OpenRouter-Title": "TR-FactBench K3-V5 Meta-Arbitration Judge",
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
    # 1. Load API key
    env_paths = [Path(".env"), Path("tr-factbench-v0.1.0-preview/.env"), Path("../.env")]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(ep)
            break

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY could not be found in environment or .env files!")

    print(f"Loaded OpenRouter API Key (prefix: {api_key[:12]}...)")
    print(f"Target Judge Model: {MODEL_ID}")

    # 2. Paths
    ROOT = Path(".")
    TFB = ROOT / "tr-factbench-v0.1.0-preview"
    K2 = ROOT / "k2_nli"

    # Load K1 predictions
    k1_dict = {
        json.loads(l)["release_example_id"]: json.loads(l)
        for l in (TFB / "data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()
    }

    # Load K2 atom predictions
    atoms_by_id: dict[str, list[dict[str, Any]]] = {}
    for l in (K2 / "runs/K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7/atom_predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        a = json.loads(l)
        eid = a.get("example_id") or a.get("source_example_id")
        atoms_by_id.setdefault(eid, []).append(a)

    # Load 123 disagreement cases
    cases_path = K2 / "data/processed/arbitration/arbitration_cases_123.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(cases)} arbitration disagreement cases.")

    # Output directory
    out_dir = K2 / "reports/experiments/K3-V5-META-ARBITRATION-LLAMA70B-v1"
    out_dir.mkdir(parents=True, exist_ok=True)

    pred_file = out_dir / "arbitration_predictions_123.jsonl"
    raw_resp_file = out_dir / "raw_responses_123.jsonl"

    # Resume capability
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

    print("\n" + "=" * 70)
    print("STARTING K3 V5 META-ARBITRATION INFERENCE")
    print("=" * 70)

    for i, case in enumerate(cases, 1):
        eid = case["example_id"]
        gold = case["gold_label"]

        if eid in existing_preds:
            res_item = existing_preds[eid]
            results.append(res_item)
            if res_item["judge_correct"]:
                correct_count += 1
            print(f"[{i:03d}/{len(cases)}] {eid} (Cached) -> Judge: {res_item['judge_decision']} | Gold: {gold} | Correct: {res_item['judge_correct']}")
            continue

        prompt = build_k3_v5_prompt(case, k1_dict.get(eid, {}), atoms_by_id.get(eid, []))

        try:
            resp_json, lat = call_openrouter(prompt, api_key)
            choice = resp_json["choices"][0]
            raw_text = choice["message"]["content"]
            usage = resp_json.get("usage", {})
            total_tokens_prompt += usage.get("prompt_tokens", 0)
            total_tokens_completion += usage.get("completion_tokens", 0)

            parsed = parse_judge_output(raw_text)
            dec = parsed["final_decision"]
            is_correct = (dec == gold)
            if is_correct:
                correct_count += 1

            record = {
                "example_id": eid,
                "domain": case.get("domain", "general"),
                "gold_label": gold,
                "k1_pred": case["k1_pred"],
                "k1_correct": (case["k1_pred"] == gold),
                "k2_pred": case["k2_pred"],
                "k2_correct": (case["k2_pred"] == gold),
                "judge_decision": dec,
                "judge_correct": is_correct,
                "favored_model": parsed["favored_model"],
                "reasoning": parsed["reasoning"],
                "latency_seconds": round(lat, 2),
                "raw_output": raw_text,
            }
            results.append(record)

            with pred_file.open("a", encoding="utf-8") as f_out:
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

            with raw_resp_file.open("a", encoding="utf-8") as f_raw:
                f_raw.write(json.dumps({"example_id": eid, "response": resp_json}, ensure_ascii=False) + "\n")

            status_icon = "[OK]" if is_correct else "[X]"
            print(
                f"[{i:03d}/{len(cases)}] {status_icon} {eid} -> Judge: {dec:20s} | Gold: {gold:20s} | "
                f"Favored: {parsed['favored_model']} ({lat:.1f}s)"
            )

            # Politeness delay
            time.sleep(0.5)

        except Exception as e:
            print(f"[{i:03d}/{len(cases)}] [ERR] {eid}: {e}")
            raise

    # Summary
    acc = correct_count / len(cases)
    print("\n" + "=" * 70)
    print("ARBITRATION RUN COMPLETED")
    print(f"Total Disagreement Cases: {len(cases)}")
    print(f"K3 V5 Correct Decisions:  {correct_count} / {len(cases)} ({acc:.2%})")
    print("=" * 70)


if __name__ == "__main__":
    main()
