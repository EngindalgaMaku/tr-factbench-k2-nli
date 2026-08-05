from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .io import sha256_file


def create_run_directory(base: str | Path, run_id: str) -> Path:
    path = Path(base) / run_id
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Run directory already exists and is not empty: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def git_commit(root: str | Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def base_manifest(dataset_path: str | Path, arguments: dict) -> dict:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(Path(dataset_path).resolve()),
        "dataset_sha256": sha256_file(dataset_path),
        "arguments": arguments,
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": git_commit(Path(__file__).resolve().parents[2]),
    }


def write_json(path: str | Path, value: dict) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
