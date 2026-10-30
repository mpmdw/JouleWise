"""L9-STEP4-5: the plan-named member codes reach a step-4 cell through the real extractor.

L9-STEP4-4 made window_evidence_precheck_missing, campaign_cooldown_evidence_missing
and idle_window_suspect R3 because they reach an extractor cell; until now only a
comment said so (Opus F2 and Fable F1 of the L9-STEP4-4 delta reviews). Each case
below changes one synthetic member, r06 of the kept-units arithmetic corpus, and
runs fe.extract_cells with the kept units. window_evidence_precheck, the
extractor's precheck forwarding filter and _evaluate_member all run unpatched;
the only seams are the arithmetic corpus's own (strict validator, whole-window
refusals, drift allowances and consumption session), none of which reads a
member's reasons. Every input is synthetic.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from joulewise import floor_extraction as fe
from joulewise.b5_analysis.steps import classify_step4_exit
from tests.b5_analysis import test_floor_kept_units as kept

MEMBER = 'r06'


class Step4MemberCodeTests(unittest.TestCase):
    def setUp(self):
        self.fresh_corpus()
        seams = kept.arithmetic_seams()
        seams.__enter__()
        self.addCleanup(seams.__exit__, None, None, None)

    def fresh_corpus(self):
        tmp = tempfile.TemporaryDirectory(prefix='s4-member-codes-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / 'runs'
        base, spec = kept.arithmetic()
        shutil.copytree(base, self.root)
        self.spec = copy.deepcopy(spec)

    def summary(self, change):
        path = self.root / MEMBER / 'summary_metrics.json'
        summary = json.loads(path.read_bytes())
        change(summary)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')

    def request_metric(self):
        """Point the absolute cell at energy_request_j, with each member's envelope for it."""
        for bundle in self.spec['cells'][0]['members']:
            path = self.root / bundle['bundle_id'] / 'summary_metrics.json'
            summary = json.loads(path.read_bytes())
            envelopes = summary['energy_anchor_shift_envelopes']
            envelopes['/energy_request_j'] = dict(envelopes['/gross_energy_j'])
            path.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
        self.spec['cells'][0]['metric'] = 'energy_request_j'
        kept.family(self.spec['cells'][0], 'df-s4')

    def target(self, **kwargs):
        report = fe.extract_cells(self.root, self.spec, kept_units=kept.units_for(self.spec), **kwargs)
        cell, other = report['cells']
        self.assertTrue(other['extractable'], other['refusal_reasons'])
        return report, cell

    def assert_r3_cell(self, code):
        report, cell = self.target()
        self.assertFalse(cell['extractable'])
        self.assertEqual(cell['refusal_reasons'], [code])
        row = next(m for m in cell['members'] if m['bundle_id'] == MEMBER)
        self.assertEqual(row['reasons'], [code])
        self.assertEqual(classify_step4_exit(1, report, self.spec), 'extraction_cell_r3_refusal')

    def test_controls_extract_both_cells(self):
        for metric in ('gross_energy_j', 'energy_request_j'):
            with self.subTest(metric=metric):
                if metric == 'energy_request_j':
                    self.request_metric()
                _, cell = self.target()
                self.assertTrue(cell['extractable'], cell['refusal_reasons'])

    def test_missing_precheck_root_is_r3_on_the_target_cell(self):
        self.summary(lambda summary: summary.pop('window_evidence_precheck'))
        self.assert_r3_cell('window_evidence_precheck_missing')

    def test_stored_non_reducer_reasons_become_precheck_missing(self):
        # Fable F1: the precheck forwards reducer vocabulary only; a stored claim-gate code
        # or unlisted code never reaches the cell verbatim.
        for stored in ('paired_block_incomplete', 'fixed_n_plan_incomplete', 'syn_reason_in_neither_list'):
            with self.subTest(stored=stored):
                self.fresh_corpus()
                self.summary(lambda summary: summary['window_evidence_precheck'].update(
                    gross_request={'eligible': False, 'reasons': [stored]}))
                self.assert_r3_cell('window_evidence_precheck_missing')

    def test_idle_window_suspect_on_energy_request_j_is_r3_on_the_target_cell(self):
        self.request_metric()
        self.summary(lambda summary: summary['measurement_quality'].update(idle_window_suspect=True))
        self.assert_r3_cell('idle_window_suspect')

    def test_unverified_campaign_cooldown_is_r3_on_the_target_cell(self):
        manifest_path = self.root / 'campaign_manifests/synthetic-session.json'
        manifest = json.loads(manifest_path.read_bytes())
        member = next(m for m in manifest['members'] if m['run_id'] == MEMBER)
        member['preceding_campaign_cooldown']['raw_artifact']['sha256'] = hashlib.sha256(b'other').hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        self.assertIs(fe.campaign_cooldown_evidence(self.root)[MEMBER]['verified'], False)
        self.assert_r3_cell('campaign_cooldown_evidence_missing')

    def test_verified_cap_hit_is_filtered_from_cell_reasons(self):
        # Fable F5: the forwarding filter drops cooldown_cap_hit, which same-slot exclusion
        # dispositions (legacy) or the kept-unit stop raises (block 5); it is never a cell reason.
        kept.ArithmeticTests.cap_hit(self, MEMBER)
        report = fe.extract_cells(self.root, self.spec)
        cell = report['cells'][0]
        self.assertTrue(cell['extractable'], cell['refusal_reasons'])
        self.assertEqual(cell['excluded_slots'], [MEMBER])
        row = next(m for m in cell['members'] if m['bundle_id'] == MEMBER)
        self.assertTrue(row['excluded'])
        self.assertNotIn('cooldown_cap_hit', row['reasons'])


if __name__ == '__main__':
    unittest.main()
