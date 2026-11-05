"""Whole-turn admission and deadman tests; native computation is entirely fake.

No model mirrors, SHADE caches, measurement bundles or network are accessed.
"""
from dataclasses import replace
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import signal
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.budget import DeadmanExpired, EpisodeDeadman
from joulewise.align.apple.campaign import _counterbalanced, generate_campaign
from joulewise.align.apple.diagnostics import end_state
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.pilot_analysis import episode_ineligibility_reasons
from joulewise.align.apple.workload import EpisodeSpec, read_episode_bundle
from joulewise.align.interfaces import ChatMessage
from joulewise.clock import FakeClock, SystemClock
from joulewise.schemas import BenchmarkConfig, RuntimeBackend
from scripts.align_pilot_session import episode_summary
from tests.align.test_apple_campaign import base_config, episode_spec
from tests.align.test_apple_endpoint import ReviewTask, ReviewTokenizer, run_native_review
from tests.align.test_pilot3_cache import CacheAPI

ROOT = Path(__file__).resolve().parents[2]


class ScaledClock(FakeClock):
    def __init__(self, scale):
        super().__init__()
        self.scale = scale
        self.native = False

    def sleep(self, seconds):
        super().sleep(seconds * (self.scale if self.native else 1))


@contextmanager
def scale_work(clock):
    """Change native/tool speed while keeping controller/sampler cadence fixed."""
    def wrap(fn):
        def call(*args, **kwargs):
            clock.native = True
            try:
                return fn(*args, **kwargs)
            finally:
                clock.native = False
        return call
    with patch.object(MlxRuntimeAdapter, '_generate', wrap(MlxRuntimeAdapter._generate)), patch.object(
        ReviewTask, 'call_tool', wrap(ReviewTask.call_tool)
    ):
        yield


def run(root, *, budget=181, deadman=1086, clock=None, **updates):
    clock = clock or FakeClock()
    with scale_work(clock):
        return run_native_review(root, 'think', clock, spec_updates={
            'max_episode_decode_tokens': budget, 'deadman_s': deadman, **updates,
        })


def read(path):
    return json.loads(path.read_text())


class SpecTests(unittest.TestCase):
    def test_new_config_fields_round_trip_and_distinguish_counterbalanced_cells(self):
        base = replace(episode_spec(hidden=False), max_episode_decode_tokens=8192, deadman_s=1086)
        self.assertEqual(EpisodeSpec.from_text(base.to_text()), base)
        other = replace(base, condition='sabotage', max_episode_decode_tokens=9216)
        _, flags = _counterbalanced((base, other))
        self.assertIn('unmatched_condition_cells_retained', flags)
        _, flags = _counterbalanced((base, replace(other, max_episode_decode_tokens=8192, deadman_s=1087)))
        self.assertIn('unmatched_condition_cells_retained', flags)
        with tempfile.TemporaryDirectory() as d:
            paths = generate_campaign(base_config(), (base,), Path(d), model_tag='synthetic-new-cell')
            config = BenchmarkConfig.from_mapping(read(paths[0]))
            self.assertEqual(EpisodeSpec.from_text(config.workload_profile.prompt_text), base)

    def test_invalid_limits_and_mixed_wall_guard_are_rejected(self):
        spec = episode_spec(hidden=False)
        for value in (0, -1, True, 1.5, '8192', 40961):
            with self.subTest(budget=value), self.assertRaises(ValueError):
                EpisodeSpec.from_text(replace(spec, max_episode_decode_tokens=value).to_text())
        for value in (0, -1, True, '1086', float('inf'), float('nan')):
            with self.subTest(deadman=value), self.assertRaises(ValueError):
                EpisodeSpec.from_text(replace(spec, deadman_s=value).to_text())
        for update in ({'max_episode_decode_tokens': 8192}, {'deadman_s': 1086}):
            with self.subTest(update=update), self.assertRaisesRegex(ValueError, 'combined'):
                EpisodeSpec.from_text(replace(spec, max_episode_seconds=120, **update).to_text())
        with self.assertRaisesRegex(ValueError, 'context cap'):
            EpisodeSpec.from_text(replace(spec, max_episode_decode_tokens=8192, max_context_tokens=4096).to_text())


class AdmissionTests(unittest.TestCase):
    def test_endpoint_error_after_text_is_failed_even_when_budget_exhausts(self):
        with tempfile.TemporaryDirectory() as d:
            for budget, deadman in ((None, None), (100, 1086)):
                with self.subTest(budget=budget), patch(
                    'joulewise.align.apple.endpoint.reasoning_tokens_from_ids',
                    side_effect=RuntimeError('synthetic accounting fault after text'),
                ):
                    bundle, status, _ = run(Path(d) / str(budget), budget=budget, deadman=deadman)
                    self.assertEqual(status.status.value, 'failed', status)
                    ep = read_episode_bundle(bundle)
                    self.assertTrue(ep.turns[0].tool_calls)
                    self.assertTrue(any(f.startswith('endpoint_error:') for f in ep.flags))
                    if budget is not None:
                        self.assertIn('episode.decode_budget:1', ep.flags)
                        self.assertTrue(ep.hardware['token_budget']['stop_reason'].startswith('endpoint_error:'))
                        failure = read(bundle / 'outputs/align_failure.json')
                        self.assertEqual(failure['episode_outcome']['stop_condition'], 'endpoint_error')
                    self.assertEqual(end_state(ep), 'runner.error')
                    summary = episode_summary(bundle)
                    self.assertEqual(summary['end_state'], 'runner.error')
                    for fault in ('episode_error:RuntimeError:synthetic', 'endpoint_error:RuntimeError:synthetic',
                                  'runner.error:synthetic'):
                        faulted = replace(ep, flags=('episode.decode_budget:1', fault))
                        self.assertEqual(end_state(faulted), 'runner.error')
                        self.assertEqual(end_state(replace(faulted, flags=(*faulted.flags, 'episode.deadman:1'))),
                                         'episode.deadman:1')

    def test_exact_threshold_and_overshoot_keep_the_full_admitted_turn(self):
        with tempfile.TemporaryDirectory() as d:
            for budget, counts, reason in ((180, [180], 'episode.decode_budget:1'),
                                           (181, [180, 260], 'episode.decode_budget:2')):
                with self.subTest(budget=budget):
                    bundle, status, projection = run(Path(d) / str(budget), budget=budget)
                    self.assertEqual(status.status.value, 'succeeded', status)
                    ep = read_episode_bundle(bundle)
                    self.assertEqual([t.decode_tokens for t in ep.turns], counts)
                    self.assertEqual(end_state(ep), reason)
                    record = ep.hardware['token_budget']
                    self.assertEqual(record['decode_tokens_used'], sum(counts))
                    self.assertEqual(record['prefill_tokens_used'], sum(t.prefill_tokens for t in ep.turns))
                    self.assertEqual(record['max_episode_decode_tokens'], budget)
                    self.assertEqual(record['max_tokens_per_turn'], 300)
                    self.assertEqual(record['effective_context_cap'], 40960)
                    if budget == 181:
                        self.assertEqual(sum(t.hidden_tokens for t in ep.turns), 70)
                    self.assertEqual(record['stop_reason'], reason)
                    self.assertFalse(record['incomplete'])
                    self.assertTrue(all(t.tool_calls for t in ep.turns))
                    metadata = read(bundle / 'metadata.json')
                    self.assertEqual(metadata['workload_provenance']['episode_outcome']['token_budget'], record)
                    self.assertEqual(metadata['adapters']['runtime']['align_episode']['token_budget'], record)
                    for key in ('sampler', 'output_policy'):
                        actual = metadata['workload_provenance'][key]
                        if key == 'output_policy':
                            actual = {k: v for k, v in actual.items() if k != 'emitted_tokens'}
                        self.assertEqual(actual, projection['workload_provenance'][key])
                    summary = episode_summary(bundle)
                    self.assertEqual(summary['end_state'], reason)
                    self.assertEqual(summary['token_budget'], record)
                    self.assertEqual(summary['configuration']['max_episode_decode_tokens'], budget)
                    self.assertEqual(summary['configuration']['max_tokens'], 300)
                    self.assertNotIn(reason, episode_ineligibility_reasons({'summary': summary}))

    def test_machine_speed_does_not_change_admitted_work(self):
        with tempfile.TemporaryDirectory() as d:
            identities = []
            durations = []
            for scale in (.25, 20):
                bundle, status, _ = run(Path(d) / str(scale), clock=ScaledClock(scale))
                self.assertEqual(status.status.value, 'succeeded', status)
                ep = read_episode_bundle(bundle)
                durations.append((ep.end_ns - ep.start_ns) / 1e9)
                rows = [json.loads(line) for line in (bundle / 'outputs/align_turns.jsonl').read_text().splitlines()]
                identities.append(([t.decode_tokens for t in ep.turns],
                                   [row['generation']['output_token_ids'] for row in rows], end_state(ep)))
            self.assertEqual(*identities)
            self.assertLess(durations[0], 120)
            self.assertGreater(durations[1], 120)

    def test_context_guard_still_reserves_the_full_turn_cap(self):
        with tempfile.TemporaryDirectory() as d:
            bundle, status, _ = run(Path(d), budget=1, max_context_tokens=1700)
            ep = read_episode_bundle(bundle)
            self.assertEqual(status.status.value, 'succeeded', status)
            self.assertEqual(ep.turns, ())
            self.assertIn('episode.context_limit:0', ep.flags)
            self.assertEqual(ep.hardware['token_budget']['decode_tokens_used'], 0)

    def test_normal_return_and_turn_cap_are_not_relabelled_as_episode_budget(self):
        with tempfile.TemporaryDirectory() as d:
            for scenario, updates, counts in (('think', {}, [180, 260, 140, 90]),
                                               ('truncate', {'max_turns': 2}, [180, 300])):
                bundle, status, _ = run_native_review(Path(d) / scenario, scenario, FakeClock(), spec_updates={
                    'max_episode_decode_tokens': 8192, 'deadman_s': 1086, **updates})
                self.assertEqual(status.status.value, 'succeeded', status)
                ep = read_episode_bundle(bundle)
                self.assertEqual([t.decode_tokens for t in ep.turns], counts)
                self.assertFalse(any(f.startswith('episode.decode_budget:') for f in ep.flags))
                if scenario == 'truncate':
                    self.assertIn('turn_token_budget_reached:1', ep.flags)


class DeadmanTests(unittest.TestCase):
    def test_boundary_expiry_uses_monotonic_time_at_equality(self):
        clock = FakeClock()
        deadman = EpisodeDeadman(clock, clock.stamp(), 5)
        clock.sleep(5)
        self.assertTrue(deadman.expired())
        with self.assertRaises(DeadmanExpired), deadman.guard():
            self.fail('expired work was admitted')

    def test_mid_decode_keeps_partial_evidence_and_never_executes_tools(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            full, _, _ = run(root / 'full')
            ep = read_episode_bundle(full)
            deadline = (ep.turns[0].first_token_ns - ep.start_ns) / 1e9 + .05
            bundle, status, _ = run(root / 'deadman', deadman=deadline)
            self.assertEqual(status.status.value, 'failed', status)
            ep = read_episode_bundle(bundle)
            self.assertEqual(end_state(ep), 'episode.deadman:0')
            self.assertEqual(len(ep.turns), 1)
            self.assertGreater(ep.turns[0].decode_tokens, 0)
            self.assertLess(ep.turns[0].decode_tokens, 180)
            self.assertEqual(ep.turns[0].tool_calls, ())
            self.assertIsNone(ep.main_task_score)
            record = ep.hardware['token_budget']
            self.assertTrue(record['incomplete'])
            self.assertEqual(record['stop_reason'], 'episode.deadman:0')
            self.assertEqual(record['decode_tokens_used'], ep.turns[0].decode_tokens)
            self.assertIn('episode.deadman', status.failure_message)
            self.assertEqual(read(bundle / 'outputs/align_failure.json')['episode_outcome']['token_budget'], record)
            self.assertTrue((bundle / 'outputs/align_runtime_events.jsonl').is_file())
            summary = episode_summary(bundle)
            self.assertEqual(summary['end_state'], 'episode.deadman:0')
            self.assertIn('episode.deadman:0', episode_ineligibility_reasons({'summary': summary}))

    def test_budget_and_interrupted_decode_with_the_episode_prefix_cache(self):
        with tempfile.TemporaryDirectory() as d, patch(
            'joulewise.align.apple.prompt_cache.native_cache_api', return_value=CacheAPI()
        ):
            root = Path(d)
            full, status, _ = run(root / 'full', prompt_cache='episode_prefix')
            self.assertEqual(status.status.value, 'succeeded', status)
            ep = read_episode_bundle(full)
            self.assertEqual([t.decode_tokens for t in ep.turns], [180, 260])
            self.assertGreater(ep.turns[1].context_tokens, 0)
            self.assertEqual(episode_summary(full)['accounting_check']['status'], 'pass')
            deadline = (ep.turns[0].first_token_ns - ep.start_ns) / 1e9 + .05
            partial, status, _ = run(root / 'partial', prompt_cache='episode_prefix', deadman=deadline)
            self.assertEqual(status.status.value, 'failed', status)
            ep = read_episode_bundle(partial)
            self.assertEqual(len(ep.turns), 1)
            self.assertLess(ep.turns[0].decode_tokens, 180)
            self.assertFalse(any(f.startswith('endpoint_error:') for f in ep.flags), ep.flags)
            self.assertEqual(episode_summary(partial)['end_state'], 'episode.deadman:0')

    def test_zero_token_deadman_is_retained_as_deadman_not_no_model_output(self):
        clock = FakeClock()
        def slow_render(*args, **kwargs):
            clock.sleep(1)
            return 100
        with tempfile.TemporaryDirectory() as d, patch.object(MlxEndpoint, 'rendered_prompt_length', slow_render):
            bundle, status, _ = run(Path(d), clock=clock, deadman=.5, max_context_tokens=40960)
            ep = read_episode_bundle(bundle)
            self.assertEqual(status.status.value, 'failed', status)
            self.assertEqual(sum(t.decode_tokens for t in ep.turns), 0)
            self.assertEqual(end_state(ep), 'episode.deadman:0')
            self.assertNotIn('no_model_call_returned_tokens', status.failure_message)

    def test_deadman_during_tool_stops_before_next_turn(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            full, _, _ = run(root / 'full')
            ep = read_episode_bundle(full)
            deadline = (ep.turns[0].end_ns - ep.start_ns) / 1e9 + 1
            bundle, status, _ = run(root / 'tool', deadman=deadline)
            ep = read_episode_bundle(bundle)
            self.assertEqual(status.status.value, 'failed', status)
            self.assertEqual([t.decode_tokens for t in ep.turns], [180])
            self.assertEqual(end_state(ep), 'episode.deadman:0')

    def test_stalled_stream_is_interrupted_and_signal_state_is_restored(self):
        clock = SystemClock()
        config = base_config()
        config = replace(config, hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
        runtime = MlxRuntimeAdapter(clock)
        runtime._model, runtime._tokenizer = object(), ReviewTokenizer()
        closed = []
        def stream_generate(*args, **kwargs):
            try:
                yield SimpleNamespace(token=42, text='partial', finish_reason=None)
                clock.sleep(10)  # The timer must interrupt a no-yield hang.
                yield SimpleNamespace(token=43, text='unreachable', finish_reason='stop')
            finally:
                closed.append(True)
        native = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
        runtime._mlx_lm = native
        handler, timer = signal.getsignal(signal.SIGALRM), signal.getitimer(signal.ITIMER_REAL)
        endpoint = MlxEndpoint(runtime, config, clock, episode_domain='fake-stream',
                               deadman=EpisodeDeadman(clock, clock.stamp(), .25), enforce_turn_cap=True)
        result = endpoint.chat([ChatMessage('user', 'fake')], max_tokens=300, temperature=0, seed=None)
        self.assertEqual(result.completion_tokens, 1)
        self.assertEqual(result.raw_usage['raw_text'], 'partial')
        self.assertIn('episode.deadman:0', endpoint.flags)
        self.assertFalse(any(f.startswith('endpoint_error:') for f in endpoint.flags), endpoint.flags)
        self.assertEqual(closed, [True])
        self.assertIs(runtime._mlx_lm, native)
        self.assertEqual(signal.getsignal(signal.SIGALRM), handler)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), timer)

    def test_opt_in_stream_cap_stops_an_endpoint_ignoring_max_tokens(self):
        clock = FakeClock()
        config = base_config()
        config = replace(config, hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
        runtime = MlxRuntimeAdapter(clock)
        runtime._model, runtime._tokenizer = object(), ReviewTokenizer()
        emitted, closed = [], []
        def stream_generate(*args, **kwargs):
            try:
                for index in range(100):
                    emitted.append(index)
                    clock.sleep(.01)
                    yield SimpleNamespace(token=index + 1, text='x', finish_reason=None)
            finally:
                closed.append(True)
        runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
        endpoint = MlxEndpoint(runtime, config, clock, episode_domain='fake-stream', enforce_turn_cap=True)
        result = endpoint.chat([ChatMessage('user', 'fake')], max_tokens=3, temperature=0, seed=None)
        self.assertEqual(result.completion_tokens, 3)
        self.assertEqual(emitted, [0, 1, 2])
        self.assertEqual(closed, [True])
        self.assertIn('turn_token_budget_reached:0', endpoint.flags)


class AnchorRegressionTests(unittest.TestCase):
    def test_anchor_configs_and_canonical_spec_text_are_byte_identical(self):
        # Frozen from c9a0a3943; config paths are read only inside this clone.
        hashes = (
            '6d2c4ecda2022b25ccb68bc455bf783851f5d77b7b09c89737cdd0a50df4bb58', '6a5c0daaa019e66440e8860ef82163312dea84fd9aaaa28f6fd0f3b6464712a8', '56105368782182d14e5dbd125854de1dff888cad4c1c25d21aa6820fcf2062d2', '5b893b05211f36450bb60c7c01b39ec1721415022c65797d0c2fb3831d1a7bfa',
        )
        plan = read(ROOT / 'configs/campaigns/align_pilot_v3/collection_plan.json')
        for member, expected in zip(plan['members'][:4], hashes, strict=True):
            raw = (ROOT / member['config_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected)
            text = json.loads(raw)['workload_profile']['prompt_text']
            spec = EpisodeSpec.from_text(text)
            self.assertEqual(spec.to_text(), text)
            self.assertEqual(spec.max_episode_seconds, 120)
            self.assertIsNone(spec.max_episode_decode_tokens)
            self.assertIsNone(spec.deadman_s)

    def test_120_second_guard_checks_only_at_turn_boundaries(self):
        with tempfile.TemporaryDirectory() as d:
            clock = ScaledClock(20)
            with scale_work(clock):
                bundle, status, _ = run_native_review(Path(d), 'think', clock,
                    spec_updates={'max_episode_seconds': 120})
            self.assertEqual(status.status.value, 'succeeded', status)
            ep = read_episode_bundle(bundle)
            self.assertEqual([t.decode_tokens for t in ep.turns], [180, 260])
            self.assertIn('episode.time_guard:2', ep.flags)
            self.assertEqual(end_state(ep), 'episode.time_guard:2')
            self.assertGreater((ep.turns[-1].end_ns - ep.start_ns) / 1e9, 120)
            self.assertNotIn('token_budget', ep.hardware)
            summary = episode_summary(bundle)
            self.assertNotIn('token_budget', summary)
            self.assertNotIn('deadman_s', summary['configuration'])
            # Independently derived by executing the c9a0a3943 endpoint,
            # workload, diagnostics and pilot_analysis sources in this fake
            # world. Only the temporary model-root string is normalized.
            expected = {
                'align_turns.jsonl': 'cd44770b7ca1d5f3039d874ca1167458ff87cc6878a1512cbc91f548998c4659',
                'align_transcript.jsonl': '334ee272e1d8d36726be2bc3438f87c9ebee8ad6f6314fc571394ad2be38228a',
                'align_episode.json': 'ff51796b687ba71cf8ff830e979008bd7fb9e2dc441af2b1528a4c00419b1c90',
                'desk': '1015dc3765f02eeec485690efdbd527496b6d90b98f19c693b58148abb6eb459',
                'policy': '7e3e974cdb1c888a745ad645b7fde9ff694384aea11e90017940d8e7e678f797',
            }
            payloads = {name: (bundle / 'outputs' / name).read_text()
                        for name in expected if name.startswith('align_')}
            payloads['desk'] = json.dumps(summary, sort_keys=True)
            provenance = read(bundle / 'metadata.json')['workload_provenance']
            payloads['policy'] = json.dumps({k: provenance[k] for k in
                ('sampler', 'output_policy', 'episode_outcome')}, sort_keys=True)
            for name, text in payloads.items():
                normalized = text.replace(d, '<synthetic-root>')
                self.assertEqual(hashlib.sha256(normalized.encode()).hexdigest(), expected[name], name)


if __name__ == '__main__':
    unittest.main()
