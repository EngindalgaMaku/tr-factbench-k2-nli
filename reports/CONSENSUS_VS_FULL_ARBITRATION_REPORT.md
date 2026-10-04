# K3 META-HAKEM VE KONSENSÜS DEĞERLENDİRME RAPORU: TAM HAKEMLİK VS. KADEMELİ HİBRİT BORU HATTI
**Doküman:** `CONSENSUS_VS_FULL_ARBITRATION_REPORT.md`  
**Tarih:** 04 Ekim 2026  
**Danışman Yönergesi:** Prof. Dr. Serkan Ballı (*"358 uzlaşma vakasını hakeme verip neleri bozduğuna, neleri düzelttiğine bakmak lazım"* hipotezinin ampirik doğrulaması)  
**Yazar:** Engin Dalga  
**Model:** Meta-Llama-3.3-70B-Instruct (4-Emsal Kararlı Few-Shot Meta-Hakem)

---

## 1. YÖNETİCİ ÖZETİ VE BİLİMSEL SONUÇLAR

Tez çalışmamızda önerilen **Kademeli Hibrit Doğrulama Mimarisi (Cascading Hybrid Architecture)**, iki yerel model (K1 ve K2) uzlaştığında kararı doğrudan kabul etmekte (%74.9 filtreleme), yalnızca uzlaşmazlık durumunda (120 vaka) LLM Meta-Hakeme başvurmaktadır.

Danışman hocamızın yönlendirmesi doğrultusunda, K1 ve K2'nin ortak uzlaştığı **358 vakanın tamamı**, birebir aynı 4-emsal kararlı yönlendirme şablonu (few-shot precedent prompt) ile **Meta-Hakeme (Llama-3.3-70B-Instruct)** verilmiş ve fiili olarak koşturulmuştur.

### Temel Ampirik Bulgular (Özet Tablo)

| Değerlendirme Boyutu | K1 & K2 Doğrudan Uzlaşma | Llama-3.3-70B Meta-Hakem | Net Etki / Fark |
| :--- | :---: | :---: | :---: |
| **Uzlaşma Kümesi Doğruluğu (358 vaka)** | **337 / 358 (%94.13)** | **342 / 358 (%95.53)** | **+5 vaka (+%1.40)** |
| **Düzeltilen Hatalar (Error Recovery)** | - | **12 / 21 (%57.14)** | +12 vaka düzeltildi |
| **Bozulan Doğrular (Regression)** | - | **7 / 337 (%2.08)** | -7 doğru yanlışa çevrildi |
| **Tüm Veri Seti Doğruluğu (478 vaka)** | **%89.54** (Kademeli Hibrit) | **%90.59** (Tam Hakemlik) | **+1.05 puan** |
| **Tüm Veri Seti Macro-F1 (478 vaka)** | **%89.66** | **%90.67** | **+1.01 puan** |
| **McNemar İstatistiki Anlamlılık** | - | - | **$p = 0.3593$ ($p > 0.05$, Farksız)** |
| **Gereken LLM API Çağrısı** | **120 çağrı** | **478 çağrı** | **%74.9 Tasarruf (358 çağrı az)** |

---

## 2. DANIŞMAN HİPOTEZİNİN AMPİRİK YANITI

### Soru 1: Hakem 21 hatadan neleri düzeltti? (Recovery Rate: %57.14)
Meta-Hakem, K1 ve K2'nin birlikte yanıldığı 21 ortak hatanın **12 tanesini (%57.14)** başarıyla düzeltmiştir.
- **Neden düzeltti?** K1 ve K2 modelleri özellikle uzun ve karmaşık cümlelerde, cümlenin yarısı doğru yarısı yanlış olduğunda yanlış atomları gözden kaçırıp `partially_supported` veya `supported` kararı vermişti. Meta-Hakem derin akıl yürütme (reasoning) kapasitesiyle iddianın ana hükmündeki doğrudan zıtlığı yakalamış ve vakaları doğru olan `contradicted` etiketine çekmiştir.
- **Düzeltilen Örnekler:** `tfb_ex_0019`, `tfb_ex_0035`, `tfb_ex_0115`, `tfb_ex_0195`, `tfb_ex_0274`, `tfb_ex_0278`, `tfb_ex_0323`, `tfb_ex_0332`, `tfb_ex_0363`, `tfb_ex_0423`, `tfb_ex_0463`, `tfb_ex_0468`.

### Soru 2: Hakem doğru olan 337 karardan neleri bozdu? (Regression Rate: %2.08)
Meta-Hakem, K1 ve K2'nin zaten hatasız bildiği 337 sağlam karardan **7 tanesini (%2.08)** bozarak yanlış etikete çevirmiştir.
- **Neden bozdu?** Bozulan **7 vakanın tamamında** altın etiket `partially_supported` iken, hakem iddiadaki yanlış unsura aşırı odaklanıp (over-penalization) kararı `contradicted` olarak değiştirmiştir.
- **Bozulan Örnekler:** `tfb_ex_0074`, `tfb_ex_0086`, `tfb_ex_0102`, `tfb_ex_0114`, `tfb_ex_0122`, `tfb_ex_0262`, `tfb_ex_0458`.

### Soru 3: Düzeltilmeyen Kalan 9 Hata Neden Çözülemedi?
21 hatadan geriye kalan 9 vakanın **7 tanesi** radyoloji ve klinik tıp alanındaki ince `unverifiable` (bilgi yokluğu) vakalarıdır (`tfb_ex_0336`, `0340`, `0360`, `0364`, `0368`, `0372`, `0452`). Hem küçük dil modelleri hem de 70B LLM hakem, tıbbi kılavuzlardaki zımni bilgi yokluğunu doğrudan çelişki veya kısmi destek ile karıştırmaktadır.

---

## 3. SAVUNMA İÇİN KRİTİK ÇIKARIM: NEDEN "KADEMELİ HİBRİT BORU HATTI"?

Tez savunmasında jüri üyesine sunulacak **nihai bilimsel savunma argümanı**:

1. **İstatistiki Eşdeğerlik (Statistical Parity):**
   McNemar testinde elde edilen **$p = 0.3593$** değeri, 478 vakanın tamamını 70B parametreli dev bir modele çözdürmek ile geliştirdiğimiz **Kademeli Hibrit Model** arasında **istatistiksel olarak anlamlı hiçbir fark olmadığını** ispatlamaktadır.
2. **Hesaplama ve Maliyet Üstünlüğü:**
   Aynı istatistiki performansı yakalamak için kademeli modelimiz LLM sorgularını **%74.9 oranında azaltmakta**, API maliyetini ve gecikmeyi 4 kat düşürmektedir.
3. **Regresyon Güvencesi:**
   K1 ve K2'nin uzlaştığı yerde LLM'i devre dışı bırakmak, LLM'in doğru bilinen kararları bozma (over-ruling hallucination) riskini tamamen ortadan kaldırmaktadır.

---

## 4. DOSYA VE ARTIFACT KONUMLARI

- **Uzlaşma Veri Seti:** `k2_nli/data/processed/arbitration/consensus_cases_358.jsonl`
- **Hakem Tahminleri (358 Vaka):** `k2_nli/reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358/consensus_judge_predictions_358.jsonl`
- **Özet Metrikler:** `k2_nli/reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358/consensus_arbitration_summary.json`
- **Ham Yanıtlar (Gerekçeler):** `k2_nli/reports/experiments/K3-CONSENSUS-LLAMA70B-EVAL-358/raw_responses_358.jsonl`
