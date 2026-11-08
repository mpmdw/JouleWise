"""Failing-first witnesses for the Opus cold review of the v4 registration package.

docs/align/squeeze/fanout/v4-opus-cold-review.md, finding HIGH-1. Synthetic only:
no model, sensor, SHADE cache, custody or network is opened.

HIGH-1. Protocol v4 (``Complete WP21's full desk, WP22's synthetic W1 dry run``)
requires the WP22 dry run before registration. The minimal dry run below reached
a desk record (``desk_status == 'ok'``) at the R10 baseline d600baba0 and fails
at 353446ad6 in two stacked places:

  (a) ``scripts/align_v4_w1_synthetic.py`` binds a contrast_fit computed for
      WP18 X max_turns=5 at import, but ``collect`` re-measures X turns from the
      synthetic pilot-7 reference and rewrites WP18, so the kit refuses with
      ``R11 contrast_fit/contrast_g0_cap_s must bind ...``;
  (b) with (a) fixed, ``align_v4_thermal_desk.registration_evidence`` calls
      ``v4_registration.validate_u3``, which raises unconditionally while U3 is
      PENDING, so the whole desk aborts instead of reporting U3 inconclusive.

The full-window tests that would show this skip unless JW_WP22_FULL=1, so CI
never runs them. This witness takes about 4 s.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import align_v4_w1_synthetic as dry


class Wp22DryRunReachesTheDesk(unittest.TestCase):
    def test_minimal_synthetic_w1_produces_a_desk_record(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'w1'
            self.assertEqual(dry.main([str(out), '--inject', 'none', '--members', '5']), 0)
            record = json.loads((out / 'dry_run_record.json').read_text())
            self.assertEqual(record['desk_status'], 'ok', record.get('desk_error'))


if __name__ == '__main__':
    unittest.main()
