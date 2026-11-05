#!/usr/bin/env python3
"""
120_ragbench_systems_results.py
Builds the hybrid systems for the Turkish RAGBench medical slice with the frozen AP6 v1
rules (scripts/88) and scores every system against the RAGBench silver labels (K-018).

  P0: K1 == K2 -> shared label; K1 != K2 -> V4 judge (Llama-3.3-70B); no K2 -> K1
  PA: P0, but where routing ended in consensus on partially_supported / contradicted,
      the blind Gemma-26B zero-shot label is used instead

Scoring is binary (supported vs unsupported; any non-"supported" 4-class label counts as
unsupported), metrics are for the unsupported class. 95% intervals come from a cluster
bootstrap over questions (74 clusters, 10,000 resamples, seed 42), as in scripts/119.
K1 is additionally reported on truncated / non-truncated inputs (researcher decision, K-018).

Output: data/ragbench/medical/build/predictions/system_predictions.jsonl
        data/ragbench/medical/build/systems_results.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "data" / "ragbench" / "medical" / "build"
PRED = BUILD / "predictions"
GEMMA = BUILD / "llm_baselines" / "ragbench_tr_medical_v1" / "google_gemma-4-26b-a4b-it" / "zero_shot" / "predictions.jsonl"
ROUTE_LABELS = {"partially_supported", "contradicted"}      # frozen AP6 v1 PA routing set
N_BOOT, SEED = 10000, 42


def rd(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def binary(label):
    return None if label is None else (0 if label == "supported" else 1)


def scores(pred: np.ndarray, y: np.ndarray) -> dict:
    tp = int(((pred == 1) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"f1": 2 * tp / (2 * tp + fp + fn) if tp else 0.0, "precision": p, "recall": r,
            "false_alarm": fp / (fp + tn) if fp + tn else 0.0, "accuracy": (tp + tn) / len(y)}


def main() -> None:
    global BUILD, PRED, GEMMA
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(BUILD))
    ap.add_argument("--claims", default="ragbench_tr_medical_claims.jsonl")
    ap.add_argument("--gemma-dataset", default="ragbench_tr_medical_v1")
    ap.add_argument("--data-label", default="RAGBench pubmedqa test, 74 questions x 2 models, Turkish translation, GPT-4 silver labels")
    args = ap.parse_args()
    BUILD = Path(args.build).resolve()
    PRED = BUILD / "predictions"
    GEMMA = BUILD / "llm_baselines" / args.gemma_dataset / "google_gemma-4-26b-a4b-it" / "zero_shot" / "predictions.jsonl"
    claims = {r["example_id"]: r for r in rd(BUILD / args.claims)}
    k1 = {r["example_id"]: r for r in rd(PRED / "k1.jsonl")}
    k2 = {r["example_id"]: r["k2"] for r in rd(PRED / "k2_windowed.jsonl")}
    judge = {r["example_id"]: r["judge_decision"] for r in rd(PRED / "v4_judge.jsonl")}
    gemma = {r["example_id"]: r["predicted_label"] for r in rd(GEMMA) if r.get("status") == "success"}

    missing_judge = [e for e in claims if k2.get(e) is not None and k1[e]["predicted_label"] != k2[e]
                     and e not in judge]
    if missing_judge:
        raise SystemExit(f"V4 judge missing for {len(missing_judge)} sentences")

    rows = []
    for e, c in claims.items():
        a = k1[e]["predicted_label"]
        if k2.get(e) is None:
            p0, route = a, "k2_missing_k1"
        elif a == k2[e]:
            p0, route = a, "consensus"
        else:
            p0, route = judge[e], "v4_judge"
        routable = route == "consensus" and p0 in ROUTE_LABELS
        pa = gemma.get(e) if routable else p0           # None if Gemma has no answer for a routed row
        rows.append({"example_id": e, "question_id": c["question_id"], "model": c["model"],
                     "gold_binary": c["gold_binary"], "k1": a, "k1_truncated": k1[e]["truncated"],
                     "k2": k2.get(e), "route": route, "v4_judge": judge.get(e),
                     "hybrid_P0": p0, "hybrid_PA": pa, "gemma26b_zero_shot": gemma.get(e)})
    with (PRED / "system_predictions.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    y_all = np.array([1 if r["gold_binary"] == "unsupported" else 0 for r in rows])
    by_q = defaultdict(list)
    for i, r in enumerate(rows):
        by_q[r["question_id"]].append(i)
    questions = sorted(by_q)
    rng = np.random.default_rng(SEED)
    boots = [np.concatenate([by_q[questions[q]] for q in rng.choice(len(questions), len(questions))])
             for _ in range(N_BOOT)]

    def evaluate(key: str, subset=None) -> dict:
        keep = np.array([(binary(r[key]) is not None) and (subset is None or subset(r)) for r in rows])
        pred = np.array([binary(r[key]) if binary(r[key]) is not None else -1 for r in rows])
        point = scores(pred[keep], y_all[keep])
        dist = defaultdict(list)
        for idx in boots:
            idx = idx[keep[idx]]
            if len(idx) == 0 or y_all[idx].sum() == 0:
                continue
            for k, v in scores(pred[idx], y_all[idx]).items():
                dist[k].append(v)
        out = {"n": int(keep.sum()), "n_unsupported_gold": int(y_all[keep].sum())}
        for k, v in point.items():
            out[k] = round(v, 4)
            out[k + "_ci95"] = [round(float(np.percentile(dist[k], 2.5)), 4),
                                round(float(np.percentile(dist[k], 97.5)), 4)]
        return out

    gold_rate = float(y_all.mean())
    results = {
        "data": args.data_label,
        "n_sentences": len(rows), "unsupported_rate": round(gold_rate, 4),
        "trivial_all_unsupported_f1": round(2 * gold_rate / (1 + gold_rate), 4),
        "bootstrap": f"cluster over questions ({len(questions)}), {N_BOOT} resamples, seed {SEED}, 95% percentile",
        "routing": dict(Counter(r["route"] for r in rows)),
        "llm_call_rate_P0": round(sum(r["route"] == "v4_judge" for r in rows) / len(rows), 4),
        "pa_rerouted_to_gemma": sum(r["route"] == "consensus" and r["hybrid_P0"] in ROUTE_LABELS for r in rows),
        "systems": {
            "K1": evaluate("k1"),
            "K1_not_truncated": evaluate("k1", lambda r: not r["k1_truncated"]),
            "K1_truncated": evaluate("k1", lambda r: r["k1_truncated"]),
            "K2_windowed": evaluate("k2"),
            "Hybrid_P0": evaluate("hybrid_P0"),
            "Hybrid_PA": evaluate("hybrid_PA"),
            "Gemma26B_zero_shot": evaluate("gemma26b_zero_shot"),
        },
        "notes": ["Silver labels (GPT-4), binary per sentence; 4-class outputs collapsed to binary.",
                  "K2 uses per-document windowing (K-017); K1 sees the full context truncated at 512 tokens.",
                  "Gemma26B rows without a successful answer are excluded from its own score (n shown)."],
    }
    (BUILD / "systems_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{'sistem':22} {'n':>4} {'F1':>6} {'[95% GA]':>16} {'kesinlik':>9} {'duyarlılık':>11} {'YA':>6} {'doğruluk':>9}")
    for name, m in results["systems"].items():
        print(f"{name:22} {m['n']:4} {m['f1']:6.3f} {str(m['f1_ci95']):>16} {m['precision']:9.3f} "
              f"{m['recall']:11.3f} {m['false_alarm']:6.3f} {m['accuracy']:9.3f}")
    print("\nyönlendirme:", results["routing"], "| LLM çağrı oranı (P0):", results["llm_call_rate_P0"],
          "| PA'da Gemma'ya giden:", results["pa_rerouted_to_gemma"],
          "| saf taban F1:", results["trivial_all_unsupported_f1"])


if __name__ == "__main__":
    main()
