"""Synthetic cache mechanics and byte compatibility; no model/data downloads."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.workload import EpisodeRuntimeAdapter
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
    mlx.core = SimpleNamespace(array=lambda value: value, eval=lambda *values: None)
    return {'mlx': mlx, 'mlx.core': mlx.core}


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.core = patch.dict('sys.modules', fake_core())
        self.core.start()
        self.api = patch('joulewise.align.apple.prompt_cache.native_cache_api', return_value=HybridAPI())
        self.api.start()
        self.addCleanup(self.api.stop)
        self.addCleanup(self.core.stop)
        self.model = HybridModel()
        self.cache = EpisodePromptCache(self.model)

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
        self.cache = EpisodePromptCache(self.model)
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
        endpoint = MlxEndpoint(runtime, config, clock, episode_domain='synthetic', prompt_cache='episode_prefix')
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
        self.assertEqual(g['cache_checkpoint_count'], 2)
        self.assertIn('cache_checkpoint_restore_bytes', json.loads(json.dumps(endpoint.turn_provenance))[-1]['generation'])


class CompatibilityAndSizingTests(unittest.TestCase):
    def test_nonhybrid_append_only_endpoint_bytes_match_base_commit(self):
        class LegacyEndpointCache(LegacyCache):
            # Adapt only the new call sites; the baseline reconciliation and
            # finish implementations are the untouched c9a0a394 source fixture.
            hybrid = False

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
        self.assertIsNotNone(hybrid_checkpoint_policy(cfg))
        self.assertIsNotNone(hybrid_checkpoint_policy({'model_type': 'qwen3_next'}))
        self.assertIsNone(hybrid_checkpoint_policy({'model_type': 'qwen3_moe'}))
        self.assertIsNone(hybrid_checkpoint_policy(None))

    def test_hybrid_policy_identity_addition_leaves_anchor_policy_unchanged(self):
        runtime = SimpleNamespace(name='synthetic', _model_config={'model_type': 'qwen3_moe'})
        adapter = EpisodeRuntimeAdapter(runtime, FakeClock())
        adapter.prepared = {'version': 'synthetic'}
        config = as_config(replace(episode_spec(hidden=False), prompt_cache='episode_prefix'), 'synthetic-policy')
        anchor = adapter.identity_projection_metadata(config)['sampler']['execution_policy']
        self.assertEqual(anchor['fallback'], 'whole_cache_rebuild_on_untrimmable_rewrite')
        self.assertNotIn('checkpoint', anchor)
        runtime._model_config = {'model_type': 'qwen3_next'}
        hybrid = adapter.identity_projection_metadata(config)['sampler']['execution_policy']
        self.assertEqual(hybrid['checkpoint']['limit'], 2)
        self.assertEqual(hybrid['checkpoint']['policy'], 'hybrid_boundary_v1')
        self.assertEqual(hybrid['fallback'], 'checkpoint_then_whole_cache_rebuild_on_untrimmable_rewrite')


if __name__ == '__main__':
    unittest.main()
