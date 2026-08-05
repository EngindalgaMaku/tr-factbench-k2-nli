# K2 — Atom-Tabanlı Zero-Shot NLI Deney Hattı

Bu klasör, K1'deki task-specific ELECTRA hattından ayrı olarak K2'nin bilimsel ve tekrar üretilebilir deneylerini yürütür.
K2'nin temel amacı, önceden atomize edilmiş claim'leri hazır çok dilli NLI modelleriyle doğrulamak ve atom kararlarını dört sınıflı claim kararına deterministik biçimde birleştirmektir.

## Deneysel ayrım

- **K1:** task-specific, doğrudan dört sınıflı sınıflandırıcı.
- **K2-ZS:** TR-FactBench üzerinde fine-tune edilmemiş hazır NLI modeli + atomlar + sabit aggregation.
- **K2-Cal:** ayrı calibration bölümü üzerinde eşik/kalibrasyon öğrenilmiş K2 varyantı.
- **K2-FT:** ileride eklenebilecek task-adapted atom verifier; K2-ZS ile karıştırılmaz.

Atomizer bu klasörün parçası değildir. K2 yalnızca sürümlenmiş atom JSONL dosyalarını girdi olarak kabul eder.

## Veri rolleri

`dev_general.jsonl` ve `dev_stress.jsonl` tek-annotator insan etiketli claim-level veri setleridir. Dosyalardaki resmi durum `single_annotator_provisional` olduğundan, bunlar "adjudicated gold test" olarak adlandırılmaz.

- `dev_general`: context-group seviyesinde model seçimi, calibration ve internal evaluation bölümlerine ayrılır.
- `dev_stress`: model seçimi ve eşik ayarında kullanılmadan stres/challenge değerlendirmesi için korunur.
- Claim-level etiketler tam K2 pipeline'ını değerlendirmek için yeterlidir.
- Atom verifier'ı tek başına değerlendirmek için atom metni + atom-level NLI etiketi gerekir. Bunun için dengeli bir 240 örneklik annotation şablonu üretilir.

## İlk model paneli

- `joeddav/xlm-roberta-large-xnli` — mevcut ana aday
- `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` — güçlü ve daha verimli rakip
- `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` — geniş NLI eğitimli rakip
- `MoritzLaurer/xlm-v-base-mnli-xnli` — vocabulary ablation adayı
- `emrecan/convbert-base-turkish-mc4-cased-allnli_tr` — monolingual Türkçe kontrol modeli

Model seçimi yalnız `general_model_selection_nli3` üzerinde yapılır. Stress sonuçları model seçimini değiştirmek için kullanılmaz.

## İlk kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/00_validate_data.py
python scripts/01_prepare_splits.py
pytest -q
```

## Sıralı deneyler

1. `K2-00` — veri ve şema denetimi
2. `K2-10` — claim-level üç sınıflı zero-shot model seçimi
3. `K2-20` — calibration ve threshold ablation
4. `K2-30` — human gold-atom verifier değerlendirmesi
5. `K2-40` — sürümlenmiş atomizer çıktılarıyla gerçek dört sınıflı K2 pipeline
6. `K2-50` — ablation ve hata analizi
7. `K2-60` — tablolar, grafikler ve nihai rapor

## Temel ilkeler

- `partially_supported` hiçbir zaman claim-level `neutral` sınıfına çevrilmez.
- Model seçimi için üç sınıflı claim-level deneyde `partially_supported` örnekler dışarıda bırakılır.
- Dört sınıflı pipeline değerlendirmesinde bütün örnekler kullanılır.
- Etiket sırası bütün metriklerde açıkça sabittir.
- Atom hypothesis hiçbir zaman truncate edilmez; gerektiğinde yalnız premise kısaltılır.
- Her run değiştirilemez bir klasöre, veri hash'i ve model revision bilgisiyle yazılır.
- Aynı run kimliği üzerine yazılmaz.

Ayrıntılı kullanım için `docs/EXPERIMENT_PROTOCOL.md` ve `docs/DATASET_USAGE.md` dosyalarına bakın.
# tr-factbench-k2-nli
