#!/usr/bin/env python3
"""
97_ap6_preregistered_analysis.py — AP6 ön kayıtlı analizi (protokol §1, §8; v1.2, v1.5, v1.6, v1.8).

Bu betik etiketler sistem tahminleriyle hiç karşılaştırılmadan yazılmış ve çalıştırılmadan önce commit edilmiştir.
Bir kez çalıştırılır; sonuçlar görüldükten sonra yapılan her değişiklik "post-hoc" olarak ayrıca raporlanır (§9).

Tanımlar
- İnsan etiketi: labels_A.jsonl, her madde için son kayıt (uzlaşma dahil). 858 cümlenin tamamı (tam sayım, v1.5).
- Değerlendirme kümesi: insanın çekimser OLMADIĞINI söylediği cümleler (v1.2). Çekimser cümleler ayrıca betimlenir.
- İkili görev: pozitif = halüsinasyon = insan etiketi supported DEĞİL. Sistem pozitifi = sistem etiketi supported değil.
  S1 yanlış alarm oranı = YP / (insan supported).  S2 = pozitif sınıf için kesinlik, duyarlılık, F1.
- 4 sınıf: yalnızca betimsel karışıklık matrisi, doğruluk ve Macro-F1 (§8: ana ölçüt değildir).
- S3: model ve alan bazında halüsinasyon oranı (değerlendirme kümesinde insan etiketi supported değil), sınıf ve hata türü dağılımı,
  model ve soru türü bazında çekimserlik oranı.
- S4: K1, K2, hibrit P0 / PA / PB, tek başına Gemma-4-26B (örneksiz) ve GPT-4.1-mini (8 örnek) aynı ölçütlerle; eşleştirilmiş
  karşılaştırmalar: ikili doğruluk üzerinde kesin McNemar testi ve F1 farkı için bootstrap GA.
- Maliyet: büyük dil modeli çağrı oranı (858 cümlenin tamamında; sistem insan çekimserlik kararını bilmez).
  P0 = K1 ≠ K2; PA = P0 + uzlaşılan etiketi partially_supported/contradicted olanlar; PB = P0 + bunların yalnızca tıp alanındakiler.
- GA: soru düzeyinde küme bootstrap, 10.000 tekrar, seed 42 (v1.6). Model bazındaki oranlarda yalnızca o modelin cümleleri.
- K2'nin karar veremediği cümle (atomizer hatası, v1.4) K2 ölçütlerinden çıkarılır ve sayısı raporlanır.
- Alt kümeler (betimsel): soru türü (answerable / multi_fact / partial), geri göndermeli cümleler (v1.3).
Çıktı: reports/AP6_RESULTS_v1.{md,json}
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
AP6 = ROOT / "data" / "ap6"
REP = ROOT / "reports"
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
SYSTEMS = ["k1", "k2", "hybrid_P0", "hybrid_PA", "hybrid_PB", "gemma26b_zero_shot", "gpt41mini_few_shot_8"]
SYS_TR = {"k1": "K1", "k2": "K2", "hybrid_P0": "Hibrit P0", "hybrid_PA": "Hibrit PA", "hybrid_PB": "Hibrit PB",
          "gemma26b_zero_shot": "Gemma-4-26B (örneksiz)", "gpt41mini_few_shot_8": "GPT-4.1-mini (8 örnek)"}
MODEL_TR = {"mistralai/ministral-3b-2512": "Ministral-3B", "qwen/qwen3-8b": "Qwen3-8B", "deepseek/deepseek-v4-pro": "DeepSeek-V4"}
PAIRS = [("hybrid_P0", "k1"), ("hybrid_P0", "k2"), ("hybrid_P0", "gemma26b_zero_shot"),
         ("hybrid_P0", "gpt41mini_few_shot_8"), ("hybrid_PA", "hybrid_P0"), ("hybrid_PB", "hybrid_P0")]
N_BOOT, SEED = 10_000, 42


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load() -> list[dict]:
    key = {r["item_id"]: r["example_id"] for r in jl(AP6 / "annotation" / "internal" / "item_key_v1.jsonl")}
    lab = {}
    for r in jl(AP6 / "annotation" / "labels_A.jsonl"):
        lab[r["item_id"]] = r
    sent = {r["sentence_id"]: r for r in jl(AP6 / "generation" / "sentences.jsonl")}
    pred = {r["example_id"]: r for r in jl(AP6 / "verifier" / "system_predictions_v1.jsonl")}
    assert len(key) == len(lab) == len(pred) == 858, (len(key), len(lab), len(pred))
    rows = []
    for iid, ex in key.items():
        h, p, s = lab[iid], pred[ex], sent[ex]
        rows.append({"item_id": iid, "example_id": ex, "qid": ex.split("__")[0], "domain": p["domain"],
                     "model": MODEL_TR[p["model"]], "qtype": s["question_type"],
                     "back_ref": str(s["back_reference"]) == "True",
                     "auto_abst": bool(p["abstention_flag"]),
                     "abst": h["abstention"] == "yes", "gold": h["label"], "err": h["error_type"],
                     "route": p["route"], **{k: p[k] for k in SYSTEMS}})
    return rows


def binary(rs: list[dict], sysk: str) -> dict:
    tp = fp = fn = tn = 0
    for r in rs:
        y, s = r["gold"] != "supported", r[sysk] != "supported"
        tp += y and s; fp += (not y) and s; fn += y and not s; tn += (not y) and not s
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if tp else 0.0
    return {"n": len(rs), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "false_alarm": fp / (fp + tn) if fp + tn else float("nan"), "precision": prec, "recall": rec, "f1": f1}


def four(rs: list[dict], sysk: str) -> dict:
    cm = {g: Counter() for g in LABELS}
    for r in rs:
        cm[r["gold"]][r[sysk]] += 1
    f1s = []
    for c in LABELS:
        tp = cm[c][c]
        fp = sum(cm[g][c] for g in LABELS if g != c)
        fn = sum(cm[c][p] for p in LABELS if p != c)
        f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    return {"accuracy": sum(cm[c][c] for c in LABELS) / len(rs), "macro_f1": sum(f1s) / 4,
            "per_class_f1": dict(zip(LABELS, f1s)), "confusion": {g: dict(cm[g]) for g in LABELS}}


def cluster_boot(rs: list[dict], stat, n=N_BOOT, seed=SEED):
    by_q = defaultdict(list)
    for r in rs:
        by_q[r["qid"]].append(r)
    qs = sorted(by_q)
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sample = [r for q in (rng.choice(qs) for _ in qs) for r in by_q[q]]
        v = stat(sample)
        if v == v:
            vals.append(v)
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]


def mcnemar(rs: list[dict], a: str, b: str) -> dict:
    ca = [(r[a] != "supported") == (r["gold"] != "supported") for r in rs]
    cb = [(r[b] != "supported") == (r["gold"] != "supported") for r in rs]
    only_a = sum(x and not y for x, y in zip(ca, cb))
    only_b = sum(y and not x for x, y in zip(ca, cb))
    p = binomtest(only_a, only_a + only_b, 0.5).pvalue if only_a + only_b else 1.0
    return {"only_a_correct": only_a, "only_b_correct": only_b, "p_exact": p}


def call_rates(rows: list[dict]) -> dict:
    p0 = pa = pb = 0
    for r in rows:
        dis = r["route"] != "consensus" and r["route"] != "k2_missing_k1"
        cons_flag = r["route"] == "consensus" and r["k1"] in ("partially_supported", "contradicted")
        p0 += dis
        pa += dis or cons_flag
        pb += dis or (cons_flag and r["domain"] == "medical")
    n = len(rows)
    return {"n": n, "P0": p0 / n, "PA": pa / n, "PB": pb / n}


def main() -> None:
    rows = load()
    ev = [r for r in rows if not r["abst"]]
    out = {"inputs": {p: sha(AP6 / p) for p in ["annotation/labels_A.jsonl", "annotation/internal/item_key_v1.jsonl",
                                                 "verifier/system_predictions_v1.jsonl", "generation/sentences.jsonl"]},
           "n_sentences": len(rows), "n_abstention_human": len(rows) - len(ev), "n_eval": len(ev)}

    # S3 — insan etiketlerinden oranlar
    hal = lambda rs: sum(r["gold"] != "supported" for r in rs) / len(rs) if rs else float("nan")
    s3 = {"overall": {"rate": hal(ev), "ci": cluster_boot(ev, hal), "n": len(ev)}, "by_model": {}, "by_domain": {},
          "label_dist": Counter(r["gold"] for r in ev), "error_types": Counter(r["err"] for r in ev if r["gold"] != "supported"),
          "by_model_label": {}, "abstention": {}}
    for m in MODEL_TR.values():
        sub = [r for r in ev if r["model"] == m]
        s3["by_model"][m] = {"rate": hal(sub), "ci": cluster_boot(sub, hal), "n": len(sub)}
        s3["by_model_label"][m] = Counter(r["gold"] for r in sub)
        allm = [r for r in rows if r["model"] == m]
        s3["abstention"][m] = {"n_sent": len(allm), "abst": sum(r["abst"] for r in allm),
                               "by_qtype": {t: [sum(r["abst"] for r in allm if r["qtype"] == t),
                                                sum(1 for r in allm if r["qtype"] == t)] for t in ("answerable", "multi_fact", "partial")}}
    for d in ("finance", "legal", "medical"):
        sub = [r for r in ev if r["domain"] == d]
        s3["by_domain"][d] = {"rate": hal(sub), "ci": cluster_boot(sub, hal), "n": len(sub)}
    s3["auto_abstention_flag_vs_human"] = dict(Counter((r["auto_abst"], r["abst"]) for r in rows).items())
    out["S3"] = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in s3.items()}
    out["S3"]["by_model_label"] = {m: dict(c) for m, c in s3["by_model_label"].items()}
    out["S3"]["auto_abstention_flag_vs_human"] = {f"auto={a},human={h}": n for (a, h), n in s3["auto_abstention_flag_vs_human"].items()}

    # S1, S2, S4 — sistemler
    res = {}
    for s in SYSTEMS:
        rs = [r for r in ev if r[s] in LABELS]
        b = binary(rs, s)
        b["n_excluded_no_prediction"] = len(ev) - len(rs)
        for k in ("false_alarm", "precision", "recall", "f1"):
            b[k + "_ci"] = cluster_boot(rs, lambda x, k=k: binary(x, s)[k])
        b["four_class_descriptive"] = four(rs, s)
        b["by_model"] = {m: binary([r for r in rs if r["model"] == m], s) for m in MODEL_TR.values()}
        b["by_qtype"] = {t: binary([r for r in rs if r["qtype"] == t], s) for t in ("answerable", "multi_fact", "partial")}
        b["back_reference"] = binary([r for r in rs if r["back_ref"]], s)
        res[s] = b
    out["systems"] = res
    comp = {}
    for a, b in PAIRS:
        rs = [r for r in ev if r[a] in LABELS and r[b] in LABELS]
        mc = mcnemar(rs, a, b)
        mc["f1_diff"] = binary(rs, a)["f1"] - binary(rs, b)["f1"]
        mc["f1_diff_ci"] = cluster_boot(rs, lambda x: binary(x, a)["f1"] - binary(x, b)["f1"])
        mc["n"] = len(rs)
        comp[f"{a} vs {b}"] = mc
    out["comparisons"] = comp
    out["llm_call_rate"] = call_rates(rows)

    REP.mkdir(exist_ok=True)
    (REP / "AP6_RESULTS_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=float), encoding="utf-8")

    f = lambda x: f"{x:.3f}"
    ci = lambda c: f"[{c[0]:.3f}, {c[1]:.3f}]"
    L = ["# AP6 — Ön kayıtlı analiz sonuçları v1", "",
         f"Cümle: {len(rows)} · insan çekimser: {len(rows) - len(ev)} · değerlendirme kümesi: {len(ev)}. "
         "GA: soru düzeyinde küme bootstrap (10.000, seed 42).", "",
         "## S3 — Halüsinasyon oranı (insan etiketi supported değil)", "",
         "| Grup | n | Oran | %95 GA |", "|---|---:|---:|---|",
         f"| Genel | {len(ev)} | {f(s3['overall']['rate'])} | {ci(s3['overall']['ci'])} |"]
    L += [f"| {m} | {v['n']} | {f(v['rate'])} | {ci(v['ci'])} |" for m, v in s3["by_model"].items()]
    L += [f"| {d} | {v['n']} | {f(v['rate'])} | {ci(v['ci'])} |" for d, v in s3["by_domain"].items()]
    L += ["", f"Sınıf dağılımı: {dict(s3['label_dist'])}", f"Hata türleri: {dict(s3['error_types'])}", "",
          "Model bazında sınıflar: " + "; ".join(f"{m}: {dict(c)}" for m, c in s3["by_model_label"].items()), "",
          "Çekimserlik (model; soru türüne göre çekimser/cümle): " +
          "; ".join(f"{m}: {v['abst']}/{v['n_sent']} {v['by_qtype']}" for m, v in s3["abstention"].items()), "",
          f"Otomatik çekimser işareti ile insan kararı: {out['S3']['auto_abstention_flag_vs_human']}", "",
          "## S1, S2, S4 — Sistemler (ikili: halüsinasyon = supported değil)", "",
          "| Sistem | n | Yanlış alarm (S1) | Kesinlik | Duyarlılık (S2) | F1 | 4 sınıf doğruluk* | Macro-F1* |",
          "|---|---:|---|---|---|---|---:|---:|"]
    for s, b in res.items():
        L.append(f"| {SYS_TR[s]} | {b['n']} | {f(b['false_alarm'])} {ci(b['false_alarm_ci'])} | {f(b['precision'])} {ci(b['precision_ci'])} | "
                 f"{f(b['recall'])} {ci(b['recall_ci'])} | {f(b['f1'])} {ci(b['f1_ci'])} | "
                 f"{f(b['four_class_descriptive']['accuracy'])} | {f(b['four_class_descriptive']['macro_f1'])} |")
    L += ["", "\\* Betimsel; ana ölçüt değildir (§8).", "", "## Eşleştirilmiş karşılaştırmalar (ikili doğruluk, kesin McNemar; F1 farkı)", "",
          "| Karşılaştırma | n | Yalnız ilki doğru | Yalnız ikincisi doğru | p | F1 farkı [%95 GA] |", "|---|---:|---:|---:|---:|---|"]
    for k, v in comp.items():
        a, b = k.split(" vs ")
        L.append(f"| {SYS_TR[a]} – {SYS_TR[b]} | {v['n']} | {v['only_a_correct']} | {v['only_b_correct']} | {v['p_exact']:.3g} | "
                 f"{v['f1_diff']:+.3f} {ci(v['f1_diff_ci'])} |")
    cr = out["llm_call_rate"]
    L += ["", f"## Maliyet — büyük dil modeli çağrı oranı (n = {cr['n']})", "",
          f"P0 {cr['P0']:.3f} · PA {cr['PA']:.3f} · PB {cr['PB']:.3f}", "",
          "## Alt kümeler (betimsel, ikili F1 / yanlış alarm / duyarlılık)", ""]
    for s, b in res.items():
        parts = [f"{t}: F1 {f(v['f1'])}, YA {f(v['false_alarm'])}, D {f(v['recall'])} (n {v['n']})" for t, v in b["by_model"].items()]
        parts += [f"{t}: F1 {f(v['f1'])}, YA {f(v['false_alarm'])}, D {f(v['recall'])} (n {v['n']})" for t, v in b["by_qtype"].items()]
        br = b["back_reference"]
        parts.append(f"geri gönderme: F1 {f(br['f1'])}, YA {f(br['false_alarm'])}, D {f(br['recall'])} (n {br['n']})")
        L.append(f"- **{SYS_TR[s]}** — " + "; ".join(parts))
    L += ["", f"K2 karar vermediği için çıkarılan cümle: {res['k2']['n_excluded_no_prediction']}.",
          "Girdi dosyalarının SHA-256 değerleri JSON çıktısındadır."]
    (REP / "AP6_RESULTS_v1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("Yazıldı: reports/AP6_RESULTS_v1.{md,json}")


if __name__ == "__main__":
    main()
