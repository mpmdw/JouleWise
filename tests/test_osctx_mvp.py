"""Offline OSCTX production-wrapper, bundle, schedule, and statistic checks."""
from __future__ import annotations

import copy
from contextlib import redirect_stderr
import io
import json
import math
from pathlib import Path
import plistlib
import shlex
import shutil
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from scripts.diagnostics.osctx_mvp import analyze, cell, common, runner

FIXTURES = Path(__file__).parent / "fixtures" / "osctx_mvp"


def make_bundle(parent: Path, name: str, fixture="bench_smoke", *, energy=None, rate=None, token_offset=0):
    bundle = parent / name
    bundle.mkdir(parents=True)
    source = FIXTURES / fixture
    summary = json.loads((source / "summary_metrics.json").read_text())
    if energy is not None:
        summary["energy_output_token_j"] = energy
        summary["idle_subtracted_energy_j"] = energy * 512
    if rate is not None:
        summary["inter_token_throughput_tokens_s"] = rate
    (bundle / "summary_metrics.json").write_text(json.dumps(summary))
    shutil.copy(FIXTURES / "bench_smoke" / "power_trace.csv", bundle / "power_trace.csv")
    shutil.copy(FIXTURES / "bench_smoke" / "events.jsonl", bundle / "events.jsonl")
    (bundle / "outputs").mkdir()
    (bundle / "outputs" / "tokens.jsonl").write_text("".join(json.dumps({"index": n, "token_id": n + token_offset}) + "\n" for n in range(512)))
    return bundle


def make_cell(parent: Path, config, stage, block, arm, energies, rates=None, *, fixture="bench_smoke", token_offset=0):
    directory = parent / f"{block}.1.{arm}.a1"
    directory.mkdir()
    runs = []
    for number, energy in enumerate(energies, 1):
        bundle = make_bundle(directory, f"bundle-{number}", fixture, energy=energy,
                             rate=(rates or [84.] * len(energies))[number-1], token_offset=token_offset)
        runs.append({"bundle": str(bundle), "child": {"pid": 700 + number}})
    record = {"stage": stage, "state": "A" if stage == "stage0" else "U", "context": arm,
              "pid": 500, "cell_id": 1, "runs": runs, "cpu": [{"seconds": 5.1}], "allow_pids": [], "flags": [], "interrupted": False}
    (directory / "cell.json").write_text(json.dumps(record))
    (directory / "done.json").write_text(json.dumps({"ok": True, "interrupted": False}))
    return directory


class OSCTXTests(unittest.TestCase):
    def setUp(self):
        self.config = common.load_config()

    def test_williams_schedule_and_stage_sizes(self):
        orders = common.williams_orders(self.config["seed"], "U1")
        self.assertEqual(len(set(orders)), 6)
        self.assertEqual(orders, common.williams_orders(self.config["seed"], "U1"))
        self.assertNotEqual(orders, common.williams_orders(self.config["seed"]+1, "U1"))
        self.assertEqual([b["arms"] for b in common.blocks(self.config, "stage0")],
                         [["I", "SH"], ["SH", "I"], ["I", "SH"]])
        self.assertEqual(sum(len(b["arms"]) for b in common.blocks(self.config, "U1")), 21)
        self.assertEqual(sum(len(b["arms"]) for b in common.blocks(self.config, "U2")), 18)
        self.assertEqual([b["state"] for b in common.blocks(self.config, "S")], ["U"]*3+["S"]*3+["U"]*3)

    def test_rendered_zsh_exec_and_shell_detachment(self):
        with tempfile.TemporaryDirectory() as temp:
            actions = runner.plan(Path(temp), common.DEFAULT_CONFIG, self.config, "U1", "/python")
            d = next(a for a in actions if a["context"] == "D")
            sh = next(a for a in actions if a["context"] == "SH")
            self.assertEqual(sh["start"][:3], ["nohup", "caffeinate", "-is"])
            self.assertEqual(sh["start"][3:5], ["/bin/zsh", "-c"])
            self.assertIn("--python /python", sh["start"][5])
            with Path(d["cell_dir"], "job.plist").open("rb") as stream:
                pl = plistlib.load(stream)
            self.assertEqual(pl["ProgramArguments"][:2], ["/bin/zsh", "-c"])
            self.assertEqual(pl.get("ProcessType"), None)
            self.assertEqual(pl["WorkingDirectory"], str(runner.ROOT))
            with patch("subprocess.Popen") as popen:
                runner.SystemBackend().spawn_shell(sh["start"], Path(sh["cell_dir"]))
                self.assertTrue(popen.call_args.kwargs["start_new_session"])

    def test_runs_per_cell_defaults_to_two(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config.json"
            config = copy.deepcopy(self.config)
            config.pop("runs_per_cell")
            path.write_text(json.dumps(config))
            self.assertEqual(common.load_config(path)["runs_per_cell"], {stage: 2 for stage in common.STAGES})

    def test_materialized_config_only_two_edits_and_hashes(self):
        source = cell.ROOT / self.config["source_config"]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "run.json"
            hashes = cell.materialize_config(source, target, "osctx-stage0-01-i-r1")
            original, modified = json.loads(source.read_text()), json.loads(target.read_text())
            self.assertEqual(modified.pop("run_id"), "osctx-stage0-01-i-r1")
            self.assertEqual(modified["run_metadata"].pop("tags"), cell.TAGS)
            original.pop("run_id")
            original["run_metadata"].pop("tags")
            self.assertEqual(modified, original)
            self.assertEqual(hashes["source_sha256"], cell.sha256(source))
            self.assertEqual(hashes["materialized_sha256"], cell.sha256(target))

    def test_wrapper_command_and_settle(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            cmd = cell.production_command("/python", out / "run-r1.json", out)
            self.assertEqual(cmd, ["/python", "-m", "joulewise", "run", str(out / "run-r1.json"),
                                   "--runs-dir", str(out / "runs"), "--post-window-sampling-dwell-s", "60"])
            cfg = copy.deepcopy(self.config)
            cfg["segments"].update({"cpu_seconds": 0, "cpu_iterations": 1, "cpu_repeats": 3, "settle_seconds": 60})
            calls = []
            class Fake:
                def command(self, argv): return {"stdout": "", "returncode": 0}
                def idle(self): return 700
                def display(self): return "on"
                def sleep(self, seconds): calls.append(("sleep", seconds))
                def preread(self, model): calls.append(("preread", model)); return []
                def production(self, argv, log): calls.append(("production", argv)); return {"pid": 123, "returncode": 0}
                def cpu_probe(self, iterations): calls.append(("cpu", iterations)); return 1
            cell.run(out, cfg, "A", "I", 1, stage="stage0", backend=Fake(), python="/python")
            self.assertEqual([x[0] for x in calls], ["preread", "production", "production", "cpu", "cpu", "cpu", "sleep"])
            self.assertEqual(calls[-1], ("sleep", 60))
            self.assertTrue((out / "done.json").exists())

    def test_paired_t_and_verdict_boundaries(self):
        values = [.01, .02, .03, .04, .05, .06]
        interval = analyze.paired_interval(values)
        self.assertAlmostEqual(interval["mean_log"], .035)
        self.assertAlmostEqual(interval["sd_log"], math.sqrt(.00175/5))
        self.assertAlmostEqual(analyze.student_t_cdf(2.5705818366, 5), .975, places=8)
        self.assertAlmostEqual(interval["upper_log"]-interval["mean_log"],
                               analyze.student_t_ppf(.996875, 5)*math.sqrt(.00175/5)/math.sqrt(6))
        def i(low, high): return {"lower_log": low, "upper_log": high}
        self.assertEqual(analyze.verdict(i(analyze.LOWER, analyze.UPPER)), "EQUIVALENT")
        self.assertEqual(analyze.verdict(i(analyze.UPPER, analyze.UPPER+.001)), "INCONCLUSIVE")
        self.assertEqual(analyze.verdict(i(analyze.UPPER+.0001, analyze.UPPER+.001)), "DIFFERENT")

    def test_power_grid_and_stage0_spread(self):
        self.assertEqual(analyze.equivalence_power(0., 6), 1.)
        self.assertLess(analyze.equivalence_power(.2, 12), .01)
        table = analyze.power_table(0., 0.)
        self.assertEqual(len(table), 24)
        self.assertEqual({r["contrast"] for r in table}, {"D/I", "SH/I"})
        self.assertEqual({r["sd_multiplier"] for r in table}, {1., 1.5, 2.})
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for i, (a, b) in enumerate(((.40, .41), (.43, .42), (.39, .40)), 1):
                make_cell(root, self.config, "stage0", f"stage0-{i:02}", "I", [a, a*1.01])
                make_cell(root, self.config, "stage0", f"stage0-{i:02}", "SH", [b, b*1.02])
            rows = analyze.analyze_directory(root, self.config)["cells"]
            spread = analyze.stage0_spread(rows)
            self.assertGreater(spread["within_run_sd_log"]["E"], 0)
            self.assertGreater(spread["between_cell_paired_sd_log"]["E"], 0)

    def test_drift_equivalence_and_edge_difference_gates(self):
        rows = []
        for number in range(1, 7):
            for arm in ("D", "I", "SH"):
                energy = 1.04 if arm == "D" else 1.0
                rows.append({"stage": "U1", "block": f"U1-{number:02}", "context": arm,
                             "metrics": {"E": energy, "R": 50., "net_j": energy * 512,
                                         "drift_ratio": .01, "attribution_bound_j": 1.,
                                         "edge_bound_j_per_token": .10 if arm == "D" else .001,
                                         "median_sample_interval_s": .1, "cpu_seconds": 5.}})
        decision = analyze.decision_table(rows, self.config)
        self.assertEqual(decision["verdicts"]["D/I:E"], "INCONCLUSIVE")
        self.assertIn("edge_bound_downgrade:D/I:E", decision["flags"])
        self.assertEqual(decision["verdicts"]["SH/I:E"], "EQUIVALENT")
        self.assertLess(decision["intervals"]["SH/I:E"]["widened_lower_ratio"],
                        decision["intervals"]["SH/I:E"]["lower_ratio"])
        for row in rows:
            row["metrics"]["drift_ratio"] = .04
        decision = analyze.decision_table(rows, self.config)
        self.assertEqual(decision["verdicts"]["SH/I:E"], "INCONCLUSIVE-by-attribution")
        self.assertEqual(decision["verdicts"]["SH/I:R"], "EQUIVALENT")

    def test_interruption_and_same_order_retry(self):
        self.assertTrue(runner.interrupted({"hid_idle_seconds": 599, "display_state": "on"}, "U", 600, "on"))
        self.assertTrue(runner.interrupted({"hid_idle_seconds": 700, "display_state": "asleep"}, "U", 600, "on"))
        self.assertFalse(runner.interrupted({"hid_idle_seconds": 700, "display_state": "unknown"}, "U", 600, "on"))
        block = common.blocks(self.config, "U1")[2]
        self.assertEqual(runner.retry_block(block, 1)["arms"], block["arms"])
        self.assertFalse(cell.census_sample(SimpleNamespace(command=lambda argv: {"stdout":""}, idle=lambda:700,
                                                         display=lambda:"on"), "U", "on", 600)["interrupted"])

    def test_runner_replays_invalid_bundle_block_in_same_order(self):
        config = copy.deepcopy(self.config)
        class FakeRunner:
            def __init__(self):
                self.started = []
            def write_cell(self, script):
                parts = shlex.split(script)
                directory = Path(parts[parts.index("--out") + 1])
                self.started.append(directory.name)
                block, slot, arm, attempt = directory.name.split(".")
                fixture = "failed_status" if directory.name == "stage0-01.1.I.a1" else "bench_smoke"
                runs = []
                for number in (1, 2):
                    bundle = make_bundle(directory, f"bundle-{number}", fixture)
                    runs.append({"bundle": str(bundle), "child": {"pid": 800 + number}})
                (directory / "cell.json").write_text(json.dumps({
                    "stage": "stage0", "state": "A", "context": arm, "cell_id": int(slot),
                    "pid": 500, "runs": runs, "flags": [], "interrupted": False}))
                (directory / "done.json").write_text(json.dumps({"ok": True, "interrupted": False}))
            def run(self, argv):
                if argv[1] == "bootstrap":
                    script = plistlib.loads(Path(argv[-1]).read_bytes())["ProgramArguments"][2]
                    self.write_cell(script)
                return SimpleNamespace(returncode=1 if argv[1] in ("print", "-f") else 0,
                                       stdout="", stderr="")
            def spawn_shell(self, argv, directory):
                self.write_cell(argv[5]); return object()
            def stop_shell(self, process): pass
            def now(self): return 0.
            def sleep(self, seconds): pass
            def display(self): return "on"
            def idle(self): return 700.
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            actions = runner.plan(out, common.DEFAULT_CONFIG, config, "stage0", "/python")
            fake = FakeRunner()
            runner.execute(out, common.DEFAULT_CONFIG, config, "stage0", "/python",
                           backend=fake, existing_actions=actions)
            self.assertEqual(len(fake.started), 7)
            discarded = json.loads((out / "stage0-01.1.I.a1" / "discarded.json").read_text())
            self.assertEqual(discarded["reason"], "bundle_invalid")
            self.assertTrue((out / "stage0-01.1.I.a2" / "done.json").exists())
            self.assertTrue((out / "stage0-01.2.SH.a2" / "done.json").exists())

    def test_three_distinct_invalid_cells_stop_stage(self):
        class FakeRunner:
            def write_cell(self, script):
                parts = shlex.split(script)
                directory = Path(parts[parts.index("--out") + 1])
                block, slot, arm, attempt = directory.name.split(".")
                (directory / "cell.json").write_text(json.dumps({
                    "stage": "stage0", "state": "A", "context": arm, "cell_id": int(slot),
                    "pid": 500, "runs": [{"bundle": str(directory / f"r{n}")} for n in (1, 2)],
                    "interrupted": False}))
                (directory / "done.json").write_text(json.dumps({"ok": True, "interrupted": False}))
            def run(self, argv):
                if argv[1] == "bootstrap":
                    self.write_cell(plistlib.loads(Path(argv[-1]).read_bytes())["ProgramArguments"][2])
                return SimpleNamespace(returncode=1 if argv[1] in ("print", "-f") else 0, stdout="", stderr="")
            def spawn_shell(self, argv, directory): self.write_cell(argv[5]); return object()
            def stop_shell(self, process): pass
            def now(self): return 0.
            def sleep(self, seconds): pass
            def display(self): return "on"
            def idle(self): return 700.
        def evidence(bundle, reference):
            name = bundle.parent.name
            invalid = ".SH.a1" in name
            return {"valid": not invalid, "output_hash": "same"}
        with tempfile.TemporaryDirectory() as temp, patch.object(runner, "bundle_evidence", side_effect=evidence):
            out = Path(temp)
            actions = runner.plan(out, common.DEFAULT_CONFIG, self.config, "stage0", "/python")
            with self.assertRaisesRegex(RuntimeError, "3 invalid cells in SH"):
                runner.execute(out, common.DEFAULT_CONFIG, self.config, "stage0", "/python",
                               backend=FakeRunner(), existing_actions=actions)

    def test_u2_rejects_non_u1_or_incomplete_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary = root / "summary.json"
            summary.write_text(json.dumps({"stage": None, "verdicts": {"D/I:E": "INCONCLUSIVE"},
                                           "errors": [], "cells": []}))
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                runner.main(["--stage", "U2", "--out", str(root / "U2"), "--u1-summary", str(summary)])
            summary.write_text(json.dumps({"stage": "U1", "verdicts": {"D/I:E": "INCONCLUSIVE"},
                                           "errors": [], "cells": []}))
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                runner.main(["--stage", "U2", "--out", str(root / "U2"), "--u1-summary", str(summary)])

    def test_census_cpu_delta_allowlist(self):
        def record(t, cpu):
            return {"wall_ns": int(t*1e9), "ps": {"pid": 999,
                    "stdout": f"PID PPID TIME COMM\n42 1 00:{cpu:05.2f} daemon\n43 1 00:{cpu:05.2f} allowed\n"}}
        flags = analyze.census_cpu_flags([record(1000., 0.), record(1005., .3)],
                                         {("run", 1): (1000., 1005.)}, workload_pid=500,
                                         sampler_pid=2, allow_pids=[43])
        self.assertEqual([x["pid"] for x in flags], [42])
        self.assertAlmostEqual(flags[0]["core_fraction"], .06)

    def test_bundle_validity_and_edge_from_real_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            good = make_bundle(root, "good")
            record = analyze.bundle_evidence(good)
            self.assertTrue(record["valid"], record["issues"])
            self.assertAlmostEqual(record["metrics"]["E"], .405500367643082)
            self.assertGreater(record["metrics"]["edge_bound_j"], 0.)
            self.assertGreater(record["metrics"]["drift_ratio"], .03)
            failed = make_bundle(root, "failed", "failed_status")
            self.assertIn("status", analyze.bundle_evidence(failed)["issues"])
            precheck = make_bundle(root, "precheck", "failed_precheck")
            self.assertTrue(any(x.startswith("precheck:") for x in analyze.bundle_evidence(precheck)["issues"]))
            mismatch = analyze.bundle_evidence(good, "token_ids:bad")
            self.assertIn("output_hash_mismatch", mismatch["issues"])
            short = good / "outputs" / "tokens.jsonl"
            short.write_text("".join(short.read_text().splitlines(keepends=True)[:511]))
            self.assertIn("output_tokens", analyze.bundle_evidence(good)["issues"])

    def test_analyzer_synthetic_bundle_cells_and_verdict_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for block in common.blocks(self.config, "U1"):
                if block["discard"] or block["arms"] == ["B"]: continue
                for arm in block["arms"]:
                    value = .42 if arm == "D" else .4
                    make_cell(root, self.config, "U1", block["id"], arm, [value])
            invalid = make_cell(root, self.config, "U1", "U1-B-extra", "B", [.4], fixture="failed_status")
            report = analyze.analyze_directory(root, self.config)
            self.assertEqual(len(report["cells"]), 19)
            self.assertEqual(report["verdicts"]["D/I:E"], "DIFFERENT")
            self.assertEqual(report["verdicts"]["SH/I:R"], "EQUIVALENT")
            self.assertEqual(report["invalid_cell_counts"]["B"], 1)
            self.assertIn("bundle_invalid", next(r for r in report["cells"] if r["dir"] == str(invalid))["flags"])
            interval = report["intervals"]["D/I:E"]
            self.assertGreater(interval["widened_upper_ratio"] - interval["widened_lower_ratio"], 0)
            self.assertIn("Absolute J/token", (root / "summary.md").read_text())
            make_cell(root, self.config, "U1", "U1-B-other", "B", [.4], token_offset=1)
            rerun = analyze.analyze_directory(root, self.config)
            self.assertIn("output_hash_mismatch", next(r for r in rerun["cells"] if "other" in r["block"])["flags"])


if __name__ == "__main__":
    unittest.main()
