EDITS = [
# header: drafted-by line
("drafted by the items-rl165 drafter 2026-11-14 PST, ISSUED",
 "drafted by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED"),
("a launch that cannot meet rules 5 to 7: NOTHING launches",
 "a launch that cannot meet rules 5 to 7 (rule 6 is now the c3f4bacd8 launch window 02:35:00-22:40:00, RL-171): NOTHING launches"),
# rule 3(c) example
("(for example the evening after a Sunday pull, with the next counted span at 02:40).",
 "(for example Sunday afternoon after the dev-02 pull: dev-02's second half, `dev-02-s03`, is the Monday span of the 6 + 6 split, so it cannot arm before Mon 00:00:00)."),
# rule 6
("6. **Latest launch.** Launch + 12,180 s is at or before the next 01:30:00 local (RL-164 §5; RL-155 §4 rule 4). With 60 s of slack, the latest t0 is 22:06:00 on any evening. **No F0 launches between 01:30:00 and 02:40:00.**",
 "6. **Launch window: 02:35:00 to 22:40:00 local (RL-171 §2 and §3; RL-156 §5's 22:40 restored).** RL-171 retires \"launch + 12,180 s by 01:30\" (RL-164 §5) and \"no F0 between 01:30 and 02:40\". What is left is what the bytes at `c3f4bacd8` do: `soak_child` refuses a soak whose start lies in (22:50:40, 02:35:00), because the soak plus Part C's cap (11,360 s) would meet 02:00-02:35 (run on the Air at `c3f4bacd8`: soak start 22:50:40 admitted, 22:50:41 refused, 02:34:59 refused, 02:35:00 admitted; `/Volumes/JW-EXT/scratch/items-rl171/probe/c3f4-soak-child-boundary.txt`). So the launch is at or after 02:35:00 and at or before 22:40:00 (ten minutes of preflight before the latest soak start). RL-171 §4 keeps this refusal until the slot session has run. A run that crosses 00:00 is recorded, not a gate."),
# rule 7 example
("Example: with the Sunday dev-02 pull staged and not yet run (latest t0 18:33:10), an F0 may launch only by 14:50:10 (18:33:10 - 12,180 s - 1,200 s).",
 "Under RL-171 a counted span's latest legal t0 is the end of its item's window (the calendar day for the dev-02 halves). Example: with the Sunday dev-02 pull staged and not yet run (window to Sun 23:59:59), an F0 may launch only by 20:16:59 (23:59:59 - 12,180 s - 1,200 s); a staged span inside the 10:50-13:15 band of its pin cannot arm there, so it does not bind rule 7 there."),
# conditions: 20-minute quiet -> close interval
("  - **20-minute quiet** after the latest close of anything on this host (span, Part C or F0, slot session, W1) (RL-155 R-B):",
 "  - **The close interval (RL-171 §6.1, amending RL-155 R-B's 20 minutes)** after the latest close of anything on this host (span, Part C or F0, slot session, W1): every restore line of that close passed and its Check (with the hash-verified journal copy) is reported, and at least GAP seconds have passed. GAP is QUIET_CAMPAIGN_S when the latest close was a campaign span (LEAD FILLS below: 300 s once the lead has confirmed from the 11-14 and 11-15 closes that the Check and the copy finish inside 5 min, else their longest time + 120 s; 1,200 s until the lead fills it), and 1,200 s after a Part C or F0, F2, a slot session or W1. The close is read from"),
("  - **The complete eligibility check runs twice:** in \"Start and check\" and again as the first step of \"Run\", on state re-read at that moment (the current clock, the current W1-line head, the expiry, the refusal and reply state, the staged items' latest t0s, the session reservation).",
 "  - **The complete eligibility check runs twice:** in \"Start and check\" and again as the first step of \"Run\", on state re-read at that moment (the current clock, the current W1-line head, the expiry, the refusal and reply state, the staged items' window ends, the session reservation, LAST_CLOSE_KIND)."),
("- **Timing.** Part C's cap 9,560 s; the launcher's minimum for `--fresh-soak --parts C` is **12,180 s (3 h 23 min), the worst case**. Expected about 2 h (item 322's run: 7,134 s). The fence deadline is launch + 14,400 s, **capped at the next 01:30:00 local**. At this commit the soak child refuses a soak start whose soak + Part C span (11,360 s) would meet 02:00-02:35 (22:50:40 on any evening); rule 6 is stricter and is the bound. There is no 10:50-13:15 bound on this commit (the batch window is 02:00-02:35; RL-155a §3's exclusion binds the campaign kits only). A run across 00:00 is recorded (the `/private/tmp` walk), not a gate.",
 "- **Timing.** Part C's cap 9,560 s; the launcher's minimum for `--fresh-soak --parts C` is **12,180 s (3 h 23 min), the worst case**. Expected about 2 h (item 322's run: 7,134 s). The fence deadline is launch + 14,400 s (the 01:30 cap is retired with RL-164 §5's rule, RL-171 §2). At this commit the soak child refuses a soak start whose soak + Part C span (11,360 s) would meet 02:00-02:35: that is rule 6's window, 02:35:00-22:40:00. There is no 10:50-13:15 bound on this commit (its `OS_BATCH_WINDOW_LOCAL` is 02:00-02:35, so it has no midday soak wait): F0 is the one rung that fills 10:50-13:15 while the campaign pins `b4b6aeb19`, `dd206025a` and `2d347f721` cannot launch there. A run across 00:00 is recorded (the `/private/tmp` walk), not a gate."),
# script: close interval
("  # Never while anything is armed; 20-min quiet after the latest close of anything (span, Part C or F0, session, W1)",
 "  # Never while anything is armed; the close interval after the latest close of anything (RL-171 §6.1)"),
("  test \"$(date +%s)\" -ge $((HOST_LAST_CLOSE + 1200)) || { echo \"WAIT: 20 min quiet after the latest close ($HOST_LAST_CLOSE)\"; return 1; }",
 "  case \"${LAST_CLOSE_KIND:-}\" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo \"STOP: set LAST_CLOSE_KIND to campaign or other\"; return 1;; esac\n  test \"$(date +%s)\" -ge $((HOST_LAST_CLOSE + GAP)) || { echo \"WAIT: close interval $GAP s after the latest close ($HOST_LAST_CLOSE; RL-171 §6.1)\"; return 1; }"),
("EXPIRY_EPOCH=<LEAD FILLS: EXPIRY_EPOCH>",
 "EXPIRY_EPOCH=<LEAD FILLS: EXPIRY_EPOCH>\nQUIET_CAMPAIGN_S=1200   # LEAD FILLS (RL-171 §6.1): 300 once the lead confirms the Check + hash-verified copy finish inside 5 min (else their longest + 120); 1200 until then"),
# python rule 5/6/7
("  NEXT_0130=\"$(\"$PY\" -I -B - \"$LEDGER\" \"${COUNTED_LATEST:?}\" \"${SESSION_T0:?}\" <<'PY'",
 "  F0_NOW=\"$(\"$PY\" -I -B - \"$LEDGER\" \"${COUNTED_LATEST:?}\" \"${SESSION_T0:?}\" <<'PY'"),
("""hm = d.hour * 3600 + d.minute * 60 + d.second
if 5400 <= hm < 9600: sys.exit("STOP: no F0 between 01:30 and 02:40 (rule 6)")
day = d.date() if hm < 5400 else d.date() + dt.timedelta(days=1)
nxt = int(dt.datetime.combine(day, dt.time(1, 30), TZ).timestamp())
if now + 12180 + 60 > nxt: sys.exit(f"STOP: launch + 12,180 s would pass 01:30:00 ({nxt}) (rule 6)")
""",
 """hm = d.hour * 3600 + d.minute * 60 + d.second
if not (9300 <= hm <= 81600): sys.exit("STOP: outside 02:35:00-22:40:00, the c3f4bacd8 soak child's window (rule 6, RL-171)")
"""),
("print(nxt)\nPY\n)\" || return 1\n  echo \"F0 ELIGIBLE at $(date +%s); next 01:30 = $NEXT_0130; trigger $TRIGGER $TRIGGER_SPAN; host last close $HOST_LAST_CLOSE\"",
 "print(int(now))\nPY\n)\" || return 1\n  echo \"F0 ELIGIBLE at $F0_NOW; trigger $TRIGGER $TRIGGER_SPAN; host last close $HOST_LAST_CLOSE ($LAST_CLOSE_KIND, gap $GAP s)\""),
("#   OTHER_CLOSE_EPOCH   REQUIRED: a whole epoch (rounded up) of a close outside the census roots (session, W1), or an explicit 0\n#   SESSION_READY, SESSION_T0, COUNTED_LATEST   R-A, the reservation and rule 7",
 "#   OTHER_CLOSE_EPOCH   REQUIRED: a whole epoch (rounded up) of a close outside the census roots (session, W1), or an explicit 0\n#   LAST_CLOSE_KIND     campaign (the latest close was a campaign span) or other (Part C/F0, F2, slot session, W1)\n#   SESSION_READY, SESSION_T0, COUNTED_LATEST   R-A, the reservation and rule 7 (COUNTED_LATEST: the window-end epochs\n#                       of every staged counted span due today, space-separated, or none)"),
# deadline (start and check)
("# Deadline: launch + 4 h, capped at the next 01:30:00 (rule 6); the launcher refuses anything under 12,180 s\nDEADLINE=\"$(\"$PY\" -B -c \"import time; print(min(time.time()+14400, $NEXT_0130))\")\"\n\"$PY\" -B -c \"import time,sys; sys.exit(0 if $DEADLINE - time.time() >= 12180 + 60 else 1)\" || { echo \"STOP: worst case cannot end by 01:30\"; exit 1; }",
 "# Deadline: launch + 4 h (RL-171 retires the 01:30 cap); the launcher refuses anything under 12,180 s\nDEADLINE=\"$(\"$PY\" -B -c \"import time; print(time.time()+14400)\")\""),
# run block
("f0_eligible || exit 1\nDEADLINE=\"$(\"$PY\" -B -c \"import time; print(min(time.time()+14400, $NEXT_0130))\")\"\n\"$PY\" -B -c \"import time,sys; sys.exit(0 if $DEADLINE - time.time() >= 12180 + 60 else 1)\" || { echo \"STOP: worst case cannot end by 01:30\"; exit 1; }\nT0=$(date +%s)",
 "f0_eligible || exit 1\nDEADLINE=\"$(\"$PY\" -B -c \"import time; print(time.time()+14400)\")\"\nT0=$(date +%s)"),
("Record PY, MAGISTRATE_PID, OUT, DEADLINE, NEXT_0130, T0,",
 "Record PY, MAGISTRATE_PID, OUT, DEADLINE, T0, LAST_CLOSE_KIND, QUIET_CAMPAIGN_S,"),
# check: maintenance line
("**Check (next activation, after the fence is gone):** item 325's Check, verbatim, with this run's `$OUT`:",
 """**Check (next activation, after the fence is gone):**

**Maintenance line first (RL-171 §5 item 1; as item 331). Print only: it gates nothing and is not a stop.** One read-only system-log query over the run's interval (from OUT's UTC launch stamp to the receipt's mtime) for the OS maintenance processes, saved BESIDE the journals as `$OUT/maintenance-log.txt`, with a per-10-minute count printed for the report. F0 now launches from 02:35, beside the second cluster (02:37-02:43) and the XProtect fast scans (05:08, 11:08, 17:08, 23:08 on the current boot); the line records what overlapped. Nothing is judged on it.

```sh
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \\
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd"}' \\
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
```

Then item 325's Check, verbatim, with this run's `$OUT`:"""),
("- the close used for the quiet, the previous F0 t0, this t0, and whether 00:00 fell inside the span;",
 "- the maintenance line's counts (print only);\n- the close used for the close interval and its kind (LAST_CLOSE_KIND, GAP), the previous F0 t0, this t0, and whether 00:00 fell inside the span;"),
]
