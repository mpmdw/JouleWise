"""Cross-cutting adversarial coverage for the P2-038 capture eras."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import cli
from joulewise.schemas import TelemetryBackend
from joulewise.uncertainty_evidence import (
    CLOCK_METHOD_V2,
    CLOCK_METHOD_V3,
    SCHEMA_VERSION_V2,
    SCHEMA_VERSION_V3,
    capture_pipeline_refusal,
)
from tests.test_powermetrics import FIXTURE, make_config


class _Reader:
    def __init__(self, root: Path, metadata: dict, config=None) -> None:
        self.path = root
        self._metadata = metadata
        self._config = config

    def raw_metadata(self) -> dict:
        return self._metadata

    def config(self):
        return self._config


class CapturePipelineEraTests(unittest.TestCase):
    def _strict_problems(self, schema: str, method: str) -> list[str]:
        # Missing stamps intentionally stops before byte replay: this is the
        # crossed-era refusal attack, not a coincidental estimator mismatch.
        metadata = {
            "uncertainty_evidence": {
                "schema_version": schema,
                "telemetry_backend": "powermetrics",
                "clock_anchor": {"method": method},
                "sample_phase": {},
            }
        }
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            cli,
            "_validated_config_telemetry_backend",
            return_value=TelemetryBackend.POWERMETRICS,
        ):
            return cli._strict_uncertainty_evidence_problems(
                _Reader(Path(tmp), metadata)  # type: ignore[arg-type]
            )

    def test_crossed_schema_method_pairs_refuse_before_rederivation(self) -> None:
        for schema, method in (
            (SCHEMA_VERSION_V2, CLOCK_METHOD_V3),
            (SCHEMA_VERSION_V3, CLOCK_METHOD_V2),
        ):
            with self.subTest(schema=schema, method=method):
                problems = self._strict_problems(schema, method)
                self.assertIn(
                    "strict: uncertainty evidence: clock_anchor_era_inconsistent",
                    problems,
                )

    def test_claim_barrier_rejects_every_non_v3_stored_method(self) -> None:
        for method in (CLOCK_METHOD_V2, "unregistered-anchor-method"):
            with self.subTest(method=method):
                self.assertEqual(
                    capture_pipeline_refusal(
                        {"uncertainty_evidence": {"clock_anchor": {"method": method}}}
                    ),
                    "capture_pipeline_superseded",
                )
        self.assertIsNone(
            capture_pipeline_refusal(
                {
                    "uncertainty_evidence": {
                        "clock_anchor": {"method": CLOCK_METHOD_V3}
                    }
                }
            )
        )

    def test_v3_corrupt_rich_telemetry_is_not_fail_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "raw" / "powermetrics.plist").write_bytes(FIXTURE.read_bytes())
            (root / "rich_telemetry.jsonl").write_text('{"corrupt":true}\n')
            metadata = {
                "uncertainty_evidence": {
                    "schema_version": SCHEMA_VERSION_V3,
                    "clock_anchor": {
                        "status": "bounded",
                        "method": CLOCK_METHOD_V3,
                        "first_sample_end_point_epoch_s": 1_783_394_101.0,
                    },
                }
            }
            problems = cli._strict_rich_telemetry_problems(
                _Reader(root, metadata, make_config())  # type: ignore[arg-type]
            )
        self.assertEqual(len(problems), 1)
        self.assertIn("does not match", problems[0])

    def test_v3_unresolved_rich_telemetry_uses_its_fallback_endpoint(self) -> None:
        self.assertEqual(
            cli._powermetrics_trace_endpoint_s(
                {},
                {
                    "method": CLOCK_METHOD_V3,
                    "status": "unknown",
                    "trace_fallback_endpoint_epoch_s": 42.0,
                },
            ),
            42.0,
        )

    def test_adapter_empty_capture_emits_the_active_v3_method(self) -> None:
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        from joulewise.clock import ClockStamp, FakeClock

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        stamp = ClockStamp(1.0, 1.0, 1.0, 0.0, 0.0)
        with (
            patch.object(adapter, "_drain_until_stop_bracket", return_value=None),
            patch.object(adapter, "_take_measured_capture", return_value=(None, None)),
        ):
            result = adapter.stop_sampling_with_evidence(
                make_config(),
                None,
                sampling_started=stamp,
                sampling_stopped=stamp,
            )
        self.assertEqual(
            result.uncertainty_evidence["clock_anchor"]["method"],
            CLOCK_METHOD_V3,
        )

    def test_adapter_bracket_rederivation_emits_the_active_v3_method(self) -> None:
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        from joulewise.clock import ClockStamp, FakeClock
        from tests.test_powermetrics import documents_to_stream, fixture_documents

        capture = documents_to_stream(fixture_documents())
        seen_methods: list[str] = []

        def deriver(method: str):
            seen_methods.append(method)
            return lambda **_kwargs: (
                {
                    "clock_anchor": {
                        "status": "bounded",
                        "method": method,
                        "admissible_lower_epoch_s": 100.0,
                    }
                },
                100.0,
            )

        adapter = PowermetricsTelemetryAdapter(FakeClock(start=100.0))
        stamp = ClockStamp(100.0, 100.0, 100.0, 0.0, 0.0)
        with (
            patch.object(adapter, "_drain_until_stop_bracket", return_value=101.0),
            patch.object(adapter, "_take_measured_capture", return_value=(capture, None)),
            patch.object(adapter, "_freeze_stop_bracketing_prefix", return_value=capture),
            patch(
                "joulewise.adapters.powermetrics.resolve_clock_evidence_deriver",
                side_effect=deriver,
            ),
        ):
            result = adapter.stop_sampling_with_evidence(
                make_config(),
                None,
                sampling_started=stamp,
                sampling_stopped=stamp,
            )
        self.assertEqual(seen_methods, [CLOCK_METHOD_V3, CLOCK_METHOD_V3])
        self.assertEqual(
            result.uncertainty_evidence["clock_anchor"]["method"],
            CLOCK_METHOD_V3,
        )

    def test_adapter_drain_probe_emits_the_active_v3_method(self) -> None:
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        from joulewise.clock import ClockStamp, FakeClock
        from tests.test_powermetrics import documents_to_stream, fixture_documents

        class RunningProcess:
            def poll(self):
                return None

        adapter = PowermetricsTelemetryAdapter(FakeClock())
        adapter._process = RunningProcess()
        adapter._first_parse_stamp = ClockStamp(80.0, 80.0, 80.0, 0.0, 0.0)
        with tempfile.TemporaryDirectory() as tmp:
            adapter._capture_path = Path(tmp) / "capture.plist"
            adapter._capture_path.write_bytes(
                documents_to_stream(fixture_documents()[:1])
            )
            with patch(
                "joulewise.adapters.powermetrics.resolve_clock_evidence_deriver",
                return_value=lambda **_kwargs: (
                    {"clock_anchor": {"admissible_lower_epoch_s": 90.0}},
                    90.0,
                ),
            ) as resolver:
                adapter._drain_until_stop_bracket(
                    make_config(),
                    sampling_started=ClockStamp(80.0, 80.0, 80.0, 0.0, 0.0),
                    sampling_stopped=ClockStamp(87.0, 87.0, 87.0, 0.0, 0.0),
                )
        self.assertTrue(resolver.call_args_list)
        self.assertEqual(
            {args.args[0] for args in resolver.call_args_list},
            {CLOCK_METHOD_V3},
        )

    def test_arm_readiness_recognizes_the_r5_v3_acceptance_generation(self) -> None:
        from joulewise.arm_readiness import _issued_d079

        policy = {
            "selection": "issued_d116_artifact_only",
            "issued": "d079_calibration_acceptance_v2_n17_r5",
        }
        self.assertTrue(_issued_d079({"acceptance_policy": policy}))
        self.assertFalse(
            _issued_d079(
                {
                    "acceptance_policy": {
                        **policy,
                        "issued": "d079_calibration_acceptance_v2_n17_r6",
                    }
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
