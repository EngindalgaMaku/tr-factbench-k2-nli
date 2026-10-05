# Bileşen 3: CoT (Zincirleme Akıl Yürütme) Bilgilendirilmiş Meta-Hakem - TR-FactBench Gold 480

**Experiment ID:** `K3-COT-REASONING-FIRST-LLAMA70B-v1`  
**Model:** `meta-llama/llama-3.3-70b-instruct`  
**Tarih:** 5 Ekim 2026  
**Durum:** Tamamlandı (%100 Kapsamalı K2 ile Doğrulandı)

---

## 1. Deney Özeti ve Amaç
Bu deneyde, K1 (ELECTRA-TR) ve %100 kapsama oranına ulaşan güncel K2 (Gemma-4-2B + mDeBERTa) modellerinin uyuşmazlığa düştüğü **123 gri alan vakasında**, Llama-3.3-70B modeli bir **Meta-Hakem** olarak kullanılmıştır.

Hakem modeli, erken etiket taahhüdü (premature commitment) hatasına düşmemek için **Chain-of-Thought (Önce Mantıksal Gerekçe, Sonra Model Tercihi, En Son Karar)** akışıyla çalıştırılmıştır.

---

## 2. Kümülatif Sonuçlar (480 Vaka)

```
                         TR-FactBench Gold 480 Giriş Çifti
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
          Bileşen 1: K1 ELECTRA-TR                    Bileşen 2: K2 Gemma-4 + mDeBERTa
          (Bütüncül Doğrulayıcı)                     (Önerme Seviyesi NLI - %100 Kapsama)
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                            [K1 Kararı == K2 Kararı mı?]
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
             EVET (%74.38)                               HAYIR (%25.62)
        [Doğrudan Konsensüs]                          [Bileşen 3: CoT Meta-Hakem]
      (357 Vaka - Doğruluk: %94.40)                 (123 Vaka - Llama-3.3-70B)
                   │                                           │
                   │                                    Hakem Doğruluğu:
                   │                                    99 / 123 (%80.49)
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                                NİHAİ HİBRİT KARAR
                       Doğruluk: %90.83 (436 / 480 Doğru)
                       Macro-F1: 0.9090 | MCC: 0.8801
                       API / Gecikme Tasarrufu: %74.38
```

---

## 3. Bileşen ve Model Karşılaştırma Tablosu

| Model / Mimari | Kapsama (%) | Doğruluk (Accuracy) | Macro-F1 | MCC | Açıklama |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **K1 Tek Başına (ELECTRA-TR)** | %100.0 | %83.12 (399/480) | 0.8301 | 0.7785 | Hızlı global encoder |
| **K2 Tek Başına (Gemma-4-2B + mDeBERTa)** | **%100.0** | %80.42 (386/480) | 0.8065 | 0.7412 | 0 kayıp, önerme seviyesinde NLI |
| **Teorik Oracle Tavanı (K1 veya K2 doğru)** | %100.0 | %93.33 (448/480) | - | - | Hibrit mimarinin teorik üst sınırı |
| **KADEMELİ HİBRİT MİMARİ (Önerilen)** | **%100.0** | **%90.83 (436/480)** | **0.9090** | **0.8801** | **%74.38 maliyet tasarrufuyla %90.83 başarım** |

---

## 4. Sınıflandırma Metrikleri (480 Vaka)

| Sınıf (Label) | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **supported** | 0.9672 | 0.9833 | **0.9752** | 120 |
| **partially_supported** | 0.7943 | 0.9412 | **0.8615** | 119 |
| **contradicted** | 0.9145 | 0.8843 | **0.8992** | 121 |
| **unverifiable** | 0.9900 | 0.8250 | **0.9000** | 120 |
| **Ağırlıklı Ortalama / Doğruluk** | **0.9168** | **0.9083** | **0.9091** | **480** |

---

## 5. Çıkarımlar
1. **%100 Kapsama:** Gemma-2B'nin token üretimi ve defansif parser'ı sayesinde tek bir vaka bile feda edilmeden tüm veri kümesi atomize edilmiştir.
2. **Yüksek Konsensüs Güvenilirliği:** Modeller anlaştığında (%74.38 oranında), neredeyse 20 vakadan 19'u (%94.40) doğrudan doğrudur. Bu durum pahalı ve yavaş LLM çağrısı ihtiyacını 4'te 3 oranında ortadan kaldırır.
3. **CoT Hakem Gücü:** Gri alandaki 123 vakanın 99'u (%80.49) çözülmüş ve toplam doğruluk **%90.83** seviyesine ulaştırılmıştır.
