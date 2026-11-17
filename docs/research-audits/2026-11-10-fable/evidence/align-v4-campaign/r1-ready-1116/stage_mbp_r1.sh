#!/bin/zsh
# Lead/magistrate only, in a clean close interval. No SSH, Python, tests,
# measurement command, custody read, notice, installation or dependency install.
# Copy this committed package to an ordinary private preparation directory first.
# Usage: JW_CLOSE_WINDOW_CONFIRMED=yes ./stage_mbp_r1.sh [--dry-run]
set -euo pipefail
DRY=0
if [[ ${1:-} == --dry-run ]]; then DRY=1; shift; fi
(( $# == 0 )) || { print -u2 'STAGE STOP: unexpected argument'; exit 1; }
REPO=${JW_REPO:-/Users/edr/code/JouleWise}
WT=${JW_R1_WT:-/Users/edr/code/jw-wt/r1-slot-b2e01464d}
OUT=${JW_R1_STAGE:-/Users/edr/r1-preparation/r1-slot-b2e01464d}
VENV=${JW_R1_VENV:-/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv}
FENCE_ROOT=${JW_FENCE_ROOT:-/Users/edr/night-custody/magistrate}
PIN=b2e01464d6d4fbf2901ff4d4154df9455104a12a
HERE=${0:A:h}
die() { print -u2 -r -- "STAGE STOP: $*"; exit 1; }
run() { if (( DRY )); then print -r -- "DRY: ${(q)@}"; else "$@"; fi; }
[[ ${JW_CLOSE_WINDOW_CONFIRMED:-} == yes ]] || die 'lead must confirm the latest close Check, restores, copy/offload and absence of every armed window'
for p in "$REPO" "$WT" "$OUT" "$FENCE_ROOT" "$VENV"; do
  [[ $p == /* && $p != *$'\n'* && $p != *'/../'* && $p != */.. && $p != *'/./'* && $p != */. ]] || die 'use absolute paths without dot components'
done
[[ $WT != $REPO && $WT != $REPO/* && $OUT != $REPO && $OUT != $REPO/* && $OUT != $WT && $OUT != $WT/* ]] || die 'preparation and measurement checkout must be separate'
[[ ! -L $WT && ! -L $OUT ]] || die 'symlink destination'
[[ -d $FENCE_ROOT ]] || die 'fence observation root unavailable'
[[ ! -e $FENCE_ROOT/desk_fence.json && ! -L $FENCE_ROOT/desk_fence.json ]] || die 'desk fence exists; leave it untouched'
# pgrep 1 means absent; an observation error is a refusal.
set +e
pgrep -fl 'cadence_legs_runner|launch_cadence_span|align_r1_rehearsal|run_align_r1|launch_align_r0|run_night.py|km003c_monitor|hazard_monitor|powermetrics|close_offload|span_offload' >/dev/null 2>&1
rc=$?
set -e
[[ $rc == 1 ]] || die 'runner/monitor/offload present or process observation failed'
set +e
jobs=$(launchctl list 2>/dev/null)
rc=$?
set -e
[[ $rc == 0 ]] || die 'launchctl observation failed'
if print -r -- "$jobs" | /usr/bin/grep -Eq 'com\.joulewise\.(night|align-r0|.*icloud)'; then
  die 'night/smoke/iCloud job loaded; lead resolves before staging'
fi
if (( ! DRY )) && [[ ${JW_NO_FETCH:-0} != 1 ]]; then
  git -C "$REPO" fetch origin ops/2026-11-11-w1-presign
fi
git -C "$REPO" cat-file -e "$PIN^{commit}" || die 'pinned source object unavailable; fetch in a clean close interval'
if [[ -e $WT ]]; then
  [[ $(git -C "$WT" rev-parse --show-toplevel) == $WT ]] || die 'destination is not its own checkout'
  [[ $(git -C "$WT" rev-parse HEAD) == $PIN ]] || die 'existing checkout has another HEAD'
  if git -C "$WT" symbolic-ref -q HEAD >/dev/null; then die 'existing checkout is attached'; fi
  [[ -z $(git -C "$WT" status --porcelain --untracked-files=all) ]] || die 'existing checkout is dirty; preserve it'
else
  run mkdir -p "${WT:h}"
  run git -C "$REPO" worktree add --detach "$WT" "$PIN"
fi
# Check all pinned blobs even in dry-run. Verify working bytes when present.
while read -r expected name; do
  [[ $(git -C "$REPO" show "$PIN:$name" | shasum -a 256 | cut -c1-64) == $expected ]] || die "committed source hash $name"
  if [[ -e $WT ]]; then
    [[ ! -L $WT/$name && $(shasum -a 256 "$WT/$name" | cut -c1-64) == $expected ]] || die "working source hash $name"
  fi
done < "$HERE/SOURCES.sha256"
# prepare_checks uses ROOT/.venv. An actual directory is required by the
# existing .venv/ ignore rule (a .venv symlink would dirty the checkout).
# Link its existing contents; never rebuild/install dependencies.
[[ -x $VENV/bin/python ]] || die 'established measurement interpreter unavailable'
[[ -f $VENV/pyvenv.cfg && -d $VENV/lib ]] || die 'established venv layout unavailable'
[[ ! -L $WT/.venv ]] || die 'existing .venv is a symlink; preserve it'
run mkdir -p "$WT/.venv"
for entry in "$VENV"/*(DN); do
  target="$WT/.venv/${entry:t}"
  if [[ -e $target || -L $target ]]; then
    [[ -L $target && $(readlink "$target") == $entry ]] || die "existing venv entry differs: ${entry:t}"
  else
    run ln -s "$entry" "$target"
  fi
done
if (( ! DRY )); then
  [[ -z $(git -C "$WT" status --porcelain --untracked-files=all) ]] || die 'staging left a dirty checkout'
fi
# Frozen copies of preparation artifacts, outside the measurement tree.
# Existing different bytes are never overwritten; create-only publication.
for name in KIT.json ENTRY-DRAFT.json PLAN-INPUTS-DRAFT.json ITEM-R1.md CHECKLIST.md READY-FORECAST.md AMENDMENT-R1-DRAFT.md CARRY-RECORD-DRAFT.md VERIFICATION.md CI-AND-MERGES.json SOURCES.sha256 verify_sources.py; do
  if [[ -e $OUT/$name || -L $OUT/$name ]]; then
    [[ ! -L $OUT/$name ]] && cmp -s "$HERE/$name" "$OUT/$name" || die "existing preparation differs: $name"
  elif (( DRY )); then
    print -r -- "DRY: copy $name to $OUT/$name"
  else
    mkdir -p "$OUT"
    tmp=$(mktemp "$OUT/.stage.XXXXXX")
    cp "$HERE/$name" "$tmp"
    if ! ln "$tmp" "$OUT/$name"; then rm -f "$tmp"; die "concurrent preparation writer: $name"; fi
    rm -f "$tmp"
  fi
done
print -r -- "SOURCE STAGED ONLY (dry-run $DRY) $(date '+%Y-%m-%d %H:%M:%S %Z') pin $PIN worktree $WT preparation $OUT"
print -r -- 'NEXT: lead verifies the package commit and records staging; fresh D-7/host checks/plan/notice/install remain. No READY record was written.'
