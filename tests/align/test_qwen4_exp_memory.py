import ast
import json
from pathlib import Path
import unittest

from joulewise.align.models.qwen4_exp_memory import ALIGN_CONTEXT_CAP, memory_model
from tests.align.qwen4_exp_reference import tiny_config_dict

ROOT = Path(__file__).resolve().parents[2]


class TestMemoryModel(unittest.TestCase):
    def test_full_config_counts_and_mixed_budget(self):
        config = json.loads((ROOT / "tests/align/fixtures/qwen4_exp_text_config.json").read_text())
        report = memory_model(config)
        self.assertEqual(report["parameter_counts"]["Routed experts"], 120795955200)
        self.assertEqual(report["parameter_counts"]["PLE table (offloaded)"], 51200245760)
        self.assertEqual(report["resident_by_component"]["PLE table (offloaded)"], 0)
        self.assertTrue(report["below_80GB_model_budget"], report["resident_peak_estimate"])
        self.assertGreater(report["physical_peak_upper_estimate"], report["resident_peak_estimate"])
        # The cap comes from the real kit's explicit ruling, not a guessed RoPE limit.
        tree = ast.parse((ROOT / "scripts/align_pilot_kit.py").read_text())
        cap = next(node.value.value for node in tree.body if isinstance(node, ast.Assign) and
                   any(isinstance(n, ast.Name) and n.id == "CONTEXT_CAP" for n in node.targets))
        self.assertEqual(cap, ALIGN_CONTEXT_CAP)

    def test_context_chunk_and_bit_tradeoffs(self):
        c = tiny_config_dict()
        a = memory_model(c, "4", context_tokens=512, chunk_tokens=64, group_size=32)
        b = memory_model(c, "8", context_tokens=512, chunk_tokens=64, group_size=32)
        self.assertLess(a["weights_resident"], b["weights_resident"])
        larger_chunk = memory_model(c, "4", context_tokens=512, chunk_tokens=128, group_size=32)
        self.assertGreater(larger_chunk["resident_peak_estimate"], a["resident_peak_estimate"])
        self.assertEqual(a["state_bytes"], larger_chunk["state_bytes"])
        with self.assertRaises(ValueError):
            memory_model(c, context_tokens=0)


if __name__ == "__main__":
    unittest.main()
