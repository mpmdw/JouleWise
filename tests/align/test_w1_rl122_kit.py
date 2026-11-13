"""RL-122 item 7: the W1 kit takes the rebound pair and RL-122 3(a)'s planning release.

Dry checks on synthetic R1 records and repository files only (the saved Part B
D classification stands in for the night's); no host or study data.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import r1_phase_table, r1_runtime as rt
from scripts import align_r1_rehearsal as r1, align_v4_kit as kit, align_w1_budget_procedure as procedure
from tests.align.test_v4_kit import ready_inputs

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'configs/align/v4/r1_runtime.json'
TABLE = ROOT / 'docs/run_reports/2026-11-12-rl122/smoke_part_b.rl122.json'
# r1_runtime thermometry(): the classifier fields the runtime keeps in its summary.
RUNTIME_KEEP = ('status', 's_fast', 's_slow', 'r0_sensors', 'sensor_pick_changed', 'flags', 'die_candidates',
                'heatsink_candidates', 'record_only', 'phases', 'journal_rows', 'alias_groups', 'alias_rule',
                'classification_sha256')


def night_d(classification, pair, r0_keys):
    """The runtime's confirmation-path summary (r1_runtime thermometry), projected by the driver."""
    confirmation = rt.sensor_admissibility(classification, pair, r0_keys)
    summary = {key: classification.get(key) for key in RUNTIME_KEEP}
    summary.update(status='pass' if confirmation['ok'] else 'fail', **pair,
                   registered_picks={r: classification[r] for r in ('s_fast', 's_slow')},
                   night_confirmation=confirmation, sensor_pick_changed=False,
                   flags=[] if confirmation['ok'] else ['r1.sensor_inadmissible'])
    block = {**summary, 'reasons': confirmation['reasons'], 'classification_file': 'inventory/r1_classification.json'}
    return r1.thermometry_record(r1.STEP_D_NAME, {'thermometry': block}), confirmation


class RebindPairDryCheck(unittest.TestCase):
    """RL-122 item 7 checklist: the W1 kit accepts TV0h / TVh0 given an ok night confirmation."""

    def setUp(self):
        self.config, _ = rt.load_config(CONFIG)
        self.classification = json.loads(TABLE.read_bytes())['classification_table']['classification']
        self.pair = {r: self.config['sensors'][r] for r in ('s_fast', 's_slow')}
        self.inputs, self.slots = ready_inputs()
        policy = self.inputs['R1']['thermal_policy']
        policy['sensors'].update(self.pair)
        policy['classification_sha256'] = self.classification['classification_sha256']

    def ready(self, d):
        self.slots['thermometry']['D'] = d
        kit.require_ready(self.inputs, self.slots)

    def test_kit_accepts_the_pair_on_an_ok_confirmation(self):
        self.assertEqual(self.pair, {'s_fast': 'TV0h', 's_slow': 'TVh0'})
        d, confirmation = night_d(self.classification, self.pair, self.config['r0_classified_keys'])
        self.assertTrue(confirmation['ok'], confirmation)
        self.assertEqual(confirmation['authority'], 'RL-78')
        # The classifier's own slow pick is a heatsink key; TVh0 is admitted only as the fixed pair.
        self.assertEqual(d['registered_picks'], {'s_fast': 'TV0h', 's_slow': 'Th0C'})
        self.assertNotIn('TVh0', d['heatsink_candidates'])
        self.ready(d)

    def test_kit_refuses_without_an_ok_confirmation_or_with_aliased_keys(self):
        d, _ = night_d(self.classification, self.pair, self.config['r0_classified_keys'])
        for mutate, message in (
                (lambda x: x['night_confirmation'].update(ok=False), 'heatsink list'),
                (lambda x: x['night_confirmation'].update(authority='RL-122'), 'heatsink list'),
                (lambda x: x['night_confirmation'].update(s_slow='Th0C'), 'heatsink list'),
                (lambda x: x.update(s_slow='Th0C'), 'must equal'),
                (lambda x: x['alias_groups'].__setitem__(x['alias_groups'].index(['TV0h', 'TV1h']),
                                                         ['TV0h', 'TV1h', 'TVh0']), 'aliased')):
            bad = deepcopy(d)
            mutate(bad)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.ready(bad)


def planning_slots(names, *, reason=kit.PLANNING_RELEASE_REASON):
    """A ready R1 record whose planning turns ``names`` timed out at G0, flagged as the driver flags it."""
    inputs, slots = ready_inputs()
    results = {r1.STEP_D_NAME: {'slots': slots['slots'], 'slot_detail': {}, 'episode_flags': []},
               **{name: {'g0_outcome': 'released'} for name, _ in r1_phase_table.GATED_D_RUNS},
               'X_G_contrast': {'g0_outcome': 'released'}}
    inconclusive = {name: reason for name in names}
    u5 = {'verdict': 'inconclusive', 'c': 1.0, 'reason': 'designed start state(s) INCONCLUSIVE (R6-2)'}
    slots.update(inconclusive_segments=inconclusive, u5=u5,
                 planning_temperature={'label': 'PRINT_ONLY_R1_PLANNING_TEMPERATURE_SECONDARY',
                                       'status': 'inconclusive', 'inconclusive_states': sorted(names)},
                 inadmissible_slots=r1.inadmissible_slots(results, inconclusive, slots['thermometry'],
                                                          {'verdict': 'pass'}, u5, None))
    return inputs, slots


def release_for(slots, names, **row):
    segment = {'os_levels': [0], 'pm_states': ['Nominal'], 'heater_key': 'TVh0',
               'band_edge_c': 36.018, 'heater_key_max_last_300s_c': 36.4, **row}
    return {'schema': kit.R1_PLANNING_RELEASE_SCHEMA, 'authority': kit.PLANNING_RELEASE_AUTHORITY,
            'lead_signature': 'lead: synthetic-test 2026-11-12', 'r1_record': kit.r1_record_identity(slots),
            'desk_print': {'path': 'docs/run_reports/synthetic/planning_desk.json', 'sha256': 'e' * 64},
            'segments': {name: dict(segment) for name in names}}


class PlanningReleaseTests(unittest.TestCase):
    """RL-120 item 3 extended to R+0 by RL-122 3(a)."""

    def test_segment_names_are_the_drivers(self):
        names = [name for name, kind, *_ in r1_phase_table.phase_plan() if kind in r1.contract.PLANNING_KINDS]
        self.assertEqual(sorted(names), sorted(kit.PLANNING_SEGMENTS))
        self.assertEqual(kit.planning_heater_key(), 'TVh0')

    def test_as_built_kit_refuses_a_planning_timeout_without_the_record(self):
        inputs, slots = planning_slots(['planning_turn_R_plus_4C'])
        self.assertEqual(slots['inadmissible_slots']['U5'], ['r1.g0_timeout_run', 'r1.u5_inconclusive'])
        with self.assertRaisesRegex(ValueError, 'INCONCLUSIVE'):
            kit.require_ready(inputs, slots)

    def test_the_ruled_pattern_does_not_block(self):
        for names in (['planning_turn_R_plus_0C'], ['planning_turn_R_plus_2C', 'planning_turn_R_plus_4C'],
                      list(kit.PLANNING_SEGMENTS)):
            inputs, slots = planning_slots(names)
            for row in ({}, {'heater_key_max_last_300s_c': 36.018 - 0.3}, {'heater_key_max_last_300s_c': 35.95}):
                with self.subTest(names=names, row=row):
                    kit.require_ready(inputs, slots, planning_release=release_for(slots, names, **row))

    def test_any_other_pattern_is_refused(self):
        names = ['planning_turn_R_plus_2C', 'planning_turn_R_plus_4C']
        inputs, slots = planning_slots(names)
        cases = [
            (dict(os_levels=[0, 1]), 'OS level'),
            (dict(pm_states=['Nominal', 'Moderate']), 'non-Nominal'),
            (dict(heater_key_max_last_300s_c=36.018 - 0.31), 'band edge'),
            (dict(heater_key_max_last_300s_c=None), 'band edge'),
            (dict(heater_key='Th0C'), 'heater key'),
        ]
        for row, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                kit.require_ready(inputs, slots, planning_release=release_for(slots, names, **row))
        record = release_for(slots, names)
        for mutate, message in (
                (lambda r: r['segments'].pop(names[0]), 'exactly'),
                (lambda r: r['segments'].update(planning_turn_R_plus_0C=r['segments'][names[0]]), 'exactly'),
                (lambda r: r.update(lead_signature=kit.UNSIGNED), 'not signed'),
                (lambda r: r['r1_record'].update(I_D=1.0), 'different R1 record'),
                (lambda r: r.update(authority='RL-120 item 3'), 'authority')):
            bad = deepcopy(record)
            mutate(bad)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                kit.require_ready(inputs, slots, planning_release=bad)

    def test_the_measure_is_the_last_300_s_peak(self):
        # PR #752 cold review F1: the preheat overshoots the edge early in nearly
        # every planning G0; only the last 300 s of the interval count.
        self.assertEqual((kit.PLANNING_RELEASE_PEAK_FIELD, kit.PLANNING_RELEASE_WINDOW_S),
                         ('heater_key_max_last_300s_c', 300))
        names = ['planning_turn_R_plus_2C']
        inputs, slots = planning_slots(names)
        overshoot_then_inside = release_for(slots, names, heater_key_max_c=41.0,
                                            heater_key_max_last_300s_c=36.018 - 1.0)
        with self.assertRaisesRegex(ValueError, 'last 300 s of G0'):
            kit.require_ready(inputs, slots, planning_release=overshoot_then_inside)
        whole_g0_only = release_for(slots, names, heater_key_max_c=41.0)
        whole_g0_only['segments'][names[0]].pop('heater_key_max_last_300s_c')
        with self.assertRaisesRegex(ValueError, 'last 300 s of G0'):
            kit.require_ready(inputs, slots, planning_release=whole_g0_only)
        # RL-122 3(a): a steady hold 0.06 to 0.21 C under the edge, or a crossing, still passes.
        for peak in (36.018 - 0.21, 36.018 - 0.06, 36.5):
            with self.subTest(peak=peak):
                kit.require_ready(inputs, slots, planning_release=release_for(
                    slots, names, heater_key_max_last_300s_c=peak))

    def test_the_record_cites_its_desk_print(self):
        names = ['planning_turn_R_plus_0C']
        inputs, slots = planning_slots(names)
        for desk in (None, {}, {'path': '', 'sha256': 'e' * 64}, {'path': 'desk.json', 'sha256': 'e' * 63}):
            record = release_for(slots, names)
            if desk is None:
                record.pop('desk_print')
            else:
                record['desk_print'] = desk
            with self.subTest(desk=desk), self.assertRaisesRegex(ValueError, 'desk print'):
                kit.require_ready(inputs, slots, planning_release=record)

    def test_the_heater_key_comes_from_root(self):
        # PR #752 cold review F4: require_w1_ready(root) reads the heater key from root.
        names = ['planning_turn_R_plus_0C']
        inputs, slots = planning_slots(names)
        with tempfile.TemporaryDirectory() as tmp:
            config = json.loads(CONFIG.read_bytes())
            config['sensors']['s_slow'] = 'Tsyn'
            target = Path(tmp) / 'configs/align/v4/r1_runtime.json'
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(config))
            self.assertEqual(kit.planning_heater_key(tmp), 'Tsyn')
            with self.assertRaisesRegex(ValueError, 'heater key'):
                kit.check_r1_evidence(inputs, slots, planning_release=release_for(slots, names), root=Path(tmp))
            kit.check_r1_evidence(inputs, slots, planning_release=release_for(slots, names, heater_key='Tsyn'),
                                  root=Path(tmp))

    def test_other_flags_and_segments_stay_refused(self):
        names = ['planning_turn_R_plus_0C']
        inputs, slots = planning_slots(names, reason='r1.g0_timeout_run,r1.preheat_cap_reached')
        with self.assertRaisesRegex(ValueError, 'not a G0 timeout alone'):
            kit.require_ready(inputs, slots, planning_release=release_for(slots, names))
        for mutate, message in (
                (lambda s: s['inconclusive_segments'].update(D_bank_benign_s1_gated_held='r1.g0_timeout_run'),
                 'INCONCLUSIVE'),
                (lambda s: s['inadmissible_slots']['U5'].append('r1.agent_feed_overlap'), 'slot flags'),
                (lambda s: s['inadmissible_slots']['S6'].append('r1.gated_timeout_or_hold_suppression'), 'slot flags'),
                (lambda s: s['u5'].update(verdict='pass'), 'print inconclusive'),
                (lambda s: s['planning_temperature'].update(inconclusive_states=[]), 'print inconclusive')):
            inputs, slots = planning_slots(names)
            record = release_for(slots, names)
            mutate(slots)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                kit.require_ready(inputs, slots, planning_release=record)

    def test_budget_procedure_takes_the_same_release(self):
        names = ['planning_turn_R_plus_0C', 'planning_turn_R_plus_4C']
        _, slots = planning_slots(names)
        self.assertEqual(procedure.decide(slots, 12)['step'], 'R1-RERUN')
        released = procedure.decide(slots, 12, planning_release=release_for(slots, names))
        self.assertNotEqual(released['step'], 'R1-RERUN')
        _, clean = ready_inputs()
        self.assertEqual(released['step'], procedure.decide(clean, 12)['step'])

    def test_record_file_is_read_canonically(self):
        self.assertIsNone(kit.read_r1_planning_release(ROOT))  # none committed: no release is in force
        _, slots = planning_slots(['planning_turn_R_plus_0C'])
        record = release_for(slots, ['planning_turn_R_plus_0C'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / kit.R1_PLANNING_RELEASE
            path.parent.mkdir(parents=True)
            path.write_bytes(kit.raw_json(record))
            self.assertEqual(kit.read_r1_planning_release(tmp), record)
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'canonical'):
                kit.read_r1_planning_release(tmp)


if __name__ == '__main__':
    unittest.main()
