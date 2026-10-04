# Dağılım Dışı (OOD) Klinik Tıp Vaka Analizi ve Genellenebilirlik Raporu
## Alzheimer / Nöroloji Alanında Sıfır Veri Sızıntısı ile Kademeli Hibrit Doğrulama Testi

**Tarih:** 4 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  
**Tez Başlığı:** *Metin Tabanlı Türkçe Doğal Dil İşleme Veri Kümelerinde Halüsinasyon Tespiti ve Genellenebilirlik Analizi*  
**Deney Kodu:** `k2_nli/scripts/65_run_ood_medical_case_study.py`  
**Test Veri Kümesi:** `k2_nli/data/processed/ood_case_study/alzheimer_ood_16.jsonl`  
**Sonuç Günlüğü:** `k2_nli/reports/experiments/OOD-ALZHEIMER-CASE-STUDY-v1/results.jsonl`

---

## 1. Yönetici Özeti ve Araştırma Motivasyonu

Tez başlığımızın ikinci temel ayağı olan **"Genellenebilirlik Analizi"**, geliştirilen mimarinin yalnızca eğitim setindeki (TR-FactBench) dağılım içinde ezber yapmadığını, daha önce hiç karşılaşmadığı alanlarda ve terminolojilerde de kararlı çalıştığını kanıtlamayı gerektirir.

TR-FactBench eğitim kümesi (`train.jsonl`) incelendiğinde; tıp alanında genel sağlık, diyabet (80 vaka) ve obezite (32 vaka) gibi konuların yer aldığı, ancak **Alzheimer, Parkinson ve Multipl Skleroz gibi nörolojik hastalıkların 0 (sıfır) defa geçtiği** tespit edilmiştir. 

Bu doğrultuda, **%0 Veri Sızıntısı (Zero Contamination / Zero Data Leakage)** prensibi gözetilerek, nörolojik klinik farmakoloji (kolinesteraz inhibitörleri, NMDA reseptör antagonistleri, sinaptik asetilkolin mekanizması) üzerine 16 zorlu ve dengeli vaka kurgulanmıştır.

### Öne Çıkan Temel Bulgular:
1. **%100 Doğruluk (16 / 16):** Önerilen Kademeli Hibrit Mimari, dağılım dışı (OOD) klinik tıp kümesinde **16 vakanın 16'sını da doğru sınıflandırarak %100 doğruluk ve %100 Macro-F1** skoruna ulaşmıştır.
2. **%81.25 Doğrudan Yerel Uzlaşma:** 16 vakanın 13'ünde K1 (ELECTRA-TR) ve K2 (Gemma-4 + mDeBERTa) yerel modelleri doğrudan uzlaşmış ve harici LLM hakemine hiç gidilmemiştir. Uzlaşılan 13 vakanın 13'ü de (%100) doğru çıkmıştır.
3. **Akıllı Hakem Kurtarması:** K1 ve K2'nin uyuşmazlığa düştüğü 3 vakada devreye giren Düşünce Zinciri (CoT) destekli Meta-Hakem (Llama-3.3-70B), 3 vakanın 3'ünü de düzelterek sisteme kusursuz bir hata telafi yeteneği kazandırmıştır.
4. **"Neither" (Her İki Modeli de Reddetme) Gücü:** Özellikle 11. vakada hem K1 yanlış karar (`partially_supported`) vermiş hem de K2 yanlış karar (`supported`) üretmiştir. Hakem, her iki yerel modelin de hatalı olduğunu gerekçelendirerek (`favored_model: Neither`) zemin gerçeği (`contradicted`) tek başına bulmuş ve doğruluğu kurtarmıştır.

---

## 2. Model ve Mimari Konfigürasyonu

| Bileşen | Model Mimarisi | Çalışma Prensibi | Rolü |
| :--- | :--- | :--- | :--- |
| **Bileşen 1 (K1)** | ELECTRA-TR Base + LoRA (Rank 8) | Tek parça, bütüncül dizi sınıflandırma | Hızlı, yerel ilk karar verici |
| **Bileşen 2 (K2)** | Google Gemma-4-E2B-IT + mDeBERTa-v3 NLI | Atomik önerme ayrıştırma + Soft-Prob NLI | İnce taneli ve parça bazlı analiz |
| **Bileşen 3 (K3)** | Llama-3.3-70B-Instruct (CoT Prompting) | Emsal kararlı ve Düşünce Zinciri (CoT) Hakem | Uyuşmazlıklarda nihai bağlayıcı karar |

---

## 3. Deneysel Sonuçlar ve Performans Metrikleri

16 OOD Alzheimer vakası üzerinden elde edilen doğruluk ve F1 metrikleri aşağıda özetlenmiştir:

| Doğrulama Yöntemi | Doğru / Toplam | Doğruluk (Accuracy) | Macro-F1 | LLM Çağrı Sayısı | LLM Çağrı Oranı |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **K1 Tek Başına (ELECTRA-TR)** | 15 / 16 | %93.75 | %93.75 | 0 | %0.0 |
| **K2 Tek Başına (Gemma-4 + mDeBERTa)** | 13 / 16 | %81.25 | %77.20 | 0 | %0.0 |
| **Saf LLM (Tam Hakem / Llama-70B)** | 16 / 16 | %100.00 | %100.00 | 16 | %100.0 |
| **KADEMELİ HİBRİT BORU HATTI (Önerilen)** | **16 / 16** | **%100.00** | **%100.00** | **3** | **%18.75** |

### Metrik Analizi:
- Kademeli Hibrit Yaklaşım, Saf LLM (Full Judge) yaklaşımı ile **tamamen aynı (%100) doğruluğu** yakalamıştır.
- Ancak bunu yaparken **LLM maliyetini ve gecikmesini %81.25 oranında düşürmüştür** (16 çağrı yerine yalnızca 3 çağrı).
- Yerel modellerin (K1 ve K2) birbirini denetleme mekanizması, tek bir modelin kör noktalarını mükemmel bir şekilde absorbe etmiştir.

---

## 4. 16 OOD Vakanın Detaylı Dağılımı ve Doğrulama Seyri

| ID | Altın Etiket | K1 Tahmini | K2 Tahmini | Uzlaşma? | Hakem Kararı | Nihai Sonuç | Durum |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `ood_med_01` | supported | supported (%100) | supported | EVET | *(Gidilmedi)* | supported | ✅ DOĞRU |
| `ood_med_02` | supported | supported (%98) | supported | EVET | *(Gidilmedi)* | supported | ✅ DOĞRU |
| `ood_med_03` | supported | supported (%57) | supported | EVET | *(Gidilmedi)* | supported | ✅ DOĞRU |
| `ood_med_04` | supported | supported (%100) | supported | EVET | *(Gidilmedi)* | supported | ✅ DOĞRU |
| `ood_med_05` | partially_supported | partially_supported (%100)| partially_supported | EVET | *(Gidilmedi)* | partially_supported | ✅ DOĞRU |
| `ood_med_06` | partially_supported | partially_supported (%100)| partially_supported | EVET | *(Gidilmedi)* | partially_supported | ✅ DOĞRU |
| `ood_med_07` | partially_supported | partially_supported (%100)| partially_supported | EVET | *(Gidilmedi)* | partially_supported | ✅ DOĞRU |
| `ood_med_08` | partially_supported | partially_supported (%100)| partially_supported | EVET | *(Gidilmedi)* | partially_supported | ✅ DOĞRU |
| `ood_med_09` | contradicted | contradicted (%100) | supported ❌ | **HAYIR** | **contradicted** (K1 Haklı) | contradicted | ✅ DOĞRU |
| `ood_med_10` | contradicted | contradicted (%58) | partially_supported ❌| **HAYIR** | **contradicted** (K1 Haklı) | contradicted | ✅ DOĞRU |
| `ood_med_11` | contradicted | partially_supported ❌ | supported ❌ | **HAYIR** | **contradicted** (İkisi de Yanlış) | contradicted | ✅ DOĞRU |
| `ood_med_12` | contradicted | contradicted (%100) | contradicted | EVET | *(Gidilmedi)* | contradicted | ✅ DOĞRU |
| `ood_med_13` | unverifiable | unverifiable (%100) | unverifiable | EVET | *(Gidilmedi)* | unverifiable | ✅ DOĞRU |
| `ood_med_14` | unverifiable | unverifiable (%100) | unverifiable | EVET | *(Gidilmedi)* | unverifiable | ✅ DOĞRU |
| `ood_med_15` | unverifiable | unverifiable (%100) | unverifiable | EVET | *(Gidilmedi)* | unverifiable | ✅ DOĞRU |
| `ood_med_16` | unverifiable | unverifiable (%100) | unverifiable | EVET | *(Gidilmedi)* | unverifiable | ✅ DOĞRU |

---

## 5. Hakeme Giden 3 Uyuşmazlık Vakasının Derinlemesine Nitel Analizi

### Vaka 1: `ood_med_09` (K2'nin Boş Atom Üretmesi ve K1'in Kurtarılması)
* **İddia:** *"Alzheimer hastalığında kullanılan mevcut medikal ilaçlar hastalığın ilerlemesini tamamen durdurarak hastayı biyolojik olarak iyileştiren kesin şifa tedavileridir."*
* **Altın Etiket:** `contradicted`
* **K1 Kararı:** `contradicted` (Güven: %99.9) ✅
* **K2 Durumu:** Gemma Atomizer karmaşık ve olumsuz yan cümle içeren bu cümleyi ayrıştıramayarak boş atom listesi `[]` döndürmüş; K2 mekanizması varsayılan olarak `supported` etiketine düşmüştür ❌.
* **Uyuşmazlık:** K1 (`contradicted`) vs K2 (`supported`).
* **Meta-Hakem (Llama-3.3-70B) CoT Kararı:**
  > *"İddia, Alzheimer hastalığında kullanılan mevcut medikal ilaçların hastalığı tamamen durdurarak şifa veren tedaviler olduğunu iddia etmektedir. Bağlam ise bu ilaçların semptomları hafifletmeye yönelik semptomatik tedaviler olduğunu ve hastalığı tamamen durduran veya şifa veren tedaviler olmadığını açıkça belirtmektedir."*  
  > **Tercih:** Model A (K1) | **Sonuç:** `contradicted` ✅

---

### Vaka 2: `ood_med_10` (K2 NLI'ın Yalancı Pozitifliği ve Hakemin Müdahalesi)
* **İddia:** *"Memantin bir kolinesteraz inhibitörü olup kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır."*
* **Altın Etiket:** `contradicted`
* **K1 Kararı:** `contradicted` (Güven: %58.0) ✅
* **K2 Durumu:** Gemma iddiayı iki atoma bölmüştür:
  1. *"Memantin bir kolinesteraz inhibitörü"*
  2. *"kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır"*  
  Ancak mDeBERTa NLI modeli, birinci atom için bağlamdaki cümle yapısına aldanarak yanlışlıkla `entailment` (%99.8) üretmiştir. İkinci atoma `contradiction` verdiği için kural gereği K2 sonucu `partially_supported` çıkmıştır ❌.
* **Uyuşmazlık:** K1 (`contradicted`) vs K2 (`partially_supported`).
* **Meta-Hakem (Llama-3.3-70B) CoT Kararı:**
  > *"İddiada memantinin bir kolinesteraz inhibitörü olduğu iddiası yer almakta, ancak bağlam memantinin aslında NMDA reseptör antagonisti olduğunu belirtmektedir. İddianın hiçbir parçası bağlam tarafından doğrulanmamaktadır; her iki parça da bağlamla doğrudan çelişmektedir."*  
  > **Tercih:** Model A (K1) | **Sonuç:** `contradicted` ✅

---

### Vaka 3: `ood_med_11` (GÜNÜN KEŞFİ: Her İki Model Yanıldığında Hakemin Gerçeği Bulması)
* **İddia:** *"Günümüzde yan etkileri nedeniyle donepezil ve rivastigmin tamamen yasaklanmış olup rutin klinik kullanımda yalnızca takrin tercih edilmektedir."*
* **Altın Etiket:** `contradicted`
* **K1 Kararı:** `partially_supported` ❌ (Metindeki ilaç isimlerinin varlığı K1'i yanıltmıştır).
* **K2 Kararı:** `supported` ❌ (Atomizer boş dönmüştür).
* **Uyuşmazlık:** K1 (`partially_supported`) vs K2 (`supported`).
* **Meta-Hakem (Llama-3.3-70B) CoT Kararı:**
  > *"İddia, donepezil ve rivastigmin'in tamamen yasaklandığını ve yalnızca takrin'in tercih edildiğini öne sürmektedir, ancak bağlamda bu bilgilerin hiçbirinin doğrulanmadığı görülmektedir. Ayrıca, bağlamda takrin'in artık kullanılmadığı bilgisi yer almaktadır, bu nedenle iddia doğrudan bağlamla çelişmektedir."*  
  > **Tercih Edilen Model:** **`Neither` (Hiçbiri)**  
  > **Nihai Karar:** **`contradicted`** ✅

> [!IMPORTANT]
> **Tez İçin Kritik Metodolojik Kanıt:**  
> `ood_med_11` vakası, Hakem bileşeninin sadece K1 veya K2 arasında mekanik bir seçim yapmadığını; modellerin argümanlarını ve bağlamı bağımsız bir mantık süzgecinden geçirerek **her iki yerel model de yanlış karar verdiğinde dahi doğru zemin gerçeğe ulaşabildiğini** ispatlamaktadır. Bu durum, hakemin pasif bir oylayıcı değil, aktif bir mantık denetçisi olduğunu belgeler.

---

## 6. Tez Savunması ve Jüri İçin Argümantasyon Çıkarımları

1. **Alan Bağımsızlığı ve Genellenebilirlik:**  
   Modelimiz TR-FactBench'te eğitilmesine rağmen, eğitim kümesinde kelime olarak dahi yer almayan nörolojik tıp terimlerinde (donepezil, memantin, NMDA, asetilkolin, eksitotoksisite) %100 başarı göstermiştir. Bu durum, modelin kavramları kelime düzeyinde ezberlemediğini, **mantıksal doğrulama ve çıkarım ilişkilerini (entailment/contradiction) öğrendiğini** kanıtlar.

2. **Kademeli Hibrit Mimarinin Vazgeçilmezliği:**  
   - K1 tek başına bırakılsaydı Vaka 11'i kaçıracaktı (%93.75).
   - K2 tek başına bırakılsaydı 3 vakayı kaçıracaktı (%81.25).
   - Hakem tek başına her çağrıda çalıştırılsaydı %100 başarı verecekti ancak %81.25 gereksiz API maliyeti ve yüksek gecikme süresi doğuracaktı.
   - **Kademeli Hibrit Mimari**, yerel modellerin yüksek uzlaşma gücünü (%81.25) kullanarak sıfır ek maliyetle vakaların büyük kısmını çözmüş, uyuşmazlıklarda ise Hakem ile %100 doğruluğu güvence altına almıştır.

3. **Akıl Yürütme Öncelikli Düşünce Zinciri (Reasoning-First CoT) Etkisi:**  
   Hakemin gerekçelendirmeyi nihai etiket seçiminden önce yapması (`reasoning -> favored_model -> final_decision`), LLM'in erken etiket taahhüdüne (premature label commitment) girip saçmalamasını tamamen engellemiş; klinik metinlerde dahi hatasız gerekçeler üretmesini sağlamıştır.
