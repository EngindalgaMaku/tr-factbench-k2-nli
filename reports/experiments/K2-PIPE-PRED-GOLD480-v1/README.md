# K2 end-to-end pipeline with Gemma-predicted atoms — TR-FactBench 480 Gold Test

- **Experiment ID:** `K2-PIPE-PRED-GOLD480-v1`
- **Status:** frozen gold evaluation
- **Stage:** held-out gold pipeline evaluation
- **Run ID:** `K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7`
- **Model:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`
- **Aggregation:** flat deterministic aggregation over hard atom labels

## Research question

When Gemma-4 QLoRA predicted atoms on the official 480 held-out gold test set are verified with mDeBERTa-v3 zero-shot NLI and flat aggregation, what claim-level Macro-F1, strict accuracy, and class-level metrics are achieved compared to K1?

## Evaluation policy

The four-class metrics are computed only for examples where Gemma produced a valid, non-empty atom list. Atomizer failures are preserved as pipeline abstentions rather than being assigned an arbitrary four-class fallback label.

Two accuracy values are therefore reported:

- **Conditional accuracy:** accuracy among valid atomizations.
- **Strict end-to-end accuracy:** valid correct predictions divided by all input claims, with atomizer failures counted as incorrect.

A strict four-class Macro-F1 is not reported because the failures do not belong to one of the four semantic claim labels.

## Dataset and coverage

| Input claims | Scored claims | Atomizer failures | Coverage | Predicted atoms |
| --- | --- | --- | --- | --- |
| 480 | 480 | 0 | 1.0000 | 998 |

| Gold label | Input | Scored | Failures |
| --- | --- | --- | --- |
| supported | 120 | 120 | 0 |
| partially_supported | 119 | 119 | 0 |
| contradicted | 121 | 121 | 0 |
| unverifiable | 120 | 120 | 0 |

## Main results

| Conditional accuracy | Conditional Macro-F1 | MCC | Strict accuracy | Truncated pairs |
| --- | --- | --- | --- | --- |
| 0.7833 | 0.7838 | 0.7145 | 0.7833 | 0 |

These results are descriptive for the atomizer test set. The label distribution is strongly imbalanced, so they must not be presented as the final balanced internal-evaluation result.

## Class metrics on valid atomizations

| Label | Precision | Recall | F1 | Support |
| --- | --- | --- | --- | --- |
| supported | 0.7803 | 0.8583 | 0.8175 | 120 |
| partially_supported | 0.6763 | 0.7899 | 0.7287 | 119 |
| contradicted | 0.8033 | 0.8099 | 0.8066 | 121 |
| unverifiable | 0.9310 | 0.6750 | 0.7826 | 120 |

## Atomizer failures

Gemma failed to produce a usable atom list for **0** of **480** inputs. Full records are in `tables/atomizer_failures.csv` and the run-level `atomizer_failures.jsonl` file.

## Figures

- [Pipeline scores](figures/pipeline_scores.svg)
- [Gold-label distribution and scored coverage](figures/gold_label_distribution.svg)
- [Atom-level NLI label distribution](figures/atom_label_distribution.svg)
- [Valid-subset confusion matrix](figures/confusion_matrix_valid_subset.svg)

## Interpretation notes

- Evaluated on the exact 480 held-out gold test examples from TR-FactBench v1.0.
- Claims were atomized using google/gemma-4-E2B-it + QLoRA adapter with robust token generation.
- 480 out of 480 claims were validly atomized (100.0% coverage) yielding 998 atoms.
- NLI verification was conducted with MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7.
- Macro-F1 reached 0.7838 and accuracy reached 78.33%.

## Limitations

- Uses hard NLI labels with flat deterministic aggregation without probability calibration.
- Does not include sentence-level or multi-hop retrieval over external documents.

## Next steps

- Run sentence-grouped and contradiction-priority aggregation ablations.
- Analyze the 127 disagreement cases between K1 and K2.
- Integrate the LLM Judge for hybrid arbitration on disagreements.

## Reproducibility

```powershell
C:\Python314\python.exe scripts\45_run_k2_from_gemma_atoms.py --input "data\processed\atom_level\gemma_predicted_gold480\k2_input.jsonl" --model "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7" --run-id "K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7" --runs-dir "runs" --batch-size 8 --max-length 512 --device None
```

```powershell
C:\Python314\python.exe scripts\65_build_gemma_pipeline_report.py --config "configs\experiments\K2-PIPE-PRED-GOLD480-v1.json"
```
