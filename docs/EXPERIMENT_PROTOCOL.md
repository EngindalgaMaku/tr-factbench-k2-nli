# K2 Deney Protokolü

## K2-00 — Veri doğrulama

- JSONL parse kontrolü
- zorunlu alanlar
- izin verilen etiketler
- benzersiz example_id
- context grubu bütünlüğü
- domain/etiket dağılımı
- hash manifesti
- truncation risk dağılımı

## K2-10 — Zero-shot model seçimi

Girdi: `general_model_selection_nli3.jsonl`

Birincil metrik: macro-F1.

İkincil metrikler: accuracy, sınıf bazlı P/R/F1, MCC, NLL, multiclass Brier, ECE, latency ve peak GPU memory.

Bütün modeller aynı örnek sırası ve aynı tokenizer truncation politikasıyla çalıştırılır. Model seçimi yalnız nokta tahminine göre değil, paired bootstrap güven aralığı ve McNemar testiyle raporlanır.

## K2-20 — Calibration

Girdi: `general_calibration_nli3.jsonl`.

Raw argmax sonuçları korunur. Temperature scaling veya sınıf-eşiği varyantları ayrı run kimliğiyle kaydedilir. Calibration sonucu model seçim setinde öğrenilmez.

## K2-30 — Gold atom

Dengeli 240 claim üzerinde insan atomlaştırması ve her atom için entailment/neutral/contradiction etiketi hazırlanır. Bir alt küme ikinci annotator tarafından kontrol edilirse atom sınırı ve NLI etiketi için anlaşma ayrıca raporlanır.

## K2-40 — Tam pipeline

Girdi atom dosyası atomizer sürümü, checkpoint hash'i, generation parametreleri ve claim hash'i taşır. NLI klasörü atomizer çalıştırmaz.

## K2-50 — Ablation

- raw vs calibrated
- claim-level vs predicted atoms vs gold atoms
- context_only vs role-tagged question/context
- truncation alt grupları
- atom sayısı alt grupları
- domain ve zorluk alt grupları

## K2-60 — Raporlama

Her run için:

- manifest.json
- predictions.jsonl
- metrics.json
- confusion_matrix.csv
- class_metrics.csv
- figures/

Model karşılaştırması için:

- macro-F1 + %95 CI
- paired difference + %95 CI
- McNemar exact p
- Holm düzeltmesi
- performans/latency/memory tablosu
