#!/usr/bin/env python3
"""
65_run_ood_medical_case_study.py
Executes an end-to-end Out-of-Distribution (OOD) Case Study on 16 Alzheimer clinical claims.
Evaluates:
- Component 1: ELECTRA-TR Base
- Component 2: Gemma-4 QLoRA Atomizer + mDeBERTa-v3 Soft-Prob NLI
- Component 3: Llama-3.3-70B Chain-of-Thought Meta-Judge (for disagreements)
- Full Cascading Hybrid Pipeline
"""
from __future__ import annotations

import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from dotenv import load_dotenv
from peft import PeftModel
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path("atomizer/v2").resolve()))

from atomizer_runtime import LocalAtomizer

LABEL_MAP = {0: "supported", 1: "partially_supported", 2: "contradicted", 3: "unverifiable"}
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_LENGTH = 512

# OpenRouter
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
JUDGE_MODEL = "meta-llama/llama-3.3-70b-instruct"

# Precedents for CoT Judge
FEWSHOT_PRECEDENTS = """EMSAL KARARLAR (ÖNCEKİ MAHKEME İÇTİHATLARI):

[EMSAL 1 - İki parçalı doğru iddia]
BAĞLAM: "Alışverişlerde işyeri bir FAST-TR Karekod oluşturabilir. Müşteri bu karekodu mobil bankacılık uygulamasından okutarak FAST ödemesini başlatır."
İDDİA: "Alışverişte müşteri, işyerinin oluşturduğu karekodu mobil uygulamasından okutarak FAST ödemesi başlatabilir."
MODEL A'NIN KARARI: supported
MODEL B'NİN KARARI: supported (Atom 1: "işyeri karekod oluşturabilir" -> entailed, Atom 2: "müşteri ödeme başlatabilir" -> entailed)
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
MODEL A'NIN KARARI: contradicted (Gerekçe: Zatürre tanısı bağlamda yoktur, yanlıştır)
MODEL B'NİN KARARI: partially_supported (Atom 1: "Sarı-yeşil balgam alevlenmede görülebilir" -> entailed, Atom 2: "Zatürre tanısını kesinleştirir" -> not_in_context)
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
MODEL A'NIN KARARI: contradicted (Gerekçe: Bağlam farklı modeller olduğunu söylüyor)
MODEL B'NİN KARARI: partially_supported (Atom 1: "Ödeme iste servisi vardır" -> entailed, Atom 2: "Tek bir model vardır" -> contradicted)
HAKEM KARARI:
```json
{
  "reasoning": "İddianın ana hükmü bağlamdaki 'farklı modeller vardır' bilgisiyle doğrudan zıttır. Model B'nin iddiayı zoraki parçalayarak destek çıkarması hatalıdır; iddiada doğrulanabilir bir destek yoktur. Model A haklıdır.",
  "favored_model": "Model A",
  "final_decision": "contradicted"
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
  "reasoning": "Bağlam ödemenin geri çevrilip çevrilemeyeceğine dair hiçbir bilgi içermemektedir. Çelişki yoktur, sadece bilgi eksikliği vardır. Bu nedenle karar unverifiable olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "unverifiable"
}
```
"""


def call_cot_judge(
    context: str,
    claim: str,
    k1_pred: str,
    k2_pred: str,
    k2_atoms: list[dict[str, Any]],
    api_key: str,
) -> dict[str, Any]:
    atoms_str = "\n".join([f"- Atom {i+1}: \"{a['atom']}\" -> Sonuç: {a['label']}" for i, a in enumerate(k2_atoms)])
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

MODEL A'NIN ANALİZİ (Bileşen 1: Doğrudan Doğrulayıcı):
- Karar: {k1_pred}
- Açıklama: Cümlenin tamamını bağlamla birlikte tek seferde değerlendirmiştir.

MODEL B'NİN ANALİZİ (Bileşen 2: Atomik NLI Doğrulayıcı):
- Karar: {k2_pred}
- Ayrıştırdığı Önermeler ve NLI Sonuçları:
{atoms_str}

ETİKET KURALLARI VE DİKKAT EDİLECEK HUSUSLAR:
1. supported: İddiadaki BÜTÜN bilgiler bağlam tarafından açıkça doğrulanmaktadır. İddiada hiçbir yanlış veya bağlam dışı parça yoksa bu etiket ZORUNLUDUR. Sırf Model B iddiayı atomlara böldü diye yapay bir kusur arama!
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir bilgi yer alıyorsa bu etiket ZORUNLUDUR. Sakın sırf yanlış parça var diye contradicted seçme!
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda iddiaya dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

Lütfen ÖNCE bağlamdaki kanıtı adım adım düşünerek analiz et, ARDINDAN kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Önce bağlamdaki kanıtı ve modellerin analizini tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}}
```"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
        "X-OpenRouter-Title": "TR-FactBench OOD Alzheimer Case Study Judge",
    }
    payload = {
        "model": JUDGE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 400,
    }

    resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=90, verify=False)
    resp.raise_for_status()
    raw_content = resp.json()["choices"][0]["message"]["content"].strip()

    # Parse JSON
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
    json_str = match.group(1) if match else raw_content
    start, end = json_str.find("{"), json_str.rfind("}")
    if start >= 0 and end > start:
        json_str = json_str[start : end + 1]

    data = json.loads(json_str)
    decision = str(data.get("final_decision", "")).strip().lower()
    if decision not in LABELS:
        decision = k1_pred
    return {
        "final_decision": decision,
        "favored_model": data.get("favored_model", "Neither"),
        "reasoning": data.get("reasoning", ""),
        "raw_response": raw_content,
    }


def main() -> None:
    print(f"=== OOD ALZHEIMER MEDICAL CASE STUDY (16 Claims) ===")
    print(f"Device: {DEVICE.upper()}")

    # 1. Load API Key
    load_dotenv("tr-factbench-v0.1.0-preview/.env")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found!")

    # 2. Load Models
    # K1 ELECTRA
    k1_adapter = Path("tr-factbench-v0.1.0-preview/runs/ablations/H1_DROP10_S45_ABLATION_run/ckpt/electra-base-turkish-cased-discriminator/multidomain/seed_45/best_model")
    k1_base_name = "dbmdz/electra-base-turkish-cased-discriminator"
    print("\n[1/3] Loading Component 1 (ELECTRA-TR)...")
    k1_tokenizer = AutoTokenizer.from_pretrained(str(k1_adapter), local_files_only=True, use_fast=True)
    k1_base = AutoModelForSequenceClassification.from_pretrained(k1_base_name, num_labels=4, ignore_mismatched_sizes=True, local_files_only=True)
    k1_model = PeftModel.from_pretrained(k1_base, str(k1_adapter), local_files_only=True)
    k1_model.eval().to(DEVICE)
    print("Component 1 ready!")

    # K2 mDeBERTa
    k2_name = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
    print("\n[2/3] Loading Component 2 NLI (mDeBERTa-v3)...")
    k2_tokenizer = AutoTokenizer.from_pretrained(k2_name, local_files_only=True)
    k2_model = AutoModelForSequenceClassification.from_pretrained(k2_name, local_files_only=True)
    k2_model.eval().to(DEVICE)
    k2_id2label = {int(k): v.lower() for k, v in k2_model.config.id2label.items()}
    print("Component 2 NLI ready!")

    # K2 Gemma Atomizer
    atomizer_path = Path("atomizer/v2/outputs/google_gemma_4_e2b_it_final_adapter")
    print("\n[3/3] Loading Gemma-4 QLoRA Atomizer...")
    atomizer = LocalAtomizer(atomizer_path, base_model="google/gemma-4-e2b-it")
    print("Atomizer ready!")

    # 3. Load Dataset
    data_file = Path("k2_nli/data/processed/ood_case_study/alzheimer_ood_16.jsonl")
    cases = [json.loads(l) for l in data_file.read_text("utf-8").splitlines() if l.strip()]
    print(f"\nLoaded {len(cases)} OOD Alzheimer cases.")

    out_dir = Path("k2_nli/reports/experiments/OOD-ALZHEIMER-CASE-STUDY-v1")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "results.jsonl"
    if out_file.exists():
        out_file.unlink()

    results = []

    print("\n" + "=" * 80)
    print("STARTING END-TO-END PIPELINE INFERENCE ON 16 OOD CASES")
    print("=" * 80)

    for idx, c in enumerate(cases, 1):
        cid = c["id"]
        ctx = c["context"]
        q = c["question"]
        clm = c["claim"]
        gold = c["gold_label"]

        print(f"\n[{idx:02d}/16] ID: {cid} | Gold: {gold}")
        print(f"İDDİA: {clm}")

        # K1
        t_a = f"[CONTEXT] {ctx.strip()}"
        t_b = f"[QUESTION] {q.strip()} [CLAIM] {clm.strip()}"
        enc1 = k1_tokenizer(t_a, t_b, max_length=MAX_LENGTH, truncation=True, padding=True, return_tensors="pt")
        enc1 = {k: v.to(DEVICE) for k, v in enc1.items()}
        with torch.no_grad():
            logits1 = k1_model(**enc1).logits
        p1 = torch.softmax(logits1, dim=-1).squeeze().cpu().tolist()
        k1_pred = LABEL_MAP[int(torch.argmax(logits1, dim=-1).item())]
        k1_conf = float(max(p1))
        print(f"  -> K1 Pred: {k1_pred} (Güven: %{k1_conf*100:.1f})")

        # K2 Atomizer
        atom_out = atomizer.predict(clm)
        atoms = atom_out.atoms
        print(f"  -> Gemma Atomizer ({len(atoms)} atom): {atoms}")

        # K2 NLI
        atom_res = []
        pe_list, pn_list, pc_list = [], [], []
        for a in atoms:
            enc2 = k2_tokenizer(ctx.strip(), a.strip(), max_length=MAX_LENGTH, truncation=True, padding=True, return_tensors="pt")
            enc2 = {k: v.to(DEVICE) for k, v in enc2.items()}
            with torch.no_grad():
                logits2 = k2_model(**enc2).logits
            p2 = torch.softmax(logits2, dim=-1).squeeze().cpu().tolist()
            p_dict = {k2_id2label[i]: float(p2[i]) for i in range(len(p2))}
            best_lbl = max(p_dict, key=p_dict.get)
            pe_list.append(p_dict.get("entailment", 0.0))
            pn_list.append(p_dict.get("neutral", 0.0))
            pc_list.append(p_dict.get("contradiction", 0.0))
            atom_res.append({"atom": a, "label": best_lbl, "probs": p_dict})

        # Aggregation
        atom_labels = [x["label"] for x in atom_res]
        if len(atom_labels) == 0:
            k2_pred = "unverifiable"
        elif all(l == "entailment" for l in atom_labels):
            k2_pred = "supported"
        elif "entailment" in atom_labels:
            k2_pred = "partially_supported"
        else:
            avg_e = sum(pe_list) / max(len(pe_list), 1)
            avg_n = sum(pn_list) / max(len(pn_list), 1)
            avg_c = sum(pc_list) / max(len(pc_list), 1)
            if avg_c > max(avg_e, avg_n):
                k2_pred = "contradicted"
            else:
                k2_pred = "unverifiable"
        print(f"  -> K2 NLI Pred: {k2_pred} (Atom Etiketleri: {atom_labels})")

        # Decision Routing
        if k1_pred == k2_pred:
            final_pred = k1_pred
            source = "Consensus (Direct Acceptance)"
            reasoning = "K1 ve K2 yerel modelleri hemfikir."
            favored = "Both"
            print(f"  -> [DOĞRUDAN UZLAŞMA]: {final_pred} (Hakeme gidilmedi)")
        else:
            print(f"  -> [UYUŞMAZLIK]: K1={k1_pred} vs K2={k2_pred} -> CoT Hakeme gidiliyor...")
            j_out = call_cot_judge(ctx, clm, k1_pred, k2_pred, atom_res, api_key)
            final_pred = j_out["final_decision"]
            source = "Meta-Judge (CoT Llama-3.3-70B)"
            reasoning = j_out["reasoning"]
            favored = j_out["favored_model"]
            print(f"  -> [HAKEM KARARI]: {final_pred} (Tercih: {favored})")
            print(f"     Gerekçe: {reasoning}")

        is_corr = (final_pred == gold)
        print(f"  ==> NIHAI KARAR: {final_pred} | ALTIN ETIKET: {gold} | {'[DOGRU]' if is_corr else '[YANLIS]'}")

        rec = {
            "id": cid,
            "claim": clm,
            "gold_label": gold,
            "k1_pred": k1_pred,
            "k1_correct": k1_pred == gold,
            "atoms": atoms,
            "atom_results": atom_res,
            "k2_pred": k2_pred,
            "k2_correct": k2_pred == gold,
            "is_consensus": k1_pred == k2_pred,
            "final_pred": final_pred,
            "final_correct": is_corr,
            "decision_source": source,
            "favored_model": favored,
            "reasoning": reasoning,
        }
        results.append(rec)
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Final Metrics
    y_true = [r["gold_label"] for r in results]
    y_k1 = [r["k1_pred"] for r in results]
    y_k2 = [r["k2_pred"] for r in results]
    y_hyb = [r["final_pred"] for r in results]

    acc_k1 = accuracy_score(y_true, y_k1)
    acc_k2 = accuracy_score(y_true, y_k2)
    acc_hyb = accuracy_score(y_true, y_hyb)

    f1_k1 = f1_score(y_true, y_k1, labels=LABELS, average="macro", zero_division=0)
    f1_k2 = f1_score(y_true, y_k2, labels=LABELS, average="macro", zero_division=0)
    f1_hyb = f1_score(y_true, y_hyb, labels=LABELS, average="macro", zero_division=0)

    n_cons = sum(1 for r in results if r["is_consensus"])

    print("\n" + "=" * 80)
    print("OOD ALZHEIMER CASE STUDY NİHAİ METRİKLER (16 Vaka)")
    print("=" * 80)
    print(f"K1 Tek Başına (ELECTRA-TR)       : {sum(r['k1_correct'] for r in results)}/16 (%{acc_k1*100:.1f}) | Macro-F1: {f1_k1*100:.1f}%")
    print(f"K2 Tek Başına (Gemma+mDeBERTa)   : {sum(r['k2_correct'] for r in results)}/16 (%{acc_k2*100:.1f}) | Macro-F1: {f1_k2*100:.1f}%")
    print(f"KADEMELİ HİBRİT BORU HATTI (Önerilen) : {sum(r['final_correct'] for r in results)}/16 (%{acc_hyb*100:.1f}) | Macro-F1: {f1_hyb*100:.1f}%")
    print(f"Doğrudan Uzlaşma Oranı           : {n_cons}/16 (%{n_cons/16*100:.1f})")
    print(f"Hakeme Giden Uyuşmazlık Sayısı   : {16 - n_cons}/16 (%{(16-n_cons)/16*100:.1f})")
    print("=" * 80)


if __name__ == "__main__":
    main()
