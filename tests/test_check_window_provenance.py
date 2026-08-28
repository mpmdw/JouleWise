from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise.analysis_manifest_v3 import (
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    render_manifest,
)
from joulewise.calibration_ledger import canonical_sha256 as ledger_canonical_sha256
from joulewise.idle_admission import ADAPTER_CONTINUITY_SCHEMA
from joulewise.whole_window import (
    build_row_provenance,
    canonical_sha256,
    source_manifest_descriptors,
)
from scripts.check_window_provenance import (
    DEFAULT_EXPECTED_REFUSALS,
    main as check_main,
)
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests.test_run_campaign import read_all_jsonl, run_campaign_module


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _tree_digest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _normal_argv(fixture: dict) -> list[str]:
    return [
        "--runs-root",
        str(fixture["runs_root"]),
        "--pack-root",
        str(fixture["prospective_path"].parent),
        "--custody-root",
        str(fixture["root"]),
        "--bracket-binding",
        str(fixture["bracket_path"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--head-pin",
        str(fixture["root"] / "calibration_ledger_head.json"),
    ]


def _finalizer_argv(fixture: dict, scratch: Path) -> list[str]:
    return [
        "--expect-finalize-refusal",
        "--scratch-dir",
        str(scratch),
        "--prospective-manifest",
        str(fixture["prospective_path"]),
        "--plan-tree",
        str(fixture["plan_tree_path"]),
        "--custody-root",
        str(fixture["root"]),
        "--runs-root",
        str(fixture["runs_root"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--bracket-binding",
        str(fixture["bracket_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--aggregate-floor-artifact",
        str(fixture["floor_path"]),
        "--output-dir",
        str(fixture["root"]),
    ]


def _run(argv: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        code = check_main(argv)
    return code, stdout.getvalue()


def _install_s11_checker_fixture(root: Path) -> dict:
    fixture = install_synthetic_finalization_fixture(root)
    runs_root = fixture["runs_root"]
    manifest_path = runs_root / "campaign_manifests" / "synthetic.json"
    manifest = json.loads(manifest_path.read_text())
    prospective_sha = hashlib.sha256(fixture["prospective_path"].read_bytes()).hexdigest()
    manifest["analysis_manifest_sha256"] = prospective_sha
    manifest["session_id"] = "synthetic-science-session"
    manifest["first_physical_run_id"] = manifest["members"][0]["run_id"]
    cooldown_dir = manifest_path.parent / "cooldown"
    cooldown_dir.mkdir()
    for index, member in enumerate(manifest["members"]):
        run_id = member["run_id"]
        if index == 0:
            cooldown = {
                "result": "first_run_exempt",
                "session_id": manifest["session_id"],
                "following_run_id": run_id,
            }
        else:
            payload = b'{"release":true,"release_criteria_met_late":false}\n'
            raw_path = cooldown_dir / f"{run_id}.jsonl"
            raw_path.write_bytes(payload)
            cooldown = {
                "result": "recovered",
                "session_id": manifest["session_id"],
                "following_run_id": run_id,
                "raw_artifact": {
                    "path": f"cooldown/{run_id}.jsonl",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "records": 1,
                },
            }
        member["preceding_campaign_cooldown"] = cooldown
    _write_json(manifest_path, manifest)

    policy_path = (
        Path(__file__).resolve().parents[1]
        / "configs"
        / "campaign_policies"
        / "quiet_mac_p2_production.json"
    )
    (runs_root / "campaign_log.jsonl").write_text("")
    args = run_campaign_module.parse_args(
        [
            "--whole-window-verdict",
            "--runs-dir",
            str(runs_root),
            "--campaign-policy",
            str(policy_path),
            "--neg8-drift-bound",
            str(fixture["root"] / "neg8_drift_bound.json"),
        ]
    )
    with (
        mock.patch.object(run_campaign_module, "validate_bundle", return_value=[]),
        mock.patch.object(
            run_campaign_module, "_final_idle_admission_attempt", return_value=1
        ),
        mock.patch.object(
            run_campaign_module, "_load_idle_rich_telemetry", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module, "post_run_environment_refusals", return_value=()
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_cpu_idle_admission",
            return_value={"decision": "admitted", "conditions": []},
        ),
        mock.patch.object(
            run_campaign_module, "_adapter_observations_for", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_adapter_wattage_continuity",
            return_value={
                "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                "decision": "stable",
                "conditions": [],
            },
        ),
        mock.patch.object(
            run_campaign_module,
            "_neg8_reference_scientific_config_sha256",
            return_value="8" * 64,
        ),
        mock.patch.object(
            run_campaign_module,
            "calibration_bracket_for_bundles",
            return_value=(
                {
                    "schema_version": "joulewise.instrument_calibration_bracket.v1",
                    "status": "passed",
                    "b_fiducial_s": 0.025,
                },
                (),
            ),
        ),
        redirect_stdout(io.StringIO()),
    ):
        if run_campaign_module.run_whole_window_verdict(args) != 0:
            raise AssertionError("whole-window fixture regeneration refused")
    verdict = read_all_jsonl(runs_root / "campaign_log.jsonl")[-1]
    _write_json(fixture["verdict_path"], verdict)

    in_runs_binding = runs_root / "bracket_binding.json"
    in_runs_binding.write_bytes(fixture["bracket_path"].read_bytes())
    fixture["bracket_path"] = in_runs_binding
    return fixture


def _make_one_block_verdict(fixture: dict) -> None:
    verdict = json.loads(fixture["verdict_path"].read_text())
    keep = {bundle_id for bundle_id in verdict["bundle_ids"] if "-b01-" in bundle_id}
    verdict["bundle_ids"] = sorted(keep)
    basis = verdict["evaluation_basis"]
    basis["member_occurrences"] = [
        row for row in basis["member_occurrences"] if row["bundle_id"] in keep
    ]
    basis["sha256"] = canonical_sha256(
        {key: value for key, value in basis.items() if key != "sha256"}
    )
    core = verdict["idle_admission_core"]
    if isinstance(core.get("members"), list):
        core["members"] = [
            row for row in core["members"] if row.get("bundle_id") in keep
        ]
    verdict["member_failures"] = [
        row for row in verdict.get("member_failures", []) if row.get("bundle_id") in keep
    ]
    verdict["row_provenance"] = build_row_provenance(
        policy_sha256=verdict["campaign_policy"]["sha256"],
        bundle_ids=verdict["bundle_ids"],
        source_manifests=verdict["source_campaign_manifests"],
    )
    _write_json(fixture["verdict_path"], verdict)
    (fixture["runs_root"] / "campaign_log.jsonl").write_text(
        json.dumps(verdict, sort_keys=True) + "\n"
    )


def _mutate_d157_contract(fixture: dict) -> None:
    prospective = copy.deepcopy(fixture["prospective"])
    prospective["families"][0]["multiplicity"]["m"] = 1
    prospective["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(prospective)
    prospective["manifest_id"] = calculate_manifest_id(prospective)
    raw = render_manifest(prospective)
    fixture["prospective_path"].write_bytes(raw)
    plan_tree = json.loads(fixture["plan_tree_path"].read_text())
    plan_tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
        raw
    ).hexdigest()
    _write_json(fixture["plan_tree_path"], plan_tree)


class CheckWindowProvenanceTests(unittest.TestCase):
    def test_clean_all_assertions_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            code, output = _run(_normal_argv(fixture))
            self.assertEqual(code, 0, output)
            for assertion_id in (
                "S11-A1",
                "S11-A2",
                "S11-A3",
                "S11-A4",
                "S11-A5",
                "F5-1",
                "F5-2",
                "F5-3",
                "F5-4",
            ):
                self.assertIn(f"PASS {assertion_id} ", output)
            self.assertNotIn("FAIL ", output)

    def test_campaign_id_mutation_isolated_to_s11_a1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            source_path = fixture["runs_root"] / "campaign_manifests" / "synthetic.json"
            shadow_path = fixture["runs_root"] / "campaign_manifests" / "shadow.json"
            shadow = json.loads(source_path.read_text())
            shadow["members"] = [
                {**member, "execution": "blocked_before_invoke"}
                for member in shadow["members"]
            ]
            shadow["analysis_manifest_id"] = "am-" + "f" * 64
            _write_json(shadow_path, shadow)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertIn("FAIL S11-A1 ", output)
            fail_ids = [line.split()[1] for line in output.splitlines() if line.startswith("FAIL ")]
            self.assertEqual(fail_ids, ["S11-A1"], output)

    def test_binding_runs_root_alias_isolated_to_f5_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            alias = fixture["root"] / "runs-alias"
            os.symlink(fixture["runs_root"], alias)
            binding = json.loads(fixture["bracket_path"].read_text())
            binding["runs_root"] = str(alias)
            binding["binding_digest"] = ledger_canonical_sha256(
                {key: value for key, value in binding.items() if key != "binding_digest"}
            )
            _write_json(fixture["bracket_path"], binding)
            code, output = _run(_normal_argv(fixture))
            self.assertNotEqual(code, 0, output)
            self.assertIn("FAIL F5-3 ", output)
            fail_ids = [line.split()[1] for line in output.splitlines() if line.startswith("FAIL ")]
            self.assertEqual(fail_ids, ["F5-3"], output)

    def test_one_block_default_refusal_and_mismatches(self) -> None:
        self.assertEqual(
            DEFAULT_EXPECTED_REFUSALS,
            frozenset({"analysis_finalization_member_cover_mismatch"}),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "fixture", shared_family=True
            )
            _make_one_block_verdict(fixture)
            scratch = root / "scratch"
            code, output = _run(_finalizer_argv(fixture, scratch))
            self.assertEqual(code, 0, output)
            self.assertIn(
                "observed={analysis_finalization_member_cover_mismatch}", output
            )

            code, output = _run(
                _finalizer_argv(fixture, scratch)
                + ["--expected-refusals", "analysis_finalization_verdict_not_passed"]
            )
            self.assertNotEqual(code, 0, output)
            self.assertIn("FAIL FINALIZE-REFUSAL", output)
            self.assertIn("expected={analysis_finalization_verdict_not_passed}", output)

            _mutate_d157_contract(fixture)
            code, output = _run(_finalizer_argv(fixture, scratch))
            self.assertNotEqual(code, 0, output)
            self.assertIn("observed={analysis_finalization_prospective_invalid}", output)
            self.assertIn("expected={analysis_finalization_member_cover_mismatch}", output)

    def test_clean_run_does_not_write_runs_or_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_s11_checker_fixture(Path(tmp))
            before = _tree_digest(fixture["root"])
            code, output = _run(_normal_argv(fixture))
            after = _tree_digest(fixture["root"])
            self.assertEqual(code, 0, output)
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
