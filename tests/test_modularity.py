from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_manifest import validate_analysis_registry
from joulewise.detection_floor import (
    calibration_scope_is_registered,
    validate_floor_metric_window_class,
)
from joulewise.detection_floor_registry import (
    DetectionFloorRegistryError,
    load_detection_floor_closed_sets,
)


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_DIR = ROOT / "configs" / "campaigns" / "p2_015_floors"
GENERATOR = CAMPAIGN_DIR / "generate_configs.py"
CAMPAIGN_SPEC = CAMPAIGN_DIR / "campaign_spec.json"
ANALYSIS_REGISTRY = ROOT / "configs" / "analysis_registry" / "slice_2m_ap2.v1.json"
DETECTION_REGISTRY = (
    ROOT / "configs" / "analysis_registry" / "detection_floor_closed_sets.v1.json"
)
DETECTION_DIGEST = DETECTION_REGISTRY.with_suffix(".sha256")


def run_campaign(spec_path: Path, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--campaign-spec",
            str(spec_path),
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )


class CampaignSpecificationTests(unittest.TestCase):
    def test_default_spec_reproduces_every_frozen_generated_byte(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "generated"
            result = run_campaign(CAMPAIGN_SPEC, out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)

            excluded = {
                "backup_icloud.sh",
                "generate_configs.py",
                "campaign_spec.json",
            }
            expected = {
                path.relative_to(CAMPAIGN_DIR)
                for path in CAMPAIGN_DIR.rglob("*")
                if path.is_file()
                and path.name not in excluded
                and "__pycache__" not in path.parts
            }
            observed = {
                path.relative_to(out_dir)
                for path in out_dir.rglob("*")
                if path.is_file()
            }
            self.assertEqual(observed, expected)
            for relative_path in sorted(expected):
                with self.subTest(path=relative_path):
                    self.assertEqual(
                        (out_dir / relative_path).read_bytes(),
                        (CAMPAIGN_DIR / relative_path).read_bytes(),
                    )

    def test_model_n_profiles_block_pattern_suite_and_prefix_come_from_one_spec(self) -> None:
        source = json.loads(CAMPAIGN_SPEC.read_text(encoding="utf-8"))
        changed = copy.deepcopy(source)
        changed["campaign"]["n"] = 2
        changed["campaign"]["run_id_prefix"] = "swap7"
        changed["campaign"]["runs_dir"] = "runs/spec_swap"
        changed["model"]["tag"] = "qwen3-4b-mlx"
        changed["model"]["plan_tag"] = "qwen3-4b"
        changed["model"]["config"].update(
            {
                "name": "Qwen3-4B-Instruct-4bit",
                "family": "qwen3",
                "source": "/models/qwen3-4b",
                "revision": "revision-qwen3",
            }
        )
        changed["profiles"]["df-rq-mid"]["prompt_tokens"] = 777
        changed["suite_manifest"] = {
            "ref": "configs/suite_manifests/replacement_suite.json",
            "sha256": "a" * 64,
        }
        changed["block_pattern"] = [
            {"label": "B", "position": "B1"},
            {"label": "A", "position": "A1"},
            {"label": "A", "position": "A2"},
            {"label": "B", "position": "B2"},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec_path = tmp_path / "campaign.json"
            spec_path.write_text(json.dumps(changed), encoding="utf-8")
            out_dir = tmp_path / "generated"
            result = run_campaign(spec_path, out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)

            plan = json.loads((out_dir / "calibration_plan.json").read_text())
            order = json.loads((out_dir / "order_manifest.json").read_text())
            request_config = json.loads(
                (
                    out_dir
                    / "01_request_absolute_core"
                    / "swap7-df-rq-mid-abs-r01.json"
                ).read_text()
            )
            suite_config = json.loads(
                (
                    out_dir
                    / "06_suite_absolute"
                    / "swap7-df-su-sentinel-abs-r01.json"
                ).read_text()
            )

        self.assertEqual(plan["plan_id"], "p2-015-window-a-m3max-qwen3-4b-v1")
        self.assertEqual(plan["fixed_n"], 2)
        self.assertEqual(plan["runs_dir"], "runs/spec_swap")
        self.assertEqual(plan["execution_modes"]["expanded_window_a"]["planned_bundles"], 58)
        self.assertTrue(all(row["run_id"].startswith("swap7-") for row in order["executed_order"]))
        self.assertEqual({row["model_tag"] for row in order["executed_order"]}, {"qwen3-4b-mlx"})
        self.assertEqual(request_config["model"]["name"], "Qwen3-4B-Instruct-4bit")
        self.assertEqual(request_config["workload_profile"]["prompt_tokens"], 777)
        self.assertEqual(
            suite_config["workload_profile"]["suite_manifest_ref"],
            "configs/suite_manifests/replacement_suite.json",
        )
        comparative = next(cell for cell in plan["cells"] if cell["kind"] == "comparative_abba")
        self.assertEqual(
            comparative["ordered_blocks"][0]["executed_labels"],
            ["B", "A", "A", "B"],
        )

    def test_invalid_spec_refuses_before_creating_output(self) -> None:
        value = json.loads(CAMPAIGN_SPEC.read_text(encoding="utf-8"))
        del value["campaign"]["run_id_prefix"]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec_path = tmp_path / "bad.json"
            spec_path.write_text(json.dumps(value), encoding="utf-8")
            out_dir = tmp_path / "generated"
            result = run_campaign(spec_path, out_dir)
            self.assertEqual(result.returncode, 2)
            self.assertIn("campaign specification error", result.stderr)
            self.assertFalse(out_dir.exists())


class ClosedSetRegistryTests(unittest.TestCase):
    def test_analysis_condition_pairs_are_validated_as_registry_declarations(self) -> None:
        registry = json.loads(ANALYSIS_REGISTRY.read_text(encoding="utf-8"))
        registry["condition_pairs"] = [
            {"condition_a": "short_short", "condition_b": "long_short"},
            {"condition_a": "long_short", "condition_b": "mid_mid"},
        ]
        self.assertEqual(validate_analysis_registry(registry), [])

        duplicate = copy.deepcopy(registry)
        duplicate["condition_pairs"].append(copy.deepcopy(duplicate["condition_pairs"][0]))
        self.assertIn(
            "registry.condition_pairs: duplicate ordered pair",
            validate_analysis_registry(duplicate),
        )

    def test_detection_floor_registry_bytes_are_checksum_bound(self) -> None:
        registry = load_detection_floor_closed_sets(repository_root=ROOT)
        observed = hashlib.sha256(DETECTION_REGISTRY.read_bytes()).hexdigest()
        recorded = DETECTION_DIGEST.read_text(encoding="utf-8").split()[0]
        self.assertEqual(registry.sha256, observed)
        self.assertEqual(registry.sha256, recorded)

    def test_changed_detection_floor_declaration_requires_matching_digest(self) -> None:
        value = json.loads(DETECTION_REGISTRY.read_text(encoding="utf-8"))
        value["floor_metrics"].append(
            {
                "name": "phase_energy_j.score",
                "window_class": "phase",
                "authority": "counterfactual test declaration",
            }
        )
        value["calibration_scopes"].append(
            {
                "scope_id": "successor_window",
                "authority": "counterfactual test declaration",
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_path = tmp_path / DETECTION_REGISTRY.name
            digest_path = registry_path.with_suffix(".sha256")
            registry_path.write_text(
                json.dumps(value, indent=2) + "\n",
                encoding="utf-8",
            )
            digest_path.write_bytes(DETECTION_DIGEST.read_bytes())
            with self.assertRaisesRegex(DetectionFloorRegistryError, "sha256 mismatch"):
                load_detection_floor_closed_sets(
                    registry_path=registry_path,
                    digest_path=digest_path,
                )

            digest = hashlib.sha256(registry_path.read_bytes()).hexdigest()
            digest_path.write_text(
                f"{digest}  {registry_path.name}\n",
                encoding="utf-8",
            )
            loaded = load_detection_floor_closed_sets(
                registry_path=registry_path,
                digest_path=digest_path,
            )

        self.assertEqual(
            validate_floor_metric_window_class(
                "phase_energy_j.score",
                "phase",
                registry=loaded,
            ),
            ("phase_energy_j.score", "phase"),
        )
        self.assertTrue(
            calibration_scope_is_registered(
                "successor_window",
                registry=loaded,
            )
        )


if __name__ == "__main__":
    unittest.main()
