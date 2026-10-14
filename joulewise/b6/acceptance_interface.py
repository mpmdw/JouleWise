"""Shared evidence for the precheck, smoke desk and harvest acceptance."""
from __future__ import annotations

import dataclasses
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Mapping, Protocol


@dataclasses.dataclass(frozen=True)
class CaptureEvidence:
    slot: str
    bound_ms: float | None
    status: str
    synthetic: bool


@dataclasses.dataclass(frozen=True)
class MemberEvidence:
    stage_id: str
    run_id: str
    status: str
    flags: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class StageEvidence:
    stage_id: str
    kind: str
    expected_count: int
    members: tuple[MemberEvidence, ...]


@dataclasses.dataclass(frozen=True)
class SessionEvidence:
    pack_id: str
    stages: tuple[StageEvidence, ...]
    captures: tuple[CaptureEvidence, ...]
    runtime: Mapping[str, Any]
    synthetic: bool
    pending: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class AcceptanceResult:
    verdict: str
    reasons: tuple[str, ...]
    flags: tuple[str, ...]
    structural: bool


class Acceptance(Protocol):
    def prepare(self, *, ledger_path: Path, plan_tree: Mapping, registration_dir: Path,
                code_identity: Mapping) -> object: ...

    def evaluate(self, prepared: object, evidence: SessionEvidence) -> AcceptanceResult: ...


class StubAcceptance:
    def prepare(self, **kwargs) -> object:
        return None

    def evaluate(self, prepared: object, evidence: SessionEvidence) -> AcceptanceResult:
        return AcceptanceResult("UNAVAILABLE", ("acceptance not installed",), (), False)


def load_acceptance() -> Acceptance:
    if importlib.util.find_spec("joulewise.b6.acceptance") is None:
        return StubAcceptance()
    return importlib.import_module("joulewise.b6.acceptance").ACCEPTANCE
