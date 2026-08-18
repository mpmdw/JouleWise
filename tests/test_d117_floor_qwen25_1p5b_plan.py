from __future__ import annotations

import hashlib
import importlib.util
import json
import re
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
V1_SPEC_RELS = (
    SPEC_REL,
    Path("configs/floor_mint/d117_qwen25_7b_extraction_spec.json"),
)
GENERATOR = PACK_ROOT / "generate_configs.py"
GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "d117_alpha_generator", GENERATOR
)
assert GENERATOR_SPEC is not None and GENERATOR_SPEC.loader is not None
GENERATOR_MODULE = importlib.util.module_from_spec(GENERATOR_SPEC)
# Loading a pack generator by file location writes __pycache__ INTO the
# tracked v1 pack, where sibling arm-readiness fixtures then copy it as a
# pack file and fail on a build byproduct. Suppress the cache write for
# this one load and restore the interpreter default.
_PREVIOUS_DONT_WRITE_BYTECODE = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    GENERATOR_SPEC.loader.exec_module(GENERATOR_MODULE)
finally:
    sys.dont_write_bytecode = _PREVIOUS_DONT_WRITE_BYTECODE
PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1"
EVIDENCE_ROOT_ID = "evidence-d117-floor-qwen25-1p5b-v1"
CONTRAST_PACK = ROOT / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1"
P256_FAMILY_ID = "df-ph-prefill-p256-qwen25-1p5b"
LEGACY_DECODE_PLAN_SHA256 = "56b164904cd0ffd0b9af5710ab60e4794cbd47b866a1053de5a7548475bda182"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.detection_floor import (  # noqa: E402
    COMMON_MODE_ESTIMATOR_ID,
    CONDITION_FAMILY_DOMAIN,
    canonical_domain_sha256,
    two_shared_edge_common_mode_registration,
)
from joulewise.floor_mint_estimator import (  # noqa: E402
    selection_from_authenticated_spec,
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


FROZEN_GENERATOR_SHA256 = "ea0d93ac653bf2b0610691aff668e4f4f7941ae7734ca2e0500589ddfd325c06"
EXPECTED_PACK_SHA256 = "17210f5cea020367f3ff18574c096fee90799e115aaf525365b1806c76fbdd3b"
EXPECTED_FILE_SHA256 = {
    "generate_configs.py": "82d263bf18024875eaad2124bdcc65e3a9801c76e80a867938611b8979a9ffc6",
    "calibration_plan.json": "2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d",
    "calibration_plan.sha256": "707712fb1152ed41b6d48432932bacf16e6856c8432dafb699e951b077e09312",
    "order_manifest.json": "5c5bd84579ff6bcfe4c0e3c800550f35bd4a04a5cd0061e105c9c3e4775f9fff",
    "plan_tree.json": "3e725c047c9850d507564e4a5131d1b65a739d2e452aab209652db05433bad6c",
    "plan_tree.sha256": "76c6a6e66618acd4782d8513aa302f1b36288da276620209b02c3689f46ba972",
    "producer_contract.json": "1a99f77ff436f3a6464d63a42142c55fcb5af6bc6fd1c3b87d8dbec3ccb97a0a",
    "condition_families/condition_family_df_ph_decode.json": (
        "c9054d11a2bf9c4b1718d93ededc44864cfffb34417d19f1178a9d18addcf8a8"
    ),
    "condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json": (
        "985a4e5370724698b601303b2ba99027d298060eedc95a65d20112df413043ad"
    ),
    "condition_families/condition_family_df_ph_prefill_p256_qwen25_1p5b.json": (
        "c7d2b28276791ab8c5c10b27460bbccba6cb7aad75470e9d74ba4b64ed4ef9f2"
    ),
}
EXPECTED_SPEC_SHA256 = "d98ae4deb787caaf8a80f972b88b2c85ecc2f96a13092e9127c1e1a661640fd2"
EXPECTED_FAMILY_DOMAIN_SHA256 = {
    "df-ph-decode": "e38e2a2f3e76b8cdd6b3ef4f5d3d7090ef4846dbf83279001ff4df8a9a762bfe",
    "df-ph-prefill-p128-qwen25-1p5b": (
        "974014e096806423b866a167510787482397cb4f68bb9e6f9f0ba7fd34f93f36"
    ),
    "df-ph-prefill-p256-qwen25-1p5b": (
        "93c9ee9b32c8c2b25675cff263e2c98882fe5f0c7f81f3ad6899f55f6f9d3c39"
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
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/prefill_prompt_candidate.json": (
        "9e1d8eecb688a4ae54c76d24d71be618411c011fa5bebffa44ad6a91ef03d456"
    ),
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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


# Namespaces a pack acquires AFTER generation, from the separate governed
# tools: the D-134 freeze-receipt mint (`arm_readiness.freeze.receipts/`), the
# readiness evidence authors (`arm_readiness.evidence/`) together with the
# source facts those authors pin (`arm_readiness.sources/`), and the
# identity-pin projection minter (`identity_pin_projection.receipts/`) -- each
# JSON accompanied by its `.sha256` sidecar, which is why whole namespaces
# rather than individual files are named here.
#
# Derivation: this tuple is exactly the directory set of
# (files in the committed pack) - (the generator's own `expected_pack_paths()`)
# for every frozen D-117 pack in the family. `generate_configs.py` emits none
# of them, and the successor test re-derives that emptiness half of the
# subtraction at run time against the freshly generated pack, so the exclusion
# can never silently absorb a file generation actually owns.
GOVERNED_POST_GENERATION_NAMESPACES = (
    "arm_readiness.evidence",
    "arm_readiness.freeze.receipts",
    "arm_readiness.sources",
    "identity_pin_projection.receipts",
)


def governed_post_generation_files(pack_root: Path) -> set[Path]:
    """Return pack-relative files under the governed post-generation namespaces."""

    found: set[Path] = set()
    for namespace in GOVERNED_POST_GENERATION_NAMESPACES:
        directory = pack_root / namespace
        if not directory.is_dir():
            continue
        found |= {
            path.relative_to(pack_root)
            for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
    return found


def minted_successor_pack_rels(current_rel: Path = PACK_REL) -> list[Path]:
    """Return the successor family packs this repository has already minted."""

    family_stem = current_rel.name.removesuffix(
        GENERATOR_MODULE.CURRENT_FAMILY_SUFFIX
    )
    minted: list[Path] = []
    ordinal = 2
    while True:
        candidate = current_rel.with_name(f"{family_stem}_v{ordinal}")
        if not (ROOT / candidate).is_dir():
            return minted
        minted.append(candidate)
        ordinal += 1


def unminted_successor_family_suffix(current_rel: Path = PACK_REL) -> str:
    """Return the first successor family ordinal the repository has not minted.

    Successor generation is freeze-aware by design: the generator derives its
    arm-readiness attachment from the TARGET pack's committed state, so
    regenerating an ALREADY-minted family threads that family's D-134 freeze
    receipt into the emitted plan tree -- a receipt the emitted checkout cannot
    carry, because the governed post-generation tools mint it and
    `generate_configs.py` never does. The emitted pack would then reference a
    receipt that is not in its own inventory, and the emitted generator's own
    `--check` would refuse the frozen identity outright.

    This test is about emitting a BRAND-NEW successor family, so it always
    targets the first ordinal that has not been minted yet: `_v2` before the
    family migration, `_v3` once the `_v2` packs are committed, and so on. What
    the test exercises is therefore independent of how much of the family is
    already committed, and of whether the committed part is frozen.
    """

    minted = minted_successor_pack_rels(current_rel)
    return f"_v{len(minted) + 2}"


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
        "condition_families/condition_family_df_ph_prefill_p256_qwen25_1p5b.json",
        "01_phase_decode_absolute/order_manifest.json",
        "02_phase_decode_abba_blocks_01_05/order_manifest.json",
        "03_phase_decode_abba_blocks_06_10/order_manifest.json",
        "04_phase_prefill_p256_absolute/order_manifest.json",
        "05_phase_prefill_p256_abba_blocks_01_05/order_manifest.json",
        "06_phase_prefill_p256_abba_blocks_06_10/order_manifest.json",
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
    paths.update(
        f"04_phase_prefill_p256_absolute/d117f15-df-ph-prefill-p256-abs-r{rep:02d}.json"
        for rep in range(1, 11)
    )
    for block in range(1, 11):
        stage = (
            "05_phase_prefill_p256_abba_blocks_01_05"
            if block <= 5
            else "06_phase_prefill_p256_abba_blocks_06_10"
        )
        paths.update(
            f"{stage}/d117f15-df-cmp-abba-ph-prefill-p256-b{block:02d}-{position}.json"
            for position in ("a1", "b1", "b2", "a2")
        )
    return paths | governed_frozen_attachment_paths(PACK_ROOT)


def pack_digest(pack_root: Path) -> str:
    # Exclude interpreter byte-code caches: importing generate_configs.py
    # (which this suite does) drops __pycache__ into the pack, so an
    # unfiltered digest passes on a fresh checkout and fails on every later
    # run. Aligned with the gamma generator/suite filter (cold-gate C5).
    paths = sorted(
        path
        for path in pack_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
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


def link_successor_self_check_inputs(output_root: Path) -> None:
    if not (output_root / "joulewise").exists():
        (output_root / "joulewise").symlink_to(ROOT / "joulewise", target_is_directory=True)
    for source_dir in (ROOT / "configs", ROOT / "configs/campaigns", ROOT / "configs/floor_mint"):
        target_dir = output_root / source_dir.relative_to(ROOT)
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in source_dir.iterdir():
            # Never import committed successor-generation artifacts as
            # symlinks: they sit at exactly the paths successor generation
            # writes, and the round-4 write boundary refuses symlinked
            # targets/ancestors. Each test generates its own successors.
            if re.search(r"_v[2-9]\d*(_extraction_spec\.json)?$", source.name):
                continue
            target = target_dir / source.name
            if not target.exists():
                target.symlink_to(source, target_is_directory=source.is_dir())
    successor_contrast = (
        output_root / "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2"
    )
    if not successor_contrast.exists():
        successor_contrast.symlink_to(CONTRAST_PACK, target_is_directory=True)


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
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(actual, expected_pack_paths())
        self.assertEqual(len(actual), 154)
        self.assertEqual(pack_digest(PACK_ROOT), EXPECTED_PACK_SHA256)
        for relative, expected in EXPECTED_FILE_SHA256.items():
            with self.subTest(relative=relative):
                self.assertEqual(sha256_file(PACK_ROOT / relative), expected)
        self.assertEqual(sha256_file(SPEC_PATH), EXPECTED_SPEC_SHA256)

    def test_two_regenerations_are_byte_identical_and_check_passes(self) -> None:
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
        self.assertIn("verified unfrozen draft: 100 science configs", checked.stdout)
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for output_root in (first, second):
                generated = subprocess.run(
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
                self.assertEqual(generated.returncode, 0, generated.stderr)
            generated_paths = {
                path.as_posix() for path in GENERATOR_MODULE.expected_pack_paths()
            }
            for relative in sorted(generated_paths):
                first_bytes = (Path(first) / PACK_REL / relative).read_bytes()
                second_bytes = (Path(second) / PACK_REL / relative).read_bytes()
                self.assertEqual(first_bytes, second_bytes, relative)
                self.assertEqual(first_bytes, (PACK_ROOT / relative).read_bytes(), relative)
            self.assertEqual(
                (Path(first) / SPEC_REL).read_bytes(),
                (Path(second) / SPEC_REL).read_bytes(),
            )
            self.assertEqual((Path(first) / SPEC_REL).read_bytes(), SPEC_PATH.read_bytes())

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
            pack_id="d117_floor_qwen25_1p5b_v2",
            family_suffix="_v2",
            preserve_current_frozen_bytes=False,
        )
        future = GENERATOR_MODULE.freeze_aware_reservation_plan_arguments(
            future_identity
        )
        self.assertEqual(
            [token["value"] for token in future],
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
        self.assertEqual(frozen_state_readme, (PACK_ROOT / "README.md").read_bytes())
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
            pack_id="d117_floor_qwen25_1p5b_v2",
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
        expected = {
            successor.pack_rel / path
            for path in GENERATOR_MODULE.expected_pack_paths()
        } | {GENERATOR_MODULE.extraction_spec_rel(successor)}
        self.assertEqual(
            GENERATOR_MODULE.validate_generation_output_inventory(successor), expected
        )
        for pack_id, suffix, preserve in (
            ("d117_floor_qwen25_1p5b_v0", "_v0", False),
            ("d117_floor_qwen25_1p5b_v2", "_v2", True),
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
            pack_id="d117_floor_qwen25_1p5b_v2",
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
                prefix="d117-alpha-symlink-root-"
            ) as temp, tempfile.TemporaryDirectory(
                prefix="d117-alpha-symlink-escape-"
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
        successor_suffix = unminted_successor_family_suffix()
        successor_token = successor_suffix.removeprefix("_")
        next_suffix = f"_v{int(successor_suffix.removeprefix('_v')) + 1}"
        successor_id = PACK_REL.name.removesuffix(
            GENERATOR_MODULE.CURRENT_FAMILY_SUFFIX
        ) + successor_suffix
        successor_rel = PACK_REL.with_name(successor_id)
        successor_spec_rel = Path(
            f"configs/floor_mint/d117_qwen25_1p5b{successor_suffix}"
            "_extraction_spec.json"
        )
        next_spec_rel = Path(
            f"configs/floor_mint/d117_qwen25_1p5b{next_suffix}_extraction_spec.json"
        )
        with tempfile.TemporaryDirectory(prefix=f"d117-alpha{successor_suffix}-") as temp:
            output_root = Path(temp)
            tracked = initialize_git_tracked_checkout(
                output_root, (PACK_REL, *V1_SPEC_RELS)
            )
            self.assertTrue(set(V1_SPEC_RELS) <= tracked)
            baseline_inventory = checkout_inventory(output_root)
            v1_spec_hashes = {
                relative: sha256_file(output_root / relative)
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
                    relative: sha256_file(output_root / relative)
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
                successor_suffix,
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
                    relative: sha256_file(output_root / relative)
                    for relative in V1_SPEC_RELS
                },
                v1_spec_hashes,
            )
            # Generation owns the GENERATED layer and nothing else. The
            # governed post-generation namespaces are minted afterwards by the
            # separate governed tools, so the emitted successor carries none of
            # them -- which is exactly why the generated-vs-committed file-set
            # comparison must exclude them.
            generated_layer = {
                Path(relative)
                for relative in GENERATOR_MODULE.expected_pack_paths()
            }
            self.assertEqual(
                governed_post_generation_files(output_root / successor_rel), set()
            )
            for minted_rel in minted_successor_pack_rels():
                with self.subTest(minted_successor=minted_rel.name):
                    committed_governed = governed_post_generation_files(
                        ROOT / minted_rel
                    )
                    # Principled exclusion, not a blind filter: the excluded
                    # namespaces never overlap the generated layer, and a
                    # committed pack that has been frozen really does carry
                    # every one of them.
                    self.assertEqual(committed_governed & generated_layer, set())
                    if (
                        ROOT / minted_rel / "arm_readiness.freeze.receipts"
                    ).is_dir():
                        self.assertEqual(
                            {
                                relative.parts[0]
                                for relative in committed_governed
                            },
                            set(GOVERNED_POST_GENERATION_NAMESPACES),
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
            tree = load_json(pack_root / "plan_tree.json")
            producer = load_json(pack_root / "producer_contract.json")
            successor_spec = load_json(output_root / successor_spec_rel)
            root_manifest = load_json(pack_root / "order_manifest.json")
            root_manifest_sha256 = sha256_file(pack_root / "order_manifest.json")
            self.assertEqual(tree["plan"]["path"], "calibration_plan.json")
            self.assertEqual(tree["plan"]["sidecar_path"], "calibration_plan.sha256")
            self.assertEqual(producer["plan"]["path"], tree["plan"]["path"])
            self.assertEqual(
                tree["plan"]["plan_id"],
                PLAN_ID.removesuffix("v1") + successor_token,
            )
            self.assertEqual(
                tree["window_identity"]["evidence_root_id"],
                EVIDENCE_ROOT_ID.removesuffix("v1") + successor_token,
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
                sha256_file(output_root / successor_spec_rel),
            )
            self.assertEqual(
                producer["extraction_spec"]["sha256"],
                sha256_file(output_root / successor_spec_rel),
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
                    EVIDENCE_ROOT_ID.removesuffix("v1") + successor_token,
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
                f'CURRENT_FAMILY_SUFFIX = "{successor_suffix}"',
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

            commit_fixture(output_root, "track emitted alpha v2")
            tracked_spec_hashes = {
                relative: sha256_file(output_root / relative)
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
                    relative: sha256_file(output_root / relative)
                    for relative in (*V1_SPEC_RELS, successor_spec_rel)
                },
                tracked_spec_hashes,
            )
            self.assertFalse(
                (output_root / next_spec_rel).exists()
            )
            preserved_tree = load_json(pack_root / "plan_tree.json")
            for row in preserved_tree["science"]:
                config = load_json(output_root / row["config_path"])
                self.assertIn("launch_lineage_required", config["run_metadata"]["tags"])

        for row in self.tree["science"]:
            current = load_json(ROOT / row["config_path"])
            self.assertNotIn(
                "launch_lineage_required", current["run_metadata"]["tags"]
            )

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
        self.assertEqual(self.tree["generator"]["sha256"], FROZEN_GENERATOR_SHA256)
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
        self.assertEqual(len(rows), 100)
        self.assertEqual([row["index"] for row in rows], list(range(1, 101)))
        self.assertEqual(len({row["run_id"] for row in rows}), 100)
        self.assertEqual(
            [stage["planned_n_bundles"] for stage in self.root_manifest["subcampaign_order"]],
            [10, 20, 20, 10, 20, 20],
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
            block_rows = [row for row in rows[:50] if row["role"] == "comparative_abba_member" and row["block_index"] == block]
            self.assertEqual([row["position"] for row in block_rows], ["A1", "B1", "B2", "A2"])
            self.assertEqual([row["arm"] for row in block_rows], ["A", "B", "B", "A"])
            self.assertEqual([row["position_in_block"] for row in block_rows], [1, 2, 3, 4])
        self.assertEqual(
            [row["run_id"] for row in rows[50:60]],
            [f"d117f15-df-ph-prefill-p256-abs-r{rep:02d}" for rep in range(1, 11)],
        )
        for block in range(1, 11):
            block_rows = [
                row
                for row in rows[60:]
                if row["role"] == "comparative_abba_member"
                and row["block_index"] == block
            ]
            self.assertEqual([row["position"] for row in block_rows], ["A1", "B1", "B2", "A2"])
            self.assertEqual([row["arm"] for row in block_rows], ["A", "B", "B", "A"])
        graph_ids = [stage["stage_id"] for stage in self.tree["stage_graph"]]
        self.assertLess(graph_ids.index("alpha-science-abba-06-10"), graph_ids.index("alpha-reference-midpoint"))
        self.assertLess(graph_ids.index("alpha-reference-midpoint"), graph_ids.index("alpha-science-prefill-p256-absolute"))
        entries, warning = load_order_entries(PACK_ROOT)
        self.assertIsNone(warning)
        self.assertEqual([entry.run_id for entry in entries], [row["run_id"] for row in rows])
        self.assertEqual(self.plan["execution_mode"]["planned_reference_bundles"], 7)
        self.assertEqual(
            self.tree["runtime_budget"]["planning_estimate_minutes_with_margin"],
            376.8,
        )
        self.assertEqual(self.tree["runtime_budget"]["planning_estimate_hours_with_margin"], 6.28)

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
            is_p256 = "prefill-p256" in row["run_id"]
            if is_p256:
                self.assertNotIn("prompt_tokens", config["workload_profile"])
                self.assertIn("prompt_text", config["workload_profile"])
            else:
                self.assertEqual(config["workload_profile"]["prompt_tokens"], 128)
            self.assertEqual(config["workload_profile"]["output_tokens"], 512)
            self.assertEqual(config["sampling"], {"power_hz": 10.0, "idle_seconds": 30.0, "warmup_seconds": 5.0})
            tags = config["run_metadata"]["tags"]
            self.assertIn("d117-floor-qwen25-1p5b-v1", tags)
            self.assertIn("production-window", tags)
            self.assertIn("floor-calibration", tags)
            expected_family = P256_FAMILY_ID if is_p256 else "df-ph-decode"
            self.assertIn(f"df-condition={expected_family}", tags)
            expected_plan_sha = plan_sha if is_p256 else LEGACY_DECODE_PLAN_SHA256
            self.assertIn(f"calibration-plan-sha256={expected_plan_sha}", tags)

    def test_p256_workload_is_byte_identical_to_consumer_arm(self) -> None:
        floor_row = next(
            row
            for row in self.root_manifest["executed_order"]
            if row["run_id"].startswith("d117f15-df-ph-prefill-p256-abs-")
        )
        contrast_manifest = load_json(CONTRAST_PACK / "order_manifest.json")
        contrast_row = next(
            row
            for row in contrast_manifest["executed_order"]
            if row["measurement_arm"] == "prefill_p256" and row["arm"] == "A"
        )
        floor_workload = load_json(PACK_ROOT / floor_row["config"])["workload_profile"]
        contrast_workload = load_json(CONTRAST_PACK / contrast_row["config"])["workload_profile"]
        self.assertEqual(floor_workload, contrast_workload)
        self.assertIn("prompt_text", floor_workload)
        self.assertNotIn("prompt_tokens", floor_workload)

    def test_condition_families_and_dedicated_p256_domain(self) -> None:
        family_paths = {
            "df-ph-decode": PACK_ROOT / "condition_families/condition_family_df_ph_decode.json",
            "df-ph-prefill-p128-qwen25-1p5b": PACK_ROOT / "condition_families/condition_family_df_ph_prefill_p128_qwen25_1p5b.json",
            P256_FAMILY_ID: PACK_ROOT / "condition_families/condition_family_df_ph_prefill_p256_qwen25_1p5b.json",
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
        p256_definition = load_json(family_paths[P256_FAMILY_ID])
        self.assertEqual(p256_definition["workload_profile"]["prompt_tokens"], 256)
        self.assertEqual(p256_definition["workload_profile"]["name"], "df_ph_prefill_p256_candidate")
        p256_binding = next(
            row for row in self.tree["condition_families"]
            if row["condition_family_id"] == P256_FAMILY_ID
        )
        self.assertEqual(p256_binding["prompt_text_utf8_sha256"], "f149dddcb4b9d27b3d68b0455c5f774e56e37bfc04430b53e139a4c08f044faf")
        self.assertEqual(p256_binding["ruled_token_id_sha256_prefix"], "83099a66")
        self.assertIn("no full-hex", p256_binding["token_id_sha256_pin_status"])
        self.assertEqual(self.plan["execution_mode"]["planned_science_bundles"], 100)
        self.assertEqual(self.spec["phase_presence_contract"]["required_metrics"], ["phase_energy_j.decode", "phase_energy_j.prefill"])
        self.assertEqual(self.spec["phase_presence_contract"]["missing_registered_phase"], "refuse_before_floor_or_reported_mean_emission")

    def test_six_floor_cells_and_reported_means_keep_disjoint_domains(self) -> None:
        self.assertEqual(validate_extraction_spec(self.spec), [])
        cells = self.spec["cells"]
        self.assertEqual(
            [cell["cell_id"] for cell in cells],
            [
                "d117-df-ph-decode-qwen25-1p5b-absolute",
                "d117-df-cmp-abba-ph-decode-qwen25-1p5b",
                "d117-df-ph-prefill-p128-qwen25-1p5b-absolute",
                "d117-df-cmp-abba-ph-prefill-p128-qwen25-1p5b",
                "d117-df-ph-prefill-p256-qwen25-1p5b-absolute",
                "d117-df-cmp-abba-ph-prefill-p256-qwen25-1p5b",
            ],
        )
        references = [floor_reference_ids(cell) for cell in cells]
        self.assertEqual([len(ids) for ids in references], [10, 40, 10, 40, 10, 40])
        self.assertEqual(references[0], references[2])
        self.assertEqual(references[1], references[3])
        all_floor_references = [bundle_id for ids in references for bundle_id in ids]
        self.assertEqual(len(all_floor_references), 150)
        self.assertEqual(len(set(all_floor_references)), 100)
        self.assertTrue(set(references[0] + references[1]).isdisjoint(references[4] + references[5]))
        self.assertEqual(
            self.spec["reference_counts"],
            {
                "floor_cell_references": 150,
                "reported_energy_references": 150,
                "total_registered_references": 300,
                "unique_physical_bundles": 100,
                "unique_config_paths": 100,
            },
        )
        physical_order = [row["run_id"] for row in self.root_manifest["executed_order"]]
        reported = self.spec["reported_energy_cells"]
        self.assertEqual(len(reported), 3)
        for index, cell in enumerate(reported):
            self.assertEqual(cell["reducer"], "arithmetic_mean_over_fixed_member_universe.v1")
            self.assertEqual(cell["expected_n"], 50)
            expected_order = physical_order[:50] if index < 2 else physical_order[50:]
            self.assertEqual([member["bundle_id"] for member in cell["members"]], expected_order)
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

    def test_issued_acceptance_and_common_mode_estimator_path_are_registered(self) -> None:
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
        for cell in (self.spec["cells"][0], self.spec["cells"][2], self.spec["cells"][4]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (self.spec["cells"][1], self.spec["cells"][3], self.spec["cells"][5]):
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
                        ROOT / "configs/calibration/calibration_acceptance_d079_v2.json"
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
        for cell in (self.plan["floor_cells"][0], self.plan["floor_cells"][2], self.plan["floor_cells"][4]):
            self.assertEqual(cell["estimator"], "d054_false_effect_guard.v1")
        for cell in (self.plan["floor_cells"][1], self.plan["floor_cells"][3], self.plan["floor_cells"][5]):
            self.assertEqual(cell["estimator"], COMMON_MODE_ESTIMATOR_ID)
            self.assertNotIn("estimator_registration", cell)

    def test_typed_launch_recipes_are_complete_and_portable(self) -> None:
        graph = self.tree["stage_graph"]
        self.assertEqual([stage["ordinal"] for stage in graph], list(range(1, 17)))
        self.assertEqual(sum(len(stage["launch"]["commands"]) for stage in graph), 17)
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
        self.assertEqual(projection["state"], "frozen")
        self.assertEqual(projection["derivation_contract"], IDENTITY_PIN_DERIVATION_CONTRACT)
        self.assertEqual(projection["supersedes"], [])
        self.assertEqual(len(projection["identity_units"]), 2)
        self.assertEqual(
            [unit["identity_unit_id"] for unit in projection["identity_units"]],
            ["alpha", "alpha/prefill_p256"],
        )
        unit = projection["identity_units"][0]
        self.assertEqual(unit["identity_unit_id"], "alpha")
        self.assertTrue(
            all(
                isinstance(value, str) and len(value) == 64
                for value in unit["model_runtime_config"].values()
            )
        )
        computed_config_hashes = {
            scientific_config_identity_sha256(load_json(PACK_ROOT / row["path"]))
            for row in unit["config_inventory"]
        }
        self.assertEqual(len(computed_config_hashes), 1)
        for row in unit["config_inventory"]:
            self.assertEqual(row["sha256"], sha256_file(PACK_ROOT / row["path"]))
        p256_unit = projection["identity_units"][1]
        p256_config_hashes = {
            scientific_config_identity_sha256(load_json(PACK_ROOT / row["path"]))
            for row in p256_unit["config_inventory"]
        }
        self.assertEqual(len(p256_config_hashes), 1)
        self.assertEqual(len(p256_unit["config_inventory"]), 50)
        projection_receipt = projection["projection_receipt"]
        self.assertIsNotNone(projection_receipt)
        receipt_path = PACK_ROOT / projection_receipt["path"]
        self.assertEqual(sha256_file(receipt_path), projection_receipt["sha256"])
        self.assertEqual(
            receipt_path.with_suffix(".sha256").read_text(encoding="utf-8"),
            f"{projection_receipt['sha256']}  {receipt_path.name}\n",
        )
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
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix in {".json", ".md", ".py", ".sha256"}
        )
        self.assertNotIn(stale_marker, generated_text)

    def test_no_historical_claim_bytes_or_generation_discovery(self) -> None:
        generated_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(PACK_ROOT.rglob("*"))
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix in {".json", ".md", ".sha256"}
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
