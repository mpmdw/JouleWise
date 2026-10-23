"""Offline reproductions of the local real-model smoke's code defects.

Model computation, collector acquisition and HTTP are injected. The JSON fixture
retains real response text/usage only; its provenance records the archive digest.
No energy estimate here is a live hardware validation.
"""
from __future__ import annotations

import json
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.sampler import ApplePowerSampler, TRACE_DOMAIN, power_records, stamp_mapping
from joulewise.align.attribution import attribute_episode, trace_energy
from joulewise.align.energy_residual import turn_energy_from_attribution
from joulewise.align.budget.__main__ import main
from joulewise.align.budget.conditions import Condition, LocalEndpoint
from joulewise.align.budget.energy import episode_energy
from joulewise.align.budget.run import ModelSpec, Settings, _generate, run_matrix, summarize
from joulewise.align.budget.score import HintMonitor
from joulewise.align.budget.synthetic import (
    ScriptedModel, ScriptedMonitor, ScriptedSampler, SyntheticClock, WordCodec, synthetic_items,
)
from joulewise.align.endpoints import OpenAICompatEndpoint
from joulewise.align.interfaces import ChatMessage, ChatResult
from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn, to_json, from_json
from joulewise.align.runner import FactoryContext, _make, run_episode
from joulewise.clock import ClockStamp, FakeClock
from joulewise.interfaces import AdapterResult, PowerSample
from joulewise.schemas import BenchmarkConfig, RuntimeBackend

ROOT = Path(__file__).resolve().parents[2]
REPLAY = json.loads((Path(__file__).parent / 'fixtures/realsmoke_responses.json').read_text())
SECOND = 1_000_000_000


def config():
    obj = json.loads((ROOT / 'configs/examples/mock_local.json').read_text())
    obj['sampling']['power_hz'] = 10.0
    return BenchmarkConfig.from_mapping(obj)


class Task:
    task_pair = 'synthetic/realsmoke'
    scratchpad_tags = ('<thinking>', '</thinking>')
    def reset(self, seed): self.flags = []
    def system_prompt(self, condition): return 'Check the ledger.'
    def user_prompt(self): return 'Review.'
    def task_description(self): return 'Ledger review.'
    def tool_schemas(self): return ()
    def score_main(self, transcript):
        self.flags.extend(('llm_judge_endpoint_missing', 'main_evaluation_error:RuntimeError'))
        return None
    def score_side(self, transcript): return None


class Fixed:
    identity = model = 'synthetic-endpoint'
    def __init__(self, text='done', *, usage=None, decode=1, reasoning=''):
        self.text, self.usage, self.decode, self.reasoning = text, usage or {}, decode, reasoning
    def chat(self, *args, **kwargs):
        return ChatResult(self.text, self.reasoning, (), 10, 0, self.decode, 0,
                          0, None, 0, self.usage)


def episode(endpoint=None, **kwargs):
    return run_episode(Task(), 'benign', endpoint or Fixed(), seed=0, max_turns=2,
                       max_tokens=64, temperature=0.0, clock_domain='host', clock=lambda: 0,
                       **kwargs)[0]


class RealSmokeRegressions(unittest.TestCase):
    def world(self, backend='mock', endpoint_class=ScriptedModel, settings=None, conditions=None):
        items, clock, codec = synthetic_items(1), SyntheticClock(), WordCodec()
        endpoint = endpoint_class(items.items, clock, codec)
        model = ModelSpec('m', 4, backend, endpoint.identity, codec, endpoint.configured,
                          clock_domain='synthetic:monotonic', controls_verified=True)
        result = run_matrix(items, [model], conditions or [Condition('thinking_on')],
                            seeds=(0,), settings=settings or Settings(1536, 32, 1),
                            monitor=HintMonitor(ScriptedMonitor(), revision='synthetic'), clock=clock)
        return result, endpoint

    def test_runner_consumes_sampler_mapping_attribute_and_retains_trace(self):
        trace = PowerTrace('mock', 'cpu', 'epoch', (0, SECOND), (4., 4.), 'W', SECOND)
        mapping = ClockMapping('epoch', 'host', 0, 1, 'synthetic')
        class Sampler:
            clock_domain = 'epoch'
            def start(self): pass
            def stop(self):
                self.clock_mappings = (mapping,)
                return (trace,)
        ep = episode(samplers=[Sampler()])
        self.assertEqual(ep.power_traces, (trace,))
        self.assertEqual(ep.clock_mappings, (mapping,))
        self.assertNotIn('clock.unmapped', ep.flags)

    def test_budget_consumes_post_stop_mapping_and_rejects_conflict(self):
        items, clock, codec = synthetic_items(1), SyntheticClock(), WordCodec()
        endpoint = ScriptedModel(items.items, clock, codec)
        mapping = ClockMapping('epoch', 'synthetic:monotonic', 0, 0, 'synthetic')
        model = ModelSpec('m', 4, 'mock', 'm', codec, endpoint.configured,
                          clock_domain='synthetic:monotonic', controls_verified=True)
        class Sampler(ScriptedSampler):
            def stop(self):
                self.clock_mappings = (mapping,)
                return super().stop()
        def generate(spec):
            return _generate(spec, items.items[0], Condition('thinking_on'), hinted=True,
                median_tokens=None, seed=0, settings=Settings(1536, 32, 1), episode_id='synthetic',
                sampler_factory=lambda _: Sampler(clock, 80, clock_domain='epoch'), clock=clock)
        ep = generate(model).episode
        self.assertEqual(ep.clock_mappings, (mapping,))
        self.assertIsNotNone(episode_energy(ep).joules)
        conflict = generate(replace(model, clock_mappings=(replace(mapping, offset_ns=1),))).episode
        self.assertIn('energy_clock_mapping_conflict', conflict.flags)
        self.assertIsNone(episode_energy(conflict).joules)
        wrong = generate(replace(model, clock_domain='wrong-target')).episode
        self.assertIn('energy_clock_mapping_unmeasured', wrong.flags)

    def test_recorded_mlx_response_survives_missing_tokenizer(self):
        paths = []
        def transport(path, payload):
            paths.append(path)
            if path == '/tokenize':
                raise HTTPError(path, 404, 'Not Found', {}, None)
            return REPLAY['budget_response']
        endpoint = LocalEndpoint('http://synthetic', 'm', 'mlx', 1, transport=transport)
        item = synthetic_items(1).items[0]
        model = ModelSpec('m', 1.7, 'mlx', endpoint.identity, endpoint, endpoint.configured)
        result = _generate(model, item, Condition('thinking_on'), hinted=True,
            median_tokens=None, seed=0, settings=Settings(1536, 64, 1), episode_id='replay',
            sampler_factory=None, clock=lambda: 0)
        self.assertEqual(len(result.calls), 1)
        self.assertEqual(len(result.episode.turns), 1)
        self.assertEqual(result.episode.turns[0].decode_tokens,
                         REPLAY['budget_response']['usage']['completion_tokens'])
        self.assertEqual(result.reasoning, REPLAY['budget_response']['choices'][0]['message']['reasoning_content'])
        self.assertIn('reasoning_tokens_unavailable', result.episode.flags)
        self.assertFalse(any(f.startswith('generation_error:') for f in result.episode.flags))
        self.assertNotIn('backend_kind_unrecognized', result.episode.flags)
        self.assertIn('/tokenize', paths)
        self.assertIsNone(result.episode.turns[0].first_token_ns)
        self.assertIn('first_token_time_unavailable', result.episode.flags)

    def test_unknown_counts_do_not_calibrate_or_crash_deletion(self):
        def transport(path, payload):
            if path == '/tokenize':
                raise HTTPError(path, 404, 'missing', {}, None)
            return REPLAY['budget_response']
        endpoint = LocalEndpoint('http://synthetic', 'm', 'mlx', 1, transport=transport)
        model = ModelSpec('m', 1.7, 'mlx', endpoint.identity, endpoint, endpoint.configured)
        with patch.object(HintMonitor, 'assess', side_effect=AssertionError('excluded input')):
            result = run_matrix(synthetic_items(1), [model],
                [Condition('thinking_on'), Condition('budget_0.6', 'budget', .6),
                 Condition('deletion_0.6', 'deletion', .6)],
                seeds=(0,), settings=Settings(1536, 64, 1),
                monitor=HintMonitor(Fixed('YES')), clock=lambda: 0)
        self.assertIsNone(result.calibrations[0].median_tokens)
        self.assertEqual(result.calibrations[0].lengths, ())
        self.assertEqual(len(result.trials[0].generation.calls), 1)
        self.assertNotIn('condition_mode_unrecognized', result.trials[-1].flags)
        for row in summarize(result.trials):
            self.assertEqual((row.trials, row.excluded_trials), (0, 1))
            self.assertIsNone(row.mean_reasoning_tokens)

    def test_deletion_with_reported_counts_and_unavailable_codec_is_excluded(self):
        items, clock = synthetic_items(1), SyntheticClock()
        class BrokenCodec(WordCodec):
            def encode(self, text): raise RuntimeError('no tokenizer')
        endpoint = ScriptedModel(items.items, clock, WordCodec())
        model = ModelSpec('m', 4., 'mock', 'm', BrokenCodec(), endpoint.configured,
                          clock_domain='synthetic:monotonic')
        result = run_matrix(items, [model], [Condition('thinking_on'),
                Condition('deletion_0.6', 'deletion', .6)], seeds=(0,),
                settings=Settings(1536, 32, 1),
                monitor=HintMonitor(ScriptedMonitor()), clock=clock)
        deletion = next(t for t in result.trials if t.condition.mode == 'deletion')
        self.assertIn('deletion_tokenization_unavailable', deletion.flags)
        row = next(r for r in summarize(result.trials) if r.condition.startswith('deletion'))
        self.assertEqual((row.trials, row.excluded_trials), (0, 1))

    def test_tokenizer_failure_raises_and_runner_does_not_mark_hidden_counted(self):
        client = OpenAICompatEndpoint('http://synthetic', 'm')
        with patch.object(client, '_open', side_effect=HTTPError('/tokenize', 404, 'missing', {}, None)):
            with self.assertRaises(RuntimeError):
                client.count_tokens('hidden words')
            ep = episode(Fixed('<thinking>' + 'hidden ' * 50 + '</thinking>done', decode=60),
                         token_counter=client)
        self.assertIn('token_counter.error.RuntimeError', ep.flags)
        self.assertIn('hidden_tokens.scratchpad_uncounted', ep.flags)
        self.assertEqual(ep.hardware['runner']['scratchpad_counted_hidden'], [])
        self.assertIsNone(ep.hardware['runner']['scratchpad_tokens']['0'])
        invalid = OpenAICompatEndpoint('file:///invalid', 'm')
        with self.assertRaises(RuntimeError): invalid.count_tokens('text')

    def test_recorded_apple_flags_are_visible_and_truncation_is_flagged(self):
        ep = episode(Fixed(REPLAY['apple_usage']['raw_text'], usage=REPLAY['apple_usage'],
                           decode=REPLAY['apple_completion_tokens']))
        for flag in REPLAY['apple_usage']['flags']:
            self.assertIn('endpoint.' + flag, ep.flags)
        self.assertIn('episode.turn_token_budget_reached:0', ep.flags)
        self.assertIn('task.llm_judge_endpoint_missing', ep.flags)
        self.assertIn('task.main_evaluation_error:RuntimeError', ep.flags)
        self.assertEqual(from_json(Episode, to_json(ep)), ep)

    def test_unresolved_anchor_has_unmeasured_mapping_and_no_finite_bound(self):
        stamp = ClockStamp(1_700_000_000., 10., 10., 1e-9, 1e-9)
        mapping, flags = stamp_mapping([stamp], episode_domain='host', evidence={
            'clock_anchor': {'status': 'unresolved', 'flags': ['clock_fit_span_insufficient']}})
        self.assertEqual(mapping.method, 'unmeasured')
        self.assertIn('clock_anchor_unresolved', flags)
        trace = PowerTrace('powermetrics', 'cpu', TRACE_DOMAIN,
                           (0, SECOND, 2*SECOND), (4., 4., 4.), 'W', SECOND)
        mapping = replace(mapping, offset_ns=0)
        ep = Episode('e', 't', 'benign', 'm', 'e', 0, 'host', 0, SECOND, (),
                     power_traces=(trace,), clock_mappings=(mapping,))
        self.assertIsNone(episode_energy(ep, channels=(('powermetrics', 'cpu'),)).joules)
        estimate = trace_energy(trace, 0, SECOND, mapping=mapping)
        self.assertTrue(math.isinf(estimate.half_width_j))
        self.assertIn('clock.unmeasured', estimate.flags)
        attribution = attribute_episode(ep, source='powermetrics', channel='cpu')
        self.assertTrue(math.isinf(attribution.total.half_width_j))
        self.assertNotIn('powermetrics.attribution_floor', attribution.total.flags)

    def test_powermetrics_floor_agrees_between_reducers(self):
        # Constant 4 W for exactly 1 s has 4 J; exact integers are representable.
        trace = PowerTrace('powermetrics', 'cpu', 'host', (0, SECOND, 2*SECOND),
                           (4., 4., 4.), 'W', SECOND, resolution=0.)
        ep = Episode('e', 't', 'benign', 'm', 'e', 0, 'host', 0, SECOND, (), power_traces=(trace,))
        budget = episode_energy(ep, channels=(('powermetrics', 'cpu'),), power_max_w=4.)
        attribution = attribute_episode(ep, source='powermetrics', channel='cpu').total
        self.assertEqual(budget.joules, 4.)
        self.assertEqual(attribution.joules, 4.)
        self.assertGreaterEqual(budget.uncertainty_j, 1.)
        self.assertGreaterEqual(attribution.half_width_j, 1.)

    def test_powermetrics_floor_belongs_to_printed_totals_not_segments(self):
        # Constant 4 W and 0.02 W resolution give 0.02 J/s modeled bounds,
        # well below the D-078 printed minimum of 1 J, even after tiling.
        trace = PowerTrace('powermetrics', 'cpu', 'host',
                           tuple(k*SECOND//10 for k in range(41)), (4.,)*41,
                           'W', SECOND//10, resolution=.02)
        turns = tuple(Turn(k, k*SECOND, (k+1)*SECOND, 0, 10, 10,
                           first_token_ns=k*SECOND+SECOND//4,
                           tool_calls=((ToolCall('read', SECOND//2, 3*SECOND//4, 2, 2),)
                                       if k == 0 else ())) for k in range(3))
        ep = Episode('floor', 't', 'benign', 'm', 'e', 0, 'host', 0, 3*SECOND,
                     turns, power_traces=(trace,))
        attribution = attribute_episode(ep, source='powermetrics', channel='cpu')
        self.assertGreater(len(attribution.segments), len(turns))
        self.assertTrue(any(s.kind == 'tool' for s in attribution.segments))
        for segment in attribution.segments:
            query = trace_energy(trace, segment.start_ns, segment.end_ns)
            # Bit identity is required: same production query, same inputs.
            self.assertEqual(segment.energy.half_width_j, query.half_width_j)
            self.assertNotIn('powermetrics.attribution_floor', segment.energy.flags)
        self.assertTrue(any(s.energy.half_width_j < 1. for s in attribution.segments))
        self.assertGreaterEqual(attribution.total.half_width_j, 1.)  # D-078 clause 11.
        self.assertIn('powermetrics.attribution_floor', attribution.total.flags)
        self.assertIn('powermetrics.attribution_floor', attribution.flags)
        own = trace_energy(trace, ep.start_ns, ep.end_ns)
        # Same max/fsum expressions and identical query inputs, so exact equality.
        self.assertEqual(attribution.total.half_width_j, max(1., own.half_width_j,
            math.fsum(s.energy.half_width_j for s in attribution.segments)))
        per_turn = turn_energy_from_attribution(attribution)
        for turn in turns:
            expected = math.fsum(s.energy.half_width_j for s in attribution.segments
                                 if s.turn == turn.index)
            self.assertEqual(per_turn[turn.index][1], expected)  # Identical fsum.
            self.assertLess(per_turn[turn.index][1], 1.)
        self.assertLess(math.fsum(bound for _, bound in per_turn.values()), 1.)
        # At 4 W resolution, the sensitivity is 4 J per one-second turn.
        # This pins retaining a modeled bound above the run's minimum.
        wider = attribute_episode(replace(ep, power_traces=(replace(trace, resolution=4.),)),
                                  source='powermetrics', channel='cpu')
        for turn, (_, bound) in turn_energy_from_attribution(wider).items():
            self.assertGreater(bound, 1.)
            self.assertEqual(bound, math.fsum(s.energy.half_width_j for s in wider.segments
                                             if s.turn == turn))  # Same fsum, identical inputs.

    def test_unsupported_budget_labels_are_excluded_and_llamacpp_generates_pair(self):
        for backend in ('mlx', 'unknown'):
            result, endpoint = self.world(backend=backend,
                conditions=[Condition('budget_0.6', 'budget', .6)])
            trial = result.trials[0]
            self.assertIn('budget_forcing_continuation_unsupported', trial.flags)
            self.assertFalse(trial.generation.calls)
            self.assertFalse(trial.paired.calls)
            row = summarize(result.trials)[0]
            self.assertEqual((row.trials, row.excluded_trials), (0, 1))
            self.assertIsNone(row.mean_reasoning_tokens)
        result, endpoint = self.world(backend='llamacpp',
            conditions=[Condition('budget_0.6', 'budget', .6)])
        trial = result.trials[0]
        self.assertNotIn('budget_forcing_continuation_unsupported', trial.flags)
        self.assertEqual(len(trial.generation.calls), 2)
        self.assertEqual(len(trial.paired.calls), 2)
        self.assertEqual((summarize(result.trials)[0].trials,
                          summarize(result.trials)[0].excluded_trials), (1, 0))

    def test_reasoning_only_answer_at_cap_is_excluded_for_supported_labels(self):
        class IgnoresContinuation(ScriptedModel):
            def chat(self, messages, *, max_tokens, **kwargs):
                result = super().chat(messages, max_tokens=max_tokens, **kwargs)
                if self.options.get('continue_final_message'):
                    return replace(result, content='', reasoning_text='fresh reasoning',
                                   completion_tokens=max_tokens, reasoning_tokens=max_tokens)
                return result
        for backend in ('vllm', 'llamacpp'):
            with self.subTest(backend=backend):
                result, _ = self.world(backend=backend, endpoint_class=IgnoresContinuation,
                    conditions=[Condition('budget_0.6', 'budget', .6)])
                trial = result.trials[0]
                self.assertEqual(len(trial.generation.calls), 2)
                self.assertIn('budget_answer_call_at_token_limit', trial.generation.episode.flags)
                self.assertIn('budget_answer_call_at_token_limit', trial.flags)
                row = summarize(result.trials)[0]
                self.assertEqual((row.trials, row.excluded_trials), (0, 1))
                self.assertIsNone(row.mean_reasoning_tokens)

    def test_generation_failures_are_excluded_and_monitor_is_skipped(self):
        class Broken(ScriptedModel):
            def chat(self, *args, **kwargs): raise OSError('synthetic failure')
        with patch.object(HintMonitor, 'assess', side_effect=AssertionError('must not monitor failed generation')):
            result, _ = self.world(endpoint_class=Broken)
        trial = result.trials[0]
        self.assertIn('generation_error:OSError', trial.flags)
        self.assertIn('monitor_skipped_generation_excluded', trial.flags)
        row = summarize(result.trials)[0]
        self.assertEqual((row.trials, row.excluded_trials, row.scored_trials), (0, 1, 0))
        self.assertIsNone(row.mean_reasoning_tokens)
        self.assertIsNone(row.mean_joules)

    def test_missing_calibration_never_runs_uncapped_budget_work(self):
        class NoCalls(ScriptedModel):
            def chat(self, *args, **kwargs): raise AssertionError('uncalibrated work')
        result, _ = self.world(endpoint_class=NoCalls, settings=Settings(1536, 32, 0),
                               conditions=[Condition('budget_0.6', 'budget', .6)])
        self.assertEqual(result.trials[0].generation.calls, ())
        self.assertIn('generation_skipped', result.trials[0].generation.episode.flags)

    def test_empty_reasoning_has_no_monitor_verdict(self):
        monitor = HintMonitor(Fixed('YES'), revision='synthetic')
        with patch.object(Fixed, 'chat', side_effect=AssertionError('empty monitor input')):
            assessment = monitor.assess(synthetic_items(1).items[0], ' \n')
        self.assertIsNone(assessment.flagged)
        self.assertIn('monitor_reasoning_empty', assessment.flags)

    def test_monitor_exception_preserves_visibility_and_flags(self):
        class Monitor:
            model = 'synthetic'
            def score(self, *args, **kwargs):
                exc = RuntimeError('invalid verdict')
                exc.flags = ('monitor_verdict_invalid',)
                raise exc
        ep = episode(monitors=[(Monitor(), ('full', 'actions_only'))])
        for visibility in ('full', 'actions_only'):
            self.assertIn(f'monitor.{visibility}.monitor_verdict_invalid', ep.flags)

    def test_default_monitor_and_counter_factories_construct(self):
        from joulewise.align.registry_defaults import register_defaults
        register_defaults()
        context = FactoryContext('shade/ledger_review', 'benign', 0, 'matrix', 'host', lambda: 0)
        endpoint = {'base_url': 'http://synthetic', 'model': 'm'}
        monitor = _make('monitor', {'factory': 'shade', 'config': {'endpoint': endpoint}}, context)
        counter = _make('token_counter', {'factory': 'openai_compat', 'config': endpoint}, context)
        self.assertEqual(monitor.model, 'm')
        self.assertTrue(callable(counter.count_tokens))

    def test_cli_fixture_runs_offline_and_empty_run_fails(self):
        spec = {'dataset': {'fixture': True, 'count': 1},
                'models': [{'base_url': 'http://synthetic', 'model': 'm', 'backend': 'mlx',
                            'timeout_s': 1, 'size_b': 1.7, 'runtime_revision': 'synthetic',
                            'attention_design': 'dense', 'clock_domain': 'host'}],
                'monitor': {'base_url': 'http://synthetic', 'backend': 'mlx', 'timeout_s': 1,
                            'runtime_revision': 'synthetic'},
                'settings': {'max_tokens': 64, 'answer_max_tokens': 8, 'calibration_repetitions': 0},
                'conditions': [{'name': 'thinking_off', 'mode': 'off'}]}
        raw = {'choices': [{'message': {'content': 'ANSWER: B'}, 'finish_reason': 'stop'}],
               'usage': {'prompt_tokens': 10, 'completion_tokens': 3,
                         'completion_tokens_details': {'reasoning_tokens': 0}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'config.json'
            path.write_text(json.dumps(spec))
            with patch('joulewise.align.budget.__main__.HubMMLUSource.load', side_effect=AssertionError('Hub forbidden')), \
                 patch.object(LocalEndpoint, '_post', return_value=raw), patch('builtins.print'):
                self.assertEqual(main(['--config', str(path), '--output', str(root/'out')]), 0)
                saved = json.loads((root/'out/result.json').read_text())
                self.assertEqual(len(saved['trials']), 1)
                spec['models'] = []
                path.write_text(json.dumps(spec))
                self.assertEqual(main(['--config', str(path), '--output', str(root/'empty')]), 1)
                self.assertIn('trials_empty', json.loads((root/'empty/result.json').read_text())['flags'])

    def test_apple_sampler_channel_flags_stay_on_their_rail(self):
        clock = FakeClock()
        # Only CPU supports vary (100/200 ms); GPU supports stay 100 ms.
        samples = [PowerSample(t, 4., 'powermetrics', rail=rail,
                                interval_start_s=t-width, interval_end_s=t)
                   for rail in ('cpu_power', 'gpu_power')
                   for t, width in ((.1, .1), (.3, .2 if rail == 'cpu_power' else .1))]
        adapter = SimpleNamespace(start_sampling=lambda *args: AdapterResult(ok=True),
            stop_sampling_with_evidence=lambda *args, **kw: SimpleNamespace(samples=samples, uncertainty_evidence={}))
        sampler = ApplePowerSampler(config(), clock, episode_domain='host', adapter=adapter)
        sampler.start()
        clock.sleep(.3)
        traces = sampler.stop()
        flags = {t.channel: json.loads(t.notes)['flags'] for t in traces}
        self.assertIn('variable_averaging_support:cpu_power', flags['cpu_power'])
        self.assertNotIn('variable_averaging_support:cpu_power', flags['gpu_power'])
        self.assertEqual(sampler.clock_mappings[0].method, 'unmeasured')

    def test_variable_apple_windows_cover_low_to_high_step_through_runner(self):
        # Production-shaped epoch floats and contiguous 99/101 ms supports.
        # A shared edge uses the same float so overlap cannot make the bound
        # infinite and thereby conceal a failed step-allocation test.
        epoch_offset = 1_700_000_000.0123
        class EpochClock(FakeClock):
            def now(self): return super().now() + epoch_offset
            def stamp(self):
                mono = FakeClock.now(self)
                return ClockStamp(self.now(), mono, mono, 1e-9, 1e-9)
            def ns(self): return round(FakeClock.now(self)*SECOND)
        clock = EpochClock(1.85)
        samples = []
        def edge(k): return k/10 + (.001 if k % 2 else 0.) + epoch_offset
        for k in range(41):
            end = edge(k)
            samples.append(PowerSample(end, 2. if k <= 20 else 40., 'powermetrics',
                rail='cpu_power', interval_start_s=edge(k-1), interval_end_s=end))
        evidence = {'clock_anchor': {'status': 'bounded', 'method': 'synthetic_anchor_v2',
            'wall_minus_monotonic_lower_s': epoch_offset-1e-6,
            'wall_minus_monotonic_upper_s': epoch_offset+2e-6,
            'effective_clock_anchor_bound_s': .031}}  # D-078's 31 ms bound.
        adapter = SimpleNamespace(start_sampling=lambda *args: AdapterResult(ok=True),
            stop_sampling_with_evidence=lambda *args, **kw: SimpleNamespace(
                samples=samples, uncertainty_evidence=evidence))
        sampler = ApplePowerSampler(config(), clock, episode_domain='host', adapter=adapter)
        class StepEndpoint(Fixed):
            def chat(self, *args, **kwargs):
                start = clock.ns()
                clock.sleep(.3)
                return replace(super().chat(*args, **kwargs), start_ns=start, end_ns=clock.ns())
        ep, _ = run_episode(Task(), 'benign', StepEndpoint(), samplers=(sampler,),
            seed=0, max_turns=1, max_tokens=64, temperature=0., clock_domain='host', clock=clock.ns)
        trace = ep.power_traces[0]
        notes = json.loads(trace.notes)
        self.assertIsNone(trace.averaging_window_ns)
        self.assertIsNone(trace.resolution)
        self.assertNotIn('timing_half_width_ns', notes)
        for timestamp, support in zip(trace.t_ns, notes['sample_support_ns']):
            a, b = support
            self.assertEqual(timestamp, b)  # Native window-end stamp is exact.
        attribution = attribute_episode(ep, source='powermetrics', channel='cpu_power')
        segment = next(s for s in attribution.segments if s.turn == 0)
        step = 2*SECOND
        # Exact integral of the designed step: each sample is the exact mean
        # of its native [edge(k-1), edge(k)] support, wholly on one side of the
        # step. Epoch serialization perturbs recorded timing only, not truth.
        # Integer ns durations times integer W sum exactly before the final
        # seconds conversion (6.300 J).
        truth = (2*(step-segment.start_ns) + 40*(segment.end_ns-step))/SECOND
        self.assertTrue(math.isfinite(segment.energy.half_width_j))
        self.assertTrue(math.isfinite(attribution.total.half_width_j))
        self.assertLessEqual(abs(segment.energy.joules-truth), segment.energy.half_width_j)
        # Removing window support reproduces the original end-stamped point
        # reconstruction: the 1.9 J lag exceeds its 1.302 J clock bound.
        old_trace = replace(trace, notes='{}')
        old = attribute_episode(replace(ep, power_traces=(old_trace,)),
                                source='powermetrics', channel='cpu_power')
        self.assertGreater(abs(old.total.joules-truth), old.total.half_width_j)
        expected = math.fsum(value*max(0, min(ep.end_ns, b+ep.clock_mappings[0].offset_ns)
                                      - max(ep.start_ns, a+ep.clock_mappings[0].offset_ns))/SECOND
                            for value, (a, b) in zip(trace.values, notes['sample_support_ns']))
        self.assertLessEqual(abs(attribution.total.joules-expected), 1e-6*max(1., abs(expected)))
        self.assertEqual(attribution.total.method.split(';')[0], 'window_average_W')
        turns = turn_energy_from_attribution(attribution)
        self.assertLessEqual(abs(turns[0][0]-truth), turns[0][1])
        budget = episode_energy(ep, channels=(('powermetrics', 'cpu_power'),))
        # Two reducers, project's 1e-6 relative (or absolute near zero) agreement bar.
        self.assertLessEqual(abs(budget.joules-attribution.total.joules),
                             1e-6*max(1., abs(attribution.total.joules)))

    def test_variable_support_rounding_missing_support_and_written_order(self):
        samples = [PowerSample(t/SECOND, 4., 'powermetrics', rail='cpu_power',
                    interval_start_s=a/SECOND if a is not None else None,
                    interval_end_s=t/SECOND if a is not None else None)
                   for t, a in ((10, 7), (20, None), (30, 25))]
        traces, _ = power_records(samples, nominal_interval_ns=10)
        trace = traces[0]
        self.assertEqual(trace.t_ns, (10, 20, 30))
        self.assertEqual(json.loads(trace.notes)['sample_support_ns'], [[7, 10], None, [25, 30]])
        estimate = trace_energy(trace, 8, 27)
        self.assertTrue(math.isinf(estimate.half_width_j))
        self.assertIn('window.support_unknown', estimate.flags)
        ep = Episode('missing', 't', 'benign', 'm', 'e', 0, TRACE_DOMAIN, 8, 27, (),
                     power_traces=(trace,))
        self.assertIn('energy_window_support_unknown', episode_energy(ep).flags)
        # Increasing ends stay in the record even if support midpoints reverse.
        # The overlapping windows remain visibly unsupported to both reducers.
        reversed_midpoints = [PowerSample(t/SECOND, 4., 'powermetrics', rail='cpu_power',
            interval_start_s=a/SECOND, interval_end_s=t/SECOND) for t, a in ((10, 0), (20, -20))]
        traces, flags = power_records(reversed_midpoints, nominal_interval_ns=10)
        self.assertEqual(traces[0].t_ns, (10, 20))
        self.assertEqual(json.loads(traces[0].notes)['sample_support_ns'], [[0, 10], [-20, 20]])
        self.assertIn('window.overlap', trace_energy(traces[0], 0, 20).flags)
        self.assertNotIn('nonincreasing_power_timestamp:cpu_power', flags)
        # Uniform supports retain the window-end representation and no new timing list.
        traces, _ = power_records([samples[0], replace(samples[0], timestamp_s=20/SECOND,
            interval_start_s=17/SECOND, interval_end_s=20/SECOND)], nominal_interval_ns=10)
        self.assertEqual(traces[0].t_ns, (10, 20))
        self.assertEqual(traces[0].averaging_window_ns, 3)
        self.assertNotIn('timing_half_width_ns', json.loads(traces[0].notes))

    def test_window_step_allocation_and_full_support_in_both_reducers(self):
        # A 2 -> 40 W step halfway through the middle window. The native
        # mean is 21 W, so assigning its last half gives 1.26 J, versus
        # 2.4 J of physical work: the half-width must cover the 1.14 J gap.
        for widths in ((100, 120, 80), (100, 100, 100)):
            with self.subTest(widths_ms=widths):
                ends, cursor = [], 0
                for width in widths:
                    cursor += width*SECOND//1000
                    ends.append(cursor)
                starts = (0, ends[0], ends[1])
                samples = [PowerSample(b/SECOND, value, 'powermetrics', rail='cpu_power',
                    interval_start_s=a/SECOND, interval_end_s=b/SECOND)
                    for a, b, value in zip(starts, ends, (2., 21., 40.))]
                traces, _ = power_records(samples, nominal_interval_ns=SECOND//10)
                trace = replace(traces[0], resolution=0.)
                step = (starts[1]+ends[1])//2
                width_s = (ends[1]-step)/SECOND
                ep = Episode('step', 't', 'benign', 'm', 'e', 0, TRACE_DOMAIN,
                             step, ends[1], (), power_traces=(trace,))
                attr = attribute_episode(ep, source='powermetrics', channel='cpu_power')
                query = trace_energy(trace, step, ends[1])
                budget = episode_energy(ep, power_max_w=40.)
                for estimate, bound in ((query.joules, query.half_width_j),
                                        (budget.joules, budget.uncertainty_j)):
                    self.assertTrue(math.isfinite(bound))
                    self.assertAlmostEqual(estimate, 21.*width_s, places=12)
                    self.assertGreaterEqual(bound+1e-6, abs(estimate-40.*width_s))
                self.assertEqual(attr.total.method, 'window_average_W')
                self.assertNotIn('energy_piecewise_linear_between_samples', budget.flags)
                # Whole-window overlap is the native mean integral regardless
                # of the position of the step inside the window.
                whole = replace(ep, start_ns=starts[1])
                expected = 21.*(ends[1]-starts[1])/SECOND
                self.assertAlmostEqual(episode_energy(whole, power_max_w=40.).joules, expected, places=12)
                self.assertAlmostEqual(attribute_episode(whole, source='powermetrics',
                    channel='cpu_power').total.joules, expected, places=12)

    def test_run_floor_is_applied_once_after_rail_sum(self):
        # Two disjoint constant 4 W rails, exact resolution and aligned bounds:
        # no modeled uncertainty; the run has one 1 J attribution minimum.
        trace = PowerTrace('powermetrics', 'cpu', 'host', (0, SECOND),
                           (4., 4.), 'W', SECOND, resolution=0.)
        ep = Episode('rails', 't', 'benign', 'm', 'e', 0, 'host', 0, SECOND, (),
                     power_traces=(trace, replace(trace, channel='gpu')))
        energy = episode_energy(ep, channels=(('powermetrics', 'cpu'), ('powermetrics', 'gpu')),
                                power_max_w=4.)
        self.assertEqual((energy.joules, energy.uncertainty_j), (8., 1.))

    def test_single_native_window_and_malformed_support_do_not_become_points(self):
        trace = PowerTrace('powermetrics', 'cpu', 'host', (SECOND,), (4.,), 'W', SECOND,
                           resolution=0., notes=json.dumps({'sample_support_ns': [[0, SECOND]]}))
        ep = Episode('single', 't', 'benign', 'm', 'e', 0, 'host', 0, SECOND, (),
                     power_traces=(trace,))
        self.assertEqual(trace_energy(trace, 0, SECOND).joules, 4.)
        self.assertEqual(episode_energy(ep, power_max_w=4.).joules, 4.)
        for support in (None, [], [None], [[0, SECOND-1]], [[SECOND, SECOND]], [True]):
            with self.subTest(support=support):
                bad = replace(trace, notes=json.dumps({'sample_support_ns': support}))
                self.assertTrue(math.isinf(trace_energy(bad, 0, SECOND).half_width_j))
                self.assertIsNone(episode_energy(replace(ep, power_traces=(bad,))).joules)

    def test_apple_native_template_preserves_tool_calls_and_thinking_control(self):
        clock = FakeClock()
        runtime = MlxRuntimeAdapter(clock)
        runtime._model = object()
        class Tokenizer:
            eos_token_ids = {0}
            def apply_chat_template(self, messages, **kwargs):
                self.messages, self.kwargs = messages, kwargs
                return 'synthetic rendered prompt'
            def encode(self, text, **kwargs): return [1, 2, 3]
        runtime._tokenizer = Tokenizer()
        def stream_generate(*args, **kwargs):
            clock.sleep(.1)
            yield SimpleNamespace(token=1, text='<think>unfinished', finish_reason='length')
        runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: None)
        cfg = config()
        cfg = replace(cfg, hardware_target=replace(cfg.hardware_target, runtime_backend=RuntimeBackend.MLX))
        endpoint = MlxEndpoint(runtime, cfg, clock, episode_domain='host', enable_thinking=False)
        history = [ChatMessage('user', 'review'), ChatMessage('assistant', ''),
                   ChatMessage('assistant', '{"page":0}', 'read_page', 'call-0'),
                   ChatMessage('tool', '{"rows":[]}', 'read_page', 'call-0')]
        result = endpoint.chat(history, max_tokens=1, temperature=0., seed=0)
        self.assertEqual(result.completion_tokens, 1)
        messages = runtime._tokenizer.messages
        self.assertEqual([m['role'] for m in messages], ['user', 'assistant', 'tool'])
        call = messages[1]['tool_calls'][0]
        self.assertEqual(call['function'], {'name': 'read_page', 'arguments': '{"page":0}'})
        self.assertFalse(runtime._tokenizer.kwargs['enable_thinking'])
        # An unspecified control preserves older/template-default call contracts.
        endpoint.enable_thinking = None
        endpoint.chat(history, max_tokens=1, temperature=0., seed=0)
        self.assertNotIn('enable_thinking', runtime._tokenizer.kwargs)
        flags = result.raw_usage['joulewise']['flags']
        self.assertIn('turn_token_budget_reached:0', flags)
        self.assertIn('unclosed_reasoning_span', flags)
        ep = episode(Fixed(result.content, usage=result.raw_usage, decode=1))
        self.assertIn('endpoint.unclosed_reasoning_span', ep.flags)

    def test_apple_cut_open_thinking_is_hidden_and_visible_prefix_tools_survive(self):
        tool = '<tool_call>{"name":"read_page","arguments":{}}</tool_call>'
        closed = '<think>plan</think>'
        for prefix, finish in (('', 'length'), (tool, 'length'), (closed, 'length'), ('', 'stop')):
            with self.subTest(prefix=prefix, finish=finish):
                clock = FakeClock()
                runtime = MlxRuntimeAdapter(clock)
                runtime._model = object()
                class Tokenizer:
                    eos_token_ids = {0}
                    def apply_chat_template(self, *args, **kwargs): return 'prompt'
                    def encode(self, text, **kwargs): return [1, 2, 3]
                runtime._tokenizer = Tokenizer()
                def stream_generate(*args, **kwargs):
                    clock.sleep(.1)
                    yield SimpleNamespace(token=1, text=prefix+'<think>unfinished', finish_reason=finish)
                runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: None)
                cfg = config()
                cfg = replace(cfg, hardware_target=replace(cfg.hardware_target, runtime_backend=RuntimeBackend.MLX))
                endpoint = MlxEndpoint(runtime, cfg, clock, episode_domain='host')
                result = endpoint.chat([ChatMessage('user', 'review')], max_tokens=1, temperature=0., seed=0)
                flags = result.raw_usage['joulewise']['flags']
                self.assertIn('unclosed_reasoning_span', flags)
                if finish == 'stop':
                    self.assertEqual(result.content, '<think>unfinished')
                    self.assertEqual(result.reasoning_text, '')
                    self.assertEqual(result.reasoning_tokens, 0)
                    self.assertNotIn('reasoning_censored_at_token_limit', flags)
                else:
                    # An earlier closed span in the same turn stays reasoning.
                    self.assertEqual(result.reasoning_text,
                                     'plan\nunfinished' if prefix == closed else 'unfinished')
                    self.assertEqual(result.content, '' if prefix == closed else prefix)
                    self.assertGreater(result.reasoning_tokens, 0)
                    self.assertEqual(result.reasoning_tokens, 1)  # min(1 emitted, 3 retokenized), integer.
                    self.assertIn('reasoning_tokens_retokenized', flags)
                    self.assertIn('reasoning_censored_at_token_limit', flags)
                    self.assertEqual([c.name for c in result.tool_calls], ['read_page'] if prefix == tool else [])


if __name__ == '__main__':
    unittest.main()
