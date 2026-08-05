# K2 end-to-end pipeline with Gemma-predicted atoms — atomizer test v1

- **Experiment ID:** `K2-PIPE-PRED-ZS-ATOMIZERTEST-v1`
- **Status:** exploratory end-to-end atomizer test
- **Stage:** predicted-atom pipeline integration
- **Run ID:** `K2-PIPE-PRED-ZS-ATOMIZERTEST-v1__mdeberta_base_2mil7`
- **Model:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`
- **Aggregation:** flat deterministic aggregation over hard atom labels

## Research question

When Gemma-generated Turkish claim atoms are verified with the selected mDeBERTa zero-shot NLI model and flat deterministic aggregation, what claim-level performance and pipeline coverage are obtained on the atomizer test set?

## Evaluation policy

The four-class metrics are computed only for examples where Gemma produced a valid, non-empty atom list. Atomizer failures are preserved as pipeline abstentions rather than being assigned an arbitrary four-class fallback label.

Two accuracy values are therefore reported:

- **Conditional accuracy:** accuracy among valid atomizations.
- **Strict end-to-end accuracy:** valid correct predictions divided by all input claims, with atomizer failures counted as incorrect.

A strict four-class Macro-F1 is not reported because the failures do not belong to one of the four semantic claim labels.

## Dataset and coverage

| Input claims | Scored claims | Atomizer failures | Coverage | Predicted atoms |
| --- | --- | --- | --- | --- |
| 161 | 157 | 4 | 0.9752 | 298 |

| Gold label | Input | Scored | Failures |
| --- | --- | --- | --- |
| supported | 108 | 105 | 3 |
| partially_supported | 46 | 46 | 0 |
| contradicted | 5 | 4 | 1 |
| unverifiable | 2 | 2 | 0 |

## Main results

| Conditional accuracy | Conditional Macro-F1 | MCC | Strict accuracy | Truncated pairs |
| --- | --- | --- | --- | --- |
| 0.7580 | 0.5235 | 0.5100 | 0.7391 | 5 |

These results are descriptive for the atomizer test set. The label distribution is strongly imbalanced, so they must not be presented as the final balanced internal-evaluation result.

## Class metrics on valid atomizations

| Label | Precision | Recall | F1 | Support |
| --- | --- | --- | --- | --- |
| supported | 0.8700 | 0.8286 | 0.8488 | 105 |
| partially_supported | 0.6744 | 0.6304 | 0.6517 | 46 |
| contradicted | 0.2222 | 0.5000 | 0.3077 | 4 |
| unverifiable | 0.2000 | 0.5000 | 0.2857 | 2 |

## Atomizer failures

Gemma failed to produce a usable atom list for **4** of **161** inputs. Full records are in `tables/atomizer_failures.csv` and the run-level `atomizer_failures.jsonl` file.

## Figures

- [Pipeline scores](figures/pipeline_scores.svg)
- [Gold-label distribution and scored coverage](figures/gold_label_distribution.svg)
- [Atom-level NLI label distribution](figures/atom_label_distribution.svg)
- [Valid-subset confusion matrix](figures/confusion_matrix_valid_subset.svg)

## Interpretation notes

- The input contains Gemma-predicted atoms rather than assistant-assisted or human-gold atomizations.
- Atomizer failures are retained as abstentions and are not silently dropped or mapped to unverifiable.
- Conditional four-class metrics and strict end-to-end accuracy are reported separately.
- The selected verifier is MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 and the frozen primary aggregation baseline is flat aggregation.

## Limitations

- The set contains 161 claims with a strongly imbalanced gold-label distribution: 108 supported, 46 partially_supported, 5 contradicted, and 2 unverifiable.
- This is an atomizer test set rather than the balanced, independent K2 internal-evaluation split, so the result is not a final system estimate.
- Gemma atom-count correctness is reference-based metadata and does not establish semantic atom quality by itself.
- The experiment uses hard NLI labels and does not include probability calibration, evidence retrieval, or sliding-window inference.

## Next steps

- Inspect all atomizer failures and a stratified sample of atomizer successes, especially atom-count mismatches.
- Create Gemma-predicted atoms for the independent four-class internal-evaluation split.
- Run the same frozen mDeBERTa plus flat-aggregation pipeline on that balanced split.
- Compare direct claim-level, assistant-assisted atom, and Gemma-predicted atom systems on matched examples.

## Reproducibility

```powershell
C:\Python314\python.exe scripts\45_run_k2_from_gemma_atoms.py --input "data\processed\atom_level\gemma_predicted_v1\k2_input.jsonl" --model "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7" --run-id "K2-PIPE-PRED-ZS-ATOMIZERTEST-v1__mdeberta_base_2mil7" --runs-dir "runs" --batch-size 1 --max-length 512 --device cuda
```

```powershell
C:\Python314\python.exe scripts\65_build_gemma_pipeline_report.py --config "configs\experiments\K2-PIPE-PRED-ZS-ATOMIZERTEST-v1.json"
```
