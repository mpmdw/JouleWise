from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from copy import deepcopy
from io import StringIO
from pathlib import Path
from unittest import mock

import joulewise.floor_extraction as floor_extraction
from joulewise.detection_floor import (
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
)
from joulewise.floor_extraction import validate_extraction_spec
from joulewise.identity_pins import (
    IDENTITY_PIN_DERIVATION_CONTRACT,
    scientific_config_identity_sha256,
)
from joulewise.receipt_oracle import derive_bracket_session_receipt_oracle
from scripts.extract_detection_floors import main as extract_main
from scripts.run_campaign import load_order_entries


REPO_ROOT = Path(__file__).resolve().parents[1]
PACK = REPO_ROOT / "configs/campaigns/d117_floor_qwen25_7b_v1"
SPEC = REPO_ROOT / "configs/floor_mint/d117_qwen25_7b_extraction_spec.json"
GENERATOR = PACK / "generate_configs.py"
OLD_PACK = REPO_ROOT / "configs/campaigns/qwen25_7b_decode_floor_v1"

PLAN_ID = "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-7b-v1"
DECODE_FAMILY_ID = "df-ph-decode-qwen25-7b"
PREFILL_FAMILY_ID = "df-ph-prefill-p128-qwen25-7b"
P256_FAMILY_ID = "df-ph-prefill-p256-qwen25-7b"
CONTRAST_PACK = REPO_ROOT / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1"
LEGACY_DECODE_PLAN_SHA256 = "c20ef596f64a4a8d5367a963614c4db0f2c34a7077441e204bcf22e2b1033f40"

EXPECTED_SHA256 = {
    "calibration_plan.json": (
        "28b1c6201fa23009635ee2773f58a7ff895e8ff2e51f79eb756f11e3fdfc60da"
    ),
    "calibration_plan.sha256": (
        "b45386966b48abff588f30dff827e4057f623fbd38108555081e776de1578e33"
    ),
    "condition_families/condition_family_df_ph_decode_qwen25_7b.json": (
        "d90b8fec2ccc74f1e982e573789a32116cda78d625ce84e72f2717926edc0cdb"
    ),
    (
        "condition_families/"
        "condition_family_df_ph_prefill_p128_qwen25_7b.json"
    ): "e896aeae5eff911dbe14d09de9ebddcafe37b20c67ba059b2a6b7f6d3a6cee25",
    (
        "condition_families/"
        "condition_family_df_ph_prefill_p256_qwen25_7b.json"
    ): "d34252b4ebe6e379c9e724688c7398b5f96ff79fbddd90ab876e23316ecd1252",
    "generate_configs.py": (
        "f19d58dda779f6680bf91422a572108ee6d6d91855693a2e135586f646c73d23"
    ),
    "01_phase_decode_absolute/order_manifest.json": (
        "7ec01725aab7ddbf82d9da743f57bda155278766a61bc5c1ebe66f468552637c"
    ),
    "02_phase_decode_abba_blocks_01_05/order_manifest.json": (
        "999b3cd03ae3bdb6c11308f60170dcaf03c3e70e7f90677324add2dc923b6aa3"
    ),
    "03_phase_decode_abba_blocks_06_10/order_manifest.json": (
        "d94d7e1905271738866c46443c88e0d5440ac950a7399d4765fd9360373860de"
    ),
    "04_phase_prefill_p256_absolute/order_manifest.json": (
        "275fb5992fe6f3384924b322efbf19cfc155187d74316c46cfc0c3e3cd1f75ba"
    ),
    "05_phase_prefill_p256_abba_blocks_01_05/order_manifest.json": (
        "4efd8fa3445044e346e9c188b591904a62ca65590a09a8989d9ae121f62d0800"
    ),
    "06_phase_prefill_p256_abba_blocks_06_10/order_manifest.json": (
        "7609811f0b24d0a4ebcf8cce715edff4857fe0733333f95aede2c998a403292c"
    ),
    "order_manifest.json": (
        "03f10c10efa03c3d7fe3463da4da7893622bf15e914956af35d67d744c81a4ea"
    ),
    "plan_tree.json": (
        "00e3a89dc0bfa9e3ce512001a0040f9e25aa96b481e79da30d05def91e770fa4"
    ),
    "plan_tree.sha256": (
        "22a3a55ee61085765a2ddf03d5690e68dd3eef1f14e902362542c69c82526cda"
    ),
    "producer_contract.json": (
        "5829349c5a0fd64a7c7b50861243e6fc2e9e6ccfe8424ca93df99cc3ece5cb63"
    ),
}
EXPECTED_SPEC_SHA256 = (
    "501d77e9cdc8e30251a8e11b218aab2447452a7ddb801294b94cb5c46058ce2f"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain an object")
    return value


def expected_pack_paths() -> set[str]:
    paths = {
        "README.md",
        "generate_configs.py",
        "calibration_plan.json",
        "calibration_plan.sha256",
        "order_manifest.json",
        "plan_tree.json",
        "plan_tree.sha256",
        "producer_contract.json",
        "condition_families/condition_family_df_ph_decode_qwen25_7b.json",
        (
            "condition_families/"
            "condition_family_df_ph_prefill_p128_qwen25_7b.json"
        ),
        (
            "condition_families/"
            "condition_family_df_ph_prefill_p256_qwen25_7b.json"
        ),
        "01_phase_decode_absolute/order_manifest.json",
        "02_phase_decode_abba_blocks_01_05/order_manifest.json",
        "03_phase_decode_abba_blocks_06_10/order_manifest.json",
        "04_phase_prefill_p256_absolute/order_manifest.json",
        "05_phase_prefill_p256_abba_blocks_01_05/order_manifest.json",
        "06_phase_prefill_p256_abba_blocks_06_10/order_manifest.json",
    }
    paths.update(
        f"01_phase_decode_absolute/d117f7-df-ph-decode-abs-r{rep:02d}.json"
        for rep in range(1, 11)
    )
    for directory, first, last in (
        ("02_phase_decode_abba_blocks_01_05", 1, 5),
        ("03_phase_decode_abba_blocks_06_10", 6, 10),
    ):
        paths.update(
            (
                f"{directory}/d117f7-df-cmp-abba-ph-decode-"
                f"b{block:02d}-{position}.json"
            )
            for block in range(first, last + 1)
            for position in ("a1", "b1", "b2", "a2")
        )
    paths.update(
        f"04_phase_prefill_p256_absolute/d117f7-df-ph-prefill-p256-abs-r{rep:02d}.json"
        for rep in range(1, 11)
    )
    for directory, first, last in (
        ("05_phase_prefill_p256_abba_blocks_01_05", 1, 5),
        ("06_phase_prefill_p256_abba_blocks_06_10", 6, 10),
    ):
        paths.update(
            (
                f"{directory}/d117f7-df-cmp-abba-ph-prefill-p256-"
                f"b{block:02d}-{position}.json"
            )
            for block in range(first, last + 1)
            for position in ("a1", "b1", "b2", "a2")
        )
    return paths


def cell_member_ids(cell: dict) -> list[str]:
    if cell["kind"] == "absolute":
        return [member["bundle_id"] for member in cell["members"]]
    return [
        block["members"][position]
        for block in cell["blocks"]
        for position in ("A1", "B1", "B2", "A2")
    ]


def observed_manifest_block_order(rows: list[dict]) -> list[tuple[int, str, int]]:
    return [
        (row["block_index"], row["position"], row["position_in_block"])
        for row in rows
    ]


class D117Qwen25SevenBPlanTests(unittest.TestCase):
    maxDiff = None

    def test_exact_inventory_hashes_and_sidecars(self) -> None:
        actual = {
            path.relative_to(PACK).as_posix()
            for path in PACK.rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, expected_pack_paths())
        self.assertEqual(len(actual), 117)
        for relative, expected in EXPECTED_SHA256.items():
            self.assertEqual(file_sha256(PACK / relative), expected, relative)
        self.assertEqual(file_sha256(SPEC), EXPECTED_SPEC_SHA256)

        for stem in ("calibration_plan", "plan_tree"):
            artifact = PACK / f"{stem}.json"
            sidecar = PACK / f"{stem}.sha256"
            self.assertEqual(
                sidecar.read_text(encoding="utf-8"),
                f"{file_sha256(artifact)}  {artifact.name}\n",
            )

    def test_two_temporary_generations_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            outputs = [temp_root / "one", temp_root / "two"]
            for output in outputs:
                result = subprocess.run(
                    [sys.executable, str(GENERATOR), "--output-root", str(output)],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            for relative in sorted(expected_pack_paths()):
                committed = (PACK / relative).read_bytes()
                self.assertEqual(
                    (outputs[0] / PACK.relative_to(REPO_ROOT) / relative).read_bytes(),
                    committed,
                    relative,
                )
                self.assertEqual(
                    (outputs[1] / PACK.relative_to(REPO_ROOT) / relative).read_bytes(),
                    committed,
                    relative,
                )
            spec_relative = SPEC.relative_to(REPO_ROOT)
            self.assertEqual(
                (outputs[0] / spec_relative).read_bytes(), SPEC.read_bytes()
            )
            self.assertEqual(
                (outputs[1] / spec_relative).read_bytes(), SPEC.read_bytes()
            )

    def test_generator_check_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("draft check passed", result.stdout)

    def test_generator_check_rejects_extra_pack_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-beta-inventory-") as temp:
            check_root = Path(temp)
            shutil.copytree(PACK, check_root / PACK.relative_to(REPO_ROOT))
            (check_root / SPEC.relative_to(REPO_ROOT)).parent.mkdir(
                parents=True, exist_ok=True
            )
            shutil.copy2(SPEC, check_root / SPEC.relative_to(REPO_ROOT))
            (check_root / PACK.relative_to(REPO_ROOT) / "stray-review-probe.txt").write_text(
                "unexpected\n", encoding="utf-8"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--check",
                    "--output-root",
                    str(check_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("extras=stray-review-probe.txt", result.stderr)

    def test_manifest_order_and_midpoint_split(self) -> None:
        root = load_json(PACK / "order_manifest.json")
        rows = root["executed_order"]
        self.assertEqual(len(rows), 100)
        self.assertEqual([row["index"] for row in rows], list(range(1, 101)))
        self.assertEqual(len({row["run_id"] for row in rows}), 100)

        entries, warning = load_order_entries(PACK)
        self.assertIsNone(warning)
        self.assertEqual([entry.run_id for entry in entries], [r["run_id"] for r in rows])

        for row in rows:
            self.assertEqual(file_sha256(PACK / row["config"]), row["config_sha256"])

        stages = root["subcampaign_order"]
        self.assertEqual(
            [stage["planned_n_bundles"] for stage in stages],
            [10, 20, 20, 10, 20, 20],
        )
        for stage in stages:
            path = REPO_ROOT / stage["manifest_path"]
            manifest = load_json(path)
            self.assertEqual(stage["manifest_id"], manifest["manifest_id"])
            self.assertEqual(stage["manifest_sha256"], file_sha256(path))
            self.assertEqual(
                [row["index"] for row in manifest["executed_order"]],
                list(range(1, stage["planned_n_bundles"] + 1)),
            )

        for stage_index, expected_blocks in (
            (1, range(1, 6)),
            (2, range(6, 11)),
            (4, range(1, 6)),
            (5, range(6, 11)),
        ):
            stage_path = REPO_ROOT / stages[stage_index]["manifest_path"]
            stage_rows = load_json(stage_path)["executed_order"]
            expected_order = [
                (block, position, sequence)
                for block in expected_blocks
                for sequence, position in enumerate(
                    ("A1", "B1", "B2", "A2"), start=1
                )
            ]
            self.assertEqual(observed_manifest_block_order(stage_rows), expected_order)

        graph_ids = [
            stage["stage_id"]
            for stage in load_json(PACK / "plan_tree.json")["stage_graph"]
        ]
        self.assertLess(
            graph_ids.index("beta-science-abba-06-10"),
            graph_ids.index("beta-reference-midpoint"),
        )
        self.assertLess(
            graph_ids.index("beta-reference-midpoint"),
            graph_ids.index("beta-science-prefill-p256-absolute"),
        )
        plan = load_json(PACK / "calibration_plan.json")
        tree = load_json(PACK / "plan_tree.json")
        self.assertEqual(plan["execution_mode"]["planned_reference_bundles"], 7)
        self.assertEqual(tree["runtime_budget"]["planning_estimate_minutes_with_margin"], 388.8)
        self.assertEqual(tree["runtime_budget"]["planning_estimate_hours_with_margin"], 6.48)

    def test_manifest_order_assertion_rejects_cross_block_mutation(self) -> None:
        source = PACK / "02_phase_decode_abba_blocks_01_05/order_manifest.json"
        with tempfile.TemporaryDirectory(prefix="d117-beta-order-mutation-") as temp:
            mutated = Path(temp) / "order_manifest.json"
            shutil.copy2(source, mutated)
            payload = load_json(mutated)
            rows = payload["executed_order"]
            rows[0], rows[4] = rows[4], rows[0]
            mutated.write_text(
                json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
            )
            observed = observed_manifest_block_order(
                load_json(mutated)["executed_order"]
            )
            expected_order = [
                (block, position, sequence)
                for block in range(1, 6)
                for sequence, position in enumerate(
                    ("A1", "B1", "B2", "A2"), start=1
                )
            ]
            with self.assertRaises(AssertionError):
                self.assertEqual(observed, expected_order)

    def test_stack_family_identity_and_fresh_ids(self) -> None:
        plan = load_json(PACK / "calibration_plan.json")
        tree = load_json(PACK / "plan_tree.json")
        root = load_json(PACK / "order_manifest.json")
        old_root = load_json(OLD_PACK / "order_manifest.json")
        old_ids = {row["run_id"] for row in old_root["executed_order"]}
        new_ids = {row["run_id"] for row in root["executed_order"]}

        self.assertEqual(plan["plan_id"], PLAN_ID)
        self.assertEqual(plan["draft_status"], "unfrozen_draft")
        self.assertEqual(tree["window_identity"]["evidence_root_id"], EVIDENCE_ROOT_ID)
        self.assertEqual(tree["draft_status"], "unfrozen_draft")
        self.assertTrue(all(run_id.startswith("d117f7-") for run_id in new_ids))
        self.assertTrue(new_ids.isdisjoint(old_ids))

        stack = plan["stack_scope"]
        self.assertEqual(stack["model_name"], "Qwen2.5-7B-Instruct-4bit")
        self.assertEqual(
            stack["model_revision"],
            "c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed",
        )
        self.assertEqual(stack["quantization"], "int4")
        self.assertEqual(stack["decode_condition_family_id"], DECODE_FAMILY_ID)
        self.assertEqual(stack["prefill_condition_family_id"], PREFILL_FAMILY_ID)
        first = load_json(PACK / root["executed_order"][0]["config"])
        self.assertEqual(first["model"]["name"], stack["model_name"])
        self.assertEqual(first["model"]["revision"], stack["model_revision"])
        self.assertEqual(first["workload_profile"]["prompt_tokens"], 128)
        self.assertEqual(first["workload_profile"]["output_tokens"], 512)
        for row in root["executed_order"]:
            config = load_json(PACK / row["config"])
            tags = config["run_metadata"]["tags"]
            self.assertNotIn("splitwise-decode-floor-v1", tags)
            is_p256 = "prefill-p256" in row["run_id"]
            expected_plan_sha = file_sha256(PACK / "calibration_plan.json") if is_p256 else LEGACY_DECODE_PLAN_SHA256
            self.assertIn(f"calibration-plan-sha256={expected_plan_sha}", tags)
            if is_p256:
                self.assertNotIn("prompt_tokens", config["workload_profile"])
                self.assertIn("prompt_text", config["workload_profile"])

    def test_p256_workload_is_byte_identical_to_consumer_arm(self) -> None:
        root = load_json(PACK / "order_manifest.json")
        floor_row = next(
            row
            for row in root["executed_order"]
            if row["run_id"].startswith("d117f7-df-ph-prefill-p256-abs-")
        )
        contrast_manifest = load_json(CONTRAST_PACK / "order_manifest.json")
        contrast_row = next(
            row
            for row in contrast_manifest["executed_order"]
            if row["measurement_arm"] == "prefill_p256" and row["arm"] == "B"
        )
        floor_workload = load_json(PACK / floor_row["config"])["workload_profile"]
        contrast_workload = load_json(CONTRAST_PACK / contrast_row["config"])["workload_profile"]
        self.assertEqual(floor_workload, contrast_workload)
        self.assertIn("prompt_text", floor_workload)
        self.assertNotIn("prompt_tokens", floor_workload)

    def test_calibration_plan_shape_and_abba_members_are_family_canonical(self) -> None:
        plan = load_json(PACK / "calibration_plan.json")
        siblings = [
            load_json(
                REPO_ROOT
                / "configs/campaigns/d117_floor_qwen25_1p5b_v1/calibration_plan.json"
            ),
            load_json(
                REPO_ROOT
                / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/calibration_plan.json"
            ),
        ]
        for sibling in siblings:
            self.assertEqual(sibling["schema_version"], plan["schema_version"])
            self.assertEqual(set(sibling), set(plan))
        for cell in plan["floor_cells"]:
            if cell["kind"] in {"comparative_abba", "comparative_contrast"}:
                for block in cell["ordered_blocks"]:
                    self.assertEqual(
                        [member["position"] for member in block["members"]],
                        ["A1", "B1", "B2", "A2"],
                    )
                    self.assertTrue(
                        all(
                            set(member)
                            == {"position", "plan_label", "plan_sequence_index", "bundle_id"}
                            for member in block["members"]
                        )
                    )

    def test_rider_families_and_dedicated_p256_floor_cells(self) -> None:
        decode_path = (
            PACK
            / "condition_families/condition_family_df_ph_decode_qwen25_7b.json"
        )
        prefill_path = (
            PACK
            / "condition_families/"
            "condition_family_df_ph_prefill_p128_qwen25_7b.json"
        )
        decode = load_json(decode_path)
        prefill = load_json(prefill_path)
        p256_path = (
            PACK
            / "condition_families/"
            "condition_family_df_ph_prefill_p256_qwen25_7b.json"
        )
        p256 = load_json(p256_path)
        self.assertEqual(decode["condition_family_id"], DECODE_FAMILY_ID)
        self.assertEqual(prefill["condition_family_id"], PREFILL_FAMILY_ID)
        self.assertEqual(decode["workload_profile"], prefill["workload_profile"])
        self.assertEqual(decode["measurement_target"]["metric"], "phase_energy_j.decode")
        self.assertEqual(
            prefill["measurement_target"]["metric"], "phase_energy_j.prefill"
        )
        self.assertEqual(
            canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, decode),
            "a20018d57f06d69ffcc14e1e9365ab0121b73804ec480f9b08302384bd583843",
        )
        self.assertEqual(
            canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, prefill),
            "b95688675b5518ab6675b8688ce4475b0d756653ecfb10ec80fa913ee49d69f1",
        )
        self.assertEqual(p256["condition_family_id"], P256_FAMILY_ID)
        self.assertEqual(p256["workload_profile"]["prompt_tokens"], 256)
        self.assertEqual(
            canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, p256),
            "023a513fc4020c67d5866e8176dbb872bb3884109c63e3d57637fa6195ba9538",
        )
        tree = load_json(PACK / "plan_tree.json")
        p256_binding = next(
            row for row in tree["condition_families"]
            if row["condition_family_id"] == P256_FAMILY_ID
        )
        self.assertEqual(p256_binding["ruled_token_id_sha256_prefix"], "83099a66")
        self.assertIn("no full-hex", p256_binding["token_id_sha256_pin_status"])

        spec = load_json(SPEC)
        self.assertEqual(validate_extraction_spec(spec), [])
        cells = spec["cells"]
        self.assertEqual(len(cells), 6)
        self.assertEqual(
            [(cell["metric"], cell["kind"]) for cell in cells],
            [
                ("phase_energy_j.decode", "absolute"),
                ("phase_energy_j.decode", "comparative"),
                ("phase_energy_j.prefill", "absolute"),
                ("phase_energy_j.prefill", "comparative"),
                ("phase_energy_j.prefill", "absolute"),
                ("phase_energy_j.prefill", "comparative"),
            ],
        )
        member_lists = [cell_member_ids(cell) for cell in cells]
        self.assertEqual([len(members) for members in member_lists], [10, 40, 10, 40, 10, 40])
        self.assertEqual(sum(map(len, member_lists)), 150)
        self.assertEqual(len(set().union(*map(set, member_lists))), 100)
        self.assertEqual(member_lists[0], member_lists[2])
        self.assertEqual(member_lists[1], member_lists[3])
        self.assertTrue(set(member_lists[0] + member_lists[1]).isdisjoint(member_lists[4] + member_lists[5]))
        self.assertEqual(
            [cell["target_precheck_path"] for cell in cells],
            [
                ["phase", "decode"],
                ["phase", "decode"],
                ["phase", "prefill"],
                ["phase", "prefill"],
                ["phase", "prefill"],
                ["phase", "prefill"],
            ],
        )
        for cell in (cells[0], cells[2], cells[4]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (cells[1], cells[3], cells[5]):
            self.assertNotIn("estimator", cell)
            self.assertNotIn("estimator_registration", cell)
            self.assertEqual(
                cell["calibration_basis"]["allowance_embedding_count"], 1
            )
        plan = load_json(PACK / "calibration_plan.json")
        for cell in (plan["floor_cells"][0], plan["floor_cells"][2], plan["floor_cells"][4]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (plan["floor_cells"][1], plan["floor_cells"][3], plan["floor_cells"][5]):
            self.assertNotIn("estimator", cell)
            self.assertNotIn("estimator_registration", cell)

    def test_issued_acceptance_and_reported_mean_registration(self) -> None:
        tree = load_json(PACK / "plan_tree.json")
        self.assertEqual(
            tree["acceptance_policy"]["selection"],
            "issued_d116_artifact_only",
        )
        spec = load_json(SPEC)
        for cell in spec["cells"]:
            issued = cell["calibration_basis"]["issued_acceptance"]
            self.assertEqual(
                cell["calibration_basis"]["acceptance_selection"],
                "issued_d116_artifact_only",
            )
            self.assertEqual(
                issued["acceptance_id"], "d079_calibration_acceptance_v2_n19"
            )
            self.assertEqual(
                issued["artifact_sha256"],
                "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
            )
            self.assertEqual(
                issued["derivation_sha256"],
                "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02",
            )
            self.assertEqual(
                issued["schema_version"],
                "joulewise.calibration_acceptance_bound.v2",
            )

        root_rows = load_json(PACK / "order_manifest.json")["executed_order"]
        expected_members = [
            {
                "ordinal": index,
                "bundle_id": row["run_id"],
                "config_sha256": row["config_sha256"],
            }
            for index, row in enumerate(root_rows[:50], start=1)
        ]
        expected_p256_members = [
            {
                "ordinal": index,
                "bundle_id": row["run_id"],
                "config_sha256": row["config_sha256"],
            }
            for index, row in enumerate(root_rows[50:], start=1)
        ]
        reported = spec["reported_energy_cells"]
        self.assertEqual(len(reported), 3)
        self.assertEqual(
            [cell["measurand"] for cell in reported],
            ["gross_phase_energy_j", "gross_phase_energy_j", "gross_phase_energy_j"],
        )
        for index, cell in enumerate(reported):
            self.assertEqual(cell["expected_n"], 50)
            self.assertEqual(
                cell["reducer"],
                "arithmetic_mean_over_fixed_member_universe.v1",
            )
            self.assertEqual(
                cell["members"],
                expected_members if index < 2 else expected_p256_members,
            )
            self.assertIsNone(cell["numeric_value"])

    def test_reporting_section_does_not_change_floor_output(self) -> None:
        spec = load_json(SPEC)
        floor_only = deepcopy(spec)
        del floor_only["reported_energy_cells"]
        del floor_only["reported_energy_registration"]
        self.assertEqual(validate_extraction_spec(spec), validate_extraction_spec(floor_only))
        self.assertEqual(
            canonical_sha256(spec["cells"]),
            spec["reported_energy_registration"]["floor_projection_sha256"],
        )

        class FakeSession:
            ready = False
            refusal_reasons = ()

            def provenance_for(self, bundle_id: str) -> None:
                return None

        def fake_report(**kwargs: object) -> floor_extraction.CellReport:
            return floor_extraction.CellReport(
                cell_id=str(kwargs["cell_id"]),
                kind=(
                    "absolute" if "members" in kwargs else "comparative"
                ),
                metric=str(kwargs["metric"]),
                window_class=str(kwargs["window_class"]),
                cap_hit_policy=str(kwargs["cap_hit_policy"]),
                members=(),
                excluded_slots=(),
                n_planned=10,
                n_admitted=0,
                refusal_reasons=("synthetic_plan_test",),
                floor=None,
                anchor_shift_bound_max_j=None,
            )

        patches = (
            mock.patch.object(
                floor_extraction, "campaign_cooldown_evidence", return_value={}
            ),
            mock.patch.object(
                floor_extraction,
                "AuthenticatedConsumptionSession",
                return_value=FakeSession(),
            ),
            mock.patch.object(
                floor_extraction,
                "_whole_window_extraction_refusals",
                return_value=("synthetic_plan_test",),
            ),
            mock.patch.object(
                floor_extraction, "extract_absolute_cell", side_effect=fake_report
            ),
            mock.patch.object(
                floor_extraction, "extract_comparative_cell", side_effect=fake_report
            ),
        )
        with tempfile.TemporaryDirectory(prefix="d117-floor-output-identity-") as temp:
            temp_root = Path(temp)
            with_reported_spec = temp_root / "with-reported.json"
            floor_only_spec = temp_root / "floor-only.json"
            shutil.copy2(SPEC, with_reported_spec)
            floor_only_spec.write_text(
                json.dumps(floor_only, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with_reported_out = temp_root / "with-reported-output.json"
            floor_only_out = temp_root / "floor-only-output.json"

            with (
                patches[0],
                patches[1],
                patches[2],
                patches[3],
                patches[4],
                redirect_stderr(StringIO()),
            ):
                with_reported_status = extract_main(
                    [
                        "--runs-root",
                        str(REPO_ROOT),
                        "--spec",
                        str(with_reported_spec),
                        "--out",
                        str(with_reported_out),
                    ]
                )
                floor_only_status = extract_main(
                    [
                        "--runs-root",
                        str(REPO_ROOT),
                        "--spec",
                        str(floor_only_spec),
                        "--out",
                        str(floor_only_out),
                    ]
                )

            self.assertEqual(with_reported_status, floor_only_status)
            with_reported_bytes = with_reported_out.read_bytes()
            floor_only_bytes = floor_only_out.read_bytes()
            self.assertEqual(with_reported_bytes, floor_only_bytes)
            self.assertEqual(
                hashlib.sha256(with_reported_bytes).hexdigest(),
                hashlib.sha256(floor_only_bytes).hexdigest(),
            )

    def test_typed_stage_launch_recipes(self) -> None:
        tree = load_json(PACK / "plan_tree.json")
        stages = tree["stage_graph"]
        self.assertEqual([stage["ordinal"] for stage in stages], list(range(1, 17)))
        self.assertEqual(
            [stage["predecessor"] for stage in stages],
            [None, *[stage["stage_id"] for stage in stages[:-1]]],
        )
        self.assertEqual(
            [stage["successor"] for stage in stages],
            [*[stage["stage_id"] for stage in stages[1:]], None],
        )
        commands = [command for stage in stages for command in stage["launch"]["commands"]]
        self.assertEqual(len(commands), 17)
        self.assertEqual(len({command["command_id"] for command in commands}), 17)
        allowed_token_keys = {
            "literal": {"kind", "value"},
            "repo_path": {"kind", "value"},
            "binding": {"kind", "value"},
            "binding_path": {"kind", "value", "relative"},
            "tree_pointer": {"kind", "value"},
        }
        for stage in stages:
            launch = stage["launch"]
            self.assertEqual(launch["schema_version"], "joulewise.stage_launch.v1")
            self.assertEqual(set(launch), {"schema_version", "commands"})
            for command in launch["commands"]:
                self.assertEqual(
                    set(command),
                    {
                        "command_id",
                        "command_kind",
                        "argv_template",
                        "cwd",
                        "success_exit_codes",
                    },
                )
                self.assertEqual(command["success_exit_codes"], [0])
                self.assertEqual(command["cwd"], {"kind": "binding", "value": "repo_root"})
                template = command["argv_template"]
                self.assertEqual(set(template), {"tool_id", "interface_id", "arguments"})
                for argument in template["arguments"]:
                    self.assertIn(argument["kind"], allowed_token_keys)
                    self.assertEqual(set(argument), allowed_token_keys[argument["kind"]])
                    rendered = " ".join(str(value) for value in argument.values())
                    for forbidden in ("$", "~", "\n", ";", "&&", "|"):
                        self.assertNotIn(forbidden, rendered)


    def test_receipt_oracle_is_recomputed_from_the_production_model(self) -> None:
        tree = load_json(PACK / "plan_tree.json")
        expected = derive_bracket_session_receipt_oracle()
        actual = tree["arm_attachments"]["receipt_oracle"]
        self.assertEqual(actual, expected)
        self.assertIsNone(actual["terminal_sequence"])
        self.assertEqual(actual["arm_time_receipts"], [])
        closeout = tree["closeout_attachments"]
        self.assertEqual(closeout["postcollection_receipt_digests"], [])
        self.assertIsNone(closeout["terminal_ledger_head"])
        stale_marker = "impl/d117-" + "ledger-recovery"
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK.rglob("*"))
            if path.is_file() and path.suffix in {".json", ".md", ".py", ".sha256"}
        )
        self.assertNotIn(stale_marker, generated_text)

    def test_producer_contract_is_beta_position_and_roles(self) -> None:
        producer = load_json(PACK / "producer_contract.json")
        self.assertEqual(producer["draft_status"], "unfrozen_draft")
        for manifest_path in [PACK / "order_manifest.json", *sorted(PACK.glob("*/order_manifest.json"))]:
            self.assertEqual(load_json(manifest_path)["draft_status"], "unfrozen_draft")
        spec = load_json(SPEC)
        self.assertIn(
            "A successor acceptance artifact issuing before arm REQUIRES pack regeneration",
            spec["successor_acceptance_artifact_policy"],
        )
        self.assertIn(
            spec["successor_acceptance_artifact_policy"],
            (PACK / "README.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(producer["producer_index"], 2)
        self.assertEqual(
            producer["component_artifact_id"],
            "d117-qwen25-7b-phase-floor-component-v1",
        )
        self.assertEqual(
            [cell["role"] for cell in producer["roles"]],
            ["decode", "prefill", "prefill_p256"],
        )
        self.assertEqual(
            [cell["condition_family_id"] for cell in producer["roles"]],
            [DECODE_FAMILY_ID, PREFILL_FAMILY_ID, P256_FAMILY_ID],
        )
        self.assertEqual(producer["extraction_spec"]["member_count"], 100)
        self.assertEqual(producer["extraction_spec"]["sha256"], file_sha256(SPEC))
        projection = producer["identity_pin_projection"]
        self.assertEqual(projection["work_order"], "D117-U11-IDPIN-PROJECTION")
        self.assertEqual(projection["mode"], "derive_never_operator_enter")
        self.assertEqual(projection["state"], "unprojected")
        self.assertEqual(projection["derivation_contract"], IDENTITY_PIN_DERIVATION_CONTRACT)
        self.assertEqual(projection["supersedes"], [])
        self.assertEqual(len(projection["identity_units"]), 2)
        self.assertEqual(
            [unit["identity_unit_id"] for unit in projection["identity_units"]],
            ["beta", "beta/prefill_p256"],
        )
        unit = projection["identity_units"][0]
        self.assertEqual(unit["identity_unit_id"], "beta")
        self.assertEqual(set(unit["model_runtime_config"].values()), {None})
        computed_config_hashes = {
            scientific_config_identity_sha256(load_json(PACK / row["path"]))
            for row in unit["config_inventory"]
        }
        self.assertEqual(len(computed_config_hashes), 1)
        for row in unit["config_inventory"]:
            self.assertEqual(row["sha256"], file_sha256(PACK / row["path"]))
        p256_unit = projection["identity_units"][1]
        p256_hashes = {
            scientific_config_identity_sha256(load_json(PACK / row["path"]))
            for row in p256_unit["config_inventory"]
        }
        self.assertEqual(len(p256_hashes), 1)
        self.assertEqual(len(p256_unit["config_inventory"]), 50)
        self.assertIsNone(projection["projection_receipt"])
        self.assertEqual(
            load_json(PACK / "plan_tree.json")["arm_attachments"][
                "identity_pin_projection"
            ],
            projection,
        )

    def test_generator_has_only_inventory_directory_discovery(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")
        for forbidden in (".glob(", "os.walk", "Path.walk"):
            self.assertNotIn(forbidden, source)
        self.assertIn('.rglob("*")', source)
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK.rglob("*"))
            if path.is_file() and path.suffix in {".json", ".md", ".sha256"}
        )
        for diagnostic in ("6." + "294380", "13." + "998036"):
            self.assertNotIn(diagnostic, generated_text)


if __name__ == "__main__":
    unittest.main()
