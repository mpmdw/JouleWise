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

from joulewise.identity_pins import (
    IDENTITY_PIN_DERIVATION_CONTRACT,
    scientific_config_identity_sha256,
)
from typing import Any, Iterable
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PACK_REL = Path("configs/campaigns/d117_floor_qwen25_1p5b_v1")
PACK_ROOT = ROOT / PACK_REL
SPEC_REL = Path("configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json")
SPEC_PATH = ROOT / SPEC_REL
GENERATOR = PACK_ROOT / "generate_configs.py"
PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-1p5b-v1"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.detection_floor import (  # noqa: E402
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
)
import joulewise.floor_extraction as floor_extraction  # noqa: E402
from joulewise.floor_extraction import (  # noqa: E402
    validate_condition_family_definition,
    validate_extraction_spec,
)
from joulewise.schemas import BenchmarkConfig  # noqa: E402
from joulewise.receipt_oracle import (  # noqa: E402
    derive_bracket_session_receipt_oracle,
)
from scripts.extract_detection_floors import main as extract_main  # noqa: E402
from scripts.run_campaign import load_order_entries  # noqa: E402


EXPECTED_PACK_SHA256 = "b74673f5ea5c24b2ccb61542973bce6d453e1c26bcf2da38e0b75db88754638c"
EXPECTED_FILE_SHA256 = {
    "generate_configs.py": "f47cb1220602906b0c835dc6979a6bc448e8bcbe20ffc7031cfb261afbe97bfd",
    "calibration_plan.json": "56b164904cd0ffd0b9af5710ab60e4794cbd47b866a1053de5a7548475bda182",
    "calibration_plan.sha256": "7e38e1f7730e56614c37f778a916098eb7a7655ef4409a9e7bd0a5a97cbd5f9f",
    "order_manifest.json": "cc288667de9f38726d80318a08e24e7788c94fd965e9f2cf84c650a26bb11595",
    "plan_tree.json": "663051ddeae9fff766813becc1910883ac77445729dc080600504ed4999e19b8",
    "plan_tree.sha256": "5b7c5a060c9195a0b3ff3c4bdeca8068832b588a492adb72f7b95412df1287ca",
    "producer_contract.json": "7067c9c5714e0dc442163ee73268aa570a681511ad9d0ef6622a55635a1b1c70",
    "condition_families/condition_family_df_ph_decode.json": (
        "c9054d11a2bf9c4b1718d93ededc44864cfffb34417d19f1178a9d18addcf8a8"
    ),
    "condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json": (
        "985a4e5370724698b601303b2ba99027d298060eedc95a65d20112df413043ad"
    ),
}
EXPECTED_SPEC_SHA256 = "1b2ac6db94ff3eed369d3a6c702270b16c905ea810a90a6090aaf083b14da883"
EXPECTED_FAMILY_DOMAIN_SHA256 = {
    "df-ph-decode": "e38e2a2f3e76b8cdd6b3ef4f5d3d7090ef4846dbf83279001ff4df8a9a762bfe",
    "df-ph-prefill-p128-qwen25-1p5b": (
        "974014e096806423b866a167510787482397cb4f68bb9e6f9f0ba7fd34f93f36"
    ),
}
EXPECTED_EXTERNAL_SHA256 = {
    "configs/campaigns/neg8_reference_corpus/order_manifest.json": (
        "0ec9d68aa4265cc9378bb682091a973fc92879b76506fa25af828050a608509f"
    ),
    "configs/campaigns/window_references/start_triplet/order_manifest.json": (
        "9cac197255bdc9a0a1a0b8ee8ceb587ba3c8cabc20b976b2543dc3a400d37cb0"
    ),
    "configs/campaigns/window_references/midpoint/order_manifest.json": (
        "9ccedd91307985ba5641e791f4ac89f4e250fca414a4ba713cc7977ced6abb21"
    ),
    "configs/campaigns/window_references/end_triplet/order_manifest.json": (
        "8e65a4347aafa0722a60a2bd58c7e8061b860db66fa06f6acec24d1a1ade5c67"
    ),
    "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json": (
        "74ccdaec74497c3aa7c074ef1129ec2bf2cc01d8ac14d3d07be77ab468599688"
    ),
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256_bytes(raw)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected object: {path}")
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
        "condition_families/condition_family_df_ph_decode.json",
        "condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json",
        "01_phase_decode_absolute/order_manifest.json",
        "02_phase_decode_abba_blocks_01_05/order_manifest.json",
        "03_phase_decode_abba_blocks_06_10/order_manifest.json",
    }
    paths.update(
        f"01_phase_decode_absolute/d117f15-df-ph-decode-abs-r{rep:02d}.json"
        for rep in range(1, 11)
    )
    for block in range(1, 11):
        stage = (
            "02_phase_decode_abba_blocks_01_05"
            if block <= 5
            else "03_phase_decode_abba_blocks_06_10"
        )
        paths.update(
            f"{stage}/d117f15-df-cmp-abba-ph-decode-b{block:02d}-{position}.json"
            for position in ("a1", "b1", "b2", "a2")
        )
    return paths


def pack_digest(pack_root: Path) -> str:
    paths = sorted(path for path in pack_root.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(pack_root).as_posix()
        digest.update(f"{relative}\0{sha256_file(path)}\n".encode("utf-8"))
    return digest.hexdigest()


def floor_reference_ids(cell: dict[str, Any]) -> list[str]:
    if cell["kind"] == "absolute":
        return [member["bundle_id"] for member in cell["members"]]
    return [
        block["members"][position]
        for block in cell["blocks"]
        for position in ("A1", "B1", "B2", "A2")
    ]


class D117FloorQwen251p5BPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_json(PACK_ROOT / "calibration_plan.json")
        cls.root_manifest = load_json(PACK_ROOT / "order_manifest.json")
        cls.tree = load_json(PACK_ROOT / "plan_tree.json")
        cls.spec = load_json(SPEC_PATH)
        cls.producer = load_json(PACK_ROOT / "producer_contract.json")

    def test_exact_inventory_and_content_hashes(self) -> None:
        actual = {
            path.relative_to(PACK_ROOT).as_posix()
            for path in PACK_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, expected_pack_paths())
        self.assertEqual(len(actual), 63)
        self.assertEqual(pack_digest(PACK_ROOT), EXPECTED_PACK_SHA256)
        for relative, expected in EXPECTED_FILE_SHA256.items():
            with self.subTest(relative=relative):
                self.assertEqual(sha256_file(PACK_ROOT / relative), expected)
        self.assertEqual(sha256_file(SPEC_PATH), EXPECTED_SPEC_SHA256)

    def test_two_regenerations_are_byte_identical_and_check_passes(self) -> None:
        checked = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("verified unfrozen draft: 50 science configs", checked.stdout)
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for output_root in (first, second):
                generated = subprocess.run(
                    [
                        sys.executable,
                        str(GENERATOR),
                        "--output-root",
                        output_root,
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stderr)
            for relative in sorted(expected_pack_paths()):
                first_bytes = (Path(first) / PACK_REL / relative).read_bytes()
                second_bytes = (Path(second) / PACK_REL / relative).read_bytes()
                self.assertEqual(first_bytes, second_bytes, relative)
                self.assertEqual(first_bytes, (PACK_ROOT / relative).read_bytes(), relative)
            self.assertEqual(
                (Path(first) / SPEC_REL).read_bytes(),
                (Path(second) / SPEC_REL).read_bytes(),
            )
            self.assertEqual((Path(first) / SPEC_REL).read_bytes(), SPEC_PATH.read_bytes())

    def test_generator_check_rejects_extra_pack_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-alpha-inventory-") as temp:
            check_root = Path(temp)
            shutil.copytree(PACK_ROOT, check_root / PACK_REL)
            (check_root / SPEC_REL).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SPEC_PATH, check_root / SPEC_REL)
            (check_root / PACK_REL / "stray-review-probe.txt").write_text(
                "unexpected\n", encoding="utf-8"
            )
            checked = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--check",
                    "--output-root",
                    str(check_root),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn("extras=stray-review-probe.txt", checked.stderr)

    def test_plan_sidecars_and_embedded_hashes_recompute(self) -> None:
        plan_sha = sha256_file(PACK_ROOT / "calibration_plan.json")
        tree_sha = sha256_file(PACK_ROOT / "plan_tree.json")
        self.assertEqual(
            (PACK_ROOT / "calibration_plan.sha256").read_text(encoding="utf-8"),
            f"{plan_sha}  calibration_plan.json\n",
        )
        self.assertEqual(
            (PACK_ROOT / "plan_tree.sha256").read_text(encoding="utf-8"),
            f"{tree_sha}  plan_tree.json\n",
        )
        self.assertEqual(self.tree["plan"]["actual_sha256"], plan_sha)
        self.assertEqual(self.tree["plan"]["declared_sha256"], plan_sha)
        self.assertEqual(
            self.tree["plan"]["sidecar_sha256"],
            sha256_file(PACK_ROOT / "calibration_plan.sha256"),
        )
        self.assertEqual(self.tree["generator"]["sha256"], sha256_file(GENERATOR))
        self.assertEqual(self.root_manifest["calibration_plan_sha256"], plan_sha)
        self.assertEqual(self.producer["plan"]["sha256"], plan_sha)

        science_by_id = {row["run_id"]: row for row in self.tree["science"]}
        for row in self.root_manifest["executed_order"]:
            config_path = PACK_ROOT / row["config"]
            self.assertEqual(row["config_sha256"], sha256_file(config_path))
            self.assertEqual(science_by_id[row["run_id"]]["config_sha256"], row["config_sha256"])
            self.assertEqual(
                science_by_id[row["run_id"]]["config_path"],
                (PACK_REL / row["config"]).as_posix(),
            )

        for stage in self.root_manifest["subcampaign_order"]:
            path = ROOT / stage["manifest_path"]
            stage_manifest = load_json(path)
            self.assertEqual(stage["manifest_sha256"], sha256_file(path))
            self.assertEqual(stage["manifest_id"], stage_manifest["manifest_id"])
            self.assertEqual(stage_manifest["calibration_plan_sha256"], plan_sha)
            self.assertEqual(
                [row["index"] for row in stage_manifest["executed_order"]],
                list(range(1, stage["planned_n_bundles"] + 1)),
            )
            for row in stage_manifest["executed_order"]:
                config_path = path.parent / row["config"]
                self.assertEqual(row["config_sha256"], sha256_file(config_path))

        order_sha = sha256_file(PACK_ROOT / "order_manifest.json")
        for cell in self.spec["cells"]:
            self.assertEqual(cell["order_manifest"]["sha256"], order_sha)
        self.assertEqual(self.producer["order_manifest"]["sha256"], order_sha)
        self.assertEqual(self.producer["extraction_spec"]["sha256"], sha256_file(SPEC_PATH))
        self.assertEqual(
            self.tree["downstream_contract"]["extraction_spec"]["sha256"],
            sha256_file(SPEC_PATH),
        )
        self.assertEqual(
            self.tree["downstream_contract"]["producer_contract"]["sha256"],
            sha256_file(PACK_ROOT / "producer_contract.json"),
        )

    def test_exact_schedule_and_midpoint_split(self) -> None:
        rows = self.root_manifest["executed_order"]
        self.assertEqual(len(rows), 50)
        self.assertEqual([row["index"] for row in rows], list(range(1, 51)))
        self.assertEqual(len({row["run_id"] for row in rows}), 50)
        self.assertEqual(
            [stage["planned_n_bundles"] for stage in self.root_manifest["subcampaign_order"]],
            [10, 20, 20],
        )
        self.assertEqual(
            [row["run_id"] for row in rows[:10]],
            [f"d117f15-df-ph-decode-abs-r{rep:02d}" for rep in range(1, 11)],
        )
        first_half = rows[10:30]
        second_half = rows[30:50]
        self.assertEqual(sorted({row["block_index"] for row in first_half}), list(range(1, 6)))
        self.assertEqual(sorted({row["block_index"] for row in second_half}), list(range(6, 11)))
        for block in range(1, 11):
            block_rows = [row for row in rows if row["role"] == "comparative_abba_member" and row["block_index"] == block]
            self.assertEqual([row["position"] for row in block_rows], ["A1", "B1", "B2", "A2"])
            self.assertEqual([row["arm"] for row in block_rows], ["A", "B", "B", "A"])
            self.assertEqual([row["position_in_block"] for row in block_rows], [1, 2, 3, 4])
        graph_ids = [stage["stage_id"] for stage in self.tree["stage_graph"]]
        self.assertLess(graph_ids.index("alpha-science-abba-01-05"), graph_ids.index("alpha-reference-midpoint"))
        self.assertLess(graph_ids.index("alpha-reference-midpoint"), graph_ids.index("alpha-science-abba-06-10"))
        entries, warning = load_order_entries(PACK_ROOT)
        self.assertIsNone(warning)
        self.assertEqual([entry.run_id for entry in entries], [row["run_id"] for row in rows])

    def test_calibration_plan_shape_and_abba_members_are_family_canonical(self) -> None:
        sibling_plans = [
            load_json(
                ROOT
                / "configs/campaigns/d117_floor_qwen25_7b_v1/calibration_plan.json"
            ),
            load_json(
                ROOT
                / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/calibration_plan.json"
            ),
        ]
        for sibling in sibling_plans:
            self.assertEqual(sibling["schema_version"], self.plan["schema_version"])
            self.assertEqual(set(sibling), set(self.plan))
        for cell in self.plan["floor_cells"]:
            if cell["kind"] == "comparative_abba":
                for block in cell["ordered_blocks"]:
                    self.assertEqual(
                        [set(member) for member in block["members"]],
                        [
                            {"position", "plan_label", "plan_sequence_index", "bundle_id"}
                        ]
                        * 4,
                    )
                    self.assertEqual(
                        [member["position"] for member in block["members"]],
                        ["A1", "B1", "B2", "A2"],
                    )

    def test_science_configs_preserve_stack_and_change_only_prospective_identity(self) -> None:
        plan_sha = sha256_file(PACK_ROOT / "calibration_plan.json")
        for row in self.root_manifest["executed_order"]:
            config = load_json(PACK_ROOT / row["config"])
            BenchmarkConfig.from_mapping(config)
            self.assertEqual(config["run_id"], row["run_id"])
            self.assertEqual(config["model"]["name"], "Qwen2.5-1.5B-Instruct-4bit")
            self.assertEqual(config["model"]["revision"], "8b403126fc14f14cfc99bb4cfa72ecbc129ea677")
            self.assertEqual(config["quantization"], {"name": "int4", "bits": 4})
            self.assertEqual(config["workload_profile"]["prompt_tokens"], 128)
            self.assertEqual(config["workload_profile"]["output_tokens"], 512)
            self.assertEqual(config["sampling"], {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0})
            tags = config["run_metadata"]["tags"]
            self.assertIn("d117-floor-qwen25-1p5b-v1", tags)
            self.assertIn("production-window", tags)
            self.assertIn("floor-calibration", tags)
            self.assertIn("df-condition=df-ph-decode", tags)
            self.assertIn(f"calibration-plan-sha256={plan_sha}", tags)

    def test_condition_families_and_zero_member_prefill_rider(self) -> None:
        family_paths = {
            "df-ph-decode": PACK_ROOT / "condition_families/condition_family_df_ph_decode.json",
            "df-ph-prefill-p128-qwen25-1p5b": PACK_ROOT / "condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json",
        }
        for family_id, path in family_paths.items():
            definition = load_json(path)
            self.assertEqual(validate_condition_family_definition(definition), [])
            self.assertEqual(definition["condition_family_id"], family_id)
            self.assertEqual(
                canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition),
                EXPECTED_FAMILY_DOMAIN_SHA256[family_id],
            )
        decode = family_paths["df-ph-decode"]
        prefill = family_paths["df-ph-prefill-p128-qwen25-1p5b"]
        decode_definition = load_json(decode)
        prefill_definition = load_json(prefill)
        self.assertEqual(decode_definition["workload_profile"], prefill_definition["workload_profile"])
        self.assertEqual(decode_definition["measurement_target"]["metric"], "phase_energy_j.decode")
        self.assertEqual(prefill_definition["measurement_target"]["metric"], "phase_energy_j.prefill")
        self.assertEqual(self.plan["execution_mode"]["planned_science_bundles"], 50)
        self.assertEqual(self.spec["phase_presence_contract"]["required_metrics"], ["phase_energy_j.decode", "phase_energy_j.prefill"])
        self.assertEqual(self.spec["phase_presence_contract"]["missing_registered_phase"], "refuse_before_floor_or_reported_mean_emission")

    def test_four_floor_cells_and_reported_means_share_pack_members(self) -> None:
        self.assertEqual(validate_extraction_spec(self.spec), [])
        cells = self.spec["cells"]
        self.assertEqual(
            [cell["cell_id"] for cell in cells],
            [
                "d117-df-ph-decode-qwen25-1p5b-absolute",
                "d117-df-cmp-abba-ph-decode-qwen25-1p5b",
                "d117-df-ph-prefill-p128-qwen25-1p5b-absolute",
                "d117-df-cmp-abba-ph-prefill-p128-qwen25-1p5b",
            ],
        )
        references = [floor_reference_ids(cell) for cell in cells]
        self.assertEqual([len(ids) for ids in references], [10, 40, 10, 40])
        self.assertEqual(references[0], references[2])
        self.assertEqual(references[1], references[3])
        all_floor_references = [bundle_id for ids in references for bundle_id in ids]
        self.assertEqual(len(all_floor_references), 100)
        self.assertEqual(len(set(all_floor_references)), 50)
        self.assertEqual(
            self.spec["reference_counts"],
            {
                "floor_cell_references": 100,
                "reported_energy_references": 100,
                "total_registered_references": 200,
                "unique_physical_bundles": 50,
                "unique_config_paths": 50,
            },
        )
        physical_order = [row["run_id"] for row in self.root_manifest["executed_order"]]
        reported = self.spec["reported_energy_cells"]
        self.assertEqual(len(reported), 2)
        for cell in reported:
            self.assertEqual(cell["reducer"], "arithmetic_mean_over_fixed_member_universe.v1")
            self.assertEqual(cell["expected_n"], 50)
            self.assertEqual([member["bundle_id"] for member in cell["members"]], physical_order)
            self.assertIsNone(cell["numeric_value"])

        floor_only = deepcopy(self.spec)
        floor_only.pop("reported_energy_cells")
        floor_only.pop("reported_energy_registration")
        self.assertEqual(validate_extraction_spec(floor_only), validate_extraction_spec(self.spec))
        self.assertEqual(
            canonical_sha256(self.spec["cells"]),
            self.spec["reported_energy_registration"]["floor_projection_sha256"],
        )

    def test_reporting_section_does_not_change_floor_output(self) -> None:
        spec = load_json(SPEC_PATH)
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
            shutil.copy2(SPEC_PATH, with_reported_spec)
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
                        str(ROOT),
                        "--spec",
                        str(with_reported_spec),
                        "--out",
                        str(with_reported_out),
                    ]
                )
                floor_only_status = extract_main(
                    [
                        "--runs-root",
                        str(ROOT),
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

    def test_issued_acceptance_and_default_estimator_path_are_registered(self) -> None:
        self.assertEqual(
            self.tree["acceptance_policy"]["selection"],
            "issued_d116_artifact_only",
        )
        expected_acceptance = {
            "acceptance_id": "d079_calibration_acceptance_v2_n19",
            "path": "configs/calibration/calibration_acceptance_d079_v2.json",
            "artifact_sha256": "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
            "derivation_sha256": "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02",
            "schema_version": "joulewise.calibration_acceptance_bound.v2",
        }
        for cell in self.spec["cells"]:
            basis = cell["calibration_basis"]
            self.assertEqual(basis["issued_acceptance"], expected_acceptance)
            self.assertEqual(
                basis["acceptance_selection"], "issued_d116_artifact_only"
            )
            self.assertEqual(basis["allowance_rule"], "max(observed_drift_s,0.010818)")
            self.assertEqual(basis["allowance_embedding_count"], 1)
            self.assertEqual(basis["component_composition"], "componentwise_max_never_sum.v1")
        for cell in (self.spec["cells"][0], self.spec["cells"][2]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (self.spec["cells"][1], self.spec["cells"][3]):
            self.assertNotIn("estimator", cell)
            self.assertNotIn("estimator_registration", cell)
        for cell in (self.plan["floor_cells"][0], self.plan["floor_cells"][2]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (self.plan["floor_cells"][1], self.plan["floor_cells"][3]):
            self.assertNotIn("estimator", cell)
            self.assertNotIn("estimator_registration", cell)

    def test_typed_launch_recipes_are_complete_and_portable(self) -> None:
        graph = self.tree["stage_graph"]
        self.assertEqual([stage["ordinal"] for stage in graph], list(range(1, 14)))
        self.assertEqual(sum(len(stage["launch"]["commands"]) for stage in graph), 14)
        allowed_argument_keys = {
            "literal": {"kind", "value"},
            "repo_path": {"kind", "value"},
            "binding": {"kind", "value"},
            "binding_path": {"kind", "value", "relative"},
            "tree_pointer": {"kind", "value"},
        }
        command_ids: list[str] = []
        for stage in graph:
            launch = stage["launch"]
            self.assertEqual(launch["schema_version"], "joulewise.stage_launch.v1")
            self.assertTrue(launch["commands"])
            for command in launch["commands"]:
                self.assertEqual(
                    set(command),
                    {"command_id", "command_kind", "argv_template", "cwd", "success_exit_codes"},
                )
                command_ids.append(command["command_id"])
                self.assertEqual(command["cwd"], {"kind": "binding", "value": "repo_root"})
                self.assertEqual(command["success_exit_codes"], [0])
                template = command["argv_template"]
                self.assertEqual(set(template), {"tool_id", "interface_id", "arguments"})
                for token in template["arguments"]:
                    self.assertIn(token["kind"], allowed_argument_keys)
                    self.assertEqual(set(token), allowed_argument_keys[token["kind"]])
                    self.assertNotIn("$", token["value"])
                    self.assertNotIn("~", token["value"])
                    if token["kind"] in {"repo_path", "binding_path"}:
                        relative = token.get("relative", token["value"])
                        self.assertFalse(Path(relative).is_absolute())
                        self.assertNotIn("..", Path(relative).parts)
        self.assertEqual(len(command_ids), len(set(command_ids)))
        self.assertEqual(
            {row["name"] for row in self.tree["arm_attachments"]["launch"]["bindings"]},
            {
                "repo_root",
                "ledger_path",
                "claim_runs_root",
                "bound_runs_root",
                "operator_log_root",
                "pre_calibration_dir",
                "post_calibration_dir",
                "claim_backup_destination",
                "bound_backup_destination",
                "bracket_session_id",
                "pre_attempt_id",
                "post_attempt_id",
                "identity_epoch_json",
                "t1_bindings_json",
            },
        )

    def test_external_inputs_are_member_level_sha_pinned(self) -> None:
        for manifest in self.tree["external_inputs"]["manifests"]:
            manifest_path = manifest["manifest"]["path"]
            self.assertEqual(manifest["manifest"]["sha256"], EXPECTED_EXTERNAL_SHA256[manifest_path])
            self.assertEqual(sha256_file(ROOT / manifest_path), manifest["manifest"]["sha256"])
            self.assertEqual(manifest["expected_count"], len(manifest["members"]))
            for index, member in enumerate(manifest["members"], start=1):
                self.assertEqual(member["ordinal"], index)
                self.assertEqual(member["sha256"], sha256_file(ROOT / member["path"]))
        for artifact in self.tree["external_inputs"]["artifacts"]:
            self.assertEqual(artifact["sha256"], EXPECTED_EXTERNAL_SHA256[artifact["path"]])
            self.assertEqual(artifact["sha256"], sha256_file(ROOT / artifact["path"]))

    def test_ids_are_fresh_and_arm_pins_are_projection_owned(self) -> None:
        run_ids = {row["run_id"] for row in self.root_manifest["executed_order"]}
        historical_ids: set[str] = set()
        for path in (
            ROOT / "configs/campaigns/p2_015_floors/order_manifest.json",
            ROOT / "configs/campaigns/qwen25_7b_decode_floor_v1/order_manifest.json",
        ):
            historical_ids.update(row["run_id"] for row in load_json(path)["executed_order"])
        self.assertTrue(run_ids.isdisjoint(historical_ids))
        self.assertEqual(self.plan["plan_id"], PLAN_ID)
        self.assertEqual(self.tree["window_identity"]["window_id"], PLAN_ID)
        self.assertEqual(self.tree["window_identity"]["evidence_root_id"], EVIDENCE_ROOT_ID)
        self.assertEqual(self.plan["draft_status"], "unfrozen_draft")
        self.assertEqual(self.tree["draft_status"], "unfrozen_draft")
        self.assertEqual(self.producer["draft_status"], "unfrozen_draft")
        for manifest_path in [
            PACK_ROOT / "order_manifest.json",
            *sorted(PACK_ROOT.glob("*/order_manifest.json")),
        ]:
            self.assertEqual(load_json(manifest_path)["draft_status"], "unfrozen_draft")
        self.assertIn(
            "A successor acceptance artifact issuing before arm REQUIRES pack regeneration",
            self.spec["successor_acceptance_artifact_policy"],
        )
        self.assertIn(
            self.spec["successor_acceptance_artifact_policy"],
            (PACK_ROOT / "README.md").read_text(encoding="utf-8"),
        )
        projection = self.producer["identity_pin_projection"]
        self.assertEqual(projection["work_order"], "D117-U11-IDPIN-PROJECTION")
        self.assertEqual(projection["mode"], "derive_never_operator_enter")
        self.assertEqual(projection["state"], "unprojected")
        self.assertEqual(projection["derivation_contract"], IDENTITY_PIN_DERIVATION_CONTRACT)
        self.assertEqual(projection["supersedes"], [])
        self.assertEqual(len(projection["identity_units"]), 1)
        unit = projection["identity_units"][0]
        self.assertEqual(unit["identity_unit_id"], "alpha")
        self.assertEqual(set(unit["model_runtime_config"].values()), {None})
        computed_config_hashes = {
            scientific_config_identity_sha256(load_json(PACK_ROOT / row["path"]))
            for row in unit["config_inventory"]
        }
        self.assertEqual(len(computed_config_hashes), 1)
        for row in unit["config_inventory"]:
            self.assertEqual(row["sha256"], sha256_file(PACK_ROOT / row["path"]))
        self.assertIsNone(projection["projection_receipt"])
        self.assertEqual(
            self.tree["arm_attachments"]["identity_pin_projection"], projection
        )

    def test_receipt_oracle_is_recomputed_from_the_production_model(self) -> None:
        expected = derive_bracket_session_receipt_oracle()
        actual = self.tree["arm_attachments"]["receipt_oracle"]
        self.assertEqual(actual, expected)
        self.assertIsNone(actual["terminal_sequence"])
        self.assertEqual(actual["arm_time_receipts"], [])
        closeout = self.tree["closeout_attachments"]
        self.assertEqual(closeout["postcollection_receipt_digests"], [])
        self.assertIsNone(closeout["terminal_ledger_head"])
        stale_marker = "impl/d117-" + "ledger-recovery"
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK_ROOT.rglob("*"))
            if path.is_file() and path.suffix in {".json", ".md", ".py", ".sha256"}
        )
        self.assertNotIn(stale_marker, generated_text)

    def test_no_historical_claim_bytes_or_generation_discovery(self) -> None:
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK_ROOT.rglob("*"))
            if path.is_file() and path.suffix in {".json", ".md", ".sha256"}
        )
        for forbidden in (
            "runs_window_d_20260726",
            "runs/a10",
            "7.377086",
            "6.294380",
            "13.998036",
            "frozen_before_measurement",
            '"freeze_status"',
        ):
            self.assertNotIn(forbidden, generated_text)
        source = GENERATOR.read_text(encoding="utf-8")
        for forbidden in (".glob(", "os.walk(", "Path.walk("):
            self.assertNotIn(forbidden, source)
        self.assertIn('.rglob("*")', source)


if __name__ == "__main__":
    unittest.main()
