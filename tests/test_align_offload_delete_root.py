"""All filesystem work is synthetic, under TemporaryDirectory; no study reads."""
import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import types
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    'offload_guard', Path(__file__).resolve().parents[1] / 'scripts/align_offload_delete_root.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class DeleteRootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.align = self.root / 'night-align'
        self.align.mkdir()
        self.src = self.root / 'archived-unused-model'
        self.src.mkdir()
        (self.src / 'bytes').write_bytes(b'opaque synthetic bytes')
        (self.src / 'empty').mkdir()
        self.op = self.root / 'journal'
        self.op.mkdir()
        self.item = self.op / 'p8'
        self.item.mkdir()
        self.remote = self.root / 'cloud'
        self.remote.mkdir()
        self.keep_root = self.root / 'KEEP-root'
        self.keep_root.mkdir()
        self.keep = self.op / 'KEEP.txt'
        self.keep.write_text(str(self.keep_root) + '\n')
        self.journal = self.op / 'deletions.tsv'
        (self.op / 'approved-models.txt').write_text(str(self.src) + '\n')
        self.archive = self.remote / 'p8.tar.zst'
        self.archive.write_bytes(b'synthetic archive')
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(g, 'MANDATORY_KEEP', (self.keep_root,)).start()
        mock.patch.object(g, 'ALIGN_ROOT', self.align).start()
        # Never list the real home; dynamic measurement-root tests use this.
        self.home = self.root / 'home'
        self.home.mkdir()
        mock.patch.object(g, 'HOME', self.home).start()
        self.acl = mock.patch.object(g, 'check_acl_flags').start()
        self.upload = mock.patch.object(g, 'check_uploaded').start()
        self.pause = mock.patch.object(g, 'check_pause_and_disk').start()
        self.second = mock.patch.object(g, 'independent_copy').start()
        self.prepare()

    def prepare(self):
        rows = g.encoded(g.tree(self.src))
        for name in ('source.json', 'source-after.json', 'cloud-local.json', 'cloud-roundtrip.json'):
            (self.item / name).write_bytes(rows)
        (self.remote / 'p8.manifest.json').write_bytes(rows)
        self.manifest_sha = g.sha_file(self.item / 'source.json')
        self.archive_sha = g.sha_file(self.archive)
        (self.item / 'independent-copy.json').write_text('{}')
        (self.item / 'cloud-proof.json').write_text(json.dumps(dict(
            schema='joulewise.offload.cloud-roundtrip.v1',
            source_manifest_sha256=self.manifest_sha, archive_sha256=self.archive_sha,
            archive=str(self.archive), manifest=str(self.remote / 'p8.manifest.json'),
            evicted_dataless=True, hydrated_not_dataless=True)))
        (self.item / 'source-path.txt').write_text(str(self.src) + '\n')
        (self.item / 'source.sha256').write_text(self.manifest_sha + '  ' + str(self.item / 'source.json') + '\n')
        (self.item / 'archive.sha256').write_text(self.archive_sha + '  ' + str(self.archive) + '\n')
        for name in ('independent-receipt.txt', 'ed-approval.txt'):
            (self.item / name).write_text('\n'.join((str(self.src), self.manifest_sha, self.archive_sha)))
        (self.item / 'retention-review.json').write_text(json.dumps(dict(
            source=str(self.src), manifest_sha256=self.manifest_sha,
            archive_sha256=self.archive_sha, no_retained_ledger_locators=True)))

    def run_delete(self):
        g.delete_root(self.item, self.keep, self.remote, self.journal)

    def refused(self, reason=None):
        with mock.patch.object(g.shutil, 'rmtree') as deletion:
            with self.assertRaises(Exception) as caught:
                self.run_delete()
            if reason:
                self.assertRegex(str(caught.exception), reason)
            deletion.assert_not_called()
        self.assertTrue(self.src.exists())
        self.assertIn('REFUSED_NO_DELETE', self.journal.read_text())
        self.assertNotIn('\tDELETED\t', self.journal.read_text())

    def test_success_publishes_json_pointer_and_both_rows(self):
        self.run_delete()
        self.assertFalse(self.src.exists())
        p = json.loads(self.src.with_name(self.src.name + '.OFFLOADED.json').read_text())
        self.assertEqual(p['manifest_sha256'], self.manifest_sha)
        self.assertEqual(p['archive_sha256'], self.archive_sha)
        self.assertIn('\tDELETE_AUTHORIZED\t', self.journal.read_text())
        self.assertIn('\tDELETED\t', self.journal.read_text())
        self.assertEqual(self.upload.call_count, 2)

    def test_raw_path_variants_refuse(self):
        for raw in (str(self.src) + '/..', str(self.src) + '/', str(self.src) + ' ',
                    str(self.src) + '/.', 'relative', str(self.src) + '\nother',
                    str(self.src.parent / 'pilot-v7-e\u0301')):
            with self.subTest(raw=raw):
                (self.item / 'source-path.txt').write_text(raw + '\n')
                self.refused()

    def test_case_variant_allowed_parent_refuses(self):
        # On case-insensitive APFS 'Night-Align' IS night-align: the inode-keyed
        # pilot check refuses. On a case-sensitive FS it is another directory,
        # outside the approved list.
        original = self.src
        alias = self.root / 'Night-Align'
        alias.mkdir(exist_ok=True)
        self.src = alias / original.name
        self.src.mkdir(exist_ok=True)
        (self.src / 'bytes').write_bytes(b'x')
        self.prepare()
        self.refused('outside allowed|pilot roots retained')

    def case_variant_pilot(self):
        """Review N3/S2: approved list + receipts bound to the NIGHT-ALIGN spelling."""
        real = self.align / 'pilot-v7-20261105T015948Z'
        real.mkdir()
        (real / 'bytes').write_bytes(b'opaque synthetic pilot bytes')
        variant = self.root / 'NIGHT-ALIGN' / real.name
        if not variant.exists():
            self.skipTest('case-sensitive filesystem: the variant is not an alias here')
        mock.patch.object(g, 'MANDATORY_KEEP', (self.keep_root, self.align)).start()
        self.keep.write_text(str(self.keep_root) + '\n' + str(self.align) + '\n')
        self.src = variant
        (self.op / 'approved-models.txt').write_text(str(variant) + '\n')
        self.prepare()
        return real

    def test_native_case_variant_pilot_refuses_by_inode(self):
        real = self.case_variant_pilot()
        self.refused('pilot roots retained')
        self.assertTrue(real.is_dir() and (real / 'bytes').is_file())
        self.assertFalse(os.path.lexists(real.with_name(real.name + '.OFFLOADED.json')))

    def test_native_case_variant_refused_by_mandatory_night_align_keep_alone(self):
        # Even if the pilot check were absent, night-align is mandatory KEEP and
        # inode overlap refuses the demonstrated bypass.
        real = self.case_variant_pilot()
        with mock.patch.object(g, 'ALIGN_ROOT', self.root / 'not-the-align-root'):
            self.refused('KEEP inode overlap')
        self.assertTrue((real / 'bytes').is_file())

    def test_unlisted_home_measurement_root_refuses_until_kept_by_inode(self):
        for name in ('night-new-lane', 'NIGHT-Other', 'jw-b5-analysis'):
            with self.subTest(name=name):
                extra = self.home / name
                extra.mkdir()
                self.refused('missing mandatory KEEP \\(inode\\): ' + name)
                self.journal.unlink()
                extra.rmdir()
        (self.home / 'night-notes.txt').write_text('not a directory')
        (self.home / 'nightly').mkdir()
        extra = self.home / 'night-new-lane'
        extra.mkdir()
        self.keep.write_text(str(self.keep_root) + '\n' + str(extra) + '\n')
        self.run_delete()
        self.assertFalse(self.src.exists())

    def test_inode_overlap_despite_different_spelling(self):
        # Identity comparison catches an alias even if the OS preserves spelling.
        original = g.identity
        alias = self.root / 'case-alias'
        alias.mkdir()
        with mock.patch.object(g, 'identity', side_effect=lambda p:
                               original(self.src) if p == alias else original(p)):
            self.assertTrue(g.overlaps(self.src, alias))

    def test_keep_equal_ancestor_and_descendant_refuse(self):
        for entry in (self.src, self.src.parent, self.src / 'bytes'):
            with self.subTest(entry=entry):
                self.keep.write_text(str(self.keep_root) + '\n' + str(entry) + '\n')
                self.refused('KEEP inode overlap')

    def test_missing_mandatory_keep_entry_refuses(self):
        self.keep.write_text(str(self.op) + '\n')
        self.refused('mandatory KEEP')

    def test_empty_duplicate_missing_unresolved_keep_refuse(self):
        for text in ('', str(self.keep_root) + '\n' + str(self.keep_root) + '\n',
                     str(self.root / 'missing') + '\n', str(self.keep_root) + '/..\n'):
            with self.subTest(text=text):
                self.keep.write_text(text)
                self.refused()

    def test_symlink_source_and_ancestor_refuse(self):
        alias = self.align / 'pilot-v6-link'
        alias.symlink_to(self.src, target_is_directory=True)
        (self.item / 'source-path.txt').write_text(str(alias) + '\n')
        self.refused('symlink')
        ancestor = self.root / 'alias'
        ancestor.symlink_to(self.align, target_is_directory=True)
        (self.item / 'source-path.txt').write_text(str(ancestor / self.src.name) + '\n')
        self.refused('symlink')

    def test_pilot9_refuses(self):
        self.src = self.align / 'pilot-v8-20261105T102850Z'
        self.src.mkdir()
        self.prepare()
        self.refused('pilot roots retained')

    def test_every_pilot_root_is_retained_until_release(self):
        for version in (0, 7, 8, 9):
            self.src = self.align / ('pilot-v' + str(version) + '-test')
            self.src.mkdir()
            self.prepare()
            self.refused('pilot roots retained')

    def test_control_overlap_refuses(self):
        with mock.patch.object(g, 'overlaps', return_value=True):
            self.refused('control/source')

    def test_pointer_exists_refuses(self):
        self.src.with_name(self.src.name + '.OFFLOADED.json').write_text('old')
        self.refused('pointer already')

    def test_receipts_bound_to_both_hashes_and_source(self):
        for name in ('independent-receipt.txt', 'ed-approval.txt'):
            for value in (str(self.src), self.manifest_sha, self.archive_sha):
                self.prepare()
                p = self.item / name
                p.write_text(p.read_text().replace(value, 'wrong'))
                self.refused('receipt not bound')

    def test_missing_receipt_and_bad_checksum_refuse(self):
        (self.item / 'source.sha256').write_text('0' * 64 + '  wrong\n')
        self.refused('checksum')
        self.prepare()
        (self.item / 'independent-receipt.txt').unlink()
        self.refused()

    def test_mutated_cloud_archive_and_manifests_refuse(self):
        for p in (self.archive, self.remote / 'p8.manifest.json',
                  self.item / 'cloud-roundtrip.json', self.item / 'source-after.json',
                  self.item / 'cloud-local.json'):
            with self.subTest(path=p):
                old = p.read_bytes()
                p.write_bytes(b'wrong')
                self.refused()
                p.write_bytes(old)

    def test_mutated_source_refuses(self):
        (self.src / 'bytes').write_bytes(b'changed')
        self.refused('predelete source mismatch')

    def test_retention_receipt_missing_false_or_other_hash_refuses(self):
        p = self.item / 'retention-review.json'
        for key, value in (('no_retained_ledger_locators', False), ('manifest_sha256', 'other')):
            self.prepare()
            data = json.loads(p.read_text())
            data[key] = value
            p.write_text(json.dumps(data))
            self.refused('retention review')
        p.unlink()
        self.refused()

    def test_capture_tree_refuses_even_with_receipt(self):
        (self.src / 'runs-parent' / 'claim' / 'instrument_validation' / 'pre').mkdir(parents=True)
        self.prepare()
        self.refused('capture retention')

    def test_acl_flags_upload_or_permissions_failure_refuses(self):
        for check in (self.acl, self.upload, self.pause, self.second):
            check.side_effect = g.Refusal('preflight refused')
            self.refused('preflight refused')
            check.side_effect = None
        with mock.patch.object(g.os, 'access', return_value=False):
            self.refused('not writable')

    def test_source_changes_during_fresh_upload_check_refuses(self):
        self.second.side_effect = lambda *a: (self.src / 'bytes').write_bytes(b'changed')
        self.refused('source changed before delete')

    def test_cloud_proof_must_bind_both_hashes_and_actual_transitions(self):
        proof = self.item / 'cloud-proof.json'
        for key, value in (('evicted_dataless', False), ('hydrated_not_dataless', False),
                           ('archive_sha256', '0' * 64), ('source_manifest_sha256', '0' * 64)):
            self.prepare()
            data = json.loads(proof.read_text())
            data[key] = value
            proof.write_text(json.dumps(data))
            self.refused('cloud roundtrip proof')

    def test_interrupt_during_rmtree_logged_as_partial(self):
        for signal_like in (KeyboardInterrupt('synthetic Ctrl-C'), SystemExit(143)):
            with self.subTest(kind=type(signal_like).__name__):
                with mock.patch.object(g.shutil, 'rmtree', side_effect=signal_like):
                    with self.assertRaises(type(signal_like)):
                        self.run_delete()
                rows = self.journal.read_text()
                self.assertIn('\tDELETE_AUTHORIZED\t', rows)
                self.assertTrue(rows.rstrip('\n').split('\n')[-1].split('\t')[2] == 'FAILED_PARTIAL')
                self.assertNotIn('\tDELETED\t', rows)
                # Pending pointer survives for recovery; a rerun refuses.
                pending = self.src.with_name(self.src.name + '.OFFLOADED.json.pending')
                self.assertTrue(pending.is_file())
                pending.unlink()
                self.journal.unlink()

    def test_sigterm_handler_raises_interrupt(self):
        with self.assertRaises(KeyboardInterrupt):
            g.interrupted(15, None)

    def test_os_failure_logged_as_partial_not_deleted(self):
        with mock.patch.object(g.shutil, 'rmtree', side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):
                self.run_delete()
        self.assertIn('FAILED_PARTIAL', self.journal.read_text())
        self.assertNotIn('\tDELETED\t', self.journal.read_text())

    def test_uchg_and_acl_precheck(self):
        with mock.patch.object(Path, 'lstat', return_value=types.SimpleNamespace(st_flags=2)):
            with self.assertRaisesRegex(ValueError, 'immutable'):
                # Exercise the actual function rather than the test's ACL stub.
                SPEC2 = importlib.util.module_from_spec(SPEC)
                SPEC.loader.exec_module(SPEC2)
                SPEC2.check_acl_flags(self.src)
        # Actual ACL parser, synthetic subprocess output.
        module = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(module)
        with mock.patch.object(module.subprocess, 'run', return_value=types.SimpleNamespace(stdout='dir\n 0: user allow delete\n')):
            with self.assertRaisesRegex(ValueError, 'ACL'):
                module.check_acl_flags(self.src)

    def test_all_protected_flags_refuse_before_acl_command(self):
        module = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(module)
        for flag in (0x2, 0x4, 0x20000, 0x40000, 0x100000, 0x80000, 0x80):
            with self.subTest(flag=hex(flag)), \
                 mock.patch.object(Path, 'lstat', return_value=types.SimpleNamespace(st_flags=flag)), \
                 mock.patch.object(module.subprocess, 'run') as command:
                with self.assertRaisesRegex(g.Refusal if module is g else module.Refusal, 'flag'):
                    module.check_acl_flags(self.src)
                command.assert_not_called()

    @unittest.skipUnless(hasattr(os, 'chflags'), 'native BSD uchg unavailable')
    def test_native_uchg_refusal_on_synthetic_file(self):
        p = self.src / 'bytes'
        os.chflags(p, 2)
        try:
            module = importlib.util.module_from_spec(SPEC)
            SPEC.loader.exec_module(module)
            self.acl.side_effect = module.check_acl_flags
            self.refused('immutable')
        finally:
            os.chflags(p, 0)

    def test_dataless_source_refuses_before_read(self):
        original = Path.lstat
        def flagged(p, *a, **kw):
            s = original(p, *a, **kw)
            if p == self.src / 'bytes':
                return types.SimpleNamespace(st_mode=s.st_mode, st_dev=s.st_dev, st_flags=g.DATALESS)
            return s
        with mock.patch.object(Path, 'lstat', flagged):
            self.refused('dataless')

    def test_receipt_symlink_refuses_without_following(self):
        receipt = self.item / 'source-path.txt'
        receipt.unlink()
        receipt.symlink_to('/must-not-follow')
        self.refused('symlink')

    def test_pending_pointer_refuses_before_delete(self):
        self.src.with_name(self.src.name + '.OFFLOADED.json.pending').write_text('old')
        self.refused()

    def test_nested_filesystem_refuses(self):
        original = Path.lstat
        def other_device(p, *a, **kw):
            st = original(p, *a, **kw)
            if p == self.src / 'bytes':
                return types.SimpleNamespace(st_mode=st.st_mode, st_dev=st.st_dev + 1)
            return st
        with mock.patch.object(Path, 'lstat', other_device):
            self.refused('nested filesystem')

    def test_missing_source_or_non_directory_refuses(self):
        for p in (self.src / 'missing', self.src / 'bytes'):
            (self.item / 'source-path.txt').write_text(str(p) + '\n')
            self.refused()

    def test_source_path_requires_exact_single_newline(self):
        (self.item / 'source-path.txt').write_text(str(self.src))
        self.refused('source-path format')

    def test_control_dataless_refuses(self):
        original = Path.stat
        def flagged(p, *a, **kw):
            st = original(p, *a, **kw)
            if p == self.item / 'retention-review.json':
                return types.SimpleNamespace(st_mode=st.st_mode, st_flags=g.DATALESS)
            return st
        with mock.patch.object(Path, 'stat', flagged):
            self.refused('control receipt')

    def test_missing_archive_or_cloud_manifest_refuses(self):
        for p in (self.archive, self.remote / 'p8.manifest.json'):
            old = p.read_bytes()
            p.unlink()
            self.refused()
            p.write_bytes(old)

    def test_source_directory_not_writable_refuses(self):
        with mock.patch.object(g.os, 'access', side_effect=[True, False]):
            self.refused('source directory not writable')

    def test_archive_dataless_refuses_before_hash(self):
        original = Path.stat
        def flagged(p, *a, **kw):
            st = original(p, *a, **kw)
            if p == self.archive:
                return types.SimpleNamespace(st_mode=st.st_mode, st_flags=g.DATALESS)
            return st
        with mock.patch.object(Path, 'stat', flagged):
            self.refused('dataless')

    def test_invalid_approved_model_entry_refuses(self):
        (self.op / 'approved-models.txt').write_text(str(self.keep_root) + '/..\n')
        self.refused('non-canonical')

    def test_exact_approved_model_path_still_obeys_keep(self):
        (self.op / 'approved-models.txt').write_text(str(self.src) + '\n')
        self.keep.write_text(str(self.keep_root) + '\n' + str(self.src) + '\n')
        self.refused('KEEP inode overlap')

    def test_audit_write_failure_never_starts_deletion(self):
        self.journal.mkdir()
        self.refused_audit_failure()

    def test_journal_symlink_and_hardlink_never_append_to_keep(self):
        target = self.keep_root / 'precious'
        target.write_bytes(b'KEEP exact bytes\n')
        for link in ('symlink', 'hardlink'):
            with self.subTest(link=link):
                if link == 'symlink':
                    self.journal.symlink_to(target)
                else:
                    os.link(target, self.journal)
                # Force an early refusal, the formerly vulnerable path.
                with mock.patch.object(g.shutil, 'rmtree') as deletion:
                    with self.assertRaisesRegex(g.Refusal, 'journal'):
                        g.delete_root(self.item / 'missing', self.keep, self.remote, self.journal)
                    deletion.assert_not_called()
                self.assertEqual(target.read_bytes(), b'KEEP exact bytes\n')
                self.journal.unlink()

    def test_journal_wrong_parent_or_name_is_not_created(self):
        for path in (self.item / 'deletions.tsv', self.op / 'other.tsv'):
            with self.subTest(path=path), self.assertRaisesRegex(g.Refusal, 'journal'):
                g.delete_root(self.item, self.keep, self.remote, path)
            self.assertFalse(path.exists())

    def test_journal_link_swap_during_open_never_writes(self):
        target = self.keep_root / 'precious'
        target.write_bytes(b'KEEP')
        real_open = os.open
        def swapped(path, flags, mode):
            os.link(target, path)
            return real_open(path, flags, mode)
        with mock.patch.object(g.os, 'open', side_effect=swapped), \
             self.assertRaisesRegex(g.Refusal, 'journal'):
            self.run_delete()
        self.assertEqual(target.read_bytes(), b'KEEP')

    def refused_audit_failure(self):
        with mock.patch.object(g.shutil, 'rmtree') as deletion:
            with self.assertRaises((OSError, g.Refusal)):
                self.run_delete()
            deletion.assert_not_called()
        self.assertTrue(self.src.exists())

    def test_tree_root_dataless_and_file_changes_during_hash_refuse(self):
        original = Path.stat
        def root_flag(p, *a, **kw):
            st = original(p, *a, **kw)
            if p == self.src:
                return types.SimpleNamespace(st_mode=st.st_mode, st_dev=st.st_dev, st_flags=g.DATALESS)
            return st
        with mock.patch.object(Path, 'stat', root_flag):
            with self.assertRaisesRegex(g.Refusal, 'dataless root'):
                g.tree(self.src)
        original_digest = g.digest
        def mutate(stream):
            result = original_digest(stream)
            (self.src / 'bytes').write_bytes(b'changed during inventory')
            return result
        with mock.patch.object(g, 'digest', side_effect=mutate):
            with self.assertRaisesRegex(g.Refusal, 'source changed'):
                g.tree(self.src)

    def test_hardlink_and_special_file_refuse(self):
        os.link(self.src / 'bytes', self.src / 'hardlink')
        self.refused('hardlink')
        (self.src / 'hardlink').unlink()
        os.mkfifo(self.src / 'pipe')
        self.refused('special file')


def wait_visible(test, pid, timeout=10.0):
    import time
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        out = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'pid='], capture_output=True, text=True).stdout
        if out.strip():
            time.sleep(0.2)  # let exec complete so comm/args show the new image
            return
        time.sleep(0.05)
    test.fail('spawned process never appeared in ps')


@unittest.skipUnless(sys.platform == 'darwin', 'native macOS ps behavior')
class NativeProcessCensusTests(unittest.TestCase):
    """Spawn REAL long-path processes and prove the production census sees them.

    Only synthetic sleepers under a TemporaryDirectory; nothing is read or written
    outside it. Every child is killed in cleanup.
    """
    @classmethod
    def setUpClass(cls):
        # A copied /bin/sleep (arm64e platform binary) is SIGKILLed outside the
        # system volume, so compile a real ad-hoc-signed sleeper instead.
        cls.build = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.build.cleanup)
        cls.sleeper = Path(cls.build.name).resolve() / 'sleeper'
        source = cls.sleeper.with_suffix('.c')
        source.write_text('#include <unistd.h>\nint main(void){sleep(600);return 0;}\n')
        if shutil.which('cc') is None or subprocess.run(
                ['cc', '-o', str(cls.sleeper), str(source)], capture_output=True).returncode:
            raise unittest.SkipTest('no C compiler for a native long-path executable')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        deep = Path(self.temp.name).resolve()
        for i in range(10):
            deep = deep / ('long-path-component-%02d' % i)
        deep.mkdir(parents=True)
        self.deep = deep
        self.assertGreater(len(str(deep)), 200)

    def spawn(self, argv, **kw):
        child = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, **kw)
        def stop():
            child.kill()
            child.wait()
            child.stdin.close()
        self.addCleanup(stop)
        wait_visible(self, child.pid)
        return child

    def binary(self, *parts):
        target = self.deep.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.sleeper, target)
        target.chmod(0o755)
        return target

    def assertBusy(self, child):
        self.assertIn(str(child.pid), g.process_census())

    def test_symlinked_claude_native_layout_binary(self):
        real = self.binary('.local', 'share', 'claude', 'versions', '2.1.99')
        link = self.deep / '.local' / 'bin' / 'claude'
        link.parent.mkdir(parents=True)
        link.symlink_to(real)
        self.assertBusy(self.spawn([str(link), '600']))
        # The watchdog's PATH launch: argv[0] is the bare name `claude`.
        self.assertBusy(self.spawn(['claude', '--resume'], executable=str(link)))

    def test_disguised_argv0_still_busy_by_kernel_executable_path(self):
        real = self.binary('.local', 'share', 'claude', 'versions', '2.1.99')
        child = self.spawn(['innocuous-name', '600'], executable=str(real))
        comm = subprocess.run(['/bin/ps', '-p', str(child.pid), '-o', 'comm='],
                              capture_output=True, text=True).stdout
        self.assertNotIn('claude', comm)  # only proc_pidpath can see it
        self.assertIn('/claude/versions/', g.executable_paths([str(child.pid)])[str(child.pid)])
        self.assertBusy(child)

    def test_symlinked_claude_named_script(self):
        script = self.deep / 'npm' / 'lib' / 'node_modules' / 'pkg' / 'cli.sh'
        script.parent.mkdir(parents=True)
        script.write_text('#!/bin/sh\n/bin/sleep 600\n:\n')
        script.chmod(0o755)
        link = self.deep / 'npm' / 'bin' / 'claude'
        link.parent.mkdir(parents=True)
        link.symlink_to(script)
        self.assertBusy(self.spawn([str(link)]))

    def test_long_path_codex_binary(self):
        codex = self.binary('node_modules', '@openai', 'codex', 'vendor', 'aarch64-apple-darwin', 'codex', 'codex')
        self.assertGreater(len(str(codex)), 250)
        self.assertBusy(self.spawn([str(codex), 'exec']))

    def test_long_path_python_scripts_and_modules(self):
        watchdog = self.deep / 'scripts' / 'magistrate_watchdog.py'
        watchdog.parent.mkdir(parents=True)
        watchdog.write_text('import time\ntime.sleep(600)\n')
        self.assertBusy(self.spawn([sys.executable, '-I', '-B', str(watchdog), '--tick']))
        package = self.deep / 'fakepkg'
        package.mkdir()
        (package / '__init__.py').write_text('')
        (package / 'harvest_b5.py').write_text('import time\ntime.sleep(600)\n')
        env = dict(os.environ, PYTHONPATH=str(self.deep))
        self.assertBusy(self.spawn([sys.executable, '-B', '-m', 'fakepkg.harvest_b5'], env=env))

    def test_real_zstd_in_tar_pipeline(self):
        zstd = shutil.which('zstd')
        if zstd is None:
            self.skipTest('zstd not installed')
        # zstd blocks reading its stdin pipe; it is a writer until it exits.
        self.assertBusy(self.spawn([zstd, '-T1', '-3', '-q', '-c']))
        self.assertBusy(self.spawn(['/usr/bin/tar', '-cf', '-', '-T', '-']))

    def test_benign_long_path_sleeper_is_not_busy(self):
        child = self.spawn([str(self.binary('tools', 'benign-sleeper')), '600'])
        self.assertNotIn(str(child.pid), g.process_census())


class HelperTests(unittest.TestCase):
    def test_upload_parser_is_closed_until_real_sample_recorded(self):
        for text in ('isUploaded=1', 'isUploaded=1\nisUploading=0\nhasUnresolvedConflicts=0\n'):
            with self.subTest(text=text), self.assertRaisesRegex(g.Refusal, 'unpinned'):
                g.parse_uploaded(text)

    def test_upload_parser_rejects_pending_errors_conflicts_and_unknowns(self):
        sample = 'isUploaded=1\nisUploading=0\nhasUnresolvedConflicts=0\n'
        # Synthetic grammar exercise ONLY; this pin is never shipped as real.
        with mock.patch.object(g, 'UPLOAD_SUCCESS_SAMPLE', sample), \
             mock.patch.object(g, 'UPLOAD_SAMPLE_SHA256', hashlib.sha256(sample.encode()).hexdigest()):
            g.parse_uploaded(sample)
            for text in (sample.replace('isUploading=0', 'isUploading=1'),
                         sample + 'uploadingError=\n', sample + 'uploadingError=failed\n',
                         sample.replace('hasUnresolvedConflicts=0', 'hasUnresolvedConflicts=1'),
                         sample + 'unknown=0\n', sample + 'isUploaded=1\n',
                         sample.replace('isUploaded=1', 'isUploaded=10'),
                         sample.replace('isUploaded=1', 'isUploaded=0'),
                         'isUploaded=1', sample.replace('\n', ' ')):
                with self.subTest(text=text), self.assertRaises(g.Refusal):
                    g.parse_uploaded(text)

    def test_tree_archive_roundtrip_preserves_modes_links_and_empty_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'empty').mkdir(mode=0o750)
            (root / 'bytes').write_bytes(b'opaque synthetic bytes')
            (root / 'bytes').chmod(0o640)
            (root / 'link').symlink_to('/synthetic-target-never-read')
            expected = g.tree(root)
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode='w') as tf:
                tf.add(root, arcname='.')
            stream.seek(0)
            self.assertEqual(g.archive(stream), expected)

    def test_manifest_budget_covers_uncompressed_tar_with_long_names(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            source = root / 'source'
            source.mkdir()
            (source / ('x' * 200)).write_bytes(os.urandom(4097))
            (source / 'empty').mkdir()
            (source / 'link').symlink_to('x' * 200)
            manifest = root / 'source.json'
            manifest.write_bytes(g.encoded(g.tree(source)))
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode='w') as tf:
                tf.add(source, arcname='.')
            result = subprocess.run([sys.executable, '-I', '-B', str(Path(g.__file__)),
                                     'budget', str(manifest)], text=True, capture_output=True, check=True)
            self.assertGreater(int(result.stdout), len(stream.getvalue()) + 4 * manifest.stat().st_size)

    def test_pause_disk_and_writer_census_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            op = Path(d).resolve()
            stop = op / 'STOP'
            ours = op / 'our-STOP.txt'
            expected = 'ALIGN paused for MBP offload and gold validation; ' + str(op) + '\n'
            stop.write_text(expected)
            ours.write_text(expected)
            space = types.SimpleNamespace(f_bavail=40_000_000_000, f_frsize=1)
            with mock.patch.object(g, 'STOP_PATH', stop), mock.patch.object(g.os, 'statvfs', return_value=space), mock.patch.object(g.subprocess, 'run', return_value=types.SimpleNamespace(stdout='1 /sbin/launchd')) as ps:
                g.check_pause_and_disk(op)
                calls = [c.args[0] for c in ps.call_args_list if c.args[0][0] == '/bin/ps']
                # comm and args are each the LAST column, in separate calls, so
                # macOS never truncates the executable path to 16 characters.
                self.assertEqual(calls, [['/bin/ps', '-axww', '-o', 'pid=,comm='],
                                         ['/bin/ps', '-axww', '-o', 'pid=,args=']])
                for command in ('claude', 'codex', 'offload.py', 'align_pilot_session.py',
                                'harvest.py', 'zstd', '/usr/bin/tar', '/app/claude/versions/2.1.3'):
                    ps.return_value.stdout = '123 ' + command
                    with self.assertRaisesRegex(g.Refusal, 'census busy'):
                        g.check_pause_and_disk(op)
                # The kernel's executable field has no --item or script argv.
                # A path argument named harvest is never requested from ps.
                ps.return_value.stdout = '123 /usr/bin/python3.13\n124 /bin/zsh\n'
                g.check_pause_and_disk(op)
                ps.return_value.stdout = ''
                space.f_bavail = 29_999_999_999
                with self.assertRaisesRegex(g.Refusal, 'disk floor'):
                    g.check_pause_and_disk(op)
                space.f_bavail = 40_000_000_000
                stop.write_text('someone else')
                with self.assertRaisesRegex(g.Refusal, 'STOP mismatch'):
                    g.check_pause_and_disk(op)

    def test_night_align_is_production_mandatory_keep(self):
        self.assertIn(Path('/Users/edr/night-align'), g.MANDATORY_KEEP)
        self.assertEqual(g.ALIGN_ROOT, Path('/Users/edr/night-align'))
        self.assertEqual(g.HOME, Path('/Users/edr'))
        for name in ('night-align', 'night-custody', 'night-b5', 'night-bytes', 'night-g2a',
                     'night-b6', 'night-archive', 'night-plan-staging', 'jw_models'):
            self.assertIn(Path('/Users/edr') / name, g.MANDATORY_KEEP)
        for name in ('night-align', 'Night-Align', 'jw-b5-analysis', 'jw_models', 'night-x'):
            self.assertTrue(g.MEASUREMENT_ROOT.fullmatch(name), name)
        for name in ('nightly', 'night-', 'jw-b5', 'code'):
            self.assertFalse(g.MEASUREMENT_ROOT.fullmatch(name), name)

    def census(self, comm, args=''):
        # Synthetic `ps -axww -o pid=,comm=` and `pid=,args=` tables.
        return g.busy_processes(comm, args or comm)

    def test_census_matches_executable_basename_only(self):
        self.assertEqual(self.census('123 /bin/python3.13\n'), [])
        self.assertEqual(self.census('123 /tmp/harvest-project/python3.13\n'), [])
        self.assertEqual(self.census('123 /tmp/tar-project/other\n'), [])
        self.assertEqual(self.census('123 /bin/harvest.py\n'), ['123'])
        for script in ('offload.py', 'align_pilot_session.py', 'harvest.py'):
            self.assertEqual(self.census('123 /bin/python3.13\n', '123 python3.13 /tmp/' +
                                         script + ' --secret credential\n'), ['123'])

    def test_census_review_n1_missed_rows_now_busy(self):
        # Every row the review showed the old 16-character `comm,args` parse missed.
        py = '/opt/homebrew/Cellar/python@3.13/3.13.9/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/MacOS/Python'
        long_root = '/Users/edr/' + '/'.join('deep%02d' % i for i in range(12))
        cases = {
            'native claude': (long_root + '/.local/share/claude/versions/2.1.99', 'claude --resume'),
            'claude via symlink': (long_root + '/.local/share/claude/versions/2.1.99',
                                   '/Users/edr/.local/bin/claude -p'),
            'long-path codex': (long_root + '/node_modules/@openai/codex/bin/codex', 'codex exec'),
            'homebrew zstd': ('/opt/homebrew/Cellar/zstd/1.5.7/bin/zstd', 'zstd -T1 -3 -o x.partial'),
            'npm claude': ('/opt/homebrew/Cellar/node/24.1.0/bin/node',
                           'node /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/cli.js'),
            'npm claude bin': ('/opt/homebrew/Cellar/node/24.1.0/bin/node', 'node /opt/homebrew/bin/claude'),
            'watchdog': (py, py + ' -I -B /Users/edr/night-custody/x/scripts/magistrate_watchdog.py --tick'),
            'ledger pin': (py, 'python3.13 -B scripts/advance_b5_ledger_pin.py --pin 640'),
            'r0 checks': (py, '.venv/bin/python -B scripts/align_r0_checks.py --config c.json'),
            'harvest module': (py, 'python3.13 -m joulewise.align.harvest_b5 --root r'),
            'mlx module': (py, 'python -m mlx_lm.generate --model m'),
            'run_night': (py, 'python3.13 scripts/run_night.py --plan p'),
            'pinned guard': (py, 'python3.13 -I -B /Users/edr/night-archive/op/disk_guard.py '
                             '--path /System/Volumes/Data -- /bin/zsh -f step6-ssd.zsh'),
            'pinned guard wrapper': (py, py + ' -I -B /Users/edr/night-archive/op/disk_guard.py '
                                     '--writer-wrapper 3 -- /bin/zsh -f step6-ssd.zsh'),
            'rsync': ('/usr/bin/rsync', 'rsync -a a b'),
            'cp': ('/bin/cp', 'cp -p a b'),
            'ditto': ('/usr/bin/ditto', 'ditto a b'),
            'pzstd': ('/opt/homebrew/bin/pzstd', 'pzstd -d x'),
            'gtar': ('/opt/homebrew/Cellar/gnu-tar/1.35/libexec/gnubin/gtar', 'gtar -cf - .'),
        }
        for label, (exe, argv) in cases.items():
            with self.subTest(label=label):
                self.assertEqual(g.busy_processes('4242 ' + exe + '\n1 /sbin/launchd\n',
                                                  '4242 ' + argv + '\n1 /sbin/launchd\n'), ['4242'])

    def test_census_benign_rows_and_formats(self):
        benign = ('1 /sbin/launchd\n'
                  '2 /Users/edr/.claude/projects/notes/python3.13\n'  # hidden config dir, not agent
                  '3 /Applications/Utilities/Terminal.app/Contents/MacOS/Terminal\n'
                  '4 /bin/zsh\n')
        args = ('1 /sbin/launchd\n2 python3.13 -c pass\n3 Terminal\n'
                '4 -zsh\n5 shasum -a 256 /Users/edr/x.tar.zst\n')
        self.assertEqual(g.busy_processes(benign, args), [])
        # PID churn between the two ps calls: union of both tables is inspected.
        self.assertEqual(g.busy_processes('1 /sbin/launchd\n', '1 launchd\n9 tar -xf a\n'), ['9'])
        self.assertEqual(g.busy_processes(b'7 /bin/cp\n', b'7 cp \xff\n'), ['7'])
        for comm, args in (('', '1 a'), ('1 a', ''), ('abc def', '1 a')):
            with self.assertRaises(g.Refusal):
                g.busy_processes(comm, args)

    def test_final_pause_rechecks_lock_and_loaded_launchers(self):
        with tempfile.TemporaryDirectory() as d:
            op = Path(d).resolve()
            stop = op / 'STOP'
            text = 'ALIGN paused for MBP offload and gold validation; ' + str(op) + '\n'
            stop.write_text(text)
            (op / 'our-STOP.txt').write_text(text)
            lock = op / 'magistrate.lock'
            lock.write_text(json.dumps(dict(schema='joulewise.magistrate_lock.v1', pid=1234)))
            with mock.patch.object(g, 'STOP_PATH', stop), \
                 mock.patch.object(g.os, 'kill') as kill, \
                 mock.patch.object(g.subprocess, 'run', return_value=types.SimpleNamespace(stdout='1 launchd')) as command, \
                 mock.patch.object(g.os, 'statvfs', return_value=types.SimpleNamespace(f_bavail=40_000_000_000, f_frsize=1)):
                with self.assertRaisesRegex(g.Refusal, 'lock owner alive'):
                    g.check_pause_and_disk(op)
                command.assert_not_called()
                kill.side_effect = ProcessLookupError
                command.return_value.stdout = '123 0 com.joulewise.quiet-kit'
                with self.assertRaisesRegex(g.Refusal, 'launcher loaded'):
                    g.check_pause_and_disk(op)
                command.return_value.stdout = '1 /sbin/launchd'
                g.check_pause_and_disk(op)

    def test_archive_unsafe_duplicate_and_hardlink(self):
        for name, kind, repeat in (('../bad', tarfile.REGTYPE, False),
                                   ('restricted/data', tarfile.REGTYPE, False),
                                   ('link', tarfile.LNKTYPE, False),
                                   ('same', tarfile.REGTYPE, True)):
            b = io.BytesIO()
            with tarfile.open(fileobj=b, mode='w') as tf:
                m = tarfile.TarInfo(name)
                m.type = kind
                m.linkname = 'target'
                tf.addfile(m)
                if repeat:
                    tf.addfile(m)
            b.seek(0)
            with self.assertRaises(g.Refusal):
                g.archive(b)


if __name__ == '__main__':
    unittest.main()
