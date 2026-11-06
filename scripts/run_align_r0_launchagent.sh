#!/bin/bash
# launchd owns this process. Its PID owns the desk fence until cleanup finishes.
set -euo pipefail
helper=$1 python_bin=$2 custody=$3 purpose=$4 magistrate_pid=$5 deadline=$6
exit_wait=$7 pmset_bin=$8 disk_path=$9
shift 9
pgrep_bin=$1 kill_bin=$2
shift 2
child_pid=""
stopped_pids=""

cleanup() {
    local code=$? pid
    trap - EXIT
    trap '' TERM INT HUP
    if [[ -n "$child_pid" ]]; then
        "$kill_bin" -TERM "$child_pid" 2>/dev/null || true
        wait "$child_pid" 2>/dev/null || true
    fi
    for pid in $stopped_pids; do
        # Record failed attempts, including disappeared PIDs, for the operator.
        if ! "$kill_bin" -CONT "$pid"; then
            echo "Spotlight resume failed for pid $pid; operator check required" >&2
            code=2
        fi
    done
    "$python_bin" "$helper" clear --custody-root "$custody" --purpose "$purpose" --pid "$$" || code=2
    exit "$code"
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP

# Background + wait lets bash handle SIGTERM while the helper/runner is busy.
"$python_bin" "$helper" handoff --custody-root "$custody" --purpose "$purpose" \
    --pid "$$" --magistrate-pid "$magistrate_pid" --deadline "$deadline" \
    --exit-wait-seconds "$exit_wait" &
child_pid=$!
wait "$child_pid"
child_pid=""
"$python_bin" "$helper" preflight --pmset-bin "$pmset_bin" --disk-path "$disk_path"

for name in corespotlightd spotlightknowledged; do
    matches=""
    if matches=$("$pgrep_bin" -x "$name"); then
        for pid in $matches; do
            [[ "$pid" =~ ^[0-9]+$ && "$pid" -gt 1 ]] || { echo "invalid Spotlight pid: $pid" >&2; exit 2; }
            # Record before STOP so a partial failure still attempts every CONT.
            stopped_pids="$stopped_pids $pid"
            "$kill_bin" -STOP "$pid"
        done
    else
        rc=$?
        [[ "$rc" -eq 1 ]] || { echo "Spotlight census failed for $name (exit $rc)" >&2; exit 2; }
    fi
done
"$python_bin" "$helper" run --deadline "$deadline" --runner-spec "$1" &
child_pid=$!
wait "$child_pid"
child_pid=""
