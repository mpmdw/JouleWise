#!/bin/zsh
# SKELETON: pending S1/S2 flag landing; not to be pinned in a plan until the integration replay
# DIAGNOSTIC_NO_PACK / QUIET-MAC: invoked only by the governed night driver,
# after registration, review and agent-free admission. Nothing here arms a plan.
# S2 integration must supply the declared per-slot bindings as argv to this
# script; their CLI shape is not landed yet. They must bind d01..dNN to
# attempt IDs ${SESSION_ID}-dNN and custody under ${RUNS_ROOT}/instrument_validation.
# Required environment below comes from the future frozen plan, not a desk run.
# Window deadline is exclusive (Unix seconds). The driver retains its hard
# window deadline; this skeleton does not replace its supervision/recovery.
set -euo pipefail

cd "${0:A:h:h:h}"
: "${SESSION_ID:?required}"
: "${WINDOW_ID:?required}"
: "${PLAN_ID:?required}"
: "${PLAN_SHA256:?required}"
: "${PLAN:?required}"
: "${EVIDENCE_ROOT_ID:?required}"
: "${RUNS_ROOT:?required}"
: "${IDENTITY_EPOCH_JSON:?required}"
: "${T1_BINDINGS_JSON:?required}"
: "${WINDOW_END_EPOCH_S:?required}"
SLOT_COUNT=${SLOT_COUNT:-12}
if [[ "$SLOT_COUNT" != <-> || "$SLOT_COUNT" == 0 || "$WINDOW_END_EPOCH_S" != <-> ]]; then
    print -u2 -- "SLOT_COUNT must be positive and WINDOW_END_EPOCH_S must be Unix seconds"
    exit 64
fi

# One settle only; subsequent sleeps fill the start-to-start cadence.
sleep 600
python3 scripts/reserve_calibration_window_bracket.py \
    --session-kind derivation --slot-count "$SLOT_COUNT" \
    --session-id "$SESSION_ID" --window-id "$WINDOW_ID" \
    --plan-id "$PLAN_ID" --plan-sha256 "$PLAN_SHA256" --plan "$PLAN" \
    --evidence-root-id "$EVIDENCE_ROOT_ID" --runs-root "$RUNS_ROOT" \
    --identity-epoch-json "$IDENTITY_EPOCH_JSON" --t1-bindings-json "$T1_BINDINGS_JSON" \
    "$@" --execute

abort_window_exhausted() {
    python3 scripts/recover_calibration_ledger.py abort-session \
        --session-id "$SESSION_ID" --plan "$PLAN" --reason window_exhausted
}

next_start=$(date +%s)
for (( index = 1; index <= SLOT_COUNT; index++ )); do
    now=$(date +%s)
    if (( next_start >= WINDOW_END_EPOCH_S || now >= WINDOW_END_EPOCH_S )); then
        abort_window_exhausted
        exit 0
    fi
    if (( now < next_start )); then
        sleep "$(( next_start - now ))"
    fi
    # Recheck after sleep; scheduler delay must not start a slot past the end.
    slot_start=$(date +%s)
    if (( slot_start >= WINDOW_END_EPOCH_S )); then
        abort_window_exhausted
        exit 0
    fi
    slot=$(printf 'd%02d' "$index")
    python3 scripts/validate_powermetrics_fiducial.py \
        --allow-live --derivation-only --session-id "$SESSION_ID" --slot "$slot" \
        --attempt-id "${SESSION_ID}-${slot}" \
        --output-root "${RUNS_ROOT}/instrument_validation" --power-policy ac_high_power
    # Anchor to the actual start: never compress a later slot to catch up.
    next_start=$(( slot_start + 600 ))
done
# The last slot finalization closes the session and emits its terminal pin
# candidate. If any command fails, set -e stops; desk recovery belongs to S2.
