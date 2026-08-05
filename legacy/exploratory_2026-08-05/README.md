# NLI Verifier

Zero-shot NLI ile Türkçe claim/atom düzeyinde doğrulama bileşeni.

## Seçilen Model

**`joeddav/xlm-roberta-large-xnli`** — iki ayrı test setinde de en iyi performans.

## Sonuçlar

### Pilot Test (60 örnek, dengeli)

| Model | Macro-F1 | Accuracy |
|-------|----------|----------|
| XLM-RoBERTa-Large-XNLI | **%86.66** | **%86.67** |
| mDeBERTa-v3-base-mnli-xnli | %81.20 | %81.67 |
| mDeBERTa-v3-base-xnli-2mil7 | %76.12 | %76.67 |

### Source-Based Test (300 örnek, dengeli)

| Model | Macro-F1 | Accuracy |
|-------|----------|----------|
| XLM-RoBERTa-Large-XNLI | **%94.67** | **%94.67** |
| mDeBERTa-v3-base-mnli-xnli | %92.94 | %93.00 |
| mDeBERTa-v3-base-xnli-2mil7 | %91.28 | %91.33 |

**Alan bazlı (XLM-R, 300 örnek):**
| Alan | Macro-F1 | Accuracy |
|------|----------|----------|
| Medical | %95.99 | %96.00 |
| Finance | %95.02 | %95.00 |
| Legal | %93.00 | %93.00 |

### Atom-Level Pipeline (247 örnek, ana test seti)

| Strateji | Macro-F1 | Accuracy |
|----------|----------|----------|
| Claim-level | %83.80 | %83.92 |
| Atom worst-case | **%84.34** | **%84.42** |
| Atom majority | %83.80 | %83.92 |

## Kullanım

### Zero-Shot NLI Deneyleri (3 model)

```bash
# Pilot test (60 örnek)
python nli/run_nli_zeroshot_v2.py \
    --data nli/data/turkish_multidomain_nli_pilot_60_model_input_shuffled_seed42.jsonl \
    --review-csv nli/data/turkish_multidomain_nli_pilot_60_review.csv

# Source-based test (300 örnek)
python nli/run_nli_zeroshot_v2.py \
    --data nli/data/turkish_multidomain_nli_source_based_300_model_input_shuffled_seed42.jsonl \
    --review-csv nli/data/turkish_multidomain_nli_source_based_300_review.csv

# Sadece bir model
python nli/run_nli_zeroshot_v2.py --data <veri.jsonl> --exp NLI-C1

# Kaldığı yerden devam
python nli/run_nli_zeroshot_v2.py --data <veri.jsonl> --resume
```

### Atom-Level Pipeline

```bash
# Tam test seti (claim + atom NLI)
python nli/run_atom_nli_pipeline.py \
    --data data/hls_converted/test.jsonl \
    --output nli/outputs/atom_pipeline_full

# Sadece claim-level (hızlı)
python nli/run_atom_nli_pipeline.py \
    --data data/hls_converted/test.jsonl \
    --skip-atomizer \
    --output nli/outputs/claim_only

# Filtreli çalıştırma
python nli/run_atom_nli_pipeline.py \
    --data data/hls_converted/test.jsonl \
    --n 50 --domain medical
```

## Deney Matrisi

| ID | Model | Premise Modu |
|----|-------|-------------|
| NLI-A1 | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | context_only |
| NLI-A2 | aynı | question_context |
| NLI-B1 | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` | context_only |
| NLI-B2 | aynı | question_context |
| NLI-C1 | `joeddav/xlm-roberta-large-xnli` | context_only ← **Seçilen** |
| NLI-C2 | aynı | question_context |

> NLI formatındaki veri setlerinde (premise/hypothesis/label) `premise_mode` yok sayılır,
> sadece A1/B1/C1 çalışır.

## Veri Formatları

### NLI Formatı (doğrudan)
```json
{"id": "...", "domain": "medical", "difficulty": "easy",
 "premise": "Bağlam...", "hypothesis": "İddia...", "label": "entailment"}
```

### Hallucination Formatı (5-sınıf)
```json
{"context": "Bağlam...", "claim": "İddia...",
 "gold_label": "supported", "domain": "medical"}
```

## Etiket Dönüşümü (5→3 sınıf)

| Gold Label | NLI |
|------------|-----|
| supported | entailment |
| contradicted | contradiction |
| unsupported | neutral |
| insufficient_information | neutral |
| partially_supported | *atlanır* |

## Çıktı Yapısı

```
nli/outputs/
  NLI-A1/
    results.json        ← macro_f1, accuracy, ece, brier, nll, domain bazlı
    predictions.jsonl   ← örnek bazlı tahminler
    review_NLI-A1.csv   ← review CSV (deney ID önekli sütunlar)
  NLI-B1/ ...
  NLI-C1/ ...
  summary.json          ← tüm deneylerin özeti
  review_all_experiments.csv  ← birleşik review CSV
  atom_pipeline_full/
    predictions.jsonl   ← claim + atom NLI detayları
    analysis.json       ← özet metrikler
```

## Kritik Bulgular

1. **Neutral hataları:** XLM-R, bağlamda söylenmeyen ama alan bilgisiyle makul olan iddiaları
   entailment kabul ediyor. Bu, source-grounded doğrulama için kritik sınır.

2. **Yüksek güven + yanlış:** Bazı neutral hataları %99+ güvenle yapılıyor.
   "Güven yüksekse kabul et" stratejisi güvenli değil.

3. **Ensemble avantajı yok:** 3 modelin çoğunluk oyu (281/300 = %93.67),
   tek XLM-R'den (284/300 = %94.67) daha düşük.

4. **Atom dağılımı:** `partially_supported` örneklerde atomlar karışık
   (entailment + neutral/contradiction) — atom yaklaşımı bu sınıfı yakalamak için doğru yol.