# AP6 — Anotatörler arası uyum (uzlaşmadan önce) — v1 (2026-10-08)

Kapsam: Anotatör B'nin 50 cümlesi (items_B.jsonl, rastgele seçim seed 44, sıra seed 45). Anotatör A: aynı cümlelerin census etiketleri.
Etiketler sistem tahminleri görülmeden verildi; B, A'nın etiketlerini görmedi. Değerler uzlaşmadan öncedir.
Güven aralıkları: madde düzeyinde 10.000 bootstrap (seed 42), yüzdelik yöntem.

| Ölçü | n | Ham uyum | Cohen κ [%95 GA] |
|---|---:|---:|---|
| 5 kategori (çekimser + 4 sınıf) | 50 | 41/50 (%82) | 0,582 [0,334, 0,792] |
| Çekimser ayrımı (evet/hayır) | 50 | 45/50 (%90) | 0,558 |
| 4 sınıf (ikisinin de bilgi veren dediği cümleler) | 41 | 37/41 (%90) | 0,633 [0,303, 0,900] |
| İkili: supported / supported değil (aynı 41 cümle) | 41 | 39/41 (%95) | 0,806 |

Dağılım — A: supported 37, çekimser 7, contradicted 4, unverifiable 1, partially_supported 1.
B: supported 37, çekimser 6, partially_supported 3, unverifiable 2, contradicted 2.

Uyuşmazlıklar (9): 5'i çekimser / bilgi veren ayrımında (AP6-0396, AP6-0311, AP6-0036, AP6-0711, AP6-0865),
4'ü sınıf ayrımında (AP6-0489, AP6-0388, AP6-0231, AP6-0583).

Not: Örneklem küçük ve dengesizdir (cümlelerin ~%74'ü supported); κ bu koşullarda düşük çıkma eğilimindedir ve güven aralıkları geniştir.
Uzlaşma kaydı ayrı tutulacaktır.
