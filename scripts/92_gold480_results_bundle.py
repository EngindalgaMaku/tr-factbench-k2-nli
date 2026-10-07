#!/usr/bin/env python3
"""
92_gold480_results_bundle.py
Tez Bölüm 4 için Gold-480 ana sonuçlarını, dondurulmuş tahmin dosyalarından tek yerde ve tek yöntemle yeniden hesaplar.
Eski rapor sayıları kullanılmaz; her değer bu betiğin girdilerinden türetilir.

Sistemler: K1; K2 (düz kural ve soft-prob); kahin üst sınırı (K1 veya K2 doğru); hibrit P0 (V4 hakemi);
kör hakemli hibritler (hakem K1/K2 çıktısını görmez); PA/PB (kör Gemma-4-26B uzlaşma denetimi);
tek başına LLM'ler (4 model x sıfır/8 atış).
Ölçütler: doğruluk, Macro-F1, MCC, sınıf F1, hakem çağrı oranı; bağlam grubu bootstrap %95 GA (10.000, seed 42);
K1'e karşı kesin McNemar; alan bazında Macro-F1.
Çıktı: reports/GOLD480_RESULTS_BUNDLE.{md,json}
"""
from __future__ import annotations

import json
import random
from math import comb
from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
GOLD_DIR = TFB / "data" / "evaluation" / "gold_v1.0"
EXP = ROOT / "reports" / "experiments"
LLM = TFB / "results" / "llm_baselines" / "gold_v1.0"
LABELS = ["supported", "partially_supported", "contradicted", "unverifiable"]
ROUTE = {"partially_supported", "contradicted"}
N_BOOT = 10_000


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def eid(r: dict) -> str:
    return r.get("release_example_id") or r["example_id"]


def domain_of(i: str) -> str:
    n = int(i.rsplit("_", 1)[-1])
    return "finance" if n <= 160 else ("legal" if n <= 320 else "medical")


def mf1(y, p) -> float:
    return f1_score(y, p, labels=LABELS, average="macro", zero_division=0)


def mcnemar_exact(a_ok: list[bool], b_ok: list[bool]) -> tuple[int, int, float]:
    b = sum(x and not y for x, y in zip(a_ok, b_ok))
    c = sum(y and not x for x, y in zip(a_ok, b_ok))
    n, k = b + c, min(b, c)
    p = min(1.0, 2 * sum(comb(n, j) for j in range(k + 1)) / 2 ** n) if n else 1.0
    return b, c, p


def main() -> None:
    gold_rows = read_jsonl(GOLD_DIR / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")
    ids = [eid(r) for r in gold_rows]
    gold = {eid(r): r["gold_label"] for r in gold_rows}
    group = {eid(r): r["context"] for r in gold_rows}
    groups = sorted(set(group.values()))
    members = {g: [i for i in ids if group[i] == g] for g in groups}

    k1 = {eid(r): r["predicted_label"] for r in read_jsonl(GOLD_DIR / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")}
    agg = EXP / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
    k2s = {eid(r): r["pred_label"] for r in read_jsonl(agg / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")}
    k2f = {eid(r): r["pred_label"] for r in read_jsonl(agg / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__flat.jsonl")}
    v4 = {r["example_id"]: r["judge_decision"] for r in read_jsonl(EXP / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")}
    llm = {}
    for model in ["google_gemma-4-26b-a4b-it", "meta-llama_llama-3.3-70b-instruct", "openai_gpt-4.1-mini", "qwen_qwen-2.5-72b-instruct"]:
        for mode in ["zero_shot", "few_shot_8"]:
            llm[(model, mode)] = {eid(r): r["predicted_label"] for r in read_jsonl(LLM / model / mode / "predictions.jsonl")}

    dis = [i for i in ids if k1[i] != k2s[i]]
    systems: dict[str, tuple[dict, float | None]] = {}
    systems["K1 (ELECTRA-TR)"] = (k1, 0.0)
    systems["K2 düz kural"] = (k2f, 0.0)
    systems["K2 soft-prob"] = (k2s, 0.0)
    systems["İdeal seçim üst sınırı (K1 veya K2 doğru)"] = ({i: gold[i] if gold[i] in (k1[i], k2s[i]) else k1[i] for i in ids}, None)
    systems["Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi)"] = ({i: k1[i] if k1[i] == k2s[i] else v4[i] for i in ids}, len(dis) / len(ids))
    gz = llm[("google_gemma-4-26b-a4b-it", "zero_shot")]
    for (model, mode), pred in llm.items():
        short = model.split("_", 1)[1]
        systems[f"Hibrit P0 + kör {short} {mode}"] = ({i: k1[i] if k1[i] == k2s[i] else pred[i] for i in ids}, len(dis) / len(ids))
    p0 = systems["Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi)"][0]
    pa = {i: gz[i] if (k1[i] == k2s[i] and k1[i] in ROUTE) else p0[i] for i in ids}
    pb = {i: gz[i] if (k1[i] == k2s[i] and k1[i] in ROUTE and domain_of(i) == "medical") else p0[i] for i in ids}
    n_pa = sum(k1[i] == k2s[i] and k1[i] in ROUTE for i in ids)
    n_pb = sum(k1[i] == k2s[i] and k1[i] in ROUTE and domain_of(i) == "medical" for i in ids)
    systems["PA (P0-V4 + kör Gemma uzlaşma denetimi)"] = (pa, (len(dis) + n_pa) / len(ids))
    systems["PB (P0-V4 + yalnız tıp uzlaşma denetimi)"] = (pb, (len(dis) + n_pb) / len(ids))
    for (model, mode), pred in llm.items():
        systems[f"Tek başına {model.split('_', 1)[1]} {mode}"] = (pred, 1.0)

    rng = random.Random(42)
    boots = [[i for g in (rng.choice(groups) for _ in groups) for i in members[g]] for _ in range(N_BOOT)]
    y_all = [gold[i] for i in ids]
    k1_ok = [k1[i] == gold[i] for i in ids]
    out = {"n": len(ids), "groups": len(groups), "disagreements": len(dis), "systems": {}}
    lines = ["# Gold-480 sonuç paketi (Bölüm 4 için, betik 92)", "",
             f"n = {len(ids)}, bağlam grubu = {len(groups)}, K1≠K2 (soft-prob) = {len(dis)}. "
             f"GA: bağlam grubu bootstrap, {N_BOOT} tekrar, seed 42. McNemar: K1'e karşı, kesin.", "",
             "| Sistem | Doğruluk | Macro-F1 [%95 GA] | MCC | Çağrı oranı | McNemar vs K1 (b/c, p) | Finans | Hukuk | Tıp |",
             "|---|---:|---|---:|---:|---|---:|---:|---:|"]
    for name, (pred, calls) in systems.items():
        p_all = [pred[i] for i in ids]
        f = mf1(y_all, p_all)
        bs = sorted(mf1([gold[i] for i in s], [pred[i] for i in s]) for s in boots)
        lo, hi = bs[int(0.025 * N_BOOT)], bs[int(0.975 * N_BOOT) - 1]
        b, c, p = mcnemar_exact(k1_ok, [pred[i] == gold[i] for i in ids])
        dom = {d: mf1([gold[i] for i in ids if domain_of(i) == d], [pred[i] for i in ids if domain_of(i) == d]) for d in ("finance", "legal", "medical")}
        per = dict(zip(LABELS, f1_score(y_all, p_all, labels=LABELS, average=None, zero_division=0).round(4).tolist()))
        rec = {"accuracy": accuracy_score(y_all, p_all), "macro_f1": f, "ci95": [lo, hi], "mcc": matthews_corrcoef(y_all, p_all),
               "call_rate": calls, "mcnemar_vs_k1": {"b_k1_only": b, "c_sys_only": c, "p": p}, "domain_macro_f1": dom, "per_class_f1": per}
        out["systems"][name] = rec
        cr = "—" if calls is None else f"{calls:.1%}"
        lines.append(f"| {name} | {rec['accuracy']:.4f} | {f:.4f} [{lo:.4f}, {hi:.4f}] | {rec['mcc']:.4f} | {cr} | "
                     f"{b}/{c}, {p:.3g} | {dom['finance']:.4f} | {dom['legal']:.4f} | {dom['medical']:.4f} |")
    lines += ["", "## Sınıf bazında F1", "", "| Sistem | " + " | ".join(LABELS) + " |", "|---|" + "---:|" * 4]
    for name, rec in out["systems"].items():
        lines.append(f"| {name} | " + " | ".join(f"{rec['per_class_f1'][l]:.4f}" for l in LABELS) + " |")
    pairs = [
        ("Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot", "Tek başına gemma-4-26b-a4b-it zero_shot"),
        ("Hibrit P0 + kör gpt-4.1-mini few_shot_8", "Tek başına gpt-4.1-mini few_shot_8"),
        ("Hibrit P0 + kör llama-3.3-70b-instruct few_shot_8", "Tek başına llama-3.3-70b-instruct few_shot_8"),
        ("Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot", "Tek başına gpt-4.1-mini few_shot_8"),
        ("Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi)", "Tek başına gpt-4.1-mini few_shot_8"),
        ("Hibrit P0 + Llama-70B V4 (istem Gold'da geliştirildi)", "Hibrit P0 + kör gemma-4-26b-a4b-it zero_shot"),
        ("K2 soft-prob", "K2 düz kural"),
    ]
    lines += ["", "## Seçili eşleştirilmiş karşılaştırmalar", "",
              "| A | B | ΔMacro-F1 (A−B) [%95 GA] | McNemar (yalnız A doğru / yalnız B doğru, p) |", "|---|---|---|---|"]
    out["pairs"] = []
    for a_name, b_name in pairs:
        pa_, pb_ = systems[a_name][0], systems[b_name][0]
        d = mf1(y_all, [pa_[i] for i in ids]) - mf1(y_all, [pb_[i] for i in ids])
        ds = sorted(mf1([gold[i] for i in s], [pa_[i] for i in s]) - mf1([gold[i] for i in s], [pb_[i] for i in s]) for s in boots)
        lo, hi = ds[int(0.025 * N_BOOT)], ds[int(0.975 * N_BOOT) - 1]
        b, c, p = mcnemar_exact([pb_[i] == gold[i] for i in ids], [pa_[i] == gold[i] for i in ids])
        out["pairs"].append({"a": a_name, "b": b_name, "delta": d, "ci95": [lo, hi], "a_only": c, "b_only": b, "p": p})
        lines.append(f"| {a_name} | {b_name} | {d:+.4f} [{lo:+.4f}, {hi:+.4f}] | {c} / {b}, {p:.3g} |")
    lines += ["", "Notlar: V4 istemi ve soft-prob kuralı Gold-480 üzerinde seçilmiştir (Karar 7, 15); PA/PB Gold-480 uzlaşma hataları "
              "incelenerek tasarlanmıştır (tasarım analizi). Kör hakemler istem geliştirmesine katılmamıştır. "
              "McNemar b = yalnız K1 doğru, c = yalnız sistem doğru."]
    rep = ROOT / "reports" / "GOLD480_RESULTS_BUNDLE.md"
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "reports" / "GOLD480_RESULTS_BUNDLE.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
