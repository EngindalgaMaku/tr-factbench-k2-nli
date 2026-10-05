# K2 aggregation policy ablation on the official TR-FactBench Gold 480 test set

**Experiment ID:** `K2-AGG-ABLATION-GOLD480-v1`  
**Status:** completed gold ablation  
**Stage:** aggregation policy evaluation  

## Research question

When frozen Gemma-4 predicted atoms and mDeBERTa-v3 zero-shot NLI decisions are aggregated, how do flat, contradiction-priority, sentence-grouped, and soft-probability rules affect 4-class claim verification and boundary trade-offs on the 480 held-out gold test set?

## Rules

- **Flat:** all-entailment → supported; otherwise any entailment → partially_supported; otherwise any contradiction → contradicted; otherwise unverifiable.
- **Contradiction-priority:** all-entailment → supported; otherwise any contradiction → contradicted; otherwise any entailment → partially_supported; otherwise unverifiable.
- **Sentence-grouped:** atoms are automatically aligned to the claim sentence from which they were derived. Contradiction dominates within a sentence; sentence outcomes are then combined across the claim.
- **Soft-probability average:** preserves entailment rules; when no entailment exists, adjudicates between contradiction and unverifiable using mean posterior probabilities across atoms.

No NLI inference was repeated. All rules reuse the frozen atom decisions from the v1.1 source runs.

## Main results

| Model | Rule | Accuracy | Macro-F1 | Δ vs flat | MCC | Changed claims |
| --- | --- | --- | --- | --- | --- | --- |
| mDeBERTa-v3-base 2mil7 | Flat | 0.7833 | 0.7838 | +0.0000 | 0.7145 | 0 |
| mDeBERTa-v3-base 2mil7 | Contradiction-priority | 0.6604 | 0.6262 | -0.1576 | 0.5781 | 101 |
| mDeBERTa-v3-base 2mil7 | Sentence-grouped | 0.7312 | 0.7261 | -0.0577 | 0.6505 | 50 |
| mDeBERTa-v3-base 2mil7 | Soft-probability average | 0.8042 | 0.8065 | +0.0227 | 0.7412 | 14 |

The highest exploratory Macro-F1 is **0.8065** from **mDeBERTa-v3-base 2mil7 / Soft-probability average**.

### mDeBERTa-v3-base 2mil7

![Aggregation comparison — mDeBERTa-v3-base 2mil7](figures/aggregation_metrics__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7.svg)

## Policy-review sensitivity

The two pre-identified policy-review examples are: none.

| Model | Rule | Macro-F1 all | Macro-F1 excluding review | Difference |
| --- | --- | --- | --- | --- |
| mDeBERTa-v3-base 2mil7 | Flat | 0.7838 | 0.7838 | +0.0000 |
| mDeBERTa-v3-base 2mil7 | Contradiction-priority | 0.6262 | 0.6262 | +0.0000 |
| mDeBERTa-v3-base 2mil7 | Sentence-grouped | 0.7261 | 0.7261 | +0.0000 |
| mDeBERTa-v3-base 2mil7 | Soft-probability average | 0.8065 | 0.8065 | +0.0000 |

## Paired tests against flat

| Model | Alternative | Flat-only correct | Alternative-only correct | Discordant | Exact p |
| --- | --- | --- | --- | --- | --- |
| mDeBERTa-v3-base 2mil7 | Contradiction-priority | 75 | 16 | 91 | 0.0000 |
| mDeBERTa-v3-base 2mil7 | Sentence-grouped | 35 | 10 | 45 | 0.0002 |
| mDeBERTa-v3-base 2mil7 | Soft-probability average | 2 | 12 | 14 | 0.0129 |

McNemar tests are exploratory because the same pilot data informed the error analysis and policy hypotheses.

## Interpretation

- Evaluated on the exact 480 validly decomposed instances from the official TR-FactBench held-out gold test set.
- Flat aggregation serves as the primary pipeline baseline (Macro-F1 0.7838, Accuracy 78.33%).
- Soft probability averaging resolves conflicting atom labels without heuristic priority rules.
- Sentence grouping preserves premise context across multi-sentence claims.

## Limitations

- Evaluated on the 480 validly decomposed gold test examples with 100.0% coverage.
- Relies on zero-shot NLI probabilities without downstream calibration.

## Next steps

- Freeze soft-probability average as the primary decision rule for K2.
- Compare K1 against K2 under soft-probability aggregation to update disagreement set for LLM Judge arbitration.
- Incorporate aggregation ablation findings into Chapter 4 of the master thesis.

## Reproducibility

```powershell
C:\Python314\python.exe scripts\55_run_aggregation_ablation.py --config "configs\\experiments\\K2-AGG-ABLATION-GOLD480-v1.json"
```

Source runs:

- `runs/K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7`

Generated artifacts:

- `tables/aggregation_metrics.csv`
- `tables/class_metrics.csv`
- `tables/changed_predictions.csv`
- `tables/mcnemar_tests.csv`
- one confusion-matrix CSV and SVG per model/rule
- one derived prediction JSONL and metrics JSON per model/rule
- one aggregation-comparison SVG per model
