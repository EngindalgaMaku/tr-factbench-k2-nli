# Gold-480 sonuç paketi (Bölüm 4 için, betik 92)

n = 480, bağlam grubu = 120, K1≠K2 (soft-prob) = 123. GA: bağlam grubu bootstrap, 10000 tekrar, seed 42. McNemar: K1'e karşı, kesin.

| Sistem | Doğruluk | Macro-F1 [%95 GA] | MCC | Çağrı oranı | McNemar vs K1 (b/c, p) | Finans | Hukuk | Tıp |
|---|---:|---|---:|---:|---|---:|---:|---:|
| K1 (ELECTRA-TR) | 0.8313 | 0.8301 [0.7988, 0.8602] | 0.7785 | 0.0% | 0/0, 1 | 0.8632 | 0.8566 | 0.7667 |
| K2 düz kural | 0.7833 | 0.7838 [0.7469, 0.8190] | 0.7145 | 0.0% | 69/46, 0.0398 | 0.8350 | 0.7713 | 0.7403 |
| K2 soft-prob | 0.8042 | 0.8065 [0.7742, 0.8383] | 0.7412 | 0.0% | 62/49, 0.255 | 0.8690 | 0.7777 | 0.7707 |
| İdeal seçim üst sınırı (K1 veya K2 doğru) | 0.9333 | 0.9331 [0.9121, 0.9521] | 0.9122 | — | 0/49, 3.55e-15 | 0.9562 | 0.9313 | 0.9109 |
| Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi) | 0.9313 | 0.9315 [0.9112, 0.9504] | 0.9092 | 25.6% | 6/54, 9.72e-11 | 0.9561 | 0.9320 | 0.9056 |
| Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot | 0.9229 | 0.9223 [0.8968, 0.9453] | 0.8998 | 25.6% | 4/48, 1.31e-10 | 0.9436 | 0.9501 | 0.8692 |
| Hibrit P0 + kör gemma-4-26b-a4b-it few_shot_8 | 0.9083 | 0.9078 [0.8826, 0.9312] | 0.8823 | 25.6% | 3/40, 3.02e-09 | 0.9380 | 0.9377 | 0.8438 |
| Hibrit P0 + kör llama-3.3-70b-instruct zero_shot | 0.8396 | 0.8392 [0.8082, 0.8683] | 0.7934 | 25.6% | 24/28, 0.678 | 0.8825 | 0.8564 | 0.7748 |
| Hibrit P0 + kör llama-3.3-70b-instruct few_shot_8 | 0.9146 | 0.9145 [0.8902, 0.9375] | 0.8886 | 25.6% | 7/47, 2.29e-08 | 0.9564 | 0.9192 | 0.8651 |
| Hibrit P0 + kör gpt-4.1-mini zero_shot | 0.9021 | 0.9025 [0.8774, 0.9270] | 0.8718 | 25.6% | 15/49, 2.44e-05 | 0.9434 | 0.8934 | 0.8699 |
| Hibrit P0 + kör gpt-4.1-mini few_shot_8 | 0.9146 | 0.9149 [0.8887, 0.9379] | 0.8869 | 25.6% | 13/53, 7.24e-07 | 0.9558 | 0.8933 | 0.8934 |
| Hibrit P0 + kör qwen-2.5-72b-instruct zero_shot | 0.8833 | 0.8811 [0.8541, 0.9069] | 0.8492 | 25.6% | 12/37, 0.00047 | 0.9116 | 0.9181 | 0.8097 |
| Hibrit P0 + kör qwen-2.5-72b-instruct few_shot_8 | 0.9042 | 0.9036 [0.8776, 0.9285] | 0.8749 | 25.6% | 8/43, 6.87e-07 | 0.9564 | 0.9251 | 0.8274 |
| PA (P0-V4 + kör Gemma uzlaşma denetimi) | 0.9479 | 0.9478 [0.9291, 0.9663] | 0.9307 | 63.1% | 9/65, 1.35e-11 | 0.9557 | 0.9381 | 0.9496 |
| PB (P0-V4 + yalnız tıp uzlaşma denetimi) | 0.9458 | 0.9460 [0.9272, 0.9645] | 0.9281 | 39.8% | 6/61, 1.49e-12 | 0.9561 | 0.9320 | 0.9496 |
| Tek başına gemma-4-26b-a4b-it zero_shot | 0.9042 | 0.9022 [0.8752, 0.9264] | 0.8776 | 100.0% | 27/62, 0.000266 | 0.9181 | 0.9047 | 0.8829 |
| Tek başına gemma-4-26b-a4b-it few_shot_8 | 0.9000 | 0.8991 [0.8739, 0.9227] | 0.8733 | 100.0% | 22/55, 0.000217 | 0.9195 | 0.9244 | 0.8508 |
| Tek başına llama-3.3-70b-instruct zero_shot | 0.7167 | 0.7016 [0.6671, 0.7343] | 0.6611 | 100.0% | 95/40, 2.47e-06 | 0.7142 | 0.7175 | 0.6668 |
| Tek başına llama-3.3-70b-instruct few_shot_8 | 0.9083 | 0.9085 [0.8839, 0.9330] | 0.8798 | 100.0% | 27/64, 0.000132 | 0.9313 | 0.9067 | 0.8871 |
| Tek başına gpt-4.1-mini zero_shot | 0.7896 | 0.7621 [0.7302, 0.7937] | 0.7581 | 100.0% | 85/65, 0.121 | 0.7964 | 0.7219 | 0.7668 |
| Tek başına gpt-4.1-mini few_shot_8 | 0.9104 | 0.9098 [0.8822, 0.9350] | 0.8830 | 100.0% | 32/70, 0.000213 | 0.9241 | 0.8736 | 0.9309 |
| Tek başına qwen-2.5-72b-instruct zero_shot | 0.8250 | 0.8160 [0.7817, 0.8470] | 0.7804 | 100.0% | 50/47, 0.839 | 0.8356 | 0.8455 | 0.7632 |
| Tek başına qwen-2.5-72b-instruct few_shot_8 | 0.8667 | 0.8655 [0.8340, 0.8945] | 0.8268 | 100.0% | 41/58, 0.107 | 0.8867 | 0.8992 | 0.8096 |

## Sınıf bazında F1

| Sistem | supported | partially_supported | contradicted | unverifiable |
|---|---:|---:|---:|---:|
| K1 (ELECTRA-TR) | 0.9091 | 0.8078 | 0.7918 | 0.8116 |
| K2 düz kural | 0.8175 | 0.7287 | 0.8066 | 0.7826 |
| K2 soft-prob | 0.8175 | 0.7287 | 0.8384 | 0.8416 |
| İdeal seçim üst sınırı (K1 veya K2 doğru) | 0.9714 | 0.9274 | 0.9098 | 0.9238 |
| Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi) | 0.9669 | 0.9004 | 0.9328 | 0.9258 |
| Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot | 0.9794 | 0.8992 | 0.9218 | 0.8889 |
| Hibrit P0 + kör gemma-4-26b-a4b-it few_shot_8 | 0.9754 | 0.8614 | 0.9372 | 0.8571 |
| Hibrit P0 + kör llama-3.3-70b-instruct zero_shot | 0.9712 | 0.7652 | 0.8028 | 0.8177 |
| Hibrit P0 + kör llama-3.3-70b-instruct few_shot_8 | 0.9794 | 0.8716 | 0.9180 | 0.8889 |
| Hibrit P0 + kör gpt-4.1-mini zero_shot | 0.9794 | 0.8356 | 0.8571 | 0.9381 |
| Hibrit P0 + kör gpt-4.1-mini few_shot_8 | 0.9794 | 0.8607 | 0.8952 | 0.9244 |
| Hibrit P0 + kör qwen-2.5-72b-instruct zero_shot | 0.9754 | 0.8482 | 0.8828 | 0.8177 |
| Hibrit P0 + kör qwen-2.5-72b-instruct few_shot_8 | 0.9714 | 0.8549 | 0.9150 | 0.8732 |
| PA (P0-V4 + kör Gemma uzlaşma denetimi) | 0.9669 | 0.9167 | 0.9590 | 0.9487 |
| PB (P0-V4 + yalnız tıp uzlaşma denetimi) | 0.9669 | 0.9187 | 0.9540 | 0.9442 |
| Tek başına gemma-4-26b-a4b-it zero_shot | 0.9787 | 0.8712 | 0.9297 | 0.8293 |
| Tek başına gemma-4-26b-a4b-it few_shot_8 | 0.9917 | 0.8278 | 0.9590 | 0.8177 |
| Tek başına llama-3.3-70b-instruct zero_shot | 0.9917 | 0.4205 | 0.6779 | 0.7166 |
| Tek başına llama-3.3-70b-instruct few_shot_8 | 0.9832 | 0.8293 | 0.9225 | 0.8991 |
| Tek başına gpt-4.1-mini zero_shot | 0.9958 | 0.3841 | 0.7118 | 0.9565 |
| Tek başına gpt-4.1-mini few_shot_8 | 0.9958 | 0.8054 | 0.8764 | 0.9614 |
| Tek başına qwen-2.5-72b-instruct zero_shot | 0.9917 | 0.7920 | 0.8138 | 0.6667 |
| Tek başına qwen-2.5-72b-instruct few_shot_8 | 0.9917 | 0.7570 | 0.8897 | 0.8235 |

## Seçili eşleştirilmiş karşılaştırmalar

| A | B | ΔMacro-F1 (A−B) [%95 GA] | McNemar (yalnız A doğru / yalnız B doğru, p) |
|---|---|---|---|
| Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot | Tek başına gemma-4-26b-a4b-it zero_shot | +0.0201 [-0.0029, +0.0439] | 23 / 14, 0.188 |
| Hibrit P0 + kör gpt-4.1-mini few_shot_8 | Tek başına gpt-4.1-mini few_shot_8 | +0.0052 [-0.0194, +0.0299] | 19 / 17, 0.868 |
| Hibrit P0 + kör llama-3.3-70b-instruct few_shot_8 | Tek başına llama-3.3-70b-instruct few_shot_8 | +0.0060 [-0.0175, +0.0298] | 20 / 17, 0.743 |
| Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot | Tek başına gpt-4.1-mini few_shot_8 | +0.0126 [-0.0201, +0.0457] | 35 / 29, 0.532 |
| Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi) | Tek başına gpt-4.1-mini few_shot_8 | +0.0217 [-0.0089, +0.0522] | 35 / 25, 0.245 |
| Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi) | Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot | +0.0091 [-0.0119, +0.0308] | 14 / 10, 0.541 |
| K2 soft-prob | K2 düz kural | +0.0227 [+0.0071, +0.0390] | 12 / 2, 0.0129 |

Notlar: V4 istemi ve soft-prob kuralı Gold-480 üzerinde seçilmiştir (Karar 7, 15); PA/PB Gold-480 uzlaşma hataları incelenerek tasarlanmıştır (tasarım analizi). Kör hakemler istem geliştirmesine katılmamıştır. McNemar b = yalnız K1 doğru, c = yalnız sistem doğru.
