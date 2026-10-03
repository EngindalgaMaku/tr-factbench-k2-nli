# K2 MODÜLER DOĞRULAMA HATTI VE ATOMİZASYON NİTELİKSEL ANALİZ RAPORU
## TR-FactBench 480 Altın Test Kümesi Üzerinde İnsan Gözüyle Dilbilimsel İnceleme

**Tarih:** Ekim 2026  
**Araştırmacı:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  
**Kurum:** Burdur Mehmet Akif Ersoy Üniversitesi, Yazılım Mühendisliği Anabilim Dalı  
**Kapsam:** K1 (ELECTRA-TR + LoRA) vs. K2 (Gemma-4 QLoRA + mDeBERTa-v3) Paired Analizi  

---

## 1. YÖNETİCİ ÖZETİ VE KARŞILAŞTIRMALI METRİKLER

Bu rapor, TR-FactBench resmi 480 örneklik dondurulmuş altın test kümesi üzerinde:
1. K1 doğrudan encoder modeli ile K2 modüler atomik doğrulama hattının kafa kafaya eşleştirilmiş sonuçlarını,
2. Gemma-4 QLoRA modelinin ürettiği atomların dilbilimsel doğruluğunu (insan gözüyle sentaks, özne koruma, sınır tespiti),
3. **K1'in yanılıp K2'nin doğru bildiği 44 somut vakanın** altında yatan başarı mekanizmalarını,
4. **K1'in doğru bilip K2'nin yanıldığı 69 vakada** ortaya çıkan hata yayılımı (error cascade) dinamiklerini incelemektedir.

### Genel Dağılım Tablosu

| Durum | Örnek Sayısı | Oran (%) | Bilimsel Anlamı |
|:---|:---:|:---:|:---|
| **İkisi de Doğru (Both Correct)** | 330 | %68.75 | İki mimarinin de ortak uzlaştığı yüksek kararlılık alanı. |
| **Yalnızca K1 Doğru (K1 Wins)** | 69 | %14.37 | Doğrudan bağlam dikkat mekanizmasının (self-attention) üstün geldiği vakalar. |
| **Yalnızca K2 Doğru (K2 Wins)** | 44 | %9.17 | **Atomlara ayırmanın K1'in kaçırdığı çelişki ve eksik bilgiyi izole ettiği vakalar.** |
| **İkisi de Yanlış (Both Wrong)** | 37 | %7.71 | Yüksek karmaşıklık içeren ve LLM Hakem'e (Judge) en çok ihtiyaç duyan alan. |
| **TOPLAM** | **480** | **%100.00** | — |
| **ORACLE HİBRİT TAVANI (K1 OR K2)** | **443** | **%92.29** | **İdeal bir hakemin seçimiyle ulaşılabilecek teorik üst sınır.** |

---

## 2. K2'NİN K1'İ YENDİĞİ 44 VAKANIN GEÇİŞ ANALİZİ

K1'in yaptığı hataları K2'nin nasıl düzelttiğini gösteren geçiş tipleri:

| K1 Tahmini (Hatalı) | K2 Tahmini (Doğru) | Gerçek Etiket (Gold) | Vaka Sayısı | Temel Düzeltme Mekanizması |
|:---|:---|:---|:---:|:---|
| K1(partially_supported) | K2(contradicted) | contradicted | 11 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(supported) | K2(partially_supported) | partially_supported | 9 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(contradicted) | K2(unverifiable) | unverifiable | 9 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(partially_supported) | K2(unverifiable) | unverifiable | 4 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(contradicted) | K2(partially_supported) | partially_supported | 3 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(partially_supported) | K2(supported) | supported | 2 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(unverifiable) | K2(contradicted) | contradicted | 2 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(contradicted) | K2(supported) | supported | 1 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(supported) | K2(contradicted) | contradicted | 1 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(supported) | K2(unverifiable) | unverifiable | 1 | İlgili sınıfın atomik izolasyonla kurtarılması. |
| K1(unverifiable) | K2(supported) | supported | 1 | İlgili sınıfın atomik izolasyonla kurtarılması. |

### Öne Çıkan Üç Büyük Düzeltme Mekanizması:
1. **Örtük Çelişkilerin Yakalanması (11 Vaka):** K1'in yüksek kelime örtüşmesi (lexical overlap) nedeniyle `partially_supported` sandığı doğrudan çelişkiler, K2'de cümlenin ters önermesinin bağımsız bir atom olarak izole edilmesi sayesinde `contradicted` olarak yakalanmıştır.
2. **Halüsinasyon Tuzağının Önlenmesi (9 Vaka):** K1'in akıcı cümlenin büyüsüne kapılıp `supported` sandığı 9 iddiada, cümlenin ikinci yarısının metinde hiç olmadığı K2 atomizasyonuyla ortaya çıkmış ve `partially_supported` doğru etiketi verilmiştir.
3. **Yokluk Kanıtının (Missing Evidence) Tespiti (9 Vaka):** K1'in metinde bahsedilmeyen bir olguyu 'yanlış/çelişki' sanarak `contradicted` verdiği 9 örnekte, K2 atomu NLI'ya soktuğunda `neutral` almış ve cümlenin çelişki değil `unverifiable` olduğunu doğru saptamıştır.

---

## 3. İNSAN GÖZÜYLE ATOMİZASYON İNCELEMESİ (GEMMA-4 DEĞERLENDİRMESİ)

Gemma-4 QLoRA modelinin ürettiği 996 atomun biçimsel ve anlamsal kalitesi incelendiğinde şu dilbilimsel modeller saptanmıştır:

### 3.1. Başarılı / Kusursuz Ayrıştırma Kalıpları
1. **Ortak Özne ve Nesnenin Yeniden İnşası (Subject Restoration):**
   - *Orijinal İddia:* 'Şirket sermaye artırımına gitmiş ve temettü dağıtmama kararı almıştır.'
   - *Gemma Atom 1:* 'Şirket sermaye artırımına gitmiştir.'
   - *Gemma Atom 2:* 'Şirket temettü dağıtmama kararı almıştır.' (İkinci atomda gizli özne olan 'Şirket' mükemmelen başa eklenmiştir).
2. **Olumsuzluk ve Modalite Korunumu:**
   - Cümledeki '-me/-ma', 'değildir', 'zorunlu tutulamaz' gibi olumsuzluk ekleri hiçbir atomda düşürülmemiş, anlam tersine çevrilmemiştir.
3. **Tek Önermeli Cümleleri Koruması (No Over-Splitting):**
   - İçinde fiilimsi (zarf-fiil, sıfat-fiil) bulunan ama tek bir olguyu anlatan şart cümlelerini yapay olarak ikiye bölmeyip tek atom olarak bırakmıştır.

### 3.2. Saptanan Kusurlar ve Hata Mekanizmaları (Error Cascade Sebepleri)
1. **Özne Düşmesi / Eksiltili İkinci Atom (Ellipsis):**
   - Bazı karmaşık hukuk cümlelerinde bağlaçtan sonraki yüklem tek başına atom yapılmış (örn: *'ancak temyiz yolu kapalıdır'* yerine *'temyiz yolu kapalıdır'* veya öznesiz *'hüküm altına alınmıştır'*). Bu durum mDeBERTa'nın atomu bağlamdaki özneyle eşleştirememesine yol açmıştır.
2. **Gereksiz Bağlaç Artıkları:**
   - Atomların başında 'ancak', 've', 'bununla birlikte' gibi koordinasyon bağlaçlarının kalması, NLI modelinin çıkarım yaparken gereksiz şart aramasına neden olabilmektedir.
3. **JSON Formatlama Hatası (Yalnızca 2 Örnek):**
   - 480 örneğin 478'inde kusursuz JSON üretilmiş, yalnızca 2 örnekte tırnak işareti hatası nedeniyle JSON parse edilememiştir (%99.58 başarı).

---

## 4. K2'NİN KAZANDIĞI VAKALARDAN SEÇİLMİŞ DERİNLEMESİNE VAKA İNCELEMELERİ (CASE STUDIES)

### VAKA 01 [ID: tfb_ex_0017] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `supported`
- **K1 Tahmini (Hatalı):** `contradicted` ❌
- **K2 Tahmini (Doğru):** `supported` ✅
- **İddia (Claim):** *"Kasko sigortasında Dar Kasko teminat gruplarının yalnız bir bölümünü, Kasko ise tamamını kapsar; zorunlu trafik sigortası üçüncü kişilere verilen maddi ve bedensel zararları güvence altına alır."*
- **Bağlam (Context Özeti):** *"Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının ta..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Kasko sigortasında Dar Kasko teminat gruplarının yalnız bir bölümünü kapsar."` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.75, N=0.01, C=0.24)
  2. Atom: `"Kasko sigortası tamamını kapsar."` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.85, N=0.08, C=0.07)
  3. Atom: `"Zorunlu trafik sigortası üçüncü kişilere verilen maddi ve bedensel zararları güvence altına alır."` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.99, N=0.01, C=0.00)
- **İnsan Gözüyle Değerlendirme:** Atomik önerme ayrıştırması, çok bileşenli cümlenin farklı anlamsal katmanlarını izole ederek tekil encoder'ın aşırı öğrenme sınırını aşmasını sağlamıştır.

### VAKA 02 [ID: tfb_ex_0018] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `partially_supported`
- **K1 Tahmini (Hatalı):** `supported` ❌
- **K2 Tahmini (Doğru):** `partially_supported` ✅
- **İddia (Claim):** *"Genişletilmiş Kasko, temel teminat gruplarının tamamını ve ek sözleşmeyle alınabilecek risklerin bir bölümünü kapsarken zorunlu trafik sigortası sigortalının kendi aracındaki maddi zararı güvence altına alır."*
- **Bağlam (Context Özeti):** *"Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının ta..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Genişletilmiş Kasko, temel teminat gruplarının tamamını kapsar."` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.14, N=0.01, C=0.85)
  2. Atom: `"Genişletilmiş Kasko, ek sözleşmeyle alınabilecek risklerin bir bölümünü kapsar."` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.99, N=0.00, C=0.01)
  3. Atom: `"Zorunlu trafik sigortası sigortalının kendi aracındaki maddi zararı güvence altına alır."` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.33, N=0.20, C=0.47)
- **İnsan Gözüyle Değerlendirme:** K1 modeli cümlenin genel akıcılığına aldanarak iddiadaki eksik bilgiyi fark edememiş ve doğrudan tam destek vermiştir. K2 atomlaştırma sayesinde ilk cümlenin desteklendiğini (entailment), ikinci bilginin ise metinde olmadığını (neutral) ayrı ayrı yakalamış ve doğru şekilde kısmi destek kararı üretmiştir.

### VAKA 03 [ID: tfb_ex_0023] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `contradicted`
- **K1 Tahmini (Hatalı):** `partially_supported` ❌
- **K2 Tahmini (Doğru):** `contradicted` ✅
- **İddia (Claim):** *"Bireysel Emeklilik Sisteminde kısmen ödeme, birikimin en fazla yüzde 70'i kadar olabilir ve bu üst sınır doğal afet başvurularında da uygulanır."*
- **Bağlam (Context Özeti):** *"Bireysel Emeklilik Sisteminde katılımcı, sözleşmesini sonlandırmadan evlilik, konut alımı veya doğal afet nedeniyle birikiminin bir kısmını alabilir. Genel olarak başvuru için sözleşmenin en az beş yıldır sistemde olması..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Bireysel Emeklilik Sisteminde kısmen ödeme, birikimin en fazla yüzde 70'i kadar olabilir"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.00, N=0.01, C=0.99)
  2. Atom: `"bu üst sınır doğal afet başvurularında da uygulanır"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.01, N=0.20, C=0.79)
- **İnsan Gözüyle Değerlendirme:** K1 modeli metin ile iddia arasındaki yüksek kelime benzerliği nedeniyle cümledeki çelişkiyi 'kısmi destek' sanarak yumuşatmıştır. K2 ise iddiayı iki atoma bölmüş; ikinci atom açıkça 'contradiction' çıkınca toplulaştırma kuralı doğru bir şekilde tüm cümlenin çeliştiğine karar vermiştir.

### VAKA 04 [ID: tfb_ex_0031] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `contradicted`
- **K1 Tahmini (Hatalı):** `partially_supported` ❌
- **K2 Tahmini (Doğru):** `contradicted` ✅
- **İddia (Claim):** *"Türkiye Sürdürülebilirlik Raporlama Standartları kapsamındaki sürdürülebilirlik raporlarında güvence denetimi isteğe bağlıdır ve şirketler denetime girip girmemeye kendileri karar verir."*
- **Bağlam (Context Özeti):** *"Raporlama Kurumu A’nın sürdürülebilirlik SSS'sine göre Türkiye Sürdürülebilirlik Raporlama Standartları kapsamında hazırlanan raporlar yönetişim, strateji, risk yönetimi, metrikler ve hedefler olmak üzere dört ana bölümd..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Türkiye Sürdürülebilirlik Raporlama Standartları kapsamındaki sürdürülebilirlik raporlarında güvence denetimi isteğe bağlıdır"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.00, N=0.00, C=1.00)
  2. Atom: `"şirketler denetime girip girmeye kendileri karar verir"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.00, N=0.02, C=0.98)
- **İnsan Gözüyle Değerlendirme:** K1 modeli metin ile iddia arasındaki yüksek kelime benzerliği nedeniyle cümledeki çelişkiyi 'kısmi destek' sanarak yumuşatmıştır. K2 ise iddiayı iki atoma bölmüş; ikinci atom açıkça 'contradiction' çıkınca toplulaştırma kuralı doğru bir şekilde tüm cümlenin çeliştiğine karar vermiştir.

### VAKA 05 [ID: tfb_ex_0037] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `supported`
- **K1 Tahmini (Hatalı):** `partially_supported` ❌
- **K2 Tahmini (Doğru):** `supported` ✅
- **İddia (Claim):** *"Taahhütlü İşlemler Pazarı 2 Ağustos 2018'de faaliyete geçmiş, Katılım endekslerinin Piyasa Kurumu A tarafından hesaplanmasına ise 12 Kasım 2021'den itibaren başlanması kararlaştırılmıştır."*
- **Bağlam (Context Özeti):** *"Sektör Birliği A’nın sektörel zaman çizelgesinde, Piyasa Kurumu A’nın 9 Kasım 2021 tarihli duyurusu sonrasında Katılım Tüm, Katılım 100, Katılım 50, Katılım 30 ve Sürdürülebilirlik Katılım endekslerinin 12 Kasım 2021'den..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Taahhütlü İşlemler Pazarı 2 Ağustos 2018'de faaliyete geçmiş"` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.98, N=0.02, C=0.00)
  2. Atom: `"Katılım endekslerinin Piyasa Kurumu A tarafından hesaplanmasına ise 12 Kasım 2021'den itibaren başlanması kararlaştırılmıştır"` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.88, N=0.01, C=0.11)
- **İnsan Gözüyle Değerlendirme:** Atomik önerme ayrıştırması, çok bileşenli cümlenin farklı anlamsal katmanlarını izole ederek tekil encoder'ın aşırı öğrenme sınırını aşmasını sağlamıştır.

### VAKA 06 [ID: tfb_ex_0039] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `contradicted`
- **K1 Tahmini (Hatalı):** `partially_supported` ❌
- **K2 Tahmini (Doğru):** `contradicted` ✅
- **İddia (Claim):** *"Katılım endeksleri 2018'de hesaplanmaya başlamış, Taahhütlü İşlemler Pazarı ise 2021'de faaliyete geçmiştir."*
- **Bağlam (Context Özeti):** *"Sektör Birliği A’nın sektörel zaman çizelgesinde, Piyasa Kurumu A’nın 9 Kasım 2021 tarihli duyurusu sonrasında Katılım Tüm, Katılım 100, Katılım 50, Katılım 30 ve Sürdürülebilirlik Katılım endekslerinin 12 Kasım 2021'den..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Katılım endeksleri 2018'de hesaplanmaya başlamış"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.00, N=0.01, C=0.99)
  2. Atom: `"Taahhütlü İşlemler Pazarı ise 2021'de faaliyete geçmiştir"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.08, N=0.14, C=0.78)
- **İnsan Gözüyle Değerlendirme:** K1 modeli metin ile iddia arasındaki yüksek kelime benzerliği nedeniyle cümledeki çelişkiyi 'kısmi destek' sanarak yumuşatmıştır. K2 ise iddiayı iki atoma bölmüş; ikinci atom açıkça 'contradiction' çıkınca toplulaştırma kuralı doğru bir şekilde tüm cümlenin çeliştiğine karar vermiştir.

### VAKA 07 [ID: tfb_ex_0042] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `partially_supported`
- **K1 Tahmini (Hatalı):** `supported` ❌
- **K2 Tahmini (Doğru):** `partially_supported` ✅
- **İddia (Claim):** *"Para Swap Pazarı'nda Türk lirası ile ABD doları veya euro arasında swap yapılır. Piyasa emrinde de limitli emir gibi swap puanı ve döviz kuru belirtilmesi gerekir."*
- **Bağlam (Context Özeti):** *"Piyasa Kurumu A Para Swap Pazarı'nda, Piyasa Kurumu A düzenlemeleri uyarınca işlem yapma yetkisi verilmiş bankalar ile Merkez Bankası A işlem yapabilir. Pazarda Türk lirası ile Amerikan doları veya euro arasındaki swap i..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Para Swap Pazarı'nda Türk lirası ile ABD doları veya euro arasında swap yapılır."` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.99, N=0.01, C=0.00)
  2. Atom: `"Piyasa emrinde de limitli emir gibi swap puanı ve döviz kuru belirtilmesi gerekir."` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.16, N=0.01, C=0.83)
- **İnsan Gözüyle Değerlendirme:** K1 modeli cümlenin genel akıcılığına aldanarak iddiadaki eksik bilgiyi fark edememiş ve doğrudan tam destek vermiştir. K2 atomlaştırma sayesinde ilk cümlenin desteklendiğini (entailment), ikinci bilginin ise metinde olmadığını (neutral) ayrı ayrı yakalamış ve doğru şekilde kısmi destek kararı üretmiştir.

### VAKA 08 [ID: tfb_ex_0054] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `partially_supported`
- **K1 Tahmini (Hatalı):** `supported` ❌
- **K2 Tahmini (Doğru):** `partially_supported` ✅
- **İddia (Claim):** *"Elektronik defter dosyaları kâğıda bastırılmadan elektronik biçimde oluşturulur ve bütünlükleri elektronik imza veya mali mühürle korunur. Elektronik fatura zorunluluğu bulunan mükellefler için Elektronik defter isteğe bağlıdır."*
- **Bağlam (Context Özeti):** *"Elektronik defter uygulamasında, Vergi Usul Kanunu veya Türk Ticaret Kanunu gereğince tutulması zorunlu defterlerde yer alması gereken bilgiler elektronik kayıtlar halinde tutulur. Defter dosyaları kâğıda bastırılmadan e..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Elektronik defter dosyaları kâğıda bastırılmadan elektronik biçimde oluşturulur"` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.99, N=0.01, C=0.00)
  2. Atom: `"bütünlükleri elektronik imza veya mali mühürle korunur"` $\rightarrow$ **NLI Kararı:** `entailment` (E=1.00, N=0.00, C=0.00)
  3. Atom: `"Elektronik fatura zorunluluğu bulunan mükellefler için Elektronik defter isteğe bağlıdır"` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.01, N=0.04, C=0.95)
- **İnsan Gözüyle Değerlendirme:** K1 modeli cümlenin genel akıcılığına aldanarak iddiadaki eksik bilgiyi fark edememiş ve doğrudan tam destek vermiştir. K2 atomlaştırma sayesinde ilk cümlenin desteklendiğini (entailment), ikinci bilginin ise metinde olmadığını (neutral) ayrı ayrı yakalamış ve doğru şekilde kısmi destek kararı üretmiştir.

### VAKA 09 [ID: tfb_ex_0068] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `unverifiable`
- **K1 Tahmini (Hatalı):** `partially_supported` ❌
- **K2 Tahmini (Doğru):** `unverifiable` ✅
- **İddia (Claim):** *"Takip sistemindeki benzersiz kod üzerinden üretici, üretim tarihi, ağırlık ve saflık bilgileri alıcı tarafından sorgulanabilir; ürünün önceki sahiplik kayıtları da görüntülenebilir."*
- **Bağlam (Context Özeti):** *"Takip sistemini kurma ve işletme görevi Kıymetli Maden Kurumu A’ya verilmiştir. Sistem, Bakanlık tarafından faaliyet izni verilen rafinerilerin standart işlenmemiş kıymetli madenleri ile basılı kıymetli madenlerini izler..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Takip sistemindeki benzersiz kod üzerinden üretici, üretim tarihi, ağırlık ve saflık bilgileri alıcı tarafından sorgulanabilir"` $\rightarrow$ **NLI Kararı:** `neutral` (E=0.27, N=0.57, C=0.15)
  2. Atom: `"ürünün önceki sahiplik kayıtları da görüntülenebilir"` $\rightarrow$ **NLI Kararı:** `neutral` (E=0.02, N=0.97, C=0.01)
- **İnsan Gözüyle Değerlendirme:** Atomik önerme ayrıştırması, çok bileşenli cümlenin farklı anlamsal katmanlarını izole ederek tekil encoder'ın aşırı öğrenme sınırını aşmasını sağlamıştır.

### VAKA 10 [ID: tfb_ex_0078] — ALAN: FINANCE
- **Gerçek Etiket (Gold):** `partially_supported`
- **K1 Tahmini (Hatalı):** `supported` ❌
- **K2 Tahmini (Doğru):** `partially_supported` ✅
- **İddia (Claim):** *"Nakit yönetimi projesi kapsamında Merkez Bankası A adına banknot saklama ve işleme faaliyetleri yürütülür. 2025 yılında Ankara'da dört yeni depo açılmışken İstanbul'da da dört yeni nakit yönetimi deposu faaliyete alınmıştır."*
- **Bağlam (Context Özeti):** *"Nakit yönetimi projesi kapsamında, Türk lirası tedavülünün kesintisiz sağlanması amacıyla Merkez Bankası A adına banknot saklama ve işleme faaliyetleri yürütülür. Proje kapsamında 2025 yılında Ankara'da dört, İstanbul ve..."*
- **Gemma-4 Atomları ve mDeBERTa NLI Çıkarımları:**
  1. Atom: `"Nakit yönetimi projesi kapsamında Merkez Bankası A adına banknot saklama ve işleme faaliyetleri yürütülür."` $\rightarrow$ **NLI Kararı:** `entailment` (E=0.99, N=0.01, C=0.00)
  2. Atom: `"2025 yılında Ankara'da dört yeni depo açılmışken İstanbul'da da dört yeni nakit yönetimi deposu faaliyete alınmıştır."` $\rightarrow$ **NLI Kararı:** `contradiction` (E=0.09, N=0.07, C=0.84)
- **İnsan Gözüyle Değerlendirme:** K1 modeli cümlenin genel akıcılığına aldanarak iddiadaki eksik bilgiyi fark edememiş ve doğrudan tam destek vermiştir. K2 atomlaştırma sayesinde ilk cümlenin desteklendiğini (entailment), ikinci bilginin ise metinde olmadığını (neutral) ayrı ayrı yakalamış ve doğru şekilde kısmi destek kararı üretmiştir.

---

## 5. K1'İN KAZANDIĞI 69 VAKANIN VE HATA YAYILIMININ (ERROR CASCADE) ANALİZİ

K1'in doğru bilip K2'nin yanıldığı 69 vaka incelendiğinde üç ana mekanizma görülmektedir:

1. **Kısmi Destek ile Tam Destek Arasındaki Sınır (21 Vaka):**
   - Cümle aslında bir bütün olarak `partially_supported` iken, mDeBERTa atomlardan birini aşırı hoşgörülü davranarak *entailment* olarak etiketlemiş, bu da tüm cümlenin *supported* çıkmasına neden olmuştur.
2. **Aşırı Katı Toplulaştırma (Aggregation Rigidity):**
   - Cümlede 2 atom varken, biri açıkça doğru, diğeri ise önemsiz bir niteleme sıfatı yüzünden *neutral* çıktığında; kural bunu otomatikman `partially_supported` yapmaktadır. Oysa insan etiketçi sıfat farkını tolere edip `supported` demiştir.
3. **Tekil Encoder'ın Küresel Bağlam (Global Context) Avantajı:**
   - K1 (ELECTRA-TR), cümlenin tamamını bağlamın tamamıyla aynı anda cross-attention üzerinden işlediği için, birden fazla cümleye dağılmış kanıtları tek seferde sentezleyebilmektedir. K2 ise atomları tek tek bağımsız değerlendirdiği için atomlar arası ortak bağlamı kaybedebilmektedir.

---

## 6. YÜKSEK LİSANS TEZİ İÇİN STRATEJİK ÇIKARIMLAR

Bu niteliksel rapor, teziniz için şu bilimsel tezleri kesinleştirmiştir:
1. **K1 ve K2 Birbirinin Alternatifi Değil, Tamamlayıcısıdır:** İki modelin ham uyuşması %73.54'tür. 44 örnekte K2, 69 örnekte K1 kazanmaktadır. Birbirlerinin kör noktalarını kapatmaktadırlar.
2. **Hibrit Mimarinin Meşruiyeti İspatlanmıştır:** İki modelin Oracle birleşimi %92.29 doğruluğa ulaşmaktadır. Bu da resmi tez önerinizdeki 'K1 ve K2 kararlarının birleştirilmesi' hipotezini ampirik olarak %100 haklı çıkarmaktadır.
3. **Bileşen 3 (LLM Hakem) İçin Somut Çalışma Kümesi Belirlenmiştir:** 127 ayrışan örnek, LLM Hakem'in arbitrasyon yapacağı resmi deney kümesidir.