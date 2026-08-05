#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from k2_nli.io import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--general", default="data/reviewed/claim_level/dev_general.jsonl")
    parser.add_argument("--stress", default="data/reviewed/claim_level/dev_stress.jsonl")
    parser.add_argument("--split-manifest", default="data/processed/split_manifest.json")
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()

    output = Path(args.output_dir)
    figures = output / "figures"
    tables = output / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    frames = []
    for name, path in (("dev_general", args.general), ("dev_stress", args.stress)):
        frame = pd.DataFrame(read_jsonl(path))
        frame["dataset"] = name
        frame["context_chars"] = frame["context"].str.len()
        frame["claim_chars"] = frame["claim"].str.len()
        frame["question_chars"] = frame["question"].str.len()
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)

    label_table = pd.crosstab(data["dataset"], data["gold_label"])
    label_table.to_csv(tables / "dataset_label_counts.csv")
    domain_table = pd.crosstab(data["dataset"], data["domain"])
    domain_table.to_csv(tables / "dataset_domain_counts.csv")
    length_table = data.groupby("dataset")[["context_chars", "claim_chars", "question_chars"]].describe()
    length_table.to_csv(tables / "dataset_length_summary.csv")

    labels = ["supported", "partially_supported", "contradicted", "unverifiable"]
    x = np.arange(len(labels))
    width = 0.36
    plt.figure(figsize=(9, 5))
    for index, dataset in enumerate(["dev_general", "dev_stress"]):
        counts = [int(label_table.loc[dataset].get(label, 0)) for label in labels]
        plt.bar(x + (index - 0.5) * width, counts, width=width, label=dataset)
    plt.xticks(x, labels, rotation=20, ha="right")
    plt.ylabel("Örnek sayısı")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "label_distribution.png", dpi=220)
    plt.close()

    domains = ["medical", "finance", "legal"]
    x = np.arange(len(domains))
    plt.figure(figsize=(8, 5))
    for index, dataset in enumerate(["dev_general", "dev_stress"]):
        counts = [int(domain_table.loc[dataset].get(domain, 0)) for domain in domains]
        plt.bar(x + (index - 0.5) * width, counts, width=width, label=dataset)
    plt.xticks(x, domains)
    plt.ylabel("Örnek sayısı")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "domain_distribution.png", dpi=220)
    plt.close()

    plt.figure(figsize=(8, 5))
    values = [
        data.loc[data["dataset"] == "dev_general", "context_chars"],
        data.loc[data["dataset"] == "dev_stress", "context_chars"],
    ]
    plt.boxplot(values, tick_labels=["dev_general", "dev_stress"], showfliers=False)
    plt.ylabel("Bağlam uzunluğu (karakter)")
    plt.tight_layout()
    plt.savefig(figures / "context_length_boxplot.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5))
    positions = []
    values = []
    labels_out = []
    pos = 1
    for dataset in ["dev_general", "dev_stress"]:
        for label in labels:
            values.append(data.loc[(data["dataset"] == dataset) & (data["gold_label"] == label), "claim_chars"])
            positions.append(pos)
            labels_out.append(f"{dataset}\n{label}")
            pos += 1
        pos += 1
    plt.boxplot(values, positions=positions, showfliers=False)
    plt.xticks(positions, labels_out, rotation=35, ha="right", fontsize=8)
    plt.ylabel("Claim uzunluğu (karakter)")
    plt.tight_layout()
    plt.savefig(figures / "claim_length_by_label.png", dpi=220)
    plt.close()

    annotation_table = pd.crosstab(data["dataset"], data["annotation_status"])
    annotation_table.to_csv(tables / "annotation_status_counts.csv")

    report = [
        "# Veri Profili",
        "",
        "## Etiket dağılımı",
        "",
        label_table.to_markdown(),
        "",
        "## Domain dağılımı",
        "",
        domain_table.to_markdown(),
        "",
        "## Annotation durumu",
        "",
        annotation_table.to_markdown(),
        "",
        "Grafikler `reports/figures/` altında üretilmiştir.",
    ]
    (output / "data_profile.md").write_text("\n".join(report), encoding="utf-8")
    print(output / "data_profile.md")


if __name__ == "__main__":
    main()
