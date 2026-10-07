#!/usr/bin/env python3
"""
93_profile_frozen_system.py — Dondurulmuş sistemin süre ve bellek profili (tez 4.8).

Yerel bileşenler (tek GPU, iddia başına, yığın boyutu 1):
  - K1: Gold-480'in 480 iddiası.
  - K2 NLI: her iddianın dondurulmuş Gold-480 önermeleri tek yığında (480 iddia).
  - Atomik ayrıştırıcı: Gold-480'den sabit örneklem (60 iddia, seed 42), dondurulmuş ayar (180 belirteç).
  Her bileşen için ısınma (5 çağrı) sonrası ortalama, medyan ve p95 süre; tepe GPU belleği.
Dış çağrılar (yeniden çalıştırılmaz; kayıtlardan okunur):
  - Tek başına LLM'ler: Gold-480 request_log gecikmeleri ve OpenRouter ücretleri.
  - V4 hakemi: genellenebilirlik değerlendirmesindeki 466 çağrının gecikmeleri.
Çıktı: reports/FROZEN_SYSTEM_PROFILE.{md,json}
"""
from __future__ import annotations

import json
import platform
import random
import statistics as st
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
TFB = ROOT.parent / "tr-factbench-v0.1.0-preview"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "atomizer" / "v2"))
GOLD = TFB / "data/evaluation/gold_v1.0/gold/TR-FactBench_controlled480_GOLD_v1.0.jsonl"
ATOMS = ROOT / "data/processed/atom_level/gemma_predicted_gold480/k2_input.jsonl"
NLI_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
N_ATOMIZER = 60


def rj(p):
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def summarize(ts):
    s = sorted(ts)
    return {"n": len(s), "mean_ms": 1000 * st.mean(s), "median_ms": 1000 * st.median(s), "p95_ms": 1000 * s[int(0.95 * (len(s) - 1))]}


def timed(fn, items, warmup=5):
    for it in items[:warmup]:
        fn(it)
    torch.cuda.synchronize()
    out = []
    for it in items:
        t0 = time.perf_counter()
        fn(it)
        torch.cuda.synchronize()
        out.append(time.perf_counter() - t0)
    return out


def main():
    dev = "cuda"
    gold = rj(GOLD)
    atoms = {r["example_id"]: r for r in rj(ATOMS)}
    res = {"gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "python": platform.python_version(), "components": {}}

    # K1
    spec = __import__("importlib.util").util.spec_from_file_location("k1", ROOT / "scripts/84_run_k1_frozen.py")
    k1mod = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(k1mod)
    cfg = json.loads((TFB / "data/evaluation/gold_v1.0/verifier_hold/VERIFIER_CONFIG_v1.0.json").read_text(encoding="utf-8"))
    torch.cuda.reset_peak_memory_stats()
    tok, model = k1mod.load_k1(cfg, dev)
    fmt = cfg["input_format"]

    def k1_one(r):
        enc = tok(fmt["text_a"].format(context=r["context"].strip()),
                  fmt["text_b"].format(question=r["question"].strip(), claim=r["claim"].strip()),
                  max_length=512, truncation=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            model(**enc)
    ts = timed(k1_one, gold)
    res["components"]["K1 (ELECTRA-TR LoRA)"] = {**summarize(ts), "peak_gpu_mb": torch.cuda.max_memory_allocated() / 2**20}
    del model
    torch.cuda.empty_cache()

    # K2 NLI
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    torch.cuda.reset_peak_memory_stats()
    ntok = AutoTokenizer.from_pretrained(NLI_ID)
    nli = AutoModelForSequenceClassification.from_pretrained(NLI_ID).to(dev).eval()
    ids = [r["release_example_id"] for r in gold]

    def nli_one(i):
        a = atoms[i]
        enc = ntok([a["context"]] * len(a["pred_atoms"]), a["pred_atoms"], max_length=512, truncation="only_first",
                   padding=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            nli(**enc)
    ts = timed(nli_one, ids)
    res["components"]["K2 NLI (mDeBERTa-v3, iddianın bütün önermeleri)"] = {**summarize(ts), "peak_gpu_mb": torch.cuda.max_memory_allocated() / 2**20}
    del nli
    torch.cuda.empty_cache()

    # Atomik ayrıştırıcı
    from atomizer_runtime import LocalAtomizer
    torch.cuda.reset_peak_memory_stats()
    at = LocalAtomizer(adapter_path=str(ROOT.parent / "atomizer/v2/outputs/google_gemma_4_e2b_it_final_adapter"),
                       base_model="google/gemma-4-E2B-it", max_new_tokens=180)
    sample = random.Random(42).sample(gold, N_ATOMIZER)
    ts = timed(lambda r: at.predict(r["claim"]), sample, warmup=2)
    res["components"]["Atomik ayrıştırıcı (Gemma-4-E2B QLoRA, 4 bit)"] = {**summarize(ts), "peak_gpu_mb": torch.cuda.max_memory_allocated() / 2**20}

    # Dış çağrılar (kayıtlardan)
    ext = {}
    llm_root = TFB / "results/llm_baselines/gold_v1.0"
    for model_dir in ["google_gemma-4-26b-a4b-it", "meta-llama_llama-3.3-70b-instruct", "openai_gpt-4.1-mini", "qwen_qwen-2.5-72b-instruct"]:
        for mode in ["zero_shot", "few_shot_8"]:
            log = rj(llm_root / model_dir / mode / "request_log.jsonl")
            lat = [r["latency_seconds"] for r in log if r.get("status") == "success" and r.get("latency_seconds")]
            cost = [r["usage"].get("cost") for r in log if r.get("usage") and r["usage"].get("cost") is not None]
            ext[f"{model_dir} {mode}"] = {"n": len(lat), "median_s": st.median(lat), "p95_s": sorted(lat)[int(0.95 * (len(lat) - 1))],
                                          "mean_cost_usd": st.mean(cost) if cost else None}
    v4 = [r["latency_seconds"] for r in rj(ROOT / "data/ap6/verifier/v4_judge_predictions.jsonl")]
    ext["V4 hakemi (Llama-3.3-70B), genellenebilirlik çağrıları"] = {"n": len(v4), "median_s": st.median(v4), "p95_s": sorted(v4)[int(0.95 * (len(v4) - 1))], "mean_cost_usd": None}
    res["external"] = ext

    (ROOT / "reports/FROZEN_SYSTEM_PROFILE.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    L = [f"# Dondurulmuş sistem profili (betik 93)", "", f"GPU: {res['gpu']} · torch {res['torch']} · Python {res['python']}", "",
         "| Yerel bileşen | n | Ortalama (ms) | Medyan (ms) | p95 (ms) | Tepe GPU belleği (MB) |", "|---|---:|---:|---:|---:|---:|"]
    for k, v in res["components"].items():
        L.append(f"| {k} | {v['n']} | {v['mean_ms']:.1f} | {v['median_ms']:.1f} | {v['p95_ms']:.1f} | {v['peak_gpu_mb']:.0f} |")
    L += ["", "| Dış çağrı (kayıtlardan) | n | Medyan (s) | p95 (s) | Ortalama ücret (USD) |", "|---|---:|---:|---:|---:|"]
    for k, v in ext.items():
        c = "—" if v["mean_cost_usd"] is None else f"{v['mean_cost_usd']:.6f}"
        L.append(f"| {k} | {v['n']} | {v['median_s']:.2f} | {v['p95_s']:.2f} | {c} |")
    (ROOT / "reports/FROZEN_SYSTEM_PROFILE.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
