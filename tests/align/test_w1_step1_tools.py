"""Synthetic Git and subprocess witnesses for the W1 step-1 runbook tools."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[2] / "docs/run_reports/2026-11-24-w1-step1"
RECEIPT_STOP = "align_v4_kit: registration_receipt is pending or malformed"
MISMATCH = "align_v4_kit: inputs.R1.I_D 431.1234567 differs from r1_slots.slots.I_D 457.9876543"
PIN_SOURCE = "joulewise/align/apple/v4_registration.py"


class GitFixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "--quiet")
        self.git("config", "user.email", "fixture@example.test")
        self.git("config", "user.name", "Synthetic Fixture")
        self.git("config", "core.autocrlf", "false")

    def git(self, *argv):
        return subprocess.check_output(["git", *argv], cwd=self.repo, stderr=subprocess.PIPE).decode().rstrip("\n")

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def commit(self, label):
        self.git("add", "-A")
        self.git("commit", "--quiet", "-m", label)
        return self.git("rev-parse", "HEAD")

    def component_file(self, **heads):
        path = self.root / "heads.json"
        path.write_text(json.dumps(heads), encoding="utf-8")
        return path


class Step1Tests(GitFixture):
    def setUp(self):
        super().setUp()
        spec = importlib.util.spec_from_file_location("w1_step1", TOOLS / "w1_step1.py")
        self.step1 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.step1)
        self.paths = tuple(f"source{i}.py" for i in range(10))
        for name in (*self.paths, "substitute.py"):
            self.write(name, "# synthetic\n")
        self.write(PIN_SOURCE, f"R1_EXECUTED_SOURCES = {self.paths!r}\n")
        digest = "a" * 64
        self.write(self.step1.INPUTS, json.dumps({"R0": {"reasoning_effort": "synthetic"},
                                                 "R1": {"thermal_policy": {"sensors": {"enabled": True}}}}))
        self.write(self.step1.RUNTIME, json.dumps({"sensors": {"fan_keys": ["synthetic"], "r0_sha256": digest}}))
        self.write("scripts/validate_align_v4_w1_plan.py", "")
        self.write(self.step1.TRACE, "{}\n")
        self.write("scripts/align_v4_dynamic_trace.py",
                   "import sys\nfrom pathlib import Path\n"
                   "Path(sys.argv[2]).write_text('{\"scenarios\": {\"synthetic\": {\"ok\": true}}}')\n")
        self.write("tests/__init__.py", "")
        self.write("tests/hazards/__init__.py", "")
        self.write("tests/hazards/refusal_census.py", "")
        self.pin = self.commit("synthetic frozen sources")
        self.seconds = self.root / "seconds.json"
        self.seconds.write_text(json.dumps([10] * 18), encoding="utf-8")
        self.out = self.root / "out"
        self.census = self.root / "census.py"
        self.census.write_text(
            "import subprocess, sys\n"
            "rev = sys.argv[sys.argv.index('--rev') + 1]\n"
            "def git(*args):\n"
            "    return subprocess.check_output(['git', *args])\n"
            "assert git('cat-file', '-t', rev).strip() == b'tree'\n"
            "assert git('show', rev + ':generated.py') == b'# generated\\n'\n"
            f"assert b'synthetic' in git('show', rev + ':{self.step1.TRACE}')\n",
            encoding="utf-8",
        )

    def install_kit(self, message=RECEIPT_STOP, exit_code=1, *, initial=False):
        condition = "True" if initial else "'--check' in sys.argv"
        self.write("scripts/align_v4_kit.py",
                   "import sys\nfrom pathlib import Path\n"
                   f"if {condition}:\n"
                   f"    print({message!r}, file=sys.stderr)\n"
                   f"    sys.exit({exit_code})\n"
                   "Path('generated.py').write_text('# generated\\n')\n")
        return self.commit("synthetic kit")

    def invoke(self, *extra, heads=None):
        heads = heads or self.component_file(**{"826": self.pin})
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr), patch.object(self.step1, "build_plan"):
            status = self.step1.main([
                "--repo", str(self.repo), "--r0-record-sha256", "a" * 64,
                "--member-seconds", str(self.seconds), "--plan-id", "synthetic",
                "--out", str(self.out), "--pin", self.pin, "--component-heads", str(heads), *extra,
            ])
        raw = (self.out / "step1-receipt.json").read_text(encoding="utf-8")
        return status, json.loads(raw), stdout.getvalue() + stderr.getvalue() + raw

    def test_id_mismatch_is_redacted_at_check_and_in_subprocess_wrapper(self):
        for initial in (False, True):
            with self.subTest(initial=initial):
                self.install_kit(MISMATCH, initial=initial)
                status, receipt, all_output = self.invoke()
                self.assertEqual(status, 2)
                self.assertNotIn("431.1234567", all_output)
                self.assertNotIn("457.9876543", all_output)
                self.assertEqual(receipt["refusal"]["exception"], "ValueError")
                self.assertEqual(receipt["refusal"]["fields"], ["inputs.R1.I_D", "r1_slots.slots.I_D"])
                self.git("restore", ".")
                (self.repo / "generated.py").unlink(missing_ok=True)

    def test_opaque_child_error_is_hashed(self):
        self.install_kit("arbitrary synthetic secret", initial=True)
        status, receipt, all_output = self.invoke()
        self.assertEqual(status, 2)
        self.assertNotIn("arbitrary synthetic secret", all_output)
        self.assertRegex(receipt["refusal"]["message_sha256"], r"^[0-9a-f]{64}$")

    def test_generated_tree_is_censused_after_trace_with_real_index_untouched(self):
        head = self.install_kit()
        tree = self.git("write-tree")
        status, receipt, _ = self.invoke("--trace", "--reader-census", str(self.census))
        self.assertEqual(status, 0)
        self.assertEqual(receipt["result"], "READY_FOR_LEAD_REVIEW")
        self.assertEqual(receipt["missing"], [])
        self.assertNotEqual(receipt["reader_census_tree"], tree)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("write-tree"), tree)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    def test_missing_evidence_is_partial(self):
        self.install_kit()
        status, receipt, _ = self.invoke()
        self.assertEqual(status, 1)
        self.assertEqual(receipt["result"], "PARTIAL")
        self.assertCountEqual(receipt["missing"], ["trace", "reader_census"])

    def test_success_exit_or_lookalike_receipt_stop_is_refused(self):
        for message, code in ((RECEIPT_STOP, 0), ("unexpected: " + RECEIPT_STOP, 1),
                              (RECEIPT_STOP + "\nanother failure", 1)):
            with self.subTest(message=message, code=code):
                self.install_kit(message, code)
                status, receipt, _ = self.invoke("--trace", "--reader-census", str(self.census))
                self.assertEqual(status, 2)
                self.assertEqual(receipt["result"], "PARTIAL")
                self.assertIn("registration_receipt_stop", receipt["missing"])
                self.git("restore", ".")
                (self.repo / "generated.py").unlink(missing_ok=True)

    def test_pin_inventory_cannot_swap_a_modified_path_for_an_unchanged_one(self):
        self.install_kit()
        self.write(self.paths[0], "# changed frozen source\n")
        self.write(PIN_SOURCE, f"R1_EXECUTED_SOURCES = {('substitute.py', *self.paths[1:])!r}\n")
        self.commit("attempt to swap inventory")
        status, receipt, _ = self.invoke()
        self.assertEqual(status, 2)
        self.assertIn(self.paths[0], receipt["refusal"]["fields"])
        self.assertFalse((self.repo / "generated.py").exists())

    def test_missing_component_is_refused_during_preflight(self):
        self.git("checkout", "--quiet", "--detach", self.pin)
        self.write("component.txt", "component\n")
        component = self.commit("unmerged component")
        self.git("checkout", "--quiet", "--detach", self.pin)
        self.install_kit()
        status, receipt, _ = self.invoke(heads=self.component_file(**{"839": component}))
        self.assertEqual(status, 2)
        self.assertEqual(receipt["refusal"]["code"], "COMPONENT_NOT_IN_HEAD")
        self.assertFalse((self.repo / "generated.py").exists())


class AcceptedDiffTests(GitFixture):
    def setUp(self):
        super().setUp()
        self.source = "tests/align/test_w1_prequal.py"
        self.original = "# base\n" + "\n".join(f"# context {i}" for i in range(12)) + "\nVALUE = 0\n"
        self.write(self.source, self.original)
        self.base = self.commit("base")
        self.write(self.source, self.original.replace("# base", "# presign edit"))
        self.presign = self.commit("presign")
        self.git("checkout", "--quiet", "--detach", self.base)
        self.component_bytes = self.original.replace("VALUE = 0", "VALUE = 1")
        self.write(self.source, self.component_bytes)
        self.component = self.commit("component")
        self.git("checkout", "--quiet", "--detach", self.presign)
        self.git("merge", "--quiet", "--no-edit", self.component)
        self.merged = self.git("rev-parse", "HEAD")

    def proof(self, *extra, heads=None):
        heads = heads or self.component_file(**{"886": self.component})
        result = subprocess.run([
            sys.executable, "-B", str(TOOLS / "accepted_diff.py"), "HEAD", self.base,
            "--presign", self.presign, "--component-heads", str(heads), *extra,
        ], cwd=self.repo, capture_output=True, text=True)
        self.assertTrue(result.stdout, result.stderr)
        report = json.loads(result.stdout)
        return result.returncode, {row["path"]: row for row in report["paths"]}

    def test_clean_merge_reconstructs_presign_and_component(self):
        status, rows = self.proof()
        self.assertEqual(status, 0)
        self.assertEqual(rows[self.source]["result"], "reconstructed-equal")

    def test_planted_load_tests_is_a_residual_until_explicitly_accepted(self):
        planted = "def load_tests(loader, tests, pattern):\n    return loader.suiteClass()\n\n"
        self.write(self.source, planted + (self.repo / self.source).read_text(encoding="utf-8"))
        self.commit("plant empty test suite")
        status, rows = self.proof()
        self.assertEqual(status, 1)
        self.assertEqual(rows[self.source]["result"], "residual")
        self.assertIn("PR #886", rows[self.source]["owners"])
        self.assertEqual(self.proof("--accept-residual", self.source)[0], 0)

    def test_component_blob_that_drops_presign_edit_is_a_residual(self):
        self.write(self.source, self.component_bytes)
        self.commit("erase presign edit")
        status, rows = self.proof()
        self.assertEqual(status, 1)
        self.assertEqual(rows[self.source]["result"], "residual")

    def test_named_ranges_cover_exact_bytes_and_modes_for_nul_delimited_names(self):
        spaced = "a file\twith\nwhitespace"
        self.write(spaced, "synthetic\n")
        step = self.commit("step 1")
        self.write(self.source, (self.repo / self.source).read_text(encoding="utf-8") + "# PR edit\n")
        pr = self.commit("PR change")
        ranges = ("--step1", f"{self.merged}..{step}", "--pr973", f"{step}..{pr}")
        self.assertEqual(self.proof(*ranges)[0], 0)
        (self.repo / spaced).chmod(0o755)
        self.commit("unapproved executable mode")
        status, rows = self.proof(*ranges)
        self.assertEqual(status, 1)
        self.assertEqual(rows[spaced]["result"], "residual")

    def test_pr839_supersedes_pr826_only_on_shared_paths(self):
        self.git("checkout", "--quiet", "--detach", self.component)
        self.write("only-826.txt", "retained\n")
        p826 = self.commit("PR 826")
        self.git("checkout", "--quiet", "--detach", self.base)
        self.write(self.source, self.original.replace("VALUE = 0", "VALUE = 2"))
        p839 = self.commit("PR 839")
        self.git("merge", "--quiet", "-s", "ours", "--no-edit", p826, self.presign)
        self.write(self.source, self.original.replace("# base", "# presign edit").replace("VALUE = 0", "VALUE = 2"))
        self.write("only-826.txt", "retained\n")
        self.commit("apply authoritative shared change")
        status, rows = self.proof(heads=self.component_file(**{"826": p826, "839": p839}))
        self.assertEqual(status, 0)
        self.assertEqual(rows[self.source]["owners"], ["presign", "PR #839"])
        self.assertEqual(rows["only-826.txt"]["owners"], ["PR #826"])

    def test_only_exact_derived_bytes_can_be_classified_as_step1_generated(self):
        self.write("derived.txt", "generated\n")
        self.write("wrong.txt", "altered\n")
        self.write("inputs.json", "passthrough\n")
        self.commit("candidate generation")
        spec = importlib.util.spec_from_file_location("accepted_diff", TOOLS / "accepted_diff.py")
        proof = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = proof
        self.addCleanup(sys.modules.pop, spec.name)
        spec.loader.exec_module(proof)
        kit = SimpleNamespace(INPUTS=Path("inputs.json"), R1_SLOTS=Path("slots.json"),
                              R1_PLANNING_RELEASE=Path("release.json"), W1_PLAN=Path("plan.json"),
                              build_files=lambda root: {Path("derived.txt"): b"generated\n",
                                                        Path("wrong.txt"): b"generated\n",
                                                        Path("inputs.json"): b"passthrough\n"})
        stdout = io.StringIO()
        with redirect_stdout(stdout), patch.object(proof, "load_kit", return_value=kit):
            status = proof.main(["HEAD", self.base, "--repo", str(self.repo), "--presign", self.presign,
                                 "--component-heads", str(self.component_file(**{"886": self.component})),
                                 "--kit-root", str(self.repo)])
        rows = {row["path"]: row["result"] for row in json.loads(stdout.getvalue())["paths"]}
        self.assertEqual(status, 1)
        self.assertEqual(rows["derived.txt"], "step1-generated")
        self.assertEqual(rows["wrong.txt"], "residual")
        self.assertEqual(rows["inputs.json"], "residual")
