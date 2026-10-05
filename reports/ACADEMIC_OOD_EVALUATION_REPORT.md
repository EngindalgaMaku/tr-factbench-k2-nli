# Harici Veri Kümelerinde Kademeli Hibrit Mimari Analiz Raporu

**Tarih:** 5 Ekim 2026  
**Yazar:** Engin Dalga  
**Danışman:** Prof. Dr. Serkan Ballı  

## 1. Giriş
Bu raporda, Kademeli Hibrit Mimarinin eğitim aşamasında hiç karşılaşmadığı harici alanlardaki (Tıp, Hukuk, Finans) genellenebilirlik performansını test etmek amacıyla oluşturulan toplam 48 vakanın analizi sunulmaktadır. Modellerin verdikleri yanıtlar, atomik bileşenler, hakem mekanizmasının kararları ve sonuçlar vaka bazında listelenmiştir.


## 2. Deney Kurulumu ve Kademeli Hibrit Mimari

Bu testler, halüsinasyon tespiti ve doğrulama (fact-checking) için önerilen **Kademeli Hibrit Mimari** kullanılarak gerçekleştirilmiştir. Mimari üç ana bileşenden oluşmaktadır:

1. **K1 - Doğrudan Sınıflandırıcı (ELECTRA-TR):** Cümleyi ve bağlamı bir bütün olarak değerlendiren, hızlı ve bütüncül (holistik) bir encoder (kodlayıcı) modeldir.
2. **K2 - Atomik NLI Ayrıştırıcı (Gemma-4-2B + mDeBERTa):** Karmaşık iddiaları daha küçük yapıtaşlarına (atomlarına) bölen Gemma tabanlı bir LLM ile, bu atomları tek tek Doğal Dil Çıkarımı (NLI) yöntemiyle test eden mDeBERTa modelinin kombinasyonudur.
3. **Meta-Hakem (Llama-3.3-70B):** K1 ve K2 farklı kararlar verdiğinde (*Uyuşmazlık*) devreye giren son karar merciidir (Arbitrator). Her iki modelin de analizlerini görerek zincirleme mantık (Chain-of-Thought) yöntemiyle nihai kararı verir. K1 ve K2 anlaştığında Hakem'e gidilmez.

**Meta-Hakem (Llama-70B) için kullanılan Sistem İstem'i (Prompt):**
```text
Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı doğrulama modeli uzlaşamamıştır. Bağlamı ve modellerin analizlerini inceleyerek hakem kararını ver.

[...FEW-SHOT ÖRNEKLERİ...]

ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
'''{context}'''

İDDİA:
'''{claim}'''

MODEL A'NIN ANALİZİ (Bileşen 1: Doğrudan Doğrulayıcı):
- Karar: {k1_pred}
- Açıklama: Cümlenin tamamını bağlamla birlikte tek seferde değerlendirmiştir.

MODEL B'NİN ANALİZİ (Bileşen 2: Atomik NLI Doğrulayıcı):
- Karar: {k2_pred}
- Ayrıştırdığı Önermeler ve NLI Sonuçları:
{atoms_str}

ETİKET KURALLARI VE DİKKAT EDİLECEK HUSUSLAR:
1. supported: İddiadaki BÜTÜN bilgiler bağlam tarafından açıkça doğrulanmaktadır.
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir bilgi yer alıyorsa bu etiket ZORUNLUDUR.
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda iddiaya dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

Lütfen ÖNCE bağlamdaki kanıtı adım adım düşünerek analiz et, ARDINDAN kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
{{
  "reasoning": "<Önce bağlamdaki kanıtı ve modellerin analizini tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}}
```

## 3. Kümülatif Performans Tablosu

| Metrik / Model | Tıp (Alzheimer) | Hukuk (İş Kanunu) | Finans (Eurobond) | Toplam (48 Vaka) |
| :--- | :---: | :---: | :---: | :---: |
| K1 Doğruluğu (ELECTRA-TR) | 15/16 (%93.75) | 14/16 (%87.50) | 15/16 (%93.75) | 44/48 (%91.67) |
| K2 Doğruluğu (Gemma-4+mDeBERTa) | 15/16 (%93.75) | 12/16 (%75.0) | 14/16 (%87.5) | 41/48 (%85.4) |
| Doğrudan Uzlaşma (Hakemsiz) Oranı | 14/16 (%87.5) | 10/16 (%62.5) | 13/16 (%81.2) | 37/48 (%77.0) |
| **Hibrit Mimari Nihai Doğruluğu** | **15/16 (%93.75)** | **15/16 (%93.75)** | **15/16 (%93.75)** | **45/48 (%93.75)** |

<div class="page-break"></div>

## 4. Vaka İncelemeleri

### Bölüm: Tıp (Alzheimer) Alanı Vakaları

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_01</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Alzheimer hastalığında kolinesteraz inhibitörleri ve memantinin kullanım evreleri ile etki mekanizmaları nelerdir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Alzheimer tedavisinde kullanılan donepezil, rivastigmin ve galantamin hafif ve orta evrede asetilkolin miktarını artırarak kolinerjik iletimi güçlendirir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Alzheimer tedavisinde kullanılan donepezil, rivastigmin ve galantamin hafif ve orta evrede asetilkolin miktarını artırarak kolinerjik iletimi güçlendirir. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_02</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Memantin hangi evrede kullanılır ve nöronal hasarı nasıl engeller?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Memantin orta ve ileri evre Alzheimer hastalığında glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini önleyen bir NMDA reseptör antagonistidir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Memantin orta ve ileri evre Alzheimer hastalığında glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini önleyen bir NMDA reseptör antagonistidir. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_03</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Alzheimer hastalığındaki mevcut medikal tedavilerin temel niteliği nedir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Alzheimer hastalığında mevcut ilaç tedavileri hastalığı tamamen durduran şifa verici nitelikte olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Alzheimer hastalığında mevcut ilaç tedavileri hastalığı tamamen durduran şifa verici nitelikte olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_04</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Hangi evrede kombine ilaç tedavisi tercih edilebilir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Orta ve ağır evre Alzheimer hastalarında kolinesteraz inhibitörleri ile memantin birlikte kullanılabilir ve bu kombinasyon kognitif semptomlarda ek fayda sağlayabilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Orta ve ağır evre Alzheimer hastalarında kolinesteraz inhibitörleri ile memantin birlikte kullanılabilir <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>bu kombinasyon kognitif semptomlarda ek fayda sağlayabilir <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_05</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Kolinesteraz inhibitörleri hafif evrede ne yapar ve beyin dokusunu nasıl etkiler?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Kolinesteraz inhibitörleri hafif ve orta evrede asetilkolin miktarını artırır ve sinir hücrelerini gençleştirerek beyin dokusundaki yaşlanmayı tamamen geri döndürür.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Kolinesteraz inhibitörleri hafif ve orta evrede asetilkolin miktarını artırır. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Kolinesteraz inhibitörleri sinir hücrelerini gençleştirerek beyin dokusundaki yaşlanmayı tamamen geri döndürür. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_06</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Memantin hangi evrede kullanılır ve tansiyon üzerinde etkisi var mıdır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Memantin orta ve ileri evre Alzheimer hastalığında kullanılır ve hastanın tansiyon ilaçlarını tamamen bırakmasını sağlayarak damar sertliğini iyileştirir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Memantin orta ve ileri evre Alzheimer hastalığında kullanılır. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Memantin hastanın tansiyon ilaçlarını tamamen bırakmasını sağlayarak damar sertliğini iyileştirir. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_07</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Alzheimer tedavisinde hekim kontrolü ve yan etkiler nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Alzheimer tedavisinde ilaç dışı bilişsel yaklaşımlar yer almalıdır fakat ilaç tedavisine başlanan hastanın nöroloji uzmanı kontrolüne gitmesine gerek yoktur.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Alzheimer tedavisinde ilaç dışı bilişsel yaklaşımlar yer almalıdır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>ilaç tedavisine başlanan hastanın nöroloji uzmanı kontrolüne gitmesine gerek yoktur <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_08</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Klinik kullanımda olan kolinesteraz inhibitörleri hangileridir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Donepezil ve rivastigmin hafif evre Alzheimer tedavisinde kullanılır; ayrıca bu ilaçlar takrin ile kombine edilerek günlük rutin tedavide verilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Donepezil ve rivastigmin hafif evre Alzheimer tedavisinde kullanılır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Bu ilaçlar takrin ile kombine edilerek günlük rutin tedavide verilir <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_09</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Alzheimer hastalığındaki ilaçlar hastalığı iyileştirir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Alzheimer hastalığında kullanılan mevcut medikal ilaçlar hastalığın ilerlemesini tamamen durdurarak hastayı biyolojik olarak iyileştiren kesin şifa tedavileridir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Alzheimer hastalığında kullanılan mevcut medikal ilaçlar hastalığın ilerlemesini tamamen durdurarak hastayı biyolojik olarak iyileştiren kesin şifa tedavileridir. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_10</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge yanliş">❌ Sistem Kararı: YANLIŞ</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Memantin nasıl bir ilaçtır ve hücre içine kalsiyum girişini nasıl etkiler?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Memantin bir kolinesteraz inhibitörü olup kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Memantin bir kolinesteraz inhibitörü <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddiada memantinin bir kolinesteraz inhibitörü olduğu doğru bilgi ile kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır ifadesi yer almakta, bu ise bağlamda memantinin aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önlediği bilgisiyle doğrudan çelişmektedir. Model B'nin atomik analizinin gösterdiği gibi, iddianın bir parçası doğru (memantin ile ilgili) iken diğer parçası bağlamla çelişmektedir, bu nedenle partially_supported kararı verilmesi gerekir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_11</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Günümüzde hangi kolinesteraz inhibitörleri kullanılmaktadır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Günümüzde yan etkileri nedeniyle donepezil ve rivastigmin tamamen yasaklanmış olup rutin klinik kullanımda yalnızca takrin tercih edilmektedir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Günümüzde yan etkileri nedeniyle donepezil ve rivastigmin tamamen yasaklanmış olup rutin klinik kullanımda yalnızca takrin tercih edilmektedir. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>partially_supported</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddiada yer alan donepezil ve rivastigmin'in tamamen yasaklanmış olduğu ve yalnızca takrin'in tercih edildiği bilgisi, bağlam tarafından doğrudan çelişmekte ve yan etkileri nedeniyle takrin'in artık kullanılmadığı belirtilmektedir. Model B'nin atomik analizinin gösterdiği gibi, iddia edilen bilgiler bağlamla doğrudan zıtlık içermektedir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_12</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Kolinesteraz inhibitörleri asetilkolin miktarını nasıl değiştirir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Kolinesteraz inhibitörleri sinaptik aralıktaki asetilkolin maddesinin miktarını azaltarak kolinerjik sinirsel iletimi tamamen durdurur.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Kolinesteraz inhibitörleri sinaptik aralıktaki asetilkolin maddesinin miktarını azaltarak kolinerjik sinirsel iletimi tamamen durdurur. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_13</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Alzheimer tedavisinde vitamin takviyelerinin ilaç emilimine etkisi nedir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Alzheimer hastalarında günlük yüksek doz C vitamini kullanımı kolinesteraz inhibitörlerinin bağırsaktan emilimini iki katına çıkarır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Alzheimer hastalarında günlük yüksek doz C vitamini kullanımı kolinesteraz inhibitörlerinin bağırsaktan emilimini iki katına çıkarır <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_14</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Donepezil kullanımında içecek etkileşimleri nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Donepezil tedavisi alan hastaların ilacı her sabah aç karnına taze sıkılmış greyfurt suyuyla birlikte tüketmesi tavsiye edilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Donepezil tedavisi alan hastaların ilacı her sabah aç karnına taze sıkılmış greyfurt suyuyla birlikte tüketmesi tavsiye edilir <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_15</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Memantin tedavisi alan hastalar için egzersiz protokolü nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Memantin tedavisi gören hastaların haftada en az üç gün açık havada 45 dakika tempolu kardiyo egzersizi yapması zorunludur.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Memantin tedavisi gören hastaların haftada en az üç gün açık havada 45 dakika tempolu kardiyo egzersizi yapması zorunludur. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_med_16</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Alzheimer hastalığı tedavisinde kullanılan kolinesteraz inhibitörleri (donepezil, rivastigmin ve galantamin) genellikle hafif ve orta evre hastalıkta endikedir; bellek için kritik olan asetilkolinin sinaptik aralıktaki yıkımını engelleyerek miktarını artırır ve kolinerjik iletimi güçlendirir. Takrin ise yan etkileri nedeniyle artık kullanılmamaktadır. Memantin ise orta ve ileri evre Alzheimer hastalığında endike bir NMDA reseptör antagonistidir; beyindeki aşırı glutamat aktivitesini bloke ederek kalsiyumun hücreye aşırı girişini ve eksitotoksisiteyi önler. Orta ve ağır evrede kolinesteraz inhibitörleri ile memantinin kombine kullanımı kognitif semptomlar üzerinde ek fayda sağlayabilir. Alzheimer hastalığındaki mevcut ilaç tedavileri hastalığı tamamen durduran veya şifa veren tedaviler olmayıp semptomları hafifletmeye yönelik semptomatik tedavilerdir. Tedavide ilaç dışı bilişsel stimülasyon yaklaşımları da yer almalı, doz ayarı ve kardiyovasküler ile gastrointestinal yan etkilerin izlemi mutlaka nöroloji uzmanı kontrolünde yapılmalıdır.</p>
      <p><strong>Soru:</strong> Alzheimer ilaçlarının piyasa fiyatları nasıl belirlenir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Kolinesteraz inhibitörlerinin eczane perakende satış fiyatları her takvim yılı başında merkezi ilaç komisyonu kararıyla güncellenir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Kolinesteraz inhibitörlerinin eczane perakende satış fiyatları her takvim yılı başında merkezi ilaç komisyonu kararıyla güncellenir <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

### Bölüm: Hukuk (İş Kanunu) Alanı Vakaları

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_01</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> İşçinin kıdem tazminatına hak kazanabilmesinin temel koşulları nelerdir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> 4857 sayılı İş Kanunu'na göre aynı işverenin işyerinde en az bir tam yıl çalışmış olan işçi, iş sözleşmesinin kanunda belirtilen haklı veya geçerli nedenlerle feshedilmesi halinde kıdem tazminatına hak kazanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>4857 sayılı İş Kanunu'na göre aynı işverenin işyerinde en az bir tam yıl çalışmış olan işçi, iş sözleşmesinin kanunda belirtilen haklı veya geçerli nedenlerle feshedilmesi halinde kıdem tazminatına hak kazanır. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_02</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Altı aydan az çalışmış işçinin fesih bildirimi nasıl yapılır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken iki haftalık ihbar süresine uyulması veya bu süreye ait ücretin ihbar tazminatı olarak ödenmesi gerekir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken fesih bildirimi nasıl yapılmalıdır? <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>İşi altı aydan az sürmüş olan işçinin belirsiz süreli iş sözleşmesi feshedilirken fesih bildirimi nasıl yapılmalıdır? <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_03</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Ahlak ve iyi niyet kurallarına aykırılık halinde tazminat ödenir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İş sözleşmesi İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence feshedilen işçiye kıdem ve ihbar tazminatı ödenmez.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İş sözleşmesi İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence feshedilen işçiye kıdem ve ihbar tazminatı ödenmez. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_04</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> İşe iade davası açma usulü nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur ve doğrudan mahkemeye dava açılamaz.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
<li>Doğrudan mahkemeye dava açılamaz. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddia, bağlamda açıkça belirtilen 'feshe karşı işe iade davası açmak isteyen işçinin, bildirim tebliğinden itibaren bir ay içinde arabulucuya başvurması zorunludur ve doğrudan mahkemeye dava açılamaz' bilgisiyle tamamen uyumlu olup, her iki önerme de bağlam tarafından doğrudan doğrulanmaktadır. Model A, iddiayı doğru bir şekilde supported olarak değerlendirmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_05</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Kıdem tazminatı şartı ve hesaplama katsayısı nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İş sözleşmesinin feshinde işçinin kıdem tazminatına hak kazanması için en az bir yıl çalışması şarttır ve kıdem tazminatı tavan sınırı olmaksızın brüt ücretin iki katı üzerinden hesaplanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İş sözleşmesinin feshinde işçinin kıdem tazminatına hak kazanması için en az bir yıl çalışması şarttır. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Kıdem tazminatının hesaplanmasında tavan sınırı olmaksızın brüt ücretin iki katı üzerinden hesaplanır. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_06</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Üç yıldan fazla çalışan işçinin ihbar süresi ve uyulmama yaptırımı nedir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Üç yıldan fazla kıdemi olan işçi için ihbar süresi sekiz haftadır ve bildirim şartına uymayan taraf ihbar tazminatının yanı sıra hapis cezasıyla cezalandırılır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Üç yıldan fazla kıdemi olan işçi için ihbar süresi sekiz haftadır. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Bildirim şartına uymayan taraf ihbar tazminatının yanı sıra hapis cezasıyla cezalandırılır. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_07</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge yanliş">❌ Sistem Kararı: YANLIŞ</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> İşe iade sürecinde başvuru süreleri ve alternatif yollar nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır ancak dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
<li>dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddiada doğru bir bilgi (işe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır) ile bağlamda olmayan veya çelişen bir bilgi (dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir) bir arada yer almaktadır. Model B'nin atomik analizinin gösterdiği gibi, ikinci parça bağlam tarafından doğrulanmamaktadır ve bu durum doğrudan bir çelişki oluşturmaktadır.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_08</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Kıdemi bir buçuk yıla kadar olan işçinin ihbarı ve ahlak dışı fesih nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İşi altı aydan bir buçuk yıla kadar süren işçi için ihbar süresi dört haftadır; ayrıca 25/II maddesi gereğince ahlak kurallarına uymayan işçiye her durumda peşin ihbar tazminatı ödenmesi zorunludur.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İşi altı aydan bir buçuk yıla kadar süren işçi için ihbar süresi dört haftadır. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Ayrıca 25/II maddesi gereğince ahlak kurallarına uymayan işçiye her durumda peşin ihbar tazminatı ödenmesi zorunludur. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_09</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Altı aydan az kıdemi olan işçinin ihbar süresi kaç haftadır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> 4857 sayılı İş Kanunu'na göre işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresi sekiz hafta olarak uygulanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>4857 sayılı İş Kanunu'na göre işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresi sekiz hafta olarak uygulanır. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>supported</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddia, işi altı aydan az sürmüş bir işçinin fesih bildirimi için ihbar süresinin sekiz hafta olduğunu iddia etmektedir, ancak bağlamda bu sürenin iki hafta olduğu açıkça belirtilmiştir. Model B'nin atomik analizinin ortaya koyduğu gibi, bu iddia bağlamla doğrudan çelişmektedir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_10</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Üç ay çalıştıktan sonra istifa eden işçi kıdem tazminatı alabilir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İş yerinde sadece üç ay çalışmış olan ve kendi isteğiyle istifa eden bir işçi kıdem tazminatına tam olarak hak kazanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İş yerinde sadece üç ay çalışmış olan <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
<li>kendi isteğiyle istifa eden bir işçi <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
<li>kıdem tazminatına tam olarak hak kazanır <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddiada yer alan 'kıdem tazminatına tam olarak hak kazanır' ifadesi, bağlamda belirtilen 'işçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması' şartıyla doğrudan çelişmektedir. Ayrıca, işçi istifa ettiğinden kıdem tazminatı alamayacağı da bağlamda belirtilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_11</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Ahlak ve iyi niyete aykırı fesihte kıdem ve ihbar tazminatı ödenir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına aykırılık gerekçesiyle işten çıkarılan personele işverence hem kıdem hem de ihbar tazminatı eksiksiz ödenir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İş Kanunu'nun 25/II maddesindeki ahlak ve iyi niyet kurallarına aykırılık gerekçesiyle işten çıkarılan personele işverence hem kıdem hem de ihbar tazminatı eksiksiz ödenir. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_12</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Arabulucuya gitmeden doğrudan iş mahkemesinde dava açılabilir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İş sözleşmesi feshedilen çalışan, arabulucuya başvurma şartı aranmaksızın doğrudan doğruya iş mahkemesinde dava açabilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İş sözleşmesi feshedilen çalışan, arabulucuya başvurma şartı aranmaksızın doğrudan doğruya iş mahkemesinde dava açabilir. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_13</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Bir yılı dolduran işçinin yıllık izin hakkı kaç gündür?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Aynı işverenin işyerinde bir yılı dolduran işçinin yıllık ücretli izin hakkı en az on dört iş günüdür.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Aynı işverenin işyerinde bir yılı dolduran işçinin yıllık ücretli izin hakkı en az on dört iş günüdür. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddia, yıllık ücretli izin hakkının en az on dört iş günü olduğunu belirtmektedir, ancak bağlamda bu bilgiye dair hiçbir kanıt veya doğrulama bulunmamaktadır. Model B'nin kararı, bağlamın yalnızca ihbar süreleri, kıdem tazminatı ve iş sözleşmesinin feshi ile ilgili hükümleri içerdiği gerçeğini göz ardı etmektedir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_14</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Haftalık kırk beş saati aşan fazla çalışmalar nasıl ücretlendirilir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Haftalık kırk beş saati aşan fazla çalışma süreleri için işçiye normal saatlik ücretinin yüzde elli fazlası ödenir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Haftalık kırk beş saati aşan fazla çalışma süreleri için işçiye normal saatlik ücretinin yüzde elli fazlası ödenir. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_15</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> Kıdem tazminatı tavan ücreti nasıl belirlenir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Kıdem tazminatına esas teşkil eden tavan ücret her yıl Asgari Ücret Tespit Komisyonu tarafından oy birliğiyle belirlenir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Kıdem tazminatına esas teşkil eden tavan ücret her yıl Asgari Ücret Tespit Komisyonu tarafından belirlenir. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_law_16</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> 4857 sayılı İş Kanunu'na göre belirsiz süreli iş sözleşmelerinin feshinden önce durumun diğer tarafa bildirilmesi gerekir. İhbar süresi; işi altı aydan az sürmüş işçi için iki hafta, altı aydan bir buçuk yıla kadar sürmüş işçi için dört hafta, bir buçuk yıldan üç yıla kadar sürmüş işçi için altı hafta ve üç yıldan fazla sürmüş işçi için sekiz haftadır. Bildirim şartına uymayan taraf, bildirim süresine ilişkin ücret tutarında ihbar tazminatı ödemek zorundadır. İşçinin kıdem tazminatına hak kazanabilmesi için aynı işverenin işyerinde en az bir tam yıl (365 gün) çalışmış olması ve iş sözleşmesinin kanunda sayılan haklı veya geçerli nedenlerle sona ermiş olması şarttır; istifa eden (kanundaki istisnalar hariç) işçi kıdem tazminatı alamaz. İş Kanunu'nun 25/II maddesi uyarınca ahlak ve iyi niyet kurallarına uymayan haller sebebiyle işverence yapılan fesihlerde işçiye kıdem ve ihbar tazminatı ödenmez. Feshe karşı işe iade davası açmak isteyen işçi, fesih bildiriminin tebliğinden itibaren bir ay içinde arabulucuya başvurmak zorundadır; doğrudan iş mahkemesinde dava açılamaz.</p>
      <p><strong>Soru:</strong> İhbar süresi boyunca işçiye yeni iş arama izni verilir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> İhbar süresi boyunca işveren işçiye günde iki saatten az olmamak üzere yeni iş arama izni vermekle yükümlüdür.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>İhbar süresi boyunca işveren işçiye günde iki saatten az olmamak üzere yeni iş arama izni vermekle yükümlüdür <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>contradicted</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> Bağlamda ihbar süresi boyunca işverenin işçiye yeni iş arama izni verme yükümlülüğü hakkında hiçbir bilgi bulunmamaktadır. Model B'nin kararı olan 'unverifiable' doğru bir değerlendirmedir çünkü bağlamda bu konuya dair hiçbir bilgi yoktur.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

### Bölüm: Finans (Eurobond) Alanı Vakaları

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_01</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Hazine ihraçlı Eurobondların kupon ödeme sıklığı ve niteliği nedir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Türkiye Cumhuriyeti Hazinesi tarafından ihraç edilen Eurobondlar genellikle altı ayda bir ya da yılda bir kupon faizi ödemesi gerçekleştiren uzun vadeli borçlanma araçlarıdır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Türkiye Cumhuriyeti Hazinesi tarafından ihraç edilen Eurobondlar <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>genellikle altı ayda bir ya da yılda bir kupon faizi ödemesi gerçekleştiren uzun vadeli borçlanma araçlarıdır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_02</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobond işlemlerinde standart takas süresi nedir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddia, bağlamda açıkça belirtilen 'Eurobond alım satım işlemlerinde standart piyasa takas süresi işlem gününü izleyen ikinci iş günü (T+2) olarak uygulanır' bilgisini doğrudan tekrarlamaktadır. Model A'nin kararı, bağlamın iddianın tümünü desteklediğini doğru bir şekilde yansıtmaktadır.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_03</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Yerli bireysel yatırımcı için kupon faizlerinde stopaj kesintisi var mıdır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Hazine ihraçlı Eurobondların kupon faiz gelirlerinde yerli bireysel yatırımcılara uygulanan stopaj oranı yüzde sıfırdır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Hazine ihraçlı Eurobondların kupon faiz gelirlerinde yerli bireysel yatırımcılara uygulanan stopaj oranı yüzde sıfırdır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_04</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobondlar fiziken mi teslim edilir yoksa kayden mi saklanır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobondlar yatırımcılara fiziki olarak teslim edilmeyip Takasbank ile Euroclear veya Clearstream gibi merkezlerde kaydi sistemde saklanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobondlar yatırımcılara fiziki olarak teslim edilmeyip Takasbank ile Euroclear veya Clearstream gibi merkezlerde kaydi sistemde saklanır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
            <td><code>supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_05</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Takas süresi ve senet teslimi nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobond alım satımında standart takas süresi T+2 olarak uygulanır ve alıcılar vadesi gelen tahvillerin fiziki senetlerini doğrudan banka şubesinden teslim alabilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobond alım satımında standart takas süresi T+2 olarak uygulanır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>alıcılar vadesi gelen tahvillerin fiziki senetlerini doğrudan banka şubesinden teslim alabilir <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_06</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobond kupon faizlerinin stopajı ve beyanname zorunluluğu nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Hazine Eurobondlarının kupon faiz gelirlerinde stopaj oranı yüzde sıfırdır ve elde edilen gelir tutarı ne kadar yüksek olursa olsun hiçbir şekilde yıllık vergi beyannamesine dahil edilmez.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Hazine Eurobondlarının kupon faiz gelirlerinde stopaj oranı yüzde sıfırdır <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>elde edilen gelir tutarı ne kadar yüksek olursa olsun hiçbir şekilde yıllık vergi beyannamesine dahil edilmez <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_07</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobondların para birimi ve teminat yapısı nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobondlar ulusal para birimi dışındaki yabancı para cinsinden ihraç edilir; ayrıca Hazine tarafından ihraç edilen her bir Eurobond için Merkez Bankası altın cinsinden yüzde yüz karşılık tutmak zorundadır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobondlar ulusal para birimi dışındaki yabancı para cinsinden ihraç edilir. <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>Hazine tarafından ihraç edilen her bir Eurobond için Merkez Bankası altın cinsinden yüzde yüz karşılık tutmak zorundadır. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_08</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Kupon frekansı ve erken satış stopajı nasıldır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobond kupon ödemeleri altı ayda bir veya yılda bir yapılabilir; ayrıca vadeden önce ikincil piyasada yapılan satışlarda bankalarca anında yüzde kırk oranında kaynakta stopaj kesintisi yapılır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobond kupon ödemeleri altı ayda bir veya yılda bir yapılabilir <br><span class="atom-label entailment">mDeBERTa NLI Tahmini: <code>entailment</code></span></li>
<li>vadeden önce ikincil piyasada yapılan satışlarda bankalarca anında yüzde kırk oranında kaynakta stopaj kesintisi yapılır <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
            <td><code>partially_supported</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>partially_supported</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_09</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobond işlemlerinde takas aynı gün mü yapılır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobond işlemlerinde işlemlerin takas ve ödeme mutabakatı işlem yapılan gün içinde (T+0 aynı gün) anlık olarak sonuçlandırılmak zorundadır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobond işlemlerinde işlemlerin takas ve ödeme mutabakatı işlem yapılan gün içinde (T+0 aynı gün) anlık olarak sonuçlandırılmak zorundadır. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_10</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Hazine Eurobondlarının kuponlarında stopaj kesintisi oranı nedir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Hazine ihraçlı Eurobond kupon gelirleri üzerinden yerli bireysel yatırımcılardan kupon ödeme anında yüzde yirmi beş oranında peşin stopaj vergisi kesilir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Hazine ihraçlı Eurobond kupon gelirleri üzerinden yerli bireysel yatırımcılardan kupon ödeme anında yüzde yirmi beş oranında peşin stopaj vergisi kesilir. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>unverifiable</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> İddiada yer alan yüzde yirmi beş oranında peşin stopaj vergisi kesilmesi bilgisi, bağlamda belirtilen yüzde sıfır stopaj oranıyla doğrudan çelişmektedir. Model B'nin atomik olarak ayırdığı önerme de bu çelişkiyi doğrulamaktadır.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_11</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobond kupon oranları değişken olarak belirlenebilir mi?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobond ihraçlarında belirlenen kupon faiz oranlarının ihraç esnasında değişken olarak belirlenmesi kanunen kesinlikle yasaklanmıştır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobond ihraçlarında belirlenen kupon faiz oranlarının ihraç esnasında değişken olarak belirlenmesi kanunen kesinlikle yasaklanmıştır. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_12</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobondlar fiziki kıymetli evrak mıdır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Yatırımcılar satın aldıkları Eurobondları Takasbank kaydı yerine basılı kıymetli evrak olarak fiziki şekilde saklamakla yükümlüdür.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Yatırımcılar satın aldıkları Eurobondları Takasbank kaydı yerine basılı kıymetli evrak olarak fiziki şekilde saklamakla yükümlüdür. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_13</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobond işlemlerinde asgari alım tutarı ne kadardır?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Bankalar arası Eurobond işlemlerinde asgari işlem limiti genellikle iki yüz bin ABD Doları olarak uygulanır.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Bankalar arası Eurobond işlemlerinde asgari işlem limiti genellikle iki yüz bin ABD Doları olarak uygulanır. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_14</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> CDS primleri Eurobond kupon oranlarını nasıl etkiler?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Türkiye'nin beş yıllık kredi temerrüt takası (CDS) primi arttığında ihraç edilecek Eurobondların kupon faizleri yükselir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Türkiye'nin beş yıllık kredi temerrüt takası (CDS) primi arttığında <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
<li>ihraç edilecek Eurobondların kupon faizleri yükselir <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_15</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge hakem">⚖️ Hakem Kararı</span>
      <span class="badge yanliş">❌ Sistem Kararı: YANLIŞ</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Eurobond faiz ödemeleri hangi para biriminde talep edilir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler. <br><span class="atom-label contradiction">mDeBERTa NLI Tahmini: <code>contradiction</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>contradicted</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>contradicted</code></p>
      <p><strong>Mekanizma:</strong> Meta-Hakem (Llama-3.3-70B) Kararı</p>
<p><strong>Hakem Gerekçesi (Reasoning):</strong> Bağlamda Eurobondların genellikle ABD Doları veya Avro gibi yabancı para birimleri cinsinden ihraç edildiği belirtilmektedir, ancak kupon faizlerinin yalnızca İsviçre frangı cinsinden talep edilebileceği bilgisi bulunmamaktadır. Model B'nin doğrudan çelişki kararı vermesi daha uygun görünmektedir çünkü iddia edilen durum bağlam tarafından doğrulanmamaktadır.</p>
    </div>
  </div>
</div>
<div class="page-break"></div>

<div class="case-container">
  <div class="case-header">
    <h4>Vaka İncelemesi: <code>ood_fin_16</code></h4>
    <div style="display: flex; gap: 10px;">
      <span class="badge doğru">✅ Sistem Kararı: DOĞRU</span>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">1. Girdi Verileri (Bağlam ve Test Edilen İddia)</div>
    <div class="section-content">
      <p><strong>Bağlam:</strong> Eurobondlar (Eurotahvil), devletlerin veya şirketlerin kendi ulusal para birimleri dışındaki yabancı para birimleri (genellikle ABD Doları veya Avro) cinsinden uluslararası piyasalarda ihraç ettiği uzun vadeli borçlanma araçlarıdır. Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı tarafından ihraç edilen Eurobondlar genellikle 6 ayda bir veya yılda bir kupon faiz ödemesi yapar ve kupon oranları ihraç sırasında sabit veya değişken olarak belirlenir. Eurobond alım-satım işlemlerinde standart takas süresi işlem gününü takip eden ikinci iş günüdür (T+2). Hazine ihraçlı Eurobondlardan elde edilen kupon faiz gelirleri üzerinden yerli bireysel yatırımcılar için stopaj (kaynakta vergi kesintisi) oranı yüzde sıfırdır (%0); ancak yıllık beyan sınırını aşan gelirler yıllık gelir vergisi beyannamesi ile beyan edilmek zorundadır. Vadesinden önce ikincil piyasada satılan Eurobondlarda oluşan değer artış kazançları ise stopaja tabi olmayıp Gelir Vergisi Kanunu'na göre vergilendirilir. Eurobondlar fiziki olarak teslim edilmez; Takasbank ve uluslararası takas merkezleri (Euroclear ve Clearstream) nezdinde kaydi olarak saklanır.</p>
      <p><strong>Soru:</strong> Kurumsal Eurobond portföyleri ne sıklıkla denetlenir?</p>
      <p><strong>İddia (Sistem Çıktısı):</strong> Kurumsal yatırımcıların portföylerindeki Eurobond tutarı Bankacılık Düzenleme ve Denetleme Kurumu tarafından üç ayda bir denetlenir.</p>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">2. K2 Süreci (Gemma-4 ile Ayrıştırma, mDeBERTa ile Doğrulama)</div>
    <div class="section-content">
<ul>
<li>Kurumsal yatırımcıların portföylerindeki Eurobond tutarı Bankacılık Düzenleme ve Denetleme Kurumu tarafından üç ayda bir denetlenir. <br><span class="atom-label neutral">mDeBERTa NLI Tahmini: <code>neutral</code></span></li>
</ul>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">3. Modellerin Karar Matrisi</div>
    <div class="section-content">
      <table>
        <thead>
          <tr>
            <th>Zemin Gerçeği (Gold Label)</th>
            <th>K1 Kararı (ELECTRA)</th>
            <th>K2 Kararı (Gemma+mDeBERTa)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
            <td><code>unverifiable</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-box">
    <div class="section-title">4. Nihai Karar ve Gerekçe</div>
    <div class="section-content">
      <p><strong>Nihai Karar:</strong> <code>unverifiable</code></p>
      <p><strong>Mekanizma:</strong> Yerel Modeller Arası Doğrudan Uzlaşma (LLM'e gidilmedi)</p>
<p><strong>Açıklama:</strong> K1 ve K2 modelleri birbiriyle tam uyuştuğu için karar doğrudan kabul edilmiştir.</p>
    </div>
  </div>
</div>

<div class="page-break"></div>

## 5. Hata Analizi (Derinlemesine İnceleme)

Sistem, Dağılım Dışı (OOD) test setindeki 48 vakanın 45'ini kusursuz şekilde sınıflandırmış, ancak 3 vakada (1 Tıp, 1 Hukuk, 1 Finans) hata yapmıştır. Hibrit mimarinin zayıf noktalarını tespit etmek amacıyla bu 3 vakanın hata mekanizmaları aşağıda detaylandırılmıştır.

### 4.1. Tıp Vakası (ood_med_10)
- **İddia:** *Memantin bir kolinesteraz inhibitörü olup kalsiyumun hücreye aşırı girişini hızlandırarak eksitotoksisiteyi artırmak amacıyla uygulanır.*
- **Altın Etiket:** Contradicted (Bağlamla Çelişiyor)
- **Sistem Kararı:** Partially Supported (Kısmen Destekleniyor) ❌
- **Hata Mekanizması (Hakem Halüsinasyonu):** İddianın tamamı bağlamla çelişmesine rağmen, K2 NLI modülü (mDeBERTa) iddiayı atomlarına böldükten sonra hatalı bir şekilde `[entailment, contradiction]` tahmini yapmış ve uyuşmazlık Hakem'e (Llama-3.3-70B) gitmiştir. Büyük dil modeli (Hakem) bağlamı okurken tıp domaini ile ilgili kendi içsel (pre-trained) bilgisini araya karıştırmış, memantinin bir kolinesteraz inhibitörü olduğunu zannederek iddianın ilk yarısını *doğru* kabul etmiş ve kararı `partially_supported` olarak onaylamıştır. Bu durum, Hakem modelinin aşırı özgüvenli halüsinasyonlarının sistemin doğruluğunu nasıl bozduğuna dair klasik bir örnektir.

### 4.2. Hukuk Vakası (ood_law_07)
- **İddia:** *İşe iade talebinde bulunan işçi fesih tebliğinden itibaren bir ay içinde arabulucuya başvurmalıdır ancak dileyen işçi arabulucuya gitmeden doğrudan noter kanalıyla tazminatını tahsil edebilir.*
- **Altın Etiket:** Partially Supported (Kısmen Destekleniyor)
- **Sistem Kararı:** Contradicted (Bağlamla Çelişiyor) ❌
- **Hata Mekanizması (Kavramsal Yanılgı):** İddia, bağlamda var olan DOĞRU bir bilgi ile bağlamla çelişen YANLIŞ bir bilginin birleşiminden oluştuğu için tam olarak *Partially Supported* etiketine uymaktadır. Ancak Hakem modeli (Llama), *"bir cümlenin içinde tek bir yalan varsa o cümlenin tamamı yalandır"* şeklinde katı bir mantıksal tümevarım (strict boolean logic) yürüterek kararı `contradicted` olarak bozmuştur. Model, *Kısmen Destekleniyor* etiketinin tanım sınırlarını esnetememiştir.

### 4.3. Finans Vakası (ood_fin_15)
- **İddia:** *Eurobond satın alan yatırımcılar ilgili tahvilin kupon faizlerini yalnızca İsviçre frangı cinsinden talep edebilirler.*
- **Altın Etiket:** Unverifiable (Doğrulanamaz)
- **Sistem Kararı:** Contradicted (Bağlamla Çelişiyor) ❌
- **Hata Mekanizması (Aşırı Çıkarım - Over-inference):** Bağlamda Eurobondların *"genellikle ABD Doları veya Avro gibi para birimleri cinsinden ihraç edildiği"* bilgisi yer almaktadır. Bağlam, İsviçre frangını kesin bir dille yasaklamadığı için altın etiket `unverifiable` olmalıdır. Ancak K2 ve Hakem modeli, *"genellikle dolar veya avro ise, YALNIZCA İsviçre frangı olması imkansızdır"* şeklinde probabilistik (olasılıksal) bir mantık yürüterek bunu doğrudan çelişki (`contradicted`) olarak işaretlemiştir. Dil modellerinin, metinde verilmeyen bilgileri dünyevi mantıkla (world knowledge) çürütmeye çalışması bu hatanın temel sebebidir.
