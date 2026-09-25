"""Offline OSCTX production-wrapper, bundle, schedule, and statistic checks."""
from __future__ import annotations

import copy
from contextlib import redirect_stderr
import hashlib
import io
import json
import math
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
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
    (bundle / "metadata.json").write_text(json.dumps({"run_id": name, "workload_observed": {"output_token_count": 512}}))
    return bundle


def make_cell(parent: Path, config, stage, block, arm, energies, rates=None, *, fixture="bench_smoke", token_offset=0, attempt=1):
    scheduled = next((a for a in json.loads((parent / "command_sequence.json").read_text())["actions"]
                      if a["block"] == block and a["context"] == arm), None)
    if scheduled is None:
        raise ValueError("test cell must be scheduled")
    slot = scheduled["cell_id"]
    directory = parent / f"{block}.{slot}.{arm}.a{attempt}"
    directory.mkdir(exist_ok=True)
    runs = []
    for number, energy in enumerate(energies, 1):
        run_id = f"osctx-{stage.lower()}-{block.lower()}-{slot}-{arm.lower()}-r{number}"
        bundle = make_bundle(directory / "runs", run_id, fixture, energy=energy,
                             rate=(rates or [84.] * len(energies))[number-1], token_offset=token_offset)
        cfg = directory / f"run-r{number}.json"
        cfg.write_text(json.dumps({"run_id": run_id}))
        runs.append({"bundle": str(bundle), "run_id": run_id, "config": str(cfg),
                     "materialized_sha256": hashlib.sha256(cfg.read_bytes()).hexdigest(),
                     "child": {"pid": 700 + number}})
    record = {"stage": stage, "state": "A" if stage == "stage0" else "U", "context": arm,
              "pid": 500, "cell_id": slot, "runs": runs, "cpu": [{"seconds": 5.1}], "allow_pids": [], "flags": [], "interrupted": False}
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
            self.assertEqual(common.load_config(path)["runs_per_cell"],
                             {stage: (1 if stage == "rehearsal" else 2) for stage in common.STAGES})

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
            runner.plan(root, common.DEFAULT_CONFIG, self.config, "stage0", "/python")
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
        self.assertTrue(runner.interrupted({"hid_idle_seconds": 700, "display_state": "unknown"}, "U", 600, "on"))
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

    def test_two_plus_one_failed_attempts_stop_stage(self):
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
            fail = ("stage0-01" in name and ".SH.a1" in name) or \
                   ("stage0-01" in name and ".SH.a2" in name) or \
                   ("stage0-02" in name and ".SH.a1" in name)
            return {"valid": not fail, "output_hash": "same"}
        with tempfile.TemporaryDirectory() as temp, patch.object(runner, "bundle_evidence", side_effect=evidence):
            out = Path(temp)
            actions = runner.plan(out, common.DEFAULT_CONFIG, self.config, "stage0", "/python")
            with self.assertRaisesRegex(RuntimeError, "3 invalid cells in SH"):
                runner.execute(out, common.DEFAULT_CONFIG, self.config, "stage0", "/python",
                               backend=FakeRunner(), existing_actions=actions)

    def test_analyzer_counts_failed_attempts_not_slots(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runner.plan(root, common.DEFAULT_CONFIG, self.config, "stage0", "/python")
            for block, attempt in (("stage0-01", 1), ("stage0-01", 2), ("stage0-02", 1)):
                directory = make_cell(root, self.config, "stage0", block, "SH", [.4, .4], attempt=attempt)
                (directory / "discarded.json").write_text(json.dumps({"reason": "bundle_invalid", "block": block,
                                                                       "attempt": attempt}))
            report = analyze.analyze_directory(root, self.config)
            self.assertEqual(report["invalid_cell_counts_by_stage"]["stage0"]["SH"], 3)
            self.assertEqual(len(report["discarded"]), 3)

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
            runner.plan(root, common.DEFAULT_CONFIG, self.config, "U1", "/python")
            for block in common.blocks(self.config, "U1"):
                if block["discard"] or block["arms"] == ["B"]: continue
                for arm in block["arms"]:
                    value = .42 if arm == "D" else .4
                    make_cell(root, self.config, "U1", block["id"], arm, [value])
            invalid = make_cell(root, self.config, "U1", "U1-B-01", "B", [.4], fixture="failed_status")
            report = analyze.analyze_directory(root, self.config)
            self.assertEqual(len(report["cells"]), 19)
            self.assertEqual(report["verdicts"]["D/I:E"], "DIFFERENT")
            self.assertEqual(report["verdicts"]["SH/I:R"], "EQUIVALENT")
            self.assertEqual(report["invalid_cell_counts"]["B"], 1)
            self.assertIn("bundle_invalid", next(r for r in report["cells"] if r["dir"] == str(invalid))["flags"])
            interval = report["intervals"]["D/I:E"]
            self.assertGreater(interval["widened_upper_ratio"] - interval["widened_lower_ratio"], 0)
            self.assertIn("Absolute J/token", (root / "summary.md").read_text())
            make_cell(root, self.config, "U1", "U1-B-02", "B", [.4], token_offset=1)
            rerun = analyze.analyze_directory(root, self.config)
            self.assertIn("output_hash_mismatch", next(r for r in rerun["cells"] if r["block"] == "U1-B-02")["flags"])

    def test_schedule_rejects_foreign_bundles_and_config_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runner.plan(root, common.DEFAULT_CONFIG, self.config, "U1", "/python")
            cells = []
            for block in common.blocks(self.config, "U1"):
                if len(block["arms"]) != 3:
                    continue
                for arm in block["arms"]:
                    cells.append(make_cell(root, self.config, "U1", block["id"], arm, [.4]))
            foreign = make_bundle(root / "foreign", "wrong")
            for directory in cells:
                record = json.loads((directory / "cell.json").read_text())
                record["runs"][0]["bundle"] = str(foreign)
                (directory / "cell.json").write_text(json.dumps(record))
            report = analyze.analyze_directory(root, self.config)
            self.assertEqual(len(report["cells"]), 0)
            self.assertEqual(len(report["errors"]), 18)
            self.assertTrue(all("foreign bundle" in error["error"] for error in report["errors"]))
            record = json.loads((cells[0] / "cell.json").read_text())
            record["runs"][0]["bundle"] = str(cells[0] / "runs" / record["runs"][0]["run_id"])
            (cells[0] / "cell.json").write_text(json.dumps(record))
            (cells[0] / "run-r1.json").write_text('{"run_id":"tampered"}')
            report = analyze.analyze_directory(root, self.config)
            self.assertIn("sha256 mismatch", next(e for e in report["errors"] if e["cell"] == str(cells[0]))["error"])

    def test_pairing_never_crosses_stages(self):
        rows = [{"stage": stage, "block": "same", "context": arm, "metrics": {"E": value}}
                for stage, arm, value in (("U1", "D", 1.), ("U2", "I", 1.))]
        self.assertEqual(analyze.paired_rows(rows, "D/I", "E")[0], [])
        rows.append({"stage": "U1", "block": "same", "context": "D", "metrics": {"E": 1.}})
        with self.assertRaisesRegex(ValueError, "duplicate pairing arm"):
            analyze.paired_rows(rows, "D/I", "E")

    def test_unknown_required_observations_interrupt_or_abort(self):
        backend = SimpleNamespace(command=lambda argv: {"stdout": ""},
                                  idle=lambda: (_ for _ in ()).throw(RuntimeError("HID unreadable")),
                                  display=lambda: "unknown")
        observation = cell.census_sample(backend, "U", "on", 600)
        self.assertTrue(observation["interrupted"])
        polls = []
        backend.sleep = lambda seconds: polls.append(seconds)
        with self.assertRaisesRegex(RuntimeError, "unknown after 3 polls"):
            runner.wait_gate(backend, self.config, lambda **record: None)
        self.assertEqual(len(polls), 2)

    def test_census_idle_baseline_cpu_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runner.plan(root, common.DEFAULT_CONFIG, self.config, "U1", "/python")
            directory = make_cell(root, self.config, "U1", "U1-01", "I", [.4]) if "I" in common.blocks(self.config, "U1")[1]["arms"] else None
            if directory is None:
                self.fail("Williams block must contain I")
            bundle = Path(json.loads((directory / "cell.json").read_text())["runs"][0]["bundle"])
            with (bundle / "events.jsonl").open("a") as stream:
                stream.write(json.dumps({"timestamp_s": 1000., "event_type": "stage_started", "phase": "idle_baseline"}) + "\n")
                stream.write(json.dumps({"timestamp_s": 1010., "event_type": "stage_completed", "phase": "idle_baseline"}) + "\n")
            def record(t, cpu):
                return {"wall_ns": int(t*1e9), "ps": {"pid": 999, "stdout": f"PID PPID TIME COMM\n42 1 00:{cpu:05.2f} daemon\n"}}
            (directory / "census.jsonl").write_text("\n".join(json.dumps(x) for x in (record(1000, 0), record(1005, .5))) + "\n")
            analyzed = analyze.analyze_cell(directory, self.config)
            self.assertIn("census_cpu", analyzed["flags"])
            self.assertEqual(analyzed["census_cpu_flags"][0]["segment"], "idle.1")

    def test_text_hash_cannot_substitute_for_token_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = make_bundle(Path(temp), "text-only")
            (bundle / "outputs" / "tokens.jsonl").unlink()
            (bundle / "outputs" / "response.txt").write_text("same decoded text")
            evidence = analyze.bundle_evidence(bundle)
            self.assertFalse(evidence["valid"])
            self.assertIn("output_tokens", evidence["issues"])
            self.assertIn("output_hash_missing", evidence["issues"])

    def test_u_replication_variance_component(self):
        spread = {"between_cell_paired_sd_log": {"E": .015, "R": .02},
                  "within_run_sd_log": {"E": .015, "R": .02}}
        scaled = analyze.u_replication_spread(spread, 1, 2)
        self.assertAlmostEqual(scaled["E"], .015 * math.sqrt(2))
        self.assertAlmostEqual(analyze.equivalence_power(scaled["E"], 6), .13745, delta=.01)
        self.assertEqual({row["runs_per_cell_U"] for row in analyze.power_table(scaled["E"], scaled["R"])}, {1})

    def test_network_time_order_and_fail_closed(self):
        sudoers = (runner.ROOT / "scripts/joulewise-network-time.sudoers").read_text()
        for setting in ("off", "on"):
            self.assertIn("/usr/sbin/systemsetup -setusingnetworktime " + setting, sudoers)
            self.assertEqual(runner.NETWORK_TIME + [setting],
                             ["sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", setting])
        class Fake:
            def __init__(self, off=0, on=0):
                self.calls = []
                self.off, self.on = off, on
            def run(self, argv):
                self.calls.append(argv)
                return SimpleNamespace(returncode=self.off if argv[-1] == "off" else self.on,
                                       stdout="", stderr=f"{argv[-1]} stderr")
        records = []
        fake = Fake()
        def failure():
            fake.calls.append("body")
            raise ValueError("injected")
        with self.assertRaisesRegex(ValueError, "injected"):
            runner.with_network_time(fake, lambda **r: records.append(r), failure)
        self.assertEqual(fake.calls, [runner.NETWORK_TIME + ["off"], "body", runner.NETWORK_TIME + ["on"]])
        self.assertEqual([(r["argv"][-1], r["returncode"], r["stderr"]) for r in records],
                         [("off", 0, "off stderr"), ("on", 0, "on stderr")])
        fake = Fake()
        with self.assertRaises(KeyboardInterrupt):
            runner.with_network_time(fake, lambda **r: records.append(r),
                                     lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
        self.assertEqual(fake.calls, [runner.NETWORK_TIME + ["off"], runner.NETWORK_TIME + ["on"]])
        fake = Fake(off=1)
        with self.assertRaisesRegex(RuntimeError, "network time off failed"):
            runner.with_network_time(fake, lambda **r: records.append(r),
                                     lambda: fake.calls.append("body"))
        self.assertEqual(fake.calls, [runner.NETWORK_TIME + ["off"], runner.NETWORK_TIME + ["on"]])
        fake = Fake(on=1)
        with self.assertRaisesRegex(RuntimeError, "network time on failed"):
            runner.with_network_time(fake, lambda **r: records.append(r), lambda: None)

    def test_launchd_pid_and_survivor_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "cell"
            directory.mkdir()
            action = {"cell_dir": str(directory), "label": "com.joulewise.dummy.osctx.test",
                      "stop": ["/bin/launchctl", "bootout", "gui/501", "job.plist"]}
            class Fake:
                def __init__(self, captured=True, survivor=False, ps_alive=False):
                    self.calls = []
                    self.captured, self.survivor, self.ps_alive = captured, survivor, ps_alive
                def run(self, argv):
                    self.calls.append(argv)
                    if argv[0] == "/bin/launchctl" and argv[1] == "print":
                        if self.captured:
                            self.captured = False
                            return SimpleNamespace(returncode=0, stdout="state = running\n    pid = 4321\n", stderr="")
                        return SimpleNamespace(returncode=1, stdout="", stderr="not found")
                    if argv[:3] == ["/bin/ps", "-p", "4321"] and argv[-1] == "pgid=":
                        return SimpleNamespace(returncode=0, stdout="9876\n", stderr="")
                    if argv[0] == "/usr/bin/pgrep":
                        return SimpleNamespace(returncode=0 if self.survivor else 1,
                                               stdout="4321\n" if self.survivor else "", stderr="")
                    if argv[:3] == ["/bin/ps", "-p", "4321"] and self.ps_alive:
                        return SimpleNamespace(returncode=0, stdout="4321\n", stderr="")
                    return SimpleNamespace(returncode=1 if argv[0] == "/bin/ps" else 0,
                                           stdout="", stderr="")
            fake = Fake()
            proof = runner.launch_pid(fake, action, lambda **r: None)
            self.assertEqual((proof["pid"], proof["pgid"]), (4321, 9876))
            self.assertEqual(json.loads((directory / "launch_proof.json").read_text())["pid"], 4321)
            runner.prove_bootout(fake, action, proof, lambda **r: None)
            self.assertIn(["/usr/bin/pgrep", "-g", "9876"], fake.calls)
            self.assertIn(["/bin/ps", "-p", "4321", "-o", "pid="], fake.calls)
            self.assertFalse(any(call[:2] == ["/usr/bin/pgrep", "-f"] for call in fake.calls))
            fake = Fake(survivor=True)
            proof = runner.launch_pid(fake, action, lambda **r: None)
            with self.assertRaisesRegex(RuntimeError, "survivor"):
                runner.prove_bootout(fake, action, proof, lambda **r: None)
            fake = Fake(ps_alive=True)
            proof = runner.launch_pid(fake, action, lambda **r: None)
            with self.assertRaisesRegex(RuntimeError, "survivor"):
                runner.prove_bootout(fake, action, proof, lambda **r: None)
            (directory / "done.json").write_text("{}")
            fake = Fake(captured=False)
            proof = runner.launch_pid(fake, action, lambda **r: None)
            self.assertIsNone(proof["pid"])
            runner.prove_bootout(fake, action, proof, lambda **r: None)
            fallback = next(call[-1] for call in fake.calls if call[:2] == ["/usr/bin/pgrep", "-f"])
            self.assertIn("osctx_mvp/cell\\.py", fallback)
            self.assertIn(str(directory), fallback)
            own = f"/python /repo/scripts/diagnostics/osctx_mvp/cell.py --out {directory} --state U\n"
            reviewer = f"/python reviewer.py --path {directory} --note osctx_mvp/cell.py\n"
            matched = subprocess.run(["/usr/bin/grep", "-E", fallback], input=own+reviewer,
                                     text=True, capture_output=True, check=False)
            self.assertEqual(matched.returncode, 0)
            self.assertEqual(matched.stdout, own)

    def test_rehearsal_render_and_real_analysis_refusal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(runner.main(["--stage", "rehearsal", "--render-only", str(root / "rehearsal")]), 0)
            schedule = json.loads((root / "rehearsal" / "command_sequence.json").read_text())
            self.assertEqual([(a["state"], a["context"]) for a in schedule["actions"]],
                             [("A", "I"), ("A", "SH")])
            self.assertTrue(all(item.get("gate") is None for item in schedule["sequence"]))
            self.assertEqual(self.config["runs_per_cell"]["rehearsal"], 1)
            u_config = copy.deepcopy(self.config)
            u_config["rehearsal_state"] = "U"
            runner.plan(root / "rehearsal_u", common.DEFAULT_CONFIG, u_config, "rehearsal", "/python")
            u_schedule = json.loads((root / "rehearsal_u" / "command_sequence.json").read_text())
            self.assertEqual(u_schedule["sequence"][0]["gate"], "HIDIdleTime >= 600 s")
            runner.plan(root / "U1", common.DEFAULT_CONFIG, self.config, "U1", "/python")
            rehearsal = make_cell(root / "rehearsal", self.config, "rehearsal",
                                  "rehearsal-01", "I", [.4])
            record = json.loads((rehearsal / "cell.json").read_text())
            record["state"] = "A"
            (rehearsal / "cell.json").write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "rehearsal"):
                analyze.analyze_directory(root, self.config)
            report = analyze.analyze_directory(root / "rehearsal", self.config)
            self.assertEqual(len(report["cells"]), 1)
            self.assertEqual(report["verdicts"], {})

    def test_freeze_rule_constructed_spreads(self):
        def spread(between, within):
            return {"between_cell_paired_sd_log": {"E": between, "R": between},
                    "within_run_sd_log": {"E": within, "R": within}}
        cases = [((.005, 0.), (6, 1, "cheapest_powered_within_budget")),
                 ((.006, .006), (6, 2, "cheapest_powered_within_budget")),
                 ((.009, 0.), (12, 1, "cheapest_powered_within_budget")),
                 ((.020, 0.), (12, 1, "underpowered_by_prereg"))]
        for (between, within), expected in cases:
            with self.subTest(between=between, within=within):
                frozen = runner.freeze_rule(spread(between, within), self.config)
                self.assertEqual((frozen["total_u_blocks"], frozen["runs_per_cell"], frozen["reason"]), expected)
                self.assertEqual(len(frozen["power_at_1p5_sd"]), 4)
                self.assertEqual([c["estimated_wall_minutes"] for c in frozen["candidates"]],
                                 [79.8, 126.0, 148.2, 234.0])
                self.assertFalse(frozen["candidates"][-1]["within_budget"])
                if expected[2] == "underpowered_by_prereg":
                    self.assertTrue(all(power < .80 for power in frozen["power_at_1p5_sd"].values()))

    def test_stage0u_is_gated_sizing_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runner.plan(root, common.DEFAULT_CONFIG, self.config, "stage0U", "/python")
            schedule = json.loads((root / "command_sequence.json").read_text())
            self.assertEqual(len(schedule["actions"]), 6)
            self.assertTrue(all(block["gate"] == "HIDIdleTime >= 600 s" for block in schedule["sequence"]))
            for block in common.blocks(self.config, "stage0U"):
                for arm in block["arms"]:
                    make_cell(root, self.config, "stage0U", block["id"], arm, [.4, .401])
            report = analyze.analyze_directory(root, self.config)
            self.assertEqual(len(report["cells"]), 6)
            self.assertEqual(report["verdicts"], {})
            self.assertEqual(analyze.stage0_spread(report["cells"])["paired_block_count_by_endpoint"],
                             {"E": 3, "R": 3})

    def test_session_chains_once_and_freezes_before_u1(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(runner.main(["--session", "U", "--render-only", str(root / "render")]), 0)
            self.assertEqual(json.loads((root / "render" / "session_plan.json").read_text())["stages"],
                             ["stage0U", "U1", "U2", "S"])
            class Fake:
                def __init__(self): self.calls = []
                def run(self, argv):
                    self.calls.append(argv)
                    return SimpleNamespace(returncode=0, stdout="", stderr="")
            fake = Fake()
            stages = []
            def execute(out, config_path, config, stage, python, **kwargs):
                stages.append(stage)
                self.assertFalse(kwargs["manage_network"])
                if stage == "U1":
                    self.assertTrue((out.parent / "freeze.json").is_file())
                    self.assertEqual(config["runs_per_cell"]["U1"], 1)
            def analyze_dir(path, config):
                if path.name == "stage0U": return {"cells": [], "errors": []}
                if path.name == "U1": return {"stage": "U1", "cells": [], "errors": [],
                                              "verdicts": {"D/I:E": "EQUIVALENT"}}
                return {"errors": [], "verdicts": {}}
            sizing = {"total_u_blocks": 12, "runs_per_cell": 1, "reason": "underpowered_by_prereg",
                      "candidates": [], "power_at_1p5_sd": {}}
            with patch.object(runner, "execute", side_effect=execute), \
                 patch.object(runner, "analyze_directory", side_effect=analyze_dir), \
                 patch.object(runner, "stage0_spread", return_value={
                     "paired_block_count": 3, "paired_block_count_by_endpoint": {"E": 3, "R": 3},
                     "between_cell_paired_sd_log": {"E": .01, "R": .01},
                     "within_run_sd_log": {"E": 0., "R": 0.}}), \
                 patch.object(runner, "power_table", return_value=[]), \
                 patch.object(runner, "freeze_rule", return_value=sizing):
                runner.run_session(root / "live", common.DEFAULT_CONFIG, self.config, "/python", backend=fake)
            self.assertEqual(stages, ["stage0U", "U1", "U2", "S"])
            self.assertEqual(fake.calls, [runner.NETWORK_TIME + ["off"], runner.NETWORK_TIME + ["on"]])
            session = json.loads((root / "live" / "session.json").read_text())
            self.assertEqual(session["status"], "complete")
            self.assertEqual([step["step"] for step in session["steps"]],
                             ["stage0U", "analyze_power", "freeze", "U1", "U2", "S", "final_analyze"])
            self.assertTrue(all(step["start_wall_ns"] <= step["end_wall_ns"] for step in session["steps"]))
            with self.assertRaises(FileExistsError):
                runner.run_session(root / "live", common.DEFAULT_CONFIG, self.config, "/python", backend=fake)

    def test_six_block_session_skips_or_runs_u2_by_u1_verdict(self):
        class Fake:
            def __init__(self): self.calls = []
            def run(self, argv):
                self.calls.append(argv[-1])
                return SimpleNamespace(returncode=0, stdout="", stderr="")
        spread = {"paired_block_count_by_endpoint": {"E": 3, "R": 3},
                  "between_cell_paired_sd_log": {"E": .005, "R": .005},
                  "within_run_sd_log": {"E": 0., "R": 0.}}
        sizing = {"total_u_blocks": 6, "runs_per_cell": 1, "reason": "cheapest_powered_within_budget",
                  "candidates": [], "power_at_1p5_sd": {}}
        for verdict, expected in (("EQUIVALENT", ["stage0U", "U1", "S"]),
                                  ("INCONCLUSIVE", ["stage0U", "U1", "U2", "S"])):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as temp:
                stages, fake = [], Fake()
                def execute(out, config_path, config, stage, python, **kwargs): stages.append(stage)
                def analyze_dir(path, config):
                    if path.name == "stage0U": return {"cells": [], "errors": []}
                    if path.name == "U1": return {"verdicts": {"D/I:E": verdict}, "errors": []}
                    return {"errors": [], "verdicts": {}}
                with patch.object(runner, "execute", side_effect=execute), \
                     patch.object(runner, "analyze_directory", side_effect=analyze_dir), \
                     patch.object(runner, "stage0_spread", return_value=spread), \
                     patch.object(runner, "power_table", return_value=[]), \
                     patch.object(runner, "freeze_rule", return_value=sizing):
                    runner.run_session(Path(temp), common.DEFAULT_CONFIG, self.config, "/python", backend=fake)
                self.assertEqual(stages, expected)
                self.assertEqual(fake.calls, ["off", "on"])
                session = json.loads((Path(temp) / "session.json").read_text())
                self.assertEqual(next(s for s in session["steps"] if s["step"] == "U2")["outcome"],
                                 "skipped" if verdict == "EQUIVALENT" else "complete")

    def test_session_failure_records_reason_and_restores_network_time(self):
        with tempfile.TemporaryDirectory() as temp:
            calls = []
            class Fake:
                def run(self, argv):
                    calls.append(argv[-1])
                    return SimpleNamespace(returncode=0, stdout="", stderr="")
            def fail_stage(*args, **kwargs):
                calls.append("stage0U")
                raise RuntimeError("injected stage failure")
            with patch.object(runner, "execute", side_effect=fail_stage):
                with self.assertRaisesRegex(RuntimeError, "injected stage failure"):
                    runner.run_session(Path(temp), common.DEFAULT_CONFIG, self.config, "/python", backend=Fake())
            self.assertEqual(calls, ["off", "stage0U", "on"])
            session = json.loads((Path(temp) / "session.json").read_text())
            self.assertEqual(session["status"], "stopped")
            self.assertIn("injected stage failure", session["reason"])
            self.assertEqual(session["steps"][0]["outcome"], "stopped")
            self.assertIsNotNone(session["steps"][0]["end_wall_ns"])


if __name__ == "__main__":
    unittest.main()
