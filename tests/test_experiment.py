"""Tests for the experiment runner: repetitions, manifests, cooldown gate.

Slice 2F (D-005 one-bundle-per-rep + experiment manifest; D-010 member IDs;
D-014 idle-power-recovery cooldown gate). Every test runs on a ``FakeClock`` in
a temp dir so the all-mock vertical slice is instant, deterministic, and never
touches the wall clock (D-019). The cooldown unit tests drive a stub telemetry
adapter so ``recovered`` / ``cap_hit`` branches are exercised without hardware.
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.aggregate import aggregate_experiment
from joulewise.adapters import resolve_runtime, resolve_transport
from joulewise.clock import Clock, FakeClock
from joulewise.cli import main, validate_bundle
from joulewise.controller import (
    COOLDOWN_CAP_S,
    COOLDOWN_SUBWINDOW_S,
    _member_gap_note,
    cooldown_gate,
    _cooldown_between_reps,
    run_experiment,
)
from joulewise.environment import evaluate_environment_policy
from joulewise.interfaces import AdapterResult, PowerSample, ThermalState
from joulewise.schemas import (
    BenchmarkConfig,
    CooldownPolicy,
    IdleBaseline,
    RunStatus,
    SummaryMetrics,
    TelemetryBackend,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"

#: The final experiment line shape the CLI contract pins.
EXPERIMENT_LINE = re.compile(r"^experiment: (\S+) members=(\d+)$")
BUNDLE_LINE = re.compile(r"^bundle: (\S+) status=(\w+)( reason=\w+)?$")

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _example_config_data() -> dict[str, Any]:
    return json.loads(EXAMPLE_CONFIG_PATH.read_text())


def make_config(run_id: str, repetitions: int, **overrides: Any) -> BenchmarkConfig:
    data = _example_config_data()
    data["run_id"] = run_id
    data["workload_profile"]["repetitions"] = repetitions
    for key, value in overrides.items():
        data[key] = value
    return BenchmarkConfig.from_mapping(data)


class DeterministicClock:
    """Non-Fake test clock that advances instantly without host time."""

    def __init__(self, start: float = 1_700_000_000.0) -> None:
        self._start = float(start)
        self._now = float(start)

    def now(self) -> float:
        return self._now

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("cannot sleep a negative duration")
        self._now += seconds

    def info(self) -> dict[str, Any]:
        return {"kind": "deterministic-test", "start_s": self._start}


def fake_environment_run(command, **kwargs):
    if tuple(command) == ("git", "rev-parse", "HEAD"):
        return subprocess.CompletedProcess(command, 0, "0" * 40 + "\n", "")
    outputs = {
        ("pmset", "-g", "batt"): "Now drawing from 'AC Power'\n -InternalBattery-0 100%; charged; 0:00 remaining\n",
        ("pmset", "-g"): " lowpowermode 0\n",
        ("pmset", "-g", "assertions"): "   PreventUserIdleDisplaySleep    0\n",
        ("pmset", "-g", "systemstate"): (
            "Current System Capabilities: Audio Network\n"
        ),
        ("pmset", "-g", "therm"): "No thermal warning level has been recorded\n",
        ("defaults", "-currentHost", "read", "com.apple.screensaver"): (
            "{ moduleDict = { moduleName = Ventura; }; idleTime = 1200; }\n"
        ),
        ("ioreg", "-c", "IOHIDSystem"): '"HIDIdleTime" = 5000000000\n',
        ("memory_pressure", "-Q"): "System-wide memory free percentage: 42.0%\n",
        ("vm_stat",): (
            "Mach Virtual Memory Statistics: (page size of 4096 bytes)\n"
            "Pages free: 1000.\n"
            "Pageins: 2000.\n"
            "Pageouts: 30.\n"
            "Pages occupied by compressor: 400.\n"
            "Pages stored in compressor: 500.\n"
        ),
        ("sysctl", "vm.swapusage"): "vm.swapusage: total = 1.00G used = 0.00M free = 1.00G\n",
        ("system_profiler", "SPDisplaysDataType", "-json"): """{
          "SPDisplaysDataType": [
            {
              "_name": "Apple GPU",
              "spdisplays_ndrvs": [
                {
                  "_name": "Built-in Display",
                  "spdisplays_online": "spdisplays_yes",
                  "spdisplays_connection_type": "spdisplays_internal"
                }
              ]
            }
          ]
        }""",
        ("ioreg", "-r", "-c", "IOMobileFramebuffer"): (
            "+-o IOMobileFramebufferShim  <class IOMobileFramebufferShim, id 0x1, registered>\n"
            '  |   "IONameMatched" = "disp0,t603x"\n'
        ),
        ("ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1"): (
            '"ExternalConnected" = Yes\n'
            '"IsCharging" = No\n'
            '"AdapterDetails" = {"Watts"=96,"Description"="USB-C"}\n'
        ),
        ("sysctl", "-n", "kern.boottime"): "{ sec = 1700000000, usec = 0 }\n",
        ("pgrep", "-x", "timed"): "123\n",
        ("uptime",): "12:00 up 1 day, load averages: 1.00 2.00 3.00\n",
        ("sw_vers",): "ProductName:\t\tmacOS\nProductVersion:\t\t14.0\nBuildVersion:\t\t23A344\n",
        (
            "sysctl",
            "-n",
            "hw.model",
            "hw.ncpu",
            "machdep.cpu.brand_string",
        ): "MacTest1,1\n8\nTest CPU\n",
    }
    key = tuple(command)
    if key not in outputs:
        return subprocess.CompletedProcess(command, 1, "", "unexpected command")
    return subprocess.CompletedProcess(command, 0, outputs[key], "")


# ---------------------------------------------------------------------------
# Stub adapters / registries


class _StubTelemetry:
    """Telemetry whose idle readings the test pins, with optional powermetrics
    backend so the cooldown gate (skipped for mock) actually runs.

    ``measure_idle`` sleeps on the clock (so a FakeClock advances exactly like a
    real bounded idle window) and returns a constant ``idle_mean``. The measured
    window is a flat trace so the run still reduces to a SUCCEEDED bundle.
    """

    name = "stub-telemetry"

    def __init__(
        self,
        clock: Clock,
        idle_mean: float = 5.0,
        cooldown_mean: float | None = None,
        cooldown_means: list[float] | None = None,
        thermal_pressure: str | None = "Nominal",
    ) -> None:
        self._clock = clock
        self._idle_mean = idle_mean
        # Reading returned for cooldown sub-windows (idle_seconds trimmed to
        # COOLDOWN_SUBWINDOW_S); defaults to the lifecycle idle mean (instant
        # recovery). Set higher to force a cap_hit.
        self._cooldown_mean = cooldown_mean if cooldown_mean is not None else idle_mean
        # Optional time-varying sequence of cooldown sub-window means, consumed
        # one per sub-window; once exhausted the last value repeats. Drives the
        # rolling-window high-to-low RECOVERY transition.
        self._cooldown_means = list(cooldown_means) if cooldown_means else None
        self._cooldown_index = 0
        self._thermal_pressure = thermal_pressure
        self._start: float | None = None

    def _next_cooldown_mean(self) -> float:
        if self._cooldown_means is None:
            return self._cooldown_mean
        index = min(self._cooldown_index, len(self._cooldown_means) - 1)
        self._cooldown_index += 1
        return self._cooldown_means[index]

    def device_metadata(self, config: BenchmarkConfig, context=None) -> dict:
        return {
            "device": config.hardware_target.id,
            "telemetry": self.name,
            "rail_manifest": ["stub"],
        }

    def measure_idle(self, config: BenchmarkConfig, context=None) -> IdleBaseline:
        duration_s = config.sampling.idle_seconds
        self._clock.sleep(duration_s)
        is_cooldown_subwindow = duration_s == COOLDOWN_SUBWINDOW_S
        mean = self._next_cooldown_mean() if is_cooldown_subwindow else self._idle_mean
        return IdleBaseline(
            power_w_mean=mean,
            power_w_stddev=0.0,
            duration_s=duration_s,
            sample_count=max(2, int(duration_s * config.sampling.power_hz)),
            telemetry_backend=TelemetryBackend.POWERMETRICS,
            idle_window_suspect=False,
        )

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        self._start = self._clock.now()
        return AdapterResult(ok=True)

    def stop_sampling(self, config: BenchmarkConfig, context=None) -> list[PowerSample]:
        start = self._start if self._start is not None else self._clock.now()
        end = self._clock.now()
        samples = [
            PowerSample(timestamp_s=start, power_w=7.5, source="stub", rail="stub"),
            PowerSample(timestamp_s=end, power_w=7.5, source="stub", rail="stub"),
        ]
        self._start = None
        return samples

    def thermal_state(self, config: BenchmarkConfig, context=None) -> ThermalState:
        return ThermalState(
            timestamp_s=self._clock.now(),
            temperature_c=42.0,
            thermal_pressure=self._thermal_pressure,
        )


class _StubRegistry:
    """Mock runtime + transport, but a caller-supplied telemetry factory.

    Lets the experiment tests run a real measured lifecycle while pinning the
    cooldown gate's idle readings (or injecting a runtime kill).
    """

    def __init__(
        self,
        telemetry_factory,
        *,
        kill_on_prepare_rep: int | None = None,
    ) -> None:
        self._telemetry_factory = telemetry_factory
        self._kill_on_prepare_rep = kill_on_prepare_rep

    def resolve_transport(self, config: BenchmarkConfig):
        return resolve_transport(config)

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        runtime, failure = resolve_runtime(config, clock)
        if self._kill_on_prepare_rep is not None and runtime is not None:
            runtime = _KillingRuntime(runtime, self._kill_on_prepare_rep)
        return runtime, failure

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return self._telemetry_factory(clock), None


class _KillingRuntime:
    """Wraps a runtime to raise KeyboardInterrupt during a target rep's prepare.

    The target rep is identified by the ``__rN`` suffix on the run_id, so the
    kill lands deterministically on rep N's prepare stage (before any bundle for
    rep N is finalized).
    """

    def __init__(self, inner, kill_rep: int) -> None:
        self._inner = inner
        self._kill_rep = kill_rep

    @property
    def name(self) -> str:
        return self._inner.name

    def prepare(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        if config.run_id is not None and config.run_id.endswith(f"__r{self._kill_rep}"):
            raise KeyboardInterrupt("simulated kill during rep prepare")
        return self._inner.prepare(config)

    def warmup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.warmup(config)

    def run_workload(self, config: BenchmarkConfig, context=None):
        return self._inner.run_workload(config)

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.cleanup(config)


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------------------
# Test 1: 3-rep mock experiment


class ThreeRepMockExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"

    def test_three_complete_bundles_and_manifest(self) -> None:
        config = make_config("exp-test", repetitions=3)
        clock = FakeClock()
        manifest_path, members = run_experiment(config, self.runs_root, clock)

        self.assertEqual(len(members), 3)
        member_dirs = [bundle.name for bundle, _ in members]
        self.assertEqual(member_dirs, ["exp-test__r1", "exp-test__r2", "exp-test__r3"])

        for bundle, summary in members:
            self.assertTrue(bundle.is_dir())
            self.assertEqual(bundle.parent, self.runs_root)
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            self.assertEqual(validate_bundle(bundle), [])

        self.assertEqual(manifest_path, self.runs_root / "experiments" / "exp-test.json")
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["experiment_id"], "exp-test")
        self.assertEqual(
            manifest["members"], ["exp-test__r1", "exp-test__r2", "exp-test__r3"]
        )
        self.assertEqual(manifest["condition_order"], ["mock_smoke"] * 3)
        self.assertEqual(
            manifest["member_gaps"],
            [
                {"member": "exp-test__r1", "preceding_gap_s": None},
                {"member": "exp-test__r2", "preceding_gap_s": 2.0},
                {"member": "exp-test__r3", "preceding_gap_s": 2.0},
            ],
        )
        self.assertIn("created_at_s", manifest)
        self.assertIsInstance(manifest["created_at_s"], (int, float))
        self.assertRegex(manifest["config_sha256"], _HEX64)
        self.assertIn("aggregate", manifest)
        aggregate = manifest["aggregate"]
        self.assertEqual(aggregate["members_total"], 3)
        self.assertEqual(aggregate["members_succeeded"], 3)
        energy_request = aggregate["metrics"]["energy_request_j"]
        self.assertEqual(energy_request["repetitions"], 3)
        self.assertTrue(energy_request["interval_available"])
        self.assertTrue(energy_request["below_headline_protocol"])
        self.assertFalse(energy_request["below_minimum_protocol"])
        poisoned_manifest = dict(manifest)
        poisoned_manifest["aggregate"] = {"poison": "must be ignored"}
        self.assertEqual(
            aggregate_experiment(self.runs_root, poisoned_manifest),
            aggregate,
        )

        # Two cooldown gates (between r1/r2 and r2/r3), both skipped for mock.
        cooldown = manifest["cooldown"]
        self.assertEqual(len(cooldown), 2)
        for index, note in enumerate(cooldown, start=1):
            self.assertEqual(note["result"], "skipped")
            self.assertEqual(note["reason"], "mock telemetry")
            self.assertEqual(note["after_member"], f"exp-test__r{index}")

        first_metadata = json.loads((self.runs_root / "exp-test__r1" / "metadata.json").read_text())
        second_metadata = json.loads((self.runs_root / "exp-test__r2" / "metadata.json").read_text())
        self.assertIsNone(first_metadata["extra"]["preceding_gap_s"])
        self.assertEqual(second_metadata["extra"]["preceding_gap_s"], 2.0)

    def test_experiment_members_capture_per_run_environment_snapshots(self) -> None:
        config = make_config("exp-env", repetitions=3)
        clock = DeterministicClock()
        with patch(
            "joulewise.environment.subprocess.run",
            side_effect=fake_environment_run,
        ) as run:
            _manifest_path, members = run_experiment(config, self.runs_root, clock)

        environment_calls = [
            call for call in run.call_args_list if call.args[0][0] != "git"
        ]
        # Four full snapshots (experiment fallback + three prepare-end) plus
        # one three-command post-run guard observation per member.
        self.assertEqual(len(environment_calls), 18 * 4 + 3 * 3)
        environments = [
            json.loads((bundle / "metadata.json").read_text())["environment"]
            for bundle, _summary in members
        ]
        captured_at = [environment["captured_at_s"] for environment in environments]
        self.assertEqual(captured_at, sorted(captured_at))
        for environment in environments:
            self.assertFalse(environment["capture_skipped"])
            self.assertEqual(environment["capture_scope"], "run")
            self.assertIsNone(environment["captured_for_rep"])
            self.assertIsInstance(environment["captured_at_s"], (int, float))
            self.assertIsInstance(environment["env_capture_duration_s"], (int, float))
            self.assertEqual(environment["settle_s"], 2.0)
            self.assertEqual(environment["power_source"], "AC Power")
            self.assertEqual(environment["display"]["probe"], "system_profiler_spdisplays")
            self.assertEqual(environment["display"]["active_displays"], 1)
            self.assertEqual(environment["power"]["adapter_watts"], 96)
            self.assertEqual(environment["clock_sync"]["status"], "limited_without_admin")
            self.assertIs(environment["clock_sync"]["timed_running"], True)

    def test_config_hash_is_over_as_given_shared_config(self) -> None:
        # The manifest hash is the bundle writer's D-001 hash of the SHARED
        # config (with its original run_id), not any per-member config.
        config = make_config("exp-hash", repetitions=2)
        clock = FakeClock()
        from joulewise.controller import _config_sha256

        manifest_path, _ = run_experiment(config, self.runs_root, clock)
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["config_sha256"], _config_sha256(config))

    def test_aggregate_reruns_from_minimal_manifest(self) -> None:
        """D-002: the aggregate is reconstructable from member bundles alone."""
        config = make_config("exp-minimal-aggregate", repetitions=3)
        manifest_path, _ = run_experiment(config, self.runs_root, FakeClock())
        manifest = json.loads(manifest_path.read_text())
        minimal_manifest = {
            "experiment_id": manifest["experiment_id"],
            "members": manifest["members"],
            "aggregate": {"poison": "must be ignored"},
        }

        self.assertEqual(
            aggregate_experiment(self.runs_root, minimal_manifest),
            manifest["aggregate"],
        )

    def test_partial_manifest_aggregates_only_listed_members(self) -> None:
        """D-005: a partial experiment manifest is a valid aggregate input."""
        config = make_config("exp-partial-aggregate", repetitions=3)
        manifest_path, _ = run_experiment(config, self.runs_root, FakeClock())
        manifest = json.loads(manifest_path.read_text())
        partial_manifest = {
            "experiment_id": manifest["experiment_id"],
            "members": manifest["members"][:2],
        }

        aggregate = aggregate_experiment(self.runs_root, partial_manifest)

        self.assertEqual(aggregate["members_total"], 2)
        self.assertEqual(aggregate["members_read"], 2)
        self.assertEqual(aggregate["members_succeeded"], 2)
        self.assertEqual(
            aggregate["metrics"]["energy_request_j"]["repetitions"],
            2,
        )


# ---------------------------------------------------------------------------
# Test 2: kill after rep 2 leaves a valid 2-member manifest


class KillAfterRepTwoTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"

    def test_kill_during_rep3_leaves_two_member_manifest(self) -> None:
        config = make_config("exp-kill", repetitions=3)
        clock = FakeClock()
        registry = _StubRegistry(
            lambda clk: _StubTelemetry(clk), kill_on_prepare_rep=3
        )
        with self.assertRaises(KeyboardInterrupt):
            run_experiment(config, self.runs_root, clock, registry=registry)

        manifest_path = self.runs_root / "experiments" / "exp-kill.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text())  # valid JSON
        self.assertEqual(manifest["members"], ["exp-kill__r1", "exp-kill__r2"])
        self.assertEqual(manifest["condition_order"], ["mock_smoke", "mock_smoke"])
        # Both completed members are valid bundles.
        for member in manifest["members"]:
            self.assertEqual(validate_bundle(self.runs_root / member), [])
        # The interrupted member is finalized for evidence custody but is not
        # registered as a completed experiment member; the original interrupt
        # still propagates to the caller.
        r3 = self.runs_root / "exp-kill__r3"
        self.assertTrue((r3 / "summary_metrics.json").is_file())
        interrupted = json.loads((r3 / "summary_metrics.json").read_text())
        self.assertEqual(interrupted["status"], "failed")
        self.assertIn("KeyboardInterrupt", interrupted["failure_message"])

    def test_interrupt_before_aggregation_leaves_completed_member_registered(self) -> None:
        config = make_config("exp-aggregate-interrupt", repetitions=1)

        with patch(
            "joulewise.controller.aggregate_experiment",
            side_effect=KeyboardInterrupt("simulated aggregate interrupt"),
        ), self.assertRaises(KeyboardInterrupt):
            run_experiment(config, self.runs_root, FakeClock())

        manifest_path = self.runs_root / "experiments" / "exp-aggregate-interrupt.json"
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["members"], ["exp-aggregate-interrupt__r1"])
        self.assertNotIn("aggregate", manifest)
        self.assertEqual(
            aggregate_experiment(self.runs_root, manifest)["members_read"],
            1,
        )

    def test_aggregate_exception_is_recorded_for_retry(self) -> None:
        config = make_config("exp-aggregate-error", repetitions=1)

        with patch(
            "joulewise.controller.aggregate_experiment",
            side_effect=RuntimeError("simulated aggregate failure"),
        ), self.assertRaisesRegex(RuntimeError, "simulated aggregate failure"):
            run_experiment(config, self.runs_root, FakeClock())

        manifest_path = self.runs_root / "experiments" / "exp-aggregate-error.json"
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["members"], ["exp-aggregate-error__r1"])
        self.assertNotIn("aggregate", manifest)
        self.assertEqual(
            manifest["aggregate_error"],
            {
                "error_type": "RuntimeError",
                "message": "simulated aggregate failure",
                "retryable": True,
            },
        )
        self.assertEqual(
            aggregate_experiment(self.runs_root, manifest)["members_read"],
            1,
        )


# ---------------------------------------------------------------------------
# Test 3: cooldown gate (stub telemetry + FakeClock)


class CooldownGateUnitTests(unittest.TestCase):
    def _config(self) -> BenchmarkConfig:
        # A non-mock telemetry backend so the gate is in play; the stub registry
        # supplies the actual readings.
        data = _example_config_data()
        data["run_id"] = "exp-cool"
        data["hardware_target"]["telemetry_backend"] = "powermetrics"
        data["workload_profile"]["repetitions"] = 2
        return BenchmarkConfig.from_mapping(data)

    def _reference(self, mean: float) -> IdleBaseline:
        return IdleBaseline(
            power_w_mean=mean,
            power_w_stddev=0.0,
            duration_s=30.0,
            sample_count=30,
            telemetry_backend=TelemetryBackend.POWERMETRICS,
        )

    def test_recovered_when_within_tolerance(self) -> None:
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(clock, idle_mean=5.2)  # ~4% above 5.0
        note = cooldown_gate(telemetry, self._reference(5.0), config, clock)
        self.assertEqual(note["result"], "recovered")
        # Cooldown v2 refuses the old single-5 s-subwindow release defect.
        self.assertGreaterEqual(note["waited_s"], 30.0)
        self.assertGreaterEqual(note["window_coverage_s"], 30.0)
        self.assertTrue(note["window_complete"])
        self.assertEqual(note["thresholds"]["sustained_window_s"], 30.0)
        self.assertEqual(note["thresholds"]["subwindow_s"], 5.0)

    def test_real_clock_shaped_probe_gaps_release_at_coverage_threshold(self) -> None:
        class GappedTelemetry(_StubTelemetry):
            def measure_idle(self, config, context=None):
                self._clock.sleep(config.sampling.idle_seconds)
                return IdleBaseline(
                    power_w_mean=5.0,
                    power_w_stddev=0.0,
                    duration_s=config.sampling.idle_seconds - (0.005 / 6.0),
                    sample_count=5,
                    telemetry_backend=TelemetryBackend.POWERMETRICS,
                    idle_window_suspect=False,
                )

        clock = FakeClock()
        note = cooldown_gate(
            GappedTelemetry(clock),
            self._reference(5.0),
            self._config(),
            clock,
        )
        self.assertEqual(note["result"], "recovered")
        self.assertAlmostEqual(note["window_coverage_s"], 29.995, places=6)
        self.assertGreaterEqual(note["window_span_s"], 30.0)
        self.assertEqual(note["thresholds"]["coverage_fraction"], 0.8)
        self.assertTrue(note["coverage_complete"])

    def test_genuine_evidence_hole_below_coverage_fraction_does_not_release(self) -> None:
        class SparseTelemetry(_StubTelemetry):
            def measure_idle(self, config, context=None):
                self._clock.sleep(config.sampling.idle_seconds)
                return IdleBaseline(
                    power_w_mean=5.0,
                    power_w_stddev=0.0,
                    duration_s=3.0,
                    sample_count=3,
                    telemetry_backend=TelemetryBackend.POWERMETRICS,
                    idle_window_suspect=False,
                )

        clock = FakeClock()
        policy = CooldownPolicy(cap_s=30.0)
        note = cooldown_gate(
            SparseTelemetry(clock),
            self._reference(5.0),
            self._config(),
            clock,
            policy=policy,
        )
        self.assertEqual(note["result"], "cap_hit")
        self.assertGreaterEqual(note["window_span_s"], 30.0)
        self.assertLess(note["window_coverage_s"], note["required_coverage_s"])
        self.assertFalse(note["coverage_complete"])

    def test_cap_precedes_recovery_when_final_capture_finishes_late(self) -> None:
        class SlowCaptureTelemetry(_StubTelemetry):
            def measure_idle(self, config, context=None):
                self._clock.sleep(2.1)
                return IdleBaseline(
                    power_w_mean=5.0,
                    power_w_stddev=0.0,
                    duration_s=2.0,
                    sample_count=2,
                    telemetry_backend=TelemetryBackend.POWERMETRICS,
                    idle_window_suspect=False,
                )

        clock = FakeClock()
        note = cooldown_gate(
            SlowCaptureTelemetry(clock),
            self._reference(5.0),
            self._config(),
            clock,
            policy=CooldownPolicy(
                subwindow_s=2.0,
                sustained_window_s=10.0,
                cap_s=10.0,
            ),
        )

        self.assertEqual(note["result"], "cap_hit")
        self.assertAlmostEqual(note["waited_s"], 10.5)
        self.assertTrue(note["window_complete"])
        trace = note["_trace"]
        self.assertTrue(trace[-1]["release_criteria_met_late"])
        self.assertFalse(trace[-1]["release"])

    def test_recovers_after_rolling_window_crosses_into_tolerance(self) -> None:
        # Drive the rolling-30 s-mean high-to-low RECOVERY transition: the first
        # two sub-windows read 7.5 W (50% above the 5.0 W reference, outside the
        # 10% band), then every later sub-window reads 5.1 W (inside the band).
        # The rolling mean stays outside while the two high readings sit inside
        # the 30 s window and only crosses into tolerance once they age out, so
        # recovery takes several sub-windows (waited_s well over one sub-window,
        # well under the 300 s cap).
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(
            clock, idle_mean=5.0, cooldown_means=[7.5, 7.5, 5.1]
        )
        note = cooldown_gate(telemetry, self._reference(5.0), config, clock)
        self.assertEqual(note["result"], "recovered")
        # More than one sub-window was consumed before recovery.
        self.assertGreater(note["waited_s"], COOLDOWN_SUBWINDOW_S)
        self.assertLess(note["waited_s"], COOLDOWN_CAP_S)

    def test_below_reference_counts_as_recovered_after_complete_window(self) -> None:
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(clock, idle_mean=3.0)
        note = cooldown_gate(telemetry, self._reference(5.0), config, clock)
        self.assertEqual(note["result"], "recovered")
        self.assertLess(note["decision_rolling_mean_power_w"], 5.0)
        self.assertEqual(note["policy_version"], "cooldown-v2")
        self.assertTrue(note["thermal_nominal"])

    def test_cap_hit_when_readings_pinned_high(self) -> None:
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(clock, idle_mean=7.5)  # 50% above 5.0
        note = cooldown_gate(telemetry, self._reference(5.0), config, clock)
        self.assertEqual(note["result"], "cap_hit")
        # The cap is honored: we wait at least the cap, and not unboundedly.
        self.assertGreaterEqual(note["waited_s"], COOLDOWN_CAP_S)
        self.assertLessEqual(note["waited_s"], COOLDOWN_CAP_S + 10.0)

    def test_absolute_ceiling_is_an_upper_cap_not_an_or_escape(self) -> None:
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(clock, idle_mean=5.0)
        policy = CooldownPolicy(cap_s=30.0, absolute_ceiling_w=4.5)
        note = cooldown_gate(
            telemetry, self._reference(5.0), config, clock, policy=policy
        )
        self.assertEqual(note["result"], "cap_hit")
        self.assertEqual(note["reference_upper_w"], 5.5)
        self.assertEqual(note["effective_upper_w"], 4.5)
        self.assertEqual(
            note["release_criterion"]["absolute_ceiling_role"],
            "additional_upper_cap",
        )

    def test_non_nominal_thermal_state_prevents_release(self) -> None:
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(
            clock, idle_mean=3.0, thermal_pressure="Elevated"
        )
        policy = CooldownPolicy(cap_s=30.0)
        note = cooldown_gate(
            telemetry, self._reference(5.0), config, clock, policy=policy
        )
        self.assertEqual(note["result"], "cap_hit")
        self.assertTrue(note["window_complete"])
        self.assertFalse(note["thermal_nominal"])


class CooldownThroughExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"

    def test_cap_hit_lands_in_next_rep_quality_and_metadata(self) -> None:
        data = _example_config_data()
        data["run_id"] = "exp-caphit"
        data["hardware_target"]["telemetry_backend"] = "powermetrics"
        data["workload_profile"]["repetitions"] = 2
        config = BenchmarkConfig.from_mapping(data)

        clock = FakeClock()
        # The lifecycle idle baseline reads 5.0 (the cooldown reference); the
        # cooldown sub-windows read 7.5 (50% high) so the gate between r1 and r2
        # never recovers and caps.
        registry = _StubRegistry(
            lambda clk: _StubTelemetry(clk, idle_mean=5.0, cooldown_mean=7.5)
        )
        manifest_path, members = run_experiment(
            config, self.runs_root, clock, registry=registry
        )

        self.assertEqual(len(members), 2)
        (r1_bundle, r1_summary), (r2_bundle, r2_summary) = members

        # r1 had no preceding cooldown gate, so its flag is None.
        self.assertIsNone(r1_summary.measurement_quality.cooldown_cap_hit)
        # r2 follows a cap_hit gate.
        self.assertIs(r2_summary.measurement_quality.cooldown_cap_hit, True)

        # The flag is in r2's summary on disk and in its metadata.json extra.
        r2_summary_disk = json.loads((r2_bundle / "summary_metrics.json").read_text())
        self.assertIs(
            r2_summary_disk["measurement_quality"]["cooldown_cap_hit"], True
        )
        r2_metadata = json.loads((r2_bundle / "metadata.json").read_text())
        self.assertIs(r2_metadata["extra"]["cooldown_cap_hit"], True)
        self.assertAlmostEqual(r2_metadata["extra"]["preceding_gap_s"], 302.0)

        # r1's metadata carries gap provenance but no cooldown cap-hit flag.
        r1_metadata = json.loads((r1_bundle / "metadata.json").read_text())
        self.assertIsNone(r1_metadata["extra"]["preceding_gap_s"])
        self.assertNotIn("cooldown_cap_hit", r1_metadata["extra"])

        # The manifest records the single cap_hit gate.
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(len(manifest["cooldown"]), 1)
        note = manifest["cooldown"][0]
        self.assertEqual(note["result"], "cap_hit")
        self.assertEqual(note["after_member"], "exp-caphit__r1")
        self.assertEqual(note["reference_power_w"], 5.0)
        self.assertEqual(note["tolerance_fraction"], 0.1)
        self.assertEqual(note["decision_rolling_mean_power_w"], 7.5)
        self.assertAlmostEqual(note["waited_s"], 300.0)
        self.assertIn("raw_artifact", note)
        trace_path = manifest_path.parent / note["raw_artifact"]
        self.assertTrue(trace_path.is_file())
        trace_records = [
            json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()
        ]
        self.assertEqual(len(trace_records), 60)
        self.assertEqual(
            [round(record["waited_s"], 9) for record in trace_records],
            [float(value) for value in range(5, 301, 5)],
        )
        self.assertEqual(trace_records[-1]["rolling_mean_power_w"], 7.5)

    def test_flagged_contaminated_previous_rep_uses_frozen_clean_anchor(self) -> None:
        data = _example_config_data()
        data["run_id"] = "exp-flagged-reference"
        data["hardware_target"]["telemetry_backend"] = "powermetrics"
        config = BenchmarkConfig.from_mapping(data)
        policy_path = REPO_ROOT / "configs" / "campaign_policies" / "quiet_mac_exploratory.json"
        from joulewise.schemas import CampaignPolicy

        policy = CampaignPolicy.from_mapping(json.loads(policy_path.read_text()))
        summary = SummaryMetrics(
            status=RunStatus.SUCCEEDED,
            idle_baseline=IdleBaseline(
                power_w_mean=9.0,
                power_w_stddev=0.0,
                duration_s=30.0,
                sample_count=30,
                telemetry_backend=TelemetryBackend.POWERMETRICS,
                idle_window_suspect=True,
            ),
        )
        bundle = self.runs_root / "exp-flagged-reference__r1"
        bundle.mkdir(parents=True)
        (bundle / "metadata.json").write_text(
            json.dumps(
                {
                    "campaign_policy": {"sha256": "a" * 64},
                    "environment_admission": {
                        "critical_environment_passed": True,
                        "decision": "flagged",
                        "reference_provenance_present": True,
                    },
                }
            )
        )
        anchor_baseline = {
            "power_w_mean": 5.0,
            "power_w_stddev": 0.0,
            "duration_s": 30.0,
            "sample_count": 30,
            "telemetry_backend": "powermetrics",
            "idle_window_suspect": False,
        }
        registry = _StubRegistry(lambda clk: _StubTelemetry(clk, idle_mean=5.0))
        note, _cap_hit = _cooldown_between_reps(
            config,
            self.runs_root,
            "exp-flagged-reference",
            bundle.name,
            summary,
            registry,
            FakeClock(),
            campaign_policy=policy,
            frozen_anchor={
                "schema_version": "joulewise.cooldown_anchor.v1",
                "baseline": anchor_baseline,
                "immutable_after_freeze": True,
            },
        )
        self.assertEqual(note["reference_selection"], "frozen_clean_anchor")
        self.assertFalse(note["reference_eligibility"]["eligible"])
        self.assertEqual(note["reference_power_w"], 5.0)

    def test_campaign_policy_recaptures_each_rep_and_battery_flip_aborts_r2(self) -> None:
        from joulewise.schemas import CampaignPolicy

        policy_path = REPO_ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
        policy = CampaignPolicy.from_mapping(json.loads(policy_path.read_text()))
        clean = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "capture_scope": "run",
            "settle_s": 0.0,
        }
        battery = {**clean, "power_source": "Battery Power"}
        evaluation = evaluate_environment_policy(clean, policy.environment_guard)
        binding = {"sha256": "a" * 64}
        preflight = {
            "evaluation": evaluation,
            "override": None,
            "policy_sha256": "a" * 64,
        }
        config = make_config("exp-power-flip", repetitions=2)
        with (
            patch(
                "joulewise.controller._campaign_policy_from_environment",
                return_value=(policy, binding, preflight),
            ),
            patch(
                "joulewise.controller._capture_environment",
                side_effect=[clean, battery],
            ) as capture,
        ):
            _manifest, members = run_experiment(
                config,
                self.runs_root,
                FakeClock(),
                registry=_StubRegistry(lambda clk: _StubTelemetry(clk)),
            )
        self.assertEqual(capture.call_count, 2)
        self.assertEqual(members[0][1].status, RunStatus.SUCCEEDED)
        self.assertEqual(members[1][1].status, RunStatus.FAILED)
        r2_metadata = json.loads(
            (members[1][0] / "metadata.json").read_text()
        )
        self.assertEqual(r2_metadata["environment"]["power_source"], "Battery Power")
        self.assertEqual(
            r2_metadata["environment_admission"]["decision"], "abort"
        )

    def test_prepare_end_capture_rejects_power_flip_during_prepare(self) -> None:
        from joulewise.schemas import CampaignPolicy

        policy_path = REPO_ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
        policy = CampaignPolicy.from_mapping(json.loads(policy_path.read_text()))
        clean = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "capture_scope": "run",
            "settle_s": 0.0,
        }
        state = {"power_source": "AC Power"}

        class PowerFlippingRuntime:
            def __init__(self, inner):
                self._inner = inner
                self.name = inner.name

            def prepare(self, config, context=None):
                result = self._inner.prepare(config, context)
                state["power_source"] = "Battery Power"
                return result

            def warmup(self, config, context=None):
                return self._inner.warmup(config, context)

            def run_workload(self, config, context=None):
                return self._inner.run_workload(config, context)

            def cleanup(self, config, context=None):
                return self._inner.cleanup(config, context)

        class PowerFlippingRegistry(_StubRegistry):
            def resolve_runtime(self, config, clock):
                runtime, failure = super().resolve_runtime(config, clock)
                return PowerFlippingRuntime(runtime), failure

        evaluation = evaluate_environment_policy(clean, policy.environment_guard)
        binding = {"sha256": "a" * 64}
        preflight = {
            "evaluation": evaluation,
            "override": None,
            "policy_sha256": "a" * 64,
        }

        def capture_after_prepare(_clock, **_kwargs):
            return {**clean, "power_source": state["power_source"]}

        with (
            patch(
                "joulewise.controller._campaign_policy_from_environment",
                return_value=(policy, binding, preflight),
            ),
            patch(
                "joulewise.controller._capture_environment",
                side_effect=capture_after_prepare,
            ) as capture,
        ):
            _manifest, members = run_experiment(
                make_config("exp-prepare-power-flip", repetitions=1),
                self.runs_root,
                FakeClock(),
                registry=PowerFlippingRegistry(lambda clk: _StubTelemetry(clk)),
            )

        self.assertEqual(capture.call_count, 1)
        self.assertEqual(members[0][1].status, RunStatus.FAILED)
        metadata = json.loads((members[0][0] / "metadata.json").read_text())
        self.assertEqual(metadata["environment"]["power_source"], "Battery Power")
        self.assertEqual(metadata["environment_admission"]["decision"], "abort")

    def test_explicit_campaign_anchor_survives_ineligible_r1_and_gates_r2(self) -> None:
        from joulewise.schemas import CampaignPolicy

        policy_path = REPO_ROOT / "configs" / "campaign_policies" / "quiet_mac_exploratory.json"
        policy = CampaignPolicy.from_mapping(json.loads(policy_path.read_text()))
        clean = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "capture_scope": "run",
            "settle_s": 0.0,
        }
        evaluation = evaluate_environment_policy(clean, policy.environment_guard)
        binding = {"sha256": "a" * 64}
        preflight = {
            "evaluation": evaluation,
            "override": None,
            "policy_sha256": "a" * 64,
        }
        anchor = {
            "schema_version": "joulewise.cooldown_anchor.v1",
            "source_kind": "neg8_reference_start",
            "bundle_id": "neg8-anchor",
            "policy_sha256": "a" * 64,
            "environment_snapshot_sha256": "b" * 64,
            "immutable_after_freeze": True,
            "baseline": {
                "power_w_mean": 5.0,
                "power_w_stddev": 0.0,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": False,
            },
        }
        original_anchor = json.loads(json.dumps(anchor))

        class SuspectLifecycleTelemetry(_StubTelemetry):
            def measure_idle(self, config, context=None):
                baseline = super().measure_idle(config, context)
                if config.sampling.idle_seconds != policy.cooldown.subwindow_s:
                    return replace(baseline, idle_window_suspect=True)
                return baseline

        with (
            patch(
                "joulewise.controller._campaign_policy_from_environment",
                return_value=(policy, binding, preflight),
            ),
            patch(
                "joulewise.controller._capture_environment",
                return_value=clean,
            ),
        ):
            config_data = _example_config_data()
            config_data["run_id"] = "exp-campaign-anchor"
            config_data["hardware_target"]["telemetry_backend"] = "powermetrics"
            config_data["workload_profile"]["repetitions"] = 2
            manifest_path, members = run_experiment(
                BenchmarkConfig.from_mapping(config_data),
                self.runs_root,
                FakeClock(),
                registry=_StubRegistry(lambda clk: SuspectLifecycleTelemetry(clk)),
                frozen_cooldown_anchor=anchor,
            )

        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(len(members), 2)
        self.assertEqual(manifest["cooldown_anchor"], original_anchor)
        self.assertEqual(manifest["cooldown"][0]["result"], "recovered")
        self.assertEqual(
            manifest["cooldown"][0]["reference_selection"],
            "frozen_clean_anchor",
        )
        self.assertFalse(manifest["cooldown"][0]["reference_eligibility"]["eligible"])
        self.assertEqual(manifest["cooldown"][0]["reference_power_w"], 5.0)
        self.assertEqual(anchor, original_anchor)

    def test_cooldown_trace_write_error_is_manifest_metadata_not_campaign_failure(self) -> None:
        data = _example_config_data()
        data["run_id"] = "exp-cooldown-ioerr"
        data["hardware_target"]["telemetry_backend"] = "powermetrics"
        data["workload_profile"]["repetitions"] = 2
        config = BenchmarkConfig.from_mapping(data)
        experiments_dir = self.runs_root / "experiments"
        experiments_dir.mkdir(parents=True)
        (experiments_dir / "raw").write_text("not a directory")

        registry = _StubRegistry(
            lambda clk: _StubTelemetry(clk, idle_mean=5.0, cooldown_mean=7.5)
        )
        manifest_path, members = run_experiment(
            config, self.runs_root, FakeClock(), registry=registry
        )

        self.assertEqual(len(members), 2)
        manifest = json.loads(manifest_path.read_text())
        note = manifest["cooldown"][0]
        self.assertEqual(note["result"], "cap_hit")
        self.assertNotIn("raw_artifact", note)
        self.assertIn("FileExistsError", note["raw_artifact_error"])

    def test_member_gap_note_is_fail_soft_when_metadata_missing(self) -> None:
        missing_metadata_bundle = self.runs_root / "missing-metadata"
        missing_metadata_bundle.mkdir(parents=True)

        self.assertEqual(
            _member_gap_note(missing_metadata_bundle),
            {
                "member": "missing-metadata",
                "preceding_gap_s": None,
                "error": "metadata_unavailable",
            },
        )


# ---------------------------------------------------------------------------
# Test 4: CLI dispatch for repetitions > 1


class CliExperimentDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.runs_dir = self.tmp / "runs"

    def _write_config(self, run_id: str, repetitions: int) -> Path:
        data = _example_config_data()
        data["run_id"] = run_id
        data["workload_profile"]["repetitions"] = repetitions
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data))
        return path

    def test_repetitions_three_mock_cli_dispatch(self) -> None:
        config_path = self._write_config("cli-exp", repetitions=3)
        code, stdout, stderr = _run_cli(
            ["run", str(config_path), "--runs-dir", str(self.runs_dir)]
        )
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")

        lines = [line for line in stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 4)  # 3 bundle lines + 1 experiment line

        bundle_lines = lines[:3]
        for line in bundle_lines:
            match = BUNDLE_LINE.match(line)
            self.assertIsNotNone(match, line)
            self.assertEqual(match.group(2), "succeeded")

        experiment_line = lines[3]
        match = EXPERIMENT_LINE.match(experiment_line)
        self.assertIsNotNone(match, experiment_line)
        manifest_path = Path(match.group(1))
        self.assertEqual(int(match.group(2)), 3)
        self.assertTrue(manifest_path.is_file())
        self.assertEqual(
            manifest_path, self.runs_dir / "experiments" / "cli-exp.json"
        )


if __name__ == "__main__":
    unittest.main()
