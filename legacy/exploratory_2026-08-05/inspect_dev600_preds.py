import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

recs = [json.loads(l) for l in open("nli/outputs/atom_dev600_stress/predictions.jsonl", encoding="utf-8") if l.strip()]
print("Toplam:", len(recs))
print("Keys:", list(recs[0].keys()))
print()

print("Gold dagilimi:", dict(Counter(r["gold_label"] for r in recs)))
print()
print("Claim NLI dagilimi:", dict(Counter(r["claim_nli"]["label"] for r in recs)))
print()

# gold_nli3 (pipeline'in atadigi)
print("gold_nli3 dagilimi:", dict(Counter(r["gold_nli3"] for r in recs)))
print()

# Unverifiable olanlarda claim NLI ne diyor?
unv = [r for r in recs if r["gold_label"] == "unverifiable"]
print(f"Unverifiable ornekler ({len(unv)}):")
print("  Claim NLI:", dict(Counter(r["claim_nli"]["label"] for r in unv)))
print("  gold_nli3:", dict(Counter(r["gold_nli3"] for r in unv)))
print()

# Partially supported orneklerde
ps = [r for r in recs if r["gold_label"] == "partially_supported"]
print(f"Partially_supported ornekler ({len(ps)}):")
print("  Claim NLI:", dict(Counter(r["claim_nli"]["label"] for r in ps)))
print("  Atom ortalama:", sum(len(r.get("atom_nli",[])) for r in ps)/len(ps) if ps else 0)
print()

# Ilk 3 ornek detay
for r in recs[:3]:
    print(f"gold={r['gold_label']}  gold_nli3={r['gold_nli3']}  claim_nli={r['claim_nli']['label']}")
    print(f"  claim: {r['claim'][:100]}")
    atom_labels = [a['label'] for a in r.get('atom_nli', [])]
    print(f"  atoms: {atom_labels}")
    print()