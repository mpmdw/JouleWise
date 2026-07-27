#!/bin/bash
# Pre-window readiness gate (operator tool; no admin required).
#
# WHY THIS EXISTS
#   On 2026-07-27 a measurement window failed on its FIRST member, roughly five
#   minutes after launch, because Apple's XProtectRemediator malware scanner was
#   running at 94% CPU. The instrument's CPU-admission gate correctly refused the
#   member -- but by then the window had been launched, the display slept, and the
#   operator had walked away. The failure cost the launch and required a manual
#   diagnose-wait-relaunch cycle.
#
#   Idle-triggered macOS daemons fire in roughly the first ten minutes of a quiet
#   window. That is exactly when a window launches. This script checks for them
#   BEFORE launch, and can wait for them to finish.
#
#   This is a READINESS check, not a measurement gate. It never waives, relaxes,
#   or substitutes for the campaign's own environment and CPU admission gates --
#   those remain authoritative and unchanged. It only avoids launching into a
#   condition those gates will refuse anyway.
#
# USAGE
#   scripts/prewindow_check.sh                 # check once, report, exit 0/1
#   scripts/prewindow_check.sh --wait          # wait until ready (default 45 min cap)
#   scripts/prewindow_check.sh --wait --timeout-min 90
#   scripts/prewindow_check.sh --window c      # also verify that window's runs roots are clear

set -uo pipefail

WAIT=0
TIMEOUT_MIN=45
WINDOW=""
CPU_LIMIT="${CPU_LIMIT:-5.0}"        # percent, per contaminating process
LOAD_LIMIT="${LOAD_LIMIT:-2.0}"      # 1-minute load average
SETTLE_CHECKS=3                      # consecutive clean checks required
INTERVAL_S=30

while [ $# -gt 0 ]; do
  case "$1" in
    --wait) WAIT=1; shift ;;
    --timeout-min) TIMEOUT_MIN="$2"; shift 2 ;;
    --window) WINDOW="$2"; shift 2 ;;
    *) echo "usage: $0 [--wait] [--timeout-min N] [--window LETTER]" >&2; exit 2 ;;
  esac
done

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$*"; }
bad()  { printf '  \033[31mBLOCK\033[0m %s\n' "$*"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$*"; }

# Daemons observed or documented to contaminate a quiet window. XProtect is the
# one with a confirmed incident; the rest are the same class and cheap to include.
CONTAMINANTS='XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd'

check_once() {
  local blocked=0

  # 1. Contaminating daemons, by actual CPU use rather than mere presence.
  local busy
  busy="$(ps aux | grep -iE "$CONTAMINANTS" | grep -v grep \
          | awk -v lim="$CPU_LIMIT" '$3+0 > lim {printf "%s(%.1f%%) ", $11, $3}')"
  if [ -n "$busy" ]; then
    bad "background daemon active: $busy"
    blocked=1
  else
    ok "no contaminating daemon above ${CPU_LIMIT}% CPU"
  fi

  # 2. Overall load. A high load average with no named culprit is still a reason
  #    not to launch; the campaign's CPU admission would likely refuse.
  local load1
  load1="$(uptime | sed -n 's/.*load averages*: *\([0-9.]*\).*/\1/p')"
  if awk -v l="$load1" -v m="$LOAD_LIMIT" 'BEGIN{exit !(l+0 > m)}'; then
    bad "1-minute load average ${load1} exceeds ${LOAD_LIMIT}"
    blocked=1
  else
    ok "load average ${load1}"
  fi

  # 3. Power. The production policy requires AC with an external supply.
  if pmset -g batt 2>/dev/null | head -1 | grep -q "AC Power"; then
    ok "on AC power"
  else
    bad "not on AC power"
    blocked=1
  fi

  # 4. Clock pinned. Measurement windows run with automatic network time
  #    disabled (see scripts/quiet_window_clock.sh); a live adjuster caused two
  #    window failures on 2026-07-26.
  local nt
  nt="$(sudo -n systemsetup -getusingnetworktime 2>/dev/null | sed -n 's/.*Network Time: *//p')"
  if [ -z "$nt" ]; then
    warn "cannot read network-time state without admin; confirm the clock is pinned"
  elif [ "$nt" = "Off" ]; then
    ok "automatic network time disabled (clock pinned)"
  else
    bad "automatic network time is On -- run scripts/quiet_window_clock.sh disable"
    blocked=1
  fi

  # 5. Target window's runs roots must be absent. An occupied slot makes the
  #    chain fail late rather than early.
  if [ -n "$WINDOW" ]; then
    local hits
    hits="$(ls -d /Users/edr/code/JouleWise/runs_window_${WINDOW}_* 2>/dev/null | tr '\n' ' ')"
    if [ -n "$hits" ]; then
      bad "runs roots already exist for window ${WINDOW}: $hits"
      blocked=1
    else
      ok "runs roots clear for window ${WINDOW}"
    fi
  fi

  # 6. Disk headroom. A window writes a few GB; running out mid-campaign loses it.
  local avail_gb
  avail_gb="$(df -g /Users/edr/code/JouleWise | awk 'NR==2 {print $4}')"
  if [ "${avail_gb:-0}" -lt 20 ]; then
    bad "only ${avail_gb} GB free; a window needs several GB with headroom"
    blocked=1
  else
    ok "${avail_gb} GB free"
  fi

  # 7. No agent or measurement process already running.
  local procs
  procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"
  if [ "$procs" -gt 0 ]; then
    bad "$procs agent/measurement process(es) already running"
    blocked=1
  else
    ok "no agent or measurement process running"
  fi

  return $blocked
}

bold "Pre-window readiness check — $(date '+%Y-%m-%d %H:%M:%S %Z')"
if [ "$WAIT" -eq 0 ]; then
  if check_once; then
    bold ""; bold "READY."
    exit 0
  else
    bold ""; bold "NOT READY. Fix the BLOCK lines above, or re-run with --wait."
    exit 1
  fi
fi

# --wait: require SETTLE_CHECKS consecutive clean passes, so a daemon that is
# briefly between bursts does not read as finished.
deadline=$(( $(date +%s) + TIMEOUT_MIN * 60 ))
clean=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  if check_once; then
    clean=$((clean + 1))
    bold "  clean check ${clean}/${SETTLE_CHECKS}"
    if [ "$clean" -ge "$SETTLE_CHECKS" ]; then
      bold ""; bold "READY after $(( ($(date +%s) - (deadline - TIMEOUT_MIN * 60)) / 60 )) min."
      exit 0
    fi
  else
    clean=0
    bold "  not ready; re-checking in ${INTERVAL_S}s"
  fi
  sleep "$INTERVAL_S"
done

bold ""; bold "TIMED OUT after ${TIMEOUT_MIN} min without ${SETTLE_CHECKS} consecutive clean checks."
bold "Do not launch. Investigate what is keeping the machine busy."
exit 1
