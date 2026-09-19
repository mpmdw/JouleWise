"""Campaign mechanics and negative scientific branches using fixtures only."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
from joulewise import quiet_predicate_campaign as campaign
from joulewise import night_gate

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads((ROOT / campaign.PROTOCOL_PATH).read_text())


def good_round(busy=0):
    return {"round":1, "session":"fixture", "os_build":"25G83", "os_build_valid":True,
            "census_clean":True, "observer_cpu_s":1,
            "observation":{"metrics":{"busy_cores":busy}}, "hard_probes":[{"result":[
                {"argv":list(night_gate.PMSET_BATT_ARGV),"exit_code":0,"stdout":"Now drawing from 'AC Power'"},
                {"argv":list(night_gate.THERMAL_ARGV),"exit_code":0,"stdout":"CPU_Speed_Limit = 100"}]}]}


class CampaignTests(unittest.TestCase):
    def test_frozen_protocol_and_size_use_upper_bound_not_sd(self):
        sha = campaign.digest((ROOT / campaign.CHAIN_PATH).read_bytes())
        self.assertEqual(campaign.validate_protocol(PROTOCOL, sha), PROTOCOL)
        for key in ('settle_s','envelopes','envelope_s','interior_s','sample_interval_s','window_max_s'):
            with self.assertRaises(ValueError):
                campaign.validate_protocol({**PROTOCOL,key:1}, sha)
        self.assertEqual(campaign.size_block_two(.3), 3)
        self.assertEqual(campaign.size_block_two(1), 8)
        self.assertGreater(campaign.size_block_two(2), 24)
        for upper in (None, True, float('nan'), -1):
            with self.assertRaises(ValueError):
                campaign.size_block_two(upper)

    def test_busy_cores_never_exclude_and_each_hard_mechanism_does(self):
        self.assertEqual(campaign.hard_exclusions([good_round(999)]), [])
        for mutate, name in (
            (lambda r:r.update(census_clean=None),'census_not_clean_or_unknown'),
            (lambda r:r['hard_probes'][0]['result'][0].update(stdout='Battery Power'),'ac_not_AC_Power_or_probe_error'),
            (lambda r:r['hard_probes'][0]['result'][1].update(stdout='CPU_Speed_Limit = 99'),'CPU_Speed_Limit_below_100_or_thermal_probe_error'),
            (lambda r:r['hard_probes'][0]['result'][1].update(exit_code=2),'CPU_Speed_Limit_below_100_or_thermal_probe_error'),
            (lambda r:r.update(hard_probes=[]),'ac_not_AC_Power_or_probe_error')):
            row = good_round()
            mutate(row)
            self.assertIn(name, campaign.hard_exclusions([row]))

    def test_all_three_stop_branches_and_missing_evidence_never_qualify(self):
        self.assertEqual(campaign.stop_branch()["outcome"], "no decision")
        for kwargs in ({"s_upper":2}, {"observer_floor":.051}, {"block_two_upper_j":1.01}):
            self.assertEqual(campaign.stop_branch(**kwargs)["outcome"], "no cutoff qualifies")
        self.assertEqual(campaign.stop_branch(s_upper=0,observer_floor=.05,block_two_upper_j=1)["outcome"], "no decision")

    def test_partial_envelopes_remain_and_exclusions_do_not_bridge_adjacency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = []
            for index in range(1, 13):
                out = root / f'envelope-{index:02d}'
                out.mkdir()
                session = {'session':'fixture','boot_id':'boot','os_build':'25G83','power':{'anchor':{'status':'bounded'}},
                           'interior':{'complete_support':True,'power':{'energy_j':{'rail_sum_w':index,'combined_w':index}}}}
                row = good_round(100)
                if index in (3, 7, 11):
                    row['census_clean'] = None
                if index == 12:
                    session['interior']['complete_support'] = False
                (out/'session.json').write_text(json.dumps(session))
                (out/'rounds.jsonl').write_text(json.dumps(row)+'\n')
                entries.append({'index':index,'start_drift_s':0})
            report = campaign.pilot_summary(root, PROTOCOL, entries)
            self.assertEqual(report['retained'], 8)
            self.assertEqual(report['status'], 'INCONCLUSIVE')  # fewer than six original adjacent pairs
            self.assertEqual(len(report['envelopes']), 12)
            self.assertNotIn({'left':2,'right':4,'delta_j':2}, report['adjacent_pairs'])
            self.assertIsNone(report['s_upper'])  # no unruled confidence/plug-in shortcut
            self.assertFalse(report['cutoff_authority'])

    def test_group_journal_retirement_no_pid_reuse_signalling_and_bounded_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'groups.jsonl'
            campaign.append_event(path, {'kind':'collector','pgid':99999999})
            with patch.object(campaign,'group_absent',return_value=True), patch.object(campaign.os,'killpg') as kill:
                result = campaign.cleanup_groups(path, budget_s=1)
            self.assertTrue(result['cleanup_proven'])
            self.assertEqual(campaign.process_groups(path), set())
            kill.assert_not_called()
            campaign.append_event(path, {'kind':'sampler','pgid':99999998})
            with patch.object(campaign,'group_absent',return_value=False), patch.object(campaign.os,'killpg') as kill:
                result = campaign.cleanup_groups(path, budget_s=.01)
            self.assertFalse(result['cleanup_proven'])
            self.assertEqual(result['residue'], [99999998])
            kill.assert_called()

    def test_unsafe_own_group_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'groups.jsonl'
            campaign.append_event(path, {'kind':'collector','pgid':os.getpgrp()})
            with self.assertRaisesRegex(ValueError,'unsafe'):
                campaign.process_groups(path)

    def test_verify_branch_does_not_call_executor_or_recorder(self):
        with patch.object(campaign,'verify_environment',return_value=(None,None,'a'*64)), \
                patch.object(campaign,'execute') as execute, patch.object(campaign,'record_covariates') as record:
            self.assertEqual(campaign.main(['verify']), 0)
        execute.assert_not_called()
        record.assert_not_called()


class FrozenExecutorTests(unittest.TestCase):
    def test_twelve_protocol_envelopes_one_recorder_no_load_and_cleanup(self):
        from dataclasses import replace
        from types import SimpleNamespace
        from tests.test_night_gate import make_plan
        calls, processes = [], {}
        class Clock:
            now = 0.
            def monotonic(self): return self.now
            def time(self): return 1000+self.now
            def sleep(self, seconds): self.now += seconds
        clock = Clock()
        class Child:
            def __init__(self, argv, **kwargs):
                self.pid = 8000000+len(calls)
                self.argv, self.returncode = argv, None
                calls.append(argv)
                processes[self.pid] = self
                if 'collect' in argv:
                    out = Path(argv[argv.index('--out')+1])
                    out.mkdir()
                    index = int(argv[argv.index('--repeat')+1])
                    self.end = float(argv[argv.index('--envelope-start-mono-s')+1])+600
                    session={'session':'fixture','os_build':'25G83','boot_id':'boot','start_drift_s':0,
                        'power':{'anchor':{'status':'bounded'}},'interior':{'complete_support':True,
                        'power':{'energy_j':{'rail_sum_w':index,'combined_w':index}}}}
                    (out/'session.json').write_text(json.dumps(session))
                    (out/'rounds.jsonl').write_text(json.dumps(good_round())+'\n')
            def poll(self): return self.returncode
            def wait(self, timeout):
                clock.now = max(clock.now, self.end)
                self.returncode = 0
                return 0
        def terminate(pgid, sig): processes[pgid].returncode = -sig
        with tempfile.TemporaryDirectory() as tmp, patch.object(campaign,'time',clock), \
                patch.object(campaign.subprocess,'Popen',side_effect=Child), \
                patch.object(campaign,'group_absent',side_effect=lambda pgid:processes[pgid].returncode is not None), \
                patch.object(campaign.os,'killpg',side_effect=terminate):
            plan=replace(make_plan(),t0_epoch_s=1000,window_max_s=9000)
            self.assertEqual(campaign.execute(plan,PROTOCOL,Path(tmp)),0)
            cleanup=json.loads((Path(tmp)/'evidence_cleanup.json').read_text())
            self.assertTrue(cleanup['cleanup_proven'])
            summary=json.loads((Path(tmp)/'evidence/summary.json').read_text())
            self.assertEqual(summary['retained'],12)
            self.assertEqual(len(summary['adjacent_pairs']),11)
        self.assertEqual(len(calls),13)
        self.assertEqual(sum('record' in cmd for cmd in calls),1)
        self.assertEqual(sum('collect' in cmd for cmd in calls),12)
        self.assertFalse(any('load' in cmd for cmd in calls))
        for cmd in calls[1:]:
            self.assertEqual(cmd[cmd.index('--duration-s')+1],'600')
            self.assertEqual(cmd[cmd.index('--interior-s')+1],'480')
            self.assertEqual(cmd[cmd.index('--sample-interval-s')+1],'30')
