#!/bin/zsh -f
# External scheduler for the R12 full ALPHA/GAMMA sessions on the MBP.
# Synthetic only. Writes nothing inside a chain tree except the seed's
# generator-parent-exit.txt receipt, exactly as b6_r12_batch.py's ended().
#
# usage: b6_r12_mbp_pair.zsh <resolved TMPDIR> <new seed name> <pack>:<new root name>...
# 1. fresh pinned prerequisite seed (b6_r12_session_fixture.py --seed-probe);
# 2. only after seed exit 0, one chain per pack, concurrently:
#    profile session (first smoke driver) && generation-only full supervisor.
# Each step's pid, native start/end and actual exit go to <root>.events.
set -u
T=$1 SEED=$2
shift 2
REPO=${0:A:h:h}
cd -- $REPO || exit 90
PY=/opt/homebrew/opt/python@3.13/bin/python3.13
sane=(/usr/bin/env -u PYTHONPATH -u PYTHONSTARTUP -u PYTHONHOME
      PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
      GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1
      XDG_CONFIG_HOME=$T/r12-xdg-empty PYTHONNOUSERSITE=1 TMPDIR=$T)
mkdir -p -- $T/r12-xdg-empty
stamp() { /bin/date +%Y-%m-%dT%H:%M:%S%z }

run() {  # run <events file> <label> argv... ; actual child pid and exit recorded
  local ev=$1 label=$2
  shift 2
  "${sane[@]}" "$@" < /dev/null &
  local pid=$!
  print -r -- "start label=$label pid=$pid native=$(stamp) argv=${(q)*}" >> $ev
  wait $pid
  local rc=$?
  print -r -- "end label=$label pid=$pid exit=$rc native=$(stamp)" >> $ev
  return $rc
}

[[ -e $T/$SEED ]] && { print -r -- "seed root exists; a fresh seed is required" >&2; exit 91 }
print -r -- "launcher pid=$$ head=$(/usr/bin/git -C $REPO rev-parse HEAD) native=$(stamp)" >> $T/launcher.events
run $T/$SEED.events seed $PY -B scripts/b6_r12_session_fixture.py --out $T/$SEED \
    --synthetic-models --volume prerequisite --seed-probe > $T/$SEED.log 2>&1
rc=$?
[[ -d $T/$SEED ]] && print -r -- $rc > $T/$SEED/generator-parent-exit.txt
print -r -- "seed exit=$rc native=$(stamp)" >> $T/launcher.events
(( rc == 0 )) || exit 2

pids=()
for spec in "$@"; do
  pack=${spec%%:*} name=${spec#*:}
  ( run $T/$name.events first $PY -B scripts/b6_r12_profile_session.py --out $T/$name \
        --prior-chain-root $T/$SEED --pack $pack --scenario plain --volume full \
    && run $T/$name.events supervisor $PY -B scripts/b6_r12_full_supervise.py \
        --cohort-root $T/$name --generation-only ) > $T/$name.log 2>&1 &
  pids+=($!)
  print -r -- "chain pack=$pack root=$T/$name subshell_pid=$! native=$(stamp)" >> $T/launcher.events
done
for pid in $pids; do
  wait $pid
  print -r -- "chain subshell_pid=$pid exit=$? native=$(stamp)" >> $T/launcher.events
done
