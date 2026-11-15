# Seat: Mythos 5.2, #789 delta

`date`: Sat Nov 14 17:59:22 PST 2026 (end of the seat; it started at 17:49:03).

## Verdict

**ADMIT WITH FIXES** for the hp-01 smoke on `dd206025a` (kit `7eaf2660…d2965`).

- F1 to F9 are closed.
- I found no new path that leaves the host in High Power unnoticed, and none by which `restore-owed` sets a mode other than 0 or acts under a lock holder.
- The fixes are procedure text only: D1 and D4 before H001-H003 arm, and D1's second line before the remainder arms.
- No code change is needed. If the builder does change code for any D item, it must land and re-pin before the smoke, or the smoke and the remainder run on different bytes (RL-150 R5).

New findings are numbered D1 to D6 so they do not collide with the first report's F numbers.

## What I checked

Read via git only: `git diff a95812f14 bbd34dc87`, the files at `dd206025a`, RL-157 and RL-161.

| Check | Result |
|---|---|
| Kit sha256 at `bbd34dc87` | `7eaf2660…d2965`, matches |
| Kit diff | Only `frozen.commit`, four hashes, the master seed, twelve seeds and the rule 6 text |
| The four changed hashes (`desk.py`, `kit.py`, `stops.py`, the runner) | Re-hashed from the blobs at `dd206025a`; all match |
| Three unchanged hashes (`legs.py`, `align_r1_rehearsal.py`, `launch_cadence_span.py`) | Re-hashed; match |
| The other 30 hashes | Unchanged in the kit; `9526c29b0` and `dd206025a` touch no other frozen path |
| Twelve seeds | Recomputed from `sha256("cl-hp-01\|2026111404\|seed\|i")`; all twelve match |
| RL-157 §2 condition 1 | Holds: `run_child` refuses with the attempt's name and proof (runner `:219-220`) before any summary or `finished` count |
| RL-157 §2 condition 3 | Holds for the leg child's modules I searched: the only pmset uses are `-g batt` and `-g custom` |

**Not done.**
- No test, mock, validator or mutant was run; the builder's counts are unverified. This session refused Python, so hashes came from `shasum` and seeds were converted by hand.
- CI on `bbd34dc87` was incomplete when I looked: `build`, `changes`, `fences`, `quick` and four others passed; the 12 test shards and `calibration-exits-exclusive` were pending.
- I did not check whether `host_run`'s 15 s cap can stop a hung `sudo pmset`. That is inherited, not from this delta.
- No measurement, slot, transcript, energy, power, meter or powermetrics file was opened. No SSH. No file was edited.

## 1. Is each F closed?

| # | Closed? | Note |
|---|---|---|
| F1 | Yes | `stops.py` fires on anything but `restore_proven: true` when `block_mode` is 2, including no result. See D6 for the two conditions |
| F2 | Yes, as scoped | Detection plus one human command; no automatic restore, which §13.2.3 puts to the research lead. See D3 and D4 |
| F3 | Yes for admission | Every admitted leg now has an observation before and after it. See D1 for how it surfaces |
| F4 | Yes | Three attempts, stops on a deferral, a raised attempt counts as failed. See D2 for the timing claim |
| F5 | Yes | `_close` sits in its own `finally`; the ignore loop is bounded at four passes (runner `:637-661`) |
| F6 | Yes | `before_high` must read 0 (`:329-331`); `_held` needs this span's tag and owner (`:346-354`, `:664-667`) |
| F7 | Yes | See D5 for one wording nit |
| F8 | Yes | 16:50 + 32,850 s = 01:57:30 |
| F9 | Kept | Agreed |

Two points I checked specifically:
- **The F4 retry does not weaken the W1 rule.** After a failed first attempt the guard is disarmed, so later attempts skip the lock retake and the W1 marker check (`align_r1_rehearsal.py:391-421`). The lock from the first retake is still held, so no W1 install can have written a marker in between.
- **The F6 refusal restores Automatic.** `touched` is set before the check, so a mode found changed after the soak ends with the host at 0 and the proof true.

## Findings

**D1. A withdrawal at the close's last look is silent at the desk. MEDIUM, procedure.**
- `last_look` returns rc 0 when High Power is not held (runner `:693-701`). The span closes rc 0, `MEASURED_OK`, with no named stop. The test asserts rc 0.
- The same event at a per-leg check is a REFUSAL (`:573-577`).
- The desk table has no `admitted` column (`desk.py:159-171`; dev-01 F8, not yet landed). The table for a span with a withdrawn leg is identical to one without.
- The reason is only in the receipt (`high_power.revoked`, `high_power.before_restore`), which is not a desk input.
- The leg record still says `ac_powermode: 2`, so §13.2.1's "every leg's `ac_powermode` 2" check passes for a withdrawn leg.
- What does carry it: `admitted: false` in the leg summary, the desk bundle and `desk_summary.json`. All three are the same object, so they agree.
- **Fix before the smoke arms (one line in the arm record):** the hand-read takes `admitted` from each leg summary and reads the receipt's `high_power.revoked` and `before_restore`.
- **Fix before the remainder arms:** any `revoked` entry holds the next hp-01 span until the research lead rules, as a REFUSAL would.
- **Fix in code (next re-pin, with the `admitted` column):** a failed last look sets rc 2, and the inclusion code reads `admitted` from the summary, never recomputing from the leg record.

**D2. The close can pass the 180 s grace in the all-hang case. LOW.**
- The builder's "about 96 s" is the restore step alone. The power steps are now: last look up to 30 s, restore up to 94 s, proof up to 30 s, so 154 s where it was 60 s.
- **External SIGTERM mid-leg** (a bootout): the launcher kills 180 s after its SIGTERM (`launch_cadence_span.py:179-183`). Child teardown takes up to about 70 s (my first report), so the third attempt can end at 194 s and the proof at 224 s.
- **The runner's own deadline:** inside. Work stops 370 s before the deadline and the kill comes 10 s before it, which leaves about 136 s for the feed stops.
- The overrun needs every pmset call to hang to its 15 s cap, which is the case where the restore fails anyway. The outcome is a kept marker and no receipt, which F1 now turns into RESTORE_UNPROVEN.
- The F5 loop adds no measurable time.
- **Fix:** correct the doc figure at the next change. Optional in code: stop retrying when the close's remaining budget is short.

**D3. `restore-owed` checks the W1 tag before it takes the lock. LOW.**
- It never sets a mode other than 0, defers under any lock holder, and removes the marker only after 0 reads back. It refuses a W1 marker in the standing state (armed session, no lock held).
- The W1 check is outside the lock (runner `:1075`), and `powermode.restore_owed` with no owner re-reads presence under the lock but not the tag (`powermode.py:318-329`). A W1 install would have to run start to finish between two adjacent statements, so this is theoretical.
- The check is negative: `w1_marker` returns False on a read error (`powermode.py:60-66`), and any non-W1 marker is restored, not only a cadence span's.
- "Safe when" is text only. The command does not look at the desk fence or a loaded night job, and Automatic spans and plan-0 nights hold no lock (`align_v4_session.py:1727-1730`). Run during one, it would issue a 0-to-0 `pmset` write under a leg. QUIET-MAC already forbids the session that would do this.
- **Fix in code (next re-pin):** take the `HostLock` in the runner's `restore_owed`, require the R1 tag and `writer: cadence span` under it, and pass the lock down. Optionally refuse on a live fence or loaded night job.

**D4. The restore command exists only at or after `dd206025a`. LOW, doc.**
- The marker and the checklist say "from the measurement checkout". dev-01 and dev-02 pin `b4b6aeb19`, which has no `restore-owed`; there the command exits 2 on usage.
- The command touches only the host state directory and pmset, so any checkout works.
- **Fix before the smoke (doc or arm record):** "run it from any checkout at or after `dd206025a`".

**D5. Text nits.**
- Rule 6 says "retried up to three times"; the code makes three attempts.
- `revoked` also lists legs that were never admitted (`:674-678`; the append is outside the `if`).
- After a SIGKILL the last finished leg keeps `admitted: true` on disk with no later observation. Rule 6 as written excludes it, and the hand-read should say so.
- Two failed `pmset -g custom` reads withdraw a leg just as a changed mode does. That is conservative, and the reason records which it was.

**D6. Gate conditions on the new commit. NOTE, the lead's.**
- F1's guard needs the Air desk at or after `dd206025a` and invoked with `--kit`. With `--adapter` the block mode defaults to 0 and the guard is inert (`scripts/air/cadence_desk.py:28-32`).
- RL-155 §5.2's lines (row-1 review, CI, the recorded mock) were met on `d8ae17db2` and need to hold on `dd206025a`.
- I assumed no hp-01 span ran on the old kit `bd7c8711…`; I opened no record to confirm it.

## The other five questions

**2. `restore-owed`.** It creates no new way to leave the host wrong: the only mode it writes is 0, never under a lock holder, and it exits 0 only on powermode 0 with no marker. It cannot undo a W1 marker in any state I could construct outside D3's window. It marks itself a production entry (runner `:1183`), so a stray host-state override refuses.

**3. F3's rewrite.** The rewrite itself is consistent: the leg's file, the desk bundle and the receipt carry the same summary object. The desk table can miss it and the hand-read catches it only if it reads the fields named in D1.

**4. The grace.** D2. Inside on the runner's own deadline; outside only after an external SIGTERM with every host command hanging.

**5. The seed.** The leg list is correct: twelve legs, L001-L012, band q0, 19,458 and 4,096 tokens, seeds as recomputed. No other kit uses 2026111404:
- `cl-dev-01` uses 2026111401 and `cl-dev-02` uses 2026111402.
- Both `cl-dev-03` kits on `origin/align/2026-11-14-kit-v1-1` use 2026111403.
- The literal appears only in this branch's kit, doc and test.
- I used the local refs of the v1.1 branches as they stood at 17:48 and did not fetch them.

**6. Countability and the next Automatic block.**
- Nothing new makes hp-01's data non-countable, given D1's hand-read lines and no code change between the smoke and the remainder.
- A later Automatic block's start state is not at risk. Every new path ends at 0 or leaves the marker, and `read_power` still gates the mode at every start.