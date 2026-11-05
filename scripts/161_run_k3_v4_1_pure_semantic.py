#!/usr/bin/env python3
"""
161_run_k3_v4_1_pure_semantic.py
Hibrit K3 V4.1 Yalın Semantik Hakem (Anchoring-Free / No-Numbers)

Based on V4 (script 75, 110/123 = 89.43% accuracy):
- ZERO probability numbers, ZERO confidence percentages (Prevents Anchoring Bias).
- Atoms provided purely as plain text strings (Adheres to Karar Kaydı #5).
- Adds only 3 semantic logic rules discovered in 143-case audit:
  1. Contradiction Priority: 1 Contradiction + 1 Unverifiable (0 Supported) => contradicted (never partially_supported).
  2. Partial Support Priority: 1 Supported + 1 Contradiction => partially_supported (never contradicted).
  3. Voice Equivalence: Passive vs Active voice ("sona erdirilir = işletmeci fesheder") is semantic equivalence.
- Robust JSON regex parser: Recovers truncated outputs (e.g. tfb_ex_0165).

Target Model: meta-llama/llama-3.3-70b-instruct via OpenRouter API
Output: k2_nli/reports/experiments/K3-V4-1-PURE-SEMANTIC-LLAMA70B-v1/
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure k2_nli package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from k2_nli.labels import CLAIM_LABELS

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "meta-llama/llama-3.3-70b-instruct"

# 6 Clean Precedents (Pure text, NO probability numbers, NO atom labels)
FEWSHOT_PRECEDENTS = """EMSAL KARARLAR (ÖNCEKİ İÇTİHATLAR):

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

[EMSAL 2 - Kısmi Destek Kuralı: En az bir doğru + en az bir bağlam dışı parça]
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
  "reasoning": "İddiada doğru bir bilgi (balgam rengi) ile bağlamda olmayan bir bilgi (zatürre) bir aradadır. İddia doğru parça içerdiği için ASLA contradicted olamaz; partially_supported olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "partially_supported"
}
```

[EMSAL 3 - Kısmi Destek Kuralı: 1 Doğru Parça + 1 Açık Çelişen Parça]
BAĞLAM: "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir. Göz hareket ettikçe elektrotlar arasındaki potansiyel fark değişir."
İDDİA: "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir. Kayıt işlemi göz hareketinden bağımsız sabit bir potansiyeli ölçer."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir"
2. "Kayıt işlemi göz hareketinden bağımsız sabit bir potansiyeli ölçer"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "İddianın ilk cümlesi bağlamca harfiyen doğrulanmakta, ikinci cümlesi ise bağlamla çelişmektedir. İddiada açıkça doğrulanmış bir gerçek parça var olduğu için karar contradicted değil, partially_supported olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "partially_supported"
}
```

[EMSAL 4 - Çelişki Önceliği: 1 Çelişen Parça + 1 Bilgi Yokluğu (SIFIR Destek)]
BAĞLAM: "Rüçhan hakkı kullanım süresi en az 15, en çok 60 gündür. Kuponlar Pay Piyasasında işlem görür."
İDDİA: "Rüçhan hakkı kullanım süresi en az 90 gündür. Kuponlar tezgahüstü piyasada işlem görür."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "Rüçhan hakkı süresi en az 90 gündür"
2. "Kuponlar tezgahüstü piyasada işlem görür"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "DİKKAT: İddiada 1 Çelişki (süre 90 gün) ve 1 Bilgi Yokluğu vardır; bağlamca DESTEKLENEN HİÇBİR BİLGİ YOKTUR. Desteklenen hiçbir olgu yokken bir iddia ASLA partially_supported olamaz. Karar kesinlikle contradicted'dır. Model A haklıdır.",
  "favored_model": "Model A",
  "final_decision": "contradicted"
}
```

[EMSAL 5 - Bilgi Yokluğu / Semantik Yüklem Kuralı]
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
  "reasoning": "Bağlam FAST sisteminden bahsetse de ödemenin geri çevrilip çevrilemeyeceği eylemine/yüklemine dair hiçbir bilgi içermemektedir. Çelişki yoktur, yüklem doğrulanmamaktadır. Bu nedenle karar unverifiable olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "unverifiable"
}
```

[EMSAL 6 - Anlamsal ve Çatı Eşdeğerliği: Edilgen / Etken Yapılar]
BAĞLAM: "İnternet abonelik fesih bildiriminin ulaşmasından itibaren abonelik en geç yedi gün içinde sona erdirilir."
İDDİA: "İşletmeci fesih bildiriminden sonra feshi en geç yedi gün içinde tamamlar."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "İşletmeci fesih bildiriminden sonra feshi en geç yedi gün içinde tamamlar"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): supported
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "Mevzuatta feshin 'sona erdirilmesi' yükümlülüğü zaten işletmeciye aittir. Cümlenin edilgen ya da etken kurulmuş olması anlam farkı veya bilgi eksikliği yaratmaz. İddia bağlam tarafından tam desteklenmektedir. Model A haklıdır.",
  "favored_model": "Model A",
  "final_decision": "supported"
}
```
"""


def build_v4_1_prompt(case: dict[str, Any]) -> str:
    context = case["context"]
    claim = case["claim"]
    k1_pred = case["k1_pred"]
    k2_pred = case["k2_pred"]

    atoms_list = case.get("k2_atoms", [])
    if atoms_list:
        atoms_str = "\n".join(
            [f'{i+1}. "{a.get("atom", a.get("claim_atom", ""))}"' for i, a in enumerate(atoms_list)]
        )
    else:
        atoms_str = f'1. "{claim}"'

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
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek eylem/bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir önerme yer alıyorsa bu etiket ZORUNLUDUR. (Bir iddiada hem doğru hem zıt bir parça varsa asla contradicted deme, partially_supported seç!).
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve en az bir açık zıtlık/çelişki varsa seçilir. DİKKAT: İddiada 1 çelişen parça ve 1 bilgi yokluğu varsa (ve hiç doğru parça yoksa) karar partially_supported DEĞİL, contradicted olmalıdır!
4. unverifiable: Bağlamda önermelere dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

*** ÇOK ÖNEMLİ: SEMANTİK YÜKLEM VE EYLEM KURALI ***
- Bir cümlenin sadece öznesinin veya kavram adının bağlamda geçmesi o cümlenin "desteklenen parçası" SAYILMAZ!
- Desteklenen bir parçadan söz edebilmek için, özneye yüklenen eylemin/özelliğin/hükmün de bağlamda açıkça doğrulanması gerekir.
- Eğer iddiadaki önermelerin özneleri bağlamda geçiyor fakat iddia edilen eylemler/hükümler bağlamda yer almıyorsa, karar kesinlikle partially_supported DEĞİL, 'unverifiable' OLMALIDIR!
- Etken ve edilgen çatı arasındaki eşdeğerlikleri ("sona erdirilir = işletmeci sona erdirir") ve sayısal eşanlamlıları ("15 dakika = çeyrek saat") tam desteklenmiş kabul et.

Lütfen ÖNCE bağlamdaki kanıtı ve ayrıştırılmış önermelerin yüklemlerini/eylemlerini adım adım analiz et, ARDINDAN kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Önce bağlamdaki kanıtı ve önermelerin eylemlerini tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
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
        # Robust regex fallback parser (recovers truncated JSON like tfb_ex_0165)
        lowered = cleaned.lower()
        found = "unverifiable"
        # Check explicit final_decision match first
        m = re.search(r'"final_decision"\s*:\s*"?(supported|partially_supported|contradicted|unverifiable)', lowered)
        if m:
            found = m.group(1)
        else:
            for lbl in ["partially_supported", "unverifiable", "contradicted", "supported"]:
                if f'"{lbl}"' in lowered or f"'{lbl}'" in lowered:
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
        "X-OpenRouter-Title": "TR-FactBench K3-V4.1 Semantic Judge",
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

    ROOT = Path(".")
    K2 = ROOT / "k2_nli"

    cases_path = K2 / "data/processed/arbitration/arbitration_cases_123.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(cases)} arbitration disagreement cases.")

    out_dir = K2 / "reports/experiments/K3-V4-1-PURE-SEMANTIC-LLAMA70B-v1"
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

    print("\n" + "=" * 70)
    print("STARTING K3 V4.1 PURE SEMANTIC INFERENCE (NO PROBABILITIES)")
    print("=" * 70)

    for i, case in enumerate(cases, 1):
        eid = case["example_id"]
        gold = case["gold_label"]

        if eid in existing_preds:
            res_item = existing_preds[eid]
            results.append(res_item)
            if res_item["judge_correct"]:
                correct_count += 1
            status_icon = "[OK]" if res_item["judge_correct"] else "[X]"
            print(f"[{i:03d}/{len(cases)}] {status_icon} {eid} (Cached) -> Judge: {res_item['judge_decision']} | Gold: {gold}")
            continue

        prompt = build_v4_1_prompt(case)

        try:
            resp_json, lat = call_openrouter(prompt, api_key)
            choice = resp_json["choices"][0]
            raw_text = choice["message"]["content"]

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

            time.sleep(0.4)

        except Exception as e:
            print(f"[{i:03d}/{len(cases)}] [ERR] {eid}: {e}")
            raise

    acc = correct_count / len(cases)
    print("\n" + "=" * 70)
    print("V4.1 ARBITRATION RUN COMPLETED")
    print(f"Total Disagreement Cases: {len(cases)}")
    print(f"K3 V4.1 Correct Decisions: {correct_count} / {len(cases)} ({acc:.2%})")
    print("=" * 70)


if __name__ == "__main__":
    main()
