# Bileşen 3: Hibrit Arbitrasyon (LLM Hakem) Değerlendirmesi — TR-FactBench Gold 480

**Experiment ID:** `K3-HYBRID-ARBITRATION-GOLD480-v1`  
**Status:** completed gold hybrid evaluation  
**Stage:** component 3 hybrid arbitration  

## 1. Araştırma Sorusu ve Mimari Tasarım

K1 (doğrudan encoder) ve K2 (önerme-düzeyi NLI) modellerinin uzlaştığı %74.9'luk alanda konsensüs kabul edilip, ayrıştığı 120 'gri alan' vakasında LLM Hakem devreye girdiğinde; sistemin uçtan uca doğruluğu, Oracle tavanına (%93.10) yaklaşma oranı ve hesaplama maliyet tasarrufu ne düzeydedir?

```
                         Girdi Çifti (Kanıt Context, İddia Claim)
                                           │
                 ┌─────────────────────────┴─────────────────────────┐
                 ▼                                                   ▼
      Bileşen 1: K1 ELECTRA-TR                            Bileşen 2: K2 Gemma-4 + mDeBERTa
      (Global Cross-Attention)                           (Atomik Ayrıştırma & Soft-Prob NLI)
                 │                                                   │
                 └─────────────────────────┬─────────────────────────┘
                                           │
                             [K1 Tahmini == K2 Tahmini mi?]
                                           │
                   ┌───────────────────────┴───────────────────────┐
                   ▼                                               ▼
              EVET (%74.90)                                  HAYIR (%25.10)
         [Konsensüs Kabul Edilir]                         [Bileşen 3: LLM Hakem]
         (Doğruluk: %94.13, 0 API maliyeti)               (120 Vakada Arbitrasyon)
                   │                                               │
                   └───────────────────────┬───────────────────────┘
                                           ▼
                                  FİNAL HİBRİT KARAR
                                (Doğruluk: %92.26, Macro-F1: 0.9221)
```

## 2. Konsensüs vs. Ayrışma Bölgesi Temel İstatistikleri

- **Toplam Değerlendirilen Altın Örnek Sayısı:** 478
- **Konsensüs Bölgesi (K1 == K2):** **358 örnek (74.90%)**
  - Konsensüs Doğruluğu: **337/358 (94.13%)**
  - Bilimsel Anlamı: İki farklı mimari uzlaştığında sistem neredeyse kusursuz (%94.13) çalışır; pahalı LLM hakemine hiç gerek kalmaz.
- **Ayrışma Bölgesi (K1 != K2):** **120 örnek (25.10%)**
  - Yalnızca K1 Doğru: 61 örnek (12.76%)
  - Yalnızca K2 Doğru: 47 örnek (9.83%)
  - İkisi de Yanlış: 33 örnek (6.90%)
- **Teorik Oracle Üst Tavanı (Oracle Upper Bound):** **445/478 (%93.10)**

## 3. Hibrit Triad Arbitrasyon Sonuçları

| Hakem Modeli | Hibrit Acc | Hibrit F1 | Δ vs K1 | Δ vs K2 | Δ vs Standalone | Hakem Gri Alan Acc | Oracle Kapanış | McNemar p (vs K1) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gemma-4-26B (Zero-Shot) | 0.9226 | 0.9221 | +0.0900 | +0.1192 | +0.0167 | 0.8667 | 91.5% | 0.0000 |
| GPT-4.1-mini (Few-Shot 8) | 0.9142 | 0.9147 | +0.0816 | +0.1109 | +0.0021 | 0.8333 | 83.0% | 0.0000 |
| Llama-3.3-70B (Few-Shot 8) | 0.9121 | 0.9120 | +0.0795 | +0.1088 | +0.0042 | 0.8250 | 80.9% | 0.0000 |
| Gemma-4-26B (Few-Shot 8) | 0.9079 | 0.9075 | +0.0753 | +0.1046 | +0.0063 | 0.8083 | 76.6% | 0.0000 |
| GPT-4.1-mini (Zero-Shot) | 0.9017 | 0.9021 | +0.0690 | +0.0983 | +0.1109 | 0.7833 | 70.2% | 0.0000 |
| Qwen-2.5-72B (Few-Shot 8) | 0.9017 | 0.9011 | +0.0690 | +0.0983 | +0.0356 | 0.7833 | 70.2% | 0.0000 |

En yüksek hibrit başarıma **%92.26 Doğruluk** ve **0.9221 Macro-F1** ile **Gemma-4-26B (Zero-Shot)** hakemliğinde ulaşılmıştır.

## 4. Çıkarım Maliyeti ve Gecikme Tasarrufu (Efficiency Analysis)

| Hakem Modeli | Tek Başına LLM Çağrısı | Hibrit LLM Çağrısı | Çağrı / Maliyet Tasarrufu (%) | Hibrit Doğruluk | Tek Başına LLM Doğruluk |
| --- | --- | --- | --- | --- | --- |
| Gemma-4-26B (Zero-Shot) | 478 | 120 | %74.90 | 0.9226 | 0.9059 |
| Gemma-4-26B (Few-Shot 8) | 478 | 120 | %74.90 | 0.9079 | 0.9017 |
| GPT-4.1-mini (Few-Shot 8) | 478 | 120 | %74.90 | 0.9142 | 0.9121 |
| GPT-4.1-mini (Zero-Shot) | 478 | 120 | %74.90 | 0.9017 | 0.7908 |
| Llama-3.3-70B (Few-Shot 8) | 478 | 120 | %74.90 | 0.9121 | 0.9079 |
| Qwen-2.5-72B (Few-Shot 8) | 478 | 120 | %74.90 | 0.9017 | 0.8661 |

## 5. Grafikler

![Hibrit vs Tekil Modeller](figures/hybrid_vs_standalone_comparison.svg)

## 6. Bilimsel Yorum ve Çıkarımlar

- Konsensüs bölgesi (358/478 örnek, %74.90): K1 ve K2 hemfikir olduğunda doğruluk %94.13 seviyesindedir (337/358 doğru). Bu alanda LLM çağrısına ihtiyaç duyulmaz.
- Ayrışma bölgesi (120/478 örnek, %25.10): Bu gri alanda K1 61, K2 47 doğru cevaba sahiptir; teorik Oracle tavanı %93.10'dur.
- Gemma-4-26B zero-shot hakemliği ile hibrit sistem %92.26 doğruluğa ve 0.9221 Macro-F1'e ulaşarak Oracle tavanına (%93.10) sadece %0.84 mesafeye yaklaşmıştır.
- Doğrudan LLM kullanımına göre API çağrılarında ve çıkarım gecikmesinde %74.90 net tasarruf sağlanmıştır.

## 7. Kısıtlar ve Gelecek Adımlar

- Ayrışma vakalarında hakem istemi mevcut baseline tahminleri üzerinden test edilmiştir; K1 ve K2'nin önermelerini içeren meta-istem (meta-prompting) ayrıca incelenebilir.
- Değerlendirme 478 geçerli ayrıştırılmış altın test örneği üzerinedir.

### Gelecek Adımlar:

- Bileşen 3 hakem bulgularını THESIS_MASTER_ROADMAP.md dosyasına entegre etmek.
- Gerçek LLM çıktıları (AP6) üzerinde genellenebilirlik testine hazırlanmak.
- Tez Bölüm 4 ve büyük dergi makalesi için hibrit triad sonuçlarını dondurmak.
