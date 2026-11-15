"""Shared RL-171 rewrites for the campaign items (exact strings; every one is counted)."""
import re

QUIET_BLOCK = '''QUIET_CAMPAIGN_S=1200   # LEAD FILLS (RL-171 §6.1): 300 once the lead has confirmed from the 11-14/11-15 closes that the Check and the
                        # hash-verified copy finish inside 5 min (else their longest time + 120 s); 1200 until the lead fills it
: "${LAST_CLOSE_KIND:?Set to campaign if the latest close of anything on this host was a campaign span, else other (Part C/F0, F2, slot session, W1)}"
case "$LAST_CLOSE_KIND" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo "STOP: LAST_CLOSE_KIND must be campaign or other"; exit 1;; esac
echo "close interval GAP $GAP s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)"'''

ARG_SET = '''ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"'''

ARG_RECHECK = '''NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG" \\
  || { echo "STOP: the clock left ARG $ARG's band (or this item's window) since Start and check; run Start and check again (new OUT) or mail the lead"; exit 1; }'''

MAINT = '''**Maintenance line first (RL-171 §5 item 1; as item 331). Print only: it gates nothing and is not a stop.** Set `ARG` to the batch-window argument recorded at the arm (`export ARG=...`); the receipt assert below compares with it. Then one read-only system-log query over the span's interval (from OUT's UTC launch stamp to the receipt's mtime) for the OS maintenance processes, saved BESIDE the journals as `$OUT/maintenance-log.txt`, plus a per-10-minute count printed for the report. Report the counts and which legs' intervals they overlap (from each `leg_summary.json`'s start and end, if present; else say "overlap left to the desk"). A leg hit by a maintenance job is judged by rule 5 as before (RL-171 §2 item 2). With `13:14-13:15` a leg may run through 02:00-02:35 (dasd about 02:08; XProtect to about 02:28): that is the case rule 5 exists for (one redo of about 21 min, quota 2).

```sh
: "${ARG:?Set ARG to the batch-window argument recorded at the arm}"; export ARG
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \\
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd"}' \\
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
# per 10-minute bucket and process: "HH:M0 process count"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
```

The Check proper:
'''

HOST_PROSE_OLD = "at least 1,200 s since that latest close (the newest"
HOST_PROSE_NEW = ("at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is "
                  "QUIET_CAMPAIGN_S after a campaign span's close, which the lead fills as 300 s once it has confirmed that the "
                  "Check and the hash-verified copy finish inside 5 min, else 1,200 s; GAP is 1,200 s after a Part C or F0, F2, "
                  "a slot session or W1) (the newest")

def count_sub(s, old, new, n=None):
    k = s.count(old)
    if n is not None and k != n:
        raise SystemExit(f"expected {n} of {old[:90]!r}, found {k}")
    if k == 0:
        raise SystemExit(f"none of {old[:90]!r}")
    return s.replace(old, new)

def common(s, check_heading, pick_fn):
    # the argument on every validate-kit / plan / launch line
    s = count_sub(s, 'validate-kit "$KIT" --repo "$REPO" --batch-window 02:00-02:35', 'validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"', 1)
    s, k = re.subn(r'(scripts/cadence_legs_runner\.py plan --kit "\$KIT" --legs \S+) --batch-window 02:00-02:35', r'\1 --batch-window "$ARG"', s)
    assert k == 1, ("plan", k)
    s, k = re.subn(r'(  --kit "\$KIT" --legs \S+) --batch-window 02:00-02:35 \\', r'\1 --batch-window "$ARG" \\', s)
    assert k == 1, ("launch", k)
    s = count_sub(s, 'batch_windows must be ["02:00-02:35"]', 'batch_windows must be ["$ARG"]', 1)
    s = count_sub(s, 'assert r["batch_windows"] == ["02:00-02:35"]',
                  'assert r["batch_windows"] == [__import__("os").environ["ARG"]], r["batch_windows"]   # ARG as recorded at the arm (RL-171)', 1)
    s = count_sub(s, '`plan.batch_windows` equal to `["02:00-02:35"]`',
                  '`plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check', 1)
    s, k = re.subn(r'\. Record (SPAN|PRIOR_CLOSE_EPOCH|RAN)', r'. Record ARG, LAST_CLOSE_KIND, GAP, QUIET_CAMPAIGN_S, \1', s)
    assert k == 1, ("record", k)
    s = count_sub(s, 'test "$(date +%s)" -ge $((HOST_LAST_CLOSE + 1200)) || { echo "WAIT: 20 min quiet after the latest close of anything on this host (RL-155 R-B)"; exit 1; }',
                  'test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }', 1)
    if "no leg starts inside 02:00-02:35" in s: s = count_sub(s, "no leg starts inside 02:00-02:35", "no leg starts inside the batch-window argument (`$ARG`: 02:00-02:35 or 13:14-13:15, chosen by the launch time, RL-171 §3)", 1)
    s = count_sub(s, HOST_PROSE_OLD, HOST_PROSE_NEW, 1)
    s = count_sub(s, check_heading, check_heading + "\n\n" + MAINT.rstrip("\n"), 1)
    return s
