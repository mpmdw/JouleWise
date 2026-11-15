import sys
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import *
D = "/Volumes/JW-EXT/scratch/items-rl171"
CH = "**Check (next activation, after the fence is gone):**"
QOLD, QNEW = "be81e466882912f4de1accb8981a1f3e212935295d9769e013aab3919209b353", "366662cecb9794b9d13dbc67dd5721acd2bdf00b5055cc8df70861c07b593fbb"

def line_sub(s, prefix, new):
    lines = s.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(idx) == 1, (prefix, len(idx)); lines[idx[0]] = new; return "\n".join(lines)
def block_sub(s, first_prefix, last_prefix, new):
    lines = s.split("\n"); a = [i for i, l in enumerate(lines) if l.startswith(first_prefix)]
    assert len(a) == 1, (first_prefix, len(a)); b = [i for i, l in enumerate(lines) if l.startswith(last_prefix) and i >= a[0]]
    assert b, last_prefix; lines[a[0]:b[0] + 1] = new.split("\n"); return "\n".join(lines)
LAUNCHER_OLD = "The launcher itself refuses a fence end after 01:50, a t0 between 10:50 and 13:15,"
LAUNCHER_NEW = ("The launcher itself refuses a fence end (worst case + 1,460 s) that passes ten minutes before the window in `--batch-window` "
                "(01:50 for `02:00-02:35`, 13:04 for `13:14-13:15`), a t0 strictly between 10:50 and 13:15 under either argument,")

# ---------------- pilot ----------------
s = open("/Volumes/JW-EXT/scratch/items-rl165/ITEM-dev03-pilot.md").read()
PICK = open(f"{D}/plans/bands/dev03-s01.sh").read().rstrip("\n")
E = [
("drafted by the items-rl165 drafter 2026-11-14 PST, ISSUED", "drafted by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED"),
("EARLIEST: 20 min after dev-02's last span (`dev-02-s03`, or `dev-02-s01` if Sunday's pull did not run) closed with its fence gone, with no further word from the lead (RL-165 §1). LAUNCH on Mon 16 Nov inside that earliest time to 10:50:00, or 13:15:00 to 20:48:10; never between 10:50 and 13:15.",
 "EARLIEST: the close interval (RL-171 §6.1) after dev-02's last span (`dev-02-s03`, or `dev-02-s01` if Sunday's pull did not run) closed with its fence gone, with no further word from the lead (RL-165 §1), and not before 00:00:00 PST Mon 16 Nov (epoch 1794816000). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Wed 18 Nov (LIMIT, epoch 1795075199), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 20:48:10; `13:14-13:15` from 20:48:11 to 02:34:59."),
("deadline: 2026-11-17T02:50:00-08:00", "deadline: 2026-11-19T06:02:00-08:00"),
("or a launch that cannot happen inside (dev-02's close + 20 min)-10:50:00 or 13:15:00-20:48:10 PST Mon 16 Nov: NOTHING",
 "or a launch that cannot happen inside (dev-02's close + the close interval) to 23:59:59 PST Wed 18 Nov (epoch 1795075199), outside 10:50:00-13:15:00: NOTHING"),
("this pilot arms at dev-02's close + 20 min with no further word from the lead. If READY later, the lead stages it in a close interval and the pilot takes the first legal t0, up to Mon 20:48:10.",
 "this pilot arms at dev-02's close + the close interval (RL-171 §6.1) with no further word from the lead. If READY later, the lead stages it in a close interval and the pilot takes the first legal t0 (RL-171 retires the Mon 20:48:10 bound, which was the 01:50 fence; this item's window runs to Wed 23:59:59)."),
("so this pin keeps both of RL-155a §3's bounds.", "so this pin keeps both of RL-155a §3's bounds in code: RL-171 §3 moves off the fence by the argument `13:14-13:15`, and the 10:50-13:15 refusal stays until the qualification pin."),
("`legs.fence_problems` refuses a fence end after 01:50:00 and any t0 strictly between 10:50 and 13:15 (Air `plan` at `2d347f721`: 10:50:01 and 20:48:11 refused, 20:48:10 accepted, `/Volumes/JW-EXT/scratch/items-rl165/plans/plan-x-v11-pilot-*.json`).",
 "`legs.fence_problems` refuses a fence end that passes ten minutes before the window passed in `--batch-window` (01:50:00 for `02:00-02:35`; 13:04:00 for `13:14-13:15`) and, under either argument, any t0 strictly between 10:50 and 13:15 (it reads the soak window from `OS_BATCH_WINDOW_LOCAL`, 11:45-13:15 at this pin, not from the argument). Air `plan` at `2d347f721`, 2026-11-15: with `02:00-02:35` 20:48:10 accepted, 20:48:11 refused, 10:50:00 accepted, 10:50:01 refused; with `13:14-13:15` 08:02:10 accepted, 08:02:11 refused, 13:15:00 accepted (`/Volumes/JW-EXT/scratch/items-rl171/probe/plan/dev03-s01-*`)."),
("Plan for this roster (`plan --batch-window 02:00-02:35`, blackout_clear true; Air at `2d347f721`, `/Volumes/JW-EXT/scratch/items-rl165/plans/plan-dev-03_pilot_L001-L003.json`)",
 "Plan for this roster (`plan` at `2d347f721` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev03-s01.txt`)"),
("  - Forecast t0 05:57:36 (dev-02-s03's expected close 05:37:36 + 20 min): expected end 07:54:40, worst end 10:35:06, fence end 10:59:26.\n  - t0 20:48:10: expected end 22:45:14, worst end 01:25:40, fence end **01:50:00**.\n  - The remainder's window follows from this close: nine legs need t0 by 10:50 or in 13:15-16:18:10 (ITEM-dev03-rest).\n  - Pointer deadline = latest fence end (01:50:00 Tue) + 1 h.",
 "  - **Bands (RL-171 §3; the `pick_arg` function below), every day Mon to Wed:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-20:48:10 `02:00-02:35`; 20:48:11-02:34:59 `13:14-13:15` (which admits three legs up to 08:02:10). A mock span at t0 Mon 00:30 with `13:14-13:15` (L003 across 02:00): rc 0, 3 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev03-s01-alt-00:30/`).\n  - Forecast t0 Mon 03:02:36 (dev-02-s03's expected close 02:57:36 + 5 min), argument `02:00-02:35`: expected end 04:59:40, worst end 07:40:06, fence end 08:04:26.\n  - The remainder (nine legs) can then take any t0 outside 10:50-13:15 by the same argument rule (ITEM-dev03-rest).\n  - Pointer deadline = latest fence end (LIMIT + 18,110 s = Thu 05:01:49) + 1 h."),
("  - Your activation is not inside 01:30-02:40.\n", "  - RL-171 retires \"activation not inside 01:30-02:40\" with the quiet: quiet is the per-leg agent census, process census and rule 5.\n"),
("  - Every `plan` and `launch` passes `--batch-window 02:00-02:35` and `--legs L001,L002,L003` written out;",
 "  - Every `validate-kit`, `plan` and `launch` passes `--batch-window \"$ARG\"` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3) and `--legs L001,L002,L003` written out;"),
('NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior close"; exit 1; }\n{ test "$NOW" -ge 1794825600 && { test "$NOW" -le 1794855000 || { test "$NOW" -ge 1794863700 && test "$NOW" -le 1794890890; }; }; } \\\n  || { echo "STOP: outside (prior close + 20 min)-10:50:00 and 13:15:00-20:48:10 PST Mon 16 Nov; mail the lead"; exit 1; }',
 QUIET_BLOCK + "\n# The launch bands (EARLIEST 1794816000 Mon 00:00:00; LIMIT 1795075199 Wed 23:59:59; none 10:50:01-13:14:59)\n" + PICK +
 '\nNOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }\n' + ARG_SET),
('NOW=$(date +%s); { test "$NOW" -ge 1794825600 && { test "$NOW" -le 1794855000 || { test "$NOW" -ge 1794863700 && test "$NOW" -le 1794890890; }; }; } \\\n  || { echo "STOP: outside 10:50 / 13:15-20:48:10 PST Mon 16 Nov; mail the lead"; exit 1; }\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior close"; exit 1; }',
 ARG_RECHECK + '\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior close"; exit 1; }'),
(LAUNCHER_OLD, LAUNCHER_NEW),
(f"(sha256 `{QOLD}`; `dev-03-s02` L004-L012, and the 3 + 3 + 6 pair `dev-03-s02b` L004-L006 / `dev-03-s03b` L007-L012, each `rerun_of: dev-03-s02`; validate-queue ok at `2d347f721`, four plan ids)",
 f"(sha256 `{QNEW}`, re-written by the items-rl171 builder with `dev-03-s03b`'s not_before 2026-11-17 moved to 2026-11-16; `dev-03-s02` L004-L012, and the 3 + 3 + 6 pair `dev-03-s02b` L004-L006 / `dev-03-s03b` L007-L012, each `rerun_of: dev-03-s02`, which ITEM-dev03-rest withdraws unarmed; validate-queue ok at `2d347f721`, four plan ids, `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`)"),
]
for old, new in E:
    s = count_sub(s, old, new, 1)
s = common(s, CH, None)
open(f"{D}/ITEM-dev03-pilot.md", "w").write(s)

# ---------------- rest (nine legs only) ----------------
s = open("/Volumes/JW-EXT/scratch/items-rl165/ITEM-dev03-rest.md").read()
PICK = open(f"{D}/plans/bands/dev03-s02.sh").read().rstrip("\n")
E = [
("drafted by the items-rl165 drafter 2026-11-14 PST, ISSUED", "drafted by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED"),
("The roster is chosen by the launch time on Mon 16 Nov: **L004-L012 (span `dev-03-s02`, nine legs) if you launch by 10:50:00 or between 13:15:00 and 16:18:10; L004-L006 (span `dev-03-s02b`, three legs; the 3 + 3 + 6 alternate) if you launch after 16:18:10 and by 20:48:10; never between 10:50 and 13:15; after 20:48:10 nothing launches.**",
 "**The roster is L004-L012 (span `dev-03-s02`, nine legs) at every launch time.** RL-171 §3's argument route admits nine legs at every t0 outside 10:50-13:15, so RL-161's 3 + 3 + 6 alternate, which existed only for the 01:50 fence, is not used: `dev-03-s02b` and `dev-03-s03b` are WITHDRAWN UNARMED by this arm record."),
("EARLIEST: 20 min after the dev-03 pilot closed with its fence gone, and only once the lead's hand-read is recorded with L002's G0 released (this item is issued only then).",
 "EARLIEST: the close interval (RL-171 §6.1) after the dev-03 pilot closed with its fence gone, and only once the lead's hand-read is recorded with L002's G0 released (this item is issued only then); not before 00:00:00 PST Mon 16 Nov (epoch 1794816000). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Wed 18 Nov (LIMIT, epoch 1795075199), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 16:18:10; `13:14-13:15` from 16:18:11 to 02:34:59."),
("deadline: 2026-11-17T02:50:00-08:00", "deadline: 2026-11-19T10:32:00-08:00"),
("or a launch that cannot happen inside its roster's window on Mon 16 Nov (02:40-10:50 or 13:15-16:18:10 for nine legs; 16:18:10-20:48:10 for three): NOTHING of this item launches; mail the lead; the lead takes the nine legs at Tue 02:40 by a new item (RL-165 §1), and the standing F0 item applies meanwhile.",
 "or a launch that cannot happen inside the bands below (Mon 00:00:00 to Wed 23:59:59 PST, outside 10:50:00-13:15:00): NOTHING of this item launches; mail the lead; a later t0 needs a new item, and the standing F0 item applies meanwhile."),
("A chosen cut lands on an own-shaped leg (RL-161 §1): the three-leg branch ends at L006, so L007 (own) starts the last span.",
 "A chosen cut lands on an own-shaped leg (RL-161 §1); nine legs in one span make no cut."),
("Exactly one roster runs; the other is WITHDRAWN UNARMED by this arm record (`dev-03-s02b` and `dev-03-s03b` if nine legs arm; `dev-03-s02` if three legs arm).",
 "Only `dev-03-s02` runs; `dev-03-s02b` and `dev-03-s03b` are WITHDRAWN UNARMED by this arm record (RL-171 removes the reason for 3 + 3 + 6)."),
("with `--legs \"$LEGS\"` written out and `--batch-window 02:00-02:35` on every `plan` and `launch`;",
 "with `--legs \"$LEGS\"` written out and `--batch-window \"$ARG\"` on every `validate-kit`, `plan` and `launch` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3);"),
("- **May run:** this span, once, with ONE of the two rosters. **May NOT:** the other roster, `dev-03-s03b` (Tue 02:40, its own item), dev-04,",
 "- **May run:** this span, once, nine legs. **May NOT:** `dev-03-s02b`, `dev-03-s03b`, dev-04,"),
("(32,850 s for nine legs or 16,650 s for three)", "(32,850 s)"),
(f"at `<LEAD FILLS: commit>`, sha256 `{QOLD}`",
 f"at `<LEAD FILLS: commit>`, sha256 `{QNEW}` (the items-rl171 copy: `dev-03-s03b`'s not_before moved from 2026-11-17 to 2026-11-16, nothing else; `validate-queue` ok, `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`)"),
(f"| shasum -a 256 | cut -c1-64)\" = {QOLD}", f"| shasum -a 256 | cut -c1-64)\" = {QNEW}"),
("\n#   L010 (consume) 1467, L011 1251, L012 (consume) 1547; three legs: L004 (capture), L005, L006; $EXPECT; blackout_clear true",
 "\n#   L010 (consume) 1467, L011 1251, L012 (consume) 1547; $EXPECT; blackout_clear true"),
('NOW=$(date +%s); { test "$NOW" -ge 1794825600 && test "$NOW" -le "$LIMIT" && { test "$NOW" -le 1794855000 || test "$NOW" -ge 1794863700; }; } \\\n  || { echo "STOP: past this roster\'s latest t0 or inside 10:50-13:15; do NOT switch rosters after the plan; mail the lead"; exit 1; }\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior close"; exit 1; }',
 ARG_RECHECK + '\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior close"; exit 1; }'),
(LAUNCHER_OLD, LAUNCHER_NEW),
("Record SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the roster withdrawn unarmed,",
 "Record SPAN, LEGS, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, the two spans withdrawn unarmed (`dev-03-s02b`, `dev-03-s03b`),"),
("dev-04's first span arms at the first legal t0 after this close + 20 min (before 10:50, else from 13:15, latest 18:33:10), on its own item,",
 "dev-04's first span arms at the first legal t0 after this close + the close interval (any t0 outside 10:50-13:15; RL-171 retires the 18:33:10), on its own item,"),
(" On the three-leg branch, `dev-03-s03b` (L007-L012) takes Tue 02:40 by its own item and dev-04 follows it.", ""),
]
for old, new in E:
    s = count_sub(s, old, new, 1)
s = line_sub(s, "- **Why (RL-165 §1; RL-158 §3).**",
 "- **Why (RL-165 §1; RL-158 §3; RL-171).** The remainder arms once the hand-read is recorded and L002 released. RL-165 §1 gave it Monday before 10:50 or 13:15-16:18:10, and after 16:18:10 the 3 + 3 + 6 alternate or nine legs at Tue 02:40. RL-171 retires the 01:50 fence and the 02:40 start, and the pin's fence check is met by the argument `13:14-13:15` after 16:18:10 (RL-171 §3), so **nine legs arm at the first t0 outside 10:50-13:15**. dev-03's remainder stays one span of nine (RL-158 §3: an exception to \"at most six\", which keeps 5 of 10 consumers and saves a soak; RL-171 §6.4 favours the longer span). A leg's calendar day is the local date of its span's t0.")
s = block_sub(s, "- **Timing.** Plans at `2d347f721`", "  - Pointer deadline = latest fence end (01:50:00 Tue) + 1 h.",
 "- **Timing.** Plans at `2d347f721` with both arguments (blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-dev03-s02.txt`):\n"
 "  - Nine legs, L004-L012: expected 15,163 s (4.2 h), worst case 32,850 s (9.1 h); fence deadline launch + 34,310 s.\n"
 "  - **Bands (RL-171 §3; the `pick_arg` function below), every day Mon to Wed:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-16:18:10 `02:00-02:35`; 16:18:11-02:34:59 `13:14-13:15` (which admits nine legs up to 03:32:10). Checked: with `02:00-02:35` 16:18:10 accepted and 16:18:11 refused; with `13:14-13:15` 03:32:10 accepted and 03:32:11 refused; 10:50:01 refused under either. A mock span at t0 Mon 00:30 with `13:14-13:15` (L006-L008 across 02:00-02:35): rc 0, 9 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/dev03-s02-alt-00:30/`).\n"
 "  - Forecast t0 Mon 05:19:40 (the pilot's expected close 04:59:40 + a 20-min hand-read), argument `02:00-02:35`: expected end 09:32:23, worst end 14:27:10, fence end 14:51:30.\n"
 "  - If the hand-read ends inside 10:50-13:15, the nine legs arm from 13:15.\n"
 "  - Pointer deadline = latest fence end (LIMIT + 34,310 s = Thu 09:31:49) + 1 h.")
s = block_sub(s, "# The roster is chosen by the launch time (RL-165 §1; RL-161 §4's named alternate 3 + 3 + 6)",
              "else echo \"STOP: outside 02:40-10:50, 13:15-16:18:10 (nine legs)",
 "# The roster: nine legs at every launch time (RL-171 §3; dev-03-s02b and dev-03-s03b are withdrawn unarmed)\n"
 "SPAN=dev-03-s02;  LEGS=L004,L005,L006,L007,L008,L009,L010,L011,L012; DEADLINE_S=34310; WORST_S=32850; EXPECT=\"expected_s 15163, worst_case_s 32850\"\n"
 + QUIET_BLOCK + "\n# The launch bands (EARLIEST 1794816000 Mon 00:00:00; LIMIT 1795075199 Wed 23:59:59; none 10:50:01-13:14:59)\n" + PICK + "\n" + ARG_SET)
s = count_sub(s, 'NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior close"; exit 1; }\n# The roster: nine',
              'NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200 - 1200)) || true   # (the close interval is checked below, once GAP is known)\n# The roster: nine', 1)
s = count_sub(s, ARG_SET, 'NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior close"; exit 1; }\n' + ARG_SET, 1)
s = count_sub(s, 'NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200 - 1200)) || true   # (the close interval is checked below, once GAP is known)\n', '', 1)
s = count_sub(s, 'echo "SPAN $SPAN LEGS $LEGS"   # record it; the other roster is withdrawn unarmed by this arm', 'echo "SPAN $SPAN LEGS $LEGS"   # record it; dev-03-s02b and dev-03-s03b are withdrawn unarmed by this arm', 1)
s = common(s, CH, None)
open(f"{D}/ITEM-dev03-rest.md", "w").write(s)
print("ok")
DB = ("  - **Day balance (coordinator, 11-15; Mythos throughput §3 item 4 as the DEFAULT until the research lead rules; RL-150 R3, RL-149 §2.3: every error is leave-one-day-out, so prompt size must not collect on one day):** at most two development blocks START on this span's local calendar day, counting this block; qualification days hold no development span. ")
s = open(f"{D}/ITEM-dev03-pilot.md").read()
s = count_sub(s, "- **Two separate records after this span (RL-161 §2).**",
              DB.replace("  - ", "- ", 1) + "On the forecast path Monday starts dev-03 (this block) and dev-04, and dev-05 waits for Tuesday; dev-03 does not start on a day that already started two blocks. <LEAD FILLS: the blocks that started on this span's day, from the ledger>.\n- **Two separate records after this span (RL-161 §2).**", 1)
open(f"{D}/ITEM-dev03-pilot.md", "w").write(s)
s = open(f"{D}/ITEM-dev03-rest.md").read()
s = count_sub(s, "legs run and admitted (of 9 or 3);", "legs run and admitted (of 9);", 1)
open(f"{D}/ITEM-dev03-rest.md", "w").write(s)
print("ok3")
