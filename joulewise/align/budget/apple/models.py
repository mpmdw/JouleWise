"""Resolve repository IDs to pinned, offline Hugging Face snapshots."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


MODEL_SIZES = {
    "mlx-community/Qwen3-4B-4bit": 4.0,
    "mlx-community/Qwen3-8B-4bit": 8.0,
    "mlx-community/Qwen3-14B-4bit": 14.0,
}


@dataclass(frozen=True)
class CachedModel:
    repo_id: str
    revision: str
    snapshot: str
    size_b: float
    quantization_bits: int = 4


def resolve_model(repo_id: str, cache: Path, revision: str | None = None) -> CachedModel:
    """Never download or choose between ambiguous revisions implicitly.

    A missing main ref is acceptable only with one complete local snapshot.
    Inspect index names and existence, without loading tensor bytes.
    """
    if repo_id not in MODEL_SIZES:
        raise ValueError(f"unsupported D3 repository: {repo_id}")
    root = Path(cache) / ("models--" + repo_id.replace("/", "--"))
    if revision is None:
        ref = root / "refs" / "main"
        if ref.is_file():
            revision = ref.read_text(encoding="utf-8").strip()
        else:
            snapshots = sorted(p.name for p in (root / "snapshots").glob("*") if p.is_dir())
            if len(snapshots) != 1:
                raise ValueError(f"pin a cached revision for {repo_id}: {snapshots}")
            revision = snapshots[0]
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise ValueError("revision must be a full Hugging Face commit SHA")
    snapshot = root / "snapshots" / revision
    for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
        if not (snapshot / name).is_file():
            raise ValueError(f"incomplete cached snapshot: {snapshot / name}")
    config = json.loads((snapshot / "config.json").read_text(encoding="utf-8"))
    bits = (config.get("quantization") or config.get("quantization_config") or {}).get("bits")
    if bits != 4 or config.get("model_type") != "qwen3":
        raise ValueError("D3 requires dense Qwen3 with recorded 4-bit quantization")
    index = snapshot / "model.safetensors.index.json"
    weights = (set(json.loads(index.read_text())["weight_map"].values()) if index.is_file()
               else {p.name for p in snapshot.glob("*.safetensors")})
    if not weights or any(Path(w).name != w or not (snapshot / w).is_file() for w in weights):
        raise ValueError(f"missing cached weights: {repo_id}@{revision}")
    return CachedModel(repo_id, revision, str(snapshot.absolute()), MODEL_SIZES[repo_id])
