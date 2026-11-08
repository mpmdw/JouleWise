#!/usr/bin/env python3
"""R16 offline kit/replay/parser. No native run is started by this CLI.

The magistrate uses condition_waits_native.run_attempt / cw1.execute_kit with
qualified native final checks. This tool only reads explicitly named exports.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import condition_waits as cw, condition_waits_cw1 as kit


def read(path):
    return json.loads(Path(path).read_bytes())


def finalize_standin(output, *, blocks=64):
    """Bounded 64 MiB synthetic write/hash/compress/copy, offline, exclusive.

    Represents operations, not a calibrated dose of finalize/offload heat.
    It does not traverse any pre-existing directory or read any real data.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    block = hashlib.shake_256(b'CW-1 synthetic finalize v1').digest(1024*1024)
    h = hashlib.sha256()
    with (output/'synthetic.bin').open('xb') as f:
        for _ in range(blocks):
            f.write(block)
    with (output/'synthetic.bin').open('rb') as f, (output/'offload.gz').open('xb') as dest:
        with gzip.GzipFile(filename='', fileobj=dest, mode='wb', mtime=0) as compressed:
            while data := f.read(1024*1024):
                h.update(data)
                compressed.write(data)
    return {'synthetic': True, 'bytes': blocks*len(block), 'sha256': h.hexdigest(),
            'operations': ['write', 'sha256', 'gzip', 'local copy stand-in'], 'network': False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    make = sub.add_parser('kit')
    for name in ('python', 'r0-config', 'output', 'r1-sha256', 'reference-authority'):
        make.add_argument('--'+name, required=True)
    replay = sub.add_parser('replay')
    replay.add_argument('--policy', required=True)
    replay.add_argument('--evidence', required=True, help='JSON {header, rows}; no path discovery')
    for name in ('cw1-parse', 'guard-replay'):
        child = sub.add_parser(name)
        child.add_argument('--policy', required=True)
        child.add_argument('--idle-traces', required=True)
        if name == 'cw1-parse':
            child.add_argument('--run', required=True)
    standin = sub.add_parser('finalize-standin')
    standin.add_argument('--output', required=True)
    args = p.parse_args(argv)
    if args.command == 'kit':
        result = kit.run_kit(python=args.python, r0_config=args.r0_config, output=args.output,
                            r1_sha256=args.r1_sha256, reference_authority=args.reference_authority)
    elif args.command == 'finalize-standin':
        result = finalize_standin(args.output)
    elif args.command == 'replay':
        evidence = read(args.evidence)
        result = cw.replay(read(args.policy), evidence['header'], evidence['rows'])
    elif args.command == 'cw1-parse':
        result = kit.parse_run(read(args.policy), read(args.run), read(args.idle_traces))
    else:
        result = kit.guard_replay(read(args.policy), read(args.idle_traces))
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
