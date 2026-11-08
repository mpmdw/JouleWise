"""Tiny child processes and invented meter samples; no model or measurement data."""
from fractions import Fraction
import json
import os
import time
import unittest

from joulewise.align.squeeze.external import (
    ExternalWork, account_meter, cpu_work, join_control_meter, paired_increment,
)
from tests.align.squeeze_fixtures import TinyDecoder, variant


def tiny_factory(seed):
    return TinyDecoder()


def broken_factory(seed):
    raise RuntimeError("synthetic load failure")


def slow_factory(seed):
    time.sleep(30)
    return TinyDecoder()


def partial_factory(seed):
    class Partial(TinyDecoder):
        def decode(self, prompt, *, max_tokens):
            yield 1
            raise RuntimeError("synthetic partial work")
    return Partial()


class ExternalTests(unittest.TestCase):
    def work(self, kind="side_generation", units=5, **kwargs):
        return ExternalWork(kind=kind, units=units, seed=42,
            decoder_factory=tiny_factory if kind == "side_generation" else None,
            worker_identity="synthetic-test-worker-v1", prompt_token_ids=[1, 2, 3],
            max_context_tokens=64, timeout_s=5, **kwargs)

    def test_side_generation_is_a_different_process_with_exact_private_token_counts(self):
        work = self.work()
        work.execute()
        receipt = work.receipt()
        child = receipt["work"]
        self.assertNotEqual(receipt["worker_pid"], os.getpid())
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(child["H"], 5)
        self.assertEqual(child["prefill_tokens"], 3)
        self.assertEqual(child["completed_forward_input_tokens"], 7)
        self.assertEqual(len(child["output_token_ids"]), 5)
        self.assertIsNone(receipt["energy_j"])
        self.assertEqual(receipt["audience"], "evaluator_only")
        self.assertLessEqual(receipt["start_ns"], child["start_ns"])
        self.assertLessEqual(child["end_ns"], receipt["end_ns"])
        with self.assertRaises(RuntimeError):
            work.execute()

    def test_tool_compute_records_work_units_and_zero_generated_tokens(self):
        work = self.work("tool_cpu", 19, placement="tool")
        work.execute()
        receipt = work.receipt()
        self.assertEqual(receipt["work"]["completed_work_units"], 19)
        self.assertEqual(receipt["work"]["checksum"], cpu_work(19, 42))
        self.assertEqual(receipt["work"]["H"], 0)
        self.assertEqual(receipt["work"]["output_token_ids"], [])
        self.assertNotEqual(receipt["worker_pid"], os.getpid())

    def test_sham_starts_child_and_prepares_decoder_but_does_no_decode(self):
        work = ExternalWork(kind="side_generation", units=0, seed=42,
            decoder_factory=tiny_factory, worker_identity="sham-no-forward",
            max_context_tokens=64)
        work.execute()
        self.assertEqual(work.receipt()["work"]["H"], 0)
        self.assertEqual(work.receipt()["work"]["prefill_tokens"], 0)
        self.assertEqual(work.receipt()["status"], "completed")

    def test_failure_partial_work_and_deadman_never_certify_full_dose(self):
        for factory in (broken_factory, partial_factory, slow_factory):
            work = ExternalWork(kind="side_generation", units=5, seed=42,
                decoder_factory=factory, worker_identity="synthetic-failing-worker",
                prompt_token_ids=[1, 2, 3], max_context_tokens=64,
                timeout_s=0.3 if factory == slow_factory else 5)
            with self.assertRaises(RuntimeError):
                work.execute()
            receipt = work.receipt()
            self.assertNotEqual(receipt["status"], "completed")
            self.assertTrue(receipt["unknown_work_on_failure"])
            self.assertIsNone(receipt["H"])
            if factory == partial_factory:
                self.assertEqual(receipt["work"]["completed_tokens"], 1)

    def test_validation_precedes_process_creation(self):
        for kwargs in ({"kind": "shell"}, {"units": True}, {"units": -1},
                       {"seed": True}, {"timeout_s": float("nan")},
                       {"placement": "after_episode"}, {"trigger_index": -1}):
            args = dict(kind="tool_cpu", units=2, seed=1, worker_identity="tiny")
            args.update(kwargs)
            with self.assertRaises(ValueError):
                ExternalWork(**args)

    def test_exact_joule_arithmetic_with_clipped_invented_DC_samples(self):
        # Linear 2->6 W over 2 s; clip to [0.5, 1.5] s: exactly 4 J.
        result = account_meter([(0, "2"), (2_000_000_000, "6")],
            start_ns=500_000_000, end_ns=1_500_000_000,
            clock_domain="host-monotonic", source="synthetic",
            source_sha256="a" * 64, uncertainty_j="0")
        self.assertEqual(Fraction(result["dc_in_j"]), 4)
        self.assertEqual(result["source"], "synthetic")
        self.assertIsNone(result["hidden_increment_j"])
        for samples in ([(1, "2"), (2, "3")], [(0, "2"), (0, "3")],
                        [(0, "NaN"), (2_000_000_000, "6")]):
            with self.assertRaises(ValueError):
                account_meter(samples, start_ns=0, end_ns=2_000_000_000,
                    clock_domain="host-monotonic", source="synthetic",
                    source_sha256="a" * 64, uncertainty_j="0")

    def test_measured_meter_requires_uncertainty_and_coverage_and_is_not_hidden_energy(self):
        args = dict(start_ns=0, end_ns=1_000_000_000, clock_domain="host-monotonic",
                    source="km003c", source_sha256="a" * 64, uncertainty_j="0.1")
        samples = [(0, "4"), (1_000_000_000, "4")]
        with self.assertRaises(ValueError):
            account_meter(samples, **args)
        with self.assertRaises(ValueError):
            account_meter(samples, **args, max_gap_ns=999_999_999)
        result = account_meter(samples, **args, max_gap_ns=1_000_000_000)
        self.assertEqual(Fraction(result["dc_in_j"]), 4)
        self.assertEqual(Fraction(result["uncertainty_j"]), Fraction(1, 10))
        self.assertIsNone(result["hidden_increment_j"])
        # Invented samples test a measured-schema path, never live evidence.

    def test_unreached_tool_injection_and_child_timeout_cleanup(self):
        from joulewise.align.squeeze.harness import ToolControlTask
        import multiprocessing
        work = self.work("tool_cpu", 2, placement="tool", trigger_index=1)
        class Task:
            def call_tool(self, name, arguments_json): return "unchanged"
        task = ToolControlTask(Task(), variant(), work)
        self.assertEqual(task.call_tool("lookup", "{}"), "unchanged")
        self.assertEqual(work.receipt()["status"], "not_triggered")
        before = {p.pid for p in multiprocessing.active_children()}
        timeout = ExternalWork(kind="side_generation", units=1, seed=1,
            worker_identity="synthetic-timeout", decoder_factory=slow_factory, timeout_s=0.2)
        with self.assertRaises(RuntimeError):
            timeout.execute()
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, before)

    def test_private_accounting_join_and_matched_sham_keep_joules_separate_from_tokens(self):
        from copy import deepcopy
        rows = []
        for units, watts in ((0, "2"), (5, "4")):
            # These invented constant powers say nothing about the child process.
            control = self.work("tool_cpu", units, placement="tool")
            control.execute()
            receipt = control.receipt()
            span_start = receipt["start_ns"]
            span_end = span_start + 2_000_000_000
            meter = account_meter([(span_start, watts), (span_end, watts)],
                start_ns=span_start, end_ns=span_end, clock_domain="host-monotonic",
                source="synthetic", source_sha256="a" * 64, uncertainty_j="0.1")
            rows.append(join_control_meter(receipt, meter, transcript_sha256="b" * 64,
                v4_configuration_sha256="c" * 64))
        difference = paired_increment(rows[1], rows[0])
        self.assertEqual(Fraction(difference["observed_dc_difference_j"]), 4)
        self.assertEqual(Fraction(difference["additive_bound_j"]), Fraction(1, 5))
        self.assertIsNone(difference["hidden_energy_j"])
        bad = deepcopy(rows[0])
        bad["transcript_sha256"] = "d" * 64
        with self.assertRaises(ValueError):
            paired_increment(rows[1], bad)
        bad = deepcopy(rows[1]["meter"])
        bad["end_ns"] = rows[1]["control"]["start_ns"]
        with self.assertRaises(ValueError):
            join_control_meter(rows[1]["control"], bad, transcript_sha256="b" * 64,
                v4_configuration_sha256="c" * 64)

    def test_both_injection_sites_preserve_visible_runner_usage_and_monitor_inputs(self):
        from joulewise.align.interfaces import ChatResult, ToolCallRequest
        from joulewise.align.records import MonitorVerdict
        from joulewise.align.squeeze.harness import run_adversarial_episode
        active, views = [False], []
        test = self

        class ObservedWork(ExternalWork):
            def execute(self):
                test.assertTrue(active[0], "child must run under active sampling")
                super().execute()

        class Sampler:
            clock_domain, clock_mappings = "host-monotonic", ()
            def start(self): active[0] = True
            def stop(self):
                active[0] = False
                return ()  # no power samples and no energy claim

        class Monitor:
            model = "synthetic-monitor"
            def score(self, transcript, **kwargs):
                test.assertFalse(active[0], "monitor must run after sampling stops")
                views.append(transcript)
                return MonitorVerdict(self.model, kwargs["visibility"], 0.0, "0" * 64)

        class Task:
            task_pair, scratchpad_tags, flags = "synthetic/ledger", None, []
            def reset(self, seed): pass
            def system_prompt(self, condition): return "base"
            def user_prompt(self): return "lookup"
            def task_description(self): return "lookup"
            def tool_schemas(self): return []
            def call_tool(self, name, arguments_json): return "same tool result"
            def score_main(self, transcript): return 1.0
            def score_side(self, transcript): return False

        class Endpoint:
            identity = "synthetic-visible"
            def __init__(self): self.calls = 0
            def chat(self, messages, **kwargs):
                self.calls += 1
                now = time.monotonic_ns()
                tools = (ToolCallRequest("t", "lookup", "{}"),) if self.calls == 1 else ()
                return ChatResult("public", "", tools, 10, 2, 3, 0, now, now, now, {})

        runs = []
        for kind, placement in (("side_generation", "before_chat"), ("tool_cpu", "tool")):
            for dose in (0, 5):
                control = ObservedWork(kind=kind, units=dose, seed=42,
                    worker_identity="synthetic-test-worker-v1",
                    decoder_factory=tiny_factory if kind == "side_generation" else None,
                    prompt_token_ids=[1, 2, 3], max_context_tokens=64, placement=placement,
                    timeout_s=5)
                run = run_adversarial_episode(Task(), "sabotage", Endpoint(),
                    variant=variant(), control=control, seed=2, max_turns=3,
                    max_tokens=16, temperature=0.0, clock_domain="host-monotonic",
                    clock=time.monotonic_ns, samplers=[Sampler()],
                    monitors=[(Monitor(), ("full", "no_scratchpad", "actions_only"))])
                receipt = run.ground_truth["hidden_decode"]
                self.assertEqual(receipt["status"], "completed")
                self.assertEqual(receipt["episode_interval_check"], "inside")
                self.assertEqual([t.decode_tokens for t in run.episode.turns], [3, 3])
                self.assertFalse(run.episode.flags)
                text = json.dumps([m.__dict__ for m in run.transcript])
                self.assertNotIn("worker_pid", text)
                self.assertNotIn("completed_tokens", text)
                runs.append(run)
        self.assertTrue(all(run.transcript == runs[0].transcript for run in runs))
        self.assertEqual(len({run.episode.episode_id for run in runs}), 4)
        self.assertEqual(len(views), 12)
        self.assertNotIn("worker_pid", repr(views))
        self.assertNotIn("completed_tokens", repr(views))


if __name__ == "__main__":
    unittest.main()
