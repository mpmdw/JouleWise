"""Discrete causal cache checks; native computation is synthetic, not hardware QA."""
from __future__ import annotations

from dataclasses import asdict, replace
import gzip
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.prompt_cache import EpisodePromptCache
from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec
from joulewise.align.interfaces import ChatMessage
from joulewise.align.runner import RepetitionObserver
from joulewise.clock import FakeClock
from joulewise.identity_pins import derive_model_runtime_config_from_metadata
from joulewise.schemas import RuntimeBackend
from tests.align.test_apple_campaign import base_config, episode_spec, as_config


class StatefulCache:
    def __init__(self, trimmable=True):
        self.represented_tokens = []
        self.trimmable = trimmable

    @property
    def offset(self):
        return len(self.represented_tokens)

    def is_trimmable(self):
        return self.trimmable

    def trim(self, n):
        actual = min(n, self.offset)
        if actual:
            del self.represented_tokens[-actual:]
        return actual


class CacheAPI:
    def __init__(self, trimmable=True, wrong_trim=False):
        self.created = []
        self.trimmable = trimmable
        self.wrong_trim = wrong_trim

    def make_prompt_cache(self, model):
        cache = [StatefulCache(self.trimmable), StatefulCache(self.trimmable)]
        self.created.append(cache)
        return cache

    def can_trim_prompt_cache(self, cache):
        return all(c.is_trimmable() for c in cache)

    def trim_prompt_cache(self, cache, n):
        actual = [c.trim(n) for c in cache][0]
        return actual - 1 if self.wrong_trim else actual


def consume(cache, ids):
    for c in cache:
        c.represented_tokens.extend(ids)


class Tokenizer:
    eos_token_ids = {0}

    def apply_chat_template(self, messages, **kwargs):
        return messages[-1]['content']

    def encode(self, text, **kwargs):
        return {'<think>': [90], '</think>': [91]}.get(text, json.loads(text) if text.startswith('[') else [])


def fake_endpoint(api, *, cache=True, mutation=None):
    clock = FakeClock()
    runtime = MlxRuntimeAdapter(clock)
    runtime._model, runtime._tokenizer = object(), Tokenizer()
    seen = []

    def stream_generate(model, tokenizer, prompt, *, max_tokens, sampler, prompt_cache=None):
        native = prompt_cache if prompt_cache is not None else api.make_prompt_cache(model)
        seen.append(list(prompt))
        fed = list(prompt)
        if mutation == 'duplicated_prefix':
            fed = list(native[0].represented_tokens) + fed
        elif mutation == 'omitted_prefix' and native[0].offset:
            for c in native:
                c.represented_tokens.pop(0)
        consume(native, fed)
        # Next token depends on the entire causal sequence, not just the delta.
        token = 1 + int(hashlib.sha256(json.dumps(native[0].represented_tokens).encode()).hexdigest()[:6], 16)
        clock.sleep(len(prompt) * .001)  # D-019 fixture rate: 1 ms per fed token.
        for token, text, finish in ((token, 'x', None), (0, '', 'stop')):
            consume(native, [token])  # MLX lookahead consumes EOS as well.
            clock.sleep(.01)  # D-019 fixture rate: 10 ms per output token.
            yield SimpleNamespace(token=token, text=text, finish_reason=finish)

    runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
    config = base_config()
    config = replace(config, hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
    endpoint = MlxEndpoint(runtime, config, clock, episode_domain='synthetic',
                           prompt_cache='episode_prefix' if cache else None)
    return endpoint, seen


def chat(endpoint, ids):
    return endpoint.chat([ChatMessage('user', json.dumps(ids))], max_tokens=8, temperature=0., seed=1)


class CacheTests(unittest.TestCase):
    def test_exact_outputs_partition_eos_empty_delta_and_hidden_annotations(self):
        api = CacheAPI()
        with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
            cached, seen = fake_endpoint(api)
            uncached, _ = fake_endpoint(api, cache=False)
            prompt = [1, 90, 8, 9, 91, 4]
            for index in range(4):
                a, b = chat(cached, prompt), chat(uncached, prompt)
                ga, gb = cached.turn_provenance[-1]['generation'], uncached.turn_provenance[-1]['generation']
                self.assertEqual(ga['output_token_ids'], gb['output_token_ids'])
                self.assertEqual(a.prompt_tokens, len(prompt))
                self.assertEqual(a.cached_prompt_tokens + ga['prefill_tokens'], len(prompt))
                self.assertEqual(seen[-1], prompt[a.cached_prompt_tokens:])
                self.assertEqual(api.created[0][0].represented_tokens, prompt + ga['output_token_ids'])
                self.assertEqual(ga['prior_hidden_prefill_tokens'], 0)  # unchanged rendered-counterfactual meaning
                self.assertEqual(ga['cached_hidden_context_tokens'] + ga['fresh_hidden_prefill_tokens'], 2)
                prefill = next(e for e in cached.events if e.phase == 'prefill' and e.event_type == 'phase_start'
                               and e.metadata['align_turn_index'] == index)
                self.assertEqual(prefill.metadata['prompt_tokens'], len(prompt))
                self.assertEqual(prefill.metadata['cached_tokens'], a.cached_prompt_tokens)
                self.assertEqual(prefill.metadata['prefill_tokens'], len(seen[-1]))
                # First append is exact, next prompt is fully represented (empty
                # delta would otherwise occur), last one rewrites hidden content.
                if index == 0:
                    prompt = prompt + ga['output_token_ids'] + [5, 6]
                elif index == 1:
                    prompt = prompt + ga['output_token_ids']
                else:
                    prompt = [1, 90, 8, 10, 91, 4]
            self.assertEqual(len(seen[2]), 1)
            self.assertEqual(cached.turn_provenance[-1]['generation']['fresh_hidden_prefill_tokens'], 1)

    def test_untrimmable_whole_cache_rebuild_and_empty_input_rejection(self):
        api = CacheAPI(trimmable=False)
        with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
            endpoint, _ = fake_endpoint(api)
            chat(endpoint, [1, 2, 3])
            generation = endpoint.turn_provenance[-1]['generation']
            chat(endpoint, [1, 2, 3] + generation['output_token_ids'] + [4])
            self.assertEqual(len(api.created), 1)
            chat(endpoint, [1, 9, 3])
            self.assertEqual(len(api.created), 2)
            g = endpoint.turn_provenance[-1]['generation']
            self.assertTrue(g['cache_rebuilt'])
            self.assertEqual(g['cache_fallback_reason'], 'untrimmable_rewrite')
            self.assertEqual(g['cached_prompt_tokens'], 0)
            self.assertIn('cache.rebuilt_untrimmable:2', endpoint.flags)
            with self.assertRaisesRegex(ValueError, 'empty_prompt'):
                endpoint._episode_cache.prepare([])

    def test_consumed_terminal_ids_and_untrimmable_fully_represented_prompt(self):
        for trimmable in (True, False):
            api = CacheAPI(trimmable=trimmable)
            with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
                state = EpisodePromptCache(object())
                delta, metadata = state.prepare([1, 2])
                consume(state.cache, delta + [3])
                # A native stream may yield the terminal ID before consuming
                # it. The actual offset, not the emitted count, owns K.
                state.finish([1, 2], [3, 0], metadata)
                self.assertEqual(state.represented_ids, [1, 2, 3])
                self.assertEqual(metadata['cache_unconsumed_output_tokens'], 1)
                delta, metadata = state.prepare([1, 2, 3])
                self.assertEqual(delta, [3] if trimmable else [1, 2, 3])
                self.assertEqual(metadata['cache_rebuilt'], not trimmable)

    def test_mutated_prefix_or_wrong_trim_cannot_pass(self):
        for mutation in ('duplicated_prefix', 'omitted_prefix', 'wrong_trim'):
            with self.subTest(mutation=mutation):
                api = CacheAPI(wrong_trim=mutation == 'wrong_trim')
                with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
                    endpoint, _ = fake_endpoint(api, mutation=None if mutation == 'wrong_trim' else mutation)
                    chat(endpoint, [1, 2, 3])
                    # Reuse a nonempty prefix but force reconciliation as well.
                    chat(endpoint, [1, 2, 8])
                    self.assertTrue(any(f.startswith('endpoint_error:ValueError:cache_') for f in endpoint.flags), endpoint.flags)
                    self.assertIsNone(endpoint._episode_cache)

    def test_recorded_pilot2_prompts_cover_exact_rewinds_and_B_suffix(self):
        fixture = json.loads(gzip.decompress(Path(__file__).with_name('fixtures').joinpath('pilot2_cache_ids.json.gz').read_bytes()))
        rewinds = {}
        for member in fixture['members']:
            api = CacheAPI(trimmable=member['member'] != 'b-e10')
            with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
                state = EpisodePromptCache(object())
                for index, row in enumerate(member['turns']):
                    p, o = row['prompt_token_ids'], row['output_token_ids']
                    prior = list(state.represented_ids)
                    delta, metadata = state.prepare(p)
                    self.assertEqual(state.represented_ids + delta, p)
                    consume(state.cache, delta)
                    consume(state.cache, o)
                    state.finish(p, o, metadata)
                    self.assertEqual(state.represented_ids, p + o)
                    if metadata['cache_trimmed_tokens']:
                        rewinds[(member['member'], index)] = metadata['cache_trimmed_tokens']
                    if member['member'] == 'b-e05' and index:
                        self.assertEqual(metadata['cache_trimmed_tokens'], len(prior) - len(member['turns'][index-1]['prompt_token_ids']) + 4)
                    if member['member'] == 'b-e10':
                        self.assertFalse(metadata['cache_rebuilt'])
        self.assertEqual({k: v for k, v in rewinds.items() if k[0].startswith('a-')},
                         {('a-e01', 11): 143, ('a-e03', 8): 560, ('a-e03', 10): 257})

    def test_warmup_and_episode_instances_never_share_cache(self):
        api = CacheAPI()
        with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
            warmup, _ = fake_endpoint(api, cache=False)
            chat(warmup, [1, 2, 3])
            a, _ = fake_endpoint(api)
            b, _ = fake_endpoint(api)
            for endpoint in (a, b):
                result = chat(endpoint, [1, 2, 3])
                self.assertEqual(result.cached_prompt_tokens, 0)
            self.assertIsNot(a._episode_cache.cache, b._episode_cache.cache)

    def test_cached_episode_real_prepare_warmup_controller_reduce_and_identity(self):
        import tempfile
        from tests.align.test_apple_endpoint import run_native_review
        from joulewise.align.apple.workload import read_episode_bundle
        from joulewise.cli import validate_bundle
        api = CacheAPI()
        with tempfile.TemporaryDirectory() as d, patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api):
            bundle, summary, projection = run_native_review(Path(d), 'think', FakeClock(), prompt_cache='episode_prefix')
            self.assertEqual(summary.status.value, 'succeeded', summary)
            episode = read_episode_bundle(bundle)
            rows = [json.loads(line) for line in (bundle / 'outputs/align_turns.jsonl').read_text().splitlines()]
            self.assertEqual(rows[0]['generation']['cached_prompt_tokens'], 0)
            self.assertEqual(len(api.created), 1)  # warmup never received the measured cache
            for turn, row in zip(episode.turns, rows, strict=True):
                g = row['generation']
                self.assertEqual(turn.context_tokens + turn.prefill_tokens, len(g['prompt_token_ids']))
                self.assertEqual(turn.context_tokens, g['cached_prompt_tokens'])
            self.assertEqual(rows[2]['generation']['prior_hidden_prefill_tokens'], 74)
            self.assertEqual(rows[2]['generation']['prior_hidden_prefill_method'], 'chat_template_token_count_difference')
            config = json.loads((bundle / 'config.json').read_text())
            metadata = json.loads((bundle / 'metadata.json').read_text())
            self.assertEqual(derive_model_runtime_config_from_metadata(config, metadata),
                             derive_model_runtime_config_from_metadata(config, projection))
            self.assertEqual(metadata['workload_provenance']['cache_policy'], 'episode_prefix')
            self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_campaign_does_not_match_across_cache_policies(self):
        from joulewise.align.apple.campaign import _counterbalanced
        spec = episode_spec(hidden=False)
        ordered, flags = _counterbalanced((spec, replace(spec, condition='sabotage', prompt_cache='episode_prefix')))
        self.assertIn('unmatched_condition_cells_retained', flags)
        self.assertEqual(len(ordered), 2)

    def test_spec_legacy_bytes_and_governed_policy_digest(self):
        spec = episode_spec(hidden=False)
        legacy = asdict(spec)
        for key in ('prompt_cache', 'enable_thinking', 'max_context_tokens'):
            if legacy[key] is None:
                del legacy[key]
        self.assertEqual(spec.to_text(), json.dumps(legacy, sort_keys=True, separators=(',', ':'), allow_nan=False))
        adapter = EpisodeRuntimeAdapter(None, FakeClock())
        adapter.prepared = {"version": "synthetic", "model_artifact_identity": {"sha256": "a" * 64}}
        def identity(s):
            config = as_config(s, "identity-policy")
            metadata = {'workload_provenance': adapter.identity_projection_metadata(config),
                        'runtime': {'name': 'mock', 'version': 'synthetic'},
                        'adapters': {'runtime': {'name': 'mock', 'prepare_metadata': {'version': 'synthetic'}},
                                     'telemetry': {'name': 'mock'}},
                        'device': {}, 'quantization': {}}
            return derive_model_runtime_config_from_metadata(config.to_dict(), metadata)[1]['runtime_identity_sha256']
        projection = adapter.identity_projection_metadata(as_config(spec, "identity-policy"))
        self.assertNotIn('execution_policy', projection['sampler'])
        # This is the pre-cache sampler projection, explicitly constructed from
        # the old contract rather than comparing the new default to itself.
        self.assertEqual(projection['sampler'], {'kind': 'greedy', 'temperature': 0.0, 'pinned': True,
                                                'requested_temperature': spec.temperature, 'max_tokens': spec.max_tokens})
        self.assertEqual(identity(spec), identity(replace(spec, prompt_cache=None)))
        self.assertNotEqual(identity(spec), identity(replace(spec, prompt_cache='episode_prefix')))
        with self.assertRaisesRegex(ValueError, 'prompt_cache'):
            EpisodeSpec.from_text(replace(spec, prompt_cache='wrong').to_text())


class RepetitionTests(unittest.TestCase):
    def test_b_e05_preview_loop_flags_every_repeated_turn_without_stop(self):
        observer = RepetitionObserver()
        flags = [observer.observe([('preview_rule', '{"b":2,"a":1}' if n % 2 else '{"a":1,"b":2}', 'same output')]) for n in range(5)]
        self.assertEqual(flags, [[], *[[f'repetition.identical_call_and_output:{n}'] for n in range(2, 6)]])

    def test_recorded_b_e05_and_b_e12_tool_turns(self):
        members = json.loads(gzip.decompress(Path(__file__).with_name('fixtures').joinpath('pilot2_repetition.json.gz').read_bytes()))
        for member in members:
            observer = RepetitionObserver()
            observed = [observer.observe(turn) for turn in member['turns']]
            if member['member'] == 'b-e05':
                self.assertTrue(any(f.startswith('repetition.identical_call_and_output:') for flags in observed for f in flags))
            else:
                self.assertEqual(member['member'], 'b-e12')
                self.assertTrue(all(not flags for flags in observed), observed)

    def test_b_e12_ten_distinct_contacts_are_not_a_loop(self):
        observer = RepetitionObserver()
        for index in range(10):
            self.assertEqual(observer.observe([('add_venmo_contact', json.dumps({'name': f'Friend {index}'}), f'Added Friend {index}')]), [])
        observer = RepetitionObserver()
        observer.observe([('lookup', '{"page":1}', 'same')])
        self.assertEqual(observer.observe([('lookup', '{"page":2}', 'same')]), ['repetition.identical_output:2'])
        self.assertEqual(observer.observe([]), [])
