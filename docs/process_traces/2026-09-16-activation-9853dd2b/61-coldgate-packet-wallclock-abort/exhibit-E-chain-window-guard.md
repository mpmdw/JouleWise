# Exhibit E — scripts/night_chains/calibration_derivation_only.zsh at main 5472ff53: the window guard and abort_window_exhausted (verbatim excerpts)

```
    48	# flags are deliberately ABSENT: this night has no operator present and no
    49	# display action to schedule; the writer requires neither.
    50	#
    51	# Required environment comes from the plan-pinned wrapper, not a desk run.
    52	# WINDOW_END_EPOCH_S is the exclusive window end in Unix seconds.
    53	set -euo pipefail
    54	
    55	cd "${0:A:h:h:h}"
    56	REPO="${PWD}"
```
```
   125	abort_window_exhausted() {
   126	    log_event "session_abort reason=window_exhausted"
   127	    "$PY" "$REPO/scripts/recover_calibration_ledger.py" \
   128	        --ledger "$CALIBRATION_LEDGER" \
   129	        --head-pin "$LEDGER_HEAD_PIN" \
   130	        abort-session \
   131	        --session-id "$SESSION_ID" \
   132	        --plan "$PLAN" \
   133	        --reason window_exhausted
   134	}
   135	
   136	preflight_inputs() {
   137	    local input
   138	    # Every file input is authenticated as PRESENT before any window time is
   139	    # spent. A missing frozen plan or T1 vector discovered after the settle
```
```
   214	next_start=$("$DATE" +%s)
   215	for (( index = 1; index <= SLOT_COUNT; index++ )); do
   216	    slot=$(printf 'd%02d' "$index")
   217	    # Refuse before waiting: a slot whose capture cannot finish inside the
   218	    # window is recorded unused now rather than after a pointless sleep.
   219	    if (( next_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S )); then
   220	        log_event "slot_unused slot=$slot reason=window_exhausted"
   221	        abort_window_exhausted
   222	        exit 0
   223	    fi
   224	    now=$("$DATE" +%s)
   225	    if (( now < next_start )); then
   226	        "$SLEEP" "$(( next_start - now ))"
   227	    fi
   228	    # Re-read the clock after the wait: scheduler delay must not start a slot
   229	    # the window can no longer finish.
   230	    slot_start=$("$DATE" +%s)
   231	    if (( slot_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S )); then
   232	        log_event "slot_unused slot=$slot reason=window_exhausted"
   233	        abort_window_exhausted
   234	        exit 0
   235	    fi
   236	    log_event "slot_start slot=$slot"
```

Chain digest at this head: 4f1ede1e19af550cd153c86860eb4bd3cb1efc2c5f4a6c30fbb5cdcc45721e37
