# AP6 — Ön kayıtlı analiz sonuçları v1

Cümle: 858 · insan çekimser: 75 · değerlendirme kümesi: 783. GA: soru düzeyinde küme bootstrap (10.000, seed 42).

## S3 — Halüsinasyon oranı (insan etiketi supported değil)

| Grup | n | Oran | %95 GA |
|---|---:|---:|---|
| Genel | 783 | 0.166 | [0.135, 0.199] |
| Ministral-3B | 296 | 0.304 | [0.243, 0.366] |
| Qwen3-8B | 271 | 0.122 | [0.080, 0.168] |
| DeepSeek-V4 | 216 | 0.032 | [0.013, 0.056] |
| finance | 263 | 0.190 | [0.127, 0.264] |
| legal | 251 | 0.124 | [0.085, 0.165] |
| medical | 269 | 0.182 | [0.134, 0.239] |

Sınıf dağılımı: {'unverifiable': 64, 'supported': 653, 'partially_supported': 29, 'contradicted': 37}
Hata türleri: {'relation_fabrication': 23, 'added_information': 72, 'other': 2, 'scope': 6, 'negation': 16, 'number_date': 11}

Model bazında sınıflar: Ministral-3B: {'supported': 206, 'unverifiable': 41, 'partially_supported': 19, 'contradicted': 30}; Qwen3-8B: {'unverifiable': 17, 'supported': 238, 'partially_supported': 9, 'contradicted': 7}; DeepSeek-V4: {'supported': 209, 'unverifiable': 6, 'partially_supported': 1}

Çekimserlik (model; soru türüne göre çekimser/cümle): Ministral-3B: 14/310 {'answerable': [5, 102], 'multi_fact': [2, 122], 'partial': [7, 86]}; Qwen3-8B: 36/307 {'answerable': [8, 111], 'multi_fact': [7, 126], 'partial': [21, 70]}; DeepSeek-V4: 25/241 {'answerable': [3, 78], 'multi_fact': [5, 100], 'partial': [17, 63]}

Otomatik çekimser işareti ile insan kararı: {'auto=False,human=False': 777, 'auto=True,human=True': 47, 'auto=False,human=True': 28, 'auto=True,human=False': 6}

## S1, S2, S4 — Sistemler (ikili: halüsinasyon = supported değil)

| Sistem | n | Yanlış alarm (S1) | Kesinlik | Duyarlılık (S2) | F1 | 4 sınıf doğruluk* | Macro-F1* |
|---|---:|---|---|---|---|---:|---:|
| K1 | 783 | 0.417 [0.371, 0.464] | 0.271 [0.218, 0.326] | 0.777 [0.691, 0.858] | 0.402 [0.335, 0.467] | 0.563 | 0.352 |
| K2 | 782 | 0.372 [0.308, 0.439] | 0.255 [0.197, 0.318] | 0.643 [0.553, 0.729] | 0.365 [0.296, 0.432] | 0.577 | 0.307 |
| Hibrit P0 | 783 | 0.217 [0.180, 0.258] | 0.411 [0.338, 0.486] | 0.762 [0.686, 0.833] | 0.534 [0.461, 0.602] | 0.727 | 0.415 |
| Hibrit PA | 783 | 0.179 [0.144, 0.216] | 0.456 [0.378, 0.536] | 0.754 [0.676, 0.827] | 0.568 [0.494, 0.636] | 0.764 | 0.451 |
| Hibrit PB | 783 | 0.213 [0.174, 0.254] | 0.416 [0.342, 0.492] | 0.762 [0.686, 0.833] | 0.538 [0.465, 0.606] | 0.734 | 0.425 |
| Gemma-4-26B (örneksiz) | 783 | 0.242 [0.201, 0.284] | 0.415 [0.342, 0.490] | 0.862 [0.797, 0.916] | 0.560 [0.484, 0.630] | 0.732 | 0.513 |
| GPT-4.1-mini (8 örnek) | 783 | 0.119 [0.089, 0.152] | 0.547 [0.445, 0.645] | 0.723 [0.642, 0.805] | 0.623 [0.538, 0.697] | 0.824 | 0.534 |

\* Betimsel; ana ölçüt değildir (§8).

## Eşleştirilmiş karşılaştırmalar (ikili doğruluk, kesin McNemar; F1 farkı)

| Karşılaştırma | n | Yalnız ilki doğru | Yalnız ikincisi doğru | p | F1 farkı [%95 GA] |
|---|---:|---:|---:|---:|---|
| Hibrit P0 – K1 | 783 | 152 | 24 | 6.01e-24 | +0.132 [0.097, 0.170] |
| Hibrit P0 – K2 | 782 | 156 | 39 | 8.98e-18 | +0.170 [0.114, 0.226] |
| Hibrit P0 – Gemma-4-26B (örneksiz) | 783 | 94 | 91 | 0.883 | -0.026 [-0.086, 0.031] |
| Hibrit P0 – GPT-4.1-mini (8 örnek) | 783 | 50 | 109 | 3.31e-06 | -0.089 [-0.151, -0.027] |
| Hibrit PA – Hibrit P0 | 783 | 25 | 1 | 8.05e-07 | +0.034 [0.019, 0.052] |
| Hibrit PB – Hibrit P0 | 783 | 3 | 0 | 0.25 | +0.004 [0.000, 0.012] |

## Maliyet — büyük dil modeli çağrı oranı (n = 858)

P0 0.544 · PA 0.618 · PB 0.561

## Alt kümeler (betimsel, ikili F1 / yanlış alarm / duyarlılık)

- **K1** — Ministral-3B: F1 0.579, YA 0.432, D 0.811 (n 296); Qwen3-8B: F1 0.293, YA 0.424, D 0.697 (n 271); DeepSeek-V4: F1 0.106, YA 0.392, D 0.714 (n 216); answerable: F1 0.356, YA 0.438, D 0.775 (n 275); multi_fact: F1 0.353, YA 0.411, D 0.692 (n 334); partial: F1 0.544, YA 0.390, D 0.895 (n 174); geri gönderme: F1 0.439, YA 0.569, D 0.872 (n 183)
- **K2** — Ministral-3B: F1 0.558, YA 0.296, D 0.652 (n 295); Qwen3-8B: F1 0.282, YA 0.374, D 0.606 (n 271); DeepSeek-V4: F1 0.095, YA 0.445, D 0.714 (n 216); answerable: F1 0.307, YA 0.370, D 0.575 (n 275); multi_fact: F1 0.309, YA 0.362, D 0.549 (n 333); partial: F1 0.516, YA 0.397, D 0.842 (n 174); geri gönderme: F1 0.492, YA 0.347, D 0.744 (n 183)
- **Hibrit P0** — Ministral-3B: F1 0.690, YA 0.209, D 0.778 (n 296); Qwen3-8B: F1 0.446, YA 0.227, D 0.758 (n 271); DeepSeek-V4: F1 0.143, YA 0.215, D 0.571 (n 216); answerable: F1 0.484, YA 0.243, D 0.775 (n 275); multi_fact: F1 0.519, YA 0.170, D 0.673 (n 334); partial: F1 0.611, YA 0.272, D 0.868 (n 174); geri gönderme: F1 0.593, YA 0.306, D 0.897 (n 183)
- **Hibrit PA** — Ministral-3B: F1 0.723, YA 0.155, D 0.767 (n 296); Qwen3-8B: F1 0.481, YA 0.193, D 0.758 (n 271); DeepSeek-V4: F1 0.160, YA 0.187, D 0.571 (n 216); answerable: F1 0.508, YA 0.204, D 0.750 (n 275); multi_fact: F1 0.560, YA 0.135, D 0.673 (n 334); partial: F1 0.647, YA 0.228, D 0.868 (n 174); geri gönderme: F1 0.602, YA 0.278, D 0.872 (n 183)
- **Hibrit PB** — Ministral-3B: F1 0.690, YA 0.209, D 0.778 (n 296); Qwen3-8B: F1 0.450, YA 0.223, D 0.758 (n 271); DeepSeek-V4: F1 0.148, YA 0.206, D 0.571 (n 216); answerable: F1 0.488, YA 0.238, D 0.775 (n 275); multi_fact: F1 0.526, YA 0.163, D 0.673 (n 334); partial: F1 0.611, YA 0.272, D 0.868 (n 174); geri gönderme: F1 0.593, YA 0.306, D 0.897 (n 183)
- **Gemma-4-26B (örneksiz)** — Ministral-3B: F1 0.696, YA 0.282, D 0.878 (n 296); Qwen3-8B: F1 0.434, YA 0.286, D 0.848 (n 271); DeepSeek-V4: F1 0.227, YA 0.153, D 0.714 (n 216); answerable: F1 0.444, YA 0.277, D 0.750 (n 275); multi_fact: F1 0.584, YA 0.202, D 0.865 (n 334); partial: F1 0.667, YA 0.265, D 0.974 (n 174); geri gönderme: F1 0.567, YA 0.361, D 0.923 (n 183)
- **GPT-4.1-mini (8 örnek)** — Ministral-3B: F1 0.749, YA 0.131, D 0.778 (n 296); Qwen3-8B: F1 0.449, YA 0.151, D 0.606 (n 271); DeepSeek-V4: F1 0.308, YA 0.072, D 0.571 (n 216); answerable: F1 0.574, YA 0.136, D 0.725 (n 275); multi_fact: F1 0.626, YA 0.096, D 0.692 (n 334); partial: F1 0.674, YA 0.140, D 0.763 (n 174); geri gönderme: F1 0.621, YA 0.222, D 0.821 (n 183)

K2 karar vermediği için çıkarılan cümle: 1.
Girdi dosyalarının SHA-256 değerleri JSON çıktısındadır.
