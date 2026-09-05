"""Shared, behavior-preserving mechanics for D-117 campaign generators.

Campaign generator modules own scientific pins and genuine family differences.
This module owns mechanics whose implementations were byte-identical across the
live generators. Keeping these operations here gives later producers one
reviewed write boundary without turning campaign policy into a generic
configuration language.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any


_generation_write_boundary_observer: (
    Callable[[Path, tuple[Path, ...]], None] | None
) = None


def render_json(value: Any, transform: Callable[[Any], Any]) -> bytes:
    """Return the canonical bytes used by campaign generator artifacts."""

    return (
        json.dumps(transform(value), indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def make_render_json(transform: Callable[[Any], Any]) -> Callable[[Any], bytes]:
    """Bind canonical rendering to one generator's identity projection."""

    def bound_render_json(value: Any) -> bytes:
        return render_json(value, transform)

    bound_render_json.shared_implementation = render_json  # type: ignore[attr-defined]
    return bound_render_json


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 digest of *data*."""

    return hashlib.sha256(data).hexdigest()


def sidecar_bytes(digest: str, filename: str) -> bytes:
    """Render a GNU-compatible SHA-256 sidecar row."""

    return f"{digest}  {filename}\n".encode("utf-8")


def actual_pack_paths(pack_root: Path) -> set[Path]:
    """Return the pack's regular-file inventory, excluding Python caches."""

    return {
        path.relative_to(pack_root)
        for path in pack_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def validate_generation_write_boundary(
    output_root: Path, outputs: Iterable[Path]
) -> None:
    """Refuse link traversal or anomalous existing nodes before any write.

    This is a check-then-write boundary.  It closes accidental traversal for
    single-operator desk generation; it does not claim to resist a concurrent
    adversarial process that swaps a checked path before the later write.
    """

    root = output_root.absolute()
    relative_outputs = tuple(outputs)

    def refuse(path: Path, reason: str) -> None:
        destination = path.resolve(strict=False)
        raise ValueError(
            f"refusing generation: {reason}: {path} -> {destination}"
        )

    if root.is_symlink():
        refuse(root, "output root is a symlink")
    if root.exists() and not root.is_dir():
        refuse(root, "output root is not a real directory")

    for relative in sorted(relative_outputs, key=lambda path: path.as_posix()):
        current = root
        for component in relative.parts[:-1]:
            current = current / component
            if current.is_symlink():
                refuse(current, "write ancestor is a symlink")
            if current.exists() and not current.is_dir():
                refuse(current, "write ancestor is not a real directory")
        target = current / relative.name
        if target.is_symlink():
            refuse(target, "write target is a symlink")
        if target.exists() and not target.is_file():
            refuse(target, "existing write target is not a regular file")

    if _generation_write_boundary_observer is not None:
        _generation_write_boundary_observer(root, relative_outputs)


__all__ = [
    "actual_pack_paths",
    "make_render_json",
    "render_json",
    "sha256_bytes",
    "sidecar_bytes",
    "validate_generation_write_boundary",
]
