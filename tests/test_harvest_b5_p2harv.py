"""Gate-prune round 2, lane P2-HARV: the block-5 harvest side of PLAN2.

Built on the synthetic window of ``tests/test_harvest_b5_window.py`` (real
strict validation, re-reduction and replays; fakes only at the named seams).

* Row 1: the desk whole-window verdict writer gets max(1,800 s, 90 s per
  claim-root bundle), a heartbeat, its own session (a timeout kills its whole
  process group, proven gone), and ``campaign.lock`` is removed only when it
  is the dead child's own; the writer runs concurrently with the member
  assessment.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.b5 import harvest as h
from tests import test_harvest_b5_window as base

ROOT = base.ROOT
EXCLUSIONS = base.EXCLUSIONS


def setUpModule():  # noqa: N802 (unittest hook)
    # The shared member template may have been removed by the other module's teardown.
    if base._TEMPLATE is not None and not base._TEMPLATE.exists():
        base._TEMPLATE = None


def tearDownModule():  # noqa: N802 (unittest hook)
    base.tearDownModule()
    base._TEMPLATE = None


def _no_synchronous_runner(argv, **kwargs):
    """The desk writer must not run through the blocking ``runner`` seam."""
    if "--whole-window-verdict" in argv:
        raise AssertionError("the desk verdict ran through the synchronous runner")
    raise AssertionError(f"unexpected runner call: {argv[:3]}")


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# A desk writer that takes its own campaign.lock (the runner's format), leaves
# a grandchild in its process group, ignores SIGTERM and never finishes.
_HUNG_WRITER = textwrap.dedent("""
    import json, os, signal, subprocess, sys, time
    from joulewise.measurement_liveness import observe_identity
    runs, pidfile = sys.argv[1], sys.argv[2]
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    identity = observe_identity(os.getpid())
    with open(os.path.join(runs, "campaign.lock"), "w") as handle:
        handle.write(f"pid={os.getpid()} nonce=n created_at=t start_time={json.dumps(identity.start_time)}\\n")
    grandchild = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])
    with open(pidfile, "w") as handle:
        handle.write(json.dumps({"child": os.getpid(), "grandchild": grandchild.pid}))
    print("writer started", flush=True)
    time.sleep(600)
""")


class DeskVerdictBudgetTests(base.WindowTestCase):
    """Row 1: the 1,800 s kill lost every block-5 verdict (ALPHA needs about 3,700 s)."""

    def test_the_budget_is_ninety_seconds_per_claim_root_bundle_with_a_1800_s_floor(self):
        self.assertEqual(h.desk_verdict_timeout_s(107), 9630.0)  # ALPHA's claim root
        self.assertEqual(h.desk_verdict_timeout_s(20), 1800.0)
        self.assertEqual(h.desk_verdict_timeout_s(0), 1800.0)

    def test_the_writer_gets_the_budget_of_the_bundles_it_validates(self):
        window = self.window(prefix_ledger=True)
        asked = []

        def runner(argv, **kwargs):
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        def timeout(bundles):
            asked.append(bundles)
            return h.desk_verdict_timeout_s(bundles)

        seams = base.desk_seams(runner, runner=_no_synchronous_runner, desk_timeout_s=timeout)
        window.harvest(seams=seams, prepare_desk=True, run_g3=False)
        # Six member bundles; the two calibration captures under instrument_validation are not bundles.
        self.assertEqual(asked, [len(base.MEMBERS)])
        run = json.loads((window.archive / "withheld" / "desk-verdict-run.json").read_bytes())
        self.assertEqual((run["bundles"], run["timeout_s"], run["timed_out"], run["returncode"]),
                         (len(base.MEMBERS), 1800.0, False, 1))
        self.assertNotIn("whole_window.producer_failed", window.codes())


class DeskVerdictTeardownTests(base.WindowTestCase):
    """Row 1: on its budget the writer's whole group is killed and proven gone; only its own lock goes."""

    def test_a_writer_over_budget_is_killed_with_its_group_and_its_own_lock_is_removed(self):
        window = self.window(prefix_ledger=True)
        scratch = Path(tempfile.mkdtemp(prefix="b5-desk-hung-", dir=base.REAL_TMP))
        self.addCleanup(lambda: __import__("shutil").rmtree(scratch, ignore_errors=True))
        script, pidfile = scratch / "writer.py", scratch / "pids.json"
        script.write_text(_HUNG_WRITER)
        spawned = []

        def popen(argv, **kwargs):
            self.assertIs(kwargs.get("start_new_session"), True)
            runs = argv[argv.index("--runs-dir") + 1]
            process = subprocess.Popen([sys.executable, "-B", str(script), runs, str(pidfile)],
                                       env={**os.environ, "PYTHONPATH": str(ROOT)}, **kwargs)
            spawned.append(process)
            return process

        def cleanup():
            for name in ("child", "grandchild"):
                try:
                    os.kill(json.loads(pidfile.read_text())[name], signal.SIGKILL)
                except (OSError, ValueError, KeyError):
                    pass
        self.addCleanup(cleanup)
        seams = h.Seams(group_alive=h.group_alive, exclusions_compute=EXCLUSIONS, runner=_no_synchronous_runner,
                        desk_popen=popen, desk_timeout_s=lambda bundles: 4.0, desk_heartbeat_s=0.5,
                        desk_term_grace_s=0.5, desk_gone_wait_s=10.0)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            window.harvest(seams=seams, prepare_desk=True, run_g3=False)
        self.assertEqual(len(spawned), 1)
        pids = json.loads(pidfile.read_text())
        self.assertFalse(_alive(pids["child"]))
        deadline = time.monotonic() + 10
        while _alive(pids["grandchild"]) and time.monotonic() < deadline:
            time.sleep(0.05)  # reparented to launchd, reaped there
        self.assertFalse(_alive(pids["grandchild"]))
        self.assertFalse((window.claim / "campaign.lock").exists())
        flag = next(flag for flag in window.flags() if flag["code"] == "whole_window.producer_failed")
        self.assertEqual({key: flag["observed"][key] for key in ("timed_out", "group_gone", "lock", "timeout_s")},
                         {"timed_out": True, "group_gone": True, "lock": "removed", "timeout_s": 4.0})
        self.assertIn("whole_window.verdict_absent", window.codes())
        self.assertNotIn("records.source_changed_during_harvest", window.codes())
        run = json.loads((window.archive / "withheld" / "desk-verdict-run.json").read_bytes())
        self.assertGreaterEqual(run["heartbeats"], 1)
        self.assertIn("whole-window verdict running", stderr.getvalue())
        self.assertNotIn("desk", [fault["collector"] for fault in
                                  json.loads((window.archive / "harvest.json").read_bytes())["faults"]])


class CampaignLockRemovalTests(unittest.TestCase):
    """Row 1: the lock is removed only for the dead child's recorded pid and start time."""

    START = "Tue Oct  6 12:00:00 2026"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="b5-desk-lock-", dir=base.REAL_TMP)
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name)

    def lock(self, pid: int, start: str | None) -> Path:
        path = self.runs / "campaign.lock"
        path.write_text(f"pid={pid} nonce=n created_at=t start_time={json.dumps(start)}\n")
        return path

    def remove(self, *, child_pid=4242, child_start=START, state="DEAD"):
        return h.remove_dead_child_lock(self.runs, child_pid=child_pid, child_start_time=child_start,
                                        observe_identity=lambda pid: SimpleNamespace(state=state, start_time=None))

    def test_only_the_dead_childs_own_lock_is_removed(self):
        cases = {
            "removed": (dict(), (4242, self.START)),
            "kept:other_pid": (dict(), (4243, self.START)),
            "kept:other_start_time": (dict(), (4242, "Tue Oct  6 12:00:01 2026")),
            "kept:pid_not_dead": (dict(state="LIVE"), (4242, self.START)),
            "kept:child_start_unobserved": (dict(child_start=None), (4242, self.START)),
        }
        for expected, (kwargs, (pid, start)) in cases.items():
            with self.subTest(expected):
                path = self.lock(pid, start)
                self.assertEqual(self.remove(**kwargs), expected)
                self.assertEqual(path.exists(), expected != "removed")
                path.unlink(missing_ok=True)
        self.assertEqual(self.remove(), "absent")
        (self.runs / "campaign.lock").write_text("not a lock\n")
        self.assertEqual(self.remove(), "kept:unparseable")


class DeskConcurrencyTests(base.WindowTestCase):
    """Row 1: the verdict writer runs while the members are assessed, not before."""

    def concurrent_harvest(self, *, touch: str | None = None):
        window = self.window(prefix_ledger=True)
        assessed = threading.Event()
        seen: list[bool] = []
        calls: list[str] = []
        children = []

        class SlowWriter:
            """Writes the verdict and exits only after the first member assessment began."""

            def __init__(self, argv, **kwargs):
                self.runs = Path(argv[argv.index("--runs-dir") + 1])
                self.returncode, self.pid = None, -1
                children.append(self)

            def wait(self, timeout=None):
                if not assessed.wait(timeout):
                    raise subprocess.TimeoutExpired("desk", timeout)
                if self.returncode is None:
                    if touch is not None:
                        (self.runs / touch / "logs" / "controller.log").write_text("changed under the harvest\n")
                    (self.runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
                    self.returncode = 1
                return self.returncode

            def poll(self):
                return self.returncode

        def assess(task):
            calls.append(task["run_id"])
            seen.append(children[0].returncode is None if children else False)
            assessed.set()
            return base.cached_assess(task)

        seams = h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
                        runner=_no_synchronous_runner, desk_popen=SlowWriter, desk_heartbeat_s=5.0)
        with mock.patch.object(h, "assess_member", assess):
            record = window.harvest(seams=seams, prepare_desk=True, run_g3=False)
        return window, record, seen, calls

    def test_the_first_member_is_assessed_while_the_writer_runs(self):
        window, record, seen, calls = self.concurrent_harvest()
        self.assertTrue(seen and seen[0], "the first assessment ran after the writer had finished")
        # Every early result was bound to the archived bytes and reused: one assessment per member.
        self.assertEqual(sorted(calls), sorted(run_id for run_id, *_rest in base.MEMBERS))
        self.assertEqual(record["members_assessed"], len(base.MEMBERS))
        self.assertNotIn("records.source_changed_during_harvest", window.codes())
        for run_id, *_rest in base.MEMBERS:
            rereduced = window.archive / "withheld" / "reductions" / f"{run_id}.summary_metrics.rereduced.json"
            self.assertEqual(rereduced.read_bytes(), (window.claim / run_id / "summary_metrics.json").read_bytes())

    def test_a_bundle_that_changed_under_the_early_assessment_is_assessed_again(self):
        window, record, _seen, calls = self.concurrent_harvest(touch="b5t-abs-r01")
        self.assertEqual(calls.count("b5t-abs-r01"), 2)
        flags = [flag["observed"] for flag in window.flags() if flag["code"] == "records.source_changed_during_harvest"]
        self.assertIn(["b5t-abs-r01/logs/controller.log"], [item.get("changed") for item in flags])
        self.assertIn(["b5t-abs-r01"], [item.get("early_assessments_discarded") for item in flags])
        assessments = json.loads((window.archive / "withheld" / "member-assessments.json").read_bytes())["members"]
        self.assertIn("/withheld/reassessed/", assessments["b5t-abs-r01"]["rereduced"]["path"])


if __name__ == "__main__":
    unittest.main()


class WorkerCalibrationCacheTests(base.WindowTestCase):
    """X3 (t3-9): one calibration physics cache per worker, for the re-reduction and (with J2) strict."""

    CACHE_ASSESSMENTS = False

    def assess_two(self, *, j2: bool):
        window = self.window()
        seen = {"reduce": [], "strict": []}
        from joulewise import cli, reduce as reducer
        real_reduce, real_validate = reducer.reduce_bundle, cli.validate_bundle

        def reduce_spy(path, **kwargs):
            seen["reduce"].append(kwargs.get("_instrument_calibration_physics_cache"))
            return real_reduce(path, **kwargs)

        if j2:
            def validate_spy(path, strict=False, physics_cache=None):
                seen["strict"].append(physics_cache)
                return real_validate(path, strict)
        else:
            def validate_spy(path, strict=False):
                seen["strict"].append("no-keyword")
                return real_validate(path, strict)

        h._WORKER_PHYSICS_CACHE.clear()
        self.addCleanup(h._WORKER_PHYSICS_CACHE.clear)
        with mock.patch.object(reducer, "reduce_bundle", reduce_spy), \
                mock.patch.object(cli, "validate_bundle", validate_spy):
            results = [h.assess_member({"run_id": run_id, "bundle_path": str(window.claim / run_id),
                                        "withheld_dir": str(window.root / "withheld")})
                       for run_id in ("b5t-abs-r01", "b5t-abs-r02")]
        return seen, results

    def test_the_rereduction_uses_the_workers_cache(self):
        seen, results = self.assess_two(j2=False)
        rereduce = [cache for cache in seen["reduce"] if cache is not None]
        # Strict (without J2) reduces without a cache; the re-reduction with the worker's.
        self.assertEqual(len(rereduce), 2)
        self.assertTrue(all(cache is h._WORKER_PHYSICS_CACHE for cache in rereduce))
        self.assertEqual(seen["strict"], ["no-keyword", "no-keyword"])
        for result in results:
            self.assertTrue(result["strict_valid"], result["strict_problems"])
            self.assertTrue(result["rereduced"]["identical_to_stored"])
            self.assertFalse(result["calibration_cache"]["strict_uses_cache"])

    def test_strict_validation_shares_the_cache_once_the_cli_takes_it(self):
        seen, results = self.assess_two(j2=True)
        self.assertEqual(len(seen["strict"]), 2)
        self.assertTrue(all(cache is h._WORKER_PHYSICS_CACHE for cache in seen["strict"]))
        self.assertTrue(all(result["calibration_cache"]["strict_uses_cache"] for result in results))


class Prune2CodeRegistrationTests(unittest.TestCase):
    """PLAN2 3.1 (P2-HARV) and 2.2 G: every round-2 code is classified in the draft, the fixture and the harvest."""

    EXPECTED = {
        "member.timeout": ("MEMBER_VALIDITY", "NUMBER", "EXCLUDE_MEMBER"),
        "census.unmeasured": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "monitor.crash_loop": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "calibration.refit_cache_miss": ("CALIBRATION", "REPRESENTATION", "DISCLOSE"),
        "roster.horizon_truncated": ("ROSTER", "REPRESENTATION", "DISCLOSE"),
        "member.retried": ("ROSTER", "REPRESENTATION", "DISCLOSE"),
        "yield.stage_zero": ("DIAGNOSTIC", "REPRESENTATION", "DISCLOSE"),
        "yield.stage_low": ("DIAGNOSTIC", "REPRESENTATION", "DISCLOSE"),
        "yield.stage_stalled": ("DIAGNOSTIC", "REPRESENTATION", "DISCLOSE"),
        "stage.members_refused_pre_bundle_identical": ("DIAGNOSTIC", "REPRESENTATION", "DISCLOSE"),
        "records.runs_root_override": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "yield.harvest_disagrees_with_window": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "collection.zero_yield": ("ROSTER", "REPRESENTATION", "DISCLOSE"),
        "collection.failure_histogram": ("DIAGNOSTIC", "REPRESENTATION", "DISCLOSE"),
        "chain.stopped_before_collection": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "roster.dispatch_unresolved": ("ROSTER", "REPRESENTATION", "DISCLOSE"),
        "records.identity_unmeasured_superseded": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "thermal.stage_battery_rise": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
        "thermal.battery_temperature_unmeasured": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
    }

    def test_every_round_two_code_is_classified_everywhere(self):
        from joulewise.flags.catalog import DRAFT_CODES
        fixture = json.loads((base.FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        self.assertEqual(set(self.EXPECTED), set(h.PRUNE2_CODES))
        for code, expected in self.EXPECTED.items():
            with self.subTest(code):
                self.assertEqual((DRAFT_CODES[code]["family"], DRAFT_CODES[code]["klass"],
                                  DRAFT_CODES[code]["effect"]), expected)
                self.assertEqual((fixture[code]["family"], fixture[code]["klass"], fixture[code]["effect"]),
                                 expected)
                self.assertEqual((h.CODES[code].family, h.CODES[code].klass), expected[:2])
