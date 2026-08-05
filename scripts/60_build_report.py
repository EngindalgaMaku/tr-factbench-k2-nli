#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from k2_nli.io import read_jsonl


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value)


def save_confusion_matrix(matrix: np.ndarray, labels: list[str], title: str, path: Path) -> None:
    plt.figure(figsize=(6, 5))
    plt.imshow(matrix, interpolation="nearest")
    plt.title(title)
    plt.xticks(np.arange(len(labels)), labels, rotation=30, ha="right")
    plt.yticks(np.arange(len(labels)), labels)
    plt.xlabel("Tahmin")
    plt.ylabel("Gold")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            plt.text(column, row, str(int(matrix[row, column])), ha="center", va="center")
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()


def save_reliability(frame: pd.DataFrame, path: Path, bins: int = 10) -> None:
    edges = np.linspace(0.0, 1.0, bins + 1)
    confidence = frame["confidence"].to_numpy()
    correct = (frame["gold_label"] == frame["pred_label"]).astype(float).to_numpy()
    x_values = []
    y_values = []
    counts = []
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (confidence > low) & (confidence <= high)
        if not mask.any():
            continue
        x_values.append(float(confidence[mask].mean()))
        y_values.append(float(correct[mask].mean()))
        counts.append(int(mask.sum()))
    plt.figure(figsize=(6, 5))
    plt.plot([0, 1], [0, 1], linestyle="--")
    if x_values:
        plt.plot(x_values, y_values, marker="o")
        for x_value, y_value, count in zip(x_values, y_values, counts):
            plt.annotate(str(count), (x_value, y_value), xytext=(4, 4), textcoords="offset points", fontsize=8)
    plt.xlabel("Ortalama güven")
    plt.ylabel("Gözlenen doğruluk")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()
    output = Path(args.output_dir)
    figures = output / "figures"
    tables = output / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    class_rows = []
    domain_rows = []
    truncation_rows = []
    error_frames = []
    run_frames: dict[str, pd.DataFrame] = {}
    run_labels: dict[str, list[str]] = {}

    for run_path in args.runs:
        path = Path(run_path)
        run_name = path.name
        metrics = json.loads((path / "metrics.json").read_text(encoding="utf-8"))
        predictions = pd.DataFrame(read_jsonl(path / "predictions.jsonl"))
        run_frames[run_name] = predictions
        labels = list(metrics["labels"])
        run_labels[run_name] = labels
        metadata = metrics.get("model_metadata", {})
        summary_rows.append({
            "run": run_name,
            "n_examples": metrics["n_examples"],
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "weighted_f1": metrics["weighted_f1"],
            "mcc": metrics["mcc"],
            "nll": metrics.get("nll"),
            "brier": metrics.get("multiclass_brier"),
            "ece": metrics.get("ece"),
            "pairs_per_second": metadata.get("pairs_per_second"),
            "peak_gpu_memory_bytes": metadata.get("peak_gpu_memory_bytes"),
            "n_truncated_pairs": metadata.get("n_truncated_pairs"),
        })
        report = metrics["classification_report"]
        for label in labels:
            values = report[label]
            class_rows.append({
                "run": run_name,
                "label": label,
                "precision": values["precision"],
                "recall": values["recall"],
                "f1": values["f1-score"],
                "support": values["support"],
            })
        for domain, group in predictions.groupby("domain"):
            domain_rows.append({
                "run": run_name,
                "domain": domain,
                "n_examples": len(group),
                "accuracy": accuracy_score(group["gold_label"], group["pred_label"]),
                "macro_f1": f1_score(
                    group["gold_label"], group["pred_label"], labels=labels,
                    average="macro", zero_division=0,
                ),
            })
        if "was_truncated" in predictions.columns:
            for truncated, group in predictions.groupby("was_truncated"):
                truncation_rows.append({
                    "run": run_name,
                    "was_truncated": bool(truncated),
                    "n_examples": len(group),
                    "accuracy": accuracy_score(group["gold_label"], group["pred_label"]),
                    "macro_f1": f1_score(
                        group["gold_label"], group["pred_label"], labels=labels,
                        average="macro", zero_division=0,
                    ),
                })
        errors = predictions[predictions["gold_label"] != predictions["pred_label"]].copy()
        if not errors.empty:
            errors.insert(0, "run", run_name)
            error_frames.append(errors)

        matrix = confusion_matrix(predictions["gold_label"], predictions["pred_label"], labels=labels)
        save_confusion_matrix(
            matrix, labels, f"Confusion Matrix — {run_name}",
            figures / f"confusion_matrix__{safe_name(run_name)}.png",
        )
        if {"confidence", "gold_label", "pred_label"}.issubset(predictions.columns):
            save_reliability(predictions, figures / f"reliability__{safe_name(run_name)}.png")
            correct = predictions[predictions["gold_label"] == predictions["pred_label"]]["confidence"]
            wrong = predictions[predictions["gold_label"] != predictions["pred_label"]]["confidence"]
            plt.figure(figsize=(7, 5))
            plt.hist(correct, bins=20, alpha=0.6, label="doğru")
            plt.hist(wrong, bins=20, alpha=0.6, label="yanlış")
            plt.xlabel("Güven")
            plt.ylabel("Örnek sayısı")
            plt.legend()
            plt.tight_layout()
            plt.savefig(figures / f"confidence_hist__{safe_name(run_name)}.png", dpi=220)
            plt.close()
        if "pair_tokens_untruncated" in predictions.columns:
            token_frame = predictions.copy()
            token_frame["token_bin"] = pd.cut(
                token_frame["pair_tokens_untruncated"],
                bins=[0, 128, 256, 384, 512, 768, 1024, np.inf],
                right=True,
            )
            rows = []
            for token_bin, group in token_frame.groupby("token_bin", observed=True):
                rows.append({
                    "token_bin": str(token_bin),
                    "accuracy": accuracy_score(group["gold_label"], group["pred_label"]),
                    "n": len(group),
                })
            token_summary = pd.DataFrame(rows)
            token_summary.to_csv(tables / f"token_accuracy__{safe_name(run_name)}.csv", index=False)
            if not token_summary.empty:
                plt.figure(figsize=(8, 5))
                positions = np.arange(len(token_summary))
                plt.bar(positions, token_summary["accuracy"])
                plt.xticks(positions, token_summary["token_bin"], rotation=30, ha="right")
                plt.ylim(0, 1)
                plt.ylabel("Accuracy")
                plt.xlabel("Truncation öncesi pair token aralığı")
                plt.tight_layout()
                plt.savefig(figures / f"token_accuracy__{safe_name(run_name)}.png", dpi=220)
                plt.close()

    summary = pd.DataFrame(summary_rows).sort_values("macro_f1", ascending=False)
    class_metrics = pd.DataFrame(class_rows)
    domain_metrics = pd.DataFrame(domain_rows)
    truncation_metrics = pd.DataFrame(truncation_rows)
    summary.to_csv(tables / "run_summary.csv", index=False)
    class_metrics.to_csv(tables / "class_metrics.csv", index=False)
    domain_metrics.to_csv(tables / "domain_metrics.csv", index=False)
    if not truncation_metrics.empty:
        truncation_metrics.to_csv(tables / "truncation_metrics.csv", index=False)
    if error_frames:
        pd.concat(error_frames, ignore_index=True).to_csv(tables / "all_errors.csv", index=False)

    plt.figure(figsize=(max(7, len(summary) * 1.4), 5))
    positions = np.arange(len(summary))
    plt.bar(positions, summary["macro_f1"])
    plt.xticks(positions, summary["run"], rotation=30, ha="right")
    plt.ylabel("Macro-F1")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(figures / "macro_f1_by_run.png", dpi=220)
    plt.close()

    if not class_metrics.empty:
        pivot = class_metrics.pivot(index="label", columns="run", values="f1")
        pivot.plot(kind="bar", figsize=(10, 5))
        plt.ylabel("F1")
        plt.ylim(0, 1)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(figures / "class_f1_by_run.png", dpi=220)
        plt.close()

    if not domain_metrics.empty:
        pivot = domain_metrics.pivot(index="domain", columns="run", values="macro_f1")
        plt.figure(figsize=(max(7, 1.4 * len(pivot.columns)), 4.5))
        plt.imshow(pivot.to_numpy(), aspect="auto", vmin=0, vmax=1)
        plt.xticks(np.arange(len(pivot.columns)), pivot.columns, rotation=30, ha="right")
        plt.yticks(np.arange(len(pivot.index)), pivot.index)
        for row in range(pivot.shape[0]):
            for column in range(pivot.shape[1]):
                plt.text(column, row, f"{pivot.iloc[row, column]:.3f}", ha="center", va="center")
        plt.colorbar(label="Macro-F1")
        plt.tight_layout()
        plt.savefig(figures / "domain_macro_f1_heatmap.png", dpi=220)
        plt.close()

    report_lines = [
        "# K2 Deney Özeti",
        "",
        "## Genel sonuçlar",
        "",
        summary.to_markdown(index=False),
        "",
        "## Sınıf bazlı sonuçlar",
        "",
        class_metrics.to_markdown(index=False),
        "",
        "## Domain bazlı sonuçlar",
        "",
        domain_metrics.to_markdown(index=False),
        "",
    ]
    if not truncation_metrics.empty:
        report_lines.extend([
            "## Truncation alt grupları",
            "",
            truncation_metrics.to_markdown(index=False),
            "",
        ])
    (output / "experiment_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report written to {output / 'experiment_report.md'}")


if __name__ == "__main__":
    main()
