"""Production-shaped P2-038 assertion over the real evidence-writing path.

This CI test uses a mock runtime only to avoid an MLX dependency. Telemetry is
the real PowermetricsTelemetryAdapter, running a real child process and the
committed captured fixture plists through the production parser, controller,
reducer, and strict validator. It does not replace the required quiet-machine
lead shakedown against true /usr/bin/powermetrics and approved backup.
"""

from __future__ import annotations

import json
import hashlib
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import joulewise.adapters
from joulewise.adapters.powermetrics import (
    PowermetricsTelemetryAdapter,
    parse_powermetrics_records,
)
from joulewise.bundle_read import BundleReader
from joulewise.cli import validate_bundle
from joulewise.clock import SystemClock
from joulewise.controller import _load_instrument_calibration_attachment, run_benchmark
from joulewise.environment import evaluate_environment_policy
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig, CampaignPolicy


FIXTURE_PROCESS = Path(__file__).parent / "fixtures" / "fake_powermetrics_process.py"


def claim_admission_fixture():
    """Return a complete claim-bearing policy binding over fixture telemetry."""

    policy = CampaignPolicy.from_mapping(
        {
            "schema_version": "joulewise.campaign_policy.v1",
            "policy_id": "p2038-production-path-test",
            "policy_version": "p2038-production-path-test-v1",
            "profile": "production",
            "post_window_sampling_dwell_s": 1.0,
            "environment_guard": {
                "require_ac_power": True,
                "require_external_connected": True,
                "require_low_power_mode_off": True,
                "require_displays_asleep": True,
                "require_screensaver_disengaged": True,
                "require_thermal_nominal": True,
                "critical_unknown_fail_closed": True,
            },
            "idle_admission": {
                "enabled": True,
                "on_fail": "abort",
                "retry_attempts": 1,
            },
            "idle_admission_extension": {
                "schema_version": "joulewise.idle_admission_extension.v1",
                "policy_version": "idle-admission-core-v1",
                "claim_bearing": True,
                "cpu_criteria": {
                    "cpu_busy_ratio_p95_max": 1.0,
                    "processor_combined_power_w_p95_max": 100.0,
                    "min_samples": 5,
                    "on_missing_telemetry": "fail",
                },
                "adapter_wattage": {"require_known_wattage": True},
                "neg8_bracket": {
                    "require_bracket": True,
                    "max_abs_delta_j": 0.05,
                    "max_rel_delta": 0.25,
                },
            },
            "cooldown": {
                "policy_version": "cooldown-v2",
                "subwindow_s": 1.0,
                "sustained_window_s": 2.0,
                "coverage_fraction": 0.8,
                "tolerance_fraction": 0.1,
                "cap_s": 30.0,
                "absolute_ceiling_w": None,
                "require_thermal_nominal": False,
            },
        }
    )
    snapshot = {
        "power_source": "AC Power",
        "power": {"external_connected": True},
        "low_power_mode": False,
        "display_power_state": "all_asleep",
        "screensaver_engaged": False,
        "screensaver_module": "Ventura",
        "screensaver_delay_s": 1200,
        "hid_idle_s": 1200.0,
        "thermal_pressure": "nominal",
        "load_average_1m": 0.0,
        "capture_scope": "provided_test_fixture",
        "python_packages": {"mlx": {"version": "p2038-test-mlx"}},
    }
    evaluation = evaluate_environment_policy(snapshot, policy.environment_guard)
    policy_sha256 = "a" * 64
    binding = {
        "schema_version": policy.schema_version,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "profile": policy.profile.value,
        "sha256": policy_sha256,
        "source": "tests/test_p2038_production_path.py",
    }
    preflight = {
        "schema_version": "joulewise.campaign_environment_preflight.v1",
        "policy_sha256": policy_sha256,
        "snapshot": snapshot,
        "evaluation": evaluation,
        "override": None,
        "admitted": True,
    }
    return policy, binding, preflight, snapshot


def install_complete_calibration(directory: Path) -> None:
    """Build a hash-bound validation directory for the production attach path."""

    # Reuse the real synthetic 40-pulse plist/event calibration constructed by
    # the reducer regressions. The former fixture paired one unrelated plist
    # frame and a dummy event with forty invented zero-residual rows; F2 now
    # correctly rejects that non-physical combination.
    from tests.test_reduce import self_consistent_calibration
    from joulewise.powermetrics_fiducial import (
        MAX_AGE_S,
        PROTOCOL_ID,
        PROTOCOL_V2_SHA256,
        RESIDUAL_REGION_METHOD,
    )

    raw_dir = directory / "raw"
    raw_dir.mkdir(parents=True)
    evidence, raw_bytes, event_bytes = self_consistent_calibration()
    (raw_dir / "powermetrics.plist").write_bytes(raw_bytes)
    (directory / "events.jsonl").write_bytes(event_bytes)
    bindings = {
        "hardware_model": "Mac15,9",
        "os_build": "24G720",
        "powermetrics_sha256": hashlib.sha256(
            FIXTURE_PROCESS.read_bytes()
        ).hexdigest(),
        "sampling_interval_ms": 50.0,
        "anchor_method_version": (
            "powermetrics_native_second_censored_intersection_v1"
        ),
        "mlx_version": "p2038-test-mlx",
        "pulse_protocol_id": PROTOCOL_ID,
        "power_policy": "ac_high_power",
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "protocol_sha256": PROTOCOL_V2_SHA256,
    }
    evidence["protocol_id"] = PROTOCOL_ID
    evidence["capture_wall_time_s"] = time.time()
    evidence["max_age_s"] = MAX_AGE_S
    evidence["bindings"] = bindings
    canonical_bindings = json.dumps(
        bindings, sort_keys=True, separators=(",", ":")
    ).encode()
    evidence["binding_evidence"] = {
        "schema_version": "joulewise.instrument_binding_evidence.v1",
        "binding_vector_sha256": hashlib.sha256(canonical_bindings).hexdigest(),
        "powermetrics_binary": {
            "path": str(FIXTURE_PROCESS),
            "sha256": bindings["powermetrics_sha256"],
        },
        "power_policy": {"id": bindings["power_policy"]},
    }
    evidence_raw = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode()
    artifact_path = directory / "instrument_evidence.json"
    artifact_path.write_bytes(evidence_raw)
    power_trace_raw = (
        b"timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
    )
    (directory / "power_trace.csv").write_bytes(power_trace_raw)
    artifacts = {
        "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
        "raw/powermetrics.plist": hashlib.sha256(raw_bytes).hexdigest(),
        "events.jsonl": hashlib.sha256(event_bytes).hexdigest(),
        "power_trace.csv": hashlib.sha256(power_trace_raw).hexdigest(),
    }
    manifest = {
        "schema_version": "joulewise.instrument_validation_manifest.v1",
        "artifacts": artifacts,
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


class LogicalDrainTimer:
    """Count requested drain waits, not host scheduling delays."""

    def __init__(self) -> None:
        self.now_s = 0.0

    def monotonic(self) -> float:
        return self.now_s

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)
        self.now_s += seconds


class ProductionShapedRegistry:
    def resolve_runtime(self, config, clock):
        return joulewise.adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config, clock):
        drain_timer = LogicalDrainTimer()
        return (
            PowermetricsTelemetryAdapter(
                clock,
                executable=str(FIXTURE_PROCESS),
                privilege_prefix=(sys.executable,),
                drain_monotonic=drain_timer.monotonic,
                drain_sleep=drain_timer.sleep,
            ),
            None,
        )

    def resolve_transport(self, config):
        return joulewise.adapters.resolve_transport(config)


def production_config() -> BenchmarkConfig:
    return BenchmarkConfig.from_mapping(
        {
            "schema_version": "0.1",
            "run_id": "p2038-production-shaped",
            "model": {"name": "mock-model"},
            "quantization": {"name": "none"},
            "hardware_target": {
                "id": "macbook_m3_max",
                "transport": "local",
                "runtime_backend": "mock",
                "telemetry_backend": "powermetrics",
            },
            "workload_profile": {
                "name": "p2038_production_shaped",
                "prompt_tokens": 32,
                "output_tokens": 200,
            },
            "sampling": {"power_hz": 20.0, "idle_seconds": 0.25},
        }
    )


class P2038ProductionPathTests(unittest.TestCase):
    def test_calibration_attachment_refuses_runtime_executable_digest_mismatch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            calibration = Path(tmp) / "calibration"
            install_complete_calibration(calibration)
            runtime_digest = hashlib.sha256(FIXTURE_PROCESS.read_bytes()).hexdigest()
            matched = _load_instrument_calibration_attachment(
                calibration,
                power_policy="ac_high_power",
                runtime_powermetrics_sha256=runtime_digest,
                runtime_power_policy="ac_high_power",
            )
            self.assertIsNotNone(matched)
            self.assertEqual(
                matched.metadata["binding_observations"]["powermetrics_sha256"],
                runtime_digest,
            )
            with self.assertRaisesRegex(
                ValueError, "runtime-observed executable digest"
            ):
                _load_instrument_calibration_attachment(
                    calibration,
                    power_policy="ac_high_power",
                    runtime_powermetrics_sha256="0" * 64,
                    runtime_power_policy="ac_high_power",
                )

    def test_calibration_attachment_refuses_config_only_power_policy(self) -> None:
        # R6 defect shape: the CLI label and artifact used to be copied into
        # binding_observations and accepted without a live observation.
        with tempfile.TemporaryDirectory() as tmp:
            calibration = Path(tmp) / "calibration"
            install_complete_calibration(calibration)
            runtime_digest = hashlib.sha256(FIXTURE_PROCESS.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "runtime-observed power policy"):
                _load_instrument_calibration_attachment(
                    calibration,
                    power_policy="ac_high_power",
                    runtime_powermetrics_sha256=runtime_digest,
                    runtime_power_policy=None,
                )

    def run_mode(self, root: Path, mode: str):
        state_path = root / f"{mode}.state"
        policy, binding, preflight, snapshot = claim_admission_fixture()
        guard_observation = {
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "screensaver_module": "Ventura",
            "screensaver_delay_s": 1200,
            "hid_idle_s": 1200.0,
            "power_source": "AC Power",
            "adapter_wattage_w": 140.0,
            "adapter_description": "fixture adapter",
            "errors": {},
        }
        calibration_dir = root / "calibration"
        install_complete_calibration(calibration_dir)
        with (
            patch.dict(
                os.environ,
                {
                    "P2038_FAKE_POWERMETRICS_MODE": mode,
                    "P2038_FAKE_POWERMETRICS_STATE": str(state_path),
                },
            ),
            patch(
                "joulewise.controller.collect_environment_guard_observation",
                side_effect=lambda **_kwargs: dict(guard_observation),
            ),
        ):
            return run_benchmark(
                production_config(),
                root,
                SystemClock(),
                registry=ProductionShapedRegistry(),
                reducer=reduce_bundle,
                environment_snapshot=snapshot,
                campaign_policy=policy,
                campaign_policy_binding=binding,
                campaign_environment_preflight=preflight,
                instrument_calibration_dir=calibration_dir,
                instrument_power_policy="ac_high_power",
            )

    def test_real_powermetrics_evidence_path_passes_p2029_p2040_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle, summary = self.run_mode(root, "normal")
            self.assertGreaterEqual(int((root / "normal.state").read_text()), 1)
            self.assertEqual(summary.status.value, "succeeded")
            self.assertEqual(validate_bundle(bundle, strict=True), [])
            metadata = json.loads((bundle / "metadata.json").read_text())
            calibration = metadata["instrument_calibration"]
            self.assertEqual(
                calibration["artifact_path"],
                "instrument_calibration/instrument_evidence.json",
            )
            self.assertEqual(
                calibration["bindings"]["power_policy"], "ac_high_power"
            )
            self.assertEqual(
                calibration["binding_observations"]["powermetrics_sha256"],
                hashlib.sha256(FIXTURE_PROCESS.read_bytes()).hexdigest(),
            )
            self.assertTrue(
                (bundle / "instrument_calibration" / "manifest.json").is_file()
            )
            stored = json.loads((bundle / "summary_metrics.json").read_text())
            events = [
                json.loads(line)
                for line in (bundle / "events.jsonl").read_text().splitlines()
            ]
            lifecycle = [(event["event_type"], event["phase"]) for event in events]
            self.assertLess(
                lifecycle.index(("sampling_stopped", "measured_run")),
                lifecycle.index(("stage_started", "idle_drift_sentinel")),
            )
            self.assertLess(
                lifecycle.index(("stage_completed", "idle_drift_sentinel")),
                lifecycle.index(("stage_started", "cleanup")),
            )
            self.assertTrue((bundle / "raw" / "powermetrics_idle.plist").is_file())
            self.assertTrue((bundle / "raw" / "powermetrics.plist").is_file())
            self.assertTrue((bundle / "raw" / "powermetrics_idle_post.plist").is_file())
            self.assertNotIn("clock_anchor_bound_s", metadata.get("extra", {}))
            self.assertNotIn("idle_drift_bound_w", metadata.get("extra", {}))
            self.assertEqual(metadata["uncertainty_evidence"]["schema_version"], "p2-038.2")
            clock_anchor = metadata["uncertainty_evidence"]["clock_anchor"]
            self.assertEqual(clock_anchor["status"], "bounded")
            self.assertEqual(
                clock_anchor["method"],
                "powermetrics_native_second_censored_intersection_v1",
            )
            self.assertGreaterEqual(clock_anchor["native_rollover_count"], 1)
            self.assertIn("energy_anchor_shift_envelopes", stored)
            self.assertIn(
                "/gross_energy_j", stored["energy_anchor_shift_envelopes"]
            )
            self.assertIsNotNone(
                stored["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"]
            )
            request_gate = stored["window_evidence_precheck"]["gross_request"]
            self.assertGreaterEqual(
                request_gate["clock_anchor_bound_s"],
                calibration["verified_effective_b_fiducial_s"],
            )
            self.assertGreaterEqual(
                metadata["trace_window_margins"]["achieved_post_window_margin_s"],
                request_gate["clock_anchor_bound_s"],
            )
            self.assertIsNotNone(
                request_gate["observed_bracketing_max_sample_gap_s"]
            )
            self.assertIsNotNone(request_gate["cadence_ratio"])
            self.assertGreaterEqual(request_gate["cadence_ratio"], 4.0)
            self.assertEqual(request_gate["reasons"], [])
            reader = BundleReader(bundle)
            measured_window = reader.measured_window()
            self.assertIsNotNone(measured_window)
            support_end_s = reader.summed_curve()[-1].support_end_s
            self.assertIsNotNone(support_end_s)
            self.assertGreaterEqual(support_end_s, measured_window.end_s)
            # scripts/run_campaign.assert_production_uncertainty still pins
            # p2-038.1 (outside this stream's write scope); replicate its
            # bundle-level guarantees against the p2-038.2 evidence here.
            for key in (
                "clock_anchor_bound_s",
                "marker_to_first_sample_phase_bound_s",
                "marker_to_last_sample_phase_bound_s",
                "idle_drift_bound_w",
            ):
                self.assertIsInstance(metadata.get(key), float)
                self.assertGreaterEqual(metadata[key], 0.0)
            self.assertEqual(
                metadata["uncertainty_evidence"]["sample_phase"]["status"],
                "bounded",
            )
            self.assertEqual(
                metadata["uncertainty_evidence"]["idle_drift"]["status"],
                "bounded",
            )
            self.assertIs(
                stored["window_evidence_precheck"]["gross_request"]["eligible"],
                True,
            )

    def test_rail_only_sentinels_withhold_drift_but_leave_gross_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle, summary = self.run_mode(Path(tmp), "rail_only")
            self.assertEqual(summary.status.value, "succeeded")
            self.assertEqual(validate_bundle(bundle, strict=True), [])
            metadata = json.loads((bundle / "metadata.json").read_text())
            self.assertNotIn("idle_drift_bound_w", metadata)
            self.assertEqual(
                metadata["uncertainty_evidence"]["idle_drift"],
                {"status": "unknown", "reason": "contamination_evidence_unknown"},
            )
            gates = json.loads((bundle / "summary_metrics.json").read_text())[
                "window_evidence_precheck"
            ]
            # Rail-only post-idle evidence withholds only the idle-subtracted
            # drift term. Host scheduling may independently trip cadence or
            # envelope-ratio gates, so assert the causal separation rather
            # than laundering those unrelated fail-closed reasons into a pass.
            self.assertNotIn(
                "drift_term_unknown", gates["gross_request"]["reasons"]
            )
            self.assertNotIn(
                "clock_anchor_unresolved", gates["gross_request"]["reasons"]
            )
            self.assertNotIn(
                "instrument_calibration_invalid",
                gates["gross_request"]["reasons"],
            )
            # If the gate is not eligible, the ONLY acceptable refusals are
            # the host-timing-sensitive gates; anything else is a defect this
            # test must catch, not launder.
            if gates["gross_request"]["eligible"] is not True:
                self.assertLessEqual(
                    set(gates["gross_request"]["reasons"]),
                    {
                        "cadence_ratio_below_threshold",
                        "clock_bound_exceeds_quarter_window",
                        "anchor_energy_envelope_exceeds_quarter_metric",
                        "post_window_trace_tail_shorter_than_anchor_bound",
                    },
                )
            self.assertIs(gates["idle_subtracted_request"]["eligible"], False)
            self.assertIn(
                "drift_term_unknown",
                gates["idle_subtracted_request"]["reasons"],
            )

    def test_extreme_post_idle_sentinel_cannot_leak_into_measured_trace_or_energy(self) -> None:
        class SnapshotAdapter(PowermetricsTelemetryAdapter):
            trace_before_sentinel: bytes | None = None

            def measure_post_run_idle(self, config, baseline, context):
                assert context is not None
                type(self).trace_before_sentinel = (
                    context.bundle_path / "power_trace.csv"
                ).read_bytes()
                return super().measure_post_run_idle(config, baseline, context)

        class SnapshotRegistry(ProductionShapedRegistry):
            def resolve_telemetry(self, config, clock):
                return (
                    SnapshotAdapter(
                        clock,
                        executable=str(FIXTURE_PROCESS),
                        privilege_prefix=(sys.executable,),
                    ),
                    None,
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "extreme.state"
            with patch.dict(
                os.environ,
                {
                    "P2038_FAKE_POWERMETRICS_MODE": "extreme_post",
                    "P2038_FAKE_POWERMETRICS_STATE": str(state_path),
                },
            ):
                bundle, summary = run_benchmark(
                    production_config(),
                    root,
                    SystemClock(),
                    registry=SnapshotRegistry(),
                    environment_snapshot=None,
                )
            self.assertEqual(summary.status.value, "succeeded")
            post_records = parse_powermetrics_records(
                (bundle / "raw" / "powermetrics_idle_post.plist").read_bytes()
            )
            self.assertGreater(min(record.combined_power_w for record in post_records), 1e9)
            self.assertIsNotNone(SnapshotAdapter.trace_before_sentinel)
            self.assertEqual(
                (bundle / "power_trace.csv").read_bytes(),
                SnapshotAdapter.trace_before_sentinel,
            )

            stored = json.loads((bundle / "summary_metrics.json").read_text())
            metadata_path = bundle / "metadata.json"
            original_metadata = metadata_path.read_bytes()
            metadata = json.loads(original_metadata)
            metadata.pop("idle_drift_bound_w", None)
            metadata["uncertainty_evidence"]["idle_drift"] = {
                "status": "unknown",
                "reason": "post_idle_unavailable",
            }
            metadata_path.write_text(json.dumps(metadata))
            try:
                no_sentinel_baseline = reduce_bundle(bundle)
            finally:
                metadata_path.write_bytes(original_metadata)
            self.assertEqual(
                stored["gross_energy_j"], no_sentinel_baseline.gross_energy_j
            )

    def test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits(self) -> None:
        expected = {
            "inconsistent": "clock_anchor_unresolved",
            "contaminated_post": "drift_term_unknown",
        }
        for mode, reason in expected.items():
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                bundle, summary = self.run_mode(Path(tmp), mode)
                self.assertEqual(summary.status.value, "succeeded")
                self.assertEqual(validate_bundle(bundle, strict=True), [])
                stored = json.loads((bundle / "summary_metrics.json").read_text())
                request_gate = stored["window_evidence_precheck"][
                    "idle_subtracted_request"
                ]
                self.assertIs(request_gate["eligible"], False)
                self.assertIn(reason, request_gate["reasons"])
        # D-078: a wide first sampling interval no longer makes the anchor
        # unresolved. Host scheduling can still trip an independent cadence
        # or envelope-ratio gate, so assert the causal anchor property itself
        # rather than laundering those independent refusals into a pass.
        with self.subTest(mode="wide"), tempfile.TemporaryDirectory() as tmp:
            bundle, summary = self.run_mode(Path(tmp), "wide")
            self.assertEqual(summary.status.value, "succeeded")
            self.assertEqual(validate_bundle(bundle, strict=True), [])
            stored = json.loads((bundle / "summary_metrics.json").read_text())
            request_gate = stored["window_evidence_precheck"]["gross_request"]
            self.assertNotIn("clock_anchor_unresolved", request_gate["reasons"])
            # Same closed allowlist as above: ineligibility is acceptable
            # only via the host-timing-sensitive gates.
            if request_gate["eligible"] is not True:
                self.assertLessEqual(
                    set(request_gate["reasons"]),
                    {
                        "cadence_ratio_below_threshold",
                        "clock_bound_exceeds_quarter_window",
                        "anchor_energy_envelope_exceeds_quarter_metric",
                        "post_window_trace_tail_shorter_than_anchor_bound",
                    },
                )
            self.assertGreaterEqual(
                request_gate["clock_anchor_bound_s"],
                json.loads((bundle / "metadata.json").read_text())[
                    "instrument_calibration"
                ]["verified_effective_b_fiducial_s"],
            )

    def test_strict_rederivation_rejects_evidence_raw_and_marker_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle, summary = run_benchmark(
                production_config(),
                Path(tmp),
                SystemClock(),
                registry=ProductionShapedRegistry(),
                environment_snapshot=None,
            )
            self.assertEqual(summary.status.value, "succeeded")
            targets = {
                "metadata": bundle / "metadata.json",
                "events": bundle / "events.jsonl",
                "post_idle": bundle / "raw" / "powermetrics_idle_post.plist",
            }
            originals = {name: path.read_bytes() for name, path in targets.items()}

            metadata = json.loads(originals["metadata"])
            metadata["clock_anchor_bound_s"] += 0.01
            targets["metadata"].write_text(json.dumps(metadata))
            self.assertTrue(validate_bundle(bundle, strict=True))
            targets["metadata"].write_bytes(originals["metadata"])

            metadata = json.loads(originals["metadata"])
            metadata["uncertainty_evidence"]["clock_anchor"]["method"] = "tampered"
            targets["metadata"].write_text(json.dumps(metadata))
            self.assertTrue(validate_bundle(bundle, strict=True))
            targets["metadata"].write_bytes(originals["metadata"])

            metadata = json.loads(originals["metadata"])
            del metadata["uncertainty_evidence"]
            targets["metadata"].write_text(json.dumps(metadata))
            self.assertTrue(validate_bundle(bundle, strict=True))
            targets["metadata"].write_bytes(originals["metadata"])

            targets["post_idle"].write_bytes(b"not a plist")
            self.assertTrue(validate_bundle(bundle, strict=True))
            targets["post_idle"].write_bytes(originals["post_idle"])

            event_rows = [json.loads(line) for line in originals["events"].decode().splitlines()]
            next(
                event for event in event_rows if event["event_type"] == "sampling_started"
            )["timestamp_s"] += 0.01
            targets["events"].write_text(
                "".join(json.dumps(event) + "\n" for event in event_rows)
            )
            self.assertTrue(validate_bundle(bundle, strict=True))


if __name__ == "__main__":
    unittest.main()
