# K3 Meta-Hakem Modeli Çoklu LLM Karşılaştırma ve Ablasyon Raporu

**Tarih:** 2026-10-03  
**Çalışma:** TR-FactBench Türkçe Olgusal Doğrulama Hibrit Hattı (K1 + K2 + K3)  
**Yazar:** Engin Dalga | Danışman: Prof. Dr. Serkan Ballı  
**Kurum:** Burdur Mehmet Akif Ersoy Üniversitesi  

---

## 1. Yönetici Özeti (Executive Summary)

Bu rapor, TR-FactBench 480 resmi altın test kümesi üzerinde Bütüncül Encoder (K1: ELECTRA-TR) ile Önerme Düzeyli Doğrulayıcı (K2: Gemma-4 QLoRA Atomizer + mDeBERTa-v3 NLI) arasındaki uyuşmazlıkları çözmek için tasarlanan **K3 Meta-Hakem (Meta-Arbitration)** mekanizmasının model-agnostik değerlendirmesini sunmaktadır.

Farklı LLM ailelerinden 4 farklı mimari (Meta Llama-3.3-70B, Alibaba Qwen-2.5-72B, OpenAI GPT-4o-mini ve yerel Google Gemma-4-E2B-it), aynı 4 emsal içtihadına dayalı `few-shot informed` hakem protokolü altında 120 uyuşmazlık vakasında ve 478 tam test örneğinde değerlendirilmiştir.

---

## 2. Ana Karşılaştırma Tablosu

| Meta-Hakem Modeli | Mimari & Sağlayıcı | Parametre | 120 Uyuşmazlık Doğruluğu | 478 Uçtan Uca Doğruluk | Macro-F1 | MCC | McNemar vs K1 ($p$) | McNemar vs K2 ($p$) | Ortalama Yanıt Süresi | 120 Vaka Maliyeti (USD) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Meta Llama-3.3-70B-Instruct** | Açık Ağırlıklı / Meta | 70B | **%75.83** (91/120) | **%89.54** (428/478) | **0.8966** | **0.8628** | **p = 0.00064** | **p = 1.34e-12** | 2.84s | $0.0360 |
| **Alibaba Qwen-2.5-72B-Instruct** | Açık Ağırlıklı / Alibaba | 72B | **%70.00** (84/120) | **%88.08** (421/478) | **0.8821** | **0.8450** | **p = 0.00954** | **p = 3.02e-09** | 4.57s | $0.0922 |
| **OpenAI GPT-4o-mini** | Kapalı Ticari / OpenAI | Hafif LLM | **%63.33** (76/120) | **%86.40** (413/478) | **0.8666** | **0.8259** | p = 0.07693 | **p = 2.49e-05** | 2.41s | $0.0296 |
| **Gemma-4-E2B-it (Yerel 4-bit)** | Yerel Küçük / Google | 2B | %50.00 (60/120) | %83.05 (397/478) | 0.8294 | 0.7840 | p = 1.0000 | p = 0.1340 | 8.07s | $0.00 (Yerel GPU) |
| *K1 Tekil (ELECTRA-TR Base)* | Tekil Encoder | 110M | %50.83 (61/120) | %83.26 (398/478) | 0.8316 | 0.7802 | — | — | ~12ms | $0.00 |
| *K2 Tekil (mDeBERTa-v3 Soft-Prob)* | Tekil Önerme NLI | 278M | %39.17 (47/120) | %80.33 (384/478) | 0.8059 | 0.7405 | — | — | ~28ms | $0.00 |
| *Teorik Üst Sınır (Oracle)* | Tavan | — | %90.00 (108/120) | %93.10 (445/478) | — | — | — | — | — | — |

---

## 3. Temel Bilimsel Bulgular ve Tartışma

1. **Model-Agnostik Hibrit Başarı:**  
   Metodoloji tek bir LLM'e (Llama) aşırı uyum (overfitting) sağlamamıştır. Test edilen 3 büyük model ailesinin üçünde de (Llama, Qwen, GPT-4o-mini), hibrit hat tekil K1 ve K2 modellerinin belirgin üzerine çıkmıştır.
2. **Açık Kaynak 70B Modellerin Üstünlüğü:**  
   Açık ağırlıklı Llama-3.3-70B (%75.83) ve Qwen-2.5-72B (%70.00), ticari hafif model GPT-4o-mini'yi (%63.33) belirgin farkla geride bırakmıştır. Nüanslı ve emsal içtihadına dayalı hukuki/tıbbi muhakemede 70B ölçekli modellerin üstünlüğü kanıtlanmıştır.
3. **Parametre Ölçeğinin Zorunluluğu:**  
   2B yerel model (Gemma-4-E2B-it), iki modelin çelişkisini çözmede %50.00 (rastgele yazı-tura seviyesinde) kalarak K1'in üzerine çıkamamıştır. Bu durum, tezde meta-hakemlik görevi için yüksek parametreli düşünme modellerinin gerekliliğini doğrulamaktadır.
4. **Maliyet ve Hız Optimizasyonu (Konsensüs Tasarrufu):**  
   Test kümesindeki 478 örneğin 358'inde (%74.9) K1 ve K2 doğrudan uzlaşmaktadır. Bu alanda doğruluk **%94.13** olup sıfır API maliyeti ve ~35ms gecikmeyle sonuçlanmaktadır. Dış LLM çağrısı sadece ayrışan %25.1'lik dilimde devreye girmekte, böylece 120 vaka sadece **$0.036 USD (yaklaşık 1 TL)** maliyetle çözülmektedir.

---

## 4. Deney Dosyaları ve Veri Yolları

- **Llama-3.3-70B:** `reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1/arbitration_predictions_120.jsonl`
- **Qwen-2.5-72B:** `reports/experiments/K3-FEWSHOT-QWEN72B-ARBITRATION-v1/arbitration_predictions_120.jsonl`
- **GPT-4o-mini:** `reports/experiments/K3-FEWSHOT-GPT4OMINI-ARBITRATION-v1/arbitration_predictions_120.jsonl`
- **Gemma-4-E2B-it:** `reports/experiments/K3-LIVE-GEMMA-ARBITRATION-v1/arbitration_predictions_120.jsonl`
- **Ablasyon Betiği:** `scripts/62_run_multimodel_meta_arbitration.py`
