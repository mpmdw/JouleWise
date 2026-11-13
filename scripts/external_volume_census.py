#!/usr/bin/env python3
"""Read-only pre-arm gate. No external media may be attached during a window.

Two independent layers must both be clean:

1. Volumes: diskutil's external inventory AND mount, so an unmounted USB disk
   or a mounted network/image volume cannot evade the check.
2. Bus devices (review N2): `diskutil eject` removes the media but leaves an
   enclosure's USB4/Thunderbolt/USB bridge powered on the bus, so layer 1 goes
   clean. system_profiler (Thunderbolt, USB, USB host, NVMe) and ioreg
   (Thunderbolt switches, USB host devices, block-storage devices) are compared
   against an unplugged baseline recorded ONCE on the measurement Mac, in its
   exact measurement cabling, before the SSD is ever plugged in. Any device row
   absent from that baseline refuses.

Without a baseline the census always refuses. Output contains only device IDs,
mount points and generic device labels; serials and platform identifiers enter
only as SHA-256 digests. Never mount options, server URLs or credentials.
Run again immediately before arming; this cannot prevent a later attachment.

Usage (Ed/magistrate, on the measurement Mac):
  external_volume_census.py --record-baseline NEW.json --attest-unplugged
  external_volume_census.py --baseline BASELINE.json --baseline-sha256 HEX
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import plistlib
import re
import subprocess
import sys

SCHEMA = 'joulewise.external-volume-census.v2'
BASELINE_SCHEMA = 'joulewise.bus-baseline.v1'
SP_TYPES = ('SPThunderboltDataType', 'SPUSBDataType', 'SPUSBHostDataType', 'SPNVMeDataType')
IOREG_CLASSES = ('IOThunderboltSwitch', 'IOUSBHostDevice', 'IOBlockStorageDevice')
# Link/power/speed/BSD numbering may change without any device change; they are
# not identity. Everything else (names, vendor/product IDs, serials, receptacle
# status, detachable/removable flags, sizes, topology) is identity.
VOLATILE = ('speed', 'link_status', 'power', 'current', 'bsd_name', 'free', 'smart_status',
            'mount', 'writable', 'time', 'retain', 'busy', 'state', 'registryentryid')
IOREG_KEYS = ('IOObjectClass', 'IORegistryEntryName', 'Depth', 'Route String', 'UID',
              'Device ID', 'Device Model ID', 'Device Model Name', 'Device Vendor ID',
              'Device Vendor Name', 'Upstream Port Number', 'idVendor', 'idProduct',
              'USB Product Name', 'USB Vendor Name', 'USB Serial Number', 'kUSBProductString',
              'kUSBVendorString', 'kUSBSerialNumberString', 'locationID', 'bDeviceClass')
IOREG_NESTED = {'Protocol Characteristics': ('Physical Interconnect', 'Physical Interconnect Location'),
                'Device Characteristics': ('Product Name', 'Vendor Name', 'Serial Number',
                                           'Medium Type')}


class Refusal(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refusal(reason)


def command(argv):
    timeout = 180 if argv[0].endswith('system_profiler') else 30
    return subprocess.run(argv, check=True, capture_output=True, timeout=timeout).stdout


def external_ids(value):
    if not isinstance(value, dict) or not isinstance(value.get('AllDisks'), list):
        raise Refusal('unknown diskutil external inventory')
    ids = value['AllDisks']
    if any(not isinstance(d, str) or not re.fullmatch(r'disk\d+(?:s\d+)*', d) for d in ids):
        raise Refusal('unknown external device ID')
    entries = value.get('AllDisksAndPartitions')
    if not isinstance(entries, list) or (entries and not ids):
        raise Refusal('inconsistent external inventory')
    return sorted(set(ids))


def mounted_rows(text):
    rows = []
    for line in text.splitlines():
        m = re.fullmatch(r'(.+?) on (/.+|/) \(([^\n()]*)\)', line)
        if not m:
            raise Refusal('unknown mount format')
        rows.append((m[1], m[2], m[3].split(',')[0].strip()))
    if not rows or not any(path == '/' for _, path, _ in rows):
        raise Refusal('mount inventory lacks system root')
    return rows


def volume_census(run=command):
    disks = external_ids(plistlib.loads(run(['/usr/sbin/diskutil', 'list', '-plist', 'external'])))
    mounts = mounted_rows(run(['/sbin/mount']).decode('utf-8'))
    rejected = []
    for device, path, kind in mounts:
        if path == '/Volumes' or path.startswith('/Volumes/'):
            rejected.append(path)
        elif re.fullmatch(r'/dev/disk\d+(?:s\d+)*', device):
            info = plistlib.loads(run(['/usr/sbin/diskutil', 'info', '-plist', device]))
            # APFS synthesized disks/snapshots are admitted only with affirmative
            # internal-media identity. Missing/ambiguous keys fail closed.
            if info.get('Internal') is not True:
                rejected.append(path)
        elif not ((device == 'devfs' and path == '/dev' and kind == 'devfs') or
                  (kind == 'autofs' and path in ('/System/Volumes/Data/home', '/home'))):
            rejected.append(path)
    return disks, sorted(set(rejected))


def _volatile(key):
    folded = key.casefold().replace(' ', '_')
    return any(word in folded for word in VOLATILE)


def _scalar(value):
    return isinstance(value, (str, int, float, bool))


def _row(source, label, identity):
    text = json.dumps([source, identity], sort_keys=True, ensure_ascii=True, separators=(',', ':'))
    return dict(digest=hashlib.sha256(text.encode()).hexdigest(), label=source + ': ' + label)


def sp_rows(doc):
    """Flatten every system_profiler node (bus, receptacle, device, drive)."""
    require(isinstance(doc, dict), 'unknown system_profiler inventory')
    rows, present = [], sorted(k for k in SP_TYPES if k in doc)

    def walk(source, path, value):
        if isinstance(value, list):
            for child in value:
                walk(source, path, child)
            return
        if not isinstance(value, dict):
            return
        name = value.get('_name')
        here = path + ((name,) if isinstance(name, str) else ())
        identity = dict(path=list(here), fields=sorted(
            [k, v] for k, v in value.items() if _scalar(v) and not _volatile(k)))
        rows.append(_row(source, '/'.join(str(p) for p in here) or '(node)', identity))
        for key, child in sorted(value.items()):
            if isinstance(child, (dict, list)):
                walk(source, here + (key,), child)

    for key in present:
        require(isinstance(doc[key], list), 'unknown system_profiler section')
        walk(key, (), doc[key])
    return present, rows


def ioreg_rows(cls, raw):
    if not raw.strip():
        return []  # no instance of this class is registered
    entries = plistlib.loads(raw)
    require(isinstance(entries, list) and all(isinstance(e, dict) for e in entries),
            'unknown ioreg inventory')
    rows = []
    for entry in entries:
        identity = sorted([k, entry[k]] for k in IOREG_KEYS if k in entry and _scalar(entry[k]))
        for outer, keys in IOREG_NESTED.items():
            inner = entry.get(outer)
            if isinstance(inner, dict):
                identity += sorted([outer + '/' + k, inner[k]] for k in keys
                                   if k in inner and _scalar(inner[k]))
        label = str(entry.get('IORegistryEntryName', entry.get('IOObjectClass', '?')))
        rows.append(_row('ioreg:' + cls, label, identity))
    return rows


def machine_digest(run=command):
    raw = run(['/usr/sbin/ioreg', '-r', '-d', '1', '-c', 'IOPlatformExpertDevice', '-a'])
    entries = plistlib.loads(raw)
    uuid = entries[0].get('IOPlatformUUID') if isinstance(entries, list) and entries else None
    require(isinstance(uuid, str) and re.fullmatch(r'[0-9A-F-]{36}', uuid), 'unknown platform identity')
    return hashlib.sha256(('joulewise-bus-baseline:' + uuid).encode()).hexdigest()


def bus_inventory(run=command):
    doc = json.loads(run(['/usr/sbin/system_profiler', '-json', *SP_TYPES]))
    present, rows = sp_rows(doc)
    for cls in IOREG_CLASSES:
        rows += ioreg_rows(cls, run(['/usr/sbin/ioreg', '-r', '-c', cls, '-a', '-d', '1']))
    rows.sort(key=lambda r: (r['label'], r['digest']))
    return dict(machine_sha256=machine_digest(run), system_profiler_sections=present,
                ioreg_classes=list(IOREG_CLASSES), rows=rows), doc


def check_baseline(baseline):
    require(isinstance(baseline, dict) and baseline.get('schema') == BASELINE_SCHEMA and
            set(baseline) == {'schema', 'machine_sha256', 'system_profiler_sections',
                              'ioreg_classes', 'rows', 'attestation'} and
            isinstance(baseline['rows'], list) and baseline['rows'] and
            all(isinstance(r, dict) and set(r) == {'digest', 'label'} and
                re.fullmatch('[0-9a-f]{64}', str(r['digest'])) for r in baseline['rows']),
            'unknown bus baseline')


def extra_devices(current, baseline):
    check_baseline(baseline)
    require(current['machine_sha256'] == baseline['machine_sha256'],
            'bus baseline was recorded on a different Mac')
    require(current['system_profiler_sections'] == baseline['system_profiler_sections'] and
            current['ioreg_classes'] == baseline['ioreg_classes'],
            'bus inventory sections differ from baseline; re-record after review')
    extra = (collections.Counter(r['digest'] for r in current['rows']) -
             collections.Counter(r['digest'] for r in baseline['rows']))
    labels = {r['digest']: r['label'] for r in current['rows']}
    return sorted(labels[d] for d in extra.elements())


def census(run=command, baseline=None):
    disks, rejected = volume_census(run)
    result = dict(schema=SCHEMA, external_device_ids=disks, refused_mounts=rejected)
    if baseline is None:
        result.update(bus_baseline='ABSENT: census cannot see an ejected-but-plugged enclosure',
                      extra_bus_devices=None)
        bus_ok = False
    else:
        extras = extra_devices(bus_inventory(run)[0], baseline)
        result.update(bus_baseline='compared', extra_bus_devices=extras)
        bus_ok = not extras
    result['safe_to_arm'] = not disks and not rejected and bus_ok
    return result


def _detachable(value):
    if isinstance(value, list):
        return any(_detachable(v) for v in value)
    if isinstance(value, dict):
        return (str(value.get('detachable_drive', '')).casefold() == 'yes' or
                str(value.get('removable_media', '')).casefold() == 'yes' or
                any(_detachable(v) for v in value.values()))
    return False


def record_baseline(run=command):
    """Unplugged state only: volume layer clean and no detachable NVMe drive.

    The bus layer cannot know by itself that nothing is plugged in: Ed attests
    it, and Saturday's eject-before-unplug acceptance test proves that this
    baseline discriminates the actual enclosure.
    """
    disks, rejected = volume_census(run)
    require(not disks and not rejected, 'volume census not clean; unplug everything first')
    inventory, doc = bus_inventory(run)
    require(not _detachable(doc.get('SPNVMeDataType', [])),
            'detachable NVMe drive present; unplug it before recording the baseline')
    inventory.update(schema=BASELINE_SCHEMA,
                     attestation='Ed: SSD/enclosure not plugged in; exact measurement cabling')
    return inventory


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--baseline', type=Path)
    p.add_argument('--baseline-sha256')
    p.add_argument('--record-baseline', type=Path)
    p.add_argument('--attest-unplugged', action='store_true')
    args = p.parse_args(argv)
    if sys.platform != 'darwin':
        raise Refusal('pre-arm census requires macOS')
    if args.record_baseline is not None:
        require(args.attest_unplugged and args.baseline is None,
                '--record-baseline requires --attest-unplugged and no --baseline')
        baseline = record_baseline(command)
        data = (json.dumps(baseline, sort_keys=True, indent=1) + '\n').encode()
        with args.record_baseline.open('xb') as f:  # never overwrite a baseline
            f.write(data)
        print(json.dumps(dict(schema=BASELINE_SCHEMA, path=str(args.record_baseline),
                              sha256=hashlib.sha256(data).hexdigest(), rows=len(baseline['rows']),
                              labels=sorted({r['label'] for r in baseline['rows']})),
                         sort_keys=True))
        return 0
    baseline = None
    if args.baseline is not None:
        data = args.baseline.read_bytes()
        require(args.baseline_sha256 is not None and
                hashlib.sha256(data).hexdigest() == args.baseline_sha256,
                'bus baseline digest missing or mismatched')
        baseline = json.loads(data)
    result = census(command, baseline=baseline)
    print(json.dumps(result, sort_keys=True))
    return 0 if result['safe_to_arm'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        # Never export raw subprocess stderr or mount lines into custody logs.
        reason = str(exc) if isinstance(exc, Refusal) else type(exc).__name__
        print('STOP: external volume census failed (' + reason + '); inspect locally',
              file=sys.stderr)
        sys.exit(1)
