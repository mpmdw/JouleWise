#!/usr/bin/env python3
"""B5 of the R1 slot desk (RL-135; spec section 2.5): RL-107's three proofs and the named
test ids, recorded on the slots PR head.

Blind-safe: code and registration only. Reads the head checkout's
``configs/campaigns/align_v4/registration/r1_slots.json``, the desk's ``record.json``
(``identity.registration_sha256`` only) and the ten condition-13 sources; runs named
unit tests in a subprocess with ``cwd=ROOT``.

Proofs:
1. RL-107 item 1: ``R1ExecutedSourceTests`` two named tests, each line ``... ok``
   (a skip is not a pass).
2. RL-107 item 2: ``r1_slots.json`` ``executed_commit`` == the night commit, and its
   sha256 == ``record.json`` ``identity.registration_sha256``.
3. RL-107 item 3: the head's own ``verify_r1_executed_sources(root, slots)`` returns the
   night commit; beside it the ten sha256 values recomputed on the head and whether each
   equals the night commit's bytes.
4. RL-106 / RL-112: the named classes and test, every line ``... ok``.

Usage:
  python3.13 -B -s -E scripts/align_r1_slots_proofs.py --root HEAD_CHECKOUT \
      --record out/record.json --night-commit <40-hex> --json-out out/proofs.json

Exit 0: every proof ok. 1: some proof not ok. 2: unusable input.
Output is deterministic: sorted keys, no wall clock.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = 'joulewise.align_r1_slots_proofs.v1'
SLOTS_PATH = 'configs/campaigns/align_v4/registration/r1_slots.json'
PYTHON = sys.executable or 'python3.13'
PROOF1_IDS = (
    'tests.align.test_v4_registration.R1ExecutedSourceTests.test_condition13_names_exactly_the_ten_ruled_sources',
    'tests.align.test_v4_registration.R1ExecutedSourceTests.test_condition13_changes_each_file_commit_and_missing_phase_module',
)
PROOF4_IDS = (
    'tests.align.test_r1_followup.DefaultBundleTests',
    'tests.align.test_r1_followup.DispatchTests',
    'tests.test_w1_reliability.OutcomeTests.test_nonzero_chain_exit_faults_result_hazard_and_courier_without_changing_go',
)
TEN = 10
# unittest -v: "test_name (module.Class.test_name)" then, on this or a later line
# (a docstring line may intervene), " ... <result>".
_HEAD = re.compile(r'^(\w+) \(([\w.]+)\)')


class Unusable(RuntimeError):
    pass


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args, binary=False):
    out = subprocess.run(['git', *args], cwd=root, capture_output=True, check=False)
    if out.returncode:
        return None
    return out.stdout if binary else out.stdout.decode().strip()


def parse_verbose(stderr):
    """{full test id: (result text, evidence line)} from unittest -v output."""
    results, current, lines = {}, None, stderr.splitlines()
    for line in lines:
        match = _HEAD.match(line)
        if match:
            name, dotted = match.groups()
            current = dotted if dotted.endswith('.' + name) else f'{dotted}.{name}'
        if current is not None and ' ... ' in line:
            results[current] = (line.rsplit(' ... ', 1)[1].strip(), line.strip())
            current = None
    return results


def child_env():
    """The caller's environment without PYTHONPATH: the head's own tree (cwd) is the only import root."""
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    return env


def run_ids(root, test_id):
    proc = subprocess.run([PYTHON, '-B', '-m', 'unittest', '-v', test_id], cwd=root, env=child_env(),
                          capture_output=True, text=True, check=False)
    return proc.returncode, parse_verbose(proc.stderr), proc.stderr


def test_proof(root, proof_id, test_id):
    """ok iff the id names at least one test and every test under it reads '... ok'."""
    rc, results, stderr = run_ids(root, test_id)
    mine = {k: v for k, v in results.items() if k == test_id or k.startswith(test_id + '.')}
    if not mine:
        tail = [x for x in stderr.strip().splitlines() if x.strip()][-1:] or ['no output']
        return {'id': proof_id, 'test_id': test_id, 'ok': False,
                'evidence_lines': [f'test id not found ({tail[0]})'], 'unittest_rc': rc}
    ok = rc == 0 and all(result == 'ok' for result, _ in mine.values())
    return {'id': proof_id, 'test_id': test_id, 'ok': ok,
            'evidence_lines': [line for _, (_, line) in sorted(mine.items())], 'unittest_rc': rc}


def head_registration(root, slots_path):
    """The head's R1_EXECUTED_SOURCES and verify_r1_executed_sources result, from its own code."""
    code = ('import json,sys\nfrom pathlib import Path\nsys.path.insert(0, ".")\n'
            'from joulewise.align.apple import v4_registration as v\n'
            'out = {"sources": list(v.R1_EXECUTED_SOURCES), "module": str(Path(v.__file__).resolve())}\n'
            'try:\n'
            '    out["commit"] = v.verify_r1_executed_sources(Path("."), json.loads(Path(sys.argv[1]).read_text()))\n'
            'except Exception as e:\n'
            '    out["error"] = f"{type(e).__name__}: {e}"\n'
            'print(json.dumps(out))\n')
    proc = subprocess.run([PYTHON, '-B', '-s', '-E', '-c', code, slots_path], cwd=root,
                          capture_output=True, text=True, check=False)
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {'error': 'head registration import failed: ' + (proc.stderr.strip().splitlines() or ['?'])[-1]}


def prove(root, record_path, night):
    root = Path(root).resolve()
    if not re.fullmatch(r'[0-9a-f]{40}', night or ''):
        raise Unusable('--night-commit must be a full 40-hex commit')
    head = git(root, 'rev-parse', 'HEAD')
    if not head:
        raise Unusable(f'{root}: not a git checkout')
    try:
        record = json.loads(Path(record_path).read_text())
    except (OSError, ValueError) as error:
        raise Unusable(f'record.json unreadable: {error}') from error
    proofs = []
    for test_id in PROOF1_IDS:
        proofs.append(test_proof(root, 'proof1:' + test_id.rsplit('.', 1)[1], test_id))

    slots_file = root / SLOTS_PATH
    try:
        raw = slots_file.read_bytes()
        slots = json.loads(raw)
    except (OSError, ValueError) as error:
        raw, slots = None, None
        proofs.append({'id': 'proof2:slots_commit_and_sha', 'ok': False,
                       'evidence_lines': [f'{SLOTS_PATH} unreadable: {error}']})
    if raw is not None:
        expected = (record.get('identity') or {}).get('registration_sha256') if isinstance(record, dict) else None
        digest = sha256_bytes(raw)
        commit = slots.get('executed_commit') if isinstance(slots, dict) else None
        lines = [f'executed_commit {commit} {"==" if commit == night else "!="} night {night}',
                 f'sha256({SLOTS_PATH}) {digest} ' + (
                     'record.json identity.registration_sha256 absent' if expected is None else
                     f'{"==" if digest == expected else "!="} record.json identity.registration_sha256 {expected}')]
        proofs.append({'id': 'proof2:slots_commit_and_sha', 'ok': commit == night and expected == digest,
                       'evidence_lines': lines})

    reg = head_registration(root, str(slots_file))
    sources = reg.get('sources') or []
    ten = []
    night_bytes_ok = True
    for path in sources:
        try:
            local = (root / path).read_bytes()
            digest = sha256_bytes(local)
        except OSError:
            local, digest = None, None
        committed = git(root, 'show', f'{night}:{path}', binary=True)
        if committed is None:
            night_bytes_ok = False
        ten.append({'path': path, 'sha256': digest,
                    'equals_night': local is not None and committed is not None and local == committed})
    p3_lines = []
    if len(sources) != TEN:
        p3_lines.append(f'R1_EXECUTED_SOURCES has {len(sources)} entries, not {TEN}')
    if 'error' in reg:
        p3_lines.append('verify_r1_executed_sources: ' + reg['error'])
    else:
        p3_lines.append(f'verify_r1_executed_sources -> {reg.get("commit")} '
                        f'{"==" if reg.get("commit") == night else "!="} night {night}')
    if not night_bytes_ok:
        p3_lines.append('a source is absent at the night commit (or the commit is not in this repository)')
    differing = [row['path'] for row in ten if not row['equals_night']]
    if differing:
        p3_lines.append('differs from the night commit: ' + ', '.join(differing))
    proofs.append({'id': 'proof3:condition13_sources',
                   'ok': (len(sources) == TEN and 'error' not in reg and reg.get('commit') == night
                          and not differing and night_bytes_ok),
                   'evidence_lines': p3_lines})

    for test_id in PROOF4_IDS:
        proofs.append(test_proof(root, 'proof4:' + test_id.split('.', 2)[2], test_id))

    dirty = git(root, 'status', '--porcelain', '--untracked-files=no')
    # Review fix 7 (L1): the tests and the ten hashes are read from the working tree, so a checkout with
    # tracked changes does not prove the head it names.
    proofs.append({'id': 'head_clean', 'ok': dirty == '',
                   'evidence_lines': (['no tracked change in the checkout'] if dirty == '' else
                                      ['tracked changes in the checkout (or git status failed): the proofs are '
                                       'not of head ' + str(head)]
                                      + ['    ' + line for line in (dirty or '').splitlines()[:50]])})
    return {'schema': SCHEMA, 'head': head, 'night_commit': night,
            'worktree_tracked_changes': bool(dirty),
            'record': {'path': str(record_path), 'sha256': sha256_bytes(Path(record_path).read_bytes())},
            'proofs': proofs, 'ten_paths': ten, 'all_ok': all(p['ok'] for p in proofs)}


def render(report):
    lines = [f"R1 slots proofs: head {report['head']} night {report['night_commit']}"
             + ('  [tracked files modified in the checkout]' if report['worktree_tracked_changes'] else '')]
    for p in report['proofs']:
        lines.append(f"{'ok  ' if p['ok'] else 'FAIL'} {p['id']}")
        lines.extend('    ' + line for line in p['evidence_lines'])
    lines.append('ten condition-13 paths (sha256 on head; equals night):')
    for row in report['ten_paths']:
        lines.append(f"    {row['sha256']}  {'yes' if row['equals_night'] else 'NO '}  {row['path']}")
    lines.append('all_ok: ' + str(report['all_ok']))
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--night-commit', required=True)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        report = prove(args.root, args.record, args.night_commit)
    except Unusable as error:
        print(f'slots proofs: {error}', file=sys.stderr)
        return 2
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(render(report))
    return 0 if report['all_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
