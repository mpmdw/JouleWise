"""Native exporter end to end (scripts/export_v4_series.py). SYNTHETIC ONLY; no real custody is read.

The series is built with real producers (``native_series``): WP22's world and controller for W1 and the C members
(configs from the real series kit), the real thermal desk, production-layout sessions finalized, packed and restored
by the real harvest-off CLI, and window records committed in the Scenario shape. NOT a real producer: the raw
powermetrics plist (WP22's synthetic GPU rail writes none; it is written from the bundle's own power_trace.csv), the
KM003C stream, the U3 bar and the R1 references (RELEASE-RUNBOOK-v4.md section 6a).

Plan: W1, C1 (captured, GO), C2#1 (zero capture), C2#2 (captured retry, GO). Each window exports as it lands; then the
recompute and the pinned engine read the export, and release_v4 runs when the engine produces a run.

Builds: engine-r23k (72410b0b4) and the recompute at 7b06c6058, the commits that implement the r23k-review
export contract (plan_source, planned_config). release_v4.py still pins engine-r23j and recompute 9f8a8749e, so
``test_release_agrees`` is an expected failure until the release pins move and the classified gaps close
(RELEASE-RUNBOOK-v4.md section 6a.2); an unexpected success means flip it.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import support  # noqa: E402
import native_series  # noqa: E402

EXPORTER = REPO / 'scripts' / 'export_v4_series.py'
ENGINE_COMMIT = '72410b0b4f725d770298a301a55802e70d466537'      # origin/engine-r23k (R23l + plan owner refinement)
RECOMPUTE_COMMIT = '7b06c6058efa211fd14acb14838cc84c13694012'   # align/2026-11-08-v4-recompute-opus (config custody)
# Engine refusals classified in RELEASE-RUNBOOK-v4.md section 6a.2 (a refusal outside this list fails the test).
KNOWN_ENGINE_REFUSALS = {'series manifest roster differs from R15': 'EXP-G2',
                         'roster differs from R15 allocation': 'EXP-G2'}
PLAN = ('W1#1', 'C1#1', 'C2#1', 'C2#2')
_SERIES = {}


def series():
    if 'config' not in _SERIES:
        synth = support.synth_module()
        config, timings = native_series.cached(synth, synth.FrameTemplate(n_tasks=0, seed=7, clusters=0))
        _SERIES.update(config=config, timings=timings)
    return _SERIES['config']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export(config_path, *windows):
    argv = [sys.executable, '-B', str(EXPORTER), 'export', '--config', str(config_path)]
    argv += ['--all'] if not windows else [x for w in windows for x in ('--window', w)]
    t = time.monotonic()
    r = subprocess.run(argv, capture_output=True)
    return r.returncode, json.loads(r.stdout or b'{}'), time.monotonic() - t, r.stderr.decode()


def config_copy(work, **changes):
    value = json.loads(Path(series()).read_text())
    value['export_root'] = str(Path(work) / 'export')
    value.update(changes)
    path = Path(work) / 'config.json'
    path.write_text(json.dumps(value, indent=1))
    return path, value


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(Path(root).rglob('*')) if p.is_file()}


def have_commits():
    return all(subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', c + '^{commit}'], capture_output=True)
               .returncode == 0 for c in (ENGINE_COMMIT, RECOMPUTE_COMMIT, support.RECOMPUTE_COMMIT))


@unittest.skipUnless(have_commits(), 'pinned build commits unavailable (shallow clone)')
class ExporterEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-v4-export-e2e-')
        cls.work = Path(cls.tmp.name)
        cls.config, cls.value = config_copy(cls.work)
        cls.root = Path(cls.value['export_root'])
        cls.results, cls.wall, cls.snapshots = {}, {}, {}
        for w in PLAN:
            cls.results[w] = export(cls.config, w)
            cls.wall[w] = cls.results[w][2]
            cls.snapshots[w] = inventory(cls.root)
        t = time.monotonic()
        cls.rerun = export(cls.config)
        cls.wall['reexport_all'] = time.monotonic() - t
        t = time.monotonic()
        cls.recompute_exit = support.run_recompute(cls.root, tree_dir=support.tree(RECOMPUTE_COMMIT))
        cls.wall['recompute'] = time.monotonic() - t
        t = time.monotonic()
        cls.engine_exit, cls.engine_verdict = support.run_engine(cls.root, workers=4,
                                                                 tree_dir=support.tree(ENGINE_COMMIT))
        cls.wall['engine'] = time.monotonic() - t
        detail = cls.root / 'engine-out-cal' / 'refusal-detail.json'
        cls.engine_refusal = json.loads(detail.read_text()) if detail.exists() else None
        stderr = cls.root / 'recompute-stderr.txt'
        (Path(tempfile.gettempdir()) / 'jw-v4-export-e2e-timings.json').write_text(json.dumps(dict(
            exporter_s={w: cls.wall[w] for w in PLAN}, series_build=_SERIES.get('timings'),
            recompute_exit=cls.recompute_exit, recompute_stderr=stderr.read_text()[-3000:] if stderr.exists() else None,
            engine_exit=cls.engine_exit, engine_verdict=cls.engine_verdict, engine_refusal=cls.engine_refusal,
            **{k: v for k, v in cls.wall.items() if k not in PLAN}), indent=1))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_each_window_exports_as_it_lands(self):
        for w in PLAN:
            code, out, _, err = self.results[w]
            self.assertEqual(code, 0, err[-2000:])
            self.assertEqual([r['outcome'] for r in out['windows']], ['exported'])
        self.assertEqual({r['window'] for w in PLAN for r in self.results[w][1]['windows']},
                         {'W1', 'C1', 'C2-z1', 'C2'})

    def test_later_windows_never_rewrite_earlier_ones_and_reexport_is_identical(self):
        index = ('engine-input.json', 'crosswalk.json', 'census.json', 'engine/series-manifest.json',
                 'recompute/series.json', 'recompute/u3_bar.json', 'recompute/references.json',
                 'recompute/allocation/series_manifest.json', 'state/timings.jsonl')
        for earlier, later in zip(PLAN, PLAN[1:]):
            before = {k: v for k, v in self.snapshots[earlier].items() if k not in index}
            after = self.snapshots[later]
            self.assertEqual({k: after.get(k) for k in before}, before, f'{later} rewrote {earlier} files')
        code, out, _, err = self.rerun
        self.assertEqual(code, 0, err)
        self.assertEqual({r['outcome'] for r in out['windows']}, {'unchanged'})

    def test_both_layouts_read_the_same_raw_bytes(self):
        payload = json.loads((self.root / 'engine-input.json').read_text())
        checked = 0
        for w in payload['windows']:
            doc = json.loads((self.root / w['raw_source']['path']).read_text())
            for m in doc['members']:
                if not m['captured']:
                    continue
                for key in ('powermetrics', 'config'):
                    ref = m[key]
                    self.assertTrue(ref['path'].startswith('recompute/windows/'), ref['path'])
                    self.assertEqual(sha(self.root / ref['path']), ref['sha256'])
                    checked += 1
                for ref in m.get('dc_streams', []):
                    self.assertTrue(ref['path'].startswith('recompute/windows/'))
                self.assertEqual(sha(self.root / m['episode']['path']), m['episode']['sha256'])
        self.assertEqual(checked, 2 * (18 + 22 + 22))

    def test_export_contract_fields(self):
        payload = json.loads((self.root / 'engine-input.json').read_text())
        self.assertEqual([w['attempt_id'] for w in payload['windows']], list(PLAN))
        manifest = json.loads((self.root / payload['series_source']['path']).read_text())
        self.assertEqual([w['window'] for w in manifest['windows']], ['W1', *[f'C{i}' for i in range(1, 15)],
                                                                      'T1', 'T2', 'T3'])
        series = json.loads((self.root / 'recompute/series.json').read_text())
        self.assertEqual(series['h_star_grid'], [128, 256, 384, 512, 768, 1024, 1536, 2048])
        self.assertEqual(series['allocation_source']['sha256'], support.common_series.ALLOCATION_SHA256)
        self.assertEqual(sha(self.root / 'recompute' / series['allocation_source']['path']),
                         support.common_series.ALLOCATION_SHA256)
        self.assertEqual([w['window_id'] for w in series['windows']], ['W1', 'C1', 'C2-z1', 'C2'])
        text = (self.root / 'engine-input.json').read_text()
        self.assertNotIn('"terminal_result"', text)
        for w in payload['windows']:
            captured = w['attempt_id'] != 'C2#1'
            self.assertEqual('terminal_result_source' in w, captured and w['window'].startswith('C'))
            for slot in w['roster']:
                self.assertEqual(slot['run_id'].startswith(w['window'] + ':'), slot['series_role'] == 'anchor')
        for wid in ('W1', 'C1', 'C2-z1', 'C2'):
            doc = json.loads((self.root / 'recompute/windows' / wid / 'window.json').read_text())
            self.assertNotIn('terminal_result', doc)
            self.assertEqual('terminal_result_source' in doc, wid in ('C1', 'C2'))
            self.assertEqual(doc.get('slot'), None if wid == 'W1' else wid.split('-')[0])
            self.assertEqual(doc.get('sentinel_ordinals'), [5, 17] if wid == 'W1' else None)
            for m in doc['members']:
                self.assertEqual(m['run_id'].startswith(wid + ':'), m['kind'] == 'anchor')
            if 'terminal_result_source' in doc:
                ref = doc['terminal_result_source']
                self.assertEqual(sha(self.root / 'recompute' / ref['path']), ref['sha256'])
        raw = json.loads((self.root / 'engine/windows/W1/raw.json').read_text())
        for m in raw['members']:
            self.assertIs(type(m['first_record_endpoint_s']), float)
            self.assertIs(type(m['offset_ns']), int)
            self.assertTrue(all(type(s[k]) in (int, float) for s in m['stamps'] for k in s))
        cross = json.loads((self.root / 'crosswalk.json').read_text())
        self.assertEqual(len(cross['members']), 18 + 3 * 22)
        self.assertTrue(all(isinstance(m['attempt_id'], str) for m in cross['members']))

    def test_config_custody_chain(self):
        """plan_source on every attempt, both layouts, one file; planned_config on every captured member; the kit
        digest is the plan row's and the bundle config.json is the writer's bytes of that kit config."""
        from scripts import export_v4_series as ex
        payload = json.loads((self.root / 'engine-input.json').read_text())
        for w in payload['windows']:
            rec_wid = {'C2#1': 'C2-z1'}.get(w['attempt_id'], w['window'])
            doc = json.loads((self.root / 'recompute/windows' / rec_wid / 'window.json').read_text())
            self.assertEqual(w['plan_source']['path'], 'recompute/' + doc['plan_source']['path'])
            self.assertEqual(w['plan_source']['sha256'], doc['plan_source']['sha256'])
            plan = {r['run_id']: r for r in json.loads((self.root / w['plan_source']['path']).read_text())['members']}
            rows = {r['run_id']: r for r in doc['members']}
            for m in json.loads((self.root / w['raw_source']['path']).read_text())['members']:
                if not m['captured']:
                    continue
                local = m['run_id'].partition(':')[2] or m['run_id']
                kit = (self.root / m['planned_config']['path']).read_bytes()
                self.assertEqual(m['planned_config']['sha256'], plan[local]['config_sha256'])
                self.assertEqual(hashlib.sha256(ex.writer_config_bytes(kit)).hexdigest(), m['config']['sha256'])
                rrow = rows[m['run_id'].replace(w['window'] + ':', rec_wid + ':', 1)]
                self.assertEqual('recompute/' + rrow['planned_config']['path'], m['planned_config']['path'])
            for r in doc['members']:
                self.assertIn('seed_index', r)
                self.assertIn('expected_episode_seed', r)

    def test_census_names_every_raw_reference(self):
        census = {(r['path'], r['sha256']) for r in json.loads((self.root / 'census.json').read_text())['references']}
        payload = json.loads((self.root / 'engine-input.json').read_text())
        refs = [payload['series_source']] + [w[k] for w in payload['windows']
                                             for k in ('raw_source', 'terminal_result_source', 'plan_source')
                                             if k in w]
        for w in payload['windows']:
            for m in json.loads((self.root / w['raw_source']['path']).read_text())['members']:
                refs += [m[k] for k in ('episode', 'powermetrics', 'config', 'planned_config', 'journal') if k in m]
                refs += m.get('dc_streams', [])
        self.assertTrue(all((r['path'], r['sha256']) in census for r in refs))
        for path, digest in census:
            self.assertEqual(sha(self.root / path), digest)

    def test_recompute_accepts_the_export(self):
        self.assertEqual(self.recompute_exit, 0, (self.root / 'recompute-stderr.txt').read_text()[-3000:]
                         if (self.root / 'recompute-stderr.txt').exists() else '')

    def test_engine_runs_or_refuses_only_for_a_classified_gap(self):
        """The pinned engine either completes on the real-layout export or refuses for a classified contract gap;
        it never refuses on the export's custody (config chain, census, references)."""
        if self.engine_exit == 0:
            return
        detail = (self.engine_refusal or {}).get('detail', '')
        self.assertIn(detail, KNOWN_ENGINE_REFUSALS, self.engine_refusal)

    @unittest.expectedFailure
    def test_release_agrees(self):
        """AGREE on real-producer data (exit 0). Expected to fail: this checkout's release_v4 pins engine-r23j, and
        with the release-tools pins (72410b0b4 / 7b06c6058) the comparator still refuses on EXP-G3 (display-name
        model keys) and EXP-G4 (unmapped production cache_statistics); see RELEASE-RUNBOOK-v4.md section 6a.2."""
        self.assertEqual(self.engine_exit, 0)
        support.write_record(self.root, commit=ENGINE_COMMIT)
        checkout = support.release_checkout(self.work / 'checkout')
        code, verdict, _ = support.run_release(checkout, self.root, self.work / 'restricted',
                                               engine_commit=ENGINE_COMMIT, recompute_commit=RECOMPUTE_COMMIT)
        self.assertEqual((code, verdict.get('verdict')), (0, 'agree'), verdict)


@unittest.skipUnless(have_commits(), 'pinned build commits unavailable (shallow clone)')
class ExporterRefusals(unittest.TestCase):
    """Every custody inconsistency refuses with a fixed code (exit 2, structure-only stdout); nothing lands."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-v4-export-refusals-')
        cls.work = Path(cls.tmp.name)
        cls.config, cls.value = config_copy(cls.work)
        cls.root = Path(cls.value['export_root'])
        code, _, _, err = export(cls.config, 'W1#1')
        assert code == 0, err
        cls.repo = Path(cls.value['records_repo'])
        cls.c1 = next(w for w in cls.value['windows'] if w['attempt_id'] == 'C1#1')
        cls.session = Path(cls.c1['session_root'])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def refused(self, code_expected, entry=None, attempt='C1#1'):
        value = copy.deepcopy(self.value)
        if entry is not None:
            value['windows'] = [w if w['attempt_id'] != attempt else dict(entry, attempt_id=attempt)
                                for w in value['windows']]
        path = self.work / 'mutated.json'
        path.write_text(json.dumps(value))
        before = inventory(self.root)
        code, out, _, err = export(path, attempt)
        self.assertEqual((code, out), (2, {'status': 'refused', 'code': code_expected}), err[-1500:])
        self.assertEqual(inventory(self.root), before)          # nothing landed, no index rewritten

    def record(self, mutate, sources=None):
        """Commit a mutated copy of C1's record (and optionally mutated sources); returns its config entry."""
        git = lambda *a: native_series.git(self.repo, *a)  # noqa: E731
        record = json.loads(git('show', f'{self.c1["record_commit"]}:{self.c1["record_path"]}'))
        for name, change in (sources or {}).items():
            raw = git('show', f'{self.c1["record_commit"]}:{record["sources"][name]["path"]}').encode() + b'\n'
            if name == 'courier_sent':
                raw = b''
            raw = change(raw) if raw is not None else None
            if raw is None:
                record['sources'].pop(name)
                continue
            rel = f'mutations/{name}-{hashlib.sha256(raw).hexdigest()[:12]}.json'
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / rel).write_bytes(raw)
            record['sources'][name] = {'path': rel, 'sha256': hashlib.sha256(raw).hexdigest()}
        mutate(record)
        raw = json.dumps(record, sort_keys=True).encode() + b'\n'
        rel = f'mutations/record-{hashlib.sha256(raw).hexdigest()[:12]}.json'
        (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.repo / rel).write_bytes(raw)
        git('add', '.')
        git('commit', '-qm', 'mutation', '--allow-empty')
        return dict(self.c1, record_commit=git('rev-parse', 'HEAD'), record_path=rel)

    def member_file(self, name):
        return self.session / 'runs-parent/claim/align-v4-c1-e06' / name

    def test_digest_mismatch(self):
        path = self.member_file('config.json')
        raw = path.read_bytes()
        try:
            path.write_bytes(raw + b' ')
            self.refused('digest_mismatch')
        finally:
            path.write_bytes(raw)

    def test_member_bundle_file_missing(self):
        path = self.member_file('raw/powermetrics.plist')
        hold = self.work / 'held.plist'
        os.rename(path, hold)
        try:
            self.refused('member_file_missing')
        finally:
            os.rename(hold, path)

    def test_symlink_refuses(self):
        path = self.member_file('metadata.json')
        hold = self.work / 'held-metadata.json'
        os.rename(path, hold)
        try:
            path.symlink_to(hold)
            self.refused('path_refused')
        finally:
            path.unlink()
            os.rename(hold, path)

    def test_traversal_refuses(self):
        from scripts import export_v4_series as ex
        session = ex.Session(self.session, {'entries': {}})
        for bad in ('runs-parent/../session.json', '/etc/hosts', '', '.'):
            with self.subTest(path=bad), self.assertRaises(ex.Refused) as caught:
                session.path(bad)
            self.assertEqual(caught.exception.code, 'path_refused')

    def test_session_root_must_be_the_finalized_source_root(self):
        self.refused('session_root_differs', dict(self.c1, session_root=str(self.work)))

    def test_roster_differs_from_manifest(self):
        def change(raw):
            plan = json.loads(raw)
            plan['members'][6]['seed_index'] += 1
            return json.dumps(plan).encode()
        self.refused('roster_differs_from_manifest', self.record(lambda r: None, {'collection_plan': change}))

    def test_roster_differs_from_plan(self):
        self.refused('roster_differs_from_plan', self.record(lambda r: None, {'plan': lambda raw: raw + b' '}))

    def test_capture_missing_from_record(self):
        def mutate(record):
            record['captures']['align-v4-c1-e06'] = None
        self.refused('capture_missing_from_record', self.record(mutate))

    def test_capture_digest_differs(self):
        def mutate(record):
            # The record's raw_evidence inventory lists the capture descriptors; keep it consistent so the
            # mismatch reaches the exporter's own plist check (WindowRecord refuses an inconsistent inventory).
            record['captures']['align-v4-c1-e06']['sha256'] = '0' * 64
            record['raw_evidence'] = [record['finalized_manifest']]
        self.refused('capture_digest_differs', self.record(mutate))

    def test_inconsistent_raw_evidence_inventory_refuses(self):
        def mutate(record):
            record['captures']['align-v4-c1-e06']['sha256'] = '0' * 64
        self.refused('record_unreadable', self.record(mutate))

    def test_terminal_evidence_missing(self):
        self.refused('terminal_evidence_missing', self.record(lambda r: None, {'chain_exited': lambda raw: None}))

    def test_terminal_evidence_mismatch(self):
        self.refused('terminal_evidence_mismatch',
                     self.record(lambda r: None, {'chain_exited': lambda raw: b'{"exit_code": 1}\n'}))

    def test_broken_plan_digest(self):
        def change(raw):
            plan = json.loads(raw)
            plan['members'][6]['config_sha256'] = '0' * 64
            return json.dumps(plan).encode()
        self.refused('config_digest_not_planned', self.record(lambda r: None, {'collection_plan': change}))

    def test_bundle_config_that_is_not_the_writers_bytes_of_the_planned_kit(self):
        """A digest-consistent plan and kit whose writer bytes are not the member's bundle config.json."""
        kit_root = Path(self.value['kit_root'])
        plan = json.loads(native_series.git(self.repo, 'show', f"{self.c1['record_commit']}:"
                                            f"{json.loads(native_series.git(self.repo, 'show', self.c1['record_commit'] + ':' + self.c1['record_path']))['sources']['collection_plan']['path']}"))
        row = plan['members'][6]
        kit = json.loads((kit_root / row['config_path']).read_bytes())
        kit['run_metadata']['tags'] = list(kit['run_metadata']['tags']) + ['not-the-planned-config']
        raw = (json.dumps(kit, indent=2, sort_keys=True) + '\n').encode()
        rel = 'mutations/kit-' + hashlib.sha256(raw).hexdigest()[:12] + '.json'
        (kit_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (kit_root / rel).write_bytes(raw)

        def change(_):
            row.update(config_path=rel, config_sha256=hashlib.sha256(raw).hexdigest())
            return json.dumps(plan).encode()
        self.refused('config_digest_not_planned', self.record(lambda r: None, {'collection_plan': change}))

    def test_a_plan_of_another_window_refuses_wrong_window(self):
        def change(raw):
            plan = json.loads(raw)
            plan.update(plan_id='align-v4-c2', window_id='C2')
            return json.dumps(plan).encode()
        self.refused('config_digest_not_planned:wrong_window', self.record(lambda r: None, {'collection_plan': change}))

    def test_swapped_plan_run_ids_refuse(self):
        """Production C/T run ids are align-v4-<slot>-eNN by ordinal (scripts/align_v4_series.py:285)."""
        def change(raw):
            plan = json.loads(raw)
            a, b = plan['members'][6], plan['members'][7]
            a['run_id'], b['run_id'] = b['run_id'], a['run_id']
            return json.dumps(plan).encode()

        def mutate(record):
            c = record['captures']
            c['align-v4-c1-e07'], c['align-v4-c1-e08'] = c['align-v4-c1-e08'], c['align-v4-c1-e07']
        self.refused('roster_differs_from_manifest', self.record(mutate, {'collection_plan': change}))

    def test_an_invalid_planned_kit_is_exported_for_the_builds_to_exclude(self):
        """config_invalid is the builds' exclusion: a digest-consistent kit that is not a JSON object exports."""
        kit_root = Path(self.value['kit_root'])
        raw = b'[1, 2, 3]\n'
        rel = 'mutations/kit-invalid.json'
        (kit_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (kit_root / rel).write_bytes(raw)

        def change(text):
            plan = json.loads(text)
            plan['members'][6].update(config_path=rel, config_sha256=hashlib.sha256(raw).hexdigest())
            return json.dumps(plan).encode()
        entry = self.record(lambda r: None, {'collection_plan': change})
        value = copy.deepcopy(self.value)
        value['export_root'] = str(self.work / 'invalid-kit')
        value['windows'] = [value['windows'][0], dict(entry, attempt_id='C1#1')]
        path = self.work / 'invalid-kit.json'
        path.write_text(json.dumps(value))
        self.assertEqual(export(path, 'W1#1')[0], 0)
        code, out, _, err = export(path, 'C1#1')
        self.assertEqual(code, 0, err[-1500:])
        doc = json.loads((self.work / 'invalid-kit/engine/windows/C1/raw.json').read_text())
        member = next(m for m in doc['members'] if m['run_id'] == 'align-v4-c1-e07')
        self.assertEqual(member['planned_config']['sha256'], hashlib.sha256(raw).hexdigest())

    def test_unknown_record_key(self):
        def mutate(record):
            record['terminal_result'] = {'verdict': 'GO', 'chain_exit_code': 0}
        self.refused('unknown_contract_key', self.record(mutate))

    def test_declared_bar_must_match_the_committed_desk(self):
        def mutate(record):
            record['barred'] = 'u1_u3_fail'
        self.refused('declared_bar_inconsistent', self.record(mutate))

    def test_desk_record_differs(self):
        def change(raw):
            pilot = json.loads(raw)
            member = next(m for m in pilot['extra_checks']['thermal']['members'] if m['id'] == 'align-v4-c1-e06')
            member['battery'] = dict(member['battery'], flags=['battery.member_span'])
            return json.dumps(pilot).encode()
        self.refused('desk_record_differs', self.record(lambda r: None, {'pilot': change}))

    def test_owned_energy_flags_never_enter_the_release_path(self):
        def change(raw):
            pilot = json.loads(raw)
            next(m for m in pilot['extra_checks']['thermal']['members']
                 if m['id'] == 'align-v4-c1-e06')['owned_energy_flags'] = []
            return json.dumps(pilot).encode()
        self.refused('owned_energy_flags_unexpected', self.record(lambda r: None, {'pilot': change}))

    def test_window_order_gap(self):
        value = copy.deepcopy(self.value)
        value['export_root'] = str(self.work / 'fresh')
        path = self.work / 'fresh.json'
        path.write_text(json.dumps(value))
        code, out, _, _ = export(path, 'C1#1')
        self.assertEqual((code, out['code']), (2, 'window_order_gap'))

    def test_record_id_collision(self):
        """Two configured attempts that resolve to the same record id (here C1 committed twice)."""
        value = copy.deepcopy(self.value)
        value['export_root'] = str(self.work / 'collide')
        value['windows'] = [value['windows'][0], self.c1, dict(self.record(lambda r: r.update(window='C1#2')),
                                                               attempt_id='C1#2')]
        path = self.work / 'collide.json'
        path.write_text(json.dumps(value))
        self.assertEqual(export(path, 'W1#1', 'C1#1')[0], 0)
        code, out, _, _ = export(path, 'C1#2')
        self.assertEqual((code, out['code']), (2, 'anchor_id_collision'))

    def test_reexport_that_differs_refuses(self):
        value = copy.deepcopy(self.value)
        value['export_root'] = str(self.work / 'differs')
        path = self.work / 'differs.json'
        path.write_text(json.dumps(value))
        self.assertEqual(export(path, 'W1#1')[0], 0)
        window = self.work / 'differs/recompute/windows/W1/window.json'
        window.write_bytes(window.read_bytes() + b' ')
        code, out, _, _ = export(path, 'W1#1')
        self.assertEqual((code, out['code']), (2, 'window_already_exported_differs'))


if __name__ == '__main__':
    unittest.main()
