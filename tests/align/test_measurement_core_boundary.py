"""The ALIGN extension must not alter the pre-#658 measurement core bytes."""
import hashlib
from pathlib import Path
import unittest


class MeasurementCoreBoundaryTests(unittest.TestCase):
    def test_pilot9_measurement_core_is_unchanged(self):
        expected = {
            'smc': 'c1896f0c4fd8510ab4a2273927d4d71d8cc7a1a6940928117ba50d8441f70351',
            'monitor': '9ed83410fc2fe7bdbf8e8acffcf913af5bd4442bb23adc14ed61430e0a3c957b',
        }
        root = Path(__file__).resolve().parents[2]
        for name, digest in expected.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((root/'joulewise/hazards'/f'{name}.py').read_bytes()).hexdigest(), digest)
