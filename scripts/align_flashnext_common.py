"""No MLX imports here. Approval and identity gates for later desk execution."""
from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import sys


REVIEWED_PR_FILES = {
    "models/qwen4_exp.py": "d6470a2131a64ff37024dfffd2b5bc8c3f4db625f0f3b1ceec7fe346852c1a87",
    "models/cache.py": "c64e81d97bc6425afa155b65625ddb4a9bb8fac17b164ab519559abe4c5e9323",
    "utils.py": "a653ed112e3b59df1a7dfc227dcb2c944b6e6846aaadba8b7e208c6aa3b7a78a",
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root):
    root = Path(root)
    if root.is_symlink() or "restricted" in root.parts:
        raise ValueError("symlink/restricted artifact root refused")
    result = {}
    for parent, dirs, files in os.walk(root, followlinks=False):
        if "restricted" in dirs:
            raise ValueError("restricted artifact directory refused")
        for name in dirs + files:
            if (Path(parent) / name).is_symlink():
                raise ValueError("artifact symlinks refused; materialize an approved snapshot first")
        for name in files:
            path = Path(parent) / name
            result[path.relative_to(root).as_posix()] = sha256(path)
    if not result:
        raise ValueError("empty artifact inventory")
    return dict(sorted(result.items()))


def verify_inventory(root, expected):
    if not expected or inventory(root) != expected:
        raise ValueError("artifact inventory/sha256 mismatch")


def approved_runtime(approved, pins_path):
    # Evaluate this before locating or importing any installed third-party package.
    if not approved:
        raise ValueError("requires --approved-desk at a later, approved Mac desk session")
    if sys.prefix == sys.base_prefix or platform.system() != "Darwin" or platform.machine() != "arm64":
        raise ValueError("requires isolated Apple Silicon Mac venv")
    pins = json.loads(Path(pins_path).read_text())
    commit = pins["mlx_lm_commit"]
    if not re.fullmatch(r"2097324[0-9a-f]{33}", commit):
        raise ValueError("pin full 40-hex PR commit beginning 2097324; no floating ref")
    versions = pins["package_versions"]
    if not {"mlx", "mlx-metal", "mlx-lm", "numpy", "transformers", "tokenizers", "jinja2", "safetensors"} <= versions.keys():
        raise ValueError("incomplete runtime package pins")
    for package, version in versions.items():
        if importlib.metadata.version(package) != version:
            raise ValueError("package version mismatch: " + package)
    spec = importlib.util.find_spec("mlx_lm")
    if spec is None or not spec.origin:
        raise ValueError("mlx_lm is not installed")
    root = Path(spec.origin).parent.resolve()
    if ".engine" in root.parts or not root.is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError("engine must be installed in the isolated venv, not loaded from staged sources")
    expected = pins["mlx_lm_python_sha256"]
    actual = {p.relative_to(root).as_posix(): sha256(p) for p in root.rglob("*.py")}
    if actual != expected or "models/qwen4_exp.py" not in expected:
        raise ValueError("installed engine source inventory mismatch")
    if any(actual.get(name) != digest for name, digest in REVIEWED_PR_FILES.items()):
        raise ValueError("installed port/cache/loader differs from the statically reviewed snapshot")
    if pins.get("python_version") != platform.python_version():
        raise ValueError("Python version mismatch")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    return pins
