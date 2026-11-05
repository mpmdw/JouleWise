#!/usr/bin/env python3
"""Derive model KEEP paths from repository text only. Never follow model paths."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import subprocess


def sources(value, model_context=False):
    found = set()
    if isinstance(value, list):
        for child in value:
            found |= sources(child, model_context)
    elif isinstance(value, dict):
        for key, child in value.items():
            context = model_context or key in ('model', 'models', 'model_artifact_inventory')
            if isinstance(child, str) and child.startswith('/') and (
                    key == 'model_source' or
                    key in ('source', 'root', 'resolved_path') and (
                        context or '/jw_models/' in child or '/huggingface/' in child)):
                p = PurePosixPath(child)
                if '..' in p.parts or str(p) != child or child != child.strip():
                    raise ValueError('noncanonical model source')
                found.add(child)
            found |= sources(child, context)
    return found


def derive(repo, r0_config):
    names = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z',
                                     '--', 'configs', 'docs'], text=True).split('\0')
    # Superset: every config JSON, not only the currently named kit/roster.
    selected = sorted(p for p in names if p and (
        p.startswith('configs/') and p.endswith('.json') or
        'roster' in PurePosixPath(p).name.lower()))
    required = ('configs/campaigns/bytes_v1/roster.json',
                'configs/b6/registration/identity_pins.json',
                'configs/bytes/identity_pins.json')
    if not all(p in selected for p in required) or not any(
            '/align_pilot_' in p and p.endswith('/registration/identity_pins.json') for p in selected):
        raise ValueError('STOP: integrated BYTES/B6/ALIGN source files missing')
    r0 = r0_config.relative_to(repo).as_posix()  # config must be in this checkout
    if r0 not in selected:
        selected.append(r0)
    paths, receipts = set(), []
    for name in selected:
        parts = PurePosixPath(name).parts
        if '..' in parts or {'restricted', 'withheld'} & set(parts):
            raise ValueError('blinded input path: STOP without opening')
        p = repo / name
        for component in (p, *p.parents):
            if component == repo:
                break
            if component.is_symlink():
                raise ValueError('symlink repository input')
        data = p.read_bytes()
        if p.suffix == '.json':
            found = sources(json.loads(data))
        else:
            # Do not invent a local directory from a prose model name. The
            # roster must supply machine-readable sources in configs; operator
            # compares prose roster IDs against this printed source census.
            found = set(re.findall(
                r'/Users/edr/(?:jw_models|\.cache/huggingface)/[^\s`|<>"\)]+',
                data.decode('utf-8')))
        paths |= found
        receipts.append(dict(input=name, sha256=hashlib.sha256(data).hexdigest(),
                             sources=sorted(found)))
    if not sources(json.loads(r0_config.read_bytes())):
        raise ValueError('R0 config has no model sources')
    if not paths:
        raise ValueError('empty model KEEP')
    return sorted(paths), receipts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--r0-config', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    paths, receipts = derive(args.repo, args.r0_config)
    with args.output.open('x') as f:
        json.dump(dict(paths=paths, inputs=receipts), f, indent=2)
        f.write('\n')
    print('\n'.join(paths))


if __name__ == '__main__':
    main()
