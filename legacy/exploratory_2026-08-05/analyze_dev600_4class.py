#!/usr/bin/env python3
"""
4-sinifli K2 atom pipeline analizi.
TR-FactBench sinifları: supported, partially_supported, contradicted, unverifiable

NLI→4sinif eslemesi (atom worst-case):
  - Tum atomlar entailment  → supported
  - Herhangi atom contradiction var → contradicted
  - Tum atomlar neutral     → unverifiable
  - Karisik (entailment + neutral) → partially_supported

Karsilastirma: K1 ELECTRA-TR DEV600-STR macro F1 = 0.8782
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PRED_FILE = Path("nli/outputs/atom_dev600_stress/predictions.jsonl")
LABELS4 = ["supported", "partially_supported", "contradicted", "unverifiable"]

# NLI 3-sinif → 4-sinif kurallar (claim-level)
# unverifiable = neutral, contradicted = contradiction, supported = entailment
# partially_supported: atom-level'da yakalanacak

CLAIM_MAP = {
    "entailment":    "supported",
    "neutral":       "unverifiable",
    "contradiction": "contradicted",
}


def atom_rule_4class(atom_labels: list[str]) -> str:
    """
    Atom listesinden 4-sinif karar kuralı:
    - Hepsi entailment → supported
    - Hepsi contradiction → contradicted
    - Hepsi neutral → unverifiable
    - Karisik (entailment + neutral)  → partially_supported
    - Karisik (entailment + contradiction) → partially_supported
    - Karisik (neutral + contradiction) → contradicted (baskın sinyal)
    """
    if not atom_labels:
        return None
    has_ent  = "entailment"    in atom_labels
    has_neu  = "neutral"       in atom_labels
    has_con  = "contradiction" in atom_labels

    # Karisik durum: entailment + (neutral veya contradiction) = partially_supported
    if has_ent and (has_neu or has_con):
        return "partially_supported"
    if has_con:
        return "contradicted"
    if has_ent:
        return "supported"
    return "unverifiable"


def macro_f1_4class(gold, pred, labels=LABELS4):
    from sklearn.metrics import classification_report
    report = classification_report(gold, pred, labels=labels, output_dict=True, zero_division=0)
    return report["macro avg"]["f1-score"], report["accuracy"], {lbl: report[lbl] for lbl in labels if lbl in report}


recs = [json.loads(l) for l in open(PRED_FILE, encoding="utf-8") if l.strip()]
n = len(recs)
print(f"Toplam: {n} ornek\n")

gold = [r["gold_label"] for r in recs]

# --- 1. Claim-level 3→4 sinif
claim_pred_4 = [CLAIM_MAP.get(r["claim_nli"]["label"], "unverifiable") for r in recs]
mf1, acc, per_cls = macro_f1_4class(gold, claim_pred_4)
print(f"[CLAIM-LEVEL 3→4 sinif eslemesi]")
print(f"  Macro-F1: {mf1*100:.2f}%  Accuracy: {acc*100:.2f}%")
for lbl in LABELS4:
    c = per_cls.get(lbl, {})
    print(f"  {lbl:25s}: F1={c.get('f1-score',0)*100:.1f}  P={c.get('precision',0)*100:.1f}  R={c.get('recall',0)*100:.1f}  n={int(c.get('support',0))}")

# Gold dagilimi → claim pred
print(f"\n  Gold → Claim-pred dagilimi:")
g2p = defaultdict(Counter)
for g, p in zip(gold, claim_pred_4):
    g2p[g][p] += 1
for lbl in LABELS4:
    print(f"  {lbl:25s}: {dict(g2p[lbl])}")

print()

# --- 2. Atom-level kural (atom_rule_4class)
atom_pred_4 = []
atom_pred_valid = []
for r in recs:
    atom_labels = [a["label"] for a in r.get("atom_nli", [])]
    if atom_labels:
        atom_pred_4.append(atom_rule_4class(atom_labels))
        atom_pred_valid.append(True)
    else:
        # Atomizer calisabildiyse claim-level'a fallback
        atom_pred_4.append(CLAIM_MAP.get(r["claim_nli"]["label"], "unverifiable"))
        atom_pred_valid.append(False)

mf1_a, acc_a, per_cls_a = macro_f1_4class(gold, atom_pred_4)
print(f"[ATOM-LEVEL kural tabanlı (worst-case+partial)]")
print(f"  Macro-F1: {mf1_a*100:.2f}%  Accuracy: {acc_a*100:.2f}%")
for lbl in LABELS4:
    c = per_cls_a.get(lbl, {})
    print(f"  {lbl:25s}: F1={c.get('f1-score',0)*100:.1f}  P={c.get('precision',0)*100:.1f}  R={c.get('recall',0)*100:.1f}  n={int(c.get('support',0))}")

# Gold dagilimi → atom pred
print(f"\n  Gold → Atom-pred dagilimi:")
g2a = defaultdict(Counter)
for g, p in zip(gold, atom_pred_4):
    g2a[g][p] += 1
for lbl in LABELS4:
    print(f"  {lbl:25s}: {dict(g2a[lbl])}")

# Atomizer kac ornegi atomize edebildi
n_atomized = sum(atom_pred_valid)
avg_atoms  = sum(len(r.get("atom_nli",[])) for r in recs) / n
print(f"\n  Atomize edilen: {n_atomized}/{n}  Ort atom: {avg_atoms:.2f}")

print(f"\n{'='*60}")
print(f"  K1 ELECTRA DEV600-STR macro F1 : 87.82%")
print(f"  K2 Claim-level macro F1        : {mf1*100:.2f}%")
print(f"  K2 Atom-level macro F1         : {mf1_a*100:.2f}%")
print(f"{'='*60}")