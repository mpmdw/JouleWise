"""Gate-prune round 2, lane P2-CTL, M4 controller part (PLAN2 t1-07 safe
variant): on a HAZARD root the before_attempt_1 guard probes run during the
admission sampler's start, and the sampler spawn seam adopts only the thread
that entered it."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise import controller
from joulewise.flags import core as flags_core
from joulewise.sampler_teardown import SamplerTeardown
from joulewise.schemas import BenchmarkConfig, CampaignPolicy, RunStatus
from tests.test_controller import (
    EXAMPLE_CONFIG_PATH,
    PRODUCTION_POLICY_PATH,
    CleanAdmissionPowermetricsAdapter,
    FakeProcessPowermetricsRegistry,
)
from tests.test_controller_hazard_flags import WRITER
from tests.test_sampler_teardown import FakeProcess
from tests import child_guard


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()



class _SignallingAdapter(CleanAdmissionPowermetricsAdapter):
    begin_entered: threading.Event

    def begin_admission_window_sampling(self, config, context=None):
        type(self).begin_entered.set()
        return super().begin_admission_window_sampling(config, context)


class _SignallingRegistry(FakeProcessPowermetricsRegistry):
    adapter_type = _SignallingAdapter


class GuardProbeDuringSamplerStartTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.custody = Path(tmp.name) / "custody"
        self.custody.mkdir()
        self.context = flags_core.HazardFlagContext(
            writer=WRITER, custody_root=self.custody, plan_id=None, attempt=None,
            scope_resolved=False)

    def run_member(self, run_id: str) -> tuple[Path, Any, list[dict[str, Any]]]:
        """``tests.test_controller._produce_admission_powermetrics_bundle`` with a
        guard probe that reports whether the sampler start had begun."""

        _SignallingAdapter.begin_entered = threading.Event()
        calls: list[dict[str, Any]] = []
        clean = {"power_source": "AC Power", "display_power_state": "all_asleep",
                 "screensaver_engaged": False,
                 "power": {"adapter_watts": 140.0, "adapter_description": "synthetic adapter"},
                 "errors": {}}

        def observe(**_kwargs):
            on_helper = threading.current_thread() is not threading.main_thread()
            if not calls and on_helper:
                _SignallingAdapter.begin_entered.wait(10.0)
            calls.append({"helper_thread": on_helper,
                          "sampler_start_begun": _SignallingAdapter.begin_entered.is_set()})
            return json.loads(json.dumps(clean))

        payload = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        payload["run_id"] = run_id
        payload["hardware_target"].update({"id": "synthetic_mac", "telemetry_backend": "powermetrics"})
        payload["sampling"].update({"power_hz": 20.0, "idle_seconds": 1.5})
        config = BenchmarkConfig.from_mapping(payload)
        policy_bytes = PRODUCTION_POLICY_PATH.read_bytes()
        policy = CampaignPolicy.from_mapping(json.loads(policy_bytes))
        snapshot = {"power_source": "AC Power", "power": {"external_connected": True},
                    "low_power_mode": False, "display_power_state": "all_asleep",
                    "screensaver_engaged": False, "thermal_pressure": "nominal"}
        from joulewise.clock import SystemClock
        from joulewise.environment import evaluate_environment_policy

        preflight = {"schema_version": "joulewise.campaign_environment_preflight.v1",
                     "policy_sha256": sha256(policy_bytes), "snapshot": snapshot,
                     "evaluation": evaluate_environment_policy(snapshot, policy.environment_guard),
                     "override": None, "admitted": True}
        binding = {"schema_version": policy.schema_version, "policy_id": policy.policy_id,
                   "policy_version": policy.policy_version, "profile": policy.profile.value,
                   "sha256": sha256(policy_bytes), "source": str(PRODUCTION_POLICY_PATH)}
        with patch("joulewise.controller.collect_environment_guard_observation", side_effect=observe):
            bundle, summary = controller.run_benchmark(
                config, self.runs_root, SystemClock(), registry=_SignallingRegistry(),
                environment_snapshot=snapshot, campaign_policy=policy,
                campaign_policy_binding=binding, campaign_environment_preflight=preflight,
                post_window_sampling_dwell_s=1.0)
        return bundle, summary, calls

    def test_hazard_probe_runs_during_sampler_start_and_the_sampler_is_still_adopted(self) -> None:
        with patch.object(flags_core, "hazard_flag_context", return_value=self.context):
            bundle, summary, calls = self.run_member("hazard-m4-probe")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(calls[0], {"helper_thread": True, "sampler_start_begun": True})
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        phases = [row["phase"] for row in metadata["environment_admission"]["guard_observations"]]
        self.assertEqual(phases[:2], ["before_attempt_1", "after_attempt_1"])
        teardown = metadata["uncertainty_evidence"]["process_group_teardown"]
        self.assertTrue(teardown["spawn_observed"])
        self.assertEqual(teardown["status"], "clean")

    def test_legacy_probe_runs_before_sampler_start(self) -> None:
        bundle, summary, calls = self.run_member("legacy-m4-probe")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(calls[0], {"helper_thread": False, "sampler_start_begun": False})


class SpawnSeamThreadTests(unittest.TestCase):
    def test_a_sampler_shaped_spawn_from_another_thread_is_not_adopted(self) -> None:
        helper_process, sampler_process = FakeProcess(301), FakeProcess(302)
        custodian = SamplerTeardown(termination_grace_s=0.0, census_timeout_s=0.0)
        returned: list[Any] = []
        with patch("joulewise.sampler_teardown.subprocess.Popen",
                   side_effect=[helper_process, sampler_process]), \
                patch("joulewise.sampler_teardown.os.setpgid"):
            with custodian.intercept_popen(owner_thread_only=True):
                helper = threading.Thread(target=lambda: returned.append(
                    subprocess.Popen(["/usr/bin/powermetrics", "-o", "elsewhere"])))
                helper.start()
                helper.join()
                self.assertIs(returned[0], helper_process)
                self.assertFalse(custodian.spawned)
                subprocess.Popen(["/usr/bin/powermetrics", "-o", "capture"])
        self.assertTrue(custodian.spawned)
        self.assertEqual(custodian._direct_child_pid, 302)

    def test_legacy_seam_still_adopts_a_sampler_spawn_from_another_thread(self) -> None:
        # Review F1: the thread filter is HAZARD-only; the default seam keeps
        # the base behaviour (first sampler spawn from any thread is adopted).
        custodian = SamplerTeardown(termination_grace_s=0.0, census_timeout_s=0.0)
        with patch("joulewise.sampler_teardown.subprocess.Popen",
                   return_value=FakeProcess(302)), \
                patch("joulewise.sampler_teardown.os.setpgid"):
            with custodian.intercept_popen():
                helper = threading.Thread(
                    target=lambda: subprocess.Popen(["/usr/bin/powermetrics", "-o", "capture"]))
                helper.start()
                helper.join()
        self.assertTrue(custodian.spawned)
        self.assertEqual(custodian._direct_child_pid, 302)


class GuardProbeSafetyTests(unittest.TestCase):
    """Review F2/F5: the probe's work ends before idle and before a failed
    member returns; its error cannot become success; legacy has no helper."""

    def fixture(self) -> GuardProbeDuringSamplerStartTests:
        case = GuardProbeDuringSamplerStartTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def test_probe_finishes_before_the_idle_capture(self) -> None:
        case = self.fixture()
        started, entered_idle, done = threading.Event(), threading.Event(), threading.Event()
        original_init = controller._GuardProbe.__init__
        original_start = controller._Execution._start_telemetry_with_parent_adoption
        original_measure = controller._Execution._measure_idle_admission_attempt

        def init(probe, collect):
            def delayed():
                started.wait(10)
                entered_idle.wait(0.5)
                result = collect()
                done.set()
                return result
            original_init(probe, delayed)

        def start(execution, *args, **kwargs):
            result = original_start(execution, *args, **kwargs)
            started.set()
            return result

        def measure(execution, *args, **kwargs):
            completed = done.is_set()
            entered_idle.set()
            if not completed:
                raise AssertionError("guard probe still running when idle starts")
            return original_measure(execution, *args, **kwargs)

        with patch.object(flags_core, "hazard_flag_context", return_value=case.context), \
                patch.object(controller._GuardProbe, "__init__", init), \
                patch.object(controller._Execution, "_start_telemetry_with_parent_adoption", start), \
                patch.object(controller._Execution, "_measure_idle_admission_attempt", measure):
            _bundle, summary, _calls = case.run_member("probe-before-idle")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)

    def test_a_probe_error_fails_the_member(self) -> None:
        case = self.fixture()
        original = controller._Execution._guard_observation_payload

        def payload(execution):
            if threading.current_thread().name == "joulewise-guard-probe":
                raise RuntimeError("synthetic probe failure")
            return original(execution)

        with patch.object(flags_core, "hazard_flag_context", return_value=case.context), \
                patch.object(controller._Execution, "_guard_observation_payload", payload):
            _bundle, summary, _calls = case.run_member("probe-error")
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertIn("synthetic probe failure", summary.failure_message)

    def test_legacy_runs_no_helper_probe(self) -> None:
        case = self.fixture()
        _bundle, summary, calls = case.run_member("legacy-no-helper")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertTrue(calls)
        self.assertTrue(all(not call["helper_thread"] for call in calls), calls)

    def test_a_failed_sampler_start_waits_for_the_probe(self) -> None:
        case = self.fixture()
        ready, release, done = threading.Event(), threading.Event(), threading.Event()
        original_payload = controller._Execution._guard_observation_payload

        def payload(execution):
            if threading.current_thread().name == "joulewise-guard-probe":
                ready.set()
                release.wait(30)
                try:
                    return original_payload(execution)
                finally:
                    done.set()
            return original_payload(execution)

        def start(execution, *args, **kwargs):
            ready.wait(10)
            # Let the probe finish shortly after the failure is raised: the
            # member must still be inside run_benchmark when that happens.
            threading.Timer(0.3, release.set).start()
            raise RuntimeError("synthetic sampler start failure")

        try:
            with patch.object(flags_core, "hazard_flag_context", return_value=case.context), \
                    patch.object(controller._Execution, "_guard_observation_payload", payload), \
                    patch.object(controller._Execution, "_start_telemetry_with_parent_adoption", start):
                _bundle, summary, _calls = case.run_member("failed-sampler-start")
            self.assertEqual(summary.status, RunStatus.FAILED)
            self.assertIn("synthetic sampler start failure", summary.failure_message)
            self.assertTrue(done.is_set(), "guard probe outlived the failed member")
        finally:
            release.set()
            done.wait(10)


# Test hygiene (2026-10-07): a test or class in this module that leaves a child process running
# is reported as failed, and the child is stopped (tests/child_guard.py).
child_guard.guard_test_classes(globals())


if __name__ == "__main__":
    unittest.main()
