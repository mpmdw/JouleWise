"""All HTTP, devices, /proc and clocks are synthetic; no sockets or weights."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.endpoints import EndpointRequestFailed
from joulewise.align.interfaces import ChatEndpoint, ChatMessage
from joulewise.align.linux.backend import LlamaCppBackend, LlamaCppEndpoint
from joulewise.align.linux.quiet import (
    ContentionPolicy, CpuSnapshot, LinuxQuietGuard, ProcessCpu, QuietIndeterminate,
    cpu_interval, proc_snapshot,
)
from joulewise.align.linux.samplers import (
    CsvReplayWallMeter, HttpJsonWallMeter, RaplSampler, WallMeterAdapter, WallMeterSampler,
)
from joulewise.align.linux.seeds import episode_seed, turn_seed
from joulewise.align.linux.session import run_member, validate_config, write_attempt
from joulewise.align.records import Episode, PowerTrace, from_json, to_json
from joulewise.align.runner import run_episode
from joulewise.align.shade import ShadeTask
from tests.align.test_shade import fixture_source
from tests.align.test_power_nvml import FakeNvmlLibrary, collect


class FakeServer:
    """HTTP-JSON/SSE shaped transport, deliberately never binds a socket."""

    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []

    def __call__(self, url, body, timeout):
        self.requests.append((url, body, timeout))
        reply = next(self.replies)
        if isinstance(reply, Exception):
            raise reply
        return io.BytesIO(reply)


def sse(content="done", *, calls=(), reasoning="private plan", usage=True, done=True,
        cached=3, prompt=20, completion=7, hidden=2):
    delta = {"content": content, "reasoning_content": reasoning}
    if calls:
        delta["tool_calls"] = [{"index": i, "id": str(i), "type": "function",
                                "function": {"name": name, "arguments": args}}
                               for i, (name, args) in enumerate(calls)]
    chunks = [{"choices": [{"index": 0, "delta": delta,
                            "finish_reason": "tool_calls" if calls else "stop"}]}]
    if usage:
        chunks.append({"choices": [], "usage": {
            "prompt_tokens": prompt, "completion_tokens": completion,
            "prompt_tokens_details": {"cached_tokens": cached},
            "completion_tokens_details": {"reasoning_tokens": hidden}}})
    raw = "".join("data: " + json.dumps(c) + "\n\n" for c in chunks)
    return (raw + ("data: [DONE]\n\n" if done else "")).encode()


class TickClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        self.now += 1_000_000
        return self.now


class FakeGuard:
    def __init__(self, decision="keep"):
        self.decision = decision
        self.stopped = False

    def start(self):
        pass

    def stop(self, attempt=0):
        self.stopped = True
        return {"decision": self.decision, "intervals": [], "errors": [], "attempt": attempt}


class FakeSampler:
    clock_mappings = ()

    def __init__(self, source="wall_meter", empty=False):
        self.source, self.empty = source, empty

    def start(self):
        import time
        self.start_ns = time.monotonic_ns() - 100

    def stop(self):
        import time
        return (PowerTrace(self.source, "test", "test", () if self.empty else
                           (self.start_ns, time.monotonic_ns() + 100),
                           () if self.empty else (100.0, 100.0), "W", 1),)


class EndpointTests(unittest.TestCase):
    def test_same_shade_loop_seeds_counts_reasoning_and_tool_history(self):
        with fixture_source() as source:
            server = FakeServer([sse("", calls=(("read_ledger", "{}"),)), sse("finished")])
            endpoint = LlamaCppEndpoint("http://127.0.0.1:8080", "tiny-synthetic",
                seed_model_id="test-model", task_pair="shade/ledger_review", post=server)
            self.assertIsInstance(endpoint, ChatEndpoint)
            task = ShadeTask("ledger_review", upstream=source)
            episode, transcript, quiet = run_member(task, "sabotage", endpoint,
                [FakeSampler()], FakeGuard(), seed=14, max_turns=3, max_tokens=32,
                temperature=0.6, clock_domain="test")
            self.assertEqual([t.decode_tokens for t in episode.turns], [7, 7])
            self.assertEqual([t.hidden_tokens for t in episode.turns], [2, 2])
            self.assertEqual([t.context_tokens for t in episode.turns], [3, 3])
            self.assertEqual([t.prefill_tokens for t in episode.turns], [17, 17])
            self.assertEqual(task.seed, 14)
            self.assertTrue(any("private plan" in m.content for m in transcript))
            self.assertEqual(episode.turns[0].tool_calls[0].name, "read_ledger")
            self.assertFalse(any(f.startswith("wall_meter.") for f in episode.flags))
            logical = episode_seed("test-model", "thinking_on", task.task_pair, 14)
            for index, (_, body, _) in enumerate(server.requests):
                self.assertEqual(body["seed"], turn_seed(logical, index) & 0xFFFFFFFF)
                self.assertFalse(body["cache_prompt"])
                self.assertTrue(body["stream_options"]["include_usage"])
            next_history = server.requests[1][1]["messages"]
            assistant = next(m for m in next_history if m["role"] == "assistant")
            self.assertEqual(assistant["tool_calls"][0]["function"]["name"], "read_ledger")
            self.assertNotIn("private plan", json.dumps([m for m in next_history if m["role"] == "assistant"]))
            raw = episode.hardware["runner"]["raw_usage"]["0"]["joulewise"]["seed"]
            self.assertEqual(raw["episode_seed_uint64"], logical)
            evidence = episode.hardware["runner"]["raw_usage"]["0"]["joulewise"]
            self.assertEqual(evidence["completion"]["reasoning_text"], "private plan")
            self.assertEqual(evidence["request"]["body"], server.requests[0][1])
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "attempt0"
                write_attempt(path, episode, transcript, {"status": "DRAFT"}, quiet)
                restored = from_json(Episode, (path / "episode.json").read_text())
                self.assertEqual(restored, episode)
                manifest = json.loads((path / "manifest.json").read_text())
                for name, digest in manifest["sha256"].items():
                    self.assertEqual(hashlib.sha256((path / name).read_bytes()).hexdigest(), digest)
                self.assertIn("private plan", (path / "transcript.jsonl").read_text())
                with self.assertRaises(FileExistsError):
                    write_attempt(path, episode, transcript, {}, quiet)

    def test_new_session_resets_turn_seed_and_endpoint_history(self):
        server = FakeServer([sse(), sse()])
        backend = LlamaCppBackend({"base_url": "http://fake", "model": "tiny",
                                  "seed_model_id": "same"}, "/synthetic-unused", post=server)
        for _ in range(2):
            endpoint = backend.new_session("shade/test")
            endpoint.chat([ChatMessage("user", "x")], max_tokens=20, temperature=0.6, seed=1)
        self.assertEqual(server.requests[0][1]["seed"], server.requests[1][1]["seed"])

    def test_seed_law_matches_existing_apple_golden(self):
        # V11 in the council design: spam/benign seed-index 14.
        self.assertEqual(episode_seed("qwen3-30b-a3b", "thinking_on", "shade/spam_filter_update", 14),
                         8158640411307706161)

    def test_inline_reasoning_missing_count_is_not_estimated(self):
        endpoint = LlamaCppEndpoint("http://fake/v1", "tiny", inline_thinking=True,
            post=FakeServer([sse("<think>secret</think>answer", reasoning="", hidden=0)]))
        result = endpoint.chat([], max_tokens=20, temperature=0.6, seed=1)
        self.assertEqual((result.reasoning_text, result.content, result.reasoning_tokens),
                         ("secret", "answer", 0))
        self.assertIn("reasoning_tokens_unreported", result.raw_usage["joulewise"]["flags"])

    def test_cut_stream_missing_usage_and_timeout_keep_failed_evidence_without_retry(self):
        for reply in (sse(done=False), sse(usage=False), TimeoutError("synthetic timeout")):
            with self.subTest(reply=type(reply).__name__):
                server = FakeServer([reply])
                endpoint = LlamaCppEndpoint("http://fake", "tiny", seed_model_id="m",
                    task_pair="shade/test", post=server)
                with self.assertRaises(EndpointRequestFailed) as caught:
                    endpoint.chat([], max_tokens=20, temperature=0.6, seed=2)
                self.assertEqual(len(server.requests), 1)
                self.assertIn("seed", caught.exception.partial_result.raw_usage["joulewise"])

    def test_llamacpp_timings_usage_and_reasoning_alias(self):
        chunk = {"choices": [{"delta": {"content": "ok", "reasoning": "plan"},
                              "finish_reason": "stop"}],
                 "timings": {"prompt_n": 10, "cache_n": 2, "predicted_n": 4}}
        reply = ("data: " + json.dumps(chunk) + "\n\ndata: [DONE]\n\n").encode()
        endpoint = LlamaCppEndpoint("http://fake", "tiny", post=FakeServer([reply]))
        result = endpoint.chat([], max_tokens=20, temperature=0, seed=1)
        self.assertEqual((result.prompt_tokens, result.cached_prompt_tokens, result.completion_tokens), (12, 2, 4))
        self.assertEqual(result.reasoning_text, "plan")
        self.assertIn("reasoning_tokens_unreported", result.raw_usage["joulewise"]["flags"])


class SamplerTests(unittest.TestCase):
    def test_rtx3050_nvml_power_energy_and_unsupported_energy_are_independent(self):
        library = FakeNvmlLibrary(architecture=7, name="NVIDIA GeForce RTX 3050")
        traces = collect(library)
        self.assertEqual({t.source for t in traces}, {"nvml_power", "nvml_energy"})
        for trace in traces:
            self.assertIsNone(trace.averaging_window_ns)  # no A100 facts borrowed
            self.assertIsNone(trace.duty_fraction)
        library.energy_supported = False
        traces = collect(library)
        self.assertTrue(next(t for t in traces if t.channel.endswith(":power_usage")).values)
        self.assertFalse(next(t for t in traces if t.unit == "J_cumulative").values)

    def test_http_meter_field_mapping_and_stale_detection(self):
        replies = iter([{"sensor": {"watts": 123}, "time": 1}] * 2)
        meter = HttpJsonWallMeter("http://fake/power", power_field="sensor.watts",
            timestamp_field="time", fetch=lambda *args: next(replies))
        self.assertIsInstance(meter, WallMeterAdapter)
        self.assertEqual(meter.read()[0], 123)
        with self.assertRaisesRegex(ValueError, "stale"):
            meter.read()

    def test_missing_and_bad_meter_streams_are_flagged_not_zero_filled(self):
        for adapter in (None, HttpJsonWallMeter("http://fake", fetch=lambda *a: {"power_w": float("nan")})):
            sampler = WallMeterSampler(adapter, clock_ns=TickClock(), interval_s=100)
            sampler.start()
            trace, = sampler.stop()
            self.assertEqual(trace.values, ())
            self.assertTrue(json.loads(trace.notes)["flags"])
            self.assertIs(sampler.stop()[0], trace)

    def test_successful_meter_brackets_and_raw_readings(self):
        meter = HttpJsonWallMeter("http://fake", fetch=lambda *a: {"power_w": 100})
        sampler = WallMeterSampler(meter, clock_ns=TickClock(), interval_s=100)
        sampler.start()
        trace, = sampler.stop()
        self.assertEqual(trace.values, (100.0, 100.0))
        self.assertEqual(json.loads(trace.notes)["raw"][0]["reading"], {"power_w": 100})
        self.assertEqual(trace, from_json(PowerTrace, to_json(trace)))

    def test_csv_replay_interpolation_exhaustion_and_synthetic_label(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "meter.csv"
            path.write_text("elapsed_s,power_w\n0,100\n2,200\n")
            clock = TickClock()
            meter = CsvReplayWallMeter(path, clock_ns=clock)
            clock.now = 0
            self.assertEqual(meter.read()[0], 100)
            clock.now = 1_000_000_000
            self.assertEqual(meter.read()[0], 150)
            clock.now = 3_000_000_000
            with self.assertRaises(EOFError):
                meter.read()
            self.assertIn("SYNTHETIC", meter.identity)
            path.write_text("elapsed_s,power_w\n0,100\n0,200\n")
            with self.assertRaises(ValueError):
                CsvReplayWallMeter(path)

    def test_rapl_package_only_raw_units_and_decrease(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "intel-rapl:0"
            package.mkdir()
            (package / "name").write_text("package-0\n")
            (package / "energy_uj").write_text("9000000\n")
            (package / "max_energy_range_uj").write_text("10000000\n")
            child = package / "intel-rapl:0:0"
            child.mkdir()
            (child / "name").write_text("core\n")
            sampler = RaplSampler(directory, clock_ns=TickClock(), interval_s=100)
            sampler.start()
            (package / "energy_uj").write_text("1000000\n")
            trace, = sampler.stop()
            self.assertEqual(trace.values, (9.0, 1.0))
            self.assertEqual(trace.source, "rapl_energy")
            self.assertEqual(trace.unit, "J_cumulative")
            self.assertEqual(from_json(PowerTrace, to_json(trace)), trace)
            notes = json.loads(trace.notes)
            self.assertTrue(any("wrap_or_reset" in f for f in notes["flags"]))
            self.assertEqual(notes["raw"][0]["reading"][0]["energy_uj"], 9000000)

    def test_rapl_unavailable_and_permission_denied_preserve_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            sampler = RaplSampler(directory, clock_ns=TickClock(), interval_s=100)
            sampler.start()
            trace, = sampler.stop()
            self.assertEqual(trace.values, ())
            self.assertTrue(json.loads(trace.notes)["flags"])
        with patch.object(Path, "iterdir", side_effect=PermissionError("fake denied")):
            with self.assertRaises(QuietIndeterminate):
                proc_snapshot("/synthetic-proc")

    def test_rapl_counter_attribution_has_unknown_age_and_no_negative_energy(self):
        from joulewise.align.attribution import trace_energy
        trace = PowerTrace("rapl_energy", "package-0", "test", (0, 1_000_000_000),
                           (3.0, 5.0), "J_cumulative", 1_000_000_000, resolution=1e-6)
        estimate = trace_energy(trace, 0, 1_000_000_000)
        self.assertEqual(estimate.joules, 2.0)
        self.assertIn("timing.sensor_age_unknown", estimate.flags)
        self.assertEqual(estimate.half_width_j, float("inf"))


def snapshot(seconds, processes):
    return CpuSnapshot(round(seconds * 1e9), tuple(ProcessCpu(*p) for p in processes))


class QuietTests(unittest.TestCase):
    def interval(self, start, end, *, heavy=0.5, second=0.0):
        return cpu_interval(snapshot(start, [(2, 1, 1, 0, "outside"), (3, 1, 1, 0, "other")]),
            snapshot(end, [(2, 1, 1, round(100 * (end-start) * heavy), "outside"),
                           (3, 1, 1, round(100 * (end-start) * second), "other")]), ticks_per_s=100)

    def test_single_process_threshold_once_redo_then_flag(self):
        policy = ContentionPolicy()
        policy.observe(self.interval(0, 30))
        self.assertEqual(policy.decision(0), "keep")
        policy.observe(self.interval(30, 60))
        self.assertEqual(policy.decision(0), "redo")
        self.assertEqual(policy.decision(1), "contended")

    def test_aggregate_only_and_bursts_never_redo(self):
        policy = ContentionPolicy()
        for start in (0, 30, 60):
            policy.observe(self.interval(start, start + 30, heavy=0.3, second=0.3))
        self.assertEqual(policy.decision(0), "keep")
        self.assertTrue(all(r["flagged"] for r in policy.receipts))
        self.assertTrue(all(r["outside_cpu_s_per_s"] >= 0.5 for r in policy.receipts))
        burst = ContentionPolicy()
        for start, end, rate in ((0, 30, 0.5), (30, 60, 0.0), (60, 90, 0.5)):
            burst.observe(self.interval(start, end, heavy=rate))
        self.assertFalse(burst.sustained)

    def test_tree_exclusion_pid_reuse_and_counter_regression(self):
        opening = snapshot(0, [(10, 1, 1, 0, "server"), (11, 10, 1, 0, "worker"), (12, 1, 1, 0, "old")])
        closing = snapshot(30, [(10, 1, 1, 3000, "server"), (11, 10, 1, 3000, "worker"), (12, 1, 2, 9000, "new")])
        row = cpu_interval(opening, closing, ticks_per_s=100, tree_roots=(10,))
        self.assertIsNone(row["largest_outside"])
        self.assertEqual(len(row["unaccounted_started"]), 1)
        with self.assertRaises(QuietIndeterminate):
            cpu_interval(closing, snapshot(60, [(10, 1, 1, 1, "server")]), ticks_per_s=100)

    def test_proc_stat_parses_parenthesized_command_and_ticks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "42"
            path.mkdir()
            fields = ["S"] + ["0"] * 21
            fields[1], fields[11], fields[12], fields[19] = "1", "120", "30", "500"
            (path / "stat").write_text("42 (worker (cpu)) " + " ".join(fields))
            result = proc_snapshot(directory, clock_ns=TickClock())
            self.assertEqual(result.processes[0], ProcessCpu(42, 1, 500, 150, "worker (cpu)"))

    def test_guard_records_raw_snapshots_and_refuses_unknown(self):
        calls = iter(snapshot(t, [(2, 1, 1, t*50, "outside")]) for t in (0, 30, 60))
        guard = LinuxQuietGuard(snapshot=lambda: next(calls), ticks_per_s=100, interval_s=100, window_s=100)
        guard.window_ns = 30_000_000_000
        guard.start()
        guard.check()
        result = guard.stop()
        self.assertEqual(result["decision"], "redo")
        self.assertEqual(len(result["snapshots"]), 3)
        bad = LinuxQuietGuard(snapshot=lambda: (_ for _ in ()).throw(PermissionError("denied")), ticks_per_s=100)
        with self.assertRaises(QuietIndeterminate):
            bad.start()

    def test_required_server_root_cannot_disappear_or_be_reused(self):
        calls = iter((snapshot(0, [(42, 1, 1, 0, "server")]),
                      snapshot(30, [(42, 1, 2, 1, "replacement")]),
                      snapshot(60, [(12, 1, 1, 0, "outside")])))
        guard = LinuxQuietGuard(snapshot=lambda: next(calls), ticks_per_s=100,
                                tree_roots=(42,))
        for _ in range(3):
            guard.check()
        self.assertTrue(any("reused" in e for e in guard.errors))
        self.assertTrue(any("absent" in e for e in guard.errors))


class MemberTests(unittest.TestCase):
    def test_missing_wall_is_a_flag_on_every_member_including_endpoint_failure(self):
        with fixture_source() as source:
            for replies in ([sse()], [TimeoutError("fake timeout")]):
                guard = FakeGuard()
                endpoint = LlamaCppEndpoint("http://fake", "tiny", post=FakeServer(replies))
                episode, _, _ = run_member(ShadeTask("ledger_review", upstream=source), "benign",
                    endpoint, [FakeSampler(empty=True)], guard, seed=1,
                    max_turns=2, max_tokens=20, temperature=0, clock_domain="test")
                self.assertIn("wall_meter.missing_stream", episode.flags)
                self.assertTrue(guard.stopped)

    def test_draft_template_requires_actual_rig_provenance(self):
        path = Path(__file__).resolve().parents[2] / "configs/align/x86/pilot.draft.json"
        config = json.loads(path.read_text())
        with self.assertRaises(ValueError):
            validate_config(config)
        config["server_pid"] = 123
        config["provenance"]["gguf_sha256"] = "a" * 64
        config["provenance"]["llama_cpp_commit"] = "b" * 40
        self.assertIs(validate_config(config), config)

    def test_session_keeps_original_and_one_redo_for_each_paired_member(self):
        from joulewise.align.linux import session
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            config = json.loads((Path(__file__).resolve().parents[2] /
                                 "configs/align/x86/pilot.draft.json").read_text())
            config.update(server_pid=123, seeds=[1])
            config["provenance"].update(gguf_sha256="a"*64, llama_cpp_commit="b"*40)
            fake_task = SimpleNamespace(upstream=SimpleNamespace(prepare=lambda: True),
                                        reset=lambda seed: None, _definition=object())
            backend = SimpleNamespace(task=lambda pair: fake_task, new_session=lambda pair: None)
            calls = []
            def member(task, condition, endpoint, samplers, guard, *, attempt, seed, **kwargs):
                calls.append((condition, seed, attempt))
                decision = "redo" if attempt == 0 else "contended"
                return Episode("id", "shade/fake", condition, "tiny", "fake", seed,
                               "test", 0, 1, ()), [], {"decision": decision}
            with patch("joulewise.align.linux.backend.LlamaCppBackend", return_value=backend), \
                 patch("joulewise.align.linux.quiet.LinuxQuietGuard",
                       return_value=SimpleNamespace(errors=[], check=lambda: None)), \
                 patch.object(session, "run_member", side_effect=member), \
                 patch.object(session.time, "sleep"):
                session.run_session(config, Path(directory)/"session")
            manifests = sorted((Path(directory)/"session").glob("*/manifest.json"))
            self.assertEqual(len(manifests), 8)  # 2 pairs x 2 conditions x 2 attempts
            self.assertEqual([attempt for _, _, attempt in calls], [0, 1]*4)
            self.assertEqual(sum(json.loads(p.read_text())["decision"] == "contended" for p in manifests), 4)


if __name__ == "__main__":
    unittest.main()
