"""WP22: synthetic W1 dry run against FINAL-DESIGN 219fb1515 + Amendment 1 6eb1ff5be.

Quick tests (always): the synthetic inputs pass the kit's fail-closed admission,
and the roster bridge reproduces A1. The full 18-member window runs only with
JW_WP22_FULL=1 (about 3 min each under ``nice -n 19 taskpolicy -b``). Properties
where the current pipeline diverges from the design are expectedFailure and
name the WP22 finding; an unexpected success means the divergence was fixed.
Everything is synthetic: no model, SHADE cache, sensor or network is opened.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts import align_v4_w1_synthetic as dry
from scripts import align_v4_kit as kit

A1_ROLES = ['anchor'] * 4 + ['D', 'X-G', 'Y-S', 'D', 'X-S', 'Y-G', 'D', 'Y-G', 'X-S', 'D', 'Y-S', 'X-G', 'D', 'D']
FULL = os.environ.get('JW_WP22_FULL') == '1'


class KitBridgeTests(unittest.TestCase):
    def test_synthetic_inputs_pass_admission_and_roster_is_a1(self):
        plan, configs, files = dry.build_kit(dry.SYN_INPUTS)
        self.assertEqual(plan['status'], 'FOR_LEAD_REVIEW')
        self.assertEqual([m['role'] for m in plan['members']], A1_ROLES)
        self.assertEqual({m['ordinal']: m['replay_of'][-3:] for m in plan['members'] if m.get('replay_of')},
                         {12: 'e10', 13: 'e09', 15: 'e07', 16: 'e06', 17: 'e05'})
        positions = {}
        for m in plan['members']:
            positions.setdefault(m['role'], []).append(m['ordinal'])
        self.assertEqual({k: sum(v) for k, v in positions.items() if k[0] in 'XY'},
                         {'X-G': 22, 'X-S': 22, 'Y-S': 22, 'Y-G': 22})
        self.assertEqual([m['seed_index'] for m in plan['members'] if m['role'] == 'D'], [1, 1, 1, 1, 1, 93])

    def test_consumer_custody_rebinds_to_synthesized_capture_bytes(self):
        from joulewise.schemas import BenchmarkConfig
        _, raw, _ = dry.build_kit(dry.SYN_INPUTS)
        with tempfile.TemporaryDirectory() as tmp:
            configs = {o: dry.synthesize(c, Path(tmp)) for o, c in raw.items()}
            digest = dry.rebind(configs)
            self.assertEqual(digest, hashlib.sha256(kit.bundle_config_bytes(
                BenchmarkConfig.from_mapping(configs[5]))).hexdigest())
            for o in range(6, 19):
                spec = json.loads(configs[o]['workload_profile']['prompt_text'])
                if 'thermal' in spec:
                    self.assertEqual(spec['thermal']['window_reference']['source_config_sha256'], digest)

    def test_contrast_deadman_follows_the_30b_member_law_and_admits_a_g0_timeout(self):
        # WP22 F1 (resolved on the integrated head): the WP7 330 s deadman,
        # armed at G0 entry, ended contrast arms before a G0 timeout could
        # even be reached. The kit now applies FD's T_dead,m to the 30B.
        plan, _, _ = dry.build_kit(dry.SYN_INPUTS)
        dead = {m['spec'].get('deadman_s') for m in plan['members'] if m['role'][:1] in 'XY'}
        self.assertEqual(dead, {kit.CONTRAST_DEADMAN_S})
        proof = kit.w1_contrast_g0_cap(dry.SYN_R1_SLOTS, 5)
        self.assertLessEqual(proof['value_s'] + proof['episode_s'] + 10, kit.CONTRAST_DEADMAN_S)
        self.assertIsNone(proof['predeclared'])

    def test_synthetic_t_dead_is_bound_by_l1_and_the_r1_tail(self):
        r1 = dry.SYN_INPUTS['R1']
        self.assertEqual(r1['T_dead'], kit.l1_t_dead(r1['I_D'], dry.SYN_R1_SLOTS['max_r1_tail_s']))
        plan, _, _ = dry.build_kit(dry.SYN_INPUTS)
        self.assertEqual({m['ac_powermode'] for m in plan['members']}, {0})
        with self.assertRaisesRegex(ValueError, 'AC powermode'):
            dry.build_kit(dry.SYN_INPUTS, {**dry.SYN_R1_SLOTS, 'ac_powermode': None})


class MinimalDryRunTests(unittest.TestCase):
    """The 4 s WP22 dry run runs in the DEFAULT test run (no JW_WP22_FULL opt-in), so CI sees it.

    Opus cold HIGH-1: the full-window classes below skip by default, which hid a red dry run.
    """

    def test_minimal_synthetic_w1_reaches_the_desk_with_u3_pending_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'w1'
            self.assertEqual(dry.main([str(out), '--inject', 'none', '--members', '5']), 0)
            record = json.loads((out / 'dry_run_record.json').read_text())
            self.assertEqual(record['desk_status'], 'ok', record.get('desk_error'))
            pilot = (out / 'desk/PILOT.json')
            desk = json.loads(pilot.read_text())
            self.assertTrue(desk['u3_pending'])            # a PENDING U3 is an input, not a crash
            self.assertIsNone(desk['u3_bar'])
            for window in desk['model_windows'].values():
                self.assertNotEqual(window['U3']['status'], 'pass')
            from joulewise.align.apple import v4_registration as registration
            with self.assertRaises(ValueError):           # arming stays refused
                registration.validate_u3(None)

    def test_the_synthetic_contrast_is_rederived_after_the_wp18_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'w1'
            dry.main([str(out), '--inject', 'none', '--members', '5'])
            results = json.loads((out / 'run_results.json').read_text())
            inputs = results['inputs']
            slots = {**dry.SYN_R1_SLOTS, 'x_g': {**dry.SYN_R1_SLOTS['x_g'],
                                                 'admitted_turns': inputs['WP18']['X']['max_turns']}}
            contrast = kit.w1_contrast_g0_cap(slots, inputs['WP18']['X']['max_turns'])
            self.assertEqual(inputs['R1']['thermal_policy']['contrast_fit'], contrast)
            self.assertNotEqual(inputs['WP18']['X']['max_turns'], dry.SYN_INPUTS['WP18']['X']['max_turns'])


class _Window(unittest.TestCase):
    ARGS = ()

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'w1'
        dry.main([str(cls.out), *cls.ARGS])
        cls.record = json.loads((cls.out / 'dry_run_record.json').read_text())
        cls.results = json.loads((cls.out / 'run_results.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def member(self, ordinal):
        return next(m for m in self.results['members'] if m['ordinal'] == ordinal)

    def desk_member(self, ordinal):
        run_id = self.member(ordinal)['run_id']
        return next(m for m in self.record['desk']['members'] if m['id'] == run_id)

    def desk_model(self, prefix):
        return next(v for k, v in self.record['desk']['model_windows'].items()
                    if k.startswith(prefix) and k.endswith('/W1'))


@unittest.skipUnless(FULL, 'set JW_WP22_FULL=1 for the full synthetic window')
class CleanWindowTests(_Window):
    ARGS = ('--inject', 'none')

    def test_all_members_succeed_without_exclusions(self):
        for m in self.results['members']:
            self.assertEqual(m['status'], 'succeeded', m['ordinal'])
        self.assertEqual([m['calibration_exclusions'] for m in self.record['desk']['members']],
                         [[]] * len(self.record['desk']['members']))

    def test_desk_energy_matches_independent_world_integral(self):
        oracle = {m['run_id']: m['E_oracle_j'] for m in self.record['expected']['members']}
        for m in self.record['desk']['members']:
            if m['id'] in oracle:
                # Gated members agree to <0.1 J; ungated anchors' guard-cut
                # edges differ by up to ~2.4 J, inside the desk's own bound.
                self.assertAlmostEqual(m['turn_owned_j'], oracle[m['id']],
                                       delta=max(0.5, m['turn_owned_half_width_j']))

    def test_u1_u3_and_contrast_match_design(self):
        for prefix, model in (('Qwen3.8', 'D'), ('Qwen3-30B', '30B')):
            desk, expected = self.desk_model(prefix), self.record['expected']['models'][model]
            for u in ('U1', 'U3', 'U4', 'U5', 'U6'):
                # R11/R03: no U3 bar is installed (pending), so the desk reports U3 inconclusive
                # instead of the oracle's pass; every other check is unchanged.
                want = 'inconclusive' if u == 'U3' else expected[u]
                self.assertEqual(desk[u]['status'], want, (model, u))
            self.assertEqual(desk['consequence'], expected['consequence'])
        desk = self.record['desk']['deciding_experiment']
        oracle = self.record['expected']['contrast_token_identical_runs']
        self.assertEqual(desk['verdict'], oracle['verdict'])
        # R06: the desk's stage-adjusted eight-row fit differs from the oracle's plain
        # difference by a fraction of a joule; the verdict above is the contract.
        self.assertAlmostEqual(desk['arm_effect_j'], oracle['delta_j'], delta=0.1)


@unittest.skipUnless(FULL, 'set JW_WP22_FULL=1 for the full synthetic window')
class InjectedWindowTests(_Window):
    def test_desk_runs_on_a_window_with_failed_members(self):
        self.assertEqual(self.record['desk_status'], 'ok', self.record.get('desk_error'))

    def test_clean_members_succeed(self):
        for o in (1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 15, 16, 17):
            self.assertEqual(self.member(o)['status'], 'succeeded', o)

    def test_os_level_nonzero_is_x1(self):
        self.assertIn('thermal.os_level_nonzero', self.desk_member(13)['calibration_exclusions'])

    def test_malformed_xml_stops_and_is_excluded(self):
        self.assertIn('episode.malformed_tool_call:1', self.desk_member(11)['calibration_exclusions'])

    def test_deadman_is_x7(self):
        self.assertEqual(self.member(14)['status'], 'failed')
        self.assertTrue(any(f.startswith('episode.deadman:') for f in self.desk_member(14)['calibration_exclusions']))

    def test_g0_timeout_ends_the_member_promptly_as_x2(self):
        # WP22 F2, resolved in round 4 (cold pass MEDIUM-2): the deadman starts
        # at G0 entry, so going on after 600 s of G0 left D ~486 s for an
        # ~900 s episode and X2 became X7. An unreleased G0 now ends the
        # member before its first turn; it stays X2 and fails nothing.
        self.assertEqual(self.member(8)['status'], 'succeeded')
        self.assertEqual(self.desk_member(8)['calibration_exclusions'], ['thermal.start_gate_timeout'])

    @unittest.expectedFailure
    def test_collector_death_is_x4_and_episode_continues(self):
        # WP22 F3, accepted divergence: §2.6 makes >10% failed reads a timed
        # wait plus X4; WP8 F2 (8ef3c30f4) deliberately fails the member fast
        # on a dead collector instead. The desk still counts it as X4 (see
        # test_d_u1_counts_two_thermal_exclusions_and_fails).
        self.assertEqual(self.member(18)['status'], 'succeeded')
        self.assertIn('thermal.state_unobserved', self.desk_member(18)['calibration_exclusions'])

    def test_u4_to_u6_inconclusive_in_w1(self):
        for result in self.record['desk']['model_windows'].values():
            for k in (4, 5, 6):
                self.assertEqual(result[f'U{k}']['status'], 'inconclusive')

    def test_d_u1_counts_two_thermal_exclusions_and_fails(self):
        # Design: 8 (X2) + 18 (X4) -> 2 > 1 -> D "thermal protocol not met".
        # The dead-collector member fails fast (WP8 F2) and still counts as X4.
        d = self.desk_model('Qwen3.8')
        self.assertEqual(d['U1']['status'], 'fail')
        self.assertEqual(d['consequence'], 'thermal protocol not met')

    def test_30b_u1_counts_the_x1_member_and_passes(self):
        result = self.desk_model('Qwen3-30B')
        self.assertEqual(result['U1']['thermal_excluded_members'], 1)
        self.assertEqual(result['U1']['status'], 'pass')

    def test_contrast_verdict_matches_design_rule(self):
        expected = self.record['expected']['contrast_excluding_X_codes']['verdict']
        self.assertEqual(self.record['desk']['deciding_experiment']['verdict'], expected)


if __name__ == '__main__':
    unittest.main()
