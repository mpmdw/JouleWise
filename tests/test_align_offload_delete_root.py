"""All filesystem work is synthetic, under TemporaryDirectory; no study reads."""
import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
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
                self.assertIn(reason, str(caught.exception))
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
        # Real case-insensitive volumes alias this; emulate on case-sensitive CI.
        original = self.src
        alias = self.root / 'Night-Align'
        alias.mkdir(exist_ok=True)
        self.src = alias / original.name
        self.src.mkdir(exist_ok=True)
        (self.src / 'bytes').write_bytes(b'x')
        self.prepare()
        self.refused('outside allowed')

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
                self.assertEqual(ps.call_args.args[0], ['/bin/ps', '-axo', 'pid=,comm=,args='])
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

    def test_census_matches_executable_basename_only(self):
        self.assertEqual(g.busy_processes('123 /bin/python3.13\n'), [])
        self.assertEqual(g.busy_processes('123 /tmp/harvest-project/python3.13\n'), [])
        self.assertEqual(g.busy_processes('123 /tmp/tar-project/other\n'), [])
        self.assertEqual(g.busy_processes('123 /bin/harvest.py\n'), ['123'])
        for script in ('offload.py', 'align_pilot_session.py', 'harvest.py'):
            self.assertEqual(g.busy_processes('123 /bin/python3.13 python3.13 /tmp/' +
                                             script + ' --secret credential\n'), ['123'])

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
