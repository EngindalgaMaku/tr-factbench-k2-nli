#!/usr/bin/env python3
"""
87_ap6_run_v4_judge.py
Runs the frozen V4 predicate-aware meta-judge (Llama-3.3-70B) on AP6 K1/K2
disagreement sentences. Prompt construction and output parsing are imported
unchanged from scripts/75_run_predicate_aware_debiased_arbitration.py; the
request payload (model, temperature 0, top_p 1, max_tokens 400) is identical.
Only difference: TLS certificate verification is ON (75 used verify=False),
which does not change the request content.

Inputs: data/ap6/verifier/{ap6_claims.jsonl, k1_predictions.jsonl, k2_soft_prob_predictions.jsonl}
        data/ap6/verifier/atoms/k2_input.jsonl (atoms shown to the judge, unlabeled)
Output: data/ap6/verifier/v4_judge_predictions.jsonl (resumable)
"""
from __future__ import annotations

import importlib.util
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VER = ROOT / "data" / "ap6" / "verifier"

spec = importlib.util.spec_from_file_location("v4", ROOT / "scripts" / "75_run_predicate_aware_debiased_arbitration.py")
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def call(prompt: str, api_key: str, retries: int = 5) -> tuple[dict, float]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
               "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
               "X-OpenRouter-Title": "TR-FactBench AP6 V4 judge"}
    payload = {"model": v4.MODEL_ID, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.0, "top_p": 1.0, "max_tokens": 400, "stream": False}
    t0 = time.time()
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(v4.ENDPOINT, headers=headers, json=payload, timeout=90)
            if resp.status_code == 200:
                return resp.json(), time.time() - t0
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("max retries exceeded")


def main() -> None:
    load_dotenv(ROOT.parent / "tr-factbench-v0.1.0-preview" / ".env")
    api_key = os.environ["OPENROUTER_API_KEY"]
    claims = {r["example_id"]: r for r in read_jsonl(VER / "ap6_claims.jsonl")}
    k1 = {r["example_id"]: r["predicted_label"] for r in read_jsonl(VER / "k1_predictions.jsonl")}
    k2 = {r["example_id"]: r["pred_label"] for r in read_jsonl(VER / "k2_soft_prob_predictions.jsonl")}
    atoms = {r["example_id"]: r["pred_atoms"] for r in read_jsonl(VER / "atoms" / "k2_input.jsonl")}
    out_path = VER / "v4_judge_predictions.jsonl"
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
        resp, latency = call(prompt, api_key)
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
