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
from joulewise.align.apple.sampler import ApplePowerSampler, TRACE_DOMAIN, stamp_mapping
from joulewise.align.attribution import trace_energy
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
from joulewise.align.records import ClockMapping, Episode, PowerTrace, to_json, from_json
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

    def test_powermetrics_floor_agrees_between_reducers(self):
        # Constant 4 W for exactly 1 s has 4 J; exact integers are representable.
        trace = PowerTrace('powermetrics', 'cpu', 'host', (0, SECOND, 2*SECOND),
                           (4., 4., 4.), 'W', SECOND, resolution=0.)
        ep = Episode('e', 't', 'benign', 'm', 'e', 0, 'host', 0, SECOND, (), power_traces=(trace,))
        budget = episode_energy(ep, channels=(('powermetrics', 'cpu'),), power_max_w=4.)
        attribution = trace_energy(trace, 0, SECOND)
        self.assertEqual(budget.joules, 4.)
        self.assertEqual(attribution.joules, 4.)
        self.assertGreaterEqual(budget.uncertainty_j, 1.)
        self.assertGreaterEqual(attribution.half_width_j, 1.)

    def test_non_vllm_budget_is_excluded_without_generating_pair(self):
        for backend in ('mlx', 'llamacpp'):
            result, endpoint = self.world(backend=backend,
                conditions=[Condition('budget_0.6', 'budget', .6)])
            trial = result.trials[0]
            self.assertIn('budget_forcing_continuation_unsupported', trial.flags)
            self.assertFalse(trial.generation.calls)
            self.assertFalse(trial.paired.calls)
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


if __name__ == '__main__':
    unittest.main()
