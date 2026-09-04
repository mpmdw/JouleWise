from __future__ import annotations

import dataclasses
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import textwrap
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise.night_plan_writer import night_plan_mapping, write_night_plan
from scripts import magistrate_watchdog as wd


RETIRED_V1 = (
    Path(__file__).resolve().parent / "fixtures" / "night_plan_v1_retired.json"
)


class MutableClock:
    def __init__(self, wall: dt.datetime, monotonic: float = 1000.0) -> None:
        self.wall = wall
        self.mono = monotonic

    def wall_now(self) -> dt.datetime:
        return self.wall

    def monotonic(self) -> float:
        return self.mono


class FakeProcessTable:
    def __init__(self, rows: list[wd.ProcessInfo] | None = None) -> None:
        self.rows = list(rows or [])
        self.signals: list[tuple[int, int]] = []
        self.exit_on_term = False

    def snapshot(self) -> list[wd.ProcessInfo]:
        return list(self.rows)

    def send_signal(self, pid: int, signum: int) -> None:
        self.signals.append((pid, signum))
        if signum == signal.SIGKILL or self.exit_on_term:
            self.rows = [row for row in self.rows if row.pid != pid]


class FakeChild:
    def __init__(self, pid: int = 100) -> None:
        self.pid = pid
        self.exit_code: int | None = None

    def poll(self) -> int | None:
        return self.exit_code


class Harness:
    def __init__(self, root: Path, wall: dt.datetime) -> None:
        self.storage = wd.Storage(root)
        self.clock = MutableClock(wall)
        self.census = wd.CensusObservation(True, 1, "", "")
        self.census_calls = 0
        self.stop = wd.StopObservation("CLEAR", "clear")
        self.processes = FakeProcessTable()
        self.spawn_calls: list[tuple[tuple[str, ...], Path, Path, Path]] = []
        self.child = FakeChild()
        self.version = "2.1.260 (Claude Code)"

        def spawn(argv: object, cwd: Path, stdout: Path, stderr: Path) -> FakeChild:
            self.spawn_calls.append((tuple(argv), cwd, stdout, stderr))  # type: ignore[arg-type]
            return self.child

        def census() -> wd.CensusObservation:
            self.census_calls += 1
            return self.census

        self.deps = wd.Dependencies(
            wall_now=self.clock.wall_now,
            monotonic=self.clock.monotonic,
            census=census,
            git_probe=lambda: self.stop,
            processes=self.processes,
            spawn=spawn,
            version_probe=lambda _path: self.version,
            sleep=lambda _seconds: None,
        )


class WatchdogTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.local_tz = dt.datetime.now().astimezone().tzinfo
        assert self.local_tz is not None
        self.base = dt.datetime(2026, 9, 4, 1, 0, tzinfo=self.local_tz)
        self.harness = Harness(self.temp / "magistrate", self.base)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_plan(
        self,
        *,
        t0: float | None = None,
        name: str = "night-a",
        **changes: object,
    ) -> wd.NightPlan:
        custody = self.temp / name
        plan = wd.NightPlan(
            plan_id=name,
            receipt_class="REHEARSAL_STUB",
            t0_epoch_s=self.base.timestamp() + 3600 if t0 is None else t0,
            window_max_s=600,
            authored_epoch_s=self.base.timestamp() - 60,
            repo_head="a" * 40,
            measurement_root=str(self.temp / "measurement"),
            measurement_head="b" * 40,
            chain_path=str(custody / "chain.sh"),
            chain_sha256_path=str(custody / "chain.sh.sha256"),
            custody_root=str(custody),
            registration_path=str(custody / "registration.json"),
        )
        if changes:
            plan = dataclasses.replace(plan, **changes)
        custody.mkdir(parents=True, exist_ok=True)
        write_night_plan(custody / "night_plan.json", plan)
        return plan

    def write_live_lock(self, pid: int = 100, start: str = "token-a") -> dict[str, object]:
        record: dict[str, object] = {
            "schema": wd.LOCK_SCHEMA,
            "activation_id": "activation-a",
            "pid": pid,
            "start_time": start,
            "supervisor_pid": 99,
            "launch_epoch_s": self.base.timestamp(),
            "binary_symlink": str(wd.DEFAULT_SESSION_BIN),
            "binary_version": "2.1.260 (Claude Code)",
        }
        self.harness.storage.atomic_json(self.harness.storage.root / "magistrate.lock", record)
        return record

    def supervisor(self, plan: wd.NightPlan) -> wd.ResidentSupervisor:
        record = self.write_live_lock()
        self.harness.processes.rows = [wd.ProcessInfo(100, 99, "token-a", "session")]
        state = wd.initial_state()
        state.update({"state": "ACTIVE", "activation_id": "activation-a"})
        return wd.ResidentSupervisor(
            self.harness.storage,
            self.harness.deps,
            state,
            self.harness.child,
            record,
            self.harness.storage.root / "stdout",
            self.harness.storage.root / "stderr",
        )


class FenceTests(WatchdogTestCase):
    def test_retired_v1_is_ignored_once_and_only_v2_plan_sets_span(self) -> None:
        valid = self.make_plan(t0=self.base.timestamp() + 10 * 60, name="valid-v2")
        retired_root = self.temp / "retired-v1"
        retired_root.mkdir()
        shutil.copyfile(RETIRED_V1, retired_root / "night_plan.json")

        snapshot = wd.load_plans(
            self.harness.storage, now_epoch_s=self.base.timestamp()
        )
        self.assertEqual([plan.plan_id for plan in snapshot.plans], [valid.plan_id])
        self.assertTrue(
            wd.plan_span_active(
                snapshot.plans[0], self.base.timestamp(), self.harness.storage
            )
        )
        self.assertEqual(
            wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state,
            "FENCED",
        )
        self.assertEqual(snapshot.errors, ())
        wd.record_plan_diagnostics(
            self.harness.storage,
            snapshot.diagnostics,
            activation_id="activation-a",
        )
        wd.record_plan_diagnostics(
            wd.Storage(self.harness.storage.root),
            snapshot.diagnostics,
            activation_id="activation-a",
        )
        events = [
            json.loads(line)
            for line in (self.harness.storage.root / "events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        ignored = [event for event in events if event["kind"] == "plan_retired_v1"]
        self.assertEqual(len(ignored), 1)
        self.assertEqual(ignored[0]["plan_dir"], str(retired_root.resolve()))

    def test_unreadable_plan_is_recorded_once_and_holds(self) -> None:
        broken_root = self.temp / "broken-plan"
        broken_root.mkdir()
        (broken_root / "night_plan.json").write_text("{not-json", encoding="utf-8")

        decision = wd.decide(
            self.harness.storage, self.harness.deps, wd.initial_state()
        )
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("night_plan_unreadable", decision.reason)
        snapshot = wd.load_plans(self.harness.storage)
        self.assertEqual(len(snapshot.errors), 1)
        for _ in range(2):
            wd.record_plan_diagnostics(
                wd.Storage(self.harness.storage.root),
                snapshot.diagnostics,
                activation_id="activation-a",
            )
        events = [
            json.loads(line)
            for line in (self.harness.storage.root / "events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        unreadable = [event for event in events if event["kind"] == "plan_unreadable"]
        self.assertEqual(len(unreadable), 1)
        self.assertEqual(unreadable[0]["plan_dir"], str(broken_root.resolve()))

    def test_plan_event_key_distinguishes_changed_kind_and_dry_run_has_no_memory(self) -> None:
        plan_root = self.temp / "changing-plan"
        plan_root.mkdir()
        plan_path = plan_root / "night_plan.json"
        shutil.copyfile(RETIRED_V1, plan_path)
        first = wd.load_plans(
            self.harness.storage, now_epoch_s=self.base.timestamp()
        )
        dry_storage = wd.Storage(self.harness.storage.root, dry_run=True)
        wd.record_plan_diagnostics(
            dry_storage, first.diagnostics, activation_id="activation-a"
        )
        self.assertFalse((self.harness.storage.root / "events.jsonl").exists())
        dry_storage.dry_run = False
        wd.record_plan_diagnostics(
            dry_storage, first.diagnostics, activation_id="activation-a"
        )

        source = self.make_plan(name="writer-source")
        mapping = night_plan_mapping(source)
        del mapping["measurement_head"]
        plan_path.write_text(
            json.dumps(mapping, sort_keys=True) + "\n", encoding="utf-8"
        )
        second = wd.load_plans(
            self.harness.storage, now_epoch_s=self.base.timestamp()
        )
        wd.record_plan_diagnostics(
            dry_storage, second.diagnostics, activation_id="activation-a"
        )
        events = [
            json.loads(line)
            for line in (self.harness.storage.root / "events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        changing_events = [
            event for event in events if event.get("plan_dir") == str(plan_root.resolve())
        ]
        self.assertEqual(
            ["plan_retired_v1", "plan_malformed"],
            [event["kind"] for event in changing_events],
        )

    def test_future_authorship_is_malformed_and_holds(self) -> None:
        self.make_plan(authored_epoch_s=self.base.timestamp() + 1)
        decision = wd.decide(
            self.harness.storage, self.harness.deps, wd.initial_state()
        )
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("night_plan_malformed", decision.reason)
        self.assertIn("authored_epoch_s is in the future", decision.reason)

    def test_armed_plan_conflicts_hold_but_nonoverlapping_roots_compose(self) -> None:
        self.make_plan(
            name="left",
            t0=self.base.timestamp() + 60 * 60,
            measurement_root=str(self.temp / "measurement-left"),
        )
        self.make_plan(
            name="right",
            t0=self.base.timestamp() + 61 * 60,
            measurement_root=str(self.temp / "measurement-right"),
        )
        state = wd.initial_state()
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("plan_conflict", decision.reason)
        self.assertIn("overlapping spans", decision.reason)

        (self.temp / "right" / "night_plan.json").unlink()
        self.make_plan(
            name="right-later",
            t0=self.base.timestamp() + 30 * 60 * 60,
            measurement_root=str(self.temp / "measurement-right"),
        )
        state = wd.initial_state()
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual("LAUNCHING", decision.state)
        self.assertEqual(3, len(state["fenced_checkouts"]))
        prompt = wd.render_prompt(self.harness.storage, state, self.base)
        self.assertIn(str(self.temp / "measurement-left"), prompt)
        self.assertIn(str(self.temp / "measurement-right"), prompt)
        fence_line = next(
            line for line in prompt.splitlines() if line.startswith("Frozen checkout triples")
        )
        rendered_rows = json.loads(fence_line.split(": ", 1)[1].removesuffix("."))
        self.assertEqual(state["fenced_checkouts"], rendered_rows)
        self.assertEqual(
            ["__canonical_repo__", str(wd.CANONICAL_REPO), None], rendered_rows[0]
        )

    def test_one_measurement_root_at_two_heads_holds_for_any_spans(self) -> None:
        root = str(self.temp / "same-measurement")
        self.make_plan(name="head-a", measurement_root=root, measurement_head="a" * 40)
        self.make_plan(
            name="head-b",
            t0=self.base.timestamp() + 5 * 60 * 60,
            measurement_root=root,
            measurement_head="b" * 40,
        )
        decision = wd.decide(
            self.harness.storage, self.harness.deps, wd.initial_state()
        )
        self.assertEqual("HOLD_UNSAFE", decision.state)
        self.assertIn("multiple heads", decision.reason)

    def test_stale_gate_plan_remains_a_conservative_watchdog_fence(self) -> None:
        self.make_plan(
            t0=self.base.timestamp() + 10 * 60,
            authored_epoch_s=self.base.timestamp() - wd.PLAN_MAX_AGE_S - 1,
        )
        decision = wd.decide(
            self.harness.storage, self.harness.deps, wd.initial_state()
        )
        self.assertEqual("FENCED", decision.state)

    def test_plan_fence_boundaries_request_term_kill_and_completion(self) -> None:
        plan = self.make_plan()
        t0 = plan.t0_epoch_s
        self.assertEqual(wd.PLAN_LEAD_S, 1500)
        self.assertEqual(wd.REQUEST_LEAD_S, 1500)
        self.assertEqual(wd.TERM_LEAD_S, 960)
        self.assertEqual(wd.KILL_LEAD_S, 900)
        self.assertFalse(wd.plan_span_active(plan, t0 - wd.PLAN_LEAD_S - 0.001, self.harness.storage))
        self.assertTrue(wd.plan_span_active(plan, t0 - wd.PLAN_LEAD_S, self.harness.storage))
        self.assertEqual(wd.standdown_phase(plan, t0 - wd.REQUEST_LEAD_S), "REQUEST")
        self.assertEqual(wd.standdown_phase(plan, t0 - wd.TERM_LEAD_S), "TERM")
        self.assertEqual(wd.standdown_phase(plan, t0 - wd.KILL_LEAD_S), "KILL")

        night = Path(plan.custody_root) / "night"
        night.mkdir()
        (night / "courier.sent").write_text("sent\n", encoding="utf-8")
        completion = wd.plan_completion_epoch(plan)
        self.assertTrue(wd.plan_span_active(plan, completion, self.harness.storage))
        self.assertFalse(wd.plan_span_active(plan, completion + 0.001, self.harness.storage))

    def test_courier_and_deadman_lock_fresh_boundaries(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        after_completion = wd.plan_completion_epoch(plan) + 1
        self.assertTrue(wd.plan_span_active(plan, after_completion, self.harness.storage))
        (night / "courier.sent").write_text("sent\n", encoding="utf-8")
        self.assertFalse(wd.plan_span_active(plan, after_completion, self.harness.storage))
        (night / "courier.sent").unlink()

        deadman_end = wd._next_deadman_epoch(plan.t0_epoch_s) + wd.COURIER_LOCK_FRESH_S
        self.assertTrue(wd.plan_span_active(plan, deadman_end, self.harness.storage))
        self.assertFalse(wd.plan_span_active(plan, deadman_end + 0.001, self.harness.storage))

    def test_live_chain_extends_past_deadman_until_exit(self) -> None:
        plan = self.make_plan()
        night = Path(plan.custody_root) / "night"
        night.mkdir()
        late = wd._next_deadman_epoch(plan.t0_epoch_s) + wd.COURIER_LOCK_FRESH_S + 1
        (night / "chain.started").write_text("{}", encoding="utf-8")
        self.assertTrue(wd.plan_span_active(plan, late, self.harness.storage))
        (night / "chain.exited").write_text("{}", encoding="utf-8")
        self.assertFalse(wd.plan_span_active(plan, late, self.harness.storage))

    def test_fixed_belt_is_half_open(self) -> None:
        tz = self.local_tz
        self.assertIsNone(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 2, 44, 59, 999999, tzinfo=tz)))
        self.assertEqual(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 2, 45, tzinfo=tz)), "belt_02:45_03:30")
        self.assertEqual(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 3, 29, 59, 999999, tzinfo=tz)), "belt_02:45_03:30")
        self.assertIsNone(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 3, 30, tzinfo=tz)))

    def test_deadman_minute_is_half_open(self) -> None:
        tz = self.local_tz
        self.assertIsNone(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 6, 59, 59, 999999, tzinfo=tz)))
        self.assertEqual(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 7, 0, tzinfo=tz)), "deadman_minute_07:00")
        self.assertEqual(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 7, 0, 59, 999999, tzinfo=tz)), "deadman_minute_07:00")
        self.assertIsNone(wd.local_fixed_fence(dt.datetime(2026, 9, 4, 7, 1, tzinfo=tz)))


class StopAndDecisionTests(WatchdogTestCase):
    def test_stop_branch_present_absent_and_positive_control_failure(self) -> None:
        ok = subprocess.CompletedProcess([], 0, "main\n", "")
        absent = subprocess.CompletedProcess([], 2, "", "")
        present = subprocess.CompletedProcess([], 0, "stop\n", "")
        failed = subprocess.CompletedProcess([], 128, "", "network")

        with mock.patch.object(wd.subprocess, "run", side_effect=[ok, absent]):
            self.assertEqual(wd.remote_stop_probe().state, "CLEAR")
        with mock.patch.object(wd.subprocess, "run", side_effect=[ok, present]):
            self.assertEqual(wd.remote_stop_probe().state, "STOPPED")
        with mock.patch.object(wd.subprocess, "run", side_effect=[failed]) as run:
            self.assertEqual(wd.remote_stop_probe().state, "NETWORK_UNCERTAIN")
            self.assertEqual(run.call_count, 1, "a failed positive control cannot clear the switch")

    def test_stop_glob_catches_shortened_magistrate_branch_name(self) -> None:
        shortened = "refs/heads/ops/stop-magistrat"
        self.assertEqual(wd.STOP_REF_GLOB, "refs/heads/ops/stop*")
        self.assertTrue(fnmatch.fnmatchcase(shortened, wd.STOP_REF_GLOB))

    def test_injected_stop_observations_gate_launch(self) -> None:
        for stop, expected in (
            (wd.StopObservation("STOPPED", "present"), "STOPPED"),
            (wd.StopObservation("NETWORK_UNCERTAIN", "rc=128"), "NETWORK_UNCERTAIN"),
            (wd.StopObservation("CLEAR", "absent"), "LAUNCHING"),
        ):
            with self.subTest(stop=stop.state):
                state = wd.initial_state()
                self.harness.stop = stop
                self.assertEqual(wd.decide(self.harness.storage, self.harness.deps, state).state, expected)

    def test_local_stop_file_wins(self) -> None:
        self.harness.storage.mkdir(self.harness.storage.root)
        (self.harness.storage.root / "STOP").write_text("stop\n", encoding="utf-8")
        self.assertEqual(
            wd.decide(self.harness.storage, self.harness.deps, wd.initial_state()).state,
            "STOPPED",
        )

    def test_stale_pid_reused_by_another_process_is_not_owned(self) -> None:
        self.write_live_lock(pid=77, start="old-token")
        self.harness.processes.rows = [wd.ProcessInfo(77, 1, "new-token", "unrelated")]
        decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
        self.assertEqual(decision.state, "LAUNCHING")
        self.assertFalse((self.harness.storage.root / "magistrate.lock").exists())
        self.assertEqual(self.harness.processes.signals, [])

    def test_defunct_lock_owner_is_not_live(self) -> None:
        self.write_live_lock(pid=77, start="token-a")
        self.harness.processes.rows = [wd.ProcessInfo(77, 1, "token-a", "session <defunct>")]
        decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
        self.assertEqual(decision.state, "LAUNCHING")
        self.assertFalse((self.harness.storage.root / "magistrate.lock").exists())

    def test_live_lock_refuses_second_magistrate(self) -> None:
        self.write_live_lock()
        self.harness.processes.rows = [wd.ProcessInfo(100, 1, "token-a", "owned")]
        decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
        self.assertEqual(decision.state, "ACTIVE")
        self.assertFalse(decision.launch)
        self.assertEqual(self.harness.spawn_calls, [])

    def test_unowned_census_hit_inside_span_holds_without_kill(self) -> None:
        plan = self.make_plan(t0=self.base.timestamp() + 10 * 60)
        self.harness.census = wd.CensusObservation(False, 0, "222 unowned", "")
        self.harness.processes.rows = [wd.ProcessInfo(222, 1, "u", "unowned")]
        decision = wd.decide(self.harness.storage, self.harness.deps, wd.initial_state())
        self.assertEqual(decision.state, "HOLD_CENSUS")
        self.assertFalse(decision.launch)
        self.assertEqual(self.harness.processes.signals, [])
        self.assertTrue(wd.plan_span_active(plan, self.base.timestamp(), self.harness.storage))

    def test_clock_skew_enters_clock_uncertain_and_needs_two_sane_samples(self) -> None:
        state = wd.initial_state()
        state["last_clock"] = {
            "epoch_s": self.base.timestamp() - 10,
            "monotonic": self.harness.clock.mono - 100,
        }
        self.assertEqual(wd.decide(self.harness.storage, self.harness.deps, state).state, "CLOCK_UNCERTAIN")
        state["state"] = "CLOCK_UNCERTAIN"
        self.harness.clock.wall += dt.timedelta(seconds=60)
        self.harness.clock.mono += 60
        self.assertEqual(wd.decide(self.harness.storage, self.harness.deps, state).state, "CLOCK_UNCERTAIN")
        self.harness.clock.wall += dt.timedelta(seconds=60)
        self.harness.clock.mono += 60
        self.assertEqual(wd.decide(self.harness.storage, self.harness.deps, state).state, "LAUNCHING")


class SupervisorTests(WatchdogTestCase):
    def test_supervisor_poll_is_exactly_ten_seconds(self) -> None:
        self.assertEqual(wd.SUPERVISOR_POLL_S, 10)

    def test_resident_loop_hits_term_to_kill_deadline(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        self.harness.clock.wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.TERM_LEAD_S, tz=self.local_tz
        )

        def advance_clock(seconds: float) -> None:
            self.harness.clock.wall += dt.timedelta(seconds=seconds)
            self.harness.clock.mono += seconds

        self.harness.deps.sleep = advance_clock
        supervisor.run()

        events = [
            json.loads(line)
            for line in (self.harness.storage.root / "events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        signal_events = [event for event in events if event["kind"] == "signal"]
        self.assertEqual(
            [event["signal"] for event in signal_events],
            ["SIGTERM", "SIGKILL"],
        )
        self.assertEqual(
            signal_events[1]["epoch_s"] - signal_events[0]["epoch_s"],
            wd.STOP_TERM_GRACE_S,
        )

    def test_notice_ack_is_consumed_before_child_exit(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        supervisor.state["notice_pending"] = [{"id": "transition-1-usage_backoff"}]
        (self.harness.storage.root / "notice.ack").write_text(
            json.dumps({"activation_id": "activation-a"}), encoding="utf-8"
        )
        self.harness.child.exit_code = 0

        self.assertFalse(supervisor.step())
        self.assertEqual(supervisor.state["notice_pending"], [])
        self.assertFalse((self.harness.storage.root / "notice.ack").exists())
        persisted = json.loads(
            (self.harness.storage.root / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(persisted["notice_pending"], [])

    def test_sleeping_remote_probe_cannot_delay_plan_term_or_kill(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        probe_started = threading.Event()

        def sleeping_probe() -> wd.StopObservation:
            probe_started.set()
            time.sleep(30)
            return wd.StopObservation("CLEAR", "late clear")

        self.harness.deps.git_probe = sleeping_probe
        first_wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.REQUEST_LEAD_S - 1, tz=self.local_tz
        )
        self.harness.clock.wall = first_wall
        self.assertTrue(supervisor.step())
        self.assertTrue(probe_started.wait(1), "resident must start the probe asynchronously")

        started = time.monotonic()
        term_wall = dt.datetime.fromtimestamp(plan.t0_epoch_s - wd.TERM_LEAD_S, tz=self.local_tz)
        self.harness.clock.mono += (term_wall - first_wall).total_seconds()
        self.harness.clock.wall = term_wall
        self.assertTrue(supervisor.step())
        self.assertIn((100, signal.SIGTERM), self.harness.processes.signals)

        kill_wall = dt.datetime.fromtimestamp(plan.t0_epoch_s - wd.KILL_LEAD_S, tz=self.local_tz)
        self.harness.clock.mono += (kill_wall - term_wall).total_seconds()
        self.harness.clock.wall = kill_wall
        self.assertFalse(supervisor.step())
        self.assertIn((100, signal.SIGKILL), self.harness.processes.signals)
        self.assertLess(time.monotonic() - started, 10)

    def test_clock_uncertain_resident_drains_with_monotonic_deadlines(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        supervisor.state["last_clock"] = {
            "epoch_s": self.base.timestamp() - 10,
            "monotonic": self.harness.clock.mono - 100,
        }

        self.assertTrue(supervisor.step())
        self.assertEqual(supervisor.state["state"], "CLOCK_UNCERTAIN")
        self.assertTrue(supervisor.state["clock_drain"])
        self.assertTrue((self.harness.storage.root / "standdown.request").exists())
        self.assertEqual(self.harness.processes.signals, [])

        self.harness.clock.wall += dt.timedelta(seconds=wd.STOP_COOPERATIVE_S)
        self.harness.clock.mono += wd.STOP_COOPERATIVE_S
        self.assertTrue(supervisor.step())
        self.assertIn((100, signal.SIGTERM), self.harness.processes.signals)

        self.harness.clock.wall += dt.timedelta(seconds=wd.STOP_TERM_GRACE_S)
        self.harness.clock.mono += wd.STOP_TERM_GRACE_S
        self.assertFalse(supervisor.step())
        self.assertIn((100, signal.SIGKILL), self.harness.processes.signals)

    def test_cooperative_exit_after_request_never_signals(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        self.harness.clock.wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.REQUEST_LEAD_S, tz=self.local_tz
        )
        self.assertTrue(supervisor.step())
        self.assertTrue((self.harness.storage.root / "standdown.request").exists())
        self.harness.child.exit_code = 0
        self.harness.clock.wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.TERM_LEAD_S, tz=self.local_tz
        )
        self.assertFalse(supervisor.step())
        self.assertEqual(self.harness.processes.signals, [])
        self.assertEqual(supervisor.state["state"], "FENCED")

    def test_ignored_request_gets_term_then_kill_and_census(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        self.harness.clock.wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.REQUEST_LEAD_S, tz=self.local_tz
        )
        self.assertTrue(supervisor.step())
        self.assertTrue(
            (self.harness.storage.root / "standdown.request").exists(),
            "ignored-session enforcement must still begin with the cooperative request",
        )
        term_wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.TERM_LEAD_S, tz=self.local_tz
        )
        self.harness.clock.mono += (term_wall - self.harness.clock.wall).total_seconds()
        self.harness.clock.wall = term_wall
        self.assertTrue(supervisor.step())
        self.assertIn((100, signal.SIGTERM), self.harness.processes.signals)
        kill_wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.KILL_LEAD_S, tz=self.local_tz
        )
        self.harness.clock.mono += (kill_wall - self.harness.clock.wall).total_seconds()
        self.harness.clock.wall = kill_wall
        self.assertFalse(supervisor.step())
        self.assertIn((100, signal.SIGKILL), self.harness.processes.signals)
        self.assertEqual(self.harness.census_calls, 1, "KILL must be followed by production census")
        self.assertEqual(supervisor.state["state"], "FENCED")
        self.assertEqual([item["kind"] for item in supervisor.state["notice_pending"]], ["forced_standdown"])

    def test_forced_hold_polls_child_to_reap_defunct_owner(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        process_table = self.harness.processes
        process_table.rows = [wd.ProcessInfo(100, 99, "token-a", "session <defunct>")]

        class ReapingChild:
            pid = 100

            def __init__(self) -> None:
                self.poll_calls = 0

            def poll(self) -> int | None:
                self.poll_calls += 1
                process_table.rows = []
                return -signal.SIGKILL

        child = ReapingChild()
        supervisor.child = child
        self.assertFalse(supervisor._forced_hold(self.base))
        self.assertEqual(child.poll_calls, 1)
        self.assertFalse((self.harness.storage.root / "magistrate.lock").exists())
        self.assertEqual(supervisor.state["state"], "FENCED")

    def test_plan_signal_revalidates_lock_token(self) -> None:
        plan = self.make_plan()
        supervisor = self.supervisor(plan)
        self.harness.processes.rows = [wd.ProcessInfo(100, 99, "reused-token", "unrelated")]
        self.harness.clock.wall = dt.datetime.fromtimestamp(
            plan.t0_epoch_s - wd.TERM_LEAD_S, tz=self.local_tz
        )
        self.assertFalse(supervisor.step())
        self.assertEqual(self.harness.processes.signals, [])
        self.assertFalse((self.harness.storage.root / "magistrate.lock").exists())
        self.assertEqual(supervisor.state["state"], "FENCED")

    def test_process_tree_walk_kills_descendant_that_escaped_pgid(self) -> None:
        table = FakeProcessTable(
            [
                wd.ProcessInfo(100, 1, "a", "root pgid=100"),
                wd.ProcessInfo(200, 100, "b", "child pgid=100"),
                wd.ProcessInfo(300, 200, "c", "escaped pgid=300"),
            ]
        )
        killed = wd.signal_owned_tree(table, 100, signal.SIGKILL)
        self.assertEqual(set(killed), {100, 200, 300})
        self.assertEqual({pid for pid, sig in table.signals if sig == signal.SIGKILL}, {100, 200, 300})
        self.assertEqual(table.signals[-1], (100, signal.SIGKILL), "root must be signalled last")


class BackoffAndEventTests(WatchdogTestCase):
    def test_usage_classification_is_conservative(self) -> None:
        accepted = (
            "Usage limit reached; resets in 2 hours",
            "monthly spend limit",
            "rate limit reached",
            "error type rate_limit",
            "quota exhausted",
            "usage resets at 09:00",
            "session limit resets 12:50am",
            "HTTP 429",
            "You've hit your limit",
        )
        for text in accepted:
            with self.subTest(text=text):
                self.assertEqual(wd.classify_exit(1, text), "usage_exhausted")
        self.assertEqual(wd.classify_exit(0, "usage limit"), "clean")

    def test_real_429_spend_limit_is_usage_exhausted(self) -> None:
        output = (
            "You've hit your monthly spend limit · raise it at "
            "claude.ai/settings/usage?from=cc_cli_limit_message · your session limit "
            "resets 12:50am (America/Los_Angeles) (error type rate_limit, HTTP 429, "
            "request id req_011CefuL7Ahwwne6SEyTBqDt, model sent to the API: "
            "claude-fable-5-1)"
        )
        self.assertEqual(wd.classify_exit(1, output), "usage_exhausted")

    def test_unknown_error_is_generic_error(self) -> None:
        self.assertEqual(wd.classify_exit(7, "unknown server error"), "generic_error")

    def test_usage_backoff_ladder_and_activation_jitter(self) -> None:
        state = wd.initial_state()
        state.update({"state": "ACTIVE", "activation_id": "stable-activation"})
        jitter = wd.jitter_for_activation("stable-activation")
        expected_ladder = (900, 1800, 3600, 7200, 7200)
        self.assertEqual(wd.USAGE_BACKOFF_S, expected_ladder)
        observed: list[int] = []
        mono = 100.0
        for index in range(5):
            wd.apply_backoff(
                self.harness.storage,
                state,
                self.base,
                mono,
                "usage_exhausted",
                "usage limit reached",
            )
            observed.append(round(float(state["next_eligible_monotonic"]) - mono))
            mono += observed[-1]
        self.assertEqual(observed, [base + jitter for base in expected_ladder])
        self.assertEqual(len(state["notice_pending"]), 1, "unchanged backoff transition queues one notice")

    def test_backoff_never_overrides_new_plan_span(self) -> None:
        self.make_plan(t0=self.base.timestamp() + 10 * 60)
        state = wd.initial_state()
        state["next_eligible_monotonic"] = self.harness.clock.mono + 99999
        decision = wd.decide(self.harness.storage, self.harness.deps, state)
        self.assertEqual(decision.state, "FENCED")

    def test_one_event_per_transition(self) -> None:
        state = wd.initial_state()
        wd.transition(self.harness.storage, state, "FENCED", "first", self.base)
        wd.transition(self.harness.storage, state, "FENCED", "same state", self.base)
        events = (self.harness.storage.root / "events.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(events), 1)
        self.assertEqual(json.loads(events[0])["to"], "FENCED")

    def test_notice_ack_clears_only_the_current_activation(self) -> None:
        state = wd.initial_state()
        state.update(
            {
                "activation_id": "activation-a",
                "notice_pending": [{"id": "transition-1-usage_backoff"}],
            }
        )
        self.harness.storage.mkdir(self.harness.storage.root)
        (self.harness.storage.root / "notice.ack").write_text(
            json.dumps({"activation_id": "other"}), encoding="utf-8"
        )
        self.assertFalse(wd.consume_notice_ack(self.harness.storage, state, self.base))
        self.assertEqual(len(state["notice_pending"]), 1)
        (self.harness.storage.root / "notice.ack").write_text(
            json.dumps({"activation_id": "activation-a"}), encoding="utf-8"
        )
        self.assertTrue(wd.consume_notice_ack(self.harness.storage, state, self.base))
        self.assertEqual(state["notice_pending"], [])
        self.assertFalse((self.harness.storage.root / "notice.ack").exists())

    def test_missing_binary_enters_generic_backoff_without_spawn(self) -> None:
        state = wd.initial_state()
        state.update({"state": "LAUNCHING", "activation_id": "a"})
        supervisor = wd.start_session_guarded(
            self.harness.storage,
            self.harness.deps,
            state,
            binary_path=self.temp / "missing-session-bin",
        )
        self.assertIsNone(supervisor)
        self.assertEqual(state["state"], "BACKOFF")
        self.assertEqual(self.harness.spawn_calls, [])


class ContractTests(WatchdogTestCase):
    def test_handoff_inventory_separates_owned_tree_and_unclassified_orphans(self) -> None:
        table = FakeProcessTable(
            [
                wd.ProcessInfo(900, 800, "caller", "python magistrate_watchdog.py handoff-inventory"),
                wd.ProcessInfo(800, 100, "shell", "/bin/zsh -c inventory"),
                wd.ProcessInfo(100, 50, "twin", "/Users/edr/.local/bin/claude --resume magistrate"),
                wd.ProcessInfo(110, 100, "daemon", "/Users/edr/.local/bin/claude daemon run"),
                wd.ProcessInfo(111, 110, "host", "claude bg-pty-host /tmp/spare.pty.sock"),
                wd.ProcessInfo(112, 111, "spare", "claude bg-spare /tmp/spare.claim.sock"),
                wd.ProcessInfo(200, 1, "orphan-host", "/Applications/ClaudeCode.app/Contents/MacOS/claude --bg-pty-host /tmp/orphan.sock"),
                wd.ProcessInfo(201, 200, "orphan-child", "claude bg-spare /tmp/orphan.claim.sock"),
                wd.ProcessInfo(300, 1, "snapshot", "/bin/zsh -c source /Users/edr/.claude/shell-snapshots/snapshot-zsh.sh"),
                wd.ProcessInfo(301, 300, "snapshot-child", "/usr/bin/tail -f monitor.log"),
                wd.ProcessInfo(400, 1, "unowned", "codex exec unrelated"),
                wd.ProcessInfo(500, 1, "other-claude", "/Users/edr/.local/bin/claude --resume unrelated"),
            ]
        )

        inventory = wd.handoff_inventory(table.snapshot(), 900)

        self.assertEqual(inventory["interactive_pid"], 100)
        self.assertEqual(
            {row["pid"] for row in inventory["owned"]},
            {100, 110, 111, 112},
        )
        self.assertEqual(
            {row["pid"] for row in inventory["unclassified_candidates"]},
            {200, 201, 300, 301},
        )
        listed = {
            row["pid"]
            for key in ("owned", "unclassified_candidates")
            for row in inventory[key]
        }
        self.assertNotIn(400, listed)
        self.assertNotIn(500, listed)
        self.assertEqual(table.signals, [], "inventory is read-only")

        adopted = wd.handoff_inventory(
            table.snapshot(), 900, adoptions=((200, "orphan-host"),)
        )
        self.assertEqual(
            {row["pid"] for row in adopted["owned"]},
            {100, 110, 111, 112, 200, 201},
        )
        self.assertEqual(
            {row["pid"] for row in adopted["unclassified_candidates"]},
            {300, 301},
        )
        self.assertEqual(
            "explicit_adoption",
            next(row for row in adopted["owned"] if row["pid"] == 200)["provenance"],
        )
        self.assertEqual(
            [{"pid": 200, "start_time": "orphan-host"}],
            adopted["explicit_adoptions"],
        )

    def test_handoff_inventory_rejects_headless_print_session_as_interactive(self) -> None:
        rows = [
            wd.ProcessInfo(900, 100, "caller", "python magistrate_watchdog.py handoff-inventory"),
            wd.ProcessInfo(100, 1, "headless", "claude -p prompt --output-format stream-json"),
        ]
        with self.assertRaisesRegex(RuntimeError, "Terminal-hosted interactive"):
            wd.handoff_inventory(rows, 900)

    def test_dry_run_injects_filesystem_and_spawn_but_suppresses_both(self) -> None:
        dry = wd.Storage(self.temp / "dry" / "magistrate", dry_run=True)
        decision = wd.tick(dry, self.harness.deps, dry_run=True)
        self.assertEqual(decision.state, "LAUNCHING")
        self.assertTrue(any("state.json" in action for action in dry.would_write))
        self.assertFalse(dry.root.exists())
        self.assertEqual(self.harness.spawn_calls, [])

    def test_storage_refuses_every_write_outside_custody(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "outside custody root"):
            self.harness.storage.atomic_bytes(self.temp / "repo" / "bad", b"bad")

    def test_launchd_program_argv_is_census_safe_and_has_no_keepalive(self) -> None:
        template = (
            Path(__file__).resolve().parents[1]
            / "configs"
            / "launchd"
            / "com.joulewise.magistrate.plist.template"
        ).read_text(encoding="utf-8")
        program = template.split("<key>ProgramArguments</key>", 1)[1].split("</array>", 1)[0].lower()
        for forbidden in ("claude", "codex", "t3"):
            self.assertNotIn(forbidden, program)
        self.assertNotIn("KeepAlive", template)
        self.assertIn("<integer>300</integer>", template)
        self.assertIn("<true/>", template)

    def test_session_spawn_uses_print_stream_shape_symlink_and_canonical_cwd(self) -> None:
        target = self.temp / "versions" / "2.1.260"
        target.parent.mkdir()
        target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        target.chmod(0o755)
        link = self.temp / "bin" / "session"
        link.parent.mkdir()
        link.symlink_to(target)
        self.harness.processes.rows = [wd.ProcessInfo(100, 1, "child-token", "session")]
        state = wd.initial_state()
        state.update({"state": "LAUNCHING", "activation_id": "activation-a"})
        wd.start_session(self.harness.storage, self.harness.deps, state, binary_path=link)
        argv, cwd, stdout, stderr = self.harness.spawn_calls[0]
        self.assertEqual(argv[0], str(link))
        self.assertEqual(argv[1], "-p")
        self.assertNotIn("--bg", argv)
        self.assertEqual(argv[argv.index("--output-format") + 1], "stream-json")
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "auto")
        self.assertEqual(cwd, wd.CANONICAL_REPO)
        self.assertEqual(stdout.parent.parent, self.harness.storage.root / "attempts")
        self.assertEqual(stderr.parent.parent, self.harness.storage.root / "attempts")
        lock = json.loads((self.harness.storage.root / "magistrate.lock").read_text(encoding="utf-8"))
        self.assertEqual(lock["binary_symlink"], str(link))
        self.assertNotIn(str(target), json.dumps(lock))

    def test_first_install_adopts_current_tree_and_arming_stays_outside_charter(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        installer = (repo / "scripts" / "install_magistrate_watchdog.sh").read_text(encoding="utf-8")
        prompt = (repo / "docs" / "process" / "MAGISTRATE_RELAUNCH_PROMPT.md").read_text(encoding="utf-8")
        self.assertIn('"first_install_adoption": True', installer)
        self.assertIn("os.O_EXCL", installer)
        self.assertIn("must be run by the current magistrate session", installer)
        self.assertIn("Never arm or re-arm a night except", prompt)
        self.assertIn("Ed's NO always overrides", prompt)

    def test_prompt_has_at_most_twenty_five_lines_and_required_order(self) -> None:
        prompt = (
            Path(__file__).resolve().parents[1] / "docs" / "process" / "MAGISTRATE_RELAUNCH_PROMPT.md"
        ).read_text(encoding="utf-8")
        self.assertLessEqual(len(prompt.splitlines()), 25)
        self.assertLess(prompt.index("First act"), prompt.index("Email Ed"))
        self.assertIn("notice_pending", prompt)
        self.assertIn("exit within nine minutes", prompt)
        self.assertIn("@@FENCED_CHECKOUTS@@", prompt)
        self.assertIn("(plan_id, root, head)", prompt)
        self.assertIn("never fast-forward, pull, checkout, or otherwise move", prompt)
        self.assertIn("requires a re-arm with a re-pinned plan", prompt)
        self.assertIn("Do not ratify or amend any process rule", prompt)
        self.assertIn("cold gate or Ed", prompt)
        self.assertIn("Arming a night obligates this session to end its loop", prompt)
        self.assertIn("under a v2 plan", prompt)
        self.assertIn("installed from that plan's `measurement_root`", prompt)

    def test_documented_example_plans_use_the_production_writer(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        text = (repo / "docs" / "process" / "MAGISTRATE_WATCHDOG.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("from joulewise.night_plan_writer import write_night_plan", text)
        self.assertNotIn(".write_text(json.dumps(plan)", text)
        python_blocks = re.findall(r"<<'PY'.*?\n(.*?)\n\s*PY$", text, re.DOTALL | re.MULTILINE)
        self.assertGreaterEqual(len(python_blocks), 4)
        for index, block in enumerate(python_blocks):
            with self.subTest(block=index):
                compile(textwrap.dedent(block), f"MAGISTRATE_WATCHDOG.md:{index}", "exec")
        plan = self.make_plan(name="writer-contract")
        self.assertEqual(plan, wd.NightPlan.from_mapping(night_plan_mapping(plan)))

    def test_install_handoff_is_ordered_and_measurement_checkout_owned(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        watchdog = (repo / "docs" / "process" / "MAGISTRATE_WATCHDOG.md").read_text(
            encoding="utf-8"
        )
        ordered = (
            "stop every background task",
            'mv "$HOME/night-custody/$name" "$HOME/night-custody/retired-v1/$name"',
            "magistrate_watchdog.py handoff-inventory",
            "install_magistrate_watchdog.sh --install",
            "signals only `owned`",
            "next five-minute tick",
        )
        positions = [watchdog.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("never signals an unclassified or census PID", watchdog)

        handback = (repo / "docs" / "process" / "NIGHT_HANDBACK.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("For every v2 plan", handback)
        self.assertIn("FROM", handback)
        self.assertIn("plan's `measurement_root`", handback)


if __name__ == "__main__":
    unittest.main()
