"""Round-2 ruling witnesses; all real inputs are permitted, read-only rehearsals."""
import json
import math
from pathlib import Path
import statistics
import shutil
import tempfile
import unittest
from .support import recompute as r, full_pack, remove_member, dump, run_cli
from .test_rehearsals import R18

S10 = Path('/Users/edr/night-archive/independent-recompute/xcheck/synthetic')
DECODE = 'ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b'
PREFILL = 'ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b'


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def window(self, pack='ALPHA', n=5):
        archive = full_pack(self.root, pack, n)
        flags = []
        return archive, r.Window(pack, archive, flags), flags

    def test_survivors_subtract_harvest_losses_and_basis(self):
        for mode in ('harvest_loss', 'outside_basis'):
            with self.subTest(mode=mode):
                archive = full_pack(self.root / mode, 'ALPHA', 5)
                rid = 'neg8-window-start-r1'
                if mode == 'harvest_loss':
                    path = archive / 'derived/neg8-screen.json'
                    screen = json.loads(path.read_text())
                    screen['harvest_reference_losses'] = {rid: 'member.timeout'}
                    screen['rescreen']['survivors']['reference_counts']['start'] = 2
                    dump(path, screen)
                else:
                    path = archive / 'sources/claim-runs/whole-window-verdict.json'
                    verdict = json.loads(path.read_text())
                    verdict['evaluation_basis']['member_occurrences'] = [
                        m for m in verdict['evaluation_basis']['member_occurrences'] if m['bundle_id'] != rid]
                    dump(path, verdict)
                w = r.Window('ALPHA', archive, [])
                self.assertNotIn(rid, w.neg8['survivor_ids'])
                self.assertEqual(w.neg8['n_start'], 2)

    def test_four_structural_comparison_stops(self):
        self.assertIn('kept_units_disagree', r.STOP_FLAG_CODES)  # PLAN 86-91; RECONCILE section 2, last paragraph.
        cases = ('excluded_reference_in_screen', 'kept_member_outside_verdict_membership',
                 'neg8_source_not_rescreen', 'harvest_checkout_not_clean')
        for code in cases:
            with self.subTest(code=code):
                a = full_pack(self.root / code, 'ALPHA', 5)
                if code == 'excluded_reference_in_screen':
                    remove_member(a, 'neg8-window-start-r1')
                elif code == 'kept_member_outside_verdict_membership':
                    p = a / 'sources/claim-runs/whole-window-verdict.json'
                    d = json.loads(p.read_text()); d['bundle_ids'].remove('fixture-decode-r01'); dump(p, d)
                elif code == 'neg8_source_not_rescreen':
                    dump(a / 'derived/neg8-allowance.json', {'source': 'stored_verdict'})
                else:
                    dump(a / 'harvest.json', {'harvest_checkout': {'status_clean': False}})
                rc, out, _ = run_cli({'ALPHA': a}, self.root / (code + '.json'))
                self.assertEqual(rc, 0)
                flags = [f for f in out['flags'] if f['code'] == code]
                self.assertTrue(flags)
                self.assertIn(code, r.FLAG_CODES)
                self.assertIn(code, r.STOP_FLAG_CODES)
                self.assertTrue(all(f['stops_comparison'] for f in flags))
                self.assertTrue(out['comparison_stopped'])

    def test_stored_and_corpus_fallback_only_diagnostic(self):
        a = full_pack(self.root, 'ALPHA', 5)
        (a / 'derived/neg8-clean-corpus.json').unlink()
        dump(a / 'derived/neg8-allowance.json', {'source': 'stored_verdict'})
        bound = a / 'sources/bound-runs'
        from .support import bundle
        ids = [f'neg8-refcorpus-r{i:02}' for i in range(1, 19)]
        for rid in ids[12:]:
            bundle(bound, rid, 5., 'Qwen2.5-1.5B-Instruct-4bit')
        dump(bound / 'neg8-drift-bound.json', {'reference_corpus': {'member_ids': ids}})
        p = a / 'sources/claim-runs/whole-window-verdict.json'
        verdict = json.loads(p.read_text())
        verdict['idle_admission_core'] = {'neg8_bracket': {'drift_allowances': {'gross_energy': {'allowance_j': .3}}}}
        dump(p, verdict)
        flags = []; registered = r.Window('ALPHA', a, flags)
        diagnostic = r.Window('ALPHA', a, [], diagnostic=True)
        self.assertEqual(registered.neg8['corpus_n'], 0)
        self.assertIsNone(registered.neg8['allowance_j'])
        self.assertIsNone(registered.neg8['allowance_recorded_j'])
        self.assertEqual(diagnostic.neg8['corpus_n'], 18)
        self.assertEqual(diagnostic.neg8['allowance_recorded_j'], .3)

    def test_binding_capture_identity_and_name_fallback(self):
        a, w, flags = self.window()
        self.assertFalse(any(f['code'] == 'calibration_capture_name_fallback' for f in flags))
        (a / 'derived/bracket-binding.json').unlink()
        flags = []; fallback = r.Window('ALPHA', a, flags)
        self.assertEqual(fallback.b['b_op_s'], w.b['b_op_s'])
        self.assertTrue(any(f['code'] == 'calibration_capture_name_fallback' for f in flags))
        self.assertFalse(any(f['code'] == 'b_op_from_record' for f in flags))
        # A binding whose id exists only in the capture record is independent of directory names.
        dump(a / 'derived/bracket-binding.json', {'endpoints': {s: {'attempt_id': 'fixture-cal-' + s}
                                                               for s in ('pre', 'post')}})
        base = a / 'sources/claim-runs/instrument_validation'
        for slot in ('pre', 'post'):
            (base / ('fixture-cal-' + slot)).rename(base / ('unrelated-' + slot))
        flags = []; bound = r.Window('ALPHA', a, flags)
        self.assertEqual(bound.b['b_op_s'], w.b['b_op_s'])
        self.assertFalse(any(f['code'] in ('calibration_capture_name_fallback', 'b_op_from_record') for f in flags))

    def test_plan_slots_and_digest_disagreement(self):
        a, _, _ = self.window()
        p = a / 'sources/repo/configs/campaigns/ALPHA/plan_tree.json'
        tree = json.loads(p.read_text()); tree['stage_graph'][0]['spare_retry']['slot'] = 'end'; dump(p, tree)
        flags = []; w = r.Window('ALPHA', a, flags)
        self.assertEqual(w.reference_slots['neg8-window-start-r1'], 'end')
        self.assertTrue({'reference_slot_disagrees', 'roster_plan_tree_not_sealed'} <= {f['code'] for f in flags})
        (a / 'sources/repo/configs/campaigns/v5_claim_25g83/sizing_b5.json').unlink()
        flags = []; w = r.Window('ALPHA', a, flags)
        self.assertEqual(w.plan_binding['sizing_source'], 'analysis_checkout')
        self.assertTrue(any(f['code'] == 'roster_plan_tree_not_sealed' for f in flags))

    def test_paired_loo_both_keep_and_only_one_keeps_block(self):
        left = [2., 1., 3., 4., 5., 6.]
        right = [1., 2., 1.5, 2.5, 3., 4.]
        left_ids = [f'decode-b{i:02}' for i in range(1, 7)]
        right_ids = [f'prefill-b{i:02}' for i in range(1, 7)]
        for lost in (False, True):
            with self.subTest(other_lost_block=lost):
                ds = right[1:] if lost else right
                ids = right_ids[1:] if lost else right_ids
                primary = r.contrast_stats(left, .05)
                partner = r.contrast_stats(ds, .05)
                out = r.finish_contrast(primary, partner['p'], .1, left_ids,
                                        partner=(partner, ids, None, False))
                other = r.finish_contrast(partner, primary['p'], .1, ids,
                                          partner=(primary, left_ids, None, False))
                row = out['loo'][0]
                # Independent paired-t tails and the two-element Holm formula.
                def pvalue(data):
                    t = statistics.fmean(data) / (statistics.stdev(data) / math.sqrt(len(data)))
                    return r.student_p(t, len(data) - 1)
                p0, p1 = pvalue(left[1:]), pvalue(right[1:])
                expected = min(1., 2 * p0) if p0 <= p1 else min(1., max(2 * p1, p0))
                self.assertAlmostEqual(row['holm_p'], expected, delta=1e-14)
                self.assertEqual(row['partner_n'], 5)
                self.assertEqual(len(out['loo']), 6)
                self.assertEqual(len(other['loo']), 5 if lost else 6)
                if lost:
                    self.assertNotIn(1, [x['block_number'] for x in other['loo']])
                else:
                    self.assertEqual(other['loo'][0]['partner_n'], 5)
                    self.assertAlmostEqual(other['loo'][0]['partner_p'], p0, delta=1e-14)

    def test_allowance_flips_all_four_floor_consumers(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        w = SimpleNamespace(b={'b_op_s': .045}, neg8={'allowance_j': 1., 'source': 'survivor_rescreen'}, diagnostic=True)
        # The actual J5 composition is used to supply every consumer's floor.
        with patch.object(r, 'floor_estimate', return_value={'n': 0, 'status': 'computed', 'guarded_floor_j': 1.}):
            _, cell = r.make_floors(w, 'decode', {'repeat': [], 'quad': []}, {'removed_units': []})
        self.assertEqual(cell['floor_gate_j'], 2.)
        old, minted = 1., cell['floor_gate_j']
        with self.subTest(consumer='effect_not_above_floor'):
            row = r.contrast_stats([1.6] * 6)
            self.assertEqual(r.finish_contrast(row, .001, old)['outcome'], 'direction_supported')
            self.assertEqual(r.finish_contrast(row, .001, minted)['outcome'], 'not_resolvable')
        with self.subTest(consumer='loo_above_floor'):
            row = r.contrast_stats([1.6] * 6)
            self.assertTrue(all(x['above_floor'] for x in r.finish_contrast(row, .001, old)['loo']))
            self.assertFalse(any(x['above_floor'] for x in r.finish_contrast(row, .001, minted)['loo']))
        with self.subTest(consumer='quarter_floor_magnitude'):
            row = r.contrast_stats([5., 2.6, 2.6, 2.6, 2.6, 2.6])
            self.assertTrue(r.finish_contrast(row, .001, old)['loo_magnitude_influential'])
            self.assertFalse(r.finish_contrast(row, .001, minted)['loo_magnitude_influential'])
        with self.subTest(consumer='decision_interval_vs_floor'):
            self.assertTrue(r.decision_beyond_floor({'dbar_j': 2.6, 'decision_interval_j': [1.6, 3.6]}, old))
            self.assertFalse(r.decision_beyond_floor({'dbar_j': 2.6, 'decision_interval_j': [1.6, 3.6]}, minted))

    def test_load_line_steps_one_to_four_and_no_restoration(self):
        archives = {p: full_pack(self.root, p, 6) for p in ('ALPHA', 'BETA', 'GAMMA')}
        remove_member(archives['GAMMA'], 'fixture-decode-b01-a1', ('contention.request_overlap',))
        remove_member(archives['GAMMA'], 'fixture-prefill-p2048-b01-a1',
                      ('thermal.os_level_nonzero', 'member.admission_aborted'))
        remove_member(archives['ALPHA'], 'fixture-decode-r01', ('thermal.os_level_nonzero',))
        _, out, _ = run_cli(archives, self.root / 'load.json')
        lines = out['disclosures']['load_sensitivity']
        for cid in (DECODE, PREFILL):
            line = lines[cid]
            self.assertTrue({'n', 'dbar_j', 'metrology_interval_j'} <= set(line))
            self.assertFalse({'holm_p', 'p', 'D_j', 'floor_gate_j', 'outcome', 'ceiling'} & set(line))
            self.assertIn('restored_count', line); self.assertIn('code_families', line)
        self.assertEqual(lines[DECODE]['restored_count'], 1)
        self.assertEqual(lines[DECODE]['code_families'], ['contention'])
        self.assertEqual(lines[PREFILL]['code_families'], ['thermal pressure'])
        self.assertEqual(lines[PREFILL]['restored_count'], 0)
        self.assertEqual(lines[PREFILL]['note'], 'no unit restored')
        self.assertEqual(lines['df-ph-decode-qwen3-1p7b']['restored_by_stratum'], {'repeat': 1, 'quad': 0})
        flags = [f for f in out['flags'] if f['code'] == 'loo_kept_n_equals_minimum']
        self.assertEqual(len(flags), 2)
        self.assertTrue(all(f['blinding'] == 'STRUCTURE' and not f['stops_comparison'] for f in flags))
        self.assertEqual(len(out['contrasts'][DECODE]['loo']), 5)
        self.assertTrue(all(x['n'] == 4 for x in out['contrasts'][DECODE]['loo']))

    def test_sensitivity_epoch_cutoff_invariance_and_primary_equal_window(self):
        archives = {p: full_pack(self.root, p, 5) for p in ('ALPHA', 'BETA', 'GAMMA')}
        for pack, a in archives.items():
            dump(a / 'derived/terminal-pin.json', {'sequence': 405 if pack == 'GAMMA' else 400})
        gamma = archives['GAMMA']
        rows = [
            {'sequence': 376, 'disposition': 'valid', 'identity_epoch': {'test': 'epoch'}, 'exact_bound_lexeme_s': '.8'},
            {'sequence': 401, 'disposition': 'systematic-invalid', 'identity_epoch': {'test': 'epoch'}, 'exact_bound_lexeme_s': '.060'},
            {'sequence': 402, 'disposition': 'random-invalid', 'identity_epoch': {'test': 'epoch'}, 'exact_bound_lexeme_s': '.7'},
            {'sequence': 403, 'disposition': 'valid', 'identity_epoch': {'test': 'other'}, 'exact_bound_lexeme_s': '.9'},
            {'sequence': 406, 'disposition': 'valid', 'identity_epoch': {'test': 'epoch'}, 'exact_bound_lexeme_s': '1.0'}]
        (gamma / 'sources/ledger/calibration_observation_ledger.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in rows))
        # BETA's own operative bound is larger than B_max.
        beta = archives['BETA']
        for slot in ('pre', 'post'):
            p = beta / f'sources/claim-runs/instrument_validation/fixture-cal-{slot}/instrument_evidence.json'
            d = json.loads(p.read_text()); d['b_fiducial_s'] = .055469; dump(p, d)
        dump(beta / 'withheld/bracket-evaluation.json', {'assessment': {'b_fiducial_s': .07}})
        _, out, _ = run_cli(archives, self.root / 'sensitivity.json')
        line = out['disclosures']['sensitivity_bound']
        self.assertEqual((line['B_max_s'], line['attaining_sequence'], line['T']), (.06, 401, 405))
        self.assertAlmostEqual(line['windows']['BETA']['b_sens_s'], .07, delta=1e-15)
        self.assertEqual(line['windows']['ALPHA']['b_sens_s'], .06)
        self.assertEqual(line['windows']['GAMMA']['b_sens_s'], .06)
        self.assertEqual(line['windows']['BETA']['note'], 'sensitivity values equal primary')
        for cid, primary in out['reported_cells'].items():
            sens = line['reported_cells'][cid]
            with self.subTest(cell=cid):
                self.assertEqual(sens['mean_j'], primary['mean_j'])
                self.assertEqual(sens['interval']['h_j'], primary['interval']['h_j'])
                if primary['model'] == r.MODELS['BETA']:
                    self.assertEqual(sens, primary)
                else:
                    self.assertGreater(sens['interval']['B_j'], primary['interval']['B_j'])
        for cid, primary in out['contrasts'].items():
            sens = line['contrasts'][cid]
            for key in ('dbar_j', 's_d_j', 'metrology_interval_j', 'p', 'holm_p'):
                with self.subTest(contrast=cid, key=key): self.assertEqual(sens[key], primary[key])
            self.assertIn('outcome_equals_primary', sens)
            self.assertGreater(sens['D_j'], primary['D_j'])
            self.assertIn('floor', sens)
        for key, primary in out['floors'].items():
            sens = line['floors'][key]
            if key.startswith(r.MODELS['BETA']): self.assertEqual(sens, primary)
            else: self.assertGreater(sens['drift_widened_guarded_floor_j'], primary['drift_widened_guarded_floor_j'])


@unittest.skipUnless((S10 / 'alpha/archive').exists(), 'S10 synthetic archives unavailable')
class ArchivedSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        extra = [x for pack in ('alpha', 'beta', 'gamma') for kind in ('claim', 'bound')
                 for x in ('--' + kind + '-runs-' + pack, str(S10 / pack / 'custody' / ('runs_' + kind)))]
        cls.rc, cls.out, cls.stdout = run_cli({p.upper(): S10 / p / 'archive' for p in ('alpha', 'beta', 'gamma')},
                                             Path(cls.tmp.name) / 's10.json', extra)

    def test_eight_floors_match_l9_and_J5_disclosures(self):
        count = 0
        for pack in ('alpha', 'beta'):
            path = S10 / 'l9-out' / (pack + '-extraction.json')
            self.assertTrue(path.exists())
            data = json.loads(path.read_text())
            for cell in data['cells']:
                if not cell['extractable']: continue
                phase = 'decode' if 'decode' in cell['cell_id'] else 'prefill'
                if 'p42' in cell['cell_id']: continue
                model = r.MODELS[pack.upper()]
                ours = self.out['floors'][model + '/' + phase + '/' + cell['kind']]
                with self.subTest(pack=pack, cell=cell['cell_id']):
                    self.assertAlmostEqual(ours['drift_widened_guarded_floor_j'], cell['operative_floor_j'],
                                           delta=abs(cell['operative_floor_j']) * 1e-12)
                    self.assertAlmostEqual(ours['allowance_j'], cell['whole_window_drift_allowance']['allowance_j'], delta=1e-12)
                    self.assertTrue({'guarded_floor_j', 'allowance_j', 'allowance_source',
                                     'drift_widened_guarded_floor_j'} <= set(ours))
                count += 1
        self.assertEqual(count, 8)
        for prefix, cell in self.out['floor_cells'].items():
            self.assertEqual(cell['floor_gate_j'], max(cell['floor_abs_j'], cell['floor_cmp_j']))
            self.assertEqual(cell['floor_abs_j'], self.out['floors'][prefix + '/absolute']['drift_widened_guarded_floor_j'])
            self.assertEqual(cell['floor_cmp_j'], self.out['floors'][prefix + '/comparative']['drift_widened_guarded_floor_j'])
        for cid, c in self.out['contrasts'].items():
            self.assertTrue(c['floor']['attained_by'])
            self.assertEqual(c['floor_gate_j'], max(x['floor_gate_j'] for x in c['floor']['sides'].values()))
            self.assertEqual(self.out['disclosures']['decision_vs_floor'][cid], r.decision_beyond_floor(c, c['floor_gate_j']))
            self.assertEqual(c['loo_magnitude_influential'], any(
                abs(row['dbar_j'] - c['dbar_j']) > .25 * c['floor_gate_j'] for row in c['loo']))
            for row in c['loo']:
                self.assertEqual(row['above_floor'], abs(row['dbar_j']) > c['floor_gate_j'])

    def test_three_binding_captures(self):
        expected = {'ALPHA': .03824698449914623, 'BETA': .039254064620926975, 'GAMMA': .040261144699051975}
        for pack, value in expected.items():
            with self.subTest(pack=pack): self.assertAlmostEqual(self.out['windows'][pack]['b_op_s'], value, delta=1e-15)
        self.assertFalse(any(f['code'] in ('b_op_from_record', 'calibration_capture_name_fallback') for f in self.out['flags']))


@unittest.skipUnless(R18.exists(), 'R18 rehearsal unavailable')
class RegisteredRehearsalTests(unittest.TestCase):
    def test_R18_clean_checkout_plan_survivors_bop_and_all_meter_requests(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        _, out, _ = run_cli({'ALPHA': R18}, Path(tmp) / 'r18.json')
        window = out['windows']['ALPHA']
        self.assertAlmostEqual(window['neg8']['allowance_j'], 1.153521798393328, delta=1e-12)
        self.assertAlmostEqual(window['b_op_s'], .045030653137666625, delta=1e-15)
        self.assertEqual(window['neg8']['source'], 'survivor_rescreen')
        self.assertEqual(window['plan_tree_binding']['sizing_source'], 'analysis_checkout')
        self.assertEqual(window['plan_tree_binding']['sha256'], window['plan_tree_binding']['sealed_sha256'])
        # ERR X1 overrides the brief's no-tripwire prediction: this rehearsal
        # excludes two basis references not named by either screen loss list.
        stops = r.STOP_FLAG_CODES & {f['code'] for f in out['flags']}
        self.assertEqual(stops, {'excluded_reference_in_screen'})
        tripwire = next(f for f in out['flags'] if f['code'] == 'excluded_reference_in_screen')
        self.assertEqual(tripwire['detail']['run_ids'], ['neg8-window-end-r2', 'neg8-window-start-r1'])
        archived = json.loads((R18 / 'withheld/meter.json').read_text())['members']
        recomputed = out['disclosures']['whole_machine']['windows']['ALPHA']['members']
        self.assertEqual(len(archived), 53)
        for rid, record in archived.items():
            with self.subTest(member=rid):
                ours = recomputed[rid]['phases']['request']
                expected = record['machine']
                if rid == 'd117fq31p7-df-cmp-abba-ph-decode-b01-b1':
                    self.assertEqual(ours['recorded_comparison']['mismatched_fields'], ['rail_delta_J'])
                else:
                    self.assertTrue(ours['recorded_comparison']['matches'], ours['recorded_comparison'])
                for keys in (('delta_J',), ('meter', 'energy_J'), ('meter', 'baseline_W')):
                    value = r.get(expected, *keys)
                    self.assertAlmostEqual(r.get(ours, *keys), value, delta=max(.5, abs(value) * .005))
                self.assertLessEqual(abs(ours['meter']['n'] - expected['meter']['n']), 2)
                self.assertEqual(ours['battery']['n'], expected['battery']['n'])
                self.assertLessEqual(abs(ours['window_ns'][0] - expected['window_ns'][0]), 1e6)
        mismatches = [f for f in out['flags'] if f['code'] == 'meter_request_mismatch']
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]['scope'], 'd117fq31p7-df-cmp-abba-ph-decode-b01-b1')
        self.assertIn('anchor unknown', mismatches[0]['detail']['cause'])
