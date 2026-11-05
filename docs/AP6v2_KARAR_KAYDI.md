# AP6 v2 — Karar kaydı

Bu dosya AP6 v2 deneyinin tasarım kararlarını, verildikleri sırayla kaydeder. Her karar araştırmacıyla birlikte tartışılarak verilir.
Literatür taraması: `../../reports/RAG halüsinasyon etiketleme protokolleri.md`

## K-001 — AP6 v1'in statüsü (2026-10-10)
AP6 v1 pilot çalışma olarak kabul edilir. Tezde kısa bir özetle ve protokol boşluklarına ilişkin bulgularıyla yer alır.

## K-002 — Pilot sistem sonuçları (2026-10-10)
Yol 1: v1 etiketleri üzerindeki sistem karşılaştırması (K1, K2, hibrit, LLM'ler) pilot özetine alınmaz. Sistem karşılaştırması v2 etiketleriyle yeniden yapılır.

## K-003 — Bağlam kurulumu (2026-10-11)
Seçenek B: kontrollü bağlam. Her sorunun bağlamı kanıt parçaları ve retrieval'dan gelen çeldirici parçalarla kurulur.
Kısmi sorularda eksik parçanın kanıtı bilerek dışarıda bırakılır ve bağlamda bulunmadığı doğrulanır.
Gerekçe: v1'de 6 "yanıtlanabilir" soruda kanıt bağlama girmemişti (belge düzeyinde hit@3 = 1,0 bunu göstermedi).
Soru tipi ile bağlam içeriğinin her zaman uyuşması ve yanlış çekimserliğin ölçülebilmesi amaçlanır.
Sınırlılık: gerçek retrieval hataları kapsam dışında kalır; tezde belirtilecek.

## K-004 — Bağlam uzunluğu (2026-10-11)
Seçenek 1: kısa bağlam. Bağlam, hedef cümleyle birlikte K2'nin 512 token sınırına sığacak uzunlukta tutulur
(yaklaşık en fazla 220 kelime; K2 tokenizer'ıyla ölçülür). Yapı: bir ya da iki kanıt parçası + çeldirici parçalar.
K1 ve K2 değiştirilmez; pencereleme eklenmez.
Gerekçe: kanıt parçası araştırmacı tarafından bütün olarak seçildiği için kısa bağlam kanıtın kesilmesine yol açmaz;
dondurulmuş sistemler Gold-480 ve AP6'da aynı kalır.
Sınırlılık: gerçek RAG bağlamlarından kısadır; uzun bağlam gerekirse ayrı bir dayanıklılık deneyi olarak eklenebilir.

## K-005 — Soru seti (2026-10-11)
Seçenek C: sorular baştan yazılır; v1'in 60 sorusu kullanılmaz.

## K-006 — Soru tipleri ve sayıları (2026-10-11)
Alan başına 20, toplam 60 soru: T1 tek bilgi 6, T2 çok bilgi 6, T3 kısmi 4, T4 yanıtlanamaz 4.
- T1: kanıt + çeldiriciler; beklenen doğru yanıt.
- T2: aynı konuda 2–3 bilgi, tek soru cümlesi; tüm kanıtlar bağlamda.
- T3: tek soru cümlesinde iki bilgi; birinin kanıtı bilerek bağlama konmaz.
- T4: konuyla ilgili ama cevabı bağlamda olmayan soru; yalnızca ilgili çeldiriciler.
Gerekçe: v1'deki birleşik iki soruluk kısmi sorular yanıtları karmaşıklaştırdı; tamamen yanıtlanamaz koşul yoktu.
T1–T4 birlikte doğru çekimserlik, yanlış çekimserlik ve uydurmanın ayrı ayrı ölçülmesini sağlar.

## K-007 — Kaynak belgeler (2026-10-11)
Seçenek B: hukuk (5) ve finans (5) belgeleri korunur; sağlık alanı resmî halk sağlığı sayfalarıyla genişletilir
(v1'de sağlık ≈ 4.600 kelime, hukuk ≈ 26.500, finans ≈ 22.000). Hastane sayfaları resmî sayfalarla değiştirilebilir.
Belge seçim ölçütleri: resmî kurum; özgün dili Türkçe; güncel; erişim tarihi ve sha256 kaydı;
alan başına en az 5 belge; bir belgeden en fazla 5 soru.

## K-008 — Sağlık belgeleri (2026-10-11)
Hastane sayfaları (T3 Fibromiyalji, T4 Varis, T5 Sedef) çıkarıldı. T1a, T1b, T2 korundu.
Eklenenler (Sağlık Bakanlığı alan adları): T6a Kuduz (Aşı Portalı), T6b Kuduz SSS (HSGM PDF), T7 Tuz ve Tuz Kullanımı
(HSGM broşürü, 2021), T8 Hipertansiyon (HSGM), T9a Mevsimsel Grip (Aşı Portalı), T10a Tetanos, T10b Erişkin Aşılama,
T11 Kızamık (Aşı Portalı), T12 Fiziksel Aktivite (HSGM).
Değişiklikler: "Tuz ve Sağlık" HTML sayfası ve grip.saglik.gov.tr SSS sayfası 404 verdi; ilki yerine HSGM tuz broşürü alındı,
ikincisi çıkarıldı. Hukuk ve finans belgeleri v1'den aynı ham dosyalarla kopyalandı (yeniden indirilmedi).
Script: `scripts/100_ap6v2_fetch_sources.py`; çıktı: `data/ap6v2/sources/`.
Hacim: hukuk 5 belge ≈ 26.500 kelime, finans 5 belge ≈ 22.000, sağlık 12 belge ≈ 10.600.
Not: T6a–T6b 6 cümle, T10a–T10b 2 cümle paylaşıyor; bağlam kurarken "kanıt bağlamda yok" kontrolü tüm parçalar üzerinde yapılmalı.

## K-009 — Soruların yazılması (2026-10-11)
Sorular araştırmacı ile Claude (Anthropic) birlikte, belge belge yazılır: Claude aday soruları kanıt parçası, tip,
beklenen cevap ve (T3/T4 için) yokluk kontrolüyle önerir; araştırmacı kabul eder, düzeltir ya da reddeder.
Her soru için taslak/onay bilgisi tutulur. Claude, yanıt üreten (Mistral, Qwen, DeepSeek) ve değerlendiren
(Gemma, GPT, Llama) model ailelerinden farklıdır. Sorular kaynak metinden ve yazım kurallarından üretilir;
pilot sonuçlarındaki model zayıflıkları hedeflenmez; set dondurulana kadar hiçbir modele sorulmaz.
SSS sayfaları yalnızca konu fikri için kullanılır (seçenek B); SSS soru başlığı kanıt parçasına konmaz.
Yazım kuralları: (1) tek, doğal soru cümlesi; (2) T1 tek somut bilgi; (3) kanıt cümlesini kelimesi kelimesine tekrar etmez;
(4) cevap yalnızca kanıttan çıkarılabilir; (5) kanıt parçası ≤ 80 kelime ve bütün; (6) T3'te eksik bilgi hiçbir belgede
yoktur (metin aramasıyla doğrulanır) ve makul bir meraktır; (7) T4 konuyla ilgili, cevabı hiçbir belgede yok;
(8) görüş/değerlendirme/kişisel tavsiye sorusu yok; (9) belge başına ≤ 5 soru; alan başına T1 6, T2 6, T3 4, T4 4.
Başlangıç alanı: sağlık.
Ek kural (2026-10-11): SSS başlığı olmadan anlamını yitiren listelerde kanıt parçası, soru biçiminde olmayan kısa bir
açıklayıcı giriş cümlesiyle başlatılır (ör. "Kuduz aşısı uygulaması gerektirmeyen durumlar şunlardır:"). Bu ekleme kayıtta not edilir.

## K-010 — Sağlık soruları (2026-10-11)
20 soru yazıldı ve tek tek onaylandı (MED-01…MED-20; T1 6, T2 6, T3 4, T4 4): `data/ap6v2/questions/questions_v2_draft.jsonl`.
Şablon tekrarı (MED-08/MED-16 gebelik + doz/yaş; MED-10/MED-17 Türkiye istatistiği) bilinçli olarak bırakıldı;
hukuk ve finansta T3/T4 kalıpları çeşitlendirilecek. Toplu kontrol için Excel: `AP6v2_saglik_sorulari_kontrol.xlsx` (araştırmacı kontrolü bekliyor).
Kaynak tutarsızlıkları nedeniyle soru yazılmayan konular: gebelere grip aşısı zamanı (T9a–T10b), KKK doz sayısı (T10b),
yetişkin haftalık aktivite hedefi ve hedef kalp hızı oranları (T12).

## K-011 — Mevcut benchmark kullanımı (2026-10-12)
Doğal çıktı deneyi için sıfırdan veri üretmek yerine yerleşik bir RAG halüsinasyon veri seti kullanılacak.
Aday: RAGBench (Friel vd., 2024; rungalileo/ragbench, CC BY 4.0) — soru + 4 belge + yanıt, yanıt cümlesi düzeyinde
destek etiketi; alanlar: biyomedikal (PubMedQA, CovidQA-RAG), hukuk (CUAD), finans (FinQA, TAT-QA); yayımlanmış
RAGAS/TruLens/DeBERTa sonuçları kıyaslama imkânı verir.
Etiketler: RAGBench'in GPT-4 (gümüş) etiketleri olduğu gibi kullanılır; yeniden etiketleme yapılmaz.
Çeviri: kesit Türkçeye cümle cümle, temiz biçimde çevrilir (cümle hizası korunur, etiketler cümleye taşınır).
Çeviri sonrası, etiketlerin Türkçe metinde geçerliliği için bir kontrol yapılır.
Başlangıç alanı: tıp (PubMedQA, CovidQA-RAG). K-003…K-010'daki kendi veri üretim çalışması bekletiliyor;
akıbeti RAGBench örnekleri incelendikten sonra konuşulacak.

## K-012 — RAGBench tıp kesiti ve çeviri (2026-10-12)
Kesit: PubMedQA test bölümünden rastgele (seed 42) 75 soru; her soru için iki modelin yanıtı (GPT-3.5-turbo-0125,
Claude 3 Haiku; aynı bağlam) → 150 yanıt, 818 yanıt cümlesi, 100 desteklenmeyen (%12,2; test bölümü: %12,8).
Dosyalar: `data/ragbench/medical/pmq75_source_en.jsonl` (çevirmene giden), `pmq75_labels_DO_NOT_SHOW_TRANSLATOR.jsonl`.
Çeviri: seçenek A — Claude ile bu oturumda, kontrollü ve parti parti; araştırmacı her partiyi kontrol eder.
Kurallar: cümle hizası ve anahtarlar korunur; bilgi eklenmez/çıkarılmaz; hatalar ve kesinlik düzeyi korunur;
sayı/birim/olumsuzluk aynen; terim sözlüğü tutulur; çevirmen etiketleri görmez; GPT-4 gerekçeleri çevrilmez.
Makalede: "Claude desteğiyle, kurallı ve insan kontrollü çeviri".

## K-013 — PMQ-053 beklemede (2026-10-11)
PMQ-053 (koyunlarda E. coli O103 izolasyonu; AIMS/AIMS-ELISA) çevirisi, güvenlik sınıflandırıcısı yanıtı
yarıda kestiği için tamamlanamadı. Parti 8'e dahil edilmedi (9 madde çevrildi).
Karar (araştırmacı, 2026-10-11): seçenek (a). Madde örneklemde kalır (75 soru korunur); çevirisi ayrı bir
oturumda tamamlanacak. Örneklemden madde çıkarılmaz, yedek soru eklenmez.
Açık iş: PMQ-053 çevirisi + parti 8'e eklenmesi.

## K-014 — Çeviri sonrası etiket kontrolü (2026-10-11)
Kapsamlı yeniden etiketleme yapılmadı; gerekçe: cümle anahtarı hizası ve sayılar her partide otomatik doğrulandı,
1.680 cümlenin tamamı araştırmacı tarafından İngilizce-Türkçe yan yana okundu (parti 1-10 kontrol dosyaları).
Araştırmacı kararı: riski en yüksek 22 desteklenmeyen cümlede Claude tarafından noktasal kontrol.
Seçim ölçütü: İngilizce cümlede olumsuzluk ifadesi (+2), sayı (+2), kesinlik/çıkarım ifadesi (+1) → en yüksek 22 satır.
Sonuç: 22/22 etikette çeviri etiketi bozmuyor; kesinlik düzeyi, olumsuzluk ve sayılar korunmuş.
Script: `scripts/111_ragbench_label_check.py` (tam kontrol dosyası da üretir: `review/etiket_kontrol.xlsx`).

## K-015 — RAGBench veri kalitesi notları (2026-10-11)
(1) Anahtar biçimi: 7 yanıtta GPT-4 cümle anahtarını noktayla yazmış ("a." yerine "a"); 26 etiket kaydı ve
PMQ-045'in 2 desteklenmeyen anahtarı bu nedenle eşleşmiyor. Veri birleştirmede anahtarlar normalleştirilecek
(sondaki nokta atılır); normalleştirmeden sonra desteklenmeyen cümle sayısı 100'e tamamlanıyor.
(2) İç tutarsızlık: 5 cümlede `fully_supported` alanı False ama cümle `unsupported_keys` listesinde değil
(PMQ-014/f, PMQ-035/c, PMQ-039/i, PMQ-069/e, PMQ-069/g; hepsi Claude yanıtlarında).
(3) Gerekçe-etiket uyuşmazlığı: PMQ-021 (a) desteklenmeyen listesinde, ancak GPT-4'ün gerekçesi cümleyi
"generally supported" diye niteliyor.
Analizde esas alınacak alan: `unsupported_keys` (RAGBench'in kendi raporladığı etiket). Yukarıdaki üç nokta
tezde veri kalitesi sınırlılığı olarak belirtilecek.

## K-016 — Veri seti birleştirme (2026-10-11)
Script: `scripts/112_ragbench_build_dataset.py`. Çıktı: `data/ragbench/medical/build/`
- `ragbench_tr_medical_claims.jsonl` (809 satır, doğrulayıcı girdisi; AP6 v1 satır biçimiyle uyumlu)
- `ragbench_tr_medical_labels.jsonl` (etiketler + GPT-4 gerekçeleri; isteme girmez)
- `manifest.json` (kaynak, dilim, çeviri, etiket şeması, sayımlar, sha256)
Kapsam: 74 madde, 148 yanıt, 809 yanıt cümlesi; 100 desteklenmeyen (%12,36). PMQ-053 henüz yok.
Etiket şeması: RAGBench ikili (supported / unsupported). `gold_binary` gerçek etiket;
`gold_label` yalnızca araç uyumluluğu içindir (unsupported → "unverifiable"), `label_status` bunu belirtir.
Bu dosyada 4 sınıflı metrik geçersizdir; tahminler puanlanmadan önce ikiliye indirilir.

## K-017 — Bağlam uzunluğu ve K2 (2026-10-11; karar 2026-10-14)
Ölçüm: 809 satırın 422'sinde (tam bağlam + iddia) mDeBERTa token sayısı 512'yi aşıyor (en uzun 961).
Belge bazlı pencerelemede hiçbir pencere sınırı aşmıyor (en uzun 362 token). Bu nedenle her satıra
`context_windows` alanı eklendi (kaynak belge başına 1 pencere, satır başına 5 pencere).
Açık karar: K2 pencereleme ile mi çalıştırılacak (her pencere ayrı puanlanıp en güçlü destek alınır)
yoksa bağlam kısaltılacak mı? Pencereleme dondurulmuş K2 akışında bir değişikliktir ve araştırmacı onayı gerekir.

Test (araştırmacı isteği, 2026-10-14): önce 10 satır (`scripts/113_ragbench_window_smoke.py`), ardından
809 satırın tamamı (`scripts/114_ragbench_window_compare.py`, çıktı `build/window_compare.json`).
Testler NLI kararını ölçer; Gemma atomlaştırıcısı atlanır, yani K2'nin nihai iddia etiketi değildir.
İkili eşleme: entailment → destekleniyor, diğerleri → desteklenmiyor; metrikler desteklenmeyen sınıfı içindir.
Sonuç (809 satır, gümüş etiketlere göre):
- A tam bağlam (512'de kesilir, 422 satır kesiliyor): F1 0,188 | duyarlılık 0,45 | yanlış alarm 0,470 | doğruluk 0,520
- B belge bazlı pencereleme: F1 0,301 | duyarlılık 0,62 | yanlış alarm 0,353 | doğruluk 0,644
- 282 satırda karar değişti: 191'i gerçek etikete yaklaştı, 91'i uzaklaştı (değişenlerin 54'ü 'general' gibi
  yumuşak destek değerine sahip satırlar).
Pencereleme her ölçütte daha iyi; ayrıca kesilme tamamen ortadan kalkıyor.
Karar (araştırmacı, 2026-10-14): belge bazlı pencereleme kullanılacak. Her kaynak belge ayrı pencere olarak
puanlanır, en güçlü destek alınır (entailment > neutral > contradiction; eşitlikte yüksek entailment olasılığı).
Tezde yöntem bölümünde belirtilecek ve A/B karşılaştırma tablosu eke konacak. Gold-480 sonuçlarıyla
karşılaştırmalarda bu farkın not edilmesi gerekir.

## K-018 — RAGBench tıp: sistem çalıştırma kararları (2026-10-14)
- K2: belge bazlı pencereleme (K-017) + dondurulmuş soft_prob_avg birleştirme kuralı (`scripts/116_ragbench_run_k2_windowed.py`).
  Atomlar: dondurulmuş Gemma-4 QLoRA atomlaştırıcı (`scripts/generate_gold480_gemma_atoms.py`, girdi RAGBench iddiaları).
- K1: dondurulmuş haliyle, tam bağlamla (512 token, kesilme olduğu gibi). Kesilen satır sayısı raporlanacak;
  K1 sonuçları kesilen ve kesilmeyen satırlar için ayrı ayrı verilecek (araştırmacı kararı).
- Hibrit: AP6 v1'in dondurulmuş kuralları. P0 = K1=K2 ise ortak karar; farklıysa V4 hakem (Llama-3.3-70B,
  OpenRouter); K2 yoksa K1. PA = P0 + uzlaşma etiketi partially_supported/contradicted olan satırlarda kör Gemma-26B.
  Dış API çağrıları (OpenRouter) araştırmacı tarafından onaylandı; gönderilen veri kamuya açık RAGBench metinlerinin çevirisidir.
- Puanlama: ikili (destekleniyor / desteklenmiyor), gümüş etiketlere göre; desteklenmeyen sınıfı için F1, yanlış alarm, doğruluk.

## K-019 — Çeviri etkisi kontrolü: İngilizce ve Türkçe (2026-10-15)
Amaç: düşük sistem başarısının çeviriden kaynaklanıp kaynaklanmadığını ayırmak (araştırmacı onayı).
Kurulum (iki dilde aynı): dondurulmuş K2 NLI modeli, aynı 809 cümle, aynı gümüş etiketler, cümle hipotez olarak
(atomlaştırıcı yok; Türkçe eğitimli olduğu için İngilizce atomlar karşılaştırılabilir olmazdı), belge bazlı pencereleme.
Script: `scripts/118_ragbench_en_tr_nli_compare.py`; çıktı `build/en_tr_nli_compare.json`.
Sonuç: İngilizce F1 0,285 / AUROC 0,656; Türkçe F1 0,301 / AUROC 0,681; ikili kararlar 638/809 cümlede aynı.
Saf taban çizgisi ("hepsi desteklenmiyor") F1 0,220.
Yorum: çeviri performansı düşürmüyor; düşük başarı çeviriden değil, görevin ve/veya gümüş etiketlerin zorluğundan.
Bağlam: RAGBench Tablo 3 (PubMedQA, İngilizce, tüm test bölümü) AUROC — ince ayarlı DeBERTa 0,80, TruLens 0,62,
RAGAS 0,54, GPT-3.5 0,51. Alt küme farklı olduğundan doğrudan karşılaştırma değildir.
Güven aralıkları (`scripts/119_ragbench_en_tr_bootstrap.py`, `build/en_tr_bootstrap.json`): eşleştirilmiş küme bootstrap'i,
74 soru kümesi, 10.000 yeniden örnekleme, seed 42, %95 yüzdelik aralık.
- İngilizce: F1 0,285 [0,189; 0,371], AUROC 0,656 [0,561; 0,737]
- Türkçe: F1 0,301 [0,211; 0,385], AUROC 0,681 [0,625; 0,735]
- Fark (TR−EN): F1 +0,016 [−0,030; +0,069], AUROC +0,025 [−0,038; +0,097]; her iki aralık da 0'ı içeriyor.
- McNemar (cümle düzeyi, destekleyici): yalnız EN'nin desteklenmiyor dediği 83, yalnız TR'nin 88 cümle, p = 0,76.
Sonuç: iki dil arasında istatistiksel olarak anlamlı fark yok; çeviri performansı düşürmüyor.

## K-020 — RAGBench tıp: sistem sonuçları (2026-10-16)
Script: `scripts/120_ragbench_systems_results.py`; çıktılar `build/systems_results.json`,
`build/predictions/system_predictions.jsonl`. Hibrit kuralları AP6 v1'den değiştirilmeden alındı (K-018).
Girdi tamlığı: K1 809/809 (248 satırda bağlam kesildi), K2 808/809 (1 atomlaştırıcı hatası, o satırda K1 kullanıldı),
V4 hakem 458/458 (ayrıştırma hatası yok), Gemma-26B 809/809 (ağ kesintisi ve ayrıştırma hataları yeniden denenerek tamamlandı).
Yönlendirme: 350 uzlaşma, 458 hakem (LLM çağrı oranı %56,6), 1 K2 yok; PA'da 67 satır Gemma'ya yönlendirildi.
Puanlama: ikili, desteklenmeyen sınıfı; %95 aralıklar 74 soru üzerinden küme bootstrap'i (10.000, seed 42).
Saf taban ("hepsi desteklenmiyor") F1 0,220.

| Sistem | n | F1 [%95 GA] | Kesinlik | Duyarlılık | Yanlış alarm | Doğruluk |
|---|---|---|---|---|---|---|
| K1 (tümü) | 809 | 0,243 [0,171; 0,311] | 0,147 | 0,690 | 0,563 | 0,469 |
| K1, kesilmeyen | 561 | 0,296 [0,207; 0,377] | 0,191 | 0,659 | 0,520 | 0,508 |
| K1, kesilen | 248 | 0,125 [0,049; 0,220] | 0,067 | 0,917 | 0,648 | 0,379 |
| K2 (pencereli) | 808 | 0,295 [0,202; 0,379] | 0,195 | 0,600 | 0,349 | 0,645 |
| Hibrit P0 | 809 | 0,319 [0,224; 0,406] | 0,208 | 0,680 | 0,365 | 0,640 |
| Hibrit PA | 809 | 0,327 [0,235; 0,411] | 0,221 | 0,630 | 0,313 | 0,680 |
| Gemma-26B sıfır atış | 809 | 0,363 [0,264; 0,448] | 0,252 | 0,650 | 0,272 | 0,718 |

Gözlem: sıralama AP6 v1 ile aynı yönde (K1 < K2 < P0 ≤ PA < Gemma), ancak güven aralıkları geniş ve örtüşüyor.
Tüm sistemlerde kesinlik düşük (0,15–0,25). K1'in kesilen bağlamlardaki F1'i saf tabanın altında.
Yorum ve tezdeki sunuş henüz araştırmacıyla karara bağlanmadı.

## K-021 — Hukuk alanı: ClaimRAG-LAW (2026-10-16)
RAGBench-CUAD incelendi ve elendi: tek belge olarak sözleşmenin tamamı (ortalama 6.250, en çok 34.000 kelime),
tek üretici model, desteklenmeyen oranı %4,5 ve bu cümleler 510 maddenin yalnızca 38'inde. Rastgele kesit
çevrilemeyecek kadar uzun; kısa sözleşmelerle sınırlamak ise çok az pozitif bırakıyor.
PARCEL (Demir vd., 2026) elendi: sentetik bozma iddiaları, insan doğrulaması yok, lisans yok.
Karar (araştırmacı, 2026-10-16): ClaimRAG-LAW (Das, Abualhaija ve Bianculli, 2026; SNTSVV/ClaimRAG-LAW, CC BY 4.0),
GDPR (İngilizce) ve Lüksemburg Medeni Kanunu (Fransızca) bölümlerinin ikisi de.
Veri: GPT-4'ün kanun maddesine dayalı yanıtlarından çıkarılmış özne–yüklem–nesne iddiaları; tek hukuk uzmanı
tarafından Entailment / Neutral / Contradiction olarak etiketlenmiş (insan etiketi; anotatörler arası uyum yok).
Yalnızca *-CLAIM-LAW.json dosyaları kullanılır (RAG dosyalarıyla soru numaraları eşleşmiyor).
Ayıklama (`scripts/130_claimrag_prepare_sources.py`):
- Uzmanın Correct dediği ve NLI etiketi verdiği iddialar tutulur; boş etiket ve "Doesn't Make Sense" atılır (makaledeki gibi).
- Kanıt metni yayında boş olan 6 soru çıkarılır (GDPR-Q025, Q034, Q060, Q066; CIVIL-Q092, Q095): etiketler kontrol edilemiyor.
- İkili puanlama: Entailment → destekleniyor; Neutral ve Contradiction → desteklenmiyor.
Sonuç kesit: GDPR 61 soru / 426 iddia (157 desteklenmiyor), Medeni Kanun 87 soru / 361 iddia (89 desteklenmiyor);
toplam 148 soru, 787 iddia, %31 desteklenmiyor; 51 farklı kanıt metni.
Çeviri (araştırmacı kararı: kontrol pratik ve az turlu olacak):
- Çevrilen: kanıt metni (her biri bir kez), soru, iddia (üçlü tek bir Türkçe cümleye dönüştürülür). GPT-4 yanıt
  metinleri çevrilmez (sistemler görmez), kaynak dilde üstveri olarak kalır.
- Dört parti: GDPR ilk parti (üslup), GDPR kalanı, Medeni Kanun iki parti. Kontrol dosyası soru başına tek satır,
  otomatik denetimler (madde/sayı eşleşmesi, iddia eksikliği, terim tutarlılığı) önceden işaretlenmiş.
- Tıptaki çeviri kuralları geçerli; GDPR terimleri KVKK karşılıklarıyla tutulur.
Çeviri kontrolü (araştırmacı, 2026-10-16): dört partinin tamamı uygun bulundu, düzeltme istenmedi.

## K-022 — Hukuk kesiti: veri seti ve sistem çalıştırma (2026-10-16)
Veri seti (`scripts/132_claimrag_build_dataset.py`, `data/claimrag_law/build/`): 148 soru, 787 iddia, 51 bağlam;
gold_label: supported 541, unverifiable 215, contradicted 31; ikili: 246 desteklenmiyor (%31,3).
Etiket eşlemesi: Entailment → supported, Neutral → unverifiable, Contradiction → contradicted
(gold_label gerçek bir 3 sınıflı etikettir; partially_supported yoktur).
Bağlam uzunluğu: 51 bağlamdan yalnızca ikisi mDeBERTa sınırını aşıyor (GDPR-C15 1.427 token, GDPR-C21 997 token;
116 iddia). K-017'nin aynısı: bu bağlamlar paragraf sınırlarından, sırası korunarak, en çok 400 token'lık
pencerelere bölünür (C15: 5, C21: 4 pencere); diğer bağlamlar tek pencere. K1 dondurulmuş haliyle tam bağlamı
görür (116 satırda kesilme), sonuçları kesilen/kesilmeyen ayrı raporlanır (K-018 ile aynı).
Sistemler K-018'deki dondurulmuş kurallarla çalıştırılır; scriptler 116, 117, 120 veri seti yolunu parametre
olarak alacak biçimde genişletildi (varsayılan tıp; tıp sonuç tablosu değişmeden yeniden üretildi).

## K-023 — Hukuk kesiti: sistem sonuçları (2026-10-16)
Çıktılar: `data/claimrag_law/build/systems_results.json`, `predictions/system_predictions.jsonl` (script 120, --build).
Girdi tamlığı: K1 787/787 (116 kesilme), atomlaştırıcı 787/787 (hata yok; bilgisayar kapanması sonrası kaldığı yerden
sürdürüldü, yarım satır yok), K2 787/787 (1.184 çift, kesilme yok), V4 hakem 382/382 (ayrıştırma hatası yok),
Gemma-26B 787/787. Yönlendirme: 405 uzlaşma, 382 hakem (LLM çağrı oranı %48,5); PA'da 39 satır Gemma'ya.
Saf taban F1 0,476 (desteklenmeyen oranı %31,3; tıpta 0,220).

| Sistem | n | F1 [%95 GA] | Kesinlik | Duyarlılık | Yanlış alarm | Doğruluk |
|---|---|---|---|---|---|---|
| K1 (tümü) | 787 | 0,585 [0,523; 0,638] | 0,456 | 0,817 | 0,444 | 0,638 |
| K1, kesilmeyen | 671 | 0,589 [0,518; 0,648] | 0,462 | 0,813 | 0,410 | 0,657 |
| K1, kesilen | 116 | 0,567 [0,377; 0,682] | 0,429 | 0,837 | 0,657 | 0,526 |
| K2 (pencereli) | 787 | 0,565 [0,498; 0,624] | 0,460 | 0,732 | 0,390 | 0,648 |
| Hibrit P0 | 787 | 0,628 [0,565; 0,680] | 0,505 | 0,829 | 0,370 | 0,693 |
| Hibrit PA | 787 | 0,633 [0,570; 0,685] | 0,518 | 0,813 | 0,344 | 0,705 |
| Gemma-26B sıfır atış | 787 | 0,643 [0,577; 0,697] | 0,538 | 0,797 | 0,310 | 0,723 |

Gözlem: sıralama tıpla aynı (K2 ≤ K1 < P0 ≤ PA < Gemma); hibrit her iki küçük modeli geçiyor ve Gemma'ya
0,01 F1 içinde yaklaşıyor; aralıklar örtüşüyor. Mutlak değerler desteklenmeyen oranı farklı olduğundan tıpla doğrudan
karşılaştırılmaz (saf tabana göre fark verilmeli). Yorum ve tezdeki sunuş araştırmacıyla birlikte yapılacak.

## K-024 — Finans alanı: FinDVer (2026-10-16)
Taranan adaylar ve eleme gerekçeleri:
- RAGBench FinQA / TAT-QA: desteklenmeyen cümle oranı %2,6 / %1,6 — ölçüm için pozitif yok.
- FinHalu (FinGround, 2026): ideal (LLM yanıtları, iddia düzeyi 3 sınıf, 3 uzman κ = 0,83) ama veri yayımlanmamış.
- HaluBench-FinanceBench (Patronus): bozma ile üretilmiş kısa (çoğu sayısal) yanıtlar, cevap düzeyi, CC BY-NC.
- PHANTOM (NeurIPS 2025 D&B): yanıt çiftleri, halüsinasyonlar LLM ile eklenmiş; insan doğrulaması teyit edilemedi.
Karar (araştırmacı, 2026-10-16): FinDVer (Zhao vd., EMNLP 2024; yilunzhao/FinDVer, MIT). 10-K/10-Q raporları hakkında
uzmanların yazdığı iddialar; etiket entailed / refuted (uzman, anotatörler arası uyum %90,3); kanıt paragrafları işaretli.
Not: iddialar LLM yanıtı değil uzman yazımıdır; tezde "üç alan, üç etiket kaynağı" (GPT-4 gümüş / tek uzman / çift uzman)
olarak sunulacak.
Kesit (`scripts/140_findver_prepare_sources.py`; araştırmacı seçimi C):
- test bölümü, FDV-IE ve FDV-MATH alt kümeleri (FDV-KNOW dış bilgi gerektirdiği için bağlama dayalı tanıma uymaz);
- raporlar seed 42 ile karıştırılıp bütün olarak eklendi (≥ 160 iddia: 46 rapor, 166 iddia);
- kanıtı 600 kelimeyi aşan 41 iddia çeviri maliyeti nedeniyle çıkarıldı (yöntemde belirtilecek; uzun kanıt aleyhine seçim yanlılığı).
Sonuç: 40 rapor, 125 iddia (IE 55, MATH 70); 70 refuted (%56) / 55 entailed; 266 kanıt öğesi (191 paragraf, 75 tablo).
Bağlam = uzmanın işaretlediği kanıt öğeleri (makaledeki oracle ayarı); K2 için her öğe ayrı pencere (K-017 ile aynı mantık).
İkili puanlama: entailed → destekleniyor, refuted → desteklenmiyor (gold_label: supported / contradicted).
Çeviri: hukuktaki gibi dört parti, tek sayfa kontrol, otomatik denetim. Tablolarda başlık ve satır adları çevrilir,
sayılar ve tablo yapısı aynen korunur.
Çeviri kontrolü (araştırmacı, 2026-10-16): dört partinin tamamı uygun bulundu, düzeltme istenmedi.

## K-025 — Finans kesiti: veri seti ve sistem çalıştırma (2026-10-16)
Veri seti (`scripts/142_findver_build_dataset.py`, `data/findver/build/`): 40 rapor, 125 iddia (IE 55, MATH 70),
266 kanıt öğesi; ikili: 70 desteklenmiyor (%56) / 55 destekleniyor; gold_label: supported / contradicted.
FinDVer'de soru yoktur: `question` alanı boş bırakıldı (K1, atomlaştırıcı, hakem ve LLM çalıştırıcısı boş soruyu kabul ediyor).
Tablolar çeviride hücre eşlemesiyle aktarıldı (`scripts/141_findver_translation_review.py`): sayılar ve yapı kaynakla bayt düzeyinde aynı.
Bağlam = uzmanın işaretlediği kanıt öğeleri, rapordaki sırayla. Medyan 470 token, en çok 1.150; 57 iddiada 512'yi aşıyor.
Pencereleme (K-017'nin aynı mantığı): her kanıt öğesi bir pencere; 450 token'a sığmayan 19 öğe satır (gerekirse cümle) sınırından
en çok 400 token'lık ardışık pencerelere bölündü. Sınırlılık: bölünen tablolarda ikinci pencere tablo başlığını görmez.
K1 dondurulmuş haliyle tam bağlamı görür; 50 satırda kesilme (K1 tokenizer'ı ile), ayrı raporlanacak.
Sistemler K-018'deki dondurulmuş kurallarla, hukuktaki parametreli scriptlerle (116, 117, 120) çalıştırılır.

## K-026 — Finans kesiti: sistem sonuçları (2026-10-16)
Çıktılar: `data/findver/build/systems_results.json`, `predictions/system_predictions.jsonl`.
Girdi tamlığı: K1 125/125 (50 kesilme), atomlaştırıcı 125/125, K2 125/125 (565 çift, kesilme yok),
V4 hakem 79/79 (1 ayrıştırma yedeği), Gemma-26B 125/125 (1 satır yeniden denendi). Yönlendirme: 46 uzlaşma, 79 hakem
(LLM çağrı oranı %63,2); PA'da 29 satır Gemma'ya. Kümeler: 40 rapor (bootstrap rapor üzerinden).
Desteklenmeyen oranı %56 olduğundan saf taban F1 0,718 ve çoğunluk sınıfı doğruluğu 0,560'tır; bu kesitte F1 yanıltıcıdır,
doğruluk ve yanlış alarm birlikte okunmalıdır.

| Sistem | n | F1 [%95 GA] | Kesinlik | Duyarlılık | Yanlış alarm | Doğruluk |
|---|---|---|---|---|---|---|
| K1 (tümü) | 125 | 0,692 [0,605; 0,772] | 0,556 | 0,914 | 0,927 | 0,544 |
| K1, kesilmeyen | 75 | 0,635 [0,495; 0,756] | 0,500 | 0,872 | 0,944 | 0,480 |
| K1, kesilen | 50 | 0,769 [0,667; 0,861] | 0,638 | 0,968 | 0,895 | 0,640 |
| K2 (pencereli) | 125 | 0,592 [0,486; 0,683] | 0,549 | 0,643 | 0,673 | 0,504 |
| Hibrit P0 | 125 | 0,713 [0,626; 0,787] | 0,644 | 0,800 | 0,564 | 0,640 |
| Hibrit PA | 125 | 0,724 [0,638; 0,795] | 0,671 | 0,786 | 0,491 | 0,664 |
| Gemma-26B sıfır atış | 125 | 0,752 [0,683; 0,812] | 0,678 | 0,843 | 0,509 | 0,688 |

Alt kümelere göre doğruluk (çoğunluk sınıfı IE 0,564, MATH 0,557):
- IE (55): K1 0,545; K2 0,618; P0 0,673; PA 0,745; Gemma 0,727.
- MATH (70): K1 0,543; K2 0,414; P0 0,614; PA 0,600; Gemma 0,657.
Gözlem: K1 bu kesitte neredeyse her iddiaya "desteklenmiyor" diyor (yanlış alarm 0,93) ve çoğunluk sınıfı düzeyinde kalıyor;
K2 hesap gerektiren MATH iddialarında çoğunluk sınıfının altında. Hibrit, hakem sayesinde iki küçük modeli belirgin biçimde geçiyor;
IE'de PA Gemma düzeyinde. Sayısal akıl yürütme NLI tabanlı sistemlerin açık zayıflığı. K1'in kesilen satırlarda daha iyi görünmesi,
K1'in hep "desteklenmiyor" demesinin ve bu satırlarda çürütülmüş oranının daha yüksek olmasının sonucudur; gerçek bir üstünlük değildir.
(Doğrulama: kesilen satırlarda desteklenmeyen oranı %62, kesilmeyenlerde %52.)

## K-027 — Sistemler arası eşleştirilmiş fark testleri (2026-10-16)
Script: `scripts/150_paired_system_tests.py`; çıktı `docs/ap6v2_paired_tests.json`. Planlı dört karşılaştırma (P0−K1, P0−K2, PA−P0,
Gemma−PA), her alanda F1 ve doğruluk farkı; eşleştirilmiş küme bootstrap'i (10.000, seed 42), iki yönlü bootstrap p,
alan × ölçüt içinde Holm düzeltmesi; destekleyici exact McNemar.
Holm düzeltmeli p < 0,05 olan farklar (doğruluk / F1):
- Tıp: P0 > K1 (doğruluk +0,172, F1 +0,075); PA > P0 (doğruluk +0,040). P0−K2 ve Gemma−PA anlamlı değil
  (Gemma−PA doğruluk +0,038, p_holm 0,078; McNemar düzeltmesiz p 0,02).
- Hukuk: P0 > K1 (doğruluk +0,055; F1 +0,043, p_holm 0,067); P0 > K2 (doğruluk +0,044, F1 +0,062); PA > P0 (doğruluk +0,013).
  Gemma−PA anlamlı değil (doğruluk +0,018, p_holm 0,37).
- Finans: P0 > K2 (doğruluk +0,136, F1 +0,121). P0−K1 (doğruluk +0,096, p_holm 0,17), PA−P0 ve Gemma−PA anlamlı değil (125 iddia).
Özet: hibrit her alanda küçük modellerden en az birini anlamlı biçimde geçiyor; Gemma-26B ile PA arasındaki fark hiçbir alanda
Holm düzeltmesinden sonra anlamlı değil. PA kuralının P0'a katkısı küçük ama tıp ve hukukta tutarlı.

## K-028 — Hata analizi: Hibrit PA yanlış alarmları (2026-10-16)
Örneklem: Hibrit PA'nın yanlış alarmları (gold supported, PA unsupported), alan başına 10, seed 42
(`scripts/151_error_analysis_sample.py`; yanlış alarm sayıları: tıp 222, hukuk 186, finans 27).
Kategoriler okumadan önce sabitlendi: A yeniden ifade/basit çıkarım, B dağılmış ya da bölünmüş bilgi, C sayısal hesap
(A–C sistem hatası); D etiket esnek (bağlam dışı genel bilgi), E etiket şüpheli (D–E etiket kaynaklı); F içeriksiz cümle;
G çeviri kaynaklı. Kodlama (Claude, bağlam okunarak): `docs/ap6v2_error_coding.jsonl`.
Sonuç (30): A 9, D 6, B 5, C 4, F 4, E 2, G 0.
- Tıp: F 4, A 3, D 2, E 1 — hataların yarısından fazlası etiket ya da içeriksiz cümle kaynaklı.
- Hukuk: A 5, D 4, E 1 — sistem hataları yeniden ifadede; etiket tarafında madde numarası gibi parçada olmayan bilgi.
- Finans: B 5, C 4, A 1 — tamamı sistem hatası: birden çok kanıt öğesine dağılan birleşik iddialar ve hesap.
Çeviri kaynaklı hata bulunmadı.
Tüm yanlış alarmlar üzerinde iki ek ölçüm:
1. Yanlış alarmların çoğu hakem yolundan geliyor (tıp 177/222, hukuk 141/186, finans 13/27). Gold'un destekli dediği
   K1/K2 anlaşmazlıklarında hakem yalnızca yaklaşık yarısında "supported" diyor (tıp 223/400, hukuk 134/275, finans 23/36):
   hakem bu verilerde katı. Tıpta hakem yolundaki 177 yanlış alarmın 97'sinde K2 doğru biçimde "supported" demişti.
   Dondurulmuş kurallar değiştirilmedi; bu yalnızca bulgu ve gelecek çalışma notudur (test verisinde ayar yapılmaz).
2. Tıpta iki noktayla biten içeriksiz giriş cümleleri: 86 cümle, GPT-4 bunların 82'sini destekli saymış; PA yanlış
   alarmlarının 67/222'si (%30) bu cümleler. Önceden kararlaştırıldığı gibi tıp sonuçları bu cümleler hariç de raporlanır
   (n = 723, desteklenmeyen 96, saf taban F1 0,234): F1 / doğruluk — K1 0,273 / 0,506; K2 0,305 / 0,628; P0 0,379 / 0,696;
   PA 0,396 / 0,739; Gemma 0,441 / 0,779. Sıralama değişmiyor; hibrit ile K2 arasındaki fark açılıyor.
Sınırlılık: kodlamayı tek kişi (Claude) yaptı; 30 örnek yön göstericidir, oran tahmini değildir.
Araştırmacı kodlamanın tamamını gözden geçirip onayladı (2026-10-17; `docs/ap6v2_hata_kodlama_kontrol.xlsx`).

## K-029 — GPT-4.1-mini karşılaştırması yinelenmedi (2026-10-17)
Pilotta sekiz örnekli GPT-4.1-mini hibrit sistemden anlamlı biçimde iyiydi. v2'de yalnızca örneksiz Gemma-4-26B çalıştırıldı.
OpenRouter bakiyesi (≈ 0,72 $) üç kesit için gereken ≈ 1,7–2 $'a yetmiyor; araştırmacı yeni yükleme yapmamayı seçti (seçenek b).
Gemini (AI Studio ücretsiz katmanı) GPT-4.1-mini'nin yerini tutmayacağı için kullanılmadı.
Tezde geçerlilik tehditlerinde açıkça yazılır: pilotta GPT-4.1-mini (8 örnek) hibritten anlamlı biçimde iyiydi; bütçe nedeniyle
dış veri kümelerinde yinelenmedi. Dergi makalesi aşamasında GPT ve Gemini karşılaştırmaları eklenecek.

## Açık kararlar
- Çeviri sonrası etiket kontrolünün kapsamı
- Sağlık sorularının (MED-01…20) akıbeti; hukuk ve finans
- Soruları kimin yazacağı, soru yazım kuralları
- Kanıt işaretleme yöntemi, çeldirici sayısı ve seçimi, parça sınırları, parça sırası
- Prompt kuralları
- Etiketleme birimi, etiket şeması, çekimser kuralları, anotatör tasarımı, örnekleme, kılavuz
