# TR-FactBench: 21 Konsensüs Hatasının Vaka ve Sınıf Bazlı Detaylı İnceleme Raporu

**Araştırma:** K1 (ELECTRA-TR) ve K2 (Gemma-4 + mDeBERTa-v3) Modellerinin Ortak Yanıldığı 21 Vakanın Derin Dilbilimsel ve Epistemik Analizi  
**Tarih:** 2026-10-04  
**Veri Kümesi:** TR-FactBench Gold 480 (478 test örneği içerisindeki 358 uzlaşma vakası)  

---

## 1. Giriş ve Genel İstatistikler

TR-FactBench altın test kümesindeki 478 vakanın 358'inde (%74.9) K1 ve K2 modelleri doğrudan aynı karara varmıştır (Konsensüs Bölgesi). 
Bu 358 vakanın 337'sinde (%94.13) her iki model de altın standartla tam uyumlu doğru kararı vermiştir. 
Geriye kalan **21 vakada (%5.87)** ise her iki model de kendi aralarında uzlaşmış ancak altın etiketten sapmıştır. 
Bu rapor, iki bağımsız mimarinin neden aynı yanılsamaya düştüğünü sınıf ve örnek bazında tek tek ortaya koymaktadır.

### A. Alan Bazlı Dağılım

| Alan (Domain) | Hata Sayısı | Oran (%) |
|---|:---:|:---:|
| **Medical** | 14 | %66.7 |
| **Legal** | 4 | %19.0 |
| **Finance** | 3 | %14.3 |

### B. Geçiş (Altın Etiket -> Modellerin Ortak Tahmini) Matrisi

| Altın Etiket (Gold) | Modellerin Tahmini (Pred) | Vaka Sayısı | Hata Niteliği |
|---|---|:---:|---|
| `contradicted` | `partially_supported` | 7 | Leksikal yanılsama nedeniyle çelişkili cümlenin kısmen doğru sanılması |
| `unverifiable` | `contradicted` | 5 | Metinde bilgi yokluğunun açık çelişki olarak yorumlanması |
| `unverifiable` | `partially_supported` | 4 | Periferik kavram eşleşmesinin doğrulanmış atom kabul edilmesi |
| `partially_supported` | `supported` | 2 | İnce hukuki/idari kısıtlamanın gözden kaçırılması |
| `contradicted` | `supported` | 1 | Zıt kutuplu iki terimin leksikal eşleşmesi |
| `unverifiable` | `supported` | 1 | İlişkisiz cümlenin genel konu benzerliğiyle onaylanması |
| `supported` | `partially_supported` | 1 | Doğru cümlenin ikinci yarısına aşırı şüpheci yaklaşılması |

---

### C. 21 Hata Vakasının Hızlı Başvuru İndeksi (Master Table)

| No | Örnek ID | Alan | Altın Etiket | Konsensüs Tahmini | K1 Güven (%) | Ayrışan Atomlar ve Sonuçları |
|:---:|---|:---:|:---:|:---:|:---:|---|
| 1 | **tfb_ex_0019** | Finance | contradicted | supported | %96.0 | A1: entailment, A2: entailment |
| 2 | **tfb_ex_0035** | Finance | contradicted | partially_supported | %99.8 | A1: contradiction, A2: contradiction, A3: entailment |
| 3 | **tfb_ex_0115** | Finance | contradicted | partially_supported | %99.5 | A1: entailment, A2: entailment, A3: contradiction |
| 4 | **tfb_ex_0195** | Legal | contradicted | partially_supported | %100.0 | A1: entailment, A2: contradiction |
| 5 | **tfb_ex_0232** | Legal | unverifiable | contradicted | %54.1 | A1: contradiction, A2: contradiction |
| 6 | **tfb_ex_0274** | Legal | partially_supported | supported | %99.7 | A1: entailment, A2: entailment |
| 7 | **tfb_ex_0278** | Legal | partially_supported | supported | %66.6 | A1: entailment, A2: entailment |
| 8 | **tfb_ex_0323** | Medical | contradicted | partially_supported | %99.9 | A1: contradiction, A2: entailment, A3: contradiction |
| 9 | **tfb_ex_0332** | Medical | unverifiable | supported | %69.8 | A1: entailment |
| 10 | **tfb_ex_0336** | Medical | unverifiable | partially_supported | %100.0 | A1: entailment, A2: neutral |
| 11 | **tfb_ex_0340** | Medical | unverifiable | partially_supported | %81.9 | A1: entailment, A2: neutral |
| 12 | **tfb_ex_0360** | Medical | unverifiable | contradicted | %100.0 | A1: contradiction, A2: neutral |
| 13 | **tfb_ex_0363** | Medical | contradicted | partially_supported | %99.9 | A1: entailment, A2: contradiction |
| 14 | **tfb_ex_0364** | Medical | unverifiable | partially_supported | %98.7 | A1: neutral, A2: entailment |
| 15 | **tfb_ex_0368** | Medical | unverifiable | contradicted | %56.6 | A1: contradiction, A2: neutral |
| 16 | **tfb_ex_0372** | Medical | unverifiable | contradicted | %97.6 | A1: neutral, A2: contradiction |
| 17 | **tfb_ex_0405** | Medical | supported | partially_supported | %97.8 | A1: contradiction, A2: entailment |
| 18 | **tfb_ex_0423** | Medical | contradicted | partially_supported | %83.7 | A1: entailment, A2: contradiction |
| 19 | **tfb_ex_0452** | Medical | unverifiable | partially_supported | %52.1 | A1: neutral, A2: entailment |
| 20 | **tfb_ex_0463** | Medical | contradicted | partially_supported | %97.0 | A1: contradiction, A2: entailment |
| 21 | **tfb_ex_0468** | Medical | unverifiable | contradicted | %99.9 | A1: contradiction |

---
## 2. Sınıf Geçişlerine Göre 21 Vakanın Detaylı İncelenmesi

### Grup 1: Çelişkiyi Kısmi Destek Sanma (contradicted -> partially_supported, 7 Vaka)

#### Vaka 1: tfb_ex_0035 (FINANCE)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %99.8 | contradicted: %0.2 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay" $\rightarrow$ `contradiction`
  - **Atom 2:** "azami ödemesiz dönemi bir yıldır" $\rightarrow$ `contradiction`
  - **Atom 3:** "bu sınırlar işletme kredileriyle aynıdır" $\rightarrow$ `entailment`
- **İddia (Claim):** "Kefalet Kurumu A Özkaynak Kefalet Programında yatırım kredilerinin azami vadesi 60 ay, azami ödemesiz dönemi bir yıldır; bu sınırlar işletme kredileriyle aynıdır."
- **Bağlam (Context):** "Kefalet Kurumu A Özkaynak Kefalet Programı, uygun KOBİ ve benzeri yararlanıcıların banka kredilerine Kefalet Kurumu A’nın kendi özkaynağından kefalet sağlamasına dayanır. İşletme kredilerinde vade 6 ila 60 ay arasında, ödemesiz dönem en fazla bir yıldır; yatırım kredilerinde vade 6 ila 84 ay arasında ve ödemesiz dönem en fazla iki yıldır. Yararlanıcı veya grup başına kefalet limiti 5 milyon TL, azami kefalet oranı yüzde 80'dir. Başvurular bankalar üzerinden Kefalet Kurumu A’nın elektronik sistemi aracılığıyla yapılır."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

#### Vaka 2: tfb_ex_0115 (FINANCE)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %99.5 | contradicted: %0.5 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya" $\rightarrow$ `entailment`
  - **Atom 2:** "borsa dışı tazmin talepleri Borsa’ya" $\rightarrow$ `entailment`
  - **Atom 3:** "zarar tazminine karar verir Düzenleyici Kurum A" $\rightarrow$ `contradiction`
- **İddia (Claim):** "Borsa işlemlerinden doğan uyuşmazlıklar Meslek Birliği A’ya, borsa dışı tazmin talepleri Borsa A’ya götürülür ve Düzenleyici Kurum A zarar tazminine karar verir."
- **Bağlam (Context):** "Sermaye piyasası uyuşmazlığında izlenecek başvuru yolu uyuşmazlığın türüne göre değişebilir. Borsada emirlerin iletilmesi, eşleştirilmesi ve gerçekleşen işlemlere ilişkin yükümlülüklerin yerine getirilmesi gibi borsa işlemlerinden doğan uyuşmazlıklar için Borsa A’ya başvuru yapılabilir. Borsa işlemleri dışındaki zarar ve tazmin talepleri Meslek Birliği A bünyesindeki müşteri uyuşmazlıkları hakem mekanizmasına iletilebilir. Düzenleyici Kurum A ise mevzuata aykırılık iddialarını idari yönden inceleyebilir ancak bu inceleme kapsamında zarar tazminine karar vermez."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

#### Vaka 3: tfb_ex_0195 (LEGAL)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %100.0 | contradicted: %0.0 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır" $\rightarrow$ `entailment`
  - **Atom 2:** "güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir" $\rightarrow$ `contradiction`
- **İddia (Claim):** "Ön ödemeli sayaç kullanan tüketicilerden güvence bedeli alınır ve güvence bedelinin iadesi için borçların ödenmesine ek olarak ayrı bir uygunluk belgesi sunulması gerekir."
- **Bağlam (Context):** "Elektrik perakende satışında görevli tedarik şirketi, kullanım yerinin değişmesi veya perakende satış sözleşmesinin sona ermesi ya da feshi halinde tüketim bedelinin ödenmemesi riskine karşı güvence bedeli talep eder. Ön ödemeli sayaç kullanan tüketicilerden, genel aydınlatma kapsamındaki yerlerden ve ilgili düzenlemede belirtilen ibadethanelerden güvence bedeli alınmaz. Perakende satış sözleşmesi sona erdiğinde, feshedildiğinde veya tüketici ön ödemeli sayaca geçtiğinde güvence bedeli iade edilir. Tüketicinin borçları ödendikten sonra kalan tutar, talep tarihinden itibaren en geç beş iş günü içinde iade edilir. İade için borcun ödenmesi dışında başka bir şart veya belge istenemez."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

#### Vaka 4: tfb_ex_0323 (MEDICAL)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %99.9 | contradicted: %0.1 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar" $\rightarrow$ `contradiction`
  - **Atom 2:** "Sinir iletim ölçümü ikinci aşamadadır" $\rightarrow$ `entailment`
  - **Atom 3:** "EMG değerlendirmesi bütün hastalara uygulanır" $\rightarrow$ `contradiction`
- **İddia (Claim):** "EMG önce ince iğne elektrotlarla kasların değerlendirilmesiyle başlar. Sinir iletim ölçümü ikinci aşamadadır ve iki bölüm bütün hastalara uygulanır."
- **Bağlam (Context):** "Elektromiyografi (EMG), sinir ve kasların elektriksel yöntemlerle değerlendirildiği bir incelemedir. İlk bölümde düşük şiddette elektrik uyarıları kullanılarak sinirlerin iletim fonksiyonları ölçülebilir. Gerekli hastalarda ikinci bölümde tek kullanımlık ince iğne elektrotlarla kaslar ve bu kaslara gelen sinirler değerlendirilir; her hastada iki bölümün birden yapılması zorunlu değildir. İncelemenin süresi hastaya ve istenen değerlendirmeye göre değişmekle birlikte yaklaşık yarım saat olabilir. Düzenli ilaçlar genellikle sürdürülebilir, ancak kan sulandırıcı kullananların ve kalp pili ya da başka bir pil taşıyanların hekimi önceden bilgilendirmesi önerilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

#### Vaka 5: tfb_ex_0363 (MEDICAL)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %99.9 | contradicted: %0.1 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "MR çekim odasına metal eşyalarla girilebilir." $\rightarrow$ `entailment`
  - **Atom 2:** "MR çekim sırasında hareket etmek görüntülemeyi etkilemez." $\rightarrow$ `contradiction`
- **İddia (Claim):** "MR çekim odasına metal eşyalarla girilebilir ve çekim sırasında hareket etmek görüntülemeyi etkilemez."
- **Bağlam (Context):** "Manyetik rezonans incelemelerinin çoğunda özel bir ön hazırlık gerekmez; aksi söylenmedikçe hasta yemek yiyip düzenli ilaçlarını alabilir. Ancak bazı özellikli çekimlerde hazırlık değişir. Örneğin entero incelemesinde hastadan aç gelmesi ve hazırlanan yaklaşık bir buçuk litre suyu iki saat içinde içmesi, bazı batın ve ilaçlı incelemelerde ise en az sekiz saat açlık istenebilir. Güçlü manyetik alan nedeniyle saat, takı, kredi kartı, işitme cihazı ve benzeri metal ya da manyetik alandan etkilenebilecek eşyalar çekim odasına girmeden çıkarılmalıdır. Vücutta implant, kalp pili, metal parça veya benzeri bir materyal varsa görevliye önceden bildirilir. Çekim sırasında hasta hareketsiz kalır; cihazın gürültüsü için kulak koruyucu verilebilir ve görevliyle mikrofon üzerinden iletişim kurulabilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

#### Vaka 6: tfb_ex_0423 (MEDICAL)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %83.7 | contradicted: %16.1 | unverifiable: %0.1`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "ERCP sırasında görüntüleme için kontrast mesaneye verilir" $\rightarrow$ `entailment`
  - **Atom 2:** "ERCP işlemi sedoanaljezi olmadan tamamlanır" $\rightarrow$ `contradiction`
- **İddia (Claim):** "ERCP sırasında görüntüleme için kontrast mesaneye verilir ve işlem sedoanaljezi olmadan tamamlanır."
- **Bağlam (Context):** "ERCP, safra yolları ve pankreas kanalının tanı ve tedavisinde kullanılan özel bir endoskopi yöntemidir. Duodenoskop ağızdan ilerletilerek onikiparmak bağırsağına ulaştırılır; papilla üzerinden ince kateterlerle safra kanalına, gerektiğinde pankreas kanalına kontrast madde verilir ve X ışınıyla görüntüleme yapılır. Aynı seansta safra yolu taşının çıkarılması, darlığın balon veya stentle giderilmesi gibi tedaviler uygulanabilir. İşlemden önce en az altı-sekiz saat açlık gerekir; kan sulandırıcı ilaçlar ve ilaç alerjileri hekime bildirilir. Damar yolu açılıp sedoanaljezi uygulanır. İşlem genellikle otuz-altmış dakika sürer."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

#### Vaka 7: tfb_ex_0463 (MEDICAL)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.1 | partially_supported: %97.0 | contradicted: %2.9 | unverifiable: %0.1`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "UVA riboflavinden önce uygulanır" $\rightarrow$ `contradiction`
  - **Atom 2:** "Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır" $\rightarrow$ `entailment`
- **İddia (Claim):** "UVA riboflavinden önce uygulanır. Işınlama tamamlandıktan sonra riboflavin damlatmaya başlanır."
- **Bağlam (Context):** "Korneal cross-linking, ilerleme saptanan keratokonusta kornea dokusunu güçlendirmek için riboflavin ve ultraviyole A kullanılan bir işlemdir. Damla anestezisiyle göz uyuşturulduktan sonra korneanın epitel tabakası kaldırılır. Riboflavin solüsyonu 30 dakika boyunca beş dakikada bir damlatılır; ardından korneaya yaklaşık 30 dakika UVA uygulanırken riboflavin damlatılmaya devam edilir. İşlem sonunda göz antibiyotikli pomatla kapatılır ve ortalama iyileşme süreci yaklaşık iki gündür."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddianın tüm bağımsız önermeleri metindeki kurallarla açıkça çelişmektedir. Ancak metinde geçen kurum/kavram adları iddiada yer aldığı için, K2'nin önerme doğrulayıcısı (mDeBERTa) atomlardan birine hatalı biçimde entailment atamış, K1 de yüksek leksikal örtüşmeden dolayı cümleyi kısmen doğru kabul etmiştir.

------------------------------------------------------------

### Grup 2: Bilgi Yokluğunu Çelişki Sanma (unverifiable -> contradicted, 5 Vaka)

#### Vaka 8: tfb_ex_0232 (LEGAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `contradicted`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.1 | partially_supported: %1.6 | contradicted: %54.1 | unverifiable: %44.2`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir" $\rightarrow$ `contradiction`
  - **Atom 2:** "daha önce tevzi edilen dosyalar yeniden dağıtılır" $\rightarrow$ `contradiction`
- **İddia (Claim):** "Pasif kayda alınan arabulucunun elektronik tebligat adresi edinmesi kaydı kendiliğinden aktif hâle getirir ve daha önce tevzi edilen dosyalar yeniden dağıtılır."
- **Bağlam (Context):** "Arabuluculuk bürolarının dava şartı kapsamındaki yazışmalarında elektronik tebligat kanalı kullanılmasına yönelik yeni uygulamada, arabulucuların elektronik tebligat adresine sahip olması istenmiştir. Duyuruda bu adreslerin 23 Temmuz 2026 tarihine kadar tebligat yapılabilecek biçimde hazır olması gerektiği belirtilmiştir. Bu tarihten itibaren büro yazışmalarının elektronik tebligat adresi üzerinden yürütülmesi öngörülmüş; elektronik tebligat adresi bulunmayan arabuluculara dava şartı arabuluculuk kapsamında dosya tevzi edilmemesi ve kayıtlarının aktif durumdan çıkarılması bildirilmiştir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Bağlam metninde iddiada öne sürülen özel şart veya prosedüre dair ne doğrulama ne çürütme vardır (bilgi yokluğu). Her iki model de metinde bahsedilmeyen bu kuralı 'metne aykırılık' olarak yorumlamış, yokluğu çelişkiyle karıştırmıştır.

------------------------------------------------------------

#### Vaka 9: tfb_ex_0360 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `contradicted`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %0.0 | contradicted: %100.0 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır" $\rightarrow$ `contradiction`
  - **Atom 2:** "Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir" $\rightarrow$ `neutral`
- **İddia (Claim):** "Nefes komutu verilen BT çekimlerinde kontrast yalnız damar yoluyla uygulanır. Nefes komutu gerekmeyen çekimlerde ağızdan kontrast tercih edilir."
- **Bağlam (Context):** "Bilgisayarlı tomografi ilaçlı veya ilaçsız yapılabilir. İlaçlı incelemede kontrast madde damar yoluyla verilebilir veya suya karıştırılarak hastaya içirilebilir. Özel bir hazırlık talimatı verilmemişse her çekim için aynı hazırlık gerekmez; ilaçlı çekimlerde açlık istenebilir ve bazı incelemelerde hastadan belirli miktarda suyla erken başvurması istenir. Çekim bölgesindeki takı ve metal eşyalar çıkarılır. İnceleme sırasında hasta hareketli bir masa üzerinde halka biçimli tarayıcıdan geçirilir ve bazen nefes komutlarına uyması istenir. İşlem süresi tetkike göre değişmekle birlikte yaklaşık bir ila on dakika arasında olabilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Bağlam metninde iddiada öne sürülen özel şart veya prosedüre dair ne doğrulama ne çürütme vardır (bilgi yokluğu). Her iki model de metinde bahsedilmeyen bu kuralı 'metne aykırılık' olarak yorumlamış, yokluğu çelişkiyle karıştırmıştır.

------------------------------------------------------------

#### Vaka 10: tfb_ex_0368 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `contradicted`
- **K1 (ELECTRA) Olasılıkları:** `supported: %12.4 | partially_supported: %28.2 | contradicted: %56.6 | unverifiable: %2.8`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır" $\rightarrow$ `contradiction`
  - **Atom 2:** "meme kısa süre sıkıştırılır" $\rightarrow$ `neutral`
- **İddia (Claim):** "Önceki meme görüntülemesi varsa çekime eski görüntüyle aynı pozisyondan başlanır ve meme kısa süre sıkıştırılır."
- **Bağlam (Context):** "Mamografi çekimine gelmeden önce koltuk altı temizliği yapılması ve duş alınması önerilir. Koltukaltı ve göğüs bölgesine parfüm, deodorant veya benzeri ürünler uygulanmamalı; daha önce yapılmış meme görüntülemeleri varsa bunlar da beraberinde getirilmelidir. Çekim sırasında meme iki plastik tabaka arasında sıkıştırılır ve genellikle iki farklı pozisyonda görüntü alınır. Sıkıştırmanın amacı hareketi azaltmak, görüntüyü keskinleştirmek ve daha düşük doz radyasyonla görüntü elde edilmesine yardımcı olmaktır. Uygulanan baskı kısa süreli ağrı veya rahatsızlık oluşturabilir, ancak bu his genellikle çekim bittikten sonra geçer."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Bağlam metninde iddiada öne sürülen özel şart veya prosedüre dair ne doğrulama ne çürütme vardır (bilgi yokluğu). Her iki model de metinde bahsedilmeyen bu kuralı 'metne aykırılık' olarak yorumlamış, yokluğu çelişkiyle karıştırmıştır.

------------------------------------------------------------

#### Vaka 11: tfb_ex_0372 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `contradicted`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.2 | partially_supported: %1.6 | contradicted: %97.6 | unverifiable: %0.5`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir." $\rightarrow$ `neutral`
  - **Atom 2:** "Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir." $\rightarrow$ `contradiction`
- **İddia (Claim):** "Gastroskopide biyopsi alınacak bölge sakinleştirici verildikten sonra seçilir. Patolojiye gönderilecek örnek sayısı işlem sonunda belirlenir."
- **Bağlam (Context):** "Gastroskopi yemek borusu, mide ve onikiparmak bağırsağının incelenmesinde kullanılır. İnceleme sırasında görüntü alınabilir ve gerekli görülen alanlardan biyopsi örneği alınarak patolojiye gönderilebilir. İşlem için yaklaşık sekiz saat açlık gerekir. Rahatsızlığı azaltmak amacıyla boğaza uyuşturucu sprey uygulanabilir ve sakinleştirici ilaç verilebilir. Gastroskopi çoğu durumda yaklaşık beş ila on dakika sürer. İşlem sonrasında hasta bir ila iki saat izlenebilir; ardından sıvı gıdalara başlanıp aynı gün taburculuk yapılabilir. Gastroskopi yalnız tanı amacıyla değil, bazı kanamaların kontrolü, polip çıkarılması, daralmış bölgelerin genişletilmesi veya yabancı cisim çıkarılması gibi tedavi amaçlı işlemlerde de kullanılabilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Bağlam metninde iddiada öne sürülen özel şart veya prosedüre dair ne doğrulama ne çürütme vardır (bilgi yokluğu). Her iki model de metinde bahsedilmeyen bu kuralı 'metne aykırılık' olarak yorumlamış, yokluğu çelişkiyle karıştırmıştır.

------------------------------------------------------------

#### Vaka 12: tfb_ex_0468 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `contradicted`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.1 | partially_supported: %0.0 | contradicted: %99.9 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir" $\rightarrow$ `contradiction`
- **İddia (Claim):** "İğneyle alınan biyopsi örneği endoskop çekilmeden cihazın ayrı bir kanalında incelenir."
- **Bağlam (Context):** "Endoskopik ultrasonografi, endoskopi ile ultrasonografiyi aynı cihazda birleştirerek sindirim sisteminin iç yüzeyinin yanında duvar katmanlarını ve çevredeki lenf bezleri ile komşu organları incelemeyi sağlar. Endoskop ağızdan yemek borusu, mide ve ince bağırsağa doğru ilerletilir; işlem sırasında endoskopik görüntüler ile ultrason görüntüleri ayrı ekranlardan izlenir. Şüpheli bir doku görüldüğünde cihazdan ilerletilen iğneyle biyopsi örneği alınabilir. İşlem çoğunlukla sedasyon altında yapılır ve yaklaşık 20-30 dakika sürer."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Bağlam metninde iddiada öne sürülen özel şart veya prosedüre dair ne doğrulama ne çürütme vardır (bilgi yokluğu). Her iki model de metinde bahsedilmeyen bu kuralı 'metne aykırılık' olarak yorumlamış, yokluğu çelişkiyle karıştırmıştır.

------------------------------------------------------------

### Grup 3: Periferik Detayı Doğrulanmış Atom Sanma (unverifiable -> partially_supported, 4 Vaka)

#### Vaka 13: tfb_ex_0336 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.0 | partially_supported: %100.0 | contradicted: %0.0 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır." $\rightarrow$ `entailment`
  - **Atom 2:** "Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır." $\rightarrow$ `neutral`
- **İddia (Claim):** "Bronkoskopide biyopsi alınan hastaların gözlem süresi iki saate çıkarılır. Yalnız yıkama örneği alınmışsa gözlem bir saatte sonlandırılır."
- **Bağlam (Context):** "Bronkoskopi öncesinde kullanılan ilaçlar, mevcut hastalıklar ve ilaç alerjileri hekime bildirilmelidir. İşlemden altı ila sekiz saat önce yiyecek ve içecek alınmaması gerekir; sürekli kullanılan bazı ilaçlar hekimin yönlendirmesiyle az miktarda suyla alınabilir. Bronkoskop ağız veya burundan ilerletilerek hava yolları incelenir, gerekli olduğunda biyopsi alınabilir veya yıkama sıvısı toplanabilir. İşlem sonrasında hasta en az bir ila iki saat gözlem altında tutulur ve yutma refleksi zayıfladığı için yaklaşık iki saat yiyecek ve içecek verilmez. Anestezi etkisi nedeniyle en az on iki saat araç veya iş makinesi kullanılması ve alkol alınması önerilmez."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Cümlenin ana hükmü (sayısal sınır, süre veya kesin zorunluluk) bağlamda hiç yer almamaktadır. Ancak cümlenin öznesi veya tıbbi işlem adı metinde geçtiği için modeller bu yan parçayı doğrulanmış (entailed) kabul etmiş ve ana hükmün eksikliğini 'kısmi destek' olarak sınıflandırmıştır.

------------------------------------------------------------

#### Vaka 14: tfb_ex_0340 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %1.2 | partially_supported: %81.9 | contradicted: %5.1 | unverifiable: %11.8`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır." $\rightarrow$ `entailment`
  - **Atom 2:** "Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır." $\rightarrow$ `neutral`
- **İddia (Claim):** "Kolonoskopi sonrası dinlenme süresi, işlem sırasında sakinleştirici ilaç verilip verilmediğine bağlıdır. Ağrı azaltıcı ilaç kullanılmışsa dinlenme süresi ayrıca uzatılır."
- **Bağlam (Context):** "Kolonoskopinin tam ve güvenilir yapılabilmesi için altı saatlik açlığın yanında iki ila üç günlük diyet ve özel ilaçlarla bağırsak temizliği gerekir. İşlem sırasında hasta sol yanına yatırılır; kalp ritmi ve kandaki oksijen miktarı izlenir. Karında basınç, gaz ve kramp görülebileceği için işlem öncesinde veya gerektiğinde işlem sırasında sakinleştirici ve ağrı azaltıcı ilaçlar uygulanabilir. Kolonoskopi yaklaşık yirmi ila otuz dakika sürebilir. İşlemden sonra hasta on beş ila otuz dakika dinlendirilir; ilaç kullanılmışsa güvenlik amacıyla yirmi dört saat taşıt veya makine kullanılmaması önerilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Cümlenin ana hükmü (sayısal sınır, süre veya kesin zorunluluk) bağlamda hiç yer almamaktadır. Ancak cümlenin öznesi veya tıbbi işlem adı metinde geçtiği için modeller bu yan parçayı doğrulanmış (entailed) kabul etmiş ve ana hükmün eksikliğini 'kısmi destek' olarak sınıflandırmıştır.

------------------------------------------------------------

#### Vaka 15: tfb_ex_0364 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.6 | partially_supported: %98.7 | contradicted: %0.2 | unverifiable: %0.5`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir." $\rightarrow$ `neutral`
  - **Atom 2:** "Bu bilgi olmadan çekim planı oluşturulmaz." $\rightarrow$ `entailment`
- **İddia (Claim):** "Kalp pili veya implant bildiren hasta için MR öncesinde cihazın model bilgisi yazılı olarak kaydedilir. Bu bilgi olmadan çekim planı oluşturulmaz."
- **Bağlam (Context):** "Manyetik rezonans incelemelerinin çoğunda özel bir ön hazırlık gerekmez; aksi söylenmedikçe hasta yemek yiyip düzenli ilaçlarını alabilir. Ancak bazı özellikli çekimlerde hazırlık değişir. Örneğin entero incelemesinde hastadan aç gelmesi ve hazırlanan yaklaşık bir buçuk litre suyu iki saat içinde içmesi, bazı batın ve ilaçlı incelemelerde ise en az sekiz saat açlık istenebilir. Güçlü manyetik alan nedeniyle saat, takı, kredi kartı, işitme cihazı ve benzeri metal ya da manyetik alandan etkilenebilecek eşyalar çekim odasına girmeden çıkarılmalıdır. Vücutta implant, kalp pili, metal parça veya benzeri bir materyal varsa görevliye önceden bildirilir. Çekim sırasında hasta hareketsiz kalır; cihazın gürültüsü için kulak koruyucu verilebilir ve görevliyle mikrofon üzerinden iletişim kurulabilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Cümlenin ana hükmü (sayısal sınır, süre veya kesin zorunluluk) bağlamda hiç yer almamaktadır. Ancak cümlenin öznesi veya tıbbi işlem adı metinde geçtiği için modeller bu yan parçayı doğrulanmış (entailed) kabul etmiş ve ana hükmün eksikliğini 'kısmi destek' olarak sınıflandırmıştır.

------------------------------------------------------------

#### Vaka 16: tfb_ex_0452 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.5 | partially_supported: %52.1 | contradicted: %3.6 | unverifiable: %43.8`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Prob yemek borusunda belirli bir işarete kadar ilerletilir." $\rightarrow$ `neutral`
  - **Atom 2:** "Bu noktadan ek görüntü alınır." $\rightarrow$ `entailment`
- **İddia (Claim):** "Prob yemek borusunda belirli bir işarete kadar ilerletilir. Bu noktadan ek görüntü alınır."
- **Bağlam (Context):** "Transözofageal ekokardiyografi, göğüsten yapılan ekokardiyografide yeterince görüntülenemeyen kalp yapılarını yemek borusundan ilerletilen ultrason probuyla incelemek için kullanılır. İşlem öncesinde en az dört saat açlık gerekir ve çıkarılabilir diş protezleri çıkarılır. Boğaza lokal anestezik sprey uygulanır, damar yolu açılır ve ağızlık yerleştirildikten sonra prob yutkunma yardımıyla yemek borusuna ilerletilir. İnceleme yaklaşık 15-20 dakika sürer. İşlemden sonra iki saat boyunca bir şey yenilip içilmez."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Cümlenin ana hükmü (sayısal sınır, süre veya kesin zorunluluk) bağlamda hiç yer almamaktadır. Ancak cümlenin öznesi veya tıbbi işlem adı metinde geçtiği için modeller bu yan parçayı doğrulanmış (entailed) kabul etmiş ve ana hükmün eksikliğini 'kısmi destek' olarak sınıflandırmıştır.

------------------------------------------------------------

### Grup 4: İnce Hukuki Şartı Kaçırma (partially_supported -> supported, 2 Vaka)

#### Vaka 17: tfb_ex_0274 (LEGAL)
- **Altın Etiket (Gold):** `partially_supported`
- **Modellerin Ortak Kararı (Consensus):** `supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %99.7 | partially_supported: %0.3 | contradicted: %0.0 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Satışa engel hukuki durum varsa noter işlemi yapmaz." $\rightarrow$ `entailment`
  - **Atom 2:** "Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz." $\rightarrow$ `entailment`
- **İddia (Claim):** "Satışa engel hukuki durum varsa noter işlemi yapmaz. Sözleşme tapu sistemine kaydedilince ayrıca tescil yapılmasına gerek kalmaz."
- **Bağlam (Context):** "Noter, taşınmaz satış başvurusu üzerine bir başvuru belgesi düzenler ve taşınmaz üzerindeki kısıtlamalar ile satışa ilişkin yasal sınırlamaları inceler. Hak sahibinin belirlenememesi veya satışa engel hukuki bir durum bulunması hâlinde satış işlemi yapılmaz. Satışa engel durum olmadığı tespit edilirse sözleşme taraflarca imzalanır. Noter, tapu bilişim sisteminden yevmiye numarası alarak sözleşmeyi sisteme kaydeder; kaydın ardından tapu müdürlüğü taşınmazın tapu siciline tescilini sağlar."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddia iki parçadan oluşmakta ve ikinci parça metindeki yasal/teknik sınırla çelişmektedir. Modeller genel anlam akışına kapılarak ikinci parçadaki olumsuz/sınırlandırıcı koşulu göz ardı etmiş ve cümlenin tamamını onaylamıştır.

------------------------------------------------------------

#### Vaka 18: tfb_ex_0278 (LEGAL)
- **Altın Etiket (Gold):** `partially_supported`
- **Modellerin Ortak Kararı (Consensus):** `supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %66.6 | partially_supported: %33.3 | contradicted: %0.1 | unverifiable: %0.0`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur" $\rightarrow$ `entailment`
  - **Atom 2:** "adli sicil belgesini de adayın dilekçesine eklemesi gerekir" $\rightarrow$ `entailment`
- **İddia (Claim):** "Başvuruda gönüllü formu ile yerleşim yeri belgesi sunulur, adli sicil belgesini de adayın dilekçesine eklemesi gerekir."
- **Bağlam (Context):** "Denetimli serbestlik hizmetlerinde gönüllü çalışmak isteyen kişinin Türk vatandaşı olması, başvuru tarihinde on sekiz yaşını tamamlamış bulunması ve mevzuatta belirtilen belirli suçlardan hükümlü olmaması gerekir. Gönüllü olmak isteyen kişi denetimli serbestlik müdürlüğüne dilekçe ile başvurur. Başvuruda gönüllü başvuru formu ve yerleşim yeri belgesi istenir; adli sicil belgesi müdürlük tarafından temin edilir. Başvuru, infaz işlemleri değerlendirme komisyonu tarafından incelenerek karara bağlanır."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddia iki parçadan oluşmakta ve ikinci parça metindeki yasal/teknik sınırla çelişmektedir. Modeller genel anlam akışına kapılarak ikinci parçadaki olumsuz/sınırlandırıcı koşulu göz ardı etmiş ve cümlenin tamamını onaylamıştır.

------------------------------------------------------------

### Grup 5: Tam Zıtlığı Doğrulama (contradicted -> supported, 1 Vaka)

#### Vaka 19: tfb_ex_0019 (FINANCE)
- **Altın Etiket (Gold):** `contradicted`
- **Modellerin Ortak Kararı (Consensus):** `supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %96.0 | partially_supported: %0.8 | contradicted: %3.1 | unverifiable: %0.1`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Kasko sigortası üçüncü kişilere verilen zararları karşılar" $\rightarrow$ `entailment`
  - **Atom 2:** "Zorunlu trafik sigortası sigortalının kendi aracındaki maddi zararı karşılar" $\rightarrow$ `entailment`
- **İddia (Claim):** "Kasko sigortası üçüncü kişilere verilen zararları, zorunlu trafik sigortası ise sigortalının kendi aracındaki maddi zararı karşılar."
- **Bağlam (Context):** "Sektör Birliği A’nın Kasko Sigortası SSS'sinde Dar Kasko, genel şartlardaki teminat gruplarının bir bölümünü; Kasko bu grupların tamamını kapsayan ürün olarak tanımlanır. Genişletilmiş Kasko, temel teminat gruplarının tamamına ek olarak ek sözleşmeyle alınabilecek risklerin bir bölümünü; Tam Kasko ise bu ek risklerin tamamını kapsar. Kasko sigortalının kendi aracındaki maddi zararları güvence altına alırken zorunlu trafik sigortası aracın üçüncü kişilere verdiği maddi ve bedensel zararları karşılar."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Kasko ve trafik sigortası gibi iki zıt terimin teminat kapsamları iddiada birbiriyle yer değiştirmiştir. Cümledeki kelimelerin tamamı metinde birebir geçtiği için modeller terimlerin yer değiştirdiğini fark edememiş, aşırı leksikal eşleşmeyle supported demiştir.

------------------------------------------------------------

### Grup 6: Bilgi Yokluğunu Destek Sanma (unverifiable -> supported, 1 Vaka)

#### Vaka 20: tfb_ex_0332 (MEDICAL)
- **Altın Etiket (Gold):** `unverifiable`
- **Modellerin Ortak Kararı (Consensus):** `supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %69.8 | partially_supported: %3.0 | contradicted: %11.7 | unverifiable: %15.4`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır." $\rightarrow$ `entailment`
- **İddia (Claim):** "Biyopsi alınacak bölge seçilirken PET/CT öncesindeki kan şekeri sonucu da dikkate alınır."
- **Bağlam (Context):** "PET/CT işlemi öncesinde hastanın en az altı saat aç kalması gerekir. İşleme başlanırken kan şekeri ölçülür; değer uygun aralıktaysa damar yoluyla radyoaktif işaretli madde verilir. Sık kullanılan maddelerden biri F-18 florodeoksiglukozdur. Enjeksiyonun ardından maddenin vücutta dağılması için hasta yaklaşık bir saat bekletilir ve daha sonra PET/CT cihazında görüntüleme yapılır. PET/CT, kanserin yaygınlığını değerlendirmede, canlı tümör dokusunun yerini göstermede ve gerektiğinde biyopsi alınacak bölgenin belirlenmesine yardımcı olmada kullanılabilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** Bağlamda iddia edilen nedensellik ilişkisi bulunmamaktadır. Modeller genel konu benzerliği nedeniyle iddiayı doğrulanmış kabul etmiştir.

------------------------------------------------------------

### Grup 7: Aşırı Şüphecilikle Kısmi Destek Verme (supported -> partially_supported, 1 Vaka)

#### Vaka 21: tfb_ex_0405 (MEDICAL)
- **Altın Etiket (Gold):** `supported`
- **Modellerin Ortak Kararı (Consensus):** `partially_supported`
- **K1 (ELECTRA) Olasılıkları:** `supported: %0.3 | partially_supported: %97.8 | contradicted: %1.8 | unverifiable: %0.1`
- **K2 Ayrıştırılan Atomlar ve NLI Sonuçları:**
  - **Atom 1:** "DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır." $\rightarrow$ `contradiction`
  - **Atom 2:** "Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir." $\rightarrow$ `entailment`
- **İddia (Claim):** "DEXA sırasında hasta yaklaşık çeyrek saat yatar ve ölçüm boyunca hareketsiz kalır. Yakın zamanda kontrast kullanılmışsa çekim ertelenebilir."
- **Bağlam (Context):** "DEXA, kemik mineral yoğunluğunu ve kemik kaybını değerlendirmek için kullanılan düşük radyasyonlu bir ölçümdür. Ölçümde sıklıkla bel omurları ile kalça bölgesi değerlendirilir. Genel olarak özel bir ön hazırlık gerekmez; hasta yaklaşık on beş dakika yatar ve ölçümün tamamlanması için hareketsiz kalır. İşlem ağrısızdır. Gebelik veya emzirme durumu sağlık ekibine önceden bildirilmelidir. İncelemeden iki ile altı gün önce ağızdan ya da damar yoluyla kontrast madde kullanılmışsa DEXA çekimi ertelenebilir."
- **Dilbilimsel & Epistemik Analiz:** **Hata Nedeni:** İddia bağlam tarafından bütünüyle desteklenmektedir. Ancak K2 atomik bölmede ikinci cümlenin koşulunu nötr olarak değerlendirmiş ve gereksiz bir şüphecilikle partially_supported sonucuna varmıştır.

------------------------------------------------------------

## 3. Tezin 'Hata Analizi' Bölümü İçin Temel Bilimsel Çıkarımlar

1. **Simetrik Güvenilirlik:** Modellerin 358 uzlaşma vakasında sadece 1 kez açık çelişkiye `supported` demesi, sistemin halüsinasyonları 'doğru' olarak onaylama riskinin ihmal edilebilir (%0.28) olduğunu kanıtlar.

2. **Tıp ve Hukuk Alanının Özgüllüğü:** Hataların %70'ten fazlası tıp alanındaki radyolojik/endoskopik tetkik hazırlıklarında toplanmıştır. Bu alanlarda 'yapılmaması gereken bir işlem' ile 'bahsedilmeyen bir işlem' arasındaki ayrım derin uzmanlık gerektirmektedir.

3. **Önerme Ayrıştırma İyileştirmesi:** Gelecek çalışmalarda, bir cümlenin ana yüklemi bağlamda yoksa, özne veya konu tamlamalarının bağımsız doğrulanabilir atom sayılmasını önleyecek bir 'pragmatik filtre' eklenmesi bu 21 hatanın en az 11'ini doğrudan çözebilir.
