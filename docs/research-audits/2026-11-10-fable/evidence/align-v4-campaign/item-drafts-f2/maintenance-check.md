Maintenance is print-only (RL-174 B.5 and D.1). Query the span's interval for the same processes as qualification. Earlier checks whose predicates lacked the three cloud jobs recorded them as unobserved.

```sh
(
  START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
  START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")" || exit 1
  END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')" || exit 1
  echo "maintenance window $START_LOCAL .. $END_LOCAL"
  sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
    --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd","bird","cloudd","fileproviderd"}' \
    > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err" || exit 1
  wc -l < "$OUT/maintenance-log.txt" || exit 1
  # per 10-minute bucket and process: "HH:M0 process count"
  awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
) || echo 'maintenance log unavailable; record as unobserved'
```
