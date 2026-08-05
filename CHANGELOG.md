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

## Bilinen sınır

Bu teslimatta model ağırlıkları indirilip beş modelin tam inference benchmark'ı çalıştırılmadı. `runs/` klasörü bu nedenle boştur. Deney komutları ve raporlama hattı hazırdır.
