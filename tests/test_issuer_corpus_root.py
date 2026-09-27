"""Synthetic custody-parent issuance and value-blind member authentication."""

from __future__ import annotations

from contextlib import redirect_stdout
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from scripts import issue_calibration_acceptance_generation as issuer
from tests.fixtures.epoch_bootstrap.build import Slot, build_derivation_ledger


ROOT = Path(__file__).resolve().parents[1]
SESSION_A = "plan-w1"
SESSION_B = "plan-w2"


class IssuerCorpusRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name).resolve()
        cls.parent = cls.base / "night-custody"
        cls.repo = cls.base / "repo"
        registration = ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
        cls.prereg = cls.base / "historical-registration.md"
        cls.prereg.write_text(
            registration.read_text(encoding="utf-8").split("# Revision 5 (", 1)[0],
            encoding="utf-8",
        )
        cls.prereg_sha = hashlib.sha256(cls.prereg.read_bytes()).hexdigest()
        sealed = registration.read_text(encoding="utf-8")
        sealed = sealed.replace("<PR-L-MERGE-SHA>", "a" * 40)
        sealed = sealed.replace("<TEMPLATE-SHA256:night>", "b" * 64)
        sealed = sealed.replace("<TEMPLATE-SHA256:probe>", "c" * 64)
        cls.revision_five_prereg = cls.base / "sealed-revision-5.md"
        cls.revision_five_prereg.write_text(sealed, encoding="utf-8")
        cls.revision_five_sha = hashlib.sha256(cls.revision_five_prereg.read_bytes()).hexdigest()
        values = [Slot(str(Decimal("0.0200") + Decimal("0.0006") * i))
                  for i in range(20)]
        cls.fixture = build_derivation_ledger(
            cls.repo, values[:10], session_id=SESSION_A,
            second_session=(SESSION_B, values[10:]), custody_parent=cls.parent,
        )

    def setUp(self) -> None:
        self.out = self.base / f"{self._testMethodName}.json"
        self.out.unlink(missing_ok=True)

    def prepare(self, corpus_root: Path | None = None, *,
                fixture: dict[str, Path] | None = None,
                revision_five: bool = False) -> tuple[int, str]:
        self.out.unlink(missing_ok=True)
        fixture = self.fixture if fixture is None else fixture
        prereg = self.revision_five_prereg if revision_five else self.prereg
        prereg_sha = self.revision_five_sha if revision_five else self.prereg_sha
        argv = [
            "prepare-candidate", "--ledger", str(fixture["ledger"]),
            "--head-pin", str(fixture["pin"]), "--repo-root", str(fixture["root"]),
            "--preregistration", str(prereg),
            "--preregistration-sha256", prereg_sha,
            "--predecessor-acceptance",
            str(issuer.DEFAULT_ACCEPTANCE_BOUND_PATH if revision_five else
                ROOT / "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"),
            "--registration-session-id", SESSION_A,
            "--registration-session-id", SESSION_B,
            "--nights-ruling", "synthetic two-session registration",
            "--slot-count-ruling", "synthetic ten-slot session",
            "--d125-ruling", "synthetic D-125 reference",
            "--out", str(self.out),
        ]
        if corpus_root is not None:
            argv += ["--corpus-root", str(corpus_root)]
        stream = io.StringIO()
        with redirect_stdout(stream):
            if revision_five:
                with mock.patch.object(issuer, "_registered_dispositions", return_value={}):
                    code = issuer.main(argv)
            else:
                with mock.patch.object(issuer, "REVISION_FIVE_EPOCH", {}):
                    code = issuer.main(argv)
        return code, stream.getvalue()

    def verify(self, parent: Path, artifact: Path | None = None) -> tuple[int, str]:
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = issuer.main([
                "verify-members", "--artifact", str(artifact or self.out),
                "--corpus-root", str(parent),
            ])
        return code, stream.getvalue()

    def first(self) -> tuple[str, Path]:
        member_id = f"{SESSION_A}-d01"
        return member_id, self.parent / SESSION_A / "runs/instrument_validation" / member_id

    def test_two_sibling_roots_issue_and_repo_root_stays_authoritative(self) -> None:
        code, text = self.prepare(self.parent)
        self.assertEqual(code, 0, text)
        payload = json.loads(self.out.read_text(encoding="utf-8"))
        members = payload["derivation_corpus"]["members"]
        self.assertEqual(len(members), 20)
        self.assertEqual({p["source_directory"].split("/")[0] for p in members},
                         {SESSION_A, SESSION_B})
        self.assertTrue(all(p["source_directory"].endswith(p["member_id"])
                            for p in members))
        self.assertNotIn(str(self.parent), self.out.read_text(encoding="utf-8"))
        self.assertIn("verify-members --artifact <file> --corpus-root <dir>",
                      payload["derivation_notes"]["member_custody"])
        # The corpus parent contains no ledger, pin, battery module or .git.
        self.assertFalse((self.parent / ".git").exists())
        self.assertFalse((self.parent / "runs/calibration_observation_ledger.jsonl").exists())
        self.assertEqual(self.verify(self.parent)[0], 0)

    def test_revision_five_uses_run_checkout_for_battery_authentication(self) -> None:
        repo = self.base / "revision-five-repo"
        parent = self.base / "revision-five-custody"
        values = [Slot(str(Decimal("0.0300") + Decimal("0.0010") * i), native_frames=True)
                  for i in range(12)]
        fixture = build_derivation_ledger(
            repo, values, session_id=SESSION_A,
            second_session=(SESSION_B, values), custody_parent=parent,
            verdict_records=True, preregistration_sha256=self.revision_five_sha,
        )
        for absent in (parent / ".git", parent / "runs/calibration_observation_ledger.jsonl",
                       parent / "configs/calibration/calibration_ledger_head.json",
                       parent / "configs/calibration/battery_float_verdicts"):
            self.assertFalse(absent.exists(), absent)
        for owned in (repo / ".git", fixture["ledger"], fixture["pin"],
                      repo / "configs/calibration/battery_float_verdicts"
                      / f"{SESSION_A}.json"):
            self.assertTrue(owned.exists(), owned)
        code, report = self.prepare(parent, fixture=fixture, revision_five=True)
        self.assertEqual(code, 0, report)
        self.assertEqual(len(json.loads(self.out.read_text())["derivation_corpus"]["members"]), 24)

        original = issuer.authenticate_battery_epoch
        def route_battery_to_corpus(*args: object, **kwargs: object) -> object:
            kwargs["repo_root"] = parent
            return original(*args, **kwargs)

        with mock.patch.object(issuer, "authenticate_battery_epoch",
                               side_effect=route_battery_to_corpus):
            code, report = self.prepare(parent, fixture=fixture, revision_five=True)
        self.assertEqual(code, 3, report)
        self.assertFalse(self.out.exists())

    def test_same_ledger_flag_equivalence(self) -> None:
        repo = self.base / "same-ledger-repo"
        values = [Slot(str(Decimal("0.0200") + Decimal("0.0006") * i))
                  for i in range(20)]
        parent = repo / "night-custody"
        fixture = build_derivation_ledger(
            repo, values[:10], session_id=SESSION_A,
            second_session=(SESSION_B, values[10:]), custody_parent=parent,
        )
        code, report = self.prepare(fixture=fixture)
        self.assertEqual(code, 0, report)
        absent = json.loads(self.out.read_text())
        code, report = self.prepare(parent, fixture=fixture)
        self.assertEqual(code, 0, report)
        present = json.loads(self.out.read_text())
        for payload in (absent, present):
            self.assertEqual(len(payload["derivation_corpus"]["members"]), 20)
        self.assertEqual(
            [m["member_id"] for m in absent["derivation_corpus"]["members"]],
            [m["member_id"] for m in present["derivation_corpus"]["members"]],
        )
        for old, new in zip(absent["derivation_corpus"]["members"],
                            present["derivation_corpus"]["members"], strict=True):
            self.assertEqual(old["source_directory"], f"night-custody/{new['source_directory']}")
        self.assertEqual(absent["derivation_input_sha256"], present["derivation_input_sha256"])
        self.assertEqual(absent["ledger_cutoff"], present["ledger_cutoff"])
        self.assertNotEqual(absent["derivation_sha256"], present["derivation_sha256"])
        absent.pop("derivation_sha256")
        present.pop("derivation_sha256")
        for old, new in zip(absent["derivation_corpus"]["members"],
                            present["derivation_corpus"]["members"], strict=True):
            old["source_directory"] = new["source_directory"]
        absent["derivation_notes"].pop("member_custody", None)
        present["derivation_notes"].pop("member_custody", None)
        self.assertEqual(absent, present)

    def test_undeclared_root_and_wrong_roots_refuse_whole_run(self) -> None:
        for parent, reason in ((None, "lies outside the repository"),
                               (self.base, "exactly four parts"),
                               (self.parent / SESSION_A, "exactly four parts"),
                               (self.base / "absent", "declared corpus root")):
            with self.subTest(parent=parent):
                code, text = self.prepare(parent)
                self.assertEqual(code, 3, text)
                self.assertIn(reason, text)
                self.assertFalse(self.out.exists())

    def test_path_refusal_matrix(self) -> None:
        member_id, directory = self.first()
        # Read only path names and existence. The directory need not be parsed.
        cases = [
            (str(directory).replace("/runs/", "/runs/../runs/"), "canonical"),
            (str(directory) + "/", "canonical"),
            (str(directory).replace("/runs/", "//runs/"), "canonical"),
            (str(directory.parent), "exactly four parts"),
        ]
        for locator, reason in cases:
            with self.subTest(locator=locator):
                with self.assertRaisesRegex(issuer.PrepareRefusal, reason):
                    issuer._corpus_relative_custody(locator, member_id, SESSION_A, self.parent)
        with self.assertRaisesRegex(issuer.PrepareRefusal, "canonical"):
            issuer._corpus_relative_custody(str(directory.relative_to(self.parent)), member_id,
                                            SESSION_A, self.parent)
        with self.assertRaisesRegex(issuer.PrepareRefusal, "session id"):
            issuer._corpus_relative_custody(str(directory), member_id, SESSION_B, self.parent)
        with self.assertRaisesRegex(issuer.PrepareRefusal, "capture id"):
            issuer._corpus_relative_custody(str(directory), "another-capture", SESSION_A,
                                            self.parent)
        with self.assertRaisesRegex(issuer.PrepareRefusal, "outside"):
            issuer._corpus_relative_custody(str(directory), member_id, SESSION_A,
                                            self.base / "repo")

    def test_exact_four_part_shape_has_one_corpus_root(self) -> None:
        member_id, directory = self.first()
        nested = self.parent / SESSION_A / SESSION_A / "runs/instrument_validation" / member_id
        shutil.copytree(directory, nested)
        self.addCleanup(shutil.rmtree, nested)
        self.assertEqual(
            issuer._corpus_relative_custody(str(nested), member_id, SESSION_A,
                                            self.parent / SESSION_A),
            f"{SESSION_A}/runs/instrument_validation/{member_id}",
        )
        with self.assertRaisesRegex(issuer.PrepareRefusal, "exactly four parts"):
            issuer._corpus_relative_custody(str(nested), member_id, SESSION_A, self.parent)
        malformed = (
            self.parent / SESSION_A / "runs" / member_id,
            self.parent / SESSION_A / "runs/instrument_validation/extra" / member_id,
            self.parent / SESSION_A / "other/instrument_validation" / member_id,
        )
        for target, reason in zip(malformed,
                                  ("exactly four parts", "exactly four parts",
                                   "runs/instrument_validation"), strict=True):
            shutil.copytree(directory, target)
            self.addCleanup(shutil.rmtree, target)
            with self.subTest(target=target), self.assertRaisesRegex(
                    issuer.PrepareRefusal, reason):
                issuer._corpus_relative_custody(str(target), member_id, SESSION_A,
                                                self.parent)

    def test_duplicate_valid_attempt_refuses_before_value_read(self) -> None:
        snapshot = issuer.load_calibration_ledger_snapshot(
            self.fixture["ledger"], self.fixture["pin"], require_committed_pin=True,
            verify_custody=False, mode="read_replay", repo_root=self.repo,
        )
        row = issuer._registration_observations(snapshot, (SESSION_A,))[0]
        with mock.patch.object(issuer, "_read_member_evidence", side_effect=AssertionError(
                "value parser reached")):
            with self.assertRaisesRegex(issuer.PrepareRefusal, "duplicate valid attempt id"):
                issuer._select_members([row, row], self.repo, Decimal("1"), self.parent)

    def test_symlinked_locator_and_primary_file_refuse_before_value_read(self) -> None:
        member_id, directory = self.first()
        link = self.parent / SESSION_A / "runs/instrument_validation/alias"
        link.symlink_to(directory, target_is_directory=True)
        self.addCleanup(link.unlink)
        with self.assertRaisesRegex(issuer.PrepareRefusal, "symlink"):
            issuer._corpus_relative_custody(str(link), "alias", SESSION_A, self.parent)
        code, text = self.prepare(self.parent)
        self.assertEqual(code, 0, text)
        evidence = directory / "instrument_evidence.json"
        outside = self.base / "outside-evidence.json"
        shutil.copyfile(evidence, outside)
        backup = self.base / "evidence-backup.json"
        evidence.rename(backup)
        evidence.symlink_to(outside)
        self.addCleanup(lambda: (evidence.unlink(), backup.rename(evidence)))
        with mock.patch.object(issuer, "_read_member_evidence", side_effect=AssertionError(
            "value parser reached")):
            refused, reason = self.prepare(self.parent)
        self.assertEqual(refused, 3, reason)
        self.assertIn("primary file instrument_evidence.json", reason)
        self.assertFalse(self.out.exists())

    def test_missing_primary_refuses_whole_run_before_value_read(self) -> None:
        _, directory = self.first()
        primary = directory / "manifest.json"
        backup = self.base / "manifest-backup.json"
        primary.rename(backup)
        self.addCleanup(lambda: backup.rename(primary))
        with mock.patch.object(issuer, "_read_member_evidence", side_effect=AssertionError(
            "value parser reached")):
            code, text = self.prepare(self.parent)
        self.assertEqual(code, 3, text)
        self.assertIn("manifest.json", text)
        self.assertFalse(self.out.exists())

    def test_verifier_relocation_mutation_and_stored_path_refusals(self) -> None:
        code, text = self.prepare(self.parent)
        self.assertEqual(code, 0, text)
        original = self.out.read_bytes()
        relocated = self.base / "restored"
        shutil.copytree(self.parent, relocated)
        self.addCleanup(lambda: shutil.rmtree(relocated))
        code, report = self.verify(relocated)
        self.assertEqual(code, 0, report)
        self.assertEqual(report.count(": PASS"), 20)
        self.assertEqual(original, self.out.read_bytes())
        payload = json.loads(original)
        first = payload["derivation_corpus"]["members"][0]
        original_source = first["source_directory"]
        wrong_session = (relocated / SESSION_B / "runs/instrument_validation"
                         / first["member_id"])
        shutil.copytree(relocated / original_source, wrong_session)
        for path in (str(relocated / first["source_directory"]),
                     SESSION_A + "/../" + first["source_directory"],
                     first["source_directory"] + "/",
                     first["source_directory"].replace("/runs/", "//runs/"),
                     first["source_directory"].replace(SESSION_A + "/runs",
                                                        SESSION_B + "/runs")):
            with self.subTest(path=path):
                first["source_directory"] = path
                self.out.write_text(json.dumps(payload), encoding="utf-8")
                code, report = self.verify(relocated)
                self.assertEqual(code, 3, report)
                self.assertEqual(report.count(": FAIL"), 1)
                self.assertEqual(report.count(": PASS"), 19)
        self.out.write_bytes(original)
        primary = relocated / original_source / "manifest.json"
        raw = primary.read_bytes()
        primary.write_bytes(bytes((raw[0] ^ 1,)) + raw[1:])
        code, report = self.verify(relocated)
        self.assertEqual(code, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)
        self.assertEqual(report.count(": PASS"), 19)
        self.assertEqual(self.verify(self.repo)[0], 3)

    def test_verifier_refuses_symlink_escapes_and_wrong_capture(self) -> None:
        code, text = self.prepare(self.parent)
        self.assertEqual(code, 0, text)
        payload = json.loads(self.out.read_text(encoding="utf-8"))
        first = payload["derivation_corpus"]["members"][0]
        member_id = first["member_id"]
        copied = self.base / "verify-copy"
        shutil.copytree(self.parent, copied)
        self.addCleanup(lambda: shutil.rmtree(copied))
        directory = copied / first["source_directory"]
        outside = self.base / "outside-capture" / member_id
        shutil.copytree(directory, outside)
        self.addCleanup(lambda: shutil.rmtree(outside.parent))
        shutil.rmtree(directory)
        directory.symlink_to(outside, target_is_directory=True)
        result, report = self.verify(copied)
        self.assertEqual(result, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)
        directory.unlink()
        shutil.copytree(outside, directory)
        evidence = directory / "instrument_evidence.json"
        evidence.unlink()
        evidence.symlink_to(outside / "instrument_evidence.json")
        result, report = self.verify(copied)
        self.assertEqual(result, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)
        evidence.unlink()
        shutil.copyfile(outside / "instrument_evidence.json", evidence)
        wrong = directory.with_name("wrong-capture")
        directory.rename(wrong)
        first["source_directory"] = first["source_directory"].replace(member_id,
                                                                           "wrong-capture")
        self.out.write_text(json.dumps(payload), encoding="utf-8")
        result, report = self.verify(copied)
        self.assertEqual(result, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)

    def test_verifier_checks_stored_member_lexeme(self) -> None:
        code, text = self.prepare(self.parent)
        self.assertEqual(code, 0, text)
        payload = json.loads(self.out.read_text(encoding="utf-8"))
        payload["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.123456"
        self.out.write_text(json.dumps(payload), encoding="utf-8")
        result, report = self.verify(self.parent)
        self.assertEqual(result, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)
        self.assertEqual(report.count(": PASS"), 19)

    def test_verifier_refuses_missing_primary_and_prior_session_mismatch(self) -> None:
        code, report = self.prepare(self.parent)
        self.assertEqual(code, 0, report)
        original = self.out.read_bytes()
        payload = json.loads(original)
        first = payload["derivation_corpus"]["members"][0]
        copied = self.base / "missing-primary-copy"
        shutil.copytree(self.parent, copied)
        (copied / first["source_directory"] / "manifest.json").unlink()
        code, report = self.verify(copied)
        self.assertEqual(code, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)
        for row in payload["prior_observation_set"]["observations"]:
            if row["attempt_id"] == first["member_id"]:
                row["session_id"] = SESSION_B
                break
        else:
            self.fail("first member absent from prior set")
        self.out.write_text(json.dumps(payload), encoding="utf-8")
        code, report = self.verify(self.parent)
        self.assertEqual(code, 3, report)
        self.assertEqual(report.count(": FAIL"), 1)

    def test_verifier_enforces_four_part_stored_shape(self) -> None:
        code, report = self.prepare(self.parent)
        self.assertEqual(code, 0, report)
        original = self.out.read_bytes()
        member = json.loads(original)["derivation_corpus"]["members"][0]
        source = self.parent / member["source_directory"]
        member_id = member["member_id"]
        malformed = (
            self.parent / SESSION_A / "runs" / member_id,
            self.parent / SESSION_A / "runs/instrument_validation/extra" / member_id,
            self.parent / SESSION_A / "other/instrument_validation" / member_id,
        )
        for target in malformed:
            shutil.copytree(source, target)
            self.addCleanup(shutil.rmtree, target)
            payload = json.loads(original)
            payload["derivation_corpus"]["members"][0]["source_directory"] = (
                target.relative_to(self.parent).as_posix())
            self.out.write_text(json.dumps(payload), encoding="utf-8")
            with self.subTest(target=target):
                code, report = self.verify(self.parent)
                self.assertEqual(code, 3, report)
                self.assertEqual(report.count(": FAIL"), 1)

    def test_verifier_refuses_duplicate_id_and_source(self) -> None:
        code, report = self.prepare(self.parent)
        self.assertEqual(code, 0, report)
        original = self.out.read_bytes()
        for field in ("member_id", "source_directory"):
            payload = json.loads(original)
            members = payload["derivation_corpus"]["members"]
            members[1][field] = members[0][field]
            self.out.write_text(json.dumps(payload), encoding="utf-8")
            # Isolate list uniqueness from the per-member authentication seam.
            with mock.patch.object(issuer, "_verify_corpus_member", return_value=True):
                code, report = self.verify(self.parent)
            with self.subTest(field=field):
                self.assertEqual(code, 3, report)
                self.assertEqual(report.count(": FAIL"), 2)


if __name__ == "__main__":
    unittest.main()
