# Gold-480 anotatör sağlamlık analizi

Gold v1.0 etiketleri 48/48 uyuşmazlıkta Annotator A lehine çözülmüştür (A = veri setini oluşturan araştırmacı;
bkz. `gold_v1.0/provenance/ANNOTATOR_ROLES_ERRATUM_TR_v1.0.1.md`). Bu tablo, sonuçların bu uzlaşmaya bağlı olup
olmadığını sınamak için tüm sistemleri üç referansa göre puanlar.

Üretim: `python scripts/77_gold480_annotator_robustness.py` · uzlaşılan alt küme n = 432

| Sistem | Gold v1.0 (= A) Acc | Gold v1.0 (= A) Macro-F1 | Annotator B Acc | Annotator B Macro-F1 | A = B agreed subset Acc | A = B agreed subset Macro-F1 |
|---|---:|---:|---:|---:|---:|---:|
| K1 (ELECTRA-TR) | 0.8313 | 0.8301 | 0.7812 | 0.7841 | 0.8449 | 0.8425 |
| K2 (Gemma atomizer + mDeBERTa, soft-prob) | 0.8042 | 0.8065 | 0.7458 | 0.7494 | 0.8125 | 0.8110 |
| Hybrid + Llama-3.3-70B V4 (prompt tuned on gold) | 0.9313 | 0.9315 | 0.8667 | 0.8683 | 0.9468 | 0.9457 |
| Hybrid + Gemma-4-26B blind zero-shot | 0.9229 | 0.9223 | 0.8500 | 0.8527 | 0.9306 | 0.9287 |
| Standalone GPT-4.1-mini 8-shot | 0.9104 | 0.9098 | 0.8604 | 0.8587 | 0.9306 | 0.9254 |
| Standalone Gemma-4-26B zero-shot | 0.9042 | 0.9022 | 0.8250 | 0.8269 | 0.9097 | 0.9054 |

Yorum: Üç referansta da K1 > K2 sıralaması ve hibrit sistemlerin K1/K2'den üstünlüğü korunur.
Hibrit ile tek başına güçlü LLM arasındaki sıra referansa göre değişebilir (B'ye göre GPT-4.1-mini >
kör Gemma hibriti); bu farklar Gold-480'de zaten istatistiksel olarak anlamlı değildir.

Not: V4 hakem istemi Gold-480 uyuşmazlıkları üzerinde geliştirildiği için held-out sonuç değildir.
