"""Q12: distinguish the frozen-byte anchor from r4, and audit release HEAD.

No custody is read. Repository checks read code, documentation and commit fields
only; all executable release probes use disposable synthetic repositories.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import release_b5 as release
from tests.git_fixture import init_git_fixture
from tests.b5_analysis.test_frozen_files import (
    B5_ANALYSIS_COMMIT, EVOLVED_ON_MAIN, ROOT, frozen_digests,
)


R4_TAG = "b5/analysis-r4"
REMOTE_PREFIX = "origin" + "/"
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "synthetic", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "synthetic", "GIT_COMMITTER_EMAIL": "test@example.invalid"}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=GIT_ENV)


def commit_or_skip(repo, ref):
    result = git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if result.returncode:
        raise unittest.SkipTest(f"analysis identity ref {ref} unavailable (tags/history may be absent in a shallow clone)")
    return result.stdout.strip()


def remote_branch_literals(source):
    """Flag every remote-ref literal in the B5 tests, including nested helpers.

    There are no allowlisted uses today. Prefix construction here and in the
    scanner's negative probes avoids introducing a resolving ref literal itself.
    """
    return [(node.lineno, node.value) for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and node.value.startswith(REMOTE_PREFIX)]


class AnalysisIdentityTests(unittest.TestCase):
    def test_r4_descends_from_frozen_anchor_with_only_documented_rebinds(self):
        tag = commit_or_skip(ROOT, R4_TAG)
        anchor = commit_or_skip(ROOT, B5_ANALYSIS_COMMIT)
        identities = f"frozen-files constant={anchor}; {R4_TAG}={tag}"
        self.assertNotEqual(anchor, tag, identities)
        result = git(ROOT, "merge-base", "--is-ancestor", anchor, tag)
        self.assertEqual(result.returncode, 0, identities + "; tag must descend from frozen anchor")
        paths = sorted(frozen_digests())
        changed = git(ROOT, "diff", "--name-only", anchor, tag, "--", *paths)
        self.assertEqual(changed.returncode, 0, changed.stderr)
        self.assertEqual(set(changed.stdout.splitlines()), set(EVOLVED_ON_MAIN),
                         identities + "; changed frozen paths must be exactly the cited in-place rebinds")
        stable = sorted(set(paths) - EVOLVED_ON_MAIN)
        self.assertTrue(stable)
        result = git(ROOT, "diff", "--quiet", anchor, tag, "--", *stable)
        self.assertEqual(result.returncode, 0, identities + "; non-rebound frozen files differ")

    def test_runbook_derives_pinned_commit_from_record(self):
        runbook = (ROOT / "docs/analysis/b5/RELEASE-RUNBOOK-lean.md").read_text()
        self.assertIn("PINNED=<record analysis_commit>", runbook)
        self.assertIn('--pinned-commit "$PINNED"', runbook)

    def test_documented_execution_commit_matches_r4_tag(self):
        text = (ROOT / "docs/analysis/b5/DEVIATION-LOG.md").read_text()
        match = re.search(r"analysis commit stays `b5/analysis-r4` \(`([0-9a-f]{7,40})`\)", text)
        self.assertIsNotNone(match, "DLE-5 must name the r4 execution commit")
        tag = commit_or_skip(ROOT, R4_TAG)
        self.assertTrue(tag.startswith(match[1]), f"DLE-5={match[1]}; {R4_TAG}={tag}")

    def test_committed_record_commit_matches_r4_when_available(self):
        # The record normally lives only in custody. Do not follow an absolute
        # path from a config, open a results ref, or substitute a fixture for it.
        records = git(ROOT, "ls-files", "--", "**/B5-BLIND-DRY-RUN-RECORD.json",
                      "**/B5-RELEASE-RECORD.json")
        self.assertEqual(records.returncode, 0, records.stderr)
        paths = records.stdout.splitlines()
        if not paths:
            self.skipTest("no committed B5 dry-run/release record; actual analysis_commit is unverified (custody not read)")
        tag = commit_or_skip(ROOT, R4_TAG)
        for path in paths:
            with self.subTest(record=path):
                self.assertFalse(set(Path(path).parts) & {"restricted", "night-custody", "night-archive"})
                record = git(ROOT, "show", "HEAD:" + path)
                self.assertEqual(record.returncode, 0, record.stderr)
                self.assertEqual(json.loads(record.stdout).get("analysis_commit"), tag,
                                 f"{path}:analysis_commit differs from {R4_TAG}={tag}")

    def test_b5_tests_do_not_resolve_moving_remote_branches(self):
        offenders = []
        for path in sorted((ROOT / "tests/b5_analysis").rglob("*.py")):
            offenders.extend(f"{path.relative_to(ROOT)}:{line}: {value!r}"
                             for line, value in remote_branch_literals(path.read_text()))
        self.assertEqual(offenders, [], "moving remote branch literals:\n" + "\n".join(offenders))

    def test_branch_scan_catches_lane_and_other_remote_refs_but_allows_tags(self):
        lane = "/".join(("origin", "lane", "moving"))
        other = "/".join(("origin", "main"))
        source = f"REF = {lane!r}\ndef nested():\n    return {other!r}\nTAG = {R4_TAG!r}\n"
        self.assertEqual(remote_branch_literals(source), [(1, lane), (3, other)])
        self.assertEqual(remote_branch_literals(f"TAG = {R4_TAG!r}\n# {lane}\n"), [])

    def test_absent_tag_is_an_explicit_skip(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(os.environ, GIT_ENV):
            repo = Path(temporary)
            init_git_fixture(repo, "-q")
            with self.assertRaisesRegex(unittest.SkipTest, re.escape(R4_TAG) + " unavailable"):
                commit_or_skip(repo, R4_TAG)


class ReleaseCheckoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.repo = cls.root / "repo"
        pins = cls.repo / "configs/analysis/b5/seal_pins.json"
        pins.parent.mkdir(parents=True)
        pins.write_bytes((ROOT / "configs/analysis/b5/seal_pins.json").read_bytes())
        with mock.patch.dict(os.environ, GIT_ENV):
            init_git_fixture(cls.repo, "-q")
        for args in (("add", "."), ("commit", "-q", "-m", "synthetic pins")):
            result = git(cls.repo, *args)
            if result.returncode:
                raise RuntimeError(result.stderr)
        cls.pinned = commit_or_skip(cls.repo, "HEAD")
        result = git(cls.repo, "commit", "-q", "--allow-empty", "-m", "synthetic descendant")
        if result.returncode:
            raise RuntimeError(result.stderr)
        cls.head = commit_or_skip(cls.repo, "HEAD")
        result = git(cls.repo, "commit-tree", "HEAD^{tree}", "-m", "synthetic unrelated root")
        if result.returncode:
            raise RuntimeError(result.stderr)
        cls.unrelated = result.stdout.strip()

    def test_native_git_relations_include_behind_divergent_and_missing(self):
        for head, pinned, expected in (
            (self.head, self.head, "equals_pinned"),
            (self.head, self.pinned, "descends_from_pinned"),
            (self.pinned, self.head, "unrelated"),
            (self.head, self.unrelated, "unrelated"),
            (self.head, "0" * 40, "unknown"),
            ("0" * 40, "0" * 40, "unknown"),
        ):
            with self.subTest(head=head, pinned=pinned):
                self.assertEqual(release.checkout_relation(self.repo, head, pinned), expected)

    def test_invalid_identity_is_unknown_without_invoking_git(self):
        for head, pinned in ((None, self.pinned), (self.head, None), (7, self.pinned),
                             (self.head, 7), ("HEAD", self.pinned), (self.head, "--bad")):
            with self.subTest(head=head, pinned=pinned), mock.patch.object(release.subprocess, "run") as run:
                self.assertEqual(release.checkout_relation(self.repo, head, pinned), "unknown")
                run.assert_not_called()

    def test_git_error_is_unknown_and_never_a_success_relation(self):
        with mock.patch.object(release.subprocess, "run", side_effect=OSError("unavailable")):
            self.assertEqual(release.checkout_relation(self.repo, self.head, self.pinned), "unknown")
        for code in (2, 128, -9):
            with self.subTest(code=code), mock.patch.object(release.subprocess, "run") as run:
                run.return_value.returncode = code
                self.assertEqual(release.checkout_relation(self.repo, self.head, self.pinned), "unknown")

    def test_verdict_persists_relations_without_changing_decisions(self):
        for pinned, relation in ((self.head, "equals_pinned"), (self.pinned, "descends_from_pinned"),
                                 (self.unrelated, "unrelated"), ("0" * 40, "unknown")):
            for refusal, disagreement, expected_code in ((None, False, 0),
                                                        ("comparator_disagreement", True, 1),
                                                        ("comparator_refused", False, 2)):
                with self.subTest(relation=relation, code=expected_code), tempfile.TemporaryDirectory() as temporary:
                    with mock.patch.object(release, "verify_digests", return_value=({}, {}, {})), \
                         mock.patch.object(release, "stage_recompute", return_value=({}, None)), \
                         mock.patch.object(release, "stage_compare", return_value=({}, refusal, disagreement)):
                        verdict, code = release.release(self.root / "unused-custody", self.root / "unused-index",
                                                        pinned, temporary, repo=self.repo)
                    self.assertEqual(code, expected_code)
                    self.assertEqual(verdict["verdict"], "agree" if code == 0 else "hold")
                    self.assertEqual(verdict["reason"], refusal)
                    self.assertEqual(verdict["checkout_head"], self.head)
                    self.assertEqual(verdict["checkout_relation"], relation)
                    self.assertEqual(verdict["release_checkout"], {"commit": self.head, "clean": True})
                    self.assertEqual(json.loads((Path(temporary) / "verdict.json").read_text()), verdict)

    def test_checkout_refusal_keeps_unknown_metadata_and_existing_exit(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(release, "check_checkout", side_effect=release.Refusal("release_checkout_not_clean")), \
                 mock.patch.object(release, "verify_digests") as verify:
                verdict, code = release.release(None, None, self.pinned, temporary, repo=self.repo)
            self.assertEqual((code, verdict["reason"]), (2, "release_checkout_not_clean"))
            self.assertIsNone(verdict["checkout_head"])
            self.assertEqual(verdict["checkout_relation"], "unknown")
            verify.assert_not_called()

    def test_synthetic_record_identity_must_equal_pinned_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = root / "index.json"
            entry = {"pack": "alpha", "plan_id": "synthetic", "harvest_record_sha256": "a" * 64,
                     **{key: str(root / "synthetic-inputs")
                        for key in ("archive_root", "claim_runs_root", "bound_runs_root")}}
            index.write_text(json.dumps({"attempts": [entry]}))
            pins = json.loads((self.repo / "configs/analysis/b5/seal_pins.json").read_text())["sealed"]
            record = {"schema_version": release.RECORD_SCHEMA, "mode": "blind-dry-run",
                      "analysis_commit": self.pinned, "window_index_sha256": hashlib.sha256(index.read_bytes()).hexdigest(),
                      "sealed": {k: pins[v] for k, v in release.SEAL_KEYS.items()}, "windows": [entry],
                      "input_census": [], "steps": [{"outputs": []}], "completed_without_tooling_refusal": True}
            path = root / release.RECORD
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(record))
            verified, _, _ = release.verify_digests(root, index, self.pinned, self.repo)
            self.assertEqual(verified["analysis_commit"], self.pinned)
            record["analysis_commit"] = self.head
            path.write_text(json.dumps(record))
            with self.assertRaises(release.Refusal) as refused:
                release.verify_digests(root, index, self.pinned, self.repo)
            self.assertEqual((refused.exception.code, refused.exception.where),
                             (release.DIFFERS, "binding/analysis_commit"))
