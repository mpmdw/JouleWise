"""Opt-in archive rehearsals, disabled before archive access in synthetic-only runs.

Unrounded energies, envelopes and records use COMMON's agreement bars;
printed witnesses match exact decimal words.
"""
import json
import math
from pathlib import Path
import tempfile
import unittest
from .support import (assert_values_agree, archive_available, recompute as r, run_cli)

REHEARSALS=Path('/Users/edr/night-archive/gate-prune/rehearsal-real')
R18=REHEARSALS/'corpus18-20261009T1949Z/archive-pinned'
ALPHA1=REHEARSALS/'alpha-1/archive'
GAMMA2=REHEARSALS/'gamma-2/archive'


class RehearsalTests(unittest.TestCase):
    def check_members(self,archive,pack):
        phases=0;skipped=0
        for root in (archive/'sources/claim-runs',archive/'sources/bound-runs'):
            for path in sorted(root.glob('*/metadata.json')):
                meta=json.loads(path.read_text());summary=json.loads((path.parent/'summary_metrics.json').read_text())
                if summary.get('status')!='succeeded' or r.get(meta,'uncertainty_evidence','clock_anchor','status')!='bounded':
                    skipped+=1;continue
                # Science identity is irrelevant to the independent per-member arithmetic check.
                member=r.Member(path.parent,path.parent.name,r.Reader(pack,[]),None,r.role(path.parent.name))
                for phase in ('prefill','decode'):
                    energy=r.get(summary,'phase_energy_j',phase)
                    bound=r.get(summary,'energy_anchor_shift_envelopes','/phase_energy_j/'+phase,'max_abs_delta_j')
                    if r.finite(energy) and r.finite(bound):
                        with self.subTest(archive=archive.name,run_id=path.parent.name,phase=phase):
                            assert_values_agree(self, member.energies[phase], energy)
                            assert_values_agree(self, member.pre[phase]['max_abs_delta_j'], bound)
                        phases+=1
        self.assertGreater(phases,0)
        return phases,skipped

    @unittest.skipUnless(archive_available(R18),'R18 rehearsal unavailable')
    def test_R18_every_succeeded_bounded_phase_within_common_bar(self):
        phases,skipped=self.check_members(R18,'ALPHA')
        self.assertEqual(skipped,1)
        self.assertEqual(phases,104)

    @unittest.skipUnless(archive_available(ALPHA1),'alpha-1 rehearsal unavailable')
    def test_alpha1_every_succeeded_bounded_phase_within_common_bar(self):
        self.assertEqual(self.check_members(ALPHA1,'ALPHA')[0],22)

    @unittest.skipUnless(archive_available(GAMMA2),'gamma-2 rehearsal unavailable')
    def test_gamma2_every_succeeded_bounded_phase_within_common_bar(self):
        self.assertEqual(self.check_members(GAMMA2,'GAMMA')[0],19)

    @unittest.skipUnless(archive_available(R18),'R18 rehearsal unavailable')
    def test_R18_plist_csv_696_records(self):
        path=R18/'sources/claim-runs/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b08-b1'
        meta=json.loads((path/'metadata.json').read_text())
        anchor=r.get(meta,'uncertainty_evidence','clock_anchor','first_sample_end_point_epoch_s')
        plist=r.plist_records((path/'raw/powermetrics.plist').read_bytes(),anchor)
        csv=r.csv_records((path/'power_trace.csv').read_bytes())
        self.assertEqual(len(plist),696)
        assert_values_agree(self, plist, csv)

    @unittest.skipUnless(archive_available(R18),'R18 rehearsal unavailable')
    def test_R18_registered_bop_allowance_and_minimum(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc,out,line=run_cli({'ALPHA':R18},Path(tmp)/'r18.json')
        self.assertEqual(rc,0);self.assertIn('sha256=',line)
        window=out['windows']['ALPHA']
        assert_values_agree(self, window['b_op_s'], .045030653137666625)
        assert_values_agree(self, window['neg8']['allowance_j'], 1.153521798393328)
        self.assertEqual(window['neg8']['corpus_n'],12)
        self.assertEqual((window['neg8']['n_start'],window['neg8']['n_mid'],window['neg8']['n_end']),(2,1,3))
        for cell in out['reported_cells'].values():
            self.assertEqual(cell['status'],'below_minimum')
            for key in ('mean_j','lower_j','upper_j'):self.assertIsNone(cell[key])
        self.assertEqual(len(out['reported_cells']),2)

    @unittest.skipUnless(archive_available(R18),'R18 rehearsal unavailable')
    def test_R18_diagnostic_comparative_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            _,out,_=run_cli({'ALPHA':R18},Path(tmp)/'diagnostic.json',('--diagnostic-ignore-exclusions',))
        self.assertEqual(out['mode'],'DIAGNOSTIC_NOT_REGISTERED')
        f=out['floors']['Qwen3-1.7B-4bit/prefill/comparative']
        self.assertEqual(f['n'],5);assert_values_agree(self, f['guard'], 1.5)
        for key in ('guarded_floor_j','R','R_cm'):
            self.assertTrue(math.isfinite(f[key]),key)
        self.assertEqual(len(f['widths_j']),5)
        self.assertTrue(all(math.isfinite(v) for key in ('widths_j','shared_j','local_j') for v in f[key]))
        self.assertIsNone(out['dominance']['branch'])
