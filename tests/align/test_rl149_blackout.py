"""RL-149 section 2.9 item 4: every copy of the R1 follow-up sizing follows the 02:00-02:35 blackout.

Fast and clock-free: the driver's own construction (align_r1_rehearsal.night_worst_case_s) against the
constants the arm route (r1_arm), the prequalification (w1_prequal) and the follow-up kit carry. PR #777
row-1 review mutant c3 (w1_prequal.R1_BATCH_ENCOUNTER_S back to 12,964) survived the kit modules; this
pins it.
"""
import math
from pathlib import Path
import unittest

from joulewise.align import r1_arm, w1_prequal
from joulewise.b6.plan_inputs import window_max_s
from scripts import align_r1_rehearsal as r1

ROOT = Path(__file__).resolve().parents[2]


class BlackoutSizingTests(unittest.TestCase):
    def setUp(self):
        self.bounds = r1.night_worst_case_s(['--config', str(ROOT / 'configs/align/v4/r1_runtime.json')])

    def test_the_window_and_its_blackout(self):
        self.assertEqual(r1.OS_BATCH_WINDOW_LOCAL, ((2, 0), (2, 35)))
        self.assertEqual(r1.os_batch_blackout_s(), 2100)
        self.assertEqual(self.bounds['batch_blackout_s'], 2100)
        self.assertEqual(r1_arm.BATCH_START_LOCAL, r1.OS_BATCH_WINDOW_LOCAL[0])

    def test_prequal_r1_constants_equal_the_driver_construction(self):
        b = self.bounds
        self.assertEqual(w1_prequal.R1_BATCH_ENCOUNTER_S, math.ceil(b['batch_encounter_max_s']))
        self.assertEqual(w1_prequal.R1_BATCH_ENCOUNTER_S, 9664)
        self.assertEqual(w1_prequal.R1_FOLLOWUP_FLOOR_S, b['floor_s'])
        self.assertEqual(w1_prequal.R1_FOLLOWUP_SPAN_S, b['programmed_span_s'])
        self.assertEqual(w1_prequal.R1_FOLLOWUP_WINDOW_S, b['window_max_s'])
        self.assertEqual((b['floor_s'], b['programmed_span_s'], b['window_max_s']), (93168, 102168, 119880))

    def test_arm_route_constants_equal_the_driver_construction(self):
        self.assertEqual(r1_arm.R1_FOLLOWUP_SPAN_S, self.bounds['programmed_span_s'])
        self.assertEqual(r1_arm.R1_FOLLOWUP_WINDOW_S,
                         window_max_s({'programmed_span_s': {'seconds': r1_arm.R1_FOLLOWUP_SPAN_S}}))

    def test_w1_and_contrast_encounter_is_untouched(self):
        # RL-149: W1, C and T never waited for the batch.
        self.assertEqual(w1_prequal.BATCH_ENCOUNTER_S, 11164)


if __name__ == '__main__':
    unittest.main()
