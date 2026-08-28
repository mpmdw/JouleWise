from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import tokenize
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
import joulewise.arm_readiness_evidence as evidence_author
from joulewise.arm_readiness import (
    HISTSEM_REASON_CODES,
    READINESS_REASON_CODES,
    HistoricalSemanticsError,
    _authenticate_generic_evidence_item,
    committed_pack_tree_sha256,
    generate_arm_receipt,
    generate_freeze_receipt,
    gnu_sidecar,
    historical_pack_tree_sha256,
    render_json,
    verify_all_receipt_histsem,
    verify_receipt_histsem_pack,
)
from tests.test_arm_readiness_evidence_author import (
    make_author_fixture,
    passing_suites,
)
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID
from tests.test_arm_readiness_lifecycle import commit_u11_projection


ROOT = Path(__file__).resolve().parents[1]
PINSET = ROOT / "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"
PINSET_SHA256 = "d81515505d677c2ca045238e721c87eae8f38439a89a5377e58fa9064eaf2f21"
REPRESENTATIVE_PACK = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v3"

# The versioned successor member of the code-enumerated chain.  It does not
# exist until S-0 mints it, and the chain loader treats an absent enumerated
# member as contributing no rows rather than as a refusal
# (arm_readiness.py:3196-3199; docs/contracts/receipt_histsem_verifier.md:53-57).
# Every assertion about it below is therefore PRESENCE-CONDITIONAL: vacuous
# before the mint, active after it.
SUCCESSOR_PINSET = ROOT / "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
# D-151 condition-3 ruled shape literals.  These are CONSISTENCY CHECKS ONLY and
# are explicitly NOT byte authenticators: condition 2 forbids this file from
# authenticating the successor, whose only byte authenticator is the hS literal
# pinned by the post-window fixation commit (D-153 A1).  Asserting shape here
# must never be read as, or relied on as, authenticating the minted bytes.
SUCCESSOR_PACK_COUNT = 3
SUCCESSOR_RECEIPT_COUNT = 33
SUCCESSOR_PACK_IDS = frozenset(
    {
        "d117_contrast_qwen25_1p5b_vs_7b_v4",
        "d117_floor_qwen25_1p5b_v4",
        "d117_floor_qwen25_7b_v4",
    }
)


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )


def write_custody_json(directory: Path, name: str, value: object) -> Path:
    """Write a canonical custody artifact plus its GNU sha256 sidecar."""

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    raw = render_json(value)
    path.write_bytes(raw)
    path.with_name(f"{name}.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(raw).hexdigest(), name)
    )
    return path


def write_pinset(path: Path, mutate: callable) -> Path:
    value = json.loads(PINSET.read_bytes())
    row = next(item for item in value["packs"] if item["pack_id"] == REPRESENTATIVE_PACK.name)
    mutate(row)
    path.write_bytes(render_json(value))
    return path


class ReceiptHistoricalSemanticsTests(unittest.TestCase):
    def test_contract_defines_custody_coordinate_and_tautology_at_first_use(
        self,
    ) -> None:
        contract = (
            ROOT / "docs/contracts/receipt_histsem_verifier.md"
        ).read_text(encoding="utf-8")
        custody_definition = (
            "A **custody coordinate** is the current committed pack state being "
            "protected"
        )
        tautology_definition = (
            "A **tautology** is a comparison that cannot independently detect "
            "the change"
        )
        self.assertEqual(
            contract.lower().find("custody coordinate"),
            contract.lower().find(custody_definition.lower()) + 4,
        )
        self.assertEqual(
            contract.lower().find("tautology"),
            contract.lower().find(tautology_definition.lower()) + 4,
        )
        echo = contract.index("committed `plan_tree.json` is mutated")
        self.assertLess(echo, contract.index("`calibration_plan.json`", echo))
        self.assertRegex(contract[echo:], r"pinned\s+external\s+artifacts")

    def test_pinset_chain_is_closed_ordered_and_absent_successor_is_unchanged(self) -> None:
        self.assertEqual(
            readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH,
            (
                Path("configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"),
                Path("configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"),
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            directory = repository / "configs/arm_readiness"
            directory.mkdir(parents=True)
            (directory / "legacy_receipt_histsem_pinset_v1.json").write_bytes(PINSET.read_bytes())
            rows = readiness._load_histsem_pinset(repository)
            self.assertEqual(len(rows), 9)

            unenumerated = json.loads(PINSET.read_bytes())
            unenumerated["packs"][0]["pack_id"] = "not-governed-by-an-unenumerated-file"
            (directory / "receipt_histsem_pinset_rogue.json").write_bytes(render_json(unenumerated))
            self.assertEqual(len(readiness._load_histsem_pinset(repository)), 9)

    def test_pinset_chain_unions_successor_and_refuses_cross_member_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            directory = repository / "configs/arm_readiness"
            directory.mkdir(parents=True)
            (directory / "legacy_receipt_histsem_pinset_v1.json").write_bytes(PINSET.read_bytes())
            successor_path = directory / "legacy_receipt_histsem_pinset_v4_v1.json"
            successor = json.loads(PINSET.read_bytes())
            row = copy.deepcopy(successor["packs"][0])
            row["pack_id"] = "d117_synthetic_v4"
            row["pack_path"] = "configs/campaigns/d117_synthetic_v4"
            successor["packs"] = [row]
            successor_path.write_bytes(render_json(successor))
            rows = readiness._load_histsem_pinset(repository)
            self.assertEqual(len(rows), 10)
            self.assertEqual(rows[-1]["pack_id"], "d117_synthetic_v4")

            successor_path.write_bytes(PINSET.read_bytes())
            with self.assertRaises(HistoricalSemanticsError) as caught:
                readiness._load_histsem_pinset(repository)
            self.assertEqual(caught.exception.reason_code, "histsem_pinset_invalid")

    def test_v4_builder_interface_is_exact_and_has_no_network_or_update_lane(self) -> None:
        completed = subprocess.run(
            ("python3", "scripts/build_v4_histsem_pinset.py", "--help"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        for option in (
            "--repository",
            "--base-pinset",
            "--historical-head",
            "--current-head",
            "--pack-root",
            "--output",
        ):
            self.assertIn(option, completed.stdout)
        source = (ROOT / "scripts/build_v4_histsem_pinset.py").read_text(encoding="utf-8")
        uncommented = "".join(
            token.string
            for token in tokenize.generate_tokens(io.StringIO(source).readline)
            if token.type != tokenize.COMMENT
        )
        for forbidden in ("fetch", "unshallow", "--update", "checkout"):
            self.assertNotIn(forbidden, uncommented)

    def test_pinset_is_byte_pinned_and_has_no_update_lane(self) -> None:
        self.assertEqual(hashlib.sha256(PINSET.read_bytes()).hexdigest(), PINSET_SHA256)
        script = (ROOT / "scripts/verify_receipt_histsem.py").read_text(encoding="utf-8")
        self.assertNotIn("--update", script)
        value = json.loads(PINSET.read_bytes())
        self.assertEqual(len(value["packs"]), 9)
        self.assertEqual(sum(row["receipt_count"] for row in value["packs"]), 99)

    def test_successor_member_shape_when_present(self) -> None:
        """Presence-conditional shape check on the versioned successor member.

        THIS IS NOT AN AUTHENTICATOR.  D-151 condition 2 forbids this file from
        authenticating the successor: allowlist membership makes it eligible for
        subtraction but never proves its bytes.  The successor's ONLY byte
        authenticator is the hS literal that the post-window fixation commit
        pins (D-153 A1), and nothing here may be relied on in its place.  What
        this method does is cheaper and different: it checks that the minted
        artifact has the SHAPE D-151 condition 3 ruled for it, so a
        structurally wrong mint is caught by the ordinary suite instead of
        surviving to the confirmation table.

        It is vacuous until the successor exists.  An absent enumerated member
        contributes no rows and is not a refusal (arm_readiness.py:3196-3199;
        docs/contracts/receipt_histsem_verifier.md:53-57), so before the mint
        this method asserts only that absence is handled as ruled -- which is
        why it can live in the PRE-DERIVATION candidate without being
        mint-falsifiable (D-153 A2).
        """

        if not SUCCESSOR_PINSET.exists():
            # Absence semantics: the chain still loads, and it holds exactly the
            # v1 member's rows.  Nothing about the successor is asserted.
            rows = readiness._load_histsem_pinset(ROOT)
            self.assertEqual(
                len(rows), len(json.loads(PINSET.read_bytes())["packs"])
            )
            self.skipTest("successor member not minted yet; shape check is vacuous")

        raw = SUCCESSOR_PINSET.read_bytes()
        # Canonical D-134 encoding: the committed bytes must already be the
        # canonical rendering, not merely parseable JSON.
        value = readiness.parse_json_bytes(raw, require_canonical=True)
        self.assertEqual(raw, render_json(value))
        # D-151 condition-3 ruled literals, used as consistency checks only.
        self.assertEqual(len(value["packs"]), SUCCESSOR_PACK_COUNT)
        self.assertEqual(
            sum(row["receipt_count"] for row in value["packs"]),
            SUCCESSOR_RECEIPT_COUNT,
        )
        self.assertEqual(
            {row["pack_id"] for row in value["packs"]}, set(SUCCESSOR_PACK_IDS)
        )
        # The v1 member is unchanged by the mint; the chain is the union of both.
        self.assertEqual(hashlib.sha256(PINSET.read_bytes()).hexdigest(), PINSET_SHA256)
        rows = readiness._load_histsem_pinset(ROOT)
        self.assertEqual(
            len(rows),
            len(json.loads(PINSET.read_bytes())["packs"]) + SUCCESSOR_PACK_COUNT,
        )

    def test_verifier_cli_refusal_is_canonical_and_exit_two(self) -> None:
        completed = subprocess.run(
            (
                "python3",
                "scripts/verify_receipt_histsem.py",
                "--repository-root",
                ".",
                "--pinset",
                "/definitely/absent/receipt-histsem-pinset.json",
            ),
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "REFUSE")
        self.assertEqual(payload["reason_codes"], ["histsem_pinset_invalid"])
        self.assertEqual(completed.stdout, render_json(payload))

    def test_differential_self_test_all_governed_packs(self) -> None:
        # Iterates the LOADED CHAIN rather than the v1 file, so the method stays
        # true in both coordinates: nine rows before the successor is minted,
        # twelve after, with no edit at the mint.  The old name asserted a count
        # that the mint falsifies (D-153 A2).
        for row in readiness._load_histsem_pinset(ROOT):
            with self.subTest(pack=row["pack_id"]):
                pack = ROOT / row["pack_path"]
                self.assertEqual(
                    historical_pack_tree_sha256(ROOT, row["pack_path"], "HEAD"),
                    committed_pack_tree_sha256(pack),
                )

    def test_full_corpus_verifies_two_coordinates_and_facts(self) -> None:
        result = verify_all_receipt_histsem(ROOT, require_published=True)
        self.assertEqual(result["status"], "PASS")
        # Corpus totals are DERIVED FROM THE LOADED CHAIN, never literal 9/99.
        # The mint alone would redden a literal pair here, which is precisely the
        # published-head-suite trap D-153 A2 removes: no mint-falsifiable
        # assertion may sit in a pre-derivation test.
        chain = readiness._load_histsem_pinset(ROOT)
        self.assertEqual(result["pack_count"], len(chain))
        self.assertEqual(
            result["receipt_count"],
            sum(int(row["receipt_count"]) for row in chain),
        )
        # Every governed receipt in the chain resolves at its recorded path and
        # carries at least one fact -- the two-coordinate/facts property, stated
        # over whatever the chain currently holds.
        for row in chain:
            for item in row["receipts"]:
                receipt_path = ROOT / row["pack_path"] / item["path"]
                with self.subTest(pack=row["pack_id"], receipt=item["path"]):
                    self.assertTrue(
                        json.loads(receipt_path.read_bytes())["facts"],
                        "governed receipt carries no facts",
                    )
        # The v1 member's own fact subtotal keeps its literal: v1 is archival and
        # byte-pinned by PINSET_SHA256, so the mint cannot move it.
        pinset = json.loads(PINSET.read_bytes())
        fact_count = sum(
            len(json.loads((ROOT / row["pack_path"] / item["path"]).read_bytes())["facts"])
            for row in pinset["packs"]
            for item in row["receipts"]
        )
        self.assertEqual(fact_count, 108)
        self.assertTrue(
            all(not row["advisories"] for row in result["packs"]), result["packs"]
        )
        # The committed archival records carry a foreign absolute pack_root.
        # Passing here pins the ruled location-agnostic behavior.
        freeze = json.loads(
            (REPRESENTATIVE_PACK / "arm_readiness.freeze.receipts/freeze-0003.json").read_bytes()
        )
        self.assertNotEqual(Path(freeze["pack_identity"]["pack_root"]), REPRESENTATIVE_PACK)

    def test_required_refusal_granularity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = {
                "histsem_historical_digest_mismatch": lambda row: row.__setitem__(
                    "historical_pack_sha256", "0" * 64
                ),
                "histsem_binding_mismatch": lambda row: row["freeze_receipt"].__setitem__(
                    "sha256", "0" * 64
                ),
                "histsem_pinset_mismatch": lambda row: row.__setitem__(
                    "current_pack_sha256", "0" * 64
                ),
                "histsem_post_authoring_delta_unexpected": lambda row: row[
                    "post_authoring_delta"
                ]["added"].pop(),
            }
            for expected, mutate in cases.items():
                with self.subTest(expected=expected):
                    pinset = write_pinset(root / f"{expected}.json", mutate)
                    rows = readiness._validate_histsem_pinset(
                        readiness.parse_json_bytes(
                            pinset.read_bytes(), require_canonical=True
                        )
                    )
                    with self.assertRaises(HistoricalSemanticsError) as caught:
                        verify_receipt_histsem_pack(
                            REPRESENTATIVE_PACK, _pinset_rows=rows
                        )
                    self.assertEqual(caught.exception.reason_code, expected)

            with self.assertRaises(HistoricalSemanticsError) as caught:
                verify_receipt_histsem_pack(
                    REPRESENTATIVE_PACK, pinset_path=root / "absent.json"
                )
            self.assertEqual(caught.exception.reason_code, "histsem_pinset_invalid")

            copied = root / "copied-valid-pinset.json"
            copied.write_bytes(PINSET.read_bytes())
            with self.assertRaises(HistoricalSemanticsError) as copied_refusal:
                verify_receipt_histsem_pack(
                    REPRESENTATIVE_PACK, pinset_path=copied
                )
            self.assertEqual(
                copied_refusal.exception.reason_code, "histsem_pinset_invalid"
            )

    def test_vocabulary_is_disjoint_closed_and_each_code_constructs(self) -> None:
        self.assertFalse(HISTSEM_REASON_CODES & READINESS_REASON_CODES)
        for code in HISTSEM_REASON_CODES:
            with self.subTest(code=code):
                self.assertEqual(HistoricalSemanticsError(code, "test").reason_code, code)
        with self.assertRaisesRegex(ValueError, "unregistered historical-semantics"):
            HistoricalSemanticsError("histsem_not_registered", "test")

    def test_shallow_history_refuses_without_fetch_or_repair(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "shallow"
            subprocess.run(
                (
                    "git",
                    "clone",
                    "-q",
                    "--depth=1",
                    f"file://{ROOT}",
                    str(clone),
                ),
                check=True,
                capture_output=True,
            )
            with self.assertRaises(HistoricalSemanticsError) as caught:
                historical_pack_tree_sha256(
                    clone,
                    "configs/campaigns/d117_floor_qwen25_1p5b_v3",
                    "HEAD",
                )
            self.assertEqual(caught.exception.reason_code, "histsem_history_shallow")
        source = readiness._histsem_git.__doc__ or ""
        self.assertIn("without fetch or repair", source)

    def test_origin_main_is_ci_hard_and_pre_arm_advisory(self) -> None:
        original = readiness._histsem_git

        def unpublished(repository: Path, *args: str):
            if args[:2] == ("merge-base", "--is-ancestor") and args[-1] == "origin/main":
                return 1, b"", b""
            return original(repository, *args)

        with mock.patch.object(readiness, "_histsem_git", side_effect=unpublished):
            advisory = verify_receipt_histsem_pack(REPRESENTATIVE_PACK)
            self.assertEqual(advisory["advisories"], ["histsem_commit_unpublished"])
            with self.assertRaises(HistoricalSemanticsError) as caught:
                verify_receipt_histsem_pack(
                    REPRESENTATIVE_PACK, require_published=True
                )
        self.assertEqual(caught.exception.reason_code, "histsem_commit_unpublished")

    def test_coherent_legacy_tamper_control_accepts_but_histsem_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(clone)),
                check=True,
                capture_output=True,
            )
            git(clone, "config", "user.email", "tests@joulewise.invalid")
            git(clone, "config", "user.name", "JouleWise tests")
            clone_pinset = clone / PINSET.relative_to(ROOT)
            self.assertEqual(clone_pinset.read_bytes(), PINSET.read_bytes())

            pack = clone / REPRESENTATIVE_PACK.relative_to(ROOT)
            tree_path = pack / "plan_tree.json"
            tree = json.loads(tree_path.read_bytes())
            freeze_path = pack / tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]["path"]
            freeze = json.loads(freeze_path.read_bytes())
            item = next(
                candidate
                for candidate in freeze["evidence"]
                if candidate["schema_version"] == readiness.EVIDENCE_RECEIPT_SCHEMA
            )
            receipt_path = pack / item["path"]
            receipt = json.loads(receipt_path.read_bytes())

            # Payload + the six-file receipt→sidecar→freeze→sidecar→plan→sidecar
            # authentication chain are changed coherently and committed.
            producer = pack / "producer_contract.json"
            producer_value = json.loads(producer.read_bytes())
            producer_value["histsem_regression_marker"] = "coherent-tamper"
            producer.write_bytes(render_json(producer_value))
            receipt["issued_at_utc"] = "2026-08-20T23:59:59Z"
            receipt_raw = render_json(receipt)
            receipt_path.write_bytes(receipt_raw)
            receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
            receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
                gnu_sidecar(receipt_sha, receipt_path.name)
            )
            item["sha256"] = receipt_sha
            freeze_raw = render_json(freeze)
            freeze_path.write_bytes(freeze_raw)
            freeze_sha = hashlib.sha256(freeze_raw).hexdigest()
            freeze_path.with_name(f"{freeze_path.name}.sha256").write_bytes(
                gnu_sidecar(freeze_sha, freeze_path.name)
            )
            tree["arm_attachments"]["arm_readiness"]["freeze_receipt"][
                "sha256"
            ] = freeze_sha
            tree_raw = readiness._render_plan_tree(tree)
            tree_path.write_bytes(tree_raw)
            (pack / "plan_tree.sha256").write_bytes(
                gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
            )
            git(clone, "add", pack.relative_to(clone).as_posix())
            git(clone, "commit", "-qm", "coherent legacy tamper")

            # CONTROL: this is the frozen PACK call shape that omits
            # expected_pack_sha256.  Both existing authenticators accept it.
            self.assertRegex(committed_pack_tree_sha256(pack), r"^[0-9a-f]{64}$")
            authenticated = _authenticate_generic_evidence_item(
                item, pack, pack, enforce_expiry=False
            )
            self.assertEqual(authenticated["evidence_id"], item["evidence_id"])

            # NEW: the static-current pin refuses before an arm custody write.
            with self.assertRaises(HistoricalSemanticsError) as caught:
                verify_receipt_histsem_pack(pack)
            self.assertEqual(caught.exception.reason_code, "histsem_pinset_mismatch")
            custody = Path(temporary) / "custody"
            result = generate_arm_receipt(pack, {}, custody)
            self.assertEqual(result["status"], "REFUSE")
            self.assertEqual(result["reason_codes"], ["histsem_pinset_mismatch"])
            self.assertIsNone(result["receipt_path"])
            self.assertFalse(custody.exists())

            # HEAD still defines this pack as governed, so removing the
            # worktree pinset cannot turn the gate off or replace its rows.
            (clone / PINSET.relative_to(ROOT)).unlink()
            with self.assertRaises(HistoricalSemanticsError) as absent:
                readiness._gate_receipt_histsem(pack)
            self.assertEqual(absent.exception.reason_code, "histsem_pinset_mismatch")

    def test_twelfth_unreferenced_legacy_receipt_cannot_bypass_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(clone)),
                check=True,
                capture_output=True,
            )
            git(clone, "config", "user.email", "tests@joulewise.invalid")
            git(clone, "config", "user.name", "JouleWise tests")
            pack = clone / REPRESENTATIVE_PACK.relative_to(ROOT)

            source_receipt = next((pack / "arm_readiness.evidence").glob("*.json"))
            rogue = json.loads(source_receipt.read_bytes())
            rogue["evidence_id"] = "freeze-extra-valid-legacy-v1"
            rogue["issued_at_utc"] = "2026-08-20T23:59:59Z"
            readiness.validate_evidence_receipt(rogue)
            (pack / "arm_readiness.evidence/extra-valid-legacy.json").write_bytes(
                render_json(rogue)
            )
            git(clone, "add", pack.relative_to(clone).as_posix())
            git(clone, "commit", "-qm", "add unused valid legacy receipt")
            self.assertEqual(
                len(list((pack / "arm_readiness.evidence").glob("*.json"))), 12
            )

            with self.assertRaises(HistoricalSemanticsError) as direct:
                verify_receipt_histsem_pack(pack)
            self.assertEqual(direct.exception.reason_code, "histsem_pinset_mismatch")
            with self.assertRaises(HistoricalSemanticsError) as gate:
                readiness._gate_receipt_histsem(pack)
            self.assertEqual(gate.exception.reason_code, "histsem_pinset_mismatch")

            custody = Path(temporary) / "custody"
            result = generate_arm_receipt(pack, {}, custody)
            self.assertEqual(result["status"], "REFUSE")
            self.assertEqual(result["reason_codes"], ["histsem_pinset_mismatch"])
            self.assertIsNone(result["receipt_path"])
            self.assertFalse(custody.exists())

    def test_gate_refuses_when_governed_clone_object_store_is_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            subprocess.run(
                ("git", "clone", "-q", "--no-local", str(ROOT), str(clone)),
                check=True,
                capture_output=True,
            )
            pack = clone / REPRESENTATIVE_PACK.relative_to(ROOT)
            objects = clone / ".git/objects"
            original_mode = objects.stat().st_mode
            objects.chmod(0)
            try:
                with self.assertRaises(HistoricalSemanticsError) as caught:
                    readiness._gate_receipt_histsem(pack)
            finally:
                objects.chmod(original_mode)
            self.assertEqual(caught.exception.reason_code, "histsem_history_unavailable")

    def test_symlinked_predecessor_alias_engages_histsem_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(clone)),
                check=True,
                capture_output=True,
            )
            git(clone, "config", "user.email", "tests@joulewise.invalid")
            git(clone, "config", "user.name", "JouleWise tests")
            git(clone, "config", "gc.auto", "0")
            git(clone, "config", "maintenance.auto", "false")
            pack = clone / REPRESENTATIVE_PACK.relative_to(ROOT)
            alias = pack.parent / "governed-pack-predecessor-alias"
            alias.symlink_to(pack, target_is_directory=True)

            # Make the governed pack fail its committed HEAD pin.  The alias
            # must resolve to the governed immutable identity before matching
            # the HEAD pinset row; an unresolved final component would miss it.
            producer = pack / "producer_contract.json"
            producer_value = json.loads(producer.read_bytes())
            producer_value["histsem_symlink_regression_marker"] = "tampered"
            producer.write_bytes(render_json(producer_value))
            git(clone, "add", pack.relative_to(clone).as_posix())
            git(clone, "commit", "-qm", "tamper governed pack for symlink regression")

            with self.assertRaises(HistoricalSemanticsError) as caught:
                readiness._gate_receipt_histsem(alias)
            self.assertEqual(caught.exception.reason_code, "histsem_pinset_mismatch")

    def test_committed_pinset_deletion_gate_returns_normally(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(clone)),
                check=True,
                capture_output=True,
            )
            git(clone, "config", "user.email", "tests@joulewise.invalid")
            git(clone, "config", "user.name", "JouleWise tests")
            # The removal commit below can trigger detached git auto-maintenance,
            # which races Python 3.11's tempdir teardown on CI (ENOTEMPTY).
            git(clone, "config", "gc.auto", "0")
            git(clone, "config", "maintenance.auto", "false")
            pack = clone / REPRESENTATIVE_PACK.relative_to(ROOT)
            self.assertTrue(list((pack / "arm_readiness.evidence").glob("*.json")))
            pinset = clone / PINSET.relative_to(ROOT)
            pinset.unlink()
            git(clone, "add", "-u", PINSET.relative_to(ROOT).as_posix())
            git(clone, "commit", "-qm", "remove committed histsem pinset")
            self.assertFalse(pinset.exists())

            self.assertIsNone(readiness._gate_receipt_histsem(pack))

    def test_synthetic_pack_without_pinset_stays_ordinary_with_legacy_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repo"
            repository.mkdir()
            git(repository, "init", "-q")
            git(repository, "config", "user.email", "tests@joulewise.invalid")
            git(repository, "config", "user.name", "JouleWise tests")
            pack = repository / "configs/campaigns/synthetic-pack"
            pack.mkdir(parents=True)
            (pack / "payload.json").write_text("{}", encoding="utf-8")
            evidence = {
                "schema_version": readiness.EVIDENCE_RECEIPT_SCHEMA,
                "evidence_id": "arm-t0-synthetic-v1",
                "kind": "T0",
                "status": "PASS",
                "issued_at_utc": "2026-08-20T00:00:00Z",
                "boot_session_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "valid_until_monotonic_ns": 10**30,
                "pack_sha256": "0" * 64,
                "head_commit": "a" * 40,
                "facts": [],
                "checks": [],
                "reason_codes": [],
                "assurance": readiness.ASSURANCE.copy(),
            }
            evidence_path = pack / "arm_readiness.evidence/arm-t0-synthetic-v1.json"
            evidence_path.parent.mkdir()
            evidence_path.write_bytes(render_json(evidence))
            readiness.validate_evidence_receipt(evidence)
            git(repository, "add", pack.relative_to(repository).as_posix())
            git(repository, "commit", "-qm", "synthetic pack with legacy T-0 receipt")

            self.assertIsNone(readiness._gate_receipt_histsem(pack))

    def test_fail_ugly_is_caught_at_arm_and_freeze_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            predecessor = root / "predecessor"
            (pack / "arm_readiness.evidence").mkdir(parents=True)
            predecessor.mkdir()
            (pack / "arm_readiness.evidence/evidence.json").write_text("{}")
            refusal = HistoricalSemanticsError(
                "histsem_history_unavailable", "missing historical blob"
            )
            with mock.patch.object(
                readiness, "_gate_receipt_histsem", side_effect=refusal
            ):
                arm = generate_arm_receipt(pack, {}, root / "custody")
                freeze = generate_freeze_receipt(
                    pack,
                    measurement_checkout=root,
                    predecessor_pack_root=predecessor,
                )
            self.assertEqual(arm["reason_codes"], ["histsem_history_unavailable"])
            self.assertEqual(freeze["reason_codes"], ["histsem_history_unavailable"])
            self.assertIsNone(arm["receipt_path"])
            self.assertIsNone(freeze["receipt_path"])
            self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())

    def test_temporary_workspace_allocation_failure_is_governed_at_arm_and_freeze_boundaries(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            successor = root / "successor"
            successor.mkdir()
            workspace_parent = root / "workspaces"
            workspace_parent.mkdir()
            failure = OSError("simulated histsem temporary-workspace exhaustion")
            with mock.patch.object(
                readiness.tempfile, "TemporaryDirectory", side_effect=failure
            ):
                arm = generate_arm_receipt(
                    REPRESENTATIVE_PACK, {}, root / "custody"
                )
                freeze = generate_freeze_receipt(
                    successor,
                    measurement_checkout=root,
                    predecessor_pack_root=REPRESENTATIVE_PACK,
                )
            self.assertEqual(list(workspace_parent.iterdir()), [])
        self.assertEqual(arm["status"], "REFUSE")
        self.assertEqual(arm["reason_codes"], ["histsem_history_unavailable"])
        self.assertIn("temporary workspace", arm["detail"])
        self.assertEqual(freeze["status"], "REFUSE")
        self.assertEqual(freeze["reason_codes"], ["histsem_history_unavailable"])
        self.assertIn("temporary workspace", freeze["detail"])

    def test_temporary_workspace_materialization_failure_is_governed_at_arm_and_freeze_boundaries(
        self,
    ) -> None:
        real_run = subprocess.run
        real_temporary_directory = tempfile.TemporaryDirectory
        with real_temporary_directory() as temporary:
            root = Path(temporary)
            successor = root / "successor"
            successor.mkdir()
            workspace_parent = root / "workspaces"
            workspace_parent.mkdir()
            created: list[Path] = []

            def tracking_directory(*args, **kwargs):
                kwargs.setdefault("dir", workspace_parent)
                workspace = real_temporary_directory(*args, **kwargs)
                created.append(Path(workspace.name))
                return workspace

            def fail_clone(command, *args, **kwargs):
                if tuple(command[:2]) == ("git", "clone"):
                    raise OSError("simulated historical clone failure")
                return real_run(command, *args, **kwargs)

            with (
                mock.patch.object(
                    readiness.tempfile,
                    "TemporaryDirectory",
                    side_effect=tracking_directory,
                ),
                mock.patch.object(
                    readiness.subprocess, "run", side_effect=fail_clone
                ),
            ):
                arm = generate_arm_receipt(
                    REPRESENTATIVE_PACK, {}, root / "materialization-custody"
                )
                freeze = generate_freeze_receipt(
                    successor,
                    measurement_checkout=root,
                    predecessor_pack_root=REPRESENTATIVE_PACK,
                )

            self.assertEqual(len(created), 2)
            self.assertTrue(all(not path.exists() for path in created))
            self.assertEqual(list(workspace_parent.iterdir()), [])
        self.assertEqual(arm["status"], "REFUSE")
        self.assertEqual(arm["reason_codes"], ["histsem_git_unavailable"])
        self.assertIn("materialize", arm["detail"])
        self.assertEqual(freeze["status"], "REFUSE")
        self.assertEqual(freeze["reason_codes"], ["histsem_git_unavailable"])
        self.assertIn("materialize", freeze["detail"])

    def test_temporary_workspace_cleanup_failure_is_governed_at_arm_and_freeze_boundaries(
        self,
    ) -> None:
        real_temporary_directory = tempfile.TemporaryDirectory
        with real_temporary_directory() as temporary:
            root = Path(temporary)
            successor = root / "successor"
            successor.mkdir()
            workspace_parent = root / "workspaces"
            workspace_parent.mkdir()
            created: list[Path] = []
            retained: list[tempfile.TemporaryDirectory[str]] = []
            nonempty_before_failure: list[bool] = []

            class CleanupFailure:
                def __init__(self, *args, **kwargs):
                    kwargs.setdefault("dir", workspace_parent)
                    self.inner = real_temporary_directory(*args, **kwargs)
                    retained.append(self.inner)
                    created.append(Path(self.inner.name))

                def __enter__(self):
                    return self.inner.__enter__()

                def __exit__(self, exc_type, exc_value, traceback):
                    scratch = Path(self.inner.name)
                    nonempty_before_failure.append(any(scratch.iterdir()))
                    # S13 refuter F1: a read-only child directory survives a
                    # plain ``shutil.rmtree(ignore_errors=True)`` fallback, so
                    # the leak regression plants one before failing.
                    blocked = scratch / "blocked-readonly"
                    blocked.mkdir()
                    (blocked / "ordinary").write_bytes(b"residue")
                    blocked.chmod(0o500)
                    raise OSError("simulated historical workspace cleanup failure")

            try:
                with mock.patch.object(
                    readiness.tempfile, "TemporaryDirectory", CleanupFailure
                ):
                    arm = generate_arm_receipt(
                        REPRESENTATIVE_PACK, {}, root / "cleanup-custody"
                    )
                    freeze = generate_freeze_receipt(
                        successor,
                        measurement_checkout=root,
                        predecessor_pack_root=REPRESENTATIVE_PACK,
                    )

                self.assertEqual(len(created), 2)
                self.assertEqual(nonempty_before_failure, [True, True])
                self.assertTrue(all(not path.exists() for path in created))
                self.assertEqual(list(workspace_parent.iterdir()), [])
            finally:
                for workspace in retained:
                    workspace.cleanup()
        self.assertEqual(arm["status"], "REFUSE")
        self.assertEqual(arm["reason_codes"], ["histsem_history_unavailable"])
        self.assertIn("temporary workspace", arm["detail"])
        self.assertEqual(freeze["status"], "REFUSE")
        self.assertEqual(freeze["reason_codes"], ["histsem_history_unavailable"])
        self.assertIn("temporary workspace", freeze["detail"])


class HistsemScratchTreeRemovalTests(unittest.TestCase):
    """The fallback removal never reaches outside the scratch tree."""

    def test_symlinked_root_is_unlinked_and_its_target_left_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / "outside"
            nested = outside / "nested"
            nested.mkdir(parents=True)
            (nested / "file").write_bytes(b"keep")
            (nested / "file").chmod(0o400)
            nested.chmod(0o500)
            outside.chmod(0o500)
            link = root / "scratch-link"
            link.symlink_to(outside, target_is_directory=True)
            try:
                readiness._histsem_remove_scratch_tree(link)
                self.assertFalse(link.is_symlink())
                self.assertEqual((nested / "file").read_bytes(), b"keep")
                self.assertEqual(stat.S_IMODE(outside.stat().st_mode), 0o500)
                self.assertEqual(stat.S_IMODE(nested.stat().st_mode), 0o500)
                self.assertEqual(stat.S_IMODE((nested / "file").stat().st_mode), 0o400)
            finally:
                outside.chmod(0o700)
                nested.chmod(0o700)


class SuccessorPinsetDigestConditionTests(unittest.TestCase):
    """D-151 condition 2 — the C -> S edge, exercised in both directions.

    Allowlist MEMBERSHIP makes the successor pinset path eligible for
    subtraction from the R1 changed set; it is not sufficient.  The bytes
    committed at the reviewed HEAD must also hash to the digest Ed recorded in
    the step-6 confirmation table's ``successor_pinset`` section.  These tests
    prove both arms: a matching digest subtracts, and every non-matching
    condition (no table, wrong digest, table naming another path, table absent
    from custody) leaves the path relevant and refuses DEPENDENCY_CHANGED_SET.
    """

    SUCCESSOR = readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1].as_posix()

    def build(self) -> tuple[Path, Path, dict, dict, dict]:
        from tests.test_arm_readiness_evidence import (
            content_source_and_receipt,
            lifecycle_registry,
            plan_tree,
        )

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name) / "repository"
        custody = Path(temporary.name) / "custody"
        repository.mkdir()
        custody.mkdir()
        git(repository, "init", "-q")
        git(repository, "config", "user.email", "test@example.invalid")
        git(repository, "config", "user.name", "S1 Finish Round")
        (repository / "dependency.txt").write_text("stable\n")
        (repository / "pack").mkdir()
        (repository / "pack/plan_tree.json").write_bytes(plan_tree(frozen=False))
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "derivation")
        derivation = git(repository, "rev-parse", "HEAD").stdout.strip()
        source, receipt = content_source_and_receipt(repository, derivation)
        registry = lifecycle_registry(allowlist=(self.SUCCESSOR,))
        registry["successor_policy"]["family_publication_first_generation"] = 4
        return repository, custody, registry, source, receipt

    def commit_successor(self, repository: Path, payload: bytes) -> tuple[str, str]:
        path = repository / self.SUCCESSOR
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        git(repository, "add", self.SUCCESSOR)
        git(repository, "commit", "-qm", "mint successor pinset")
        return (
            git(repository, "rev-parse", "HEAD").stdout.strip(),
            hashlib.sha256(payload).hexdigest(),
        )

    def table(self, custody: Path, name: str, **overrides: object) -> Path:
        from tests.test_family_marker import confirmation

        value = confirmation()
        value["successor_pinset"].update(overrides)
        return write_custody_json(custody, name, value)

    def gate(
        self,
        repository,
        receipt,
        source,
        registry,
        head,
        table_path,
        expected_digest=None,
    ):
        return readiness.validate_r1_evidence_lifecycle(
            repository,
            receipt,
            source,
            registry,
            current_head=head,
            expected_freshness_class="RE_DERIVABLE",
            plan_tree_path="pack/plan_tree.json",
            step6_confirmation_table=table_path,
            expected_confirmation_digest=expected_digest,
        )

    def test_confirmed_digest_subtracts_the_successor_path(self) -> None:
        repository, custody, registry, source, receipt = self.build()
        head, digest = self.commit_successor(repository, b'{"packs": []}\n')
        table_path = self.table(custody, "table.json", sha256=digest)
        expected_digest = hashlib.sha256(table_path.read_bytes()).hexdigest()
        changed = self.gate(
            repository,
            receipt,
            source,
            registry,
            head,
            table_path,
            expected_digest,
        )
        self.assertEqual(changed, (self.SUCCESSOR,))

    def test_unconfirmed_successor_bytes_refuse_dependency_changed_set(self) -> None:
        repository, custody, registry, source, receipt = self.build()
        head, digest = self.commit_successor(repository, b'{"packs": []}\n')
        confirmed = self.table(custody, "confirmed.json", sha256=digest)
        other_path = self.table(
            custody,
            "other-path.json",
            sha256=digest,
            path="configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json",
        )
        wrong_digest = self.table(custody, "wrong.json", sha256="c" * 64)
        malformed_transaction = self.table(custody, "malformed-transaction.json")
        malformed_value = json.loads(malformed_transaction.read_bytes())
        malformed_value["transaction_id"] = []
        malformed_raw = render_json(malformed_value)
        malformed_transaction.write_bytes(malformed_raw)
        malformed_transaction.with_name(
            f"{malformed_transaction.name}.sha256"
        ).write_bytes(
            gnu_sidecar(
                hashlib.sha256(malformed_raw).hexdigest(),
                malformed_transaction.name,
            )
        )
        noncanonical = custody / "noncanonical.json"
        noncanonical_raw = json.dumps(json.loads(confirmed.read_bytes())).encode() + b"\n"
        noncanonical.write_bytes(noncanonical_raw)
        noncanonical.with_name(f"{noncanonical.name}.sha256").write_bytes(
            gnu_sidecar(
                hashlib.sha256(noncanonical_raw).hexdigest(), noncanonical.name
            )
        )
        inconsistent_sidecar = self.table(
            custody, "inconsistent-sidecar.json", sha256=digest
        )
        inconsistent_sidecar.with_name(
            f"{inconsistent_sidecar.name}.sha256"
        ).write_bytes(gnu_sidecar("0" * 64, inconsistent_sidecar.name))
        cases = {
            "self-consistent ED/YES table without out-of-band digest": (
                confirmed,
                None,
                "no expected confirmation digest supplied",
            ),
            "malformed expected digest": (
                confirmed,
                "A" * 64,
                "supplied expected confirmation digest is malformed",
            ),
            "non-string expected digest": (
                confirmed,
                7,
                "supplied expected confirmation digest is malformed",
            ),
            "digest of other bytes": (
                confirmed,
                hashlib.sha256(other_path.read_bytes()).hexdigest(),
                "table bytes differ from the expected confirmation digest",
            ),
            "no table supplied": (
                None,
                hashlib.sha256(confirmed.read_bytes()).hexdigest(),
                "no step-6 confirmation table supplied",
            ),
            "table absent from custody": (
                custody / "absent.json",
                hashlib.sha256(confirmed.read_bytes()).hexdigest(),
                "custody artifact is absent",
            ),
            # The table schema itself pins the successor section to the
            # code-enumerated chain member, so a table naming a different path
            # is refused one layer earlier, as an inadmissible table.  The
            # helper's own path equality check stays as the second line of
            # defence for any future growth of the conditional class.
            "table names another path": (
                other_path,
                hashlib.sha256(other_path.read_bytes()).hexdigest(),
                "successor-pinset constants differ",
            ),
            "digest differs": (
                wrong_digest,
                hashlib.sha256(wrong_digest.read_bytes()).hexdigest(),
                "differ from Ed's confirmed step-6 digest",
            ),
            "non-string transaction id": (
                malformed_transaction,
                hashlib.sha256(malformed_transaction.read_bytes()).hexdigest(),
                "transaction_id must be a nonempty string",
            ),
            "noncanonical table": (
                noncanonical,
                hashlib.sha256(noncanonical_raw).hexdigest(),
                "custody JSON is noncanonical",
            ),
            "sidecar-inconsistent table": (
                inconsistent_sidecar,
                hashlib.sha256(inconsistent_sidecar.read_bytes()).hexdigest(),
                "custody artifact sidecar differs",
            ),
        }
        for label, (table_path, expected_digest, fragment) in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(readiness.EvidenceLifecycleError) as caught:
                    self.gate(
                        repository,
                        receipt,
                        source,
                        registry,
                        head,
                        table_path,
                        expected_digest,
                    )
                self.assertEqual(caught.exception.role, "DEPENDENCY_CHANGED_SET")
                self.assertIn(self.SUCCESSOR, str(caught.exception))
                self.assertIn(fragment, str(caught.exception))

        # A later mutation of the same path is refused against the same table:
        # the condition is on bytes at HEAD, never on the path alone.
        mutated_head, _digest = self.commit_successor(
            repository, b'{"packs": [], "mutated": true}\n'
        )
        with self.assertRaises(readiness.EvidenceLifecycleError) as caught:
            self.gate(
                repository,
                receipt,
                source,
                registry,
                mutated_head,
                confirmed,
                hashlib.sha256(confirmed.read_bytes()).hexdigest(),
            )
        self.assertEqual(caught.exception.role, "DEPENDENCY_CHANGED_SET")

    def test_build_lane_deferral_subtracts_without_a_table_and_ledgers_it(self) -> None:
        """S0-O2 cure, primary arm: the build lane subtracts and discloses.

        Same minted-successor fixture as the enforcing tests above, with the
        one difference that defines the marker-BUILD lane: no table, no
        out-of-band digest, and a deferral ledger in their place.  The path is
        subtracted from the changed set (the gate returns it as accounted for),
        and the ledger names it, so the marker built from this evaluation can
        say exactly which condition went unevaluated.
        """

        repository, custody, registry, source, receipt = self.build()
        head, _digest = self.commit_successor(repository, b'{"packs": []}\n')

        # Control: the same head with neither table nor deferral still refuses.
        with self.assertRaises(readiness.EvidenceLifecycleError) as caught:
            self.gate(repository, receipt, source, registry, head, None, None)
        self.assertEqual(caught.exception.role, "DEPENDENCY_CHANGED_SET")
        self.assertIn("no expected confirmation digest supplied", str(caught.exception))

        deferral = readiness.R1ConditionalDeferral()
        changed = readiness.validate_r1_evidence_lifecycle(
            repository,
            receipt,
            source,
            registry,
            current_head=head,
            expected_freshness_class="RE_DERIVABLE",
            plan_tree_path="pack/plan_tree.json",
            conditional_deferral=deferral,
        )
        self.assertEqual(changed, (self.SUCCESSOR,))
        self.assertEqual(deferral.deferred_paths, (self.SUCCESSOR,))
        self.assertEqual(
            deferral.disclosure(),
            {
                "gate": readiness.R1_DIGEST_CONDITIONAL_GATE_ID,
                "deferred_paths": [self.SUCCESSOR],
                "enforced_at_entry_points": [
                    "arm",
                    "freeze",
                    "verification",
                    "marker-replay",
                ],
            },
        )

    def test_deferral_and_confirmation_inputs_together_fail_closed(self) -> None:
        """The build lane and the enforcing lanes are exclusive, not additive.

        A caller that hands the gate both a deferral and a confirmation input
        has not said which lane it is in.  Rather than silently preferring one,
        the gate refuses with the changed-set role it already owns.
        """

        repository, custody, registry, source, receipt = self.build()
        head, digest = self.commit_successor(repository, b'{"packs": []}\n')
        table_path = self.table(custody, "table.json", sha256=digest)
        expected_digest = hashlib.sha256(table_path.read_bytes()).hexdigest()
        for label, table, expected in (
            ("table only", table_path, None),
            ("digest only", None, expected_digest),
            ("both", table_path, expected_digest),
        ):
            with self.subTest(case=label):
                with self.assertRaises(readiness.EvidenceLifecycleError) as caught:
                    readiness.validate_r1_evidence_lifecycle(
                        repository,
                        receipt,
                        source,
                        registry,
                        current_head=head,
                        expected_freshness_class="RE_DERIVABLE",
                        plan_tree_path="pack/plan_tree.json",
                        step6_confirmation_table=table,
                        expected_confirmation_digest=expected,
                        conditional_deferral=readiness.R1ConditionalDeferral(),
                    )
                self.assertEqual(caught.exception.role, "DEPENDENCY_CHANGED_SET")
                self.assertIn("exclusive", str(caught.exception))

    def test_ledger_refuses_paths_outside_the_conditional_class(self) -> None:
        """The disclosure field cannot be turned into a laundering channel."""

        deferral = readiness.R1ConditionalDeferral()
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            deferral.record("joulewise/arm_readiness.py")
        self.assertEqual(
            caught.exception.reason_code, "readiness_row_registry_mismatch"
        )
        self.assertEqual(deferral.deferred_paths, ())

    def test_conditional_class_is_exactly_the_successor_pinset(self) -> None:
        self.assertEqual(
            readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS,
            frozenset({self.SUCCESSOR}),
        )
        registry, _raw = readiness.load_registry(ROOT)
        allowlist = set(
            registry["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]
        )
        self.assertLessEqual(
            readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS, allowlist
        )


def load_v4_builder():
    """Import `scripts/build_v4_histsem_pinset.py` as a module.

    The import is local, not module-level: `docs/process_traces/2026-08-22-t20/
    s0-runsheet-r4.md` §0.3 pins this file's lines 32 and 138-165, and a new
    top-level import would silently drift all three.
    """

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_v4_histsem_pinset", ROOT / "scripts/build_v4_histsem_pinset.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PreAuthoringProjectionCustodyTests(unittest.TestCase):
    """The pre-authoring test must admit U11 projection custody.

    The ruled `_v4` transaction order (runsheet §3.2) commits each pack's
    identity-pin projection receipt BEFORE any evidence is authored, because
    the v2 issuance gate refuses to freeze a dirty tree.  The generic receipts
    authored at §3.4 therefore record a `derivation_commit` -- the historical
    coordinate the builder is handed -- whose pack tree ALREADY contains
    `identity_pin_projection.receipts/`.

    Uncured, that made the builder's two gates mutually unsatisfiable:

    * Gate A (the pre-authoring test) refused any historical head whose pack
      tree held ANY member of `_HISTSEM_CUSTODY_DIRECTORIES`, projection
      receipts included -- so it refused the derivation head.
    * Gate B requires the historical head to equal the coordinate the authored
      receipts recorded, which IS the derivation head -- so the only head Gate
      A accepted (the pre-projection bootstrap) failed Gate B.

    The cure narrows Gate A to AUTHORING custody.  These tests pin both
    directions: projection custody passes, authoring and freeze custody still
    refuse.
    """

    PACK_RELATIVE = "configs/campaigns/d117_synthetic_v4"

    def _repository(self, temporary: str, historical_custody: tuple[str, ...]) -> tuple[Path, Path, str, str]:
        """Build a repo whose historical coordinate carries `historical_custody`.

        Returns `(repository, pack_root, historical_head, current_head)`.
        History: bootstrap (plan tree only) -> historical (custody added) ->
        current (an allowed producer-contract modification), mirroring the
        runsheet's generate -> custody -> later-commit shape.
        """

        repository = Path(temporary)
        pack = repository / self.PACK_RELATIVE
        pack.mkdir(parents=True)
        # No `arm_attachments`: every cured run must reach -- and stop at --
        # the plan-tree gate that follows the pre-authoring test.
        (pack / "plan_tree.json").write_bytes(render_json({"arm_attachments": {}}))
        (pack / "producer_contract.json").write_bytes(render_json({"revision": 1}))
        git(repository, "init", "-q", "-b", "main")
        git(repository, "config", "user.name", "histsem test")
        git(repository, "config", "user.email", "histsem@invalid")
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "bootstrap")

        for directory in historical_custody:
            write_custody_json(pack / directory, "record-0001.json", {"kind": directory})
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "historical custody")
        historical_head = git(repository, "rev-parse", "HEAD").stdout.strip()

        (pack / "producer_contract.json").write_bytes(render_json({"revision": 2}))
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "later commit")
        current_head = git(repository, "rev-parse", "HEAD").stdout.strip()
        return repository, pack, historical_head, current_head

    def _row_error(self, historical_custody: tuple[str, ...]) -> str:
        builder = load_v4_builder()
        with tempfile.TemporaryDirectory() as temporary:
            repository, pack, historical, current = self._repository(
                temporary, historical_custody
            )
            with self.assertRaises(builder.BuildError) as caught:
                builder._row(repository, pack, self.PACK_RELATIVE, historical, current)
            return str(caught.exception)

    def test_projection_custody_at_the_historical_head_passes_the_gate(self) -> None:
        # RED before the cure: this raised "historical coordinate is not
        # pre-authoring".  GREEN after: execution reaches the NEXT gate.
        detail = self._row_error(("identity_pin_projection.receipts",))
        self.assertNotIn("pre-authoring", detail)
        self.assertEqual(detail, "plan tree has no pinned freeze receipt")

    def test_authoring_and_freeze_custody_still_refuse(self) -> None:
        for directory in (
            "arm_readiness.evidence",
            "arm_readiness.freeze.receipts",
            "arm_readiness.sources",
        ):
            with self.subTest(custody=directory):
                self.assertEqual(
                    self._row_error((directory,)),
                    "historical coordinate is not pre-authoring",
                )

    def test_projection_custody_does_not_mask_authoring_custody(self) -> None:
        self.assertEqual(
            self._row_error(
                ("identity_pin_projection.receipts", "arm_readiness.evidence")
            ),
            "historical coordinate is not pre-authoring",
        )

    def test_custody_frozenset_is_unchanged_and_authoring_is_its_subset(self) -> None:
        # The ruling forbids editing the frozenset itself: the post-authoring
        # DELTA envelope still admits projection bytes as a legitimate addition.
        self.assertEqual(
            readiness._HISTSEM_CUSTODY_DIRECTORIES,
            frozenset(
                {
                    "arm_readiness.evidence",
                    "arm_readiness.freeze.receipts",
                    "arm_readiness.sources",
                    "identity_pin_projection.receipts",
                }
            ),
        )
        self.assertEqual(
            readiness._HISTSEM_AUTHORING_CUSTODY_DIRECTORIES,
            readiness._HISTSEM_CUSTODY_DIRECTORIES
            - {"identity_pin_projection.receipts"},
        )
        self.assertFalse(
            readiness._histsem_tree_has_authoring_custody(
                ("identity_pin_projection.receipts/projection-0001.json",)
            )
        )
        for path in (
            "arm_readiness.evidence/evidence-acceptance-owner.json",
            "arm_readiness.freeze.receipts/freeze-0004.json",
            "arm_readiness.sources/source-0001.json",
        ):
            with self.subTest(path=path):
                self.assertTrue(
                    readiness._histsem_tree_has_authoring_custody((path,))
                )

    def test_both_pre_authoring_call_sites_share_one_predicate(self) -> None:
        """Neither gate may drift back to the full custody frozenset."""

        for relative in (
            "joulewise/arm_readiness.py",
            "scripts/build_v4_histsem_pinset.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            # Strip comments AND strings: the prose above each gate names both
            # constants deliberately, and only executable code is being pinned.
            code_only = "".join(
                token.string
                for token in tokenize.generate_tokens(io.StringIO(source).readline)
                if token.type not in (tokenize.COMMENT, tokenize.STRING)
            )
            with self.subTest(module=relative):
                self.assertIn("_histsem_tree_has_authoring_custody", code_only)
                # Executable uses of the FULL frozenset that must survive:
                # its own definition, the authoring-subset definition, and the
                # post-authoring delta envelope in `joulewise/` (3); the
                # builder keeps only its own delta envelope (1).  Any further
                # occurrence means a pre-authoring gate drifted back.
                self.assertEqual(
                    code_only.count("_HISTSEM_CUSTODY_DIRECTORIES"),
                    3 if relative.startswith("joulewise/") else 1,
                )

    def test_verifier_still_refuses_an_authoring_coordinate(self) -> None:
        """The verifier shares the gate, so it must keep the negative too.

        HEAD's representative pack carries `arm_readiness.evidence/`, so a row
        pinned at HEAD is a genuine post-authoring coordinate.  The row's
        historical digest is recomputed at that head so the digest check ahead
        of the gate passes and the gate itself is what refuses.
        """

        with tempfile.TemporaryDirectory() as temporary:
            pinset = Path(temporary) / "pinset.json"
            row_head = git(ROOT, "rev-parse", "HEAD").stdout.strip()
            digest = historical_pack_tree_sha256(
                ROOT, f"configs/campaigns/{REPRESENTATIVE_PACK.name}", row_head
            )
            write_pinset(
                pinset,
                lambda row: row.update(
                    {"head_commit": row_head, "historical_pack_sha256": digest}
                ),
            )
            rows = readiness._validate_histsem_pinset(
                readiness.parse_json_bytes(pinset.read_bytes(), require_canonical=True)
            )
            with self.assertRaises(HistoricalSemanticsError) as caught:
                verify_receipt_histsem_pack(REPRESENTATIVE_PACK, _pinset_rows=rows)
            self.assertEqual(
                caught.exception.reason_code,
                "histsem_historical_tree_not_pre_authoring",
            )


class PackAuthenticationRegenerationTests(unittest.TestCase):
    """Defect-shaped A94 regressions over the recorded generator coordinate."""

    def test_same_bytes_echo_under_a_foreign_identifier_is_refused_at_both_boundaries(
        self,
    ) -> None:
        pack_relative = "configs/campaigns/d117_floor_qwen25_1p5b_v1"
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
                check=True,
                capture_output=True,
            )
            git(repository, "config", "user.email", "histsem@invalid")
            git(repository, "config", "user.name", "histsem test")
            current_pack = repository / pack_relative
            source = json.loads(
                (
                    current_pack
                    / "arm_readiness.sources/pack-authentication.json"
                ).read_bytes()
            )
            historical_head = str(source["head_commit"])
            historical_digest = str(source["pack_sha256"])
            git(repository, "checkout", "-q", "--detach", historical_head)
            historical_pack = repository / pack_relative
            tree, _tree_raw = readiness._plan_tree(historical_pack)
            context = evidence_author._DerivationContext(
                pack_root=historical_pack,
                repository=repository.resolve(strict=True),
                tree=tree,
                pack_sha256=historical_digest,
                head_commit=historical_head,
            )
            generator_artifact, generator_raw = evidence_author._pinned_artifact(
                context,
                tree["generator"],
                kind="PACK_AUTHENTICATION",
                label="pack generator",
            )

            # The closed exception is not deny-everything: this exact reviewed
            # historical blob runs bare and proves its recorded coordinate.
            self.assertIn(
                hashlib.sha256(generator_raw).hexdigest(),
                evidence_author._REVIEWED_FLAGLESS_GENERATOR_SHA256_ALLOWLIST,
            )
            admitted = evidence_author._recorded_generator_check(
                context,
                generator_artifact["path"],
                generator_raw,
                kind="PACK_AUTHENTICATION",
                preserve_current_frozen_bytes=False,
            )
            self.assertEqual(admitted["derivation_mode"], "regenerated")
            self.assertFalse(admitted["preserve_flag_supported"])
            readiness._histsem_rederive_pack_authentication(
                repository, pack_relative, historical_head, historical_digest
            )

            # V7's shape: the generator reads the already-mutated committed
            # output under `saved`, re-emits it as its candidate, and compares
            # the bytes with themselves.  There is deliberately no identifier
            # containing `preserve_current_frozen_bytes`.
            foreign_raw = (
                "import sys\n"
                "from pathlib import Path\n"
                "if '--check' not in sys.argv:\n"
                "    raise SystemExit(2)\n"
                "saved = Path(__file__).with_name('plan_tree.json').read_bytes()\n"
                "candidate = saved\n"
                "if candidate != saved:\n"
                "    raise SystemExit(1)\n"
                "print('accepted existing bytes', len(candidate))\n"
            ).encode("utf-8")
            generator_path = repository / generator_artifact["path"]
            generator_path.write_bytes(foreign_raw)
            tree["generator"]["sha256"] = hashlib.sha256(foreign_raw).hexdigest()
            mutated_tree_raw = render_json(tree)
            (historical_pack / "plan_tree.json").write_bytes(mutated_tree_raw)
            (historical_pack / "plan_tree.sha256").write_bytes(
                gnu_sidecar(
                    hashlib.sha256(mutated_tree_raw).hexdigest(), "plan_tree.json"
                )
            )
            git(repository, "add", pack_relative)
            git(repository, "commit", "-qm", "install foreign same-bytes echo")
            foreign_head = git(repository, "rev-parse", "HEAD").stdout.strip()
            foreign_digest = committed_pack_tree_sha256(historical_pack)
            bare = subprocess.run(
                evidence_author._generator_command(str(generator_path)),
                cwd=repository,
                check=False,
                capture_output=True,
                env=evidence_author._generator_environment(),
            )
            self.assertEqual(bare.returncode, 0, bare.stderr.decode())

            foreign_tree, _tree_raw = readiness._plan_tree(historical_pack)
            foreign_context = evidence_author._DerivationContext(
                pack_root=historical_pack,
                repository=repository.resolve(strict=True),
                tree=foreign_tree,
                pack_sha256=foreign_digest,
                head_commit=foreign_head,
            )
            with self.assertRaises(evidence_author.EvidenceAuthoringError) as author:
                evidence_author._recorded_generator_check(
                    foreign_context,
                    foreign_tree["generator"]["path"],
                    foreign_raw,
                    kind="PACK_AUTHENTICATION",
                    preserve_current_frozen_bytes=False,
                )
            self.assertEqual(
                author.exception.reason_code,
                "evidence_author_pack_authentication_underivable",
            )
            self.assertIn("closed reviewed historical allowlist", str(author.exception))

            with self.assertRaises(HistoricalSemanticsError) as histsem:
                readiness._histsem_rederive_pack_authentication(
                    repository, pack_relative, foreign_head, foreign_digest
                )
            self.assertEqual(
                histsem.exception.reason_code, "histsem_historical_digest_mismatch"
            )
            self.assertIn("closed reviewed historical allowlist", str(histsem.exception))

    def _projected_histsem_fixture(self) -> tuple[Path, Path, dict[str, object]]:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        repository = repository.resolve(strict=True)
        pack = pack.resolve(strict=True)
        pack_relative = pack.relative_to(repository).as_posix()
        projection_receipt = json.loads(
            (pack / "identity_pin_projection.receipts/projection-0001.json").read_bytes()
        )
        projection_anchor = projection_receipt["pack"]["reviewed_git_commit"]
        git(repository, "checkout", projection_anchor, "--", pack_relative)
        shutil.rmtree(pack / "identity_pin_projection.receipts")
        predecessor_digest = "a" * 64
        generator_raw = (
            "import argparse\n"
            "import json\n"
            "import sys\n"
            "from pathlib import Path\n"
            f"CURRENT_FROZEN_RECEIPT_SHA256 = {predecessor_digest!r}\n"
            "pack = Path(__file__).resolve().parent\n"
            "tree = json.loads((pack / 'plan_tree.json').read_bytes())\n"
            "readiness = tree.get('arm_attachments', {}).get('arm_readiness', {})\n"
            "reference = readiness.get('freeze_receipt')\n"
            "current = reference.get('sha256') if isinstance(reference, dict) else None\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--check', action='store_true')\n"
            "parser.add_argument('--preserve-current-frozen-bytes', "
            "action=argparse.BooleanOptionalAction, default=None)\n"
            "args = parser.parse_args()\n"
            "preserve = (current == CURRENT_FROZEN_RECEIPT_SHA256) "
            "if args.preserve_current_frozen_bytes is None "
            "else args.preserve_current_frozen_bytes\n"
            "if not args.check:\n"
            "    raise SystemExit(2)\n"
            "if preserve:\n"
            "    print('synthetic preserved pack check passed')\n"
            "elif (pack / 'identity_pin_projection.receipts').exists():\n"
            "    print('projected current tree cannot regenerate bare', file=sys.stderr)\n"
            "    raise SystemExit(1)\n"
            "else:\n"
            "    print('synthetic regenerated pack check passed')\n"
        ).encode("utf-8")
        (pack / "generate_configs.py").write_bytes(generator_raw)
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        tree["generator"]["sha256"] = hashlib.sha256(generator_raw).hexdigest()
        tree_raw = render_json(tree)
        (pack / "plan_tree.json").write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
        )
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "install stale-constant projected generator")
        commit_u11_projection(repository, pack, ("alpha",))
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        historical_head = git(repository, "rev-parse", "HEAD").stdout.strip()
        historical_digest = committed_pack_tree_sha256(pack)
        with (
            mock.patch.object(
                readiness,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
            mock.patch.object(
                readiness, "_utc_now", return_value="2026-08-12T12:00:00Z"
            ),
            mock.patch.object(evidence_author.time, "monotonic_ns", return_value=100),
            mock.patch.object(
                evidence_author,
                "_execute_unittest_suite_subprocess",
                side_effect=lambda repo, test_ids: passing_suites(repo, test_ids),
            ),
        ):
            authored = evidence_author.author_arm_readiness_evidence(pack)
            self.assertEqual(authored["status"], "PASS")
            git(repository, "add", "-A")
            git(repository, "commit", "-qm", "author projected evidence")
            frozen = generate_freeze_receipt(pack, measurement_checkout=repository)
            self.assertEqual(frozen["status"], "PASS", frozen)
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "freeze projected evidence")

        tree_raw = (pack / "plan_tree.json").read_bytes()
        tree = json.loads(tree_raw)
        freeze_reference = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
        freeze = json.loads((pack / freeze_reference["path"]).read_bytes())
        pack_receipts = [
            dict(item)
            for item in freeze["evidence"]
            if item["namespace"] == "PACK"
            and item["schema_version"] in readiness.GENERIC_EVIDENCE_RECEIPT_SCHEMAS
        ]
        row: dict[str, object] = {
            "pack_id": pack.name,
            "pack_path": pack_relative,
            "head_commit": historical_head,
            "historical_pack_sha256": historical_digest,
            "current_pack_sha256": committed_pack_tree_sha256(pack),
            "freeze_receipt": dict(freeze_reference),
            "plan_tree_sha256": hashlib.sha256(tree_raw).hexdigest(),
            "plan_sha256": freeze["pack_identity"]["plan_sha256"],
            "post_authoring_delta": readiness._histsem_delta(
                repository, pack_relative, historical_head
            ),
            "receipt_count": len(pack_receipts),
            "receipts": pack_receipts,
            "published_anchor": "synthetic-local-history",
        }
        return repository, pack, row

    def test_recorded_anchor_replay_refuses_historical_science_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
                check=True,
                capture_output=True,
            )
            git(repository, "config", "user.email", "histsem@invalid")
            git(repository, "config", "user.name", "histsem test")
            current_pack = repository / REPRESENTATIVE_PACK.relative_to(ROOT)
            receipt = next(
                json.loads(path.read_bytes())
                for path in (current_pack / "arm_readiness.evidence").glob("*.json")
                if json.loads(path.read_bytes())["kind"] == "PACK_AUTHENTICATION"
            )
            historical_head = str(receipt["head_commit"])
            git(repository, "checkout", "-q", "--detach", historical_head)
            historical_pack = repository / REPRESENTATIVE_PACK.relative_to(ROOT)
            science_row = (
                historical_pack
                / "01_phase_decode_absolute/d117f15-df-ph-decode-abs-r01.json"
            )
            science_row.write_bytes(science_row.read_bytes() + b"\n")
            git(repository, "add", science_row.relative_to(repository).as_posix())
            git(repository, "commit", "-qm", "mutate historical science row")
            mutated_head = git(repository, "rev-parse", "HEAD").stdout.strip()
            mutated_digest = committed_pack_tree_sha256(historical_pack)

            with self.assertRaises(HistoricalSemanticsError) as caught:
                readiness._histsem_rederive_pack_authentication(
                    repository,
                    REPRESENTATIVE_PACK.relative_to(ROOT).as_posix(),
                    mutated_head,
                    mutated_digest,
                )
            self.assertEqual(
                caught.exception.reason_code, "histsem_historical_digest_mismatch"
            )
            self.assertIn("generator", str(caught.exception))

    def test_recorded_anchor_replay_refuses_unresolvable_or_off_lineage_commit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            subprocess.run(
                ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
                check=True,
                capture_output=True,
            )
            git(repository, "config", "user.email", "histsem@invalid")
            git(repository, "config", "user.name", "histsem test")
            pack = repository / REPRESENTATIVE_PACK.relative_to(ROOT)
            pinset = json.loads(PINSET.read_bytes())
            row = copy.deepcopy(
                next(item for item in pinset["packs"] if item["pack_id"] == pack.name)
            )
            absent_head = "b" * 40

            freeze_path = pack / row["freeze_receipt"]["path"]
            freeze = json.loads(freeze_path.read_bytes())
            pack_auth_item = next(
                item
                for item in freeze["evidence"]
                if item["receipt_kind"] == "PACK_AUTHENTICATION"
            )
            receipt_path = pack / pack_auth_item["path"]
            receipt = json.loads(receipt_path.read_bytes())
            source_path = pack / next(
                fact["source_path"]
                for fact in receipt["facts"]
                if fact["fact_id"] == "desk.current_pack.v1"
            )
            source = json.loads(source_path.read_bytes())
            source["head_commit"] = absent_head
            source_raw = render_json(source)
            source_path.write_bytes(source_raw)
            source_digest = hashlib.sha256(source_raw).hexdigest()
            for fact in receipt["facts"]:
                if fact["fact_id"] == "desk.current_pack.v1":
                    fact["source_sha256"] = source_digest
            receipt["head_commit"] = absent_head
            receipt_raw = render_json(receipt)
            receipt_path.write_bytes(receipt_raw)
            receipt_digest = hashlib.sha256(receipt_raw).hexdigest()
            receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
                gnu_sidecar(receipt_digest, receipt_path.name)
            )
            pack_auth_item["sha256"] = receipt_digest
            freeze_raw = render_json(freeze)
            freeze_path.write_bytes(freeze_raw)
            freeze_digest = hashlib.sha256(freeze_raw).hexdigest()
            freeze_path.with_name(f"{freeze_path.name}.sha256").write_bytes(
                gnu_sidecar(freeze_digest, freeze_path.name)
            )
            tree_path = pack / "plan_tree.json"
            tree = json.loads(tree_path.read_bytes())
            tree["arm_attachments"]["arm_readiness"]["freeze_receipt"][
                "sha256"
            ] = freeze_digest
            tree_raw = readiness._render_plan_tree(tree)
            tree_path.write_bytes(tree_raw)
            (pack / "plan_tree.sha256").write_bytes(
                gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
            )
            git(repository, "add", pack.relative_to(repository).as_posix())
            git(repository, "commit", "-qm", "coherently replace recorded anchor")

            row.update(
                {
                    "head_commit": absent_head,
                    "current_pack_sha256": committed_pack_tree_sha256(pack),
                    "freeze_receipt": copy.deepcopy(
                        tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
                    ),
                    "plan_tree_sha256": hashlib.sha256(tree_raw).hexdigest(),
                    "receipt_count": len(
                        [
                            item
                            for item in freeze["evidence"]
                            if item["namespace"] == "PACK"
                            and item["schema_version"]
                            in readiness.GENERIC_EVIDENCE_RECEIPT_SCHEMAS
                        ]
                    ),
                    "receipts": [
                        copy.deepcopy(item)
                        for item in freeze["evidence"]
                        if item["namespace"] == "PACK"
                        and item["schema_version"]
                        in readiness.GENERIC_EVIDENCE_RECEIPT_SCHEMAS
                    ],
                }
            )
            with self.assertRaises(HistoricalSemanticsError) as absent:
                verify_receipt_histsem_pack(pack, _pinset_rows=(row,))
            self.assertEqual(absent.exception.reason_code, "histsem_commit_unresolvable")

        original = readiness._histsem_git

        def off_lineage(repository: Path, *args: str):
            if args[:2] == ("merge-base", "--is-ancestor") and args[-1] == "HEAD":
                return 1, b"", b""
            return original(repository, *args)

        with mock.patch.object(readiness, "_histsem_git", side_effect=off_lineage):
            with self.assertRaises(HistoricalSemanticsError) as off_lineage_error:
                verify_receipt_histsem_pack(REPRESENTATIVE_PACK)
        self.assertEqual(
            off_lineage_error.exception.reason_code, "histsem_commit_off_lineage"
        )

    def test_projected_pack_pack_auth_receipt_survives_histsem_regeneration_gate(
        self,
    ) -> None:
        _repository, pack, row = self._projected_histsem_fixture()
        with mock.patch.object(
            readiness,
            "_histsem_rederive_pack_authentication",
            wraps=readiness._histsem_rederive_pack_authentication,
        ) as regeneration:
            result = verify_receipt_histsem_pack(pack, _pinset_rows=(row,))
        self.assertEqual(result["status"], "PASS")
        regeneration.assert_called_once()
        pack_authentication = next(
            json.loads((pack / item["path"]).read_bytes())
            for item in row["receipts"]
            if item["receipt_kind"] == "PACK_AUTHENTICATION"
        )
        self.assertEqual(
            pack_authentication.get(
                "derivation_commit", pack_authentication.get("head_commit")
            ),
            row["head_commit"],
        )

    def test_v4_prefreeze_authors_then_postfreeze_bare_refuses_without_invalidating_recorded_authentication(
        self,
    ) -> None:
        repository, pack, row = self._projected_histsem_fixture()
        bare = subprocess.run(
            (
                sys.executable,
                "-I",
                "-B",
                str(pack / "generate_configs.py"),
                "--check",
            ),
            cwd=repository,
            check=False,
            capture_output=True,
        )
        self.assertNotEqual(bare.returncode, 0, bare.stdout.decode(errors="replace"))
        with mock.patch.object(
            readiness,
            "_histsem_rederive_pack_authentication",
            wraps=readiness._histsem_rederive_pack_authentication,
        ) as regeneration:
            self.assertEqual(
                verify_receipt_histsem_pack(pack, _pinset_rows=(row,))["status"],
                "PASS",
            )
        regeneration.assert_called_once()



if __name__ == "__main__":
    unittest.main()
