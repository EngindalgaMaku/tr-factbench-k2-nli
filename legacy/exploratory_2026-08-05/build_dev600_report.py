#!/usr/bin/env python3
"""
dev600_stress atom pipeline sonuclarini detayli MD raporuna donusturur.
Her ornek icin: claim, context ozeti, gold_label, atomlar, atom NLI,
final tahmin, dogru/yanlis durumu.
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PRED_FILE    = Path("nli/outputs/atom_dev600_stress/predictions.jsonl")
SOURCE_FILE  = Path("tr-factbench-v0.1.0-preview/data/evaluation/preview_v0.1/dev_stress.jsonl")
OUT_FILE     = Path("nli/outputs/atom_dev600_stress/detailed_report.md")

LABELS4 = ["supported", "partially_supported", "contradicted", "unverifiable"]

CMAP = {
    "entailment":    "supported",
    "neutral":       "unverifiable",
    "contradiction": "contradicted",
}

NLI_EMOJI = {
    "entailment":    "ENT",
    "neutral":       "NEU",
    "contradiction": "CON",
}

LABEL_EMOJI = {
    "supported":          "SUPPORTED",
    "partially_supported":"PARTIAL",
    "contradicted":       "CONTRADICTED",
    "unverifiable":       "UNVERIFIABLE",
}


def atom_rule_4class(atom_labels):
    if not atom_labels:
        return None
    has_ent = "entailment"    in atom_labels
    has_neu = "neutral"       in atom_labels
    has_con = "contradiction" in atom_labels
    if has_ent and (has_neu or has_con):
        return "partially_supported"
    if has_con:
        return "contradicted"
    if has_ent:
        return "supported"
    return "unverifiable"


recs = [json.loads(l) for l in open(PRED_FILE, encoding="utf-8") if l.strip()]

# Source'dan context'i yükle (example_id üzerinden)
ctx_map = {}
if SOURCE_FILE.exists():
    for l in open(SOURCE_FILE, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            ctx_map[r["example_id"]] = r.get("context", "")

# Ozet istatistik
from collections import Counter, defaultdict
total = len(recs)
correct = 0
by_label = defaultdict(lambda: {"total": 0, "correct": 0})

lines = []
lines.append("# DEV600-STR Atom Pipeline Detaylı Rapor\n")
lines.append(f"**Toplam örnek:** {total}  \n")
lines.append(f"**Model:** XLM-RoBERTa-Large-XNLI (zero-shot NLI)  \n")
lines.append(f"**Atomizer:** Gemma-4-E2B-IT fine-tuned (V3)  \n\n")
lines.append("---\n\n")

for i, r in enumerate(recs, 1):
    gold   = r["gold_label"]
    atoms  = r.get("atoms", [])
    atom_nli = r.get("atom_nli", [])
    claim_nli_label = r["claim_nli"]["label"]
    atom_labels = [a["label"] for a in atom_nli]
    
    final_pred = atom_rule_4class(atom_labels) if atom_labels else CMAP.get(claim_nli_label, "unverifiable")
    is_correct = (final_pred == gold)
    
    if is_correct:
        correct += 1
    by_label[gold]["total"] += 1
    if is_correct:
        by_label[gold]["correct"] += 1
    
    status = "✓ DOGRU" if is_correct else "✗ YANLIS"
    
    lines.append(f"## Örnek {i} — `{status}`\n")
    lines.append(f"**Domain:** {r.get('domain', '?')}  \n")
    lines.append(f"**Gold Label:** `{gold}`  \n")
    lines.append(f"**Tahmin:** `{final_pred}`  \n\n")
    
    lines.append(f"**Claim:**\n> {r['claim']}\n\n")
    
    # Context özeti (ilk 200 karakter varsa)
    # context yok bu veri setinde, sadece context_len
    context_text = ctx_map.get(r.get("example_id", ""), "")
    if context_text:
        lines.append(f"**Bağlam:**\n> {context_text}\n\n")
    else:
        lines.append(f"**Bağlam uzunluğu:** {r.get('context_len', '?')} karakter\n\n")
    
    lines.append(f"**Claim-level NLI:** `{claim_nli_label}` → `{CMAP.get(claim_nli_label,'?')}`  \n")
    conf = r["claim_nli"].get("confidence", 0)
    lines.append(f"**Güven:** {conf:.3f}  \n\n")
    
    if atoms:
        lines.append("**Atomlar ve NLI Kararları:**\n\n")
        lines.append("| # | Atom | NLI Kararı | Güven |\n")
        lines.append("|---|------|-----------|-------|\n")
        for j, (atom, anli) in enumerate(zip(atoms, atom_nli), 1):
            nli_lbl = anli["label"]
            nli_conf = anli.get("confidence", 0)
            lines.append(f"| {j} | {atom[:90]} | `{nli_lbl}` | {nli_conf:.3f} |\n")
        lines.append("\n")
        lines.append(f"**Atom karar kuralı:** `{' + '.join(atom_labels)}` → **`{final_pred}`**\n\n")
    else:
        lines.append("**Atomizer:** Geçersiz/boş — claim-level fallback kullanıldı  \n\n")
    
    lines.append("---\n\n")

# Özet
lines.insert(4, f"**Doğruluk:** {correct}/{total} ({correct/total*100:.1f}%)  \n\n")
lines.insert(5, "**Sınıf bazlı doğruluk:**\n\n")
lines.insert(6, "| Sınıf | Doğru | Toplam | Oran |\n")
lines.insert(7, "|-------|-------|--------|------|\n")
for lbl in LABELS4:
    v = by_label[lbl]
    t, c = v["total"], v["correct"]
    lines.insert(8 + LABELS4.index(lbl),
                 f"| {lbl} | {c} | {t} | {c/t*100:.1f}% |\n")
lines.insert(12, "\n---\n\n")

out_text = "".join(lines)
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(out_text)

print(f"Rapor yazildi: {OUT_FILE}")
print(f"Toplam: {total}  Dogru: {correct}  Acc: {correct/total*100:.1f}%")
for lbl in LABELS4:
    v = by_label[lbl]
    print(f"  {lbl}: {v['correct']}/{v['total']}")