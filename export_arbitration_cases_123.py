import json
from pathlib import Path

gold_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl")
k1_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl")
k2_path = Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")
atom_preds_path = Path("runs/K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7/atom_predictions.jsonl")
out_path = Path("data/processed/arbitration/arbitration_cases_123.jsonl")
out_path.parent.mkdir(parents=True, exist_ok=True)

gold_data = {}
for line in gold_path.read_text(encoding="utf-8-sig").splitlines():
    if not line.strip(): continue
    item = json.loads(line)
    eid = item.get("release_example_id") or item.get("example_id")
    gold_data[eid] = item

k1_data = {}
for line in k1_path.read_text(encoding="utf-8-sig").splitlines():
    if not line.strip(): continue
    item = json.loads(line)
    eid = item.get("release_example_id") or item.get("example_id")
    k1_data[eid] = item

k2_data = {}
for line in k2_path.read_text(encoding="utf-8-sig").splitlines():
    if not line.strip(): continue
    item = json.loads(line)
    eid = item.get("release_example_id") or item.get("example_id")
    k2_data[eid] = item

# atom predictions mapping: example_id -> list of {"atom": ..., "label": ...}
atom_map = {}
for line in atom_preds_path.read_text(encoding="utf-8-sig").splitlines():
    if not line.strip(): continue
    rec = json.loads(line)
    eid = rec.get("release_example_id") or rec.get("example_id")
    if eid not in atom_map:
        atom_map[eid] = []
    atom_map[eid].append({
        "atom": rec.get("atom_text") or rec.get("atom") or rec.get("claim_atom"),
        "label": rec.get("predicted_label") or rec.get("label") or rec.get("pred_label")
    })

disagreements = []
for eid, g in gold_data.items():
    gold_label = g.get("gold_label") or g.get("label")
    k1_p = k1_data[eid]["predicted_label"]
    k2_p = k2_data[eid]["pred_label"]
    
    if k1_p != k2_p:
        case = {
            "example_id": eid,
            "domain": g.get("domain", "general"),
            "context": g["context"],
            "question": g.get("question", ""),
            "claim": g["claim"],
            "gold_label": gold_label,
            "k1_pred": k1_p,
            "k1_correct": (k1_p == gold_label),
            "k2_pred": k2_p,
            "k2_correct": (k2_p == gold_label),
            "k2_atoms": atom_map.get(eid, [])
        }
        disagreements.append(case)

with open(out_path, "w", encoding="utf-8") as f:
    for d in disagreements:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print(f"Başarıyla kaydedildi: {out_path} ({len(disagreements)} vaka)")
