"""RL-84 smoke bars and selection, using synthetic cells and classifier inputs."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_followup_kit as kit
from tests.align.test_r1_round2 import classified
from tests.align.test_r1_inventory import step_capture, PREFILL_NS, LAST_DECODE_NS, R0_SENSORS

PHASES = ('pre_warmup_idle', 'quiet', 'load', 'recovery')


def cells(keys):
    spans = {name: (i * 2000 * rt.NS, (i * 2000 + 1000) * rt.NS)
             for i, name in enumerate(PHASES)}
    rows = [{'started': {'monotonic_ns': start + i * rt.NS},
             'finished': {'monotonic_ns': start + i * rt.NS},
             'values': {'sensors': dict.fromkeys(keys, 40.), 'errors': {}}}
            for start, _ in spans.values() for i in range(1000)]
    return spans, rows


class PerKeyCoverageTests(unittest.TestCase):
    def test_each_key_bar_rejects_only_that_key_in_every_phase(self):
        keys = ['TV0h', 'TV0m', 'Tf08']
        spans, rows = cells(keys)
        for phase, (start, end) in spans.items():
            for case in ('under_99_pct', 'one_pct_errors', 'adjacent_empty'):
                bad = deepcopy(rows)
                holes = ({50 + 40*i for i in range(20)} if case == 'under_99_pct' else
                         {50 + 80*i for i in range(10)} if case == 'one_pct_errors' else {500, 501})
                for row in bad:
                    stamp = row['started']['monotonic_ns']
                    if start <= stamp < end and (stamp-start)//rt.NS in holes:
                        row['values']['sensors']['TV0m'] = None
                        if case == 'one_pct_errors':
                            row['values']['errors']['TV0m'] = 'synthetic failure'
                report = kit.phase_coverage(bad, keys, spans)
                with self.subTest(phase=phase, case=case):
                    self.assertTrue(report['pass'], report)
                    self.assertTrue(all(s['pass'] for s in report['sampler'].values()))
                    self.assertFalse(report['phases'][phase]['TV0m']['pass'])
                    self.assertTrue(report['phases'][phase]['TV0h']['pass'])
                    self.assertTrue(report['phases'][phase]['Tf08']['pass'])

    def test_sweep_bar_fails_smoke_even_with_no_candidate_keys(self):
        spans, rows = cells([])
        for phase, (start, end) in spans.items():
            for holes in ({50 + 40*i for i in range(20)}, {500, 501}):
                bad = [r for r in rows if not (start <= r['started']['monotonic_ns'] < end
                       and (r['started']['monotonic_ns']-start)//rt.NS in holes)]
                report = kit.phase_coverage(bad, [], spans, required_keys=[])
                with self.subTest(phase=phase, holes=len(holes)):
                    self.assertFalse(report['sampler'][phase]['pass'])
                    self.assertFalse(report['pass'])

    def test_tf08_failure_or_absence_fails_smoke_with_healthy_sweeps(self):
        spans, rows = cells(['TV0h', 'Tf08'])
        for phase, (start, end) in spans.items():
            bad = deepcopy(rows)
            for row in bad:
                if start <= row['started']['monotonic_ns'] < end:
                    row['values']['errors']['Tf08'] = 'synthetic failure'
            report = kit.phase_coverage(bad, ['TV0h', 'Tf08'], spans)
            with self.subTest(phase=phase):
                self.assertTrue(all(s['pass'] for s in report['sampler'].values()))
                self.assertFalse(report['pass'])
        self.assertFalse(kit.phase_coverage(rows, ['TV0h'], spans)['pass'])

    def test_exact_99_pct_and_sub_one_pct_errors_are_admitted(self):
        spans, rows = cells(['Tf08'])
        holes = {50 + 80*i for i in range(10)}
        rows = [r for r in rows if (r['started']['monotonic_ns']//rt.NS) % 2000 not in holes]
        report = kit.phase_coverage(rows, ['Tf08'], spans)
        self.assertTrue(report['pass'], report)
        for phase in PHASES:
            self.assertEqual(report['sampler'][phase]['sample_fraction'], .99)
        spans, rows = cells(['Tf08'])
        for row in rows[:9]:
            row['values']['errors']['Tf08'] = 'synthetic failure'
        # Spread the errors so the consecutive-empty bar passes too.
        for i in range(9):
            rows[i]['values']['errors'].clear()
            rows[50 + 80*i]['values']['errors']['Tf08'] = 'synthetic failure'
        self.assertTrue(kit.phase_coverage(rows, ['Tf08'], spans)['pass'])


class SelectionAndTableTests(unittest.TestCase):
    def test_smoke_refuses_failed_bars_or_selection_after_saving_diagnostics(self):
        from joulewise.align.apple import thermal_gates
        for coverage_ok, selection_ok in ((False, True), (True, False)):
            with self.subTest(coverage_ok=coverage_ok), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / 'smoke'
                def invoke(runtime, kind, out, **kwargs):
                    if kind == 'capture-predecessor-30b':
                        return {'synthetic': True}
                    out.mkdir(parents=True)
                    (out / 'smoke_part_a.json').write_text('{}')
                    (out / rt.CUSTODY_NAME).write_text(json.dumps({
                        'files': {'runs/member/config.json': 'a'*64}}))
                    return {'bundle': 'runs/member'}
                table = {'coverage': {'pass': coverage_ok}, 'selection': {'ok': selection_ok}}
                runtime = ['synthetic', '--config', str(kit.ROOT / kit.r1.DEFAULT_RUNTIME_CONFIG)]
                with patch.object(kit.reg, 'verify_r1_executed_sources'), \
                        patch.object(thermal_gates, 'load_window_reference', return_value=({}, {})), \
                        patch.object(kit, 'smoke_table', return_value=table), \
                        self.assertRaisesRegex(ValueError, 'smoke Part B'):
                    kit.smoke(output, 'B', runtime, soak_reference='synthetic', invoke=invoke)
                self.assertEqual(json.loads((output / 'smoke_part_b.json').read_text()), table)
                self.assertEqual(json.loads((output / 'smoke.json').read_text())['part_b'], table)

    def test_prewarm_rejection_excludes_registered_and_fallback_roles(self):
        c = classified()
        original = deepcopy(c)
        keys = [r['key'] for r in c['ranking']]
        spans, rows = cells(keys + ['Tf08'])
        coverage = kit.phase_coverage(rows, keys + ['Tf08'], spans)
        self.assertTrue(kit.smoke_selection(c, coverage, keys)['ok'])
        for role in ('s_fast', 's_slow'):
            bad = deepcopy(coverage)
            bad['phases']['pre_warmup_idle'][c[role]]['pass'] = False
            self.assertFalse(kit.smoke_selection(c, bad, keys)['ok'])
        fallback = deepcopy(c)
        next(r for r in fallback['ranking'] if r['key'] == c['s_slow'])['class'] = 'die'
        fallback.update(s_slow=None, heatsink_candidates=[])
        self.assertTrue(kit.smoke_selection(fallback, coverage, keys)['fallback'])
        coverage['phases']['pre_warmup_idle'][original['s_slow']]['pass'] = False
        self.assertFalse(kit.smoke_selection(fallback, coverage, keys)['ok'])
        # The original classifier table is never rewritten to hide a rejection.
        self.assertEqual(c, original)

    def test_registered_classifier_rejects_bad_key_and_continues(self):
        inventory, rows = step_capture()
        candidate = R0_SENSORS['s_fast']
        for row in rows:
            row['values']['sensors']['Txtr'] = row['values']['sensors'][candidate] * .99
            if PREFILL_NS <= row['started']['monotonic_ns'] < LAST_DECODE_NS:
                row['values']['errors'][candidate] = 'synthetic failure'
        inventory['keys'].append({'key': 'Txtr', 'unit': 'degC', 'data_type': 'flt ', 'data_size': 4})
        c = rt.classify_step(inventory, rows, prefill_ns=PREFILL_NS, last_decode_ns=LAST_DECODE_NS,
                             r0_sensors=R0_SENSORS)
        rejected = next(r for r in c['ranking'] if r['key'] == candidate)
        self.assertIn('coverage', rejected['reason'])
        self.assertEqual(rejected['class'], 'record-only')
        self.assertEqual(c['s_fast'], 'Txtr')

    def test_smoke_table_lists_rejection_class_phase_reason_without_global_failure(self):
        c = classified()
        keys = [r['key'] for r in c['ranking'] if r['unit'] == 'degC'] + ['Tf08']
        spans, rows = cells(keys)
        # Ta0P is a non-selected, record-only synthetic key.
        rows[2500]['values']['errors']['Ta0P'] = 'synthetic failure'
        rows[2501]['values']['errors']['Ta0P'] = 'synthetic failure'
        c['phase_bounds_ns'] = {p: list(spans[p]) for p in PHASES[1:]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / kit.r1.DEFAULT_RUNTIME_CONFIG
            config_path.parent.mkdir(parents=True)
            config_path.write_text(json.dumps({'r0_classified_keys': keys,
                'r0_classes': {r['key']: r['class'] for r in c['ranking']}}))
            segment = root / 'segment'
            (segment / 'inventory').mkdir(parents=True)
            bundle = segment / 'member'
            bundle.mkdir()
            (bundle / 'events.jsonl').write_text(json.dumps({
                'event_type': 'stage_started', 'phase': 'idle_baseline', 'timestamp_s': 0}) + '\n')
            (segment / rt.RESULT_NAME).write_text(json.dumps({'bundle': 'member'}))
            saved = {'classification': c, 'inventory': {'keys': [
                {'key': key, 'unit': 'degC'} for key in keys]}}
            (segment / 'inventory/r1_classification.json').write_text(json.dumps(saved))
            (segment / 'inventory/inventory_journal.jsonl').write_text(
                ''.join(json.dumps(r) + '\n' for r in rows))
            journal = {'rows': [], 's_fast': c['s_fast'], 's_slow': c['s_slow'],
                       'g0': [{'start_ns': 0, 'end_ns': rt.NS}]}
            with patch.object(kit, 'ROOT', root), patch.object(kit.replay, 'read_journal', return_value=journal), \
                    patch.object(kit.replay, 'Session') as session, \
                    patch.object(kit.replay, 'warmup_anchor', return_value=1000*rt.NS), \
                    patch.object(kit.replay, 'candidate_replays', return_value=[]):
                session.return_value.mono_from_epoch.side_effect = lambda t: t
                table = kit.smoke_table(segment)
            self.assertEqual(table['status'], 'FOR_RESEARCH_LEAD_RULING')
            self.assertTrue(table['selection']['ok'])
            self.assertIn({'key': 'Ta0P', 'r0_class': 'record-only', 'phase': 'load',
                           'reason': 'two consecutive empty one-second cells'}, table['rejected_keys'])
            self.assertEqual(table['classification_table'], saved)


if __name__ == '__main__':
    unittest.main()
