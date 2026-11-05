"""F1/F2 gates on disposable Git objects; no study data or pipeline runs."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import freeze_by_commit as f
from tests.git_fixture import init_git_fixture


class CommitFreezeTests(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop(f.REGISTRATION_COMMIT_ENV, None)
        self.temporary = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        init_git_fixture(self.repo, "-q")
        self.write("estimator.py", "VALUE = 1\n")
        self.base = self.commit("registered computation")
        self.git("tag", "-a", "b5/analysis-r2", "-m", "release")
        self.registration = {
            "schema": "joulewise.block_freeze.v1",
            "active_analysis": "b5/analysis-r2",
            "tags": {"b5/analysis-r2": self.tag_record()},
            "ruled_descendants": {},
        }

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), "-c", "user.name=Fixture", "-c",
             "user.email=fixture@example.invalid", *args], stderr=subprocess.PIPE,
        ).decode().strip()

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def tag_record(self):
        return {"tag_object": self.git("rev-parse", "refs/tags/b5/analysis-r2"),
                "commit": self.base, "tree": self.git("rev-parse", self.base + "^{tree}")}

    def require(self, head):
        return f.require_analysis_head(self.repo, head, registration=self.registration)

    def ruled_child(self, text="VALUE = 2\n"):
        self.write("estimator.py", text)
        self.write("docs/ruling.md", "Fixture owner permits this exact change.\n")
        head = self.commit("ruled block correction")
        self.registration["ruled_descendants"][head] = {
            "tree": self.git("rev-parse", head + "^{tree}"), "ruling": "docs/ruling.md",
            "ruling_sha256": hashlib.sha256((self.repo / "docs/ruling.md").read_bytes()).hexdigest(),
        }
        return head

    def test_release_does_not_need_origin_main(self):
        self.assertEqual(self.git("remote"), "")
        self.require(self.base)
        self.write("estimator.py", "later main bytes\n")
        self.assertEqual(f.blob(self.repo, self.base, "estimator.py"), b"VALUE = 1\n")
        self.assertEqual(f.blob_digests(self.repo, self.base, ["estimator.py"]),
                         {"estimator.py": hashlib.sha256(b"VALUE = 1\n").hexdigest()})

    def test_lightweight_moved_or_wrong_tree_tag_refuses(self):
        for defect in ("lightweight", "moved", "tree", "object"):
            with self.subTest(defect=defect):
                self.git("tag", "-d", "b5/analysis-r2")
                self.git("tag", "-a", "b5/analysis-r2", self.base, "-m", "release")
                record = self.tag_record()
                if defect == "lightweight":
                    self.git("tag", "-f", "b5/analysis-r2", self.base)
                elif defect == "moved":
                    self.write("estimator.py", defect)
                    child = self.commit(defect)
                    self.git("tag", "-fa", "b5/analysis-r2", child, "-m", defect)
                else:
                    record["tree" if defect == "tree" else "tag_object"] = "0" * 40
                with self.assertRaises(f.FreezeIdentityError):
                    f.verify_tag(self.repo, "b5/analysis-r2", record)

    def test_descendant_ledger_cannot_authorize_even_the_first_fix(self):
        first = self.ruled_child()
        with self.assertRaisesRegex(f.FreezeIdentityError, "analysis_descendant_unruled"):
            self.require(first)
        self.write("estimator.py", "unruled intermediate\n")
        middle = self.commit("unruled")
        last = self.ruled_child("last\n")
        with self.assertRaisesRegex(f.FreezeIdentityError, "analysis_descendant_unruled"):
            self.require(last)
        self.assertNotIn(middle, self.registration["ruled_descendants"])

    def test_environment_registration_cannot_authorize_a_descendant(self):
        self.write(f.REGISTRATION, json.dumps(self.registration))
        self.commit("checkout registration")
        child = self.ruled_child()
        self.write(f.REGISTRATION, json.dumps(self.registration))
        authority = self.commit("register the already-reviewed block correction")
        self.git("checkout", "--detach", child)
        self.assertTrue((self.repo / f.REGISTRATION).exists())
        with mock.patch.dict(os.environ, {f.REGISTRATION_COMMIT_ENV: authority}):
            with self.assertRaises(f.FreezeIdentityError):
                f.require_analysis_head(self.repo, child)
        for invalid in ("main", "../outside", "f" * 40):
            with mock.patch.dict(os.environ, {f.REGISTRATION_COMMIT_ENV: invalid}):
                with self.assertRaises(f.FreezeIdentityError):
                    f.require_analysis_head(self.repo, child)

    def test_forged_tag_and_registration_cannot_replace_checkout_authority(self):
        self.write(f.REGISTRATION, json.dumps(self.registration))
        self.commit("checkout registration")
        child = self.ruled_child()
        self.git("tag", "-a", "b5/analysis-r3", "-m", "unreviewed fix")
        forged = json.loads(json.dumps(self.registration))
        forged["active_analysis"] = "b5/analysis-r3"
        forged["tags"]["b5/analysis-r3"] = {
            "tag_object": self.git("rev-parse", "refs/tags/b5/analysis-r3"),
            "commit": child, "tree": self.git("rev-parse", child + "^{tree}"),
        }
        self.write(f.REGISTRATION, json.dumps(forged))
        authority = self.commit("forged registration authority")
        self.git("checkout", "--detach", child)
        with mock.patch.dict(os.environ, {f.REGISTRATION_COMMIT_ENV: authority}):
            with self.assertRaises(f.FreezeIdentityError):
                f.require_analysis_head(self.repo, child)
        # Neither a local tag nor a docs blob called a ruling grants authority.
        with self.assertRaisesRegex(f.FreezeIdentityError, "analysis_descendant_unruled"):
            f.require_analysis_head(self.repo, child)

    def test_nonempty_legacy_ledger_in_checkout_refuses(self):
        self.ruled_child()
        self.write(f.REGISTRATION, json.dumps(self.registration))
        with self.assertRaisesRegex(f.FreezeIdentityError, "freeze_registration_invalid"):
            f.load_registration(self.repo)

    def test_unrelated_history_and_missing_objects_refuse(self):
        self.git("checkout", "--orphan", "unrelated")
        self.write("estimator.py", "different history\n")
        head = self.commit("not a descendant")
        for commit in (head, "f" * 40):
            with self.assertRaises(f.FreezeIdentityError):
                self.require(commit)

    def test_ruling_and_tree_must_authenticate_at_the_ruled_commit(self):
        head = self.ruled_child()
        record = self.registration["ruled_descendants"][head]
        for key, bad in (("tree", "0" * 40), ("ruling_sha256", "0" * 64),
                         ("ruling", "docs/missing.md"), ("ruling", "../outside"),
                         ("ruling", None), ("ruling_sha256", None)):
            with self.subTest(key=key, bad=bad):
                old = record[key]
                record[key] = bad
                with self.assertRaises(f.FreezeIdentityError):
                    self.require(head)
                record[key] = old

    def test_merged_side_commit_also_needs_a_ruling(self):
        self.git("checkout", "-b", "side")
        self.write("side.py", "unruled side branch\n")
        side = self.commit("side")
        self.git("checkout", "-b", "block", self.base)
        self.ruled_child()
        self.git("merge", "--no-ff", "side", "-m", "merge")
        head = self.git("rev-parse", "HEAD")
        self.registration["ruled_descendants"][head] = {
            "tree": self.git("rev-parse", head + "^{tree}"), "ruling": "docs/ruling.md",
            "ruling_sha256": hashlib.sha256((self.repo / "docs/ruling.md").read_bytes()).hexdigest(),
        }
        with self.assertRaisesRegex(f.FreezeIdentityError, "analysis_descendant_unruled"):
            self.require(head)
        self.assertNotIn(side, self.registration["ruled_descendants"])

    def test_git_path_scope_and_calibration_stub_fail_closed(self):
        for path in ("/Users/edr/outside", "restricted/data", "docs/restricted/data", "../data"):
            with self.assertRaisesRegex(f.FreezeIdentityError, "freeze_path_invalid"):
                f.blob(self.repo, self.base, path)
        with self.assertRaisesRegex(f.FreezeIdentityError, "calibration_commit_scope_reissue_pending"):
            f.require_commit_scoped_calibration()

    def test_custody_requests_the_registered_analysis_gate(self):
        from joulewise import paper_custody as custody, identity_pins as pins
        ref = custody.ReportedEnergyParentsRef(role="fixture.synthetic", runs_root=self.repo)
        refusal = pins.IdentityPinProjectionError("readiness_identity_artifact_unreadable", "fixture")
        with mock.patch.object(custody, "_mint_git_anchor", side_effect=refusal) as anchor:
            with self.assertRaises(custody.PaperCustodyRefusal):
                custody.open_paper_input(ref)
        anchor.assert_called_once_with(require_registered_analysis=True)

    def test_mint_anchor_uses_registered_identity_and_retains_clean_gate(self):
        from joulewise import identity_pins as pins
        class MintError(ValueError):
            pass
        module = SimpleNamespace(REPO_ROOT=self.repo, MintError=MintError,
                                 _actual_v2_git_state=lambda: (self.base, None))
        with mock.patch.object(pins, "_load_mint_module", return_value=module), \
             mock.patch.object(f, "load_registration", return_value=self.registration):
            self.assertEqual(pins._mint_git_anchor(require_registered_analysis=True), (self.repo, self.base))
            self.assertEqual(pins._mint_git_anchor(require_origin_main=True), (self.repo, self.base))
            self.write("estimator.py", "on main alone\n")
            child = self.commit("unruled main change")
            module._actual_v2_git_state = lambda: (child, True)
            with self.assertRaises(pins.IdentityPinProjectionError):
                pins._mint_git_anchor(require_registered_analysis=True)
            def dirty():
                raise MintError("requires a clean Git working tree")
            module._actual_v2_git_state = dirty
            with self.assertRaises(pins.IdentityPinProjectionError) as raised:
                pins._mint_git_anchor(require_registered_analysis=True)
            self.assertEqual(raised.exception.reason_code, "readiness_identity_environment_dirty")


if __name__ == "__main__":
    unittest.main()
