# Dondurulmuş sistem profili (betik 93)

GPU: NVIDIA GeForce RTX 4060 Laptop GPU · torch 2.11.0+cu126 · Python 3.14.3

| Yerel bileşen | n | Ortalama (ms) | Medyan (ms) | p95 (ms) | Tepe GPU belleği (MB) |
|---|---:|---:|---:|---:|---:|
| K1 (ELECTRA-TR LoRA) | 480 | 16.5 | 16.4 | 18.1 | 454 |
| K2 NLI (mDeBERTa-v3, iddianın bütün önermeleri) | 480 | 19.3 | 19.1 | 20.6 | 596 |
| Atomik ayrıştırıcı (Gemma-4-E2B QLoRA, 4 bit) | 60 | 7529.0 | 6990.6 | 10180.8 | 6731 |

| Dış çağrı (kayıtlardan) | n | Medyan (s) | p95 (s) | Ortalama ücret (USD) |
|---|---:|---:|---:|---:|
| google_gemma-4-26b-a4b-it zero_shot | 480 | 4.50 | 13.46 | 0.000147 |
| google_gemma-4-26b-a4b-it few_shot_8 | 480 | 2.78 | 6.44 | 0.000235 |
| meta-llama_llama-3.3-70b-instruct zero_shot | 480 | 4.57 | 10.79 | 0.000350 |
| meta-llama_llama-3.3-70b-instruct few_shot_8 | 480 | 4.38 | 7.25 | 0.000477 |
| openai_gpt-4.1-mini zero_shot | 480 | 3.93 | 5.93 | 0.000720 |
| openai_gpt-4.1-mini few_shot_8 | 480 | 3.80 | 6.17 | 0.000695 |
| qwen_qwen-2.5-72b-instruct zero_shot | 480 | 10.08 | 31.00 | 0.000476 |
| qwen_qwen-2.5-72b-instruct few_shot_8 | 480 | 6.06 | 9.86 | 0.001310 |
| V4 hakemi (Llama-3.3-70B), genellenebilirlik çağrıları | 466 | 3.54 | 7.97 | — |
