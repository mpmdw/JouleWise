#!/bin/zsh
# SKELETON: pending S1/S2 flag landing; not to be pinned in a plan until the integration replay
#
# One DIAGNOSTIC_NO_PACK derivation night for the new identity epoch, per
# cold-gate ruling 46 §R-c: ONE 600 s settle after the last operator action,
# then ONE derivation-kind ledger session of $SLOT_COUNT declared slots, then
# one derivation-only capture per slot at a 600 s START-TO-START cadence.
# A slot the window cannot reach is recorded unused by the session abort
# (reason window_exhausted), never compressed, retried, or replaced.
#
# NO probe ladder, NO measurement pack, NO Git, NO claim output. Nothing here
# arms a plan; the governed night driver invokes it only after registration,
# review, and agent-free admission, and it keeps its own hard window deadline,
# supervision, and recovery. The shape follows the G2-a chain the runbook pins
# (scripts/gen_g2_phase_d.py): timestamp(), settle(), one operator-log line per
# lifecycle transition, absolute interpreter and coreutil paths.
#
# UNLANDED SURFACE, written exactly as ruling 46 specifies (seats S1/S2):
#   reserve_calibration_window_bracket.py  --session-kind derivation --slot-count N
#   validate_powermetrics_fiducial.py      --derivation-only
#   the declared per-slot bindings, whose CLI shape becomes a list (addendum 11
#   N2). Until it lands, S2 integration supplies them as this script's argv,
#   binding d01..dNN to attempt ids ${SESSION_ID}-dNN with custody under
#   ${RUNS_ROOT}/instrument_validation; they are forwarded verbatim.
# The G2-a chain's --arm-countdown-s and --sleep-display-before-capture writer
# flags are deliberately ABSENT: this night has no operator present and no
# display action to schedule. Confirm with S1 before the integration replay.
#
# Required environment comes from the future frozen plan, not a desk run.
# WINDOW_END_EPOCH_S is the exclusive window end in Unix seconds.
set -euo pipefail

cd "${0:A:h:h:h}"
REPO="${PWD}"

: "${SESSION_ID:?required}"
: "${WINDOW_ID:?required}"
: "${PLAN_ID:?required}"
: "${PLAN_SHA256:?required}"
: "${PLAN:?required}"
: "${EVIDENCE_ROOT_ID:?required}"
: "${RUNS_ROOT:?required}"
: "${WINDOW_CUSTODY_ROOT:?required}"
: "${CALIBRATION_LEDGER:?required}"
: "${LEDGER_HEAD_PIN:?required}"
: "${IDENTITY_EPOCH_JSON:?required}"
: "${T1_BINDINGS_JSON:?required}"
: "${WINDOW_END_EPOCH_S:?required}"

PY="${PY:-$REPO/.venv/bin/python}"
SLEEP="${SLEEP:-/bin/sleep}"
DATE="${DATE:-/bin/date}"
SLOT_COUNT="${SLOT_COUNT:-12}"
SETTLE_S="${SETTLE_S:-600}"
SLOT_CADENCE_S="${SLOT_CADENCE_S:-600}"
# Ruling 46 V3 budgets 8 min for a capture; a slot that cannot FINISH inside
# the window must not be started, or the night runs past its agent-free end.
SLOT_CAPTURE_BUDGET_S="${SLOT_CAPTURE_BUDGET_S:-480}"

# Refuse before the settle, the reservation, and any operator-log write, so an
# unusable declaration costs no window time and leaves no partial night.
for _value in "$SLOT_COUNT" "$SETTLE_S" "$SLOT_CADENCE_S" \
    "$SLOT_CAPTURE_BUDGET_S" "$WINDOW_END_EPOCH_S"; do
    if [[ "$_value" != <-> ]]; then
        print -u2 -- "slot count, cadence, budget and window end must be Unix seconds"
        exit 64
    fi
done
if (( SLOT_COUNT < 1 || SLOT_CADENCE_S < 1 )); then
    print -u2 -- "SLOT_COUNT and SLOT_CADENCE_S must be positive"
    exit 64
fi

OPERATOR_LOG_ROOT="$WINDOW_CUSTODY_ROOT/operator_logs"
mkdir -p "$OPERATOR_LOG_ROOT" "$RUNS_ROOT/instrument_validation"
CHAIN_LOG="$OPERATOR_LOG_ROOT/derivation-chain.log"

timestamp() {
    TZ=UTC "$DATE" '+%Y-%m-%dT%H:%M:%SZ'
}

log_event() {
    echo "$(timestamp) $1" >> "$CHAIN_LOG"
}

settle() {
    "$SLEEP" "$SETTLE_S"
}

abort_window_exhausted() {
    log_event "session_abort reason=window_exhausted"
    "$PY" "$REPO/scripts/recover_calibration_ledger.py" \
        --ledger "$CALIBRATION_LEDGER" \
        --head-pin "$LEDGER_HEAD_PIN" \
        abort-session \
        --session-id "$SESSION_ID" \
        --plan "$PLAN" \
        --reason window_exhausted
}

log_event "chain_start session=$SESSION_ID window=$WINDOW_ID slots=$SLOT_COUNT"

# The ONE settle of the night. The cadence below is start-to-start and never
# inserts a second one.
settle
log_event "settle_complete settle_s=$SETTLE_S"

"$PY" "$REPO/scripts/reserve_calibration_window_bracket.py" \
    --ledger "$CALIBRATION_LEDGER" \
    --head-pin "$LEDGER_HEAD_PIN" \
    --session-kind derivation \
    --slot-count "$SLOT_COUNT" \
    --session-id "$SESSION_ID" \
    --window-id "$WINDOW_ID" \
    --plan-id "$PLAN_ID" \
    --plan-sha256 "$PLAN_SHA256" \
    --plan "$PLAN" \
    --evidence-root-id "$EVIDENCE_ROOT_ID" \
    --runs-root "$RUNS_ROOT" \
    --identity-epoch-json "$IDENTITY_EPOCH_JSON" \
    --t1-bindings-json "$T1_BINDINGS_JSON" \
    "$@" \
    --execute
log_event "session_open kind=derivation slots=$SLOT_COUNT"

next_start=$("$DATE" +%s)
for (( index = 1; index <= SLOT_COUNT; index++ )); do
    slot=$(printf 'd%02d' "$index")
    # Refuse before waiting: a slot whose capture cannot finish inside the
    # window is recorded unused now rather than after a pointless sleep.
    if (( next_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S )); then
        log_event "slot_unused slot=$slot reason=window_exhausted"
        abort_window_exhausted
        exit 0
    fi
    now=$("$DATE" +%s)
    if (( now < next_start )); then
        "$SLEEP" "$(( next_start - now ))"
    fi
    # Re-read the clock after the wait: scheduler delay must not start a slot
    # the window can no longer finish.
    slot_start=$("$DATE" +%s)
    if (( slot_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S )); then
        log_event "slot_unused slot=$slot reason=window_exhausted"
        abort_window_exhausted
        exit 0
    fi
    log_event "slot_start slot=$slot"
    "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
        --allow-live \
        --derivation-only \
        --ledger "$CALIBRATION_LEDGER" \
        --head-pin "$LEDGER_HEAD_PIN" \
        --session-id "$SESSION_ID" \
        --slot "$slot" \
        --attempt-id "${SESSION_ID}-${slot}" \
        --output-root "$RUNS_ROOT/instrument_validation" \
        --power-policy ac_high_power
    log_event "slot_end slot=$slot"
    # Anchor the cadence to the actual start: never compress a later slot to
    # catch up on a long capture.
    next_start=$(( slot_start + SLOT_CADENCE_S ))
done

# Finalizing the last declared slot closes the session and emits its terminal
# pin candidate; the desk reviews and commits it before the next night opens.
# Any failure above stops the chain under set -e with the session still open;
# recovery is seat S2's desk tool, never a retry inside the window.
log_event "derivation_night_complete slots=$SLOT_COUNT"
