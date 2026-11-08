"""DLE-1 lean release check (scripts/release_b5.py) end to end on SYNTHETIC custody only.

The custody is the comparator's producer-shaped synthetic L9 output (test_comparator.l9_files), written with
a full blind-dry-run record whose input census binds three small synthetic archives (support.full_pack) and
whose pinned commit is a scratch Git repository's head carrying the real seal pins. Stage (a) and the
comparator always run for real. In the agreement and disagreement cases the recompute stage writes the
comparator fixture's matching recompute output (the synthetic archives cannot reproduce those values); one
case runs the real recompute on the archives and expects a held verdict, with the pipeline intact.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tests.git_fixture import init_git_fixture

from . import test_comparator as tc
from .support import ROOT, dump, full_pack

spec = importlib.util.spec_from_file_location("release_b5_test_subject", ROOT / "scripts/release_b5.py")
rel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rel)
INDEX_ATTEMPTS = json.loads(tc.WINDOW_INDEX.read_text())["attempts"]
FLOAT = re.compile(r"(?<![A-Za-z0-9])(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)(?![A-Za-z0-9])")
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The scratch repository and the three synthetic archives are shared; a test that changes one restores it.
        cls.shared = tempfile.TemporaryDirectory()
        shared = Path(cls.shared.name)
        cls.repo = cls.make_repo(shared / "repo")
        cls.pinned = subprocess.run(["git", "-C", str(cls.repo), "rev-parse", "HEAD"], check=True, capture_output=True,
                                    text=True, env=GIT_ENV).stdout.strip()
        cls.archives = {p: full_pack(shared / "archives", p.upper()) for p in rel.PACKS}

    @classmethod
    def tearDownClass(cls):
        cls.shared.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.index = self.write_index()
        self.custody = self.write_custody()
        self.ours = tc.recompute_output()
        self.ours["comparison_stopped"] = False

    # -- synthetic inputs -------------------------------------------------------------------------------
    @staticmethod
    def make_repo(repo):
        target = repo / "configs/analysis/b5/seal_pins.json"
        target.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "configs/analysis/b5/seal_pins.json", target)
        init_git_fixture(repo, "-q")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, env=GIT_ENV)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "pins"], check=True, env=GIT_ENV)
        return repo

    def preserve(self, path):
        """Restore a shared file after the test that changes it."""
        raw = path.read_bytes()
        self.addCleanup(path.write_bytes, raw)

    def analysed(self):
        return {e["pack"]: e for e in INDEX_ATTEMPTS if e["claim_usable"]}

    def write_index(self):
        attempts = copy.deepcopy(INDEX_ATTEMPTS)
        for entry in attempts:
            if entry["claim_usable"]:
                archive = self.archives[entry["pack"]]
                entry.update(archive_root=str(archive), claim_runs_root=str(archive / "sources/claim-runs"),
                             bound_runs_root=str(archive / "sources/bound-runs"),
                             measurement_root=str(self.root / "measurement" / entry["pack"]),
                             harvest_record_sha256=sha(archive / "harvest.json"))
        path = self.root / "index.json"
        dump(path, {"schema": "joulewise.b5_window_index.v1", "attempts": attempts})
        return path

    def write_custody(self, files=None):
        files = tc.l9_files() if files is None else files
        custody = self.root / "custody"
        outputs = []
        for name, value in files.items():
            path = custody / rel.RESTRICTED / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = tc.written(name, value)
            path.write_bytes(raw)
            outputs.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
        census, windows = [], []
        for pack, entry in self.analysed().items():
            archive = self.archives[pack]
            windows.append({"pack": pack, "plan_id": entry["plan_id"], "harvest_record_sha256": sha(archive / "harvest.json"),
                            "harvest_pin": "0" * 40, "kept_counts": {}})
            census += [{"window": pack, "path": "harvest.json", "sha256": sha(archive / "harvest.json"), "check": "window_index"},
                       {"window": pack, "path": "derived/exclusions.json",
                        "sha256": sha(archive / "derived/exclusions.json"), "check": "harvest_outputs"},
                       {"window": pack, "path": "original/claim-runs/whole-window-verdict.json",
                        "sha256": sha(archive / "sources/claim-runs/whole-window-verdict.json"), "check": "input_census"},
                       {"window": pack, "path": "binding/plan_tree", "sha256": "1" * 64, "check": "plan_tree_binding:synthetic"}]
        pins = json.loads((ROOT / "configs/analysis/b5/seal_pins.json").read_text())["sealed"]
        record = {"schema_version": rel.RECORD_SCHEMA, "mode": "blind-dry-run", "analysis_commit": self.pinned,
                  "window_index_sha256": sha(self.index),
                  "sealed": {k: pins[v] for k, v in rel.SEAL_KEYS.items()}, "attempts": [], "windows": windows,
                  "input_census": census,
                  "steps": [{"step": "11", "window": None, "status": "ok", "exit_status": 0, "registered_exit": None,
                             "schema_valid": True, "outputs": outputs, "refusal": None, "flags": []}],
                  "completed_without_tooling_refusal": True}
        dump(custody / rel.RECORD, record)
        return custody

    # -- running -----------------------------------------------------------------------------------------
    def fake_recompute(self, ours):
        real = rel.run_program

        def run(argv, restricted, name):
            if name == "recompute":
                out = Path(argv[argv.index("--out") + 1])
                out.write_text(json.dumps(ours))
                self.recompute_argv = argv
                return 0
            return real(argv, restricted, name)
        return mock.patch.object(rel, "run_program", run)

    def release(self, fake=True, ours=None, **kwargs):
        out = rel.prepare_restricted(self.root / ("restricted-out-" + str(len(list(self.root.glob("restricted-out-*"))))),
                                     self.custody)
        args = (self.custody, self.index, kwargs.pop("pinned", self.pinned), out)
        if fake:
            with self.fake_recompute(self.ours if ours is None else ours):
                verdict, code = rel.release(*args, repo=self.repo, workers=3, **kwargs)
        else:
            verdict, code = rel.release(*args, repo=self.repo, workers=3, **kwargs)
        text = (out / "verdict.json").read_text()
        self.assertIsNone(FLOAT.search(text), "verdict must be structure only")
        self.assertEqual(json.loads(text), verdict)
        return verdict, code, out

    # -- cases -------------------------------------------------------------------------------------------
    def test_agreement_releases(self):
        verdict, code, out = self.release()
        self.assertEqual((code, verdict["verdict"], verdict["reason"]), (0, "agree", None))
        stages = verdict["stages"]
        self.assertEqual(stages["digests"]["status"], "verified")
        self.assertEqual(stages["digests"]["outputs_verified"], len(tc.l9_files()))
        self.assertEqual(stages["digests"]["input_census_verified"], 9)
        self.assertEqual(stages["digests"]["input_census_binding_rows"], 3)
        self.assertEqual(stages["comparator"]["status"], "agree")
        self.assertTrue(stages["comparator"]["families"])
        self.assertTrue(all(row["verdict"] == "agree" and row["fail"] == 0
                            for row in stages["comparator"]["families"].values()))
        self.assertEqual(stages["comparator"]["step11"]["unmapped"], 0)
        self.assertTrue((out / "comparison.json").is_file() and (out / "recompute.json").is_file())
        # The recompute ran on every indexed root, with the member detail and the requested pool.
        argv = self.recompute_argv
        for pack, archive in self.archives.items():
            self.assertEqual(argv[argv.index("--" + pack) + 1], str(archive))
            self.assertEqual(argv[argv.index("--claim-runs-" + pack) + 1], str(archive / "sources/claim-runs"))
            self.assertEqual(argv[argv.index("--bound-runs-" + pack) + 1], str(archive / "sources/bound-runs"))
        self.assertIn("--member-detail", argv)
        self.assertEqual(argv[argv.index("--workers") + 1], "3")

    def test_disagreement_holds_with_family_counts_only(self):
        ours = copy.deepcopy(self.ours)
        cid = tc.DECODE
        ours["contrasts"][cid]["dbar_j"] += 1.0
        verdict, code, _ = self.release(ours=ours)
        self.assertEqual((code, verdict["verdict"], verdict["reason"]), (1, "hold", "comparator_disagreement"))
        families = verdict["stages"]["comparator"]["families"]
        self.assertEqual(families["contrast_j"]["verdict"], "hold")
        self.assertGreater(families["contrast_j"]["fail"], 0)
        self.assertEqual(families["run_phase_energy_j"]["verdict"], "agree")

    def test_tampered_output_digest_refuses_before_any_program_runs(self):
        name = next(iter(tc.l9_files()))
        path = self.custody / rel.RESTRICTED / name
        path.write_bytes(path.read_bytes() + b" ")
        with mock.patch.object(rel, "run_program", side_effect=AssertionError("must not run")):
            verdict, code, out = self.release(fake=False)
        self.assertEqual((code, verdict["verdict"], verdict["reason"]), (2, "hold", rel.DIFFERS))
        self.assertEqual(verdict["stages"]["recompute"]["status"], "not_run")
        self.assertEqual((out / "refusal-location.txt").read_text(), "output/" + name + "\n")

    def test_missing_output_refuses(self):
        (self.custody / rel.RESTRICTED / next(iter(tc.l9_files()))).unlink()
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))

    def test_symlinked_output_refuses(self):
        name = next(iter(tc.l9_files()))
        path = self.custody / rel.RESTRICTED / name
        copy_path = self.root / "elsewhere.json"
        copy_path.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(copy_path)
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))

    def test_tampered_input_census_refuses(self):
        path = self.archives["beta"] / "sources/claim-runs/whole-window-verdict.json"
        self.preserve(path)
        path.write_bytes(path.read_bytes() + b"\n")
        verdict, code, out = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))
        self.assertEqual((out / "refusal-location.txt").read_text(),
                         "input/beta/original/claim-runs/whole-window-verdict.json\n")

    def test_special_file_in_input_census_refuses_instead_of_hanging(self):
        # Fable cold pass (PR #688): a FIFO at an indexed input path blocked a hashing thread forever.
        path = self.archives["beta"] / "sources/claim-runs/whole-window-verdict.json"
        raw = path.read_bytes()
        path.unlink()
        os.mkfifo(path)

        def restore():
            path.unlink()
            path.write_bytes(raw)
        self.addCleanup(restore)
        verdict, code, out = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))
        self.assertEqual((out / "refusal-location.txt").read_text(),
                         "input/beta/original/claim-runs/whole-window-verdict.json\n")

    def test_file_sha256_hashes_regular_files_only(self):
        regular = self.root / "regular.bin"
        regular.write_bytes(b"x" * (3 << 20))
        self.assertEqual(rel.file_sha256(regular), hashlib.sha256(regular.read_bytes()).hexdigest())
        self.assertIsNone(rel.file_sha256(self.root))
        self.assertIsNone(rel.file_sha256(self.root / "absent"))

    def test_malformed_seal_pins_at_the_commit_refuse_as_such(self):
        # Fable cold pass (PR #688): malformed pins were reported as an unavailable commit.
        real = rel.git

        def git(repo, *args):
            return b"{not json" if args[:1] == ("show",) else real(repo, *args)
        with mock.patch.object(rel, "git", git):
            verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, "seal_pins_invalid"))

    def test_other_pinned_commit_refuses(self):
        verdict, code, out = self.release(pinned="a" * 40)
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))
        self.assertEqual((out / "refusal-location.txt").read_text(), "binding/analysis_commit\n")

    def test_record_sealed_digest_differing_from_pins_at_the_commit_refuses(self):
        record_path = self.custody / rel.RECORD
        record = json.loads(record_path.read_text())
        record["sealed"]["analysis_plan_sha256"] = "2" * 64
        record_path.write_text(json.dumps(record))
        verdict, code, out = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))
        self.assertEqual((out / "refusal-location.txt").read_text(), "binding/sealed\n")

    def test_other_window_index_refuses(self):
        self.index.write_bytes(self.index.read_bytes() + b"\n")
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))

    def test_incomplete_or_release_record_refuses(self):
        record_path = self.custody / rel.RECORD
        original = record_path.read_text()
        for edit, reason in ((lambda r: r.update(completed_without_tooling_refusal=False), "dry_run_not_completed"),
                             (lambda r: r.update(mode="release"), "dry_run_record_invalid"),
                             (lambda r: r.update(release_difference={"path": "x"}), "dry_run_record_invalid")):
            record = json.loads(original)
            edit(record)
            record_path.write_text(json.dumps(record))
            with self.subTest(reason=reason):
                verdict, code, _ = self.release()
                self.assertEqual((code, verdict["reason"]), (2, reason))
        record_path.unlink()
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, "dry_run_record_missing_or_incomplete"))

    def test_duplicate_key_in_record_refuses(self):
        record_path = self.custody / rel.RECORD
        record_path.write_text('{"mode": "blind-dry-run", ' + record_path.read_text()[1:])
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, "dry_run_record_invalid"))

    def test_dirty_release_checkout_refuses(self):
        (self.repo / "untracked.txt").write_text("x")
        self.addCleanup((self.repo / "untracked.txt").unlink)
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, "release_checkout_not_clean"))

    def test_fifo_output_refuses_instead_of_hanging(self):
        # Sol adversarial pass (PR #688): a FIFO among the custody outputs blocked the no-follow open.
        record = json.loads((self.custody / rel.RECORD).read_text())
        name = record["steps"][0]["outputs"][0]["name"]
        path = self.custody / rel.RESTRICTED / name
        path.unlink()
        os.mkfifo(path)
        verdict, code, out = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))
        self.assertEqual((out / "refusal-location.txt").read_text(), "output/" + name + "\n")

    def fake_comparison(self, result, exit_code=0):
        real = rel.run_program

        def run(argv, restricted, name):
            if name == "comparator":
                Path(argv[argv.index("--restricted-out") + 1]).write_text(json.dumps(result))
                return exit_code
            return real(argv, restricted, name)
        return mock.patch.object(rel, "run_program", run)

    def test_comparison_without_coverage_lists_or_comparisons_holds(self):
        # Sol adversarial pass (PR #688): exit 0 with {"counts": {}, "coverage": {}} released.
        empty = {"unmapped": [], "nonfinite": [], "uncovered_numeric": [], "absent_sources": []}
        cases = [({"counts": {}, "coverage": {}}, "comparison_output_unreadable"),
                 ({"counts": {}, "coverage": empty}, "comparison_vacuous"),
                 ({"counts": {"count": {"pass": 0, "fail": 0}}, "coverage": empty}, "comparison_vacuous")]
        for result, reason in cases:
            with self.subTest(reason=reason), self.fake_comparison(result):
                verdict, code, _ = self.release()
                self.assertEqual((code, verdict["verdict"], verdict["reason"]), (2, "hold", reason))
        with self.fake_comparison({"counts": {"count": {"pass": 1, "fail": 0}}, "coverage": empty}):
            verdict, code, _ = self.release()
        self.assertEqual((code, verdict["verdict"]), (0, "agree"))

    def test_recompute_stop_payload_reaches_the_verdict_only_as_null(self):
        ours = dict(self.ours, comparison_stopped={"word": "resolved", "value": 12})
        verdict, code, _ = self.release(ours=ours)
        self.assertEqual((code, verdict["reason"]), (2, "recompute_comparison_stopped"))
        self.assertIsNone(verdict["stages"]["recompute"]["comparison_stopped"])
        self.assertNotIn("resolved", json.dumps(verdict))

    def test_recompute_stop_flag_holds(self):
        ours = dict(self.ours, comparison_stopped=True)
        verdict, code, _ = self.release(ours=ours)
        self.assertEqual((code, verdict["reason"]), (2, "recompute_comparison_stopped"))
        self.assertEqual(verdict["stages"]["comparator"]["status"], "not_run")

    def test_real_recompute_runs_on_the_indexed_roots(self):
        # The synthetic archives' numbers are not the fixture custody's: the pipeline runs end to end and holds.
        verdict, code, out = self.release(fake=False)
        self.assertEqual(verdict["stages"]["recompute"]["status"], "ok")
        self.assertEqual(verdict["stages"]["recompute"]["exit"], 0)
        self.assertIs(verdict["stages"]["recompute"]["comparison_stopped"], False)
        self.assertNotEqual(code, 0)
        self.assertEqual(verdict["verdict"], "hold")
        self.assertIn(verdict["reason"], ("comparator_disagreement", "comparator_refused"))
        members = json.loads((out / "recompute.json").read_text())["members"]
        self.assertEqual(set(members), {"ALPHA", "BETA", "GAMMA"})

    def test_restricted_out_must_be_new_and_outside_checkout_and_custody(self):
        existing = self.root / "exists"
        existing.mkdir()
        cases = ((existing, "restricted_out_exists"), (ROOT / "scratch-release-out", "restricted_out_inside_checkout_or_custody"),
                 (self.custody / rel.RESTRICTED / "x", "restricted_out_inside_checkout_or_custody"))
        for path, reason in cases:
            with self.subTest(reason=reason), self.assertRaises(rel.Refusal) as caught:
                rel.prepare_restricted(path, self.custody)
            self.assertEqual(caught.exception.code, reason)
            self.assertFalse((ROOT / "scratch-release-out").exists())

    def test_cli_prints_the_blinded_verdict(self):
        out = self.root / "cli-out"
        command = [sys.executable, "-B", str(ROOT / "scripts/release_b5.py"), "--custody", str(self.custody),
                   "--window-index", str(self.index), "--pinned-commit", "b" * 40, "--restricted-out", str(out)]
        result = subprocess.run(command, capture_output=True, text=True)
        verdict = json.loads(result.stdout)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(verdict["verdict"], "hold")
        self.assertIsNone(FLOAT.search(result.stdout))
        self.assertEqual(result.stderr, "")

    def test_symlinked_restricted_folder_refuses(self):
        restricted = self.custody / rel.RESTRICTED
        moved = self.root / "moved-restricted"
        restricted.rename(moved)
        restricted.symlink_to(moved, target_is_directory=True)
        verdict, code, _ = self.release()
        self.assertEqual((code, verdict["reason"]), (2, rel.DIFFERS))

    def test_release_bars_are_pinned(self):
        bars = json.loads(rel.RELEASE_BARS.read_text())
        bars["families"]["contrast_j"]["absolute"] = 1000.0
        loose = self.root / "loose-bars.json"
        loose.write_text(json.dumps(bars))
        with mock.patch.object(rel, "RELEASE_BARS", loose):
            verdict, code, _ = self.release(ours=self.disagreeing())
        self.assertEqual((code, verdict["reason"]), (2, "release_bars_differ"))
        self.assertEqual(verdict["stages"]["recompute"]["status"], "not_run")
        self.assertEqual(rel.file_sha256(rel.RELEASE_BARS), rel.RELEASE_BARS_SHA256)
        self.assertNotIn("--bars", rel.main.__code__.co_consts)

    def test_guard_replaced_verdict_never_exits_zero(self):
        with mock.patch.object(rel, "FLOAT_TOKEN", re.compile("agree")):
            verdict, code, _ = self.release()
        self.assertEqual((code, verdict["verdict"], verdict["reason"]), (2, "hold", "verdict_not_structure_only"))

    def test_verdict_carries_only_registered_identifiers(self):
        verdict, _, _ = self.release()
        self.assertEqual(verdict["stages"]["comparator"]["bars_sha256"], rel.RELEASE_BARS_SHA256)
        self.assertNotIn("bar_set", verdict["stages"]["comparator"])
        self.assertLessEqual(set(verdict["stages"]["comparator"]["families"]), rel.FAMILIES)
        verdict, code, _ = self.release(pinned="not_resolvable")
        self.assertEqual((code, verdict["reason"], verdict["pinned_commit"]), (2, "pinned_commit_invalid", None))

    def disagreeing(self):
        ours = copy.deepcopy(self.ours)
        ours["contrasts"][tc.DECODE]["dbar_j"] += 1.0
        return ours

    def test_no_repository_import(self):
        text = (ROOT / "scripts/release_b5.py").read_text()
        self.assertNotRegex(text, r"(?m)^\s*(from|import)\s+(joulewise|scripts|tests)\b")


if __name__ == "__main__":
    unittest.main()
