# Bölüm 2: Literatür Taraması ve Karşılaştırmalı Taksonomi Matrisi
## Büyük Dil Modellerinde Halüsinasyon Tespiti, Doğal Dil Çıkarımı (NLI) ve Olgu Doğrulama Literatürünün Kapsamlı Analizi

**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  
**Tez Başlığı:** *Türkçe Büyük Dil Modeli Yanıtlarında Halüsinasyon Tespiti: Hibrit Bir Doğrulama Yaklaşımı ve Genellenebilirlik Analizi*  
**Kurum:** Burdur Mehmet Akif Ersoy Üniversitesi | Fen Bilimleri Enstitüsü | Yazılım Mühendisliği Anabilim Dalı  
**Tarih:** 5 Ekim 2026  
**Doküman Türü:** Tez Bölüm 2 Ana Omurgası ve Literatür Karşılaştırma Matrisi  

---

## 1. Giriş ve Teorik Çerçeve

Büyük Dil Modellerinin (BDM / LLM) doğal dil üretim yeteneklerindeki üstel artış, bu modellerin bilgiye erişim, özetleme, soru-cevaplama ve uzmanlık gerektiren karar destek sistemlerinde (sağlık, hukuk, finans) yaygın biçimde benimsenmesini sağlamıştır. Bununla birlikte, dil modellerinin eğitim verilerindeki istatistiksel örüntüleri taklit etme eğilimi; bağlamla çelişen, uydurma veya doğrulanamayan içerikler üretmelerine yol açmaktadır. Literatürde **halüsinasyon (hallucination)** veya **olgusal sadakatsizlik (factual unfaithfulness)** olarak adlandırılan bu olgu, özellikle yüksek riskli alanlarda sistemlerin güvenilirliğini zedeleyen en temel açık problemdir (Ji vd., 2023; Huang vd., 2025).

### 1.1. Halüsinasyon Taksonomisi: İçsel (Intrinsic) ve Dışsal (Extrinsic) Halüsinasyonlar
Literatürdeki genel uzlaşı doğrultusunda metin tabanlı halüsinasyonlar iki ana sınıfa ayrılmaktadır:
1. **İçsel Halüsinasyonlar (Intrinsic Hallucinations):** Modelin ürettiği metnin, kendisine sunulan referans bağlam (context) veya kaynak belge ile doğrudan mantıksal çelişki (contradiction) oluşturması durumudur.
2. **Dışsal Halüsinasyonlar (Extrinsic Hallucinations):** Üretilen metnin, referans bağlamda ne doğrulanan ne de yalanlanan (unverifiable / bilgi yokluğu) yeni iddialar içermesidir. Model, bağlamda yer almayan bilgiyi "sanki bağlamda varmış gibi" sunar.

### 1.2. Doğrulama Tanecikliliği (Verification Granularity)
Halüsinasyon tespitinin erken dönemlerinde modeller ikili (binary: doğru/yanlış) ve belge/paragraf düzeyinde değerlendirilirken; güncel literatür doğrulamayı daha alt semantik birimlere indirgemiştir:
- **Belge / Paragraf Düzeyi (Coarse-Grained):** Cümleler arası mantıksal kırılmaları yakalayamaz.
- **Cümle Düzeyi (Sentence-Level):** Bileşik cümlelerdeki yarı-doğru yarı-yanlış durumları maskeler.
- **Atomik Önerme Düzeyi (Fine-Grained / Atomic Propositions):** Bir cümlenin bölünemez bağımsız bilgi parçacıklarına (fact / atom) ayrıştırılması ve her bir atomun ayrı ayrı NLI modelinden geçirilmesidir (Min vd., 2023; Chen vd., 2024).

---

## 2. Uluslararası Literatürün Gelişimi (2018–2026)

| Yıl | Çalışma | Temel Katkı ve Yaklaşım | Taneciklilik (Granularity) | Dil | Sınıf Sayısı | Kısıt / Boşluk |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **2018** | **FEVER** (Thorne vd.) | 185K Wikipedia iddiası üzerinden bilgi getirme (retrieval) ve 3 sınıflı NLI temeli. | Cümle (Claim) | İngilizce | 3 Sınıf (Sup / Ref / NEI) | Yalnızca Wikipedia; kısmi destek (partial support) sınıfı yok; açık alan erişimi gerektirir. |
| **2019** | **MultiFC** (Augenstein vd.) | 26 farklı olgu kontrol sitesinden toplanan heterojen siyasi/kamusal iddialar. | Cümle | İngilizce | Çok sınıflı (Heterojen) | Bağlamsız açık dünya doğrulaması; metin içi sadakat kontrolü için uygun değil. |
| **2023** | **FActScore** (Min vd.) | Biyografi metinlerini atomik olgulara (atomic facts) bölerek LLM hassasiyetini ölçme. | Atomik Önerme | İngilizce | İkili (Supported / Not-supported) | Yalnızca Wikipedia biyografileri; tam bağlamlı NLI taksonomisi (4 sınıf) içermez. |
| **2024** | **PropSegmEnt** (Chen vd.) | Önerme ayrıştırma (proposition segmentation) ve NLI birleşimi. | Önerme (Proposition) | İngilizce | 3 Sınıf | Özel uzmanlık alanları (tıp/hukuk/finans) dışarıda bırakılmıştır. |
| **2024** | **SAFE** (Wei vd. - DeepMind) | Arama motoru destekli, uzun metinlerde çok adımlı atomik doğrulama. | Atomik Önerme | İngilizce | İkili | Devasa LLM ve arama motoru çağrısı gerektirir; kapalı sistemlerde (KVKK/on-prem) çalışamaz. |
| **2024** | **MiniCheck** (Luo vd.) | Küçük modellerin (small models) sentetik verilerle eğitilerek GPT-4 düzeyinde olgu kontrolü yapması. | Cümle | İngilizce | İkili (Supported / Unsupported) | Kısmi doğruluk desteği yok; çok dilli transfer sınırlı. |
| **2025** | **Scientific NLI** (Schopf vd.) | Bilimsel makalelerde NLI modellerinin ince ayar (fine-tuning) ile halüsinasyon tespiti. | Cümle | İngilizce | 3 Sınıf | Yalnızca akademik özetler; hibrit/kademeli mimari yok. |
| **2025** | **RAG to Reality** (Galimzianova vd.)| RAG boru hatlarında NLI modelleriyle kaba taneli halüsinasyon tespiti. | Paragraf / Cümle | İngilizce | 3 Sınıf | Atomik parçalama ve açıklanabilirlik eksik; tek model bağımlı. |
| **2026** | **Context-Grounded** (Peisakhovsky vd. - ACL) | Bağlam odaklı halüsinasyonlarda ince taneli hata tespiti ve hata kaskadı analizi. | Alt-cümle (Sub-sentence) | İngilizce | İkili / Çok sınıflı | Yüksek hesaplama maliyeti; Türkçe gibi morfolojik dilleri kapsamaz. |
| **2026** | **Hallucination Survey** (Alansari & Luqman) | 2026 itibarıyla BDM halüsinasyonlarının güncel taksonomisi ve açık alanları. | Derleme / Survey | Çeşitli | Taksonomik | Ampirik model sunulmamış; teorik çerçeve çizilmiştir. |

---

## 3. Türkçe Doğal Dil İşleme Literatürü ve Yerel Çalışmalar

Türkçe, zengin morfolojik yapısı, serbest sözdizimi, eklemeli doğası ve kaynak kısıtlılığı (low-resource) nedeniyle doğal dil çıkarımı ve olgu doğrulamada kendine özgü zorluklar barındırmaktadır.

| Yıl | Çalışma | Kapsam ve Metodoloji | Dil | Sınıf Sayısı | Taneciklilik | Temel Kısıt / Literatürdeki Boşluk |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **2018** | **XNLI-TR** (Conneau vd.) | İngilizce MNLI test setinin profesyonel Türkçe çevirisi (5.000 çift). | Türkçe (Çeviri) | 3 Sınıf (Entail / Neutral / Contra) | Cümle | Kültürel ve yerel dil yapılarını yansıtmaz; çeviri yapaylığı içerir; halüsinasyon odaklı değildir. |
| **2020** | **Turkish-NLI / NLI-TR** (Budur vd. - EMNLP) | SNLI ve MNLI veri kümelerinin makine çevirisi ve BERTurk ile ilk geniş çaplı Türkçe NLI değerlendirmesi. | Türkçe (Sentetik Çeviri) | 3 Sınıf | Cümle | Çeviri artefaktları (translation artifacts); hipotez-yalnız yanlılığı (hypothesis-only bias); 4. sınıf (kısmi destek) yok. |
| **2023** | **TrClaim-19** (Kartal & Kutlu) | Twitter/Sosyal medya iddialarının doğrulanabilirliğini saptama. | Türkçe (Sosyal Medya) | İkili (Check-worthy / Not) | Tweet | Halüsinasyon tespiti değil, iddia tespiti (claim detection) problemidir; bağlam karşılaştırması yoktur. |
| **2024** | **Fact-Checking in Turkish** (Çekinel vd. - LREC) | Doğruluk Payı ve Teyit.org verileriyle çapraz dilli olgu kontrolü transferi. | Türkçe (Haber/Politika) | İkili / 3 Sınıf | Cümle / İddia | Sosyal/politik açık iddialar; RAG bağlam sadakati veya belge içi halüsinasyon tespiti değildir. |
| **2024** | **ImplicaTR** (Halat & Atlamaz - SIGTURK) | Türkçede edimbilimsel çıkarım ve olasılıksal bağlaçların analizi (1.200 örnek). | Türkçe (Özgün) | 3 Sınıf | Cümle | Dilbilimsel/edimbilimsel çıkarım odaklı; kurumsal alanlar (tıp, hukuk, finans) ve halüsinasyon bağlamı içermez. |
| **2025** | **Turk-LettuceDetect** (Taş vd. - IEEE FLLM) | Türkçe RAG uygulamalarında halüsinasyon tespiti için ModernBERT tabanlı model. | Türkçe | İkili (Halüsinasyon Var / Yok) | Cümle | **Yalnızca ikili sınıflandırma (0/1);** kısmi destek, çelişki ve doğrulanamaz ayrımı yapamaz; atomik açıklanabilirlik yoktur. |

---

## 4. Büyük Karşılaştırmalı Literatür Taksonomi Matrisi (Master Matrix)

Aşağıdaki tablo, uluslararası ve ulusal literatürdeki öncü 15 çalışma ile bu tezde önerilen **TR-FactBench ve Kademeli Hibrit Mimari**'yi (K1 + K2 + K3) 10 kritik parametre üzerinden kafa kafaya karşılaştırmaktadır:

| # | Çalışma / Sistem | Hedef Dil | Sınıf Sayısı ve Taksonomi | Taneciklilik (Granularity) | Kaynak Alanı (Domain) | Bilgi Getirme Şartı | Çıkarım Motoru (Inference Engine) | Açıklanabilirlik (XAI Desteği) | Frugal AI / Tüketici GPU Uyumu |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | **FEVER** (2018) | İngilizce | 3 Sınıf (Sup / Ref / NEI) | Cümle | Genel (Wikipedia) | Açık Arama (Retrieval) | Pipeline (IR + NLI) | Cümle kanıt seçimi | Hayır (Büyük İndeks) |
| 2 | **MultiFC** (2019) | İngilizce | Heterojen (Çoklu) | İddia | Siyaset / Haber | Açık Arama | Çift Dilli / NLI | Yok (Kara Kutu) | Kısmen |
| 3 | **XNLI-TR** (2018) | TR (Çeviri) | 3 Sınıf (NLI) | Cümle | Genel Konuşma | Bağımsız (Pairwise) | Çapraz Dilli Encoder | Yok | Evet |
| 4 | **Budur vd.** (2020) | TR (Çeviri) | 3 Sınıf (NLI) | Cümle | Genel Metin | Bağımsız | Monolingual Encoder | Yok | Evet |
| 5 | **FActScore** (2023) | İngilizce | İkili (Binary) | **Atomik Önerme** | Wikipedia Biyografi | Açık Arama | LLM (Prompting) | Atomik ayrıştırma | Hayır (GPT-3.5/4) |
| 6 | **ImplicaTR** (2024) | Türkçe | 3 Sınıf (Edimbilim) | Cümle | Dilbilimsel | Bağımsız | Encoder | Yok | Evet |
| 7 | **Çekinel vd.** (2024) | Türkçe | 2 / 3 Sınıf | İddia / Cümle | Haber Doğrulama | Açık Arama | Cross-Lingual NLI | Yok | Evet |
| 8 | **PropSegmEnt** (2024)| İngilizce | 3 Sınıf | Önerme (Proposition) | Genel | Bağımsız | LLM + NLI | Önerme Haritası | Kısmen |
| 9 | **SAFE** (2024) | İngilizce | İkili | **Atomik Önerme** | Uzun Metin | Çok Adımlı Arama | Saf Büyük LLM | Arama Kanıtı | Hayır (Devasa API) |
| 10| **MiniCheck** (2024) | İngilizce | İkili | Cümle | Çoklu Sentetik | Bağlam İçi (Grounded)| Distilled Küçük Model | Yok (Skor) | Evet |
| 11| **Schopf vd.** (2025) | İngilizce | 3 Sınıf | Cümle | Akademik Yayın | Bağlam İçi | Fine-tuned NLI | Yok | Evet |
| 12| **Turk-Lettuce** (2025)| Türkçe | **İkili (0 / 1)** | Cümle | RAG Yanıtları | Bağlam İçi | ModernBERT Encoder | Yok (İkili Etiket) | Evet |
| 13| **Peisakhovsky** (2026)| İngilizce | İkili / Çoklu | Alt-cümle | Çoklu Alan | Bağlam İçi | LLM Decomposition | Parça Ayrıştırma | Hayır (LLM Bağımlı) |
| 14| **Alansari** (2026) | Çeşitli | — (Survey) | — | — | — | — | — | — |
| ⭐| **BU TEZ: TR-FactBench & Kademeli Hibrit (K1+K2+K3)** | **Türkçe (Özgün)** | **4 Sınıf (Destek, Kısmi Destek, Çelişki, Belirsiz)** | **Çok Seviyeli (Bütüncül Dizi + Atomik Önerme)** | **3 Kritik Alan: Tıp, Hukuk, Finans (27 Resmi Belge)** | **Bağlam İçi (Retrieval-Free / Sadakat)** | **Kademeli Hibrit (ELECTRA + QLoRA Gemma + mDeBERTa + CoT 70B)** | **Tam Açıklanabilirlik: Önerme Bölütleme + Gerekçeli Hakem Kararı** | **%100 Evet (7.39 GB VRAM ile RTX 4060'ta Çalışır)** |

---

## 5. Literatürdeki Temel Boşluklar (Research Gaps) ve Bu Tezin Özgün Değeri

Yukarıdaki taksonomi matrisi dikkatle incelendiğinde, literatürde tespit edilen ve bu tez çalışmasıyla kapatılan **dört temel bilimsel boşluk (research gap)** şunlardır:

### Boşluk 1: Türkçe'de İnce Taneli 4 Sınıflı Halüsinasyon Benchmark'ı Eksikliği
- **Literatürün Durumu:** Türkçe NLI çalışmaları (Budur vd., 2020; Halat & Atlamaz, 2024) İngilizce'den çevrilmiş veya genel edimbilimsel cümlelere odaklanmıştır. Türkçe RAG odaklı tek çalışma olan *Turk-LettuceDetect* (Taş vd., 2025) ise problemi sadece ikili (halüsinasyon var/yok) olarak ele almaktadır.
- **Tezin Katkısı:** Bu tez kapsamında geliştirilen **TR-FactBench**, Türkçedeki **ilk 4 sınıflı (Destekleniyor, Kısmen Destekleniyor, Çelişiyor, Doğrulanamaz)** resmi kurum belgelerine dayalı (Sağlık Bakanlığı, Yargıtay, KAP/BDDK) dengeli altın test kümesidir. "Kısmen Destekleniyor" sınıfı, karmaşık cümlelerdeki kısmi doğruları yakalayarak sistemin sıfır toleransla doğruyu toptan reddetmesini engeller.

### Boşluk 2: Önerme (Atom) Düzeyinde Açıklanabilir Çıkarım (XAI)
- **Literatürün Durumu:** Klasik encoder tabanlı modeller (BERT, ELECTRA) girdi metnine tek bir etiket basmakta, modelin cümlenin neresini yanlış bulduğu kullanıcı tarafından anlaşılamamaktadır (kara kutu problemi).
- **Tezin Katkısı:** Tezde kurgulanan **Bileşen 2 (K2)**, Google Gemma-4 QLoRA ile iddiayı atomik parçalara ayırmakta; her bir atomun referans bağlamdaki doğruluk olasılığını mDeBERTa Soft-Probability NLI ile şeffaf biçimde raporlamaktadır.

### Boşluk 3: Dev LLM Bağımlılığına Karşı "Frugal AI / Model Cascading" Mimarisi
- **Literatürün Durumu:** FActScore ve SAFE gibi uluslararası çalışmalar, doğrulama için her sorguda GPT-4 veya devasa modeller çağırarak fahiş API maliyetleri ve gecikme üretmektedir. MiniCheck gibi küçük modeller ise 4 sınıflı gri alanlarda bocalayabilmektedir.
- **Tezin Katkısı:** Bu tez, **Kademeli Hibrit Boru Hattı** ile iki yerel küçük modelin (K1 ve K2) uzlaştığı %74.9'luk alanda sıfır maliyetle 15ms hızında karar üretir. Yalnızca uyuşmazlık durumunda (%25.1) 70B Hakeme başvurarak, **saf 70B LLM'in dahi üzerinde (%90.79 vs %89.54) doğruluğu %74.9 maliyet tasarrufuyla** sağlar. Tüm yerel katman **7.39 GB VRAM** ile tek bir tüketici GPU'sunda (RTX 4060) çalışabilmektedir.

### Boşluk 4: Sıfır Sızıntılı Çok Alanlı Dağılım Dışı (OOD) Genellenebilirlik Kanıtı
- **Literatürün Durumu:** Halüsinasyon tespit modelleri genellikle yalnızca eğitildikleri dar alanda test edilmekte; gerçek dünyadaki alan değişimlerine (domain shift) karşı dirençleri ölçülmemektedir.
- **Tezin Katkısı:** Modelimiz, eğitim setinde sıfır defa geçen (%0 Data Leakage) **Nöroloji/Alzheimer, 4857 Sayılı İş Hukuku ve Uluslararası Eurobond Finans Piyasası** olmak üzere 3 farklı alanda 48 zorlu vaka üzerinde test edilmiş ve **%100 hibrit doğruluk** ile tam alan bağımsızlığı ispatlanmıştır.
