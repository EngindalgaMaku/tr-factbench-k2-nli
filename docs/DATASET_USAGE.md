# Veri Setlerinin K2'de Kullanımı

## İncelenen dosyalar

| Veri | Örnek | Benzersiz bağlam | Domain | Etiket yapısı |
|---|---:|---:|---:|---|
| dev_general | 960 | 240 | 3 | Her context için 4 claim; sınıflar yaklaşık dengeli |
| dev_stress | 600 | 150 | 3 | Her context için 4 claim; sınıflar yaklaşık dengeli |

Her iki dosya da `single_annotator_provisional` ve `single_annotator_blind_human` olarak işaretlidir. Bu durum insan anotasyonu bulunduğunu gösterir, fakat çift anotasyon/adjudication yapılmadığını da açıkça belirtir.

## Neleri doğrudan değerlendirebiliriz?

### Claim-level zero-shot NLI

`partially_supported` çıkarıldıktan sonra:

- `supported -> entailment`
- `contradicted -> contradiction`
- `unverifiable -> neutral`

Bu dönüşüm claim-level üç sınıflı model seçimi için kullanılabilir. `partially_supported` karışık bir claim olduğu için tek bir NLI etiketine dönüştürülemez.

### Tam K2 pipeline

Atomizer çıktıları hazır olduğunda dört sınıfın tamamı kullanılabilir. Atom NLI kararları claim seviyesinde şu kuralla birleştirilir:

- bütün atomlar entailment -> supported
- en az bir entailment ve en az bir neutral/contradiction -> partially_supported
- entailment yok ve en az bir contradiction -> contradicted
- bütün atomlar neutral -> unverifiable

### Atom verifier değerlendirmesi

Claim-level etiket atomların ayrı ayrı etiketlerini belirlemez. Özellikle `partially_supported` ve çok atomlu `contradicted` claim'lerde hangi atomun hangi NLI etiketini taşıdığı claim etiketinden çıkarılamaz. Bu nedenle atom-level gold alt küme zorunludur.

## Önerilen rol dağılımı

`dev_general`, context_id seviyesinde ve domain dengesi korunarak üç parçaya ayrılır:

- model_selection: domain başına 54 context
- calibration: domain başına 13 context
- internal_eval: domain başına 13 context

Aynı context'e ait dört claim kesinlikle farklı bölümlere dağıtılmaz.

`dev_stress` bölünmez ve model seçimi/calibration için kullanılmaz. Yalnız challenge değerlendirmesi yapılır.

## Nihai sonuç dili

Bu dosyalar `dev` ve tek annotator provisional olduğu için raporda şu ifadeler kullanılır:

- "development evaluation"
- "stress/challenge evaluation"
- "single-annotator human labels"

Şu ifadeler kullanılmaz:

- "unseen final test" (ayrı test dosyası yoksa)
- "adjudicated gold"
- "inter-annotator agreement" (ikinci annotator yoksa)
