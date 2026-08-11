"""Provenance helpers for realized workload identity."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any

PROMPT_TOKEN_IDS_HASH_DOMAIN = "joulewise.prompt_token_ids.v1"
SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN = "joulewise.suite_prompt_token_ids.v1"
MODEL_ARTIFACT_HASH_DOMAIN = "joulewise.model_artifact_identity.v1"
MODEL_WEIGHT_SUFFIXES = (
    ".safetensors",
    ".bin",
    ".pt",
    ".pth",
    ".npz",
    ".gguf",
)
FIXED_BUDGET_EXACT = "fixed_budget_exact"
FIXED_BUDGET_INCOMPLETE = "fixed_budget_incomplete"


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_hex_shape(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


def normalized_sha256_hex(value: Any) -> str | None:
    return value.lower() if sha256_hex_shape(value) else None


def suite_prompt_plan_class(
    suite_id: str,
    suite_profile: str,
    source_id: str,
) -> str:
    identity = " ".join((suite_id, suite_profile, source_id)).lower()
    if "jw_mixed_v1" in identity:
        return "budgeted"
    if "affine" in identity:
        return "affine"
    return "other"


def prompt_token_ids_sha256(token_ids: list[int]) -> str:
    canonical = json.dumps(token_ids, separators=(",", ":"), sort_keys=True)
    return sha256_hex(PROMPT_TOKEN_IDS_HASH_DOMAIN + "\0" + canonical)


def folded_model_artifact_sha256(file_hashes: dict[str, str]) -> str:
    canonical = json.dumps(file_hashes, separators=(",", ":"), sort_keys=True)
    return sha256_hex(MODEL_ARTIFACT_HASH_DOMAIN + "\0" + canonical)


def _unavailable_model_artifact(reason: str, **details: Any) -> dict[str, Any]:
    return {"status": "unavailable", "reason": reason, **details}


def _stable_file_sha256(path: Path) -> tuple[str, int] | dict[str, Any]:
    """Hash one file while refusing an in-flight replacement or mutation."""

    try:
        before_link = path.lstat()
        if not stat.S_ISREG(before_link.st_mode) and not stat.S_ISLNK(before_link.st_mode):
            return _unavailable_model_artifact(
                "model inventory entry is not a regular file", path=str(path)
            )
        if stat.S_ISLNK(before_link.st_mode):
            path.resolve(strict=True)
        target_before = path.stat()
        if target_before.st_mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH) == 0:
            return _unavailable_model_artifact(
                "model weight file is unreadable", path=str(path)
            )
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            opened_before = os.fstat(handle.fileno())
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            opened_after = os.fstat(handle.fileno())
        after_link = path.lstat()
        target_after = path.stat()
    except (OSError, RuntimeError) as exc:
        return _unavailable_model_artifact(
            f"cannot read model weight file: {exc}", path=str(path)
        )

    stable_open = (
        opened_before.st_dev,
        opened_before.st_ino,
        opened_before.st_size,
        opened_before.st_mtime_ns,
    ) == (
        opened_after.st_dev,
        opened_after.st_ino,
        opened_after.st_size,
        opened_after.st_mtime_ns,
    )
    stable_target = (
        target_before.st_dev,
        target_before.st_ino,
        target_before.st_size,
        target_before.st_mtime_ns,
    ) == (
        target_after.st_dev,
        target_after.st_ino,
        target_after.st_size,
        target_after.st_mtime_ns,
    )
    stable_link = (
        before_link.st_dev,
        before_link.st_ino,
        before_link.st_size,
        before_link.st_mtime_ns,
        stat.S_IFMT(before_link.st_mode),
    ) == (
        after_link.st_dev,
        after_link.st_ino,
        after_link.st_size,
        after_link.st_mtime_ns,
        stat.S_IFMT(after_link.st_mode),
    )
    if not (stable_open and stable_target and stable_link):
        return _unavailable_model_artifact(
            "model inventory changed during read", path=str(path)
        )
    return digest.hexdigest(), opened_after.st_size


def _directory_inventory(root: Path) -> tuple[list[Path], list[str]]:
    paths: list[Path] = []
    errors: list[str] = []

    def onerror(exc: OSError) -> None:
        errors.append(str(exc))

    try:
        for current, directory_names, file_names in os.walk(
            root, topdown=True, followlinks=False, onerror=onerror
        ):
            current_path = Path(current)
            retained_directories: list[str] = []
            for name in sorted(directory_names):
                candidate = current_path / name
                try:
                    if not candidate.is_symlink():
                        retained_directories.append(name)
                except OSError as exc:
                    errors.append(str(exc))
            directory_names[:] = retained_directories
            for name in sorted(file_names):
                candidate = current_path / name
                if candidate.name.endswith(MODEL_WEIGHT_SUFFIXES):
                    paths.append(candidate)
    except OSError as exc:
        errors.append(str(exc))
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix()), errors


def model_artifact_identity(source: str | None) -> dict[str, Any]:
    """Derive the governed identity of a local model file or model tree.

    Directory identities use lexical model-root-relative POSIX paths and do
    not traverse directory symlinks. File symlinks retain their lexical path
    while recording the resolved target and hashing the followed bytes.
    """

    if not source:
        return _unavailable_model_artifact("model source is not configured")
    path = Path(source).expanduser()
    if path.is_file():
        hashed = _stable_file_sha256(path)
        if isinstance(hashed, dict):
            return hashed
        digest, size_bytes = hashed
        try:
            resolved = path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            return _unavailable_model_artifact(
                f"cannot resolve model weight file: {exc}", path=str(path)
            )
        return {
            "status": "ok",
            "kind": "single_file",
            "algorithm": "sha256",
            "sha256": digest,
            "path": str(path),
            "inventory": [
                {
                    "path": path.name,
                    "resolved_path": str(resolved),
                    "sha256": digest,
                    "size_bytes": size_bytes,
                    "symlink": path.is_symlink(),
                }
            ],
        }
    if path.is_dir():
        children, enumeration_errors = _directory_inventory(path)
        if enumeration_errors:
            return _unavailable_model_artifact(
                "cannot enumerate model directory: " + "; ".join(enumeration_errors),
                root=str(path),
            )
        if not children:
            return _unavailable_model_artifact(
                "no recognized model weight files found", root=str(path)
            )
        file_hashes: dict[str, str] = {}
        inventory: list[dict[str, Any]] = []
        for child in children:
            lexical = child.relative_to(path).as_posix()
            hashed = _stable_file_sha256(child)
            if isinstance(hashed, dict):
                return hashed
            digest, size_bytes = hashed
            try:
                resolved = child.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                return _unavailable_model_artifact(
                    f"cannot resolve model weight file: {exc}", path=str(child)
                )
            file_hashes[lexical] = digest
            inventory.append(
                {
                    "path": lexical,
                    "resolved_path": str(resolved),
                    "sha256": digest,
                    "size_bytes": size_bytes,
                    "symlink": child.is_symlink(),
                }
            )
        after_children, after_errors = _directory_inventory(path)
        if after_errors or [p.relative_to(path).as_posix() for p in after_children] != list(
            file_hashes
        ):
            return _unavailable_model_artifact(
                "model inventory changed during read", root=str(path)
            )
        return {
            "status": "ok",
            "kind": "file_set",
            "algorithm": "sha256",
            "folded_sha256": folded_model_artifact_sha256(file_hashes),
            "files": file_hashes,
            "inventory": inventory,
            "root": str(path),
        }
    return _unavailable_model_artifact(
        "model source is not a local file or directory", source=source
    )


def suite_prompt_rollup(
    per_item_hashes: list[str], total_tokens: int
) -> dict[str, Any]:
    canonical = json.dumps(per_item_hashes, separators=(",", ":"), sort_keys=True)
    return {
        "realized_token_count": total_tokens,
        "token_hash_domain": SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN,
        "token_ids_sha256": sha256_hex(
            SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN + "\0" + canonical
        ),
        "text_sha256": None,
    }


def output_policy(
    name: str,
    *,
    requested_tokens: int,
    emitted_tokens: int,
    stop_condition: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "requested_tokens": requested_tokens,
        "emitted_tokens": emitted_tokens,
        "stop_condition": stop_condition,
    }


def fixed_budget_outcome_name(
    *, requested_tokens: int, emitted_tokens: int, stop_condition: str
) -> str:
    """Name the realized outcome of a fixed-budget generation attempt.

    ``fixed_budget_exact`` is evidence-bearing: it is emitted only when the
    requested count was realized and the runtime recorded the corresponding
    stop.  An underrun retains the same existing output-policy record but is
    labelled incomplete rather than falsely asserting exactness.
    """

    if (
        emitted_tokens == requested_tokens
        and stop_condition == "requested_tokens_emitted"
    ):
        return FIXED_BUDGET_EXACT
    return FIXED_BUDGET_INCOMPLETE


def prompt_provenance(token_ids: list[int], text: str | None = None) -> dict[str, Any]:
    return {
        "realized_token_count": len(token_ids),
        "token_hash_domain": PROMPT_TOKEN_IDS_HASH_DOMAIN,
        "token_ids_sha256": prompt_token_ids_sha256(token_ids),
        "text_sha256": sha256_hex(text) if text is not None else None,
    }
