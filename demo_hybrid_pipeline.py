#!/usr/bin/env python3
"""
demo_hybrid_pipeline.py
========================
TR-FactBench Akademik Araştırma ve Hibrit Doğrulama Laboratuvarı
Burdur Mehmet Akif Ersoy Üniversitesi | Fen Bilimleri Enstitüsü
Öğrenci: Engin Dalga | Danışman: Prof. Dr. Serkan Ballı
"""
from __future__ import annotations

import html as html_lib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import numpy as np
import requests
import torch
import urllib3
from dotenv import load_dotenv
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

urllib3.disable_warnings()

# ── KÖK DİZİN VE ORTAM AYARLARI ──────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "tr-factbench-v0.1.0-preview").exists() else HERE.parent

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

for ep in [ROOT / "tr-factbench-v0.1.0-preview" / ".env", ROOT / "k2_nli" / ".env", ROOT / ".env"]:
    if ep.exists():
        load_dotenv(ep)
        break

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ── SABİTLER VE ETİKET TANIMLARI ─────────────────────────────────────────────
LABEL_MAP = {0: "supported", 1: "partially_supported", 2: "contradicted", 3: "unverifiable"}
LABEL_TR = {
    "supported": "Destekleniyor (Supported)",
    "partially_supported": "Kısmen Destekleniyor (Partially Supported)",
    "contradicted": "Çelişiyor (Contradicted)",
    "unverifiable": "Doğrulanamaz (Unverifiable)",
    "unsupported": "Desteklenmiyor (Unsupported - İkili)",
}
LABEL_SHORT_TR = {
    "supported": "Destekleniyor",
    "partially_supported": "Kısmi Destek",
    "contradicted": "Çelişiyor",
    "unverifiable": "Doğrulanamaz",
    "unsupported": "Desteklenmiyor",
}
LABEL_COLOR = {
    "supported": "#15803d",
    "partially_supported": "#b45309",
    "contradicted": "#b91c1c",
    "unverifiable": "#475569",
    "unsupported": "#be123c",
}
LABEL_BG = {
    "supported": "#f0fdf4",
    "partially_supported": "#fffbeb",
    "contradicted": "#fef2f2",
    "unverifiable": "#f8fafc",
    "unsupported": "#fff1f2",
}
ATOM_NLI_TR = {
    "entailment": "Doğrulanıyor (Entailment)",
    "contradiction": "Çelişiyor (Contradiction)",
    "neutral": "Bağlam Dışı / Nötr (Neutral)",
}
ATOM_NLI_COLOR = {
    "entailment": "#15803d",
    "contradiction": "#b91c1c",
    "neutral": "#475569",
}
DOMAIN_TR = {
    "finance": "Finans",
    "legal": "Hukuk",
    "medical": "Tıp / Sağlık",
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_LENGTH = 512

# ── MODEL YÜKLEME (BAŞLANGIÇTA BİR KEZ) ───────────────────────────────────────
print(f"[{DEVICE.upper()}] TR-FactBench Modelleri Yükleniyor...")

K1_ADAPTER = (
    ROOT
    / "tr-factbench-v0.1.0-preview"
    / "runs"
    / "ablations"
    / "H1_DROP10_S45_ABLATION_run"
    / "ckpt"
    / "electra-base-turkish-cased-discriminator"
    / "multidomain"
    / "seed_45"
    / "best_model"
)
K1_BASE = "dbmdz/electra-base-turkish-cased-discriminator"

print("[1/3] Bileşen 1 (K1 ELECTRA-TR LoRA H1_DROP10_S45) yükleniyor...")
k1_tokenizer = AutoTokenizer.from_pretrained(str(K1_ADAPTER), local_files_only=True, use_fast=True)
k1_base = AutoModelForSequenceClassification.from_pretrained(
    K1_BASE, num_labels=4, ignore_mismatched_sizes=True, local_files_only=True
)
k1_model = PeftModel.from_pretrained(k1_base, str(K1_ADAPTER), local_files_only=True)
k1_model.eval().to(DEVICE)

K2_MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
print("[2/3] Bileşen 2 (K2 mDeBERTa-v3-base-xnli-2mil7) yükleniyor...")
k2_tokenizer = AutoTokenizer.from_pretrained(K2_MODEL_ID, local_files_only=True)
k2_model = AutoModelForSequenceClassification.from_pretrained(K2_MODEL_ID, local_files_only=True)
k2_model.eval().to(DEVICE)
k2_id2label = {int(k): v.lower() for k, v in k2_model.config.id2label.items()}

sys.path.insert(0, str((ROOT / "atomizer" / "v2").resolve()))
from atomizer_runtime import LocalAtomizer

GEMMA_ATOMIZER_PATH = ROOT / "atomizer" / "v2" / "outputs" / "google_gemma_4_e2b_it_final_adapter"
print("[3/3] Bileşen 0 (Gemma-4-E2B-it QLoRA Atomizer) yükleniyor...")
local_atomizer: LocalAtomizer | None = None
try:
    if GEMMA_ATOMIZER_PATH.exists():
        local_atomizer = LocalAtomizer(
            adapter_path=str(GEMMA_ATOMIZER_PATH),
            base_model="google/gemma-4-E2B-it",
            max_new_tokens=180,
        )
except Exception as e:
    print(f"Gemma-4 Atomizer yükleme uyarısı: {e}")


# ── VERİ TABANI VE ÖNBELLEK YÜKLEYİCİ (4.667 ÖRNEK) ─────────────────────────
def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        if line.strip()
    ]


def _to_binary(label: str | None) -> str | None:
    if not label:
        return None
    return "supported" if label == "supported" else "unsupported"


DATASET_CATALOG: dict[str, dict[str, dict[str, Any]]] = {
    "GOLD480": {},
    "OOD48": {},
    "AP6": {},
    "RAGBENCH_MED": {},
    "CLAIMRAG_LAW": {},
    "FINDVER_FIN": {},
    "DEV960": {},
    "DEV600_STR": {},
}

# Kısa, temiz ve taşmayan açılır liste etiketleri
DATASET_LABELS = {
    "GOLD480": "TR-FactBench Gold-480 (Altın Test - 480 Vaka)",
    "OOD48": "OOD Vaka Çalışmaları (Alzheimer/Hukuk/Finans - 48 Vaka)",
    "AP6": "AP6 Doğal Türkçe RAG Yanıtları (858 Cümle)",
    "RAGBENCH_MED": "RAGBench-TR Tıp (PubMedQA - 809 Cümle)",
    "CLAIMRAG_LAW": "ClaimRAG-LAW Hukuk (GDPR & Medeni K. - 787 İddia)",
    "FINDVER_FIN": "FinDVer-TR Finans (10-K/10-Q - 125 İddia)",
    "DEV960": "TR-FactBench DEV960-GEN (Genel Geliştirme - 960 Vaka)",
    "DEV600_STR": "TR-FactBench DEV600-STR (Zorlu Stres - 600 Vaka)",
}


def _load_gold480() -> None:
    tfb = ROOT / "tr-factbench-v0.1.0-preview"
    k2_dir = ROOT / "k2_nli"
    gold_rows = _read_jsonl(tfb / "data" / "evaluation" / "gold_v1.0" / "gold" / "TR-FactBench_controlled480_GOLD_v1.0.jsonl")
    k1_rows = {
        (r.get("release_example_id") or r.get("example_id")): r
        for r in _read_jsonl(tfb / "data" / "evaluation" / "gold_v1.0" / "verifier_hold" / "PREDICTIONS_v1.0.jsonl")
    }
    agg_dir = k2_dir / "reports" / "experiments" / "K2-AGG-ABLATION-GOLD480-v1" / "artifacts"
    k2_soft = {
        (r.get("release_example_id") or r.get("example_id")): r["pred_label"]
        for r in _read_jsonl(agg_dir / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__soft_prob_avg.jsonl")
    }
    k2_flat = {
        (r.get("release_example_id") or r.get("example_id")): r["pred_label"]
        for r in _read_jsonl(agg_dir / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__flat.jsonl")
    }
    k2_cp = {
        (r.get("release_example_id") or r.get("example_id")): r["pred_label"]
        for r in _read_jsonl(agg_dir / "predictions__K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7__contradiction_priority.jsonl")
    }
    atoms_by_ex: dict[str, list[dict[str, Any]]] = {}
    for ar in _read_jsonl(k2_dir / "runs" / "K2-PIPE-PRED-GOLD480-v1__mdeberta_base_2mil7" / "atom_predictions.jsonl"):
        eid = ar.get("example_id") or ar.get("source_example_id")
        atoms_by_ex.setdefault(eid, []).append({
            "atom": ar["atom"],
            "label": ar["pred_label"],
            "probs": {
                "entailment": float(ar.get("prob_entailment", 0.0)),
                "neutral": float(ar.get("prob_neutral", 0.0)),
                "contradiction": float(ar.get("prob_contradiction", 0.0)),
            },
        })
    v4_judge = {
        r["example_id"]: r
        for r in _read_jsonl(k2_dir / "reports" / "experiments" / "K3-PREDICATE-AWARE-DEBIASED-LLAMA70B-v1" / "arbitration_predictions_123.jsonl")
    }
    con_judge = {
        r["example_id"]: r
        for r in _read_jsonl(k2_dir / "reports" / "experiments" / "K3-CONSENSUS-LLAMA70B-EVAL-358" / "consensus_judge_predictions_358.jsonl")
    }
    gemma26b_zs = {
        (r.get("release_example_id") or r.get("example_id")): r["predicted_label"]
        for r in _read_jsonl(tfb / "results" / "llm_baselines" / "gold_v1.0" / "google_gemma-4-26b-a4b-it" / "zero_shot" / "predictions.jsonl")
    }

    for r in gold_rows:
        eid = r["release_example_id"]
        num = int(eid.rsplit("_", 1)[-1])
        dom = "finance" if num <= 160 else ("legal" if num <= 320 else "medical")
        k1_p = k1_rows.get(eid, {}).get("predicted_label")
        k2_p = k2_soft.get(eid)
        atoms = atoms_by_ex.get(eid, [])
        is_dis = (k1_p != k2_p)
        v4_r = v4_judge.get(eid) or con_judge.get(eid)
        p0_p = k1_p if not is_dis else (v4_r["judge_decision"] if v4_r else k1_p)
        gz_p = gemma26b_zs.get(eid)
        pa_p = gz_p if (not is_dis and k1_p in ("partially_supported", "contradicted") and gz_p) else p0_p
        pb_p = gz_p if (not is_dis and k1_p in ("partially_supported", "contradicted") and dom == "medical" and gz_p) else p0_p

        special_tags = []
        if r["gold_label"] == "partially_supported" and len(atoms) == 1:
            special_tags.append("1_atom_ps_paradox")
        if r.get("required_adjudication"):
            special_tags.append("human_adjudicated_48")

        DATASET_CATALOG["GOLD480"][eid] = {
            "example_id": eid,
            "dataset": "GOLD480",
            "domain": dom,
            "context": r["context"],
            "question": r.get("question", ""),
            "claim": r["claim"],
            "context_windows": [],
            "gold_label": r["gold_label"],
            "gold_binary": _to_binary(r["gold_label"]),
            "label_scheme": "4class",
            "k1_pred": k1_p,
            "k2_pred": k2_p,
            "k2_flat_pred": k2_flat.get(eid),
            "k2_cp_pred": k2_cp.get(eid),
            "atoms": atoms,
            "n_atoms": len(atoms),
            "is_disagreement": is_dis,
            "v4_judge_decision": v4_r["judge_decision"] if v4_r else None,
            "v4_favored_model": v4_r.get("favored_model") if v4_r else None,
            "v4_reasoning": v4_r.get("reasoning") if v4_r else None,
            "hybrid_P0": p0_p,
            "hybrid_PA": pa_p,
            "hybrid_PB": pb_p,
            "gemma26b_zero_shot": gz_p,
            "special_tags": special_tags,
            "meta_note": f"Anotasyon: {r.get('gold_decision_source', 'consensus')}",
        }


def _load_ood48() -> None:
    k2_dir = ROOT / "k2_nli"
    ood_configs = [
        ("alzheimer_ood_16.jsonl", "OOD-ALZHEIMER-CASE-STUDY-v1", "medical", "Klinik Tıp (Alzheimer)"),
        ("legal_ood_16.jsonl", "OOD-LEGAL-CASE-STUDY-v1", "legal", "Türk İş Hukuku (4857 S.K.)"),
        ("finance_ood_16.jsonl", "OOD-FINANCE-CASE-STUDY-v1", "finance", "Finans (Eurobond & Takas)"),
    ]
    for src_file, exp_folder, dom, sub_title in ood_configs:
        src_rows = {r["id"]: r for r in _read_jsonl(k2_dir / "data" / "processed" / "ood_case_study" / src_file)}
        res_rows = {r["id"]: r for r in _read_jsonl(k2_dir / "reports" / "experiments" / exp_folder / "results.jsonl")}
        for oid, s in src_rows.items():
            res = res_rows.get(oid, {})
            atoms = [
                {
                    "atom": ar.get("atom", ""),
                    "label": ar.get("label", "neutral"),
                    "probs": ar.get("probs", {"entailment": 0.0, "neutral": 1.0, "contradiction": 0.0}),
                }
                for ar in res.get("atom_results", [])
            ]
            k1_p = res.get("k1_pred")
            k2_p = res.get("k2_pred")
            is_dis = (k1_p != k2_p)
            DATASET_CATALOG["OOD48"][oid] = {
                "example_id": oid,
                "dataset": "OOD48",
                "domain": dom,
                "context": s["context"],
                "question": s.get("question", ""),
                "claim": s["claim"],
                "context_windows": [],
                "gold_label": s["gold_label"],
                "gold_binary": _to_binary(s["gold_label"]),
                "label_scheme": "4class",
                "k1_pred": k1_p,
                "k2_pred": k2_p,
                "atoms": atoms,
                "n_atoms": len(atoms),
                "is_disagreement": is_dis,
                "v4_judge_decision": res.get("final_pred") if is_dis else None,
                "v4_favored_model": res.get("favored_model") if is_dis else None,
                "v4_reasoning": res.get("reasoning") if is_dis else None,
                "hybrid_P0": res.get("final_pred"),
                "hybrid_PA": res.get("final_pred"),
                "hybrid_PB": res.get("final_pred"),
                "special_tags": ["ood_zero_leakage"],
                "meta_note": f"{sub_title}",
            }


def _load_ap6() -> None:
    ap6_dir = ROOT / "k2_nli" / "data" / "ap6"
    if not ap6_dir.exists():
        return
    key_map = {r["example_id"]: r["item_id"] for r in _read_jsonl(ap6_dir / "annotation" / "internal" / "item_key_v1.jsonl")}
    lab_map = {r["item_id"]: r for r in _read_jsonl(ap6_dir / "annotation" / "labels_A.jsonl")}
    claims = _read_jsonl(ap6_dir / "verifier" / "ap6_claims.jsonl")
    sys_preds = {r["example_id"]: r for r in _read_jsonl(ap6_dir / "verifier" / "system_predictions_v1.jsonl")}
    v4_preds = {r["example_id"]: r for r in _read_jsonl(ap6_dir / "verifier" / "v4_judge_predictions.jsonl")}
    atoms_by_ex: dict[str, list[dict[str, Any]]] = {}
    for ar in _read_jsonl(ap6_dir / "verifier" / "runs" / "AP6-K2-NLI-v1.7" / "atom_predictions.jsonl"):
        eid = ar["example_id"]
        atoms_by_ex.setdefault(eid, []).append({
            "atom": ar["atom"],
            "label": ar["pred_label"],
            "probs": {
                "entailment": float(ar.get("prob_entailment", 0.0)),
                "neutral": float(ar.get("prob_neutral", 0.0)),
                "contradiction": float(ar.get("prob_contradiction", 0.0)),
            },
        })
    for c in claims:
        eid = c["example_id"]
        iid = key_map.get(eid, "")
        h = lab_map.get(iid, {})
        sp = sys_preds.get(eid, {})
        v4 = v4_preds.get(eid, {})
        gold_lbl = h.get("label", c.get("gold_label", "unverifiable"))
        abst = h.get("abstention") == "yes"
        k1_p = sp.get("k1")
        k2_p = sp.get("k2")
        atoms = atoms_by_ex.get(eid, [])
        is_dis = (k1_p != k2_p) and (k2_p is not None)
        tags = []
        if abst:
            tags.append("abstention")
        DATASET_CATALOG["AP6"][eid] = {
            "example_id": eid,
            "dataset": "AP6",
            "domain": c.get("domain", "medical"),
            "context": c["context"],
            "question": c.get("question", ""),
            "claim": c["claim"],
            "context_windows": [],
            "gold_label": gold_lbl,
            "gold_binary": _to_binary(gold_lbl),
            "label_scheme": "4class_and_binary",
            "k1_pred": k1_p,
            "k2_pred": k2_p,
            "atoms": atoms,
            "n_atoms": len(atoms),
            "is_disagreement": is_dis,
            "v4_judge_decision": v4.get("judge_decision") or sp.get("v4_judge"),
            "v4_favored_model": v4.get("favored_model"),
            "v4_reasoning": v4.get("reasoning"),
            "hybrid_P0": sp.get("hybrid_P0"),
            "hybrid_PA": sp.get("hybrid_PA"),
            "hybrid_PB": sp.get("hybrid_PB"),
            "gemma26b_zero_shot": sp.get("gemma26b_zero_shot"),
            "special_tags": tags,
            "meta_note": f"Üretici: {c.get('model', '')}",
        }


def _load_external_rag_slice(key: str, build_dir: Path, claims_file: str, default_domain: str, scheme_note: str) -> None:
    if not build_dir.exists():
        return
    claims = _read_jsonl(build_dir / claims_file)
    sys_preds = {r["example_id"]: r for r in _read_jsonl(build_dir / "predictions" / "system_predictions.jsonl")}
    v4_preds = {r["example_id"]: r for r in _read_jsonl(build_dir / "predictions" / "v4_judge.jsonl")}
    atoms_by_ex: dict[str, list[dict[str, Any]]] = {}
    for ar in _read_jsonl(build_dir / "predictions" / "k2_windowed_atoms.jsonl"):
        eid = ar["example_id"]
        atoms_by_ex.setdefault(eid, []).append({
            "atom": ar["atom"],
            "label": ar["pred_label"],
            "best_window": ar.get("best_window"),
            "window_labels": ar.get("window_labels", []),
            "probs": {
                "entailment": 1.0 if ar["pred_label"] == "entailment" else 0.0,
                "neutral": 1.0 if ar["pred_label"] == "neutral" else 0.0,
                "contradiction": 1.0 if ar["pred_label"] == "contradiction" else 0.0,
            },
        })
    for c in claims:
        eid = c["example_id"]
        sp = sys_preds.get(eid, {})
        v4 = v4_preds.get(eid, {})
        k1_p = sp.get("k1")
        k2_p = sp.get("k2")
        is_dis = (k1_p != k2_p) and (k2_p is not None)
        atoms = atoms_by_ex.get(eid, [])
        gold_bin = c.get("gold_binary", _to_binary(c.get("gold_label")))
        gold_lbl = c.get("gold_label", gold_bin)
        tags = ["windowed_rag"]
        if sp.get("k1_truncated"):
            tags.append("k1_truncated_512")
        DATASET_CATALOG[key][eid] = {
            "example_id": eid,
            "dataset": key,
            "domain": c.get("domain", default_domain),
            "context": c["context"],
            "question": c.get("question", ""),
            "claim": c["claim"],
            "context_windows": c.get("context_windows", []),
            "gold_label": gold_lbl if key != "RAGBENCH_MED" else gold_bin,
            "gold_binary": gold_bin,
            "label_scheme": "binary" if key == "RAGBENCH_MED" else "3class_and_binary",
            "k1_pred": k1_p,
            "k1_truncated": sp.get("k1_truncated", False),
            "k2_pred": k2_p,
            "atoms": atoms,
            "n_atoms": len(atoms),
            "is_disagreement": is_dis,
            "v4_judge_decision": v4.get("judge_decision") or sp.get("v4_judge"),
            "v4_favored_model": v4.get("favored_model"),
            "v4_reasoning": v4.get("reasoning"),
            "hybrid_P0": sp.get("hybrid_P0"),
            "hybrid_PA": sp.get("hybrid_PA"),
            "hybrid_PB": sp.get("hybrid_PA") if default_domain == "medical" else sp.get("hybrid_P0"),
            "gemma26b_zero_shot": sp.get("gemma26b_zero_shot"),
            "special_tags": tags,
            "meta_note": f"{scheme_note} | {len(c.get('context_windows', []))} Pencere",
        }


def _load_dev_sets() -> None:
    tfb = ROOT / "tr-factbench-v0.1.0-preview"
    prev_run = tfb / "runs" / "preview_evaluations" / "H1_DROP10_S45_PREVIEW"
    k1_dev960 = {r["example_id"]: r["predicted_label"] for r in _read_jsonl(prev_run / "predictions_DEV960-GEN.jsonl")}
    k1_dev600 = {r["example_id"]: r["predicted_label"] for r in _read_jsonl(prev_run / "predictions_DEV600-STR.jsonl")}

    for r in _read_jsonl(tfb / "data" / "evaluation" / "preview_v0.1" / "dev_general.jsonl"):
        eid = r["example_id"]
        DATASET_CATALOG["DEV960"][eid] = {
            "example_id": eid,
            "dataset": "DEV960",
            "domain": r.get("domain", "finance"),
            "context": r["context"],
            "question": r.get("question", ""),
            "claim": r["claim"],
            "context_windows": [],
            "gold_label": r["gold_label"],
            "gold_binary": _to_binary(r["gold_label"]),
            "label_scheme": "4class",
            "k1_pred": k1_dev960.get(eid),
            "k2_pred": None,
            "atoms": [],
            "n_atoms": 0,
            "is_disagreement": False,
            "v4_judge_decision": None,
            "v4_favored_model": None,
            "v4_reasoning": None,
            "hybrid_P0": None,
            "hybrid_PA": None,
            "hybrid_PB": None,
            "special_tags": ["dev_general"],
            "meta_note": f"Grup: {r.get('context_id', '')}",
        }

    for r in _read_jsonl(tfb / "data" / "evaluation" / "preview_v0.1" / "dev_stress.jsonl"):
        eid = r["example_id"]
        DATASET_CATALOG["DEV600_STR"][eid] = {
            "example_id": eid,
            "dataset": "DEV600_STR",
            "domain": r.get("domain", "finance"),
            "context": r["context"],
            "question": r.get("question", ""),
            "claim": r["claim"],
            "context_windows": [],
            "gold_label": r["gold_label"],
            "gold_binary": _to_binary(r["gold_label"]),
            "label_scheme": "4class",
            "k1_pred": k1_dev600.get(eid),
            "k2_pred": None,
            "atoms": [],
            "n_atoms": 0,
            "is_disagreement": False,
            "v4_judge_decision": None,
            "v4_favored_model": None,
            "v4_reasoning": None,
            "hybrid_P0": None,
            "hybrid_PA": None,
            "hybrid_PB": None,
            "special_tags": ["dev_stress"],
            "meta_note": f"Konu: {r.get('topic', '-')}",
        }


_load_gold480()
_load_ood48()
_load_ap6()
_load_external_rag_slice("RAGBENCH_MED", ROOT / "k2_nli" / "data" / "ragbench" / "medical" / "build", "ragbench_tr_medical_claims.jsonl", "medical", "RAGBench PubMedQA")
_load_external_rag_slice("CLAIMRAG_LAW", ROOT / "k2_nli" / "data" / "claimrag_law" / "build", "claimrag_tr_law_claims.jsonl", "legal", "ClaimRAG-LAW")
_load_external_rag_slice("FINDVER_FIN", ROOT / "k2_nli" / "data" / "findver" / "build", "findver_tr_finance_claims.jsonl", "finance", "FinDVer")
_load_dev_sets()


# ── ÇIKARIM VE DOĞRULAMA MOTORU FONKSİYONLARI ─────────────────────────────────

def predict_k1(context: str, question: str, claim: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    text_a = f"[CONTEXT] {context.strip()}"
    text_b = f"[QUESTION] {question.strip()} [CLAIM] {claim.strip()}"
    untrunc = k1_tokenizer(text_a, text_b, truncation=False)
    n_tokens = len(untrunc["input_ids"])
    was_truncated = n_tokens > MAX_LENGTH

    enc = k1_tokenizer(text_a, text_b, max_length=MAX_LENGTH, truncation=True, padding=True, return_tensors="pt")
    enc = {k: v.to(DEVICE) for k, v in enc.items()}
    with torch.no_grad():
        logits = k1_model(**enc).logits
    probs = torch.softmax(logits, dim=-1).squeeze().cpu().tolist()
    pred_id = int(torch.argmax(logits, dim=-1).item())
    pred_label = LABEL_MAP[pred_id]

    p_arr = np.clip(np.array(probs, dtype=np.float64), 1e-12, 1.0)
    entropy = float(-np.sum(p_arr * np.log2(p_arr)))
    sorted_p = np.sort(p_arr)[::-1]
    margin = float(sorted_p[0] - sorted_p[1])
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return {
        "pred_label": pred_label,
        "confidence": float(max(probs)),
        "probs": {LABEL_MAP[i]: float(probs[i]) for i in range(4)},
        "entropy_bits": round(entropy, 3),
        "top2_margin": round(margin, 3),
        "n_tokens": n_tokens,
        "was_truncated": was_truncated,
        "latency_ms": elapsed_ms,
    }


def extract_claim_atoms(claim: str, cached_atoms: list[str] | None = None, use_cache: bool = False) -> tuple[list[str], str, float]:
    t0 = time.perf_counter()
    text = claim.strip()
    if not text:
        return [], "Boş Girdi", 0.0

    if use_cache and cached_atoms:
        return cached_atoms, "Önbellek (Gemma-4 QLoRA)", 0.1

    if local_atomizer is not None:
        try:
            res = local_atomizer.predict(text)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            lat = round((time.perf_counter() - t0) * 1000, 1)
            if res.json_valid and res.atoms:
                return res.atoms, "Gemma-4-E2B QLoRA (GPU)", lat
        except Exception as e:
            print(f"Gemma-4 Atomizer Çıkarım Hatası: {e}")

    if cached_atoms:
        return cached_atoms, "Önbellek (Gemma-4 QLoRA)", 0.1

    return [text], "Doğrudan İddia (Tek Atom)", round((time.perf_counter() - t0) * 1000, 1)


def _split_context_windows(context: str, explicit_windows: list[str] | None = None) -> list[str]:
    if explicit_windows and len(explicit_windows) > 0:
        return [w.strip() for w in explicit_windows if w.strip()]
    paras = [p.strip() for p in re.split(r"\n\s*\n", context.strip()) if p.strip()]
    if len(paras) <= 1:
        return [context.strip()]
    windows: list[str] = []
    cur = ""
    for p in paras:
        cand = f"{cur}\n\n{p}".strip() if cur else p
        if len(cand.split()) <= 260:
            cur = cand
        else:
            if cur:
                windows.append(cur)
            cur = p
    if cur:
        windows.append(cur)
    return windows if windows else [context.strip()]


def _aggregate_atoms(atom_results: list[dict[str, Any]], rule: str) -> str:
    labels = [a["label"] for a in atom_results]
    if not labels:
        return "unverifiable"

    if rule == "contradiction_priority":
        if "contradiction" in labels:
            return "contradicted"
        if all(l == "entailment" for l in labels):
            return "supported"
        if "entailment" in labels:
            return "partially_supported"
        return "unverifiable"

    if rule == "flat":
        if all(l == "entailment" for l in labels):
            return "supported"
        if "entailment" in labels:
            return "partially_supported"
        if "contradiction" in labels:
            return "contradicted"
        return "unverifiable"

    if all(l == "entailment" for l in labels):
        return "supported"
    if "entailment" in labels:
        return "partially_supported"
    avg_e = sum(a["probs"]["entailment"] for a in atom_results) / len(atom_results)
    avg_n = sum(a["probs"]["neutral"] for a in atom_results) / len(atom_results)
    avg_c = sum(a["probs"]["contradiction"] for a in atom_results) / len(atom_results)
    if avg_c > max(avg_e, avg_n):
        return "contradicted"
    return "unverifiable"


def predict_k2_nli(
    context: str,
    atoms: list[str],
    agg_rule: str = "soft_prob_avg",
    windowing_mode: str = "auto",
    explicit_windows: list[str] | None = None,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    use_windows = (
        windowing_mode == "windowed"
        or (windowing_mode == "auto" and ((explicit_windows and len(explicit_windows) > 1) or len(context.split()) > 320))
    )
    windows = _split_context_windows(context, explicit_windows) if use_windows else [context.strip()]

    atom_results = []
    for atom in atoms:
        win_scores = []
        for w_idx, win_text in enumerate(windows):
            enc = k2_tokenizer(
                win_text,
                atom.strip(),
                max_length=MAX_LENGTH,
                truncation=True,
                padding=True,
                return_tensors="pt",
            )
            enc = {k: v.to(DEVICE) for k, v in enc.items()}
            with torch.no_grad():
                logits = k2_model(**enc).logits
            probs = torch.softmax(logits, dim=-1).squeeze().cpu().tolist()
            prob_dict = {k2_id2label[i]: float(probs[i]) for i in range(len(probs))}
            pred_lbl = max(prob_dict, key=prob_dict.get)
            win_scores.append({
                "window_index": w_idx,
                "label": pred_lbl,
                "probs": {
                    "entailment": prob_dict.get("entailment", 0.0),
                    "neutral": prob_dict.get("neutral", 0.0),
                    "contradiction": prob_dict.get("contradiction", 0.0),
                },
            })

        chosen = None
        for target_lbl, p_key in [("entailment", "entailment"), ("contradiction", "contradiction")]:
            hits = [w for w in win_scores if w["label"] == target_lbl]
            if hits:
                chosen = max(hits, key=lambda x: x["probs"][p_key])
                break
        if chosen is None:
            chosen = max(win_scores, key=lambda x: x["probs"]["neutral"])

        atom_results.append({
            "atom": atom,
            "label": chosen["label"],
            "probs": chosen["probs"],
            "best_window": chosen["window_index"],
            "n_windows_tested": len(windows),
            "window_labels": [w["label"] for w in win_scores],
        })

    pred_soft = _aggregate_atoms(atom_results, "soft_prob_avg")
    pred_flat = _aggregate_atoms(atom_results, "flat")
    pred_cp = _aggregate_atoms(atom_results, "contradiction_priority")
    chosen_pred = _aggregate_atoms(atom_results, agg_rule)

    avg_e = sum(a["probs"]["entailment"] for a in atom_results) / max(len(atom_results), 1)
    avg_n = sum(a["probs"]["neutral"] for a in atom_results) / max(len(atom_results), 1)
    avg_c = sum(a["probs"]["contradiction"] for a in atom_results) / max(len(atom_results), 1)

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    return {
        "pred_label": chosen_pred,
        "all_rule_preds": {
            "soft_prob_avg": pred_soft,
            "flat": pred_flat,
            "contradiction_priority": pred_cp,
        },
        "avg_probs": {
            "entailment": round(avg_e, 4),
            "neutral": round(avg_n, 4),
            "contradiction": round(avg_c, 4),
        },
        "atoms": atom_results,
        "used_windowing": use_windows and len(windows) > 1,
        "n_windows": len(windows),
        "latency_ms": elapsed_ms,
    }


FEWSHOT_PRECEDENTS_V4 = """EMSAL KARARLAR (ÖNCEKİ MAHKEME İÇTİHATLARI):

[EMSAL 1 - İki parçalı doğru iddia]
BAĞLAM: "Alışverişlerde işyeri bir FAST-TR Karekod oluşturabilir. Müşteri bu karekodu mobil bankacılık uygulamasından okutarak FAST ödemesini başlatır."
İDDİA: "Alışverişte müşteri, işyerinin oluşturduğu karekodu mobil uygulamasından okutarak FAST ödemesi başlatabilir."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "işyeri karekod oluşturabilir"
2. "müşteri mobil uygulamadan karekodu okutarak FAST ödemesi başlatabilir"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): supported
- Model B (Atomik Analiz): supported
HAKEM KARARI:
```json
{
  "reasoning": "İddiadaki her iki önerme de bağlam tarafından doğrudan ve açıkça desteklenmektedir. Her iki model de isabetli karar vermiştir.",
  "favored_model": "Model B",
  "final_decision": "supported"
}
```

[EMSAL 2 - Kısmi Destek Kuralı: En az bir doğru + en az bir bağlam dışı/çelişkili parça]
BAĞLAM: "KOAH'ta kronik öksürük balgamlı veya balgamsız olabilir. Hastalığın alevlenme dönemlerinde balgamın sarı-yeşil renge dönmesi mümkündür."
İDDİA: "Sarı-yeşil balgam alevlenmede görülebilir, bu renk değişikliği zatürre tanısını kesinleştirir."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "Sarı-yeşil balgam alevlenmede görülebilir"
2. "bu renk değişikliği zatürre tanısını kesinleştirir"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "DİKKAT: İddiada doğru bir bilgi (balgam rengi) ile bağlamda olmayan bir bilgi (zatürre) bir aradadır. Tanım gereği bu vaka ASLA contradicted olamaz; doğru parça içerdiği için partially_supported olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "partially_supported"
}
```

[EMSAL 3 - Tam Çelişki Kuralı: Sıfır destek + en az bir doğrudan zıtlık]
BAĞLAM: "Ödeme İste servisinde farklı kullanım modelleri bulunur. Modeller, talebin kabul edilebileceği tarih ile ödemenin beklendiği tarihe göre değişebilir."
İDDİA: "Ödeme İste servisinde tarihe göre değişmeyen tek bir kullanım modeli vardır."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "Ödeme İste servisi vardır"
2. "tarihe göre değişmeyen tek bir kullanım modeli vardır"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): partially_supported
HAKEM KARARI:
```json
{
  "reasoning": "İddianın temel iddiası 'tek bir model olduğu' yönündedir ve bu bilgi bağlamla taban tabana zıttır. Giriş ifadesi bağımsız bir olgu değil, zıt önermenin taşıyıcısıdır. Model A'nın contradicted kararı doğrudur.",
  "favored_model": "Model A",
  "final_decision": "contradicted"
}
```

[EMSAL 4 - Bilgi Yokluğu / Semantik Yüklem Kuralı]
BAĞLAM: "FAST sistemi 8 Ocak 2021 tarihinde işletime alınmıştır. Ödeme talimatları saniyeler içinde sonuçlanabilir."
İDDİA: "FAST bildirimi alan taraf tamamlanan ödemeyi bir saat içinde geri çevirebilir."
İDDİANIN ATOMİK ÖNERMELERİ:
1. "FAST bildirimi alan taraf tamamlanan ödemeyi bir saat içinde geri çevirebilir"
BİLİRKİŞİ DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): contradicted
- Model B (Atomik Analiz): unverifiable
HAKEM KARARI:
```json
{
  "reasoning": "Bağlam FAST sisteminden bahsetse de ödemenin geri çevrilip çevrilemeyeceği eylemine/yüklemine dair hiçbir bilgi içermemektedir. Çelişki yoktur, yüklem doğrulanmamaktadır. Bu nedenle karar unverifiable olmalıdır. Model B haklıdır.",
  "favored_model": "Model B",
  "final_decision": "unverifiable"
}
```"""


def build_judge_prompt(
    context: str,
    claim: str,
    k1_pred: str,
    k2_pred: str,
    atoms: list[str],
    prompt_version: str = "V4",
) -> str:
    if prompt_version in ("BLIND_8SHOT", "BLIND_0SHOT"):
        mode_note = (
            "[Eğitim kümesinden seçilmiş 8 sabit çözülmüş örnek (few_shot_8) bu sistem istemiyle birlikte gönderilir]"
            if prompt_version == "BLIND_8SHOT"
            else "[Sıfır örnekli (zero_shot) koşul — örnek gösterilmeden doğrudan karar istenir]"
        )
        return f"""Sen, Türkçe kaynak-temelli olgusal doğrulama benchmarkında çalışan dikkatli bir sınıflandırıcısın. (KÖR HAKEM MODU — Model A ve Model B kararları gizlenmiştir)

GÖREV:
Yalnızca verilen BAĞLAM ile tek bir İDDİA arasındaki olgusal ilişkiyi değerlendir. Dış bilgi kullanma.

{mode_note}

ETİKETLER VE KARAR KURALI:
1. supported: İddiadaki bütün atomik önermeler bağlam tarafından desteklenir.
2. partially_supported: İddia en az iki atomik önerme içerir; en az bir atom desteklenir, en az bir başka atom bağlamda bulunmaz veya çelişir.
3. contradicted: İddiada desteklenen atom yoktur ve en az bir atom bağlamdaki açık bilgiyle çelişir.
4. unverifiable: İddiadaki hiçbir atom bağlam tarafından desteklenmez ve açıkça çürütülmez.

BAĞLAM:
\"\"\"{context}\"\"\"

İDDİA:
\"\"\"{claim}\"\"\"

SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Kısa Türkçe gerekçe>",
  "favored_model": "Kör Hakem (Bağımsız)",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}}
```"""

    atoms_str = "\n".join([f'{i+1}. "{a}"' for i, a in enumerate(atoms)]) if atoms else f'1. "{claim}"'
    predicate_block = ""
    if prompt_version == "V4":
        predicate_block = """
*** ÇOK ÖNEMLİ: SEMANTİK YÜKLEM VE EYLEM KURALI (V4 PROTOKOLÜ) ***
- Bir cümlenin sadece öznesinin veya kavram adının bağlamda geçmesi o cümlenin "desteklenen parçası" SAYILMAZ!
- Desteklenen bir parçadan söz edebilmek için, özneye yüklenen eylemin/özelliğin/hükmün de bağlamda açıkça doğrulanması gerekir.
- Eğer iddiadaki önermelerin özneleri bağlamda geçiyor fakat iddia edilen eylemler/hükümler bağlamda yer almıyorsa (eylem doğrulanmıyorsa ve bağlamda bu konuda bir bilgi yoksa), karar kesinlikle partially_supported DEĞİL, 'unverifiable' OLMALIDIR!
- Bir iddianın içinde hem doğrulanmış bir gerçek hem de açık bir zıtlık varsa asla contradicted deme, partially_supported seç!
"""
    return f"""Sen, iki farklı yapay zeka modelinin çelişkisini çözen tarafsız bir Baş Hakemsin.

GÖREV:
Aşağıdaki BAĞLAM ve İDDİA üzerinde iki farklı bilirkişi modeli değerlendirme yapmıştır. İddianın bağımsız olarak ayrıştırılmış atomik önermelerini ve bilirkişi modellerinin kararlarını inceleyerek hakem kararını ver.

{FEWSHOT_PRECEDENTS_V4}

--------------------------------------------------
ŞİMDİ KARAR VERMEN GEREKEN YENİ VAKA:

BAĞLAM:
\"\"\"{context}\"\"\"

İDDİA:
\"\"\"{claim}\"\"\"

İDDİANIN ATOMİK ÖNERMELERİ (Ön İnceleme - Bağımsız Ayrıştırıcı Tarafından Bölünmüş Yapıtaşları):
{atoms_str}

BİLİRKİŞİ MODELLERİNİN DEĞERLENDİRMELERİ:
- Model A (Bütüncül Analiz): {k1_pred}
- Model B (Atomik Analiz): {k2_pred}

ETİKET KURALLARI:
1. supported: İddiadaki BÜTÜN önermeler bağlam tarafından açıkça doğrulanmaktadır.
2. partially_supported: İddiada bağlamın doğruladığı en az bir gerçek eylem/bilgi varken, ek olarak bağlamda olmayan veya çelişen başka bir önerme yer alıyorsa bu etiket ZORUNLUDUR.
3. contradicted: İddiada bağlam tarafından doğrulanan HİÇBİR parça yoksa ve doğrudan açık bir yalan/zıtlık varsa seçilir.
4. unverifiable: Bağlamda önermelere dair ne doğrulama ne çürütme varsa (bilgi yokluğu) seçilir.
{predicate_block}
SADECE aşağıdaki JSON formatında çıktı üret:
```json
{{
  "reasoning": "<Bağlamdaki kanıtı ve önermelerin eylemlerini tarafsızca değerlendiren en fazla 2 cümlelik mantıklı Türkçe gerekçe>",
  "favored_model": "<Model A | Model B | Neither>",
  "final_decision": "<supported | partially_supported | contradicted | unverifiable>"
}}
```"""


def _lookup_cached_blind_baseline(example_id: str, judge_model: str, prompt_version: str) -> dict[str, Any] | None:
    slug = judge_model.replace("/", "_")
    sub = "few_shot_8" if prompt_version == "BLIND_8SHOT" else "zero_shot"
    p_file = ROOT / "tr-factbench-v0.1.0-preview" / "results" / "llm_baselines" / "gold_v1.0" / slug / sub / "predictions.jsonl"
    if not p_file.exists():
        return None
    for r in _read_jsonl(p_file):
        eid = r.get("release_example_id") or r.get("example_id")
        if eid == example_id and r.get("predicted_label"):
            return r
    return None


def call_live_meta_judge(
    context: str,
    claim: str,
    k1_pred: str,
    k2_pred: str,
    atoms: list[str],
    judge_model: str = "meta-llama/llama-3.3-70b-instruct",
    prompt_version: str = "V4",
    cached_record: dict[str, Any] | None = None,
    use_cached_judge: bool = True,
) -> dict[str, Any]:
    prompt = build_judge_prompt(context, claim, k1_pred, k2_pred, atoms, prompt_version=prompt_version)

    if use_cached_judge and cached_record:
        if prompt_version in ("BLIND_8SHOT", "BLIND_0SHOT"):
            b_hit = _lookup_cached_blind_baseline(cached_record.get("example_id", ""), judge_model, prompt_version)
            if b_hit:
                dec = b_hit["predicted_label"]
                fav = (
                    "Kör Hakem (K1 ile Aynı)"
                    if dec == k1_pred and dec != k2_pred
                    else ("Kör Hakem (K2 ile Aynı)" if dec == k2_pred and dec != k1_pred else "Kör Hakem (Bağımsız)")
                )
                return {
                    "final_decision": dec,
                    "favored_model": fav,
                    "reasoning": b_hit.get("brief_rationale") or "Dondurulmuş kör hakem deney kaydından yüklendi.",
                    "latency": round(float(b_hit.get("latency_seconds", 0.01)), 2),
                    "source": f"Kör Hakem Önbelleği ({'8-Örnekli' if prompt_version == 'BLIND_8SHOT' else 'Sıfır-Örnekli'})",
                    "prompt": prompt,
                }
        elif cached_record.get("v4_judge_decision") and prompt_version == "V4" and "llama-3.3-70b" in judge_model:
            return {
                "final_decision": cached_record["v4_judge_decision"],
                "favored_model": cached_record.get("v4_favored_model") or "Model A/B (Önbellek)",
                "reasoning": cached_record.get("v4_reasoning") or "Dondurulmuş deney kaydından yüklendi.",
                "latency": 0.01,
                "source": "Deney Önbelleği (SHA-256)",
                "prompt": prompt,
            }

    if not OPENROUTER_API_KEY:
        return {
            "final_decision": k1_pred,
            "favored_model": "Model A (API Anahtarı Yok)",
            "reasoning": "OpenRouter API anahtarı bulunamadığı için varsayılan K1 kararı uygulandı.",
            "latency": 0.0,
            "source": "Fallback",
            "prompt": prompt,
        }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/EngindalgaMaku/tr-factbench",
        "X-OpenRouter-Title": f"TR-FactBench ({judge_model})",
    }
    payload = {
        "model": judge_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 420,
    }

    t0 = time.perf_counter()
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            verify=False,
            timeout=65,
        )
        lat = round(time.perf_counter() - t0, 2)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            json_str = match.group(1) if match else content
            s_idx, e_idx = json_str.find("{"), json_str.rfind("}")
            if s_idx >= 0 and e_idx > s_idx:
                json_str = json_str[s_idx : e_idx + 1]
            data = json.loads(json_str)
            dec = str(data.get("final_decision", "")).strip().lower()
            if dec not in ["supported", "partially_supported", "contradicted", "unverifiable"]:
                dec = k1_pred
            return {
                "final_decision": dec,
                "favored_model": data.get("favored_model", "Neither"),
                "reasoning": data.get("reasoning", "Gerekçe üretilmedi."),
                "latency": lat,
                "source": f"Canlı API ({judge_model.split('/')[-1]})",
                "prompt": prompt,
            }
        else:
            err_msg = f"API Hatası (HTTP {resp.status_code})"
            return {
                "final_decision": k1_pred,
                "favored_model": "Model A (Fallback)",
                "reasoning": err_msg,
                "latency": lat,
                "source": "Fallback",
                "prompt": prompt,
            }
    except Exception as e:
        return {
            "final_decision": k1_pred,
            "favored_model": "Model A (Fallback)",
            "reasoning": f"İstek hatası: {e}",
            "latency": 0.0,
            "source": "Fallback",
            "prompt": prompt,
        }


# ── VERİ SETİ FİLTRELEME VE SEÇİM YARDIMCILARI ───────────────────────────────

def filter_dataset_examples(
    dataset_key: str,
    filter_mode: str,
    domain_filter: str,
    search_query: str = "",
) -> list[tuple[str, str]]:
    records = list(DATASET_CATALOG.get(dataset_key, {}).values())
    filtered = []
    q = search_query.strip().lower()

    for r in records:
        if domain_filter != "ALL" and r.get("domain") != domain_filter:
            continue

        k1_p = r.get("k1_pred")
        k2_p = r.get("k2_pred")
        gold_4 = r.get("gold_label")
        gold_bin = r.get("gold_binary")
        is_bin_ds = r.get("label_scheme") == "binary"

        def _is_ok(pred: str | None) -> bool:
            if not pred:
                return False
            if is_bin_ds:
                return _to_binary(pred) == gold_bin
            return pred == gold_4

        k1_ok = _is_ok(k1_p)
        k2_ok = _is_ok(k2_p)
        p0_ok = _is_ok(r.get("hybrid_P0"))
        is_dis = bool(r.get("is_disagreement"))

        if filter_mode == "DISAGREEMENT" and not is_dis:
            continue
        elif filter_mode == "CONSENSUS" and (is_dis or k2_p is None):
            continue
        elif filter_mode == "ONLY_K1_CORRECT" and not (k1_ok and not k2_ok and k2_p is not None):
            continue
        elif filter_mode == "ONLY_K2_CORRECT" and not (k2_ok and not k1_ok):
            continue
        elif filter_mode == "BOTH_WRONG" and not (not k1_ok and not k2_ok and k2_p is not None):
            continue
        elif filter_mode == "JUDGE_RESCUED" and not (is_dis and p0_ok and (not k1_ok or not k2_ok)):
            continue
        elif filter_mode == "PARADOX_1ATOM_PS" and "1_atom_ps_paradox" not in r.get("special_tags", []):
            continue
        elif filter_mode == "HUMAN_ADJUDICATED_48" and "human_adjudicated_48" not in r.get("special_tags", []):
            continue
        elif filter_mode == "K1_TRUNCATED" and "k1_truncated_512" not in r.get("special_tags", []):
            continue

        if q:
            haystack = f"{r['example_id']} {r['claim']} {r['context']} {r.get('question', '')}".lower()
            if q not in haystack:
                continue

        dom_lbl = DOMAIN_TR.get(r.get("domain", ""), "")
        status_tag = "Ayrışma" if is_dis else ("Uzlaşma" if k2_p else "K1")
        gold_disp = LABEL_SHORT_TR.get(gold_bin if is_bin_ds else gold_4, gold_4)
        claim_snip = r["claim"][:70] + ("..." if len(r["claim"]) > 70 else "")
        label_str = f"{r['example_id']} | {dom_lbl} | {status_tag} | Gold: {gold_disp} — {claim_snip}"
        filtered.append((label_str, r["example_id"]))

    return filtered[:400]


def get_dataset_summary_badge(dataset_key: str, total_matching: int) -> str:
    all_recs = DATASET_CATALOG.get(dataset_key, {})
    n_all = len(all_recs)
    n_dis = sum(1 for r in all_recs.values() if r.get("is_disagreement"))
    n_con = sum(1 for r in all_recs.values() if not r.get("is_disagreement") and r.get("k2_pred") is not None)
    return (
        f"<div style='font-size:0.86em; color:#475569; padding:4px 2px'>"
        f"Seçili Küme: <b>{n_all}</b> toplam vaka (<b>{n_dis}</b> K1≠K2 ayrışma, <b>{n_con}</b> uzlaşma) &nbsp;&bull;&nbsp; "
        f"Filtreye uyan: <b style='color:#0f172a'>{total_matching}</b> vaka"
        f"</div>"
    )


# ── ANA ÇALIŞTIRMA VE HTML RAPOR ÜRETİCİSİ ───────────────────────────────────

def execute_workbench(
    context: str,
    question: str,
    claim: str,
    exec_mode: str,
    routing_policy: str,
    agg_rule: str,
    windowing_mode: str,
    judge_model: str,
    judge_prompt_ver: str,
    use_cached_judge: bool,
    dataset_key: str,
    selected_example_id: str | None,
) -> tuple[str, str, str, str, str]:
    if not context.strip() or not claim.strip():
        msg = "<div style='color:#b91c1c;padding:12px 16px;border:1px solid #fecaca;background:#fef2f2;border-radius:8px;font-weight:600'>Lütfen Bağlam ve İddia alanlarını doldurun veya yukarıdaki listeden bir vaka seçin.</div>"
        return msg, "", "", "", ""

    t_total_start = time.perf_counter()

    cached_rec: dict[str, Any] | None = None
    if selected_example_id and selected_example_id in DATASET_CATALOG.get(dataset_key, {}):
        cand = DATASET_CATALOG[dataset_key][selected_example_id]
        if cand["claim"].strip() == claim.strip() and cand["context"].strip() == context.strip():
            cached_rec = cand

    explicit_windows = cached_rec.get("context_windows", []) if cached_rec else []

    # 1. K1 ÇIKARIMI
    run_k1 = exec_mode in ("HYBRID_FULL", "ONLY_K1", "K1_AND_K2")
    k1_res = predict_k1(context, question, claim) if run_k1 else None

    # 2. BİLEŞEN 0 (ATOMIZER) VE K2 NLI ÇIKARIMI
    run_atomizer = exec_mode in ("HYBRID_FULL", "ONLY_ATOMIZER", "ONLY_K2", "K1_AND_K2")
    run_k2 = exec_mode in ("HYBRID_FULL", "ONLY_K2", "K1_AND_K2")

    atoms: list[str] = []
    atomizer_src = "Çalıştırılmadı"
    atomizer_lat_ms = 0.0
    k2_res = None

    if run_atomizer:
        cached_atom_texts = [a["atom"] for a in cached_rec.get("atoms", [])] if cached_rec else None
        atoms, atomizer_src, atomizer_lat_ms = extract_claim_atoms(
            claim,
            cached_atoms=cached_atom_texts,
            use_cache=(local_atomizer is None and cached_atom_texts is not None),
        )

    if run_k2 and atoms:
        k2_res = predict_k2_nli(
            context=context,
            atoms=atoms,
            agg_rule=agg_rule,
            windowing_mode=windowing_mode,
            explicit_windows=explicit_windows,
        )

    # 3. K3 HİBRİT YÖNLENDİRME VE META-HAKEM
    k1_label = k1_res["pred_label"] if k1_res else None
    k2_label = k2_res["pred_label"] if k2_res else None

    judge_res = None
    final_label = None
    decision_mechanism = ""
    routing_explanation = ""

    if exec_mode == "ONLY_ATOMIZER":
        final_label = "supported"
        decision_mechanism = f"Bileşen 0 (Atomizer) — {len(atoms)} Atomik Önerme Üretildi"
    elif exec_mode == "ONLY_K1" and k1_label:
        final_label = k1_label
        decision_mechanism = "Bileşen 1 (K1: ELECTRA-TR LoRA Doğrudan Sınıflandırıcı)"
    elif exec_mode == "ONLY_K2" and k2_label:
        final_label = k2_label
        decision_mechanism = f"Bileşen 2 (K2: Atomik Zero-Shot NLI — {agg_rule})"
    elif exec_mode == "K1_AND_K2" and k1_label and k2_label:
        is_con = (k1_label == k2_label)
        final_label = k1_label
        decision_mechanism = (
            f"K1 ve K2 Uzlaştı ({LABEL_SHORT_TR[k1_label]})"
            if is_con
            else f"K1 ({LABEL_SHORT_TR[k1_label]}) ≠ K2 ({LABEL_SHORT_TR[k2_label]}) Ayrışması (Hakem Kapalı)"
        )
    elif exec_mode == "HYBRID_FULL" and k1_label and k2_label:
        is_consensus = (k1_label == k2_label)
        domain_val = cached_rec.get("domain", "medical") if cached_rec else "medical"

        if routing_policy == "FORCE_JUDGE":
            judge_res = call_live_meta_judge(
                context, claim, k1_label, k2_label, atoms,
                judge_model=judge_model, prompt_version=judge_prompt_ver,
                cached_record=cached_rec, use_cached_judge=use_cached_judge,
            )
            final_label = judge_res["final_decision"]
            decision_mechanism = f"Zorunlu Meta-Hakem Denetimi ({judge_res['favored_model']})"
            routing_explanation = "K1=K2 uzlaşmasına bakılmaksızın doğrudan K3 Meta-Hakem çağrıldı."
        elif not is_consensus:
            judge_res = call_live_meta_judge(
                context, claim, k1_label, k2_label, atoms,
                judge_model=judge_model, prompt_version=judge_prompt_ver,
                cached_record=cached_rec, use_cached_judge=use_cached_judge,
            )
            final_label = judge_res["final_decision"]
            decision_mechanism = f"K1≠K2 Ayrışma Arbitrasyonu ({judge_res['favored_model']})"
            routing_explanation = "K1 (Bütüncül) ve K2 (Atomik NLI) farklı sınıflar tahmin ettiği için vaka K3 Meta-Hakeme yönlendirildi."
        else:
            needs_pa_audit = (
                routing_policy == "PA" and k1_label in ("partially_supported", "contradicted")
            ) or (
                routing_policy == "PB" and k1_label in ("partially_supported", "contradicted") and domain_val == "medical"
            )
            if needs_pa_audit:
                if cached_rec and cached_rec.get("gemma26b_zero_shot") and use_cached_judge:
                    final_label = cached_rec["gemma26b_zero_shot"]
                    decision_mechanism = f"{routing_policy} Uzlaşma Denetimi (Kör Gemma-4-26B)"
                    routing_explanation = (
                        f"K1 ve K2 '{LABEL_SHORT_TR[k1_label]}' üzerinde uzlaştı; {routing_policy} politikası gereği "
                        f"vaka Kör Gemma-4-26B denetimine yönlendirildi -> {LABEL_SHORT_TR[final_label]}."
                    )
                else:
                    judge_res = call_live_meta_judge(
                        context, claim, k1_label, k2_label, atoms,
                        judge_model=judge_model, prompt_version=judge_prompt_ver,
                        cached_record=cached_rec, use_cached_judge=use_cached_judge,
                    )
                    final_label = judge_res["final_decision"]
                    decision_mechanism = f"{routing_policy} Riskli Uzlaşma Denetimi (Meta-Hakem)"
                    routing_explanation = f"K1 ve K2 '{LABEL_SHORT_TR[k1_label]}' üzerinde uzlaştı; {routing_policy} politikası uyarınca hakeme doğrulattırıldı."
            else:
                final_label = k1_label
                decision_mechanism = "K1 == K2 Doğrudan Uzlaşma (%94.13 Güvenilirlik, 0 API Çağrısı)"
                routing_explanation = (
                    "İki yerel model bağımsız olarak aynı kararda birleşti. "
                    "Uzlaşma alanında LLM hakemi baypas edilerek sıfır API maliyetiyle karar onaylandı."
                )

    total_elapsed_s = round(time.perf_counter() - t_total_start, 2)

    # ── TEMİZ VE AKADEMİK HTML KARTLARI ───────────────────────────────────────

    # 1. K1 KARTI
    if k1_res:
        k1_c = LABEL_COLOR[k1_label]
        k1_bg = LABEL_BG[k1_label]
        prob_bars = "".join([
            f"<div style='margin:6px 0;font-size:0.84em'>"
            f"<div style='display:flex;justify-content:space-between;color:#334155'><span>{LABEL_TR[lbl]}</span><b>%{val*100:.1f}</b></div>"
            f"<div style='background:#e2e8f0;border-radius:4px;height:6px;overflow:hidden;margin-top:3px'>"
            f"<div style='background:{LABEL_COLOR[lbl]};width:{val*100:.1f}%;height:100%'></div></div></div>"
            for lbl, val in k1_res["probs"].items()
        ])
        trunc_txt = f"⚠️ 512 Sınırında Kesildi ({k1_res['n_tokens']} token)" if k1_res["was_truncated"] else f"{k1_res['n_tokens']} / 512 token"
        q_warn = (
            "<div style='background:#fffbeb;border-left:3px solid #d97706;padding:6px 10px;border-radius:4px;font-size:0.78em;color:#78350f;margin-bottom:10px'>"
            "⚠️ <b>Soru Alanı Boş:</b> K1 modeli <code>Bağlam + Soru + İddia</code> üçlü şablonuyla eğitilmiştir; soru girilmediğinde K1 performansı düşebilir."
            "</div>"
            if not question.strip()
            else ""
        )
        k1_html = f"""
        <div style='border:1px solid #cbd5e1; border-top:4px solid {k1_c}; border-radius:10px; padding:18px; background:#ffffff; height:100%'>
          <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px'>
            <span style='font-size:0.92em; color:#0f172a; font-weight:700'>Bileşen 1 (K1) — ELECTRA-TR LoRA</span>
            <span style='font-size:0.78em; color:#475569; background:#f1f5f9; padding:2px 8px; border-radius:6px'>{k1_res['latency_ms']} ms &bull; {trunc_txt}</span>
          </div>
          {q_warn}
          <div style='background:{k1_bg}; padding:12px 14px; border-radius:8px; margin-bottom:14px'>
            <div style='font-size:1.2em; font-weight:800; color:{k1_c}'>{LABEL_TR[k1_label]}</div>
            <div style='font-size:0.82em; color:#475569; margin-top:4px'>
              Güven: <b>%{k1_res['confidence']*100:.1f}</b> &nbsp;&bull;&nbsp;
              Entropi: <b>{k1_res['entropy_bits']} bit</b> &nbsp;&bull;&nbsp;
              Marj: <b>{k1_res['top2_margin']:.3f}</b>
            </div>
          </div>
          <div>{prob_bars}</div>
        </div>
        """
    else:
        k1_html = "<div style='border:1px dashed #cbd5e1;border-radius:10px;padding:24px;color:#64748b;text-align:center'>Bileşen 1 (K1) bu modda çalıştırılmadı.</div>"

    # 2. K2 KARTI
    if exec_mode == "ONLY_ATOMIZER":
        atom_items = "".join([
            f"<div style='margin:6px 0;padding:8px 12px;background:#f8fafc;border-left:3px solid #2563eb;border-radius:4px;font-size:0.9em'><b>Atom {i+1}:</b> {html_lib.escape(a)}</div>"
            for i, a in enumerate(atoms)
        ])
        k2_html = f"""
        <div style='border:1px solid #cbd5e1; border-top:4px solid #2563eb; border-radius:10px; padding:18px; background:#ffffff; height:100%'>
          <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px'>
            <span style='font-size:0.92em; color:#0f172a; font-weight:700'>Bileşen 0 — Gemma-4-E2B QLoRA Atomizer</span>
            <span style='font-size:0.78em; color:#475569; background:#f1f5f9; padding:2px 8px; border-radius:6px'>{len(atoms)} Atom</span>
          </div>
          {atom_items}
        </div>
        """
    elif k2_res:
        k2_c = LABEL_COLOR[k2_label]
        k2_bg = LABEL_BG[k2_label]
        atom_cards = ""
        for i, a in enumerate(k2_res["atoms"]):
            albl = a["label"]
            ac = ATOM_NLI_COLOR[albl]
            win_info = f" (Pencere #{a['best_window']+1}/{a['n_windows_tested']})" if a.get("n_windows_tested", 1) > 1 else ""
            atom_cards += f"""
            <div style='background:#f8fafc; border-left:3px solid {ac}; padding:8px 12px; margin:6px 0; border-radius:4px; font-size:0.85em'>
              <div style='color:#0f172a; font-weight:600'>Atom {i+1}: "{html_lib.escape(a['atom'])}"</div>
              <div style='margin-top:3px; display:flex; justify-content:space-between; color:#475569'>
                <span style='color:{ac}; font-weight:700'>{ATOM_NLI_TR[albl]}{win_info}</span>
                <span>E:%{a['probs']['entailment']*100:.0f} | N:%{a['probs']['neutral']*100:.0f} | C:%{a['probs']['contradiction']*100:.0f}</span>
              </div>
            </div>
            """
        rc = k2_res["all_rule_preds"]
        win_txt = f"{k2_res['n_windows']} Pencere" if k2_res["used_windowing"] else "Tam Bağlam"
        k2_html = f"""
        <div style='border:1px solid #cbd5e1; border-top:4px solid {k2_c}; border-radius:10px; padding:18px; background:#ffffff; height:100%'>
          <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px'>
            <span style='font-size:0.92em; color:#0f172a; font-weight:700'>Bileşen 2 (K2) — Atomik Zero-Shot NLI</span>
            <span style='font-size:0.78em; color:#475569; background:#f1f5f9; padding:2px 8px; border-radius:6px'>{k2_res['latency_ms']} ms &bull; {win_txt}</span>
          </div>
          <div style='background:{k2_bg}; padding:12px 14px; border-radius:8px; margin-bottom:10px'>
            <div style='font-size:1.2em; font-weight:800; color:{k2_c}'>{LABEL_TR[k2_label]}</div>
            <div style='font-size:0.82em; color:#475569; margin-top:4px'>
              <b>{len(atoms)} Önerme</b> &nbsp;&bull;&nbsp;
              Soft-Prob: <b>{LABEL_SHORT_TR[rc['soft_prob_avg']]}</b> |
              Flat: <b>{LABEL_SHORT_TR[rc['flat']]}</b> |
              CP: <b>{LABEL_SHORT_TR[rc['contradiction_priority']]}</b>
            </div>
          </div>
          <div style='max-height:240px; overflow-y:auto'>{atom_cards}</div>
        </div>
        """
    else:
        k2_html = "<div style='border:1px dashed #cbd5e1;border-radius:10px;padding:24px;color:#64748b;text-align:center'>Bileşen 2 (K2 NLI) bu modda çalıştırılmadı.</div>"

    # 3. K3 KARTI
    if exec_mode == "HYBRID_FULL" and k1_label and k2_label:
        if judge_res:
            jc = LABEL_COLOR[judge_res["final_decision"]]
            k3_html = f"""
            <div style='border:1px solid #cbd5e1; border-top:4px solid #b45309; background:#ffffff; border-radius:10px; padding:18px; margin-top:12px'>
              <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px'>
                <span style='font-size:0.95em; color:#0f172a; font-weight:700'>Bileşen 3 (K3) — Emsalli Meta-Hakem ({judge_prompt_ver} Protokolü)</span>
                <span style='font-size:0.78em; background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:6px; font-weight:600'>{judge_res['source']} &bull; {judge_res['latency']}s</span>
              </div>
              <div style='font-size:0.88em; color:#475569; margin-bottom:10px'>{routing_explanation}</div>
              <div style='background:#fffbeb; border-left:4px solid {jc}; padding:12px 16px; border-radius:6px'>
                <div style='font-size:1.05em; font-weight:800; color:{jc}'>Hakem Kararı: {LABEL_TR[judge_res['final_decision']]} &nbsp;({judge_res['favored_model']})</div>
                <div style='font-size:0.9em; margin-top:6px; color:#1e293b; line-height:1.5'><b>Gerekçe:</b> {html_lib.escape(judge_res['reasoning'])}</div>
              </div>
              <details style='margin-top:10px; font-size:0.82em; color:#475569'>
                <summary style='cursor:pointer; font-weight:600'>Hakeme Gönderilen İstemi (Prompt) Görüntüle</summary>
                <pre style='background:#0f172a; color:#f8fafc; padding:12px; border-radius:6px; overflow-x:auto; white-space:pre-wrap; margin-top:6px'>{html_lib.escape(judge_res['prompt'])}</pre>
              </details>
            </div>
            """
        else:
            fc = LABEL_COLOR[final_label]
            k3_html = f"""
            <div style='border:1px solid #cbd5e1; border-top:4px solid #15803d; background:#ffffff; border-radius:10px; padding:16px 18px; margin-top:12px'>
              <div style='display:flex; justify-content:space-between; align-items:center'>
                <span style='font-size:0.95em; color:#0f172a; font-weight:700'>Bileşen 3 (K3) — Konsensüs ve Yönlendirme Kapısı ({routing_policy})</span>
                <span style='font-size:0.78em; background:#dcfce7; color:#166534; padding:3px 10px; border-radius:6px; font-weight:600'>0 LLM Çağrısı &bull; $0.00</span>
              </div>
              <div style='font-size:1.05em; font-weight:700; margin:6px 0; color:{fc}'>{decision_mechanism}</div>
              <div style='font-size:0.88em; color:#475569'>{routing_explanation}</div>
            </div>
            """
    else:
        k3_html = ""

    # 4. NİHAİ KARAR BANNER
    f_lbl = final_label or "unverifiable"
    f_col = LABEL_COLOR.get(f_lbl, "#475569")
    f_bg = LABEL_BG.get(f_lbl, "#f8fafc")
    final_banner = f"""
    <div style='background:{f_bg}; border:1.5px solid {f_col}; border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px'>
      <div>
        <div style='font-size:0.76em; color:#475569; font-weight:700; text-transform:uppercase; letter-spacing:0.8px'>NİHAİ DOĞRULAMA KARARI ({exec_mode} &bull; {routing_policy})</div>
        <div style='font-size:1.65em; font-weight:800; color:{f_col}; margin-top:2px'>{LABEL_TR.get(f_lbl, f_lbl)}</div>
      </div>
      <div style='text-align:right; font-size:0.86em; color:#334155'>
        <div><b>Mekanizma:</b> {decision_mechanism}</div>
        <div style='margin-top:2px'><b>İkili Karşılık:</b> <code>{_to_binary(f_lbl).upper()}</code> &nbsp;&bull;&nbsp; <b>Süre:</b> {total_elapsed_s}s</div>
      </div>
    </div>
    """

    # 5. ALTIN REFERANS VE DONDURULMUŞ DENEY KIYASLAMA SATIRI
    if cached_rec:
        g_lbl = cached_rec["gold_label"]
        g_bin = cached_rec["gold_binary"]
        is_bin_only = cached_rec["label_scheme"] == "binary"

        def _cell(title: str, pred: str | None) -> str:
            if not pred:
                return f"<div style='padding:8px 10px;background:#f8fafc;border-radius:6px'><div style='font-size:0.75em;color:#64748b'>{title}</div><div style='color:#94a3b8;font-weight:600'>—</div></div>"
            ok = (_to_binary(pred) == g_bin) if is_bin_only else (pred == g_lbl)
            mark = "✓" if ok else "✗"
            col = "#15803d" if ok else "#b91c1c"
            return (
                f"<div style='padding:8px 10px;background:#f8fafc;border-radius:6px;border-left:3px solid {col}'>"
                f"<div style='font-size:0.75em;color:#64748b'>{title}</div>"
                f"<div style='font-weight:700;color:{col};font-size:0.9em'>{mark} {LABEL_SHORT_TR.get(pred, pred)}</div>"
                f"</div>"
            )

        paradox_note = ""
        if "1_atom_ps_paradox" in cached_rec.get("special_tags", []):
            paradox_note = (
                "<div style='background:#fffbeb;border-left:3px solid #d97706;padding:8px 12px;margin-top:8px;font-size:0.84em;color:#78350f'>"
                "<b>Akademik Not (1-Atomlu Kısmi Destek Paradoksu):</b> Bu örnekte yan cümlecik tek atom olarak korunduğu için K2 NLI matematiksel olarak "
                "kısmi destek üretemezken, K1 (ELECTRA-TR) cümle içi dikkat mekanizmasıyla kısmi desteği doğru yakalamıştır."
                "</div>"
            )

        gold_audit_html = f"""
        <div style='border:1px solid #cbd5e1; background:#ffffff; border-radius:10px; padding:14px 18px; margin-bottom:12px'>
          <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; font-size:0.86em'>
            <span style='font-weight:700; color:#0f172a'>Referans Karşılaştırma Tablosu — Vaka: <code>{cached_rec['example_id']}</code> ({DOMAIN_TR.get(cached_rec['domain'], '')})</span>
            <span style='color:#64748b'>{cached_rec.get('meta_note', '')}</span>
          </div>
          <div style='display:grid; grid-template-columns:repeat(6, 1fr); gap:8px'>
            <div style='padding:8px 10px;background:#eff6ff;border-radius:6px;border-left:3px solid #1d4ed8'>
              <div style='font-size:0.75em;color:#1e40af;font-weight:600'>Altın Etiket (Gold)</div>
              <div style='font-weight:800;color:#1e3a8a;font-size:0.92em'>{LABEL_SHORT_TR.get(g_lbl, g_lbl)}</div>
            </div>
            {_cell("K1 (Dondurulmuş)", cached_rec.get("k1_pred"))}
            {_cell("K2 (Soft-Prob)", cached_rec.get("k2_pred"))}
            {_cell("Hibrit P0 (V4)", cached_rec.get("hybrid_P0"))}
            {_cell("Hibrit PA", cached_rec.get("hybrid_PA"))}
            {_cell("Kör Gemma-26B", cached_rec.get("gemma26b_zero_shot"))}
          </div>
          {paradox_note}
        </div>
        """
    else:
        gold_audit_html = ""

    return final_banner, gold_audit_html, k1_html, k2_html, k3_html


# ── BAĞIMSIZ BİLEŞEN TEST RAPOR ÜRETİCİLERİ (SAYFA 3, 4 VE 5 İÇİN) ─────────

def filter_cases_json(
    dataset_key: str,
    filter_mode: str,
    domain_filter: str,
    search_query: str = "",
) -> dict[str, Any]:
    all_recs = DATASET_CATALOG.get(dataset_key, {})
    records = list(all_recs.values())
    n_total = len(records)
    n_dis = sum(1 for r in records if r.get("is_disagreement"))
    n_con = sum(1 for r in records if not r.get("is_disagreement") and r.get("k2_pred") is not None)

    q = search_query.strip().lower()
    cases_out = []

    for r in records:
        if domain_filter != "ALL" and r.get("domain") != domain_filter:
            continue

        k1_p = r.get("k1_pred")
        k2_p = r.get("k2_pred")
        gold_4 = r.get("gold_label")
        gold_bin = r.get("gold_binary")
        is_bin_ds = r.get("label_scheme") == "binary"

        def _is_ok(pred: str | None) -> bool:
            if not pred:
                return False
            if is_bin_ds:
                return _to_binary(pred) == gold_bin
            return pred == gold_4

        k1_ok = _is_ok(k1_p)
        k2_ok = _is_ok(k2_p)
        p0_ok = _is_ok(r.get("hybrid_P0"))
        is_dis = bool(r.get("is_disagreement"))

        if filter_mode == "DISAGREEMENT" and not is_dis:
            continue
        elif filter_mode == "CONSENSUS" and (is_dis or k2_p is None):
            continue
        elif filter_mode == "ONLY_K1_CORRECT" and not (k1_ok and not k2_ok and k2_p is not None):
            continue
        elif filter_mode == "ONLY_K2_CORRECT" and not (k2_ok and not k1_ok):
            continue
        elif filter_mode == "BOTH_WRONG" and not (not k1_ok and not k2_ok and k2_p is not None):
            continue
        elif filter_mode == "JUDGE_RESCUED" and not (is_dis and p0_ok and (not k1_ok or not k2_ok)):
            continue
        elif filter_mode == "PARADOX_1ATOM_PS" and "1_atom_ps_paradox" not in r.get("special_tags", []):
            continue
        elif filter_mode == "HUMAN_ADJUDICATED_48" and "human_adjudicated_48" not in r.get("special_tags", []):
            continue
        elif filter_mode == "K1_TRUNCATED" and "k1_truncated_512" not in r.get("special_tags", []):
            continue

        if q:
            haystack = f"{r['example_id']} {r['claim']} {r['context']} {r.get('question', '')}".lower()
            if q not in haystack:
                continue

        gold_disp = gold_bin if is_bin_ds else gold_4
        claim_snip = r["claim"]
        cases_out.append({
            "example_id": r["example_id"],
            "domain": r.get("domain", ""),
            "gold_display": gold_disp,
            "k1_pred": k1_p,
            "k2_pred": k2_p,
            "hybrid_P0": r.get("hybrid_P0"),
            "claim_snippet": claim_snip,
        })

    return {
        "total_in_dataset": n_total,
        "disagreements_in_dataset": n_dis,
        "consensus_in_dataset": n_con,
        "matching_count": len(cases_out),
        "cases": cases_out[:350],
    }


def build_k1_standalone_html(
    context: str,
    question: str,
    claim: str,
    dataset_key: str = "GOLD480",
    example_id: str | None = None,
) -> str:
    if not claim.strip():
        return "<div style='color:#b91c1c;padding:14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;font-weight:600'>Lütfen en azından İddia alanını doldurun.</div>"

    # 1. Tam Girdi (Bağlam + Soru + İddia) Çıkarımı
    res_full = predict_k1(context, question, claim)
    # 2. Sorusuz Girdi Ablasyonu (Soru=Boş, Yalnızca Bağlam + İddia)
    res_no_q = predict_k1(context, "", claim)
    # 3. Bağlam Bağımlılığı Ablasyonu (Bağlam=Boş, Yalnızca Soru + İddia)
    res_no_ctx = predict_k1("", question, claim)

    lbl_f = res_full["pred_label"]
    lbl_nq = res_no_q["pred_label"]
    lbl_n = res_no_ctx["pred_label"]
    col_f = LABEL_COLOR[lbl_f]
    col_nq = LABEL_COLOR[lbl_nq]
    col_n = LABEL_COLOR[lbl_n]

    def _prob_rows(probs: dict[str, float]) -> str:
        out = ""
        for k, v in probs.items():
            c = LABEL_COLOR[k]
            out += (
                f"<div style='margin:7px 0;font-size:0.84em'>"
                f"<div style='display:flex;justify-content:space-between;color:#1e293b'><span>{LABEL_TR[k]}</span><b>%{v*100:.2f}</b></div>"
                f"<div style='background:#e2e8f0;border-radius:4px;height:7px;overflow:hidden;margin-top:3px'>"
                f"<div style='background:{c};width:{v*100:.1f}%;height:100%'></div></div></div>"
            )
        return out

    same_label_ctx = (lbl_f == lbl_n)
    conf_diff_ctx = (res_full["confidence"] - res_no_ctx["confidence"]) * 100.0
    same_label_q = (lbl_f == lbl_nq)
    conf_diff_q = (res_full["confidence"] - res_no_q["confidence"]) * 100.0

    q_ablation_note = (
        f"Soru çıkarıldığında K1'in kararı <b>{LABEL_SHORT_TR[lbl_f]}</b> &rarr; <b>{LABEL_SHORT_TR[lbl_nq]}</b> olarak değişti "
        f"(güven farkı: {conf_diff_q:+.1f} puan). Bu bulgu, K1'in karar verirken <code>Soru</code> bileşenine doğrudan bağımlı olduğunu gösterir."
        if not same_label_q
        else f"Soru çıkarıldığında sınıf değişmedi (<b>{LABEL_SHORT_TR[lbl_nq]}</b>), güven değişimi: <b>{conf_diff_q:+.1f} puan</b>."
    )

    ablation_alert = (
        f"<div style='background:#f0fdf4;border-left:4px solid #15803d;padding:12px 16px;border-radius:6px;margin-top:14px;font-size:0.88em;color:#14532d;line-height:1.55'>"
        f"<div><b>1. Bağlam Duyarlılığı (Context-Sensitivity):</b> Bağlam çıkarıldığında K1'in kararı "
        f"<b>{LABEL_SHORT_TR[lbl_f]}</b> &rarr; <b>{LABEL_SHORT_TR[lbl_n]}</b> olarak değişti! "
        f"Model bu vakada doğrudan bağlamdaki kanıta dayanmaktadır.</div>"
        f"<div style='margin-top:4px'><b>2. Soru Bileşeni Etkisi (Question-Sensitivity):</b> {q_ablation_note}</div>"
        f"</div>"
        if not same_label_ctx
        else f"<div style='background:#fffbeb;border-left:4px solid #d97706;padding:12px 16px;border-radius:6px;margin-top:14px;font-size:0.88em;color:#78350f;line-height:1.55'>"
        f"<div><b>1. Yüzeysel İpucu / Bağlamsız Tahmin Analizi:</b> Bağlam tamamen silindiğinde dahi K1 aynı sınıfı "
        f"(<b>{LABEL_SHORT_TR[lbl_f]}</b>, bağlamsız güven: <b>%{res_no_ctx['confidence']*100:.1f}</b>, güven farkı: {conf_diff_ctx:+.1f} puan) tahmin etti.</div>"
        f"<div style='margin-top:4px'><b>2. Soru Bileşeni Etkisi (Question-Sensitivity):</b> {q_ablation_note}</div>"
        f"</div>"
    )

    trunc_badge = (
        f"<span style='background:#fef2f2;color:#b91c1c;padding:3px 9px;border-radius:6px;font-weight:700;font-size:0.8em'>⚠️ 512 Token Sınırında Kesildi ({res_full['n_tokens']} token)</span>"
        if res_full["was_truncated"]
        else f"<span style='background:#f0fdf4;color:#15803d;padding:3px 9px;border-radius:6px;font-weight:700;font-size:0.8em'>✓ Kesilme Yok ({res_full['n_tokens']} / 512 token)</span>"
    )

    gold_box = ""
    if example_id and example_id in DATASET_CATALOG.get(dataset_key, {}):
        rec = DATASET_CATALOG[dataset_key][example_id]
        if rec["claim"].strip() == claim.strip():
            g_lbl = rec["gold_label"]
            ok = (_to_binary(lbl_f) == rec["gold_binary"]) if rec["label_scheme"] == "binary" else (lbl_f == g_lbl)
            g_col = "#15803d" if ok else "#b91c1c"
            gold_box = (
                f"<div style='background:#f8fafc;border:1px solid #cbd5e1;border-left:4px solid {g_col};padding:10px 14px;border-radius:8px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;font-size:0.88em'>"
                f"<div><b>Seçili Vaka:</b> <code>{example_id}</code> &nbsp;|&nbsp; <b>Altın Etiket:</b> <b style='color:#1e3a8a'>{LABEL_TR.get(g_lbl, g_lbl)}</b></div>"
                f"<div style='color:{g_col};font-weight:800'>{'✓ K1 Tahmini Altın Etiket ile Uyumlu' if ok else '✗ K1 Tahmini Altın Etiketten Farklı'}</div>"
                f"</div>"
            )

    return f"""
    <div style='background:#ffffff;border:1px solid #cbd5e1;border-radius:10px;padding:20px'>
      <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid #e2e8f0;padding-bottom:10px'>
        <div>
          <span style='font-size:1.05em;font-weight:800;color:#0f172a'>Bileşen 1 (K1: ELECTRA-TR LoRA <code>H1_DROP10_S45</code>) — Tanısal Çıkarım ve 3'lü Girdi Ablasyonu</span>
        </div>
        <div style='display:flex;gap:8px;align-items:center'>
          {trunc_badge}
          <span style='background:#f1f5f9;color:#334155;padding:3px 9px;border-radius:6px;font-size:0.8em;font-weight:600'>{res_full['latency_ms']} ms</span>
        </div>
      </div>
      {gold_box}
      <div style='display:grid;grid-template-columns:repeat(3, 1fr);gap:14px'>
        <div style='border:1px solid #cbd5e1;border-top:4px solid {col_f};border-radius:8px;padding:14px'>
          <div style='font-size:0.8em;font-weight:800;color:#1e3a8a;text-transform:uppercase;margin-bottom:6px'>1. Tam Girdi (Bağlam + Soru + İddia)</div>
          <div style='font-size:1.2em;font-weight:800;color:{col_f};margin-bottom:4px'>{LABEL_TR[lbl_f]}</div>
          <div style='font-size:0.8em;color:#475569;margin-bottom:12px'>
            Güven: <b>%{res_full['confidence']*100:.2f}</b> &bull;
            Entropi: <b>{res_full['entropy_bits']} bit</b> &bull;
            Marj: <b>{res_full['top2_margin']:.3f}</b>
          </div>
          {_prob_rows(res_full['probs'])}
        </div>
        <div style='border:1px solid #cbd5e1;border-top:4px solid {col_nq};border-radius:8px;padding:14px;background:#fcfcfd'>
          <div style='font-size:0.8em;font-weight:800;color:#475569;text-transform:uppercase;margin-bottom:6px'>2. Sorusuz Ablasyon (Soru = Boş)</div>
          <div style='font-size:1.2em;font-weight:800;color:{col_nq};margin-bottom:4px'>{LABEL_TR[lbl_nq]}</div>
          <div style='font-size:0.8em;color:#475569;margin-bottom:12px'>
            Güven: <b>%{res_no_q['confidence']*100:.2f}</b> &bull;
            Entropi: <b>{res_no_q['entropy_bits']} bit</b> &bull;
            Marj: <b>{res_no_q['top2_margin']:.3f}</b>
          </div>
          {_prob_rows(res_no_q['probs'])}
        </div>
        <div style='border:1px solid #cbd5e1;border-top:4px solid {col_n};border-radius:8px;padding:14px;background:#fcfcfd'>
          <div style='font-size:0.8em;font-weight:800;color:#475569;text-transform:uppercase;margin-bottom:6px'>3. Bağlamsız Ablasyon (Bağlam = Boş)</div>
          <div style='font-size:1.2em;font-weight:800;color:{col_n};margin-bottom:4px'>{LABEL_TR[lbl_n]}</div>
          <div style='font-size:0.8em;color:#475569;margin-bottom:12px'>
            Güven: <b>%{res_no_ctx['confidence']*100:.2f}</b> &bull;
            Entropi: <b>{res_no_ctx['entropy_bits']} bit</b> &bull;
            Marj: <b>{res_no_ctx['top2_margin']:.3f}</b>
          </div>
          {_prob_rows(res_no_ctx['probs'])}
        </div>
      </div>
      {ablation_alert}
    </div>
    """


def build_k2_standalone_html(
    context: str,
    atoms: list[str],
    dataset_key: str = "GOLD480",
    example_id: str | None = None,
) -> str:
    if not context.strip() or not atoms:
        return "<div style='color:#b91c1c;padding:14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;font-weight:600'>Lütfen Bağlam ve en az bir Atomik Önerme girin.</div>"

    explicit_windows = []
    cached_rec = None
    if example_id and example_id in DATASET_CATALOG.get(dataset_key, {}):
        cached_rec = DATASET_CATALOG[dataset_key][example_id]
        explicit_windows = cached_rec.get("context_windows", [])

    res_full = predict_k2_nli(context, atoms, agg_rule="soft_prob_avg", windowing_mode="full")
    res_win = predict_k2_nli(
        context, atoms, agg_rule="soft_prob_avg", windowing_mode="windowed", explicit_windows=explicit_windows
    )

    rows_html = ""
    for i, a in enumerate(res_full["atoms"]):
        aw = res_win["atoms"][i]
        rows_html += (
            f"<tr style='border-bottom:1px solid #e2e8f0'>"
            f"<td style='padding:10px;font-weight:700;color:#334155'>#{i+1}</td>"
            f"<td style='padding:10px;color:#0f172a;font-weight:500'>{html_lib.escape(a['atom'])}</td>"
            f"<td style='padding:10px;color:{ATOM_NLI_COLOR[a['label']]};font-weight:700'>{ATOM_NLI_TR[a['label']]}</td>"
            f"<td style='padding:10px;font-family:monospace;font-size:0.85em'>"
            f"E:%{a['probs']['entailment']*100:.1f} | N:%{a['probs']['neutral']*100:.1f} | C:%{a['probs']['contradiction']*100:.1f}</td>"
            f"<td style='padding:10px;color:{ATOM_NLI_COLOR[aw['label']]};font-weight:700'>"
            f"{ATOM_NLI_TR[aw['label']]} <span style='color:#64748b;font-weight:400;font-size:0.85em'>(Pencere #{aw['best_window']+1}/{aw['n_windows_tested']})</span></td>"
            f"<td style='padding:10px;font-family:monospace;font-size:0.85em'>"
            f"E:%{aw['probs']['entailment']*100:.1f} | N:%{aw['probs']['neutral']*100:.1f} | C:%{aw['probs']['contradiction']*100:.1f}</td>"
            f"</tr>"
        )

    rf = res_full["all_rule_preds"]
    rw = res_win["all_rule_preds"]

    return f"""
    <div style='background:#ffffff;border:1px solid #cbd5e1;border-radius:10px;padding:20px'>
      <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid #e2e8f0;padding-bottom:10px'>
        <span style='font-size:1.05em;font-weight:800;color:#0f172a'>Bileşen 2 (K2: mDeBERTa-v3 Zero-Shot NLI) — Atom Bazlı Olasılık ve 3 Kural Kıyaslaması</span>
        <span style='background:#f1f5f9;color:#334155;padding:3px 10px;border-radius:6px;font-size:0.82em;font-weight:600'>
          Tam Bağlam: {res_full['latency_ms']} ms &bull; Pencereli ({res_win['n_windows']} Pencere): {res_win['latency_ms']} ms
        </span>
      </div>

      <div style='overflow-x:auto'>
        <table style='width:100%;border-collapse:collapse;font-size:0.88em'>
          <thead>
            <tr style='background:#f8fafc;border-bottom:2px solid #cbd5e1;text-align:left;color:#334155'>
              <th style='padding:10px'>#</th>
              <th style='padding:10px'>Atomik Önerme</th>
              <th style='padding:10px'>Tam Bağlam NLI</th>
              <th style='padding:10px'>Tam Bağlam Olasılıkları</th>
              <th style='padding:10px'>Pencereli NLI (K-017)</th>
              <th style='padding:10px'>Pencereli Olasılıklar</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>

      <div style='display:grid;grid-template-columns:repeat(3, 1fr);gap:14px;margin-top:16px'>
        <div style='background:#f0fdf4;border:1px solid #bbf7d0;border-top:4px solid #15803d;padding:14px;border-radius:8px'>
          <div style='font-size:0.82em;font-weight:800;color:#14532d;text-transform:uppercase;margin-bottom:6px'>1. Soft-Probability Average (Tez Seçimi — 0.8065 F1)</div>
          <div style='font-size:0.9em;margin:4px 0'>Tam Bağlam: <b style='color:{LABEL_COLOR[rf['soft_prob_avg']]}'>{LABEL_TR[rf['soft_prob_avg']]}</b></div>
          <div style='font-size:0.9em;margin:4px 0'>Belge Pencereli: <b style='color:{LABEL_COLOR[rw['soft_prob_avg']]}'>{LABEL_TR[rw['soft_prob_avg']]}</b></div>
        </div>
        <div style='background:#f8fafc;border:1px solid #cbd5e1;border-top:4px solid #334155;padding:14px;border-radius:8px'>
          <div style='font-size:0.82em;font-weight:800;color:#1e293b;text-transform:uppercase;margin-bottom:6px'>2. Flat (Deterministik Düz Kural — 0.7838 F1)</div>
          <div style='font-size:0.9em;margin:4px 0'>Tam Bağlam: <b style='color:{LABEL_COLOR[rf['flat']]}'>{LABEL_TR[rf['flat']]}</b></div>
          <div style='font-size:0.9em;margin:4px 0'>Belge Pencereli: <b style='color:{LABEL_COLOR[rw['flat']]}'>{LABEL_TR[rw['flat']]}</b></div>
        </div>
        <div style='background:#fff1f2;border:1px solid #fecdd3;border-top:4px solid #be123c;padding:14px;border-radius:8px'>
          <div style='font-size:0.82em;font-weight:800;color:#881337;text-transform:uppercase;margin-bottom:6px'>3. Contradiction-Priority (0.6237 F1)</div>
          <div style='font-size:0.9em;margin:4px 0'>Tam Bağlam: <b style='color:{LABEL_COLOR[rf['contradiction_priority']]}'>{LABEL_TR[rf['contradiction_priority']]}</b></div>
          <div style='font-size:0.9em;margin:4px 0'>Belge Pencereli: <b style='color:{LABEL_COLOR[rw['contradiction_priority']]}'>{LABEL_TR[rw['contradiction_priority']]}</b></div>
        </div>
      </div>
    </div>
    """


def build_k3_standalone_html(
    context: str,
    claim: str,
    k1_pred: str,
    k2_pred: str,
    atoms: list[str],
    judge_model: str,
    prompt_version: str,
    use_cached_judge: bool,
    dataset_key: str = "GOLD480",
    example_id: str | None = None,
) -> str:
    if not context.strip() or not claim.strip():
        return "<div style='color:#b91c1c;padding:14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;font-weight:600'>Lütfen Bağlam ve İddia alanlarını doldurun.</div>"

    cached_rec = None
    if example_id and example_id in DATASET_CATALOG.get(dataset_key, {}):
        cand = DATASET_CATALOG[dataset_key][example_id]
        if cand["claim"].strip() == claim.strip():
            cached_rec = cand

    if not atoms:
        cached_atom_texts = [a["atom"] for a in cached_rec.get("atoms", [])] if cached_rec else None
        atoms, _, _ = extract_claim_atoms(claim, cached_atoms=cached_atom_texts, use_cache=bool(cached_atom_texts))

    j_res = call_live_meta_judge(
        context=context,
        claim=claim,
        k1_pred=k1_pred,
        k2_pred=k2_pred,
        atoms=atoms,
        judge_model=judge_model,
        prompt_version=prompt_version,
        cached_record=cached_rec,
        use_cached_judge=use_cached_judge,
    )

    dec = j_res["final_decision"]
    jc = LABEL_COLOR.get(dec, "#334155")
    jbg = LABEL_BG.get(dec, "#f8fafc")

    gold_cmp = ""
    if cached_rec:
        g_lbl = cached_rec["gold_label"]
        ok = (_to_binary(dec) == cached_rec["gold_binary"]) if cached_rec["label_scheme"] == "binary" else (dec == g_lbl)
        col = "#15803d" if ok else "#b91c1c"
        gold_cmp = (
            f"<div style='margin-top:12px;padding:10px 14px;background:#f8fafc;border-left:4px solid {col};border-radius:6px;font-size:0.88em;display:flex;justify-content:space-between'>"
            f"<span><b>Altın Etiket (Gold):</b> {LABEL_TR.get(g_lbl, g_lbl)}</span>"
            f"<b style='color:{col}'>{'✓ Hakem Kararı Altın Etiket ile Tam Uyumlu' if ok else '✗ Hakem Kararı Altın Etiketten Farklı'}</b>"
            f"</div>"
        )

    return f"""
    <div style='background:#ffffff;border:1px solid #cbd5e1;border-top:4px solid {jc};border-radius:10px;padding:20px'>
      <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px'>
        <span style='font-size:1.05em;font-weight:800;color:#0f172a'>Bileşen 3 (K3) — Meta-Hakem Arbitrasyon Sonucu ({prompt_version} Protokolü)</span>
        <span style='background:#fef3c7;color:#92400e;padding:4px 10px;border-radius:6px;font-size:0.82em;font-weight:700'>{j_res['source']} &bull; {j_res['latency']}s</span>
      </div>

      <div style='display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-bottom:14px;font-size:0.88em'>
        <div style='background:#f8fafc;padding:10px 12px;border-radius:6px;border:1px solid #e2e8f0'>
          <div style='color:#64748b;font-size:0.8em'>Model A (K1 — Bütüncül) Kararı</div>
          <div style='font-weight:800;color:{LABEL_COLOR.get(k1_pred, "#334155")};margin-top:2px'>{LABEL_TR.get(k1_pred, k1_pred)}</div>
        </div>
        <div style='background:#f8fafc;padding:10px 12px;border-radius:6px;border:1px solid #e2e8f0'>
          <div style='color:#64748b;font-size:0.8em'>Model B (K2 — Atomik NLI) Kararı</div>
          <div style='font-weight:800;color:{LABEL_COLOR.get(k2_pred, "#334155")};margin-top:2px'>{LABEL_TR.get(k2_pred, k2_pred)}</div>
        </div>
        <div style='background:#eff6ff;padding:10px 12px;border-radius:6px;border:1px solid #bfdbfe'>
          <div style='color:#1e40af;font-size:0.8em'>Hakemin Haklı Bulduğu Model</div>
          <div style='font-weight:800;color:#1e3a8a;margin-top:2px'>{html_lib.escape(str(j_res['favored_model']))}</div>
        </div>
      </div>

      <div style='background:{jbg};border-left:4px solid {jc};padding:14px 18px;border-radius:8px'>
        <div style='font-size:1.25em;font-weight:800;color:{jc}'>Nihai Hakem Kararı: {LABEL_TR.get(dec, dec)}</div>
        <div style='font-size:0.94em;color:#1e293b;margin-top:8px;line-height:1.55'>
          <b>Hakem Gerekçesi:</b> {html_lib.escape(str(j_res['reasoning']))}
        </div>
      </div>

      {gold_cmp}

      <details style='margin-top:14px;font-size:0.84em;color:#475569'>
        <summary style='cursor:pointer;font-weight:700;color:#1e3a8a'>Hakeme Gönderilen Tam İstemi (Few-Shot Emsaller + {prompt_version} Kuralları) Görüntüle</summary>
        <pre style='background:#0f172a;color:#f8fafc;padding:14px;border-radius:8px;overflow-x:auto;white-space:pre-wrap;margin-top:8px;line-height:1.45'>{html_lib.escape(j_res['prompt'])}</pre>
      </details>
    </div>
    """


# ── ÇOK SAYFALI AKADEMİK WEB SUNUCUSU (HTTP REST API + HTML ARAYÜZ) ──────────

UI_HTML_FILE = HERE / "ui_hybrid_workbench.html"
if not UI_HTML_FILE.exists() and (ROOT / "ui_hybrid_workbench.html").exists():
    UI_HTML_FILE = ROOT / "ui_hybrid_workbench.html"


class WorkbenchHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            if UI_HTML_FILE.exists():
                html_bytes = UI_HTML_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(html_bytes)
            else:
                self._send_json({"error": "ui_hybrid_workbench.html bulunamadı"}, 404)
            return

        if path == "/api/cases":
            ds = qs.get("dataset", ["GOLD480"])[0]
            flt = qs.get("filter", ["DISAGREEMENT"])[0]
            dom = qs.get("domain", ["ALL"])[0]
            q = qs.get("q", [""])[0]
            self._send_json(filter_cases_json(ds, flt, dom, q))
            return

        if path == "/api/case_detail":
            ds = qs.get("dataset", ["GOLD480"])[0]
            ex_id = qs.get("id", [""])[0]
            rec = DATASET_CATALOG.get(ds, {}).get(ex_id)
            if not rec:
                self._send_json({"error": "Vaka bulunamadı"}, 404)
            else:
                self._send_json(rec)
            return

        self._send_json({"error": f"Bilinmeyen uç nokta: {path}"}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        data = self._read_json_body()

        if path == "/api/run_hybrid":
            final_banner, gold_audit_html, k1_html, k2_html, k3_html = execute_workbench(
                context=data.get("context", ""),
                question=data.get("question", ""),
                claim=data.get("claim", ""),
                exec_mode="HYBRID_FULL",
                routing_policy=data.get("routing_policy", "P0"),
                agg_rule=data.get("agg_rule", "soft_prob_avg"),
                windowing_mode=data.get("windowing_mode", "auto"),
                judge_model=data.get("judge_model", "meta-llama/llama-3.3-70b-instruct"),
                judge_prompt_ver=data.get("judge_prompt_ver", "V4"),
                use_cached_judge=bool(data.get("use_cached_judge", True)),
                dataset_key=data.get("dataset", "GOLD480"),
                selected_example_id=data.get("id"),
            )
            combined_html = f"""
            {final_banner}
            {gold_audit_html}
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px'>
              <div>{k1_html}</div>
              <div>{k2_html}</div>
            </div>
            {k3_html}
            """
            self._send_json({"html": combined_html})
            return

        if path == "/api/run_k1":
            html_out = build_k1_standalone_html(
                context=data.get("context", ""),
                question=data.get("question", ""),
                claim=data.get("claim", ""),
                dataset_key=data.get("dataset", "GOLD480"),
                example_id=data.get("id"),
            )
            self._send_json({"html": html_out})
            return

        if path == "/api/run_atomizer":
            claim_txt = data.get("claim", "")
            atoms, src, lat_ms = extract_claim_atoms(claim_txt, use_cache=False)
            self._send_json({"atoms": atoms, "source": src, "latency_ms": lat_ms})
            return

        if path == "/api/run_k2":
            html_out = build_k2_standalone_html(
                context=data.get("context", ""),
                atoms=data.get("atoms", []),
                dataset_key=data.get("dataset", "GOLD480"),
                example_id=data.get("id"),
            )
            self._send_json({"html": html_out})
            return

        if path == "/api/run_k3":
            html_out = build_k3_standalone_html(
                context=data.get("context", ""),
                claim=data.get("claim", ""),
                k1_pred=data.get("k1_pred", "partially_supported"),
                k2_pred=data.get("k2_pred", "supported"),
                atoms=data.get("atoms", []),
                judge_model=data.get("judge_model", "meta-llama/llama-3.3-70b-instruct"),
                prompt_version=data.get("prompt_version", "V4"),
                use_cached_judge=bool(data.get("use_cached_judge", True)),
                dataset_key=data.get("dataset", "GOLD480"),
                example_id=data.get("id"),
            )
            self._send_json({"html": html_out})
            return

        self._send_json({"error": f"Bilinmeyen POST uç noktası: {path}"}, 404)


def run_server(port: int = 7865) -> None:
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer(("127.0.0.1", port), WorkbenchHTTPHandler)
    print("\n" + "=" * 76)
    print("  TR-FactBench Çok Sayfalı Akademik Doğrulama Laboratuvarı Hazır!")
    print(f"  Tarayıcı Adresi: http://127.0.0.1:{port}")
    print("=" * 76 + "\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
        server.server_close()


if __name__ == "__main__":
    run_server(port=7865)

