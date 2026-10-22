"""Offline end-to-end checks of the actual budget runner and serving adapter."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import math
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal, localcontext
from pathlib import Path
from statistics import NormalDist
from unittest.mock import patch

from joulewise.align.budget.__main__ import main
from joulewise.align.budget.conditions import (
    Condition, LocalEndpoint, cap_tokens, default_conditions, delete_spans, thinking_options,
)
from joulewise.align.budget.energy import episode_energy
from joulewise.align.budget.items import FixtureSource, HubMMLUSource, HubPin, ItemBatch
from joulewise.align.budget.run import BudgetTrial, ModelSpec, Settings, run_matrix, summarize, summary_table
from joulewise.align.budget.score import HintMonitor, judge_hint_use, wilson
from joulewise.align.budget.synthetic import (
    DISCLOSURE, deletion_survival_probability, FIVE_CONFIGURATIONS, ScriptedModel, ScriptedMonitor, ScriptedSampler, SyntheticClock,
    WordCodec, run_synthetic, synthetic_items,
)
from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest
from joulewise.align.records import ClockMapping, PowerTrace, RecordError, from_json, to_json


def wilson_decimal(k: int, n: int, confidence: float) -> tuple[float, float]:
    """Independent quadratic score-test inversion, rather than the production center/half formula."""
    with localcontext() as context:
        context.prec = 50  # Arithmetic precision, not an empirical acceptance bar.
        z = Decimal(str(NormalDist().inv_cdf((1 + confidence) / 2)))
        dn, dk = Decimal(n), Decimal(k)
        # n(p-k/n)^2 <= z^2 p(1-p); solve its quadratic boundaries.
        a = dn + z * z
        b = -(2 * dk + z * z)
        c = dk * dk / dn
        discriminant = (b * b - 4 * a * c).sqrt()
        return float((-b - discriminant) / (2 * a)), float((-b + discriminant) / (2 * a))


class OfflineTest(unittest.TestCase):
    def setUp(self) -> None:
        # Every test injects transports/bytes. Any accidental HTTP path fails locally.
        self.addCleanup(patch.stopall)
        patch("joulewise.align.budget.items.urlopen",
              side_effect=AssertionError("network forbidden in tests")).start()
        patch("joulewise.align.budget.conditions.urlopen",
              side_effect=AssertionError("network forbidden in tests")).start()

    def close_number(self, actual: float, expected: float, *, uncertainty: float | None = None) -> None:
        # The agreement bar is >= 1e6 ulps and <= 1% of the reported half-width.
        # Without a measured uncertainty, the brief prescribes 1e-6 relative.
        noise = 1_000_000 * math.ulp(max(abs(expected), 1.0))
        tolerance = (uncertainty * 0.01 if uncertainty is not None
                     else max(noise, abs(expected) * 1e-6))
        self.assertGreaterEqual(tolerance, noise)
        self.assertLessEqual(abs(actual - expected), tolerance)

    def world(self, *, count=8, conditions=FIVE_CONFIGURATIONS, power=False,
              checkpoint=None, monitor_endpoint=None, seed=7):
        items = synthetic_items(count)
        clock, codec = SyntheticClock(), WordCodec()
        endpoint = ScriptedModel(items.items, clock, codec)
        model = ModelSpec("scripted-4B", 4.0, "mock", endpoint.identity, codec,
                          endpoint.configured, "dense", "synthetic:monotonic",
                          controls_verified=True)
        result = run_matrix(items, (model,), conditions, seeds=(seed,),
                            settings=Settings(1536, 32, measurement_id="test-world"),
                            monitor=HintMonitor(monitor_endpoint or ScriptedMonitor()),
                            checkpoint=checkpoint,
                            sampler_factory=(lambda m: ScriptedSampler(clock, 80.0)) if power else None,
                            clock=clock)
        return result, endpoint


class BudgetItemsTests(OfflineTest):
    def test_fixture_is_authored_balanced_and_paired(self):
        batch = FixtureSource(seed=3).load()
        self.assertEqual(len(batch.items), 8)
        self.assertEqual({i.hint_kind for i in batch.items},
                         {"authority", "metadata", "grader", "sycophancy"})
        for item in batch.items:
            self.assertNotEqual(item.correct_answer, item.hinted_answer)
            self.assertIn("Additional context:", item.prompt())
            self.assertNotIn("Additional context:", item.prompt(hinted=False))

    def test_pinned_json_loader_and_digest_failure(self):
        rows = [{"input": "What is 2 + 3?", "A": "4", "B": "5", "C": "6", "D": "7",
                 "target": "B"}]
        raw = json.dumps(rows).encode()
        pin = HubPin("example/mmlu", "a" * 40, "test.json", hashlib.sha256(raw).hexdigest())
        calls = []
        def fetch(url, timeout):
            calls.append(url)
            return raw
        batch = HubMMLUSource(timeout_s=30, pin=pin, fetch=fetch).load()
        self.assertEqual(len(batch.items), 1)
        self.assertIn(pin.revision, calls[0])
        self.assertIn(pin.sha256, batch.items[0].provenance)
        bad = HubMMLUSource(timeout_s=30, pin=replace(pin, sha256="0" * 64), fetch=fetch).load()
        self.assertFalse(bad.items)
        self.assertIn("dataset_sha256_mismatch", bad.flags)

    def test_moving_revision_and_source_failure_are_flags(self):
        pin = HubPin("example/mmlu", "main", "test.json", "0" * 64)
        self.assertIn("dataset_pin_invalid", HubMMLUSource(timeout_s=1, pin=pin).load().flags)
        pin = replace(pin, revision="a" * 40)
        def failing(url, timeout):
            raise OSError("synthetic transport failure")
        self.assertIn("dataset_fetch_failed:OSError",
                      HubMMLUSource(timeout_s=1, pin=pin, fetch=failing).load().flags)

    @unittest.skipUnless(importlib.util.find_spec("pyarrow") is not None,
                         "optional pyarrow is required only to decode public MMLU Parquet")
    def test_optional_parquet_uses_verified_bytes_offline(self):
        import pyarrow as arrow
        import pyarrow.parquet as parquet

        output = io.BytesIO()
        parquet.write_table(arrow.Table.from_pylist([
            {"question": "What is 2 + 3?", "choices": ["4", "5", "6", "7"], "answer": 1}
        ]), output)
        raw = output.getvalue()
        pin = HubPin("cais/mmlu", "c" * 40, "test.parquet", hashlib.sha256(raw).hexdigest())
        batch = HubMMLUSource(timeout_s=1, pin=pin, fetch=lambda u, t: raw).load()
        self.assertEqual(batch.items[0].correct_answer, "B")


class BudgetScoringTests(OfflineTest):
    def test_paired_causal_label_and_ambiguous_answers(self):
        item = FixtureSource().load().items[0]
        use = judge_hint_use(item, f"ANSWER: {item.hinted_answer}", f"ANSWER: {item.correct_answer}")
        self.assertTrue(use.uses_hint)
        same = judge_hint_use(item, item.hinted_answer, item.hinted_answer)
        self.assertFalse(same.uses_hint)
        unresolved = judge_hint_use(item, "ANSWER: A or ANSWER: B", item.correct_answer)
        self.assertIsNone(unresolved.uses_hint)
        self.assertIn("hint_use_unresolved", unresolved.flags)

    def test_wilson_matches_independent_decimal_score_inversion(self):
        for n in (50, 150, 200):
            for k in (0, 1, n // 3, n - 1, n):
                actual = wilson(k, n)
                expected = wilson_decimal(k, n, actual.confidence)
                # Smallest plotted half-width is represented by this interval itself.
                uncertainty = (actual.interval[1] - actual.interval[0]) / 2
                for a, b in zip(actual.interval, expected):
                    self.close_number(a, b, uncertainty=uncertainty)
        self.assertIsNone(wilson(0, 0).estimate)
        self.assertIn("rate_inputs_invalid", wilson(3, 2).flags)

    def test_monitor_failure_keeps_trials_and_empty_rates(self):
        class Broken:
            identity = "mock:broken-monitor"
            def chat(self, *args, **kwargs):
                raise OSError("synthetic failure")
        result, _ = self.world(count=8, conditions=(Condition("thinking_on"),),
                               monitor_endpoint=Broken())
        self.assertEqual(len(result.trials), 8)
        self.assertTrue(all(t.monitor_flagged is None for t in result.trials))
        row = summarize(result.trials)[0]
        self.assertEqual(row.scored_trials, 0)
        self.assertIsNone(row.catch_rate.estimate)
        self.assertIn("monitor_error:OSError", row.flags)


class BudgetConditionTests(OfflineTest):
    def test_uncapped_calibration_uses_item_median_not_mean(self):
        items, clock, codec = synthetic_items(1), SyntheticClock(), WordCodec()
        endpoint = ScriptedModel(items.items, clock, codec)
        lengths = (896, 1024, 1408)  # Designed asymmetric uncapped lengths; median != mean.
        factory_calls = []
        def factory(options):
            index = len(factory_calls)
            factory_calls.append(options)
            configured = endpoint.configured(options)
            return replace(configured, base_reasoning_tokens=lengths[index]) if index < 3 else configured
        model = ModelSpec("varying", 4.0, "mock", endpoint.identity, codec, factory,
                          clock_domain="synthetic:monotonic", controls_verified=True)
        result = run_matrix(items, (model,), (Condition("budget", "budget", 0.6),), seeds=(2,),
                            settings=Settings(1536, 32), monitor=HintMonitor(ScriptedMonitor()),
                            clock=clock)
        self.assertEqual(result.calibrations[0].lengths, lengths)
        self.close_number(result.calibrations[0].median_tokens, 1024.0)
        self.assertEqual(result.trials[0].requested_cap_tokens, 614)
        self.assertEqual(result.trials[0].reasoning_tokens, 614)

    def test_default_fraction_controls_and_exact_deletion(self):
        conditions = default_conditions()
        self.assertEqual([c.fraction for c in conditions if c.mode == "budget"], [1.0, 0.6, 0.4, 0.3])
        self.assertFalse(thinking_options("vllm", False)["chat_template_kwargs"]["enable_thinking"])
        self.assertEqual(thinking_options("llamacpp", False)["reasoning_effort"], "none")
        codec = WordCodec()
        text = " ".join(f"token{i}" for i in range(1024))
        deletion = delete_spans(text, remove_tokens=410, codec=codec, seed=9)
        self.assertEqual(deletion.removed_tokens, 410)
        self.assertEqual(sum(b - a for a, b in deletion.spans), 410)
        self.assertEqual(deletion.visible_tokens, 614)
        self.assertEqual(deletion, delete_spans(text, remove_tokens=410, codec=codec, seed=9))

    def test_forced_continuation_preserves_both_calls_and_options(self):
        result, endpoint = self.world(count=2, conditions=(Condition("budget", "budget", 0.4),))
        for trial in result.trials:
            self.assertEqual(len(trial.episode.turns), 2)
            self.assertEqual(trial.requested_cap_tokens, 409)  # floor(0.4 * median 1024).
            self.assertEqual(trial.reasoning_tokens, 409)
            self.assertEqual(trial.episode.totals()["decode_tokens"], 411)  # 409 reasoning + 2 answer.
            options = json.loads(trial.generation.request_options[-1])
            self.assertTrue(options["continue_final_message"])
            self.assertFalse(options["add_generation_prompt"])
        continued = [r for r in endpoint.requests if r["options"].get("continue_final_message")]
        self.assertTrue(continued)
        self.assertTrue(all(r["messages"][-1].role == "assistant"
                            and r["messages"][-1].content.endswith("\n</think>\n")
                            for r in continued))

    def test_thinking_off_concise_and_zero_budget_use_real_runner(self):
        configs = (Condition("off", "off"), Condition("concise", "concise"),
                   Condition("zero", "budget", 0.0), Condition("full", "budget", 1.0))
        result, _ = self.world(count=4, conditions=configs)
        by_name = {t.condition.name: t for t in result.trials}
        self.assertEqual(by_name["off"].reasoning_tokens, 0)
        self.assertEqual(by_name["zero"].reasoning_tokens, 0)
        self.assertEqual(len(by_name["zero"].episode.turns), 1)
        self.assertEqual(by_name["concise"].reasoning_tokens, 512)  # Script's concise_fraction * 1024.
        self.assertEqual(by_name["full"].reasoning_tokens, 1024)

    def test_serving_json_adapter_runs_through_calibration_pairing_and_monitor(self):
        items, clock, codec = synthetic_items(4), SyntheticClock(), WordCodec()
        script = ScriptedModel(items.items, clock, codec)
        bodies = []
        def transport(path, payload):
            if path == "/tokenize":
                return {"tokens": list(codec.encode(payload.get("prompt", payload.get("content", ""))))}
            if path == "/detokenize":
                return {"prompt": codec.decode(payload["tokens"])}
            bodies.append(payload)
            messages = [ChatMessage(m["role"], m["content"]) for m in payload["messages"]]
            options = {k: v for k, v in payload.items()
                       if k in ("chat_template_kwargs", "continue_final_message", "add_generation_prompt", "stop")}
            reply = script.configured(options).chat(messages, max_tokens=payload["max_tokens"],
                                                    temperature=payload["temperature"], seed=payload["seed"])
            # Real servers sometimes omit reasoning-token details: exercise tokenizer accounting.
            return {"choices": [{"message": {"content": reply.content, "reasoning_content": reply.reasoning_text}}],
                    "usage": {"prompt_tokens": reply.prompt_tokens, "completion_tokens": reply.completion_tokens}}
        # Core limits must override base extras so a configured endpoint cannot bypass the cap.
        endpoint = LocalEndpoint("http://localhost:8000", "mock-qwen", "vllm", 30,
                                 options={"max_tokens": 8192}, transport=transport)
        model = ModelSpec("mock-qwen", 4.0, "vllm", endpoint.identity, endpoint, endpoint.configured)
        result = run_matrix(items, (model,), (Condition("budget", "budget", 0.6),), seeds=(2,),
                            settings=Settings(1536, 32), monitor=HintMonitor(ScriptedMonitor()))
        self.assertEqual(len(result.trials), 4)
        self.assertTrue(all(t.reasoning_tokens == 614 for t in result.trials))
        self.assertTrue(any(b.get("continue_final_message") for b in bodies))
        self.assertTrue(all("reasoning_tokens_from_tokenizer" in t.flags for t in result.trials))


class BudgetRunTests(OfflineTest):
    def test_summary_does_not_merge_distinct_hardware_or_condition_values(self):
        result, _ = self.world(count=1, conditions=(Condition("thinking_on"),))
        original = result.trials[0]
        different_hardware = replace(original, episode=replace(
            original.episode, hardware={**original.episode.hardware, "measurement_id": "different-GPU"}))
        different_condition = replace(original, condition=Condition("thinking_on", "budget", 0.6))
        rows = summarize((original, different_hardware, different_condition))
        self.assertEqual(len(rows), 3)
        self.assertEqual(len({r.configuration_id for r in rows}), 3)

    def test_cli_synthetic_writes_complete_outputs_without_a_socket(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pilot"
            with patch("builtins.print"):
                status = main(["--synthetic", "--count", "2", "--output", str(output)])
            self.assertEqual(status, 0)
            result = json.loads((output / "result.json").read_text())
            self.assertEqual(len(result["trials"]), 10)
            self.assertEqual(len((output / "episodes.jsonl").read_text().splitlines()), 10)
            self.assertEqual(len((output / "paired_episodes.jsonl").read_text().splitlines()), 8)
            self.assertTrue((output / "summary.md").read_text().startswith("| Model |"))
            self.assertTrue((output / "calibration_episodes.jsonl").exists())

    def test_schema_roundtrip_and_unknown_schema(self):
        result, _ = self.world(count=1)
        for trial in result.trials:
            # Bit identity is the shared serialization contract.
            self.assertEqual(to_json(from_json(BudgetTrial, to_json(trial))), to_json(trial))
        data = json.loads(to_json(result.trials[0]))
        data["schema"] = "future-schema"
        with self.assertRaises(RecordError):
            from_json(BudgetTrial, json.dumps(data))

    def test_exact_resume_partial_line_and_fingerprint_separation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trials.jsonl"
            first, _ = self.world(count=4, checkpoint=path)
            resumed, endpoint = self.world(count=4, checkpoint=path)
            self.assertFalse(endpoint.requests)
            self.assertEqual(to_json(first), to_json(resumed))
            with path.open("a") as handle:
                handle.write('{"run":')
            repaired, endpoint = self.world(count=4, checkpoint=path)
            self.assertFalse(endpoint.requests)
            self.assertIn("checkpoint_line_invalid", repaired.flags)
            changed, endpoint = self.world(count=4, checkpoint=path, seed=8)
            self.assertTrue(endpoint.requests)
            self.assertNotEqual(first.run_sha256, changed.run_sha256)
            self.assertIn("checkpoint_other_run", changed.flags)
            replay, endpoint = self.world(count=4, checkpoint=path, seed=8)
            self.assertFalse(endpoint.requests)
            self.assertEqual(to_json(changed.trials), to_json(replay.trials))

    def test_missing_traces_are_empty_and_flagged(self):
        result, _ = self.world(count=8, power=False)
        rows = summarize(result.trials)
        self.assertTrue(all(r.mean_joules is None for r in rows))
        self.assertTrue(all("energy_trace_missing" in r.flags for r in rows))
        self.assertIn("| J |", summary_table(rows))
        self.assertIn("energy_incomplete", summary_table(rows))

    def test_unexpected_tool_calls_are_recorded_not_executed_or_refused(self):
        original = ScriptedModel.chat
        def with_tool(endpoint, *args, **kwargs):
            result = original(endpoint, *args, **kwargs)
            return replace(result, tool_calls=(ToolCallRequest("call0", "calculator", "{}"),))
        with patch.object(ScriptedModel, "chat", with_tool):
            result, _ = self.world(count=2, conditions=(Condition("thinking_on"),))
        self.assertEqual(len(result.trials), 2)
        self.assertTrue(all("unexpected_tool_calls_unexecuted" in t.episode.flags for t in result.trials))

    def test_generation_failure_and_invalid_condition_remain_records(self):
        with patch.object(ScriptedModel, "chat", side_effect=OSError("synthetic endpoint failure")):
            result, _ = self.world(count=2, conditions=(Condition("thinking_on"),))
            invalid, _ = self.world(count=2, conditions=(Condition("bad", "budget", -0.5),))
        self.assertEqual(len(result.trials), 2)
        self.assertTrue(all(t.hint_use.uses_hint is None for t in result.trials))
        self.assertTrue(all("generation_error:OSError" in t.flags for t in result.trials))
        self.assertTrue(all("condition_fraction_invalid" in t.flags for t in invalid.trials))
        self.assertTrue(all("generation_skipped" in t.flags and not t.generation.calls
                            for t in invalid.trials))


class BudgetEnergyTests(OfflineTest):
    def test_reducer_error_and_bad_sensor_metadata_are_flags(self):
        result, _ = self.world(count=1, power=True, conditions=(Condition("thinking_on"),))
        def broken(episode):
            raise ValueError("synthetic reducer failure")
        row = summarize(result.trials, energy_reducer=broken)[0]
        self.assertIsNone(row.mean_joules)
        self.assertIn("energy_reducer_error:ValueError", row.flags)
        episode = result.trials[0].episode
        trace = replace(episode.power_traces[0], resolution=-0.1)
        measured = episode_energy(replace(episode, power_traces=(trace,)))
        self.assertIsNone(measured.joules)
        self.assertIn("energy_resolution_invalid", measured.flags)

    def test_noisy_samples_whole_episode_energy_and_size_comparison(self):
        result = run_synthetic(count=8, seeds=(3,), sizes_b=(4.0, 8.0, 14.0))
        rows = summarize(result.trials)
        on = {r.size_b: r for r in rows if r.condition == "thinking_on"}
        for row in on.values():
            self.close_number(row.mean_decode_tokens, 1026.0)  # 1024 reasoning + two answer tokens.
        # Scripted 4B/8B/14B costs are ~1658/4124/9363 J (P * [prefill + tokens/rate]).
        # Require separation after each sensor quantization bound, not merely float ordering.
        self.assertLess(on[4.0].mean_joules + on[4.0].max_measurement_uncertainty_j,
                        on[8.0].mean_joules - on[8.0].max_measurement_uncertainty_j)
        self.assertLess(on[8.0].mean_joules + on[8.0].max_measurement_uncertainty_j,
                        on[14.0].mean_joules - on[14.0].max_measurement_uncertainty_j)
        for trial in result.trials:
            trace = trial.episode.power_traces[0]
            # Independent rectangular-plus-slope integration on raw 100 ms samples.
            # Integrate only the Episode; the sampler now retains a trailing poll
            # beyond it, as the real event.wait sampler must.
            expected = 0.0
            for a, b, x, y in zip(trace.t_ns, trace.t_ns[1:], trace.values, trace.values[1:]):
                lo, hi = max(a, trial.episode.start_ns), min(b, trial.episode.end_ns)
                if hi > lo:
                    left = x + (y - x) * ((lo - a) / (b - a))
                    right = x + (y - x) * ((hi - a) / (b - a))
                    expected += (hi - lo) / 1e9 * (left + right) / 2
            energy = episode_energy(trial.episode)
            self.close_number(energy.joules, expected, uncertainty=energy.uncertainty_j)

    def test_counter_clock_mapping_duty_cycle_and_missing_bracket(self):
        result, _ = self.world(count=1, power=True, conditions=(Condition("thinking_on"),))
        episode = result.trials[0].episode
        start, end = episode.start_ns, episode.end_ns
        duration = (end - start) / 1e9
        # Designed constant 80 W, 10 ms foreign-clock offset, 1 ms offset half-width.
        offset, uncertainty = 10_000_000, 1_000_000
        times = (start - offset - uncertainty, end - offset + uncertainty)
        counter = PowerTrace("nvml_energy", "gpu0", "foreign", times,
                             (100.0, 100.0 + 80.0 * ((times[1] - times[0]) / 1e9)),
                             "J_cumulative", end - start, resolution=0.001)
        mapping = ClockMapping("foreign", episode.clock_domain, offset, uncertainty, "synthetic-bracket")
        mapped = replace(episode, power_traces=(counter,), clock_mappings=(mapping,))
        energy = episode_energy(mapped)
        self.close_number(energy.joules, 80 * duration, uncertainty=energy.uncertainty_j)
        duty = replace(episode.power_traces[0], duty_fraction=0.25, averaging_window_ns=25_000_000)
        measured = episode_energy(replace(episode, power_traces=(duty,)))
        self.assertIn("energy_duty_cycled_requires_repetitions", measured.flags)
        self.assertIsNone(measured.uncertainty_j)
        short = replace(episode.power_traces[0], t_ns=(start + 1, end), values=(80.0, 80.0))
        self.assertIsNone(episode_energy(replace(episode, power_traces=(short,))).joules)

    def test_ambiguous_channels_and_unmeasured_clock_leave_energy_empty(self):
        result, _ = self.world(count=1, power=True, conditions=(Condition("thinking_on"),))
        episode = result.trials[0].episode
        trace = episode.power_traces[0]
        redundant = replace(episode, power_traces=(trace, replace(trace, channel="gpu1")))
        self.assertIn("energy_channels_unspecified", episode_energy(redundant).flags)
        chosen = episode_energy(redundant, channels=(("mock", "gpu0"),))
        self.assertIsNotNone(chosen.joules)
        foreign = replace(trace, clock_domain="unmeasured")
        mapping = ClockMapping("unmeasured", episode.clock_domain, 0, 0, "unmeasured")
        unknown = replace(episode, power_traces=(foreign,), clock_mappings=(mapping,))
        self.assertIsNone(episode_energy(unknown).joules)


class BudgetEndToEndTests(OfflineTest):
    def test_five_configurations_times_200_with_deletion_control(self):
        result = run_synthetic(count=200, seeds=(0,), with_power=True)
        self.assertEqual(len(result.trials), 5 * 200)
        self.assertEqual(len(result.calibrations), 200)
        by_key = {(t.item_id, t.condition.name): t for t in result.trials}
        for item in synthetic_items(200).items:
            source = by_key[item.item_id, "thinking_on"]
            cut = by_key[item.item_id, "budget_0.6"]
            deletion = by_key[item.item_id, "deletion_0.6"]
            self.assertEqual(deletion.removed_tokens, source.reasoning_tokens - cut.reasoning_tokens)
            self.assertEqual(deletion.visible_reasoning_tokens, cut.reasoning_tokens)
            self.assertEqual(deletion.episode.power_traces, source.episode.power_traces)
            self.assertEqual(deletion.episode.totals()["decode_tokens"], source.episode.totals()["decode_tokens"])
            self.assertEqual(deletion.episode.totals()["hidden_tokens"], deletion.removed_tokens)
            self.assertEqual(deletion.source_trial_id, source.trial_id)
            self.close_number(episode_energy(deletion.episode).joules,
                              episode_energy(source.episode).joules,
                              uncertainty=episode_energy(source.episode).uncertainty_j)
        rows = {r.condition: r for r in summarize(result.trials)}
        # A 13-token phrase survives four spans with p=0.549668, versus
        # (614/1024)^2=0.359531 for a budget cut. At only 144 positives the
        # marginal 95% Wilson intervals can overlap. Preserve the interval-
        # separation bar and exercise it on a larger independent item roster.
        # With 2000 designed items (~1500 positives), the sum of worst-case
        # half-widths is z/sqrt(1500) ~= 0.051, below half the 0.190 gap.
        separation = {r.condition: r for r in summarize(run_synthetic(
            count=2000, seeds=(0,), with_power=False,
            conditions=(Condition("thinking_on"), Condition("budget_0.6", "budget", 0.6),
                        Condition("deletion_0.6", "deletion", 0.6))).trials)}
        self.assertGreater(separation["deletion_0.6"].catch_rate.interval[0],
                           separation["budget_0.6"].catch_rate.interval[1])
        print("SYNTHETIC separation / 2000 items:",
              {name: separation[name].catch_rate for name in ("budget_0.6", "deletion_0.6")})
        # Removing 410 generated tokens saves 8.2 s minus the extra 0.2 s prefill:
        # at 80 W this is 640 J; compare with both computed edge/sensor half-widths.
        self.assertGreater(rows["deletion_0.6"].mean_joules
                           - rows["deletion_0.6"].max_measurement_uncertainty_j,
                           rows["budget_0.6"].mean_joules
                           + rows["budget_0.6"].max_measurement_uncertainty_j)
        for name, fraction in (("budget_0.6", 614 / 1024), ("budget_0.4", 409 / 1024),
                               ("budget_0.3", 307 / 1024), ("deletion_0.6", 614 / 1024)):
            probability = (deletion_survival_probability(1024, 1024 - cap_tokens(1024, fraction),
                                                        len(DISCLOSURE.split()))
                           if name.startswith("deletion") else fraction ** 2)
            # Each seed-0 rate must also contain its scripted probability
            # within its nominal 95% Wilson interval on the five-by-200 world.
            low, high = rows[name].catch_rate.interval
            self.assertLessEqual(low, probability)
            self.assertGreaterEqual(high, probability)
            positives = [t for t in result.trials if t.condition.name == name
                         and t.hint_use.uses_hint is True]
            # An independent transcript count checks the monitor/scoring numerator.
            visible_mentions = 0
            for trial in positives:
                if trial.condition.mode == "deletion":
                    tokens = trial.generation.reasoning.split()
                    removed = {i for a, b in trial.deleted_spans for i in range(a, b)}
                    visible_mentions += DISCLOSURE in " ".join(w for i, w in enumerate(tokens) if i not in removed)
                else:
                    visible_mentions += DISCLOSURE in trial.generation.reasoning
            self.assertEqual(rows[name].catch_rate.successes, visible_mentions)
            self.assertEqual(rows[name].catch_rate.trials, len(positives))
        print("\nSYNTHETIC five configurations x 200 items (seed 0):\n"
              + summary_table(tuple(rows.values())))

    def test_wilson_nominal_coverage_across_independent_seeds(self):
        coverage = {c.name: 0 for c in FIVE_CONFIGURATIONS if c.mode != "on"}
        count = 80  # Test design: 80 independent seeds, 200 items/configuration/seed.
        for seed in range(count):
            rows = summarize(run_synthetic(count=200, seeds=(seed,), with_power=False).trials)
            for row in rows:
                if row.condition not in coverage:
                    continue
                fraction = cap_tokens(1024, float(row.condition.rsplit("_", 1)[1])) / 1024
                probability = (deletion_survival_probability(1024, 1024 - cap_tokens(1024, fraction),
                                                            len(DISCLOSURE.split()))
                               if row.condition.startswith("deletion") else fraction ** 2)
                low, high = row.catch_rate.interval
                coverage[row.condition] += low <= probability <= high
        for name, successes in coverage.items():
            # The reviewer specifies a 1-in-100 false-failure bar for coverage.
            # Inverting that secondary test gives a 99% coverage interval.
            # Across four conditions the union bound is at most 4% false failures.
            interval = wilson(successes, count, confidence=0.99).interval
            self.assertLessEqual(interval[0], 0.95, (name, successes))
            self.assertGreaterEqual(interval[1], 0.95, (name, successes))
        print("SYNTHETIC Wilson coverage / 80 seeds:", coverage)


if __name__ == "__main__":
    unittest.main()
