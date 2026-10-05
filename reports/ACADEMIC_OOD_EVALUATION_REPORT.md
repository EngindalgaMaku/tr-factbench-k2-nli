# Dağılım Dışı (OOD) Veri Kümelerinde Kademeli Hibrit Mimari Analiz Raporu

**Tarih:** 5 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  

## 1. Giriş
Bu raporda, Kademeli Hibrit Mimarinin eğitim verisinde bulunmayan (Dağılım Dışı / Out-of-Distribution) metinlerdeki performansını değerlendirmek amacıyla Tıp (Alzheimer), Hukuk (İş Kanunu) ve Finans (Eurobond) alanlarında oluşturulan toplam 48 vakanın analizi sunulmaktadır. Modellerin verdikleri yanıtlar, hakem mekanizmasının kararları ve sonuçlar vaka bazında listelenmiştir.

## 2. Kümülatif Performans Tablosu

| Metrik / Model | Tıp (Alzheimer) | Hukuk (İş Kanunu) | Finans (Eurobond) | Toplam (48 Vaka) |
| :--- | :---: | :---: | :---: | :---: |
| K1 Doğruluğu (ELECTRA-TR) | 15/16 (%93.75) | 14/16 (%87.50) | 15/16 (%93.75) | 44/48 (%91.67) |
| K2 Doğruluğu (Gemma-4+mDeBERTa) | 13/16 (%81.25) | 15/16 (%93.75) | 11/16 (%68.75) | 39/48 (%81.25) |
| Doğrudan Uzlaşma (Hakemsiz) Oranı | 13/16 (%81.25) | 13/16 (%81.25) | 10/16 (%62.50) | 36/48 (%75.00) |
| **Hibrit Mimari Nihai Doğruluğu** | **16/16 (%100.0)** | **16/16 (%100.0)** | **16/16 (%100.0)** | **48/48 (%100.0)** |

<div class="page-break"></div>

## 3. Vaka İncelemeleri

### Tıp (Alzheimer) Alanı Vakaları

#### Vaka: `ood_med_01`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Alzheimer tedavisinde kullanılan donepezil, rivastigmin ve galantamin hafif ve orta evrede asetilkolin miktarını artırarak kolinerjik iletimi güçlendirir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_02`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Memantin orta ve ileri evre Alzheimer hastalığında glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini önleyen bir NMDA reseptör antagonistidir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_03`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Alzheimer hastalığında mevcut ilaç tedavileri hastalığı tamamen durduran şifa verici nitelikte olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_04`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Orta ve ağır evre Alzheimer hastalarında kolinesteraz inhibitörleri ile memantin birlikte kullanılabilir ve bu kombinasyon kognitif semptomlarda ek fayda sağlayabilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_05`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Kolinesteraz inhibitörleri hafif ve orta evrede asetilkolin miktarını artırır ve sinir hücrelerini gençleştirerek beyin dokusundaki yaşlanmayı tamamen geri döndürür.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_06`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Memantin orta ve ileri evre Alzheimer hastalığında kullanılır ve hastanın tansiyon ilaçlarını tamamen bırakmasını sağlayarak damar sertliğini iyileştirir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_07`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Alzheimer tedavisinde ilaç dışı bilişsel yaklaşımlar yer almalıdır fakat ilaç tedavisine başlanan hastanın nöroloji uzmanı kontrolüne gitmesine gerek yoktur.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_08`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Donepezil ve rivastigmin hafif evre Alzheimer tedavisinde kullanılır; ayrıca bu ilaçlar takrin ile kombine edilerek günlük rutin tedavide verilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_09`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Alzheimer hastalığında kullanılan mevcut medikal ilaçlar hastalığın ilerlemesini tamamen durdurarak hastayı biyolojik olarak iyileştiren kesin şifa tedavileridir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `supported` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddia, Alzheimer hastalığında kullanılan mevcut medikal ilaçların hastalığı tamamen durdurarak şifa veren tedaviler olduğunu iddia etmektedir. Bağlam ise bu ilaçların semptomları hafifletmeye yönelik semptomatik tedaviler olduğunu ve hastalığı tamamen durduran veya şifa veren tedaviler olmadığını açıkça belirtmektedir.

---

#### Vaka: `ood_med_10`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Memantin bir kolinesteraz inhibitörü olup kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `partially_supported` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddiada memantinin bir kolinesteraz inhibitörü olduğu doğru bilgi ile kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanması bilgisi bir arada bulunmakta, ancak bağlam memantinin aslında kalsiyumun hücreye aşırı girişini engelleyerek eksitotoksisiteyi önlediğini belirtmektedir. Model B'nin atomik analizinin gösterdiği gibi, iddianın bir parçası (memantin bir kolinesteraz inhibitörü değildir, NMDA reseptör antagonistidir) doğrudan bağlam tarafından çelişmekte ve diğer parçası (eksitotoksisiteyi artırmak amacıyla uygulanması) da bağlamla çelişmektedir.

---

#### Vaka: `ood_med_11`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Günümüzde yan etkileri nedeniyle donepezil ve rivastigmin tamamen yasaklanmış olup rutin klinik kullanımda yalnızca takrin tercih edilmektedir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `partially_supported` | `supported` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddia, donepezil ve rivastigmin'in tamamen yasaklandığını ve yalnızca takrin'in tercih edildiğini öne sürmektedir, ancak bağlamda bu bilgilerin hiçbirinin doğrulanmadığı görülmektedir. Ayrıca, bağlamda takrin'in artık kullanılmadığı bilgisi yer almaktadır, bu nedenle iddia doğrudan bağlamla çelişmektedir.

---

#### Vaka: `ood_med_12`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Kolinesteraz inhibitörleri sinaptik aralıktaki asetilkolin maddesinin miktarını azaltarak kolinerjik sinirsel iletimi tamamen durdurur.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_13`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Alzheimer hastalarında günlük yüksek doz C vitamini kullanımı kolinesteraz inhibitörlerinin bağırsaktan emilimini iki katına çıkarır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_14`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Donepezil tedavisi alan hastaların ilacı her sabah aç karnına taze sıkılmış greyfurt suyuyla birlikte tüketmesi tavsiye edilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_15`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Memantin tedavisi gören hastaların haftada en az üç gün açık havada 45 dakika tempolu kardiyo egzersizi yapması zorunludur.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_med_16`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**İddia:** Kolinesteraz inhibitörlerinin eczane perakende satış fiyatları her takvim yılı başında merkezi ilaç komisyonu kararıyla güncellenir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

<div class="page-break"></div>

### Hukuk (İş Kanunu) Alanı Vakaları

#### Vaka: `ood_law_01`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** 4857 sayılı İş Kanunu'na göre aynı işverenin işyerinde en az bir tam yıl çalışmış olan işçi, iş sözleşmesinin kanunda belirtilen haklı veya geçerli nedenlerle feshedilmesi halinde kıdem tazminatına hak kazanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_02`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken iki haftalık ihbar süresine uyulması veya bu süreye ait ücretin ihbar tazminatı olarak ödenmesi gerekir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_03`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İş sözleşmesi İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence feshedilen işçiye kıdem ve ihbar tazminatı ödenmez.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_04`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** Feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur ve doğrudan mahkemeye dava açılamaz.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `partially_supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddia, bağlamda açıkça belirtilen 'feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur ve doğrudan mahkemeye dava açılamaz' bilgisini doğrudan yansıtmaktadır. Model A, iddiayı bütün olarak değerlendirerek supported kararı vermiştir ve bu doğru bir yaklaşımdır.

---

#### Vaka: `ood_law_05`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İş sözleşmesinin feshinde işçinin kıdem tazminatına hak kazanması için en az bir yıl çalışması şarttır ve kıdem tazminatı tavan sınırı olmaksızın brüt ücretin iki katı üzerinden hesaplanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_06`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** Üç yıldan fazla kıdemi olan işçi için ihbar süresi sekiz haftadır ve bildirim şartına uymayan taraf ihbar tazminatının yanı sıra hapis cezasıyla cezalandırılır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_07`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır ancak dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `contradicted` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddiada iki farklı önerme bulunmaktadır: 'İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır' ve 'dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir'. İlk önerme bağlam tarafından doğrulanırken, ikinci önerme bağlamda bulunmamaktadır ve doğrudan bir çelişki oluşturmamaktadır, ancak bağlamda böyle bir olanaktan da bahsedilmez. Dolayısıyla, iddianın bir kısmı bağlam tarafından desteklenirken, diğer kısmı bağlamda yer almayan bir duruma işaret etmektedir.

---

#### Vaka: `ood_law_08`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İşi altı aydan bir buçuk yıla kadar süren işçi için ihbar süresi dört haftadır; ayrıca 25/II maddesi gereğince ahlak kurallarına uymayan işçiye her durumda peşin ihbar tazminatı ödenmesi zorunludur.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_09`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** 4857 sayılı İş Kanunu'na göre işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresi sekiz hafta olarak uygulanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `supported` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddiada yer alan ihbar süresinin sekiz hafta olarak uygulanması ifadesi, bağlamda belirtilen altı aydan az sürmüş işçi için iki hafta olan ihbar süresiyle doğrudan çelişmektedir. Model B'nin atomik olarak ayırdığı önerme doğrudan bağlamla çeliştiğinden, Model B'nin kararı doğru görünmektedir.

---

#### Vaka: `ood_law_10`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İş yerinde sadece üç ay çalışmış olan ve kendi isteğiyle istifa eden bir işçi kıdem tazminatına tam olarak hak kazanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `unverifiable` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddiada yer alan 'kıdem tazminatına tam olarak hak kazanır' ifadesi, bağlamda belirtilen 'işçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl çalışmış olması' şartıyla doğrudan çelişmektedir. Ayrıca, işçi kendi isteğiyle istifa ettiğinde kıdem tazminatı alamayacağı da belirtilmiştir.

---

#### Vaka: `ood_law_11`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına aykırılık gerekçesiyle işten çıkarılan personele işverence hem kıdem hem de ihbar tazminatı eksiksiz ödenir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_12`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İş sözleşmesi feshedilen çalışan, arabulucuya başvurma şartı aranmaksızın doğrudan doğruya iş mahkemesinde dava açabilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_13`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** Aynı işverenin işyerinde bir yılı dolduran işçinin yıllık ücretli izin hakkı en az on dört iş günüdür.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `supported` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** Bağlamda yıllık ücretli izin hakkına ilişkin bir bilgi bulunmamaktadır. Model B'nin kararı yanlıştır çünkü bağlamda bu bilgiye dair hiçbir kanıt veya doğrulama yoktur.

---

#### Vaka: `ood_law_14`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** Haftalık kırk beş saati aşan fazla çalışma süreleri için işçiye normal saatlik ücretinin yüzde elli fazlası ödenir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_15`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** Kıdem tazminatına esas teşkil eden tavan ücret her yıl Asgari Ücret Tespit Komisyonu tarafından oy birliğiyle belirlenir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_law_16`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**İddia:** İhbar süresi boyunca işveren işçiye günde iki saatten az olmamak üzere yeni iş arama izni vermekle yükümlüdür.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `contradicted` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** Bağlamda ihbar süresi boyunca işverenin işçiye yeni iş arama izni verme yükümlülüğü hakkında hiçbir bilgi bulunmamaktadır. Model B'nin kararı doğru olup, bağlamda bu konuya dair hiçbir bilgi bulunmadığından unverifiable kararı verilmesi gerekmektedir.

---

<div class="page-break"></div>

### Finans (Eurobond) Alanı Vakaları

#### Vaka: `ood_fin_01`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Türkiye Cumhuriyeti Hazinesi tarafından ihraç edilen Eurobondlar genellikle altı ayda bir ya da yılda bir kupon faizi ödemesi gerçekleştiren uzun vadeli borçlanma araçlarıdır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_02`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `contradicted` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** İddia, bağlamda açıkça belirtilen 'Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır' bilgisini doğrudan tekrarlamaktadır. Model A'nın kararı, bağlamın iddianın tümünü desteklediğini doğru bir şekilde yansıtmaktadır.

---

#### Vaka: `ood_fin_03`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Hazine ihraçlı Eurobondların kupon faiz gelirlerinde yerli bireysel yatırımcılara uygulanan stopaj oranı yüzde sıfırdır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_04`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobondlar yatırımcılara fiziki olarak teslim edilmeyip Takasbank ile Euroclear veya Clearstream gibi merkezlerde kaydi sistemde saklanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `supported` | `supported` | `supported` | `supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_05`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobond alım satımında standart takas süresi T+2 olarak uygulanır ve alıcılar vadesi gelen tahvillerin fiziki senetlerini doğrudan banka şubesinden teslim alabilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_06`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Hazine Eurobondlarının kupon faiz gelirlerinde stopaj oranı yüzde sıfırdır ve elde edilen gelir tutarı ne kadar yüksek olursa olsun hiçbir şekilde yıllık vergi beyannamesine dahil edilmez.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_07`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobondlar ulusal para birimi dışındaki yabancı para cinsinden ihraç edilir; ayrıca Hazine tarafından ihraç edilen her bir Eurobond için Merkez Bankası altın cinsinden yüzde yüz karşılık tutmak zorundadır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_08`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobond kupon ödemeleri altı ayda bir veya yılda bir yapılabilir; ayrıca vadeden önce ikincil piyasada yapılan satışlarda bankalarca anında yüzde kırk oranında kaynakta stopaj kesintisi yapılır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` | `partially_supported` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_09`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobond işlemlerinde işlemlerin takas ve ödeme mutabakatı işlem yapılan gün içinde (T+0 aynı gün) anlık olarak sonuçlandırılmak zorundadır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_10`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Hazine ihraçlı Eurobond kupon gelirleri üzerinden yerli bireysel yatırımcılardan kupon ödeme anında yüzde yirmi beş oranında peşin stopaj vergisi kesilir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `unverifiable` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** Bağlam, Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj oranının yüzde sıfır (%0) olduğunu belirtmektedir. İddia ise yüzde yirmi beş oranında peşin stopaj vergisi kesildiğini öne sürmekte ve bu doğrudan bağlamla çelişmektedir.

---

#### Vaka: `ood_fin_11`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobond ihraçlarında belirlenen kupon faiz oranlarının ihraç esnasında değişken olarak belirlenmesi kanunen kesinlikle yasaklanmıştır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_12`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Yatırımcılar satın aldıkları Eurobondları Takasbank kaydı yerine basılı kıymetli evrak olarak fiziki şekilde saklamakla yükümlüdür.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` | `contradicted` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_13`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Bankalar arası Eurobond işlemlerinde asgari işlem limiti genellikle iki yüz bin ABD Doları olarak uygulanır.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_14`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Türkiye'nin beş yıllık kredi temerrüt takası (CDS) primi arttığında ihraç edilecek Eurobondların kupon faizleri yükselir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

#### Vaka: `ood_fin_15`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `contradicted` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** Bağlamda Eurobond'lardan elde edilen kupon faiz gelirlerinin döviz cinsinden ödenmesiyle ilgili herhangi bir bilgi bulunmamaktadır. Model B'nin doğrudan çelişki kararı vermesi daha uygun görünmektedir çünkü iddia edilen durum bağlamda açıkça doğrulanmıyor veya reddedilmiyor, ancak bağlamda bulunan bilgilerle doğrudan çelişen bir durum da söz konusu değildir, sadece bilgi eksikliği vardır.

---

#### Vaka: `ood_fin_16`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**İddia:** Kurumsal yatırımcıların portföylerindeki Eurobond tutarı Bankacılık Düzenleme ve Denetleme Kurumu tarafından üç ayda bir denetlenir.

| Zemin Gerçeği | K1 Kararı | K2 Kararı | Nihai Karar | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` | `unverifiable` | **✅ DOĞRU** |

**Hakem / Uzlaşma Gerekçesi:** K1 ve K2 yerel modelleri hemfikir.

---

<div class="page-break"></div>

