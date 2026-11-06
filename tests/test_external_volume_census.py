"""Synthetic tool responses only; never run diskutil or enumerate real mounts."""
import importlib.util
from pathlib import Path
import plistlib
import unittest

SPEC = importlib.util.spec_from_file_location('volumes', Path(__file__).resolve().parents[1] /
                                              'scripts/external_volume_census.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class ExternalVolumeTests(unittest.TestCase):
    def setUp(self):
        self.disks = {'AllDisks': [], 'AllDisksAndPartitions': []}
        self.mounts = ('/dev/disk3s1s1 on / (apfs, sealed, local, read-only)\n'
                       'devfs on /dev (devfs, local, nobrowse)\n'
                       '/dev/disk3s5 on /System/Volumes/Data (apfs, local, journaled)\n'
                       'map auto_home on /System/Volumes/Data/home (autofs, automounted)\n')
        self.internal = True
        self.calls = []

    def tool_output(self, argv):
        self.calls.append(argv)
        if argv == ['/usr/sbin/diskutil', 'list', '-plist', 'external']:
            return plistlib.dumps(self.disks)
        if argv == ['/sbin/mount']:
            return self.mounts.encode()
        self.assertEqual(argv[:4], ['/usr/sbin/diskutil', 'info', '-plist', argv[3]])
        return plistlib.dumps({} if self.internal is None else {'Internal': self.internal})

    def test_internal_apfs_system_mounts_pass(self):
        self.assertTrue(v.census(self.tool_output)['safe_to_arm'])

    def test_attached_unmounted_ssd_also_refuses(self):
        self.disks = {'AllDisks': ['disk4', 'disk4s1'],
                      'AllDisksAndPartitions': [{'DeviceIdentifier': 'disk4'}]}
        result = v.census(self.tool_output)
        self.assertFalse(result['safe_to_arm'])
        self.assertEqual(result['external_device_ids'], ['disk4', 'disk4s1'])

    def test_ssd_network_and_image_mounts_refuse_even_if_external_list_empty(self):
        for device, kind in (('/dev/disk6s1', 'apfs'), ('//secret:password@host/share', 'smbfs'),
                             ('/dev/disk8s1', 'hfs')):
            with self.subTest(kind=kind):
                original = self.mounts
                self.mounts += device + ' on /Volumes/Backup SSD (' + kind + ', local)\n'
                result = v.census(self.tool_output)
                self.assertFalse(result['safe_to_arm'])
                self.assertEqual(result['refused_mounts'], ['/Volumes/Backup SSD'])
                self.assertNotIn('password', str(result))
                self.mounts = original

    def test_external_mount_outside_volumes_or_unknown_internal_flag_refuses(self):
        for value in (False, None):
            self.internal = value
            self.assertFalse(v.census(self.tool_output)['safe_to_arm'])

    def test_unknown_non_system_mount_refuses(self):
        self.mounts += '//private on /private/tmp/share (smbfs)\n'
        self.assertFalse(v.census(self.tool_output)['safe_to_arm'])

    def test_malformed_empty_or_missing_census_refuses(self):
        for value in ({}, {'AllDisks': ['not-a-disk'], 'AllDisksAndPartitions': []},
                      {'AllDisks': [], 'AllDisksAndPartitions': [{}]}):
            self.disks = value
            with self.assertRaises(v.Refusal):
                v.census(self.tool_output)
        self.disks = {'AllDisks': [], 'AllDisksAndPartitions': []}
        for text in ('', 'new mount format', 'devfs on /dev (devfs)\n'):
            self.mounts = text
            with self.assertRaises(v.Refusal):
                v.census(self.tool_output)

    def test_tool_failure_never_passes(self):
        def failure(argv):
            raise OSError('synthetic failure')
        with self.assertRaises(OSError):
            v.census(failure)


if __name__ == '__main__':
    unittest.main()
