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


if __name__ == "__main__":
    unittest.main()
