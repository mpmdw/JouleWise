"""Busy-only controller admission survives the desk with raw CPU evidence intact."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import run_campaign as runner
from joulewise.environment_admission import environment_admission_refusals
from tests import test_run_campaign as fixtures


class BusyFractionDeskTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.fixture = fixtures.IdleAdmissionCoreVerdictTests()
        self.fixture.root = Path(temporary.name)
        path = self.fixture._write_extended_sidecar(mutate=lambda p: p[
            "idle_admission_extension"]["cpu_criteria"].update(
                cpu_busy_ratio_p95_max=0.30, min_samples=576))
        self.binding = runner.load_campaign_policy(str(path))
        # This member-only test has no NEG-8 references; isolate their unrelated
        # not-evaluated diagnostic, keeping CPU/environment/adapter checks real.
        bracket = mock.patch.object(runner, "neg8_bracket_not_evaluated",
                                    return_value={"conditions": []})
        bracket.start()
        self.addCleanup(bracket.stop)

    def member(self, *, signal=True, power=0.4, decision="admitted"):
        records = [{"processor_combined_power_w": power,
                    "clusters": [{"cpus": [{"idle_ratio": 1 - busy, "down_ratio": 0.0}]}]}
                   for busy in [0.10] * 540 + [0.60] * 36]
        member = self.fixture._member("member", records=records, admission_decision=decision)
        row = member.metadata["environment_admission"]["attempts"][-1]
        row["gpu_admitted"] = True
        row["cpu_admission"] = runner.evaluate_cpu_idle_admission(
            records, self.binding.idle_admission_extension.cpu_criteria, gpu_admitted=True)
        if signal:
            row["busy_fraction_admitted"] = True
        return member

    def test_busy_only_admission_keeps_member_and_evaluator_output(self):
        member = self.member()
        expected = copy.deepcopy(member.metadata["environment_admission"]["attempts"][-1]["cpu_admission"])
        self.assertEqual(expected["conditions"], ["cpu_busy_ratio_p95_exceeded"])
        result = runner._idle_admission_core_evaluation([member], self.binding)
        self.assertEqual(result.member_failures, ())
        self.assertEqual(result.core["conditions"], [])
        self.assertEqual(result.core["members"][0]["cpu_admission"], expected)
        self.assertFalse(expected["admitted"])
        self.assertNotIn("cpu_admission_core_failed", runner._idle_admission_claim_barrier_reasons(result.core))

    def test_block5_shape_without_signal_keeps_busy_member_failure(self):
        member = self.member(signal=False, decision="abort")
        result = runner._idle_admission_core_evaluation([member], self.binding)
        self.assertIn("cpu_busy_ratio_p95_exceeded", result.core["conditions"])
        self.assertIn("cpu_busy_ratio_p95_exceeded", {r["reason_code"] for r in result.member_failures})
        self.assertIn("cpu_admission_core_failed", runner._idle_admission_claim_barrier_reasons(result.core))

    def test_admitted_bit_alone_does_not_opt_in(self):
        result = runner._idle_admission_core_evaluation([self.member(signal=False)], self.binding)
        self.assertIn("cpu_busy_ratio_p95_exceeded", {r["reason_code"] for r in result.member_failures})

    def test_power_failure_with_signal_still_excludes(self):
        result = runner._idle_admission_core_evaluation([self.member(power=1.5)], self.binding)
        self.assertIn("processor_combined_power_w_p95_exceeded", result.core["conditions"])
        self.assertIn("processor_combined_power_w_p95_exceeded", {r["reason_code"] for r in result.member_failures})
        self.assertNotIn("cpu_busy_ratio_p95_exceeded", result.core["conditions"])
        self.assertIn("cpu_admission_core_failed", runner._idle_admission_claim_barrier_reasons(result.core))

    def test_core_barrier_requires_final_marker_and_both_cpu_results_busy_only(self):
        core = runner._idle_admission_core_evaluation([self.member()], self.binding).core
        for case in ("not_admitted", "marker_absent", "metadata_power_failure", "core_power_failure"):
            with self.subTest(case=case):
                mutated = copy.deepcopy(core)
                member = mutated["members"][0]
                final = member["final_admission_attempt"]
                if case == "not_admitted":
                    final["admitted"] = False
                elif case == "marker_absent":
                    final.pop("busy_fraction_admitted")
                else:
                    cpu = final["cpu_admission"] if case == "metadata_power_failure" else member["cpu_admission"]
                    cpu["conditions"].append("processor_combined_power_w_p95_exceeded")
                self.assertIn("cpu_admission_core_failed", runner._idle_admission_claim_barrier_reasons(mutated))

    def test_other_derived_conditions_with_signal_still_fail(self):
        member = self.member()
        for condition in ("cpu_baseline_telemetry_missing", "gpu_idle_admission_not_passed"):
            with self.subTest(condition=condition), mock.patch.object(
                    runner, "evaluate_cpu_idle_admission", return_value={
                        "admitted": False, "conditions": ["cpu_busy_ratio_p95_exceeded", condition]}):
                result = runner._idle_admission_core_evaluation([member], self.binding)
                self.assertIn(condition, result.core["conditions"])
                self.assertIn(condition, {r["reason_code"] for r in result.member_failures})

    def test_attempt_validators_accept_extra_signal_and_clear_busy_only_refusal(self):
        member = self.member(signal=False)
        admission = member.metadata["environment_admission"]
        before = environment_admission_refusals(admission)
        self.assertEqual(before, ("environment_admission_failed",))
        self.assertNotIn("environment_admission_missing", before)
        admission["attempts"][-1]["busy_fraction_admitted"] = True
        self.assertEqual(environment_admission_refusals(admission), ())
        self.assertEqual(runner._final_idle_admission_attempt(member), 1)


if __name__ == "__main__":
    unittest.main()
