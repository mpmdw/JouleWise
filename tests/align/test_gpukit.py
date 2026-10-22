"""Offline matrix, cost, bootstrap and whole-session campaign rehearsals."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

from joulewise.align.gpukit.cost import estimate, work_counts
from joulewise.align.gpukit.matrix import expand, load_matrix, validate
from joulewise.align.gpukit.session import (
    IsolationError, SessionOptions, package_results, run_session, verify_manifest, whole_gpu,
)
from joulewise.align.records import read_episodes

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "align"


class MatrixTests(unittest.TestCase):
    def test_committed_matrices_counts_and_printed_wall_estimates(self):
        for name, rows, episodes, monitors in (
                ("shade", 60, 60, 180), ("moe_stage_a", 30, 30, 90),
                ("budget", 4224, 5760, 4224)):
            with self.subTest(name=name):
                matrix, flags = load_matrix(CONFIG / (name + ".json"))
                self.assertEqual(flags, ())
                self.assertEqual(len(expand(matrix)), rows)  # Integer Cartesian row identity.
                self.assertEqual(matrix["measured_episode_count"], episodes)
                self.assertEqual(matrix["monitor_call_count"], monitors)
                for gpu, printed in matrix["planning_wall_seconds"].items():
                    result = estimate(matrix, gpu)
                    self.assertEqual(result.measured_episodes, episodes)
                    self.assertEqual(result.monitor_calls, monitors)
                    # No uncertainty on arithmetic: prescribed 1e-6 relative bar.
                    self.assertTrue(math.isclose(result.wall_seconds, printed, rel_tol=1e-6))
                    self.assertIsNone(result.total_usd)
                    self.assertIn("price_not_supplied", result.flags)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "optional jsonschema is not installed")
    def test_json_schema(self):
        import jsonschema
        schema = json.loads((ROOT / "joulewise/align/gpukit/matrix.schema.json").read_text())
        for name in ("shade", "moe_stage_a", "budget"):
            matrix, _ = load_matrix(CONFIG / (name + ".json"))
            jsonschema.Draft202012Validator(schema).validate(matrix)

    def test_independent_hand_arithmetic(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        gpu = matrix["gpu_classes"]["A100-80GB"]
        # Separate closed-form scenario: five pairs * two conditions * three
        # seeds = 30 episodes/model. Each sees 40k prefill + 8k decode tokens.
        agent_seconds = 30 * (40000 / 2000 + 8000 / 60 + 16 + 12)
        agent_seconds += 30 * (40000 / 1700 + 8000 / 51 + 16 + 12)
        # Three monitor visibilities * 60 episodes = 180 calls. Qwen3-4B rate
        # is 2800 prefill/s and 84 decode/s in this unmeasured scenario.
        monitor_seconds = 180 * (8000 / 2800 + 32 / 84)
        seconds = 1800 + 5 * 180 + agent_seconds + monitor_seconds
        scenario_price = 2.0  # Test input only, not a provider price or recommendation.
        result = estimate(matrix, "A100-80GB", usd_per_gpu_hour=scenario_price)
        # Prescribed 1e-6 relative agreement bar for quantities without uncertainty.
        self.assertTrue(math.isclose(result.wall_seconds, seconds, rel_tol=1e-6))
        self.assertTrue(math.isclose(result.total_usd, seconds / 3600 * scenario_price,
                                     rel_tol=1e-6))
        changed = copy.deepcopy(matrix)
        changed["gpu_classes"]["A100-80GB"]["gpu_count"] = 2
        doubled = estimate(changed, "A100-80GB", usd_per_gpu_hour=scenario_price)
        self.assertTrue(math.isclose(doubled.gpu_hours, result.gpu_hours * 2, rel_tol=1e-6))
        self.assertEqual(gpu["gpu_count"], 1)

    def test_bad_inputs_are_flags(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        for mutation, expected in (
            (lambda m: m.update(episode_count=1), "matrix_episode_count_mismatch"),
            (lambda m: m["gpu_classes"]["A100-80GB"]["throughput"]
             ["Qwen/Qwen3-8B"].update(decode_tps=0),
             "matrix_throughput_invalid:A100-80GB:Qwen/Qwen3-8B:decode_tps"),
            (lambda m: m["seeds"].append(0), "matrix_duplicate_seeds"),
        ):
            broken = copy.deepcopy(matrix)
            mutation(broken)
            self.assertIn(expected, validate(broken))
            self.assertIsNone(estimate(broken, "A100-80GB").gpu_hours)
        self.assertIn("price_invalid", estimate(matrix, "A100-80GB",
                                                usd_per_gpu_hour=float("nan")).flags)
        self.assertIn("gpu_class_unknown", estimate(matrix, "other").flags)

    def test_budget_deletion_does_not_invent_fresh_energy(self):
        matrix, _ = load_matrix(CONFIG / "budget.json")
        # 32 items * (3 calibration + 3 seeds * 7 live conditions * 2 paired
        # generations) = 1440 episodes per model. All 11 conditions get monitors.
        for episodes, monitors in work_counts(matrix).values():
            self.assertEqual(episodes, 32 * (3 + 3 * 7 * 2))
            self.assertEqual(monitors, 32 * 3 * 11)


@unittest.skipUnless(shutil.which("bash"), "bootstrap requires Bash")
class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="joulewise-gpukit-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.old_env = dict(os.environ)
        self.addCleanup(self._restore_env)
        os.environ["PATH"] = str(self.bin) + os.pathsep + os.environ.get("PATH", "")
        os.environ["GPUKIT_READY"] = str(self.base / "ready")
        self._script("nvidia-smi", """#!/usr/bin/env python3
import os
mig = os.environ.get("GPUKIT_MIG", "Disabled")
mode = os.environ.get("GPUKIT_VIRT", "None")
print(f"<nvidia_smi_log><driver_version>fixture</driver_version><gpu>"
      f"<product_name>NVIDIA A100-SXM4-80GB</product_name><uuid>GPU-fixture</uuid>"
      f"<mig_mode><current_mig>{mig}</current_mig></mig_mode>"
      f"<gpu_virtualization_mode><virtualization_mode>{mode}</virtualization_mode>"
      f"</gpu_virtualization_mode></gpu></nvidia_smi_log>")
""")
        self._script("vllm", """#!/usr/bin/env python3
import os
from pathlib import Path
import time
Path(os.environ["GPUKIT_READY"]).write_text("ready")
while True:
    time.sleep(1)
""")
        self._script("fixture-python", """#!/usr/bin/env python3
import sys
if sys.argv[1:] == ["-m", "joulewise.align.power.preflight"]:
    print('{"flags": [], "fixture": true}')
    raise SystemExit(0)
raise SystemExit(1)
""")
        self.runner = self.base / "runner.py"
        self.runner.write_text(textwrap.dedent("""\
            import argparse
            from pathlib import Path
            from joulewise.align.records import Episode, PowerTrace, ToolCall, Turn, write_episodes
            parser = argparse.ArgumentParser()
            parser.add_argument("--matrix")
            parser.add_argument("--model")
            parser.add_argument("--endpoint")
            parser.add_argument("--output")
            args = parser.parse_args()
            import json
            matrix = json.loads(Path(args.matrix).read_text())
            episodes = []
            # 12 turns, eight tools, realistic token counts. Each turn is 11 s
            # inference plus 2 s tool wait for eight turns: 148 s total. This
            # synthetic clock runs in memory; no network, GPU or wall-time wait.
            for task in matrix["tasks"]:
                for condition in matrix["conditions"]:
                    for seed in matrix["seeds"]:
                        turns = []
                        cursor = 1_000_000_000
                        start = cursor
                        for i in range(12):
                            tool = ((ToolCall("fixture_lookup", cursor + 11_000_000_000,
                                              cursor + 13_000_000_000, 96, 2048),)
                                    if i < 8 else ())
                            end = cursor + (13 if tool else 11) * 1_000_000_000
                            turns.append(Turn(i, cursor, end, i * 2048,
                                              3333 if i < 11 else 3337,
                                              666 if i < 11 else 674,
                                              hidden_tokens=128 if condition == "sabotage" else 0,
                                              first_token_ns=cursor + 1_000_000_000,
                                              tool_calls=tool))
                            cursor = end
                        # 100 ms sampling matches the NVML documented period.
                        # 1 W alternating noise is a fixture parameter, not
                        # an accuracy claim. Tool waits reduce power by 80 W.
                        times = tuple(range(start, cursor + 1, 100_000_000))
                        watts = tuple(280.0 + (1.0 if n % 2 else -1.0)
                                      - (80.0 if any(c.start_ns <= t < c.end_ns
                                                   for turn in turns for c in turn.tool_calls) else 0.0)
                                      for n, t in enumerate(times))
                        trace = PowerTrace("mock", "gpu0", "fixture:monotonic", times, watts,
                                           "W", 100_000_000, resolution=1.0,
                                           notes="synthetic, no hardware measurement")
                        episodes.append(Episode(
                            f"{args.model}:{task}:{condition}:{seed}", task, condition,
                            args.model, args.endpoint, seed, "fixture:monotonic",
                            start, cursor, tuple(turns), power_traces=(trace,)))
            write_episodes(Path(args.output), episodes)
            """), encoding="utf-8")

    def _restore_env(self):
        os.environ.clear()
        os.environ.update(self.old_env)

    def _script(self, name, text):
        path = self.bin / name
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)

    def _options(self, name="session", **changes):
        # The 30 s fixture subprocess budget and 10 ms poll are test-runner
        # scheduling parameters; no physics threshold depends on either.
        values = dict(matrix=CONFIG / "shade.json", output=self.base / name,
                      runner_command=(sys.executable, str(self.runner), "--matrix", "{matrix}",
                                      "--model", "{model}", "--endpoint", "{endpoint}",
                                      "--output", "{output}"),
                      preflight_command=("fixture-python", "-m", "joulewise.align.power.preflight"),
                      ready_command=(sys.executable, "-c",
                                     'import os,sys; sys.exit(not os.path.exists(os.environ["GPUKIT_READY"]))'),
                      ready_timeout_s=30.0, command_timeout_s=30.0, poll_s=0.01)
        values.update(changes)
        return SessionOptions(**values)

    def test_shell_bootstrap_end_to_end(self):
        options = self._options(destination=str(self.base / "returned"), copy_kind="local")
        command = ["bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"), "--skip-install",
                   str(options.matrix), "--output", str(options.output),
                   "--runner-command", json.dumps(options.runner_command),
                   "--preflight-command", json.dumps(options.preflight_command),
                   "--ready-command", json.dumps(options.ready_command),
                   "--ready-timeout-s", "30", "--command-timeout-s", "30", "--poll-s", "0.01",
                   "--destination", options.destination, "--copy-kind", "local"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "completed_with_flags")
        self.assertEqual(receipt["preflight_returncode"], 0)
        self.assertTrue(receipt["data_complete"])
        self.assertEqual(receipt["transfer_flags"], [])
        self.assertNotIn("runner_output_unreadable", " ".join(receipt["flags"]))
        self.assertNotIn("runner_episode_count_mismatch", receipt["flags"])
        self.assertNotIn("episode_power_missing", receipt["flags"])
        self.assertEqual(verify_manifest(options.output), ())
        episodes = []
        for path in sorted(options.output.glob("model-*/episodes.jsonl")):
            episodes.extend(read_episodes(path))
        self.assertEqual(len(episodes), 5 * 2 * 2 * 3)
        for episode in episodes:
            self.assertEqual(episode.totals()["prefill_tokens"], 40000)
            self.assertEqual(episode.totals()["decode_tokens"], 8000)
            self.assertEqual(episode.totals()["tool_calls"], 8)
            self.assertEqual(episode.totals()["turns"], 12)
            self.assertEqual(episode.totals()["duration_ns"], 148_000_000_000)
            self.assertEqual(len(episode.power_traces[0].t_ns), 1481)
            trace = episode.power_traces[0]
            energy = math.fsum((b - a) / 1e9 * (u + v) / 2
                               for a, b, u, v in zip(trace.t_ns, trace.t_ns[1:],
                                                     trace.values, trace.values[1:]))
            # 148 s * 280 W - eight 2 s tool waits * 80 W = 40160 J.
            # Alternating +/-1 W cancels over each adjacent sample interval.
            # Prescribed 1e-6 relative arithmetic bar, no measurement uncertainty.
            self.assertTrue(math.isclose(energy, 40160.0, rel_tol=1e-6))
        archive = Path(receipt["archive"])
        returned = self.base / "returned" / archive.name
        # Exact bytes/hash equality is the custody property, not float agreement.
        self.assertEqual(hashlib.sha256(returned.read_bytes()).digest(),
                         hashlib.sha256(archive.read_bytes()).digest())
        sample = options.output / "model-0/episodes.jsonl"
        sample.write_text(sample.read_text() + "\n", encoding="utf-8")
        self.assertIn("manifest_bytes_changed:model-0/episodes.jsonl",
                      verify_manifest(options.output))

    def test_isolation_explicit_refusal_and_unknown_flags(self):
        os.environ["GPUKIT_MIG"] = "Enabled"
        with self.assertRaises(IsolationError):
            whole_gpu(gpu_index=0, timeout_s=30)
        receipt = run_session(self._options("mig"))
        self.assertEqual(receipt["status"], "refused")
        self.assertIn("whole_gpu_required", receipt["flags"])
        self.assertFalse(receipt["data_complete"])
        self.assertEqual(verify_manifest(self.base / "mig"), ())
        os.environ["GPUKIT_MIG"] = "Disabled"
        os.environ["GPUKIT_VIRT"] = "VGPU"
        with self.assertRaises(IsolationError):
            whole_gpu(gpu_index=0, timeout_s=30)
        os.environ["GPUKIT_VIRT"] = "N/A"
        self.assertIn("gpu_virtualization_unverified",
                      whole_gpu(gpu_index=0, timeout_s=30)["flags"])

    def test_missing_preflight_runner_output_and_router_are_flags(self):
        options = self._options("failure", preflight_command=("missing-preflight",),
                                runner_command=(sys.executable, "-c", "pass"))
        receipt = run_session(options)
        self.assertIn("nvml_preflight_failed", receipt["flags"])
        self.assertFalse(receipt["data_complete"])
        self.assertIn("runner_output_unreadable:FileNotFoundError", receipt["flags"])
        self.assertNotEqual(receipt["status"], "refused")
        self.assertEqual(verify_manifest(options.output), ())
        # A real matrix expansion through the same production session, with
        # episode output but missing router records, must advertise the gap.
        moe = run_session(self._options("moe", matrix=CONFIG / "moe_stage_a.json"))
        self.assertIn("episode_router_log_missing", moe["flags"])
        self.assertFalse(moe["data_complete"])
        self.assertNotIn("runner_episode_count_mismatch", moe["flags"])

    def test_readiness_failure_still_seals_evidence(self):
        self._script("vllm", "#!/usr/bin/env python3\nraise SystemExit(1)\n")
        options = self._options("not-ready", ready_command=(sys.executable, "-c", "raise SystemExit(1)"))
        receipt = run_session(options)
        self.assertIn("endpoint_exited_before_ready", receipt["flags"])
        self.assertEqual(verify_manifest(options.output), ())

    def test_shell_installation_uses_pinned_vllm_and_repository(self):
        calls = self.base / "install-calls.jsonl"
        wrapper = self.bin / "install-python"
        # Fake venv and pip only; the production shell still selects its actual
        # code path. The separate end-to-end test runs the real session module.
        wrapper.write_text(
            "#!" + sys.executable + "\n"
            + "import json, os, pathlib, sys\n"
            + "args = sys.argv[1:]\n"
            + f"with open({str(calls)!r}, 'a') as h: h.write(json.dumps(args) + '\\n')\n"
            + "if args[:2] == ['-m', 'venv']:\n"
            + "    target = pathlib.Path(args[2]) / 'bin'\n"
            + "    target.mkdir(parents=True)\n"
            + "    dest = target / 'python'\n"
            + "    dest.write_bytes(pathlib.Path(__file__).read_bytes())\n"
            + "    dest.chmod(0o755)\n"
            + "elif args[:2] == ['-m', 'pip']:\n"
            + "    pass\n"
            + "elif args[:2] == ['-m', 'joulewise.align.gpukit.session']:\n"
            + "    print('session reached')\n"
            + "else:\n"
            + f"    os.execv({sys.executable!r}, [{sys.executable!r}, *args])\n",
            encoding="utf-8")
        wrapper.chmod(0o755)
        env = dict(os.environ, JOULEWISE_PYTHON=str(wrapper),
                   JOULEWISE_VENV=str(self.base / "venv"))
        result = subprocess.run(["bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"),
                                 "--fixture-session-argument"], cwd=ROOT, env=env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        recorded = [json.loads(line) for line in calls.read_text().splitlines()]
        self.assertIn(["-m", "pip", "install", "vllm==0.10.2"], recorded)
        self.assertIn(["-m", "pip", "install", "--no-deps", str(ROOT)], recorded)
        self.assertIn(["-m", "joulewise.align.gpukit.session",
                       "--fixture-session-argument"], recorded)

    def test_existing_output_is_preserved(self):
        options = self._options("preserved")
        options.output.mkdir()
        marker = options.output / "marker"
        marker.write_text("original", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            run_session(options)
        self.assertEqual(marker.read_text(), "original")

    def test_package_inventory_checks_unexpected_and_unsafe_paths(self):
        output = self.base / "package"
        output.mkdir()
        (output / "a").write_text("evidence", encoding="utf-8")
        archive, checksum = package_results(output)
        self.assertTrue(archive.is_file())
        self.assertTrue(checksum.is_file())
        self.assertEqual(verify_manifest(output), ())
        (output / "extra").write_text("extra", encoding="utf-8")
        self.assertIn("manifest_inventory_changed", verify_manifest(output))
        data = json.loads((output / "manifest.json").read_text())
        data["files"][0]["path"] = "../outside"
        (output / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("manifest_path_invalid", verify_manifest(output))
