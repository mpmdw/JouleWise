#!/bin/zsh
# Non-claim ALIGN v4 R1 chain. A registered night plan pins these bytes and
# run_night invokes the chain only after its ordinary admission gates.
set -euo pipefail

restore_automatic() {
  sudo -n /usr/bin/pmset -c powermode 0
}
on_signal() {
  # Ignore (not default) further signals: a second TERM/INT must not kill this
  # shell or the restoring sudo, which inherits the ignored disposition.
  trap - EXIT
  trap '' HUP INT TERM
  restore_automatic || true
  exit 130
}
trap 'restore_automatic' EXIT
trap 'on_signal' HUP INT TERM

# Refuse before model/runtime work unless the exact two commands are visible
# and Automatic can actually be restored. Broader sudo access is not consumed.
SUDO_RULES="$(sudo -n -l)"
print -r -- "$SUDO_RULES" | /usr/bin/grep -F -- '/usr/bin/pmset -c powermode 0' >/dev/null
print -r -- "$SUDO_RULES" | /usr/bin/grep -F -- '/usr/bin/pmset -c powermode 2' >/dev/null
restore_automatic

: "${NIGHT_DIR:?run_night must supply NIGHT_DIR}"
: "${ALIGN_R1_RUNTIME:?WP15 runtime argv is required}"
REPO="${0:A:h:h:h}"
PY="${PY:-$REPO/.venv/bin/python}"
REGISTRATION="${ALIGN_R1_REGISTRATION:-$NIGHT_DIR/align-r1/r1_slots.json}"
: "${MEASUREMENT_ROOT:?run_night must supply stable MEASUREMENT_ROOT}"
POWER_MARKER="$MEASUREMENT_ROOT/.align-r1-high-power"

# A prior SIGKILL cannot run traps.  The persistent marker makes startup
# perform another restore before any runtime work and is cleared by the driver.
if [[ -e "$POWER_MARKER" ]]; then
  restore_automatic
fi

# ALIGN_R1_RUNTIME is an operator-pinned executable path, not shell text.
"$PY" -B "$REPO/scripts/align_r1_rehearsal.py" \
  --output "$NIGHT_DIR/align-r1" \
  --registration "$REGISTRATION" \
  --power-marker "$POWER_MARKER" \
  --runtime "$ALIGN_R1_RUNTIME"
