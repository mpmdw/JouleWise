"""Focused driver tests using a small injected night-gate contract fake."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_night.py"


class FakeRefusal:
    def __init__(self, reason: str, detail: str = "detail", evidence: object = None) -> None:
        self.reason = reason
        self.detail = detail
        self.evidence = evidence


class FakeProbeResult:
    def __init__(self, argv, exit_code, stdout, stderr, monotonic_ns) -> None:
        self.argv = tuple(argv)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.monotonic_ns = monotonic_ns


class FakePlan:
    def __init__(self, mapping: dict[str, object]) -> None:
        self.plan_id = str(mapping["plan_id"])
        self.receipt_class = str(mapping["receipt_class"])
        self.t0_epoch_s = float(mapping.get("t0_epoch_s", 1_788_000_000))
        self.window_max_s = float(mapping.get("window_max_s", 600))
        self.authored_epoch_s = float(mapping.get("authored_epoch_s", 1_788_000_000))
        self.repo_head = str(mapping["repo_head"])
        self.chain_path = str(mapping["chain_path"])
        self.chain_sha256_path = str(mapping["chain_sha256_path"])
        self.custody_root = str(mapping["custody_root"])
        self.registration_path = str(mapping.get("registration_path", "registration.json"))

    @classmethod
    def from_mapping(cls, mapping: dict[str, object]):
        return cls(mapping)


class FakeReceipt:
    def __init__(self, plan: FakePlan, verdict: str, refusal: FakeRefusal | None = None) -> None:
        self.plan_id = plan.plan_id
        self.receipt_class = plan.receipt_class
        self.verdict = verdict
        self.refusal = refusal

    def to_json_bytes(self) -> bytes:
        refusal = None if self.refusal is None else self.refusal.__dict__
        return (json.dumps({"plan_id": self.plan_id, "verdict": self.verdict, "refusal": refusal}) + "\n").encode()


class FakeProbes:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


def _gate_module() -> types.ModuleType:
    module = types.ModuleType("joulewise.night_gate")
    module.SCHEMA = "test.receipt"
    module.RESULT_SCHEMA = "test.result"
    module.NightPlan = FakePlan
    module.ProbeResult = FakeProbeResult
    module.Probes = FakeProbes
    module.receipt_verdict = "GO"
    module.receipt_refusal = None
    module.census_responses = []

    def evaluate(plan, _probes):
        return FakeReceipt(plan, module.receipt_verdict, module.receipt_refusal)

    def agent_census(_probes):
        if module.census_responses:
            return module.census_responses.pop(0)
        return FakeProbeResult(("pgrep",), 1, "", "", 1), None

    module.evaluate_night = evaluate
    module.agent_census = agent_census
    return module


def _load_driver(gate: types.ModuleType):
    previous = sys.modules.get("joulewise.night_gate")
    sys.modules["joulewise.night_gate"] = gate
    try:
        spec = importlib.util.spec_from_file_location("run_night_test_module", SCRIPT_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            del sys.modules["joulewise.night_gate"]
        else:
            sys.modules["joulewise.night_gate"] = previous


class FakeProcess:
    def __init__(self, argv, return_code: int = 0, running_once: bool = False) -> None:
        self.argv = argv
        self.return_code = return_code
        self.running_once = running_once
        self.pid = 4242
        self._poll_count = 0

    def poll(self):
        self._poll_count += 1
        if self.running_once and self._poll_count == 1:
            return None
        return self.return_code

    def wait(self, timeout=None):
        return self.return_code


class NightDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = _gate_module()
        self.driver = _load_driver(self.gate)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.chain = self.root / "chain.zsh"
        self.chain.write_text("echo chain\n", encoding="utf-8")
        self.sidecar = self.root / "chain.zsh.sha256"
        self.sidecar.write_text(
            f"{self.driver._sha256_path(self.chain)}  chain.zsh\n", encoding="utf-8"
        )
        self.plan_path = self.root / "plan.json"
        self.plan_path.write_text(
            json.dumps(
                {
                    "plan_id": "night-plan",
                    "receipt_class": "DIAGNOSTIC_NO_PACK",
                    "repo_head": "f" * 40,
                    "chain_path": str(self.chain),
                    "chain_sha256_path": str(self.sidecar),
                    "custody_root": str(self.custody),
                }
            ),
            encoding="utf-8",
        )
        self.real_durable_record = self.driver._durable_record
        self.driver._durable_record = mock.Mock()
        self.real_run_courier = self.driver.run_courier
        self.driver.run_courier = mock.Mock(return_value=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _popen_recorder(self, return_code: int = 0, running_once: bool = False):
        calls = []

        def spawn(argv=None, *args, **kwargs):
            calls.append(kwargs.get("args", argv))
            return FakeProcess(kwargs.get("args", argv), return_code, running_once)

        return calls, spawn

    def test_refusal_writes_receipt_and_refusal_without_spawning_chain(self) -> None:
        self.gate.receipt_verdict = "REFUSED"
        self.gate.receipt_refusal = FakeRefusal("night_refused_agent_present")
        calls, spawn = self._popen_recorder()
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 3)
        night = self.custody / "night"
        self.assertTrue((night / "receipt.json").is_file())
        self.assertTrue((night / "refusal.json").is_file())
        self.assertEqual(calls, [])

    def test_go_spawns_chain_once_even_if_the_chain_fails(self) -> None:
        calls, spawn = self._popen_recorder(return_code=17)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path), 5)
        self.assertEqual(calls, [["/bin/zsh", str(self.chain)]])
        result = json.loads((self.custody / "night" / "result.json").read_text())
        self.assertEqual(result["chain_exit_code"], 17)

    def test_census_refusal_terminates_group_and_records_abort(self) -> None:
        self.gate.census_responses = [
            (FakeProbeResult(("pgrep",), 0, "agent", "", 2), FakeRefusal("night_refused_agent_present"))
        ]
        calls, spawn = self._popen_recorder(running_once=True)
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.os, "killpg"
        ) as kill_group, mock.patch.object(self.driver.time, "sleep"):
            self.assertEqual(self.driver.run_night(self.plan_path), 4)
        kill_group.assert_called_once()
        refusal = json.loads((self.custody / "night" / "refusal.json").read_text())
        self.assertEqual(refusal["refusal"]["reason"], "night_aborted_agent_present")

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

    def test_rehearsal_refuses_a_non_rehearsal_plan(self) -> None:
        calls, spawn = self._popen_recorder()
        with mock.patch.object(self.driver.subprocess, "Popen", spawn):
            self.assertEqual(self.driver.run_night(self.plan_path, rehearsal=True), 3)
        self.assertEqual(calls, [])

    def test_clone_failure_does_not_change_a_go_exit_code(self) -> None:
        calls, spawn = self._popen_recorder()
        self.driver._durable_record = self.real_durable_record
        with mock.patch.object(self.driver.subprocess, "Popen", spawn), mock.patch.object(
            self.driver.subprocess, "run", side_effect=OSError("clone unavailable")
        ):
            self.assertEqual(self.driver.run_night(self.plan_path), 0)
        self.assertEqual(len(calls), 1)

    def test_courier_argv_has_the_reviewed_shape(self) -> None:
        plan = self.driver._load_plan(self.plan_path)
        argv = self.driver._courier_argv(self.custody, plan)
        self.assertEqual(argv[:3], ("/usr/bin/env", "claude", "-p"))
        self.assertEqual(argv[-4:], ("--output-format", "text", "--allowedTools", self.driver.COURIER_ALLOWED_TOOLS))
        self.assertIn(str(self.custody), argv[3])
        self.assertIn(plan.plan_id, argv[3])

    def test_launch_agent_template_and_installer_stay_user_level(self) -> None:
        template = (REPO_ROOT / "configs" / "launchd" / "com.joulewise.night.plist.template").read_text()
        installer = (REPO_ROOT / "scripts" / "install_night_agent.sh").read_text()
        self.assertIn("com.joulewise.night", template)
        self.assertIn("@@HOUR@@", template)
        self.assertIn("@@MINUTE@@", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/launchd.out", template)
        self.assertIn("@@CUSTODY_ROOT@@/night/launchd.err", template)
        self.assertEqual(installer.count("sudo"), 0)
        self.assertIn("dead-man", installer)


if __name__ == "__main__":
    unittest.main()
