from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_engine.inputs import (
    _manifest_collection_id,
    campaign_cooldown_evidence,
)
from joulewise.analysis_manifest_v3 import FINALIZED_SCHEMA_VERSION
from tests.test_run_campaign import (
    cli_cmd_for,
    make_fake_cli,
    read_all_jsonl,
    run_campaign,
    write_config,
)


MANIFEST_ID = "am-" + ("a" * 64)
STAGE_NAME = "01_science_stage"
STAGE_ORDER_ID = "synthetic-science-stage-order-v1"
RUN_ID = "science-bundle"


def _write_json(path: Path, value: object) -> bytes:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    return payload


def _install_valid_v3_pack(root: Path) -> dict[str, object]:
    pack_root = root / "pack"
    stage_dir = pack_root / STAGE_NAME
    stage_dir.mkdir(parents=True)
    config_path = write_config(stage_dir, "science.json", RUN_ID)

    order_manifest = {
        "schema_version": "joulewise.order_manifest.v1",
        "manifest_id": STAGE_ORDER_ID,
        "executed_order": [
            {
                "index": 1,
                "config": config_path.name,
                "run_id": RUN_ID,
            }
        ],
    }
    order_path = stage_dir / "order_manifest.json"
    order_bytes = _write_json(order_path, order_manifest)

    plan_path = pack_root / "plan_tree.json"
    plan_bytes = _write_json(
        plan_path,
        {
            "schema_version": "synthetic.plan_tree.v1",
            "plan_id": "synthetic-science-plan",
        },
    )
    analysis_manifest = {
        "schema_version": "joulewise.analysis_manifest.v3.prospective",
        "manifest_id": MANIFEST_ID,
        "plan": {
            "plan_id": "synthetic-science-plan",
            "path": plan_path.name,
            "sha256": hashlib.sha256(plan_bytes).hexdigest(),
        },
        "stage_manifests": [
            {
                "index": 1,
                "subcampaign_id": STAGE_NAME,
                "role": "science",
                "optional": False,
                "planned_n_bundles": 1,
                "manifest_path": f"{STAGE_NAME}/order_manifest.json",
                "manifest_id": STAGE_ORDER_ID,
                "manifest_sha256": hashlib.sha256(order_bytes).hexdigest(),
            }
        ],
    }
    analysis_path = pack_root / "analysis_manifest_v3.json"
    analysis_bytes = _write_json(analysis_path, analysis_manifest)
    return {
        "pack_root": pack_root,
        "stage_dir": stage_dir,
        "order_path": order_path,
        "analysis_path": analysis_path,
        "analysis_manifest": analysis_manifest,
        "analysis_sha256": hashlib.sha256(analysis_bytes).hexdigest(),
    }


def _campaign_manifest(runs_dir: Path) -> tuple[Path, dict]:
    paths = sorted((runs_dir / "campaign_manifests").glob("*.json"))
    if len(paths) != 1:
        raise AssertionError(f"expected one campaign manifest, found {paths}")
    return paths[0], json.loads(paths[0].read_text(encoding="utf-8"))


class CollectorAnalysisManifestIdentityTests(unittest.TestCase):
    def test_collector_fixture_run_records_v3_manifest_identity_and_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            runs_dir = root / "runs"
            sentinel = root / "bundle-invoked"
            fake_cli = make_fake_cli(root, sentinel)

            result = run_campaign(
                fixture["stage_dir"],
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(sentinel.is_file())
            _, campaign = _campaign_manifest(runs_dir)
            self.assertEqual(campaign["analysis_manifest_id"], MANIFEST_ID)
            self.assertEqual(
                campaign["analysis_manifest_sha256"],
                fixture["analysis_sha256"],
            )

    def test_finalized_v3_collection_identity_selects_collector_cooldown_only(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            runs_dir = root / "runs"
            fake_cli = make_fake_cli(root)
            result = run_campaign(
                fixture["stage_dir"],
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            finalized = {
                "schema_version": FINALIZED_SCHEMA_VERSION,
                "lineage": {"collection_manifest_id": MANIFEST_ID},
            }
            collection_id = _manifest_collection_id(finalized)
            self.assertEqual(collection_id, MANIFEST_ID)

            # A calibration campaign is deliberately null-bound.  Its row
            # must not join to the finalized science collection identity.
            null_session = "calibration-null-session"
            _write_json(
                runs_dir / "campaign_manifests" / "calibration-null.json",
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "session_id": null_session,
                    "analysis_manifest_id": None,
                    "first_physical_run_id": "calibration-null-bundle",
                    "members": [
                        {
                            "execution": "invoked",
                            "run_id": "calibration-null-bundle",
                            "bundle_ids": ["calibration-null-bundle"],
                            "preceding_campaign_cooldown": {
                                "result": "first_run_exempt",
                                "session_id": null_session,
                                "following_run_id": "calibration-null-bundle",
                            },
                        }
                    ],
                },
            )

            selected = campaign_cooldown_evidence(runs_dir, collection_id)
            self.assertIn(RUN_ID, selected)
            self.assertTrue(selected[RUN_ID]["verified"])
            self.assertNotIn("calibration-null-bundle", selected)

    def test_calibration_parent_without_v3_manifest_stays_null(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = root / "calibration-pack-without-v3"
            stage_dir = parent / "calibration-window"
            stage_dir.mkdir(parents=True)
            write_config(stage_dir, "calibration.json", "calibration-bundle")
            runs_dir = root / "runs"
            sentinel = root / "bundle-invoked"
            fake_cli = make_fake_cli(root, sentinel)

            result = run_campaign(
                stage_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(parent.is_dir())
            self.assertFalse((parent / "analysis_manifest_v3.json").exists())
            self.assertTrue(sentinel.is_file())
            _, campaign = _campaign_manifest(runs_dir)
            self.assertIsNone(campaign["analysis_manifest_id"])
            self.assertNotIn("analysis_manifest_sha256", campaign)

    def _assert_refusal(
        self,
        root: Path,
        fixture: dict[str, object],
        expected_reason: str,
    ) -> None:
        runs_dir = root / "runs"
        sentinel = root / "bundle-invoked"
        fake_cli = make_fake_cli(root, sentinel)
        result = run_campaign(
            fixture["stage_dir"],
            runs_dir,
            cli_cmd=cli_cmd_for(fake_cli),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(sentinel.exists())
        self.assertIn(expected_reason, result.stderr)
        rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
        self.assertEqual(rows[-1]["collection"]["verdict"], "invalid")
        self.assertEqual(rows[-1]["collection"]["reasons"], [expected_reason])
        self.assertEqual(
            rows[-1]["preflight"]["prospective_analysis_manifest"][
                "reason_code"
            ],
            expected_reason,
        )
        self.assertFalse((runs_dir / "campaign_manifests").exists())

    def test_today_gamma_shape_missing_manifest_id_refuses_before_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            manifest = copy.deepcopy(fixture["analysis_manifest"])
            manifest.pop("manifest_id")
            _write_json(fixture["analysis_path"], manifest)
            self._assert_refusal(
                root,
                fixture,
                "analysis_prospective_identity_mismatch",
            )

    def test_changed_stage_order_bytes_refuse_before_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            order_path = fixture["order_path"]
            order_path.write_bytes(order_path.read_bytes() + b" \n")
            self._assert_refusal(
                root,
                fixture,
                "analysis_prospective_source_hash_mismatch",
            )

    def test_ambiguous_duplicate_stage_binding_refuses_before_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            manifest = copy.deepcopy(fixture["analysis_manifest"])
            manifest["stage_manifests"].append(
                copy.deepcopy(manifest["stage_manifests"][0])
            )
            _write_json(fixture["analysis_path"], manifest)
            self._assert_refusal(
                root,
                fixture,
                "analysis_prospective_member_cover_mismatch",
            )


if __name__ == "__main__":
    unittest.main()
