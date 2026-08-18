#!/bin/bash
# ED-QUALIFICATION step 2: short production-supervised sampler lifecycle check.

set -euo pipefail

ORIGINAL_ARGS=("$@")
DRY_RUN=0
NO_SUDO=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --no-sudo) NO_SUDO=1 ;;
    *) echo "usage: $0 [--dry-run] [--no-sudo]" >&2; exit 2 ;;
  esac
  shift
done

if [ "$NO_SUDO" -eq 1 ] && [ "$DRY_RUN" -ne 1 ]; then
  echo "REFUSE: --no-sudo is a dry-run inspection aid only; a live sampler check requires sudo -n." >&2
  exit 2
fi

SESSION_ROOT=/tmp/ed-session
mkdir -p "$SESSION_ROOT"
STAMP="${ED_SESSION_STAMP:-$(date -u '+%Y%m%dT%H%M%SZ')}"
LOG="$SESSION_ROOT/sampler-checklist-$STAMP.log"
CAPTURE="$SESSION_ROOT/sampler-checklist-$STAMP.plist"
if [ "${ED_SESSION_TEE_ACTIVE:-0}" -ne 1 ]; then
  set +e
  ED_SESSION_TEE_ACTIVE=1 ED_SESSION_STAMP="$STAMP" \
    /bin/bash "$0" ${ORIGINAL_ARGS[@]+"${ORIGINAL_ARGS[@]}"} 2>&1 | /usr/bin/tee -a "$LOG"
  status="${PIPESTATUS[0]}"
  exit "$status"
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)"
PYTHON="$REPO_ROOT/.venv/bin/python"
[ -x "$PYTHON" ] || PYTHON=python3

require_empty_sampler_census() {
  local output rc
  set +e
  output="$(/usr/bin/pgrep -fl '[p]owermetrics' 2>&1)"
  rc=$?
  set -e
  case "$rc" in
    0) echo "$output"; echo "REFUSE: a powermetrics process already exists." >&2; return 1 ;;
    1) echo "PASS: no powermetrics process found."; return 0 ;;
    *) echo "REFUSE: powermetrics census is unavailable: $output" >&2; return 1 ;;
  esac
}

echo "ED-QUALIFICATION sampler checklist"
echo "evidence_log=$LOG"
echo "capture=$CAPTURE"

echo "1. Confirm the intended command and evidence directory."
echo "/usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 5 --samplers battery,cpu_power,gpu_power,ane_power,thermal --format plist -o $CAPTURE"

echo "2. Confirm non-interactive sudo before any live sampler starts."
if [ "$DRY_RUN" -eq 1 ]; then
  if [ "$NO_SUDO" -eq 1 ]; then
    echo "DRY-RUN: sudo probe skipped; --no-sudo requested."
  else
    echo "DRY-RUN: sudo probe skipped."
  fi
else
  if [ ! -x /usr/bin/sudo ]; then
    echo "REFUSE: /usr/bin/sudo is missing; install/restore sudo before qualification." >&2
    exit 1
  fi
  if ! /usr/bin/sudo -n /usr/bin/true; then
    echo "REFUSE: sudo -n is unavailable. Fix the governed passwordless powermetrics sudoers entry; do not enter a password inside this script." >&2
    exit 1
  fi
  echo "PASS: sudo -n authorization is available."
fi

echo "3. Census pre-existing sampler processes."
if ! require_empty_sampler_census; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: census refusal recorded without starting a sampler."
  else
    echo "Stop and identify the sampler owner or restore the process census before retrying." >&2
    exit 1
  fi
fi

echo "4. Run a five-sample capture under the production sampler-lifetime supervisor."
if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN: production supervisor import and live capture skipped."
else
  printf "Press Return to start the supervised five-sample check: "
  IFS= read -r _confirmation
  cd "$REPO_ROOT"
  "$PYTHON" - "$CAPTURE" <<'PY'
import subprocess
import sys
from pathlib import Path

from joulewise.adapters.powermetrics import parse_powermetrics_records
from scripts.validate_powermetrics_fiducial import _sampler_lifetime

capture = Path(sys.argv[1])
command = [
    "/usr/bin/sudo", "-n", "/usr/bin/powermetrics",
    "-b", "0", "-i", "1000", "-n", "5",
    "--samplers", "battery,cpu_power,gpu_power,ane_power,thermal",
    "--format", "plist", "-o", str(capture),
]
with _sampler_lifetime(command) as process:
    try:
        return_code = process.wait(timeout=20)
    except subprocess.TimeoutExpired as exc:
        raise SystemExit("REFUSE: supervised sampler did not finish within 20 seconds") from exc
if return_code != 0:
    raise SystemExit(f"REFUSE: powermetrics exited {return_code}")
records = parse_powermetrics_records(capture.read_bytes())
if len(records) < 2:
    raise SystemExit(f"REFUSE: expected at least 2 complete records, observed {len(records)}")
intervals_s = [record.elapsed_ns / 1_000_000_000 for record in records]
print(f"records={len(records)}")
print("cadence_s=" + ",".join(f"{value:.6f}" for value in intervals_s))
print(f"cadence_mean_s={sum(intervals_s) / len(intervals_s):.6f}")
PY
fi

echo "5. Verify teardown left no orphaned sampler process."
if ! require_empty_sampler_census; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: post-teardown census refusal recorded without starting a sampler."
  else
    echo "REFUSE: teardown is not qualified until an empty census is observed." >&2
    exit 1
  fi
fi

echo "6. Record the result."
if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN COMPLETE: command, refusal gates, teardown census, and cadence parser are staged."
else
  echo "PASS: supervised sampler lifecycle, orphan census, and cadence record completed."
fi
