import json, sys
from collections import Counter
from sklearn.metrics import classification_report
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

recs = [json.loads(l) for l in open("nli/outputs/atom_dev600_stress/predictions.jsonl", encoding="utf-8") if l.strip()]

CMAP = {"entailment": "supported", "neutral": "unverifiable", "contradiction": "contradicted"}
LABELS4 = ["supported", "partially_supported", "contradicted", "unverifiable"]

# 3 sinif (partially_supported haric)
recs3 = [r for r in recs if r["gold_label"] != "partially_supported"]
gold3 = [r["gold_label"] for r in recs3]
pred3 = [CMAP[r["claim_nli"]["label"]] for r in recs3]

rep = classification_report(gold3, pred3, labels=["supported","contradicted","unverifiable"], output_dict=True, zero_division=0)
print(f"3-sinif (partially_supported haric, {len(recs3)} ornek):")
print(f"  Macro-F1: {rep['macro avg']['f1-score']*100:.2f}%  Acc: {rep['accuracy']*100:.2f}%")
for lbl in ["supported","contradicted","unverifiable"]:
    r2 = rep[lbl]
    print(f"  {lbl:20s}: F1={r2['f1-score']*100:.1f}  P={r2['precision']*100:.1f}  R={r2['recall']*100:.1f}  n={int(r2['support'])}")

print()
print("Ham confusion (gold -> claim NLI):")
g2p = {}
for r in recs:
    g = r["gold_label"]
    p = r["claim_nli"]["label"]
    g2p.setdefault(g, Counter())[p] += 1
for lbl in LABELS4:
    if lbl in g2p:
        print(f"  gold={lbl}: {dict(g2p[lbl])}")

print()
print("NLI model daha once ne verdi?")
print("  Pilot test (300 ornek): Macro-F1=%94.67 (kayitli)")
print("  Bu veri (600 ornek, dev_stress): hicbir esitlik yok - tamamen farkli siniflar")
print()
print("KRITIK: Eski NLI test seti 3 sinif (entailment/neutral/contradiction)")
print("Yeni veri seti 4 sinif (supported/partially_supported/contradicted/unverifiable)")
print("Karsilastirma yapilamazdi - farkli gorev!")