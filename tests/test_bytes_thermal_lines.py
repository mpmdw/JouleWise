"""Synthetic production-harvest checks for exclusion-only thermal alternatives."""
from __future__ import annotations

import contextlib
import copy
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import bytes_thermal_lines as t
from tests.b6 import test_bytes_p2_thermal_window as fixtures
from tests import test_harvest_b5_window as w
from joulewise import bytes_analysis as ba


def add_campaign_pass_identity(manifest):
    # The analysis-only synthetic campaign predates archived pass identities.
    for session in manifest['sessions']:
        archive = Path(session['archive'])
        pack_id = json.loads((archive / 'derived/roster.json').read_bytes())['pack_id']
        path = archive / 'sources/repo/configs/campaigns' / pack_id / 'plan_tree.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'bytes_pass': session['pass_id']}))


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
        repeated = t.transform('hull-p2', source, again, export)
        self.assertEqual(json.dumps(repeated['changes']), json.dumps(record['changes']))
        self.assertEqual((out / 'view_manifest.json').read_bytes(), (again / 'view_manifest.json').read_bytes())
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
            {'pack_id': 'thermal-fixture', 'members': [{'run_id': 'science', 'kind': 'science', 'units': []}]}))
        tree = source / 'sources/repo/configs/campaigns/thermal-fixture/plan_tree.json'
        tree.parent.mkdir(parents=True)
        tree.write_text('{"bytes_pass":2}')
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
            add_campaign_pass_identity(manifest)
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
                    (source / 'derived/window_flags.json').write_text(json.dumps({'hazards': {'thermal': {'continuous': {
                        'journal': {'sha256': hashlib.sha256(journal.read_bytes()).hexdigest()}}}}}))
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
        native_archives = set()


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
                native_archives.add(win.archive)
                journal = win.archive / "sources/night-custody/hazards/monitor/thermal.jsonl"
                actual, malformed = t.journal_readings(t.h.read_bytes(journal))
                expected, prod_malformed = t.h.read_monitor_journal(journal, "thermal")
                def projection(rows):
                    return [(r.monotonic_ns, r.monotonic_raw_ns, r.wall_ns,
                             r.started_monotonic_ns, r.started_wall_ns, r.status,
                             t.h._int(r.values.get("level"))) for r in rows]
                check("native journal: consumed projections equal", projection(actual) == projection(expected))
                check("native journal: malformed counts equal", malformed == prod_malformed)
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
            if code == 0 and archive in native_archives:
                record = json.loads(buf.getvalue())
                check("native harvest: no untrusted member", not any(
                    m['status'].startswith('not defined') for m in record['member_statuses']))
                check("native harvest: no replay disagreement", not any(
                    n['code'] == 'records.thermal_hull_replay_disagrees' for n in record['notices']))
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
            wrong = json.loads((root / "wrongpass/thermal_line.json").read_text())
            check("pass mismatch recorded, hull-invariant members remain equal", code == 0
                  and wrong["equals_registered_line"]
                  and member_codes(root / "wrongpass") == p1
                  and {"code": "records.thermal_pass_mismatch", "reason": "pass mismatch"} in wrong["notices"], err)

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
                hull_record = t.transform("hull-p2", two.archive, dest)
                check("native variant hull: no untrusted member", not any(
                    m["status"].startswith("not defined") for m in hull_record["member_statuses"]))
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
            add_campaign_pass_identity(manifest)
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
                        (arch / 'derived/window_flags.json').write_text(json.dumps({'hazards': {'thermal': {'continuous': {
                            'journal': {'sha256': hashlib.sha256(j.read_bytes()).hexdigest()}}}}}))
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
        self.put('sources/repo/configs/campaigns/thermal-fixture/plan_tree.json', {'bytes_pass': 1})
        self.put('derived/roster.json', {'members': [
            {'run_id': r, 'kind': 'science', 'units': []} for r in ('a', 'b')]})
        self.put('withheld/spans.json', {'spans': {
            r: {'member': [20 * fixtures.NS, 100 * fixtures.NS],
                'request': [40 * fixtures.NS, 80 * fixtures.NS]} for r in ('a', 'b')}})
        self.journal = self.archive / 'sources/night-custody/hazards/monitor/thermal.jsonl'
        self.journal.parent.mkdir(parents=True)
        fixtures.thermal_journal(range(0, 126, 5), {90}).dump(self.journal)
        self.put('derived/window_flags.json', {'hazards': {'thermal': {'continuous': {
            'journal': {'sha256': hashlib.sha256(self.journal.read_bytes()).hexdigest()}}}}})

    def put(self, name, data):
        if name == 'derived/roster.json':
            data = dict(data, pack_id='thermal-fixture')
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

    def test_w4_faults_cli(self):
        import subprocess
        import sys
        for fault in ('excluding-null', 'missing-code', 'missing-run', 'utf8', 'session', 'empty-csv'):
            with self.subTest(fault=fault):
                acceptance = {'session_id': 's', 'excluding': [{'scope': 'member', 'run_id': 'a', 'code': t.CODE}]}
                roster = {'members': [{'run_id': r, 'kind': 'science', 'units': []} for r in ('a', 'b')]}
                if fault == 'excluding-null':
                    acceptance['excluding'] = None
                elif fault == 'missing-code':
                    acceptance['excluding'][0].pop('code')
                elif fault == 'missing-run':
                    roster['members'][0].pop('run_id')
                elif fault == 'session':
                    acceptance.pop('session_id')
                self.put('derived/b6-acceptance.json', acceptance)
                self.put('derived/roster.json', roster)
                export = self.root / ('exp-' + fault)
                export.mkdir()
                raw = (b'run_id,exclusion_codes,excluded\na,\xff,True\n' if fault == 'utf8' else b'')
                (export / 's.runs.csv').write_bytes(raw)
                out = self.root / ('w4-' + fault)
                args = [sys.executable, t.__file__, 'request-end-p1', str(self.archive), str(out)]
                if fault in ('utf8', 'session', 'empty-csv'):
                    args += ['--export', str(export)]
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(result.stdout)
                affected = record['member_statuses'][:1] if fault == 'missing-code' else record['member_statuses']
                self.assertTrue(all(m['status'].startswith('not defined (') for m in affected))
                self.assertEqual(record['changes'], [])
                if fault in ('utf8', 'empty-csv'):
                    self.assertEqual((out / 'export/s.runs.csv').read_bytes(), raw)
                    self.assertNotIn('changed member absent', record['member_statuses'][0]['status'])

    def test_verify_structural_damage_and_paths_cli(self):
        import subprocess
        import sys
        for index, damage in enumerate(({'notices': [None]}, {'notices': [{}]}, {'notices': [{'code': 1}]},
                {'source_sha256': None}, {'source_sha256': []}, {'source_sha256': {'x': 1}},
                {'view_manifest_sha256': None})):
            out = self.root / ('damage-' + str(index))
            t.transform('request-end-p1', self.archive, out)
            path = out / 'thermal_line.json'
            record = json.loads(path.read_bytes())
            record.update(damage)
            path.unlink()
            path.write_text(json.dumps(record))
            p = subprocess.run([sys.executable, t.__file__, 'verify', str(out)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            record = json.loads(path.read_bytes())
            self.assertTrue(record['records.thermal_view_changed'])
            self.assertIn('thermal_line.json', record['view_differing_paths'])
        out = self.root / 'real-output'
        t.transform('request-end-p1', self.archive, out)
        link = self.root / 'link'
        link.symlink_to(out)
        p = subprocess.run([sys.executable, t.__file__, 'verify', str(link)], capture_output=True, text=True)
        self.assertEqual((p.returncode, p.stdout.strip()), (0, 'view verified'))
        # A valid record copied into a source must never be rewritten there.
        source_record = self.archive / 'thermal_line.json'
        source_record.write_bytes((out / 'thermal_line.json').read_bytes())
        before = source_record.read_bytes()
        link.unlink()
        link.symlink_to(self.archive)
        p = subprocess.run([sys.executable, t.__file__, 'verify', str(link)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('"records.thermal_view_changed": true', p.stdout)
        self.assertEqual(source_record.read_bytes(), before)
        self.assertFalse((self.archive / 'view_manifest.json').exists())
        missing = self.root / 'missing-output'
        p = subprocess.run([sys.executable, t.__file__, 'verify', str(missing)], capture_output=True, text=True)
        self.assertEqual((p.returncode, p.stdout.strip()), (0, 'output missing'))
        self.assertFalse(missing.exists())

    def test_missing_journal_with_and_without_affected_members(self):
        self.journal.unlink()
        (self.archive / 'derived/window_flags.json').unlink()
        record, _ = self.run_line('missing')
        self.assertIn({'code': 'records.thermal_journal_provenance_unavailable'}, record['notices'])
        statuses = {r['run_id']: r['status'] for r in record['member_statuses']}
        self.assertEqual(statuses['a'], 'not defined (archived thermal journal unavailable)')
        self.assertEqual(statuses['b'], 'equals registered line')
        self.put('derived/b6-acceptance.json', {'session_id': 's', 'excluding': []})
        record, _ = self.run_line('clean')
        self.assertEqual(record['status'], 'equals registered line')

    def test_missing_journal_provenance_preserves_original_codes(self):
        flags = self.archive / 'derived/window_flags.json'
        flags.unlink()
        for name, value in [('absent', None), ('no-sha', {'hazards': {'thermal': {'continuous': {'journal': {}}}}})]:
            if value is not None:
                self.put('derived/window_flags.json', value)
            original = (self.archive / 'derived/b6-acceptance.json').read_bytes()
            record, out = self.run_line('provenance-' + name)
            self.assertEqual(record['changes'], [])
            self.assertEqual(record['member_statuses'][0]['status'], 'not defined (journal provenance unavailable)')
            self.assertEqual(record['member_statuses'][1]['status'], 'equals registered line')
            self.assertIn({'code': 'records.thermal_journal_provenance_unavailable'}, record['notices'])
            self.assertEqual((out / 'derived/b6-acceptance.json').read_bytes(), original)

    def test_pass_mismatch_is_recorded(self):
        self.put('sources/repo/configs/campaigns/thermal-fixture/plan_tree.json', {'bytes_pass': 2})
        record, _ = self.run_line('pass')
        self.assertIn('not defined (pass mismatch)', [r['status'] for r in record['member_statuses']])

    def test_fault_direction_and_pass_mismatch_for_both_lines(self):
        for mode in t.LABELS:
            with self.subTest(mode=mode):
                self.put('sources/repo/configs/campaigns/thermal-fixture/plan_tree.json', {'bytes_pass': 2 if mode == 'hull-p2' else 1})
                self.journal.unlink(missing_ok=True)
                record = t.transform(mode, self.archive, self.root / (mode + '-unavailable'))
                statuses = [m['status'] for m in record['member_statuses']]
                reason = 'hull assessment unavailable' if mode == 'hull-p2' else 'archived thermal journal unavailable'
                expected = ['equals registered line', 'not defined (' + reason + ')']
                self.assertEqual(statuses, expected if mode == 'hull-p2' else expected[::-1])
                self.assertFalse(record['equals_registered_line'])
                self.assertEqual(record['changes'], [])
                self.put('sources/repo/configs/campaigns/thermal-fixture/plan_tree.json', {'bytes_pass': 1 if mode == 'hull-p2' else 2})
                record = t.transform(mode, self.archive, self.root / (mode + '-wrong-pass'))
                self.assertEqual([m['status'] for m in record['member_statuses']],
                                 (['equals registered line', 'not defined (pass mismatch)'] if mode == 'hull-p2'
                                  else ['not defined (pass mismatch)', 'equals registered line']))
                self.assertFalse(record['equals_registered_line'])
                self.assertEqual(record['changes'], [])

    def test_hull_record_faults_keep_existing_code_only(self):
        for index, value in enumerate(({}, {'excluded': True},
                {'excluded': None, 'journal_available': True},
                {'excluded': False, 'journal_available': False})):
            with self.subTest(value=value):
                self.put('sources/repo/configs/campaigns/thermal-fixture/plan_tree.json', {'bytes_pass': 2})
                self.put('withheld/member-assessments.json', {'members': {
                    r: {t.FIELD: value} for r in ('a', 'b')}})
                record = t.transform('hull-p2', self.archive, self.root / ('hull-fault-' + str(index)))
                self.assertEqual([m['status'] for m in record['member_statuses']],
                                 ['equals registered line', 'not defined (hull assessment unavailable)'])
                self.assertFalse(record['equals_registered_line'])
                self.assertEqual(record['changes'], [])

    def test_invalid_csv_records_fault_and_copies_bytes(self):
        export = self.root / 'bad-export'
        export.mkdir()
        path = export / 's.runs.csv'
        for index, raw in enumerate(('', 'run_id,excluded\na,True\nb,False\n')):
            path.write_text(raw)
            record, out = self.run_line('bad-csv-' + str(index), export)
            self.assertEqual(record['changes'], [])
            self.assertFalse(record['equals_registered_line'])
            self.assertTrue(all(m['status'].startswith('not defined (') for m in record['member_statuses']))
            self.assertEqual((out / 'export/s.runs.csv').read_bytes(), path.read_bytes())

    def test_git_unavailable_records_null_producer(self):
        import os
        with patch.dict(os.environ, {'GIT_DIR': str(self.root / 'no-git')}):
            record, _ = self.run_line('no-git')
        self.assertIsNone(record['producing_commit'])
        self.assertIsNone(record['producing_tree_dirty'])

    def test_would_add_requires_matching_seal(self):
        self.put('derived/b6-acceptance.json', {'session_id': 's', 'excluding': []})
        fixtures.thermal_journal(range(0, 126, 5), {60}).dump(self.journal)
        self.put('derived/window_flags.json', {'hazards': {'thermal': {'continuous': {
            'journal': {'sha256': '0' * 64}}}}})
        record, _ = self.run_line('mismatch-add')
        self.assertEqual(record['changes'], [])
        self.assertIn({'code': 'records.thermal_journal_mismatch'}, record['notices'])
        self.assertEqual([m['status'] for m in record['member_statuses']],
                         ['equals registered line'] * 2)
        (self.archive / 'derived/window_flags.json').unlink()
        record, _ = self.run_line('unsealed-add')
        self.assertEqual([m['status'] for m in record['member_statuses']],
                         ['equals registered line'] * 2)
        self.put('derived/window_flags.json', {'hazards': {'thermal': {'continuous': {
            'journal': {'sha256': hashlib.sha256(self.journal.read_bytes()).hexdigest()}}}}})
        out = self.root / 'sealed-add'
        with self.assertRaisesRegex(ValueError, 'request-end would add'):
            t.transform('request-end-p1', self.archive, out)
        self.assertFalse(out.exists())

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

    def test_empty_code_bytes_match_exporters_dictwriter(self):
        from joulewise.b6 import export_runs
        fields = ['run_id', 'exclusion_codes', 'excluded', 'opaque']
        rows = [dict(zip(fields, ['a', t.CODE, 'True', 'opaque,"\r\ntext'])),
                dict(zip(fields, ['b', '', 'False', 'unchanged']))]
        def fresh_export():
            stream = io.StringIO(newline='')
            writer = export_runs.csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            return stream.getvalue().encode()
        export = self.root / 'writer-export'
        export.mkdir()
        (export / 's.runs.csv').write_text('run_id,exclusion_codes,excluded,opaque\r\nb,,False,unchanged\r\n', newline='')
        store = export / 'store.csv'
        # Same DictWriter and parameters used by export_runs.write_withheld.
        original = fresh_export()
        store.write_bytes(original)
        # Public b is already present; keep only the withheld a row here.
        parsed = t.csv_fields(original.decode())
        store.write_bytes(original[:parsed[2][0][0]])
        (export / 's.session.json').write_text(json.dumps({
            'blinding': {'withheld': {'path': 'store.csv', 'row_count': 1}}}))
        record, out = self.run_line('writer-output', export)
        self.assertEqual([c['run_id'] for c in record['changes']], ['a'])
        rows[0].update(exclusion_codes='', excluded='False')
        expected = fresh_export()
        parsed = t.csv_fields(expected.decode())
        self.assertEqual((out / 'export/withheld/s.withheld.csv').read_bytes(),
                         expected[:parsed[2][0][0]])

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
                         ['withheld/reductions/a.json', 'withheld/spans.json',
                          'source changed since transform: ' + str(self.archive / 'withheld/spans.json')])
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

    def test_existing_linked_output_refuses_without_source_writes(self):
        export = self.root / 'export'
        export.mkdir()
        csv_path = export / 's.runs.csv'
        csv_path.write_text('run_id,exclusion_codes,excluded\na,' + t.CODE + ',True\nb,,False\n')
        out = self.root / 'linked-output'
        out.mkdir()
        (out / 'export').symlink_to(export, target_is_directory=True)
        before = csv_path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'new directory'):
            t.transform('request-end-p1', self.archive, out, export)
        self.assertEqual(csv_path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in out.iterdir()), ['export'])

    def test_fresh_outputs_have_identical_manifests_and_changes(self):
        export = self.root / 'repeat-export'
        export.mkdir()
        (export / 's.runs.csv').write_text('run_id,exclusion_codes,excluded\na,' + t.CODE + ',True\nb,,False\n')
        first = self.root / 'first'
        second = self.root / 'second'
        a = t.transform('request-end-p1', self.archive, first, export)
        b = t.transform('request-end-p1', self.archive, second, export)
        self.assertEqual((first / 'view_manifest.json').read_bytes(), (second / 'view_manifest.json').read_bytes())
        self.assertEqual(json.dumps(a['changes']).encode(), json.dumps(b['changes']).encode())
        before = {str(p.relative_to(first)): p.read_bytes() for p in first.rglob('*') if p.is_file()}
        self.put('sources/repo/configs/campaigns/thermal-fixture/plan_tree.json', {'bytes_pass': 2})
        with self.assertRaisesRegex(ValueError, 'new directory'):
            t.transform('request-end-p1', self.archive, first)
        # Linked source payload can change, but the certified export/control files cannot.
        for name in ('export/s.runs.csv', 'view_manifest.json', 'thermal_line.json', 'derived/b6-acceptance.json'):
            self.assertEqual((first / name).read_bytes(), before[name])

    def test_dangling_output_symlink_is_existing(self):
        out = self.root / 'dangling'
        target = self.root / 'absent'
        out.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'new directory'):
            t.transform('request-end-p1', self.archive, out)
        self.assertTrue(out.is_symlink())
        self.assertFalse(target.exists())

    def test_destination_directory_guard(self):
        out = self.root / 'guard'
        out.mkdir()
        (out / 'export').mkdir()
        (out / 'export/withheld').symlink_to(self.archive, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            t.write_copy(out / 'export/withheld/payload', 'opaque', out, [self.archive])
        self.assertFalse((self.archive / 'payload').exists())

    def test_malformed_manifests_record_reason_and_exit_zero(self):
        row = {'path': 'payload', 'size': 0, 'sha256': '0' * 64}
        cases = [None, [], {}, {'files': {}}, {'files': [None]}, {'files': [{'path': 7}]},
                 {'files': [dict(row, path=7)]}, {'files': [dict(row, path='../payload')]},
                 {'files': [dict(row, path='/payload')]}, {'files': [dict(row, path='a//b')]},
                 {'files': [row, row]}, {'files': [dict(row, size=True)]},
                 {'files': [dict(row, sha256=7)]}, {'files': [dict(row, inode=True, mtime_ns=1)]},
                 {'files': [dict(row, inode=1)]}, {'files': [dict(row, extra=1)]}]
        for index, value in enumerate(cases + ['invalid-json', 'deep-json', 'missing-file']):
            with self.subTest(index=index):
                out = self.root / ('damaged-' + str(index))
                t.transform('request-end-p1', self.archive, out)
                path = out / 'view_manifest.json'
                path.unlink()
                if value != 'missing-file':
                    path.write_text('[' * 2000 + '0' + ']' * 2000 if value == 'deep-json' else
                                    '{' if value == 'invalid-json' else json.dumps(value))
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    self.assertIsNone(t.main(['verify', str(out)]))
                record = json.loads((out / 'thermal_line.json').read_bytes())
                self.assertIs(record['records.thermal_view_changed'], True)
                self.assertIn('view_manifest.json', record['view_differing_paths'])
                self.assertTrue(any(n['code'] == 'records.thermal_view_changed' and n['reason'] for n in record['notices']))

    def test_missing_or_invalid_thermal_record_flags_and_exits_zero(self):
        for index, value in enumerate((None, '{bad', 'null', '[]')):
            with self.subTest(value=value):
                _, out = self.run_line('bad-record-' + str(index))
                path = out / 'thermal_line.json'
                path.unlink()
                if value is not None:
                    path.write_text(value)
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    self.assertIsNone(t.main(['verify', str(out)]))
                self.assertIn('thermal_line.json', capture.getvalue().splitlines())
                record = json.loads(path.read_bytes())
                self.assertTrue(record['records.thermal_view_changed'])
                self.assertIn('thermal_line.json', record['view_differing_paths'])

    def test_verify_rechecks_every_recorded_source_digest(self):
        export = self.root / 'fresh-export'
        export.mkdir()
        csv_path = export / 's.runs.csv'
        csv_path.write_text('run_id,exclusion_codes,excluded\na,' + t.CODE + ',True\nb,,False\n')
        record, out = self.run_line('source-freshness', export)
        sources = record['source_sha256']
        for index, source in enumerate(sources):
            path = Path(source)
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                self.assertIsNone(t.main(['verify', str(out)]))
            self.assertIn('source changed since transform: ' + source, capture.getvalue().splitlines())
            result = json.loads((out / 'thermal_line.json').read_bytes())
            self.assertTrue(result['records.thermal_view_changed'])
            self.assertEqual(result['source_differing_paths'], [source])
            path.write_bytes(original)
        Path(next(iter(sources))).unlink()
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            self.assertIsNone(t.main(['verify', str(out)]))
        self.assertIn('source changed since transform: ', capture.getvalue())

    def test_existing_output_and_manifest_binding(self):
        existing = self.root / 'existing'
        existing.mkdir()
        with self.assertRaisesRegex(ValueError, 'new directory'):
            t.transform('request-end-p1', self.archive, existing)
        record, out = self.run_line('fresh')
        self.assertEqual(t.verify(out), [])
        manifest = out / 'view_manifest.json'
        manifest.chmod(0o644)
        manifest.write_bytes(manifest.read_bytes() + b'\n')
        self.assertEqual(t.verify(out), ['view_manifest.json'])
        result = json.loads((out / 'thermal_line.json').read_bytes())
        self.assertTrue(any(n['code'] == 'records.thermal_view_changed' and n['reason'] for n in result['notices']))
        manifest.write_text('{}')
        differing = t.verify(out)
        self.assertIn('view_manifest.json', differing)
        self.assertIn('derived/b6-acceptance.json', differing)


if __name__ == '__main__':
    unittest.main()


# Ported from JouleWise-data 0858773e by-therm-consult/trust_matrix.py.
# X6: all fixtures identify their pack at the producer archive location.
NS = 10**9
SCRIPT = Path(t.__file__)
SPAN = {"member": [20 * NS, 100 * NS], "request": [40 * NS, 80 * NS]}
ACC, ROS, PLAN = "derived/b6-acceptance.json", "derived/roster.json", "sources/repo/configs/campaigns/thermal-fixture/plan_tree.json"
HULL, SPANS, SEAL = "withheld/member-assessments.json", "withheld/spans.json", "derived/window_flags.json"


class TrustArchive:
    """One science member `a` and one reference `r`; the trusted archive for (mode, present, candidate)."""

    def __init__(self, root, mode, present, candidate):
        self.root, self.a, self.mode = Path(root), Path(root) / "archive", mode
        self.put(ACC, {"session_id": "s", "excluding":
                 [{"scope": "member", "run_id": "a", "code": t.CODE}] if present else []})
        self.put(ROS, {"pack_id": "thermal-fixture", "members": [{"run_id": "a", "kind": "science", "units": [{"cell_id": "c", "stratum": "quad", "unit_id": "u"}]},
                                   {"run_id": "r", "kind": "reference", "units": []}]})
        self.put(PLAN, {"bytes_pass": 2 if mode == "hull-p2" else 1})
        self.put(HULL, {"members": {"a": {t.FIELD: {"excluded": candidate, "journal_available": True}}}})
        self.put(SPANS, {"spans": {"a": dict(SPAN)}})
        self.journal = self.a / "sources/night-custody/hazards/monitor/thermal.jsonl"
        self.journal.parent.mkdir(parents=True, exist_ok=True)
        # The registered hull decision (present) must be reproducible from the journal on [20, 100]:
        # present -> a nonzero read in the hull; the request-end candidate decides whether it lies in [20, 80].
        nonzero = set()
        if mode == "request-end-p1":
            if present:
                nonzero = {60} if candidate else {90}
            elif candidate:
                nonzero = {60}  # the ruled would-add stop: code absent, request-end window finds a nonzero read
        else:
            nonzero = {60 if candidate else 90}
        fixtures.thermal_journal(range(0, 126, 5), nonzero).dump(self.journal)
        self.seal()

    def put(self, name, data=None, raw=None):
        path = self.a / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            path.rmdir()
        path.write_bytes(raw if raw is not None else json.dumps(data).encode())

    def text(self, name):
        return (self.a / name).read_text()

    def seal(self, value=None):
        digest = hashlib.sha256(self.journal.read_bytes()).hexdigest() if value is None else value
        self.put(SEAL, {"hazards": {"thermal": {"continuous": {"journal": {"sha256": digest}}}}})

    def journal_rows(self):
        return [json.loads(line) for line in self.journal.read_text().splitlines()]

    def write_journal(self, rows, extra=""):
        self.journal.write_text("".join(json.dumps(row) + "\n" for row in rows) + extra)
        self.seal()


# Document-level fault trust_kinds, applied to any JSON source the tool consumes.
def trust_document_faults(name):
    def trailing(x, c):
        x.put(name, raw=(x.text(name) + " ]]garbage").encode())

    def truncated(x, c):
        x.put(name, raw=x.text(name)[:-1].encode())

    def sibling(x, c):
        x.put(name, raw=(x.text(name)[:-1] + ', "zz": @@}').encode())

    def duplicate(x, c):
        raw = x.text(name)
        x.put(name, raw=(raw[:-1] + ", " + raw[1:]).encode())  # every top-level key repeated

    def bad_number(x, c):
        x.put(name, raw=(x.text(name)[:-1] + ', "zz": 01}').encode())

    def not_utf8(x, c):
        x.put(name, raw=(x.text(name)[:-1] + ', "zz": "').encode() + b'\xff"}')

    def absent(x, c):
        (x.a / name).unlink()

    def directory(x, c):
        (x.a / name).unlink()
        (x.a / name).mkdir()

    def prefix(x, c):
        x.put(name, raw=b"{bad")

    return {"absent": absent, "directory": directory, "not-utf8": not_utf8, "unparsable-prefix": prefix,
            "trailing-garbage": trailing, "truncated-final-brace": truncated, "junk-sibling": sibling,
            "duplicate-key": duplicate, "leading-zero-number": bad_number}


def trust_kinds():
    """kind -> (mode or None, class, mutator). class in trusted/member/global/stop."""
    ks = {"trusted": (None, "trusted", lambda x, c: None)}

    def add(prefix, only, cls, faults):
        for fault, mut in faults.items():
            ks[prefix + "." + fault] = (only, cls, mut)

    # Documents: whole-text faults on each consumed JSON source.
    add("hull", "hull-p2", "member", trust_document_faults(HULL))
    add("spans", "request-end-p1", "member", trust_document_faults(SPANS))
    add("seal", "request-end-p1", "member", trust_document_faults(SEAL))
    add("plan", None, "member", trust_document_faults(PLAN))
    # Acceptance and roster: a document fault leaves no member list -> stop (ruled stop proposed);
    # typed faults inside them are W4 global faults.
    add("acceptance", None, "stop", {k: v for k, v in trust_document_faults(ACC).items()})
    add("roster", None, "stop", {k: v for k, v in trust_document_faults(ROS).items()})
    # Typed fields.
    def hull_rec(x, c, **kw):
        rec = {"excluded": c, "journal_available": True}
        rec.update(kw)
        x.put(HULL, {"members": {"a": {t.FIELD: rec}}})
    add("hull", "hull-p2", "member", {
        "members-list": lambda x, c: x.put(HULL, {"members": [{"a": {}}]}),
        "member-missing": lambda x, c: x.put(HULL, {"members": {"zz": {}}}),
        "field-missing": lambda x, c: x.put(HULL, {"members": {"a": {}}}),
        "excluded-int": lambda x, c: hull_rec(x, int(c)), "excluded-str": lambda x, c: hull_rec(x, str(c)),
        "excluded-null": lambda x, c: hull_rec(x, None), "excluded-missing": lambda x, c: x.put(HULL, {"members": {"a": {t.FIELD: {"journal_available": True}}}}),
        "ja-false": lambda x, c: hull_rec(x, c, journal_available=False), "ja-int": lambda x, c: hull_rec(x, c, journal_available=1),
        "ja-missing": lambda x, c: x.put(HULL, {"members": {"a": {t.FIELD: {"excluded": c}}}})})

    def sp(x, member, request):
        x.put(SPANS, {"spans": {"a": {"member": member, "request": request}}})
    M, R = SPAN["member"], SPAN["request"]
    add("spans", "request-end-p1", "member", {
        "spans-list": lambda x, c: x.put(SPANS, {"spans": []}), "member-missing": lambda x, c: x.put(SPANS, {"spans": {}}),
        "record-list": lambda x, c: x.put(SPANS, {"spans": {"a": [M, R]}}),
        "request-field-missing": lambda x, c: x.put(SPANS, {"spans": {"a": {"member": M}}}),
        "member-field-missing": lambda x, c: x.put(SPANS, {"spans": {"a": {"request": R}}}),
        "member-null-request-present": lambda x, c: sp(x, None, R),
        "request-len3": lambda x, c: sp(x, M, R + [1]), "stamp-float": lambda x, c: sp(x, [20.0 * NS, M[1]], R),
        "stamp-bool": lambda x, c: sp(x, M, [True, R[1]]), "stamp-str": lambda x, c: sp(x, M, [R[0], str(R[1])]),
        "stamp-negative": lambda x, c: sp(x, [-1, M[1]], R),
        # producer invariants (member_spans): member[0] <= request[0] <= request[1] <= member[1]
        "request-inverted": lambda x, c: sp(x, M, [R[1], R[0]]),
        "request-end-after-member-end": lambda x, c: sp(x, M, [R[0], 120 * NS]),
        "request-start-before-member-start": lambda x, c: sp(x, M, [10 * NS, R[1]]),
        "member-inverted": lambda x, c: sp(x, [M[1], M[0]], R)})
    add("seal", "request-end-p1", "member", {
        "field-missing": lambda x, c: x.put(SEAL, {"hazards": {"thermal": {"continuous": {"journal": {}}}}}),
        "journal-null": lambda x, c: x.put(SEAL, {"hazards": {"thermal": {"continuous": {"journal": None}}}}),
        "sha-int": lambda x, c: x.seal(5), "sha-empty": lambda x, c: x.seal(""), "sha-differs": lambda x, c: x.seal("0" * 64),
        "sha-uppercase": lambda x, c: x.seal(hashlib.sha256(x.journal.read_bytes()).hexdigest().upper())})

    def rows_without_level(x, c):
        rows = x.journal_rows()
        for row in rows:
            row["values"].pop("level", None)
        x.write_journal(rows)

    def rows_wrong_level(x, c):
        rows = x.journal_rows()
        for row in rows:
            row["values"]["level"] = {}
        x.write_journal(rows)

    def rows_all_errors(x, c):
        rows = x.journal_rows()
        for row in rows:
            row["error"] = {"type": "read_failed"}
        x.write_journal(rows)

    def rows_all_zero(x, c):
        rows = x.journal_rows()
        for row in rows:
            row["values"]["level"] = 0
        x.write_journal(rows)  # sealed, usable, and contradicts a registered exclusion

    add("journal", "request-end-p1", "member", {
        "absent": lambda x, c: x.journal.unlink(), "directory": lambda x, c: (x.journal.unlink(), x.journal.mkdir()),
        "appended-after-seal": lambda x, c: x.journal.write_bytes(x.journal.read_bytes() + b"\n"),
        "sealed-not-json": lambda x, c: (x.journal.write_text("{bad\n"), x.seal()),
        "sealed-empty": lambda x, c: (x.journal.write_text(""), x.seal()),
        "sealed-missing-level": rows_without_level, "sealed-wrong-level": rows_wrong_level,
        "sealed-all-errors": rows_all_errors, "sealed-all-zero": rows_all_zero})
    want = lambda x: 2 if x.mode == "hull-p2" else 1
    add("plan", None, "member", {
        "no-bytes_pass": lambda x, c: x.put(PLAN, {"blinding_group": "bytes"}), "wrong": lambda x, c: x.put(PLAN, {"bytes_pass": 3 - want(x)}),
        "null": lambda x, c: x.put(PLAN, {"bytes_pass": None}), "str": lambda x, c: x.put(PLAN, {"bytes_pass": str(want(x))}),
        "bool": lambda x, c: x.put(PLAN, {"bytes_pass": True}), "float": lambda x, c: x.put(PLAN, raw=('{"bytes_pass": %d.0}' % want(x)).encode()),
        "second-tree-wrong": lambda x, c: x.put("sources/repo/alternate/thermal-fixture/plan_tree.json", {"bytes_pass": 3 - want(x)}),
        "decoy-only-with-pack_id": lambda x, c: ((x.a / PLAN).unlink(), x.put("sources/repo/decoy/plan_tree.json", {"bytes_pass": want(x)}),
                                                 x.put(ROS, {"pack_id": "bytes-s5-p2", "members": json.loads(x.text(ROS))["members"]})),
        "pack_id-names-wrong-tree": lambda x, c: (x.put("sources/repo/configs/campaigns/bytes-s5-p2/plan_tree.json", {"bytes_pass": 3 - want(x)}),
                                                  x.put(ROS, {"pack_id": "bytes-s5-p2", "members": json.loads(x.text(ROS))["members"]}))})
    ks["plan.pack_id-names-right-tree"] = (None, "trusted", lambda x, c: (
        (x.a / PLAN).unlink(), x.put("sources/repo/other/plan_tree.json", {"bytes_pass": 3 - want(x)}),
        x.put("sources/repo/configs/campaigns/bytes-s5-p2/plan_tree.json", {"bytes_pass": want(x)}),
        x.put(ROS, {"pack_id": "bytes-s5-p2", "members": json.loads(x.text(ROS))["members"]})))
    # W4-style structural faults inside acceptance and roster: global.
    def acc(x, rows):
        x.put(ACC, {"session_id": "s", "excluding": rows})
    code_row = {"scope": "member", "run_id": "a", "code": t.CODE}
    add("acceptance", None, "global", {
        "excluding-null": lambda x, c: acc(x, None), "excluding-object": lambda x, c: acc(x, {"a": 1}),
        "row-not-object": lambda x, c: acc(x, [code_row, "x"]), "row-run_id-missing": lambda x, c: acc(x, [{"scope": "member", "code": t.CODE}]),
        "row-run_id-list": lambda x, c: acc(x, [{"scope": "member", "run_id": ["a"], "code": t.CODE}]),
        "row-ghost-run": lambda x, c: acc(x, json.loads(x.text(ACC))["excluding"] + [{"scope": "member", "run_id": "ghost", "code": t.CODE}])})

    def ros(x, members):
        x.put(ROS, {"pack_id": "thermal-fixture", "members": members})
    add("roster", None, "global", {
        "run_id-missing": lambda x, c: ros(x, [{"kind": "science", "units": []}, {"run_id": "r", "kind": "reference", "units": []}]),
        "run_id-int": lambda x, c: ros(x, [{"run_id": 5, "kind": "science", "units": []}, {"run_id": "r", "kind": "reference", "units": []}]),
        "units-null": lambda x, c: ros(x, [{"run_id": "a", "kind": "science", "units": None}, {"run_id": "r", "kind": "reference", "units": []}]),
        "unit-missing-cell_id": lambda x, c: ros(x, [{"run_id": "a", "kind": "science", "units": [{"stratum": "quad", "unit_id": "u"}]}, {"run_id": "r", "kind": "reference", "units": []}])})
    add("roster", None, "stop", {
        "members-missing": lambda x, c: x.put(ROS, {}), "members-dict": lambda x, c: x.put(ROS, {"members": {"a": {}}}),
        "member-not-object": lambda x, c: ros(x, ["a", "r"])})
    add("acceptance", None, "global", {"excluding-missing": lambda x, c: x.put(ACC, {"session_id": "s"})})
    return ks


def trust_run_cell(mode, present, agrees, kind, cls, mut, n, base):
    candidate = present if agrees else not present
    x = TrustArchive(base / f"c{n}", mode, present, candidate)
    mut(x, candidate)
    out = x.root / "out"
    p = subprocess.run([sys.executable, str(SCRIPT), mode, str(x.a), str(out)], capture_output=True, text=True)
    tail = ((p.stdout + p.stderr).strip().splitlines() or [""])[-1][:110]
    mutable = present if mode == "request-end-p1" else not present
    if cls == "stop" or (cls == "trusted" and mode == "request-end-p1" and candidate and not present):
        return p.returncode == 2 and not out.exists(), f"exit={p.returncode} {tail}"
    if p.returncode != 0:
        return False, f"exit={p.returncode} {tail}"
    r = json.loads(p.stdout)
    st = {m["run_id"]: m["status"] for m in r["member_statuses"] if m["run_id"] is not None}
    rows = json.loads((out / "derived/b6-acceptance.json").read_bytes()).get("excluding")
    codes = {row["code"] for row in (rows if isinstance(rows, list) else []) if isinstance(row, dict) and "code" in row}
    a_status = next((m["status"] for m in r["member_statuses"] if m["run_id"] in ("a", 5, None)), "")
    if cls == "trusted":
        changed = mutable and not agrees
        exp = ("evaluated" if changed else "equals registered line", {t.CODE} if (candidate if changed else present) else set(), not changed)
    elif cls == "member":
        exp = ("not defined (" if mutable else "equals registered line", {t.CODE} if present else set(), not mutable)
    else:
        # A global fault keeps the acceptance byte for byte (its rows may be the fault itself).
        exp = ("not defined (", None, False)
        codes = None if (out / ACC).read_bytes() == (x.a / ACC).read_bytes() else "changed"
    ok = (a_status.startswith(exp[0]) and codes == exp[1] and r["equals_registered_line"] == exp[2]
          and st.get("r") == "equals registered line")
    shown = "acceptance-unchanged" if codes is None else codes if isinstance(codes, str) else sorted(codes)
    return ok, f"a={a_status!r} codes={shown} eq={r['equals_registered_line']}"



class ProducerTrustTests(unittest.TestCase):
    def test_generated_684_cells_real_cli(self):
        cells = 0
        with tempfile.TemporaryDirectory() as tmp:
            for kind, (only, cls, mutate) in trust_kinds().items():
                for mode in ("hull-p2", "request-end-p1"):
                    if only and only != mode:
                        continue
                    for present in (False, True):
                        for agrees in (False, True):
                            cells += 1
                            with self.subTest(kind=kind, mode=mode, present=present, agrees=agrees):
                                ok, detail = trust_run_cell(mode, present, agrees, kind, cls, mutate, cells, Path(tmp))
                                self.assertTrue(ok, detail)
        self.assertEqual(cells, 684)

    def cli(self, archive, name='out', mode='hull-p2', export=None):
        out = archive.root / name
        args = [sys.executable, t.__file__, mode, str(archive.a), str(out)]
        if export:
            args.extend(['--export', str(export)])
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), out

    def test_lexer_break_cases_cli_and_blinding(self):
        # Every malformed value lies in an unconsumed sibling of intact evidence.
        bad = ['01', '.5', '1.', '+1', 'NaN', 'Infinity', '0x10',
               '"control\x00"', '"control\n"', r'"\x20"', r'"\u12xz"', r'"\ud800"',
               r'"\udc00"', r'"\ud800x"', r'"\ud800\u0000"']
        texts = ['{"members":{"a":{"' + t.FIELD + '":{"excluded":true,"journal_available":true}}},"unused":' + value + '}'
                 for value in bad]
        valid = '{"members":{"a":{"' + t.FIELD + '":{"excluded":true,"journal_available":true}}}}'
        texts += ['\ufeff' + valid, valid + '{}', valid + '\u00a0',
                  valid[:-1] + ',"unused":{"a":{"x":1,"x":2}}}',
                  valid[:-1] + r',"unused":{"a":1,"\u0061":2}}']
        with tempfile.TemporaryDirectory() as tmp:
            for index, raw in enumerate(texts):
                with self.subTest(raw=repr(raw)):
                    archive = TrustArchive(Path(tmp) / str(index), 'hull-p2', False, True)
                    archive.put(HULL, raw=raw.encode())
                    record, out = self.cli(archive)
                    self.assertEqual(record['changes'], [])
                    self.assertEqual(record['member_statuses'][0]['status'], 'not defined (hull assessment unavailable)')
                    self.assertFalse(record['equals_registered_line'])
                    self.assertEqual((out / ACC).read_bytes(), (archive.a / ACC).read_bytes())
            # The same lexical rule protects acceptance, roster, plan, spans, seal,
            # sidecar and both controls through their validators (matrix + below).
            for raw in texts:
                for validate in (t.document, t.validate_record, t.validate_manifest):
                    with self.assertRaises(ValueError):
                        validate(raw)
                self.assertIsNotNone(t.validate_sidecar(raw)[1])
            # A valid million-deep unused value must also survive navigation past it.
            archive = TrustArchive(Path(tmp) / 'deep', 'hull-p2', False, True)
            archive.put(HULL, raw=('{"unused":' + '[' * 10**6 + '0' + ']' * 10**6 + ',' + valid[1:]).encode())
            record, _ = self.cli(archive)
            self.assertEqual(record['member_statuses'][0]['status'], 'evaluated')
            self.assertEqual(record['changes'][0]['action'], 'added')
            # Decode neither retained measurement values nor unknown non-key strings.
            archive = TrustArchive(Path(tmp) / 'splice', 'request-end-p1', True, False)
            row = r'{"scope":"window","code":"w","rail_mw":6666.750,"opaque":"\ud83d\ude00"}'
            archive.put(ACC, raw=('{"session_id":"s","energy_j":7777.123456789e3,"excluding":[' + row +
                ',{"scope":"member","run_id":"a","code":"' + t.CODE + '"}]}').encode())
            real_loads = json.loads
            def guarded(raw, *args, **kwargs):
                raw = raw.decode() if isinstance(raw, bytes) else raw
                self.assertNotIn('6666.750', raw)
                self.assertNotIn('7777.123456789e3', raw)
                self.assertNotIn('ud83d', raw)
                return real_loads(raw, *args, **kwargs)
            with patch.object(t.json, 'loads', side_effect=guarded):
                record = t.transform('request-end-p1', archive.a, archive.root / 'spliced')
            raw = (archive.root / 'spliced' / ACC).read_text()
            self.assertIn(row, raw)
            self.assertIn('7777.123456789e3', raw)
            self.assertEqual(record['changes'][0]['action'], 'removed')

    def test_span_invariant_edges_real_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases = [('equal', [20 * NS, 100 * NS], [20 * NS, 100 * NS], True, 'equals registered line'),
                     ('zero-request', [20 * NS, 100 * NS], [40 * NS, 40 * NS], True, 'evaluated'),
                     ('zero-stamp', [0, 100 * NS], [0, 80 * NS], True, 'evaluated'),
                     ('large-stamp', [0, 2**63], [0, 2**63], True, 'equals registered line'),
                     ('null-request', [20 * NS, 100 * NS], None, True, 'equals registered line'),
                     ('null-both', None, None, True, 'not defined ('),
                     ('null-member', None, [40 * NS, 80 * NS], True, 'not defined ('),
                     ('inverted-null-request', [100 * NS, 20 * NS], None, True, 'not defined (')]
            for name, member, request, present, expected in cases:
                with self.subTest(name=name):
                    archive = TrustArchive(Path(tmp) / name, 'request-end-p1', present, False)
                    archive.put(SPANS, {'spans': {'a': {'member': member, 'request': request}}})
                    record, _ = self.cli(archive, mode='request-end-p1')
                    self.assertTrue(record['member_statuses'][0]['status'].startswith(expected), record)
                    self.assertEqual(bool(record['changes']), expected == 'evaluated')

    def test_pack_identity_edges_real_cli(self):
        cases = ('missing', 'int', 'slash', 'backslash', 'dotdot', 'two-pack-trees', 'fallback-only', 'decoy-only', 'other-pack')
        with tempfile.TemporaryDirectory() as tmp:
            for name in cases:
                with self.subTest(name=name):
                    archive = TrustArchive(Path(tmp) / name, 'hull-p2', False, True)
                    roster = json.loads(archive.text(ROS))
                    if name == 'missing':
                        roster.pop('pack_id')
                    elif name in ('int', 'slash', 'backslash', 'dotdot'):
                        roster['pack_id'] = {'int': 1, 'slash': 'a/b', 'backslash': 'a\\b', 'dotdot': 'a..b'}[name]
                    elif name == 'two-pack-trees':
                        archive.put('sources/repo/elsewhere/thermal-fixture/plan_tree.json', {'bytes_pass': 2})
                    elif name in ('fallback-only', 'decoy-only'):
                        (archive.a / PLAN).unlink()
                        archive.put('sources/pack/plan_tree.json' if name == 'fallback-only' else 'sources/repo/decoy/plan_tree.json', {'bytes_pass': 2})
                    else:
                        archive.put('sources/repo/other/plan_tree.json', {'bytes_pass': 1})
                    archive.put(ROS, roster)
                    record, _ = self.cli(archive)
                    self.assertEqual(record['member_statuses'][0]['status'],
                                     'evaluated' if name == 'other-pack' else 'not defined (pass mismatch)')

    def test_sidecar_never_stops_and_csv_grammar(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, raw in enumerate((b'\xff', b'{}{}', b'{"blinding":{"withheld":{"path":1}}}', b'{"blinding":{"withheld":{"path":"\\u0000"}}}', b'{}')):
                archive = TrustArchive(Path(tmp) / str(index), 'hull-p2', False, True)
                export = archive.root / 'export'
                export.mkdir()
                (export / 's.runs.csv').write_text('run_id,exclusion_codes\nr,\n')
                (export / 's.session.json').write_bytes(raw)
                record, out = self.cli(archive, export=export)
                self.assertEqual(record['member_statuses'][0]['status'], 'not defined (changed member absent from export)')
                self.assertEqual((out / 'export/s.session.json').read_bytes(), raw)
            archive = TrustArchive(Path(tmp) / 'unreadable', 'hull-p2', False, True)
            export = archive.root / 'export'
            export.mkdir()
            (export / 's.runs.csv').write_text('run_id,exclusion_codes\nr,\n')
            sidecar = export / 's.session.json'
            sidecar.write_text('{}')
            sidecar.chmod(0)
            try:
                record, _ = self.cli(archive, export=export)
                self.assertEqual(record['member_statuses'][0]['status'], 'not defined (changed member absent from export)')
            finally:
                sidecar.chmod(0o644)
        for raw in ('run_id,exclusion_codes\na,b"c\n', 'run_id,exclusion_codes\na,"b"x\n'):
            self.assertIsNotNone(t.validate_export(raw)[1])

    def test_verify_roots_and_directory_record_cli(self):
        import os
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            archive = TrustArchive(Path(tmp), 'hull-p2', False, True)
            _, out = self.cli(archive)
            # Relative links and more than one recorded archive root are structural.
            for path in out.rglob('*'):
                if path.is_symlink():
                    target = path.resolve()
                    path.unlink()
                    path.symlink_to(os.path.relpath(target, path.parent))
            other = archive.root / 'other'
            (other / 'payload').mkdir(parents=True)
            (other / 'payload/one').write_text('opaque')
            (out / 'payload').mkdir()
            (out / 'payload/one').symlink_to(other / 'payload/one')
            self.assertIn(archive.a.resolve(), t.linked_roots(out))
            self.assertIn(other.resolve(), t.linked_roots(out))
            inside = archive.a / 'view'
            shutil.copytree(out, inside, symlinks=True)
            # Make copied relative links point to the same archived targets.
            for path in inside.rglob('*'):
                if path.is_symlink():
                    relative = path.relative_to(inside)
                    target = (out / relative).resolve()
                    path.unlink()
                    path.symlink_to(os.path.relpath(target, path.parent))
            (archive.a / 'renamed').write_text('opaque')
            path = inside / HULL
            path.unlink()
            path.symlink_to(archive.a / 'renamed')
            record = inside / 'thermal_line.json'
            record.chmod(0o644)
            record.write_text('{"source_sha256": []}')
            before = {str(p): p.read_bytes() for p in archive.a.rglob('*') if p.is_file()}
            result = subprocess.run([sys.executable, t.__file__, 'verify', str(inside)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"records.thermal_view_changed": true', result.stdout)
            self.assertEqual(before, {str(p): p.read_bytes() for p in archive.a.rglob('*') if p.is_file()})
            record = out / 'thermal_line.json'
            record.unlink()
            record.mkdir()
            result = subprocess.run([sys.executable, t.__file__, 'verify', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"records.thermal_view_changed": true', result.stdout)
            self.assertTrue(record.is_dir())

    def test_verify_control_values_stay_opaque(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = TrustArchive(Path(tmp), 'hull-p2', False, True)
            _, out = self.cli(archive)
            path = out / 'thermal_line.json'
            path.chmod(0o644)
            raw = path.read_text()
            retained = '"opaque_energy":7777.123456789e3'
            path.write_text(raw[:-2] + ',\n' + retained + '\n}\n')
            real_loads = json.loads
            def guarded(raw, *args, **kwargs):
                value = raw.decode() if isinstance(raw, bytes) else raw
                self.assertNotIn('7777.123456789e3', value)
                return real_loads(raw, *args, **kwargs)
            with patch.object(t.json, 'loads', side_effect=guarded):
                self.assertEqual(t.verify(out), [])
            self.assertIn(retained, path.read_text())
            # Verify's own control documents receive the same lexical validation.
            data = json.loads(path.read_text())
            for name in ('thermal_line.json', 'view_manifest.json'):
                control = out / name
                original = control.read_bytes()
                control.chmod(0o644)
                control.write_bytes(original + b'{}')
                if name == 'view_manifest.json':
                    data['view_manifest_sha256'] = hashlib.sha256(control.read_bytes()).hexdigest()
                    path.chmod(0o644)
                    path.write_text(json.dumps(data))
                different = t.verify(out)
                self.assertIn(name, different)
                control.chmod(0o644)
                control.write_bytes(original)

    def test_consumed_identity_types_are_records_faults(self):
        with tempfile.TemporaryDirectory() as tmp:
            faults = [('scope', None), ('scope', 1), ('scope', True), ('scope', []),
                      ('run_id', 1), ('run_id', []), ('run_id', float('inf'))]
            for index, (field, value) in enumerate(faults):
                with self.subTest(field=field, value=value):
                    archive = TrustArchive(Path(tmp) / str(index), 'hull-p2', False, True)
                    if field == 'scope':
                        row = {'scope': value, 'run_id': 'a', 'code': t.CODE}
                        if value is None:
                            row.pop('scope')
                        archive.put(ACC, {'excluding': [row]})
                        reason = 'exclusion row missing scope'
                    else:
                        roster = json.loads(archive.text(ROS))
                        roster['members'][0]['run_id'] = value
                        raw = json.dumps(roster).replace('Infinity', '1e309')
                        archive.put(ROS, raw=raw.encode())
                        reason = 'roster member missing run_id'
                    record, out = self.cli(archive)
                    self.assertEqual(record['member_statuses'][0]['status'], 'not defined (' + reason + ')')
                    self.assertEqual(record['changes'], [])
                    self.assertFalse(record['equals_registered_line'])
                    t.validate_record((out / 'thermal_line.json').read_text())

    def test_null_request_fallback_still_checks_journal_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            for present in (False, True):
                archive = TrustArchive(Path(tmp) / str(present), 'request-end-p1', present, False)
                archive.put(SPANS, {'spans': {'a': {'member': SPAN['member'], 'request': None}}})
                # Re-seal a journal contradicting the registered hull code.
                fixtures.thermal_journal(range(0, 126, 5), set() if present else {90}).dump(archive.journal)
                archive.seal()
                record, out = self.cli(archive, mode='request-end-p1')
                self.assertEqual(record['changes'], [])
                self.assertEqual(record['member_statuses'][0]['status'],
                                 'not defined (journal does not reproduce the registered hull decision)' if present else 'equals registered line')
                self.assertIn({'run_id': 'a', 'code': 'records.thermal_hull_replay_disagrees'}, record['notices'])
                self.assertEqual((out / ACC).read_bytes(), (archive.a / ACC).read_bytes())

    def test_journal_lines_use_the_same_lexer_and_blinding(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, extra in enumerate((',"unused":NaN', ',"unused":1,"unused":2', r',"a":1,"\u0061":2')):
                archive = TrustArchive(Path(tmp) / str(index), 'request-end-p1', True, True)
                lines = archive.journal.read_text().splitlines()
                archive.journal.write_text(''.join((line[:-1] + extra + '}' if json.loads(line)['values']['level'] else line) + '\n' for line in lines))
                archive.seal()
                record, _ = self.cli(archive, mode='request-end-p1')
                self.assertEqual(record['member_statuses'][0]['status'], 'not defined (journal line not producer output)')
                self.assertEqual(record['changes'], [])
            archive = TrustArchive(Path(tmp) / 'opaque', 'request-end-p1', True, False)
            lines = archive.journal.read_text().splitlines()
            archive.journal.write_text(''.join(line[:-1] + ',"energy":6666.750}\n' for line in lines))
            archive.seal()
            loads = json.loads
            def guarded(raw, *args, **kwargs):
                raw = raw.decode() if isinstance(raw, bytes) else raw
                self.assertNotIn('6666.750', raw)
                return loads(raw, *args, **kwargs)
            with patch.object(t.json, 'loads', side_effect=guarded):
                record = t.transform('request-end-p1', archive.a, archive.root / 'out')
                bookkeeping = json.dumps({'schema': t.h.JOURNAL_SCHEMA, 'module': 'thermal',
                    'kind': sorted(t.h.BOOKKEEPING_KINDS)[0]})[:-1] + ',"energy":6666.750}\n'
                self.assertEqual(t.journal_readings(bookkeeping.encode()), ([], 0))
            self.assertEqual(record['member_statuses'][0]['status'], 'evaluated')
            self.assertEqual(record['changes'][0]['action'], 'removed')


class RoundSixTests(unittest.TestCase):
    def test_production_json_divergence_never_restores(self):
        variants = {
            'dup-level': lambda s: s.replace('"level":1', '"level":0,"level":1'),
            'nan-sibling': lambda s: s[:-1] + ',"x":NaN}',
            'lone-surrogate': lambda s: s[:-1] + r',"x":"\ud800"}',
            'bom': lambda s: '\ufeff' + s,
            'utf16': lambda s: s,
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, mutate in variants.items():
                with self.subTest(name=name):
                    x = TrustArchive(Path(tmp) / name, 'request-end-p1', True, False)
                    fixtures.thermal_journal(range(0, 126, 5), {80, 95}).dump(x.journal)
                    lines = x.journal.read_text().splitlines()
                    data = []
                    for line in lines:
                        if json.loads(line)['finished']['monotonic_ns'] == 80 * fixtures.NS:
                            line = mutate(line)
                            data.append(line.encode('utf-16') if name == 'utf16' else line.encode())
                        else:
                            data.append(line.encode())
                    x.journal.write_bytes(b'\n'.join(data) + b'\n')
                    x.seal()
                    record = t.transform('request-end-p1', x.a, x.root / 'out')
                    self.assertEqual(record['member_statuses'][0]['status'],
                                     'not defined (journal line not producer output)')
                    self.assertEqual(record['restored_members'], [])
                    self.assertEqual(record['changes'], [])
                    self.assertFalse(any(n['code'] == 'records.monitor_line_malformed' for n in record['notices']))

    def test_truncated_line_keeps_malformed_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            x = TrustArchive(Path(tmp), 'request-end-p1', True, False)
            with x.journal.open('ab') as stream:
                stream.write(b'{"truncated":')
            x.seal()
            record = t.transform('request-end-p1', x.a, x.root / 'out')
            self.assertEqual(record['restored_members'], ['a'])
            self.assertIn({'code': 'records.monitor_line_malformed'}, record['notices'])

    def test_duplicate_roster_identity_is_global_fault(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ('hull-p2', 'request-end-p1'):
                for kind in ('science', 'reference'):
                    x = TrustArchive(Path(tmp) / (mode + kind), mode, mode == 'request-end-p1', True)
                    roster = json.loads(x.text(ROS))
                    duplicate = dict(roster['members'][0], kind=kind)
                    roster['members'].append(duplicate)
                    roster['members'].append(dict(duplicate, run_id='b', kind='science'))
                    x.put(ROS, roster)
                    record = t.transform(mode, x.a, x.root / 'out')
                    statuses = {m['run_id']: m['status'] for m in record['member_statuses']}
                    for run in ('a', 'b'):
                        self.assertEqual(statuses[run], 'not defined (roster repeated run_id)')
                    self.assertEqual(record['changes'], [])
                    self.assertEqual((x.root / 'out' / ACC).read_bytes(), (x.a / ACC).read_bytes())

    def test_export_session_component_and_writer_containment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sentinel = root / 'escape.withheld.csv'
            sentinel.write_bytes(b'SENTINEL')
            for i, session in enumerate(('../escape', '../../../escape', '/escape', r'a\b', '.', '..', 'a\x00b', '')):
                x = TrustArchive(root / str(i), 'hull-p2', False, True)
                acc = json.loads(x.text(ACC)); acc['session_id'] = session; x.put(ACC, acc)
                export = x.root / 'export'; export.mkdir()
                result = subprocess.run([sys.executable, t.__file__, 'hull-p2', str(x.a),
                                         str(x.root / 'out'), '--export', str(export)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(record['member_statuses'][0]['status'], 'not defined (unsafe export session_id)')
                self.assertEqual(record['changes'], [])
                self.assertEqual(sentinel.read_bytes(), b'SENTINEL')
                self.assertFalse((x.root / 'out/export').exists())
            out = root / 'guard'; out.mkdir()
            for path in (out / '../escape.withheld.csv', root / 'escape.withheld.csv'):
                with self.assertRaisesRegex(ValueError, 'outside output|not in the subpath'):
                    t.write_copy(path, 'changed', out)
            link = out / 'leaf'; link.symlink_to(sentinel)
            with self.assertRaisesRegex(ValueError, 'outside output'):
                t.write_copy(link, 'changed', out)
            self.assertEqual(sentinel.read_bytes(), b'SENTINEL')

    def test_huge_level_is_unavailable_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            for present in (False, True):
                for fallback in (False, True):
                    x = TrustArchive(Path(tmp) / f'{present}-{fallback}', 'request-end-p1', present, False)
                    rows = x.journal_rows()
                    rows[0]['values']['level'] = 10**1000
                    x.write_journal(rows)
                    if fallback:
                        x.put(SPANS, {'spans': {'a': {'member': SPAN['member'], 'request': None}}})
                    result = subprocess.run([sys.executable, t.__file__, 'request-end-p1', str(x.a), str(x.root / 'out')], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    record = json.loads(result.stdout)
                    self.assertEqual(record['member_statuses'][0]['status'],
                                     'not defined (journal level conversion unavailable)' if present else 'equals registered line')
                    self.assertEqual(record['changes'], [])
                    self.assertFalse(any(n['code'] == 'records.thermal_hull_replay_disagrees' for n in record['notices']))

    def test_unknown_span_is_not_replay_disagreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            for present in (False, True):
                x = TrustArchive(Path(tmp) / str(present), 'request-end-p1', present, False)
                x.put(SPANS, {'spans': {'a': {'member': None, 'request': None}}})
                record = t.transform('request-end-p1', x.a, x.root / 'out')
                self.assertEqual(record['member_statuses'][0]['status'],
                                 'not defined (member span unavailable)' if present else 'equals registered line')
                self.assertEqual(record['changes'], [])
                self.assertFalse(any(n['code'] == 'records.thermal_hull_replay_disagrees' for n in record['notices']))

    def test_production_rejected_lines_keep_malformed_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            x = TrustArchive(Path(tmp), 'request-end-p1', True, False)
            clean = x.journal.read_bytes()
            line = clean.splitlines()[0]
            cases = [b'[]', b'null']
            limit = sys.get_int_max_str_digits()
            if limit:
                huge = b'1' * (limit + 1)
                cases.extend([line[:-1] + b',"unused":' + huge + b'}',
                              line[:-1] + b',"unused":0,"unused":' + huge + b'}'])
            for i, extra in enumerate(cases):
                x.journal.write_bytes(clean + extra + b'\n'); x.seal()
                expected, malformed = t.h.read_monitor_journal(x.journal, 'thermal')
                actual, tool_malformed = t.journal_readings(x.journal.read_bytes())
                projection = lambda rows: [(r.monotonic_ns, r.started_monotonic_ns, r.status,
                                             t.h._int(r.values.get('level'))) for r in rows]
                self.assertEqual(projection(actual), projection(expected))
                self.assertEqual((malformed, tool_malformed), (1, 1))
                record = t.transform('request-end-p1', x.a, x.root / str(i))
                self.assertEqual(record['restored_members'], ['a'])
