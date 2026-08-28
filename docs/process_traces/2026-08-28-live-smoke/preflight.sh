#!/bin/bash
# Read-only operator gate for PIPELINE-SMOKE-LIVE-01.
# This script performs no measurement and creates no intentional project or measurement artifacts.

set -uo pipefail

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

if [ -z "${REVIEWED_HEAD:-}" ]; then
  fail 'REVIEWED_HEAD is required'
elif ! [[ "$REVIEWED_HEAD" =~ ^[0-9a-f]{40}$ ]]; then
  fail 'REVIEWED_HEAD must be a full 40-character lowercase SHA-1'
else
  pass 'REVIEWED_HEAD is present and well formed'
fi

SMOKE_ROOT=/Users/edr/JouleWise-smoke
source_python='/Users/edr/code/JouleWise/.venv/bin/python'
if [ "${PY:-}" != "$source_python" ]; then
  fail 'PY must name the exact source venv interpreter'
elif [ ! -x "$source_python" ]; then
  fail 'source venv Python is missing or not executable'
else
  pass 'PY names the exact executable source venv interpreter'
fi

if [ "${PYTHONPATH:-}" != "${SMOKE_CHECKOUT:-}" ] || [ -z "${PYTHONPATH:-}" ]; then
  fail 'PYTHONPATH must equal SMOKE_CHECKOUT for every Python command'
else
  pass 'PYTHONPATH equals SMOKE_CHECKOUT for every Python command'
fi

if [ -z "${SMOKE_CHECKOUT:-}" ]; then
  fail 'SMOKE_CHECKOUT is required'
elif [ "$SMOKE_CHECKOUT" != "$SMOKE_ROOT/checkout" ]; then
  fail 'SMOKE_CHECKOUT must be the smoke-dedicated checkout below the quarantine root'
elif [ ! -d "$SMOKE_CHECKOUT/.git" ] && [ ! -f "$SMOKE_CHECKOUT/.git" ]; then
  fail 'SMOKE_CHECKOUT is not a Git checkout'
else
  pass 'SMOKE_CHECKOUT is a Git checkout'
fi

if [ -n "${SMOKE_CHECKOUT:-}" ] && [ -e "$SMOKE_CHECKOUT" ]; then
  if ! observed_head="$(git -C "$SMOKE_CHECKOUT" rev-parse --verify HEAD 2>/dev/null)"; then
    fail 'checkout HEAD cannot be read'
    observed_head=''
  elif [ -n "${REVIEWED_HEAD:-}" ] && [ "$observed_head" = "$REVIEWED_HEAD" ]; then
    pass 'checkout HEAD equals REVIEWED_HEAD'
  else
    fail "checkout HEAD does not equal REVIEWED_HEAD (observed ${observed_head:-unreadable})"
  fi

  if ! dirty="$(git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all 2>/dev/null)"; then
    fail 'git status probe failed'
  elif [ -z "$dirty" ]; then
    pass 'checkout working tree is clean'
  else
    fail 'checkout working tree is not clean'
  fi

  if ! branch_count="$(git -C "$SMOKE_CHECKOUT" branch --list 2>/dev/null | /usr/bin/wc -l | tr -d ' ')"; then
    fail 'local-branch census failed'
  elif ! checked_branch="$(git -C "$SMOKE_CHECKOUT" branch --show-current 2>/dev/null)"; then
    fail 'checked-out branch cannot be read'
  elif ! only_branch="$(git -C "$SMOKE_CHECKOUT" branch --format='%(refname:short)' 2>/dev/null)"; then
    fail 'local-branch roster cannot be read'
  elif [ "$branch_count" = 1 ] && [ -n "$checked_branch" ] && [ "$checked_branch" = "$only_branch" ]; then
    pass 'checkout has exactly one local branch and it is checked out'
  else
    fail 'checkout must have exactly one local branch and it must be checked out'
  fi

  lock_path="$SMOKE_CHECKOUT/env/mac-measurement-lock.txt"
  if [ ! -f "$lock_path" ]; then
    fail 'env/mac-measurement-lock.txt is missing'
  else
    wanted="$(grep -Ev '^(#|[[:space:]]*$)' "$lock_path" | sort)"
    have="$($source_python -m pip freeze --exclude-editable 2>/dev/null | sort)"
    if [ "$wanted" = "$have" ]; then
      pass 'source venv relock gate is an empty normalized diff against the smoke checkout lock'
    else
      fail 'source venv relock gate differs from the smoke checkout env/mac-measurement-lock.txt'
    fi
  fi

  if [ -x "$source_python" ]; then
    if ! joulewise_path="$(cd "$SMOKE_CHECKOUT" && "$source_python" -c 'import joulewise,sys; print(joulewise.__file__)' 2>/dev/null)"; then
      fail 'joulewise import probe failed'
    else
      case "$joulewise_path" in
        "$SMOKE_CHECKOUT"/*) pass 'joulewise imports from the smoke checkout' ;;
        *) fail "joulewise imports outside the smoke checkout (observed ${joulewise_path:-unreadable})" ;;
      esac
    fi
  fi

  if [ -x "$source_python" ] && "$source_python" -c 'import mlx, mlx_lm' >/dev/null 2>&1; then
    pass 'mlx and mlx_lm import in the source venv'
  else
    fail 'mlx or mlx_lm is not importable in the source venv'
  fi

  # B10: authenticate the physical calibration ledger against the committed
  # tracked pin with the production loader. This deliberately disables only
  # custody-store replay; it does not weaken ledger parsing, chain, head-pin,
  # rollback, stale-head, or committed-pin checks.
  ledger_path="$SMOKE_CHECKOUT/runs/calibration_observation_ledger.jsonl"
  ledger_pin="$SMOKE_CHECKOUT/configs/calibration/calibration_ledger_head.json"
  if "$source_python" - "$ledger_path" "$ledger_pin" "$SMOKE_CHECKOUT" <<'PY'
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
# Use a separate earlier arm on the real frozen _v4 pack, with throwaway
# attempt/session ids and the registry-governed 300 s arm-to-consume budget.
# Let that arm expire/refuse without launch and verify that no bundle was
# written. Never let this rehearsal arm straddle the later T-0 clean dwell.

if [ ! -e "$SMOKE_ROOT" ]; then
  pass 'quarantine root does not exist (fresh pre-provisioning state)'
elif ! smoke_entries="$(/usr/bin/find "$SMOKE_ROOT" -mindepth 1 -maxdepth 1 -print 2>/dev/null)"; then
  fail 'quarantine-root census failed'
elif [ "$smoke_entries" = "$SMOKE_ROOT/checkout" ] && [ -d "$SMOKE_ROOT/checkout" ]; then
  pass 'quarantine root contains exactly the fresh checkout'
else
  fail 'quarantine root contains something other than the fresh checkout (never reuse it)'
fi

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
