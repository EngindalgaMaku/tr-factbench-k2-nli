from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.stats import binomtest

from .experiment_reporting import (
    fmt,
    markdown_table,
    model_display_name,
    read_json,
    read_jsonl,
    sha256_file,
    write_confusion_svg,
    write_csv,
    write_grouped_bar_svg,
)
from .labels import CLAIM_LABELS, NLI_LABELS
from .metrics import evaluate_predictions

AGGREGATION_RULES = ("flat", "contradiction_priority", "sentence_grouped")
_RULE_TITLES = {
    "flat": "Flat",
    "contradiction_priority": "Contradiction-priority",
    "sentence_grouped": "Sentence-grouped",
}
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_TOKEN_RE = re.compile(r"[^\W_]+", flags=re.UNICODE)


@dataclass(frozen=True)
class SourceRun:
    run_id: str
    run_dir: Path
    model_id: str
    display_name: str
    predictions: list[dict[str, Any]]
    manifest: dict[str, Any]


def normalize_atom_labels(labels: Sequence[str]) -> list[str]:
    normalized = [str(label).strip().lower() for label in labels]
    unknown = set(normalized) - set(NLI_LABELS)
    if unknown:
        raise ValueError(f"Unknown atom labels: {sorted(unknown)}")
    if not normalized:
        raise ValueError("At least one atom label is required")
    return normalized


def aggregate_flat(labels: Sequence[str]) -> str:
    normalized = normalize_atom_labels(labels)
    if all(label == "entailment" for label in normalized):
        return "supported"
    if "entailment" in normalized:
        return "partially_supported"
    if "contradiction" in normalized:
        return "contradicted"
    return "unverifiable"


def aggregate_contradiction_priority(labels: Sequence[str]) -> str:
    normalized = normalize_atom_labels(labels)
    if all(label == "entailment" for label in normalized):
        return "supported"
    if "contradiction" in normalized:
        return "contradicted"
    if "entailment" in normalized:
        return "partially_supported"
    return "unverifiable"


def split_claim_sentences(claim: str) -> list[str]:
    text = str(claim).strip()
    if not text:
        return [""]
    sentences = [part.strip() for part in _SENTENCE_RE.split(text) if part.strip()]
    return sentences or [text]


def tokenize(text: str) -> set[str]:
    return {match.group(0).casefold() for match in _TOKEN_RE.finditer(str(text))}


def sentence_alignment_scores(atom: str, sentence: str) -> tuple[float, float, int]:
    atom_tokens = tokenize(atom)
    sentence_tokens = tokenize(sentence)
    if not atom_tokens or not sentence_tokens:
        return (0.0, 0.0, 0)
    overlap = atom_tokens & sentence_tokens
    atom_recall = len(overlap) / len(atom_tokens)
    union = atom_tokens | sentence_tokens
    jaccard = len(overlap) / len(union) if union else 0.0
    return (atom_recall, jaccard, len(overlap))


def align_atoms_to_sentences(claim: str, atoms: Sequence[dict[str, Any]]) -> list[int]:
    sentences = split_claim_sentences(claim)
    if len(sentences) == 1:
        return [0] * len(atoms)

    assignments: list[int] = []
    for atom_index, atom in enumerate(atoms):
        atom_text = str(atom.get("atom") or atom.get("text") or "")
        scores = [sentence_alignment_scores(atom_text, sentence) for sentence in sentences]
        best_score = max(scores)
        if best_score == (0.0, 0.0, 0):
            # Deterministic fallback preserves atom order when lexical alignment is impossible.
            projected = int(atom_index * len(sentences) / max(len(atoms), 1))
            assignments.append(min(projected, len(sentences) - 1))
        else:
            assignments.append(scores.index(best_score))
    return assignments


def aggregate_sentence_group(labels: Sequence[str]) -> str:
    """Aggregate atoms that belong to one source sentence.

    A contradiction makes the conjunctive sentence false. Entailment mixed with neutral
    remains partially supported rather than fully unverifiable.
    """
    normalized = normalize_atom_labels(labels)
    if all(label == "entailment" for label in normalized):
        return "supported"
    if "contradiction" in normalized:
        return "contradicted"
    if "entailment" in normalized:
        return "partially_supported"
    return "unverifiable"


def aggregate_sentence_grouped(
    claim: str,
    atoms: Sequence[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    if not atoms:
        raise ValueError("At least one atom is required")
    sentences = split_claim_sentences(claim)
    assignments = align_atoms_to_sentences(claim, atoms)
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for atom, sentence_index in zip(atoms, assignments):
        grouped[sentence_index].append(atom)

    group_outputs: list[dict[str, Any]] = []
    for sentence_index in sorted(grouped):
        group_atoms = grouped[sentence_index]
        group_label = aggregate_sentence_group([atom["pred_label"] for atom in group_atoms])
        group_outputs.append({
            "sentence_index": sentence_index,
            "sentence": sentences[sentence_index],
            "atom_ids": [atom.get("atom_id") for atom in group_atoms],
            "atom_labels": [atom["pred_label"] for atom in group_atoms],
            "group_label": group_label,
        })

    group_labels = [group["group_label"] for group in group_outputs]
    if all(label == "supported" for label in group_labels):
        claim_label = "supported"
    elif any(label in {"supported", "partially_supported"} for label in group_labels):
        claim_label = "partially_supported"
    elif "contradicted" in group_labels:
        claim_label = "contradicted"
    else:
        claim_label = "unverifiable"
    return claim_label, group_outputs


def aggregate_prediction(prediction: dict[str, Any], rule: str) -> tuple[str, list[dict[str, Any]] | None]:
    atoms = list(prediction.get("atoms") or [])
    labels = [atom["pred_label"] for atom in atoms]
    if rule == "flat":
        return aggregate_flat(labels), None
    if rule == "contradiction_priority":
        return aggregate_contradiction_priority(labels), None
    if rule == "sentence_grouped":
        return aggregate_sentence_grouped(str(prediction.get("claim", "")), atoms)
    raise ValueError(f"Unknown aggregation rule: {rule}")


def hard_label_metrics(y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, Any]:
    probabilities = np.zeros((len(y_true), len(CLAIM_LABELS)), dtype=float)
    for row, label in enumerate(y_pred):
        probabilities[row, CLAIM_LABELS.index(label)] = 1.0
    metrics = evaluate_predictions(y_true, y_pred, probabilities, CLAIM_LABELS)
    for name in ("nll", "multiclass_brier", "ece"):
        metrics.pop(name, None)
    return metrics


def exact_mcnemar(flat_correct: Sequence[bool], alternative_correct: Sequence[bool]) -> dict[str, Any]:
    if len(flat_correct) != len(alternative_correct):
        raise ValueError("Correctness vectors must have equal length")
    flat_only = sum(bool(flat) and not bool(alt) for flat, alt in zip(flat_correct, alternative_correct))
    alternative_only = sum(not bool(flat) and bool(alt) for flat, alt in zip(flat_correct, alternative_correct))
    discordant = flat_only + alternative_only
    p_value = 1.0 if discordant == 0 else float(
        binomtest(min(flat_only, alternative_only), discordant, p=0.5, alternative="two-sided").pvalue
    )
    return {
        "flat_only_correct": flat_only,
        "alternative_only_correct": alternative_only,
        "discordant": discordant,
        "exact_p_value": p_value,
    }


def load_source_run(project_root: Path, runs_dir: str, run_id: str) -> SourceRun:
    run_dir = project_root / runs_dir / run_id
    predictions_path = run_dir / "predictions.jsonl"
    manifest_path = run_dir / "manifest.json"
    metrics_path = run_dir / "metrics.json"
    missing = [path.name for path in (predictions_path, manifest_path, metrics_path) if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Run {run_id} is missing: {', '.join(missing)}")
    metrics = read_json(metrics_path)
    manifest = read_json(manifest_path)
    model_id = str(metrics.get("model_metadata", {}).get("model_id", ""))
    return SourceRun(
        run_id=run_id,
        run_dir=run_dir,
        model_id=model_id,
        display_name=model_display_name(model_id, run_id),
        predictions=read_jsonl(predictions_path),
        manifest=manifest,
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", value).strip("_")
    return slug or "item"


def _metrics_row(
    run: SourceRun,
    rule: str,
    metrics: dict[str, Any],
    subset: str,
    n_changed_from_flat: int,
) -> dict[str, Any]:
    return {
        "model": run.display_name,
        "run_id": run.run_id,
        "rule": rule,
        "rule_title": _RULE_TITLES[rule],
        "subset": subset,
        "n_examples": metrics["n_examples"],
        "accuracy": metrics["accuracy"],
        "macro_f1": metrics["macro_f1"],
        "weighted_f1": metrics["weighted_f1"],
        "mcc": metrics["mcc"],
        "n_changed_from_flat": n_changed_from_flat,
    }


def update_ablation_registry(
    registry_path: Path,
    config: dict[str, Any],
    best_row: dict[str, Any],
    report_dir: Path,
) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    experiment_id = str(config["experiment_id"])
    row = (
        f"| `{experiment_id}` | {config.get('stage', 'aggregation policy selection')} | "
        f"{config.get('status', 'exploratory ablation')} | "
        f"{best_row['model']} / {best_row['rule_title']} | "
        f"{fmt(best_row['macro_f1'])} | [{experiment_id}](../{report_dir.as_posix()}/README.md) |"
    )
    if registry_path.exists():
        lines = registry_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = [
            "# Experiment registry",
            "",
            "This file indexes reproducible experiments. Detailed reports live under `reports/experiments/`.",
            "",
            "| Experiment | Stage | Status | Best model | Macro-F1 | Report |",
            "|---|---|---|---|---:|---|",
        ]
    for index, line in enumerate(lines):
        if f"`{experiment_id}`" in line and line.lstrip().startswith("|"):
            lines[index] = row
            break
    else:
        lines.append(row)
    registry_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_aggregation_ablation(config_path: Path, project_root: Path) -> Path:
    config = read_json(config_path)
    experiment_id = str(config["experiment_id"])
    rules = list(config.get("rules", AGGREGATION_RULES))
    unknown_rules = set(rules) - set(AGGREGATION_RULES)
    if unknown_rules:
        raise ValueError(f"Unknown aggregation rules in config: {sorted(unknown_rules)}")
    if "flat" not in rules:
        raise ValueError("The ablation must include flat as the reference rule")

    runs_dir = str(config.get("runs_dir", "runs"))
    reports_root = project_root / str(config.get("reports_dir", "reports/experiments"))
    output_dir = reports_root / experiment_id
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    artifacts_dir = output_dir / "artifacts"
    for directory in (tables_dir, figures_dir, artifacts_dir):
        directory.mkdir(parents=True, exist_ok=True)

    source_runs = [load_source_run(project_root, runs_dir, run_id) for run_id in config["source_run_ids"]]
    policy_review_ids = {str(item) for item in config.get("policy_review_example_ids", [])}

    summary_rows: list[dict[str, Any]] = []
    class_rows: list[dict[str, Any]] = []
    change_rows: list[dict[str, Any]] = []
    statistical_rows: list[dict[str, Any]] = []
    all_results: dict[str, Any] = {}

    for run in source_runs:
        prediction_ids = [str(row["example_id"]) for row in run.predictions]
        if len(prediction_ids) != len(set(prediction_ids)):
            raise ValueError(f"Duplicate example_id values in {run.run_id}")

        per_rule_predictions: dict[str, list[dict[str, Any]]] = {}
        per_rule_metrics: dict[str, dict[str, Any]] = {}
        per_rule_clean_metrics: dict[str, dict[str, Any]] = {}

        for rule in rules:
            derived_rows: list[dict[str, Any]] = []
            for source in run.predictions:
                pred_label, sentence_groups = aggregate_prediction(source, rule)
                row = {
                    "example_id": source["example_id"],
                    "context_id": source.get("context_id"),
                    "domain": source.get("domain"),
                    "gold_label": source["gold_label"],
                    "pred_label": pred_label,
                    "is_correct": pred_label == source["gold_label"],
                    "rule": rule,
                    "claim": source.get("claim"),
                    "n_atoms": source.get("n_atoms", len(source.get("atoms") or [])),
                    "atom_labels": [atom["pred_label"] for atom in source.get("atoms") or []],
                    "sentence_groups": sentence_groups,
                    "policy_review": str(source["example_id"]) in policy_review_ids,
                }
                derived_rows.append(row)
            per_rule_predictions[rule] = derived_rows
            metrics = hard_label_metrics(
                [row["gold_label"] for row in derived_rows],
                [row["pred_label"] for row in derived_rows],
            )
            clean_rows = [row for row in derived_rows if not row["policy_review"]]
            clean_metrics = hard_label_metrics(
                [row["gold_label"] for row in clean_rows],
                [row["pred_label"] for row in clean_rows],
            )
            per_rule_metrics[rule] = metrics
            per_rule_clean_metrics[rule] = clean_metrics
            write_jsonl(artifacts_dir / f"predictions__{safe_slug(run.run_id)}__{rule}.jsonl", derived_rows)
            write_json(artifacts_dir / f"metrics__{safe_slug(run.run_id)}__{rule}.json", metrics)

        flat_labels = [row["pred_label"] for row in per_rule_predictions["flat"]]
        flat_correct = [row["is_correct"] for row in per_rule_predictions["flat"]]
        for rule in rules:
            current_rows = per_rule_predictions[rule]
            changed_count = sum(
                flat != current["pred_label"] for flat, current in zip(flat_labels, current_rows)
            )
            summary_rows.append(_metrics_row(run, rule, per_rule_metrics[rule], "all_200", changed_count))
            summary_rows.append(_metrics_row(run, rule, per_rule_clean_metrics[rule], "policy_clean", changed_count))

            report = per_rule_metrics[rule]["classification_report"]
            for label in CLAIM_LABELS:
                item = report[label]
                class_rows.append({
                    "model": run.display_name,
                    "run_id": run.run_id,
                    "rule": rule,
                    "label": label,
                    "precision": item["precision"],
                    "recall": item["recall"],
                    "f1_score": item["f1-score"],
                    "support": item["support"],
                })

            matrix = per_rule_metrics[rule]["confusion_matrix"]
            matrix_rows = []
            for gold_index, gold_label in enumerate(CLAIM_LABELS):
                matrix_rows.append({
                    "gold_label": gold_label,
                    **{
                        f"pred_{pred_label}": matrix[gold_index][pred_index]
                        for pred_index, pred_label in enumerate(CLAIM_LABELS)
                    },
                })
            file_stem = f"{safe_slug(run.run_id)}__{rule}"
            write_csv(
                tables_dir / f"confusion_matrix__{file_stem}.csv",
                ["gold_label", *[f"pred_{label}" for label in CLAIM_LABELS]],
                matrix_rows,
            )
            write_confusion_svg(
                figures_dir / f"confusion_matrix__{file_stem}.svg",
                f"{run.display_name} — {_RULE_TITLES[rule]}",
                list(CLAIM_LABELS),
                matrix,
            )

            if rule != "flat":
                current_correct = [row["is_correct"] for row in current_rows]
                test = exact_mcnemar(flat_correct, current_correct)
                statistical_rows.append({
                    "model": run.display_name,
                    "run_id": run.run_id,
                    "alternative_rule": rule,
                    **test,
                })
                for flat_row, alternative_row in zip(
                    per_rule_predictions["flat"], current_rows
                ):
                    if flat_row["pred_label"] == alternative_row["pred_label"]:
                        continue
                    if (not flat_row["is_correct"]) and alternative_row["is_correct"]:
                        effect = "corrected_by_alternative"
                    elif flat_row["is_correct"] and (not alternative_row["is_correct"]):
                        effect = "broken_by_alternative"
                    else:
                        effect = "changed_but_still_wrong"
                    change_rows.append({
                        "model": run.display_name,
                        "run_id": run.run_id,
                        "alternative_rule": rule,
                        "example_id": flat_row["example_id"],
                        "domain": flat_row.get("domain"),
                        "gold_label": flat_row["gold_label"],
                        "flat_pred": flat_row["pred_label"],
                        "alternative_pred": alternative_row["pred_label"],
                        "effect": effect,
                        "policy_review": flat_row["policy_review"],
                        "claim": flat_row.get("claim"),
                        "atom_labels": " | ".join(flat_row["atom_labels"]),
                    })

        all_results[run.run_id] = {
            "model": run.display_name,
            "model_id": run.model_id,
            "metrics": per_rule_metrics,
            "policy_clean_metrics": per_rule_clean_metrics,
        }

        # One comparison chart per model keeps all labels readable.
        write_grouped_bar_svg(
            figures_dir / f"aggregation_metrics__{safe_slug(run.run_id)}.svg",
            f"Aggregation ablation — {run.display_name}",
            [_RULE_TITLES[rule] for rule in rules],
            [
                ("Accuracy", [float(per_rule_metrics[rule]["accuracy"]) for rule in rules]),
                ("Macro-F1", [float(per_rule_metrics[rule]["macro_f1"]) for rule in rules]),
                ("MCC", [float(per_rule_metrics[rule]["mcc"]) for rule in rules]),
            ],
            y_max=1.0,
            y_label="Score",
        )

    write_csv(tables_dir / "aggregation_metrics.csv", list(summary_rows[0].keys()), summary_rows)
    write_csv(tables_dir / "class_metrics.csv", list(class_rows[0].keys()), class_rows)
    write_csv(
        tables_dir / "changed_predictions.csv",
        list(change_rows[0].keys()) if change_rows else [
            "model", "run_id", "alternative_rule", "example_id", "domain", "gold_label",
            "flat_pred", "alternative_pred", "effect", "policy_review", "claim", "atom_labels",
        ],
        change_rows,
    )
    write_csv(
        tables_dir / "mcnemar_tests.csv",
        list(statistical_rows[0].keys()) if statistical_rows else [
            "model", "run_id", "alternative_rule", "flat_only_correct",
            "alternative_only_correct", "discordant", "exact_p_value",
        ],
        statistical_rows,
    )

    best_row = max(
        (row for row in summary_rows if row["subset"] == "all_200"),
        key=lambda row: float(row["macro_f1"]),
    )
    flat_rows = {
        row["run_id"]: row
        for row in summary_rows
        if row["subset"] == "all_200" and row["rule"] == "flat"
    }

    report_table = []
    for row in summary_rows:
        if row["subset"] != "all_200":
            continue
        delta = float(row["macro_f1"]) - float(flat_rows[row["run_id"]]["macro_f1"])
        report_table.append([
            row["model"],
            row["rule_title"],
            fmt(row["accuracy"]),
            fmt(row["macro_f1"]),
            f"{delta:+.4f}",
            fmt(row["mcc"]),
            row["n_changed_from_flat"],
        ])

    sensitivity_table = []
    clean_lookup = {
        (row["run_id"], row["rule"]): row
        for row in summary_rows
        if row["subset"] == "policy_clean"
    }
    for row in summary_rows:
        if row["subset"] != "all_200":
            continue
        clean = clean_lookup[(row["run_id"], row["rule"])]
        sensitivity_table.append([
            row["model"],
            row["rule_title"],
            fmt(row["macro_f1"]),
            fmt(clean["macro_f1"]),
            f"{float(clean['macro_f1']) - float(row['macro_f1']):+.4f}",
        ])

    test_table = [[
        row["model"],
        _RULE_TITLES[row["alternative_rule"]],
        row["flat_only_correct"],
        row["alternative_only_correct"],
        row["discordant"],
        fmt(row["exact_p_value"]),
    ] for row in statistical_rows]

    notes = [str(item) for item in config.get("notes", [])]
    limitations = [str(item) for item in config.get("limitations", [])]
    next_steps = [str(item) for item in config.get("next_steps", [])]
    markdown = [
        f"# {config.get('title', experiment_id)}",
        "",
        f"**Experiment ID:** `{experiment_id}`  ",
        f"**Status:** {config.get('status', 'exploratory ablation')}  ",
        f"**Stage:** {config.get('stage', 'aggregation policy selection')}  ",
        "",
        "## Research question",
        "",
        str(config.get("research_question", "Not specified.")),
        "",
        "## Rules",
        "",
        "- **Flat:** all-entailment → supported; otherwise any entailment → partially_supported; otherwise any contradiction → contradicted; otherwise unverifiable.",
        "- **Contradiction-priority:** all-entailment → supported; otherwise any contradiction → contradicted; otherwise any entailment → partially_supported; otherwise unverifiable.",
        "- **Sentence-grouped:** atoms are automatically aligned to the claim sentence from which they were derived. Contradiction dominates within a sentence; sentence outcomes are then combined across the claim.",
        "",
        "No NLI inference was repeated. All rules reuse the frozen atom decisions from the v1.1 source runs.",
        "",
        "## Main results",
        "",
        markdown_table(
            ["Model", "Rule", "Accuracy", "Macro-F1", "Δ vs flat", "MCC", "Changed claims"],
            report_table,
        ),
        "",
        f"The highest exploratory Macro-F1 is **{fmt(best_row['macro_f1'])}** from **{best_row['model']} / {best_row['rule_title']}**.",
        "",
    ]
    for run in source_runs:
        markdown.extend([
            f"### {run.display_name}",
            "",
            f"![Aggregation comparison — {run.display_name}](figures/aggregation_metrics__{safe_slug(run.run_id)}.svg)",
            "",
        ])
    markdown.extend([
        "## Policy-review sensitivity",
        "",
        f"The two pre-identified policy-review examples are: {', '.join(f'`{item}`' for item in sorted(policy_review_ids)) or 'none'}.",
        "",
        markdown_table(
            ["Model", "Rule", "Macro-F1 all", "Macro-F1 excluding review", "Difference"],
            sensitivity_table,
        ),
        "",
        "## Paired tests against flat",
        "",
        markdown_table(
            ["Model", "Alternative", "Flat-only correct", "Alternative-only correct", "Discordant", "Exact p"],
            test_table,
        ),
        "",
        "McNemar tests are exploratory because the same pilot data informed the error analysis and policy hypotheses.",
        "",
        "## Interpretation",
        "",
        *([f"- {item}" for item in notes] or ["- No manual interpretation notes were supplied."]),
        "",
        "## Limitations",
        "",
        *([f"- {item}" for item in limitations] or ["- No limitations were supplied."]),
        "",
        "## Next steps",
        "",
        *([f"- {item}" for item in next_steps] or ["- No next steps were supplied."]),
        "",
        "## Reproducibility",
        "",
        "```powershell",
        f'C:\\Python314\\python.exe scripts\\55_run_aggregation_ablation.py --config "{config_path.as_posix().replace("/", "\\\\")}"',
        "```",
        "",
        "Source runs:",
        "",
        *[f"- `{run.run_dir.relative_to(project_root).as_posix()}`" for run in source_runs],
        "",
        "Generated artifacts:",
        "",
        "- `tables/aggregation_metrics.csv`",
        "- `tables/class_metrics.csv`",
        "- `tables/changed_predictions.csv`",
        "- `tables/mcnemar_tests.csv`",
        "- one confusion-matrix CSV and SVG per model/rule",
        "- one derived prediction JSONL and metrics JSON per model/rule",
        "- one aggregation-comparison SVG per model",
        "",
    ])
    (output_dir / "README.md").write_text("\n".join(markdown), encoding="utf-8")

    source_manifest = []
    for run in source_runs:
        source_manifest.append({
            "run_id": run.run_id,
            "model_id": run.model_id,
            "predictions_sha256": sha256_file(run.run_dir / "predictions.jsonl"),
            "manifest_sha256": sha256_file(run.run_dir / "manifest.json"),
            "metrics_sha256": sha256_file(run.run_dir / "metrics.json"),
        })
    report_manifest = {
        "experiment_id": experiment_id,
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "source_runs": source_manifest,
        "rules": rules,
        "policy_review_example_ids": sorted(policy_review_ids),
        "best_setting": best_row,
        "results": all_results,
    }
    write_json(output_dir / "report_manifest.json", report_manifest)
    update_ablation_registry(
        project_root / str(config.get("registry_path", "docs/EXPERIMENTS.md")),
        config,
        best_row,
        output_dir.relative_to(project_root),
    )
    return output_dir
