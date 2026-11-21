#!/usr/bin/env python3
"""Census reviewed Git blobs, never checkout/model/data paths or merged trees."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import subprocess

ROLES = ('main', 'bytes', 'b6', 'align-v4', 'amendment-1', 'r0-v4')
AMENDMENT = 'docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md'
ALIGN = 'configs/campaigns/align_pilot_v4/'
B6_ROSTER = 'docs/design/block6_collection_draft.md'


def safe_input(name):
    p = PurePosixPath(name)
    if (p.is_absolute() or str(p) != name or '..' in p.parts or
            {'restricted', 'withheld'} & {s.casefold() for s in p.parts} or
            p.parts[0] not in ('configs', 'docs') or ':' in name):
        raise ValueError('blinded or unsafe Git input: STOP without opening')
    return name


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


def model_ids(text):
    # Conservative identity aliases also cover prose-only plan model names and
    # HF models--org--name spellings. These are KEEP, never guessed local paths.
    return set(m.rstrip('.,;:') for m in re.findall(
        r'(?i)(?:Qwen|Llama|Mistral|Gemma|DeepSeek|Phi)[A-Za-z0-9_.-]+', text))


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def commit(repo, ref):
    sha = git(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    if not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('not a full reviewed commit SHA')
    return sha


def blob_names(repo, sha):
    entries = {}
    for record in git(repo, 'ls-tree', '-r', '-z', sha, '--', 'configs', 'docs').split(b'\0'):
        if record:
            metadata, name = record.decode().split('\t', 1)
            mode, kind, _ = metadata.split()
            entries[name] = (mode, kind)
    return entries


def derive(repo, refs, r0_config):
    """Each role supplies its own reviewed ref. All bytes come from git show."""
    if set(refs) != set(ROLES):
        raise ValueError('all six reviewed ref roles are required')
    safe_input(r0_config)
    paths, ids, receipts, reviewed = set(), set(), [], {}
    for role in ROLES:
        sha = commit(repo, refs[role])
        reviewed[role] = sha
        entries = blob_names(repo, sha)
        selected = {p for p in entries if p.endswith('/identity_pins.json') or
                    'roster' in PurePosixPath(p).name.lower() and p.endswith(('.json', '.md'))}
        required = {
            'main': set(),
            'bytes': {'configs/campaigns/bytes_v1/roster.json', 'configs/bytes/identity_pins.json'},
            'b6': {'configs/b6/registration/identity_pins.json', B6_ROSTER},
            'align-v4': {ALIGN + 'registration/identity_pins.json'},
            'amendment-1': {AMENDMENT},
            'r0-v4': {r0_config},
        }[role]
        if role == 'align-v4':
            selected |= {p for p in entries if p.startswith(ALIGN) and p.endswith(('.json', '.md'))}
        selected |= required
        if not selected or not required <= entries.keys():
            raise ValueError('STOP: required reviewed inputs missing for ' + role)
        for name in sorted(selected):
            safe_input(name)
            if entries[name] not in (('100644', 'blob'), ('100755', 'blob')):
                raise ValueError('symlink or non-file Git input')
            data = git(repo, 'show', sha + ':' + name)
            text = data.decode('utf-8')
            found = sources(json.loads(text)) if name.endswith('.json') else set(re.findall(
                r'/Users/edr/(?:jw_models|\.cache/huggingface)/[^\s`|<>"\)]+', text))
            if role == 'r0-v4' and name == r0_config and not found:
                raise ValueError('R0 config has no model sources')
            paths |= found
            aliases = model_ids(text)
            ids |= aliases
            receipts.append(dict(role=role, ref=refs[role], commit=sha, input=name,
                                 sha256=hashlib.sha256(data).hexdigest(),
                                 sources=sorted(found), model_ids=sorted(aliases)))
    if not paths:
        raise ValueError('empty model KEEP')
    return dict(schema='joulewise.offload.model-census.v2', reviewed_refs=reviewed,
                r0_config=r0_config, paths=sorted(paths), model_ids=sorted(ids), inputs=receipts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--main-ref', default='origin/main')
    p.add_argument('--bytes-ref', default='c58282f87')
    p.add_argument('--b6-ref', default='dda456f98')
    p.add_argument('--align-ref', required=True)
    p.add_argument('--amendment-ref', default='origin/lane/2026-11-05-align-window-council')
    p.add_argument('--r0-ref', required=True)
    p.add_argument('--r0-config', required=True, help='repository-relative Git blob path')
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    refs = dict(zip(ROLES, (args.main_ref, args.bytes_ref, args.b6_ref, args.align_ref,
                           args.amendment_ref, args.r0_ref)))
    result = derive(args.repo, refs, args.r0_config)
    with args.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print('\n'.join(result['paths']))


if __name__ == '__main__':
    main()
