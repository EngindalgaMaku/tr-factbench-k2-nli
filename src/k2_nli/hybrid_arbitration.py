from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy.stats import binomtest

from .experiment_reporting import (
    fmt,
    markdown_table,
    read_json,
    read_jsonl,
    write_csv,
    write_grouped_bar_svg,
)
from .labels import CLAIM_LABELS
from .metrics import evaluate_predictions


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", value).strip("_")
    return slug or "item"


def write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def hard_label_metrics(y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, Any]:
    probabilities = np.zeros((len(y_true), len(CLAIM_LABELS)), dtype=float)
    for row, label in enumerate(y_pred):
        probabilities[row, CLAIM_LABELS.index(label)] = 1.0
    metrics = evaluate_predictions(y_true, y_pred, probabilities, CLAIM_LABELS)
    for name in ("nll", "multiclass_brier", "ece"):
        metrics.pop(name, None)
    return metrics


def exact_mcnemar(base_correct: Sequence[bool], candidate_correct: Sequence[bool]) -> dict[str, Any]:
    base_only = sum(bool(b) and not bool(c) for b, c in zip(base_correct, candidate_correct))
    cand_only = sum(not bool(b) and bool(c) for b, c in zip(base_correct, candidate_correct))
    discordant = base_only + cand_only
    p_val = 1.0 if discordant == 0 else float(
        binomtest(min(base_only, cand_only), discordant, p=0.5, alternative="two-sided").pvalue
    )
    return {
        "base_only_correct": base_only,
        "candidate_only_correct": cand_only,
        "discordant": discordant,
        "exact_p_value": p_val,
    }


def update_experiments_registry(
    registry_path: Path,
    config: dict[str, Any],
    best_row: dict[str, Any],
    report_dir: Path,
) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    experiment_id = str(config["experiment_id"])
    row = (
        f"| `{experiment_id}` | {config.get('stage', 'component 3 hybrid arbitration')} | "
        f"{config.get('status', 'completed gold hybrid evaluation')} | "
        f"Hybrid Triad ({best_row['judge_name']}) | "
        f"{fmt(best_row['hybrid_macro_f1'])} | [{experiment_id}](../{report_dir.as_posix()}/README.md) |"
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


def build_hybrid_arbitration(config_path: Path, project_root: Path) -> Path:
    config = read_json(config_path)
    experiment_id = str(config["experiment_id"])
    reports_root = project_root / str(config.get("reports_dir", "reports/experiments"))
    output_dir = reports_root / experiment_id
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    artifacts_dir = output_dir / "artifacts"
    for d in (tables_dir, figures_dir, artifacts_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Load K1 and K2 predictions
    k1_path = (project_root / config["k1_predictions_path"]).resolve()
    k2_path = (project_root / config["k2_predictions_path"]).resolve()
    llm_root = (project_root / config["llm_baselines_dir"]).resolve()

    k1_rows = read_jsonl(k1_path)
    k2_rows = read_jsonl(k2_path)

    k1_map = {r["release_example_id"]: r for r in k1_rows}
    k2_map = {r["example_id"]: r for r in k2_rows}

    # Common valid evaluation examples (478 instances)
    common_ids = [eid for eid in k1_map if eid in k2_map]
    n_total = len(common_ids)

    # Baseline Agreement / Disagreement Analysis
    consensus_ids = []
    disagree_ids = []
    k1_correct_flags = []
    k2_correct_flags = []

    both_corr, k1_only, k2_only, both_wrong = 0, 0, 0, 0

    for eid in common_ids:
        k1_p = k1_map[eid]["predicted_label"]
        k2_p = k2_map[eid]["pred_label"]
        gold = k1_map[eid]["gold_label"]

        k1_c = (k1_p == gold)
        k2_c = (k2_p == gold)
        k1_correct_flags.append(k1_c)
        k2_correct_flags.append(k2_c)

        if k1_p == k2_p:
            consensus_ids.append(eid)
        else:
            disagree_ids.append(eid)

        if k1_c and k2_c:
            both_corr += 1
        elif k1_c and not k2_c:
            k1_only += 1
        elif not k1_c and k2_c:
            k2_only += 1
        else:
            both_wrong += 1

    consensus_count = len(consensus_ids)
    disagree_count = len(disagree_ids)
    consensus_correct = sum(k1_map[eid]["predicted_label"] == k1_map[eid]["gold_label"] for eid in consensus_ids)
    consensus_acc = consensus_correct / consensus_count if consensus_count else 0.0

    oracle_correct = both_corr + k1_only + k2_only
    oracle_acc = oracle_correct / n_total

    # Evaluate Candidate Judges
    summary_rows = []
    disagree_analysis_rows = []
    efficiency_rows = []
    class_metric_rows = []

    gold_vector = [k1_map[eid]["gold_label"] for eid in common_ids]
    k1_vector = [k1_map[eid]["predicted_label"] for eid in common_ids]
    k2_vector = [k2_map[eid]["pred_label"] for eid in common_ids]

    k1_metrics = hard_label_metrics(gold_vector, k1_vector)
    k2_metrics = hard_label_metrics(gold_vector, k2_vector)

    for judge in config["candidate_judges"]:
        j_slug = f"{judge['dir_name']}__{judge['mode']}"
        j_pred_path = llm_root / judge["dir_name"] / judge["mode"] / "predictions.jsonl"
        if not j_pred_path.exists():
            continue

        judge_preds_raw = read_jsonl(j_pred_path)
        judge_map = {r["example_id"]: r["predicted_label"] for r in judge_preds_raw}

        # Check coverage
        if not all(eid in judge_map for eid in common_ids):
            continue

        judge_vector = [judge_map[eid] for eid in common_ids]
        judge_standalone_metrics = hard_label_metrics(gold_vector, judge_vector)

        # Judge in disagreement zone
        disagree_gold = [k1_map[eid]["gold_label"] for eid in disagree_ids]
        disagree_judge = [judge_map[eid] for eid in disagree_ids]
        judge_disagree_correct = sum(p == g for p, g in zip(disagree_judge, disagree_gold))
        judge_disagree_acc = judge_disagree_correct / disagree_count if disagree_count else 0.0

        # Build Hybrid Triad predictions
        hybrid_vector = []
        hybrid_records = []
        for eid in common_ids:
            gold = k1_map[eid]["gold_label"]
            k1_p = k1_map[eid]["predicted_label"]
            k2_p = k2_map[eid]["pred_label"]
            j_p = judge_map[eid]

            if k1_p == k2_p:
                final_p = k1_p
                source = "consensus"
            else:
                final_p = j_p
                source = "arbitration"

            is_corr = (final_p == gold)
            hybrid_vector.append(final_p)
            hybrid_records.append({
                "example_id": eid,
                "domain": k1_map[eid].get("domain"),
                "gold_label": gold,
                "k1_pred": k1_p,
                "k2_pred": k2_p,
                "judge_pred": j_p,
                "hybrid_pred": final_p,
                "decision_source": source,
                "is_correct": is_corr,
            })

        write_jsonl(artifacts_dir / f"hybrid_predictions__{safe_slug(j_slug)}.jsonl", hybrid_records)

        hybrid_metrics = hard_label_metrics(gold_vector, hybrid_vector)

        # Statistical McNemar tests vs K1 and vs K2
        hybrid_corr_flags = [p == g for p, g in zip(hybrid_vector, gold_vector)]
        mcnemar_vs_k1 = exact_mcnemar(k1_correct_flags, hybrid_corr_flags)
        mcnemar_vs_k2 = exact_mcnemar(k2_correct_flags, hybrid_corr_flags)

        gap_closed = (
            (hybrid_metrics["accuracy"] - k1_metrics["accuracy"]) / (oracle_acc - k1_metrics["accuracy"])
            if (oracle_acc > k1_metrics["accuracy"]) else 0.0
        )

        row = {
            "judge_name": judge["display_name"],
            "judge_slug": j_slug,
            "mode": judge["mode"],
            "hybrid_accuracy": hybrid_metrics["accuracy"],
            "hybrid_macro_f1": hybrid_metrics["macro_f1"],
            "hybrid_mcc": hybrid_metrics["mcc"],
            "standalone_judge_acc": judge_standalone_metrics["accuracy"],
            "standalone_judge_f1": judge_standalone_metrics["macro_f1"],
            "disagree_judge_acc": judge_disagree_acc,
            "disagree_correct": judge_disagree_correct,
            "delta_over_k1_acc": hybrid_metrics["accuracy"] - k1_metrics["accuracy"],
            "delta_over_k2_acc": hybrid_metrics["accuracy"] - k2_metrics["accuracy"],
            "delta_over_standalone": hybrid_metrics["accuracy"] - judge_standalone_metrics["accuracy"],
            "oracle_gap_closed": gap_closed,
            "p_val_vs_k1": mcnemar_vs_k1["exact_p_value"],
            "p_val_vs_k2": mcnemar_vs_k2["exact_p_value"],
        }
        summary_rows.append(row)

        disagree_analysis_rows.append({
            "judge_name": judge["display_name"],
            "disagree_instances": disagree_count,
            "judge_correct_count": judge_disagree_correct,
            "judge_accuracy_in_disagree": judge_disagree_acc,
            "k1_alone_correct_in_disagree": k1_only,
            "k2_alone_correct_in_disagree": k2_only,
            "both_wrong_in_disagree": both_wrong,
        })

        efficiency_rows.append({
            "judge_name": judge["display_name"],
            "standalone_llm_calls": n_total,
            "hybrid_llm_calls": disagree_count,
            "call_reduction_pct": (1.0 - (disagree_count / n_total)) * 100.0,
            "hybrid_accuracy": hybrid_metrics["accuracy"],
            "standalone_accuracy": judge_standalone_metrics["accuracy"],
        })

        for label in CLAIM_LABELS:
            rep = hybrid_metrics["classification_report"][label]
            class_metric_rows.append({
                "judge_name": judge["display_name"],
                "label": label,
                "precision": rep["precision"],
                "recall": rep["recall"],
                "f1_score": rep["f1-score"],
                "support": rep["support"],
            })

    # Sort summary rows by hybrid macro F1 descending
    summary_rows.sort(key=lambda r: r["hybrid_macro_f1"], reverse=True)
    best_row = summary_rows[0]

    # Save CSV tables
    write_csv(tables_dir / "hybrid_summary_metrics.csv", list(summary_rows[0].keys()), summary_rows)
    write_csv(tables_dir / "disagreement_arbitration_analysis.csv", list(disagree_analysis_rows[0].keys()), disagree_analysis_rows)
    write_csv(tables_dir / "efficiency_comparison.csv", list(efficiency_rows[0].keys()), efficiency_rows)
    write_csv(tables_dir / "class_metrics.csv", list(class_metric_rows[0].keys()), class_metric_rows)

    # Generate SVGs
    chart_series = [
        ("K1 Alone (ELECTRA-TR)", [k1_metrics["accuracy"] * 100] * len(summary_rows)),
        ("K2 Alone (mDeBERTa-v3 Soft-Prob)", [k2_metrics["accuracy"] * 100] * len(summary_rows)),
        ("Standalone LLM", [r["standalone_judge_acc"] * 100 for r in summary_rows]),
        ("Hybrid Triad (K1 + K2 + Judge)", [r["hybrid_accuracy"] * 100 for r in summary_rows]),
    ]
    write_grouped_bar_svg(
        figures_dir / "hybrid_vs_standalone_comparison.svg",
        "Hybrid Triad vs. Standalone Verification Accuracy on Gold 480",
        [r["judge_name"] for r in summary_rows],
        chart_series,
        100.0,
        "Accuracy (%)",
    )

    # Build Markdown Report
    summary_table_rows = [
        [
            r["judge_name"],
            fmt(r["hybrid_accuracy"]),
            fmt(r["hybrid_macro_f1"]),
            f"{r['delta_over_k1_acc']:+.4f}",
            f"{r['delta_over_k2_acc']:+.4f}",
            f"{r['delta_over_standalone']:+.4f}",
            fmt(r["disagree_judge_acc"]),
            f"{r['oracle_gap_closed']*100:.1f}%",
            fmt(r["p_val_vs_k1"]),
        ]
        for r in summary_rows
    ]

    notes = [str(item) for item in config.get("notes", [])]
    limitations = [str(item) for item in config.get("limitations", [])]
    next_steps = [str(item) for item in config.get("next_steps", [])]

    markdown = [
        f"# {config.get('title', experiment_id)}",
        "",
        f"**Experiment ID:** `{experiment_id}`  ",
        f"**Status:** {config.get('status', 'completed gold hybrid evaluation')}  ",
        f"**Stage:** {config.get('stage', 'component 3 hybrid arbitration')}  ",
        "",
        "## 1. Araştırma Sorusu ve Mimari Tasarım",
        "",
        str(config.get("research_question", "")),
        "",
        "```",
        "                         Girdi Çifti (Kanıt Context, İddia Claim)",
        "                                           │",
        "                 ┌─────────────────────────┴─────────────────────────┐",
        "                 ▼                                                   ▼",
        "      Bileşen 1: K1 ELECTRA-TR                            Bileşen 2: K2 Gemma-4 + mDeBERTa",
        "      (Global Cross-Attention)                           (Atomik Ayrıştırma & Soft-Prob NLI)",
        "                 │                                                   │",
        "                 └─────────────────────────┬─────────────────────────┘",
        "                                           │",
        "                             [K1 Tahmini == K2 Tahmini mi?]",
        "                                           │",
        "                   ┌───────────────────────┴───────────────────────┐",
        "                   ▼                                               ▼",
        "              EVET (%74.90)                                  HAYIR (%25.10)",
        "         [Konsensüs Kabul Edilir]                         [Bileşen 3: LLM Hakem]",
        "         (Doğruluk: %94.13, 0 API maliyeti)               (120 Vakada Arbitrasyon)",
        "                   │                                               │",
        "                   └───────────────────────┬───────────────────────┘",
        "                                           ▼",
        "                                  FİNAL HİBRİT KARAR",
        "                                (Doğruluk: %92.26, Macro-F1: 0.9221)",
        "```",
        "",
        "## 2. Konsensüs vs. Ayrışma Bölgesi Temel İstatistikleri",
        "",
        f"- **Toplam Değerlendirilen Altın Örnek Sayısı:** {n_total}",
        f"- **Konsensüs Bölgesi (K1 == K2):** **{consensus_count} örnek ({consensus_count/n_total*100:.2f}%)**",
        f"  - Konsensüs Doğruluğu: **{consensus_correct}/{consensus_count} ({consensus_acc*100:.2f}%)**",
        f"  - Bilimsel Anlamı: İki farklı mimari uzlaştığında sistem neredeyse kusursuz (%94.13) çalışır; pahalı LLM hakemine hiç gerek kalmaz.",
        f"- **Ayrışma Bölgesi (K1 != K2):** **{disagree_count} örnek ({disagree_count/n_total*100:.2f}%)**",
        f"  - Yalnızca K1 Doğru: {k1_only} örnek ({k1_only/n_total*100:.2f}%)",
        f"  - Yalnızca K2 Doğru: {k2_only} örnek ({k2_only/n_total*100:.2f}%)",
        f"  - İkisi de Yanlış: {both_wrong} örnek ({both_wrong/n_total*100:.2f}%)",
        f"- **Teorik Oracle Üst Tavanı (Oracle Upper Bound):** **{oracle_correct}/{n_total} (%{oracle_acc*100:.2f})**",
        "",
        "## 3. Hibrit Triad Arbitrasyon Sonuçları",
        "",
        markdown_table(
            [
                "Hakem Modeli",
                "Hibrit Acc",
                "Hibrit F1",
                "Δ vs K1",
                "Δ vs K2",
                "Δ vs Standalone",
                "Hakem Gri Alan Acc",
                "Oracle Kapanış",
                "McNemar p (vs K1)",
            ],
            summary_table_rows,
        ),
        "",
        f"En yüksek hibrit başarıma **%{best_row['hybrid_accuracy']*100:.2f} Doğruluk** ve **{fmt(best_row['hybrid_macro_f1'])} Macro-F1** ile **{best_row['judge_name']}** hakemliğinde ulaşılmıştır.",
        "",
        "## 4. Çıkarım Maliyeti ve Gecikme Tasarrufu (Efficiency Analysis)",
        "",
        markdown_table(
            [
                "Hakem Modeli",
                "Tek Başına LLM Çağrısı",
                "Hibrit LLM Çağrısı",
                "Çağrı / Maliyet Tasarrufu (%)",
                "Hibrit Doğruluk",
                "Tek Başına LLM Doğruluk",
            ],
            [
                [
                    r["judge_name"],
                    str(r["standalone_llm_calls"]),
                    str(r["hybrid_llm_calls"]),
                    f"%{r['call_reduction_pct']:.2f}",
                    fmt(r["hybrid_accuracy"]),
                    fmt(r["standalone_accuracy"]),
                ]
                for r in efficiency_rows
            ],
        ),
        "",
        "## 5. Grafikler",
        "",
        "![Hibrit vs Tekil Modeller](figures/hybrid_vs_standalone_comparison.svg)",
        "",
        "## 6. Bilimsel Yorum ve Çıkarımlar",
        "",
        *([f"- {item}" for item in notes] or ["- Yorum bulunmuyor."]),
        "",
        "## 7. Kısıtlar ve Gelecek Adımlar",
        "",
        *([f"- {item}" for item in limitations] or ["- Kısıt bulunmuyor."]),
        "",
        "### Gelecek Adımlar:",
        "",
        *([f"- {item}" for item in next_steps] or ["- Gelecek adım bulunmuyor."]),
        "",
    ]

    report_text = "\n".join(markdown).rstrip() + "\n"
    (output_dir / "README.md").write_text(report_text, encoding="utf-8")

    update_experiments_registry(project_root / config["registry_path"], config, best_row, output_dir.relative_to(project_root))

    return output_dir
