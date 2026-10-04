# Kademeli Hibrit Boru Hattı 44 Hata Detaylı İnceleme ve Taksonomi Raporu
## TR-FactBench 478 Held-Out Test Kümesinde Başarısız Olunan Vakaların Kök Neden Analizi

**Tarih:** 4 Ekim 2026  
**Genel Başarım:** 434 / 478 Doğru (%90.79) | 44 / 478 Hata (%9.21)  
**Hata Dağılımı:** 21 Konsensüs Hatası (%47.7) + 23 Hakem Arbitrasyon Hatası (%52.3)  

---

## 1. Yönetici Özeti ve Hata Kategorizasyonu

Sistemin başarısız olduğu 44 vaka incelendiğinde, hataların rastgele dağılmadığı; aksine **semantik sınır çizgilerinde (boundary cases)** yoğunlaştığı görülmüştür.

| Hata Kategorisi | Vaka Sayısı | Yüzde (%) | Temel Dilsel/Semantik Neden |
|:---|:---:|:---:|:---|
| **Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)** | **14** | **%31.8** | İddiada bağlamla örtüşen kelimeler bulunması sebebiyle modelin/hakemin tam yalanı kısmi destek sanması. |
| **Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)** | **14** | **%31.8** | Bağlamda hiç olmayan bir konunun/öznenin, metindeki genel konuya benzerliği sebebiyle var sanılması. |
| **Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)** | **6** | **%13.6** | Bağlamda bilgi bulunmamasının doğrudan çelişki (yalan) olarak yorumlanması. |
| **Cat-4: Sıfır Tolerans Yanılgısı (Kısmi Doğruyu Göremeyip Tam Çelişki Sanma)** | **4** | **%9.1** | İddiada doğru bir önerme yer almasına rağmen, yanlış parçanın ağırlığı altında doğrunun gözden kaçırılması. |
| **Cat-5: Halüsinasyon Körlüğü (Yanlış Parçayı Kaçırıp Destekleniyor Sanma)** | **2** | **%4.5** | İddiadaki uydurma veya hatalı eklemenin fark edilmeyip bütünün doğru kabul edilmesi. |
| **Cat-6: Diğer Sınır Vakaları (supported -> partially_supported)** | **2** | **%4.5** | Nadir sınır vakaları ve ikili etiket geçişleri. |
| **Cat-6: Diğer Sınır Vakaları (contradicted -> supported)** | **1** | **%2.3** | Nadir sınır vakaları ve ikili etiket geçişleri. |
| **Cat-6: Diğer Sınır Vakaları (unverifiable -> supported)** | **1** | **%2.3** | Nadir sınır vakaları ve ikili etiket geçişleri. |

---

## 2. Hata Aşaması ve Alan (Domain) Dağılımı

### A. Hata Aşamasına Göre:
- **Aşama 1 (Konsensüs Hatası - K1 == K2 != Gold):** 21 / 44 (%47.7)
- **Aşama 2 (Hakem Arbitrasyon Hatası - Judge != Gold):** 23 / 44 (%52.3)

### B. Alana (Domain) Göre:
- **Klinik Tıp (Medical):** 20 / 44 (%45.5) *(Konsensüs hatalarının %66.7'si tıpta gerçekleşmiştir)*
- **Hukuk (Legal):** 14 / 44 (%31.8)
- **Finans (Finance):** 10 / 44 (%22.7)

---

## 3. Seçilmiş Somut Vaka Örnekleri ve Derinlemesine İnceleme

## 3. 44 Hatanın Tek Tek Derinlemesine İncelenmesi

Bu bölümde, boru hattının başarısız olduğu 44 vakanın tamamı iki ana aşamada (21 Konsensüs Hatası ve 23 Hakem Hatası) eksiksiz olarak incelenmiştir.

### 3.1. Konsensüs Hataları (21 Vaka: K1 == K2 != Altın Etiket)
Bu vakalarda her iki yerel model (ELECTRA ve Gemma+mDeBERTa) aynı yanlış etiket üzerinde uzlaşmış, sistem uyuşmazlık algılamadığı için hakeme gidilmeden doğrudan yanlış karar üretilmiştir.

#### Vaka 01 (Konsensüs): `tfb_ex_0019` — FINANCE
- **Başarısızlık Kategorisi:** Cat-6: Diğer Sınır Vakaları (contradicted -> supported)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `supported`
- **K1 (ELECTRA) Kararı:** `supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `supported`
- **İddia (Claim):** *"Kasko sigortası üçüncü kişilere verilen zararları, zorunlu trafik sigortası ise sigortalının kendi aracındaki maddi zararı karşılar."*
- **Bağlam (Context):** *"Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının tamamına ek olarak ek sözleşmeyle alınabilecek risklerin bir bölümünü; Tam Kasko ise bu ek risklerin tamamını kapsar. Kasko sigortalının kendi aracındaki maddi zararları güvence altına alırken zorunlu trafik sigortası aracın üçüncü kişilere verdiği maddi ve bedensel zararları karşılar."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Kasko sigortası üçüncü kişilere verilen zararları karşılar', 'label': 'entailment'}" | "{'atom': 'Zorunlu trafik sigortası sigortalının kendi aracındaki maddi zararı karşılar', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddia, kasko sigortasının üçüncü kişilere verilen zararları karşıladığını ve zorunlu trafik sigortasının sigortalının kendi aracındaki maddi zararı karşıladığını iddia etmektedir. Bağlam ise bu iddianın tam tersini belirtmektedir: kasko sigortası sigortalının kendi aracındaki maddi zararları güvence altına alırken, zorunlu trafik sigortası aracın üçüncü kişilere verdiği maddi ve bedensel zararları karşılar."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 02 (Konsensüs): `tfb_ex_0035` — FINANCE
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay, azami ödemesiz dönemi bir yıldır; bu sınırlar işletme kredileriyle aynıdır."*
- **Bağlam (Context):** *"Kefalet Kurumu A Özkaynak Kefalet Programı, uygun KOBİ ve benzeri yararlanıcıların banka kredilerine Kefalet Kurumu A’nın kendi özkaynağından kefalet sağlamasına dayanır. İşletme kredilerinde vade 6 ila 60 ay arasında, ödemesiz dönem en fazla bir yıldır; yatırım kredilerinde vade 6 ila 84 ay arasında ve ödemesiz dönem en fazla iki yıldır. Yararlanıcı veya grup başına kefalet limiti 5 milyon TL, azami kefalet oranı yüzde 80'dir. Başvurular bankalar üzerinden Kefalet Kurumu A’nın elektronik sistemi aracılığıyla yapılır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay', 'label': 'contradiction'}" | "{'atom': 'azami ödemesiz dönemi bir yıldır', 'label': 'contradiction'}" | "{'atom': 'bu sınırlar işletme kredileriyle aynıdır', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan yatırım kredilerinin azami vadesi ve azami ödemesiz dönemi bilgisi bağlamla doğrudan çelişmekte, ayrıca bu sınırların işletme kredileriyle aynı olduğu iddiası da yanlıştır. Bu nedenle iddia tamamen bağlam tarafından çürütülmektedir."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 03 (Konsensüs): `tfb_ex_0115` — FINANCE
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya, borsa dışı tazmin talepleri Borsa A’ya götürülür ve Düzenleyici Kurum A zarar tazminine karar verir."*
- **Bağlam (Context):** *"Sermaye piyasası uyuşmazlığında izlenecek başvuru yolu uyuşmazlığın türüne göre değişebilir. Borsada emirlerin iletilmesi, eşleştirilmesi ve gerçekleşen işlemlere ilişkin yükümlülüklerin yerine getirilmesi gibi borsa işlemlerinden doğan uyuşmazlıklar için Borsa A’ya başvuru yapılabilir. Borsa işlemleri dışındaki zarar ve tazmin talepleri Meslek Birliği A bünyesindeki müşteri uyuşmazlıkları hakem mekanizmasına iletilebilir. Düzenleyici Kurum A ise mevzuata aykırılık iddialarını idari yönden inceleyebilir ancak bu inceleme kapsamında zarar tazminine karar vermez."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya', 'label': 'entailment'}" | "{'atom': 'borsa dışı tazmin talepleri Borsa’ya', 'label': 'entailment'}" | "{'atom': 'zarar tazminine karar verir Düzenleyici Kurum A', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan tüm bilgiler bağlam tarafından doğrudan veya dolaylı olarak çelişmekte ya da bağlamda olmayan bilgiler içermektedir. Model B'nin analizinde görüldüğü gibi, iddianın parçaları bağlamla hem doğrulanabilir hem de çelişen bilgiler içerse de, iddianın genelinde bağlamın doğruladığı doğru bir parça bulunmamaktadır."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 04 (Konsensüs): `tfb_ex_0195` — LEGAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır ve güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir."*
- **Bağlam (Context):** *"Elektrik perakende satışında görevli tedarik şirketi, kullanım yerinin değişmesi veya perakende satış sözleşmesinin sona ermesi ya da feshi halinde tüketim bedelinin ödenmemesi riskine karşı güvence bedeli talep eder. Ön ödemeli sayaç kullanan tüketicilerden, genel aydınlatma kapsamındaki yerlerden ve ilgili düzenlemede belirtilen ibadethanelerden güvence bedeli alınmaz. Perakende satış sözleşmesi sona erdiğinde, feshedildiğinde veya tüketici ön ödemeli sayaca geçtiğinde güvence bedeli iade edilir. Tüketicinin borçları ödendikten sonra kalan tutar, talep tarihinden itibaren en geç beş iş günü içinde iade edilir. İade için borcun ödenmesi dışında başka bir şart veya belge istenemez."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır', 'label': 'entailment'}" | "{'atom': 'güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan 'Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır' ifadesi bağlam tarafından doğrudan çelişmekte, 'güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir' ifadesi ise bağlamda yer almayan ve çelişen bir bilgi olarak görülmektedir. Model B, her iki atomu ayrı ayrı değerlendirmiş ve doğru bir şekilde birini doğrulama diğerini çelişki olarak belirlemiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 05 (Konsensüs): `tfb_ex_0232` — LEGAL
- **Başarısızlık Kategorisi:** Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `contradicted`
- **K1 (ELECTRA) Kararı:** `contradicted`
- **K2 (Gemma+mDeBERTa) Kararı:** `contradicted`
- **İddia (Claim):** *"Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir ve daha önce tevzi edilen dosyalar yeniden dağıtılır."*
- **Bağlam (Context):** *"Arabuluculuk bürolarının dava şartı kapsamındaki yazışmalarında elektronik tebligat kanalı kullanılmasına yönelik yeni uygulamada, arabulucuların elektronik tebligat adresine sahip olması istenmiştir. Duyuruda bu adreslerin 23 Temmuz 2026 tarihine kadar tebligat yapılabilecek biçimde hazır olması gerektiği belirtilmiştir. Bu tarihten itibaren büro yazışmalarının elektronik tebligat adresi üzerinden yürütülmesi öngörülmüş; elektronik tebligat adresi bulunmayan arabuluculara dava şartı arabuluculuk kapsamında dosya tevzi edilmemesi ve kayıtlarının aktif durumdan çıkarılması bildirilmiştir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir', 'label': 'contradiction'}" | "{'atom': 'daha önce tevzi edilen dosyalar yeniden dağıtılır', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan her iki önerme de (pasif kaydın aktif hâle gelmesi ve dosyaların yeniden dağıtılması) bağlam tarafından doğrudan doğrulanmamaktadır ve açıkça çelişmektedir. Model B, her iki atomu da ayrı ayrı değerlendirmiş ve her ikisinin de çelişki içerdiğini doğru olarak tespit etmiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 06 (Konsensüs): `tfb_ex_0274` — LEGAL
- **Başarısızlık Kategorisi:** Cat-5: Halüsinasyon Körlüğü (Yanlış Parçayı Kaçırıp Destekleniyor Sanma)
- **Altın Etiket (Doğru):** `partially_supported`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `supported`
- **K1 (ELECTRA) Kararı:** `supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `supported`
- **İddia (Claim):** *"Satışa engel hukuki durum varsa noter işlemi yapmaz. Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz."*
- **Bağlam (Context):** *"Noter, taşınmaz satış başvurusu üzerine bir başvuru belgesi düzenler ve taşınmaz üzerindeki kısıtlamalar ile satışa ilişkin yasal sınırlamaları inceler. Hak sahibinin belirlenememesi veya satışa engel hukuki bir durum bulunması hâlinde satış işlemi yapılmaz. Satışa engel durum olmadığı tespit edilirse sözleşme taraflarca imzalanır. Noter, tapu bilişim sisteminden yevmiye numarası alarak sözleşmeyi sisteme kaydeder; kaydın ardından tapu müdürlüğü taşınmazın tapu siciline tescilini sağlar."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Satışa engel hukuki durum varsa noter işlemi yapmaz.', 'label': 'entailment'}" | "{'atom': 'Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz.', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada 'satışa engel hukuki durum varsa noter işlemi yapmaz' ifadesi bağlam tarafından doğrulanırken, 'sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz' ifadesi bağlamda bulunmamaktadır. Model B, her iki atomu ayrı ayrı değerlendirmiş ve doğru kararı vermiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 07 (Konsensüs): `tfb_ex_0278` — LEGAL
- **Başarısızlık Kategorisi:** Cat-5: Halüsinasyon Körlüğü (Yanlış Parçayı Kaçırıp Destekleniyor Sanma)
- **Altın Etiket (Doğru):** `partially_supported`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `supported`
- **K1 (ELECTRA) Kararı:** `supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `supported`
- **İddia (Claim):** *"Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur, adli sicil belgesini de adayın dilekçesine eklemesi gerekir."*
- **Bağlam (Context):** *"Denetimli serbestlik hizmetlerinde gönüllü çalışmak isteyen kişinin Türk vatandaşı olması, başvuru tarihinde on sekiz yaşını tamamlamış bulunması ve mevzuatta belirtilen belirli suçlardan hükümlü olmaması gerekir. Gönüllü olmak isteyen kişi denetimli serbestlik müdürlüğüne dilekçe ile başvurur. Başvuruda gönüllü başvuru formu ve yerleşim yeri belgesi istenir; adli sicil belgesi müdürlük tarafından temin edilir. Başvuru, infaz işlemleri değerlendirme komisyonu tarafından incelenerek karara bağlanır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur', 'label': 'entailment'}" | "{'atom': 'adli sicil belgesini de adayın dilekçesine eklemesi gerekir', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada 'başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur' ifadesi bağlam tarafından doğrulanırken, 'adli sicil belgesini de adayın dilekçesine eklemesi gerekir' ifadesi bağlamda yanlış olarak sunulmuştur, çünkü adli sicil belgesi müdürlük tarafından temin edilir. Model B, her iki atomu ayrı ayrı değerlendirdiği için daha doğru bir analiz sunmuştur."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 08 (Konsensüs): `tfb_ex_0323` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar. Sinir iletim ölçümü ikinci aşamadadır ve iki bölüm bütün hastalara uygulanır."*
- **Bağlam (Context):** *"Elektromiyografi (EMG), sinir ve kasların elektriksel yöntemlerle değerlendirildiği bir incelemedir. İlk bölümde düşük şiddette elektrik uyarıları kullanılarak sinirlerin iletim fonksiyonları ölçülebilir. Gerekli hastalarda ikinci bölümde tek kullanımlık ince iğne elektrotlarla kaslar ve bu kaslara gelen sinirler değerlendirilir; her hastada iki bölümün birden yapılması zorunlu değildir. İncelemenin süresi hastaya ve istenen değerlendirmeye göre değişmekle birlikte yaklaşık yarım saat olabilir. Düzenli ilaçlar genellikle sürdürülebilir, ancak kan sulandırıcı kullananların ve kalp pili ya da başka bir pil taşıyanların hekimi önceden bilgilendirmesi önerilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar', 'label': 'contradiction'}" | "{'atom': 'Sinir iletim ölçümü ikinci aşamadadır', 'label': 'entailment'}" | "{'atom': 'EMG değerlendirmesi bütün hastalara uygulanır', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan 'EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar' ve 'iki bölüm bütün hastalara uygulanır' ifadeleri bağlam tarafından doğrudan çelişmekte, sadece 'Sinir iletim ölçümü ikinci aşamadadır' ifadesi desteklenmektedir. Model B, her bir atomu ayrı ayrı değerlendirdiği için daha doğru bir analiz sunmaktadır."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 09 (Konsensüs): `tfb_ex_0332` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-6: Diğer Sınır Vakaları (unverifiable -> supported)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `supported`
- **K1 (ELECTRA) Kararı:** `supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `supported`
- **İddia (Claim):** *"Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır."*
- **Bağlam (Context):** *"PET/CT işlemi öncesinde hastanın en az altı saat aç kalması gerekir. İşleme başlanırken kan şekeri ölçülür; değer uygun aralıktaysa damar yoluyla radyoaktif işaretli madde verilir. Sık kullanılan maddelerden biri F-18 florodeoksiglukozdur. Enjeksiyonun ardından maddenin vücutta dağılması için hasta yaklaşık bir saat bekletilir ve daha sonra PET/CT cihazında görüntüleme yapılır. PET/CT, kanserin yaygınlığını değerlendirmede, canlı tümör dokusunun yerini göstermede ve gerektiğinde biyopsi alınacak bölgenin belirlenmesine yardımcı olmada kullanılabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır.', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"Bağlamda biyopsi alınacak bölgenin seçilmesinde kan şekeri sonucunun dikkate alınıp alınmadığına dair hiçbir bilgi bulunmamaktadır. Bu nedenle iddia doğrulanamaz."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 10 (Konsensüs): `tfb_ex_0336` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır. Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır."*
- **Bağlam (Context):** *"Bronkoskopi öncesinde kullanılan ilaçlar, mevcut hastalıklar ve ilaç alerjileri hekime bildirilmelidir. İşlemden altı ila sekiz saat önce yiyecek ve içecek alınmaması gerekir; sürekli kullanılan bazı ilaçlar hekimin yönlendirmesiyle az miktarda suyla alınabilir. Bronkoskop ağız veya burundan ilerletilerek hava yolları incelenir, gerekli olduğunda biyopsi alınabilir veya yıkama sıvısı toplanabilir. İşlem sonrasında hasta en az bir ila iki saat gözlem altında tutulur ve yutma refleksi zayıfladığı için yaklaşık iki saat yiyecek ve içecek verilmez. Anestezi etkisi nedeniyle en az on iki saat araç veya iş makinesi kullanılması ve alkol alınması önerilmez."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır.', 'label': 'entailment'}" | "{'atom': 'Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır.', 'label': 'neutral'}"
- **Hakemin Değerlendirmesi:** *"İddiada biyopsi alınan hastaların gözlem süresinin iki saate çıkarıldığı bilgisi bağlam tarafından doğrulanırken, yıkama örneği alınmışsa gözlem süresinin bir saatte sonlandırıldığı bilgisi bağlamda bulunmamaktadır. Model B, her iki atomu ayrı ayrı değerlendirmesi nedeniyle daha doğru bir analiz sunmaktadır."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 11 (Konsensüs): `tfb_ex_0340` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır. Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır."*
- **Bağlam (Context):** *"Kolonoskopinin tam ve güvenilir yapılabilmesi için altı saatlik açlığın yanında iki ila üç günlük diyet ve özel ilaçlarla bağırsak temizliği gerekir. İşlem sırasında hasta sol yanına yatırılır; kalp ritmi ve kandaki oksijen miktarı izlenir. Karında basınç, gaz ve kramp görülebileceği için işlem öncesinde veya gerektiğinde işlem sırasında sakinleştirici ve ağrı azaltıcı ilaçlar uygulanabilir. Kolonoskopi yaklaşık yirmi ila otuz dakika sürebilir. İşlemden sonra hasta on beş ila otuz dakika dinlendirilir; ilaç kullanılmışsa güvenlik amacıyla yirmi dört saat taşıt veya makine kullanılmaması önerilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır.', 'label': 'entailment'}" | "{'atom': 'Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır.', 'label': 'neutral'}"
- **Hakemin Değerlendirmesi:** *"İddiada, kolonoskopi sonrası dinlenme süresinin sakinleştirici ilaçla ilişkisi bağlam tarafından doğrulanırken, ağrı azaltıcı ilaç kullanımı ve dinlenme süresinin uzatılması konusunda bağlamda bilgi bulunmamaktadır. Model B, her iki atomu ayrı ayrı değerlendirmesi ve doğru olanı desteklemesi nedeniyle daha doğru bir analiz sunmaktadır."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 12 (Konsensüs): `tfb_ex_0360` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `contradicted`
- **K1 (ELECTRA) Kararı:** `contradicted`
- **K2 (Gemma+mDeBERTa) Kararı:** `contradicted`
- **İddia (Claim):** *"Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır. Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir."*
- **Bağlam (Context):** *"Bilgisayarlı tomografi ilaçlı veya ilaçsız yapılabilir. İlaçlı incelemede kontrast madde damar yoluyla verilebilir veya suya karıştırılarak hastaya içirilebilir. Özel bir hazırlık talimatı verilmemişse her çekim için aynı hazırlık gerekmez; ilaçlı çekimlerde açlık istenebilir ve bazı incelemelerde hastadan belirli miktarda suyla erken başvurması istenir. Çekim bölgesindeki takı ve metal eşyalar çıkarılır. İnceleme sırasında hasta hareketli bir masa üzerinde halka biçimli tarayıcıdan geçirilir ve bazen nefes komutlarına uyması istenir. İşlem süresi tetkike göre değişmekle birlikte yaklaşık bir ila on dakika arasında olabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır', 'label': 'contradiction'}" | "{'atom': 'Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir', 'label': 'neutral'}"
- **Hakemin Değerlendirmesi:** *"İddiada 'Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır' ifadesi bağlam tarafından doğrulanırken, 'Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir' ifadesi bağlamda doğrudan doğrulanmamaktadır. Model B, her iki atomu ayrı ayrı değerlendirdiği için daha doğru bir analiz sunmaktadır."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 13 (Konsensüs): `tfb_ex_0363` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"MR çekim odasına metal eşyalarla girilebilir ve çekim sırasında hareket etmek görüntülemeyi etkilemez."*
- **Bağlam (Context):** *"Manyetik rezonans incelemelerinin çoğunda özel bir ön hazırlık gerekmez; aksi söylenmedikçe hasta yemek yiyip düzenli ilaçlarını alabilir. Ancak bazı özellikli çekimlerde hazırlık değişir. Örneğin entero incelemesinde hastadan aç gelmesi ve hazırlanan yaklaşık bir buçuk litre suyu iki saat içinde içmesi, bazı batın ve ilaçlı incelemelerde ise en az sekiz saat açlık istenebilir. Güçlü manyetik alan nedeniyle saat, takı, kredi kartı, işitme cihazı ve benzeri metal ya da manyetik alandan etkilenebilecek eşyalar çekim odasına girmeden çıkarılmalıdır. Vücutta implant, kalp pili, metal parça veya benzeri bir materyal varsa görevliye önceden bildirilir. Çekim sırasında hasta hareketsiz kalır; cihazın gürültüsü için kulak koruyucu verilebilir ve görevliyle mikrofon üzerinden iletişim kurulabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'MR çekim odasına metal eşyalarla girilebilir.', 'label': 'entailment'}" | "{'atom': 'MR çekim sırasında hareket etmek görüntülemeyi etkilemez.', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan her iki önerme de bağlam tarafından doğrudan çelişmekte veya desteklenmemektedir. Model A ve Model B'nin partially_supported kararı hatalıdır çünkü iddia edilen her iki durum da bağlamda açıkça yasaklanmıştır."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 14 (Konsensüs): `tfb_ex_0364` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir. Bu bilgi olmadan çekim planı oluşturulmaz."*
- **Bağlam (Context):** *"Manyetik rezonans incelemelerinin çoğunda özel bir ön hazırlık gerekmez; aksi söylenmedikçe hasta yemek yiyip düzenli ilaçlarını alabilir. Ancak bazı özellikli çekimlerde hazırlık değişir. Örneğin entero incelemesinde hastadan aç gelmesi ve hazırlanan yaklaşık bir buçuk litre suyu iki saat içinde içmesi, bazı batın ve ilaçlı incelemelerde ise en az sekiz saat açlık istenebilir. Güçlü manyetik alan nedeniyle saat, takı, kredi kartı, işitme cihazı ve benzeri metal ya da manyetik alandan etkilenebilecek eşyalar çekim odasına girmeden çıkarılmalıdır. Vücutta implant, kalp pili, metal parça veya benzeri bir materyal varsa görevliye önceden bildirilir. Çekim sırasında hasta hareketsiz kalır; cihazın gürültüsü için kulak koruyucu verilebilir ve görevliyle mikrofon üzerinden iletişim kurulabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir.', 'label': 'neutral'}" | "{'atom': 'Bu bilgi olmadan çekim planı oluşturulmaz.', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada 'Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir' ifadesi bağlamda doğrudan doğrulanmamaktadır, ancak 'Bu bilgi olmadan çekim planı oluşturulmaz' ifadesi bağlamın ima ettiği güvenlik önlemlerine uygun olarak değerlendirilebilir. Model B, her iki atomu ayrı ayrı değerlendirdiği için daha doğru bir analiz sunmaktadır."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 15 (Konsensüs): `tfb_ex_0368` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `contradicted`
- **K1 (ELECTRA) Kararı:** `contradicted`
- **K2 (Gemma+mDeBERTa) Kararı:** `contradicted`
- **İddia (Claim):** *"Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır ve meme kısa süre sıkıştırılır."*
- **Bağlam (Context):** *"Mamografi çekimine gelmeden önce koltuk altı temizliği yapılması ve duş alınması önerilir. Koltukaltı ve göğüs bölgesine parfüm, deodorant veya benzeri ürünler uygulanmamalı; daha önce yapılmış meme görüntülemeleri varsa bunlar da beraberinde getirilmelidir. Çekim sırasında meme iki plastik tabaka arasında sıkıştırılır ve genellikle iki farklı pozisyonda görüntü alınır. Sıkıştırmanın amacı hareketi azaltmak, görüntüyü keskinleştirmek ve daha düşük doz radyasyonla görüntü elde edilmesine yardımcı olmaktır. Uygulanan baskı kısa süreli ağrı veya rahatsızlık oluşturabilir, ancak bu his genellikle çekim bittikten sonra geçer."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır', 'label': 'contradiction'}" | "{'atom': 'meme kısa süre sıkıştırılır', 'label': 'neutral'}"
- **Hakemin Değerlendirmesi:** *"İddiada 'meme kısa süre sıkıştırılır' ifadesi bağlam tarafından doğrulanırken, 'çekime eski görüntüyle aynı pozisyondan başlanır' ifadesi bağlamda yer almadığı için kısmen desteklenmektedir. Model B, iddiayı atomik olarak analiz ederek doğru ve yanlış parçaları ayırt etmiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 16 (Konsensüs): `tfb_ex_0372` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `contradicted`
- **K1 (ELECTRA) Kararı:** `contradicted`
- **K2 (Gemma+mDeBERTa) Kararı:** `contradicted`
- **İddia (Claim):** *"Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir. Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir."*
- **Bağlam (Context):** *"Gastroskopi yemek borusu, mide ve onikiparmak bağırsağının incelenmesinde kullanılır. İnceleme sırasında görüntü alınabilir ve gerekli görülen alanlardan biyopsi örneği alınarak patolojiye gönderilebilir. İşlem için yaklaşık sekiz saat açlık gerekir. Rahatsızlığı azaltmak amacıyla boğaza uyuşturucu sprey uygulanabilir ve sakinleştirici ilaç verilebilir. Gastroskopi çoğu durumda yaklaşık beş ila on dakika sürer. İşlem sonrasında hasta bir ila iki saat izlenebilir; ardından sıvı gıdalara başlanıp aynı gün taburculuk yapılabilir. Gastroskopi yalnız tanı amacıyla değil, bazı kanamaların kontrolü, polip çıkarılması, daralmış bölgelerin genişletilmesi veya yabancı cisim çıkarılması gibi tedavi amaçlı işlemlerde de kullanılabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir.', 'label': 'neutral'}" | "{'atom': 'Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir.', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan 'Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir' ifadesi bağlamda bulunmamaktadır ve 'Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir' ifadesi de bağlam tarafından doğrulanmamaktadır. Model B, her iki atomu da ayrı ayrı değerlendirmiş ve doğru kararı vermiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 17 (Konsensüs): `tfb_ex_0405` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-6: Diğer Sınır Vakaları (supported -> partially_supported)
- **Altın Etiket (Doğru):** `supported`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır. Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir."*
- **Bağlam (Context):** *"DEXA, kemik mineral yoğunluğunu ve kemik kaybını değerlendirmek için kullanılan düşük radyasyonlu bir ölçümdür. Ölçümde sıklıkla bel omurları ile kalça bölgesi değerlendirilir. Genel olarak özel bir ön hazırlık gerekmez; hasta yaklaşık on beş dakika yatar ve ölçümün tamamlanması için hareketsiz kalır. İşlem ağrısızdır. Gebelik veya emzirme durumu sağlık ekibine önceden bildirilmelidir. İncelemeden iki ile altı gün önce ağızdan ya da damar yoluyla kontrast madde kullanılmışsa DEXA çekimi ertelenebilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır.', 'label': 'contradiction'}" | "{'atom': 'Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir.', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada doğru bir bilgi (kontrast madde kullanımı sonrası erteleme) ve bağlamla çelişen bir bilgi (hasta yatarak geçirdiği süre) bir arada bulunmaktadır. Model B, her iki atomu da ayrı ayrı değerlendirmiş ve doğru kararı vermiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 18 (Konsensüs): `tfb_ex_0423` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"ERCP sırasında görüntüleme için kontrast mesaneye verilir ve işlem sedoanaljezi olmadan tamamlanır."*
- **Bağlam (Context):** *"ERCP, safra yolları ve pankreas kanalının tanı ve tedavisinde kullanılan özel bir endoskopi yöntemidir. Duodenoskop ağızdan ilerletilerek onikiparmak bağırsağına ulaştırılır; papilla üzerinden ince kateterlerle safra kanalına, gerektiğinde pankreas kanalına kontrast madde verilir ve X ışınıyla görüntüleme yapılır. Aynı seansta safra yolu taşının çıkarılması, darlığın balon veya stentle giderilmesi gibi tedaviler uygulanabilir. İşlemden önce en az altı-sekiz saat açlık gerekir; kan sulandırıcı ilaçlar ve ilaç alerjileri hekime bildirilir. Damar yolu açılıp sedoanaljezi uygulanır. İşlem genellikle otuz-altmış dakika sürer."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'ERCP sırasında görüntüleme için kontrast mesaneye verilir', 'label': 'entailment'}" | "{'atom': 'ERCP işlemi sedoanaljezi olmadan tamamlanır', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan 'kontrast mesaneye verilir' ve 'sedoanaljezi olmadan tamamlanır' ifadeleri bağlam tarafından doğrudan çelişmekte ve yalanlanmaktadır. Model B, her iki atomu da doğru şekilde analiz etmiş ve biri doğrudan çelişki içerdiğinden contradicted kararı verilmesi gerektiği sonucuna varmıştır."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 19 (Konsensüs): `tfb_ex_0452` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"Prob yemek borusunda belirli bir işarete kadar ilerletilir. Bu noktadan ek görüntü alınır."*
- **Bağlam (Context):** *"Transözofageal ekokardiyografi, göğüsten yapılan ekokardiyografide yeterince görüntülenemeyen kalp yapılarını yemek borusundan ilerletilen ultrason probuyla incelemek için kullanılır. İşlem öncesinde en az dört saat açlık gerekir ve çıkarılabilir diş protezleri çıkarılır. Boğaza lokal anestezik sprey uygulanır, damar yolu açılır ve ağızlık yerleştirildikten sonra prob yutkunma yardımıyla yemek borusuna ilerletilir. İnceleme yaklaşık 15-20 dakika sürer. İşlemden sonra iki saat boyunca bir şey yenilip içilmez."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Prob yemek borusunda belirli bir işarete kadar ilerletilir.', 'label': 'neutral'}" | "{'atom': 'Bu noktadan ek görüntü alınır.', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada 'prob yemek borusunda belirli bir işarete kadar ilerletilir' ifadesi bağlamda doğrudan doğrulanmamıştır, ancak 'bu noktadan ek görüntü alınır' ifadesi bağlamın işlemin amacı ile örtüşmektedir. Model B, iddiayı atomik olarak analiz etmiş ve daha doğru bir karar vermiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Hayır, Hakem de Yanılırdı

---

#### Vaka 20 (Konsensüs): `tfb_ex_0463` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `partially_supported`
- **K1 (ELECTRA) Kararı:** `partially_supported`
- **K2 (Gemma+mDeBERTa) Kararı:** `partially_supported`
- **İddia (Claim):** *"UVA riboflavinden önce uygulanır. Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır."*
- **Bağlam (Context):** *"Korneal cross-linking, ilerleme saptanan keratokonusta kornea dokusunu güçlendirmek için riboflavin ve ultraviyole A kullanılan bir işlemdir. Damla anestezisiyle göz uyuşturulduktan sonra korneanın epitel tabakası kaldırılır. Riboflavin solüsyonu 30 dakika boyunca beş dakikada bir damlatılır; ardından korneaya yaklaşık 30 dakika UVA uygulanırken riboflavin damlatılmaya devam edilir. İşlem sonunda göz antibiyotikli pomatla kapatılır ve ortalama iyileşme süreci yaklaşık iki gündür."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'UVA riboflavinden önce uygulanır', 'label': 'contradiction'}" | "{'atom': 'Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır', 'label': 'entailment'}"
- **Hakemin Değerlendirmesi:** *"İddiada yer alan 'UVA riboflavinden önce uygulanır' ifadesi bağlam tarafından doğrudan çelişmekte, 'Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır' ifadesi ise bağlam tarafından doğrulanmaktadır. Model B, her iki atomu ayrı ayrı değerlendirmiş ve doğru sonuçları üretmiştir."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

#### Vaka 21 (Konsensüs): `tfb_ex_0468` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Sistemin Yanlış Kararı (K1 & K2 Konsensüsü):** `contradicted`
- **K1 (ELECTRA) Kararı:** `contradicted`
- **K2 (Gemma+mDeBERTa) Kararı:** `contradicted`
- **İddia (Claim):** *"İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir."*
- **Bağlam (Context):** *"Endoskopik ultrasonografi, endoskopi ile ultrasonografiyi aynı cihazda birleştirerek sindirim sisteminin iç yüzeyinin yanında duvar katmanlarını ve çevredeki lenf bezleri ile komşu organları incelemeyi sağlar. Endoskop ağızdan yemek borusu, mide ve ince bağırsağa doğru ilerletilir; işlem sırasında endoskopik görüntüler ile ultrason görüntüleri ayrı ekranlardan izlenir. Şüpheli bir doku görüldüğünde cihazdan ilerletilen iğneyle biyopsi örneği alınabilir. İşlem çoğunlukla sedasyon altında yapılır ve yaklaşık 20-30 dakika sürer."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir', 'label': 'contradiction'}"
- **Hakemin Değerlendirmesi:** *"Bağlamda biyopsi örneğinin cihazın ayrı bir kanalında incelenip incelenmediğine dair hiçbir bilgi bulunmamaktadır. Her iki modelin de contradicted kararı vermesi hatalıdır, çünkü bağlamda doğrudan bir çelişki veya doğrulama yoktur."*
- **Hakem Olsaydı Düzeltir miydi?:** Evet, Hakem Doğruyu Bulabilirdi

---

### 3.2. Hakem Arbitrasyon Hataları (23 Vaka: Hakem != Altın Etiket)
Bu vakalarda K1 ve K2 modelleri uyuşmazlığa düşmüş (`K1 != K2`) ve Baş Hakem (Llama-3.3-70B) devreye girmiştir. Ancak Hakem, modellerin analizlerini değerlendirirken yanlış modeli tercih etmiş veya yanlış nihai karar vermiştir.

#### Vaka 01 (Hakem): `tfb_ex_0020` — FINANCE
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Sektör Birliği A’nın kasko sınıflandırmasında Tam Kasko priminde ek sözleşmeyle alınabilecek risklerin sayısı esas alınır' ifadesi bağlam tarafından doğrulanmaktadır. Ancak 'risk sayısı arttıkça ortak bir katsayı uygulanır' ifadesine ilişkin bağlamda herhangi bir bilgi bulunmamaktadır."*
- **İddia (Claim):** *"Sektör Birliği A’nın kasko sınıflandırmasında Tam Kasko priminde ek sözleşmeyle alınabilecek risklerin sayısı esas alınır ve risk sayısı arttıkça ortak bir katsayı uygulanır."*
- **Bağlam (Context):** *"Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının tamamına ek olarak ek sözleşmeyle alınabilecek risklerin bir bölümünü; Tam Kasko ise bu ek risklerin tamamını kapsar. Kasko sigortalının kendi aracındaki maddi zararları güvence altına alırken zorunlu trafik sigortası aracın üçüncü kişilere verdiği maddi ve bedensel zararları karşılar."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Sektör Birliği A’nın kasko sınıflandırmasında Tam Kasko priminde ek sözleşmeyle alınabilecek risklerin sayısı esas alınır', 'label': 'entailment'}" | "{'atom': 'risk sayısı arttıkça ortak bir katsayı uygulanır', 'label': 'neutral'}"

---

#### Vaka 02 (Hakem): `tfb_ex_0040` — FINANCE
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Katılım endekslerinin kapsamı şirketlerin katılım esaslarına uygunluk değerlendirmesine göre güncellenir' ifadesi bağlam tarafından doğrulanmaktadır. Ancak, 'bu değerlendirme sonuçları dönemsel olarak Piyasa Kurumu A tarafından yayımlanır' ifadesine ilişkin bağlamda yeterli bilgi bulunmamaktadır."*
- **İddia (Claim):** *"Katılım endekslerinin kapsamı şirketlerin katılım esaslarına uygunluk değerlendirmesine göre güncellenir ve bu değerlendirme sonuçları dönemsel olarak Piyasa Kurumu A tarafından yayımlanır."*
- **Bağlam (Context):** *"Sektör Birliği A’nın sektörel zaman çizelgesinde, Piyasa Kurumu A’nın 9 Kasım 2021 tarihli duyurusu sonrasında Katılım Tüm, Katılım 100, Katılım 50, Katılım 30 ve Sürdürülebilirlik Katılım endekslerinin 12 Kasım 2021'den itibaren Piyasa Kurumu A tarafından hesaplanmasına karar verildiği belirtilir. Aynı kayıtta, kira sertifikalarının işlem gördüğü Taahhütlü İşlemler Pazarı'nın 2 Ağustos 2018'de faaliyete geçtiği ve bunun Türkiye'de katılım esaslı repo ve ters repo pazarını oluşturduğu aktarılır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Katılım endekslerinin kapsamı şirketlerin katılım esaslarına uygunluk değerlendirmesine göre güncellenir', 'label': 'entailment'}" | "{'atom': 'Bu değerlendirme sonuçları dönemsel olarak Piyasa Kurumu A tarafından yayımlanır', 'label': 'neutral'}"

---

#### Vaka 03 (Hakem): `tfb_ex_0048` — FINANCE
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Bildirim Sistemi A'da Şüpheli İşlem Bildirim modülünden gönderilen bildirimler elektronik tebligat ekranında aynı kayıt numarasıyla izlenir' ifadesi bağlamda doğrudan doğrulanmamıştır, ancak 'yükümlü raporları' ile ilgili bilgi bağlamda mevcuttur. Model B, iddiayı atomlara ayırarak kısmi desteği doğru bir şekilde belirlemiştir."*
- **İddia (Claim):** *"Bildirim Sistemi A'da Şüpheli İşlem Bildirim modülünden gönderilen bildirimler elektronik tebligat ekranında aynı kayıt numarasıyla izlenir ve yükümlü raporları bu kayda bağlanır."*
- **Bağlam (Context):** *"Bildirim Sistemi A, şüpheli işlem bildirimlerinin iletilmesi, elektronik tebligat işlemleri ve yükümlülere sunulan raporlar için kullanılan güvenli bir çevrim içi uygulama ve iletişim kanalıdır. Bildirim Sistemi A ile sistemin erişim güvenliği artırılmış, farklı sektörlerin ihtiyaçlarına göre esnek ve özelleştirilebilir yapılar oluşturulmuş ve Şüpheli İşlem Bildirim modülü devreye alınmıştır. Elektronik tebligat işlemleri de Bildirim Sistemi A üzerinden tüm yükümlü grupları için kullanılabilir durumdadır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': "Bildirim Sistemi A'da Şüpheli İşlem Bildirim modülünden gönderilen bildirimler elektronik tebligat ekranında aynı kayıt numarasıyla izlenir", 'label': 'neutral'}" | "{'atom': 'yükümlü raporları bu kayda bağlanır', 'label': 'entailment'}"

---

#### Vaka 04 (Hakem): `tfb_ex_0079` — FINANCE
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada Ankara'da bir yeni depo faaliyete alınmıştır ifadesi bağlam tarafından doğrulanırken, İzmir'de dört yeni depo faaliyete alınmıştır ifadesi bağlamla doğrudan çelişmektedir. Model B'nin atomik analizinin bu ayrımı doğru bir şekilde yansıttığı görülmektedir."*
- **İddia (Claim):** *"2025 yılında Nakit yönetimi projesi kapsamında Ankara'da bir, İzmir'de dört yeni depo faaliyete alınmıştır."*
- **Bağlam (Context):** *"Nakit yönetimi projesi kapsamında, Türk lirası tedavülünün kesintisiz sağlanması amacıyla Merkez Bankası A adına banknot saklama ve işleme faaliyetleri yürütülür. Proje kapsamında 2025 yılında Ankara'da dört, İstanbul ve Antalya'da ikişer, İzmir ve Adana'da birer yeni nakit yönetimi deposu faaliyete alınmıştır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': "2025 yılında Nakit yönetimi projesi kapsamında Ankara'da bir yeni depo faaliyete alınmıştır.", 'label': 'entailment'}" | "{'atom': "2025 yılında Nakit yönetimi projesi kapsamında İzmir'de dört yeni depo faaliyete alınmıştır.", 'label': 'contradiction'}"

---

#### Vaka 05 (Hakem): `tfb_ex_0091` — FINANCE
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada iki farklı iddia bulunmaktadır: 'Sorgu için mirasçılık ilişkisinin doğrulanması gerekmez' ve 'Hizmet hesap bakiyesini ve şube bilgisini ayrıntılı biçimde gösterir'. Bağlam, ilk iddianın yanlış olduğunu (mirasçılık ilişkisi doğrulanır) ve ikinci iddianın doğru olduğunu (hizmet hesap bakiyesi ve şube bilgisini göstermez, ilgili bankaya başvurulması gerekir) belirtmektedir. Model B, bu durumu doğru bir şekilde partially_supported olarak değerlendirmiştir."*
- **İddia (Claim):** *"Sorgu için mirasçılık ilişkisinin doğrulanması gerekmez. Hizmet hesap bakiyesini ve şube bilgisini ayrıntılı biçimde gösterir."*
- **Bağlam (Context):** *"Mirasçılık belgesi bulunan bir kişi, vefat eden kişinin hangi bankalarda mevduat veya katılım fonu hesabı bulunduğunu elektronik kamu hizmeti üzerinden sorgulayabilir. Sorgudan önce mirasçılık ilişkisi, belgenin alındığı adli makam veya noterlik sistemi üzerinden doğrulanır. Hizmet, hesap bulunan bankaları gösterir; hesap bakiyesi ve hesabın hangi şubede bulunduğu gibi ayrıntılar için ilgili bankaya başvurulması gerekir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Sorgu için mirasçılık ilişkisinin doğrulanması gerekmez.', 'label': 'contradiction'}" | "{'atom': 'Hizmet hesap bakiyesini ve şube bilgisini ayrıntılı biçimde gösterir.', 'label': 'entailment'}"

---

#### Vaka 06 (Hakem): `tfb_ex_0096` — FINANCE
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada günlük bildirim seçildiğinde alış ve satış mesajlarının birleştirilmesi doğru gibi görünse de, bağlamda bu bilgi açıkça doğrulanmamaktadır. Rehin bildirimlerinin ayrı gönderilmesi ise bağlamda doğrudan doğrulanmamaktadır, bu nedenle Model B'nin atomik analizinin daha doğru olduğu görülmektedir."*
- **İddia (Claim):** *"Günlük bildirim seçildiğinde alış ve satış mesajları tek bildirimde birleştirilir. Rehin bildirimleri ayrı gönderilir."*
- **Bağlam (Context):** *"Merkezi Saklama Kuruluşu A tarafından sunulan bildirim hizmetinde yatırımcı, hesabındaki menkul kıymet işlemleri için SMS veya e-posta bildirimi alabilir. Bildirimler anlık, günlük ya da haftalık periyotlarda seçilebilir ve hizmet ücretsizdir. Alış, satış, transfer, rehin ve haciz gibi işlem türleri bildirim kapsamına girebilir. Bildirim tercihleri Yatırımcı Uygulaması A içindeki bildirim ayarlarından yönetilir. Başkasına ait hesapta rehin edilen pay senedi işlemlerinde ise bildirim hizmetine üyelik zorunludur."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Günlük bildirim seçildiğinde alış ve satış mesajları tek bildirimde birleştirilir.', 'label': 'entailment'}" | "{'atom': 'Rehin bildirimleri ayrı gönderilir.', 'label': 'neutral'}"

---

#### Vaka 07 (Hakem): `tfb_ex_0104` — FINANCE
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada tüzel kişilerin uzaktan müşteri olabileceği bilgisi bağlam tarafından doğrulanmaktadır, ancak belirli sektörlerle sınırlı olduğuna dair bir bilgi bağlamda bulunmamaktadır. Model B'nin atomik analizi, tüzel kişilerin uzaktan müşteri olabileceğini doğrularken, belirli sektörlerle sınırlı olma koşulunu nötr olarak değerlendirmesi doğru bir yaklaşım olup, bu durum partially_supported etiketini gerektirmektedir."*
- **İddia (Claim):** *"Tüzel kişiler uzaktan müşteri olurken yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır."*
- **Bağlam (Context):** *"Bankaların uzaktan kimlik tespiti yoluyla müşteri edinmesine ilişkin düzenleme 1 Mayıs 2021’de yürürlüğe girdi ve başlangıçta T.C. Kimlik Kartına sahip gerçek kişiler ile gerçek kişi tacirlerin uzaktan müşteri olmasına imkân verdi. Daha sonra yapılan değişiklikle tüzel kişilerin de uzaktan müşteri edinimi yoluyla banka müşterisi olabilmesinin önü açıldı. Böylece müşteri ilişkisinin kurulması için her durumda banka şubesine fiziksel olarak gidilmesi zorunlu değildir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Tüzel kişiler uzaktan müşteri olurken', 'label': 'entailment'}" | "{'atom': 'yalnız belirli sektörlerde faaliyet gösteriyorsa kapsama alınır', 'label': 'neutral'}"

---

#### Vaka 08 (Hakem): `tfb_ex_0175` — LEGAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada iki farklı önerme bulunmaktadır: 'Güvenli elektronik imzalı metinle fesih talebi iletilemez' ve 'İşletmeci talebin alındığını en geç yedi gün içinde bildirmekle yükümlüdür'. Bağlam, ilk önermenin yanlış olduğunu (güvenli elektronik imzalı metinle fesih talebi iletilebileceğini) ve ikinci önermenin doğru olduğunu (işletmeci talebin alındığını en geç yirmi dört saat içinde bildirmekle yükümlüdür, ancak bu durum farklı bir zaman dilimine işaret etse de, işletmeci tarafından bir bildirim yapıldığını doğrulamaktadır) göstermektedir. Model B, bu durumu doğru bir şekilde analiz etmiş ve kısmen desteklenen bir iddia olduğunu belirtmiştir."*
- **İddia (Claim):** *"Güvenli elektronik imzalı metinle fesih talebi iletilemez ve işletmeci talebin alındığını en geç yedi gün içinde bildirmekle yükümlüdür."*
- **Bağlam (Context):** *"İnternet aboneliğinin feshi için abone, işletmeciye yazılı başvuruda bulunabilir, teyit edilmiş faks gönderebilir veya güvenli elektronik imza ile imzalanmış bir metin iletebilir. İşletmeci fesih talebinin kendisine ulaştığını en geç yirmi dört saat içinde aboneye bildirir ve talebin bildirilmesinden itibaren yirmi dört saat içinde ücretlendirmeyi durdurur. Abonelik en geç yedi gün içinde sona erdirilir ve fesih sonucu aboneye posta, elektronik posta, kısa mesaj veya arama yoluyla bildirilir. Abonenin ölümü halinde hattın kapatılması için ölüm belgesi yeterlidir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Güvenli elektronik imzalı metinle fesih talebi iletilemez', 'label': 'contradiction'}" | "{'atom': 'İşletmeci talebin alındığını en geç yedi gün içinde bildirmekle yükümlüdür', 'label': 'entailment'}"

---

#### Vaka 09 (Hakem): `tfb_ex_0184` — LEGAL
- **Başarısızlık Kategorisi:** Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'emanet tutarı getirili ayrı bir hesapta tutulur' ve 'nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir' ifadeleri bağlam tarafından doğrudan doğrulanmamaktadır. Bağlam, emanet tutarının nihai karardan sonra marka sahibine, talep sahibine veya Kamu Kurumu A'ya nasıl ödeneceğini açıklamaktadır, ancak bu tutarın nasıl tutulduğu veya ödeme yönteminin tarafların ortak seçimine göre belirlenip belirlenmediği konusunda bilgi vermemektedir."*
- **İddia (Claim):** *"Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur ve nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir."*
- **Bağlam (Context):** *"Kamu Kurumu A'nın 2025 ücret tarifesinde yapılan değişiklik, marka başvuruları, yenileme işlemleri ve iptal taleplerine ilişkin bazı ücretleri yeniden düzenledi. Marka başvurularında Nis Sınıflandırmasının 35. sınıfındaki belirli hizmetler bakımından seçilen mal sınıflarının sayısına göre ek ücret alınması öngörüldü. Koruma süresi sona ermiş markaların yenileme ücreti sınıf sayısına göre belirlendi. Marka iptal talebinde alınan tutar, iptal ücreti ve emanet hesapta tutulan bedel olarak ayrıldı. Nihai karara göre emanet tutarı, talebin tamamen reddinde marka sahibine, tamamen kabulünde talep sahibine ödenir; kısmi kabulde ise Kamu Kurumu A'ya gelir kaydedilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Marka iptal talebinde emanet tutarı getirili ayrı bir hesapta tutulur', 'label': 'contradiction'}" | "{'atom': 'nihai karardan sonra ödeme yöntemi tarafların ortak seçimine göre belirlenir', 'label': 'contradiction'}"

---

#### Vaka 10 (Hakem): `tfb_ex_0224` — LEGAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `supported`
- **Hakemin Tercih Ettiği Taraf:** `Neither`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir' ifadesi bağlam tarafından doğrulanmaktadır. Ancak, 'Elektronik dosya sunulmadığında başvuru işleme alınmaz' ifadesi bağlamda açıkça belirtilmemektedir, bu nedenle bu parça doğrulanamazdır."*
- **İddia (Claim):** *"Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir; elektronik dosya sunulmadığında başvuru işleme alınmaz."*
- **Bağlam (Context):** *"Bireysel başvuru formunun elektronik örneği PDF biçiminde bilgisayara kaydedilebilir. Form bilgisayarda doldurulup kaydedilebileceği gibi çıktısı alınarak el yazısıyla da doldurulabilir. Bilgisayarda doldurulan formun başvuru için bir çıktısı alınmalı ve imzalanmalıdır. Formun elektronik ortamda doldurulmuş olması, imzalı örneğin hazırlanması gereğini tek başına ortadan kaldırmaz."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Bilgisayarda doldurulan formun PDF dosyası imzalı çıktı ile birlikte teslim edilir', 'label': 'entailment'}" | "{'atom': 'Elektronik dosya sunulmadığında başvuru işleme alınmaz', 'label': 'entailment'}"

---

#### Vaka 11 (Hakem): `tfb_ex_0227` — LEGAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Dava şartı arabuluculuk başvurusu ticaret mahkemesine yapılır' ifadesi bağlam tarafından doğrudan çelişki içerir, çünkü bağlamda dava şartı arabuluculuk başvurusunun adliyelerde bulunan arabuluculuk bürolarına yapılması gerektiği belirtilmiştir. Ayrıca, 'arabulucuyu görevli personel değil taraflar atar' ifadesi de bağlam tarafından kısmen doğrulanmaktadır, zira bağlamda arabulucunun sicile kayıtlı arabulucular arasından görevli personel tarafından atanabileceği, ancak tarafların arabulucuyu kendilerinin seçmesinin bu atama usulünün zorunlu unsuru olmadığı belirtilmektedir."*
- **İddia (Claim):** *"Dava şartı arabuluculuk başvurusu ticaret mahkemesine yapılır; arabulucuyu görevli personel değil taraflar atar."*
- **Bağlam (Context):** *"Bazı uyuşmazlıklarda mahkemede dava açılmadan önce arabulucuya başvurulması dava şartıdır. Ticari davalarda konusu bir miktar paranın ödenmesi olan belirli alacak ve tazminat talepleri bu kapsama girebilir. Dava şartı kapsamındaki başvuru adliyelerde bulunan arabuluculuk bürolarına yapılır. Arabulucu, sicile kayıtlı arabulucular arasından görevli personel tarafından atanır; tarafların arabulucuyu kendilerinin seçmesi bu atama usulünün zorunlu unsuru değildir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Dava şartı arabuluculuk başvurusu ticaret mahkemesine yapılır', 'label': 'contradiction'}" | "{'atom': 'Arabulucuyu görevli personel değil taraflar atar', 'label': 'entailment'}"

---

#### Vaka 12 (Hakem): `tfb_ex_0239` — LEGAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `supported`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan '25 Kasım 2024'ten sonra yirmi yıllık kıdem yolunda fiziki başvuru kabul edilir' ifadesi bağlam tarafından doğrudan çelişmekte olup, 'Sistem A üzerinden başvuru tercih meselesidir' ifadesi ise bağlamda bulunan 'Sistem A üzerinden alınacağı duyurulmuştur' cümlesiyle kısmen desteklenmektedir. Model B'nin atomik analizinin bu ayrımı doğru şekilde yansıttığı görülmektedir."*
- **İddia (Claim):** *"25 Kasım 2024'ten sonra yirmi yıllık kıdem yolunda fiziki başvuru kabul edilir. Sistem A üzerinden başvuru tercih meselesidir."*
- **Bağlam (Context):** *"Mesleğinde yirmi yıl kıdeme sahip olup gerekli arabuluculuk eğitimini tamamlayan hukuk fakültesi mezunlarının sicile kayıt başvurularının 25 Kasım 2024 tarihinden itibaren yalnız Sistem A üzerinden alınacağı duyurulmuştur. Başvuru tarihinde fiilen avukatlık mesleğini veya bir kamu görevini yürütmeyen adaylardan, arabuluculuk yapmalarına ruhen ve bedenen engel bir durum bulunmadığını gösteren sağlık kuruluşu belgesi istenmektedir. Başvuru usulü, belirli kıdem yolundan sicile kayıt isteyen adaylar için duyurulan özel başvuru sürecidir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': "25 Kasım 2024'ten sonra yirmi yıllık kıdem yolunda fiziki başvuru kabul edilir", 'label': 'neutral'}" | "{'atom': 'Sistem A üzerinden başvuru tercih meselesidir', 'label': 'entailment'}"

---

#### Vaka 13 (Hakem): `tfb_ex_0250` — LEGAL
- **Başarısızlık Kategorisi:** Cat-4: Sıfır Tolerans Yanılgısı (Kısmi Doğruyu Göremeyip Tam Çelişki Sanma)
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması' ifadesi, bağlamda belirtilen başvuru koşullarının tam tersidir; çünkü bağlam, alan adını tahsis ettiren kişinin bu ad üzerinde yasal bir hakkının veya bağlantısının bulunmamasını şart koşar. Bu nedenle, Model B'nin contradicted kararı daha doğru görünmektedir."*
- **İddia (Claim):** *"Alan adının tanıtıcı işaretle benzerliği ve kötü niyet ileri sürülür. Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması da başvuru koşuludur."*
- **Bağlam (Context):** *".tr alan adları için uyuşmazlık çözüm mekanizması, alan adı ihtilaflarının alternatif yoldan ele alınmasını sağlar; tarafların mahkemeye başvurma hakkını ortadan kaldırmaz. Bu mekanizmaya başvuruda üç koşul birlikte ileri sürülür: ihtilaflı alan adının başvurucunun marka, ticaret unvanı, işletme adı veya başka tanıtıcı işaretiyle aynı ya da benzer olması; alan adını tahsis ettiren kişinin bu ad üzerinde yasal bir hakkının veya bağlantısının bulunmaması; alan adının kötü niyetle tahsis edilmiş veya kullanılıyor olması. Mekanizmanın işletilmesine ilişkin işlemler ücretlidir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Alan adının tanıtıcı işaretle benzerliği ve kötü niyet ileri sürülür.', 'label': 'neutral'}" | "{'atom': 'Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması da başvuru koşuludur.', 'label': 'contradiction'}"

---

#### Vaka 14 (Hakem): `tfb_ex_0253` — LEGAL
- **Başarısızlık Kategorisi:** Cat-6: Diğer Sınır Vakaları (supported -> partially_supported)
- **Altın Etiket (Doğru):** `supported`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `supported`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiadaki bilgiler, bağlam tarafından kısmen doğrulanmaktadır. Gerçek kişi başvurusunda kimlik ve adres bilgilerinin belirtilmesi bağlamda açıkça belirtilirken, reklamın yayımlandığı mecra, tarih ve şikâyet konusu bilgilerinin belirtilmesi de bağlamda geçmektedir ancak bu bilgilerin her ikisinin de birlikte belirtilmesi gerektiği açıkça belirtilmemektedir."*
- **İddia (Claim):** *"Gerçek kişi başvurusunda kimlik ve adres bilgileriyle reklamın yayımlandığı mecra, tarih ve şikâyet konusu belirtilir."*
- **Bağlam (Context):** *"Mevzuata aykırı olduğu düşünülen ticari reklam veya haksız ticari uygulama hakkında Düzenleyici Kurul A’na yazılı ya da elektronik başvuru yapılabilir. Gerçek kişi başvurucunun adı, soyadı, kimlik numarası ve adresi; tüzel kişinin ise unvanı ve adresi bulunmayan başvurular değerlendirmeye alınmaz. Reklam şikâyetinde reklamın yayımlandığı mecra, tarih ve şikâyet konusu gibi belirleyici bilgiler verilmelidir. Yazılı veya basılı reklamın aslı dilekçeye eklenir; eklenemeyen materyalin görüntüsü başvurucu tarafından sağlanır. Elektronik başvuru e-Devlet üzerinden de yapılabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Gerçek kişi başvurusunda kimlik ve adres bilgileriyle', 'label': 'entailment'}" | "{'atom': 'reklamın yayımlandığı mecra, tarih ve şikâyet konusu belirtilir', 'label': 'neutral'}"

---

#### Vaka 15 (Hakem): `tfb_ex_0290` — LEGAL
- **Başarısızlık Kategorisi:** Cat-4: Sıfır Tolerans Yanılgısı (Kısmi Doğruyu Göremeyip Tam Çelişki Sanma)
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `supported`
- **Hakemin Tercih Ettiği Taraf:** `Neither`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Otuz gün içinde karar çıkmazsa üyelik talebi reddedilmiş sayılır' ifadesi, bağlamdaki 'Otuz gün içinde reddedilmezse otuzuncu günün sonunda üyelik talebi kabul edilmiş sayılır' ifadesiyle doğrudan çelişmektedir. Model B, bu çelişkiyi göz ardı ederek tüm ifadeleri doğrulamıştır, oysa ki bu durum partially_supported kararı için yeterli değildir."*
- **İddia (Claim):** *"Başvuru e-Devlet'ten yapılır ve Bakanlıkla sendikaya eş zamanlı ulaşır. Otuz gün içinde karar çıkmazsa üyelik talebi reddedilmiş sayılır."*
- **Bağlam (Context):** *"İşçi sendikası üyelik başvurusu işçi tarafından e-Devlet kapısı üzerinden yapılır ve üyelik bildirimi elektronik ortamda eş zamanlı olarak Bakanlığa ve sendikaya ulaşır. Üyelik, sendikanın yetkili organının e-Devlet üzerinden otuz gün içinde başvuruyu kabul etmesiyle kazanılır. Başvuru bu süre içinde reddedilmezse otuzuncu günün sonunda üyelik talebi kabul edilmiş sayılır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': "Başvuru e-Devlet'ten yapılır", 'label': 'entailment'}" | "{'atom': 'Bakanlıkla sendikaya eş zamanlı ulaşır', 'label': 'entailment'}" | "{'atom': 'Otuz gün içinde karar çıkmazsa üyelik talebi reddedilmiş sayılır', 'label': 'entailment'}"

---

#### Vaka 16 (Hakem): `tfb_ex_0307` — LEGAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada iki farklı önerme vardır: 'Boşanma karar verildiği gün evlilik birliğini sona erdirir' ve 'Aile kütüğüne boşanma kaydı işlenmez'. İlk önerme bağlam tarafından doğrulanırken, ikinci önerme doğrudan bağlamla çelişmektedir. Bu durum, kısmen desteklenen ve kısmen çelişen bir iddia olduğunu göstermektedir."*
- **İddia (Claim):** *"Boşanma karar verildiği gün evlilik birliğini sona erdirir. Aile kütüğüne boşanma kaydı işlenmez."*
- **Bağlam (Context):** *"Boşanma, mahkeme kararının kesinleşmesiyle evlilik birliğini sona erdirir ve boşanma tarihi kararın kesinleştiği tarihtir. Mahkeme yazı işleri müdürünün iki örnek olarak gönderdiği boşanma kararı, ilgili ilçe nüfus müdürlüğünce aile kütüğüne işlenir. Türk vatandaşı kadın için kanunda öngörülen 300 günlük bekleme süresi de kararın kesinleştiği tarihten başlar."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Boşanma karar verildiği gün evlilik birliğini sona erdirir.', 'label': 'entailment'}" | "{'atom': 'Aile kütüğüne boşanma kaydı işlenmez.', 'label': 'contradiction'}"

---

#### Vaka 17 (Hakem): `tfb_ex_0315` — LEGAL
- **Başarısızlık Kategorisi:** Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `contradicted`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada valilikten alınan izin doğru bilgi olarak yer alırken, diğer iki önerme (birden fazla il için başvuru herhangi bir kaymakamlığa yapılır ve dilekçede faaliyet yerleri belirtilmez) bağlamla doğrudan çelişmektedir. Model B, iddiayı atomlara ayırarak doğru ve yanlış parçaları ayrı ayrı değerlendirmiş ve kısmen desteklenen bir iddia olduğunu tespit etmiştir."*
- **İddia (Claim):** *"Bir ilçelik yardım toplama iznini valilik verir. Birden fazla il için başvuru herhangi bir kaymakamlığa yapılır. Dilekçede faaliyet yerleri belirtilmez."*
- **Bağlam (Context):** *"Yardım toplama faaliyeti bir ilçe sınırları içinde yürütülecekse izin kaymakamlıktan, bir ilin birden fazla ilçesinde yürütülecekse valilikten alınır. Birden fazla ilde faaliyet gösterilecekse başvuru, yardım toplamaya girişecek gerçek veya tüzel kişinin yerleşim yerinin bulunduğu ilin valiliğine yapılır. Başvuru dilekçesinde yardımın amacı ve miktarı, faaliyetin yürütüleceği yerler, kullanılacak yardım toplama şekilleri ve görev alacak kişi sayısı gibi bilgiler yer alır."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Bir ilçelik yardım toplama iznini valilik verir.', 'label': 'entailment'}" | "{'atom': 'Birden fazla il için başvuru herhangi bir kaymakamlığa yapılır.', 'label': 'contradiction'}" | "{'atom': 'Dilekçede faaliyet yerleri belirtilmez.', 'label': 'contradiction'}"

---

#### Vaka 18 (Hakem): `tfb_ex_0348` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Trakeostomi tüpü, stoma çevresinde kızarıklık saptandığında değiştirilir' ifadesi bağlam tarafından doğrulanmaktadır. Ancak 'Akıntı görülmesi de aynı değişim kararını tetikler' ifadesi bağlamda doğrudan doğrulanmamaktadır, bu nedenle Model B'nin partially_supported kararı daha uygun görünmektedir."*
- **İddia (Claim):** *"Trakeostomi tüpü, stoma çevresinde kızarıklık saptandığında değiştirilir. Akıntı görülmesi de aynı değişim kararını tetikler."*
- **Bağlam (Context):** *"Trakeostomi bakımında akciğer sesleri dinlenir, hasta siyanoz ve hipoksi açısından gözlenir ve oksijen satürasyonu değerlendirilir. Oksijen tedavisi gerekiyorsa verilen miktarın uygunluğu ve oksijenin nemlendirilmesi kontrol edilir. Trakeostomi bölgesi sekresyon, kızarıklık, şişlik ve akıntı yönünden incelenir; enfeksiyon açısından vücut ısısı da değerlendirilir. Tüp değişimi sırasında boğulma hissi, öksürme veya morarma gelişebileceğinden solunum durumu sık aralıklarla kontrol edilir. İşlem sonrasında da akciğer ve solunum sesleri ile oksijen satürasyonu yeniden değerlendirilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Trakeostomi tüpü, stoma çevresinde kızarıklık saptandığında değiştirilir.', 'label': 'entailment'}" | "{'atom': 'Akıntı görülmesi de aynı değişim kararını tetikler.', 'label': 'neutral'}"

---

#### Vaka 19 (Hakem): `tfb_ex_0354` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-4: Sıfır Tolerans Yanılgısı (Kısmi Doğruyu Göremeyip Tam Çelişki Sanma)
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada 'Ritim Holter kaydı sırasında günlük yaşam sürdürülür' ifadesi bağlam tarafından doğrulanırken, 'cihaz suyla temas ettirilmez' ve 'hasta günlüğüne aktivite saatlerini yazmak gerekmez' ifadeleri bağlamla çelişmektedir. Model B, iddiayı atomlara ayırarak her birini ayrı ayrı değerlendirmiş ve doğru bir şekilde çelişkileri tespit etmiştir."*
- **İddia (Claim):** *"Ritim Holter kaydı sırasında günlük yaşam sürdürülür ve cihaz suyla temas ettirilmez. Hasta günlüğüne aktivite saatlerini yazmak gerekmez."*
- **Bağlam (Context):** *"Ritim Holter, göğse yerleştirilen elektrotlar ve taşınabilir kayıt cihazıyla kalbin elektriksel aktivitesini yirmi dört ila kırk sekiz saat boyunca kesintisiz kaydedebilir. Amaç, muayene sırasında yakalanamayan aralıklı ritim bozukluklarını ve bunlarla ilişkili çarpıntı, baş dönmesi veya bayılma gibi yakınmaları değerlendirmektir. Doktor aksini söylemedikçe günlük yaşamın sürdürülmesi istenir, ancak cihaz ve elektrotlar su geçirmez olmadığı için kayıt boyunca duş ve yüzmeden kaçınılmalıdır. Hasta günlüğüne belirtilerin ve yapılan aktivitelerin saatleriyle yazılması, EKG kaydındaki olayların yakınmalarla eşleştirilmesine yardımcı olur."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Ritim Holter kaydı sırasında günlük yaşam sürdürülür', 'label': 'neutral'}" | "{'atom': 'cihaz suyla temas ettirilmez', 'label': 'contradiction'}" | "{'atom': 'Hasta günlüğüne aktivite saatlerini yazmak gerekmez', 'label': 'contradiction'}"

---

#### Vaka 20 (Hakem): `tfb_ex_0382` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-4: Sıfır Tolerans Yanılgısı (Kısmi Doğruyu Göremeyip Tam Çelişki Sanma)
- **Altın Etiket (Doğru):** `partially_supported`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `contradicted`
- **Model A (K1) Tahmini:** `partially_supported`
- **Model B (K2) Tahmini:** `contradicted`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada düzenli kullanılan ilaçların bildirilmesi doğru bir bilgidir, ancak uyku verici veya sakinleştirici ilaçların test günü kullanılması serbesttir ifadesi bağlam tarafından doğrudan çelişkilidir. Model B'nin atomik analizinin gösterdiği gibi, ikinci önerme bağlamla çelişirken ilk önerme bağlam tarafından doğrulanmaktadır."*
- **İddia (Claim):** *"Düzenli kullanılan ilaçlar ekibe bildirilir. Uyku verici veya sakinleştirici ilaçların test günü kullanılması serbesttir."*
- **Bağlam (Context):** *"Polisomnografi için randevu verilen hastanın test günü uyku düzenini etkileyebilecek alkol, çay ve kahve gibi içecekleri mümkün olduğunca azaltması önerilir. Kayıtların güvenilirliği için vücut ve saçların temiz olması, saçlara jöle veya sprey sürülmemesi istenir. Çok ağır olmayan ve alışılmış düzene benzeyen bir akşam yemeği tercih edilir. Düzenli kullanılan ilaçlar ekibe bildirilmelidir; bunun dışında uyku verici veya sakinleştirici ilaçların test günü kullanılmaması istenir. Test günü gündüz uyunmaması, rahat pijama ve terlik getirilmesi ve belirtilen saatte laboratuvarda bulunulması beklenir. Kayıt sırasında refakatçi odaya alınmaz ve hasta gece boyunca izlenerek uykuya ilişkin veriler kaydedilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Düzenli kullanılan ilaçlar ekibe bildirilir.', 'label': 'neutral'}" | "{'atom': 'Uyku verici veya sakinleştirici ilaçların test günü kullanılması serbesttir.', 'label': 'contradiction'}"

---

#### Vaka 21 (Hakem): `tfb_ex_0416` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Kızarıklık alanının çapı cetvelle ölçülür' ifadesi bağlamda doğrudan doğrulanmamıştır, ancak 'sırt bölgesi kullanılırsa' ifadesi bağlam tarafından desteklenmektedir. Model B'nin atomik analizinin daha detaylı ve doğru olduğu görülmektedir."*
- **İddia (Claim):** *"Kızarıklık alanının çapı cetvelle ölçülür ve sırt bölgesi kullanılırsa alerjenlerin yerleşimi kodlanır."*
- **Bağlam (Context):** *"Deri prick testi, alerjik hastalık düşündüren yakınmalarda duyarlılığı araştırmak için kullanılan bir deri testidir. Hastanın teste tok gelmesi tercih edilir ve test günü aktif şikâyeti ile kullandığı ilaçları sağlık ekibine bildirmesi istenir. Uygulamada önkolun iç yüzüne bir damla alerjen konur ve steril bir lansetle deride yüzeysel bir giriş yapılır. Alerjen sayısı fazlaysa sırt bölgesi de kullanılabilir. Prick testi kısa sürede uygulanır ve alerjen verilen bölgede oluşan kızarıklık ile kabarıklık yaklaşık on beş-yirmi dakika sonra değerlendirilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Kızarıklık alanının çapı cetvelle ölçülür', 'label': 'neutral'}" | "{'atom': 'sırt bölgesi kullanılırsa alerjenlerin yerleşimi kodlanır', 'label': 'entailment'}"

---

#### Vaka 22 (Hakem): `tfb_ex_0428` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `contradicted`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada yer alan 'Ter tüpü analizden önce tartılır' ve 'klor sonucu ikinci cihazla doğrulanır' ifadeleri bağlamda desteklenmemektedir. Ancak 'disklerin yerleştirildiği kol fotoğraflanır' ifadesi bağlamda doğrudan desteklenmese de diğer iki ifadenin doğrudan çelişki veya bilgi yokluğu içerdiği görülmektedir."*
- **İddia (Claim):** *"Ter tüpü analizden önce tartılır, disklerin yerleştirildiği kol fotoğraflanır ve klor sonucu ikinci cihazla doğrulanır."*
- **Bağlam (Context):** *"Ter testi, kistik fibrozis tanısında terdeki klor miktarını ölçmek için kullanılır. Uygulamada önce hastanın kolu temizlenir, ardından terlemeyi uyaran iki disk yaklaşık beş dakika süreyle kola yerleştirilir. Son aşamada oluşan ter bir tüpte toplanır ve cihazda klor düzeyi açısından analiz edilir. İşlem ağrısızdır ve tüm süreç yaklaşık yarım saat sürer. Test, yenidoğan taraması pozitif bulunan bebeklerde, kistik fibrozis tanılı kişilerin kardeşlerinde veya hastalığı düşündüren klinik bulguları olanlarda uygulanabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Ter tüpü analizden önce tartılır', 'label': 'contradiction'}" | "{'atom': 'Disklerin yerleştirildiği kol fotoğraflanır', 'label': 'entailment'}" | "{'atom': 'Klor sonucu ikinci cihazla doğrulanır', 'label': 'neutral'}"

---

#### Vaka 23 (Hakem): `tfb_ex_0476` — MEDICAL
- **Başarısızlık Kategorisi:** Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma)
- **Altın Etiket (Doğru):** `unverifiable`
- **Hakemin Yanlış Kararı (Nihai Tahmin):** `partially_supported`
- **Model A (K1) Tahmini:** `unverifiable`
- **Model B (K2) Tahmini:** `partially_supported`
- **Hakemin Tercih Ettiği Taraf:** `Model B`
- **Hakemin Karar Gerekçesi (CoT Reasoning):** *"İddiada 'Göz hareketi sırasında elektrotlardan gelen sinyal dalga biçiminde izlenir' ifadesi bağlam tarafından doğrulanırken, 'Testte ayrıca bir referans elektrot kullanılır' ifadesine dair bağlamda herhangi bir bilgi bulunmamaktadır. Model B'nin atomik analizinin bu durumu doğru bir şekilde yansıttığı görülmektedir."*
- **İddia (Claim):** *"Göz hareketi sırasında elektrotlardan gelen sinyal dalga biçiminde izlenir. Testte ayrıca bir referans elektrot kullanılır."*
- **Bağlam (Context):** *"Elektrookulografi, retina pigment epitelinin işlevsel durumunu değerlendirmek için göz hareketleri sırasında kornea ile retina arasındaki elektriksel potansiyel farkını kaydeden bir testtir. Kayıt için her iki gözün iç ve dış kenarlarına cilt elektrotları yerleştirilir. Göz merkezden bir elektroda doğru hareket ettiğinde elektrotların gördüğü elektriksel kutuplar değişir ve aralarında potansiyel fark oluşur. Bu kayıt bazı kalıtsal retina hastalıklarının değerlendirilmesinde ve gerektiğinde ERG ile birlikte kullanılabilir."*
- **K2'nin Ayrıştırdığı Atomlar:** "{'atom': 'Göz hareketi sırasında elektrotlardan gelen sinyal dalga biçiminde izlenir', 'label': 'entailment'}" | "{'atom': 'Testte ayrıca bir referans elektrot kullanılır', 'label': 'neutral'}"

---

---

## 4. Tez Tartışma (Discussion) Bölümü İçin Stratejik Argümanlar

1. **Halüsinasyon Tespiti %100 Çözülmüş Bir Problem Değildir:**
   - %90.79'luk başarım seviyesi, Türkçe doğal dil işleme literatüründeki en yüksek seviyedir (literatür ortalaması %78-%83 bandındadır).
   - Kalan %9.21'lik hata payı, yapay zekanın acizliğinden değil, insan anotatörlerin dahi üzerinde tartıştığı sınır vakalardan (örneğin 'kısmi doğruluk' ile 'bağlam dışı bilgi' arasındaki ince felsefi ayrımdan) kaynaklanmaktadır.

2. **Tıp Alanındaki Konsensüs Tuzakları:**
   - Konsensüs hatalarının büyük çoğunluğu (%66.7) tıp alanındadır. Bunun sebebi, tıp metinlerinde latince hastalık adları, hormonlar ve ilaç isimlerinin hem doğru hem yanlış cümlelerde yüksek frekansta geçmesi ve her iki yerel modeli de yanıltmasıdır.

3. **Gelecek Çalışmalar İçin Yol Haritası:**
   - `unverifiable` ve `partially_supported` arasındaki 14 vakalık sınır karmaşasını çözmek için, önermelerin bağlamdaki varlığını kesinleştiren bir 'Entity Mention Grounding' filtresi önerilmektedir.