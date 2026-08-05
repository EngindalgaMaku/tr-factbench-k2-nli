#!/usr/bin/env python3
"""
Atom-Level NLI Pipeline
=======================
Ana veri setinden claim–context örnekleri alır ve iki aşamalı analiz yapar:

  Aşama 1 — Claim-level NLI:
    XLM-RoBERTa-Large-XNLI ile tam claim → {entailment, neutral, contradiction}

  Aşama 2 — Atom-level NLI:
    Gemma-4-E2B-it + LoRA ile claim → atomlar
    Her atom için XLM-R → NLI tahmini
    Atom tahminlerini birleştirme stratejileri:
      - majority: çoğunluk oyu
      - worst:    en kötü atom (contradiction > neutral > entailment)
      - mean_prob: ortalama olasılık vektörü

  Aşama 3 — 5-sınıf hizalama analizi:
    NLI tahminlerini gold_label (5 sınıf) ile karşılaştırır.

Kullanım:
    python nli_zeroshot_v2/run_atom_nli_pipeline.py \\
        --data data/hls_converted/test.jsonl \\
        --n 100 \\
        --output nli_zeroshot_v2/outputs/atom_pipeline

    # Tüm veri seti
    python nli_zeroshot_v2/run_atom_nli_pipeline.py \\
        --data data/hls_converted/test.jsonl \\
        --output nli_zeroshot_v2/outputs/atom_pipeline
"""

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import pipeline as hf_pipeline

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ["HF_HUB_OFFLINE"] = "1"

# ── Sabitler ──────────────────────────────────────────────────────────────────
NLI_MODEL    = "joeddav/xlm-roberta-large-xnli"
ATOMIZER_BASE    = "google/gemma-4-E2B-it"
ATOMIZER_ADAPTER = Path("atomizer/v2/outputs/google_gemma_4_E2B_it_final_adapter")

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
    '{"atoms": ["..."]} biçiminde geçerli JSON üret.'
)

NLI_LABELS = ["entailment", "neutral", "contradiction"]
LABEL2IDX  = {l: i for i, l in enumerate(NLI_LABELS)}

# 5-sınıf → 3-sınıf NLI eşlemesi (referans için)
GOLD5_TO_NLI3 = {
    "supported":                "entailment",
    "contradicted":             "contradiction",
    "unsupported":              "neutral",
    "insufficient_information": "neutral",
    "partially_supported":      "partial",   # özel durum
}

# ── Global cache ───────────────────────────────────────────────────────────────
_nli_pipe     = None
_atomizer     = None


# ── NLI yardımcıları ──────────────────────────────────────────────────────────

def get_nli_pipe():
    global _nli_pipe
    if _nli_pipe is not None:
        return _nli_pipe
    print(f"NLI modeli yükleniyor: {NLI_MODEL}")
    device = 0 if torch.cuda.is_available() else -1
    _nli_pipe = hf_pipeline(
        "text-classification",
        model=NLI_MODEL,
        device=device,
        dtype=torch.float32,   # XLM-R-large için FP32
    )
    print("NLI modeli hazır.")
    return _nli_pipe


def normalize_nli_label(raw: str) -> str:
    raw = raw.lower()
    if "entail" in raw:
        return "entailment"
    if "contradict" in raw:
        return "contradiction"
    if "neutral" in raw:
        return "neutral"
    raise ValueError(f"Tanınmayan NLI etiketi: {raw}")


def nli_predict(premise: str, hypothesis: str) -> dict:
    """Tek bir premise–hypothesis çifti için NLI tahmini döndürür."""
    pipe = get_nli_pipe()
    out  = pipe({"text": premise, "text_pair": hypothesis}, top_k=None)
    prob_dict = {normalize_nli_label(item["label"]): item["score"] for item in out}
    probs = [prob_dict.get(l, 0.0) for l in NLI_LABELS]
    s = sum(probs)
    probs = [p / s for p in probs]
    pred_idx = int(np.argmax(probs))
    return {
        "label":                NLI_LABELS[pred_idx],
        "prob_entailment":      round(probs[0], 4),
        "prob_neutral":         round(probs[1], 4),
        "prob_contradiction":   round(probs[2], 4),
        "confidence":           round(max(probs), 4),
    }


# ── Atomizer yardımcıları ─────────────────────────────────────────────────────

def get_atomizer():
    global _atomizer
    if _atomizer is not None:
        return _atomizer
    import re
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel

    if not ATOMIZER_ADAPTER.exists():
        raise FileNotFoundError(f"Atomizer adaptörü bulunamadı: {ATOMIZER_ADAPTER}")

    print(f"Atomizer yükleniyor: {ATOMIZER_BASE}")
    tokenizer_src = ATOMIZER_ADAPTER if (ATOMIZER_ADAPTER / "tokenizer_config.json").exists() else ATOMIZER_BASE
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_src), use_fast=True, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    base = AutoModelForCausalLM.from_pretrained(
        ATOMIZER_BASE,
        quantization_config=quant_config,
        device_map="cuda",
        torch_dtype=compute_dtype,
        local_files_only=True,
    )
    model = PeftModel.from_pretrained(base, str(ATOMIZER_ADAPTER), is_trainable=False)
    model.eval()
    model.config.use_cache = True
    _atomizer = (tokenizer, model)
    print("Atomizer hazır.")
    return _atomizer


def extract_atoms_from_json(text: str):
    import re, json as _json
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        obj = _json.loads(cleaned[start: end + 1])
    except _json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or "atoms" not in obj:
        return None
    atoms = obj.get("atoms")
    if not isinstance(atoms, list) or not atoms:
        return None
    if not all(isinstance(a, str) and a.strip() for a in atoms):
        return None
    return [a.strip() for a in atoms]


@torch.inference_mode()
def atomize(claim: str) -> tuple[list[str] | None, str]:
    """Claim'i atomlara ayırır. (atoms, raw_output) döndürür."""
    tokenizer, model = get_atomizer()
    user_content = f"{ATOMIZER_SYSTEM_PROMPT}\n\n{json.dumps({'claim': claim}, ensure_ascii=False)}"
    messages = [{"role": "user", "content": user_content}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    eos_ids = [tokenizer.eos_token_id]
    for extra in ["<end_of_turn>", "<turn|>", "<|eot_id|>", "<|im_end|>"]:
        try:
            tok_id = tokenizer.convert_tokens_to_ids(extra)
            if tok_id is not None and not isinstance(tok_id, str) and tok_id != tokenizer.unk_token_id:
                eos_ids.append(tok_id)
        except Exception:
            pass
    if hasattr(tokenizer, "eot_token") and tokenizer.eot_token:
        try:
            tok_id = tokenizer.convert_tokens_to_ids(tokenizer.eot_token)
            if tok_id is not None and not isinstance(tok_id, str) and tok_id != tokenizer.unk_token_id:
                eos_ids.append(tok_id)
        except Exception:
            pass
    eos_ids = list(set(eos_ids))

    output = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=eos_ids,
    )
    generated = output[0, inputs["input_ids"].shape[1]:]
    raw = tokenizer.decode(generated, skip_special_tokens=True).strip()
    atoms = extract_atoms_from_json(raw)
    return atoms, raw


# ── Atom tahminlerini birleştirme ─────────────────────────────────────────────

def aggregate_atom_predictions(atom_preds: list[dict]) -> dict:
    """
    Atom NLI tahminlerini 3 stratejiyle birleştirir.
    atom_preds: [{"label": ..., "prob_entailment": ..., ...}, ...]
    """
    if not atom_preds:
        return {}

    labels = [p["label"] for p in atom_preds]
    probs  = np.array([[p["prob_entailment"], p["prob_neutral"], p["prob_contradiction"]]
                       for p in atom_preds])

    # Majority vote
    cnt = Counter(labels)
    majority_label = cnt.most_common(1)[0][0]

    # Worst-case: contradiction > neutral > entailment
    priority = {"contradiction": 2, "neutral": 1, "entailment": 0}
    worst_label = max(labels, key=lambda l: priority[l])

    # Mean probability
    mean_probs = probs.mean(axis=0)
    mean_label = NLI_LABELS[int(np.argmax(mean_probs))]

    return {
        "majority":      majority_label,
        "worst":         worst_label,
        "mean_prob":     mean_label,
        "mean_prob_vec": {
            "entailment":    round(float(mean_probs[0]), 4),
            "neutral":       round(float(mean_probs[1]), 4),
            "contradiction": round(float(mean_probs[2]), 4),
        },
        "atom_label_counts": dict(cnt),
        "n_atoms": len(atom_preds),
    }


# ── Ana pipeline ──────────────────────────────────────────────────────────────

def run_pipeline(data: list[dict], output_dir: Path, skip_atomizer: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pred_path = output_dir / "predictions.jsonl"

    # Resume: daha önce işlenmiş örnek ID'lerini yükle
    done_ids: set[str] = set()
    results: list[dict] = []
    if pred_path.exists():
        with open(pred_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    done_ids.add(r["example_id"])
                    results.append(r)
        if done_ids:
            print(f"  Resume: {len(done_ids)} örnek zaten işlenmiş, atlanıyor.")

    t0 = time.time()
    # Append modunda aç
    fout = open(pred_path, "a", encoding="utf-8")

    try:
        for i, ex in enumerate(data):
            ex_id   = ex.get("example_id") or ex.get("id") or f"ex_{i}"
            if ex_id in done_ids:
                continue

            context = ex["context"]
            claim   = ex["claim"]
            gold    = ex.get("gold_label", "")

            # ── Aşama 1: Claim-level NLI ──────────────────────────────────────
            claim_nli = nli_predict(context, claim)

            # ── Aşama 2: Atom-level NLI ───────────────────────────────────────
            atom_results = []
            atoms        = None
            atomizer_raw = ""
            atom_agg     = {}

            if not skip_atomizer:
                atoms, atomizer_raw = atomize(claim)
                if atoms:
                    for atom in atoms:
                        atom_nli = nli_predict(context, atom)
                        atom_results.append({
                            "atom":  atom,
                            **atom_nli,
                        })
                    atom_agg = aggregate_atom_predictions(atom_results)

            # ── Kayıt ─────────────────────────────────────────────────────────
            record = {
                "example_id":     ex_id,
                "domain":         ex.get("domain", ""),
                "gold_label":     gold,
                "gold_nli3":      GOLD5_TO_NLI3.get(gold, "unknown"),
                "claim":          claim,
                "context_len":    len(context),
                "claim_nli":      claim_nli,
                "n_atoms":        len(atoms) if atoms else 0,
                "atomizer_valid": atoms is not None,
                "atoms":          atoms or [],
                "atom_nli":       atom_results,
                "atom_agg":       atom_agg,
                "atomizer_raw":   atomizer_raw,
            }
            results.append(record)
            # Anında diske yaz (resume için)
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            fout.flush()

            processed = len(results)
            if processed % 10 == 0 or processed == len(data):
                elapsed = time.time() - t0
                print(f"  {processed}/{len(data)} — {elapsed:.1f}s")

    finally:
        fout.close()

    print(f"\nTahminler kaydedildi: {pred_path} ({len(results)} örnek)")

    # ── Analiz ────────────────────────────────────────────────────────────────
    analyze_results(results, output_dir)


def analyze_results(results: list[dict], output_dir: Path) -> None:
    """Claim-level ve atom-level NLI tahminlerini 5-sınıf gold label ile karşılaştırır."""
    from sklearn.metrics import classification_report, confusion_matrix

    gold5_labels  = [r["gold_label"] for r in results]
    gold3_labels  = [r["gold_nli3"]  for r in results]
    claim_preds   = [r["claim_nli"]["label"] for r in results]

    # Sadece 3-sınıf eşlenebilen örnekler (partial hariç)
    valid_mask = [g != "partial" for g in gold3_labels]
    valid_gold3  = [g for g, v in zip(gold3_labels, valid_mask) if v]
    valid_claim  = [p for p, v in zip(claim_preds, valid_mask) if v]

    print(f"\n{'='*65}")
    print(f"  ANALİZ — {len(results)} örnek ({sum(valid_mask)} 3-sınıf eşlenebilir)")
    print(f"{'='*65}")

    # Claim-level
    if valid_gold3:
        report = classification_report(
            valid_gold3, valid_claim,
            target_names=NLI_LABELS,
            output_dict=True,
            zero_division=0,
        )
        macro_f1 = report["macro avg"]["f1-score"]
        accuracy = report["accuracy"]
        print(f"\n  Claim-level NLI (gold 3-sınıf):")
        print(f"    Macro-F1 : {macro_f1*100:.2f}%")
        print(f"    Accuracy : {accuracy*100:.2f}%")
        for cls in NLI_LABELS:
            r = report[cls]
            print(f"    {cls:15s}: F1={r['f1-score']*100:.2f}  P={r['precision']*100:.2f}  R={r['recall']*100:.2f}  n={int(r['support'])}")

    # 5-sınıf gold → claim NLI dağılımı
    print(f"\n  Gold 5-sınıf → Claim NLI tahmin dağılımı:")
    gold5_to_pred = defaultdict(Counter)
    for r in results:
        gold5_to_pred[r["gold_label"]][r["claim_nli"]["label"]] += 1
    for gold5 in ["supported", "contradicted", "unsupported", "insufficient_information", "partially_supported"]:
        if gold5 in gold5_to_pred:
            dist = dict(gold5_to_pred[gold5])
            total = sum(dist.values())
            print(f"    {gold5:30s} (n={total}): {dist}")

    # Atom-level analiz
    atom_results_valid = [r for r in results if r["atomizer_valid"] and r["atom_agg"]]
    if atom_results_valid:
        print(f"\n  Atom-level NLI ({len(atom_results_valid)} atomize edilmiş örnek):")
        avg_atoms = np.mean([r["n_atoms"] for r in atom_results_valid])
        print(f"    Ortalama atom sayısı: {avg_atoms:.2f}")

        for strategy in ["majority", "worst", "mean_prob"]:
            strat_preds = [r["atom_agg"].get(strategy) for r in atom_results_valid if r["atom_agg"].get(strategy)]
            strat_gold  = [r["gold_nli3"] for r in atom_results_valid if r["atom_agg"].get(strategy) and r["gold_nli3"] != "partial"]
            strat_preds_filtered = [p for r, p in zip(atom_results_valid, strat_preds)
                                    if r["gold_nli3"] != "partial" and r["atom_agg"].get(strategy)]

            if strat_gold and strat_preds_filtered:
                rep = classification_report(
                    strat_gold, strat_preds_filtered,
                    target_names=NLI_LABELS,
                    output_dict=True,
                    zero_division=0,
                )
                print(f"\n    Strateji: {strategy}")
                print(f"      Macro-F1 : {rep['macro avg']['f1-score']*100:.2f}%")
                print(f"      Accuracy : {rep['accuracy']*100:.2f}%")

        # Atom sayısı dağılımı
        atom_counts = Counter(r["n_atoms"] for r in atom_results_valid)
        print(f"\n    Atom sayısı dağılımı: {dict(sorted(atom_counts.items()))}")

        # Partially_supported örneklerde atom dağılımı
        partial_results = [r for r in atom_results_valid if r["gold_label"] == "partially_supported"]
        if partial_results:
            print(f"\n    partially_supported örneklerde atom NLI dağılımı ({len(partial_results)} örnek):")
            for r in partial_results[:5]:
                atom_labels = [a["label"] for a in r["atom_nli"]]
                print(f"      {r['example_id']}: {atom_labels}")

    # Özet metrikleri kaydet
    summary = {
        "n_total":          len(results),
        "n_valid_3class":   sum(valid_mask),
        "n_atomized":       len(atom_results_valid),
        "claim_level": {
            "macro_f1": report["macro avg"]["f1-score"] if valid_gold3 else None,
            "accuracy": report["accuracy"] if valid_gold3 else None,
        } if valid_gold3 else {},
        "gold5_to_claim_nli": {k: dict(v) for k, v in gold5_to_pred.items()},
    }

    with open(output_dir / "analysis.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n  Analiz kaydedildi: {output_dir / 'analysis.json'}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Atom-Level NLI Pipeline")
    parser.add_argument("--data",    required=True, help="JSONL veri dosyası (context, claim, gold_label)")
    parser.add_argument("--output",  default="nli_zeroshot_v2/outputs/atom_pipeline", help="Çıktı klasörü")
    parser.add_argument("--n",       type=int, default=None, help="Kaç örnek işlenecek (None=tümü)")
    parser.add_argument("--seed",    type=int, default=42,   help="Örnekleme seed'i")
    parser.add_argument("--domain",  default=None, help="Sadece bu domain (medical/finance/legal)")
    parser.add_argument("--gold",    default=None, help="Sadece bu gold_label")
    parser.add_argument("--skip-atomizer", action="store_true", help="Atomizer'ı atla, sadece claim-level NLI")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Atom-Level NLI Pipeline")
    print(f"Veri   : {args.data}")
    print(f"Çıktı  : {args.output}")

    # Veri yükle
    data = []
    with open(args.data, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    print(f"Toplam : {len(data)} örnek")

    # Filtrele
    if args.domain:
        data = [ex for ex in data if ex.get("domain", "") == args.domain]
        print(f"Domain filtresi ({args.domain}): {len(data)} örnek")
    if args.gold:
        data = [ex for ex in data if ex.get("gold_label", "") == args.gold]
        print(f"Gold filtresi ({args.gold}): {len(data)} örnek")

    # Örnekle
    if args.n and args.n < len(data):
        rng = np.random.default_rng(args.seed)
        idx = rng.choice(len(data), size=args.n, replace=False)
        data = [data[i] for i in sorted(idx)]
        print(f"Örneklendi: {len(data)} örnek (seed={args.seed})")

    # Gold dağılımı
    dist = Counter(ex.get("gold_label", "") for ex in data)
    print(f"Gold dağılımı: {dict(dist)}")

    output_dir = Path(args.output)
    print(f"\nPipeline başlıyor...")
    run_pipeline(data, output_dir, skip_atomizer=args.skip_atomizer)


if __name__ == "__main__":
    main()