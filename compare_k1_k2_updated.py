import json
from pathlib import Path

gold_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl")
k1_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl")
k2_path = Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")

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

total = len(gold_data)
consensus = []
disagreements = []

for eid, g in gold_data.items():
    gold_label = g.get("gold_label") or g.get("label")
    k1_p = k1_data[eid]["predicted_label"]
    k2_p = k2_data[eid]["pred_label"]
    
    if k1_p == k2_p:
        consensus.append({
            "example_id": eid,
            "gold": gold_label,
            "pred": k1_p,
            "correct": (k1_p == gold_label)
        })
    else:
        disagreements.append({
            "example_id": eid,
            "gold": gold_label,
            "k1_pred": k1_p,
            "k1_correct": (k1_p == gold_label),
            "k2_pred": k2_p,
            "k2_correct": (k2_p == gold_label)
        })

print(f"======================================================================")
print(f"GUNCEL K1 ve K2 (100% KAPSAMALI YENI ATOMIZER) KARSILASTIRMASI")
print(f"======================================================================")
print(f"Toplam Vaka: {total}")
print(f"Konsensüs (K1 == K2): {len(consensus)} / {total} (%{len(consensus)/total*100:.2f})")
cons_correct = sum(1 for c in consensus if c["correct"])
print(f"Konsensüs Doğruluğu: {cons_correct} / {len(consensus)} (%{cons_correct/len(consensus)*100:.2f})")
print(f"Uyuşmazlık (K1 != K2): {len(disagreements)} / {total} (%{len(disagreements)/total*100:.2f})")
k1_dis_corr = sum(1 for d in disagreements if d["k1_correct"])
k2_dis_corr = sum(1 for d in disagreements if d["k2_correct"])
oracle_corr = sum(1 for d in disagreements if d["k1_correct"] or d["k2_correct"])
print(f"Uyuşmazlıkta K1 Doğru: {k1_dis_corr} / {len(disagreements)} (%{k1_dis_corr/len(disagreements)*100:.2f})")
print(f"Uyuşmazlıkta K2 Doğru: {k2_dis_corr} / {len(disagreements)} (%{k2_dis_corr/len(disagreements)*100:.2f})")
print(f"Uyuşmazlıkta Oracle Doğru (en az biri doğru): {oracle_corr} / {len(disagreements)} (%{oracle_corr/len(disagreements)*100:.2f})")
print(f"Toplam Hibrit Oracle Tavanı: {cons_correct + oracle_corr} / {total} (%{(cons_correct + oracle_corr)/total*100:.2f})")
print(f"======================================================================")
