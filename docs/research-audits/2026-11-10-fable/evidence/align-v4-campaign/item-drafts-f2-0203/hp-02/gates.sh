hp_gate() {
  now=$(date +%s)
  for proof in "HP_LOOK_RUN:${HP_LOOK_RUN:-}" "HP_DELTA_OK:${HP_DELTA_OK:-}" "HP01_SMOKE_PASS:${HP01_SMOKE_PASS:-}" "LINE2_OK:${LINE2_OK:-}" "LINE9_OK:${LINE9_OK:-}" "CHECKLIST_OK:${CHECKLIST_OK:-}" "STOPS_CLEAR:${STOPS_CLEAR:-}" "HOST_STATE_RECORDED:${HOST_STATE_RECORDED:-}" "COPY_TYPED_OK:${COPY_TYPED_OK:-}" "HOST_RESTORE_OK:${HOST_RESTORE_OK:-}" "GROUPS_ABSENT:${GROUPS_ABSENT:-}"; do
    case "$proof" in HP_LOOK_RUN:no|*:yes) ;; *) echo "STOP: missing/failed hp-02 admission $proof"; return 1;; esac
  done
  test "${HP_LOOK_RUN:-}" = no || { echo 'VOID: lm-hp-01 already run or unknown'; return 1; }
  test -n "${HP_LOOK_RECORD:-}" && test -n "${COPY_EVIDENCE:-}" && test -n "${HP01_DATES_RECORD:-}" || { echo 'STOP: evidence pointers required'; return 1; }
  for val in "${ISSUED_EPOCH:-}" "${KIT_ISSUED_EPOCH:-}" "${WATCH_UNTIL_EPOCH:-}" "${QUAL_CLOSE_EPOCH:-}" "${LATEST_CLOSE_EPOCH:-}" "${PRIOR_CLOSE_EPOCH:-}" "${NEXT_COUNTED_EPOCH:-}"; do
    case "$val" in ''|*[!0-9]*) echo 'STOP: missing/invalid epoch'; return 1;; esac
  done
  test "$ISSUED_EPOCH" -le "$now" && test "$now" -lt $((ISSUED_EPOCH+86400)) && test "$now" -lt 1795420800 || { echo 'VOID: item/queue expiry'; return 1; }
  test "$KIT_ISSUED_EPOCH" -le "$now" && test "$now" -lt $((KIT_ISSUED_EPOCH+604800)) || { echo 'VOID: seven-day kit expiry'; return 1; }
  test "$now" -lt "$WATCH_UNTIL_EPOCH" && test "$WATCH_UNTIL_EPOCH" -le $((now+86400)) || { echo 'STOP: watcher stale/future'; return 1; }
  today=$("$PY" -I -B -c 'import datetime,sys; from zoneinfo import ZoneInfo; print(datetime.datetime.fromtimestamp(int(sys.argv[1]),ZoneInfo("America/Los_Angeles")).date())' "$now") || return 1
  test "${QUAL_DATE:-}" = "$today" && test "$QUAL_CLOSE_EPOCH" -lt "$now" && test "${QUAL_CLEAN:-}" = yes && test -n "${QUAL_RECORD:-}" || { echo 'WAIT: a clean qualification span on this t0-date must precede hp-02'; return 1; }
  qday=$("$PY" -I -B -c 'import datetime,sys; from zoneinfo import ZoneInfo; print(datetime.datetime.fromtimestamp(int(sys.argv[1]),ZoneInfo("America/Los_Angeles")).date())' "$QUAL_CLOSE_EPOCH") || return 1
  # QUAL_DATE is the qualification SPAN t0-date, not its close date. A close may cross midnight.
  case ",${HP01_T0_DATES:-}," in *",$today,"*) echo 'VOID: hp-01 leg on same t0-date'; return 1;; esac
  test -n "${HP01_T0_DATES:-}" || { echo 'STOP: hp-01 date census required'; return 1; }
  for proof in "SESSION_READY:${SESSION_READY:-}" "COUNTED_READY:${COUNTED_READY:-}" "F2_READY:${F2_READY:-}"; do
    case "$proof" in *:no) ;; *:yes) echo "CEDE: higher rung $proof"; return 1;; *) echo 'STOP: priority unknown'; return 1;; esac
  done
  test "${F0_ELIGIBLE:-}" = no || { echo 'CEDE: F0 eligible/unknown'; return 1; }
  case "${F0_REASON:-}" in spacing|daily_cap|launch_window) ;; *) echo 'STOP: unsafe F0 refusal'; return 1;; esac
  test -n "${PRIORITY_RECORD:-}" || { echo 'STOP: priority census missing'; return 1; }
  if test "$NEXT_COUNTED_EPOCH" != 0 && test "$NEXT_COUNTED_EPOCH" -lt $((now+PROTECTED_S)); then echo 'CEDE: protected counted start'; return 1; fi
  case "${LAST_CLOSE_KIND:-}" in campaign) gap=300;; other) gap=1200;; *) echo 'STOP: close kind unknown'; return 1;; esac
  test "$LATEST_CLOSE_EPOCH" -ge "$QUAL_CLOSE_EPOCH" && test "$now" -ge $((LATEST_CLOSE_EPOCH+gap)) && test "$now" -ge $((PRIOR_CLOSE_EPOCH+gap)) || { echo 'WAIT: latest-close interval'; return 1; }
  test -n "${LATEST_CLOSE_RECORD:-}" || { echo 'STOP: latest-close receipt census record required'; return 1; }
  test "${PREDECESSOR_CLEAN:-}" = yes && test -n "${PREDECESSOR_RECORD:-}" || { echo 'VOID: predecessor not clean; never skip'; return 1; }
  picked=$(pick_arg "$now")
  test "$picked" != NONE && test "$picked" = "$ARG" || { echo 'STOP: date/band/argument changed'; return 1; }
  echo 'HP02 GATES PASS (record-backed operational observations only)'
}
