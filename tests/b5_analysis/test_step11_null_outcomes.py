"""D-190: step 11 carries a registered not-resolvable or not-estimable contrast as null.

Synthetic only. Each case runs the real code that step 11 runs: the sensitivity pass
(sensitivity_pass, with the real engine composition behind its arithmetic seams), the
disclosures producer (produce_disclosures) and the results-fill adapter
(adapt_claim_verdicts). The verdicts have the shapes the engine writes in each state
that step 9b calls not issuable (D-189). Before D-190, the sensitivity pass refused a
refused floor or a null D with sensitivity_inputs_invalid. The disclosures refused a
null interval or floor with disclosure_input_invalid. Neither code is registered, so
step 11 became an unclassified refusal. The anchor-missing state reached neither path,
so step 11's public status also told the states apart (review of PR #642).
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import unittest
from unittest import mock

from joulewise import analysis_engine as engine
from joulewise.analysis_engine.claim_side_bound import ClaimSideBoundRefusal, produce_claim_side_bound
from joulewise.analysis_engine.inputs import unavailable_floor_resolution
from joulewise.b5_analysis import disclosures as d
from joulewise.b5_analysis import sensitivity as sensitivity_module
from joulewise.b5_analysis.dry_run import claim_side_bound_not_issuable
from joulewise.b5_analysis.kept_units import CellKeptUnits, DroppedUnit, Unit
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s5 as s5
from tests.b5_analysis.test_disclosures import Harness, items
from tests.b5_analysis.test_sensitivity import EXAMPLE, PassHarness, pass_fixture

ANCHOR = 'E_clock_anchor_shift_bound_j'
LEGIT_PRODUCER_CODES = {'paper_claim_side_bound_cell_mismatch', 'paper_claim_side_bound_shape_invalid',
                        'paper_claim_side_bound_anchor_missing'}


class RefusedFloor(PassHarness):
    """The second floor resolution is refused, as the engine writes it (source cells kept)."""
    def resolutions(self):
        rows = super().resolutions()
        return [rows[0], replace(rows[1], status='refused', floor_abs_j=None, floor_cmp_j=None,
                                 floor_gate_j=None, reason_codes=('cell_missing',))]


class UnavailableFloor(PassHarness):
    """inputs.unavailable_floor_resolution: refused, with no source cell."""
    def resolutions(self):
        return [super().resolutions()[0],
                unavailable_floor_resolution({'artifact_id': 'synthetic-floor'}, 'a' * 64)]


class NotEstimable(PassHarness):
    """One complete block per contrast: the engine writes no estimate (n < 2)."""
    def __init__(self):
        base = pass_fixture()
        loaded = s5.arithmetic_inputs(EXAMPLE, removed=tuple(range(2, len(EXAMPLE) + 1)))
        super().__init__()
        self.f.loaded = loaded
        self.f.kept = {**self.f.kept, 'gamma': replace(loaded.kept_units, window=base.windows['gamma'])}
        self.primary = self.primary_verdicts()


class NoAnchor(PassHarness):
    def math(self, D):
        stack = super().math(D)
        stack.enter_context(mock.patch.object(engine, 'deterministic_bounds',
                                              return_value=({'E_interpolation_joint_edge_bound_j': D}, ())))
        return stack


class NoTerms(PassHarness):
    def math(self, D):
        stack = super().math(D)
        stack.enter_context(mock.patch.object(engine, 'deterministic_bounds', return_value=({}, ())))
        return stack


STATES = {'refused_floor': RefusedFloor, 'unavailable_floor': UnavailableFloor,
          'not_estimable': NotEstimable, 'no_anchor_term': NoAnchor, 'no_deterministic_terms': NoTerms}


def _parents(harness):
    manifest = {'contrasts': [{'contrast_id': row['contrast_id']} for row in harness.primary['contrasts']]}
    floor = {'artifact_id': 'synthetic-floor', 'cells': [{'cell_id': c['cell_id']} for c in harness.f.artifact['cells']]}
    return manifest, floor


def _raw(verdicts):
    return json.dumps(verdicts, allow_nan=False, sort_keys=True).encode()


class SensitivityPassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass_fixture()

    def test_every_non_issuable_state_completes_the_real_sensitivity_pass(self):
        for state, harness_class in STATES.items():
            with self.subTest(state):
                h = harness_class()
                raw = _raw(h.primary)
                manifest, floor = _parents(h)
                # Step 9b calls exactly this verdict not issuable, and the producer agrees.
                self.assertTrue(claim_side_bound_not_issuable(raw, finalized_manifest=manifest, floor_artifact=floor))
                with self.assertRaises(ClaimSideBoundRefusal) as refusal:
                    produce_claim_side_bound(raw, finalized_manifest=manifest, floor_artifact=floor)
                self.assertIn(refusal.exception.code, LEGIT_PRODUCER_CODES)
                record = h.call()
                self.assertEqual(len(record['contrasts']), 2)
                for row in record['contrasts']:
                    floors = [row[side][key] for side in ('primary', 'sensitivity')
                              for key in ('floor_abs_j', 'floor_cmp_j', 'floor_gate_j')]
                    D = [row[side]['D_j'] for side in ('primary', 'sensitivity')]
                    if state in ('refused_floor', 'unavailable_floor'):
                        self.assertEqual(floors, [None] * 6)
                        self.assertEqual(row['primary']['outcome'], 'not_resolvable')
                        # Only the usable resolution's cell is a sensitivity floor cell.
                        self.assertEqual(row['floor_cell_ids'], ['minted-alpha'])
                    else:
                        self.assertTrue(all(type(value) is float for value in floors))
                    if state == 'not_estimable':
                        self.assertEqual(D, [None, None])
                        self.assertEqual(row['primary']['outcome'], 'not_estimable')
                    else:
                        self.assertTrue(all(type(value) is float for value in D))
                    self.assertTrue(row['not_below_primary'])
                    self.assertTrue(row['outcome_equals_primary'])
                sensitivity_module.to_structure_record(record)
                # The disclosures accept the record as written (null on both sides).
                d._validate_sensitivity(record)

    def test_issuable_records_are_unchanged(self):
        # Every resolution usable and an estimate present: the same keys, numbers and cells.
        record = PassHarness().call()
        for row in record['contrasts']:
            self.assertEqual(row['floor_cell_ids'], ['minted-alpha', 'minted-beta'])
            for side in ('primary', 'sensitivity'):
                self.assertTrue(all(type(row[side][key]) is float
                                    for key in ('floor_abs_j', 'floor_cmp_j', 'floor_gate_j', 'D_j')))

    def test_a_null_outside_the_registered_states_still_refuses(self):
        def call(harness, edit):
            primary = deepcopy(harness.primary)
            edit(primary['contrasts'][0])
            return harness.call(primary_claim_verdicts=primary)
        cases = {
            # A refused floor never carries a value (engine._combined_floor).
            'refused_floor_with_a_value': (RefusedFloor, lambda row: row['floor'].update(active_floor_j=1.25)),
            # A resolved floor always carries one.
            'resolved_floor_without_a_value': (PassHarness, lambda row: row['floor'].update(active_floor_j=None)),
            # D is null only without an estimate.
            'estimate_without_D': (PassHarness, lambda row: row['deterministic_bounds'].update(total=None)),
        }
        for name, (harness_class, edit) in cases.items():
            with self.subTest(name), self.assertRaisesRegex(AnalysisRefusal, '^sensitivity_inputs_invalid$'):
                call(harness_class(), edit)

    def test_whether_a_floor_resolves_does_not_depend_on_the_bound(self):
        refused = RefusedFloor()
        resolved = PassHarness()
        for primary, harness in ((refused.primary, resolved), (resolved.primary, refused)):
            with self.subTest(primary=primary['contrasts'][0]['floor']['status']), \
                 self.assertRaisesRegex(AnalysisRefusal, '^sensitivity_changed_bound_independent_value$'):
                harness.call(primary_claim_verdicts=primary)


def _add_not_estimable(h, *, cid='decode', kept=1, floor=None):
    """A gamma contrast keeping `kept` quads, with the engine's not-estimable verdict row."""
    ds = (3.1, 2.9, 3.3, 3., 2.8, 3.2, 3.1, 2.9, 3., 2.7)
    units, dropped, rows = [], [], []
    for n, delta in enumerate(ds, 1):
        bid = f'{cid}-b{n:02d}'
        unit = Unit(cid, 'quad', bid, tuple(bid + '-' + p for p in ('A1', 'B1', 'B2', 'A2')),
                    tuple(range(4 * n - 3, 4 * n + 1)), ('science',) * 4)
        if n > kept:
            dropped.append(DroppedUnit(**unit.__dict__, codes=('member.admission_aborted',),
                                       families=('MEMBER_VALIDITY',)))
        else:
            units.append(unit)
        rows.append({'block_id': bid, 'a_mean_j': 10., 'b_mean_j': 10. + delta, 'd_j': delta})
    cell = CellKeptUnits(cid, True, {'quad': len(ds)}, {'quad': 5}, {'quad': tuple(units)}, tuple(dropped), 0, len(units))
    h.kept['gamma'] = replace(h.kept['gamma'], cells={**h.kept['gamma'].cells, cid: cell})
    h.observations[cid] = rows
    h.verdicts['contrasts'].append({
        'contrast_id': cid, 'estimator': engine._empty_estimator('abba_block_arm_mean_difference_t_v1', kept),
        'deterministic_bounds': {'terms': [], 'total': None, 'decision_interval': None},
        'floor': floor or {'status': 'resolved', 'active_floor_j': 1.2}, 'loo': {'rows': []}})


def _refused_floor():
    return engine._combined_floor([unavailable_floor_resolution({'artifact_id': 'synthetic-floor'}, 'a' * 64)])


class DisclosuresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass_fixture()
        cls.records = {state: harness().call() for state, harness in STATES.items()}

    def lines(self, record, line):
        return [row['text'] for row in items(record, 'contrasts', line)]

    def test_a_refused_floor_prints_as_not_resolvable(self):
        h = Harness(); h.add_contrast(); h.sens = deepcopy(self.records['refused_floor'])
        h.verdicts['contrasts'][0]['floor'] = _refused_floor()
        record = h.produce()
        self.assertEqual(self.lines(record, 'decision_floor'),
                         [t for t in self.lines(record, 'decision_floor') if t.endswith('; floor not resolvable')])
        self.assertEqual(len(self.lines(record, 'decision_floor')), 1)
        self.assertIsNone(items(record, 'contrasts', 'decision_floor')[0]['floor_j'])
        text = d.render_disclosures(record, released=True)
        self.assertNotIn(d.DECISION_SENTENCE, text)
        self.assertIn('floor_gate_j not available', text)
        # The estimate and its intervals are printed as before.
        self.assertIn('J per output token; metrology interval', text)
        self.assertIn('rounded t* (2.306 for 2.306004)', text)

    def test_a_not_estimable_contrast_prints_as_itself(self):
        for kept in (0, 1):
            with self.subTest(kept=kept):
                h = Harness(); _add_not_estimable(h, kept=kept); h.sens = deepcopy(self.records['not_estimable'])
                record = h.produce()
                self.assertEqual(self.lines(record, 'primary_contrast'),
                                 [f'decode: not estimable (n = {kept}; fewer than 2 complete quads)'])
                self.assertEqual(self.lines(record, 'magnitude_per_token'),
                                 ['decode: registered descriptive estimates: per-token value not estimable'])
                self.assertEqual(self.lines(record, 'contrast_interval'), [f'decode: no interval (not estimable; n = {kept})'])
                self.assertEqual(self.lines(record, 'decision_floor'),
                                 ['decode: decision interval not available (not estimable); floor 1.20000 J'])
                self.assertEqual(self.lines(record, 'magnitude_ratio'),
                                 ['decode: registered descriptive estimates: ratio not computable'])
                text = d.render_disclosures(record, released=True)
                self.assertIn('D_j not available', text)
                self.assertNotIn('None', text)

    def test_both_states_together_and_beside_an_issuable_contrast(self):
        h = Harness(); h.add_contrast(cid='prefill')
        _add_not_estimable(h, kept=1, floor=_refused_floor())
        h.sens = deepcopy(self.records['refused_floor'])
        record = h.produce()
        self.assertEqual(self.lines(record, 'decision_floor')[1],
                         'decode: decision interval not available (not estimable); floor not resolvable')
        self.assertTrue(self.lines(record, 'decision_floor')[0].startswith('prefill: decision interval near end '))

    def test_the_registered_shapes_only(self):
        def run(edit, *, kept=1):
            h = Harness(); _add_not_estimable(h, kept=kept); h.sens = deepcopy(self.records['not_estimable'])
            edit(h)
            with self.assertRaises(AnalysisRefusal) as refusal:
                h.produce()
            return refusal.exception.code
        row = lambda h: h.verdicts['contrasts'][0]
        # No estimate but an interval, or an estimate without one: not an engine shape.
        self.assertEqual(run(lambda h: row(h)['estimator'].update(metrology_aware_CI95={'lower': 0., 'upper': 1.})),
                         'disclosure_input_invalid')
        self.assertEqual(run(lambda h: row(h)['deterministic_bounds'].update(decision_interval={'lower': 0., 'upper': 1.})),
                         'disclosure_input_invalid')
        h = Harness(); h.add_contrast(); h.verdicts['contrasts'][0]['deterministic_bounds']['decision_interval'] = None
        with self.assertRaises(AnalysisRefusal) as refusal:
            h.produce()
        self.assertEqual(refusal.exception.code, 'disclosure_input_invalid')
        # No estimate while two quads are kept: the observations differ from the verdict.
        self.assertEqual(run(lambda h: None, kept=2), 'contrast_observations_differ_from_verdict')
        self.assertEqual(run(lambda h: row(h)['estimator'].update(n=0)), 'contrast_observations_differ_from_verdict')
        # A null floor that is not a refused floor.
        self.assertEqual(run(lambda h: row(h)['floor'].update(active_floor_j=None)), 'disclosure_input_invalid')
        # A sensitivity record null on one side only.
        def one_side(h):
            h.sens['contrasts'][0]['sensitivity']['D_j'] = 1.0
        self.assertEqual(run(one_side), 'sensitivity_record_invalid')
        def cell_null(h):
            h.sens['floor_cells'][0]['primary']['floor_abs_j'] = None
            h.sens['floor_cells'][0]['sensitivity']['floor_abs_j'] = None
        self.assertEqual(run(cell_null), 'sensitivity_record_invalid')


class ResultsFillTests(unittest.TestCase):
    def test_the_adapter_copies_both_states_as_null(self):
        from joulewise.analysis_engine.artifact import finalize_claim_verdicts, render_claim_verdicts
        from joulewise.analysis_engine.claims import evaluate_claim
        from joulewise.results_fill_adapter import adapt_claim_verdicts
        from tests.test_results_fill_adapter import campaigns, produced_verdict
        refused = deepcopy(produced_verdict('not_resolvable'))
        row = refused['contrasts'][0]
        row['floor']['resolutions'][0].update(status='refused', floor_abs_j=None, floor_cmp_j=None,
                                              floor_gate_j=None, reason_codes=['consumer_term_unknown'])
        row['floor'].update(status='refused', transport_verdict='refused', floor_abs_j=None, floor_cmp_j=None,
                            active_floor_j=None)
        row['claim_evaluation'] = evaluate_claim(
            estimate=row['estimator']['estimate'], metrology_aware_ci95=row['estimator']['metrology_aware_CI95'],
            decision_interval=row['deterministic_bounds']['decision_interval'], floor_gate_j=None,
            adjusted_rejected=row['multiplicity']['rejected'], hypothesized_direction=row['hypothesized_direction'],
            equivalence=row['equivalence'])
        for state, artifact in (('refused_floor', finalize_claim_verdicts(refused)),
                                ('not_estimable', produced_verdict('not_estimable'))):
            with self.subTest(state):
                raw = render_claim_verdicts(artifact)
                contrast = artifact['contrasts'][0]
                manifest = {'contrasts': [{'contrast_id': contrast['contrast_id']}]}
                floor = {'artifact_id': 'synthetic-floor',
                         'cells': [{'cell_id': c} for c in contrast['floor']['floor_row_ids']] or [{'cell_id': 'x'}]}
                self.assertTrue(claim_side_bound_not_issuable(raw, finalized_manifest=manifest, floor_artifact=floor))
                value = adapt_claim_verdicts(raw, campaigns=campaigns())['gamma']['contrasts'][0]
                if state == 'refused_floor':
                    self.assertEqual((value['floor']['active_floor_j'], value['claim_evaluation']['outcome']),
                                     (None, 'not_resolvable'))
                else:
                    self.assertEqual((value['estimate'], value['interval'], value['decision_interval']), (None,) * 3)
                    self.assertEqual(value['claim_evaluation']['outcome'], 'not_estimable')


if __name__ == '__main__':
    unittest.main()
