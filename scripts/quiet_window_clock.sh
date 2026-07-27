#!/bin/bash
# Quiet-window clock stabilization (operator tool; requires administrator rights).
#
# WHY THIS EXISTS
#   On 2026-07-26 two window-C collection attempts failed because the machine's
#   wall clock was being slewed against the monotonic clock by more than the
#   governed 5 ms anchor ceiling (5.544 ms at ~+110 ppm, then 7.769 ms at
#   ~-158 ppm). Those rates match adjtime(2), which macOS network time
#   synchronisation uses to speed up or slow down the clock by a fraction of a
#   percent. Every environment gate passed on both failing members, so nothing
#   else caught it. Disabling automatic network time for the duration of a
#   measurement window removes the adjuster.
#
#   This is OPERATIONAL STABILIZATION, NOT A PROTOCOL WAIVER. The 5 ms anchor
#   predicate remains authoritative and is never relaxed. Nothing here touches
#   admission gates, --max-failures, or any measurement code.
#
# USAGE
#   scripts/quiet_window_clock.sh status    # show clock state and current offset
#   scripts/quiet_window_clock.sh disable   # BEFORE a window: verify, then pin
#   scripts/quiet_window_clock.sh enable    # AFTER the window: restore and resync
#
# SAFETY
#   `disable` REFUSES to pin the clock if it is currently off by more than
#   MAX_OFFSET_S. Pinning a wrong clock is worse than leaving sync on: the
#   window would carry a fixed timestamp error instead of a transient one.

set -uo pipefail

MAX_OFFSET_S="${MAX_OFFSET_S:-0.5}"   # refuse to pin if |offset| exceeds this
TIME_SERVER="${TIME_SERVER:-time.apple.com}"
SETTLE_S="${SETTLE_S:-180}"

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
warn() { printf '\033[33m%s\033[0m\n' "$*"; }
fail() { printf '\033[31m%s\033[0m\n' "$*" >&2; }

# Query the time server WITHOUT changing the clock. Prints a signed float, or
# nothing if the offset could not be determined.
measure_offset() {
  local out
  out="$(sntp "$TIME_SERVER" 2>/dev/null | tail -n 1)"
  # Expected tail shape: "+0.056823 +/- 0.013687 time.apple.com 17.253.x.x"
  printf '%s' "$out" | grep -oE '^[+-][0-9]+\.[0-9]+' || true
}

sync_state() {
  sudo systemsetup -getusingnetworktime 2>/dev/null \
    | sed -n 's/.*Network Time: *//p'
}

show_status() {
  local state offset
  state="$(sync_state)"
  bold "Network time synchronisation: ${state:-UNKNOWN}"

  offset="$(measure_offset)"
  if [ -n "$offset" ]; then
    bold "Measured offset vs ${TIME_SERVER}: ${offset} s"
    # 5 ms is the governed anchor ceiling; a standing offset near it is notable.
    if awk -v o="$offset" 'BEGIN{exit !(o<0.005 && o>-0.005)}'; then
      echo "  (within the 5 ms anchor ceiling)"
    fi
  else
    warn "Could not measure offset (no network, or ${TIME_SERVER} unreachable)."
  fi
}

do_disable() {
  local offset abs_ok
  bold "Step 1/3 — verifying the clock is correct before pinning it"

  offset="$(measure_offset)"
  if [ -z "$offset" ]; then
    fail "Cannot measure the clock offset (no network, or ${TIME_SERVER} unreachable)."
    fail "REFUSING to pin an unverified clock. Restore connectivity and retry,"
    fail "or set MAX_OFFSET_S deliberately if you have another way to trust it."
    exit 1
  fi

  abs_ok="$(awk -v o="$offset" -v m="$MAX_OFFSET_S" \
    'BEGIN{a=(o<0)?-o:o; print (a<=m)?"yes":"no"}')"
  echo "  offset vs ${TIME_SERVER}: ${offset} s   (limit ${MAX_OFFSET_S} s)"

  if [ "$abs_ok" != "yes" ]; then
    fail ""
    fail "REFUSING: the clock is off by more than ${MAX_OFFSET_S} s."
    fail "Pinning it now would bake that error into the whole window."
    fail "Fix first:  scripts/quiet_window_clock.sh enable"
    fail "then wait a minute for it to converge and run 'disable' again."
    exit 1
  fi
  echo "  clock is good — safe to pin"

  bold ""
  bold "Step 2/3 — disabling automatic network time"
  sudo systemsetup -setusingnetworktime off >/dev/null 2>&1
  local state
  state="$(sync_state)"
  if [ "$state" = "On" ]; then
    fail "FAILED: network time is still On. Do not start the window."
    exit 1
  fi
  echo "  network time synchronisation: ${state:-Off}"

  bold ""
  bold "Step 3/3 — settle before collecting"
  cat <<EOF
  Wait ${SETTLE_S}s before launching, per the run-book settle rule.
  The chain also settles ${SETTLE_S}s on its own before the pre-calibration,
  so launching immediately is acceptable if you would rather not wait twice.

$(bold "Ready. Launch window C:")
  caffeinate -is /bin/zsh /Users/edr/JouleWise-window-plans/window_c_20260726/window-chain.zsh \\
                          /Users/edr/JouleWise-window-plans/window_c_20260726

$(bold "Then window D:")
  caffeinate -is /bin/zsh /Users/edr/JouleWise-window-plans/window_d_20260726/window-chain.zsh \\
                          /Users/edr/JouleWise-window-plans/window_d_20260726

$(warn "AFTER the last window completes, restore normal timekeeping:")
  scripts/quiet_window_clock.sh enable
EOF
}

do_enable() {
  bold "Re-enabling automatic network time"
  sudo systemsetup -setusingnetworktime on >/dev/null 2>&1
  sleep 2
  local state
  state="$(sync_state)"
  echo "  network time synchronisation: ${state:-UNKNOWN}"
  if [ "$state" != "On" ]; then
    fail "WARNING: expected On. Check System Settings > General > Date & Time."
    exit 1
  fi
  echo ""
  show_status
  echo ""
  echo "If the offset is still large, give it a minute to converge and re-check."
}

case "${1:-status}" in
  status)  show_status ;;
  disable) do_disable ;;
  enable)  do_enable ;;
  *)
    fail "usage: $0 [status|disable|enable]"
    exit 2
    ;;
esac
