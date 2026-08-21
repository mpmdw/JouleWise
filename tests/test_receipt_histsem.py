from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
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


def write_pinset(path: Path, mutate: callable) -> Path:
    value = json.loads(PINSET.read_bytes())
    row = next(item for item in value["packs"] if item["pack_id"] == REPRESENTATIVE_PACK.name)
    mutate(row)
    path.write_bytes(render_json(value))
    return path


class ReceiptHistoricalSemanticsTests(unittest.TestCase):
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
        self.assertEqual(payload["reason_codes"], ["histsem_pinset_absent"])
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
                    with self.assertRaises(HistoricalSemanticsError) as caught:
                        verify_receipt_histsem_pack(
                            REPRESENTATIVE_PACK, pinset_path=pinset
                        )
                    self.assertEqual(caught.exception.reason_code, expected)

            with self.assertRaises(HistoricalSemanticsError) as caught:
                verify_receipt_histsem_pack(
                    REPRESENTATIVE_PACK, pinset_path=root / "absent.json"
                )
            self.assertEqual(caught.exception.reason_code, "histsem_pinset_absent")

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
            # worktree pinset cannot turn the gate off.
            (clone / PINSET.relative_to(ROOT)).unlink()
            with self.assertRaises(HistoricalSemanticsError) as absent:
                readiness._gate_receipt_histsem(pack)
            self.assertEqual(absent.exception.reason_code, "histsem_pinset_absent")

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

    def test_committed_pinset_deletion_refuses_before_arm_custody(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
