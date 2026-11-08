"""Default-run witness for the WP22 proof refresh hidden by JW_WP22_FULL.

Only the handoff between the synthetic pilot references and kit admission is
exercised. No window, model, hardware reader, or measurement data is opened.
This deliberately remains red until the owning lane repairs the dry-run harness.
"""
from contextlib import nullcontext
import argparse
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import align_v4_w1_synthetic as dry


class _AdmissionObserved(Exception):
    pass


class Wp22AdmissionWitnessTests(unittest.TestCase):
    def test_generated_pilot_turn_counts_refresh_the_contrast_proof(self):
        def inspect_admission(inputs):
            expected = dry.kit.w1_contrast_g0_cap(
                dry.SYN_R1_SLOTS, inputs['WP18']['X']['max_turns'])
            self.assertEqual(inputs['WP18']['X']['max_turns'], 3)
            self.assertEqual(
                inputs['R1']['thermal_policy']['contrast_fit'], expected,
                'collect() changed WP18 turn counts without refreshing its R11 proof')
            raise _AdmissionObserved()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'outputs').mkdir()
            (root / 'outputs/align_turns.jsonl').write_bytes(b'{"synthetic":true}\n')
            args = argparse.Namespace(leak=0.004, variant='kit', inject='none')
            with patch.object(dry.syn, 'patches', return_value=(nullcontext(), None)), \
                    patch.object(dry, 'synthesize', side_effect=lambda config, _: config), \
                    patch.object(dry, 'run_member', return_value={'bundle': str(root)}), \
                    patch('joulewise.align.apple.workload.read_episode_bundle',
                          return_value=SimpleNamespace(turns=[None] * 3)), \
                    patch.object(dry, 'build_kit', side_effect=inspect_admission), \
                    self.assertRaises(_AdmissionObserved):
                dry.collect(args, root)


if __name__ == '__main__':
    unittest.main()
