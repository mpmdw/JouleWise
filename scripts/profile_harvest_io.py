#!/usr/bin/env python3
"""Bounded-residency SYNTHETIC harvest I/O profile; no study-data discovery.

Processes every requested byte, in stripes so a 26.4 GB test does not consume
the machine's remaining disk. This measures I/O primitives, NOT a full harvest
or a cold-cache/native performance claim. CPU use is bounded to two threads.
"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.b5.harvest import archive_sources, tree_inventory
from joulewise.harvest_transport import pack_raw, unpack_raw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--total-gb', type=float, required=True)
    p.add_argument('--output', type=Path, required=True, help='new JSON receipt')
    p.add_argument('--stripe-mib', type=int, default=128)
    args = p.parse_args()
    if not 0 < args.total_gb <= 26.4 or not 16 <= args.stripe_mib <= 512:
        p.error('total-gb must be in (0,26.4]; stripe-mib in 16..512')
    try:
        os.nice(10)
        nice_applied = True
    except PermissionError:
        nice_applied = False
    totals, calls = {}, {}

    @contextmanager
    def timed(stage):
        start = time.monotonic()
        yield
        totals[stage] = totals.get(stage, 0.0)+time.monotonic()-start
        calls[stage] = calls.get(stage, 0)+1

    # The repeated XML is intentionally low entropy: report the ratio rather
    # than treating it as the ratio of a real window's traces.
    xml = (b'<?xml version="1.0"?><plist version="1.0"><dict>'
           b'<key>elapsed_ns</key><integer>100000000</integer>'
           b'<key>processor</key><dict><key>gpu_power</key><real>12456</real>'
           b'</dict></dict></plist>\0')
    block = (xml*((1 << 20)//len(xml)+1))[:1 << 20]
    rng = random.Random(20261108)
    total = int(args.total_gb*1e9)
    pm_total, other_total = int(total*.89), total-int(total*.89)
    remaining = total
    compressed, files, stripes = 0, 0, 0
    with args.output.open('x', encoding='utf-8') as receipt:
        with tempfile.TemporaryDirectory(prefix='harvest-io-') as tmp:
            root = Path(tmp)
            while remaining:
                budget = min(remaining, args.stripe_mib << 20)
                pm = min(pm_total, int(budget*.89)) if remaining > budget else pm_total
                other = budget-pm
                pm_total -= pm
                other_total -= other
                source = root/'source'
                source.mkdir()
                with timed('generate'):
                    # Eight files/stripe give bounded hashing actual parallel work.
                    for kind, count in (('powermetrics.plist', pm), ('other.bin', other)):
                        for index in range(4):
                            n = count//4 + (index < count % 4)
                            path = source/f'{index}-{kind}'
                            with path.open('xb') as stream:
                                while n:
                                    size = min(n, len(block))
                                    stream.write(block[:size] if kind.endswith('plist') else rng.randbytes(size))
                                    n -= size
                with timed('archive_serial_hash_copy_verify'):
                    original = archive_sources({'raw': source}, root/'serial', workers=1)
                with timed('archive_parallel_hash_copy_verify'):
                    parallel = archive_sources({'raw': source}, root/'parallel', workers=2)
                if (original != parallel or (root/'serial/sources/SHA256SUMS').read_bytes()
                        != (root/'parallel/sources/SHA256SUMS').read_bytes()):
                    raise AssertionError('archive equality')
                with timed('final_source_rehash'):
                    if tree_inventory(source, workers=2) != original['raw']:
                        raise AssertionError('source changed')
                expected = original['raw']
                with timed('stream_hash_compress'):
                    packed = pack_raw(source, root/'transport', expected, workers=2)
                with timed('decompress_hash_write_verify'):
                    unpack_raw(root/'transport', root/'air', expected)
                compressed += packed['payload_bytes']
                files += packed['files']
                stripes += 1
                remaining -= budget
                for name in ('source', 'serial', 'parallel', 'transport', 'air'):
                    shutil.rmtree(root/name)  # only this invocation's synthetic stripe
                if stripes % 20 == 0:
                    print(json.dumps({'processed_GB': (total-remaining)/1e9}), flush=True)
        record = {'schema': 'joulewise.synthetic_harvest_io.v1', 'synthetic': True,
            'total_bytes': total, 'powermetrics_bytes': int(total*.89), 'files': files,
            'stripes': stripes, 'stripe_mib': args.stripe_mib, 'workers': 2,
            'nice_applied': nice_applied,
            'payload_bytes': compressed, 'stage_wall_s': totals, 'stage_calls': calls,
            'byte_equality': True, 'limits': [
                'low-entropy XML-shaped bytes, not complete valid PM records',
                'bounded resident stripes; warm filesystem cache; loaded host',
                'no full-window reducer, eligibility or native measurement timing']}
        receipt.write(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(json.dumps(record, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
