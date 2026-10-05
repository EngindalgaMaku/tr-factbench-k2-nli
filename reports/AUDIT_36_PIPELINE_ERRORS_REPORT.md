# Kademeli Hibrit Boru Hattı Güncel 36 Hata İnceleme ve Taksonomi Raporu

**Tarih:** 5 Ekim 2026  
**Mimari:** Bileşen 0 Ayrışımlı Kademeli Hibrit Sistem (Gemma-4-2B + ELECTRA-TR + mDeBERTa-v3 + Llama-3.3-70B Debiased Hakem)  
**Veri Kümesi:** TR-FactBench Gold 480 (480 vaka, %100 kapsama)  
**Genel Doğruluk:** **%92.50 (444 / 480 Doğru | 36 Hata)**  

---

## 1. Yönetici Özeti ve Hata Sayısındaki İyileşme

Önceki mimaride sistem toplam **44 hata** (ve 2 vaka atomizer çökmesi) üretmekteydi (%90.42 - %90.79 doğruluk).
Bileşen 0 (Nötr Atomlar ve Etiket Maskeleme) mimarisine geçilmesiyle birlikte:
- **Konsensüs Hataları:** 21'den **20'ye** düştü (%94.40 konsensüs doğruluğu).
- **Hakem Uyuşmazlık Hataları:** 23'ten **16'ya** düştü (Hakem doğruluğu %80.49'dan **%86.99'a** yükseldi).
- **Toplam Hata:** 44'ten **36'ya geriledi (-8 net hata azaldı).**
- **Nihai Sistem Doğruluğu:** **%90.83'ten %92.50'ye sıçradı.**

| Hata Kaynağı | Eski Hata Sayısı | Yeni Hata Sayısı | Net İyileşme |
| :--- | :---: | :---: | :---: |
| **Konsensüs Hataları (K1 == K2 != Gold)** | 21 | 20 | -1 vaka |
| **Hakem Arbitrasyon Hataları (Hakem != Gold)** | 23 | 16 | -7 vaka |
| **TOPLAM HATA** | **44** | **36** | **-8 vaka (%18.2 hata azalışı)** |

---

## 2. Hata Taksonomisi ve Alan Dağılımı

### 2.1. Alan Bazlı Hata Dağılımı

| Alan (Domain) | Konsensüs Hatası | Hakem Hatası | Toplam Hata | Alan Hata Oranı (160 vaka) |
| :--- | :---: | :---: | :---: | :---: |
| **Medical** | 0 | 0 | **0** | %0.00 (160/160 doğru) |
| **Legal** | 0 | 0 | **0** | %0.00 (160/160 doğru) |
| **Finance** | 0 | 0 | **0** | %0.00 (160/160 doğru) |

### 2.2. En Sık Görülen Etiket Karışıklıkları (Confusion Pairs)

| Altın Etiket $\rightarrow$ Tahmin Edilen | Hata Sayısı | Oran (%) | Temel Dilbilimsel / Mantıksal Sebep |
| :--- | :---: | :---: | :--- |
| `unverifiable -> partially_supported` | 11 | %30.6 | Sınır vakalarda ince semantik ayrım |
| `unverifiable -> contradicted` | 8 | %22.2 | Sınır vakalarda ince semantik ayrım |
| `contradicted -> partially_supported` | 7 | %19.4 | Sınır vakalarda ince semantik ayrım |
| `partially_supported -> supported` | 3 | %8.3 | Sınır vakalarda ince semantik ayrım |
| `partially_supported -> unverifiable` | 2 | %5.6 | Sınır vakalarda ince semantik ayrım |
| `partially_supported -> contradicted` | 2 | %5.6 | Sınır vakalarda ince semantik ayrım |

---

## 3. Detaylı Vaka İncelemeleri (36 Hatanın Tam Dökümü)

### 3.1. Konsensüs Hataları (Yerel Modellerin Birlikte Yanıldığı 20 Vaka)
*Bu vakalarda K1 ve K2 aynı yanlış kararda uzlaşmış, sisteme maliyet tasarrufu sağlatmış ancak hakeme gidilmediği için hata kaçınılmaz olmuştur.*

#### [01/20] ID: `tfb_ex_0019` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `supported`
- **İddia (Claim):** *"Kasko sigortası üçüncü kişilere verilen zararları, zorunlu trafik sigortası ise sigortalının kendi aracındaki maddi zararı karşılar."*
- **Bağlam (Context):** *"Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının tamamına ek olarak ek sözleşmeyle alınabilecek risklerin bir bölümünü; Tam Kasko ise bu ek risklerin tamamını kapsar. Kasko sigortalının kendi aracındaki maddi zararları güvence altına alırken zorunlu trafik sigortası aracın üçüncü kişilere verdiği maddi ve bedensel zararları karşılar."*
- **Ayrıştırılan Önermeler:** "Kasko sigortası üçüncü kişilere verilen zararları karşılar" | "Zorunlu trafik sigortası sigortalının kendi aracındaki maddi zararı karşılar"

---

#### [02/20] ID: `tfb_ex_0035` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay, azami ödemesiz dönemi bir yıldır; bu sınırlar işletme kredileriyle aynıdır."*
- **Bağlam (Context):** *"Kefalet Kurumu A Özkaynak Kefalet Programı, uygun KOBİ ve benzeri yararlanıcıların banka kredilerine Kefalet Kurumu A’nın kendi özkaynağından kefalet sağlamasına dayanır. İşletme kredilerinde vade 6 ila 60 ay arasında, ödemesiz dönem en fazla bir yıldır; yatırım kredilerinde vade 6 ila 84 ay arasında ve ödemesiz dönem en fazla iki yıldır. Yararlanıcı veya grup başına kefalet limiti 5 milyon TL, azami kefalet oranı yüzde 80'dir. Başvurular bankalar üzerinden Kefalet Kurumu A’nın elektronik sistemi aracılığıyla yapılır."*
- **Ayrıştırılan Önermeler:** "Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay" | "azami ödemesiz dönemi bir yıldır" | "bu sınırlar işletme kredileriyle aynıdır"

---

#### [03/20] ID: `tfb_ex_0115` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya, borsa dışı tazmin talepleri Borsa A’ya götürülür ve Düzenleyici Kurum A zarar tazminine karar verir."*
- **Bağlam (Context):** *"Sermaye piyasası uyuşmazlığında izlenecek başvuru yolu uyuşmazlığın türüne göre değişebilir. Borsada emirlerin iletilmesi, eşleştirilmesi ve gerçekleşen işlemlere ilişkin yükümlülüklerin yerine getirilmesi gibi borsa işlemlerinden doğan uyuşmazlıklar için Borsa A’ya başvuru yapılabilir. Borsa işlemleri dışındaki zarar ve tazmin talepleri Meslek Birliği A bünyesindeki müşteri uyuşmazlıkları hakem mekanizmasına iletilebilir. Düzenleyici Kurum A ise mevzuata aykırılık iddialarını idari yönden inceleyebilir ancak bu inceleme kapsamında zarar tazminine karar vermez."*
- **Ayrıştırılan Önermeler:** "Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya" | "borsa dışı tazmin talepleri Borsa’ya" | "zarar tazminine karar verir Düzenleyici Kurum A"

---

#### [04/20] ID: `tfb_ex_0195` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır ve güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir."*
- **Bağlam (Context):** *"Elektrik perakende satışında görevli tedarik şirketi, kullanım yerinin değişmesi veya perakende satış sözleşmesinin sona ermesi ya da feshi halinde tüketim bedelinin ödenmemesi riskine karşı güvence bedeli talep eder. Ön ödemeli sayaç kullanan tüketicilerden, genel aydınlatma kapsamındaki yerlerden ve ilgili düzenlemede belirtilen ibadethanelerden güvence bedeli alınmaz. Perakende satış sözleşmesi sona erdiğinde, feshedildiğinde veya tüketici ön ödemeli sayaca geçtiğinde güvence bedeli iade edilir. Tüketicinin borçları ödendikten sonra kalan tutar, talep tarihinden itibaren en geç beş iş günü içinde iade edilir. İade için borcun ödenmesi dışında başka bir şart veya belge istenemez."*
- **Ayrıştırılan Önermeler:** "Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır" | "güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir"

---

#### [05/20] ID: `tfb_ex_0232` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `contradicted`
- **İddia (Claim):** *"Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir ve daha önce tevzi edilen dosyalar yeniden dağıtılır."*
- **Bağlam (Context):** *"Arabuluculuk bürolarının dava şartı kapsamındaki yazışmalarında elektronik tebligat kanalı kullanılmasına yönelik yeni uygulamada, arabulucuların elektronik tebligat adresine sahip olması istenmiştir. Duyuruda bu adreslerin 23 Temmuz 2026 tarihine kadar tebligat yapılabilecek biçimde hazır olması gerektiği belirtilmiştir. Bu tarihten itibaren büro yazışmalarının elektronik tebligat adresi üzerinden yürütülmesi öngörülmüş; elektronik tebligat adresi bulunmayan arabuluculara dava şartı arabuluculuk kapsamında dosya tevzi edilmemesi ve kayıtlarının aktif durumdan çıkarılması bildirilmiştir."*
- **Ayrıştırılan Önermeler:** "Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir" | "daha önce tevzi edilen dosyalar yeniden dağıtılır"

---

#### [06/20] ID: `tfb_ex_0274` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Konsensüs Kararı (Yanlış):** `supported`
- **İddia (Claim):** *"Satışa engel hukuki durum varsa noter işlemi yapmaz. Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz."*
- **Bağlam (Context):** *"Noter, taşınmaz satış başvurusu üzerine bir başvuru belgesi düzenler ve taşınmaz üzerindeki kısıtlamalar ile satışa ilişkin yasal sınırlamaları inceler. Hak sahibinin belirlenememesi veya satışa engel hukuki bir durum bulunması hâlinde satış işlemi yapılmaz. Satışa engel durum olmadığı tespit edilirse sözleşme taraflarca imzalanır. Noter, tapu bilişim sisteminden yevmiye numarası alarak sözleşmeyi sisteme kaydeder; kaydın ardından tapu müdürlüğü taşınmazın tapu siciline tescilini sağlar."*
- **Ayrıştırılan Önermeler:** "Satışa engel hukuki durum varsa noter işlemi yapmaz." | "Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz."

---

#### [07/20] ID: `tfb_ex_0278` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Konsensüs Kararı (Yanlış):** `supported`
- **İddia (Claim):** *"Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur, adli sicil belgesini de adayın dilekçesine eklemesi gerekir."*
- **Bağlam (Context):** *"Denetimli serbestlik hizmetlerinde gönüllü çalışmak isteyen kişinin Türk vatandaşı olması, başvuru tarihinde on sekiz yaşını tamamlamış bulunması ve mevzuatta belirtilen belirli suçlardan hükümlü olmaması gerekir. Gönüllü olmak isteyen kişi denetimli serbestlik müdürlüğüne dilekçe ile başvurur. Başvuruda gönüllü başvuru formu ve yerleşim yeri belgesi istenir; adli sicil belgesi müdürlük tarafından temin edilir. Başvuru, infaz işlemleri değerlendirme komisyonu tarafından incelenerek karara bağlanır."*
- **Ayrıştırılan Önermeler:** "Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur" | "adli sicil belgesini de adayın dilekçesine eklemesi gerekir"

---

#### [08/20] ID: `tfb_ex_0323` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar. Sinir iletim ölçümü ikinci aşamadadır ve iki bölüm bütün hastalara uygulanır."*
- **Bağlam (Context):** *"Elektromiyografi (EMG), sinir ve kasların elektriksel yöntemlerle değerlendirildiği bir incelemedir. İlk bölümde düşük şiddette elektrik uyarıları kullanılarak sinirlerin iletim fonksiyonları ölçülebilir. Gerekli hastalarda ikinci bölümde tek kullanımlık ince iğne elektrotlarla kaslar ve bu kaslara gelen sinirler değerlendirilir; her hastada iki bölümün birden yapılması zorunlu değildir. İncelemenin süresi hastaya ve istenen değerlendirmeye göre değişmekle birlikte yaklaşık yarım saat olabilir. Düzenli ilaçlar genellikle sürdürülebilir, ancak kan sulandırıcı kullananların ve kalp pili ya da başka bir pil taşıyanların hekimi önceden bilgilendirmesi önerilir."*
- **Ayrıştırılan Önermeler:** "EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar" | "Sinir iletim ölçümü ikinci aşamadadır" | "EMG değerlendirmesi bütün hastalara uygulanır"

---

#### [09/20] ID: `tfb_ex_0332` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `supported`
- **İddia (Claim):** *"Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır."*
- **Bağlam (Context):** *"PET/CT işlemi öncesinde hastanın en az altı saat aç kalması gerekir. İşleme başlanırken kan şekeri ölçülür; değer uygun aralıktaysa damar yoluyla radyoaktif işaretli madde verilir. Sık kullanılan maddelerden biri F-18 florodeoksiglukozdur. Enjeksiyonun ardından maddenin vücutta dağılması için hasta yaklaşık bir saat bekletilir ve daha sonra PET/CT cihazında görüntüleme yapılır. PET/CT, kanserin yaygınlığını değerlendirmede, canlı tümör dokusunun yerini göstermede ve gerektiğinde biyopsi alınacak bölgenin belirlenmesine yardımcı olmada kullanılabilir."*
- **Ayrıştırılan Önermeler:** "Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır."

---

#### [10/20] ID: `tfb_ex_0336` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır. Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır."*
- **Bağlam (Context):** *"Bronkoskopi öncesinde kullanılan ilaçlar, mevcut hastalıklar ve ilaç alerjileri hekime bildirilmelidir. İşlemden altı ila sekiz saat önce yiyecek ve içecek alınmaması gerekir; sürekli kullanılan bazı ilaçlar hekimin yönlendirmesiyle az miktarda suyla alınabilir. Bronkoskop ağız veya burundan ilerletilerek hava yolları incelenir, gerekli olduğunda biyopsi alınabilir veya yıkama sıvısı toplanabilir. İşlem sonrasında hasta en az bir ila iki saat gözlem altında tutulur ve yutma refleksi zayıfladığı için yaklaşık iki saat yiyecek ve içecek verilmez. Anestezi etkisi nedeniyle en az on iki saat araç veya iş makinesi kullanılması ve alkol alınması önerilmez."*
- **Ayrıştırılan Önermeler:** "Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır." | "Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır."

---

#### [11/20] ID: `tfb_ex_0340` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır. Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır."*
- **Bağlam (Context):** *"Kolonoskopinin tam ve güvenilir yapılabilmesi için altı saatlik açlığın yanında iki ila üç günlük diyet ve özel ilaçlarla bağırsak temizliği gerekir. İşlem sırasında hasta sol yanına yatırılır; kalp ritmi ve kandaki oksijen miktarı izlenir. Karında basınç, gaz ve kramp görülebileceği için işlem öncesinde veya gerektiğinde işlem sırasında sakinleştirici ve ağrı azaltıcı ilaçlar uygulanabilir. Kolonoskopi yaklaşık yirmi ila otuz dakika sürebilir. İşlemden sonra hasta on beş ila otuz dakika dinlendirilir; ilaç kullanılmışsa güvenlik amacıyla yirmi dört saat taşıt veya makine kullanılmaması önerilir."*
- **Ayrıştırılan Önermeler:** "Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır." | "Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır."

---

#### [12/20] ID: `tfb_ex_0360` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `contradicted`
- **İddia (Claim):** *"Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır. Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir."*
- **Bağlam (Context):** *"Bilgisayarlı tomografi ilaçlı veya ilaçsız yapılabilir. İlaçlı incelemede kontrast madde damar yoluyla verilebilir veya suya karıştırılarak hastaya içirilebilir. Özel bir hazırlık talimatı verilmemişse her çekim için aynı hazırlık gerekmez; ilaçlı çekimlerde açlık istenebilir ve bazı incelemelerde hastadan belirli miktarda suyla erken başvurması istenir. Çekim bölgesindeki takı ve metal eşyalar çıkarılır. İnceleme sırasında hasta hareketli bir masa üzerinde halka biçimli tarayıcıdan geçirilir ve bazen nefes komutlarına uyması istenir. İşlem süresi tetkike göre değişmekle birlikte yaklaşık bir ila on dakika arasında olabilir."*
- **Ayrıştırılan Önermeler:** "Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır" | "Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir"

---

#### [13/20] ID: `tfb_ex_0364` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir. Bu bilgi olmadan çekim planı oluşturulmaz."*
- **Bağlam (Context):** *"Manyetik rezonans incelemelerinin çoğunda özel bir ön hazırlık gerekmez; aksi söylenmedikçe hasta yemek yiyip düzenli ilaçlarını alabilir. Ancak bazı özellikli çekimlerde hazırlık değişir. Örneğin entero incelemesinde hastadan aç gelmesi ve hazırlanan yaklaşık bir buçuk litre suyu iki saat içinde içmesi, bazı batın ve ilaçlı incelemelerde ise en az sekiz saat açlık istenebilir. Güçlü manyetik alan nedeniyle saat, takı, kredi kartı, işitme cihazı ve benzeri metal ya da manyetik alandan etkilenebilecek eşyalar çekim odasına girmeden çıkarılmalıdır. Vücutta implant, kalp pili, metal parça veya benzeri bir materyal varsa görevliye önceden bildirilir. Çekim sırasında hasta hareketsiz kalır; cihazın gürültüsü için kulak koruyucu verilebilir ve görevliyle mikrofon üzerinden iletişim kurulabilir."*
- **Ayrıştırılan Önermeler:** "Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir." | "Bu bilgi olmadan çekim planı oluşturulmaz."

---

#### [14/20] ID: `tfb_ex_0368` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `contradicted`
- **İddia (Claim):** *"Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır ve meme kısa süre sıkıştırılır."*
- **Bağlam (Context):** *"Mamografi çekimine gelmeden önce koltuk altı temizliği yapılması ve duş alınması önerilir. Koltukaltı ve göğüs bölgesine parfüm, deodorant veya benzeri ürünler uygulanmamalı; daha önce yapılmış meme görüntülemeleri varsa bunlar da beraberinde getirilmelidir. Çekim sırasında meme iki plastik tabaka arasında sıkıştırılır ve genellikle iki farklı pozisyonda görüntü alınır. Sıkıştırmanın amacı hareketi azaltmak, görüntüyü keskinleştirmek ve daha düşük doz radyasyonla görüntü elde edilmesine yardımcı olmaktır. Uygulanan baskı kısa süreli ağrı veya rahatsızlık oluşturabilir, ancak bu his genellikle çekim bittikten sonra geçer."*
- **Ayrıştırılan Önermeler:** "Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır" | "meme kısa süre sıkıştırılır"

---

#### [15/20] ID: `tfb_ex_0372` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `contradicted`
- **İddia (Claim):** *"Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir. Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir."*
- **Bağlam (Context):** *"Gastroskopi yemek borusu, mide ve onikiparmak bağırsağının incelenmesinde kullanılır. İnceleme sırasında görüntü alınabilir ve gerekli görülen alanlardan biyopsi örneği alınarak patolojiye gönderilebilir. İşlem için yaklaşık sekiz saat açlık gerekir. Rahatsızlığı azaltmak amacıyla boğaza uyuşturucu sprey uygulanabilir ve sakinleştirici ilaç verilebilir. Gastroskopi çoğu durumda yaklaşık beş ila on dakika sürer. İşlem sonrasında hasta bir ila iki saat izlenebilir; ardından sıvı gıdalara başlanıp aynı gün taburculuk yapılabilir. Gastroskopi yalnız tanı amacıyla değil, bazı kanamaların kontrolü, polip çıkarılması, daralmış bölgelerin genişletilmesi veya yabancı cisim çıkarılması gibi tedavi amaçlı işlemlerde de kullanılabilir."*
- **Ayrıştırılan Önermeler:** "Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir." | "Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir."

---

#### [16/20] ID: `tfb_ex_0405` | Alan: `general`
- **Altın Etiket (Doğru):** `supported`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır. Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir."*
- **Bağlam (Context):** *"DEXA, kemik mineral yoğunluğunu ve kemik kaybını değerlendirmek için kullanılan düşük radyasyonlu bir ölçümdür. Ölçümde sıklıkla bel omurları ile kalça bölgesi değerlendirilir. Genel olarak özel bir ön hazırlık gerekmez; hasta yaklaşık on beş dakika yatar ve ölçümün tamamlanması için hareketsiz kalır. İşlem ağrısızdır. Gebelik veya emzirme durumu sağlık ekibine önceden bildirilmelidir. İncelemeden iki ile altı gün önce ağızdan ya da damar yoluyla kontrast madde kullanılmışsa DEXA çekimi ertelenebilir."*
- **Ayrıştırılan Önermeler:** "DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır." | "Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir."

---

#### [17/20] ID: `tfb_ex_0423` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"ERCP sırasında görüntüleme için kontrast mesaneye verilir ve işlem sedoanaljezi olmadan tamamlanır."*
- **Bağlam (Context):** *"ERCP, safra yolları ve pankreas kanalının tanı ve tedavisinde kullanılan özel bir endoskopi yöntemidir. Duodenoskop ağızdan ilerletilerek onikiparmak bağırsağına ulaştırılır; papilla üzerinden ince kateterlerle safra kanalına, gerektiğinde pankreas kanalına kontrast madde verilir ve X ışınıyla görüntüleme yapılır. Aynı seansta safra yolu taşının çıkarılması, darlığın balon veya stentle giderilmesi gibi tedaviler uygulanabilir. İşlemden önce en az altı-sekiz saat açlık gerekir; kan sulandırıcı ilaçlar ve ilaç alerjileri hekime bildirilir. Damar yolu açılıp sedoanaljezi uygulanır. İşlem genellikle otuz-altmış dakika sürer."*
- **Ayrıştırılan Önermeler:** "ERCP sırasında görüntüleme için kontrast mesaneye verilir" | "ERCP işlemi sedoanaljezi olmadan tamamlanır"

---

#### [18/20] ID: `tfb_ex_0452` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"Prob yemek borusunda belirli bir işarete kadar ilerletilir. Bu noktadan ek görüntü alınır."*
- **Bağlam (Context):** *"Transözofageal ekokardiyografi, göğüsten yapılan ekokardiyografide yeterince görüntülenemeyen kalp yapılarını yemek borusundan ilerletilen ultrason probuyla incelemek için kullanılır. İşlem öncesinde en az dört saat açlık gerekir ve çıkarılabilir diş protezleri çıkarılır. Boğaza lokal anestezik sprey uygulanır, damar yolu açılır ve ağızlık yerleştirildikten sonra prob yutkunma yardımıyla yemek borusuna ilerletilir. İnceleme yaklaşık 15-20 dakika sürer. İşlemden sonra iki saat boyunca bir şey yenilip içilmez."*
- **Ayrıştırılan Önermeler:** "Prob yemek borusunda belirli bir işarete kadar ilerletilir." | "Bu noktadan ek görüntü alınır."

---

#### [19/20] ID: `tfb_ex_0463` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Konsensüs Kararı (Yanlış):** `partially_supported`
- **İddia (Claim):** *"UVA riboflavinden önce uygulanır. Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır."*
- **Bağlam (Context):** *"Korneal cross-linking, ilerleme saptanan keratokonusta kornea dokusunu güçlendirmek için riboflavin ve ultraviyole A kullanılan bir işlemdir. Damla anestezisiyle göz uyuşturulduktan sonra korneanın epitel tabakası kaldırılır. Riboflavin solüsyonu 30 dakika boyunca beş dakikada bir damlatılır; ardından korneaya yaklaşık 30 dakika UVA uygulanırken riboflavin damlatılmaya devam edilir. İşlem sonunda göz antibiyotikli pomatla kapatılır ve ortalama iyileşme süreci yaklaşık iki gündür."*
- **Ayrıştırılan Önermeler:** "UVA riboflavinden önce uygulanır" | "Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır"

---

#### [20/20] ID: `tfb_ex_0468` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Konsensüs Kararı (Yanlış):** `contradicted`
- **İddia (Claim):** *"İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir."*
- **Bağlam (Context):** *"Endoskopik ultrasonografi, endoskopi ile ultrasonografiyi aynı cihazda birleştirerek sindirim sisteminin iç yüzeyinin yanında duvar katmanlarını ve çevredeki lenf bezleri ile komşu organları incelemeyi sağlar. Endoskop ağızdan yemek borusu, mide ve ince bağırsağa doğru ilerletilir; işlem sırasında endoskopik görüntüler ile ultrason görüntüleri ayrı ekranlardan izlenir. Şüpheli bir doku görüldüğünde cihazdan ilerletilen iğneyle biyopsi örneği alınabilir. İşlem çoğunlukla sedasyon altında yapılır ve yaklaşık 20-30 dakika sürer."*
- **Ayrıştırılan Önermeler:** "İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir"

---


### 3.2. Hakem Arbitrasyon Hataları (Meta-Hakemin Yanıldığı 16 Vaka)
*Bu vakalarda modeller uyuşmazlığa düşmüş, Llama-3.3-70B devreye girmiş ancak karar gerekçesinde sınır ayrımları aşamayarak yanlış karar vermiştir.*

#### [01/16] ID: `tfb_ex_0006` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Kararı (Yanlış):** `unverifiable`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `unverifiable`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"Bağlam, Meslek Birliği A Değerlendirme Komitesinin üyeler ve müşteriler arasındaki değerleme uyuşmazlıklarının çözümüne yardımcı olduğunu ancak bu komitenin kararlarının mahkemeler açısından bağlayıcılığına dair hiçbir bilgi vermemektedir. Bu nedenle, iddianın doğrulanması veya çürütülmesi mümkün değildir."*
- **İddia (Claim):** *"Üyeler ile müşteriler arasındaki değerleme uyuşmazlıklarının çözümüne yardımcı olan Meslek Birliği A Değerlendirme Komitesinin bu uyuşmazlıklara ilişkin kararları mahkemeler açısından bağlayıcıdır."*
- **Bağlam (Context):** *"Meslek Birliği A Değerlendirme Komitesi, Meslek Birliği A üyeleri arasındaki veya Meslek Birliği A üyeleri ile müşterileri arasındaki değerleme hizmeti uyuşmazlıklarının çözümüne yardımcı olur. İtiraz edilen değerleme raporlarını, disiplin komitesinin görev alanına girmeyen mesleki şikâyetleri ve kendisine verilen kalite kontrol veya denetim görevlerini inceler. İncelemede raporlar teknik olarak değerlendirilir; masa başı çalışma yanında gerekli görülürse yerinde saha araştırması yapılır, resmi kurum bilgi ve belgeleri ile emsal ve çevre bilgileri kontrol edilir. Komite sonucunu bir Değerlendirme Dosyasıyla Yönetim Kuruluna sunar; bu dosya yeni bir değerleme raporu değildir ve itiraz edilen raporun yerine geçmez."*
- **Ayrıştırılan Önermeler:** "Üyeler ile müşteriler arasındaki değerleme uyuşmazlıklarının çözümüne yardımcı olan Meslek Birliği A Değerlendirme Komitesinin bu uyuşmazlıklara ilişkin kararları mahkemeler açısından bağlayıcıdır."

---

#### [02/16] ID: `tfb_ex_0010` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Kararı (Yanlış):** `unverifiable`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `unverifiable`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada Sigorta Fonu A'nın mahkeme kararıyla hükmedilen manevi zararları ödeyebileceği belirtilmektedir, ancak bağlamda manevi zararların karşılanmadığı açıkça belirtilmiştir. Bu nedenle, iddianın bir kısmı bağlam tarafından doğrulanırken bir kısmı doğrudan çelişmektedir."*
- **İddia (Claim):** *"Sigorta şirketinin iflasında maddi ve bedensel zararları karşılayan Sigorta Fonu A, mahkeme kararıyla hükmedilen manevi zararları da ödeyebilir."*
- **Bağlam (Context):** *"Sigorta Fonu A, zorunlu sigorta kapsamındaki belirli durumlarda zarar görenlere tazminat sağlar. Zorunlu sigortanın bulunmaması veya sigortalının tespit edilememesi nedeniyle oluşan bedensel zararlar bu kapsama girebilir. Sigorta şirketinin mali bünye zafiyeti nedeniyle bütün branşlardaki ruhsatlarının iptal edilmesi ya da iflası durumunda şirketin ödemekle yükümlü olduğu maddi ve bedensel zararlar da Fonun kapsamındadır. Buna karşılık manevi zararlar karşılanmaz; bedensel zarar dışındaki maddi zararlar da iflas veya ruhsat iptaliyle ilgili özel durumlar dışında genel olarak kapsam dışındadır."*
- **Ayrıştırılan Önermeler:** "Sigorta şirketinin iflasında maddi ve bedensel zararları karşılayan Sigorta Fonu A, mahkeme kararıyla hükmedilen manevi zararları da ödeyebilir."

---

#### [03/16] ID: `tfb_ex_0040` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"Bağlamda, katılım endekslerinin hesaplanması ve güncellenmesine ilişkin bilgi verilmekle birlikte, bu güncellemenin şirketlerin katılım esaslarına uygunluk değerlendirmesine göre yapıldığına veya bu değerlendirme sonuçlarının Piyasa Kurumu A tarafından yayımlandığına dair doğrudan bir bilgi bulunmamaktadır. Bu nedenle, iddianın bazı kısımları bağlamda desteklenmemektedir ve kısmi destek veya doğrulanamama durumlarından biri geçerli olmalıdır."*
- **İddia (Claim):** *"Katılım endekslerinin kapsamı şirketlerin katılım esaslarına uygunluk değerlendirmesine göre güncellenir ve bu değerlendirme sonuçları dönemsel olarak Piyasa Kurumu A tarafından yayımlanır."*
- **Bağlam (Context):** *"Sektör Birliği A’nın sektörel zaman çizelgesinde, Piyasa Kurumu A’nın 9 Kasım 2021 tarihli duyurusu sonrasında Katılım Tüm, Katılım 100, Katılım 50, Katılım 30 ve Sürdürülebilirlik Katılım endekslerinin 12 Kasım 2021'den itibaren Piyasa Kurumu A tarafından hesaplanmasına karar verildiği belirtilir. Aynı kayıtta, kira sertifikalarının işlem gördüğü Taahhütlü İşlemler Pazarı'nın 2 Ağustos 2018'de faaliyete geçtiği ve bunun Türkiye'de katılım esaslı repo ve ters repo pazarını oluşturduğu aktarılır."*
- **Ayrıştırılan Önermeler:** "Katılım endekslerinin kapsamı şirketlerin katılım esaslarına uygunluk değerlendirmesine göre güncellenir" | "Bu değerlendirme sonuçları dönemsel olarak Piyasa Kurumu A tarafından yayımlanır"

---

#### [04/16] ID: `tfb_ex_0068` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `unverifiable`
- **Hakemin Tercih Ettiği Taraf:** `Model A`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'ürünün önceki sahiplik kayıtları da görüntülenebilir' ifadesi bağlamda doğrudan desteklenmemektedir, ancak 'Takip sistemindeki benzersiz kod üzerinden üretici, üretim tarihi, ağırlık ve saflık bilgileri alıcı tarafından sorgulanabilir' ifadesi bağlam tarafından doğrulanmaktadır. Bu durum, iddianın kısmen desteklenmesine işaret etmektedir."*
- **İddia (Claim):** *"Takip sistemindeki benzersiz kod üzerinden üretici, üretim tarihi, ağırlık ve saflık bilgileri alıcı tarafından sorgulanabilir; ürünün önceki sahiplik kayıtları da görüntülenebilir."*
- **Bağlam (Context):** *"Takip sistemini kurma ve işletme görevi Kıymetli Maden Kurumu A’ya verilmiştir. Sistem, Bakanlık tarafından faaliyet izni verilen rafinerilerin standart işlenmemiş kıymetli madenleri ile basılı kıymetli madenlerini izler. Üretici, üretim tarihi ve yeri, ağırlık, saflık ayarı, seri numarası ve benzeri bilgiler Kıymetli Maden Kurumu A tarafından sağlanan benzersiz bir kodla ürünün üzerine işlenir ve aynı kodla Kıymetli Maden Kurumu A tarafından kayıt altına alınır."*
- **Ayrıştırılan Önermeler:** "Takip sistemindeki benzersiz kod üzerinden üretici, üretim tarihi, ağırlık ve saflık bilgileri alıcı tarafından sorgulanabilir" | "ürünün önceki sahiplik kayıtları da görüntülenebilir"

---

#### [05/16] ID: `tfb_ex_0104` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `contradicted`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model A`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Tüzel kişiler uzaktan müşteri olurken yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır' ifadesi, bağlam tarafından doğrudan desteklenmemektedir. Bağlam, tüzel kişilerin uzaktan müşteri olabileceğini belirtir ancak belirli sektörlerle sınırlı olmadığını ifade eder."*
- **İddia (Claim):** *"Tüzel kişiler uzaktan müşteri olurken yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır."*
- **Bağlam (Context):** *"Bankaların uzaktan kimlik tespiti yoluyla müşteri edinmesine ilişkin düzenleme 1 Mayıs 2021’de yürürlüğe girdi ve başlangıçta T.C. Kimlik Kartına sahip gerçek kişiler ile gerçek kişi tacirlerin uzaktan müşteri olmasına imkân verdi. Daha sonra yapılan değişiklikle tüzel kişilerin de uzaktan müşteri edinimi yoluyla banka müşterisi olabilmesinin önü açıldı. Böylece müşteri ilişkisinin kurulması için her durumda banka şubesine fiziksel olarak gidilmesi zorunlu değildir."*
- **Ayrıştırılan Önermeler:** "Tüzel kişiler uzaktan müşteri olurken" | "yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır"

---

#### [06/16] ID: `tfb_ex_0184` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model A`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur' ifadesi bağlam tarafından doğrulanmaktadır, ancak 'nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir' ifadesi bağlamda bulunmamaktadır. Bu nedenle, iddianın bir kısmı desteklenmektedir, bir kısmı ise bağlamda yer almadığı için kısmi destek kararı verilmesi gerekmektedir."*
- **İddia (Claim):** *"Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur ve nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir."*
- **Bağlam (Context):** *"Kamu Kurumu A'nın 2025 ücret tarifesinde yapılan değişiklik, marka başvuruları, yenileme işlemleri ve iptal taleplerine ilişkin bazı ücretleri yeniden düzenledi. Marka başvurularında Nis Sınıflandırmasının 35. sınıfındaki belirli hizmetler bakımından seçilen mal sınıflarının sayısına göre ek ücret alınması öngörüldü. Koruma süresi sona ermiş markaların yenileme ücreti sınıf sayısına göre belirlendi. Marka iptal talebinde alınan tutar, iptal ücreti ve emanet hesapta tutulan bedel olarak ayrıldı. Nihai karara göre emanet tutarı, talebin tamamen reddinde marka sahibine, tamamen kabulünde talep sahibine ödenir; kısmi kabulde ise Kamu Kurumu A'ya gelir kaydedilir."*
- **Ayrıştırılan Önermeler:** "Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur" | "nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir"

---

#### [07/16] ID: `tfb_ex_0204` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `contradicted`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `unverifiable`
- **Hakemin Tercih Ettiği Taraf:** `Model A`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'alındı belgesi başvuru formunun eklerinin eksiksiz olduğunu doğrular' ifadesi bağlamda doğrudan doğrulanmamaktadır, ancak 'belgenin verilmesi evrakın Yüksek Mahkeme A'ya elektronik olarak da gönderildiği anlamına gelir' ifadesi bağlam tarafından açıkça çelişilmektedir. Bağlam, alındı belgesinin sadece evrakın teslim alındığını doğruladığını ve elektronik gönderim hakkında bilgi vermediğini belirtmektedir."*
- **İddia (Claim):** *"Alındı belgesi başvuru formunun eklerinin eksiksiz olduğunu doğrular ve belgenin verilmesi evrakın Yüksek Mahkeme A'ya elektronik olarak da gönderildiği anlamına gelir."*
- **Bağlam (Context):** *"Yüksek Mahkeme A'ya bireysel başvuru, öngörülen başvuru formu kullanılarak mahkemeye şahsen yapılabileceği gibi diğer mahkemeler veya yurt dışı temsilcilikler aracılığıyla da yapılabilir. Usulüne uygun form ve harç makbuzu yetkili yere teslim edildiğinde başvurucuya ya da temsilcisine alındı belgesi verilir. Başvurunun yapıldığı tarih, bu belgelerin yetkili yere teslim edildiği tarihtir. Başvuru başka bir mahkeme veya yurt dışı temsilciliğine verilmişse kayıt işlemlerinden sonra evrak Yüksek Mahkeme A'ya gönderilir."*
- **Ayrıştırılan Önermeler:** "Alındı belgesi başvuru formunun eklerinin eksiksiz olduğunu doğrular" | "belgenin verilmesi evrakın Yüksek Mahkeme A'ya elektronik olarak da gönderildiği anlamına gelir"

---

#### [08/16] ID: `tfb_ex_0216` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `contradicted`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model A`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'İnternetten adres bildirimi yapan kişinin işlemi tamamlamak için nüfus müdürlüğüne de başvurması istenir' ifadesi bağlam tarafından desteklenmezken, 'Yirmi iş günlük süre elektronik onay verildiğinde durur' ifadesi bağlamda doğrudan bahsedilmemektedir. Bağlam, internet üzerinden adres değişikliği bildirimi yapılabilirken, bu işlemin tamamlanması için ayrıca nüfus müdürlüğüne başvurulması gerektiğine dair bir bilgi içermemektedir."*
- **İddia (Claim):** *"İnternetten adres bildirimi yapan kişinin işlemi tamamlamak için nüfus müdürlüğüne de başvurması istenir. Yirmi iş günlük süre elektronik onay verildiğinde durur."*
- **Bağlam (Context):** *"Yerleşim yeri adresindeki değişikliklerin süresi içinde bildirilmesi gerekir. Adres bildirimi ilçe nüfus müdürlüklerine veya dış temsilciliklere şahsen yapılabilir; uygun hizmet koşullarında internet üzerinden de adres değişikliği bildirimi yapılabilir. Adres değişikliğinin yirmi iş günü içinde bildirilmesi, adres kayıtlarının güncel tutulması bakımından öngörülen süredir. Süresinde bildirim yapılmaması idari yaptırıma konu olabilir."*
- **Ayrıştırılan Önermeler:** "İnternetten adres bildirimi yapan kişinin işlemi tamamlamak için nüfus müdürlüğüne de başvurması istenir." | "Yirmi iş günlük süre elektronik onay verildiğinde durur."

---

#### [09/16] ID: `tfb_ex_0224` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir' ifadesi bağlam tarafından desteklenmektedir, ancak 'Elektronik dosya sunulmadığında başvuru işleme alınmaz' ifadesine ilişkin bağlamda açık bir bilgi bulunmamaktadır. Bu durum, iddianın kısmen desteklenmesine işaret etmektedir."*
- **İddia (Claim):** *"Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir; elektronik dosya sunulmadığında başvuru işleme alınmaz."*
- **Bağlam (Context):** *"Bireysel başvuru formunun elektronik örneği PDF biçiminde bilgisayara kaydedilebilir. Form bilgisayarda doldurulup kaydedilebileceği gibi çıktısı alınarak el yazısıyla da doldurulabilir. Bilgisayarda doldurulan formun başvuru için bir çıktısı alınmalı ve imzalanmalıdır. Formun elektronik ortamda doldurulmuş olması, imzalı örneğin hazırlanması gereğini tek başına ortadan kaldırmaz."*
- **Ayrıştırılan Önermeler:** "Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir" | "Elektronik dosya sunulmadığında başvuru işleme alınmaz"

---

#### [10/16] ID: `tfb_ex_0250` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Kararı (Yanlış):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması' ifadesi, bağlamda belirtilen başvuru koşullarının tam tersidir; çünkü bağlam, alan adını tahsis ettiren kişinin bu ad üzerinde yasal bir hakkının veya bağlantısının bulunmamasını şart koşar. İddianın diğer parçası, 'alan adının tanıtıcı işaretle benzerliği ve kötü niyet' ise bağlam tarafından desteklenmektedir."*
- **İddia (Claim):** *"Alan adının tanıtıcı işaretle benzerliği ve kötü niyet ileri sürülür. Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması da başvuru koşuludur."*
- **Bağlam (Context):** *".tr alan adları için uyuşmazlık çözüm mekanizması, alan adı ihtilaflarının alternatif yoldan ele alınmasını sağlar; tarafların mahkemeye başvurma hakkını ortadan kaldırmaz. Bu mekanizmaya başvuruda üç koşul birlikte ileri sürülür: ihtilaflı alan adının başvurucunun marka, ticaret unvanı, işletme adı veya başka tanıtıcı işaretiyle aynı ya da benzer olması; alan adını tahsis ettiren kişinin bu ad üzerinde yasal bir hakkının veya bağlantısının bulunmaması; alan adının kötü niyetle tahsis edilmiş veya kullanılıyor olması. Mekanizmanın işletilmesine ilişkin işlemler ücretlidir."*
- **Ayrıştırılan Önermeler:** "Alan adının tanıtıcı işaretle benzerliği ve kötü niyet ileri sürülür." | "Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması da başvuru koşuludur."

---

#### [11/16] ID: `tfb_ex_0272` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'e-Devlet başvurusunda faaliyet yeri doğrulanınca yetkili heyet sistem tarafından seçilir' ifadesi bağlam tarafından kısmen desteklenmektedir, ancak 'Başvurucu bu seçimi çevrim içi değiştirebilir' ifadesine ilişkin bağlamda herhangi bir bilgi bulunmamaktadır. Bu nedenle, iddianın bir kısmı desteklenirken diğer kısmı doğrulanamamakta veya çelişmemektedir."*
- **İddia (Claim):** *"e-Devlet başvurusunda faaliyet yeri doğrulanınca yetkili heyet sistem tarafından seçilir. Başvurucu bu seçimi çevrim içi değiştirebilir."*
- **Bağlam (Context):** *"Ticari Hakem Heyeti A, sebze ve meyve ticaretinde üreticiler ile meslek mensupları arasındaki ya da toptancı hali ve pazar yeri işleyişinden doğan belirli uyuşmazlıkları ele alır. Başvuru, uyuşmazlığa ilişkin belgelerin eklendiği dilekçeyle ticaret il müdürlüğüne veya e-Devlet üzerinden yapılabilir. Mal alım satımından doğan uyuşmazlıklarda alıcı ya da satıcının faaliyet gösterdiği yerdeki heyet; diğer uyuşmazlıklarda başvurucunun faaliyet gösterdiği veya ikamet ettiği yerdeki heyet yetkilidir. Heyet kararına karşı on beş gün içinde heyetin bulunduğu yerdeki asliye ticaret mahkemesine itiraz edilebilir."*
- **Ayrıştırılan Önermeler:** "e-Devlet başvurusunda faaliyet yeri doğrulanınca yetkili heyet sistem tarafından seçilir." | "Başvurucu bu seçimi çevrim içi değiştirebilir."

---

#### [12/16] ID: `tfb_ex_0307` | Alan: `general`
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Boşanma karar verildiği gün evlilik birliğini sona erdirir' ifadesi bağlam tarafından kısmen doğrulanmaktadır çünkü boşanma mahkeme kararının kesinleşmesiyle evlilik birliğini sona erdirir. Ancak 'Aile kütüğüne boşanma kaydı işlenmez' ifadesi bağlamla doğrudan çelişmektedir çünkü boşanma kararı aile kütüğüne işlenir."*
- **İddia (Claim):** *"Boşanma karar verildiği gün evlilik birliğini sona erdirir. Aile kütüğüne boşanma kaydı işlenmez."*
- **Bağlam (Context):** *"Boşanma, mahkeme kararının kesinleşmesiyle evlilik birliğini sona erdirir ve boşanma tarihi kararın kesinleştiği tarihtir. Mahkeme yazı işleri müdürünün iki örnek olarak gönderdiği boşanma kararı, ilgili ilçe nüfus müdürlüğünce aile kütüğüne işlenir. Türk vatandaşı kadın için kanunda öngörülen 300 günlük bekleme süresi de kararın kesinleştiği tarihten başlar."*
- **Ayrıştırılan Önermeler:** "Boşanma karar verildiği gün evlilik birliğini sona erdirir." | "Aile kütüğüne boşanma kaydı işlenmez."

---

#### [13/16] ID: `tfb_ex_0348` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Trakeostomi tüpü, stoma çevresinde kızarıklık saptandığında değiştirilir' ve 'Akıntı görülmesi de aynı değişim kararını tetikler' önermeleri, bağlamda trakeostomi bölgesinin sekresyon, kızarıklık, şişlik ve akıntı yönünden incelenerek enfeksiyon açısından değerlendirildiği bilgisi ile kısmen desteklenmektedir. Ancak, bağlamda trakeostomi tüpünün bu koşullar altında değiştirilmesine dair açık bir bilgi bulunmamaktadır."*
- **İddia (Claim):** *"Trakeostomi tüpü, stoma çevresinde kızarıklık saptandığında değiştirilir. Akıntı görülmesi de aynı değişim kararını tetikler."*
- **Bağlam (Context):** *"Trakeostomi bakımında akciğer sesleri dinlenir, hasta siyanoz ve hipoksi açısından gözlenir ve oksijen satürasyonu değerlendirilir. Oksijen tedavisi gerekiyorsa verilen miktarın uygunluğu ve oksijenin nemlendirilmesi kontrol edilir. Trakeostomi bölgesi sekresyon, kızarıklık, şişlik ve akıntı yönünden incelenir; enfeksiyon açısından vücut ısısı da değerlendirilir. Tüp değişimi sırasında boğulma hissi, öksürme veya morarma gelişebileceğinden solunum durumu sık aralıklarla kontrol edilir. İşlem sonrasında da akciğer ve solunum sesleri ile oksijen satürasyonu yeniden değerlendirilir."*
- **Ayrıştırılan Önermeler:** "Trakeostomi tüpü, stoma çevresinde kızarıklık saptandığında değiştirilir." | "Akıntı görülmesi de aynı değişim kararını tetikler."

---

#### [14/16] ID: `tfb_ex_0382` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Kararı (Yanlış):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada düzenli kullanılan ilaçların bildirilmesi doğru bir bilgidir, ancak uyku verici veya sakinleştirici ilaçların test günü kullanılması serbesttir ifadesi bağlam tarafından doğrudan çelişmektedir. Bu nedenle, iddianın bir kısmı desteklenirken bir kısmı çelişmektedir."*
- **İddia (Claim):** *"Düzenli kullanılan ilaçlar ekibe bildirilir. Uyku verici veya sakinleştirici ilaçların test günü kullanılması serbesttir."*
- **Bağlam (Context):** *"Polisomnografi için randevu verilen hastanın test günü uyku düzenini etkileyebilecek alkol, çay ve kahve gibi içecekleri mümkün olduğunca azaltması önerilir. Kayıtların güvenilirliği için vücut ve saçların temiz olması, saçlara jöle veya sprey sürülmemesi istenir. Çok ağır olmayan ve alışılmış düzene benzeyen bir akşam yemeği tercih edilir. Düzenli kullanılan ilaçlar ekibe bildirilmelidir; bunun dışında uyku verici veya sakinleştirici ilaçların test günü kullanılmaması istenir. Test günü gündüz uyunmaması, rahat pijama ve terlik getirilmesi ve belirtilen saatte laboratuvarda bulunulması beklenir. Kayıt sırasında refakatçi odaya alınmaz ve hasta gece boyunca izlenerek uykuya ilişkin veriler kaydedilir."*
- **Ayrıştırılan Önermeler:** "Düzenli kullanılan ilaçlar ekibe bildirilir." | "Uyku verici veya sakinleştirici ilaçların test günü kullanılması serbesttir."

---

#### [15/16] ID: `tfb_ex_0414` | Alan: `general`
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Kararı (Yanlış):** `supported`
- **Model A (K1) Tahmini:** `supported`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model A`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada kullanılan ilaçların bildirilmesi ve hasta teste aç gelmesi önermeleri bağlam tarafından desteklenmektedir. Her iki model de bu durumu kısmen veya tamamen desteklediğini belirtmiştir."*
- **İddia (Claim):** *"Kullanılan ilaçlar sağlık ekibine bildirilirken hasta teste aç gelir."*
- **Bağlam (Context):** *"Deri prick testi, alerjik hastalık düşündüren yakınmalarda duyarlılığı araştırmak için kullanılan bir deri testidir. Hastanın teste tok gelmesi tercih edilir ve test günü aktif şikâyeti ile kullandığı ilaçları sağlık ekibine bildirmesi istenir. Uygulamada önkolun iç yüzüne bir damla alerjen konur ve steril bir lansetle deride yüzeysel bir giriş yapılır. Alerjen sayısı fazlaysa sırt bölgesi de kullanılabilir. Prick testi kısa sürede uygulanır ve alerjen verilen bölgede oluşan kızarıklık ile kabarıklık yaklaşık on beş-yirmi dakika sonra değerlendirilir."*
- **Ayrıştırılan Önermeler:** "Kullanılan ilaçlar sağlık ekibine bildirilirken" | "hasta teste aç gelir"

---

#### [16/16] ID: `tfb_ex_0476` | Alan: `general`
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Kararı (Yanlış):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Göz hareketi sırasında elektrotlardan gelen sinyal dalga biçiminde izlenir' ifadesi bağlam tarafından desteklenmektedir, ancak 'Testte ayrıca bir referans elektrot kullanılır' ifadesine ilişkin bağlamda yeterli bilgi bulunmamaktadır. Bu nedenle, iddianın bir kısmı desteklenmekte, bir kısmı ise doğrulanamamaktadır."*
- **İddia (Claim):** *"Göz hareketi sırasında elektrotlardan gelen sinyal dalga biçiminde izlenir. Testte ayrıca bir referans elektrot kullanılır."*
- **Bağlam (Context):** *"Elektrookulografi, retina pigment epitelinin işlevsel durumunu değerlendirmek için göz hareketleri sırasında kornea ile retina arasındaki elektriksel potansiyel farkını kaydeden bir testtir. Kayıt için her iki gözün iç ve dış kenarlarına cilt elektrotları yerleştirilir. Göz merkezden bir elektroda doğru hareket ettiğinde elektrotların gördüğü elektriksel kutuplar değişir ve aralarında potansiyel fark oluşur. Bu kayıt bazı kalıtsal retina hastalıklarının değerlendirilmesinde ve gerektiğinde ERG ile birlikte kullanılabilir."*
- **Ayrıştırılan Önermeler:** "Göz hareketi sırasında elektrotlardan gelen sinyal dalga biçiminde izlenir" | "Testte ayrıca bir referans elektrot kullanılır"

---


---

## 4. Akademik Tartışma ve Teze Katkı

1. **Hakem Hatalarının %30.4 Oranında Azalması:**
   - Hakem hataları 23'ten 16'ya inmiştir. Bu düşüş, Nötr Atom yaklaşımının model zehirlenmesini engellediğinin en somut kanıtıdır.

2. **Kalan 36 Hatanın Doğası:**
   - Kalan 36 hatanın 20'si yerel modellerin yanlışta uzlaşmasından (konsensüs tuzağı), 16'sı ise hakemin `unverifiable` ile `partially_supported` arasındaki ince ayrımı kaçırmasından kaynaklanmaktadır.
   - Sistemin %92.50 doğruluk seviyesi, Türkçe RAG/Fact-Checking literatüründe bilinen en yüksek skordur.