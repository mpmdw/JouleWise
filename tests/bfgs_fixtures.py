"""Test-only, digest-bound battery evidence for prospective non-mock bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Mapping
from unittest.mock import patch

from joulewise import battery_float


FIXTURES = Path(__file__).parent / "fixtures" / "battery_float"
WALL_TIME_S = 1790373526.0  # one second after the committed captures' UpdateTime


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _put_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _backend_labels(value: Any, backend: str) -> None:
    """Change backend labels in existing metadata and summary structures."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("telemetry", "telemetry_backend") and item == "mock":
                value[key] = backend
            else:
                _backend_labels(item, backend)
    elif isinstance(value, list):
        for item in value:
            _backend_labels(item, backend)


def rebind_config(bundle: Path | str, *, telemetry_backend: str = "powermetrics") -> None:
    """Rebind config bytes and metadata digest, updating existing backend labels together."""
    if telemetry_backend == "mock":
        raise ValueError("rebind requires a non-mock backend")
    root = Path(bundle)
    config_path = root / "config.json"
    metadata_path = root / "metadata.json"
    config = _json(config_path)
    metadata = _json(metadata_path)
    config["hardware_target"]["telemetry_backend"] = telemetry_backend
    _backend_labels(metadata, telemetry_backend)
    for name in ("summary.json", "summary_metrics.json"):
        path = root / name
        if path.is_file():
            summary = _json(path)
            _backend_labels(summary, telemetry_backend)
            _put_json(path, summary)
    _put_json(config_path, config)
    metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
    _put_json(metadata_path, metadata)


def injected_battery_runner(*, charging: bool = False):
    """Answer only the ruled ioreg argv with fixed, committed fixture bytes."""
    name = "charging-synthetic-from-real.ioreg" if charging else "float.ioreg"
    raw = (FIXTURES / name).read_bytes()

    def run(argv):
        if tuple(argv) != battery_float.IOREG_BATTERY_ARGV:
            raise AssertionError(f"unexpected battery probe argv: {argv!r}")
        return subprocess.CompletedProcess(list(argv), 0, raw, b"")

    return run


def injected_battery_runner_at(now, *, charging: bool = False):
    """For a run on a real clock: the committed bytes with a fresh reading time.

    ``now`` is a callable returning wall time in seconds.  At each call the one
    ``UpdateTime`` line of the committed fixture is rewritten to ``int(now())``,
    so the reading is as fresh as a live probe's; no other byte changes.
    """
    name = "charging-synthetic-from-real.ioreg" if charging else "float.ioreg"
    raw = (FIXTURES / name).read_bytes()

    def run(argv):
        if tuple(argv) != battery_float.IOREG_BATTERY_ARGV:
            raise AssertionError(f"unexpected battery probe argv: {argv!r}")
        stamped, count = re.subn(
            rb'("UpdateTime" = )\d+',
            lambda match: match.group(1) + str(int(now())).encode("ascii"),
            raw,
        )
        if count != 1:
            raise AssertionError("fixture must hold exactly one UpdateTime line")
        return subprocess.CompletedProcess(list(argv), 0, stamped, b"")

    return run


def produce_strict_bundle(
    runs_root: Path | str,
    run_id: str,
    *,
    mutate_config: Callable[[dict[str, Any]], None] | None = None,
    clock_start: float = 1790373526.0,
) -> Path:
    """Run the controller to produce a strict, raw-backed powermetrics bundle."""
    # Keep test-module imports here: test_powermetrics imports this helper.
    from joulewise.clock import FakeClock
    from joulewise.controller import run_benchmark
    from joulewise.schemas import BenchmarkConfig, RunStatus
    from tests.test_powermetrics import (
        FIXTURE_D0_S, SPAWN_ADVANCE_S, documents_to_stream,
        fixture_documents, rebased_documents,
    )

    fixture = (Path(__file__).parent / "fixtures" / "powermetrics_sample.plist").read_bytes()
    config_data = _json(Path(__file__).parent.parent / "configs" / "examples" / "mock_local.json")
    config_data["run_id"] = run_id
    config_data["hardware_target"]["telemetry_backend"] = "powermetrics"
    config_data["workload_profile"]["output_tokens"] = 300
    config_data["sampling"] = {"power_hz": 2.0, "idle_seconds": 5.0}
    if mutate_config is not None:
        mutate_config(config_data)
    if config_data["hardware_target"]["telemetry_backend"] == "mock":
        raise ValueError("strict bundle on mock backend")
    config = BenchmarkConfig.from_mapping(config_data)
    clock = FakeClock(start=clock_start)

    def fake_run(command, **kwargs):
        if "-o" in command:
            Path(command[command.index("-o") + 1]).write_bytes(fixture)
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

    class FakePopen:
        def __init__(self, command, **kwargs):
            self.path = Path(command[command.index("-o") + 1])
            self.path.write_bytes(
                documents_to_stream(
                    rebased_documents(
                        fixture_documents(),
                        first_endpoint_s=clock.now() + FIXTURE_D0_S,
                    )
                )
            )
            self.returncode = None
            clock.sleep(SPAWN_ADVANCE_S)

        def poll(self):
            return self.returncode

        def terminate(self):
            self.returncode = 0

        def kill(self):
            self.returncode = -9

        def communicate(self, timeout=None):
            self.returncode = 0
            return b"", b""

    with (
        patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
        patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
    ):
        bundle, summary = run_benchmark(
            config, Path(runs_root), clock, battery_runner=injected_battery_runner(),
        )
    assert summary.status == RunStatus.SUCCEEDED, (
        f"strict bundle run failed: {summary.status}"
    )
    return bundle


def _bound_nonmock(root: Path) -> dict[str, Any]:
    """Refuse before creating raw files or changing metadata."""
    config_bytes = (root / "config.json").read_bytes()
    metadata = _json(root / "metadata.json")
    if hashlib.sha256(config_bytes).hexdigest() != metadata.get("config_sha256"):
        raise ValueError("config not bound")
    backend = json.loads(config_bytes)["hardware_target"]["telemetry_backend"]
    if backend == "mock":
        raise ValueError("battery pair on mock config")
    return metadata


def _bundle_span(root: Path) -> tuple[int, int]:
    path = root / "events.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []
    starts = [r for r in rows if r.get("event_type") == "stage_started" and r.get("phase") == "idle_baseline"]
    ends = [r for r in rows if r.get("event_type") == "stage_completed" and r.get("phase") == "idle_drift_sentinel"]
    start = starts[0]["metadata"]["monotonic_ns"] if starts else 30
    end = ends[-1]["metadata"]["monotonic_ns"] if ends else max(start, 80)
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < start:
        raise ValueError("invalid bundle span")
    additions = []
    for present, event_type, phase, stamp in (
        (starts, "stage_started", "idle_baseline", start),
        (ends, "stage_completed", "idle_drift_sentinel", end),
    ):
        if not present:
            additions.append({"timestamp_s": float(stamp), "event_type": event_type,
                              "phase": phase, "message": "fixture boundary",
                              "metadata": {"monotonic_ns": stamp}})
    if additions:
        with path.open("a", encoding="utf-8") as stream:
            for row in additions:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
    return start, end


def _record_pair(root: Path, *, kind: str, charging: bool,
                 run_id: str | None = None, validation_id: str | None = None,
                 slot: str | None = None) -> dict[str, Any]:
    span = _bundle_span(root) if kind == "bundle" else None
    pair = {}
    for phase in ("pre", "post"):
        relative = f"raw/battery_float.{phase}.ioreg"
        is_charging = charging and phase == "pre"
        runner = injected_battery_runner(charging=is_charging)
        if span is None:
            stamps = (10, 20) if phase == "pre" else (90, 100)
        else:
            stamps = (max(0, span[0] - 1), span[0]) if phase == "pre" else (span[1], span[1] + 1)
        ticks = iter(stamps)
        record, raw = battery_float.observe(
            phase=f"{kind}_{phase}", runner=runner, raw_path=relative,
            session_id=run_id, slot=slot, attempt_id=validation_id,
            wall_time_s=WALL_TIME_S, monotonic_ns=lambda: next(ticks),
        )
        (root / "raw").mkdir(exist_ok=True)
        (root / relative).write_bytes(raw)
        pair[phase] = record
    return pair


def write_passing_pair(bundle: Path | str) -> dict[str, Any]:
    """Write an authentic passing bundle pair only after a non-mock rebind."""
    root = Path(bundle)
    metadata = _bound_nonmock(root)
    metadata["battery_float"] = _record_pair(root, kind="bundle", charging=False,
                                              run_id=metadata["run_id"])
    _put_json(root / "metadata.json", metadata)
    return metadata["battery_float"]


def write_charging_pair(bundle: Path | str) -> dict[str, Any]:
    """Write an authentic confounded bundle pair only after a non-mock rebind."""
    root = Path(bundle)
    metadata = _bound_nonmock(root)
    metadata["battery_float"] = _record_pair(root, kind="bundle", charging=True,
                                              run_id=metadata["run_id"])
    _put_json(root / "metadata.json", metadata)
    return metadata["battery_float"]


def write_capture_evidence(capture_dir: Path | str, *, validation_id: str,
                           session_id: str | None = None, slot: str | None = None,
                           charging: bool = False,
                           evidence: Mapping[str, Any] | None = None) -> str:
    """Write parseable capture evidence and pair; return its SHA-256 for a ledger."""
    root = Path(capture_dir)
    root.mkdir(parents=True, exist_ok=True)
    pair = _record_pair(root, kind="slot", charging=charging, run_id=session_id,
                        validation_id=validation_id, slot=slot)
    document = dict(evidence or {})
    document.update({"schema_version": "joulewise.instrument_evidence.v1",
                     "validation_id": validation_id, "battery_float": pair})
    path = root / "instrument_evidence.json"
    _put_json(path, document)
    return hashlib.sha256(path.read_bytes()).hexdigest()
