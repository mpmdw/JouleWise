"""Pinned optional MLX numerical gate. Random tiny weights, never model/data I/O.

Run explicitly: python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
Skipping this module is NOT evidence of numerical exactness.
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import unittest

from joulewise.align.apple.prompt_cache import EpisodePromptCache, _arrays, checkpoint_size_from_config


AVAILABLE = importlib.util.find_spec('mlx_lm') is not None


@unittest.skipUnless(AVAILABLE, 'requires offline mlx==0.31.2 and mlx-lm==0.31.3')
class NativeCheckpointTests(unittest.TestCase):
    def test_tiny_random_qwen3_next_bf16_and_float32(self):
        self.assertEqual(importlib.metadata.version('mlx'), '0.31.2')
        self.assertEqual(importlib.metadata.version('mlx-lm'), '0.31.3')
        import mlx.core as mx
        from mlx.utils import tree_map
        from mlx_lm.models.qwen3_next import Model, ModelArgs

        config = dict(
            model_type='qwen3_next', hidden_size=64, num_hidden_layers=4,
            intermediate_size=128, num_attention_heads=2, num_key_value_heads=1,
            head_dim=32, rms_norm_eps=1e-6, vocab_size=64,
            max_position_embeddings=256, rope_theta=10000., partial_rotary_factor=1.,
            rope_scaling=None, attention_bias=False, tie_word_embeddings=False,
            full_attention_interval=2, linear_conv_kernel_dim=4,
            linear_key_head_dim=32, linear_value_head_dim=32,
            linear_num_key_heads=1, linear_num_value_heads=2,
            num_experts=4, num_experts_per_tok=2, moe_intermediate_size=16,
            shared_expert_intermediate_size=16, decoder_sparse_step=1,
            norm_topk_prob=True, mlp_only_layers=[],
        )
        for dtype in (mx.float32, mx.bfloat16):
            with self.subTest(dtype=str(dtype)):
                mx.random.seed(11)
                model = Model(ModelArgs.from_dict(config))
                model.update(tree_map(lambda a: a.astype(dtype), model.parameters()))
                mx.eval(model.parameters())
                state = EpisodePromptCache(model)
                old = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                delta, metadata = state.prepare(old, stable_prefix_ids=old[:5])
                tail = state.prefill_checkpoint(delta, metadata)
                model(mx.array([tail + [10, 11]]), cache=state.cache)
                mx.eval(*list(_arrays([c.state for c in state.cache])))
                state.finish(old, [10, 11], metadata)
                saved = state.checkpoints[-1]
                expected_size = checkpoint_size_from_config(config, conv_itemsize=4 if dtype == mx.float32 else 2)
                self.assertEqual(saved.state_bytes, expected_size['state_bytes'])
                independent_prefix = state.api.make_prompt_cache(model)
                model(mx.array([old[:5]]), cache=independent_prefix)
                mx.eval(*list(_arrays([c.state for c in independent_prefix])))
                saved_state = [list(_arrays(independent_prefix[i].state)) for i in saved.recurrent]
                for layer, expected in zip(saved.recurrent.values(), saved_state):
                    for actual, original in zip(_arrays(layer.state), expected):
                        self.assertTrue(bool(mx.array_equal(actual, original).item()), 'snapshot changed during old suffix prefill')

                def fresh(ids, split=None):
                    cache = state.api.make_prompt_cache(model)
                    if split is not None:
                        model(mx.array([ids[:split]]), cache=cache)
                        mx.eval(*list(_arrays([c.state for c in cache])))
                        logits = model(mx.array([ids[split:]]), cache=cache)
                    else:
                        logits = model(mx.array([ids]), cache=cache)[:, 5:]
                    mx.eval(logits)
                    return logits

                # Repeated rewinds exercise snapshot ownership after mutations
                # and restoration. Every suffix differs from the old history.
                for suffix in ([21, 22, 23], [31, 32, 33]):
                    ids = old[:5] + suffix
                    delta, metadata = state.prepare(ids)
                    self.assertEqual(delta, suffix)
                    self.assertEqual(metadata['cache_checkpoint_restore_count'], 1)
                    restored = model(mx.array([delta]), cache=state.cache)
                    mx.eval(restored)
                    state.finish(ids, [], metadata)
                    reference, repeated = fresh(ids, 5), fresh(ids, 5)
                    deterministic = bool(mx.array_equal(reference, repeated).item())
                    same = bool(mx.array_equal(restored, reference).item())
                    if deterministic:
                        self.assertTrue(same, 'deterministic matched-schedule restore must be bitwise exact')
                    else:
                        # Only repeated identical forward schedules can justify
                        # nondeterminism here; chunking alone cannot excuse it.
                        tolerance = 1e-5 if dtype == mx.float32 else .015625
                        self.assertTrue(bool(mx.allclose(restored, reference, atol=tolerance, rtol=tolerance).item()))
                    bulk = fresh(ids)
                    tolerance = 1e-5 if dtype == mx.float32 else .015625
                    self.assertTrue(bool(mx.allclose(restored, bulk, atol=tolerance, rtol=tolerance).item()),
                                    'one-shot versus split prefill changes matmul/recurrent reduction order')
                    difference = float(mx.max(mx.abs(restored.astype(mx.float32) - bulk.astype(mx.float32))).item())
                    print(f'checkpoint numerical gate dtype={dtype} deterministic={deterministic} '
                          f'matched_schedule_bitwise={same} bulk_max_abs={difference} atol=rtol={tolerance}')
                    for layer, expected in zip(saved.recurrent.values(), saved_state):
                        for actual, original in zip(_arrays(layer.state), expected):
                            self.assertTrue(bool(mx.array_equal(actual, original).item()))


if __name__ == '__main__':
    unittest.main()
