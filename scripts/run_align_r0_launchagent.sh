#!/bin/bash
# launchd owns this process. Its PID owns the desk fence until cleanup finishes.
set -euo pipefail
helper=$1 python_bin=$2 custody=$3 purpose=$4 magistrate_pid=$5 deadline=$6
exit_wait=$7 pmset_bin=$8 disk_path=$9
shift 9
pgrep_bin=$1 kill_bin=$2
shift 2
runner_spec=$1 launchctl_bin=$2 service_target=$3
# Durable record of SIGSTOPped Spotlight PIDs. SIGKILL cannot run the trap;
# the record survives for the operator, and the watchdog's stale-fence notice
# points at it. Removed only after every SIGCONT succeeds.
spotlight_record="$(dirname "$runner_spec")/spotlight-stopped"
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
    local resumed=1
    for pid in $stopped_pids; do
        # Record failed attempts, including disappeared PIDs, for the operator.
        if ! "$kill_bin" -CONT "$pid"; then
            echo "Spotlight resume failed for pid $pid; operator check required" >&2
            code=2
            resumed=0
        fi
    done
    if [[ "$resumed" -eq 1 ]]; then
        rm -f "$spotlight_record"
        "$python_bin" "$helper" clear --custody-root "$custody" --purpose "$purpose" --pid "$$" || code=2
    else
        # Leave the fence: once this PID is gone the watchdog removes it and
        # queues a desk_fence_stale notice for Ed.
        echo "desk fence left for watchdog stale notice; see $spotlight_record" >&2
    fi
    # Unload only our unique one-shot label, after runner/Spotlight/fence
    # cleanup. bootout may signal us; termination traps remain ignored here.
    local bootout_output bootout_code
    if bootout_output=$("$launchctl_bin" bootout "$service_target" 2>&1); then
        :
    else
        bootout_code=$?
        if [[ "$bootout_code" -eq 113 && "$bootout_output" == *[Cc]ould\ not\ find\ service* ]] ||
           [[ "$bootout_code" -eq 3 && "$bootout_output" == *[Nn]o\ such\ process* ]]; then
            : # Already unloaded; repeating cleanup is harmless.
        else
            echo "LaunchAgent bootout failed for $service_target: $bootout_output" >&2
            code=2
        fi
    fi
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
    if matches=$("$pgrep_bin" -U "$(id -u)" -x "$name"); then
        for pid in $matches; do
            [[ "$pid" =~ ^[0-9]+$ && "$pid" -gt 1 ]] || { echo "invalid Spotlight pid: $pid" >&2; exit 2; }
            # Record before STOP so a partial failure still attempts every CONT.
            stopped_pids="$stopped_pids $pid"
            echo "$pid $name" >> "$spotlight_record"
            "$kill_bin" -STOP "$pid"
        done
    else
        rc=$?
        [[ "$rc" -eq 1 ]] || { echo "Spotlight census failed for $name (exit $rc)" >&2; exit 2; }
    fi
done
"$python_bin" "$helper" run --deadline "$deadline" --runner-spec "$runner_spec" &
child_pid=$!
wait "$child_pid"
child_pid=""
