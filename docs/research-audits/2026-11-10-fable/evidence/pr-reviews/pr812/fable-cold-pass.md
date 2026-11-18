# PR #812 cold final pass (gate-ledger row 4)

Fable 5.2, research lead. 2026-11-18 02:05 PST. Head `0d03cb7833bb8b15bc391127a7fe5519b7d98602`, parent `e1b85a59c`, drafts `ab63e041f`.

**Verdict: PASS.** The PR's code admits and refuses qualification starts as RL-175 C.3/C.4 and RL-179 F-1/F-2/F-7 say, and it changes nothing that is measured. No change to the PR is required. Five corrections are owed in the item drafts before issue (section 3); they are data, need no re-pin, and do not hold the merge.

Cites are `file:line` at the head for code, and `gates.sh:line` at `ab63e041f` for the drafts' gate block (included verbatim in each item).

## 1. The four checks

| Check | Result | Where |
|---|---|---|
| Calendar date | **As ruled.** The child tests its recorded start against the authorized America/Los_Angeles date with integer arithmetic, on three stamps (both ends of the projected interval and its own wall read). The draft keys the plan by span, allows one block a date and refuses a receipt that disagrees with its own span's entry. s01's latest start is worked back from 23:59:59 through s02 (F-1 rule 3). | `scripts/cadence_legs_runner.py:410-416`; `gates.sh:184-192, 224-232, 325-336` |
| Batch rule | **As ruled, one reading stricter (3c).** Boot time is read at each arm. The gate holds from the predicted batch less the expected span until batch + 27 min, and hands the child both edges. | `gates.sh:354, 374-385`; child bounds `cadence_legs_runner.py:408-411` |
| "Close proven", no timed gap | **As ruled and as frozen.** Latest attempt by sequence, else recorded boot order then monotonic; never wall clock. The receipt must carry that attempt's own id and a passed restore. Close and start compare in nanoseconds. The launcher re-proves under the fence lock and publishes the new attempt before bootstrap. No 300 s or 1,200 s remains in the gates. | `scripts/launch_cadence_span.py:98-118, 126-136, 274-280`; `gates.sh:63-70, 88-104, 369` |
| Lower and upper bound, sleep-inclusive clock | **As ruled.** Lower inclusive, cutoff exclusive, exact close bound in ns. Elapsed time since the arm sample is read on Darwin `CLOCK_MONOTONIC_RAW`, which counts sleep. A child clock behind the anchor refuses. The refusal comes before the output directory exists. | `cadence_legs_runner.py:149-155, 399-416, 433-438, 446` |
| Required ledger arguments | **As ruled.** A qualification kit without ledger, previous receipt, span id and close bound is refused before any host check or bootstrap. Both CLIs refuse a qualification kit without date and both bounds; the child also needs the anchor. | `launch_cadence_span.py:221-225, 387-393`; `cadence_legs_runner.py:383-396, 1065` |

**What I ran.** 28 synthetic probes against the exported head and the draft kit `cl-qual-01` (sha `35ded7c8…`), all as expected:
- bound equality and ±1 ns at both edges and at the close bound;
- wall rollback under the lower bound, and sleep-inclusive elapsed past the cutoff;
- the 23:59:59.9999998 stamp and the next midnight;
- sequence against wall order, a missing receipt, a foreign id, no id, a failed readback, a duplicate sequence, two boots with no order;
- the three launcher omissions.

The kit's 38 frozen paths hash-match the head, and its `frozen.commit` is the head. CI on the head shows 21 passed, 2 skipped.

## 2. Does it change what is measured, or how?

**No.** The diff touches two scripts and one test file. Soak, G0, legs, feeds, plan and restore are untouched.
- The guard runs before `output.mkdir`, so a refused start writes nothing (`cadence_legs_runner.py:433-446`).
- The receipt gains `t0_authority`, `span_id`, `started.epoch_ns`, `started.continuous_ns` and `ended.epoch_ns` (`:439-455, 718-720`).
- `started.epoch_s` becomes the anchored projection in place of a bare wall read (`:417-423`). It still feeds `plan_span` (`:629`). With no clock step the two agree to the arm sampling width. The date is the same by construction, because all three stamps must fall on the authorized date. I accept the anchored stamp as the span's t0 for `lm-qual-01`'s day.

## 3. Owed in the drafts before issue (lead; data only, no re-pin)

a. **RL-181 §4(a) is missing, and this one admits wrongly.** `ITEM-qual01-s02` gates on the RL-172a soak comparison only (`gates.sh:303-306`). Add the second hand-read on qual-01-s01 as s02's condition, with re-dating under C.3 if it has not passed by s02's latest t0. RL-181 §1.0's registration commit before qual-01-s01 arms also has no line in the item.

b. **Terms RL-179 dropped still bound the start.** They refuse starts the rulings admit, which costs time and never validity. Strike them at the regeneration, once the register rows are committed:
- the 24 h item expiry (`gates.sh:5-10, 322`; F-6);
- the watcher as an arm gate and as a bound (`gates.sh:11-16, 316, 322`; F-6 table);
- the line 9 debt gate (`gates.sh:268-292, 397`; F-3 b);
- the seven-day queue test in shell (`gates.sh:254`; F-6 keeps it only where pinned bytes enforce it).

c. **Batch reading confirmed, no change.** The gate also holds when the batch falls inside the soak (`gates.sh:380`), which is stricter than C.4's "between its soak end and its expected close". Release is batch + 27 min, so a batch that starts in the soak is still running at the first leg. The stricter reading is the rule.

d. **Stale text.** The 24-leg cap and "two blocks" sentence (`gates.sh:234`, item day-law bullet) describe an allowance F-1 rule 5 retired. `record-shapes.md` names `0576ed76d` for `LINE2_PIN`; the gate tests the current pin.

e. **First-arm prerequisites, so that qual-01-s01 does not strand.**
- Seed the ledger with `sequence` numbers from row one. That avoids the same-boot false refusal audit-2 verified.
- The latest entry before qual-01-s01 (dev-05-s02 or a filler, on an older pin) has no `span_id` in its receipt. The lead must supply its identity-bound close Check with `restore_readbacks`, or `proven_close` refuses (`launch_cadence_span.py:126-136`).
- A child refusal at rc 3 leaves a published attempt with no receipt (`launch_cadence_span.py:279` against `cadence_legs_runner.py:438`). Every successor then refuses until the lead writes that attempt's close Check. Put the recovery in the item.

## 4. For the next runner pin, not now

- Run directly, the child accepts a qualification kit without `--span-id` and `--t0-not-before-ns` (`cadence_legs_runner.py:381-396`). The launcher always passes both, and a receipt without an id cannot serve as a proof, so it fails closed.
- Launches outside this launcher are invisible to the ledger (audit-2). The desk fence and the process census cover the host; the ledger's completeness is the lead's.

## Not checked

- I did not run the repository test suite. It has process-signalling cases, and CI covers it.
- The sleep-inclusive property rests on Apple's `clock_gettime(3)` text and Astra's Libc cite. This Air has not slept since boot, so I could not observe it.
- The 00:07 `RESUME.md` is no longer on disk; it was overwritten at 00:49. I used the frozen definition as quoted in `/Volumes/JW-EXT/scratch/pl-812/AUDIT.md`.
- I read the gate block and `ITEM-qual01-s01` in full, confirmed s02's gate block is identical, and read only the per-item constants of the other four.
- No custody, energy, power, meter, transcript, slot, hazard, sealed or restricted file was opened. No repo edit, push or ssh.

**VERDICT: PASS** (PR #812 at `0d03cb783`; merge may proceed; section 3 is owed in the drafts before issue)
