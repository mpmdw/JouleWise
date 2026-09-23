"""Campaign mechanics and negative scientific branches using fixtures only."""
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
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


def consumers(*rows, observer_command="/usr/bin/powermetrics", observer_busy=.114):
    """`top_consumers` as a v3 recorder journals them.

    `rows` are (command, pid, busy_cores) for NON-observer processes; the
    observer's own power sampler is always present and always marked, because
    under registration v3 the recorder runs with the chain root as its
    observer pid and every process the measurement started is its descendant.
    """

    marked = [{"command": observer_command, "pid": 900, "busy_cores": observer_busy,
               "start_identity": "Tue Sep 22 21:10:02 2026", "observer": True}]
    return marked + [{"command": command, "pid": pid, "busy_cores": busy,
                      "start_identity": "Fri Sep 18 17:41:17 2026", "observer": False}
                     for command, pid, busy in rows]


def journal_row(index, *rows, interval_s=30.0, observer_cpu_s=.2, offset=0, span=30,
                observer_busy=.114, busy_cores=None):
    """One recorder journal row joined to envelope `index`'s support.

    `observer_busy` is the measurement's own power sampler, marked; it never
    enters the per-envelope exclusion, which reads named NON-observer
    processes only.
    """

    start = index * 600 + offset
    total = observer_busy + sum(row[2] for row in rows) if busy_cores is None else busy_cores
    return {"monotonic_start": start, "monotonic_end": start + span,
            "observer_cpu_s": observer_cpu_s,
            "observation": {"interval_s": interval_s,
                            "metrics": {"busy_cores": total,
                                        "top_consumers": consumers(*rows, observer_busy=observer_busy)}}}


def stamps(span_s=600.0, observer_cpu_s=12.0):
    """The collector's own clock stamps and whole-envelope observer cost.

    Registration v3's observer floor is `whole_envelope_observer_cpu_s` over
    this span, so a session fixture without them is refused by name.
    """

    return {"start_stamp": {"monotonic_before_s": 1000.0},
            "end_stamp": {"monotonic_before_s": 1000.0 + span_s},
            "whole_envelope_observer_cpu_s": observer_cpu_s}


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
                    **stamps(),
                    'network_time_provenance': provenance(
                        *(('slew_attested', 1) if index in slew else ())),
                    'power':{'recorder_kind':'powermetrics','anchor':{'status':'bounded'}},
                    'interior':{'complete_support':True,
                        'power':{'energy_j':{'rail_sum_w':energy, 'combined_w':energy}}}}
                row = good_round()
                if observer_core is not None:
                    # v3's floor is the WHOLE envelope's observer cost over the
                    # collector's own span, not the round block's (synthesis 35).
                    session.update(stamps(observer_cpu_s=600 * observer_core))
                    row.update(observer_cpu_s=30 * observer_core, round_mono_start_s=index*600, round_mono_end_s=index*600+30)
                if index in excluded:
                    row['census_clean'] = False
                (out / 'session.json').write_text(json.dumps(session))
                (out / 'rounds.jsonl').write_text(json.dumps(row) + '\n')
                entries.append({'index':index, 'scheduled_mono_s':index*600, 'start_drift_s':drift})
                if recorder:
                    # The excursion is the measurement's OWN power sampler:
                    # busy cores stay a covariate under v3, and only a named
                    # NON-observer process can cost an envelope its claim.
                    excursion = 99 if index == 5 else .01
                    campaign.append_event(root.parent / PROTOCOL['recorder_journal'],
                                          journal_row(index, observer_busy=excursion,
                                                      busy_cores=excursion))
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
                session = {'session':'fixture','boot_id':'boot','os_build':'25G83','power':{'recorder_kind':'powermetrics','anchor':{'status':'bounded'}},
                           **stamps(), 'network_time_provenance': provenance(),
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
                 attest_burn=0, tolerate_raise=False, final_cleanup_unproven=False,
                 recorder_kind='powermetrics', busy_rows=None):
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

        ``final_cleanup_unproven`` fails the NIGHT-level teardown -- the one
        `cleanup_record` runs in the `finally`, after the last envelope --
        rather than a slot's.  It is the axis the truth table had no row
        for: residue that only the final sweep can see.
        """
        from contextlib import ExitStack
        from dataclasses import replace
        from types import SimpleNamespace
        from tests.test_night_gate import make_plan
        protocol = PROTOCOL if protocol is None else protocol
        envelope_s = protocol['envelope_s']
        burn_at = burn_at or {}
        calls, processes = [], {}
        # Every environment the executor hands a child, so a regression can
        # prove the bench replay's switch is in none of them (R9).
        self.popen_envs = popen_envs = []
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
                popen_envs.append(dict(kwargs.get('env') or {}))
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
                    power={'anchor':{'status':'bounded','clock_stamps':{
                            'sampling_started':{'epoch_s':1000+self.end-envelope_s,
                                                'monotonic_before_s':self.end-envelope_s},
                            'sampling_stopped':{'epoch_s':1000+self.end+stepped_stop_s,
                                                'monotonic_before_s':self.end}}}}
                    # ``recorder_kind=None`` writes NO key at all: a session
                    # that never said which recorder produced its frames is
                    # not a claim of production provenance either (R5).
                    if recorder_kind is not None:
                        power['recorder_kind'] = recorder_kind
                    session={'session':'fixture','os_build':'25G83','boot_id':'boot','start_drift_s':0,
                        **stamps(),
                        'network_time_provenance':{k:v for k,v in provenance().items() if k!='attestation'},
                        'power':power,
                        'interior':{'complete_support':True,
                        'power':{'energy_j':{'rail_sum_w':index,'combined_w':index}}}}
                    (out/'session.json').write_text(json.dumps(session))
                    (out/'rounds.jsonl').write_text(json.dumps(good_round())+'\n')
                    # The covariate recorder is a stub here, so a regression
                    # that needs journal rows inside this envelope's support
                    # supplies them: `busy_rows(index, scheduled)` returns the
                    # rows the real recorder would have appended by now.
                    if busy_rows is not None:
                        for journalled in busy_rows(index, self.end - envelope_s):
                            campaign.append_event(
                                out.parent.parent / protocol['recorder_journal'], journalled)
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
            elif final_cleanup_unproven:
                # No `exclude` means this is `cleanup_record`'s own sweep.
                result['cleanup_proven'] = False
                result['residue'] = [9999999]
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
            # The executor reads the bench replay's switch from its OWN
            # environment (the harvest refusal `execute` takes on it), so
            # every night driven here runs under a SCRUBBED copy of this
            # shell's environment rather than the shell itself: a desk shell
            # that happens to carry the switch must not decide what these
            # tests prove (execution lens 17b S4).  A spy that wants the
            # variable sets it on top, and R9 puts it back deliberately.
            from scripts.sample_quiet_predicate_evidence import REPLAY_ENV as _replay_env
            enter(patch.dict(campaign.os.environ,
                             {k: v for k, v in os.environ.items() if k != _replay_env},
                             clear=True))
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
            self.assertEqual(cleanup['cleanup_proven'], not final_cleanup_unproven)
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
            # The refusal DOCUMENTS, not just their count: the typed reason is
            # what distinguishes a machine-state abort from a failed probe.
            self.refusal_documents=[json.loads(path.read_text()) for path in sorted(refusals)]
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
            (out / "session.json").write_text(json.dumps({"power": {"recorder_kind": "powermetrics", "anchor": {"clock_stamps": {
                "sampling_started": {"epoch_s": 1000.0, "monotonic_before_s": 50.0},
                "sampling_stopped": {"epoch_s": 1600.0, "monotonic_before_s": 650.0}}}}}))
            with patch.object(campaign.subprocess, "run",
                              return_value=SimpleNamespace(returncode=1, stdout="", stderr="")):
                attestation = campaign.attest_network_time(out, timeout=5)
            self.assertEqual(attestation["state"], "asserted")
            self.assertEqual(attestation["exit_code"], 1)
            self.assertEqual(attestation["window_epoch_s"], [999.0, 1601.0])
            # A missing capture window is also asserted, never authenticated.
            (out / "session.json").write_text("{}")
            with patch.object(campaign.subprocess, "run",
                              side_effect=AssertionError("must not query")):
                self.assertEqual(campaign.attest_network_time(out, timeout=5)["state"], "asserted")

    def test_the_query_bound_must_be_passed_and_cannot_be_defaulted(self):
        """R5.5: no call site binds the floor by accident.

        The bound belongs to the registration the night is running -- the
        inter-slot gap less the teardown's budget -- and a default here let a
        caller that forgot it run a 5 s query while believing it had asked
        for the gap.  It is keyword-only with no default, so forgetting it is
        a `TypeError` at the call, not a quiet 5 s.
        """
        import inspect
        parameter = inspect.signature(campaign.attest_network_time).parameters["timeout"]
        self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIs(parameter.default, inspect.Parameter.empty)
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            with self.assertRaises(TypeError) as raised:
                campaign.attest_network_time(Path(tmp))
            self.assertIn("timeout", str(raised.exception))
            # Positionally, too: the third argument is no longer reachable.
            with self.assertRaises(TypeError):
                campaign.attest_network_time(Path(tmp), None, 5)

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

    def test_regression_2_frozen_protocol_takes_v3_and_refuses_v1_and_v2(self):
        directory = ROOT / 'configs/campaigns/quiet_predicate_evidence_01'
        v3 = (directory / 'pilot_protocol_v3.json').read_bytes()
        v2 = (directory / 'pilot_protocol_v2.json').read_bytes()
        v1 = (directory / 'pilot_protocol_v1.json').read_bytes()
        self.assertEqual(campaign.PROTOCOL_PATH,
                         'configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json')
        self.assertEqual(campaign.frozen_protocol(v3)['slot_pitch_s'], 620)
        # Both superseded registrations are refused BY THE SAME CHECK: the
        # executor runs the bytes the gate pinned, never a predecessor's.
        for superseded in (v1, v2):
            with self.assertRaisesRegex(ValueError, 'not the ruled pilot registration'):
                campaign.frozen_protocol(superseded)
        # v3 differs from v2 in exactly the four ruled fields and nothing else
        # (cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2; ruling 31's
        # reporting limbs as adjudicated by synthesis 35).
        second, third = json.loads(v2), json.loads(v3)
        self.assertEqual({k for k in set(second) | set(third) if second.get(k) != third.get(k)},
                         {'exclusions', 'ruling', 'non_observer_process_busy',
                          't0_non_observer_share_max', 'observer_floor'})
        self.assertEqual(third['exclusions'], second['exclusions'] + ['non_observer_process_busy'])
        self.assertEqual(third['chain_source_sha256'], second['chain_source_sha256'])
        self.assertEqual(third['non_observer_process_busy']['bar_core_seconds'], 30)
        self.assertEqual(third['non_observer_process_busy']['abort_after_consecutive'], 2)
        self.assertEqual(third['t0_non_observer_share_max'], .5)
        self.assertNotIn('observer_floor_tolerance', third['block_two'])
        self.assertNotIn('observer_variation', third)
        self.assertEqual(third['stop_branches'], second['stop_branches'])
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
                attestation = campaign.attest_network_time(out, blocked=blocked, timeout=5)
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
                    **stamps(),
                    'start_drift_s': 2.3,  # what the collector measured
                    'network_time_provenance': provenance(),
                    'power': {'recorder_kind': 'powermetrics', 'anchor': {'status': 'bounded'}},
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
    (out / "session.json").write_text(json.dumps({"power": {"recorder_kind": "powermetrics", "anchor": {"clock_stamps": {
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
        self.assertEqual(campaign.attestation_timeout_s(tight)
                         + campaign.cleanup_budget_s(tight), 6)
        self.assertGreater(campaign.attestation_timeout_s(tight)
                           + campaign.cleanup_budget_s(tight),
                           tight['slot_pitch_s'] - tight['envelope_s'])
        # Ruling 18 Q2: a TWO-POINT pin, because a one-point one (20 s gap
        # only) is killed by `return ATTESTATION_TIMEOUT_FLOOR_S` and by
        # nothing else.  `cleanup_budget_s` reads the module global at call
        # time, so moving the reserve to 10 moves what the query is left:
        # 10 s at the 20 s gap, and still the 5 s FLOOR at the 3 s gap.  The
        # pair additionally kills `return CLEANUP_BUDGET_RESERVE_S`,
        # `return max(FLOOR, RESERVE)` and the unfloored `gap -
        # cleanup_budget_s` (which gives 2 at the 3 s gap).
        with patch.object(campaign, "CLEANUP_BUDGET_RESERVE_S", 10):
            self.assertEqual(campaign.attestation_timeout_s(PROTOCOL), 10)
            self.assertEqual(campaign.attestation_timeout_s(
                {**PROTOCOL, 'slot_pitch_s': 603}), 5)

    @staticmethod
    def _spend_the_whole_teardown_budget(stack, module):
        """Make the teardown spend its budget on the harness's fake clock."""
        real = module.cleanup_groups
        def spend(*args, **kwargs):
            result = real(*args, **kwargs)
            if kwargs.get("exclude"):
                module.time.now += kwargs["budget_s"]
            return result
        stack.enter_context(patch.object(module, "cleanup_groups", side_effect=spend))

    def test_a_gap_under_six_seconds_pushes_every_spawn_late_by_six_minus_gap(self):
        """Ruling 18 Q3 C3: what the sub-6 s band actually costs, executed.

        Below a 6 s gap the two FLOORS (the teardown's 1 s and the query's
        5 s) add to 6 and overrun the gap.  Both floors are spent here on the
        harness's fake clock -- the teardown by `_spend_the_whole_teardown_
        budget`, the query by `attest_burn=5`, which is what a query that
        times out at its bound costs -- so the overrun is real work, not an
        injected number.

        The overrun is ``6 - gap`` per slot and it does NOT compound: the
        collector's deadline is ABSOLUTE (`sample_quiet_predicate_evidence`
        `deadline = scheduled + duration_s`), so a spawn that is late by d
        captures for ``envelope_s - d`` and still ends at its scheduled end,
        and the next slot inherits the same ``6 - gap`` and no more.  Both
        halves are pinned below, because "the drift accumulates" and "the
        drift is a constant per-slot lateness" call for different detectors.

        At a 3 s gap the 3 s overrun is over the scaled 2 s abort bar, so the
        night ends REFUSED at envelope 2 -- the FIRST eligible spawn
        (envelope 01 follows the settle and tests no pitch).  At a 5 s gap
        the 1 s overrun is under the bar, every one of the twelve slots is
        late by exactly 1 s, and the abort never fires: the residual is then
        a standing per-slot lateness that `start_drift_max_s` (10 s under v2)
        is the only thing that would ever exclude.
        """
        tight = {**PROTOCOL, 'slot_pitch_s': 603, 'start_drift_abort_s': 2}
        self.assertEqual(campaign.cleanup_budget_s(tight)
                         + campaign.attestation_timeout_s(tight), 6)
        rc, summary, outcome, refusals, calls, *_ = self.exercise(
            protocol=tight, attest_burn=5, spy=self._spend_the_whole_teardown_budget)
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        # Envelope 02 is the first spawn the pitch governs, and it never runs.
        self.assertEqual(sum('collect' in cmd for cmd in calls), 1)
        self.assertEqual([row['index'] for row in self.envelope_journal], [1, 2])
        aborted = self.envelope_journal[-1]
        self.assertEqual(aborted['abort'], 'start_drift_abort')
        self.assertAlmostEqual(aborted['start_drift_s'], 6 - 3)
        self.assertEqual(outcome['outcome'], 'refused')
        self.assertIn('start_drift_abort: envelope 2', outcome['error'])
        # A 5 s gap: the same 6 s of floors, a 1 s overrun, no abort, and the
        # SAME 1 s on every later slot -- the lateness does not compound.
        loose = {**PROTOCOL, 'slot_pitch_s': 605, 'start_drift_abort_s': 2}
        self.assertEqual(campaign.cleanup_budget_s(loose)
                         + campaign.attestation_timeout_s(loose), 6)
        rc, summary, outcome, refusals, *_ = self.exercise(
            protocol=loose, attest_burn=5, spy=self._spend_the_whole_teardown_budget)
        self.assertEqual(rc, 0)
        self.assertEqual(outcome['outcome'], 'complete')
        self.assertEqual([round(row['start_drift_s'], 6) for row in self.envelope_journal],
                         [0] + [6 - 5] * 11)
        self.assertEqual([row.get('abort') for row in self.envelope_journal], [None] * 12)
        self.assertLess(6 - 5, PROTOCOL['start_drift_max_s'])

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
        # Nothing is retained.  DEVIATION from ruling 18 Q3 C4, executed:
        # the ruling dictates `assertIn("network_time_unattested",
        # v["excluded"])`, and that assertion is RED here --
        # `AssertionError: 'network_time_unattested' not found in
        # ['incomplete_interior_support']`.  With the session record gone,
        # `pilot_summary` fails its own read at the `try` and `continue`s
        # with the interior exclusion BEFORE it ever reaches the attestation
        # state, so the exclusion it prints is exactly that one and no other.
        # The vacuous `assertTrue(all(...))` the ruling was right to reject
        # is replaced by the specific list, and the attestation's own verdict
        # is pinned on the journal row above (`asserted` x 12).
        for v in summary["envelopes"]:
            self.assertEqual(v["excluded"], ["incomplete_interior_support"])
            self.assertIsNone(v["joules"])
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
        # `cleanup_proven` as a real axis: twelve complete envelopes, every
        # slot's teardown proven, and residue that only the night's FINAL
        # sweep sees.  Before this row every row in the table asserted
        # `cleanup_proven` True, so the axis was a constant.
        ("complete envelopes, final cleanup unproven",
         {"final_cleanup_unproven": True}, "refused", True, 1, 2, False),
        ("complete envelopes, final cleanup unproven, restore failed",
         {"final_cleanup_unproven": True, "on_exit": 1}, "refused", False, 1, 2, False),
    )

    def test_the_truth_table_over_outcome_cleanup_and_restore(self):
        """R5.3: `cleanup_proven` is an axis of this table, not a constant.

        The last two rows are the ones the table lacked.  Note what the
        document says on them: the envelopes all completed, but a night whose
        final teardown cannot be proven is REFUSED by `execute` before the
        outcome is written, so `outcome` reads `refused` and never
        `complete`.  The cold gate's phrasing ("a row with outcome ==
        complete and final cleanup_proven False") describes the envelopes'
        outcome, which `execute` computes and then overrides; the return code
        it asks for -- 2 -- is what these rows pin.
        """
        for label, kwargs, expected_outcome, restored, refusal_count, code, *proven in self.ROWS:
            with self.subTest(case=label):
                rc, summary, outcome, refusals, calls, control, sessions = self.exercise(**kwargs)
                self.assertEqual(outcome["outcome"], expected_outcome)
                self.assertIs(outcome["cleanup_proven"], proven[0] if proven else True)
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
            # A write failure does not mask a restore that worked -- and
            # R5.4: it is no longer silent.  The receipt is the only artifact
            # that says the machine was put back; a write that cannot land
            # leaves a hole in the record, and the hole now names itself on
            # the executor's stdout, which the night log keeps.
            import io
            from contextlib import redirect_stdout
            said = io.StringIO()
            with patch.object(campaign, "set_network_time", return_value=self.receipt()), \
                    patch.object(campaign, "write_control_record",
                                 side_effect=PermissionError("read-only night")), \
                    redirect_stdout(said):
                self.assertTrue(campaign.restore_network_time(night))
            self.assertIn("restore receipt write failed: PermissionError: read-only night",
                          said.getvalue())

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

    def test_a_rename_that_fails_leaves_no_temporary_behind(self):
        """R5.2: the `.tmp` assertion belongs on the path that can make one.

        On the read-only-directory path above the temporary can never be
        created, so asserting its absence there proved nothing.  Here the
        write SUCCEEDS and only `os.replace` fails, which is the shape that
        left a complete `session.json.tmp` -- carrying the `authenticated`
        state this branch withdraws -- beside the record it failed to
        replace.
        """
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp) / "envelope-01"
            out.mkdir()
            (out / "session.json").write_text(json.dumps({"session": "fixture"}))
            before = (out / "session.json").read_bytes()
            attestation = {"state": "authenticated", "matched_lines": 0}
            written = {}
            def replace(source, target):
                written["existed"] = Path(source).exists()
                written["payload"] = json.loads(Path(source).read_text())
                raise OSError("cross-device link")
            with patch.object(campaign.os, "replace", side_effect=replace):
                self.assertFalse(campaign.record_attestation(out, attestation))
            # The temporary really was complete when the rename failed ...
            self.assertTrue(written["existed"])
            self.assertEqual(
                written["payload"]["network_time_provenance"]["attestation"]["state"],
                "authenticated")
            # ... and nothing of it survives.
            self.assertEqual(list(out.glob("*.tmp")), [])
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["session.json"])
            self.assertEqual((out / "session.json").read_bytes(), before)
            self.assertEqual(attestation["state"], "asserted")
            self.assertTrue(attestation["reason"].startswith("session rewrite failed: "),
                            attestation["reason"])
            self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                             ["network_time_unattested"])

    def test_C8_a_NaN_in_the_session_record_asserts_the_envelope_not_the_night(self):
        """Ruling 18 C8 (pre-existing): `json.loads` takes NaN, `dumps` will not.

        A collector that wrote `NaN` anywhere in `session.json` produced a
        record that parses and then cannot be written back under
        `allow_nan=False`.  The `ValueError` that raises is not an `OSError`,
        so it escaped `record_attestation` and `execute`'s outer handler
        refused the NIGHT -- twelve envelopes lost to one envelope's
        annotation.  Now it is the same withdrawal every other failed
        rewrite gets.
        """
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp) / "envelope-01"
            out.mkdir()
            (out / "session.json").write_text(
                '{"session": "fixture", "interior": {"power": {"energy_j": NaN}}}')
            before = (out / "session.json").read_bytes()
            self.assertTrue(math.isnan(
                json.loads(before)["interior"]["power"]["energy_j"]))
            attestation = {"state": "authenticated", "matched_lines": 0}
            self.assertFalse(campaign.record_attestation(out, attestation))
            self.assertEqual(attestation["state"], "asserted")
            self.assertTrue(attestation["reason"].startswith(
                "session rewrite failed: ValueError: "), attestation["reason"])
            self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                             ["network_time_unattested"])
            # The collector's own bytes are kept, and no temporary survives.
            self.assertEqual((out / "session.json").read_bytes(), before)
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["session.json"])

    def test_R_C1_a_cleanup_that_raises_never_costs_the_night(self):
        """Ruling 18 Q1: the withdrawal comes first, the cleanup cannot raise.

        The rename fails and the removal of the complete `.tmp` it left
        behind fails too (an immutable or root-owned temporary raises
        `PermissionError`, which is an `OSError` this handler does not
        re-enter).  Before the cure that second failure escaped
        `record_attestation` with the state still `authenticated`, and
        `execute`'s outer handler refused the whole night; now the envelope
        is `asserted`, both failures are in the reason, and the collector's
        own bytes are untouched.
        """
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            out = Path(tmp) / "envelope-01"
            out.mkdir()
            (out / "session.json").write_text(json.dumps({"session": "fixture"}))
            before = (out / "session.json").read_bytes()
            attestation = {"state": "authenticated", "matched_lines": 0}
            with patch.object(campaign.os, "replace", side_effect=OSError("disk full")), \
                    patch.object(Path, "unlink", side_effect=PermissionError("immutable")):
                self.assertFalse(campaign.record_attestation(out, attestation))
            self.assertEqual(attestation["state"], "asserted")
            self.assertIn("session rewrite failed", attestation["reason"])
            self.assertIn("OSError: disk full", attestation["reason"])
            self.assertIn("not removed", attestation["reason"])
            self.assertIn("PermissionError: immutable", attestation["reason"])
            self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                             ["network_time_unattested"])
            self.assertEqual((out / "session.json").read_bytes(), before)

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
        # Ruling 18 C7: the reason is DURABLE.  `session.json` keeps the
        # collector's unannotated bytes on this path, so the journal row is
        # the only place a harvester can read why the envelope was withdrawn.
        for row in self.envelope_journal:
            self.assertIn("session rewrite failed: PermissionError: read-only envelope",
                          row["network_time_attestation_reason"])
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
                attestation = campaign.attest_network_time(out, timeout=5)
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
                    {"power": {"recorder_kind": "powermetrics", "anchor": {"clock_stamps": {
                        "sampling_started": {"epoch_s": 1000.0, "monotonic_before_s": 50.0},
                        "sampling_stopped": {"epoch_s": stopped,
                                             "monotonic_before_s": 650.0}}}}}))
                with patch.object(campaign.subprocess, "run",
                                  side_effect=AssertionError("must not query logd")):
                    attestation = campaign.attest_network_time(out, timeout=5)
                self.assertEqual(attestation["state"], "asserted")
                self.assertIn("capture window unavailable", attestation["reason"])
                self.assertIsNone(attestation["window_epoch_s"])
                self.assertEqual(campaign.attestation_exclusions(attestation["state"]),
                                 ["network_time_unattested"])


class BenchReplayFailClosedTests(unittest.TestCase):
    """R5-R7, R9: the bench replay can never be labelled evidence.

    Cold gate #3 ruling 10 Q7; brief D6.  Three independent refusal points
    exist (arm, run, harvest); the arm one lives in `run_night` and is pinned
    in that module's tests.  These are the run and harvest ones, plus the
    driver's own verdict and the proof that an ordinary night's children never
    see the switch.
    """

    ROOT = Path(__file__).resolve().parents[1]
    STUB = ROOT / "scripts/bench_replay_systemsetup_stub.py"
    # A slot whose finalisation tail really ran: the fields `verdict` admits
    # a slot on (execution lens 17b B2/S3).  Drift figures are per-test.
    SLOT = {"collector_exit": 0, "cleanup_proven": True, "anchor_status": "bounded",
            "interior_complete_support": True, "attestation_state": "authenticated",
            # The rest is what `markdown()` prints; none of it is admissible
            # input, and every value here is inert.
            "scheduled_mono_s": 0.0, "actual_mono_s": 0.0, "cleanup_wall_s": 0.02,
            "network_time_attestation_wall_s": 0.8, "tail_s": 1.0,
            "recorder_kind": "replay", "label_shift": "auto", "label_shift_s": 36497,
            "frames_written": 253, "source_plist_sha256": "0" * 64,
            "written_stream_sha256": "0" * 64}
    # Cold ruling 21 rule (6) budgets the worst measured tail plus the
    # archive's worst SKIPPED tail against the protocol's own inter-slot gap
    # (`slot_pitch_s - envelope_s`), so a protocol stating neither figure
    # fails that rule rather than skipping it.  The full protocol's gap is
    # 20 s; `SLOT`'s `tail_s` is 1.0 s, so the budget is 3.3 s.
    PROTOCOL = {"envelopes": 12, "slot_pitch_s": 620, "envelope_s": 600}

    def bench_slot(self, index, **overrides):
        """A bench row whose anchor CLASS is the ARCHIVED night's for that slot.

        Cold ruling 21 rule (4) compares each replayed slot's anchor class
        against `ARCHIVED_V31_BOUNDED`, and a slot resolving where the
        archive did not VOIDS the run.  A fixture that made every slot
        `bounded` would therefore be five admitting-direction mismatches, not
        a clean run; these rows are the faithful replay the rule expects.
        """

        from scripts import bench_replay_start_drift as bench
        bounded = index in bench.ARCHIVED_V31_BOUNDED
        row = dict(self.SLOT, index=index,
                   anchor_status="bounded" if bounded else "unknown",
                   anchor_detail=None if bounded else "affine_clock_fit_empty",
                   interior_complete_support=bounded)
        row.update(overrides)
        return row

    def test_R5_a_replay_recorder_refuses_the_whole_night_at_the_summary(self):
        from unittest.mock import patch
        from scripts import sample_quiet_predicate_evidence as sampler
        harness = FrozenExecutorTests()

        def spy(stack, module):
            # The executor reads the variable to stamp the outcome document;
            # the bench driver is what sets it in the real run.
            stack.enter_context(patch.dict(
                module.os.environ, {sampler.REPLAY_ENV: "/Users/edr/night-archive/pilot"}))

        rc, summary, outcome, refusals, _calls, _control, sessions = \
            harness.exercise(recorder_kind="replay", spy=spy)
        # HARVEST: the summary is replaced outright, not annotated.
        self.assertEqual(summary["status"], campaign.REPLAY_NEVER_EVIDENCE)
        self.assertEqual(summary["evidence_status"], campaign.REPLAY_NEVER_EVIDENCE)
        self.assertEqual(summary["retained"], [])
        self.assertIsNone(summary["s_upper"])
        self.assertEqual([row["index"] for row in summary["replay_recorder_envelopes"]],
                         list(range(1, 13)))
        # RUN: the outcome document names the recorder, the night is refused,
        # and the process exits 2.
        self.assertEqual(outcome["outcome"], "refused")
        self.assertEqual(outcome["error"], campaign.REPLAY_REFUSAL_REASON)
        self.assertEqual(outcome["error"], "replay_recorder")
        self.assertEqual(outcome["recorder_kind"], "replay")
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        # And the drift measurement -- the only thing the bench is for --
        # survives the refusal intact, because the rows are appended inside
        # the slot loop, before anything the refusal touches.
        self.assertEqual([row["index"] for row in harness.envelope_journal], list(range(1, 13)))
        for row in harness.envelope_journal:
            self.assertIn("start_drift_s", row)
            self.assertIn("cleanup_wall_s", row)
            self.assertIn("network_time_attestation_wall_s", row)
        self.assertEqual([s["power"]["recorder_kind"] for s in sessions], ["replay"] * 12)
        # L3 (17a N2): and no ENERGY survives the override, so the document's
        # own claim that no number can be lifted from it is true.  The
        # schedule-side diagnostics the bench exists for are what remain.
        self.assertEqual(summary["sizing_pairs"], [])
        self.assertEqual(summary["adjacent_pairs"], [])
        self.assertIsNone(summary["pair_sd_j"])
        self.assertIsNone(summary["single_envelope_sd_j"])
        self.assertIsNone(summary["unfiltered_single_envelope_sd_j"])
        self.assertIsNone(summary["max_abs_delta_j"])
        self.assertIsNone(summary["block_two_stop"])
        for v in summary["envelopes"]:
            self.assertIsNone(v["joules"])
            self.assertIsNone(v["combined_joules"])
            self.assertIsNone(v["interior"])
            self.assertIn("start_drift_s", v)
            self.assertIn("busy_cores", v)

    def test_R5_counterfactual_the_same_night_under_powermetrics_completes(self):
        # The kill.  One field changes and the night is a night again: rc 0,
        # outcome complete, twelve retained, a real spread status.
        rc, summary, outcome, refusals, *_ = FrozenExecutorTests().exercise(
            recorder_kind="powermetrics")
        self.assertEqual(rc, 0)
        self.assertEqual(outcome["outcome"], "complete")
        self.assertEqual(outcome["recorder_kind"], "powermetrics")
        self.assertEqual(summary["status"], "SPREAD_RECORDED")
        self.assertEqual(summary["retained"], 12)
        self.assertEqual(refusals, 0)
        self.assertNotIn("replay_recorder_envelopes", summary)

    def test_R5_a_session_with_no_recorder_kind_at_all_also_refuses(self):
        # Fail-closed: an absent marker is not a claim of production
        # provenance.  A session that never said what recorded it cannot be
        # admitted on the strength of not having said "replay".
        rc, summary, outcome, _refusals, _calls, _control, sessions = \
            FrozenExecutorTests().exercise(recorder_kind=None)
        # The variant is a power RECORD that omits the key -- a recorder was
        # built and did not say what it was -- never `power: null`, which is
        # the early-refusal path L1 exempts.
        for session in sessions:
            self.assertIsInstance(session["power"], dict)
            self.assertNotIn("recorder_kind", session["power"])
        self.assertEqual(summary["status"], campaign.REPLAY_NEVER_EVIDENCE)
        self.assertEqual([row["recorder_kind"] for row in summary["replay_recorder_envelopes"]],
                         [None] * 12)
        self.assertEqual(outcome["outcome"], "refused")
        self.assertEqual(rc, 2)

    def test_X3_a_replay_night_whose_journals_are_lost_still_refuses(self):
        """Execution lens 17b S1: the harvest check failed OPEN on a bad read.

        `recorder_kind` was read AFTER a `try` that `continue`s on any
        `OSError`/`ValueError` from `session.json` OR `rounds.jsonl`, so
        twelve sessions each saying `recorder_kind: "replay"` with their
        `rounds.jsonl` absent produced an ordinary INCONCLUSIVE summary,
        `evidence_status: "PROVISIONAL"`, no `replay_recorder_envelopes`, and
        `execute` did not refuse: rc 0.  The replay variable is NOT set here,
        so the refusal can only come from the summary's own reading.
        """
        from unittest.mock import patch
        harness = FrozenExecutorTests()

        def spy(stack, module):
            real = module.pilot_summary
            def lose_the_journals(directory, protocol, envelopes, observer_cpu_s=None):
                for path in sorted(directory.glob("envelope-*/rounds.jsonl")):
                    path.unlink()
                return real(directory, protocol, envelopes, observer_cpu_s)
            stack.enter_context(patch.object(module, "pilot_summary",
                                             side_effect=lose_the_journals))

        rc, summary, outcome, refusals, _calls, _control, sessions = \
            harness.exercise(recorder_kind="replay", spy=spy)
        self.assertEqual([s["power"]["recorder_kind"] for s in sessions], ["replay"] * 12)
        self.assertEqual(summary["status"], campaign.REPLAY_NEVER_EVIDENCE)
        self.assertEqual(summary["evidence_status"], campaign.REPLAY_NEVER_EVIDENCE)
        self.assertEqual([row["index"] for row in summary["replay_recorder_envelopes"]],
                         list(range(1, 13)))
        self.assertEqual(outcome["outcome"], "refused")
        self.assertEqual(outcome["error"], campaign.REPLAY_REFUSAL_REASON)
        # X7: the outcome document reads the SESSIONS too, so it says `replay`
        # even though this executor's environment never carried the switch.
        self.assertEqual(outcome["recorder_kind"], "replay")
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        # Each envelope still reports the read that failed, on its own terms.
        for v in summary["envelopes"]:
            self.assertIn("incomplete_interior_support", v["excluded"])

    def test_L2_a_replay_night_that_wrote_no_session_still_refuses(self):
        """Lane contract lens 17a S2: the RUN marker is a refusal point too.

        `pilot_summary`'s refusal reads the session records, so it is silent
        when none of them can be read: a feeder that crashes on a malformed
        archive has every collector killed at `envelope_s + 30` before it
        writes, and the night used to end `partial` with rc 0 -- ordinary
        INCONCLUSIVE prose in `summary.md` -- with
        `evidence_outcome.recorder_kind: "replay"` as the only tell.  The
        executor's own environment now refuses it, independent of what any
        child managed to write.
        """
        from unittest.mock import patch
        from scripts import sample_quiet_predicate_evidence as sampler
        harness = FrozenExecutorTests()

        def spy(stack, module):
            stack.enter_context(patch.dict(
                module.os.environ, {sampler.REPLAY_ENV: "/Users/edr/night-archive/pilot"}))
            real = module.pilot_summary
            def nothing_readable(directory, protocol, envelopes, observer_cpu_s=None):
                for path in sorted(directory.glob("envelope-*/*.json*")):
                    path.unlink()
                for path in sorted(directory.glob("envelope-*/rounds.jsonl")):
                    path.unlink()
                return real(directory, protocol, envelopes, observer_cpu_s)
            stack.enter_context(patch.object(module, "pilot_summary",
                                             side_effect=nothing_readable))

        rc, summary, outcome, refusals, _calls, _control, sessions = harness.exercise(spy=spy)
        # Nothing readable, so the SUMMARY cannot see a replay recorder ...
        self.assertEqual(sessions, [])
        self.assertEqual(summary["status"], "INCONCLUSIVE")
        self.assertNotIn("replay_recorder_envelopes", summary)
        # ... and the night is refused anyway, by the executor's environment.
        self.assertEqual(outcome["outcome"], "refused")
        self.assertEqual(outcome["error"], campaign.REPLAY_REFUSAL_REASON)
        self.assertEqual(outcome["recorder_kind"], "replay")
        self.assertEqual(rc, 2)
        self.assertEqual(refusals, 1)
        # The drift rows the bench exists for survive the refusal.
        self.assertEqual([row["index"] for row in harness.envelope_journal],
                         list(range(1, 13)))

    def test_D1_a_bench_abort_keeps_its_own_error_beside_the_replay_marker(self):
        """Delta lenses (execution SHOULD-FIX 1, contract N1): no clobber.

        The bench sets the replay switch on EVERY run, so `execute`'s
        environment-side refusal overwrote whatever `error` already held.  A
        night aborted at envelope 02 by `start_drift_abort` -- the exact
        failure the bench replay exists to detect -- reached
        `evidence_outcome.json` and `write_refusal` reading `replay_recorder`
        alone, and the abort text survived only as the journal row's `abort`
        key.  Both texts now travel together, the specific one first.

        The night is the ruled C3 pitch-603 harness: a 3 s gap against 6 s of
        floors (teardown 1 s spent by `_spend_the_whole_teardown_budget`,
        query 5 s spent by `attest_burn`), so envelope 02 -- the first spawn
        the pitch governs -- is 3 s late against a 2 s abort bar.
        """
        from unittest.mock import patch
        from scripts import sample_quiet_predicate_evidence as sampler
        harness = FrozenExecutorTests()
        tight = {**PROTOCOL, 'slot_pitch_s': 603, 'start_drift_abort_s': 2}

        def spy(stack, module):
            stack.enter_context(patch.dict(
                module.os.environ, {sampler.REPLAY_ENV: "/Users/edr/night-archive/pilot"}))
            AttestationBudgetTests._spend_the_whole_teardown_budget(stack, module)

        rc, _summary, outcome, refusals, *_ = harness.exercise(
            protocol=tight, attest_burn=5, spy=spy)
        self.assertEqual((rc, refusals), (2, 1))
        self.assertEqual(outcome["outcome"], "refused")
        self.assertEqual(harness.envelope_journal[-1]["abort"], "start_drift_abort")
        # BOTH, in this order: the diagnostic the bench came for, then the
        # marker that says no frame here is evidence.
        self.assertIn("start_drift_abort: envelope 2", outcome["error"])
        self.assertTrue(outcome["error"].endswith("; " + campaign.REPLAY_REFUSAL_REASON),
                        outcome["error"])
        # The counterfactual at 9e7061be, executed on the same helper: an
        # unconditional assignment keeps only the marker.
        self.assertEqual(campaign.REPLAY_REFUSAL_REASON, "replay_recorder")
        self.assertNotEqual(outcome["error"], campaign.REPLAY_REFUSAL_REASON)
        # A night with nothing more specific to say still says exactly the
        # marker (the ruled L2 shape), and a night both refusal points fire
        # on never says it twice (R5's ordinary bench case).
        self.assertEqual(campaign.replay_refusal_error(None),
                         campaign.REPLAY_REFUSAL_REASON)
        self.assertEqual(campaign.replay_refusal_error(""),
                         campaign.REPLAY_REFUSAL_REASON)
        self.assertEqual(campaign.replay_refusal_error(campaign.REPLAY_REFUSAL_REASON),
                         campaign.REPLAY_REFUSAL_REASON)
        self.assertEqual(outcome["error"].count(campaign.REPLAY_REFUSAL_REASON), 1)

    def test_L1_a_real_night_with_a_power_null_envelope_is_not_a_replay(self):
        """Lane contract lens 17a S1: an early refusal is not a replay.

        `collect` initialises `session["power"] = None` and only replaces it
        with the recorder's metadata once a recorder was BUILT, so an
        envelope that refused on the network-time provenance path -- before
        any recorder existed -- writes `power: null`.  Reading
        `(session.get("power") or {}).get("recorder_kind")` turned that null
        into "does not say powermetrics" and discarded the WHOLE night as a
        bench replay: twelve envelopes, `retained: []`, rc 2, under a reason
        that is false.  The night here is a real one (the replay variable is
        absent) whose envelope 07 refused early; it keeps its own exclusion
        and the other eleven keep their verdict.
        """
        from unittest.mock import patch
        harness = FrozenExecutorTests()

        def spy(stack, module):
            real = module.pilot_summary
            def refuse_envelope_seven(directory, protocol, envelopes, observer_cpu_s=None):
                path = directory / "envelope-07" / "session.json"
                session = json.loads(path.read_text())
                session["power"] = None
                path.write_text(json.dumps(session))
                return real(directory, protocol, envelopes, observer_cpu_s)
            stack.enter_context(patch.object(module, "pilot_summary",
                                             side_effect=refuse_envelope_seven))

        rc, summary, outcome, refusals, _calls, _control, _sessions = harness.exercise(spy=spy)
        self.assertNotEqual(summary["status"], campaign.REPLAY_NEVER_EVIDENCE)
        self.assertNotIn("replay_recorder_envelopes", summary)
        self.assertEqual(summary["evidence_status"], "PROVISIONAL")
        self.assertEqual(rc, 0)
        self.assertEqual(outcome["outcome"], "complete")
        self.assertEqual(outcome["recorder_kind"], "powermetrics")
        self.assertEqual(refusals, 0)
        # Envelope 07 is excluded on its OWN terms and nothing else is.
        by_index = {v["index"]: v for v in summary["envelopes"]}
        self.assertIn("clock_anchor_unresolved", by_index[7]["excluded"])
        self.assertEqual([v["index"] for v in summary["envelopes"] if v["excluded"]], [7])
        self.assertEqual(summary["retained"], 11)

    def test_R9_no_child_of_an_ordinary_night_ever_sees_the_replay_switch(self):
        """R9, rebuilt to construct its own condition (execution lens 17b S4).

        The test used to run an ordinary night and assert the switch was in
        none of its thirteen child environments -- true only because the
        shell it ran in happened to be clean.  Run from a shell carrying the
        variable the whole module went red (`env
        EVIDENCE_POWER_RECORDER_REPLAY=… python3 -m unittest …` ->
        "unexpectedly found"), so it could only ever fail for the wrong
        reason.  Both halves are now built from environment COPIES:

        (a) the ARM side, with the variable PRESENT: the driver's own
            child-environment derivation raises rather than popping, so no
            night can be armed from a shell carrying it -- which is why (b)
            is a property of nights and not of this machine;
        (b) the RUN side, under a SCRUBBED copy: every one of the thirteen
            children of an ordinary night lacks the key.
        """
        from unittest.mock import patch
        from scripts import sample_quiet_predicate_evidence as sampler
        from tests.test_night_gate import make_plan
        from tests.test_run_night import _load_driver
        driver = _load_driver()
        self.assertEqual(driver.REPLAY_RECORDER_ENV, sampler.REPLAY_ENV)

        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            # (a) present -> the arm refuses, whatever this shell carries.
            with patch.dict(os.environ,
                            {sampler.REPLAY_ENV: "/Users/edr/night-archive/pilot"}):
                with self.assertRaises(ValueError) as caught:
                    driver._chain_environment(make_plan(), Path(tmp) / "night")
            self.assertIn("never runs a replay recorder", str(caught.exception))

        # (b) scrubbed -> the night runs and no child sees the key.  The copy
        # is built by removing the key from whatever this shell has, so the
        # assertion holds from a carrying shell too.
        scrubbed = {k: v for k, v in os.environ.items() if k != sampler.REPLAY_ENV}
        with patch.dict(os.environ, scrubbed, clear=True):
            self.assertNotIn(sampler.REPLAY_ENV, os.environ)
            harness = FrozenExecutorTests()
            rc, *_ = harness.exercise()
        self.assertEqual(rc, 0)
        self.assertEqual(len(harness.popen_envs), 13)
        for environment in harness.popen_envs:
            self.assertNotIn(sampler.REPLAY_ENV, environment)
            self.assertIn(campaign.NETWORK_TIME_RECORD_ENV, environment)

    def test_R6_the_systemsetup_stub_refuses_without_the_variable(self):
        from joulewise.arm_readiness import EXPECTED_NETWORK_TIME_OFF_STDOUT
        from scripts import sample_quiet_predicate_evidence as sampler
        argv = [str(self.STUB), "-n", str(self.STUB), "-setusingnetworktime", "off"]
        bare = {k: v for k, v in os.environ.items() if k != sampler.REPLAY_ENV}
        without = subprocess.run(argv, capture_output=True, text=True, env=bare, timeout=30)
        # The exact shape of a toggle that did not happen.
        self.assertEqual(without.returncode, 2)
        self.assertEqual(without.stdout, "")
        # The kill: the guard is what produces that shape.  With the variable
        # set, the very same argv prints the line the chain's imported
        # comparator demands and exits 0.
        with_variable = subprocess.run(
            argv, capture_output=True, text=True, timeout=30,
            env={**bare, sampler.REPLAY_ENV: "/Users/edr/night-archive/pilot"})
        self.assertEqual(with_variable.returncode, 0)
        self.assertEqual(with_variable.stdout, EXPECTED_NETWORK_TIME_OFF_STDOUT)
        # And a refused toggle refuses the NIGHT: `establish_network_time_off`
        # is the production function, run here with both executable constants
        # rebound to the stub, exactly as the bench driver rebinds them.
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(campaign, "SUDO", str(self.STUB)), \
                patch.object(campaign, "SYSTEMSETUP", str(self.STUB)), \
                patch.dict(os.environ, bare, clear=True):
            with self.assertRaises(ValueError) as caught:
                campaign.establish_network_time_off(Path(tmp))
            record = json.loads((Path(tmp) / campaign.NETWORK_TIME_CONTROL_BASENAME).read_text())
        self.assertIn("network time OFF not established", str(caught.exception))
        self.assertEqual(record["off"]["exit_code"], 2)
        self.assertEqual(record["off"]["stdout"], "")

    def test_L4_the_drivers_own_guards_each_refuse_what_they_name(self):
        """Lane contract lens 17a N3: the four refusals ahead of the night.

        `verdict` was the only part of the driver with a regression.  These
        are the guards that run BEFORE any collector is spawned, each driven
        through its own seam: no real `launchctl`, no real `git`, no night.
        """
        from types import SimpleNamespace
        from unittest.mock import patch
        from scripts import bench_replay_start_drift as bench

        # 1. A loaded night agent.  The bench never runs beside one, and a
        # census that could not be taken is not a claim that none is loaded.
        loaded = "-\t0\tcom.joulewise.night.qpe01-pilot-n1-20260922-0217\n12\t0\tcom.apple.Finder\n"
        with patch.object(bench, "run_text", return_value=(0, loaded)):
            with self.assertRaises(bench.BenchRefusal) as caught:
                bench.require_no_night_agent()
        self.assertIn("com.joulewise.night.qpe01-pilot-n1-20260922-0217", str(caught.exception))
        with patch.object(bench, "run_text", return_value=(1, "")):
            with self.assertRaises(bench.BenchRefusal) as caught:
                bench.require_no_night_agent()
        self.assertIn("cannot prove no night agent is loaded", str(caught.exception))
        # The counterfactual: an ordinary machine passes the same guard.
        with patch.object(bench, "run_text", return_value=(0, "12\t0\tcom.apple.Finder\n")):
            self.assertEqual(bench.require_no_night_agent(), [])

        # 2. A dirty tree, and a HEAD that is not the sha the replay is pinned
        # to: either way the run's sha would not name the bytes it ran.
        def fake_git(dirty, head):
            def git(*arguments):
                if arguments[0] == "status":
                    return " M joulewise/quiet_predicate_campaign.py\n" if dirty else ""
                return head + "\n"
            return git
        with patch.object(bench, "git", fake_git(True, "a" * 40)):
            with self.assertRaises(bench.BenchRefusal) as caught:
                bench.require_clean_head()
        self.assertIn("working tree is not clean", str(caught.exception))
        with patch.object(bench, "git", fake_git(False, "a" * 40)):
            with self.assertRaises(bench.BenchRefusal) as caught:
                bench.require_clean_head("b" * 8)
            self.assertEqual(bench.require_clean_head("a" * 8), "a" * 40)
        self.assertIn("not the expected", str(caught.exception))

        # 3. A smoke may never be filed under the ruled artifact's name: the
        # bar comes from the 20 s gap and the smoke scales the gap away.
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            report = {"kind": "smoke", "night_dir": str(Path(tmp) / "night")}
            ruled = Path(tmp) / f"2026-09-22{bench.RULED_ARTIFACT_SUFFIX}"
            args = SimpleNamespace(raw=None, artifact=str(ruled))
            with self.assertRaises(bench.BenchRefusal) as caught:
                bench.write_outputs(report, args)
            self.assertIn("a smoke never writes the ruled artifact name",
                          str(caught.exception))
            self.assertFalse(ruled.exists())
            # The counterfactual: the same smoke under any other name writes.
            args.artifact = str(Path(tmp) / "bench-replay-smoke.md")
            report["slots"], report["verdict"] = [], {"status": "FAIL", "statement": "none",
                "max_session_start_drift_s": None, "session_bar_s": 0.5,
                "session_slots_over_bar": [], "escalate_chain_pass_session_fail": False}
            report.update({"head": "a" * 40, "clean_tree": True, "schema": bench.SCHEMA,
                           "protocol": {k: 0 for k in ("envelope_s", "slot_pitch_s",
                                                       "settle_s", "envelopes")},
                           "cleanup_budget_s": 15, "attestation_timeout_s": 5,
                           "registration_sha256": "0" * 64, "bench_script_sha256": "0" * 64,
                           "archive": "/dev/null", "outcome": "refused", "returncode": 2,
                           "summary_status": campaign.REPLAY_NEVER_EVIDENCE,
                           "outcome_recorder_kind": "replay", "plan_id": "bench-replay-x",
                           "custody_root": tmp, "machine_start": {"uptime": "", "pgrep_claude": 0},
                           "machine_end": {"uptime": "", "pgrep_claude": 0}})
            raw, artifact = bench.write_outputs(report, args)
            self.assertTrue(artifact.exists())

        # 4. The plan id carries the ruled prefix and the root is the bench
        # root -- never the night custody root, which has its own refusal.
        self.assertEqual(bench.PLAN_ID_PREFIX, "bench-replay-")
        self.assertEqual(bench.BENCH_ROOT, Path.home() / "night-bench")
        self.assertEqual(bench.CUSTODY_ROOT_FORBIDDEN, Path.home() / "night-custody")
        seen = {}
        def stop_at_build_plan(plan_id, head, custody_root):
            seen.update(plan_id=plan_id, custody_root=custody_root)
            raise bench.BenchRefusal("stopped before staging")
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp, \
                patch.object(bench, "require_clean_head", return_value="a" * 40), \
                patch.object(bench, "require_no_night_agent", return_value=[]), \
                patch.object(bench, "BENCH_ROOT", Path(tmp) / "night-bench"), \
                patch.object(bench, "build_plan", side_effect=stop_at_build_plan):
            args = SimpleNamespace(archive=tmp, smoke=True, label_shift="none",
                                   expect_sha=None, transaction_merge=None)
            with self.assertRaises(bench.BenchRefusal):
                bench.execute_bench(args)
        self.assertTrue(seen["plan_id"].startswith("bench-replay-"))
        self.assertEqual(seen["custody_root"].parent.name, "night-bench")
        # And with the bench root moved ONTO the custody root, the run refuses
        # before it builds a plan at all.
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp, \
                patch.object(bench, "require_clean_head", return_value="a" * 40), \
                patch.object(bench, "require_no_night_agent", return_value=[]), \
                patch.object(bench, "BENCH_ROOT", bench.CUSTODY_ROOT_FORBIDDEN), \
                patch.object(bench, "build_plan", side_effect=stop_at_build_plan):
            args = SimpleNamespace(archive=tmp, smoke=True, label_shift="none",
                                   expect_sha=None, transaction_merge=None)
            with self.assertRaises(bench.BenchRefusal) as caught:
                bench.execute_bench(args)
        self.assertIn("never writes under the night custody root", str(caught.exception))

    def test_R7_the_bench_verdict_fails_on_a_single_slot_over_the_bar(self):
        from scripts import bench_replay_start_drift as bench
        protocol = self.PROTOCOL
        rows = [self.bench_slot(i, chain_start_drift_s=0.12 + i * 0.001,
                                session_start_drift_s=0.26 + i * 0.001) for i in range(1, 13)]
        passing = bench.verdict(rows, protocol)
        self.assertEqual(passing["status"], "PASS")
        self.assertLessEqual(passing["max_chain_start_drift_s"], bench.START_DRIFT_BAR_S)
        self.assertFalse(passing["escalate_chain_pass_session_fail"])
        # One slot at 0.6 s -- inside the night's 2 s in-chain abort, over the
        # ruled 0.5 s bench bar.  The two bars are sequential, not
        # alternatives, so this FAILS.
        over = [dict(row) for row in rows]
        over[6]["chain_start_drift_s"] = 0.6
        failing = bench.verdict(over, protocol)
        self.assertEqual(failing["status"], "FAIL")
        self.assertEqual(failing["slots_over_bar"], [7])
        self.assertIn("NOT shown", failing["statement"])
        # The counterfactual, executed: compare the SAME journal against the
        # 2 s abort threshold instead of the ruled bar and it passes -- which
        # is the mistake this regression exists to kill.
        self.assertEqual(bench.verdict(over, protocol, bar_s=2)["status"], "PASS")
        self.assertEqual(bench.START_DRIFT_BAR_S, 0.5)

    def test_X1_a_chain_pass_with_a_session_figure_over_the_night_rule_escalates(self):
        """Execution lens 17b B1: a split is a THIRD status, and exits 3.

        A269 ruling 10 A1: the session-level figure runs ~0.12-0.16 s above
        the chain-level one, and a split verdict is escalated, never passed.
        It used to be a boolean beside `status: "PASS"`: the headline printed
        `**PASS**` and `main()` returned 0.  The lens's own live smoke hit
        it -- chain max 0.479 s under the bar, session max 0.734 s over it,
        exit 0 -- on a run that is launched detached and unattended, where
        the exit code and the headline are what a magistrate reads.

        The status survives cold ruling 21 unchanged; the BAR it splits
        against does not.  Ruling 21 Q1 held the 0.5 s bench bar to be
        chain-level only, so the figure a session excess is measured against
        is now the night's ruled 2 s rule (`SESSION_BAR_S = 2.0`), and the
        0.6-0.7 s figures the old convention escalated on now pass.
        """
        from types import SimpleNamespace
        from unittest.mock import patch
        from scripts import bench_replay_start_drift as bench
        rows = [self.bench_slot(i, chain_start_drift_s=0.4,
                                session_start_drift_s=2.4 if i in (1, 3) else 0.3)
                for i in range(1, 13)]
        result = bench.verdict(rows, self.PROTOCOL)
        self.assertEqual(result["status"], "ESCALATE")
        self.assertTrue(result["escalate_chain_pass_session_fail"])
        self.assertEqual(result["session_slots_over_bar"], [1, 3])
        self.assertEqual(result["max_chain_start_drift_s"], 0.4)
        self.assertEqual(result["max_session_start_drift_s"], 2.4)
        self.assertIn("ESCALATED to the magistrate", result["statement"])
        # The convention ruling 21 struck out, executed: the SAME rows with
        # slot 1 at 0.608 s -- the executed 2026-09-22 replay's own figure --
        # exited ESCALATE rc 3 under the old 0.5 s session bar and PASS now.
        ruled = bench.verdict(
            [self.bench_slot(i, chain_start_drift_s=0.4,
                             session_start_drift_s=0.608 if i == 1 else 0.3)
             for i in range(1, 13)], self.PROTOCOL)
        self.assertEqual(ruled["status"], "PASS")
        self.assertEqual(ruled["session_slots_over_bar"], [])
        self.assertEqual(bench.SESSION_BAR_S, 2.0)
        # The headline a reader sees.
        report = {"schema": bench.SCHEMA, "kind": "full", "head": "a" * 40,
                  "clean_tree": True, "slots": rows, "verdict": result,
                  "protocol": {k: 0 for k in ("envelope_s", "slot_pitch_s", "settle_s",
                                              "envelopes")},
                  "cleanup_budget_s": 15, "attestation_timeout_s": 5,
                  "registration_sha256": "0" * 64, "bench_script_sha256": "0" * 64,
                  "archive": "/dev/null", "outcome": "refused", "returncode": 2,
                  "summary_status": campaign.REPLAY_NEVER_EVIDENCE,
                  "outcome_recorder_kind": "replay", "plan_id": "bench-replay-x",
                  "custody_root": "/tmp", "machine_start": {"uptime": "", "pgrep_claude": 0},
                  "machine_end": {"uptime": "", "pgrep_claude": 0}}
        text = bench.markdown(report)
        self.assertIn("**ESCALATE**", text)
        self.assertNotIn("**PASS**", text)
        # And the exit code the unattended run leaves behind.
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp, \
                patch.object(bench, "execute_bench", return_value=report), \
                patch.object(bench, "write_outputs",
                             return_value=(Path(tmp) / "raw.json", Path(tmp) / "a.md")):
            self.assertEqual(bench.main(["--archive", tmp]), 3)
            # The counterfactual, executed: the same run with both figures
            # under the bar exits 0, and one chain figure over it exits 1.
            report["verdict"] = bench.verdict(
                [dict(row, session_start_drift_s=0.3) for row in rows], self.PROTOCOL)
            self.assertEqual(report["verdict"]["status"], "PASS")
            self.assertEqual(bench.main(["--archive", tmp]), 0)
            report["verdict"] = bench.verdict(
                [dict(row, chain_start_drift_s=0.9, session_start_drift_s=0.3)
                 for row in rows], self.PROTOCOL)
            self.assertEqual(report["verdict"]["status"], "FAIL")
            self.assertEqual(bench.main(["--archive", tmp]), 1)

    def test_D2_a_fail_that_is_also_over_the_session_bar_reports_the_split(self):
        """Delta execution lens SHOULD-FIX 2: the split is not a status.

        `escalate_chain_pass_session_fail` is by construction
        `status == "ESCALATE"`, so a run that is over the session bar AND
        carries an inadmissible slot came back FAIL with that boolean FALSE
        and a statement that never mentioned the session figure at all: a
        reader of `slot_defects` plus that boolean concluded the
        session-level figure had been fine, on a run launched detached and
        unattended.  `session_bar_exceeded` is now independent of the status,
        and the statement names the over-bar session slots whenever there
        are any.
        """
        from scripts import bench_replay_start_drift as bench
        protocol = self.PROTOCOL
        rows = [self.bench_slot(i, chain_start_drift_s=0.1,
                                session_start_drift_s=2.9 if i == 4 else 0.2)
                for i in range(1, 13)]
        rows[6]["collector_exit"] = 1
        result = bench.verdict(rows, protocol)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["session_slots_over_bar"], [4])
        self.assertTrue(result["session_bar_exceeded"])
        # The counterfactual, executed: the flag this run USED to be read
        # through stays False, because the status is FAIL and not ESCALATE.
        self.assertFalse(result["escalate_chain_pass_session_fail"])
        self.assertIn("slot 7 collector_exit=1", result["statement"])
        self.assertIn("the night's session-level rule is exceeded too (max 2.900 s > 2.0 s "
                      "on slots [4])", result["statement"])
        # The same split on an otherwise clean run is the ESCALATE the
        # statement already named, and the flag holds there too.
        clean = bench.verdict([dict(row, collector_exit=0) for row in rows], protocol)
        self.assertEqual(clean["status"], "ESCALATE")
        self.assertTrue(clean["session_bar_exceeded"])
        self.assertTrue(clean["escalate_chain_pass_session_fail"])
        # A run under both bars sets neither.
        under = bench.verdict([dict(row, collector_exit=0, session_start_drift_s=0.2)
                               for row in rows], protocol)
        self.assertEqual(under["status"], "PASS")
        self.assertFalse(under["session_bar_exceeded"])
        # And the artifact a magistrate reads carries the split on its own line.
        report = {"schema": bench.SCHEMA, "kind": "full", "head": "a" * 40,
                  "clean_tree": True, "slots": rows, "verdict": result,
                  "protocol": {k: 0 for k in ("envelope_s", "slot_pitch_s", "settle_s",
                                              "envelopes")},
                  "cleanup_budget_s": 15, "attestation_timeout_s": 5,
                  "registration_sha256": "0" * 64, "bench_script_sha256": "0" * 64,
                  "archive": "/dev/null", "outcome": "refused", "returncode": 2,
                  "summary_status": campaign.REPLAY_NEVER_EVIDENCE,
                  "outcome_recorder_kind": "replay", "plan_id": "bench-replay-x",
                  "custody_root": "/tmp", "machine_start": {"uptime": "", "pgrep_claude": 0},
                  "machine_end": {"uptime": "", "pgrep_claude": 0}}
        text = bench.markdown(report)
        self.assertIn("Session bar exceeded (true whatever the status): True", text)
        self.assertIn("**FAIL**", text)

    def test_X2_a_run_whose_finalisation_tail_never_ran_is_not_admissible(self):
        """Execution lens 17b B2 as AMENDED by cold ruling 21 Q2.

        `verdict` read only the two drift figures.  In all three slots of the
        lens's live smoke the anchor was `unknown`
        (`clock_fit_span_insufficient`) and `interior_complete_support` was
        False -- `align_frames` returned nothing, so the per-round
        integration and the interior reduction, the expensive part of the
        tail the bench exists to time, did not run -- and the bench returned
        PASS.  The lens's cure demanded `bounded` with complete interior
        support on EVERY slot (the lead's convention "X2"); ruling 21 Q2
        struck that, because the archived night itself left five of its
        twelve envelopes unresolved, so a FAITHFUL replay fails X2 by
        construction.  A slot is now admissible on `collector_exit == 0` and
        `cleanup_proven`, and the lens's own defect is caught instead by the
        ruled FLOOR (rule 5) -- at least one slot `bounded` with complete
        interior support -- which the all-unknown run below still fails, at
        the run level, exactly as the lens intended.
        """
        from scripts import bench_replay_start_drift as bench
        protocol = self.PROTOCOL
        rows = [self.bench_slot(i, chain_start_drift_s=0.1,
                                session_start_drift_s=0.2) for i in range(1, 13)]
        self.assertEqual(bench.verdict(rows, protocol)["status"], "PASS")
        broken = [dict(row) for row in rows]
        broken[4]["collector_exit"] = 1
        broken[5]["cleanup_proven"] = False
        broken[6]["collector_exit"] = 3
        broken[7]["cleanup_proven"] = False
        result = bench.verdict(broken, protocol)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual([(d["index"], d["field"], d["value"]) for d in result["slot_defects"]],
                         [(5, "collector_exit", 1), (6, "cleanup_proven", False),
                          (7, "collector_exit", 3), (8, "cleanup_proven", False)])
        for fragment in ("slot 5 collector_exit=1", "slot 6 cleanup_proven=False",
                         "slot 7 collector_exit=3"):
            self.assertIn(fragment, result["statement"])
        # Four defective slots is one over the cap the statement spells out,
        # so the fourth is summarised rather than named (fix round 2 item 3,
        # delta execution lens NIT 1); `slot_defects` above still carries it.
        self.assertIn("… and 1 more", result["statement"])
        self.assertNotIn("slot 8 cleanup_proven=False", result["statement"])
        # The two anchor fields are no longer PER-SLOT admissibility input,
        # so one unresolved slot in an otherwise faithful run is not a defect
        # at all: it is a refusing-direction mismatch, reported and
        # admissible (ruling 21 rule 4).
        one_refusing = [dict(row) for row in rows]
        one_refusing[1].update(anchor_status="unknown",
                               anchor_detail="affine_clock_residual_exceeded",
                               interior_complete_support=False)
        refusing = bench.verdict(one_refusing, protocol)
        self.assertEqual(refusing["status"], "PASS")
        self.assertEqual(refusing["slot_defects"], [])
        self.assertEqual(refusing["refusing_direction_slots"], [2])
        # And a run with NO tail anywhere still fails, on the floor, under
        # the full protocol -- while the smoke, whose 60 s envelope cannot
        # resolve an anchor at all, is exempt from rules (4) and (5).
        unresolved = [dict(row, anchor_status="unknown", interior_complete_support=False)
                      for row in rows]
        self.assertEqual(bench.verdict(unresolved, protocol, smoke=True)["status"], "PASS")
        failed = bench.verdict(unresolved, protocol)
        self.assertEqual(failed["status"], "FAIL")
        self.assertFalse(failed["bounded_interior_floor_met"])
        self.assertTrue(failed["statement"].startswith(
            "no slot is 'bounded' with complete interior support"), failed["statement"])
        # And the smoke's artifact says why it was allowed to.
        report = {"schema": bench.SCHEMA, "kind": "smoke", "head": "a" * 40,
                  "clean_tree": True, "slots": unresolved,
                  "verdict": bench.verdict(unresolved, protocol, smoke=True),
                  "protocol": {k: 0 for k in ("envelope_s", "slot_pitch_s", "settle_s",
                                              "envelopes")},
                  "cleanup_budget_s": 15, "attestation_timeout_s": 5,
                  "registration_sha256": "0" * 64, "bench_script_sha256": "0" * 64,
                  "archive": "/dev/null", "outcome": "refused", "returncode": 2,
                  "summary_status": campaign.REPLAY_NEVER_EVIDENCE,
                  "outcome_recorder_kind": "replay", "plan_id": "bench-replay-x",
                  "custody_root": "/tmp", "machine_start": {"uptime": "", "pgrep_claude": 0},
                  "machine_end": {"uptime": "", "pgrep_claude": 0}}
        text = bench.markdown(report)
        self.assertIn("`anchor_status` CANNOT resolve at this envelope length", text)
        self.assertIn("NOT APPLIED under `--smoke`", text)
        report["kind"] = "full"
        report["verdict"] = bench.verdict(unresolved, protocol)
        full = bench.markdown(report)
        self.assertNotIn("CANNOT resolve at this envelope length", full)
        self.assertIn("## Anchor fidelity vs the archived v3.1 class", full)

    def test_D3_an_admissibility_only_fail_opens_with_the_defect_and_stays_short(self):
        """Delta execution lens NIT 1: the leading clause is the real defect.

        An admissibility-only FAIL -- every chain figure under the bar, the
        journal complete, the tails that did not run -- opened with "max <=
        0.5 s NOT shown: over=[] missing=[] recorded=12/12", which reports
        the bar as unmet when it was met and hides the defect behind three
        empty fields; twelve unresolved slots then appended 24 clauses to
        that one line, which is what the artifact headline and the terminal
        both print.
        """
        from scripts import bench_replay_start_drift as bench
        protocol = self.PROTOCOL
        # Two defects on every slot: the collector did not exit and the group
        # teardown was not proven.  (Before cold ruling 21 the twenty-four
        # clauses came from the two anchor fields, which are no longer
        # per-slot admissibility input; the statement shape under test is the
        # same one.)
        rows = [self.bench_slot(i, chain_start_drift_s=0.1, session_start_drift_s=0.2,
                                collector_exit=1, cleanup_proven=False)
                for i in range(1, 13)]
        result = bench.verdict(rows, protocol)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(len(result["slot_defects"]), 24)
        statement = result["statement"]
        self.assertTrue(statement.startswith("12/12 slots NOT admissible"), statement)
        self.assertNotIn("NOT shown", statement)
        self.assertIn("… and 21 more", statement)
        self.assertLess(len(statement), 600)
        # The ruled rules that can also lead a FAIL do not, because none of
        # them fired: this run is faithful, has its floor and fits the gap.
        self.assertEqual(result["admitting_direction_slots"], [])
        self.assertTrue(result["bounded_interior_floor_met"])
        self.assertTrue(result["tail_budget"]["fits"])
        # The counterfactual, executed: the same rows with ONE chain figure
        # over the bar keep the drift-first opening, because then the bar
        # really was not met.
        over = [dict(row) for row in rows]
        over[2]["chain_start_drift_s"] = 0.9
        self.assertTrue(bench.verdict(over, protocol)["statement"].startswith(
            "max <= 0.5 s NOT shown: over=[3]"))
        # Three defective slots is at the cap: all of them are named, nothing
        # is summarised.
        few = [dict(row, collector_exit=0, cleanup_proven=True) for row in rows]
        for i in (0, 1, 2):
            few[i]["cleanup_proven"] = False
        statement = bench.verdict(few, protocol)["statement"]
        self.assertTrue(statement.startswith("3/12 slots NOT admissible"), statement)
        self.assertNotIn("more", statement.split("under the bar")[0])
        for index in (1, 2, 3):
            self.assertIn(f"slot {index} cleanup_proven=False", statement)

    def test_X5_a_slewed_slot_is_expected_on_the_bench_an_asserted_one_is_not(self):
        """Execution lens 17b S3: the bench never turns network time off.

        The `systemsetup` stub toggles nothing, so `timed` keeps applying
        corrections for the whole run; the lens's slot 2 came back
        `slew_attested` on a real, live slew.  On a night that is an
        exclusion; on the bench it is the expected state, and the attestation
        walls the bench reports are live-log-with-slews costs.  `asserted` is
        a defect: the query did not run, so its cost was not measured.
        """
        from scripts import bench_replay_start_drift as bench
        protocol = self.PROTOCOL
        rows = [self.bench_slot(i, chain_start_drift_s=0.1, session_start_drift_s=0.2,
                                attestation_state="slew_attested" if i == 2
                                else "authenticated")
                for i in range(1, 13)]
        passing = bench.verdict(rows, protocol)
        self.assertEqual(passing["status"], "PASS")
        self.assertEqual(passing["slot_defects"], [])
        for state in ("asserted", None, "unknown"):
            with self.subTest(state=state):
                broken = [dict(row) for row in rows]
                broken[3]["attestation_state"] = state
                result = bench.verdict(broken, protocol)
                self.assertEqual(result["status"], "FAIL")
                self.assertEqual(result["slot_defects"],
                                 [{"index": 4, "field": "attestation_state", "value": state,
                                   "required": "authenticated or slew_attested"}])
                self.assertIn(f"slot 4 attestation_state={state!r}", result["statement"])
        # The smoke does not exempt it either: a query that did not run is a
        # query whose cost was not measured, at any envelope length.
        broken = [dict(row) for row in rows]
        broken[3]["attestation_state"] = "asserted"
        self.assertEqual(bench.verdict(broken, protocol, smoke=True)["status"], "FAIL")
        # And the artifact says why a slew is not a failure here.
        report = {"schema": bench.SCHEMA, "kind": "full", "head": "a" * 40,
                  "clean_tree": True, "slots": rows, "verdict": passing,
                  "protocol": {k: 0 for k in ("envelope_s", "slot_pitch_s", "settle_s",
                                              "envelopes")},
                  "cleanup_budget_s": 15, "attestation_timeout_s": 5,
                  "registration_sha256": "0" * 64, "bench_script_sha256": "0" * 64,
                  "archive": "/dev/null", "outcome": "refused", "returncode": 2,
                  "summary_status": campaign.REPLAY_NEVER_EVIDENCE,
                  "outcome_recorder_kind": "replay", "plan_id": "bench-replay-x",
                  "custody_root": "/tmp", "machine_start": {"uptime": "", "pgrep_claude": 0},
                  "machine_end": {"uptime": "", "pgrep_claude": 0}}
        text = bench.markdown(report)
        self.assertIn("The bench NEVER turns network time off", text)
        self.assertIn("`slew_attested` and `authenticated` alike", text)
        self.assertIn("Only `asserted`", text)

    def test_R7_a_journal_short_of_the_registered_slot_count_never_passes(self):
        from scripts import bench_replay_start_drift as bench
        rows = [self.bench_slot(i, chain_start_drift_s=0.1, session_start_drift_s=0.2)
                for i in range(1, 12)]
        result = bench.verdict(rows, self.PROTOCOL)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["slots_recorded"], 11)


ARCHIVE = Path.home() / "night-archive"
CONTAMINATED = ARCHIVE / "qpe01-pilot-n1-20260922-2100-harvest-20260922" / "night"
CLEAN = ARCHIVE / "qpe01-pilot-n1-20260922-0217-harvest-20260922" / "night"
FSEVENTSD = ("/System/Library/Frameworks/CoreServices.framework/Versions/A/"
             "Frameworks/FSEvents.framework/Versions/A/Support/fseventsd")


def archive_summary(night, protocol):
    """Re-derive one archived night's summary under the given registration.

    The envelope entries are the executor's own rows from
    `evidence_envelopes.jsonl`, and the journal is the night's own; nothing is
    synthesised, so the numbers here are the night's numbers under new rules.
    """

    entries = [json.loads(line) for line in
               (night / "evidence_envelopes.jsonl").read_text().splitlines() if line]
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
        root = Path(tmp)
        (root / protocol["recorder_journal"]).write_bytes(
            (night / protocol["recorder_journal"]).read_bytes())
        evidence = root / "evidence"
        shutil.copytree(night / "evidence", evidence,
                        ignore=shutil.ignore_patterns("summary.json", "summary.md"))
        return campaign.pilot_summary(evidence, protocol, entries)


class NonObserverProcessTests(unittest.TestCase):
    """Cold gate QPE01-DAEMON-CONTAMINATION-01 (2026-09-23), ruling 10 §5.

    The forcing problem: on 2026-09-22 21:00 the pilot captured twelve
    envelopes while the system daemon `fseventsd` held a full busy core in
    every one of 243 samples, 16 h into a logged failure loop, and every rule
    the registration carried admitted the night -- because no rule read a
    named process's share, and because no journal row the chain has ever
    written carried `observer: true`, so the measurement's own power sampler
    was indistinguishable from the machine.
    """

    def ps_row(self, pid, ppid, command, cpu):
        return {"pid": pid, "ppid": ppid, "start_identity": "Tue Sep 22 21:00:00 2026",
                "start_epoch_s": 0., "command": command, "cumulative_cpu_seconds": cpu}

    def chain_table(self, cpu=0.):
        """The night's real process shape: recorder and collector are SIBLINGS.

        1000 is the executor (the chain root); it spawns the covariate
        recorder 1003 and, separately, each collector 1001.  `powermetrics`
        1002 is the COLLECTOR's child, so it is a cousin of the recorder, not
        a descendant -- which is the whole defect.
        """

        return {(row["pid"], row["start_identity"]): row for row in (
            self.ps_row(1, 0, "/sbin/launchd", 0.),
            self.ps_row(1000, 1, "/usr/bin/python3 -m joulewise.quiet_predicate_campaign run", cpu),
            self.ps_row(1001, 1000, "/usr/bin/python3 sample_quiet_predicate_evidence.py collect", cpu),
            self.ps_row(1002, 1001, "/usr/bin/powermetrics", 3 * cpu),
            self.ps_row(1003, 1000, "/usr/bin/python3 -m joulewise.quiet_predicate_campaign record", cpu),
            self.ps_row(1004, 1003, "/usr/bin/top", cpu),
            self.ps_row(341, 1, FSEVENTSD, 30 * cpu))}

    def test_regression_0_the_chain_root_marks_the_power_sampler_the_recorder_pid_does_not(self):
        from joulewise.quiet_admission import interval_metrics
        before, after = self.chain_table(0.), self.chain_table(1.)
        marked = {}
        for label, observer_pid in (("chain root", 1000), ("recorder only", 1003)):
            metrics = interval_metrics(before, after, interval_s=30., idle_fraction=.9,
                                       logical_cpu=16, observer_pid=observer_pid, wall_start=-1)
            marked[label] = {consumer["pid"]: consumer["observer"]
                             for consumer in metrics["top_consumers"]}
        # The cure: every process the measurement started is marked.
        self.assertEqual(marked["chain root"],
                         {1: False, 341: False, 1000: True, 1001: True,
                          1002: True, 1003: True, 1004: True})
        # The defect, reproduced: with the recorder as the observer root the
        # power sampler reads as a non-observer consumer -- which is why the
        # clean night's `powermetrics` sat at 0.111-0.115 "machine" cores.
        self.assertEqual(marked["recorder only"][1002], False)
        self.assertEqual(marked["recorder only"][1003], True)

    def test_regression_0_the_recorder_refuses_to_run_without_a_chain_root(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            with self.assertRaisesRegex(ValueError, "chain root pid"):
                campaign.record_covariates(PROTOCOL, Path(tmp))
            for bad in (0, -1, "1000", 1000.0):
                with self.assertRaisesRegex(ValueError, "chain root pid"):
                    campaign.record_covariates(PROTOCOL, Path(tmp), observer_pid=bad)

    def test_regression_0_record_covariates_hands_the_pid_to_every_observation(self):
        import signal as signal_module
        seen = []

        def one_sample(interval_s, observer_pid=None):
            seen.append((interval_s, observer_pid))
            os.kill(os.getpid(), signal_module.SIGTERM)  # the executor's own stop signal
            return {"metrics": {"busy_cores": 0}}

        previous = signal_module.getsignal(signal_module.SIGTERM)
        try:
            with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
                with patch("joulewise.quiet_admission.sample_interval", one_sample):
                    self.assertEqual(campaign.record_covariates(PROTOCOL, Path(tmp),
                                                                observer_pid=4242), 0)
                rows = [json.loads(line) for line in
                        (Path(tmp) / PROTOCOL["recorder_journal"]).read_text().splitlines() if line]
        finally:
            signal_module.signal(signal_module.SIGTERM, previous)
        self.assertEqual(seen, [(PROTOCOL["sample_interval_s"], 4242)])
        self.assertEqual(len(rows), 1)

    def test_regression_0_the_executor_launches_the_recorder_with_its_own_pid(self):
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise_scaled()
        recorder = next(argv for argv in calls if "record" in argv)
        self.assertIn("--observer-pid", recorder)
        self.assertEqual(recorder[recorder.index("--observer-pid") + 1], str(os.getpid()))

    def exercise_scaled(self, **kwargs):
        return FrozenExecutorTests.exercise(self, protocol=SCALED, **kwargs)

    def test_regression_1_a_full_core_daemon_excludes_every_envelope_it_ran_in(self):
        """The 2026-09-22 21:00 shape, at the archive's own magnitudes.

        Counterfactual input: twenty 30.355 s rows per envelope carrying
        `fseventsd` at 0.9995 busy cores (the archive's median) -- 606
        core-seconds, twenty times the registered 30 core-second bar -- and,
        in envelope 01 only, `mediaanalysisd` at 1.6 cores for eleven samples.
        The clean night's largest non-observer integral was 6.3 core-seconds,
        so the same code excludes nothing there.
        """

        contaminated = self.summarize_rows(lambda index: [
            journal_row(index, (FSEVENTSD, 341, .9995),
                        *(((("/System/Library/PrivateFrameworks/MediaAnalysis.framework/"
                             "Versions/A/Support/mediaanalysisd"), 763, 1.6),)
                          if index == 1 and sample < 11 else ()),
                        interval_s=30.355, offset=sample * 30, span=30)
            for sample in range(20)])
        clean = self.summarize_rows(lambda index: [
            journal_row(index, ("/usr/libexec/WindowServer", 411, .0105),
                        interval_s=30.355, offset=sample * 30, span=30)
            for sample in range(20)])
        self.assertEqual([v["excluded"] for v in contaminated["envelopes"]],
                         [["non_observer_process_busy"]] * 12)
        self.assertEqual(contaminated["retained"], 0)
        first = contaminated["envelopes"][0]["non_observer_process_busy"]
        self.assertEqual([(hit["process"], hit["pid"]) for hit in first],
                         [("fseventsd", 341), ("mediaanalysisd", 763)])
        self.assertAlmostEqual(first[0]["core_seconds"], 20 * .9995 * 30.355, places=3)
        self.assertAlmostEqual(first[1]["core_seconds"], 11 * 1.6 * 30.355, places=3)
        for envelope in contaminated["envelopes"][1:]:
            self.assertEqual([hit["process"] for hit in envelope["non_observer_process_busy"]],
                             ["fseventsd"])
        # The clean night's shape: 6.4 core-seconds, a fifth of the bar.
        self.assertEqual([v["excluded"] for v in clean["envelopes"]], [[]] * 12)
        self.assertEqual(clean["retained"], 12)
        # One shape for one meaning (fix round 1, lens S2 / Fable N5): the
        # summary always writes its re-derived list, empty when clean, as the
        # executor's rows always did.
        self.assertEqual(clean["envelopes"][0]["non_observer_process_busy"], [])

    def test_regression_6_the_integral_catches_the_burst_a_median_would_admit(self):
        # Ruling 10 Q2 MATERIAL: an eight-sample burst at 1.5 busy cores is
        # 360 core-seconds and about 270 J, and it passes a twenty-sample
        # median (twelve zeroes carry the middle).  The same eight samples at
        # 0.09 cores are 21.6 core-seconds, under the bar, and stay as idle
        # variance by design.
        for busy, excluded, core_seconds in ((1.5, True, 360.), (.09, False, 21.6)):
            with self.subTest(busy_cores=busy):
                report = self.summarize_rows(lambda index: [
                    journal_row(index, ("/usr/sbin/mediaanalysisd", 763,
                                        busy if sample < 8 else 0.),
                                interval_s=30., offset=sample * 30, span=30,
                                observer_busy=0.)
                    for sample in range(20)])
                envelope = report["envelopes"][0]
                median = envelope["busy_cores"]["median"]
                self.assertEqual(envelope["excluded"],
                                 ["non_observer_process_busy"] if excluded else [])
                if excluded:
                    self.assertAlmostEqual(
                        envelope["non_observer_process_busy"][0]["core_seconds"], core_seconds)
                    # The median the ruling rejected would have admitted it.
                    self.assertLess(median, .10)

    def summarize_rows(self, rows_for):
        """Twelve identical envelopes, with `rows_for(index)` as the journal."""

        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = Path(tmp) / "evidence"
            root.mkdir()
            entries = []
            for index in range(1, 13):
                out = root / f"envelope-{index:02d}"
                out.mkdir()
                (out / "session.json").write_text(json.dumps({
                    "session": "fixture", "boot_id": "boot", "os_build": "25G83", **stamps(),
                    "network_time_provenance": provenance(),
                    "power": {"recorder_kind": "powermetrics", "anchor": {"status": "bounded"}},
                    "interior": {"complete_support": True,
                                 "power": {"energy_j": {"rail_sum_w": index, "combined_w": index}}}}))
                (out / "rounds.jsonl").write_text(json.dumps(good_round()) + "\n")
                entries.append({"index": index, "scheduled_mono_s": index * 600, "start_drift_s": 0})
                for row in rows_for(index):
                    campaign.append_event(root.parent / PROTOCOL["recorder_journal"], row)
            campaign.pilot_summary(root, PROTOCOL, entries)
            return json.loads((root / "summary.json").read_text())

    def test_a_v2_night_never_emits_a_reason_its_registration_does_not_carry(self):
        # A269 ruling 10 Q2 byte-pins `exclusions`.  v2 has no such rule, so
        # the same journal that costs a v3 night every envelope costs a v2
        # night nothing -- the rule arrives with its registration.
        v2 = json.loads((ROOT / "configs/campaigns/quiet_predicate_evidence_01"
                         / "pilot_protocol_v2.json").read_text())
        self.assertIsNone(campaign.non_observer_rule(v2))
        self.assertIsNotNone(campaign.non_observer_rule(PROTOCOL))
        for missing in ({}, {"bar_core_seconds": 0, "abort_after_consecutive": 2},
                        {"bar_core_seconds": 30, "abort_after_consecutive": 0},
                        {"bar_core_seconds": "30", "abort_after_consecutive": 2}):
            with self.assertRaises(ValueError):
                campaign.non_observer_rule({**PROTOCOL, "non_observer_process_busy": missing})
        # A rule without its exclusion reason is a registration defect too.
        with self.assertRaisesRegex(ValueError, "without its exclusion reason"):
            campaign.non_observer_rule({**PROTOCOL, "exclusions": v2["exclusions"]})


class NonObserverAbortTests(FrozenExecutorTests):
    """Ruling 10 Q2: two consecutive excluded envelopes end the chain.

    The forcing problem is arithmetic: on 2026-09-22 the night ran its full
    three hours and produced twelve envelopes no rule could use.  Under the
    registered abort it would have ended about 31 minutes after t0 (600 s
    settle + 2 x 620 s), with the machine free for a re-arm the same night.
    """

    def busy_rows(self, busy_envelopes, busy_cores=6.):
        """A journal in which the named envelopes carry a daemon over the bar.

        At `SCALED`'s six-second envelopes one row of 6 busy cores over 6 s is
        36 core-seconds, past the registered 30; a clean envelope's row is
        0.01 cores, 0.06 core-seconds.
        """

        def rows(index, scheduled):
            busy = busy_cores if index in busy_envelopes else .01
            return [{"monotonic_start": scheduled, "monotonic_end": scheduled + 6,
                     "observer_cpu_s": .1,
                     "observation": {"interval_s": 6.,
                                     "metrics": {"busy_cores": busy,
                                                 "top_consumers": consumers(
                                                     (FSEVENTSD, 341, busy))}}}]
        return rows

    def test_regression_3_two_consecutive_exclusions_abort_the_chain_by_name(self):
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            protocol=SCALED, busy_rows=self.busy_rows({1, 2}))
        self.assertEqual(rc, 2)
        self.assertEqual(outcome["outcome"], "refused")
        self.assertEqual(outcome["envelopes_attempted"], 2)
        self.assertIn("2 consecutive envelopes excluded non_observer_process_busy",
                      outcome["error"])
        self.assertIn("fseventsd pid 341 36.0 core-s (bar 30)", outcome["error"])
        # The typed document: a reader holding only refusal.json can tell a
        # machine-state abort from a probe that failed.
        self.assertEqual(refusals, 1)
        document = self.refusal_documents[0]
        self.assertEqual(document["refusal"]["reason"], "non_observer_process_busy")
        self.assertEqual(document["verdict"], "REFUSED")
        self.assertIn("evidence chain refused: NonObserverAbort",
                      document["refusal"]["detail"])
        # No successor is arranged here: the D-182 addendum is Ed's to ratify.
        self.assertEqual(self.envelope_directories, ["envelope-01", "envelope-02"])

    def test_regression_3_one_exclusion_then_a_clean_envelope_never_aborts(self):
        # The counterfactual that decides the rule's shape: envelope 01 of the
        # 2026-09-22 night carried `mediaanalysisd` as well as the daemon, and
        # one such envelope in an otherwise clean night must not end it.
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            protocol=SCALED, busy_rows=self.busy_rows({1, 3}))
        self.assertEqual(rc, 0)
        self.assertEqual(outcome["outcome"], "complete")
        self.assertEqual(outcome["envelopes_attempted"], SCALED["envelopes"])
        self.assertEqual(refusals, 0)
        self.assertEqual([v["excluded"] for v in summary["envelopes"]],
                         [["non_observer_process_busy"], [], ["non_observer_process_busy"], []])

    @staticmethod
    def verdicts(rows, key):
        return {row["index"]: [(hit["process"], hit["pid"], round(hit["core_seconds"], 6))
                               for hit in row[key]] for row in rows}

    def test_regression_5_the_summary_re_derives_the_executors_own_exclusion_set(self):
        # The executor decides the abort in-chain from the journal; the
        # summary re-derives the same verdict from disk afterwards.  If those
        # two ever disagreed, the night's record would contradict its abort.
        #
        # Fix round 1 (lens S2): before, the summary overwrote the executor's
        # list only when it found an offender, so on a clean envelope the
        # executor's list passed through and this comparison compared the
        # executor with itself.  Now the summary ALWAYS writes its own list
        # under `non_observer_process_busy` and keeps the executor's under
        # `executor_non_observer_process_busy`; this test reads the two keys.
        rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
            protocol=SCALED, busy_rows=self.busy_rows({1, 3}))
        executor = self.verdicts(self.envelope_journal, "non_observer_process_busy")
        derived = self.verdicts(summary["envelopes"], "non_observer_process_busy")
        kept = self.verdicts(summary["envelopes"], "executor_non_observer_process_busy")
        self.assertEqual(kept, executor)
        self.assertEqual(derived, executor)
        self.assertEqual(executor, {1: [("fseventsd", 341, 36.)], 2: [],
                                    3: [("fseventsd", 341, 36.)], 4: []})
        # `excluded` follows the SUMMARY's own list, envelope by envelope.
        self.assertEqual({v["index"]: v["excluded"] for v in summary["envelopes"]},
                         {index: ["non_observer_process_busy"] if hits else []
                          for index, hits in derived.items()})
        self.assertEqual([v["non_observer_verdict_disagreement"] for v in summary["envelopes"]],
                         [False] * 4)

    def test_regression_5_a_tampered_executor_verdict_is_caught_not_passed_through(self):
        """The mutation counterfactual for regression 5 (fix round 1, lens S2).

        The executor's stored list for envelope 02 -- a clean envelope -- is
        tampered to name a fake offender before the summary reads it.  A
        summary that re-derives from the journal reports envelope 02 clean,
        keeps the tampered list beside it and flags the disagreement.  The
        16900e3d summary let the executor's list pass through on a clean
        envelope, so its row named the fake offender while its `excluded`
        lacked the reason, and the old regression-5 comparison (the summary's
        list against the executor's journal) found the two equal.
        """

        fake = {"process": "fakeoffenderd", "pid": 4242, "start_identity": "x",
                "core_seconds": 99., "bar_core_seconds": 30}
        real_summary = campaign.pilot_summary

        def tampered(directory, protocol, envelopes, *args, **kwargs):
            envelopes = [dict(entry, non_observer_process_busy=[fake]) if entry["index"] == 2 else entry
                         for entry in envelopes]
            return real_summary(directory, protocol, envelopes, *args, **kwargs)

        with patch.object(campaign, "pilot_summary", side_effect=tampered):
            rc, summary, outcome, refusals, calls, control, sessions = self.exercise(
                protocol=SCALED, busy_rows=self.busy_rows({3}))
        self.assertEqual(rc, 0)
        derived = self.verdicts(summary["envelopes"], "non_observer_process_busy")
        kept = self.verdicts(summary["envelopes"], "executor_non_observer_process_busy")
        # The detection: the summary's own verdict differs from the stored one.
        self.assertNotEqual(derived, kept)
        self.assertEqual(derived[2], [])
        self.assertEqual(kept[2], [("fakeoffenderd", 4242, 99.)])
        envelope = summary["envelopes"][1]
        self.assertEqual(envelope["excluded"], [])
        self.assertIs(envelope["non_observer_verdict_disagreement"], True)
        # Every other envelope agrees, and envelope 03 is excluded on its own.
        self.assertEqual([v["non_observer_verdict_disagreement"] for v in summary["envelopes"]],
                         [False, True, False, False])
        self.assertEqual(summary["envelopes"][2]["excluded"], ["non_observer_process_busy"])

# The v3 registration's bytes as of fix round 1 (the components text now
# names the load recorder as a sibling outside whole).  Pinned as a literal
# here AND as `night_gate.QPE01_PILOT_REGISTRATION_SHA256`.
V3_REGISTRATION_SHA256 = "9491bc370b515c7d56d21f87e0c6721be8cb2b6501b430b9dce75a93f59a6f0a"
V2_PROTOCOL = json.loads((ROOT / "configs/campaigns/quiet_predicate_evidence_01"
                          / "pilot_protocol_v2.json").read_text())


class ObserverFloorTests(unittest.TestCase):
    """Cold gate round 3 (ruling 31's reporting limbs, synthesis 35 §3).

    The forcing problem: `observer_floor_cores` summed each ROUND's
    `observer_cpu_s` -- the sampler's worker/census block -- and never read the
    `whole_envelope_observer_cpu_s` the session already recorded.  The 100 ms
    power recorder is reaped by the collector after the round block ends, so
    two thirds of the apparatus was missing: both archived nights reported
    ~0.053 cores where the whole envelope costs 0.16-0.18.  The corrected
    number is EXPECTED to fire the registered stop branch (0.16-0.18 > the
    0.05 smallest level); that is the honest registered result, not a defect.
    """

    def summarize(self, whole, spans=None, rounds=1.0, recorder=.2, drop=()):
        spans = [600.] * len(whole) if spans is None else spans
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = Path(tmp) / "evidence"
            root.mkdir()
            entries = []
            for index, (cpu, span) in enumerate(zip(whole, spans), 1):
                out = root / f"envelope-{index:02d}"
                out.mkdir()
                session = {"session": "fixture", "boot_id": "boot", "os_build": "25G83",
                           "start_stamp": {"monotonic_before_s": 1000.},
                           "end_stamp": {"monotonic_before_s": 1000. + span},
                           "whole_envelope_observer_cpu_s": cpu,
                           "network_time_provenance": provenance(),
                           "power": {"recorder_kind": "powermetrics", "anchor": {"status": "bounded"}},
                           "interior": {"complete_support": True,
                                        "power": {"energy_j": {"rail_sum_w": 10, "combined_w": 10}}}}
                for key in drop:
                    session.pop(key, None)
                (out / "session.json").write_text(json.dumps(session))
                row = dict(good_round(), observer_cpu_s=rounds)
                (out / "rounds.jsonl").write_text(json.dumps(row) + "\n")
                entries.append({"index": index, "scheduled_mono_s": index * 600, "start_drift_s": 0})
                campaign.append_event(root.parent / PROTOCOL["recorder_journal"],
                                      journal_row(index, observer_cpu_s=recorder))
            campaign.pilot_summary(root, PROTOCOL, entries)
            return json.loads((root / "summary.json").read_text())

    def test_the_floor_is_the_whole_envelope_over_the_collectors_own_span(self):
        # Counterfactual input: twelve envelopes whose ROUND block is 1 s but
        # whose whole envelope cost 105 s -- the archived shape, where the
        # round block is a third of the apparatus.  Under the v2 statistic
        # this reads 1/600 = 0.0017 cores and passes; the whole envelope over
        # the span is 0.175 and fires the branch.
        report = self.summarize([105.] * 12)
        self.assertAlmostEqual(report["observer_floor_cores"], .175)
        self.assertEqual(report["observer_support_s"], 7200.)
        self.assertEqual(report["observer_variation_cores"], 0.)
        self.assertEqual(report["block_two_stop"]["causes"],
                         ["observer_floor_above_smallest_holdable_share"])
        self.assertEqual(report["block_two_stop"]["outcome"], "no cutoff qualifies")
        components = report["envelopes"][0]["observer_floor_components"]
        self.assertEqual(components["round_block"], {"cpu_s": 1., "inside_whole": True})
        self.assertEqual(components["load_recorder"], {"cpu_s": .2, "inside_whole": False})
        self.assertEqual(components["power_recorder_residue"]["inside_whole"], True)
        self.assertAlmostEqual(components["power_recorder_residue"]["cpu_s"], 104.)
        # A DEFINITIONAL identity, not a measurement: the residue is defined
        # as whole minus round_block, so the two inside-whole components sum
        # to whole by construction.  It guards the bookkeeping (no component
        # outside whole may be subtracted from it), not the physics.
        self.assertAlmostEqual(components["round_block"]["cpu_s"]
                               + components["power_recorder_residue"]["cpu_s"],
                               components["whole_envelope_observer_cpu_s"], delta=1e-9)

    def test_the_residue_no_longer_subtracts_the_sibling_load_recorder(self):
        """Fix round 1, lens S1 as ruled by the magistrate (2026-09-23).

        The forcing fact: `whole_envelope_observer_cpu_s` is the collector's
        RUSAGE_SELF + RUSAGE_CHILDREN; the 30 s load recorder is launched by
        the executor as the collector's SIBLING and journals its own CPU, so
        it was never inside whole.  The 16900e3d formula subtracted it anyway
        (residue = whole - round_block - load_recorder), understating the
        power recorder's residue by exactly the load recorder's CPU.

        Counterfactual: a fixture whose load recorder is NOT zero (0.2 s per
        envelope).  The old formula gives 105 - 1 - 0.2 = 103.8; the ruled one
        gives 105 - 1 = 104.0.  With a zero load recorder the two agree and
        the test could not tell them apart.
        """

        report = self.summarize([105.] * 12, rounds=1.0, recorder=.2)
        old_formula = 105. - 1.0 - .2
        for value in report["envelopes"]:
            components = value["observer_floor_components"]
            self.assertGreater(components["load_recorder"]["cpu_s"], 0)
            self.assertAlmostEqual(components["power_recorder_residue"]["cpu_s"], 104.)
            self.assertNotAlmostEqual(components["power_recorder_residue"]["cpu_s"], old_formula)
            self.assertFalse(components["load_recorder"]["inside_whole"])
        # The ruled floor keeps the load recorder out; the REPORTED companion
        # adds the sibling back over the same readable envelopes and spans.
        self.assertAlmostEqual(report["observer_floor_cores"], 12 * 105. / 7200.)
        self.assertAlmostEqual(report["observer_floor_including_load_recorder_cores"],
                               (12 * 105. + 12 * .2) / 7200.)
        # Reported only: the stop branch reads the ruled floor, never the
        # companion (a companion above the smallest share changes no cause).
        self.assertEqual(report["block_two_stop"]["causes"],
                         ["observer_floor_above_smallest_holdable_share"])
        self.assertIn("sibling process of the collector", report["observer_floor_components_role"])
        self.assertIn("never a stop input", report["observer_floor_components_role"])

    def test_the_summary_observer_definition_is_the_ruled_sentence_plus_the_sibling_fact(self):
        # Fix round 1 (lens N5): the pre-v3 string ("SELF + reaped CHILDREN,
        # including collector, recorder, sampler and census") was one of the
        # three conflicting definitions refuter 32 named.
        ruled = PROTOCOL["observer_floor"]["definition"]
        report = self.summarize([105.] * 12)
        self.assertEqual(report["observer_definition"],
                         ruled + ", with the 30 s load recorder a sibling process reported "
                                 "beside it (see observer_floor_components_role)")

    def test_the_registration_pins_the_corrected_components_text(self):
        """Fix round 1 (lens S1): v3's bytes change only in the components text.

        The four ruled strings stay byte-for-byte as ruling 31 / brief 6(c)
        gave them -- including the `definition`'s "including ... load
        recorder", whose inaccuracy the magistrate holds for the block-two
        consult rather than patching -- and the magistrate-authored
        `components` text now says in plain words that the load recorder is a
        sibling outside whole.  The digest is pinned here as a literal so a
        silent change to the bytes cannot pass by re-pinning the constant.
        """

        import hashlib
        raw = (ROOT / campaign.PROTOCOL_PATH).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(digest, V3_REGISTRATION_SHA256)
        self.assertEqual(digest, night_gate.QPE01_PILOT_REGISTRATION_SHA256)
        floor = json.loads(raw)["observer_floor"]
        self.assertEqual(floor["statistic"],
                         "per envelope: session.whole_envelope_observer_cpu_s / (end_stamp.monotonic_before_s"
                         " - start_stamp.monotonic_before_s); campaign value = sum of "
                         "whole_envelope_observer_cpu_s over all readable envelopes / sum of their spans")
        self.assertEqual(floor["definition"],
                         "SELF + all reaped CHILDREN, including collector, power recorder, load recorder "
                         "and census; never subtracted")
        self.assertEqual(floor["limitation_sentence"],
                         "Block two measures the marginal energy of the level on top of this observer, "
                         "not on an idle machine.")
        self.assertEqual(floor["supersedes"],
                         "v2 observer_floor_cores summed per-round observer_cpu_s (worker/census block only) "
                         "and omitted the power recorder; v2 reported 0.0531 (20260922-0217) and 0.0528 "
                         "(20260922-2100); corrected whole-envelope values 0.176 and 0.159 cores")
        self.assertIn("load_recorder (30 s covariate recorder; inside_whole false) is a sibling process "
                      "of the collector", floor["components"])
        self.assertIn("outside whole_envelope_observer_cpu_s", floor["components"])
        self.assertIn("never a stop input", floor["components"])
        self.assertNotIn("whole minus those two", floor["components"])

    def test_the_variation_is_the_sample_sd_of_the_per_envelope_shares(self):
        import statistics
        whole = [105. + (2. if index % 2 else -2.) for index in range(12)]
        report = self.summarize(whole)
        self.assertAlmostEqual(report["observer_variation_cores"],
                               statistics.stdev(cpu / 600 for cpu in whole))
        # A span that differs per envelope is honoured, not rounded to 600.
        uneven = self.summarize([105.] * 12, spans=[597. + index for index in range(12)])
        self.assertAlmostEqual(uneven["observer_floor_cores"],
                               12 * 105. / sum(597. + index for index in range(12)))

    def test_a_session_without_the_whole_envelope_cost_or_span_refuses(self):
        for missing in ("whole_envelope_observer_cpu_s", "start_stamp", "end_stamp"):
            with self.subTest(missing=missing):
                with self.assertRaisesRegex(ValueError, "absent evidence is never a pass"):
                    self.summarize([105.] * 12, drop=(missing,))

    @unittest.skipUnless(CLEAN.is_dir() and CONTAMINATED.is_dir(),
                         "the 2026-09-22 harvest archives are not on this machine")
    def test_both_archived_nights_re_derive_to_the_corrected_floor(self):
        # The two nights' own bytes, under the corrected statistic, with the
        # v2 retention rules so nothing but the floor changes (exhibit G and
        # ruling 31 §1 recompute the same numbers independently).
        for night, floor, variation, including in ((CLEAN, .17572, .00214, .183),
                                                   (CONTAMINATED, .15909, .00267, .166)):
            with self.subTest(night=night.parent.name):
                archived = json.loads((night / "evidence/summary.json").read_text())
                report = archive_summary(night, V2_PROTOCOL)
                self.assertAlmostEqual(report["observer_floor_cores"], floor, places=3)
                self.assertAlmostEqual(report["observer_variation_cores"], variation, places=4)
                # The registered stop branch, unchanged in form, on the
                # corrected input.  It is read from `stop_branch` directly for
                # the 02:17 night: that night predates `power.recorder_kind`,
                # so re-deriving it with TODAY's code trips the bench-replay
                # guard and blanks every energy field -- an artefact of the
                # re-derivation, not of this change, and the reason its
                # energies are compared only where the guard did not fire.
                self.assertEqual(campaign.stop_branch(observer_floor=report["observer_floor_cores"],
                                                      protocol=V2_PROTOCOL)["causes"],
                                 ["observer_floor_above_smallest_holdable_share"])
                # The v2 numbers these supersede, for the record.
                self.assertLess(archived["observer_floor_cores"], .054)
                # The two inside-whole components sum to whole (a definitional
                # identity: the residue IS whole minus round_block), and the
                # sibling load recorder is reported outside it.
                for value in report["envelopes"]:
                    components = value["observer_floor_components"]
                    self.assertAlmostEqual(
                        components["round_block"]["cpu_s"] + components["power_recorder_residue"]["cpu_s"],
                        components["whole_envelope_observer_cpu_s"], delta=1e-9)
                    self.assertFalse(components["load_recorder"]["inside_whole"])
                    self.assertGreater(components["load_recorder"]["cpu_s"], 0)
                # The reported companion with the sibling load recorder added
                # back (magistrate ruling on lens S1): ~0.183 / ~0.166 cores.
                self.assertAlmostEqual(report["observer_floor_including_load_recorder_cores"],
                                       including, delta=.002)
                self.assertGreater(report["observer_floor_including_load_recorder_cores"],
                                   report["observer_floor_cores"])
                if report["status"] != campaign.REPLAY_NEVER_EVIDENCE:
                    self.assertEqual([v["joules"] for v in report["envelopes"]],
                                     [v["joules"] for v in archived["envelopes"]])
                    self.assertEqual(report["pair_sd_j"], archived["pair_sd_j"])
                    self.assertEqual(report["s_upper"], archived["s_upper"])
                    self.assertEqual(report["retained"], archived["retained"])
                    self.assertEqual([v["excluded"] for v in report["envelopes"]],
                                     [v["excluded"] for v in archived["envelopes"]])

    @unittest.skipUnless(CLEAN.is_dir() and CONTAMINATED.is_dir(),
                         "the 2026-09-22 harvest archives are not on this machine")
    def test_the_contaminated_night_loses_every_envelope_under_v3(self):
        # Regression 1 on the night's own bytes.  Both archived journals were
        # written before the observer-marking cure, so every row reads
        # `observer: false` -- including the measurement's own `powermetrics`,
        # which is why the production rule names it here beside the daemon and
        # why the diagnostic re-analysis must state an explicit observer set.
        report = archive_summary(CONTAMINATED, PROTOCOL)
        self.assertEqual([v["excluded"] for v in report["envelopes"]],
                         [["non_observer_process_busy"]] * 12)
        self.assertEqual(report["retained"], 0)
        named = {hit["process"] for value in report["envelopes"]
                 for hit in value["non_observer_process_busy"]}
        self.assertEqual(named, {"fseventsd", "mediaanalysisd", "powermetrics"})
        daemon = next(hit for hit in report["envelopes"][0]["non_observer_process_busy"]
                      if hit["process"] == "fseventsd")
        self.assertAlmostEqual(daemon["core_seconds"], 575.6, places=0)
        # The clean night has no daemon at all: its only named consumer is the
        # unmarked power sampler, at a third of the daemon's cost.
        clean = archive_summary(CLEAN, PROTOCOL)
        self.assertEqual({hit["process"] for value in clean["envelopes"]
                          for hit in value["non_observer_process_busy"]}, {"powermetrics"})
