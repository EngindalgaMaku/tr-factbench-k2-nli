# Experiment registry

This file indexes reproducible experiments. Detailed reports live under `reports/experiments/`.

Claim-level 3-class model selection runs exist under `runs/K2-10-selection-v1__*` (486 examples). They are not in the table below because there is no generated report under `reports/experiments/`. Best model on disk: mDeBERTa-v3-base 2mil7, Macro-F1 0.8684 (`runs/K2-10-selection-v1__mdeberta_base_2mil7/metrics.json`).

| Experiment | Stage | Status | Best model | Macro-F1 | Report |
|---|---|---|---|---:|---|
| `K2-ATOM-ASSISTED-ZS-PILOT-v1.1` | model comparison and atomization verification | frozen pilot | mDeBERTa-v3-base 2mil7 | 0.7935 | [K2-ATOM-ASSISTED-ZS-PILOT-v1.1](../reports/experiments/K2-ATOM-ASSISTED-ZS-PILOT-v1.1/README.md) |
| `K2-AGG-ABLATION-ASSISTED-PILOT-v1.1` | aggregation policy selection | exploratory ablation | mDeBERTa-v3-base 2mil7 / Sentence-grouped | 0.8004 | [K2-AGG-ABLATION-ASSISTED-PILOT-v1.1](../reports/experiments/K2-AGG-ABLATION-ASSISTED-PILOT-v1.1/README.md) |
| `K2-PIPE-PRED-ZS-ATOMIZERTEST-v1` | predicted-atom pipeline integration | exploratory end-to-end atomizer test | mDeBERTa-v3-base 2mil7 | 0.5235 | [K2-PIPE-PRED-ZS-ATOMIZERTEST-v1](../reports/experiments/K2-PIPE-PRED-ZS-ATOMIZERTEST-v1/README.md) |
| `K2-PIPE-PRED-GOLD480-v1` | held-out gold pipeline evaluation | frozen gold evaluation | mDeBERTa-v3-base 2mil7 | 0.7830 | [K2-PIPE-PRED-GOLD480-v1](../reports/experiments/K2-PIPE-PRED-GOLD480-v1/README.md) |
| `K2-AGG-ABLATION-GOLD480-v1` | aggregation policy evaluation | completed gold ablation | mDeBERTa-v3-base 2mil7 / Soft-probability average | 0.8059 | [K2-AGG-ABLATION-GOLD480-v1](../reports/experiments/K2-AGG-ABLATION-GOLD480-v1/README.md) |
| `K3-HYBRID-ARBITRATION-GOLD480-v1` | component 3 hybrid arbitration | completed gold hybrid evaluation | Hybrid Triad (Gemma-4-26B (Zero-Shot)) | 0.9221 | [K3-HYBRID-ARBITRATION-GOLD480-v1](../reports/experiments/K3-HYBRID-ARBITRATION-GOLD480-v1/README.md) |
| `K3-LIVE-GEMMA-ARBITRATION-v1` | component 3 live local arbitration | completed live 2B arbitration | Hybrid (Gemma-4-E2B-it Local Judge) | 0.8294 | [K3-LIVE-GEMMA-ARBITRATION-v1](../reports/experiments/K3-LIVE-GEMMA-ARBITRATION-v1/metrics_summary.json) |
| `K3-LIVE-LLAMA70B-ARBITRATION-v1` | component 3 live API arbitration | completed live 70B arbitration | Hybrid (Llama-3.3-70B OpenRouter Judge - Zero-Shot) | 0.8262 | [K3-LIVE-LLAMA70B-ARBITRATION-v1](../reports/experiments/K3-LIVE-LLAMA70B-ARBITRATION-v1/REPORT_K3_LIVE_LLAMA70B.md) |
| `K3-FEWSHOT-LLAMA70B-ARBITRATION-v1` | component 3 informed few-shot arbitration | completed few-shot meta-judge | Hybrid (Llama-3.3-70B Few-Shot Meta-Judge) | 0.8966 | [K3-FEWSHOT-LLAMA70B-ARBITRATION-v1](../reports/experiments/K3-FEWSHOT-LLAMA70B-ARBITRATION-v1/REPORT_K3_FEWSHOT_LLAMA70B.md) |
| `AUDIT-K2-K3-v1` | cross-component audit and integrity check | verified zero-leakage audit | Comprehensive Audit & Comparison | - | [AUDIT-K2-K3-v1](../reports/experiments/AUDIT-K2-K3-v1/README.md) |
