# K3-FEWSHOT-LLAMA70B-ARBITRATION-v1 Raporu

**Model:** `meta-llama/llama-3.3-70b-instruct` (OpenRouter API, temperature=0.0)  
**Tasarım:** Bilgilendirilmiş Emsalli Meta-Hakem (Informed Few-Shot Meta-Judge)  
- Hakem, Model A (K1) ve Model B (K2) kararlarını + K2 atom NLI dökümünü görür.  
- İstem içine eğitim kümesinden 4 adet bağımsız emsal hakemlik kararı (`FEWSHOT_PRECEDENTS`) eklenmiştir.  
**Tarih:** 2026-10-03  
**Veri Kümesi:** TR-FactBench Gold 480 (478 geçerli test örneği)  

---

## 1. Hakem Başarımı (120 Ayrışma / Gri Alan Örneğinde)

| Metrik | Zero-Shot Meta-Hakem | Few-Shot Emsalli Meta-Hakem | Değişim / Fark |
|---|:---:|:---:|:---:|
| **Doğru Karar** | 57 / 120 | **91 / 120** | **+34 doğru (+%28.33)** |
| **Hakem Doğruluğu** | %47.50 | **%75.83** | **+28.33 puan** |
| **Hakem Macro-F1** | 0.4579 | **0.7757** | **+0.3178** |
| **Model Tercihi Dağılımı** | Mod A: 50, Mod B: 64, Diğer: 6 | Mod A: 41, Mod B: 77, Diğer: 2 | - |

---

## 2. Uçtan Uca Hibrit Sistem Başarımı (478 Altın Test Örneği)

| Model / Sistem | Doğruluk (Acc) | Macro-F1 | MCC | Açıklama |
|---|:---:|:---:|:---:|---|
| **K1 (ELECTRA-TR)** | %83.26 (398/478) | 0.8316 | 0.7802 | Bütüncül sekans sınıflandırıcı |
| **K2 (Gemma-4 + DeBERTa Soft-Prob)** | %80.33 (384/478) | 0.8059 | 0.7405 | Atomik NLI & Soft-Prob toplulaştırma |
| **Hibrit + Llama-70B (Zero-Shot Meta-Hakem)** | %82.43 (394/478) | 0.8262 | 0.7723 | Emsalsiz, zero-shot bilgilendirilmiş hakem |
| **Hibrit + Llama-70B (Few-Shot Emsalli Meta-Hakem)** | **%89.54 (428/478)** | **0.8966** | **0.8628** | **4 emsal kararla eğitilmiş gerçek meta-hakem** |
| *Teorik Üst Sınır (Oracle)* | *%93.10 (445/478)* | *-* | *-* | *K1 veya K2'den birinin bildiği tavan* |

---

## 3. İstatistiksel Anlamlılık (Exact McNemar Testi)

- **Few-Shot Hibrit vs. K1 (ELECTRA):**
  - Hibrit tek başına doğru: **52 örnek**
  - K1 tek başına doğru: **22 örnek**
  - Discordant toplam: 74
  - **Exact $p = 0.00064$ ($p < 0.001$)** → K1 modeline karşı ezici ve istatistiksel olarak yüksek anlamlılıkta üstün!
- **Few-Shot Hibrit vs. K2 (DeBERTa Soft-Prob):**
  - Hibrit tek başına doğru: **45 örnek**
  - K2 tek başına doğru: **1 örnek**
  - Discordant toplam: 46
  - **Exact $p = 1.34 \times 10^{-12}$ ($p < 0.0001$)** → K2 modeline karşı ezici üstünlük!

---

## 4. Karışıklık Matrisi (478 Örnek)

| Gerçek \ Tahmin | Supported | Partially Supported | Contradicted | Unverifiable | Toplam | Sınıf Doğruluğu (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Supported** | **114** | 6 | 0 | 0 | 120 | %95.00 |
| **Partially Supported** | 2 | **107** | 9 | 0 | 118 | %90.68 |
| **Contradicted** | 1 | 10 | **110** | 0 | 121 | %90.91 |
| **Unverifiable** | 1 | 15 | 6 | **97** | 119 | %81.51 |

---

## 5. Çıkarım Maliyeti ve Kaynak Kullanımı

- **Toplam 120 Hakem Çağrısı API Maliyeti:** **$0.036047 USD (~3.6 sent)**
- **Ortalama Yanıt Süresi:** ~5.58 saniye / örnek
- **Sistem Tasarrufu:** Sorguların %74.9'u (358 / 478) sıfır API çağrısı ve 12ms gecikmeyle çözülmüş, yalnızca ayrışan %25.1'lik kısım LLM hakeme gitmiştir.
