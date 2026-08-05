# Aggregation ablation protocol

This experiment reuses frozen atom-level NLI predictions. It does not load a transformer model and does not repeat GPU inference.

## Compared rules

### Flat

- all atoms entailment → `supported`
- otherwise any entailment → `partially_supported`
- otherwise any contradiction → `contradicted`
- otherwise → `unverifiable`

This is the K2 pilot baseline.

### Contradiction-priority

- all atoms entailment → `supported`
- otherwise any contradiction → `contradicted`
- otherwise any entailment → `partially_supported`
- otherwise → `unverifiable`

This rule tests whether a single contradicted component should invalidate the full claim.

### Sentence-grouped

Atoms are automatically aligned to the sentence in the original claim with the strongest lexical overlap. Contradiction dominates within one source sentence. Sentence-level outcomes are then combined:

- all sentences supported → `supported`
- at least one supported/partially-supported sentence → `partially_supported`
- otherwise any contradicted sentence → `contradicted`
- otherwise → `unverifiable`

This rule preserves a distinction between a false conjunction inside one sentence and a multi-sentence claim containing both supported and contradicted statements.

## Command

```powershell
C:\Python314\python.exe scripts\55_run_aggregation_ablation.py --config "configs\experiments\K2-AGG-ABLATION-ASSISTED-PILOT-v1.1.json"
```

## Outputs

The report is generated under:

```text
reports/experiments/K2-AGG-ABLATION-ASSISTED-PILOT-v1.1/
```

It contains summary and class metrics, changed-claim tables, exact McNemar comparisons, confusion matrices, derived predictions, source hashes, figures, and a Markdown interpretation report.
