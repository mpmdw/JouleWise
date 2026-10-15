"""Small lane contracts and their production adapters."""
from __future__ import annotations

import json
import plistlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class LaneMissing:
    name: str


@dataclass(frozen=True)
class Hazard:
    hazard: str
    detail: str = ""  # never copied to mail


@dataclass(frozen=True)
class Exclusion:
    code: str
    pack_id: str | None = None


@dataclass(frozen=True)
class PrecheckResult:
    would_refuse: tuple[Hazard, ...] = ()
    certain_exclusion: tuple[Exclusion, ...] = ()
    thin_margin: bool = False
    predicted_flags: tuple[str, ...] = ()
    fingerprint: dict = field(default_factory=dict)
    remedies: tuple[str, ...] = ()


@dataclass(frozen=True)
class Prepared:
    session_id: str
    plan_path: str
    terminal_path: str
    max_s: int


@dataclass(frozen=True)
class Running:
    handle: str


@dataclass(frozen=True)
class Refused:
    """The driver refused at arm or t0; no measured run started (driver lane at merge)."""
    hazards: tuple[str, ...]


@dataclass(frozen=True)
class Done:
    chain_rc: int = 0
    physics_stop: str | None = None


@dataclass(frozen=True)
class SmokeResult:
    status: str
    codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SessionLine:
    session_id: str
    packs: tuple[str, ...]
    chain_rc: int = 0
    harvest_rc: int = 0
    verdict: str = "COLLECTED"
    physics_stop: str | None = None
    window_flags: tuple[str, ...] = ()
    pack_flags: dict = field(default_factory=dict)
    counts: dict = field(default_factory=dict)
    structure_ok: bool = True
    structure_defects: tuple[str, ...] = ()
    minutes: dict = field(default_factory=dict)
    compressed: bool = False


@dataclass(frozen=True)
class HarvestCapabilities:
    pack_scoped_flags: bool = False
    hidden_offsets: bool = False
    block_id_strata: bool = False


class P1(Protocol):
    def run(self, layout, plan_path: str) -> PrecheckResult | LaneMissing: ...


class P2(Protocol):
    def remedy(self, hazard: str) -> bool | LaneMissing: ...


class D1(Protocol):
    def prepare_session(self, layout, rendered, *, smoke: bool, keep: dict,
                        staging_root: Path) -> Prepared | LaneMissing: ...


class D2(Protocol):
    def launch(self, prepared: Prepared) -> Running | Done | Refused | LaneMissing: ...
    def status(self, handle: Running) -> Running | Done | Refused | LaneMissing: ...


class S1(Protocol):
    def evaluate_smoke(self, prepared: Prepared, done: Done) -> SmokeResult | LaneMissing: ...


class K1(Protocol):
    def session_desk(self, prepared: Prepared, done: Done) -> SessionLine | LaneMissing: ...


class H3(Protocol):
    def capabilities(self) -> HarvestCapabilities | LaneMissing: ...


class A1(Protocol):
    def precision_reached(self, pack_id: str, reg, counting_ids: list[str]) -> bool | None | LaneMissing: ...


class PrecheckStub:
    def run(self, layout, plan_path): return LaneMissing("precheck")
    def remedy(self, hazard): return LaneMissing("precheck")


class DriverStub:
    def prepare_session(self, layout, rendered, **kwargs): return LaneMissing("driver")
    def launch(self, prepared): return LaneMissing("driver")
    def status(self, handle): return LaneMissing("driver")


class DeskStub:
    def evaluate_smoke(self, prepared, done): return LaneMissing("smoke")
    def session_desk(self, prepared, done): return LaneMissing("desk")


class HarvestStub:
    def capabilities(self): return LaneMissing("harvest")


class AnalysisStub:
    def precision_reached(self, pack_id, reg, counting_ids): return LaneMissing("analysis")


@dataclass(frozen=True)
class Lanes:
    precheck: P1 | P2
    driver: D1 | D2
    desk: S1 | K1
    harvest: H3
    analysis: A1


def resolve(repo_root=None, loop_root=None, *, run=None, config=None, clock=None) -> Lanes:
    if repo_root is None or loop_root is None:
        return Lanes(PrecheckStub(), DriverStub(), DeskStub(), HarvestStub(), AnalysisStub())
    import subprocess
    from joulewise.b6.analysis_lane import AnalysisLane, HarvestLane
    from joulewise.b6.precheck_lane import PrecheckLane
    from joulewise.b6.driver_lane import DriverLane
    from joulewise.b6.desk_lane import DeskLane
    options = {"config": config}
    if clock is not None:
        options["clock"] = clock
    return Lanes(PrecheckLane(repo_root, loop_root, run or subprocess.run),
                 DriverLane(repo_root, loop_root, run or subprocess.run, **options),
                 DeskLane(repo_root, loop_root, run or subprocess.run), HarvestLane(), AnalysisLane())


def collection_live(loop_root) -> bool:
    """A collection may be measuring: the marker exists and its terminal record does not (yet)."""
    try:
        lines = (Path(loop_root) / "collection.active").read_text().splitlines()
    except FileNotFoundError:
        return False
    return not lines or not lines[0] or not Path(lines[0]).exists()


class Waker:
    """Record once per reason/context, optionally bootstrap a one-shot job."""
    def __init__(self, loop_root, *, wake_argv=(), run=None):
        self.root = Path(loop_root) / "wake"
        self.argv, self.run = list(wake_argv), run

    def wake(self, reason, ctx):
        self.root.mkdir(parents=True, exist_ok=True)
        records = sorted(self.root.glob("*.json"))
        for path in records:
            record = json.loads(path.read_text())
            if record["reason"] == reason and record["ctx"] == ctx:
                self._bootstrap(path, record)
                return record
        seq = len(records) + 1
        record = {"seq": seq, "reason": reason, "ctx": ctx}
        path = self.root / f"{seq:06}.json"
        path.write_text(json.dumps(record) + "\n")
        self._bootstrap(path, record)
        return record

    def bootstrap_deferred(self):
        if collection_live(self.root.parent):
            return
        for path in sorted(self.root.glob("*.json")):
            record = json.loads(path.read_text())
            if record.get("job_deferred"):
                self._bootstrap(path, record)

    def _bootstrap(self, record_path, record):
        if self.argv and self.run is not None and not record.get("bootstrap_attempted"):
            if collection_live(self.root.parent):
                record["job_deferred"] = True
                record_path.write_text(json.dumps(record) + "\n")
                return
            import os
            seq = record["seq"]
            label = f"com.joulewise.b6wake.{seq}"
            path = self.root / f"{label}.plist"
            argv = [arg.replace("{wake_record}", str(record_path.resolve())) for arg in self.argv]
            path.write_bytes(plistlib.dumps({"Label": label, "ProgramArguments": argv,
                                             "RunAtLoad": True, "ProcessType": "Background"}))
            record.update(bootstrap_attempted=True, job_deferred=False)
            record_path.write_text(json.dumps(record) + "\n")
            self.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(path)])
