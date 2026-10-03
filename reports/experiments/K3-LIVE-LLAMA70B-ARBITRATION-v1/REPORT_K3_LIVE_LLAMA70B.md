# K3-LIVE-LLAMA70B-ARBITRATION-v1 Raporu

**Model:** `meta-llama/llama-3.3-70b-instruct` (OpenRouter API, temperature=0)  
**Tasarım:** Bilgilendirilmiş meta-hakem (hakem K1 ve K2 kararlarını + K2 atom NLI dökümünü görür)  
**Tarih:** 2026-10-03 17:14:36  
**Veri Kümesi:** TR-FactBench Gold 480 (478 geçerli test örneği; 2 örnek atomizer hatası nedeniyle dışarıda)  

---

## 1. Hakem Başarımı (120 Ayrışma Örneğinde)

- **Doğru Karar:** 57 / 120 (**%47.50**)
- **Hakem Macro-F1:** 0.4579
- **Geçerli JSON:** 118 / 120
- **Beyan edilen `favored_model` dağılımı:** Model A (K1): 50, Model B (K2): 64, Neither/Unknown: 6

---

## 2. Uçtan Uca Hibrit Sistem Başarımı (478 Örnek)

| Model / Sistem | Doğruluk | Macro-F1 | MCC | Açıklama |
|---|---|---|---|---|
| K1 (ELECTRA-TR) | %83.26 | 0.8316 | 0.7802 | Bütüncül sınıflandırıcı |
| K2 (Gemma-4 atomizer + mDeBERTa, soft-prob) | %80.33 | 0.8059 | 0.7405 | Atomik NLI |
| Hibrit + Gemma-4-E2B-it (bilgilendirilmiş meta-hakem, yerel) | %83.05 | 0.8294 | 0.7840 | K1/K2 kararlarını gören 2B hakem |
| **Hibrit + Llama-3.3-70B (bilgilendirilmiş meta-hakem)** | **%82.43 (394/478)** | **0.8262** | **0.7723** | 70B hakem |
| *Oracle tavanı* | *%93.10 (445/478)* | - | - | K1 veya K2 doğruysa doğru sayılır |

---

## 3. İstatistiksel Anlamlılık (Exact McNemar, örnek kimliğine göre eşlenmiş)

| Karşılaştırma | Yalnız Hibrit doğru | Yalnız karşı taraf doğru | p (exact) |
|---|---:|---:|---:|
| Hibrit vs K1 | 29 | 33 | 0.7035 |
| Hibrit vs K2 | 31 | 21 | 0.2116 |
| Hibrit(Llama-70B) vs Hibrit(Gemma-E2B) | 27 | 30 | 0.7914 |

---

## 4. Kaynak ve Maliyet

- Prompt token: 79,609 | Tamamlama token: 14,009
- **Gerçek faturalanan maliyet (OpenRouter `usage.cost`):** $0.0207 USD
- Toplam istek süresi: 793.8 sn (ortalama 6.61 sn/örnek)

---

## 5. Yorum (bkz. `reports/experiments/AUDIT-K2-K3-v1/README.md`)

Bu bilgilendirilmiş meta-hakem tasarımı, aynı 120 örnekte **kör (blind) LLM hakem** tasarımının
(resmi TR-FactBench sistem istemi + 8-shot) gerisinde kalmıştır. Ana hata kaynağı, hakemin
`contradicted` etiketini aşırı üretmesidir (gold kısmi-destek örneklerinin çoğu `contradicted`
olarak etiketlenmiştir). Bu desen aynı modelin kör zero-shot çıktısında da görüldüğünden, düşüşün
temel nedeni K1/K2 bilgisinin gösterilmesinden çok, zero-shot ayarı ve istemdeki etiket tanımlarının
resmi tanımlardan sapmasıdır.
