#!/usr/bin/env python3
"""
demo_hybrid_pipeline.py
========================
TR-FactBench Uçtan Uca Hibrit Doğrulama Hattı İnteraktif Demo Arayüzü (Gradio)
Bileşenler:
  - Bileşen 1 (K1): ELECTRA-TR Cross-Encoder (Global Sequence Classifier)
  - Bileşen 2 (K2): Atomik Ayrıştırma & mDeBERTa-v3 NLI (Önerme Düzeyli Doğrulama)
  - Bileşen 3 (K3): Hibrit Karar & Llama-3.3-70B Emsalli Meta-Hakem (Arbitrasyon)
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
urllib3.disable_warnings()
import torch
from dotenv import load_dotenv
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Gradio import
import gradio as gr

# Offline mode settings
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Load API key for Component 3 Judge
ENV_PATHS = [
    Path("tr-factbench-v0.1.0-preview/.env"),
    Path("../tr-factbench-v0.1.0-preview/.env"),
    Path(".env"),
]
for ep in ENV_PATHS:
    if ep.exists():
        load_dotenv(ep)
        break

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ── SABİTLER VE ETİKET TANIMLARI ─────────────────────────────────────────────
LABEL_MAP = {0: "supported", 1: "partially_supported", 2: "contradicted", 3: "unverifiable"}
LABEL_TR = {
    "supported": "✅ Destekleniyor (Supported)",
    "partially_supported": "⚠️ Kısmen Destekleniyor (Partially Supported)",
    "contradicted": "❌ Çelişiyor (Contradicted)",
    "unverifiable": "❔ Doğrulanamaz (Unverifiable)",
}
LABEL_COLOR = {
    "supported": "#28a745",
    "partially_supported": "#fd7e14",
    "contradicted": "#dc3545",
    "unverifiable": "#6c757d",
}
ATOM_NLI_TR = {
    "entailment": "✅ Doğrulanıyor (Entailed)",
    "contradiction": "❌ Çelişiyor (Contradicted)",
    "neutral": "❔ Bağlam Dışı (Not in Context)",
}
ATOM_NLI_COLOR = {
    "entailment": "#28a745",
    "contradiction": "#dc3545",
    "neutral": "#6c757d",
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_LENGTH = 512

# ── MODEL YÜKLEME (BAŞLANGIÇTA BİR KEZ) ───────────────────────────────────────
print(f"[{DEVICE.upper()}] Modeller yükleniyor...")

# 1. K1 ELECTRA-TR
K1_ADAPTER = Path(
    "tr-factbench-v0.1.0-preview/runs/ablations/"
    "H1_DROP10_S45_ABLATION_run/ckpt/"
    "electra-base-turkish-cased-discriminator/multidomain/seed_45/best_model"
)
K1_BASE = "dbmdz/electra-base-turkish-cased-discriminator"

print("[1/2] K1 (ELECTRA-TR) yükleniyor...")
k1_tokenizer = AutoTokenizer.from_pretrained(str(K1_ADAPTER), local_files_only=True, use_fast=True)
k1_base = AutoModelForSequenceClassification.from_pretrained(
    K1_BASE,
    num_labels=4,
    ignore_mismatched_sizes=True,
    local_files_only=True,
)
k1_model = PeftModel.from_pretrained(k1_base, str(K1_ADAPTER), local_files_only=True)
k1_model.eval().to(DEVICE)
print("K1 ELECTRA-TR hazır!")

# 2. K2 mDeBERTa-v3 NLI
K2_MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
print("[2/3] K2 (mDeBERTa-v3 NLI) yükleniyor...")
k2_tokenizer = AutoTokenizer.from_pretrained(K2_MODEL_ID, local_files_only=True)
k2_model = AutoModelForSequenceClassification.from_pretrained(K2_MODEL_ID, local_files_only=True)
k2_model.eval().to(DEVICE)
print("K2 mDeBERTa-v3 hazır!")

# mDeBERTa Label Mapping: {0: 'entailment', 1: 'neutral', 2: 'contradiction'}
k2_id2label = {int(k): v.lower() for k, v in k2_model.config.id2label.items()}

# 3. K2 Gemma-4 QLoRA Atomizer (Tezimizin Eğitilmiş Önerme Ayrıştırıcısı)
sys.path.insert(0, str(Path("atomizer/v2").resolve()))
from atomizer_runtime import LocalAtomizer

GEMMA_ATOMIZER_PATH = Path("atomizer/v2/outputs/google_gemma_4_e2b_it_final_adapter")
print("[3/3] K2 (Gemma-4 QLoRA Atomizer) yükleniyor...")
local_atomizer = None
try:
    if GEMMA_ATOMIZER_PATH.exists():
        local_atomizer = LocalAtomizer(
            adapter_path=str(GEMMA_ATOMIZER_PATH),
            base_model="google/gemma-4-E2B-it",
            max_new_tokens=180,
        )
        print("K2 Gemma-4 QLoRA Atomizer GPU üzerinde hazır!")
    else:
        print(f"Uyarı: Gemma-4 adaptör yolu bulunamadı ({GEMMA_ATOMIZER_PATH}).")
except Exception as e:
    print(f"Gemma-4 Atomizer yükleme uyarısı: {e}")

print("Tüm K1, K2 ve Atomizer yerel modelleri başarıyla yüklendi!")


# ── YARDIMCI VE ÇIKARIM FONKSİYONLARI ─────────────────────────────────────────

def predict_k1(context: str, question: str, claim: str) -> dict[str, Any]:
    text_a = f"[CONTEXT] {context.strip()}"
    text_b = f"[QUESTION] {question.strip()} [CLAIM] {claim.strip()}"
    enc = k1_tokenizer(text_a, text_b, max_length=MAX_LENGTH, truncation=True, padding=True, return_tensors="pt")
    enc = {k: v.to(DEVICE) for k, v in enc.items()}
    with torch.no_grad():
        logits = k1_model(**enc).logits
    probs = torch.softmax(logits, dim=-1).squeeze().cpu().tolist()
    pred_id = int(torch.argmax(logits, dim=-1).item())
    pred_label = LABEL_MAP[pred_id]
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return {
        "pred_label": pred_label,
        "confidence": float(max(probs)),
        "probs": {LABEL_MAP[i]: float(probs[i]) for i in range(4)},
    }


ATOMIZER_SYSTEM_PROMPT = (
    "Türkçe bir iddiayı bağımsız doğrulanabilir atomik önermelere ayır. "
    "Her atom tek başına anlaşılır olmalı. Ortak özne, nesne veya tamlayıcı "
    "ikinci bir önermede düşürülmüşse, onu iddianın kendi içindeki bilgiden yeniden kur. "
    "Özneleri veya baş ögeleri yeniden kurarken kelime eksiltme, kısaltma veya kırpma yapma; "
    "iddiadaki isim ve sıfat tamlamalarını tam olarak koru. "
    "Her atom dilbilgisel olarak eksiksiz ve öznesi açık bir cümle olmalıdır. "
    "Yeni bilgi ekleme. Olumsuzluk, koşul, modalite, sayı, zaman, karşılaştırma ve "
    "kapsam ifadelerini koru. Koşullu tek bir önerme sırf birden fazla fiil içeriyor diye "
    "bölünmemelidir. İddia zaten atomikse değiştirmeden tek atom döndür. "
    "BİR cümlenin içindeki yan cümleler veya sıfat tamlamaları ayrı atom YAPILMAZ; "
    "yalnızca 've', 'ayrıca', 'öte yandan', 'bununla birlikte', 'ancak', 'fakat', "
    "noktalı virgül veya açık nokta gibi koordinasyon sınırlarında böl. "
    'Yalnızca {"atoms": ["..."]} biçiminde geçerli JSON üret.'
)


def extract_claim_atoms(claim: str) -> tuple[list[str], str]:
    """
    Bileşen 2 (K2) 1. Aşama: Eğitilmiş yerel Gemma-4 QLoRA Atomizer ile
    iddianın doğrulanabilir bağımsız atomik önermelere ayrıştırılması.
    """
    text = claim.strip()
    if not text:
        return [], "Boş Girdi"

    # 1. Öncelikli Yol: Eğitilmiş Yerel Gemma-4 QLoRA Atomizer
    if local_atomizer is not None:
        try:
            res = local_atomizer.predict(text)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            if res.json_valid and res.atoms:
                return res.atoms, "Eğitilmiş Yerel Gemma-4 QLoRA Atomizer (GPU)"
        except Exception as e:
            print(f"Gemma-4 Atomizer Çıkarım Hatası: {e}")

    # 2. Yedek Yol: Gemini 2.5 Flash API
    if OPENROUTER_API_KEY:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
            "X-OpenRouter-Title": "TR-FactBench Atomizer",
        }
        payload = {
            "model": "google/gemini-2.5-flash",
            "messages": [
                {"role": "system", "content": ATOMIZER_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps({"claim": text}, ensure_ascii=False)},
            ],
            "temperature": 0.0,
            "max_tokens": 300,
        }
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                verify=False,
                timeout=25,
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
                cand = match.group(1) if match else content
                data = json.loads(cand)
                atoms = data.get("atoms", [])
                if isinstance(atoms, list) and atoms and all(isinstance(a, str) and a.strip() for a in atoms):
                    return [a.strip() for a in atoms], "Google Gemini 2.5 Flash (Yedek LLM)"
        except Exception as e:
            print(f"Gemini Atomizer Hatası: {e}")

    return [text], "Doğrudan İddia (Fallback)"


def predict_k2_nli(context: str, atoms: list[str]) -> dict[str, Any]:
    atom_results = []
    prob_e_list, prob_n_list, prob_c_list = [], [], []

    for idx, atom in enumerate(atoms):
        enc = k2_tokenizer(context.strip(), atom.strip(), max_length=MAX_LENGTH, truncation=True, padding=True, return_tensors="pt")
        enc = {k: v.to(DEVICE) for k, v in enc.items()}
        with torch.no_grad():
            logits = k2_model(**enc).logits
        probs = torch.softmax(logits, dim=-1).squeeze().cpu().tolist()

        prob_dict = {k2_id2label[i]: float(probs[i]) for i in range(len(probs))}
        pred_atom_label = max(prob_dict, key=prob_dict.get)

        prob_e = prob_dict.get("entailment", 0.0)
        prob_n = prob_dict.get("neutral", 0.0)
        prob_c = prob_dict.get("contradiction", 0.0)

        prob_e_list.append(prob_e)
        prob_n_list.append(prob_n)
        prob_c_list.append(prob_c)

        atom_results.append({
            "atom": atom,
            "label": pred_atom_label,
            "probs": {"entailment": prob_e, "neutral": prob_n, "contradiction": prob_c},
        })

    # Soft-Probability Average Toplulaştırma
    labels = [a["label"] for a in atom_results]
    if all(l == "entailment" for l in labels):
        k2_pred = "supported"
    elif "entailment" in labels:
        k2_pred = "partially_supported"
    else:
        avg_e = sum(prob_e_list) / max(len(prob_e_list), 1)
        avg_n = sum(prob_n_list) / max(len(prob_n_list), 1)
        avg_c = sum(prob_c_list) / max(len(prob_c_list), 1)
        if avg_c > max(avg_e, avg_n):
            k2_pred = "contradicted"
        elif avg_n > max(avg_e, avg_c):
            k2_pred = "unverifiable"
        else:
            k2_pred = "unverifiable"

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return {
        "pred_label": k2_pred,
        "atoms": atom_results,
    }


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


def call_live_meta_judge(
    context: str,
    claim: str,
    k1_pred: str,
    k2_pred: str,
    k2_atoms: list[dict[str, Any]],
    judge_model: str = "meta-llama/llama-3.3-70b-instruct",
) -> dict[str, Any]:
    if not OPENROUTER_API_KEY:
        return {
            "final_decision": k1_pred,
            "favored_model": "Model A (Fallback - No API Key)",
            "reasoning": "OpenRouter API anahtarı bulunamadığı için varsayılan K1 kararı uygulandı.",
            "latency": 0.0,
        }

    # Neutral atomic propositions without intermediate NLI labels
    if k2_atoms:
        atoms_str = "\n".join([f"{i+1}. \"{a['atom']}\"" for i, a in enumerate(k2_atoms)])
    else:
        atoms_str = f"1. \"{claim}\""

    prompt = f"""Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı bilirkişi modeli uzlaşamamıştır. İddianın bağımsız olarak ayrıştırılmış atomik önermelerini ve bilirkişi modellerinin kararlarını inceleyerek hakem kararını ver.

{FEWSHOT_PRECEDENTS}

--------------------------------------------------
ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
'''{context}'''

İDDİA:
'''{claim}'''

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

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
        "X-OpenRouter-Title": f"TR-FactBench Live Demo Judge ({judge_model})",
    }
    payload = {
        "model": judge_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 400,
    }

    t0 = time.time()
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            verify=False,
            timeout=60,
        )
        lat = round(time.time() - t0, 2)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            json_str = match.group(1) if match else content
            data = json.loads(json_str)
            dec = data.get("final_decision", "").strip().lower()
            if dec not in ["supported", "partially_supported", "contradicted", "unverifiable"]:
                dec = k1_pred
            return {
                "final_decision": dec,
                "favored_model": data.get("favored_model", "Model A"),
                "reasoning": data.get("reasoning", "Gerekçe üretilmedi."),
                "latency": lat,
            }
        else:
            err_msg = f"API Hatası (HTTP {resp.status_code}): {resp.text[:150]}"
            print(f"Meta-Judge {err_msg}")
            return {
                "final_decision": k1_pred,
                "favored_model": "Model A (Hata durumunda fallback)",
                "reasoning": err_msg,
                "latency": lat,
            }
    except Exception as e:
        err_msg = f"API İstek Hatası: {str(e)}"
        print(f"Meta-Judge {err_msg}")
        return {
            "final_decision": k1_pred,
            "favored_model": "Model A (Hata durumunda fallback)",
            "reasoning": err_msg,
            "latency": 0.0,
        }


def run_full_pipeline(
    context: str,
    question: str,
    claim: str,
    judge_model: str = "meta-llama/llama-3.3-70b-instruct",
) -> tuple[str, str, str, str]:
    if not context.strip() or not claim.strip():
        empty_msg = "<div style='color:red;padding:10px;'>Lütfen Bağlam ve İddia alanlarını doldurun.</div>"
        return empty_msg, "", "", ""

    t_start = time.time()

    # 1. K1 ELECTRA-TR
    k1_res = predict_k1(context, question, claim)
    k1_label = k1_res["pred_label"]
    k1_conf = k1_res["confidence"] * 100
    k1_color = LABEL_COLOR[k1_label]
    k1_tr = LABEL_TR[k1_label]

    # K1 HTML
    prob_bars = "".join(
        [
            f"<div style='margin:3px 0;font-size:0.85em'>{LABEL_TR[lbl]}: <b>%{val*100:.1f}</b>"
            f"<div style='background:#e9ecef;border-radius:4px;height:8px;overflow:hidden'>"
            f"<div style='background:{LABEL_COLOR[lbl]};width:{val*100:.1f}%;height:100%'></div></div></div>"
            for lbl, val in k1_res["probs"].items()
        ]
    )
    k1_html = f"""
    <div style='border:1.5px solid {k1_color}; border-radius:12px; padding:18px; margin-bottom:12px; background:#ffffff; box-shadow:0 2px 10px rgba(0,0,0,0.04); min-height:240px'>
      <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:10px; margin-bottom:12px'>
        <span style='font-size:1em; color:#1e293b; font-weight:700'>BİLEŞEN 1: DOĞRUDAN DOĞRULAYICI (K1)</span>
        <span style='font-size:0.8em; background:#e0e7ff; color:#3730a3; padding:3px 10px; border-radius:12px; font-weight:600'>dbmdz/electra-base-turkish (~12ms)</span>
      </div>
      <div style='font-size:1.4em; font-weight:800; color:{k1_color}; margin:6px 0'>{k1_tr}</div>
      <div style='font-size:0.9em; color:#64748b; margin-bottom:12px'>Model Güven Skoru: <b>%{k1_conf:.1f}</b></div>
      <div style='background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #edf2f7'>
        <div style='font-size:0.85em; font-weight:700; color:#475569; margin-bottom:8px'>4 Sınıflı Olasılık Dağılımı:</div>
        {prob_bars}
      </div>
    </div>
    """

    # 2. K2 Atomik Doğrulama (Gemma-4 QLoRA Atomizer + mDeBERTa-v3 NLI)
    atoms, atomizer_src = extract_claim_atoms(claim)
    k2_res = predict_k2_nli(context, atoms)
    k2_label = k2_res["pred_label"]
    k2_color = LABEL_COLOR[k2_label]
    k2_tr = LABEL_TR[k2_label]

    atom_cards = ""
    for i, a in enumerate(k2_res["atoms"]):
        lbl = a["label"]
        c = ATOM_NLI_COLOR[lbl]
        atom_cards += f"""
        <div style='background:#ffffff; border-left:4px solid {c}; padding:10px 14px; margin:8px 0; border-radius:6px; font-size:0.9em; box-shadow:0 1px 4px rgba(0,0,0,0.05); border:1px solid #edf2f7; border-left-width:4px'>
          <b>Önerme {i+1}:</b> "{a['atom']}"<br>
          <div style='margin-top:4px'>
            <span style='color:{c}; font-weight:700'>{ATOM_NLI_TR[lbl]}</span>
            <span style='color:#64748b; font-size:0.85em; margin-left:8px'>[Doğrulama: %{a['probs']['entailment']*100:.0f} | Çelişki: %{a['probs']['contradiction']*100:.0f} | Nötr: %{a['probs']['neutral']*100:.0f}]</span>
          </div>
        </div>
        """

    k2_html = f"""
    <div style='border:1.5px solid {k2_color}; border-radius:12px; padding:18px; margin-bottom:12px; background:#ffffff; box-shadow:0 2px 10px rgba(0,0,0,0.04); min-height:240px'>
      <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:10px; margin-bottom:12px'>
        <span style='font-size:1em; color:#1e293b; font-weight:700'>BİLEŞEN 2: ÖNERME-DÜZEYLİ NLI (K2)</span>
        <span style='font-size:0.8em; background:#e0e7ff; color:#3730a3; padding:3px 10px; border-radius:12px; font-weight:600'>Atomizer: {atomizer_src}</span>
      </div>
      <div style='font-size:1.4em; font-weight:800; color:{k2_color}; margin:6px 0'>{k2_tr}</div>
      <div style='font-size:0.9em; color:#64748b; margin-bottom:12px'>Ayrıştırılan Önerme Sayısı: <b>{len(atoms)} atomik iddia</b> &nbsp;|&nbsp; Model: <b>mDeBERTa-v3 Soft-Prob (~28ms)</b></div>
      <div style='background:#f8fafc; padding:10px; border-radius:8px; border:1px solid #edf2f7; max-height:280px; overflow-y:auto'>
        {atom_cards}
      </div>
    </div>
    """

    # 3. K3 Karar Mekanizması & Hakem
    is_consensus = (k1_label == k2_label)
    model_name_map = {
        "meta-llama/llama-3.3-70b-instruct": "Llama-3.3-70B-Instruct (Meta)",
        "qwen/qwen-2.5-72b-instruct": "Qwen-2.5-72B-Instruct (Alibaba)",
        "openai/gpt-4o-mini": "GPT-4o-mini (OpenAI)",
    }
    disp_name = model_name_map.get(judge_model, judge_model)

    if is_consensus:
        final_label = k1_label
        final_color = LABEL_COLOR[final_label]
        final_tr = LABEL_TR[final_label]
        k3_html = f"""
        <div style='border:2px solid #28a745; background:#f4fbf6; border-radius:12px; padding:18px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.03)'>
          <div style='display:flex; justify-content:space-between; align-items:center'>
            <span style='font-size:1.05em; color:#155724; font-weight:700'>✅ DOĞRUDAN UZLAŞMA BÖLGESİ</span>
            <span style='font-size:0.8em; background:#d4edda; color:#155724; padding:3px 10px; border-radius:12px; font-weight:600'>0 LLM API Çağrısı &bull; $0.00 Maliyet</span>
          </div>
          <div style='font-size:1.3em; font-weight:800; margin:10px 0; color:#155724'>
            K1 ve K2 Modelleri Hemfikir: {k1_tr}
          </div>
          <p style='margin:0; font-size:0.95em; color:#1e7e34; line-height:1.5'>
            İki farklı yapay zeka mimarisi (Doğrudan Doğrulayıcı ve Önerme Düzeyli NLI) bağımsız olarak aynı sonuca vardı. 
            Altın test kümesindeki <b>%94.13 uzlaşma güvenilirliği</b> nedeniyle dış LLM hakemine ihtiyaç kalmadan doğrudan ve anında onaylandı.
          </p>
          <div style='font-size:0.85em; color:#666; margin-top:10px'>İşlem Gecikmesi: <b>~35ms</b> &nbsp;|&nbsp; Güvenilirlik: <b>%94.13 (337/358 Altın Test Örneği)</b></div>
        </div>
        """
        judge_info = "Konsensüs sağlandı; meta-hakeme ihtiyaç duyulmadı."
    else:
        # Disagreement -> Call Selected Meta-Judge
        judge_res = call_live_meta_judge(context, claim, k1_label, k2_label, k2_res["atoms"], judge_model=judge_model)
        final_label = judge_res["final_decision"]
        final_color = LABEL_COLOR[final_label]
        final_tr = LABEL_TR[final_label]
        favored = judge_res["favored_model"]
        reason = judge_res["reasoning"]
        lat = judge_res["latency"]

        k3_html = f"""
        <div style='border:2px solid #fd7e14; background:#fffbf6; border-radius:12px; padding:18px; margin-bottom:14px; box-shadow:0 2px 10px rgba(0,0,0,0.04)'>
          <div style='display:flex; justify-content:space-between; align-items:center'>
            <span style='font-size:1.05em; color:#d96504; font-weight:700'>⚖️ AYRIŞMA TESPİT EDİLDİ &mdash; BİLEŞEN 3: {disp_name.upper()} HAKEM DEVREDE</span>
            <span style='font-size:0.8em; background:#ffe8d6; color:#a73a00; padding:3px 10px; border-radius:12px; font-weight:600'>Emsal Destekli Meta-Hakem</span>
          </div>
          <div style='display:flex; gap:24px; margin:12px 0; font-size:0.95em'>
            <div><b>Model A (K1 Bütüncül):</b> <span style='color:{LABEL_COLOR[k1_label]}; font-weight:bold'>{k1_tr}</span></div>
            <div><b>Model B (K2 Atomik):</b> <span style='color:{LABEL_COLOR[k2_label]}; font-weight:bold'>{k2_tr}</span></div>
          </div>
          <div style='background:#ffffff; border-left:5px solid #fd7e14; padding:12px 16px; margin:10px 0; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,0.05)'>
            <div style='font-size:1em; font-weight:700; color:#d96504'>Hakemin Nihai Hükmü: {favored}</div>
            <div style='font-size:0.95em; margin-top:6px; color:#2d3748; line-height:1.5'><b>Gerekçeli Karar:</b> {reason}</div>
          </div>
          <div style='font-size:0.85em; color:#64748b'>Hakem Modeli: <b>{disp_name}</b> | Muhakeme Süresi: <b>{lat}s</b> | Emsal İçtihat Başarımı: <b>%75.83</b></div>
        </div>
        """
        judge_info = f"Hakem Tercihi: {favored} | Gerekçe: {reason}"

    # Final Banner (Full Width, Modern Hero Card)
    total_time = round(time.time() - t_start, 2)
    final_banner = f"""
    <div style='background:linear-gradient(135deg, {final_color}10 0%, {final_color}22 100%); border:2px solid {final_color}; border-radius:12px; padding:22px; text-align:center; margin-bottom:16px; box-shadow:0 4px 12px rgba(0,0,0,0.04)'>
      <div style='font-size:0.9em; color:#555; font-weight:700; letter-spacing:1.5px; text-transform:uppercase'>NİHAİ HİBRİT DOĞRULAMA KARARI</div>
      <div style='font-size:2.2em; font-weight:800; color:{final_color}; margin:6px 0'>{final_tr}</div>
      <div style='font-size:0.95em; color:#444; margin-top:6px'>
        Karar Mekanizması: <b>{'K1 & K2 Doğrudan Konsensüs (%94.13 Başarım - 0 LLM Maliyeti)' if is_consensus else f'{disp_name} Meta-Hakem Kararı ({favored})'}</b>
        &nbsp;&bull;&nbsp; Toplam Çıkarım Süresi: <b>{total_time}s</b>
      </div>
    </div>
    """

    return final_banner, k1_html, k2_html, k3_html



CUSTOM_CSS = """
#verify-btn {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #3b82f6 100%) !important;
    color: #ffffff !important;
    font-size: 1.15em !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 28px !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

#verify-btn:hover {
    transform: translateY(-2.5px) !important;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.55), 0 4px 10px rgba(0, 0, 0, 0.12) !important;
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 50%, #2563eb 100%) !important;
}

#verify-btn:active {
    transform: translateY(2px) scale(0.98) !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.45) !important;
    transition: transform 0.05s ease !important;
}

#verify-btn[disabled], #verify-btn.disabled, button[disabled]#verify-btn {
    opacity: 0.7 !important;
    cursor: not-allowed !important;
    pointer-events: none !important;
    background: linear-gradient(135deg, #64748b 0%, #475569 100%) !important;
    box-shadow: 0 2px 8px rgba(71, 85, 105, 0.3) !important;
    transform: none !important;
    filter: grayscale(0.3) !important;
}
"""

def set_btn_loading():
    return gr.update(value="⏳ Analiz Ediliyor ve Doğrulanıyor... Lütfen Bekleyin", interactive=False)

def restore_btn_ready():
    return gr.update(value="🚀 Hibrit Doğrulama Hattını Çalıştır (K1 + K2 + K3)", interactive=True)


# ── GRADIO ARAYÜZ TASARIMI ───────────────────────────────────────────────────
with gr.Blocks(title="TR-FactBench Hibrit Doğrulama Hattı", css=CUSTOM_CSS) as demo:
    gr.Markdown("""
    # 🛡️ TR-FactBench: Türkçe Olgusal Doğrulama Hibrit Hattı
    **Yüksek Lisans Tezi Araştırma Prototipi** | Burdur Mehmet Akif Ersoy Üniversitesi | Danışman: Prof. Dr. Serkan Ballı  
    *Bileşen 1: ELECTRA-TR (110M) &nbsp;|&nbsp; Bileşen 2: mDeBERTa-v3 Önerme NLI (278M) &nbsp;|&nbsp; Bileşen 3: Llama-3.3-70B Meta-Hakem*
    """)

    with gr.Tabs():
        # ── TAB 1: CANLI ÇIKARIM ──────────────────────────────────────────────
        with gr.Tab("🔬 Canlı Hibrit Doğrulama (Live Pipeline)"):
            with gr.Group():
                gr.Markdown("### 📝 1. Girdi Bilgileri (Kanıt Dokümanı ve Doğrulanacak İfade)")
                with gr.Row():
                    with gr.Column(scale=6):
                        context_in = gr.Textbox(
                            label="📄 BAĞLAM (Kanıt Dokümanı / Resmi Kaynak Metin)",
                            lines=7,
                            placeholder="Kaynak resmi metni, raporu veya kanıtı buraya yapıştırın...",
                        )
                    with gr.Column(scale=6):
                        claim_in = gr.Textbox(
                            label="💬 İDDİA (Doğrulanacak LLM Yanıtı / İfade)",
                            lines=3,
                            placeholder="Doğruluğu denetlenecek tekil veya bileşik iddiayı buraya yazın...",
                        )
                        question_in = gr.Textbox(
                            label="❓ Soru (İsteğe bağlı)",
                            lines=1,
                            placeholder="İddia hangi soru bağlamında üretildi?",
                        )
                        judge_model_dropdown = gr.Dropdown(
                            label="⚖️ Meta-Hakem Modeli (Bileşen 3 - Uyuşmazlık Çözücü)",
                            choices=[
                                ("Meta Llama-3.3-70B-Instruct (Önerilen - %75.8 Uyuşmazlık Başarımı)", "meta-llama/llama-3.3-70b-instruct"),
                                ("Alibaba Qwen-2.5-72B-Instruct (%70.0 Uyuşmazlık Başarımı)", "qwen/qwen-2.5-72b-instruct"),
                                ("OpenAI GPT-4o-mini (%63.3 Uyuşmazlık Başarımı)", "openai/gpt-4o-mini"),
                            ],
                            value="meta-llama/llama-3.3-70b-instruct",
                        )

                verify_btn = gr.Button(
                    "🚀 Hibrit Doğrulama Hattını Çalıştır (K1 + K2 + K3)",
                    variant="primary",
                    size="lg",
                    elem_id="verify-btn",
                )

            gr.Markdown("---")

            with gr.Group():
                gr.Markdown("### 🎯 2. Hibrit Çıkarım ve Doğrulama Raporu")
                # 1. Büyük Nihai Karar Banner'ı (Tam Genişlik)
                final_out = gr.HTML(label="Nihai Karar")

                # 2. K1 ve K2 Yan Yana Geniş Kartlar (Her biri %50)
                with gr.Row():
                    with gr.Column(scale=6):
                        k1_out = gr.HTML(label="Bileşen 1 (K1)")
                    with gr.Column(scale=6):
                        k2_out = gr.HTML(label="Bileşen 2 (K2)")

                # 3. K3 Karar Mekanizması / Meta-Hakem (Tam Genişlik)
                k3_out = gr.HTML(label="Bileşen 3 (K3 Hakem)")

            verify_btn.click(
                fn=set_btn_loading,
                outputs=[verify_btn],
            ).then(
                fn=run_full_pipeline,
                inputs=[context_in, question_in, claim_in, judge_model_dropdown],
                outputs=[final_out, k1_out, k2_out, k3_out],
                api_name="run_pipeline",
            ).then(
                fn=restore_btn_ready,
                outputs=[verify_btn],
            )

        # ── TAB 2: BENCHMARK GEZGİNİ ──────────────────────────────────────────
        with gr.Tab("📚 TR-FactBench Gold 480 Veri Gezgini"):
            gr.Markdown("""
            ### 478 Altın Test Örneğinde Modellerin Kararları
            Aşağıdaki butona tıklayarak Gold 480 test kümesindeki 120 çelişki örneğini ve 358 konsensüs örneğini inceleyebilirsiniz.
            """)
            gold_btn = gr.Button("📂 Altın Test Kümesi Örneklerini Yükle")
            gold_display = gr.HTML()

            def load_gold_samples():
                arb_path = Path("reports/experiments/K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1/arbitration_predictions_123.jsonl")
                if not arb_path.exists():
                    arb_path = Path("k2_nli/reports/experiments/K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1/arbitration_predictions_123.jsonl")
                if not arb_path.exists():
                    return "<div>Veri dosyası bulunamadı.</div>"
                records = [json.loads(l) for l in arb_path.read_text(encoding="utf-8").splitlines() if l.strip()][:15]
                html = "<table border='1' cellpadding='6' style='border-collapse:collapse;width:100%;font-size:0.85em'>"
                html += "<tr style='background:#f0f0f0'><th>ID</th><th>Alan</th><th>Altın Etiket</th><th>K1</th><th>K2</th><th>Hakem (Llama-70B)</th><th>Tercih</th><th>Sonuç</th></tr>"
                for r in records:
                    ok = "✅" if r["judge_correct"] else "❌"
                    html += f"<tr><td><b>{r['example_id']}</b></td><td>{r['domain']}</td><td>{LABEL_TR.get(r['gold_label'], r['gold_label'])}</td><td>{r['k1_pred']}</td><td>{r['k2_pred']}</td><td><b>{r['judge_decision']}</b></td><td>{r['favored_model']}</td><td>{ok}</td></tr>"
                html += "</table><p style='color:#666;font-size:0.8em;margin-top:6px'>* İlk 15 ayrışma örneği gösterilmektedir.</p>"
                return html

            gold_btn.click(fn=load_gold_samples, outputs=gold_display)

        # ── TAB 3: TEZ KARŞILAŞTIRMA MATRİSİ ──────────────────────────────────
        with gr.Tab("📊 Tez Karşılaştırma Matrisi & Metrikler"):
            gr.Markdown("""
            ### 1. Ana Hibrit Hat vs Tekil Modeller (478 Altın Test Örneği)

            | Sistem / Model | Türü | 120 Ayrışmada Doğruluk | Uçtan Uca Doğruluk (478) | Macro-F1 | MCC | Açıklama |
            |---|---|:---:|:---:|:---:|:---:|---|
            | **K1 (ELECTRA-TR Base)** | Tekil Verifier | %50.83 (61/120) | %83.26 (398/478) | 0.8316 | 0.7802 | Göreve özgü doğrudan 4-sınıflı verifier |
            | **K2 (mDeBERTa-v3 Soft-Prob)** | Tekil NLI Hattı | %39.17 (47/120) | %80.33 (384/478) | 0.8059 | 0.7405 | Atomik önerme NLI hattı |
            | **Hibrit + Zero-Shot Llama-70B** | Emsalsiz Meta-Hakem | %47.50 (57/120) | %82.43 (394/478) | 0.8262 | 0.7723 | Zero-shot aşırı çelişki yanlılığı |
            | **Hibrit + Few-Shot Llama-70B** | **Emsalli Meta-Hakem (K3)** | **%75.83 (91/120)** | **%89.54 (428/478)** | **0.8966** | **0.8628** | **4 emsal içtihadıyla eğitilmiş canlı hakem** |
            | *Teorik Üst Sınır (Oracle)* | Tavan | %90.00 (108/120) | %93.10 (445/478) | - | - | K1 veya K2'den birinin bildiği tavan |

            ---

            ### 2. K3 Meta-Hakem Model Ablasyon Analizi (Farklı LLM Aileleri Karşılaştırması)
            *Aynı 4 emsal kararlı hakem protokolü altında 120 uyuşmazlık vakasında test edilmiştir:*

            | Meta-Hakem Modeli | Sağlayıcı / Mimari | Uyuşmazlık Doğruluğu (120) | Tam Hibrit Doğruluk (478) | Hibrit Macro-F1 | Hibrit MCC | McNemar vs K1 ($p$) | McNemar vs K2 ($p$) | Ortalama Gecikme | 120 Vaka Maliyeti |
            |---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
            | **Llama-3.3-70B-Instruct** | Meta (Açık Ağırlıklı) | **%75.83 (91/120)** | **%89.54 (428/478)** | **0.8966** | **0.8628** | **p = 0.00064** | **p = 1.34e-12** | 2.84s | $0.0360 USD |
            | **Qwen-2.5-72B-Instruct** | Alibaba (Açık, Çok Dilli) | **%70.00 (84/120)** | **%88.08 (421/478)** | **0.8821** | **0.8450** | **p = 0.00954** | **p = 3.02e-09** | 4.57s | $0.0922 USD |
            | **GPT-4o-mini** | OpenAI (Ticari / Kapalı) | **%63.33 (76/120)** | **%86.40 (413/478)** | **0.8666** | **0.8259** | p = 0.07693 | **p = 2.49e-05** | 2.41s | $0.0296 USD |
            | **Gemma-4-E2B-it (Yerel)** | Google (Küçük Model, 4-bit) | %50.00 (60/120) | %83.05 (397/478) | 0.8294 | 0.7840 | p = 1.0000 | p = 0.1340 | 8.07s | $0.00 (Yerel) |

            ---

            #### 📌 Temel Bilimsel Çıkarımlar:
            1. **Model-Agnostik Doğrulama:** Yöntem tek bir modele bağımlı değildir; 3 büyük model ailesinde de K1 ve K2'yi istatistiksel olarak geride bırakmıştır.
            2. **Açık Ağırlıklı 70B Modellerin Üstünlüğü:** Açık kaynaklı Llama-3.3-70B (%75.83) ve Qwen-2.5-72B (%70.00), ticari GPT-4o-mini'yi (%63.33) belirgin şekilde geride bırakmıştır.
            3. **Konsensüs Alanı Tasarrufu:** 358 vakada (%74.9) iki model doğrudan uzlaşmakta ve doğruluk **%94.13** seviyesine çıkmaktadır (0 API çağrısı, ~35ms).
            """)

if __name__ == "__main__":
    demo.launch(server_port=7865, inbrowser=False, show_error=True)
