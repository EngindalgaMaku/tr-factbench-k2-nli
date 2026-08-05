#!/usr/bin/env python3
"""
Zero-Shot NLI Deneyleri — v2
Sırayla 3 model denenir:
  NLI-A: MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7
  NLI-B: MoritzLaurer/mDeBERTa-v3-base-mnli-xnli
  NLI-C: joeddav/xlm-roberta-large-xnli

Her model için 2 premise modu:
  context_only      → yalnızca bağlam
  question_context  → soru + bağlam

Toplam 6 deney: NLI-A1, NLI-A2, NLI-B1, NLI-B2, NLI-C1, NLI-C2

Kullanım:
    # Tüm deneyleri çalıştır
    python nli_zeroshot_v2/run_nli_zeroshot.py --data <veri_dosyası.jsonl>

    # Sadece belirli bir deney
    python nli_zeroshot_v2/run_nli_zeroshot.py --data <veri.jsonl> --exp NLI-A1

    # Tamamlananları atla (resume)
    python nli_zeroshot_v2/run_nli_zeroshot.py --data <veri.jsonl> --resume

Çıktı: nli_zeroshot_v2/outputs/<deney_id>/
  results.json       — metrikler
  predictions.jsonl  — örnek bazlı tahminler
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    log_loss,
    brier_score_loss,
)
from transformers import pipeline

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Klasörler ─────────────────────────────────────────────────────────────────
OUTPUT_BASE = Path(__file__).parent / "outputs"

# ── Deney matrisi ─────────────────────────────────────────────────────────────
EXPERIMENTS = [
    {
        "id": "NLI-A1",
        "model_name": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
        "premise_mode": "context_only",
        "desc": "mDeBERTa-xnli-2mil7 | Yalnızca bağlam",
    },
    {
        "id": "NLI-A2",
        "model_name": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
        "premise_mode": "question_context",
        "desc": "mDeBERTa-xnli-2mil7 | Soru + bağlam",
    },
    {
        "id": "NLI-B1",
        "model_name": "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
        "premise_mode": "context_only",
        "desc": "mDeBERTa-mnli-xnli | Yalnızca bağlam",
    },
    {
        "id": "NLI-B2",
        "model_name": "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
        "premise_mode": "question_context",
        "desc": "mDeBERTa-mnli-xnli | Soru + bağlam",
    },
    {
        "id": "NLI-C1",
        "model_name": "joeddav/xlm-roberta-large-xnli",
        "premise_mode": "context_only",
        "desc": "XLM-R-large-xnli | Yalnızca bağlam",
    },
    {
        "id": "NLI-C2",
        "model_name": "joeddav/xlm-roberta-large-xnli",
        "premise_mode": "question_context",
        "desc": "XLM-R-large-xnli | Soru + bağlam",
    },
]

# ── Etiket dönüşümü ───────────────────────────────────────────────────────────
# Format A: doğrudan NLI (premise/hypothesis/label)
# Format B: hallucination dataset (context/claim/gold_label → 5 sınıf)
LABEL_MAP_5TO3 = {
    "supported":                "entailment",
    "contradicted":             "contradiction",
    "unsupported":              "neutral",
    "insufficient_information": "neutral",
    "partially_supported":      None,   # atlanır
}

NLI_LABELS   = ["entailment", "neutral", "contradiction"]
LABEL2IDX    = {l: i for i, l in enumerate(NLI_LABELS)}


def detect_format(data: list[dict]) -> str:
    """Veri formatını otomatik algıla: 'nli' veya 'hallucination'"""
    if not data:
        return "nli"
    sample = data[0]
    if "premise" in sample and "hypothesis" in sample and "label" in sample:
        return "nli"
    return "hallucination"


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def load_data(path: str) -> list[dict]:
    """JSONL veya CSV dosyasını yükler. CSV'de context/claim/label sütunları beklenir."""
    p = Path(path)
    if p.suffix.lower() == ".csv":
        import csv
        records = []
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # CSV → JSONL-uyumlu dict: context→premise, claim→hypothesis, label→label
                records.append({
                    "id":         row.get("id", ""),
                    "domain":     row.get("domain", ""),
                    "difficulty": row.get("difficulty", ""),
                    "premise":    row.get("context", row.get("premise", "")),
                    "hypothesis": row.get("claim",   row.get("hypothesis", "")),
                    "label":      row.get("label",   "").strip().lower(),
                    "rationale":  row.get("rationale", ""),
                    # orijinal CSV sütunlarını da sakla (çıktı için)
                    "_csv_row":   dict(row),
                })
        return records
    # JSONL
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_review_csv(
    template_path: str,
    predictions_log: list[dict],
    exp_id: str,
    output_path: str,
) -> None:
    """
    Review CSV'yi tahminlerle doldurur.
    template_path: orijinal CSV (başlık + boş sütunlar)
    predictions_log: run_experiment'ten dönen tahmin listesi
    exp_id: sütun adı öneki (örn. NLI-A1)
    output_path: yazılacak CSV yolu
    """
    import csv

    # id → tahmin eşlemesi
    pred_map = {p["example_id"]: p for p in predictions_log}

    with open(template_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # Sütun adları: deney ID'si ile öneklenmiş
    col_pred   = f"{exp_id}_predicted_label"
    col_ent    = f"{exp_id}_entailment_score"
    col_neu    = f"{exp_id}_neutral_score"
    col_con    = f"{exp_id}_contradiction_score"
    col_ok     = f"{exp_id}_is_correct"

    new_cols = [col_pred, col_ent, col_neu, col_con, col_ok]
    for col in new_cols:
        if col not in fieldnames:
            fieldnames.append(col)

    for row in rows:
        ex_id = row.get("id", "")
        p = pred_map.get(ex_id)
        if p:
            row[col_pred] = p["pred_nli"]
            row[col_ent]  = p["prob_entailment"]
            row[col_neu]  = p["prob_neutral"]
            row[col_con]  = p["prob_contradiction"]
            row[col_ok]   = "1" if p["correct"] else "0"
        else:
            for col in new_cols:
                row[col] = ""

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  ✓ Review CSV güncellendi: {output_path}")


def filter_and_map(data: list[dict], fmt: str, include_partial: bool = False) -> list[dict]:
    """
    Etiketleri normalize et ve nli_label alanını ekle.
    fmt='nli'           → label zaten entailment/neutral/contradiction
    fmt='hallucination' → gold_label 5 sınıf, 3 sınıfa dönüştür
    """
    out = []
    for ex in data:
        if fmt == "nli":
            raw = ex.get("label", "").lower().strip()
            if raw not in LABEL2IDX:
                continue
            out.append({**ex, "nli_label": raw})
        else:
            nli_label = LABEL_MAP_5TO3.get(ex.get("gold_label", ""))
            if nli_label is None:
                if include_partial:
                    nli_label = "neutral"
                else:
                    continue
            out.append({**ex, "nli_label": nli_label})
    return out


def build_premise(ex: dict, mode: str, fmt: str) -> str:
    """
    fmt='nli'           → premise alanı doğrudan kullanılır (mode yok sayılır)
    fmt='hallucination' → context_only veya question_context
    """
    if fmt == "nli":
        return ex["premise"]
    if mode == "context_only":
        return ex["context"]
    elif mode == "question_context":
        q = ex.get("question", "").strip()
        c = ex["context"]
        return f"{q}\n\n{c}" if q else c
    raise ValueError(f"Bilinmeyen premise_mode: {mode}")


def get_hypothesis(ex: dict, fmt: str) -> str:
    """Hypothesis/claim alanını formatına göre döndür."""
    if fmt == "nli":
        return ex["hypothesis"]
    return ex["claim"]


def get_example_id(ex: dict, i: int) -> str:
    return ex.get("id") or ex.get("example_id") or f"ex_{i}"


def normalize_label(raw: str) -> str:
    raw = raw.lower()
    if "entail" in raw:
        return "entailment"
    if "contradict" in raw:
        return "contradiction"
    if "neutral" in raw:
        return "neutral"
    raise ValueError(f"Tanınmayan NLI etiketi: {raw}")


def compute_ece(probs: list[list[float]], labels: list[int], n_bins: int = 10) -> float:
    probs  = np.array(probs)
    labels = np.array(labels)
    max_p  = probs.max(axis=1)
    preds  = probs.argmax(axis=1)
    correct = (preds == labels).astype(float)
    edges  = np.linspace(0, 1, n_bins + 1)
    ece    = 0.0
    for i in range(n_bins):
        mask = (max_p >= edges[i]) & (max_p < edges[i + 1])
        if mask.sum() == 0:
            continue
        ece += mask.sum() * abs(correct[mask].mean() - max_p[mask].mean())
    return float(ece / len(labels))


def run_experiment(exp: dict, data: list[dict], fmt: str = "nli") -> dict:
    print(f"\n{'='*65}")
    print(f"  {exp['id']}: {exp['desc']}")
    print(f"  Model : {exp['model_name']}")
    print(f"  Örnek : {len(data)}")
    print(f"{'='*65}")

    device   = 0 if torch.cuda.is_available() else -1
    is_large = "large" in exp["model_name"].lower()
    # XLM-R-large BF16 ile CUDA assert verebilir → FP32
    use_bf16 = torch.cuda.is_bf16_supported() and not is_large
    dtype    = torch.bfloat16 if use_bf16 else torch.float32

    print(f"  Cihaz : {'CUDA' if device == 0 else 'CPU'} | dtype: {dtype}")

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    pipe = pipeline(
        "text-classification",
        model=exp["model_name"],
        device=device,
        dtype=dtype,
    )

    # Etiket sırası doğrulama
    id2label = pipe.model.config.id2label
    raw_labels = [id2label[i].lower() for i in range(len(id2label))]
    print(f"  Model etiket sırası: {raw_labels}")
    for expected in NLI_LABELS:
        assert any(expected in l for l in raw_labels), f"Etiket bulunamadı: {expected}"

    # Hızlı sanity check
    print("  Sanity check...")
    checks = [
        ("Türkiye Ankara'da bulunmaktadır.", "Türkiye'nin başkenti Ankara'dır.", "entailment"),
        ("Türkiye Ankara'da bulunmaktadır.", "Türkiye'nin başkenti İstanbul'dur.", "contradiction"),
        ("Türkiye Ankara'da bulunmaktadır.", "Türkiye'nin nüfusu 85 milyondur.", "neutral"),
    ]
    for premise, hyp, expected in checks:
        out  = pipe({"text": premise, "text_pair": hyp}, top_k=None)
        pred = normalize_label(max(out, key=lambda x: x["score"])["label"])
        mark = "✓" if pred == expected else "✗"
        print(f"    {mark} beklenen={expected:15s} tahmin={pred}")

    # ── Ana değerlendirme ──────────────────────────────────────────────────────
    print(f"\n  Değerlendirme başlıyor ({len(data)} örnek)...")
    t0 = time.time()

    gold_labels      = []
    pred_labels      = []
    pred_probs_list  = []
    predictions_log  = []

    for i, ex in enumerate(data):
        premise    = build_premise(ex, exp["premise_mode"], fmt)
        hypothesis = get_hypothesis(ex, fmt)

        out = pipe({"text": premise, "text_pair": hypothesis}, top_k=None)

        prob_dict = {normalize_label(item["label"]): item["score"] for item in out}
        probs     = [prob_dict.get(l, 0.0) for l in NLI_LABELS]
        s         = sum(probs)
        probs     = [p / s for p in probs]

        pred_idx   = int(np.argmax(probs))
        pred_label = NLI_LABELS[pred_idx]
        gold_label = ex["nli_label"]

        gold_labels.append(LABEL2IDX[gold_label])
        pred_labels.append(pred_idx)
        pred_probs_list.append(probs)

        predictions_log.append({
            "example_id":         get_example_id(ex, i),
            "domain":             ex.get("domain", ""),
            "difficulty":         ex.get("difficulty", ""),
            "gold_5class":        ex.get("gold_label", ""),
            "gold_nli":           gold_label,
            "pred_nli":           pred_label,
            "correct":            pred_label == gold_label,
            "prob_entailment":    round(probs[0], 4),
            "prob_neutral":       round(probs[1], 4),
            "prob_contradiction": round(probs[2], 4),
            "max_prob":           round(max(probs), 4),
        })

        if (i + 1) % 100 == 0 or (i + 1) == len(data):
            elapsed = time.time() - t0
            print(f"    {i+1}/{len(data)} — {elapsed:.1f}s")

    elapsed_total    = time.time() - t0
    samples_per_sec  = len(data) / elapsed_total

    # ── Metrikler ──────────────────────────────────────────────────────────────
    gold_arr  = np.array(gold_labels)
    pred_arr  = np.array(pred_labels)
    probs_arr = np.array(pred_probs_list)

    report = classification_report(
        gold_arr, pred_arr,
        target_names=NLI_LABELS,
        output_dict=True,
        zero_division=0,
    )
    cm        = confusion_matrix(gold_arr, pred_arr, labels=[0, 1, 2])
    macro_f1  = report["macro avg"]["f1-score"]
    accuracy  = report["accuracy"]
    ece       = compute_ece(pred_probs_list, gold_labels)
    nll       = log_loss(gold_arr, probs_arr)

    brier_scores = []
    for cls_idx in range(3):
        b_gold = (gold_arr == cls_idx).astype(int)
        b_prob = probs_arr[:, cls_idx]
        brier_scores.append(brier_score_loss(b_gold, b_prob))
    brier_avg = float(np.mean(brier_scores))

    # Alan bazlı
    domain_results = {}
    for domain in ["medical", "finance", "legal"]:
        mask   = np.array([ex.get("domain", "") == domain for ex in data])
        d_gold = gold_arr[mask]
        d_pred = pred_arr[mask]
        if len(d_gold) > 0:
            d_rep = classification_report(
                d_gold, d_pred,
                target_names=NLI_LABELS,
                output_dict=True,
                zero_division=0,
            )
            domain_results[domain] = {
                "macro_f1": d_rep["macro avg"]["f1-score"],
                "accuracy": d_rep["accuracy"],
                "n": int(mask.sum()),
            }

    # ── Ekrana yazdır ──────────────────────────────────────────────────────────
    print(f"\n  {'─'*55}")
    print(f"  Macro-F1 : {macro_f1*100:.2f}%")
    print(f"  Accuracy : {accuracy*100:.2f}%")
    print(f"  ECE      : {ece:.4f}")
    print(f"  Brier    : {brier_avg:.4f}")
    print(f"  NLL      : {nll:.4f}")
    print(f"  Süre     : {elapsed_total:.1f}s ({samples_per_sec:.1f} örnek/s)")
    print(f"\n  Sınıf bazlı:")
    for cls in NLI_LABELS:
        r = report[cls]
        print(f"    {cls:15s}: F1={r['f1-score']*100:.2f}  P={r['precision']*100:.2f}  R={r['recall']*100:.2f}  n={int(r['support'])}")
    print(f"\n  Alan bazlı Macro-F1:")
    for domain, dr in domain_results.items():
        print(f"    {domain:10s}: {dr['macro_f1']*100:.2f}%  acc={dr['accuracy']*100:.2f}%  (n={dr['n']})")
    print(f"\n  Confusion matrix (E=entailment, N=neutral, C=contradiction):")
    print(f"         E    N    C")
    for i, row_label in enumerate(["E", "N", "C"]):
        print(f"    {row_label}  {cm[i][0]:4d} {cm[i][1]:4d} {cm[i][2]:4d}")

    # ── Kaydet ─────────────────────────────────────────────────────────────────
    out_dir = OUTPUT_BASE / exp["id"]
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "experiment_id":   exp["id"],
        "model_name":      exp["model_name"],
        "premise_mode":    exp["premise_mode"],
        "n_examples":      len(data),
        "macro_f1":        macro_f1,
        "accuracy":        accuracy,
        "ece":             ece,
        "brier_avg":       brier_avg,
        "nll":             nll,
        "elapsed_sec":     elapsed_total,
        "samples_per_sec": samples_per_sec,
        "per_class": {
            cls: {
                "f1":        report[cls]["f1-score"],
                "precision": report[cls]["precision"],
                "recall":    report[cls]["recall"],
                "support":   int(report[cls]["support"]),
            }
            for cls in NLI_LABELS
        },
        "domain_results":    domain_results,
        "confusion_matrix":  cm.tolist(),
    }

    with open(out_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(out_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
        for p in predictions_log:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"\n  ✓ Kaydedildi: {out_dir}")

    del pipe
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return results


def print_summary(all_results: list[dict]) -> None:
    print(f"\n{'='*75}")
    print(f"  ÖZET TABLO")
    print(f"{'='*75}")
    hdr = f"{'Deney':8} {'Model':42} {'Premise':18} {'F1':>7} {'Acc':>7} {'ECE':>7}"
    print(hdr)
    print("-" * len(hdr))
    for r in all_results:
        model = r["model_name"].split("/")[-1][:40]
        print(
            f"{r['experiment_id']:8} {model:42} {r['premise_mode']:18} "
            f"{r['macro_f1']*100:>6.2f}% {r['accuracy']*100:>6.2f}% {r['ece']:>7.4f}"
        )

    # En iyi deney
    best = max(all_results, key=lambda r: r["macro_f1"])
    print(f"\n  En iyi: {best['experiment_id']} — Macro-F1 {best['macro_f1']*100:.2f}%")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zero-Shot NLI Deneyleri v2")
    parser.add_argument(
        "--data", required=True,
        help="Test verisi: JSONL veya CSV dosyası"
    )
    parser.add_argument(
        "--review-csv", default=None,
        help="Sonuçların yazılacağı review CSV (belirtilmezse --data CSV ise o kullanılır)"
    )
    parser.add_argument(
        "--exp", default=None,
        help="Sadece bu deneyi çalıştır (örn: NLI-A1). Belirtilmezse tümü çalışır."
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Tamamlanmış deneyleri atla (results.json varsa)"
    )
    parser.add_argument(
        "--no-filter", action="store_true",
        help="partially_supported örnekleri de dahil et (NLI etiketine neutral olarak map edilir)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Zero-Shot NLI Deneyleri v2")
    print(f"Veri : {args.data}")

    raw_data = load_data(args.data)
    print(f"Toplam örnek: {len(raw_data)}")

    # Format otomatik algıla
    fmt = detect_format(raw_data)
    print(f"Veri formatı: {fmt}")

    data = filter_and_map(raw_data, fmt, include_partial=args.no_filter)
    print(f"Kullanılan örnek: {len(data)}")

    # Etiket dağılımı
    dist = defaultdict(int)
    for ex in data:
        dist[ex["nli_label"]] += 1
    print(f"NLI dağılımı: {dict(dist)}")

    # NLI formatında premise_mode anlamsız — sadece context_only deneyleri çalıştır
    if fmt == "nli":
        exps_to_run_all = [e for e in EXPERIMENTS if e["premise_mode"] == "context_only"]
        print(f"NLI formatı: premise_mode yok sayılır, {len(exps_to_run_all)} deney çalışır (A1/B1/C1).")
    else:
        exps_to_run_all = EXPERIMENTS

    # --exp filtresi
    if args.exp:
        exps_to_run = [e for e in exps_to_run_all if e["id"] == args.exp]
        if not exps_to_run:
            valid = [e["id"] for e in exps_to_run_all]
            print(f"Hata: '{args.exp}' bulunamadı. Geçerli ID'ler: {valid}")
            sys.exit(1)
    else:
        exps_to_run = exps_to_run_all

    # Review CSV yolu belirle
    review_csv_path = None
    if args.review_csv:
        review_csv_path = args.review_csv
    elif Path(args.data).suffix.lower() == ".csv":
        review_csv_path = args.data
    if review_csv_path:
        print(f"Review CSV: {review_csv_path}")

    all_results = []
    for exp in exps_to_run:
        result_path = OUTPUT_BASE / exp["id"] / "results.json"
        if args.resume and result_path.exists():
            print(f"\n[SKIP] {exp['id']} zaten tamamlanmış.")
            with open(result_path, encoding="utf-8") as f:
                all_results.append(json.load(f))
            continue
        try:
            result = run_experiment(exp, data, fmt=fmt)
            all_results.append(result)

            # Review CSV güncelle
            if review_csv_path:
                pred_log_path = OUTPUT_BASE / exp["id"] / "predictions.jsonl"
                if pred_log_path.exists():
                    import csv as _csv
                    pred_log = []
                    with open(pred_log_path, encoding="utf-8") as pf:
                        for line in pf:
                            if line.strip():
                                pred_log.append(json.loads(line))
                    out_csv = OUTPUT_BASE / exp["id"] / f"review_{exp['id']}.csv"
                    write_review_csv(review_csv_path, pred_log, exp["id"], str(out_csv))

        except Exception as e:
            print(f"\n[HATA] {exp['id']} başarısız: {e}")
            import traceback
            traceback.print_exc()

    if all_results:
        print_summary(all_results)
        OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_BASE / "summary.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nÖzet: {OUTPUT_BASE / 'summary.json'}")

        # Tüm deneyleri tek review CSV'ye birleştir
        if review_csv_path:
            import csv as _csv
            # Tüm deney CSV'lerini oku ve birleştir
            all_pred_logs = {}
            for exp in exps_to_run:
                pred_log_path = OUTPUT_BASE / exp["id"] / "predictions.jsonl"
                if pred_log_path.exists():
                    with open(pred_log_path, encoding="utf-8") as pf:
                        for line in pf:
                            if line.strip():
                                p = json.loads(line)
                                ex_id = p["example_id"]
                                if ex_id not in all_pred_logs:
                                    all_pred_logs[ex_id] = {}
                                all_pred_logs[ex_id][exp["id"]] = p

            # Tüm deneylerin sonuçlarını tek CSV'ye yaz
            combined_csv = OUTPUT_BASE / "review_all_experiments.csv"
            with open(review_csv_path, encoding="utf-8-sig") as f:
                reader = _csv.DictReader(f)
                fieldnames = list(reader.fieldnames or [])
                rows = list(reader)

            for exp in exps_to_run:
                eid = exp["id"]
                for col in [f"{eid}_predicted_label", f"{eid}_entailment_score",
                             f"{eid}_neutral_score", f"{eid}_contradiction_score", f"{eid}_is_correct"]:
                    if col not in fieldnames:
                        fieldnames.append(col)

            for row in rows:
                ex_id = row.get("id", "")
                for exp in exps_to_run:
                    eid = exp["id"]
                    p = all_pred_logs.get(ex_id, {}).get(eid)
                    if p:
                        row[f"{eid}_predicted_label"]      = p["pred_nli"]
                        row[f"{eid}_entailment_score"]     = p["prob_entailment"]
                        row[f"{eid}_neutral_score"]        = p["prob_neutral"]
                        row[f"{eid}_contradiction_score"]  = p["prob_contradiction"]
                        row[f"{eid}_is_correct"]           = "1" if p["correct"] else "0"

            with open(combined_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = _csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
            print(f"\nBirleşik review CSV: {combined_csv}")


if __name__ == "__main__":
    main()