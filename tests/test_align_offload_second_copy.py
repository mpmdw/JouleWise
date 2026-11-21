"""SSD and cloud proof tests use only temp trees and injected macOS responses."""
import importlib.util
import io
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tarfile
import tempfile
import types
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('copy_guard', Path(__file__).resolve().parents[1] /
                                             'scripts/align_offload_delete_root.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class SecondCopyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.src = self.root / 'source'
        self.src.mkdir()
        (self.src / 'bytes').write_bytes(b'synthetic only')
        self.item = self.root / 'item'
        self.item.mkdir()
        self.mount = self.root / 'Volumes' / 'Borrowed SSD'
        self.restore = self.mount / 'restore'
        self.restore.mkdir(parents=True)
        (self.restore / 'bytes').write_bytes(b'synthetic only')
        self.manifest = self.mount / 'manifest.json'
        self.manifest.write_bytes(g.encoded(g.tree(self.src)))
        self.sha = g.sha_file(self.manifest)
        self.archive = self.mount / 'archive.tar.zst'
        self.archive.write_bytes(b'synthetic compressed archive')
        self.asha = g.sha_file(self.archive)
        self.info = dict(VolumeUUID='synthetic-uuid', Internal=False, MountPoint=str(self.mount),
                         FilesystemType='apfs', BusProtocol='PCI-Express',
                         APFSPhysicalStores=[{'APFSPhysicalStore': 'disk6s2'}])
        self.store = dict(Internal=False, BusProtocol='PCI-Express', ParentWholeDisk='disk6',
                          MediaName='')
        self.whole = dict(Internal=False, BusProtocol='PCI-Express', ParentWholeDisk='disk6',
                          MediaName='WD_BLACK SN7100 2TB', VirtualOrPhysical='Physical')
        self.receipt = dict(schema='joulewise.offload.independent-copy.v1', source=str(self.src),
                            manifest_sha256=self.sha, archive_sha256=self.asha,
                            volume=str(self.mount), volume_uuid='synthetic-uuid',
                            archive=str(self.archive), manifest=str(self.manifest),
                            restore=str(self.restore), verified_utc='2026-11-07T18:00:00Z')
        self.write_receipt()
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(g, 'VOLUME_ROOT', self.root / 'Volumes').start()
        self.mounted = mock.patch.object(g.os.path, 'ismount', return_value=True).start()
        self.queried = []
        def info(p):
            self.queried.append(str(p))
            return {'disk6s2': self.store, 'disk6': self.whole}.get(str(p), self.info)
        mock.patch.object(g, 'external_info', side_effect=info).start()
        self.device = mock.patch.object(g, 'volume_device', side_effect=lambda p:
                                        2 if p == self.mount or self.mount in p.parents else 1).start()

    def write_receipt(self):
        (self.item / 'independent-copy.json').write_text(json.dumps(self.receipt))

    def check(self):
        return g.independent_copy(self.item, self.src, self.sha, self.asha)

    def test_mounted_independent_full_copy_passes(self):
        self.assertEqual(self.check(), self.receipt)

    def test_unplugged_remounted_wrong_uuid_or_internal_device_refuses(self):
        self.mounted.return_value = False
        with self.assertRaisesRegex(g.Refusal, 'not mounted'):
            self.check()
        self.mounted.return_value = True
        for key, value in (('VolumeUUID', 'replacement'), ('Internal', True),
                           ('MountPoint', '/other'), ('FilesystemType', 'unknown')):
            old = self.info[key]
            self.info[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(g.Refusal, 'identity mismatch'):
                self.check()
            self.info[key] = old

    def test_disk_image_or_non_physical_store_is_not_an_independent_copy(self):
        # Review N7/S9: an hdiutil APFS image on the internal SSD reports
        # Internal=false, FilesystemType=apfs, BusProtocol='Disk Image'.
        for target, key, value in ((self.info, 'BusProtocol', 'Disk Image'),
                                   (self.store, 'BusProtocol', 'Disk Image'),
                                   (self.whole, 'BusProtocol', 'Disk Image'),
                                   (self.whole, 'MediaName', 'Disk Image'),
                                   (self.whole, 'VirtualOrPhysical', 'Virtual'),
                                   (self.whole, 'Internal', True),
                                   (self.store, 'Internal', None),
                                   (self.info, 'BusProtocol', 'Apple Fabric'),
                                   (self.info, 'BusProtocol', None),
                                   (self.store, 'ParentWholeDisk', '../disk0'),
                                   (self.info, 'APFSPhysicalStores', []),
                                   (self.info, 'APFSPhysicalStores', [{'APFSPhysicalStore': 'disk0s2;x'}])):
            old = target.get(key)
            target[key] = value
            with self.subTest(key=key, value=value), \
                    self.assertRaisesRegex(g.Refusal, 'not on physical external'):
                self.check()
            target[key] = old
        for bus in ('USB', 'Thunderbolt', 'PCI-Express'):
            self.info['BusProtocol'] = self.store['BusProtocol'] = self.whole['BusProtocol'] = bus
            self.assertEqual(self.check(), self.receipt)

    def test_volume_check_enrolls_physical_media_name(self):
        g.external_volume_identity(self.mount, 'synthetic-uuid', 'WD_BLACK SN7100 2TB')
        for media in ('Other Disk', ''):
            with self.assertRaisesRegex(g.Refusal, 'physical media mismatch'):
                g.external_volume_identity(self.mount, 'synthetic-uuid', media)
        with self.assertRaisesRegex(g.Refusal, 'identity mismatch'):
            g.external_volume_identity(self.mount, 'other-uuid', 'WD_BLACK SN7100 2TB')

    def test_same_device_and_path_escape_refuse(self):
        self.device.side_effect = lambda p: 1
        with self.assertRaisesRegex(g.Refusal, 'shares source'):
            self.check()
        self.device.side_effect = lambda p: 2 if p == self.mount or self.mount in p.parents else 1
        self.receipt['archive'] = str(self.src / 'bytes')
        self.write_receipt()
        with self.assertRaisesRegex(g.Refusal, 'outside enrolled'):
            self.check()

    def test_missing_mutated_archive_manifest_restore_or_symlink_refuse(self):
        for path in (self.archive, self.manifest, self.restore / 'bytes'):
            old = path.read_bytes()
            path.write_bytes(b'corrupt')
            with self.subTest(path=path), self.assertRaisesRegex(g.Refusal, 'bytes mismatch'):
                self.check()
            path.write_bytes(old)
            path.unlink()
            with self.assertRaises((OSError, g.Refusal)):
                self.check()
            path.symlink_to('/synthetic-target-must-never-be-opened')
            with self.assertRaises(g.Refusal):
                self.check()
            path.unlink()
            path.write_bytes(old)

    def test_receipt_bindings_cannot_be_reused_for_another_item(self):
        for key in ('source', 'manifest_sha256', 'archive_sha256'):
            old = self.receipt[key]
            self.receipt[key] = 'wrong'
            self.write_receipt()
            with self.subTest(key=key), self.assertRaisesRegex(g.Refusal, 'binding mismatch'):
                self.check()
            self.receipt[key] = old

    def test_enrollment_checks_all_members_before_exclusive_publication(self):
        (self.item / 'source-path.txt').write_text(str(self.src) + '\n')
        (self.item / 'source.json').write_bytes(self.manifest.read_bytes())
        (self.item / 'source.sha256').write_text(self.sha + '  ' + str(self.item / 'source.json') + '\n')
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode='w') as tf:
            tf.add(self.src, arcname='.')
        child = mock.MagicMock()
        child.wait.return_value = 0
        child.stdout = data
        with mock.patch.object(g.subprocess, 'Popen', return_value=mock.MagicMock(
                __enter__=mock.Mock(return_value=child), __exit__=mock.Mock(return_value=False))):
            # Existing receipt is never silently overwritten.
            data.seek(0)
            with self.assertRaises(FileExistsError):
                g.enroll_second(self.item, self.mount, 'synthetic-uuid', self.archive,
                                self.manifest, self.restore)
            (self.item / 'independent-copy.json').unlink()
            data.seek(0)
            g.enroll_second(self.item, self.mount, 'synthetic-uuid', self.archive,
                            self.manifest, self.restore)
            self.assertEqual(self.check()['archive_sha256'], self.asha)


class CloudRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.src = self.root / 'source'
        self.src.mkdir()
        (self.src / 'bytes').write_bytes(b'synthetic bytes')
        self.item = self.root / 'item'
        self.item.mkdir()
        self.remote = self.root / 'cloud'
        self.remote.mkdir()
        self.archive = self.remote / 'item.tar.zst'
        self.archive.write_bytes(b'synthetic compressed archive')
        rows = g.encoded(g.tree(self.src))
        (self.item / 'source.json').write_bytes(rows)
        (self.remote / 'item.manifest.json').write_bytes(rows)
        for name, path in (('source', self.item / 'source.json'), ('archive', self.archive)):
            (self.item / (name + '.sha256')).write_text(g.sha_file(path) + '  ' + str(path) + '\n')
        self.addCleanup(mock.patch.stopall)
        self.uploaded = mock.patch.object(g, 'check_uploaded').start()
        self.run = mock.patch.object(g.subprocess, 'run').start()
        self.wait = mock.patch.object(g, 'wait_dataless').start()
        self.child = mock.MagicMock()
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode='w') as tf:
            tf.add(self.src, arcname='.')
        data.seek(0)
        self.child.stdout = data
        self.child.wait.return_value = 0
        mock.patch.object(g.subprocess, 'Popen', return_value=mock.MagicMock(
            __enter__=mock.Mock(return_value=self.child), __exit__=mock.Mock(return_value=False))).start()

    def test_proof_only_after_both_real_transitions_and_full_member_checks(self):
        g.cloud_roundtrip(self.item, self.remote)
        self.assertEqual(self.uploaded.call_count, 2)
        self.assertEqual([call.args[1] for call in self.wait.call_args_list], [True, False, True, False])
        self.assertEqual((self.item / 'cloud-roundtrip.json').read_bytes(),
                         (self.item / 'source.json').read_bytes())
        self.assertTrue(json.loads((self.item / 'cloud-proof.json').read_text())['evicted_dataless'])

    def test_failed_eviction_upload_hydration_or_decompression_never_publishes_proof(self):
        for gate in (self.wait, self.uploaded):
            gate.side_effect = g.Refusal('synthetic STOP')
            with self.assertRaises(g.Refusal):
                g.cloud_roundtrip(self.item, self.remote)
            self.assertFalse((self.item / 'cloud-proof.json').exists())
            gate.side_effect = None
        self.child.wait.return_value = 1
        with self.assertRaisesRegex(g.Refusal, 'decompression failed'):
            g.cloud_roundtrip(self.item, self.remote)
        self.assertFalse((self.item / 'cloud-proof.json').exists())

    def test_wait_dataless_polls_until_transition_and_times_out_on_noop(self):
        fake = mock.Mock()
        fake.lstat.side_effect = [types.SimpleNamespace(st_flags=0),
                                 types.SimpleNamespace(st_flags=g.DATALESS)]
        # Recover actual wait function; this fixture stubs it for roundtrip tests.
        real = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(real)
        with mock.patch.object(real.time, 'sleep') as sleep:
            real.wait_dataless(fake, True)
            sleep.assert_called_once_with(5)
            fake.lstat.side_effect = None
            fake.lstat.return_value.st_flags = 0
            with self.assertRaisesRegex(real.Refusal, 'not observed'):
                real.wait_dataless(fake, True)
            self.assertEqual(sleep.call_count, 241)


if __name__ == '__main__':
    unittest.main()


@unittest.skipUnless(sys.platform == 'darwin' and os.path.exists('/usr/bin/hdiutil'),
                     'native disk image')
class NativeDiskImageTests(unittest.TestCase):
    """N7, natively: a real APFS image in a TemporaryDirectory on the INTERNAL
    SSD, mounted at a temp mount point, must never pass as the second copy."""

    def test_real_apfs_disk_image_refuses_with_real_diskutil(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            image = root / 'second-copy.sparseimage'
            mount = root / 'Volumes' / 'JWN7IMG'
            mount.mkdir(parents=True)
            subprocess.run(['/usr/bin/hdiutil', 'create', '-size', '40m', '-fs', 'APFS',
                            '-volname', 'JWN7IMG', '-type', 'SPARSE', str(root / 'second-copy')],
                           check=True, capture_output=True)
            attach = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-mountpoint',
                                     str(mount), str(image)], check=True, capture_output=True,
                                    text=True).stdout
            whole = re.search(r'^(/dev/disk\d+)\s', attach, re.M)[1]
            try:
                info = g.external_info(mount)
                # The demonstrated bypass: every legacy identity check passes.
                self.assertIs(info.get('Internal'), False)
                self.assertEqual(info.get('FilesystemType', '').casefold(), 'apfs')
                self.assertEqual(info.get('MountPoint'), str(mount))
                self.assertEqual(info.get('BusProtocol'), 'Disk Image')
                with mock.patch.object(g, 'VOLUME_ROOT', root / 'Volumes'):
                    with self.assertRaisesRegex(g.Refusal, 'not on physical external'):
                        g.external_volume_identity(mount, info['VolumeUUID'])
                    with self.assertRaisesRegex(g.Refusal, 'not on physical external'):
                        g.physical_external(info)
            finally:
                subprocess.run(['/usr/bin/hdiutil', 'detach', '-force', whole],
                               check=True, capture_output=True)
