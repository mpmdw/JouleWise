"""Hash-bound analysis declarations used by detection-floor validation.

The registry keeps campaign-extensible names out of Python source while the
adjacent checksum keeps a changed declaration from being accepted silently.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


REGISTRY_SCHEMA_VERSION = "joulewise.detection_floor_closed_sets.v1"
REGISTRY_ID = "detection_floor_closed_sets_v1"
# The adjacent digest detects accidental corruption. This source pin is the
# reviewed authority that prevents edited declarations from retaining the
# frozen v1 identity merely by editing that adjacent digest too.
FROZEN_REGISTRY_SHA256 = (
    "fc91df6d14b02d17dba31d1018c31287b65bde2d94f2b608825411f98b2aed1d"
)
REGISTRY_RELATIVE_PATH = Path(
    "configs/analysis_registry/detection_floor_closed_sets.v1.json"
)
REGISTRY_DIGEST_RELATIVE_PATH = REGISTRY_RELATIVE_PATH.with_suffix(".sha256")
ROOT = Path(__file__).resolve().parents[1]

_TOP_KEYS = {
    "schema_version",
    "registry_id",
    "freeze_status",
    "calibration_scopes",
    "floor_metrics",
}
_SCOPE_KEYS = {"scope_id", "authority"}
_METRIC_KEYS = {"name", "window_class", "authority"}
_IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class DetectionFloorRegistryError(ValueError):
    """Raised when the detection-floor declaration registry is not authentic."""


@dataclass(frozen=True)
class DetectionFloorClosedSets:
    """Authenticated closed sets consumed by analysis validators."""

    path: Path
    sha256: str
    calibration_scopes: tuple[str, ...]
    metric_window_classes: Mapping[str, str]

    @property
    def floor_metrics(self) -> tuple[str, ...]:
        return tuple(self.metric_window_classes)


def _exact_keys(value: Mapping[str, Any], expected: set[str], where: str) -> None:
    observed = set(value)
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        detail = []
        if missing:
            detail.append(f"missing {missing}")
        if extra:
            detail.append(f"unexpected {extra}")
        raise DetectionFloorRegistryError(f"{where}: {'; '.join(detail)}")


def _read_digest(path: Path, registry_name: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DetectionFloorRegistryError(
            f"cannot read detection-floor registry digest {path}: {exc}"
        ) from exc
    fields = text.strip().split()
    if len(fields) != 2 or not _SHA256_RE.fullmatch(fields[0]):
        raise DetectionFloorRegistryError(
            f"{path}: expected '<64 lowercase hex>  {registry_name}'"
        )
    recorded_name = fields[1].removeprefix("*")
    if recorded_name != registry_name:
        raise DetectionFloorRegistryError(
            f"{path}: digest names {recorded_name!r}, expected {registry_name!r}"
        )
    return fields[0]


def load_detection_floor_closed_sets(
    *,
    repository_root: Path | None = None,
    registry_path: Path | None = None,
    digest_path: Path | None = None,
) -> DetectionFloorClosedSets:
    """Load and authenticate the registry before returning its declarations."""

    root = ROOT if repository_root is None else Path(repository_root)
    path = Path(registry_path) if registry_path is not None else root / REGISTRY_RELATIVE_PATH
    checksum_path = (
        Path(digest_path)
        if digest_path is not None
        else (path.with_suffix(".sha256") if registry_path is not None else root / REGISTRY_DIGEST_RELATIVE_PATH)
    )
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DetectionFloorRegistryError(
            f"cannot read detection-floor registry {path}: {exc}"
        ) from exc
    expected_sha256 = _read_digest(checksum_path, path.name)
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if observed_sha256 != expected_sha256:
        raise DetectionFloorRegistryError(
            f"{path}: sha256 mismatch (expected {expected_sha256}, observed {observed_sha256})"
        )
    if observed_sha256 != FROZEN_REGISTRY_SHA256:
        raise DetectionFloorRegistryError(
            f"{path}: immutable trust anchor mismatch for {REGISTRY_ID!r}; "
            "changed declarations require a new registry identity"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DetectionFloorRegistryError(f"{path}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise DetectionFloorRegistryError(f"{path}: top level must be an object")
    _exact_keys(value, _TOP_KEYS, "registry")
    if value["schema_version"] != REGISTRY_SCHEMA_VERSION:
        raise DetectionFloorRegistryError(
            f"registry.schema_version: expected {REGISTRY_SCHEMA_VERSION!r}"
        )
    if value["registry_id"] != REGISTRY_ID:
        raise DetectionFloorRegistryError(
            f"registry.registry_id: expected {REGISTRY_ID!r}"
        )
    if value["freeze_status"] != "frozen":
        raise DetectionFloorRegistryError("registry.freeze_status: expected 'frozen'")

    scopes = value["calibration_scopes"]
    if not isinstance(scopes, list) or not scopes:
        raise DetectionFloorRegistryError(
            "registry.calibration_scopes: expected a nonempty array"
        )
    scope_ids: list[str] = []
    for index, row in enumerate(scopes):
        where = f"registry.calibration_scopes[{index}]"
        if not isinstance(row, Mapping):
            raise DetectionFloorRegistryError(f"{where}: expected an object")
        _exact_keys(row, _SCOPE_KEYS, where)
        scope_id = row["scope_id"]
        authority = row["authority"]
        if not isinstance(scope_id, str) or not _IDENTIFIER_RE.fullmatch(scope_id):
            raise DetectionFloorRegistryError(f"{where}.scope_id: invalid identifier")
        if not isinstance(authority, str) or not authority.strip():
            raise DetectionFloorRegistryError(f"{where}.authority: expected nonempty text")
        scope_ids.append(scope_id)
    if len(scope_ids) != len(set(scope_ids)):
        raise DetectionFloorRegistryError(
            "registry.calibration_scopes: duplicate scope_id"
        )

    metrics = value["floor_metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise DetectionFloorRegistryError(
            "registry.floor_metrics: expected a nonempty array"
        )
    metric_window_classes: dict[str, str] = {}
    for index, row in enumerate(metrics):
        where = f"registry.floor_metrics[{index}]"
        if not isinstance(row, Mapping):
            raise DetectionFloorRegistryError(f"{where}: expected an object")
        _exact_keys(row, _METRIC_KEYS, where)
        name = row["name"]
        window_class = row["window_class"]
        authority = row["authority"]
        if not isinstance(name, str) or not _IDENTIFIER_RE.fullmatch(name):
            raise DetectionFloorRegistryError(f"{where}.name: invalid metric identifier")
        if window_class not in {"request", "phase"}:
            raise DetectionFloorRegistryError(
                f"{where}.window_class: expected 'request' or 'phase'"
            )
        if name.startswith("phase_energy_j.") != (window_class == "phase"):
            raise DetectionFloorRegistryError(
                f"{where}: metric prefix and window_class disagree"
            )
        if not isinstance(authority, str) or not authority.strip():
            raise DetectionFloorRegistryError(f"{where}.authority: expected nonempty text")
        if name in metric_window_classes:
            raise DetectionFloorRegistryError(f"registry.floor_metrics: duplicate name {name!r}")
        metric_window_classes[name] = window_class

    return DetectionFloorClosedSets(
        path=path,
        sha256=observed_sha256,
        calibration_scopes=tuple(scope_ids),
        metric_window_classes=metric_window_classes,
    )


@lru_cache(maxsize=1)
def default_detection_floor_closed_sets() -> DetectionFloorClosedSets:
    """Return the repository registry, authenticated once per process."""

    return load_detection_floor_closed_sets()


__all__ = [
    "DetectionFloorClosedSets",
    "DetectionFloorRegistryError",
    "FROZEN_REGISTRY_SHA256",
    "REGISTRY_ID",
    "REGISTRY_DIGEST_RELATIVE_PATH",
    "REGISTRY_RELATIVE_PATH",
    "REGISTRY_SCHEMA_VERSION",
    "default_detection_floor_closed_sets",
    "load_detection_floor_closed_sets",
]
