"""Shared, additive evidence interface for harvest, precheck and smoke."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class CaptureEvidence:
    slot: str
    bound_ms: float | None
    status: str
    synthetic: bool


@dataclass(frozen=True)
class MemberEvidence:
    stage_id: str
    run_id: str
    status: str
    flags: tuple[str, ...] = ()
    units: tuple[tuple[str, str, str], ...] = ()
    role: str = "science"
    config_key: str | None = None
    runtime: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StageEvidence:
    stage_id: str
    kind: str
    expected_count: int
    members: tuple[MemberEvidence, ...]


@dataclass(frozen=True)
class SessionEvidence:
    pack_id: str
    stages: tuple[StageEvidence, ...]
    captures: tuple[CaptureEvidence, ...]
    runtime: Mapping[str, Any]
    synthetic: bool
    pending: tuple[str, ...]
    session_id: str | None = None
    stop_reason: str | None = None
    window_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AcceptanceResult:
    verdict: str
    reasons: tuple[str, ...]
    flags: tuple[str, ...]
    structural: bool
    counting: bool = False
    record: Mapping[str, Any] = field(default_factory=dict)


class Acceptance(Protocol):
    def prepare(self, *, ledger_path: Path, plan_tree: Mapping,
                registration_dir: Path, code_identity: Mapping,
                pack_root: Path | None = None,
                ledger_rows: Sequence | None = None) -> object: ...

    def evaluate(self, prepared: object, evidence: SessionEvidence) -> AcceptanceResult: ...


class StubAcceptance:
    def prepare(self, **kwargs: Any) -> object:
        return None

    def evaluate(self, prepared: object, evidence: SessionEvidence) -> AcceptanceResult:
        return AcceptanceResult("UNAVAILABLE", ("acceptance not installed",), (), False)


def load_acceptance() -> Acceptance:
    try:
        from joulewise.b6.acceptance import ACCEPTANCE
    except ImportError:
        return StubAcceptance()
    return ACCEPTANCE
