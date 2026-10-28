"""One instrument-calibration physics cache per analysis run (ED-RULING item 1, amended 2026-10-27).

Synthetic only: one committed S10 ALPHA member (neg8-window-end-r1, the reference
whose bracket-calibration refit stopped step 9b) is extracted from its committed
archive. The cache key and the hash checks before it stay in the governed reducer.
"""
import contextlib
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

from joulewise import cli, powermetrics_fiducial as pf, whole_window as ww
from joulewise.b5_analysis import dry_run as d

ARCHIVE = d.ROOT / 'tests/fixtures/b5_analysis/s10/alpha/archive.tar.xz'
MEMBER = 'archive/sources/night-custody/runs_claim/neg8-window-end-r1/'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class JumpingClock(types.ModuleType):
    """powermetrics_fiducial's clock only: every budget check sees +1000 s (a slow host)."""

    def __init__(self):
        super().__init__('time')
        self._now = time.monotonic()

    def monotonic(self):
        self._now += 1000.0
        return self._now

    def __getattr__(self, name):
        return getattr(time, name)


class SharedPhysicsCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='shared-physics-cache-')
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        with tarfile.open(ARCHIVE) as blob:
            members = [m for m in blob.getmembers() if m.name.startswith(MEMBER)]
            blob.extractall(root, members=members, filter='data')
        cls.member = root / MEMBER
        cls.evidence = cls.member / 'instrument_calibration/instrument_evidence.json'

    def setUp(self):
        self.refits = 0
        original = pf.rederive_detection_from_artifacts

        def counted(*args, **kwargs):
            self.refits += 1
            return original(*args, **kwargs)
        patcher = mock.patch.object(pf, 'rederive_detection_from_artifacts', counted)
        patcher.start()
        self.addCleanup(patcher.stop)

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli.main([str(arg) for arg in argv])
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def outputs(self, label):
        """Step-1 and step-2 programs exactly as the driver dispatches them."""
        target = Path(self.tmp.name) / (label + '.reduced.json')
        validate = self.cli('validate-bundle', '--strict', self.member)
        reduced = self.cli('reduce', self.member, '--output', target)
        return validate, reduced, target.read_bytes()

    def test_cached_and_uncached_step_outputs_are_byte_identical(self):
        uncached = self.outputs('uncached')
        self.assertEqual(self.refits, 2)
        self.assertEqual(uncached[0][0], 0, uncached[0])
        self.refits = 0
        cache = {}
        with ww.shared_instrument_calibration_physics_cache(cache):
            cold = self.outputs('cold')
            self.assertEqual(self.refits, 1, 'one verified refit serves both programs')
            warm = self.outputs('warm')
        self.assertEqual(self.refits, 1, 'a warm shared cache refits nothing')
        # One partition (the member's exact metadata bound), holding one verified fit.
        self.assertEqual([list(partition) for partition in cache.values()], [[sha(self.evidence)]])
        for other in (cold, warm):
            self.assertEqual(other[0], uncached[0])
            self.assertEqual(other[1][0], uncached[1][0])
            self.assertEqual(other[2], uncached[2])

    def test_deadline_hit_fit_is_never_cached(self):
        cache = {}
        with ww.shared_instrument_calibration_physics_cache(cache), \
             mock.patch.object(pf, 'time', JumpingClock()):
            code, out, _ = self.cli('validate-bundle', '--strict', self.member)
            self.assertEqual(code, 2, out)
            self.assertEqual(cache, {})
            self.cli('reduce', self.member, '--output', Path(self.tmp.name) / 'forced.json')
            self.assertEqual(cache, {})
        self.assertEqual(self.refits, 2)

    def test_cache_hit_requires_the_content_hash_key(self):
        bound = json.loads(self.evidence.read_bytes())['b_fiducial_s']
        raw = self.member / 'instrument_calibration/raw/powermetrics.plist'
        # Keys without the evidence artifact's content hash: its path, the raw
        # capture's hash, and a hash of a different document. None is a hit.
        for key in ('instrument_calibration/instrument_evidence.json', sha(raw),
                    hashlib.sha256(self.evidence.read_bytes() + b' ').hexdigest()):
            with self.subTest(key=key):
                self.refits = 0
                partition = ww._effective_bound_partition(
                    json.loads((self.member / 'metadata.json').read_bytes()))
                cache = {partition: {key: bound}}
                with ww.shared_instrument_calibration_physics_cache(cache):
                    self.cli('validate-bundle', '--strict', self.member)
                self.assertEqual(self.refits, 1)
                self.assertIn(sha(self.evidence), cache[partition])

    def test_cached_bound_never_admits_changed_capture_bytes(self):
        copy = Path(self.tmp.name) / 'changed' / self.member.name
        shutil.copytree(self.member, copy)
        cache = {}
        with ww.shared_instrument_calibration_physics_cache(cache):
            self.assertEqual(self.cli('validate-bundle', '--strict', self.member)[0], 0)
            events = copy / 'instrument_calibration/events.jsonl'
            events.write_bytes(events.read_bytes() + b'\n')
            code, out, _ = self.cli('validate-bundle', '--strict', copy)
        self.assertEqual(code, 2, out)

    def test_whole_window_strict_validation_shares_the_run_cache(self):
        ww.strict_validate_bundles([self.member], workers=1)
        ww.strict_validate_bundles([self.member], workers=1)
        self.assertEqual(self.refits, 2, 'without a run cache each call refits')
        self.refits = 0
        with ww.shared_instrument_calibration_physics_cache({}):
            ww.strict_validate_bundles([self.member], workers=1)
            ww.strict_validate_bundles([self.member], workers=1)
        self.assertEqual(self.refits, 1)

    def test_cache_scope_is_reset_and_type_checked(self):
        self.assertIsNone(ww.shared_physics_cache())
        with ww.shared_instrument_calibration_physics_cache({}) as cache:
            self.assertIs(ww.shared_physics_cache(), cache)
        self.assertIsNone(ww.shared_physics_cache())
        with self.assertRaises(TypeError):
            with ww.shared_instrument_calibration_physics_cache(None):
                pass


class DriverRunCacheScopeTests(unittest.TestCase):
    def test_each_driver_run_has_its_own_cache_for_every_step(self):
        seen = []

        def probe(s, r):
            seen.append(ww.shared_physics_cache())
            return [s.record('0')]
        with tempfile.TemporaryDirectory(prefix='shared-cache-driver-') as tmp:
            root = Path(tmp)
            (root / 'repo').mkdir()
            index = root / 'index.json'
            index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
            with mock.patch.object(d, 'STEPS', [('0', probe), ('1', probe)]), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                for name in ('first', 'second'):
                    try:
                        d.run('blind-dry-run', index, root / name, _test_repo_root=root / 'repo',
                              _git=lambda repo: 'b' * 40)
                    except Exception:  # noqa: BLE001 - only the probe's observation matters
                        pass
        self.assertEqual(len(seen), 4)
        self.assertTrue(all(isinstance(cache, dict) for cache in seen))
        self.assertIs(seen[0], seen[1])
        self.assertIs(seen[2], seen[3])
        self.assertIsNot(seen[0], seen[2])
        self.assertIsNone(ww.shared_physics_cache())


if __name__ == '__main__':
    unittest.main()


class MetadataBoundPartitionTests(unittest.TestCase):
    """L9-SOL-REV MAJOR-1: the run cache must not carry one bundle's metadata bound into another's.

    The reducer caches max(metadata b_fiducial_s, fresh bound) under the evidence
    artifact's hash and accepts a metadata bound within 1e-12 of the artifact's.
    Two bundles with the same calibration evidence and metadata bounds 5e-13 apart
    must reduce and strict-validate exactly as they do with no run cache.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='bound-partition-')
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(root, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)], filter='data')
        cls.low = root / MEMBER
        cls.high = root / 'high'
        shutil.copytree(cls.low, cls.high)
        metadata = json.loads((cls.high / 'metadata.json').read_bytes())
        metadata['instrument_calibration']['b_fiducial_s'] += 5e-13
        (cls.high / 'metadata.json').write_text(json.dumps(metadata))
        # The higher-bound bundle's stored summary is its own real re-reduction
        # (reduce refuses to write inside its input bundle).
        code, summary = cls.reduce(cls.high, root / 'high-summary.json')
        assert code == 0
        (cls.high / 'summary_metrics.json').write_bytes(summary)

    @staticmethod
    def reduce(bundle, output):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = cli.main(['reduce', str(bundle), '--output', str(output)])
        return code, Path(output).read_bytes()

    @staticmethod
    def strict(bundle):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            try:
                code = cli.main(['validate-bundle', '--strict', str(bundle)])
            except SystemExit as exc:
                code = exc.code
        return code

    def test_a_higher_bound_seed_does_not_change_the_other_bundle(self):
        root = Path(self.tmp.name)
        plain = self.reduce(self.low, root / 'plain.json')
        with ww.shared_instrument_calibration_physics_cache({}) as store:
            self.reduce(self.high, root / 'seed.json')
            shared = self.reduce(self.low, root / 'shared.json')
            self.assertEqual((self.strict(self.high), self.strict(self.low)), (0, 0))
        self.assertEqual(shared, plain)
        self.assertEqual(len(store), 2, 'one partition per exact metadata bound')
        self.assertEqual((self.strict(self.high), self.strict(self.low)), (0, 0))

    def test_cross_call_reuse_within_one_bound_still_avoids_refits(self):
        calls = []
        original = pf.rederive_detection_from_artifacts

        def counted(*args, **kwargs):
            calls.append(1)
            return original(*args, **kwargs)
        with mock.patch.object(pf, 'rederive_detection_from_artifacts', counted), \
             ww.shared_instrument_calibration_physics_cache({}):
            for bundle in (self.low, self.high, self.low, self.high):
                self.assertEqual(self.strict(bundle), 0)
        self.assertEqual(len(calls), 2, 'one refit per distinct (evidence, metadata bound)')

    def test_a_call_keeps_its_own_previous_semantics(self):
        # whole_window/bracket sites shared one dict across a call's members before
        # the run cache existed; that local dict still decides first.
        local = {}
        with ww.shared_instrument_calibration_physics_cache({}):
            first = ww.physics_cache_for(local, {'instrument_calibration': {'b_fiducial_s': 0.5}})
            first['key'] = 0.5
            second = ww.physics_cache_for(local, {'instrument_calibration': {'b_fiducial_s': 0.25}})
            self.assertEqual(second.get('key'), 0.5)
            fresh = ww.physics_cache_for(None, {'instrument_calibration': {'b_fiducial_s': 0.25}})
            self.assertIsNone(fresh.get('key'))
            self.assertEqual(ww.physics_cache_for({}, {'instrument_calibration': {'b_fiducial_s': 0.5}}).get('key'), 0.5)
            self.assertIs(ww.physics_cache_for(local, {'instrument_calibration': {}}), local)
        self.assertIs(ww.physics_cache_for(local, {'instrument_calibration': {'b_fiducial_s': 0.5}}), local)
