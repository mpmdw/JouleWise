"""Final R17 delta review, seat 2: synthetic CLI and closure witnesses.

Required-property assertions stay red for unresolved findings. Git probes use
temporary repositories; interpreter identity is an explicit synthetic seam.
No measurement fixture, model, home custody or network is used.
"""
from contextlib import redirect_stderr, redirect_stdout
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

setUpModule, tearDownModule = synthetic_custody.setUpModule, synthetic_custody.tearDownModule
REAL_TMP = os.path.realpath(tempfile.gettempdir())


class Scratch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hoff-delta2-sol2-', dir=REAL_TMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def checkout(self):
        checkout = self.root / 'checkout'
        checkout.mkdir()
        (checkout / '.gitignore').write_text('.venv/\nruns/\nother-ignored/\n')
        (checkout / 'tracked.json').write_text('{"synthetic":true}')
        (checkout / '.venv/bin').mkdir(parents=True)
        (checkout / '.venv/bin/python').write_text('never executed: identity seam')
        (checkout / 'runs').mkdir()
        (checkout / 'runs/ledger.jsonl').write_bytes(b'{"synthetic_ledger":1}\n')
        for args in (('init', '-q'), ('add', '.'), ('commit', '-qm', 'synthetic checkout')):
            subprocess.run(['git', '-c', 'user.name=Synthetic', '-c',
                            'user.email=synthetic@example.invalid', '-C', str(checkout), *args],
                           check=True, capture_output=True)
        return checkout

    @staticmethod
    def run_identity(argv, **kwargs):
        if argv[0] == 'git':
            return subprocess.run(argv, **kwargs)
        return subprocess.CompletedProcess(argv, 0, stdout='synthetic-python\nsynthetic-packages\n')

    def session(self, checkout):
        session = self.root / 'session'
        (session / 'custody/night').mkdir(parents=True)
        (session / 'custody/night/result.json').write_text('{}')
        (session / 'measurement').mkdir()
        # The production measurement_view links runs/ as a whole directory.
        (session / 'measurement/runs').symlink_to(checkout / 'runs', target_is_directory=True)
        (session / 'plan.json').write_text(json.dumps({
            'custody_root': str(session / 'custody'),
            'hazard_window': {'bindings': {'ledger_path': str(session / 'measurement/runs/ledger.jsonl')}}}))
        (session / 'session.json').write_text(json.dumps({
            'session_id': 'synthetic', 'plan_path': str(session / 'plan.json'),
            'measurement_root': str(session / 'measurement'), 'source_measurement_root': str(checkout)}))
        return session

    def cli(self, *argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = runner.main(list(map(str, argv)), run=self.run_identity)
        return code, stdout.getvalue(), stderr.getvalue()


@unittest.skipUnless(shutil.which('zstd'), 'zstd required')
class ProductionPolicyTests(Scratch):
    def round_trip(self, mutate=None, *, extra_input=True):
        checkout = self.checkout()
        session = self.session(checkout)
        extra = checkout / 'runs/undeclared-input.json'
        original = b'{"synthetic_input":"MBP"}\n'
        if extra_input:
            extra.write_bytes(original)
        identity = runner.checkout_identity(checkout, run=self.run_identity)
        self.assertTrue(runner._usable_identity(identity))
        finalized_path, transport = self.root / 'finalized.json', self.root / 'offload'
        code, _, error = self.cli('finalize-manifest', '--session-root', session, '--out', finalized_path)
        if code:
            return 'finalize refused', error
        final = json.loads(finalized_path.read_bytes())
        self.assertIn(str(checkout / 'runs/ledger.jsonl'), final['closure']['inputs'])
        code, _, error = self.cli('pack', '--session-root', session, '--out', transport,
                                  '--finalized-manifest', finalized_path, '--threads', 1)
        if code:
            return 'pack refused', error
        session.rename(self.root / 'kept')
        if mutate is not None:
            mutate(extra)
        self.assertEqual(runner.checkout_identity(checkout, run=self.run_identity), identity)
        code, _, error = self.cli('unpack', '--offload', transport, '--finalized-manifest', finalized_path,
                                  '--finalized-sha256', off.manifest_sha256(final))
        if code:
            self.assertFalse(session.exists(), 'a refused restore must not publish the session')
            return 'unpack refused', error
        self.assertEqual(off.verify_tree(session, json.loads((transport / off.MANIFEST).read_bytes())), [])
        self.assertEqual((session / 'measurement/runs/ledger.jsonl').read_bytes(),
                         b'{"synthetic_ledger":1}\n')
        return 'restored', ((session / 'measurement/runs/undeclared-input.json').read_bytes() if extra_input
                            else (session / 'measurement/runs/ledger.jsonl').read_bytes())

    def test_honest_cli_restore_preserves_declared_ledger_and_inputs(self):
        stage, value = self.round_trip(extra_input=False)
        self.assertEqual(stage, 'restored', value)
        self.assertEqual(value, b'{"synthetic_ledger":1}\n')

    def test_cli_must_refuse_or_bind_undeclared_bytes_below_declared_runs_directory(self):
        stage, value = self.round_trip(lambda path: path.write_bytes(b'{"synthetic_input":"Air"}\n'))
        if stage != 'restored':
            return  # Fail-closed finalize, pack or restore is an acceptable fix.
        self.assertEqual(value, b'{"synthetic_input":"MBP"}\n',
                         'production CLI silently admitted changed, undeclared runs/ bytes')

    def test_cli_must_notice_new_undeclared_files_below_declared_runs_directory(self):
        stage, value = self.round_trip(lambda path: (path.parent / 'new-input.json').write_text('{}'),
                                       extra_input=False)
        if stage != 'restored':
            return
        self.assertFalse((self.root / 'session/measurement/runs/new-input.json').exists(),
                         'a new ignored input is reachable through the verified restored view')

    def test_direct_undeclared_ignored_file_link_is_refused(self):
        checkout = self.checkout()
        session = self.session(checkout)
        extra = checkout / 'runs/undeclared.json'
        extra.write_text('{}')
        (session / 'direct-input').symlink_to(extra)
        code, _, error = self.cli('finalize-manifest', '--session-root', session,
                                  '--out', self.root / 'finalized.json')
        self.assertEqual(code, 1)
        self.assertIn('undeclared ignored input', error)

    def test_ignored_directory_outside_the_declaration_is_refused(self):
        checkout = self.checkout()
        session = self.session(checkout)
        ignored = checkout / 'other-ignored'
        ignored.mkdir()
        (ignored / 'input').write_bytes(b'synthetic')
        (session / 'other-input').symlink_to(ignored, target_is_directory=True)
        code, _, error = self.cli('finalize-manifest', '--session-root', session,
                                  '--out', self.root / 'finalized.json')
        self.assertEqual(code, 1)
        self.assertIn('undeclared ignored input', error)


class LinkAndWalkTests(Scratch):
    @unittest.skipUnless(shutil.which('zstd'), 'zstd required')
    def test_symlink_parent_dotdot_must_bind_the_file_the_os_actually_opens(self):
        source, outer, actual = self.root / 'session', self.root / 'outer', self.root / 'actual'
        source.mkdir()
        outer.mkdir()
        (actual / 'deep').mkdir(parents=True)
        (outer / 'input.json').write_bytes(b'{"decoy":true}')
        (actual / 'input.json').write_bytes(b'{"actual":"MBP"}')
        (outer / 'alias').symlink_to(actual / 'deep', target_is_directory=True)
        # POSIX resolves alias before ..; normpath first selects a different file.
        (source / 'input').symlink_to(str(outer / 'alias/../input.json'))
        self.assertEqual((source / 'input').read_bytes(), b'{"actual":"MBP"}')
        try:
            final = off.finalized_manifest(source)
            off.pack(source, self.root / 'offload', finalized=final, threads=1)
        except off.OffloadRefused:
            return
        source.rename(self.root / 'kept')
        (actual / 'input.json').write_bytes(b'{"actual":"Air"}')
        try:
            off.unpack(self.root / 'offload', finalized=final, finalized_sha256=off.manifest_sha256(final))
        except off.OffloadRefused:
            return
        self.assertEqual((source / 'input').read_bytes(), b'{"actual":"MBP"}',
                         'lexical dotdot normalization bound a decoy rather than the consumed file')

    @unittest.skipUnless(shutil.which('zstd'), 'zstd required')
    def test_external_alias_returning_into_session_cannot_change_selected_input(self):
        source = self.root / 'session'
        source.mkdir()
        (source / 'a.json').write_bytes(b'{"selected":"A"}')
        (source / 'b.json').write_bytes(b'{"selected":"B"}')
        alias = self.root / 'operator-selected-input'
        alias.symlink_to(source / 'a.json')
        (source / 'selected-input').symlink_to(alias)
        try:
            final = off.finalized_manifest(source)
            off.pack(source, self.root / 'offload', finalized=final, threads=1)
        except off.OffloadRefused:
            return
        source.rename(self.root / 'kept')
        # A stable alias copied with the wrong target on the receiver; no race.
        alias.unlink()
        alias.symlink_to(source / 'b.json')
        try:
            off.unpack(self.root / 'offload', finalized=final, finalized_sha256=off.manifest_sha256(final))
        except off.OffloadRefused:
            return
        self.assertEqual((source / 'selected-input').read_bytes(), b'{"selected":"A"}',
                         'an external hop disappeared from the closure because it ended inside the session')

    def test_finalize_walks_a_shared_external_directory_once(self):
        source, external = self.root / 'session', self.root / 'external'
        source.mkdir()
        external.mkdir()
        target = external / 'input'
        target.write_bytes(b'synthetic')
        for index in range(22):
            (source / f'member-{index:02d}').symlink_to(external, target_is_directory=True)
        with mock.patch.object(off.os, 'walk', wraps=os.walk) as walk, \
                mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashing:
            final = off.finalized_manifest(source)
        self.assertEqual(sum(Path(call.args[0]) == external for call in walk.call_args_list), 1)
        self.assertEqual(sum(call.args[0] == target for call in hashing.call_args_list), 1)
        self.assertEqual(len(final['closure']['files']), 1)

    def test_unreadable_session_directory_refuses(self):
        source = self.root / 'session'
        (source / 'unreadable').mkdir(parents=True)
        original = os.scandir

        def scandir(path):
            if Path(path) == source / 'unreadable':
                raise PermissionError('synthetic session directory error')
            return original(path)

        with mock.patch.object(os, 'scandir', side_effect=scandir):
            with self.assertRaises(off.OffloadRefused):
                off.finalized_manifest(source)

    def test_directory_limit_refuses_during_enumeration(self):
        source, external = self.root / 'session', self.root / 'external'
        source.mkdir()
        (external / 'a/b').mkdir(parents=True)
        (source / 'input').symlink_to(external, target_is_directory=True)
        with mock.patch.object(off, 'CLOSURE_MAX_DIRECTORIES', 1):
            with self.assertRaisesRegex(off.OffloadRefused, 'directories'):
                off.finalized_manifest(source)


class FenceTests(unittest.TestCase):
    def test_recorded_synthetic_audit_event_fails_child_module_teardown(self):
        # Fabricated event only: neither parent nor child probes this locator.
        locator = str(synthetic_custody.HOME / 'night-custody/synthetic-never-opened')
        code = ('import os, sys; from tests.align import synthetic_custody as c; '
                'c.setUpModule(); c._audit("open", (os.fsencode(sys.argv[1]), "r", 0)); '
                'assert len(c.OPENED) == 1; c.tearDownModule()')
        child = subprocess.run([sys.executable, '-B', '-c', code, locator], capture_output=True, text=True)
        self.assertNotEqual(child.returncode, 0)
        self.assertIn('AssertionError: synthetic custody fence violated', child.stderr)


if __name__ == '__main__':
    unittest.main()
