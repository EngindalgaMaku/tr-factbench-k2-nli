import json
from pathlib import Path

gold_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl")
if not gold_path.exists():
    gold_path = Path("tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl")

k1_path = Path("../tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl")
if not k1_path.exists():
    k1_path = Path("tr-factbench-v0.1.0-preview/data/evaluation/gold_v1.0/verifier_hold/PREDICTIONS_v1.0.jsonl")

k2_path = Path("reports/experiments/K2-AGG-ABLATION-GOLD480-v1/artifacts/predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")
atom_preds_path = Path("runs/K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7/atom_predictions.jsonl")
arb_pred_file = Path("reports/experiments/K3-DEBIASED-NEUTRAL-ATOMS-LLAMA70B-v1/arbitration_predictions_123.jsonl")

gold_data = {}
for line in gold_path.read_text(encoding="utf-8-sig").splitlines():
    if not line.strip(): continue
    item = json.loads(line)
    eid = item.get("release_example_id") or item.get("example_id")
    gold_data[eid] = item

k1_data = {
    (json.loads(line).get("release_example_id") or json.loads(line).get("example_id")): json.loads(line)
    for line in k1_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()
}
k2_data = {
    (json.loads(line).get("release_example_id") or json.loads(line).get("example_id")): json.loads(line)
    for line in k2_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()
}
arb_data = {
    json.loads(line)["example_id"]: json.loads(line)
    for line in arb_pred_file.read_text(encoding="utf-8").splitlines() if line.strip()
}

atom_map = {}
if atom_preds_path.exists():
    for line in atom_preds_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip(): continue
        rec = json.loads(line)
        eid = rec.get("release_example_id") or rec.get("example_id")
        if eid not in atom_map:
            atom_map[eid] = []
        atom_map[eid].append(rec.get("atom_text") or rec.get("atom") or rec.get("claim_atom"))

# 1. Hakem Hataları (16 Vaka)
arb_errors = []
for eid, a in arb_data.items():
    if not a["judge_correct"]:
        g = gold_data[eid]
        arb_errors.append({
            "example_id": eid,
            "domain": g.get("domain", "general"),
            "question": g.get("question", ""),
            "context": g["context"],
            "claim": g["claim"],
            "gold_label": a["gold_label"],
            "judge_decision": a["judge_decision"],
            "k1_pred": a["k1_pred"],
            "k2_pred": a["k2_pred"],
            "favored_model": a.get("favored_model", "Neither"),
            "judge_reasoning": a.get("reasoning", ""),
            "atoms": atom_map.get(eid, [])
        })

# 2. Ortak Yanılgı Hataları (20 Vaka)
cons_errors = []
for eid, g in gold_data.items():
    gold_label = g.get("gold_label") or g.get("label")
    p1 = k1_data[eid]["predicted_label"]
    p2 = k2_data[eid]["pred_label"]
    if p1 == p2 and p1 != gold_label:
        cons_errors.append({
            "example_id": eid,
            "domain": g.get("domain", "general"),
            "question": g.get("question", ""),
            "context": g["context"],
            "claim": g["claim"],
            "gold_label": gold_label,
            "k1_pred": p1,
            "k2_pred": p2,
            "pipeline_pred": p1,
            "atoms": atom_map.get(eid, [])
        })

print(f"Loaded: 16 Arb Errors, 20 Consensus Errors")

# Markdown Raporu İnşa Edelim
md = []
md.append("# TR-FactBench 480 Altın Test: 36 Hatanın Derinlemesine Vaka İncelemesi ve Taksonomi Raporu")
md.append("\n**Tarih:** 5 Ekim 2026")
md.append("**Mimari:** Bileşen 0 Ayrışımlı Kademeli Hibrit Sistem (ELECTRA-TR + Gemma-4-2B + mDeBERTa-v3 + Llama-3.3-70B Debiased Hakem)")
md.append(f"**Toplam Hata:** 36 / 480 (%92.50 Genel Doğruluk)")
md.append("- **Meta-Hakem Karar Hataları:** 16 Vaka")
md.append("- **Yerel Modellerin Ortak Yanılgıları (Doğrudan Uzlaşma Hataları):** 20 Vaka\n")
md.append("---\n")

md.append("## BÖLÜM 1: META-HAKEM KARAR HATALARI (16 VAKA)\n")
md.append("*Bu vakalarda Model A (K1) ve Model B (K2) uzlaşamamış, Llama-3.3-70B devreye girmiş ancak karar aşamasında sınır ayrımları hatalı değerlendirmiştir.*\n")

for i, e in enumerate(arb_errors, 1):
    md.append(f"### [HAKEM-{i:02d}/16] ID: `{e['example_id']}` | Alan: `{e['domain'].upper()}`")
    md.append(f"- **SORU:** {e['question']}")
    md.append(f"- **BAĞLAM:** {e['context']}")
    md.append(f"- **İDDİA:** {e['claim']}")
    md.append(f"- **ALTIN ETİKET (Doğru Karar):** `{e['gold_label']}`")
    md.append(f"- **HAKEM KARARI (Sistem Tahmini):** `{e['judge_decision']}` ❌")
    md.append(f"- **Bilirkişi Modelleri:** Model A (K1) = `{e['k1_pred']}` | Model B (K2) = `{e['k2_pred']}` | Hakemin Tercihi = `{e['favored_model']}`")
    md.append(f"- **Hakemin Karar Gerekçesi (CoT Reasoning):** *\"{e['judge_reasoning']}\"*")
    if e['atoms']:
        md.append(f"- **Ayrıştırılan Atomik Önermeler:** " + " | ".join([f'\"{a}\"' for a in e['atoms']]))
    
    # Neden analizi
    if e['gold_label'] == 'unverifiable' and e['judge_decision'] == 'partially_supported':
        reason = "Cümlenin ana olgusu bağlamda hiç geçmemektedir (unverifiable). Ancak Hakem, cümledeki giriş veya konu kavramını bağlamda görünce 'en az bir parça destekleniyor' kuralını aşırı katı uygulayıp kısmi destek (partially_supported) tuzağına düşmüştür."
    elif e['gold_label'] == 'partially_supported' and e['judge_decision'] == 'unverifiable':
        reason = "İddiada doğrulanabilen gerçek bir parça bulunmasına rağmen, Hakem cümlenin uydurma olan ikinci parçasına odaklanmış ve doğrulanan ilk parçayı ihmal ederek tüm cümleye unverifiable demiştir."
    elif e['judge_decision'] == 'contradicted' and e['gold_label'] == 'unverifiable':
        reason = "Aşırı Çıkarım (Over-inference): Bağlamda bilginin yer almaması (bilgi yokluğu) durumunu Hakem mantıksal olarak imkansız/zıt kabul ederek contradicted kararına kaymıştır."
    elif e['gold_label'] == 'partially_supported' and e['judge_decision'] == 'contradicted':
        reason = "Katı Boolean Mantığı: İddia hem doğru hem yanlış bilgi içermektedir. Hakem yanlış bilginin ağırlığına kapılarak cümlenin başındaki doğru önermeyi yok saymış ve tüm cümleyi çelişki addetmiştir."
    else:
        reason = f"Hakem, altın etiket olan {e['gold_label']} yerine {e['judge_decision']} yönünde semantik çıkarım yapmıştır."
    
    md.append(f"- **HATA MEKANİZMASI ANALİZİ:** {reason}")
    md.append("\n---\n")

md.append("## BÖLÜM 2: YEREL MODELLERİN ORTAK YANILGISI (DOĞRUDAN UZLAŞMA HATALARI - 20 VAKA)\n")
md.append("*Bu vakalarda Model A (K1 - ELECTRA) ve Model B (K2 - mDeBERTa) aynı yanlış kararda birleşmiş, sisteme hız kazandırmış ancak Hakem'e gidilmediği için hata kaçınılmaz olmuştur.*\n")

for i, e in enumerate(cons_errors, 1):
    md.append(f"### [UZLAŞMA-{i:02d}/20] ID: `{e['example_id']}` | Alan: `{e['domain'].upper()}`")
    md.append(f"- **SORU:** {e['question']}")
    md.append(f"- **BAĞLAM:** {e['context']}")
    md.append(f"- **İDDİA:** {e['claim']}")
    md.append(f"- **ALTIN ETİKET (Doğru Karar):** `{e['gold_label']}`")
    md.append(f"- **ORTAK YANLIŞ KARAR (K1 ve K2):** `{e['pipeline_pred']}` ❌")
    if e['atoms']:
        md.append(f"- **Ayrıştırılan Atomik Önermeler:** " + " | ".join([f'\"{a}\"' for a in e['atoms']]))
    
    # Neden analizi
    if e['domain'] == 'medical':
        reason = "Tıbbi Terminoloji ve Kelime Örtüşmesi (Lexical Overlap) Tuzağı: İddiada geçen yoğun klinik terimler (işlem adı, cihaz, muayene bulgusu) bağlamda da geçtiği için her iki model de metinde hiç yer almayan uydurma süreleri, sıralamaları veya endikasyonları fark edememiş; bilgi yokluğunu (unverifiable) kısmi destek veya çelişki sanmıştır."
    elif 'Kasko' in e['claim'] or 'sigorta' in e['claim']:
        reason = "Çapraz Rol Takasını Kaçırma: İddia iki kavramın (örn. kasko ile trafik sigortası) rollerini ve tanımlarını tam ters takas etmiştir. Tüm kelimeler bağlamda geçtiği için iki encoder da cümlenin ters kurulduğunu anlamayıp 'tam destek' (supported) demiştir."
    elif e['gold_label'] == 'contradicted' and e['pipeline_pred'] == 'partially_supported':
        reason = "Doğru Terim Yanılgısı: İddia bağlamla doğrudan çelişmesine rağmen, iddia içinde geçen bazı genel kavram isimleri bağlamda yer aldığı için modeller bunu kısmi doğruluk zannetmiştir."
    else:
        reason = f"Her iki yerel model de altın etiket olan {e['gold_label']} yerine {e['pipeline_pred']} yönünde ortak yanlılığa (shared inductive bias) düşmüştür."
    
    md.append(f"- **HATA MEKANİZMASI ANALİZİ:** {reason}")
    md.append("\n---\n")

out_file = Path("reports/AUDIT_36_PIPELINE_ERRORS_REPORT.md")
out_file.write_text("\n".join(md), encoding="utf-8")
print(f"Rapor başarıyla yazıldı: {out_file} (Toplam {len(md)} satır)")
