"""Exporter Sol seat 1 witnesses (reviewed at 6d0f9c731), kept as REQUIRED-PROPERTY tests. SYNTHETIC ONLY.

Each finding method asserts the required property (F1 producer session accepted, F2 custody-derived captures,
F3 landed windows rebound to the configured record, F4 series references require their digest); all are green
since the fixes. A red method is a regression.
The producer fixture is the branch's WP22/harvest-off native_series, never real
custody. Run this module alone with python3.13, TMPDIR=/private/tmp,
PYTHONNOUSERSITE=1, JW_B5_SYNTHETIC_ONLY=1 and JW_WP22_FULL=1.
No models, hardware, network, or home-directory custody are needed.
"""
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tests.align import synthetic_custody
from tests.v4_release import native_series, support
from scripts import export_v4_series as ex

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule
REPO = Path(__file__).absolute().parents[2]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def replace_bytes(path, raw):
    """Break a possible hard link before changing an isolated fixture copy."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.review-tmp')
    temp.write_bytes(raw)
    os.replace(temp, path)


def serial_battery(bundles, journal_path):
    """Same production join, serial to keep review CPU use small."""
    from joulewise.align.apple import v4_battery
    journal = v4_battery.load_journal(journal_path) if journal_path else ([], None, 1)
    return [v4_battery.bundle_evidence(bundle, journal) for bundle in bundles]


def production_series_state(root, slot='C1'):
    """Run the real session-state producer; stub only host/kit/admission work.

    In particular, do not hand-author v4_series (the existing native fixture
    does that and misses two keys).
    """
    from scripts import align_v4_session as session, align_v4_series as series
    root.mkdir()
    measurement, target = root / 'measurement', root / 'session'
    measurement.mkdir()
    target.mkdir()
    manifest_raw = native_series.MANIFEST.read_bytes()
    for rel, raw in ((series.MANIFEST, manifest_raw), (series.ADMISSION, b'{}')):
        path = measurement / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    with ExitStack() as stack:
        for obj, name, value in (
            (session, 'session_start_restore', {'action': 'none'}),
            (session.kit, 'generate', None),
            (series, 'load', json.loads(manifest_raw)),
            (series, 'require_admission', None),
            (series, 'generate', None),
            (session, 'series_ac_powermode', 0),
            (session.pilot, 'prepare', {'preparation_status': 'STAGED'}),
        ):
            stack.enter_context(patch.object(obj, name, return_value=value))
        state = session.prepare(measurement, target, window_id=slot)
    assert read(target / 'session.json')['v4_series'] == state['v4_series']
    return state['v4_series']


class DerivedFieldControls(unittest.TestCase):
    def test_identity_and_wp22_span_use_the_registered_bytes_and_first_g0(self):
        rows = [{'turn': 0, 'generation': {'prompt_token_ids': [2, 10], 'output_token_ids': [7]}},
                {'turn': 1, 'generation': {'prompt_token_ids': [2, 10, 7], 'output_token_ids': [8, 9]}}]
        self.assertEqual(ex.identity_sha256(rows), digest(b'[[[2,10],[7]],[[2,10,7],[8,9]]]'))
        self.assertEqual(ex.registered_span_ns({'start_ns': 30, 'end_ns': 90, 'hardware': {
            'thermal': {'intervals': [{'kind': 'G1', 'start_ns': 50}, {'kind': 'G0', 'start_ns': 10},
                                      {'kind': 'G0', 'start_ns': 20}]}}}), [10, 90])

    def test_every_manifest_bound_raw_type_refuses_changed_bytes(self):
        with tempfile.TemporaryDirectory(prefix='v4-sol1-digests-', dir='/private/tmp') as tmp:
            root = Path(tmp)
            for name in ('config.json', 'planned_config.json', 'collection_plan.json', 'terminal_result.json',
                         'hazards/meter/stream-000.jsonl', 'raw/powermetrics.plist',
                         'outputs/align_thermal.jsonl', 'hazards/monitor/battery.jsonl'):
                with self.subTest(name=name):
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b'original')
                    session = ex.Session(root, {'entries': {name: {'sha256': digest(b'original'), 'size': 8}}})
                    path.write_bytes(b'changed!')
                    for check in (session.read, session.verify_file):
                        with self.assertRaises(ex.Refused) as caught:
                            check(name)
                        self.assertEqual(caught.exception.code, 'digest_mismatch')


@unittest.skipUnless(support.have_commits(), 'pinned synthetic producer support unavailable')
class NativeCustodyWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='v4-export-sol1-', dir='/private/tmp')
        cls.work = Path(cls.tmp.name)
        supplied = os.environ.get('JW_V4_SOL1_SYNTHETIC_CONFIG')
        if supplied:
            config = Path(supplied).absolute()
            if not (config.is_relative_to('/private/tmp') or config.is_relative_to(REPO)):
                raise AssertionError('review fixtures must live in the checkout or /private/tmp')
        else:
            synth = support.synth_module()
            source = cls.work / 'native-source'
            source.mkdir()
            # A prefix is enough: W1, captured C1, and a genuinely empty C2.
            config, _ = native_series.build(source, synth, synth.FrameTemplate(n_tasks=0, seed=7, clusters=0),
                                            plan=native_series.default_plan()[:3])
        cls.value = read(config)
        # Work in our own records repo; never add review mutations to the shared fixture cache.
        cls.repo = cls.work / 'records'
        shutil.copytree(cls.value['records_repo'], cls.repo)
        cls.value['records_repo'] = str(cls.repo)
        cls.seed = cls.work / 'w1-prefix'
        cls.value['export_root'] = str(cls.seed)
        cls.config = cls.work / 'base.json'
        cls.config.write_bytes(ex.canonical(cls.value))
        with patch.object(ex, 'battery_evidence', serial_battery):
            ex.run(cls.config, ['W1#1'])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.tmp_case = tempfile.TemporaryDirectory(prefix='case-', dir=self.work)
        self.addCleanup(self.tmp_case.cleanup)
        self.case = Path(self.tmp_case.name)
        self.value = deepcopy(type(self).value)
        self.root = self.case / 'export'
        shutil.copytree(self.seed, self.root, copy_function=os.link)
        self.value['export_root'] = str(self.root)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(ex, 'battery_evidence', serial_battery))

    def run_export(self, *attempts):
        config = self.case / 'config.json'
        config.write_bytes(ex.canonical(self.value))
        return ex.run(config, list(attempts) if attempts else 'all')

    def entry(self, attempt):
        return next(w for w in self.value['windows'] if w['attempt_id'] == attempt)

    def mutate_record(self, attempt, mutate=lambda r: None, sources=None, finalized=None):
        entry = self.entry(attempt)
        git = lambda *args: native_series.git(self.repo, *args)
        record = json.loads(git('show', entry['record_commit'] + ':' + entry['record_path']))
        folder = 'review/' + self.case.name + '-' + attempt.replace('#', '-')

        def source(name, raw):
            rel = folder + '/' + name + '.json'
            replace_bytes(self.repo / rel, raw)
            return {'path': rel, 'sha256': digest(raw)}
        for name, raw in (sources or {}).items():
            record['sources'][name] = source(name, raw)
        if finalized is not None:
            # Finalized-manifest canonicalization has no trailing newline.
            record['finalized_manifest'] = source('finalized', json.dumps(
                finalized, sort_keys=True, separators=(',', ':')).encode())
        mutate(record)
        ref = source('record', ex.canonical(record))
        git('add', 'review')
        git('commit', '-qm', 'synthetic exporter review ' + attempt)
        entry.update(record_commit=git('rev-parse', 'HEAD'), record_path=ref['path'])
        return record

    def test_actual_prepare_session_is_accepted_by_the_exporter(self):
        """F1: production v4_series contains extra_sentinels/admission_sha256."""
        produced = production_series_state(self.case / 'producer')
        entry = self.entry('C1#1')
        old = Path(entry['session_root'])
        session = self.case / 'restored-air-session'
        shutil.copytree(old, session, copy_function=os.link)
        state = read(session / 'session.json')
        # Relocate the synthetic source before binding its new finalized manifest.
        state = json.loads(json.dumps(state).replace(str(old), str(session)))
        state['v4_series'] = produced
        replace_bytes(session / 'session.json', ex.canonical(state))
        night_plan = json.loads((session / 'custody/night_plan.json').read_bytes())
        night_plan['custody_root'] = str(session / 'custody')
        plan_raw = ex.canonical(night_plan)
        replace_bytes(session / 'custody/night_plan.json', plan_raw)
        record = json.loads(native_series.git(self.repo, 'show', entry['record_commit'] + ':' + entry['record_path']))
        finalized = json.loads(native_series.git(self.repo, 'show', entry['record_commit'] + ':' +
                                                record['finalized_manifest']['path']))
        finalized['source_root'] = str(session)
        for rel in ('session.json', 'custody/night_plan.json'):
            raw = (session / rel).read_bytes()
            finalized['entries'][rel].update(sha256=digest(raw), size=len(raw))
        # The relocation moves the custody root, so the watchdog's release latch (plan_id:custody_root:result
        # sha256, checked since F5) is rebound with it, consistently with the relocated night plan.
        result_raw = (session / 'custody/night/result.json').read_bytes()
        latch = f"{night_plan['plan_id']}:{night_plan['custody_root']}:{digest(result_raw)}"
        watchdog = ex.canonical({'released_terminal_windows': [latch]})
        self.mutate_record('C1#1', sources={'plan': plan_raw, 'watchdog_state': watchdog}, finalized=finalized)
        entry['session_root'] = str(session)
        try:
            result = self.run_export('C1#1')
        except ex.Refused as exc:
            self.fail(f'actual prepare() v4_series refused: {exc.code}: {exc.detail}; keys={sorted(produced)}')
        self.assertEqual(result['windows'][0]['captured'], 22)

    def test_all_null_capture_inventory_must_not_hide_finalized_plists(self):
        """F2: an all-null inventory must receive the same cross-check as a partial-null inventory."""
        def clear(record):
            record['captures'] = dict.fromkeys(record['captures'])
        record = self.mutate_record('C1#1', clear)
        finalized = json.loads(native_series.git(self.repo, 'show', self.entry('C1#1')['record_commit'] + ':' +
                                                record['finalized_manifest']['path']))
        self.assertEqual(sum(name.endswith('/raw/powermetrics.plist') for name in finalized['entries']), 22)
        # Keep session_root supplied: this is an operator inventory mistake, not a missing restore.
        try:
            self.run_export('C1#1')
        except ex.Refused:
            return
        engine = read(self.root / 'engine/windows/C1-z1/raw.json')['members']
        recompute = read(self.root / 'recompute/windows/C1-z1/window.json')['members']
        self.assertTrue(all(m['captured'] is False for m in engine + recompute))
        self.fail('both layouts silently exported 22 existing synthetic captures as empty C1-z1')

    def test_incremental_export_must_not_reuse_a_different_configured_w1_record(self):
        """F3: a fresh config must not silently select old final adjudication from the output root."""
        w1 = self.entry('W1#1')
        old_commit = w1['record_commit']
        record = json.loads(native_series.git(self.repo, 'show', old_commit + ':' + w1['record_path']))
        plan = json.loads(native_series.git(self.repo, 'show', old_commit + ':' + record['sources']['collection_plan']['path']))
        rid = plan['members'][4]['run_id']
        # This changes a scientific input, while preserving a valid completed final adjudication.
        exclusions = ex.canonical({'members_excluded': [{'run_id': rid, 'codes': ['member.runtime_failure']}]})
        self.mutate_record('W1#1', sources={'exclusions': exclusions})
        self.assertNotEqual(w1['record_commit'], old_commit)
        requested, _ = ex.open_record(self.value, w1)
        self.assertIsNone(requested.final_evidence(), 'the requested replacement record must itself be final')
        try:
            self.run_export('C1#1')
        except ex.Refused:
            return
        landed = read(self.root / 'state/W1.json')
        self.assertEqual(landed['record']['commit'], w1['record_commit'],
                         'incremental success ignored the configured W1 record and its changed exclusions')

    def test_series_reference_files_require_the_declared_digest(self):
        """F4: a missing SHA must not silently turn a pinned input into a path-only read."""
        for key in ('u3_bar', 'r1_references', 'registration_inputs'):
            with self.subTest(key=key):
                value = deepcopy(self.value)
                value[key].pop('sha256')
                with self.assertRaises(ex.Refused, msg=key + ' accepted without sha256'):
                    ex.series_inputs(value)

    def test_normal_prefix_retry_projection_and_reexport_controls(self):
        result = self.run_export('C1#1', 'C2#1')
        self.assertEqual([w['window'] for w in result['windows']], ['C1', 'C2-z1'])
        payload = read(self.root / 'engine-input.json')
        census = {(r['path'], r['sha256']) for r in read(self.root / 'census.json')['references']}
        count = 0
        for window in payload['windows']:
            for key in ('plan_source', 'terminal_result_source', 'raw_source'):
                if key in window:
                    ref = window[key]
                    self.assertIn((ref['path'], ref['sha256']), census)
            raw = read(self.root / window['raw_source']['path'])
            for row in raw['members']:
                if not row['captured']:
                    continue
                count += 1
                for key in ('config', 'planned_config', 'episode', 'journal'):
                    ref = row[key]
                    self.assertEqual(digest((self.root / ref['path']).read_bytes()), ref['sha256'])
                sidecar = read(self.root / row['journal']['path'])
                from joulewise.align.apple.thermal_desk import normalize_journal
                local = row['run_id'].partition(':')[2] or row['run_id']
                rec_id = window['window']
                thermal = self.root / f'recompute/windows/{rec_id}/members/{row["run_id"]}/outputs/align_thermal.jsonl'
                if thermal.exists():
                    self.assertEqual([json.loads(line) for line in thermal.read_bytes().splitlines()],
                                     normalize_journal(sidecar))
                # Preserve production's seed INDEX. The derived seed belongs to the roster.
                episode = read(self.root / row['episode']['path'])
                slot = next(s for s in window['roster'] if s['run_id'] == row['run_id'])
                self.assertEqual(episode['seed'], slot['seed_index'], local)
                self.assertNotEqual(episode['seed'], slot['expected_episode_seed'], local)
        self.assertEqual(count, 40)
        self.assertEqual(payload['windows'][2]['attempt_id'], 'C2#1')
        self.assertTrue(all(not m['captured'] for m in read(self.root / 'engine/windows/C2-z1/raw.json')['members']))
        inventory = lambda: {p.relative_to(self.root).as_posix(): digest(p.read_bytes())
                             for p in self.root.rglob('*') if p.is_file() and p.name != 'timings.jsonl'}
        before = inventory()
        self.assertEqual({r['outcome'] for r in self.run_export()['windows']}, {'unchanged'})
        self.assertEqual(inventory(), before)

    def test_zero_capture_retry_has_distinct_record_ids_in_the_same_slot(self):
        """An honest second empty attempt stays empty and shares only its registered slot."""
        first = deepcopy(self.entry('C2#1'))
        self.mutate_record('C2#1', lambda record: record.update(window='C2#2'))
        retry = self.entry('C2#1')
        retry['attempt_id'] = 'C2#2'
        self.value['windows'].insert(self.value['windows'].index(retry), first)
        result = self.run_export('C1#1', 'C2#1', 'C2#2')
        self.assertEqual([r['window'] for r in result['windows']], ['C1', 'C2-z1', 'C2-z2'])
        payload = read(self.root / 'engine-input.json')
        self.assertEqual([r['attempt_id'] for r in payload['windows'][-2:]], ['C2#1', 'C2#2'])
        for wid in ('C2-z1', 'C2-z2'):
            window = read(self.root / f'recompute/windows/{wid}/window.json')
            self.assertEqual(window['slot'], 'C2')
            self.assertTrue(all(row['captured'] is False for row in window['members']))


if __name__ == '__main__':
    unittest.main()
