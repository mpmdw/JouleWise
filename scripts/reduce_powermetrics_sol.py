#!/usr/bin/env python3
"""Reduce explicitly listed raw members off the measurement machine.

Jobs JSON: {"members": [{"id": "m1", "raw": "raw.plist", optional
"episode": "episode.json", "first_record_endpoint_s": ..., and
"nominal_interval_ns": ...}]}. Paths are relative to the jobs file.
An optional uncertainty_evidence object is passed to existing attribution.
No config paths are followed. No decision or refusal is cached.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.align.apple.reduce_sol import cache_path, producer_sha256, reduce_members, turn_energy_table
from joulewise.align.records import Episode, from_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args(argv)
    jobs = json.loads(args.jobs.read_text())['members']
    if not isinstance(jobs, list) or any(not isinstance(j, dict) for j in jobs):
        parser.error('members must be a list of objects')
    if len({j['id'] for j in jobs}) != len(jobs):
        parser.error('duplicate member id')
    def explicit_path(value):
        path = Path(value)
        return path if path.is_absolute() else args.jobs.parent / path
    raw_paths = [explicit_path(j['raw']) for j in jobs]
    inputs = [args.jobs, *raw_paths, *(explicit_path(j['episode']) for j in jobs if 'episode' in j)]
    for path in inputs:
        alias = args.output.resolve() == path.resolve()
        if not alias:
            try:
                alias = args.output.samefile(path)
            except FileNotFoundError:
                pass
        if alias:
            parser.error('--output aliases an input; immutable inputs must be preserved')
    samples = reduce_members(raw_paths,
                             cache_dir=args.cache, workers=args.workers)
    members = []
    for job, columns in zip(jobs, samples):
        row = {'id': job['id'], 'raw_sha256': columns.raw_sha256, 'raw_size': columns.raw_size,
               'samples': len(columns), 'columns_path': str(cache_path(args.cache, columns.raw_sha256)),
               'dropped_tail': columns.dropped_tail}
        if 'episode' in job:
            episode_bytes = explicit_path(job['episode']).read_bytes()
            episode = from_json(Episode, episode_bytes.decode('utf-8'))
            endpoint = job['first_record_endpoint_s']
            row.update(episode_sha256=hashlib.sha256(episode_bytes).hexdigest(),
                       first_record_endpoint_s=endpoint, nominal_interval_ns=job['nominal_interval_ns'],
                       uncertainty_evidence=job.get('uncertainty_evidence'))
            row['energy'] = turn_energy_table(columns, episode,
                    first_record_endpoint_s=endpoint, nominal_interval_ns=job['nominal_interval_ns'],
                    evidence=job.get('uncertainty_evidence'))
            row['native_pm'] = []
            # Arrays are stored in the raw-derived cache. Mapped timestamps are
            # cheap fresh views, tied to this episode's independently read map.
            mapping = next((m for m in episode.clock_mappings
                            if m.trace_domain == 'joulewise.controller.epoch_ns'
                            and m.episode_domain == episode.clock_domain), None)
            if mapping is not None:
                row['native_pm'] = columns.native_pm_samples(endpoint, mapping.offset_ns)
        members.append(row)
    # No output is published for a failed job. Derived columns of earlier valid
    # members may remain, with no admission/selection information in them.
    payload = json.dumps({'schema': 'joulewise.reduce-sol.members.v1',
                         'producer_sha256': producer_sha256(), 'members': members},
                         sort_keys=True, indent=2) + '\n'
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=args.output.parent,
                                         prefix='.reduce-report-', delete=False) as handle:
            name = handle.name
            handle.write(payload)
        os.replace(name, args.output)
    finally:
        if name is not None and os.path.exists(name):
            os.unlink(name)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        raise SystemExit(2)
