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
            with custodian.intercept_popen():
                helper = threading.Thread(target=lambda: returned.append(
                    subprocess.Popen(["/usr/bin/powermetrics", "-o", "elsewhere"])))
                helper.start()
                helper.join()
                self.assertIs(returned[0], helper_process)
                self.assertFalse(custodian.spawned)
                subprocess.Popen(["/usr/bin/powermetrics", "-o", "capture"])
        self.assertTrue(custodian.spawned)
        self.assertEqual(custodian._direct_child_pid, 302)

if __name__ == "__main__":
    unittest.main()
