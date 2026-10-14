"""Opening-capture block-6 screen, rendered by the chain in round two."""

SCREEN_SHELL = r'''
screen_b6_calibration() {
  local dir="$1"
  local b
  b="$(/usr/bin/jq -r '.b_fiducial_s // empty' "$dir/instrument_evidence.json")"
  if [ -z "$b" ]; then
    flag calibration.bracket_incomplete window "" '{"slot":"pre","reason":"bound_absent"}' "$CLAIM_RUNS_ROOT" "opening capture has no bound"
    return 0
  fi
  if (( b > B6_ALIGNMENT_REFERENCE_S )); then
    flag calibration.alignment_above_reference window "" "{\"b_fiducial_s\":$b}" "$CLAIM_RUNS_ROOT" "opening alignment above reference; bound carried"
  fi
  if [[ "$B6_OPERATIVE_BOUND_STOP_S" != "null" ]] && (( b + B6_BRACKET_SCREEN_S > B6_OPERATIVE_BOUND_STOP_S )); then
    stop_chain operative_bound_above_stop 12
  fi
  return 0
}
'''
