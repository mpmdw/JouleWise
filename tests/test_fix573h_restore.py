"""Cold FIX-573g probes: realistic compression must preserve restore stops."""
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import desk_compress as desk, desk_restore as restore
from joulewise import floor_extraction as floor, whole_window as ww
from joulewise.bundle_read import BundleReader
from scripts import run_campaign as campaign
from tests.desk_restore_support import compress_member


@unittest.skipUnless(Path(desk.zstd_path()).is_file(), 'zstd CLI required')
class RealisticCompressedArchiveTests(unittest.TestCase):
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
        self.runs = Path(self.tmp.name) / 'runs'
        self.bundle = self.runs / 'corpus0'
        shutil.copytree(self.source, self.bundle)
        self.metadata = json.loads((self.bundle / 'metadata.json').read_bytes())
        self.summary = json.loads((self.bundle / 'summary_metrics.json').read_bytes())
        self.evaluation = SimpleNamespace(bundle_path=self.bundle,
                                          metadata=self.metadata, summary=self.summary)
        self.space = mock.patch.object(restore.shutil, 'disk_usage',
                                       return_value=SimpleNamespace(free=1024**4))
        self.space.start()
        self.addCleanup(self.space.stop)

    def compress(self):
        # The default desk threshold leaves small JSON plain. Compress a real
        # raw member only, with a journal discoverable from the runs root.
        compress_member(self.bundle / 'raw/powermetrics.plist', self.runs)
        for name in ('metadata.json', 'config.json', 'summary_metrics.json', 'events.jsonl'):
            self.assertTrue((self.bundle / name).is_file())
        with self.assertRaises(restore.RestoreRefused):
            BundleReader(self.bundle)

    def test_reference_span_stops_instead_of_returning_none(self):
        self.assertIsNotNone(campaign._reference_window_span(self.evaluation))
        self.compress()
        with self.assertRaisesRegex(restore.RestoreRefused, 'compressed_bundle_requires_restore'):
            campaign._reference_window_span(self.evaluation)

    def test_environment_consumers_pass_the_bundle_reader_stop(self):
        self.assertFalse(ww.custody_telemetry_identity(
            self.bundle, summary=self.summary, metadata=self.metadata).production_predicate_exempt)
        self.assertIn(self.summary['summary_provenance']['reducer_version'], {'0.5.2', '0.6.2'})
        self.compress()
        for read in (lambda: campaign._current_member_environment_refusals(self.evaluation),
                     lambda: floor._cpu_admission_bundle_reasons(self.bundle, self.summary)):
            with self.subTest(read=read):
                with self.assertRaisesRegex(restore.RestoreRefused, 'compressed_bundle_requires_restore'):
                    read()

    def test_common_mode_preserves_storage_cause_and_exception(self):
        self.compress()
        members = [SimpleNamespace(position=p, bundle_id='corpus0')
                   for p in ('A1', 'B1', 'B2', 'A2')]
        with self.assertRaisesRegex(restore.RestoreRefused, 'compressed_bundle_requires_restore'):
            floor._common_mode_block_inputs_from_evidence(
                members, runs_root=self.runs, metric='phase_energy_j.decode', shared_edge_bound_s=1)
