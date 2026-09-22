"""Campaign mechanics and negative scientific branches using fixtures only."""
import json
import math
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock
from joulewise import quiet_predicate_campaign as campaign
from joulewise import night_gate

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads((ROOT / campaign.PROTOCOL_PATH).read_text())
EXPECTED_OFF = campaign.EXPECTED_NETWORK_TIME_OFF_STDOUT


def provenance(state="authenticated", matched=0):
    """An envelope's network-time provenance as the chain records it.

    After the cold gate every envelope carries the chain's OFF receipt plus a
    per-envelope attestation from the ``timed`` log; only ``authenticated``
    envelopes are claim-bearing.
    """
    return {"state": "off", "method": "systemsetup_setusingnetworktime_off_exact_stdout",
            "established_epoch_s": 1000.0, "established_monotonic_s": 10.0,
            "record": "network_time_control.json", "record_sha256": "0" * 64,
            "attestation": {"state": state, "method": campaign.TIMED_LOG_ATTESTATION_METHOD,
                            "window_epoch_s": [1000.0, 1600.0], "log": "timed-log.txt",
                            "log_sha256": "1" * 64, "matched_lines": matched, "exit_code": 0}}


def good_round(busy=0):
    return {"round":1, "session":"fixture", "os_build":"25G83", "os_build_valid":True,
            "census_clean":True, "observer_cpu_s":1,
            "observation":{"metrics":{"busy_cores":busy}}, "hard_probes":[{"result":[
                {"argv":list(night_gate.PMSET_BATT_ARGV),"exit_code":0,"stdout":"Now drawing from 'AC Power'"},
                {"argv":list(night_gate.THERMAL_ARGV),"exit_code":0,"stdout":"CPU_Speed_Limit = 100"}]}]}


class CampaignTests(unittest.TestCase):
    def summarize(self, energies, excluded=(), missing=(), observer_core=None, recorder=False, drift=0):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            root = Path(tmp) / 'evidence'
            root.mkdir()
            entries = []
            for index, energy in enumerate(energies, 1):
                if index in missing:
                    continue
                out = root / f'envelope-{index:02d}'
                out.mkdir()
                session = {'session':'fixture', 'boot_id':'boot', 'os_build':'25G83',
                    'network_time_provenance': provenance(),
                    'power':{'anchor':{'status':'bounded'}},
                    'interior':{'complete_support':True,
                        'power':{'energy_j':{'rail_sum_w':energy, 'combined_w':energy}}}}
                row = good_round()
                if observer_core is not None:
                    row.update(observer_cpu_s=30 * observer_core, round_mono_start_s=index*600, round_mono_end_s=index*600+30)
                if index in excluded:
                    row['census_clean'] = False
                (out / 'session.json').write_text(json.dumps(session))
                (out / 'rounds.jsonl').write_text(json.dumps(row) + '\n')
                entries.append({'index':index, 'scheduled_mono_s':index*600, 'start_drift_s':drift})
                if recorder:
                    campaign.append_event(root.parent / PROTOCOL['recorder_journal'], {
                        'monotonic_start':index*600, 'monotonic_end':index*600+30,
                        'observation':{'metrics':{'busy_cores':99 if index == 5 else .01}}, 'observer_cpu_s':.2})
            campaign.pilot_summary(root, PROTOCOL, entries)
            memo = (root / 'summary.md').read_text()
            self.assertIn('normally distributed', memo)
            return json.loads((root / 'summary.json').read_text())

    def test_recorder_excursion_joins_only_envelope_five_never_retention(self):
        report = self.summarize([10]*12, recorder=True)
        self.assertEqual(report['retained'], 12)
        self.assertEqual([r['busy_cores']['max'] for r in report['envelopes']], [.01]*4+[99]+[.01]*7)
        self.assertEqual(report['envelopes'][4]['busy_cores']['median'], 99)
        self.assertEqual(report['clean_machine_busy_cores']['max'], 99)
        excluded = self.summarize([10]*12, recorder=True, excluded={5})
        self.assertEqual(excluded['clean_machine_busy_cores']['max'], .01)
        self.assertEqual(excluded['envelopes'][4]['busy_cores']['max'], 99)

    def test_twelve_constant_energies_point_one_observer_core_stops(self):
        report = self.summarize([10]*12, observer_core=.1)
        self.assertEqual(report['retained'], 12)
        self.assertEqual(report['s_upper'], 0)
        self.assertAlmostEqual(report['observer_floor_cores'], .1)
        self.assertEqual(report['block_two_stop']['outcome'], 'no cutoff qualifies')
        self.assertEqual(report['block_two_stop']['causes'], ['observer_floor_above_smallest_holdable_share'])

    def test_start_drift_ten_seconds_included_beyond_excluded_by_name(self):
        self.assertEqual(self.summarize([10]*12, drift=10)['retained'], 12)
        report = self.summarize([10]*12, drift=10.01)
        self.assertEqual(report['retained'], 0)
        self.assertEqual(report['envelopes'][0]['excluded'], ['start_drift'])

    def test_foreign_group_eperm_is_logged_absence_alone_proves_cleanup(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            path = Path(tmp)/'groups.jsonl'
            campaign.append_event(path, {'kind':'power','pgid':99999999})
            with patch.object(campaign, 'group_absent', side_effect=[False, True]), \
                    patch.object(campaign.os, 'killpg', side_effect=PermissionError('foreign group')):
                result = campaign.cleanup_groups(path, budget_s=1)
            self.assertTrue(result['cleanup_proven'], result)
            self.assertTrue(result['signal_errors'])
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['residue'], [])

    def test_missing_journal_trivially_clean_malformed_journal_returns_error(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            path = Path(tmp)/'groups.jsonl'
            self.assertTrue(campaign.cleanup_groups(path)['cleanup_proven'])
            path.write_text('{bad')
            result = campaign.cleanup_groups(path)
            self.assertFalse(result['cleanup_proven'])
            self.assertTrue(result['errors'])

    def test_disjoint_pairs_drop_exactly_one_original_pair_for_each_exclusion(self):
        original = {(1,2), (3,4), (5,6), (7,8), (9,10), (11,12)}
        for excluded in range(1, 13):
            with self.subTest(excluded=excluded):
                report = self.summarize(range(1, 13), excluded=[excluded])
                pairs = {(d['left'], d['right']) for d in report['sizing_pairs']}
                left = excluded if excluded % 2 else excluded - 1
                self.assertEqual(pairs, original - {(left, left + 1)})
                self.assertEqual([d['delta_j'] for d in report['sizing_pairs']], [1] * 5)
                self.assertEqual(report['retained_pairs'], 5)
                self.assertEqual(report['status'], 'SPREAD_RECORDED')
                self.assertEqual(len(report['adjacent_pairs']), 11)
        report = self.summarize(range(1, 13), missing=[3])
        self.assertEqual({(d['left'], d['right']) for d in report['sizing_pairs']}, original - {(3,4)})
        self.assertNotIn((2,4), {(d['left'], d['right']) for d in report['adjacent_pairs']})

    def test_four_pairs_minimum_even_when_eight_envelopes_survive(self):
        report = self.summarize(range(1, 13), excluded=[1,3,5,7])
        self.assertEqual(report['retained'], 8)
        self.assertEqual(report['retained_pairs'], 2)
        self.assertEqual(report['status'], 'INCONCLUSIVE')
        self.assertIsNone(report['s_upper'])
        self.assertIsNone(report['block_two_pairs'])
        self.assertEqual(report['block_two_stop']['outcome'], 'no decision')
        self.assertFalse(report['top_up'])
        for excluded in ([1,3,5], [1,3]):
            report = self.summarize(range(1, 13), excluded=excluded)
            self.assertEqual(report['status'], 'INCONCLUSIVE' if len(excluded) == 3 else 'SPREAD_RECORDED')
            self.assertEqual(report['block_two_pairs'], None if len(excluded) == 3 else 3)

    def test_chi_square_quantiles_and_n_six_n_four_factors(self):
        # Independent reference quantiles, not recomputed with the implementation.
        for df, quantile in ((3, .5843743741551835), (4, 1.063623216779224),
                             (5, 1.6103079869623227), (11, 5.57778478979985)):
            self.assertAlmostEqual(campaign.chi_square_lower_decile(df), quantile, places=11)
        for df in (2, 12, True, 3.0):
            with self.assertRaises(ValueError):
                campaign.chi_square_lower_decile(df)
        for excluded, factor, df in (([], 1.762, 5), ([1,3], 2.266, 3)):
            report = self.summarize([10,9.5, 10,9.7, 10,9.9, 10,10.1, 10,10.3, 10,10.5], excluded=excluded)
            self.assertAlmostEqual(report['s_upper_factor'], factor, places=3)
            self.assertEqual(report['pair_df'], df)
            if df == 3:
                self.assertAlmostEqual(report['pair_sd_j'], math.sqrt(1 / 15), places=12)
                self.assertAlmostEqual(report['s_upper'], math.sqrt(.2 / .5843743741551835), places=12)

    def test_overlapping_and_single_values_are_diagnostics_never_sizing(self):
        # Large between-pair drift; small disjoint differences. Using either
        # the overlapping series or single values for sizing must fail here.
        energies = [100, 99.5, 200, 199.7, 300, 299.9, 400, 400.1, 500, 500.3, 600, 600.5]
        report = self.summarize(energies)
        self.assertEqual([v['joules'] for v in report['envelopes']], energies)
        self.assertEqual(len(report['adjacent_pairs']), 11)
        self.assertEqual(len(report['sizing_pairs']), 6)
        self.assertAlmostEqual(report['pair_sd_j'], math.sqrt(.14), places=12)
        self.assertAlmostEqual(report['s_upper'], math.sqrt(.14 * 5 / 1.6103079869623227), places=12)
        self.assertEqual(report['block_two_pairs'], 4)  # point SD alone gives 3
        self.assertGreater(report['adjacent_pair_sd_j'], 50)
        self.assertGreater(report['single_envelope_sd_j'], 100)
        self.assertEqual(report['first_to_last_retained_drift_j'], 500.5)
        self.assertEqual([(d['left'], d['right']) for d in report['pairs_above_3_pair_sd']],
                         [(2,3), (4,5), (6,7), (8,9), (10,11)])
        self.assertEqual(report['block_two_stop']['outcome'], 'no decision')
        self.assertEqual(report['evidence_status'], 'PROVISIONAL')
        self.assertFalse(report['cutoff_authority'])

    def test_summary_sizing_floor_and_stop_above_24_pairs(self):
        report = self.summarize([10] * 12)
        self.assertEqual(report['s_upper'], 0)
        self.assertEqual(report['block_two_pairs'], 3)
        report = self.summarize([10,9, 10,9, 10,9, 10,11, 10,11, 10,11])
        self.assertEqual(report['block_two_pairs'], 30)
        self.assertEqual(report['block_two_stop']['outcome'], 'no cutoff qualifies')
        self.assertEqual(report['block_two_stop']['causes'], ['sized_pairs_above_24'])
        self.assertEqual(campaign.stop_branch(s_upper=math.sqrt(3))['pairs'], 24)
        self.assertEqual(campaign.stop_branch(s_upper=math.sqrt(3))['outcome'], 'no decision')

    def test_frozen_protocol_and_size_use_upper_bound_not_sd(self):
        sha = campaign.digest((ROOT / campaign.CHAIN_PATH).read_bytes())
        self.assertEqual(campaign.validate_protocol(PROTOCOL, sha), PROTOCOL)
        self.assertEqual(PROTOCOL['minimum_adjacent_pairs'], 4)
        self.assertEqual(PROTOCOL['sizing']['delta_j'], 1)
        self.assertEqual(PROTOCOL['sizing']['multiplier'], 8)
        self.assertEqual(PROTOCOL['sizing']['chi_square_lower_tail_probability'], .10)
        self.assertEqual(PROTOCOL['sizing']['confidence'], .90)
        self.assertEqual(PROTOCOL['sizing']['minimum_pairs'], 3)
        self.assertEqual(PROTOCOL['sizing']['maximum_pairs'], 24)
        self.assertEqual(PROTOCOL['sizing']['reference_factors'], {'n_6':1.762, 'n_4':2.266})
        self.assertEqual(PROTOCOL['pairing_rule'], 'disjoint_original_adjacent_pairs_both_retained_no_bridging')
        self.assertIn('normally distributed', PROTOCOL['sizing']['assumption'])
        self.assertIn('normality of the pair\ndifferences are assumptions',
                      (ROOT / 'configs/campaigns/quiet_predicate_evidence_01/README.md').read_text())
        for key in ('settle_s','envelopes','envelope_s','interior_s','sample_interval_s','window_max_s',
                    'minimum_adjacent_pairs', 'pairing_rule'):
            with self.assertRaises(ValueError):
                campaign.validate_protocol({**PROTOCOL,key:1}, sha)
        self.assertEqual(campaign.size_block_two(.3), 3)
        self.assertEqual(campaign.size_block_two(1), 8)
        self.assertGreater(campaign.size_block_two(2), 24)
        for upper in (None, True, float('nan'), -1):
            with self.assertRaises(ValueError):
                campaign.size_block_two(upper)

    def test_all_five_sizing_constants_are_read_from_frozen_protocol(self):
        import copy
        sha = campaign.digest((ROOT / campaign.CHAIN_PATH).read_bytes())
        self.assertEqual(PROTOCOL['block_two']['smallest_holdable_share'], .05)
        for section, key, value in (('sizing','delta_j',2), ('sizing','multiplier',4),
                ('sizing','minimum_pairs',5), ('sizing','maximum_pairs',7),
                ('block_two','smallest_holdable_share',.2)):
            changed = copy.deepcopy(PROTOCOL)
            changed[section][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                campaign.validate_protocol(changed, sha)
            # Isolate consumers: the runtime cannot bypass file-owned values.
            with patch.object(campaign, 'frozen_protocol', return_value=changed):
                expected = max(changed['sizing']['minimum_pairs'], math.ceil(changed['sizing']['multiplier'] / changed['sizing']['delta_j']**2))
                self.assertEqual(campaign.size_block_two(1), expected)
                self.assertEqual(campaign.size_block_two(0), changed['sizing']['minimum_pairs'])
                stop = campaign.stop_branch(s_upper=1, observer_floor=.1)
                self.assertEqual('sized_pairs_above_24' in stop['causes'], expected > changed['sizing']['maximum_pairs'])
                self.assertEqual('observer_floor_above_smallest_holdable_share' in stop['causes'], .1 > changed['block_two']['smallest_holdable_share'])
        for key in ('sizing', 'stop_branches', 'exclusions', 'power_interval_ms', 'start_drift_max_s', 'block_two'):
            changed = copy.deepcopy(PROTOCOL)
            changed.pop(key)
            with self.subTest(missing=key), self.assertRaises(ValueError):
                campaign.validate_protocol(changed, sha)

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
                           'network_time_provenance': provenance(),
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
            self.assertEqual(report['status'], 'INCONCLUSIVE')  # fewer than four fixed disjoint pairs
            self.assertEqual(len(report['envelopes']), 12)
            self.assertNotIn({'left':2,'right':4,'delta_j':2}, report['adjacent_pairs'])
            self.assertIsNone(report['s_upper'])  # insufficient retained disjoint pairs
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
    def exercise(self, errors=(), cleanup_failures=(), recorder_dead=False,
                 off_stdout=None, on_exit=0, timed_log="", commands=None,
                 interrupt_settle=False, protocol=None, burn=0, stepped_stop_s=0,
                 window_max_s=9000, spy=None):
        """Drive the real ``execute`` against a stub collector on a fake clock.

        ``burn`` is the seconds the stub collector spends AFTER its capture
        before it exits -- the finalisation tail (recorder exit wait, plist
        parse, anchor derive) that A269 measured at 7.6-10.2 s on the real
        night.  It is the whole counterfactual: under the pre-cure schedule
        the tail pushed the next spawn late and nothing noticed.
        """
        from contextlib import ExitStack
        from dataclasses import replace
        from types import SimpleNamespace
        from tests.test_night_gate import make_plan
        protocol = PROTOCOL if protocol is None else protocol
        envelope_s = protocol['envelope_s']
        calls, processes = [], {}
        class Clock:
            now = 0.
            interrupt = interrupt_settle
            def monotonic(self): return self.now
            def time(self): return 1000+self.now
            def sleep(self, seconds):
                self.now += seconds
                if self.interrupt and seconds == protocol['settle_s']:
                    # Exactly what the executor's own SIGTERM handler raises.
                    self.interrupt = False
                    raise InterruptedError('evidence chain signal 15')
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
                    self.index = index
                    self.end = float(argv[argv.index('--envelope-start-mono-s')+1])+envelope_s
                    # Both clocks stamp both ends: the monotonic pair gives the
                    # capture's length and the wall pair its position, which is
                    # what the union window (ruling 10 Q4 i) reads.
                    # ``stepped_stop_s`` displaces the stop stamp's WALL
                    # reading only, exactly as a clock step would.
                    session={'session':'fixture','os_build':'25G83','boot_id':'boot','start_drift_s':0,
                        'network_time_provenance':{k:v for k,v in provenance().items() if k!='attestation'},
                        'power':{'anchor':{'status':'bounded','clock_stamps':{
                            'sampling_started':{'epoch_s':1000+self.end-envelope_s,
                                                'monotonic_before_s':self.end-envelope_s},
                            'sampling_stopped':{'epoch_s':1000+self.end+stepped_stop_s,
                                                'monotonic_before_s':self.end}}}},
                        'interior':{'complete_support':True,
                        'power':{'energy_j':{'rail_sum_w':index,'combined_w':index}}}}
                    (out/'session.json').write_text(json.dumps(session))
                    (out/'rounds.jsonl').write_text(json.dumps(good_round())+'\n')
            def poll(self):
                if recorder_dead and 'record' in self.argv:
                    self.returncode = 1
                return self.returncode
            def wait(self, timeout):
                clock.now = max(clock.now, self.end) + burn
                self.returncode = 1 if self.index in errors else 0
                return self.returncode
        real_cleanup = campaign.cleanup_groups
        cleanup_count = 0
        self.slot_cleanup_budgets = []
        def cleanup(*args, **kwargs):
            nonlocal cleanup_count
            result = real_cleanup(*args, **kwargs)
            if kwargs.get('exclude'):
                cleanup_count += 1
                self.slot_cleanup_budgets.append(result['budget_s'])
                if cleanup_count in cleanup_failures:
                    result['cleanup_proven'] = False
            return result
        def terminate(pgid, sig): processes[pgid].returncode = -sig
        # Only the OS boundary is faked: set_network_time, the exact-stdout
        # comparator, the timed-log argv, the scanner and the atomic session
        # rewrite all run for real (the fake sudo/log regressions below run
        # real executables through the same constants).
        def run(argv, **kwargs):
            from subprocess import CompletedProcess
            if argv[0] == campaign.SUDO:
                state = argv[-1]
                stdout = (EXPECTED_OFF if off_stdout is None else off_stdout) \
                    if state == 'off' else 'setUsingNetworkTime: On\n'
                return CompletedProcess(argv, 0 if state == 'off' else on_exit, stdout, '')
            if argv[0] == campaign.LOG:
                return CompletedProcess(argv, 0, timed_log, '')
            raise AssertionError(f'unexpected command {argv}')
        real_popen = campaign.subprocess.Popen
        def popen(argv, **kwargs):
            # With real fake EXECUTABLES bound to the constants, the sudo and
            # log calls go through the real subprocess machinery; only the
            # night's own children stay simulated.
            if commands and str(argv[0]) in {str(commands[0]), str(commands[1])}:
                return real_popen(argv, **kwargs)
            return Child(argv, **kwargs)
        with ExitStack() as stack:
            enter = stack.enter_context
            tmp = enter(tempfile.TemporaryDirectory())
            enter(patch.object(campaign,'time',clock))
            if commands:
                enter(patch.object(campaign,'SUDO',str(commands[0])))
                enter(patch.object(campaign,'LOG',str(commands[1])))
                enter(patch.object(campaign.subprocess,'Popen',side_effect=popen))
            else:
                enter(patch.object(campaign.subprocess,'run',side_effect=run))
                enter(patch.object(campaign.subprocess,'Popen',side_effect=Child))
            enter(patch.object(campaign,'group_absent',side_effect=lambda pgid:processes[pgid].returncode is not None))
            enter(patch.object(campaign.os,'killpg',side_effect=terminate))
            enter(patch.object(campaign,'cleanup_groups',side_effect=cleanup))
            if spy is not None:
                spy(stack, campaign)
            plan=replace(make_plan(),t0_epoch_s=1000,window_max_s=window_max_s)
            rc = campaign.execute(plan,protocol,Path(tmp))
            cleanup=json.loads((Path(tmp)/'evidence_cleanup.json').read_text())
            self.assertTrue(cleanup['cleanup_proven'])
            journal=Path(tmp)/'evidence_envelopes.jsonl'
            self.envelope_journal=[json.loads(line) for line in
                                   journal.read_text().splitlines() if line] if journal.exists() else []
            self.envelope_directories=sorted(
                p.name for p in (Path(tmp)/'evidence').glob('envelope-*'))
            self.timed_logs=sorted(
                p.read_text() for p in (Path(tmp)/'evidence').glob('envelope-*/timed-log.txt'))
            summary=json.loads((Path(tmp)/'evidence/summary.json').read_text())
            outcome=json.loads((Path(tmp)/'evidence_outcome.json').read_text())
            refusals=list(Path(tmp).glob('refusal*.json'))
            control=json.loads((Path(tmp)/campaign.NETWORK_TIME_CONTROL_BASENAME).read_text())
            sessions=[json.loads(path.read_text())
                      for path in sorted((Path(tmp)/'evidence').glob('envelope-*/session.json'))]
            return rc, summary, outcome, len(refusals), calls, control, sessions

    def test_twelve_protocol_envelopes_one_recorder_no_load_and_cleanup(self):
        rc, summary, outcome, refusals, calls, *_ = self.exercise()
        self.assertEqual(rc, 0)
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

    def test_envelope_three_collect_error_continues_frozen_cadence_retains_eleven(self):
        rc, summary, outcome, refusals, calls, *_ = self.exercise(errors={3})
        self.assertEqual(rc, 0)
        self.assertEqual(outcome['envelopes_attempted'], 12)
        self.assertEqual(summary['retained'], 11)
        self.assertEqual(summary['envelopes'][2]['excluded'], ['collect_error'])
        self.assertEqual(outcome['outcome'], 'partial')
        self.assertEqual(refusals, 0)
        # A269 cure 2: the SPAWNS run on slot_pitch_s (620 s), the captures
        # keep envelope_s (600 s); the 20 s difference is the gap the
        # finalisation tail, teardown and attestation live in.
        starts = [float(a[a.index('--envelope-start-mono-s')+1]) for a in calls if 'collect' in a]
        self.assertEqual(starts, [600 + 620 * i for i in range(12)])
        durations = {a[a.index('--duration-s')+1] for a in calls if 'collect' in a}
        self.assertEqual(durations, {'600'})

    def test_isolated_cleanup_unproven_continues_but_two_consecutive_refuse(self):
        for failures, attempted, retained, refusal_count in (({3}, 12, 11, 0), ({3,5}, 12, 10, 0), ({3,4}, 4, 2, 1)):
            with self.subTest(failures=failures):
                rc, summary, outcome, refusals, *_ = self.exercise(cleanup_failures=failures)
                self.assertEqual(outcome['envelopes_attempted'], attempted)
                self.assertEqual(summary['retained'], retained)
                self.assertEqual(summary['envelopes'][2]['excluded'], ['cleanup_unproven'])
                self.assertEqual(refusals, refusal_count)
                self.assertEqual(rc, 2 if refusal_count else 0)

    def test_dead_covariate_recorder_refuses_with_document(self):
        rc, summary, outcome, refusals, *_ = self.exercise(recorder_dead=True)
        self.assertEqual(rc, 2)
        self.assertEqual(outcome['envelopes_attempted'], 1)
        self.assertEqual(refusals, 1)


# --------------------------------------------------------------------------
# A267 QPE01-CLOCK-DISCIPLINE-ANCHOR-01 — cold-gate regressions 7 and 12
# (ruling 10 Q1 rules 1-5, rebuttal ruling 14 R4).  The sudo and log calls run
# REAL executables here: fake scripts bound to the module constants, because
# an absolute argv cannot be faked through PATH.
# --------------------------------------------------------------------------

FIXTURES = ROOT / "tests/fixtures/qpe01_pilot_n1_20260922"


class NetworkTimeControlTests(FrozenExecutorTests):
    """The night establishes OFF, attests every envelope, and restores ON."""

    def fake_commands(self, *, off_stdout=None, off_exit=0, on_exit=0, timed_log=""):
        import shutil
        import stat
        directory = Path(tempfile.mkdtemp(dir="/tmp"))
        self.addCleanup(shutil.rmtree, directory)
        off = EXPECTED_OFF if off_stdout is None else off_stdout
        log_file = directory / "timed.txt"
        log_file.write_text(timed_log)
        # The stdout bytes live in files, so the fake prints them verbatim:
        # a shell escape would be the one thing the exact comparator tests.
        (directory / "off-stdout.txt").write_text(off)
        (directory / "on-stdout.txt").write_text("setUsingNetworkTime: On\n")
        sudo = directory / "sudo"
        sudo.write_text(
            "#!/bin/sh\n"
            f'printf %s "$@" >> "{directory}/sudo-calls.txt"\n'
            f'printf "\\n" >> "{directory}/sudo-calls.txt"\n'
            'if [ "$4" = "off" ]; then\n'
            f'  cat "{directory}/off-stdout.txt"\n'
            f"  exit {off_exit}\n"
            "fi\n"
            f'cat "{directory}/on-stdout.txt"\n'
            f"exit {on_exit}\n")
        log = directory / "log"
        log.write_text(f'#!/bin/sh\nprintf %s "$@" >> "{directory}/log-calls.txt"\n'
                       f'cat "{log_file}"\n')
        for path in (sudo, log):
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        self.command_directory = directory
        return sudo, log

    def sudo_calls(self):
        path = self.command_directory / "sudo-calls.txt"
        return path.read_text().splitlines() if path.exists() else []

    def test_exact_off_stdout_reaches_settle_and_records_both_toggles(self):
        commands = self.fake_commands()
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands)
        self.assertEqual(rc, 0)
        self.assertEqual(refusals, 0)
        self.assertEqual(len(self.envelope_directories), 12)
        self.assertEqual(control["schema"], "joulewise.network_time_control.v1")
        self.assertEqual(control["off"]["exit_code"], 0)
        self.assertEqual(control["off"]["stdout"], EXPECTED_OFF)
        self.assertEqual(control["off"]["argv"][1:],
                         ["-n", campaign.SYSTEMSETUP, "-setusingnetworktime", "off"])
        self.assertEqual(control["on"]["exit_code"], 0)
        self.assertEqual(control["on"]["argv"][-1], "on")
        self.assertTrue(outcome["network_time_restored"])
        # The receipt reaches every collector, and OFF precedes the settle.
        self.assertEqual(self.sudo_calls()[0],
                         f"-n{campaign.SYSTEMSETUP}-setusingnetworktimeoff")
        self.assertEqual(self.sudo_calls()[-1],
                         f"-n{campaign.SYSTEMSETUP}-setusingnetworktimeon")
        self.assertEqual(summary["retained"], 12)

    def test_lower_case_stdout_or_nonzero_exit_refuses_before_any_envelope(self):
        for label, kwargs in (("lower case", {"off_stdout": "setUsingNetworkTime: off\n"}),
                              ("exit 1", {"off_exit": 1})):
            with self.subTest(case=label):
                commands = self.fake_commands(**kwargs)
                rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
                    commands=commands)
                self.assertEqual(rc, 2)
                self.assertEqual(refusals, 1)
                self.assertEqual(self.envelope_directories, [])
                self.assertEqual(calls, [])  # no recorder, no collector
                self.assertEqual(outcome["outcome"], "refused")
                self.assertIn("network time OFF not established", outcome["error"])
                # The refused attempt AND the restore are both on the record.
                self.assertEqual(control["off"]["stdout"],
                                 kwargs.get("off_stdout", EXPECTED_OFF))
                self.assertEqual(control["off"]["exit_code"], kwargs.get("off_exit", 0))
                self.assertEqual(control["on"]["exit_code"], 0)
                self.assertTrue(outcome["network_time_restored"])

    def test_termination_during_settle_still_restores_network_time(self):
        commands = self.fake_commands()
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands, interrupt_settle=True)
        self.assertEqual(rc, 2)
        self.assertEqual(self.envelope_directories, [])
        self.assertIn("InterruptedError", outcome["error"])
        self.assertEqual(control["on"]["exit_code"], 0)
        self.assertTrue(outcome["network_time_restored"])

    def test_failed_restore_is_reported_with_its_own_exit_code(self):
        commands = self.fake_commands(on_exit=1)
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands)
        # The envelopes were captured under a proven OFF; their validity is
        # unaffected, so the night is not refused.  Only the machine state is
        # wrong, and it gets its own code so the harvester re-attempts it.
        self.assertEqual(rc, 3)
        self.assertEqual(outcome["outcome"], "complete")
        self.assertFalse(outcome["network_time_restored"])
        self.assertEqual(control["on"]["exit_code"], 1)
        self.assertEqual(summary["retained"], 12)

    def test_every_envelope_is_attested_from_the_timed_log(self):
        commands = self.fake_commands()
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands)
        self.assertEqual(len(sessions), 12)
        for session in sessions:
            attestation = session["network_time_provenance"]["attestation"]
            self.assertEqual(attestation["state"], "authenticated")
            self.assertEqual(attestation["method"], "timed_log_show_predicate_v1")
            self.assertEqual(attestation["matched_lines"], 0)
            self.assertEqual(attestation["log"], "timed-log.txt")
            self.assertEqual(attestation["log_sha256"], campaign.digest(b""))
            window = attestation["window_epoch_s"]
            self.assertAlmostEqual(window[1] - window[0], 602)
        self.assertEqual(len(self.timed_logs), 12)
        self.assertEqual([v["excluded"] for v in summary["envelopes"]], [[]] * 12)

    def test_an_applied_slew_inside_a_window_excludes_that_night_envelope(self):
        commands = self.fake_commands(timed_log=(FIXTURES / "exhibit-D-timed-log.txt").read_text())
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands)
        for session in sessions:
            attestation = session["network_time_provenance"]["attestation"]
            self.assertEqual(attestation["state"], "slew_attested")
            self.assertEqual(attestation["matched_lines"], 10)
        self.assertEqual(summary["retained"], 0)
        self.assertEqual([v["excluded"] for v in summary["envelopes"]],
                         [["network_time_slew_attested"]] * 12)
        self.assertEqual(summary["status"], "INCONCLUSIVE")

    def test_the_production_commands_are_the_ruled_absolute_argv(self):
        self.assertEqual(campaign.SUDO, "/usr/bin/sudo")
        self.assertEqual(campaign.SYSTEMSETUP, "/usr/sbin/systemsetup")
        self.assertEqual(campaign.LOG, "/usr/bin/log")
        self.assertEqual(campaign.network_time_argv("off"),
                         ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup",
                          "-setusingnetworktime", "off"))
        self.assertEqual(campaign.network_time_argv("on"),
                         ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup",
                          "-setusingnetworktime", "on"))
        self.assertEqual(campaign.EXPECTED_NETWORK_TIME_OFF_STDOUT,
                         "setUsingNetworkTime: Off\n")
        argv = campaign.timed_log_argv(1790073429.0, 1790074020.0)
        self.assertEqual(argv[:8], ("/usr/bin/log", "show", "--info", "--debug",
                                    "--style", "syslog", "--predicate",
                                    'process == "timed"'))
        self.assertEqual(argv[8], "--start")
        self.assertEqual(argv[10], "--end")
        for value in (argv[9], argv[11]):
            self.assertRegex(value, r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$")


class TimedLogScannerTests(unittest.TestCase):
    """Regression 12: the scanner over the packet's own exhibit D."""

    def test_exhibit_d_has_ten_applied_corrections_and_a_clean_log_has_none(self):
        text = (FIXTURES / "exhibit-D-timed-log.txt").read_text()
        self.assertEqual(len(text.splitlines()), 191)
        self.assertEqual(campaign.timed_log_matches(text), 10)
        clean = "\n".join(line for line in text.splitlines()
                          if not any(marker in line for marker in campaign.TIMED_LOG_MARKERS))
        self.assertEqual(campaign.timed_log_matches(clean), 0)
        self.assertEqual(campaign.timed_log_matches(""), 0)
        for marker in ("ntp_adjtime", "settimeofday"):
            self.assertEqual(campaign.timed_log_matches(f"a {marker} b"), 1)

    def test_only_an_authenticated_state_keeps_an_envelope_claim_bearing(self):
        self.assertEqual(campaign.attestation_exclusions("authenticated"), [])
        self.assertEqual(campaign.attestation_exclusions("slew_attested"),
                         ["network_time_slew_attested"])
        for state in ("asserted", None, "unknown"):
            self.assertEqual(campaign.attestation_exclusions(state),
                             ["network_time_unattested"])

    def test_a_failed_log_query_is_asserted_not_authenticated(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp)
            (out / "session.json").write_text(json.dumps({"power": {"anchor": {"clock_stamps": {
                "sampling_started": {"epoch_s": 1000.0},
                "sampling_stopped": {"epoch_s": 1600.0}}}}}))
            with patch.object(campaign.subprocess, "run",
                              return_value=SimpleNamespace(returncode=1, stdout="", stderr="")):
                attestation = campaign.attest_network_time(out)
            self.assertEqual(attestation["state"], "asserted")
            self.assertEqual(attestation["exit_code"], 1)
            self.assertEqual(attestation["window_epoch_s"], [999.0, 1601.0])
            # A missing capture window is also asserted, never authenticated.
            (out / "session.json").write_text("{}")
            with patch.object(campaign.subprocess, "run",
                              side_effect=AssertionError("must not query")):
                self.assertEqual(campaign.attest_network_time(out)["state"], "asserted")

    def test_the_session_rewrite_is_atomic_and_keeps_the_collector_provenance(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp)
            original = {"session": "fixture",
                        "network_time_provenance": {k: v for k, v in provenance().items()
                                                    if k != "attestation"}}
            (out / "session.json").write_text(json.dumps(original))
            attestation = {"state": "authenticated", "matched_lines": 0}
            real_replace = campaign.os.replace
            seen = {}
            def replace(source, target):
                seen["temporary"] = Path(source).name
                seen["existing"] = json.loads(Path(target).read_text())
                return real_replace(source, target)
            with patch.object(campaign.os, "replace", side_effect=replace):
                self.assertTrue(campaign.record_attestation(out, attestation))
            self.assertEqual(seen["temporary"], "session.json.tmp")
            # The destination still held the complete previous record when the
            # rename happened: no reader ever sees a partial file.
            self.assertEqual(seen["existing"], original)
            session = json.loads((out / "session.json").read_text())
            self.assertEqual(session["network_time_provenance"]["attestation"], attestation)
            self.assertEqual(session["network_time_provenance"]["state"], "off")
            self.assertEqual(session["session"], "fixture")
            self.assertFalse(list(out.glob("*.tmp")))
