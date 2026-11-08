"""Small synthetic full-consumer-chain benchmark; never loads model weights.

This historical timing helper splices only the pilot and session modules. Use
test_desk_equivalence_review for whole-tree equivalence and heterogeneous
residual/thermal evidence; timing output here is not that stronger proof.

python3.13 -B -m tests.align.desk_benchmark --reference <base-sha> --output <new-dir>
The harvest subprocess is an inert receipt producer; its inputs are already
synthetic archived records. No hardware/production-harvest timing is implied.
"""
import argparse
from contextlib import nullcontext, redirect_stdout
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import subprocess
import time
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from scripts import align_v4_session as current
from tests.align.test_desk_parallel import synthetic_record

ROOT = Path(__file__).resolve().parents[2]


def reference_module(revision, name):
    path = f'scripts/{name}.py'
    source = subprocess.run(['git', '-C', str(ROOT), 'show', f'{revision}:{path}'],
                            check=True, capture_output=True, text=True,
                            env=dict(os.environ, GIT_NO_LAZY_FETCH='1')).stdout
    module = ModuleType('desk_serial_reference_'+name)
    module.__file__ = str(ROOT/path)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--members', type=int, default=18)
    parser.add_argument('--samples', type=int, default=12000)
    parser.add_argument('--repeat', type=int, default=2)
    args = parser.parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=False)
    session = synthetic_record(args.output/'record', args.members)
    (session/'staging').mkdir()
    for path in (args.output/'record/runs').glob('*/power_trace.csv'):
        with path.open() as handle:
            rows = list(csv.DictReader(handle))
        first, last = float(rows[0]['timestamp_s']), float(rows[-1]['timestamp_s'])
        with path.open('w') as handle:
            writer = csv.writer(handle, lineterminator='\n')
            writer.writerow(('timestamp_s', 'power_w', 'source', 'rail'))
            for i in range(args.samples):
                writer.writerow((first+(last-first)*i/(args.samples-1), 7.5+(i%11)*.01, 'mock', 'mock'))
    old = reference_module(args.reference, 'align_v4_session')
    old.pilot = reference_module(args.reference, 'align_pilot_session')
    observations, golden = [], None
    # This is the only subprocess seam under timing: it returns a synthetic
    # existing-harvest receipt and deliberately never launches harvest code.
    def harvested(argv, **kwargs):
        return SimpleNamespace(returncode=6, stdout='synthetic harvest receipt\n', stderr='')
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (args.output/'record').rglob('*') if p.is_file()}
    for repeat in range(args.repeat):
        for label, module, workers in (('original_serial', old, 1), ('current_serial', current, 1),
                                       ('current_parallel', current, 2)):
            stream = io.StringIO()
            profile = args.output/f'{repeat}-{label}.json'
            started = time.perf_counter()
            with redirect_stdout(stream), patch('joulewise.align.apple.v4_registration.validate_u3'), \
                    patch('joulewise.align.apple.desk_execution.host_desk_guard', side_effect=lambda _: nullcontext()):
                options = {} if module is old else {'workers': workers, 'profile': profile}
                module.desk(session, run=harvested, **options)
            wall = time.perf_counter()-started
            outputs = ((session/'PILOT.json').read_bytes(), (session/'desk.json').read_bytes(), stream.getvalue())
            if golden is None:
                golden = outputs
            assert outputs == golden, f'full-chain byte inequality: {label}'
            # Canonical desk writes are permitted; all original evidence stays fixed.
            assert all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in before.items())
            observations.append(dict(repeat=repeat, path=label, workers=workers, wall_s=wall,
                                     output_bytes=sum(len(v.encode() if isinstance(v, str) else v) for v in outputs),
                                     peak_parent_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
            print(json.dumps(observations[-1], sort_keys=True), flush=True)
    record = dict(reference=args.reference, members=args.members, samples_per_member=args.samples,
                  input_bytes=sum(path.stat().st_size for path in before),
                  missing_members=1, corrupt_members=1, observations=observations,
                  equality='PILOT.json, desk.json and stdout byte-identical to original serial',
                  cache='OS cache uncontrolled; repeated identical synthetic inputs; no cache flush',
                  harvest='inert synthetic receipt producer; no real harvest launched',
                  pending_gate='validate_u3 isolated in parent only for downstream rendering')
    (args.output/'benchmark.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
