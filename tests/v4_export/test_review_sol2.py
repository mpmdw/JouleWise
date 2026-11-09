"""Independent seat-2 exporter witnesses. SYNTHETIC ONLY.

Every test asserts the required property; the five former expectedFailure markers were removed when the
exporter was fixed (F1-F5 of this seat). A red test is a regression.
The native fixture uses the repository's synthetic controller/harvest-off chain.
No real custody, hardware, model weights or network is used.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from scripts import export_v4_series as ex
from tests.v4_release import test_exporter_e2e as fixture


class TerminalAndReferenceWitnesses(unittest.TestCase):
    def test_terminal_result_must_belong_to_its_night_plan(self):
        """A stale GO result can have matching digests and exit code, but another plan_id."""
        result = ex.canonical(dict(schema=ex.RESULT_SCHEMA, plan_id='previous-window',
                                   verdict='GO', chain_exit_code=0))

        class Record:
            def source(self, name, *, json_value=True):
                return {'result': result, 'chain_exited': {'exit_code': 0},
                        'courier_sent': b'', 'plan': {'plan_id': 'current-window'}}[name]

        with tempfile.TemporaryDirectory(prefix='jw-sol2-terminal-') as tmp:
            root = Path(tmp)
            path = root / 'custody/night/result.json'
            path.parent.mkdir(parents=True)
            path.write_bytes(result)
            session = ex.Session(root, {'entries': {'custody/night/result.json': {
                'sha256': hashlib.sha256(result).hexdigest(), 'size': len(result)}}})
            with self.assertRaises(ex.Refused):
                ex.terminal_evidence(Record(), session, 'custody')

    def test_series_reference_requires_a_digest(self):
        """Runbook 6a.1 requires {path, sha256}, including R1/U3 registration inputs."""
        with tempfile.TemporaryDirectory(prefix='jw-sol2-reference-') as tmp:
            path = Path(tmp) / 'r1.json'
            path.write_bytes(b'{"qualified":true}\n')
            with self.assertRaises(ex.Refused):
                ex.read_ref_file({'path': str(path)}, 'r1_references_invalid')

    def test_series_reference_with_wrong_digest_refuses(self):
        with tempfile.TemporaryDirectory(prefix='jw-sol2-reference-') as tmp:
            path = Path(tmp) / 'r1.json'
            path.write_bytes(b'{}\n')
            with self.assertRaises(ex.Refused):
                ex.read_ref_file({'path': str(path), 'sha256': '0' * 64}, 'r1_references_invalid')

    def test_thermal_normalizer_projects_production_reading_rows(self):
        from joulewise.align.apple.thermal_desk import normalize_journal
        rows = [{'module': 'temperature', 'kind': 'reading', 'started': {'monotonic_ns': 17},
                 'finished': {'monotonic_ns': 23},
                 'values': {'sensors': {'fast': 40., 'slow': 38.}, 'status': {'os_level': 'nominal'}}},
                {'module': 'temperature', 'kind': 'session', 'ignored': True}]
        self.assertEqual(normalize_journal(rows), [dict(kind='sample', monotonic_ns=17,
            finished={'monotonic_after_ns': 23}, sensors={'fast': 40., 'slow': 38.},
            status={'os_level': 'nominal'})])

    def test_w1_contrast_stage_must_match_registered_ordinal(self):
        """A stale stage_id overrides the production a/b allocation in BOTH projections."""
        repo = Path(__file__).resolve().parents[2]
        allocation = json.loads((repo / 'configs/campaigns/align_v4/series/series_manifest.json').read_text())
        rows = json.loads((repo / 'configs/campaigns/align_v4/collection_plan.json').read_text())['members']
        _, normal = ex.build_roster('W1', rows, allocation)
        self.assertEqual(normal[5]['contrast']['stage'], 0)   # ordinal 6 is in first half (1..9)
        self.assertTrue(rows[5]['stage_id'].endswith('-a'))
        rows[5]['stage_id'] = rows[5]['stage_id'][:-1] + 'b'
        with self.assertRaises(ex.Refused):
            ex.build_roster('W1', rows, allocation)


@unittest.skipUnless(fixture.have_commits(), 'pinned synthetic producer commits unavailable')
class NativeCustodyWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-sol2-native-')
        cls.work = Path(cls.tmp.name)
        cls.config, cls.value = fixture.config_copy(cls.work)
        cls.prefix = Path(cls.value['export_root'])
        code, _, _, err = fixture.export(cls.config, 'W1#1')
        if code:
            raise AssertionError(err)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.case_tmp = tempfile.TemporaryDirectory(prefix='jw-sol2-case-')
        self.addCleanup(self.case_tmp.cleanup)
        self.case = Path(self.case_tmp.name)
        self.value = copy.deepcopy(self.value)
        self.root = self.case / 'export'
        shutil.copytree(self.prefix, self.root)
        self.value['export_root'] = str(self.root)
        self.repo = self.case / 'records'
        shutil.copytree(Path(self.value['records_repo']), self.repo)
        self.value['records_repo'] = str(self.repo)

    def export(self, attempt):
        path = self.case / 'config.json'
        path.write_text(json.dumps(self.value))
        return fixture.export(path, attempt)

    def entry(self, attempt):
        return next(w for w in self.value['windows'] if w['attempt_id'] == attempt)

    def mutate_record(self, attempt, mutate):
        entry = self.entry(attempt)
        record = json.loads(fixture.native_series.git(self.repo, 'show',
                                                     entry['record_commit'] + ':' + entry['record_path']))
        mutate(record)
        path = self.repo / 'review/record.json'
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(ex.canonical(record))
        fixture.native_series.git(self.repo, 'add', 'review/record.json')
        fixture.native_series.git(self.repo, 'commit', '-qm', 'synthetic review mutation')
        entry.update(record_commit=fixture.native_series.git(self.repo, 'rev-parse', 'HEAD'),
                     record_path='review/record.json')
        return record

    def test_all_null_captures_cannot_hide_manifest_bound_plists(self):
        """An accidentally empty capture census must not erase a captured window."""
        def change(record):
            record['captures'] = dict.fromkeys(record['captures'])
            record['raw_evidence'] = [record['finalized_manifest']]

        record = self.mutate_record('C1#1', change)
        manifest = json.loads(fixture.native_series.git(self.repo, 'show',
            self.entry('C1#1')['record_commit'] + ':' + record['finalized_manifest']['path']))
        plists = [p for p in manifest['entries'] if p.endswith('/raw/powermetrics.plist')]
        self.assertEqual(len(plists), 22)   # committed evidence already contradicts the census
        code, out, _, err = self.export('C1#1')
        self.assertEqual((code, out.get('status')), (2, 'refused'), err)

    def test_incremental_export_must_bind_prior_state_to_configured_record(self):
        """A corrected committed W1 record is ignored when exporting the next window."""
        prior = json.loads((self.root / 'state/W1.json').read_text())
        self.mutate_record('W1#1', lambda r: r.update(review_should_refuse=True))
        # A fresh read of the NEW configured record refuses an unknown contract key.
        with self.assertRaises(ex.Refused) as caught:
            ex.open_record(self.value, self.entry('W1#1'))
        self.assertEqual(caught.exception.code, 'unknown_contract_key')
        self.assertNotEqual(prior['record']['commit'], self.entry('W1#1')['record_commit'])
        code, out, _, err = self.export('C1#1')
        self.assertEqual((code, out.get('status')), (2, 'refused'), err)

    def test_zero_capture_retry_and_prefix_reexport_remain_deterministic(self):
        for attempt in ('C1#1', 'C2#1', 'C2#2'):
            code, _, _, err = self.export(attempt)
            self.assertEqual(code, 0, err)
        before = fixture.inventory(self.root)
        code, out, _, err = self.export('C2#2')
        self.assertEqual(code, 0, err)
        self.assertEqual(out['windows'][0]['outcome'], 'unchanged')
        after = fixture.inventory(self.root)
        self.assertEqual({k: v for k, v in before.items() if k != 'state/timings.jsonl'},
                         {k: v for k, v in after.items() if k != 'state/timings.jsonl'})

    def test_independent_fresh_w1_export_is_byte_identical(self):
        before = fixture.inventory(self.root)
        self.value['export_root'] = str(self.case / 'fresh-export')
        code, _, _, err = self.export('W1#1')
        self.assertEqual(code, 0, err)
        after = fixture.inventory(Path(self.value['export_root']))
        self.assertEqual({k: v for k, v in before.items() if k != 'state/timings.jsonl'},
                         {k: v for k, v in after.items() if k != 'state/timings.jsonl'})

    @unittest.skipUnless(sys.version_info[:2] == (3, 13), 'release engine identity requires CPython 3.13')
    def test_a27_scored_c_sabotage_battery_rows_are_sealed(self):
        """Real producer battery arrays must not bypass the engine's member seals."""
        code, _, _, err = self.export('C1#1')
        self.assertEqual(code, 0, err)
        code, verdict = fixture.support.run_engine(self.root, workers=1, through_window='C1')
        self.assertEqual(code, 0, verdict)
        fill = json.loads((self.root / 'engine-out-cal/fill.json').read_text())
        window = next(w for w in fill['windows'] if w['window'] == 'C1')
        sabotage = {'align-v4-c1-e09', 'align-v4-c1-e18'}
        primary = [r for r in window['eligibility'] if r['run_id'] in sabotage]
        self.assertEqual(len(primary), 2)
        self.assertTrue(all(r.get('status') == 'sealed' for r in primary))
        rows = [r for r in window['battery']['members'] if r['run_id'] in sabotage]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row.get('status'), 'sealed', row.keys())
            self.assertFalse({'soc_pct', 'charger_w', 'flags'} & set(row))

    def test_exported_member_hull_inputs_are_the_production_bytes(self):
        """Lead DC-span ruling (b) / engine de4a54db9: the whole-member DC hull is the production
        harvest.member_spans(metadata, events)['member'], derived by each build from the digest-bound bundle
        metadata.json and events.jsonl the export references. No span is exported (the engine refuses one)."""
        from joulewise.b5.harvest import member_spans
        raw = json.loads((self.root / 'engine/windows/W1/raw.json').read_text())
        members = [m for m in raw['members'] if m.get('dc_streams')]
        self.assertTrue(members)
        session = Path(self.entry('W1#1')['session_root'])
        for member in members:
            self.assertNotIn('member_span_ns', member)
            meta_raw = (self.root / member['metadata']['path']).read_bytes()
            events_raw = (self.root / member['events']['path']).read_bytes()
            self.assertEqual(hashlib.sha256(meta_raw).hexdigest(), member['metadata']['sha256'])
            self.assertEqual(hashlib.sha256(events_raw).hexdigest(), member['events']['sha256'])
            local = member['run_id'].partition(':')[2] or member['run_id']
            bundle = session / 'runs-parent/claim' / local
            self.assertEqual((bundle / 'metadata.json').read_bytes(), meta_raw)      # the custody bytes, unchanged
            self.assertEqual((bundle / 'events.jsonl').read_bytes(), events_raw)
            hull = member_spans(json.loads(meta_raw), [json.loads(line) for line in events_raw.splitlines() if line.strip()])
            self.assertEqual(list(hull['member']), member['battery']['spans']['member'])   # = the production hull
            episode = json.loads((self.root / member['episode']['path']).read_text())
            self.assertNotEqual(list(hull['member']), [episode['start_ns'], episode['end_ns']])
            # The recompute layout carries the same two files byte for byte.
            rec = self.root / 'recompute/windows/W1/members' / member['run_id']
            self.assertEqual((rec / 'metadata.json').read_bytes(), meta_raw)
            self.assertEqual((rec / 'events.jsonl').read_bytes(), events_raw)

if __name__ == '__main__':
    unittest.main()
