"""Shared, behavior-preserving mechanics for D-117 campaign generators.

Campaign generator modules own scientific pins and genuine family differences.
This module owns mechanics whose implementations were byte-identical across the
generators.  Keeping these operations here gives later producers one reviewed
write boundary and one generation-identity implementation without turning
campaign policy into a generic configuration language.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any


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

    def refuse(path: Path, reason: str) -> None:
        destination = path.resolve(strict=False)
        raise ValueError(
            f"refusing generation: {reason}: {path} -> {destination}"
        )

    if root.is_symlink():
        refuse(root, "output root is a symlink")
    if root.exists() and not root.is_dir():
        refuse(root, "output root is not a real directory")

    for relative in sorted(outputs, key=lambda path: path.as_posix()):
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


def make_generation_identity_class(
    *,
    module_name: str,
    pack_rel: Path,
    current_family_suffix: str,
    preserve_current_frozen_bytes: bool,
    draft_status: str,
    frozen_status: str,
    freeze_aware_status: Callable[[object], str],
    arm_readiness_attachment: Callable[[], object],
) -> type:
    """Build the common generation-identity type around family-owned pins.

    The returned class deliberately reads the arm attachment through a callback:
    generator tests and successor emission can replace the module-level
    attachment while retaining the historical implementation's behavior.
    """

    preserve_default = preserve_current_frozen_bytes

    class GenerationIdentity:
        def __init__(
            self,
            pack_id: str | None = None,
            family_suffix: str | None = None,
            preserve_current_frozen_bytes: bool | None = None,
        ) -> None:
            if pack_id is None:
                pack_id = pack_rel.name
            if family_suffix is None:
                family_suffix = current_family_suffix
            if preserve_current_frozen_bytes is None:
                preserve_current_frozen_bytes = preserve_default
            self.pack_id = pack_id
            self.family_suffix = family_suffix
            self.preserve_current_frozen_bytes = preserve_current_frozen_bytes
            if not self.family_suffix.startswith("_v") or not self.family_suffix[2:].isdigit():
                raise ValueError("family suffix must use the _v<positive integer> form")
            if int(self.family_suffix[2:]) < 1:
                raise ValueError("family suffix ordinal must be positive")
            expected_pack_id = (
                pack_rel.name.removesuffix(current_family_suffix) + self.family_suffix
            )
            if self.pack_id != expected_pack_id:
                raise ValueError(
                    f"pack id must equal {expected_pack_id!r} for {self.family_suffix}"
                )
            if self.target_ordinal < self.current_ordinal:
                raise ValueError(
                    f"generator family ordinal {self.current_ordinal} refuses the "
                    f"downgrade target {self.pack_id!r} (family ordinal "
                    f"{self.target_ordinal}): an earlier family's committed bytes "
                    "are never rewritten by a later generator, in any mode"
                )
            if self.preserve_current_frozen_bytes and not self.target_is_current:
                raise ValueError("preserve mode requires the current target identity")
            if (
                not self.preserve_current_frozen_bytes
                and self.target_is_current
                and (
                    preserve_default
                    or self.target_status == frozen_status
                )
            ):
                raise ValueError("the current frozen identity requires preserve mode")

        @property
        def pack_rel(self) -> Path:
            return pack_rel.with_name(self.pack_id)

        @property
        def current_ordinal(self) -> int:
            return int(current_family_suffix[2:])

        @property
        def target_ordinal(self) -> int:
            return int(self.family_suffix[2:])

        @property
        def target_is_current(self) -> bool:
            return (
                self.pack_id == pack_rel.name
                and self.target_ordinal == self.current_ordinal
            )

        @property
        def target_is_successor_family(self) -> bool:
            return self.target_ordinal >= 2

        @property
        def target_status(self) -> str:
            if not self.target_is_current:
                return draft_status
            attachment = arm_readiness_attachment()
            if not isinstance(attachment, dict):
                return draft_status
            return freeze_aware_status(attachment.get("freeze_receipt"))

    GenerationIdentity.__name__ = "GenerationIdentity"
    GenerationIdentity.__qualname__ = "GenerationIdentity"
    GenerationIdentity.__module__ = module_name
    return GenerationIdentity


__all__ = [
    "actual_pack_paths",
    "make_generation_identity_class",
    "make_render_json",
    "render_json",
    "sha256_bytes",
    "sidecar_bytes",
    "validate_generation_write_boundary",
]
