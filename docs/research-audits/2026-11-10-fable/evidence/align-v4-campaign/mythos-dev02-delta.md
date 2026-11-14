# Seat: Mythos 5.2, cl-dev-02 delta

Sat Nov 14 15:06:03 PST 2026 (`date`). Cold seat for RL-155 §3.3 line 1. I did not write the kits, the queue or the plans.

**Bytes checked.**
- `cl-dev-01.json` at `589748f15`: blob `aea8643a`, sha256 `c76344c5…66d7`, the kit I admitted.
- `cl-dev-02.json` at `589748f15`: blob `7e8dc7a2`, sha256 `d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8`.
- Draft queue: sha256 `58f05a0a…4375`. The builder changed it while I worked; the first copy I read (`2afb3b5a…`) had `not_before` 2026-11-15.
- Runner, queue library and launcher by `git show` at `b4b6aeb19`.

## Verdict

**ADMIT** for dev-02's §2.8 line 1. I have no finding against kit `d963500b…` and it needs no change.

Six findings follow. None is against the kit. They sit on line 3 (F1), the launch item (F2, F4, F5), line 2 (F3) and the lead's records (F6), and F1 to F3 must close before the arm.

## Answers

**1. The kit delta.** Every difference is one that "same kit, next seeds" and RL-155's anchor-only reading allow.

| Field | cl-dev-01 | cl-dev-02 | Allowed |
|---|---|---|---|
| `campaign_id` | `cl-dev-01` | `cl-dev-02` | Yes, the id |
| `title` | dev-01 with its pilot | "the dev-01 kit with the next seeds … one span" | Yes; accurate |
| `seed_law.master_seed` | 2026111401 | 2026111402 | Yes, the next seed |
| `legs[].seed` (12) | dev-01's | regenerated | Yes |
| `inclusion_rules` | 11 entries | 10: `pilot_counted` removed | Yes |
| Everything else | | byte-equal | |

- **Inclusion rules.** The only change is the removal of `pilot_counted`, whose own text says "(dev-01 only)". The other ten entries are identical and in the same order.
  - Rule 5 carries R7's words exactly.
  - The energy-read rule carries R8's sentence exactly.
  - Rules 1 to 4 and 6 are RL-149 §2.4's.
- **Frozen block: byte-equal.** The blob diff has no hunk in it. It names commit `b4b6aeb19` and 37 paths.
- **Hashes.** I recomputed all 37 sha256 values from the blobs at `b4b6aeb19`, and all match the kit. `git diff --stat b4b6aeb19 589748f15` touches no frozen path.
- **Roster.** The kit has no roster field; the queue span names all twelve legs in kit order.
- No kit text states the 120-leg cap, so nothing in it contradicts the move to 132.

**2. Seeds and leg shape.**
- I recomputed the twelve seeds from the `sha256-v1` law, and all match the kit. One band, so the shuffle changes nothing.
- No seed equals any dev-01 seed, and the twelve are distinct. None equals the frozen step seed (`r1_runtime.json` `step.seed` = 1).
- RL-149, RL-150 and RL-155 name no forbidden seed history, so those two sets are what I compared against.
- All twelve legs are type A at the anchor shape: 19,458 prefill tokens (40,000 characters), decode cap 4,096, band `q0`, quiet 0 s, Automatic.
- Run ids are `cadence-cl-dev-02-L0xx`, so they cannot collide with dev-01's.

**3. The draft queue.**
- **Pin:** yes, `d963500b…28a8`, the committed blob's sha.
- **Finite, one span:** yes. `dev-02-s01`, attempt 1, L001-L012 in seeded order, plan id `cq-dev-02-s01-a1`.
- **Expiry:** `2026-11-21T23:59:00-08:00`. Whether that is within seven days depends on the commit time (F1).
- **`validate-queue`:** every rule of `validate_queue` holds on my reading of the code against the file. I could not execute it.
  - It passes only with `--kits-root` at a tree holding kit blob `7e8dc7a2` (`589748f15` or `8bd31ae5a`).
  - Against the measurement checkout at `b4b6aeb19` it is refused, because the in-tree kit there is the `efbd0b020` pin.

**4. The calendar, at t0 Mon 16 Nov 02:40:00 (epoch 1794825600).**

| | Time, Mon | Margin |
|---|---|---|
| Expected end (18,162 s) | 07:42:42 | |
| Worst-case end (40,950 s) | 14:02:30 | |
| Fence end (worst + 560 + 900 s, item 317's form) | 14:26:50 | 790 s under the launcher's 12 h ceiling |
| Next 01:50 | Tue | 11 h 23 min after the fence end |
| Slot 7's latest t0 | 16:50 | 2 h 23 min after the fence end |

- These are the builder's `plans/dev02-all12-mon0240.json` figures; I checked the arithmetic by hand.
- The span clears the next blackout and the next slot.
- At the front there is no margin: 02:40 is the edge of the 01:50-02:40 band, and the plan itself accepts a launch from 02:35 (F2).
- At this t0 a launch without `--batch-window` is refused by the plan, because the worst case meets the frozen 11:45-13:15 default. So the missing-flag case fails closed here.

**5. Countability.** F1, F2 and F3. The kit adds nothing new.

## Findings

**F1. The queue's expiry is over seven days out if it is committed today.** Major by the letter of §2.8 line 3; a one-field edit.
- Evidence: a commit before Sat 23:59 PST puts `expires_at` more than seven days after it. `validate_queue` checks only that the time parses.
- The builder's README has the condition reversed ("holds only if committed by 11-14 or 11-15"). It fails on 11-14 and holds from 11-15 00:00.
- Fix: set `expires_at` to `2026-11-20T23:59:00-08:00`, as dev-01's queue has, or commit on Sunday and record the commit time beside the expiry. Either way the file's sha changes; pin the new one in line 3.

**F2. The day and the launch window are held by the item's time gate alone, and RL-155's window (02:40 to 14:30) is too wide on these bytes.** Major for the item; no effect at a 02:40 launch.
- `not_before` is format-checked only; `next_action` never reads it. Nothing in code stops a Sunday launch, which RL-155 rules out.
- A launch between about 10:50 and 13:15 waits out the frozen 11:45-13:15 soak window (`cadence_legs_runner.py:304`, `:455`), up to about 2 h 20 min that the plan does not budget.
- A 14:30 launch is accepted by the plan (`plans/dev02-all12-mon1430.json`), with worst-case end Tue 01:52:30 and fence end 02:16:50. That is inside the blackout and past item 317's 01:50 rule.
- Fix: the item gates on epoch, as 317 did, in both the check block and the run block:
  - 1794825600 to 1794855000 (Mon 02:40:00 to 10:50:00), or
  - 1794863700 to 1794866590 (13:15:00 to 14:03:10).
- The magistrate's activation should also start at 02:40, not before, so its checks are not load inside the quiet period. That is my reading of R-B.
- One line to the research lead, since the table says 14:30. The builder's README reaches the same window.
- Slot 5's "latest t0 21:20" has the same defect (worst end 01:57:30; item 317 used 20:48 for the same plan). That is hp-01's item, but it is the span before this t0.

**F3. Line 2's extended reading names eight red modules; the record has ten.** Major for line 2; the research lead's line.
- RL-155 extends RL-152 §2.2 to this kit. That text says "exactly the eight modules" and "every other module is green".
- `rl152-redset/LINE2.md` records 12 red tests in ten modules. The two extra are `align.test_r1_followup` (1 ERROR) and `hazards.test_refusal_allowlist`.
- By that note, base and head are equal test for test and the full suite is green at #777's head `ae340d3da`. So the substance holds for all ten. I did not read CI.
- Fix: one line from the research lead restating the set, recorded in dev-02's line 2. The pilot armed on the same record.

**F4. A separate queue takes lines 6 and 9 out of `next`.** Minor, procedure.
- `next_action` halts on a bad-terminal span and applies the k+2 rule within one queue file. A one-span queue never waits.
- Fix: the item records by hand that no stop is open from dev-01 span 2 (and from hp-01's pilot if it ran), and that the desk of the campaign span two back is final (RL-155 §3.4).

**F5. Arm conditions carried from the pilot.** Minor; none is new. The dev-02 item needs each:
- `--batch-window 02:00-02:35` on `plan` and `launch`, with the receipt's `batch_windows` asserted.
- `--legs L001,…,L012` written out.
- Do not run `cadence_queue.py checklist`. Its `span_window` line needs 13:20, and the kit's template still says 13:20 to 00:45.
- The measurement_mode and network-time line (RL-150 F5). It matters more here, because Part C, fillers and possibly a High Power block run between the pilot and this span.
- A fresh detached worktree at `b4b6aeb19`.
- The kit copied from `589748f15` to a new path, with the sha asserted.
- A new `OUT` outside every v4 root.
- The check script with twelve legs and the meter feed's re-hash skipped.

**F6. Records to bring into line.** Minor, lead.
- The ledger at `8bd31ae5a` still shows dev-02 as `HOLD_FOR_CELL_LAW`, `qual-01` depending on dev-02, and no dev-03 to dev-05. Its dev-02 entry is where RL-155 §3.3 gets cited, since the kit cites RL-149 only and stays as built.
- `standing_notice` is null in the queue. §2.8 says the notice names the queue, kit, legs and expiry.
- The look manifest's block list must include dev-02.

**A suggestion, not a finding.** Sunday's dev-01 span 2 is the first span at a 02:40 t0. Its soak and step lines show whether the batch tail or the hourly job seen at 02:42 disturbs the soak. Read them before issuing dev-02.

## What I did and did not do

- **Did:** the kit blob diff; the twelve seeds and the 37 frozen hashes by `shasum`; `kit.py`, `queue.py`, `legs.py`, `cadence_queue.py`, `cadence_legs_runner.py`, `launch_cadence_span.py` and `cadence_leg.py` at `b4b6aeb19`; RL-149 §2 and §5, RL-150, RL-152 §2 and RL-155 in the log at `95af25d8b`; item 317 in `RUN_STATE.md`; the builder's README, queue and plans.
- **Could not run:** Python was denied in this seat. So `validate-kit`, `gen-legs`, `plan`, `validate-queue` and `mock` were not run by me. The plan figures are the builder's.
- **Not read:** CI, the builder's mock directories, the dev-01 span-2 item draft. No dev-02 item draft exists yet, so F2, F4 and F5 are conditions on it.
- **Blinding held.** No slot, transcript, energy, power, meter or powermetrics file was opened, nothing under `~/night-*` or `campaign-out`, and no `smoke_part_*`. The step-3 files in the evidence directory were listed, not opened. No SSH.
- **Nothing edited.** The harness saved two oversized command outputs to its own session cache.