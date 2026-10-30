"""L9-STEP4-1: every step-4 exit names a registered class (plan section 3.1).

Synthetic specs and reports only. Each branch below returned the bare
"refused" at 49991c73a, which the step record could only show as
unclassified_refusal.
"""
import copy
import unittest

from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.steps import classify_step4_exit, step_record

SPEC = {'cells': [
    {'cell_id': 'syn-target', 'kind': 'absolute', 'condition_family_id': 'cell-target'},
    {'cell_id': 'syn-cmp', 'kind': 'comparative', 'condition_family_id': 'cell-target'},
    {'cell_id': 'syn-p42-abs', 'kind': 'absolute', 'condition_family_id': 'cell-p42'},
    {'cell_id': 'syn-p42-cmp', 'kind': 'comparative', 'condition_family_id': 'cell-p42-x'}]}
P42 = ('syn-p42-abs', 'syn-p42-cmp')


# Synthetic picks from configs/analysis/b5/step4_reason_classes.json (L9-STEP4-2):
# a blind-mask code that is not R3, a tooling code, an unlisted code and an R3 code.
MASK = 'insufficient_idle_samples'
TOOLING = 'marker_self_digest_mismatch'
UNLISTED = 'syn_reason_in_neither_list'
R3 = 'kept_units_below_minimum'
R3_CODES = ('anchor_energy_envelope_exceeds_quarter_metric', 'cadence_ratio_below_threshold',
            'calibration_acceptance_bound_stale', 'campaign_cooldown_evidence_missing',
            'clock_bound_exceeds_quarter_window', 'idle_window_suspect',
            'insufficient_in_window_samples', 'insufficient_members_after_exclusion',
            'instrument_calibration_stale', 'kept_units_below_minimum', 'window_evidence_precheck_missing')
# The plan section 2.2 bullet 3 member codes the L9-STEP4-4 ruling moved to R3.
PLAN_NAMED = ('window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect')


def cell(cell_id, refused, reasons=(MASK,)):
    return {'cell_id': cell_id, 'extractable': not refused,
            'refusal_reasons': list(reasons) if refused else [], 'floor': None}


def report(refused=(), reasons=None, **changes):
    """Refused cells carry a non-R3 mask reason unless `reasons` maps a cell id to its own."""
    reasons = reasons or {}
    value = {'spec_membership_refusals': [],
             'cells': [cell(c['cell_id'], c['cell_id'] in refused, reasons.get(c['cell_id'], (MASK,)))
                       for c in SPEC['cells']]}
    value.update(changes)
    return value


def record(code):
    """The step record the driver writes when it passes the class through."""
    registered = code if code == 'p42_floor_cells_only' else None
    return step_record('4', window='alpha', exit_status=1, classes=d.refusal_classes(),
                       refusal_code=None if registered else code, registered_exit=registered)


class Step4ExitClassTests(unittest.TestCase):
    def assertClass(self, rep, code, status, spec=SPEC):
        self.assertEqual(classify_step4_exit(1, rep, spec), code)
        row = record(code)
        self.assertEqual(row.status, status)
        self.assertNotEqual(row.status, 'unclassified_refusal')
        if status == 'tooling_refusal':
            self.assertEqual(row.refusal, code)
        if status == 'outcome_class':
            self.assertEqual(row.refusal, 'outcome-class refusal at step 4')

    def test_S1_every_p42_floor_cell_refused_is_the_registered_exit(self):
        self.assertClass(report(P42), 'p42_floor_cells_only', 'ok')
        self.assertEqual(record('p42_floor_cells_only').registered_exit, 'p42_floor_cells_only')

    def test_S1_a_nonempty_subset_of_p42_floor_cells_is_the_registered_exit(self):
        for refused in ((P42[0],), (P42[1],)):
            with self.subTest(refused=refused):
                self.assertClass(report(refused), 'p42_floor_cells_only', 'ok')

    def test_S2_a_refused_non_p42_floor_cell_is_a_stop_never_an_outcome(self):
        # L9-STEP4-3: floor_cell_not_extractable (outcome_class) at 8222d0e47 for these mask-only reports.
        for refused in (('syn-target',), ('syn-cmp',), ('syn-target', *P42)):
            with self.subTest(refused=refused):
                self.assertClass(report(refused), 'extraction_cell_tooling_refusal', 'tooling_refusal')
        classes = d.refusal_classes()
        self.assertNotIn('floor_cell_not_extractable', classes['tooling_refusal'] + classes['outcome_class'])

    def test_S2_p42_floor_cells_are_absolute_or_comparative_cells_of_the_p42_family_token(self):
        spec = copy.deepcopy(SPEC)
        spec['cells'] += [{'cell_id': 'syn-p42-reported', 'kind': 'reported', 'condition_family_id': 'cell-p42'},
                          {'cell_id': 'syn-p420', 'kind': 'absolute', 'condition_family_id': 'cell-p420'}]
        for refused in (('syn-p42-reported',), ('syn-p420',), ('syn-p420', *P42)):
            with self.subTest(refused=refused):
                rep = {'spec_membership_refusals': [],
                       'cells': [cell(c['cell_id'], c['cell_id'] in refused) for c in spec['cells']]}
                self.assertClass(rep, 'extraction_cell_tooling_refusal', 'tooling_refusal', spec)

    def test_S2_a_refused_cell_in_a_spec_without_p42_cells_is_a_stop(self):
        spec = {'cells': SPEC['cells'][:2]}
        rep = {'spec_membership_refusals': [],
               'cells': [cell('syn-target', True), cell('syn-cmp', False)]}
        self.assertClass(rep, 'extraction_cell_tooling_refusal', 'tooling_refusal', spec)

    def test_S3_spec_membership_refusal_is_tooling(self):
        for refused in ((), P42, ('syn-target',)):
            with self.subTest(refused=refused):
                self.assertClass(report(refused, spec_membership_refusals=[{'bundle_id': 'syn-bundle'}]),
                                 'extraction_spec_membership_refused', 'tooling_refusal')

    def test_S3_cell_set_mismatch_is_tooling(self):
        missing = report(P42);missing['cells'].pop(0)
        extra = report(P42);extra['cells'].append(cell('syn-extra', False))
        for rep in (missing, extra):
            with self.subTest(cells=len(rep['cells'])):
                self.assertClass(rep, 'extraction_cell_set_differs_from_spec', 'tooling_refusal')

    def test_S3_duplicate_ids_are_tooling(self):
        rep = report(P42);rep['cells'].append(dict(rep['cells'][0]))
        self.assertClass(rep, 'extraction_cell_ids_duplicated', 'tooling_refusal')
        spec = copy.deepcopy(SPEC);spec['cells'].append(dict(spec['cells'][0]))
        self.assertClass(report(P42), 'extraction_cell_ids_duplicated', 'tooling_refusal', spec)

    def test_S3_malformed_report_or_cells_are_tooling(self):
        bad_cell = report(P42);bad_cell['cells'][0] = 'syn-target'
        empty_id = report(P42);empty_id['cells'][0]['cell_id'] = ''
        for rep in (None, [], report(P42, cells={}), report(P42, cells=None), bad_cell, empty_id,
                    {'cells': report(P42)['cells']}, report(P42, spec_membership_refusals=None)):
            with self.subTest(report=rep):
                self.assertClass(rep, 'extraction_report_malformed', 'tooling_refusal')

    def test_S3_malformed_spec_is_tooling(self):
        no_kind = copy.deepcopy(SPEC);del no_kind['cells'][0]['kind']
        no_family = copy.deepcopy(SPEC);no_family['cells'][2]['condition_family_id'] = None
        for spec in (None, {}, {'cells': {}}, no_kind, no_family):
            with self.subTest(spec=spec):
                self.assertClass(report(P42), 'extraction_spec_malformed', 'tooling_refusal', spec)

    def test_S3_non_boolean_extractable_is_tooling(self):
        for value in (None, 0, 'false'):
            rep = report(P42);rep['cells'][2]['extractable'] = value
            with self.subTest(value=value):
                self.assertClass(rep, 'extraction_extractable_not_boolean', 'tooling_refusal')

    def test_S3_exit_1_with_no_refused_cell_is_tooling(self):
        self.assertClass(report(), 'extraction_exit_without_refused_cell', 'tooling_refusal')

    def test_S3_other_exit_statuses_keep_their_handling(self):
        self.assertEqual(classify_step4_exit(0, report(), SPEC), 'ok')
        for rep, spec in ((None, SPEC), ([], SPEC), (report(), None), (report(), [])):
            with self.subTest(report=rep, spec=spec):
                self.assertEqual(classify_step4_exit(0, rep, spec), 'refused')
        for status in (2, 3, -1, True, None, '1'):
            with self.subTest(status=status):
                self.assertEqual(classify_step4_exit(status, report(P42), SPEC), 'refused')

    def test_every_returned_code_is_registered(self):
        from joulewise.b5_analysis import steps
        classes = d.refusal_classes()
        codes = {getattr(steps, name) for name in dir(steps) if name.startswith('STEP4_')}
        self.assertEqual(len(codes), 10)
        for code in codes - {'p42_floor_cells_only'}:
            with self.subTest(code=code):
                self.assertIn(code, classes['tooling_refusal'] + classes['outcome_class'])
                self.assertIsNotNone(d._TOKEN.fullmatch(code))



class Step4ReasonClassTests(unittest.TestCase):
    """L9-STEP4-3 ruling: every refused non-p42 cell is a stop, named by its reasons' class.

    At 8222d0e47 the mask-only cases below returned floor_cell_not_extractable
    (outcome_class), and extraction_cell_r3_refusal did not exist.
    """
    assertClass = Step4ExitClassTests.assertClass

    def test_R2_tooling_only_reasons_are_a_tooling_refusal(self):
        # L9-STEP4-4: window_evidence_precheck_missing moved to R3; its unknown-state sibling
        # and the same-slot cooldown-cap code stay tooling.
        for reasons in ((TOOLING,), (TOOLING, 'content_digest'), ('idle_window_suspect_unknown',),
                        ('cooldown_cap_hit',)):
            with self.subTest(reasons=reasons):
                rep = report(('syn-target',), {'syn-target': reasons})
                self.assertClass(rep, 'extraction_cell_tooling_refusal', 'tooling_refusal')

    def test_R2_blind_mask_codes_outside_r3_are_a_tooling_refusal(self):
        # Fable F3/F4 and Opus F3: reachable mask codes that are not R3 are tooling.
        for reasons in ((MASK,), ('cell_stale',), ('admissible_set_uncertainty_dominates_point_floor',),
                        ('calibration_bracket_exceeds_minted_bound',), ('sensitivity_bound_below_operative',),
                        ('numeric_padding_insufficient', 'proposal_count_exceeds_configured_cap')):
            with self.subTest(reasons=reasons):
                rep = report(('syn-target',), {'syn-target': reasons})
                self.assertClass(rep, 'extraction_cell_tooling_refusal', 'tooling_refusal')

    def test_R2_r3_only_reasons_are_an_r3_refusal(self):
        for code in R3_CODES:
            with self.subTest(code=code):
                self.assertClass(report(('syn-target',), {'syn-target': (code,)}),
                                 'extraction_cell_r3_refusal', 'tooling_refusal')
        rep = report(('syn-target', 'syn-cmp'), {'syn-target': R3_CODES, 'syn-cmp': (R3,)})
        self.assertClass(rep, 'extraction_cell_r3_refusal', 'tooling_refusal')

    def test_R2_plan_named_member_codes_are_r3_and_claim_gate_codes_are_not(self):
        # L9-STEP4-4 counterfactual: each of these three gave extraction_cell_tooling_refusal
        # at 901956944; the claim-gate codes never reach a cell and stay out of R3.
        for code in PLAN_NAMED:
            with self.subTest(code=code):
                self.assertClass(report(('syn-target',), {'syn-target': (code,)}),
                                 'extraction_cell_r3_refusal', 'tooling_refusal')
        for code in ('paired_block_incomplete', 'fixed_n_plan_incomplete'):
            with self.subTest(code=code):
                self.assertClass(report(('syn-target',), {'syn-target': (code,)}),
                                 'extraction_cell_tooling_refusal', 'tooling_refusal')

    def test_R2_r3_takes_precedence_over_tooling_on_any_refused_non_p42_cell(self):
        for refused, reasons in ((('syn-target',), {'syn-target': (TOOLING, R3)}),
                                 (('syn-target',), {'syn-target': (UNLISTED, MASK, 'cadence_ratio_below_threshold')}),
                                 (('syn-target', 'syn-cmp'), {'syn-target': (TOOLING,), 'syn-cmp': (R3,)}),
                                 (('syn-target', 'syn-cmp'), {'syn-target': (R3,), 'syn-cmp': (UNLISTED,)}),
                                 (('syn-target', *P42), {'syn-target': (TOOLING, 'instrument_calibration_stale')})):
            with self.subTest(refused=refused, reasons=reasons):
                self.assertClass(report(refused, reasons), 'extraction_cell_r3_refusal', 'tooling_refusal')

    def test_R2_an_r3_code_on_a_p42_cell_does_not_make_a_target_refusal_r3(self):
        rep = report(('syn-target', *P42), {'syn-target': (TOOLING,), P42[0]: (R3,), P42[1]: (R3,)})
        self.assertClass(rep, 'extraction_cell_tooling_refusal', 'tooling_refusal')

    def test_R2_an_unclassified_reason_is_a_tooling_refusal(self):
        for reasons in ((UNLISTED,), (MASK, UNLISTED), ('',), (R3 + ' ',), (R3.upper(),)):
            with self.subTest(reasons=reasons):
                rep = report(('syn-target',), {'syn-target': reasons})
                self.assertClass(rep, 'extraction_cell_tooling_refusal', 'tooling_refusal')

    def test_R2_a_refused_non_p42_cell_without_reasons_is_a_malformed_report(self):
        # At 8222d0e47 an empty list with floor null was floor_cell_not_extractable (outcome_class).
        rep = report(('syn-target',), {'syn-target': ()})
        with_floor = copy.deepcopy(rep);with_floor['cells'][0]['floor'] = {'guarded_floor_j': None}
        no_floor_key = copy.deepcopy(rep);del no_floor_key['cells'][0]['floor']
        beside_r3 = report(('syn-target', 'syn-cmp'), {'syn-target': (R3,), 'syn-cmp': ()})
        for bad in (rep, with_floor, no_floor_key, beside_r3):
            with self.subTest(cells=bad['cells'][:2]):
                self.assertClass(bad, 'extraction_report_malformed', 'tooling_refusal')

    def test_R2_p42_cell_reasons_are_irrelevant_to_the_registered_exit(self):
        # L9-STEP4-5 (Opus F5): the plan-named R3 codes on p42 cells change nothing either.
        for reasons in ((TOOLING,), (UNLISTED,), (MASK, TOOLING), (R3,), (R3, TOOLING), (),
                        *((code,) for code in PLAN_NAMED), PLAN_NAMED + (TOOLING,)):
            with self.subTest(reasons=reasons):
                rep = report(P42, {P42[0]: reasons, P42[1]: reasons})
                self.assertClass(rep, 'p42_floor_cells_only', 'ok')

    def test_R2_malformed_refusal_reasons_are_a_malformed_report(self):
        for target in ('syn-target', P42[0]):
            for value in ('missing', None, MASK, (MASK,), {MASK: True}, [None], [1], [[MASK]]):
                rep = report((target, *P42))
                row = next(c for c in rep['cells'] if c['cell_id'] == target)
                if value == 'missing':del row['refusal_reasons']
                else:row['refusal_reasons'] = value
                with self.subTest(cell=target, value=value):
                    self.assertClass(rep, 'extraction_report_malformed', 'tooling_refusal')
        # An extractable cell's reasons are not read.
        rep = report(P42);del rep['cells'][0]['refusal_reasons']
        self.assertClass(rep, 'p42_floor_cells_only', 'ok')

    def test_R2_new_codes_are_registered_tooling_only(self):
        classes = d.refusal_classes()
        for code in ('extraction_cell_tooling_refusal', 'extraction_cell_r3_refusal'):
            with self.subTest(code=code):
                self.assertIn(code, classes['tooling_refusal'])
                self.assertNotIn(code, classes['outcome_class'])

    def test_R2_no_step4_exit_1_report_is_an_outcome_class(self):
        reports = [report(refused, {c: reasons for c in refused})
                   for refused in (('syn-target',), ('syn-cmp',), ('syn-target', *P42))
                   for reasons in ((MASK,), (TOOLING,), (UNLISTED,), (R3,), ())]
        for rep in reports:
            with self.subTest(report=rep['cells']):
                code = classify_step4_exit(1, rep, SPEC)
                self.assertNotEqual(record(code).status, 'outcome_class')


if __name__ == '__main__':
    unittest.main()
