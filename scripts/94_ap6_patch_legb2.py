#!/usr/bin/env python3
"""
94_ap6_patch_legb2.py — Protokol v1.7: LEG-B2 sorusunun düzeltilmesinden sonra sistem tahminlerini ve etiketleme
setini, mevcut madde kimliklerini ve verilmiş etiketleri bozmadan günceller.

- Sistem tahminleri, 88'deki dondurulmuş kurallarla (P0/PA/PB) 858 cümle için yeniden üretilir;
  LEG-B2 dışındaki 843 cümlede bütün tahminler v1.6 ile aynı olmalıdır (betik bunu doğrular).
- Eski LEG-B2 maddeleri (11; hiçbiri etiketlenmemişti) etiketleme dosyalarından çıkarılır.
- Yeni LEG-B2 cümleleri (15) yeni kimliklerle (AP6-0855…) eklenir ve henüz etiketlenmemiş bölgeye
  rastgele (seed 47) yerleştirilir; daha önce verilmiş etiketlerin kimlikleri değişmez.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AP6 = ROOT / "data" / "ap6"
VER, ANN = AP6 / "verifier", AP6 / "annotation"
ARCH = AP6 / "_archive_v1.6_before_legb2_fix"
ROUTE = {"partially_supported", "contradicted"}


def rj(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def wj(p: Path, rows: list[dict]) -> None:
    with p.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> None:
    sentences = rj(AP6 / "generation" / "sentences.jsonl")
    claims = {r["example_id"]: r for r in rj(VER / "ap6_claims.jsonl")}
    questions = {r["question_id"]: r["question"] for r in rj(AP6 / "questions" / "questions_v1.1.jsonl")}
    k1 = {r["example_id"]: r["predicted_label"] for r in rj(VER / "k1_predictions.jsonl")}
    k2 = {r["example_id"]: r["pred_label"] for r in rj(VER / "k2_soft_prob_predictions.jsonl")}
    judge = {r["example_id"]: r["judge_decision"] for r in rj(VER / "v4_judge_predictions.jsonl")}
    llm = VER / "llm_baselines" / "ap6_v1"
    gemma = {r["example_id"]: r["predicted_label"] for r in rj(llm / "google_gemma-4-26b-a4b-it/zero_shot/predictions.jsonl")}
    gpt = {r["example_id"]: r["predicted_label"] for r in rj(llm / "openai_gpt-4.1-mini/few_shot_8/predictions.jsonl")}

    systems = []
    for s in sentences:
        i = s["sentence_id"]
        if i not in k2:
            p0, route = k1[i], "k2_missing_k1"
        elif k1[i] == k2[i]:
            p0, route = k1[i], "consensus"
        else:
            p0, route = judge[i], "v4_judge"
        routable = route == "consensus" and p0 in ROUTE
        systems.append({"example_id": i, "domain": s["domain"], "model": s["model"], "abstention_flag": s["abstention"],
                        "k1": k1[i], "k2": k2.get(i), "route": route, "v4_judge": judge.get(i), "hybrid_P0": p0,
                        "hybrid_PA": gemma[i] if routable else p0,
                        "hybrid_PB": gemma[i] if routable and s["domain"] == "medical" else p0,
                        "gemma26b_zero_shot": gemma[i], "gpt41mini_few_shot_8": gpt[i]})
    old = {r["example_id"]: r for r in rj(ARCH / "verifier" / "system_predictions_v1.jsonl")}
    diffs = [r["example_id"] for r in systems if not r["example_id"].startswith("LEG-B2") and old[r["example_id"]] != r]
    assert not diffs, f"LEG-B2 dışındaki tahminler değişti: {diffs[:5]}"
    wj(VER / "system_predictions_v1.jsonl", systems)

    # Etiketleme dosyaları
    items_a = rj(ANN / "items_A.jsonl")
    key = rj(ANN / "internal" / "item_key_v1.jsonl")
    key_by_item = {k["item_id"]: k for k in key}
    labeled = {r["item_id"] for r in rj(ANN / "labels_A.jsonl")} if (ANN / "labels_A.jsonl").exists() else set()
    old_legb2 = [k["item_id"] for k in key if k["example_id"].startswith("LEG-B2")]
    assert not (set(old_legb2) & labeled), "eski LEG-B2 maddelerinden etiketlenen var"
    items_a = [it for it in items_a if it["item_id"] not in old_legb2]
    key = [k for k in key if k["item_id"] not in old_legb2]

    by_answer: dict[tuple, list[dict]] = {}
    for s in sentences:
        by_answer.setdefault((s["question_id"], s["model"]), []).append(s)
    for v in by_answer.values():
        v.sort(key=lambda x: x["position"])
    flagged = {r["example_id"] for r in systems if any(r[k] not in (None, "supported") for k in
               ["k1", "k2", "hybrid_P0", "hybrid_PA", "hybrid_PB", "gemma26b_zero_shot", "gpt41mini_few_shot_8"])}
    new_ids = sorted(s["sentence_id"] for s in sentences if s["question_id"] == "LEG-B2")
    next_n = max(int(k["item_id"].split("-")[1]) for k in rj(ARCH / "annotation" / "internal" / "item_key_v1.jsonl")) + 1
    new_items = []
    for n, i in enumerate(new_ids, start=next_n):
        s = next(x for x in sentences if x["sentence_id"] == i)
        ans = by_answer[(s["question_id"], s["model"])]
        pos = [x["sentence_id"] for x in ans].index(i)
        item_id = f"AP6-{n:04d}"
        new_items.append({"item_id": item_id, "question": questions[s["question_id"]],
                          "answer_before": " ".join(x["sentence"] for x in ans[:pos]), "sentence": s["sentence"],
                          "answer_after": " ".join(x["sentence"] for x in ans[pos + 1:]),
                          "context": claims[i]["context"], "domain": s["domain"]})
        key.append({"item_id": item_id, "example_id": i,
                    "stratum": "system_flagged" if i in flagged else ("abstention_flag" if s["abstention"] else "census_rest"),
                    "inclusion_prob": 1.0, "added_in": "v1.7"})
    # Henüz etiketlenmemiş bölgeye rastgele yerleştir
    last_labeled = max((k for k, it in enumerate(items_a) if it["item_id"] in labeled), default=-1)
    rng = random.Random(47)
    for it in new_items:
        items_a.insert(rng.randint(last_labeled + 1, len(items_a)), it)
    wj(ANN / "items_A.jsonl", items_a)
    wj(ANN / "internal" / "item_key_v1.jsonl", key)

    items_b = rj(ANN / "items_B.jsonl")
    b_legb2 = [it["item_id"] for it in items_b if it["item_id"] in old_legb2]
    if b_legb2:
        repl = rng.sample(new_items, len(b_legb2))
        items_b = [it for it in items_b if it["item_id"] not in old_legb2] + repl
        rng.shuffle(items_b)
        wj(ANN / "items_B.jsonl", items_b)

    man_p = ANN / "internal" / "annotation_set_manifest_v1.json"
    man = json.loads(man_p.read_text(encoding="utf-8"))
    man.update({"protocol_amendment": "v1.7 (LEG-B2 question fix)", "n_sentences": len(sentences), "n_items_A": len(items_a),
                "n_items_B": len(items_b), "legb2_removed_items": old_legb2, "legb2_added_items": [it["item_id"] for it in new_items],
                "b_items_replaced": b_legb2,
                "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                           [VER / "system_predictions_v1.jsonl", ANN / "items_A.jsonl", ANN / "items_B.jsonl", ANN / "internal" / "item_key_v1.jsonl"]}})
    man_p.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: man[k] for k in ["n_sentences", "n_items_A", "n_items_B", "b_items_replaced"]}, ensure_ascii=False),
          "| removed", len(old_legb2), "added", len(new_items), "| labeled kept", len(labeled))


if __name__ == "__main__":
    main()
