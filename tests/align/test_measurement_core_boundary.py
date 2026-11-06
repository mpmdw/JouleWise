"""The ALIGN extension must not alter the pre-#658 measurement core bytes."""
import hashlib
from pathlib import Path
import unittest


class MeasurementCoreBoundaryTests(unittest.TestCase):
    def test_pilot9_measurement_core_is_unchanged(self):
        # SHA-256 of each complete file at pilot-9 c9a0a3943. No Git or
        # access to measurement data is needed to enforce this in shallow CI.
        expected = {
            'joulewise/schemas.py': '344b12ce178b8acb212059097a4ade507812a4be1673a6552ec221a83055e1d1',
            'joulewise/b5/driver.py': 'e1b3df745c82f4a4cec812ade3e4e7c1b460c6c4bec1f6970a3ef13736ab2e89',
            'joulewise/b5/harvest.py': '2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744',
            'joulewise/hazards/smc.py': 'c1896f0c4fd8510ab4a2273927d4d71d8cc7a1a6940928117ba50d8441f70351',
            'joulewise/hazards/monitor.py': '9ed83410fc2fe7bdbf8e8acffcf913af5bd4442bb23adc14ed61430e0a3c957b',
        }
        root = Path(__file__).resolve().parents[2]
        for name, digest in expected.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(), digest)

    def test_wp14_c_untouched_execution_path_files(self):
        expected = {
            'scripts/run_campaign.py': '734820b2467a4296d07001ead3af4f8f0def451bb1a4ab130f3d87457716efc7',
            'joulewise/controller.py': 'a50b0b66098a0d12b4fa7598ea6b317992e52ec7af128372edcf57a3dd880c90',
            'joulewise/adapters/__init__.py': '32917f9f483bf66158a38318e05f751dc976443dc1c234b534ccdb3ffdbad54a',
            'joulewise/__main__.py': 'fb8ca2a72fae8f2b3a725b457d7befd8f9761620922457166553d0eaaa95c33e',
            'joulewise/bundle.py': '871d71c71082fc01da6534c82095ce8932a1caa31202c82fd72837be0d9ef1d8',
        }
        root = Path(__file__).resolve().parents[2]
        for name, digest in expected.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(), digest)
