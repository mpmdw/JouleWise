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

echo "== verdict: review the residual list above; if only system daemons near-idle remain and powermetrics is OK, the machine is quiet enough for P2-038 shakedown."
