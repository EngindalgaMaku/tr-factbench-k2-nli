# TR-FactBench 480 Altın Test: Kalan 33 Hatanın Derinlemesine İnceleme Raporu

**Tarih:** 6 Ekim 2026  
**Mimari:** Semantik Yüklem Denetimli Hibrit Sistem (ELECTRA-TR + Gemma-4-2B + mDeBERTa-v3 + Llama-3.3-70B Yüklem Hakemi)  
**Genel Başarım:** **%93.13 (447 / 480 Doğru | Yalnızca 33 Hata)**  
**Teorik Oracle Tavanı:** %93.33 (448 / 480) — **Tavana Uzaklık: Sadece 1 Vaka (%0.21)!**  
- **Meta-Hakem Karar Hataları:** 13 Vaka  
- **Yerel Modellerin Ortak Yanılgıları (Doğrudan Uzlaşma Hataları):** 20 Vaka  

---

## BÖLÜM 1: META-HAKEM KARAR HATALARI (13 VAKA)
*Semantik yüklem kuralı sayesinde hakem hataları 23'ten 13'e inmiştir. Kalan 13 vakanın tam dökümü:*

### [HAKEM-01/13] ID: `tfb_ex_0006` | Alan: `GENERAL`
- **SORU:** Meslek Birliği A Değerlendirme Komitesi neyi inceler? Değerlendirme süreci nasıl yürütülüp sonuçlandırılır?
- **BAĞLAM:** Meslek Birliği A Değerlendirme Komitesi, Meslek Birliği A üyeleri arasındaki veya Meslek Birliği A üyeleri ile müşterileri arasındaki değerleme hizmeti uyuşmazlıklarının çözümüne yardımcı olur. İtiraz edilen değerleme raporlarını, disiplin komitesinin görev alanına girmeyen mesleki şikâyetleri ve kendisine verilen kalite kontrol veya denetim görevlerini inceler. İncelemede raporlar teknik olarak değerlendirilir; masa başı çalışma yanında gerekli görülürse yerinde saha araştırması yapılır, resmi kurum bilgi ve belgeleri ile emsal ve çevre bilgileri kontrol edilir. Komite sonucunu bir Değerlendirme Dosyasıyla Yönetim Kuruluna sunar; bu dosya yeni bir değerleme raporu değildir ve itiraz edilen raporun yerine geçmez.
- **İDDİA:** Üyeler ile müşteriler arasındaki değerleme uyuşmazlıklarının çözümüne yardımcı olan Meslek Birliği A Değerlendirme Komitesinin bu uyuşmazlıklara ilişkin kararları mahkemeler açısından bağlayıcıdır.
- **ALTIN ETİKET (Doğru Karar):** `partially_supported`
- **HAKEM KARARI (Yanlış Tahmin):** `unverifiable` ❌
- **Bilirkişi Modelleri:** Model A = `partially_supported` | Model B = `unverifiable` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Meslek Birliği A Değerlendirme Komitesinin kararlarının mahkemeler açısından bağlayıcı olduğu' ifadesi, bağlam tarafından doğrulanmamaktadır. Bağlam, komitenin değerleme uyuşmazlıklarının çözümüne yardımcı olduğunu ve bir Değerlendirme Dosyası sunduğunu belirtse de, bu kararların mahkemeler açısından bağlayıcı olduğuna dair bir bilgi içermemektedir."*
- **Ayrıştırılan Atomik Önermeler:** "Üyeler ile müşteriler arasındaki değerleme uyuşmazlıklarının çözümüne yardımcı olan Meslek Birliği A Değerlendirme Komitesinin bu uyuşmazlıklara ilişkin kararları mahkemeler açısından bağlayıcıdır."

---

### [HAKEM-02/13] ID: `tfb_ex_0010` | Alan: `GENERAL`
- **SORU:** Sigorta Fonu A hangi zararları, hangi koşullarda karşılar?
- **BAĞLAM:** Sigorta Fonu A, zorunlu sigorta kapsamındaki belirli durumlarda zarar görenlere tazminat sağlar. Zorunlu sigortanın bulunmaması veya sigortalının tespit edilememesi nedeniyle oluşan bedensel zararlar bu kapsama girebilir. Sigorta şirketinin mali bünye zafiyeti nedeniyle bütün branşlardaki ruhsatlarının iptal edilmesi ya da iflası durumunda şirketin ödemekle yükümlü olduğu maddi ve bedensel zararlar da Fonun kapsamındadır. Buna karşılık manevi zararlar karşılanmaz; bedensel zarar dışındaki maddi zararlar da iflas veya ruhsat iptaliyle ilgili özel durumlar dışında genel olarak kapsam dışındadır.
- **İDDİA:** Sigorta şirketinin iflasında maddi ve bedensel zararları karşılayan Sigorta Fonu A, mahkeme kararıyla hükmedilen manevi zararları da ödeyebilir.
- **ALTIN ETİKET (Doğru Karar):** `partially_supported`
- **HAKEM KARARI (Yanlış Tahmin):** `unverifiable` ❌
- **Bilirkişi Modelleri:** Model A = `partially_supported` | Model B = `unverifiable` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada Sigorta Fonu A'nın mahkeme kararıyla hükmedilen manevi zararları da ödeyebileceği belirtilmektedir, ancak bağlamda manevi zararların karşılanmadığı açıkça belirtilmiştir. İddiada doğru olan Sigorta Fonu A'nın maddi ve bedensel zararları karşıladığı bilgisi bulunmaktadır, ancak manevi zararlar konusunda bağlamla çelişmektedir."*
- **Ayrıştırılan Atomik Önermeler:** "Sigorta şirketinin iflasında maddi ve bedensel zararları karşılayan Sigorta Fonu A, mahkeme kararıyla hükmedilen manevi zararları da ödeyebilir."

---

### [HAKEM-03/13] ID: `tfb_ex_0104` | Alan: `GENERAL`
- **SORU:** Bankalarda uzaktan müşteri ediniminin kapsamı zaman içinde ne yönde genişledi?
- **BAĞLAM:** Bankaların uzaktan kimlik tespiti yoluyla müşteri edinmesine ilişkin düzenleme 1 Mayıs 2021’de yürürlüğe girdi ve başlangıçta T.C. Kimlik Kartına sahip gerçek kişiler ile gerçek kişi tacirlerin uzaktan müşteri olmasına imkân verdi. Daha sonra yapılan değişiklikle tüzel kişilerin de uzaktan müşteri edinimi yoluyla banka müşterisi olabilmesinin önü açıldı. Böylece müşteri ilişkisinin kurulması için her durumda banka şubesine fiziksel olarak gidilmesi zorunlu değildir.
- **İDDİA:** Tüzel kişiler uzaktan müşteri olurken yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `contradicted` | Model B = `partially_supported` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada tüzel kişilerin uzaktan müşteri olabileceği bilgisi bağlam tarafından doğrulanmaktadır, ancak 'yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır' ifadesi bağlamda doğrulanmamaktadır. Bu nedenle, iddianın bir parçası doğrulanırken diğer parçası doğrulanmamaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "Tüzel kişiler uzaktan müşteri olurken" | "yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır"

---

### [HAKEM-04/13] ID: `tfb_ex_0139` | Alan: `GENERAL`
- **SORU:** Bedelli sermaye artırımında rüçhan hakkı ne kadar süre kullanılabilir? Kuponlar alınıp satılabilir mi?
- **BAĞLAM:** Yeni pay alma hakkı, pay sahibine şirketin bedelli sermaye artırımına öncelikli katılma imkânı verir. Rüçhan hakkının kullanım süresi en az 15, en çok 60 gündür. Bu hakka ilişkin kuponlar Borsa İstanbul Rüçhan Hakkı Kupon Pazarı’nda alınıp satılabilir.
- **İDDİA:** Rüçhan hakkının kullanım süresi en az 60 gündür. Kuponlar yalnız tezgâhüstü piyasada işlem görür.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `partially_supported` | Model B = `unverifiable` | Tercih = `Model A`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Rüçhan hakkının kullanım süresi en az 60 gündür' ifadesi bağlam tarafından doğrudan çelişmekte olup, 'en az 15, en çok 60 gündür' ifadesi ile uyumsuzdur. Ayrıca, 'Kuponlar yalnız tezgâhüstü piyasada işlem görür' ifadesi bağlamda yer almayan bir bilgi içermektedir ve bağlam 'Borsa İstanbul Rüçhan Hakkı Kupon Pazarı’nda alınıp satılabilir' demekte olup, bu iki eylem arasında doğrudan bir çelişki veya doğrulama bulunmamaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "Rüçhan hakkının kullanım süresi en az 60 gündür" | "Kuponlar yalnız tezgâhüstü piyasada işlem görür"

---

### [HAKEM-05/13] ID: `tfb_ex_0165` | Alan: `GENERAL`
- **SORU:** Özel Şirket A hakkındaki rekabet incelemesinde hangi sorunlar ele alındı? Süreç nasıl sonuçlandı?
- **BAĞLAM:** Düzenleyici Kurum A, Özel Şirket A hakkında internet satışlarının kısıtlanması, alım yükümlülükleri, ürünlerin birlikte alınmasının zorunlu tutulması ve indirim uygulamaları gibi davranışları inceledi. İnternet satışlarının kısıtlanmasının Kanun A'nın 4. maddesini ihlal ettiğine karar verilerek Özel Şirket A'ya idari para cezası uygulandı. Dışlayıcı davranışlara ilişkin rekabet endişelerini gidermek amacıyla Özel Şirket A'nın sunduğu taahhütler kabul edilerek bağlayıcı hale getirildi. Taahhütlerin uygulanmasına ilişkin bilgilerin beş yıl boyunca yıllık olarak Düzenleyici Kurum A'ya sunulması öngörüldü.
- **İDDİA:** Düzenleyici Kurum A, Özel Şirket A'nın internet satışlarını kısıtlamasının Kanun A'nın 4. maddesini ihlal ettiğine karar vererek şirkete idari para cezası uyguladı.
- **ALTIN ETİKET (Doğru Karar):** `supported`
- **HAKEM KARARI (Yanlış Tahmin):** `unverifiable` ❌
- **Bilirkişi Modelleri:** Model A = `supported` | Model B = `unverifiable` | Tercih = `Neither`
- **Hakemin Gerekçesi (CoT Reasoning):** *"Parse failure."*
- **Ayrıştırılan Atomik Önermeler:** "Düzenleyici Kurum A, Özel Şirket A'nın internet satışlarını kısıtlamasının Kanun A'nın 4. maddesini ihlal ettiğine karar vererek şirkete idari para cezası uyguladı."

---

### [HAKEM-06/13] ID: `tfb_ex_0173` | Alan: `GENERAL`
- **SORU:** İnternet aboneliği fesih süreci nasıl işler?
- **BAĞLAM:** İnternet aboneliğinin feshi için abone, işletmeciye yazılı başvuruda bulunabilir, teyit edilmiş faks gönderebilir veya güvenli elektronik imza ile imzalanmış bir metin iletebilir. İşletmeci fesih talebinin kendisine ulaştığını en geç yirmi dört saat içinde aboneye bildirir ve talebin bildirilmesinden itibaren yirmi dört saat içinde ücretlendirmeyi durdurur. Abonelik en geç yedi gün içinde sona erdirilir ve fesih sonucu aboneye posta, elektronik posta, kısa mesaj veya arama yoluyla bildirilir. Abonenin ölümü halinde hattın kapatılması için ölüm belgesi yeterlidir.
- **İDDİA:** İnternet aboneliği yazılı başvuru, teyit edilmiş faks veya güvenli elektronik imzalı metinle feshedilebilir; işletmeci feshi en geç yedi gün içinde tamamlar.
- **ALTIN ETİKET (Doğru Karar):** `supported`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `supported` | Model B = `partially_supported` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddianın ilk önermesi 'İnternet aboneliği yazılı başvuru, teyit edilmiş faks veya güvenli elektronik imzalı metinle feshedilebilir' bağlam tarafından doğrulanmaktadır. İkinci önerme 'İşletmeci feshi en geç yedi gün içinde tamamlar' da bağlamda bulunan 'Abonelik en geç yedi gün içinde sona erdirilir' ifadesiyle uyumlu görünse de, tamamlama eyleminin işletmeci tarafından yapılacağına dair bağlamda açık bir bilgi bulunmamaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "İnternet aboneliği yazılı başvuru, teyit edilmiş faks veya güvenli elektronik imzalı metinle feshedilebilir" | "İşletmeci feshi en geç yedi gün içinde tamamlar"

---

### [HAKEM-07/13] ID: `tfb_ex_0184` | Alan: `GENERAL`
- **SORU:** 2025 ek ücret düzenlemesi marka işlemlerini nasıl etkiledi?
- **BAĞLAM:** Kamu Kurumu A'nın 2025 ücret tarifesinde yapılan değişiklik, marka başvuruları, yenileme işlemleri ve iptal taleplerine ilişkin bazı ücretleri yeniden düzenledi. Marka başvurularında Nis Sınıflandırmasının 35. sınıfındaki belirli hizmetler bakımından seçilen mal sınıflarının sayısına göre ek ücret alınması öngörüldü. Koruma süresi sona ermiş markaların yenileme ücreti sınıf sayısına göre belirlendi. Marka iptal talebinde alınan tutar, iptal ücreti ve emanet hesapta tutulan bedel olarak ayrıldı. Nihai karara göre emanet tutarı, talebin tamamen reddinde marka sahibine, tamamen kabulünde talep sahibine ödenir; kısmi kabulde ise Kamu Kurumu A'ya gelir kaydedilir.
- **İDDİA:** Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur ve nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `partially_supported` | Model B = `contradicted` | Tercih = `Model A`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur' ifadesi bağlam tarafından doğrulanmaktadır. Ancak, 'nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir' ifadesi bağlamda doğrulanmamaktadır, bu eylem/hüküm bağlamda yer almamaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur" | "nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir"

---

### [HAKEM-08/13] ID: `tfb_ex_0224` | Alan: `GENERAL`
- **SORU:** Bireysel başvuru formu nasıl hazırlanıp imzalanır?
- **BAĞLAM:** Bireysel başvuru formunun elektronik örneği PDF biçiminde bilgisayara kaydedilebilir. Form bilgisayarda doldurulup kaydedilebileceği gibi çıktısı alınarak el yazısıyla da doldurulabilir. Bilgisayarda doldurulan formun başvuru için bir çıktısı alınmalı ve imzalanmalıdır. Formun elektronik ortamda doldurulmuş olması, imzalı örneğin hazırlanması gereğini tek başına ortadan kaldırmaz.
- **İDDİA:** Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir; elektronik dosya sunulmadığında başvuru işleme alınmaz.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `contradicted` | Model B = `supported` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir' ifadesi bağlam tarafından kısmen doğrulanmaktadır, çünkü formun bilgisayarda doldurulup imzalı bir çıktısı alınabileceği belirtilmektedir. Ancak, 'Elektronik dosya sunulmadığında başvuru işleme alınmaz' ifadesi bağlamda açıkça doğrulanmamaktadır, bu nedenle bu iddia kısmen desteklenmektedir."*
- **Ayrıştırılan Atomik Önermeler:** "Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir" | "Elektronik dosya sunulmadığında başvuru işleme alınmaz"

---

### [HAKEM-09/13] ID: `tfb_ex_0239` | Alan: `GENERAL`
- **SORU:** Yirmi yıllık kıdem yoluyla arabulucu siciline başvuru nasıl yapılır? Hangi adaylardan ek sağlık belgesi istenir?
- **BAĞLAM:** Mesleğinde yirmi yıl kıdeme sahip olup gerekli arabuluculuk eğitimini tamamlayan hukuk fakültesi mezunlarının sicile kayıt başvurularının 25 Kasım 2024 tarihinden itibaren yalnız Sistem A üzerinden alınacağı duyurulmuştur. Başvuru tarihinde fiilen avukatlık mesleğini veya bir kamu görevini yürütmeyen adaylardan, arabuluculuk yapmalarına ruhen ve bedenen engel bir durum bulunmadığını gösteren sağlık kuruluşu belgesi istenmektedir. Başvuru usulü, belirli kıdem yolundan sicile kayıt isteyen adaylar için duyurulan özel başvuru sürecidir.
- **İDDİA:** 25 Kasım 2024'ten sonra yirmi yıllık kıdem yolunda fiziki başvuru kabul edilir. Sistem A üzerinden başvuru tercih meselesidir.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `supported` | Model B = `partially_supported` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada yer alan '25 Kasım 2024'ten sonra yirmi yıllık kıdem yolunda fiziki başvuru kabul edilir' ifadesi bağlam tarafından doğrudan çelişmekte olup, 'Sistem A üzerinden başvuru tercih meselesidir' ifadesi ise bağlamda yer alan 'Sistem A üzerinden alınacağı' bilgisine kısmen destek vermektedir. Ancak, bağlamda 'fiziki başvuru' konusuna dair bir bilgi bulunmamaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "25 Kasım 2024'ten sonra yirmi yıllık kıdem yolunda fiziki başvuru kabul edilir" | "Sistem A üzerinden başvuru tercih meselesidir"

---

### [HAKEM-10/13] ID: `tfb_ex_0272` | Alan: `GENERAL`
- **SORU:** Ticari Hakem Heyeti A’nda yetkili yer nasıl belirlenir? Karara itiraz süresi nedir?
- **BAĞLAM:** Ticari Hakem Heyeti A, sebze ve meyve ticaretinde üreticiler ile meslek mensupları arasındaki ya da toptancı hali ve pazar yeri işleyişinden doğan belirli uyuşmazlıkları ele alır. Başvuru, uyuşmazlığa ilişkin belgelerin eklendiği dilekçeyle ticaret il müdürlüğüne veya e-Devlet üzerinden yapılabilir. Mal alım satımından doğan uyuşmazlıklarda alıcı ya da satıcının faaliyet gösterdiği yerdeki heyet; diğer uyuşmazlıklarda başvurucunun faaliyet gösterdiği veya ikamet ettiği yerdeki heyet yetkilidir. Heyet kararına karşı on beş gün içinde heyetin bulunduğu yerdeki asliye ticaret mahkemesine itiraz edilebilir.
- **İDDİA:** e-Devlet başvurusunda faaliyet yeri doğrulanınca yetkili heyet sistem tarafından seçilir. Başvurucu bu seçimi çevrim içi değiştirebilir.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `unverifiable` | Model B = `partially_supported` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'e-Devlet başvurusunda faaliyet yeri doğrulanınca yetkili heyet sistem tarafından seçilir' ifadesi bağlam tarafından kısmen desteklenmektedir, çünkü bağlamda e-Devlet üzerinden başvuru yapılabilir ve yetkili heyet belirlenir. Ancak, 'başvurucu bu seçimi çevrim içi değiştirebilir' ifadesi bağlamda doğrulanmamaktadır, çünkü bağlamda böyle bir eylem veya olanaktan bahsedilmez. Bu nedenle, iddianın bir parçası desteklenirken diğer parçası doğrulanmamaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "e-Devlet başvurusunda faaliyet yeri doğrulanınca yetkili heyet sistem tarafından seçilir." | "Başvurucu bu seçimi çevrim içi değiştirebilir."

---

### [HAKEM-11/13] ID: `tfb_ex_0307` | Alan: `GENERAL`
- **SORU:** Boşanma hangi tarihte hukuken sonuç doğurur? Karar aile kütüğüne nasıl işlenir?
- **BAĞLAM:** Boşanma, mahkeme kararının kesinleşmesiyle evlilik birliğini sona erdirir ve boşanma tarihi kararın kesinleştiği tarihtir. Mahkeme yazı işleri müdürünün iki örnek olarak gönderdiği boşanma kararı, ilgili ilçe nüfus müdürlüğünce aile kütüğüne işlenir. Türk vatandaşı kadın için kanunda öngörülen 300 günlük bekleme süresi de kararın kesinleştiği tarihten başlar.
- **İDDİA:** Boşanma karar verildiği gün evlilik birliğini sona erdirir. Aile kütüğüne boşanma kaydı işlenmez.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **HAKEM KARARI (Yanlış Tahmin):** `partially_supported` ❌
- **Bilirkişi Modelleri:** Model A = `contradicted` | Model B = `partially_supported` | Tercih = `Model B`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddianın ilk önermesi 'Boşanma karar verildiği gün evlilik birliğini sona erdirir' bağlam tarafından doğrulanmaktadır, ancak ikinci önerme 'Aile kütüğüne boşanma kaydı işlenmez' bağlamla doğrudan çelişmektedir. Bu nedenle, iddianın bir parçası doğrulanırken diğer parçası çelişmektedir."*
- **Ayrıştırılan Atomik Önermeler:** "Boşanma karar verildiği gün evlilik birliğini sona erdirir." | "Aile kütüğüne boşanma kaydı işlenmez."

---

### [HAKEM-12/13] ID: `tfb_ex_0414` | Alan: `GENERAL`
- **SORU:** Deri prick testi öncesinde hangi bilgiler önemlidir? Sonuç hangi bulgulara göre değerlendirilir?
- **BAĞLAM:** Deri prick testi, alerjik hastalık düşündüren yakınmalarda duyarlılığı araştırmak için kullanılan bir deri testidir. Hastanın teste tok gelmesi tercih edilir ve test günü aktif şikâyeti ile kullandığı ilaçları sağlık ekibine bildirmesi istenir. Uygulamada önkolun iç yüzüne bir damla alerjen konur ve steril bir lansetle deride yüzeysel bir giriş yapılır. Alerjen sayısı fazlaysa sırt bölgesi de kullanılabilir. Prick testi kısa sürede uygulanır ve alerjen verilen bölgede oluşan kızarıklık ile kabarıklık yaklaşık on beş-yirmi dakika sonra değerlendirilir.
- **İDDİA:** Kullanılan ilaçlar sağlık ekibine bildirilirken hasta teste aç gelir.
- **ALTIN ETİKET (Doğru Karar):** `partially_supported`
- **HAKEM KARARI (Yanlış Tahmin):** `supported` ❌
- **Bilirkişi Modelleri:** Model A = `supported` | Model B = `partially_supported` | Tercih = `Model A`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddiada kullanılan ilaçların bildirilmesi ve hasta teste aç gelmesi durumları bağlamda yer almaktadır. Ancak, 'hasta teste aç gelir' ifadesi bağlamda 'Hastanın teste tok gelmesi tercih edilir' şeklinde geçmekte ve bu iki ifade arasında bir çelişki bulunmamaktadır, sadece 'tok' kelimesi 'aç' kelimesinin zıddı olarak yorumlanmamalıdır, zira bağlam 'tok' kelimesini tercih edilebilirlik bağlamında kullanmaktadır."*
- **Ayrıştırılan Atomik Önermeler:** "Kullanılan ilaçlar sağlık ekibine bildirilirken" | "hasta teste aç gelir"

---

### [HAKEM-13/13] ID: `tfb_ex_0474` | Alan: `GENERAL`
- **SORU:** Elektrookulografide elektrotlar nereye yerleştirilir, hangi potansiyel değişimi kaydedilir?
- **BAĞLAM:** Elektrookulografi, retina pigment epitelinin işlevsel durumunu değerlendirmek için göz hareketleri sırasında kornea ile retina arasındaki elektriksel potansiyel farkını kaydeden bir testtir. Kayıt için her iki gözün iç ve dış kenarlarına cilt elektrotları yerleştirilir. Göz merkezden bir elektroda doğru hareket ettiğinde elektrotların gördüğü elektriksel kutuplar değişir ve aralarında potansiyel fark oluşur. Bu kayıt bazı kalıtsal retina hastalıklarının değerlendirilmesinde ve gerektiğinde ERG ile birlikte kullanılabilir.
- **İDDİA:** Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir. Kayıt, göz hareketinden bağımsız sabit bir potansiyeli ölçer.
- **ALTIN ETİKET (Doğru Karar):** `partially_supported`
- **HAKEM KARARI (Yanlış Tahmin):** `contradicted` ❌
- **Bilirkişi Modelleri:** Model A = `contradicted` | Model B = `partially_supported` | Tercih = `Model A`
- **Hakemin Gerekçesi (CoT Reasoning):** *"İddianın ilk önermesi 'Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir' bağlam tarafından doğrulanmaktadır. Ancak ikinci önerme 'Kayıt, göz hareketinden bağımsız sabit bir potansiyeli ölçer' bağlamda yer alan 'Göz merkezden bir elektroda doğru hareket ettiğinde elektrotların gördüğü elektriksel kutuplar değişir ve aralarında potansiyel fark oluşur' ifadesiyle çelişmektedir, çünkü kayıt göz hareketine bağlı olarak değişen bir potansiyel farkı ölçmektedir."*
- **Ayrıştırılan Atomik Önermeler:** "Elektrotlar gözlerin iç ve dış kenarlarına yerleştirilir." | "Kayıt, göz hareketinden bağımsız sabit bir potansiyeli ölçer."

---

## BÖLÜM 2: YEREL MODELLERİN ORTAK YANILGISI (20 VAKA)
*K1 ve K2 aynı yanlış kararda uzlaştığı için Hakem'e gidilmeden doğrudan onaylanan 20 vaka:*

### [UZLAŞMA-01/20] ID: `tfb_ex_0019` | Alan: `GENERAL`
- **SORU:** Kasko ürünleri teminat kapsamına göre nasıl ayrılır? Zorunlu trafik sigortasından temel farkı nedir?
- **BAĞLAM:** Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının tamamına ek olarak ek sözleşmeyle alınabilecek risklerin bir bölümünü; Tam Kasko ise bu ek risklerin tamamını kapsar. Kasko sigortalının kendi aracındaki maddi zararları güvence altına alırken zorunlu trafik sigortası aracın üçüncü kişilere verdiği maddi ve bedensel zararları karşılar.
- **İDDİA:** Kasko sigortası üçüncü kişilere verilen zararları, zorunlu trafik sigortası ise sigortalının kendi aracındaki maddi zararı karşılar.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Kasko sigortası üçüncü kişilere verilen zararları karşılar" | "Zorunlu trafik sigortası sigortalının kendi aracındaki maddi zararı karşılar"

---

### [UZLAŞMA-02/20] ID: `tfb_ex_0035` | Alan: `GENERAL`
- **SORU:** Kefalet Kurumu A Özkaynak Kefalet Programında kredi vadeleri, kefalet koşulları ve başvuru yolu nasıldır?
- **BAĞLAM:** Kefalet Kurumu A Özkaynak Kefalet Programı, uygun KOBİ ve benzeri yararlanıcıların banka kredilerine Kefalet Kurumu A’nın kendi özkaynağından kefalet sağlamasına dayanır. İşletme kredilerinde vade 6 ila 60 ay arasında, ödemesiz dönem en fazla bir yıldır; yatırım kredilerinde vade 6 ila 84 ay arasında ve ödemesiz dönem en fazla iki yıldır. Yararlanıcı veya grup başına kefalet limiti 5 milyon TL, azami kefalet oranı yüzde 80'dir. Başvurular bankalar üzerinden Kefalet Kurumu A’nın elektronik sistemi aracılığıyla yapılır.
- **İDDİA:** Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay, azami ödemesiz dönemi bir yıldır; bu sınırlar işletme kredileriyle aynıdır.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay" | "azami ödemesiz dönemi bir yıldır" | "bu sınırlar işletme kredileriyle aynıdır"

---

### [UZLAŞMA-03/20] ID: `tfb_ex_0115` | Alan: `GENERAL`
- **SORU:** Sermaye piyasasındaki bir uyuşmazlıkta başvuru mercii neye göre değişir?
- **BAĞLAM:** Sermaye piyasası uyuşmazlığında izlenecek başvuru yolu uyuşmazlığın türüne göre değişebilir. Borsada emirlerin iletilmesi, eşleştirilmesi ve gerçekleşen işlemlere ilişkin yükümlülüklerin yerine getirilmesi gibi borsa işlemlerinden doğan uyuşmazlıklar için Borsa A’ya başvuru yapılabilir. Borsa işlemleri dışındaki zarar ve tazmin talepleri Meslek Birliği A bünyesindeki müşteri uyuşmazlıkları hakem mekanizmasına iletilebilir. Düzenleyici Kurum A ise mevzuata aykırılık iddialarını idari yönden inceleyebilir ancak bu inceleme kapsamında zarar tazminine karar vermez.
- **İDDİA:** Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya, borsa dışı tazmin talepleri Borsa A’ya götürülür ve Düzenleyici Kurum A zarar tazminine karar verir.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya" | "borsa dışı tazmin talepleri Borsa’ya" | "zarar tazminine karar verir Düzenleyici Kurum A"

---

### [UZLAŞMA-04/20] ID: `tfb_ex_0195` | Alan: `GENERAL`
- **SORU:** Elektrik perakende satışında güvence bedeli hangi koşullarda alınır ve nasıl iade edilir?
- **BAĞLAM:** Elektrik perakende satışında görevli tedarik şirketi, kullanım yerinin değişmesi veya perakende satış sözleşmesinin sona ermesi ya da feshi halinde tüketim bedelinin ödenmemesi riskine karşı güvence bedeli talep eder. Ön ödemeli sayaç kullanan tüketicilerden, genel aydınlatma kapsamındaki yerlerden ve ilgili düzenlemede belirtilen ibadethanelerden güvence bedeli alınmaz. Perakende satış sözleşmesi sona erdiğinde, feshedildiğinde veya tüketici ön ödemeli sayaca geçtiğinde güvence bedeli iade edilir. Tüketicinin borçları ödendikten sonra kalan tutar, talep tarihinden itibaren en geç beş iş günü içinde iade edilir. İade için borcun ödenmesi dışında başka bir şart veya belge istenemez.
- **İDDİA:** Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır ve güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır" | "güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir"

---

### [UZLAŞMA-05/20] ID: `tfb_ex_0232` | Alan: `GENERAL`
- **SORU:** Arabulucuların elektronik tebligat adresiyle ilgili 23 Temmuz 2026 kuralı dosya tevziini nasıl etkiler?
- **BAĞLAM:** Arabuluculuk bürolarının dava şartı kapsamındaki yazışmalarında elektronik tebligat kanalı kullanılmasına yönelik yeni uygulamada, arabulucuların elektronik tebligat adresine sahip olması istenmiştir. Duyuruda bu adreslerin 23 Temmuz 2026 tarihine kadar tebligat yapılabilecek biçimde hazır olması gerektiği belirtilmiştir. Bu tarihten itibaren büro yazışmalarının elektronik tebligat adresi üzerinden yürütülmesi öngörülmüş; elektronik tebligat adresi bulunmayan arabuluculara dava şartı arabuluculuk kapsamında dosya tevzi edilmemesi ve kayıtlarının aktif durumdan çıkarılması bildirilmiştir.
- **İDDİA:** Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir ve daha önce tevzi edilen dosyalar yeniden dağıtılır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `contradicted` ❌
- **Ayrıştırılan Atomik Önermeler:** "Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir" | "daha önce tevzi edilen dosyalar yeniden dağıtılır"

---

### [UZLAŞMA-06/20] ID: `tfb_ex_0274` | Alan: `GENERAL`
- **SORU:** Noterde taşınmaz satışı yapılırken hukuki kontrollerden tapu tesciline kadar süreç nasıl ilerler?
- **BAĞLAM:** Noter, taşınmaz satış başvurusu üzerine bir başvuru belgesi düzenler ve taşınmaz üzerindeki kısıtlamalar ile satışa ilişkin yasal sınırlamaları inceler. Hak sahibinin belirlenememesi veya satışa engel hukuki bir durum bulunması hâlinde satış işlemi yapılmaz. Satışa engel durum olmadığı tespit edilirse sözleşme taraflarca imzalanır. Noter, tapu bilişim sisteminden yevmiye numarası alarak sözleşmeyi sisteme kaydeder; kaydın ardından tapu müdürlüğü taşınmazın tapu siciline tescilini sağlar.
- **İDDİA:** Satışa engel hukuki durum varsa noter işlemi yapmaz. Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz.
- **ALTIN ETİKET (Doğru Karar):** `partially_supported`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Satışa engel hukuki durum varsa noter işlemi yapmaz." | "Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz."

---

### [UZLAŞMA-07/20] ID: `tfb_ex_0278` | Alan: `GENERAL`
- **SORU:** Denetimli serbestlik hizmetlerinde gönüllü çalışmak isteyen biri hangi koşulları sağlamalı, başvuruyu nasıl yapmalıdır?
- **BAĞLAM:** Denetimli serbestlik hizmetlerinde gönüllü çalışmak isteyen kişinin Türk vatandaşı olması, başvuru tarihinde on sekiz yaşını tamamlamış bulunması ve mevzuatta belirtilen belirli suçlardan hükümlü olmaması gerekir. Gönüllü olmak isteyen kişi denetimli serbestlik müdürlüğüne dilekçe ile başvurur. Başvuruda gönüllü başvuru formu ve yerleşim yeri belgesi istenir; adli sicil belgesi müdürlük tarafından temin edilir. Başvuru, infaz işlemleri değerlendirme komisyonu tarafından incelenerek karara bağlanır.
- **İDDİA:** Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur, adli sicil belgesini de adayın dilekçesine eklemesi gerekir.
- **ALTIN ETİKET (Doğru Karar):** `partially_supported`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur" | "adli sicil belgesini de adayın dilekçesine eklemesi gerekir"

---

### [UZLAŞMA-08/20] ID: `tfb_ex_0323` | Alan: `GENERAL`
- **SORU:** EMG incelemesi nasıl uygulanır? Hangi durumlarda ek bölüm ya da ön bildirim gerekir?
- **BAĞLAM:** Elektromiyografi (EMG), sinir ve kasların elektriksel yöntemlerle değerlendirildiği bir incelemedir. İlk bölümde düşük şiddette elektrik uyarıları kullanılarak sinirlerin iletim fonksiyonları ölçülebilir. Gerekli hastalarda ikinci bölümde tek kullanımlık ince iğne elektrotlarla kaslar ve bu kaslara gelen sinirler değerlendirilir; her hastada iki bölümün birden yapılması zorunlu değildir. İncelemenin süresi hastaya ve istenen değerlendirmeye göre değişmekle birlikte yaklaşık yarım saat olabilir. Düzenli ilaçlar genellikle sürdürülebilir, ancak kan sulandırıcı kullananların ve kalp pili ya da başka bir pil taşıyanların hekimi önceden bilgilendirmesi önerilir.
- **İDDİA:** EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar. Sinir iletim ölçümü ikinci aşamadadır ve iki bölüm bütün hastalara uygulanır.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar" | "Sinir iletim ölçümü ikinci aşamadadır" | "EMG değerlendirmesi bütün hastalara uygulanır"

---

### [UZLAŞMA-09/20] ID: `tfb_ex_0332` | Alan: `GENERAL`
- **SORU:** PET/CT için hazırlık ve çekim süreci nasıldır? Hangi klinik amaçlarla kullanılır?
- **BAĞLAM:** PET/CT işlemi öncesinde hastanın en az altı saat aç kalması gerekir. İşleme başlanırken kan şekeri ölçülür; değer uygun aralıktaysa damar yoluyla radyoaktif işaretli madde verilir. Sık kullanılan maddelerden biri F-18 florodeoksiglukozdur. Enjeksiyonun ardından maddenin vücutta dağılması için hasta yaklaşık bir saat bekletilir ve daha sonra PET/CT cihazında görüntüleme yapılır. PET/CT, kanserin yaygınlığını değerlendirmede, canlı tümör dokusunun yerini göstermede ve gerektiğinde biyopsi alınacak bölgenin belirlenmesine yardımcı olmada kullanılabilir.
- **İDDİA:** Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır."

---

### [UZLAŞMA-10/20] ID: `tfb_ex_0336` | Alan: `GENERAL`
- **SORU:** Bronkoskopi süreci baştan sona nasıl ilerler?
- **BAĞLAM:** Bronkoskopi öncesinde kullanılan ilaçlar, mevcut hastalıklar ve ilaç alerjileri hekime bildirilmelidir. İşlemden altı ila sekiz saat önce yiyecek ve içecek alınmaması gerekir; sürekli kullanılan bazı ilaçlar hekimin yönlendirmesiyle az miktarda suyla alınabilir. Bronkoskop ağız veya burundan ilerletilerek hava yolları incelenir, gerekli olduğunda biyopsi alınabilir veya yıkama sıvısı toplanabilir. İşlem sonrasında hasta en az bir ila iki saat gözlem altında tutulur ve yutma refleksi zayıfladığı için yaklaşık iki saat yiyecek ve içecek verilmez. Anestezi etkisi nedeniyle en az on iki saat araç veya iş makinesi kullanılması ve alkol alınması önerilmez.
- **İDDİA:** Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır. Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır." | "Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır."

---

### [UZLAŞMA-11/20] ID: `tfb_ex_0340` | Alan: `GENERAL`
- **SORU:** Kolonoskopi için hazırlık, izlem ve işlem sonrası güvenlik nasıl sağlanır?
- **BAĞLAM:** Kolonoskopinin tam ve güvenilir yapılabilmesi için altı saatlik açlığın yanında iki ila üç günlük diyet ve özel ilaçlarla bağırsak temizliği gerekir. İşlem sırasında hasta sol yanına yatırılır; kalp ritmi ve kandaki oksijen miktarı izlenir. Karında basınç, gaz ve kramp görülebileceği için işlem öncesinde veya gerektiğinde işlem sırasında sakinleştirici ve ağrı azaltıcı ilaçlar uygulanabilir. Kolonoskopi yaklaşık yirmi ila otuz dakika sürebilir. İşlemden sonra hasta on beş ila otuz dakika dinlendirilir; ilaç kullanılmışsa güvenlik amacıyla yirmi dört saat taşıt veya makine kullanılmaması önerilir.
- **İDDİA:** Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır. Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır." | "Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır."

---

### [UZLAŞMA-12/20] ID: `tfb_ex_0360` | Alan: `GENERAL`
- **SORU:** Bilgisayarlı tomografi çekimi nasıl hazırlanıp uygulanır?
- **BAĞLAM:** Bilgisayarlı tomografi ilaçlı veya ilaçsız yapılabilir. İlaçlı incelemede kontrast madde damar yoluyla verilebilir veya suya karıştırılarak hastaya içirilebilir. Özel bir hazırlık talimatı verilmemişse her çekim için aynı hazırlık gerekmez; ilaçlı çekimlerde açlık istenebilir ve bazı incelemelerde hastadan belirli miktarda suyla erken başvurması istenir. Çekim bölgesindeki takı ve metal eşyalar çıkarılır. İnceleme sırasında hasta hareketli bir masa üzerinde halka biçimli tarayıcıdan geçirilir ve bazen nefes komutlarına uyması istenir. İşlem süresi tetkike göre değişmekle birlikte yaklaşık bir ila on dakika arasında olabilir.
- **İDDİA:** Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır. Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `contradicted` ❌
- **Ayrıştırılan Atomik Önermeler:** "Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır" | "Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir"

---

### [UZLAŞMA-13/20] ID: `tfb_ex_0364` | Alan: `GENERAL`
- **SORU:** MR çekimine hazırlanırken nelere dikkat edilir? Çekim sırasında hastadan ne beklenir?
- **BAĞLAM:** Manyetik rezonans incelemelerinin çoğunda özel bir ön hazırlık gerekmez; aksi söylenmedikçe hasta yemek yiyip düzenli ilaçlarını alabilir. Ancak bazı özellikli çekimlerde hazırlık değişir. Örneğin entero incelemesinde hastadan aç gelmesi ve hazırlanan yaklaşık bir buçuk litre suyu iki saat içinde içmesi, bazı batın ve ilaçlı incelemelerde ise en az sekiz saat açlık istenebilir. Güçlü manyetik alan nedeniyle saat, takı, kredi kartı, işitme cihazı ve benzeri metal ya da manyetik alandan etkilenebilecek eşyalar çekim odasına girmeden çıkarılmalıdır. Vücutta implant, kalp pili, metal parça veya benzeri bir materyal varsa görevliye önceden bildirilir. Çekim sırasında hasta hareketsiz kalır; cihazın gürültüsü için kulak koruyucu verilebilir ve görevliyle mikrofon üzerinden iletişim kurulabilir.
- **İDDİA:** Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir. Bu bilgi olmadan çekim planı oluşturulmaz.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir." | "Bu bilgi olmadan çekim planı oluşturulmaz."

---

### [UZLAŞMA-14/20] ID: `tfb_ex_0368` | Alan: `GENERAL`
- **SORU:** Mamografi öncesi hazırlık nasıldır? Meme neden sıkıştırılır?
- **BAĞLAM:** Mamografi çekimine gelmeden önce koltuk altı temizliği yapılması ve duş alınması önerilir. Koltukaltı ve göğüs bölgesine parfüm, deodorant veya benzeri ürünler uygulanmamalı; daha önce yapılmış meme görüntülemeleri varsa bunlar da beraberinde getirilmelidir. Çekim sırasında meme iki plastik tabaka arasında sıkıştırılır ve genellikle iki farklı pozisyonda görüntü alınır. Sıkıştırmanın amacı hareketi azaltmak, görüntüyü keskinleştirmek ve daha düşük doz radyasyonla görüntü elde edilmesine yardımcı olmaktır. Uygulanan baskı kısa süreli ağrı veya rahatsızlık oluşturabilir, ancak bu his genellikle çekim bittikten sonra geçer.
- **İDDİA:** Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır ve meme kısa süre sıkıştırılır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `contradicted` ❌
- **Ayrıştırılan Atomik Önermeler:** "Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır" | "meme kısa süre sıkıştırılır"

---

### [UZLAŞMA-15/20] ID: `tfb_ex_0372` | Alan: `GENERAL`
- **SORU:** Gastroskopi süreci baştan sona nasıl ilerler?
- **BAĞLAM:** Gastroskopi yemek borusu, mide ve onikiparmak bağırsağının incelenmesinde kullanılır. İnceleme sırasında görüntü alınabilir ve gerekli görülen alanlardan biyopsi örneği alınarak patolojiye gönderilebilir. İşlem için yaklaşık sekiz saat açlık gerekir. Rahatsızlığı azaltmak amacıyla boğaza uyuşturucu sprey uygulanabilir ve sakinleştirici ilaç verilebilir. Gastroskopi çoğu durumda yaklaşık beş ila on dakika sürer. İşlem sonrasında hasta bir ila iki saat izlenebilir; ardından sıvı gıdalara başlanıp aynı gün taburculuk yapılabilir. Gastroskopi yalnız tanı amacıyla değil, bazı kanamaların kontrolü, polip çıkarılması, daralmış bölgelerin genişletilmesi veya yabancı cisim çıkarılması gibi tedavi amaçlı işlemlerde de kullanılabilir.
- **İDDİA:** Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir. Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `contradicted` ❌
- **Ayrıştırılan Atomik Önermeler:** "Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir." | "Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir."

---

### [UZLAŞMA-16/20] ID: `tfb_ex_0405` | Alan: `GENERAL`
- **SORU:** Kemik yoğunluğu ölçümünde hastadan ne beklenir? Çekim ne zaman ertelenebilir?
- **BAĞLAM:** DEXA, kemik mineral yoğunluğunu ve kemik kaybını değerlendirmek için kullanılan düşük radyasyonlu bir ölçümdür. Ölçümde sıklıkla bel omurları ile kalça bölgesi değerlendirilir. Genel olarak özel bir ön hazırlık gerekmez; hasta yaklaşık on beş dakika yatar ve ölçümün tamamlanması için hareketsiz kalır. İşlem ağrısızdır. Gebelik veya emzirme durumu sağlık ekibine önceden bildirilmelidir. İncelemeden iki ile altı gün önce ağızdan ya da damar yoluyla kontrast madde kullanılmışsa DEXA çekimi ertelenebilir.
- **İDDİA:** DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır. Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir.
- **ALTIN ETİKET (Doğru Karar):** `supported`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır." | "Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir."

---

### [UZLAŞMA-17/20] ID: `tfb_ex_0423` | Alan: `GENERAL`
- **SORU:** ERCP öncesindeki hazırlıkla aynı seansta yapılabilen görüntüleme ve tedaviler nelerdir?
- **BAĞLAM:** ERCP, safra yolları ve pankreas kanalının tanı ve tedavisinde kullanılan özel bir endoskopi yöntemidir. Duodenoskop ağızdan ilerletilerek onikiparmak bağırsağına ulaştırılır; papilla üzerinden ince kateterlerle safra kanalına, gerektiğinde pankreas kanalına kontrast madde verilir ve X ışınıyla görüntüleme yapılır. Aynı seansta safra yolu taşının çıkarılması, darlığın balon veya stentle giderilmesi gibi tedaviler uygulanabilir. İşlemden önce en az altı-sekiz saat açlık gerekir; kan sulandırıcı ilaçlar ve ilaç alerjileri hekime bildirilir. Damar yolu açılıp sedoanaljezi uygulanır. İşlem genellikle otuz-altmış dakika sürer.
- **İDDİA:** ERCP sırasında görüntüleme için kontrast mesaneye verilir ve işlem sedoanaljezi olmadan tamamlanır.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "ERCP sırasında görüntüleme için kontrast mesaneye verilir" | "ERCP işlemi sedoanaljezi olmadan tamamlanır"

---

### [UZLAŞMA-18/20] ID: `tfb_ex_0452` | Alan: `GENERAL`
- **SORU:** TEE için hangi hazırlık yapılır? Prob yemek borusuna nasıl ilerletilir, işlem sonrasında neye dikkat edilir?
- **BAĞLAM:** Transözofageal ekokardiyografi, göğüsten yapılan ekokardiyografide yeterince görüntülenemeyen kalp yapılarını yemek borusundan ilerletilen ultrason probuyla incelemek için kullanılır. İşlem öncesinde en az dört saat açlık gerekir ve çıkarılabilir diş protezleri çıkarılır. Boğaza lokal anestezik sprey uygulanır, damar yolu açılır ve ağızlık yerleştirildikten sonra prob yutkunma yardımıyla yemek borusuna ilerletilir. İnceleme yaklaşık 15-20 dakika sürer. İşlemden sonra iki saat boyunca bir şey yenilip içilmez.
- **İDDİA:** Prob yemek borusunda belirli bir işarete kadar ilerletilir. Bu noktadan ek görüntü alınır.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "Prob yemek borusunda belirli bir işarete kadar ilerletilir." | "Bu noktadan ek görüntü alınır."

---

### [UZLAŞMA-19/20] ID: `tfb_ex_0463` | Alan: `GENERAL`
- **SORU:** Korneal cross-linking sırasında riboflavin ile UVA hangi sırayla uygulanır?
- **BAĞLAM:** Korneal cross-linking, ilerleme saptanan keratokonusta kornea dokusunu güçlendirmek için riboflavin ve ultraviyole A kullanılan bir işlemdir. Damla anestezisiyle göz uyuşturulduktan sonra korneanın epitel tabakası kaldırılır. Riboflavin solüsyonu 30 dakika boyunca beş dakikada bir damlatılır; ardından korneaya yaklaşık 30 dakika UVA uygulanırken riboflavin damlatılmaya devam edilir. İşlem sonunda göz antibiyotikli pomatla kapatılır ve ortalama iyileşme süreci yaklaşık iki gündür.
- **İDDİA:** UVA riboflavinden önce uygulanır. Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır.
- **ALTIN ETİKET (Doğru Karar):** `contradicted`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `partially_supported` ❌
- **Ayrıştırılan Atomik Önermeler:** "UVA riboflavinden önce uygulanır" | "Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır"

---

### [UZLAŞMA-20/20] ID: `tfb_ex_0468` | Alan: `GENERAL`
- **SORU:** Endoskopik ultrasonografi hangi yapıları gösterir? Şüpheli dokudan biyopsi nasıl alınabilir?
- **BAĞLAM:** Endoskopik ultrasonografi, endoskopi ile ultrasonografiyi aynı cihazda birleştirerek sindirim sisteminin iç yüzeyinin yanında duvar katmanlarını ve çevredeki lenf bezleri ile komşu organları incelemeyi sağlar. Endoskop ağızdan yemek borusu, mide ve ince bağırsağa doğru ilerletilir; işlem sırasında endoskopik görüntüler ile ultrason görüntüleri ayrı ekranlardan izlenir. Şüpheli bir doku görüldüğünde cihazdan ilerletilen iğneyle biyopsi örneği alınabilir. İşlem çoğunlukla sedasyon altında yapılır ve yaklaşık 20-30 dakika sürer.
- **İDDİA:** İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir.
- **ALTIN ETİKET (Doğru Karar):** `unverifiable`
- **ORTAK YANLIŞ KARAR (K1 ve K2):** `contradicted` ❌
- **Ayrıştırılan Atomik Önermeler:** "İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir"

---
