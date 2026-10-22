"""Synthetic D3 matrix and native-shaped MLX boundary regressions."""

from __future__ import annotations

import json
import io
import math
import tempfile
import unittest
from dataclasses import replace
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.budget.apple.__main__ import main
from joulewise.align.budget.apple.endpoint import BudgetMlxEndpoint
from joulewise.align.budget.apple.models import MODEL_SIZES, CachedModel, resolve_model
from joulewise.align.budget.apple.run import (
    DOMAIN, SyntheticAppleTelemetry, _conditions, run_dry, run_live,
)
from joulewise.align.budget.apple.sampling import CHANNELS, BudgetAppleSampler, apple_energy, normalize_result
from joulewise.align.budget.conditions import default_conditions
from joulewise.align.budget.energy import episode_energy
from joulewise.align.budget.run import Settings
from joulewise.align.budget.score import HintMonitor
from joulewise.align.budget.storage import read_episode_views, read_result
from joulewise.align.budget.synthetic import ScriptedModel, ScriptedMonitor, synthetic_items
from joulewise.align.interfaces import ChatMessage
from joulewise.align.records import Episode, to_json
from joulewise.clock import ClockStamp, FakeClock
from joulewise.interfaces import AdapterResult, PowerSample, TelemetryStopResult
from joulewise.schemas import BenchmarkConfig

ROOT = Path(__file__).resolve().parents[2]


def base():
    return BenchmarkConfig.from_mapping(json.loads((ROOT / "configs/examples/mac_mlx_local.json").read_text()))


class Tokenizer:
    eos_token_ids = {0}

    def apply_chat_template(self, messages, **kwargs):
        self.options = kwargs
        self.messages = messages
        return json.dumps(messages, sort_keys=True)

    def encode(self, text, *, add_special_tokens=False):
        return [ord(c) for c in text]

    def decode(self, tokens):
        return "".join(chr(c) for c in tokens)


def native_runtime(clock, text=None, *, fail_template=False):
    runtime = MlxRuntimeAdapter(clock)
    runtime._model = object()
    runtime._tokenizer = Tokenizer()
    runtime.observed_tokens = []
    if fail_template:
        runtime._tokenizer.apply_chat_template = lambda *a, **kw: (_ for _ in ()).throw(ValueError("synthetic"))

    def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler):
        assert tokenizer is runtime._tokenizer  # Real tokenizer type reaches native generation.
        options = tokenizer.options
        raw = text if text is not None else (
            "ANSWER: A" if options.get("continue_final_message") or not options.get("enable_thinking", True)
            else "step by step</think>ANSWER: A")
        clock.sleep(len(prompt) * 0.001)  # D-019 synthetic prompt time.
        for i, c in enumerate(raw[:max_tokens]):
            clock.sleep(0.010)  # D-019 synthetic decode time.
            runtime.observed_tokens.append(c)
            finish = "stop" if i == len(raw) - 1 else "length" if i == max_tokens - 1 else None
            yield SimpleNamespace(token=ord(c), text=c, finish_reason=finish)

    runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
    return runtime


def endpoint(runtime, clock):
    return BudgetMlxEndpoint(MlxEndpoint(runtime, base(), clock, episode_domain=DOMAIN,
                                        prepare_metadata={"mlx_version": "synthetic", "mlx_lm_version": "synthetic"}))


class ModelCacheTests(unittest.TestCase):
    def snapshot(self, root, revision="a" * 40):
        p = root / "models--mlx-community--Qwen3-8B-4bit" / "snapshots" / revision
        p.mkdir(parents=True)
        for name, obj in (("config.json", {"model_type": "qwen3", "quantization": {"bits": 4}}),
                          ("tokenizer.json", {}), ("tokenizer_config.json", {})):
            (p / name).write_text(json.dumps(obj))
        (p / "model.safetensors").write_bytes(b"synthetic-not-a-model")
        return p

    def test_single_snapshot_without_ref_is_pinned_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.snapshot(Path(tmp))
            m = resolve_model("mlx-community/Qwen3-8B-4bit", Path(tmp))
            self.assertEqual((m.revision, m.snapshot, m.size_b), ("a" * 40, str(p), 8.0))

    def test_ambiguous_revisions_need_a_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.snapshot(Path(tmp))
            self.snapshot(Path(tmp), "b" * 40)
            with self.assertRaisesRegex(ValueError, "pin a cached revision"):
                resolve_model("mlx-community/Qwen3-8B-4bit", Path(tmp))
            self.assertEqual(resolve_model("mlx-community/Qwen3-8B-4bit", Path(tmp), "b" * 40).revision, "b" * 40)

    def test_missing_shard_and_wrong_quantization_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.snapshot(Path(tmp))
            (p / "model.safetensors.index.json").write_text(json.dumps({"weight_map": {"w": "missing.safetensors"}}))
            with self.assertRaisesRegex(ValueError, "missing cached weights"):
                resolve_model("mlx-community/Qwen3-8B-4bit", Path(tmp))
            (p / "config.json").write_text(json.dumps({"model_type": "qwen3", "quantization": {"bits": 8}}))
            with self.assertRaisesRegex(ValueError, "4-bit"):
                resolve_model("mlx-community/Qwen3-8B-4bit", Path(tmp))


class EndpointTests(unittest.TestCase):
    def call(self, endpoint, **kwargs):
        return endpoint.chat((ChatMessage("user", "Question"),), max_tokens=100,
                              temperature=0.0, seed=3, **kwargs)

    def test_toggle_and_continuation_reach_template(self):
        clock = FakeClock()
        runtime = native_runtime(clock)
        ep = endpoint(runtime, clock)
        native = runtime._mlx_lm
        off = self.call(ep.configured({"chat_template_kwargs": {"enable_thinking": False}}))
        self.assertFalse(runtime._tokenizer.options["enable_thinking"])
        self.assertEqual((off.content, off.reasoning_tokens), ("ANSWER: A", 0))
        for shape in ("Natural close.", "mid", "paragraph\n", ""):
            result = ep.configured({"chat_template_kwargs": {"enable_thinking": True},
                                    "continue_final_message": True, "add_generation_prompt": False}).chat(
                (ChatMessage("user", "Question"), ChatMessage("assistant", "<think>\n" + shape.strip("\n") + "\n</think>\n")),
                max_tokens=32, temperature=0.0, seed=3)
            self.assertTrue(runtime._tokenizer.options["continue_final_message"])
            self.assertFalse(runtime._tokenizer.options["add_generation_prompt"])
            self.assertEqual((result.content, result.reasoning_tokens), ("ANSWER: A", 0))
        self.assertIs(runtime._mlx_lm, native)
        self.assertIs(ep.endpoint.runtime, runtime)

    def test_string_stop_spanning_tokens_keeps_exact_work(self):
        clock = FakeClock()
        runtime = native_runtime(clock, "reasoning</think>SHOULD NOT GENERATE")
        ep = endpoint(runtime, clock)
        result = self.call(ep.configured({"stop": ["</think>"], "chat_template_kwargs": {"enable_thinking": True}}))
        self.assertEqual("".join(runtime.observed_tokens), "reasoning</think>")
        self.assertEqual(result.reasoning_text, "reasoning")
        self.assertEqual(result.reasoning_tokens, len("reasoning"))
        self.assertEqual(result.completion_tokens, len("reasoning</think>"))
        self.assertEqual(result.raw_usage["_finish_reason"], "stop")
        self.assertEqual(sum(e["event_type"] == "token" for e in result.raw_usage["native_events"]),
                         result.completion_tokens)
        self.assertTrue(any(e.event_type == "token" for e in ep.endpoint.events))

    def test_censored_prefilled_reasoning_has_no_answer(self):
        clock = FakeClock()
        runtime = native_runtime(clock, "thinking continues")
        ep = endpoint(runtime, clock)
        native_flags = []
        for _ in range(2):
            result = ep.chat((ChatMessage("user", "Question"),), max_tokens=4, temperature=0.0, seed=3)
            self.assertEqual((result.content, result.reasoning_text, result.reasoning_tokens), ("", "thin", 4))
            self.assertEqual(result.raw_usage["_finish_reason"], "length")
            self.assertIn("turn_token_budget_reached", result.raw_usage["_budget_flags"])
            self.assertFalse(any(f.startswith("turn_token_budget_reached:") for f in result.raw_usage["_budget_flags"]))
            indexed = [f for f in result.raw_usage["flags"] if f.startswith("turn_token_budget_reached:")]
            self.assertEqual(indexed, [f"turn_token_budget_reached:{result.raw_usage['native_generation']['turn']}"])
            self.assertNotIn("turn_token_budget_reached", result.raw_usage["flags"])
            self.assertEqual(result.raw_usage["native_generation"], ep.endpoint.turn_provenance[-1])
            native_flags.extend(indexed)
        self.assertEqual(len(set(native_flags)), 2)  # Native calls retain distinct indices.

    def test_fault_restores_runtime_and_is_not_empty_success(self):
        clock = FakeClock()
        runtime = native_runtime(clock, fail_template=True)
        ep = endpoint(runtime, clock)
        native = runtime._mlx_lm
        with self.assertRaisesRegex(RuntimeError, "endpoint_error"):
            self.call(ep)
        self.assertIs(runtime._mlx_lm, native)
        self.assertIs(ep.endpoint.runtime, runtime)

    def test_nonzero_sampling_is_refused(self):
        clock = FakeClock()
        with self.assertRaisesRegex(ValueError, "greedy"):
            endpoint(native_runtime(clock), clock).chat((), max_tokens=10, temperature=0.6, seed=0)


class MatrixTests(unittest.TestCase):
    def test_synthetic_sampler_emits_completed_intervals_only(self):
        clock = FakeClock(100.0)
        adapter = SyntheticAppleTelemetry(clock)
        config = replace(base(), sampling=replace(base().sampling, power_hz=10.0))
        adapter.start_sampling(config, None)
        clock.sleep(0.25)
        result = adapter.stop_sampling_with_evidence(config, None)
        self.assertEqual({s.timestamp_s for s in result.samples}, {100.1, 100.2})
        self.assertTrue(all(s.interval_end_s <= clock.now() for s in result.samples))

    def test_condition_order_preserves_the_full_matrix(self):
        order = [c.name for c in reversed(default_conditions())]
        self.assertEqual([c.name for c in _conditions(order)], order)
        with self.assertRaisesRegex(ValueError, "permutation"):
            _conditions(order[:-1])
    def test_full_dry_matrix_roundtrip_replay_and_energy_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_dry(output=out, config=base(), count=1, seed=7)
            self.assertEqual(len(result.trials), 3 * len(default_conditions()))
            self.assertEqual({t.model for t in result.trials}, set(MODEL_SIZES))
            self.assertTrue(result.metadata["d3"]["synthetic"])
            self.assertEqual(to_json(read_result(out / "result.json")), to_json(result))
            self.assertEqual(list(read_episode_views(out / "episodes.jsonl")), [t.episode for t in result.trials])
            self.assertEqual(normalize_result(result), result)
            for trial in result.trials:
                self.assertFalse(any("generation_error" in f for f in trial.flags), trial.flags)
                self.assertTrue(all(m.method != "unmeasured" for m in trial.episode.clock_mappings))
                self.assertFalse(any("energy_clock_mapping_unmeasured" in f for f in trial.flags))
                energy = apple_energy(trial.episode)
                # Independent closed-form oracle for a designed constant 32.3 W
                # three-rail trace. With uncertainty_j=None (no half-width),
                # CLAUDE.local.md "No silly numbers" defaults to 1e-6 relative
                # (DIFFICULTY revision 2.3). FakeClock has epoch=monotonic,
                # offset=0; a conservative float floor is ~1e-13 relative
                # (observed worst 3.51e-16 relative / 1.07e-14 J), so this
                # bar exceeds 1e6 times noise and is far below 1% of the
                # ~1 J attribution limit.
                expected = (trial.end_ns - trial.start_ns) / 1e9 * (4.0 + 28.0 + 0.3)
                self.assertTrue(math.isclose(energy.joules, expected, rel_tol=1e-6), energy)
                self.assertIsNone(energy.uncertainty_j)  # Unknown native quantum stays unknown.
                self.assertIn("energy_powermetrics_attribution_floor", energy.flags)
                if trial.condition.mode == "deletion":
                    source = next(t for t in result.trials if t.trial_id == trial.source_trial_id)
                    self.assertEqual(trial.episode.power_traces, source.episode.power_traces)
                    self.assertEqual(energy.joules, apple_energy(source.episode).joules)  # Identical capture.
            with patch("joulewise.align.budget.synthetic.ScriptedModel.chat", side_effect=AssertionError("not resumed")), patch.object(
                BudgetAppleSampler, "start", side_effect=AssertionError("must replay trace")):
                replay = run_dry(output=out, config=base(), count=1, seed=7)
            self.assertEqual(replay, result)

    def test_offset_ramp_energy_oracle_and_mapping_counterfactual(self):
        # Production-shaped interval averages on three designed linear rails.
        offset_s = 1_790_901_234.567
        offset_ns = 1_790_901_234_567_000_000  # Exact decimal OFF * 1e9, without float-product rounding.
        start_ns = 100_000_000_000  # run_dry starts monotonic time at 100 s.
        t0 = offset_s + start_ns / 1e9
        rails = {"cpu_power": (4.0, 2.0), "gpu_power": (28.0, 7.0), "ane_power": (0.3, 1.0)}

        class OffsetClock:
            def __init__(self, start=100.0):
                self.mono = float(start)

            def now(self):
                return self.mono + offset_s

            def stamp(self):
                return ClockStamp(epoch_s=self.now(), monotonic_before_s=self.mono,
                                  monotonic_after_s=self.mono, wall_resolution_s=0.0,
                                  monotonic_resolution_s=0.0)

            def sleep(self, seconds):
                self.mono += seconds

            def info(self):
                return {"kind": "offset-fake"}

        class RampTelemetry:
            def __init__(self, clock):
                self.clock = clock

            def start_sampling(self, config, context):
                self.start_s = self.clock.now()
                return AdapterResult(ok=True)

            def stop_sampling_with_evidence(self, config, context, **kwargs):
                step = 1 / config.sampling.power_hz
                count = math.floor((self.clock.now() - self.start_s) / step)
                samples = []
                for i in range(1, count + 1):
                    t = self.start_s + i * step
                    for rail, (watts, slope) in rails.items():
                        samples.append(PowerSample(t, watts + slope * ((t - step / 2) - t0),
                                                   "powermetrics", rail, t - step, t))
                return TelemetryStopResult(samples, {"clock_anchor": {
                    "status": "bounded", "method": "synthetic_offset_anchor",
                    "wall_minus_monotonic_lower_s": offset_s,
                    "wall_minus_monotonic_upper_s": offset_s,
                    "effective_clock_anchor_bound_s": 0.0}})

        config = BenchmarkConfig.from_mapping(json.loads((ROOT / "configs/examples/mock_local.json").read_text()))
        with tempfile.TemporaryDirectory() as tmp, patch(
            "joulewise.align.budget.apple.run.FakeClock", OffsetClock
        ), patch("joulewise.align.budget.apple.run.SyntheticAppleTelemetry", RampTelemetry):
            result = run_dry(output=Path(tmp), config=config, count=1, seed=3)
        # A width-dt support overlapping by o uses its WHOLE-support mean.
        # On a linear ramp its error is k*o*(dt-o)/2, maximized at o=dt/2:
        # k*dt**2/8. Only the two episode-edge supports can err, so the
        # bound is 2*k*dt**2/8 = 0.025 J (summed slope k=10 W/s, dt=0.1 s).
        # Epoch-scale float noise is ~1.7e-6 J, four orders below this bar.
        # The 1e-6 relative default is not used: it sits far below doctrine's
        # 1e6x float-noise separation; shorter trials could fail on timestamp noise.
        k, dt = 10.0, 0.1
        bar_j = 2 * k * dt ** 2 / 8
        for trial in result.trials:
            episode = trial.episode
            # Subtract integer monotonic ns BEFORE converting to relative
            # seconds since T0; the oracle never adds an epoch-sized float.
            s = (episode.start_ns - start_ns) / 1e9
            e = (episode.end_ns - start_ns) / 1e9
            expected = sum(a * (e - s) + b * (e ** 2 - s ** 2) / 2 for a, b in rails.values())
            energy = apple_energy(episode)
            self.assertIsNotNone(energy.joules, (trial.trial_id, energy.flags))
            self.assertLessEqual(abs(energy.joules - expected), bar_j, trial.trial_id)
            self.assertTrue(episode.clock_mappings)
            for mapping in episode.clock_mappings:
                self.assertLessEqual(abs(mapping.offset_ns + offset_ns), mapping.uncertainty_ns)
            # A -100 ms offset shift moves integration 0.1 s RIGHT, within
            # the sampler's 1 s post-window dwell. Total slope is 10 W/s,
            # so this changes energy by 10 * 0.1 * duration = ~1 J/s of
            # trial, exercising the mapping well above the derived bar.
            shifted = replace(episode, clock_mappings=tuple(
                replace(m, offset_ns=m.offset_ns - 100_000_000) for m in episode.clock_mappings))
            wrong = apple_energy(shifted)
            self.assertIsNotNone(wrong.joules, (trial.trial_id, wrong.flags))
            self.assertGreater(abs(wrong.joules - expected), bar_j, trial.trial_id)
            # End-stamped averages treated as points lag half an interval.
            point = episode_energy(episode, channels=CHANNELS)
            self.assertIsNotNone(point.joules, (trial.trial_id, point.flags))
            self.assertGreater(abs(point.joules - expected), bar_j, trial.trial_id)

    def test_step_interval_average_energy_with_partial_edge_bound(self):
        # Designed levels, not M3 measurements: summed IDLE=1.5 W, BUSY=34.3 W.
        idle = {"cpu_power": 1.0, "gpu_power": 0.5, "ane_power": 0.0}
        busy = {"cpu_power": 6.0, "gpu_power": 28.0, "ane_power": 0.3}
        delta_w = math.fsum(busy.values()) - math.fsum(idle.values())  # 32.8 W.
        dt = 0.1  # Designed 10 Hz supports, matching powermetrics' interval convention.
        original_chat = ScriptedModel.chat
        for phase_s in (0.0, 0.05):
            with self.subTest(phase_s=phase_s):
                calls = []

                def chat(model, *args, **kwargs):
                    result = original_chat(model, *args, **kwargs)
                    calls.append((result.start_ns, result.end_ns))
                    return result

                def busy_ns(a, b):
                    return sum(max(0, min(b, end) - max(a, start)) for start, end in calls)

                class StepTelemetry:
                    def __init__(self, clock):
                        self.clock = clock

                    def start_sampling(self, config, context):
                        self.start_s = self.clock.now() + phase_s
                        return AdapterResult(ok=True)

                    def stop_sampling_with_evidence(self, config, context, **kwargs):
                        step = 1 / config.sampling.power_hz
                        count = math.floor((self.clock.now() - self.start_s) / step)
                        samples = []
                        for i in range(1, count + 1):
                            t = self.start_s + i * step
                            a, b = round((t - step) * 1e9), round(t * 1e9)
                            fraction = busy_ns(a, b) / (b - a)
                            for rail in idle:
                                watts = idle[rail] + (busy[rail] - idle[rail]) * fraction
                                samples.append(PowerSample(t, watts, "powermetrics", rail, t - step, t))
                        return TelemetryStopResult(samples, {"clock_anchor": {
                            "status": "bounded", "method": "synthetic_identity_clock",
                            "wall_minus_monotonic_lower_s": 0.0,
                            "wall_minus_monotonic_upper_s": 0.0,
                            "effective_clock_anchor_bound_s": 0.0}})

                with tempfile.TemporaryDirectory() as tmp, patch.object(ScriptedModel, "chat", chat), patch(
                    "joulewise.align.budget.apple.run.SyntheticAppleTelemetry", StepTelemetry
                ):
                    result = run_dry(output=Path(tmp), config=base(), count=1)
                seen = set()
                for trial in result.trials:
                    episode = trial.episode
                    key = episode.start_ns, episode.end_ns
                    if key in seen:
                        continue
                    seen.add(key)
                    start, end = key
                    expected = (math.fsum(idle.values()) * (end - start)
                                + delta_w * busy_ns(start, end)) / 1e9
                    supports = json.loads(episode.power_traces[0].notes)["sample_support_ns"]
                    # With power bounded in [IDLE, BUSY], a support straddling
                    # an edge by o errs by <= dP*o*(dt-o)/dt, at most
                    # dP*dt/4 = 0.82 J per edge here. Full supports inside
                    # the episode are exact: mean times width is the integral.
                    bound = 0.0
                    for edge in (start, end):
                        for a, b in supports:
                            if a < edge < b:
                                o = max(0, min(end, b) - max(start, a)) / 1e9
                                bound += delta_w * o * (dt - o) / dt
                    # COMMON 1e-6 relative default for float noise; FakeClock
                    # noise here is ~1e-13 relative, far below this allowance.
                    bound += 1e-6 * expected
                    energy = apple_energy(episode)
                    self.assertIsNotNone(energy.joules, (phase_s, trial.trial_id, energy.flags))
                    self.assertLessEqual(abs(energy.joules - expected), bound, (phase_s, trial.trial_id))
                    self.assertIsNone(energy.uncertainty_j)
                    self.assertIn("energy_interval_average_support_overlap", energy.flags)

    def test_unresolved_anchor_and_missing_channel_have_no_energy(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_dry(output=Path(tmp), config=base(), count=1)
            ep = result.trials[0].episode
            first, *rest = ep.power_traces

            def with_notes(notes):
                return replace(ep, power_traces=(replace(first, notes=json.dumps(notes)), *rest))

            missing = json.loads(first.notes)
            missing.pop("sample_support_ns")
            cases = [(with_notes(missing), "energy_sample_support_missing")]
            supports = json.loads(first.notes)["sample_support_ns"]
            for malformed in (None, [], supports[:-1], [None, *supports[1:]],
                              [[0, 0], *supports[1:]], [[0.0, 1], *supports[1:]],
                              [supports[1], supports[0], *supports[2:]]):
                notes = json.loads(first.notes)
                notes["sample_support_ns"] = malformed
                cases.append((with_notes(notes), "energy_sample_support_missing"))
            for value in (-1.0, math.inf, math.nan):
                cases.append((replace(ep, power_traces=(
                    replace(first, values=(value, *first.values[1:])), *rest)), "energy_samples_invalid"))
            cases.extend([
                (replace(ep, power_traces=tuple(rest)), "energy_channel_missing_or_duplicate"),
                # Three traces can still duplicate one rail while missing another.
                (replace(ep, power_traces=(first, first, rest[0])), "energy_channel_missing_or_duplicate"),
                (replace(ep, clock_mappings=tuple(replace(m, episode_domain="unrelated")
                                                for m in ep.clock_mappings)), "energy_clock_mapping_invalid"),
                (replace(ep, clock_mappings=(*ep.clock_mappings, *ep.clock_mappings)),
                 "energy_clock_mapping_invalid"),
                (replace(ep, clock_mappings=tuple(replace(m, uncertainty_ns=-1)
                                                for m in ep.clock_mappings)), "energy_clock_mapping_invalid"),
                (replace(ep, clock_mappings=tuple(replace(m, method="unmeasured")
                                                for m in ep.clock_mappings)), "energy_clock_mapping_unmeasured"),
                (replace(ep, clock_mappings=tuple(replace(m, offset_ns=m.offset_ns + 1_000_000_000_000)
                                                for m in ep.clock_mappings)), "energy_trace_unbracketed"),
                (replace(ep, power_traces=tuple(replace(t, t_ns=(), values=()) for t in ep.power_traces)),
                 "energy_trace_missing"),
            ])
            for episode, flag in cases:
                with self.subTest(flag=flag, episode=episode.episode_id):
                    energy = apple_energy(episode)
                    self.assertIsNone(energy.joules)
                    self.assertEqual(energy.flags, (flag,))
            duplicate_scope = replace(ep.power_traces[0], channel="package",
                                      values=tuple(1000.0 for _ in ep.power_traces[0].values))
            self.assertEqual(apple_energy(replace(ep, power_traces=(*ep.power_traces, duplicate_scope))).joules,
                             apple_energy(ep).joules)  # Same three selected channels, exactly.
            traces = []
            for trace in ep.power_traces:
                notes = json.loads(trace.notes)
                notes["clock_anchor"]["status"] = "unknown"
                traces.append(replace(trace, notes=json.dumps(notes)))
            self.assertEqual(apple_energy(replace(ep, power_traces=tuple(traces))).flags,
                             ("energy_apple_anchor_unresolved",))

            # One dropped poll doubles an otherwise regular 100 ms cycle;
            # the shared 1.5-cycle diagnostic flags it without refusing J.
            notes = json.loads(first.notes)
            del notes["sample_support_ns"][2]
            notes["flags"].append("synthetic_trace_flag")
            dropped = replace(first, t_ns=first.t_ns[:2] + first.t_ns[3:],
                              values=first.values[:2] + first.values[3:], notes=json.dumps(notes),
                              duty_fraction=0.5)
            energy = apple_energy(replace(ep, power_traces=(dropped, *rest), flags=("synthetic_episode_flag",)))
            self.assertIsNotNone(energy.joules)
            for flag in ("energy_sample_gap", "synthetic_trace_flag", "synthetic_episode_flag",
                         "energy_duty_cycled_requires_repetitions", "energy_interval_average_support_overlap"):
                self.assertIn(flag, energy.flags)
            self.assertIsNone(energy.uncertainty_j)

            # Mapping uncertainty that extends past both trace bounds admits
            # measured overlap and labels the partial clock bracket.
            extent = first.t_ns[-1] - first.t_ns[0]
            partial = replace(ep, clock_mappings=tuple(replace(m, uncertainty_ns=extent)
                                                     for m in ep.clock_mappings))
            energy = apple_energy(partial)
            self.assertIsNotNone(energy.joules)
            self.assertIn("energy_clock_bracket_partial", energy.flags)

    def test_unavailable_sampler_preserves_notes_without_zero_energy(self):
        clock = FakeClock(100.0)
        adapter = SimpleNamespace(start_sampling=lambda *a: AdapterResult(ok=False, message="synthetic permission denied"))
        sampler = BudgetAppleSampler(base(), clock, episode_domain=DOMAIN, adapter=adapter)
        sampler.start()
        clock.sleep(1.0)
        traces = sampler.stop()
        ep = Episode("unavailable", "synthetic", "benign", "mock", "mock", 0, DOMAIN,
                     100_000_000_000, 101_000_000_000, (), power_traces=traces,
                     clock_mappings=sampler.clock_mappings)
        self.assertIsNone(apple_energy(ep).joules)
        self.assertEqual(apple_energy(ep).flags, ("energy_trace_missing",))
        empty = apple_energy(replace(ep, power_traces=()))
        self.assertIsNone(empty.joules)
        self.assertEqual(empty.flags, ("energy_trace_missing",))
        self.assertEqual(traces[0].values, ())
        self.assertIn("power_unavailable:synthetic permission denied", json.loads(traces[0].notes)["flags"])

    def test_live_entrypoint_with_native_boundary_injected(self):
        clock = FakeClock(100.0)
        runtime = native_runtime(clock)
        metadata = {"mlx_version": "synthetic", "mlx_lm_version": "synthetic",
                    "load_wall_time_s": 12.0, "memory_snapshots": ["synthetic"]}
        settings = Settings(100, 32, calibration_repetitions=1, temperature=0.0, measurement_id="synthetic-live-seam")
        model = CachedModel("mlx-community/Qwen3-4B-4bit", "a" * 40, "/synthetic", 4.0)
        original_sampler = BudgetAppleSampler

        def sampler(*args, **kwargs):
            return original_sampler(*args, **kwargs, adapter=SyntheticAppleTelemetry(clock))

        with tempfile.TemporaryDirectory() as tmp, patch(
            "joulewise.align.budget.apple.run.platform.system", return_value="Darwin"
        ), patch("joulewise.align.budget.apple.run.platform.machine", return_value="arm64"), patch(
            "joulewise.align.budget.apple.run.subprocess.check_output", return_value="Apple M3 Max"
        ), patch("joulewise.align.budget.apple.run.SystemClock", return_value=clock), patch(
            "joulewise.adapters.mlx_runtime.MlxRuntimeAdapter", return_value=runtime
        ), patch.object(runtime, "prepare", return_value=AdapterResult(ok=True, metadata=metadata)), patch.object(
            runtime, "cleanup", return_value=AdapterResult(ok=True)
        ), patch("joulewise.align.budget.apple.run.BudgetAppleSampler", side_effect=sampler), patch.dict("os.environ"):
            out = Path(tmp)
            args = dict(output=out, config=base(), model=model, items=synthetic_items(1),
                        monitor=HintMonitor(ScriptedMonitor(), model="synthetic-monitor", revision="test"),
                        settings=settings, seed=0, controls_verified=True)
            result = run_live(**args)
            self.assertEqual(len(result.trials), 11)
            self.assertEqual(len(list((out / "preflight").glob("*.json"))), 1)
            self.assertTrue((out / "rosters" / (result.metadata["d3"]["roster_sha256"] + ".json")).is_file())
            self.assertNotIn("load_wall_time_s", result.metadata["d3"]["prepare"])
            for t in result.trials:
                self.assertFalse(any("generation_error" in f or "backend_kind_unrecognized" in f for f in t.flags), t.flags)
                self.assertIsNotNone(apple_energy(t.episode).joules)
            # New preparation time/memory are not part of experiment identity.
            metadata["load_wall_time_s"] = 99.0
            metadata["memory_snapshots"] = ["different"]
            with patch.object(BudgetMlxEndpoint, "chat", side_effect=AssertionError("only warm calls allowed")):
                # Skip warm generation for this checkpoint-only replay.
                with patch("joulewise.align.budget.apple.run.preflight", return_value=()):
                    replay = run_live(**args)
            self.assertEqual(replay.run_sha256, result.run_sha256)
            self.assertEqual(to_json(replay.trials), to_json(result.trials))

    def test_cli_rejects_live_without_configuration(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--live", "--benchmark", str(ROOT / "configs/examples/mac_mlx_local.json"),
                                   "--output", tmp]), 1)


if __name__ == "__main__":
    unittest.main()
