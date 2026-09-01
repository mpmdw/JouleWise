"""Defect-shaped tests for TRANSFER-FIDUCIAL-01."""

from __future__ import annotations

import hashlib
import json
import math
import plistlib
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from joulewise import powermetrics_fiducial
from joulewise import transfer_fiducial
from joulewise.powermetrics_fiducial import (
    PROTOCOL_ID,
    RESIDUAL_REGION_METHOD,
    CommandedPulse,
    TraceInterval,
    detect_pulses,
)
from joulewise.schemas import BenchmarkConfig
from joulewise.transfer_fiducial import (
    TRANSFER_FIDUCIAL_ESTIMATOR_SHA256,
    TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND_V2,
    TRANSFER_FIDUCIAL_PLAN_SCHEMA_V2,
    TransferFiducialError,
    build_capture,
    canonical_receipt_bytes,
    classify_bundle,
    fit_run,
    issue_pre_data_receipt,
    receipt_sha256_sidecar_path,
    summarize_target_edge_radii,
    transfer_fiducial_rule_constants,
)
from scripts import fit_transfer_fiducial as fit_transfer_cli
from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

ROOT = Path(__file__).resolve().parents[1]
CI_PYTHON = Path("/Users/edr/code/JouleWise/.venv/bin/python")


def _edge_shape(t_s: float, on_s: float, off_s: float) -> float:
    if not on_s < t_s < off_s:
        return 0.0
    return max(0.0, min(1.0, (t_s - on_s) / 0.1, (off_s - t_s) / 0.1))


def synthetic_valley_trace(*, gap_shift_s: float = 0.0) -> list[TraceInterval]:
    intervals: list[TraceInterval] = []
    for index in range(130):
        start_s = index / 10.0
        end_s = (index + 1) / 10.0
        midpoint_s = (start_s + end_s) / 2.0
        # The shift moves the entire 500 ms valley relative to the commanded
        # stamps. One-interval edge ramps avoid asserting an instantaneous
        # physical power step while preserving a >=10 W interior plateau.
        power_w = (
            2.0
            + 20.0 * _edge_shape(midpoint_s, 5.0 + gap_shift_s, 6.0 + gap_shift_s)
            + 20.0 * _edge_shape(midpoint_s, 6.5 + gap_shift_s, 7.5 + gap_shift_s)
            + 0.03 * math.sin(2.3 * index)
        )
        intervals.append(TraceInterval(start_s, end_s, power_w))
    return intervals


def _stamp(epoch_s: float) -> dict[str, float]:
    return {
        "epoch_s": epoch_s,
        "monotonic_before_s": epoch_s,
        "monotonic_after_s": epoch_s,
        "wall_resolution_s": 0.0,
        "monotonic_resolution_s": 0.0,
    }


def _event(event_type: str, phase: str, epoch_s: float) -> dict[str, object]:
    metadata: dict[str, object] = {
        "clock_stamp": _stamp(epoch_s),
        "diagnostic_kind": "transfer_fiducial_v1",
    }
    if event_type.startswith("fiducial_gap_"):
        metadata.update(
            boundary_semantics="first_yield_one_step_queued",
            commanded_gap_s=0.5,
            synchronization="mlx.core.synchronize_after_gap_start_stamp",
        )
    return {
        "timestamp_s": epoch_s,
        "event_type": event_type,
        "phase": phase,
        "message": f"synthetic {event_type} {phase}",
        "metadata": metadata,
    }


def _config_mapping(run_id: str) -> dict[str, object]:
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "model": {
            "name": "Qwen2.5-1.5B-Instruct-4bit",
            "family": "qwen2.5",
            "source": "/synthetic/model",
            "revision": "synthetic-revision",
            "weight_format": "mlx",
            "context_window": 32768,
        },
        "quantization": {"name": "int4", "bits": 4},
        "hardware_target": {
            "id": "macbook_m3_max",
            "transport": "local",
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "device_kind": "apple_silicon_unified_memory",
        },
        "workload_profile": {
            "name": "transfer_fiducial_v1",
            "prompt_tokens": 4096,
            "output_tokens": 512,
            "repetitions": 1,
            "warmup_runs": 1,
            "transfer_fiducial_gap_s": 0.5,
        },
        "sampling": {"power_hz": 10.0, "idle_seconds": 30.0},
        "run_metadata": {"project": "synthetic-transfer-test"},
    }


def _plist_trace() -> bytes:
    frames: list[bytes] = []
    for index, interval in enumerate(synthetic_valley_trace()):
        processor = {
            "cpu_power": 1000.0,
            "gpu_power": interval.power_w * 1000.0,
            "ane_power": 0.0,
            "cpu_energy": 100,
            "gpu_energy": 100,
            "ane_energy": 0,
        }
        frames.append(
            plistlib.dumps(
                {
                    "timestamp": datetime(2026, 8, 28, tzinfo=timezone.utc),
                    "elapsed_ns": 100_000_000,
                    "processor": processor,
                    "is_delta": True,
                }
            )
        )
    return b"\0".join(frames)


def make_synthetic_capture_fixture(root: Path) -> tuple[Path, Path, Path]:
    runs_root = root / "runs"
    calibration_dir = root / "calibration"
    configs_dir = root / "configs"
    runs_root.mkdir(parents=True)
    calibration_dir.mkdir()
    configs_dir.mkdir()
    bindings = {
        "hardware_model": "Mac15,9",
        "os_build": "25F84",
        "powermetrics_sha256": "a" * 64,
        "sampling_interval_ms": 100,
        "anchor_method_version": CLOCK_METHOD_V3,
        "mlx_version": "0.31.2",
        "pulse_protocol_id": PROTOCOL_ID,
        "power_policy": "ac_high_power",
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "protocol_sha256": powermetrics_fiducial.PROTOCOL_V3_SHA256,
    }
    calibration_evidence = {
        "status": "valid",
        "reasons": [],
        "validation_id": "synthetic-transfer-calibration",
        "capture_wall_time_s": 1_777_000_000.0,
        "protocol_id": PROTOCOL_ID,
        "residual_region_method": RESIDUAL_REGION_METHOD,
        "b_fiducial_s": 0.2,
        "bindings": bindings,
    }
    calibration_raw = (
        json.dumps(calibration_evidence, indent=2, sort_keys=True) + "\n"
    ).encode()
    (calibration_dir / "instrument_evidence.json").write_bytes(calibration_raw)
    calibration_sha = hashlib.sha256(calibration_raw).hexdigest()
    descriptors: list[dict[str, object]] = []
    for run_index in range(1, 11):
        run_id = f"synthetic-transfer-r{run_index:02d}"
        mapping = _config_mapping(run_id)
        config = BenchmarkConfig.from_mapping(mapping)
        normalized = (
            json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"
        ).encode()
        source_path = configs_dir / f"{run_id}.json"
        source_path.write_bytes(normalized)
        descriptor = {
            "bundle_id": run_id,
            "config_path": str(source_path.resolve()),
            "config_sha256": hashlib.sha256(normalized).hexdigest(),
        }
        descriptors.append(descriptor)
        bundle = runs_root / run_id
        (bundle / "raw").mkdir(parents=True)
        (bundle / "config.json").write_bytes(normalized)
        events = [
            _event("phase_start", "prefill", 5.0),
            _event("phase_end", "prefill", 6.0),
            _event("fiducial_gap_start", "fiducial_gap", 6.0),
            _event("fiducial_gap_end", "fiducial_gap", 6.5),
            _event("phase_start", "decode", 6.5),
            _event("phase_end", "decode", 7.5),
        ]
        (bundle / "events.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in events)
        )
        metadata = {
            "git_commit": "1" * 40,
            "device": {"hw_model": "Mac15,9", "kern_osversion": "25F84"},
            "uncertainty_evidence": {
                "clock_anchor": {
                    "status": "bounded",
                    "method": CLOCK_METHOD_V3,
                    "first_sample_end_point_epoch_s": 0.1,
                    "effective_clock_anchor_bound_s": 0.002,
                }
            },
            "instrument_calibration": {
                "artifact_path": "calibration/instrument_evidence.json",
                "artifact_sha256": calibration_sha,
                "b_fiducial_s": 0.2,
                "bindings": bindings,
                "binding_observations": {
                    "powermetrics_sha256": bindings["powermetrics_sha256"],
                    "power_policy": bindings["power_policy"],
                },
            },
        }
        (bundle / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        (bundle / "raw" / "powermetrics.plist").write_bytes(_plist_trace())
    stratum_config = _config_mapping("ignored")
    plan = {
        "schema_version": "joulewise.transfer_fiducial_plan.v1",
        "diagnostic": True,
        "claim_bearing": False,
        "diagnostic_kind": "transfer_fiducial_v1",
        "pooling": "forbidden",
        "strata": [
            {
                "stratum_id": "synthetic-q15",
                "model": stratum_config["model"],
                "quantization": stratum_config["quantization"],
                "hardware_target": stratum_config["hardware_target"],
                "prompt_tokens": 4096,
                "output_tokens": 512,
                "repetitions": 1,
                "transfer_fiducial_gap_s": 0.5,
                "planned_runs": 10,
                "configs": descriptors,
            }
        ],
    }
    plan_path = root / "plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return plan_path, runs_root, calibration_dir


def make_synthetic_v2_capture_fixture(root: Path) -> tuple[Path, Path, Path]:
    """Promote a fresh V1 fixture into the explicit V2 protocol for tests."""

    plan_path, runs_root, calibration_dir = make_synthetic_capture_fixture(root)
    evidence_path = calibration_dir / "instrument_evidence.json"
    evidence = json.loads(evidence_path.read_text())
    evidence["capture_wall_time_s"] = 1.0
    evidence_raw = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode()
    evidence_path.write_bytes(evidence_raw)
    evidence_sha256 = hashlib.sha256(evidence_raw).hexdigest()

    plan = json.loads(plan_path.read_text())
    plan["schema_version"] = TRANSFER_FIDUCIAL_PLAN_SCHEMA_V2
    plan["diagnostic_kind"] = TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND_V2
    plan["pre_data_receipt_required"] = True
    plan["fit_rule_constants"] = transfer_fiducial_rule_constants()
    stratum = plan["strata"][0]
    stratum.update(
        minimum_prefill_s=0.8,
        minimum_decode_s=0.8,
        post_window_sampling_dwell_s=6.0,
    )
    prompt_text = "A deterministic prompt used only by the transfer V2 fixture."
    stratum["prompt_text_utf8_sha256"] = hashlib.sha256(
        prompt_text.encode("utf-8")
    ).hexdigest()
    for descriptor in stratum["configs"]:
        source_path = Path(descriptor["config_path"])
        config = json.loads(source_path.read_text())
        config["workload_profile"].pop("prompt_tokens")
        config["workload_profile"]["prompt_text"] = prompt_text
        config_raw = (
            json.dumps(
                BenchmarkConfig.from_mapping(config).to_dict(),
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode()
        source_path.write_bytes(config_raw)
        descriptor["config_sha256"] = hashlib.sha256(config_raw).hexdigest()
        bundle = runs_root / descriptor["bundle_id"]
        (bundle / "config.json").write_bytes(config_raw)
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["trace_window_margins"] = {
            "requested_post_window_dwell_s": 6.0,
            "achieved_pre_window_margin_s": 0.0,
            "achieved_post_window_margin_s": 0.0,
        }
        metadata["instrument_calibration"]["artifact_sha256"] = evidence_sha256
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return plan_path, runs_root, calibration_dir


def write_receipt_and_sidecar(path: Path, receipt: dict[str, object]) -> None:
    rendered = canonical_receipt_bytes(receipt)
    path.write_bytes(rendered)
    receipt_sha256_sidecar_path(path).write_text(
        hashlib.sha256(rendered).hexdigest() + "\n"
    )


def issue_receipt_cli(plan: Path, calibration: Path, receipt: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(CI_PYTHON if CI_PYTHON.is_file() else Path(sys.executable)),
            str(ROOT / "scripts" / "fit_transfer_fiducial.py"),
            "--plan",
            str(plan),
            "--pulse-calibration-dir",
            str(calibration),
            "--issue-receipt",
            "--receipt",
            str(receipt),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class TransferFiducialTests(unittest.TestCase):
    def test_two_active_pulses_recover_known_inserted_valley_edges(self) -> None:
        pulses = [CommandedPulse(5.0, 6.0), CommandedPulse(6.5, 7.5)]
        clean = detect_pulses(
            synthetic_valley_trace(), pulses, trace_anchor_bound_s=0.001
        )
        self.assertTrue(clean.all_pulses_detected, clean.reasons)
        self.assertGreaterEqual(min(fit.amplitude_w for fit in clean.fits), 10.0)
        self.assertLessEqual(abs(clean.fits[0].delta_off_s), 0.1)
        self.assertLessEqual(abs(clean.fits[1].delta_on_s), 0.1)

        # The complete-region projection is orthogonal to the defect shape:
        # pin it to a narrow accepted rectangle so the twin isolates whether
        # coordinate fitting follows the shifted TRACE rather than the stamps.
        with patch.object(
            powermetrics_fiducial,
            "_accepted_region_projection",
            return_value=(0.29, 0.31, 0.29, 0.31),
        ):
            shifted = detect_pulses(
                synthetic_valley_trace(gap_shift_s=0.3),
                pulses,
                trace_anchor_bound_s=0.001,
            )
        self.assertTrue(shifted.all_pulses_detected, shifted.reasons)
        self.assertAlmostEqual(shifted.fits[0].delta_off_s, 0.3, delta=0.1)
        self.assertAlmostEqual(shifted.fits[1].delta_on_s, 0.3, delta=0.1)
        self.assertGreater(
            shifted.fits[0].delta_off_s - clean.fits[0].delta_off_s, 0.2
        )

    def test_transfer_classifier_uses_config_or_events_and_rejects_mismatch(self) -> None:
        config = {"workload_profile": {"transfer_fiducial_gap_s": 0.5}}
        events = [_event("fiducial_gap_start", "fiducial_gap", 1.0)]
        self.assertEqual(
            classify_bundle(config, events),
            classify_bundle(config, events).__class__(True, True, True, False),
        )
        config_only = classify_bundle(config, [])
        event_only = classify_bundle({}, events)
        self.assertTrue(config_only.is_diagnostic and config_only.inconsistent)
        self.assertTrue(event_only.is_diagnostic and event_only.inconsistent)
        self.assertFalse(classify_bundle({}, []).is_diagnostic)

    def test_transfer_fit_is_inconclusive_if_any_pulse_is_undetected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan, runs, calibration = make_synthetic_capture_fixture(Path(tmp))
            del plan, calibration
            bundle = runs / "synthetic-transfer-r01"
            frames = plistlib.loads((bundle / "raw" / "powermetrics.plist").read_bytes().split(b"\0")[0])
            raw = (bundle / "raw" / "powermetrics.plist").read_bytes()
            documents = [plistlib.loads(frame) for frame in raw.split(b"\0") if frame]
            for index, document in enumerate(documents):
                midpoint = (index + 0.5) / 10.0
                if 6.5 <= midpoint <= 7.5:
                    document["processor"]["gpu_power"] = 3000.0
            bundle.joinpath("raw", "powermetrics.plist").write_bytes(
                b"\0".join(plistlib.dumps(document) for document in documents)
            )
            fit = fit_run(bundle)
            self.assertEqual(fit.verdict, "inconclusive")
            self.assertIn("not_all_pulses_detected", fit.reasons)
            del frames

    def test_transfer_fit_uses_max_target_edge_radius_not_p95(self) -> None:
        values = [0.01] * 19 + [0.2]
        summary = summarize_target_edge_radii(values)
        self.assertEqual(summary["residual_transfer_s"], 0.2)
        self.assertEqual(summary["residual_p95_s_diagnostic_only"], 0.01)
        self.assertNotEqual(
            summary["residual_transfer_s"],
            summary["residual_p95_s_diagnostic_only"],
        )

    def test_transfer_capture_records_estimator_revision_and_both_magnitudes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan, runs, calibration = make_synthetic_capture_fixture(Path(tmp))
            capture = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
            )
            self.assertEqual(capture["estimator_revision"], RESIDUAL_REGION_METHOD)
            self.assertEqual(capture["b_pulse_s"], 0.2)
            self.assertIsInstance(capture["residual_transfer_s"], float)
            self.assertEqual(capture["verdict"], "supported")
            self.assertEqual(capture["target_edge_sample_count"], 20)
            self.assertTrue(capture["diagnostic"])
            self.assertFalse(capture["claim_bearing"])

            output = Path(tmp) / "capture.json"
            result = subprocess.run(
                [
                    str(CI_PYTHON if CI_PYTHON.is_file() else Path(sys.executable)),
                    str(ROOT / "scripts" / "fit_transfer_fiducial.py"),
                    "--plan", str(plan),
                    "--runs-root", str(runs),
                    "--pulse-calibration-dir", str(calibration),
                    "--output", str(output),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), json.loads(result.stdout))

    def test_transfer_estimator_source_digest_is_frozen(self) -> None:
        digest = hashlib.sha256(
            (ROOT / "joulewise" / "powermetrics_fiducial.py").read_bytes()
        ).hexdigest()
        self.assertEqual(digest, TRANSFER_FIDUCIAL_ESTIMATOR_SHA256)
        self.assertEqual(
            digest,
            "386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92",
        )


class TransferFiducialV1CompatibilityTests(unittest.TestCase):
    def test_v1_invalid_planned_config_still_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan, runs, calibration = make_synthetic_capture_fixture(Path(tmp))
            plan_value = json.loads(plan.read_text())
            source = Path(plan_value["strata"][0]["configs"][0]["config_path"])
            invalid = json.loads(source.read_text())
            invalid["workload_profile"]["output_tokens"] = 0
            source.write_text(json.dumps(invalid, indent=2, sort_keys=True) + "\n")
            with self.assertRaisesRegex(
                TransferFiducialError, "planned config is invalid"
            ):
                build_capture(
                    plan_path=plan,
                    runs_root=runs,
                    pulse_calibration_dir=calibration,
                )


class TransferFiducialV2ReceiptTests(unittest.TestCase):
    def _issue(
        self, plan: Path, calibration: Path, receipt_path: Path
    ) -> dict[str, object]:
        receipt = issue_pre_data_receipt(
            plan_path=plan,
            pulse_calibration_dir=calibration,
        )
        write_receipt_and_sidecar(receipt_path, receipt)
        return receipt

    def test_v2_requires_receipt_while_v1_remains_receipt_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, runs, calibration = make_synthetic_v2_capture_fixture(root)
            missing = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
            )
            self.assertEqual(missing["verdict"], "inconclusive")
            self.assertIn("pre_data_receipt_missing", missing["reasons"])
            receipt_path = root / "pre_data_receipt.json"
            self._issue(plan, calibration, receipt_path)
            capture = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertEqual(capture["verdict"], "supported", capture["reasons"])

    def test_receipt_binds_exact_config_and_receipt_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, runs, calibration = make_synthetic_v2_capture_fixture(root)
            receipt_path = root / "pre_data_receipt.json"
            receipt = self._issue(plan, calibration, receipt_path)
            self.assertEqual(receipt_path.read_bytes(), canonical_receipt_bytes(receipt))

            plan_value = json.loads(plan.read_text())
            source = Path(plan_value["strata"][0]["configs"][0]["config_path"])
            original_source = source.read_bytes()
            source.write_bytes(original_source + b" ")
            config_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn(
                "pre_data_receipt_config_source_sha256_mismatch",
                config_drift["reasons"],
            )
            source.write_bytes(original_source)

            receipt_path.write_bytes(receipt_path.read_bytes() + b" ")
            receipt_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn("pre_data_receipt_noncanonical_json", receipt_drift["reasons"])
            self.assertIn(
                "pre_data_receipt_sha256_sidecar_mismatch",
                receipt_drift["reasons"],
            )

    def test_receipt_binds_actual_wrapper_core_and_estimator_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, runs, calibration = make_synthetic_v2_capture_fixture(root)
            wrapper = root / "fit_transfer_fiducial.py"
            core = root / "transfer_fiducial.py"
            estimator = root / "powermetrics_fiducial.py"
            wrapper.write_bytes((ROOT / "scripts/fit_transfer_fiducial.py").read_bytes())
            core.write_bytes((ROOT / "joulewise/transfer_fiducial.py").read_bytes())
            estimator.write_bytes(
                (ROOT / "joulewise/powermetrics_fiducial.py").read_bytes()
            )
            with ExitStack() as stack:
                stack.enter_context(
                    patch.object(transfer_fiducial, "_FITTER_SOURCE_REL", wrapper)
                )
                stack.enter_context(
                    patch.object(transfer_fiducial, "_FITTER_MODULE_REL", core)
                )
                stack.enter_context(
                    patch.object(powermetrics_fiducial, "__file__", str(estimator))
                )
                receipt_path = root / "pre_data_receipt.json"
                self._issue(plan, calibration, receipt_path)
                cases = (
                    (
                        wrapper,
                        "pre_data_receipt_fitter_source_sha256_mismatch",
                    ),
                    (
                        core,
                        "pre_data_receipt_fitter_module_source_sha256_mismatch",
                    ),
                    (
                        estimator,
                        "pre_data_receipt_estimator_source_sha256_mismatch",
                    ),
                )
                for source_path, reason in cases:
                    with self.subTest(source=source_path.name):
                        original = source_path.read_bytes()
                        source_path.write_bytes(original + b" ")
                        capture = build_capture(
                            plan_path=plan,
                            runs_root=runs,
                            pulse_calibration_dir=calibration,
                            pre_data_receipt_path=receipt_path,
                        )
                        self.assertEqual(capture["verdict"], "inconclusive")
                        self.assertIn(reason, capture["reasons"])
                        source_path.write_bytes(original)

    def test_receipt_binds_plan_calibration_and_rule_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, runs, calibration = make_synthetic_v2_capture_fixture(root)
            receipt_path = root / "pre_data_receipt.json"
            receipt = self._issue(plan, calibration, receipt_path)

            original_plan = plan.read_bytes()
            plan.write_bytes(original_plan + b" ")
            plan_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn("pre_data_receipt_plan_sha256_mismatch", plan_drift["reasons"])
            plan.write_bytes(original_plan)

            evidence = calibration / "instrument_evidence.json"
            original_evidence = evidence.read_bytes()
            evidence.write_bytes(original_evidence + b" ")
            calibration_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn(
                "pre_data_receipt_calibration_identity_mismatch",
                calibration_drift["reasons"],
            )
            evidence.write_bytes(original_evidence)

            receipt["fit_rule_constants"]["minimum_prefill_s"] = 0.7
            write_receipt_and_sidecar(receipt_path, receipt)
            rule_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn(
                "pre_data_receipt_fit_rule_constants_mismatch",
                rule_drift["reasons"],
            )

    def test_duplicate_and_concurrent_receipt_issuance_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, _runs, calibration = make_synthetic_v2_capture_fixture(root)
            receipt_path = root / "issued.json"
            first = issue_receipt_cli(plan, calibration, receipt_path)
            second = issue_receipt_cli(plan, calibration, receipt_path)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 2)
            self.assertIn("pre_data_receipt_already_exists", second.stderr)
            issued = json.loads(first.stdout)
            self.assertEqual(receipt_path.read_bytes(), canonical_receipt_bytes(issued))
            self.assertEqual(
                receipt_sha256_sidecar_path(receipt_path).read_text(),
                hashlib.sha256(receipt_path.read_bytes()).hexdigest() + "\n",
            )

            race_path = root / "race.json"
            barrier = threading.Barrier(2)

            def publish() -> str:
                barrier.wait()
                try:
                    fit_transfer_cli._publish_pre_data_receipt(race_path, issued)
                except TransferFiducialError as exc:
                    return str(exc)
                return "published"

            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = list(executor.map(lambda _index: publish(), range(2)))
            self.assertEqual(outcomes.count("published"), 1)
            self.assertEqual(outcomes.count("pre_data_receipt_already_exists"), 1)

    def test_v2_dwell_and_calibration_time_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, runs, calibration = make_synthetic_v2_capture_fixture(root)
            receipt_path = root / "pre_data_receipt.json"
            self._issue(plan, calibration, receipt_path)
            metadata_path = runs / "synthetic-transfer-r01" / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["trace_window_margins"]["requested_post_window_dwell_s"] = 5.0
            metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
            dwell_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn(
                "synthetic-transfer-r01:post_window_sampling_dwell_mismatch",
                dwell_drift["reasons"],
            )

            evidence_path = calibration / "instrument_evidence.json"
            evidence = json.loads(evidence_path.read_text())
            evidence["capture_wall_time_s"] = 6.0
            evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
            temporal_drift = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertIn(
                "synthetic-transfer-r01:pre_data_receipt_calibration_not_earlier",
                temporal_drift["reasons"],
            )

    def test_v2_invalid_planned_config_is_named_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan, runs, calibration = make_synthetic_v2_capture_fixture(root)
            receipt_path = root / "pre_data_receipt.json"
            self._issue(plan, calibration, receipt_path)
            plan_value = json.loads(plan.read_text())
            source = Path(plan_value["strata"][0]["configs"][0]["config_path"])
            invalid = json.loads(source.read_text())
            invalid["workload_profile"]["output_tokens"] = 0
            source.write_text(json.dumps(invalid, indent=2, sort_keys=True) + "\n")
            capture = build_capture(
                plan_path=plan,
                runs_root=runs,
                pulse_calibration_dir=calibration,
                pre_data_receipt_path=receipt_path,
            )
            self.assertEqual(capture["verdict"], "inconclusive")
            self.assertIn(
                "synthetic-transfer-r01:planned_config_unreadable_or_invalid",
                capture["reasons"],
            )


if __name__ == "__main__":
    unittest.main()
