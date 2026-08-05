from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .experiment_reporting import (
    CLAIM_LABELS,
    ATOM_LABELS,
    fmt,
    model_display_name,
    read_json,
    read_jsonl,
    sha256_file,
    write_confusion_svg,
    write_count_bar_svg,
    write_csv,
    write_grouped_bar_svg,
)


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _update_registry(
    registry_path: Path,
    config: dict[str, Any],
    model_name: str,
    macro_f1: float,
    report_dir: Path,
) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    experiment_id = str(config["experiment_id"])
    header = [
        "# Experiment registry",
        "",
        "This file indexes reproducible experiments. Detailed reports live under `reports/experiments/`.",
        "",
        "| Experiment | Stage | Status | Best model | Macro-F1 | Report |",
        "|---|---|---|---|---:|---|",
    ]
    row = (
        f"| `{experiment_id}` | {config.get('stage', 'unspecified')} | "
        f"{config.get('status', 'unspecified')} | {model_name} | {fmt(macro_f1)} | "
        f"[{experiment_id}](../{report_dir.as_posix()}/README.md) |"
    )
    if registry_path.exists():
        lines = registry_path.read_text(encoding="utf-8").splitlines()
        replaced = False
        for index, line in enumerate(lines):
            if f"`{experiment_id}`" in line and line.lstrip().startswith("|"):
                lines[index] = row
                replaced = True
                break
        if not replaced:
            lines.append(row)
    else:
        lines = [*header, row]
    registry_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_gemma_pipeline_report(config_path: Path, project_root: Path) -> Path:
    config = read_json(config_path)
    experiment_id = str(config["experiment_id"])
    run_id = str(config["run_id"])
    runs_dir = project_root / str(config.get("runs_dir", "runs"))
    reports_root = project_root / str(config.get("reports_dir", "reports/experiments"))
    run_dir = runs_dir / run_id
    required = [
        "metrics.json",
        "manifest.json",
        "predictions.jsonl",
        "scored_predictions.jsonl",
        "atom_predictions.jsonl",
        "atomizer_failures.jsonl",
    ]
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Run {run_id} is missing: {', '.join(missing)}")

    metrics = read_json(run_dir / "metrics.json")
    manifest = read_json(run_dir / "manifest.json")
    predictions = read_jsonl(run_dir / "predictions.jsonl")
    scored = read_jsonl(run_dir / "scored_predictions.jsonl")
    atom_predictions = read_jsonl(run_dir / "atom_predictions.jsonl")
    failures = read_jsonl(run_dir / "atomizer_failures.jsonl")

    output_dir = reports_root / experiment_id
    figures_dir = output_dir / "figures"
    tables_dir = output_dir / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    metadata = metrics.get("model_metadata", {})
    pipeline = metrics.get("pipeline_summary", {})
    strict = metrics.get("strict_end_to_end", {})
    model_id = str(metadata.get("model_id") or "")
    model_name = model_display_name(model_id, run_id)

    summary_row = {
        "run_id": run_id,
        "model": model_name,
        "model_id": model_id,
        "evaluation_scope": metrics.get("evaluation_scope"),
        "n_input_claims": strict.get("n_input_claims"),
        "n_scored_claims": strict.get("n_scored_claims"),
        "n_atomizer_failures": strict.get("n_atomizer_failures"),
        "coverage": strict.get("coverage"),
        "conditional_accuracy": metrics.get("accuracy"),
        "conditional_macro_f1": metrics.get("macro_f1"),
        "conditional_weighted_f1": metrics.get("weighted_f1"),
        "conditional_mcc": metrics.get("mcc"),
        "strict_accuracy_failures_as_incorrect": strict.get("accuracy_failures_counted_as_incorrect"),
        "n_atoms": pipeline.get("n_atoms"),
        "n_truncated_pairs": metadata.get("n_truncated_pairs"),
        "pairs_per_second": metadata.get("pairs_per_second"),
        "peak_gpu_memory_bytes": metadata.get("peak_gpu_memory_bytes"),
        "model_revision": metadata.get("model_revision"),
    }
    write_csv(tables_dir / "pipeline_metrics.csv", list(summary_row.keys()), [summary_row])

    class_rows: list[dict[str, Any]] = []
    report = metrics.get("classification_report", {})
    for label in CLAIM_LABELS:
        row = report.get(label, {})
        class_rows.append({
            "label": label,
            "precision": row.get("precision"),
            "recall": row.get("recall"),
            "f1_score": row.get("f1-score"),
            "support": row.get("support"),
        })
    write_csv(tables_dir / "class_metrics_valid_subset.csv", list(class_rows[0].keys()), class_rows)

    matrix = metrics.get("confusion_matrix", [])
    matrix_rows = []
    for gold_index, gold_label in enumerate(CLAIM_LABELS):
        matrix_rows.append({
            "gold_label": gold_label,
            **{
                f"pred_{label}": matrix[gold_index][pred_index]
                for pred_index, label in enumerate(CLAIM_LABELS)
            },
        })
    write_csv(
        tables_dir / "confusion_matrix_valid_subset.csv",
        ["gold_label", *[f"pred_{label}" for label in CLAIM_LABELS]],
        matrix_rows,
    )
    write_confusion_svg(
        figures_dir / "confusion_matrix_valid_subset.svg",
        f"Valid-subset confusion matrix — {model_name}",
        CLAIM_LABELS,
        matrix,
    )

    failure_rows = [{
        "example_id": item.get("example_id"),
        "source_example_id": item.get("source_example_id"),
        "domain": item.get("domain"),
        "gold_label": item.get("gold_label"),
        "failure_reason": item.get("failure_reason"),
        "json_valid": item.get("json_valid"),
        "atom_count_correct": item.get("atom_count_correct"),
        "claim": item.get("claim"),
    } for item in failures]
    failure_fields = list(failure_rows[0].keys()) if failure_rows else [
        "example_id", "source_example_id", "domain", "gold_label", "failure_reason",
        "json_valid", "atom_count_correct", "claim",
    ]
    write_csv(tables_dir / "atomizer_failures.csv", failure_fields, failure_rows)

    prediction_rows = [{
        "example_id": item.get("example_id"),
        "source_example_id": item.get("source_example_id"),
        "domain": item.get("domain"),
        "gold_label": item.get("gold_label"),
        "pred_label": item.get("pred_label"),
        "is_correct": item.get("is_correct"),
        "pipeline_status": item.get("pipeline_status"),
        "n_atoms": item.get("n_atoms"),
        "json_valid": item.get("json_valid"),
        "atom_count_correct": item.get("atom_count_correct"),
    } for item in predictions]
    write_csv(tables_dir / "claim_predictions.csv", list(prediction_rows[0].keys()), prediction_rows)

    gold_counts = Counter(item["gold_label"] for item in predictions)
    scored_gold_counts = Counter(item["gold_label"] for item in scored)
    failure_gold_counts = Counter(item["gold_label"] for item in failures)
    label_rows = [{
        "label": label,
        "input_count": gold_counts.get(label, 0),
        "scored_count": scored_gold_counts.get(label, 0),
        "failure_count": failure_gold_counts.get(label, 0),
    } for label in CLAIM_LABELS]
    write_csv(tables_dir / "gold_label_distribution.csv", list(label_rows[0].keys()), label_rows)
    write_count_bar_svg(
        figures_dir / "gold_label_distribution.svg",
        "Input-label distribution and scored coverage",
        CLAIM_LABELS,
        [
            ("Input", [gold_counts.get(label, 0) for label in CLAIM_LABELS]),
            ("Scored", [scored_gold_counts.get(label, 0) for label in CLAIM_LABELS]),
        ],
    )

    atom_counts = Counter(item["pred_label"] for item in atom_predictions)
    write_count_bar_svg(
        figures_dir / "atom_label_distribution.svg",
        "Gemma-atom NLI label distribution",
        ATOM_LABELS,
        [(model_name, [atom_counts.get(label, 0) for label in ATOM_LABELS])],
    )
    write_grouped_bar_svg(
        figures_dir / "pipeline_scores.svg",
        "Gemma-predicted atom pipeline scores",
        ["Conditional accuracy", "Conditional Macro-F1", "Strict accuracy"],
        [(model_name, [
            float(metrics.get("accuracy", 0)),
            float(metrics.get("macro_f1", 0)),
            float(strict.get("accuracy_failures_counted_as_incorrect", 0)),
        ])],
        y_max=1.0,
        y_label="Score",
    )

    gold_table = [[
        label,
        gold_counts.get(label, 0),
        scored_gold_counts.get(label, 0),
        failure_gold_counts.get(label, 0),
    ] for label in CLAIM_LABELS]
    class_table = [[
        row["label"],
        fmt(row["precision"]),
        fmt(row["recall"]),
        fmt(row["f1_score"]),
        int(row["support"] or 0),
    ] for row in class_rows]

    notes = [str(note) for note in config.get("notes", [])]
    limitations = [str(note) for note in config.get("limitations", [])]
    next_steps = [str(note) for note in config.get("next_steps", [])]
    markdown = [
        f"# {config.get('title', experiment_id)}",
        "",
        f"- **Experiment ID:** `{experiment_id}`",
        f"- **Status:** {config.get('status', 'unspecified')}",
        f"- **Stage:** {config.get('stage', 'unspecified')}",
        f"- **Run ID:** `{run_id}`",
        f"- **Model:** `{model_id}`",
        f"- **Aggregation:** {config.get('aggregation', 'flat deterministic aggregation')}",
        "",
        "## Research question",
        "",
        str(config.get("research_question", "Not specified.")),
        "",
        "## Evaluation policy",
        "",
        "The four-class metrics are computed only for examples where Gemma produced a valid, non-empty atom list. Atomizer failures are preserved as pipeline abstentions rather than being assigned an arbitrary four-class fallback label.",
        "",
        "Two accuracy values are therefore reported:",
        "",
        "- **Conditional accuracy:** accuracy among valid atomizations.",
        "- **Strict end-to-end accuracy:** valid correct predictions divided by all input claims, with atomizer failures counted as incorrect.",
        "",
        "A strict four-class Macro-F1 is not reported because the failures do not belong to one of the four semantic claim labels.",
        "",
        "## Dataset and coverage",
        "",
        _markdown_table(
            ["Input claims", "Scored claims", "Atomizer failures", "Coverage", "Predicted atoms"],
            [[
                strict.get("n_input_claims"),
                strict.get("n_scored_claims"),
                strict.get("n_atomizer_failures"),
                fmt(strict.get("coverage")),
                pipeline.get("n_atoms"),
            ]],
        ),
        "",
        _markdown_table(["Gold label", "Input", "Scored", "Failures"], gold_table),
        "",
        "## Main results",
        "",
        _markdown_table(
            ["Conditional accuracy", "Conditional Macro-F1", "MCC", "Strict accuracy", "Truncated pairs"],
            [[
                fmt(metrics.get("accuracy")),
                fmt(metrics.get("macro_f1")),
                fmt(metrics.get("mcc")),
                fmt(strict.get("accuracy_failures_counted_as_incorrect")),
                metadata.get("n_truncated_pairs"),
            ]],
        ),
        "",
        "These results are descriptive for the atomizer test set. The label distribution is strongly imbalanced, so they must not be presented as the final balanced internal-evaluation result.",
        "",
        "## Class metrics on valid atomizations",
        "",
        _markdown_table(["Label", "Precision", "Recall", "F1", "Support"], class_table),
        "",
        "## Atomizer failures",
        "",
        f"Gemma failed to produce a usable atom list for **{len(failures)}** of **{len(predictions)}** inputs. Full records are in `tables/atomizer_failures.csv` and the run-level `atomizer_failures.jsonl` file.",
        "",
        "## Figures",
        "",
        "- [Pipeline scores](figures/pipeline_scores.svg)",
        "- [Gold-label distribution and scored coverage](figures/gold_label_distribution.svg)",
        "- [Atom-level NLI label distribution](figures/atom_label_distribution.svg)",
        "- [Valid-subset confusion matrix](figures/confusion_matrix_valid_subset.svg)",
        "",
        "## Interpretation notes",
        "",
        *([f"- {note}" for note in notes] or ["- No notes were supplied."]),
        "",
        "## Limitations",
        "",
        *([f"- {note}" for note in limitations] or ["- No limitations were supplied."]),
        "",
        "## Next steps",
        "",
        *([f"- {note}" for note in next_steps] or ["- No next steps were supplied."]),
        "",
        "## Reproducibility",
        "",
        "```powershell",
        " ".join([
            "C:\\Python314\\python.exe",
            "scripts\\45_run_k2_from_gemma_atoms.py",
            "--input", f'\"{manifest.get("arguments", {}).get("input", config.get("dataset_path", ""))}\"',
            "--model", f'\"{manifest.get("arguments", {}).get("model", model_id)}\"',
            "--run-id", f'\"{run_id}\"',
            "--runs-dir", f'\"{manifest.get("arguments", {}).get("runs_dir", "runs")}\"',
            "--batch-size", str(manifest.get("arguments", {}).get("batch_size", 1)),
            "--max-length", str(manifest.get("arguments", {}).get("max_length", 512)),
            "--device", str(manifest.get("arguments", {}).get("device", "cuda")),
        ]),
        "```",
        "",
        "```powershell",
        f'C:\\Python314\\python.exe scripts\\65_build_gemma_pipeline_report.py --config \"{config_path.relative_to(project_root)}\"',
        "```",
        "",
    ]
    (output_dir / "README.md").write_text("\n".join(markdown), encoding="utf-8")

    artifact_manifest = {
        "experiment_id": experiment_id,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "run_id": run_id,
        "metrics_sha256": sha256_file(run_dir / "metrics.json"),
        "manifest_sha256": sha256_file(run_dir / "manifest.json"),
        "predictions_sha256": sha256_file(run_dir / "predictions.jsonl"),
        "atom_predictions_sha256": sha256_file(run_dir / "atom_predictions.jsonl"),
        "failures_sha256": sha256_file(run_dir / "atomizer_failures.jsonl"),
        "model": model_name,
        "conditional_macro_f1": metrics.get("macro_f1"),
        "strict_accuracy": strict.get("accuracy_failures_counted_as_incorrect"),
        "coverage": strict.get("coverage"),
    }
    (output_dir / "report_manifest.json").write_text(
        json.dumps(artifact_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    registry_path = project_root / str(config.get("registry_path", "docs/EXPERIMENTS.md"))
    _update_registry(
        registry_path,
        config,
        model_name,
        float(metrics.get("macro_f1", 0.0)),
        output_dir.relative_to(project_root),
    )
    return output_dir
