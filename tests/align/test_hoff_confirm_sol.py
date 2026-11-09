"""Confirmation controls for R17's session-link class; synthetic inputs only.

The nested-link assertion is an ordinary required-property test. Run this
module alone; it must pass before admitting the namespace-resolution repair.
"""
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from tests.align import synthetic_custody
from joulewise.align.apple import harvest_offload as off

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule
REAL_TMP = os.path.realpath(tempfile.gettempdir())


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class SessionNamespaceTests(unittest.TestCase):
    def round_trip(self, *, nested):
        with tempfile.TemporaryDirectory(prefix='hoff-confirm-sol-', dir=REAL_TMP) as temporary:
            base = Path(temporary)
            source = base / 'session'
            source.mkdir()
            original = b'{"synthetic":true}\n'
            (source / 'data.json').write_bytes(original)
            if nested:
                (source / 'current.json').symlink_to('data.json')
            alias = base / 'operator-current'
            alias.symlink_to(source / ('current.json' if nested else 'data.json'))
            (source / 'selected.json').symlink_to(alias)
            self.assertEqual((source / 'selected.json').read_bytes(), original)

            final = off.finalized_manifest(source)
            row = final['closure']['links']['selected.json']
            self.assertEqual(row['class'], 'session')
            self.assertEqual(len(row['hops']), 3 if nested else 2)
            off.pack(source, base / 'offload', finalized=final, threads=1)
            source.rename(base / 'original-kept')
            # Exactly the normal same-path restore: no receiver mutation,
            # alias change, forged manifest or concurrently changing input.
            try:
                off.unpack(base / 'offload', finalized=final,
                           finalized_sha256=off.manifest_sha256(final))
            except off.OffloadRefused as error:
                self.assertFalse(source.exists(), 'a refused restore must stay unpublished')
                self.fail(f'unchanged session-link chain must restore: {error}')
            self.assertEqual((source / 'selected.json').read_bytes(), original)

    def test_unchanged_external_alias_to_session_file_restores(self):
        self.round_trip(nested=False)

    def test_unchanged_external_alias_to_session_symlink_restores(self):
        self.round_trip(nested=True)


class DeclaredInputTests(unittest.TestCase):
    def test_declared_input_dotdot_refuses(self):
        with tempfile.TemporaryDirectory(prefix='hoff-confirm-sol-', dir=REAL_TMP) as temporary:
            base = Path(temporary)
            source = base / 'session'
            source.mkdir()
            (base / 'directory').mkdir()
            (base / 'input.json').write_bytes(b'{}')
            with self.assertRaisesRegex(off.OffloadRefused, 'without'):
                off.finalized_manifest(source, inputs=(base / 'directory/../input.json',))


if __name__ == '__main__':
    unittest.main()
