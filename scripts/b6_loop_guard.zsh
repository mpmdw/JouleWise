#!/bin/zsh
# Native zsh reads and stat: no Python process during an active collection.
emulate -L zsh
zmodload zsh/stat
zmodload zsh/datetime
loop_root=${JW_B6_LOOP_ROOT:-/Users/edr/night-b6/loop}
active=$loop_root/collection.active
if [[ -f $active ]]; then
    { IFS= read -r terminal; IFS= read -r overrun_s; } < $active
    typeset -A info
    if zstat -H info -- "$active" 2>/dev/null && [[ -n $terminal && ! -e $terminal && $overrun_s == <-> ]] &&
       (( EPOCHSECONDS - info[mtime] < overrun_s )); then
        exit 0
    fi
fi
# DONE is terminal. The loop publishes this marker after its final I/O;
# an explicit control that changes state makes the guard fall through again.
if [[ -f $loop_root/done.idle && -f $loop_root/state.json ]]; then
    while IFS= read -r line; do
        if [[ $line =~ '^  "state"[[:space:]]*:[[:space:]]*"DONE"[[:space:]]*,?[[:space:]]*$' ]]; then
            exit 0
        fi
    done < $loop_root/state.json
fi
if [[ -n ${JW_B6_LOOP_TICK:-} ]]; then
    # An argv string split by zsh's lexical parser, never evaluated as shell code.
    typeset -a tick_argv
    tick_argv=(${(z)JW_B6_LOOP_TICK})
    exec "${(@Q)tick_argv}"
fi
repo_root=${0:A:h:h}
exec /opt/homebrew/bin/python3.13 -B "$repo_root/scripts/b6_loop.py" tick --loop-root "$loop_root"
