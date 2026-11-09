"""R23c release-contract hand witnesses; all inputs are synthetic."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.v4_analysis import analyze, engine as e
from joulewise.align.v4_analysis import io as reader
from joulewise.align.v4_analysis.io import canonical, digest, load
from joulewise.align.v4_analysis.synthetic import series
from tests.align.test_v4_r23_engine import w1_window


def native_payload():
    p = series(turns=4)
    p['windows'].insert(0, w1_window(p))
    for w in p['windows']:
        for m in w['members']:
            if m['slot']['series_role'] == 'anchor':
                run = w['window']+':'+m['slot']['run_id']
                m['slot']['run_id'] = m['thermal']['id'] = run
    p['synthetic'] = False
    p['series_manifest'] = r24_manifest(p)
    return p


def r24_manifest(p):
    """R23j: the full frozen R24 allocation (W1, C1-C14, T1-T3), anchors prefixed."""
    from joulewise.align.v4_analysis.synthetic import release_manifest
    return release_manifest(p['windows'])


def write_export(root, payload):
    """One source-bound export, including W1; no capture or model files."""
    p = copy.deepcopy(payload)
    def write(name, value):
        data = canonical(value)
        (root/name).write_bytes(data)
        return dict(path=name, sha256=digest(data))
    p['series_source'] = write('series.json', p.pop('series_manifest'))
    for w in p['windows']:
        # R23j: every captured C window carries its committed terminal result.
        if w['window'].startswith('C') and 'terminal_result_source' not in w:
            w['terminal_result_source'] = write(w['attempt_id'].replace('#', '_')+'-terminal.json',
                w.pop('terminal_result', dict(verdict='GO', chain_exit_code=0)))
        members = w.pop('members')
        rows = [{**m['thermal'], 'run_id': m['slot']['run_id'],
                 'summary': m['summary'], 'captured': m['captured'],
                 'exclusion_codes': m.get('source_flags', [])} for m in members]
        # Attempt-named, so a zero-capture attempt and its retry never collide.
        source = write(w.get('attempt_id', w['window']).replace('#', '_')+'.json', dict(members=rows))
        w.update(roster=[m['slot'] for m in members], thermal_source=source, residual_source=source)
    path = root/'input.json'
    path.write_bytes(canonical(p))
    return path


class W1ContractTests(unittest.TestCase):
    def test_selection_only_refused_in_api_loader_and_cli_before_sources(self):
        from scripts.analyze_align_v4 import main
        for key in ('selection_desk', 'selection_source'):
            for anchors in (False, True):
                with self.subTest(key=key, full_anchor_evidence=anchors):
                    p = series(turns=4)
                    w1 = w1_window(p)
                    selection = dict(members=[m['thermal'] for m in w1['members']])
                    if anchors:
                        selection['anchor_members'] = w1['members'][:4]
                    p[key] = selection if key == 'selection_desk' else dict(
                        path='must-not-open.json', sha256='0'*64)
                    with self.assertRaisesRegex(ValueError, 'selection-only W1'):
                        analyze(p)
                    with tempfile.TemporaryDirectory() as tmp:
                        root = Path(tmp)
                        path = root/'input.json'
                        path.write_bytes(canonical(p))
                        with patch.object(reader, 'read_source', side_effect=AssertionError('source opened')):
                            with self.assertRaisesRegex(ValueError, 'selection-only W1'):
                                load(path)
                            with contextlib.redirect_stdout(io.StringIO()):
                                rc = main(['--input', str(path), '--output', str(root/'out'),
                                           '--workers', '1', '--calibration-only'])
                        self.assertEqual(rc, 2)
                        detail = reader.strict_json((root/'out'/'refusal-detail.json').read_bytes())
                        self.assertIn('selection-only W1', detail['detail'])

    def test_window_is_the_only_w1_evidence_even_with_legacy_snapshot(self):
        p = series(turns=4)
        p['windows'].insert(0, w1_window(p))
        expected = analyze(p)
        p['selection_desk'] = dict(members=[], anchor_members=[])
        self.assertEqual(tuple(map(canonical, analyze(p))), tuple(map(canonical, expected)))

    def test_w1_anchor_block_discloses_inclusion_exclusion_and_absence(self):
        p = series(turns=4)
        p['windows'].insert(0, w1_window(p))
        good, _ = analyze(p)
        self.assertEqual((good['anchor_sigma_w']['K'], good['anchor_sigma_w']['W1_anchor_block']),
                         (12, 'included'))
        for flag, expected in (('runtime.oom', 'X6'), ('battery.member_span', 'B'),
                               ('wrong_seed', 'seed_identity_differs'), ('recorded_X3', 'X3')):
            with self.subTest(flag=flag):
                q = copy.deepcopy(p)
                m = q['windows'][0]['members'][0]
                if flag == 'wrong_seed':
                    m['summary']['seed'] += 1
                elif flag == 'recorded_X3':
                    m['source_flags'] = ['X3']
                elif flag.startswith('battery.'):
                    m['thermal']['battery']['flags'].append(flag)
                else:
                    m['thermal']['flags'].append(flag)
                fill, _ = analyze(q)
                self.assertEqual(fill['anchor_sigma_w']['K'], 11)
                self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'excluded:'+expected)
        p['windows'][0]['members'].pop(0)
        fill, _ = analyze(p)
        self.assertEqual(fill['anchor_sigma_w']['K'], 11)
        self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'unavailable:four W1 anchors required')
        p['windows'].pop(0)
        fill, _ = analyze(p)
        self.assertEqual(fill['anchor_sigma_w']['K'], 11)
        self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'unavailable:W1 window unavailable')

    def test_w1_checks_and_contrast_receive_screened_thermal_fields(self):
        p = series(turns=4)
        w1 = w1_window(p)
        p['windows'].insert(0, w1)
        replay = w1['members'][4]
        replay['source_flags'] = ['X3']
        replay['thermal'].update(g0_slow_c=99., template='X', arm='S')
        # X3 comes only from the full member screen, not the thermal snapshot.
        with patch.object(e.td, 'deciding_experiment', wraps=e.td.deciding_experiment) as contrast:
            fill, _ = analyze(p)
        checks = fill['W1']['checks'][e.D_MODEL]
        self.assertEqual(checks['U1']['thermal_excluded_members'], 1)
        self.assertEqual(checks['U2']['g0_slow_range_c'], 0.)
        self.assertEqual(checks['U3']['pairs'][0]['reason'], 'ineligible replay member')
        row = contrast.call_args.args[0][0]
        self.assertEqual(row['analysis_classes'], ['X3'])
        self.assertTrue(row['analysis_ineligible'])
        self.assertTrue(row['captured'])
        self.assertEqual(row['turn_counts'], replay['thermal']['turn_counts'])
        self.assertNotIn('analysis_classes', replay['thermal'])  # input remains immutable

    def test_single_export_cli_roundtrip_keeps_w1_on_full_run(self):
        from scripts.analyze_align_v4 import main
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = native_payload()
            p['selection_desk'] = dict(members=[])  # ignored in favor of W1 window
            path = write_export(root, p)
            # Exercise the legacy reference field too: it must not break the
            # CLI's internal T-only load after W1 was verified with C.
            document = reader.strict_json(path.read_bytes())
            data = canonical(dict(members=[]))
            (root/'selection.json').write_bytes(data)
            document['selection_source'] = dict(path='selection.json', sha256=digest(data))
            path.write_bytes(canonical(document))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['--input', str(path), '--output', str(root/'cal'),
                    '--workers', '1', '--calibration-only']), 0)
                self.assertEqual(main(['--input', str(path), '--output', str(root/'full'),
                    '--workers', '1', '--thresholds', str(root/'cal'/'thresholds.json')]), 0)
            for output in ('cal', 'full'):
                fill = reader.strict_json((root/output/'fill.json').read_bytes())
                self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'included')
                self.assertEqual(fill['W1']['status'], 'computed')
            self.assertEqual((root/'cal'/'thresholds.json').read_bytes(),
                             (root/'full'/'thresholds.json').read_bytes())


class StrictAnchorTests(unittest.TestCase):
    def test_raw_adapter_refuses_invalid_ids_before_member_reads(self):
        from joulewise.align.v4_analysis import raw
        for target in ('roster', 'source'):
            for fault in ('bare', 'mixed', 'wrong_prefix', 'non_anchor'):
                with self.subTest(target=target, fault=fault):
                    slots = e.roster('C1')
                    for slot in slots[:4]:
                        slot['run_id'] = 'C1:'+slot['run_id']
                    sources = [dict(run_id=s['run_id'], captured=False) for s in slots]
                    rows = slots if target == 'roster' else sources
                    if fault in ('bare', 'mixed'):
                        for row in rows[:4 if fault == 'bare' else 1]:
                            row['run_id'] = row['run_id'].split(':', 1)[1]
                    elif fault == 'wrong_prefix':
                        rows[0]['run_id'] = rows[0]['run_id'].replace('C1:', 'C2:')
                    else:
                        rows[4]['run_id'] = 'C1:'+rows[4]['run_id']
                    with patch.object(raw, 'member', side_effect=AssertionError('member read')):
                        with self.assertRaises(ValueError):
                            raw.window(Path.cwd(), dict(members=sources), slots, window_id='C1')

    def test_native_manifest_and_observations_require_every_anchor_prefix(self):
        for target in ('manifest', 'observation'):
            for window in ('W1', 'C1'):
                for count in (1, 4):  # mixed IDs, then wholly bare IDs
                    with self.subTest(target=target, window=window, bare_count=count):
                        p = native_payload()
                        w = next(w for w in p['windows'] if w['window'] == window)
                        if target == 'manifest':
                            slots = next(w['members'] for w in p['series_manifest']['windows']
                                         if w['window'] == window)
                        else:
                            slots = [m['slot'] for m in w['members']]
                        for slot in slots[:count]:
                            slot['run_id'] = slot['run_id'].split(':', 1)[1]
                        with self.assertRaisesRegex(ValueError, 'anchor run_id requires window prefix'):
                            analyze(p)

    def test_wrong_prefix_and_prefixed_non_anchor_still_refuse(self):
        for target in ('manifest', 'observation'):
            for window in ('W1', 'C1'):
                for ordinal in (1, 5):
                    with self.subTest(target=target, window=window, ordinal=ordinal):
                        p = native_payload()
                        w = next(w for w in p['windows'] if w['window'] == window)
                        slots = (next(w['members'] for w in p['series_manifest']['windows']
                                      if w['window'] == window) if target == 'manifest' else
                                 [m['slot'] for m in w['members']])
                        slot = slots[ordinal-1]
                        slot['run_id'] = ('T9:'+slot['run_id'].split(':', 1)[-1] if ordinal == 1
                                          else window+':'+slot['run_id'])
                        with self.assertRaisesRegex(ValueError, 'window prefix'):
                            analyze(p)

    def test_release_loader_requires_prefix_even_when_marked_synthetic(self):
        for bare_count in (1, 4):
            for target in ('manifest', 'observation'):
                with self.subTest(bare_count=bare_count, target=target):
                    p = native_payload()
                    p['synthetic'] = True
                    if target == 'manifest':
                        slots = p['series_manifest']['windows'][0]['members']
                    else:
                        slots = [m['slot'] for m in p['windows'][0]['members']]
                    for slot in slots[:bare_count]:
                        slot['run_id'] = slot['run_id'].split(':', 1)[1]
                    with tempfile.TemporaryDirectory() as tmp:
                        path = write_export(Path(tmp), p)
                        with self.assertRaisesRegex(ValueError, 'anchor run_id requires window prefix'):
                            load(path)


if __name__ == '__main__':
    unittest.main()
