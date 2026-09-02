"""Focused driver tests against the real night-gate module."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from joulewise import night_gate


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
        )


def _load_driver():
    spec = importlib.util.spec_from_file_location("run_night_test_module", SCRIPT_PATH)
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


class NightDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = _load_driver()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.chain = self.root / "chain.zsh"
        self.chain.write_text("echo chain\n", encoding="utf-8")
        self.sidecar = self.root / "chain.zsh.sha256"
        self.sidecar.write_text(
            hashlib.sha256(self.chain.read_bytes()).hexdigest() + "\n", encoding="utf-8"
        )
        self.registration = self.root / "registration.json"
        self.registration.write_text('{"registered":true}\n', encoding="utf-8")
        self.t0_epoch_s = datetime(2026, 9, 2, 1, 0).timestamp()
        self.source = ProbeSource(self.t0_epoch_s + 1)
        self.plan_path = self.root / "plan.json"
        self._write_plan()
        self.registration_hash_patch = mock.patch.object(
            night_gate,
            "D166_REGISTRATION_SHA256",
            hashlib.sha256(self.registration.read_bytes()).hexdigest(),
        )
        self.registration_hash_patch.start()
        self.probes_patch = mock.patch.object(
            self.driver, "make_probes", return_value=self.source.probes()
        )
        self.probes_patch.start()
        self.real_durable_record = self.driver._durable_record
        self.driver._durable_record = mock.Mock()
        self.real_run_courier = self.driver.run_courier
        self.driver.run_courier = mock.Mock(return_value=True)

    def tearDown(self) -> None:
        self.probes_patch.stop()
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
        self.plan_path.write_text(
            json.dumps(
                {
                    "schema": night_gate.PLAN_SCHEMA,
                    "plan_id": "night-plan",
                    "receipt_class": receipt_class,
                    "t0_epoch_s": t0,
                    "window_max_s": window_max_s,
                    "authored_epoch_s": t0 - 1,
                    "repo_head": HEAD,
                    "chain_path": str(self.chain),
                    "chain_sha256_path": str(self.sidecar),
                    "custody_root": str(self.custody),
                    "registration_path": str(self.registration),
                }
            ),
            encoding="utf-8",
        )

    def _popen_recorder(self, return_code: int = 0, running_once: bool = False):
        calls = []

        def spawn(argv, *args, **kwargs):
            calls.append(argv)
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
        self.assertIn("epoch", exited)
        self.assertIn("monotonic_ns", exited)

    def test_chain_claim_prevents_a_second_spawn_after_a_failed_chain(self) -> None:
        calls, spawn = self._popen_recorder(return_code=17)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 5)
            self.assertEqual(self.driver.run_night(self.plan_path), 3)
        night = self.custody / "night"
        claim = json.loads((night / "chain.started").read_text())
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        self.assertEqual(
            set(claim), {"driver_pid", "epoch", "monotonic_ns", "plan_id"}
        )
        self.assertEqual(claim["driver_pid"], os.getpid())
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["chain_already_started"]
        )

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
        kill_group.assert_called_once()
        night = self.custody / "night"
        refusal = json.loads((night / "refusal.json").read_text())
        exited = json.loads((night / "chain.exited").read_text())
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["aborted_agent_present"]
        )
        self.assertEqual(exited["exit_code"], 0)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])

    def test_courier_tries_three_times_with_the_declared_backoffs(self) -> None:
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
                self.assertFalse(self.driver.run_courier(self.custody, plan))
        finally:
            self.driver.COURIER_DEADLINE_S = old_deadline
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [60, 180])
        self.assertEqual(self.driver.COURIER_BACKOFF_S, (60, 180, 600))

    def test_dead_man_skips_when_courier_sent_exists(self) -> None:
        sent = self.custody / "night" / "courier.sent"
        sent.parent.mkdir()
        sent.write_text("sent\n", encoding="utf-8")
        self.assertEqual(self.driver.dead_man(self.plan_path), 0)
        self.driver.run_courier.assert_not_called()

    def test_dead_man_refuses_while_the_chain_is_alive_without_spawning(self) -> None:
        night = self.custody / "night"
        night.mkdir()
        (night / "chain.started").write_text("claimed\n", encoding="utf-8")
        calls, spawn = self._popen_recorder()
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.dead_man(self.plan_path), 3)
        refusal = json.loads((night / "refusal.json").read_text())
        self.assertEqual(
            refusal["refusal"]["reason"], self.driver._CODES["chain_alive"]
        )
        self.assertEqual(calls, [])
        self.driver.run_courier.assert_not_called()

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
        self.assertEqual(gate_calls, [])
        self.assertEqual(calls, [])

    def test_rehearsal_refuses_a_non_rehearsal_plan(self) -> None:
        exit_code, calls = self._run_night(rehearsal=True)
        self.assertEqual(exit_code, 3)
        self.assertEqual(calls, [])

    def test_clone_failure_does_not_change_a_go_exit_code(self) -> None:
        self.driver._durable_record = self.real_durable_record
        calls, spawn = self._popen_recorder()
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.subprocess, "run", side_effect=OSError("clone unavailable")
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        self.assertEqual(len(calls), 1)

    def test_courier_argv_has_the_reviewed_shape(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        argv = self.driver._courier_argv(self.custody, plan)
        self.assertEqual(argv[:3], ("/usr/bin/env", "claude", "-p"))
        self.assertEqual(
            argv[-4:],
            ("--output-format", "text", "--allowedTools", self.driver.COURIER_ALLOWED_TOOLS),
        )
        self.assertIn(str(self.custody), argv[3])
        self.assertIn(plan.plan_id, argv[3])

    def test_launch_agent_template_disables_restart_and_installer_rejects_keepalive(self) -> None:
        template = (
            REPO_ROOT / "configs" / "launchd" / "com.joulewise.night.plist.template"
        ).read_text()
        installer = (REPO_ROOT / "scripts" / "install_night_agent.sh").read_text()
        self.assertIn("com.joulewise.night", template)
        self.assertIn("@@HOUR@@", template)
        self.assertIn("@@MINUTE@@", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/launchd.out", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/launchd.err", template)
        self.assertNotIn("<key>KeepAlive</key>", template)
        self.assertIn("<key>RunAtLoad</key>\n  <false/>", template)
        self.assertIn('/usr/bin/grep -q "KeepAlive"', installer)
        self.assertIn("DEADMAN_HOUR", installer)
        self.assertIn("DEADMAN_MINUTE", installer)
        self.assertNotIn("<integer>7</integer>", template)
        self.assertNotIn("<integer>7</integer>", installer)
        self.assertEqual(installer.count("sudo"), 0)

    def test_driver_reason_codes_are_registered_and_are_not_literal_call_sites(self) -> None:
        registered = night_gate.NIGHT_GATE_REASON_CODES | night_gate.NIGHT_DRIVER_REASON_CODES
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        literal_lines = [
            line
            for line in source.splitlines()
            if '"night_' in line and "_CODES" not in line
        ]
        self.assertTrue(set(self.driver._CODES.values()) <= registered)
        self.assertEqual(literal_lines, [])


if __name__ == "__main__":
    unittest.main()
