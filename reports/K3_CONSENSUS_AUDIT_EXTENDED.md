# Uzlaşma denetimi: genişletilmiş fayda–maliyet analizi (Gold-480, tasarım analizi)

Temel hibrit (uyuşmazlıkta V4 hakemi): doğruluk 0.9313; uzlaşma 357, uyuşmazlık 123.
Uzlaşma denetiminde kör hakemlerin (K1/K2 çıktısını görmeyen) mevcut Gold-480 tahminleri kullanıldı; API maliyeti yok.
Net değişim için %95 güven aralığı: örnek düzeyinde eşleştirilmiş bootstrap (5000 tekrar).

| Hakem | Kural | Ek çağrı | Toplam çağrı oranı | Düzelen | Bozulan | Net [%95 GA] | Çağrı başına net | Doğruluk |
|---|---|---:|---:|---:|---:|---|---:|---:|
| google_gemma-4-26b-a4b-it__few_shot_8 | all_consensus | 357 | 100.0% | 15 | 19 | -4 [-15, +7] | -0.0112 | 0.9229 |
| google_gemma-4-26b-a4b-it__few_shot_8 | PA_label_PS_or_C | 180 | 63.1% | 11 | 6 | +5 [-3, +13] | 0.0278 | 0.9417 |
| google_gemma-4-26b-a4b-it__few_shot_8 | PB_medical_and_PS_or_C | 68 | 39.8% | 7 | 3 | +4 [-2, +10] | 0.0588 | 0.9396 |
| google_gemma-4-26b-a4b-it__few_shot_8 | medical_only | 114 | 49.4% | 8 | 7 | +1 [-6, +9] | 0.0088 | 0.9333 |
| google_gemma-4-26b-a4b-it__zero_shot | all_consensus | 357 | 100.0% | 14 | 23 | -9 [-21, +3] | -0.0252 | 0.9125 |
| google_gemma-4-26b-a4b-it__zero_shot | PA_label_PS_or_C | 180 | 63.1% | 11 | 3 | +8 [+1, +16] | 0.0444 | 0.9479 |
| google_gemma-4-26b-a4b-it__zero_shot | PB_medical_and_PS_or_C | 68 | 39.8% | 7 | 0 | +7 [+2, +13] | 0.1029 | 0.9458 |
| google_gemma-4-26b-a4b-it__zero_shot | medical_only | 114 | 49.4% | 7 | 5 | +2 [-5, +9] | 0.0175 | 0.9354 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | all_consensus | 357 | 100.0% | 17 | 20 | -3 [-14, +9] | -0.0084 | 0.9250 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | PA_label_PS_or_C | 180 | 63.1% | 13 | 12 | +1 [-8, +11] | 0.0056 | 0.9333 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | PB_medical_and_PS_or_C | 68 | 39.8% | 9 | 5 | +4 [-3, +12] | 0.0588 | 0.9396 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | medical_only | 114 | 49.4% | 10 | 7 | +3 [-5, +11] | 0.0263 | 0.9375 |
| openai_gpt-4.1-mini__few_shot_8 | all_consensus | 357 | 100.0% | 17 | 19 | -2 [-13, +10] | -0.0056 | 0.9271 |
| openai_gpt-4.1-mini__few_shot_8 | PA_label_PS_or_C | 180 | 63.1% | 14 | 18 | -4 [-14, +7] | -0.0222 | 0.9229 |
| openai_gpt-4.1-mini__few_shot_8 | PB_medical_and_PS_or_C | 68 | 39.8% | 10 | 5 | +5 [-2, +13] | 0.0735 | 0.9417 |
| openai_gpt-4.1-mini__few_shot_8 | medical_only | 114 | 49.4% | 11 | 5 | +6 [-1, +14] | 0.0526 | 0.9438 |
| openai_gpt-4.1-mini__zero_shot | all_consensus | 357 | 100.0% | 16 | 70 | -54 [-72, -36] | -0.1513 | 0.8188 |
| openai_gpt-4.1-mini__zero_shot | PA_label_PS_or_C | 180 | 63.1% | 14 | 65 | -51 [-68, -34] | -0.2833 | 0.8250 |
| openai_gpt-4.1-mini__zero_shot | PB_medical_and_PS_or_C | 68 | 39.8% | 10 | 22 | -12 [-23, -1] | -0.1765 | 0.9062 |
| openai_gpt-4.1-mini__zero_shot | medical_only | 114 | 49.4% | 11 | 23 | -12 [-24, -1] | -0.1053 | 0.9062 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | all_consensus | 357 | 100.0% | 15 | 33 | -18 [-31, -5] | -0.0504 | 0.8938 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | PA_label_PS_or_C | 180 | 63.1% | 11 | 18 | -7 [-17, +4] | -0.0389 | 0.9167 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | PB_medical_and_PS_or_C | 68 | 39.8% | 7 | 7 | +0 [-7, +7] | 0.0 | 0.9312 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | medical_only | 114 | 49.4% | 8 | 11 | -3 [-11, +5] | -0.0263 | 0.9250 |

## Alan kırılımı (düzelen / bozulan)

| Hakem | Kural | Finans | Hukuk | Tıp |
|---|---|---|---|---|
| google_gemma-4-26b-a4b-it__few_shot_8 | all_consensus | 3/6 | 4/6 | 8/7 |
| google_gemma-4-26b-a4b-it__few_shot_8 | PA_label_PS_or_C | 2/3 | 2/0 | 7/3 |
| google_gemma-4-26b-a4b-it__few_shot_8 | PB_medical_and_PS_or_C | 0/0 | 0/0 | 7/3 |
| google_gemma-4-26b-a4b-it__few_shot_8 | medical_only | 0/0 | 0/0 | 8/7 |
| google_gemma-4-26b-a4b-it__zero_shot | all_consensus | 3/7 | 4/11 | 7/5 |
| google_gemma-4-26b-a4b-it__zero_shot | PA_label_PS_or_C | 2/2 | 2/1 | 7/0 |
| google_gemma-4-26b-a4b-it__zero_shot | PB_medical_and_PS_or_C | 0/0 | 0/0 | 7/0 |
| google_gemma-4-26b-a4b-it__zero_shot | medical_only | 0/0 | 0/0 | 7/5 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | all_consensus | 3/7 | 4/6 | 10/7 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | PA_label_PS_or_C | 2/3 | 2/4 | 9/5 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | PB_medical_and_PS_or_C | 0/0 | 0/0 | 9/5 |
| meta-llama_llama-3.3-70b-instruct__few_shot_8 | medical_only | 0/0 | 0/0 | 10/7 |
| openai_gpt-4.1-mini__few_shot_8 | all_consensus | 3/8 | 3/6 | 11/5 |
| openai_gpt-4.1-mini__few_shot_8 | PA_label_PS_or_C | 2/7 | 2/6 | 10/5 |
| openai_gpt-4.1-mini__few_shot_8 | PB_medical_and_PS_or_C | 0/0 | 0/0 | 10/5 |
| openai_gpt-4.1-mini__few_shot_8 | medical_only | 0/0 | 0/0 | 11/5 |
| openai_gpt-4.1-mini__zero_shot | all_consensus | 3/22 | 2/25 | 11/23 |
| openai_gpt-4.1-mini__zero_shot | PA_label_PS_or_C | 2/22 | 2/21 | 10/22 |
| openai_gpt-4.1-mini__zero_shot | PB_medical_and_PS_or_C | 0/0 | 0/0 | 10/22 |
| openai_gpt-4.1-mini__zero_shot | medical_only | 0/0 | 0/0 | 11/23 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | all_consensus | 3/14 | 4/8 | 8/11 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | PA_label_PS_or_C | 2/8 | 2/3 | 7/7 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | PB_medical_and_PS_or_C | 0/0 | 0/0 | 7/7 |
| qwen_qwen-2.5-72b-instruct__few_shot_8 | medical_only | 0/0 | 0/0 | 8/11 |
