"""R5 coverage worlds pass through the same output validator as session receipts."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from joulewise.align.gpukit.session import _incomplete_flag, _validate_output
from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn, write_episodes


class CoverageTests(unittest.TestCase):
    # 10 ms polling and 50 us/channel half-widths model NVML's serial reads.
    interval = 10_000_000
    start = 1_000_000_000
    duration = 2_000_000_000

    def trace(self, channel="energy", gaps=None, *, average=0, period=0, supported=True):
        gaps = gaps or [10_000_000] * 198
        times = [self.start + 5_000_000]
        for gap in gaps:
            times.append(times[-1] + gap)
        energy = channel == "energy"
        notes = dict(supported=supported, timing_half_width_ns=[50_000] * len(times),
                     sensor_facts={"period_ns": period} if period else {},
                     field_timestamps_us=[t // 1000 for t in times] if period else [],
                     output_averaging_window_ns=average)
        return PowerTrace("nvml_energy" if energy else "nvml_power", "gpu0:" + channel,
                          "host.monotonic", tuple(times) if supported else (),
                          tuple(50.0 for _ in times) if supported else (),
                          "J_cumulative" if energy else "W", self.interval,
                          notes=json.dumps(notes))

    def episode(self, traces, *, duration=None):
        end = self.start + (self.duration if duration is None else duration)
        # Twelve model turns and eleven tool calls, with production-sized usage.
        step = (end - self.start) // 12
        turns = tuple(Turn(i, self.start + i * step, self.start + (i + 1) * step,
                           i * 1200, 1200, 160, tool_calls=(
                               ToolCall("read", self.start + i * step,
                                        self.start + i * step + step // 4, 64, 1500),))
                      for i in range(12))
        return Episode("e", "shade/task", "benign", "Qwen/Qwen3-8B", "vllm:test", 0,
                       "host.monotonic", self.start, end, turns,
                       power_traces=tuple(traces), flags=("power.empty",))

    def validate(self, episode):
        metrics = {}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "episodes.jsonl"
            write_episodes(path, [episode])
            flags = _validate_output(path, expected_count=1, router=False,
                                     model=episode.agent_model, measured_devices=(0,),
                                     expected_coordinates=[("shade/task", "benign", 0)],
                                     power_metrics=metrics)
        return not any(_incomplete_flag(f) for f in flags), flags, metrics

    def test_clean_jitter_dedup_and_unsupported(self):
        # Median 10 ms, maximum 18 ms = 1.8 cycles; edges 5 and 15 ms < B.
        gaps = [10_000_000] * 198
        gaps[20:22] = [18_000_000, 2_000_000]
        traces = [self.trace(gaps=gaps),
                  self.trace("power_average", [100_000_000] * 19, average=1_000_000_000,
                             period=100_000_000),
                  self.trace("power_instant", supported=False)]
        complete, flags, metrics = self.validate(self.episode(traces))
        self.assertTrue(complete, flags)
        self.assertIn("episode_power_channel_unsupported:gpu0:power_instant", flags)
        self.assertEqual(metrics["episodes_checked"], 1)
        self.assertEqual(metrics["episodes_incomplete_on_power"], 0)
        self.assertEqual(metrics["episodes_with_lost_reads"], 0)

    def test_covered_lost_read_and_power_hole(self):
        # One 25 ms gap = 2.5 nominal cycles, above B~20 ms. Other 10 ms
        # gaps fix C; the final edge is 20 ms. The 1 s average covers 25 ms.
        gaps = [10_000_000] * 196
        gaps[20] = 25_000_000
        for channel, average, complete in (("energy", 0, True),
                                           ("power_usage", 1_000_000_000, True),
                                           ("power_instant", 0, False)):
            ok, flags, metrics = self.validate(self.episode([
                self.trace(channel, gaps, average=average)]))
            self.assertEqual(ok, complete, flags)
            if complete:
                self.assertIn("episode_power_reads_lost:gpu0:" + channel, flags)
                self.assertEqual(metrics["episodes_with_lost_reads"], 1)
            else:
                self.assertIn("episode_power_coverage_hole:gpu0:" + channel, flags)

    def test_tail_and_offset_uncertainty(self):
        # Last reading at 1.975 s leaves 25 ms, above two 10.1 ms cycles.
        trace = self.trace(gaps=[10_000_000] * 197)
        episode = self.episode([trace])
        ok, flags, _ = self.validate(episode)
        self.assertFalse(ok)
        self.assertIn("episode_power_coverage_edge:gpu0:energy", flags)
        # A 5 ms mapping half-width covers the excess at the edge. Offset is
        # exact 1 s and is applied before comparing to the episode clock.
        shifted = replace(trace, clock_domain="sensor", t_ns=tuple(t - 1_000_000_000 for t in trace.t_ns))
        mapped = replace(episode, power_traces=(shifted,),
                         clock_mappings=(ClockMapping("sensor", "host.monotonic",
                                                      1_000_000_000, 5_000_000, "fixture"),))
        self.assertTrue(self.validate(mapped)[0])

    def test_two_40_second_probes(self):
        for name, gaps, check in (
                ("two", [40_000_000_000], "cycle"),
                ("stall", [5_000_000, 39_990_000_000, 5_000_000], "hole")):
            trace = self.trace("power_instant", gaps)
            trace = replace(trace, t_ns=tuple(t - 5_000_000 for t in trace.t_ns))
            ok, flags, metrics = self.validate(self.episode([trace], duration=40_000_000_000))
            self.assertFalse(ok, name)
            self.assertIn("episode_power_coverage_" + check + ":gpu0:power_instant", flags)
            self.assertEqual(metrics["episodes_incomplete_on_power"], 1)
            self.assertEqual(metrics["episodes_with_lost_reads"], 0)

    def test_period_from_driver_stamps_and_missing_supported_device(self):
        trace = self.trace("power_average", [100_000_000] * 19, period=100_000_000)
        notes = json.loads(trace.notes)
        notes["sensor_facts"] = {}
        trace = replace(trace, notes=json.dumps(notes))
        ok, flags, _ = self.validate(self.episode([trace]))
        self.assertTrue(ok, flags)
        self.assertIn("episode_power_sensor_period_from_driver_timestamps:gpu0:power_average", flags)
        ok, flags, _ = self.validate(self.episode([self.trace(supported=False)]))
        self.assertFalse(ok)
        self.assertIn("episode_measured_device_power_missing:0", flags)
        empty = replace(self.trace(), t_ns=(), values=())
        self.assertIn("episode_power_missing", self.validate(self.episode([empty]))[1])


class ServeTests(unittest.TestCase):
    def test_argv_matches_every_model_and_monitor_in_each_config(self):
        from joulewise.align.gpukit.session import _serve_argv, SessionOptions
        root = Path(__file__).resolve().parents[2]
        options = SessionOptions(Path("unused"), Path("unused"), (), 20, 0.2, 120, 500, "none")
        for path in sorted((root / "configs/align").glob("*.json")):
            matrix = json.loads(path.read_text())
            specs = [*matrix["models"], matrix["monitor_serving"]]
            specs.extend({**m, **option} for m in matrix["models"]
                         for option in m.get("layout_options", ()))
            for spec in specs:
                argv = _serve_argv(options, spec, 18761)
                for field, flag in (("reasoning_parser", "--reasoning-parser"),
                                    ("tool_call_parser", "--tool-call-parser")):
                    if spec[field] is None:
                        self.assertNotIn(flag, argv)
                    else:
                        self.assertEqual(argv.count(flag), 1)
                        self.assertEqual(argv[argv.index(flag) + 1], spec[field])
                self.assertEqual("--enable-auto-tool-choice" in argv,
                                 spec["enable_auto_tool_choice"])
                self.assertNotIn("--enable-reasoning", argv)
                if spec["id"] == "Qwen/Qwen3-Next-80B-A3B-Thinking":
                    self.assertEqual(spec["reasoning_parser"], "deepseek_r1")
            null = dict(matrix["models"][0], reasoning_parser=None)
            self.assertNotIn("--reasoning-parser", _serve_argv(options, null, 18761))

    def test_missing_parser_is_flagged_and_required_by_schema(self):
        from joulewise.align.gpukit.matrix import validate
        root = Path(__file__).resolve().parents[2]
        matrix = json.loads((root / "configs/align/shade.json").read_text())
        del matrix["models"][0]["reasoning_parser"]
        self.assertIn("matrix_reasoning_parser_invalid", validate(matrix))
        schema = json.loads((root / "joulewise/align/gpukit/matrix.schema.json").read_text())
        self.assertIn("reasoning_parser", schema["properties"]["models"]["items"]["required"])

    @unittest.skipUnless(__import__("importlib.util", fromlist=["find_spec"]).find_spec("jsonschema"),
                         "optional jsonschema is not installed")
    def test_jsonschema_rejects_missing_parser(self):
        import jsonschema
        root = Path(__file__).resolve().parents[2]
        matrix = json.loads((root / "configs/align/shade.json").read_text())
        schema = json.loads((root / "joulewise/align/gpukit/matrix.schema.json").read_text())
        del matrix["models"][0]["reasoning_parser"]
        self.assertGreaterEqual(len(list(jsonschema.Draft202012Validator(schema).iter_errors(matrix))), 1)


class ExitTests(unittest.TestCase):
    def test_invalid_matrix_fails_before_any_hardware_or_child_command(self):
        import contextlib
        import io
        from unittest.mock import patch
        from joulewise.align.gpukit import session
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            invalid = base / "invalid.json"
            invalid.write_text("[]")
            unreadable = base / "directory.json"
            unreadable.mkdir()
            malformed = base / "malformed.json"
            malformed.write_text("{")
            for i, matrix in enumerate((base / "missing.json", invalid, unreadable, malformed)):
                with patch.object(session, "whole_gpu") as inventory, \
                     patch.object(session, "snapshot") as snapshot, \
                     patch.object(session, "_command") as command, \
                     patch.object(session.subprocess, "Popen") as child:
                    stdout = io.StringIO()
                    output = base / ("run-" + str(i))
                    with contextlib.redirect_stdout(stdout):
                        code = session.main([
                            str(matrix), "--output", str(output),
                            "--ready-timeout-s", "20", "--command-timeout-s", "120",
                            "--runner-timeout-s", "500", "--poll-s", "0.2",
                            "--monitor-placement", "none"])
                    receipt = json.loads(stdout.getvalue())
                    self.assertEqual(code, 3)
                    self.assertEqual(receipt["status"], "failed")
                    self.assertFalse(receipt["data_complete"])
                    self.assertTrue(any(f.startswith("matrix_") for f in receipt["flags"]))
                    inventory.assert_not_called()
                    snapshot.assert_not_called()
                    command.assert_not_called()
                    child.assert_not_called()
                    self.assertEqual(session.verify_manifest(output), ())

    def test_unexpected_session_exception_exits_three(self):
        import contextlib
        import io
        from unittest.mock import patch
        from joulewise.align.gpukit import session
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(session, "_command", side_effect=RuntimeError("fixture")):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = session.main([
                        str(root / "configs/align/shade.json"), "--output", directory + "/run",
                        "--runner-command", '["true"]',
                        "--ready-timeout-s", "20", "--command-timeout-s", "120",
                        "--runner-timeout-s", "500", "--poll-s", "0.2",
                        "--monitor-placement", "none"])
            receipt = json.loads(stdout.getvalue())
            self.assertEqual(code, 3)
            self.assertEqual(receipt["status"], "failed")
            self.assertIn("session_failed:RuntimeError", receipt["flags"])
            self.assertFalse(receipt["data_complete"])


class IdentityTests(unittest.TestCase):
    def test_shared_model_identity_and_calibration_path(self):
        from joulewise.align.gpukit.identity import model_identity_matches
        from joulewise.align.gpukit.cost import estimate
        root = Path(__file__).resolve().parents[2]
        matrix = json.loads((root / "configs/align/shade.json").read_text())
        world = CoverageTests()
        episode = world.episode([world.trace()])
        with tempfile.TemporaryDirectory() as directory:
            for i, spec in enumerate(matrix["models"]):
                model = spec["id"]
                identity = "vllm:" + model + "@http://127.0.0.1:18761/v1"
                self.assertTrue(model_identity_matches(model, model))
                self.assertTrue(model_identity_matches(identity, model))
                self.assertFalse(model_identity_matches("vllm:another/model@http://local/v1", model))
                self.assertFalse(model_identity_matches(model + "-FP8", model))
                row = replace(episode, agent_model=identity, endpoint=identity)
                model_dir = Path(directory) / ("model-" + str(i))
                model_dir.mkdir()
                path = model_dir / "episodes.jsonl"
                write_episodes(path, [row])
                flags = _validate_output(path, expected_count=1, router=False, model=model)
                self.assertNotIn("runner_episode_model_mismatch", flags)
            result = estimate(matrix, "H100-SXM-80GB", calibration=Path(directory))
            self.assertFalse(any(f.startswith("calibration_model_missing:") for f in result.flags))
            self.assertEqual(set(result.calibration_basis), {m["id"] for m in matrix["models"]})
            for basis in result.calibration_basis.values():
                self.assertEqual(basis["observed_episodes"], 1)
                # Same episode brackets; default 1e-6 relative arithmetic bar.
                self.assertTrue(math.isclose(basis["mean_episode_seconds"], 2.0, rel_tol=1e-6))
