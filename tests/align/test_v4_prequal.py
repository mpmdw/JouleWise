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
        # PR #686: top-level hf bookkeeping is counted, not compared.
        self.assertEqual(row["hf_cache_bookkeeping_result"], [])
        self.assertEqual(row["hf_cache_bookkeeping_counted"], [".cache/huggingface/download/x.metadata"])

    def test_kit_check_r0_passes_w1_needs_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = prequal.check_kit(ctx(tmp))
            self.assertEqual(row["status"], "pass", row["problems"])
            self.assertIn("R0.reasoning_effort", row["pending_inputs"])
            self.assertFalse([p for p in row["pending_inputs"] if p.startswith("WP11.")])
            self.assertEqual(row["d_identity_folded_sha256"],
                             "a8d1c5c963787dd9dc524912e05d409172124da773d196e8f5123820b4c36b30")
            self.assertEqual(prequal.check_kit(ctx(tmp, stage="w1"))["status"], "fail")

    def test_kit_check_fails_a_filled_wp11_that_does_not_bind_the_pins_at_any_stage(self):
        from scripts import align_v4_kit as kit
        inputs = kit.read_inputs(REPO)
        inputs["WP11"]["identity_unit"]["model_artifact_sha256"] = "f" * 64
        with tempfile.TemporaryDirectory() as tmp, patch.object(kit, "read_inputs", return_value=inputs), \
                patch.object(kit, "build_files", return_value={}):
            row = prequal.check_kit(ctx(tmp))
        self.assertEqual(row["status"], "fail")
        self.assertTrue(any("WP11 D identity" in p for p in row["problems"]), row["problems"])

    def test_kit_check_w1_readiness_includes_r1_sizing(self):
        from scripts import align_v4_kit as kit
        with tempfile.TemporaryDirectory() as tmp, patch.object(kit, "require_ready"):
            row = prequal.check_kit(ctx(tmp, stage="w1"))
        self.assertEqual(row["status"], "fail")
        self.assertIn("sizing_b5.json is not derivable yet", row["require_ready"])


class W1PlanCheck(unittest.TestCase):
    """The R1 kit checks (validate_align_v4_w1_plan.py, L1, fit rule) in the prequal."""

    def test_w1_plan_is_in_the_runner_and_r0_stage_passes_while_r1_is_pending(self):
        self.assertIn("w1-plan", dict(prequal.AIR_CHECKS))
        with tempfile.TemporaryDirectory() as tmp:
            row = prequal.check_w1_plan(ctx(tmp))
        self.assertEqual(row["status"], "pass", row["problems"])
        self.assertTrue(row["w1_plan"].startswith("pending"))
        self.assertEqual(row["fit_rule_planning_span_s"], 26927)

    def test_stage_w1_requires_the_filled_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = prequal.check_w1_plan(ctx(tmp, stage="w1"))
        self.assertEqual(row["status"], "fail")
        self.assertIn("W1 requires the R1-filled", row["problems"][0])

    def test_template_drift_and_a_permissive_validator_fail(self):
        from scripts import validate_align_v4_w1_plan as validator
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(validator, "template_bytes", return_value=b"{}"):
                self.assertIn("drifted", prequal.check_w1_plan(ctx(tmp))["problems"][0])
            with patch.object(validator, "validate", return_value={}):
                self.assertIn("accepted the PENDING_R1 template", prequal.check_w1_plan(ctx(tmp))["problems"][0])

    def test_a_filled_plan_is_validated_against_inputs_and_r1_slots(self):
        from scripts import align_v4_kit as kit
        from tests.align.test_v4_kit import filled_w1_plan, ready_inputs
        inputs, slots = ready_inputs()
        with patch.object(kit, "read_inputs", return_value=inputs), \
                patch.object(kit, "read_r1_slots", return_value=slots), \
                patch.object(kit, "read_w1_plan_bytes", return_value=None):
            plan = json.loads(kit.build_files(REPO)[kit.KIT / "collection_plan.json"])
        filled = filled_w1_plan(inputs, slots, collection_plan=plan)
        from scripts import validate_align_v4_w1_plan as validator
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(kit, "read_inputs", return_value=inputs), \
                patch.object(kit, "read_r1_slots", return_value=slots), \
                patch.object(kit, "read_w1_plan", return_value=filled), \
                patch.object(validator, "template_bytes", side_effect=lambda p: (REPO / kit.KIT / "night_plan.template.json").read_bytes()):
            # The collection plan on disk is the committed one; bind to the ready roster instead.
            real = Path.read_bytes
            def read_bytes(path):
                if path == REPO / kit.KIT / "collection_plan.json":
                    return json.dumps(plan).encode()
                return real(path)
            with patch.object(Path, "read_bytes", read_bytes):
                row = prequal.check_w1_plan(ctx(tmp, stage="w1"))
                self.assertEqual(row["w1_plan"]["status"], "VALID", row)
                self.assertEqual(row["w1_plan"]["programmed_span_s"], 26927)
                self.assertTrue(any("sizing_b5.json missing" in p for p in row["problems"]), row["problems"])
                filled["align_v4"]["B_D"] = 7168
                row = prequal.check_w1_plan(ctx(tmp, stage="w1"))
                self.assertTrue(row["w1_plan"].startswith("REFUSED"), row["w1_plan"])


class SiblingLoadReference(unittest.TestCase):
    """R0 load-reference follow-ups (PR #686): the sibling has its own NLL entry."""

    def table(self):
        return json.loads(prequal.SIBLING_NLL_REFERENCE_PATH.read_text())

    def test_sibling_table_is_a_valid_explicit_reference_entry(self):
        from joulewise.align import r0
        table = r0.validate_references(self.table())
        entry, = table["models"]
        self.assertEqual((entry["label"], entry["mode"]), (prequal.SIBLING_NLL_LABEL, "reference"))
        self.assertEqual(entry["revision"], prequal.SIBLING_REVISION)
        self.assertEqual(entry["fixture_sha256"], json.loads(prequal.REFERENCE_PATH.read_text())["nll_prompt"]["sha256"])
        self.assertEqual(entry["reference"]["nll_nats_per_token"], 0.4669)

    def test_verdict_keys_on_the_sibling_revision_never_d(self):
        from joulewise.align import r0
        entry = self.table()["models"][0]
        losses = [b for b in entry["reference"]["bins256"] for _ in range(256)]
        ok = r0.nll_verdict(losses, revision=prequal.SIBLING_REVISION, fixture_sha256=entry["fixture_sha256"],
                            references=self.table())
        self.assertEqual((ok["status"], ok["entry"]), ("pass", prequal.SIBLING_NLL_LABEL))
        d_like = r0.nll_verdict([11.06] * 2048, revision=prequal.SIBLING_REVISION,
                                fixture_sha256=entry["fixture_sha256"], references=self.table())
        self.assertEqual(d_like["status"], "fail")
        borrowed = r0.nll_verdict(losses, revision="815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9",
                                  fixture_sha256=entry["fixture_sha256"], references=self.table())
        self.assertEqual(borrowed["reason"], "no_reference")

    def test_sibling_backend_names_its_own_revision(self):
        class FakeMlx:
            def __init__(self, tag, directory, shade, guard):
                self.config = SimpleNamespace(model=SimpleNamespace(revision="815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9"))
        info = {"dir": Path("/x"), "source": "/y", "revision": prequal.SIBLING_REVISION, "bytes": 1,
                "substitutions": {}, "layers": 24}
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(prequal, "build_sibling_dir", return_value=info), \
                patch.object(prequal, "_r0_mlx", return_value=SimpleNamespace(MlxBackend=FakeMlx)), \
                patch.object(prequal.Context, "shade_cache", return_value=Path("/s")):
            backend = prequal.SiblingBackend(ctx(tmp))
        from joulewise.align import r0
        self.assertEqual(r0.model_revision(backend), prequal.SIBLING_REVISION)

    def result(self, *, nll="pass", entry=prequal.SIBLING_NLL_LABEL, generation=True, outcome="fail"):
        ref = json.loads(prequal.REFERENCE_PATH.read_text())
        attempt = {"decode": "greedy", "status": outcome, "problems": [] if outcome == "pass" else ["no_tool_call"],
                   "prompt_sha256": "p" * 64, "envelopes": {"attempted_envelopes": 0},
                   "turn": {"prompt_token_ids": [1, 2, 3], "tokens": 17}}
        return {"nll_prompt_sha256": ref["nll_prompt"]["sha256"], "nll_nats_per_token": 0.47,
                "short": {"prompt_token_ids": [], "tokens": 3, "visible_text": "42"},
                "nll_verdict": {"status": nll, "reason": None if nll == "pass" else "mean_outside_tolerance",
                                "mode": "reference", "entry": entry, "model_revision": prequal.SIBLING_REVISION},
                "generation": ({"status": outcome, "problems": attempt["problems"], "attempts": [attempt],
                                "requested_tool": "end_task", "retried": False, "decode": "greedy", "tokens": 17}
                               if generation else None),
                "status": "fail", "coherent": True,
                "tool_round_trip": {"succeeded": True, "error": None}}

    def check(self, result):
        from joulewise.align import r0
        seen = {}
        def fake(backend, **kwargs):
            seen.update(kwargs)
            return result
        with tempfile.TemporaryDirectory() as tmp, patch.object(r0, "load_coherence", fake), \
                patch.object(prequal, "_model_backend", return_value=object()):
            row = prequal.check_load(ctx(tmp, model_backend="sibling"))
        self.assertEqual(seen["references"]["models"][0]["label"], prequal.SIBLING_NLL_LABEL)
        return row

    def test_load_passes_on_sibling_nll_pass_and_end_to_end_generation_even_if_its_outcome_fails(self):
        row = self.check(self.result())
        self.assertEqual(row["status"], "pass", row["problems"])
        self.assertTrue(row["generation_outcome_is_diagnostic"])
        self.assertEqual(row["generation_outcome"]["status"], "fail")

    def test_load_requires_the_sibling_nll_verdict_to_pass(self):
        row = self.check(self.result(nll="fail"))
        self.assertEqual(row["status"], "fail")
        self.assertIn("sibling NLL verdict fail", row["problems"][0])
        row = self.check(self.result(entry="D"))
        self.assertIn("NLL verdict did not use the sibling's own reference entry", row["problems"])

    def test_load_requires_generation_to_run_end_to_end(self):
        self.assertIn("generation check did not run", self.check(self.result(generation=False))["problems"])
        broken = self.result()
        broken["generation"]["attempts"][0]["turn"]["tokens"] = 0
        broken["generation"]["attempts"][0].pop("envelopes")
        problems = self.check(broken)["problems"]
        self.assertIn("attempt 0: no decoded tokens", problems)
        self.assertIn("attempt 0: tool_envelopes accounting missing", problems)
        unresolved = self.result()
        unresolved["generation"]["attempts"][0]["problems"] = ["schema_ref_unresolved:x"]
        self.assertIn("attempt 0: schema validation could not run", self.check(unresolved)["problems"])

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
