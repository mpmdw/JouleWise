from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import joulewise.window_duration_margins as margins
from joulewise.adapters.powermetrics import samples_from_raw_powermetrics
from joulewise.authentication_io import read_authentication_input
from joulewise.bundle_read import BundleReader
from joulewise.reduce import _in_window_sample_count, _window_gap_stats
from joulewise.whole_window import MAX_BRACKET_CONSUMPTION_SEMANTICS_ID


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "powermetrics_sample.plist"
CONFIG_FIXTURE = (
    REPO_ROOT
    / "configs"
    / "campaigns"
    / "d117_contrast_qwen25_1p5b_vs_7b_v1"
    / "01_decode_contrast_blocks_01_05"
    / "d117c15v7-decode-contrast-b01-a1.json"
)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class WindowDurationMarginsTests(unittest.TestCase):
    PACK_ID = "plan-synthetic-two-cell-pack-v1"
    BASIS_SHA = "b" * 64

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository_root = self.root / "repository"
        self.pack_root = self.repository_root / "pack"
        self.runs_root = self.root / "runs"
        self.receipt_root = self.root / "receipts"
        self.repository_root.mkdir()
        self.pack_root.mkdir()
        self.runs_root.mkdir()
        self.bundle_ids = {
            "decode": [f"synthetic-decode-{index}" for index in range(1, 5)],
            "prefill": [f"synthetic-prefill-p256-{index}" for index in range(1, 5)],
        }
        self.config_sha_by_id: dict[str, str] = {}
        for phase, bundle_ids in self.bundle_ids.items():
            for index, bundle_id in enumerate(bundle_ids, start=1):
                self._make_bundle(
                    bundle_id,
                    phase=phase,
                    start_s=99.0,
                    end_s=103.0 + 0.1 * index,
                )
        self._write_pack()
        occurrences = [
            {"bundle_id": bundle_id}
            for bundle_id in sorted(self.config_sha_by_id)
        ]
        _write_jsonl(
            self.runs_root / "campaign_log.jsonl",
            [
                {
                    "record_type": "idle_admission_whole_window_verdict",
                    "evaluation_basis": {
                        "sha256": self.BASIS_SHA,
                        "consumption_semantics_id": (
                            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
                        ),
                        "member_occurrences": occurrences,
                    },
                }
            ],
        )

    def _make_bundle(
        self,
        bundle_id: str,
        *,
        phase: str,
        start_s: float,
        end_s: float,
    ) -> None:
        bundle = self.runs_root / bundle_id
        raw_dir = bundle / "raw"
        raw_dir.mkdir(parents=True)
        config = json.loads(CONFIG_FIXTURE.read_text(encoding="utf-8"))
        config["run_id"] = bundle_id
        config_raw = _json_bytes(config)
        (bundle / "config.json").write_bytes(config_raw)
        self.config_sha_by_id[bundle_id] = hashlib.sha256(config_raw).hexdigest()
        metadata = {
            "device": {
                "rail_manifest": ["cpu_power", "gpu_power", "ane_power"]
            },
            "uncertainty_evidence": {
                "clock_anchor": {
                    "status": "bounded",
                    "first_sample_end_point_epoch_s": 100.0,
                }
            },
        }
        _write_json(bundle / "metadata.json", metadata)
        os.link(RAW_FIXTURE, raw_dir / "powermetrics.plist")
        samples = samples_from_raw_powermetrics(
            RAW_FIXTURE.read_bytes(), first_record_endpoint_s=100.0
        )
        with (bundle / "power_trace.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(
                [
                    "timestamp_s",
                    "power_w",
                    "source",
                    "rail",
                    "interval_start_s",
                    "interval_end_s",
                ]
            )
            for sample in samples:
                writer.writerow(
                    [
                        sample.timestamp_s,
                        sample.power_w,
                        sample.source,
                        sample.rail,
                        sample.interval_start_s,
                        sample.interval_end_s,
                    ]
                )
        _write_jsonl(
            bundle / "events.jsonl",
            [
                {
                    "timestamp_s": start_s,
                    "event_type": "phase_start",
                    "phase": phase,
                    "message": f"{phase} started",
                    "metadata": {},
                },
                {
                    "timestamp_s": end_s,
                    "event_type": "phase_end",
                    "phase": phase,
                    "message": f"{phase} completed",
                    "metadata": {},
                },
            ],
        )
        reader = BundleReader(bundle)
        window = reader.phase_windows()[phase][0]
        curve = reader.summed_curve()
        cadence = _window_gap_stats(curve, window)["cadence_ratio"]
        self.assertIsNotNone(cadence)
        _write_json(
            bundle / "summary_metrics.json",
            {
                "window_evidence_precheck": {
                    "phase": {
                        phase: {
                            "window_count": 1,
                            "windows": [
                                {
                                    "window_duration_s": window.duration_s,
                                    "in_window_sample_count": _in_window_sample_count(
                                        curve, window
                                    ),
                                    "cadence_ratio": cadence,
                                    "cadence_ratio_min": 2.0,
                                }
                            ],
                        }
                    }
                }
            },
        )

    def _manifest(self) -> dict[str, object]:
        contrasts: list[dict[str, object]] = []
        for cell_id, phase in (
            ("cell-decode", "decode"),
            ("cell-prefill-p256", "prefill"),
        ):
            contrasts.append(
                {
                    "contrast_id": cell_id,
                    "measurement_arm": (
                        "decode" if phase == "decode" else "prefill_p256"
                    ),
                    "metric": f"phase_energy_j.{phase}",
                    "members": [
                        {
                            "run_id": bundle_id,
                            "config_sha256": self.config_sha_by_id[bundle_id],
                        }
                        for bundle_id in self.bundle_ids[phase]
                    ],
                }
            )
        return {
            "schema_version": "joulewise.analysis_manifest.v3.prospective",
            "plan": {"plan_id": self.PACK_ID, "sha256": "a" * 64},
            "contrasts": contrasts,
        }

    def _write_pack(self, manifest: dict[str, object] | None = None) -> None:
        manifest = self._manifest() if manifest is None else manifest
        manifest_raw = _json_bytes(manifest)
        (self.pack_root / "analysis_manifest_v3.json").write_bytes(manifest_raw)
        tree = {
            "schema_version": "joulewise.d117_plan_tree.v1",
            "plan": {"plan_id": self.PACK_ID, "actual_sha256": "a" * 64},
            "window_identity": {"window_id": self.PACK_ID},
            "downstream_contract": {
                "analysis_manifest_path": "analysis_manifest_v3.json",
                "analysis_manifest_sha256": hashlib.sha256(
                    manifest_raw
                ).hexdigest(),
            },
        }
        tree_raw = _json_bytes(tree)
        (self.pack_root / "plan_tree.json").write_bytes(tree_raw)
        (self.pack_root / "plan_tree.sha256").write_text(
            f"{hashlib.sha256(tree_raw).hexdigest()}  plan_tree.json\n",
            encoding="utf-8",
        )

    @contextmanager
    def _authenticated(self, *, bound: float | None = 0.25, refusals: tuple[str, ...] = ()):
        class FakeConsumptionSession:
            def __init__(
                fake_self,
                runs_root: Path,
                referenced_bundle_ids: set[str],
                **_kwargs: object,
            ) -> None:
                fake_self.runs_root = Path(runs_root)
                fake_self.referenced_bundle_ids = frozenset(referenced_bundle_ids)
                fake_self.ready = False
                fake_self.refusal_reasons: tuple[str, ...] = ()
                fake_self.operative_fiducial_bound_s: float | None = None
                fake_self.summaries: dict[str, object] = {}

            def summary_for(fake_self, bundle_id: str) -> object:
                return fake_self.summaries.get(bundle_id)

        def fake_refusals(
            runs_root: Path,
            referenced_bundle_ids: set[str],
            *,
            consumption_session: FakeConsumptionSession,
            **_kwargs: object,
        ) -> tuple[str, ...]:
            self.assertEqual(Path(runs_root), consumption_session.runs_root)
            self.assertEqual(
                frozenset(referenced_bundle_ids),
                consumption_session.referenced_bundle_ids,
            )
            if refusals:
                consumption_session.refusal_reasons = refusals
                return refusals
            consumption_session.operative_fiducial_bound_s = bound
            consumption_session.summaries = {
                bundle_id: json.loads(
                    read_authentication_input(
                        self.runs_root / bundle_id / "summary_metrics.json",
                        grammar="json",
                        label=f"fake authenticated summary {bundle_id}",
                    ).decode("utf-8")
                )
                for bundle_id in referenced_bundle_ids
            }
            consumption_session.ready = True
            return ()

        with mock.patch.object(
            margins, "AuthenticatedConsumptionSession", FakeConsumptionSession
        ), mock.patch.object(
            margins, "whole_window_refusal_reasons", fake_refusals
        ):
            yield

    def _derive(self, *, bound: float | None = 0.25) -> dict[str, object]:
        with self._authenticated(bound=bound):
            return margins.derive_window_duration_margins(
                repository_root=self.repository_root,
                pack_root=self.pack_root,
                runs_root=self.runs_root,
                pack_identity=self.PACK_ID,
            )

    def _output_path(self) -> Path:
        return margins.deterministic_window_duration_margins_path(
            self.receipt_root,
            pack_identity=self.PACK_ID,
            evaluation_basis_sha256=self.BASIS_SHA,
        )

    def _assert_record_refuses(
        self,
        expected_reason: str,
        *,
        bound: float | None = 0.25,
        refusals: tuple[str, ...] = (),
    ) -> None:
        with self._authenticated(bound=bound, refusals=refusals):
            with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                margins.record_window_duration_margins(
                    repository_root=self.repository_root,
                    pack_root=self.pack_root,
                    runs_root=self.runs_root,
                    receipt_root=self.receipt_root,
                    pack_identity=self.PACK_ID,
                )
        self.assertEqual(caught.exception.reason, expected_reason)
        self.assertFalse(self._output_path().exists())

    def test_census_discovers_two_cells_including_p256_shape(self) -> None:
        receipt = self._derive()
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(
            [cell["cell_id"] for cell in receipt["cells"]],
            ["cell-decode", "cell-prefill-p256"],
        )
        self.assertEqual([cell["member_count"] for cell in receipt["cells"]], [4, 4])
        sources = {row["source"] for row in receipt["authoritative_inputs"]}
        for bundle_id in self.config_sha_by_id:
            for relative in (
                "config.json",
                "events.jsonl",
                "metadata.json",
                "power_trace.csv",
                "raw/powermetrics.plist",
                "summary_metrics.json",
            ):
                self.assertIn(f"runs:{bundle_id}/{relative}", sources)
        self.assertTrue(
            {
                "pack:analysis_manifest_v3.json",
                "pack:plan_tree.json",
                "pack:plan_tree.sha256",
                "runs:campaign_log.jsonl",
            }.issubset(sources)
        )
        margins.validate_window_duration_margins_receipt(receipt)

    def test_tampered_events_refuses_without_output(self) -> None:
        bundle = self.runs_root / self.bundle_ids["decode"][0]
        rows = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        rows[1]["timestamp_s"] -= 0.25
        _write_jsonl(bundle / "events.jsonl", rows)
        self._assert_record_refuses("summary_precheck_mismatch")

    def test_tampered_power_trace_refuses_without_output(self) -> None:
        trace = self.runs_root / self.bundle_ids["decode"][0] / "power_trace.csv"
        rows = trace.read_text(encoding="utf-8").splitlines()
        fields = rows[1].split(",")
        fields[1] = str(float(fields[1]) + 1.0)
        rows[1] = ",".join(fields)
        trace.write_text("\n".join(rows) + "\n", encoding="utf-8")
        self._assert_record_refuses("raw_to_trace_replay_failed")

    def test_missing_member_refuses_without_output(self) -> None:
        shutil.rmtree(self.runs_root / self.bundle_ids["decode"][0])
        self._assert_record_refuses("member_missing")

    def test_duplicate_registered_member_refuses_without_output(self) -> None:
        manifest = self._manifest()
        members = manifest["contrasts"][0]["members"]
        members[1] = copy.deepcopy(members[0])
        self._write_pack(manifest)
        self._assert_record_refuses("member_non_unique")

    def test_duplicate_present_member_refuses_without_output(self) -> None:
        bundle_id = self.bundle_ids["decode"][0]
        duplicate = self.runs_root / "moved-duplicate"
        shutil.copytree(self.runs_root / bundle_id, duplicate)
        self._assert_record_refuses("member_non_unique")

    def test_non_unique_phase_boundaries_refuse_without_output(self) -> None:
        bundle = self.runs_root / self.bundle_ids["decode"][0]
        rows = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        rows.extend(
            [
                {
                    "timestamp_s": 104.2,
                    "event_type": "phase_start",
                    "phase": "decode",
                    "message": "second decode started",
                    "metadata": {},
                },
                {
                    "timestamp_s": 104.4,
                    "event_type": "phase_end",
                    "phase": "decode",
                    "message": "second decode completed",
                    "metadata": {},
                },
            ]
        )
        _write_jsonl(bundle / "events.jsonl", rows)
        self._assert_record_refuses("phase_window_non_unique")

    def test_unknown_b_operative_refuses_without_output(self) -> None:
        self._assert_record_refuses(
            "authenticated_b_operative_unavailable", bound=None
        )

    def test_unavailable_b_operative_refuses_without_output(self) -> None:
        self._assert_record_refuses(
            "authenticated_b_operative_unavailable",
            refusals=("instrument_calibration_invalid",),
        )

    def test_nonfinite_arithmetic_refuses_without_output(self) -> None:
        self._assert_record_refuses("nonfinite_arithmetic", bound=1e308)

    def test_two_derivations_are_byte_identical(self) -> None:
        first = margins.render_window_duration_margins_receipt(self._derive())
        second = margins.render_window_duration_margins_receipt(self._derive())
        self.assertEqual(first, second)

    def test_record_is_deterministic_and_idempotent(self) -> None:
        with self._authenticated():
            first = margins.record_window_duration_margins(
                repository_root=self.repository_root,
                pack_root=self.pack_root,
                runs_root=self.runs_root,
                receipt_root=self.receipt_root,
                pack_identity=self.PACK_ID,
            )
        first_bytes = first.path.read_bytes()
        with self._authenticated():
            second = margins.record_window_duration_margins(
                repository_root=self.repository_root,
                pack_root=self.pack_root,
                runs_root=self.runs_root,
                receipt_root=self.receipt_root,
                pack_identity=self.PACK_ID,
            )
        self.assertEqual(first.path, second.path)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first_bytes, second.path.read_bytes())

    def test_negative_margin_is_still_pass(self) -> None:
        receipt = self._derive(bound=3.0)
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(
            all(
                cell["min_duration_minus_2b_operative_s"] < 0.0
                for cell in receipt["cells"]
            )
        )

    def test_closed_schema_rejects_unknown_keys(self) -> None:
        receipt = self._derive()
        receipt["operator_status"] = "PASS"
        with self.assertRaisesRegex(ValueError, "receipt keys"):
            margins.validate_window_duration_margins_receipt(receipt)

    def test_summary_precheck_is_cross_check_not_copy_source(self) -> None:
        bundle = self.runs_root / self.bundle_ids["prefill"][0]
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["window_evidence_precheck"]["phase"]["prefill"]["windows"][0][
            "cadence_ratio"
        ] += 0.5
        _write_json(bundle / "summary_metrics.json", summary)
        self._assert_record_refuses("summary_precheck_mismatch")


if __name__ == "__main__":
    unittest.main()
