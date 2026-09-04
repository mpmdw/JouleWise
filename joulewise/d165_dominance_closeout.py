"""Paper-custody adapter for the D-165 dominance close-out validators."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from joulewise.analysis_engine.inputs import (
    AnalysisInputError,
    authenticate_floor_artifact_bytes,
)
from joulewise.analysis_manifest_v3 import validate_finalized_analysis_manifest_v3
from joulewise.dominance_closeout import (
    validate_d165_closeout,
    validate_d165_replay_sidecar,
)


_D165_PAPER_VALIDATOR_CODE_ORDER = (
    "d165_paper_finalized_manifest_invalid",
    "d165_paper_floor_artifact_invalid",
    "d165_paper_replay_sidecar_invalid",
    "d165_paper_closeout_invalid",
)
D165_PAPER_VALIDATOR_CODES = frozenset(_D165_PAPER_VALIDATOR_CODE_ORDER)


def _object(raw: bytes) -> Mapping[str, Any] | None:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def validate_d165_paper_sources(
    *,
    closeout: Mapping[str, Any],
    finalized_manifest_bytes: bytes,
    finalized_manifest_path: Path,
    custody_root: Path,
    floor_artifact_bytes: bytes,
    replay_sidecar_bytes: bytes,
) -> tuple[str, ...]:
    """Replay all four owners and return only closed, non-renderable codes."""

    codes: list[str] = []
    manifest = _object(finalized_manifest_bytes)
    if manifest is None or validate_finalized_analysis_manifest_v3(
        manifest,
        manifest_path=finalized_manifest_path,
        custody_root=custody_root,
    ):
        codes.append("d165_paper_finalized_manifest_invalid")
    try:
        authenticate_floor_artifact_bytes(floor_artifact_bytes)
    except (AnalysisInputError, TypeError, ValueError):
        codes.append("d165_paper_floor_artifact_invalid")
    sidecar = _object(replay_sidecar_bytes)
    if sidecar is None or validate_d165_replay_sidecar(sidecar):
        codes.append("d165_paper_replay_sidecar_invalid")
    if validate_d165_closeout(
        closeout,
        finalized_manifest_bytes=finalized_manifest_bytes,
        floor_artifact_bytes=floor_artifact_bytes,
        replay_sidecar_bytes=replay_sidecar_bytes,
    ):
        codes.append("d165_paper_closeout_invalid")
    return tuple(code for code in _D165_PAPER_VALIDATOR_CODE_ORDER if code in codes)


__all__ = ["D165_PAPER_VALIDATOR_CODES", "validate_d165_paper_sources"]
