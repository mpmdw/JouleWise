"""Gate-7 regressions: synthetic inputs only; every host and process interface is stubbed."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest
from unittest import mock

from joulewise.cadence import standing as law
from scripts import cadence_controller as cc, cadence_controller_synthetic as synth
from tests.cadence import test_standing as t
from tests.cadence.test_cadence_controller import HAVE_TOOLS, WorldCase


class Gate7Law(unittest.TestCase):
    def test_duplicate_gate_keys_are_invalid_in_either_order(self):
        for gate in ('L002', 'L005', law.CLASS_A):
            release = t.released(('cq-prior-a1', gate))[0]
            hold = dict(release, decision='hold', record='lead hold')
            for records in ([hold, release], [release, hold], [release, release]):
                with self.subTest(gate=gate, records=records):
                    with self.assertRaises(law.StandingError):
                        t.standing(gate_records=records)

    def test_withdrawn_executed_legs_still_fill_the_mixed_date(self):
        rec, rel = t.pilot_done('05')
        other = t.record('cq-dev-04-s01-a1', '04', t.L[:6], t.NOW - 3 * 3600, closed=t.NOW - 2000)
        gates = rel + t.released((other['plan_id'], law.CLASS_A), (other['plan_id'], 'L005'))
        rest = t.view([t.span(1, 'dev-05-s02', '05', t.L[6:])], path='Q2.json')
        st = t.standing(gate_records=gates, dispositions=[{
            'plan_id': other['plan_id'], 'resolution': 'withdrawn', 'record': 'withdraw evidence'}])
        decision = law.select(t.snap([rest], st, records=[rec, other]))
        self.assertEqual(decision.action, 'halt')
        self.assertIn('DATE_DEV_MIXED_CAP', t.codes(decision))

    def test_withdrawn_execution_retains_total_cap_and_phase_date(self):
        run = law.Run('cq-executed-a1', 'campaign', 'development', 'dev-01', 24, False,
                      t.NOW - 3600, t.NOW - 600, 'CLOSED_OK', 'prior', resolution='withdrawn')
        for key, want in (('01', 'DATE_DEV_CAP'), ('q1', 'DATE_QUAL_DEV_OVERLAP')):
            with self.subTest(key=key):
                reasons = law.date_reasons(t.span(1, 'candidate-s01', key, t.L[:6]),
                                          law.kit_class(t.BY_KEY[key]), t.NOW, [run], [],
                                          t.standing(freeze2='frozen'))
                self.assertIn(want, {r['code'] for r in reasons})

    def test_zero_leg_withdrawal_occupies_no_development_date(self):
        run = law.Run('cq-never-ran-a1', 'campaign', 'development', 'dev-01', 0, False,
                      t.NOW - 3600, t.NOW - 600, 'REFUSED', 'prior', resolution='withdrawn')
        reasons = law.date_reasons(t.span(1, 'qual-01-s01', 'q1', t.L[:6]), law.kit_class(t.QUAL1),
                                  t.NOW, [run], [], t.standing(freeze2='frozen'))
        self.assertNotIn('DATE_QUAL_DEV_OVERLAP', {r['code'] for r in reasons})


@unittest.skipUnless(HAVE_TOOLS, 'git and ssh-keygen are needed for the synthetic origin')
class Gate7Controller(WorldCase):
    def world(self, **kw):
        self.world_number = getattr(self, 'world_number', 0) + 1
        w = synth.World(Path(self.tmp.name) / f'w{self.world_number}', **kw)
        w.controller()
        return w

    def prior_world(self, mutation=None):
        w = self.world(prior=False)
        priors = []
        for n, cid, day, hour, roster in (
                (1, 'cl-dev-04', '2026-11-15', 2, t.L[:6]),
                (2, 'cl-dev-01', '2026-11-16', 13, t.L[3:9])):
            pid = f'cq-prior-p{n}-a1'
            row = {'plan_id': pid, 'campaign_id': cid, 'block_id': cid,
                   'kit_sha256': w.sha[cid], 'roster': roster, 'legs': len(roster), 'mixed': n == 1,
                   't0': f'{day}T00:00:00-08:00', 'closed': f'{day}T{hour:02d}:00:00-08:00',
                   'desk_final': 'lead hand read'}
            priors.append(row)
            source = Path(w.cfg['output_root']) / cid / (pid + '-20261115T080000Z')
            source.mkdir(parents=True)
            receipt = {'roster': roster, 'kit': {'sha256': w.sha[cid], 'campaign_id': cid},
                       'rc': 0, 'error': None,
                       'span_result': {'chain_exit_code': 0, 'chain_outcome': 'COMPLETE',
                                       'fault': False, 'outcome': 'MEASURED_OK'},
                       'steps': [{'name': 'soak', 'rc': 0}, {'name': 'restore', 'rc': 0}],
                       'feeds': {'meter': {'stop': {'proven_stopped': True}}},
                       'legs_finished': len(roster), 'legs_planned': len(roster),
                       'legs': [{'leg_id': lid, 'summary': {'g0_outcome': 'released'}} for lid in roster]}
            if n == 1 and mutation == 'receipt-campaign':
                receipt['kit']['campaign_id'] = 'f2-inst-01'
            path = source / cc.RECEIPT
            path.write_text(json.dumps(receipt))
            ended = law.parse_time(row['closed'])
            os.utime(path, (ended, ended))
            marker = synth.offload_marker(pid, w.env.now(), str(source))
            (Path(w.cfg['copy_marker_dir']) / (pid + '.ok')).write_text(json.dumps(marker))
        if mutation == 'campaign':
            priors[0]['campaign_id'] = 'f2-inst-01'
        elif mutation == 'mixed':
            priors[0]['mixed'] = False
        elif mutation == 'count':
            priors[0]['legs'] = 0
        w.standing['prior_spans'] = priors
        w.standing['gate_records'] = t.released(
            (priors[0]['plan_id'], law.CLASS_A), (priors[0]['plan_id'], 'L005'))
        w.queue('pilot', [w.span(1, 'dev-05-s01', 'cl-dev-05', t.L[:6])], role='smoke')
        return w

    def test_honest_prior_preserves_q1_debt(self):
        w = self.prior_world()
        status = w.tick()
        self.assertEqual(status['state'], 'WAIT')
        self.assertIn('K2_Q1_DEBT', status['detail']['codes'])
        self.assertEqual(w.launcher.launched, [])

    def test_prior_declarations_and_receipt_cannot_hide_pinned_identity_or_count(self):
        for mutation in ('campaign', 'mixed', 'count', 'receipt-campaign'):
            with self.subTest(mutation=mutation):
                w = self.prior_world(mutation)
                status = w.tick()
                self.assertIn(status['state'], ('PAGED', 'HALTED'))
                self.assertIn('PRIOR_CONTRADICTS', self.pages(w))
                self.assertEqual(w.launcher.launched, [])

    def test_pinned_prior_classification_and_receipt_count_survive_bad_declarations(self):
        st = t.standing()
        prior = copy.deepcopy(st['prior_spans'][0])
        prior.update(campaign_id='f2-inst-01', mixed=False, legs=0, kit_sha256=t.SHA['04'], roster=t.L[:6])
        st['prior_spans'] = [prior]
        run = law.build_runs(st, [], [], kits=t.KITS, prior_receipts={prior['plan_id']: {
            'roster': prior['roster'], 'kit_sha256': t.SHA['04'], 'campaign_id': 'cl-dev-04',
            'legs_finished': 6}})[0]
        self.assertEqual((run.kind, run.phase, run.campaign, run.mixed, run.legs),
                         ('campaign', 'development', 'cl-dev-04', True, 6))

    def test_abnormal_cli_exit_preserves_lease_and_restart_reports_lapse(self):
        for failure in ('sleep', 'watch-open', 'watch-wait', 'watch-close', 'second-tick'):
            with self.subTest(failure=failure):
                w = self.world(prior=False)
                watcher = mock.Mock()
                if failure == 'sleep':
                    tick = mock.Mock(return_value={'state': 'WAIT', 'detail': {}})
                    w.env.sleep = mock.Mock(side_effect=OSError('synthetic wait failure'))
                else:
                    tick = mock.Mock(return_value={'state': 'LIVE', 'detail': {}})
                    if failure == 'second-tick':
                        tick.side_effect = [{'state': 'LIVE', 'detail': {}}, OSError('synthetic second tick')]
                    elif failure == 'watch-open':
                        w.env.watch = mock.Mock(side_effect=OSError('synthetic watch open'))
                    else:
                        getattr(watcher, 'wait' if failure == 'watch-wait' else 'close').side_effect = OSError(failure)
                    if failure != 'watch-open':
                        w.env.watch = mock.Mock(return_value=watcher)
                with mock.patch.object(cc, 'load_config', return_value=w.cfg), \
                        mock.patch.object(cc, 'Controller', return_value=w.ctl), \
                        mock.patch.object(w.ctl, 'tick', tick):
                    with self.assertRaises(OSError):
                        cc.main(['loop', '--config', 'synthetic.json'])
                expected = cc.read_json(w.ctl.state / 'standing-lease.json')
                held = cc.fence.read_fence(w.ctl.custody)
                self.assertEqual(expected, held)
                self.assertIsNotNone(held)
                w.env.t = held['deadline'] + 1
                w.env.watch = mock.Mock(return_value=mock.Mock())
                w.controller()
                self.assertEqual(w.ctl.startup_fence(), 'lapsed')
                self.assertEqual(w.tick()['state'], 'HALTED')
                self.assertIn('ARM_INDETERMINATE', self.pages(w))
                self.assertEqual(w.launcher.launched, [])
