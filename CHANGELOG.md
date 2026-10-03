# İlk Temizleme Özeti

## Eski yapıdan ayrılan noktalar

- Eski keşifsel scriptler `legacy/exploratory_2026-08-05/` altında donduruldu.
- Atomizer bağımlılığı NLI paketinden çıkarıldı.
- `unverifiable -> neutral` eşlemesi merkezileştirildi.
- `partially_supported -> neutral` dönüşümü kaldırıldı.
- NLI ve claim etiket sıraları sabitlendi.
- Multiclass NLL ve Brier hesapları kanonik olasılık sütun sırasına göre uygulandı.
- Hypothesis korunarak yalnız premise truncation politikası tanımlandı.
- Truncation bilgisi örnek bazında raporlanır hâle getirildi.
- Context-group seviyesinde model selection/calibration/internal evaluation splitleri oluşturuldu.
- Stress seti model seçimi ve calibration dışında bırakıldı.
- Immutable run klasörü, manifest, veri SHA-256 ve model revision kayıtları eklendi.
- Paired bootstrap, exact McNemar ve Holm düzeltmeli karşılaştırma scriptleri eklendi.
- Atom-level human gold için dengeli 240 örneklik annotation şablonu oluşturuldu.
- Veri dağılım grafikleri ve ayrıntılı deney raporu üreticileri eklendi.
- Dokuz birim testi eklendi ve tamamı geçti.

## Bilinen sınır (ilk teslimat)

İlk teslimatta beş modelin inference benchmark'ı henüz çalıştırılmamıştı ve `runs/` boştu. Deney komutları ve raporlama hattı hazırdı.

## Güncelleme

`runs/` artık boş değildir. Diskte duran başlıca koşular:

- `K2-10-selection-v1` — beş model, claim-level 3-sınıf, 486 örnek
- `K2-ATOM-ASSISTED-ZS-PILOT-v1.1`
- `K2-PIPE-PRED-ZS-ATOMIZERTEST-v1`
- `K2-PIPE-PRED-GOLD480-v1` — resmi 480 held-out altın test kümesi değerlendirmesi (Macro-F1 0.7830, %99.58 kapsama, paired K1 vs K2 analizi)

İndeks: `docs/EXPERIMENTS.md` ve `reports/experiments/`.

