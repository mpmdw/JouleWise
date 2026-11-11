"""RL-78 and prepare wiring: synthetic clocks, records and model identities only."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt, thermal, v4_registration as reg
from scripts import align_r1_followup_kit as kit, align_r1_rehearsal as r1, align_r1_thermal_replay as replay
from tests.align.test_r1_inventory import step_capture, PREFILL_NS, LAST_DECODE_NS, R0_SENSORS
from tests.align.test_thermal_gate import session, policy
from tests.hazards.fakes import FakeClocks
from joulewise.hazards.base import Context


def classified():
    inventory, rows = step_capture()
    return rt.classify_step(inventory, rows, prefill_ns=PREFILL_NS, last_decode_ns=LAST_DECODE_NS,
                            r0_sensors=R0_SENSORS)


class SelectionTests(unittest.TestCase):
    def test_registered_pair_and_fallback_longest_return_without_tau_floor(self):
        c = classified()
        keys = [r['key'] for r in c['ranking']]
        self.assertEqual(rt.select_smoke_sensors(c, keys)['s_slow'], c['s_slow'])
        self.assertFalse(rt.select_smoke_sensors(c, keys)['fallback'])
        slow = next(r for r in c['ranking'] if r['key'] == c['s_slow'])
        slow.update(tau_s=55., t_band_s=299., **{'class': 'die'})
        c.update(s_slow=None, heatsink_candidates=[])
        pick = rt.select_smoke_sensors(c, keys)
        self.assertTrue(pick['ok'], pick)
        self.assertEqual(pick['s_slow'], slow['key'])
        self.assertTrue(pick['fallback'])
        self.assertEqual(pick['second_key_label'], 'near-die settling check')
        # No lower tau bound: the return time still decides.
        slow.update(tau_s=.5, t_band_s=2.)
        self.assertTrue(rt.select_smoke_sensors(c, keys)['ok'])

    def test_fallback_rejects_alias_noise_rise_return_clamp_unclassified_and_coverage(self):
        c = classified()
        keys = [r['key'] for r in c['ranking']]
        slow = next(r for r in c['ranking'] if r['key'] == c['s_slow'])
        c.update(s_slow=None, heatsink_candidates=[])
        for change in ({'noise': .151}, {'resolving': False}, {'t_band_s': 300.01},
                       {'clamped': True}, {'above_junction': True}, {'heat_ordering_excluded': True}):
            bad = deepcopy(c)
            next(r for r in bad['ranking'] if r['key'] == slow['key']).update(change)
            self.assertFalse(rt.select_smoke_sensors(bad, keys)['ok'], change)
        self.assertFalse(rt.select_smoke_sensors(c, [c['s_fast']])['ok'])
        c['alias_groups'] = [[c['s_fast'], slow['key']]]
        self.assertFalse(rt.select_smoke_sensors(c, keys)['ok'])

    def test_night_confirms_admissibility_and_never_reranks(self):
        c = classified()
        picks = {r: c[r] for r in ('s_fast', 's_slow')}
        keys = [r['key'] for r in c['ranking']]
        c.update(s_fast='Tnew', s_slow='Ttop')
        # Class-edge margins do not veto a fixed pick: only admissibility.
        next(r for r in c['ranking'] if r['key'] == picks['s_fast']).update(tau_s=61., t_band_s=200., **{'class': 'heatsink'})
        self.assertTrue(rt.sensor_admissibility(c, picks, keys)['ok'])
        next(r for r in c['ranking'] if r['key'] == picks['s_slow'])['t_band_s'] = 301
        self.assertFalse(rt.sensor_admissibility(c, picks, keys)['ok'])

    def test_prepare_requires_smoke_pair_coverage_ruling_and_default_band(self):
        c = classified()
        picks = {r: c[r] for r in ('s_fast', 's_slow')}
        config = {'sensors': {**picks, 'record_keys': ['Tf08']}, 'slow_band_floor_c': 1.,
                  'r0_classified_keys': [r['key'] for r in c['ranking']]}
        table = {'classification_table': {'classification': c}, 'coverage': {'pass': True}}
        table.update(r0_classified_keys=config['r0_classified_keys'], selection=rt.select_smoke_sensors(c, config['r0_classified_keys']))
        ruling = {'research_lead_ruling': 'SYNTHETIC', 'authorizes_night': True,
                  'sensors': config['sensors'], 'smoke_part_b_sha256': 'a'*64}
        self.assertTrue(kit.validate_sensor_ruling(config, ruling, 'a'*64, table)['ok'])
        for mutate in (lambda x: x['coverage'].update({'pass': False}),
                       lambda x: x['classification_table']['classification'].update(s_fast='Tbad')):
            bad = deepcopy(table); mutate(bad)
            with self.assertRaises(ValueError): kit.validate_sensor_ruling(config, ruling, 'a'*64, bad)
        config['slow_band_floor_c'] = 1.5
        with self.assertRaisesRegex(ValueError, 'default'): kit.validate_sensor_ruling(config, ruling, 'a'*64, table)

    def test_class_margins_are_disclosure_only(self):
        c = classified()
        before = deepcopy(c)
        margins = kit.class_edge_margins(c)
        self.assertTrue(all('tau_above_slow_edge_s' in r and 'return_time_below_300_s' in r for r in margins))
        self.assertEqual(c, before)


class RecordingTests(unittest.TestCase):
    class Reader:
        def read(self, keys): return {'values': {k: 40. for k in keys}, 'errors': {}}
        def close(self): pass

    def test_absent_field_matches_old_journal_bytes(self):
        old = ModuleType('joulewise.align.apple._old_thermal')
        exec(compile(subprocess.check_output(['git', 'show', 'a85ee8ec6:joulewise/align/apple/thermal.py'], cwd=r1.ROOT),
                     old.__name__, 'exec'), old.__dict__)
        config = {'s_fast': 'Tfak', 's_slow': 'Tslw', 'fan_keys': [], 'r0_sha256': 'a'*64}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            results = []
            for i, cls in enumerate((old.Sidecar, thermal.Sidecar)):
                clocks = FakeClocks(); clocks.read_cost_ns = 0
                obj = cls(path/str(i), config, reader=self.Reader(), ctx=Context(clocks=clocks))
                obj.start(background=False)
                for _ in range(3): obj.tick(); clocks.advance(1)
                obj.stop()
                results.append(obj.path.read_bytes())
            self.assertEqual(*results)

    def test_recorded_key_is_journalled_but_no_gate_reads_it(self):
        config = policy()
        config['sensors']['record_keys'] = ['Tf08']
        obj, clock = session(config=config)
        self.addCleanup(obj.close)
        original = obj.sidecar.tick
        class GateValues(dict):
            def get(self, key, *args):
                if key == 'Tf08': raise AssertionError('gate read record-only key')
                return super().get(key, *args)
            def __getitem__(self, key):
                if key == 'Tf08': raise AssertionError('gate read record-only key')
                return super().__getitem__(key)
        for row in obj.sidecar.readings:
            self.assertIn('Tf08', row['values']['sensors'])
            row['values']['sensors'] = GateValues(row['values']['sensors'])
        def tick():
            row = original()
            row['values']['sensors'] = GateValues(row['values']['sensors'])
            return row
        obj.sidecar.tick = tick
        for kind in ('G0', 'G1', 'H'):
            gate = obj.wait(kind)
            self.assertEqual(gate['outcome'], 'released', gate)

    def test_ordinary_predecessor_records_tf08_without_a_gate_or_template_edit(self):
        from tests.align import r1_synthetic as syn
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = syn.synthetic_config(root/"config")
            config, sha = rt.load_config(path)
            original = Path(config["templates"]["model_30b"]).read_bytes()
            backend = syn.SyntheticBackend(config)
            out = root/"segment"; out.mkdir()
            segment = rt.Segment(kind="capture-predecessor-30b", out=out, duration_s=None, soak=None,
                                 config=config, config_sha256=sha, backend=backend)
            try:
                fields = segment.k_capture_predecessor_30b()
                rows = [json.loads(line) for line in (out/fields["bundle"]/"outputs/align_thermal.jsonl").read_text().splitlines()]
                self.assertTrue(any(r["kind"] == "reading" and "Tf08" in r["values"]["sensors"] for r in rows))
                self.assertFalse(any(r["kind"] in ("align_thermal_gate", "align_thermal_hold") for r in rows))
                self.assertEqual(original, Path(config["templates"]["model_30b"]).read_bytes())
            finally:
                backend.close()

    def test_policy_refuses_non_temperature_duplicates_and_unknown_fields(self):
        p = policy()['sensors']
        for bad in (['F0Ac'], ['Tf08', 'Tf08'], [None], [dict()], 'Tf08'):
            with self.assertRaises(ValueError): thermal.validate_policy({**p, 'record_keys': bad})
        self.assertEqual(thermal.keys({**p, 'record_keys': ['Tslw', 'Tf08']}), ('Tfak', 'Tslw', 'Tf08'))
        self.assertIn('joulewise/align/apple/thermal.py', reg.R1_EXECUTED_SOURCES)


class DeskTests(unittest.TestCase):
    def test_each_start_tf08_excess_and_within_window_condition_comparison(self):
        from tests.test_align_r1_thermal_replay import journal_lines, T0, NS, WALL_OFFSET
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phases = []
            for name, temperature, condition in (("step_D_prefill_10k_decode_4096", 30., "benign"),
                                                  ("D_other", 32., "sabotage")):
                bundle = root/name/"runs/member"
                (bundle/"outputs").mkdir(parents=True)
                lines = journal_lines(lambda i: temperature, n=200)
                (bundle/"outputs/align_thermal.jsonl").write_text("".join(json.dumps(r)+"\n" for r in lines))
                (bundle/"events.jsonl").write_text(json.dumps({"event_type": "stage_started", "phase": "warmup",
                    "timestamp_s": (T0+100*NS+WALL_OFFSET)/NS})+"\n"+json.dumps({"event_type": "stage_started",
                    "phase": "measured_run", "timestamp_s": (T0+130*NS+WALL_OFFSET)/NS})+"\n")
                (bundle/"config.json").write_text(json.dumps({"workload_profile": {
                    "prompt_text": json.dumps({"condition": condition})}}))
                phases.append({"name": name, "result": {"bundle": "runs/member"}})
            (root/"r1_result.json").write_text(json.dumps({"phases": phases}))
            desk = replay.night_desk(root)
            self.assertEqual([r["Tf08_start_excess_c"] for r in desk["members"]], [0., 2.])
            self.assertEqual(desk["Tf08_disclosure"]["condition_comparisons"][0]["median_excess_a_minus_b_c"], -2.)
            (root/"r1_result.json").write_text(json.dumps({"phases": phases, "thermometry": {"D": {
                "night_confirmation": {"ok": False, "reasons": ["noise failed"]}}}}))
            with self.assertRaisesRegex(replay.Refused, "research lead"): replay.night_desk(root)

    def test_kit_admits_confirmed_slow_pick_without_reranking_or_heatsink_lower_tau_bar(self):
        from tests.align.test_v4_kit import ready_inputs
        from scripts import align_v4_kit as v4kit
        inputs, slots = ready_inputs()
        d = slots["thermometry"]["D"]
        d["heatsink_candidates"] = []
        with self.assertRaisesRegex(ValueError, "heatsink"): v4kit.require_ready(inputs, slots)
        d["night_confirmation"] = {"ok": True, "authority": "RL-78", "s_fast": d["s_fast"], "s_slow": d["s_slow"]}
        v4kit.require_ready(inputs, slots)
        d["night_confirmation"]["ok"] = False
        with self.assertRaisesRegex(ValueError, "heatsink"): v4kit.require_ready(inputs, slots)


class PrepareChecksTests(unittest.TestCase):
    def test_real_check_apis_project_all_members_to_three_registered_roots(self):
        config, _ = rt.load_config(r1.ROOT/r1.DEFAULT_RUNTIME_CONFIG)
        inventory = json.loads((r1.ROOT/reg.REGISTRATION/'model_artifact_inventory.json').read_text())['artifacts']
        identities = {r['root']: r for r in inventory.values()}
        pins = json.loads((r1.ROOT/reg.REGISTRATION/'identity_pins.json').read_text())
        seen = []
        def identity(root):
            # Strings only: never follow any registered absolute data path.
            seen.append(root); return identities[root]
        checks = kit.prepare_checks(r1.ROOT, config, identity_fn=identity,
                                     runtime_runner=lambda python: pins['runtime_versions'])
        self.assertTrue(checks['weight_digests']['ok'], checks)
        self.assertTrue(checks['runtime_stack']['ok'], checks)
        self.assertEqual(len(seen), 3)
        self.assertEqual(len(checks['registered_member_roots']), len(kit.MEMBER_ROOTS))
        changed = deepcopy(pins['runtime_versions']); changed['packages']['mlx'] = 'SYNTHETIC-MISMATCH'
        failed = kit.prepare_checks(r1.ROOT, config, identity_fn=identity, runtime_runner=lambda python: changed)
        self.assertFalse(failed['runtime_stack']['ok'])
        self.assertIn('differs: mlx', '; '.join(failed['runtime_stack']['reasons']))

    def test_missing_inventory_still_records_the_stack_result_without_reading_weights(self):
        config, _ = rt.load_config(r1.ROOT/r1.DEFAULT_RUNTIME_CONFIG)
        pins = json.loads((r1.ROOT/reg.REGISTRATION/"identity_pins.json").read_text())
        def read(path):
            if Path(path).name == "model_artifact_inventory.json":
                raise FileNotFoundError("synthetic missing inventory")
            return pins
        with patch.object(kit.v4_session, "weight_digest_preflight") as weights:
            result = kit.prepare_checks(r1.ROOT, config, reader=read,
                runtime_runner=lambda python: pins["runtime_versions"])
            weights.assert_not_called()
        self.assertFalse(result["weight_digests"]["ok"])
        self.assertTrue(result["runtime_stack"]["ok"])
        self.assertIn("unavailable", result["weight_digests"]["reasons"][0])

    def test_both_refusals_recorded_and_joined_before_identity_or_dwell(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'refused.json'
            with patch.object(reg, 'verify_r1_executed_sources') as identity:
                with self.assertRaisesRegex(ValueError, 'weight-failed; stack-failed'):
                    kit.prepare(out,
                        weight_digest_check=lambda *a, **kw: {'ok': False, 'reasons': ['weight-failed']},
                        runtime_stack_check=lambda *a, **kw: {'ok': False, 'reasons': ['stack-failed']})
                identity.assert_not_called()
            record = json.loads(out.read_text())
            self.assertFalse(record['weight_digests']['ok'])
            self.assertFalse(record['runtime_stack']['ok'])


if __name__ == '__main__': unittest.main()
