from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.analysis_engine.inputs import (
    load_manifest,
    realized_scientific_identity,
)
from joulewise.analysis_manifest_v3 import (
    ARM_FREEZE,
    ESTIMATOR_ID,
    EXACT_STACK_RULE_ID,
    FLOOR_RULE_ID,
    GOVERNED_TRANSPORT_RULE_ID,
    SCHEMA_VERSION,
    FINALIZATION_CONTRACT_ID,
    FINALIZED_BASENAME_SUFFIX,
    FINALIZED_NAMESPACE_RULE_ID,
    PROSPECTIVE_SCHEMA_VERSION,
    PROSPECTIVE_INTERNAL_ERROR_CODE,
    PROSPECTIVE_MALFORMED_VALUE_CODE,
    PROSPECTIVE_DOMINANCE_REPLAY_ATTACHMENT_MISSING,
    PROSPECTIVE_REFUSAL_CODES,
    SEMANTICS_PROJECTION_RULE_ID,
    _ATTACHMENT_DECLARATION_KEYS,
    _BRACKET_BINDING_SCHEMA,
    _FLOOR_SCHEMA,
    _LEDGER_SCHEMA,
    _REQUIRED_ATTACHMENT_ROLES,
    _WHOLE_WINDOW_SCHEMA,
    analysis_semantics_sha256_v1,
    build_analysis_manifest_v3,
    build_prospective_analysis_manifest_v3,
    calculate_manifest_id,
    normalized_realized_stack_identity,
    prospective_finalization_required_attachments,
    render_manifest,
    validate_analysis_manifest_v3,
    validate_prospective_analysis_manifest_v3,
)


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_DIR = ROOT / "configs" / "campaigns" / "splitwise_decode_v1"
MANIFEST_PATH = CAMPAIGN_DIR / "analysis_manifest_v3.json"
GAMMA_DIR = (
    ROOT
    / "configs"
    / "campaigns"
    / "d117_contrast_qwen25_1p5b_vs_7b_v1"
)
V1_MODULE = ROOT / "joulewise" / "analysis_manifest.py"
V1_MODULE_SHA256 = (
    "5b4ba3ff4962bb9941c64a7f7acad98e6128119c5b4b93ad686e104a746e8cc9"
)


def reidentify(manifest: dict) -> dict:
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    return manifest


def independent_prospective_semantics(value: dict) -> dict:
    """Test-only projection spelled independently of production code."""

    return {
        "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
        "design": copy.deepcopy(value["design"]),
        "replacement_policy": copy.deepcopy(value["replacement_policy"]),
        "condition_families": copy.deepcopy(value["condition_families"]),
        "families": copy.deepcopy(value["families"]),
        "contrasts": copy.deepcopy(value["contrasts"]),
        "required_attachments": copy.deepcopy(
            value["finalization_contract"]["required_attachments"]
        ),
    }


def independent_semantics_sha256(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            independent_prospective_semantics(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def install_synthetic_prospective_fixture(
    root: Path,
    *,
    shared_family: bool = False,
    transport_mode: str = "exact_stack_only",
    runtime_backend: str = "mlx",
    telemetry_backend: str = "powermetrics",
    floor_cells_by_slot: dict[tuple[str, str], dict] | None = None,
    dominance_criterion: dict | None = None,
) -> tuple[Path, Path, dict]:
    """Install a resolved, shape-true gamma declaration in temporary custody.

    Both the default two-m=1 shape and the optional shared-m=2 shape are
    synthetic engine fixtures, not a production multiplicity ruling.  The
    checked-in unresolved pack remains untouched.
    """

    campaign = Path(root) / "pack"
    shutil.copytree(GAMMA_DIR, campaign)
    draft = json.loads((campaign / "analysis_manifest_v3.json").read_text())
    if runtime_backend != "mlx" or telemetry_backend != "powermetrics":
        config_sha256_by_path: dict[str, str] = {}
        for source in draft["contrasts"]:
            for member in source["members"]:
                relative = member["config"]
                config_path = campaign / relative
                config = json.loads(config_path.read_text())
                config["hardware_target"]["runtime_backend"] = runtime_backend
                config["hardware_target"]["telemetry_backend"] = telemetry_backend
                raw = (json.dumps(config, indent=2) + "\n").encode()
                config_path.write_bytes(raw)
                digest = hashlib.sha256(raw).hexdigest()
                member["config_sha256"] = digest
                config_sha256_by_path[relative] = digest

        stage_sha256_by_path: dict[str, str] = {}
        for stage in draft["stage_manifests"]:
            stage_relative = stage["manifest_path"]
            stage_path = campaign / stage_relative
            stage_manifest = json.loads(stage_path.read_text())
            stage_root = Path(stage_relative).parent
            for row in stage_manifest["executed_order"]:
                config_relative = (stage_root / row["config"]).as_posix()
                row["config_sha256"] = config_sha256_by_path[config_relative]
            stage_raw = (json.dumps(stage_manifest, indent=2) + "\n").encode()
            stage_path.write_bytes(stage_raw)
            digest = hashlib.sha256(stage_raw).hexdigest()
            stage["manifest_sha256"] = digest
            stage_sha256_by_path[stage_relative] = digest

        root_order_path = campaign / draft["root_order_manifest"]["path"]
        root_order = json.loads(root_order_path.read_text())
        for row in root_order["executed_order"]:
            row["config_sha256"] = config_sha256_by_path[row["config"]]
        for row in root_order["subcampaign_order"]:
            row["manifest_sha256"] = stage_sha256_by_path[row["manifest_path"]]
        root_order_raw = (json.dumps(root_order, indent=2) + "\n").encode()
        root_order_path.write_bytes(root_order_raw)
        draft["root_order_manifest"]["sha256"] = hashlib.sha256(
            root_order_raw
        ).hexdigest()
    if floor_cells_by_slot is not None:
        for condition in draft["condition_families"]:
            slot = (condition["measurement_arm"], condition["arm"])
            floor_cell = floor_cells_by_slot[slot]
            definition = copy.deepcopy(
                floor_cell["key"]["condition_family_definition"]
            )
            raw = (json.dumps(definition, indent=2, sort_keys=True) + "\n").encode()
            (campaign / condition["path"]).write_bytes(raw)
            condition.update(
                {
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "condition_family_id": floor_cell["key"][
                        "condition_family_id"
                    ],
                    "canonical_domain_sha256": floor_cell["key"][
                        "condition_family_sha256"
                    ],
                }
            )
        for source in draft["contrasts"]:
            measurement_arm = source["measurement_arm"]
            source["condition_a_id"] = floor_cells_by_slot[
                (measurement_arm, "A")
            ]["key"]["condition_family_id"]
            source["condition_b_id"] = floor_cells_by_slot[
                (measurement_arm, "B")
            ]["key"]["condition_family_id"]
    if dominance_criterion is not None:
        for source in draft["contrasts"]:
            source["floor_estimator_registration"] = {
                **copy.deepcopy(source["floor_estimator_registration"]),
                "dominance_criterion": copy.deepcopy(dominance_criterion),
            }
    families = []
    contrasts = []
    for index, source in enumerate(draft["contrasts"]):
        contrast_id = source["contrast_id"]
        family_id = f"synthetic-family-{source['measurement_arm']}"
        metric_tag = (
            "phase_decode_energy"
            if source["measurement_arm"] == "decode"
            else "phase_prefill_p256_energy"
        )
        families.append(
            {
                "family_id": family_id,
                "family_instance_id": family_id,
                "plan_id": draft["plan"]["plan_id"],
                "claim_role": "primary",
                "metric_tag": metric_tag,
                "multiplicity": {
                    "method": "holm",
                    "alpha": 0.05,
                    "q": None,
                    "m": 1,
                },
                "contrast_ids": [contrast_id],
            }
        )
        transport_rule = (
            EXACT_STACK_RULE_ID
            if transport_mode == "exact_stack_only"
            else GOVERNED_TRANSPORT_RULE_ID
        )
        selector = {
            "backend": "from_bundle",
            "metric": source["metric"],
            "window_class": "phase",
            "condition_family_ids": [
                source["condition_a_id"],
                source["condition_b_id"],
            ],
            "floor_field": "floor_gate_j",
            "transport_rule_id": transport_rule,
            "claim_floor_rule": "cross_stack_armwise_max.v1",
        }
        contrasts.append(
            {
                "contrast_id": contrast_id,
                "measurement_arm": source["measurement_arm"],
                "metric": source["metric"],
                "metric_tag": metric_tag,
                "target_precheck_path": source["target_precheck_path"],
                "condition_a_id": source["condition_a_id"],
                "condition_b_id": source["condition_b_id"],
                "difference_orientation": source["difference_orientation"],
                "point_estimator": source["point_estimator"],
                "floor_estimator_registration": source[
                    "floor_estimator_registration"
                ],
                "block_ids": source["block_ids"],
                "members": source["members"],
                "family_instance_id": family_id,
                "claim_role": "primary",
                "test": "two_sided",
                "scientific_hypothesis_direction": "positive",
                "equivalence": None,
                "mde": None,
                "floor_dependency": {
                    "required_artifact_schema": (
                        "joulewise.detection_floor_artifact.v2"
                    ),
                    "floor_selector": selector,
                    "transport": {
                        "mode": transport_mode,
                        "rule_id": transport_rule,
                        "transport_groups": [
                            {
                                "transport_group_id": (
                                    floor_cells_by_slot[
                                        (source["measurement_arm"], arm)
                                    ]["transport_group_id"]
                                    if floor_cells_by_slot is not None
                                    else "synthetic-floor-group-"
                                    f"{source['measurement_arm']}-{arm.lower()}"
                                ),
                                "condition_family_id": condition_id,
                                "condition_domain_sha256": next(
                                    row["canonical_domain_sha256"]
                                    for row in draft["condition_families"]
                                    if row["condition_family_id"] == condition_id
                                ),
                                "group_rule_id": GOVERNED_TRANSPORT_RULE_ID,
                            }
                            for arm, condition_id in zip(
                                ("A", "B"),
                                (
                                    source["condition_a_id"],
                                    source["condition_b_id"],
                                ),
                                strict=True,
                            )
                        ],
                    },
                },
                "prompt": (
                    None
                    if index == 0
                    else {
                        "path": source["prompt_candidate"]["path"],
                        "sha256": source["prompt_candidate"]["sha256"],
                        "status": "synthetic_fixture_ratified",
                    }
                ),
            }
        )
    if shared_family:
        family_id = "synthetic-shared-cross-arm-family"
        families = [
            {
                "family_id": family_id,
                "family_instance_id": family_id,
                "plan_id": draft["plan"]["plan_id"],
                "claim_role": "primary",
                "metric_tag": "synthetic_cross_arm_energy",
                "multiplicity": {
                    "method": "holm",
                    "alpha": 0.05,
                    "q": None,
                    "m": 2,
                },
                "contrast_ids": [
                    contrast["contrast_id"] for contrast in contrasts
                ],
            }
        ]
        for contrast in contrasts:
            contrast["family_instance_id"] = family_id
    prospective = {
        "schema_version": PROSPECTIVE_SCHEMA_VERSION,
        "manifest_id": "",
        "freeze_status": "frozen",
        "plan": draft["plan"],
        "root_order_manifest": draft["root_order_manifest"],
        "stage_manifests": draft["stage_manifests"],
        "evidence_root_id": draft["evidence_root_id"],
        "condition_families": draft["condition_families"],
        "design": {
            "design_id": "synthetic-d117-two-contrast-abba-v1",
            "analysis_type": "comparative_contrast",
            "null_alias": False,
            "unit_of_analysis": "abba_block_arm_mean_difference",
            "difference_orientation": "condition_b_minus_condition_a",
            "sampling_plan": {
                "design": "fixed_n",
                "planned_n_blocks": 10,
                "freeze_basis": "frozen_before_measurement",
                "allowed_replacement_reasons": [],
            },
            "randomization": {
                "scheme": "deterministic_abba",
                "exchangeability": "none",
                "seed": None,
            },
        },
        "replacement_policy": {
            "outcome_dependent_top_up": "forbidden",
            "science_member_replacements": 0,
            "allowed_replacement_reasons": [],
        },
        "families": families,
        "contrasts": contrasts,
        "finalization_contract": {
            "contract_id": FINALIZATION_CONTRACT_ID,
            "projection_rule_id": SEMANTICS_PROJECTION_RULE_ID,
            "namespace_rule_id": FINALIZED_NAMESPACE_RULE_ID,
            "output_basename_suffix": FINALIZED_BASENAME_SUFFIX,
            "required_attachments": prospective_finalization_required_attachments(
                optional_roles=(
                    ("dominance_replay_sidecar",)
                    if dominance_criterion is not None
                    else ()
                )
            ),
        },
        "frozen_semantics_sha256": "",
    }
    prospective["frozen_semantics_sha256"] = independent_semantics_sha256(
        prospective
    )
    prospective["manifest_id"] = calculate_manifest_id(prospective)
    manifest_path = campaign / "analysis_manifest_v3.json"
    manifest_path.write_bytes(render_manifest(prospective))
    plan_tree = {
        "schema_version": "joulewise.d117_plan_tree.v1",
        "plan": {
            "plan_id": prospective["plan"]["plan_id"],
            "actual_sha256": prospective["plan"]["sha256"],
            "declared_sha256": prospective["plan"]["sha256"],
        },
        "downstream_contract": {
            "analysis_manifest_path": "analysis_manifest_v3.json",
            "analysis_manifest_sha256": hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
        },
    }
    plan_tree_path = campaign / "synthetic_plan_tree.json"
    plan_tree_path.write_text(json.dumps(plan_tree, indent=2) + "\n")
    return manifest_path, plan_tree_path, prospective


def authenticate_prospective_fixture(
    manifest_path: Path, plan_tree_path: Path, prospective: dict
) -> None:
    prospective["frozen_semantics_sha256"] = independent_semantics_sha256(
        prospective
    )
    reidentify(prospective)
    manifest_path.write_bytes(render_manifest(prospective))
    plan_tree = json.loads(plan_tree_path.read_text())
    plan_tree["downstream_contract"]["analysis_manifest_sha256"] = hashlib.sha256(
        manifest_path.read_bytes()
    ).hexdigest()
    plan_tree_path.write_text(json.dumps(plan_tree, indent=2) + "\n")


def retarget_prospective_prefill_arm(prospective: dict, prefill_arm: str) -> None:
    for condition in prospective["condition_families"]:
        if condition["measurement_arm"] != "decode":
            condition["measurement_arm"] = prefill_arm
    prefill_contrast_id = None
    for contrast in prospective["contrasts"]:
        if contrast["measurement_arm"] != "decode":
            contrast["measurement_arm"] = prefill_arm
            contrast["metric_tag"] = f"phase_{prefill_arm}_energy"
            prefill_contrast_id = contrast["contrast_id"]
    for family in prospective["families"]:
        if prefill_contrast_id in family["contrast_ids"]:
            family["metric_tag"] = f"phase_{prefill_arm}_energy"


class AnalysisManifestV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_generated_manifest_is_source_linked_and_byte_idempotent(self) -> None:
        self.assertEqual(
            validate_analysis_manifest_v3(
                self.manifest,
                manifest_dir=CAMPAIGN_DIR,
            ),
            [],
        )
        rebuilt = build_analysis_manifest_v3(CAMPAIGN_DIR)
        self.assertEqual(rebuilt, self.manifest)
        self.assertEqual(render_manifest(rebuilt), MANIFEST_PATH.read_bytes())

        loaded, digest = load_manifest(MANIFEST_PATH)
        self.assertEqual(loaded, self.manifest)
        self.assertEqual(digest, hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest())

    def test_v1_validator_module_remains_byte_identical(self) -> None:
        self.assertEqual(hashlib.sha256(V1_MODULE.read_bytes()).hexdigest(), V1_MODULE_SHA256)

    def test_ratified_freeze_and_refusal_edges(self) -> None:
        mutations = {
            "analysis_type": lambda value: value["design"].__setitem__(
                "analysis_type", "single_condition"
            ),
            "null_alias": lambda value: value["design"].__setitem__("null_alias", True),
            "n": lambda value: value["design"]["sampling_plan"].__setitem__(
                "planned_n_blocks", 9
            ),
            "orientation": lambda value: value["design"].__setitem__(
                "difference_orientation", "condition_a_minus_condition_b"
            ),
            "verdict_basis": lambda value: value["source"][
                "authenticated_verdict_basis"
            ].__setitem__("evaluation_basis_sha256", "0" * 64),
            "stage_order": lambda value: value["source"][
                "stage_order_manifests"
            ][0].__setitem__("sha256", "0" * 64),
            "family_hash": lambda value: value["arms"][0].__setitem__(
                "condition_family_sha256", "0" * 64
            ),
            "estimator": lambda value: value["contrasts"][0].__setitem__(
                "estimator", "paired_t_v1"
            ),
            "holm_m": lambda value: value["families"][0]["multiplicity"].__setitem__(
                "m", 2
            ),
            "negative_hypothesis": lambda value: value["contrasts"][0].__setitem__(
                "hypothesized_direction", "negative"
            ),
            "equivalence": lambda value: value["contrasts"][0].__setitem__(
                "equivalence", {"margin": 1.0, "method": "tost_v1"}
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                candidate = copy.deepcopy(self.manifest)
                mutate(candidate)
                reidentify(candidate)
                self.assertTrue(validate_analysis_manifest_v3(candidate))

        contrast = self.manifest["contrasts"][0]
        self.assertEqual(contrast["estimator"], ESTIMATOR_ID)
        self.assertEqual(
            contrast["floor_selector"]["claim_floor_rule"], FLOOR_RULE_ID
        )
        self.assertEqual(contrast["hypothesized_direction"], "positive")
        self.assertIsNone(contrast["equivalence"])
        self.assertIsNone(contrast["mde"])

    def test_legacy_v3_arms_refuse_each_floor_identity_key(self) -> None:
        for key, value in (
            ("floor_cell_id", "cell-forbidden-on-prospective"),
            ("floor_stack_identity", {}),
        ):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.manifest)
                candidate["arms"][0][key] = value
                reidentify(candidate)
                errors = validate_analysis_manifest_v3(
                    candidate,
                    manifest_dir=CAMPAIGN_DIR,
                )
                self.assertTrue(errors)
                self.assertTrue(
                    any("manifest.arms[0]" in error for error in errors)
                )

    def test_every_physical_position_is_consumed_once(self) -> None:
        consumed = [
            entry_id
            for block in self.manifest["blocks"]
            for entry_id in block["position_entry_ids"].values()
        ]
        self.assertEqual(len(consumed), 40)
        self.assertEqual(len(set(consumed)), 40)
        self.assertEqual(set(consumed), {row["entry_id"] for row in self.manifest["entries"]})

        duplicate = copy.deepcopy(self.manifest)
        duplicate["blocks"][1]["position_entry_ids"]["A1"] = duplicate["blocks"][0][
            "position_entry_ids"
        ]["A1"]
        reidentify(duplicate)
        errors = validate_analysis_manifest_v3(duplicate)
        self.assertTrue(any("consumed exactly once" in error for error in errors))

        noncontiguous = copy.deepcopy(self.manifest)
        noncontiguous["blocks"][1]["block_number"] = 3
        reidentify(noncontiguous)
        errors = validate_analysis_manifest_v3(noncontiguous)
        self.assertTrue(any("not contiguous" in error for error in errors))

    def test_real_mlx_metadata_file_set_folded_sha256_normalizes(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "d078_r01"
        raw_config = json.loads(
            (fixture / "config.json").read_text(encoding="utf-8")
        )
        metadata = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        artifact = metadata["workload_provenance"]["model"][
            "artifact_identity"
        ]
        self.assertEqual(artifact["kind"], "file_set")
        self.assertNotIn("sha256", artifact)

        realized = realized_scientific_identity(raw_config, metadata)
        self.assertIsNotNone(realized)
        self.assertEqual(realized["model_artifact"]["sha256"], artifact["folded_sha256"])
        self.assertEqual(
            normalized_realized_stack_identity(realized),
            normalized_realized_stack_identity(
                ARM_FREEZE["A"]["realized_stack_identity"]
            ),
        )

        file_identity = copy.deepcopy(realized)
        file_identity["model_artifact"] = {
            "algorithm": "sha256",
            "kind": "file",
            "sha256": artifact["folded_sha256"],
        }
        normalized_file = normalized_realized_stack_identity(file_identity)
        self.assertEqual(
            normalized_file["model_artifact"]["digest_sha256"],
            artifact["folded_sha256"],
        )

        invalid = copy.deepcopy(ARM_FREEZE["A"]["realized_stack_identity"])
        invalid["model_artifact"]["folded_sha256"] = "not-a-digest"
        self.assertIsNone(normalized_realized_stack_identity(invalid))

    def test_schema_is_v3_sibling_not_v1_alias(self) -> None:
        self.assertEqual(self.manifest["schema_version"], SCHEMA_VERSION)
        self.assertNotEqual(SCHEMA_VERSION, "joulewise.analysis_manifest.v1")
        self.assertNotEqual(SCHEMA_VERSION, "joulewise.analysis_manifest.v2")

    def test_resolved_prospective_schema_is_deterministic_and_source_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first_path, first_tree, first = (
                install_synthetic_prospective_fixture(Path(tmp) / "first")
            )
            second_path, second_tree, second = (
                install_synthetic_prospective_fixture(Path(tmp) / "second")
            )
            self.assertEqual(
                validate_prospective_analysis_manifest_v3(
                    first,
                    manifest_dir=first_path.parent,
                    plan_tree_path=first_tree,
                ),
                (),
            )
            self.assertEqual(first, second)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertEqual(first_tree.read_bytes(), second_tree.read_bytes())
            self.assertEqual(
                analysis_semantics_sha256_v1(first),
                independent_semantics_sha256(first),
            )
            self.assertEqual(
                build_prospective_analysis_manifest_v3(
                    first_path.parent, plan_tree_path=first_tree
                ),
                first,
            )

    def test_prospective_accepts_legacy_and_each_ruled_prefill_arm(self) -> None:
        for prefill_arm in (
            "prefill_p256",
            "prefill_p512",
            "prefill_p1024",
            "prefill_p2048",
            "prefill_p4096",
        ):
            with self.subTest(prefill_arm=prefill_arm), tempfile.TemporaryDirectory() as tmp:
                manifest_path, plan_tree_path, prospective = (
                    install_synthetic_prospective_fixture(Path(tmp))
                )
                retarget_prospective_prefill_arm(prospective, prefill_arm)
                authenticate_prospective_fixture(
                    manifest_path, plan_tree_path, prospective
                )
                self.assertEqual(
                    validate_prospective_analysis_manifest_v3(
                        prospective,
                        manifest_dir=manifest_path.parent,
                        plan_tree_path=plan_tree_path,
                    ),
                    (),
                )

    def test_prospective_refuses_mixed_or_unsupported_prefill_arms(self) -> None:
        cases = ("mixed_condition_slots", "contrast_disagrees", "unsupported")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                manifest_path, plan_tree_path, prospective = (
                    install_synthetic_prospective_fixture(Path(tmp))
                )
                prefill_conditions = [
                    condition
                    for condition in prospective["condition_families"]
                    if condition["measurement_arm"] != "decode"
                ]
                prefill_contrast = next(
                    contrast
                    for contrast in prospective["contrasts"]
                    if contrast["measurement_arm"] != "decode"
                )
                if case == "mixed_condition_slots":
                    prefill_conditions[0]["measurement_arm"] = "prefill_p4096"
                    prefill_conditions[1]["measurement_arm"] = "prefill_p1024"
                elif case == "contrast_disagrees":
                    for condition in prefill_conditions:
                        condition["measurement_arm"] = "prefill_p4096"
                    prefill_contrast["measurement_arm"] = "prefill_p1024"
                else:
                    for condition in prefill_conditions:
                        condition["measurement_arm"] = "prefill_p768"
                    prefill_contrast["measurement_arm"] = "prefill_p768"
                authenticate_prospective_fixture(
                    manifest_path, plan_tree_path, prospective
                )
                refusals = validate_prospective_analysis_manifest_v3(
                    prospective,
                    manifest_dir=manifest_path.parent,
                    plan_tree_path=plan_tree_path,
                )
                self.assertTrue(refusals)
                self.assertIn(
                    "analysis_prospective_contrast_cover_mismatch",
                    {refusal.reason_code for refusal in refusals},
                )

    def test_prospective_transport_and_multiplicity_boundaries_are_total(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(root / "exact")
            )
            transported_path, transported_tree, transported = (
                install_synthetic_prospective_fixture(
                    root / "transported",
                    transport_mode="governed_transport",
                )
            )
            self.assertEqual(
                validate_prospective_analysis_manifest_v3(
                    transported,
                    manifest_dir=transported_path.parent,
                    plan_tree_path=transported_tree,
                ),
                (),
            )

            for method, alpha, q in (
                ("benjamini_hochberg", None, 0.05),
                ("exploratory_none", None, None),
            ):
                with self.subTest(valid_method=method):
                    valid = copy.deepcopy(prospective)
                    for family in valid["families"]:
                        family["multiplicity"].update(
                            method=method,
                            alpha=alpha,
                            q=q,
                        )
                    valid["frozen_semantics_sha256"] = (
                        independent_semantics_sha256(valid)
                    )
                    reidentify(valid)
                    manifest_path.write_bytes(render_manifest(valid))
                    tree = json.loads(plan_tree_path.read_text())
                    tree["downstream_contract"]["analysis_manifest_sha256"] = (
                        hashlib.sha256(manifest_path.read_bytes()).hexdigest()
                    )
                    plan_tree_path.write_text(json.dumps(tree, indent=2) + "\n")
                    self.assertEqual(
                        validate_prospective_analysis_manifest_v3(
                            valid,
                            manifest_dir=manifest_path.parent,
                            plan_tree_path=plan_tree_path,
                        ),
                        (),
                    )

            manifest_path.write_bytes(render_manifest(prospective))
            tree = json.loads(plan_tree_path.read_text())
            tree["downstream_contract"]["analysis_manifest_sha256"] = (
                hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            )
            plan_tree_path.write_text(json.dumps(tree, indent=2) + "\n")

            mutations = {
                "backend": lambda value: value["contrasts"][0][
                    "floor_dependency"
                ]["floor_selector"].__setitem__("backend", "mock"),
                "floor_field": lambda value: value["contrasts"][0][
                    "floor_dependency"
                ]["floor_selector"].__setitem__("floor_field", "floor_abs_j"),
                "claim_rule": lambda value: value["contrasts"][0][
                    "floor_dependency"
                ]["floor_selector"].__setitem__("claim_floor_rule", "max.v0"),
                "condition_domain": lambda value: value["contrasts"][0][
                    "floor_dependency"
                ]["transport"]["transport_groups"][0].__setitem__(
                    "condition_domain_sha256", "0" * 64
                ),
                "holm_q": lambda value: value["families"][0][
                    "multiplicity"
                ].__setitem__("q", 0.05),
                "bh_alpha": lambda value: value["families"][0][
                    "multiplicity"
                ].update(
                    method="benjamini_hochberg", alpha=0.05, q=0.05
                ),
                "exploratory_alpha": lambda value: value["families"][0][
                    "multiplicity"
                ].update(method="exploratory_none", alpha=0.05, q=None),
            }
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    candidate = copy.deepcopy(prospective)
                    mutate(candidate)
                    candidate["frozen_semantics_sha256"] = (
                        independent_semantics_sha256(candidate)
                    )
                    reidentify(candidate)
                    reasons = validate_prospective_analysis_manifest_v3(
                        candidate,
                        manifest_dir=manifest_path.parent,
                        plan_tree_path=plan_tree_path,
                    )
                    self.assertTrue(reasons)
                    self.assertTrue(
                        all(
                            reason.reason_code.startswith("analysis_")
                            for reason in reasons
                        )
                    )

            fuzzed = copy.deepcopy(prospective)
            fuzzed["families"][0]["contrast_ids"] = [{}]
            refusals = validate_prospective_analysis_manifest_v3(
                fuzzed,
                manifest_dir=manifest_path.parent,
                plan_tree_path=plan_tree_path,
            )
            self.assertTrue(refusals)
            self.assertTrue(
                all(item.reason_code.startswith("analysis_") for item in refusals)
            )

    def test_prospective_boundary_maps_wrong_typed_sites_to_closed_vocabulary(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(Path(tmp))
            )
            cases = {
                "top_level_list": [],
                "top_level_integer": 7,
                "top_level_none": None,
                "top_level_bool": False,
                "top_level_bytes": b"not-json",
                "plan": {**prospective, "plan": 7},
                "root_order_manifest": {
                    **prospective,
                    "root_order_manifest": 7,
                },
                "stage_manifests": {**prospective, "stage_manifests": 7},
                "condition_families": {
                    **prospective,
                    "condition_families": 7,
                },
                "design": {**prospective, "design": 7},
                "replacement_policy": {
                    **prospective,
                    "replacement_policy": 7,
                },
                "families": {**prospective, "families": 7},
                "contrasts": {**prospective, "contrasts": 7},
                "nested_multiplicity": {
                    **prospective,
                    "families": [
                        {**prospective["families"][0], "multiplicity": None},
                        *prospective["families"][1:],
                    ],
                },
                "nested_members": {
                    **prospective,
                    "contrasts": [
                        {**prospective["contrasts"][0], "members": True},
                        *prospective["contrasts"][1:],
                    ],
                },
                "finalization_contract": {
                    **prospective,
                    "finalization_contract": 7,
                },
            }
            for label, candidate in cases.items():
                with self.subTest(label=label):
                    refusals = validate_prospective_analysis_manifest_v3(
                        candidate,
                        manifest_dir=manifest_path.parent,
                        plan_tree_path=plan_tree_path,
                    )
                    self.assertEqual(len(refusals), 1)
                    self.assertEqual(
                        refusals[0].reason_code,
                        PROSPECTIVE_MALFORMED_VALUE_CODE,
                    )
                    self.assertIn("manifest", refusals[0].detail)
                    self.assertIn("got", refusals[0].detail)
                    self.assertIsNotNone(refusals[0].cause)
                    self.assertIsInstance(refusals[0].cause.__cause__, TypeError)

            exact = validate_prospective_analysis_manifest_v3(
                [],
                manifest_dir=manifest_path.parent,
                plan_tree_path=plan_tree_path,
            )
            self.assertEqual(len(exact), 1)
            self.assertEqual(
                exact[0].reason_code,
                PROSPECTIVE_MALFORMED_VALUE_CODE,
            )
            self.assertIn("manifest", exact[0].detail)
            self.assertIn("list", exact[0].detail)

    def test_prospective_boundary_classifies_internal_helper_failures(self) -> None:
        self.assertNotEqual(
            PROSPECTIVE_MALFORMED_VALUE_CODE,
            PROSPECTIVE_INTERNAL_ERROR_CODE,
        )
        self.assertIn(PROSPECTIVE_MALFORMED_VALUE_CODE, PROSPECTIVE_REFUSAL_CODES)
        self.assertIn(PROSPECTIVE_INTERNAL_ERROR_CODE, PROSPECTIVE_REFUSAL_CODES)
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(Path(tmp))
            )
            for exception_type in (RuntimeError, TypeError):
                injected = exception_type("injected validator defect")
                with self.subTest(exception_type=exception_type.__name__), mock.patch(
                    "joulewise.analysis_manifest_v3."
                    "analysis_semantics_sha256_v1",
                    side_effect=injected,
                ):
                    refusals = validate_prospective_analysis_manifest_v3(
                        prospective,
                        manifest_dir=manifest_path.parent,
                        plan_tree_path=plan_tree_path,
                    )
                    self.assertEqual(len(refusals), 1)
                    self.assertEqual(
                        refusals[0].reason_code,
                        PROSPECTIVE_INTERNAL_ERROR_CODE,
                    )
                    self.assertNotEqual(
                        refusals[0].reason_code,
                        PROSPECTIVE_MALFORMED_VALUE_CODE,
                    )
                    self.assertIn(exception_type.__name__, refusals[0].detail)
                    self.assertIs(refusals[0].cause, injected)

    def test_whole_object_empty_slots_are_classified_as_unresolved(self) -> None:
        empty_slot = {
            "status": "EMPTY",
            "value": "",
            "todo": "restore the ruled prospective value",
        }
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(Path(tmp))
            )
            candidates = {}
            test_slot = copy.deepcopy(prospective)
            test_slot["contrasts"][0]["test"] = copy.deepcopy(empty_slot)
            candidates["test"] = test_slot
            floor_slot = copy.deepcopy(prospective)
            floor_slot["contrasts"][0]["floor_dependency"][
                "floor_selector"
            ]["backend"] = copy.deepcopy(empty_slot)
            candidates["floor_dependency_child"] = floor_slot

            for label, candidate in candidates.items():
                with self.subTest(label=label):
                    refusals = validate_prospective_analysis_manifest_v3(
                        candidate,
                        manifest_dir=manifest_path.parent,
                        plan_tree_path=plan_tree_path,
                    )
                    self.assertTrue(refusals)
                    self.assertEqual(
                        refusals[0].reason_code,
                        "analysis_prospective_unresolved_slot",
                    )
                    self.assertNotIn(
                        PROSPECTIVE_INTERNAL_ERROR_CODE,
                        {item.reason_code for item in refusals},
                    )

    def test_prospective_finalization_attachment_accessor_matches_contract(
        self,
    ) -> None:
        declarations = prospective_finalization_required_attachments()
        expected_schemas = {
            "whole_window_verdict": _WHOLE_WINDOW_SCHEMA,
            "bracket_binding": _BRACKET_BINDING_SCHEMA,
            "calibration_ledger": _LEDGER_SCHEMA,
            "aggregate_floor_artifact": _FLOOR_SCHEMA,
        }
        self.assertEqual(len(declarations), 4)
        self.assertEqual(
            {frozenset(item) for item in declarations},
            {frozenset(_ATTACHMENT_DECLARATION_KEYS)},
        )
        self.assertEqual(
            {item["role"] for item in declarations},
            _REQUIRED_ATTACHMENT_ROLES,
        )
        self.assertEqual(
            {
                item["role"]: item["schema_version"]
                for item in declarations
            },
            expected_schemas,
        )
        self.assertIsNot(
            prospective_finalization_required_attachments(), declarations
        )

    def test_prospective_attachment_accessor_adds_dominance_role_only_when_asked(
        self,
    ) -> None:
        declarations = prospective_finalization_required_attachments(
            optional_roles=("dominance_replay_sidecar",)
        )
        self.assertEqual(len(declarations), 5)
        self.assertEqual(
            declarations[-1],
            {
                "role": "dominance_replay_sidecar",
                "schema_version": "joulewise.d165_dominance_replay.v1",
            },
        )

    def test_dominance_criterion_without_attachment_is_named_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(
                    Path(tmp), dominance_criterion={"rule_id": "test-dominance"}
                )
            )
            prospective["finalization_contract"]["required_attachments"] = (
                prospective_finalization_required_attachments()
            )
            prospective["frozen_semantics_sha256"] = independent_semantics_sha256(
                prospective
            )
            reidentify(prospective)
            refusals = validate_prospective_analysis_manifest_v3(
                prospective,
                manifest_dir=manifest_path.parent,
                plan_tree_path=plan_tree_path,
            )
        named = [
            item
            for item in refusals
            if item.reason_code == PROSPECTIVE_DOMINANCE_REPLAY_ATTACHMENT_MISSING
        ]
        self.assertEqual(len(named), 1)
        self.assertEqual(
            named[0].detail,
            "every dominance-enabled prospective manifest must declare the "
            "dominance_replay_sidecar attachment role",
        )

    def test_checked_in_placeholder_manifest_is_not_a_frozen_prospective(self) -> None:
        draft = json.loads((GAMMA_DIR / "analysis_manifest_v3.json").read_text())
        refusals = validate_prospective_analysis_manifest_v3(
            draft,
            manifest_dir=GAMMA_DIR,
            plan_tree_path=GAMMA_DIR / "plan_tree.json",
        )
        reason_codes = {item.reason_code for item in refusals}
        self.assertIn("analysis_prospective_unresolved_slot", reason_codes)
        self.assertIn("analysis_prospective_unknown_key", reason_codes)
        self.assertIn("analysis_prospective_not_frozen", reason_codes)

    def test_prospective_prompt_hash_and_plan_pin_refuse_semantic_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(Path(tmp))
            )
            wrong_prompt = copy.deepcopy(prospective)
            wrong_prompt["contrasts"][1]["prompt"]["sha256"] = "0" * 64
            wrong_prompt["frozen_semantics_sha256"] = independent_semantics_sha256(
                wrong_prompt
            )
            reidentify(wrong_prompt)
            prompt_codes = {
                item.reason_code
                for item in validate_prospective_analysis_manifest_v3(
                    wrong_prompt,
                    manifest_dir=manifest_path.parent,
                    plan_tree_path=plan_tree_path,
                )
            }
            self.assertIn("analysis_prospective_source_hash_mismatch", prompt_codes)

            changed_family = copy.deepcopy(prospective)
            changed_family["families"][0]["multiplicity"]["alpha"] = 0.01
            changed_family["frozen_semantics_sha256"] = independent_semantics_sha256(
                changed_family
            )
            reidentify(changed_family)
            family_codes = {
                item.reason_code
                for item in validate_prospective_analysis_manifest_v3(
                    changed_family,
                    manifest_dir=manifest_path.parent,
                    plan_tree_path=plan_tree_path,
                )
            }
            self.assertIn("analysis_prospective_plan_tree_mismatch", family_codes)


if __name__ == "__main__":
    unittest.main()
