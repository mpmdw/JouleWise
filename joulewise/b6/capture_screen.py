"""Opening-capture block-6 screen, rendered by the chain in round two."""

from decimal import Decimal


PACK_ALIASES = {
    "d117_floor_qwen3-1p7b_v5": "alpha",
    "d117_floor_qwen3-8b_v5": "beta",
    "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5": "gamma",
}
# Registration S-5, confirmed by the 2026-10-16 lead ruling: the smallest
# 1.7B phase reaches 25% attribution at 6.5 J / (0.047 J/ms), rounded up
# to 139 ms. BETA has no registered T10; never borrow the 1.7B line.
REGISTERED_T10_STOP_S = {"alpha": Decimal("0.139"), "gamma": Decimal("0.139"), "beta": None}


def operative_bound_stop_s(registration, pack_id=None):
    """Use the pack's registered line, with no fallback to another pack."""
    identity = pack_id if pack_id is not None else registration.get("pack_id", "")
    label = PACK_ALIASES.get(identity, str(identity).lower())
    if label in REGISTERED_T10_STOP_S:
        return REGISTERED_T10_STOP_S[label]
    own = registration.get("pack_id", "")
    if PACK_ALIASES.get(own, str(own).lower()) != label:
        return None
    value = registration.get("calibration", registration).get("operative_bound_stop_s")
    return None if value is None else Decimal(str(value))

SCREEN_SHELL = r'''
screen_b6_calibration() {
  local dir="$1"
  local b
  b="$(/usr/bin/jq -r '.b_fiducial_s // empty' "$dir/instrument_evidence.json")"
  if [ -z "$b" ]; then
    flag calibration.bracket_incomplete window "" '{"slot":"pre","reason":"bound_absent"}' "$CLAIM_RUNS_ROOT" "opening capture has no bound"
    return 1
  fi
  if [[ "$B6_ALIGNMENT_REFERENCE_S" != "null" ]] && (( b > B6_ALIGNMENT_REFERENCE_S )); then
    flag calibration.alignment_above_reference window "" "{\"b_fiducial_s\":$b}" "$CLAIM_RUNS_ROOT" "opening alignment above reference; bound carried"
  fi
  if [[ "$B6_OPERATIVE_BOUND_STOP_S" == "null" ]]; then
    flag calibration.stop_line_unsized window "" "{\"b_fiducial_s\":$b}" "$CLAIM_RUNS_ROOT" "no registered T10 stop; bound carried and run phase checks decide"
  fi
  if [[ "$B6_OPERATIVE_BOUND_STOP_S" != "null" && "$B6_BRACKET_SCREEN_S" != "null" ]] && (( b + B6_BRACKET_SCREEN_S > B6_OPERATIVE_BOUND_STOP_S )); then
    stop_chain operative_bound_above_stop 13
  fi
  return 0
}
'''
