"""FIX-573f: the cold review's storage probes, without live hardware."""
import ast
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import shutil
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import authentication_io as auth, desk_compress as desk, desk_restore as restore
from joulewise import whole_window as ww
from joulewise.b5 import harvest as harvest
from joulewise.bundle_read import BundleReader
from joulewise.cli import main as cli_main, validate_bundle
from joulewise.reduce import reduce_bundle

ROOT = Path(__file__).resolve().parents[1]


def _restore_worker(source, scratch, entered, release, results, checked, second=False):
    """Two processes see one run's available allocation, updated by the first copy."""
    def free(_path):
        allocated = sum(p.stat().st_size for p in Path(scratch).rglob('*') if p.is_file())
        required = sum(p.stat().st_size for p in Path(source).rglob('*') if p.is_file())
        if second:
            checked.set()
        return SimpleNamespace(free=restore.MIN_RESERVE_GIB * 1024**3 + required - allocated)

    copy = restore._copy
    def slow_copy(*args):
        entered.set()
        if not release.wait(10):
            raise RuntimeError('test lock release timed out')
        return copy(*args)

    try:
        with mock.patch.object(restore.shutil, 'disk_usage', side_effect=free), \
             mock.patch.object(restore, '_copy', side_effect=slow_copy):
            with restore.restored_run(source, scratch):
                results.put('readable')
                release.wait(10)
                if not second and not checked.wait(10):
                    raise RuntimeError('second reserve check timed out')
    except restore.RestoreRefused as exc:
        results.put(str(exc))


class FailClosedReadTests(unittest.TestCase):
    def test_every_authentication_read_requires_a_named_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.json'
            Path(str(path) + '.zst').write_bytes(b'not decompressed in this test')
            calls = [lambda: auth.read_authentication_input(path, grammar='json', label='fixture'),
                     lambda: auth.read_authentication_text(path, grammar='json', label='fixture'),
                     lambda: auth.open_authentication_input(path, grammar='json', label='fixture'),
                     lambda: auth.sha256_authentication_input(path, label='fixture')]
            for active in (False, True):
                with ExitStack() as stack:
                    if active:
                        session = stack.enter_context(auth.V2AuthenticationReadSession())
                        calls += [lambda: session.read(path, grammar='json', label='fixture'),
                                  lambda: session.sha256_streaming_raw(path, label='fixture')]
                    for call in calls:
                        with self.assertRaisesRegex(auth.CompressedBundleRequiresRestore,
                                                    'compressed_bundle_requires_restore'):
                            call()
            with mock.patch.object(desk, 'read_bytes', return_value=b'{"fixture":true}'):
                self.assertEqual(auth.read_authentication_input(path, grammar='json', label='fixture',
                                                                allow_compressed=True), b'{"fixture":true}')

    def test_unrestored_reducer_refuses_even_when_only_a_late_primary_is_compressed(self):
        for name in ('config.json', 'events.jsonl', 'raw/powermetrics.plist',
                     'instrument_calibration/manifest.json', 'outputs/requests.jsonl'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                p = root / (name + '.zst')
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'fixture')
                with self.assertRaisesRegex(auth.CompressedBundleRequiresRestore,
                                            'compressed_bundle_requires_restore'):
                    reduce_bundle(root)

    def test_scratch_creation_failure_is_a_program_restore_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'metadata.json.zst').write_bytes(b'not reached')
            journal = root / 'compression.jsonl'
            journal.write_text('')
            with mock.patch.object(restore.tempfile, 'TemporaryDirectory', side_effect=OSError('fixture scratch creation')):
                with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused: fixture scratch creation'):
                    with restore.readable_run(root, compression_records=journal):
                        self.fail('reader reached')

    def test_storage_refusals_never_become_strict_or_survivor_findings(self):
        from joulewise.b6 import survivor_screen
        def refuse(*_args, **_kwargs):
            raise restore.RestoreRefused('fixture storage')
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused: fixture storage'):
            ww.strict_validate_bundles([Path('a')], workers=1, validator=refuse)
        members = [{'run_id': f'corpus{i}', 'stage_id': 'neg8_bound', 'status': 'succeeded'} for i in range(6)]
        members += [{'run_id': f'{slot}{i}', 'stage_id': f'{slot}_reference', 'status': 'succeeded'}
                    for slot in ('start', 'end') for i in range(2)]
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused: fixture storage'):
            survivor_screen.screen({'members': members}, {}, refuse, {'neg8': {'corpus_cap': 6, 'corpus_minimum': 6}})
        # Exercise the real process-pool result and outer fallback catchers too.
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i in range(2):
                path = Path(tmp) / str(i)
                path.mkdir()
                (path / 'metadata.json.zst').write_bytes(b'not opened: journal missing')
                paths.append(path)
            with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused:.*compression.jsonl'):
                ww.strict_validate_bundles(paths, workers=2)

    def test_parallel_materializations_cannot_jointly_cross_reserve(self):
        context = multiprocessing.get_context('fork')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, scratch = root / 'archive/sources/claim-runs/run', root / 'scratch'
            source.mkdir(parents=True)
            (source / 'metadata.json').write_text('{"fixture":true}')
            entered, release = context.Event(), context.Event()
            results = context.Queue()
            checked = context.Event()
            first = context.Process(target=_restore_worker, args=(source, scratch, entered, release, results, checked))
            second = context.Process(target=_restore_worker, args=(source, scratch, entered, release, results, checked, True))
            first.start()
            try:
                self.assertTrue(entered.wait(10))
                second.start()
                time.sleep(.1)
                self.assertTrue(results.empty(), 'second worker bypassed the materialization lock')
                release.set()
                outcomes = [results.get(timeout=10), results.get(timeout=10)]
                self.assertCountEqual(outcomes, ['readable', 'restore_refused: insufficient scratch space'])
            finally:
                release.set()
                for process in (first, second):
                    if process.pid:
                        process.join(10)
                        if process.is_alive():
                            process.kill()
                            process.join()
                results.close()
            self.assertEqual(list(scratch.iterdir()), [])


@unittest.skipUnless(Path(desk.zstd_path()).is_file(), 'zstd CLI required')
class ColdReviewProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.test_p2038_production_path import P2038ProductionPathTests
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.source, _ = P2038ProductionPathTests().run_mode(cls.root / 'primary', 'normal')
        cls.plain = reduce_bundle(cls.source, reducer_version='0.5.2').to_dict()
        cls.energy = ww._reference_energy_evidence_detail(cls.source)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.tmp.cleanup)
        self.case = Path(self.tmp.name)
        self.archive, self.custody = self.case / 'archive', self.case / 'custody'
        (self.archive / 'sources').mkdir(parents=True)
        (self.archive / 'harvest.json').write_text('{"verdict":"COLLECTED"}\n')
        (self.custody / 'night').mkdir(parents=True)
        (self.custody / 'night/chain.exited').write_text('{}\n')
        self.live = self.case / 'live-runs' / 'corpus0'
        shutil.copytree(self.source, self.live)
        self.journal = Path(str(self.archive) + '.desk') / 'compression.jsonl'
        self.space = mock.patch.object(restore.shutil, 'disk_usage', return_value=SimpleNamespace(free=1024**4))
        self.space.start()
        self.addCleanup(self.space.stop)

    def compress(self):
        rc, report = desk.compress(archive=self.archive, custody=self.custody,
                                   runs_roots=[self.live.parent], min_bytes=0)
        self.assertEqual(rc, 0, report)

    def test_probes_1_2_6_and_probe2_live_member_match_after_explicit_restore(self):
        inventory = {p.relative_to(self.live): p.read_bytes() for p in self.live.rglob('*') if p.is_file()}
        self.compress()
        compressed = {p.relative_to(self.live): p.read_bytes() for p in self.live.rglob('*') if p.is_file()}
        journal = self.journal.read_bytes()
        with self.assertRaisesRegex(auth.CompressedBundleRequiresRestore, 'compressed_bundle_requires_restore'):
            reduce_bundle(self.live)
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused:.*compression.jsonl'):
            ww._reference_energy_evidence_detail(self.live)
        with restore.readable_run(self.live, compression_records=self.journal) as plain:
            self.assertEqual(reduce_bundle(plain, reducer_version='0.5.2').to_dict(), self.plain)
            self.assertEqual(ww._reference_energy_evidence_detail(plain), self.energy)
            self.assertEqual({p.relative_to(plain): p.read_bytes() for p in plain.rglob('*') if p.is_file()}, inventory)
            restored = plain
        self.assertFalse(restored.exists())
        self.assertEqual(ww._reference_energy_evidence_detail(self.live, compression_records=self.journal), self.energy)
        self.assertEqual({p.relative_to(self.live): p.read_bytes() for p in self.live.rglob('*') if p.is_file()}, compressed)
        self.assertEqual(self.journal.read_bytes(), journal)
        task = {'run_id': 'corpus0', 'bundle_path': str(self.live), 'withheld_dir': str(self.case / 'assessment'),
                'compression_records': str(self.journal)}
        result = harvest.assess_member(task)
        self.assertTrue(result['rereduced']['identical_to_stored'])
        self.assertTrue(result['strict_valid'])
        self.assertEqual(result['bundle_path'], str(self.live))

    def test_prepare_restores_the_complete_bundle_before_its_own_checks(self):
        self.compress()
        session = object.__new__(ww.AuthenticatedConsumptionSession)
        def inspect(**kwargs):
            plain = kwargs['bundle_paths']['corpus0']
            self.assertNotEqual(plain, self.live)
            self.assertTrue((plain / 'instrument_calibration/manifest.json').is_file())
            self.assertFalse(list(plain.rglob('*.zst')))
            self.assertEqual(reduce_bundle(plain, reducer_version='0.5.2').to_dict(), self.plain)
            self.assertEqual(kwargs['original_paths'], {'corpus0': self.live})
            return plain
        with mock.patch.object(session, '_prepare_plain', side_effect=inspect):
            plain = session._prepare(bundle_paths={'corpus0': self.live}, policy=SimpleNamespace(),
                                     compression_records=self.journal)
        self.assertFalse(plain.exists())

    def test_probe2_mint_and_bound_recheck_restore_before_predicates_and_inventory(self):
        def select():
            manifest = {'members': [{'bundle_id': 'corpus0', 'bundle_path': 'corpus0'}]}
            # Condition/launch eligibility is independent of this production-shaped fixture's storage.
            with mock.patch.object(ww, '_scientific_config_identity', return_value=('c' * 64, True)):
                return ww._hazard_neg8_corpus_selection(self.live.parent, manifest, compression_records=self.journal)
        before = select()
        self.assertEqual(before['drops'], [])
        self.assertEqual(before['indeterminate'], [])
        self.assertEqual(len(before['rows']), 1)
        member = before['rows'][0]['evidence']
        fields = before['rows'][0]['fields']
        bound = {'reference_corpus': {'members': [member], 'scientific_config_sha256': 'c' * 64},
                 'freshness': {'bindings': {'calibration_identity_sha256': fields['calibration_identity_sha256']}}}
        with mock.patch.object(ww, '_scientific_config_identity', return_value=('c' * 64, True)):
            expected = harvest.neg8_bound_member_problems(bound, self.live.parent)
        self.compress()
        self.assertEqual(select(), before)
        with mock.patch.object(ww, '_scientific_config_identity', return_value=('c' * 64, True)):
            self.assertEqual(harvest.neg8_bound_member_problems(bound, self.live.parent,
                            compression_records=self.journal), expected)

    def test_probes_3_4_5_exact_reserve_short_disk_digest_and_cleanup(self):
        self.compress()
        required = sum(e[4] for e in restore._inventory(self.live.resolve(), restore._records(self.journal)))
        scratch = self.case / 'scratch'
        for free, succeeds in ((required + 40 * 1024**3, True), (required + 40 * 1024**3 - 1, False), (0, False)):
            with self.subTest(free=free), mock.patch.object(restore.shutil, 'disk_usage', return_value=SimpleNamespace(free=free)):
                if succeeds:
                    with restore.restored_run(self.live, scratch, compression_records=self.journal) as plain:
                        self.assertEqual(reduce_bundle(plain, reducer_version='0.5.2').to_dict(), self.plain)
                else:
                    with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused: insufficient scratch space'):
                        with restore.restored_run(self.live, scratch, compression_records=self.journal):
                            self.fail('reader reached')
                self.assertEqual(list(scratch.iterdir()), [])
        rows = [json.loads(line) for line in self.journal.read_text().splitlines()]
        for row in rows:
            if row['path'].startswith(str(self.live)):
                row['sha256'] = '0' * 64
        self.journal.write_text(''.join(json.dumps(r) + '\n' for r in rows))
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused:.*digest mismatch'):
            with restore.restored_run(self.live, scratch, compression_records=self.journal):
                self.fail('reader reached')
        self.assertEqual(list(scratch.iterdir()), [])

    def test_cli_reduce_and_strict_restore_or_stop_without_writing_a_summary(self):
        archive_run = self.archive / 'sources/claim-runs' / self.live.name
        shutil.copytree(self.live, archive_run)
        self.compress()
        expected = self.plain
        output = self.case / 'prospective.json'
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            rc = cli_main(['reduce', str(archive_run), '--output', str(output)])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.read_bytes()), expected)
        self.assertEqual(validate_bundle(archive_run, strict=True), [])
        self.journal.unlink()
        output.unlink()
        err = io.StringIO()
        with redirect_stderr(err):
            rc = cli_main(['reduce', str(archive_run), '--output', str(output)])
        self.assertNotEqual(rc, 0)
        self.assertIn('restore_refused:', err.getvalue())
        self.assertFalse(output.exists())
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused:'):
            validate_bundle(archive_run, strict=True)

    def test_harvest_refusals_escape_member_and_step_fences(self):
        self.compress()
        task = {'run_id': 'corpus0', 'bundle_path': str(self.live), 'withheld_dir': str(self.case / 'assessment')}
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused:.*compression.jsonl'):
            harvest.assess_member(task)
        task['compression_records'] = str(self.journal)
        with mock.patch.object(restore.shutil, 'disk_usage', return_value=SimpleNamespace(free=0)):
            with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused: insufficient scratch space'):
                harvest.assess_members([task], workers=1)
        fake = SimpleNamespace(_record_error=mock.Mock())
        with self.assertRaisesRegex(restore.RestoreRefused, 'restore_refused: fixture storage'):
            harvest._Harvest.step(fake, 'members', lambda: (_ for _ in ()).throw(restore.RestoreRefused('fixture storage')))
        fake._record_error.assert_not_called()
        err = io.StringIO()
        with mock.patch.object(harvest, '_harvest', side_effect=restore.RestoreRefused('fixture storage')), redirect_stderr(err):
            with self.assertRaises(restore.RestoreRefused):
                harvest.harvest(None, self.archive)
        self.assertEqual(err.getvalue(), 'restore_refused: fixture storage\n')


class SyntheticHarvestGateTests(unittest.TestCase):
    def test_synthetic_only_import_never_probes_a_local_archive(self):
        import os
        import runpy
        forbidden = '/Users/edr/night-forbidden-synthetic-test'
        is_file = Path.is_file
        def guarded(path, *args, **kwargs):
            if str(path).startswith(forbidden):
                self.fail('synthetic-only import attempted a local archive probe')
            return is_file(path, *args, **kwargs)
        with mock.patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '1', 'JW_B5_B3W1_ROOT': forbidden}), \
             mock.patch.object(Path, 'is_file', guarded):
            module = runpy.run_path(str(ROOT / 'tests/test_harvest_b5_window.py'), run_name='harvest_synthetic_gate_probe')
        self.assertTrue(module['RehearsalRound1Tests'].__unittest_skip__)
        self.assertTrue(module['RealB3w1BytesTests'].__unittest_skip__)


class ReductionCensusTests(unittest.TestCase):
    def test_walk_every_reducer_entry_point(self):
        """New aliases or callers require an explicit storage-path disposition."""
        calls, references = [], []
        names = {'reduce_bundle', '_rederive_summary_for_authenticated_fiducial_bound'}
        def walk(node, path, call_names, function='<module>', parent=None):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function = node.name
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ''
                if name in call_names:
                    calls.append((path, function, name))
            symbol = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else ''
            if symbol in call_names and not (isinstance(parent, ast.Call) and parent.func is node):
                references.append((path, function, symbol))
            for child in ast.iter_child_nodes(node):
                walk(child, path, call_names, function, node)
        for base in ('joulewise', 'scripts'):
            for path in sorted((ROOT / base).rglob('*.py')):
                tree = ast.parse(path.read_text())
                call_names = names | {alias.asname or alias.name for node in ast.walk(tree)
                                      if isinstance(node, ast.ImportFrom) and node.module == 'joulewise.reduce'
                                      for alias in node.names if alias.name in names}
                walk(tree, path.relative_to(ROOT).as_posix(), call_names)
        self.assertCountEqual(calls, [
            ('joulewise/reduce.py', '_rederive_summary_for_authenticated_fiducial_bound', 'reduce_bundle'),
            ('joulewise/controller.py', '_stage_reduce', 'reduce_bundle'),
            ('joulewise/cli.py', '_plain_strict_problems', 'reduce_bundle'),
            ('joulewise/cli.py', '_plain_strict_problems', 'reduce_bundle'),
            ('joulewise/cli.py', '_plain_strict_problems', 'reduce_bundle'),
            ('joulewise/cli.py', '_cmd_reduce', 'reduce_bundle'),
            ('joulewise/b5/harvest.py', 'rereduce', 'reduce_bundle'),
            ('joulewise/whole_window.py', '_prepare_plain', '_rederive_summary_for_authenticated_fiducial_bound'),
            ('joulewise/whole_window.py', '_plain_reference_energy_evidence_detail', 'reduce_bundle'),
            ('joulewise/bytes_analysis.py', 'operative_summary', '_rederive_summary_for_authenticated_fiducial_bound')])
        self.assertCountEqual(references, [
            ('joulewise/controller.py', '_stage_reduce', 'reduce_bundle'),
            ('scripts/harvest_v5_g2b_window.py', 'l10_a', 'reduce_bundle')])
        # The historical injected reducer is also an entry point, even without an ast.Call spelling.
        legacy = ast.parse((ROOT / 'scripts/harvest_v5_g2b_window.py').read_text())
        injected = [(n.name, a.id) for n in ast.walk(legacy) if isinstance(n, ast.FunctionDef)
                    for a in n.args.kw_defaults if isinstance(a, ast.Name) and a.id in names]
        self.assertEqual(injected, [('l10_a', 'reduce_bundle')])

    def test_issued_reducer_is_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT / 'joulewise/reduce.py').read_bytes()).hexdigest(),
                         '7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc')
