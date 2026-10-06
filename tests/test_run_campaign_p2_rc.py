"""Gate-prune round 2, lane P2-RC: scripts/run_campaign.py on the HAZARD_PACK path.

PLAN2 (night-archive gate-prune/prune2/PLAN2.md) items, each checked on a HAZARD
runs root and on a plain (legacy) runs root, whose behaviour must not change:

- M3: in-window validation is structural (``strict=False``); the strict checks
  are deferred to the harvest, and the cheap keepers still run.
- S4: the stage writes one provisional minimal ``campaign_verdict`` row and never
  evaluates the sampling audit, idle-admission core or claim readiness.

The stages run in process (``run_campaign.main``) with the fake CLI of
``tests.test_run_campaign_hazard_flags`` plus a few extra member behaviours.
"""

from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.run_campaign as run_campaign
from tests.test_run_campaign_hazard_flags import (
    FAKE_CLI,
    PREFLIGHT_ENV,
    ROOT,
    TEST_POLICY,
    _observe,
    _Stage,
)

# Extra member behaviours, keyed on the run id; anything else falls through to
# the shared fake CLI, which writes a real (mock-telemetry) bundle.
PRELUDE = textwrap.dedent(
    """
    import json as _json, os as _os, signal as _signal, subprocess as _subprocess, sys as _sys, time as _time
    from pathlib import Path as _Path

    _rid = _json.loads(_Path(_sys.argv[2]).read_text())["run_id"]
    _runs = _Path(_sys.argv[_sys.argv.index("--runs-dir") + 1])
    _mark = str(_runs.parent / (_runs.name + "." + _rid))

    def _ordered():
        with (_runs.parent / (_runs.name + ".order.log")).open("a") as _handle:
            _handle.write(_rid + "\\n")

    if "hang" in _rid or "stubborn" in _rid:
        _ordered()
        _grandchild = _subprocess.Popen([_sys.executable, "-c", "import time; time.sleep(30)"])
        _Path(_mark + ".grandchild").write_text(str(_grandchild.pid))
        if "stubborn" in _rid:
            _signal.signal(_signal.SIGTERM, _signal.SIG_IGN)
        else:
            def _term(signum, frame):
                _Path(_mark + ".term").write_text("term")
                raise SystemExit(143)
            _signal.signal(_signal.SIGTERM, _term)
        print("member " + _rid + " waiting since 12:00:05", file=_sys.stderr, flush=True)
        _Path(_mark + ".ready").write_text("ready")
        # Self-limited, so a tree without the cap (the base) fails instead of hanging.
        _until = _time.monotonic() + 12.0
        while _time.monotonic() < _until:
            _time.sleep(0.2)
        raise SystemExit(5)
    if "refuse" in _rid:
        _ordered()
        print("loading 3 shards", file=_sys.stderr)
        print("error: idle admission refused member 7 at 0.25 W", file=_sys.stderr)
        print("   ", file=_sys.stderr)
        raise SystemExit(2)
    if "lineage" in _rid:
        _ordered()
        print("Traceback (most recent call last):", file=_sys.stderr)
        print("joulewise.arm_readiness.LaunchLineageError: launch_consumption_missing: "
              "no consumption record for window 42", file=_sys.stderr)
        raise SystemExit(1)
    """
).lstrip()

TEMPERATURE_OUTPUT = (
    '+-o AppleSmartBattery  <class AppleSmartBattery>\n'
    '    {\n'
    '      "VirtualTemperature" = 2999\n'
    '      "Temperature" = 3035\n'
    '    }\n'
)


def setUpModule() -> None:
    temporary = tempfile.TemporaryDirectory()
    unittest.addModuleCleanup(temporary.cleanup)
    env = patch.dict(os.environ, {
        "JOULEWISE_CUSTODY_PARENT": str(Path(temporary.name) / "custody-parent"),
        "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": "[]",
    })
    env.start()
    unittest.addModuleCleanup(env.stop)
    identity = patch.object(run_campaign, "observe_identity", side_effect=_observe)
    identity.start()
    unittest.addModuleCleanup(identity.stop)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _gone_within(pid: int, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not _alive(pid):
            return True
        time.sleep(0.05)
    return not _alive(pid)


class _P2Stage(_Stage):
    def setUp(self) -> None:
        super().setUp()
        self.cli.write_text(PRELUDE + FAKE_CLI.format(root=str(ROOT), preflight_env=PREFLIGHT_ENV))
        # Short cap and grace so a hung member resolves in seconds; the
        # thermistor command is a fixed fake so no test reads the real battery.
        for name, value in (("HAZARD_MEMBER_CAP_S", 1.5), ("HAZARD_MEMBER_TERM_GRACE_S", 1.0),
                            ("BATTERY_TEMPERATURE_COMMAND",
                             (sys.executable, "-c", f"print({TEMPERATURE_OUTPUT!r}, end='')"))):
            patcher = patch.object(run_campaign, name, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def member_rows(self, runs: Path) -> list[dict]:
        return [row for row in self.log_rows(runs) if "run_id" in row and "record_type" not in row]

    def row_for(self, runs: Path, run_id: str) -> dict:
        rows = [row for row in self.member_rows(runs) if row["run_id"] == run_id]
        self.assertEqual(len(rows), 1, self.log_rows(runs))
        return rows[0]

    def manifests(self, runs: Path) -> list[dict]:
        return [json.loads(path.read_text())
                for path in sorted((runs / "campaign_manifests").glob("*.json"))]

    def marker(self, runs: Path, run_id: str, suffix: str) -> Path:
        return runs.parent / f"{runs.name}.{run_id}.{suffix}"


class StrictValidationDeferredTests(_P2Stage):
    """M3."""

    def _recording(self):
        real = run_campaign.validate_bundle
        calls: list[bool] = []

        def wrapper(path, strict=False):
            calls.append(bool(strict))
            return real(path, strict=strict)

        return calls, patch.object(run_campaign, "validate_bundle", side_effect=wrapper)

    def test_hazard_member_is_validated_structurally_and_labelled_deferred(self) -> None:
        runs = self.hazard_root()
        calls, patcher = self._recording()
        with patcher:
            result = self.run_stage(self.configs("hz-m3-a", "hz-m3-b"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(calls, [False, False])
        for run_id in ("hz-m3-a", "hz-m3-b"):
            member = self.row_for(runs, run_id)["members"][0]
            self.assertIs(member["strict_valid"], True)
            self.assertEqual(member["strict_validation"], "deferred_to_harvest")
            self.assertEqual(member["collection_classification"], "usable")

    def test_keepers_still_fail_the_member_in_window(self) -> None:
        runs = self.hazard_root()
        disagree = type("Identity", (), {"custody_bound_config": True, "triangle_agrees": False})()
        with patch.object(run_campaign, "custody_telemetry_identity", return_value=disagree):
            result = self.run_stage(self.configs("hz-m3-tri"), runs)
        self.assertEqual(result.code, 1, result.err)
        member = self.row_for(runs, "hz-m3-tri")["members"][0]
        self.assertIs(member["strict_valid"], False)
        self.assertIn("bundle_strict_invalid", member["validation_problems"])

        runs = self.hazard_root("runs_claim_binding")
        with patch.object(run_campaign, "_bundle_config_binding_problem",
                          return_value="config_manifest_mismatch: fixture"):
            result = self.run_stage(self.configs("hz-m3-bind", name="configs-bind"), runs)
        self.assertEqual(result.code, 1, result.err)
        member = self.row_for(runs, "hz-m3-bind")["members"][0]
        self.assertIn("config_manifest_mismatch", member["collection_integrity_flags"])
        self.assertEqual(member["collection_classification"], "failed")

    def test_structural_problem_still_fails_the_member(self) -> None:
        runs = self.hazard_root()
        with patch.object(run_campaign, "validate_bundle",
                          return_value=["power_trace.csv: fixture structural problem"]):
            result = self.run_stage(self.configs("hz-m3-struct"), runs)
        self.assertEqual(result.code, 1, result.err)
        member = self.row_for(runs, "hz-m3-struct")["members"][0]
        self.assertIs(member["strict_valid"], False)

    def test_legacy_root_still_validates_strictly(self) -> None:
        runs = self.plain_root()
        calls, patcher = self._recording()
        with patcher:
            result = self.run_stage(self.configs("pl-m3-a"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertIn(True, calls)
        self.assertNotIn(False, calls)
        member = self.row_for(runs, "pl-m3-a")["members"][0]
        self.assertNotIn("strict_validation", member)


class MinimalStageVerdictTests(_P2Stage):
    """S4 (closes A20)."""

    SKIPPED = ("sampling_audit_for", "idle_admission_core_verdict", "claim_readiness_for",
               "apply_idle_admission_claim_barrier")

    def _watching(self):
        patchers = {name: patch.object(run_campaign, name, wraps=getattr(run_campaign, name))
                    for name in self.SKIPPED}
        return patchers

    def test_hazard_stage_writes_one_provisional_minimal_row(self) -> None:
        runs = self.hazard_root()
        patchers = self._watching()
        mocks = {name: patcher.start() for name, patcher in patchers.items()}
        try:
            result = self.run_stage(self.configs("hz-s4-a", "hz-s4-b"), runs)
        finally:
            for patcher in patchers.values():
                patcher.stop()
        self.assertEqual(result.code, 0, result.err)
        for name, mock in mocks.items():
            self.assertEqual(mock.call_count, 0, name)
        verdicts = self.verdicts(runs)
        self.assertEqual(len(verdicts), 1)
        row = verdicts[0]
        self.assertIs(row["provisional"], True)
        self.assertEqual(row["idle_admission_core"], {"status": "deferred_to_desk"})
        self.assertEqual(row["strict_validation"], "deferred_to_harvest")
        self.assertEqual(row["collection"]["verdict"], "usable")
        self.assertEqual(row["collection"]["categories"]["usable"], ["hz-s4-a", "hz-s4-b"])
        self.assertEqual(row["counts"], {"ok": 2})
        self.assertNotIn("claim_readiness", row)
        self.assertNotIn("members", row)

    def test_a_failed_member_keeps_rc_1(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-s4-ok", "hz-s4-nobundle"), runs)
        self.assertEqual(result.code, 1, result.err)
        row = self.verdicts(runs)[0]
        self.assertEqual(row["collection"]["verdict"], "blocked")
        self.assertEqual(row["collection"]["categories"]["missing"], ["hz-s4-nobundle"])

    def test_legacy_root_keeps_the_full_verdict(self) -> None:
        runs = self.plain_root()
        result = self.run_stage(self.configs("pl-s4-a"), runs)
        self.assertEqual(result.code, 0, result.err)
        row = self.verdicts(runs)[0]
        self.assertNotIn("provisional", row)
        self.assertIn("claim_readiness", row)
        self.assertIn("sampling_audit", row)
        self.assertEqual(len(row["members"]), 1)


if __name__ == "__main__":
    unittest.main()
