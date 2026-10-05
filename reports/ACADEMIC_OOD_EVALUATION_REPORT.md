# Dağılım Dışı (OOD) Veri Kümelerinde Kademeli Hibrit Mimari Analiz Raporu

**Tarih:** 5 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  

## 1. Giriş
Bu raporda, Kademeli Hibrit Mimarinin eğitim verisinde bulunmayan (Dağılım Dışı / Out-of-Distribution) metinlerdeki performansını değerlendirmek amacıyla Tıp (Alzheimer), Hukuk (İş Kanunu) ve Finans (Eurobond) alanlarında oluşturulan toplam 48 vakanın analizi sunulmaktadır. Modellerin verdikleri yanıtlar, atomik bileşenler, hakem mekanizmasının kararları ve sonuçlar vaka bazında listelenmiştir. 

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

**Soru:** Alzheimer hastalığında kolinesteraz inhibitörleri ve memantinin kullanım evreleri ile etki mekanizmaları nelerdir?

**İddia (Sistem Çıktısı):** Alzheimer tedavisinde kullanılan donepezil, rivastigmin ve galantamin hafif ve orta evrede asetilkolin miktarını artırarak kolinerjik iletimi güçlendirir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Alzheimer tedavisinde kullanılan donepezil, rivastigmin ve galantamin hafif ve orta evrede asetilkolin miktarını artırarak kolinerjik iletimi güçlendirir. _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_02`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Memantin hangi evrede kullanılır ve nöronal hasarı nasıl engeller?

**İddia (Sistem Çıktısı):** Memantin orta ve ileri evre Alzheimer hastalığında glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini önleyen bir NMDA reseptör antagonistidir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Memantin orta ve ileri evre Alzheimer hastalığında glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini önleyen bir NMDA reseptör antagonistidir. _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_03`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Alzheimer hastalığındaki mevcut medikal tedavilerin temel niteliği nedir?

**İddia (Sistem Çıktısı):** Alzheimer hastalığında mevcut ilaç tedavileri hastalığı tamamen durduran şifa verici nitelikte olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Alzheimer hastalığında mevcut ilaç tedavileri hastalığı tamamen durduran şifa verici nitelikte olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_04`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Hangi evrede kombine ilaç tedavisi tercih edilebilir?

**İddia (Sistem Çıktısı):** Orta ve ağır evre Alzheimer hastalarında kolinesteraz inhibitörleri ile memantin birlikte kullanılabilir ve bu kombinasyon kognitif semptomlarda ek fayda sağlayabilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Orta ve ağır evre Alzheimer hastalarında kolinesteraz inhibitörleri ile memantin birlikte kullanılabilir _(Tahmin: `entailment`)_
2. bu kombinasyon kognitif semptomlarda ek fayda sağlayabilir _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_05`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Kolinesteraz inhibitörleri hafif evrede ne yapar ve beyin dokusunu nasıl etkiler?

**İddia (Sistem Çıktısı):** Kolinesteraz inhibitörleri hafif ve orta evrede asetilkolin miktarını artırır ve sinir hücrelerini gençleştirerek beyin dokusundaki yaşlanmayı tamamen geri döndürür.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Kolinesteraz inhibitörleri hafif ve orta evrede asetilkolin miktarını artırır. _(Tahmin: `entailment`)_
2. Kolinesteraz inhibitörleri sinir hücrelerini gençleştirerek beyin dokusundaki yaşlanmayı tamamen geri döndürür. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_06`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Memantin hangi evrede kullanılır ve tansiyon üzerinde etkisi var mıdır?

**İddia (Sistem Çıktısı):** Memantin orta ve ileri evre Alzheimer hastalığında kullanılır ve hastanın tansiyon ilaçlarını tamamen bırakmasını sağlayarak damar sertliğini iyileştirir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Memantin orta ve ileri evre Alzheimer hastalığında kullanılır. _(Tahmin: `entailment`)_
2. Memantin hastanın tansiyon ilaçlarını tamamen bırakmasını sağlayarak damar sertliğini iyileştirir. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_07`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Alzheimer tedavisinde hekim kontrolü ve yan etkiler nasıldır?

**İddia (Sistem Çıktısı):** Alzheimer tedavisinde ilaç dışı bilişsel yaklaşımlar yer almalıdır fakat ilaç tedavisine başlanan hastanın nöroloji uzmanı kontrolüne gitmesine gerek yoktur.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Alzheimer tedavisinde ilaç dışı bilişsel yaklaşımlar yer almalıdır _(Tahmin: `entailment`)_
2. ilaç tedavisine başlanan hastanın nöroloji uzmanı kontrolüne gitmesine gerek yoktur _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_08`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Klinik kullanımda olan kolinesteraz inhibitörleri hangileridir?

**İddia (Sistem Çıktısı):** Donepezil ve rivastigmin hafif evre Alzheimer tedavisinde kullanılır; ayrıca bu ilaçlar takrin ile kombine edilerek günlük rutin tedavide verilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Donepezil ve rivastigmin hafif evre Alzheimer tedavisinde kullanılır _(Tahmin: `entailment`)_
2. Bu ilaçlar takrin ile kombine edilerek günlük rutin tedavide verilir _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_09`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Alzheimer hastalığındaki ilaçlar hastalığı iyileştirir mi?

**İddia (Sistem Çıktısı):** Alzheimer hastalığında kullanılan mevcut medikal ilaçlar hastalığın ilerlemesini tamamen durdurarak hastayı biyolojik olarak iyileştiren kesin şifa tedavileridir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
- _Atom bulunamadı_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddia, Alzheimer hastalığında kullanılan mevcut medikal ilaçların hastalığı tamamen durdurarak şifa veren tedaviler olduğunu iddia etmektedir. Bağlam ise bu ilaçların semptomları hafifletmeye yönelik semptomatik tedaviler olduğunu ve hastalığı tamamen durduran veya şifa veren tedaviler olmadığını açıkça belirtmektedir.

---

#### Vaka: `ood_med_10`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Memantin nasıl bir ilaçtır ve hücre içine kalsiyum girişini nasıl etkiler?

**İddia (Sistem Çıktısı):** Memantin bir kolinesteraz inhibitörü olup kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Memantin bir kolinesteraz inhibitörü _(Tahmin: `entailment`)_
2. kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddiada memantinin bir kolinesteraz inhibitörü olduğu doğru bilgi ile kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanması bilgisi bir arada bulunmakta, ancak bağlam memantinin aslında kalsiyumun hücreye aşırı girişini engelleyerek eksitotoksisiteyi önlediğini belirtmektedir. Model B'nin atomik analizinin gösterdiği gibi, iddianın bir parçası (memantin bir kolinesteraz inhibitörü değildir, NMDA reseptör antagonistidir) doğrudan bağlam tarafından çelişmekte ve diğer parçası (eksitotoksisiteyi artırmak amacıyla uygulanması) da bağlamla çelişmektedir.

---

#### Vaka: `ood_med_11`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Günümüzde hangi kolinesteraz inhibitörleri kullanılmaktadır?

**İddia (Sistem Çıktısı):** Günümüzde yan etkileri nedeniyle donepezil ve rivastigmin tamamen yasaklanmış olup rutin klinik kullanımda yalnızca takrin tercih edilmektedir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
- _Atom bulunamadı_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `partially_supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddia, donepezil ve rivastigmin'in tamamen yasaklandığını ve yalnızca takrin'in tercih edildiğini öne sürmektedir, ancak bağlamda bu bilgilerin hiçbirinin doğrulanmadığı görülmektedir. Ayrıca, bağlamda takrin'in artık kullanılmadığı bilgisi yer almaktadır, bu nedenle iddia doğrudan bağlamla çelişmektedir.

---

#### Vaka: `ood_med_12`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Kolinesteraz inhibitörleri asetilkolin miktarını nasıl değiştirir?

**İddia (Sistem Çıktısı):** Kolinesteraz inhibitörleri sinaptik aralıktaki asetilkolin maddesinin miktarını azaltarak kolinerjik sinirsel iletimi tamamen durdurur.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Kolinesteraz inhibitörleri sinaptik aralıktaki asetilkolin maddesinin miktarını azaltarak kolinerjik sinirsel iletimi tamamen durdurur. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_13`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Alzheimer tedavisinde vitamin takviyelerinin ilaç emilimine etkisi nedir?

**İddia (Sistem Çıktısı):** Alzheimer hastalarında günlük yüksek doz C vitamini kullanımı kolinesteraz inhibitörlerinin bağırsaktan emilimini iki katına çıkarır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Alzheimer hastalarında günlük yüksek doz C vitamini kullanımı kolinesteraz inhibitörlerinin bağırsaktan emilimini iki katına çıkarır _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_14`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Donepezil kullanımında içecek etkileşimleri nasıldır?

**İddia (Sistem Çıktısı):** Donepezil tedavisi alan hastaların ilacı her sabah aç karnına taze sıkılmış greyfurt suyuyla birlikte tüketmesi tavsiye edilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Donepezil tedavisi alan hastaların ilacı her sabah aç karnına taze sıkılmış greyfurt suyuyla birlikte tüketmesi tavsiye edilir _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_15`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Memantin tedavisi alan hastalar için egzersiz protokolü nasıldır?

**İddia (Sistem Çıktısı):** Memantin tedavisi gören hastaların haftada en az üç gün açık havada 45 dakika tempolu kardiyo egzersizi yapması zorunludur.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Memantin tedavisi gören hastaların haftada en az üç gün açık havada 45 dakika tempolu kardiyo egzersizi yapması zorunludur. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_med_16`

**Bağlam:** Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.

**Soru:** Alzheimer ilaçlarının piyasa fiyatları nasıl belirlenir?

**İddia (Sistem Çıktısı):** Kolinesteraz inhibitörlerinin eczane perakende satış fiyatları her takvim yılı başında merkezi ilaç komisyonu kararıyla güncellenir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Kolinesteraz inhibitörlerinin eczane perakende satış fiyatları her takvim yılı başında merkezi ilaç komisyonu kararıyla güncellenir _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

<div class="page-break"></div>

### Hukuk (İş Kanunu) Alanı Vakaları

#### Vaka: `ood_law_01`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** İşçinin kıdem tazminatına hak kazanabilmesinin temel koşulları nelerdir?

**İddia (Sistem Çıktısı):** 4857 sayılı İş Kanunu'na göre aynı işverenin işyerinde en az bir tam yıl çalışmış olan işçi, iş sözleşmesinin kanunda belirtilen haklı veya geçerli nedenlerle feshedilmesi halinde kıdem tazminatına hak kazanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. 4857 sayılı İş Kanunu'na göre aynı işverenin işyerinde en az bir tam yıl çalışmış olan işçi, iş sözleşmesinin kanunda belirtilen haklı veya geçerli nedenlerle feshedilmesi halinde kıdem tazminatına hak kazanır. _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_02`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Altı aydan az çalışmış işçinin fesih bildirimi nasıl yapılır?

**İddia (Sistem Çıktısı):** İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken iki haftalık ihbar süresine uyulması veya bu süreye ait ücretin ihbar tazminatı olarak ödenmesi gerekir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken fesih bildirimi nasıl yapılmalıdır? _(Tahmin: `entailment`)_
2. İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken fesih bildirimi nasıl yapılmalıdır? _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_03`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Ahlak ve iyi niyet kurallarına aykırılık halinde tazminat ödenir mi?

**İddia (Sistem Çıktısı):** İş sözleşmesi İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence feshedilen işçiye kıdem ve ihbar tazminatı ödenmez.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İş sözleşmesi İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence feshedilen işçiye kıdem ve ihbar tazminatı ödenmez. _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_04`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** İşe iade davası açma usulü nasıldır?

**İddia (Sistem Çıktısı):** Feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur ve doğrudan mahkemeye dava açılamaz.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur. _(Tahmin: `neutral`)_
2. Doğrudan mahkemeye dava açılamaz. _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddia, bağlamda açıkça belirtilen 'feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur ve doğrudan mahkemeye dava açılamaz' bilgisini doğrudan yansıtmaktadır. Model A, iddiayı bütün olarak değerlendirerek supported kararı vermiştir ve bu doğru bir yaklaşımdır.

---

#### Vaka: `ood_law_05`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Kıdem tazminatı şartı ve hesaplama katsayısı nasıldır?

**İddia (Sistem Çıktısı):** İş sözleşmesinin feshinde işçinin kıdem tazminatına hak kazanması için en az bir yıl çalışması şarttır ve kıdem tazminatı tavan sınırı olmaksızın brüt ücretin iki katı üzerinden hesaplanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İş sözleşmesinin feshinde işçinin kıdem tazminatına hak kazanması için en az bir yıl çalışması şarttır. _(Tahmin: `entailment`)_
2. Kıdem tazminatının hesaplanmasında tavan sınırı olmaksızın brüt ücretin iki katı üzerinden hesaplanır. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_06`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Üç yıldan fazla çalışan işçinin ihbar süresi ve uyulmama yaptırımı nedir?

**İddia (Sistem Çıktısı):** Üç yıldan fazla kıdemi olan işçi için ihbar süresi sekiz haftadır ve bildirim şartına uymayan taraf ihbar tazminatının yanı sıra hapis cezasıyla cezalandırılır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Üç yıldan fazla kıdemi olan işçi için ihbar süresi sekiz haftadır. _(Tahmin: `entailment`)_
2. Bildirim şartına uymayan taraf ihbar tazminatının yanı sıra hapis cezasıyla cezalandırılır. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_07`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** İşe iade sürecinde başvuru süreleri ve alternatif yollar nasıldır?

**İddia (Sistem Çıktısı):** İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır ancak dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır _(Tahmin: `neutral`)_
2. dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddiada iki farklı önerme bulunmaktadır: 'İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır' ve 'dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir'. İlk önerme bağlam tarafından doğrulanırken, ikinci önerme bağlamda bulunmamaktadır ve doğrudan bir çelişki oluşturmamaktadır, ancak bağlamda böyle bir olanaktan da bahsedilmez. Dolayısıyla, iddianın bir kısmı bağlam tarafından desteklenirken, diğer kısmı bağlamda yer almayan bir duruma işaret etmektedir.

---

#### Vaka: `ood_law_08`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Kıdemi bir buçuk yıla kadar olan işçinin ihbarı ve ahlak dışı fesih nasıldır?

**İddia (Sistem Çıktısı):** İşi altı aydan bir buçuk yıla kadar süren işçi için ihbar süresi dört haftadır; ayrıca 25/II maddesi gereğince ahlak kurallarına uymayan işçiye her durumda peşin ihbar tazminatı ödenmesi zorunludur.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İşi altı aydan bir buçuk yıla kadar süren işçi için ihbar süresi dört haftadır. _(Tahmin: `entailment`)_
2. Ayrıca 25/II maddesi gereğince ahlak kurallarına uymayan işçiye her durumda peşin ihbar tazminatı ödenmesi zorunludur. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_09`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Altı aydan az kıdemi olan işçinin ihbar süresi kaç haftadır?

**İddia (Sistem Çıktısı):** 4857 sayılı İş Kanunu'na göre işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresi sekiz hafta olarak uygulanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. 4857 sayılı İş Kanunu'na göre işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresi sekiz hafta olarak uygulanır. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `supported` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddiada yer alan ihbar süresinin sekiz hafta olarak uygulanması ifadesi, bağlamda belirtilen altı aydan az sürmüş işçi için iki hafta olan ihbar süresiyle doğrudan çelişmektedir. Model B'nin atomik olarak ayırdığı önerme doğrudan bağlamla çeliştiğinden, Model B'nin kararı doğru görünmektedir.

---

#### Vaka: `ood_law_10`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Üç ay çalıştıktan sonra istifa eden işçi kıdem tazminatı alabilir mi?

**İddia (Sistem Çıktısı):** İş yerinde sadece üç ay çalışmış olan ve kendi isteğiyle istifa eden bir işçi kıdem tazminatına tam olarak hak kazanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İş yerinde sadece üç ay çalışmış olan _(Tahmin: `contradiction`)_
2. kendi isteğiyle istifa eden bir işçi _(Tahmin: `neutral`)_
3. kıdem tazminatına tam olarak hak kazanır _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddiada yer alan 'kıdem tazminatına tam olarak hak kazanır' ifadesi, bağlamda belirtilen 'işçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl çalışmış olması' şartıyla doğrudan çelişmektedir. Ayrıca, işçi kendi isteğiyle istifa ettiğinde kıdem tazminatı alamayacağı da belirtilmiştir.

---

#### Vaka: `ood_law_11`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Ahlak ve iyi niyete aykırı fesihte kıdem ve ihbar tazminatı ödenir mi?

**İddia (Sistem Çıktısı):** İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına aykırılık gerekçesiyle işten çıkarılan personele işverence hem kıdem hem de ihbar tazminatı eksiksiz ödenir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
- _Atom bulunamadı_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_12`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Arabulucuya gitmeden doğrudan iş mahkemesinde dava açılabilir mi?

**İddia (Sistem Çıktısı):** İş sözleşmesi feshedilen çalışan, arabulucuya başvurma şartı aranmaksızın doğrudan doğruya iş mahkemesinde dava açabilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İş sözleşmesi feshedilen çalışan, arabulucuya başvurma şartı aranmaksızın doğrudan doğruya iş mahkemesinde dava açabilir. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_13`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Bir yılı dolduran işçinin yıllık izin hakkı kaç gündür?

**İddia (Sistem Çıktısı):** Aynı işverenin işyerinde bir yılı dolduran işçinin yıllık ücretli izin hakkı en az on dört iş günüdür.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Aynı işverenin işyerinde bir yılı dolduran işçinin yıllık ücretli izin hakkı en az on dört iş günüdür. _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** Bağlamda yıllık ücretli izin hakkına ilişkin bir bilgi bulunmamaktadır. Model B'nin kararı yanlıştır çünkü bağlamda bu bilgiye dair hiçbir kanıt veya doğrulama yoktur.

---

#### Vaka: `ood_law_14`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Haftalık kırk beş saati aşan fazla çalışmalar nasıl ücretlendirilir?

**İddia (Sistem Çıktısı):** Haftalık kırk beş saati aşan fazla çalışma süreleri için işçiye normal saatlik ücretinin yüzde elli fazlası ödenir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Haftalık kırk beş saati aşan fazla çalışma süreleri için işçiye normal saatlik ücretinin yüzde elli fazlası ödenir. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_15`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** Kıdem tazminatı tavan ücreti nasıl belirlenir?

**İddia (Sistem Çıktısı):** Kıdem tazminatına esas teşkil eden tavan ücret her yıl Asgari Ücret Tespit Komisyonu tarafından oy birliğiyle belirlenir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Kıdem tazminatına esas teşkil eden tavan ücret her yıl Asgari Ücret Tespit Komisyonu tarafından belirlenir. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_law_16`

**Bağlam:** 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.

**Soru:** İhbar süresi boyunca işçiye yeni iş arama izni verilir mi?

**İddia (Sistem Çıktısı):** İhbar süresi boyunca işveren işçiye günde iki saatten az olmamak üzere yeni iş arama izni vermekle yükümlüdür.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. İhbar süresi boyunca işveren işçiye günde iki saatten az olmamak üzere yeni iş arama izni vermekle yükümlüdür _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `contradicted` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** Bağlamda ihbar süresi boyunca işverenin işçiye yeni iş arama izni verme yükümlülüğü hakkında hiçbir bilgi bulunmamaktadır. Model B'nin kararı doğru olup, bağlamda bu konuya dair hiçbir bilgi bulunmadığından unverifiable kararı verilmesi gerekmektedir.

---

<div class="page-break"></div>

### Finans (Eurobond) Alanı Vakaları

#### Vaka: `ood_fin_01`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Hazine ihraçlı Eurobondların kupon ödeme sıklığı ve niteliği nedir?

**İddia (Sistem Çıktısı):** Türkiye Cumhuriyeti Hazinesi tarafından ihraç edilen Eurobondlar genellikle altı ayda bir ya da yılda bir kupon faizi ödemesi gerçekleştiren uzun vadeli borçlanma araçlarıdır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Türkiye Cumhuriyeti Hazinesi tarafından ihraç edilen Eurobondlar _(Tahmin: `entailment`)_
2. genellikle altı ayda bir ya da yılda bir kupon faizi ödemesi gerçekleştiren uzun vadeli borçlanma araçlarıdır _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_02`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobond işlemlerinde standart takas süresi nedir?

**İddia (Sistem Çıktısı):** Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** İddia, bağlamda açıkça belirtilen 'Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır' bilgisini doğrudan tekrarlamaktadır. Model A'nın kararı, bağlamın iddianın tümünü desteklediğini doğru bir şekilde yansıtmaktadır.

---

#### Vaka: `ood_fin_03`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Yerli bireysel yatırımcı için kupon faizlerinde stopaj kesintisi var mıdır?

**İddia (Sistem Çıktısı):** Hazine ihraçlı Eurobondların kupon faiz gelirlerinde yerli bireysel yatırımcılara uygulanan stopaj oranı yüzde sıfırdır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Hazine ihraçlı Eurobondların kupon faiz gelirlerinde yerli bireysel yatırımcılara uygulanan stopaj oranı yüzde sıfırdır _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_04`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobondlar fiziken mi teslim edilir yoksa kayden mi saklanır?

**İddia (Sistem Çıktısı):** Eurobondlar yatırımcılara fiziki olarak teslim edilmeyip Takasbank ile Euroclear veya Clearstream gibi merkezlerde kaydi sistemde saklanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobondlar yatırımcılara fiziki olarak teslim edilmeyip Takasbank ile Euroclear veya Clearstream gibi merkezlerde kaydi sistemde saklanır _(Tahmin: `entailment`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `supported` | `supported` | `supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_05`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Takas süresi ve senet teslimi nasıldır?

**İddia (Sistem Çıktısı):** Eurobond alım satımında standart takas süresi T+2 olarak uygulanır ve alıcılar vadesi gelen tahvillerin fiziki senetlerini doğrudan banka şubesinden teslim alabilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobond alım satımında standart takas süresi T+2 olarak uygulanır _(Tahmin: `entailment`)_
2. alıcılar vadesi gelen tahvillerin fiziki senetlerini doğrudan banka şubesinden teslim alabilir _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_06`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobond kupon faizlerinin stopajı ve beyanname zorunluluğu nasıldır?

**İddia (Sistem Çıktısı):** Hazine Eurobondlarının kupon faiz gelirlerinde stopaj oranı yüzde sıfırdır ve elde edilen gelir tutarı ne kadar yüksek olursa olsun hiçbir şekilde yıllık vergi beyannamesine dahil edilmez.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Hazine Eurobondlarının kupon faiz gelirlerinde stopaj oranı yüzde sıfırdır _(Tahmin: `entailment`)_
2. elde edilen gelir tutarı ne kadar yüksek olursa olsun hiçbir şekilde yıllık vergi beyannamesine dahil edilmez _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_07`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobondların para birimi ve teminat yapısı nasıldır?

**İddia (Sistem Çıktısı):** Eurobondlar ulusal para birimi dışındaki yabancı para cinsinden ihraç edilir; ayrıca Hazine tarafından ihraç edilen her bir Eurobond için Merkez Bankası altın cinsinden yüzde yüz karşılık tutmak zorundadır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobondlar ulusal para birimi dışındaki yabancı para cinsinden ihraç edilir. _(Tahmin: `entailment`)_
2. Hazine tarafından ihraç edilen her bir Eurobond için Merkez Bankası altın cinsinden yüzde yüz karşılık tutmak zorundadır. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_08`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Kupon frekansı ve erken satış stopajı nasıldır?

**İddia (Sistem Çıktısı):** Eurobond kupon ödemeleri altı ayda bir veya yılda bir yapılabilir; ayrıca vadeden önce ikincil piyasada yapılan satışlarda bankalarca anında yüzde kırk oranında kaynakta stopaj kesintisi yapılır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobond kupon ödemeleri altı ayda bir veya yılda bir yapılabilir _(Tahmin: `entailment`)_
2. vadeden önce ikincil piyasada yapılan satışlarda bankalarca anında yüzde kırk oranında kaynakta stopaj kesintisi yapılır _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `partially_supported` | `partially_supported` | `partially_supported` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `partially_supported` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_09`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobond işlemlerinde takas aynı gün mü yapılır?

**İddia (Sistem Çıktısı):** Eurobond işlemlerinde işlemlerin takas ve ödeme mutabakatı işlem yapılan gün içinde (T+0 aynı gün) anlık olarak sonuçlandırılmak zorundadır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
- _Atom bulunamadı_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_10`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Hazine Eurobondlarının kuponlarında stopaj kesintisi oranı nedir?

**İddia (Sistem Çıktısı):** Hazine ihraçlı Eurobond kupon gelirleri üzerinden yerli bireysel yatırımcılardan kupon ödeme anında yüzde yirmi beş oranında peşin stopaj vergisi kesilir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Hazine ihraçlı Eurobond kupon gelirleri üzerinden yerli bireysel yatırımcılardan kupon ödeme anında yüzde yirmi beş oranında peşin stopaj vergisi kesilir. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `unverifiable` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** Bağlam, Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj oranının yüzde sıfır (%0) olduğunu belirtmektedir. İddia ise yüzde yirmi beş oranında peşin stopaj vergisi kesildiğini öne sürmekte ve bu doğrudan bağlamla çelişmektedir.

---

#### Vaka: `ood_fin_11`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobond kupon oranları değişken olarak belirlenebilir mi?

**İddia (Sistem Çıktısı):** Eurobond ihraçlarında belirlenen kupon faiz oranlarının ihraç esnasında değişken olarak belirlenmesi kanunen kesinlikle yasaklanmıştır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobond ihraçlarında belirlenen kupon faiz oranlarının ihraç esnasında değişken olarak belirlenmesi kanunen kesinlikle yasaklanmıştır. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_12`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobondlar fiziki kıymetli evrak mıdır?

**İddia (Sistem Çıktısı):** Yatırımcılar satın aldıkları Eurobondları Takasbank kaydı yerine basılı kıymetli evrak olarak fiziki şekilde saklamakla yükümlüdür.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Yatırımcılar satın aldıkları Eurobondları Takasbank kaydı yerine basılı kıymetli evrak olarak fiziki şekilde saklamakla yükümlüdür. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `contradicted` | `contradicted` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `contradicted` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_13`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobond işlemlerinde asgari alım tutarı ne kadardır?

**İddia (Sistem Çıktısı):** Bankalar arası Eurobond işlemlerinde asgari işlem limiti genellikle iki yüz bin ABD Doları olarak uygulanır.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Bankalar arası Eurobond işlemlerinde asgari işlem limiti genellikle iki yüz bin ABD Doları olarak uygulanır. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_14`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** CDS primleri Eurobond kupon oranlarını nasıl etkiler?

**İddia (Sistem Çıktısı):** Türkiye'nin beş yıllık kredi temerrüt takası (CDS) primi arttığında ihraç edilecek Eurobondların kupon faizleri yükselir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Türkiye'nin beş yıllık kredi temerrüt takası (CDS) primi arttığında _(Tahmin: `neutral`)_
2. ihraç edilecek Eurobondların kupon faizleri yükselir _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

#### Vaka: `ood_fin_15`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Eurobond faiz ödemeleri hangi para biriminde talep edilir?

**İddia (Sistem Çıktısı):** Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler. _(Tahmin: `contradiction`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `contradicted` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Meta-Hakem (Llama-3.3-70B) Kararı
- **Hakem Gerekçesi (Reasoning):** Bağlamda Eurobond'lardan elde edilen kupon faiz gelirlerinin döviz cinsinden ödenmesiyle ilgili herhangi bir bilgi bulunmamaktadır. Model B'nin doğrudan çelişki kararı vermesi daha uygun görünmektedir çünkü iddia edilen durum bağlamda açıkça doğrulanmıyor veya reddedilmiyor, ancak bağlamda bulunan bilgilerle doğrudan çelişen bir durum da söz konusu değildir, sadece bilgi eksikliği vardır.

---

#### Vaka: `ood_fin_16`

**Bağlam:** Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.

**Soru:** Kurumsal Eurobond portföyleri ne sıklıkla denetlenir?

**İddia (Sistem Çıktısı):** Kurumsal yatırımcıların portföylerindeki Eurobond tutarı Bankacılık Düzenleme ve Denetleme Kurumu tarafından üç ayda bir denetlenir.

**K2 Atomları (Gemma-4 + mDeBERTa):**
1. Kurumsal yatırımcıların portföylerindeki Eurobond tutarı Bankacılık Düzenleme ve Denetleme Kurumu tarafından üç ayda bir denetlenir. _(Tahmin: `neutral`)_

| Zemin Gerçeği | K1 (ELECTRA) | K2 (Gemma+mDeBERTa) |
| :--- | :--- | :--- |
| `unverifiable` | `unverifiable` | `unverifiable` |

**Nihai Karar ve Gerekçe:**
- **Karar:** `unverifiable` ✅ (Sistem doğru karara ulaştı.)
- **Mekanizma:** Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)
- **Açıklama:** K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.

---

<div class="page-break"></div>

