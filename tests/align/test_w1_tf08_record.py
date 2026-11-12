"""RL-84 P-2: R0's heatsink is journalled, never promoted to a gate input.

Repository configs and synthetic clocks/readers only; no host or study data.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal
from scripts import align_v4_kit as kit, validate_align_v4_w1_plan as validator
from tests.align.test_thermal_gate import policy, session
from tests.align.test_v4_kit import filled_w1_plan, ready_inputs
from tests.hazards.fakes import FakeClocks
from tests.hazards.test_temperature import FakeSensors, POLICY as SIDECAR_POLICY
from joulewise.hazards.base import Context

ROOT = Path(__file__).resolve().parents[2]
# RL-94: R0's heatsink is read from r0_picks, not sensors.s_slow (an R1 pick since RL-89).
HEATSINK = json.loads((ROOT / 'configs/align/v4/r1_runtime.json').read_bytes())['r0_picks']['s_slow']


class W1RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs, cls.slots = ready_inputs()
        with patch.object(kit, 'read_inputs', return_value=cls.inputs), \
                patch.object(kit, 'read_r1_slots', return_value=cls.slots):
            cls.files = kit.build_files(ROOT)
        cls.plan = json.loads(cls.files[kit.KIT / 'collection_plan.json'])

    def check_ready(self, plan):
        # Exercise the actual PREQUAL/arm entry, isolating unrelated live gates.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / kit.KIT / 'collection_plan.json'
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(plan))
            registered = Path(tmp) / 'configs/align/v4/r1_runtime.json'
            registered.parent.mkdir(parents=True)
            registered.write_bytes((ROOT / 'configs/align/v4/r1_runtime.json').read_bytes())
            with patch.object(kit, 'read_inputs', return_value=self.inputs), \
                    patch.object(kit, 'read_r1_slots', return_value=self.slots), \
                    patch.object(kit, 'read_ruling_1f_receipt', return_value=None), \
                    patch.object(kit, 'pending_inputs', return_value=['WP11.test']), \
                    patch.object(kit, 'require_ready'), patch.object(kit, 'require_sizing'), \
                    patch.object(kit, 'validate_wp18_fixtures'), \
                    patch('joulewise.align.apple.v4_registration.require_registration'):
                kit.require_w1_ready(Path(tmp))

    def test_generated_policies_and_configs_record_registered_heatsink(self):
        self.assertEqual(HEATSINK, 'Tf08')  # registered R0 witness, not the R1 gate pick
        for member in self.plan['members']:
            with self.subTest(ordinal=member['ordinal']):
                spec = member['spec']
                config = json.loads(self.files[Path(member['config_path'])])
                self.assertEqual(json.loads(config['workload_profile']['prompt_text']), spec)
                if member['role'] == 'anchor':
                    self.assertNotIn('thermal', spec)
                    self.assertNotIn('record_keys', spec)
                else:
                    self.assertEqual(spec['thermal']['sensors'].get('record_keys'), [HEATSINK])
                    self.assertNotIn(HEATSINK, [spec['thermal']['sensors'][role]
                                               for role in ('s_fast', 's_slow')])
        self.check_ready(self.plan)

    def test_provisional_generator_also_carries_the_record_key(self):
        files = kit.build_files(ROOT)
        plan = json.loads(files[kit.KIT / 'collection_plan.json'])
        for member in plan['members'][4:]:
            self.assertEqual((member['spec']['thermal']['sensors'] or {}).get('record_keys'), [HEATSINK])

    def policy_with(self, config, inputs=None):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'configs/align/v4/r1_runtime.json'
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(config))
            return kit.thermal_policy(inputs or self.inputs, heavy=True, per_turn=True,
                                      window_reference={'role': 'capture'}, root=Path(tmp))

    def test_policy_derives_record_key_from_registered_r0_config(self):
        config = json.loads((ROOT / 'configs/align/v4/r1_runtime.json').read_bytes())
        config['r0_picks']['s_slow'] = 'Tsyn'
        config['sensors']['record_keys'] = ['Tsyn']
        result = self.policy_with(config)
        self.assertEqual(result['sensors']['record_keys'], ['Tsyn'])
        self.assertEqual(result['sensors']['s_slow'], self.inputs['R1']['thermal_policy']['sensors']['s_slow'])

    def test_rl94_record_key_is_r0_pick_not_runtime_s_slow(self):
        # RL-94: with the runtime's s_slow an R1 pick (Th0C), W1 records Tf08
        # and gates on the R1 picks; a changed s_slow alone moves nothing.
        config = json.loads((ROOT / 'configs/align/v4/r1_runtime.json').read_bytes())
        self.assertEqual((config['sensors']['s_fast'], config['sensors']['s_slow']), ('TV0h', 'Th0C'))
        self.assertEqual(config['r0_picks'], {'s_fast': 'TV0h', 's_slow': 'Tf08'})
        self.assertEqual(kit.r0_heatsink_key(ROOT), 'Tf08')
        inputs = deepcopy(self.inputs)
        inputs['R1']['thermal_policy']['sensors'].update(s_fast='TV0h', s_slow='Th0C')
        result = self.policy_with(config, inputs)
        self.assertEqual(result['sensors']['record_keys'], ['Tf08'])
        self.assertEqual((result['sensors']['s_fast'], result['sensors']['s_slow']), ('TV0h', 'Th0C'))
        config['sensors']['s_slow'] = 'Tsyn'
        self.assertEqual(self.policy_with(config, inputs)['sensors']['record_keys'], ['Tf08'])

    def test_r0_pick_must_be_named_and_recorded_by_the_runtime(self):
        config = json.loads((ROOT / 'configs/align/v4/r1_runtime.json').read_bytes())
        for mutate, message in ((lambda c: c.pop('r0_picks'), 'r0_picks.s_slow'),
                                (lambda c: c['r0_picks'].update(s_slow=None), 'r0_picks.s_slow'),
                                (lambda c: c['sensors'].update(record_keys=['Tbad']), 'not in .*record_keys')):
            candidate = deepcopy(config)
            mutate(candidate)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.policy_with(candidate)

    def test_readiness_refuses_missing_or_wrong_record_key_in_each_sidecar_member(self):
        for index in range(4, 18):
            for keys in (None, [], ['Tbad']):
                candidate = deepcopy(self.plan)
                sensors = candidate['members'][index]['spec']['thermal']['sensors']
                if keys is None:
                    sensors.pop('record_keys', None)
                else:
                    sensors['record_keys'] = keys
                with self.subTest(ordinal=index + 1, keys=keys), self.assertRaisesRegex(
                        ValueError, rf'member {index + 1}.*record_keys.*{HEATSINK}'):
                    self.check_ready(candidate)

    def test_readiness_refuses_sidecar_on_each_ungated_anchor(self):
        for index in range(4):
            candidate = deepcopy(self.plan)
            candidate['members'][index]['spec']['thermal'] = deepcopy(self.plan['members'][4]['spec']['thermal'])
            with self.subTest(ordinal=index + 1), self.assertRaisesRegex(
                    ValueError, rf'member {index + 1}.*ungated.*sidecar'):
                self.check_ready(candidate)

    def test_plan_validator_refuses_missing_wrong_and_ungated_sidecar(self):
        value = filled_w1_plan(self.inputs, self.slots, collection_plan=self.plan)
        self.assertEqual(validator.validate(value, self.inputs, self.slots,
                                           collection_plan=self.plan)['members'], 18)
        for mutation in ('missing', 'wrong', 'ungated'):
            candidate = deepcopy(self.plan)
            if mutation == 'ungated':
                candidate['members'][0]['spec']['thermal'] = deepcopy(candidate['members'][4]['spec']['thermal'])
                message = 'member 1.*ungated.*sidecar'
            else:
                sensors = candidate['members'][4]['spec']['thermal']['sensors']
                sensors.pop('record_keys', None)
                if mutation == 'wrong':
                    sensors['record_keys'] = ['Tbad']
                message = rf'member 5.*record_keys.*{HEATSINK}'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, message):
                validator.validate(value, self.inputs, self.slots, collection_plan=candidate)


class RecordOnlyTests(unittest.TestCase):
    def test_absent_record_keys_preserves_base_journal_bytes(self):
        name = 'joulewise/align/apple/thermal.py'
        raw = subprocess.run(['git', 'show', 'origin/ops/2026-11-11-w1-tf08-base:' + name],
                             cwd=ROOT, check=True, capture_output=True).stdout
        legacy = {'__name__': 'synthetic_legacy_thermal'}
        exec(compile(raw, '<synthetic legacy thermal>', 'exec'), legacy)
        journals = []
        with tempfile.TemporaryDirectory() as tmp:
            for index, sidecar_class in enumerate((legacy['Sidecar'], thermal.Sidecar)):
                sidecar = sidecar_class(Path(tmp) / str(index), SIDECAR_POLICY,
                                        reader=FakeSensors(), ctx=Context(clocks=FakeClocks(read_cost_ns=0)))
                sidecar.start(background=False)
                sidecar.tick()
                sidecar.stop()
                journals.append(sidecar.path.read_bytes())
        self.assertEqual(journals[0], journals[1])
        reading = json.loads(journals[1].splitlines()[1])['values']
        self.assertEqual(reading['errors'], {})
        self.assertEqual(reading['sensors'][SIDECAR_POLICY['s_fast']], 50.)

    def test_policy_validation_and_sampling_union(self):
        base = policy()['sensors']
        self.assertEqual(thermal.validate_policy(base), base)
        recorded = thermal.validate_policy({**base, 'record_keys': [HEATSINK, base['s_fast']]})
        self.assertEqual(thermal.keys(recorded), (*thermal.keys(base), HEATSINK))
        for keys in ([HEATSINK, HEATSINK], ['F0Ac'], 'Tf08', [None]):
            with self.subTest(keys=keys), self.assertRaisesRegex(ValueError, 'record_keys'):
                thermal.validate_policy({**base, 'record_keys': keys})

    def test_gate_module_bytes_are_unchanged(self):
        name = 'joulewise/align/apple/thermal_gates.py'
        base = subprocess.run(['git', 'show', 'origin/ops/2026-11-11-w1-tf08-base:' + name],
                              cwd=ROOT, check=True, capture_output=True).stdout
        self.assertEqual((ROOT / name).read_bytes(), base)

    def test_g0_g1_and_hold_decisions_ignore_record_only_heat_and_errors(self):
        results = []
        for recorded in (False, True):
            config = policy()
            if recorded:
                config['sensors']['record_keys'] = [HEATSINK]
            obj, clock = session(config=config)
            self.addCleanup(obj.close)
            # Same synthetic journal in each replay. The extra key is very hot
            # or unreadable: neither changes gate coverage or release decisions.
            read = obj.reader.read
            def readings(keys):
                result = read(keys)
                if recorded:
                    result['values'][HEATSINK] = 120. if int(clock.now()) % 2 else None
                    if result['values'][HEATSINK] is None:
                        result['errors'][HEATSINK] = 'synthetic missing key'
                return result
            with patch.object(obj.reader, 'read', side_effect=readings):
                decisions = []
                for hot in (False, True):
                    obj.reader._transport.values = lambda t, hot=hot: (45., 40.) if hot else (40., 40.)
                    for kind in (('G1', 'H') if hot else ('G0', 'G1', 'H')):
                        row = obj.wait(kind)
                        decisions.append({k: row[k] for k in (
                            'kind', 'outcome', 'duration_s', 'start_ns', 'end_ns',
                            'reference', 'release', 'slope_c_per_min')})
                results.append((decisions, list(obj.flags)))
        self.assertEqual(results[0], results[1])
        self.assertEqual(json.dumps(results[0], sort_keys=True), json.dumps(results[1], sort_keys=True))
        self.assertEqual([r['outcome'] for r in results[0][0]][:3], ['released'] * 3)
        self.assertIn('timeout', [r['outcome'] for r in results[0][0]])


if __name__ == '__main__':
    unittest.main()
