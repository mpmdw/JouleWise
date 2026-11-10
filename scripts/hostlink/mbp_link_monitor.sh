#!/bin/bash
# mbp_link_monitor.sh: run by the Air LaunchAgent com.joulewise.hostlink.monitor every 300 s.
# One bounded SSH probe of the MBP per run, never during an armed span.
# It writes a one-line status file that the lead session watches and pushes to Ed.
# The probe:
#   - runs `true` (reachability);
#   - lists the LOADED state of the watchdog agent and the presence of the night
#     agents, as label names only;
#   - counts claude processes.
# It never reads custody, plans or night records.
# Armed-span guard: if com.joulewise.night is loaded on the MBP, the probe
# stops after that check (one launchctl query) and reports "armed".
set -u
OUT_DIR="$HOME/Library/Logs/jw-hostlink"; mkdir -p "$OUT_DIR"
STATUS="$OUT_DIR/status"; HIST="$OUT_DIR/history.log"
now=$(/bin/date +%Y-%m-%dT%H:%M:%S%z)
opts=(-o BatchMode=yes -o ConnectTimeout=6 -o ConnectionAttempts=1 -o ServerAliveInterval=10 -o ServerAliveCountMax=2)
probe='l=$(/bin/launchctl list 2>/dev/null); n=$(printf "%s\n" "$l" | /usr/bin/grep -c "com\.joulewise\.night$"); if [ "$n" -gt 0 ]; then echo "armed"; exit 0; fi; w=$(printf "%s\n" "$l" | /usr/bin/grep -c "com\.joulewise\.magistrate$"); c=$(/usr/bin/pgrep -x claude | /usr/bin/wc -l | /usr/bin/tr -d " "); echo "idle watchdog_loaded=$w claude_procs=$c"'
# Local gate: no connection at all while an armed span may be live. The lead (or the
# arming procedure) writes the span's latest end as epoch seconds in $OUT_DIR/armed_until.
ARMED_FILE="$OUT_DIR/armed_until"
if [[ -f $ARMED_FILE ]]; then
  until_s=$(/usr/bin/tr -cd '0-9' < "$ARMED_FILE")
  if [[ -n $until_s && $(/bin/date +%s) -lt $until_s ]]; then
    line="$now ARMED-SKIP until=$until_s"; printf '%s\n' "$line" > "$STATUS"; printf '%s\n' "$line" >> "$HIST"; exit 0
  fi
fi
res=""; via=""
for alias in mbp-ts mbp-wired mbp mbp-ip; do
  if r=$(/usr/bin/ssh "${opts[@]}" "$alias" "$probe" 2>/dev/null); then res=$r; via=$alias; break; fi
done
prev_fails=0; [[ -f $STATUS ]] && prev_fails=$(/usr/bin/sed -n 's/.* fails=\([0-9]*\).*/\1/p' "$STATUS")
if [[ -n $res ]]; then
  line="$now UP via=$via fails=0 $res"
else
  line="$now DOWN fails=$((${prev_fails:-0}+1))"
fi
printf '%s\n' "$line" > "$STATUS.new" && /bin/mv "$STATUS.new" "$STATUS"
printf '%s\n' "$line" >> "$HIST"
# Keep the history bounded.
/usr/bin/tail -n 4000 "$HIST" > "$HIST.new" 2>/dev/null && /bin/mv "$HIST.new" "$HIST"
