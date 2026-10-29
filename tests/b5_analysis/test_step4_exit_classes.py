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


def report(refused=(), **changes):
    value = {'spec_membership_refusals': [],
             'cells': [{'cell_id': c['cell_id'], 'extractable': c['cell_id'] not in refused} for c in SPEC['cells']]}
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

    def test_S2_a_non_p42_floor_cell_not_extractable_is_an_outcome_class(self):
        for refused in (('syn-target',), ('syn-cmp',), ('syn-target', *P42)):
            with self.subTest(refused=refused):
                self.assertClass(report(refused), 'floor_cell_not_extractable', 'outcome_class')
        self.assertIn('floor_cell_not_extractable', d.refusal_classes()['outcome_class'])

    def test_S2_p42_floor_cells_are_absolute_or_comparative_cells_of_the_p42_family_token(self):
        spec = copy.deepcopy(SPEC)
        spec['cells'] += [{'cell_id': 'syn-p42-reported', 'kind': 'reported', 'condition_family_id': 'cell-p42'},
                          {'cell_id': 'syn-p420', 'kind': 'absolute', 'condition_family_id': 'cell-p420'}]
        for refused in (('syn-p42-reported',), ('syn-p420',), ('syn-p420', *P42)):
            with self.subTest(refused=refused):
                rep = {'spec_membership_refusals': [], 'cells': [
                    {'cell_id': c['cell_id'], 'extractable': c['cell_id'] not in refused} for c in spec['cells']]}
                self.assertClass(rep, 'floor_cell_not_extractable', 'outcome_class', spec)

    def test_S2_a_refused_cell_in_a_spec_without_p42_cells_is_an_outcome_class(self):
        spec = {'cells': SPEC['cells'][:2]}
        rep = {'spec_membership_refusals': [],
               'cells': [{'cell_id': 'syn-target', 'extractable': False}, {'cell_id': 'syn-cmp', 'extractable': True}]}
        self.assertClass(rep, 'floor_cell_not_extractable', 'outcome_class', spec)

    def test_S3_spec_membership_refusal_is_tooling(self):
        for refused in ((), P42, ('syn-target',)):
            with self.subTest(refused=refused):
                self.assertClass(report(refused, spec_membership_refusals=[{'bundle_id': 'syn-bundle'}]),
                                 'extraction_spec_membership_refused', 'tooling_refusal')

    def test_S3_cell_set_mismatch_is_tooling(self):
        missing = report(P42);missing['cells'].pop(0)
        extra = report(P42);extra['cells'].append({'cell_id': 'syn-extra', 'extractable': True})
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
        self.assertEqual(len(codes), 9)
        for code in codes - {'p42_floor_cells_only'}:
            with self.subTest(code=code):
                self.assertIn(code, classes['tooling_refusal'] + classes['outcome_class'])
                self.assertIsNotNone(d._TOKEN.fullmatch(code))


if __name__ == '__main__':
    unittest.main()
