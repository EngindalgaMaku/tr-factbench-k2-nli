#!/usr/bin/env python3
"""
140_findver_prepare_sources.py
Prepares the FinDVer finance slice (Zhao et al., EMNLP 2024; yilunzhao/FinDVer, MIT) for Turkish
translation (K-024).

Sampling (researcher decision, option C):
  - test split, subsets FDV-IE and FDV-MATH (FDV-KNOW needs outside knowledge, so it is not grounded);
  - reports shuffled with seed 42 and added whole (all their IE/MATH claims) until >= 160 claims;
  - a claim is kept only if its expert-marked evidence paragraphs total <= 600 words (translation cost).
Context = the expert-marked evidence paragraphs/tables only (the paper's oracle setting), in report order.
Each evidence element is translated once even if several claims cite it.

Output: data/findver/findver_source.json                 (shown to the translator, no labels)
        data/findver/findver_labels_DO_NOT_SHOW_TRANSLATOR.jsonl
"""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "finance_candidates" / "FinDVer"
OUT = ROOT / "data" / "findver"
SUBSETS = ("ie", "numeric")
TARGET, SEED, CAP_WORDS = 160, 42, 600


def main() -> None:
    data = [x for x in json.loads((SRC / "test.json").read_text(encoding="utf-8")) if x["subset"] in SUBSETS]
    reports = sorted({x["report"] for x in data})
    random.Random(SEED).shuffle(reports)
    chosen, n = [], 0
    for r in reports:
        chosen.append(r)
        n += sum(x["report"] == r for x in data)
        if n >= TARGET:
            break

    evidence: dict[str, dict] = {}
    claims, labels, dropped = [], [], []
    for r in chosen:
        ctx = {e["id"]: e for e in json.loads((SRC / "reports" / r).read_text(encoding="utf-8"))["context"]}
        for x in [x for x in data if x["report"] == r]:
            ids = sorted(x["relevant_context"])
            if sum(len(ctx[i]["context"].split()) for i in ids) > CAP_WORDS:
                dropped.append(x["example_id"])
                continue
            keys = []
            for i in ids:
                key = f"{r.removesuffix('.json')}#{i}"
                evidence.setdefault(key, {"evidence_id": key, "report": r, "para_id": i,
                                          "type": ctx[i]["type"], "text": ctx[i]["context"]})
                keys.append(key)
            claims.append({"claim_id": x["example_id"], "report": r, "subset": x["subset"],
                           "statement": x["statement"], "evidence": keys})
            labels.append({"claim_id": x["example_id"], "report": r, "subset": x["subset"],
                           "entailment_label": x["entailment_label"],
                           "binary": "supported" if x["entailment_label"] else "unsupported",
                           "explanation_en": x["explanation"]})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "findver_source.json").write_text(
        json.dumps({"evidence": list(evidence.values()), "claims": claims}, ensure_ascii=False, indent=1), encoding="utf-8")
    with (OUT / "findver_labels_DO_NOT_SHOW_TRANSLATOR.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for row in labels:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("reports", len(chosen), "| claims kept", len(claims), "dropped (evidence >", CAP_WORDS, "words):", len(dropped))
    print("by subset/label", dict(Counter((l["subset"], l["binary"]) for l in labels)))
    print("evidence elements", len(evidence), dict(Counter(e["type"] for e in evidence.values())),
          "| reports with kept claims", len({c["report"] for c in claims}))


if __name__ == "__main__":
    main()
