from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import subprocess
import tempfile
import tokenize
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
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


ROOT = Path(__file__).resolve().parents[1]
PINSET = ROOT / "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"
PINSET_SHA256 = "d81515505d677c2ca045238e721c87eae8f38439a89a5377e58fa9064eaf2f21"
REPRESENTATIVE_PACK = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v3"


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

    def test_differential_self_test_all_nine_packs(self) -> None:
        value = json.loads(PINSET.read_bytes())
        for row in value["packs"]:
            with self.subTest(pack=row["pack_id"]):
                pack = ROOT / row["pack_path"]
                self.assertEqual(
                    historical_pack_tree_sha256(ROOT, row["pack_path"], "HEAD"),
                    committed_pack_tree_sha256(pack),
                )

    def test_full_corpus_verifies_two_coordinates_and_facts(self) -> None:
        result = verify_all_receipt_histsem(ROOT, require_published=True)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["pack_count"], 9)
        self.assertEqual(result["receipt_count"], 99)
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
                    pack, predecessor_pack_root=predecessor
                )
            self.assertEqual(arm["reason_codes"], ["histsem_history_unavailable"])
            self.assertEqual(freeze["reason_codes"], ["histsem_history_unavailable"])
            self.assertIsNone(arm["receipt_path"])
            self.assertIsNone(freeze["receipt_path"])
            self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())


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
    """Import `scripts/build_v4_histsem_pinset.py` as a module."""

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



if __name__ == "__main__":
    unittest.main()
