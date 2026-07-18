#!/bin/bash
# quiet_mac_prep.sh — prepare the Mac for a [QUIET-MAC] measurement window.
# Conservative by design: gracefully quits nonessential USER APPS only,
# reports (never kills) daemons/background load, and prints a quietness
# verdict. Nothing here deletes or force-kills anything.
set -u

KEEP_REGEX='^(Terminal|iTerm2|Finder|SystemUIServer|Dock|loginwindow|WindowServer|coreautha|universalaccessd)$'

echo "== JouleWise quiet-Mac prep $(date -u +%FT%TZ)"

# 1. Power state (no wall meter needed for P2-038/floors; AC is required).
pmset -g batt | head -2
pmset -g batt | grep -q "AC Power" || echo "WARN: not on AC power — plug in before the window."

# 2. Gracefully quit visible nonessential apps.
osascript -e '
tell application "System Events"
  set appList to name of every application process whose background only is false
end tell
return appList' 2>/dev/null | tr ',' '\n' | sed 's/^ *//' | while read -r app; do
  [ -z "$app" ] && continue
  if echo "$app" | grep -Eq "$KEEP_REGEX"; then
    echo "keep : $app"
  else
    echo "quit : $app"
    osascript -e "tell application \"$app\" to quit" >/dev/null 2>&1 &
  fi
done
sleep 5

# 3. Report residual CPU load (top consumers >1% — review, don't kill).
echo "== residual top CPU consumers:"
ps -Aro pcpu,comm | awk '$1>1.0' | head -12

# 4. Agent/tooling load check — these MUST be zero during a window.
echo "== agent-load check (must be empty):"
pgrep -fl "codex exec|codex mcp|claude" | grep -v "$$" || echo "  none"

# 5. Background churn worth knowing about (informational).
echo "== informational:"
pgrep -x mds_stores >/dev/null && echo "  Spotlight (mds_stores) present — fine if idle; check CPU above."
pgrep -x bird >/dev/null && echo "  iCloud sync (bird) present — fine if idle; avoid big file churn."
pgrep -x backupd >/dev/null && echo "  Time Machine backup RUNNING — consider waiting or: sudo tmutil disable"

# 6. powermetrics readiness (D-004 sudoers should make this passwordless).
if sudo -n /usr/bin/powermetrics -i 200 -n 1 >/dev/null 2>&1; then
  echo "OK: passwordless powermetrics works."
else
  echo "FAIL: sudo -n powermetrics refused — fix sudoers before the window."
fi

# 7. Snapshot the configured screensaver and current HID-idle evidence.
# Missing idleTime means the macOS default (20 minutes / 1200 s); no setting
# is written here.
echo "== display/screensaver pre-arm evidence:"
defaults -currentHost read com.apple.screensaver 2>/dev/null || echo "WARN: screensaver defaults probe unavailable."
SCREENSAVER_DELAY_S=$(defaults -currentHost read com.apple.screensaver idleTime 2>/dev/null || echo 1200)
case "$SCREENSAVER_DELAY_S" in
  ''|*[!0-9]*)
    echo "FAIL: unrecognized screensaver idleTime value; state is unknown."
    SCREENSAVER_DELAY_S=""
    ;;
esac
HID_IDLE_NS=$(ioreg -c IOHIDSystem 2>/dev/null | awk -F'= ' '/"HIDIdleTime"/{gsub(/[^0-9]/, "", $2); print $2; exit}')
if [ -n "$HID_IDLE_NS" ] && [ -n "$SCREENSAVER_DELAY_S" ]; then
  HID_IDLE_S=$((HID_IDLE_NS / 1000000000))
  echo "screensaver_delay_s=$SCREENSAVER_DELAY_S hid_idle_s=$HID_IDLE_S"
  if [ "$SCREENSAVER_DELAY_S" -gt 0 ] && [ "$HID_IDLE_S" -ge "$SCREENSAVER_DELAY_S" ]; then
    echo "FAIL: HID idle has reached the configured screensaver delay — dismiss it before arming."
  fi
else
  echo "FAIL: HIDIdleTime probe unavailable."
fi

# 8. Explicit transient arming. This requests display sleep only; it does not
# mutate displaysleep, screensaver, or any other persistent power setting.
echo "== arming display sleep in 5 seconds (move/input now to cancel manually):"
for remaining in 5 4 3 2 1; do
  echo "  $remaining"
  sleep 1
done
if pmset displaysleepnow; then
  sleep 2
  SYSTEMSTATE=$(pmset -g systemstate 2>/dev/null || true)
  echo "$SYSTEMSTATE"
  if echo "$SYSTEMSTATE" | grep -E "Current System Capabilities( are)?:.*Graphics" >/dev/null; then
    echo "FAIL: display verification still reports Graphics capability (any display awake)."
  elif echo "$SYSTEMSTATE" | grep -E "Current System Capabilities( are)?:" >/dev/null; then
    echo "OK: display verification reports all online displays asleep."
  else
    echo "FAIL: unrecognized pmset systemstate output; display state is unknown."
  fi

  # Re-probe screensaver/HID evidence after the display-sleep request. The
  # campaign performs its own equivalent verification before member 1.
  POST_SCREENSAVER_DELAY_S=$(defaults -currentHost read com.apple.screensaver idleTime 2>/dev/null || echo 1200)
  POST_HID_IDLE_NS=$(ioreg -c IOHIDSystem 2>/dev/null | awk -F'= ' '/"HIDIdleTime"/{gsub(/[^0-9]/, "", $2); print $2; exit}')
  case "$POST_SCREENSAVER_DELAY_S" in
    ''|*[!0-9]*) POST_SCREENSAVER_DELAY_S="" ;;
  esac
  if [ -n "$POST_HID_IDLE_NS" ] && [ -n "$POST_SCREENSAVER_DELAY_S" ]; then
    POST_HID_IDLE_S=$((POST_HID_IDLE_NS / 1000000000))
    echo "post_arm_screensaver_delay_s=$POST_SCREENSAVER_DELAY_S post_arm_hid_idle_s=$POST_HID_IDLE_S"
    if [ "$POST_SCREENSAVER_DELAY_S" -eq 0 ] || [ "$POST_HID_IDLE_S" -lt "$POST_SCREENSAVER_DELAY_S" ]; then
      echo "OK: post-arm evidence reports screensaver disengaged."
    else
      echo "FAIL: post-arm HID idle has reached the screensaver delay."
    fi
  else
    echo "FAIL: post-arm screensaver/HID probe unavailable; state is unknown."
  fi
else
  echo "FAIL: pmset displaysleepnow failed."
fi

echo "== verdict: campaign preflight must independently re-probe AC/external power, low-power mode, display sleep, screensaver state, and Nominal thermal pressure before member 1."
