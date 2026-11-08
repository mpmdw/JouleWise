"""Tiny local Git histories only; no measurements, network, or weight caches."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ops"))
import prune_inventory as census
import prune_branch_names as names
import prune_verify as verifier


class PruneOpsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="jw-prune-test-")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.out = Path(self.tmp.name) / "census"
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Synthetic")
        self.git("config", "user.email", "synthetic@example.invalid")
        self.put("tools/code.py", "# ancestor\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", self.base)
        self.git("update-ref", "refs/remotes/origin/old-name", self.base)
        self.previous = [dict(branch="old-name", snapshot_commit=self.base,
                              disposition="MERGED-CANDIDATE")]

    def git(self, *args):
        return census.git(self.repo, *args).decode().strip()

    def put(self, path, text):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)

    def hold(self):
        self.git("checkout", "--orphan", "hold")
        self.git("rm", "-rf", ".")
        self.put("seed.txt", "off-main\n")
        self.git("add", ".")
        self.git("commit", "-m", "unique")
        pin = self.git("rev-parse", "HEAD")
        self.put("docs/deep/registration.md", f"pin {pin}\n")
        self.put("tools/check.py", f"# pin {pin}; uses old-name\n")
        self.put("restricted/sealed.txt", "never-read-old-name feedface1\n")
        self.put("tests/fixtures/captures/power_trace.csv", "never-read-old-name deadbee1\n")
        self.put("tests/fixtures/captures/observations.json", '{"data": "deadbee2 old-name"}\n')
        self.put("configs/registration.json", '{"commit": "' + pin + '"}\n')
        (self.repo / "tools/link").symlink_to("../restricted/sealed.txt")
        self.git("add", ".")
        self.git("commit", "-m", "references")
        self.git("update-ref", "refs/remotes/origin/hold", "HEAD")
        self.git("checkout", "main")
        return pin

    def refresh(self):
        census.inventory(self.repo, self.out, self.previous)
        tags = self.out / "TAGS-TO-CREATE.tsv"
        census.write_tsv(tags, ["tag", "commit"], [dict(
            tag="archive/process-traces-before-release-prune-2026-11-08", commit=self.base)])
        return tags

    def test_hold_docs_tools_and_branch_name_are_scanned_without_sealed_blobs(self):
        pin = self.hold()
        self.refresh()
        pins = {r["commit"]: r for r in census.rows(self.out / "PIN-COMMITS.tsv")}
        self.assertEqual(pins[pin]["coverage"], "HOLD-BUNDLE-ONLY")
        self.assertIn("docs/deep/registration.md", pins[pin]["source_locations"])
        self.assertIn("tools/check.py", pins[pin]["source_locations"])
        self.assertTrue(names.scan(self.repo, self.out, self.out / "names.tsv"))
        hits = census.rows(self.out / "names.tsv")
        self.assertEqual({r["path"] for r in hits}, {"tools/check.py"})
        self.assertNotIn("feedface1", (self.out / "PIN-UNRESOLVED.tsv").read_text())
        self.assertNotIn("deadbee1", (self.out / "PIN-UNRESOLVED.tsv").read_text())
        self.assertNotIn("deadbee2", (self.out / "PIN-UNRESOLVED.tsv").read_text())

    def test_hold_only_pins_block_release_until_whole_tip_is_tagged(self):
        self.hold()
        tags = self.refresh()
        self.git("tag", "-a", census.rows(tags)[0]["tag"], self.base, "-m", "archive")
        with self.assertRaisesRegex(ValueError, "HOLD-only=1"):
            verifier.verify(self.repo, self.out, tags, self.base, True)
        tip = self.git("rev-parse", "refs/remotes/origin/hold")
        self.git("tag", "-a", "archive/branch/hold", tip, "-m", "retire whole tip")
        archive = census.rows(tags)
        archive.append(dict(tag="archive/branch/hold", commit=tip))
        census.write_tsv(tags, ["tag", "commit"], archive)
        with contextlib.redirect_stdout(io.StringIO()):
            verifier.verify(self.repo, self.out, tags, self.base, True)

    def test_stale_archive_row_and_moved_branch_refuse(self):
        self.hold()
        tags = self.refresh()
        data = census.rows(tags)
        data[0]["commit"] = self.git("rev-parse", "refs/remotes/origin/hold")
        census.write_tsv(tags, ["tag", "commit"], data)
        with self.assertRaisesRegex(ValueError, "stale archive TSV"):
            verifier.verify(self.repo, self.out, tags, self.base)
        self.git("update-ref", "refs/remotes/origin/hold", self.base)
        with self.assertRaisesRegex(ValueError, "stale census scope"):
            verifier.verify(self.repo, self.out, tags, self.base)

    def test_new_or_moved_merged_branch_stays_hold(self):
        self.git("update-ref", "refs/remotes/origin/new", self.base)
        result = {r["branch"]: r for r in census.classify(self.repo, self.base, self.previous)}
        self.assertEqual(result["new"]["disposition"], "HOLD")
        self.assertEqual(result["old-name"]["disposition"], "MERGED-CANDIDATE")

    def test_added_remote_ref_invalidates_the_scan(self):
        tags = self.refresh()
        self.git("update-ref", "refs/remotes/origin/new", self.base)
        with self.assertRaisesRegex(ValueError, "stale branch census"):
            verifier.verify(self.repo, self.out, tags, self.base)

    def test_numeric_fixture_values_do_not_become_commit_pins(self):
        self.assertEqual(list(census.commit_literals("value=0.5033793, time=1234567")), [])
        self.assertEqual(list(census.commit_literals('commit="1234567"; head 7654321')),
                         ["1234567", "7654321"])

    def test_incomplete_hold_scope_refuses(self):
        self.hold()
        tags = self.refresh()
        scopes = census.rows(self.out / "CENSUS-SCOPE.tsv")
        census.write_tsv(self.out / "CENSUS-SCOPE.tsv", ["ref", "commit", "scan"], scopes[:1])
        with self.assertRaisesRegex(ValueError, "incomplete main/HOLD scope"):
            verifier.verify(self.repo, self.out, tags, self.base)

    def test_grep_preserves_overlapping_literal_candidates(self):
        self.hold()
        self.git("update-ref", "refs/remotes/origin/old", self.base)
        self.previous.append(dict(branch="old", snapshot_commit=self.base,
                                  disposition="MERGED-CANDIDATE"))
        self.refresh()
        names.scan(self.repo, self.out, self.out / "names.tsv")
        hits = census.rows(self.out / "names.tsv")
        self.assertEqual({r["candidate"] for r in hits}, {"old", "old-name"})

    def test_one_command_refresh_cli(self):
        self.refresh()
        output = Path(self.tmp.name) / "refreshed"
        script = Path(__file__).resolve().parents[1] / "scripts/ops/prune_refresh.py"
        result = subprocess.run([sys.executable, "-B", str(script), "--repo", str(self.repo),
                                 "--inputs", str(self.out), "--output", str(output),
                                 "--archive-commit", self.base, "--archive-date", "2026-11-08"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output / "BRANCH-NAME-CONSUMERS.tsv").is_file())

    def test_literal_prefilter_escapes_names_and_shares_overlapping_prefixes(self):
        pattern = names.literal_pattern(["impl/a.b", "impl/a+b", "old", "old-name"])
        self.assertIsNotNone(pattern.search("uses impl/a.b"))
        self.assertIsNotNone(pattern.search("uses impl/a+b"))
        self.assertIsNotNone(pattern.search("uses old-name"))
        self.assertIsNone(pattern.search("uses impl/axb"))

    def test_census_outputs_are_independent_of_python_hash_seed(self):
        self.put("tools/digests.py", "# " + " ".join(f"{i:064x}" for i in range(8)) + "\n")
        self.git("add", ".")
        self.git("commit", "-m", "synthetic source digests")
        self.base = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", self.base)
        self.refresh()
        script = Path(__file__).resolve().parents[1] / "scripts/ops/prune_inventory.py"
        outputs = []
        for seed in (1, 2):
            dest = Path(self.tmp.name) / f"seed-{seed}"
            result = subprocess.run([sys.executable, "-B", str(script), "--repo", str(self.repo),
                                     "--triage", str(self.out / "BRANCH-TRIAGE.tsv"), "--output", str(dest)],
                                    env=dict(os.environ, PYTHONHASHSEED=str(seed)), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append({p.name: p.read_bytes() for p in dest.iterdir()})
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
