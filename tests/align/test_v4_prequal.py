"""Off-Mac prequalification: fail-closed runner, config/pin/kit checks, launcher dry run.

Stdlib only by default. The tokenizer-backed checks run when mlx_lm is installed
and JW_PREQUAL_HF names a cache holding D's verified non-weight files.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align import prequal

REPO = Path(__file__).resolve().parents[2]


def ctx(tmp, **kwargs):
    return prequal.Context(repo=REPO, work=Path(tmp) / "work", **kwargs)


class FakeApi:
    def __init__(self, pins, *, mutate=lambda siblings: siblings, sha=None):
        self.pins, self.mutate, self.sha = pins, mutate, sha

    def model_info(self, repo, revision=None, files_metadata=False):
        siblings = [SimpleNamespace(rfilename=name, size=pin["size"], blob_id=pin["git_blob_sha1"],
                                    lfs=SimpleNamespace(sha256=pin["sha256"]) if pin.get("sha256") else None)
                    for name, pin in self.pins["files"].items()]
        return SimpleNamespace(sha=self.sha or revision, siblings=self.mutate(siblings))


class RunnerSemantics(unittest.TestCase):
    def run_with(self, checks, model=(), backend="none"):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(prequal, "AIR_CHECKS", checks), patch.object(prequal, "MODEL_CHECKS", model):
            return prequal.run(ctx(tmp, model_backend=backend))

    def test_all_pass_is_pass(self):
        report = self.run_with((("a", lambda c: {"status": "pass"}), ("b", lambda c: {"status": "diagnostic"})))
        self.assertEqual(report["status"], "pass")

    def test_exception_is_failure_not_skip(self):
        def boom(c):
            raise OSError("network down")
        report = self.run_with((("a", boom), ("b", lambda c: {"status": "pass"})))
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["failed"], ["a"])
        self.assertIn("network down", report["checks"][0]["error"])

    def test_invalid_status_fails(self):
        report = self.run_with((("a", lambda c: {"status": "ok"}),))
        self.assertEqual(report["status"], "fail")

    def test_no_model_backend_is_incomplete(self):
        report = self.run_with((("a", lambda c: {"status": "pass"}),),
                               model=(("model-load", lambda c: {"status": "pass"}),))
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["not_run"], ["model-load"])

    def test_model_checks_blocked_after_failed_load(self):
        with patch.dict(prequal.BACKENDS, {"fake": lambda c: None}):
            report = self.run_with((), model=(("model-load", lambda c: {"status": "fail"}),
                                              ("load", lambda c: {"status": "pass"})), backend="fake")
        self.assertEqual([r["status"] for r in report["checks"]], ["fail", "not_run"])
        self.assertEqual(report["status"], "fail")

    def test_offline_skips_network_check_and_is_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(prequal, "AIR_CHECKS", (("d-pins", lambda c: {"status": "pass"}),)), \
                patch.object(prequal, "MODEL_CHECKS", ()):
            report = prequal.run(ctx(tmp, offline=True))
        self.assertEqual(report["status"], "incomplete")

    def test_report_lists_the_mac_only_boundary_and_writes_once(self):
        report = self.run_with((("a", lambda c: {"status": "pass"}),))
        for key in ("r0.smc", "r0.ladder", "r0.memory", "r0.long-decode", "r0.load (D numerics)"):
            self.assertIn(key, report["mac_only"])
        with tempfile.TemporaryDirectory() as tmp:
            out = prequal.write(report, Path(tmp) / "out")
            self.assertIn("Stays on the measurement Mac", (out / "prequal.md").read_text())
            json.loads((out / "prequal.json").read_text())
            with self.assertRaises(FileExistsError):
                prequal.write(report, out)


class ConfigPinKitChecks(unittest.TestCase):
    def test_real_r0_config_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = prequal.check_r0_config(ctx(tmp))
        self.assertEqual(row["status"], "pass", row["problems"])

    def test_tampered_r0_config_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "configs/align/v4").mkdir(parents=True)
            config = json.loads((REPO / "configs/align/v4/r0_desk.json").read_text())
            config["models"]["D"]["source"] = "/Users/edr/jw_models/other"
            (repo / "configs/align/v4/r0_desk.json").write_text(json.dumps(config))
            row = prequal.check_r0_config(prequal.Context(repo=repo, work=Path(tmp) / "w"))
        self.assertEqual(row["status"], "fail")

    def test_d_pins_against_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = ctx(tmp)
            pins = c.pins()
            c._hf_api = FakeApi(pins)
            self.assertEqual(prequal.check_d_pins(c)["status"], "pass")
            c._hf_api = FakeApi(pins, sha="0" * 40)
            self.assertEqual(prequal.check_d_pins(c)["status"], "fail")
            def grow(siblings):
                siblings[0].size += 1
                return siblings + [SimpleNamespace(rfilename="extra.bin", size=1, blob_id="0", lfs=None)]
            c._hf_api = FakeApi(pins, mutate=grow)
            row = prequal.check_d_pins(c)
            self.assertEqual(row["status"], "fail")
            self.assertTrue(any("extra.bin" in p for p in row["problems"]))
            def bad_lfs(siblings):
                for s in siblings:
                    if s.lfs:
                        s.lfs = SimpleNamespace(sha256="f" * 64)
                return siblings
            c._hf_api = FakeApi(pins, mutate=bad_lfs)
            self.assertEqual(prequal.check_d_pins(c)["status"], "fail")

    def test_pin_verifier_selftest(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = prequal.check_pin_verifier(ctx(tmp))
        self.assertEqual(row["status"], "pass", row["problems"])
        self.assertTrue(row["hf_cache_bookkeeping_result"])

    def test_kit_check_r0_passes_w1_needs_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = prequal.check_kit(ctx(tmp))
            self.assertEqual(row["status"], "pass", row["problems"])
            self.assertIn("R0.reasoning_effort", row["pending_inputs"])
            self.assertEqual(prequal.check_kit(ctx(tmp, stage="w1"))["status"], "fail")

    def test_non_weight_pins_use_blob_only_without_lfs(self):
        pins = json.loads(prequal.PINS_PATH.read_text())
        self.assertTrue(pins["files"]["tokenizer.json"]["sha256"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "f"
            path.write_bytes(b"hello\n")
            self.assertEqual(prequal.git_blob_sha1(path), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_example_values_satisfy_schema_shapes(self):
        root = {"$defs": {"Kind": {"enum": ["a", "b"]}}}
        self.assertEqual(prequal._example({"$ref": "#/$defs/Kind"}, root), "a")
        self.assertEqual(prequal._example({"anyOf": [{"type": "null"}, {"type": "integer"}]}, root), 3)
        self.assertEqual(prequal._example({"type": "array", "items": {"type": "boolean"}}, root), [True])
        self.assertEqual(prequal._example({"type": "object", "properties": {"x": {"type": "number"}}}, root),
                         {"x": 1.5})


def _main_launcher():
    try:
        subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", "origin/main:scripts/launch_align_r0.py"],
                       check=True, capture_output=True)
        return "origin/main"
    except (OSError, subprocess.CalledProcessError):
        return None


@unittest.skipUnless(_main_launcher(), "origin/main launcher not available in this clone")
class LauncherDryRun(unittest.TestCase):
    """The 2026-11-06 venv bug class: the LaunchAgent must exec the unresolved venv python."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.venv = base / "venv"
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(self.venv)], check=True)
        self.python = self.venv / "bin/python"

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, **kwargs):
        c = prequal.Context(repo=REPO, work=Path(self.tmp.name) / "work", python_bin=str(self.python),
                            stack={}, **kwargs)
        return prequal.check_launcher(c)

    def test_real_launcher_keeps_the_venv(self):
        row = self.run_check(launcher_ref=_main_launcher())
        self.assertEqual(row["status"], "pass", row.get("problems"))
        self.assertEqual(row["runner_json"][0], os.path.abspath(self.python))
        self.assertTrue(row["interpreter"]["is_symlink"])
        self.assertEqual(Path(row["interpreter"]["prefix"]).resolve(), self.venv.resolve())

    def test_resolving_launcher_is_caught(self):
        out = Path(self.tmp.name) / "bad"
        out.mkdir()
        for name in ("launch_align_r0.py", "run_align_r0_launchagent.sh"):
            data = subprocess.run(["git", "-C", str(REPO), "show", f"origin/main:scripts/{name}"],
                                  check=True, capture_output=True).stdout
            (out / name).write_bytes(data)
        text = (out / "launch_align_r0.py").read_text()
        broken = text.replace("args.python_bin = Path(os.path.abspath(args.python_bin.expanduser()))",
                              "args.python_bin = args.python_bin.expanduser().resolve()")
        self.assertNotEqual(text, broken)
        (out / "launch_align_r0.py").write_text(broken)
        row = self.run_check(launcher=str(out / "launch_align_r0.py"))
        self.assertEqual(row["status"], "fail")

    def test_missing_launcher_fails_closed(self):
        with patch.object(prequal, "_launcher_files", side_effect=FileNotFoundError("absent")):
            with tempfile.TemporaryDirectory() as tmp, \
                    patch.object(prequal, "AIR_CHECKS", (("launcher", prequal.check_launcher),)), \
                    patch.object(prequal, "MODEL_CHECKS", ()):
                report = prequal.run(ctx(tmp))
        self.assertEqual(report["status"], "fail")


class Cli(unittest.TestCase):
    def test_subset_is_incomplete_exit_3_and_output_must_be_new(self):
        script = REPO / "scripts/align_v4_prequal.py"
        spec = importlib.util.spec_from_file_location("prequal_cli", script)
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(cli.main(["--output", str(out), "--only", "r0-config"]), 3)
            self.assertEqual(json.loads((out / "prequal.json").read_text())["status"], "incomplete")
            with self.assertRaises(SystemExit):
                cli.main(["--output", str(out), "--only", "r0-config"])
            with self.assertRaises(SystemExit):
                cli.main(["--output", str(Path(tmp) / "x"), "--only", "nope"])


def _tokenizer_ready():
    hf = os.environ.get("JW_PREQUAL_HF")
    return bool(hf) and importlib.util.find_spec("mlx_lm") is not None and importlib.util.find_spec("pydantic") is not None


@unittest.skipUnless(_tokenizer_ready(), "needs mlx_lm, SHADE deps and JW_PREQUAL_HF with D's non-weight files")
class TokenizerTier(unittest.TestCase):
    """Reproduces the measurement Mac's R0 token IDs from D's pinned tokenizer files."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.ctx = prequal.Context(repo=REPO, work=Path(cls.tmp.name), hf_cache=os.environ["JW_PREQUAL_HF"],
                                  offline=os.environ.get("JW_PREQUAL_OFFLINE") == "1")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_nll_fixture_matches_mac(self):
        row = prequal.check_nll_fixture(self.ctx)
        self.assertEqual(row["status"], "pass", row["problems"])

    def test_tool_roundtrip_reproduces_mac_second_prompt(self):
        row = prequal.check_tool_roundtrip(self.ctx)
        self.assertEqual(row["status"], "pass", row["problems"])

    def test_template_rewrites_runs_without_model(self):
        self.assertEqual(prequal.check_template_rewrites(self.ctx)["status"], "diagnostic")


if __name__ == "__main__":
    unittest.main()
