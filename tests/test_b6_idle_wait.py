"""Waiting admission through the controller on synthetic telemetry and clocks."""
from dataclasses import replace
from contextlib import nullcontext
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from joulewise import controller
from joulewise.b6.idle_wait import WaitLedger, abandon_admission_sampling, busy_fraction_only, next_step
from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter, RAW_SAMPLES_NAME
from joulewise.clock import FakeClock
from joulewise.flags import core as flags_core
from joulewise.interfaces import AdapterResult
from joulewise.schemas import RunStatus
from tests.test_controller import AdmissionIdleRegistry, campaign_policy_fixture, make_config


class B6AdmissionAbandonTests(unittest.TestCase):
    def test_abandon_discards_stream_preserves_attempt_slice_and_counter(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as directory:
            adapter = PowermetricsTelemetryAdapter(FakeClock())
            stream = Path(directory) / "stream"
            stream.write_bytes(b"discarded stream tail")
            attempt = Path(directory) / "persisted-attempt"
            attempt.write_bytes(b"retained idle slice")
            process = Mock()
            process.poll.return_value = None
            adapter._process = process
            adapter._capture_path = stream
            adapter._pending_captures[RAW_SAMPLES_NAME] = stream
            adapter._idle_attempts_by_run["run"] = 3
            adapter._idle_admission_records_by_run["run"] = {3: [{"power": .1}]}
            adapter._admission_sampling_handoff_pending = True
            abandon_admission_sampling(adapter)
            process.terminate.assert_called_once()
            process.communicate.assert_called_once_with(timeout=10.0)
            self.assertIsNone(adapter._process)
            self.assertFalse(adapter._admission_sampling_handoff_pending)
            self.assertFalse(stream.exists())
            self.assertEqual(attempt.read_bytes(), b"retained idle slice")
            self.assertEqual(adapter._idle_attempts_by_run["run"], 3)
            self.assertEqual(adapter._idle_admission_records_by_run["run"][3], [{"power": .1}])


class IdleWaitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.hazard = flags_core.HazardFlagContext("core-controller", self.root, "plan", 1, True)
        self.ledger = WaitLedger(self.root / "collection/idle_wait.jsonl")

    def run_member(self, *, power=(5, 5, 5, .1), busy=(.1,), gpu=(False,),
                   record_count=None, cap=1500, budget=7200, native_name=False):
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        policy = replace(policy, idle_admission=replace(policy.idle_admission, wait_cap_s=cap,
                         session_wait_budget_s=budget, retry_backoff_s=300))
        config = make_config("wait-member")
        clock = FakeClock(start=1700000000)
        registry = AdmissionIdleRegistry(list(gpu), cpu_busy_sequence=list(busy), combined_power_sequence=list(power))
        resolve = registry.resolve_telemetry
        self.events, self.promoted = [], []
        def telemetry(*args):
            adapter, failure = resolve(*args)
            if record_count is not None:
                records = adapter.idle_admission_records
                adapter.idle_admission_records = lambda **kw: records(**kw)[:record_count]
            if native_name:
                adapter.name = "powermetrics"
            adapter.begin_admission_window_sampling = lambda *_: (self.events.append("begin") or AdapterResult(ok=True))
            adapter.abandon_admission_window_sampling = lambda **_: self.events.append("abandon")
            adapter.promote_idle_admission_attempt = lambda **kw: self.promoted.append(kw["attempt"])
            return adapter, failure
        registry.resolve_telemetry = telemetry
        with mock.patch.object(flags_core, "hazard_flag_context", return_value=self.hazard):
            path, summary = controller.run_benchmark(config, self.root / "runs", clock,
                registry=registry, environment_snapshot=snapshot, campaign_policy=policy,
                campaign_policy_binding=binding, campaign_environment_preflight=preflight)
        self.flags = [json.loads(line) for line in self.hazard.path.read_text().splitlines()]
        self.codes = [row["code"] for row in self.flags]
        self.rows = [json.loads(line) for line in self.ledger.path.read_text().splitlines()]
        self.admission = json.loads((path / "metadata.json").read_text())["environment_admission"]
        return summary

    def test_pass_on_attempt_four_restarts_promotes_records_one_wait(self):
        custodians = []
        def custodian():
            instance = mock.Mock(spawned=False, report={"status": "clean"})
            instance.teardown.return_value = {"status": "clean"}
            instance.intercept_popen.side_effect = lambda **_: nullcontext()
            custodians.append(instance)
            return instance
        with mock.patch.object(controller, "SamplerTeardown", side_effect=custodian):
            self.assertEqual(self.run_member(native_name=True).status, RunStatus.SUCCEEDED)
        self.assertEqual(len(custodians), 4)
        self.assertTrue(all(r["sampler_teardown"]["status"] == "clean" for r in self.admission["attempts"][:-1]))
        self.assertEqual(self.promoted, [4])
        self.assertEqual(self.events, ["begin", "abandon"] * 3 + ["begin"])
        self.assertEqual(self.codes.count("idle.waited"), 1)
        self.assertEqual(self.rows[-1]["outcome"], "admitted")
        self.assertEqual(self.admission["wait_s"], self.admission["attempts"][3]["sampler_start_s"] - self.admission["attempts"][0]["sampler_start_s"])
        self.assertEqual(self.admission["retry_backoff_ignored"], {"requested_s": 300})
        self.assertEqual([r["phase"] for r in self.admission["guard_observations"]],
                         [f"{when}_attempt_{k}" for k in range(1, 5) for when in ("before", "after")])

    def test_cap_skip_is_abort_and_ledger_consumes_added_attempt_time(self):
        self.assertEqual(self.run_member(power=(5,), cap=5).status, RunStatus.FAILED)
        self.assertEqual(self.admission["decision"], "abort")
        self.assertEqual(self.admission["skip_reason"], "wait_cap_reached")
        self.assertIn("idle.wait_cap_skip", self.codes)
        self.assertEqual(self.rows[-1]["outcome"], "skipped")
        attempts = self.admission["attempts"]
        self.assertEqual(self.rows[-1]["wait_s"], attempts[-1]["end_s"] - attempts[0]["end_s"])

    def test_spent_budget_still_attempts_first_baseline_then_skips(self):
        self.ledger.append(run_id="earlier", wait_s=7200, outcome="admitted")
        self.assertEqual(self.run_member(power=(5,)).status, RunStatus.FAILED)
        self.assertEqual(len(self.admission["attempts"]), 1)
        self.assertEqual(self.admission["skip_reason"], "wait_budget_exhausted")
        self.assertIn("idle.wait_budget_skip", self.codes)
        self.assertEqual(self.codes.count("idle.wait_budget_exhausted"), 1)
        self.assertEqual(self.rows[-1]["wait_s"], 0)
        self.assertTrue(self.ledger.remaining(7200) <= 0)
        self.assertTrue(self.ledger.exhausted_recorded)

    def test_partial_budget_shortens_cap(self):
        self.ledger.append(run_id="earlier", wait_s=7195, outcome="admitted")
        self.run_member(power=(5,))
        self.assertEqual(self.admission["effective_wait_cap_s"], 5)
        self.assertIn("idle.wait_budget_skip", self.codes)

    def test_unreadable_ledger_uses_full_cap_and_discloses(self):
        self.ledger.path.parent.mkdir()
        self.ledger.path.write_text("broken\n")
        # Read flags and metadata without parsing the deliberately malformed ledger.
        with mock.patch.object(WaitLedger, "append") as append:
            self.ledger.path.write_text('{"wait_s": "invalid"}\n')
            self.assertEqual(self.run_member(power=(.1,)).status, RunStatus.SUCCEEDED)
        self.assertIn("idle.wait_budget_unreadable", self.codes)
        self.assertEqual(self.admission["effective_wait_cap_s"], 1500)
        append.assert_called_once()

    def test_busy_fraction_only_admits_with_flag(self):
        self.assertEqual(self.run_member(power=(.1,), busy=(.9,)).status, RunStatus.SUCCEEDED)
        self.assertTrue(self.admission["attempts"][-1]["busy_fraction_admitted"])
        self.assertIn("idle.busy_fraction_exceeded", self.codes)
        self.assertEqual(self.events, ["begin"])
        self.assertEqual(len(self.admission["attempts"]), 1)

    def test_busy_fraction_with_only_a18_evidence_admits_with_both_flags(self):
        for gpu, count in ((False, 1), (None, 30), (None, 1)):
            with self.subTest(gpu=gpu, sample_count=count):
                self.assertEqual(self.run_member(power=(.1,), busy=(.9,), gpu=(gpu,),
                                                record_count=count).status, RunStatus.SUCCEEDED)
                self.assertEqual(len(self.admission["attempts"]), 1)
                self.assertEqual(self.admission["decision"], "admitted")
                self.assertIs(self.admission["reference_provenance_present"], False)
                self.assertIs(self.admission["attempts"][0]["cpu_admission"]["admitted"], False)
                self.assertIn("idle.busy_fraction_exceeded", self.codes)
                self.assertIn("member.idle_admission_telemetry_missing", self.codes)
                self.assertNotIn("idle.waited", self.codes)
                # Each subcase uses an independent member and ledger.
                import shutil
                shutil.rmtree(self.root / "runs")
                self.hazard.path.unlink()
                self.ledger.path.unlink()

    def test_busy_fraction_evidence_rule_rejects_physical_failures(self):
        evidence = controller._IDLE_ADMISSION_EVIDENCE_CONDITIONS
        for extra in ("processor_combined_power_w_p95_exceeded", "gpu_idle_admission_not_passed"):
            self.assertFalse(busy_fraction_only(
                {"conditions": ["cpu_busy_ratio_p95_exceeded", "cpu_baseline_sample_count_insufficient", extra],
                 "gpu_admitted": True}, evidence_conditions=evidence))
        self.run_member(power=(.1,), busy=(.9,), gpu=(True, False), record_count=1)
        self.assertEqual(len(self.admission["attempts"]), 2)
        self.assertIn("idle.waited", self.codes)

    def test_unwritable_ledger_discloses_records_failure_and_collects(self):
        self.ledger.path.parent.mkdir()
        self.ledger.path.write_text("")
        with mock.patch.object(WaitLedger, "append", side_effect=OSError("desk write fault")):
            self.assertEqual(self.run_member(power=(.1,)).status, RunStatus.SUCCEEDED)
        flag, = [row for row in self.flags if row["code"] == "idle.wait_ledger_unwritable"]
        self.assertEqual((flag["family"], flag["klass"]), ("RECORDS", "REPRESENTATION"))
        self.assertEqual(self.rows, [])
        self.assertNotIn("env.member_guard_flagged", self.codes)

    def test_power_failure_still_waits_and_budget_projection_is_strict(self):
        self.run_member(power=(5, .1), busy=(.9,))
        self.assertEqual(len(self.admission["attempts"]), 2)
        self.assertIn("idle.waited", self.codes)
        self.assertEqual(next_step(attempt_start_s=0, now_s=75, last_attempt_s=75, cap_s=150, remaining_s=200), "retry")
        self.assertEqual(next_step(attempt_start_s=0, now_s=76, last_attempt_s=75, cap_s=150, remaining_s=200), "skip_cap")
