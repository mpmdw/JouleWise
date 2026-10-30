"""L9-STEP4-2 R1 and L9-STEP4-3: the registered step-4 reason table is the blind table plus the recorded ruling.

step4_reason_classes.json copies the mask and tooling lists of
CLASS_TABLE.json at 08ea5c958. step4_reasons/make_table.py is that commit's
generator, byte for byte; rerunning it over this checkout's extractor modules
must reproduce both lists, so a new extractor code literal cannot fall
outside the registered table without this test failing.

L9-STEP4-3 records the lead's ruling (RUN_STATE items 132-133 and 138) beside
the generator output, never inside it: the 'r3' list of plan section 2.2 codes
and the step-4 rule. The registered file must equal generator output plus
RULING below, byte for byte, so the table and this test change together.

L9-STEP4-4 (lead ruling, plan-literal reading of section 2.2 bullet 3; Fable
F1 of L9-STEP4-3-FABLE-REV): every member-level code that bullet names
literally and that can reach a step-4 extractor cell is R3 too. The two it
names that never reach a cell (claim-gate codes) are pinned out below.
"""
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis import steps

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / 'configs/analysis/b5/step4_reason_classes.json'
GENERATOR = Path(__file__).resolve().parent / 'step4_reasons/make_table.py'
PLAN = ROOT / 'configs/campaigns/v5_claim_25g83/analysis_plan_block5.md'

HEADER = {
    'schema_version': 'joulewise.b5_step4_reason_classes.v2',
    'source': {
        'commit': '08ea5c95849654c066811273807f9ca6bf5327cf',
        'table': 'docs/process_traces/2026-10-30-step4-reasons/CLASS_TABLE.json',
        'generator': 'docs/process_traces/2026-10-30-step4-reasons/make_table.py',
        'generator_sha256': '051c13b267c747f3c4bf88318c819bcb9c5c603ba608160ca04389e817a549d2',
    },
}
RULING = {
    'r3': ['anchor_energy_envelope_exceeds_quarter_metric', 'cadence_ratio_below_threshold',
           'calibration_acceptance_bound_stale', 'campaign_cooldown_evidence_missing',
           'clock_bound_exceeds_quarter_window', 'idle_window_suspect',
           'instrument_calibration_stale', 'insufficient_in_window_samples',
           'insufficient_members_after_exclusion', 'kept_units_below_minimum',
           'window_evidence_precheck_missing'],
    'step4_rule': {
        'ruling': 'L9-STEP4-3 lead ruling, RUN_STATE items 132-133 and 138, made blind',
        'refused_cells_only_p42': 'p42_floor_cells_only',
        'refused_non_p42_cell_without_reasons': 'extraction_report_malformed',
        'any_r3_reason_on_a_refused_non_p42_cell': 'extraction_cell_r3_refusal',
        'otherwise': 'extraction_cell_tooling_refusal',
        'mask_and_tooling_lists': 'blind generator output, not read at step 4',
    },
}

# Plan section 2.2 sentences that route each R3 code (whitespace-normalized).
MINIMUM_RULE = ('If an analysis program finds fewer, the program and the exclusion function disagree: '
                'the analysis stops and the step goes to R3.')
MEMBER_RULE = ("If one fires on a kept unit, the registration's member rules and the code disagree: "
               'the analysis stops and the step goes to R3.')
# code -> (producer module, emission site literal, plan sentence)
R3_PINS = {
    'kept_units_below_minimum':
        ('joulewise/floor_extraction.py', 'refusals.append("kept_units_below_minimum")', MINIMUM_RULE),
    'insufficient_members_after_exclusion':
        ('joulewise/floor_extraction.py', 'refusals.append("insufficient_members_after_exclusion")', MINIMUM_RULE),
    'insufficient_in_window_samples':
        ('joulewise/reduce.py', 'reasons.append("insufficient_in_window_samples")', MEMBER_RULE),
    'cadence_ratio_below_threshold':
        ('joulewise/reduce.py', 'reasons.append("cadence_ratio_below_threshold")', MEMBER_RULE),
    'clock_bound_exceeds_quarter_window':
        ('joulewise/reduce.py', 'reasons.append("clock_bound_exceeds_quarter_window")', MEMBER_RULE),
    'anchor_energy_envelope_exceeds_quarter_metric':
        ('joulewise/reduce.py', 'return ["anchor_energy_envelope_exceeds_quarter_metric"]', MEMBER_RULE),
    'instrument_calibration_stale':
        ('joulewise/reduce.py', 'return None, "instrument_calibration_stale"', MEMBER_RULE),
    'calibration_acceptance_bound_stale':
        ('joulewise/calibration_bracketing.py', 'return finish(("calibration_acceptance_bound_stale",))', MEMBER_RULE),
    # L9-STEP4-4: the bullet's own member-level codes that the precheck emits; the
    # extractor extends every member's reasons with them (floor_extraction.py, only
    # cooldown_cap_hit is filtered).
    'window_evidence_precheck_missing':
        ('joulewise/analysis_engine/inputs.py', 'reasons.append("window_evidence_precheck_missing")', MEMBER_RULE),
    'campaign_cooldown_evidence_missing':
        ('joulewise/analysis_engine/inputs.py', 'reasons.append("campaign_cooldown_evidence_missing")', MEMBER_RULE),
    'idle_window_suspect':
        ('joulewise/analysis_engine/inputs.py', 'reasons.append("idle_window_suspect")', MEMBER_RULE),
}
# The member-level codes plan 2.2 bullet 3 names literally that reach an extractor cell.
PLAN_NAMED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect'}
# The bullet's claim-gate codes: never in an extractor cell, so never R3 at step 4.
CLAIM_GATE_ONLY = ('paired_block_incomplete', 'fixed_n_plan_incomplete')
# Every member-rule code the window-evidence precheck forwards onto kept units (Fable F2, L9-STEP4-4 F1).
FORWARDED_PRECHECK = {code for code, pin in R3_PINS.items() if pin[2] is MEMBER_RULE}


class Step4ReasonTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = TABLE.read_bytes()
        cls.table = json.loads(cls.raw)

    def test_R1_table_shape_is_sorted_disjoint_and_pins_its_source(self):
        table = self.table
        self.assertEqual(list(table), ['schema_version', 'source', 'modules', 'mask_rule', 'mask', 'tooling',
                                       'r3', 'step4_rule'])
        self.assertEqual(table['schema_version'], 'joulewise.b5_step4_reason_classes.v2')
        self.assertEqual(table['source']['commit'], '08ea5c95849654c066811273807f9ca6bf5327cf')
        for name in ('mask', 'tooling', 'r3'):
            self.assertEqual(table[name], sorted(set(table[name])))
            self.assertTrue(all(type(code) is str and code for code in table[name]))
        self.assertFalse(set(table['mask']) & set(table['tooling']))
        self.assertEqual((len(table['mask']), len(table['tooling'])), (42, 1898))

    def test_R1_generator_copy_is_the_committed_blind_generator(self):
        digest = hashlib.sha256(GENERATOR.read_bytes()).hexdigest()
        self.assertEqual(digest, self.table['source']['generator_sha256'])
        self.assertEqual(digest, '051c13b267c747f3c4bf88318c819bcb9c5c603ba608160ca04389e817a549d2')

    def test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file(self):
        run = subprocess.run([sys.executable, '-I', str(GENERATOR), str(ROOT)],
                             capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 0, run.stderr)
        fresh = json.loads(run.stdout)
        self.assertEqual(set(fresh), {'modules', 'mask_rule', 'mask', 'tooling'})
        expected = {**HEADER, **{key: fresh[key] for key in ('modules', 'mask_rule', 'mask', 'tooling')}, **RULING}
        self.assertEqual(self.table, expected)
        self.assertEqual(self.raw, (json.dumps(expected, indent=1) + '\n').encode())

    def test_R3_list_is_read_by_the_classifier_and_is_mask_codes_plus_plan_named_codes(self):
        self.assertEqual(steps.step4_r3_reasons(), frozenset(RULING['r3']))
        self.assertEqual(set(R3_PINS), set(RULING['r3']))
        # L9-STEP4-4 invariant: r3 is the blind MASK codes the ruling routes to R3 plus the
        # three plan-named member codes, which are blind tooling codes pinned to the
        # precheck and the member rule. No outcome; nothing else moves out of tooling.
        mask, tooling = set(self.table['mask']), set(self.table['tooling'])
        self.assertEqual(set(RULING['r3']) - mask, PLAN_NAMED)
        self.assertLessEqual(PLAN_NAMED, tooling)
        plan = ' '.join(PLAN.read_text().split())
        bullet = plan[plan.index('- Nothing else excludes a member'):plan.index('- **p42.**')]
        self.assertIn(MEMBER_RULE, bullet)
        for code in PLAN_NAMED:
            with self.subTest(code=code):
                self.assertEqual(R3_PINS[code][:1] + R3_PINS[code][2:],
                                 ('joulewise/analysis_engine/inputs.py', MEMBER_RULE))
                self.assertIn('`%s`' % code, bullet)
        for code in CLAIM_GATE_ONLY:
            with self.subTest(code=code):
                self.assertIn('`%s`' % code, bullet)
                self.assertNotIn(code, RULING['r3'])

    def test_R3_step4_rule_names_the_classifier_codes_and_they_are_registered(self):
        rule = self.table['step4_rule']
        self.assertEqual(rule['refused_cells_only_p42'], steps.STEP4_P42_FLOOR_CELLS_ONLY)
        self.assertEqual(rule['refused_non_p42_cell_without_reasons'], steps.STEP4_REPORT_MALFORMED)
        self.assertEqual(rule['any_r3_reason_on_a_refused_non_p42_cell'], steps.STEP4_CELL_R3_REFUSAL)
        self.assertEqual(rule['otherwise'], steps.STEP4_CELL_TOOLING_REFUSAL)
        classes = d.refusal_classes()
        for code in (steps.STEP4_REPORT_MALFORMED, steps.STEP4_CELL_R3_REFUSAL, steps.STEP4_CELL_TOOLING_REFUSAL):
            self.assertIn(code, classes['tooling_refusal'])
        self.assertFalse(hasattr(steps, 'STEP4_FLOOR_CELL_NOT_EXTRACTABLE'))

    def test_R3_each_code_is_pinned_to_its_producer_emission_site_and_plan_line(self):
        plan = ' '.join(PLAN.read_text().split())
        section = plan[plan.index('### 2.2 Members and units'):plan.index('### 2.3 ')]
        for code, (module, emission, sentence) in R3_PINS.items():
            with self.subTest(code=code):
                self.assertIn(code, emission)
                self.assertIn(emission, (ROOT / module).read_text())
                self.assertIn(sentence, section)

    def test_R3_forwarded_precheck_codes_are_exactly_the_blind_mask_reducer_codes(self):
        from joulewise.analysis_engine.claims import REDUCER_REASON_CODES
        self.assertEqual(len(FORWARDED_PRECHECK), 9)
        self.assertEqual(set(self.table['mask']) & REDUCER_REASON_CODES, FORWARDED_PRECHECK - PLAN_NAMED)
        # The plan-named codes are the precheck's own, not reducer vocabulary.
        self.assertFalse(PLAN_NAMED & REDUCER_REASON_CODES)
        # The window-evidence precheck forwards reducer reasons onto the cell's members.
        inputs = (ROOT / 'joulewise/analysis_engine/inputs.py').read_text()
        self.assertRegex(inputs, re.compile(r'def window_evidence_precheck\b'))

    def test_R3_claim_gate_member_codes_cannot_reach_a_step4_cell(self):
        # The precheck forwards only reducer vocabulary (anything else becomes
        # window_evidence_precheck_missing), and in the eleven extractor modules these
        # literals occur only as the code argument of a kept-unit stop, which raises
        # member_code_on_kept_unit (exit 2) instead of entering a cell's reasons.
        import ast
        from joulewise.analysis_engine.claims import REDUCER_REASON_CODES
        self.assertFalse(set(CLAIM_GATE_ONLY) & REDUCER_REASON_CODES)
        self.assertFalse(set(CLAIM_GATE_ONLY) & set(self.table['mask']))
        seen = {code: 0 for code in CLAIM_GATE_ONLY}
        for module in self.table['modules']:
            tree = ast.parse((ROOT / module).read_text())
            stop_args = {id(call.args[2]) for call in ast.walk(tree)
                         if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                         and call.func.attr == 'stop_if_member_code_on_kept_unit' and len(call.args) >= 3}
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and node.value in seen:
                    seen[node.value] += 1
                    with self.subTest(module=module, code=node.value, line=node.lineno):
                        self.assertIn(id(node), stop_args)
        self.assertEqual(seen['fixed_n_plan_incomplete'], 0)


if __name__ == '__main__':
    unittest.main()
