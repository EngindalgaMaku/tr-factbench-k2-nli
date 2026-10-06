#!/usr/bin/env python3
"""
82_ap6_generate_answers.py
AP6 step 3: generate RAG answers for the 60 frozen questions with the three
frozen responder models (OpenRouter), using the frozen prompt v1.1 (v1.0 + max_tokens 2000) and the
frozen top-3 retrieval contexts.

Resumable: existing (question_id, model) pairs are skipped.
Records the requested and resolved model ids, token usage, the raw API
response and any reasoning block stripped from the visible answer.

Output: data/ap6/generation/answers.jsonl, raw_responses.jsonl
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
RAG = ROOT / "data" / "ap6" / "rag"
OUT = ROOT / "data" / "ap6" / "generation"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def call(payload: dict, api_key: str, retries: int = 5) -> dict:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
               "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
               "X-OpenRouter-Title": "TR-FactBench AP6 RAG generation"}
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=180)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("max retries exceeded")


def main() -> None:
    for env in (ROOT.parent / "tr-factbench-v0.1.0-preview" / ".env", ROOT / ".env"):
        if env.exists():
            load_dotenv(env)
            break
    api_key = os.environ["OPENROUTER_API_KEY"]

    prompt = json.loads((RAG / "generation_prompt_v1.1.json").read_text(encoding="utf-8"))
    assert prompt["status"] == "frozen"
    digest = hashlib.sha256((prompt["system"] + "\n" + prompt["user_template"]).encode("utf-8")).hexdigest()
    assert digest == prompt["sha256_of_system_and_template"], "prompt changed after freezing"

    chunks = {c["chunk_id"]: c["text"] for c in read_jsonl(RAG / "chunks.jsonl")}
    retrieval = read_jsonl(RAG / "retrieval_top3.jsonl")

    OUT.mkdir(parents=True, exist_ok=True)
    answers_path, raw_path = OUT / "answers.jsonl", OUT / "raw_responses.jsonl"
    done = {(a["question_id"], a["model_requested"]) for a in read_jsonl(answers_path)}

    for model in prompt["models"]:
        for r in retrieval:
            if (r["question_id"], model) in done:
                continue
            c1, c2, c3 = (chunks[cid] for cid in r["chunk_ids"])
            user = prompt["user_template"].format(chunk_1=c1, chunk_2=c2, chunk_3=c3, question=r["question"])
            payload = {"model": model,
                       "messages": [{"role": "system", "content": prompt["system"]},
                                    {"role": "user", "content": user}],
                       **prompt["decoding"],
                       "reasoning": {"exclude": True}}
            t0 = time.time()
            resp = call(payload, api_key)
            latency = time.time() - t0
            choice = resp.get("choices", [{}])[0]
            raw_text = (choice.get("message", {}) or {}).get("content") or ""
            answer = THINK_RE.sub("", raw_text).strip()
            rec = {"question_id": r["question_id"], "domain": r["domain"], "type": r["type"],
                   "model_requested": model, "model_resolved": resp.get("model"),
                   "provider": resp.get("provider"), "answer": answer,
                   "think_block_stripped": answer != raw_text.strip(),
                   "finish_reason": choice.get("finish_reason"), "usage": resp.get("usage"),
                   "latency_seconds": round(latency, 2), "prompt_sha256": digest,
                   "context_chunk_ids": r["chunk_ids"]}
            with answers_path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            with raw_path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"question_id": r["question_id"], "model_requested": model, "response": resp},
                                   ensure_ascii=False) + "\n")
            print(f"[{model:32s}] {r['question_id']}  words={len(answer.split()):4d}  finish={rec['finish_reason']}")
            time.sleep(0.3)


if __name__ == "__main__":
    main()
