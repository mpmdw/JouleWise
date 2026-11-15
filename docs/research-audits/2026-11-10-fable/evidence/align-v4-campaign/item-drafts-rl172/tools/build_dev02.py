import sys
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import *
D = "/Volumes/JW-EXT/scratch/items-rl171"
CH = "**Check (next activation, after the fence is gone):**"
DRAFTED_OLD = "drafted by the dev02-ready builder and finalized for RL-165 §2 by the items-rl165 drafter 2026-11-14 PST, ISSUED"
DRAFTED_NEW = "drafted by the dev02-ready builder, finalized for RL-165 §2 by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED"
F2_OLD = "  - Your activation is not inside 01:30-02:40 (Mythos dev-02 F2).\n"
F2_NEW = "  - RL-171 retires Mythos dev-02 F2's \"activation not inside 01:30-02:40\" with the quiet: quiet is the per-leg agent census, process census and rule 5, and your own checks end before the launch (you exit at once).\n"

# ---------------- dev-02-s02 (Sunday half) ----------------
s = open("/Volumes/JW-EXT/scratch/items-rl165/ITEM-dev02-s02.md").read()
PICK = open(f"{D}/plans/bands/dev02-s02.sh").read().rstrip("\n")
E = [
(DRAFTED_OLD, DRAFTED_NEW),
("EARLIEST: 20 min after the last close on Sunday (the last hp-01 span that runs on Sunday, or `dev-01-s04` if none does) with its fence gone. LAUNCH inside that earliest time to 10:50:00, or 13:15:00 to 18:33:10, PST Sun 15 Nov; never between 10:50 and 13:15 and never after 18:33:10 (6 + 6 only: after 18:33:10 there is no Sunday pull, RL-165 §2).",
 "EARLIEST: the close interval (RL-171 §6.1) after the last close on Sunday (the last hp-01 span that runs on Sunday, or `dev-01-s04` if none does) with its fence gone, and not before 00:00:00 PST Sun 15 Nov (epoch 1794729600). LAUNCH as soon as every gate holds, at any hour of Sun 15 Nov up to 23:59:59 PST (LIMIT, epoch 1794815999: the 6 + 6 split's Sunday half, RL-165 §2; RL-171 retires the 18:33:10 that was the 01:50 fence), except 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 19:07:30; `13:14-13:15` before 02:35:00 and after 19:07:30."),
("deadline: 2026-11-16T02:50:00-08:00", "deadline: 2026-11-16T08:17:00-08:00"),
("or a launch that cannot happen inside (the last Sunday close + 20 min)-10:50:00 or 13:15:00-18:33:10 PST Sun 15 Nov: NOTHING",
 "or a launch that cannot happen inside (the last Sunday close + the close interval) to 23:59:59 PST Sun 15 Nov (epoch 1794815999), outside 10:50:00-13:15:00: NOTHING"),
("dev-02 may run as 6 + 6: L001-L006 on Sunday by 18:33:10 (this span), L007-L012 at Mon 02:40 (`dev-02-s03`, its own item).",
 "dev-02 may run as 6 + 6: L001-L006 on Sunday (this span), L007-L012 on Monday (`dev-02-s03`, its own item). RL-171 retires the two clock values in RL-165 §2's sentence: 18:33:10 was the 01:50 fence bound and 02:40 was the quiet's end. The calendar split stays (RL-171 §2: the calendar-day rules stand)."),
("**6 + 6 only:** if 18:33:10 is missed, filler P does not take dev-02 on Sunday,",
 "**6 + 6 only:** if this span cannot launch on Sunday (by 23:59:59), filler P does not take dev-02 on Sunday,"),
("Plan for this roster (`plan --batch-window 02:00-02:35`, blackout_clear true; reproduced on the Air at `b4b6aeb19`, `/Volumes/JW-EXT/scratch/items-rl165/plans/plan-dev-02-s02_L001-L006.json` and `plan-x-dev02-s02-Sun183310.json`)",
 "Plan for this roster (`plan` at `b4b6aeb19` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev02-s02.txt` and `probe/plan/`)"),
("  - Forecast t0 13:24:27 (hp-01's third span's expected close + 20 min): expected end 16:22:03, worst end 20:16:57, fence end 20:41:17.\n  - t0 18:33:10: expected end 21:30:46, worst end 01:25:40, fence end **01:50:00** (RL-155a §3; 18:33:11 overshoots).\n  - No launch between 10:50 and 13:15 (RL-155a §3: the soak path waits out 11:45-13:15 unbudgeted).",
 "  - **Bands (RL-171 §3; the `pick_arg` function below):** 00:00:00-02:34:59 `13:14-13:15`; 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-19:07:30 `02:00-02:35`; 19:07:31-23:59:59 `13:14-13:15` (`02:00-02:35` refuses six legs from 19:07:31 to 02:34:59; `13:14-13:15` admits them from 13:15:00 to 06:21:30). `validate-kit` is ok with either argument. A mock span at t0 00:30 with `13:14-13:15` (six legs, L003-L005 across 02:00-02:35): rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev02-s02-alt-00:30/`). The mock does not model the soak path's 11:45-13:15 wait.\n  - Forecast t0 10:19:27 (hp-01-s03's expected close 10:14:27 + 5 min), argument `02:00-02:35`: expected end 13:17:03, worst end 17:11:57, fence end 17:36:17. With a 20-min interval the forecast t0 (10:44:27 + 20 min) falls in 10:50-13:15 and moves to 13:15:00.\n  - t0 23:59:59 (LIMIT), argument `13:14-13:15`: worst end Mon 06:52:29, fence end 07:16:49.\n  - No launch between 10:50 and 13:15: RL-171 calls it a defect of this pin, not a rule, but its soak path still waits out 11:45-13:15 unbudgeted (`OS_BATCH_WINDOW_LOCAL` at `b4b6aeb19` is 11:45-13:15)."),
("  - Pointer deadline = latest fence end (01:50:00 Mon) + 1 h.", "  - Pointer deadline = latest fence end (LIMIT + 26,210 s = 07:16:49 Mon) + 1 h."),
(F2_OLD, F2_NEW),
("  - Every `plan` and `launch` passes `--batch-window 02:00-02:35` and `--legs L001,L002,L003,L004,L005,L006` written out,",
 "  - Every `validate-kit`, `plan` and `launch` passes `--batch-window \"$ARG\"` (chosen once in Start and check by the launch time and re-checked in Run; RL-171 §3) and `--legs L001,L002,L003,L004,L005,L006` written out,"),
('NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior close"; exit 1; }\n{ test "$NOW" -ge 1794739200 && { test "$NOW" -le 1794768600 || { test "$NOW" -ge 1794777300 && test "$NOW" -le 1794796390; }; }; } \\\n  || { echo "STOP: outside (prior close + 20 min)-10:50:00 and 13:15:00-18:33:10 PST Sun 15 Nov: no Sunday pull; mail the lead"; exit 1; }',
 QUIET_BLOCK + "\n# The launch bands (EARLIEST 1794729600 Sun 00:00:00; LIMIT 1794815999 Sun 23:59:59; none 10:50:01-13:14:59)\n" + PICK +
 '\nNOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }\n' + ARG_SET),
('NOW=$(date +%s); { test "$NOW" -ge 1794739200 && { test "$NOW" -le 1794768600 || { test "$NOW" -ge 1794777300 && test "$NOW" -le 1794796390; }; }; } \\\n  || { echo "STOP: outside 10:50 / 13:15-18:33:10 PST Sun 15 Nov: no Sunday pull; mail the lead"; exit 1; }\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior close"; exit 1; }',
 ARG_RECHECK + '\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior close"; exit 1; }'),
("(close leaves no staged item within 2 h 30 min: the next counted span is Mon 02:40)",
 "(close leaves no staged item within 2 h 30 min: the next counted span, `dev-02-s03`, is the Monday half and cannot arm before Mon 00:00:00)"),
]
for old, new in E:
    s = count_sub(s, old, new, 1)
s = common(s, CH, None)
open(f"{D}/ITEM-dev02-s02.md", "w").write(s)

# ---------------- dev-02-s03 / s01 (Monday) ----------------
s = open("/Volumes/JW-EXT/scratch/items-rl165/ITEM-dev02-s03.md").read()
P6 = open(f"{D}/plans/bands/dev02-s03.sh").read().rstrip("\n").replace("pick_arg()", "pick_arg6()")
P12 = open(f"{D}/plans/bands/dev02-s01.sh").read().rstrip("\n").replace("pick_arg()", "pick_arg12()")
E = [
(DRAFTED_OLD, DRAFTED_NEW),
("**if `dev-02-s02` (L001-L006) ran on Sunday, arm `dev-02-s03` = L007-L012 and launch between 02:40 and 10:50 or between 13:15 and 18:33:10; if it never armed, arm `dev-02-s01` = L001-L012 (the queued twelve-leg span) and launch between 02:40 and 10:50 or between 13:15 and 14:03:10.**",
 "**if `dev-02-s02` (L001-L006) ran on Sunday, arm `dev-02-s03` = L007-L012; if it never armed, arm `dev-02-s01` = L001-L012 (the queued twelve-leg span).** EARLIEST: 00:00:00 PST Mon 16 Nov (epoch 1794816000; this is dev-02's Monday span, RL-165 §2) and the close interval after the latest close (RL-171 §6.1). LAUNCH as soon as every gate holds, at any hour of Mon 16 Nov up to 23:59:59 PST (LIMIT, epoch 1794902399), except 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted) and, for twelve legs only, 01:51:31-02:34:59 (both arguments refuse it). The batch-window argument follows the launch time and the roster (RL-171 §3; bands below)."),
(" Your activation starts no earlier than 02:40 PST Mon 16 Nov. Never launch between 10:50 and 13:15.", " Never launch between 10:50 and 13:15."),
("deadline: 2026-11-17T02:50:00-08:00", "deadline: 2026-11-17T12:47:00-08:00"),
("or a launch that cannot happen inside the chosen roster's window on Mon 16 Nov (02:40-10:50, or 13:15 to 18:33:10 for six legs or 14:03:10 for twelve): NOTHING",
 "or a launch that cannot happen inside the chosen roster's bands on Mon 16 Nov (00:00:00 to 23:59:59 outside 10:50:00-13:15:00; twelve legs also not 01:51:31-02:34:59): NOTHING"),
("dev-02 runs as 6 + 6 when Sunday's pull ran: L007-L012 here at Mon 02:40. If the Sunday pull did not run (18:33:10 missed, or the append was refused),",
 "dev-02 runs as 6 + 6 when Sunday's pull ran: L007-L012 here, on Monday (RL-171 retires the 02:40 start; the calendar split stays). If the Sunday pull did not run (Sunday missed, or the append was refused),"),
("Plans at `b4b6aeb19` (`plan --batch-window 02:00-02:35`, blackout_clear true; reproduced on the Air, `/Volumes/JW-EXT/scratch/items-rl165/plans/plan-dev-02-s03_L007-L012.json` and `plan-x-dev02-s01-12-Mon0240.json`):",
 "Plans at `b4b6aeb19` with both arguments (blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev02-s03.txt`, `verify-dev02-s01.txt` and `probe/plan/`):"),
("fence deadline launch + 26,210 s. At t0 02:40: expected end 05:37:36, worst end 09:32:30, fence end 09:56:50. Latest t0 **18:33:10** (fence end 01:50:00 Tue).",
 "fence deadline launch + 26,210 s. Bands: 00:00:00-02:34:59 `13:14-13:15`; 02:35:00-10:50:00 `02:00-02:35`; 13:15:00-19:07:30 `02:00-02:35`; 19:07:31-23:59:59 `13:14-13:15`. Forecast t0 00:00:00 (the last Sunday F0's expected close 23:20:57 + 20 min, then the calendar), argument `13:14-13:15`: expected end 02:57:36, worst end 06:52:30, fence end 07:16:50. A mock span at t0 00:30 with `13:14-13:15` (L009-L011 across 02:00-02:35): rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev02-s03-alt-00:30/`)."),
("At t0 02:40: expected end 07:42:42, worst end 14:02:30, fence end 14:26:50. Latest t0 **14:03:10** (fence end 01:50:00 Tue); a 14:30 launch is NOT allowed (fence end 02:16:50).",
 "Bands: 00:00:00-01:51:30 `13:14-13:15` (it refuses 01:51:31 on, the worst case meeting 13:14 the same day); none 01:51:31-02:34:59 (`02:00-02:35` refuses it too); 02:35:00-10:50:00 `02:00-02:35`; 13:15:00-14:37:30 `02:00-02:35`; 14:37:31-23:59:59 `13:14-13:15`. RL-171 retires the 14:03:10 (the 01:50 fence). A mock span at t0 00:30 with `13:14-13:15` (twelve legs): rc 0, 12 legs, no stops (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev02-s01-alt-00:30/`)."),
("  - No launch between 10:50 and 13:15 (RL-155a §3). The epoch is the gate, in both blocks (Mythos dev-02 F2).\n  - Pointer deadline = latest fence end (01:50:00 Tue) + 1 h.",
 "  - No launch between 10:50 and 13:15: RL-171 calls it a defect of this pin, not a rule, but its soak path still waits out 11:45-13:15 unbudgeted. The epoch is the gate, in both blocks (Mythos dev-02 F2).\n  - Pointer deadline = latest fence end (LIMIT 23:59:59 + 42,410 s for twelve legs = Tue 11:46:49) + 1 h."),
("  - Your activation starts no earlier than 02:40 PST Mon 16 Nov, so that your own checks are not load inside the quiet (Mythos dev-02 F2). The epoch gate in \"Start and check\" fails an earlier start.\n",
 "  - RL-171 retires Mythos dev-02 F2's \"activation no earlier than 02:40\" with the quiet: quiet is the per-leg agent census, process census and rule 5, and your own checks end before the launch (you exit at once). The epoch gate in \"Start and check\" still fails a start before Mon 00:00:00.\n"),
("  - Every `plan` and `launch` passes `--batch-window 02:00-02:35` and `--legs` written out,",
 "  - Every `validate-kit`, `plan` and `launch` passes `--batch-window \"$ARG\"` (chosen once in Start and check by the launch time and the roster, re-checked in Run; RL-171 §3) and `--legs` written out,"),
('  dev-02-s02) SPAN=dev-02-s03; LEGS=L007,L008,L009,L010,L011,L012; LATEST=1794882790; DEADLINE_S=26210;',
 '  dev-02-s02) SPAN=dev-02-s03; LEGS=L007,L008,L009,L010,L011,L012; PICK=pick_arg6; DEADLINE_S=26210;'),
('  none)       SPAN=dev-02-s01; LEGS=L001,L002,L003,L004,L005,L006,L007,L008,L009,L010,L011,L012; LATEST=1794866590; DEADLINE_S=42410;',
 '  none)       SPAN=dev-02-s01; LEGS=L001,L002,L003,L004,L005,L006,L007,L008,L009,L010,L011,L012; PICK=pick_arg12; DEADLINE_S=42410;'),
(': "${RAN:?Set RAN to dev-02-s02',
 "# The launch bands (EARLIEST 1794816000 Mon 00:00:00; LIMIT 1794902399 Mon 23:59:59; none 10:50:01-13:14:59)\n" + P6 + "\n" + P12 + "\npick_arg() { \"$PICK\" \"$1\"; }\n" + QUIET_BLOCK + '\n: "${RAN:?Set RAN to dev-02-s02'),
('NOW=$(date +%s); { test "$NOW" -ge 1794825600 && { test "$NOW" -le 1794855000 || { test "$NOW" -ge 1794863700 && test "$NOW" -le "$LATEST"; }; }; } \\\n  || { echo "STOP: outside 02:40-10:50 and 13:15-latest PST Mon 16 Nov for $SPAN; mail the lead"; exit 1; }',
 'NOW=$(date +%s)\n' + ARG_SET),
('# The window and the campaign dependency, last of all\nNOW=$(date +%s); { test "$NOW" -ge 1794825600 && { test "$NOW" -le 1794855000 || { test "$NOW" -ge 1794863700 && test "$NOW" -le "$LATEST"; }; }; } \\\n  || { echo "STOP: outside this roster\'s window; do NOT switch rosters after the plan; mail the lead"; exit 1; }',
 '# The band, last of all (do NOT switch rosters after the plan)\n' + ARG_RECHECK),
]
for old, new in E:
    s = count_sub(s, old, new, 1)
s = common(s, CH, None)
open(f"{D}/ITEM-dev02-s03.md", "w").write(s)
print("ok")
s = open(f"{D}/ITEM-dev02-s03.md").read()
s = count_sub(s, "F2: the epoch gate in both blocks and no activation before 02:40;", "F2: the epoch gate in both blocks (its \"no activation before 02:40\" is retired by RL-171);", 1)
s = count_sub(s, "the dev-03 pilot arms at this span's close + 20 min with no further word from the lead,", "the dev-03 pilot arms at this span's close + the close interval (RL-171 §6.1) with no further word from the lead,", 1)
open(f"{D}/ITEM-dev02-s03.md", "w").write(s)
print("ok2")
s = open(f"{D}/ITEM-dev02-s02.md").read()
s = count_sub(s, "- **What dev-02 is (RL-155 §3.3).**",
 "- **Day balance (coordinator, 11-15; Mythos throughput §3 item 4 as the DEFAULT until the research lead rules; RL-150 R3, RL-149 §2.3: every error is leave-one-day-out):** at most two development blocks START on this span's local calendar day, counting this block; qualification days hold no development span. Sunday starts dev-02 only (dev-01 started Saturday; hp-01 is not development). The 6 + 6 split keeps dev-02's legs on Sunday and Monday, as RL-165's plan had them: Sat 7, Sun 11, Mon 30, Tue 12 development legs. <LEAD FILLS: the blocks that started on this span's day, from the ledger>.\n- **What dev-02 is (RL-155 §3.3).**", 1)
open(f"{D}/ITEM-dev02-s02.md", "w").write(s)
print("ok4")
