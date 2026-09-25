"""The launch context owns scheduling; children do not change their own QoS."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class NoChildQosOverrideTests(unittest.TestCase):
    def test_driver_and_sampler_contain_no_child_qos_override(self):
        forbidden = re.compile(
            r"\btaskpolicy\b|\bsetpriority\b|\bos\.nice\s*\(|\bnice\s*\("
            r"|\b(?:qos|QOS_CLASS_[A-Z_]+|pthread_set_qos_class_self_np|set_qos_class)\b",
            re.IGNORECASE,
        )
        for relative in ("scripts/run_night.py", "joulewise/adapters/powermetrics.py"):
            with self.subTest(path=relative):
                self.assertIsNone(forbidden.search((ROOT / relative).read_text()))


if __name__ == "__main__":
    unittest.main()
