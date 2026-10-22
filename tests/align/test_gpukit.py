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

from joulewise.align.gpukit.cost import estimate, printable, work_counts
from joulewise.align.gpukit.throughput import ceilings
from joulewise.align.gpukit.runner_adapter import runner_matrix, write_runner_matrix
from joulewise.align.gpukit.matrix import expand, load_matrix, validate
from joulewise.align.gpukit.session import (
    IsolationError, SessionOptions, package_results, run_session, verify_manifest, whole_gpu,
)
from joulewise.align.records import read_episodes

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "align"


def planning_fixture(matrix):
    """Explicit synthetic volumes/allowances, never committed production estimates."""
    value = copy.deepcopy(matrix)
    value["workload"].update(prefill_tokens=40000, decode_tokens=8000,
                             tool_wait_s=16, host_overhead_s=12,
                             monitor_prefill_tokens=8000, monitor_decode_tokens=32,
                             derivation="Synthetic fixture inputs: 12 turns, eight 2 s tools; not SHADE measurements.")
    for gpu in value["gpu_classes"].values():
        gpu.update(setup_s=1800, model_load_s=180, router_overhead_fraction=0.25,
                   derivation="Explicit synthetic setup/load/router parameters; not observed hardware.")
    return value


class MatrixTests(unittest.TestCase):
    def test_committed_matrices_counts_and_printed_wall_estimates(self):
        for name, rows, episodes, monitors in (
                ("shade", 60, 60, 180), ("moe_stage_a", 30, 30, 90),
                ("budget", 26400, 36000, 26400)):
            with self.subTest(name=name):
                matrix, flags = load_matrix(CONFIG / (name + ".json"))
                self.assertEqual(flags, ())
                self.assertEqual(len(expand(matrix)), rows)  # Integer Cartesian row identity.
                self.assertEqual(matrix["measured_episode_count"], episodes)
                self.assertEqual(matrix["monitor_call_count"], monitors)
                for gpu, printed in matrix["lower_bound_wall_seconds"].items():
                    self.assertIsNone(printed)
                    unavailable = estimate(matrix, gpu)
                    self.assertIsNone(unavailable.lower_bound_wall_seconds)
                    self.assertIn("workload_token_volumes_unavailable:prefill_tokens,decode_tokens", unavailable.flags)
                    result = estimate(planning_fixture(matrix), gpu)
                    self.assertEqual(result.measured_episodes, episodes)
                    self.assertEqual(result.monitor_calls, monitors)
                    # Printed bound is rounded downward at two significant digits.
                    # A rounding cell spans 10^(floor(log10(bound))-1) seconds.
                    quantum = 10 ** (math.floor(math.log10(result.lower_bound_wall_seconds)) - 1)
                    printed = math.floor(result.lower_bound_wall_seconds / quantum) * quantum
                    self.assertLessEqual(printed, result.lower_bound_wall_seconds)
                    self.assertLess(result.lower_bound_wall_seconds, printed + quantum)
                    self.assertIsNone(matrix["planning_wall_seconds"][gpu])
                    self.assertIsNone(result.wall_seconds)
                    self.assertIsNone(result.gpu_hours)
                    self.assertIsNone(result.total_usd)
                    self.assertIn("price_not_supplied", result.flags)
                    self.assertIn("throughput_efficiency_not_supplied", result.flags)
                    self.assertEqual(printable(result)["lower_bound_wall_seconds"], printed)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "optional jsonschema is not installed")
    def test_json_schema(self):
        import jsonschema
        schema = json.loads((ROOT / "joulewise/align/gpukit/matrix.schema.json").read_text())
        for name in ("shade", "moe_stage_a", "budget"):
            matrix, _ = load_matrix(CONFIG / (name + ".json"))
            jsonschema.Draft202012Validator(schema).validate(matrix)

    def test_independent_hand_arithmetic(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        matrix = planning_fixture(matrix)
        # NVIDIA A100 datasheet p1 SXM4 80GB: 2039 GB/s, dense BF16 312 TFLOPS.
        # https://images.nvidia.com/data-center/a100/a100-datasheet.pdf (2026-10-22)
        # HF model cards (same access date): Qwen3-8B 8.2B, 30B-A3B 3.3B
        # active (30.5B total), monitor Qwen3-4B 4.0B.
        # Closed form: each weight uses 2 BF16 bytes and 2 multiply-add FLOPs.
        # Five pairs * two conditions * three seeds = 30 episodes/model;
        # three visibilities * 60 episodes = 180 monitor calls.
        bandwidth, flops = 2039 * 10**9, 312 * 10**12
        agent_bound = 30 * (40000 * 2 * (8.2e9 + 3.3e9) / flops
                            + 8000 * 2 * (6.95e9 + 151936 * 4096
                                         + 3.3e9 - 151936 * 2048) / bandwidth)
        monitor_bound = 0  # Off-box scoring contributes zero agent-GPU token work (R2).
        seconds = agent_bound + monitor_bound
        price_input = 2.0  # An explicit test price parameter, never a provider quote.
        result = estimate(matrix, "A100-SXM4-80GB", usd_per_gpu_hour=price_input)
        # Prescribed 1e-6 relative agreement bar: no measurement uncertainty.
        self.assertTrue(math.isclose(result.lower_bound_wall_seconds, seconds, rel_tol=1e-6))
        self.assertTrue(math.isclose(result.lower_bound_total_usd, seconds / 3600 * price_input,
                                     rel_tol=1e-6))
        self.assertIsNone(result.total_usd)
        # Test-only synthetic efficiency: observed time = twice the ideal time,
        # hence achieved rate / ceiling = 1/2. This is not public performance.
        for rate in matrix["gpu_classes"]["A100-SXM4-80GB"]["throughput"].values():
            rate.update(efficiency=1 / 2, efficiency_source={
                "url": "https://github.com/mpmdw/JouleWise/blob/lane/2026-10-21-align-gpukit/tests/align/test_gpukit.py",
                "accessed": "2026-10-22", "note": "Synthetic twice-ideal-duration fixture only."})
        planned = estimate(matrix, "A100-SXM4-80GB", usd_per_gpu_hour=price_input)
        # Synthetic explicit allowances: 1800 setup, two 180 s loads, and
        # 60 agent episodes with 16 s tool waits + 12 s host overhead.
        planned_seconds = 2 * seconds + 1800 + 2 * 180 + 60 * (16 + 12)
        self.assertTrue(math.isclose(planned.wall_seconds, planned_seconds, rel_tol=1e-6))
        self.assertTrue(math.isclose(planned.total_usd, planned_seconds / 3600 * price_input,
                                     rel_tol=1e-6))
        self.assertNotIn("throughput_efficiency_not_supplied", planned.flags)
        for model in matrix["models"]:
            model["tensor_parallel_size"] = 2
        # Synthetic aggregate efficiency halves on two devices: same wall time,
        # twice the held GPU count. No TP performance claim is made.
        for rate in matrix["gpu_classes"]["A100-SXM4-80GB"]["throughput"].values():
            rate["efficiency"] /= 2
        doubled = estimate(matrix, "A100-SXM4-80GB", usd_per_gpu_hour=price_input)
        # Two allocated devices bill twice the GPU-hours; no speedup assumed.
        self.assertTrue(math.isclose(doubled.gpu_hours, planned.gpu_hours * 2, rel_tol=1e-6))
        self.assertTrue(math.isclose(doubled.wall_seconds, planned.wall_seconds, rel_tol=1e-6))

    def test_static_missing_input_flags_are_recomputed(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        missing = estimate(matrix, "A100-SXM4-80GB")
        self.assertIn("throughput_efficiency_not_supplied", missing.flags)
        self.assertIn("workload_token_volumes_unavailable:prefill_tokens,decode_tokens",
                      missing.flags)
        supplied = planning_fixture(matrix)
        # Explicit synthetic achieved rate is one half the ideal ceiling;
        # other GPU classes retain null efficiency and cannot taint this estimate.
        for rate in supplied["gpu_classes"]["A100-SXM4-80GB"]["throughput"].values():
            rate.update(efficiency=1 / 2, efficiency_source={
                "url": "https://github.com/mpmdw/JouleWise/blob/lane/2026-10-21-align-gpukit/tests/align/test_gpukit.py",
                "accessed": "2026-10-22", "note": "Synthetic twice-ideal-duration fixture only."})
        current = estimate(supplied, "A100-SXM4-80GB")
        self.assertNotIn("throughput_efficiency_not_supplied", current.flags)
        self.assertFalse(any(f.startswith("workload_token_volumes_unavailable")
                             for f in current.flags))
        self.assertIn("provisional_planning_inputs", current.flags)
        # One missing active-model efficiency must still flag the selected class.
        first = supplied["models"][0]["id"]
        supplied["gpu_classes"]["A100-SXM4-80GB"]["throughput"][first]["efficiency"] = None
        self.assertIn("throughput_efficiency_not_supplied",
                      estimate(supplied, "A100-SXM4-80GB").flags)

    def test_bad_inputs_are_flags(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        for mutation, expected in (
            (lambda m: m.update(episode_count=1), "matrix_episode_count_mismatch"),
            (lambda m: m["gpu_classes"]["A100-SXM4-80GB"]["throughput"]
             ["Qwen/Qwen3-8B"].update(efficiency=0),
             "matrix_throughput_efficiency_invalid:A100-SXM4-80GB:Qwen/Qwen3-8B"),
            (lambda m: m["seeds"].append(0), "matrix_duplicate_seeds"),
        ):
            broken = copy.deepcopy(matrix)
            mutation(broken)
            self.assertIn(expected, validate(broken))
            self.assertIsNone(estimate(broken, "A100-SXM4-80GB").lower_bound_wall_seconds)
        self.assertIn("price_invalid", estimate(matrix, "A100-SXM4-80GB",
                                                usd_per_gpu_hour=float("nan")).flags)
        self.assertIn("gpu_class_unknown", estimate(matrix, "other").flags)
        rate = matrix["gpu_classes"]["A100-SXM4-80GB"]["throughput"]["Qwen/Qwen3-8B"]
        rate["efficiency"] = 1 / 2  # Positive synthetic parameter without required citation.
        self.assertIn("matrix_throughput_efficiency_source_missing:A100-SXM4-80GB:Qwen/Qwen3-8B",
                      validate(matrix))

    def test_sku_ceilings_and_missing_source(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        # H100 NVIDIA datasheet p1: 1979 sparse TFLOPS / 2 = dense BF16,
        # 3.35 TB/s. HF card active 3.3B, not the 30.5B resident total.
        prefill, decode = ceilings(matrix, "H100-SXM-80GB", "Qwen/Qwen3-30B-A3B")
        # No uncertainty on arithmetic: prescribed 1e-6 relative agreement.
        self.assertTrue(math.isclose(prefill, (1979e12 / 2) / (2 * 3.3e9), rel_tol=1e-6))
        self.assertTrue(math.isclose(decode, 3.35e12 / (2 * (3.3e9 - 151936 * 2048)), rel_tol=1e-6))
        # MoE total weights occupy 30.5B * 2 bytes, above L40S's 48GB,
        # while the ceiling calculation correctly uses only active weights.
        l40 = estimate(matrix, "L40S-PCIe-48GB")
        self.assertIn("model_bf16_weights_exceed_device_memory:Qwen/Qwen3-30B-A3B", l40.flags)
        matrix["gpu_classes"]["H100-SXM-80GB"]["hardware"]["memory_bandwidth_bytes_s"]["value"] = None
        result = estimate(matrix, "H100-SXM-80GB")
        self.assertIn("throughput_source_unavailable", result.flags)
        self.assertIsNone(result.lower_bound_wall_seconds)
        self.assertIsNone(result.wall_seconds)

    def test_budget_deletion_does_not_invent_fresh_energy(self):
        matrix, _ = load_matrix(CONFIG / "budget.json")
        # 200 items * (3 calibration + 3 seeds * 7 live conditions * 2 paired
        # generations) = 9000 episodes per model. All 11 conditions get monitors.
        for episodes, monitors in work_counts(matrix).values():
            self.assertEqual(episodes, 200 * (3 + 3 * 7 * 2))
            self.assertEqual(monitors, 200 * 3 * 11)


class RunnerAdapterTests(unittest.TestCase):
    def test_documented_matrix_keys_and_round_trip(self):
        matrix, _ = load_matrix(CONFIG / "moe_stage_a.json")
        # Run limits/order are explicit synthetic inputs, not production cutoffs.
        settings = dict(task_factory="fixture.task", endpoint_factory="fixture.endpoint",
                        monitor_factory="fixture.monitor", sampler_factory="fixture.power",
                        token_counter_factory="fixture.tokens", max_turns=12,
                        max_tokens=8000, order_seed=0, temperature=0.0,
                        imports=["fixture.factories"],
                        endpoint_config={"custom": "retained", "router_logging": "{router_logging}"},
                        sampler_config={"interval_ns": "{interval_ns}"})
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "model-0"
            value, flags = runner_matrix(matrix, model=matrix["models"][0]["id"],
                                         endpoint="http://127.0.0.1:8000", output_dir=output,
                                         settings=settings, session_id="fixed-fixture-session",
                                         monitor_endpoint="http://offbox.example")
            self.assertEqual(flags, ("runner_adapter_provisional",))
            self.assertEqual(set(value), {
                "matrix_id", "order_seed", "task_pairs", "conditions", "seeds", "endpoints",
                "monitors", "samplers", "token_counter", "max_turns", "max_tokens",
                "temperature", "output_dir", "imports"})
            self.assertEqual(len(value["task_pairs"]) * len(value["conditions"]) * len(value["seeds"]), 30)
            self.assertEqual([x["task_pair"] for x in value["task_pairs"]], matrix["tasks"])
            self.assertEqual(value["monitors"][0]["visibilities"], matrix["monitor_visibilities"])
            self.assertEqual(value["samplers"][0]["config"]["interval_ns"], matrix["sampling"]["interval_ns"])
            self.assertTrue(value["endpoints"][0]["config"]["router_logging"])
            self.assertEqual(value["endpoints"][0]["config"]["custom"], "retained")
            path = Path(temporary) / "runner-matrix.json"
            written = write_runner_matrix(path, matrix, model=matrix["models"][0]["id"],
                                           endpoint="http://127.0.0.1:8000", output_dir=output,
                                           settings=settings, session_id="fixed-fixture-session",
                                           monitor_endpoint="http://offbox.example")
            self.assertEqual(written, flags)
            self.assertEqual(json.loads(path.read_text()), value)  # Exact serialization identity.

    def test_missing_factories_and_budget_are_flags(self):
        matrix, _ = load_matrix(CONFIG / "budget.json")
        value, flags = runner_matrix(matrix, model=matrix["models"][0]["id"],
                                     endpoint="http://127.0.0.1:8000", output_dir=Path("."),
                                     settings={})
        self.assertEqual(value, {})
        self.assertIn("budget_runner_adapter_required", flags)
        self.assertIn("runner_adapter_factory_missing:endpoint", flags)


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
        os.environ["JOULEWISE_PYTHON"] = sys.executable
        os.environ["JOULEWISE_PROBE_TIMEOUT_S"] = "30"
        os.environ["JOULEWISE_GPU_INDICES"] = "0"
        os.environ["GPUKIT_SERVER_CALLS"] = str(self.base / "servers.jsonl")
        os.environ["JOULEWISE_VENV"] = str(self.base / "session-venv")
        os.environ["PATH"] = str(self.bin) + os.pathsep + os.environ.get("PATH", "")
        # Child fixture scripts run from a temporary directory without an installed
        # package. Scope the source checkout path to this test and its children.
        os.environ["PYTHONPATH"] = str(ROOT) + (
            os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else "")
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
import time, json, sys
with open(os.environ["GPUKIT_SERVER_CALLS"], "a") as handle:
    handle.write(json.dumps({"argv": sys.argv[1:], "devices": os.environ["CUDA_VISIBLE_DEVICES"], "device_order": os.environ.get("CUDA_DEVICE_ORDER")}) + "\\n")
Path(os.environ["GPUKIT_READY"]).write_text("ready")
while True:
    time.sleep(1)
""")
        self._script("fixture-python", """#!/usr/bin/env python3
import sys, json, os
from pathlib import Path
if sys.argv[1:3] == ["-m", "joulewise.align.power.preflight"]:
    mode = os.environ.get("GK_PREFLIGHT", "ready")
    if mode == "missing":
        raise SystemExit(2)
    refused = mode == "refused"
    report = {"refused": refused, "measurement_ready": mode == "ready",
              "flags": ["fixture_not_ready"] if mode == "unready" else []}
    if mode == "no-readiness":
        report.pop("measurement_ready")
    elif mode == "string-readiness":
        report["measurement_ready"] = "true"
    elif mode == "numeric-readiness":
        report["measurement_ready"] = 1
    elif mode == "null-readiness":
        report["measurement_ready"] = None
    Path(sys.argv[sys.argv.index("--out") + 1]).write_text(json.dumps(report))
    raise SystemExit(2 if refused else 0)
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
                        trace = PowerTrace("nvml_power", "gpu0", "fixture:monotonic", times, watts,
                                           "W", 100_000_000, resolution=1.0,
                                           notes="synthetic, no hardware measurement")
                        episodes.append(Episode(
                            f"{args.model}:{task}:{condition}:{seed}", task, condition,
                            args.model, args.endpoint, seed, "fixture:monotonic",
                            start, cursor, tuple(turns), power_traces=(trace,)))
            import os
            from dataclasses import replace
            mode = os.environ.get("GK_EP_MODE", "complete")
            devices = [int(x) for x in os.environ.get("GK_DEVICES", "0").split(",")]
            episodes = [replace(e, power_traces=tuple(replace(e.power_traces[0], channel=f"gpu{i}")
                                                      for i in devices)) for e in episodes]
            if mode == "mock":
                episodes = [replace(e, power_traces=tuple(replace(p, source="mock")
                                                         for p in e.power_traces)) for e in episodes]
            elif mode == "duplicate":
                episodes = [replace(episodes[i % (len(episodes) // 2)], episode_id=f"dup:{i}")
                            for i in range(len(episodes))]
            elif mode == "short":
                episodes = episodes[:-1]
            elif mode == "onesample":
                episodes = [replace(e, power_traces=tuple(replace(p, t_ns=p.t_ns[:1], values=p.values[:1])
                                                         for p in e.power_traces)) for e in episodes]
            elif mode == "empty":
                episodes = [replace(e, turns=()) for e in episodes]
            elif mode == "failure":
                episodes = [replace(e, flags=("endpoint.error.AttributeError",)) for e in episodes]
            elif mode == "identity":
                episodes = [replace(e, agent_model="vllm:" + args.model + "@" + args.endpoint)
                            for e in episodes]
            elif mode == "wrong-model":
                episodes = [replace(e, agent_model="Qwen/Qwen3-14B") for e in episodes]
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
                      ready_timeout_s=30.0, command_timeout_s=30.0, runner_timeout_s=30.0,
                      monitor_placement="none", poll_s=0.01, preflight_timeout_s=30.0,
                      copy_timeout_s=30.0, stop_grace_s=5.0)
        values.update(changes)
        return SessionOptions(**values)

    def test_shell_bootstrap_end_to_end(self):
        options = self._options(destination=str(self.base / "returned"), copy_kind="local")
        command = ["bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"), "--skip-install",
                   str(options.matrix), "--output", str(options.output),
                   "--runner-command", json.dumps(options.runner_command),
                   "--preflight-command", json.dumps(options.preflight_command),
                   "--ready-command", json.dumps(options.ready_command),
                   "--ready-timeout-s", "30", "--command-timeout-s", "30",
                   "--preflight-timeout-s", "30", "--copy-timeout-s", "30", "--stop-grace-s", "5", "--poll-s", "0.01",
                   "--runner-timeout-s", "30", "--monitor-placement", "none",
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
        self.assertIn("nvml_preflight_unavailable", receipt["flags"])
        self.assertEqual(receipt["status"], "refused")
        self.assertEqual(receipt["models"], [])
        # With a readable non-refusing report, a failed runner remains a flag.
        receipt = run_session(self._options("runner-failure", runner_command=(sys.executable, "-c", "pass")))
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
        self.assertNotIn("runner_command_failed", moe["flags"])
        episodes = read_episodes(self.base / "moe/model-0/episodes.jsonl")
        self.assertEqual(len(episodes), 5 * 2 * 3)  # All requested integer trial rows.
        self.assertTrue(all(e.router_log is None and e.power_traces for e in episodes))
        self.assertEqual(moe["models"][0]["runner_returncode"], 0)

    def test_default_runner_emits_matrix_and_missing_settings_are_flags(self):
        missing = run_session(self._options("settings-missing", runner_command=()))
        self.assertIn("runner_settings_missing", missing["flags"])
        self.assertFalse(missing["data_complete"])
        self.assertEqual(verify_manifest(self.base / "settings-missing"), ())
        settings = self.base / "runner-settings.json"
        settings.write_text(json.dumps(dict(
            task_factory="fixture.task", endpoint_factory="fixture.endpoint",
            monitor_factory="fixture.monitor", sampler_factory="fixture.power",
            token_counter_factory="fixture.tokens", max_turns=12, max_tokens=8000,
            order_seed=0, temperature=0.0)), encoding="utf-8")
        # The runner lane is absent on the spine. Its CLI should be attempted
        # through the real subprocess path, preserving failure and translated
        # matrices. If an integrated checkout has it, unknown fixture factories
        # still yield flagged episodes rather than scientific data.
        options = self._options("default-runner", runner_command=(), runner_settings=settings)
        receipt = run_session(options)
        self.assertIn("runner_adapter_provisional", receipt["flags"])
        self.assertFalse(receipt["data_complete"])
        for path in sorted(options.output.glob("model-*/runner-matrix.json")):
            value = json.loads(path.read_text())
            self.assertEqual(value["output_dir"], str(path.parent))
            self.assertEqual(value["samplers"][0]["factory"], "fixture.power")
        self.assertEqual(len(list(options.output.glob("model-*/runner-matrix.json"))), 2)
        self.assertEqual(verify_manifest(options.output), ())

    def test_default_budget_keeps_requested_conditions_as_flags(self):
        settings = self.base / "budget-settings.json"
        settings.write_text(json.dumps(dict(
            task_factory="fixture.task", endpoint_factory="fixture.endpoint",
            monitor_factory="fixture.monitor", sampler_factory="fixture.power",
            token_counter_factory="fixture.tokens", max_turns=12, max_tokens=8000,
            order_seed=0, temperature=0.0)), encoding="utf-8")
        options = self._options("budget-default", matrix=CONFIG / "budget.json",
                                runner_command=(), runner_settings=settings)
        receipt = run_session(options)
        self.assertIn("budget_runner_adapter_required", receipt["flags"])
        self.assertFalse(receipt["data_complete"])
        kept = json.loads((options.output / "matrix.json").read_text())
        self.assertIn("thinking_on", kept["conditions"])
        self.assertEqual(verify_manifest(options.output), ())

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
            + "    print(json.dumps({'measured_gpu_indices': [0], 'monitor_gpu_index': None}) if '--validate-only' in args else 'session reached')\n"
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
        self.assertIn(["-m", "joulewise.align.gpukit.session", "--gpu-indices", "0",
                       "--fixture-session-argument"], recorded)
        # Second session must select the existing venv, even when the original
        # creator/system interpreter is unavailable. No new install is allowed.
        calls.write_text("", encoding="utf-8")
        env.pop("JOULEWISE_PYTHON")
        result = subprocess.run(
            ["bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"),
             "--skip-install", "--fixture-session-argument"],
            cwd=self.base, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        recorded = [json.loads(line) for line in calls.read_text().splitlines()]
        self.assertEqual(recorded[-1], ["-m", "joulewise.align.gpukit.session", "--gpu-indices", "0",
                                       "--fixture-session-argument"])
        self.assertFalse(any(args[:2] in (["-m", "venv"], ["-m", "pip"])
                             for args in recorded))

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


    def test_complete_positive_control_and_large_failure_worlds(self):
        # Every fixture episode spans 148 s at 100 ms cadence; removing all but
        # one sample exceeds the I+W=100 ms coverage bar by nearly 148 s.
        complete = run_session(self._options("complete-positive"))
        self.assertTrue(complete["data_complete"])
        self.assertIn("monitoring_deferred", complete["flags"])
        self.assertIn("judging_deferred", complete["flags"])
        for mode, reason in (
                ("mock", "episode_power_mock"),
                ("duplicate", "runner_episode_coordinates_mismatch"),
                ("short", "runner_episode_count_mismatch"),
                ("onesample", "episode_power_coverage_incomplete"),
                ("empty", "episode_turns_missing"),
                ("failure", "endpoint.error.AttributeError")):
            os.environ["GK_EP_MODE"] = mode
            result = run_session(self._options("defect-" + mode))
            self.assertFalse(result["data_complete"], mode)
            self.assertIn(reason, result["flags"])
            self.assertEqual(verify_manifest(self.base / ("defect-" + mode)), ())

    def test_preflight_report_verdicts_and_no_runner_on_refusal(self):
        marker = self.base / "runner-marker"
        # C2 amends R4: false, absent and non-boolean readiness now refuse.
        for mode, flag in (("refused", "nvml_preflight_refused"),
                           ("missing", "nvml_preflight_unavailable"),
                           ("no-readiness", "nvml_measurement_not_ready"),
                           ("string-readiness", "nvml_measurement_not_ready"),
                           ("numeric-readiness", "nvml_measurement_not_ready"),
                           ("null-readiness", "nvml_measurement_not_ready"),
                           ("unready", "nvml_measurement_not_ready")):
            os.environ["GK_PREFLIGHT"] = mode
            options = self._options("preflight-" + mode, runner_command=(
                sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"))
            result = run_session(options)
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["data_complete"])
            self.assertIn(flag, result["flags"])
            self.assertFalse(marker.exists())
            self.assertEqual(list(options.output.glob("model-*")), [])
            self.assertEqual(verify_manifest(options.output), ())
        self.assertFalse(result["preflight"]["refused"])
        self.assertFalse(result["preflight"]["measurement_ready"])
        self.assertIn("fixture_not_ready", result["flags"])
        self.assertTrue((options.output / "preflight.json").is_file())
        self.assertTrue(options.output.with_name(options.output.name + ".tar.gz").is_file())

    def test_preflight_refusal_cli_exit_two(self):
        import contextlib
        import io
        from joulewise.align.gpukit.session import main
        for mode in ("refused", "unready"):
            os.environ["GK_PREFLIGHT"] = mode
            options = self._options("preflight-cli-" + mode)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main([str(options.matrix), "--output", str(options.output),
                             "--ready-timeout-s", "30", "--command-timeout-s", "30",
                   "--preflight-timeout-s", "30", "--copy-timeout-s", "30", "--stop-grace-s", "5",
                             "--runner-timeout-s", "30", "--poll-s", "0.01",
                             "--monitor-placement", "none",
                             "--preflight-command", json.dumps(options.preflight_command),
                             "--runner-command", json.dumps(options.runner_command)])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "refused")
            self.assertEqual(verify_manifest(options.output), ())

    def test_endpoint_identity_model_and_different_model(self):
        os.environ["GK_EP_MODE"] = "identity"
        result = run_session(self._options("endpoint-identity"))
        self.assertTrue(result["data_complete"])
        self.assertNotIn("runner_episode_model_mismatch", result["flags"])
        os.environ["GK_EP_MODE"] = "wrong-model"
        result = run_session(self._options("wrong-model"))
        self.assertFalse(result["data_complete"])
        self.assertIn("runner_episode_model_mismatch", result["flags"])

    def test_offbox_gpu_served_once_and_not_sampled(self):
        settings = self.base / "placed-settings.json"
        settings.write_text(json.dumps(dict(
            task_factory="fixture.task", endpoint_factory="fixture.endpoint",
            monitor_factory="fixture.monitor", sampler_factory="fixture.power",
            token_counter_factory="fixture.tokens", max_turns=40, max_tokens=600,
            order_seed=7, temperature=0.0,
            endpoint_config={"base_url": "{agent_base_url}", "model": "{agent_model}"},
            monitor_config={"base_url": "{monitor_base_url}", "model": "{monitor_model}"},
            sampler_config={"device_indices": "{device_indices}"})), encoding="utf-8")
        options = self._options("offbox-gpu", monitor_placement="gpu", monitor_gpu_index=1,
                                monitor_port=8001, runner_settings=settings)
        result = run_session(options)
        self.assertTrue(result["data_complete"])
        calls = [json.loads(line) for line in (self.base / "servers.jsonl").read_text().splitlines()]
        self.assertTrue(all(call["device_order"] == "PCI_BUS_ID" for call in calls))
        self.assertEqual([c["devices"] for c in calls].count("1"), 1)
        self.assertEqual([c["devices"] for c in calls].count("0"), 2)
        self.assertEqual({r["gpu_index"] for r in result["hardware"]}, {0, 1})
        argv = result["preflight_argv"]
        self.assertEqual([argv[i + 1] for i, a in enumerate(argv) if a == "--device"], ["0"])
        for path in options.output.glob("model-*/runner-matrix.json"):
            matrix = json.loads(path.read_text())
            self.assertEqual(matrix["monitors"][0]["config"]["base_url"], "http://127.0.0.1:8001/v1")
            self.assertEqual(matrix["samplers"][0]["config"]["device_indices"], [0])
        self.assertNotIn("monitoring_deferred", result["flags"])

    def test_tensor_parallel_verifies_and_samples_all_measured_devices(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        matrix["models"] = [matrix["models"][0]]
        matrix["models"][0]["tensor_parallel_size"] = 2
        matrix.update(episode_count=30, measured_episode_count=30, monitor_call_count=90)
        path = self.base / "parallel.json"
        path.write_text(json.dumps(matrix))
        os.environ["GK_DEVICES"] = "2,4"
        result = run_session(self._options("parallel", matrix=path, gpu_indices=(2, 4)))
        self.assertTrue(result["data_complete"])
        self.assertEqual({r["gpu_index"] for r in result["hardware"]}, {2, 4})
        argv = result["preflight_argv"]
        self.assertEqual([argv[i + 1] for i, a in enumerate(argv) if a == "--device"], ["2", "4"])
        calls = [json.loads(line) for line in (self.base / "servers.jsonl").read_text().splitlines()]
        self.assertTrue(all(call["device_order"] == "PCI_BUS_ID" for call in calls))
        self.assertEqual(calls[0]["devices"], "2,4")
        argv = calls[0]["argv"]
        self.assertEqual(argv[argv.index("--tensor-parallel-size") + 1], "2")
        os.environ["GK_DEVICES"] = "2"
        incomplete = run_session(self._options("parallel-missing", matrix=path, gpu_indices=(2, 4)))
        self.assertFalse(incomplete["data_complete"])
        self.assertIn("episode_measured_device_power_missing:4", incomplete["flags"])

    def test_runner_timeout_kills_grandchild(self):
        marker = self.base / "grandchild"
        code = ("import subprocess,time; from pathlib import Path; "
                "p=subprocess.Popen(['sleep','300']); "
                f"Path({str(marker)!r}).write_text(str(p.pid)); time.sleep(300)")
        # Five seconds is explicit test scheduling policy, not a measured cutoff.
        result = run_session(self._options("hang", matrix=CONFIG / "moe_stage_a.json",
                                           runner_command=(sys.executable, "-c", code),
                                           runner_timeout_s=5.0))
        self.assertIn("runner_timeout", result["flags"])
        self.assertFalse(result["data_complete"])
        pid = int(marker.read_text())
        status = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)],
                                capture_output=True, text=True, check=False)
        self.assertFalse(status.stdout.strip() and not status.stdout.lstrip().startswith("Z"))

    def test_bootstrap_flag_order_and_passthrough(self):
        for virt in ("Pass-Through", "pass through", "passthrough"):
            os.environ["GPUKIT_VIRT"] = virt
            self.assertEqual(whole_gpu(gpu_index=0, timeout_s=30)["flags"], [])
        for args in (["--skip-install", "--check-only"], ["--check-only", "--skip-install"]):
            result = subprocess.run(["bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"), *args],
                                    cwd=self.base, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)


    def test_throttle_snapshots_on_real_session_path(self):
        for mode in ("clear", "active", "advance", "missing"):
            marker = self.base / ("throttle-sequence-" + mode)
            self._script("nvidia-smi", """#!/usr/bin/env python3
import os
from pathlib import Path
p = Path(os.environ["GK_THROTTLE_SEQUENCE"])
n = int(p.read_text()) + 1 if p.exists() else 0
p.write_text(str(n))
mode = os.environ["GK_THROTTLE_MODE"]
active = "Active" if mode == "active" else "Not Active"
duration = n if mode == "advance" else 0
extra = "" if mode == "missing" else (
    "<clocks_event_reasons>"
    f"<clocks_event_reason_hw_slowdown>{active}</clocks_event_reason_hw_slowdown>"
    f"<clocks_event_reason_hw_power_brake_slowdown>{active}</clocks_event_reason_hw_power_brake_slowdown>"
    "<clocks_event_reason_sw_power_cap>Not Active</clocks_event_reason_sw_power_cap>"
    "</clocks_event_reasons><clocks_event_reasons_counters>"
    f"<clocks_event_reasons_counters_hw_power_brake>{duration} us</clocks_event_reasons_counters_hw_power_brake>"
    "<clocks_event_reasons_counters_hw_therm_slowdown>0 us</clocks_event_reasons_counters_hw_therm_slowdown>"
    f"<clocks_event_reasons_counters_sw_power_cap>{duration} us</clocks_event_reasons_counters_sw_power_cap>"
    "</clocks_event_reasons_counters><gpu_power_readings>"
    "<default_power_limit>400.00 W</default_power_limit>"
    "<enforced_power_limit>350.00 W</enforced_power_limit>"
    "<current_power_limit>350.00 W</current_power_limit></gpu_power_readings>")
print("<nvidia_smi_log><gpu><mig_mode><current_mig>Disabled</current_mig></mig_mode>"
      "<gpu_virtualization_mode><virtualization_mode>None</virtualization_mode>"
      "</gpu_virtualization_mode>" + extra + "</gpu></nvidia_smi_log>")
""")
            os.environ["GK_THROTTLE_MODE"] = mode
            os.environ["GK_THROTTLE_SEQUENCE"] = str(marker)
            result = run_session(self._options("throttle-" + mode))
            self.assertTrue(result["data_complete"])
            self.assertNotEqual(result["status"], "refused")
            self.assertEqual(len(result["throttle_start"]), 1)
            change = result["models"][0]["throttle_changes"][0]
            if mode == "active":
                self.assertIn("throttle_hardware_active:hw_power_brake_slowdown", result["flags"])
            elif mode == "advance":
                self.assertIn("throttle_hardware_counter_advanced:hw_power_brake", result["flags"])
                # Counter quantum is one printed microsecond; >0 means at least one tick.
                self.assertGreater(int(change["counter_deltas_us"]["sw_power_cap"]), 0)
            elif mode == "missing":
                self.assertIn("throttle_reason_unavailable:hw_slowdown", result["flags"])
            else:
                self.assertEqual(change["counter_deltas_us"]["sw_power_cap"], "0")
                self.assertFalse(any(f.startswith("throttle_hardware_") for f in result["flags"]))
            self.assertTrue((self.base / ("throttle-" + mode) / "model-0/before-gpu0.xml").is_file())
            self.assertEqual(verify_manifest(self.base / ("throttle-" + mode)), ())


    def test_calibration_slice_extrapolates_real_episode_outputs(self):
        options = self._options("calibration-slice", calibration_slice=True)
        result = run_session(options)
        self.assertTrue(result["data_complete"])
        full, _ = load_matrix(CONFIG / "shade.json")
        projection = estimate(full, "H100-SXM-80GB", calibration=options.output)
        # Slice: 5 task pairs * 2 conditions * 1 seed * 2 models = 20.
        # Full: 60 Episodes, each exactly 148 s in this synthetic clock world.
        self.assertEqual(sum(row["observed_episodes"] for row in projection.calibration_basis.values()), 20)
        self.assertTrue(math.isclose(projection.generation_wall_seconds, 60 * 148, rel_tol=1e-6))
        for row in projection.calibration_basis.values():
            self.assertTrue(math.isclose(row["mean_prefill_tokens"], 40000, rel_tol=1e-6))
            self.assertTrue(math.isclose(row["mean_decode_tokens"], 8000, rel_tol=1e-6))
        self.assertIsNone(projection.wall_seconds)
        self.assertIn("calibration_setup_load_and_offbox_waits_unavailable", projection.flags)


    def test_v13_board_limits_on_session_path(self):
        self._script("nvidia-smi", """#!/usr/bin/env python3
print("<nvidia_smi_log><gpu><mig_mode><current_mig>Disabled</current_mig></mig_mode>"
      "<gpu_virtualization_mode><virtualization_mode>Pass-Through</virtualization_mode>"
      "</gpu_virtualization_mode><gpu_power_readings>"
      "<current_power_limit>700.00 W</current_power_limit>"
      "<requested_power_limit>650.00 W</requested_power_limit>"
      "<default_power_limit>700.00 W</default_power_limit></gpu_power_readings>"
      "<module_power_readings><current_power_limit>N/A</current_power_limit>"
      "</module_power_readings></gpu></nvidia_smi_log>")
""")
        result = run_session(self._options("v13-power-limits"))
        self.assertTrue(result["data_complete"], result["flags"])
        self.assertNotIn("throttle_power_limit_unavailable:enforced", result["flags"])
        for model in result["models"]:
            for snapshot in (*model["throttle_before"], *model["throttle_after"]):
                self.assertEqual(snapshot["power_limits"]["enforced"], "700.00 W")
                self.assertEqual(snapshot["power_limits"]["requested"], "650.00 W")



    def test_record_matrix_provenance_flag_still_collects(self):
        matrix = json.loads((CONFIG / "shade.json").read_text())
        matrix["workload"]["prefill_tokens"] = 40000  # Fixture's twelve-turn context work.
        matrix["workload"]["derivation"] = ""
        path = self.base / "unsourced.json"
        path.write_text(json.dumps(matrix))
        result = run_session(self._options("unsourced", matrix=path))
        self.assertTrue(result["data_complete"])
        self.assertEqual(result["status"], "completed_with_flags")
        self.assertIn("matrix_numeric_source_missing:workload.prefill_tokens", result["flags"])
        self.assertEqual(len(result["models"]), 2)
        self.assertIn("preflight_returncode", result)

    def test_stale_declared_counts_do_not_change_data_completeness(self):
        matrix = json.loads((CONFIG / "shade.json").read_text())
        # Two seeds generate 40 coordinates; retain the old declarations deliberately.
        matrix["seeds"] = [0, 1]
        path = self.base / "stale.json"
        path.write_text(json.dumps(matrix))
        result = run_session(self._options("stale", matrix=path))
        self.assertTrue(result["data_complete"])
        self.assertIn("matrix_measured_episode_count_mismatch", result["flags"])
        self.assertEqual([m["power_coverage"]["episodes_checked"] for m in result["models"]], [20, 20])

    def test_malformed_planning_section_still_collects(self):
        matrix = json.loads((CONFIG / "shade.json").read_text())
        matrix["workload"] = None
        path = self.base / "bad-planning.json"
        path.write_text(json.dumps(matrix))
        result = run_session(self._options("bad-planning", matrix=path))
        self.assertTrue(result["data_complete"])
        self.assertIn("matrix_planning_field_invalid", result["flags"])
        self.assertEqual(len(result["models"]), 2)

    def test_structural_condition_typo_fails_before_hardware(self):
        from unittest.mock import patch
        from joulewise.align.gpukit import session
        matrix = json.loads((CONFIG / "shade.json").read_text())
        matrix["conditions"] = ["benign", "attack"]
        path = self.base / "bad-condition.json"
        path.write_text(json.dumps(matrix))
        with patch.object(session, "whole_gpu") as hardware, patch.object(session, "_command") as command:
            result = run_session(self._options("bad-condition", matrix=path))
        self.assertEqual(result["status"], "failed")
        self.assertIn("matrix_conditions_invalid", result["flags"])
        self.assertEqual(result["models"], [])
        hardware.assert_not_called()
        command.assert_not_called()


    def test_budget_adapter_skip_is_failed_when_no_runner_started(self):
        result = run_session(self._options("budget-skips", matrix=CONFIG / "budget.json",
                                           runner_command=()))
        self.assertEqual(result["status"], "failed")
        self.assertIn("budget_runner_adapter_required", result["flags"])
        self.assertIn("session_ran_no_model", result["flags"])
        self.assertFalse(any("runner_returncode" in m for m in result["models"]))

    def test_argument_error_exits_three(self):
        from joulewise.align.gpukit.session import main
        with self.assertRaises(SystemExit) as raised:
            main(["--bad-arg"])
        self.assertEqual(raised.exception.code, 3)

    def test_validate_only_has_no_output_or_hardware_calls(self):
        from unittest.mock import patch
        from joulewise.align.gpukit.session import validate_session
        from joulewise.align.gpukit import session
        options = self._options("validate-only")
        with patch.object(session, "whole_gpu") as hardware, patch.object(session, "_command") as command:
            result = validate_session(options)
        self.assertEqual(result["structural_flags"], [])
        self.assertEqual(result["measured_gpu_indices"], [0])
        self.assertFalse(options.output.exists())
        hardware.assert_not_called()
        command.assert_not_called()



    def test_bootstrap_tp2_checks_mig_on_second_device_before_install(self):
        matrix = json.loads((CONFIG / "shade.json").read_text())
        matrix["models"][0]["tensor_parallel_size"] = 2
        path = self.base / "tp2.json"
        path.write_text(json.dumps(matrix))
        calls = self.base / "inventory.jsonl"
        self._script("nvidia-smi", "#!" + sys.executable + "\n" +
                     "import sys,json\n" +
                     f"with open({str(calls)!r}, 'a') as h: h.write(json.dumps(sys.argv[1:]) + '\\n')\n" +
                     "i = sys.argv[sys.argv.index('-i') + 1]\n" +
                     "mig = 'Enabled' if i == '1' else 'Disabled'\n" +
                     "print('<nvidia_smi_log><gpu><uuid>GPU-test</uuid><mig_mode><current_mig>' + mig + '</current_mig></mig_mode><gpu_virtualization_mode><virtualization_mode>None</virtualization_mode></gpu_virtualization_mode></gpu></nvidia_smi_log>')\n")
        result = subprocess.run([
            "bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"),
            "--gpu-index", "0", str(path), "--output", str(self.base / "tp2-run"),
            "--ready-timeout-s", "30", "--command-timeout-s", "30",
                   "--preflight-timeout-s", "30", "--copy-timeout-s", "30", "--stop-grace-s", "5",
            "--runner-timeout-s", "30", "--poll-s", "0.01", "--monitor-placement", "none"],
            cwd=self.base, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 2, result.stderr)
        indices = [json.loads(line)[1] for line in calls.read_text().splitlines()]
        self.assertEqual(indices, ["0", "1"])
        self.assertFalse((self.base / "session-venv").exists())
        self.assertFalse((self.base / "tp2-run").exists())

    def test_bootstrap_invalid_arguments_do_not_install(self):
        result = subprocess.run([
            "bash", str(ROOT / "joulewise/align/gpukit/bootstrap.sh"),
            str(CONFIG / "shade.json"), "--bad-arg"],
            cwd=self.base, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertFalse((self.base / "session-venv").exists())



    def test_preflight_timeout_and_probe_timeout_are_separate(self):
        delayed = self.base / "delayed-preflight.py"
        delayed.write_text(
            "import sys,time,json\nfrom pathlib import Path\n"
            "time.sleep(0.2)\n"
            "Path(sys.argv[sys.argv.index('--out')+1]).write_text(json.dumps("
            "{'refused':False,'measurement_ready':True,'flags':[]}))\n")
        command = (sys.executable, str(delayed))
        # Fixture scheduling limits: 50 ms expires before its explicit 200 ms sleep;
        # 30 s is the existing subprocess allowance, unrelated to a sensor bar.
        refused = run_session(self._options("preflight-timeout", preflight_command=command,
                                            preflight_timeout_s=0.05))
        self.assertEqual(refused["status"], "refused")
        self.assertIn("nvml_preflight_timeout", refused["flags"])
        self.assertNotIn("nvml_preflight_unavailable", refused["flags"])
        complete = run_session(self._options("preflight-separate", preflight_command=command,
                                             command_timeout_s=0.05, preflight_timeout_s=30.0))
        self.assertTrue(complete["data_complete"])
        self.assertNotIn("nvml_preflight_timeout", complete["flags"])

    def test_copy_timeout_keeps_sealed_archive(self):
        self._script("rsync", "#!" + sys.executable + "\nimport time\ntime.sleep(30)\n")
        # Explicit sleeping stub exceeds 50 ms; this tests command wiring, no
        # network transfer or measured-throughput comparison is involved.
        result = run_session(self._options("copy-timeout", destination="fixture-destination",
                                           copy_timeout_s=0.05))
        self.assertEqual(result["transfer_flags"], ("copy_timeout",))
        self.assertTrue(Path(result["archive"]).is_file())
        self.assertEqual(verify_manifest(self.base / "copy-timeout"), ())


    def test_stop_group_waits_for_sigkill_and_complete_group_disappearance(self):
        from joulewise.align.gpukit.session import _stop_group, _enable_child_reaping
        import signal
        _enable_child_reaping()
        ready = self.base / "term-ignoring-ready"
        process = subprocess.Popen([
            sys.executable, "-c",
            "import signal,time,sys; from pathlib import Path; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            "Path(sys.argv[1]).write_text('ready'); time.sleep(30)", str(ready)],
            start_new_session=True)
        self.addCleanup(lambda: process.poll() is None and _stop_group(process, grace_s=0.05))
        # Existing 30 s fixture setup budget, no timing assertion on scheduler latency.
        import time
        deadline = time.monotonic() + 30
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)  # Existing fixture readiness polling cadence.
        self.assertTrue(ready.exists())
        _stop_group(process, grace_s=0.05)  # Operator-selected cleanup policy for this stub.
        self.assertEqual(process.returncode, -signal.SIGKILL)
        with self.assertRaises(ProcessLookupError):
            os.killpg(process.pid, 0)


class FixArithmeticTests(unittest.TestCase):
    def test_budget_protocol_counts_by_hand(self):
        matrix, flags = load_matrix(CONFIG / "budget.json")
        self.assertEqual(flags, ())
        self.assertEqual(matrix["budget"]["protocol_commit"], "58750718f")
        self.assertEqual(matrix["monitor_model"], "openai/gpt-oss-20b")
        self.assertEqual(matrix["models"][-1]["id"], "Qwen/Qwen3-Next-80B-A3B-Thinking")
        # 200 items * 3 unpaired calibration calls = 600 Episodes.
        # Per item/seed: 3 single-call + 4 two-call forced conditions, each hinted
        # and paired. 14 generation Episodes, 22 model calls at positive caps.
        # Four deletion views add zero generation Episodes, one monitor each.
        # A forced logical generation is two Turns in ONE Episode.
        for episodes, monitors in work_counts(matrix).values():
            self.assertEqual(episodes, 600 + 200 * 3 * 14)
            self.assertEqual(monitors, 200 * 3 * (3 + 4 + 4))
        self.assertEqual(matrix["measured_episode_count"], 4 * 9000)
        self.assertEqual(matrix["monitor_call_count"], 4 * 6600)

    def test_all_numeric_input_leaves_are_sourced_or_null(self):
        from joulewise.align.gpukit.matrix import numeric_provenance
        for path in CONFIG.glob("*.json"):
            self.assertEqual(numeric_provenance(json.loads(path.read_text())), (), path.name)
        # Exact old-head structure: these two values were unsourced at 280866c8d.
        old = {"workload": {"prefill_tokens": 40000, "source": "Operator-supplied"},
               "gpu_classes": {"H100": {"setup_s": 1800, "source": "Operator-supplied"}},
               "model_parameters": {}}
        self.assertEqual(set(numeric_provenance(old)), {
            "matrix_numeric_source_missing:workload.prefill_tokens",
            "matrix_numeric_source_missing:gpu_classes.H100.setup_s"})
        broken, _ = load_matrix(CONFIG / "shade.json")
        broken["workload"]["prefill_tokens"] = 40000
        broken["workload"].pop("derivation")
        self.assertIn("matrix_numeric_source_missing:workload.prefill_tokens", numeric_provenance(broken))

    def test_decode_weights_from_independent_cited_fields(self):
        matrix, _ = load_matrix(CONFIG / "budget.json")
        # Reviewer/card printed non-embedding counts + full output head for dense
        # Qwen; MoE/Phi active totals - input lookup. Config vocab/hidden are
        # integer dimensions. 1e-6 relative is the brief's arithmetic bar.
        expected = {
            "Qwen/Qwen3-4B": 3.6e9 + 151936 * 2560,
            "Qwen/Qwen3-8B": 6.95e9 + 151936 * 4096,
            "Qwen/Qwen3-14B": 13.2e9 + 151936 * 5120,
            "Qwen/Qwen3-30B-A3B": 3.3e9 - 151936 * 2048,
            "microsoft/Phi-3.5-mini-instruct": 3.8e9 - 32064 * 3072,
            "Qwen/Qwen3-Next-80B-A3B-Thinking": 3e9 - 151936 * 2048,
        }
        for model, weights in expected.items():
            parameters = matrix["model_parameters"][model]
            self.assertTrue(math.isclose(parameters["decode_weight_parameters"], weights, rel_tol=1e-6))
            _, decode = ceilings(matrix, "H100-SXM-80GB", model)
            self.assertTrue(math.isclose(decode, 3.35e12 / (2 * weights), rel_tol=1e-6))
        # Match the reviewer's last printed 0.01B digit, without inventing a bar.
        for model, printed in zip(list(expected)[:5], ("3.99", "7.57", "13.98", "2.99", "3.70")):
            self.assertEqual(f"{expected[model] / 1e9:.2f}", printed)

    def test_monitor_tokens_never_change_agent_cost_and_one_load_per_model(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        matrix = planning_fixture(matrix)
        for rate in matrix["gpu_classes"]["H100-SXM-80GB"]["throughput"].values():
            rate.update(efficiency=0.5, efficiency_source={
                "url": "https://github.com/mpmdw/JouleWise", "accessed": "2026-10-22",
                "quote": "Synthetic test efficiency 1/2, not a device performance claim."})
        before = estimate(matrix, "H100-SXM-80GB", usd_per_gpu_hour=2,
                          monitor_placement="gpu", monitor_usd_per_gpu_hour=3)
        matrix["workload"].update(monitor_prefill_tokens=10**12, monitor_decode_tokens=10**12)
        after = estimate(matrix, "H100-SXM-80GB", usd_per_gpu_hour=2,
                         monitor_placement="gpu", monitor_usd_per_gpu_hour=3)
        # Identical code on identical agent inputs is a bit-identity property.
        self.assertEqual(before.wall_seconds, after.wall_seconds)
        self.assertEqual(before.gpu_hours, after.gpu_hours)
        self.assertEqual(before.model_load_count, 2)
        # Monitor GPU is held for full session wall time, no token charge to agent.
        self.assertTrue(math.isclose(before.monitor_gpu_hours, before.wall_seconds / 3600, rel_tol=1e-6))
        self.assertTrue(math.isclose(before.monitor_total_usd, before.monitor_gpu_hours * 3, rel_tol=1e-6))

    def test_memory_layout_alternatives(self):
        from joulewise.align.gpukit.cost import memory_fit
        matrix, _ = load_matrix(CONFIG / "budget.json")
        model = matrix["models"][-1]
        for option, weights, capacity in ((model["layout_options"][0], 160e9, 320e9),
                                         (model["layout_options"][1], 80e9, 160e9)):
            spec = {**model, **option}
            fit = memory_fit(matrix, "H100-SXM-80GB", spec)
            # Exact integers: 80B weights * BF16/FP8 bytes, 80GB/device * TP.
            self.assertEqual(fit["weight_bytes"], weights)
            self.assertEqual(fit["capacity_bytes"], capacity)
            self.assertIsNone(fit["fits"])
            spec["kv_headroom_bytes"] = capacity - weights
            self.assertTrue(memory_fit(matrix, "H100-SXM-80GB", spec)["fits"])
            spec["kv_headroom_bytes"] += 1  # One byte over capacity must fail, no float tolerance.
            self.assertFalse(memory_fit(matrix, "H100-SXM-80GB", spec)["fits"])

    def test_placeholder_configs_and_per_session_ids(self):
        matrix, _ = load_matrix(CONFIG / "shade.json")
        settings = dict(task_factory="mock.inbox", endpoint_factory="mock.scripted",
                        sampler_factory="mock.power", monitor_factory="mock.monitor",
                        token_counter_factory="mock.tokens", order_seed=7,
                        max_turns=40, max_tokens=600, temperature=0.0,
                        clock={"factory": "mock.clock"}, clock_domain="mock.monotonic")
        kwargs = dict(model=matrix["models"][0]["id"], endpoint="http://127.0.0.1:8000",
                      output_dir=Path("/tmp/unused"), settings=settings)
        first, flags = runner_matrix(matrix, **kwargs)
        second, _ = runner_matrix(matrix, **kwargs)
        self.assertEqual(flags, ("runner_adapter_provisional",))
        self.assertNotEqual(first["matrix_id"], second["matrix_id"])
        # Runner protocol hashes exactly these coordinates and matrix ID. Compare
        # integer identities/hashes exactly, not with a numerical tolerance.
        from joulewise.align.records import to_json
        def ids(spec):
            return {hashlib.sha256(to_json([task["task_pair"], condition,
                                           "same-endpoint", seed, spec["matrix_id"]]).encode()).hexdigest()
                    for task in spec["task_pairs"] for condition in spec["conditions"]
                    for seed in spec["seeds"]}
        self.assertTrue(ids(first).isdisjoint(ids(second)))
        self.assertEqual(first["endpoints"][0]["config"], {})
        self.assertEqual(first["samplers"][0]["config"], {})
        self.assertEqual(first["task_pairs"][0]["config"], {})
        self.assertEqual(first["clock"], settings["clock"])
        self.assertEqual(first["clock_domain"], "mock.monotonic")
        from joulewise.align.records import Episode, PowerTrace, Turn, write_episodes
        from joulewise.align.gpukit.session import _validate_output
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mock.jsonl"
            write_episodes(path, [Episode(
                "mock-id", "task", "benign", "synthetic-8B", "mock/synthetic-8B/v1/test",
                0, "mock.monotonic", 0, 1_000_000_000,
                (Turn(0, 0, 1_000_000_000, 0, 800, 80),),
                power_traces=(PowerTrace("mock", "gpu0", "mock.monotonic",
                                        (0, 1_000_000_000), (55.0, 55.0),
                                        "W", 100_000_000),))])
            output_flags = _validate_output(path, expected_count=1, router=False,
                                            model=matrix["models"][0]["id"],
                                            expected_coordinates=[("task", "benign", 0)])
            # R5 also catches this declared mock's 1 s median cycle against
            # 2*100 ms expected: synthetic identity tolerance does not waive it.
            self.assertEqual(output_flags, ("episode_power_coverage_cycle:gpu0",
                                            "episode_power_coverage_incomplete",
                                            "episode_power_mock"))
        settings["endpoint_config"] = {"model": "{agent_model}", "base_url": "{agent_base_url}"}
        requested, _ = runner_matrix(matrix, **kwargs)
        self.assertEqual(requested["endpoints"][0]["config"],
                         {"model": matrix["models"][0]["id"], "base_url": "http://127.0.0.1:8000/v1"})

    def test_condition_and_visibility_typos_are_flags(self):
        for field, typo, reason in (
                ("conditions", "attack", "matrix_conditions_invalid"),
                ("monitor_visibilities", "everything", "matrix_monitor_visibilities_invalid")):
            matrix, _ = load_matrix(CONFIG / "shade.json")
            matrix[field].append(typo)
            self.assertIn(reason, validate(matrix))

    def test_decimal_display_has_two_digits_and_downward_bounds(self):
        from decimal import Decimal
        from joulewise.align.gpukit.throughput import display_number
        for value, printed in ((0.479, 0.47), (1.999, 1.9), (0.579, 0.57)):
            number = display_number(value, lower_bound=True)
            self.assertEqual(number, printed)  # Exact displayed decimal cell.
            self.assertLessEqual(Decimal(str(number)), Decimal(str(value)))
            self.assertLessEqual(len(Decimal(str(number)).normalize().as_tuple().digits), 2)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "optional jsonschema is not installed")
    def test_schema_typos_and_cited_price_rows(self):
        import jsonschema
        schema = json.loads((ROOT / "joulewise/align/gpukit/matrix.schema.json").read_text())
        validator = jsonschema.Draft202012Validator(schema)
        base, _ = load_matrix(CONFIG / "shade.json")
        for field, value in (("conditions", "attack"), ("monitor_visibilities", "everything")):
            matrix = copy.deepcopy(base)
            matrix[field].append(value)
            self.assertGreaterEqual(len(list(validator.iter_errors(matrix))), 1)
        row = {"usd_per_gpu_hour": 2, "url": "https://example.org/test-only-price",
               "date_seen": "2026-10-22", "gpu_class": "H100-SXM-80GB"}
        matrix = copy.deepcopy(base)
        matrix["example_prices"] = [row]
        self.assertEqual(list(validator.iter_errors(matrix)), [])
        for field in row:
            broken = copy.deepcopy(matrix)
            broken["example_prices"][0].pop(field)
            self.assertGreaterEqual(len(list(validator.iter_errors(broken))), 1)
