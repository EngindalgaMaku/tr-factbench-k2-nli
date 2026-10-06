#!/usr/bin/env python3
"""
77_gold480_annotator_robustness.py
Scores every system on Gold-480 against three references:
  (1) gold v1.0 (= Annotator A after adjudication),
  (2) Annotator B raw labels,
  (3) the 432 examples where A and B agreed before adjudication.
Tests whether the A-favoured adjudication changes any conclusion.

Output: reports/GOLD480_ANNOTATOR_ROBUSTNESS.md
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score

LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = ROOT.parent / "tr-factbench-v0.1.0-preview" / "data" / "evaluation" / "gold_v1.0"
EXP = ROOT / "reports" / "experiments"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def eid(rec: dict) -> str:
    return rec.get("release_example_id") or rec["example_id"]


def main() -> None:
    aligned = list(csv.DictReader((GOLD_DIR / "agreement" / "AB_ALIGNED_480_v1.0.csv").open(encoding="utf-8-sig")))
    ids = [r["release_example_id"] for r in aligned]
    ref_a = {r["release_example_id"]: r["A_label"] for r in aligned}
    ref_b = {r["release_example_id"]: r["B_label"] for r in aligned}
    gold = {eid(r): r["gold_label"] for r in read_jsonl(GOLD_DIR / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")}
    assert all(gold[i] == ref_a[i] for i in ids), "gold v1.0 is expected to equal Annotator A"
    agreed = [i for i in ids if ref_a[i] == ref_b[i]]

    k1 = {eid(r): r["predicted_label"] for r in read_jsonl(GOLD_DIR / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")}
    k2 = {eid(r): r["pred_label"] for r in read_jsonl(
        EXP / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
        / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")}
    v4 = {r["example_id"]: r["judge_decision"] for r in read_jsonl(
        EXP / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")}
    blind_dir = EXP / "K3-HYBRID-ARBITRATION-GOLD480-v1" / "artifacts"
    gemma = {r["example_id"]: r for r in read_jsonl(blind_dir / "hybrid_predictions__google_gemma-4-26b-a4b-it__zero_shot.jsonl")}
    gpt = {r["example_id"]: r for r in read_jsonl(blind_dir / "hybrid_predictions__openai_gpt-4.1-mini__few_shot_8.jsonl")}

    systems = {
        "K1 (ELECTRA-TR)": k1,
        "K2 (Gemma atomizer + mDeBERTa, soft-prob)": k2,
        "Hybrid + Llama-3.3-70B V4 (prompt tuned on gold)": {i: k1[i] if k1[i] == k2[i] else v4[i] for i in ids},
        "Hybrid + Gemma-4-26B blind zero-shot": {i: gemma[i]["hybrid_pred"] for i in ids},
        "Standalone GPT-4.1-mini 8-shot": {i: gpt[i]["judge_pred"] for i in ids},
        "Standalone Gemma-4-26B zero-shot": {i: gemma[i]["judge_pred"] for i in ids},
    }
    refs = [("Gold v1.0 (= A)", ref_a, ids), ("Annotator B", ref_b, ids), ("A = B agreed subset", ref_a, agreed)]

    lines = [
        "# Gold-480 anotatör sağlamlık analizi",
        "",
        "Gold v1.0 etiketleri 48/48 uyuşmazlıkta Annotator A lehine çözülmüştür (A = veri setini oluşturan araştırmacı;",
        "bkz. `gold_v1.0/provenance/ANNOTATOR_ROLES_ERRATUM_TR_v1.0.1.md`). Bu tablo, sonuçların bu uzlaşmaya bağlı olup",
        "olmadığını sınamak için tüm sistemleri üç referansa göre puanlar.",
        "",
        f"Üretim: `python scripts/77_gold480_annotator_robustness.py` · uzlaşılan alt küme n = {len(agreed)}",
        "",
        "| Sistem | " + " | ".join(f"{name} Acc | {name} Macro-F1" for name, _, _ in refs) + " |",
        "|---|" + "---:|---:|" * len(refs),
    ]
    for name, pred in systems.items():
        cells = []
        for _, ref, subset in refs:
            y = [ref[i] for i in subset]
            p = [pred[i] for i in subset]
            cells += [f"{accuracy_score(y, p):.4f}", f"{f1_score(y, p, labels=LABELS, average='macro', zero_division=0):.4f}"]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Yorum: Üç referansta da K1 > K2 sıralaması ve hibrit sistemlerin K1/K2'den üstünlüğü korunur.",
        "Hibrit ile tek başına güçlü LLM arasındaki sıra referansa göre değişebilir (B'ye göre GPT-4.1-mini >",
        "kör Gemma hibriti); bu farklar Gold-480'de zaten istatistiksel olarak anlamlı değildir.",
        "",
        "Not: V4 hakem istemi Gold-480 uyuşmazlıkları üzerinde geliştirildiği için held-out sonuç değildir.",
        "",
    ]
    out = ROOT / "reports" / "GOLD480_ANNOTATOR_ROBUSTNESS.md"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
