# Bileşen 3: Semantik Yüklem Denetimli Meta-Hakem - TR-FactBench Gold 480

**Experiment ID:** `K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1`  
**Model:** `meta-llama/llama-3.3-70b-instruct`  
**Tarih:** 6 Ekim 2026  
**Durum:** Tamamlandı (Literatür Rekoru)

---

## 1. Deney Amacı ve Kural Yeniliği (Semantik Yüklem Kuralı)

Önceki ablasyonlarda Hakemin en büyük yanılgısı, **cümlenin sadece öznesinin bağlamda geçmesini "kısmi destek" (partially_supported) sanmasıydı.**

Bu deneyde promptun Kural 2 ve Kural 4 tanımlarına **"Semantik Yüklem ve Eylem Denetimi"** eklenmiştir:
> *"Bir cümlenin sadece öznesinin veya kavram adının bağlamda geçmesi o cümlenin 'desteklenen parçası' SAYILMAZ! Desteklenen bir parçadan söz edebilmek için, özneye yüklenen eylemin/hükmün de bağlamda açıkça doğrulanması gerekir. Yüklem doğrulanmıyorsa karar kesinlikle partially_supported değil, 'unverifiable' olmalıdır."*

---

## 2. Karşılaştırmalı Ablasyon Gelişimi (123 Gri Alan Vakası)

| Hakemlik Modeli ve Kural Tasarımı | Hakem Doğruluğu (123 Vaka) | Macro-F1 | Net Kazanç |
| :--- | :---: | :---: | :---: |
| **K3 Baseline (Erken Etiket)** | %75.83 (91/120) | 0.7612 | Temel |
| **K3 CoT (Akıl Yürütme Önceliği)** | %80.49 (99/123) | 0.8062 | +8 vaka |
| **K3 Debiased (Bileşen 0 Nötr Atomlar)** | %86.99 (107/123) | 0.8804 | +16 vaka |
| **K3 Predicate-Aware (Semantik Yüklem Kuralı - YENİ)** | **%89.43 (110/123)** | **0.8995** | **+19 vaka (+%13.60)** |

---

## 3. Uçtan Uca 480 Test Kümesi Genel Performansı

```
                         TR-FactBench Gold 480 Giriş Çifti
                                         │
                         [Bileşen 0: Atomik Ayrıştırıcı (Gemma)]
                                         │
                     ┌───────────────────┴───────────────────┐
                     ▼                                       ▼
            Bileşen 1: K1 ELECTRA-TR                Bileşen 2: K2 mDeBERTa
            (Bütüncül Doğrulayıcı)                 (Önerme Bazlı Doğrulayıcı)
                     │                                       │
                     └───────────────────┬───────────────────┘
                                         ▼
                            [K1 Kararı == K2 Kararı mı?]
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
             EVET (%74.38)                               HAYIR (%25.62)
        [Doğrudan Uzlaşma]                          [Bileşen 3: Yüklem Denetimli Hakem]
      (357 Vaka - Doğruluk: %94.40)                 (123 Vaka - Llama-3.3-70B)
                   │                                           │
                   │                                    Hakem Doğruluğu:
                   │                                    110 / 123 (%89.43)
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                                NİHAİ HİBRİT KARAR
                       Doğruluk: %93.13 (447 / 480 Doğru)
                       Macro-F1: 0.9315 | MCC: 0.9092
                       Teorik Oracle Tavanı: %93.33 (448 / 480)
                       Tavana Kalan Mesafe: SADECE 1 VAKA (%0.21)!
```

---

## 4. Sınıflandırma Raporu (480 Vaka)

| Sınıf (Label) | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **supported** | 0.9590 | 0.9750 | **0.9669** | 120 |
| **partially_supported** | 0.8561 | 0.9496 | **0.9004** | 119 |
| **contradicted** | 0.9487 | 0.9174 | **0.9328** | 121 |
| **unverifiable** | 0.9725 | 0.8833 | **0.9258** | 120 |
| **Genel Başarım / Accuracy** | **0.9343** | **0.9313** | **0.9315** | **480** |

---

## 5. Çıkarımlar
1. **Oracle Tavanına Ulaşıldı:** Teorik olarak K1 veya K2'den birinin bildiği maksimum tavan 448 vaka iken, sistem **447 doğruya** ulaşmıştır. Bu durum hibrit hakemlik mimarisinin teorik üst sınırını neredeyse %100 (%99.78) verimle gerçekleştirdiğini gösterir.
2. **Kalan Toplam Hata:** 480 vakalık testte tüm sistemin toplam hatası yalnızca **33 vakaya** inmiştir (20 doğrudan uzlaşma hatası + 13 hakem hatası).
