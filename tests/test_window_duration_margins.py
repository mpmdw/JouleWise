from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import joulewise.window_duration_margins as margins
from joulewise.adapters.powermetrics import samples_from_raw_powermetrics
from joulewise.authentication_io import (
    V2AuthenticationReadSession,
    read_authentication_input,
)
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

FROZEN_FLOOR_PACKS = (
    {
        "model": "1p5b",
        "pack": "d117_floor_qwen25_1p5b_v1",
        "pack_identity": "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1",
        "registry_sha256": "d98ae4deb787caaf8a80f972b88b2c85ecc2f96a13092e9127c1e1a661640fd2",
        "cell_ids": (
            "d117-df-cmp-abba-ph-decode-qwen25-1p5b",
            "d117-df-cmp-abba-ph-prefill-p128-qwen25-1p5b",
            "d117-df-cmp-abba-ph-prefill-p256-qwen25-1p5b",
        ),
    },
    {
        "model": "7b",
        "pack": "d117_floor_qwen25_7b_v1",
        "pack_identity": "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1",
        "registry_sha256": "86809f31d2c6933cda42881e10a32bc521cddec01fa941ac4613cd32b9ef49b8",
        "cell_ids": (
            "d117-df-cmp-abba-ph-decode-qwen25-7b",
            "d117-df-cmp-abba-ph-prefill-p128-qwen25-7b",
            "d117-df-cmp-abba-ph-prefill-p256-qwen25-7b",
        ),
    },
)
GAMMA_PACK = "d117_contrast_qwen25_1p5b_vs_7b_v1"
GAMMA_PACK_ID = "plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1"
GAMMA_REGISTRY_SHA = "e3bc0e3620be2a25c60a6dc7bcab0910997d7d97030f5e80727cd5d951559a57"


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


class FrozenPackRecorderAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def _floor_spec_path(self, model: str, *, root: Path = REPO_ROOT) -> Path:
        return (
            root
            / "configs"
            / "floor_mint"
            / f"d117_qwen25_{model}_extraction_spec.json"
        )

    def _pack_path(self, pack: str, *, root: Path = REPO_ROOT) -> Path:
        return root / "configs" / "campaigns" / pack

    def _copy_floor_pack(self, model: str) -> tuple[Path, Path, Path, dict[str, object]]:
        repository_root = self.root / f"repository-{model}"
        case = next(case for case in FROZEN_FLOOR_PACKS if case["model"] == model)
        source_pack = self._pack_path(str(case["pack"]))
        pack_root = self._pack_path(str(case["pack"]), root=repository_root)
        pack_root.mkdir(parents=True)
        for name in ("plan_tree.json", "plan_tree.sha256"):
            shutil.copy2(source_pack / name, pack_root / name)
        spec_path = self._floor_spec_path(model, root=repository_root)
        spec_path.parent.mkdir(parents=True)
        shutil.copy2(self._floor_spec_path(model), spec_path)
        tree = json.loads((pack_root / "plan_tree.json").read_text(encoding="utf-8"))
        return repository_root, pack_root, spec_path, tree

    def _copy_gamma_pack(self) -> tuple[Path, Path, Path, dict[str, object]]:
        repository_root = self.root / "repository-gamma"
        source_pack = self._pack_path(GAMMA_PACK)
        pack_root = self._pack_path(GAMMA_PACK, root=repository_root)
        pack_root.mkdir(parents=True)
        for name in (
            "plan_tree.json",
            "plan_tree.sha256",
            "analysis_manifest_v3.json",
        ):
            shutil.copy2(source_pack / name, pack_root / name)
        manifest_path = pack_root / "analysis_manifest_v3.json"
        tree = json.loads((pack_root / "plan_tree.json").read_text(encoding="utf-8"))
        return repository_root, pack_root, manifest_path, tree

    def _rewrite_plan_tree(self, pack_root: Path, tree: dict[str, object]) -> None:
        tree_raw = _json_bytes(tree)
        (pack_root / "plan_tree.json").write_bytes(tree_raw)
        (pack_root / "plan_tree.sha256").write_text(
            f"{hashlib.sha256(tree_raw).hexdigest()}  plan_tree.json\n",
            encoding="utf-8",
        )

    def test_frozen_floor_pack_census_and_governed_grant_are_exact(self) -> None:
        for case in FROZEN_FLOOR_PACKS:
            with self.subTest(model=case["model"]):
                pack_root = self._pack_path(str(case["pack"]))
                spec_path = self._floor_spec_path(str(case["model"]))
                with V2AuthenticationReadSession() as authentication:
                    with mock.patch.object(
                        authentication,
                        "allow_governed_extraction_spec",
                        wraps=authentication.allow_governed_extraction_spec,
                    ) as grant:
                        _tree_sha, registry_sha, cells = margins._pack_inventory(
                            authentication,
                            REPO_ROOT,
                            pack_root,
                            str(case["pack_identity"]),
                        )
                grant.assert_called_once_with(spec_path.resolve())
                self.assertEqual(registry_sha, case["registry_sha256"])
                self.assertEqual(
                    tuple(cell.cell_id for cell in cells), case["cell_ids"]
                )
                self.assertEqual(
                    [(cell.metric, len(cell.members)) for cell in cells],
                    [
                        ("phase_energy_j.decode", 40),
                        ("phase_energy_j.prefill", 40),
                        ("phase_energy_j.prefill", 40),
                    ],
                )
                registry = json.loads(spec_path.read_text(encoding="utf-8"))
                comparative = [
                    cell for cell in registry["cells"] if cell.get("kind") == "comparative"
                ]
                self.assertEqual(len(comparative), 3)
                for raw_cell, registered in zip(comparative, cells):
                    self.assertEqual(len(raw_cell["blocks"]), 10)
                    self.assertEqual(len(raw_cell["member_config_sha256"]), 40)
                    self.assertEqual(
                        raw_cell["estimator_registration"]["estimator_id"],
                        "d124_two_shared_edge_common_mode.v1",
                    )
                    expected_members = tuple(
                        block["members"][position]
                        for block in raw_cell["blocks"]
                        for position in ("A1", "B1", "B2", "A2")
                    )
                    self.assertEqual(
                        tuple(bundle_id for bundle_id, _sha in registered.members),
                        expected_members,
                    )
                    self.assertEqual(len(set(expected_members)), 40)

    def test_selected_floor_grant_does_not_authorize_other_pack_spec(self) -> None:
        alpha = FROZEN_FLOOR_PACKS[0]
        beta_path = self._floor_spec_path("7b")
        real_pack_inventory = margins._pack_inventory

        def attempt_other_pack(
            authentication: V2AuthenticationReadSession,
            repository_root: Path,
            pack_root: Path,
            pack_identity: str,
        ) -> object:
            inventory = real_pack_inventory(
                authentication,
                repository_root,
                pack_root,
                pack_identity,
            )
            margins._json_object(beta_path, label="unselected floor spec")
            return inventory

        runs_root = self.root / "other-pack-runs"
        receipt_root = self.root / "other-pack-receipts"
        runs_root.mkdir()
        with mock.patch.object(
            margins, "_pack_inventory", side_effect=attempt_other_pack
        ):
            with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                margins.record_window_duration_margins(
                    repository_root=REPO_ROOT,
                    pack_root=self._pack_path(str(alpha["pack"])),
                    runs_root=runs_root,
                    receipt_root=receipt_root,
                    pack_identity=str(alpha["pack_identity"]),
                )
        self.assertEqual(caught.exception.reason, "authoritative_input_invalid")
        self.assertIn(
            "v2_authentication_forbidden_json_key", caught.exception.detail
        )
        self.assertIn(
            "unselected floor spec.cells[1].estimator_registration",
            caught.exception.detail,
        )
        self.assertFalse(receipt_root.exists())

    def test_tampered_selected_spec_refuses_before_census_processing(self) -> None:
        repository_root, pack_root, spec_path, _tree = self._copy_floor_pack("1p5b")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        comparative = next(
            cell for cell in spec["cells"] if cell.get("kind") == "comparative"
        )
        comparative["estimator_registration"]["status"] = "tampered"
        _write_json(spec_path, spec)
        with V2AuthenticationReadSession() as authentication:
            with mock.patch.object(
                margins,
                "_floor_cells",
                side_effect=AssertionError("census ran before the spec pin check"),
            ), mock.patch.object(
                authentication,
                "allow_governed_extraction_spec",
                wraps=authentication.allow_governed_extraction_spec,
            ) as grant:
                with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                    margins._pack_inventory(
                        authentication,
                        repository_root,
                        pack_root,
                        str(FROZEN_FLOOR_PACKS[0]["pack_identity"]),
                    )
        self.assertEqual(caught.exception.reason, "pack_pin_invalid")
        grant.assert_called_once_with(spec_path.resolve())

    def test_wrong_path_grant_attempt_is_normalized_to_refusal(self) -> None:
        repository_root, pack_root, spec_path, tree = self._copy_floor_pack("1p5b")
        wrong_path = spec_path.with_suffix(".txt")
        shutil.copy2(spec_path, wrong_path)
        extraction = tree["downstream_contract"]["extraction_spec"]
        extraction["path"] = wrong_path.relative_to(repository_root).as_posix()
        extraction["sha256"] = hashlib.sha256(wrong_path.read_bytes()).hexdigest()
        self._rewrite_plan_tree(pack_root, tree)
        with V2AuthenticationReadSession() as authentication:
            with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                margins._pack_inventory(
                    authentication,
                    repository_root,
                    pack_root,
                    str(FROZEN_FLOOR_PACKS[0]["pack_identity"]),
                )
        self.assertEqual(caught.exception.reason, "authoritative_input_invalid")
        self.assertIn("must be a JSON file", caught.exception.detail)

    def test_escaping_floor_spec_path_refuses_before_any_grant(self) -> None:
        repository_root, pack_root, _spec_path, tree = self._copy_floor_pack("1p5b")
        tree["downstream_contract"]["extraction_spec"]["path"] = "../outside.json"
        self._rewrite_plan_tree(pack_root, tree)
        with V2AuthenticationReadSession() as authentication:
            with mock.patch.object(
                authentication,
                "allow_governed_extraction_spec",
                side_effect=AssertionError("escaping path reached the grant"),
            ):
                with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                    margins._pack_inventory(
                        authentication,
                        repository_root,
                        pack_root,
                        str(FROZEN_FLOOR_PACKS[0]["pack_identity"]),
                    )
        self.assertEqual(caught.exception.reason, "pack_pin_invalid")

    def test_real_gamma_census_uses_no_governed_spec_grant(self) -> None:
        pack_root = self._pack_path(GAMMA_PACK)
        with V2AuthenticationReadSession() as authentication:
            with mock.patch.object(
                authentication,
                "allow_governed_extraction_spec",
                side_effect=AssertionError("GAMMA must not receive a governed grant"),
            ) as grant:
                _tree_sha, registry_sha, cells = margins._pack_inventory(
                    authentication,
                    REPO_ROOT,
                    pack_root,
                    GAMMA_PACK_ID,
                )
        grant.assert_not_called()
        self.assertEqual(registry_sha, GAMMA_REGISTRY_SHA)
        self.assertEqual(
            [(cell.cell_id, cell.metric, len(cell.members)) for cell in cells],
            [
                ("ctr-d117-decode-qwen25-1p5b-vs-7b", "phase_energy_j.decode", 40),
                (
                    "ctr-d117-prefill-p256-qwen25-1p5b-vs-7b",
                    "phase_energy_j.prefill",
                    40,
                ),
            ],
        )

    def test_frozen_floor_census_truncation_refuses(self) -> None:
        case = FROZEN_FLOOR_PACKS[0]
        real_floor_cells = margins._floor_cells

        def truncate_to_two(registry: object) -> object:
            return real_floor_cells(registry)[:2]

        with V2AuthenticationReadSession() as authentication:
            with mock.patch.object(
                margins, "_floor_cells", side_effect=truncate_to_two
            ):
                with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                    margins._pack_inventory(
                        authentication,
                        REPO_ROOT,
                        self._pack_path(str(case["pack"])),
                        str(case["pack_identity"]),
                    )
        self.assertEqual(caught.exception.reason, "registered_cell_inventory_invalid")

    def test_frozen_gamma_census_truncation_refuses(self) -> None:
        real_gamma_cells = margins._gamma_cells

        def truncate_to_one(manifest: object) -> object:
            return real_gamma_cells(manifest)[:1]

        with V2AuthenticationReadSession() as authentication:
            with mock.patch.object(
                margins, "_gamma_cells", side_effect=truncate_to_one
            ):
                with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                    margins._pack_inventory(
                        authentication,
                        REPO_ROOT,
                        self._pack_path(GAMMA_PACK),
                        GAMMA_PACK_ID,
                    )
        self.assertEqual(caught.exception.reason, "registered_cell_inventory_invalid")

    def test_gamma_estimator_registration_refuses_publicly_without_receipt(self) -> None:
        repository_root, pack_root, manifest_path, tree = self._copy_gamma_pack()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["contrasts"][0]["estimator_registration"] = {"forged": True}
        manifest_raw = _json_bytes(manifest)
        manifest_path.write_bytes(manifest_raw)
        tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
            manifest_raw
        ).hexdigest()
        self._rewrite_plan_tree(pack_root, tree)
        runs_root = self.root / "gamma-runs"
        receipt_root = self.root / "gamma-receipts"
        runs_root.mkdir()
        with mock.patch.object(
            V2AuthenticationReadSession,
            "allow_governed_extraction_spec",
            side_effect=AssertionError("GAMMA must not receive a governed grant"),
        ):
            with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                margins.record_window_duration_margins(
                    repository_root=repository_root,
                    pack_root=pack_root,
                    runs_root=runs_root,
                    receipt_root=receipt_root,
                    pack_identity=GAMMA_PACK_ID,
                )
        self.assertEqual(caught.exception.reason, "authoritative_input_invalid")
        self.assertIn("v2_authentication_forbidden_json_key", caught.exception.detail)
        self.assertIn(
            "contrasts[0].estimator_registration", caught.exception.detail
        )
        self.assertFalse(receipt_root.exists())


class WindowDurationMarginsTests(unittest.TestCase):
    PACK_ID = "plan-synthetic-three-cell-floor-pack-v1"
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
            "prefill_p128": [
                f"synthetic-prefill-p128-{index}" for index in range(1, 5)
            ],
            "prefill_p256": [
                f"synthetic-prefill-p256-{index}" for index in range(1, 5)
            ],
        }
        self.config_sha_by_id: dict[str, str] = {}
        for arm, bundle_ids in self.bundle_ids.items():
            phase = "decode" if arm == "decode" else "prefill"
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

    def _registry(self) -> dict[str, object]:
        cells: list[dict[str, object]] = []
        for cell_id, arm, phase in (
            ("cell-decode", "decode", "decode"),
            ("cell-prefill-p128", "prefill_p128", "prefill"),
            ("cell-prefill-p256", "prefill_p256", "prefill"),
        ):
            # This four-member fixture exists only to keep receipt arithmetic
            # and publication tests small. Frozen-pack tests above own every
            # claim about the production census and governed vocabulary.
            cells.append(
                {
                    "cell_id": f"{cell_id}-absolute",
                    "kind": "absolute",
                    "metric": f"phase_energy_j.{phase}",
                }
            )
            members = self.bundle_ids[arm]
            cells.append(
                {
                    "cell_id": cell_id,
                    "kind": "comparative",
                    "metric": f"phase_energy_j.{phase}",
                    "member_config_sha256": [
                        {
                            "bundle_id": bundle_id,
                            "config_sha256": self.config_sha_by_id[bundle_id],
                        }
                        for bundle_id in members
                    ],
                    "blocks": [
                        {
                            "block_id": f"{cell_id}-b01",
                            "members": dict(zip(("A1", "B1", "B2", "A2"), members)),
                        }
                    ],
                }
            )
        return {
            "schema_version": "joulewise.detection_floor_extraction_spec.v1",
            "cells": cells,
        }

    def _write_pack(self, registry: dict[str, object] | None = None) -> None:
        registry = self._registry() if registry is None else registry
        registry_raw = _json_bytes(registry)
        (self.repository_root / "extraction_spec.json").write_bytes(registry_raw)
        tree = {
            "schema_version": "joulewise.d117_plan_tree.v1",
            "plan": {"plan_id": self.PACK_ID, "actual_sha256": "a" * 64},
            "window_identity": {"window_id": self.PACK_ID},
            "downstream_contract": {
                "extraction_spec": {
                    "path": "extraction_spec.json",
                    "sha256": hashlib.sha256(registry_raw).hexdigest(),
                },
            },
        }
        tree_raw = _json_bytes(tree)
        (self.pack_root / "plan_tree.json").write_bytes(tree_raw)
        (self.pack_root / "plan_tree.sha256").write_text(
            f"{hashlib.sha256(tree_raw).hexdigest()}  plan_tree.json\n",
            encoding="utf-8",
        )

    def _cli_environment(self) -> dict[str, str]:
        shim_root = self.root / "process-shim"
        shim_root.mkdir(exist_ok=True)
        (shim_root / "sitecustomize.py").write_text(
            textwrap.dedent(
                """
                import json
                import os
                from pathlib import Path

                import joulewise.window_duration_margins as margins
                from joulewise.authentication_io import read_authentication_input

                class FakeConsumptionSession:
                    def __init__(self, runs_root, referenced_bundle_ids, **_kwargs):
                        self.runs_root = Path(runs_root)
                        self.referenced_bundle_ids = frozenset(referenced_bundle_ids)
                        self.ready = False
                        self.refusal_reasons = ()
                        self.operative_fiducial_bound_s = None
                        self.summaries = {}

                    def summary_for(self, bundle_id):
                        return self.summaries.get(bundle_id)

                def fake_refusals(runs_root, referenced_bundle_ids, *, consumption_session, **_kwargs):
                    consumption_session.operative_fiducial_bound_s = float(
                        os.environ.get("WINDOW_MARGIN_TEST_BOUND", "0.25")
                    )
                    consumption_session.summaries = {
                        bundle_id: json.loads(
                            read_authentication_input(
                                Path(runs_root) / bundle_id / "summary_metrics.json",
                                grammar="json",
                                label=f"fake authenticated summary {bundle_id}",
                            ).decode("utf-8")
                        )
                        for bundle_id in referenced_bundle_ids
                    }
                    consumption_session.ready = True
                    return ()

                margins.AuthenticatedConsumptionSession = FakeConsumptionSession
                margins.whole_window_refusal_reasons = fake_refusals
                """
            ),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        python_path = [str(shim_root), str(REPO_ROOT)]
        if environment.get("PYTHONPATH"):
            python_path.append(environment["PYTHONPATH"])
        environment["PYTHONPATH"] = os.pathsep.join(python_path)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return environment

    def _cli_command(self, receipt_root: Path) -> list[str]:
        return [
            sys.executable,
            str(REPO_ROOT / "scripts" / "record_window_duration_margins.py"),
            "--repository-root",
            str(self.repository_root),
            "--pack-root",
            str(self.pack_root),
            "--runs-root",
            str(self.runs_root),
            "--receipt-root",
            str(receipt_root),
            "--pack-identity",
            self.PACK_ID,
        ]

    @contextmanager
    def _authenticated(self, *, bound: float | None = 0.25, refusals: tuple[str, ...] = ()):
        # Only the production whole-window verdict validator and calibration-
        # ledger-backed B_operative derivation are mocked.  Pack/registry
        # authentication, bundle discovery, config pins, raw-to-trace replay,
        # event-window derivation, summary cross-checking, receipt validation,
        # and publication remain real.  This is safe for these focused receipt
        # tests because the mocked layers have their own end-to-end suites; the
        # fixture controls their two outputs (ready/refusal and authenticated
        # bound) without replacing any arithmetic audited in this module.
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

    def _namespace_inventory(self) -> list[tuple[str, str]]:
        namespace = self.receipt_root / margins.RECEIPT_NAMESPACE
        if not namespace.exists():
            return []
        return sorted(
            (
                path.relative_to(namespace).as_posix(),
                "directory" if path.is_dir() else "file",
            )
            for path in namespace.rglob("*")
        )

    def _assert_record_refuses(
        self,
        expected_reason: str,
        *,
        bound: float | None = 0.25,
        refusals: tuple[str, ...] = (),
        repository_root: Path | None = None,
        pack_identity: str | None = None,
    ) -> None:
        before = self._namespace_inventory()
        with self._authenticated(bound=bound, refusals=refusals):
            with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                margins.record_window_duration_margins(
                    repository_root=(
                        self.repository_root
                        if repository_root is None
                        else repository_root
                    ),
                    pack_root=self.pack_root,
                    runs_root=self.runs_root,
                    receipt_root=self.receipt_root,
                    pack_identity=(
                        self.PACK_ID if pack_identity is None else pack_identity
                    ),
                )
        self.assertEqual(caught.exception.reason, expected_reason)
        self.assertEqual(self._namespace_inventory(), before)

    def test_synthetic_arithmetic_fixture_derives_three_cells(self) -> None:
        receipt = self._derive()
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(
            [cell["cell_id"] for cell in receipt["cells"]],
            ["cell-decode", "cell-prefill-p128", "cell-prefill-p256"],
        )
        self.assertEqual(
            [cell["member_count"] for cell in receipt["cells"]], [4, 4, 4]
        )
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
                "pack:plan_tree.json",
                "pack:plan_tree.sha256",
                "repository:extraction_spec.json",
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
        registry = self._registry()
        comparative = next(
            cell for cell in registry["cells"] if cell.get("kind") == "comparative"
        )
        members = comparative["blocks"][0]["members"]
        members["B1"] = members["A1"]
        self._write_pack(registry)
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

    def test_authoritative_input_invalid_refuses_without_output(self) -> None:
        self._assert_record_refuses(
            "authoritative_input_invalid",
            repository_root=self.root / "missing-repository-root",
        )

    def test_member_config_mismatch_refuses_without_output(self) -> None:
        config_path = (
            self.runs_root / self.bundle_ids["decode"][0] / "config.json"
        )
        config_path.write_bytes(config_path.read_bytes() + b" ")
        self._assert_record_refuses("member_config_mismatch")

    def test_pack_identity_invalid_refuses_without_output(self) -> None:
        self._assert_record_refuses(
            "pack_identity_invalid", pack_identity="../namespace-escape"
        )

    def test_pack_pin_invalid_refuses_without_output(self) -> None:
        (self.pack_root / "plan_tree.sha256").write_text(
            f"{'0' * 64}  plan_tree.json\n", encoding="utf-8"
        )
        self._assert_record_refuses("pack_pin_invalid")

    def test_registered_membership_invalid_refuses_without_output(self) -> None:
        registry = self._registry()
        comparative = next(
            cell for cell in registry["cells"] if cell.get("kind") == "comparative"
        )
        comparative["member_config_sha256"].pop()
        self._write_pack(registry)
        self._assert_record_refuses("registered_membership_invalid")

    def test_unrecordable_minimum_refuses_without_output(self) -> None:
        self._assert_record_refuses("unrecordable_minimum", bound=0.0)

    def test_two_derivations_are_byte_identical(self) -> None:
        first = margins.render_window_duration_margins_receipt(self._derive())
        second = margins.render_window_duration_margins_receipt(self._derive())
        self.assertEqual(first, second)

    def test_second_record_call_refuses_and_preserves_first_receipt_bytes(self) -> None:
        with self._authenticated():
            first = margins.record_window_duration_margins(
                repository_root=self.repository_root,
                pack_root=self.pack_root,
                runs_root=self.runs_root,
                receipt_root=self.receipt_root,
                pack_identity=self.PACK_ID,
            )
        first_bytes = first.path.read_bytes()
        first_sha = hashlib.sha256(first_bytes).hexdigest()
        before = self._namespace_inventory()
        with self._authenticated():
            with self.assertRaises(margins.WindowDurationMarginsRefusal) as caught:
                margins.record_window_duration_margins(
                    repository_root=self.repository_root,
                    pack_root=self.pack_root,
                    runs_root=self.runs_root,
                    receipt_root=self.receipt_root,
                    pack_identity=self.PACK_ID,
                )
        self.assertEqual(caught.exception.reason, "receipt_namespace_conflict")
        self.assertEqual(hashlib.sha256(first.path.read_bytes()).hexdigest(), first_sha)
        self.assertEqual(first.path.read_bytes(), first_bytes)
        self.assertEqual(self._namespace_inventory(), before)

    def test_recorder_cli_is_deterministic_across_independent_processes(self) -> None:
        environment = self._cli_environment()
        receipt_paths: list[Path] = []
        for suffix in ("a", "b"):
            receipt_root = self.root / f"cli-receipts-{suffix}"
            completed = subprocess.run(
                self._cli_command(receipt_root),
                cwd=REPO_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "PASS")
            receipt_paths.append(Path(result["receipt_path"]))
        self.assertEqual(receipt_paths[0].read_bytes(), receipt_paths[1].read_bytes())

    def test_recorder_cli_refuses_republication_in_same_namespace(self) -> None:
        environment = self._cli_environment()
        command = self._cli_command(self.receipt_root)

        first = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(first.returncode, 0, first.stderr or first.stdout)
        first_result = json.loads(first.stdout)
        self.assertEqual(first_result["status"], "PASS")
        receipt_path = Path(first_result["receipt_path"])
        first_bytes = receipt_path.read_bytes()
        first_sha = hashlib.sha256(first_bytes).hexdigest()
        self.assertEqual(first_result["receipt_sha256"], first_sha)
        inventory = self._namespace_inventory()

        identical = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(identical.returncode, 2, identical.stderr)
        identical_result = json.loads(identical.stdout)
        self.assertEqual(identical_result["status"], "REFUSE")
        self.assertEqual(
            identical_result["reason"], "receipt_namespace_conflict"
        )
        self.assertEqual(self._namespace_inventory(), inventory)
        self.assertEqual(hashlib.sha256(receipt_path.read_bytes()).hexdigest(), first_sha)

        differing_bytes = margins.render_window_duration_margins_receipt(
            self._derive(bound=0.5)
        )
        self.assertNotEqual(differing_bytes, first_bytes)
        differing_environment = environment.copy()
        differing_environment["WINDOW_MARGIN_TEST_BOUND"] = "0.5"
        differing = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=differing_environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(differing.returncode, 2, differing.stderr)
        differing_result = json.loads(differing.stdout)
        self.assertEqual(differing_result["status"], "REFUSE")
        self.assertEqual(
            differing_result["reason"], "receipt_namespace_conflict"
        )
        self.assertEqual(self._namespace_inventory(), inventory)
        self.assertEqual(hashlib.sha256(receipt_path.read_bytes()).hexdigest(), first_sha)

    def test_hand_computed_numeric_oracle(self) -> None:
        receipt = self._derive(bound=0.25)
        for cell in receipt["cells"]:
            # The fixture has five explicitly enumerated interval supports
            # overlapping every [99.0, 103.1+] window.  MIN_PHASE_SAMPLES is
            # three, so the literal count margin is 5 - 3 = 2.  The shortest
            # window is 103.1 - 99.0 = 4.1 s; 2B is 0.5 s, giving 3.6 s and
            # 8.2 as the hand-computed duration margin and ratio.
            self.assertEqual(
                [member["overlapping_power_interval_count"] for member in cell["members"]],
                [5, 5, 5, 5],
            )
            self.assertEqual(
                [member["sample_count_margin"] for member in cell["members"]],
                [2, 2, 2, 2],
            )
            self.assertEqual(cell["min_overlapping_power_interval_count"], 5)
            self.assertEqual(cell["min_sample_count_margin"], 2)
            self.assertAlmostEqual(cell["min_phase_window_duration_s"], 4.1)
            self.assertAlmostEqual(cell["min_duration_minus_2b_operative_s"], 3.6)
            self.assertAlmostEqual(cell["min_duration_to_2b_operative_ratio"], 8.2)

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
        bundle = self.runs_root / self.bundle_ids["prefill_p128"][0]
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["window_evidence_precheck"]["phase"]["prefill"]["windows"][0][
            "cadence_ratio"
        ] += 0.5
        _write_json(bundle / "summary_metrics.json", summary)
        self._assert_record_refuses("summary_precheck_mismatch")


if __name__ == "__main__":
    unittest.main()
