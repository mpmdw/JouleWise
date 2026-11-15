"""RL-172 and the Sol items-rl171 review, applied in place to the built drafts (run after tools/build_*.py).

(a) day law: t0-date windows, the day_gate (receipts census), the day-law text; (f) the session reservation line retired;
(h) the batch-time print; §0 the 300 s floor confirmed; Sol P1 the journal-copy marker gate; Sol P3 the band-change message."""
import re, sys, glob, os
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import count_sub
D = "/Volumes/JW-EXT/scratch/items-rl171"

def sub1(s, old, new, n=1):
    return count_sub(s, old, new, n)
def resub(s, pat, new, n=None, flags=0):
    s2, k = re.subn(pat, new, s, flags=flags)
    if n is not None and k != n:
        raise SystemExit(f"{pat[:80]!r}: {k} matches, expected {n}")
    return s2

QUIET_OLD = ("QUIET_CAMPAIGN_S=1200   # LEAD FILLS (RL-171 §6.1): 300 once the lead has confirmed from the 11-14/11-15 closes that the Check and the\n"
             "                        # hash-verified copy finish inside 5 min (else their longest time + 120 s); 1200 until the lead fills it")
QUIET_NEW = "QUIET_CAMPAIGN_S=300    # RL-171 §6.1, confirmed by RL-172 §0: 300 s after a campaign close; 1,200 s after F0, F2 or any other close"
F0_QUIET_OLD = "QUIET_CAMPAIGN_S=1200   # LEAD FILLS (RL-171 §6.1): 300 once the lead confirms the Check + hash-verified copy finish inside 5 min (else their longest + 120); 1200 until then"
PROSE_Q_OLD = "which the lead fills as 300 s once it has confirmed that the Check and the hash-verified copy finish inside 5 min, else 1,200 s;"
PROSE_Q_NEW = "300 s, confirmed by RL-172 §0;"

from rl172_gates import CLOSE_CENSUS, COPY_GATE, day_gate, OLD_CENSUS_HEAD, OLD_CENSUS_TAIL, RUN_EFF, RUN_EFF_OLD

BATCH = r'''# RL-172 (h): the OS daily batch time computed from the boot time (boot + 12 h + 48 s, then every 24 h). PRINT ONLY: it gates nothing
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in
  ''|*[!0-9]*) echo "batch print: kern.boottime unreadable";;
  *) NEXT_BATCH=$((BOOT + 43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH + 86400)); done
     echo "boot $(date -r "$BOOT" '+%Y-%m-%d %H:%M:%S %Z'); next OS batch $(date -r "$NEXT_BATCH" '+%Y-%m-%d %H:%M:%S %Z') (boot + 12 h + 48 s + whole days)";;
esac      # record this line in the arm record'''

def daylaw(date, what, indent):
    return (f"{indent}- **Day law (RL-172 (a), which replaces the two-starts default):** a day is the local date of a span's t0. "
            "No t0-date holds more than 12 mixed-size development legs (dev-03, dev-04, dev-05) or more than 24 development legs; "
            "qualification t0-dates are disjoint from development t0-dates; hp-01, F0, F2 and v4 sessions are outside the count. "
            f"**This span's t0-date is {date}** ({what}); this item's window admits only that date. A span that misses its date is "
            "re-dated by the lead with a new item, never doubled up. Planned: Sat 7, Sun 11, Mon 18 (dev-02-s03 and dev-03), "
            "Tue 12 (dev-04), Wed 12 (dev-05). Because the queue does not yet enforce dates, `day_gate` counts the development legs "
            "already launched on the t0-date from their receipts and refuses this span past either cap; the committed queues' "
            "`not_before` values are lower bounds only.")

RES_PROSE = re.compile(r"if a session is staged with an intended t0, this span launches only if launch \+ its worst case \([^)]*\) \+ 1,200 s is at or before that t0\.")
RES_NEW = ("RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower "
           "priority arms, and the session takes the next clean close; before that record this span arms as usual.")
RES_SCRIPT_OLD = (': "${SESSION_READY:?Set to yes if a v4 slot session (R1 or W1) is READY and staged for this slot, else no}"\n'
                  ': "${SESSION_T0:?Set to the intended t0 epoch of a staged v4 slot session, or none}"\n'
                  'test "$SESSION_READY" = no || { echo "CEDE: a READY v4 session takes this slot (RL-155 R-A); do not launch; mail the lead"; exit 1; }\n'
                  'test "$SESSION_T0" = none || test $(( $(date +%s) + WORST_S + 1200 )) -le "$SESSION_T0" \\\n'
                  '  || { echo "STOP: worst case + 20 min quiet passes the reserved session t0 (RL-165 §7); mail the lead"; exit 1; }')
RES_SCRIPT_NEW = (': "${SESSION_READY:?Set to yes if the lead has recorded a v4 session (R1 or W1) as READY, else no (RL-172 (f))}"\n'
                  'test "$SESSION_READY" = no || { echo "CEDE: a READY v4 session takes the next clean close (RL-172 (f); RL-155 R-A); do not launch; mail the lead"; exit 1; }\n'
                  '# RL-172 (f): RL-165 §7\'s worst-case reservation (launch + worst + 1,200 s <= SESSION_T0) is retired.')
P3_OLD = 'run Start and check again (new OUT) or mail the lead"; exit 1; }'
P3_NEW = 'do not launch; mail the lead (a re-issue or a re-plan): the argument chosen in Start and check no longer belongs to the launch time"; exit 1; }'

DATES = {  # file: (date label, 3-letter day, earliest epoch, limit epoch, pointer deadline, latest fence text, block plan text, mixed)
 "ITEM-dev02-s02.md": ("Sun 15 Nov", "Sun", None, None, None, None, "dev-02's first half, 6 legs, not mixed-size: Sun 11 with dev-01-s04", False),
 "ITEM-dev02-s03.md": ("Mon 16 Nov", "Mon", None, None, None, None, "dev-02's second half, 6 legs (or dev-02-s01, 12, if RAN=none), not mixed-size: Mon 18 with dev-03", False),
 "ITEM-dev03-pilot.md": ("Mon 16 Nov", "Mon", 1794816000, 1794902399, "2026-11-17T06:02:00-08:00", "Tue 05:01:49", "dev-03, 12 mixed-size legs over the pilot and the remainder", True),
 "ITEM-dev03-rest.md": ("Mon 16 Nov", "Mon", 1794816000, 1794902399, "2026-11-17T10:32:00-08:00", "Tue 09:31:49", "dev-03, 12 mixed-size legs over the pilot and this remainder", True),
 "ITEM-dev04-s01.md": ("Tue 17 Nov", "Tue", 1794902400, 1794988799, "2026-11-18T08:17:00-08:00", "Wed 07:16:49", "dev-04, 12 mixed-size legs over its two spans", True),
 "ITEM-dev04-s02.md": ("Tue 17 Nov", "Tue", 1794902400, 1794988799, "2026-11-18T08:17:00-08:00", "Wed 07:16:49", "dev-04, 12 mixed-size legs over its two spans", True),
 "ITEM-dev05-s01.md": ("Wed 18 Nov", "Wed", 1794988800, 1795075199, "2026-11-19T08:17:00-08:00", "Thu 07:16:49", "dev-05, 12 mixed-size legs over its two spans", True),
 "ITEM-dev05-s02.md": ("Wed 18 Nov", "Wed", 1794988800, 1795075199, "2026-11-19T08:17:00-08:00", "Thu 07:16:49", "dev-05, 12 mixed-size legs over its two spans", True),
}
BANDS = {"ITEM-dev03-pilot.md": "dev03-s01", "ITEM-dev03-rest.md": "dev03-s02", "ITEM-dev04-s01.md": "dev04-s01",
         "ITEM-dev04-s02.md": "dev04-s02", "ITEM-dev05-s01.md": "dev05-s01", "ITEM-dev05-s02.md": "dev05-s02"}
CAMPAIGN = ["ITEM-hp01-s01.md"] + list(DATES)

for f in CAMPAIGN:
    p = f"{D}/{f}"; s = open(p).read()
    # §0: the 300 s floor is ruled
    s = sub1(s, QUIET_OLD, QUIET_NEW)
    s = resub(s, re.escape(PROSE_Q_OLD), PROSE_Q_NEW, None)
    # (f)
    s = resub(s, RES_PROSE.pattern, RES_NEW, None)
    s = sub1(s, RES_SCRIPT_OLD, RES_SCRIPT_NEW)
    s = resub(s, r"SESSION_READY, SESSION_T0, ", "SESSION_READY, ", 1)
    # Sol P3
    s = sub1(s, P3_OLD, P3_NEW)
    # Sol P1 and (a): gate functions after the close-interval block; calls in Start (before the plan) and in Run (after the census)
    anchor = 'echo "close interval GAP $GAP s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)"'
    extra = CLOSE_CENSUS + "\n" + COPY_GATE + ("\n" + day_gate(DATES[f][7]) if f in DATES else "")
    # the Run census becomes close_census (the same selection copy_gate uses)
    i = s.index(OLD_CENSUS_HEAD); j = s.index(OLD_CENSUS_TAIL, i); k = s.index("\n", j)
    s = s[:i] + 'close_census || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; exit 1; }' + s[k:]
    s = sub1(s, anchor, anchor + "\n" + extra)
    calls = "copy_gate || exit 1" + ("\nday_gate || exit 1" if f in DATES else "")
    start_calls = 'effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }\n' + calls
    s = resub(s, r"(\n# The kit: )", "\n# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation\n" + start_calls.replace("\\", "\\\\") + r"\1", 1)
    s = sub1(s, RUN_EFF_OLD, RUN_EFF)
    s = resub(s, r"git -C /Users/edr/code/JouleWise worktree add --detach (\S+) (\S+)", r"test -e \1 || git -C /Users/edr/code/JouleWise worktree add --detach \1 \2   # reused on a retry after a WAIT", 1)
    s = sub1(s, 'echo "host last close $HOST_LAST_CLOSE"', 'echo "host last close $HOST_LAST_CLOSE"\n' + calls)
    # (h): the batch print, once, in Start and check (the arm record)
    i = s.index("sudo -n systemsetup -getusingnetworktime"); j = s.index("\n", i)
    s = s[:j + 1] + BATCH + "\n" + s[j + 1:]
    s = resub(s, r"\. Record ARG, LAST_CLOSE_KIND, GAP, QUIET_CAMPAIGN_S, ",
              ". Record ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), "
              + ("the day_gate line, " if f in DATES else "") + "the batch-time print, ", 1)
    # host-gate prose: the copy marker, and no SSH once armed
    s = resub(s, r"(or a session's close given as OTHER_CLOSE_EPOCH, a whole epoch or an explicit 0\)|\(or OTHER_CLOSE_EPOCH\))",
              r"\1; and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker "
              r"`/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed)",
              1)
    if f in DATES:
        date, d3, early, lim, dl, fence, what, mixed = DATES[f]
        # day-law text: replace the two-starts line, or add it
        m = re.search(r"^( *)- \*\*Day balance \(coordinator[^\n]*$", s, re.M)
        if m:
            s = s[:m.start()] + daylaw(date, what, m.group(1)) + s[m.end():]
        else:
            anchor = "- **What dev-02 is (RL-155 §3.3).**" if f == "ITEM-dev02-s03.md" else "- **Counted.**"
            s = sub1(s, anchor, daylaw(date, what, "") + "\n" + anchor)
        if early is not None:
            s = resub(s, r"23:59:59 PST Wed 18 Nov \(LIMIT, epoch 1795075199\)", f"23:59:59 PST {date} (LIMIT, epoch {lim}; this block's t0-date, RL-172 (a))", 1)
            s = resub(s, r"23:59:59 PST Wed 18 Nov \(epoch 1795075199\)", f"23:59:59 PST {date} (epoch {lim})", None)
            s = resub(s, r"(Mon|Tue) 00:00:00 to Wed 23:59:59 PST", f"{d3} 00:00:00 to {d3} 23:59:59 PST", None)
            s = resub(s, r"this item's window runs to Wed 23:59:59", f"this item's window runs to {d3} 23:59:59, its t0-date", None)
            s = resub(s, r"every day (Mon|Tue) to Wed:\*\*", f"on {date}:**", 1)
            s = resub(s, r"LIMIT \+ ([0-9,]+) s = Thu [0-9:]+\)", f"LIMIT + \\1 s = {fence})", 1)
            s = resub(s, r"deadline: 2026-11-19T[0-9:]+-08:00", f"deadline: {dl}", 1)
            s = resub(s, r"not before 00:00:00 PST (Mon 16|Tue 17) Nov \(epoch [0-9]+[^)]*\)",
                      f"not before 00:00:00 PST {date} (epoch {early}; this block's t0-date, RL-172 (a))", 1)
            # the bands: the regenerated pick_arg function and its comment line
            band = open(f"{D}/plans/bands/{BANDS[f]}.sh").read().rstrip("\n")
            a = s.index("pick_arg() {"); b = s.index("  else echo NONE; fi\n}", a) + len("  else echo NONE; fi\n}")
            s = s[:a] + band + s[b:]
            s = resub(s, r"# The launch bands \(EARLIEST [0-9]+ \w+ 00:00:00; LIMIT [0-9]+ \w+ 23:59:59;",
                      f"# The launch bands (EARLIEST {early} {d3} 00:00:00; LIMIT {lim} {d3} 23:59:59, the t0-date (RL-172 (a));", 1)
            assert "1795075199" not in s or f.startswith("ITEM-dev05"), [l[:120] for l in s.split("\n") if "1795075199" in l]
    open(p, "w").write(s)
    print(f, "ok")

# item-specific text
def edit(f, pairs):
    p = f"{D}/{f}"; s = open(p).read()
    for o, n in pairs:
        s = sub1(s, o, n)
    open(p, "w").write(s)
edit("ITEM-dev03-rest.md", [
 ("dev-04's first span arms at the first legal t0 after this close + the close interval (any t0 outside 10:50-13:15; RL-171 retires the 18:33:10), on its own item,",
  "dev-04's first span arms on its t0-date, Tue 17 Nov (RL-172 (a)), at its first legal t0 after this close + the close interval, on its own item,")])
edit("ITEM-dev04-s01.md", [
 ("both not_before 2026-11-16,", "both not_before 2026-11-16 (a lower bound only: dev-04's t0-date is Tue 17 Nov, RL-172 (a), which this item's window encodes),")])
edit("ITEM-dev04-s02.md", [
 ("both not_before 2026-11-16,", "both not_before 2026-11-16 (a lower bound only: dev-04's t0-date is Tue 17 Nov, RL-172 (a), which this item's window encodes),"),
 ("**Next:** `dev-05-s01` arms on its own item at its first legal t0 from Tue 00:00:00 (day balance: dev-05 is a Tuesday block, as in RL-165's plan; the ladder fills the evening). RL-165 §1's \"dev-05 is not held for Wednesday\" still holds.",
  "**Next:** `dev-05-s01` arms on its own item on its t0-date, Wed 18 Nov (RL-172 (a)); the ladder fills the rest of Tuesday.")])
for f in ("ITEM-dev05-s01.md", "ITEM-dev05-s02.md"):
    p = f"{D}/{f}"; s = open(p).read()
    s = resub(s, r"both not_before 2026-11-17, `expires_at` 2026-11-21T23:59:00-08:00 \(the items-rl171 copy: the builder's not_before 2026-11-18 moved to 2026-11-17: dev-05 is a Tuesday block \(day balance, below\),",
              "both not_before 2026-11-17 (a lower bound only: dev-05's t0-date is Wed 18 Nov, RL-172 (a), which this item's window encodes), `expires_at` 2026-11-21T23:59:00-08:00 (the items-rl171 copy: the builder's not_before 2026-11-18 moved to 2026-11-17 under the earlier two-starts default,", 1)
    s = s.replace("development is complete (60 legs over Sat, Sun, Mon and Tue on the forecast path: 7, 11, 30 and 12, as RL-165's plan)",
                  "development is complete (60 legs: Sat 7, Sun 11, Mon 18, Tue 12, Wed 12, RL-172 (a))")
    s = s.replace("dev-05 is a Tuesday block", "dev-05's t0-date is Wednesday (RL-172 (a))")
    open(p, "w").write(s)

# ---------------- STANDING-F0 ----------------
p = f"{D}/STANDING-F0.md"; s = open(p).read()
s = sub1(s, F0_QUIET_OLD, QUIET_NEW)
s = sub1(s, "(LEAD FILLS below: 300 s once the lead has confirmed from the 11-14 and 11-15 closes that the Check and the copy finish inside 5 min, else their longest time + 120 s; 1,200 s until the lead fills it)",
         "(300 s, confirmed by RL-172 §0)")
s = sub1(s, "   - **R-A (RL-165 §7).** If a v4 slot session is staged, nothing new is armed whose worst case ends after its intended t0: F0 launches only if launch + 12,180 s + 1,200 s is at or before that t0.",
         "   - **R-A (RL-172 (f), which retires RL-165 §7's worst-case reservation).** From the lead's record that a v4 session is READY, nothing of lower priority arms, F0 included; the session takes the next clean close. Before that record F0 arms on its own rules.")
s = sub1(s, "the staged items' window ends, the session reservation, LAST_CLOSE_KIND)", "the staged items' window ends, the session READY record, LAST_CLOSE_KIND, the restart hold)")
s = sub1(s, '"${COUNTED_LATEST:?}" "${SESSION_T0:?}" <<\'PY\'', '"${COUNTED_LATEST:?}" none <<\'PY\'')
s = sub1(s, 'if sys.argv[3] != "none" and now + 12180 + 1200 > float(sys.argv[3]): sys.exit("STOP: worst case + 20 min passes the reserved session t0 (RL-165 §7)")\n', "")
s = sub1(s, "#   SESSION_READY, SESSION_T0, COUNTED_LATEST   R-A, the reservation and rule 7", "#   SESSION_READY, COUNTED_LATEST   R-A (the lead's READY record, RL-172 (f)) and rule 7; RESTART_PENDING  RL-172 (h)")
s = sub1(s, "SESSION_READY, SESSION_T0 and COUNTED_LATEST", "SESSION_READY, RESTART_PENDING, COUNTED_LATEST, the journal-copy line and the batch-time print")
s = sub1(s, '  # R-A: a READY v4 session takes the slot (RL-155 R-A; RL-165 §7)', '  # R-A: from the lead\'s READY record a v4 session takes the next clean close (RL-172 (f); RL-155 R-A)')
# the restart hold (RL-172 (h)) and the copy gate, inside f0_eligible after the close interval
f0_anchor = '  test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval $GAP s after the latest close ($HOST_LAST_CLOSE; RL-171 §6.1)"; return 1; }'
s = sub1(s, f0_anchor, f0_anchor + '''
  copy_gate || return 1
  # RL-172 (h): on the restart day no F0 arms after 12:00 until the lead records the restart done
  case "${RESTART_PENDING:-}" in yes) test "$(date +%H)" -lt 12 || { echo "HOLD: the RL-172 (h) restart is pending today; no F0 after 12:00 until it is recorded done"; return 1; };; no) ;; *) echo "STOP: set RESTART_PENDING to yes (restart due today, not yet done) or no"; return 1;; esac''')
s = sub1(s, "# THE COMPLETE ELIGIBILITY CHECK (rules 1-8,", CLOSE_CENSUS + "\n" + COPY_GATE + "\n\n# THE COMPLETE ELIGIBILITY CHECK (rules 1-8,")
i = s.index("  " + OLD_CENSUS_HEAD); j = s.index("  " + OLD_CENSUS_TAIL, i); k = s.index("\n", j)
s = s[:i] + '  close_census || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; return 1; }' + s[k:]
s = sub1(s, "\n".join("  " + l for l in RUN_EFF_OLD.replace("exit 1", "return 1").split("\n")),
         "\n".join("  " + l for l in RUN_EFF.replace("exit 1", "return 1").split("\n")))
i = s.index("sudo -n systemsetup -getusingnetworktime"); j = s.index("\n", i)
s = s[:j + 1] + BATCH + "\n" + s[j + 1:]
s = sub1(s, "8. **Host state.**", "8. **Host state and the restart (RL-172 (h)).** The MBP restarts once at 14:08 (± 15 min) on the first day no span is armed then (Sunday if dev-02's first half has closed): **no F0 arms after 12:00 that day until the lead records the restart done** (RESTART_PENDING). The lead's journal-copy marker is required after a campaign close, as for the campaign items (Sol items-rl171 P1). **Host state.**")
open(p, "w").write(s)
print("STANDING-F0.md ok")

# a WAIT (copy gate, close interval, day gate) is retried at the next activation by running Start and check again: the
# worktree is reused (above) and the kit file is re-written from git and its sha asserted, so neither blocks the retry
for f in CAMPAIGN:
    p = f"{D}/{f}"; s = open(p).read()
    s = sub1(s, 'test ! -e "$KIT" || { echo "STOP: KIT exists"; exit 1; }',
             'test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"')
    open(p, "w").write(s)
print("retry-safe ok")
for f in ("ITEM-dev04-s01.md", "ITEM-dev04-s02.md", "ITEM-dev05-s01.md", "ITEM-dev05-s02.md"):
    p = f"{D}/{f}"; s = open(p).read()
    b = f.split("-")[1][:5].replace("dev0", "dev-0")
    date = "Tue 17 Nov" if "dev04" in f else "Wed 18 Nov"
    s = resub(s, r'follows at its first legal t0 \(RL-165 §1: "dev-04 and dev-05 follow at their first legal t0"; dev-05 is not held for Wednesday\)\.',
              f'follows at its first legal t0 on its own t0-date, {date} (RL-172 (a): each mixed-size block gets its own date; this amends RL-165 §1\'s "dev-04 and dev-05 follow at their first legal t0").', 1)
    open(p, "w").write(s)
print("why ok")
