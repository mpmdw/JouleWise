"""Run-scoped content-addressed caches (L9-SPEEDUP-R1 stage 1).

Synthetic only: the committed S10 ALPHA member used by test_shared_physics_cache.
Every cache is inert outside a run; inside one a hit needs the same bytes.
"""
import contextlib
import contextvars
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import analysis_run_cache as arc, cli, environment_admission as ea
from joulewise import powermetrics_fiducial as pf, whole_window as ww
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER, JumpingClock, sha


def _cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = cli.main([str(arg) for arg in argv])
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


class _Member(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='run-caches-')
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(root, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)],
                            filter='data')
        cls.member = root / MEMBER
        cls.serial = 0

    def target(self):
        type(self).serial += 1
        return Path(self.tmp.name) / f'out-{self.serial}.json'

    def count_refits(self):
        calls = []
        original = pf.rederive_detection_from_artifacts

        def counted(*args, **kwargs):
            calls.append(1)
            return original(*args, **kwargs)
        patcher = mock.patch.object(pf, 'rederive_detection_from_artifacts', counted)
        patcher.start()
        self.addCleanup(patcher.stop)
        return calls


class RunPhysicsStoreTests(_Member):
    def test_inert_outside_a_run(self):
        self.assertFalse(arc.active())
        self.assertIsNone(arc.run_physics_store())
        self.assertIsNone(arc.memo('anything'))
        local = {}
        self.assertIs(arc.physics_cache_for_call(local, {'instrument_calibration': {'b_fiducial_s': 0.5}}), local)
        self.assertIsNone(arc.physics_cache_for_call(None, {'instrument_calibration': {'b_fiducial_s': 0.5}}))
        from joulewise import bundle_read
        with mock.patch.object(bundle_read, 'BundleReader') as reader:
            self.assertIsNone(cli._run_reduce_physics_cache(self.member))
            self.assertEqual(arc.run_reduce_physics_kwargs(self.member), {})
        reader.assert_not_called()

    def test_scope_is_reset_and_type_checked(self):
        with arc.analysis_run_caches({}) as caches:
            self.assertTrue(arc.active())
            self.assertIs(arc.run_physics_store(), caches.physics_store)
            with arc.analysis_run_caches({}) as inner:
                self.assertIs(arc.run_physics_store(), inner.physics_store)
            self.assertIs(arc.run_physics_store(), caches.physics_store)
        self.assertFalse(arc.active())
        with self.assertRaises(TypeError):
            with arc.analysis_run_caches([]):
                pass

    def test_an_isolated_replay_context_sees_the_run_store(self):
        metadata = {'instrument_calibration': {'b_fiducial_s': 0.5}}
        store = {}
        with ww.shared_instrument_calibration_physics_cache(store), arc.analysis_run_caches(store):
            outside = contextvars.Context().run(lambda: ww.physics_cache_for(None, metadata))
            self.assertIsNone(outside, 'whole_window alone drops the store in a fresh context')
            view = contextvars.Context().run(lambda: arc.physics_cache_for_call(None, metadata))
            view['k'] = 1.0
        self.assertEqual(store, {ww._effective_bound_partition(metadata): {'k': 1.0}})

    def test_fresh_context_strict_validation_and_reduce_share_one_fit(self):
        refits = self.count_refits()
        plain = [_cli('validate-bundle', '--strict', self.member), _cli('reduce', self.member, '--output', (t := self.target()))]
        plain_bytes = t.read_bytes()
        self.assertEqual(len(refits), 2)
        refits.clear()
        store = {}
        with ww.shared_instrument_calibration_physics_cache(store), arc.analysis_run_caches(store):
            isolated = contextvars.Context().run(lambda: [
                _cli('validate-bundle', '--strict', self.member),
                _cli('reduce', self.member, '--output', (u := self.target())), u])
        self.assertEqual(len(refits), 1, 'one verified fit serves both isolated calls')
        self.assertEqual([c[0] for c in isolated[:2]], [c[0] for c in plain])
        self.assertEqual(isolated[2].read_bytes(), plain_bytes)
        self.assertEqual([list(p) for p in store.values()],
                         [[sha(self.member / 'instrument_calibration/instrument_evidence.json')]])

    def test_a_deadline_hit_in_an_isolated_context_is_never_stored(self):
        store = {}
        with ww.shared_instrument_calibration_physics_cache(store), arc.analysis_run_caches(store), \
                mock.patch.object(pf, 'time', JumpingClock()):
            code = contextvars.Context().run(lambda: _cli('validate-bundle', '--strict', self.member))[0]
            contextvars.Context().run(lambda: _cli('reduce', self.member, '--output', self.target()))
        self.assertEqual(code, 2)
        self.assertEqual(store, {})


class ReferenceEnergyRefitTests(_Member):
    """Stage 4a: whole_window's NEG-8 reference-energy re-derivation shares the run store."""

    def test_reference_energy_evidence_shares_one_fit_and_is_unchanged(self):
        refits = self.count_refits()
        plain = [ww._reference_energy_evidence_detail(self.member) for _ in range(2)]
        self.assertEqual(len(refits), 2, 'without a run store each call refits')
        refits.clear()
        store = {}
        with ww.shared_instrument_calibration_physics_cache(store), arc.analysis_run_caches(store):
            shared = [ww._reference_energy_evidence_detail(self.member) for _ in range(2)]
            isolated = contextvars.Context().run(lambda: ww._reference_energy_evidence_detail(self.member))
        self.assertEqual(len(refits), 1, 'one verified fit serves every call, including an isolated context')
        self.assertEqual(shared, plain)
        self.assertEqual(isolated, plain[0])
        self.assertEqual(plain[0][2], None, plain[0])

    def test_a_deadline_hit_reference_refit_is_never_stored(self):
        store = {}
        with ww.shared_instrument_calibration_physics_cache(store), arc.analysis_run_caches(store), \
                mock.patch.object(pf, 'time', JumpingClock()):
            ww._reference_energy_evidence_detail(self.member)
        self.assertEqual(store, {})


class ContentKeyTests(unittest.TestCase):
    def test_canonical_key_is_exact(self):
        key = arc.canonical_key
        self.assertNotEqual(key([1]), key([1.0]))
        self.assertNotEqual(key([0.1]), key([0.30000000000000004 - 0.2]))
        self.assertNotEqual(key(['a', None]), key(['a', 'None']))
        self.assertEqual(key({'b': 1, 'a': [True]}), key({'a': [True], 'b': 1}))
        for bad in ([object()], [{1: 2}], [b'bytes']):
            with self.subTest(bad=bad), self.assertRaises((TypeError, ValueError)):
                key(bad)


class ThermalScanMemoTests(_Member):
    def scan(self, member=None):
        member = member or self.member
        metadata = json.loads((member / 'metadata.json').read_bytes())
        from joulewise.bundle_read import BundleReader
        window = BundleReader(member).measured_window()
        return ea._window_thermal_pressure_refusals(
            metadata, bundle_path=member,
            measured_window_start_s=window.start_s, measured_window_end_s=window.end_s)

    def test_memo_returns_the_uncached_result_and_needs_the_same_bytes(self):
        plain = self.scan()
        calls = []
        original = ea._thermal_pressure_intervals_refusals

        def counted(*args, **kwargs):
            calls.append(1)
            return original(*args, **kwargs)
        changed = Path(self.tmp.name) / 'changed' / self.member.name
        shutil.copytree(self.member, changed)
        raw = changed / 'raw/powermetrics.plist'
        raw.write_bytes(raw.read_bytes() + b'\0')
        with mock.patch.object(ea, '_thermal_pressure_intervals_refusals', counted), arc.analysis_run_caches({}):
            self.assertEqual(self.scan(), plain)
            self.assertEqual(self.scan(), plain)
            self.assertEqual(len(calls), 1)
            self.scan(changed)
            self.assertEqual(len(calls), 2, 'different raw bytes are a different key')
            self.assertEqual(arc.stats()['hits'], {ea._THERMAL_SCAN_MEMO: 1})
        self.assertEqual(self.scan(), plain)

    def test_an_exception_is_never_memoized(self):
        with arc.analysis_run_caches({}), \
                mock.patch.object(ea, '_thermal_pressure_intervals_refusals', side_effect=RuntimeError('x')):
            with self.assertRaises(RuntimeError):
                self.scan()
            self.assertEqual(arc.memo(ea._THERMAL_SCAN_MEMO), {})

    def test_reads_still_happen_on_a_hit(self):
        with arc.analysis_run_caches({}):
            self.scan()
            with mock.patch.object(ea, 'read_authentication_input', wraps=ea.read_authentication_input) as reads:
                self.scan()
        self.assertEqual(reads.call_count, 2, 'both plist reads are authenticated reads on every call')


class StrictClockEvidenceMemoTests(_Member):
    def test_memo_hit_is_a_copy_and_problems_are_unchanged(self):
        from joulewise.bundle_read import BundleReader
        plain = cli._strict_uncertainty_evidence_problems(BundleReader(self.member))
        with arc.analysis_run_caches({}):
            first = cli._strict_uncertainty_evidence_problems(BundleReader(self.member))
            (value,) = arc.memo(cli._STRICT_CLOCK_EVIDENCE_MEMO).values()
            snapshot = json.dumps(value, sort_keys=True)
            second = cli._strict_uncertainty_evidence_problems(BundleReader(self.member))
            self.assertEqual(json.dumps(value, sort_keys=True), snapshot)
            self.assertEqual(arc.stats()['hits'], {cli._STRICT_CLOCK_EVIDENCE_MEMO: 1})
        self.assertEqual((first, second), (plain, plain))

    def test_changed_raw_bytes_miss_the_memo(self):
        from joulewise.bundle_read import BundleReader
        changed = Path(self.tmp.name) / 'clock-changed' / self.member.name
        shutil.copytree(self.member, changed)
        raw = changed / 'raw/powermetrics.plist'
        raw.write_bytes(raw.read_bytes() + b'\0')
        plain = cli._strict_uncertainty_evidence_problems(BundleReader(changed))
        with arc.analysis_run_caches({}):
            cli._strict_uncertainty_evidence_problems(BundleReader(self.member))
            self.assertEqual(cli._strict_uncertainty_evidence_problems(BundleReader(changed)), plain)
            self.assertEqual(len(arc.memo(cli._STRICT_CLOCK_EVIDENCE_MEMO)), 2)
            self.assertEqual(arc.stats()['hits'], {})


if __name__ == '__main__':
    unittest.main()
