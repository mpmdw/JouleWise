"""Synthetic regressions for the cold FIX-573f re-check's low findings."""
from contextlib import redirect_stderr
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import pickle
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import authentication_io as auth, desk_compress as desk, desk_restore as restore
from joulewise import whole_window as ww
from joulewise.b5 import harvest
from joulewise.bundle_read import BundleReader


ROOT = Path(__file__).resolve().parents[1]


def _mixed_restore_worker(source, journal, scratch, reader, entered, release, started, checked, results):
    """Hold a materialization open; the other restore must wait to check space."""
    def disk_usage(_path):
        if reader:
            checked.set()
        return SimpleNamespace(free=1024**4)

    copy = restore._copy
    def blocked_copy(*args):
        if not reader:
            entered.set()
            if not release.wait(10):
                raise RuntimeError('operator copy release timed out')
        return copy(*args)

    try:
        with mock.patch.object(restore.shutil, 'disk_usage', side_effect=disk_usage), \
             mock.patch.object(restore, '_copy', side_effect=blocked_copy):
            context = (restore.readable_run(source, compression_records=journal) if reader else
                       restore.restored_run(source, scratch, compression_records=journal))
            if reader:
                started.set()
            with context as plain:
                results.put((reader, (plain / 'metadata.json').is_file()))
    except Exception as exc:
        results.put(str(exc))


class StopIdentityTests(unittest.TestCase):
    def test_compressed_stop_is_a_restore_refusal_and_survives_repeated_pickling(self):
        exc = auth.CompressedBundleRequiresRestore('/fixture/member/events.jsonl')
        expected = 'restore_refused: compressed_bundle_requires_restore: /fixture/member/events.jsonl'
        for _ in range(3):
            self.assertIsInstance(exc, restore.RestoreRefused)
            self.assertEqual(str(exc), expected)
            self.assertEqual(exc.reason, expected.removeprefix('restore_refused: '))
            exc = pickle.loads(pickle.dumps(exc))


@unittest.skipUnless(Path(desk.zstd_path()).is_file(), 'zstd CLI required')
class ColdReviewProbe3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.test_p2038_production_path import P2038ProductionPathTests
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.source, _ = P2038ProductionPathTests().run_mode(cls.root / 'primary', 'normal')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.tmp.cleanup)
        self.case = Path(self.tmp.name)
        self.archive, custody = self.case / 'archive', self.case / 'custody'
        (self.archive / 'sources').mkdir(parents=True)
        (self.archive / 'harvest.json').write_text('{"verdict":"COLLECTED"}\n')
        (custody / 'night').mkdir(parents=True)
        (custody / 'night/chain.exited').write_text('{}\n')
        self.live = self.case / 'live-runs/corpus0'
        shutil.copytree(self.source, self.live)
        (self.live / 'rich_telemetry_idle.jsonl').write_text('{"fixture":1}\n')
        self.journal = Path(str(self.archive) + '.desk') / 'compression.jsonl'
        self.kwargs = {'compression_records': self.journal}
        self.plain = self.values()
        rc, report = desk.compress(archive=self.archive, custody=custody,
                                   runs_roots=[self.live.parent], min_bytes=0)
        self.assertEqual(rc, 0, report)
        self.assertGreater(report['files'], 0)
        self.space = mock.patch.object(restore.shutil, 'disk_usage',
                                       return_value=SimpleNamespace(free=1024**4))
        self.space.start()
        self.addCleanup(self.space.stop)

    def reads(self, **kwargs):
        return [lambda: ww._measured_window_end_s(self.live, **kwargs),
                lambda: ww._load_idle_records(self.live, 1, **kwargs),
                *(lambda name=name: ww._read_json_object(self.live / name, **kwargs)
                  for name in ('summary_metrics.json', 'metadata.json', 'config.json')),
                lambda: ww._bundle_evidence_sha256(self.live, **kwargs),
                lambda: ww.custody_telemetry_identity(self.live, **kwargs),
                lambda: ww._scientific_config_identity(self.live, **kwargs)]

    def values(self, **kwargs):
        return [read() for read in self.reads(**kwargs)]

    def test_probe3_b_c_e_primary_reads_equal_plain_with_explicit_archive_journal(self):
        self.assertIsNotNone(self.plain[0])
        self.assertEqual(self.values(**self.kwargs), self.plain)
        with restore.readable_run(self.live, **self.kwargs) as plain:
            self.assertEqual(ww._plain_bundle_evidence_sha256(plain), self.plain[5])
        for read in self.reads():
            with self.assertRaisesRegex(restore.RestoreRefused, 'compression.jsonl'):
                read()

    def test_probe3_d_exact_reserve_and_one_byte_short(self):
        entries = restore._inventory(self.live.resolve(), restore._records(self.journal))
        needed = restore.MIN_RESERVE_GIB * 1024**3 + sum(row[4] for row in entries)
        for read, expected in zip(self.reads(**self.kwargs), self.plain):
            with mock.patch.object(restore.shutil, 'disk_usage', return_value=SimpleNamespace(free=needed)):
                self.assertEqual(read(), expected)
            with mock.patch.object(restore.shutil, 'disk_usage', return_value=SimpleNamespace(free=needed - 1)):
                with self.assertRaisesRegex(restore.RestoreRefused, 'insufficient scratch space'):
                    read()

    def test_digest_mismatch_stops_primary_reads_instead_of_missing_evidence(self):
        rows = [json.loads(line) for line in self.journal.read_text().splitlines()]
        changed = False
        for row in rows:
            if row.get('path') == str((self.live / 'metadata.json').resolve()):
                row['sha256'] = '0' * 64
                changed = True
        self.assertTrue(changed)
        self.journal.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        for read in self.reads(**self.kwargs):
            with self.assertRaisesRegex(restore.RestoreRefused, 'restored size or digest mismatch'):
                read()

    def replay_inputs(self):
        policy_raw = (ROOT / 'configs/campaign_policies/quiet_mac_p2_production.json').read_bytes()
        policy_sha = hashlib.sha256(policy_raw).hexdigest()
        manifest = {'campaign_policy': {'sha256': policy_sha},
                    'members': [{'execution': 'invoked', 'bundle_ids': ['corpus0']}]}
        core = {'schema_version': ww.IDLE_ADMISSION_CORE_SCHEMA, 'policy_sha256': policy_sha}
        return policy_sha, manifest, core

    def test_probe3_f_g_real_harvest_verdict_replay_stops_with_compressed_member_cause(self):
        policy_sha, manifest, core = self.replay_inputs()
        raw_manifest = json.dumps(manifest).encode()
        row = {'record_type': 'idle_admission_whole_window_verdict',
               'schema_version': ww.WHOLE_WINDOW_SCHEMA, 'status': 'passed',
               'bundle_ids': ['corpus0'], 'campaign_policy': {'sha256': policy_sha},
               'idle_admission_core': core,
               'row_provenance': {'source_campaign_manifests': [
                   {'path': 'campaign_manifests/fixture.json',
                    'sha256': hashlib.sha256(raw_manifest).hexdigest()}]}}
        raw = json.dumps(row).encode() + b'\n'
        (self.live.parent / 'whole-window-verdict.json').write_bytes(raw)
        (self.live.parent / 'campaign_log.jsonl').write_bytes(raw)
        fake = SimpleNamespace(archive=self.archive,
                               inputs=SimpleNamespace(claim_runs_root=self.live.parent),
                               emit=mock.Mock(), _record_error=mock.Mock())
        def replay(*_args, **_kwargs):
            harvest._Harvest.step(fake, 'whole_window', lambda: harvest._Harvest.whole_window(fake))
        err = io.StringIO()
        with mock.patch.object(ww, 'load_authenticated_campaign_manifest',
                               return_value=SimpleNamespace(raw_bytes=raw_manifest, value=manifest)), \
             mock.patch.object(harvest, '_harvest', side_effect=replay), redirect_stderr(err):
            with self.assertRaisesRegex(auth.CompressedBundleRequiresRestore, 'compressed_bundle_requires_restore'):
                harvest.harvest(None, self.archive)
        self.assertIn('compressed_bundle_requires_restore:', err.getvalue())
        fake.emit.assert_not_called()
        fake._record_error.assert_not_called()
        with self.assertRaises(auth.CompressedBundleRequiresRestore):
            BundleReader(self.live)

    def test_current_environment_replay_restores_with_journal_and_passes_late_refusal(self):
        policy_sha, manifest, core = self.replay_inputs()
        kwargs = dict(core=core, bundle_ids=['corpus0'], manifests=[manifest],
                      runs_root=self.live.parent, policy_sha256=policy_sha, **self.kwargs)
        def environment(_metadata, *, bundle_path, **_kwargs):
            self.assertFalse(list(bundle_path.rglob('*.zst')))
            self.assertEqual(BundleReader(bundle_path).metadata(), self.plain[3])
            return ()
        with mock.patch.object(ww, 'current_environment_refusals', side_effect=environment) as check, \
             mock.patch.object(ww, 'calibration_bracket_for_bundles', return_value=({'b_fiducial_s': 1}, ())), \
             mock.patch.object(ww, '_verify_instrument_calibration', side_effect=restore.RestoreRefused('late replay')):
            with self.assertRaisesRegex(restore.RestoreRefused, 'late replay'):
                ww._current_core_rederivation_reasons(**kwargs)
        check.assert_called_once()

    def test_prepare_plain_passes_calibration_restore_refusal(self):
        with restore.readable_run(self.live, **self.kwargs) as plain:
            session = ww.AuthenticatedConsumptionSession(
                plain.parent, {'corpus0'},
                calibration_ledger_snapshot=SimpleNamespace(refusal_reasons=()),
            )
            policy = ww.CampaignPolicy.from_mapping(json.loads(
                (ROOT / 'configs/campaign_policies/quiet_mac_p2_production.json').read_bytes()))
            with mock.patch.object(ww, 'calibration_bracket_for_bundles', return_value=({'b_fiducial_s': 1}, ())), \
                 mock.patch.object(ww, '_verify_instrument_calibration', side_effect=restore.RestoreRefused('late prepare')):
                with self.assertRaisesRegex(restore.RestoreRefused, 'late prepare'):
                    session._prepare_plain(bundle_paths={'corpus0': plain}, policy=policy,
                                           original_paths={'corpus0': self.live})

    def test_evaluation_basis_primary_hashes_restore_with_the_archive_journal(self):
        occurrence = {'bundle_id': 'corpus0', 'bundle_path': 'corpus0'}
        for name, field in (('config.json', 'config_sha256'), ('metadata.json', 'metadata_sha256'),
                            ('summary_metrics.json', 'summary_sha256')):
            occurrence[field] = hashlib.sha256((self.source / name).read_bytes()).hexdigest()
        basis = {'schema_version': ww.WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA,
                 'policy_sha256': 'a' * 64, 'member_occurrences': [occurrence],
                 'calibration_bracket_set': ww._calibration_bracket_basis(None)}
        basis['sha256'] = ww.canonical_sha256(basis)
        row = {'evaluation_basis': basis, 'campaign_policy': {'sha256': 'a' * 64},
               'bundle_ids': ['corpus0'], 'evaluation_scope': {
                   'runs_root': str(self.live.parent.resolve()), 'started_at': 'fixture',
                   'completed_at': 'fixture'}}
        # Isolate primary hashing from the separate provenance validator.
        with mock.patch.object(ww, '_consumption_provenance_valid', return_value=True):
            self.assertEqual(ww._validated_evaluation_basis(row, self.live.parent, **self.kwargs), basis)
            with self.assertRaisesRegex(restore.RestoreRefused, 'compression.jsonl'):
                ww._validated_evaluation_basis(row, self.live.parent)

    def test_operator_and_reader_share_lock_with_different_scratch_directories(self):
        context = multiprocessing.get_context('fork')
        entered, release, started, checked = (context.Event() for _ in range(4))
        results = context.Queue()
        common = (self.live, self.journal, self.case / 'operator-scratch')
        operator = context.Process(target=_mixed_restore_worker,
                                   args=(*common, False, entered, release, started, checked, results))
        reader = context.Process(target=_mixed_restore_worker,
                                 args=(*common, True, entered, release, started, checked, results))
        operator.start()
        try:
            self.assertTrue(entered.wait(10))
            reader.start()
            self.assertTrue(started.wait(10))
            self.assertFalse(checked.wait(.2), 'reader checked reserve before operator finished copying')
            release.set()
            self.assertCountEqual([results.get(timeout=10), results.get(timeout=10)],
                                  [(False, True), (True, True)])
        finally:
            release.set()
            for process in (operator, reader):
                if process.pid:
                    process.join(10)
                    if process.is_alive():
                        process.kill()
                        process.join()
            results.close()
