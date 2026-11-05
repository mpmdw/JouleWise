"""Synthetic exact-tie selection and official-reference replay regressions."""
import importlib.util
import unittest
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("torch") and importlib.util.find_spec("transformers"),
                     "optional Torch/reference stack required")
class TestReferenceSelection(unittest.TestCase):
    def test_qsa_patch_forces_indices_and_leaves_moe_alone(self):
        import torch
        from tests.align.qwen4_exp_reference import force_qsa_topk, reference_model
        model = reference_model()
        scores = torch.tensor([0., 2., 0., 0., 2., 0., 0., 0.])
        orders = []

        def select(value, k, dim):
            order = torch.argsort(value, dim=dim, descending=True, stable=True)[:k]
            orders.append(order.tolist())
            return order

        indexer = model.model.layers[1].self_attn.indexer
        # Exercise both spellings used by the reference; only the indexer is
        # patched, so routing's ordinary torch.topk keeps its original API.
        def forward():
            return scores.topk(4), torch.topk(scores, 4)

        original = torch.topk(scores, 4)
        with patch.object(indexer, "forward", forward):
            with force_qsa_topk(model, select):
                first, second = indexer()
                self.assertEqual(first.indices.tolist(), [1, 4, 0, 2])
                self.assertEqual(second.indices.tolist(), [1, 4, 0, 2])
                self.assertEqual(first.values.tolist(), [2., 2., 0., 0.])
                self.assertTrue(torch.equal(torch.topk(scores, 4).indices, original.indices))
            self.assertTrue(torch.equal(indexer()[0].indices, original.indices))
        self.assertEqual(len(orders), 2)

    def test_replay_uses_forced_orders_in_all_modes(self):
        import json
        from pathlib import Path
        import tempfile
        import numpy as np
        from tests.align.qwen4_exp_reference import replay_qsa_gold, write_gold
        with tempfile.TemporaryDirectory(prefix="jw-qsa-replay-") as work:
            root = Path(work)
            write_gold(root / "fixture", "fp32", force_ties=True)
            root = root / "fixture"
            orders = [list(range(min(2, (i + 1) // 2))) for i in range(11)]
            order_file = root / "orders.json"
            order_file.write_text(json.dumps(orders))
            evidence = replay_qsa_gold(root, order_file)
            forced = np.load(root / "forced-gold.npz")
            for mode in ("chunked", "stepwise"):
                np.testing.assert_allclose(forced[mode], forced["prefill"], atol=2e-5, rtol=2e-4)
            self.assertGreater(evidence["alternative_ties_max_abs"], 1e-6)


@unittest.skipUnless(importlib.util.find_spec("mlx"), "optional native MLX stack required")
class TestNativeQSA(unittest.TestCase):
    def test_exact_ties_and_unperturbed_nearby_scores(self):
        import numpy as np
        import mlx.core as mx
        from joulewise.align.models.qwen4_exp import qsa_topk
        rows = np.array([[0, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                         [0] * 12, [2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                         [0, 0, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf,
                          -np.inf, -np.inf, -np.inf, -np.inf, -np.inf]], dtype=np.float32)
        rows[0, 2] = np.nextafter(np.float32(0), np.float32(1)) * 1e30
        for k in (1, 4, 7, 12):
            expected = np.argsort(-rows, axis=-1, kind="stable")[:, :k]
            for _ in range(3):
                np.testing.assert_array_equal(np.array(qsa_topk(mx.array(rows), k)), expected)

    def test_unique_cut_keeps_partition_fast_path(self):
        import numpy as np
        import mlx.core as mx
        from joulewise.align.models.qwen4_exp import qsa_topk
        scores = mx.array([[1., 4., 4., 2., 0., 0., 0., 0.]])
        with patch.object(mx, "argpartition", wraps=mx.argpartition) as partition, patch.object(
                mx, "argsort", wraps=mx.argsort) as sort:
            np.testing.assert_array_equal(np.array(qsa_topk(scores, 3)), [[1, 2, 3]])
            self.assertEqual(partition.call_count, 1)
            self.assertEqual([call.args[0].shape[-1] for call in sort.call_args_list], [3])

    def test_zero_tie_selection_matches_prefill_chunks_and_steps(self):
        import numpy as np
        import mlx.core as mx
        from joulewise.align.models.qwen4_exp import ModelArgs, QSAIndexer, Qwen4ExpAttentionCache
        from tests.align.qwen4_exp_reference import tiny_config_dict
        args = ModelArgs.from_dict(tiny_config_dict())
        indexer = QSAIndexer(args)
        indexer.index_qk_proj.weight = mx.zeros_like(indexer.index_qk_proj.weight)
        length, ratio = 25, args.indexer_compress_ratio

        def selections(chunk):
            cache, output = Qwen4ExpAttentionCache(), []
            for start in range(0, length, chunk):
                end = min(start + chunk, length)
                selected = indexer(mx.ones((1, end - start, args.hidden_size)),
                                   mx.arange(start, end)[None], mx.ones((1, end), dtype=mx.bool_), cache)
                if selected is None:
                    output.extend([list(range(i + 1)) for i in range(start, end)])
                else:
                    tokens, keep = map(np.array, selected)
                    output.extend([tokens[0, j][keep[0, j]].tolist() for j in range(end - start)])
            return output

        expected = [list(range(min(args.indexer_budget, (i + 1) // ratio * ratio))) +
                    list(range((i + 1) // ratio * ratio, i + 1)) for i in range(length)]
        for chunk in (length, 3, 1):
            for _ in range(2):
                self.assertEqual(selections(chunk), expected)


if __name__ == "__main__":
    unittest.main()
