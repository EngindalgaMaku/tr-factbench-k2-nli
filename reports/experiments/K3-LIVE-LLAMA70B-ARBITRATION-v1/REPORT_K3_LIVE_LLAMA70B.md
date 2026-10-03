# K3-LIVE-LLAMA70B-ARBITRATION-v1 Raporu

**Model:** `meta-llama/llama-3.3-70b-instruct` (OpenRouter API)  
**Tarih:** 2026-10-03 17:00:04  
**Veri Kümesi:** TR-FactBench Gold 480 (478 geçerli test örneği)  

---

## 1. Hakem Başarımı (120 Çelişki Örneğinde)

- **Doğru Karar:** 57 / 120 (**%47.50**)
- **Hakem Macro-F1:** 0.4579
- **Desteklenen Model Dağılımı:**
  - Model A (K1 ELECTRA): 50
  - Model B (K2 DeBERTa Soft-Prob): 64
  - Tarafsız / İkisi de Değil: 6

---

## 2. Uçtan Uca Hibrit Sistem Başarımı (478 Örnek)

| Model / Sistem | Doğruluk (Acc) | Macro-F1 | MCC | Açıklama |
|---|---|---|---|---|
| **K1 (ELECTRA-TR Base)** | %83.26 (398/478) | 0.8316 | 0.7802 | Bütüncül sekans sınıflandırıcı |
| **K2 (Gemma-4 + DeBERTa Soft-Prob)** | %80.33 (384/478) | 0.8059 | 0.7405 | Atomik NLI & Olasılık Toplulaştırma |
| **Hibrit + Gemma-4-E2B-it (Yerel Hakem)** | %83.05 (397/478) | 0.8294 | 0.7711 | 2B Yerel LLM Hakemliği |
| **Hibrit + Llama-3.3-70B (Canlı OpenRouter Hakem)** | **%82.43 (394/478)** | **0.8262** | **0.7723** | **70B Büyük Parametreli Meta-Hakem** |
| *Teorik Üst Sınır (Oracle)* | *%93.10 (445/478)* | *-* | *-* | *K1 veya K2'den birinin bildiği tavan* |

---

## 3. İstatistiksel Anlamlılık (McNemar Testi)

- **Hibrit vs K1 (ELECTRA):**
  - Hibrit tek başına doğru: 29
  - K1 tek başına doğru: 33
  - Exact $p$-değeri: **7.0354e-01** (Anlamlılık: False)
- **Hibrit vs K2 (DeBERTa Soft-Prob):**
  - Exact $p$-değeri: **2.1161e-01** (Anlamlılık: False)
- **Hibrit (Llama-70B) vs Hibrit (Gemma-2B):**
  - Exact $p$-değeri: **7.9137e-01** (Anlamlılık: False)

---

## 4. Kaynak ve Maliyet Analizi

- Toplam Prompt Token: 79,609
- Toplam Tamamlama Token: 14,009
- Tahmini API Maliyeti: ~$0.0138 USD
- Toplam Süre: 793.8 saniye (ortalama 6.61 saniye/örnek)
