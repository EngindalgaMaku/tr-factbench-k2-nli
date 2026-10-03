# K3-FEWSHOT-LLAMA70B-ARBITRATION-v1

**Model:** `meta-llama/llama-3.3-70b-instruct` (OpenRouter API)  
**Tasarım:** Bilgilendirilmiş Emsalli Meta-Hakem (Informed Few-Shot Meta-Arbitration)  
**Tarih:** 2026-10-03  
**Veri:** TR-FactBench Gold 480 (478 test örneği)  

## Sonuç Özeti

- **120 Çelişki Örneğinde Hakem Başarımı:** **91 / 120 (%75.83)** (Zero-shot meta-hakeme göre +%28.33 artış!)
- **Uçtan Uca Hibrit Doğruluk (478 Örnek):** **%89.54 (428 / 478)**
- **Uçtan Uca Macro-F1:** **0.8966**
- **MCC:** **0.8628**
- **İstatistiksel Anlamlılık (McNemar):**
  - vs K1 (ELECTRA): $p = 0.00064$ (Anlamlı)
  - vs K2 (DeBERTa Soft-Prob): $p = 1.34 \times 10^{-12}$ (Anlamlı)
- **Gerçekleşen API Maliyeti:** $0.0360 USD (3.6 sent)
- **Detaylı Rapor:** [REPORT_K3_FEWSHOT_LLAMA70B.md](REPORT_K3_FEWSHOT_LLAMA70B.md)
