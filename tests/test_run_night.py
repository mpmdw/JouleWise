"""Focused driver tests against the real night-gate module."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import plistlib
import subprocess
import sys
import tempfile
import time
import types
import unittest
from datetime import datetime
from dataclasses import replace
from pathlib import Path
from unittest import mock

from joulewise.measurement_liveness import Identity
from joulewise import night_gate
from joulewise.night_plan_writer import write_night_plan
from tests.git_fixture import init_git_fixture


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_night.py"
HEAD = "f" * 40
BOOT_UUID = "12345678-1234-5678-9234-567812345678"


def _probe(
    argv: tuple[str, ...],
    *,
    exit_code: int = 0,
    stdout: str = "",
    stderr: str = "",
    monotonic_ns: int = 10,
) -> night_gate.ProbeResult:
    return night_gate.ProbeResult(argv, exit_code, stdout, stderr, monotonic_ns)


def _green_results() -> dict[tuple[str, ...], night_gate.ProbeResult]:
    return {
        night_gate.HID_IDLE_ARGV: _probe(night_gate.HID_IDLE_ARGV, stdout="0\n"),
        night_gate.PMSET_BATT_ARGV: _probe(
            night_gate.PMSET_BATT_ARGV, stdout="Now drawing from 'AC Power'\n"
        ),
        night_gate.PMSET_GENERAL_ARGV: _probe(
            night_gate.PMSET_GENERAL_ARGV,
            stdout="System-wide power settings:\n displaysleep 0\n sleep 0\n",
        ),
        night_gate.LOAD_AVG_ARGV: _probe(
            night_gate.LOAD_AVG_ARGV, stdout="{ 0.75 0.63 0.58 }\n"
        ),
        night_gate.THERMAL_ARGV: _probe(
            night_gate.THERMAL_ARGV,
            stdout="Note: No thermal warning level has been recorded\n",
        ),
        night_gate.BOOT_SESSION_ARGV: _probe(
            night_gate.BOOT_SESSION_ARGV, stdout=BOOT_UUID + "\n"
        ),
    }


def _init_git_repo(root: Path) -> str:
    root.mkdir(parents=True)
    init_git_fixture(root, "-q")
    marker = root / "measurement.txt"
    marker.write_text("initial\n", encoding="utf-8")
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", marker.name], check=True)
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=JouleWise Test",
            "-c",
            "user.email=joulewise-test@example.invalid",
            "commit",
            "-qm",
            "initial",
        ],
        check=True,
    )
    return subprocess.check_output(
        ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


class ProbeSource:
    def __init__(self, now_epoch_s: float) -> None:
        self.now_epoch_s = now_epoch_s
        self.results = _green_results()
        self.census_responses: list[night_gate.ProbeResult] = []
        self.monotonic_calls = 0

    def run(self, argv: tuple[str, ...]) -> night_gate.ProbeResult:
        if argv == night_gate.AGENT_CENSUS_ARGV:
            if self.census_responses:
                return self.census_responses.pop(0)
            return _probe(argv, exit_code=1)
        return self.results[argv]

    def monotonic_ns(self) -> int:
        self.monotonic_calls += 1
        return 99_000 + self.monotonic_calls

    def probes(self) -> night_gate.Probes:
        return night_gate.Probes(
            run=self.run,
            now_epoch_s=lambda: self.now_epoch_s,
            monotonic_ns=self.monotonic_ns,
            read_text=lambda path: Path(path).read_text(encoding="utf-8"),
            checkout_head=lambda: HEAD,
            measurement_head=lambda _root: HEAD,
        )


def _load_driver(script_path: Path = SCRIPT_PATH, module_name: str = "run_night_test_module"):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeProcess:
    def __init__(self, argv, return_code: int = 0, running_once: bool = False) -> None:
        self.argv = argv
        self.return_code = return_code
        self.running_once = running_once
        self.pid = 4242
        self.poll_count = 0

    def poll(self):
        self.poll_count += 1
        if self.running_once and self.poll_count == 1:
            return None
        return self.return_code

    def wait(self, timeout=None):
        return self.return_code


class UnkillableProcess(FakeProcess):
    def __init__(self, argv) -> None:
        super().__init__(argv)
        self.pid = 4343

    def poll(self):
        return None

    def wait(self, timeout=None):
        raise subprocess.TimeoutExpired(self.argv, timeout)


class NightDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = _load_driver()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        identity_patch = mock.patch.object(
            self.driver, "observe_identity", return_value=Identity("LIVE", "Tue Sep 8 01:02:03 2026")
        )
        self.identity_mock = identity_patch.start()
        self.addCleanup(identity_patch.stop)
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.chain = self.root / "chain.zsh"
        self.chain.write_text("echo chain\n", encoding="utf-8")
        self.sidecar = self.root / "chain.zsh.sha256"
        # GNU shasum form, exactly what `gen_g2_phase_d.py --emit-chain` writes;
        # both the gate and the driver must read it.
        self.sidecar.write_text(
            hashlib.sha256(self.chain.read_bytes()).hexdigest() + "  chain.zsh\n",
            encoding="utf-8",
        )
        self.registration = self.root / "registration.json"
        self.registration.write_text('{"registered":true}\n', encoding="utf-8")
        self.t0_epoch_s = datetime(2026, 9, 2, 1, 0).timestamp()
        self.source = ProbeSource(self.t0_epoch_s + 1)
        self.plan_path = self.root / "plan.json"
        self._write_plan()
        self.courier = self.root / "claude"
        self.courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        self.courier.chmod(0o755)
        self.registration_hash_patch = mock.patch.object(
            night_gate,
            "D166_REGISTRATION_SHA256",
            hashlib.sha256(self.registration.read_bytes()).hexdigest(),
        )
        self.registration_hash_patch.start()
        self.real_make_probes = self.driver.make_probes
        self.probes_patch = mock.patch.object(
            self.driver, "make_probes", return_value=self.source.probes()
        )
        self.probes_mock = self.probes_patch.start()
        self.real_resolve_courier_bin = self.driver._resolve_courier_bin
        self.resolve_patch = mock.patch.object(
            self.driver,
            "_resolve_courier_bin",
            return_value=(self.courier, None, None),
        )
        self.resolve_mock = self.resolve_patch.start()
        self.real_durable_record = self.driver._durable_record
        self.driver._durable_record = mock.Mock()
        self.real_run_courier = self.driver.run_courier
        self.sent_outcome = {
            "attempted": 1,
            "sent": True,
            "heartbeat_seen": True,
            "last_error": None,
        }
        self.driver.run_courier = mock.Mock(return_value=self.sent_outcome)
        self.popen_kwargs = []

    def tearDown(self) -> None:
        self.probes_patch.stop()
        self.resolve_patch.stop()
        self.registration_hash_patch.stop()
        self.temporary.cleanup()

    def _write_plan(
        self,
        *,
        t0_epoch_s: float | None = None,
        window_max_s: int = 60,
        receipt_class: str = "DIAGNOSTIC_NO_PACK",
    ) -> None:
        t0 = self.t0_epoch_s if t0_epoch_s is None else t0_epoch_s
        write_night_plan(
            self.plan_path,
            night_gate.NightPlan(
                plan_id="night-plan",
                receipt_class=receipt_class,
                t0_epoch_s=t0,
                window_max_s=window_max_s,
                authored_epoch_s=t0 - 1,
                repo_head=HEAD,
                measurement_root=str(self.root),
                measurement_head=HEAD,
                chain_path=str(self.chain),
                chain_sha256_path=str(self.sidecar),
                custody_root=str(self.custody),
                registration_path=str(self.registration),
            ),
        )

    def _popen_recorder(self, return_code: int = 0, running_once: bool = False):
        calls = []

        def spawn(argv, *args, **kwargs):
            calls.append(argv)
            self.popen_kwargs.append(kwargs)
            return FakeProcess(argv, return_code, running_once)

        return calls, spawn

    def _run_night(self, *, return_code: int = 0, rehearsal: bool = False):
        calls, spawn = self._popen_recorder(return_code=return_code)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            exit_code = self.driver.run_night(self.plan_path, rehearsal=rehearsal)
        return exit_code, calls

    def test_refusal_writes_receipt_and_refusal_without_spawning_chain(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n")
        ]
        exit_code, calls = self._run_night()
        night = self.custody / "night"
        self.assertEqual(exit_code, 3)
        self.assertTrue((night / "receipt.json").is_file())
        self.assertTrue((night / "refusal.json").is_file())
        self.assertEqual(calls, [])

    def test_go_spawns_chain_once_even_if_the_chain_fails(self) -> None:
        exit_code, calls = self._run_night(return_code=17)
        self.assertEqual(exit_code, 5)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        night = self.custody / "night"
        result = json.loads((night / "result.json").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(result["chain_exit_code"], 17)
        self.assertEqual(exited["exit_code"], 17)
        self.assertIn("epoch_s", exited)
        self.assertIn("monotonic_ns", exited)
        self.assertTrue(self.popen_kwargs[0]["start_new_session"])

    def test_gate_refusal_log_includes_reason_and_bounded_single_line_detail(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\nsecond\r\n" + "x" * 250)
        ]
        exit_code, calls = self._run_night()
        self.assertEqual(3, exit_code)
        self.assertEqual([], calls)
        receipt = json.loads((self.custody / "night" / "receipt.json").read_text())
        refusal = receipt["refusal"]
        expected_detail = " ".join(refusal["detail"].splitlines())[:200]
        self.assertEqual(200, len(expected_detail))
        messages = [
            line.split(" ", 1)[1]
            for line in (self.custody / "night.log").read_text().splitlines()
        ]
        self.assertEqual(
            [f"night gate verdict=REFUSED reason={refusal['reason']} detail={expected_detail}"],
            [message for message in messages if message.startswith("night gate verdict=")],
        )

    def test_non_refused_gate_log_keeps_exact_verdict_form(self) -> None:
        self._run_night()
        messages = [
            line.split(" ", 1)[1]
            for line in (self.custody / "night.log").read_text().splitlines()
        ]
        self.assertEqual(["night gate verdict=GO"],
                         [message for message in messages if message.startswith("night gate verdict=")])

    def test_stub_without_chain_files_logs_rehearsal_only(self) -> None:
        self._write_plan(receipt_class="REHEARSAL_STUB")
        self.chain.unlink()
        self.sidecar.unlink()
        exit_code, calls = self._run_night()
        self.assertEqual(self.driver.EXIT_REFUSED, exit_code)
        self.assertEqual([["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]], calls)
        receipt = json.loads((self.custody / "night" / "receipt.json").read_text())
        self.assertEqual("REHEARSAL_ONLY", receipt["verdict"])
        messages = [
            line.split(" ", 1)[1]
            for line in (self.custody / "night.log").read_text().splitlines()
        ]
        self.assertEqual(["night gate verdict=REHEARSAL_ONLY"],
                         [message for message in messages if message.startswith("night gate verdict=")])

    def test_counterfactual_inherited_coordinates_override_parsed_night_plan(self) -> None:
        parsed = night_gate.NightPlan.from_mapping(json.loads(self.plan_path.read_text()))
        parsed = replace(
            parsed,
            measurement_root=str(self.root / "measurement with spaces"),
            measurement_head="a" * 40,
        )
        write_night_plan(self.plan_path, parsed)
        self.probes_mock.return_value = replace(
            self.source.probes(), measurement_head=lambda _root: parsed.measurement_head
        )
        inherited = {
            "NIGHT_PLAN_ID": "stale-plan",
            "MEASUREMENT_ROOT": "/stale/measurement",
            "MEASUREMENT_HEAD": "b" * 40,
            "PY": "/stale/development/python",
        }
        with mock.patch.dict(os.environ, inherited):
            exit_code, calls = self._run_night()
            # The handoff changes only the child's environment.
            self.assertEqual({key: os.environ[key] for key in inherited}, inherited)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        environment = self.popen_kwargs[0]["env"]
        self.assertEqual(
            {key: environment.get(key) for key in inherited},
            {
                "NIGHT_PLAN_ID": parsed.plan_id,
                "MEASUREMENT_ROOT": parsed.measurement_root,
                "MEASUREMENT_HEAD": parsed.measurement_head,
                "PY": parsed.measurement_root + "/.venv/bin/python",
            },
        )

    def test_plan_supplies_coordinates_when_parent_exports_are_absent(self) -> None:
        keys = ("MEASUREMENT_ROOT", "MEASUREMENT_HEAD", "PY")
        parent = {key: value for key, value in os.environ.items() if key not in keys}
        with mock.patch.dict(os.environ, parent, clear=True):
            exit_code, calls = self._run_night()
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        environment = self.popen_kwargs[0]["env"]
        self.assertEqual(
            [environment.get(key) for key in keys],
            [str(self.root), HEAD, str(self.root) + "/.venv/bin/python"],
        )

    def test_chain_spawn_failure_records_refusal_and_finishes_reporting(self) -> None:
        self.driver._durable_record = self.real_durable_record
        run_argv = []

        def run_command(argv, **kwargs):
            run_argv.append(list(argv))
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        try:
            with mock.patch.object(
                self.driver.subprocess,
                "Popen",
                side_effect=FileNotFoundError("chain executable missing"),
            ), mock.patch.object(
                self.driver.subprocess, "run", side_effect=run_command
            ):
                exit_code = self.driver.run_night(self.plan_path)
        except FileNotFoundError as error:
            self.fail(f"chain launch failure escaped instead of becoming a refusal: {error}")

        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        started = json.loads((night / "chain.started").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        pushes = [argv for argv in run_argv if "push" in argv]
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["chain_launch_failed"]
        )
        self.assertEqual(self.driver.validate_refusal(refusal), [])
        self.assertIsNone(started["pid"])
        self.assertIsNone(started["pgid"])
        self.assertEqual(
            started["launch_error"],
            "FileNotFoundError: chain executable missing",
        )
        self.assertIsNone(exited["exit_code"])
        self.assertIs(exited["launch_failed"], True)
        self.driver.run_courier.assert_called_once()
        self.assertEqual(len(pushes), 2)

    def test_chain_identity_probe_follows_complete_closed_marker(self) -> None:
        from joulewise.measurement_liveness import census
        night = self.root / "claim-test" / "night"
        night.mkdir(parents=True)
        descriptor = self.driver._claim_chain_start(night)
        process = types.SimpleNamespace(pid=4242)
        class DriverKilled(BaseException):
            pass
        def killed_during_probe(pid):
            record = json.loads((night / "chain.started").read_text())
            self.assertEqual(set(record), {"pid", "pgid", "epoch_s"})
            self.assertEqual(record["pid"], pid)
            self.assertEqual(self.driver._read_started_pgid(night / "chain.started"), pid)
            with self.assertRaises(OSError):
                os.fstat(descriptor)
            raise DriverKilled()
        with mock.patch.object(self.driver, "observe_identity", side_effect=killed_during_probe):
            with self.assertRaises(DriverKilled):
                self.driver._complete_chain_start(descriptor, process, night)
        result = census(parents=[night.parent.parent], observer=lambda pid: Identity("DEAD"))
        self.assertFalse(result.clear)
        self.assertIn("indeterminate", result.refusals[0])
        self.assertFalse((night / "chain.exited").exists())
        self.assertEqual(self.driver._read_started_pgid(night / "chain.started"), 4242)

    def test_chain_identity_is_added_by_atomic_replace(self) -> None:
        night = self.root / "atomic-test"
        night.mkdir()
        descriptor = self.driver._claim_chain_start(night)
        process = types.SimpleNamespace(pid=4242)
        replace = os.replace
        def inspect_replace(source, target):
            self.assertEqual(source, night / "chain.started.tmp")
            self.assertEqual(target, night / "chain.started")
            before = json.loads(target.read_text())
            after = json.loads(source.read_text())
            self.assertEqual(set(before), {"pid", "pgid", "epoch_s"})
            self.assertEqual({k: after[k] for k in before}, before)
            self.assertEqual(after["start_time"], "Tue Sep 8 01:02:03 2026")
            replace(source, target)
        with mock.patch.object(self.driver.os, "replace", side_effect=inspect_replace) as swap:
            self.assertEqual(self.driver._complete_chain_start(descriptor, process, night), 4242)
        swap.assert_called_once()
        self.assertFalse((night / "chain.started.tmp").exists())
        self.assertEqual(json.loads((night / "chain.started").read_text())["start_time"],
                         "Tue Sep 8 01:02:03 2026")

    def test_chain_claim_prevents_a_second_spawn_after_a_failed_chain(self) -> None:
        calls, spawn = self._popen_recorder(return_code=17)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 5)
            self.assertEqual(self.driver.run_night(self.plan_path), 3)
        night = self.custody / "night"
        claim = json.loads((night / "chain.started").read_text())
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        self.assertEqual(set(claim), {"pid", "pgid", "epoch_s", "start_time"})
        self.assertEqual(claim["start_time"], "Tue Sep 8 01:02:03 2026")
        self.identity_mock.assert_called_once_with(claim["pid"])
        self.assertNotEqual(claim["pid"], os.getpid())
        rerun = list(night.glob("rerun-*.refusal.json"))
        self.assertEqual(len(rerun), 1)
        refusal = json.loads(rerun[0].read_text())
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["record_exists"])

    def test_census_refusal_terminates_group_and_records_abort(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n"),
        ]
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.os, "killpg"
        ) as kill_group, mock.patch.object(self.driver.time, "sleep"):
            self.assertEqual(self.driver.run_night(self.plan_path), 4)
        kill_group.assert_called_once_with(4242, self.driver.signal.SIGTERM)
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["aborted_agent_present"]
        )
        self.assertEqual(exited["exit_code"], 0)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def test_courier_uses_one_launch_three_retries_and_every_backoff(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        calls, spawn = self._popen_recorder(running_once=True)
        sleeps = []
        old_deadline = self.driver.COURIER_DEADLINE_S
        self.driver.COURIER_DEADLINE_S = 0
        try:
            self.driver.run_courier = self.real_run_courier
            with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
                self.driver.os, "killpg"
            ), mock.patch.object(self.driver.time, "sleep", side_effect=sleeps.append):
                outcome = self.driver.run_courier(self.custody, plan, self.courier)
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline
        self.assertFalse(outcome["sent"])
        self.assertEqual(outcome["attempted"], 4)
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [60, 180, 600])
        self.assertEqual(self.driver.COURIER_BACKOFF_S, (60, 180, 600))
        self.assertTrue(all(item["cwd"] == REPO_ROOT for item in self.popen_kwargs))
        self.assertTrue(all(item["start_new_session"] for item in self.popen_kwargs))

    def test_dead_man_skips_when_courier_sent_exists(self) -> None:
        sent = self.custody / "night" / "courier.sent"
        sent.parent.mkdir()
        sent.write_text("sent\n", encoding="utf-8")
        self.assertEqual(self.driver.dead_man(self.plan_path), 0)
        self.driver.run_courier.assert_not_called()

    def test_dead_man_stands_down_immediately_after_t0_on_empty_night(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        entries_before = set(night.iterdir())
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=self.t0_epoch_s + 1
        ), mock.patch.object(self.driver.subprocess, "Popen") as spawn, mock.patch.object(
            self.driver.subprocess, "run"
        ) as run_command, mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(set(night.iterdir()), entries_before)
        self.assertEqual(set(self.custody.iterdir()), {night, self.custody / "night.log"})
        lines = (self.custody / "night.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn(f"completion epoch {int(completion_epoch_s)}; standing down", lines[0])
        spawn.assert_not_called()
        run_command.assert_not_called()
        kill_group.assert_not_called()
        self.resolve_mock.assert_not_called()
        self.driver.run_courier.assert_not_called()
        self.driver._durable_record.assert_not_called()

    def test_dead_man_stands_down_one_second_before_completion_epoch(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        entries_before = set(night.iterdir())
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s - 1
        ), mock.patch.object(self.driver.subprocess, "Popen") as spawn, mock.patch.object(
            self.driver.subprocess, "run"
        ) as run_command, mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertEqual(set(night.iterdir()), entries_before)
        self.assertEqual(set(self.custody.iterdir()), {night, self.custody / "night.log"})
        spawn.assert_not_called()
        run_command.assert_not_called()
        kill_group.assert_not_called()
        self.resolve_mock.assert_not_called()
        self.driver.run_courier.assert_not_called()
        self.driver._durable_record.assert_not_called()

    def test_dead_man_absent_marker_at_completion_epoch_couriers(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        plan = self.driver._load_plan(self.plan_path)
        with mock.patch.object(
            self.driver.time,
            "time",
            return_value=plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S,
        ):
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        self.assertTrue((night / "censuses.jsonl").is_file())
        self.driver.run_courier.assert_called_once()

    def test_dead_man_empty_start_marker_waits_until_completion_epoch(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text("", encoding="utf-8")
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(self.driver.subprocess, "Popen") as spawn, mock.patch.object(
            self.driver.subprocess, "run"
        ) as run_command, mock.patch.object(self.driver.os, "killpg") as kill_group, mock.patch.object(
            self.driver.time, "time", return_value=self.t0_epoch_s + 2
        ):
            early_exit = self.driver.dead_man(self.plan_path)
        self.assertEqual(early_exit, self.driver.EXIT_GO)
        self.assertFalse((night / "chain.exited").exists())
        self.driver.run_courier.assert_not_called()
        spawn.assert_not_called()
        run_command.assert_not_called()
        kill_group.assert_not_called()

        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as completion_kill_group:
            completion_exit = self.driver.dead_man(self.plan_path)
        self.assertEqual(completion_exit, self.driver.EXIT_GO)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertIs(exited["launch_failed"], True)
        self.driver.run_courier.assert_called_once()
        completion_kill_group.assert_not_called()

    def test_dead_man_couriers_after_an_empty_start_marker_without_killpg(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text("", encoding="utf-8")
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertIs(exited["launch_failed"], True)
        self.assertEqual(exited["reaped_by"], "dead-man")
        kill_group.assert_not_called()
        self.driver.run_courier.assert_called_once()

    def test_dead_man_couriers_after_a_null_pgid_marker_without_killpg(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text(
            json.dumps(
                {
                    "pid": None,
                    "pgid": None,
                    "epoch_s": time.time(),
                    "launch_error": "FileNotFoundError: missing",
                }
            ),
            encoding="utf-8",
        )
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        self.assertEqual(exit_code, self.driver.EXIT_GO)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertIs(exited["launch_failed"], True)
        self.assertEqual(exited["reaped_by"], "dead-man")
        kill_group.assert_not_called()
        self.driver.run_courier.assert_called_once()

    def test_overrun_refuses_before_the_gate_or_chain(self) -> None:
        t0_epoch_s = datetime(2026, 9, 2, 6, 50).timestamp()
        self._write_plan(t0_epoch_s=t0_epoch_s, window_max_s=3600)
        self.source.now_epoch_s = t0_epoch_s + 1
        gate_calls = []
        real_evaluate = self.driver.evaluate_night

        def record_evaluate(*args, **kwargs):
            gate_calls.append(args)
            return real_evaluate(*args, **kwargs)

        calls, spawn = self._popen_recorder()
        with mock.patch.object(
            self.driver, "evaluate_night", side_effect=record_evaluate
        ), mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 3)
        refusal = json.loads((self.custody / "night" / "refusal.json").read_text())
        detail = refusal["refusal"]["detail"]
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["plan_overruns_deadman"]
        )
        self.assertIn(f"t0_epoch_s={t0_epoch_s}", detail)
        self.assertIn("window_max_s=3600", detail)
        self.assertIn("deadman_epoch_s=", detail)
        self.assertNotIn("courier_backoff", detail)
        self.assertEqual(gate_calls, [])
        self.assertEqual(calls, [])

    def test_deadman_boundary_refuses_equality_and_allows_one_second_before(self) -> None:
        deadman_epoch_s = self.driver._next_deadman_epoch(self.t0_epoch_s)
        equal_window_s = int(
            deadman_epoch_s - self.t0_epoch_s - self.driver.COURIER_DEADLINE_S
        )
        self.assertEqual(
            self.t0_epoch_s + equal_window_s + self.driver.COURIER_DEADLINE_S,
            deadman_epoch_s,
        )
        self._write_plan(window_max_s=equal_window_s)
        self.source.now_epoch_s = self.t0_epoch_s + 1
        calls, spawn = self._popen_recorder()
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            equal_exit = self.driver.run_night(self.plan_path)
        self.assertEqual(equal_exit, self.driver.EXIT_REFUSED)
        equal_refusal = json.loads(
            (self.custody / "night" / "refusal.json").read_text()
        )
        self.assertEqual(
            equal_refusal["refusal"]["reason"],
            self.driver._CODES["plan_overruns_deadman"],
        )
        self.assertEqual(calls, [])

        earlier_custody = self.root / "earlier-custody"
        earlier_plan = json.loads(self.plan_path.read_text())
        earlier_plan["window_max_s"] = equal_window_s - 1
        earlier_plan["custody_root"] = str(earlier_custody)
        self.plan_path.write_text(json.dumps(earlier_plan), encoding="utf-8")
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            earlier_exit = self.driver.run_night(self.plan_path)
        self.assertEqual(earlier_exit, self.driver.EXIT_GO)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def test_courier_backoffs_do_not_enter_the_overrun_predicate(self) -> None:
        t0_epoch_s = datetime(2026, 9, 2, 6, 45).timestamp()
        self._write_plan(t0_epoch_s=t0_epoch_s, window_max_s=60)
        self.source.now_epoch_s = t0_epoch_s + 1
        exit_code, calls = self._run_night()
        self.assertEqual(exit_code, 0)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def test_rehearsal_refuses_a_non_rehearsal_plan(self) -> None:
        exit_code, calls = self._run_night(rehearsal=True)
        self.assertEqual(exit_code, 3)
        self.assertEqual(calls, [])

    def test_clone_failure_does_not_change_a_go_exit_code(self) -> None:
        self.driver._durable_record = self.real_durable_record
        calls, spawn = self._popen_recorder()
        run_argv = []

        def fail_clone(argv, **kwargs):
            run_argv.append(list(argv))
            if argv[:3] == ["git", "clone", "--depth"]:
                raise OSError("clone unavailable")
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.subprocess, "run", side_effect=fail_clone
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        self.assertEqual(len(calls), 1)
        clones = [
            argv for argv in run_argv if argv[:3] == ["git", "clone", "--depth"]
        ]
        self.assertEqual(len(clones), 2)
        self.assertEqual(clones[0][:4], ["git", "clone", "--depth", "1"])
        self.assertEqual(clones[0][-1], str(self.custody / "results-clone"))

    def test_courier_argv_has_the_reviewed_shape(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        argv = self.driver._courier_argv(self.custody, plan, self.courier)
        self.assertEqual(argv[:2], (str(self.courier), "-p"))
        self.assertEqual(
            argv[-4:],
            ("--output-format", "text", "--allowedTools", self.driver.COURIER_ALLOWED_TOOLS),
        )
        self.assertIn(str(self.custody), argv[2])
        self.assertIn(plan.plan_id, argv[2])
        self.assertIn(str(REPO_ROOT / "docs" / "process" / "NIGHT_HANDBACK.md"), argv[2])
        self.assertIn("may not exist yet", argv[2])

    def test_courier_body_reads_watchdog_age_and_last_decision_directly(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        state_path = self.custody.parent / "magistrate" / "state.json"
        state_path.parent.mkdir()
        state_path.write_text(
            json.dumps({"state": "HOLD_UNSAFE", "reason": "plan malformed"})
            + "\n",
            encoding="utf-8",
        )
        os.utime(state_path, (1_000.0, 1_000.0))

        with mock.patch.object(self.driver.time, "time", return_value=1_901.25):
            argv = self.driver._courier_argv(self.custody, plan, self.courier)

        self.assertIn(f"Watchdog state path: {state_path}", argv[2])
        self.assertIn("Watchdog state age seconds: 901.250", argv[2])
        self.assertIn("Watchdog last decision: HOLD_UNSAFE", argv[2])
        self.assertIn("include these watchdog fields in the email body", argv[2])
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("scripts.magistrate_watchdog", source)
        self.assertNotIn("from scripts import magistrate_watchdog", source)

    def test_launch_agent_template_disables_restart_and_installer_rejects_keepalive(self) -> None:
        template = (
            REPO_ROOT / "configs" / "launchd" / "com.joulewise.night.plist.template"
        ).read_text()
        installer = (REPO_ROOT / "scripts" / "install_night_agent.sh").read_text()
        self.assertIn("com.joulewise.night", template)
        self.assertIn("@@HOUR@@", template)
        self.assertIn("@@MINUTE@@", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.err", template)
        self.assertIn("<key>WorkingDirectory</key>\n  <string>@@REPO@@</string>", template)
        self.assertIn("<key>PATH</key>\n    <string>@@PATH@@</string>", template)
        self.assertIn("@@COURIER_BIN@@", template)
        self.assertNotIn("<key>KeepAlive</key>", template)
        self.assertIn("<key>RunAtLoad</key>\n  <false/>", template)
        self.assertIn('/usr/bin/grep -q "KeepAlive"', installer)
        self.assertIn("DEADMAN_HOUR", installer)
        self.assertIn("DEADMAN_MINUTE", installer)
        self.assertNotIn("<integer>7</integer>", template)
        self.assertNotIn("<integer>7</integer>", installer)
        self.assertEqual(installer.count("sudo"), 0)

    def test_sidecar_digest_accepts_shasum_form_and_refuses_malformed_forms(self) -> None:
        # The seam with the gate: `gen_g2_phase_d.py --emit-chain` writes GNU
        # shasum form; the driver (and the gate) must read it, not bare hex
        # only.  Wrong basename / extra tokens / uppercase / empty refuse.
        digest = "ab" * 32
        self.assertEqual(self.driver._sidecar_digest(f"{digest}  chain.zsh\n", "chain.zsh"), digest)
        self.assertEqual(self.driver._sidecar_digest(f"{digest}\n", "chain.zsh"), digest)
        self.assertIsNone(self.driver._sidecar_digest(f"{digest}  other.zsh\n", "chain.zsh"))
        self.assertIsNone(self.driver._sidecar_digest(f"{digest}  a  b\n", "chain.zsh"))
        self.assertIsNone(self.driver._sidecar_digest(f"{digest.upper()}\n", "chain.zsh"))
        self.assertIsNone(self.driver._sidecar_digest("", "chain.zsh"))

    def test_driver_reason_codes_are_registered_and_are_not_literal_call_sites(self) -> None:
        registered = night_gate.NIGHT_GATE_REASON_CODES | night_gate.NIGHT_DRIVER_REASON_CODES
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        literal_lines = [
            line
            for line in source.splitlines()
            if '"night_' in line
            and "_CODES" not in line
            and 'startswith("night_")' not in line
        ]
        self.assertTrue(set(self.driver._CODES.values()) <= registered)
        self.assertEqual(literal_lines, [])

    def test_absolute_script_help_works_from_root_with_launchd_path(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            cwd="/",
            env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("unattended", completed.stdout)

    def test_missing_courier_is_a_durable_driver_refusal(self) -> None:
        self.resolve_mock.return_value = (None, "not executable", None)
        exit_code, calls = self._run_night()
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        outcome = json.loads((night / "courier.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        self.assertEqual(calls, [])
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["courier_unavailable"])
        self.assertEqual(outcome["attempted"], 0)
        self.assertFalse(outcome["sent"])
        self.assertEqual(self.driver._durable_record.call_count, 2)
        self.resolve_mock.assert_called_once()

    def test_courier_spawn_failure_records_outcome_and_second_publish(self) -> None:
        self.driver.run_courier = self.real_run_courier
        self.driver._durable_record = self.real_durable_record
        popen_argv = []
        run_argv = []

        def spawn(argv, *args, **kwargs):
            popen_argv.append(list(argv))
            if argv[0] == "/bin/zsh":
                return FakeProcess(argv)
            raise FileNotFoundError("courier vanished")

        def run_command(argv, **kwargs):
            run_argv.append(list(argv))
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        old_deadline = self.driver.COURIER_DEADLINE_S
        self.driver.COURIER_DEADLINE_S = 0
        try:
            # Pin the clock inside the night: the fixture's absolute t0 is a fixed
            # 2026-09-02 date, so its 07:00 local dead-man is in the past for any
            # real clock after that morning.
            with mock.patch.object(
                self.driver.subprocess, "Popen", side_effect=spawn
            ), mock.patch.object(
                self.driver.subprocess, "run", side_effect=run_command
            ), mock.patch.object(self.driver.time, "sleep"), mock.patch.object(
                self.driver.time, "time", return_value=self.t0_epoch_s + 1
            ):
                exit_code = self.driver.run_night(self.plan_path)
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline
        outcome = json.loads((self.custody / "night" / "courier.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        self.assertEqual(outcome["attempted"], 4)
        self.assertFalse(outcome["sent"])
        self.assertIn("courier vanished", outcome["last_error"])
        self.assertEqual(sum(argv[0] == str(self.courier) for argv in popen_argv), 4)
        pushes = [argv for argv in run_argv if "push" in argv]
        self.assertEqual(len(pushes), 2)
        self.assertTrue(all(argv[-1].startswith("HEAD:night-results/") for argv in pushes))

    def test_deleted_pinned_courier_falls_back_and_records_substitution(self) -> None:
        pinned = self.root / "versions" / "2.1.252"
        pinned.parent.mkdir()
        pinned.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        pinned.chmod(0o755)
        fallback = self.root / "bin" / "claude"
        fallback.parent.mkdir()
        fallback.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        fallback.chmod(0o755)
        pinned.unlink()

        calls, spawn = self._popen_recorder()
        self.resolve_mock.side_effect = self.real_resolve_courier_bin
        self.driver.run_courier = self.real_run_courier
        old_deadline = self.driver.COURIER_DEADLINE_S
        self.driver.COURIER_DEADLINE_S = 0
        try:
            with mock.patch.object(
                self.driver.shutil, "which", return_value=str(fallback)
            ), mock.patch.object(
                self.driver.subprocess, "Popen", side_effect=spawn
            ), mock.patch.object(self.driver.time, "sleep"), mock.patch.object(
                self.driver.time, "time", return_value=self.t0_epoch_s + 1
            ):
                exit_code = self.driver.run_night(self.plan_path, courier_bin=pinned)
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline

        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        courier_calls = [argv for argv in calls if argv[0] == str(fallback)]
        self.assertEqual(len(courier_calls), 4)
        self.assertFalse((self.custody / "night" / "refusal.json").exists())
        attempts = [
            json.loads(line)
            for line in (
                self.custody / "night" / "courier.attempts.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]
        expected_substitution = {"requested": str(pinned), "used": str(fallback)}
        self.assertTrue(attempts)
        self.assertTrue(
            all(
                attempt["courier_bin_substitution"] == expected_substitution
                for attempt in attempts
            )
        )
        night_log = (self.custody / "night.log").read_text(encoding="utf-8")
        self.assertIn(
            f"courier binary substituted requested={pinned} used={fallback}",
            night_log,
        )

    def test_write_once_rerun_preserves_the_first_nights_records(self) -> None:
        first_exit, first_calls = self._run_night()
        night = self.custody / "night"
        result_before = (night / "result.json").read_bytes()
        receipt_before = (night / "receipt.json").read_bytes()
        courier_calls = self.driver.run_courier.call_count
        probe_calls = self.probes_mock.call_count
        second_exit = self.driver.run_night(self.plan_path)
        reruns = list(night.glob("rerun-*.refusal.json"))
        self.assertEqual(first_exit, 0)
        self.assertEqual(second_exit, self.driver.EXIT_REFUSED)
        self.assertEqual(first_calls, [["/bin/zsh", str(self.chain)]])
        self.assertEqual((night / "result.json").read_bytes(), result_before)
        self.assertEqual((night / "receipt.json").read_bytes(), receipt_before)
        self.assertEqual(self.driver.run_courier.call_count, courier_calls)
        self.assertEqual(self.probes_mock.call_count, probe_calls + 1)  # first-act census precedes plan reads
        self.assertEqual(len(reruns), 1)
        rerun = json.loads(reruns[0].read_text())
        self.assertEqual(rerun["refusal"]["reason"], self.driver._CODES["record_exists"])

    def test_driver_refusal_schema_is_exact_and_not_a_gate_receipt(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        reasons = sorted(
            self.driver.NIGHT_DRIVER_REASON_CODES | self.driver.NIGHT_GATE_REASON_CODES
        )
        for index, reason in enumerate(reasons):
            with self.subTest(reason=reason):
                path = self.root / f"driver-refusal-{index}.json"
                self.driver._write_driver_refusal(path, plan, reason, "defect detail")
                document = json.loads(path.read_text())
                self.assertEqual(self.driver.validate_refusal(document), [])
                self.assertNotEqual(night_gate.validate_receipt(document), [])
                self.assertEqual(
                    set(document),
                    {"schema", "receipt_class", "plan_id", "verdict", "refusal"},
                )

    def test_unproven_chain_termination_records_unkilled_and_spawns_no_courier(self) -> None:
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n"),
        ]
        process = UnkillableProcess(["/bin/zsh", str(self.chain)])
        with mock.patch.object(self.driver.subprocess, "Popen", return_value=process), mock.patch.object(
            self.driver.os, "killpg"
        ) as kill_group:
            exit_code = self.driver.run_night(self.plan_path)
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        unkilled = json.loads((night / "chain.unkilled").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_COURIER_FAILED)
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["chain_alive"])
        self.assertEqual(unkilled["pgid"], process.pid)
        self.assertEqual(kill_group.call_args_list[0].args, (process.pid, self.driver.signal.SIGTERM))
        self.driver.run_courier.assert_not_called()

    def test_dead_man_reaps_a_gone_group_then_censuses_and_couriers(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text(
            json.dumps({"pid": 7171, "pgid": 7171, "epoch_s": time.time()}),
            encoding="utf-8",
        )
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg", side_effect=ProcessLookupError):
            exit_code = self.driver.dead_man(self.plan_path)
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(exit_code, 0)
        self.assertEqual(exited["reaped_by"], "dead-man")
        self.assertTrue((night / "censuses.jsonl").is_file())
        self.driver.run_courier.assert_called_once()
        self.assertGreaterEqual(self.driver._durable_record.call_count, 2)

    def test_dead_man_refuses_a_proven_live_process_group(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text(
            json.dumps({"pid": 7272, "pgid": 7272, "epoch_s": time.time()}),
            encoding="utf-8",
        )
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ), mock.patch.object(self.driver.os, "killpg") as kill_group:
            exit_code = self.driver.dead_man(self.plan_path)
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        kill_group.assert_called_once_with(7272, 0)
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["chain_alive"])
        self.driver.run_courier.assert_not_called()
        self.driver._durable_record.assert_called_once()

    def test_dead_man_refuses_a_fresh_live_courier_lock(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        plan = self.driver._load_plan(self.plan_path)
        completion_epoch_s = plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S
        (night / "courier.lock").write_text(
            json.dumps({"pid": os.getpid(), "epoch_s": completion_epoch_s}),
            encoding="utf-8",
        )
        (night / "courier.heartbeat").write_text("alive\n", encoding="utf-8")
        with mock.patch.object(
            self.driver.time, "time", return_value=completion_epoch_s
        ):
            exit_code = self.driver.dead_man(self.plan_path)
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["courier_running"])
        self.driver.run_courier.assert_not_called()

    def test_empty_non_json_and_missing_plans_refuse_and_attempt_courier(self) -> None:
        cases = (("empty", "{}"), ("text", "not json"), ("missing", None))
        for name, contents in cases:
            with self.subTest(name=name):
                case_root = self.root / name
                case_root.mkdir()
                plan_path = case_root / "plan.json"
                if contents is not None:
                    plan_path.write_text(contents, encoding="utf-8")
                self.driver.run_courier.reset_mock()
                self.driver._durable_record.reset_mock()
                exit_code = self.driver.run_night(plan_path)
                night = case_root / "night-custody" / "night"
                refusal = json.loads((night / "refusal.json").read_text())
                self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
                self.assertEqual(refusal["refusal"]["reason"], self.driver._CODES["plan_malformed"])
                self.assertTrue((night / "result.json").is_file())
                self.driver.run_courier.assert_called_once()
                self.assertEqual(self.driver._durable_record.call_count, 2)

    def test_rehearsal_census_hits_are_observed_without_killing_the_stub(self) -> None:
        self._write_plan(receipt_class="REHEARSAL_STUB")
        self.source.census_responses = [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="12345 claude\n"),
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="12345 claude\n"),
        ]
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.os, "killpg"
        ) as kill_group, mock.patch.object(self.driver.time, "sleep"):
            exit_code = self.driver.run_night(self.plan_path)
        night = self.custody / "night"
        result = json.loads((night / "result.json").read_text())
        self.assertEqual(exit_code, self.driver.EXIT_REFUSED)
        self.assertEqual(result["verdict"], "REHEARSAL_ONLY")
        self.assertGreater(result["census_count"], 0)
        self.assertTrue(result["census_hits"])
        self.assertEqual(result["census_hits"][0]["stdout"], "12345 claude\n")
        self.assertFalse((night / "refusal.json").exists())
        self.assertEqual(calls, [["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]])
        kill_group.assert_not_called()
        self.driver.run_courier.assert_called_once()

    def test_chain_exit_is_recorded_before_the_first_durable_publish(self) -> None:
        events = []
        real_record_exit = self.driver._record_chain_exit

        def record_exit(*args, **kwargs):
            real_record_exit(*args, **kwargs)
            events.append("exited")

        self.driver._durable_record.side_effect = lambda *args: events.append("publish")
        with mock.patch.object(self.driver, "_record_chain_exit", side_effect=record_exit):
            exit_code, _calls = self._run_night()
        self.assertEqual(exit_code, 0)
        self.assertLess(events.index("exited"), events.index("publish"))

    def test_living_chain_records_a_thirty_second_census(self) -> None:
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.time, "sleep"
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        result = json.loads((self.custody / "night" / "result.json").read_text())
        self.assertGreater(result["census_count"], 0)
        self.assertEqual(self.driver.CENSUS_INTERVAL_S, 30)
        self.assertTrue(self.popen_kwargs[0]["start_new_session"])

    def test_durable_publish_uses_shallow_clone_and_named_results_branch_twice(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        night = self.custody / "night"
        night.mkdir()
        (self.custody / "night.log").write_text("record\n", encoding="utf-8")
        argvs = []

        def fake_run(argv, **kwargs):
            argvs.append(list(argv))
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir(parents=True)
            return types.SimpleNamespace(stdout="example-origin\n", returncode=0)

        with mock.patch.object(self.driver.subprocess, "run", side_effect=fake_run):
            self.real_durable_record(self.custody, night, plan)
            (night / "courier.heartbeat").write_text("seen\n", encoding="utf-8")
            self.real_durable_record(self.custody, night, plan)
        clone = next(argv for argv in argvs if argv[:4] == ["git", "clone", "--depth", "1"])
        pushes = [argv for argv in argvs if "push" in argv]
        branch = f"night-results/{self.driver._night_date(plan)}"
        self.assertEqual(clone, ["git", "clone", "--depth", "1", "example-origin", str(self.custody / "results-clone")])
        self.assertEqual(len(pushes), 2)
        self.assertTrue(all(argv[-1] == f"HEAD:{branch}" for argv in pushes))

    def test_courier_deadline_is_derived_from_the_measured_artifact(self) -> None:
        artifact = json.loads(
            (REPO_ROOT / "docs" / "process_traces" / "2026-09-01-unattended" / "cold_start.json").read_text()
        )
        measured = artifact["median_ms"] / 1000
        expected = min(600, max(3 * measured, 300))
        self.assertEqual(self.driver.COURIER_DEADLINE_S, expected)

    def test_artifact_inventory_includes_every_courier_record(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        for name in (
            "courier.json",
            "courier.attempts.jsonl",
            "courier.heartbeat",
            "courier.sent",
        ):
            (night / name).write_text(name + "\n", encoding="utf-8")
        paths = {item["path"] for item in self.driver._artifact_list(self.custody, night)}
        self.assertTrue(
            {
                "night/courier.json",
                "night/courier.attempts.jsonl",
                "night/courier.heartbeat",
                "night/courier.sent",
            }
            <= paths
        )

    def test_code_map_rejects_a_non_night_registry_member(self) -> None:
        with self.assertRaises(RuntimeError):
            self.driver._build_code_map({"bad_prefix"})

    def test_run_path_courier_hands_off_at_the_dead_man_epoch(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        calls, spawn = self._popen_recorder()
        self.driver.run_courier = self.real_run_courier
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            outcome = self.driver.run_courier(
                self.custody,
                plan,
                self.courier,
                deadman_epoch_s=time.time() - 1,
            )
        self.assertEqual(outcome["attempted"], 0)
        self.assertFalse(outcome["sent"])
        self.assertEqual(calls, [])
        self.assertFalse((self.custody / "night" / "courier.lock").exists())

    def test_courier_wait_caps_sleep_at_the_dead_man_epoch(self) -> None:
        heartbeat = self.root / "absent-heartbeat"
        sent = self.root / "absent-sent"
        stop_epoch_s = 10_000.0
        wall_clock = [stop_epoch_s - 0.3]
        monotonic_clock = [50.0]
        sleeps = []

        def advance(delay: float) -> None:
            sleeps.append(delay)
            wall_clock[0] += delay
            monotonic_clock[0] += delay

        with mock.patch.object(
            self.driver.time, "time", side_effect=lambda: wall_clock[0]
        ), mock.patch.object(
            self.driver.time, "monotonic", side_effect=lambda: monotonic_clock[0]
        ), mock.patch.object(self.driver.time, "sleep", side_effect=advance):
            heartbeat_seen, was_sent = self.driver._wait_for_courier(
                heartbeat,
                sent,
                stop_epoch_s=stop_epoch_s,
            )
        self.assertFalse(heartbeat_seen)
        self.assertFalse(was_sent)
        self.assertTrue(sleeps)
        self.assertLessEqual(max(sleeps), 0.3)

    def test_night_date_uses_the_same_local_civil_day_as_dead_man(self) -> None:
        self._write_plan(t0_epoch_s=datetime(2026, 9, 2, 20, 0).timestamp())
        plan = self.driver._load_plan(self.plan_path)
        self.assertEqual(self.driver._night_date(plan), "20260902")

    def test_exclusive_record_writers_and_markers_are_fsynced(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        record = night / "result.json"
        with mock.patch.object(self.driver.os, "open", wraps=os.open) as open_file, mock.patch.object(
            self.driver.os, "fsync", wraps=os.fsync
        ) as fsync:
            self.driver._write_json(record, {"value": 1})
            flags = open_file.call_args_list[0].args[1]
            self.assertEqual(
                flags & (os.O_CREAT | os.O_EXCL | os.O_WRONLY),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
            with self.assertRaises(FileExistsError):
                self.driver._write_json(record, {"value": 2})
            descriptor = self.driver._claim_chain_start(night)
            self.assertIsNotNone(descriptor)
            assert descriptor is not None
            self.driver._complete_chain_start(descriptor, FakeProcess(["chain"]), night)
            self.driver._record_chain_exit(night, 0)
            sent = night / "courier.sent"
            sent.write_text("sent\n", encoding="utf-8")
            heartbeat_seen, was_sent = self.driver._wait_for_courier(
                night / "courier.heartbeat", sent
            )
        self.assertFalse(heartbeat_seen)
        self.assertTrue(was_sent)
        self.assertGreaterEqual(fsync.call_count, 4)

    def test_moved_real_measurement_checkout_refuses_as_stale(self) -> None:
        measurement = self.root / "measurement-probe"
        pinned_head = _init_git_repo(measurement)
        plan_mapping = json.loads(self.plan_path.read_text(encoding="utf-8"))
        plan_mapping["measurement_root"] = str(measurement)
        plan_mapping["measurement_head"] = pinned_head
        self.plan_path.write_text(json.dumps(plan_mapping), encoding="utf-8")

        marker = measurement / "measurement.txt"
        marker.write_text("moved\n", encoding="utf-8")
        subprocess.run(
            ["/usr/bin/git", "-C", str(measurement), "add", marker.name], check=True
        )
        subprocess.run(
            [
                "/usr/bin/git",
                "-C",
                str(measurement),
                "-c",
                "user.name=JouleWise Test",
                "-c",
                "user.email=joulewise-test@example.invalid",
                "commit",
                "-qm",
                "moved",
            ],
            check=True,
        )
        moved_head = subprocess.check_output(
            ["/usr/bin/git", "-C", str(measurement), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        self.assertNotEqual(pinned_head, moved_head)

        production_measurement_probe = self.real_make_probes().measurement_head
        fake = self.source.probes()
        probes = night_gate.Probes(
            run=fake.run,
            now_epoch_s=fake.now_epoch_s,
            monotonic_ns=fake.monotonic_ns,
            read_text=fake.read_text,
            checkout_head=fake.checkout_head,
            measurement_head=production_measurement_probe,
        )
        plan = self.driver._load_plan(self.plan_path)
        receipt = night_gate.evaluate_night(plan, probes)
        self.assertEqual("night_plan_stale", receipt.refusal.reason)
        self.assertIn("measurement_head", receipt.refusal.detail)

    def test_matching_real_measurement_checkout_uses_requested_root_and_strips_head(self) -> None:
        measurement = self.root / "matching-measurement-probe"
        pinned_head = _init_git_repo(measurement)
        driver_head = subprocess.check_output(
            ["/usr/bin/git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        self.assertNotEqual(driver_head, pinned_head)

        plan_mapping = json.loads(self.plan_path.read_text(encoding="utf-8"))
        plan_mapping["measurement_root"] = str(measurement)
        plan_mapping["measurement_head"] = pinned_head
        self.plan_path.write_text(json.dumps(plan_mapping), encoding="utf-8")

        production_measurement_probe = self.real_make_probes().measurement_head
        observed_head = production_measurement_probe(str(measurement))
        self.assertEqual(pinned_head, observed_head)
        self.assertFalse(observed_head.endswith("\n"))

        fake = self.source.probes()
        probes = night_gate.Probes(
            run=fake.run,
            now_epoch_s=fake.now_epoch_s,
            monotonic_ns=fake.monotonic_ns,
            read_text=fake.read_text,
            checkout_head=lambda: driver_head,
            measurement_head=production_measurement_probe,
        )
        plan = self.driver._load_plan(self.plan_path)
        receipt = night_gate.evaluate_night(plan, probes)
        self.assertNotIn(
            None if receipt.refusal is None else receipt.refusal.reason,
            {"night_plan_stale", "night_plan_malformed"},
        )
        self.assertEqual("GO", receipt.verdict)
        c5 = next(row for row in receipt.conditions if row.condition_id == "C5")
        self.assertEqual(pinned_head, c5.measured["measurement_checkout_head"])

    def _installer_plan(self, root: Path) -> Path:
        plan = json.loads(self.plan_path.read_text())
        plan["repo_head"] = subprocess.check_output(
            ["/usr/bin/git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        measurement_root = root / "measurement"
        plan["measurement_root"] = str(measurement_root)
        plan["measurement_head"] = _init_git_repo(measurement_root)
        plan["custody_root"] = str(root / "custody")
        plan["authored_epoch_s"] = time.time()  # bench fix: fixture authored "now" so the installer age check passes
        path = root / "install-plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        return path

    def _installer_environment(self, root: Path) -> tuple[dict[str, str], Path]:
        binary_dir = root / "bin"
        binary_dir.mkdir()
        courier = binary_dir / "claude"
        courier.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        courier.chmod(0o755)
        environment = os.environ.copy()
        environment["HOME"] = str(root / "home")
        environment["PATH"] = f"{binary_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        return environment, courier

    def _installer_symlink_environment(
        self, root: Path
    ) -> tuple[dict[str, str], Path, Path]:
        binary_dir = root / "bin"
        versions_dir = root / "share" / "claude" / "versions"
        binary_dir.mkdir()
        versions_dir.mkdir(parents=True)
        version = versions_dir / "2.1.252"
        version.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        version.chmod(0o755)
        courier = binary_dir / "claude"
        courier.symlink_to(version)
        environment = os.environ.copy()
        environment["HOME"] = str(root / "home")
        environment["PATH"] = f"{binary_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        return environment, courier, version.resolve()

    def test_installer_symlinked_courier_renders_resolved_binary_and_lookup_path(
        self,
    ) -> None:
        root = self.root / "symlink-render"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, courier, resolved_courier = self._installer_symlink_environment(
            root
        )
        rendered = root / "rendered"
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                "1",
                "--minute",
                "2",
                "--render-only",
                str(rendered),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        night = plistlib.loads((rendered / "com.joulewise.night.plist").read_bytes())
        rendered_path = night["EnvironmentVariables"]["PATH"]
        self.assertEqual(
            night["ProgramArguments"][-2:],
            ["--courier-bin", str(resolved_courier)],
        )
        self.assertEqual(
            rendered_path,
            f"{courier.parent}:/usr/bin:/bin:/usr/sbin:/sbin",
        )
        with mock.patch.dict(os.environ, {"PATH": rendered_path}, clear=True):
            found, error, substitution = self.real_resolve_courier_bin(None)
        self.assertEqual(found, courier)
        self.assertIsNone(error)
        self.assertIsNone(substitution)

    def test_installer_renders_working_directory_path_binary_and_distinct_logs(self) -> None:
        root = self.root / "render"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, courier = self._installer_environment(root)
        rendered = root / "rendered"
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                "1",
                "--minute",
                "2",
                "--render-only",
                str(rendered),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        night = plistlib.loads((rendered / "com.joulewise.night.plist").read_bytes())
        deadman = plistlib.loads((rendered / "com.joulewise.night.deadman.plist").read_bytes())
        expected_path = f"{courier.parent}:/usr/bin:/bin:/usr/sbin:/sbin"
        self.assertEqual(night["WorkingDirectory"], str(REPO_ROOT))
        self.assertEqual(night["EnvironmentVariables"]["PATH"], expected_path)
        self.assertEqual(
            night["ProgramArguments"][-2:],
            ["--courier-bin", str(courier.resolve())],
        )
        self.assertNotEqual(night["StandardOutPath"], deadman["StandardOutPath"])
        self.assertNotEqual(night["StandardErrorPath"], deadman["StandardErrorPath"])

    def test_installer_refuses_when_command_lookup_has_no_courier(self) -> None:
        root = self.root / "no-courier"
        root.mkdir()
        plan = self._installer_plan(root)
        empty_path = root / "empty-bin"
        empty_path.mkdir()
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                "1",
                "--minute",
                "2",
                "--render-only",
                str(root / "rendered"),
            ],
            env={"HOME": str(root / "home"), "PATH": str(empty_path)},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("courier unavailable", completed.stderr)

    def test_installer_refuses_the_dead_man_hour_before_rendering(self) -> None:
        root = self.root / "dead-man-hour"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        launcher = root / "launchctl-stub"
        launcher.write_text("#!/bin/zsh\nexit 0\n", encoding="utf-8")
        launcher.chmod(0o755)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                str(self.driver.DEADMAN_HOUR),
                "--minute",
                "2",
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn(
            f"refusing --hour {self.driver.DEADMAN_HOUR}: it is the dead-man hour "
            f"(DEADMAN_HOUR={self.driver.DEADMAN_HOUR})",
            completed.stderr,
        )
        launch_dir = root / "home" / "Library" / "LaunchAgents"
        self.assertFalse((launch_dir / "com.joulewise.night.plist").exists())
        self.assertFalse((launch_dir / "com.joulewise.night.deadman.plist").exists())

    def test_installer_refuses_a_stale_courier_sent_before_bootstrap(self) -> None:
        root = self.root / "stale-courier"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "courier.sent").write_text("sent\n", encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            "#!/bin/zsh\nprint -r -- \"$*\" >> \"$LAUNCH_LOG\"\nexit 0\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                "1",
                "--minute",
                "2",
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("courier.sent", completed.stderr)
        self.assertFalse(launch_log.exists())

    def test_installer_refuses_a_dangling_symlink_night_record(self) -> None:
        # Sol 135 F1: zsh `[[ -e ]]` is false for a dangling symlink, so the
        # stale-night guard must also test `-L`.
        root = self.root / "stale-symlink"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "result.json").symlink_to(root / "missing-target.json")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            "#!/bin/zsh\nprint -r -- \"$*\" >> \"$LAUNCH_LOG\"\nexit 0\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                "1",
                "--minute",
                "2",
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("result.json", completed.stderr)
        self.assertFalse(launch_log.exists())

    def test_installer_uninstalls_with_stale_courier_sent(self) -> None:
        root = self.root / "stale-uninstall"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "courier.sent").write_text("sent\n", encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            "#!/bin/zsh\nprint -r -- \"$*\" >> \"$LAUNCH_LOG\"\nexit 0\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        environment["LAUNCH_LOG"] = str(launch_log)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                str(self.driver.DEADMAN_HOUR),
                "--minute",
                "2",
                "--uninstall",
                "--launchctl-bin",
                str(launcher),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        calls = launch_log.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))

    def test_installer_uninstalls_without_courier_on_minimal_path(self) -> None:
        root = self.root / "minimal-path-uninstall"
        root.mkdir()
        plan = self._installer_plan(root)
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            "#!/bin/zsh\nprint -r -- \"$*\" >> \"$LAUNCH_LOG\"\nexit 0\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        completed = subprocess.run(
            [
                "/bin/zsh",
                str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
                "--plan",
                str(plan),
                "--hour",
                str(self.driver.DEADMAN_HOUR),
                "--minute",
                "2",
                "--uninstall",
                "--launchctl-bin",
                str(launcher),
            ],
            env={
                "HOME": str(root / "home"),
                "PATH": "/usr/bin:/bin",
                "LAUNCH_LOG": str(launch_log),
            },
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        calls = launch_log.read_text(encoding="utf-8").splitlines()
        self.assertTrue(any(line.endswith("com.joulewise.night") for line in calls))
        self.assertTrue(any(line.endswith("com.joulewise.night.deadman") for line in calls))

    def test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap(self) -> None:
        root = self.root / "install"
        root.mkdir()
        plan = self._installer_plan(root)
        environment, _courier = self._installer_environment(root)
        custody_night = root / "custody" / "night"
        custody_night.mkdir(parents=True)
        (custody_night / "chain.started").write_text("active\n", encoding="utf-8")
        launch_log = root / "launch.log"
        launcher = root / "launchctl-stub"
        launcher.write_text(
            "#!/bin/zsh\n"
            "print -r -- \"$*\" >> \"$LAUNCH_LOG\"\n"
            "if [[ \"$1\" == bootstrap && \"$*\" == *deadman* ]]; then exit 1; fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        base_argv = [
            "/bin/zsh",
            str(REPO_ROOT / "scripts" / "install_night_agent.sh"),
            "--plan",
            str(plan),
            "--hour",
            "1",
            "--minute",
            "2",
            "--launchctl-bin",
            str(launcher),
        ]
        environment["LAUNCH_LOG"] = str(launch_log)
        active = subprocess.run(
            base_argv,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(active.returncode, 3)
        self.assertIn("chain.started", active.stderr)
        self.assertFalse(launch_log.exists())
        (custody_night / "chain.started").unlink()
        failed = subprocess.run(
            base_argv,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(failed.returncode, 3)
        calls = launch_log.read_text().splitlines()
        self.assertTrue(any(line.startswith("bootstrap ") and "com.joulewise.night.plist" in line for line in calls))
        self.assertTrue(any(line.startswith("bootstrap ") and "deadman.plist" in line for line in calls))
        self.assertTrue(any(line.startswith("bootout ") and line.endswith("com.joulewise.night") for line in calls))




class PackNightProducerTests(unittest.TestCase):
    """Real driver/file custody with mocked ARM author and live probes only."""
    def setUp(self):
        from joulewise import arm_readiness as readiness, arm_readiness_evidence_t0 as author
        self.readiness, self.author = readiness, author
        self.driver = _load_driver()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.custody = (self.root / "home/night-custody/rehearsal-t0-unattended-producer-table"
                        if getattr(self, "_rehearsal_layout", False) else self.root / "custody")
        self.custody.mkdir(parents=True)
        self.pack = self.root / "pack-test"
        self.pack.mkdir()
        self.pack_custody = self.custody / self.pack.name
        self.inputs = self.pack_custody / "arm_readiness.t0.inputs"
        self.inputs.mkdir(parents=True)
        self.chain = self.root / "window-chain.zsh"
        self.chain.write_bytes(b"echo fixture\n")
        self.sidecar = self.root / "chain.sha256"
        self.sidecar.write_text(readiness.sha256_bytes(self.chain.read_bytes()) + "  window-chain.zsh\n")
        self.env = self.root / "window.env"
        self.env.write_bytes(b"fixture\n")
        self.table = self.custody / "table.json"
        self.table.write_bytes(b"{}\n")
        self.authorization = {"purpose": "G2B_SHAKEDOWN", "attempt_id": "pack-plan/1", "claim_eligible": False,
            "pack_sha256": "a" * 64, "permitted_chain_sha256": readiness.sha256_bytes(self.chain.read_bytes()),
            "permitted_blocks": 1, "authority": "D-171 §3"}
        self.confirmation = {"table_path": str(self.table), "table_sha256": readiness.sha256_bytes(self.table.read_bytes()),
            "transcript_sha256": "c" * 64, "confirmed_at": {"epoch_s": 0.0, "iso8601_utc": "1970-01-01T00:00:00.000000Z"}}
        auth_ref = self.write(self.custody / "authorization.json", self.authorization)
        confirmation_ref = self.write(self.custody / "confirmation.json", self.confirmation)
        self.manifest = self.inputs / "launch-manifest.json"
        self.write(self.manifest, {"schema_version": readiness.LAUNCH_MANIFEST_SCHEMA})
        self.write(self.inputs / "arm-context.json", {"custody_root": str(self.custody)})
        self.plan = night_gate.NightPlan(plan_id="pack-plan", receipt_class="TRANSACTION_PACK",
            t0_epoch_s=datetime(2026, 9, 2, 1, 0).timestamp(), window_max_s=60,
            authored_epoch_s=datetime(2026, 9, 2, 0, 59).timestamp(), repo_head=HEAD,
            measurement_root=str(REPO_ROOT), measurement_head=HEAD, chain_path=str(self.chain),
            chain_sha256_path=str(self.sidecar), custody_root=str(self.custody), registration_path=None,
            pack_night={"pack_id": self.pack.name, "pack_root": str(self.pack), "pack_sha256": "a" * 64,
                        "attempt_ordinal": 1, "authorization_record": auth_ref, "confirmation_record": confirmation_ref})
        self.plan_path = write_night_plan(self.custody / "night_plan.json", self.plan)
        self.raw = self.plan_path.read_bytes()
        self.events = []
        self.probe_source = ProbeSource(self.plan.t0_epoch_s + 1)
        original_probes = self.probe_source.probes()
        def probe(argv):
            self.events.append("census" if argv == night_gate.AGENT_CENSUS_ARGV else "probe")
            return original_probes.run(argv)
        self.probes = replace(original_probes, run=probe)
        for target, name, replacement in (
            (readiness, "committed_pack_tree_sha256", mock.Mock(return_value="a" * 64)),
            (readiness, "_current_boot_session_id", mock.Mock(return_value=BOOT_UUID)),
            (readiness, "scan_receipt_namespace", mock.Mock(return_value=[])),
            (readiness, "_verify_arm_receipt", mock.Mock(side_effect=self.verify)),
            (readiness, "generate_arm_receipt", mock.Mock(side_effect=self.arm)),
            (readiness, "_attested_launch_artifact_references", mock.Mock(side_effect=lambda *a, **k: self.refs())),
            (author, "author_arm_readiness_evidence_t0", mock.Mock(side_effect=self.t0)),
            (self.driver, "make_probes", mock.Mock(return_value=self.probes)),
            (self.driver, "_resolve_courier_bin", mock.Mock(return_value=(Path('/fixture/courier'), None, None))),
            (self.driver, "_finish_reporting", lambda custody, night, plan, code, *a, **k: code),
            (self.driver, "observe_identity", mock.Mock(return_value=Identity("LIVE", "fixture-start"))),
        ):
            patch = mock.patch.object(target, name, replacement)
            patch.start()
            self.addCleanup(patch.stop)
        self.arm_path = self.pack_custody / "arm_readiness.receipts/arm-0001.json"

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.readiness.render_json(value))
        return {"path": str(path), "sha256": self.readiness.sha256_bytes(path.read_bytes())}

    def refs(self):
        return {key: {"path": str(path), "sha256": self.readiness.sha256_bytes(path.read_bytes())}
                for key, path in (("launch_manifest", self.manifest), ("window_environment", self.env), ("window_chain", self.chain))}

    def t0(self, pack, custody):
        self.events.append("T0")
        inputs = [self.write(self.inputs / filename, {"capture": step}) for step, filename in self.author._CAPTURE_FILES.items()]
        source = self.write(self.pack_custody / "arm_readiness.t0.sources/source.json", {"input_artifacts": inputs})
        self.evidence = []
        paths = []
        for row in self.author._EXPECTED_ROWS:
            path = self.pack_custody / self.author._EVIDENCE_DIRECTORY / self.author._receipt_name(row)
            ref = self.write(path, {"facts": [{"source_kind": "PROBE", "source_path": str(Path(source["path"]).relative_to(self.pack_custody)), "source_sha256": source["sha256"]}]})
            self.evidence.append({"namespace": "WINDOW_CUSTODY", "path": str(path.relative_to(self.pack_custody)), "sha256": ref["sha256"]})
            paths.append(str(path))
        return {"status": "PASS", "receipt_paths": paths}

    def arm(self, pack, context, custody, **kwargs):
        self.events.append("ARM")
        self.arm_value = {"status": "PASS", "arm_disposition": "GO", "receipt_id": "arm-0001",
            "boot_session_id": BOOT_UUID, "valid_until_monotonic_ns": time.monotonic_ns() + 10**12,
            "pack": {"pack_root": str(self.pack), "pack_sha256": "a" * 64, "pack_id": self.pack.name,
                     "plan_id": self.plan.plan_id, "window_id": getattr(self, "_window_id", "production-window")},
            "reviewed_main": {"head_commit": HEAD},
            "arm_context": context, "evidence": self.evidence}
        ref = self.write(self.arm_path, self.arm_value)
        return {"status": "PASS", "arm_disposition": "GO", "receipt_path": ref["path"], "receipt_sha256": ref["sha256"]}

    def verify(self, pack, path, **kwargs):
        self.events.append("VERIFY")
        self.assertEqual(self.arm_path, path)
        self.assertIs(kwargs["require_unconsumed"], True)
        self.assertEqual(self.confirmation["table_sha256"], kwargs["expected_confirmation_digest"])
        return {"status": "PASS", "arm_disposition": "GO", "receipt_sha256": self.readiness.sha256_bytes(Path(path).read_bytes())}

    def run_driver(self):
        calls = []
        def spawn(command, **kwargs):
            self.events.append("LAUNCH")
            self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
            calls.append(command)
            return FakeProcess(command, return_code=0)
        read_bytes = Path.read_bytes
        def observed_read(path):
            if path == self.plan_path:
                self.events.append("PLAN_BYTES")
            return read_bytes(path)
        with mock.patch.object(self.driver.subprocess, "Popen", side_effect=spawn), mock.patch.object(Path, "read_bytes", observed_read):
            code = self.driver.run_night(self.plan_path)
        return code, calls

    def test_driver_self_authors_arm_before_go_and_pins_all_eight_flags(self):
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_GO, code)
        self.assertEqual("census", self.events[0])
        self.assertLess(self.events.index("PLAN_BYTES"), self.events.index("T0"))
        self.assertLess(self.events.index("T0"), self.events.index("ARM"))
        self.assertLess(self.events.index("ARM"), self.events.index("VERIFY"))
        self.assertLess(self.events.index("VERIFY"), self.events.index("LAUNCH"))
        go_path = self.custody / "night/go_receipt.json"
        go = json.loads(go_path.read_bytes())
        self.assertEqual({"schema_version", "receipt_id", "receipt_class", "purpose", "plan_id", "plan_sha256",
            "pack_id", "pack_sha256", "arm_receipt", "boot_session_id", "t0_evidence", "t0_evidence_set_sha256",
            "launch_manifest_sha256", "window_environment_sha256", "window_chain_sha256", "repo_head",
            "measurement_root", "measurement_head", "confirmation_record", "authorization", "census",
            "issued_epoch_s", "issued_monotonic_ns", "valid_until_monotonic_ns", "conditions", "verdict"}, set(go))
        self.assertEqual("joulewise.pack_night_go_receipt.v1", go["schema_version"])
        self.assertEqual("TRANSACTION_PACK", go["receipt_class"])
        self.assertEqual("G2B_SHAKEDOWN", go["purpose"])
        for key in ("plan_id", "repo_head", "measurement_root", "measurement_head"):
            self.assertEqual(getattr(self.plan, key), go[key])
        self.assertEqual(self.plan.pack_night["confirmation_record"], go["confirmation_record"])
        self.assertEqual({**self.plan.pack_night["authorization_record"], **{key: self.authorization[key] for key in ("purpose", "attempt_id", "claim_eligible")}}, go["authorization"])
        self.assertEqual({"receipt_id": "arm-0001", "sha256": self.readiness.sha256_bytes(self.arm_path.read_bytes()), "valid_until_monotonic_ns": self.arm_value["valid_until_monotonic_ns"]}, go["arm_receipt"])
        self.assertEqual(self.readiness.sha256_bytes(self.readiness.render_json(go["t0_evidence"])), go["t0_evidence_set_sha256"])
        for key, ref in self.refs().items():
            self.assertEqual(ref["sha256"], go[key + "_sha256"])
        if hasattr(self.readiness, "validate_pack_night_go_receipt"):
            self.readiness.validate_pack_night_go_receipt(go)
        self.assertIs(type(go["issued_epoch_s"]), float)
        self.assertIs(type(go["issued_monotonic_ns"]), int)
        self.assertIs(type(go["valid_until_monotonic_ns"]), int)
        self.assertEqual(["C1", "C2", "C3", "C4", "C5"], [row["condition_id"] for row in go["conditions"]])
        self.assertEqual(["PASS"] * 5, [row["status"] for row in go["conditions"]])
        self.assertEqual([None] * 5, [row["basis"] for row in go["conditions"]])
        self.assertEqual(21, len(go["t0_evidence"]))
        census_ref = next(row for row in go["conditions"] if row["condition_id"] == "C3")["evidence"][0]
        census_path = self.custody / census_ref["path"]
        census_raw = census_path.read_bytes()
        census = json.loads(census_raw)
        self.assertEqual(go["census"]["monotonic_ns"], census["monotonic_ns"])
        self.assertEqual("", census["stdout"])
        self.assertEqual(1, census["exit_code"])
        self.assertEqual(self.readiness.sha256_bytes(census_raw), census_ref["sha256"])
        with (self.custody / "night/censuses.jsonl").open("a") as journal:
            journal.write("{}\n")
        self.assertEqual(census_raw, census_path.read_bytes())
        self.assertEqual(0o600, go_path.stat().st_mode & 0o777)
        self.assertEqual(self.readiness.sha256_bytes(self.raw), go["plan_sha256"])
        self.assertEqual({"C1", "C2", "C3", "C4", "C5"}, {row["condition_id"] for row in go["conditions"] if row["status"] == "PASS"})
        self.assertEqual([], night_gate.validate_receipt(json.loads((self.custody / "night/receipt.json").read_bytes())))
        argv = calls[0]
        expected = {"--pack-root": str(self.pack), "--arm-receipt": str(self.arm_path),
            "--arm-readiness-custody-root": str(self.custody), "--launch-manifest": str(self.manifest),
            "--night-plan": str(self.plan_path), "--go-receipt": str(go_path),
            "--step6-confirmation-table": str(self.table), "--expected-confirmation-digest": self.confirmation["table_sha256"]}
        self.assertEqual(expected, dict(zip(argv[2::2], argv[3::2])))
        self.assertEqual(8, len(argv[2::2]))
        # Independent of seat 3's parser landing; missing ANY transport flag
        # breaks the exact argv assertion without requiring a staged parser.
        self.assertEqual(str(REPO_ROOT / "scripts/launch_window.py"), argv[1])
        with self.assertRaises(FileExistsError):
            self.driver._write_bytes_exclusive(go_path, b"replacement")
        self.assertEqual(go, json.loads(go_path.read_bytes()))

    def test_gate_reauthenticates_c1_and_c2_despite_forged_driver_pass_rows(self):
        prepared = self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        state = self.driver._author_pack_arm(self.plan, prepared)
        forged = {key: night_gate.ConditionRow(key, "PASS", None, (), {"forged": True})
                  for key in ("C1", "C2")}
        def evaluate():
            return night_gate.evaluate_night(self.plan, self.probes,
                pack_arm_receipt=state["path"], pack_conditions=forged)
        receipt = evaluate()
        self.assertEqual("GO", receipt.verdict)
        self.assertEqual(["PASS"] * 5, [row.status for row in receipt.conditions])
        self.assertNotIn("forged", receipt.conditions[0].measured)
        self.assertNotIn("forged", receipt.conditions[1].measured)
        for key, expected_row in (("authorization_record", 0), ("confirmation_record", 0)):
            path = Path(self.plan.pack_night[key]["path"])
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            receipt = evaluate()
            self.assertEqual("REFUSED", receipt.verdict)
            self.assertEqual("launch_go_receipt_invalid", receipt.refusal.reason)
            self.assertIn(key, receipt.refusal.detail)
            self.assertEqual("FAIL", receipt.conditions[expected_row].status)
            path.write_bytes(original)
        with mock.patch.object(self.readiness, "_verify_arm_receipt",
                side_effect=self.readiness.ArmReadinessError("readiness_dependency_refused", "forged ARM")):
            receipt = evaluate()
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("PASS", receipt.conditions[0].status)
        self.assertEqual("FAIL", receipt.conditions[1].status)
        self.assertIn("forged ARM", receipt.refusal.detail)
        missing = night_gate.evaluate_night(self.plan, self.probes, pack_conditions=forged)
        self.assertEqual("launch_go_receipt_missing", missing.refusal.reason)
        self.assertEqual("FAIL", missing.conditions[1].status)
        path = Path(state["authored"]["receipt_paths"][0])
        path.write_bytes(path.read_bytes() + b" ")
        receipt = evaluate()
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("FAIL", receipt.conditions[1].status)
        self.assertIn("t0_evidence", receipt.refusal.detail)

    def test_pack_standard_refusal_receipt_preserves_each_actual_cause(self):
        for reason, receipt_reason in (
            ("night_courier_unavailable", "night_probe_error"),
            ("night_plan_overruns_deadman", "night_probe_error"),
            ("night_chain_digest_mismatch", "night_chain_digest_mismatch"),
            ("night_chain_already_started", "night_probe_error"),
            ("launch_go_receipt_missing", "launch_go_receipt_missing"),
            ("launch_go_receipt_invalid", "launch_go_receipt_invalid"),
        ):
            with self.subTest(reason=reason):
                custody = self.root / reason
                night = custody / "night"
                night.mkdir(parents=True)
                plan = replace(self.plan, custody_root=str(custody))
                self.driver._write_standard_refusal_result(custody, night, plan, reason,
                    "cause-specific detail", self.plan.t0_epoch_s, 123)
                receipt = json.loads((night / "receipt.json").read_bytes())
                refusal = json.loads((night / "refusal.json").read_bytes())
                self.assertEqual(receipt_reason, receipt["refusal"]["reason"])
                self.assertEqual(reason, refusal["refusal"]["reason"])
                self.assertEqual("cause-specific detail", refusal["refusal"]["detail"])
                self.assertEqual(
                    f"{refusal['refusal']['reason']}: {refusal['refusal']['detail']}",
                    receipt["refusal"]["detail"],
                )
                result = json.loads((night / "result.json").read_bytes())
                self.assertEqual(reason, result["aborted_reason"])
                self.assertEqual("REFUSED", receipt["verdict"])
                self.assertEqual([], night_gate.validate_receipt(receipt))
                self.assertFalse((night / "go_receipt.json").exists())

    def test_gate_checks_authorization_fields_and_confirmation_bytes(self):
        for key, changes in (
            ("authorization_record", {"attempt_id": "another-plan/1"}),
            ("authorization_record", {"purpose": "unruled"}),
            ("authorization_record", {"claim_eligible": True}),
            ("authorization_record", {"permitted_blocks": 2}),
            ("authorization_record", {"authority": "unruled"}),
            ("confirmation_record", {"table_sha256": "0" * 64}),
            ("confirmation_record", {"confirmed_at": {"epoch_s": "0", "iso8601_utc": "1970-01-01T00:00:00.000000Z"}}),
        ):
            with self.subTest(key=key, changes=changes):
                path = Path(self.plan.pack_night[key]["path"])
                original = path.read_bytes()
                ref = self.write(path, {**json.loads(original), **changes})
                changed = replace(self.plan, pack_night={**self.plan.pack_night, key: ref})
                receipt = night_gate.evaluate_night(changed, self.probes)
                self.assertEqual("REFUSED", receipt.verdict)
                self.assertEqual("launch_go_receipt_invalid", receipt.refusal.reason)
                self.assertIn(key, receipt.refusal.detail)
                self.assertEqual("FAIL", receipt.conditions[0].status)
                path.write_bytes(original)
        for key in ("authorization_record", "confirmation_record"):
            path = Path(self.plan.pack_night[key]["path"])
            original = path.read_bytes()
            path.unlink()
            receipt = night_gate.evaluate_night(self.plan, self.probes)
            self.assertEqual("launch_go_receipt_missing", receipt.refusal.reason)
            self.assertIn(key, receipt.refusal.detail)
            path.write_bytes(original)

    def test_no_go_on_arm_refusal(self):
        self.readiness.generate_arm_receipt.side_effect = lambda *a, **k: {"status": "REFUSE", "arm_disposition": "NO_GO"}
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        receipt = json.loads((self.custody / "night/receipt.json").read_bytes())
        self.assertEqual([], night_gate.validate_receipt(receipt))
        self.assertIn("NO_GO", receipt["refusal"]["detail"])

    def test_first_census_refusal_prevents_preparation_and_arm(self):
        self.probe_source.census_responses = [_probe(night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="42 claude\n")]
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.author.author_arm_readiness_evidence_t0.assert_not_called()
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())

    def test_pack_digest_mismatch_at_preparation_and_go_refuses_without_go(self):
        self.readiness.committed_pack_tree_sha256.return_value = "f" * 64
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "pack_root.pack_sha256"):
            self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        self.readiness.committed_pack_tree_sha256.return_value = "a" * 64
        original = self.arm
        def mutate_after_arm(*args, **kwargs):
            result = original(*args, **kwargs)
            self.readiness.committed_pack_tree_sha256.return_value = "f" * 64
            return result
        self.readiness.generate_arm_receipt.side_effect = mutate_after_arm
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        self.assertIn("pack_root.pack_sha256", (self.custody / "night/receipt.json").read_text())

    def test_each_plan_record_digest_and_pinned_plan_swap_refuse(self):
        for key in ("authorization_record", "confirmation_record"):
            path = Path(self.plan.pack_night[key]["path"])
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            with self.subTest(key=key), self.assertRaisesRegex(self.driver.PackNightRefusal, key):
                self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
            path.write_bytes(original)
        self.plan_path.write_bytes(self.raw + b" ")
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "plan_sha256"):
            self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)

    def test_selected_old_arm_and_higher_receipt_and_consumption_refuse(self):
        self.arm_path.parent.mkdir()
        self.arm_path.write_bytes(b"{}")
        prepared = self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "self-written"):
            self.driver._author_pack_arm(self.plan, prepared)
        self.readiness.scan_receipt_namespace.return_value = [{"number": 2, "receipt": {"boot_session_id": BOOT_UUID}}]
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "higher-numbered"):
            self.driver._pack_no_retry(self.plan, BOOT_UUID, self.arm_path)
        self.write(self.pack_custody / "arm_readiness.consumptions/other.consumed.json", {"boot_session_id": BOOT_UUID})
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "consumption this boot"):
            self.driver._pack_no_retry(self.plan, BOOT_UUID, self.arm_path)

    def test_second_manifest_missing_symlink_and_attested_digest_refuse(self):
        for field in ("duplicate", "missing", "symlink", "digest"):
            raw = self.manifest.read_bytes()
            extra = self.inputs / "second-manifest.json"
            if field == "duplicate":
                self.write(extra, {"schema_version": self.readiness.LAUNCH_MANIFEST_SCHEMA})
            elif field == "missing":
                self.manifest.unlink()
            elif field == "symlink":
                self.manifest.unlink()
                extra.write_bytes(raw)
                self.manifest.symlink_to(extra)
            else:
                refs = self.refs()
                refs["launch_manifest"]["sha256"] = "0" * 64
                self.readiness._attested_launch_artifact_references.side_effect = lambda *a, **k: refs
            with self.subTest(field=field), self.assertRaisesRegex(self.driver.PackNightRefusal, "launch_manifest") as caught:
                self.driver._pack_launch_references(self.plan, {})
            self.assertEqual("launch_go_receipt_missing" if field == "missing" else "launch_go_receipt_invalid", caught.exception.reason)
            self.manifest.unlink(missing_ok=True)
            extra.unlink(missing_ok=True)
            self.manifest.write_bytes(raw)

    def test_machine_refusal_and_refused_receipt_never_publish_go(self):
        self.probe_source.results[night_gate.HID_IDLE_ARGV] = _probe(night_gate.HID_IDLE_ARGV, stdout="1\n")
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        refused = self.driver._pack_refused_receipt(self.plan, self.driver.PackNightRefusal("fixture refusal"), self.probes)
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "refused night"):
            self.driver._produce_pack_go(self.plan, self.plan_path, self.raw, {}, {}, refused, self.probes)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())

    def test_pack_root_must_match_the_written_arm_root_and_digest(self):
        arm = {"pack": {"pack_root": str(self.pack), "pack_id": self.pack.name, "pack_sha256": "a" * 64}}
        self.assertEqual(self.pack, self.driver._pack_digest(self.plan, arm))
        for key, value in (("pack_root", str(self.root / "other")), ("pack_sha256", "0" * 64), ("pack_id", "other")):
            changed = {"pack": {**arm["pack"], key: value}}
            with self.subTest(key=key), self.assertRaisesRegex(self.driver.PackNightRefusal, "arm_receipt.pack"):
                self.driver._pack_digest(self.plan, changed)

    def test_t0_inventory_cannot_omit_add_or_substitute_author_or_capture_bytes(self):
        prepared = self.driver._prepare_pack_night(self.plan, self.plan_path, self.raw)
        state = self.driver._author_pack_arm(self.plan, prepared)
        self.assertEqual(21, len(self.driver._pack_evidence(self.plan, state)))
        paths = state["authored"]["receipt_paths"]
        for replacement in (paths[:-1], paths + [paths[0]], paths[:-1] + [str(self.inputs / "arm-context.json")]):
            changed = {**state, "authored": {**state["authored"], "receipt_paths": replacement}}
            with self.subTest(replacement=replacement), self.assertRaisesRegex(self.driver.PackNightRefusal, "t0_evidence"):
                self.driver._pack_evidence(self.plan, changed)
        evidence = state["arm"]["evidence"]
        receipt = next(item for item in evidence if str(self.custody / self.pack.name / item["path"]) == paths[0])
        for replacement in ([item for item in evidence if item is not receipt],
                            evidence + [receipt],
                            [{**item, "path": item["path"] + ".substituted"} if item is receipt else item for item in evidence]):
            changed = {"arm": {**state["arm"], "evidence": replacement}}
            with self.subTest(evidence=replacement), self.assertRaisesRegex(self.driver.PackNightRefusal, "t0_evidence"):
                self.driver._pack_evidence(self.plan, changed)
        for path in (Path(paths[0]), self.inputs / next(iter(self.author._CAPTURE_FILES.values()))):
            raw = path.read_bytes()
            path.write_bytes(raw + b" ")
            with self.subTest(path=path), self.assertRaisesRegex(self.driver.PackNightRefusal, "t0_evidence"):
                self.driver._pack_evidence(self.plan, state)
            path.write_bytes(raw)

    def test_go_producer_enforces_two_by_two_purpose_window_table(self):
        for rehearsal in (False, True):
            for prefixed in (False, True):
                with self.subTest(rehearsal=rehearsal, prefixed=prefixed):
                    case = PackNightProducerTests()
                    case._rehearsal_layout = True
                    case.setUp()
                    try:
                        measurement = case.root / "JouleWise-rehearsal-producer-table"
                        measurement.mkdir()
                        case._window_id = case.custody.name if prefixed else "production-window"
                        case.authorization.update(purpose="T0_REHEARSAL" if rehearsal else "CAMPAIGN_TRANSACTION",
                            authority="T0-UNATTENDED-01" if rehearsal else "V5-TRANSACTION-GO-01")
                        ref = case.write(case.custody / "authorization.json", case.authorization)
                        case.plan = replace(case.plan, measurement_root=str(measurement),
                            pack_night={**case.plan.pack_night, "authorization_record": ref})
                        write_night_plan(case.plan_path, case.plan)
                        inventory = [{"deployment_id": "production", "measurement_root": str(case.root / "production"),
                            "custody_root": None, "ledger_path": None, "notes": "synthetic"}]
                        with mock.patch.object(Path, "home", return_value=case.root / "home"), \
                             mock.patch.object(case.readiness, "__file__", str(measurement / "joulewise/arm_readiness.py")), \
                             mock.patch.object(case.readiness, "_production_inventory", return_value=inventory):
                            code, calls = case.run_driver()
                        path = case.custody / "night/go_receipt.json"
                        if rehearsal == prefixed:
                            self.assertEqual(code, case.driver.EXIT_GO)
                            go = json.loads(path.read_bytes())
                            case.readiness.validate_pack_night_go_receipt(go)
                            self.assertEqual(go["purpose"], case.authorization["purpose"])
                            self.assertIs(go["authorization"]["claim_eligible"], False)
                            self.assertEqual(len(go), 26)
                            self.assertEqual(len(calls), 1)
                        else:
                            self.assertEqual(code, case.driver.EXIT_REFUSED)
                            self.assertFalse(path.exists())
                            self.assertEqual(calls, [])
                            refusal = json.loads((case.custody / "night/refusal.json").read_bytes())
                            self.assertIn("rehearsal_purpose_on_production_id" if rehearsal else "purpose", str(refusal))
                    finally:
                        case.doCleanups()

    def test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule(self):
        home = self.root / "home"
        window_id = "rehearsal-t0-unattended-test"
        custody = home / "night-custody" / window_id
        custody.mkdir(parents=True)
        # Keep launcher identity real; this test isolates the root predicates.
        measurement = Path(self.readiness.__file__).resolve().parents[1]
        claim = self.root / "isolated-claim"
        claim.mkdir()
        plan = replace(self.plan, custody_root=str(custody), measurement_root=str(measurement))
        arm = {"pack": {"window_id": window_id}, "arm_context": {"custody_root": str(custody), "claim_runs_root": str(claim)}}
        inventory = [{"deployment_id": "production", "measurement_root": str(self.root / "production"), "custody_root": None, "ledger_path": None, "notes": "synthetic"}]
        with mock.patch.object(Path, "home", return_value=home), mock.patch.object(self.readiness, "_production_inventory", return_value=inventory), mock.patch.object(self.readiness, "REHEARSAL_CLONE_PREFIX", measurement.name):
            self.driver._pack_rehearsal_roots(plan, arm, "T0_REHEARSAL")
            # Every non-custody ARM path may live inside this rehearsal child.
            for key in ("claim_runs_root", "bound_runs_root", "quarantine_root",
                        "claim_backup_destination", "bound_backup_destination", "waiver_path"):
                own = custody / key
                own.mkdir()
                changed = {**arm, "arm_context": {**arm["arm_context"], key: str(own)}}
                self.driver._pack_rehearsal_roots(plan, changed, "T0_REHEARSAL")
                for production in (home / "night-custody/magistrate" / key,
                                   self.root / "production" / key):
                    production.mkdir(parents=True)
                    changed = {**arm, "arm_context": {**arm["arm_context"], key: str(production)}}
                    with self.subTest(key=key, production=production), self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                        self.driver._pack_rehearsal_roots(plan, changed, "T0_REHEARSAL")
            # Exercise equality and both containment directions without changing
            # the authenticated launcher or creating paths in the real checkout.
            for production in (measurement, measurement / "runs", measurement.parent):
                with self.subTest(production=production), self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                    with mock.patch.object(self.readiness, "_production_inventory", return_value=[{**inventory[0], "measurement_root": str(production)}]):
                        self.driver._pack_rehearsal_roots(plan, arm, "T0_REHEARSAL")
            for root in (custody.parent, custody / window_id, custody.parent / "another"):
                root.mkdir(parents=True, exist_ok=True)
                with self.subTest(root=root), self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                    self.driver._pack_rehearsal_roots(replace(plan, custody_root=str(root)), arm, "T0_REHEARSAL")
            for field in ("measurement_root", "custody_root"):
                alias = self.root / (field + "-alias")
                alias.symlink_to(Path(getattr(plan, field)), target_is_directory=True)
                with self.subTest(field=field), self.assertRaisesRegex(self.driver.PackNightRefusal, field):
                    self.driver._pack_rehearsal_roots(replace(plan, **{field: str(alias)}), arm, "T0_REHEARSAL")
            with self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                self.driver._pack_rehearsal_roots(replace(plan, custody_root=str(measurement)), arm, "T0_REHEARSAL")
            changed = {**arm, "arm_context": {**arm["arm_context"], "claim_runs_root": str(custody.parent)}}
            with self.assertRaisesRegex(self.driver.PackNightRefusal, "rehearsal_roots_not_disjoint"):
                self.driver._pack_rehearsal_roots(plan, changed, "T0_REHEARSAL")
            for purpose, changed_arm, detail in (
                ("G2B_SHAKEDOWN", arm, "purpose"),
                ("T0_REHEARSAL", {**arm, "pack": {"window_id": "production"}}, "rehearsal_purpose_on_production_id"),
            ):
                with self.assertRaisesRegex(self.driver.PackNightRefusal, detail) as caught:
                    self.driver._pack_rehearsal_roots(plan, changed_arm, purpose)
                self.assertEqual("launch_go_receipt_invalid", caught.exception.reason)

    def test_pack_rehearsal_gate_refuses_another_measurement_checkout(self):
        other = self.root / (self.readiness.REHEARSAL_CLONE_PREFIX + "other")
        other.mkdir()
        plan = replace(self.plan, measurement_root=str(other))
        arm = {"pack": {"window_id": "rehearsal-t0-unattended-test"}, "arm_context": {}}
        with self.assertRaisesRegex(self.driver.PackNightRefusal, "launcher is not the planned clone") as caught:
            self.driver._pack_rehearsal_roots(plan, arm, "T0_REHEARSAL")
        self.assertEqual("launch_go_receipt_invalid", caught.exception.reason)

    def test_pack_gate_requires_absolute_strict_custody_root(self):
        alias = self.root / "custody-alias"
        alias.symlink_to(self.custody, target_is_directory=True)
        for root in ("relative-custody", str(self.root / "missing-custody"), str(alias)):
            with self.subTest(root=root), self.assertRaisesRegex(night_gate.PackNightRefusal, "custody_root") as caught:
                night_gate._authenticate_pack_records(replace(self.plan, custody_root=root))
            self.assertEqual(caught.exception.reason, "launch_go_receipt_invalid")

    def test_window_expiring_during_final_authentication_emits_no_go(self):
        def expire(*args, **kwargs):
            self.probe_source.now_epoch_s = self.plan.t0_epoch_s + self.plan.window_max_s + 1
            return self.refs()
        self.readiness._attested_launch_artifact_references.side_effect = expire
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.assertFalse((self.custody / "night/go_receipt.json").exists())
        self.assertIn("conditions.C5.window_expired", (self.custody / "night/receipt.json").read_text())

    def test_existing_go_alone_prevents_rearm_and_is_in_custody_inventory(self):
        path = self.custody / "night/go_receipt.json"
        raw = self.readiness.render_json({"fixture": "existing GO"})
        path.parent.mkdir()
        path.write_bytes(raw)
        code, calls = self.run_driver()
        self.assertEqual(self.driver.EXIT_REFUSED, code)
        self.assertEqual([], calls)
        self.author.author_arm_readiness_evidence_t0.assert_not_called()
        self.assertEqual(raw, path.read_bytes())
        self.assertIn({"path": "night/go_receipt.json", "sha256": self.readiness.sha256_bytes(raw)}, self.driver._artifact_list(self.custody, path.parent))


if __name__ == "__main__":
    unittest.main()
