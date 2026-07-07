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
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from joulewise.aggregate import aggregate_experiment
from joulewise.adapters import resolve_runtime, resolve_transport
from joulewise.clock import Clock, FakeClock
from joulewise.cli import main, validate_bundle
from joulewise.controller import (
    COOLDOWN_CAP_S,
    COOLDOWN_SUBWINDOW_S,
    cooldown_gate,
    run_experiment,
)
from joulewise.interfaces import AdapterResult, PowerSample, ThermalState
from joulewise.schemas import (
    BenchmarkConfig,
    IdleBaseline,
    RunStatus,
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
        return ThermalState(timestamp_s=self._clock.now(), temperature_c=42.0)


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
        # Rep 3's bundle was created but never finalized (incomplete bundle).
        r3 = self.runs_root / "exp-kill__r3"
        if r3.exists():
            self.assertFalse((r3 / "summary_metrics.json").exists())


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
        # Recovers on the very first sub-window (~5 s), well under the cap.
        self.assertLessEqual(note["waited_s"], 10.0)
        self.assertGreater(note["waited_s"], 0.0)

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

    def test_cap_hit_when_readings_pinned_high(self) -> None:
        clock = FakeClock()
        config = self._config()
        telemetry = _StubTelemetry(clock, idle_mean=7.5)  # 50% above 5.0
        note = cooldown_gate(telemetry, self._reference(5.0), config, clock)
        self.assertEqual(note["result"], "cap_hit")
        # The cap is honored: we wait at least the cap, and not unboundedly.
        self.assertGreaterEqual(note["waited_s"], COOLDOWN_CAP_S)
        self.assertLessEqual(note["waited_s"], COOLDOWN_CAP_S + 10.0)


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

        # r1's metadata carries no cooldown extra.
        r1_metadata = json.loads((r1_bundle / "metadata.json").read_text())
        self.assertNotIn("extra", r1_metadata)

        # The manifest records the single cap_hit gate.
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(len(manifest["cooldown"]), 1)
        note = manifest["cooldown"][0]
        self.assertEqual(note["result"], "cap_hit")
        self.assertEqual(note["after_member"], "exp-caphit__r1")


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
