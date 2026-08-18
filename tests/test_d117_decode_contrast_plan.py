from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Iterable
from unittest import mock

from joulewise.schemas import BenchmarkConfig
from joulewise.detection_floor import two_shared_edge_common_mode_registration
from joulewise.identity_pins import (
    IDENTITY_PIN_DERIVATION_CONTRACT,
    scientific_config_identity_sha256,
)
from joulewise.receipt_oracle import derive_bracket_session_receipt_oracle
from scripts.run_campaign import load_order_entries


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "configs" / "campaigns" / "d117_contrast_qwen25_1p5b_vs_7b_v1"
GENERATOR = PACK / "generate_configs.py"
GENERATOR_SPEC = importlib.util.spec_from_file_location("d117_gamma_generator", GENERATOR)
assert GENERATOR_SPEC is not None and GENERATOR_SPEC.loader is not None
GENERATOR_MODULE = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(GENERATOR_MODULE)
V1_SPEC_RELS = (
    Path("configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json"),
    Path("configs/floor_mint/d117_qwen25_7b_extraction_spec.json"),
)
ROW_REGISTRY_REL = Path("configs/arm_readiness/d117_row_registry_v1.json")

EXACT_SHAS = {
    "generate_configs.py": "595f142f70362d20360e63779fe3496a8b776e5058768f0a5d2129d2bd5f9ed3",
    "calibration_plan.json": "4609b74f5b1b40eb4576a1f389c5d90be3edde532bdc017314cdb300c485a218",
    "plan_tree.json": "8c53a834d78c81145b8f35b25f8d50182d596dc82c171e815f8a160117ab525d",
    "analysis_manifest_v3.json": "e3bc0e3620be2a25c60a6dc7bcab0910997d7d97030f5e80727cd5d951559a57",
    "prefill_prompt_candidate.json": "9e1d8eecb688a4ae54c76d24d71be618411c011fa5bebffa44ad6a91ef03d456",
    "consumer_family_declaration.json": "5c0950a6180346b53913e28cf12c78dcb9b97dfd1c9878158fe6619aa227d575",
}
FROZEN_GENERATOR_SHA256 = "550035ae92199185e9ad21ae0277593e4821c1788f645ee5345bd6d3268a1c09"
POSITIONS = ["A1", "B1", "B2", "A2"]
LABELS = ["A", "B", "B", "A"]


def sha256(path: Path) -> str:
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
        cwd=ROOT,
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
        shutil.copy2(ROOT / relative, target)
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


def hash_inventory(checkout_root: Path, roots: Iterable[Path]) -> dict[Path, str]:
    inventory: dict[Path, str] = {}
    for relative_root in roots:
        absolute_root = checkout_root / relative_root
        candidates = [absolute_root] if absolute_root.is_file() else absolute_root.rglob("*")
        for path in candidates:
            if path.is_file() and "__pycache__" not in path.parts:
                inventory[path.relative_to(checkout_root)] = sha256(path)
    return inventory


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return value


def actual_inventory(root: Path) -> set[Path]:
    # Exclude interpreter byte-code caches: importing generate_configs.py
    # (which this suite does) creates __pycache__ inside the pack, so an
    # unfiltered inventory passes on a fresh checkout and fails on every
    # later run.
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def governed_frozen_attachment_paths(pack_root: Path) -> set[Path]:
    tree = read_json(pack_root / "plan_tree.json")
    expected: set[Path] = set()
    freeze_reference = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
    if freeze_reference is not None:
        freeze_path = Path(freeze_reference["path"])
        expected |= {
            freeze_path,
            freeze_path.with_name(f"{freeze_path.name}.sha256"),
        }
        receipt = read_json(pack_root / freeze_path)
        for item in receipt["evidence"]:
            evidence_path = Path(item["path"])
            sidecar = (
                evidence_path.with_suffix(".sha256")
                if evidence_path.parent.name == "identity_pin_projection.receipts"
                else evidence_path.with_name(f"{evidence_path.name}.sha256")
            )
            expected |= {evidence_path, sidecar}
            evidence = read_json(pack_root / evidence_path)
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
    return expected


def link_successor_self_check_inputs(output_root: Path) -> None:
    if not (output_root / "joulewise").exists():
        (output_root / "joulewise").symlink_to(ROOT / "joulewise", target_is_directory=True)
    for source_dir in (ROOT / "configs", ROOT / "configs/campaigns"):
        target_dir = output_root / source_dir.relative_to(ROOT)
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in source_dir.iterdir():
            target = target_dir / source.name
            if not target.exists():
                target.symlink_to(source, target_is_directory=source.is_dir())


def install_v2_freeze_fixture_runtime(output_root: Path) -> Path:
    """Install the exact freeze CLI with its unavailable fixture inputs modeled."""

    joulewise_path = output_root / "joulewise"
    if joulewise_path.is_symlink():
        joulewise_path.unlink()
    shutil.copytree(ROOT / "joulewise", joulewise_path)
    arm_readiness_path = joulewise_path / "arm_readiness.py"
    source = arm_readiness_path.read_text(encoding="utf-8")
    marker = "_PROFILE_BY_PACK = {\n"
    if source.count(marker) != 1:
        raise AssertionError("D-134 profile map marker is not unique")
    additions = (
        '    "d117_floor_qwen25_1p5b_v2": "ALPHA",\n'
        '    "d117_floor_qwen25_7b_v2": "BETA",\n'
        '    "d117_contrast_qwen25_1p5b_vs_7b_v2": "GAMMA",\n'
    )
    source = source.replace(marker, marker + additions)
    boot_start = source.index("def _current_boot_session_id() -> str:\n")
    boot_end = source.index("\ndef _pairs_no_duplicates", boot_start)
    source = (
        source[:boot_start]
        + "def _current_boot_session_id() -> str:\n"
        + '    return "00000000-0000-4000-8000-000000000001"\n\n'
        + source[boot_end + 1 :]
    )
    arm_readiness_path.write_text(source, encoding="utf-8")
    scripts_path = output_root / "scripts"
    scripts_path.mkdir()
    freeze_script = scripts_path / "generate_arm_readiness.py"
    shutil.copy2(ROOT / "scripts/generate_arm_readiness.py", freeze_script)
    if freeze_script.read_bytes() != (
        ROOT / "scripts/generate_arm_readiness.py"
    ).read_bytes():
        raise AssertionError("fixture freeze CLI differs from the production route")
    return freeze_script


def remove_v2_freeze_fixture_runtime(output_root: Path) -> None:
    shutil.rmtree(output_root / "joulewise")
    (output_root / "joulewise").symlink_to(
        ROOT / "joulewise", target_is_directory=True
    )
    shutil.rmtree(output_root / "scripts")


NO_BYTECODE_ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

_FREEZE_STATE_PROBE = """
import hashlib
import importlib.util
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("freeze_state_probe", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
identity = module.GenerationIdentity(preserve_current_frozen_bytes=True)
render_readme = getattr(module, "readme_bytes", None) or module.readme
with module.generation_context(identity):
    payload = {
        "target_status": identity.target_status,
        "emitted_draft_status": module.emitted_draft_status(),
        "readme_sha256": hashlib.sha256(render_readme()).hexdigest(),
    }
print(json.dumps(payload))
"""

_FREEZE_AUTHENTICATION_PROBE = """
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.cwd()))
from joulewise.arm_readiness import (
    ArmReadinessError,
    _load_freeze_reference,
    _pack_identity,
    _plan_tree,
    _registry_reference,
    scan_receipt_namespace,
)

root = pathlib.Path(sys.argv[1]).resolve()
tree, _tree_raw = _plan_tree(root)
registry, _registry_raw, registry_reference = _registry_reference(root)
reference = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
matches = [
    item
    for item in scan_receipt_namespace(
        root / "arm_readiness.freeze.receipts", "freeze"
    )
    if f"arm_readiness.freeze.receipts/{item['path'].name}" == reference["path"]
    and item["sha256"] == reference["sha256"]
]
receipt = matches[0]["receipt"] if len(matches) == 1 else None
payload = {
    "receipt_resolved": receipt is not None,
    "receipt_sha256": reference["sha256"],
    "status": receipt["status"] if receipt else None,
    "identity_matches_committed_bytes": (
        receipt["pack_identity"] == _pack_identity(root, tree) if receipt else False
    ),
    "plan_sha256": receipt["pack_identity"]["plan_sha256"] if receipt else None,
}
try:
    _load_freeze_reference(
        root, tree, registry_reference, registry, require_pass=False
    )
except ArmReadinessError as exc:
    payload["gate_reason_code"] = exc.refusal()["code"]
else:
    payload["gate_reason_code"] = None
print(json.dumps(payload))
"""


def probe_generator_freeze_state(generator: Path, cwd: Path) -> dict[str, str]:
    """Report what a pack's own generator says about its freeze state.

    Keeps apart the two things the 2026-08-18 cold-gate verdict keeps apart:
    ``target_status``, the DYNAMIC state read from the authenticated freeze
    attachment, which must report frozen once a genuine receipt is committed;
    and the SERIALIZED status the generator would write into pack bytes, which
    must not transition, because the receipt's ``pack_identity`` pins the plan
    bytes that carry it.
    """

    completed = subprocess.run(
        [sys.executable, "-c", _FREEZE_STATE_PROBE, str(generator)],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=NO_BYTECODE_ENV,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return json.loads(completed.stdout)


def authenticate_freeze_reference(output_root: Path, pack_rel: Path) -> dict[str, Any]:
    """Run the production ``_load_freeze_reference`` gate check on a frozen pack.

    The D-134 profile map and boot-session id are unavailable for fixture packs,
    so the same modeled runtime the freeze itself used is reinstalled for the
    duration of the check and removed again, leaving the checkout clean.
    """

    install_v2_freeze_fixture_runtime(output_root)
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                _FREEZE_AUTHENTICATION_PROBE,
                str(output_root / pack_rel),
            ],
            cwd=output_root,
            check=False,
            capture_output=True,
            text=True,
            env=NO_BYTECODE_ENV,
        )
    finally:
        remove_v2_freeze_fixture_runtime(output_root)
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    return json.loads(completed.stdout)


def serialized_status_sites(pack_root: Path) -> dict[Path, str]:
    """Map every JSON artifact carrying a top-level ``draft_status`` to its value."""

    sites: dict[Path, str] = {}
    for path in sorted(pack_root.rglob("*")):
        if not path.is_file() or path.suffix != ".json":
            continue
        if "__pycache__" in path.parts:
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("draft_status"), str):
            sites[path.relative_to(pack_root)] = value["draft_status"]
    return sites


def probe_generator_status(generator: Path, cwd: Path) -> str:
    code = (
        "import importlib.util, pathlib, sys; "
        "path = pathlib.Path(sys.argv[1]); "
        "spec = importlib.util.spec_from_file_location('status_probe', path); "
        "module = importlib.util.module_from_spec(spec); "
        "spec.loader.exec_module(module); "
        "print(module.GenerationIdentity(preserve_current_frozen_bytes=True).target_status)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code, str(generator)],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=NO_BYTECODE_ENV,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


class D117GammaPlanTest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.plan = read_json(PACK / "calibration_plan.json")
        self.root_manifest = read_json(PACK / "order_manifest.json")
        self.tree = read_json(PACK / "plan_tree.json")
        self.analysis = read_json(PACK / "analysis_manifest_v3.json")

    def test_exact_inventory_and_exact_primary_hashes(self) -> None:
        expected = set(GENERATOR_MODULE.expected_pack_paths())
        expected |= governed_frozen_attachment_paths(PACK)
        self.assertEqual(len(expected), 135)
        self.assertEqual(actual_inventory(PACK), expected)
        for filename, expected_sha in EXACT_SHAS.items():
            self.assertEqual(sha256(PACK / filename), expected_sha, filename)

        for filename in ("calibration_plan", "plan_tree"):
            payload = PACK / f"{filename}.json"
            expected_sidecar = f"{sha256(payload)}  {payload.name}\n"
            self.assertEqual(
                (PACK / f"{filename}.sha256").read_text(encoding="utf-8"),
                expected_sidecar,
            )

    def test_double_regeneration_and_check_are_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-gamma-test-a-") as first:
            with tempfile.TemporaryDirectory(prefix="d117-gamma-test-b-") as second:
                outputs = []
                for output_root in (first, second):
                    completed = subprocess.run(
                        [
                            sys.executable,
                            str(GENERATOR),
                            "--output-root",
                            output_root,
                            "--preserve-current-frozen-bytes",
                        ],
                        cwd=ROOT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    outputs.append(Path(output_root) / GENERATOR_MODULE.PACK_REL)
                self.assertEqual(actual_inventory(outputs[0]), actual_inventory(outputs[1]))
                generated_paths = set(GENERATOR_MODULE.expected_pack_paths())
                self.assertEqual(actual_inventory(outputs[0]), generated_paths)
                for relative in generated_paths:
                    self.assertEqual(
                        (outputs[0] / relative).read_bytes(),
                        (outputs[1] / relative).read_bytes(),
                        relative.as_posix(),
                    )
                    self.assertEqual(
                        (outputs[0] / relative).read_bytes(),
                        (PACK / relative).read_bytes(),
                        relative.as_posix(),
                    )

        checked = subprocess.run(
            [
                sys.executable,
                str(GENERATOR),
                "--check",
                "--preserve-current-frozen-bytes",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("checked D-117 gamma unfrozen draft", checked.stdout)

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
            pack_id="d117_contrast_qwen25_1p5b_vs_7b_v2",
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
            frozen_state_readme = GENERATOR_MODULE.readme_bytes()
        self.assertEqual(frozen_state_readme, (PACK / "README.md").read_bytes())
        with GENERATOR_MODULE.generation_context(future_identity):
            successor_readme = GENERATOR_MODULE.readme_bytes().decode("utf-8")
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
            pack_id="d117_contrast_qwen25_1p5b_vs_7b_v2",
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
            source.count('"draft_status": emitted_draft_status()'), 8
        )
        self.assertNotIn("pack status {PACK_STATUS}", source)
        expected = {
            successor.pack_rel / path
            for path in GENERATOR_MODULE.expected_pack_paths()
        }
        self.assertEqual(
            GENERATOR_MODULE.validate_generation_output_inventory(successor), expected
        )
        for pack_id, suffix, preserve in (
            ("d117_contrast_qwen25_1p5b_vs_7b_v0", "_v0", False),
            ("d117_contrast_qwen25_1p5b_vs_7b_v2", "_v2", True),
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
                    cwd=ROOT, check=False, capture_output=True, text=True,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertEqual(checkout_inventory(output_root), set())

    def test_generation_refuses_symlinked_write_inventory_before_any_write(self) -> None:
        successor = GENERATOR_MODULE.GenerationIdentity(
            pack_id="d117_contrast_qwen25_1p5b_vs_7b_v2",
            family_suffix="_v2",
            preserve_current_frozen_bytes=False,
        )
        cases = {
            "pack_directory": (successor.pack_rel, True),
            "pack_file": (successor.pack_rel / "README.md", False),
            "sidecar": (
                successor.pack_rel / "calibration_plan.sha256",
                False,
            ),
        }
        for name, (relative, is_directory) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(
                prefix="d117-gamma-symlink-root-"
            ) as temp, tempfile.TemporaryDirectory(
                prefix="d117-gamma-symlink-escape-"
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
                    cwd=ROOT,
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
        successor_id = "d117_contrast_qwen25_1p5b_vs_7b_v2"
        successor_rel = GENERATOR_MODULE.PACK_REL.with_name(successor_id)
        with tempfile.TemporaryDirectory(prefix="d117-gamma-v2-") as temp:
            output_root = Path(temp)
            tracked = initialize_git_tracked_checkout(
                output_root,
                (GENERATOR_MODULE.PACK_REL, *V1_SPEC_RELS),
            )
            self.assertTrue(set(V1_SPEC_RELS) <= tracked)
            baseline_inventory = checkout_inventory(output_root)
            v1_spec_hashes = {
                relative: sha256(output_root / relative)
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
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(preserved.returncode, 0, preserved.stderr)
            self.assertEqual(git_status(output_root), "")
            self.assertEqual(checkout_inventory(output_root), baseline_inventory)
            self.assertEqual(
                {
                    relative: sha256(output_root / relative)
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
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            expected_writes = {
                successor_rel / relative
                for relative in GENERATOR_MODULE.expected_pack_paths()
            }
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
                    relative: sha256(output_root / relative)
                    for relative in V1_SPEC_RELS
                },
                v1_spec_hashes,
            )
            checked = subprocess.run(
                [*command, "--check"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)

            pack_root = output_root / successor_rel
            tree = read_json(pack_root / "plan_tree.json")
            self.assertEqual(tree["plan"]["path"], "calibration_plan.json")
            self.assertEqual(
                tree["plan"]["plan_id"],
                GENERATOR_MODULE.PLAN_ID.removesuffix("v1") + "v2",
            )
            self.assertEqual(
                tree["window_identity"]["evidence_root_id"],
                GENERATOR_MODULE.EVIDENCE_ROOT_ID.removesuffix("v1") + "v2",
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
                config = read_json(pack_root / row["config_path"])
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

            commit_fixture(output_root, "track emitted gamma v2")
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
            preserved_tree = read_json(pack_root / "plan_tree.json")
            for row in preserved_tree["science"]:
                config = read_json(pack_root / row["config_path"])
                self.assertIn("launch_lineage_required", config["run_metadata"]["tags"])

        for row in self.tree["science"]:
            current = read_json(PACK / row["config_path"])
            self.assertNotIn(
                "launch_lineage_required", current["run_metadata"]["tags"]
            )

    def test_dual_generation_transaction_and_generational_induction(self) -> None:
        from tests import test_d117_floor_qwen25_1p5b_plan as alpha_tests
        from tests import test_d117_floor_qwen25_7b_plan as beta_tests

        v1_packs = (
            GENERATOR_MODULE.PACK_REL,
            alpha_tests.PACK_REL,
            beta_tests.PACK.relative_to(ROOT),
        )
        all_v1_roots = (*v1_packs, *V1_SPEC_RELS)
        generators = (
            (GENERATOR, GENERATOR_MODULE, GENERATOR_MODULE.PACK_REL),
            (alpha_tests.GENERATOR, alpha_tests.GENERATOR_MODULE, alpha_tests.PACK_REL),
            (
                beta_tests.GENERATOR,
                beta_tests.GENERATOR_MODULE,
                beta_tests.PACK.relative_to(ROOT),
            ),
        )
        with tempfile.TemporaryDirectory(prefix="d117-dual-generation-") as temp:
            output_root = Path(temp)
            initialize_git_tracked_checkout(output_root, all_v1_roots)
            link_successor_self_check_inputs(output_root)
            alpha_tests.link_successor_self_check_inputs(output_root)
            compatibility_link = (
                output_root
                / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2"
            )
            self.assertTrue(compatibility_link.is_symlink())
            compatibility_link.unlink()
            baseline_inventory = checkout_inventory(output_root)
            v1_hashes = hash_inventory(output_root, all_v1_roots)

            v2_packs: list[Path] = []
            v2_specs: list[Path] = []
            for index, (generator, module, pack_rel) in enumerate(generators):
                v2_rel = pack_rel.with_name(pack_rel.name.removesuffix("_v1") + "_v2")
                generated = subprocess.run(
                    [
                        sys.executable,
                        str(generator),
                        "--output-root",
                        str(output_root),
                        "--pack-id",
                        v2_rel.name,
                        "--family-suffix",
                        "_v2",
                        "--no-preserve-current-frozen-bytes",
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stderr)
                v2_packs.append(v2_rel)
                if index == 0:
                    gamma_hashes = hash_inventory(output_root, (v2_rel,))
                    beta_tests.link_successor_self_check_inputs(output_root)
                    alpha_tests.link_successor_self_check_inputs(output_root)
                    self.assertEqual(hash_inventory(output_root, (v2_rel,)), gamma_hashes)
                else:
                    v2_specs.append(module.extraction_spec_rel(
                        module.GenerationIdentity(
                            pack_id=v2_rel.name,
                            family_suffix="_v2",
                            preserve_current_frozen_bytes=False,
                        )
                    ))

            expected_v2: set[Path] = set()
            for (_, module, _), pack_rel in zip(generators, v2_packs):
                expected_paths = (
                    module.expected_pack_paths()
                    if hasattr(module, "expected_pack_paths")
                    else module.expected_pack_files()
                )
                expected_v2.update(pack_rel / path for path in expected_paths)
            expected_v2.update(v2_specs)
            self.assertEqual(len(expected_v2), 334)
            self.assertEqual(checkout_inventory(output_root) - baseline_inventory, expected_v2)
            self.assertEqual(hash_inventory(output_root, all_v1_roots), v1_hashes)
            self.assertEqual(
                subprocess.run(["git", "diff", "--quiet"], cwd=output_root).returncode,
                0,
            )

            commit_fixture(output_root, "track exact 334-file v2 transaction")
            v1_v2_roots = (*all_v1_roots, *v2_packs, *v2_specs)
            v1_v2_hashes = hash_inventory(output_root, v1_v2_roots)
            baseline_v3 = checkout_inventory(output_root)
            v3_packs: list[Path] = []
            v3_specs: list[Path] = []
            for index, ((_, module, _), v2_rel) in enumerate(zip(generators, v2_packs)):
                v3_rel = v2_rel.with_name(v2_rel.name.removesuffix("_v2") + "_v3")
                emitted = output_root / v2_rel / "generate_configs.py"
                generated = subprocess.run(
                    [
                        sys.executable,
                        str(emitted),
                        "--output-root",
                        str(output_root),
                        "--pack-id",
                        v3_rel.name,
                        "--family-suffix",
                        "_v3",
                        "--no-preserve-current-frozen-bytes",
                    ],
                    cwd=output_root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stderr)
                v3_packs.append(v3_rel)
                if index:
                    v3_specs.append(
                        Path("configs/floor_mint")
                        / f"{module.SPEC_REL.stem.removesuffix('_extraction_spec')}_v3_extraction_spec.json"
                    )
            expected_v3: set[Path] = set()
            for (_, module, _), pack_rel in zip(generators, v3_packs):
                expected_paths = (
                    module.expected_pack_paths()
                    if hasattr(module, "expected_pack_paths")
                    else module.expected_pack_files()
                )
                expected_v3.update(pack_rel / path for path in expected_paths)
            expected_v3.update(v3_specs)
            self.assertEqual(len(expected_v3), 334)
            self.assertEqual(checkout_inventory(output_root) - baseline_v3, expected_v3)
            self.assertEqual(hash_inventory(output_root, v1_v2_roots), v1_v2_hashes)

            commit_fixture(output_root, "track emitted v3 families")
            for v3_rel in v3_packs:
                emitted = output_root / v3_rel / "generate_configs.py"
                preserve = [
                    sys.executable,
                    str(emitted),
                    "--output-root",
                    str(output_root),
                    "--preserve-current-frozen-bytes",
                ]
                checked = subprocess.run(
                    [*preserve, "--check"], cwd=output_root,
                    check=False, capture_output=True, text=True,
                )
                self.assertEqual(checked.returncode, 0, checked.stderr)
                regenerated = subprocess.run(
                    preserve, cwd=output_root,
                    check=False, capture_output=True, text=True,
                )
                self.assertEqual(regenerated.returncode, 0, regenerated.stderr)
                self.assertEqual(git_status(output_root), "")

    def test_authenticated_freeze_transition_preserves_frozen_bytes(self) -> None:
        from tests import test_d117_floor_qwen25_1p5b_plan as alpha_tests
        from tests import test_d117_floor_qwen25_7b_plan as beta_tests

        generators = (
            (GENERATOR, GENERATOR_MODULE, GENERATOR_MODULE.PACK_REL, 8),
            (alpha_tests.GENERATOR, alpha_tests.GENERATOR_MODULE, alpha_tests.PACK_REL, 6),
            (
                beta_tests.GENERATOR,
                beta_tests.GENERATOR_MODULE,
                beta_tests.PACK.relative_to(ROOT),
                6,
            ),
        )
        v1_roots = tuple(item[2] for item in generators)
        with tempfile.TemporaryDirectory(prefix="d117-authenticated-freeze-") as temp:
            output_root = Path(temp)
            initialize_git_tracked_checkout(
                output_root,
                (*v1_roots, *V1_SPEC_RELS, ROW_REGISTRY_REL),
            )
            link_successor_self_check_inputs(output_root)
            alpha_tests.link_successor_self_check_inputs(output_root)
            compatibility_link = (
                output_root
                / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2"
            )
            self.assertTrue(compatibility_link.is_symlink())
            compatibility_link.unlink()

            v2_packs: list[Path] = []
            preserve_commands: list[list[str]] = []
            draft_hashes: list[dict[Path, str]] = []
            draft_status_sites: list[dict[Path, str]] = []
            draft_freeze_states: list[dict[str, str]] = []
            for generator, _module, v1_rel, _status_site_count in generators:
                v2_rel = v1_rel.with_name(v1_rel.name.removesuffix("_v1") + "_v2")
                generated = subprocess.run(
                    [
                        sys.executable,
                        str(generator),
                        "--output-root",
                        str(output_root),
                        "--pack-id",
                        v2_rel.name,
                        "--family-suffix",
                        "_v2",
                        "--no-preserve-current-frozen-bytes",
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(generated.returncode, 0, generated.stderr)
                v2_packs.append(v2_rel)
                preserve = [
                    sys.executable,
                    str(output_root / v2_rel / "generate_configs.py"),
                    "--output-root",
                    str(output_root),
                    "--preserve-current-frozen-bytes",
                ]
                self.assertEqual(
                    probe_generator_status(output_root / v2_rel / "generate_configs.py", output_root),
                    "unfrozen_draft",
                )
                before = hash_inventory(output_root, (v2_rel,))
                preserved_draft = subprocess.run(
                    preserve,
                    cwd=output_root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    preserved_draft.returncode, 0, preserved_draft.stderr
                )
                self.assertEqual(
                    probe_generator_status(output_root / v2_rel / "generate_configs.py", output_root),
                    "unfrozen_draft",
                )
                self.assertEqual(hash_inventory(output_root, (v2_rel,)), before)
                preserve_commands.append(preserve)
                # Option (d) shape (cold-gate verdict 2026-08-18, holding 6):
                # what a successor pack serializes before freeze must already be
                # freeze-neutral, because these are the bytes the receipt pins
                # and they never transition. Capture them so the post-freeze leg
                # can compare against the exact pre-freeze committed bytes.
                pre_freeze_state = probe_generator_freeze_state(
                    output_root / v2_rel / "generate_configs.py", output_root
                )
                self.assertEqual(pre_freeze_state["target_status"], "unfrozen_draft")
                self.assertEqual(
                    pre_freeze_state["emitted_draft_status"],
                    "as_generated_pre_d134_freeze",
                )
                sites = serialized_status_sites(output_root / v2_rel)
                self.assertTrue(sites)
                self.assertEqual(
                    sorted(set(sites.values())), ["as_generated_pre_d134_freeze"]
                )
                readme_text = (output_root / v2_rel / "README.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(
                    "The committed D-134 freeze receipt and its plan-tree "
                    "attachment are authoritative",
                    " ".join(readme_text.split()),
                )
                for denial in ("unfrozen draft", "unfrozen_draft", "not armable"):
                    self.assertNotIn(denial, readme_text)
                draft_hashes.append(hash_inventory(output_root, (v2_rel,)))
                draft_status_sites.append(sites)
                draft_freeze_states.append(pre_freeze_state)

            commit_fixture(output_root, "track emitted draft v2 families")
            unmodeled = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/generate_arm_readiness.py"),
                    "freeze",
                    "--pack-root",
                    str(output_root / v2_packs[0]),
                ],
                cwd=output_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(unmodeled.returncode, 2, unmodeled.stderr)
            self.assertEqual(
                json.loads(unmodeled.stdout)["reason_codes"],
                ["readiness_row_registry_mismatch"],
            )
            freeze_script = install_v2_freeze_fixture_runtime(output_root)
            freeze_results: list[dict[str, Any]] = []
            try:
                for v2_rel in v2_packs:
                    frozen = subprocess.run(
                        [
                            sys.executable,
                            str(freeze_script),
                            "freeze",
                            "--pack-root",
                            str(output_root / v2_rel),
                        ],
                        cwd=output_root,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    result = json.loads(frozen.stdout)
                    self.assertEqual(
                        frozen.returncode, 1, frozen.stdout + frozen.stderr
                    )
                    self.assertEqual(result["status"], "REFUSE")
                    self.assertTrue(result["mutated"])
                    self.assertTrue(result["reason_codes"])
                    freeze_results.append(result)
            finally:
                remove_v2_freeze_fixture_runtime(output_root)

            commit_fixture(output_root, "track genuine v2 freeze receipts")
            for (
                (_generator, _module, _v1_rel, status_site_count),
                v2_rel,
                preserve,
                freeze_result,
                draft_inventory,
                draft_sites,
                draft_state,
            ) in zip(
                generators,
                v2_packs,
                preserve_commands,
                freeze_results,
                draft_hashes,
                draft_status_sites,
                draft_freeze_states,
                strict=True,
            ):
                pack_root = output_root / v2_rel
                tree = read_json(pack_root / "plan_tree.json")
                attachment = tree["arm_attachments"]["arm_readiness"][
                    "freeze_receipt"
                ]
                self.assertIsNotNone(attachment)
                self.assertEqual(attachment["sha256"], freeze_result["receipt_sha256"])
                receipt_path = pack_root / attachment["path"]
                self.assertEqual(sha256(receipt_path), attachment["sha256"])
                source = (pack_root / "generate_configs.py").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(
                    source.count('"draft_status": emitted_draft_status()'),
                    status_site_count,
                )
                frozen_bytes = hash_inventory(output_root, (v2_rel,))
                checked = subprocess.run(
                    [*preserve, "--check"],
                    cwd=output_root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(checked.returncode, 0, checked.stderr)
                self.assertEqual(
                    probe_generator_status(pack_root / "generate_configs.py", output_root),
                    "frozen_by_d134_receipt",
                )
                regenerated = subprocess.run(
                    preserve,
                    cwd=output_root,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(regenerated.returncode, 0, regenerated.stderr)
                self.assertEqual(
                    probe_generator_status(pack_root / "generate_configs.py", output_root),
                    "frozen_by_d134_receipt",
                )
                self.assertEqual(hash_inventory(output_root, (v2_rel,)), frozen_bytes)

                # ---- C1, the INVERTED freeze regression -------------------
                # Cold-gate verdict 2026-08-18, condition C1. Before this
                # round the regression only checked that DYNAMIC status
                # reports frozen; it never pinned what the frozen pack's bytes
                # say. Under option (a) the committed receipt IS the
                # transition, so the correct assertion is the opposite of the
                # superseded consult R-7: nothing serialized may move.
                #
                # (i) dynamic status reports frozen (asserted above via
                #     probe_generator_status, and again in the richer probe).
                frozen_state = probe_generator_freeze_state(
                    pack_root / "generate_configs.py", output_root
                )
                self.assertEqual(frozen_state["target_status"], "frozen_by_d134_receipt")

                # (ii) every serialized status site and the README are
                #      byte-identical to the pre-freeze committed bytes -- the
                #      option-(d)-shaped bytes -- and the generator would still
                #      emit exactly those, not a frozen transition.
                self.assertEqual(
                    frozen_state["emitted_draft_status"],
                    draft_state["emitted_draft_status"],
                )
                self.assertEqual(
                    frozen_state["emitted_draft_status"],
                    "as_generated_pre_d134_freeze",
                )
                self.assertEqual(
                    frozen_state["readme_sha256"], draft_state["readme_sha256"]
                )
                self.assertEqual(serialized_status_sites(pack_root), draft_sites)
                post_freeze_inventory = hash_inventory(output_root, (v2_rel,))
                # The freeze transaction is allowed to rewrite exactly one
                # pre-existing artifact -- the plan-tree carrier that records
                # the receipt attachment, plus its sidecar -- and that rewrite
                # happens AFTER pack_identity is computed, so it is outside the
                # pin. Nothing else may move, and the pinned plan and the
                # advisor-visible README must be byte-identical.
                moved = {
                    relative
                    for relative, digest in draft_inventory.items()
                    if post_freeze_inventory.get(relative) != digest
                }
                self.assertEqual(
                    moved,
                    {v2_rel / "plan_tree.json", v2_rel / "plan_tree.sha256"},
                )
                for name in (
                    "README.md",
                    "calibration_plan.json",
                    "calibration_plan.sha256",
                    "generate_configs.py",
                ):
                    with self.subTest(pack=v2_rel.name, path=name):
                        self.assertEqual(
                            post_freeze_inventory[v2_rel / name],
                            draft_inventory[v2_rel / name],
                        )

                # (iii) the receipt still authenticates against the committed
                #       pack bytes: its pack_identity -- the plan SHA the pin
                #       is built on -- still matches, so the unconditional
                #       identity check at the dry-run/arm/verify gates does NOT
                #       refuse with readiness_freeze_receipt_mismatch. The
                #       fixture receipts are genuine REFUSE receipts (the
                #       unavailable desk evidence is modeled, not the verdict),
                #       so the residual gate refusal is the pre-existing
                #       readiness_dependency_refused. This asserts receipt
                #       IDENTITY preservation, never PASS/GO armability.
                authentication = authenticate_freeze_reference(output_root, v2_rel)
                self.assertTrue(authentication["receipt_resolved"])
                self.assertTrue(authentication["identity_matches_committed_bytes"])
                self.assertEqual(
                    authentication["receipt_sha256"], freeze_result["receipt_sha256"]
                )
                self.assertEqual(authentication["status"], "REFUSE")
                self.assertNotEqual(
                    authentication["gate_reason_code"],
                    "readiness_freeze_receipt_mismatch",
                )
                self.assertEqual(
                    authentication["gate_reason_code"], "readiness_dependency_refused"
                )
                self.assertEqual(
                    authentication["plan_sha256"],
                    sha256(pack_root / "calibration_plan.json"),
                )

                # (iv) preserve regeneration remains byte-stable and the
                #      checkout is clean (asserted below).
                self.assertEqual(hash_inventory(output_root, (v2_rel,)), frozen_bytes)
                self.assertEqual(git_status(output_root), "")

    def test_generator_check_rejects_extra_pack_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-gamma-inventory-") as temp:
            check_root = Path(temp)
            shutil.copytree(PACK, check_root / GENERATOR_MODULE.PACK_REL)
            (check_root / GENERATOR_MODULE.PACK_REL / "stray-review-probe.txt").write_text(
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

    def test_both_arms_have_ten_complete_abba_blocks(self) -> None:
        entries = self.root_manifest["executed_order"]
        self.assertEqual(self.root_manifest["planned_n_bundles"], 80)
        self.assertEqual([entry["index"] for entry in entries], list(range(1, 81)))
        self.assertEqual(len({entry["run_id"] for entry in entries}), 80)

        cells = {
            cell["measurement_arm"]: cell for cell in self.plan["floor_cells"]
        }
        self.assertEqual(set(cells), {"decode", "prefill_p256"})
        self.assertEqual(cells["decode"]["metric"], "phase_energy_j.decode")
        self.assertEqual(cells["prefill_p256"]["metric"], "phase_energy_j.prefill")

        for measurement_arm in ("decode", "prefill_p256"):
            arm_entries = [
                entry for entry in entries if entry["measurement_arm"] == measurement_arm
            ]
            self.assertEqual(len(arm_entries), 40)
            self.assertEqual(
                sorted({entry["block_index"] for entry in arm_entries}),
                list(range(1, 11)),
            )
            for block_number in range(1, 11):
                block = [
                    entry
                    for entry in arm_entries
                    if entry["block_index"] == block_number
                ]
                self.assertEqual([entry["position"] for entry in block], POSITIONS)
                self.assertEqual([entry["arm"] for entry in block], LABELS)
                self.assertEqual(
                    [entry["position_in_block"] for entry in block], [1, 2, 3, 4]
                )

        stage_blocks = []
        for subcampaign in self.root_manifest["subcampaign_order"]:
            manifest = read_json(PACK / subcampaign["manifest_path"])
            stage_blocks.append(
                sorted({entry["block_index"] for entry in manifest["executed_order"]})
            )
        self.assertEqual(
            stage_blocks,
            [list(range(1, 6)), list(range(6, 11)), list(range(1, 6)), list(range(6, 11))],
        )
        for subcampaign in self.root_manifest["subcampaign_order"]:
            stage_manifest = read_json(PACK / subcampaign["manifest_path"])
            self.assertEqual(
                stage_manifest["successor_stage_id"],
                subcampaign["successor_stage_id"],
            )
        self.assertEqual(
            [
                (row["after_science_member"], row["stage_id"])
                for row in self.root_manifest["interior_reference_stages"]
            ],
            [
                (20, "gamma-reference-decode-midpoint"),
                (40, "gamma-reference-arm-boundary"),
                (60, "gamma-reference-prefill-midpoint"),
            ],
        )
        cadence = self.root_manifest["reference_cadence"]
        self.assertEqual(cadence, self.tree["reference_cadence"])
        self.assertEqual(
            cadence["authority"],
            "docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md "
            "§6 U7 gamma implementation session",
        )
        self.assertEqual(
            cadence["two_arm_interpretation"], "arm_midpoints_plus_arm_boundary"
        )
        self.assertEqual(
            cadence["freeze_ratification"], "PENDING-LEAD-RATIFICATION"
        )

    def test_calibration_plan_shape_and_member_encoding_match_floor_packs(self) -> None:
        siblings = [
            read_json(
                ROOT
                / "configs/campaigns/d117_floor_qwen25_1p5b_v1/calibration_plan.json"
            ),
            read_json(
                ROOT
                / "configs/campaigns/d117_floor_qwen25_7b_v1/calibration_plan.json"
            ),
        ]
        for sibling in siblings:
            self.assertEqual(sibling["schema_version"], self.plan["schema_version"])
            self.assertEqual(set(sibling), set(self.plan))
        for cell in self.plan["floor_cells"]:
            for block in cell["ordered_blocks"]:
                self.assertEqual(
                    [member["position"] for member in block["members"]],
                    POSITIONS,
                )
                self.assertTrue(
                    all(
                        set(member)
                        == {"position", "plan_label", "plan_sequence_index", "bundle_id"}
                        for member in block["members"]
                    )
                )

    def test_all_configs_and_embedded_hashes_recompute(self) -> None:
        entries = self.root_manifest["executed_order"]
        plan_sha = sha256(PACK / "calibration_plan.json")
        for entry in entries:
            config_path = PACK / entry["config"]
            self.assertEqual(sha256(config_path), entry["config_sha256"])
            config_data = read_json(config_path)
            parsed = BenchmarkConfig.from_mapping(config_data)
            self.assertEqual(parsed.run_id, entry["run_id"])
            self.assertNotIn("unfrozen_draft", parsed.run_metadata.tags)
            self.assertIn(
                "pack status unfrozen_draft.",
                config_data["hardware_target"]["notes"],
            )
            self.assertIn(
                f"calibration-plan-sha256={plan_sha}", parsed.run_metadata.tags
            )

        for subcampaign in self.root_manifest["subcampaign_order"]:
            manifest_path = PACK / subcampaign["manifest_path"]
            self.assertEqual(sha256(manifest_path), subcampaign["manifest_sha256"])
            local_entries, warning = load_order_entries(manifest_path.parent)
            self.assertIsNone(warning)
            self.assertEqual(len(local_entries), 20)

        self.assertEqual(self.tree["plan"]["actual_sha256"], plan_sha)
        self.assertEqual(self.tree["generator"]["sha256"], FROZEN_GENERATOR_SHA256)
        self.assertEqual(
            self.tree["campaign_policy"]["sha256"],
            sha256(ROOT / self.tree["campaign_policy"]["path"]),
        )
        self.assertEqual(
            self.tree["downstream_contract"]["analysis_manifest_sha256"],
            sha256(PACK / "analysis_manifest_v3.json"),
        )
        for family in self.tree["condition_families"]:
            self.assertEqual(sha256(PACK / family["path"]), family["sha256"])
        for external in self.tree["external_inputs"]:
            if "manifest_path" in external:
                self.assertEqual(
                    sha256(ROOT / external["manifest_path"]),
                    external["manifest_sha256"],
                )
                for member in external["members"]:
                    self.assertEqual(sha256(ROOT / member["path"]), member["sha256"])
            else:
                self.assertEqual(sha256(ROOT / external["path"]), external["sha256"])

    def test_prefill_prompt_candidate_is_shared_by_all_prefill_members(self) -> None:
        prompt = read_json(PACK / "prefill_prompt_candidate.json")
        self.assertEqual(prompt["draft_status"], "unfrozen_draft")
        self.assertEqual(
            prompt["candidate_status"], "PROPOSED-PENDING-LEAD-RATIFICATION"
        )
        self.assertEqual(prompt["planned_token_count"], 256)
        text = prompt["prompt_text"]
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), prompt["prompt_text_utf8_sha256"])
        self.assertEqual(text.count("The plan remains easy to audit."), 35)
        self.assertTrue(text.endswith("The plan remains easy to audit and simple to review."))

        prefill_entries = [
            entry
            for entry in self.root_manifest["executed_order"]
            if entry["measurement_arm"] == "prefill_p256"
        ]
        for entry in prefill_entries:
            workload = read_json(PACK / entry["config"])["workload_profile"]
            self.assertNotIn("prompt_tokens", workload)
            self.assertEqual(workload["output_tokens"], 512)
            self.assertEqual(workload["prompt_text"], text)

    def test_d124_estimator_is_registered_for_both_shared_edge_contrasts(self) -> None:
        self.assertEqual(
            self.tree["acceptance_policy"]["selection"],
            "issued_d116_artifact_only",
        )
        canonical = two_shared_edge_common_mode_registration()
        for cell in self.plan["floor_cells"]:
            self.assertEqual(cell["floor_estimator_registration"], canonical)
            self.assertEqual(
                cell["floor_estimator_registration"]["parameter_sha256"],
                "dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38",
            )
        for contrast in self.analysis["contrasts"]:
            self.assertEqual(
                contrast["floor_estimator_registration"], canonical
            )
        self.assertIn("D-124", self.plan["authorities"])

    def test_consumer_family_is_a_declaration_not_a_pinset(self) -> None:
        declaration = read_json(PACK / "consumer_family_declaration.json")
        self.assertEqual(declaration["draft_status"], "unfrozen_draft")
        self.assertEqual(declaration["binding_mode"], "declaration_only")
        self.assertIs(declaration["byte_binding_pinset"], False)
        self.assertEqual(
            declaration["decode_floor_cells"],
            {
                "condition_a": "d117-qwen25-1p5b-decode-floor-v1",
                "condition_b": "d117-qwen25-7b-decode-floor-v1",
                "derivation": "deterministic plan-factory floor artifact vocabulary",
                "floor_rule": "cross_stack_armwise_max.v1",
            },
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["cell_ids"]["status"],
            "EMPTY",
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["cell_ids"]["value"],
            [],
        )
        self.assertIn(
            "TODO",
            declaration["prefill_p256_floor_dependency"]["cell_ids"]["todo"],
        )
        self.assertEqual(
            declaration["prefill_p256_floor_dependency"]["transport_rule"]["status"],
            "EMPTY",
        )
        all_keys: set[str] = set()

        def collect_keys(value: Any) -> None:
            if isinstance(value, dict):
                all_keys.update(value)
                for child in value.values():
                    collect_keys(child)
            elif isinstance(value, list):
                for child in value:
                    collect_keys(child)

        collect_keys(declaration)
        self.assertFalse(any(key.endswith("_sha256") for key in all_keys))

    def test_stage_launch_recipes_and_runtime_budgets_cover_both_arms(self) -> None:
        stages = self.tree["stage_graph"]
        self.assertEqual([stage["ordinal"] for stage in stages], list(range(1, 17)))
        self.assertEqual(
            sum(len(stage["launch"]["commands"]) for stage in stages), 17
        )
        for index, stage in enumerate(stages):
            self.assertEqual(stage["launch"]["schema_version"], "joulewise.stage_launch.v1")
            self.assertEqual(
                set(stage["launch"]), {"schema_version", "commands"}
            )
            self.assertEqual(stage["predecessor"], stages[index - 1]["stage_id"] if index else None)
            self.assertEqual(
                stage["successor"],
                stages[index + 1]["stage_id"] if index + 1 < len(stages) else None,
            )
            for command in stage["launch"]["commands"]:
                self.assertEqual(
                    set(command),
                    {"command_id", "command_kind", "argv_template", "cwd", "success_exit_codes"},
                )
                self.assertIn(
                    command["argv_template"]["tool_id"],
                    {"bracket_reserver", "fiducial_capture", "campaign_runner", "backup_runs"},
                )
                for argument in command["argv_template"]["arguments"]:
                    self.assertIn(
                        argument["kind"],
                        {"literal", "repo_path", "binding", "binding_path", "tree_pointer"},
                    )

        budget = self.tree["runtime_budget"]
        self.assertEqual(budget["decode"]["members"], 40)
        self.assertEqual(budget["decode"]["minutes_with_margin"], 168.0)
        self.assertEqual(budget["prefill_p256"]["members"], 40)
        self.assertEqual(budget["prefill_p256"]["core_minutes_before_margin"], 110.0)
        self.assertEqual(budget["prefill_p256"]["minutes_with_20_percent_margin"], 130.0)
        self.assertEqual(budget["combined_minutes_with_margin"], 310.0)
        self.assertEqual(
            budget["interior_reference_augmentation"]["additional_references"], 2
        )
        self.assertEqual(
            budget["interior_reference_augmentation"]["core_minutes_before_margin"],
            10.0,
        )
        self.assertEqual(
            budget["interior_reference_augmentation"]["minutes_with_20_percent_margin"],
            12.0,
        )
        self.assertEqual(budget["combined_derivation"], "168.0 + 130.0 + 12.0")
        self.assertEqual(
            budget["interior_reference_augmentation"]["authority"],
            self.tree["reference_cadence"]["authority"],
        )

        stage_ids = [stage["stage_id"] for stage in stages]
        expected_interior = [
            "gamma-reference-decode-midpoint",
            "gamma-reference-arm-boundary",
            "gamma-reference-prefill-midpoint",
        ]
        self.assertEqual(
            [stage_id for stage_id in stage_ids if stage_id in expected_interior],
            expected_interior,
        )

    def test_unfrozen_language_and_generator_has_no_discovery(self) -> None:
        self.assertEqual(self.plan["draft_status"], "unfrozen_draft")
        self.assertEqual(self.tree["draft_status"], "unfrozen_draft")
        self.assertEqual(self.analysis["draft_status"], "unfrozen_draft")
        self.assertEqual(self.tree["schema_version"], "joulewise.d117_plan_tree.v1")
        for manifest_path in [PACK / "order_manifest.json", *sorted(PACK.glob("*/order_manifest.json"))]:
            self.assertEqual(read_json(manifest_path)["draft_status"], "unfrozen_draft")
        authored = "\n".join(
            (PACK / name).read_text(encoding="utf-8")
            for name in (
                "README.md",
                "calibration_plan.json",
                "plan_tree.json",
                "analysis_manifest_v3.json",
            )
        )
        self.assertNotIn("frozen_before_measurement", authored)
        self.assertNotIn("artifact_status", authored)
        self.assertNotIn("freeze_status", authored)
        generator_source = GENERATOR.read_text(encoding="utf-8")
        for forbidden in (".glob(", "os.walk", "Path.walk"):
            self.assertNotIn(forbidden, generator_source)
        self.assertIn('.rglob("*")', generator_source)

    def test_identity_projection_has_four_canonical_units(self) -> None:
        projection = self.tree["arm_attachments"]["identity_pin_projection"]
        self.assertEqual(projection["state"], "frozen")
        self.assertEqual(projection["work_order"], "D117-U11-IDPIN-PROJECTION")
        self.assertEqual(projection["mode"], "derive_never_operator_enter")
        self.assertEqual(projection["derivation_contract"], IDENTITY_PIN_DERIVATION_CONTRACT)
        projection_receipt = projection["projection_receipt"]
        self.assertIsNotNone(projection_receipt)
        receipt_path = PACK / projection_receipt["path"]
        self.assertEqual(sha256(receipt_path), projection_receipt["sha256"])
        self.assertEqual(
            receipt_path.with_suffix(".sha256").read_text(encoding="utf-8"),
            f"{projection_receipt['sha256']}  {receipt_path.name}\n",
        )
        units = projection["identity_units"]
        self.assertEqual(
            [unit["identity_unit_id"] for unit in units],
            ["A/decode", "A/prefill_p256", "B/decode", "B/prefill_p256"],
        )
        producer_by_arm = {
            "A": "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1",
            "B": "plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1",
        }
        for unit in units:
            arm = unit["identity_unit_id"].split("/", 1)[0]
            self.assertEqual(
                unit["producer_plan_reference"]["plan_id"], producer_by_arm[arm]
            )
            self.assertTrue(
                all(
                    isinstance(value, str) and len(value) == 64
                    for value in unit["model_runtime_config"].values()
                )
            )
            config_hashes = {
                scientific_config_identity_sha256(read_json(PACK / row["path"]))
                for row in unit["config_inventory"]
            }
            self.assertEqual(len(config_hashes), 1)
            for row in unit["config_inventory"]:
                self.assertEqual(row["sha256"], sha256(PACK / row["path"]))
        serialized = json.dumps(projection, sort_keys=True)
        self.assertNotIn('"model_artifact_sha256": {', serialized)
        self.assertNotIn('"runtime_identity_sha256": ""', serialized)

    def test_receipt_oracle_is_recomputed_from_the_production_model(self) -> None:
        expected = derive_bracket_session_receipt_oracle()
        actual = self.tree["arm_attachments"]["receipt_oracle"]
        self.assertEqual(actual, expected)
        self.assertIsNone(actual["terminal_sequence"])
        self.assertEqual(actual["arm_time_receipts"], [])
        for attachment in (
            self.tree["closeout_attachments"]["bracket_binding_sha256"],
            self.tree["closeout_attachments"]["terminal_committed_head"],
            self.analysis["postcollection_attachments"]["bracket_binding_sha256"],
            self.analysis["postcollection_attachments"][
                "committed_terminal_ledger_head"
            ],
        ):
            self.assertEqual(attachment["status"], "EMPTY")
            self.assertEqual(attachment["value"], "")
        stale_marker = "impl/d117-" + "ledger-recovery"
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK.rglob("*"))
            if path.is_file() and path.suffix in {".json", ".md", ".py", ".sha256"}
        )
        self.assertNotIn(stale_marker, generated_text)

    def test_decode_multiplicity_is_explicitly_contingent(self) -> None:
        decode = next(
            cell
            for cell in self.plan["floor_cells"]
            if cell["measurement_arm"] == "decode"
        )
        self.assertEqual(decode["family_m"], 1)
        self.assertIn("contingent", decode["multiplicity_note"])
        self.assertIn("prefill_p256", decode["multiplicity_note"])
        analysis_decode = next(
            contrast
            for contrast in self.analysis["contrasts"]
            if contrast["measurement_arm"] == "decode"
        )
        self.assertEqual(analysis_decode["multiplicity"]["m"], 1)
        self.assertIn("contingent", analysis_decode["multiplicity"]["note"])


if __name__ == "__main__":
    unittest.main()
