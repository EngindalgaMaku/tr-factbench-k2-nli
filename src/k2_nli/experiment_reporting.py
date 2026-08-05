from __future__ import annotations

import csv
import hashlib
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CLAIM_LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
ATOM_LABELS = ["entailment", "neutral", "contradiction"]


@dataclass(frozen=True)
class RunBundle:
    run_id: str
    run_dir: Path
    metrics: dict[str, Any]
    manifest: dict[str, Any]
    predictions: list[dict[str, Any]]
    display_name: str


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def model_display_name(model_id: str, run_id: str) -> str:
    lowered = model_id.lower()
    if "mdeberta-v3-base-xnli-multilingual-nli-2mil7" in lowered:
        return "mDeBERTa-v3-base 2mil7"
    if "xlm-roberta-large-xnli" in lowered:
        return "XLM-R-large XNLI"
    if model_id:
        return model_id
    return run_id


def load_run(runs_dir: Path, run_id: str) -> RunBundle:
    run_dir = runs_dir / run_id
    required = ["metrics.json", "manifest.json", "predictions.jsonl"]
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Run {run_id} is missing: {', '.join(missing)}")
    metrics = read_json(run_dir / "metrics.json")
    manifest = read_json(run_dir / "manifest.json")
    predictions = read_jsonl(run_dir / "predictions.jsonl")
    model_id = str(metrics.get("model_metadata", {}).get("model_id", ""))
    return RunBundle(
        run_id=run_id,
        run_dir=run_dir,
        metrics=metrics,
        manifest=manifest,
        predictions=predictions,
        display_name=model_display_name(model_id, run_id),
    )


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any, digits: int = 4) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def escape(text: Any) -> str:
    return html.escape(str(text), quote=True)


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="19" font-weight="700">{escape(title)}</text>',
    ]


def write_grouped_bar_svg(
    path: Path,
    title: str,
    categories: list[str],
    series: list[tuple[str, list[float]]],
    y_max: float,
    y_label: str,
) -> None:
    width, height = 960, 520
    left, right, top, bottom = 90, 30, 70, 110
    chart_w, chart_h = width - left - right, height - top - bottom
    palette = ["#2563eb", "#f97316", "#16a34a", "#7c3aed", "#dc2626"]
    lines = svg_header(width, height, title)
    lines.append(f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#111827"/>')
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#111827"/>')
    for tick in range(0, 6):
        value = y_max * tick / 5
        y = top + chart_h - (value / y_max) * chart_h
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_w}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        lines.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{value:.2f}</text>')
    group_w = chart_w / max(len(categories), 1)
    bar_w = min(42, group_w / (len(series) + 1))
    for ci, category in enumerate(categories):
        center = left + group_w * (ci + 0.5)
        lines.append(f'<text x="{center:.1f}" y="{top + chart_h + 28}" text-anchor="middle" font-family="Arial" font-size="13">{escape(category)}</text>')
        total_w = bar_w * len(series)
        start = center - total_w / 2
        for si, (name, values) in enumerate(series):
            value = float(values[ci])
            bar_h = min(value / y_max, 1.0) * chart_h
            x = start + si * bar_w + 2
            y = top + chart_h - bar_h
            color = palette[si % len(palette)]
            lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 4:.1f}" height="{bar_h:.1f}" rx="3" fill="{color}"/>')
            lines.append(f'<text x="{x + (bar_w - 4) / 2:.1f}" y="{max(y - 7, top + 10):.1f}" text-anchor="middle" font-family="Arial" font-size="11">{value:.3f}</text>')
    legend_y = height - 35
    legend_total = sum(26 + len(name) * 8 for name, _ in series)
    legend_x = max(left, (width - legend_total) / 2)
    for si, (name, _) in enumerate(series):
        color = palette[si % len(palette)]
        lines.append(f'<rect x="{legend_x:.1f}" y="{legend_y - 12}" width="14" height="14" rx="2" fill="{color}"/>')
        lines.append(f'<text x="{legend_x + 20:.1f}" y="{legend_y}" font-family="Arial" font-size="12">{escape(name)}</text>')
        legend_x += 26 + len(name) * 8
    lines.append(f'<text x="22" y="{top + chart_h / 2}" transform="rotate(-90 22 {top + chart_h / 2})" text-anchor="middle" font-family="Arial" font-size="13">{escape(y_label)}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_count_bar_svg(
    path: Path,
    title: str,
    categories: list[str],
    series: list[tuple[str, list[int]]],
) -> None:
    maximum = max((max(values) for _, values in series), default=1)
    rounded_max = max(10, int((maximum * 1.15 + 9) // 10 * 10))
    write_grouped_bar_svg(
        path=path,
        title=title,
        categories=categories,
        series=[(name, [float(x) for x in values]) for name, values in series],
        y_max=float(rounded_max),
        y_label="Atom count",
    )


def write_confusion_svg(path: Path, title: str, labels: list[str], matrix: list[list[int]]) -> None:
    width, height = 760, 650
    left, top, cell = 190, 100, 95
    max_value = max(max(row) for row in matrix) if matrix else 1
    lines = svg_header(width, height, title)
    for index, label in enumerate(labels):
        x = left + index * cell + cell / 2
        y = top + index * cell + cell / 2
        lines.append(f'<text x="{x:.1f}" y="{top - 18}" text-anchor="middle" font-family="Arial" font-size="12">{escape(label)}</text>')
        lines.append(f'<text x="{left - 15}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{escape(label)}</text>')
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            intensity = value / max_value if max_value else 0
            blue = int(245 - 145 * intensity)
            fill = f"rgb({blue},{blue + 5},{255})"
            x = left + col_index * cell
            y = top + row_index * cell
            lines.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#ffffff" stroke-width="2"/>')
            lines.append(f'<text x="{x + cell / 2}" y="{y + cell / 2 + 6}" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">{value}</text>')
    lines.append(f'<text x="{left + len(labels) * cell / 2}" y="{top + len(labels) * cell + 45}" text-anchor="middle" font-family="Arial" font-size="14">Predicted label</text>')
    y_mid = top + len(labels) * cell / 2
    lines.append(f'<text x="45" y="{y_mid}" transform="rotate(-90 45 {y_mid})" text-anchor="middle" font-family="Arial" font-size="14">Gold label</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def prediction_comparison(runs: list[RunBundle]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    by_run = {run.run_id: {row["example_id"]: row for row in run.predictions} for run in runs}
    ids = sorted(set.intersection(*(set(rows) for rows in by_run.values())))
    output: list[dict[str, Any]] = []
    buckets: dict[str, int] = {}
    for example_id in ids:
        first = by_run[runs[0].run_id][example_id]
        correct_flags = [bool(by_run[run.run_id][example_id].get("is_correct")) for run in runs]
        if all(correct_flags):
            bucket = "all_correct"
        elif not any(correct_flags):
            bucket = "all_wrong"
        elif sum(correct_flags) == 1:
            winner = runs[correct_flags.index(True)].display_name
            bucket = f"only_{winner}_correct"
        else:
            bucket = "mixed_correctness"
        buckets[bucket] = buckets.get(bucket, 0) + 1
        row: dict[str, Any] = {
            "example_id": example_id,
            "context_id": first.get("context_id"),
            "domain": first.get("domain"),
            "gold_label": first.get("gold_label"),
            "n_atoms": first.get("n_atoms"),
            "atomization_status": first.get("atomization_status"),
            "comparison_bucket": bucket,
            "claim": first.get("claim"),
        }
        for run in runs:
            pred = by_run[run.run_id][example_id]
            prefix = run.run_id
            row[f"{prefix}__pred_label"] = pred.get("pred_label")
            row[f"{prefix}__is_correct"] = pred.get("is_correct")
        output.append(row)
    return output, buckets


def build_report(config_path: Path, project_root: Path) -> Path:
    config = read_json(config_path)
    experiment_id = str(config["experiment_id"])
    runs_dir = project_root / str(config.get("runs_dir", "runs"))
    reports_root = project_root / str(config.get("reports_dir", "reports/experiments"))
    output_dir = reports_root / experiment_id
    figures_dir = output_dir / "figures"
    tables_dir = output_dir / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    runs = [load_run(runs_dir, run_id) for run_id in config["run_ids"]]
    summary_rows: list[dict[str, Any]] = []
    class_rows: list[dict[str, Any]] = []
    for run in runs:
        metrics = run.metrics
        metadata = metrics.get("model_metadata", {})
        summary_rows.append({
            "run_id": run.run_id,
            "model": run.display_name,
            "model_id": metadata.get("model_id"),
            "accuracy": metrics.get("accuracy"),
            "macro_f1": metrics.get("macro_f1"),
            "weighted_f1": metrics.get("weighted_f1"),
            "mcc": metrics.get("mcc"),
            "n_claims": metrics.get("pipeline_summary", {}).get("n_claims"),
            "n_atoms": metrics.get("pipeline_summary", {}).get("n_atoms"),
            "n_truncated_pairs": metadata.get("n_truncated_pairs"),
            "pairs_per_second": metadata.get("pairs_per_second"),
            "peak_gpu_memory_bytes": metadata.get("peak_gpu_memory_bytes"),
            "model_revision": metadata.get("model_revision"),
        })
        report = metrics.get("classification_report", {})
        for label in CLAIM_LABELS:
            row = report.get(label, {})
            class_rows.append({
                "run_id": run.run_id,
                "model": run.display_name,
                "label": label,
                "precision": row.get("precision"),
                "recall": row.get("recall"),
                "f1_score": row.get("f1-score"),
                "support": row.get("support"),
            })
        matrix = metrics.get("confusion_matrix", [])
        matrix_rows = []
        for gold_index, gold_label in enumerate(CLAIM_LABELS):
            matrix_rows.append({"gold_label": gold_label, **{
                f"pred_{label}": matrix[gold_index][pred_index]
                for pred_index, label in enumerate(CLAIM_LABELS)
            }})
        write_csv(
            tables_dir / f"confusion_matrix__{run.run_id}.csv",
            ["gold_label", *[f"pred_{label}" for label in CLAIM_LABELS]],
            matrix_rows,
        )
        write_confusion_svg(
            figures_dir / f"confusion_matrix__{run.run_id}.svg",
            f"Confusion matrix — {run.display_name}",
            CLAIM_LABELS,
            matrix,
        )

    write_csv(tables_dir / "model_metrics.csv", list(summary_rows[0].keys()), summary_rows)
    write_csv(tables_dir / "class_metrics.csv", list(class_rows[0].keys()), class_rows)

    comparison_rows, comparison_buckets = prediction_comparison(runs)
    comparison_fields = list(comparison_rows[0].keys()) if comparison_rows else []
    write_csv(tables_dir / "claim_level_comparison.csv", comparison_fields, comparison_rows)
    write_csv(
        tables_dir / "comparison_bucket_counts.csv",
        ["bucket", "count"],
        [{"bucket": key, "count": value} for key, value in sorted(comparison_buckets.items())],
    )

    write_grouped_bar_svg(
        figures_dir / "model_comparison.svg",
        "Atom-pipeline model comparison",
        ["Accuracy", "Macro-F1", "MCC"],
        [(run.display_name, [
            float(run.metrics.get("accuracy", 0)),
            float(run.metrics.get("macro_f1", 0)),
            float(run.metrics.get("mcc", 0)),
        ]) for run in runs],
        y_max=1.0,
        y_label="Score",
    )
    write_count_bar_svg(
        figures_dir / "atom_label_distribution.svg",
        "Atom-level prediction distribution",
        ATOM_LABELS,
        [(run.display_name, [
            int(run.metrics.get("pipeline_summary", {}).get("atom_pred_label_counts", {}).get(label, 0))
            for label in ATOM_LABELS
        ]) for run in runs],
    )

    best = max(runs, key=lambda run: float(run.metrics.get("macro_f1", 0)))
    worst = min(runs, key=lambda run: float(run.metrics.get("macro_f1", 0)))
    delta = float(best.metrics.get("macro_f1", 0)) - float(worst.metrics.get("macro_f1", 0))
    pipeline = best.metrics.get("pipeline_summary", {})
    atomization_counts = pipeline.get("atomization_status_counts", {})
    current_table = [[
        run.display_name,
        fmt(run.metrics.get("accuracy")),
        fmt(run.metrics.get("macro_f1")),
        fmt(run.metrics.get("mcc")),
        run.metrics.get("model_metadata", {}).get("n_truncated_pairs"),
        fmt(run.metrics.get("model_metadata", {}).get("pairs_per_second"), 2),
    ] for run in runs]
    class_table = []
    for label in CLAIM_LABELS:
        row = [label]
        for run in runs:
            item = run.metrics.get("classification_report", {}).get(label, {})
            row.append(fmt(item.get("f1-score")))
        class_table.append(row)

    notes = [str(note) for note in config.get("notes", [])]
    limitations = [str(note) for note in config.get("limitations", [])]
    next_steps = [str(note) for note in config.get("next_steps", [])]
    markdown = [
        f"# {config.get('title', experiment_id)}",
        "",
        f"**Experiment ID:** `{experiment_id}`  ",
        f"**Status:** {config.get('status', 'unspecified')}  ",
        f"**Stage:** {config.get('stage', 'unspecified')}  ",
        f"**Dataset:** `{config.get('dataset_path', 'unspecified')}`  ",
        "",
        "## Research question",
        "",
        str(config.get("research_question", "Not specified.")),
        "",
        "## Experimental setup",
        "",
        f"- Claims: **{pipeline.get('n_claims', 'n/a')}**",
        f"- Atoms: **{pipeline.get('n_atoms', 'n/a')}**",
        f"- Mean atoms per claim: **{fmt(pipeline.get('mean_atoms_per_claim'))}**",
        f"- Claim labels: {', '.join(CLAIM_LABELS)}",
        f"- Aggregation: {config.get('aggregation', 'deterministic flat aggregation')}",
        f"- Atomization status counts: `{json.dumps(atomization_counts, ensure_ascii=False)}`",
        "",
        "## Main results",
        "",
        markdown_table(
            ["Model", "Accuracy", "Macro-F1", "MCC", "Truncated pairs", "Pairs/s"],
            current_table,
        ),
        "",
        f"The best model is **{best.display_name}** with Macro-F1 **{fmt(best.metrics.get('macro_f1'))}**. "
        f"Its Macro-F1 advantage over {worst.display_name} is **{fmt(delta)}**.",
        "",
        "![Model comparison](figures/model_comparison.svg)",
        "",
        "## Class-level F1",
        "",
        markdown_table(["Label", *[run.display_name for run in runs]], class_table),
        "",
        "## Atom decision distribution",
        "",
        "![Atom-label distribution](figures/atom_label_distribution.svg)",
        "",
        "The atom-label distribution should be interpreted together with claim-level errors. A model that produces substantially more `neutral` decisions can inflate the final `unverifiable` class after aggregation.",
        "",
        "## Confusion matrices",
        "",
    ]
    for run in runs:
        markdown.extend([
            f"### {run.display_name}",
            "",
            f"![Confusion matrix — {run.display_name}](figures/confusion_matrix__{run.run_id}.svg)",
            "",
        ])
    markdown.extend([
        "## Interpretation",
        "",
        *([f"- {note}" for note in notes] or ["- No manual interpretation notes were supplied in the experiment config."]),
        "",
        "## Limitations",
        "",
        *([f"- {note}" for note in limitations] or ["- No limitations were supplied in the experiment config."]),
        "",
        "## Next steps",
        "",
        *([f"- {note}" for note in next_steps] or ["- No next steps were supplied in the experiment config."]),
        "",
        "## Reproducibility",
        "",
        "Run directories:",
        "",
        *[f"- `{run.run_dir.relative_to(project_root).as_posix()}`" for run in runs],
        "",
        "Run commands reconstructed from each manifest:",
        "",
    ])
    for run in runs:
        arguments = run.manifest.get("arguments", {})
        command_parts = ["python", "scripts/40_run_k2_from_atoms.py"]
        if arguments.get("input"):
            command_parts.extend(["--input", f'"{arguments["input"]}"'])
        elif arguments.get("data") and arguments.get("atoms"):
            command_parts.extend(["--data", f'"{arguments["data"]}"', "--atoms", f'"{arguments["atoms"]}"'])
        for key in ["model", "run_id", "runs_dir", "batch_size", "max_length", "device"]:
            value = arguments.get(key)
            if value is not None:
                option = "--" + key.replace("_", "-")
                rendered = f'"{value}"' if isinstance(value, str) and (" " in value or "/" in value or "\\" in value) else str(value)
                command_parts.extend([option, rendered])
        markdown.extend([
            f"### {run.display_name}",
            "",
            "```powershell",
            " ".join(command_parts),
            "```",
            "",
        ])
    markdown.extend([
        "Generated artifacts:",
        "",
        "- `tables/model_metrics.csv`",
        "- `tables/class_metrics.csv`",
        "- `tables/claim_level_comparison.csv`",
        "- `tables/comparison_bucket_counts.csv`",
        "- `figures/model_comparison.svg`",
        "- `figures/atom_label_distribution.svg`",
        "- one confusion-matrix CSV and SVG per run",
        "",
    ])
    (output_dir / "README.md").write_text("\n".join(markdown), encoding="utf-8")

    artifact_manifest = {
        "experiment_id": experiment_id,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "runs": [{
            "run_id": run.run_id,
            "metrics_sha256": sha256_file(run.run_dir / "metrics.json"),
            "manifest_sha256": sha256_file(run.run_dir / "manifest.json"),
            "predictions_sha256": sha256_file(run.run_dir / "predictions.jsonl"),
        } for run in runs],
        "best_model": best.display_name,
        "best_macro_f1": best.metrics.get("macro_f1"),
    }
    (output_dir / "report_manifest.json").write_text(
        json.dumps(artifact_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    registry_path = project_root / str(config.get("registry_path", "docs/EXPERIMENTS.md"))
    update_registry(registry_path, config, best, output_dir.relative_to(project_root))
    return output_dir


def update_registry(registry_path: Path, config: dict[str, Any], best: RunBundle, report_dir: Path) -> None:
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
        f"{config.get('status', 'unspecified')} | {best.display_name} | "
        f"{fmt(best.metrics.get('macro_f1'))} | [{experiment_id}](../{report_dir.as_posix()}/README.md) |"
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
