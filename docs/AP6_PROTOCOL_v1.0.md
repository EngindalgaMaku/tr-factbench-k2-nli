# AP6 — Gerçek RAG Çıktılarında Genellenebilirlik Protokolü (v1.0)

- Durum: **DONDURULDU (v1.0, 2026-10-06)** — yanıt üretiminden önce. Bundan sonraki her değişiklik ayrı bir sürümle ve gerekçesiyle kaydedilir.
- Tarih: 2026-10-06
- Üretim istemi: `k2_nli/data/ap6/rag/generation_prompt_v1.0.json` (dondurulmuş, hash kayıtlı).

---

## 1. Araştırma sorusu

Dengeli ve kontrollü veride (TR-FactBench) geliştirilen hibrit sistem, yeniden eğitim ve istem değişikliği
yapılmadan, doğal dağılımlı gerçek Türkçe RAG çıktılarında:

1. **S1 — Yanlış alarm:** Desteklenen cümleleri ne sıklıkla halüsinasyon olarak işaretliyor?
2. **S2 — Yakalama:** Gerçek halüsinasyonları (desteklenmeyen cümleleri) ne ölçüde yakalıyor?
3. **S3 — Oran ve tür:** Farklı boyuttaki Türkçe LLM'ler kaynak verildiğinde ne sıklıkla ve hangi türde sapıyor?
4. **S4 — Bileşen katkısı:** K1, K2, hibrit (P0 / PA / PB) ve tek başına LLM bu koşulda nasıl sıralanıyor?

## 2. Dondurulmuş sistem (değiştirilmeyecek)

| Bileşen | Sürüm |
|---|---|
| K1 | ELECTRA-TR LoRA `H1_DROP10_S45` |
| K2 | Gemma-4-E2B QLoRA atomizer (`google_gemma_4_e2b_it_final_adapter`) + mDeBERTa-v3 2mil7, soft-prob toplulaştırma |
| K3 uyuşmazlık hakemi | Llama-3.3-70B, V4 istemi (`scripts/75_...`) |
| K3 uzlaşma kontrolü | Kör Gemma-4-26B zero-shot; kurallar P0 / PA / PB (`configs/frozen/K3_ROUTING_POLICIES_v1.json`) |
| Karşılaştırma | Tek başına Gemma-4-26B zero-shot ve GPT-4.1-mini 8-shot (resmi benchmark istemi) |

## 3. Kaynak metinler (yeni toplanacak)

- 3 alan (finans, hukuk, tıp); her alanda 5–6 belge (toplam 16).
- Kamuya açık, kurumsal Türkçe kaynaklar. Öneri:
  - **Hukuk:** mevzuat.gov.tr kanun ve yönetmelik metinleri (FSEK md. 31 kapsamında telif dışı).
  - **Finans:** SPK, TCMB, BDDK yatırımcı ve tüketici rehberleri.
  - **Tıp:** Sağlık Bakanlığı ve üniversite hastanesi hasta bilgilendirme sayfaları.
- **Dışlama kuralı:** TR-FactBench train, DEV ve Gold bağlamlarıyla aynı konu olmamalı.
  Otomatik kontrol: karakter n-gram TF-IDF benzerliği; Gold–train için ölçülen değerler referans alınır.
- Her belge için URL, erişim tarihi ve lisans notu kaydedilir. **Gold'daki provenance eksikliği burada tekrarlanmayacak.**
- **TOPLANDI (2026-10-06):** 16 belge.
  - Script: `k2_nli/scripts/80_ap6_fetch_sources.py`
  - Kaynak listesi: `k2_nli/data/ap6/sources/source_manifest.csv` (URL, erişim zamanı, ham SHA-256, temizleme işaretleri, lisans notu)
  - Hukuk: 5199, 2918, 634, 5326, 6098 sayılı kanunlar.
  - Finans: DASK SSS, TMSF SSS, SPK Kitle Fonlaması Tebliği, Findeks SSS, TCMB Finansal Tüketici Ücretleri Tebliği.
  - Tıp: KKKA (Bakanlık + HSGM), aşırı sıcaklar, fibromiyalji, varis, sedef.
  - Dışlanan konular: Alzheimer, İş Kanunu, Eurobond (OOD geliştirme kümesi); veride sık geçen konular (enflasyon, BES, kredi kartı vb.).
  - Kırpma (KARAR VERİLDİ 2026-10-06): 2918 KTK → künye + Beşinci Kısım (sürücü belgeleri, md. 36–45) + md. 118–121 (ceza puanı); 6098 TBK → künye + Kefalet Sözleşmesi (md. 581–603). Kurallar script'te başlık işaretleriyle tanımlı.
  - Son korpus boyutu: hukuk ~26.5 bin, finans ~22 bin, tıp ~4.6 bin kelime. Tıp korpusu küçük kalır; bu, alan karşılaştırmasında sınırlılık olarak raporlanır.

## 4. RAG düzeni (gerçek retrieval) — KARAR VERİLDİ 2026-10-06

1. **Parçalama:** Belgeler paragraf sınırlarına saygılı biçimde ~70 kelimelik parçalara bölünür
   (70 kelimeyi aşan tek paragraf cümle sınırından bölünür). İlk plan 85 kelimeydi; mDeBERTa tokenizer'ı Türkçede
   ~2.2 token/kelime ürettiği için 60 bağlamın 37'si 512 sınırını aşıyordu. Yanıt üretilmeden önce 70'e indirildi
   (K1 en fazla 419 token; mDeBERTa'da 30 kelimelik test iddiasıyla yalnızca 1 bağlam 529 token). Alan başına ayrı bir korpus oluşturulur.
2. **Retrieval:** `intfloat/multilingual-e5-large` (yerel GPU; "query:" / "passage:" önekleri), kosinüs benzerliği, top-k = 3,
   yalnızca sorunun ait olduğu alanın korpusunda arama yapılır. Gerekçe: çok dilli yoğun aramada yaygın standart.
   Retriever karşılaştırması yapılmadı; yalnızca kurulum sağlık kontrolü yapıldı: kanıt belgesi ilk 3 parçada, 59/60 (%98.3).
   Kaçan soru (LEG-B2) düzeltilmedi; gerçekçi retrieval kusuru olarak deneyde kalır. Script: `k2_nli/scripts/81_ap6_build_retrieval.py`.
3. **Üretim:** Sabit sistem istemi ("Yalnızca verilen kaynaklara dayanarak Türkçe yanıtla; kaynaklarda bilgi yoksa bunu belirt."),
   temperature = 0, max_tokens = 400. İstem metni üretimden önce dondurulur ve hash'lenir.
4. **Doğrulayıcının bağlamı:** LLM'e verilen 3 parçanın birleşimi (ortalama 175, en fazla 212 kelime). K1 ve K2'nin 512 token sınırına
   kırpma olmadan sığar; LLM ile doğrulayıcılar birebir aynı metni görür. Sınırı aşan örnek olursa sayısı raporlanır.

## 5. Sorular

- Alan başına ~20, toplam ~60 soru.
- Üç tür (KARAR VERİLDİ): alan başına 8 cevaplanabilir / 7 çok bilgili / 5 kısmen cevaplanabilir. **DONDURULDU: `k2_nli/data/ap6/questions/questions_v1.0.jsonl` (SHA-256 a225bb93…)**
  - **Cevaplanabilir:** Cevap korpusta açıkça var.
  - **Çok bilgili:** "Açıkla, koşullarını ve istisnalarını belirt" tipi; daha uzun ve çok atomlu yanıt üretir.
  - **Kısmen cevaplanabilir veya korpus dışı:** Gerçekçi retrieval boşluğu yaratır.
- Soru üretimi (KARAR VERİLDİ 2026-10-06): **LLM taslağı + araştırmacı süzmesi.**
  - Taslağı yazan LLM, yanıt üreten modellerden ve hakemlerden (Llama, Gemma, GPT ailesi) farklı bir aileden olmalıdır.
  - Taslak LLM'in adı, sürümü ve istemi kaydedilir.
  - Süzme kriterleri: Türkçe doğallık, tek bir bilgi ihtiyacı, cevabı sorunun içinde vermeme, tür etiketinin doğruluğu.
  - Elenen ve düzeltilen sorular sayısıyla raporlanır.
  - Sorular yanıtlar görülmeden dondurulur.

## 6. Yanıt üreten LLM'ler — KARAR VERİLDİ 2026-10-06

| Boyut | Model (OpenRouter) | Aile |
|---|---|---|
| Küçük (~3B) | `mistralai/ministral-3b-2512` | Mistral |
| Orta (~8B) | `qwen/qwen3-8b` | Qwen |
| Güçlü | `deepseek/deepseek-v4-pro` | DeepSeek |

Dışlanan aileler: Llama (K3 hakemi), Gemma (atomizer ve kör hakem), GPT (karşılaştırma), Claude (soru taslağı).
İstenen ve OpenRouter'ın döndürdüğü model kimlikleri her yanıtla birlikte kaydedilir.

## 7. Birim ve etiketleme

- **Birim:** Yanıt cümlesi. Bölme kuralı sabittir; kırık cümleler önceden tanımlı kuralla birleştirilir.
- **Etiket şeması:** TR-FactBench'in 4 sınıfı. Ayrıca yalnızca analiz için kullanılacak bir hata türü notu
  (ilişki uydurma, sayı/tarih, kapsam, olumsuzluk, bilgi ekleme, diğer).
- **Neyin etiketleneceği (yük azaltma):**
  - Sistemlerden **herhangi birinin** supported dışı dediği tüm cümleler.
  - Geri kalanlardan rastgele örneklem: 100 cümle, seed = 42 (KARAR VERİLDİ 2026-10-06).
  - Toplam hedef ~230 cümle.
- **Anotatör A (araştırmacı):** Tüm seçilen cümleler. Kör: sistem tahminleri ve seçilme nedeni gizli,
  cümleler karışık sırada.
- **Anotatör B (bağımsız):** Rastgele ~50 cümle, A'dan habersiz. κ raporlanır. Uzlaşma kaydı tutulur;
  anotatör rolleri baştan açıkça belgelenir.

## 8. Ölçütler (önceden ilan)

- **Yanlış alarm oranı (S1):** Insan etiketi supported olan cümlelerde sistemin supported dışı deme oranı.
  Örnekleme ağırlıklarıyla düzeltilmiş.
- **İkili tespit (S2):** supported / supported dışı için precision, recall ve F1; %95 bootstrap güven aralığı.
- **4 sınıflı sonuçlar:** Yalnızca betimsel (karışıklık matrisi); sınıf sayısı küçük olacağı için Macro-F1 ana ölçüt **değildir**.
- **Halüsinasyon oranı (S3):** Model ve alan bazında, örneklem düzeltmeli tahmin.
- **Maliyet:** LLM çağrı oranı (P0 / PA / PB) ve yanıt başına toplam gecikme.
- **Karşılaştırmalar:** Eşleştirilmiş testler (McNemar) ve bootstrap güven aralığı.

## 9. Sızıntı ve dürüstlük kuralları

- Sistem, istem ve kurallar etiketler görülmeden önce çalıştırılır; tahminler hash'lenip kaydedilir.
- Etiketler görüldükten sonra yapılan her değişiklik "post-hoc" olarak ayrı raporlanır.
- Bu protokol, veri toplamadan önce v1.0 olarak dondurulur ve commit edilir.

## 10. Açık kararlar özeti

1. Alan başına belge sayısı ve kaynak listesi
2. Retrieval yöntemi ve 512 token kırpma kuralı
3. Soru türü oranları ve soruları kimin yazacağı
4. Kesin model listesi
5. Rastgele örneklem boyutu

---

## Değişiklik kaydı

### v1.1 (2026-10-06, ana üretimden önce)
- `max_tokens` 400 → 2000. Sistem istemi ve şablon değişmedi (aynı hash).
- Gerekçe: Duman testinde (MED-A1, model başına 1 yanıt) qwen3-8b ve deepseek-v4-pro'nun gizli akıl yürütme
  tokenları `max_tokens` bütçesinden düştü (400'ün 179 ve 278'i). DeepSeek'in yanıtı cümle ortasında kesildi.
  Yanıt uzunluğu "en fazla 150 kelime" talimatıyla sınırlı kalır; akıl yürütme modellerin varsayılanında bırakıldı.
- Duman testi çıktıları `data/ap6/generation/smoke_test_v1.0/` altında saklandı, veri setine alınmadı.
- Cümle bölmede Markdown biçim işaretleri (örn. `**kalın**`) temizlenir; metin içeriği değişmez.

### v1.2 (2026-10-06, yanıtlar okunmadan önce)
- **Çekimser cümleler (abstention):** Yalnızca kaynağın bir bilgiyi içermediğini söyleyen cümleler
  (örn. "Kaynaklarda … belirtilmemiştir") 4 sınıflı ana değerlendirmeden ayrılır.
  - `scripts/83_ap6_split_sentences.py` bu cümleleri önceden sabitlenmiş bir kalıpla işaretler; Anotatör A etiketleme sırasında doğrular/düzeltir.
  - Ayrıca raporlanır: (1) model ve soru türü bazında çekimserlik oranı, (2) çekimserliğin doğruluğu (bilgi kaynakta gerçekten yok mu).
  - Hem bilgi hem çekimserlik içeren karışık cümleler normal iddia olarak etiketlenir.
- Cümle bölme kuralları yanıtlar okunmadan sabitlendi (script başlığında listelenmiştir).

### v1.3 (2026-10-07, yanıtlar üretildi; doğrulayıcılar çalıştırılmadan ve etiketleme yapılmadan önce)
- **Atıf işaretleri:** İsteme rağmen 5 cümlede görülen "(Kaynak [2])" vb. işaretler biçim kabul edilerek silinir (v1.1 biçim kuralının uzantısı). İçerik değişmez.
- **Bağlama bağımlı cümleler:** Cümleler olduğu gibi bırakılır (bağımsızlaştırma yapılmaz).
  - Doğrulayıcılara cümle, soru ve bağlamla birlikte verilir.
  - Anotatör soruyu ve yanıtın tamamını görür, hedef cümle vurgulanır; göndermeler yanıta göre çözülerek cümlenin söyledikleri etiketlenir.
  - "Bu/Bunlar/Söz konusu…" ile başlayan cümleler `back_reference` olarak işaretlenir ve ayrı alt küme olarak raporlanır.

### v1.4 (2026-10-07, atomizer çalıştırıldı; K2 NLI, hakem ve etiketleme öncesinde)
- Dondurulmuş atomizer ayarıyla (en fazla 180 üretilen belirteç) 854 cümlenin 2'sinde geçerli JSON üretilmedi.
  Eski sonsuz döngü düzeltmesi (`<end_of_turn>` durdurma belirteci + ilk geçerli JSON nesnesinin alınması) etkindir; iki vakada da döngü yoktur.
- `MED-B2__qwen3-8b__s01` (8 öğeli sayım cümlesi): çıktı 180 belirteçte kesiliyor. Yalnızca bu cümle 400 belirteç sınırıyla yeniden ayrıştırıldı;
  model 251 belirteçte kendiliğinden durdu, 8 önerme üretildi. Kayıtta `atomizer_retry` alanı vardır.
- `FIN-B1__ministral-3b-2512__s02`: 180 ve 400 belirteçte de biçimi bozuk JSON (her öğeden sonra fazladan `"]`). Onarılmadı;
  atomizer hatası olarak raporlanır. Bu cümlede K2 karar vermez, hibrit sistem K1 kararını kullanır (hakeme gönderilmez).
- Dondurulmuş ayarla üretilen dosya `data/ap6/verifier/atoms/k2_input_frozen180.jsonl` olarak saklanır.
- Raporda: "Dondurulmuş ayarlarla 2/854 ayrıştırma hatası; 1'i uzunluk sınırı artırılarak giderildi, 1'i hata olarak kaldı."
- Gözlem (değişiklik yok): Kör Gemma-26B karşılaştırma koşusunda 854 yanıtın 119'u yapılandırılmış çıktı modunda boşluk tekrarına girip
  uzunluk sınırında kesildi. Etiket alanı JSON'un ilk alanı olduğu için, Gold-480'deki (2 vaka) ile aynı ayrıştırma kuralıyla etiket
  kesilmeden önceki çıktıdan alındı. Kural değiştirilmedi; sayı raporda ayrıca verilir.

### v1.5 (2026-10-07, hiçbir etiket görülmeden önce)
- §7 seçim kuralı ("herhangi bir sistemin supported dışı dediği cümleler + 100 rastgele") ~230 cümle varsayıyordu; gerçek RAG yanıtlarında
  yedi sistemden en az birinin itirazı 854 cümlenin 636'sını kapsadı (+100 rastgele = 736).
- Karar (yazar, 2026-10-07): **tam sayım** — 854 cümlenin tamamı Anotatör A tarafından etiketlenir. Örnekleme ağırlıkları gerekmez;
  S1–S3 doğrudan tam küme üzerinde hesaplanır. Anotatör B: A kümesinden rastgele 50 cümle (seçim seed 44, sıra seed 45).
- A için öğe sırası karışık (seed 43), kimlikler anlamsız (`AP6-0001`…); eşleme `data/ap6/annotation/internal/` altında, anotatöre gösterilmez.
