# Gemma-predicted atom pipeline

This stage evaluates the real K2 path rather than the assistant-assisted atom pilot:

```text
context + claim
→ Gemma pred_atoms
→ zero-shot mDeBERTa NLI for each atom
→ flat deterministic aggregation
→ four-class claim decision
```

## Input schema

Each JSONL object must contain:

- `example_id`
- `source_example_id`
- `domain`
- `context`
- `claim`
- `gold_label`
- `pred_atoms`
- `json_valid`
- `atom_count_correct`

Only `pred_atoms` is used as the atomizer prediction. Reference atom fields must not be substituted into the pipeline.

## Failure policy

Invalid Gemma JSON or an empty atom list is a pipeline abstention. These records are:

- retained in `predictions.jsonl`,
- written separately to `atomizer_failures.jsonl`,
- excluded from conditional four-class precision/recall/F1,
- counted as incorrect in strict end-to-end accuracy.

No arbitrary fallback such as `unverifiable` is assigned. Such a fallback would conflate missing atomizer output with a semantic NLI decision.

## Outputs

The run directory contains:

- `predictions.jsonl`: all input claims, including failures
- `scored_predictions.jsonl`: valid atomizations only
- `atom_predictions.jsonl`: atom-level NLI scores
- `atomizer_failures.jsonl`: unusable Gemma outputs
- `metrics.json`: conditional metrics, strict accuracy, coverage and metadata
- `manifest.json`: hashes, revisions and command arguments

The report builder creates Markdown, CSV tables and SVG figures under `reports/experiments/`.
