#!/usr/bin/env python3
"""Read-only pre-arm gate. No external media may be attached during a window.

Inspect diskutil's external inventory AND mount, so an unmounted USB disk or
a mounted network/image volume cannot evade the check. Output contains only
device IDs and mount points, never mount options, server URLs or credentials.
Run again immediately before arming; this cannot prevent a later attachment.
"""
import json
import plistlib
import re
import subprocess
import sys


class Refusal(ValueError):
    pass


def command(argv):
    return subprocess.run(argv, check=True, capture_output=True, timeout=30).stdout


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


def census(run=command):
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
    return dict(schema='joulewise.external-volume-census.v1',
                safe_to_arm=not disks and not rejected,
                external_device_ids=disks, refused_mounts=sorted(set(rejected)))


def main():
    if sys.platform != 'darwin':
        raise Refusal('pre-arm census requires macOS')
    result = census()
    print(json.dumps(result, sort_keys=True))
    return 0 if result['safe_to_arm'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        # Never export raw subprocess stderr or mount lines into custody logs.
        print('STOP: external volume census failed; inspect locally', file=sys.stderr)
        sys.exit(1)
