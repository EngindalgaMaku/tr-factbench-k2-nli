#!/usr/bin/env python3
"""
142_findver_build_dataset.py
FinDVer finance slice (K-024): merges the Turkish translation with the expert labels into one verifier
input file, in the same row format as the medical (scripts/112) and legal (scripts/132) slices.

Label scheme: expert binary entailment label. entailed -> supported, refuted -> contradicted, so
`gold_label` uses two classes of the project's 4-class scheme; `gold_binary`: supported / unsupported.
FinDVer has no question per claim: `question` is left empty (all tools accept an empty question).

Context: the expert-marked evidence elements (paragraphs / tables) in report order, joined by blank lines.
Context windows for K2 (K-025): each evidence element is one window (as each source document is one window
in K-017); an element that does not fit 450 tokens is cut at line (else sentence) boundaries into windows of at most 400.
K1 keeps the full context (truncated; reported separately).

Output: data/findver/build/findver_tr_finance_claims.jsonl, findver_tr_finance_labels.jsonl, manifest.json
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
FV = ROOT / "data" / "findver"
OUT = FV / "build"
NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
FULL_LIMIT, WINDOW_TOKENS = 450, 400


def units_of(text: str, n) -> list[str]:
    """Lines; a line that alone exceeds the window is cut into sentences, a sentence into token slices."""
    out = []
    for line in text.split("\n"):
        if n(line) <= WINDOW_TOKENS:
            out.append(line)
            continue
        for sent in re.split(r"(?<=[.;:!?])\s+", line):
            if n(sent) <= WINDOW_TOKENS:
                out.append(sent)
            else:
                words, cur = sent.split(" "), ""
                for w in words:
                    cand = f"{cur} {w}" if cur else w
                    if cur and n(cand) > WINDOW_TOKENS:
                        out.append(cur)
                        cur = w
                    else:
                        cur = cand
                out.append(cur)
    return out


def split_long(text: str, n) -> list[str]:
    if n(text) <= FULL_LIMIT:
        return [text]
    out, cur = [], ""
    for unit in units_of(text, n):
        cand = f"{cur}\n{unit}" if cur else unit
        if cur and n(cand) > WINDOW_TOKENS:
            out.append(cur)
            cur = unit
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def main() -> None:
    tok = AutoTokenizer.from_pretrained(NLI_MODEL)
    n = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
    src = json.loads((FV / "findver_source.json").read_text(encoding="utf-8"))
    ev_tr, cl_tr = {}, {}
    for i in range(1, 5):
        b = json.loads((FV / "batches" / f"batch_{i:02d}.json").read_text(encoding="utf-8"))
        ev_tr.update(b["evidence"])
        cl_tr.update(b["claims"])
    labels = {json.loads(l)["claim_id"]: json.loads(l)
              for l in (FV / "findver_labels_DO_NOT_SHOW_TRANSLATOR.jsonl").open(encoding="utf-8")}
    windows_of = {k: split_long(v, n) for k, v in ev_tr.items()}

    claims, label_rows = [], []
    per_report = Counter(c["report"] for c in src["claims"])
    pos = Counter()
    for c in src["claims"]:
        keys = list(dict.fromkeys(c["evidence"]))
        lab = labels[c["claim_id"]]
        pos[c["report"]] += 1
        context = "\n\n".join(ev_tr[k] for k in keys)
        claims.append({
            "example_id": c["claim_id"], "release_example_id": c["claim_id"],
            "domain": "finance", "part": c["subset"], "question_id": c["report"].removesuffix(".json"),
            "model": "human_expert_statement", "context": context, "question": "",
            "claim": cl_tr[c["claim_id"]],
            "gold_binary": lab["binary"], "gold_label": "supported" if lab["entailment_label"] else "contradicted",
            "label_scheme": "findver_expert_binary", "label_status": "HUMAN_EXPERT_DOUBLE_ANNOTATED",
            "position": pos[c["report"]], "n_sentences": per_report[c["report"]],
            "context_words": len(context.split()), "evidence_ids": keys,
            "context_windows": [w for k in keys for w in windows_of[k]],
        })
        label_rows.append({"example_id": c["claim_id"], "report": c["report"], "subset": c["subset"],
                           "entailment_label": lab["entailment_label"], "gold_binary": lab["binary"],
                           "statement_en": c["statement"], "explanation_en": lab["explanation_en"]})

    OUT.mkdir(parents=True, exist_ok=True)
    names = ["findver_tr_finance_claims.jsonl", "findver_tr_finance_labels.jsonl"]
    for name, rows in zip(names, [claims, label_rows]):
        with (OUT / name).open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    ctx_tokens = [n(c["context"]) for c in claims]
    manifest = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_dataset": "FinDVer (Zhao et al., EMNLP 2024), test split, subsets ie + numeric, MIT",
        "slice": "reports shuffled with seed 42 until >= 160 claims; claims with evidence > 600 words dropped (K-024)",
        "translation": "Claude, rule-based, tables cell-mapped, researcher-reviewed in 4 batches (K-024)",
        "labels": "expert entailment label (entailed / refuted); refuted = unsupported",
        "n_reports": len(per_report), "n_claims": len(claims), "n_evidence_elements": len(ev_tr),
        "by_subset": dict(Counter(c["part"] for c in claims)),
        "gold_binary": dict(Counter(c["gold_binary"] for c in claims)),
        "unsupported_rate": round(sum(c["gold_binary"] == "unsupported" for c in claims) / len(claims), 4),
        "context_tokens": {"median": sorted(ctx_tokens)[len(ctx_tokens) // 2], "max": max(ctx_tokens),
                           "over_512": sum(t > 512 for t in ctx_tokens)},
        "evidence_elements_split": {k: len(v) for k, v in windows_of.items() if len(v) > 1},
        "question_field": "empty (FinDVer has no question)",
        "sha256": {nm: hashlib.sha256((OUT / nm).read_bytes()).hexdigest() for nm in names},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
