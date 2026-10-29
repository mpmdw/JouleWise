"""Synthetic production-harvest checks for exclusion-only thermal alternatives."""
from __future__ import annotations

import contextlib
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import bytes_thermal_lines as t
from tests.b6 import test_bytes_p2_thermal_window as fixtures
from tests import test_harvest_b5_window as w
from joulewise import bytes_analysis as ba


def setUpModule():
    fixtures.setUpModule()


def tearDownModule():
    fixtures.tearDownModule()


class ThermalLinesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.builder = fixtures.HarvestEntryTests()
        self.builder.root = self.root

    def harvest(self, pass_id=2, name='window', *, clean=False, inside=False):
        factory = w.Window
        # Use the shared fixture's documented isolation catalog for its absent
        # campaign cooldown log. Every thermal/battery exclusion stays real.
        with patch.object(w, 'Window', side_effect=lambda *a, **kw: factory(
                *a, catalog_overrides=w.WindowTestCase.ISOLATE, **kw)):
            window = self.builder.window(pass_id, name=name)
        if clean or inside:
            path = window.custody / 'hazards/monitor/thermal.jsonl'
            rows = [json.loads(s) for s in path.read_text().splitlines()]
            for row in rows:
                row['values']['level'] = 0
            if inside:
                # Request-end bracketing includes the first read after request.
                start, end = w.request_span_ns(w.MEMBERS[0][0])
                first = next(row for row in rows if row['finished']['monotonic_ns'] >= end)
                first['values']['level'] = 1
            path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
        self.builder.harvest(window)
        # This shared fixture runs the B5 harvest entry; materialize the B6
        # member-exclusion wire shape from its production exclusion decision.
        exclusions = window.exclusions()['members_excluded']
        acceptance = {'session_id': w.SESSION_ID, 'counting': True,
                      'excluding': [{'scope': 'member', 'run_id': m['run_id'], 'code': code}
                                    for m in exclusions for code in m['codes']]}
        (window.archive / 'derived/b6-acceptance.json').write_text(json.dumps(acceptance))
        return window.archive

    def codes(self, archive):
        rows = json.loads((archive / 'derived/b6-acceptance.json').read_bytes())['excluding']
        result = {}
        for row in rows:
            if row.get('scope') == 'member':
                result.setdefault(row['run_id'], set()).add(row['code'])
        return result

    def export(self, archive):
        """Opaque-column CSV stressing quoting, embedded newlines and CRLF."""
        raw = (archive / 'derived/b6-acceptance.json').read_text()
        session = t.selected(raw, 'session_id')
        target = self.root / ('export-' + archive.parent.name)
        target.mkdir(exist_ok=True)
        path = target / (session + '.runs.csv')
        roster = json.loads((archive / 'derived/roster.json').read_bytes())['members']
        codes = self.codes(archive)
        with path.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['run_id', 'exclusion_codes', 'phase_decode_j', 'idle_power_w', 'dur_decode_s', 'rail'])
            for m in roster:
                writer.writerow([m['run_id'], ';'.join(sorted(codes.get(m['run_id'], set()))),
                                 '987654321.123456', '876543210.234567', '765432109.345678', 'opaque,"\n654321098.456789'])
        return target, path

    def assert_only_excluding(self, source, output):
        a = (source / 'derived/b6-acceptance.json').read_bytes().decode()
        b = (output / 'derived/b6-acceptance.json').read_bytes().decode()
        x, y = t.field_span(a, ('excluding',))
        u, v = t.field_span(b, ('excluding',))
        self.assertEqual(a[:x], b[:u])
        self.assertEqual(a[y:], b[v:])
        for path in source.rglob('*'):
            if path.is_file() and path.relative_to(source).as_posix() not in ('derived/b6-acceptance.json', 'thermal_line.json'):
                self.assertEqual(path.read_bytes(), (output / path.relative_to(source)).read_bytes())

    def test_pass2_hull_csv_bytes_blinding_idempotence_and_source_safety(self):
        source = self.harvest()
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
        export, csv_path = self.export(source)
        out = self.root / 'hull'
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            t.main(['hull-p2', str(source), str(out), '--export', str(export)])
        record = json.loads(capture.getvalue())
        science = {m[0] for m in w.MEMBERS}
        self.assertEqual({c['run_id'] for c in record['changes']}, science)
        self.assertTrue(all(c['action'] == 'added' for c in record['changes']))
        self.assertTrue(any(set(runs) == set(w.QUAD) for runs in record['dropped_units']))
        self.assert_only_excluding(source, out)
        a = csv_path.read_bytes().decode()
        b = (out / 'export' / csv_path.name).read_bytes().decode()
        ar, br = t.csv_fields(a), t.csv_fields(b)
        for old, new in zip(ar, br):
            for index in (0, 2, 3, 4, 5):
                self.assertEqual(a[slice(*old[index])], b[slice(*new[index])])
        for sentinel in ('987654321.123456', '876543210.234567', '765432109.345678', '654321098.456789'):
            self.assertNotIn(sentinel, capture.getvalue())
            self.assertEqual(a.count(sentinel), b.count(sentinel))
        again = self.root / 'again'
        repeated = t.transform('hull-p2', out, again, out / 'export')
        self.assertEqual(repeated['changes'], [])
        self.assertEqual((out / 'derived/b6-acceptance.json').read_bytes(), (again / 'derived/b6-acceptance.json').read_bytes())
        archive_only = t.transform('hull-p2', source, self.root / 'no-csv')
        self.assertEqual(record['changes'], archive_only['changes'])
        for dest in (source, source / 'new', source.parent):
            with self.assertRaisesRegex(ValueError, 'overlaps'):
                t.transform('hull-p2', source, dest)
        self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()})

    def test_pass1_restores_tail_but_preserves_battery_and_inside(self):
        source = self.harvest(1)
        path = source / 'derived/b6-acceptance.json'
        data = json.loads(path.read_bytes())
        battery_run = w.MEMBERS[1][0]
        data['excluding'].append({'scope': 'member', 'run_id': battery_run, 'code': 'battery.member_span'})
        path.write_text(json.dumps(data))
        export, _ = self.export(source)
        out = self.root / 'request'
        record = t.transform('request-end-p1', source, out, export)
        self.assertEqual({c['run_id'] for c in record['changes']}, {r[0] for r in w.MEMBERS})
        self.assertEqual(self.codes(out)[battery_run], {'battery.member_span'})
        self.assertNotIn(battery_run, record['restored_members'])
        self.assertTrue(record['restored_units'])
        self.assertTrue(record['dropped_units'])
        self.assert_only_excluding(source, out)
        archive_record = t.transform('request-end-p1', source, self.root / 'archive-only')
        self.assertEqual(record['changes'], archive_record['changes'])
        second = t.transform('request-end-p1', out, self.root / 'second')
        self.assertEqual(second['changes'], [])
        inside = self.harvest(1, 'inside', inside=True)
        result = t.transform('request-end-p1', inside, self.root / 'inside-out')
        self.assertNotIn(w.MEMBERS[0][0], [c['run_id'] for c in result['changes']])
        self.assertIn(w.MEMBERS[0][0], [c['run_id'] for c in result['dropped_members']])

    def test_clean_pass1_equals_registered_and_no_request_keeps_hull(self):
        clean = self.harvest(1, clean=True)
        out = self.root / 'clean'
        record = t.transform('request-end-p1', clean, out)
        self.assertTrue(record['equals_registered_line'])
        self.assertEqual((clean / 'derived/b6-acceptance.json').read_bytes(), (out / 'derived/b6-acceptance.json').read_bytes())
        source = self.harvest(1, 'no-request')
        path = source / 'withheld/spans.json'
        data = json.loads(path.read_bytes())
        run = w.MEMBERS[0][0]
        data['spans'][run]['request'] = None
        path.write_text(json.dumps(data))
        record = t.transform('request-end-p1', source, self.root / 'no-request-out')
        self.assertNotIn(run, [c['run_id'] for c in record['changes']])
        self.assertIn({'run_id': run, 'code': 'request_span.absent_keep_hull'}, record['notices'])

    def test_null_unavailable_and_reference_are_reported_unchanged(self):
        source = self.harvest()
        path = source / 'withheld/member-assessments.json'
        data = json.loads(path.read_bytes())
        null, missing, reference = [m[0] for m in w.MEMBERS[:3]]
        data['members'][null][t.FIELD]['excluded'] = None
        data['members'][missing][t.FIELD]['journal_available'] = False
        path.write_text(json.dumps(data))
        path = source / 'derived/roster.json'
        roster = json.loads(path.read_bytes())
        next(m for m in roster['members'] if m['run_id'] == reference)['kind'] = 'external_input'
        path.write_text(json.dumps(roster))
        record = t.transform('hull-p2', source, self.root / 'special')
        self.assertTrue({null, missing, reference}.isdisjoint(c['run_id'] for c in record['changes']))
        self.assertIn({'run_id': null, 'code': 'member.span_unknown'}, record['notices'])
        self.assertIn({'run_id': missing, 'code': 'thermal.unmeasured'}, record['notices'])
        self.assertIn({'run_id': reference, 'code': 'reference.unchanged'}, record['notices'])

    def test_monotonicity_violation_stops_before_write(self):
        source = self.harvest(1, inside=True)
        path = source / 'derived/b6-acceptance.json'
        data = json.loads(path.read_bytes())
        run = w.MEMBERS[0][0]
        data['excluding'] = [r for r in data['excluding'] if not (r.get('run_id') == run and r['code'] == t.CODE)]
        path.write_text(json.dumps(data))
        out = self.root / 'forbidden'
        with self.assertRaisesRegex(ValueError, run):
            t.transform('request-end-p1', source, out)
        self.assertFalse(out.exists())

    def test_json_measurement_lexemes_are_never_decoded(self):
        source = self.root / 'opaque'
        (source / 'derived').mkdir(parents=True)
        (source / 'withheld').mkdir()
        sentinel = '987654321.123456'
        (source / 'derived/b6-acceptance.json').write_text(
            '{"energy":' + sentinel + ',"excluding":[],"session_id":"opaque"}')
        (source / 'derived/roster.json').write_text(json.dumps(
            {'members': [{'run_id': 'science', 'kind': 'science', 'units': []}]}))
        (source / 'withheld/member-assessments.json').write_text(
            '{"members":{"science":{"energy":' + sentinel + ',"' + t.FIELD +
            '":{"excluded":true,"journal_available":true}}}}')
        loads = json.loads
        def guarded(raw, *a, **kw):
            self.assertNotIn(sentinel, raw)
            return loads(raw, *a, **kw)
        with patch.object(t.json, 'loads', side_effect=guarded):
            record = t.transform('hull-p2', source, self.root / 'opaque-out')
        self.assertNotIn(sentinel, json.dumps(record))
        self.assertIn(sentinel.encode(), (self.root / 'opaque-out/derived/b6-acceptance.json').read_bytes())

    def test_analysis_binding_unchanged(self):
        self.assertEqual(hashlib.sha256(Path(ba.__file__).read_bytes()).hexdigest(),
                         '18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71')



class BoundAnalysisReplayTests(unittest.TestCase):
    """Full 50-run modules use the existing production BYTES export fixture.

    Harvest-window tests above exercise the real session harvester separately;
    this fixture exercises released-key archive ingress and blinded CSV ingress.
    """
    def test_original_and_transformed_inputs_run_unchanged_analysis(self):
        from tests.test_bytes_analysis import archive_campaign
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = archive_campaign(root)
            for session in manifest['sessions']:
                source = Path(session['archive'])
                roster_path = source / 'derived/roster.json'
                roster = json.loads(roster_path.read_bytes())
                science = [m for m in roster['members'] if m['role'] == 'science']
                for m in roster['members']:
                    m['kind'] = 'science' if m['role'] == 'science' else 'external_input'
                roster_path.write_text(json.dumps(roster))
                model = manifest['models'][0]
                target = next(m for m in science if m['units'][0]['cell_id'] in model['cell_ids'] and m['units'][0]['stratum'] == 'quad')
                run = target['run_id']
                acceptance_path = source / 'derived/b6-acceptance.json'
                acceptance = json.loads(acceptance_path.read_bytes())
                mode = 'hull-p2' if session['pass_id'] == 2 else 'request-end-p1'
                if session['pass_id'] == 2:
                    values = {m['run_id']: {t.FIELD: {'excluded': m is target, 'journal_available': True,
                              'samples': [], 'span_monotonic_ns': [20 * fixtures.NS, 110 * fixtures.NS]}} for m in science}
                    (source / 'withheld/member-assessments.json').write_text(json.dumps({'members': values}))
                else:
                    acceptance['excluding'].append({'scope': 'member', 'run_id': run, 'code': t.CODE})
                    acceptance_path.write_text(json.dumps(acceptance))
                    spans = {m['run_id']: {'member': None, 'request': None} for m in science}
                    spans[run] = {'member': [20 * fixtures.NS, 110 * fixtures.NS], 'request': [40 * fixtures.NS, 80 * fixtures.NS]}
                    (source / 'withheld/spans.json').write_text(json.dumps({'spans': spans}))
                    (source / 'derived/harvest-thresholds.json').write_text(json.dumps({'values': w.REGISTERED_HARVEST_THRESHOLDS}))
                    journal = source / 'sources/night-custody/hazards/monitor/thermal.jsonl'
                    journal.parent.mkdir(parents=True, exist_ok=True)
                    fixtures.thermal_journal(range(0, 126, 5), {90}).dump(journal)
                csv_path = root / 'export/bytes' / (session['session_id'] + '.runs.csv')
                if session['pass_id'] == 1:
                    with csv_path.open(newline='') as stream:
                        reader = csv.DictReader(stream)
                        fields, rows = reader.fieldnames, list(reader)
                    for row in rows:
                        if row['run_id'] == run:
                            row['exclusion_codes'] = t.CODE
                    with csv_path.open('w', newline='') as stream:
                        writer = csv.DictWriter(stream, fields)
                        writer.writeheader()
                        writer.writerows(rows)
                out = root / ('line-' + str(session['pass_id']))
                record = t.transform(mode, source, out, csv_path.parent)
                self.assertEqual([c['run_id'] for c in record['changes']], [run])
                local = copy.deepcopy(manifest)
                local['sessions'] = [copy.deepcopy(session)]
                local['sessions'][0]['released_key_dir'] = str((source / session['released_key_dir']).resolve())
                original = ba.load_records(source, local, stage='all')
                changed = ba.load_records(out, local, stage='all')
                original_cells = ba.reduce_models(original, local, boundaries=('rails',))
                changed_cells = ba.reduce_models(changed, local, boundaries=('rails',))
                old = next(c for c in original_cells if c['model'] == model['model'])
                new = next(c for c in changed_cells if c['model'] == model['model'])
                self.assertEqual((old['status'], new['status']), ('computed', 'computed'))
                self.assertEqual((old['n_b'], new['n_b']), (10, 9) if session['pass_id'] == 2 else (9, 10))
                quad = {m['run_id'] for m in science if m['units'] == target['units']}
                removed = new['removed_runs'] if session['pass_id'] == 2 else old['removed_runs']
                self.assertEqual(set(removed), quad)
                # A one-session export directory avoids loading the other pass.
                original_export = root / ('original-export-' + str(session['pass_id']))
                original_export.mkdir()
                (original_export / csv_path.name).symlink_to(csv_path)
                for path in (original_export, out / 'export'):
                    records = ba.load_records(path, local, stage='blinded')
                    cells = ba.reduce_models(records, local, boundaries=('rails',))
                    self.assertEqual(next(c for c in cells if c['model'] == model['model'])['n_b'],
                                     old['n_b'] if path == original_export else new['n_b'])


if __name__ == '__main__':
    unittest.main()
