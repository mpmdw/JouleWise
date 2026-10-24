"""Storage/custody stops bypass data handlers and survive process transport."""
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
import io
import multiprocessing
from pathlib import Path
import pickle
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import authentication_io as auth, cli, desk_restore as restore
from scripts import bytes_analyze, bytes_twin, harvest_b6_session, harvest_v5_g2b_window
from scripts import extract_detection_floors, harvest_b5_window, restore_run_to_scratch, run_campaign


def _stop_worker(kind):
    if kind == 'compressed':
        raise auth.CompressedBundleRequiresRestore('/fixture/raw/powermetrics.plist')
    if kind == 'restore':
        raise restore.RestoreRefused('fixture custody cause')
    raise restore.StorageStop('fixture storage cause')


class StorageStopTests(unittest.TestCase):
    def test_ordinary_handlers_cannot_absorb_any_storage_stop(self):
        for kind, expected in (
                ('base', restore.StorageStop), ('restore', restore.RestoreRefused),
                ('compressed', auth.CompressedBundleRequiresRestore)):
            with self.subTest(kind=kind), self.assertRaises(expected):
                try:
                    _stop_worker(kind)
                except (Exception, ValueError, RuntimeError):
                    self.fail('storage stop became a data decision')
        self.assertTrue(issubclass(restore.RestoreRefused, restore.StorageStop))
        self.assertTrue(issubclass(auth.CompressedBundleRequiresRestore, restore.StorageStop))

    def test_repeated_pickle_roundtrips_keep_type_cause_and_one_prefix(self):
        for initial in (restore.StorageStop('fixture'), restore.RestoreRefused('fixture'),
                        auth.CompressedBundleRequiresRestore('/fixture')):
            exc = initial
            for _ in range(4):
                exc = pickle.loads(pickle.dumps(exc))
                self.assertIs(type(exc), type(initial))
                self.assertEqual(str(exc), str(initial))
                self.assertEqual(str(exc).count('restore_refused: '), 1)
                self.assertEqual(exc.reason, initial.reason)

    def test_process_pool_preserves_storage_stop_class_and_cause(self):
        # spawn exercises importability and exception reconstruction, not fork inheritance.
        with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context('spawn')) as pool:
            for kind, expected, cause in (
                    ('base', restore.StorageStop, 'fixture storage cause'),
                    ('restore', restore.RestoreRefused, 'fixture custody cause'),
                    ('compressed', auth.CompressedBundleRequiresRestore,
                     'compressed_bundle_requires_restore: /fixture/raw/powermetrics.plist')):
                with self.subTest(kind=kind):
                    with self.assertRaises(expected) as caught:
                        pool.submit(_stop_worker, kind).result(timeout=20)
                    self.assertEqual(str(caught.exception), 'restore_refused: ' + cause)


class EntryPointTests(unittest.TestCase):
    def check_main(self, module, args, seam, code, *, stdout=False, error_type=restore.RestoreRefused):
        out, err = io.StringIO(), io.StringIO()
        stop = error_type('fixture storage cause')
        with mock.patch.object(module.argparse.ArgumentParser, 'parse_args', return_value=args), \
             mock.patch.object(module, seam, side_effect=stop), \
             redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(module.main([]), code)
        self.assertIn('refused: restore_refused: fixture storage cause', out.getvalue() if stdout else err.getvalue())
        self.assertNotIn('Traceback', out.getvalue() + err.getvalue())

    def test_joulewise_cli_catches_the_base_stop(self):
        args = SimpleNamespace(func=mock.Mock(side_effect=restore.StorageStop('fixture storage cause')))
        err = io.StringIO()
        with mock.patch.object(cli, 'build_parser') as parser, redirect_stderr(err):
            parser.return_value.parse_args.return_value = args
            self.assertEqual(cli.main([]), 2)
        self.assertEqual(err.getvalue(), 'refused: restore_refused: fixture storage cause\n')

    def test_campaign_main_reports_stop(self):
        args = SimpleNamespace(repair_campaign_provenance=False, check_prompt_hashes=None,
                               record_supersession=None, derive_neg8_drift_bound=None,
                               whole_window_verdict=False)
        with mock.patch.object(run_campaign, 'parse_args', return_value=args):
            self.check_main(run_campaign, args, 'run_campaign', 2)

    def test_b6_main_reports_stop_from_every_phase(self):
        args = SimpleNamespace(plan=Path('plan'), registration_dir=Path('registration'),
            archive_root=Path('archive'), workers=1, allow_missing_terminal=False,
            smoke=True, pack_records_root=Path('pack'), export_dir=Path('export'), non_claim=True)
        with mock.patch.object(harvest_b6_session.registration, 'load', return_value=None), \
             mock.patch.object(harvest_b6_session, 'resolve_inputs', return_value=object()):
            self.check_main(harvest_b6_session, args, 'harvest', 3)
            with mock.patch.object(harvest_b6_session, 'harvest', return_value={}), \
                 mock.patch.object(Path, 'read_text', return_value='{}'):
                self.check_main(harvest_b6_session, args, 'accept_archive', 4)
                result = SimpleNamespace(record={}, verdict='PASS')
                with mock.patch.object(harvest_b6_session, 'accept_archive', return_value=(result, {})):
                    self.check_main(harvest_b6_session, args, 'export', 5)

    def test_bytes_analysis_main_reports_stop(self):
        args = SimpleNamespace(export=Path('export'), records=None, manifest=Path('manifest'),
                               stage='blinded', out=Path('out'), key_dir=None,
                               predictions=None, stage1_commit=None)
        with mock.patch.object(bytes_analyze.ba, 'read_json', return_value={}), \
             mock.patch.object(bytes_analyze.ba, 'validate_manifest', return_value={}):
            self.check_main(bytes_analyze, args, '_reduce', 1)

    def test_v5_harvest_main_reports_stop(self):
        self.check_main(harvest_v5_g2b_window, SimpleNamespace(), 'harvest', 3)

    def test_b5_harvest_main_reports_stop_from_resolution_and_harvest(self):
        args = SimpleNamespace(**{name: None for name in harvest_b5_window.OVERRIDES},
            plan=Path('plan'), archive_root=Path('archive'), thresholds=None,
            workers=1, prepare_desk=False, skip_g3=False, allow_missing_terminal=False)
        for seam in ('resolve_inputs', 'harvest'):
            with self.subTest(seam=seam), \
                 mock.patch.object(harvest_b5_window, 'build_parser') as parser, \
                 mock.patch.object(harvest_b5_window.h, 'resolve_inputs', return_value=object()), \
                 mock.patch.object(harvest_b5_window.h, seam,
                                   side_effect=restore.StorageStop('fixture storage cause')), \
                 redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                parser.return_value.parse_args.return_value = args
                self.assertEqual(harvest_b5_window.main([]), 3)
            self.assertEqual(err.getvalue(), 'refused: restore_refused: fixture storage cause\n')
            self.assertEqual(out.getvalue(), '')

    def test_floor_extraction_main_reports_stop_without_writing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec, output = root / 'spec.json', root / 'output/report.json'
            spec.write_text('{}')
            with mock.patch.object(extract_detection_floors, 'extract_cells',
                                   side_effect=restore.StorageStop('fixture storage cause')), \
                 redirect_stderr(io.StringIO()) as err:
                code = extract_detection_floors.main([
                    '--runs-root', str(root), '--spec', str(spec), '--out', str(output)])
            self.assertEqual(code, 2)
            self.assertEqual(err.getvalue(), 'refused: restore_refused: fixture storage cause\n')
            self.assertFalse(output.parent.exists())

    def test_survivor_archive_reader_propagates_stop_without_library_logging(self):
        from joulewise import whole_window
        from joulewise.b6 import survivor_screen
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / 'sources/claim-runs/run'
            bundle.mkdir(parents=True)
            (bundle / 'summary_metrics.json').write_text('{}')
            with mock.patch.object(whole_window, '_neg8_writer_reference_energy', None, create=True), \
                 mock.patch.object(whole_window, '_reference_energy_evidence',
                                   side_effect=restore.StorageStop('fixture storage cause')), \
                 redirect_stderr(io.StringIO()) as err:
                with self.assertRaisesRegex(restore.StorageStop, 'fixture storage cause'):
                    survivor_screen.archive_energy_of(root)({'run_id': 'run'})
            self.assertEqual(err.getvalue(), '')

    def test_twin_independent_storage_stop_escapes_data_handler(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'run'
            source.mkdir()
            (source / 'raw.plist.zst').write_bytes(b'fixture')
            with self.assertRaisesRegex(bytes_twin.StorageStop, 'restore_refused: .*compression.jsonl'):
                try:
                    with bytes_twin._readable_bundle(source, Path(tmp) / 'compression.jsonl'):
                        self.fail('missing custody reached reader')
                except Exception:
                    self.fail('twin storage stop became a data decision')
        args = SimpleNamespace(export=[Path('fixture.csv')], export_dir=None)
        self.check_main(bytes_twin, args, 'read_export', 1, stdout=True, error_type=bytes_twin.StorageStop)

    def test_operator_restore_formats_storage_stop(self):
        args = SimpleNamespace(command=['reader', '{run}'], run_dir=Path('run'),
                               scratch_dir=Path('scratch'), compression_records=None, reserve_gib=40)
        err = io.StringIO()
        with mock.patch.object(restore_run_to_scratch.argparse.ArgumentParser, 'parse_args', return_value=args), \
             mock.patch.object(restore_run_to_scratch, 'restored_run', side_effect=restore.StorageStop('fixture cause')), \
             redirect_stderr(err), self.assertRaises(SystemExit) as caught:
            restore_run_to_scratch.main([])
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(err.getvalue(), 'restore-to-scratch: restore_refused: fixture cause\n')
