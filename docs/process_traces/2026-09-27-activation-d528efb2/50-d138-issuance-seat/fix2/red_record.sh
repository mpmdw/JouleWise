#!/bin/sh
set -eu
FIX_ROOT=/Users/edr/code/JouleWise-wt-d138-impl-d528efb2
RED_ROOT=/Users/edr/code/JouleWise-wt-d138-final-d528efb2
RUNNER=/tmp/d138-fix2-d528efb2/red_runner.py
PYTHON=/opt/homebrew/bin/python3
printf 'RED worktree head: '
git -C "$RED_ROOT" rev-parse HEAD
printf 'GREEN worktree head: '
git -C "$FIX_ROOT" rev-parse HEAD
printf 'GREEN worktree status:\n'
git -C "$FIX_ROOT" status --short
for entry in \
  'HR-1:tests.test_claim_hold_routes:ClaimHoldRouteTests:test_hr1_r7_pack_capture_preflight_stays_at_r7' \
  'HR-2:tests.test_claim_hold_routes:ClaimHoldRouteTests:test_hr2_r7_pack_default_bracket_refuses_new_epoch' \
  'HR-3:tests.test_claim_hold_routes:ClaimHoldRouteTests:test_hr3_manual_route_cannot_consume_held_file' \
  'HR-5:tests.test_claim_hold_routes:ClaimHoldRouteTests:test_hr5_loader_opt_in_is_explicit' \
  'DT-1:tests.test_calibration_bracketing:DoublingTriggerDispositionTests:test_dt1_one_new_valid_capture_does_not_double' \
  'DT-2:tests.test_calibration_bracketing:DoublingTriggerDispositionTests:test_dt2_eleven_new_valid_captures_do_not_double' \
  'P6:tests.test_promote_calibration_candidate:PromotionTests:test_p6_cited_evidence_and_disclosure_mutations_refuse'
do
  label=${entry%%:*}
  spec=${entry#*:}
  red_log="/tmp/d138-fix2-d528efb2/${label}-red.log"
  green_log="/tmp/d138-fix2-d528efb2/${label}-green.log"
  if D138_TARGET_ROOT="$RED_ROOT" D138_FIX_ROOT="$FIX_ROOT" "$PYTHON" -B "$RUNNER" "$spec" > "$red_log" 2>&1; then
    printf '%s RED UNEXPECTED PASS\n' "$label"
    cat "$red_log"
    exit 1
  fi
  printf '%s RED expected fail: ' "$label"
  rg '^FAILED|^ERROR|^FAIL:' "$red_log" | tail -n 2 || true
  if D138_TARGET_ROOT="$FIX_ROOT" D138_FIX_ROOT="$FIX_ROOT" "$PYTHON" -B "$RUNNER" "$spec" > "$green_log" 2>&1; then
    printf '%s GREEN PASS\n' "$label"
  else
    printf '%s GREEN FAIL\n' "$label"
    tail -n 25 "$green_log"
    exit 1
  fi
done
printf 'RED_RECORD=PASS\n'
