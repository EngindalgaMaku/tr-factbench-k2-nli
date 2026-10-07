#!/usr/bin/env python3
"""
88_ap6_build_annotation_set.py
AP6 protokolü §7 ve v1.2–v1.4 eklerine göre:
  (1) hibrit tahminleri (P0 / PA / PB) dondurulmuş kurallarla üretir ve tüm sistem tahminlerini
      tek dosyada, SHA-256 ile kaydeder (etiketler görülmeden önce);
  (2) etiketlenecek cümleleri seçer:
        - herhangi bir sistemin supported dışı dediği bütün cümleler,
        - önceden belirlenmiş kalıpla çekimser (abstention) işaretlenen bütün cümleler
          (Anotatör A bu işareti doğrular / düzeltir),
        - geri kalanlardan rastgele 100 cümle (seed 42);
  (3) Anotatör A için tüm seçilen cümleleri, Anotatör B için bunlardan rastgele 50 cümleyi
      kör biçimde yazar: sistem tahminleri, seçilme nedeni, model adı ve çekimserlik işareti gösterilmez;
      öğe kimlikleri anlamsızdır ve sıra karıştırılmıştır. Kimlik eşlemesi ayrı bir iç dosyada tutulur.

Hibrit kurallar (configs/frozen/K3_ROUTING_POLICIES_v1.json):
  P0: K1 == K2 ise ortak karar; K1 != K2 ise V4 hakeminin kararı; K2 yoksa (atomizer hatası) K1.
  PA: P0 + uzlaşma etiketi partially_supported / contradicted olan cümlelerde kör Gemma-26B kararı.
  PB: P0 + yalnızca tıp alanında, uzlaşma etiketi partially_supported / contradicted olan cümlelerde kör Gemma-26B kararı.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AP6 = ROOT / "data" / "ap6"
VER = AP6 / "verifier"
ANN = AP6 / "annotation"
SEED = 42
N_RANDOM = 100  # v1.0 kuralı; v1.5 ile tam sayım (CENSUS = True) uygulanır
CENSUS = True
N_B = 50
ROUTE_LABELS = {"partially_supported", "contradicted"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    sentences = read_jsonl(AP6 / "generation" / "sentences.jsonl")
    claims = {r["example_id"]: r for r in read_jsonl(VER / "ap6_claims.jsonl")}
    questions = {r["question_id"]: r["question"] for r in read_jsonl(AP6 / "questions" / "questions_v1.1.jsonl")}
    k1 = {r["example_id"]: r["predicted_label"] for r in read_jsonl(VER / "k1_predictions.jsonl")}
    k2 = {r["example_id"]: r["pred_label"] for r in read_jsonl(VER / "k2_soft_prob_predictions.jsonl")}
    judge = {r["example_id"]: r["judge_decision"] for r in read_jsonl(VER / "v4_judge_predictions.jsonl")}
    llm_root = VER / "llm_baselines" / "ap6_v1"
    gemma = {r["example_id"]: r["predicted_label"] for r in read_jsonl(
        llm_root / "google_gemma-4-26b-a4b-it" / "zero_shot" / "predictions.jsonl")}
    gpt = {r["example_id"]: r["predicted_label"] for r in read_jsonl(
        llm_root / "openai_gpt-4.1-mini" / "few_shot_8" / "predictions.jsonl")}

    ids = [s["sentence_id"] for s in sentences]
    assert set(ids) == set(claims) == set(k1) == set(gemma) == set(gpt), "girdi kümeleri uyuşmuyor"
    missing_judge = [i for i in ids if i in k2 and k1[i] != k2[i] and i not in judge]
    if missing_judge:
        raise SystemExit(f"V4 hakem kararı eksik: {len(missing_judge)} cümle; önce scripts/87 tamamlanmalı")

    systems = []
    for s in sentences:
        i = s["sentence_id"]
        if i not in k2:
            p0, route = k1[i], "k2_missing_k1"
        elif k1[i] == k2[i]:
            p0, route = k1[i], "consensus"
        else:
            p0, route = judge[i], "v4_judge"
        consensus_routable = route == "consensus" and p0 in ROUTE_LABELS
        pa = gemma[i] if consensus_routable else p0
        pb = gemma[i] if consensus_routable and s["domain"] == "medical" else p0
        systems.append({"example_id": i, "domain": s["domain"], "model": s["model"],
                        "abstention_flag": s["abstention"], "k1": k1[i], "k2": k2.get(i), "route": route,
                        "v4_judge": judge.get(i), "hybrid_P0": p0, "hybrid_PA": pa, "hybrid_PB": pb,
                        "gemma26b_zero_shot": gemma[i], "gpt41mini_few_shot_8": gpt[i]})
    sys_path = VER / "system_predictions_v1.jsonl"
    write_jsonl(sys_path, systems)

    pred_keys = ["k1", "k2", "hybrid_P0", "hybrid_PA", "hybrid_PB", "gemma26b_zero_shot", "gpt41mini_few_shot_8"]
    flagged = {r["example_id"] for r in systems
               if any(r[k] is not None and r[k] != "supported" for k in pred_keys)}
    abstained = {s["sentence_id"] for s in sentences if s["abstention"]}
    rest = sorted(set(ids) - flagged - abstained)
    rng = random.Random(SEED)
    random_part = set(rest) if CENSUS else set(rng.sample(rest, min(N_RANDOM, len(rest))))
    selected = sorted(flagged | abstained | random_part)

    by_answer: dict[tuple, list[dict]] = {}
    for s in sentences:
        by_answer.setdefault((s["question_id"], s["model"]), []).append(s)
    for v in by_answer.values():
        v.sort(key=lambda x: x["position"])

    order = selected[:]
    random.Random(SEED + 1).shuffle(order)
    sent = {s["sentence_id"]: s for s in sentences}
    items_a, key = [], []
    for n, i in enumerate(order, start=1):
        s = sent[i]
        ans = by_answer[(s["question_id"], s["model"])]
        pos = [x["sentence_id"] for x in ans].index(i)
        item_id = f"AP6-{n:04d}"
        items_a.append({"item_id": item_id, "question": questions[s["question_id"]],
                        "answer_before": " ".join(x["sentence"] for x in ans[:pos]),
                        "sentence": s["sentence"],
                        "answer_after": " ".join(x["sentence"] for x in ans[pos + 1:]),
                        "context": claims[i]["context"], "domain": s["domain"]})
        key.append({"item_id": item_id, "example_id": i,
                    "stratum": "system_flagged" if i in flagged else ("abstention_flag" if i in abstained else "census_rest" if CENSUS else "random"),
                    "inclusion_prob": 1.0 if (i in flagged or i in abstained) else len(random_part) / len(rest)})
    b_ids = set(random.Random(SEED + 2).sample([it["item_id"] for it in items_a], min(N_B, len(items_a))))
    items_b = [it for it in items_a if it["item_id"] in b_ids]
    random.Random(SEED + 3).shuffle(items_b)

    write_jsonl(ANN / "items_A.jsonl", items_a)
    write_jsonl(ANN / "items_B.jsonl", items_b)
    write_jsonl(ANN / "internal" / "item_key_v1.jsonl", key)
    manifest = {
        "created_before_any_label": True, "census": CENSUS, "seed": SEED, "n_sentences": len(ids),
        "n_system_flagged": len(flagged), "n_abstention_flag_only": len(abstained - flagged),
        "n_random": len(random_part), "n_rest_pool": len(rest), "n_items_A": len(items_a), "n_items_B": len(items_b),
        "sha256": {p.name: sha256(p) for p in [sys_path, ANN / "items_A.jsonl", ANN / "items_B.jsonl",
                                                ANN / "internal" / "item_key_v1.jsonl"]},
    }
    (ANN / "internal" / "annotation_set_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "sha256"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
