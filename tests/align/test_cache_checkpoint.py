"""Synthetic cache mechanics and byte compatibility; no model/data downloads."""
from __future__ import annotations

from dataclasses import asdict, replace
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec
from joulewise.align.apple.prompt_cache import (
    EpisodePromptCache, checkpoint_size_from_config, hybrid_checkpoint_policy,
)
from joulewise.align.interfaces import ChatMessage
from joulewise.clock import FakeClock
from joulewise.schemas import RuntimeBackend
from tests.align.fixtures.prompt_cache_c9a0a394 import EpisodePromptCache as LegacyCache
from tests.align.test_pilot3_cache import CacheAPI, chat, fake_endpoint
from tests.align.test_apple_campaign import as_config, base_config, episode_spec


class StateArray:
    def __init__(self, values):
        self.values = list(values)
        self.nbytes = len(self.values) * 8


class KVCache:
    def __init__(self):
        self.represented_tokens = []

    @property
    def offset(self):
        return len(self.represented_tokens)

    @property
    def state(self):
        return [StateArray(self.represented_tokens)]

    def is_trimmable(self):
        return True

    def trim(self, n):
        actual = min(n, self.offset)
        if actual:
            del self.represented_tokens[-actual:]
        return actual


class ArraysCache:
    def __init__(self):
        self.state = [StateArray([0, 0])]
        self.padding = [0]  # non-state metadata must be copied as well

    def is_trimmable(self):
        return False


class HybridAPI:
    def make_prompt_cache(self, model):
        return [ArraysCache(), KVCache(), ArraysCache(), KVCache()]

    def can_trim_prompt_cache(self, cache):
        return all(c.is_trimmable() for c in cache)


class HybridModel:
    """A causal recurrence sensitive to every consumed token, mutated in place."""
    def __init__(self, clock=None):
        self.clock = clock

    def __call__(self, inputs, *, cache):
        ids = inputs[0]
        for c in cache:
            if isinstance(c, KVCache):
                c.represented_tokens.extend(ids)
            else:
                for token in ids:
                    c.state[0].values[0] = (c.state[0].values[0] * 17 + token) % (2**63 - 1)
                    c.state[0].values[1] += 1
                c.padding[0] += len(ids)
        if self.clock:
            self.clock.sleep(.001 * len(ids))
        return cache[0].state[0].values[0]


def fake_core():
    mlx = ModuleType('mlx')
    @contextmanager
    def context(*args):
        yield
    mlx.core = SimpleNamespace(array=lambda value: value, eval=lambda *values: None,
                               clear_cache=lambda: None, stream=context)
    return {'mlx': mlx, 'mlx.core': mlx.core,
            'mlx_lm.generate': SimpleNamespace(wired_limit=context, generation_stream=object())}


def hybrid_endpoint(model_config, limit=0):
    class Tokenizer:
        eos_token_ids = {0}

        def __init__(self):
            self.renders = []

        def apply_chat_template(self, messages, *, add_generation_prompt, **kwargs):
            self.renders.append(add_generation_prompt)
            return json.dumps(json.loads(messages[-1]['content']) + ([90] if add_generation_prompt else []))

        def encode(self, text, **kwargs):
            return json.loads(text) if text.startswith('[') else []

    clock = FakeClock()
    runtime = MlxRuntimeAdapter(clock)
    runtime._model, runtime._tokenizer = HybridModel(clock), Tokenizer()
    runtime._model_config = model_config
    fed = []

    def stream_generate(model, tokenizer, prompt, *, prompt_cache, **kwargs):
        fed.append(list(prompt))
        model([prompt], cache=prompt_cache)
        for token in (7, 0):
            model([[token]], cache=prompt_cache)
            yield SimpleNamespace(token=token, text='', finish_reason='stop' if token == 0 else None)

    runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
    config = base_config()
    config = replace(config, hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
    return MlxEndpoint(runtime, config, clock, episode_domain='synthetic',
                       prompt_cache='episode_prefix', hybrid_checkpoint_limit=limit), fed


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.core = patch.dict('sys.modules', fake_core())
        self.core.start()
        self.api = patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=HybridAPI())
        self.api.start()
        self.addCleanup(self.api.stop)
        self.addCleanup(self.core.stop)
        self.model = HybridModel()
        self.cache = EpisodePromptCache(self.model, checkpoint_limit=2)

    def turn(self, ids, boundary=None, *, output=(7, 0)):
        delta, metadata = self.cache.prepare(ids, stable_prefix_ids=ids[:boundary] if boundary else None)
        native_delta = self.cache.prefill_checkpoint(delta, metadata, step_size=2)
        self.model([native_delta + list(output)], cache=self.cache.cache)
        self.cache.finish(ids, output, metadata)
        return metadata

    def test_rewrite_restores_all_layers_and_saves_prefill(self):
        self.turn([1, 2, 3, 90], 3)
        saved = self.cache.checkpoints[0]
        self.assertEqual(saved.recurrent[0].state[0].values[1], 3)
        self.assertEqual(saved.recurrent[0].padding, [3])
        metadata = self.turn([1, 2, 3, 8, 9])
        self.assertEqual(metadata['cached_prompt_tokens'], 3)
        self.assertEqual(metadata['prefill_tokens'], 2)
        self.assertEqual(metadata['cache_prefill_tokens_saved'], 3)
        self.assertEqual(metadata['cache_checkpoint_restore_count'], 1)
        self.assertEqual(metadata['cache_checkpoint_restore_bytes'], 2 * 16 + 2 * 8)
        self.assertFalse(metadata['cache_rebuilt'])
        fresh = HybridAPI().make_prompt_cache(self.model)
        self.model([[1, 2, 3, 8, 9, 7, 0]], cache=fresh)
        for a, b in zip(self.cache.cache, fresh):
            if isinstance(a, ArraysCache):
                self.assertEqual(a.state[0].values, b.state[0].values)
                self.assertEqual(a.padding, b.padding)
        # The native forward above mutates its input state in place. Neither
        # capture nor restore may share mutable storage with the saved state.
        self.assertEqual(saved.recurrent[0].state[0].values[1], 3)
        self.assertIsNot(self.cache.cache[0], saved.recurrent[0])

    def test_real_122b_policy_and_runtime_agree_and_unknown_hybrids_fail_closed(self):
        raw = (Path(__file__).with_name('fixtures') / 'qwen35_122b_config.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         'fc1c3921b5146143cda7a5feed445cc31c8929cc3f164f967ec6340b448086eb')
        cfg = json.loads(raw)
        self.assertEqual(cfg['model_type'], 'qwen3_5_moe')
        self.assertEqual(cfg['text_config']['model_type'], 'qwen3_5_moe_text')
        self.assertEqual(cfg['text_config']['num_hidden_layers'], 48)
        self.assertEqual(cfg['quantization']['bits'], 4)
        for config, limit, expected in ((cfg, 2, 2), (cfg, 0, 0), (cfg, None, 0),
                                        ({'model_type': 'lfm2'}, 2, 0), (None, 2, 0)):
            with self.subTest(config=config and config.get('model_type'), limit=limit):
                endpoint, fed = hybrid_endpoint(config, limit)
                spec = replace(episode_spec(hidden=False), prompt_cache='episode_prefix', hybrid_checkpoint_limit=limit)
                adapter = EpisodeRuntimeAdapter(endpoint.runtime, endpoint.clock)
                policy = adapter.identity_projection_metadata(as_config(spec, 'identity'))['sampler']['execution_policy']
                self.assertEqual(policy.get('checkpoint'), endpoint._checkpoint_policy)
                self.assertEqual((policy.get('checkpoint') or {}).get('limit', 0), expected)
                chat(endpoint, [1, 2, 3])
                self.assertFalse(any(f.startswith('endpoint_error') for f in endpoint.flags), endpoint.flags)
                self.assertEqual(endpoint._episode_cache.checkpoint_limit, expected)
                self.assertEqual(len(endpoint._episode_cache.checkpoints), int(bool(expected)))
                self.assertEqual(fed, [[90]] if expected else [[1, 2, 3, 90]])
                self.assertEqual(endpoint.runtime._tokenizer.renders, [True, False] if expected else [True])

    def test_manual_prefill_matches_native_context_chunks_and_allocator_cleanup(self):
        active = set()
        calls = []
        stream = object()

        @contextmanager
        def context(name, value):
            self.assertEqual(value, [stream] if name == 'wired' else stream)
            active.add(name)
            try:
                yield
            finally:
                active.remove(name)

        model = self.model
        def forward(inputs, *, cache):
            self.assertEqual(active, {'wired', 'stream'})
            calls.append(('forward', len(inputs[0])))
            return model(inputs, cache=cache)

        def clear_cache():
            self.assertEqual(active, {'wired', 'stream'})
            calls.append(('clear', None))

        self.cache.model = forward
        core = fake_core()
        core['mlx.core'].stream = lambda value: context('stream', value)
        core['mlx.core'].clear_cache = clear_cache
        core['mlx_lm.generate'] = SimpleNamespace(
            wired_limit=lambda model, streams: context('wired', streams), generation_stream=stream)
        prefix = [1] * (2048 + 73)
        delta, metadata = self.cache.prepare(prefix + [90], stable_prefix_ids=prefix)
        with patch.dict('sys.modules', core):
            tail = self.cache.prefill_checkpoint(delta, metadata)
        self.assertEqual(tail, [90])
        self.assertEqual(calls, [('forward', 2048), ('clear', None), ('forward', 73), ('clear', None)])
        self.assertEqual(active, set())
        self.assertEqual(hybrid_checkpoint_policy({'model_type': 'qwen3_next'}, 2)['prefill_step_size'], 2048)

    def test_setup_and_provenance_checkpoint_fields_have_unambiguous_times(self):
        endpoint, _ = hybrid_endpoint({'model_type': 'qwen3_next'}, 2)
        for ids in ([1, 2, 3], [1, 2, 3, 8]):
            chat(endpoint, ids)
            generation = endpoint.turn_provenance[-1]['generation']
            setup = [e.metadata for e in endpoint.events
                     if e.phase == 'generation_setup' and e.event_type == 'phase_end'][-1]
            for key in ('cache_checkpoint_count', 'cache_checkpoint_bytes', 'cache_checkpoint_retained_bytes'):
                self.assertEqual(setup[key], generation[key])
            cache = endpoint._episode_cache
            sizes = [c.state_bytes + 8 * len(cache.offsets()) for c in cache.checkpoints]
            self.assertEqual(generation['cache_checkpoint_count_after_prefill'], len(sizes))
            self.assertEqual(generation['cache_checkpoint_bytes_after_prefill'], sizes[-1])
            self.assertEqual(generation['cache_checkpoint_retained_bytes_after_prefill'], sum(sizes))
        self.assertEqual(generation['cache_checkpoint_count'], 1)
        self.assertEqual(generation['cache_checkpoint_count_after_prefill'], 2)

    def test_newest_compatible_checkpoint_and_branch_invalidation(self):
        self.turn([1, 2, 3, 90], 3)
        previous = self.cache.represented_ids[:]
        self.turn(previous + [4, 5, 90], len(previous) + 2)
        self.assertEqual([c.length for c in self.cache.checkpoints], [3, 8])
        metadata = self.turn(previous + [4, 5, 11])
        self.assertEqual(metadata['cache_checkpoint_restored_tokens'], 8)
        metadata = self.turn([1, 2, 3, 12])
        self.assertEqual(metadata['cache_checkpoint_restored_tokens'], 3)
        self.assertEqual([c.length for c in self.cache.checkpoints], [3])

    def test_ring_bound_and_evicted_prefix_falls_back_to_full_rebuild(self):
        for i in range(4):
            ids = self.cache.represented_ids + [i + 1, 90]
            self.turn(ids, len(ids) - 1)
            self.assertLessEqual(len(self.cache.checkpoints), 2)
        self.assertEqual([c.length for c in self.cache.checkpoints], [9, 13])
        metadata = self.turn([1, 12, 13])
        self.assertTrue(metadata['cache_rebuilt'])
        self.assertEqual(metadata['cache_fallback_reason'], 'untrimmable_rewrite')
        self.assertEqual(metadata['cache_checkpoint_restore_count'], 0)
        self.assertEqual(metadata['cache_checkpoint_restore_bytes'], 0)
        self.assertEqual(metadata['cache_prefill_tokens_saved'], 0)
        self.assertEqual(self.cache.checkpoints, [])

    def test_disabled_checkpoints_keep_old_whole_rebuild(self):
        self.cache = EpisodePromptCache(self.model, checkpoint_limit=0)
        self.turn([1, 2, 3, 90], 3)
        metadata = self.turn([1, 2, 3, 91])
        self.assertTrue(metadata['cache_rebuilt'])
        self.assertNotIn('cache_checkpoint_policy', metadata)
        for value in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                EpisodePromptCache(self.model, checkpoint_limit=value)

    def test_wholly_represented_prompt_still_feeds_a_token(self):
        self.turn([1, 2, 3, 90], 3)
        delta, metadata = self.cache.prepare([1, 2, 3])
        self.assertEqual(delta, [1, 2, 3])  # checkpoint 3 exceeds capped LCP 2
        self.assertTrue(metadata['cache_rebuilt'])

    def test_bad_offsets_and_wrong_trim_fail_closed(self):
        self.turn([1, 2, 3, 90], 3)
        self.cache.cache[1].represented_tokens.pop()
        with self.assertRaisesRegex(ValueError, 'cache_offset_mismatch'):
            self.cache.prepare([1, 2, 3, 91])
        self.cache = EpisodePromptCache(self.model, checkpoint_limit=2)
        self.turn([1, 2, 3, 90], 3)
        self.cache.cache[1].trim = lambda n: n - 1
        with self.assertRaisesRegex(ValueError, 'cache_checkpoint_wrong_trim'):
            self.cache.prepare([1, 2, 3, 91])

    def test_endpoint_records_full_work_inside_prefill_phase(self):
        class Tokenizer:
            eos_token_ids = {0}

            def apply_chat_template(self, messages, *, add_generation_prompt, **kwargs):
                ids = json.loads(messages[-1]['content'])
                return json.dumps(ids + ([90] if add_generation_prompt else []))

            def encode(self, text, **kwargs):
                return json.loads(text) if text.startswith('[') else []

        clock = FakeClock()
        runtime = MlxRuntimeAdapter(clock)
        runtime._model, runtime._tokenizer = HybridModel(clock), Tokenizer()
        runtime._model_config = {'model_type': 'qwen3_next'}
        records = []
        generate = runtime._generate

        def capture_record(*args, **kwargs):
            record = generate(*args, **kwargs)
            records.append(record)
            return record

        runtime._generate = capture_record

        def stream_generate(model, tokenizer, prompt, *, prompt_cache, **kwargs):
            model([prompt], cache=prompt_cache)
            for token in (7, 0):
                model([[token]], cache=prompt_cache)
                yield SimpleNamespace(token=token, text='', finish_reason='stop' if token == 0 else None)

        runtime._mlx_lm = SimpleNamespace(stream_generate=stream_generate, make_sampler=lambda temp: object())
        config = base_config()
        config = replace(config, hardware_target=replace(config.hardware_target, runtime_backend=RuntimeBackend.MLX))
        endpoint = MlxEndpoint(runtime, config, clock, episode_domain='synthetic', prompt_cache='episode_prefix',
                               hybrid_checkpoint_limit=2)
        for ids in ([1, 2, 3], [1, 2, 3, 8]):
            result = endpoint.chat([ChatMessage('user', json.dumps(ids))], max_tokens=8, temperature=0., seed=1)
            self.assertFalse(any(f.startswith('endpoint_error') for f in endpoint.flags), endpoint.flags)
            g = endpoint.turn_provenance[-1]['generation']
            self.assertEqual(g['prefill_tokens'], result.prompt_tokens - result.cached_prompt_tokens)
            self.assertIn('cache_checkpoint_restore_bytes', g)
        g = endpoint.turn_provenance[-1]['generation']
        self.assertEqual(g['cache_prefill_tokens_saved'], 3)
        self.assertEqual(g['cache_checkpoint_restore_count'], 1)
        prefills = [e for e in endpoint.events if e.phase == 'prefill' and e.event_type == 'phase_start']
        self.assertEqual([e.metadata['prefill_tokens'] for e in prefills], [4, 2])
        self.assertEqual([r.prefill_tokens for r in records], [4, 2])
        self.assertEqual(g['cache_checkpoint_count_after_prefill'], 2)
        self.assertIn('cache_checkpoint_restore_bytes', json.loads(json.dumps(endpoint.turn_provenance))[-1]['generation'])


class CompatibilityAndSizingTests(unittest.TestCase):
    def test_checkpoint_limit_is_explicit_validated_and_part_of_identity(self):
        spec = episode_spec(hidden=False)
        self.assertEqual(spec.hybrid_checkpoint_limit, 0)
        self.assertEqual(EpisodeSpec.from_text(spec.to_text()).hybrid_checkpoint_limit, 0)
        runtime = SimpleNamespace(name='synthetic', _model_config={'model_type': 'qwen3_next'})
        adapter = EpisodeRuntimeAdapter(runtime, FakeClock())
        policies = []
        for limit in (None, 0, 1, 2):
            requested = replace(spec, prompt_cache='episode_prefix', hybrid_checkpoint_limit=limit)
            text = requested.to_text()
            self.assertEqual('hybrid_checkpoint_limit' in json.loads(text), limit is not None)
            policy = adapter.identity_projection_metadata(as_config(requested, 'policy'))['sampler']['execution_policy']
            self.assertEqual('hybrid_checkpoint_limit' in policy, limit is not None)
            if limit is not None:
                self.assertEqual(policy['hybrid_checkpoint_limit'], limit)
            if limit:
                self.assertEqual(policy['checkpoint']['limit'], limit)
            else:
                self.assertNotIn('checkpoint', policy)
                self.assertEqual(policy['fallback'], 'whole_cache_rebuild_on_untrimmable_rewrite')
            policies.append(json.dumps(policy, sort_keys=True))
        self.assertEqual(len(set(policies)), 4)
        for invalid in (-1, True, 1.5, '2'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                EpisodeSpec.from_text(replace(spec, hybrid_checkpoint_limit=invalid).to_text())

    def test_cache_constructor_defaults_to_rebuild_only(self):
        with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=HybridAPI()):
            cache = EpisodePromptCache(HybridModel())
            delta, metadata = cache.prepare([1, 2, 3], stable_prefix_ids=[1, 2])
        self.assertEqual(cache.checkpoint_limit, 0)
        self.assertIsNone(cache._checkpoint_length)
        self.assertEqual(delta, [1, 2, 3])
        self.assertNotIn('cache_checkpoint_policy', metadata)

    def test_nonhybrid_append_only_endpoint_bytes_match_base_commit(self):
        class LegacyEndpointCache(LegacyCache):
            # Adapt only the new call sites; the baseline reconciliation and
            # finish implementations are the untouched c9a0a394 source fixture.
            hybrid = False

            def __init__(self, model, **kwargs):
                super().__init__(model)

            def prefill_checkpoint(self, delta, metadata):
                return delta

        def episode(cache_type):
            api = CacheAPI()
            with patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=api), \
                 patch('tests.align.fixtures.prompt_cache_c9a0a394.native_cache_api', return_value=api), \
                 patch('joulewise.align.apple.prompt_cache.EpisodePromptCache', cache_type):
                endpoint, seen = fake_endpoint(api)
                ids = [1, 90, 3, 91, 4]
                results = []
                for _ in range(3):
                    results.append(asdict(chat(endpoint, ids)))
                    ids += endpoint.turn_provenance[-1]['generation']['output_token_ids'] + [5]
                return json.dumps({'results': results, 'events': [asdict(e) for e in endpoint.events],
                                   'turns': endpoint.turn_provenance, 'identity': endpoint.identity,
                                   'flags': endpoint.flags, 'native_inputs': seen}, sort_keys=True).encode()
        self.assertEqual(episode(EpisodePromptCache), episode(LegacyEndpointCache))

    def test_config_shape_formula_and_dtype_cost(self):
        fixture = Path(__file__).with_name('fixtures') / 'qwen38_config.json'
        cfg = json.loads(fixture.read_text())
        result = checkpoint_size_from_config(cfg)
        self.assertEqual(result['linear_layers'], 48)
        self.assertEqual(result['attention_layers'], 16)
        self.assertEqual(result['conv_bytes_per_layer'], 61440)
        self.assertEqual(result['recurrent_bytes_per_layer'], 3145728)
        self.assertEqual(result['checkpoint_bytes'], 153944192)
        fp32 = checkpoint_size_from_config(cfg, conv_itemsize=4)
        self.assertEqual(fp32['state_bytes'] - result['state_bytes'], 48 * 61440)
        self.assertIsNotNone(hybrid_checkpoint_policy(cfg, 2))
        self.assertIsNotNone(hybrid_checkpoint_policy({'model_type': 'qwen3_next'}, 2))
        self.assertIsNone(hybrid_checkpoint_policy({'model_type': 'qwen3_moe'}))
        self.assertIsNone(hybrid_checkpoint_policy(None))

    def test_hybrid_policy_identity_addition_leaves_anchor_policy_unchanged(self):
        runtime = SimpleNamespace(name='synthetic', _model_config={'model_type': 'qwen3_moe'})
        adapter = EpisodeRuntimeAdapter(runtime, FakeClock())
        adapter.prepared = {'version': 'synthetic'}
        config = as_config(replace(episode_spec(hidden=False), prompt_cache='episode_prefix', hybrid_checkpoint_limit=2), 'synthetic-policy')
        anchor = adapter.identity_projection_metadata(config)['sampler']['execution_policy']
        self.assertEqual(anchor['fallback'], 'whole_cache_rebuild_on_untrimmable_rewrite')
        self.assertNotIn('checkpoint', anchor)
        runtime._model_config = {'model_type': 'qwen3_next'}
        hybrid = adapter.identity_projection_metadata(config)['sampler']['execution_policy']
        self.assertEqual(hybrid['checkpoint']['limit'], 2)
        self.assertEqual(hybrid['checkpoint']['policy'], 'hybrid_boundary_v1')
        self.assertEqual(hybrid['fallback'], 'checkpoint_then_whole_cache_rebuild_on_untrimmable_rewrite')

    def test_next_supplied_config_payload(self):
        raw = (Path(__file__).with_name('fixtures') / 'qwen3_next_config.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         'f5a5422b8e3d47733f0073ff22dec1dc4a7832fec5fc1cf36eba31ace03cf0c4')
        cfg = json.loads(raw)
        self.assertEqual(cfg['model_type'], 'qwen3_next')
        result = checkpoint_size_from_config(cfg)
        self.assertEqual(result, dict(
            linear_layers=36, attention_layers=12,
            conv_bytes_per_layer=49152, recurrent_bytes_per_layer=2097152,
            state_bytes=77266944, offset_bytes=96, checkpoint_bytes=77267040,
            state_itemsize=4, conv_itemsize=2,
        ))
        self.assertEqual(2 * result['checkpoint_bytes'], 154534080)
        self.assertEqual(checkpoint_size_from_config(cfg, conv_itemsize=4)['checkpoint_bytes'],
                         79036512)


if __name__ == '__main__':
    unittest.main()
