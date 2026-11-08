"""Final R17 delta review: synthetic CLI/closure witnesses only.

Run this module in its own process. Red tests assert required properties;
they are not expectedFailure markers. No real custody path is accessed.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tests.align import synthetic_custody
from joulewise.align.apple import harvest_offload as off
from scripts import align_v4_harvest_off as runner

setUpModule = synthetic_custody.setUpModule
tearDownModule = synthetic_custody.tearDownModule
REAL_TMP = os.path.realpath(tempfile.gettempdir())


class Scratch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hoff-delta2-sol1-', dir=REAL_TMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def checkout(self):
        checkout = self.root / 'checkout'
        checkout.mkdir()
        (checkout / '.gitignore').write_text('.venv/\nruns/\nignored-inputs/\n')
        (checkout / 'collector.py').write_text('VERSION = 1\n')
        (checkout / '.venv/bin').mkdir(parents=True)
        # The installed interpreter, with no installation or model download.
        (checkout / '.venv/bin/python').symlink_to(sys.executable)
        for args in (('init', '-q'), ('add', '.'), ('commit', '-qm', 'synthetic checkout')):
            subprocess.run(['git', '-c', 'user.name=Synthetic', '-c',
                            'user.email=synthetic@example.invalid', '-C', str(checkout), *args],
                           capture_output=True, check=True)
        return checkout

    def session(self, checkout, *, ledger=True):
        source = self.root / 'session'
        (source / 'custody/night').mkdir(parents=True)
        (source / 'custody/night/result.json').write_text('{}')
        (source / 'measurement').symlink_to(checkout, target_is_directory=True)
        bindings = {}
        if ledger:
            path = checkout / 'runs/ledger.jsonl'
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(b'{"ledger":1}\n')
            bindings['ledger_path'] = str(source / 'measurement/runs/ledger.jsonl')
        plan = {'custody_root': str(source / 'custody'), 'measurement_root': str(source / 'measurement'),
                'pack_root': str(source / 'pack'), 'claim_runs_root': str(source / 'captures'),
                'hazard_window': {'bindings': bindings}}
        (source / 'plan.json').write_text(json.dumps(plan))
        (source / 'session.json').write_text(json.dumps({'plan_path': str(source / 'plan.json'),
            'measurement_root': str(source / 'measurement'), 'source_measurement_root': str(checkout)}))
        return source

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.main(list(map(str, args)))
        return code, out.getvalue(), err.getvalue()


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class ProductionIgnoredInputsTests(Scratch):
    def test_declared_ledger_is_bound_and_transported_by_the_real_cli(self):
        checkout = self.checkout()
        source = self.session(checkout)
        manifest, transport = self.root / 'M.json', self.root / 'offload'
        code, out, err = self.cli('finalize-manifest', '--session-root', source, '--out', manifest)
        self.assertEqual(code, 0, err)
        digest = json.loads(out)['sha256']
        final = json.loads(manifest.read_bytes())
        ledger = checkout / 'runs/ledger.jsonl'
        self.assertIn(str(ledger), final['closure']['inputs'])
        self.assertIn(str(ledger), final['closure']['files'])
        code, out, err = self.cli('pack', '--session-root', source, '--out', transport,
                                  '--finalized-manifest', manifest)
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)['external'], [str(ledger)])
        source.rename(self.root / 'kept')
        ledger.write_bytes(b'')  # a fresh receiver with the prefix of the declared ledger
        code, _, err = self.cli('unpack', '--offload', transport, '--finalized-manifest', manifest,
                                '--finalized-sha256', digest)
        self.assertEqual(code, 0, err)
        self.assertEqual((source / 'measurement/runs/ledger.jsonl').read_bytes(), b'{"ledger":1}\n')

    def test_production_cli_must_bind_or_refuse_an_undeclared_input_below_runs(self):
        checkout = self.checkout()
        source = self.session(checkout)
        pin = checkout / 'runs/terminal-pin.json'
        original = b'{"head":"MBP"}\n'
        pin.write_bytes(original)
        # A legitimate harvest input selected through the broad measurement-directory link.
        plan_path = source / 'plan.json'
        plan = json.loads(plan_path.read_bytes())
        plan['hazard_window']['bindings']['head_pin_path'] = str(source / 'measurement/runs/terminal-pin.json')
        plan_path.write_text(json.dumps(plan))
        from joulewise.b5 import harvest
        selected = harvest.resolve_inputs(plan_path).head_pin_path
        self.assertEqual(selected.read_bytes(), original)
        manifest, transport = self.root / 'M.json', self.root / 'offload'
        code, out, err = self.cli('finalize-manifest', '--session-root', source, '--out', manifest)
        if code != 0:  # Refusing an undeclared dependency is an acceptable repair.
            self.assertIn('undeclared ignored input', err)
            return
        digest = json.loads(out)['sha256']
        code, _, err = self.cli('pack', '--session-root', source, '--out', transport,
                                '--finalized-manifest', manifest)
        if code != 0:
            self.assertRegex(err, 'ignored|input|closure')
            return
        before = runner.checkout_identity(checkout)
        source.rename(self.root / 'kept')
        pin.write_bytes(b'{"head":"Air"}\n')  # an ordinary stale mirror, with no race or forged manifest
        self.assertEqual(runner.checkout_identity(checkout), before)
        code, _, err = self.cli('unpack', '--offload', transport, '--finalized-manifest', manifest,
                                '--finalized-sha256', digest)
        if code != 0:
            self.assertFalse(source.exists())
            return
        self.assertEqual(harvest.resolve_inputs(source / 'plan.json').head_pin_path.read_bytes(), original,
                         'production restore admitted changed, undeclared ignored harvest input bytes')

    def test_production_cli_refuses_an_ignored_directory_outside_the_declaration(self):
        checkout = self.checkout()
        source = self.session(checkout)
        (checkout / 'ignored-inputs').mkdir()
        (checkout / 'ignored-inputs/input.json').write_text('{}')
        code, _, err = self.cli('finalize-manifest', '--session-root', source, '--out', self.root / 'M.json')
        self.assertEqual(code, 1)
        self.assertIn('undeclared ignored input', err)

    def test_a_direct_link_to_an_undeclared_runs_file_already_refuses(self):
        checkout = self.checkout()
        source = self.session(checkout)
        pin = checkout / 'runs/terminal-pin.json'
        pin.write_text('{}')
        (source / 'pin').symlink_to(pin)
        code, _, err = self.cli('finalize-manifest', '--session-root', source, '--out', self.root / 'M.json')
        self.assertEqual(code, 1)
        self.assertIn('undeclared ignored input', err)


class ClosureRegressionTests(Scratch):
    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_an_external_alias_back_into_the_session_must_not_be_treated_as_internal(self):
        source = self.root / 'session'
        source.mkdir()
        first, second = source / 'first.json', source / 'second.json'
        first.write_bytes(b'{"member":1}\n')
        second.write_bytes(b'{"member":2}\n')
        alias = self.root / 'current-input'
        alias.symlink_to(first)
        (source / 'selected.json').symlink_to(alias)
        original = (source / 'selected.json').read_bytes()
        try:
            final = off.finalized_manifest(source)
            off.pack(source, self.root / 'offload', finalized=final)
        except off.OffloadRefused:  # A further external link is outside the permitted mirror exception.
            return
        source.rename(self.root / 'kept')
        alias.unlink()
        alias.symlink_to(second)  # a stale/current alias; no race, manifest edit or code modification
        try:
            off.unpack(self.root / 'offload', finalized=final,
                       finalized_sha256=off.manifest_sha256(final))
        except off.OffloadRefused:
            self.assertFalse(source.exists())
            return
        self.assertEqual((source / 'selected.json').read_bytes(), original,
                         'an unbound external alias changed the input selected inside a verified session')

    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_library_byte_bound_ignored_directory_must_refuse_an_added_input(self):
        checkout = self.checkout()
        ignored = checkout / 'ignored-inputs'
        ignored.mkdir()
        old = ignored / 'old.json'
        old.write_bytes(b'{"old":1}\n')
        source = self.session(checkout, ledger=False)
        identity = runner.checkout_identity(checkout)
        self.assertTrue(runner._usable_identity(identity), identity)
        final = off.finalized_manifest(source, mirror={'root': str(checkout), 'identity': identity})
        self.assertIn(str(old), final['closure']['ignored'])
        off.pack(source, self.root / 'offload', finalized=final, mirror_identity=identity)
        source.rename(self.root / 'kept')
        (ignored / 'new.json').write_bytes(b'{"new":2}\n')
        self.assertEqual(runner.checkout_identity(checkout), identity)
        with self.assertRaisesRegex(off.OffloadRefused, 'ignored|closure'):
            off.unpack(self.root / 'offload', finalized=final,
                       finalized_sha256=off.manifest_sha256(final), mirror_identity=identity)

    def test_the_root_walker_refuses_an_unreadable_session_subdirectory(self):
        source = self.root / 'session'
        hidden = source / 'unreadable'
        hidden.mkdir(parents=True)
        original = os.scandir

        def scandir(path):
            if Path(path) == hidden:
                raise PermissionError('synthetic session subtree cannot be enumerated')
            return original(path)

        with mock.patch.object(os, 'scandir', side_effect=scandir):
            with self.assertRaises(off.OffloadRefused):
                off.finalized_manifest(source)

    def test_reserved_staging_collision_refuses_before_external_hashing(self):
        source = self.root / 'session'
        source.mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        (source / off.EXTERNAL_STAGING).symlink_to(outside, target_is_directory=True)
        ledger = self.root / 'ledger'
        ledger.write_bytes(b'ledger\n')
        with mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashing:
            with self.assertRaisesRegex(off.OffloadRefused, 'reserved name'):
                off.finalized_manifest(source, inputs=(ledger,))
        hashing.assert_not_called()
        self.assertEqual(list(outside.iterdir()), [])


class FenceAccountingTests(unittest.TestCase):
    def test_teardown_fails_for_a_recorded_violation_without_touching_a_path(self):
        # The lead's D8 ruling: parent records, teardown fails. Use a private stack/counter.
        with mock.patch.object(synthetic_custody, 'OPENED', ['open:synthetic-event-only']), \
                mock.patch.object(synthetic_custody, '_STACK', contextlib.ExitStack()), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, 'synthetic custody fence violated'):
                synthetic_custody.tearDownModule()


if __name__ == '__main__':
    unittest.main()
