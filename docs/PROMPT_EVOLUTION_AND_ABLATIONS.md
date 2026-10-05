# Meta-Hakem İstem Evrimi ve Kronolojik Ablasyon Matrisi (Prompt Evolution & Ablation Matrix)

**Proje:** TR-FactBench Kademeli Hibrit Halüsinasyon Tespiti Boru Hattı  
**Model:** `meta-llama/llama-3.3-70b-instruct` (Meta-Hakem)  
**Tarih:** Ekim 2026  

Bu doküman, tez ve araştırma makalesi için Meta-Hakem (Llama-3.3-70B) isteminin (prompt) başlangıçtan zirveye kadar geçirdiği **4 kronolojik evrim aşamasını**, her aşamadaki teorik motivasyonu, tam istem metinlerini ve elde edilen ampirik metrikleri arşivlemektedir.

---

## 1. Kronolojik Evrim ve Metrik Karşılaştırma Özeti

| Versiyon | Deney Kodu | Temel Mimari / İstem Müdahalesi | 123 Gri Alan Hakem Başarımı | 480 Vaka Uçtan Uca Doğruluk | Oracle Tavanına Uzaklık |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **V1** | `K3-FEWSHOT-LLAMA70B` | **Erken Etiket Taahhüdü:** Model önce etiket, sonra açıklama üretiyor. Atomlar etiketli. | %75.83 (91/120) | %89.54 | %3.56 |
| **V2** | `K3-COT-REASONING-FIRST` | **Akıl Yürütme Önceliği (CoT):** JSON çıktısında önce `reasoning`, sonra karar token'ı üretildi. | %80.49 (99/123) | %90.83 | %2.50 |
| **V3** | `K3-DEBIASED-NEUTRAL-ATOMS` | **Bileşen 0 Ayrışımı & Nötr Atomlar:** Atomlar mDeBERTa'dan ayrıldı, NLI etiketleri maskelendi. | %86.99 (107/123) | %92.50 | %0.83 |
| **V4** | `K3-PREDICATE-AWARE` | **Semantik Yüklem & Hüküm Denetimi:** Yalnızca öznenin metinde geçmesi engellendi, eylem doğrulaması şart koşuldu. | **%89.43 (110/123)** | **%93.13 (447/480)** | **SADECE 1 VAKA (%0.21)!** |

---

## 2. Detaylı Versiyon Analizleri ve Arşivlenen İstemler

### VERSİYON 1 (V1): Temel Few-Shot İstem (Erken Etiket Taahhüdü)
- **Script:** `scripts/61_run_fewshot_meta_arbitration.py`
- **Klasör:** `reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1`
- **Temel Zaaf:** Hakemden doğrudan `{"final_decision": "...", "reasoning": "..."}` formatında çıktı istendi. Model, kanıtı tartmadan ilk token'da bir etikete bağlandığı (premature commitment) için gerekçesini bu hatalı ilk kararı meşrulaştırmak üzere kurguluyordu.

```text
[V1 İSTEM ŞABLONU]
Sen iki modelin çelişkisini çözen Baş Hakemsin.
BAĞLAM: {context}
İDDİA: {claim}
MODEL A: {k1_pred}
MODEL B: {k2_pred}
- Atom 1: "{atom_1}" -> Sonuç: {label_1}
- Atom 2: "{atom_2}" -> Sonuç: {label_2}

Çıktı Formatı:
{
  "final_decision": "<karar>",
  "favored_model": "<model>",
  "reasoning": "<gerekçe>"
}
```

---

### VERSİYON 2 (V2): Akıl Yürütme Öncelikli CoT (Chain-of-Thought)
- **Script:** `scripts/64_run_cot_reasoning_first_arbitration.py`
- **Klasör:** `reports/experiments/K3-COT-REASONING-FIRST-LLAMA70B-v1`
- **Müdahale:** JSON nesnesinin sırası tersine çevrildi: önce `reasoning`, sonra `favored_model`, en son `final_decision`. Model karar vermeden önce delilleri Türkçe olarak analiz etmeye zorlandı.
- **Kazanım:** Hakem doğruluğu %75.83'ten **%80.49'a (+%4.66)** yükseldi.

```text
[V2 İSTEM ŞABLONU]
Lütfen ÖNCE bağlamdaki kanıtı adım adım düşünerek analiz et, ARDINDAN kararını ver.
SADECE aşağıdaki JSON formatında çıktı üret:
{
  "reasoning": "<Önce kanıtı ve modellerin analizini değerlendiren 2 cümlelik mantıklı gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}
```

---

### VERSİYON 3 (V3): Bileşen 0 Ayrışımı ve Nötr Atomlar (Etiket Maskeleme)
- **Script:** `scripts/74_run_debiased_neutral_atoms_arbitration.py`
- **Klasör:** `reports/experiments/K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1`
- **Teorik Temel:** Model B'nin (mDeBERTa) ürettiği ara NLI etiketleri hakeme gösterildiğinde, hakem bu etiketleri mutlak doğru sanarak zehirleniyordu (Cascading Error / Granularity Bias).
- **Müdahale:** Atomik ayrıştırma "Bileşen 0" olarak bağımsızlaştırıldı. Atomların yanındaki `-> Sonuç: entailment` gibi NLI etiketleri tamamen maskelendi ve atomlar etiketsiz yapıtaşları olarak sunuldu.
- **Kazanım:** Hakem doğruluğu %80.49'dan **%86.99'a (+%6.50)** fırladı. OOD harici testlerinde 48'de 48 (%100.0) başarı sağlandı.

```text
[V3 İSTEM ŞABLONU]
İDDİANIN ATOMİK ÖNERMELERİ (Ön İnceleme - Bağımsız Ayrıştırıcı Tarafından Bölünmüş Yapıtaşları):
1. "{atom_1}"
2. "{atom_2}"

BİLİRKİŞİ MODELLERİNİN DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): {k1_pred}
- Model B (Atomik Analiz): {k2_pred}
```

---

### VERSİYON 4 (V4): Semantik Yüklem ve Eylem Denetimli Nihai İstem (ZİRVE)
- **Script:** `scripts/75_run_predicate_aware_debiased_arbitration.py`
- **Klasör:** `reports/experiments/K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1`
- **Teorik Temel:** Hakemin en büyük yanılgısının, cümlenin sadece öznesinin bağlamda geçmesini "kısmi destek" sanması olduğu tespit edildi.
- **Müdahale:** Prompt kurallarına açık bir semantik kural eklendi: *"Öznenin geçmesi destek sayılmaz; özneye yüklenen eylemin/hükmün de doğrulanması şarttır. Hüküm yoksa karar kesinlikle partially_supported değil, 'unverifiable' olmalıdır."*
- **Kazanım:** Hakem doğruluğu **%89.43'e (110/123)** ulaştı. 480 vakalık testte uçtan uca doğruluk **%93.13 (447/480)** seviyesine çıkarak teorik Oracle tavanına (%93.33) sadece **1 vaka mesafeye** yaklaştı.

```text
[V4 NİHAİ İSTEM ŞABLONU - CANLI KULLANILAN METİN]
Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı bilirkişi modeli uzlaşamamıştır. İddianın bağımsız olarak ayrıştırılmış atomik önermelerini ve bilirkişi modellerinin kararlarını inceleyerek hakem kararını ver.

[...FEW-SHOT EMSAL KARARLARI...]

ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
"""{context}"""

İDDİA:
"""{claim}"""

İDDİANIN ATOMİK ÖNERMELERİ (Ön İnceleme - Bağımsız Ayrıştırıcı Tarafından Bölünmüş Yapıtaşları):
{atoms_str}

BİLİRKİŞİ MODELLERİNİN DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): {k1_pred}
  (İddianın tüm bağlam içindeki mantıksal kapsamını tek seferde değerlendirmiştir.)
- Model B (Atomik Analiz): {k2_pred}
  (Yukarıdaki atomik önermelerin her birini tekil olarak test ederek bu sonuca varmıştır.)

ETİKET KURALLARI VE DİKKAT EDİLECEK HUSUSLAR:
1. supported: İddiadaki BÜTÜN önermeler bağlam tarafından açıkça doğrulanmaktadır.
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek eylem/bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir önerme yer alıyorsa bu etiket ZORUNLUDUR.
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda önermelere dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.

*** ÇOK ÖNEMLİ: SEMANTİK YÜKLEM VE EYLEM KURALI ***
- Bir cümlenin sadece öznesinin veya kavram adının bağlamda geçmesi o cümlenin "desteklenen parçası" SAYILMAZ!
- Desteklenen bir parçadan söz edebilmek için, özneye yüklenen eylemin/özelliğin/hükmün de bağlamda açıkça doğrulanması gerekir.
- Eğer iddiadaki önermelerin özneleri bağlamda geçiyor fakat iddia edilen eylemler/hükümler bağlamda yer almıyorsa (eylem doğrulanmıyorsa ve bağlamda bu konuda bir bilgi yoksa), karar kesinlikle partially_supported DEĞİL, 'unverifiable' OLMALIDIR!
- Bir iddianın içinde hem doğrulanmış bir gerçek hem de açık bir zıtlık varsa asla contradicted deme, partially_supported seç!

Lütfen ÖNCE bağlamdaki kanıtı ve ayrıştırılmış önermelerin yüklemlerini/eylemlerini adım adım analiz et, ARDINDAN kararını ver. SADECE aşağıdaki JSON formatında çıktı üret:
```json
{
  "reasoning": "<Önce bağlamdaki kanıtı ve önermelerin eylemlerini tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}
```
```

---

## 3. Teze Eklenecek İstem Mühendisliği Tartışma Argümanları

1. **Kanıt Odaklı Tasarım (Evidence-First):** V1'den V2'ye geçiş, üretici modellerin ilk ürettiği token'a sadık kalma (autoregressive commitment) zaafının CoT ile çözülebileceğini kanıtlamıştır.
2. **Kavramsal Ayrışım (Intermediate Label Masking):** V2'den V3'e geçiş, alt modellerin zayıf NLI etiketlerinin üst hakeme sızdırılmaması gerektiğini, aksi takdirde hakemin manipüle olduğunu (cascading error) göstermiştir.
3. **Yüklem Doğrulaması (Predicate Grounding):** V3'ten V4'e geçiş, büyük dil modellerinin "kavram/özne tanıdıklığı" ile "gerçek eylem doğrulaması" arasındaki farkı ayırt edebilmesi için istem seviyesinde açık mantıksal sınır şartlarına ihtiyaç duyduğunu ispatlamıştır.
