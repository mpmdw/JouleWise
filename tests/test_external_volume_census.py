"""Synthetic tool responses for both physical states; the native class only reads
this laptop's bus inventory and attaches a throwaway disk image in a temp dir."""
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

SPEC = importlib.util.spec_from_file_location('volumes', Path(__file__).resolve().parents[1] /
                                              'scripts/external_volume_census.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)

MBP_UUID = '11111111-2222-3333-4444-555555555555'


def receptacle(rid, status='receptacle_no_devices_connected', link='0x100'):
    return dict(current_speed_key='Up to 40 Gb/s', link_status_key=link,
                receptacle_id_key=rid, receptacle_status_key=status)


def unplugged_profile():
    """Measurement MBP in its measurement cabling, SSD never plugged in."""
    return {
        'SPThunderboltDataType': [
            dict(_name='thunderboltusb4_bus_%d' % i, device_name_key='MacBook Pro',
                 vendor_name_key='Apple Inc.', switch_uid_key='0x05AC0000000000%02d' % i,
                 route_string_key='0', receptacle_1_tag=receptacle(str(i + 1)))
            for i in range(3)],
        'SPUSBDataType': [dict(_name='USB31Bus', host_controller='AppleT6031USBXHCI')],
        'SPUSBHostDataType': [],
        'SPNVMeDataType': [dict(_name='Apple SSD Controller', _items=[dict(
            _name='APPLE SSD AP1024Z', bsd_name='disk0', detachable_drive='no',
            device_serial='0ba0000000000001', removable_media='no', size_in_bytes=1000555581440,
            smart_status='Verified', volumes=[dict(_name='Macintosh HD', bsd_name='disk0s2',
                                                    size_in_bytes=994662584320)])])],
    }


INTERNAL_IOREG = {
    'IOThunderboltSwitch': [dict(IOObjectClass='IOThunderboltSwitchType5', Depth=0, UID=100 + i,
                                 IORegistryEntryName='IOThunderboltSwitchType5',
                                 IORegistryEntryID=4294969000 + i, IOObjectRetainCount=27,
                                 **{'Route String': 0, 'Device Vendor Name': 'Apple Inc.'})
                            for i in range(3)],
    'IOUSBHostDevice': [],
    'IOBlockStorageDevice': [dict(IOObjectClass='IOEmbeddedNVMeBlockDevice',
                                  IORegistryEntryName='NS_01', **{
                                      'Protocol Characteristics': {'Physical Interconnect': 'Apple Fabric'},
                                      'Device Characteristics': {'Product Name': 'APPLE SSD AP1024Z'}})],
}

OWC_SWITCH = dict(IOObjectClass='IOThunderboltSwitchType3', Depth=1, UID=9001,
                  IORegistryEntryName='IOThunderboltSwitchType3',
                  **{'Route String': 1, 'Device Vendor Name': 'Other World Computing',
                     'Device Model Name': 'Express 1M2'})


class Machine:
    """Tool-output fixture keyed by exact argv; records every call."""

    def __init__(self):
        self.disks = {'AllDisks': [], 'AllDisksAndPartitions': []}
        self.mounts = ('/dev/disk3s1s1 on / (apfs, sealed, local, read-only)\n'
                       'devfs on /dev (devfs, local, nobrowse)\n'
                       '/dev/disk3s5 on /System/Volumes/Data (apfs, local, journaled)\n'
                       'map auto_home on /System/Volumes/Data/home (autofs, automounted)\n')
        self.internal = True
        self.profile = unplugged_profile()
        self.ioreg = copy.deepcopy(INTERNAL_IOREG)
        self.uuid = MBP_UUID
        self.calls = []

    def __call__(self, argv):
        self.calls.append(argv)
        if argv == ['/usr/sbin/diskutil', 'list', '-plist', 'external']:
            return plistlib.dumps(self.disks)
        if argv == ['/sbin/mount']:
            return self.mounts.encode()
        if argv[:3] == ['/usr/sbin/diskutil', 'info', '-plist']:
            return plistlib.dumps({} if self.internal is None else {'Internal': self.internal})
        if argv[:2] == ['/usr/sbin/system_profiler', '-json']:
            return json.dumps({k: self.profile[k] for k in argv[2:] if k in self.profile}).encode()
        if argv == ['/usr/sbin/ioreg', '-r', '-d', '1', '-c', 'IOPlatformExpertDevice', '-a']:
            return plistlib.dumps([{'IOPlatformUUID': self.uuid, 'IOPlatformSerialNumber': 'SECRET'}])
        if argv[:3] == ['/usr/sbin/ioreg', '-r', '-c'] and argv[4:] == ['-a', '-d', '1']:
            entries = self.ioreg[argv[3]]
            return plistlib.dumps(entries) if entries else b''
        raise AssertionError('unexpected tool call %r' % (argv,))

    # Physical states ------------------------------------------------------
    def plug_usb4_ejected(self, port=0):
        """OWC Express 1M2 on USB4 after `diskutil eject`: media gone, bridge powered."""
        bus = self.profile['SPThunderboltDataType'][port]
        bus['receptacle_1_tag']['receptacle_status_key'] = 'receptacle_connected'
        bus['_items'] = [dict(_name='Express 1M2', vendor_name_key='Other World Computing',
                              device_name_key='Express 1M2', switch_uid_key='0x0001E91000000001',
                              mode_key='usb4', route_string_key='1')]
        self.ioreg['IOThunderboltSwitch'].append(dict(OWC_SWITCH))

    def plug_usb_ejected(self):
        """Same enclosure negotiated as a USB 10 Gb/s device, media ejected."""
        self.profile['SPUSBHostDataType'] = [dict(_name='USB 10Gbps Bus', _items=[dict(
            _name='Express 1M2', USBDeviceKeyVendorID='0x1e91', USBDeviceKeyProductID='0xa2a4',
            USBDeviceKeySerialNumber='OWC-SERIAL-1', USBDeviceKeyLinkSpeed='10 Gb/s')])]
        self.ioreg['IOUSBHostDevice'] = [dict(IOObjectClass='IOUSBHostDevice',
                                              IORegistryEntryName='Express 1M2', idVendor=7825,
                                              idProduct=41636, locationID=0x01100000,
                                              **{'USB Serial Number': 'OWC-SERIAL-1'})]

    def mount_ssd(self):
        self.disks = {'AllDisks': ['disk6', 'disk6s1', 'disk6s2', 'disk7', 'disk7s1'],
                      'AllDisksAndPartitions': [{'DeviceIdentifier': 'disk6'}]}
        self.mounts += '/dev/disk7s1 on /Volumes/JW SN7100 (apfs, local, journaled)\n'
        self.profile['SPNVMeDataType'].append(dict(_name='Generic SSD Controller', _items=[dict(
            _name='WD_BLACK SN7100 2TB', bsd_name='disk6', detachable_drive='yes',
            device_serial='WD-SERIAL', removable_media='no', size_in_bytes=2000398934016)]))
        self.ioreg['IOBlockStorageDevice'].append(dict(
            IOObjectClass='IONVMeBlockStorageDevice', IORegistryEntryName='WD_BLACK SN7100 2TB',
            **{'Protocol Characteristics': {'Physical Interconnect': 'PCI-Express'}}))


class ExternalVolumeTests(unittest.TestCase):
    def setUp(self):
        self.mac = Machine()
        self.baseline = v.record_baseline(self.mac)

    def census(self):
        return v.census(self.mac, baseline=self.baseline)

    # Volume layer (unchanged behavior) -------------------------------------
    def test_internal_apfs_system_mounts_and_baseline_pass(self):
        result = self.census()
        self.assertTrue(result['safe_to_arm'], result)
        self.assertEqual(result['extra_bus_devices'], [])
        self.assertEqual(result['schema'], 'joulewise.external-volume-census.v2')

    def test_no_baseline_never_passes(self):
        result = v.census(self.mac)
        self.assertFalse(result['safe_to_arm'])
        self.assertIn('ABSENT', result['bus_baseline'])

    def test_attached_unmounted_ssd_also_refuses(self):
        self.mac.disks = {'AllDisks': ['disk4', 'disk4s1'],
                          'AllDisksAndPartitions': [{'DeviceIdentifier': 'disk4'}]}
        result = self.census()
        self.assertFalse(result['safe_to_arm'])
        self.assertEqual(result['external_device_ids'], ['disk4', 'disk4s1'])

    def test_ssd_network_and_image_mounts_refuse_even_if_external_list_empty(self):
        for device, kind in (('/dev/disk6s1', 'apfs'), ('//secret:password@host/share', 'smbfs'),
                             ('/dev/disk8s1', 'hfs')):
            with self.subTest(kind=kind):
                original = self.mac.mounts
                self.mac.mounts += device + ' on /Volumes/Backup SSD (' + kind + ', local)\n'
                result = self.census()
                self.assertFalse(result['safe_to_arm'])
                self.assertEqual(result['refused_mounts'], ['/Volumes/Backup SSD'])
                self.assertNotIn('password', str(result))
                self.mac.mounts = original

    def test_external_mount_outside_volumes_or_unknown_internal_flag_refuses(self):
        for value in (False, None):
            self.mac.internal = value
            self.assertFalse(self.census()['safe_to_arm'])

    def test_unknown_non_system_mount_refuses(self):
        self.mac.mounts += '//private on /private/tmp/share (smbfs)\n'
        self.assertFalse(self.census()['safe_to_arm'])

    def test_malformed_empty_or_missing_census_refuses(self):
        for value in ({}, {'AllDisks': ['not-a-disk'], 'AllDisksAndPartitions': []},
                      {'AllDisks': [], 'AllDisksAndPartitions': [{}]}):
            self.mac.disks = value
            with self.assertRaises(v.Refusal):
                self.census()
        self.mac.disks = {'AllDisks': [], 'AllDisksAndPartitions': []}
        for text in ('', 'new mount format', 'devfs on /dev (devfs)\n'):
            self.mac.mounts = text
            with self.assertRaises(v.Refusal):
                self.census()

    def test_tool_failure_never_passes(self):
        def failure(argv):
            raise OSError('synthetic failure')
        with self.assertRaises(OSError):
            v.census(failure, baseline=self.baseline)

    # Bus layer (N2) ----------------------------------------------------------
    def test_ejected_but_plugged_usb4_enclosure_refuses_with_clean_volume_layer(self):
        self.mac.plug_usb4_ejected()
        result = self.census()
        # The pre-N2 census saw nothing: no external disk, no /Volumes mount.
        self.assertEqual(result['external_device_ids'], [])
        self.assertEqual(result['refused_mounts'], [])
        self.assertFalse(result['safe_to_arm'])
        labels = ' '.join(result['extra_bus_devices'])
        self.assertIn('Express 1M2', labels)
        self.assertIn('ioreg:IOThunderboltSwitch', labels)

    def test_each_bus_signal_alone_refuses(self):
        # receptacle status only / device node only / ioreg switch only / block
        # storage only / a duplicated identical switch (multiset count)
        for mutate in (
                lambda m: m.profile['SPThunderboltDataType'][1]['receptacle_1_tag'].update(
                    receptacle_status_key='receptacle_connected'),
                lambda m: m.profile['SPThunderboltDataType'][2].update(
                    _items=[dict(_name='Express 1M2')]),
                lambda m: m.ioreg['IOThunderboltSwitch'].append(dict(OWC_SWITCH)),
                lambda m: m.ioreg['IOBlockStorageDevice'].append(dict(
                    IOObjectClass='IOUSBMassStorageBlockDevice', IORegistryEntryName='OWC Bridge')),
                lambda m: m.ioreg['IOThunderboltSwitch'].append(
                    dict(m.ioreg['IOThunderboltSwitch'][0]))):
            with self.subTest(mutate=mutate):
                self.mac = Machine()
                mutate(self.mac)
                result = self.census()
                self.assertFalse(result['safe_to_arm'])
                self.assertTrue(result['extra_bus_devices'])

    def test_ejected_but_plugged_usb_mode_enclosure_refuses(self):
        self.mac.plug_usb_ejected()
        result = self.census()
        self.assertEqual((result['external_device_ids'], result['refused_mounts']), ([], []))
        self.assertFalse(result['safe_to_arm'])
        self.assertTrue(any('Express 1M2' in label for label in result['extra_bus_devices']))
        self.assertNotIn('OWC-SERIAL-1', json.dumps(result))

    def test_mounted_ssd_refuses_on_both_layers(self):
        self.mac.plug_usb4_ejected()
        self.mac.mount_ssd()
        result = self.census()
        self.assertFalse(result['safe_to_arm'])
        self.assertTrue(result['external_device_ids'] and result['refused_mounts'] and
                        result['extra_bus_devices'])

    def test_full_saturday_sequence_states(self):
        # unplugged PASS -> mounted REFUSE -> ejected-but-plugged REFUSE -> unplugged PASS
        self.assertTrue(self.census()['safe_to_arm'])
        self.mac.plug_usb4_ejected()
        self.mac.mount_ssd()
        self.assertFalse(self.census()['safe_to_arm'])
        self.mac.disks = {'AllDisks': [], 'AllDisksAndPartitions': []}
        self.mac.mounts = Machine().mounts
        ejected = self.census()
        self.assertFalse(ejected['safe_to_arm'])
        self.assertTrue(ejected['extra_bus_devices'])
        self.mac = Machine()  # physically unplugged
        self.assertTrue(self.census()['safe_to_arm'])

    def test_volatile_link_speed_and_bsd_numbering_do_not_false_refuse(self):
        tag = self.mac.profile['SPThunderboltDataType'][0]['receptacle_1_tag']
        tag.update(link_status_key='0x101', current_speed_key='Up to 20 Gb/s')
        drive = self.mac.profile['SPNVMeDataType'][0]['_items'][0]
        drive.update(bsd_name='disk1', smart_status='Unknown')
        drive['volumes'][0]['bsd_name'] = 'disk1s2'
        for entry in self.mac.ioreg['IOThunderboltSwitch']:
            entry.update(IORegistryEntryID=1, IOObjectRetainCount=99)
        self.assertTrue(self.census()['safe_to_arm'])

    def test_baseline_binding_and_format_refusals(self):
        other = Machine()
        other.uuid = 'AAAAAAAA-2222-3333-4444-555555555555'
        with self.assertRaisesRegex(v.Refusal, 'different Mac'):
            v.census(other, baseline=self.baseline)
        fewer = Machine()
        del fewer.profile['SPUSBDataType']
        with self.assertRaisesRegex(v.Refusal, 'sections differ'):
            v.census(fewer, baseline=self.baseline)
        for bad in ({}, dict(self.baseline, rows=[]), dict(self.baseline, extra=1),
                    dict(self.baseline, schema='other'),
                    dict(self.baseline, rows=[{'digest': 'x', 'label': 'y'}])):
            with self.assertRaisesRegex(v.Refusal, 'unknown bus baseline'):
                v.census(self.mac, baseline=bad)

    def test_baseline_redacts_serials_and_platform_identity(self):
        text = json.dumps(self.baseline)
        for secret in (MBP_UUID, 'SECRET', '0ba0000000000001'):
            self.assertNotIn(secret, text)
        self.assertEqual(self.baseline['schema'], 'joulewise.bus-baseline.v1')

    def test_record_baseline_refuses_unclean_or_detachable_state(self):
        mounted = Machine()
        mounted.mount_ssd()
        with self.assertRaisesRegex(v.Refusal, 'volume census not clean'):
            v.record_baseline(mounted)
        detachable = Machine()
        detachable.profile['SPNVMeDataType'][0]['_items'][0]['detachable_drive'] = 'yes'
        with self.assertRaisesRegex(v.Refusal, 'detachable NVMe'):
            v.record_baseline(detachable)

    def test_cli_record_then_pinned_census(self):
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(v, 'command', self.mac), mock.patch.object(v.sys, 'platform', 'darwin'):
            path = Path(d) / 'bus-baseline.json'
            with self.assertRaisesRegex(v.Refusal, 'attest'):
                v.main(['--record-baseline', str(path)])
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(v.main(['--record-baseline', str(path), '--attest-unplugged']), 0)
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(json.loads(out.getvalue())['sha256'], sha)
            with self.assertRaises(FileExistsError):  # never overwritten
                v.main(['--record-baseline', str(path), '--attest-unplugged'])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(v.main(['--baseline', str(path), '--baseline-sha256', sha]), 0)
            for argv in (['--baseline', str(path)],
                         ['--baseline', str(path), '--baseline-sha256', '0' * 64]):
                with self.assertRaisesRegex(v.Refusal, 'digest'):
                    v.main(argv)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(v.main([]), 1)  # no baseline: never safe
            self.mac.plug_usb4_ejected()
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(v.main(['--baseline', str(path), '--baseline-sha256', sha]), 1)
            self.assertTrue(json.loads(out.getvalue())['extra_bus_devices'])


@unittest.skipUnless(sys.platform == 'darwin' and os.path.exists('/usr/bin/hdiutil'),
                     'native macOS bus inventory')
class NativeBusInventoryTests(unittest.TestCase):
    """Read-only bus inventory of THIS laptop; never prints rows or the mount table."""

    def test_native_inventory_is_stable_and_sees_an_attached_unmounted_image(self):
        first, _ = v.bus_inventory()
        baseline = dict(first, schema=v.BASELINE_SCHEMA, attestation='native test')
        v.check_baseline(baseline)
        self.assertEqual(v.extra_devices(v.bus_inventory()[0], baseline), [])
        with tempfile.TemporaryDirectory() as d:
            image = Path(d).resolve() / 'bus.sparseimage'
            subprocess.run(['/usr/bin/hdiutil', 'create', '-size', '20m', '-fs', 'APFS',
                            '-volname', 'JWBUS', '-type', 'SPARSE', str(image.with_suffix(''))],
                           check=True, capture_output=True)
            attach = subprocess.run(['/usr/bin/hdiutil', 'attach', '-nomount', str(image)],
                                    check=True, capture_output=True, text=True).stdout
            whole = re.search(r'^(/dev/disk\d+)\s', attach, re.M)[1]
            try:
                extras = v.extra_devices(v.bus_inventory()[0], baseline)
                self.assertTrue(any('IOBlockStorageDevice' in label for label in extras), extras)
            finally:
                subprocess.run(['/usr/bin/hdiutil', 'detach', '-force', whole],
                               check=True, capture_output=True)
        self.assertEqual(v.extra_devices(v.bus_inventory()[0], baseline), [])


if __name__ == '__main__':
    unittest.main()
