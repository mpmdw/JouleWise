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
import math
import os
import plistlib
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import joulewise.adapters
from joulewise.adapters.powermetrics import (
    PowermetricsTelemetryAdapter,
    parse_powermetrics_records,
)
from joulewise.bundle_read import BundleReader
from joulewise.cli import validate_bundle
from joulewise.clock import ClockStamp
from joulewise.controller import _load_instrument_calibration_attachment, run_benchmark
from joulewise.environment import evaluate_environment_policy
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig, CampaignPolicy
from joulewise.uncertainty_evidence import (
    ACTIVE_CAPTURE_ANCHOR_METHOD,
    CLOCK_METHOD_V2,
    CLOCK_METHOD_V3,
    SCHEMA_FOR_ANCHOR_METHOD,
    capture_pipeline_refusal,
    derive_powermetrics_anchor_v3,
)
from scripts.run_campaign import assert_production_uncertainty


V3_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "p2038_v3_production"
V3_FIXTURE_PROFILE = V3_FIXTURE_ROOT / "paired_clock_native_records.json"
V2_REFUSAL_FIXTURE = Path(__file__).parent / "fixtures" / "d117_v2_production"
FIXTURE_PROCESS = V3_FIXTURE_ROOT / "fake_powermetrics_process.py"
PRODUCTION_POLICY_PATH = (
    Path(__file__).resolve().parent.parent
    / "configs"
    / "campaign_policies"
    / "quiet_mac_p2_production.json"
)


class RateFitFixtureClock:
    """Replay the v3 fixture's paired clock timeline without a 62 s wall wait."""

    def __init__(self, base_s: float, profile: dict) -> None:
        self._base_s = base_s
        self._now = base_s
        self._stamps = iter(profile["clock_stamps"].values())
        self._advance_now = False

    def now(self) -> float:
        value = self._now
        if self._advance_now:
            self._now += 5.0
        return value

    def stamp(self) -> ClockStamp:
        row = next(self._stamps)
        epoch_s = self._base_s + float(row["epoch_offset_s"])
        monotonic_s = float(row["monotonic_s"])
        self._now = epoch_s
        self._advance_now = True
        return ClockStamp(
            epoch_s=epoch_s,
            monotonic_before_s=monotonic_s - 1e-6,
            monotonic_after_s=monotonic_s + 1e-6,
            wall_resolution_s=1e-6,
            monotonic_resolution_s=1e-6,
        )

    def sleep(self, seconds: float) -> None:
        self._now += seconds

    def info(self) -> dict:
        return {"kind": "p2038-v3-fixture", "epoch_s": self._base_s}


def load_v3_production_fixture(*, base_s: float) -> tuple[dict, dict]:
    """Return the fixture facts and its independently specified v3 result."""

    profile = json.loads(V3_FIXTURE_PROFILE.read_text(encoding="utf-8"))
    stamps = {
        name: ClockStamp(
            epoch_s=base_s + float(row["epoch_offset_s"]),
            monotonic_before_s=float(row["monotonic_s"]) - 1e-6,
            monotonic_after_s=float(row["monotonic_s"]) + 1e-6,
            wall_resolution_s=1e-6,
            monotonic_resolution_s=1e-6,
        )
        for name, row in profile["clock_stamps"].items()
    }
    from joulewise.uncertainty_evidence import NativeAnchorRecord

    records = [
        NativeAnchorRecord(
            elapsed_s=float(row["elapsed_ns"]) / 1_000_000_000.0,
            native_timestamp_s=base_s + float(row["endpoint_offset_s"]),
            power_w=2.0,
            energy_j=2.0,
            is_delta=True,
            elapsed_ns=int(row["elapsed_ns"]),
            native_timestamp_ns=round(
                (base_s + float(row["endpoint_offset_s"])) * 1_000_000_000
            ),
        )
        for row in profile["native_records"]
    ]
    return profile, derive_powermetrics_anchor_v3(stamps=stamps, records=records)


def claim_admission_fixture():
    """Return the registered production policy bound to fixture evidence."""

    policy_raw = PRODUCTION_POLICY_PATH.read_bytes()
    policy = CampaignPolicy.from_mapping(json.loads(policy_raw))
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
        "python_packages": {"mlx": {"version": "0.31.2"}},
    }
    evaluation = evaluate_environment_policy(snapshot, policy.environment_guard)
    policy_sha256 = hashlib.sha256(policy_raw).hexdigest()
    binding = {
        "schema_version": policy.schema_version,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "profile": policy.profile.value,
        "sha256": policy_sha256,
        "source": str(PRODUCTION_POLICY_PATH),
    }
    preflight = {
        "schema_version": "joulewise.campaign_environment_preflight.v1",
        "policy_sha256": policy_sha256,
        "snapshot": snapshot,
        "evaluation": evaluation,
        "override": None,
        "admitted": True,
    }
    return policy, binding, preflight, snapshot, policy_raw


def install_complete_calibration(directory: Path) -> None:
    """Build a hash-bound validation directory for the production attach path."""

    # Reuse the real synthetic 40-pulse plist/event calibration constructed by
    # the reducer regressions. The former fixture paired one unrelated plist
    # frame and a dummy event with forty invented zero-residual rows; F2 now
    # correctly rejects that non-physical combination.
    from tests.test_reduce import self_consistent_calibration
    from joulewise.powermetrics_fiducial import (
        MAX_AGE_S,
        PROTOCOL_V2_ID,
        PROTOCOL_V2_SHA256,
        RESIDUAL_REGION_METHOD,
        capture_wall_time_from_events,
    )

    raw_dir = directory / "raw"
    raw_dir.mkdir(parents=True)
    evidence, raw_bytes, event_bytes = self_consistent_calibration(
        first_endpoint_s=math.floor(time.time() - 60.0) + 0.05
    )
    (raw_dir / "powermetrics.plist").write_bytes(raw_bytes)
    (directory / "events.jsonl").write_bytes(event_bytes)
    bindings = {
        "hardware_model": "Mac15,9",
        "os_build": "25F84",
        "powermetrics_sha256": hashlib.sha256(
            FIXTURE_PROCESS.read_bytes()
        ).hexdigest(),
        "sampling_interval_ms": 100.0,
        "anchor_method_version": ACTIVE_CAPTURE_ANCHOR_METHOD,
        "mlx_version": "0.31.2",
        "pulse_protocol_id": PROTOCOL_V2_ID,
        "power_policy": "ac_high_power",
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "protocol_sha256": PROTOCOL_V2_SHA256,
    }
    evidence["protocol_id"] = PROTOCOL_V2_ID
    evidence["capture_wall_time_s"] = capture_wall_time_from_events(event_bytes)
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
            CampaignPositiveTelemetryAdapter(
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


class CampaignPositiveTelemetryAdapter(PowermetricsTelemetryAdapter):
    """Supply the fixture's thirty-record low-power admission observation.

    The v3 measured trace remains unchanged.  Its independent pre-run slice
    is normalized to the fixture's intended 0.5 W idle state, including the
    persisted raw artifact, so strict replay and the claim gate use identical
    evidence rather than a metadata-only test override.
    """

    def measure_idle(self, config, context=None):
        baseline = super().measure_idle(config, context)
        if context is None:
            return baseline
        raw_path = context.raw_dir / "powermetrics_idle.plist"
        documents = [
            plistlib.loads(frame)
            for frame in raw_path.read_bytes().split(b"\0")
            if frame.strip()
        ]
        for document in documents:
            processor = dict(document["processor"])
            elapsed_s = float(document["elapsed_ns"]) / 1_000_000_000.0
            processor["combined_power"] = 500.0
            processor["cpu_power"] = 500.0
            processor["cpu_energy"] = round(500.0 * elapsed_s)
            document["processor"] = processor
        raw_path.write_bytes(b"\0".join(plistlib.dumps(item) for item in documents))
        rich_path = context.bundle_path / "rich_telemetry_idle.jsonl"
        rich_rows = [
            json.loads(line)
            for line in rich_path.read_text(encoding="utf-8").splitlines()
        ]
        for row in rich_rows:
            row["processor_combined_power_w"] = 0.5
        rich_path.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rich_rows),
            encoding="utf-8",
        )
        return replace(baseline, power_w_mean=0.5, power_w_stddev=0.0)

    def idle_admission_records(self, *, run_id, attempt):
        records = super().idle_admission_records(run_id=run_id, attempt=attempt)
        if records is None:
            return None
        admitted_records = []
        for _ in range(6):
            for record in records:
                admitted = dict(record)
                admitted["processor_combined_power_w"] = 0.5
                admitted_records.append(admitted)
        return admitted_records


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
                # The fixture clock provides the 80 s capture span.  A short
                # mock decode keeps this production-path assertion focused on
                # the telemetry contract rather than simulated token time.
                "output_tokens": 8,
            },
            "sampling": {"power_hz": 10.0, "idle_seconds": 0.5},
        }
    )


class P2038ProductionPathTests(unittest.TestCase):
    def test_window_prepare_refuses_unregistered_instrument_digest_pin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            calibration = Path(tmp) / "calibration"
            install_complete_calibration(calibration)
            evidence_path = calibration / "instrument_evidence.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["binding_evidence"]["powermetrics_binary"].update(
                {
                    "acceptance_id": "unknown-instrument-row",
                    "expected_sha256": evidence["bindings"][
                        "powermetrics_sha256"
                    ],
                }
            )
            evidence_raw = (
                json.dumps(evidence, indent=2, sort_keys=True) + "\n"
            ).encode()
            evidence_path.write_bytes(evidence_raw)
            manifest_path = calibration / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["instrument_evidence.json"] = hashlib.sha256(
                evidence_raw
            ).hexdigest()
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            )
            runtime_digest = hashlib.sha256(FIXTURE_PROCESS.read_bytes()).hexdigest()
            with self.assertRaisesRegex(
                ValueError, "instrument_binary_digest_mismatch"
            ):
                _load_instrument_calibration_attachment(
                    calibration,
                    power_policy="ac_high_power",
                    runtime_powermetrics_sha256=runtime_digest,
                    runtime_power_policy="ac_high_power",
                )

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

    def run_mode(
        self,
        root: Path,
        mode: str,
        *,
        registry: object | None = None,
    ):
        state_path = root / f"{mode}.state"
        policy, binding, preflight, snapshot, _policy_raw = claim_admission_fixture()
        fixture_base_s = float(math.floor(time.time()))
        profile, _anchor = load_v3_production_fixture(base_s=fixture_base_s)
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
                    "P2038_V3_FIXTURE_EPOCH_S": str(fixture_base_s),
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
                RateFitFixtureClock(fixture_base_s, profile),
                registry=registry or ProductionShapedRegistry(),
                reducer=reduce_bundle,
                environment_snapshot=snapshot,
                campaign_policy=policy,
                campaign_policy_binding=binding,
                campaign_environment_preflight=preflight,
                instrument_calibration_dir=calibration_dir,
                instrument_power_policy="ac_high_power",
            )

    def test_real_powermetrics_evidence_path_passes_p2029_p2040_gates(self) -> None:
        fixture_base_s = float(math.floor(time.time()))
        fixture, fixture_anchor = load_v3_production_fixture(
            base_s=fixture_base_s
        )
        self.assertEqual(fixture_anchor["status"], fixture["expected"]["status"])
        self.assertEqual(fixture_anchor["method"], CLOCK_METHOD_V3)
        self.assertEqual(
            fixture_anchor["records_checked"], fixture["expected"]["records_checked"]
        )
        self.assertEqual(
            fixture_anchor["native_rollover_count"],
            fixture["expected"]["native_rollover_count"],
        )
        self.assertGreaterEqual(
            fixture_anchor["rate_fit_baseline_s"],
            fixture["expected"]["minimum_rate_fit_baseline_s"],
        )
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
            self.assertEqual(
                metadata["uncertainty_evidence"]["schema_version"],
                SCHEMA_FOR_ANCHOR_METHOD[ACTIVE_CAPTURE_ANCHOR_METHOD],
            )
            clock_anchor = metadata["uncertainty_evidence"]["clock_anchor"]
            self.assertEqual(clock_anchor["status"], "bounded")
            self.assertEqual(
                clock_anchor["method"],
                ACTIVE_CAPTURE_ANCHOR_METHOD,
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
            # The post-run environment/admission observation is persisted
            # before reduction, so the current strict campaign gate consumes
            # a causally complete v3 fixture rather than a stored refusal.
            self.assertEqual(request_gate["reasons"], [])
            reader = BundleReader(bundle)
            measured_window = reader.measured_window()
            self.assertIsNotNone(measured_window)
            support_end_s = reader.summed_curve()[-1].support_end_s
            self.assertIsNotNone(support_end_s)
            self.assertGreaterEqual(support_end_s, measured_window.end_s)
            # The production assertion and stored campaign gate consume the
            # same active-era evidence.
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
            assertion = assert_production_uncertainty(
                bundle, allow_mock_runtime=True
            )
            self.assertTrue(assertion["request_eligible"])

    def test_retained_v2_production_fixture_is_a_refusal_arm(self) -> None:
        metadata = json.loads(
            (V2_REFUSAL_FIXTURE / "strict_seed_bundle" / "metadata.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            metadata["uncertainty_evidence"]["clock_anchor"]["method"],
            CLOCK_METHOD_V2,
        )
        self.assertEqual(
            validate_bundle(V2_REFUSAL_FIXTURE / "strict_seed_bundle", strict=True),
            [],
        )
        self.assertEqual(capture_pipeline_refusal(metadata), "capture_pipeline_superseded")

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
                        "environment_admission_missing",
                    },
                )
            self.assertIs(gates["idle_subtracted_request"]["eligible"], False)
            self.assertIn(
                "drift_term_unknown",
                gates["idle_subtracted_request"]["reasons"],
            )

    def test_extreme_post_idle_sentinel_cannot_leak_into_measured_trace_or_energy(self) -> None:
        class SnapshotAdapter(CampaignPositiveTelemetryAdapter):
            trace_before_sentinel: bytes | None = None

            def measure_post_run_idle(self, config, baseline, context):
                assert context is not None
                type(self).trace_before_sentinel = (
                    context.bundle_path / "power_trace.csv"
                ).read_bytes()
                return super().measure_post_run_idle(config, baseline, context)

        class SnapshotRegistry(ProductionShapedRegistry):
            def resolve_telemetry(self, config, clock):
                drain_timer = LogicalDrainTimer()
                return (
                    SnapshotAdapter(
                        clock,
                        executable=str(FIXTURE_PROCESS),
                        privilege_prefix=(sys.executable,),
                        drain_monotonic=drain_timer.monotonic,
                        drain_sleep=drain_timer.sleep,
                    ),
                    None,
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle, summary = self.run_mode(
                root,
                "extreme_post",
                registry=SnapshotRegistry(),
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
                        "environment_admission_missing",
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
            bundle, summary = self.run_mode(Path(tmp), "normal")
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
