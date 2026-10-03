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

- `joeddav/xlm-roberta-large-xnli` — panel adayı
- `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` — güçlü ve daha verimli rakip
- `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` — K2-10 seçimi (Macro-F1 0.8684, 486 örnek, 3-sınıf)
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

## Resmi Held-Out Gold 480 Sonuçları (K2 vs K1)

TR-FactBench v1.0 resmi 480 örneklik held-out altın test kümesi üzerinde K2 uçtan uca boru hattı (`K2-PIPE-PRED-GOLD480-v1`) ve K1 (`ELECTRA-TR + LoRA`) kafa kafaya karşılaştırma sonuçları:

| Metrik / Sınıf | K1 (ELECTRA-TR + LoRA) | K2 (Gemma-4 QLoRA + mDeBERTa-v3) | Fark / Üstünlük |
|:---|:---:|:---:|:---:|
| **Macro-F1** | **0.8300** | **0.7830** | K1 +0.047 |
| **Genel Doğruluk (Accuracy)** | **%83.13** | **%78.24** (Strict: %77.92) | K1 +%4.89 |
| **MCC (Matthews Corr.)** | 0.7750 | 0.7136 | K1 +0.061 |
| **Atomizer Kapsaması (Coverage)** | — | **%99.58** (478/480) | 996 atom üretildi |
| **Supported F1** | **0.9090** | 0.8175 | K1 üstün |
| **Partially Supported F1** | **0.8080** | 0.7287 | K1 üstün |
| **Contradicted F1** | 0.7920 | **0.8017** | **K2 Üstün (+0.0097) 🚀** |
| **Unverifiable F1** | **0.8120** | 0.7843 | K1 üstün |

### K1 vs K2 İkili Anlaşma ve Oracle Tavanı (AP3)

- **Ham Uyuşma (Raw Agreement):** 353 / 480 (%73.54)
- **İkisinin de Doğru Bildiği:** 330 / 480 (%68.75)
- **Yalnızca K1'in Doğru Bildiği:** 69 / 480 (%14.37)
- **YALNIZCA K2'NİN DOĞRU BİLDİĞİ:** **44 / 480 (%9.17)** *(K1'in kaçırdığı 44 hatayı K2 tek başına kurtarmıştır; 17'si Tıp alanındadır).*
- **İkisinin de Yanıldığı:** 37 / 480 (%7.71)
- **ORACLE HİBRİT TAVANI (K1 OR K2):** **443 / 480 (%92.29)** *(Bileşen 3 LLM Hakem için teorik tavan).*

Detaylı deney raporu, SVG grafikleri ve hata matrisleri için: [`reports/experiments/K2-PIPE-PRED-GOLD480-v1/README.md`](reports/experiments/K2-PIPE-PRED-GOLD480-v1/README.md)  
İnsan gözüyle dilbilimsel ve niteliksel vaka analizi için: [`reports/K2_QUALITATIVE_ANALYSIS_GOLD480.md`](reports/K2_QUALITATIVE_ANALYSIS_GOLD480.md)

## Sıralı deneyler

1. `K2-00` — veri ve şema denetimi
2. `K2-10` — claim-level üç sınıflı zero-shot model seçimi
3. `K2-20` — calibration ve threshold ablation
4. `K2-30` — human gold-atom verifier değerlendirmesi
5. `K2-40` — sürümlenmiş atomizer çıktılarıyla gerçek dört sınıflı K2 pipeline (`K2-PIPE-PRED-GOLD480-v1` ✅)
6. `K2-50` — ablation ve hata analizi (`K2_QUALITATIVE_ANALYSIS_GOLD480.md` ✅)
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

## Citation & Benchmark Reference

If you use this modular verification pipeline or evaluate on the TR-FactBench benchmark splits, please cite the foundational benchmark paper:

```bibtex
@inproceedings{dalga2026source,
  title={Source-Grounded Factuality Verification in Turkish: A Multi-Domain Experimental Study},
  author={Dalga, Engin and Ball{\i}, Serkan},
  booktitle={2026 10th International Symposium on Multidisciplinary Studies and Innovative Technologies (ISMSIT)},
  year={2026},
  pages={1--6},
  publisher={IEEE}
}
```

> **Ecosystem Note:** The foundational dataset splits, annotation guidelines, and K1 direct encoder baselines are maintained in the companion repository: [tr-factbench](https://github.com/EngindalgaMaku/tr-factbench).


