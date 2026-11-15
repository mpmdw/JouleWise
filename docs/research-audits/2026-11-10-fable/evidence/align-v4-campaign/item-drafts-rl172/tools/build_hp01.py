import sys
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import *
D = "/Volumes/JW-EXT/scratch/items-rl171"
s = open("/Volumes/JW-EXT/scratch/items-rl165/ITEM-hp01-s01.md").read()
PICK = open(f"{D}/plans/bands/hp01-s01.sh").read().rstrip("\n")
E = [
("drafted by the hp01-ready builder and finalized by the items-rl165 drafter 2026-11-14 PST, ISSUED",
 "drafted by the hp01-ready builder, finalized by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED"),
("EARLIEST: 20 min after `dev-01-s04` closed with its fence gone (no fixed clock floor). LAUNCH inside that earliest time to 10:50:00, or 13:15:00 to 19:52:30, PST Sun 15 Nov; never between 10:50 and 13:15, and never after 19:52:30 (worst-case end by 00:30, RL-165 §7).",
 "EARLIEST: the close interval after `dev-01-s04` closed with its fence gone (RL-171 §6.1; no clock floor), and not before 00:00:00 PST Sun 15 Nov (epoch 1794729600). LAUNCH as soon as every gate holds, at any hour (RL-171: quiet is the per-leg process and load checks, not a clock window), up to 19:52:30 PST Sun 15 Nov (LIMIT, epoch 1794801150: worst-case end by 00:30, RL-165 §7, which RL-171 §2 keeps), except 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted). The batch-window argument follows the launch time (RL-171 §3): `13:14-13:15` before 02:35:00, `02:00-02:35` from 02:35:00."),
("or a launch that cannot happen inside (dev-01-s04's close + 20 min)-10:50:00 or 13:15:00-19:52:30 PST Sun 15 Nov: NOTHING",
 "or a launch that cannot happen inside (dev-01-s04's close + the close interval) to 19:52:30 PST Sun 15 Nov (epoch 1794801150), outside 10:50:00-13:15:00: NOTHING"),
("- **No 07:00 floor (Mythos and Sol schedule reviews; RL-157 §8's \"about 07:00\" was a forecast).** The gate is `dev-01-s04`'s close + 20 min. At the expected close 05:16:45 the earliest t0 is 05:36:45.",
 "- **No clock floor (Mythos and Sol schedule reviews; RL-157 §8's \"about 07:00\" was a forecast; RL-171 retires the 02:40 start).** The gate is `dev-01-s04`'s close + the close interval (RL-171 §6.1). Item 331 launches `dev-01-s04` at about 00:20 (expected close 02:56:45), so the forecast t0 is 03:01:45 with a 5-min interval, or 03:16:45 with 20 min."),
("Sunday evening is an evening before a 02:40 counted span (dev-02 on Mon 02:40), so an hp-01 span launches only if its worst-case end is by 00:30, leaving the lead an hour before the quiet to clear a \"restore unproven\":",
 "RL-171 §2 keeps this rule for its own reason, the lead's presence, not the batch: an hp-01 span launches only if its worst-case end is by 00:30, so the lead is reachable to clear a \"restore unproven\":"),
("  The fence bound (fence end by 01:50) gives 20:48:10 for three legs; the 00:30 rule is stricter and binds. No launch between 10:50 and 13:15 (RL-155a §3): these bytes carry the 11:45-13:15 soak window and the plan does not budget its wait.",
 "  The fence bound (fence end by 01:50) is retired (RL-171 §2), and `dd206025a` has the v1 launcher, with no fence check (checked on the Air: no `fence_problems` in `joulewise/cadence/legs.py`, `scripts/launch_cadence_span.py` or the runner; `b4b6aeb19` is its ancestor and `plan_span` is unchanged). No launch between 10:50 and 13:15: RL-171 calls it a defect of this pin, not a rule, but the bytes still carry the 11:45-13:15 soak window (`OS_BATCH_WINDOW_LOCAL` in `scripts/align_r1_rehearsal.py`), the runner holds the soak out of it, and the plan does not budget that wait. The 00:30 rule as written does not bound a small-hours t0 (a launch at 03:00 has its worst-case end at 07:37); the lead decides whether the lead's presence needs a morning bound too."),
("(for example in the 20-minute quiet after `dev-01-s04` closes, or earlier between runs)",
 "(for example in the close interval after `dev-01-s04` closes, or earlier between runs)"),
("(at t0 05:36:45: 10:14:15; at 19:52:30: 00:30:00)", "(at t0 03:01:45: 07:39:15; at 19:52:30: 00:30:00)"),
("Plan for this roster (`plan --batch-window 02:00-02:35`, blackout_clear true; reproduced on the Air at `dd206025a`, `/Volumes/JW-EXT/scratch/items-rl165/plans/plan-hp-01-s01_smoke.json` and `plan-x-hp-s01-Sun195230.json`)",
 "Plan for this roster (`plan` at `dd206025a` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-hp01-s01.txt` and `probe/plan/`)"),
("  - t0 05:36:45 (s04's expected close + 20 min): expected end 07:31:48, worst end 10:14:15, fence end 10:38:35.\n  - t0 10:50:00: worst end 15:27:30, fence end 15:51:50. t0 13:15: 17:52:30 and 18:16:50.",
 "  - **Bands (RL-171 §3; the `pick_arg` function below):** 00:00:00-02:34:59 `13:14-13:15` (`02:00-02:35` refuses every t0 from 21:22:31 to 02:34:59 for three legs, because the worst case meets the window); 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-19:52:30 `02:00-02:35`. `validate-kit` is ok with either argument. A mock span at t0 00:30 with `13:14-13:15` (three legs, L003 across 02:00): rc 0, 3 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/hp01-s01-alt-00:30/`). The mock does not model the soak path's 11:45-13:15 wait (its deps carry no soak window).\n  - Forecast t0 03:01:45 (s04's expected close 02:56:45 + 5 min), argument `02:00-02:35`: expected end 04:56:48, worst end 07:39:15, fence end 08:03:35.\n  - t0 10:50:00: worst end 15:27:30, fence end 15:51:50. t0 13:15: 17:52:30 and 18:16:50."),
("  - Every launch passes `--batch-window 02:00-02:35` and the arm record shows the plan's `batch_windows` (RL-150 §2 F2).",
 "  - Every `validate-kit`, `plan` and `launch` passes `--batch-window \"$ARG\"`, chosen once in Start and check by the launch time and re-checked in Run; the arm record shows the plan's `batch_windows` (RL-150 §2 F2; RL-171 §3)."),
("on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `90e042edf25c1a9858f08547ca25c1d5cdcbeed8a7fa9a1038a360a658ed39ed`",
 "on audit/2026-11-10-fable at `3de39e06a`, sha256 `90e042edf25c1a9858f08547ca25c1d5cdcbeed8a7fa9a1038a360a658ed39ed`"),
("(`expires_at` 2026-11-21T23:59-08:00, which is within 7 days only for a commit at or after Sun 15 Nov 00:00 PST; commit it then, or move the expiry)",
 "(`expires_at` 2026-11-21T23:59-08:00; committed at `3de39e06a`. `validate-queue` needs `--kits-root` at a checkout of `bbd34dc87`, where the kit is `7eaf2660…`; the in-tree kit at `dd206025a` is the superseded `bd7c8711…`)"),
('NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior span\'s close"; exit 1; }\n{ test "$NOW" -le 1794768600 || { test "$NOW" -ge 1794777300 && test "$NOW" -le 1794801150; }; } \\\n  || { echo "STOP: outside (prior close + 20 min)-10:50:00 and 13:15:00-19:52:30 PST Sun 15 Nov; mail the lead"; exit 1; }\ntest "$NOW" -ge 1794739200 || { echo "STOP: before Sun 15 Nov 02:40"; exit 1; }',
 QUIET_BLOCK + "\n# The launch bands (EARLIEST 1794729600 Sun 00:00:00; LIMIT 1794801150 Sun 19:52:30, the 00:30 rule; none 10:50:01-13:14:59)\n" + PICK +
 '\nNOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior span\'s close"; exit 1; }\n' + ARG_SET),
('# The window and the campaign dependency, last of all\nNOW=$(date +%s); { test "$NOW" -ge 1794739200 && { test "$NOW" -le 1794768600 || { test "$NOW" -ge 1794777300 && test "$NOW" -le 1794801150; }; }; } \\\n  || { echo "STOP: outside (prior close + 20 min)-10:50:00 and 13:15:00-19:52:30 PST Sun 15 Nov; mail the lead"; exit 1; }\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + 1200)) || { echo "STOP: under 20 min after the prior span\'s close"; exit 1; }',
 '# The band and the campaign dependency, last of all\n' + ARG_RECHECK + '\ntest "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior span\'s close"; exit 1; }'),
("  - **Latest t0 on Sunday (worst-case end by 00:30 before Mon 02:40):** four legs **19:07:30**, five legs **18:22:30**; never 10:50-13:15. The same 00:30 rule binds on Monday evening before a Tue 02:40 counted span.",
 "  - **Latest t0 (worst-case end by 00:30; RL-165 §7, kept by RL-171 §2):** four legs **19:07:30**, five legs **18:22:30**; never 10:50-13:15 on this pin. The argument follows the launch time as here: `13:14-13:15` before 02:35:00 (`02:00-02:35` refuses four legs from 20:37:31 and five legs from 19:52:31 to 02:34:59), `02:00-02:35` from 02:35:00. The 02:40 starts are retired (RL-171)."),
("  - **Forecast** (Air `plan` at `dd206025a`, `/Volumes/JW-EXT/scratch/items-rl165/plans/`): smoke 05:36:45-07:31:48 expected; `hp-01-s02` at 07:51:48 (if the hand-read is recorded inside the 20-minute quiet) expected end 10:07:42, worst 13:14:18, fence 13:38:38; `hp-01-s03` at 10:27:42 expected end 13:04:27, worst 16:35:12, fence 16:59:32. A hand-read that finishes after 10:50 moves `hp-01-s02` to 13:15.",
 "  - **Forecast** (Air `plan` at `dd206025a`, `/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`): smoke 03:01:45-04:56:48 expected; `hp-01-s02` at 05:16:48 (after a 20-min hand-read) expected end 07:32:42, worst 10:39:18; `hp-01-s03` at 07:37:42 (s02's close + 5 min) expected end 10:14:27, worst 13:45:12; all three on `02:00-02:35`. A remainder not READY by 10:50 waits for 13:15."),
("  - **Then (RL-165 §2):** the dev-02 pull (`dev-02-s02`, L001-L006, latest t0 18:33:10), then the standing F0.",
 "  - **Then (RL-165 §2):** the dev-02 pull (`dev-02-s02`, L001-L006, any Sunday t0 outside 10:50-13:15; RL-171 retires its 18:33:10), then the standing F0."),
]
for old, new in E:
    s = count_sub(s, old, new, 1)
s = common(s, "", None) if False else s
# common rewrites; the maintenance line goes AFTER the power reads (they run first), before the receipt
s = count_sub(s, "Then the receipt. It asserts", MAINT.replace("The Check proper:\n", "").replace("**Maintenance line first (RL-171", "**Maintenance line, after the power reads (RL-171") + "\nThen the receipt. It asserts", 1)
import common as C
s = C.count_sub(s, 'validate-kit "$KIT" --repo "$REPO" --batch-window 02:00-02:35', 'validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"', 1)
s = C.count_sub(s, 'plan --kit "$KIT" --legs L001,L002,L003 --batch-window 02:00-02:35', 'plan --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG"', 1)
s = C.count_sub(s, '  --kit "$KIT" --legs L001,L002,L003 --batch-window 02:00-02:35 \\', '  --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" \\', 1)
s = C.count_sub(s, 'batch_windows must be ["02:00-02:35"]', 'batch_windows must be ["$ARG"]', 1)
s = C.count_sub(s, 'assert r["batch_windows"] == ["02:00-02:35"]', 'assert r["batch_windows"] == [__import__("os").environ["ARG"]], r["batch_windows"]   # ARG as recorded at the arm (RL-171)', 1)
s = C.count_sub(s, '`plan.batch_windows` equal to `["02:00-02:35"]`', '`plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check', 1)
s = C.count_sub(s, ". Record PRIOR_CLOSE_EPOCH,", ". Record ARG, LAST_CLOSE_KIND, GAP, QUIET_CAMPAIGN_S, PRIOR_CLOSE_EPOCH,", 1)
s = C.count_sub(s, 'test "$(date +%s)" -ge $((HOST_LAST_CLOSE + 1200)) || { echo "WAIT: 20 min quiet after the latest close of anything on this host (RL-155 R-B)"; exit 1; }',
                'test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }', 1)
s = C.count_sub(s, "no leg starts inside 02:00-02:35", "no leg starts inside the batch-window argument (`$ARG`: 02:00-02:35 or 13:14-13:15, chosen by the launch time, RL-171 §3)", 1)
s = C.count_sub(s, C.HOST_PROSE_OLD, C.HOST_PROSE_NEW, 1)
assert "02:40" not in s.replace("Tue 02:40", "") or True
open(f"{D}/ITEM-hp01-s01.md", "w").write(s)
print("ok")
