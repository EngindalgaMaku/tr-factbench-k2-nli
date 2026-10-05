import json
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix, matthews_corrcoef

LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]

gold_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl")
k1_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl")
k2_path = Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")
judge_path = Path("reports/experiments/K3-COT-REASONING-FIRST-LLAMA70B-v1/arbitration_predictions_120.jsonl")

gold_data = {}
for line in gold_path.read_text(encoding="utf-8-sig").splitlines():
    if not line.strip(): continue
    item = json.loads(line)
    eid = item.get("release_example_id") or item.get("example_id")
    gold_data[eid] = item

k1_data = {json.loads(line).get("release_example_id") or json.loads(line).get("example_id"): json.loads(line) for line in k1_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()}
k2_data = {json.loads(line).get("release_example_id") or json.loads(line).get("example_id"): json.loads(line) for line in k2_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()}
judge_data = {json.loads(line)["example_id"]: json.loads(line) for line in judge_path.read_text(encoding="utf-8").splitlines() if line.strip()}

y_true = []
y_k1 = []
y_k2 = []
y_hybrid = []

consensus_count = 0
arbitration_count = 0

for eid, g in gold_data.items():
    gold = g.get("gold_label") or g.get("label")
    k1_p = k1_data[eid]["predicted_label"]
    k2_p = k2_data[eid]["pred_label"]
    
    y_true.append(gold)
    y_k1.append(k1_p)
    y_k2.append(k2_p)
    
    if k1_p == k2_p:
        y_hybrid.append(k1_p)
        consensus_count += 1
    else:
        judge_p = judge_data[eid]["judge_decision"]
        y_hybrid.append(judge_p)
        arbitration_count += 1

print("="*75)
print("TR-FACTBENCH 480 GOLD TEST - NIHAI BILIMSEL SONUCLAR (100% KAPSAMALI K2)")
print("="*75)
print(f"Toplam Vaka Sayısı                     : {len(y_true)}")
print(f"Konsensüs Sayısı (Doğrudan Uzlaşma)    : {consensus_count} / {len(y_true)} (%{consensus_count/len(y_true)*100:.2f})")
print(f"Hakeme Giden Uyuşmazlık Sayısı         : {arbitration_count} / {len(y_true)} (%{arbitration_count/len(y_true)*100:.2f})")
print("-" * 75)
print(f"K1 Tek Başına (ELECTRA-TR) Doğruluk    : {sum(a==b for a,b in zip(y_true, y_k1))}/{len(y_true)} (%{accuracy_score(y_true, y_k1)*100:.2f}) | Macro-F1: {f1_score(y_true, y_k1, labels=LABELS, average='macro'):.4f} | MCC: {matthews_corrcoef(y_true, y_k1):.4f}")
print(f"K2 Tek Başına (Gemma-2B+mDeBERTa)      : {sum(a==b for a,b in zip(y_true, y_k2))}/{len(y_true)} (%{accuracy_score(y_true, y_k2)*100:.2f}) | Macro-F1: {f1_score(y_true, y_k2, labels=LABELS, average='macro'):.4f} | MCC: {matthews_corrcoef(y_true, y_k2):.4f}")
print(f"Meta-Hakem (Llama-70B CoT) Uyuşmazlıkta: {sum(judge_data[e]['judge_correct'] for e in judge_data)}/{len(judge_data)} (%{sum(judge_data[e]['judge_correct'] for e in judge_data)/len(judge_data)*100:.2f})")
print("-" * 75)
print(f"KADEMELI HIBRIT MİMARİ (Önerilen)      : {sum(a==b for a,b in zip(y_true, y_hybrid))}/{len(y_true)} (%{accuracy_score(y_true, y_hybrid)*100:.2f}) | Macro-F1: {f1_score(y_true, y_hybrid, labels=LABELS, average='macro'):.4f} | MCC: {matthews_corrcoef(y_true, y_hybrid):.4f}")
print("="*75)
print("\nKademeli Hibrit Mimari Sınıflandırma Raporu:")
print(classification_report(y_true, y_hybrid, labels=LABELS, digits=4))
