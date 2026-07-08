from __future__ import annotations

import hashlib
import json
import plistlib
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

from joulewise.adapters.powermetrics import (
    RAIL_MANIFEST,
    RAW_SAMPLES_NAME,
    parse_powermetrics_records,
    samples_from_raw_powermetrics,
)
from joulewise.clock import FakeClock
from joulewise.cli import validate_bundle
from joulewise.controller import run_benchmark
from joulewise.provenance import (
    prompt_provenance,
    prompt_token_ids_sha256,
)
from joulewise.schemas import BenchmarkConfig, RunStatus


REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"
POWERMETRICS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "powermetrics_sample.plist"


def _completed(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")


def _minimal_powermetrics_document(*, elapsed_ns: int = 1_000_000_000) -> bytes:
    return plistlib.dumps(
        {
            "timestamp": datetime(2026, 7, 7, 0, 0, 0, tzinfo=timezone.utc),
            "elapsed_ns": elapsed_ns,
            "processor": {
                "cpu_power": 1000.0,
                "gpu_power": 2000.0,
                "ane_power": 3000.0,
                "cpu_energy": 10,
                "gpu_energy": 20,
                "ane_energy": 30,
            },
        }
    )


class StrictGateInteractionAmplification(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.runs_dir = self.tmp / "runs"

    def _write_config(self, run_id: str, *, powermetrics: bool = False) -> Path:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        if powermetrics:
            data["hardware_target"]["telemetry_backend"] = "powermetrics"
            data["workload_profile"]["output_tokens"] = 300
            data["sampling"] = {"power_hz": 2.0, "idle_seconds": 5.0}
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data))
        return path

    def _mock_bundle(self, run_id: str) -> Path:
        config = BenchmarkConfig.from_mapping(
            json.loads(self._write_config(run_id).read_text())
        )
        bundle, summary = run_benchmark(config, self.runs_dir, FakeClock())
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        return bundle

    def _powermetrics_bundle(self, run_id: str) -> Path:
        fixture = POWERMETRICS_FIXTURE.read_bytes()
        config = BenchmarkConfig.from_mapping(
            json.loads(self._write_config(run_id, powermetrics=True).read_text())
        )

        def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
            if "-o" in command:
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return _completed(command)

        class FakePopen:
            def __init__(self, command: list[str], **kwargs: Any) -> None:
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(fixture)
                self.returncode: Optional[int] = None

            def poll(self) -> Optional[int]:
                return self.returncode

            def terminate(self) -> None:
                self.returncode = 0

            def kill(self) -> None:
                self.returncode = -9

            def communicate(self, timeout: Optional[float] = None) -> tuple[bytes, bytes]:
                self.returncode = 0
                return b"", b""

        with patch(
            "joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run
        ), patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen):
            bundle, summary = run_benchmark(
                config,
                self.runs_dir,
                FakeClock(start=1_783_394_100.0),
            )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        return bundle

    def _rewrite_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def _trace_rows(self, bundle: Path) -> list[list[str]]:
        return [
            line.split(",")
            for line in (bundle / "power_trace.csv").read_text().splitlines()
        ]

    def _write_trace_rows(self, bundle: Path, rows: list[list[str]]) -> None:
        (bundle / "power_trace.csv").write_text(
            "".join(",".join(row) + "\n" for row in rows)
        )

    def test_legacy_summary_marker_allows_missing_workload_provenance(self) -> None:
        bundle = self._mock_bundle("amp-legacy-provenance")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary.pop("summary_provenance")
        self._rewrite_json(bundle / "summary_metrics.json", summary)
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.pop("workload_provenance")
        self._rewrite_json(bundle / "metadata.json", metadata)

        self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_legacy_summary_tolerance_does_not_hide_raw_to_trace_order_drift(self) -> None:
        bundle = self._powermetrics_bundle("amp-pm-legacy-order")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary.pop("summary_provenance")
        summary.pop("uncertainty")
        self._rewrite_json(bundle / "summary_metrics.json", summary)

        rows = self._trace_rows(bundle)
        self.assertEqual(rows[1][3], "cpu_power")
        self.assertEqual(rows[2][3], "gpu_power")
        rows[1], rows[2] = rows[2], rows[1]
        self._write_trace_rows(bundle, rows)

        problems = validate_bundle(bundle, strict=True)
        raw_problem = next((p for p in problems if "strict: raw-to-trace:" in p), None)
        self.assertIsNotNone(raw_problem, problems)
        assert raw_problem is not None
        self.assertIn("row 2", raw_problem)
        self.assertIn("rail", raw_problem)

    def test_raw_to_trace_rejects_sub_epsilon_numeric_drift(self) -> None:
        bundle = self._powermetrics_bundle("amp-pm-tiny-drift")
        rows = self._trace_rows(bundle)
        rows[1][1] = repr(float(rows[1][1]) + 1e-12)
        self._write_trace_rows(bundle, rows)

        problems = validate_bundle(bundle, strict=True)
        raw_problem = next((p for p in problems if "strict: raw-to-trace:" in p), None)
        self.assertIsNotNone(raw_problem, problems)
        assert raw_problem is not None
        self.assertIn("power_w", raw_problem)


class ProvenanceHashAmplification(unittest.TestCase):
    def test_prompt_token_hash_uses_domain_and_compact_canonical_json(self) -> None:
        token_ids = [0, 2**63, 17, 2**31 + 123]
        canonical = json.dumps(token_ids, separators=(",", ":"), sort_keys=True)
        expected = hashlib.sha256(
            ("joulewise.prompt_token_ids.v1" + "\0" + canonical).encode("utf-8")
        ).hexdigest()

        self.assertEqual(prompt_token_ids_sha256(token_ids), expected)
        self.assertNotEqual(
            prompt_token_ids_sha256(token_ids),
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def test_prompt_text_hash_is_utf8_supplemental_and_null_when_absent(self) -> None:
        token_ids = [7, 11, 13]
        text = "cafe\u0301 snowman \u2603"
        with_text = prompt_provenance(token_ids, text=text)
        without_text = prompt_provenance(token_ids, text=None)

        self.assertEqual(with_text["token_ids_sha256"], without_text["token_ids_sha256"])
        self.assertEqual(
            with_text["text_sha256"],
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )
        self.assertIsNone(without_text["text_sha256"])


class PowermetricsDegenerateAmplification(unittest.TestCase):
    def test_one_complete_frame_with_truncated_tail_derives_manifest_samples(self) -> None:
        stream = _minimal_powermetrics_document() + b"\0<plist"
        samples = samples_from_raw_powermetrics(stream, plist_anchor_offset_s=0.25)

        self.assertEqual([sample.rail for sample in samples], list(RAIL_MANIFEST))
        self.assertEqual([sample.power_w for sample in samples], [1.0, 2.0, 3.0])
        self.assertEqual({sample.source for sample in samples}, {"powermetrics"})
        self.assertEqual(
            {sample.timestamp_s for sample in samples},
            {datetime(2026, 7, 7, 0, 0, 0, tzinfo=timezone.utc).timestamp() + 0.75},
        )

    def test_zero_complete_frames_still_rejects_all_frames_dropped_tail(self) -> None:
        with self.assertRaisesRegex(ValueError, "document 0"):
            parse_powermetrics_records(b"<plist")
        with self.assertRaisesRegex(ValueError, "no complete plist documents"):
            samples_from_raw_powermetrics(b"\0\0", plist_anchor_offset_s=0.0)


if __name__ == "__main__":
    unittest.main()
