#!/bin/sh
# Install, or with --uninstall remove, the RL-127 pipeline watcher LaunchAgent.
# --dry-run prints the rendered plist, the wrapper and the commands, and changes nothing.
# The lead installs after review; persistent services are not loaded by builders.
set -eu
LABEL=com.joulewise.pipeline-watch
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
LOG="$HOME/Library/Logs/JouleWise/pipeline-watch.log"
STATEDIR="$HOME/Library/Application Support/JouleWise/pipeline-watch"
WRAPPER="$STATEDIR/pipeline-watch-run.sh"
LAUNCHCTL=${JW_LAUNCHCTL:-launchctl}
GH=${JW_GH:-gh}
DOMAIN="gui/$(id -u)"

run() {
  if [ "$DRY" = 1 ]; then echo "+ $*"; else "$@"; fi
}

if [ "$MODE" = uninstall ]; then
  run "$LAUNCHCTL" bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  run rm -f "$PLIST" "$WRAPPER"
  [ "$DRY" = 1 ] || echo "uninstalled $LABEL (idempotent; state and ledger kept)"
  exit 0
fi

case "$PYTHON" in /*) ;; *) echo "python3.13 not found; set JW_AIR_PYTHON" >&2; exit 2 ;; esac
for v in "$REPO" "$PYTHON" "$LOG" "$STATEDIR"; do
  case "$v" in *[\&\<\>\"@#\'\\]*) echo "unsupported character in path: $v" >&2; exit 2 ;; esac
done
[ -f "$REPO/scripts/pipeline_watch.py" ] || { echo "not a JouleWise checkout: $REPO" >&2; exit 2; }
render() {
  sed -e "s#@REPO@#$REPO#g" -e "s#@PYTHON@#$PYTHON#g" -e "s#@LOG@#$LOG#g" \
    -e "s#@STATEDIR@#$STATEDIR#g" "$REPO/scripts/air/$1"
}
RENDERED=$(render "$LABEL.plist.template")
RUNNER=$(render pipeline-watch-run.sh.template)

if [ "$DRY" = 1 ]; then
  printf '%s\n' "$RENDERED"
  printf '# %s:\n%s\n' "$WRAPPER" "$RUNNER"
  echo "+ mkdir -p /Volumes/JW-EXT/ledger/profiles"
  echo "+ $GH label create pipeline-alarm --repo mpmdw/JouleWise --force"
  echo "+ $LAUNCHCTL bootout $DOMAIN/$LABEL"
else
  mkdir -p "$AGENTS" "$(dirname "$LOG")" "$STATEDIR" /Volumes/JW-EXT/ledger/profiles
  "$GH" label create pipeline-alarm --repo mpmdw/JouleWise --color D93F0B \
    --description "Non-agent pipeline watcher alarm (RL-127)" --force >/dev/null 2>&1 \
    || echo "warning: could not create the pipeline-alarm label; issue alarms will fail until it exists" >&2
  "$LAUNCHCTL" bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  i=0
  while [ $i -lt 10 ] && "$LAUNCHCTL" print "$DOMAIN/$LABEL" >/dev/null 2>&1; do sleep 1; i=$((i+1)); done
  printf '%s\n' "$RUNNER" > "$WRAPPER"
  chmod 755 "$WRAPPER"
  printf '%s\n' "$RENDERED" > "$PLIST"
fi
run "$LAUNCHCTL" bootstrap "$DOMAIN" "$PLIST"
[ "$DRY" = 1 ] || echo "installed $PLIST; log: $LOG; alarms: /Volumes/JW-EXT/ledger/alarms.jsonl"
