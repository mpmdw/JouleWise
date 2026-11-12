#!/bin/sh
# Install, or with --uninstall remove, the Air results + main-CI LaunchAgent.
# --dry-run prints the rendered plist and the commands and changes nothing.
# Requires Ed's approval to run for real (persistent service).
set -eu
LABEL=com.joulewise.air-watch
MODE=install
DRY=0
for arg in "$@"; do
  case "$arg" in
    --uninstall) MODE=uninstall ;;
    --dry-run) DRY=1 ;;
    *) echo "usage: $0 [--uninstall] [--dry-run]" >&2; exit 2 ;;
  esac
done
REPO=${JW_AIR_REPO:-$(cd "$(dirname "$0")/../.." && pwd -P)}
PYTHON=${JW_AIR_PYTHON:-$(command -v python3.13 || true)}
AGENTS="$HOME/Library/LaunchAgents"
PLIST="$AGENTS/$LABEL.plist"
LOG="$HOME/Library/Logs/JouleWise/air-watch.log"
STATEDIR="$HOME/Library/Application Support/JouleWise/air-watch"
WRAPPER="$STATEDIR/air-watch-run.sh"
LAUNCHCTL=${JW_LAUNCHCTL:-launchctl}
DOMAIN="gui/$(id -u)"

run() {
  if [ "$DRY" = 1 ]; then echo "+ $*"; else "$@"; fi
}

if [ "$MODE" = uninstall ]; then
  run "$LAUNCHCTL" bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  run rm -f "$PLIST" "$WRAPPER"
  [ "$DRY" = 1 ] || echo "uninstalled $LABEL (idempotent)"
  exit 0
fi

case "$PYTHON" in /*) ;; *) echo "python3.13 not found; set JW_AIR_PYTHON" >&2; exit 2 ;; esac
for v in "$REPO" "$PYTHON" "$LOG" "$STATEDIR"; do
  case "$v" in *[\&\<\>\"@#\'\\]*) echo "unsupported character in path: $v" >&2; exit 2 ;; esac
done
[ -f "$REPO/scripts/air/air_watch_agent.py" ] || { echo "not a JouleWise checkout: $REPO" >&2; exit 2; }
render() {
  sed -e "s#@REPO@#$REPO#g" -e "s#@PYTHON@#$PYTHON#g" -e "s#@LOG@#$LOG#g" \
    -e "s#@STATEDIR@#$STATEDIR#g" "$REPO/scripts/air/$1"
}
RENDERED=$(render "$LABEL.plist.template")
RUNNER=$(render air-watch-run.sh.template)

if [ "$DRY" = 1 ]; then
  printf '%s\n' "$RENDERED"
  printf '# %s:\n%s\n' "$WRAPPER" "$RUNNER"
  echo "+ $LAUNCHCTL bootout $DOMAIN/$LABEL"
else
  mkdir -p "$AGENTS" "$(dirname "$LOG")" "$STATEDIR"
  "$LAUNCHCTL" bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  i=0
  while [ $i -lt 10 ] && "$LAUNCHCTL" print "$DOMAIN/$LABEL" >/dev/null 2>&1; do sleep 1; i=$((i+1)); done
  printf '%s\n' "$RUNNER" > "$WRAPPER"
  chmod 755 "$WRAPPER"
  printf '%s\n' "$RENDERED" > "$PLIST"
fi
run "$LAUNCHCTL" bootstrap "$DOMAIN" "$PLIST"
[ "$DRY" = 1 ] || echo "installed $PLIST; log: $LOG"
