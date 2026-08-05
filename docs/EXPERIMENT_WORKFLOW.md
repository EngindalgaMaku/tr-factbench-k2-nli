# Experiment workflow

The repository separates machine outputs from human-readable scientific records.

```text
configs/experiments/       Versioned experiment definitions
runs/                      Raw run outputs: predictions, metrics, manifests
reports/experiments/       Generated reports, CSV tables and SVG figures
docs/EXPERIMENTS.md        Experiment registry
scripts/                   Reproducible execution and reporting commands
data/processed/            Versioned experiment inputs
```

## What should be committed?

Commit the experiment config, code, dataset version, metrics, manifests, and generated report. Prediction files may also be committed when their size and data policy allow it. Model weights and Hugging Face caches must not be committed.

A zip archive is only a transport or backup artifact. It is not a substitute for an experiment report.

## Standard sequence

1. Run inference and preserve the run directory.
2. Build the report from the versioned experiment config.
3. Inspect the Markdown report, CSV tables, SVG figures, and report manifest.
4. Commit the code, config, report, metrics, and manifests.
5. Register methodological changes as a new experiment version instead of overwriting an old run.

## Report generation

```powershell
C:\Python314\python.exe scripts\50_build_experiment_report.py --config "configs\experiments\K2-ATOM-ASSISTED-ZS-PILOT-v1.1.json"
```

The command creates:

```text
reports/experiments/K2-ATOM-ASSISTED-ZS-PILOT-v1.1/
├── README.md
├── report_manifest.json
├── figures/
│   ├── model_comparison.svg
│   ├── atom_label_distribution.svg
│   └── confusion_matrix__<run-id>.svg
└── tables/
    ├── model_metrics.csv
    ├── class_metrics.csv
    ├── claim_level_comparison.csv
    ├── comparison_bucket_counts.csv
    └── confusion_matrix__<run-id>.csv
```

The same command creates or updates `docs/EXPERIMENTS.md`.
