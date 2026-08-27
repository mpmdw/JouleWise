from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_engine.inputs import (
    _manifest_collection_id,
    campaign_cooldown_evidence,
)
from joulewise.analysis_manifest_v3 import (
    FINALIZED_SCHEMA_VERSION,
    SCHEMA_VERSION,
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    render_manifest,
    validate_prospective_analysis_manifest_v3,
)
from scripts.run_campaign import resolve_prospective_analysis_manifest_v3
from tests.test_analysis_manifest_v3 import install_synthetic_prospective_fixture
from tests.test_run_campaign import (
    ROOT,
    cli_cmd_for,
    make_fake_cli,
    read_all_jsonl,
    run_campaign,
    write_config,
)


STAGE_NAME = "01_decode_contrast_blocks_01_05"


def _write_json(path: Path, value: object) -> bytes:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    return payload


def _write_manifest_and_rebind_plan_tree(
    fixture: dict[str, object], manifest: dict[str, object]
) -> bytes:
    analysis_path = fixture["analysis_path"]
    plan_tree_path = fixture["plan_tree_path"]
    assert isinstance(analysis_path, Path)
    assert isinstance(plan_tree_path, Path)
    analysis_bytes = render_manifest(manifest)
    analysis_path.write_bytes(analysis_bytes)
    plan_tree = json.loads(plan_tree_path.read_text(encoding="utf-8"))
    plan_tree["downstream_contract"]["analysis_manifest_sha256"] = (
        hashlib.sha256(analysis_bytes).hexdigest()
    )
    _write_json(plan_tree_path, plan_tree)
    return analysis_bytes


def _reidentify_fixture(
    fixture: dict[str, object], *, design_suffix: str
) -> str:
    manifest = copy.deepcopy(fixture["analysis_manifest"])
    assert isinstance(manifest, dict)
    design = manifest["design"]
    assert isinstance(design, dict)
    design["design_id"] = str(design["design_id"]) + design_suffix
    manifest["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(
        manifest
    )
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    analysis_bytes = _write_manifest_and_rebind_plan_tree(fixture, manifest)
    fixture["analysis_manifest"] = manifest
    fixture["analysis_sha256"] = hashlib.sha256(analysis_bytes).hexdigest()
    fixture["manifest_id"] = manifest["manifest_id"]
    refusals = validate_prospective_analysis_manifest_v3(
        manifest,
        manifest_dir=fixture["pack_root"],
        plan_tree_path=fixture["plan_tree_path"],
    )
    if refusals:
        raise AssertionError(
            "reidentified fixture is invalid: "
            + "; ".join(
                f"{refusal.reason_code}: {refusal.detail}"
                for refusal in refusals
            )
        )
    return str(manifest["manifest_id"])


def _install_valid_v3_pack(
    root: Path, *, stage_group: tuple[str, ...] = ()
) -> dict[str, object]:
    analysis_path, synthetic_tree_path, analysis_manifest = (
        install_synthetic_prospective_fixture(root)
    )
    pack_root = analysis_path.parent
    plan_tree_path = pack_root / "plan_tree.json"
    plan_tree_path.write_bytes(synthetic_tree_path.read_bytes())
    stage_dir = pack_root / STAGE_NAME

    if stage_group:
        grouped_stage_dir = pack_root.joinpath(*stage_group, STAGE_NAME)
        grouped_stage_dir.parent.mkdir(parents=True, exist_ok=True)
        stage_dir.rename(grouped_stage_dir)
        old_prefix = f"{STAGE_NAME}/"
        new_prefix = f"{'/'.join(stage_group)}/{STAGE_NAME}/"
        for stage in analysis_manifest["stage_manifests"]:
            if stage["manifest_path"].startswith(old_prefix):
                stage["manifest_path"] = stage["manifest_path"].replace(
                    old_prefix, new_prefix, 1
                )
        for contrast in analysis_manifest["contrasts"]:
            for member in contrast["members"]:
                if member["config"].startswith(old_prefix):
                    member["config"] = member["config"].replace(
                        old_prefix, new_prefix, 1
                    )
        stage_dir = grouped_stage_dir

    order_path = stage_dir / "order_manifest.json"
    order_manifest = json.loads(order_path.read_text(encoding="utf-8"))
    config_sha256_by_run_id: dict[str, str] = {}
    for entry in order_manifest["executed_order"]:
        config_path = stage_dir / entry["config"]
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["hardware_target"]["telemetry_backend"] = "mock"
        config_bytes = _write_json(config_path, config)
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        entry["config_sha256"] = config_sha256
        config_sha256_by_run_id[entry["run_id"]] = config_sha256
    order_bytes = _write_json(order_path, order_manifest)
    for stage in analysis_manifest["stage_manifests"]:
        if stage["subcampaign_id"] == STAGE_NAME:
            stage["manifest_sha256"] = hashlib.sha256(order_bytes).hexdigest()
    for contrast in analysis_manifest["contrasts"]:
        for member in contrast["members"]:
            if member["run_id"] in config_sha256_by_run_id:
                member["config_sha256"] = config_sha256_by_run_id[
                    member["run_id"]
                ]
    analysis_manifest["frozen_semantics_sha256"] = (
        analysis_semantics_sha256_v1(analysis_manifest)
    )
    analysis_manifest["manifest_id"] = calculate_manifest_id(
        analysis_manifest
    )

    fixture: dict[str, object] = {
        "pack_root": pack_root,
        "stage_dir": stage_dir,
        "order_path": order_path,
        "analysis_path": analysis_path,
        "plan_tree_path": plan_tree_path,
        "analysis_manifest": analysis_manifest,
        "manifest_id": analysis_manifest["manifest_id"],
    }
    analysis_bytes = _write_manifest_and_rebind_plan_tree(
        fixture, analysis_manifest
    )
    fixture["analysis_sha256"] = hashlib.sha256(analysis_bytes).hexdigest()
    if analysis_manifest["manifest_id"] != calculate_manifest_id(
        analysis_manifest
    ):
        raise AssertionError("fixture manifest_id is not canonical")
    refusals = validate_prospective_analysis_manifest_v3(
        analysis_manifest,
        manifest_dir=pack_root,
        plan_tree_path=plan_tree_path,
    )
    if refusals:
        raise AssertionError(
            "fixture is not canonically valid: "
            + "; ".join(
                f"{refusal.reason_code}: {refusal.detail}"
                for refusal in refusals
            )
        )
    return {
        **fixture,
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
            self.assertEqual(
                campaign["analysis_manifest_id"], fixture["manifest_id"]
            )
            self.assertEqual(
                campaign["analysis_manifest_sha256"],
                fixture["analysis_sha256"],
            )
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(
                verdict["analysis_manifest"],
                {
                    "manifest_id": fixture["manifest_id"],
                    "file_sha256": fixture["analysis_sha256"],
                    "validation": "valid",
                },
            )
            self.assertEqual(
                verdict["claim_readiness"]["verdict"], "not_assessed"
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
            _, campaign = _campaign_manifest(runs_dir)
            manifest_id = campaign["analysis_manifest_id"]
            run_id = campaign["members"][0]["bundle_ids"][0]

            # This deliberately minimal finalized object is sufficient for
            # this join-only test: _manifest_collection_id reads exactly the
            # finalized schema discriminator and lineage.collection_manifest_id;
            # attachment validity is owned by the finalized-manifest validator.
            finalized = {
                "schema_version": FINALIZED_SCHEMA_VERSION,
                "lineage": {"collection_manifest_id": manifest_id},
            }
            collection_id = _manifest_collection_id(finalized)
            self.assertEqual(collection_id, manifest_id)

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
            self.assertIn(run_id, selected)
            self.assertTrue(selected[run_id]["verified"])
            self.assertNotIn("calibration-null-bundle", selected)

    def test_exploratory_calibration_without_v3_marker_stays_null(self) -> None:
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

    def test_production_collection_without_any_analysis_marker_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_dir = root / "production-science-without-manifest"
            stage_dir.mkdir()
            write_config(stage_dir, "science.json", "science-bundle")
            runs_dir = root / "runs"
            sentinel = root / "bundle-invoked"
            fake_cli = make_fake_cli(root, sentinel)

            result = run_campaign(
                stage_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                campaign_policy=(
                    ROOT
                    / "configs"
                    / "campaign_policies"
                    / "quiet_mac_p2_production.json"
                ),
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn(
                "analysis_manifest_prospective_not_consumable", result.stderr
            )
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(
                verdict["collection"]["reasons"],
                ["analysis_manifest_prospective_not_consumable"],
            )

    def test_non_parent_ancestor_marker_collects_with_canonical_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root, stage_group=("group",))
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
            self.assertEqual(
                campaign["analysis_manifest_id"], fixture["manifest_id"]
            )

    def test_symlinked_stage_resolves_through_physical_pack_ancestors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            alias = root / "stage-alias"
            alias.symlink_to(fixture["stage_dir"], target_is_directory=True)

            identity = resolve_prospective_analysis_manifest_v3(alias)

            self.assertIsNotNone(identity)
            assert identity is not None
            self.assertEqual(identity.manifest_id, fixture["manifest_id"])

    def test_splitwise_decode_v1_finalized_marker_preserves_null_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_pack_root = (
                ROOT / "configs" / "campaigns" / "splitwise_decode_v1"
            )
            pack_root = root / "splitwise_decode_v1"
            shutil.copytree(source_pack_root, pack_root)
            stage_dir = pack_root / "01_decode_contrast_blocks_01_05"
            marker = json.loads(
                (pack_root / "analysis_manifest_v3.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(marker["schema_version"], SCHEMA_VERSION)
            self.assertIsNone(
                resolve_prospective_analysis_manifest_v3(stage_dir)
            )
            for config_path in stage_dir.glob("*.json"):
                if config_path.name == "order_manifest.json":
                    continue
                config = json.loads(config_path.read_text(encoding="utf-8"))
                config["hardware_target"]["telemetry_backend"] = "mock"
                _write_json(config_path, config)
            runs_dir = root / "runs"
            fake_cli = make_fake_cli(root)

            result = run_campaign(
                stage_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
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
        self.assertIn(expected_reason, rows[-1]["collection"]["reasons"])
        self.assertEqual(
            rows[-1]["preflight"]["prospective_analysis_manifest"][
                "reason_code"
            ],
            expected_reason,
        )
        self.assertIn(
            expected_reason,
            {
                refusal["reason_code"]
                for refusal in rows[-1]["preflight"][
                    "prospective_analysis_manifest"
                ]["refusals"]
            },
        )
        self.assertFalse((runs_dir / "campaign_manifests").exists())

    def test_today_gamma_shape_missing_manifest_id_refuses_before_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            manifest = copy.deepcopy(fixture["analysis_manifest"])
            manifest.pop("manifest_id")
            _write_manifest_and_rebind_plan_tree(fixture, manifest)
            self._assert_refusal(
                root,
                fixture,
                "analysis_prospective_schema_invalid",
            )

    def test_well_formed_but_invented_manifest_id_refuses_before_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            manifest = copy.deepcopy(fixture["analysis_manifest"])
            manifest["manifest_id"] = "am-" + ("a" * 64)
            _write_manifest_and_rebind_plan_tree(fixture, manifest)
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
            duplicate = copy.deepcopy(manifest["stage_manifests"][0])
            duplicate["index"] = 2
            manifest["stage_manifests"][1] = duplicate
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            _write_manifest_and_rebind_plan_tree(fixture, manifest)
            self.assertEqual(
                validate_prospective_analysis_manifest_v3(
                    manifest,
                    manifest_dir=fixture["pack_root"],
                    plan_tree_path=fixture["plan_tree_path"],
                ),
                (),
            )
            self._assert_refusal(
                root,
                fixture,
                "analysis_prospective_source_hash_mismatch",
            )

    def test_cross_id_existing_bundle_reuse_refuses_before_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            stage_dir = fixture["stage_dir"]
            assert isinstance(stage_dir, Path)
            config_path = next(
                path
                for path in sorted(stage_dir.glob("*.json"))
                if path.name != "order_manifest.json"
            )
            run_id = json.loads(config_path.read_text(encoding="utf-8"))[
                "run_id"
            ]
            runs_dir = root / "runs"
            bundle_dir = runs_dir / run_id
            bundle_dir.mkdir(parents=True)
            _write_json(bundle_dir / "summary_metrics.json", {"status": "succeeded"})
            manifest_dir = runs_dir / "campaign_manifests"
            manifest_dir.mkdir()
            _write_json(
                manifest_dir / "original-owner.json",
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "session_id": "original-owner",
                    "analysis_manifest_id": fixture["manifest_id"],
                    "first_physical_run_id": run_id,
                    "members": [
                        {
                            "execution": "invoked",
                            "run_id": run_id,
                            "bundle_ids": [run_id],
                            "preceding_campaign_cooldown": {
                                "result": "first_run_exempt"
                            },
                        }
                    ],
                },
            )
            changed_id = _reidentify_fixture(
                fixture, design_suffix="-changed-reuse"
            )
            sentinel = root / "second-bundle-invoked"
            fake_cli = make_fake_cli(root, sentinel)

            result = run_campaign(
                stage_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn(
                "analysis_manifest_collection_identity_mismatch",
                result.stderr,
            )
            self.assertIn(str(changed_id), result.stderr)
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())
            self.assertEqual(
                sorted(path.name for path in manifest_dir.glob("*.json")),
                ["original-owner.json"],
            )

    def test_cross_id_campaign_log_append_refuses_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = _install_valid_v3_pack(root)
            runs_dir = root / "runs"
            first_cli = make_fake_cli(root)
            first = run_campaign(
                fixture["stage_dir"],
                runs_dir,
                cli_cmd=cli_cmd_for(first_cli),
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            log_path = runs_dir / "campaign_log.jsonl"
            original_log = log_path.read_bytes()
            original_manifests = sorted(
                (runs_dir / "campaign_manifests").glob("*.json")
            )
            _reidentify_fixture(fixture, design_suffix="-changed-log")
            sentinel = root / "second-bundle-invoked"
            second_cli = make_fake_cli(root, sentinel)

            second = run_campaign(
                fixture["stage_dir"],
                runs_dir,
                cli_cmd=cli_cmd_for(second_cli),
            )

            self.assertEqual(second.returncode, 1, second.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn(
                "analysis_manifest_collection_identity_mismatch",
                second.stderr,
            )
            self.assertEqual(log_path.read_bytes(), original_log)
            self.assertEqual(
                sorted((runs_dir / "campaign_manifests").glob("*.json")),
                original_manifests,
            )


if __name__ == "__main__":
    unittest.main()
