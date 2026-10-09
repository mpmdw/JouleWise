"""PLAN2 lane P2-DRV: the HAZARD_PACK driver's round-2 behaviour, end to end.

Each test drives the real driver (``scripts/run_night.py`` HAZARD branch and
``joulewise/b5/driver.py``) through the shared harness of
``tests/test_b5_driver.py``; fakes stand only at hardware and other-lane seams.

Covered: the J4 launch-abandoned reader and its post-first-record re-check
(Sol R3); the in-window census wrapper (row 7); supervision safety and the
chain's pgid as a monitor tree root (row 10); monitor readiness, crash-loop
backoff and the mid-window outage stop (row 11); the interim lineage rule
(row 9); the yield plan, tripwire and terminal record, CHAIN_STOPPED and the
courier text (section 2.2 A-D).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise import arm_retry, night_gate
from joulewise.b5 import driver as b5_driver
from tests.test_b5_driver import FakeArm, Harness, fake_monitor_argv, probe

REPO_ROOT = Path(__file__).resolve().parents[1]
CENSUS = night_gate.AGENT_CENSUS_ARGV


def patch(test: unittest.TestCase, target, name: str, value) -> None:
    patcher = mock.patch.object(target, name, value)
    patcher.start()
    test.addCleanup(patcher.stop)


def flags(harness: Harness, code: str) -> list[dict]:
    return [item for item in harness.flags if item["code"] == code]


def facts(harness: Harness) -> dict:
    return harness.driver.run_courier.call_args.kwargs["report"]["facts"]


# --------------------------------------------------------------------------
# J4: the watchdog's launch-abandoned marker


class LaunchAbandonedTests(unittest.TestCase):
    def test_a_marker_present_at_start_is_a_record_and_nothing_is_written_under_night(self):
        harness = Harness(self, g10=False)
        harness.night.mkdir(parents=True, exist_ok=True)
        marker = harness.night / "launch_abandoned.json"
        marker.write_text(json.dumps({"schema": "joulewise.launch_abandoned.v1", "plan_id": harness.plan.plan_id}))
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        self.assertEqual([], harness.arm.contexts)
        # Any driver record under night/ would re-fence the released span.
        self.assertEqual(["launch_abandoned.json"], sorted(path.name for path in harness.night.iterdir()))
        self.assertIn("abandoned", (harness.custody / "night.log").read_text())

    def test_a_marker_written_after_the_first_record_refuses_before_the_arm(self):
        # Sol R3: the watchdog writes its marker and then re-checks for driver
        # records; the driver writes its first record and then re-checks for
        # the marker. A marker that lands in between is seen here.
        harness = Harness(self, g10=False)
        real = harness.driver._append_census
        seen = {"n": 0}

        def first_record_then_marker(path, probe_result, refusal):
            real(path, probe_result, refusal)
            seen["n"] += 1
            if seen["n"] == 1:
                (Path(path).parent / "launch_abandoned.json").write_text("{}")
        harness.driver._append_census = first_record_then_marker
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        self.assertEqual([], harness.arm.contexts)
        self.assertEqual(0, harness.network.calls)
        result = harness.result()
        self.assertEqual(("REFUSED", b5_driver.REFUSED_LAUNCH_ABANDONED),
                         (result["verdict"], result["aborted_reason"]))
        self.assertEqual("launch_liveness", harness.hazard()["stage_reached"])
        self.assertFalse((harness.night / "chain.started").exists())
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))
        # The watchdog's null-window release accepts this terminal record.
        decision = arm_retry.terminal_window_release(
            result, plan_id=harness.plan.plan_id, receipt_class=harness.plan.receipt_class,
            now_epoch_s=time.time() + 1, chain_started=False, chain_exited=False, courier_sent=True)
        self.assertEqual((True, "null_window"), (decision.allowed, decision.reason))

    def test_the_watchdog_gate_sees_the_reader_in_run_night(self):
        # magistrate_watchdog._launch_marker_honored keys on this literal.
        self.assertIn(b'"launch_abandoned.json"', (REPO_ROOT / "scripts/run_night.py").read_bytes())


# --------------------------------------------------------------------------
# Row 7: the in-window census


class CensusTests(unittest.TestCase):
    def setUp(self):
        patch(self, b5_driver, "CENSUS_RETRY_S", 0.01)

    def harness(self, chain="/bin/sleep 2\nexit 0\n"):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n" + chain)
        harness.driver.CENSUS_INTERVAL_S = 0.05
        return harness

    def test_a_timed_out_probe_is_retried_and_the_chain_goes_on(self):
        harness = self.harness()
        harness.census.responses += [probe(CENSUS), probe(CENSUS), probe(CENSUS, exit_code=124)]
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual("GO", harness.result()["verdict"])
        summary = harness.hazard()["census_supervision"]
        self.assertEqual((0, 1), (summary["unmeasured_censuses"], summary["retried_probes"]))
        self.assertEqual([], flags(harness, "census.unmeasured"))

    def test_unmeasured_censuses_in_a_row_are_flags_and_the_chain_runs_on(self):
        """Audit A3 (2026-10-07). Before: four in a row stopped the chain (night_stopped_census_unmeasured)."""
        harness = self.harness("/bin/sleep 2\nexit 0\n")
        harness.census.responses += [probe(CENSUS), probe(CENSUS)] + [
            probe(CENSUS, exit_code=127) for _ in range(5 * (1 + b5_driver.CENSUS_RETRIES))]
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        result = harness.result()
        self.assertEqual("GO", result["verdict"])
        self.assertNotEqual(b5_driver.STOPPED_CENSUS_UNMEASURED, result.get("aborted_reason"))
        unmeasured = flags(harness, "census.unmeasured")
        self.assertEqual([1, 2, 3, 4, 5], [item["observed"]["consecutive"] for item in unmeasured][:5])
        self.assertTrue(all("stop_after" not in item["observed"] for item in unmeasured))
        self.assertTrue(all(item["interval"]["monotonic_ns"] for item in unmeasured))
        self.assertFalse((harness.night / "refusal.json").exists())
        self.assertTrue((harness.night / "chain.exited").exists())

    def test_output_with_a_timeout_exit_is_still_an_agent(self):
        harness = self.harness("/bin/sleep 30\n")
        harness.census.responses += [probe(CENSUS), probe(CENSUS),
                                     probe(CENSUS, exit_code=124, stdout="77 claude\n")]
        self.assertEqual(harness.driver.EXIT_ABORTED, harness.run())
        self.assertEqual("night_aborted_agent_present", harness.result()["aborted_reason"])

    def test_a_census_journal_write_fault_is_a_flag_and_never_ends_supervision(self):
        harness = self.harness()
        real = harness.driver._append_census
        calls = {"n": 0}

        def failing_after_the_first(path, probe_result, refusal):
            calls["n"] += 1
            if calls["n"] == 1:
                return real(path, probe_result, refusal)
            raise OSError(5, "Input/output error")
        harness.driver._append_census = failing_after_the_first
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        hazard = harness.hazard()
        self.assertTrue(hazard["chain"]["termination_proven"])
        self.assertEqual("GO", hazard["verdict"])
        self.assertGreaterEqual(hazard["census_supervision"]["journal_failures"], 1)
        self.assertEqual(1, len(flags(harness, "census.journal_write_failed")))
        self.assertTrue((harness.night / "chain.exited").exists())

    def test_classification_reads_the_raw_probe(self):
        classify = b5_driver.HazardCensus.classify
        self.assertEqual("clean", classify(probe(CENSUS)))
        for code in (124, 127, 2, 3, 0, -1):
            self.assertEqual("unmeasured", classify(probe(CENSUS, exit_code=code)), code)
        self.assertEqual("positive", classify(probe(CENSUS, exit_code=1, stdout="5 codex\n")))


# --------------------------------------------------------------------------
# Row 10: supervision safety and the chain as a monitor tree root


class SupervisionTests(unittest.TestCase):
    def test_a_raising_supervision_step_is_flagged_once_and_the_chain_completes(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 3\nexit 0\n")

        def broken(_self):
            raise RuntimeError("statvfs exploded")
        patch(self, b5_driver.DiskFloor, "check", broken)
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        failed = flags(harness, "supervision.pass_failed")
        self.assertEqual(1, len(failed))
        self.assertEqual("disk", failed[0]["observed"]["step"])
        self.assertGreaterEqual(harness.hazard()["supervision_faults"]["disk"], 2)

    def test_the_production_monitor_config_names_the_chain_start_record_as_a_tree_root(self):
        harness = Harness(self, g10=False)
        seams = b5_driver.production_seams(REPO_ROOT)
        request = b5_driver.MonitorRequest(harness.plan, harness.plan_path, harness.custody, harness.night, 4242)
        seams.monitor_argv(request)
        config = json.loads((harness.custody / "hazards/monitor/config.json").read_text())
        self.assertEqual([4242], config["tree_roots"])
        self.assertEqual([str(harness.night / "chain.started")], config["tree_root_files"])


# --------------------------------------------------------------------------
# Row 11: monitor readiness, crash loop, mid-window outage


class FakeProcess:
    _next = 50_000

    def __init__(self, *, exits=True):
        FakeProcess._next += 1
        self.pid = FakeProcess._next
        self.exits = exits

    def poll(self):
        return 3 if self.exits else None


class MonitorTests(unittest.TestCase):
    def test_a_monitor_that_never_journals_refuses_the_window_before_launch(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        harness.monitor_argv = [sys.executable, "-c", "import time; time.sleep(600)"]
        patch(self, b5_driver, "MONITOR_READY_TIMEOUT_S", 0.5)
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        result = harness.result()
        self.assertEqual(("REFUSED", b5_driver.REFUSED_INSTRUMENT_NOT_SAMPLING),
                         (result["verdict"], result["aborted_reason"]))
        self.assertFalse((harness.night / "chain.started").exists())
        hazard = harness.hazard()
        self.assertEqual(b5_driver.MONITOR_READY_TRIES, hazard["monitor"]["starts"])
        self.assertFalse(hazard["monitor_readiness"]["ready"])
        self.assertTrue(hazard["monitor"]["stop"]["proven_stopped"])
        for event in (json.loads(line) for line in
                      (harness.night / b5_driver.MONITOR_JOURNAL).read_text().splitlines()):
            if event.get("pgid"):
                with self.assertRaises(ProcessLookupError):
                    os.killpg(event["pgid"], 0)
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))

    def test_rapid_exits_back_off_flag_a_crash_loop_once_and_never_stop_respawning(self):
        patch(self, b5_driver, "MONITOR_RESTART_INTERVAL_S", 0.0)
        with tempfile.TemporaryDirectory() as directory:
            supervisor = b5_driver.MonitorSupervisor(["monitor"], night_dir=Path(directory),
                                                     popen=lambda *a, **k: FakeProcess())
            loops = []
            supervisor.on_crash_loop = loops.append
            self.assertTrue(supervisor.start())
            for _ in range(20):
                supervisor.poll()
            self.assertTrue(supervisor.crash_loop)
            self.assertEqual(1, len(loops))
            self.assertEqual(b5_driver.MONITOR_BACKOFF_AFTER, supervisor.starts)
            self.assertFalse(supervisor.stopped)
            patch(self, b5_driver, "MONITOR_RESTART_BACKOFF_S", 0.0)
            supervisor.poll()
            self.assertEqual(b5_driver.MONITOR_BACKOFF_AFTER + 1, supervisor.starts)
            self.assertEqual(1, len(loops))
            self.assertTrue(supervisor.summary()["crash_loop"])

    def test_a_monitor_that_stays_up_clears_the_failure_count(self):
        with tempfile.TemporaryDirectory() as directory:
            supervisor = b5_driver.MonitorSupervisor(["monitor"], night_dir=Path(directory),
                                                     popen=lambda *a, **k: FakeProcess(exits=False))
            supervisor.start()
            supervisor.consecutive_failures = 4
            supervisor.started_at = time.monotonic() - b5_driver.MONITOR_RAPID_EXIT_S - 1
            supervisor.poll()
            self.assertEqual(0, supervisor.consecutive_failures)

    def test_a_crash_loop_in_the_window_is_a_fault_in_the_report(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 6\nexit 0\n")
        patch(self, b5_driver, "MONITOR_RESTART_INTERVAL_S", 0.0)
        harness.monitor_argv = lambda request: fake_monitor_argv(request.custody_root, life=0.3, code=3)
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual(1, len(flags(harness, "monitor.crash_loop")))
        report = facts(harness)
        self.assertTrue(report["fault"])
        self.assertIn("monitor_crash_loop", report["fault_reasons"])

    def test_each_monitor_restart_is_the_flag_monitor_restarted(self):
        """Audit-fix batch 1 (item 8). Before: the catalog classified monitor.restarted, and nothing wrote it."""
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 4\nexit 0\n")
        patch(self, b5_driver, "MONITOR_RESTART_INTERVAL_S", 0.0)
        harness.monitor_argv = lambda request: fake_monitor_argv(request.custody_root, life=1.0, code=3)
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        starts = harness.hazard()["monitor"]["starts"]
        self.assertGreaterEqual(starts, 2)
        restarted = flags(harness, "monitor.restarted")
        self.assertEqual(starts - 1, len(restarted))
        first = restarted[0]
        self.assertEqual(("DIAGNOSTIC", "REPRESENTATION", "window"),
                         (first["family"], first["klass"], first["scope"]["level"]))
        self.assertEqual(3, first["observed"]["last_exit"]["returncode"])
        lo, hi = first["interval"]["monotonic_ns"]
        self.assertLessEqual(lo, hi)
        from joulewise.flags.catalog import DRAFT_CODES
        self.assertEqual("DISCLOSE", DRAFT_CODES["monitor.restarted"]["effect"])

    def test_a_silent_monitor_stops_the_chain_like_disk_low(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 8\nexit 0\n")
        patch(self, b5_driver, "MONITOR_OUTAGE_S", 1.0)
        patch(self, b5_driver, "MONITOR_LIVENESS_CHECK_S", 0.1)
        self.assertEqual(harness.driver.EXIT_ABORTED, harness.run())
        result = harness.result()
        self.assertEqual(("ABORTED", b5_driver.STOPPED_MONITOR_OUTAGE), (result["verdict"], result["aborted_reason"]))
        outage = flags(harness, "monitor.outage")
        self.assertEqual(1, len(outage))
        self.assertEqual({"battery", "contention"}, set(outage[0]["observed"]["silent_s"]))
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))
        self.assertTrue((harness.night / "chain.exited").exists())

    def test_liveness_reads_only_new_error_free_lines(self):
        patch(self, b5_driver, "MONITOR_OUTAGE_S", 5.0)
        patch(self, b5_driver, "MONITOR_LIVENESS_CHECK_S", 0.0)
        now = {"t": 100.0}
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            liveness = b5_driver.MonitorLiveness(directory, clock=lambda: now["t"])

            def write(name, kind, error=None):
                with (directory / f"{name}.jsonl").open("a") as handle:
                    handle.write(json.dumps({"kind": kind, "error": error}) + "\n")
            now["t"] = 104.0
            write("battery", "reading")
            write("contention", "interval", error="ps timed out")
            self.assertIsNone(liveness.check())
            now["t"] = 106.0
            self.assertEqual({"contention": 6.0}, liveness.check()["silent_s"])
            write("contention", "snapshot")
            now["t"] = 108.0
            self.assertIsNone(liveness.check())


# --------------------------------------------------------------------------
# Row 9 (interim): lineage


class LineageTests(unittest.TestCase):
    # Doctrine 2026-10-05 (int4): an unpublished or absent locator is a flag
    # after one retry of publication, never a refusal; the chain launches.
    def test_an_absent_locator_after_one_retry_is_a_flag_and_the_chain_launches(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        patch(self, b5_driver, "LINEAGE_RETRY_S", 0.0)
        calls = []

        def broken(request):
            calls.append(request)
            raise RuntimeError("window_lineage unavailable")
        harness.publish_lineage = broken
        harness.lineage_valid = False
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual(2, len(calls))
        self.assertEqual("GO", harness.result()["verdict"])
        self.assertTrue((harness.night / "chain.started").exists())
        codes = [item["code"] for item in harness.flags]
        self.assertIn("records.lineage_formality", codes)
        self.assertIn(b5_driver.LINEAGE_PRELAUNCH_MISMATCH, codes)
        mismatch = next(item for item in harness.flags if item["code"] == b5_driver.LINEAGE_PRELAUNCH_MISMATCH)
        self.assertEqual({"claim", "bound", "science_members_expected_to_refuse"}, set(mismatch["observed"]))
        self.assertEqual(harness.plan.hazard_window["pack"]["pack_plan_id"], mismatch["expected"]["plan_id"])
        self.assertFalse((harness.night / "refusal.json").exists())
        # Audit A5: with no readable locator, the members of both roots take the
        # legacy path and refuse (launch_consumption_missing); both flags say so.
        formality = next(item for item in harness.flags if item["code"] == "records.lineage_formality")
        for flag in (mismatch, formality):
            self.assertEqual(["bound", "claim"], flag["observed"]["science_members_expected_to_refuse"])

    def test_a5_an_unusable_pack_inventory_refuses_before_launch(self):
        """Audit A5 (2026-10-07). Before: flagged and launched; every tagged member then refused."""
        from joulewise import window_lineage
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        patch(self, b5_driver, "LINEAGE_RETRY_S", 0.0)
        calls = []

        def unusable(request):
            calls.append(request)
            raise window_lineage.PackInventoryUnusableError(
                "pack inventory is unusable: plan_tree.json: [Errno 2] No such file or directory")
        harness.publish_lineage = unusable
        harness.lineage_valid = False
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        self.assertEqual(2, len(calls))
        result = harness.result()
        self.assertEqual(("REFUSED", b5_driver.REFUSED_PACK_INVENTORY_UNUSABLE),
                         (result["verdict"], result["aborted_reason"]))
        self.assertEqual("lineage_pack_inventory", harness.hazard()["stage_reached"])
        self.assertFalse((harness.night / "chain.started").exists())
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))
        self.assertEqual(2, refusal["refusal"]["evidence"]["attempts"])

    def test_a5_the_refusal_keys_on_the_exception_type_not_its_message(self):
        """Cold pass 2 N6: before, a reworded message turned the refusal into a hollow launch, and a
        base-class error carrying the message refused."""
        from joulewise import window_lineage
        for error, refused in ((window_lineage.PackInventoryUnusableError("config inventory unreadable: x"), True),
                               (window_lineage.LineagePublicationError("pack inventory is unusable: x"), False)):
            with self.subTest(error=repr(error)):
                harness = Harness(self, g10=False)
                harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
                patch(self, b5_driver, "LINEAGE_RETRY_S", 0.0)

                def failing(request, error=error):
                    raise error
                harness.publish_lineage = failing
                harness.lineage_valid = False
                code = harness.run()
                if refused:
                    self.assertEqual(harness.driver.EXIT_REFUSED, code)
                    self.assertEqual(b5_driver.REFUSED_PACK_INVENTORY_UNUSABLE, harness.result()["aborted_reason"])
                else:
                    self.assertNotEqual(b5_driver.REFUSED_PACK_INVENTORY_UNUSABLE,
                                        harness.result().get("aborted_reason"))

    def test_a5_any_other_publication_failure_still_launches(self):
        from joulewise import window_lineage
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        patch(self, b5_driver, "LINEAGE_RETRY_S", 0.0)

        def unwritable(request):
            raise window_lineage.LineagePublicationError("locator could not be written: [Errno 13] Permission denied")
        harness.publish_lineage = unwritable
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertTrue((harness.night / "chain.started").exists())
        formality = next(item for item in harness.flags if item["code"] == "records.lineage_formality")
        self.assertEqual([], formality["observed"]["science_members_expected_to_refuse"])  # the locators read valid

    def test_a_locator_absent_after_a_successful_publication_is_republished_once(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        patch(self, b5_driver, "LINEAGE_RETRY_S", 0.0)
        published, checks = [], []

        def publish(request):
            published.append(request)
            return {"ok": True}

        def verify(request):
            checks.append(request)
            absent = len(published) < 2
            return {role: {"valid": not absent, "locator_absent": absent} for role in ("claim", "bound")}
        harness.publish_lineage = publish
        harness.verify_lineage = verify
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertEqual((2, 2), (len(published), len(checks)))
        self.assertNotIn(b5_driver.LINEAGE_PRELAUNCH_MISMATCH, [item["code"] for item in harness.flags])
        record = json.loads((harness.night / b5_driver.LINEAGE_RECORD).read_text())
        self.assertTrue(record["locators_valid"])

    def test_a_bookkeeping_mismatch_is_a_flag_and_the_chain_launches(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        mismatches = {"plan_id": {"observed": "plan-of-another-window", "expected": "the-pack-plan"}}
        harness.verify_lineage = lambda request: {
            role: {"valid": False, "boot_changed": False, "mismatches": mismatches,
                   "error": "the locator names plan_id 'plan-of-another-window'"} for role in ("claim", "bound")}
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        self.assertTrue((harness.night / "chain.started").exists())
        flag = next(item for item in harness.flags if item["code"] == b5_driver.LINEAGE_PRELAUNCH_MISMATCH)
        self.assertEqual(("RECORDS", "REPRESENTATION"), (flag["family"], flag["klass"]))
        self.assertEqual(mismatches, flag["observed"]["claim"]["mismatches"])
        self.assertEqual(["night/" + b5_driver.LINEAGE_RECORD], [item["path"] for item in flag["evidence"]])
        from joulewise.flags.catalog import DRAFT_CODES
        self.assertEqual("DISCLOSE", DRAFT_CODES[b5_driver.LINEAGE_PRELAUNCH_MISMATCH]["effect"])
        record = json.loads((harness.night / b5_driver.LINEAGE_RECORD).read_text())
        self.assertEqual((False, []), (record["locators_valid"], record["boot_changed"]))

    def test_a_boot_changed_since_publication_refuses_before_launch(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        recorded, current = "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"
        harness.verify_lineage = lambda request: {
            role: {"valid": False, "boot_changed": True, "recorded_boot_session_id": recorded,
                   "current_boot_session_id": current, "error": "collection boot differs"}
            for role in ("claim", "bound")}
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        result = harness.result()
        self.assertEqual(("REFUSED", b5_driver.REFUSED_BOOT_CHANGED), (result["verdict"], result["aborted_reason"]))
        self.assertFalse((harness.night / "chain.started").exists())
        self.assertFalse((harness.night / b5_driver.MONITOR_JOURNAL).exists())
        refusal = json.loads((harness.night / "refusal.json").read_text())
        self.assertEqual([], harness.driver.validate_refusal(refusal))
        self.assertEqual(["bound", "claim"], refusal["refusal"]["evidence"]["roots"])
        self.assertEqual({"recorded": recorded, "current": current}, refusal["refusal"]["evidence"]["boots"]["claim"])

    def test_the_production_check_reads_both_locators(self):
        with tempfile.TemporaryDirectory() as directory:
            claim, bound = Path(directory, "claim"), Path(directory, "bound")
            claim.mkdir()
            bound.mkdir()
            request = b5_driver.LineageRequest(None, Path(directory), Path(directory), Path(directory), {},
                                               claim, bound, None, None, None)
            checks = b5_driver._production_lineage_check(request)
            self.assertEqual({"claim", "bound"}, set(checks))
            self.assertFalse(checks["claim"]["valid"] or checks["bound"]["valid"])
            self.assertIn("hazard locator is absent", checks["claim"]["error"])


# --------------------------------------------------------------------------
# Section 2.2: yield


def stage_yield(harness: Harness) -> list[dict]:
    return [json.loads(line) for line in (harness.night / b5_driver.STAGE_YIELD).read_text().splitlines()]


class YieldTests(unittest.TestCase):
    def test_a_full_alpha_window_reports_125_of_125(self):
        harness = Harness(self, "alpha", g10=False)
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        record = harness.hazard()["yield"]
        # The fake checkout writes bundles but no campaign_log.jsonl, so 0 rows
        # are logged here; SolReviewFixTests covers the logged counts.
        self.assertEqual(("FULL", 125, 125, 125, 0, 0),
                         (record["yield_status"], record["planned"], record["bundles_present"],
                          record["succeeded"], record["logged"], record["failed"]))
        rows = stage_yield(harness)
        self.assertEqual(10, len(rows))
        self.assertTrue(all(row["status"] == "OK" for row in rows))
        plan = json.loads((harness.night / b5_driver.YIELD_PLAN).read_text())
        minimums = {row["stage_id"]: (row["role"], row["planned"], row["min_valid"]) for row in plan["stages"]}
        self.assertEqual(("corpus", 18, 10), minimums["alpha-bound-collection"])
        # NEG-8 ruling 2026-10-07: two survivors at each endpoint; the midpoint is not required.
        self.assertEqual(("reference", 3, 2), minimums["alpha-reference-start"])
        self.assertEqual(("reference", 3, 2), minimums["alpha-reference-end"])
        self.assertEqual(("reference_midpoint", 1, 0), minimums["alpha-reference-midpoint"])
        self.assertEqual(("science", 20, 16), minimums["alpha-science-abba-01-05"])
        self.assertEqual(("science", 10, 8), minimums["alpha-science-absolute"])
        report = facts(harness)
        self.assertTrue(report["yield_line"].startswith("collected 125 of 125 planned members"))
        self.assertFalse(report["fault"])
        # Counts only: the published records never carry member identities.
        published = (harness.night / b5_driver.HAZARD_RESULT).read_text() + (
            harness.night / b5_driver.STAGE_YIELD).read_text()
        self.assertNotIn("neg8-refcorpus-r01", published)
        self.assertNotIn("duration_s", published)

    def test_gamma_plans_a_run_id_once_per_runs_root(self):
        # Lane L10 (int4): the committed GAMMA pack plans cleanly at the desk and
        # each interior reference stage launches its own member.
        harness = Harness(self, "gamma", g10=False)
        plan = b5_driver.yield_plan(harness.plan)
        midpoints = [row for row in plan["stages"] if "midpoint" in row["stage_id"] or "arm-boundary" in row["stage_id"]]
        self.assertEqual([1, 1, 1], [row["planned"] for row in midpoints])
        self.assertEqual([1, 1, 1], [row["listed"] for row in midpoints])
        self.assertEqual((107, 107), (sum(row["listed"] for row in plan["stages"]), plan["planned"]))
        # The driver's own netting of a duplicate still holds: GAMMA's pre-L10
        # shape (all three stages launching neg8-window-midpoint into one root)
        # is synthesized at the dispatch reader, after the desk has planned.
        real = b5_driver._local_stage_dispatch
        shared = "neg8-window-midpoint"

        def pre_l10(stage, **keywords):
            runs_root, run_ids, roles = real(stage, **keywords)
            if stage.stage_id in ("gamma-reference-decode-midpoint", "gamma-reference-prefill-midpoint"):
                return runs_root, [shared], roles
            return runs_root, run_ids, roles

        with mock.patch.object(b5_driver, "_local_stage_dispatch", side_effect=pre_l10):
            plan = b5_driver.yield_plan(harness.plan)
        midpoints = [row for row in plan["stages"] if "midpoint" in row["stage_id"] or "arm-boundary" in row["stage_id"]]
        self.assertEqual([[shared], [], []], [row["run_ids"] for row in midpoints])
        self.assertEqual([1, 0, 0], [row["planned"] for row in midpoints])
        self.assertEqual([1, 1, 1], [row["listed"] for row in midpoints])
        # 107 listed positions; the two repeated midpoint positions are never
        # measured (run_campaign skips a complete bundle; PLAN2 row 14).
        self.assertEqual((107, 105), (sum(row["listed"] for row in plan["stages"]), plan["planned"]))

    def test_an_empty_window_is_go_with_exit_5_and_a_fault(self):
        harness = Harness(self, "alpha", g10=False)
        ids = [row["stage_id"] for row in b5_driver.yield_plan(harness.plan)["stages"]]
        journal = "".join(
            f"print -r -- '{{\"stage_id\":\"{stage}\",\"kind\":\"campaign_collection\",\"rc\":1,"
            f"\"started_epoch_s\":0,\"ended_epoch_s\":0}}' >> \"$NIGHT_DIR/chain-stages.jsonl\"\n"
            for stage in ids)
        harness.replace_chain("#!/bin/zsh -f\n" + journal + "/bin/sleep 2\nexit 0\n", keep_yield_plan=True)
        self.assertEqual(harness.driver.EXIT_CHAIN_FAILED, harness.run())
        self.assertEqual("GO", harness.result()["verdict"])
        self.assertEqual("EMPTY", harness.hazard()["yield"]["yield_status"])
        rows = stage_yield(harness)
        self.assertEqual(ids, [row["stage_id"] for row in rows])
        self.assertTrue(all(row["status"] == "ZERO" for row in rows))
        self.assertEqual(10, len(flags(harness, "yield.stage_zero")))
        alerts = sorted(path.name for path in harness.night.glob("yield_alert-*.json"))
        self.assertEqual(10, len(alerts))
        report = facts(harness)
        self.assertTrue(report["fault"])
        self.assertIn("yield_empty", report["fault_reasons"])
        self.assertTrue(report["yield_line"].startswith("collected 0 of 125 planned members"))

    def test_a_low_science_stage_is_flagged_and_the_window_stays_go(self):
        order = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/"
                                        "05_phase_prefill_p2048_abba_blocks_01_05/order_manifest.json").read_text())
        victims = [row["run_id"] for row in order["executed_order"][:5]]
        harness = Harness(self, "alpha", g10=False, behavior={"fail_run_ids": victims})
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        low = flags(harness, "yield.stage_low")
        self.assertEqual(["alpha-science-prefill-p2048-abba-01-05"], [item["observed"]["stage_id"] for item in low])
        self.assertEqual((20, 15, 16), tuple(low[0]["observed"][key] for key in ("present", "succeeded", "min_valid")))
        self.assertEqual("LOW", harness.hazard()["yield"]["yield_status"])
        self.assertIn("yield_low", facts(harness)["fault_reasons"])

    def test_three_members_refused_before_their_bundles_for_one_cause_are_flagged(self):
        harness = Harness(self, "alpha", g10=False)
        claim = harness.plan.hazard_window["runs_roots"]["claim"]
        rows = "".join(
            f"print -r -- '{{\"run_id\":\"neg8-window-start-r{index}\",\"status\":\"failed\",\"exit_code\":3,"
            f"\"duration_s\":1.5,\"child_refusal\":\"error: refused at 12:04\"}}' >> {claim}/campaign_log.jsonl\n"
            for index in (1, 2, 3))
        harness.replace_chain("#!/bin/zsh -f\n" + rows + "/bin/sleep 1\nexit 0\n", keep_yield_plan=True)
        harness.run()
        found = flags(harness, "stage.members_refused_pre_bundle_identical")
        self.assertEqual(1, len(found))
        observed = found[0]["observed"]
        self.assertEqual((3, "child_refusal"), (observed["consecutive"], observed["cause_kind"]))
        self.assertEqual(hashlib.sha256(b"error: refused at ##:##").hexdigest(), observed["cause_sha256"])
        self.assertNotIn("refused at", json.dumps(found[0]))

    def test_a_stalled_window_is_flagged_once(self):
        harness = Harness(self, "alpha", g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 2\nexit 0\n", keep_yield_plan=True)
        patch(self, b5_driver, "YIELD_STALL_S", 0.3)
        patch(self, b5_driver, "YIELD_STALL_CHECK_S", 0.1)
        harness.run()
        self.assertEqual(1, len(flags(harness, "yield.stage_stalled")))

    def test_a_chain_stop_is_chain_stopped_not_go(self):
        harness = Harness(self, "alpha", g10=False, behavior={"reservation_rc": 1})
        self.assertEqual(harness.driver.EXIT_CHAIN_FAILED, harness.run())
        result = harness.result()
        self.assertEqual(("CHAIN_STOPPED", 10), (result["verdict"], result["chain_exit_code"]))
        hazard = harness.hazard()
        self.assertEqual(("CHAIN_STOPPED", "chain:reservation_failed"), (hazard["verdict"], hazard["stage_reached"]))
        self.assertEqual("EMPTY", hazard["yield"]["yield_status"])
        report = facts(harness)
        self.assertEqual(["yield_empty", "chain_stopped:reservation_failed"], report["fault_reasons"][:2])
        decision = arm_retry.terminal_window_release(
            result, plan_id=harness.plan.plan_id, receipt_class=harness.plan.receipt_class,
            now_epoch_s=time.time() + 1, chain_started=True, chain_exited=True, courier_sent=True)
        self.assertEqual((True, "chain_stopped"), (decision.allowed, decision.reason))

    def test_a_failed_post_calibration_is_its_own_fault_not_empty(self):
        harness = Harness(self, "alpha", g10=False, behavior={"capture_rc": {"post": 1}})
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        report = facts(harness)
        self.assertIs(True, report["post_bracket_failed"])
        self.assertIs(False, report["bound_derivation_failed"])
        self.assertEqual(["post_bracket_failed"], report["fault_reasons"])
        self.assertEqual("FULL", report["yield_status"])

    def test_the_courier_leads_with_the_yield_and_cites_the_blinding_rule(self):
        harness = Harness(self, g10=False)
        with tempfile.NamedTemporaryFile() as lock:
            report = {"facts": {"plan_id": harness.plan.plan_id, "yield_line": "collected 3 of 125 planned members",
                                "fault": True, "fault_reasons": ["yield_low"]},
                      "diagnostics": [], "result_unavailable": False, "base_exit_code": 0, "prepared": True}
            argv = harness.driver._courier_prelaunch(harness.custody, harness.plan, harness.courier,
                                                     os.open(lock.name, os.O_RDWR), report)
        prompt = " ".join(str(item) for item in argv)
        self.assertIn("known_chain.yield_line", prompt)
        self.assertIn("FAULT", prompt)
        self.assertIn("registration section 8, item 2", prompt)
        self.assertNotIn("section 9.2", prompt)
        self.assertIn("collected 3 of 125 planned members", prompt)

    def test_stage_counts_are_published_and_the_yield_plan_is_not(self):
        driver = Harness(self, g10=False).driver
        self.assertIn("stage_yield.jsonl", driver.HAZARD_ARTIFACTS)
        self.assertNotIn("yield_plan.json", driver.HAZARD_ARTIFACTS)


# --------------------------------------------------------------------------
# Sol 6.1 review of P2-DRV (findings F1-F7)


class _RecordingWindow:
    def __init__(self):
        self.flagged = []
        self.plan = mock.Mock(plan_id="plan-test")

    def flag(self, code, *args, **keywords):
        self.flagged.append(code)


class SolReviewFixTests(unittest.TestCase):
    # F1: a failed physics evaluation is never "no outage".
    def test_a_malformed_liveness_line_is_not_a_reading_and_runs_into_the_outage_bound(self):
        patch(self, b5_driver, "MONITOR_OUTAGE_S", 5.0)
        patch(self, b5_driver, "MONITOR_LIVENESS_CHECK_S", 0.0)
        now = {"t": 100.0}
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            liveness = b5_driver.MonitorLiveness(directory, clock=lambda: now["t"])
            for name in ("battery", "contention"):
                with (directory / f"{name}.jsonl").open("a") as handle:
                    handle.write(json.dumps({"kind": [], "error": None}) + "\n")
                    handle.write(json.dumps({"kind": {"reading": 1}, "error": None}) + "\n")
            now["t"] = 103.0
            self.assertIsNone(liveness.check())
            now["t"] = 106.0
            self.assertEqual({"battery": 6.0, "contention": 6.0}, liveness.check()["silent_s"])

    def test_an_unreadable_liveness_journal_runs_into_the_outage_bound(self):
        patch(self, b5_driver, "MONITOR_OUTAGE_S", 5.0)
        patch(self, b5_driver, "MONITOR_LIVENESS_CHECK_S", 0.0)
        now = {"t": 100.0}
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for name in ("battery", "contention"):
                (directory / f"{name}.jsonl").write_text(json.dumps({"kind": "reading"}) + "\n")
            liveness = b5_driver.MonitorLiveness(directory, clock=lambda: now["t"])
            patch(self, b5_driver.MonitorLiveness, "_read", mock.Mock(side_effect=RuntimeError("EIO")))
            now["t"] = 106.0
            self.assertEqual({"battery", "contention"}, set(liveness.check()["silent_s"]))
            self.assertTrue(liveness.errors)

    def test_a_raising_liveness_evaluation_stops_the_chain_at_the_outage_bound(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 8\nexit 0\n")
        patch(self, b5_driver, "MONITOR_OUTAGE_S", 1.0)
        patch(self, b5_driver.MonitorLiveness, "check", mock.Mock(side_effect=TypeError("unhashable")))
        self.assertEqual(harness.driver.EXIT_ABORTED, harness.run())
        result = harness.result()
        self.assertEqual(("ABORTED", b5_driver.STOPPED_MONITOR_OUTAGE), (result["verdict"], result["aborted_reason"]))
        outage = flags(harness, "monitor.outage")
        self.assertEqual(1, len(outage))
        self.assertTrue(outage[0]["observed"]["unmeasured"])
        self.assertEqual(["monitor_liveness"], [item["observed"]["step"]
                                                for item in flags(harness, "supervision.pass_failed")])
        self.assertIn("supervision_failed:monitor_liveness", facts(harness)["fault_reasons"])

    def test_a_raising_physics_step_makes_the_window_a_fault(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\n/bin/sleep 3\nexit 0\n")
        patch(self, b5_driver.DiskFloor, "check", mock.Mock(side_effect=RuntimeError("statvfs exploded")))
        self.assertEqual(harness.driver.EXIT_GO, harness.run())
        report = facts(harness)
        self.assertTrue(report["fault"])
        self.assertIn("supervision_failed:disk", report["fault_reasons"])
        self.assertIn("supervision_failed:disk", harness.hazard()["faults"]["reasons"])

    # F2: a locator the members' own authenticator rejects is not valid (a
    # flag since int4). The window plan id differs from the pack plan id, as
    # in every real window; the lineage carries the pack plan id.
    def lineage_request(self, w, pack_plan_id):
        from tests import test_window_lineage as lineage_fixture
        window = {"pack": {"pack_plan_id": pack_plan_id, "window_id": lineage_fixture.WINDOW_ID},
                  "bracket_session_id": lineage_fixture.SESSION_ID}
        return b5_driver.LineageRequest(mock.Mock(plan_id="REH-a-window-plan-id"), Path(w.base), w.custody,
                                        w.night, window, w.claim, w.bound, None, None, None)

    def test_a_stale_locator_from_an_ended_window_is_not_valid(self):
        from tests import test_window_lineage as lineage_fixture
        with tempfile.TemporaryDirectory() as directory:
            w = lineage_fixture.build_window(Path(directory))
            request = self.lineage_request(w, lineage_fixture.PLAN_ID)
            fresh = b5_driver._production_lineage_check(request)
            self.assertEqual((True, True), (fresh["claim"]["valid"], fresh["bound"]["valid"]))
            lineage_fixture.write_night_records(w)
            stale = b5_driver._production_lineage_check(request)
            self.assertEqual((False, False), (stale["claim"]["valid"], stale["bound"]["valid"]))
            self.assertIn("already ended", stale["claim"]["error"])

    def test_a_locator_naming_another_plan_is_not_valid(self):
        from tests import test_window_lineage as lineage_fixture
        with tempfile.TemporaryDirectory() as directory:
            w = lineage_fixture.build_window(Path(directory))
            checks = b5_driver._production_lineage_check(self.lineage_request(w, "plan-some-later-window"))
            self.assertEqual((False, False), (checks["claim"]["valid"], checks["bound"]["valid"]))
            self.assertIn("plan-some-later-window", checks["bound"]["error"])
            self.assertEqual({"plan_id": {"observed": lineage_fixture.PLAN_ID, "expected": "plan-some-later-window"}},
                             checks["claim"]["mismatches"])
            self.assertFalse(checks["claim"]["boot_changed"])

    # F3: counting only in the settle after a stage, never into a capture.
    def test_the_last_collection_stage_counts_only_at_the_terminal_record(self):
        harness = Harness(self, "alpha", g10=False)
        rows = b5_driver.yield_plan(harness.plan)["stages"]
        self.assertFalse(rows[-1]["count_in_window"])          # runs into the post-calibration capture
        self.assertTrue(all(row["count_in_window"] for row in rows[:-1]))

    def tripwire(self, night, rows, wall):
        window = _RecordingWindow()
        return window, b5_driver.YieldTripwire(window, night, rows, wall=lambda: wall["t"])

    def test_a_stage_is_counted_in_the_window_only_inside_the_following_settle(self):
        with tempfile.TemporaryDirectory() as directory:
            night, runs = Path(directory, "night"), Path(directory, "runs")
            night.mkdir()
            runs.mkdir()
            rows = [{"stage_id": f"s{index}", "ordinal": index, "role": "science", "runs_root": str(runs),
                     "run_ids": [], "planned": 0, "min_valid": 0, "count_in_window": index != 3}
                    for index in (1, 2, 3)]
            wall = {"t": 10_000.0}
            _window, tripwire = self.tripwire(night, rows, wall)

            def journal(stage_id, ended):
                with (night / "chain-stages.jsonl").open("a") as handle:
                    handle.write(json.dumps({"stage_id": stage_id, "kind": "campaign_collection", "rc": 0,
                                             "started_epoch_s": ended, "ended_epoch_s": ended}) + "\n")
            journal("s1", 9_995)                                     # fresh: inside the settle
            journal("s2", 9_900)                                     # 100 s old: a capture may be running
            journal("s3", 9_999)                                     # fresh, but a capture follows it
            tripwire.poll()
            self.assertEqual(["s1"], sorted(tripwire.counted))
            self.assertEqual(["s1"], [line["stage_id"] for line in stage_yield_lines(night)])
            tripwire.final()
            lines = stage_yield_lines(night)
            self.assertEqual([("s1", "settle"), ("s2", "terminal"), ("s3", "terminal")],
                             [(line["stage_id"], line["counted_at"]) for line in lines])

    def test_the_member_log_is_not_tailed_between_stage_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            night, runs = Path(directory, "night"), Path(directory, "runs")
            night.mkdir()
            runs.mkdir()
            rows = [{"stage_id": "s1", "ordinal": 1, "role": "science", "runs_root": str(runs),
                     "run_ids": ["m1", "m2", "m3"], "planned": 3, "min_valid": 3, "count_in_window": True}]
            window, tripwire = self.tripwire(night, rows, {"t": 10_000.0})
            with (runs / "campaign_log.jsonl").open("a") as handle:
                for run_id in ("m1", "m2", "m3"):
                    handle.write(json.dumps({"run_id": run_id, "status": "failed", "exit_code": 3}) + "\n")
            tripwire.poll()
            self.assertEqual((0, []), (tripwire.attempted, window.flagged))
            tripwire.final()
            self.assertEqual(3, tripwire.attempted)
            self.assertIn("stage.members_refused_pre_bundle_identical", window.flagged)

    # F6: the instrument-not-sampling refusal is a fault.
    def test_an_instrument_not_sampling_refusal_carries_the_fault_facts(self):
        harness = Harness(self, g10=False)
        harness.replace_chain("#!/bin/zsh -f\nexit 0\n")
        harness.monitor_argv = [sys.executable, "-c", "import time; time.sleep(600)"]
        patch(self, b5_driver, "MONITOR_READY_TIMEOUT_S", 0.3)
        self.assertEqual(harness.driver.EXIT_REFUSED, harness.run())
        report = facts(harness)
        self.assertEqual((True, ["instrument_not_sampling"]), (report["fault"], report["fault_reasons"]))
        self.assertEqual(["instrument_not_sampling"], harness.hazard()["faults"]["reasons"])

    # F7: the terminal record's logged, ok and failed counts.
    def test_the_terminal_yield_counts_the_campaign_log(self):
        with tempfile.TemporaryDirectory() as directory:
            night, runs = Path(directory, "night"), Path(directory, "runs")
            night.mkdir()
            (runs / "m1").mkdir(parents=True)
            (runs / "m1" / "summary_metrics.json").write_text(json.dumps({"status": "succeeded"}))
            with (runs / "campaign_log.jsonl").open("w") as handle:
                handle.write(json.dumps({"run_id": "m1", "status": "succeeded"}) + "\n")
                handle.write(json.dumps({"run_id": "m2", "status": "failed"}) + "\n")
                handle.write(json.dumps({"run_id": "other", "status": "failed"}) + "\n")
            rows = [{"stage_id": "s1", "ordinal": 1, "role": "science", "runs_root": str(runs),
                     "run_ids": ["m1", "m2", "m3"], "planned": 3, "min_valid": 3}]
            record = b5_driver.terminal_yield(night, rows)
            self.assertEqual((3, 2, 1, 1, 1, 1, "LOW"),
                             tuple(record[key] for key in ("planned", "logged", "ok", "failed", "bundles_present",
                                                           "succeeded", "yield_status")))


def stage_yield_lines(night: Path) -> list[dict]:
    return [json.loads(line) for line in (night / b5_driver.STAGE_YIELD).read_text().splitlines()]


if __name__ == "__main__":
    unittest.main()
