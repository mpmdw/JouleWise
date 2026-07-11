"""Production-shaped P2-038 assertion over the real evidence-writing path.

This CI test uses a mock runtime only to avoid an MLX dependency. Telemetry is
the real PowermetricsTelemetryAdapter, running a real child process and the
committed captured fixture plists through the production parser, controller,
reducer, and strict validator. It does not replace the required quiet-machine
lead shakedown against true /usr/bin/powermetrics and approved backup.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joulewise.adapters
from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.cli import validate_bundle
from joulewise.clock import SystemClock
from joulewise.controller import run_benchmark
from joulewise.schemas import BenchmarkConfig
from scripts.run_campaign import assert_production_uncertainty


FIXTURE_PROCESS = Path(__file__).parent / "fixtures" / "fake_powermetrics_process.py"


class ProductionShapedRegistry:
    def resolve_runtime(self, config, clock):
        return joulewise.adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config, clock):
        return (
            PowermetricsTelemetryAdapter(
                clock,
                executable=str(FIXTURE_PROCESS),
                privilege_prefix=(sys.executable,),
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
    def run_mode(self, root: Path, mode: str):
        state_path = root / f"{mode}.state"
        with patch.dict(
            os.environ,
            {
                "P2038_FAKE_POWERMETRICS_MODE": mode,
                "P2038_FAKE_POWERMETRICS_STATE": str(state_path),
            },
        ):
            return run_benchmark(
                production_config(),
                root,
                SystemClock(),
                registry=ProductionShapedRegistry(),
                environment_snapshot=None,
            )

    def test_real_powermetrics_evidence_path_passes_p2029_p2040_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle, summary = run_benchmark(
                production_config(),
                Path(tmp),
                SystemClock(),
                registry=ProductionShapedRegistry(),
                environment_snapshot=None,
            )
            self.assertEqual(summary.status.value, "succeeded")
            self.assertEqual(validate_bundle(bundle, strict=True), [])
            metadata = json.loads((bundle / "metadata.json").read_text())
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
            self.assertEqual(metadata["uncertainty_evidence"]["schema_version"], "p2-038.1")
            request_gate = stored["claim_eligibility"]["request"]
            self.assertIs(request_gate["eligible"], True)
            self.assertEqual(request_gate["reasons"], [])
            assertion = assert_production_uncertainty(
                bundle, allow_mock_runtime=True
            )
            self.assertIs(assertion["request_eligible"], True)

    def test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits(self) -> None:
        expected = {
            "inconsistent": "clock_bound_unrecorded",
            "wide": "clock_bound_exceeds_quarter_window",
            "contaminated_post": "drift_term_unknown",
        }
        for mode, reason in expected.items():
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                bundle, summary = self.run_mode(Path(tmp), mode)
                self.assertEqual(summary.status.value, "succeeded")
                self.assertEqual(validate_bundle(bundle, strict=True), [])
                stored = json.loads((bundle / "summary_metrics.json").read_text())
                request_gate = stored["claim_eligibility"]["request"]
                self.assertIs(request_gate["eligible"], False)
                self.assertIn(reason, request_gate["reasons"])

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
