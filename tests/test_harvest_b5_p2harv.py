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
        base.advance_pin(window)  # int3: the desk order is chain exit, pin advance, harvest (R2-1)
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
        base.advance_pin(window)  # int3: the desk order is chain exit, pin advance, harvest (R2-1)
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
        base.advance_pin(window)  # int3: the desk order is chain exit, pin advance, harvest (R2-1)
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
        # Registered at integration (int3).
        "member.stderr_uncopied": ("MEMBER_VALIDITY", "NUMBER", "EXCLUDE_MEMBER"),
        "records.auxiliary_match_raised": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "census.journal_write_failed": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "supervision.pass_failed": ("RECORDS", "REPRESENTATION", "DISCLOSE"),
        "monitor.outage": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE"),
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


def run_cli(window, *extra, overrides=()):
    """The harvest CLI on a synthetic window (its seams as CliTests sets them)."""
    from scripts import harvest_b5_window as cli

    def seams(**kwargs):
        return base._REAL_SEAMS(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
                                boot_session_uuid=lambda: "B5-CLI", **kwargs)

    stdout = io.StringIO()
    with mock.patch.object(h, "Seams", seams), contextlib.redirect_stdout(stdout):
        code = cli.main(["--plan", str(window.plan_path), "--archive-root", str(window.archive), "--workers", "1",
                         *extra])
    return code, stdout.getvalue()


def harvest_record(window) -> dict:
    return json.loads((window.archive / "harvest.json").read_bytes())


class YieldSummaryTests(base.WindowTestCase):
    """PLAN2 2.2 F: counts only, overall and per stage, in harvest.json and window_flags.json."""

    def test_the_yield_block_and_the_cli_counts(self):
        window = self.window()
        __import__("shutil").rmtree(window.claim / "b5t-abs-r02")
        (window.claim / "campaign_log.jsonl").write_text("".join(json.dumps(row) + "\n" for row in (
            {"run_id": "b5t-abs-r01", "status": "ok", "exit_code": 0,
             "members": [{"bundle_id": "b5t-abs-r01", "strict_valid": True, "strict_validation": "deferred_to_harvest"}]},
            {"run_id": "b5t-abs-r02", "status": "failed", "exit_code": None, "blocked_before_invoke": True,
             "preceding_campaign_cooldown": {"result": "unknown", "reason": "rolling mean 0.123 W over 30 s"}},
        )))
        code, output = run_cli(window)
        self.assertEqual(code, 0, output)
        record = harvest_record(window)
        planned = len(base.MEMBERS)
        expected = {"planned": planned, "present": planned - 1, "raw_valid": planned - 1,
                    "succeeded": planned - 1, "strict_deferred": 1}
        self.assertEqual({key: record["yield"][key] for key in expected}, expected)
        self.assertEqual(window.window_flags()["yield"], record["yield"])
        per_stage = {row["stage_id"]: row for row in record["yield"]["per_roster_stage"]}
        self.assertEqual((per_stage["01_abs"]["planned"], per_stage["01_abs"]["present"]), (2, 1))
        self.assertIn(f"members={planned - 1}/{planned} ", output.splitlines()[0])
        self.assertTrue(any(line.startswith("exclude_window=") for line in output.splitlines()))
        missing = next(flag["observed"] for flag in window.flags() if flag["code"] == "member.bytes_missing")
        self.assertEqual(missing, {"bundle": "absent", "campaign_status": "failed", "exit_code": None,
                                   "cooldown": {"result": "unknown", "reason": "rolling mean #.### W over ## s"}})

    def test_a_collected_window_with_nothing_present_exits_6(self):
        window = self.window()
        for run_id, *_rest in base.MEMBERS:
            __import__("shutil").rmtree(window.claim / run_id)
        code, output = run_cli(window)
        self.assertEqual(code, 6, output)
        self.assertIn("collection.zero_yield", window.codes())
        self.assertIn(f"members=0/{len(base.MEMBERS)} ", output.splitlines()[0])

    def test_the_window_counts_are_cross_checked(self):
        window = self.window()
        (window.custody / "night" / "stage_yield.jsonl").write_text(json.dumps(
            {"stage_id": "b5t-unknown-stage", "planned": 6, "present": 6, "succeeded": 6, "rc": 0}) + "\n")
        window.harvest()
        flag = next(flag["observed"] for flag in window.flags()
                    if flag["code"] == "yield.harvest_disagrees_with_window")
        self.assertEqual(flag, {"stage_id": "b5t-unknown-stage", "window": {"planned": 6, "present": 6,
                                                                            "succeeded": 6}, "harvest": None})


class RunsRootTests(base.WindowTestCase):
    """PLAN2 2.1 row 18: a missing runs root is a fault; an override is recorded and printed."""

    def test_an_absent_runs_root_is_a_harvest_fault(self):
        window = self.window()
        __import__("shutil").rmtree(window.bound)
        code, output = run_cli(window)
        self.assertEqual(code, 2, output)
        record = harvest_record(window)
        self.assertEqual(record["verdict"], "HARVEST_FAULT")
        self.assertIn("runs_roots", [fault["collector"] for fault in record["faults"]])
        errors = json.loads((window.archive / "withheld" / "collector-errors.json").read_bytes())["errors"]
        self.assertIn("runs_root_absent:bound", [error["detail"] for error in errors])

    def test_a_runs_root_override_is_recorded_and_printed(self):
        window = self.window()
        other = window.root / "elsewhere" / "runs_bound"
        other.mkdir(parents=True)
        code, output = run_cli(window, "--bound-runs-root", str(other))
        flag = next(flag["observed"] for flag in window.flags() if flag["code"] == "records.runs_root_override")
        self.assertEqual(flag, {"root": "bound", "planned": str(window.bound), "used": str(other)})
        self.assertIn(f"runs_root_override=bound:{other} planned={window.bound}", output)


class CollectionCauseTests(base.WindowTestCase):
    """PLAN2 2.2 F: the operator-log error lines, grouped; and a chain that never collected."""

    def test_error_lines_are_grouped_by_their_redacted_text(self):
        window = self.window()
        logs = window.custody / "operator-logs"
        logs.mkdir(parents=True, exist_ok=True)
        (logs / "07-b5t-science.log").write_text(
            "note\nerror: LaunchLineageError: member 3 refused after 12 s\n"
            "error: LaunchLineageError: member 4 refused after 12 s\n")
        (logs / "08-b5t-science.log").write_text("error: something else broke\n")
        window.harvest()
        observed = next(flag["observed"] for flag in window.flags() if flag["code"] == "collection.failure_histogram")
        self.assertEqual((observed["lines"], observed["distinct"]), (3, 2))
        first = observed["causes"][0]
        self.assertEqual({key: first[key] for key in ("cause_class", "text", "count", "stages")},
                         {"cause_class": "LaunchLineageError", "text": "LaunchLineageError: member # refused after ## s",
                          "count": 2, "stages": ["07-b5t-science"]})
        self.assertEqual(observed["causes"][1]["cause_class"], "unclassified")
        texts = json.loads((window.archive / "withheld" / "failure-texts.json").read_bytes())["lines"]
        self.assertEqual(len(texts), 3)

    def test_a_chain_that_journaled_no_collection_stage_is_no_collection(self):
        window = self.window()
        (window.custody / "night" / "chain-stages.jsonl").write_text(json.dumps(
            {"stage_id": "b5t-bracket-reservation", "kind": "bracket_reservation", "rc": 10,
             "started_epoch_s": 1, "ended_epoch_s": 2}) + "\n")
        code, output = run_cli(window)
        record = harvest_record(window)
        self.assertEqual(record["verdict"], "NO_COLLECTION")
        self.assertFalse(record["claim_usable"])
        self.assertEqual(record["members_assessed"], len(base.MEMBERS))  # every collector still ran
        observed = next(flag["observed"] for flag in window.flags()
                        if flag["code"] == "chain.stopped_before_collection")
        self.assertEqual(observed, {"stages_journaled": 1, "last_stage": "b5t-bracket-reservation",
                                    "last_kind": "bracket_reservation", "last_rc": 10})
        self.assertEqual(code, 0, output)

    def test_a_journaled_collection_stage_keeps_the_window_collected(self):
        window = self.window()
        (window.custody / "night" / "chain-stages.jsonl").write_text(json.dumps(
            {"stage_id": "b5t-science", "kind": "campaign_collection", "rc": 0}) + "\n")
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertNotIn("chain.stopped_before_collection", window.codes())


class StageDispatchResolverTests(base.WindowTestCase):
    """Row 14 / J3: stage_dispatches reads the chain lane's resolver; unresolved stages are flagged."""

    def add_collection_stage(self, window):
        tree_path = window.pack / "plan_tree.json"
        tree = json.loads(tree_path.read_bytes())
        tree["stage_graph"].append({
            "stage_id": "b5t-science", "kind": "campaign_collection", "ordinal": 2, "input_ref": None,
            "launch": {"commands": [{"argv_template": {"arguments": [
                {"kind": "repo_path", "value": f"configs/campaigns/{base.PACK_ID}"},
                {"kind": "literal", "value": "--runs-dir"}, {"kind": "binding", "value": "claim_runs_root"}]}}]}})
        base.put(tree_path, tree)

    def test_without_the_resolver_the_stage_is_flagged_unresolved(self):
        window = self.window()
        self.add_collection_stage(window)
        window.harvest()
        observed = next(flag["observed"] for flag in window.flags() if flag["code"] == "roster.dispatch_unresolved")
        self.assertEqual(observed["stages"], ["b5t-science"])
        self.assertEqual(harvest_record(window)["yield"]["unresolved_collection_stages"], ["b5t-science"])

    def test_the_resolver_supplies_the_stage_members_for_dispatch_and_yield(self):
        from joulewise.b5 import plan as b5_plan
        window = self.window()
        self.add_collection_stage(window)
        run_ids = [run_id for run_id, *_rest in base.MEMBERS]
        asked = []

        def resolve(stage, *, pack_root, repo_root=None):
            asked.append(stage["stage_id"])
            return "claim_runs_root", list(run_ids)

        (window.custody / "night" / "stage_yield.jsonl").write_text(json.dumps(
            {"stage_id": "b5t-science", "planned": 6, "present": 6, "succeeded": 6}) + "\n")
        with mock.patch.object(b5_plan, h.J3_RESOLVER_NAME, resolve, create=True):
            window.harvest()
        self.assertIn("b5t-science", asked)
        self.assertNotIn("roster.dispatch_unresolved", window.codes())
        stage = harvest_record(window)["yield"]["per_collection_stage"]
        self.assertEqual(stage, [{"stage_id": "b5t-science", "planned": 6, "present": 6, "raw_valid": 6,
                                  "succeeded": 6, "strict_deferred": 0}])
        self.assertNotIn("yield.harvest_disagrees_with_window", window.codes())


class BatteryThermistorTests(base.WindowTestCase):
    """Timing ruling 2026-10-06: the per-stage battery-thermistor diagnostic, disclosed only."""

    def manifest(self, window, name, readings):
        directory = window.claim / "campaign_manifests"
        directory.mkdir(exist_ok=True)
        document = {"members": [], "config_dir": f"/x/{name}"}
        if readings is not None:
            document["battery_temperature_readings"] = [
                {"temperature_centi_c": value, "error": None if value is not None else "exit 1"} for value in readings]
        base.put(directory / f"{name}.json", document)

    def test_rise_without_plateau_and_unmeasured_stages(self):
        window = self.window()
        self.manifest(window, "rising", [3000, 3200, 3400, 3600])      # +6 K, last three spread 4 K
        self.manifest(window, "plateau", [3000, 3350, 3380, 3390])     # +3.9 K, last three within 0.4 K
        self.manifest(window, "small", [3000, 3100, 3250])             # +2.5 K
        self.manifest(window, "failed", [3000, None, 3050])
        self.manifest(window, "absent", None)
        window.harvest()
        rises = [flag["observed"] for flag in window.flags() if flag["code"] == "thermal.stage_battery_rise"]
        self.assertEqual([(item["config_dir"], item["rise_k"], item["last_three_spread_k"]) for item in rises],
                         [("rising", 6.0, 4.0)])
        unmeasured = sorted((flag["observed"]["config_dir"], flag["observed"]["reason"]) for flag in window.flags()
                            if flag["code"] == "thermal.battery_temperature_unmeasured")
        self.assertEqual(unmeasured, [("absent", "no_readings_recorded"), ("failed", "readings_failed")])
        excluded = window.exclusions()["reasons"]
        self.assertNotIn("thermal.stage_battery_rise", excluded)


def arm_unmeasured(collector: str) -> dict:
    """The flag run_collectors leaves at the arm for a collector that timed out."""
    from joulewise.flags.collect import CollectorOutcome, collector_unmeasured_flag
    return collector_unmeasured_flag(CollectorOutcome(collector, "timeout", 60.0, error="timed out after 60.0 s"),
                                     {"stage": "arm", "plan_id": base.PLAN_ID, "attempt": 1})


class ArmIdentitySupersessionTests(base.WindowTestCase):
    """PLAN2 row 12: an arm *.identity_unmeasured yields to the harvest's own complete re-derivation."""

    def write_arm_flags(self, window, *collectors):
        flags = window.custody / "flags"
        flags.mkdir(parents=True, exist_ok=True)
        (flags / "arm.jsonl").write_text("".join(json.dumps(arm_unmeasured(name)) + "\n" for name in collectors))

    def test_untracked_files_under_the_executed_roots_differ_from_sealed(self):
        window = self.window(executed_overrides={"status_porcelain": "?? joulewise/stray.py\n?? notes/todo.txt\n"})
        window.harvest()
        observed = next(flag["observed"] for flag in window.flags()
                        if flag["code"] == "code.executed_differs_from_sealed")
        self.assertIn({"check": "untracked_in_executed_roots", "observed": ["joulewise/stray.py"]},
                      observed["differences"])

    def test_a_collector_the_harvest_fully_rederived_is_superseded(self):
        window = self.window()
        self.write_arm_flags(window, "checkout_identity", "executed_code", "pack_identity", "model_identity")
        window.harvest()
        codes = [flag["code"] for flag in window.flags()]
        self.assertNotIn("code.identity_unmeasured", codes)
        self.assertNotIn("pack.identity_unmeasured", codes)
        self.assertIn("model.identity_unmeasured", codes)  # the harvest does not re-hash the model
        superseded = sorted(flag["observed"]["collector"] for flag in window.flags()
                            if flag["code"] == "records.identity_unmeasured_superseded")
        self.assertEqual(superseded, ["checkout_identity", "executed_code", "pack_identity"])
        reasons = window.exclusions()["reasons"]
        self.assertIn("model.identity_unmeasured", reasons)
        self.assertNotIn("code.identity_unmeasured", reasons)

    def test_a_check_the_harvest_could_not_run_keeps_the_arm_flag(self):
        window = self.window(executed_overrides={"status_porcelain": None})
        self.write_arm_flags(window, "checkout_identity")
        window.harvest()
        self.assertIn("code.identity_unmeasured", window.codes())
        self.assertNotIn("records.identity_unmeasured_superseded", window.codes())

    def test_a_killed_collector_call_fails_closed_then_supersedes(self):
        window = self.window()
        base.put(window.custody / "night" / "arm_collectors.json",
                 {"schema": "joulewise.b5_arm_collectors.v1", "call": 1, "ran_by": "driver",
                  "collector_error": "timed out", "timed_out": True, "returncode": None})
        window.harvest()
        unmeasured = sorted((flag["code"], flag["observed"]["collector"]) for flag in window.flags()
                            if flag["code"].endswith(".identity_unmeasured"))
        self.assertEqual(unmeasured, [("model.identity_unmeasured", "model_identity")])
        self.assertIn("model.identity_unmeasured", window.exclusions()["reasons"])
        superseded = sorted(flag["observed"]["collector"] for flag in window.flags()
                            if flag["code"] == "records.identity_unmeasured_superseded")
        self.assertEqual(superseded, ["checkout_identity", "executed_code", "pack_identity"])


class ArmCollectorBudgetTests(unittest.TestCase):
    """PLAN2 row 12: the arm's per-collector budgets fit inside the driver's 120 s kill."""

    def test_the_arm_budgets_fit_inside_the_outer_kill(self):
        from joulewise.b5 import driver
        from joulewise.flags import collect
        self.assertEqual(collect.ARM_OUTER_TIMEOUT_S, driver.COLLECTOR_TIMEOUT_S)
        self.assertEqual(set(collect.ARM_TIMEOUTS_S), set(collect.DEFAULT_TIMEOUTS_S))
        self.assertLessEqual(sum(collect.ARM_TIMEOUTS_S.values()) + 10.0, driver.COLLECTOR_TIMEOUT_S)

    def test_run_collectors_uses_them_at_the_arm_only(self):
        from joulewise.flags import collect
        asked = {}

        def fake(name, params, *, timeout_s=None, python=None, module=None):
            asked.setdefault(params["stage"], {})[name] = timeout_s
            return collect.CollectorOutcome(name, "ok", 0.0)

        sink = SimpleNamespace(append=lambda flag: True)
        with mock.patch.object(collect, "run_collector", fake):
            for stage in ("arm", "desk"):
                collect.run_collectors([(name, {}) for name in collect.ARM_TIMEOUTS_S], stage=stage, sink=sink)
        self.assertEqual(asked["arm"], collect.ARM_TIMEOUTS_S)
        self.assertEqual(set(asked["desk"].values()), {None})  # the desk keeps DEFAULT_TIMEOUTS_S


# ---------------------------------------------------------------------------
# Independent review (Sol 6.1, 2026-10-06) findings F1-F7 and their probes.
# ---------------------------------------------------------------------------

def _bare_harvest(**attrs):
    """A _Harvest with only the attributes a unit under test reads; emits and errors are recorded."""
    run = object.__new__(h._Harvest)
    run.emitted, run.prior = [], []
    run.emit = lambda code, **kwargs: run.emitted.append((code, kwargs))
    run._prior_collector_error = lambda **kwargs: run.prior.append(kwargs)
    run.collector_ok, run.collector_ok_runs = set(), []
    run.__dict__.update(attrs)
    return run


def _arm_run_record(started_wall_s, ok=("pack_identity", "checkout_identity", "executed_code", "model_identity")):
    return {"schema_version": h.COLLECTOR_RUN_SCHEMA, "stage": "arm", "started": {"wall_s": started_wall_s},
            "finished": {"wall_s": started_wall_s + 20},
            "collectors": [{"collector": name, "status": "ok"} for name in ok], "collector_errors": []}


class ArmCallBindingTests(unittest.TestCase):
    """Review F1/F2: an ok arm row speaks only for a call it could have come from; a bad receipt fails closed."""

    def arm(self, night: Path, runs=(), **receipts):
        run = _bare_harvest(inputs=SimpleNamespace(night_dir=night))
        for record in runs:
            run._fold_collector_run(record, source="flags/collector_runs.jsonl:1")
        for name, value in receipts.items():
            (night / f"{name}.json").write_text(value if isinstance(value, str) else json.dumps(value))
        run._arm_collector_records(None)
        return run, sorted(code for code, _kwargs in run.emitted if code.endswith(".identity_unmeasured"))

    def killed(self, started_wall_s, call=2):
        return {"schema": "joulewise.b5_arm_collectors.v1", "call": call, "ran_by": "driver",
                "collector_error": "timed out", "timed_out": True, "returncode": None,
                "started": {"wall_s": started_wall_s}}

    def test_an_earlier_completed_call_does_not_speak_for_a_later_killed_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            _run, codes = self.arm(Path(tmp), [_arm_run_record(100.0)], **{"arm_collectors": self.killed(200.0)})
        self.assertEqual(codes, ["code.identity_unmeasured", "code.identity_unmeasured",
                                 "model.identity_unmeasured", "pack.identity_unmeasured"])

    def test_a_run_record_from_the_killed_call_itself_still_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            _run, codes = self.arm(Path(tmp), [_arm_run_record(201.0, ok=("model_identity",))],
                                   **{"arm_collectors": self.killed(200.0)})
        self.assertNotIn("model.identity_unmeasured", codes)
        self.assertIn("pack.identity_unmeasured", codes)

    def test_a_truncated_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            run, codes = self.arm(Path(tmp), [_arm_run_record(100.0)], **{"arm_collectors": '{"collector_error":'})
        self.assertIn("model.identity_unmeasured", codes)
        self.assertEqual([row["status"] for row in run.prior], ["malformed"])

    def test_a_receipt_that_is_not_an_object_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _run, codes = self.arm(Path(tmp), [_arm_run_record(100.0)], **{"arm_collectors": "[]"})
        self.assertIn("model.identity_unmeasured", codes)

    def test_a_completed_call_raises_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok = {"schema": "joulewise.b5_arm_collectors.v1", "call": 1, "ran_by": "driver", "returncode": 0,
                  "timed_out": False, "error": None, "started": {"wall_s": 99.0}}
            _run, codes = self.arm(Path(tmp), [_arm_run_record(100.0)], **{"arm_collectors": ok})
        self.assertEqual(codes, [])


class SupersessionCheckSetTests(unittest.TestCase):
    """Review F7 (M49) and probes: supersession needs the named checks, a resolved dispatch, and keeps the flag."""

    FULL = {"pack_identity": {"pins": True, "config_run_id": True, "registered_digests": True},
            "checkout_identity": {"head": True, "tracked_edits": True, "untracked_in_executed_roots": True},
            "executed_code": {"executed_inventory": True, "chain_sidecar": True}}

    def supersede(self, collector, checks, **attrs):
        record = arm_unmeasured(collector)
        ledger = SimpleNamespace(records=[record])
        ledger.remove = lambda flag_id: ledger.records.remove(record)
        run = _bare_harvest(flags=ledger, identity_checks=checks, dispatches={}, dispatch_unresolved=[], **attrs)
        run.supersede_identity_unmeasured()
        return run, record, ledger

    def test_every_named_check_is_required(self):
        for collector in ("pack_identity", "checkout_identity", "executed_code"):
            for missing in self.FULL[collector]:
                with self.subTest(collector=collector, missing=missing):
                    checks = {name: dict(value) for name, value in self.FULL.items()}
                    del checks[collector][missing]
                    _run, _record, ledger = self.supersede(collector, checks)
                    self.assertEqual(len(ledger.records), 1)

    def test_a_full_set_supersedes_and_records_the_whole_flag(self):
        run, record, ledger = self.supersede("checkout_identity", self.FULL)
        self.assertEqual(ledger.records, [])
        (code, kwargs), = run.emitted
        self.assertEqual(code, "records.identity_unmeasured_superseded")
        self.assertEqual(kwargs["observed"]["superseded_flag"], record)

    def test_pack_identity_waits_for_every_collection_stage_to_resolve(self):
        _run, _record, ledger = self.supersede("pack_identity", self.FULL)
        self.assertEqual(ledger.records, [])
        record = arm_unmeasured("pack_identity")
        ledger = SimpleNamespace(records=[record])
        ledger.remove = lambda flag_id: ledger.records.remove(record)
        run = _bare_harvest(flags=ledger, identity_checks=self.FULL, dispatches={}, dispatch_unresolved=["s"])
        run.supersede_identity_unmeasured()
        self.assertEqual(ledger.records, [record])


class ConfigRunIdReplayTests(base.WindowTestCase):
    """Review F7 (M42): the harvest replays the arm's config run-id check from the preserved bytes."""

    def test_a_config_whose_run_id_is_not_the_rosters_is_a_pack_identity_mismatch(self):
        window = self.window()
        config = window.pack / "01_abs" / "b5t-abs-r01.json"
        value = json.loads(config.read_bytes())
        value["run_id"] = "b5t-abs-other"
        config.write_bytes(base.normalized_config(value))
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "pack.identity_mismatch")
        self.assertIn({"path": f"configs/campaigns/{base.PACK_ID}/01_abs/b5t-abs-r01.json", "check": "config_run_id",
                       "expected": "b5t-abs-r01", "observed": "b5t-abs-other"}, flag["observed"]["mismatches"])


class DeskChildSupervisionTests(unittest.TestCase):
    """Review F3/F5: a started writer is never left unsupervised, and a reused group id is never signalled."""

    def test_a_failure_after_spawn_tears_the_group_down(self):
        kills, waits = [], []
        child = SimpleNamespace(pid=424242, wait=lambda timeout=None: waits.append(timeout))

        def observe(pid):
            raise OSError("ps failed")

        seams = h.Seams(desk_popen=lambda *a, **k: child, observe_identity=observe,
                        killpg=lambda pid, signum: kills.append(signum), group_alive=lambda pgid: False,
                        desk_term_grace_s=0.01, desk_gone_wait_s=0.01)
        with self.assertRaises(h.DeskChildInitError) as caught:
            h.DeskVerdictChild(["writer"], cwd=".", timeout_s=1.0, bundles=0, seams=seams, runs_root=Path("."))
        self.assertEqual(kills[:1], [signal.SIGTERM])
        self.assertTrue(caught.exception.group_gone)

    def test_an_unproven_teardown_after_spawn_is_a_harvest_fault(self):
        child = SimpleNamespace(pid=424242, wait=lambda timeout=None: None)

        def observe(pid):
            raise OSError("ps failed")

        seams = h.Seams(desk_popen=lambda *a, **k: child, observe_identity=observe, killpg=lambda *a: None,
                        group_alive=lambda pgid: True, desk_term_grace_s=0.01, desk_gone_wait_s=0.01)
        run = _bare_harvest(seams=seams, faults=[])
        run.fault = lambda collector, reason: run.faults.append((collector, reason))
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp)
            run.inputs = SimpleNamespace(claim_runs_root=runs, bracket_session_id="s", measurement_root=runs,
                                         pre_attempt_id=None, post_attempt_id=None, bound_runs_root=None,
                                         ledger_path=runs / "ledger", head_pin_path=runs / "pin")
            run._policy_path = lambda: runs / "policy.json"
            run._desk_pin_problem = lambda: None  # int3: the pin is at the session's terminal head (R2-1)
            (runs / "bracket-binding.json").write_text("{}")
            started = run.start_desk_verdict()
        self.assertFalse(started)
        self.assertIn(("desk", "desk_verdict_group_not_proven_gone"), run.faults)
        observed = next(kwargs["observed"] for code, kwargs in run.emitted if code == "whole_window.producer_failed")
        self.assertTrue(observed["started_then_torn_down"])
        self.assertFalse(observed["group_gone"])

    def supervised(self, identity, *, alive=(True, False)):
        signals, probes = [], iter(alive)
        child = object.__new__(h.DeskVerdictChild)
        child._started, child.timeout_s, child.pid, child.start_time = time.monotonic(), 5.0, 42, "original"
        child.process = SimpleNamespace(wait=lambda timeout=None: 0)
        child.timed_out, child.error, child.group_gone, child.survivors_after_exit = False, None, None, False
        child.pid_recycled = child.generation_unverified = child._reaped = False
        child.heartbeats, child.bundles = 0, 0
        child.seams = h.Seams(group_alive=lambda pgid: next(probes, True),
                              killpg=lambda pid, signum: signals.append(signum),
                              observe_identity=lambda pid: identity, desk_term_grace_s=0.01, desk_gone_wait_s=0.01)
        child._supervise()
        return child, signals

    def test_a_reused_group_id_is_not_signalled_and_the_group_counts_as_gone(self):
        child, signals = self.supervised(SimpleNamespace(state="LIVE", start_time="different-start"))
        self.assertEqual(signals, [])
        self.assertTrue(child.group_gone)
        self.assertTrue(child.pid_recycled)
        self.assertFalse(child.survivors_after_exit)

    def test_survivors_of_the_writers_own_group_are_still_killed(self):
        child, signals = self.supervised(SimpleNamespace(state="DEAD", start_time=None), alive=(True, True, False))
        self.assertIn(signal.SIGKILL, signals)
        self.assertTrue(child.survivors_after_exit)
        self.assertTrue(child.group_gone)

    def test_an_unverifiable_group_is_not_signalled_and_not_proven_gone(self):
        child, signals = self.supervised(SimpleNamespace(state="UNKNOWN", start_time=None),
                                         alive=(True,) * 1000)
        self.assertEqual(signals, [])
        self.assertTrue(child.generation_unverified)
        self.assertFalse(child.group_gone)


class DispatchAndYieldProbeTests(unittest.TestCase):
    """Review F4 and probes: a failing J3 is flagged, an empty stage stays in the yield, bytes count as present."""

    TREE = {"stage_graph": [{"stage_id": "s", "kind": "campaign_collection", "ordinal": 1,
                             "input_ref": {"kind": "external_input", "input_id": "i"}}],
            "external_inputs": [{"input_id": "i", "members": [{"run_id": "legacy"}]}]}

    def test_a_raising_resolver_falls_back_but_is_listed_unresolved(self):
        def broken(*args, **kwargs):
            raise ValueError("bad argv")
        report = {}
        with mock.patch.object(h, "_j3_resolver", return_value=broken):
            dispatches, unresolved = h.stage_dispatches(self.TREE, Path("."), Path("."), report=report)
        self.assertEqual(unresolved, ["s"])
        self.assertEqual(list(dispatches), ["legacy"])  # the counts still come from input_ref
        self.assertEqual(report["j3_failures"], {"s": "ValueError: bad argv"})

    def test_a_malformed_resolver_value_is_a_failure_and_none_is_a_decline(self):
        for value, failed in ((("root", [""]), True), (42, True), (None, False)):
            with self.subTest(value=value), mock.patch.object(h, "_j3_resolver",
                                                              return_value=lambda *a, **k: value):
                report = {}
                _dispatches, unresolved = h.stage_dispatches(self.TREE, Path("."), Path("."), report=report)
                self.assertEqual(unresolved, ["s"] if failed else [])
                self.assertEqual(bool(report["j3_failures"]), failed)

    def test_a_resolved_stage_with_no_members_stays_in_the_yield(self):
        tree = {"stage_graph": [{"stage_id": "empty", "kind": "campaign_collection", "ordinal": 3}]}
        report = {}
        with mock.patch.object(h, "_j3_resolver", return_value=lambda *a, **k: ("claim_runs_root", [])):
            dispatches, unresolved = h.stage_dispatches(tree, Path("."), Path("."), report=report)
        run = _bare_harvest(dispatches=dispatches, dispatch_unresolved=unresolved, dispatch_stages=report["stages"])
        self.assertEqual(run._collection_stages(), [("empty", [])])

    def test_bundle_bytes_without_an_assessment_are_present_not_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real-bundle").mkdir()
            run = _bare_harvest(members={}, inputs=SimpleNamespace(claim_runs_root=root, bound_runs_root=None))
            run._campaign_join = lambda: {}
            counts = run._counts(["real-bundle", "absent-bundle"])
        self.assertEqual((counts["planned"], counts["present"], counts["raw_valid"], counts["succeeded"]),
                         (2, 1, 0, 0))


class ThermistorManifestTests(unittest.TestCase):
    """Review F6: a stage manifest that cannot be read is disclosed as unmeasured, never skipped."""

    def emitted(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "campaign_manifests").mkdir()
            (root / "campaign_manifests" / "stage.json").write_text(text)
            run = _bare_harvest()
            run._runs_roots = lambda: [root]
            run.battery_thermistor()
        return [(code, kwargs["observed"].get("reason")) for code, kwargs in run.emitted]

    def test_a_truncated_manifest_is_unmeasured(self):
        self.assertEqual(self.emitted("{"), [("thermal.battery_temperature_unmeasured", "manifest_unreadable")])

    def test_a_manifest_that_is_not_an_object_is_unmeasured(self):
        self.assertEqual(self.emitted("[]"), [("thermal.battery_temperature_unmeasured", "manifest_malformed")])

    def test_a_json_object_that_is_not_a_stage_manifest_is_skipped(self):
        self.assertEqual(self.emitted('{"kind": "other"}'), [])


if __name__ == "__main__":
    unittest.main()
