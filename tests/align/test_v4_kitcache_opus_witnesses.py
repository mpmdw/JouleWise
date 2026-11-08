"""Opus cold-review witnesses for perf/2026-11-08-eng-kitcache.

Failing-first on 27d4aa40f; passing on the baseline (no cache) and after the
recommended fix (drop the caches, keep batched Git reads). Synthetic Git
repositories and synthetic text only; no study data, models or restricted paths.
See docs/perf/2026-11-08-opus-review-kitcache.md.
"""
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_v4_kit as kit
from joulewise.align.apple import v4_registration as reg


def _git(root, *args):
    return subprocess.run(['git', *args], cwd=root, check=True,
                          capture_output=True).stdout.decode().strip()


def _receipt_fixture(root):
    paths = [*reg.ARTIFACTS, 'docs/align/v4/gate-A.md', 'docs/align/v4/gate-B.md']
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('synthetic input: ' + path + '\n')
    _git(root, 'init', '-q')
    _git(root, 'add', '.')
    _git(root, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
         'commit', '-qm', 'Synthetic registration')
    hashes = {p: reg.digest((root / p).read_bytes()) for p in paths}
    return dict(schema=reg.RECEIPT_SCHEMA, status='registered', commit=_git(root, 'rev-parse', 'HEAD'),
                artifacts={p: hashes[p] for p in reg.ARTIFACTS},
                rulings={str(n): 'installed' for n in reg.RULINGS},
                gates={s: dict(verdict='ADMIT', path=f'docs/align/v4/gate-{s}.md',
                               sha256=hashes[f'docs/align/v4/gate-{s}.md']) for s in ('A', 'B')},
                lead_signature='lead: synthetic-test 2026-11-08')


class AdmissionPathNeverConsultsReceiptCache(unittest.TestCase):
    """HIGH-1: kit --check -> require_w1_ready -> require_registration ->
    validate_receipt(receipt, root) runs with the cache enabled, so the admission
    gate is not cache-independent."""

    def test_require_registration_validates_receipt_without_cache(self):
        if 'cache' not in inspect.signature(reg.validate_receipt).parameters:
            return  # no receipt cache exists: property holds trivially
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / reg.REGISTRATION / 'registration_receipt.json'
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps({'schema': 'synthetic'}))
            seen = {}

            def record(receipt, root, **kwargs):
                seen.update(kwargs)
                raise RuntimeError('recorded')
            with patch.object(reg, 'validate_receipt', side_effect=record):
                with self.assertRaisesRegex(RuntimeError, 'recorded'):
                    reg.require_registration(root)
            self.assertIs(seen.get('cache'), False,
                          'admission must validate committed bytes fresh, never from build/ cache')

    def test_planted_cache_entry_cannot_turn_commit_drift_into_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = _receipt_fixture(root)
            # Working bytes change after the commit and the receipt is re-pointed
            # at them: the working check passes, the committed check must refuse.
            path = reg.ARTIFACTS[0]
            (root / path).write_text('uncommitted reviewed bytes\n')
            receipt['artifacts'][path] = reg.digest((root / path).read_bytes())
            kwargs = {'cache': False} if 'cache' in inspect.signature(reg.validate_receipt).parameters else {}
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                reg.validate_receipt(receipt, root, **kwargs)
            if hasattr(reg, '_cache_store') and hasattr(reg, '_committed_oids'):
                # A local process with write access to build/ plants an entry.
                # The entry's checksum is a plain SHA-256, not an authenticator.
                bindings = dict(receipt['artifacts'])
                for gate in receipt['gates'].values():
                    bindings[gate['path']] = gate['sha256']
                oids = reg._committed_oids(root, receipt['commit'], list(bindings))
                key = reg._cache_key(dict(
                    receipt=receipt, oids=oids, python=sys.version,
                    validator=reg.digest(Path(reg.__file__).read_bytes()),
                    kit=reg.digest(Path(sys.modules['scripts.align_v4_kit'].__file__).read_bytes())))
                reg._cache_store(root, 'receipt', key, bindings)
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                reg.validate_receipt(receipt, root)


class GenerationCacheNeverMasksExecutingRefusal(unittest.TestCase):
    """MED-1: the generation key hashes code on disk, not the code executing.
    A refusal raised by the running builder (patched here; a long-lived process
    after a checkout in production) is masked by a warm entry."""

    def test_warm_output_root_still_runs_the_builders_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit.generate(root)
            with patch.object(kit, 'check_window_reference_roles',
                              side_effect=ValueError('witness refusal')):
                with self.assertRaisesRegex(ValueError, 'witness refusal'):
                    kit.generate(root)


if __name__ == '__main__':
    unittest.main()
