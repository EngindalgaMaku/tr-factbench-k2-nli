# Bileşen 0 Ayrışımı: Yanlılıktan Arındırılmış (Debiased) Nötr Atom Meta-Hakemliği - TR-FactBench Gold 480

**Experiment ID:** `K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1`  
**Model:** `meta-llama/llama-3.3-70b-instruct`  
**Tarih:** 5 Ekim 2026  
**Durum:** Tamamlandı (Ablasyon Kanıtlandı)

---

## 1. Hipotez ve Mimari Dönüşüm

### Temel Sorun (Bilişsel Zehirlenme ve Otorite Yanlılığı)
Önceki mimaride Gemma Atomizer, Model B'nin (mDeBERTa) alt bir parçası gibi hakeme sunuluyordu. Model B hem atomları listeliyor hem de her atoma kendi NLI etiketini (`entailment`, `contradiction`) basıyordu. Model B bir atoma yanlış etiket bastığında, Hakem bu etiketi ön-veri kabul ederek zehirleniyor (Error Propagation) ve K1'in doğru bütüncül kararını eziyordu.

### Önerilen Çözüm (Bileşen 0: Bağımsız Atomik Ayrıştırma)
1. **Bileşen 0 (Gemma-4-2B):** İddiayı bağımsız olarak yapıtaşlarına (önermelerine) böler.
2. **Tarafsız Sunum:** Hakeme sunulan atomların yanındaki tüm NLI etiketleri maskelenir. Atomlar ortak, objektif bir girdi olarak sunulur.
3. **Eşit Ağırlıklı Hakemlik:** Model A (Bütüncül Analiz) ve Model B (Atomik Analiz) eşit seviyeli bilirkişiler olarak değerlendirilir.

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
        [Doğrudan Konsensüs]                          [Bileşen 3: Debiased CoT Hakem]
      (357 Vaka - Doğruluk: %94.40)                 (123 Vaka - Llama-3.3-70B)
                   │                                           │
                   │                                    Hakem Doğruluğu:
                   │                                    107 / 123 (%86.99)
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                                NİHAİ HİBRİT KARAR
                       Doğruluk: %92.50 (444 / 480 Doğru)
                       Oracle Tavanına Uzaklık: Sadece %0.83 (4 vaka)
                       API / Gecikme Tasarrufu: %74.38
```

---

## 2. Karşılaştırmalı Ablasyon Sonuçları (123 Gri Alan Vakası)

| Hakemlik Mimarisi | Hakem Doğruluğu (123 Vaka) | Macro-F1 | Net Kazanç |
| :--- | :---: | :---: | :---: |
| **K3-FEWSHOT-LLAMA70B (Erken Etiket)** | %75.83 (91/120) | 0.7612 | Temel |
| **K3-COT-REASONING-FIRST (Etiketli Atomlar)** | %80.49 (99/123) | 0.8062 | +8 vaka (+%4.66) |
| **K3-DEBIASED-NEUTRAL-ATOMS (Nötr Atomlar - Önerilen)** | **%86.99 (107/123)** | **0.8804** | **+16 vaka (+%11.16)** |

---

## 3. Uçtan Uca 480 Test Kümesi Genel Performansı

| Sistem Yapılandırması | 480 Vaka Doğruluğu | Ulaşılan Oracle Payı |
| :--- | :---: | :---: |
| K1 Tek Başına (ELECTRA-TR) | %83.12 (399/480) | - |
| K2 Tek Başına (Gemma + mDeBERTa) | %80.42 (386/480) | - |
| Önceki Hibrit (Etiketli Atom Hakemi) | %90.83 (436/480) | %97.32 |
| **YENİ HİBRİT (Bileşen 0 + Nötr Atom Hakemi)** | **%92.50 (444/480)** | **%99.11** |
| *Teorik Oracle Tavanı (K1 veya K2 doğru)* | *%93.33 (448/480)* | *%100.00* |

---

## 4. Akademik Bulgular ve Çıkarımlar
1. **Hipotez Tam Olarak Doğrulandı:** mDeBERTa'nın ara NLI etiketlerinin hakemden gizlenmesi ve atomların bağımsız bir ön-işleme katmanı (Bileşen 0) olarak sunulması, hakemin doğruluğunu **%80.49'dan %86.99'a sıçratmıştır**.
2. **Tavana Yaklaşma:** 480 vakalık test kümesinde sistem **%92.50** genel doğruluğa ulaşarak teorik tavan olan %93.33'ün neredeyse tamamını (%99.11'ini) yakalamıştır.
3. **Maliyet-Doğruluk Dengesi:** Tüm bu başarı, vakaların %74.38'inde sıfır API çağrısı yapılarak elde edilmiştir.
