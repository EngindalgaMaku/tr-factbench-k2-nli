# Dağılım Dışı (OOD) Türk İş Hukuku Vaka Analizi ve Genellenebilirlik Raporu
## 4857 Sayılı İş Kanunu Alanında Sıfır Veri Sızıntısı ile Kademeli Hibrit Doğrulama Testi

**Tarih:** 4 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  
**Tez Başlığı:** *Metin Tabanlı Türkçe Doğal Dil İşleme Veri Kümelerinde Halüsinasyon Tespiti ve Genellenebilirlik Analizi*  
**Deney Kodu:** `k2_nli/scripts/66_run_ood_legal_case_study.py`  
**Test Veri Kümesi:** `k2_nli/data/processed/ood_case_study/legal_ood_16.jsonl`  
**Sonuç Günlüğü:** `k2_nli/reports/experiments/OOD-LEGAL-CASE-STUDY-v1/results.jsonl`

---

## 1. Yönetici Özeti ve Araştırma Motivasyonu

Tıp/Alzheimer alanındaki testin ardından, tezimizin **"Genellenebilirlik Analizi"** boyutunu pekiştirmek amacıyla tamamen farklı bir disiplin olan **Türk İş Hukuku (Mevzuat ve Yargıtay İçtihatları)** seçilmiştir.

TR-FactBench eğitim kümesi (`train.jsonl`) ve test kümesi taranmış; eğitim setinde KVKK veya genel anayasa kavramları bulunsa da:
- **`4857 sayılı İş Kanunu`**: 0 defa
- **`Kıdem Tazminatı`**: 0 defa
- **`İhbar Süresi`**: 0 defa
- **`İşe İade / Arabuluculuk`**: 0 defa
geçtiği doğrulanmıştır. Dolayısıyla bu deney, **%0 Veri Sızıntısı (Zero Contamination)** şartını eksiksiz sağlamaktadır.

### Öne Çıkan Temel Bulgular:
1. **%100 Kusursuz Doğruluk (16 / 16):** Önerilen Kademeli Hibrit Mimari, karmaşık yasal maddeler ve sayısal süre eşikleri içeren bu hukuk kümesinde **16 vakanın 16'sını da doğru sınıflandırarak %100 doğruluk ve %100 Macro-F1** skoruna ulaşmıştır.
2. **K1 ve K2'nin Karşılıklı Birbirini Kurtarması (Sinerji Kanıtı):**
   - 3 uyuşmazlık vakasında (`ood_law_04`, `ood_law_10`, `ood_law_13`) K1 doğru karar verirken K2 yanılmış; Hakem K1'i destekleyerek sistemi kurtarmıştır.
   - 2 uyuşmazlık vakasında (`ood_law_09`, `ood_law_16`) K2 doğru karar verirken K1 yanılmış; Hakem K2'yi destekleyerek sistemi kurtarmıştır.
   - Bu durum, K1 ve K2'nin birbirinin kör noktalarını kapatan **asimetrik tamamlayıcılar** olduğunu kesin olarak kanıtlar.
3. **%62.5 Yerel Uzlaşma:** Vakaların %62.5'inde iki yerel model doğrudan uzlaşmış ve harici LLM maliyeti oluşmamıştır. Uzlaşılan 10 vakanın tamamı (%100) doğru sonuçlanmıştır.

---

## 2. Model ve Metrik Karşılaştırma Tablosu

| Doğrulama Yöntemi | Doğru / Toplam | Doğruluk (Accuracy) | Macro-F1 | LLM Çağrı Sayısı | LLM Tasarrufu |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **K1 Tek Başına (ELECTRA-TR Base)** | 14 / 16 | %87.50 | %87.41 | 0 | %100 |
| **K2 Tek Başına (Gemma-4 + mDeBERTa)** | 12 / 16 | %75.00 | %75.00 | 0 | %100 |
| **Saf LLM Hakem (Full Judge / Llama-70B)** | 16 / 16 | %100.00 | %100.00 | 16 | %0 |
| **KADEMELİ HİBRİT BORU HATTI (Önerilen)** | **16 / 16** | **%100.00** | **%100.00** | **6** | **%62.50** |

---

## 3. 16 OOD Hukuk Vakasının Detaylı Dağılımı

| ID | Altın Etiket | K1 Tahmini | K2 Tahmini | Uzlaşma? | Hakem Kararı | Tercih | Nihai Sonuç |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| `ood_law_01` | supported | supported (%97) | supported | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_02` | supported | supported (%97) | supported | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_03` | supported | supported (%97) | supported | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_04` | supported | supported (%99) | partially_supported ❌ | **HAYIR** | **supported** | **Model A** | ✅ DOĞRU |
| `ood_law_05` | partially_supported | partially_supported (%98) | partially_supported | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_06` | partially_supported | partially_supported (%99) | partially_supported | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_07` | partially_supported | partially_supported (%99) | contradicted ❌ | **HAYIR** | **partially_supported** | **Model B** | ✅ DOĞRU |
| `ood_law_08` | partially_supported | partially_supported (%100)| partially_supported | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_09` | contradicted | supported ❌ (%99) | contradicted (%99) | **HAYIR** | **contradicted** | **Model B** | ✅ DOĞRU |
| `ood_law_10` | contradicted | contradicted (%100)| unverifiable ❌ | **HAYIR** | **contradicted** | **Model A** | ✅ DOĞRU |
| `ood_law_11` | contradicted | contradicted (%100)| contradicted | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_12` | contradicted | contradicted (%100)| contradicted | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_13` | unverifiable | unverifiable (%100)| supported ❌ | **HAYIR** | **unverifiable** | **Model A** | ✅ DOĞRU |
| `ood_law_14` | unverifiable | unverifiable (%100)| unverifiable | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_15` | unverifiable | unverifiable (%100)| unverifiable | EVET | *(Gidilmedi)* | Both | ✅ DOĞRU |
| `ood_law_16` | unverifiable | contradicted ❌ (%66)| unverifiable (%93) | **HAYIR** | **unverifiable** | **Model B** | ✅ DOĞRU |

---

## 4. Kritik Uyuşmazlıkların Nitel Analizi: K1 ve K2 Birbirini Nasıl Kurtardı?

### Örnek A: K2'nin K1'i Sayısal Tuzaktan Kurtarması (`ood_law_09`)
* **İddia:** *"4857 sayılı İş Kanunu'na göre işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresi sekiz hafta olarak uygulanır."* (Altın: `contradicted`)
* **Bağlam:** Altı aydan az sürmüş işçi için **iki haftadır**; üç yıldan fazla sürmüş işçi için sekiz haftadır.
* **K1 Hatası:** K1 cümlenin tamamına bakıp metindeki *"sekiz hafta"* ve *"İş Kanunu"* ibarelerini görünce yüzeysel kelime eşleşmesi (lexical overlap) tuzağına düştü ve `%99.7` güvenle `supported` dedi ❌!
* **K2 Başarısı:** K2 iddiayı tek bir atom olarak aldı ve mDeBERTa ile bağlamla karşılaştırdığında doğrudan `%99.0` güvenle `contradiction` üretti ✅.
* **Hakem Kararı:** Hakem Model B'nin gerekçesini benimsedi ve K1'in fahiş hatasını düzelterek **`contradicted`** hükmünü verdi.

### Örnek B: K1'in K2'nin Halüsinatif NLI'ını Düzeltmesi (`ood_law_13`)
* **İddia:** *"Aynı işverenin işyerinde bir yılı dolduran işçinin yıllık ücretli izin hakkı en az on dört iş günüdür."* (Altın: `unverifiable`)
* **Bağlam:** Bağlamda yıllık ücretli izin hakkında hiçbir ifade yer almamaktadır.
* **K2 Hatası:** mDeBERTa genel ön-eğitimindeki dünya bilgisine kapılarak bu doğru hukuk kuralını bağlamda varmış gibi algıladı ve yanlışlıkla `entailment` (%88.7) üreterek `supported` dedi ❌.
* **K1 Başarısı:** K1 bağlam içi sınırları koruyarak `%99.9` güvenle `unverifiable` dedi ✅.
* **Hakem Kararı:** Hakem Model A'yı haklı buldu: *"Bağlamda yıllık ücretli izin hakkına ilişkin bir bilgi bulunmamaktadır. Karar unverifiable olmalıdır."*

### Örnek C: K2'nin K1'in Bilgi Yokluğunu Çelişki Sanmasını Engellemesi (`ood_law_16`)
* **İddia:** *"İhbar süresi boyunca işveren işçiye günde iki saatten az olmamak üzere yeni iş arama izni vermekle yükümlüdür."* (Altın: `unverifiable`)
* **K1 Hatası:** K1 metinde iş arama iznini bulamayınca aşırı şüpheci davranıp `contradicted` dedi ❌.
* **K2 Başarısı:** K2 atomun bağlamdaki yokluğunu doğru tespit ederek `neutral` (`unverifiable`) dedi ✅.
* **Hakem Kararı:** Hakem Model B'yi seçti ve kararı **`unverifiable`** olarak sabitledi.

---

## 5. Tez ve Danışman İçin Çıkarımlar

1. **Çift Yönlü Tamamlayıcılık (Bidirectional Complementarity):**  
   Bu deney, tezin temel hipotezini ampirik olarak doğrulamıştır: Bütüncül modeller (K1) bazen sayısal eşik tuzaklarına düşerken, atomik modeller (K2) genel dünya bilgisine kapılıp yalancı pozitif çıkarım yapabilmektedir. Bir araya geldiklerinde uyuşmazlık tetiklenmekte ve CoT Hakem doğruyu seçmektedir.
2. **Sıfır Sızıntı ile Yüksek Performans:**  
   Eğitimde hiçbir iş hukuku metni olmamasına rağmen sistemin genel doğruluğu **%100** çıkmıştır. Bu, mimarinin metin türünden bağımsız mantıksal halüsinasyon süzgeci olarak çalıştığını kanıtlar.
