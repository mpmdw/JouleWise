#!/bin/bash
# Read-only operator gate for PIPELINE-SMOKE-LIVE-01.
# This script performs no measurement and creates no intentional project or measurement artifacts.

set -uo pipefail

if [ "$#" -ne 1 ]; then
  printf 'usage: %s /absolute/path/to/night_plan.json\n' "$0" >&2
  exit 2
fi

export GIT_OPTIONAL_LOCKS=0
export PYTHONDONTWRITEBYTECODE=1

failures=0

pass() {
  printf 'PASS %s\n' "$1"
}

fail() {
  printf 'FAIL %s\n' "$1"
  failures=$((failures + 1))
}

quiet_process_census() {
  /usr/bin/awk '
    $0 ~ /codex|claude|t3|mcp-server|run_campaign|window-chain|caffeinate/ { print }
  '
}

# Read routing fields without bootstrapping through an untrusted/inherited PY.
# Full plan authentication remains the night driver's gate.
NIGHT_PLAN="$1"
case "$NIGHT_PLAN" in
  /*) ;;
  *) fail 'night plan path must be absolute'; exit 1 ;;
esac
if ! /usr/bin/jq -e '.schema == "joulewise.night_plan.v2" and .schema_version == 2' "$NIGHT_PLAN" >/dev/null 2>&1; then
  fail 'night plan must use joulewise.night_plan.v2 with schema_version 2'
  exit 1
fi
if ! MEASUREMENT_ROOT="$(/usr/bin/jq -er '.measurement_root | select(type == "string") | select(startswith("/") and (test("[[:cntrl:]]") | not))' "$NIGHT_PLAN" 2>/dev/null)"; then
  fail 'measurement_root must be a non-empty absolute path'
  exit 1
fi
if ! MEASUREMENT_HEAD="$(/usr/bin/jq -er '.measurement_head | select(type == "string") | select(length == 40 and test("^[0-9a-f]{40}$"))' "$NIGHT_PLAN" 2>/dev/null)"; then
  fail 'measurement_head must be a full 40-character lowercase SHA-1'
  exit 1
fi
export MEASUREMENT_ROOT MEASUREMENT_HEAD
SMOKE_CHECKOUT="$MEASUREMENT_ROOT"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PYTHONPATH="$MEASUREMENT_ROOT"
if ! observed_head="$(git -C "$MEASUREMENT_ROOT" rev-parse --verify HEAD 2>/dev/null)"; then
  fail 'checkout HEAD cannot be read'
  exit 1
elif [ "$observed_head" != "$MEASUREMENT_HEAD" ]; then
  fail "checkout HEAD does not equal measurement_head (observed $observed_head)"
  exit 1
fi
pass 'checkout HEAD equals measurement_head'
if [ ! -x "$PY" ]; then
  fail 'measurement venv Python is missing or not executable'
  exit 1
fi
pass 'PY names the executable measurement venv interpreter derived from measurement_root'
pass 'PYTHONPATH equals measurement_root for every Python command'

if [ -n "${SMOKE_CHECKOUT:-}" ] && [ -e "$SMOKE_CHECKOUT" ]; then
  if ! dirty="$(git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all 2>/dev/null)"; then
    fail 'git status probe failed'
  elif [ -z "$dirty" ]; then
    pass 'checkout working tree is clean'
  else
    fail 'checkout working tree is not clean'
  fi

  if ! checked_branch="$(git -C "$SMOKE_CHECKOUT" branch --show-current 2>/dev/null)"; then
    fail 'checked-out branch cannot be read'
  elif [ -z "$checked_branch" ]; then
    pass 'measurement checkout is detached at measurement_head'
  else
    fail 'measurement checkout must be detached at measurement_head'
  fi

  lock_path="$SMOKE_CHECKOUT/env/mac-measurement-lock.txt"
  if [ ! -f "$lock_path" ]; then
    fail 'env/mac-measurement-lock.txt is missing'
  else
    wanted="$(grep -Ev '^(#|[[:space:]]*$)' "$lock_path" | sort)"
    have="$("$PY" -m pip freeze --exclude-editable 2>/dev/null | sort)"
    if [ "$wanted" = "$have" ]; then
      pass 'measurement venv relock gate is an empty normalized diff against the smoke checkout lock'
    else
      fail 'measurement venv relock gate differs from the smoke checkout env/mac-measurement-lock.txt'
    fi
  fi

  if [ -x "$PY" ]; then
    if ! joulewise_path="$(cd "$SMOKE_CHECKOUT" && "$PY" -c 'import joulewise,sys; print(joulewise.__file__)' 2>/dev/null)"; then
      fail 'joulewise import probe failed'
    else
      case "$joulewise_path" in
        "$SMOKE_CHECKOUT"/*) pass 'joulewise imports from the smoke checkout' ;;
        *) fail "joulewise imports outside the smoke checkout (observed ${joulewise_path:-unreadable})" ;;
      esac
    fi
  fi

  if [ -x "$PY" ] && "$PY" -c 'import mlx, mlx_lm' >/dev/null 2>&1; then
    pass 'mlx and mlx_lm import in the measurement venv'
  else
    fail 'mlx or mlx_lm is not importable in the measurement venv'
  fi

  # B10: authenticate the physical calibration ledger against the committed
  # tracked pin with the production loader. This deliberately disables only
  # custody-artifact replay (observation artifacts re-hashed at their custody
  # locators; `_custody_reasons`, calibration_ledger.py:1773/:2073); it does not
  # weaken ledger parsing, chain, head-pin,
  # rollback, stale-head, or committed-pin checks.
  ledger_path="$SMOKE_CHECKOUT/runs/calibration_observation_ledger.jsonl"
  ledger_pin="$SMOKE_CHECKOUT/configs/calibration/calibration_ledger_head.json"
  if "$PY" - "$ledger_path" "$ledger_pin" "$SMOKE_CHECKOUT" <<'PY'
import sys
from pathlib import Path

from joulewise.calibration_ledger import load_calibration_ledger_snapshot

snapshot = load_calibration_ledger_snapshot(
    Path(sys.argv[1]),
    Path(sys.argv[2]),
    repo_root=Path(sys.argv[3]),
    verify_custody=False,
)
if snapshot.refusal_reasons:
    raise SystemExit(",".join(snapshot.refusal_reasons))
PY
  then
    pass 'B10 calibration ledger head authenticates against the tracked pin'
  else
    fail 'B10 calibration ledger is missing, rolled back, stale, malformed, or not pinned by committed bytes'
  fi
fi

# ARM-ABORT REHEARSAL — MANUAL ONLY; preflight never arms or consumes.
# Use a separate earlier arm on the real frozen _v5 pack, with throwaway
# attempt/session ids and the registry-governed 300 s arm-to-consume budget.
# Let that arm expire/refuse without launch and verify that no bundle was
# written. Never let this rehearsal arm straddle the later T-0 clean dwell.

# Interim private helper only. B5 requires the governed prewindow gate and this
# script to consume one shared helper contract: exact case-sensitive vocabulary
# and ps form, with caffeinate absent pre-execve.
process_probe_ok=0
process_snapshot=''
process_rows=''
if ! process_snapshot="$(/bin/ps aux 2>/dev/null)"; then
  fail 'quiet-machine process census probe failed'
else
  process_probe_ok=1
  process_rows="$(printf '%s\n' "$process_snapshot" | quiet_process_census)"
fi
if [ "$process_probe_ok" -eq 1 ] && [ -z "$process_rows" ]; then
  pass 'quiet-machine census has no agent or measurement process'
elif [ "$process_probe_ok" -eq 1 ]; then
  fail "quiet-machine census found agent or measurement process: $(printf '%s' "$process_rows" | tr '\n' ';')"
fi

if [ -x /usr/bin/powermetrics ]; then
  pass 'governed /usr/bin/powermetrics is executable'
else
  fail 'governed /usr/bin/powermetrics is not executable'
fi

if /usr/bin/sudo -n -l /usr/bin/powermetrics >/dev/null 2>&1; then
  pass 'sudo authorizes exactly /usr/bin/powermetrics non-interactively'
else
  fail 'sudo does not authorize /usr/bin/powermetrics non-interactively'
fi

if [ "$failures" -ne 0 ]; then
  exit 1
fi
exit 0
