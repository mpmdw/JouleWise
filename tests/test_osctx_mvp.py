"""Offline OSCTX schedule, workload, telemetry, and statistical checks."""
from __future__ import annotations

import copy
from contextlib import redirect_stderr
from datetime import datetime, timezone
import io
import json
import math
from pathlib import Path
import plistlib
import shlex
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from scripts.diagnostics.osctx_mvp import analyze, cell, common, runner


class FakeWorkload:
    def __init__(self):
        self.calls = 0
    def command(self, argv):
        return {"argv": argv, "pid": 99999, "stdout": "", "returncode": 0}
    def idle(self):
        return 700
    def display(self):
        return "on"
    def sleep(self, seconds):
        pass
    def model_sha256(self, path):
        return "a" * 64
    def preread(self, config):
        pass
    def prepare_model(self, config):
        return {"versions": config["runtime"], "prompt": "templated prompt"}
    def generate(self, prepared, max_tokens, first_token):
        self.calls += 1
        first_token()
        return {"token_ids": list(range(max_tokens)), "output_tokens": max_tokens,
                "prompt_tps": 100., "generation_tps": 50., "finish_reason": "length"}
    def cpu_probe(self, seconds):
        return 123


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
        self.assertEqual(sum(map(lambda b: len(b["arms"]), common.blocks(self.config, "U1"))), 21)
        self.assertEqual(sum(map(lambda b: len(b["arms"]), common.blocks(self.config, "U2"))), 18)
        self.assertEqual([b["state"] for b in common.blocks(self.config, "S")], ["U"]*3+["S"]*3+["U"]*3)

    def test_rendered_zsh_exec_and_shell_detachment(self):
        with tempfile.TemporaryDirectory() as temp:
            actions = runner.plan(Path(temp), common.DEFAULT_CONFIG, self.config, "U1", "/python")
            d = next(a for a in actions if a["context"] == "D")
            i = next(a for a in actions if a["context"] == "I")
            b = next(a for a in actions if a["context"] == "B")
            sh = next(a for a in actions if a["context"] == "SH")
            self.assertEqual(sh["start"][:3], ["nohup", "caffeinate", "-is"])
            self.assertEqual(sh["start"][3:5], ["/bin/zsh", "-c"])
            self.assertTrue(sh["start"][5].startswith("exec /python "))
            self.assertTrue(sh["detached"])
            for action, process_type in ((d, None), (i, "Interactive"), (b, "Background")):
                with Path(action["cell_dir"], "job.plist").open("rb") as stream:
                    pl = plistlib.load(stream)
                self.assertEqual(pl["ProgramArguments"][:2], ["/bin/zsh", "-c"])
                self.assertTrue(pl["ProgramArguments"][2].startswith("exec /python "))
                self.assertEqual(pl.get("ProcessType"), process_type)
                self.assertEqual(pl["WorkingDirectory"], str(runner.ROOT))
                self.assertIn("PATH", pl["EnvironmentVariables"])
            backend = runner.SystemBackend()
            with patch("subprocess.Popen") as popen:
                backend.spawn_shell(sh["start"], Path(sh["cell_dir"]))
                self.assertTrue(popen.call_args.kwargs["start_new_session"])

    def test_paired_t_and_verdict_boundaries(self):
        values = [.01, .02, .03, .04, .05, .06]
        interval = analyze.paired_interval(values)
        self.assertAlmostEqual(interval["mean_log"], .035)
        self.assertAlmostEqual(interval["sd_log"], math.sqrt(.00175/5))
        self.assertAlmostEqual(analyze.student_t_cdf(2.5705818366, 5), .975, places=8)
        self.assertAlmostEqual(interval["upper_log"]-interval["mean_log"],
                               analyze.student_t_ppf(.996875, 5)*math.sqrt(.00175/5)/math.sqrt(6))
        def i(low, high):
            return {"lower_log": low, "upper_log": high}
        self.assertEqual(analyze.verdict(i(analyze.LOWER, analyze.UPPER)), "EQUIVALENT")
        self.assertEqual(analyze.verdict(i(analyze.UPPER, analyze.UPPER+.001)), "INCONCLUSIVE")
        self.assertEqual(analyze.verdict(i(analyze.UPPER+.0001, analyze.UPPER+.001)), "DIFFERENT")
        self.assertEqual(analyze.verdict(i(analyze.LOWER-.001, analyze.LOWER)), "INCONCLUSIVE")

    def test_power_known_cases(self):
        self.assertEqual(analyze.equivalence_power(0., 6), 1.)
        self.assertLess(analyze.equivalence_power(.2, 12), .01)
        table = analyze.power_table(0., 0.)
        self.assertEqual(len(table), 8)
        self.assertTrue(all(x["power"] == 1. for x in table))
        self.assertTrue(all("20000" in x["method"] for x in table))

    def test_interruption_and_same_order_retry(self):
        self.assertTrue(runner.interrupted({"hid_idle_seconds": 599, "display_state": "on"}, "U", 600, "on"))
        self.assertTrue(runner.interrupted({"hid_idle_seconds": 700, "display_state": "asleep"}, "U", 600, "on"))
        self.assertFalse(runner.interrupted({"hid_idle_seconds": 700, "display_state": "unknown"}, "U", 600, "on"))
        block = common.blocks(self.config, "U1")[2]
        retry = runner.retry_block(block, 1)
        self.assertEqual(retry["arms"], block["arms"])
        self.assertEqual(retry["attempt"], 2)
        self.assertEqual(cell.census_sample(FakeWorkload(), "U", "on", 600)["interrupted"], False)

    def test_runner_replays_whole_interrupted_block(self):
        class FakeRunner:
            def __init__(self):
                self.started = []
                self.first = True
            def run(self, argv):
                if argv[1] == "bootstrap":
                    script = plistlib.loads(Path(argv[-1]).read_bytes())["ProgramArguments"][2]
                    self.write_cell(script)
                code = 1 if argv[1] in ("print", "-f") else 0
                return SimpleNamespace(returncode=code, stdout="", stderr="")
            def write_cell(self, script):
                parts = shlex.split(script)
                directory = Path(parts[parts.index("--out")+1])
                self.started.append(directory.name)
                interrupted = self.first
                self.first = False
                (directory / "cell.json").write_text(json.dumps({"interrupted": interrupted}))
                (directory / "done.json").write_text(json.dumps({"ok": True, "interrupted": interrupted}))
            def spawn_shell(self, argv, directory):
                self.write_cell(argv[5])
                return object()
            def stop_shell(self, process): pass
            def now(self): return 0.
            def sleep(self, seconds): pass
            def display(self): return "on"
            def idle(self): return 700.
        fake = FakeRunner()
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            actions = runner.plan(out, common.DEFAULT_CONFIG, self.config, "stage0", "/python")
            runner.execute(out, common.DEFAULT_CONFIG, self.config, "stage0", "/python",
                           backend=fake, existing_actions=actions)
            self.assertEqual(len(fake.started), 7)  # first failed cell plus all six cells replayed
            self.assertTrue((out / "stage0-01.1.I.a1" / "discarded.json").exists())
            self.assertTrue((out / "stage0-01.1.I.a2" / "done.json").exists())
            self.assertTrue((out / "stage0-01.2.SH.a2" / "done.json").exists())

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
        records = [record(1000., 0.), record(1005., .3)]
        flags = analyze.census_cpu_flags(records, {("lm", 1): (1000., 1005.)}, workload_pid=1,
                                         sampler_pid=2, allow_pids=[43])
        self.assertEqual([x["pid"] for x in flags], [42])
        self.assertAlmostEqual(flags[0]["core_fraction"], .06)

    def test_token_and_hash_integrity_and_fake_cell(self):
        good = {"output_tokens": 256, "token_ids": list(range(256)), "finish_reason": "length"}
        self.assertEqual(cell.token_flags(good), [])
        self.assertEqual(cell.token_flags({**good, "output_tokens": 255}), ["token_count_mismatch"])
        self.assertIn("early_finish", cell.token_flags({**good, "finish_reason": "stop"}))
        self.assertNotEqual(cell.output_hash(good["token_ids"]), cell.output_hash(list(reversed(good["token_ids"]))))
        config = copy.deepcopy(self.config)
        config["segments"].update({"guard_seconds": 0, "idle_seconds": 0, "cpu_seconds": 0})
        fake = FakeWorkload()
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            cell.run(out, config, "A", "I", 1, stage="stage0", backend=fake, no_powermetrics=True)
            saved = json.loads((out / "cell.json").read_text())
            self.assertEqual(fake.calls, 4)
            self.assertEqual(len(saved["repeats"]["lm"]), 3)
            self.assertEqual(len([b for b in saved["boundaries"] if b["edge"] == "first_token"]), 4)
            self.assertEqual(saved["model_sha256"], "a"*64)
            self.assertTrue(json.loads((out / "done.json").read_text())["ok"])

    def test_two_integral_and_boundary_flags_on_plist(self):
        epoch = 1000.
        def make_raw(bad_counter=False):
            return b"\0".join(plistlib.dumps({"timestamp": datetime.fromtimestamp(epoch+i*.1, tz=timezone.utc),
                      "elapsed_ns": 100_000_000, "processor": {
                          "cpu_power": 12000 if 5 <= i <= 9 else 6000,
                          "gpu_power": 6000 if 5 <= i <= 9 else 3000,
                          "ane_power": 2000 if 5 <= i <= 9 else 1000,
                          "cpu_energy": (1400 if bad_counter else 1200) if 5 <= i <= 9 else 600,
                          "gpu_energy": 600 if 5 <= i <= 9 else 300,
                          "ane_energy": 200 if 5 <= i <= 9 else 100}})
                          for i in range(12)) + b"\0"
        raw = make_raw()
        bounds = [{"name": name, "repeat": repeat, "edge": edge, "wall_ns": int(t*1e9)}
                  for name, repeat, start, end in (("idle", 1, 1000.05, 1000.35), ("lm", 1, 1000.45, 1000.85))
                  for edge, t in (("start", start), ("end", end))]
        trace = analyze.reduce_trace(raw, bounds, epoch)
        self.assertGreater(trace["lm.1"]["energy_j"], 7.)
        self.assertAlmostEqual(trace["lm.1"]["energy_j"], trace["lm.1"]["counter_energy_j"], places=5)
        self.assertGreater(trace["lm.1"]["boundary_uncertainty_j"], 0.)
        repeats = [{"repeat": 1, "output_tokens": 256, "output_hash": "h", "generation_tps": 50., "prompt_tps": 100., "flags": []}]
        values, flags = analyze.request_metrics(trace, repeats, self.config)
        self.assertGreater(values[0]["net_j"], 0.)
        self.assertIn("boundary_uncertainty:lm.1", flags)
        broken = analyze.reduce_trace(make_raw(bad_counter=True), bounds, epoch)
        self.assertGreater(broken["lm.1"]["integral_disagreement_j"], .1)
        _, flags = analyze.request_metrics(broken, repeats, self.config)
        self.assertIn("two_integral_disagreement:lm.1", flags)

    def test_analyzer_end_to_end_fake_backend(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = {}
            for block in common.blocks(self.config, "U1"):
                if block["discard"] or block["arms"] == ["B"]: continue
                for arm in block["arms"]:
                    directory = root / f"{block['id']}.{arm}"
                    directory.mkdir()
                    (directory / "cell.json").write_text("{}")
                    value = 1.04 if arm == "D" else 1.
                    data[str(directory)] = {"stage": "U1", "state": "U", "context": arm,
                        "block": block["id"], "dir": str(directory),
                        "metrics": {"E": value, "R": 50.*value},
                        "requests": [{"output_hash": "same"}], "flags": []}
            extra = root / "U1-B-extra.B"
            extra.mkdir()
            (extra / "cell.json").write_text("{}")
            data[str(extra)] = {"stage": "U1", "state": "U", "context": "B", "block": "U1-B-extra",
                                "dir": str(extra), "metrics": {"E": 1., "R": 50.},
                                "requests": [{"output_hash": "different"}], "flags": []}
            report = analyze.analyze_directory(root, self.config, analyzer_backend=lambda path, config: data[str(path)])
            self.assertEqual(len(report["cells"]), 19)
            self.assertEqual(report["verdicts"]["D/I:E"], "DIFFERENT")
            self.assertEqual(report["verdicts"]["SH/I:R"], "EQUIVALENT")
            self.assertTrue(any("output_hash_mismatch" in r["flags"] for r in report["cells"]))
            self.assertIsNone(next(r for r in report["cells"] if r["context"] == "B")["metrics"]["E"])
            self.assertIn("Absolute J/token", (root / "summary.md").read_text())
            u2 = []
            for block in common.blocks(self.config, "U2"):
                for arm in block["arms"]:
                    value = 1.04 if arm == "D" else 1.
                    u2.append({"stage": "U2", "context": arm, "block": block["id"],
                               "metrics": {"E": value, "R": 50.*value}})
            combined = analyze.decision_table(report["cells"] + u2, self.config)
            self.assertEqual(combined["intervals"]["D/I:E"]["n"], 12)


if __name__ == "__main__":
    unittest.main()
