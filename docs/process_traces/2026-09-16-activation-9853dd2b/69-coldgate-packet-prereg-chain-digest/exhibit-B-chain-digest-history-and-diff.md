# Exhibit B — chain digest history and the full chain diff since sealing (scripts/night_chains/calibration_derivation_only.zsh)

| commit | date | chain sha256 (prefix) | event |
|---|---|---|---|
| d81c4cae | 2026-09-10 | b8bf5b0a85bb | the digest the pre-registration sealed |
| 3015cb39 | 2026-09-16 | b8bf5b0a85bb | main before PR #350 |
| d1aadecc | 2026-09-17 | 5383741e8705 | seat B: budget/deadline flags, NIGHT_VERIFY_ONLY, --pre-reserve-strict (PR #350 branch) |
| 64297f9d | 2026-09-17 | a7578b5ca4b9 | seat B fix round 1 (PR #350 branch) |
| 52274fc3 / c9589525 / 5472ff53 | 2026-09-17 | 4f1ede1e19af | structural bound marker export; PR #350 merged to main |
| a4d530cdab07a0b72d70f1fea00d145b177895f2 | 2026-09-17 | b5beea464d39 | abort-session --custody-budget-s (NIGHT-STALL-WALLCLOCK-ABORT-01 branch, not yet merged) |

## git diff 3015cb39..a4d530cdab07a0b72d70f1fea00d145b177895f2 -- scripts/night_chains/calibration_derivation_only.zsh
```diff
diff --git a/scripts/night_chains/calibration_derivation_only.zsh b/scripts/night_chains/calibration_derivation_only.zsh
index b74e91d7..968cbf6b 100755
--- a/scripts/night_chains/calibration_derivation_only.zsh
+++ b/scripts/night_chains/calibration_derivation_only.zsh
@@ -68,6 +68,16 @@ REPO="${PWD}"
 : "${IDENTITY_EPOCH_JSON:?required}"
 : "${T1_BINDINGS_JSON:?required}"
 : "${WINDOW_END_EPOCH_S:?required}"
+: "${NIGHT_DIR:?required}"
+: "${JOULEWISE_NIGHT_PLAN_ID:?required}"
+export JOULEWISE_NIGHT_PLAN_ID
+export JOULEWISE_CALIBRATION_REFUSAL_PATH="$NIGHT_DIR/calibration-refusal.json"
+# Inherited custody BUDGET (seconds of fresh allowance per operation), not a
+# night deadline: every process this chain starts -- the reservation, each
+# capture writer, and the session abort below, which runs when the window is
+# already spent -- bounds any governed read it was not handed a deadline for,
+# and refuses one it cannot bound. A deadline threaded by a caller still wins.
+export JOULEWISE_NIGHT_CUSTODY_BUDGET_S="${CUSTODY_BUDGET_S:-120}"
 
 PY="${PY:-$REPO/.venv/bin/python}"
 SLEEP="${SLEEP:-/bin/sleep}"
@@ -98,7 +108,6 @@ if (( SLOT_COUNT < 1 || SLOT_CADENCE_S < 1 || SETTLE_S < 1 \
 fi
 
 OPERATOR_LOG_ROOT="$WINDOW_CUSTODY_ROOT/operator_logs"
-/bin/mkdir -p "$OPERATOR_LOG_ROOT" "$RUNS_ROOT/instrument_validation"
 CHAIN_LOG="$OPERATOR_LOG_ROOT/derivation-chain.log"
 
 timestamp() {
@@ -115,13 +124,20 @@ settle() {
 
 abort_window_exhausted() {
     log_event "session_abort reason=window_exhausted"
+    # --custody-budget-s like every sibling call, and deliberately NOT a
+    # --custody-deadline-epoch-s: this runs when the window is already spent,
+    # so an absolute deadline would refuse the one operation that closes the
+    # session. The abort reads ONE slot's custody state (the next slot, the
+    # only such value it consumes), so this is the whole allowance it can
+    # spend -- not one allowance per declared slot.
     "$PY" "$REPO/scripts/recover_calibration_ledger.py" \
         --ledger "$CALIBRATION_LEDGER" \
         --head-pin "$LEDGER_HEAD_PIN" \
         abort-session \
         --session-id "$SESSION_ID" \
         --plan "$PLAN" \
-        --reason window_exhausted
+        --reason window_exhausted \
+        --custody-budget-s "${CUSTODY_BUDGET_S:-120}"
 }
 
 preflight_inputs() {
@@ -138,28 +154,42 @@ preflight_inputs() {
     done
 }
 
-# Order follows the pinned G2-a chain (SHAKEDOWN-G2-RUNSHEET.md:509-536):
-# input preflight, pre-reserve readiness, and the session reservation FIRST,
-# then chain_start, then the ONE settle, then the captures. Reserving after the
-# settle would make the reservation the last machine action before slot d01 and
+# Preserve the pinned G2-a timing order (SHAKEDOWN-G2-RUNSHEET.md:509-536):
+# input preflight and reservation's enforcing readiness precede any write,
+# then session reservation, chain_start, the ONE settle, and captures. Unlike
+# the runsheet, readiness is not a separate early-warning command here.
+# Reserving after the settle would make the reservation the last machine
+# action before slot d01 and make
 # the pre-registration's "one 600 s settle after the last operator action"
 # literally false.
 preflight_inputs
 
-# G2-a parity (runsheet L509-512): the early-warning readiness check runs before
-# the reservation, so an unready ledger refuses while nothing has been written
-# and no window time has been spent. It never authorizes ARM.
-"$PY" "$REPO/scripts/recover_calibration_ledger.py" \
-    --ledger "$CALIBRATION_LEDGER" \
-    --head-pin "$LEDGER_HEAD_PIN" \
-    readiness \
-    --phase pre-reserve \
-    --session-id "$SESSION_ID" \
-    --plan "$PLAN"
+# Reservation owns one bounded custody pass. --pre-reserve-strict preserves
+# the early refusal before retry, recovery or append, including interrupted
+# claims. It emits the pre_reserve_readiness report with frozen-plan bindings.
+# A separate readiness command would duplicate custody reads ahead of this
+# deadline. Verify-only implies strictness and uses the same arguments.
+reservation_mode=(--execute)
+if [[ "${NIGHT_VERIFY_ONLY:-0}" == 1 ]]; then
+    reservation_mode=(--verify-only)
+fi
 
-"$PY" "$REPO/scripts/reserve_calibration_window_bracket.py" \
+reservation_call() {
+    # The driver discovers input files from this exact expanded argv, using
+    # its production environment builder. Inspection never invokes reservation.
+    if [[ "${NIGHT_RESERVATION_ARGV_ONLY:-0}" == 1 ]]; then
+        printf '%s\0' "$@"
+        return 0
+    fi
+    "$PY" "$REPO/scripts/reserve_calibration_window_bracket.py" "$@"
+}
+
+reservation_call \
+    --pre-reserve-strict \
     --ledger "$CALIBRATION_LEDGER" \
     --head-pin "$LEDGER_HEAD_PIN" \
+    --custody-budget-s "${CUSTODY_BUDGET_S:-120}" \
+    --custody-deadline-epoch-s "$(( WINDOW_END_EPOCH_S - 10 ))" \
     --session-kind derivation \
     --slot-count "$SLOT_COUNT" \
     --session-id "$SESSION_ID" \
@@ -172,7 +202,12 @@ preflight_inputs
     --identity-epoch-json "$IDENTITY_EPOCH_JSON" \
     --t1-bindings-json "$T1_BINDINGS_JSON" \
     "$@" \
-    --execute
+    "${reservation_mode[@]}"
+# set -e already preserves a refused reservation's exit status and stdout.
+if [[ "${NIGHT_VERIFY_ONLY:-0}" == 1 || "${NIGHT_RESERVATION_ARGV_ONLY:-0}" == 1 ]]; then
+    exit 0
+fi
+/bin/mkdir -p "$OPERATOR_LOG_ROOT" "$RUNS_ROOT/instrument_validation"
 log_event "session_open kind=derivation slots=$SLOT_COUNT"
 log_event "chain_start session=$SESSION_ID window=$WINDOW_ID slots=$SLOT_COUNT \
 settle_s=$SETTLE_S slot_cadence_s=$SLOT_CADENCE_S slot_capture_budget_s=$SLOT_CAPTURE_BUDGET_S"
@@ -216,6 +251,8 @@ for (( index = 1; index <= SLOT_COUNT; index++ )); do
     if "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
         --allow-live \
         --derivation-only \
+        --custody-budget-s "${CUSTODY_BUDGET_S:-120}" \
+        --custody-deadline-epoch-s "$(( WINDOW_END_EPOCH_S - 10 ))" \
         --ledger "$CALIBRATION_LEDGER" \
         --head-pin "$LEDGER_HEAD_PIN" \
         --session-id "$SESSION_ID" \
```
