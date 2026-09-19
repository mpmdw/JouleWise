#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
# A230 records that 09-16 opened a ledger session and was retained despite
# runbook 0.7's empty discovery glob. It is inert, but that docs conflict is
# unresolved. This seat brief explicitly orders byte-preserving retirement
# of BOTH roots for tonight's section 1.4 precondition; it amends no rule.
# No clone is moved. Validate BOTH roots before the first mv.
print -- 'CHECK: no com.joulewise.night* label may be loaded'
loaded="$(launchctl list)" || exit 3
print -r -- "$loaded"
if print -r -- "$loaded" | awk 'NF && $NF ~ /^com[.]joulewise[.]night/ {found=1} END {exit !found}'; then
  print -u2 -- 'REFUSED: a night label is loaded; nothing moved'
  exit 3
fi
export RETIRE_LOG_DIR="${0:A:h}/retirement-evidence"
python3 -B - <<'PY'
import hashlib, json, os, re, stat, subprocess, time
from decimal import Decimal
from pathlib import Path

def check(ok, message):
    print(('PASS: ' if ok else 'REFUSED: ') + message, flush=True)
    if not ok:
        raise ValueError(message)

def tree(root):
    result = {}
    def visit(directory):
        for p in sorted(directory.iterdir()):
            s = p.lstat(); rel = p.relative_to(root).as_posix()
            if stat.S_ISDIR(s.st_mode):
                kind, value = 'directory', None
            elif stat.S_ISREG(s.st_mode):
                kind, value = 'file', hashlib.sha256(p.read_bytes()).hexdigest()
            elif stat.S_ISLNK(s.st_mode):
                kind, value = 'symlink', os.readlink(p)
            else:
                raise ValueError('unsupported entry: ' + str(p))
            result[rel] = dict(kind=kind, value=value, size=s.st_size,
                               mtime_ns=s.st_mtime_ns, mode=stat.S_IMODE(s.st_mode))
            if kind == 'directory':
                visit(p)
    visit(root)
    return result

def checksum(root, sums):
    print(f'CHECK: (cd {root} && shasum -a 256 -c {sums})', flush=True)
    subprocess.run(['shasum', '-a', '256', '-c', str(sums)], cwd=root, check=True)

try:
    prepared = []
    epoch = int(time.time())
    for day in ('20260916', '20260917'):
        ident = 'd079-epoch-25g83-derivation-n1-' + day
        live = Path('/Users/edr/night-custody') / ident
        archives = sorted(Path('/Users/edr/night-archive').glob(ident + '-harvest-2026091[0-9]'))
        archives = [p for p in archives if p.is_dir()]
        check(len(archives) == 1, f'/Users/edr/night-archive: exactly one existing harvest archive for {ident}: {archives}')
        archive = archives[0]
        sums = archive / 'SHA256SUMS'
        inventory = Path(str(archive) + '.lstat-inventory.txt')
        destination = archive.parent / (ident + '-plan-root-retired-' + str(epoch))
        for p in (live, archive):
            check(p.is_dir() and not p.is_symlink(), f'real directory {p}')
        for p in (sums, inventory):
            check(p.is_file() and not p.is_symlink(), f'archive evidence file {p}')
        check(not os.path.lexists(destination), f'destination absent {destination}')
        before, copied = tree(live), tree(archive)
        # The archive alone contains its added checksum manifest.
        copied.pop('SHA256SUMS', None)
        check(before.keys() == copied.keys(), f'complete archive/live path set {archive} == {live}')
        for rel, entry in before.items():
            other = copied[rel]
            check((entry['kind'], entry['value']) == (other['kind'], other['value']),
                  f'byte/type equality {archive / rel} == {live / rel}')
        expected = set()
        for line in inventory.read_text().splitlines():
            size, stamp, rel = line.split(maxsplit=2)
            rel = rel.removeprefix('./')
            check(not Path(rel).is_absolute() and '..' not in Path(rel).parts,
                  f'safe inventory path {inventory}: {rel}')
            expected.add(rel)
            row = before.get(rel)
            check(row is not None and row['size'] == int(size)
                  and row['mtime_ns'] == int(Decimal(stamp) * 1_000_000_000),
                  f'lstat size/mtime/presence {inventory}: {live / rel}')
        actual = {rel for rel, row in before.items()
                  if row['kind'] != 'directory' and not rel.startswith('results-clone/')}
        check(bool(expected) and expected == actual, f'complete non-results-clone inventory {inventory}')
        checksum_paths = set()
        for line in sums.read_text().splitlines():
            digest, rel = line.split(maxsplit=1)
            rel = rel.removeprefix('*').removeprefix('./')
            check(re.fullmatch(r'[0-9a-f]{64}', digest) is not None
                  and not Path(rel).is_absolute() and '..' not in Path(rel).parts,
                  f'safe checksum entry {sums}: {rel}')
            checksum_paths.add(rel)
        check(checksum_paths == expected, f'SHA256SUMS paths equal lstat inventory {sums}')
        checksum(archive, sums)
        checksum(live, sums)
        prepared.append((live, archive, sums, inventory, destination, before))
    # All archive mismatches above refuse before ANY root moves.
    logs = Path(os.environ['RETIRE_LOG_DIR']); logs.mkdir(exist_ok=False)
    for live, archive, sums, inventory, destination, before in prepared:
        check(tree(live) == before, f'unchanged since precheck {live}')
    for live, archive, sums, inventory, destination, before in prepared:
        (logs / (live.name + '-before.json')).write_text(json.dumps(before, sort_keys=True, indent=2) + '\n')
        print(f'MOVE: mv {live} {destination}', flush=True)
        subprocess.run(['mv', str(live), str(destination)], check=True)
        after = tree(destination)
        check(after == before, f'exact pre/post lstat + bytes inventory {destination}')
        checksum(destination, sums)
        (logs / (live.name + '-after.json')).write_text(json.dumps(after, sort_keys=True, indent=2) + '\n')
        print(f'RETIRED: {destination}', flush=True)
        if live.name.endswith('20260917'):
            print(f'MANUAL EXPORT: export RETIRED_0917_ROOT={destination}', flush=True)
except (OSError, TypeError, ValueError, subprocess.CalledProcessError) as exc:
    print(f'REFUSED: {exc}; no further moves; retain any completed move exactly where reported', flush=True)
    raise SystemExit(3)
PY
print -- 'CHECK: discovery glob below must be empty'
setopt BARE_GLOB_QUAL
print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
remaining=(/Users/edr/night-custody/*/night_plan.json(N))
(( ${#remaining} == 0 )) || exit 3
print -- 'STEP0 OK: both plan roots retired; clones untouched; discovery empty'
