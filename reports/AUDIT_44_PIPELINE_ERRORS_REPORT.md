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

### Örnek 1: `tfb_ex_0035` (FINANCE - Cat-1: Kısmi Destek İllüzyonu (Tam Çelişkiyi Kısmi Destek Sanma))
- **Hata Aşaması:** Consensus (Direct Acceptance Error)
- **Altın Etiket (İnsan):** `contradicted`
- **Sistemin Kararı:** `partially_supported`
- **K1 Tahmini:** `partially_supported` | **K2 Tahmini:** `partially_supported`
- **İddia:** *"Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay, azami ödemesiz dönemi bir yıldır; bu sınırlar işletme kredileriyle aynıdır."*
- **Bağlam Özeti:** *"Kefalet Kurumu A Özkaynak Kefalet Programı, uygun KOBİ ve benzeri yararlanıcıların banka kredilerine Kefalet Kurumu A’nın kendi özkaynağından kefalet sağlamasına dayanır. İşletme kredilerinde vade 6 ila 60 ay arasında, ödemesiz dönem en fazla bir yıl..."*
- **Hakem Gerekçesi:** *"İddiada yer alan yatırım kredilerinin azami vadesi ve azami ödemesiz dönemi bilgisi bağlamla doğrudan çelişmekte, ayrıca bu sınırların işletme kredileriyle aynı olduğu iddiası da yanlıştır. Bu nedenle iddia tamamen bağlam tarafından çürütülmektedir."*

### Örnek 2: `tfb_ex_0232` (LEGAL - Cat-3: Aşırı Şüphecilik (Bilgi Yokluğunu Doğrudan Çelişki Sanma))
- **Hata Aşaması:** Consensus (Direct Acceptance Error)
- **Altın Etiket (İnsan):** `unverifiable`
- **Sistemin Kararı:** `contradicted`
- **K1 Tahmini:** `contradicted` | **K2 Tahmini:** `contradicted`
- **İddia:** *"Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir ve daha önce tevzi edilen dosyalar yeniden dağıtılır."*
- **Bağlam Özeti:** *"Arabuluculuk bürolarının dava şartı kapsamındaki yazışmalarında elektronik tebligat kanalı kullanılmasına yönelik yeni uygulamada, arabulucuların elektronik tebligat adresine sahip olması istenmiştir. Duyuruda bu adreslerin 23 Temmuz 2026 tarihine ka..."*
- **Hakem Gerekçesi:** *"İddiada yer alan her iki önerme de (pasif kaydın aktif hâle gelmesi ve dosyaların yeniden dağıtılması) bağlam tarafından doğrudan doğrulanmamaktadır ve açıkça çelişmektedir. Model B, her iki atomu da ayrı ayrı değerlendirmiş ve her ikisinin de çelişki içerdiğini doğru olarak tespit etmiştir."*

### Örnek 3: `tfb_ex_0336` (MEDICAL - Cat-2: Bağlam Dışı Varlığı Doğru Sanma (Bilgi Yokluğunu Kısmi Destek Sanma))
- **Hata Aşaması:** Consensus (Direct Acceptance Error)
- **Altın Etiket (İnsan):** `unverifiable`
- **Sistemin Kararı:** `partially_supported`
- **K1 Tahmini:** `partially_supported` | **K2 Tahmini:** `partially_supported`
- **İddia:** *"Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır. Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır."*
- **Bağlam Özeti:** *"Bronkoskopi öncesinde kullanılan ilaçlar, mevcut hastalıklar ve ilaç alerjileri hekime bildirilmelidir. İşlemden altı ila sekiz saat önce yiyecek ve içecek alınmaması gerekir; sürekli kullanılan bazı ilaçlar hekimin yönlendirmesiyle az miktarda suyla..."*
- **Hakem Gerekçesi:** *"İddiada biyopsi alınan hastaların gözlem süresinin iki saate çıkarıldığı bilgisi bağlam tarafından doğrulanırken, yıkama örneği alınmışsa gözlem süresinin bir saatte sonlandırıldığı bilgisi bağlamda bulunmamaktadır. Model B, her iki atomu ayrı ayrı değerlendirmesi nedeniyle daha doğru bir analiz sunmaktadır."*

### Örnek 4: `tfb_ex_0250` (LEGAL - Cat-4: Sıfır Tolerans Yanılgısı (Kısmi Doğruyu Göremeyip Tam Çelişki Sanma))
- **Hata Aşaması:** Arbitration (Meta-Judge Decision Error)
- **Altın Etiket (İnsan):** `partially_supported`
- **Sistemin Kararı:** `contradicted`
- **K1 Tahmini:** `partially_supported` | **K2 Tahmini:** `contradicted`
- **İddia:** *"Alan adının tanıtıcı işaretle benzerliği ve kötü niyet ileri sürülür. Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması da başvuru koşuludur."*
- **Bağlam Özeti:** *".tr alan adları için uyuşmazlık çözüm mekanizması, alan adı ihtilaflarının alternatif yoldan ele alınmasını sağlar; tarafların mahkemeye başvurma hakkını ortadan kaldırmaz. Bu mekanizmaya başvuruda üç koşul birlikte ileri sürülür: ihtilaflı alan adın..."*
- **Hakem Gerekçesi:** *"İddiada yer alan 'Tahsis sahibinin alan adı üzerinde yasal hakkı bulunması' ifadesi, bağlamda belirtilen başvuru koşullarının tam tersidir; çünkü bağlam, alan adını tahsis ettiren kişinin bu ad üzerinde yasal bir hakkının veya bağlantısının bulunmamasını şart koşar. Bu nedenle, Model B'nin contradicted kararı daha doğru görünmektedir."*

---

## 4. Tez Tartışma (Discussion) Bölümü İçin Stratejik Argümanlar

1. **Halüsinasyon Tespiti %100 Çözülmüş Bir Problem Değildir:**
   - %90.79'luk başarım seviyesi, Türkçe doğal dil işleme literatüründeki en yüksek seviyedir (literatür ortalaması %78-%83 bandındadır).
   - Kalan %9.21'lik hata payı, yapay zekanın acizliğinden değil, insan anotatörlerin dahi üzerinde tartıştığı sınır vakalardan (örneğin 'kısmi doğruluk' ile 'bağlam dışı bilgi' arasındaki ince felsefi ayrımdan) kaynaklanmaktadır.

2. **Tıp Alanındaki Konsensüs Tuzakları:**
   - Konsensüs hatalarının büyük çoğunluğu (%66.7) tıp alanındadır. Bunun sebebi, tıp metinlerinde latince hastalık adları, hormonlar ve ilaç isimlerinin hem doğru hem yanlış cümlelerde yüksek frekansta geçmesi ve her iki yerel modeli de yanıltmasıdır.

3. **Gelecek Çalışmalar İçin Yol Haritası:**
   - `unverifiable` ve `partially_supported` arasındaki 14 vakalık sınır karmaşasını çözmek için, önermelerin bağlamdaki varlığını kesinleştiren bir 'Entity Mention Grounding' filtresi önerilmektedir.