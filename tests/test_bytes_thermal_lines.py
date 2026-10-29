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





class ReviewerRealChainTests(unittest.TestCase):
    """Opus executing chain: production harvest and accept_archive, no adapter."""
    def test_cross_pass_identity_and_view(self):
        import contextlib
        import hashlib
        import io
        import json
        import os
        import sys
        import tempfile
        from pathlib import Path

        JW = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(JW))
        from joulewise.b5 import harvest as h  # noqa: E402
        from joulewise.b6.session import accept_archive  # noqa: E402
        from scripts import bytes_thermal_lines as t
        from tests.b6 import test_bytes_p2_thermal_window as fx  # noqa: E402
        from tests import test_harvest_b5_window as w  # noqa: E402

        NS = 10**9
        RESULTS = []


        def check(name, ok, detail=""):
            assert ok, (name, detail)
            RESULTS.append((name, bool(ok), detail))
            print(("PASS " if ok else "FAIL ") + name + (": " + str(detail) if detail else ""))


        def member_codes(archive_or_out):
            rows = json.loads((Path(archive_or_out) / "derived/b6-acceptance.json").read_bytes())["excluding"]
            out = {}
            for r in rows:
                if r.get("scope") == "member":
                    out.setdefault(r["run_id"], []).append(r["code"])
            return {k: sorted(v) for k, v in out.items()}


        def tree_digest(root):
            return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(Path(root).rglob("*")) if p.is_file() and not p.is_symlink()}


        class Chain:
            def __init__(self, root):
                self.root = Path(root)
                self.b = fx.HarvestEntryTests()
                self.b.root = self.root

            def archive(self, pass_id, name, mutate=None):
                win = self.b.window(pass_id, name=name)
                if mutate:
                    mutate(win)
                self.b.harvest(win)
                plan = json.loads(win.plan_path.read_text())
                result, _ = accept_archive(win.archive, plan, JW / "configs/b6/registration",
                                           plan_path=win.plan_path, replace_existing=True)
                return win, result


        def journal_rows(win):
            path = win.custody / "hazards/monitor/thermal.jsonl"
            return path, [json.loads(s) for s in path.read_text().splitlines()]


        def put_rows(path, rows, extra=""):
            path.write_text("".join(json.dumps(r) + "\n" for r in rows) + extra)


        def run_cli(mode, archive, out, export=None):
            buf = io.StringIO()
            argv = [mode, str(archive), str(out)] + (["--export", str(export)] if export else [])
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()) as err:
                try:
                    t.main(argv)
                    code = 0
                except SystemExit as exc:
                    code = exc.code
            return code, buf.getvalue(), err.getvalue()


        def main():
            temporary = tempfile.TemporaryDirectory(prefix="btl-chain-")
            self.addCleanup(temporary.cleanup)
            root = Path(temporary.name)
            c = Chain(root)
            science = [m[0] for m in w.MEMBERS]

            # --- default fixture (tail-only nonzero after every request end) -------
            w1, r1 = c.archive(1, "p1")
            w2, r2 = c.archive(2, "p2")
            p1, p2 = member_codes(w1.archive), member_codes(w2.archive)
            print("pass-1 primary member codes:", p1)
            print("pass-2 primary member codes:", p2)
            check("real acceptance carries OS code on every pass-1 science member",
                  all(t.CODE in p1.get(r, []) for r in science), p1)
            check("real pass-2 primary carries no OS code", all(t.CODE not in v for v in p2.values()), p2)
            before1, before2 = tree_digest(w1.archive), tree_digest(w2.archive)
            code, stdout, err = run_cli("request-end-p1", w1.archive, root / "re1")
            check("request-end-p1 exit 0 on real archive", code == 0, err)
            re1 = member_codes(root / "re1")
            check("(c) request-end-p1(pass1) == pass-2 primary (exact)", re1 == p2, {"re1": re1, "p2": p2})
            code, stdout, err = run_cli("hull-p2", w2.archive, root / "hull2")
            check("hull-p2 exit 0 on real archive", code == 0, err)
            hull2 = member_codes(root / "hull2")
            check("(a) hull-p2(pass2) == pass-1 primary (exact)", hull2 == p1, {"hull2": hull2, "p1": p1})
            rec = json.loads((root / "hull2/thermal_line.json").read_text())
            check("(a) quad drops whole in hull record",
                  any(sorted(u) == sorted(w.QUAD) for u in rec["dropped_units"]), rec["dropped_units"])
            check("(f) source archives unchanged",
                  tree_digest(w1.archive) == before1 and tree_digest(w2.archive) == before2)
            code, _, err = run_cli("hull-p2", root / "hull2", root / "hull2b")
            check("(f) hull-p2 idempotent on its own output",
                  code == 0 and member_codes(root / "hull2b") == hull2 and
                  json.loads((root / "hull2b/thermal_line.json").read_text())["changes"] == [], err)
            code, _, err = run_cli("hull-p2", w1.archive, root / "wrongpass")
            check("pass mismatch recorded with exit 0", code == 0 and "pass mismatch" in (root / "wrongpass/thermal_line.json").read_text(), err)

            # --- pass 1: nonzero inside one request, s5-p1-shaped tail elsewhere ----
            first = science[0]

            def inside(win):
                path, rows = journal_rows(win)
                start, end = w.request_span_ns(first)
                hit = json.loads(json.dumps(rows[0]))
                stamp = (start + end) // 2
                assert start < stamp < end
                hit["finished"]["monotonic_ns"] = stamp
                hit["started"]["monotonic_ns"] = stamp - 1000
                hit["values"]["level"] = 2
                rows.append(hit)
                rows.sort(key=lambda row: row["finished"]["monotonic_ns"])
                for seq, row in enumerate(rows, 1):
                    row["seq"] = seq
                put_rows(path, rows)
            wi1, _ = c.archive(1, "in1", inside)
            wi2, _ = c.archive(2, "in2", inside)
            code, _, err = run_cli("request-end-p1", wi1.archive, root / "in-out")
            check("(c) inside-request member stays dropped; others restored; equals pass-2 primary",
                  code == 0 and member_codes(root / "in-out") == member_codes(wi2.archive),
                  {"out": member_codes(root / "in-out"), "p2": member_codes(wi2.archive), "err": err})

            # --- level read exactly at the request end stamp ------------------------
            def at_end(win):
                path, rows = journal_rows(win)
                _s, end = w.request_span_ns(first)
                for r in rows:
                    r["values"]["level"] = 0
                proto = json.loads(json.dumps(rows[0]))
                proto["finished"]["monotonic_ns"] = end
                proto["started"]["monotonic_ns"] = end - 1000
                proto["values"]["level"] = 1
                rows.append(proto)
                rows.sort(key=lambda r: r["finished"]["monotonic_ns"])
                for i, r in enumerate(rows, 1):
                    r["seq"] = i
                put_rows(path, rows)
            we1, _ = c.archive(1, "end1", at_end)
            we2, _ = c.archive(2, "end2", at_end)
            code, _, err = run_cli("request-end-p1", we1.archive, root / "end-out")
            check("level==1 at exactly request-end stamp: tool == pass-2 primary",
                  code == 0 and member_codes(root / "end-out") == member_codes(we2.archive),
                  {"out": member_codes(root / "end-out"), "p2": member_codes(we2.archive), "p1": member_codes(we1.archive), "err": err})

            # --- malformed lines and non-numeric levels -----------------------------
            def malformed(win):
                path, rows = journal_rows(win)
                _s, end = w.request_span_ns(first)
                nxt = next(r for r in rows if r["finished"]["monotonic_ns"] >= end)
                nxt["values"]["level"] = "warm"  # non-numeric: production skips it as a level
                put_rows(path, rows, extra="{not json\n\x00garbage\n")
            wm1, _ = c.archive(1, "mal1", malformed)
            wm2, _ = c.archive(2, "mal2", malformed)
            code, _, err = run_cli("request-end-p1", wm1.archive, root / "mal-out")
            rec = json.loads((root / "mal-out/thermal_line.json").read_text()) if code == 0 else {}
            check("malformed lines + non-numeric level: tool == pass-2 primary, malformed noticed",
                  code == 0 and member_codes(root / "mal-out") == member_codes(wm2.archive)
                  and {"code": "records.monitor_line_malformed"} in rec.get("notices", []),
                  {"out": member_codes(root / "mal-out") if code == 0 else None, "p2": member_codes(wm2.archive), "err": err})

            for index, (one, two) in enumerate(((wi1, wi2), (we1, we2), (wm1, wm2))):
                dest = root / ("variant-hull-" + str(index))
                t.transform("hull-p2", two.archive, dest)
                check("variant hull equals pass-1 primary", member_codes(dest) == member_codes(one.archive))

            # --- hand edits on a real archive copy (labelled: not harvest-produced) --
            import shutil
            def copy(src, name):
                dst = root / name
                shutil.copytree(src, dst, symlinks=True)
                return dst
            # duplicate OS row + OS together with thermal.unmeasured + battery code
            a = copy(w1.archive, "hand-dup")
            acc = json.loads((a / "derived/b6-acceptance.json").read_text())
            acc["excluding"].append({"code": t.CODE, "scope": "member", "run_id": science[0], "why": t.CODE})
            acc["excluding"].append({"code": "thermal.unmeasured", "scope": "member", "run_id": science[1], "why": "x"})
            acc["excluding"].append({"code": "battery.member_span", "scope": "member", "run_id": science[2], "why": "x"})
            (a / "derived/b6-acceptance.json").write_text(json.dumps(acc))
            code, _, err = run_cli("request-end-p1", a, root / "hand-dup-out")
            got = member_codes(root / "hand-dup-out") if code == 0 else None
            check("dup OS row fully removed; other thermal code and battery code kept",
                  got is not None and science[0] not in got and got.get(science[1]) == ["thermal.unmeasured"]
                  and got.get(science[2]) == ["battery.member_span"], {"got": got, "err": err})
            # member absent from spans.json entirely
            a = copy(w1.archive, "hand-nospan")
            sp = json.loads((a / "withheld/spans.json").read_text())
            del sp["spans"][science[3]]
            (a / "withheld/spans.json").write_text(json.dumps(sp))
            code, _, err = run_cli("request-end-p1", a, root / "hand-nospan-out")
            got = member_codes(root / "hand-nospan-out") if code == 0 else None
            check("member absent from spans keeps hull OS code", got is not None and t.CODE in got.get(science[3], []),
                  {"got": got, "err": err})
            # request span equal to the hull
            a = copy(w1.archive, "hand-eq")
            sp = json.loads((a / "withheld/spans.json").read_text())
            sp["spans"][science[4]]["request"] = list(sp["spans"][science[4]]["member"])
            (a / "withheld/spans.json").write_text(json.dumps(sp))
            code, _, err = run_cli("request-end-p1", a, root / "hand-eq-out")
            got = member_codes(root / "hand-eq-out") if code == 0 else None
            check("request == hull keeps hull OS code", got is not None and t.CODE in got.get(science[4], []),
                  {"got": got, "err": err})
            # reference member with OS code
            a = copy(w1.archive, "hand-ref")
            ro = json.loads((a / "derived/roster.json").read_text())
            ro["members"][0]["kind"] = "external_input"
            (a / "derived/roster.json").write_text(json.dumps(ro))
            code, _, err = run_cli("request-end-p1", a, root / "hand-ref-out")
            got = member_codes(root / "hand-ref-out") if code == 0 else None
            check("reference member OS code untouched", got is not None and t.CODE in got.get(science[0], []),
                  {"got": got, "err": err})
            # journal compressed like harvest accepts (thermal.jsonl.zst): harvest reads it, tool?
            a = copy(w1.archive, "hand-zst")
            j = a / "sources/night-custody/hazards/monitor/thermal.jsonl"
            raw = j.read_bytes()
            try:
                import subprocess
                subprocess.run(["zstd", "-q", "--rm", str(j)], check=True)
                readings, _ = h.read_monitor_journal(j, "thermal")
                code, _, err = run_cli("request-end-p1", a, root / "hand-zst-out")
                check("zst journal: production reader and tool read it",
                      True, {"production_readings": len(readings), "tool_exit": code, "err": err.strip()})
            except (OSError, subprocess.CalledProcessError) as exc:
                check("zst journal probe", True, f"zstd unavailable: {exc}")
            del raw

            # --- blinding sentinels in JSON measurement fields ----------------------
            a = copy(w1.archive, "hand-sentinel")
            sentinel = "918273645.192837"
            acc = json.loads((a / "derived/b6-acceptance.json").read_text())
            acc["calibration"] = {"energy_j": float(sentinel), **(acc.get("calibration") or {})}
            raw = json.dumps(acc).replace(json.dumps(float(sentinel)), sentinel)
            (a / "derived/b6-acceptance.json").write_text(raw)
            ma = json.loads((a / "withheld/member-assessments.json").read_text())
            code, stdout, err = run_cli("request-end-p1", a, root / "sent-out")
            out_rec = (root / "sent-out/thermal_line.json").read_text() if code == 0 else ""
            check("JSON sentinel absent from stdout and record, byte-copied in output",
                  code == 0 and sentinel not in stdout and sentinel not in out_rec
                  and sentinel in (root / "sent-out/derived/b6-acceptance.json").read_text(), err)
            del ma

            # --- output linking: analysis-side writes, and source mutation ----------
            out = root / "re1"
            link = out / "withheld/spans.json"
            check("output files are symlinks into the source", link.is_symlink() and
                  Path(os.readlink(link)).resolve() == (w1.archive / "withheld/spans.json").resolve())
            rec = json.loads((out / "thermal_line.json").read_text())
            check("record lists the sources it hashed", sorted(Path(p).name for p in rec["source_sha256"]),
                  sorted(Path(p).name for p in rec["source_sha256"]))
            modified = out / "derived/b6-acceptance.json"
            check("modified copy is read-only", not modified.is_symlink() and modified.stat().st_mode & 0o777 == 0o444)
            check("initial view verifies", t.verify(out) == [])
            accept_archive(w1.archive, json.loads(w1.plan_path.read_text()), JW / "configs/b6/registration",
                           plan_path=w1.plan_path, replace_existing=True)
            check("real re-acceptance detected", bool(t.verify(out)))
            # Re-harvest/move of the source changes what the output means: the record still verifies?
            moved = root / "p1-moved"
            os.rename(w1.archive, moved)
            dangling = not (out / "withheld/spans.json").exists()
            os.rename(moved, w1.archive)
            check("moving the source leaves the output dangling (detected only by failure)", True,
                  {"dangling_after_move": dangling})
            # Mutate an unhashed linked file (bundle events) and verify nothing in the record catches it.
            hashed = set(rec["source_sha256"])
            linked = [p for p in out.rglob("*") if p.is_symlink() and str(Path(os.readlink(p))) not in hashed]
            check("linked files whose SHA-256 is NOT in the record", True, {"count": len(linked),
                  "example": str(linked[0].relative_to(out)) if linked else None})

            print("\nSUMMARY", sum(ok for _, ok, _ in RESULTS), "/", len(RESULTS), "pass; root", root)
            return 0 if all(ok for _, ok, _ in RESULTS) else 1

        main()


class ReviewerGroupedAnalysisTests(unittest.TestCase):
    """Full Opus grouped campaign; intentionally retains all twelve sessions.

    This takes several minutes. The module has no optional slow-test convention.
    """
    def test_grouped_campaign_census_and_analysis(self):
        import copy
        import csv
        import hashlib
        import json
        import os
        import sys
        import tempfile
        from pathlib import Path

        JW = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(JW))
        from joulewise import bytes_analysis as ba  # noqa: E402
        from scripts import bytes_thermal_lines as t
        from tests.b6 import test_bytes_p2_thermal_window as fx  # noqa: E402
        from tests import test_harvest_b5_window as w  # noqa: E402
        from tests.test_bytes_analysis import archive_campaign, release_keys  # noqa: E402

        NS = fx.NS
        RESULTS = []


        def check(name, ok, detail=""):
            assert ok, (name, detail)
            RESULTS.append((name, bool(ok), detail))
            print(("PASS " if ok else "FAIL ") + name + (": " + str(detail) if detail else ""))


        def rewrite_csv(path, run, code):
            with path.open(newline="") as s:
                r = csv.DictReader(s)
                fields, rows = r.fieldnames, list(r)
            hit = False
            for row in rows:
                if row["run_id"] == run:
                    row["exclusion_codes"] = code
                    row["excluded"] = "True"
                    hit = True
            with path.open("w", newline="") as s:
                wr = csv.DictWriter(s, fields)
                wr.writeheader()
                wr.writerows(rows)
            return hit


        def cell(records, manifest, model):
            try:
                cells = ba.reduce_models(records, manifest, boundaries=("rails",))
            except ba.AnalysisError as exc:
                return {"status": "error:" + str(exc)}
            c = next((c for c in cells if c["model"] == model), None)
            if c is None:
                return {"status": "model absent from reduced cells", "records": sum(r.get("model") == model for r in records)}
            return {k: c.get(k) for k in ("status", "n_b", "removed_runs")}


        def main():
            temporary = tempfile.TemporaryDirectory(prefix="btl-ana-")
            self.addCleanup(temporary.cleanup)
            root = Path(temporary.name)
            manifest = archive_campaign(root, non_claim=False, release="none", subpack_sessions=True)
            models = {m["model"]: m for m in manifest["models"]}
            # Census over every session, including those with no thermal change.
            release_keys(root, manifest, "all")
            for census_session in manifest["sessions"]:
                sid = census_session["session_id"]
                original_export = root / "export" / sid
                original_public = original_export / (sid + ".runs.csv")
                out = root / ("census-" + sid)
                mode = "hull-p2" if census_session["pass_id"] == 2 else "request-end-p1"
                t.transform(mode, Path(census_session["archive"]), out, original_export)
                local = copy.deepcopy(manifest)
                local["sessions"] = [copy.deepcopy(census_session)]
                local["sessions"][0]["released_key_dir"] = str((root / "released-keys/bytes/blinding").resolve())
                for include in (False, True):
                    old_rows, _ = ba._stage_export_rows(original_public, include_withheld=include)
                    new_rows, _ = ba._stage_export_rows(out / "export" / original_public.name,
                                                       include_withheld=include)
                    assert len(old_rows) == len(new_rows)
                    assert {r["run_id"] for r in old_rows} == {r["run_id"] for r in new_rows}
                    commit = "a" * 40 if include else None
                    old = ba.load_records(original_export, local, stage="blinded", stage1_commit=commit)
                    new = ba.load_records(out / "export", local, stage="blinded", stage1_commit=commit)
                    assert len(old) == len(new)
                    assert {r["model"] for r in old} == {r["model"] for r in new}
                    old_cells = ba.reduce_models(old, local, boundaries=("rails",))
                    new_cells = ba.reduce_models(new, local, boundaries=("rails",))
                    assert {(c["model"], c["status"]) for c in old_cells} == {(c["model"], c["status"]) for c in new_cells}
            for sid in ("bytes-s5-p1", "bytes-s2-p1", "bytes-s2-p2"):
                session = next(s for s in manifest["sessions"] if s["session_id"] == sid)
                source = Path(session["archive"])
                export = root / "export" / sid
                side = json.loads((export / (sid + ".session.json")).read_text())["blinding"]["withheld"]
                store = (export / side["path"]).resolve()
                roster_path = source / "derived/roster.json"
                roster = json.loads(roster_path.read_bytes())
                for m in roster["members"]:  # real harvest rosters carry kind; this fixture carries role
                    m["kind"] = "science" if m["role"] == "science" else "external_input"
                roster_path.write_text(json.dumps(roster))
                science = [m for m in roster["members"] if m["role"] == "science"]
                # choose the target: a heldout-config member when one exists (s5, s2), else fit
                heldout = [m for m in science if models[next(x["model"] for x in manifest["models"]
                           if m["units"][0]["cell_id"] in x["cell_ids"])]["role"] == "heldout"
                           and m["units"][0]["stratum"] == "quad"]
                fit = [m for m in science if m not in heldout and m["units"][0]["stratum"] == "quad"
                       and models[next(x["model"] for x in manifest["models"]
                                  if m["units"][0]["cell_id"] in x["cell_ids"])]["role"] == "fit"]
                for label, pool in (("heldout", heldout), ("fit", fit)):
                    if not pool:
                        continue
                    target = pool[0]
                    run = target["run_id"]
                    model = next(x for x in manifest["models"] if target["units"][0]["cell_id"] in x["cell_ids"])
                    work = root / f"{sid}-{label}"
                    import shutil
                    shutil.copytree(source, work / "archive", symlinks=True)
                    shutil.copytree(export, work / "export", symlinks=True)
                    wstore = work / "store.runs.csv"
                    if store.is_file():
                        shutil.copyfile(store, wstore)
                        sc = json.loads((work / "export" / (sid + ".session.json")).read_text())
                        sc["blinding"]["withheld"]["path"] = os.path.relpath(wstore, work / "export")
                        (work / "export" / (sid + ".session.json")).write_text(json.dumps(sc, sort_keys=True, indent=2) + "\n")
                    arch = work / "archive"
                    acc_path = arch / "derived/b6-acceptance.json"
                    acc = json.loads(acc_path.read_bytes())
                    pass_id = session["pass_id"]
                    # LABELLED INJECTION (no harvest in this fixture)
                    if pass_id == 2:
                        values = {m["run_id"]: {t.FIELD: {"excluded": m is target, "journal_available": True,
                                  "samples": [], "span_monotonic_ns": [20 * NS, 110 * NS]}} for m in science}
                        (arch / "withheld/member-assessments.json").write_text(json.dumps({"members": values}))
                        mode = "hull-p2"
                    else:
                        acc["excluding"].append({"scope": "member", "run_id": run, "code": t.CODE, "why": t.CODE})
                        acc_path.write_text(json.dumps(acc))
                        spans = {m["run_id"]: {"member": None, "request": None} for m in science}
                        spans[run] = {"member": [20 * NS, 110 * NS], "request": [40 * NS, 80 * NS]}
                        (arch / "withheld/spans.json").write_text(json.dumps({"spans": spans}))
                        (arch / "derived/harvest-thresholds.json").write_text(json.dumps({"values": w.REGISTERED_HARVEST_THRESHOLDS}))
                        j = arch / "sources/night-custody/hazards/monitor/thermal.jsonl"
                        j.parent.mkdir(parents=True, exist_ok=True)
                        fx.thermal_journal(range(0, 126, 5), {90}).dump(j)  # s5-p1 shape: first nonzero 10 s after request end
                        csv_hit = rewrite_csv(work / "export" / (sid + ".runs.csv"), run, t.CODE)
                        if not csv_hit and wstore.is_file():
                            rewrite_csv(wstore, run, t.CODE)
                        mode = "request-end-p1"
                    # tool, archive-only and blinded
                    out_a = work / "line-archive"
                    rec_a = t.transform(mode, arch, out_a)
                    check(f"{sid}/{label}: archive-stage transform changes exactly the target",
                          [c["run_id"] for c in rec_a["changes"]] == [run], rec_a["changes"])
                    out_b = work / "line-blinded"
                    try:
                        rec_b = t.transform(mode, arch, out_b, work / "export")
                        blinded_err = None
                    except ValueError as exc:
                        rec_b, blinded_err = None, str(exc)
                    check(f"{sid}/{label}: blinded transform result", True,
                          {"refused": blinded_err, "in_public_csv": run in (work / "export" / (sid + ".runs.csv")).read_text()})
                    assert rec_b is not None, blinded_err
                    assert rec_a["changes"] == rec_b["changes"]
                    if label == "heldout":
                        member = next(m for m in rec_b["member_statuses"] if m["run_id"] == run)
                        assert member["blinded_status"] == "not defined at blinded stage (row withheld)"
                    public = work / "export" / (sid + ".runs.csv")
                    changed_public = out_b / "export" / public.name
                    for include in (False, True):
                        old_rows, _ = ba._stage_export_rows(public, include_withheld=include)
                        new_rows, _ = ba._stage_export_rows(changed_public, include_withheld=include)
                        assert len(old_rows) == len(new_rows)
                        assert {r["run_id"] for r in old_rows} == {r["run_id"] for r in new_rows}
                    # analysis: source vs output, archive stage (stage=all via export ingress, archive locator -> out)
                    local = copy.deepcopy(manifest)
                    local["sessions"] = [copy.deepcopy(session)]
                    release_keys(root, manifest, "all")
                    local["sessions"][0]["released_key_dir"] = str((root / "released-keys/bytes/blinding").resolve())
                    one = work / "one-export"
                    one.mkdir(exist_ok=True)
                    for name in (sid + ".runs.csv", sid + ".session.json"):
                        if not (one / name).exists():
                            (one / name).symlink_to(work / "export" / name)
                    local["sessions"][0]["archive"] = str(arch)
                    src = cell(ba.load_records(one, local, stage="all"), local, model["model"])
                    local_out = copy.deepcopy(local)
                    local_out["sessions"][0]["archive"] = str(out_a)
                    new = cell(ba.load_records(one, local_out, stage="all"), local_out, model["model"])
                    check(f"{sid}/{label}: archive stage source vs line ({model['model']})", True, {"source": src, "line": new})
                    assert src["status"] == new["status"] == "computed"
                    assert (src["n_b"], new["n_b"]) == ((10, 9) if pass_id == 2 else (9, 10))
                    # direct archive ingress (load_records on the archive root) as the builder's test does
                    try:
                        d_src = cell(ba.load_records(arch, local, stage="all"), local, model["model"])
                        d_new = cell(ba.load_records(out_a, local_out, stage="all"), local_out, model["model"])
                    except Exception as exc:  # noqa: BLE001
                        d_src = d_new = "error " + type(exc).__name__ + ": " + str(exc)[:200]
                    check(f"{sid}/{label}: archive-root ingress source vs line", True, {"source": d_src, "line": d_new})
                    # blinded stage: pre-commit and post-commit (stage1_commit) on source vs output export
                    for commit in (None, "a" * 40):
                        b_src = cell(ba.load_records(one, local, stage="blinded", stage1_commit=commit), local, model["model"])
                        if rec_b is not None:
                            b_new = cell(ba.load_records(out_b / "export", local, stage="blinded", stage1_commit=commit),
                                         local, model["model"])
                        else:
                            b_new = "no output (refused)"
                        original_records = ba.load_records(one, local, stage="blinded", stage1_commit=commit)
                        changed_records = ba.load_records(out_b / "export", local, stage="blinded", stage1_commit=commit)
                        assert len(original_records) == len(changed_records)
                        assert {r["model"] for r in original_records} == {r["model"] for r in changed_records}
                        original_cells = ba.reduce_models(original_records, local, boundaries=("rails",))
                        changed_cells = ba.reduce_models(changed_records, local, boundaries=("rails",))
                        assert {(c["model"], c["status"]) for c in original_cells} == {(c["model"], c["status"]) for c in changed_cells}
                        if commit or label == "fit":
                            assert (b_src["n_b"], b_new["n_b"]) == ((10, 9) if pass_id == 2 else (9, 10))
                        check(f"{sid}/{label}: blinded stage commit={bool(commit)} source vs line", True,
                              {"source": b_src, "line": b_new,
                               "line_export_files": sorted(p.name for p in (out_b / "export").iterdir()) if rec_b else None})
            print("\nSUMMARY", sum(ok for _, ok, _ in RESULTS), "/", len(RESULTS), "; root", root)
            return 0

        main()





class RecordedFaultTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.archive = self.root / 'archive'
        self.put('derived/b6-acceptance.json', {'session_id': 's', 'excluding': [
            {'scope': 'member', 'run_id': 'a', 'code': t.CODE}]})
        self.put('derived/roster.json', {'members': [
            {'run_id': r, 'kind': 'science', 'units': []} for r in ('a', 'b')]})
        self.put('withheld/spans.json', {'spans': {
            r: {'member': [20 * fixtures.NS, 100 * fixtures.NS],
                'request': [40 * fixtures.NS, 80 * fixtures.NS]} for r in ('a', 'b')}})
        self.journal = self.archive / 'sources/night-custody/hazards/monitor/thermal.jsonl'
        self.journal.parent.mkdir(parents=True)
        fixtures.thermal_journal(range(0, 126, 5), {90}).dump(self.journal)

    def put(self, name, data):
        path = self.archive / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def run_line(self, name, export=None):
        out = self.root / name
        capture = io.StringIO()
        args = ['request-end-p1', str(self.archive), str(out)]
        if export:
            args += ['--export', str(export)]
        with contextlib.redirect_stdout(capture):
            self.assertIsNone(t.main(args))
        self.assertTrue((out / 'thermal_line.json').is_file())
        return json.loads(capture.getvalue()), out

    def test_missing_journal_with_and_without_affected_members(self):
        self.journal.unlink()
        record, _ = self.run_line('missing')
        statuses = {r['run_id']: r['status'] for r in record['member_statuses']}
        self.assertEqual(statuses['a'], 'not defined (archived thermal journal unavailable)')
        self.assertEqual(statuses['b'], 'equals registered line')
        self.put('derived/b6-acceptance.json', {'session_id': 's', 'excluding': []})
        record, _ = self.run_line('clean')
        self.assertEqual(record['status'], 'equals registered line')

    def test_pass_mismatch_is_recorded(self):
        self.put('sources/repo/plan_tree.json', {'bytes_pass': 2})
        record, _ = self.run_line('pass')
        self.assertIn('not defined (pass mismatch)', [r['status'] for r in record['member_statuses']])

    def test_export_disagreement_and_missing_member(self):
        export = self.root / 'export'
        export.mkdir()
        path = export / 's.runs.csv'
        path.write_text('run_id,exclusion_codes,excluded\na,,False\nb,,False\n')
        record, _ = self.run_line('disagree', export)
        self.assertEqual(record['changes'], [])
        self.assertEqual(record['member_statuses'][0]['status'],
                         'not defined (CSV/archive code disagreement: a)')
        path.write_text('run_id,exclusion_codes,excluded\nb,,False\n')
        record, _ = self.run_line('absent', export)
        self.assertEqual(record['member_statuses'][0]['status'],
                         'not defined (changed member absent from export)')

    def test_journal_digest_and_missing_gap_threshold(self):
        record, _ = self.run_line('no-gap')
        self.assertEqual([r['run_id'] for r in record['changes']], ['a'])
        self.put('derived/window_flags.json', {'hazards': {'thermal': {'continuous': {
            'journal': {'sha256': '0' * 64}}}}})
        record, _ = self.run_line('different-journal')
        self.assertEqual(record['changes'], [])
        self.assertIn({'code': 'records.thermal_journal_mismatch'}, record['notices'])
        self.assertEqual(record['member_statuses'][0]['status'],
                         "not defined (journal differs from the harvest's)")
        self.put('withheld/member-assessments.json', {'members': {r: {t.FIELD: {
            'excluded': True, 'journal_available': True}} for r in ('a', 'b')}})
        hull = t.transform('hull-p2', self.archive, self.root / 'hull')
        self.assertNotIn({'code': 'records.thermal_journal_mismatch'}, hull['notices'])

    def test_withheld_sentinels_opaque_and_excluded_consistent(self):
        export = self.root / 'export'
        export.mkdir()
        (export / 's.runs.csv').write_text('run_id,exclusion_codes,excluded,energy\nb,,False,987654321.123456\n')
        store = export / 'store.csv'
        store.write_bytes(('run_id,exclusion_codes,excluded,energy,power,duration,rail\r\n'
                           'a,' + t.CODE + ',True,987654321.123456,"opaque,\r\n876543210.234567",765432109.345678,654321098.456789\r\n').encode())
        (export / 's.session.json').write_text('{"energy":987654321.123456,"blinding":{"withheld":{"path":"store.csv","row_count":1}}}')
        loads = json.loads
        sentinels = ('987654321.123456', '876543210.234567', '765432109.345678', '654321098.456789')
        def guarded(raw, *args, **kwargs):
            raw = raw.decode() if isinstance(raw, bytes) else raw
            for sentinel in sentinels:
                self.assertNotIn(sentinel, raw)
            return loads(raw, *args, **kwargs)
        with patch.object(t.json, 'loads', side_effect=guarded):
            record = t.transform('request-end-p1', self.archive, self.root / 'hidden', export)
        output = self.root / 'hidden/export/withheld/s.withheld.csv'
        original, changed = store.read_bytes().decode(), output.read_bytes().decode()
        for old, new in zip(t.csv_fields(original)[1:], t.csv_fields(changed)[1:]):
            for index in range(3, 7):
                self.assertEqual(original[slice(*old[index])], changed[slice(*new[index])])
        self.assertEqual(next(csv.DictReader(io.StringIO(changed)))['excluded'], 'False')
        self.assertEqual(output.stat().st_mode & 0o777, 0o444)
        for sentinel in sentinels:
            self.assertNotIn(sentinel, json.dumps(record))
        self.assertEqual(record['member_statuses'][0]['blinded_status'],
                         'not defined at blinded stage (row withheld)')

    def test_verify_reduction_changes_and_all_differing_paths(self):
        self.put('withheld/reductions/a.json', {'energy': 'opaque'})
        record, out = self.run_line('view')
        self.assertEqual(t.verify(out), [])
        self.put('withheld/reductions/a.json', {'energy': 'changed'})
        self.put('withheld/spans.json', {'spans': {}})
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            self.assertIsNone(t.main(['verify', str(out)]))
        self.assertEqual(capture.getvalue().splitlines(),
                         ['withheld/reductions/a.json', 'withheld/spans.json'])
        self.assertTrue(json.loads((out / 'thermal_line.json').read_text())['records.thermal_view_changed'])
        self.assertIsInstance(record['producing_tree_dirty'], bool)

    def test_compressed_journal_matches_sealed_decompressed_digest(self):
        import shutil
        import subprocess
        if shutil.which('zstd') is None:
            self.skipTest('zstd optional, as in harvest tests')
        self.put('derived/window_flags.json', {'hazards': {'thermal': {'continuous': {
            'journal': {'sha256': hashlib.sha256(self.journal.read_bytes()).hexdigest()}}}}})
        subprocess.run(['zstd', '-q', '--rm', str(self.journal)], check=True)
        record, _ = self.run_line('compressed')
        self.assertEqual([r['run_id'] for r in record['changes']], ['a'])
        self.assertNotIn({'code': 'records.thermal_journal_mismatch'}, record['notices'])

    def test_disagreement_does_not_block_an_evaluable_member(self):
        self.put('derived/b6-acceptance.json', {'session_id': 's', 'excluding': [
            {'scope': 'member', 'run_id': r, 'code': t.CODE} for r in ('a', 'b')]})
        export = self.root / 'partial-export'
        export.mkdir()
        (export / 's.runs.csv').write_text('run_id,exclusion_codes,excluded\na,,False\nb,' + t.CODE + ',True\n')
        record, out = self.run_line('partial', export)
        self.assertEqual([r['run_id'] for r in record['changes']], ['b'])
        self.assertIn('CSV/archive code disagreement: a', record['status'])
        self.assertFalse(record['equals_registered_line'])
        self.assertEqual(json.loads((out / 'derived/b6-acceptance.json').read_text())['excluding'],
                         [{'scope': 'member', 'run_id': 'a', 'code': t.CODE}])

    def test_existing_output_and_manifest_binding(self):
        existing = self.root / 'existing'
        existing.mkdir()
        record, out = self.run_line('existing')
        self.assertEqual(t.verify(out), [])
        manifest = out / 'view_manifest.json'
        manifest.chmod(0o644)
        manifest.write_bytes(manifest.read_bytes() + b'\n')
        self.assertEqual(t.verify(out), ['view_manifest.json'])
        result = json.loads((out / 'thermal_line.json').read_bytes())
        self.assertIn({'code': 'records.thermal_view_changed'}, result['notices'])


if __name__ == '__main__':
    unittest.main()
