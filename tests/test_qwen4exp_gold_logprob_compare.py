import importlib.util
import math
import unittest
from pathlib import Path


PATH = Path(__file__).parents[1] / "scripts" / "qwen4exp_gold_logprob_compare.py"
SPEC = importlib.util.spec_from_file_location("gold_compare", PATH)
gold = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gold)


class GoldLogprobMathTests(unittest.TestCase):
    def test_identical_logits_have_zero_symmetric_kl(self):
        result = gold.distribution_metrics([1.0, 2.0, -3.0], [1.0, 2.0, -3.0], top_k=2, target_id=0)
        self.assertAlmostEqual(result["kl_bf16_quant"], 0.0, places=14)
        self.assertAlmostEqual(result["kl_quant_bf16"], 0.0, places=14)
        self.assertEqual(result["top1_agreement"], True)
        self.assertEqual(result["topk_overlap"], 1.0)
        self.assertAlmostEqual(result["nll_difference"], 0.0, places=14)

    def test_synthetic_binary_kl_and_reverse(self):
        # softmax(log probabilities) recovers the desired distributions.
        result = gold.distribution_metrics([math.log(.8), math.log(.2)],
                                           [math.log(.5), math.log(.5)], top_k=1, target_id=1)
        expected = .8 * math.log(.8 / .5) + .2 * math.log(.2 / .5)
        reverse = .5 * math.log(.5 / .8) + .5 * math.log(.5 / .2)
        self.assertAlmostEqual(result["kl_bf16_quant"], expected, places=14)
        self.assertAlmostEqual(result["kl_quant_bf16"], reverse, places=14)
        self.assertAlmostEqual(result["nll_difference"], math.log(.2 / .5), places=14)

    def test_shape_and_target_validation(self):
        with self.assertRaises(ValueError):
            gold.distribution_metrics([1], [1, 2])
        with self.assertRaises(ValueError):
            gold.distribution_metrics([1], [1], target_id=2)


if __name__ == "__main__":
    unittest.main()
