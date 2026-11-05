#!/usr/bin/env python3
"""
117_ragbench_run_v4_judge.py
Frozen V4 meta-judge (Llama-3.3-70B, OpenRouter) on the K1/K2 disagreements of the
Turkish RAGBench medical slice (K-018). Prompt construction, parsing and the request
payload are reused unchanged from scripts/87_ap6_run_v4_judge.py (which itself imports
them from scripts/75); only the input/output paths differ.

The judge sees the full context (an LLM, not bound to the 512-token limit), the claim,
the K1 and K2 labels and the K2 atoms — exactly the AP6 v1 inputs.

Output: <build>/predictions/v4_judge.jsonl (resumable); --build/--claims select the slice (default: medical)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "data" / "ragbench" / "medical" / "build"

spec = importlib.util.spec_from_file_location("ap6judge", ROOT / "scripts" / "87_ap6_run_v4_judge.py")
ap6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap6)
v4 = ap6.v4
read_jsonl = ap6.read_jsonl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(BUILD))
    ap.add_argument("--claims", default="ragbench_tr_medical_claims.jsonl")
    args = ap.parse_args()
    build = Path(args.build).resolve()
    load_dotenv(ROOT.parent / "tr-factbench-v0.1.0-preview" / ".env")
    api_key = os.environ["OPENROUTER_API_KEY"]
    claims = {r["example_id"]: r for r in read_jsonl(build / args.claims)}
    k1 = {r["example_id"]: r["predicted_label"] for r in read_jsonl(build / "predictions" / "k1.jsonl")}
    k2 = {r["example_id"]: r["k2"] for r in read_jsonl(build / "predictions" / "k2_windowed.jsonl")
          if r["k2"] is not None}
    atoms = {r["example_id"]: r["pred_atoms"] for r in read_jsonl(build / "atoms" / "k2_input.jsonl")}
    out_path = build / "predictions" / "v4_judge.jsonl"
    done = {r["example_id"] for r in read_jsonl(out_path)}

    cases = [eid for eid in claims if eid in k2 and k1[eid] != k2[eid]]
    print(f"disagreement cases: {len(cases)} (already done: {len(done)})")
    for eid in cases:
        if eid in done:
            continue
        c = claims[eid]
        case = {"context": c["context"], "claim": c["claim"], "k1_pred": k1[eid], "k2_pred": k2[eid],
                "k2_atoms": [{"atom": a} for a in atoms.get(eid, [])]}
        prompt = v4.build_predicate_prompt(case)
        resp, latency = ap6.call(prompt, api_key)
        raw = (resp.get("choices", [{}])[0].get("message", {}) or {}).get("content", "").strip()
        parsed = v4.parse_judge_output(raw)
        rec = {"example_id": eid, "k1_pred": k1[eid], "k2_pred": k2[eid], "judge_decision": parsed["final_decision"],
               "favored_model": parsed["favored_model"], "reasoning": parsed["reasoning"],
               "parse_fallback": parsed["reasoning"] in ("JSON parse fallback used.", "Parse failure."),
               "model_resolved": resp.get("model"), "latency_seconds": round(latency, 2), "raw_output": raw}
        with out_path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        time.sleep(0.3)
    print("done")


if __name__ == "__main__":
    main()
