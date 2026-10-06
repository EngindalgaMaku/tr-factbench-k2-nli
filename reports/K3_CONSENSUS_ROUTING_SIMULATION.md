# K3 uzlaşma yönlendirme simülasyonu (Gold-480, tasarım analizi)

Uyarı: Kurallar Gold-480 hataları incelendikten sonra seçilmiştir; bu tablo held-out sonuç değildir.
Dondurulmuş kurallar: `configs/frozen/K3_ROUTING_POLICIES_v1.json` (AP6'da bir kez test edilecek).

Üretim: `python scripts/78_simulate_consensus_routing.py` · sıfır API çağrısı (mevcut tahminler yeniden kullanılır).

## K1 güveni uzlaşma hatalarını ayırt ediyor mu?

- Uzlaşma vakası: 357, uzlaşma hatası: 20
- AUROC (düşük güven → hata): 0.799
- Güveni ≥ 0.96 olan uzlaşma hatası: 13/20
- Hata güvenleri: 0.521, 0.541, 0.566, 0.666, 0.698, 0.819, 0.837, 0.960, 0.970, 0.976, 0.978, 0.987, 0.995, 0.997, 0.998, 0.999, 0.999, 1.000, 1.000, 1.000

## Yönlendirme kuralları

Temel hibrit (yalnız uyuşmazlıklar, V4): 447/480 = 0.9313, çağrı 123 (25.6%).

| Uzlaşma kontrol hakemi | Kural | Ek çağrı | Toplam çağrı oranı | Düzelen | Bozulan | Net | Doğruluk | Ek çağrı başına net |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| blind Gemma-4-26B zero-shot | All consensus cases | 357 | 100.0% | 14 | 23 | -9 | 0.9125 | -0.025 |
| blind Gemma-4-26B zero-shot | PA: agreed label PS or C | 180 | 63.1% | 11 | 3 | +8 | 0.9479 | +0.044 |
| blind Gemma-4-26B zero-shot | Agreed label PS | 93 | 45.0% | 8 | 3 | +5 | 0.9417 | +0.054 |
| blind Gemma-4-26B zero-shot | Agreed label C | 87 | 43.8% | 3 | 0 | +3 | 0.9375 | +0.034 |
| blind Gemma-4-26B zero-shot | Medical only | 114 | 49.4% | 7 | 5 | +2 | 0.9354 | +0.018 |
| blind Gemma-4-26B zero-shot | PB: medical and agreed label PS or C | 68 | 39.8% | 7 | 0 | +7 | 0.9458 | +0.103 |
| blind Gemma-4-26B zero-shot | K1 confidence < 0.99 | 65 | 39.2% | 8 | 6 | +2 | 0.9354 | +0.031 |
| blind Gemma-4-26B zero-shot | K1 confidence < 0.95 | 32 | 32.3% | 4 | 4 | +0 | 0.9313 | +0.000 |
| informed Llama-3.3-70B (V1-era prompt) | All consensus cases | 357 | 100.0% | 11 | 7 | +4 | 0.9396 | +0.011 |
| informed Llama-3.3-70B (V1-era prompt) | PA: agreed label PS or C | 180 | 63.1% | 7 | 7 | +0 | 0.9313 | +0.000 |
| informed Llama-3.3-70B (V1-era prompt) | Agreed label PS | 93 | 45.0% | 6 | 7 | -1 | 0.9292 | -0.011 |
| informed Llama-3.3-70B (V1-era prompt) | Agreed label C | 87 | 43.8% | 1 | 0 | +1 | 0.9333 | +0.011 |
| informed Llama-3.3-70B (V1-era prompt) | Medical only | 114 | 49.4% | 5 | 1 | +4 | 0.9396 | +0.035 |
| informed Llama-3.3-70B (V1-era prompt) | PB: medical and agreed label PS or C | 68 | 39.8% | 4 | 1 | +3 | 0.9375 | +0.044 |
| informed Llama-3.3-70B (V1-era prompt) | K1 confidence < 0.99 | 65 | 39.2% | 5 | 2 | +3 | 0.9375 | +0.046 |
| informed Llama-3.3-70B (V1-era prompt) | K1 confidence < 0.95 | 32 | 32.3% | 3 | 1 | +2 | 0.9354 | +0.062 |
