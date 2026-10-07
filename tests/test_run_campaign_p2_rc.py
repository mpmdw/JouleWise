"""Gate-prune round 2, lane P2-RC: scripts/run_campaign.py on the HAZARD_PACK path.

PLAN2 (night-archive gate-prune/prune2/PLAN2.md) items, each checked on a HAZARD
runs root and on a plain (legacy) runs root, whose behaviour must not change:

- M3: in-window validation is structural (``strict=False``); the strict checks
  are deferred to the harvest, and the cheap keepers still run.
- S4: the stage writes one provisional minimal ``campaign_verdict`` row and never
  evaluates the sampling audit, idle-admission core or claim readiness.
- Row 8: a member child past the wall-clock cap gets TERM, then KILL after the
  grace; its tree is proven gone; a ``timeout`` row and ``member.timeout``; two
  consecutive timeouts drain the window (only end references still run); a
  SIGTERM to the stage forwards to the child, appends ``interrupted`` and
  releases the lock.
- Yield E: the child's stderr goes to a per-member file, is copied into the
  stage log, and a failed member's last line (digits as ``#``) is ``child_refusal``.
- Battery thermistor: one ``ioreg`` reading per member at the cooldown release,
  in the campaign manifest.

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
from tests import child_guard

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


class MemberCapTests(_P2Stage):
    """Row 8: the wall-clock cap, the teardown proof, the timeout row and the drain."""

    def test_hung_member_is_terminated_flagged_and_the_stage_continues(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-hang-1", "hz-cap-ok"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.invoked(runs), ["hz-hang-1", "hz-cap-ok"])
        self.assertTrue(self.marker(runs, "hz-hang-1", "term").exists(), result.err)
        grandchild = int(self.marker(runs, "hz-hang-1", "grandchild").read_text())
        self.assertTrue(_gone_within(grandchild, 5.0), "grandchild survived the member timeout")
        row = self.row_for(runs, "hz-hang-1")
        self.assertEqual(row["status"], "timeout")
        record = row["member_timeout"]
        self.assertIs(record["timed_out"], True)
        self.assertIs(record["kill_escalated"], False)
        self.assertEqual(record["cap_s"], 1.5)
        self.assertIs(record["teardown"]["census_completed"], True)
        self.assertEqual(record["teardown"]["survivors"], [])
        self.assertGreaterEqual(record["teardown"]["tracked"], 2)
        self.assertEqual(self.row_for(runs, "hz-cap-ok")["status"], "ok")
        flags = [row for row in self.flags() if row["code"] == "member.timeout"]
        self.assertEqual([flag["scope"]["run_id"] for flag in flags], ["hz-hang-1"])
        self.assertEqual(flags[0]["scope"]["level"], "member")
        self.assertEqual(flags[0]["observed"]["consecutive"], 1)
        self.assertIs(flags[0]["observed"]["drain_requested"], False)
        self.assertEqual([row for row in self.flags() if row["code"] == "teardown.survivors"], [])
        self.assertFalse((runs / "campaign.lock").exists())

    def test_a_child_ignoring_term_is_killed_after_the_grace(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-stubborn-1"), runs)
        self.assertEqual(result.code, 1, result.err)
        row = self.row_for(runs, "hz-stubborn-1")
        self.assertEqual(row["status"], "timeout")
        self.assertIs(row["member_timeout"]["kill_escalated"], True)
        self.assertIn("SIGKILL", {entry["signal"] for entry in row["member_timeout"]["signals"]})
        self.assertEqual(row["member_timeout"]["teardown"]["survivors"], [])
        grandchild = int(self.marker(runs, "hz-stubborn-1", "grandchild").read_text())
        self.assertTrue(_gone_within(grandchild, 5.0))

    def test_two_consecutive_timeouts_drain_this_and_later_stages(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-hang-a", "hz-hang-b", "hz-after"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.invoked(runs), ["hz-hang-a", "hz-hang-b"])
        drained = self.row_for(runs, "hz-after")
        self.assertEqual(drained["status"], "drained")
        self.assertEqual(drained["drained"]["reason"], "consecutive_member_timeouts")
        marker = self.custody / "member-timeouts" / "drain.json"
        self.assertTrue(marker.is_file())
        self.assertEqual(json.loads(marker.read_text())["trigger_bundle_ids"], ["hz-hang-b"])
        flags = [row for row in self.flags() if row["code"] == "member.timeout"]
        self.assertEqual([(flag["scope"]["run_id"], flag["observed"]["drain_requested"])
                          for flag in flags], [("hz-hang-a", False), ("hz-hang-b", True)])
        verdict = self.verdicts(runs)[0]
        self.assertEqual(verdict["counts"], {"drained": 1, "timeout": 2})
        # A later stage of the same window (another runs root, same custody) drains too.
        later = self.hazard_root("runs_bound")
        result = self.run_stage(self.configs("hz-later", name="configs-later"), later)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.invoked(later), [])
        self.assertEqual(self.row_for(later, "hz-later")["status"], "drained")

    def test_a_completed_member_resets_the_consecutive_count(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(
            self.configs("hz-hang-x", "hz-mid-ok", "hz-hang-y", "hz-tail-ok"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.invoked(runs), ["hz-hang-x", "hz-mid-ok", "hz-hang-y", "hz-tail-ok"])
        self.assertFalse((self.custody / "member-timeouts" / "drain.json").exists())
        flags = [row for row in self.flags() if row["code"] == "member.timeout"]
        self.assertEqual([flag["observed"]["consecutive"] for flag in flags], [1, 1])

    def test_end_references_are_exempt_from_the_drain(self) -> None:
        end = type("Info", (), {"role": run_campaign.NEG8_REFERENCE_END_ROLE,
                                "sentinel_position": "end"})()
        start = type("Info", (), {"role": run_campaign.NEG8_REFERENCE_START_ROLE,
                                  "sentinel_position": "start"})()
        science = type("Info", (), {"role": "comparative_abba_member", "sentinel_position": None})()
        self.assertTrue(run_campaign._hazard_drain_exempt(end))
        self.assertFalse(run_campaign._hazard_drain_exempt(start))
        self.assertFalse(run_campaign._hazard_drain_exempt(science))

    def test_legacy_root_has_no_cap_and_no_runner(self) -> None:
        runs = self.plain_root()
        with patch.object(run_campaign, "_hazard_run_authenticated_campaign_child",
                          side_effect=AssertionError("HAZARD runner on a legacy root"),
                          create=True):
            result = self.run_stage(self.configs("pl-cap-ok"), runs)
        self.assertEqual(result.code, 0, result.err)
        row = self.row_for(runs, "pl-cap-ok")
        self.assertNotIn("child_stderr", row)
        self.assertNotIn("member_timeout", row)
        self.assertFalse((self.custody / "member-timeouts").exists())


class SigtermTests(_P2Stage):
    """Row 8: SIGTERM to a HAZARD stage forwards, records and releases the lock."""

    DRIVER = textwrap.dedent(
        """
        import os, sys
        from unittest.mock import patch
        sys.path.insert(0, {root!r})
        import scripts.run_campaign as run_campaign
        from joulewise.measurement_liveness import Identity, observe_identity

        def observe(pid):
            return Identity("LIVE", "Tue Sep 8 01:02:03 2026") if pid == os.getpid() \\
                else observe_identity(pid)

        run_campaign.HAZARD_MEMBER_TERM_GRACE_S = 2.0
        run_campaign.BATTERY_TEMPERATURE_COMMAND = (sys.executable, "-c", "print('')")
        with patch.object(run_campaign, "observe_identity", side_effect=observe):
            raise SystemExit(run_campaign.main(sys.argv[1:]))
        """
    ).lstrip()

    def test_first_sigterm_unwinds_before_any_signal_reaches_the_child(self) -> None:
        # The unwind snapshots the child's tree before signalling it; a TERM
        # sent from the handler first could let a grandchild be reparented
        # out of reach.  A later SIGTERM is forwarded directly.
        child = type("Child", (), {"pid": 424242, "returncode": None})()
        sent: list = []
        with patch.dict(run_campaign._HAZARD_SIGNAL_STATE,
                        {"child": child, "run_id": "x", "raised": False}), \
                patch.object(run_campaign.os, "kill", side_effect=lambda *a: sent.append(a)):
            with self.assertRaises(run_campaign._HazardInterrupted):
                run_campaign._hazard_sigterm_handler(signal.SIGTERM, None)
            self.assertEqual(sent, [])
            run_campaign._hazard_sigterm_handler(signal.SIGTERM, None)
            self.assertEqual(sent, [(424242, signal.SIGTERM)])

    def test_a_reparented_descendant_stays_in_the_signalling_set(self) -> None:
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        orphan = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(31)"])
        self.addCleanup(lambda: [p.kill() or p.wait() for p in (child, orphan)])
        watch = run_campaign._HazardMemberWatch(child, cap_s=60, grace_s=1)
        table = run_campaign._hazard_process_table()
        self.assertIsNotNone(table)
        row = next(row for row in table if row["pid"] == orphan.pid)
        watch.tracked[orphan.pid] = dict(row)  # tracked earlier, no longer under the child
        pids = {row["pid"] for row in watch._snapshot()}
        self.assertIn(orphan.pid, pids)
        self.assertIn(child.pid, pids)
        watch.tracked[orphan.pid] = {**row, "args": "a different program"}  # pid reuse
        self.assertNotIn(orphan.pid, {row["pid"] for row in watch._snapshot()})

    def test_sigterm_forwards_records_interrupted_and_releases_the_lock(self) -> None:
        runs = self.hazard_root()
        configs = self.configs("hz-hang-term", "hz-never")
        driver = self.base / "driver.py"
        driver.write_text(self.DRIVER.format(root=str(ROOT)))
        argv = [sys.executable, str(driver), str(configs), "--runs-dir", str(runs),
                "--campaign-policy", str(TEST_POLICY),
                "--cli-cmd", shlex.join([sys.executable, str(self.cli)]), "--max-failures", "10"]
        stage = subprocess.Popen(argv, cwd=ROOT, env=dict(os.environ), stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        # The stage starts a member that starts a 30 s sleeper. If the member never reports
        # ready, the assertion below fails with all three still running: stop the stage and
        # everything it started (tree=True lists the stage's descendants before it is signalled).
        child_guard.own(self, stage, tree=True)
        ready = self.marker(runs, "hz-hang-term", "ready")
        deadline = time.monotonic() + 60
        while not ready.exists() and time.monotonic() < deadline and stage.poll() is None:
            time.sleep(0.05)
        self.assertTrue(ready.exists(), "member never started")
        stage.send_signal(signal.SIGTERM)
        try:
            out, err = stage.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            stage.kill()
            out, err = stage.communicate()
            self.fail("stage did not exit after SIGTERM")
        self.assertEqual(stage.returncode, 143, err.decode())
        self.assertTrue(self.marker(runs, "hz-hang-term", "term").exists())
        grandchild = int(self.marker(runs, "hz-hang-term", "grandchild").read_text())
        self.assertTrue(_gone_within(grandchild, 5.0))
        self.assertFalse((runs / "campaign.lock").exists())
        stops = [row for row in self.log_rows(runs) if row.get("record_type") == "campaign_stop"]
        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0]["status"], "interrupted")
        self.assertEqual(stops[0]["interrupted_run_id"], "hz-hang-term")
        self.assertEqual(stops[0]["exit_code"], 143)
        self.assertEqual(self.invoked(runs), ["hz-hang-term"])


class ChildStderrTests(_P2Stage):
    """Yield E."""

    def stderr_file(self, run_id: str) -> Path:
        found = sorted((self.custody / "operator-logs" / "member-stderr").glob(f"*--{run_id}.stderr"))
        self.assertEqual(len(found), 1, found)
        return found[0]

    def test_failed_member_records_a_redacted_child_refusal(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-refuse-1", "hz-e-ok"), runs)
        self.assertEqual(result.code, 1, result.err)
        row = self.row_for(runs, "hz-refuse-1")
        self.assertEqual(row["child_refusal"], "error: idle admission refused member # at #.## W")
        path = self.stderr_file("hz-refuse-1")
        self.assertEqual(row["child_stderr"], str(path))
        self.assertIn(b"refused member 7 at 0.25 W", path.read_bytes())
        # Copied into the stage log (this process's stderr).
        self.assertIn("error: idle admission refused member 7 at 0.25 W", result.err)
        ok = self.row_for(runs, "hz-e-ok")
        self.assertNotIn("child_refusal", ok)
        self.assertEqual(ok["child_stderr"], str(self.stderr_file("hz-e-ok")))

    def test_lineage_refusal_is_named_by_its_reason_code(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-lineage-1"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.row_for(runs, "hz-lineage-1")["child_refusal"],
                         "launch_consumption_missing")

    def test_child_refusal_helper(self) -> None:
        refusal = run_campaign._hazard_child_refusal
        self.assertIsNone(refusal(b""))
        self.assertIsNone(refusal(b"\n   \n"))
        self.assertEqual(refusal(b"a 12\nerror: x 3.5\n\n"), "error: x #.#")
        self.assertEqual(len(refusal(b"y" * 1000)), 300)

    def test_legacy_root_keeps_inherited_stderr(self) -> None:
        runs = self.plain_root()
        result = self.run_stage(self.configs("pl-refuse-1"), runs)
        self.assertEqual(result.code, 1, result.err)
        row = self.row_for(runs, "pl-refuse-1")
        self.assertNotIn("child_refusal", row)
        self.assertNotIn("child_stderr", row)
        self.assertFalse((self.custody / "operator-logs").exists())


class BatteryThermistorTests(_P2Stage):
    """The thermistor reading at each cooldown release (timing ruling 2026-10-06)."""

    def test_each_member_gets_one_reading_in_the_manifest(self) -> None:
        runs = self.hazard_root()
        result = self.run_stage(self.configs("hz-temp-a", "hz-temp-b"), runs)
        self.assertEqual(result.code, 0, result.err)
        readings = [reading for manifest in self.manifests(runs)
                    for reading in manifest.get("battery_temperature_readings", [])]
        self.assertEqual([reading["following_run_id"] for reading in readings],
                         ["hz-temp-a", "hz-temp-b"])
        for reading in readings:
            self.assertEqual(reading["temperature_centi_c"], 3035)
            self.assertEqual(reading["temperature_c"], 30.35)
            self.assertIsNone(reading["error"])
            self.assertEqual(reading["schema_version"], "joulewise.battery_thermistor_reading.v1")
        self.assertEqual(readings[0]["cooldown_result"], "first_run_exempt")

    def test_an_unreadable_thermistor_is_recorded_and_collection_continues(self) -> None:
        runs = self.hazard_root()
        with patch.object(run_campaign, "BATTERY_TEMPERATURE_COMMAND",
                          (sys.executable, "-c", "raise SystemExit(3)"), create=True):
            result = self.run_stage(self.configs("hz-temp-x"), runs)
        self.assertEqual(result.code, 0, result.err)
        readings = [reading for manifest in self.manifests(runs)
                    for reading in manifest.get("battery_temperature_readings", [])]
        self.assertEqual(len(readings), 1)
        self.assertIsNone(readings[0]["temperature_centi_c"])
        self.assertEqual(readings[0]["error"], "exit 3")

    def test_legacy_root_records_no_reading(self) -> None:
        runs = self.plain_root()
        result = self.run_stage(self.configs("pl-temp-a"), runs)
        self.assertEqual(result.code, 0, result.err)
        for manifest in self.manifests(runs):
            self.assertNotIn("battery_temperature_readings", manifest)


# --- Independent review (Sol 6.1) findings F1-F8 ---------------------------------

class _FakeChild:
    """A Popen stand-in for the watch: a pid that is never a real process here."""

    def __init__(self, pid: int = 990001, returncode: int | None = None) -> None:
        self.pid = pid
        self.returncode = returncode

    def wait(self, timeout: float | None = None) -> int:
        raise subprocess.TimeoutExpired("fake", timeout or 0)


def _row(pid: int, ppid: int, args: str, *, started: str = "Tue Oct  6 10:00:00 2026",
         stat: str = "S", uid: int = 501) -> dict:
    return {"pid": pid, "ppid": ppid, "pgid": 1, "uid": uid, "stat": stat,
            "started": started, "args": args}


class _Kills:
    def __init__(self) -> None:
        self.sent: list[tuple[int, int]] = []

    def __call__(self, pid: int, signum: int) -> None:
        self.sent.append((pid, signum))

    def to(self, pid: int) -> list[int]:
        return [signum for target, signum in self.sent if target == pid]


class ReviewTeardownTests(unittest.TestCase):
    """F3, F4, F7, F8: the watch's process identity, ownership, wrapper rule and grace."""

    def watch(self, child: _FakeChild, grace: float = 1.0):
        return run_campaign._HazardMemberWatch(child, cap_s=60, grace_s=grace)

    def test_f7_sampler_wrapper_gets_term_only_and_descendants_get_kill(self) -> None:
        child = _FakeChild()
        table = [_row(child.pid, os.getpid(), "python3 member.py"),
                 _row(990002, child.pid, "sudo -n /usr/bin/powermetrics -i 100"),
                 _row(990003, 990002, "/usr/bin/powermetrics -i 100", uid=0),
                 _row(990004, child.pid, "python3 helper.py")]
        kills = _Kills()
        watch = self.watch(child)
        with patch.object(run_campaign, "_hazard_process_table", return_value=table), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            watch._terminate(lambda timeout: False)
            self.assertEqual(kills.to(990002), [signal.SIGTERM, signal.SIGTERM])
            self.assertEqual(kills.to(990004), [signal.SIGTERM, signal.SIGKILL])
            self.assertEqual(kills.to(child.pid), [signal.SIGTERM, signal.SIGKILL])
            # The teardown proof keeps the rule for a surviving wrapper.
            kills.sent.clear()
            proof = watch.teardown_proof()
        self.assertNotIn(signal.SIGKILL, kills.to(990002))
        self.assertIn(signal.SIGTERM, kills.to(990002))
        self.assertTrue(any(s["sampler"] for s in proof["survivors"]))

    def test_f4_a_reused_pid_with_the_same_argv_is_not_signalled(self) -> None:
        child = _FakeChild()
        watch = self.watch(child)
        watch.tracked[990005] = _row(990005, 1, "python3 sampler.py", started="Tue Oct  6 10:00:00 2026")
        table = [_row(child.pid, os.getpid(), "python3 member.py"),
                 _row(990005, 1, "python3 sampler.py", started="Tue Oct  6 10:31:07 2026")]
        kills = _Kills()
        with patch.object(run_campaign, "_hazard_process_table", return_value=table), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            pids = {row["pid"] for row in watch._snapshot()}
            proof = watch.teardown_proof()
        self.assertNotIn(990005, pids)
        self.assertNotIn(990005, {row["pid"] for row in proof["survivors"]})
        self.assertEqual(kills.to(990005), [])
        # The same process (same start time) is still tracked and counted.
        table[1] = _row(990005, 1, "python3 sampler.py", started="Tue Oct  6 10:00:00 2026")
        with patch.object(run_campaign, "_hazard_process_table", return_value=table):
            self.assertIn(990005, {row["pid"] for row in watch._snapshot()})

    def test_f3_a_child_gone_before_the_first_snapshot_leaves_the_census_unproven(self) -> None:
        child = _FakeChild()
        kills = _Kills()
        watch = self.watch(child)
        table = [_row(990006, 1, "/usr/bin/powermetrics -i 100", uid=0)]  # reparented orphan
        with patch.object(run_campaign, "_hazard_process_table", return_value=table), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            watch._terminate(lambda timeout: True)
            proof = watch.teardown_proof()
        self.assertIs(proof["ownership_established"], False)
        self.assertIs(proof["census_completed"], False)
        # A zombie child is gone too: its descendants may already be reparented.
        zombie = _FakeChild(990007)
        watch = self.watch(zombie)
        with patch.object(run_campaign, "_hazard_process_table",
                          return_value=[_row(990007, os.getpid(), "python3 m.py", stat="Z")]), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            watch._terminate(lambda timeout: True)
            self.assertIs(watch.teardown_proof()["census_completed"], False)
        # A live child: ownership established, census complete.
        live = _FakeChild(990008)
        watch = self.watch(live)
        with patch.object(run_campaign, "_hazard_process_table",
                          side_effect=[[_row(990008, os.getpid(), "python3 m.py")], []]), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            watch._terminate(lambda timeout: True)
            proof = watch.teardown_proof()
        self.assertIs(proof["ownership_established"], True)
        self.assertIs(proof["census_completed"], True)

    def test_f8_a_descendant_keeps_its_grace_after_the_child_exits(self) -> None:
        child = _FakeChild()
        kills = _Kills()
        tree = [_row(child.pid, os.getpid(), "python3 member.py"),
                _row(990009, child.pid, "python3 writer.py")]
        gone_at = time.monotonic() + 0.4
        def table():
            return [tree[1]] if time.monotonic() < gone_at else []
        watch = self.watch(child, grace=1.5)
        with patch.object(run_campaign, "_hazard_process_table", return_value=tree), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            watch._terminate(lambda timeout: True)  # the child exited within its grace
        child.returncode = 0
        with patch.object(run_campaign, "_hazard_process_table", side_effect=table), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            proof = watch.teardown_proof()
        self.assertEqual(kills.to(990009), [signal.SIGTERM])
        self.assertEqual(proof["survivors"], [])
        self.assertIs(proof["teardown_escalated"], False)

    def test_f8_a_descendant_past_its_grace_is_killed_and_recorded(self) -> None:
        child = _FakeChild()
        kills = _Kills()
        tree = [_row(child.pid, os.getpid(), "python3 member.py"),
                _row(990010, child.pid, "python3 writer.py")]
        watch = self.watch(child, grace=0.6)
        with patch.object(run_campaign, "_hazard_process_table", return_value=tree), \
                patch.object(run_campaign.os, "kill", side_effect=kills):
            watch._terminate(lambda timeout: True)
            child.returncode = 0
            started = time.monotonic()
            watch.teardown_proof()
        self.assertGreaterEqual(time.monotonic() - started, 0.4)
        self.assertEqual(kills.to(990010), [signal.SIGTERM, signal.SIGKILL])
        self.assertIs(watch.teardown_escalated, True)
        self.assertIs(watch.kill_escalated, True)


class ReviewRunnerTests(unittest.TestCase):
    """F1, F2, F5: the member runner's spawn window, interrupted teardown and stderr copy."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        state = patch.dict(run_campaign._HAZARD_SIGNAL_STATE,
                           {"child": None, "run_id": None, "raised": False,
                            "defer": False, "pending": False, "teardown": None})
        state.start()
        self.addCleanup(state.stop)
        for name, value in (("HAZARD_MEMBER_CAP_S", 60.0), ("HAZARD_MEMBER_TERM_GRACE_S", 1.0)):
            patcher = patch.object(run_campaign, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        stderr_path = patch.object(run_campaign, "_hazard_member_stderr_path",
                                   return_value=self.base / "member-stderr" / "s--m.stderr")
        stderr_path.start()
        self.addCleanup(stderr_path.stop)
        self.emitted: list[tuple[str, dict]] = []
        from joulewise.flags import core as flags_core
        emit = patch.object(flags_core, "emit",
                            side_effect=lambda ctx, code, **kw: self.emitted.append((code, kw)) or True)
        emit.start()
        self.addCleanup(emit.stop)

    def run_child(self, code: str):
        return run_campaign._hazard_run_authenticated_campaign_child(
            [sys.executable, "-c", code], env=None, outer_authentication=None,
            bundle_paths=[self.base / "runs" / "m-1"], hazard=object(), absent=[], run_id="m-1")

    def test_f2_sigterm_during_the_spawn_window_still_terminates_the_child(self) -> None:
        real_start = run_campaign._HazardMemberWatch.start
        seen: list = []

        def start(watch):
            seen.append(watch)
            run_campaign._hazard_sigterm_handler(signal.SIGTERM, None)  # arrives mid-setup
            return real_start(watch)

        with patch.object(run_campaign._HazardMemberWatch, "start", start):
            with self.assertRaises(run_campaign._HazardInterrupted):
                self.run_child("import time; time.sleep(30)")
        process = seen[0].process
        self.assertIsNotNone(process.poll(), "child survived a SIGTERM sent during setup")
        self.assertIs(seen[0].interrupted, True)
        self.assertIs(run_campaign._HAZARD_SIGNAL_STATE["defer"], False)
        self.assertEqual(run_campaign._HAZARD_SIGNAL_STATE["run_id"], "m-1")

    def test_f2_sigterm_during_cleanup_unwinds_after_the_cleanup(self) -> None:
        real_finish = run_campaign._HazardMemberWatch.finish

        def finish(watch):
            run_campaign._hazard_sigterm_handler(signal.SIGTERM, None)  # arrives mid-cleanup
            return real_finish(watch)

        with patch.object(run_campaign._HazardMemberWatch, "finish", finish), \
                patch.object(run_campaign, "authenticate_campaign_child_launch_lineage") as auth:
            with self.assertRaises(run_campaign._HazardInterrupted):
                self.run_child("import sys; print('done', file=sys.stderr)")
        auth.assert_not_called()
        self.assertEqual(run_campaign._HAZARD_SIGNAL_STATE["run_id"], "m-1")
        self.assertIs(run_campaign._HAZARD_SIGNAL_STATE["defer"], False)

    def test_f2_no_deferral_outlives_a_normal_member(self) -> None:
        with patch.object(run_campaign, "authenticate_campaign_child_launch_lineage"):
            result, run = self.run_child("pass")
        self.assertEqual(result.returncode, 0)
        self.assertIs(run_campaign._HAZARD_SIGNAL_STATE["defer"], False)
        self.assertIs(run_campaign._HAZARD_SIGNAL_STATE["pending"], False)
        with self.assertRaises(run_campaign._HazardInterrupted):
            run_campaign._hazard_sigterm_handler(signal.SIGTERM, None)

    def test_f5_an_interrupted_member_with_survivors_is_flagged_and_recorded(self) -> None:
        proof = {"census_completed": False, "ownership_established": False,
                 "survivors": [{"pid": 1234, "uid": 0, "program": "powermetrics", "sampler": True}]}
        real_start = run_campaign._HazardMemberWatch.start

        def start(watch):
            run_campaign._hazard_sigterm_handler(signal.SIGTERM, None)
            return real_start(watch)

        with patch.object(run_campaign._HazardMemberWatch, "start", start), \
                patch.object(run_campaign._HazardMemberWatch, "teardown_proof", return_value=proof):
            with self.assertRaises(run_campaign._HazardInterrupted):
                self.run_child("import time; time.sleep(30)")
        teardown = [kw for code, kw in self.emitted if code == "teardown.survivors"]
        self.assertEqual(len(teardown), 1, self.emitted)
        self.assertEqual(teardown[0]["run_id"], "m-1")
        self.assertEqual(teardown[0]["observed"]["phase"], "sigterm")
        self.assertIs(teardown[0]["observed"]["census_completed"], False)
        row = run_campaign._hazard_interrupted_row(run_id="m-1", campaign_provenance_path=None)
        self.assertEqual(row["teardown"], proof)

    def test_f1_an_uncopied_member_stderr_is_flagged(self) -> None:
        def unreadable(path, run_id):
            return b"", {"phase": "read", "error_type": "PermissionError"}

        with patch.object(run_campaign, "_hazard_copy_member_stderr", side_effect=unreadable), \
                patch.object(run_campaign, "authenticate_campaign_child_launch_lineage"):
            result, run = self.run_child("import sys; print('JOULEWISE_UNWRITTEN_FLAG {}', file=sys.stderr)")
        flagged = [kw for code, kw in self.emitted if code == "member.stderr_uncopied"]
        self.assertEqual([kw["run_id"] for kw in flagged], ["m-1"])
        self.assertEqual(flagged[0]["observed"]["phase"], "read")
        self.assertEqual(run.stderr_raw, b"")

    def test_f1_the_copy_reports_read_and_write_failures(self) -> None:
        raw, failure = run_campaign._hazard_copy_member_stderr(self.base / "absent.stderr", "m-1")
        self.assertEqual((raw, failure), (b"", {"phase": "read", "error_type": "FileNotFoundError"}))
        present = self.base / "present.stderr"
        present.write_bytes(b"line\n")

        class Closed:
            def write(self, text):
                raise ValueError("I/O operation on closed file")

            def flush(self):
                raise ValueError("I/O operation on closed file")

        with patch.object(run_campaign.sys, "stderr", Closed()):
            raw, failure = run_campaign._hazard_copy_member_stderr(present, "m-1")
        self.assertEqual(raw, b"line\n")
        self.assertEqual(failure, {"phase": "write", "error_type": "ValueError"})


class ReviewDrainRecoveryTests(unittest.TestCase):
    """F6: a stage that died between the count and the marker still drains the window."""

    def test_persisted_threshold_count_recovers_the_drain_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            custody = Path(directory)
            hazard = type("Hazard", (), {"custody_root": custody})()
            state = custody / "member-timeouts" / "state.json"
            state.parent.mkdir(parents=True)
            state.write_text(json.dumps({"consecutive": 2}))
            with patch.dict(run_campaign._HAZARD_TIMEOUT_MEMORY, {"consecutive": 0}):
                marker = run_campaign._hazard_drain_requested(hazard)
                self.assertEqual(marker, custody / "member-timeouts" / "drain.json")
                self.assertTrue(marker.is_file())
                self.assertIs(json.loads(marker.read_text())["recovered_from_state"], True)
                # The marker persists once an end reference resets the count.
                run_campaign._hazard_note_member_outcome(hazard, timed_out=False, bundle_ids=["end"])
                self.assertEqual(run_campaign._hazard_drain_requested(hazard), marker)
            state.write_text(json.dumps({"consecutive": 1}))
            marker.unlink()
            with patch.dict(run_campaign._HAZARD_TIMEOUT_MEMORY, {"consecutive": 0}):
                self.assertIsNone(run_campaign._hazard_drain_requested(hazard))


# Test hygiene (2026-10-07): a test or class in this module that leaves a child process running
# is reported as failed, and the child is stopped (tests/child_guard.py).
child_guard.guard_test_classes(globals())


if __name__ == "__main__":
    unittest.main()
