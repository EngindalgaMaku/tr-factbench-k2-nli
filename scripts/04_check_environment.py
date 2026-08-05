#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import platform
import sys


def version_of(package: str) -> str | None:
    try:
        module = importlib.import_module(package)
    except Exception:
        return None
    return str(getattr(module, "__version__", "unknown"))


def main() -> None:
    try:
        import torch
    except Exception as exc:
        raise SystemExit(f"PyTorch import edilemedi: {exc}") from exc

    cuda_available = bool(torch.cuda.is_available())
    payload = {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "cuda_available": cuda_available,
        "gpu_name": torch.cuda.get_device_name(0) if cuda_available else None,
        "gpu_count": torch.cuda.device_count() if cuda_available else 0,
        "transformers_version": version_of("transformers"),
        "numpy_version": version_of("numpy"),
        "pandas_version": version_of("pandas"),
        "sklearn_version": version_of("sklearn"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if "+cpu" in str(torch.__version__) or torch.version.cuda is None:
        raise SystemExit(
            "HATA: CPU-only PyTorch kurulu. K2 model deneylerini bu interpreter ile çalıştırmayın."
        )
    if not cuda_available:
        raise SystemExit(
            "HATA: CUDA build kurulu görünse de GPU erişilemiyor. NVIDIA sürücüsünü ve seçili interpreter'ı kontrol edin."
        )

    print("ORTAM UYGUN: CUDA-enabled PyTorch ve NVIDIA GPU erişilebilir.")


if __name__ == "__main__":
    main()
