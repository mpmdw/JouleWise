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
        self.assertEqual(list(cache), [sha(self.evidence)])
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
                cache = {key: bound}
                with ww.shared_instrument_calibration_physics_cache(cache):
                    self.cli('validate-bundle', '--strict', self.member)
                self.assertEqual(self.refits, 1)
                self.assertIn(sha(self.evidence), cache)

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
