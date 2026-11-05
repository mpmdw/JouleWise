"""All filesystem work is synthetic, under TemporaryDirectory; no study reads."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
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
        self.src = self.align / 'pilot-v7-test'
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
        self.archive = self.remote / 'p8.tar.zst'
        self.archive.write_bytes(b'synthetic archive')
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(g, 'MANDATORY_KEEP', (self.keep_root,)).start()
        mock.patch.object(g, 'ALIGN_ROOT', self.align).start()
        self.acl = mock.patch.object(g, 'check_acl_flags').start()
        self.upload = mock.patch.object(g, 'check_uploaded').start()
        self.prepare()

    def prepare(self):
        rows = g.encoded(g.tree(self.src))
        for name in ('source.json', 'source-after.json', 'cloud-local.json', 'cloud-roundtrip.json'):
            (self.item / name).write_bytes(rows)
        (self.remote / 'p8.manifest.json').write_bytes(rows)
        self.manifest_sha = g.sha_file(self.item / 'source.json')
        self.archive_sha = g.sha_file(self.archive)
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
                    str(self.src) + '/.', 'relative', str(self.src) + '\nother'):
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
        for entry in (self.src, self.align, self.src / 'bytes'):
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
        self.refused('pilot 9 retained')

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
        for check in (self.acl, self.upload):
            check.side_effect = g.Refusal('preflight refused')
            self.refused('preflight refused')
            check.side_effect = None
        with mock.patch.object(g.os, 'access', return_value=False):
            self.refused('not writable')

    def test_source_changes_during_fresh_upload_check_refuses(self):
        self.upload.side_effect = lambda p: (self.src / 'bytes').write_bytes(b'changed')
        self.refused('source changed before delete')

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

    @unittest.skipUnless(hasattr(os, 'chflags'), 'native BSD uchg unavailable')
    def test_native_uchg_refusal_on_synthetic_file(self):
        p = self.src / 'bytes'
        os.chflags(p, 2)
        try:
            module = importlib.util.module_from_spec(SPEC)
            SPEC.loader.exec_module(module)
            with self.assertRaisesRegex(ValueError, 'immutable'):
                module.check_acl_flags(p)
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

    def test_hardlink_and_special_file_refuse(self):
        os.link(self.src / 'bytes', self.src / 'hardlink')
        self.refused('hardlink')
        (self.src / 'hardlink').unlink()
        os.mkfifo(self.src / 'pipe')
        self.refused('special file')


class HelperTests(unittest.TestCase):
    def test_upload_parser_requires_unambiguous_one(self):
        for text, ok in (('isUploaded=1', True), ('isUploaded=0', False),
                         ('isUploaded=10', False), ('unknown', False),
                         ('isUploaded=1 isUploaded=0', False)):
            with self.subTest(text=text), mock.patch.object(g.subprocess, 'run', return_value=types.SimpleNamespace(stdout=text)):
                if ok:
                    g.check_uploaded(Path('/synthetic'))
                else:
                    with self.assertRaises(g.Refusal):
                        g.check_uploaded(Path('/synthetic'))

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
