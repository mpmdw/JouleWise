"""Campaign mechanics and negative scientific branches using fixtures only."""
import json
import math
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock
from joulewise import quiet_predicate_campaign as campaign
from joulewise import night_gate

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads((ROOT / campaign.PROTOCOL_PATH).read_text())
EXPECTED_OFF = campaign.EXPECTED_NETWORK_TIME_OFF_STDOUT
# What `log show --style syslog` prints before any entry, and prints even
# when the predicate matched nothing: the first line of the two LIVE captures
# taken with the ruled argv (fixtures exhibit-D2/exhibit-D3 below).  A fake
# log that omits it is a query that did not run.  The packet's exhibit D was
# captured in `--style compact`, whose header is a DIFFERENT line; it is a
# negative fixture from here on (cold gate #3 Q2, Q6).
TIMED_LOG_HEADER = campaign.TIMED_LOG_SYSLOG_HEADER + "\n"


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
    def summarize(self, energies, excluded=(), missing=(), observer_core=None, recorder=False,
                  drift=0, slew=()):
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
                    'network_time_provenance': provenance(
                        *(('slew_attested', 1) if index in slew else ())),
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

    def test_a_slew_attested_envelope_never_feeds_the_clean_busy_core_diagnostic(self):
        # Item 13 (05a N4).  Envelope 05 carries the recorder's 99-core
        # excursion AND an applied clock correction inside its window.  It is
        # excluded by name, and the "clean machine" distribution -- which
        # describes the machine the retained envelopes were captured on --
        # must not be shaped by it.  Before the fix the attestation was
        # computed after the busy-core join, so it was.
        report = self.summarize([10] * 12, recorder=True, slew={5})
        self.assertEqual(report['envelopes'][4]['excluded'], ['network_time_slew_attested'])
        self.assertEqual(report['retained'], 11)
        self.assertEqual(report['envelopes'][4]['busy_cores']['max'], 99)
        self.assertEqual(report['clean_machine_busy_cores']['max'], .01)
        self.assertEqual(report['busy_cores']['max'], .01)

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
                 off_stdout=None, on_exit=0, timed_log=None, commands=None,
                 interrupt_settle=False, protocol=None, burn=0, burn_at=None,
                 settle_overshoot=0, stepped_stop_s=0, window_max_s=9000, spy=None,
                 attest_burn=0, tolerate_raise=False):
        """Drive the real ``execute`` against a stub collector on a fake clock.

        ``burn`` is the seconds the stub collector spends AFTER its capture
        before it exits -- the finalisation tail (recorder exit wait, plist
        parse, anchor derive) that A269 measured at 7.6-10.2 s on the real
        night.  It is the whole counterfactual: under the pre-cure schedule
        the tail pushed the next spawn late and nothing noticed.  ``burn_at``
        is the same thing for one named envelope, and ``settle_overshoot``
        delays envelope 01 alone (the slot that follows the settle and tests
        no pitch).  ``timeline`` records each spawn and each attestation in
        order, so the placement of the clock query can be asserted.

        ``attest_burn`` stands in for a clock query that spends its whole
        bound and times out: the fake clock advances by that many seconds and
        the query returns the ``asserted`` state a timeout produces, so the
        cost of the query on the inter-slot path is measurable without any
        real waiting.  ``self.attestation_kwargs`` keeps what ``execute``
        passed each query, so the bound itself can be pinned.
        """
        from contextlib import ExitStack
        from dataclasses import replace
        from types import SimpleNamespace
        from tests.test_night_gate import make_plan
        protocol = PROTOCOL if protocol is None else protocol
        envelope_s = protocol['envelope_s']
        burn_at = burn_at or {}
        calls, processes = [], {}
        self.timeline = timeline = []
        class Clock:
            now = 0.
            interrupt = interrupt_settle
            def monotonic(self): return self.now
            def time(self): return 1000+self.now
            def sleep(self, seconds):
                self.now += seconds
                if seconds == protocol['settle_s']:
                    self.now += settle_overshoot
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
                    timeline.append(('spawn', int(argv[argv.index('--repeat')+1])))
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
                clock.now = max(clock.now, self.end) + burn + burn_at.get(self.index, 0)
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
                return CompletedProcess(
                    argv, 0, TIMED_LOG_HEADER if timed_log is None else timed_log, '')
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
            real_attest = campaign.attest_network_time
            self.attestation_kwargs = []
            def attest(out, **kwargs):
                # Every supervised child of this envelope must already be
                # reaped when the clock query runs: `log show` beside a live
                # recorder is observer energy inside a recorded window.
                live = [c for c in processes.values()
                        if 'collect' in c.argv and c.returncode is None]
                self.attestation_kwargs.append(kwargs)
                if attest_burn:
                    clock.now += attest_burn
                    attestation = {'state': 'asserted', 'matched_lines': None,
                                   'reason': f'timed log query timed out after {attest_burn:g} s'}
                else:
                    attestation = real_attest(out, **kwargs)
                timeline.append(('attest', int(out.name.split('-')[1]),
                                 [c.pid for c in live], (out/'timed-log.txt').exists()))
                return attestation
            enter(patch.object(campaign,'attest_network_time',side_effect=attest))
            if spy is not None:
                spy(stack, campaign)
            plan=replace(make_plan(),t0_epoch_s=1000,window_max_s=window_max_s)
            self.execute_error=None
            try:
                rc = campaign.execute(plan,protocol,Path(tmp))
            except Exception as exc:
                if not tolerate_raise:
                    raise
                # A variant that breaks the `finally` deliberately: the only
                # readable artefact is whatever the finally wrote BEFORE the
                # break, which is exactly what the ordering assertion needs.
                self.execute_error=exc
                self.control_text=(Path(tmp)/campaign.NETWORK_TIME_CONTROL_BASENAME).read_text()
                return None, None, None, 0, calls, json.loads(self.control_text), []
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
            # The control record's BYTES are kept too: a test that corrupts it
            # asserts they survived the restore, and an unparsable record must
            # not break the harness before the assertion runs.
            self.control_text=(Path(tmp)/campaign.NETWORK_TIME_CONTROL_BASENAME).read_text()
            try:
                control=json.loads(self.control_text)
            except ValueError:
                control=None
            receipt=Path(tmp)/campaign.NETWORK_TIME_RESTORE_BASENAME
            self.restore_receipt=json.loads(receipt.read_text()) if receipt.exists() else None
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
# The compact capture stays as the marker/envelope corpus and becomes the
# NEGATIVE header fixture; the two syslog captures are its production-format
# twins, taken by the ruled argv on the 2026-09-22 pilot night.  Their bytes
# are pinned here, so a fixture edited into agreement with the guard is a
# failing test rather than a silent re-definition of what the guard means.
COMPACT_FIXTURE = FIXTURES / "exhibit-D-timed-log.txt"
SYSLOG_FIXTURE = FIXTURES / "exhibit-D2-timed-log-0210-0435-syslog.txt"
ZERO_MATCH_FIXTURE = FIXTURES / "exhibit-D3-timed-log-zero-match-syslog.txt"
SYSLOG_FIXTURE_SHA256 = "dba7fb7cb92e9179a8e4d09e40290b578bbd68d12f29bb42eb417abcf6a4eb63"
ZERO_MATCH_FIXTURE_SHA256 = "da1b28eff7848fc42698579387fb9881a2bd1ceda8151ba16617a3b63550718b"


class NetworkTimeControlTests(FrozenExecutorTests):
    """The night establishes OFF, attests every envelope, and restores ON."""

    def fake_commands(self, *, off_stdout=None, off_exit=0, on_exit=0, timed_log=None,
                      off_sleep=0):
        import shutil
        import stat
        directory = Path(tempfile.mkdtemp(dir="/tmp"))
        self.addCleanup(shutil.rmtree, directory)
        off = EXPECTED_OFF if off_stdout is None else off_stdout
        log_file = directory / "timed.txt"
        log_file.write_text(TIMED_LOG_HEADER if timed_log is None else timed_log)
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
            # ``off_sleep`` outlasts the set form's own timeout: the one way a
            # toggle leaves without an exit code of its own.
            + (f'  sleep {off_sleep}\n' if off_sleep else "")
            + f'  cat "{directory}/off-stdout.txt"\n'
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
        toggles = []
        def spy(stack, module):
            # The real set form still runs; this only reads the clock at the
            # instant each toggle is issued (item 10 / 05a S3).
            real = module.set_network_time
            def watched(state):
                toggles.append((state, module.time.monotonic()))
                return real(state)
            stack.enter_context(patch.object(module, "set_network_time", side_effect=watched))
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands, interrupt_settle=True, spy=spy)
        self.assertEqual(rc, 2)
        self.assertEqual(self.envelope_directories, [])
        self.assertIn("InterruptedError", outcome["error"])
        self.assertEqual(control["on"]["exit_code"], 0)
        self.assertTrue(outcome["network_time_restored"])
        # Q1 rule 1's PLACEMENT, not just its argv order: the OFF receipt
        # exists on a night that died inside the settle, and the clock had not
        # yet advanced by settle_s when the toggle was issued -- so the settle
        # really does absorb any in-flight slew the daemon had started.  Moving
        # the toggle after the sleep leaves this night with no OFF receipt at
        # all, which is what the old assertions (on ``on`` alone) missed.
        self.assertIsNotNone(control["off"], "the night died inside the settle with no OFF receipt")
        self.assertEqual(control["off"]["stdout"], EXPECTED_OFF)
        self.assertEqual(control["off"]["exit_code"], 0)
        self.assertEqual([state for state, _ in toggles], ["off", "on"])
        self.assertEqual(toggles[0][1], 0.0)
        self.assertLess(toggles[0][1], PROTOCOL["settle_s"])
        self.assertGreaterEqual(toggles[1][1], PROTOCOL["settle_s"])

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
            self.assertEqual(attestation["log_sha256"],
                             campaign.digest(TIMED_LOG_HEADER.encode()))
            window = attestation["window_epoch_s"]
            self.assertAlmostEqual(window[1] - window[0], 602)
        self.assertEqual(len(self.timed_logs), 12)
        self.assertEqual([v["excluded"] for v in summary["envelopes"]], [[]] * 12)

    def test_an_applied_slew_inside_a_window_excludes_that_night_envelope(self):
        """R2.3 and R2.5: the twin corpora, one query format apart.

        The same ten applied corrections were captured twice on the pilot
        night -- once in `--style compact` (the retained exhibit D) and once
        in the ruled `--style syslog` (exhibit D2).  Everything the scanner
        measures is equal across the pair (`matched_lines` 10, marker lines
        30) and only the BYTES differ, so `log_sha256` differs.  The states
        differ, and that difference IS the cure: a body in the wrong format
        did not come from the ruled query, so it is `asserted` with the
        header reason (R2.3's end-to-end half).  The counterfactual at
        489b0953 is this pair exactly INVERTED -- the old guard asked only
        for "Timestamp" and "Process" in the first line, which the compact
        header carries and the syslog header (lower-case "(process)") does
        not, so it accepted the format the night never produces and rejected
        the one it does.
        """
        runs = {}
        for label, fixture, state, exclusion in (
                ("syslog (the ruled argv)", SYSLOG_FIXTURE, "slew_attested",
                 "network_time_slew_attested"),
                ("compact (negative fixture)", COMPACT_FIXTURE, "asserted",
                 "network_time_unattested")):
            with self.subTest(case=label):
                body = fixture.read_text()
                # Supplementary S3: ruling 14 R3 regression 12's scanner is
                # `timed_log_matches`, and it reads 10 on BOTH formats.
                self.assertEqual(campaign.timed_log_matches(body), 10)
                self.assertEqual(campaign.timed_log_marker_lines(body), 30)
                commands = self.fake_commands(timed_log=body)
                rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
                    commands=commands)
                self.assertEqual(len(sessions), 12)
                attestations = [session["network_time_provenance"]["attestation"]
                                for session in sessions]
                for attestation in attestations:
                    self.assertEqual(attestation["state"], state)
                    self.assertEqual(attestation["matched_lines"], 10)
                    self.assertEqual(attestation["matched_marker_lines"], 30)
                    if state == "asserted":
                        self.assertEqual(attestation["reason"],
                                         "timed log query returned no header")
                self.assertEqual(summary["retained"], 0)
                self.assertEqual([v["excluded"] for v in summary["envelopes"]],
                                 [[exclusion]] * 12)
                self.assertEqual(summary["status"], "INCONCLUSIVE")
                runs[state] = attestations
        for syslog, compact in zip(runs["slew_attested"], runs["asserted"]):
            self.assertEqual(syslog["matched_lines"], compact["matched_lines"])
            self.assertEqual(syslog["matched_marker_lines"], compact["matched_marker_lines"])
            self.assertNotEqual(syslog["log_sha256"], compact["log_sha256"])
        self.assertEqual(runs["slew_attested"][0]["log_sha256"],
                         campaign.digest(SYSLOG_FIXTURE.read_bytes()))
        self.assertEqual(runs["asserted"][0]["log_sha256"],
                         campaign.digest(COMPACT_FIXTURE.read_bytes()))

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
        # Ruling 14 R3 regression 12 runs over BOTH formats of the same ten
        # corrections: the retained compact capture and its syslog twin
        # (cold gate #3 Q2 R2.5, supplementary S3).
        for label, path in (("compact", COMPACT_FIXTURE), ("syslog", SYSLOG_FIXTURE)):
            with self.subTest(case=label):
                text = path.read_text()
                self.assertEqual(len(text.splitlines()), 191)
                self.assertEqual(campaign.timed_log_matches(text), 10)
                self.assertEqual(campaign.timed_log_marker_lines(text), 30)
                clean = "\n".join(line for line in text.splitlines()
                                  if not any(marker in line
                                             for marker in campaign.TIMED_LOG_MARKERS))
                self.assertEqual(campaign.timed_log_matches(clean), 0)
        # The zero-match capture is a header and nothing else.
        self.assertEqual(campaign.timed_log_matches(ZERO_MATCH_FIXTURE.read_text()), 0)
        self.assertEqual(campaign.timed_log_marker_lines(ZERO_MATCH_FIXTURE.read_text()), 0)
        text = COMPACT_FIXTURE.read_text()
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
                "sampling_started": {"epoch_s": 1000.0, "monotonic_before_s": 50.0},
                "sampling_stopped": {"epoch_s": 1600.0, "monotonic_before_s": 650.0}}}}}))
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

    def test_every_attestation_record_names_what_was_queried_even_when_nothing_was(self):
        """R4: the skeleton carries `window_argv_epoch_s`, so no reader KeyErrors.

        `window_epoch_s` is the float union window the envelope was placed
        by; `window_argv_epoch_s` is what the argv strings say, parsed back
        from those same strings (A269 ruling 10 Q4 i, cold gate #3 Q4).  A
        record that never got as far as an argv still carries the key, with
        `null`, rather than omitting it -- the counterfactual at 489b0953 is
        a `KeyError` on every blocked and every window-unavailable record.
        """
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp)
            blocked = campaign.attest_network_time(
                out, blocked="one supervised group still alive", timeout=5)
            self.assertEqual(blocked["state"], "asserted")
            self.assertIsNone(blocked["window_epoch_s"])
            self.assertIsNone(blocked["window_argv_epoch_s"])
            # No session record at all, then one with no clock stamps: both
            # land in the "capture window unavailable" branch.
            for label, payload in (("no session record", None), ("no clock stamps", "{}")):
                with self.subTest(case=label):
                    path = out / "session.json"
                    path.unlink(missing_ok=True)
                    if payload is not None:
                        path.write_text(payload)
                    with patch.object(campaign.subprocess, "run",
                                      side_effect=AssertionError("must not query")):
                        attestation = campaign.attest_network_time(out, timeout=5)
                    self.assertEqual(attestation["state"], "asserted")
                    self.assertIn("capture window unavailable", attestation["reason"])
                    self.assertIsNone(attestation["window_argv_epoch_s"])
                    # It survives the journal as `null`, not as an absence.
                    self.assertIsNone(json.loads(json.dumps(attestation))["window_argv_epoch_s"])

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


# --------------------------------------------------------------------------
# A269 ENVELOPE-START-DRIFT-01 — cold-gate regressions 1-7 (ruling 10
# §Regressions) plus R-a and R-b (refuter 11, adopted in synthesis 15).
#
# The counterfactual for every cadence regression is the pre-cure harness: a
# schedule whose pitch IS the capture length, driven by a stub collector that
# burns time after its capture.  On the 2026-09-22 pilot that tail was
# 7.6-10.2 s and pushed every envelope after the first off its schedule; the
# scaled protocol below reproduces it in a 12 s slot.
# --------------------------------------------------------------------------

SCALED = {**PROTOCOL, 'envelope_s': 6, 'slot_pitch_s': 12, 'envelopes': 4,
          'start_drift_abort_s': 2, 'start_drift_max_s': 10}


class StartDriftCadenceTests(FrozenExecutorTests):
    """The pitch schedules, the capture measures, and a late spawn refuses."""

    def test_regression_1_the_pitch_absorbs_a_tail_longer_than_the_gap(self):
        # R-a: the stub burns 14 s, longer than the 6 s gap, so the cure cannot
        # simply absorb it -- the chain must REFUSE at the first late slot.
        rc, summary, outcome, refusals, calls, *_ = self.exercise(
            protocol=SCALED, burn=14)
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        self.assertIn('start_drift_abort', outcome['error'])
        self.assertEqual([row.get('abort') for row in self.envelope_journal],
                         [None, 'start_drift_abort'])
        aborted = self.envelope_journal[-1]
        self.assertEqual(aborted['index'], 2)
        self.assertAlmostEqual(aborted['start_drift_s'], 8)
        self.assertEqual(self.envelope_directories, ['envelope-01'])
        self.assertEqual(sum('collect' in cmd for cmd in calls), 1)
        # A tail that FITS the gap is absorbed silently and completely: every
        # slot starts on its scheduled instant, which is the whole point of
        # separating the pitch from the capture.
        rc, summary, outcome, refusals, calls, *_ = self.exercise(
            protocol=SCALED, burn=5)
        self.assertEqual(rc, 0)
        self.assertEqual(outcome['outcome'], 'complete')
        self.assertEqual(sum('collect' in cmd for cmd in calls), 4)
        drifts = [row['start_drift_s'] for row in self.envelope_journal]
        self.assertEqual(len(drifts), 4)
        for drift in drifts:
            self.assertLessEqual(abs(drift), .02)
        starts = [float(a[a.index('--envelope-start-mono-s')+1]) for a in calls if 'collect' in a]
        self.assertEqual(starts, [600, 612, 624, 636])

    def test_regression_2_the_whole_schedule_is_budgeted_before_the_first_spawn(self):
        # A2: 600 + 11*750 + 600 = 9450 s does not fit a 9000 s window, and the
        # night says so before network time is touched or a child exists.
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            protocol={**PROTOCOL, 'slot_pitch_s': 750})
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        self.assertEqual(calls, [])
        self.assertEqual(self.envelope_directories, [])
        self.assertIn('window_budget_exceeded', outcome['error'])
        self.assertIn('9450', outcome['error'])
        # The ruled pitch fits, with 980 s to spare.
        fits, needed = campaign.window_budget_ok(
            SimpleNamespace(window_max_s=9000), PROTOCOL)
        self.assertTrue(fits)
        self.assertEqual(needed, 8020)

    def test_regression_2_the_registration_binds_the_cadence_fields(self):
        sha = campaign.digest((ROOT / campaign.CHAIN_PATH).read_bytes())
        self.assertEqual(campaign.validate_protocol(PROTOCOL, sha), PROTOCOL)
        self.assertEqual(PROTOCOL['slot_pitch_s'], 620)
        self.assertEqual(PROTOCOL['start_drift_abort_s'], 2)
        cases = {
            'missing slot_pitch_s': {k: v for k, v in PROTOCOL.items() if k != 'slot_pitch_s'},
            'missing start_drift_abort_s': {k: v for k, v in PROTOCOL.items()
                                            if k != 'start_drift_abort_s'},
            'pitch under the capture': {**PROTOCOL, 'slot_pitch_s': 599},
            'abort above the exclusion bar': {**PROTOCOL, 'start_drift_abort_s': 11},
            'non-numeric pitch': {**PROTOCOL, 'slot_pitch_s': '620'},
        }
        for label, protocol in cases.items():
            with self.subTest(case=label):
                # Even with the digest check satisfied, the field rules refuse.
                with patch.object(campaign, 'frozen_protocol', return_value=protocol):
                    with self.assertRaises(ValueError):
                        campaign.validate_protocol(protocol, sha)
        # A CLI override of any other field is still refused by identity.
        with self.assertRaises(ValueError):
            campaign.validate_protocol({**PROTOCOL, 'envelope_s': 1}, sha)

    def test_regression_2_frozen_protocol_takes_v2_and_refuses_v1(self):
        directory = ROOT / 'configs/campaigns/quiet_predicate_evidence_01'
        v2 = (directory / 'pilot_protocol_v2.json').read_bytes()
        v1 = (directory / 'pilot_protocol_v1.json').read_bytes()
        self.assertEqual(campaign.PROTOCOL_PATH,
                         'configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json')
        self.assertEqual(campaign.frozen_protocol(v2)['slot_pitch_s'], 620)
        with self.assertRaisesRegex(ValueError, 'not the ruled pilot registration'):
            campaign.frozen_protocol(v1)
        # v1 differs from v2 in exactly the four ruled fields and nothing else.
        first, second = json.loads(v1), json.loads(v2)
        differing = {k for k in set(first) | set(second) if first.get(k) != second.get(k)}
        self.assertEqual(differing, {'slot_pitch_s', 'start_drift_abort_s',
                                     'exclusions', 'ruling'})
        self.assertEqual(second['exclusions'],
                         first['exclusions'] + ['network_time_slew_attested',
                                                'network_time_unattested'])
        self.assertEqual(second['chain_source_sha256'], first['chain_source_sha256'])

    def test_regression_3_a_late_spawn_aborts_the_night_before_its_capture(self):
        # 2.5 s of drift injected at envelope 3: the slot is never launched,
        # the journal names the abort, and the night ends REFUSED.
        rc, summary, outcome, refusals, calls, *_ = self.exercise(burn_at={2: 22.5})
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        self.assertEqual(sum('collect' in cmd for cmd in calls), 2)
        self.assertEqual(self.envelope_directories, ['envelope-01', 'envelope-02'])
        aborted = self.envelope_journal[-1]
        self.assertEqual(aborted['index'], 3)
        self.assertEqual(aborted['abort'], 'start_drift_abort')
        self.assertAlmostEqual(aborted['start_drift_s'], 2.5)
        self.assertEqual(aborted['scheduled_mono_s'], 600 + 2 * 620)
        self.assertIn('start_drift_abort', outcome['error'])
        self.assertEqual(outcome['outcome'], 'refused')
        self.assertEqual(outcome['envelopes_attempted'], 2)
        # Envelope 01 follows the settle and tests no pitch: the same 2.5 s is
        # not an abort there, and the night runs to its twelfth envelope.
        rc, summary, outcome, refusals, calls, *_ = self.exercise(settle_overshoot=2.5)
        self.assertEqual(rc, 0)
        self.assertEqual(sum('collect' in cmd for cmd in calls), 12)
        self.assertAlmostEqual(self.envelope_journal[0]['start_drift_s'], 2.5)
        self.assertEqual([row.get('abort') for row in self.envelope_journal], [None] * 12)

    def test_regression_5_the_attestation_runs_in_the_gap_never_beside_a_capture(self):
        commands = NetworkTimeControlTests.fake_commands(self)
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands)
        self.assertEqual(rc, 0)
        # Strict alternation: envelope i is attested, with its log on disk,
        # before envelope i+1 is spawned, and no collector is alive at any
        # attestation.
        self.assertEqual([(kind, index) for kind, index, *_ in self.timeline],
                         [step for index in range(1, 13)
                          for step in (('spawn', index), ('attest', index))])
        for step in self.timeline:
            if step[0] == 'attest':
                _, index, live, log_written = step
                self.assertEqual(live, [], f'envelope {index} attested beside a live capture')
                self.assertTrue(log_written, index)
        for session in sessions:
            attestation = session['network_time_provenance']['attestation']
            self.assertEqual(attestation['window_method'], 'epoch_monotonic_union_v1')
            stamps = session['power']['anchor']['clock_stamps']
            self.assertEqual(attestation['window_epoch_s'], campaign.attestation_window(stamps))

    def test_regression_5_a_stepped_wall_clock_keeps_the_window_over_the_capture(self):
        # The stamps' monotonic pair fixes the capture's LENGTH; a wall step
        # moves one endpoint's POSITION.  The union covers the true capture
        # whichever endpoint moved -- a +-1 s window around the two wall
        # stamps does not when the step ran the clock BACK.
        for step in (30, -30):
            with self.subTest(step=step):
                commands = NetworkTimeControlTests.fake_commands(self)
                *_, sessions = self.exercise(commands=commands, stepped_stop_s=step)
                for session in sessions:
                    stamps = session['power']['anchor']['clock_stamps']
                    started = stamps['sampling_started']['epoch_s']
                    stopped = stamps['sampling_stopped']['epoch_s']
                    span = (stamps['sampling_stopped']['monotonic_before_s']
                            - stamps['sampling_started']['monotonic_before_s'])
                    window = session['network_time_provenance']['attestation']['window_epoch_s']
                    self.assertEqual(window, [min(started, stopped - span) - 1,
                                              max(stopped, started + span) + 1])
                    # Both wall readings of the capture's true extent lie
                    # inside the window; that is what the +-1 s form loses.
                    for moment in (started, started + span, stopped - span, stopped):
                        self.assertLessEqual(window[0], moment)
                        self.assertGreaterEqual(window[1], moment)
                if step < 0:
                    narrow = [started - 1, stopped + 1]
                    self.assertLess(narrow[1], started + span,
                                    'the +-1 s form would have missed the capture')

    def test_regression_5_an_unproven_teardown_refuses_the_query_not_the_night(self):
        self.assertIsNone(campaign.capture_still_live(
            {'residue': [], 'errors': [], 'cleanup_proven': True}))
        blocked = campaign.capture_still_live(
            {'residue': [4242], 'errors': [], 'cleanup_proven': False})
        self.assertIn('4242', blocked)
        self.assertIn('teardown', campaign.capture_still_live(
            {'residue': [], 'errors': ['journal unreadable']}))
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            out = Path(tmp)
            with patch.object(campaign.subprocess, 'run',
                              side_effect=AssertionError('must not query logd')):
                attestation = campaign.attest_network_time(out, blocked=blocked)
        self.assertEqual(attestation['state'], 'asserted')
        self.assertIsNone(attestation['window_epoch_s'])
        self.assertIn('live capture', attestation['reason'])
        self.assertEqual(campaign.attestation_exclusions(attestation['state']),
                         ['network_time_unattested'])

    def test_regression_6_a_failed_query_reaches_the_summary_as_unattested(self):
        # A267 Part 4 already pins the absolute argv and `--info --debug`
        # (test_the_production_commands_are_the_ruled_absolute_argv), the
        # exhibit-D ten-match slew path
        # (test_an_applied_slew_inside_a_window_excludes_that_night_envelope)
        # and the scanner's zero-match behaviour
        # (test_exhibit_d_has_ten_applied_corrections_and_a_clean_log_has_none).
        # What was not covered end to end: a query that EXITS NONZERO must
        # reach pilot_summary as network_time_unattested.
        commands = NetworkTimeControlTests.fake_commands(self)
        (self.command_directory / 'log').write_text(
            f'#!/bin/sh\nprintf %s "$@" >> "{self.command_directory}/log-calls.txt"\nexit 3\n')
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands)
        for session in sessions:
            attestation = session['network_time_provenance']['attestation']
            self.assertEqual(attestation['state'], 'asserted')
            self.assertEqual(attestation['exit_code'], 3)
        self.assertEqual([v['excluded'] for v in summary['envelopes']],
                         [['network_time_unattested']] * 12)
        self.assertEqual(summary['retained'], 0)
        self.assertEqual(summary['status'], 'INCONCLUSIVE')

    def test_regression_8_the_teardown_budget_is_the_gap_not_a_literal(self):
        self.exercise()
        reserve = campaign.CLEANUP_BUDGET_RESERVE_S
        ceiling = PROTOCOL['slot_pitch_s'] - PROTOCOL['envelope_s'] - reserve
        self.assertEqual(ceiling, 15)
        self.assertEqual(self.slot_cleanup_budgets, [15] * 12)
        for budget in self.slot_cleanup_budgets:
            self.assertLessEqual(budget, ceiling)
        # The budget follows the registration, never a constant in the code.
        self.assertEqual(campaign.cleanup_budget_s(SCALED), 1)
        self.assertEqual(campaign.cleanup_budget_s({**PROTOCOL, 'slot_pitch_s': 700}), 95)


class BatchedCensusTests(unittest.TestCase):
    """Regression 4: one census per sweep, however many groups are journaled."""

    def test_one_pgrep_settles_one_hundred_and_twenty_groups(self):
        from scripts import run_night
        live = 5000
        pgids = list(range(4000, 4120))
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            path = Path(tmp) / 'groups.jsonl'
            for pgid in pgids + [live]:
                campaign.append_event(path, {'kind': 'collector', 'pgid': pgid})
            calls = []
            real_run = run_night.subprocess.run
            def run(argv, **kwargs):
                calls.append(argv)
                from subprocess import CompletedProcess
                if argv[0].endswith('pgrep'):
                    # Only the live group has members; pgrep lists its pids.
                    return CompletedProcess(argv, 0, f'{live + 1} python collector\n', '')
                self.assertEqual(argv[0], '/bin/ps')
                return CompletedProcess(argv, 0, f'{live} {live + 1} python collector\n', '')
            with patch.object(run_night.subprocess, 'run', side_effect=run), \
                    patch.object(campaign.os, 'killpg') as killpg:
                census = campaign.groups_absent(pgids + [live])
            pgreps = [argv for argv in calls if argv[0].endswith('pgrep')]
            self.assertLessEqual(len(pgreps), 2, pgreps)
            self.assertEqual(len(calls) - len(pgreps), 1)  # one attribution pass
            self.assertEqual(pgreps[0][:4],
                             ['/usr/bin/pgrep', '-lf', '-g',
                              ','.join(str(p) for p in sorted(pgids + [live]))])
            # The live group is still reported PRESENT; every other is absent.
            self.assertFalse(census[live])
            self.assertTrue(all(census[pgid] for pgid in pgids))
            self.assertEqual(len(census), 121)
            del real_run, killpg

    def test_an_unanswerable_census_never_reports_an_empty_group(self):
        from scripts import run_night
        from subprocess import CompletedProcess
        cases = {
            'pgrep timed out': lambda argv, **kw: (_ for _ in ()).throw(
                run_night.subprocess.TimeoutExpired(argv, 1)),
            'pgrep argument malformed': lambda argv, **kw: CompletedProcess(argv, 2, '', 'usage'),
            'an unparsable listing': lambda argv, **kw: CompletedProcess(argv, 0, 'not-a-pid x\n', ''),
            'a pid that vanished': lambda argv, **kw: CompletedProcess(
                argv, 0, '7001 python\n' if argv[0].endswith('pgrep') else '', ''),
        }
        for label, side_effect in cases.items():
            with self.subTest(case=label):
                with patch.object(run_night.subprocess, 'run', side_effect=side_effect):
                    census = run_night._group_census_batch([7000, 7001], .2)
                self.assertEqual([absent for absent, _ in census.values()], [False, False])
                for _, lines in census.values():
                    self.assertTrue(lines)

    def test_the_single_group_census_keeps_its_exact_shape(self):
        from scripts import run_night
        from subprocess import CompletedProcess
        for exit_code, stdout, expected in ((1, '', (True, [])),
                                            (0, '99 python\n', (False, ['99 python']))):
            with patch.object(run_night.subprocess, 'run',
                              return_value=CompletedProcess([], exit_code, stdout, '')) as run:
                self.assertEqual(run_night._group_census_batch([99], .2), {99: expected})
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args[0][0][:3], ['/usr/bin/pgrep', '-lf', '-g'])


class LargerDriftTests(unittest.TestCase):
    """Regression 7: the exclusion reads the larger of the two drift figures."""

    def test_a_session_level_drift_alone_excludes_the_envelope(self):
        protocol = {**PROTOCOL, 'start_drift_max_s': 2}
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            root = Path(tmp) / 'evidence'
            root.mkdir()
            entries = []
            for index in range(1, 13):
                out = root / f'envelope-{index:02d}'
                out.mkdir()
                (out / 'session.json').write_text(json.dumps({
                    'session': 'fixture', 'boot_id': 'boot', 'os_build': '25G83',
                    'start_drift_s': 2.3,  # what the collector measured
                    'network_time_provenance': provenance(),
                    'power': {'anchor': {'status': 'bounded'}},
                    'interior': {'complete_support': True,
                                 'power': {'energy_j': {'rail_sum_w': 10, 'combined_w': 10}}}}))
                (out / 'rounds.jsonl').write_text(json.dumps(good_round()) + '\n')
                # What the CHAIN measured is well inside the bar; the session
                # figure is the larger one, and the bar is assessed on it (A1).
                entries.append({'index': index, 'scheduled_mono_s': index * 600,
                                'start_drift_s': 0.2})
            report = campaign.pilot_summary(root, protocol, entries)
        self.assertEqual(report['retained'], 0)
        self.assertEqual([v['excluded'] for v in report['envelopes']], [['start_drift']] * 12)
        self.assertEqual([v['collector_start_drift_s'] for v in report['envelopes']], [2.3] * 12)


class SessionRewriteAuditTests(unittest.TestCase):
    """Regression 9: the one post-collector rewrite names what it replaced."""

    def test_session_sha256_before_is_the_digest_of_the_replaced_file(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            out = Path(tmp)
            original = json.dumps({'session': 'fixture',
                                   'network_time_provenance': {'state': 'off'}})
            (out / 'session.json').write_text(original)
            before = campaign.digest(original.encode())
            attestation = {'state': 'authenticated', 'matched_lines': 0}
            renames = []
            real_replace = campaign.os.replace
            def replace(source, target):
                renames.append((Path(source).name, Path(target).name))
                return real_replace(source, target)
            with patch.object(campaign.os, 'replace', side_effect=replace):
                self.assertTrue(campaign.record_attestation(out, attestation))
            self.assertEqual(renames, [('session.json.tmp', 'session.json')])
            session = json.loads((out / 'session.json').read_text())
            recorded = session['network_time_provenance']['attestation']
            self.assertEqual(recorded['session_sha256_before'], before)
            self.assertNotEqual(campaign.digest((out / 'session.json').read_bytes()), before)
            # Nothing else rewrites session.json after the collector exits:
            # cure 2 has no finaliser pass, so no such call site exists.
            source = (ROOT / 'joulewise/quiet_predicate_campaign.py').read_text()
            self.assertEqual(source.count('os.replace('), 1)
            self.assertIn('os.replace(temporary, path)', source)
            self.assertNotIn('def finalis', source)
            self.assertNotIn('def finaliz', source)


# --------------------------------------------------------------------------
# A267 fix round 1 (magistrate brief 06 over review lenses 05a/05b).  Each
# test below pins one ruled placement, shape or bound that the implementation
# already had but no regression held in place -- the class of defect four
# surviving mutations found in one pass.
# --------------------------------------------------------------------------


def stamped_envelope(directory, *, started=1000.0, stopped=1600.0):
    """An envelope directory whose session carries a capture window."""
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    (out / "session.json").write_text(json.dumps({"power": {"anchor": {"clock_stamps": {
        "sampling_started": {"epoch_s": started, "monotonic_before_s": 50.0},
        "sampling_stopped": {"epoch_s": stopped, "monotonic_before_s": 650.0}}}}}))
    return out


def fake_log(directory, body):
    """A real executable bound to campaign.LOG; an absolute argv needs one."""
    import stat
    path = Path(directory) / "log"
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class AttestationBudgetTests(FrozenExecutorTests):
    """Item 1 (05b B1 residual): the clock query is bounded by its gap."""

    def test_a_slow_query_is_abandoned_at_its_bound_and_never_authenticates(self):
        import shutil
        directory = Path(tempfile.mkdtemp(dir="/tmp"))
        self.addCleanup(shutil.rmtree, directory)
        log = fake_log(directory, "#!/bin/sh\nsleep 5\n")
        out = stamped_envelope(directory / "envelope-01")
        with patch.object(campaign, "LOG", str(log)):
            began = time.monotonic()
            attestation = campaign.attest_network_time(out, timeout=.5)
            elapsed = time.monotonic() - began
        # Abandoned at the bound, not at the child's own five seconds.
        self.assertLess(elapsed, 3)
        self.assertEqual(attestation["state"], "asserted")
        self.assertTrue(attestation["reason"].startswith("timed log query timed out"),
                        attestation["reason"])
        self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                         ["network_time_unattested"])

    def test_the_bound_is_what_the_teardowns_budget_leaves_of_the_gap(self):
        """R3.3: the teardown and the query are two parts of ONE gap.

        The gap under v2 is 20 s, the teardown's budget is 15 s of it, and
        the query gets the 5 s that leaves.  Before the cure both functions
        subtracted the same 5 s reserve from the gap and each claimed 15 s:
        30 s of work planned into 20 s of gap.
        """
        gaps = {"v2": PROTOCOL, "the scaled protocol": SCALED,
                "a 700 s pitch": {**PROTOCOL, 'slot_pitch_s': 700},
                # The boundary of the domain: gap == FLOOR + 1.
                "the 6 s boundary gap": {**PROTOCOL, 'slot_pitch_s': 606}}
        for label, protocol in gaps.items():
            with self.subTest(case=label):
                gap = protocol['slot_pitch_s'] - protocol['envelope_s']
                self.assertGreaterEqual(gap, campaign.ATTESTATION_TIMEOUT_FLOOR_S + 1)
                self.assertLessEqual(campaign.attestation_timeout_s(protocol)
                                     + campaign.cleanup_budget_s(protocol), gap)
        # Below the boundary the two FLOORS (1 s teardown, 5 s query) add to
        # 6 and overrun the gap.  That is documented, not forbidden: the
        # overrun pushes the next spawn late and `start_drift_abort_s` is the
        # detector, so this pin records the behaviour rather than a guard.
        tight = {**PROTOCOL, 'slot_pitch_s': 603}
        self.assertEqual(campaign.cleanup_budget_s(tight), 1)
        self.assertEqual(campaign.attestation_timeout_s(tight),
                         campaign.ATTESTATION_TIMEOUT_FLOOR_S)
        self.assertEqual(campaign.attestation_timeout_s(tight) + campaign.cleanup_budget_s(tight), 6)
        self.assertGreater(campaign.attestation_timeout_s(tight)
                           + campaign.cleanup_budget_s(tight),
                           tight['slot_pitch_s'] - tight['envelope_s'])
        self.assertIn("start_drift_abort_s", PROTOCOL)

    def test_the_bound_is_the_registrations_gap_and_a_timeout_keeps_the_schedule(self):
        # 620 - 600 = 20 s of gap, 15 s of it is the teardown's budget, and
        # the query gets the 5 s that leaves; the floor holds a tiny gap open.
        self.assertEqual(campaign.attestation_timeout_s(PROTOCOL), 5)
        self.assertEqual(campaign.attestation_timeout_s(SCALED),
                         campaign.ATTESTATION_TIMEOUT_FLOOR_S)
        self.assertEqual(campaign.attestation_timeout_s({**PROTOCOL, 'slot_pitch_s': 700}), 5)
        self.assertNotIn("timeout=300", (ROOT / 'joulewise/quiet_predicate_campaign.py').read_text())
        # Every query spends its whole 5 s bound and times out: the night
        # keeps its cadence, the envelopes lose their claim-bearing state, and
        # the cost of the query is on the record for the next budget.
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(attest_burn=5)
        self.assertEqual(rc, 0)
        self.assertEqual([kwargs["timeout"] for kwargs in self.attestation_kwargs], [5] * 12)
        self.assertEqual([v["excluded"] for v in summary["envelopes"]],
                         [["network_time_unattested"]] * 12)
        self.assertEqual(summary["retained"], 0)
        self.assertEqual([row["network_time_attestation_wall_s"]
                          for row in self.envelope_journal], [5] * 12)
        starts = [float(a[a.index('--envelope-start-mono-s') + 1]) for a in calls if 'collect' in a]
        self.assertEqual(starts, [600 + 620 * i for i in range(12)])
        for row in self.envelope_journal:
            self.assertLessEqual(abs(row["start_drift_s"]), .02)


class ZeroOutputGuardTests(FrozenExecutorTests):
    """Item 2 (05b S1): an empty result is not a clean machine."""

    def test_a_body_without_the_syslog_header_is_asserted_never_authenticated(self):
        # R2.1: the two LIVE captures of the ruled argv are accepted, and the
        # bytes that were accepted are the bytes pinned here.
        self.assertEqual(campaign.digest(SYSLOG_FIXTURE.read_bytes()), SYSLOG_FIXTURE_SHA256)
        self.assertEqual(campaign.digest(ZERO_MATCH_FIXTURE.read_bytes()),
                         ZERO_MATCH_FIXTURE_SHA256)
        for label, path in (("the 191-line capture", SYSLOG_FIXTURE),
                            ("the zero-match capture", ZERO_MATCH_FIXTURE)):
            self.assertTrue(campaign.timed_log_has_header(path.read_text()), label)
        self.assertTrue(campaign.timed_log_has_header(TIMED_LOG_HEADER))
        # R2.6: `log` pads the header line with four trailing spaces; the
        # guard tolerates them and their absence alike.  (Counterfactual:
        # with `==` in place of `.rstrip() ==`, the live captures fail.)
        self.assertEqual(ZERO_MATCH_FIXTURE.read_text(),
                         campaign.TIMED_LOG_SYSLOG_HEADER + "    \n")
        self.assertTrue(campaign.timed_log_has_header(
            campaign.TIMED_LOG_SYSLOG_HEADER + "    \n"))
        self.assertTrue(campaign.timed_log_has_header(campaign.TIMED_LOG_SYSLOG_HEADER))
        # R2.3: the compact style's header is the defect this guard cures.
        self.assertFalse(campaign.timed_log_has_header(COMPACT_FIXTURE.read_text()))
        self.assertFalse(campaign.timed_log_has_header(
            COMPACT_FIXTURE.read_text().splitlines()[0]))
        # R2.4: no body, an error page, a bare newline, and an entry line
        # with no header above it (each format's own second line).
        for body in ("", "<html>error</html>\n", "\n", "2026-09-22 02:28:08.226 Df timed\n",
                     COMPACT_FIXTURE.read_text().splitlines()[1] + "\n",
                     SYSLOG_FIXTURE.read_text().splitlines()[1] + "\n"):
            self.assertFalse(campaign.timed_log_has_header(body), repr(body))
        for label, body, state in (
                ("empty", "", "asserted"),
                ("an error page", "<html>error</html>\n", "asserted"),
                ("the compact header", COMPACT_FIXTURE.read_text().splitlines()[0] + "\n",
                 "asserted"),
                ("header only", TIMED_LOG_HEADER, "authenticated"),
                # R2.2: the live zero-match capture, end to end.
                ("the live zero-match capture", ZERO_MATCH_FIXTURE.read_text(),
                 "authenticated")):
            with self.subTest(case=label):
                commands = NetworkTimeControlTests.fake_commands(self, timed_log=body)
                rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
                    commands=commands)
                self.assertEqual(rc, 0)
                self.assertEqual(len(sessions), 12)
                for session in sessions:
                    attestation = session["network_time_provenance"]["attestation"]
                    self.assertEqual(attestation["state"], state)
                    self.assertEqual(attestation["exit_code"], 0)
                    self.assertEqual(attestation["matched_lines"], 0)
                    if state == "asserted":
                        self.assertEqual(attestation["reason"],
                                         "timed log query returned no header")
                self.assertEqual([v["excluded"] for v in summary["envelopes"]],
                                 [[] if state == "authenticated"
                                  else ["network_time_unattested"]] * 12)
                self.assertEqual(summary["retained"], 12 if state == "authenticated" else 0)


class UnreadableSessionRecordTests(FrozenExecutorTests):
    """Q5 item 1 (R5.1): an annotation that cannot read what it annotates."""

    def test_an_absent_or_malformed_session_record_is_asserted_never_authenticated(self):
        # `record_attestation` returned False and left the state alone, so an
        # envelope whose record could not be read was journalled
        # `authenticated` -- the one claim-bearing state -- on the strength of
        # a query whose subject the chain could not name.
        for label, payload, exception in (("absent", None, "FileNotFoundError"),
                                          ("malformed", "{ not json\n", "JSONDecodeError")):
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
                    out = Path(tmp)
                    if payload is not None:
                        (out / "session.json").write_text(payload)
                    attestation = {"state": "authenticated", "matched_lines": 0}
                    self.assertFalse(campaign.record_attestation(out, attestation))
                    self.assertEqual(attestation["state"], "asserted")
                    self.assertTrue(attestation["reason"].startswith(
                        f"session record unreadable: {exception}: "), attestation["reason"])
                    self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                                     ["network_time_unattested"])

    def test_a_record_that_vanishes_before_the_annotation_is_journalled_asserted(self):
        # End to end: the journal row and the summary's exclusions are built
        # from the attestation AFTER `record_attestation` has had it, so the
        # state set there is the state the night reports.
        def spy(stack, module):
            real = module.record_attestation
            def vanishing(out, attestation):
                (out / "session.json").unlink()
                return real(out, attestation)
            stack.enter_context(patch.object(module, "record_attestation",
                                             side_effect=vanishing))
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(spy=spy)
        self.assertEqual(rc, 0)
        self.assertEqual(sessions, [])
        self.assertEqual([row["network_time_attestation"] for row in self.envelope_journal],
                         ["asserted"] * 12)
        # Nothing is retained.  With no session record the summary also loses
        # the interior support, so the exclusion IT prints is that one; the
        # attestation's own verdict is read off the journal row above.
        self.assertTrue(all(v["excluded"] for v in summary["envelopes"]))
        self.assertEqual(summary["retained"], 0)


class ExitCodePrecedenceTests(FrozenExecutorTests):
    """Item 3 (05b S2, 05a N2): 2 is a refusal; 3 is a machine left wrong."""

    ROWS = (
        # label, exercise kwargs, outcome, restored, refusals, exit code
        ("complete, restored", {}, "complete", True, 0, 0),
        ("complete, restore failed", {"on_exit": 1}, "complete", False, 0, 3),
        ("partial, restored", {"errors": {3}}, "partial", True, 0, 0),
        ("partial, restore failed", {"errors": {3}, "on_exit": 1}, "partial", False, 0, 3),
        ("refused (dead recorder), restored",
         {"recorder_dead": True}, "refused", True, 1, 2),
        ("refused (dead recorder), restore failed",
         {"recorder_dead": True, "on_exit": 1}, "refused", False, 1, 2),
        ("refused (two cleanup_unproven), restored",
         {"cleanup_failures": {3, 4}}, "refused", True, 1, 2),
        ("refused (two cleanup_unproven), restore failed",
         {"cleanup_failures": {3, 4}, "on_exit": 1}, "refused", False, 1, 2),
    )

    def test_the_eight_row_truth_table_over_outcome_cleanup_and_restore(self):
        for label, kwargs, expected_outcome, restored, refusal_count, code in self.ROWS:
            with self.subTest(case=label):
                rc, summary, outcome, refusals, calls, control, sessions = self.exercise(**kwargs)
                self.assertEqual(outcome["outcome"], expected_outcome)
                self.assertTrue(outcome["cleanup_proven"])
                # The restore's verdict is on the outcome document on EVERY
                # path, so collapsing its code into the refusal hides nothing.
                self.assertIn("network_time_restored", outcome)
                self.assertIs(outcome["network_time_restored"], restored)
                self.assertEqual(refusals, refusal_count)
                self.assertEqual(rc, code, label)


class NetworkTimeReceiptTests(FrozenExecutorTests):
    """Item 4 (05b S3): a toggle that never answers is still on the record."""

    def test_an_off_that_times_out_writes_its_receipt_before_refusing(self):
        commands = NetworkTimeControlTests.fake_commands(self, off_sleep=5)
        def spy(stack, module):
            # The real bound is 30 s; the seam shortens it so the regression
            # measures the timeout path, not the wall clock.
            stack.enter_context(patch.object(module, "NETWORK_TIME_SET_TIMEOUT_S", .5))
        began = time.monotonic()
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            commands=commands, spy=spy)
        self.assertLess(time.monotonic() - began, 4)
        self.assertEqual(campaign.NETWORK_TIME_SET_TIMEOUT_S, 30)
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        self.assertEqual(calls, [])  # no recorder, no collector
        self.assertEqual(outcome["outcome"], "refused")
        self.assertIn("network time OFF not established", outcome["error"])
        self.assertIn("TimeoutExpired", outcome["error"])
        # The attempt is on the record with an exit code it never got.
        self.assertEqual(control["off"]["argv"][1:],
                         ["-n", campaign.SYSTEMSETUP, "-setusingnetworktime", "off"])
        self.assertIsNone(control["off"]["exit_code"])
        self.assertIsNone(control["off"]["stdout"])
        self.assertIn("TimeoutExpired", control["off"]["error"])
        self.assertIsNotNone(control["off"]["epoch_s"])
        self.assertIsNotNone(control["off"]["monotonic_s"])
        # ... and the restore ran anyway, on the same refused path.
        self.assertEqual(control["on"]["exit_code"], 0)
        self.assertTrue(outcome["network_time_restored"])


class RestoreReceiptTests(FrozenExecutorTests):
    """Item 5 (05b S4, S5): the restore protects the record and never raises."""

    def receipt(self, exit_code=0):
        return {"argv": list(campaign.network_time_argv("on")), "exit_code": exit_code,
                "stdout": "setUsingNetworkTime: On\n", "epoch_s": 1.0, "monotonic_s": 2.0}

    def test_an_unreadable_or_non_dict_record_keeps_its_bytes(self):
        cases = {"a json list": "[]\n", "json null": "null\n", "a json string": '"off"\n',
                 "a number": "17\n", "garbage bytes": "{ not json\n"}
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            night = Path(tmp)
            path = night / campaign.NETWORK_TIME_CONTROL_BASENAME
            sibling = night / campaign.NETWORK_TIME_RESTORE_BASENAME
            for label, payload in cases.items():
                with self.subTest(case=label):
                    path.write_text(payload)
                    sibling.unlink(missing_ok=True)
                    with patch.object(campaign, "set_network_time",
                                      return_value=self.receipt()):
                        self.assertTrue(campaign.restore_network_time(night))
                    self.assertEqual(path.read_text(), payload)
                    written = json.loads(sibling.read_text())
                    self.assertEqual(written["on"]["exit_code"], 0)
                    self.assertEqual(written["off"]["state"], "unreadable")
                    self.assertEqual(written["off"]["record"],
                                     campaign.NETWORK_TIME_CONTROL_BASENAME)
                    # The verdict is still the set form's own exit code.
                    with patch.object(campaign, "set_network_time",
                                      return_value=self.receipt(exit_code=1)):
                        self.assertFalse(campaign.restore_network_time(night))
                    self.assertEqual(path.read_text(), payload)

    def test_no_exception_class_escapes_the_restore(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            night = Path(tmp)
            path = night / campaign.NETWORK_TIME_CONTROL_BASENAME
            path.write_text(json.dumps({"schema": campaign.NETWORK_TIME_CONTROL_SCHEMA,
                                        "off": {"exit_code": 0}}))
            # A toggle that raises is reported, not propagated.
            with patch.object(campaign, "set_network_time", side_effect=OSError("no sudo")):
                self.assertFalse(campaign.restore_network_time(night))
            self.assertIn("OSError", json.loads(path.read_text())["on"]["error"])
            # A failure that is NOT the toggle (here: a receipt with no exit
            # code at all) still returns a verdict instead of a traceback.
            with patch.object(campaign, "set_network_time", return_value=None):
                self.assertFalse(campaign.restore_network_time(night))
            self.assertIn("TypeError",
                          json.loads((night / campaign.NETWORK_TIME_RESTORE_BASENAME)
                                     .read_text())["on"]["error"])
            # A write failure does not mask a restore that worked.
            with patch.object(campaign, "set_network_time", return_value=self.receipt()), \
                    patch.object(campaign, "write_control_record",
                                 side_effect=PermissionError("read-only night")):
                self.assertTrue(campaign.restore_network_time(night))

    def test_a_night_whose_record_is_corrupted_still_writes_its_outcome(self):
        for label, payload in (("a json list", "[]\n"), ("garbage bytes", "{ not json\n")):
            with self.subTest(case=label):
                def spy(stack, module, payload=payload):
                    real = module.write_control_record
                    def corrupting(path, control):
                        real(path, control)
                        # Replace the record between OFF and the restore, the
                        # way a truncated write or a stray editor would.
                        if (path.name == campaign.NETWORK_TIME_CONTROL_BASENAME
                                and control.get("on") is None):
                            path.write_text(payload)
                    stack.enter_context(patch.object(module, "write_control_record",
                                                     side_effect=corrupting))
                rc, summary, outcome, refusals, calls, control, sessions = self.exercise(spy=spy)
                self.assertEqual(rc, 0)
                self.assertEqual(outcome["outcome"], "complete")
                self.assertTrue(outcome["network_time_restored"])
                self.assertEqual(summary["retained"], 12)
                self.assertEqual(self.control_text, payload)
                self.assertEqual(self.restore_receipt["on"]["exit_code"], 0)
                self.assertEqual(self.restore_receipt["off"]["state"], "unreadable")


class SessionRewriteFailureTests(FrozenExecutorTests):
    """Item 6 (05b S6): an unwritable envelope costs its own claim, not the night."""

    def test_a_read_only_envelope_asserts_itself_and_keeps_its_session(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp) / "envelope-01"
            out.mkdir()
            (out / "session.json").write_text(json.dumps({"session": "fixture"}))
            before = (out / "session.json").read_bytes()
            attestation = {"state": "authenticated", "matched_lines": 0}
            out.chmod(0o500)
            try:
                self.assertFalse(campaign.record_attestation(out, attestation))
            finally:
                out.chmod(0o700)
            self.assertEqual(attestation["state"], "asserted")
            self.assertTrue(attestation["reason"].startswith("session rewrite failed: "),
                            attestation["reason"])
            self.assertIn("PermissionError", attestation["reason"])
            self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                             ["network_time_unattested"])
            self.assertEqual((out / "session.json").read_bytes(), before)
            self.assertFalse(list(out.glob("*.tmp")))

    def test_a_night_whose_annotations_cannot_land_still_finishes(self):
        def spy(stack, module):
            stack.enter_context(patch.object(module.os, "replace",
                                             side_effect=PermissionError("read-only envelope")))
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(spy=spy)
        self.assertEqual(rc, 0)
        self.assertEqual(outcome["outcome"], "complete")
        self.assertEqual(refusals, 0)
        # Every envelope keeps the collector's own session record, unannotated,
        # and the executor's entry carries the asserted state the summary reads.
        for session in sessions:
            self.assertNotIn("attestation", session["network_time_provenance"])
        self.assertEqual([row["network_time_attestation"] for row in self.envelope_journal],
                         ["asserted"] * 12)
        self.assertEqual([v["excluded"] for v in summary["envelopes"]],
                         [["network_time_unattested"]] * 12)
        self.assertEqual(summary["retained"], 0)


class RestoreOrderTests(FrozenExecutorTests):
    """Item 11 (05a S4): the restore is the FIRST action of the finally."""

    def test_the_restore_precedes_the_cleanup_record_on_every_path(self):
        def spy(stack, module):
            # The step that follows the restore in the `finally` cannot run.
            # If the restore had been ordered after it, the machine would be
            # left with network time OFF and no receipt saying so.
            stack.enter_context(patch.object(module, "cleanup_record",
                                             side_effect=OSError("cleanup journal lost")))
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            spy=spy, tolerate_raise=True)
        self.assertIsInstance(self.execute_error, OSError)
        self.assertEqual(control["off"]["stdout"], EXPECTED_OFF)
        self.assertIsNotNone(control["on"], "the restore did not run before cleanup_record")
        self.assertEqual(control["on"]["exit_code"], 0)
        self.assertEqual(control["on"]["argv"][-1], "on")


class AttestationWindowRecordTests(unittest.TestCase):
    """Item 14: what the query was asked, and what an absurd epoch does."""

    def test_the_record_carries_both_the_union_window_and_the_queried_seconds(self):
        # 05a N3: `--start`/`--end` take whole seconds, so the query runs over
        # a truncated window.  Both readings are on the record.
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = stamped_envelope(Path(tmp) / "envelope-01",
                                   started=1790000000.4, stopped=1790000600.9)
            with patch.object(campaign.subprocess, "run",
                              return_value=SimpleNamespace(
                                  returncode=0, stdout=TIMED_LOG_HEADER, stderr="")):
                attestation = campaign.attest_network_time(out)
        self.assertEqual(attestation["state"], "authenticated")
        window = attestation["window_epoch_s"]
        self.assertEqual(window, campaign.attestation_window({
            "sampling_started": {"epoch_s": 1790000000.4, "monotonic_before_s": 50.0},
            "sampling_stopped": {"epoch_s": 1790000600.9, "monotonic_before_s": 650.0}}))
        argv_window = attestation["window_argv_epoch_s"]
        self.assertEqual(argv_window, campaign.timed_log_window_epoch_s(attestation["argv"]))
        # Whole seconds, each the truncation of its float counterpart, so the
        # queried span is never narrower than a second either side of it.
        for named, floated in zip(argv_window, window):
            self.assertEqual(named, math.floor(floated))
        self.assertEqual(argv_window[1] - argv_window[0], 602)

    def test_a_non_finite_or_absurd_capture_window_is_asserted_not_a_traceback(self):
        # 05b N1: `datetime.fromtimestamp` raises on both, from inside the
        # guarded section now.
        cases = {"not a number": float("nan"), "infinite": float("inf"),
                 "absurd but finite": 1e300, "out of range": 1e18}
        for label, stopped in cases.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory(dir="/tmp") as tmp:
                out = Path(tmp) / "envelope-01"
                out.mkdir()
                (out / "session.json").write_text(json.dumps(
                    {"power": {"anchor": {"clock_stamps": {
                        "sampling_started": {"epoch_s": 1000.0, "monotonic_before_s": 50.0},
                        "sampling_stopped": {"epoch_s": stopped,
                                             "monotonic_before_s": 650.0}}}}}))
                with patch.object(campaign.subprocess, "run",
                                  side_effect=AssertionError("must not query logd")):
                    attestation = campaign.attest_network_time(out)
                self.assertEqual(attestation["state"], "asserted")
                self.assertIn("capture window unavailable", attestation["reason"])
                self.assertIsNone(attestation["window_epoch_s"])
                self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                                 ["network_time_unattested"])
