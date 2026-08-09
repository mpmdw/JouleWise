from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.floor_extraction as floor_extraction
from joulewise.detection_floor import (
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
)
from joulewise.floor_extraction import validate_extraction_spec
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
TODO_BRANCH = "impl/d117-ledger-recovery"

EXPECTED_SHA256 = {
    "calibration_plan.json": (
        "969137e868d8615535576ae0c4eda263045c81c7f228b87c042d3f2da11f3d3e"
    ),
    "calibration_plan.sha256": (
        "708a8ed324ceca3ffb8c776d56d7f17b2812db02ea129f50c055bf3b37a925b0"
    ),
    "condition_families/condition_family_df_ph_decode_qwen25_7b.json": (
        "d90b8fec2ccc74f1e982e573789a32116cda78d625ce84e72f2717926edc0cdb"
    ),
    (
        "condition_families/"
        "condition_family_df_ph_prefill_p128_qwen25_7b.json"
    ): "e896aeae5eff911dbe14d09de9ebddcafe37b20c67ba059b2a6b7f6d3a6cee25",
    "generate_configs.py": (
        "bc4c173d4a4f1b4778957eba8d97796429ed97cfae893cb2e5fe9124f6790d1e"
    ),
    "01_phase_decode_absolute/order_manifest.json": (
        "7f87bd9e21eb7540d8ee20de43f64ba99a4ddf960c6800925c74c11edef81187"
    ),
    "02_phase_decode_abba_blocks_01_05/order_manifest.json": (
        "c54ad639b64a5a7cde03cbf164f368f5cccef136031e73be7b6cb32cc1fecab1"
    ),
    "03_phase_decode_abba_blocks_06_10/order_manifest.json": (
        "0be1844b00af9233b733237b938c50303aa47199735ca29ec51e6b03cf8df21a"
    ),
    "order_manifest.json": (
        "dec729ebddc8ae8bd8defe9b2a2be0f9ee24c80ecbd1e474f3b973b5fbfcfbc9"
    ),
    "plan_tree.json": (
        "f1e8cdcd6d50d4cc2862bbb01f7fb6231c1981dd644788601231a9d36a779b87"
    ),
    "plan_tree.sha256": (
        "31b9e84ef1ad81d4b3469b32638fc6870070ce90d6ea39a223480ca2cd373bce"
    ),
    "producer_contract.json": (
        "353f389ccf2d7d230ea515dfa9a48c88b5cd3d15c939f16d09b63e69185ca97d"
    ),
}
EXPECTED_SPEC_SHA256 = (
    "836994639d6e3b3ef73d127713cf8aefe1a6bf7fb73372bd010df7e91a80401e"
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
        "01_phase_decode_absolute/order_manifest.json",
        "02_phase_decode_abba_blocks_01_05/order_manifest.json",
        "03_phase_decode_abba_blocks_06_10/order_manifest.json",
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
    return paths


def cell_member_ids(cell: dict) -> list[str]:
    if cell["kind"] == "absolute":
        return [member["bundle_id"] for member in cell["members"]]
    return [
        block["members"][position]
        for block in cell["blocks"]
        for position in ("A1", "B1", "B2", "A2")
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
        self.assertEqual(len(actual), 63)
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

    def test_manifest_order_and_midpoint_split(self) -> None:
        root = load_json(PACK / "order_manifest.json")
        rows = root["executed_order"]
        self.assertEqual(len(rows), 50)
        self.assertEqual([row["index"] for row in rows], list(range(1, 51)))
        self.assertEqual(len({row["run_id"] for row in rows}), 50)

        entries, warning = load_order_entries(PACK)
        self.assertIsNone(warning)
        self.assertEqual([entry.run_id for entry in entries], [r["run_id"] for r in rows])

        for row in rows:
            self.assertEqual(file_sha256(PACK / row["config"]), row["config_sha256"])

        stages = root["subcampaign_order"]
        self.assertEqual([stage["planned_n_bundles"] for stage in stages], [10, 20, 20])
        for stage in stages:
            path = REPO_ROOT / stage["manifest_path"]
            manifest = load_json(path)
            self.assertEqual(stage["manifest_id"], manifest["manifest_id"])
            self.assertEqual(stage["manifest_sha256"], file_sha256(path))
            self.assertEqual(
                [row["index"] for row in manifest["executed_order"]],
                list(range(1, stage["planned_n_bundles"] + 1)),
            )

        for stage_index, expected_blocks in ((1, range(1, 6)), (2, range(6, 11))):
            stage_path = REPO_ROOT / stages[stage_index]["manifest_path"]
            stage_rows = load_json(stage_path)["executed_order"]
            observed = []
            for block in expected_blocks:
                block_rows = [row for row in stage_rows if row["block_index"] == block]
                observed.append(block)
                self.assertEqual(
                    [row["position_in_block"] for row in block_rows], [1, 2, 3, 4]
                )
                self.assertEqual(
                    [row["run_id"].rsplit("-", 1)[1] for row in block_rows],
                    ["a1", "b1", "b2", "a2"],
                )
            self.assertEqual(observed, list(expected_blocks))

        graph_ids = [
            stage["stage_id"]
            for stage in load_json(PACK / "plan_tree.json")["stage_graph"]
        ]
        self.assertLess(
            graph_ids.index("beta-science-abba-01-05"),
            graph_ids.index("beta-reference-midpoint"),
        )
        self.assertLess(
            graph_ids.index("beta-reference-midpoint"),
            graph_ids.index("beta-science-abba-06-10"),
        )

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

    def test_rider_families_and_four_floor_cells(self) -> None:
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

        spec = load_json(SPEC)
        self.assertEqual(validate_extraction_spec(spec), [])
        cells = spec["cells"]
        self.assertEqual(len(cells), 4)
        self.assertEqual(
            [(cell["metric"], cell["kind"]) for cell in cells],
            [
                ("phase_energy_j.decode", "absolute"),
                ("phase_energy_j.decode", "comparative"),
                ("phase_energy_j.prefill", "absolute"),
                ("phase_energy_j.prefill", "comparative"),
            ],
        )
        member_lists = [cell_member_ids(cell) for cell in cells]
        self.assertEqual([len(members) for members in member_lists], [10, 40, 10, 40])
        self.assertEqual(sum(map(len, member_lists)), 100)
        self.assertEqual(len(set().union(*map(set, member_lists))), 50)
        self.assertEqual(member_lists[0], member_lists[2])
        self.assertEqual(member_lists[1], member_lists[3])
        self.assertEqual(
            [cell["target_precheck_path"] for cell in cells],
            [
                ["phase", "decode"],
                ["phase", "decode"],
                ["phase", "prefill"],
                ["phase", "prefill"],
            ],
        )
        for cell in (cells[1], cells[3]):
            self.assertEqual(
                cell["estimator"],
                "d124_two_shared_edge_common_mode.v1",
            )
            self.assertEqual(
                cell["estimator_registration"]["transfer_assumption"][
                    "assumption_id"
                ],
                "d124_block_bracket_edges_shared_within_abba.v1",
            )
            self.assertEqual(
                cell["calibration_basis"]["allowance_embedding_count"], 1
            )

    def test_issued_acceptance_and_reported_mean_registration(self) -> None:
        spec = load_json(SPEC)
        for cell in spec["cells"]:
            issued = cell["calibration_basis"]["issued_acceptance"]
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
            for index, row in enumerate(root_rows, start=1)
        ]
        reported = spec["reported_energy_cells"]
        self.assertEqual(len(reported), 2)
        self.assertEqual(
            [cell["measurand"] for cell in reported],
            ["gross_phase_energy_j", "gross_phase_energy_j"],
        )
        for cell in reported:
            self.assertEqual(cell["expected_n"], 50)
            self.assertEqual(
                cell["reducer"],
                "arithmetic_mean_over_fixed_member_universe.v1",
            )
            self.assertEqual(cell["members"], expected_members)
            self.assertIsNone(cell["numeric_value"])

    def test_reporting_section_does_not_change_floor_output(self) -> None:
        spec = load_json(SPEC)
        floor_only = copy.deepcopy(spec)
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
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            with_reported = floor_extraction.extract_cells(REPO_ROOT, spec)
            floor_projection = floor_extraction.extract_cells(REPO_ROOT, floor_only)
        self.assertEqual(with_reported, floor_projection)

    def test_typed_stage_launch_recipes(self) -> None:
        tree = load_json(PACK / "plan_tree.json")
        stages = tree["stage_graph"]
        self.assertEqual([stage["ordinal"] for stage in stages], list(range(1, 14)))
        self.assertEqual(
            [stage["predecessor"] for stage in stages],
            [None, *[stage["stage_id"] for stage in stages[:-1]]],
        )
        self.assertEqual(
            [stage["successor"] for stage in stages],
            [*[stage["stage_id"] for stage in stages[1:]], None],
        )
        commands = [command for stage in stages for command in stage["launch"]["commands"]]
        self.assertEqual(len(commands), 14)
        self.assertEqual(len({command["command_id"] for command in commands}), 14)
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

        self.assertIn(TODO_BRANCH, (PACK / "README.md").read_text(encoding="utf-8"))
        self.assertIn(TODO_BRANCH, json.dumps(tree, sort_keys=True))

    def test_producer_contract_is_beta_position_and_roles(self) -> None:
        producer = load_json(PACK / "producer_contract.json")
        self.assertEqual(producer["draft_status"], "unfrozen_draft")
        self.assertEqual(producer["producer_index"], 2)
        self.assertEqual(
            producer["component_artifact_id"],
            "d117-qwen25-7b-phase-floor-component-v1",
        )
        self.assertEqual([cell["role"] for cell in producer["roles"]], ["decode", "prefill"])
        self.assertEqual(
            [cell["condition_family_id"] for cell in producer["roles"]],
            [DECODE_FAMILY_ID, PREFILL_FAMILY_ID],
        )
        self.assertEqual(producer["extraction_spec"]["member_count"], 50)
        self.assertEqual(producer["extraction_spec"]["sha256"], file_sha256(SPEC))
        projection = producer["identity_pin_projection"]
        self.assertEqual(projection["work_order"], "D117-U11-IDPIN-PROJECTION")
        self.assertEqual(projection["mode"], "derive_never_operator_enter")
        self.assertEqual(set(projection["projected_pins"].values()), {None})
        self.assertIsNone(projection["projection_receipt"])

    def test_generator_has_no_directory_discovery(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")
        for forbidden in (".glob(", ".rglob(", "os.walk", "Path.walk"):
            self.assertNotIn(forbidden, source)
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK.rglob("*"))
            if path.is_file() and path.suffix in {".json", ".md"}
        )
        for diagnostic in ("6." + "294380", "13." + "998036"):
            self.assertNotIn(diagnostic, generated_text)


if __name__ == "__main__":
    unittest.main()
