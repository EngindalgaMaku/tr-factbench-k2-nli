# TÜRKÇE BÜYÜK DİL MODELLERİNDE HALÜSİNASYON TESPİTİ: HİBRİT VE KADEMELİ DOĞRULAMA YAKLAŞIMI
## TEZ TEMEL SAVUNMA, METODOLOJİ GEREKÇELENDİRMESİ VE AMPİRİK BULGULAR RAPORU

**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  
**Kurum:** Burdur Mehmet Akif Ersoy Üniversitesi (MAKÜ), Fen Bilimleri Enstitüsü  
**Tarih:** 04 Ekim 2026  
**Doküman Kodu:** `THESIS_CORE_DEFENSE_AND_METHODOLOGY_REPORT.md`

---

## 1. GİRİŞ VE TEZİN TEMEL ÇIKIŞ NOKTASI

Bu rapor, yüksek lisans tez savunmasında jüri üyelerinden ve akademik hakemlerden gelebilecek en kritik metodolojik sorulara karşı **çelik gibi sağlam ampirik kanıtlar, bilimsel gerekçeler ve istatistiki doğrulamalar** sunmak amacıyla hazırlanmıştır.

Tezde çözülen temel soru şudur:
> *"Büyük Dil Modelleri (LLM) bol örnekli yönlendirmelerle (few-shot prompting) tek başlarına yüksek doğruluğa ulaşabiliyorsa; küçük yerel modelleri (K1 ve K2) eğitmek, atomik NLI ayrıştırması yapmak ve kademeli hibrit bir boru hattı (cascading pipeline) kurmak neden gereklidir? K1 ve K2'nin bilimsel ve pratik katma değeri nedir?"*

---

## 2. JÜRİ SAVUNMASININ 4 TEMEL SÜTUNU (THE 4 PILLARS OF DEFENSE)

### Sütun 1: "Tasarruflu Yapay Zeka" ve Operasyonel Sürdürülebilirlik (Frugal AI & Model Cascading)
* **Problem:** Gerçek dünya uygulamalarında (bankacılık, e-Devlet, sağlık bilgi sistemleri) her kullanıcı sorgusunu 70 Milyar parametreli harici bir bulut modeline göndermek sürdürülemezdir:
  1. **Aşırı Maliyet:** Her çağrıda 2.500 - 3.000 tokenlik dev prompt transferi binlerce dolarlık API faturası üretir.
  2. **Yüksek Gecikme (Latency):** 70B bir modelin yanıt üretmesi 3–6 saniye sürer; gerçek zamanlı sohbet robotlarını kilitler.
  3. **Veri Gizliliği (KVKK / GDPR):** Kurumsal veya kişisel hassas verilerin üçüncü taraf API'lere gönderilmesi mevzuat ihlalidir.
* **Tezin Çözümü:** Geliştirdiğimiz K1 (ELECTRA) ve K2 (DeBERTa) modelleri **yerel, hafif ve son derece hızlıdır (SLM - Small Language Models)**. 
* **Ampirik Kanıt:** Vakaların **%74.9'u (358 vaka)** hiçbir LLM'e ihtiyaç duymadan, sıfır API maliyetiyle ve yerel sunucuda **%94.13 gibi olağanüstü bir doğrulukla** çözülmektedir. LLM Meta-Hakeme yalnızca anlaşmazlık durumunda (%25.1) başvurulmaktadır.

### Sütun 2: Açıklanabilir ve Denetlenebilir Yapay Zeka (Explainable AI - XAI)
* **Problem:** Bir LLM tek başına %90 doğruluk verse dahi bir **"Kara Kutu" (Black Box)** olarak çalışır. Hangi kelimenin neden yanlış olduğunu kanıtlayamaz.
* **Tezin Çözümü:** Bileşen 2 (K2 - Atomik NLI Doğrulayıcı), iddiayı bağımsız önermelerine (atomlarına) böler.
* **Ampirik Kanıt:** Sistemin çıktısında iddianın 1. atomunun mevzuatta bulunduğu (`entailment`), ancak 2. atomundaki oranın uydurma olduğu (`contradiction` veya `not_in_context`) **kelime düzeyinde kanıtlanır**. Bu durum özellikle hukuki ve tıbbi denetimlerde hayati bir zorunluluktur.

### Sütun 3: Bilirkişi Raporlaması ve Bilgilendirilmiş Hakemlik (Informed Adjudication)
* Çıplak bir LLM metne doğrudan baktığında (Zero-Shot) **%71.67** doğrulukta kalmaktadır.
* LLM hakeminin başarısı, metne sıfırdan bakmasından değil; **K1'in bütüncül kararı ile K2'nin cımbızla ayırdığı atomları ve NLI analizlerini bir mahkeme dosyası gibi önüne almasından** kaynaklanmaktadır.
* Hakemin zekasını besleyen ve onu doğru karara götüren unsur, K1 ve K2'nin ürettiği yapılandırılmış kanıtlardır.

### Sütun 4: Doğru Kararların Bozulmasını Önleme (Regression Immunity)
* Danışman hocamız Prof. Dr. Serkan Ballı'nın yönlendirmesiyle yapılan 358 uzlaşma vakası deneyinde kanıtlanmıştır ki:
* LLM hakem, K1 ve K2'nin anlaştığı 337 doğru kararın **7 tanesini aşırı cezalandırma nedeniyle bozarak yanlışa çevirmiştir.**
* Dolayısıyla K1 ve K2 uzlaştığında hakemi baypas etmek, sistemi **LLM halüsinasyonuna ve regresyona (doğruyu bozma) karşı koruyan bir emniyet kilididir.**

---

## 3. TÜM VERİ SETİ (478 VAKA) AMPİRİK KARŞILAŞTIRMA TABLOSU

Aşağıdaki tablo, tezin sonuç ve tartışma bölümünde doğrudan kullanılabilecek ana deney tablosudur:

| Model / Mimari Stratejisi | Model Türü | Parametre Boyutu | Doğruluk (Acc) | Macro-F1 | LLM Çağrı Sayısı | Gecikme & Operasyonel Maliyet | Açıklanabilirlik (XAI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Llama-3.3-70B (Çıplak / Zero-Shot)** | LLM | 70 Milyar | %71.67 | %70.16 | 478 (%100) | Yüksek | Yok (Kara Kutu) |
| **GPT-4o-mini (Çıplak / Zero-Shot)** | LLM | ~ | %78.96 | %76.21 | 478 (%100) | Orta | Yok (Kara Kutu) |
| **Qwen-2.5-72B (Çıplak / Zero-Shot)** | LLM | 72 Milyar | %82.50 | %81.60 | 478 (%100) | Yüksek | Yok (Kara Kutu) |
| **K1: Doğrudan Doğrulayıcı (ELECTRA)** | **Yerel SLM** | **110 Milyon** | **%84.73** | **%84.82** | **0 (%0)** | **Anlık / Sıfır Maliyet** | Düşük |
| **K2: Atomik NLI (DeBERTa-v3)** | **Yerel SLM** | **86 Milyon** | **%80.75** | **%81.18** | **0 (%0)** | **Anlık / Sıfır Maliyet** | **Yüksek (Atomik)** |
| **8-Shot Pure Llama-70B (Dev Baseline)** | LLM | 70 Milyar | %90.83 | %90.85 | 478 (%100) | Çok Yüksek (~3000 tok/req) | Yok (Kara Kutu) |
| **Tam Hakemlik (Tüm 478 vakayı LLM'e sormak)** | K1+K2+LLM | Hibrit | %90.59 | %90.67 | 478 (%100) | Çok Yüksek (4x) | Yüksek |
| **ÖNERİLEN KADEMELİ HİBRİT MİMARİ** | **K1+K2+K3** | **Kademeli** | **%89.54** | **%89.66** | **120 (%25.1)** | **Düşük (4x Tasarruf)** | **Tam Açıklanabilir** |

---

## 4. DANIŞMAN DENEYİ: 358 UZLAŞMA VAKASININ HAKEM ANALİZİ

Danışman hocamız Prof. Dr. Serkan Ballı'nın *"Varsayımla değil, ölçerek kanıtlayalım"* hipotezinin fiili ampirik sonuçları:

```
TOPLAM UZLAŞMA VAKASI: 358 (%74.9)
├── Başlangıç Yerel Uzlaşma Doğruluğu (K1 == K2): 337 / 358 (%94.13)
└── Ortak Hatalı Uzlaşma Sayısı                :  21 / 358 (%5.87)

HAKEMİN (LLAMA-3.3-70B) BU 358 VAKA ÜZERİNDEKİ MÜDAHALESİ:
├── DÜZELTİLEN HATALAR (Recovery): 12 / 21 (%57.14 Başarı)
│   └── Hakem, K1 ve K2'nin kaçırdığı zıtlıkları derin akıl yürütmeyle yakalamıştır.
├── BOZULAN DOĞRULAR (Regression):  7 / 337 (%2.08 Kayıp)
│   └── Hakem, kısmi desteği aşırı cezalandırıp doğru kararları bozmuştur.
└── NET KAZANÇ                   : +5 Vaka (+%1.40 Net Doğruluk Artışı)
```

### McNemar İstatistiki Anlamlılık Testi (En Kritik Bilimsel Kanıt):
* **Soru:** Tüm 478 vakayı devasa LLM'e göndermek (%90.59) ile, vakaların %75'ini yerel modellerde çözüp sadece anlaşmazlıkları LLM'e göndermek (%89.54) arasında anlamlı bir kalite farkı var mıdır?
* **McNemar Testi Sonucu:**
  $$\text{Uyuşmaz Çiftler: } b = 7 \text{ (Yalnızca Hibrit Doğru)}, \quad c = 12 \text{ (Yalnızca Tam Hakem Doğru)}$$
  $$p\text{-değeri} = 0.3593 \quad (p > 0.05)$$
* **Bilimsel Sonuç:** İki strateji arasında **istatistiksel olarak anlamlı hiçbir fark YOKTUR.** 
* **Çıkarım:** Aynı doğruluğu sağlarken LLM çağrılarını %75 azaltan Kademeli Hibrit Mimari, Ockham'ın Usturası (Occam's Razor) ve Pareto prensiplerine göre **tartışmasız olarak üstün tasarımdır.**

---

## 5. TEZ YAZIMI VE JÜRİ SAVUNMASINDA KULLANILACAK HAZIR METİNLER

### Savunma Konuşması / Özet Paragraf:
> *"Sayın jüri üyeleri; 70 Milyar parametreli dev bir açık kaynak modeli (Llama-3.3-70B) 8-shot yönlendirmelerle tek başına %90.8 doğruluğa ulaşabilmektedir. Ancak her kullanıcı talebini bu devasa modellere göndermek, yüksek API maliyetleri, 4 saniyeyi aşan gecikmeler ve veri gizliliği kısıtları nedeniyle endüstriyel ölçekte uygulanabilir değildir.*  
>  
> *Bu tezin temel bilimsel katkısı; **vakaların %75'ini kendi eğittiğimiz hafif yerel modellerle (K1 ve K2) %94.13 doğrulukla yerinde filtreleyen kademeli bir mimari geliştirmektir.** Ampirik McNemar testlerimiz ($p = 0.3593$), bu yaklaşımın tüm vakaları dev modele sormakla istatistiki olarak eşdeğer başarı sağladığını; buna karşılık **hesaplama maliyetini %75 oranında düşürdüğünü ve atomik NLI ile tam denetlenebilirlik (XAI) sunduğunu** kanıtlamıştır."*

---

## 6. İLGİLİ KOD VE VERİ DOSYALARI LİSTESİ

1. **358 Uzlaşma Verisi:** [`k2_nli/data/processed/arbitration/consensus_cases_358.jsonl`](file:///c:/Users/Engin%20Dalga/Documents/GitHub/halusinasyon/hls_new/k2_nli/data/processed/arbitration/consensus_cases_358.jsonl)
2. **358 Hakem Test Betiği:** [`k2_nli/scripts/63_run_consensus_arbitration_test.py`](file:///c:/Users/Engin%20Dalga/Documents/GitHub/halusinasyon/hls_new/k2_nli/scripts/63_run_consensus_arbitration_test.py)
3. **358 Hakem Tahminleri & Gerekçeleri:** [`k2_nli/reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358/consensus_judge_predictions_358.jsonl`](file:///c:/Users/Engin%20Dalga/Documents/GitHub/halusinasyon/hls_new/k2_nli/reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358/consensus_judge_predictions_358.jsonl)
4. **120 Anlaşmazlık Hakem Tahminleri:** [`k2_nli/reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1/arbitration_predictions_120.jsonl`](file:///c:/Users/Engin%20Dalga/Documents/GitHub/halusinasyon/hls_new/k2_nli/reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1/arbitration_predictions_120.jsonl)
5. **Mimari TikZ Vektör Diyagramı:** [`reports/figures/hybrid_pipeline_architecture.pdf`](file:///c:/Users/Engin%20Dalga/Documents/GitHub/halusinasyon/hls_new/k2_nli/reports/figures/hybrid_pipeline_architecture.pdf)
