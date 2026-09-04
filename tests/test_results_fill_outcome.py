"""Acceptance coverage for the D-165 OB-01 / OR-01 renderer."""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import dominance_closeout as core
from joulewise import results_fill_outcome as renderer
from joulewise import whole_window
from joulewise.analysis_manifest_v3 import (
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    render_manifest,
    validate_prospective_analysis_manifest_v3,
)
from joulewise.identity_pins import stack_identity_sha256
from tests import test_d165_dominance_closeout as d165_fixtures
from tests.test_analysis_manifest_v3 import install_synthetic_prospective_fixture


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "results_fill_outcome"
REGISTRY = ROOT / "docs" / "paper" / "results-fill-registry.md"
FILL_KEYS = ("OB-01", "OR-01")
QWEN3 = {
    "A": {
        "family": "qwen3",
        "model_tag": "qwen3-1p7b",
        "name": "Qwen3-1.7B-4bit",
        "public_name": "Qwen3-1.7B",
        "revision": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
    },
    "B": {
        "family": "qwen3",
        "model_tag": "qwen3-8b",
        "name": "Qwen3-8B-4bit",
        "public_name": "Qwen3-8B",
        "revision": "545dc4251c05440727734bcd94334791f6ab0192",
    },
}


def _file_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _switch_sources_to_qwen3(manifest: dict, floor: dict) -> None:
    """Retarget fresh D-165 builder copies to the ruled synthetic `_v5` pair."""

    floor_by_id = {cell["cell_id"]: cell for cell in floor["cells"]}
    for arm in manifest["arms"]:
        identity = QWEN3[arm["arm_id"].rsplit(":", 1)[1]]
        arm["model_tag"] = identity["model_tag"]
        realized = arm["realized_stack_identity"]
        realized["model"].update(
            {
                "context_window": 40960,
                "family": identity["family"],
                "name": identity["name"],
                "revision": identity["revision"],
                "source": f"/Users/edr/jw_models/mlx-community/{identity['name']}",
            }
        )
        realized["tokenizer"].update(
            {
                "identifier": (
                    f"/Users/edr/jw_models/mlx-community/{identity['name']}"
                ),
                "revision": identity["revision"],
                "vocab_size": 151936,
            }
        )
        floor_stack = arm["floor_stack_identity"]
        floor_stack["tokenizer_identity"].update(
            {
                "identifier": identity["name"],
                "revision": identity["revision"],
                "vocab_size": 151936,
            }
        )
        floor_cell = floor_by_id[arm["floor_cell_id"]]
        floor_cell["source_regime"]["stack_identity"] = copy.deepcopy(floor_stack)
        floor_cell["source_regime"]["stack_identity_sha256"] = (
            stack_identity_sha256(floor_stack)
        )


def _built_sources(
    builder: str, *, v5_identity: bool = True
) -> tuple[dict | None, bytes, bytes, bytes]:
    floor = d165_fixtures.floor_artifact()
    manifest = d165_fixtures.finalized_manifest()
    if v5_identity:
        _switch_sources_to_qwen3(manifest, floor)

    if builder == "branch_a":
        for cell in floor["cells"]:
            for component_name, parent_key in (
                ("absolute", "max_abs_residual_j"),
                ("comparative", "max_abs_delta_j"),
            ):
                component = cell[component_name]
                point = core._point_unguarded_floor_from_component(
                    component, parent_key=parent_key
                )
                component["corner_widened_unguarded_floor_j"] = 2.0 * point
    elif builder == "branch_b":
        first = True
        for cell in floor["cells"]:
            for component_name, parent_key in (
                ("absolute", "max_abs_residual_j"),
                ("comparative", "max_abs_delta_j"),
            ):
                if first:
                    first = False
                    continue
                component = cell[component_name]
                point = core._point_unguarded_floor_from_component(
                    component, parent_key=parent_key
                )
                component["corner_widened_unguarded_floor_j"] = 2.0 * point
    elif builder == "closeout_refusal":
        floor["cells"][0]["absolute"]["max_abs_residual_j"] = 0.0
        floor["cells"][0]["absolute"]["prediction_component_j"] = 0.0
    elif builder not in {"none", "source_refusal", "census_refusal"}:
        raise AssertionError(f"unknown fixture builder: {builder}")

    sidecar = d165_fixtures.replay_sidecar(
        floor, residual_width_scale=10.0 if builder == "branch_b" else 20.0
    )
    if builder == "census_refusal":
        sidecar["cells"].pop()
    manifest_bytes, floor_bytes, sidecar_bytes = (
        d165_fixtures._reseal_test_sources(manifest, floor, sidecar)
    )
    if builder == "none":
        return None, manifest_bytes, floor_bytes, sidecar_bytes
    if builder == "source_refusal":
        changed_floor = json.loads(floor_bytes.decode("utf-8"))
        changed_floor["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] = 2.1
        floor_bytes = _file_json_bytes(changed_floor)
    closeout = d165_fixtures.build_d165_dominance_closeout(
        manifest_bytes, floor_bytes, sidecar_bytes
    )
    return closeout, manifest_bytes, floor_bytes, sidecar_bytes


def _render(fixture: dict, *, v5_identity: bool = True) -> dict[str, str]:
    closeout, manifest, floor, sidecar = _built_sources(
        fixture["builder"], v5_identity=v5_identity
    )
    return renderer.render_outcome_fills(
        closeout,
        finalized_manifest_bytes=manifest,
        floor_artifact_bytes=floor,
        replay_sidecar_bytes=sidecar,
    )


def _install_v5_prospective(
    root: Path, *, wrong_revision: bool = False
) -> tuple[Path, Path, dict]:
    manifest_path, plan_tree_path, prospective = (
        install_synthetic_prospective_fixture(root)
    )
    pack_root = manifest_path.parent
    config_sha256_by_path: dict[str, str] = {}
    for contrast in prospective["contrasts"]:
        for member in contrast["members"]:
            relative = member["config"]
            config_path = pack_root / relative
            config = json.loads(config_path.read_text(encoding="utf-8"))
            identity = QWEN3[member["arm"]]
            config["model"].update(
                {
                    "context_window": 40960,
                    "family": identity["family"],
                    "name": identity["name"],
                    "revision": (
                        "0" * 40
                        if wrong_revision and member["arm"] == "A"
                        else identity["revision"]
                    ),
                    "source": (
                        f"/Users/edr/jw_models/mlx-community/{identity['name']}"
                    ),
                }
            )
            raw = _file_json_bytes(config)
            config_path.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            member["config_sha256"] = digest
            config_sha256_by_path[relative] = digest

    stage_sha256_by_path: dict[str, str] = {}
    for stage in prospective["stage_manifests"]:
        stage_relative = stage["manifest_path"]
        stage_path = pack_root / stage_relative
        stage_manifest = json.loads(stage_path.read_text(encoding="utf-8"))
        stage_root = Path(stage_relative).parent
        for row in stage_manifest["executed_order"]:
            config_relative = (stage_root / row["config"]).as_posix()
            row["config_sha256"] = config_sha256_by_path[config_relative]
        stage_raw = _file_json_bytes(stage_manifest)
        stage_path.write_bytes(stage_raw)
        stage_digest = hashlib.sha256(stage_raw).hexdigest()
        stage["manifest_sha256"] = stage_digest
        stage_sha256_by_path[stage_relative] = stage_digest

    order_path = pack_root / prospective["root_order_manifest"]["path"]
    order = json.loads(order_path.read_text(encoding="utf-8"))
    for row in order["executed_order"]:
        row["config_sha256"] = config_sha256_by_path[row["config"]]
    for row in order["subcampaign_order"]:
        row["manifest_sha256"] = stage_sha256_by_path[row["manifest_path"]]
    order_raw = _file_json_bytes(order)
    order_path.write_bytes(order_raw)
    prospective["root_order_manifest"]["sha256"] = hashlib.sha256(
        order_raw
    ).hexdigest()

    prospective["frozen_semantics_sha256"] = analysis_semantics_sha256_v1(
        prospective
    )
    prospective["manifest_id"] = calculate_manifest_id(prospective)
    manifest_path.write_bytes(render_manifest(prospective))
    plan_tree = json.loads(plan_tree_path.read_text(encoding="utf-8"))
    plan_tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
        manifest_path.read_bytes()
    ).hexdigest()
    plan_tree_path.write_bytes(_file_json_bytes(plan_tree))
    refusals = validate_prospective_analysis_manifest_v3(
        prospective,
        manifest_dir=pack_root,
        plan_tree_path=plan_tree_path,
    )
    if refusals:
        raise AssertionError(
            "; ".join(
                f"{refusal.reason_code}: {refusal.detail}"
                for refusal in refusals
            )
        )
    return manifest_path, plan_tree_path, prospective


def _install_before_chain(root: Path, *, wrong_revision: bool = False) -> dict:
    manifest_path, plan_tree_path, prospective = _install_v5_prospective(
        root, wrong_revision=wrong_revision
    )
    runs_root = root / "runs"
    manifest_dir = runs_root / "campaign_manifests"
    manifest_dir.mkdir(parents=True)
    expected_ids = [
        member["run_id"]
        for contrast in prospective["contrasts"]
        for member in contrast["members"]
    ]
    source_manifest = {
        "schema_version": "joulewise.campaign_provenance.v1",
        "session_id": "fixture-session",
        "created_at": "2026-09-04T00:00:00Z",
        "config_dir": str(manifest_path.parent),
        "analysis_manifest_id": prospective["manifest_id"],
        "analysis_manifest_sha256": hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest(),
        "campaign_policy": {"sha256": "a" * 64},
        "environment_preflight": None,
        "cooldown_anchor": None,
        "first_physical_run_id": None,
        "members": [
            {
                "run_id": member_id,
                "execution": "existing",
                "config": f"{member_id}.json",
                "bundle_ids": [member_id],
            }
            for member_id in expected_ids
        ],
        "cooldown_gates": [],
    }
    source_manifest_path = manifest_dir / "fixture-session.json"
    source_manifest_raw = _file_json_bytes(source_manifest)
    source_manifest_path.write_bytes(source_manifest_raw)
    descriptor = {
        "path": source_manifest_path.relative_to(runs_root).as_posix(),
        "sha256": hashlib.sha256(source_manifest_raw).hexdigest(),
    }
    basis_payload = {
        "schema_version": "joulewise.idle_admission_evaluation_basis.v1",
        "policy_sha256": "a" * 64,
        "member_occurrences": [
            {
                "bundle_id": member_id,
                "bundle_path": member_id,
                "config_sha256": "b" * 64,
                "metadata_sha256": "c" * 64,
                "summary_sha256": "d" * 64,
            }
            for member_id in expected_ids
        ],
        "calibration_bracket_set": {},
        "consumption_semantics_id": whole_window.MINTED_CONSUMPTION_SEMANTICS_ID,
    }
    basis = {**basis_payload, "sha256": whole_window.canonical_sha256(basis_payload)}
    row = {
        "schema_version": whole_window.WHOLE_WINDOW_SCHEMA,
        "timestamp": "2026-09-04T00:00:01Z",
        "record_type": "idle_admission_whole_window_verdict",
        "status": "failed",
        "claim_licensing": True,
        "runs_dir": str(runs_root.resolve()),
        "evaluation_scope": {
            "runs_root": str(runs_root.resolve()),
            "started_at": "2026-09-04T00:00:00Z",
            "completed_at": "2026-09-04T00:00:01Z",
        },
        "evaluation_basis": basis,
        "campaign_policy": {"sha256": "a" * 64},
        "bundle_ids": expected_ids,
        "waived_bundles": [],
        "occurrence_supersessions": [],
        "excluded_bundles": [],
        "member_failures": [],
        "idle_admission_core": {
            "schema_version": whole_window.IDLE_ADMISSION_CORE_SCHEMA,
            "policy_sha256": "a" * 64,
            "conditions": ["synthetic_window_excluded"],
            "members": [],
        },
        "source_campaign_manifests": [descriptor],
        "row_provenance": {
            "schema_version": whole_window.WHOLE_WINDOW_PROVENANCE_SCHEMA,
            "policy_sha256": "a" * 64,
            "membership_sha256": whole_window.canonical_sha256(
                sorted(expected_ids)
            ),
            "source_campaign_manifests": [descriptor],
        },
    }
    verdict_path = runs_root / "whole_window_verdict.json"
    verdict_raw = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
    verdict_path.write_bytes(verdict_raw)
    campaign_log_path = runs_root / "campaign_log.jsonl"
    campaign_log_path.write_bytes(b'{"record_type": "fixture"}\n' + verdict_raw)
    return {
        "runs_root_path": runs_root,
        "campaign_log_path": campaign_log_path,
        "campaign_log_sha256": hashlib.sha256(
            campaign_log_path.read_bytes()
        ).hexdigest(),
        "whole_window_verdict_path": verdict_path,
        "whole_window_verdict_sha256": hashlib.sha256(verdict_raw).hexdigest(),
        "prospective_manifest_path": manifest_path,
        "prospective_manifest_sha256": hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest(),
        "plan_tree_path": plan_tree_path,
        "plan_tree_sha256": hashlib.sha256(plan_tree_path.read_bytes()).hexdigest(),
        "expected_ids": expected_ids,
    }


def _before_kwargs(chain: dict) -> dict:
    return {
        key: chain[key]
        for key in (
            "runs_root_path",
            "campaign_log_path",
            "campaign_log_sha256",
            "whole_window_verdict_path",
            "whole_window_verdict_sha256",
            "prospective_manifest_path",
            "prospective_manifest_sha256",
            "plan_tree_path",
            "plan_tree_sha256",
        )
    }


def _rewrite_verdict(chain: dict, mutate, *, occurrences: int = 1) -> None:
    row = json.loads(chain["whole_window_verdict_path"].read_text(encoding="utf-8"))
    mutate(row)
    raw = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
    chain["whole_window_verdict_path"].write_bytes(raw)
    chain["whole_window_verdict_sha256"] = hashlib.sha256(raw).hexdigest()
    chain["campaign_log_path"].write_bytes(
        b'{"record_type": "fixture"}\n' + raw * occurrences
    )
    chain["campaign_log_sha256"] = hashlib.sha256(
        chain["campaign_log_path"].read_bytes()
    ).hexdigest()


def _registry_oracle(name: str) -> str:
    registry = REGISTRY.read_text(encoding="utf-8")
    match = re.search(
        rf"Acceptance oracle `{re.escape(name)}`: `([^`\r\n]+)`", registry
    )
    if match is None:
        raise AssertionError(f"registry acceptance oracle missing: {name}")
    return match.group(1)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


class ResultsFillOutcomeTests(unittest.TestCase):
    maxDiff = None

    def test_b1_registered_bytes_are_the_independent_acceptance_oracle(self) -> None:
        fixture_paths = sorted(FIXTURES.glob("*.json"))
        self.assertEqual(
            [path.name for path in fixture_paths],
            [
                "before_comparison_absent_verdict.json",
                "before_comparison_refusal.json",
                "branch_a.json",
                "branch_b.json",
                "closeout_refusal.json",
            ],
        )
        for path in fixture_paths:
            fixture = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(fixture=path.stem):
                for fill_key, oracle_name in fixture["registry_oracles"].items():
                    self.assertEqual(
                        fixture["expected"][fill_key], _registry_oracle(oracle_name)
                    )
                rendered = _render(fixture)
                self.assertEqual(
                    {key: rendered[key] for key in FILL_KEYS}, fixture["expected"]
                )
                self.assertFalse(
                    any(
                        marker in value
                        for value in rendered.values()
                        for marker in ("[VALUE]", "[FILL:", "[PENDING]")
                    )
                )

    def test_f1_path_chain_replays_owning_validators_but_ambiguous_result_stops(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            chain = _install_before_chain(Path(tmp))
            expected = {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL}
            with (
                mock.patch(
                    "joulewise.analysis_manifest_v3."
                    "validate_prospective_analysis_manifest_v3",
                    wraps=validate_prospective_analysis_manifest_v3,
                ) as prospective_validator,
                mock.patch(
                    "joulewise.whole_window.whole_window_refusal_reasons",
                    wraps=whole_window.whole_window_refusal_reasons,
                ) as whole_window_validator,
            ):
                rendered = renderer.render_outcome_fills(
                    None, **_before_kwargs(chain)
                )
            self.assertEqual(rendered, expected)
            prospective_validator.assert_called_once()
            self.assertEqual(
                prospective_validator.call_args.kwargs,
                {
                    "manifest_dir": chain["prospective_manifest_path"].parent,
                    "plan_tree_path": chain["plan_tree_path"],
                },
            )
            whole_window_validator.assert_called_once_with(
                chain["runs_root_path"],
                set(chain["expected_ids"]),
                evaluation_basis_sha256=json.loads(
                    chain["whole_window_verdict_path"].read_text(encoding="utf-8")
                )["evaluation_basis"]["sha256"],
                consumption_semantics_id=(
                    whole_window.MINTED_CONSUMPTION_SEMANTICS_ID
                ),
            )

    def test_f1_path_chain_rebindings_fail_before_whole_window_replay(self) -> None:
        cases = (
            "verdict_digest",
            "plan_tree_digest",
            "plan_tree_binding",
            "duplicate_log_row",
            "missing_log_row",
            "bundle_census",
            "malformed_bundle_id",
            "manifest_binding",
            "symlink_source",
            "wrong_v5_revision",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                chain = _install_before_chain(
                    Path(tmp), wrong_revision=case == "wrong_v5_revision"
                )
                if case == "verdict_digest":
                    chain["whole_window_verdict_sha256"] = "0" * 64
                elif case == "plan_tree_digest":
                    chain["plan_tree_sha256"] = "0" * 64
                elif case == "plan_tree_binding":
                    tree = json.loads(
                        chain["plan_tree_path"].read_text(encoding="utf-8")
                    )
                    tree["downstream_contract"]["analysis_manifest_sha256"] = (
                        "0" * 64
                    )
                    tree_raw = _file_json_bytes(tree)
                    chain["plan_tree_path"].write_bytes(tree_raw)
                    chain["plan_tree_sha256"] = hashlib.sha256(
                        tree_raw
                    ).hexdigest()
                elif case == "duplicate_log_row":
                    _rewrite_verdict(chain, lambda _row: None, occurrences=2)
                elif case == "missing_log_row":
                    _rewrite_verdict(chain, lambda _row: None, occurrences=0)
                elif case == "bundle_census":
                    def remove_member(row):
                        removed = row["bundle_ids"].pop()
                        basis = row["evaluation_basis"]
                        basis["member_occurrences"] = [
                            occurrence
                            for occurrence in basis["member_occurrences"]
                            if occurrence["bundle_id"] != removed
                        ]
                        basis["sha256"] = whole_window.canonical_sha256(
                            {key: value for key, value in basis.items() if key != "sha256"}
                        )
                        row["row_provenance"]["membership_sha256"] = (
                            whole_window.canonical_sha256(sorted(row["bundle_ids"]))
                        )

                    _rewrite_verdict(chain, remove_member)
                elif case == "malformed_bundle_id":
                    _rewrite_verdict(
                        chain,
                        lambda row: row["bundle_ids"].__setitem__(0, []),
                    )
                elif case == "manifest_binding":
                    row = json.loads(
                        chain["whole_window_verdict_path"].read_text(
                            encoding="utf-8"
                        )
                    )
                    descriptor = row["source_campaign_manifests"][0]
                    source_path = chain["runs_root_path"] / descriptor["path"]
                    source = json.loads(source_path.read_text(encoding="utf-8"))
                    source["analysis_manifest_id"] = "am-" + "0" * 64
                    source_raw = _file_json_bytes(source)
                    source_path.write_bytes(source_raw)
                    source_sha = hashlib.sha256(source_raw).hexdigest()

                    def rebind_descriptor(value):
                        value["source_campaign_manifests"][0]["sha256"] = source_sha
                        value["row_provenance"]["source_campaign_manifests"][0][
                            "sha256"
                        ] = source_sha

                    _rewrite_verdict(chain, rebind_descriptor)
                elif case == "symlink_source":
                    link = chain["runs_root_path"] / "verdict-link.json"
                    link.symlink_to(chain["whole_window_verdict_path"])
                    chain["whole_window_verdict_path"] = link

                with mock.patch(
                    "joulewise.whole_window.whole_window_refusal_reasons",
                    return_value=("whole_window_neg8_verdict_failed",),
                ) as validator:
                    rendered = renderer.render_outcome_fills(
                        None, **_before_kwargs(chain)
                    )
                expected = {
                    "OB-01": renderer.STOP_FILL,
                    "OR-01": renderer.STOP_FILL,
                }
                if case == "wrong_v5_revision":
                    expected["_stop_reason"] = renderer.IDENTITY_NOT_V5
                self.assertEqual(rendered, expected)
                validator.assert_not_called()

    def test_f1_caller_result_and_normalized_byte_channels_are_removed(self) -> None:
        parameters = inspect.signature(renderer.render_outcome_fills).parameters
        self.assertNotIn("before_comparison_source_bytes", parameters)
        self.assertNotIn("before_comparison_validator_results", parameters)
        self.assertFalse(hasattr(renderer, "BeforeComparisonValidationResult"))

    def test_f2_registered_stage_order_has_no_precedence_channel(self) -> None:
        parameters = inspect.signature(renderer.render_outcome_fills).parameters
        self.assertNotIn("precedence", parameters)
        self.assertNotIn("before_comparison_stops", parameters)

        close_fixture = _fixture("closeout_refusal")
        self.assertEqual(
            _render(close_fixture)["OR-01"], close_fixture["expected"]["OR-01"]
        )

        with tempfile.TemporaryDirectory() as tmp:
            chain = _install_before_chain(Path(tmp))
            closeout, manifest, floor, sidecar = _built_sources("closeout_refusal")
            with mock.patch(
                "joulewise.whole_window.whole_window_refusal_reasons",
                return_value=("whole_window_neg8_verdict_failed",),
            ):
                rendered = renderer.render_outcome_fills(
                    closeout,
                    finalized_manifest_bytes=manifest,
                    floor_artifact_bytes=floor,
                    replay_sidecar_bytes=sidecar,
                    **_before_kwargs(chain),
                )
            self.assertEqual(rendered["OR-01"], renderer.STOP_FILL)
            self.assertEqual(
                rendered["_secondary_closeout_reason"],
                "dominance_ratio_zero_denominator",
            )

    def test_f3_top_level_closeout_reason_renders_without_matching_ratio(self) -> None:
        cases = {
            "source_refusal": (
                "floor_artifact_source_hash_mismatch",
                "closeout_source",
            ),
            "census_refusal": (
                "replay_sidecar.cells: cell census does not match floor artifact",
                "closeout_census",
            ),
        }
        for builder, (reason, oracle) in cases.items():
            with self.subTest(builder=builder):
                closeout, manifest, floor, sidecar = _built_sources(builder)
                self.assertEqual(closeout["refusal_reason"], reason)
                statuses = [
                    record["status"]
                    for key in (
                        "independent_ratios",
                        "comparative_common_mode_ratios",
                    )
                    for record in closeout[key]
                ]
                self.assertEqual(
                    all(status == "complete" for status in statuses),
                    builder == "source_refusal",
                )
                rendered = renderer.render_outcome_fills(
                    closeout,
                    finalized_manifest_bytes=manifest,
                    floor_artifact_bytes=floor,
                    replay_sidecar_bytes=sidecar,
                )
                self.assertEqual(rendered["OR-01"], _registry_oracle(oracle))

    def test_f4_v5_identity_gate_precedes_every_fill(self) -> None:
        fixture = _fixture("branch_b")
        rendered = _render(fixture, v5_identity=False)
        self.assertEqual(
            {key: rendered[key] for key in FILL_KEYS},
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
        )
        self.assertEqual(rendered["_stop_reason"], "identity_not_v5")

        _, manifest, _, _ = _built_sources("branch_a")
        identities = {
            (
                arm["realized_stack_identity"]["model"]["name"],
                arm["realized_stack_identity"]["model"]["revision"],
            )
            for arm in json.loads(manifest)["arms"]
        }
        self.assertEqual(
            identities,
            {(value["name"], value["revision"]) for value in QWEN3.values()},
        )

        closeout, manifest, floor, sidecar = _built_sources("branch_b")
        wrong_revision_manifest = json.loads(manifest)
        wrong_revision_manifest["arms"][0]["realized_stack_identity"]["model"][
            "revision"
        ] = "0" * 40
        wrong_revision_manifest["manifest_id"] = calculate_manifest_id(
            wrong_revision_manifest
        )
        wrong_manifest_bytes = _file_json_bytes(wrong_revision_manifest)
        wrong_closeout = d165_fixtures.build_d165_dominance_closeout(
            wrong_manifest_bytes, floor, sidecar
        )
        self.assertEqual(
            core.validate_d165_closeout(
                wrong_closeout,
                finalized_manifest_bytes=wrong_manifest_bytes,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
            ),
            [],
        )
        wrong_revision_rendered = renderer.render_outcome_fills(
            wrong_closeout,
            finalized_manifest_bytes=wrong_manifest_bytes,
            floor_artifact_bytes=floor,
            replay_sidecar_bytes=sidecar,
        )
        self.assertEqual(wrong_revision_rendered["_stop_reason"], "identity_not_v5")

    def test_existing_fail_closed_guards_remain_biting(self) -> None:
        stopped = {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL}
        closeout, manifest, floor, sidecar = _built_sources("branch_a")
        incomplete = copy.deepcopy(closeout)
        incomplete["independent_ratios"].pop()
        self.assertEqual(
            renderer.render_outcome_fills(
                incomplete,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
            ),
            stopped,
            "deleting one A-fixture census entry must flip the entire result",
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                closeout,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor + b" ",
                replay_sidecar_bytes=sidecar,
            ),
            stopped,
            "a close-out whose source bytes do not authenticate must stop",
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                closeout,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
                runs_root_path=Path("/unbound-partial-before-input"),
            ),
            stopped,
            "a partial path-and-digest chain must not fall through to close-out",
        )


if __name__ == "__main__":
    unittest.main()
