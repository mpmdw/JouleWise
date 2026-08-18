from __future__ import annotations

import hashlib
import importlib.util
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
from typing import Iterable
from unittest import mock

import joulewise.floor_extraction as floor_extraction
from joulewise.detection_floor import (
    COMMON_MODE_ESTIMATOR_ID,
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    two_shared_edge_common_mode_registration,
)
from joulewise.floor_mint_estimator import selection_from_authenticated_spec
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
V1_SPEC_RELS = (
    Path("configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json"),
    SPEC.relative_to(REPO_ROOT),
)
GENERATOR = PACK / "generate_configs.py"
GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "d117_beta_generator", GENERATOR
)
assert GENERATOR_SPEC is not None and GENERATOR_SPEC.loader is not None
GENERATOR_MODULE = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(GENERATOR_MODULE)
OLD_PACK = REPO_ROOT / "configs/campaigns/qwen25_7b_decode_floor_v1"

PLAN_ID = "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-7b-v1"
DECODE_FAMILY_ID = "df-ph-decode-qwen25-7b"
PREFILL_FAMILY_ID = "df-ph-prefill-p128-qwen25-7b"
P256_FAMILY_ID = "df-ph-prefill-p256-qwen25-7b"
CONTRAST_PACK = REPO_ROOT / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1"
LEGACY_DECODE_PLAN_SHA256 = "c20ef596f64a4a8d5367a963614c4db0f2c34a7077441e204bcf22e2b1033f40"
FROZEN_GENERATOR_SHA256 = "5519b18ae971fd3655af5d7e7be67d4462ee1fd487e179ba9961cb971a1c6dca"

EXPECTED_SHA256 = {
    "calibration_plan.json": (
        "77056ffc154fc8d3fd461233a6ab54800a25055fdf3296c974996c32bd9612a0"
    ),
    "calibration_plan.sha256": (
        "e57dc2beba16a5ee7687a2c7031e82f80bdb084bd4ad09ce7745fbef8f4fe031"
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
        "4229ae2497410b90950948b7bf74cd938cb7390b4c3999ecb5ad34ddd9c7818e"
    ),
    "01_phase_decode_absolute/order_manifest.json": (
        "36a5fae72b37643550ecb4471b4566db30331a4089abc3f4827593632407bba2"
    ),
    "02_phase_decode_abba_blocks_01_05/order_manifest.json": (
        "402ef473f3d7a14daeecb8178107aaf30057c6211fb285d846ed88bcd846111c"
    ),
    "03_phase_decode_abba_blocks_06_10/order_manifest.json": (
        "28cb8a5f89000fc91a1b20cc88514f1c5ecf0260bf7594e67fb628b103e7db97"
    ),
    "04_phase_prefill_p256_absolute/order_manifest.json": (
        "1e279684438d7eb5dea92f3bd01eff61c8c48aeaf70c86c5ec99fde5d4bca35a"
    ),
    "05_phase_prefill_p256_abba_blocks_01_05/order_manifest.json": (
        "b8d29e3bcd45e16653f0b369beeca838bf1b90ca05c66ceeed2ce921cc5fb610"
    ),
    "06_phase_prefill_p256_abba_blocks_06_10/order_manifest.json": (
        "82bb3363e44d7165655634e69f2647d2bb00ea05046647e401eec04adc68b67a"
    ),
    "order_manifest.json": (
        "16d6d49e7c49f18909c2c3e5ec38e9d485fdfc54b444180c93c9d25c04bc2787"
    ),
    "plan_tree.json": (
        "428301690ab8c765d65898638d861e21d0522003e51d06a637e1881316423242"
    ),
    "plan_tree.sha256": (
        "ea3f9cb18ae70a1b6d8b229de131246dacfc59fda940c2c99a4bee55667511e7"
    ),
    "producer_contract.json": (
        "23246a97191bc5136e880e190dc8d88ac6e97925a690f67957150fa28c46d35e"
    ),
}
EXPECTED_SPEC_SHA256 = (
    "86809f31d2c6933cda42881e10a32bc521cddec01fa941ac4613cd32b9ef49b8"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checkout_inventory(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
    }


def initialize_git_tracked_checkout(
    checkout_root: Path, pathspecs: Iterable[Path]
) -> set[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "--", *(path.as_posix() for path in pathspecs)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = {Path(line) for line in listed.stdout.splitlines() if line}
    if not tracked:
        raise AssertionError("real-checkout fixture has no git-tracked inputs")
    for relative in tracked:
        target = checkout_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, target)
    subprocess.run(
        ["git", "init", "-q"],
        cwd=checkout_root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "add", "--", *(path.as_posix() for path in sorted(tracked))],
        cwd=checkout_root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=D117 fixture",
            "-c",
            "user.email=d117-fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "git-tracked D117 checkout fixture",
        ],
        cwd=checkout_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return tracked


def git_status(checkout_root: Path) -> str:
    return subprocess.run(
        ["git", "status", "--short"],
        cwd=checkout_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def commit_fixture(checkout_root: Path, message: str) -> None:
    subprocess.run(["git", "add", "-f", "."], cwd=checkout_root, check=True)
    subprocess.run(
        [
            "git", "-c", "user.name=D117 fixture",
            "-c", "user.email=d117-fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-q", "-m", message,
        ],
        cwd=checkout_root,
        check=True,
    )


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


def governed_frozen_attachment_paths(pack_root: Path) -> set[str]:
    tree = load_json(pack_root / "plan_tree.json")
    expected: set[Path] = set()
    freeze_reference = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
    if freeze_reference is not None:
        freeze_path = Path(freeze_reference["path"])
        expected |= {
            freeze_path,
            freeze_path.with_name(f"{freeze_path.name}.sha256"),
        }
        receipt = load_json(pack_root / freeze_path)
        for item in receipt["evidence"]:
            evidence_path = Path(item["path"])
            sidecar = (
                evidence_path.with_suffix(".sha256")
                if evidence_path.parent.name == "identity_pin_projection.receipts"
                else evidence_path.with_name(f"{evidence_path.name}.sha256")
            )
            expected |= {evidence_path, sidecar}
            evidence = load_json(pack_root / evidence_path)
            expected.update(
                Path(fact["source_path"])
                for fact in evidence.get("facts", [])
                if "source_path" in fact
            )
    projection_reference = tree["arm_attachments"]["identity_pin_projection"][
        "projection_receipt"
    ]
    if projection_reference is not None:
        projection_path = Path(projection_reference["path"])
        expected |= {projection_path, projection_path.with_suffix(".sha256")}
    return {path.as_posix() for path in expected}


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
    return paths | governed_frozen_attachment_paths(PACK)


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


def link_successor_self_check_inputs(output_root: Path) -> None:
    if not (output_root / "joulewise").exists():
        (output_root / "joulewise").symlink_to(
            REPO_ROOT / "joulewise", target_is_directory=True
        )
    for source_dir in (
        REPO_ROOT / "configs",
        REPO_ROOT / "configs/campaigns",
        REPO_ROOT / "configs/floor_mint",
    ):
        target_dir = output_root / source_dir.relative_to(REPO_ROOT)
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in source_dir.iterdir():
            target = target_dir / source.name
            if not target.exists():
                target.symlink_to(source, target_is_directory=source.is_dir())
    successor_contrast = (
        output_root / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2"
    )
    if not successor_contrast.exists():
        successor_contrast.symlink_to(CONTRAST_PACK, target_is_directory=True)


class D117Qwen25SevenBPlanTests(unittest.TestCase):
    maxDiff = None

    def test_exact_inventory_hashes_and_sidecars(self) -> None:
        # Exclude interpreter byte-code caches: importing
        # generate_configs.py (which this suite does) drops __pycache__
        # into the pack, so an unfiltered inventory passes on a fresh
        # checkout and fails on every later run. Aligned with the gamma
        # generator/suite filter (cold-gate C5).
        actual = {
            path.relative_to(PACK).as_posix()
            for path in PACK.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(actual, expected_pack_paths())
        self.assertEqual(len(actual), 154)
        for relative, expected in EXPECTED_SHA256.items():
            self.assertEqual(file_sha256(PACK / relative), expected, relative)
        self.assertEqual(file_sha256(SPEC), EXPECTED_SPEC_SHA256)
        self.assertEqual(
            load_json(PACK / "plan_tree.json")["generator"]["sha256"],
            FROZEN_GENERATOR_SHA256,
        )

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
                    [
                        sys.executable,
                        str(GENERATOR),
                        "--output-root",
                        str(output),
                        "--preserve-current-frozen-bytes",
                    ],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            generated_paths = {
                path.as_posix() for path in GENERATOR_MODULE.expected_pack_files()
            }
            for relative in sorted(generated_paths):
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

    def test_freeze_aware_successor_contract_is_forward_only(self) -> None:
        self.assertEqual(GENERATOR_MODULE.freeze_aware_status(None), "unfrozen_draft")
        self.assertEqual(
            GENERATOR_MODULE.freeze_aware_status(
                {"sha256": GENERATOR_MODULE.CURRENT_FROZEN_RECEIPT_SHA256}
            ),
            "unfrozen_draft",
        )
        self.assertEqual(
            GENERATOR_MODULE.freeze_aware_status({"sha256": "0" * 64}),
            "frozen_by_d134_receipt",
        )
        self.assertEqual(
            GENERATOR_MODULE.freeze_aware_reservation_plan_arguments(
                GENERATOR_MODULE.GenerationIdentity()
            ),
            [],
        )
        future_identity = GENERATOR_MODULE.GenerationIdentity(
            pack_id="d117_floor_qwen25_7b_v2",
            family_suffix="_v2",
            preserve_current_frozen_bytes=False,
        )
        future = GENERATOR_MODULE.freeze_aware_reservation_plan_arguments(
            future_identity
        )
        self.assertEqual(
            [argument["value"] for argument in future],
            ["--plan", (future_identity.pack_rel / "calibration_plan.json").as_posix()],
        )
        # Holding 6 of the 2026-08-18 cold-gate verdict: the frozen-status
        # README branch is REMOVED, not merely unreachable. A frozen dynamic
        # status must leave the emitted description exactly as committed, and
        # the successor description must be freeze-neutral -- true on both
        # sides of its own D-134 receipt, naming the receipt and its plan-tree
        # attachment as the status authority, asserting nothing about
        # armability or unfrozenness.
        with mock.patch.object(
            GENERATOR_MODULE,
            "ARM_READINESS_ATTACHMENT",
            {"freeze_receipt": {"sha256": "0" * 64}},
        ):
            frozen_state_readme = GENERATOR_MODULE.readme()
        self.assertEqual(frozen_state_readme, (PACK / "README.md").read_bytes())
        with GENERATOR_MODULE.generation_context(future_identity):
            successor_readme = GENERATOR_MODULE.readme().decode("utf-8")
        self.assertIn(
            "The committed D-134 freeze receipt and its plan-tree attachment "
            "are authoritative",
            " ".join(successor_readme.split()),
        )
        for denial in ("unfrozen draft", "unfrozen_draft", "not armable"):
            self.assertNotIn(denial, successor_readme)
        self.assertNotIn(
            "frozen by D-134 receipt", GENERATOR.read_text(encoding="utf-8")
        )

    def test_target_status_inventory_and_invalid_modes_are_fail_closed(self) -> None:
        successor = GENERATOR_MODULE.GenerationIdentity(
            pack_id="d117_floor_qwen25_7b_v2",
            family_suffix="_v2",
            preserve_current_frozen_bytes=False,
        )
        self.assertEqual(successor.current_ordinal, 1)
        self.assertEqual(successor.target_ordinal, 2)
        self.assertFalse(successor.target_is_current)
        self.assertTrue(successor.target_is_successor_family)
        self.assertEqual(successor.target_status, "unfrozen_draft")
        with mock.patch.object(
            GENERATOR_MODULE,
            "ARM_READINESS_ATTACHMENT",
            {"freeze_receipt": {"sha256": "0" * 64}},
        ):
            current = GENERATOR_MODULE.GenerationIdentity()
            self.assertEqual(current.target_status, "frozen_by_d134_receipt")
        source = GENERATOR.read_text(encoding="utf-8")
        self.assertEqual(
            source.count('"draft_status": emitted_draft_status()'), 6
        )
        artifacts = GENERATOR_MODULE.build_artifacts(successor)
        expected = {
            *(successor.pack_rel / path for path in GENERATOR_MODULE.expected_pack_files()),
            GENERATOR_MODULE.extraction_spec_rel(successor),
        }
        self.assertEqual(set(artifacts), expected)
        for pack_id, suffix, preserve in (
            ("d117_floor_qwen25_7b_v0", "_v0", False),
            ("d117_floor_qwen25_7b_v2", "_v2", True),
        ):
            with self.subTest(pack_id=pack_id), tempfile.TemporaryDirectory() as temp:
                output_root = Path(temp)
                rejected = subprocess.run(
                    [
                        sys.executable, str(GENERATOR), "--output-root", str(output_root),
                        "--pack-id", pack_id, "--family-suffix", suffix,
                        "--preserve-current-frozen-bytes"
                        if preserve else "--no-preserve-current-frozen-bytes",
                    ],
                    cwd=REPO_ROOT, check=False, capture_output=True, text=True,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertEqual(checkout_inventory(output_root), set())

    def test_generation_refuses_symlinked_write_inventory_before_any_write(self) -> None:
        successor = GENERATOR_MODULE.GenerationIdentity(
            pack_id="d117_floor_qwen25_7b_v2",
            family_suffix="_v2",
            preserve_current_frozen_bytes=False,
        )
        cases = {
            "pack_directory": (successor.pack_rel, True),
            "pack_file": (successor.pack_rel / "README.md", False),
            "extraction_spec": (
                GENERATOR_MODULE.extraction_spec_rel(successor),
                False,
            ),
            "sidecar": (
                successor.pack_rel / "calibration_plan.sha256",
                False,
            ),
        }
        for name, (relative, is_directory) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(
                prefix="d117-beta-symlink-root-"
            ) as temp, tempfile.TemporaryDirectory(
                prefix="d117-beta-symlink-escape-"
            ) as escape:
                output_root = Path(temp)
                escape_root = Path(escape)
                target = output_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                destination = (
                    escape_root if is_directory else escape_root / f"{name}.escaped"
                )
                target.symlink_to(destination, target_is_directory=is_directory)
                before = checkout_inventory(output_root)
                rejected = subprocess.run(
                    [
                        sys.executable,
                        str(GENERATOR),
                        "--output-root",
                        str(output_root),
                        "--pack-id",
                        successor.pack_id,
                        "--family-suffix",
                        successor.family_suffix,
                        "--no-preserve-current-frozen-bytes",
                    ],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("refusing generation", rejected.stderr)
                self.assertIn(str(target), rejected.stderr)
                self.assertIn(str(destination.resolve(strict=False)), rejected.stderr)
                self.assertEqual(checkout_inventory(output_root), before)
                self.assertEqual(list(escape_root.iterdir()), [])

    def test_successor_generation_threads_plan_identity_and_lineage(self) -> None:
        successor_id = "d117_floor_qwen25_7b_v2"
        successor_rel = PACK.relative_to(REPO_ROOT).with_name(successor_id)
        successor_spec_rel = Path(
            "configs/floor_mint/d117_qwen25_7b_v2_extraction_spec.json"
        )
        with tempfile.TemporaryDirectory(prefix="d117-beta-v2-") as temp:
            output_root = Path(temp)
            tracked = initialize_git_tracked_checkout(
                output_root, (PACK.relative_to(REPO_ROOT), *V1_SPEC_RELS)
            )
            self.assertTrue(set(V1_SPEC_RELS) <= tracked)
            baseline_inventory = checkout_inventory(output_root)
            v1_spec_hashes = {
                relative: file_sha256(output_root / relative)
                for relative in V1_SPEC_RELS
            }
            preserved = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--output-root",
                    str(output_root),
                    "--preserve-current-frozen-bytes",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(preserved.returncode, 0, preserved.stderr)
            self.assertEqual(git_status(output_root), "")
            self.assertEqual(checkout_inventory(output_root), baseline_inventory)
            self.assertEqual(
                {
                    relative: file_sha256(output_root / relative)
                    for relative in V1_SPEC_RELS
                },
                v1_spec_hashes,
            )
            command = [
                sys.executable,
                str(GENERATOR),
                "--output-root",
                str(output_root),
                "--pack-id",
                successor_id,
                "--family-suffix",
                "_v2",
                "--no-preserve-current-frozen-bytes",
            ]
            generated = subprocess.run(
                command,
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            expected_writes = {
                successor_rel / relative
                for relative in GENERATOR_MODULE.expected_pack_files()
            } | {successor_spec_rel}
            self.assertEqual(
                checkout_inventory(output_root) - baseline_inventory,
                expected_writes,
            )
            self.assertEqual(
                subprocess.run(
                    ["git", "diff", "--quiet"],
                    cwd=output_root,
                    check=False,
                ).returncode,
                0,
            )
            self.assertEqual(
                {
                    relative: file_sha256(output_root / relative)
                    for relative in V1_SPEC_RELS
                },
                v1_spec_hashes,
            )
            checked = subprocess.run(
                [*command, "--check"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)

            pack_root = output_root / successor_rel
            tree = load_json(pack_root / "plan_tree.json")
            producer = load_json(pack_root / "producer_contract.json")
            successor_spec = load_json(output_root / successor_spec_rel)
            root_manifest = load_json(pack_root / "order_manifest.json")
            root_manifest_sha256 = file_sha256(pack_root / "order_manifest.json")
            self.assertEqual(tree["plan"]["path"], "calibration_plan.json")
            self.assertEqual(tree["plan"]["sidecar_path"], "calibration_plan.sha256")
            self.assertEqual(producer["plan"]["path"], tree["plan"]["path"])
            self.assertEqual(tree["plan"]["plan_id"], PLAN_ID.removesuffix("v1") + "v2")
            self.assertEqual(
                tree["window_identity"]["evidence_root_id"],
                EVIDENCE_ROOT_ID.removesuffix("v1") + "v2",
            )
            self.assertEqual(
                tree["downstream_contract"]["extraction_spec"]["path"],
                successor_spec_rel.as_posix(),
            )
            self.assertEqual(
                producer["extraction_spec"]["path"], successor_spec_rel.as_posix()
            )
            self.assertEqual(
                tree["downstream_contract"]["extraction_spec"]["sha256"],
                file_sha256(output_root / successor_spec_rel),
            )
            self.assertEqual(
                producer["extraction_spec"]["sha256"],
                file_sha256(output_root / successor_spec_rel),
            )
            root_configs = {
                row["run_id"]: row["config_sha256"]
                for row in root_manifest["executed_order"]
            }
            for cell in successor_spec["cells"]:
                self.assertEqual(
                    cell["order_manifest"],
                    {
                        "path": (successor_rel / "order_manifest.json").as_posix(),
                        "manifest_id": root_manifest["manifest_id"],
                        "sha256": root_manifest_sha256,
                    },
                )
                self.assertEqual(
                    cell["evidence_root_id"],
                    EVIDENCE_ROOT_ID.removesuffix("v1") + "v2",
                )
                self.assertEqual(
                    cell["member_config_sha256"],
                    [
                        {
                            "bundle_id": row["bundle_id"],
                            "config_sha256": root_configs[row["bundle_id"]],
                        }
                        for row in cell["member_config_sha256"]
                    ],
                )
            reservation = next(
                stage
                for stage in tree["stage_graph"]
                if stage["kind"] == "bracket_reservation"
            )
            arguments = reservation["launch"]["commands"][0]["argv_template"][
                "arguments"
            ]
            plan_index = next(
                index
                for index, token in enumerate(arguments)
                if token == {"kind": "literal", "value": "--plan"}
            )
            plan_token = arguments[plan_index + 1]
            expected_plan = (successor_rel / tree["plan"]["path"]).as_posix()
            self.assertEqual(plan_token, {"kind": "repo_path", "value": expected_plan})
            self.assertEqual(
                output_root / plan_token["value"],
                pack_root / tree["plan"]["path"],
            )
            for row in tree["science"]:
                config = load_json(output_root / row["config_path"])
                self.assertIn(
                    "launch_lineage_required", config["run_metadata"]["tags"]
                )

            self_referential = {
                name: (pack_root / name).read_text(encoding="utf-8")
                for name in ("README.md", "generate_configs.py")
            }
            predecessor_markers = {
                *GENERATOR_MODULE._SUCCESSOR_IDENTITY_TOKENS,
                'CURRENT_FAMILY_SUFFIX = "_v1"',
            }
            for name, content in self_referential.items():
                with self.subTest(self_referential=name):
                    for marker in predecessor_markers:
                        self.assertNotIn(marker, content)
                    self.assertIn(successor_id, content)
            self.assertIn(
                'CURRENT_FAMILY_SUFFIX = "_v2"',
                self_referential["generate_configs.py"],
            )
            self.assertIn(
                f"python3 {successor_rel.as_posix()}/generate_configs.py --check",
                self_referential["README.md"],
            )

            link_successor_self_check_inputs(output_root)
            embedded_check = subprocess.run(
                [
                    sys.executable,
                    str(pack_root / "generate_configs.py"),
                    "--check",
                    "--output-root",
                    str(output_root),
                ],
                cwd=output_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(embedded_check.returncode, 0, embedded_check.stderr)
            self.assertIn(successor_id, embedded_check.stdout)

            commit_fixture(output_root, "track emitted beta v2")
            tracked_spec_hashes = {
                relative: file_sha256(output_root / relative)
                for relative in (*V1_SPEC_RELS, successor_spec_rel)
            }
            preserve_command = [
                sys.executable,
                str(pack_root / "generate_configs.py"),
                "--output-root",
                str(output_root),
                "--preserve-current-frozen-bytes",
            ]
            preserve_check = subprocess.run(
                [*preserve_command, "--check"],
                cwd=output_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(preserve_check.returncode, 0, preserve_check.stderr)
            preserve_generate = subprocess.run(
                preserve_command,
                cwd=output_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(preserve_generate.returncode, 0, preserve_generate.stderr)
            self.assertEqual(git_status(output_root), "")
            self.assertEqual(
                {
                    relative: file_sha256(output_root / relative)
                    for relative in (*V1_SPEC_RELS, successor_spec_rel)
                },
                tracked_spec_hashes,
            )
            self.assertFalse(
                (output_root / "configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json").exists()
            )
            preserved_tree = load_json(pack_root / "plan_tree.json")
            for row in preserved_tree["science"]:
                config = load_json(output_root / row["config_path"])
                self.assertIn("launch_lineage_required", config["run_metadata"]["tags"])

        current_tree = load_json(PACK / "plan_tree.json")
        for row in current_tree["science"]:
            current = load_json(REPO_ROOT / row["config_path"])
            self.assertNotIn(
                "launch_lineage_required", current["run_metadata"]["tags"]
            )

    def test_generator_check_mode(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(GENERATOR),
                "--check",
                "--preserve-current-frozen-bytes",
            ],
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
            self.assertEqual(cell["estimator"], COMMON_MODE_ESTIMATOR_ID)
            self.assertEqual(
                cell["estimator_registration"],
                two_shared_edge_common_mode_registration(),
            )
            self.assertEqual(
                cell["estimator_registration"]["parameter_sha256"],
                "dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38",
            )
            self.assertEqual(
                selection_from_authenticated_spec(
                    cell,
                    calibration_acceptance=load_json(
                        REPO_ROOT
                        / "configs/calibration/calibration_acceptance_d079_v2.json"
                    ),
                    calibration_acceptance_sha256=(
                        "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
                    ),
                    calibration_allowance_projection={
                        "observed_drift_s": "0.001000",
                        "allowance_rule": "max(observed_drift_s,0.010818)",
                        "bracket_screen_s": "0.010818",
                        "applied_allowance_s": "0.010818",
                        "allowance_embedding_count": 1,
                    },
                    declared_calibration_scope="production_window",
                ),
                "common_mode",
            )
            self.assertEqual(
                cell["calibration_basis"]["allowance_embedding_count"], 1
            )
        plan = load_json(PACK / "calibration_plan.json")
        for cell in (plan["floor_cells"][0], plan["floor_cells"][2], plan["floor_cells"][4]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (plan["floor_cells"][1], plan["floor_cells"][3], plan["floor_cells"][5]):
            self.assertEqual(cell["estimator"], COMMON_MODE_ESTIMATOR_ID)
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
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix in {".json", ".md", ".py", ".sha256"}
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
        self.assertEqual(projection["state"], "frozen")
        self.assertEqual(projection["derivation_contract"], IDENTITY_PIN_DERIVATION_CONTRACT)
        self.assertEqual(projection["supersedes"], [])
        self.assertEqual(len(projection["identity_units"]), 2)
        self.assertEqual(
            [unit["identity_unit_id"] for unit in projection["identity_units"]],
            ["beta", "beta/prefill_p256"],
        )
        unit = projection["identity_units"][0]
        self.assertEqual(unit["identity_unit_id"], "beta")
        self.assertTrue(
            all(
                isinstance(value, str) and len(value) == 64
                for value in unit["model_runtime_config"].values()
            )
        )
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
        projection_receipt = projection["projection_receipt"]
        self.assertIsNotNone(projection_receipt)
        receipt_path = PACK / projection_receipt["path"]
        self.assertEqual(file_sha256(receipt_path), projection_receipt["sha256"])
        self.assertEqual(
            receipt_path.with_suffix(".sha256").read_text(encoding="utf-8"),
            f"{projection_receipt['sha256']}  {receipt_path.name}\n",
        )
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
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix in {".json", ".md", ".sha256"}
        )
        for diagnostic in ("6." + "294380", "13." + "998036"):
            self.assertNotIn(diagnostic, generated_text)


if __name__ == "__main__":
    unittest.main()
