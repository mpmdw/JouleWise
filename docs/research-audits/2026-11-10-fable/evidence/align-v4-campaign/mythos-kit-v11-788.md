# Seat: Mythos 5.2, #788 kit v1.1

Sat Nov 14 15:28:07 PST 2026 (`date`). Cold seat for RL-149 §2.8 line 1 and RL-155 §5.1. I did not write the code or the kits.

## Verdict

| Target | Code | Kit |
|---|---|---|
| **v1.1a** (pin `55a5670e8`, kit sha256 `bfb29f78…3a7d`) | ADMIT | ADMIT WITH FIXES (F4, F5, F6) |
| **v1.1** (pin `e82e2a1b9`, kit sha256 `a7ddae5d…0f1d`) | ADMIT WITH FIXES (F3) | ADMIT WITH FIXES (F1, F2, F4, F5, F6) |

- **Class B for v1.1a is correct**, and **class A for v1.1 is correct**. There is no gate-module edit.
- Nothing is a REFUSE. The largest finding is F1: the "at least half" rule holds only for some queue shapes.
- **I could not run Python in this seat.** So `validate-kit`, `plan`, `mock` and the tests were not run by me; the plan figures are the builder's, checked by hand arithmetic.
- **The builder's seven questions were not in anything I could reach** (PR body, commit messages, design note §14, the audit branch, the builder's scratch `body.md`). Item 5 below covers the seven choices I can see instead; the lead should map them.

## What I verified

- **Frozen hashes.** All six changed paths at each pin match the kit by `shasum`. The other paths are byte-identical to `b4b6aeb19` (`git diff --stat`) and carry dev-01's hashes.
- **Gate code.** `thermal_gates.py`, `r1_runtime.py`, `workload.py`, `cadence_leg_runtime.py`, `align_r1_rehearsal.py` and `run_align_r1_smoke.py` are unchanged from `b4b6aeb19` at both pins.
- **The cell law, by hand from `shasum` draws.** All 12 sizes, all 12 shapes and the seeds of L001 and L012 match the kit.
- **The two drafts** differ only in title, pin, four hashes, `g0_shapes`, six `g0_shape` values, rule 2's text, `pilot_counted`, the stop notes and `leg_budget_s`.

## Findings

**F1. The "at least half" rule depends on where the queue cuts the block.** Major, v1.1 only; needs a research-lead line.
- A span leg that is first in its span captures, so it is not a span-reference leg in effect (`legs.py` `leg_specs`, `position == 0`). The law does not know the cuts.
- dev-03's span-shaped legs are L002, L004, L008, L009, L010 and L012. L004 always starts the second span, because the smoke is L001-L003.
- RL-155a §2 asks for spans of at most six legs after the smoke. Of the four legal cuts, only one keeps half:

| Queue | Consumers / warm legs | RL-150 R1 part 2 |
|---|---|---|
| 3, 9 (the PR's plan) | 5 / 10 | Holds, exactly; breaks RL-155a's six-leg limit |
| 3, 3, 6 (third span starts at L007) | 5 / 9 | Holds |
| 3, 4, 5 (L008) | 4 / 9 | Fails |
| 3, 5, 4 (L009) | 4 / 9 | Fails |
| 3, 6, 3 (L010) | 4 / 9 | Fails |

- Fix now: dev-03's queue is L001-L003, L004-L006, L007-L012, and filler P never cuts at a span-shaped leg.
- Fix for dev-04 and dev-05: the law keeps span-start positions `own`, or `plan` refuses a roster that starts on a span-shaped leg after the smoke.
- The kit title's "six of the eleven warm legs" is not what will run.

**F2. The smoke can pass without ever showing a consumer turn.** Major, v1.1; research lead.
- L002 is the smoke's only consumer. If its G0 times out it runs no turn, and RL-150 R9 still passes the pilot (two admitted, exclusion under rule 2).
- Fix: for this kit, the smoke passes only if L002's G0 released against the span reference; otherwise the hand-read covers the next span too.

**F3. A redone first leg gives a warm span reference, and no projection shows it.** Medium, v1.1; research lead plus a small code change.
- The source is always `legs/<first>/runtime`. After a load redo that is the redo's capture, taken after the rejected attempt's turn. If the quota is spent, it is a contaminated attempt's capture.
- Custody is safe: the first leg's redo loop ends before any consumer starts. The meaning changes: consumers then release near a warm reference, which is R1's original problem.
- The receipt and `g0_reference_source` carry the same leg id and path in both cases.
- Fix: the receipt records the source attempt number and the reference's `record_sha256`. The research lead rules whether such consumers count toward the half.

**F4. The ruled blackout and RL-155a's two bounds are still not in code, and the free t0 removes the old fence.** Major, both kits; carried from dev-01 F2.
- The default is still 11:45-13:15 in `kit.OS_BATCH_WINDOW`, in `kit_v11.evaluate_checklist` and in the runner. Without the flag, a span crossing 02:00-02:35 passes `plan` and `checklist`.
- With the flag, `plan` accepts a worst-case end up to 02:00. RL-155a needs the fence end by 01:50, which is 34 min earlier.
- The soak still waits out 11:45-13:15 unbudgeted (`soak_windows=[r1.OS_BATCH_WINDOW_LOCAL]`), so "no launch 10:50-13:15" applies to both pins.
- Fix: every `plan`, `launch` and `checklist` passes `--batch-window 02:00-02:35`, and each item gates t0 by epoch. Latest t0 by the fence:

| Span | Worst + 1,460 s | Latest t0 |
|---|---|---|
| 3 legs | 18,110 s | 20:48:10 |
| 6 legs | 26,210 s | 18:33:10 |
| 9 legs | 34,310 s | 16:18:10 |
| 12 legs | 42,410 s | 14:03:10 |

- Better, before the final pin: make the flag required for v1.1 kits. That is class B.

**F5. Line 2 is not met for either pin.** Major, procedure.
- CI on head `17f478675` was still queued at 15:16. Head differs from the v1.1 pin by the kit file and 49 test lines only.
- Head does not cover the v1.1a pin: it needs its own suite result at `55a5670e8` or `08982ec0a`.
- The pin-identity tests skip when the commit is not in the clone, so a green CI may not have run them. I confirmed the identity myself by diff.

**F6. Kit text states a balance the law does not give.** Minor, both kits.
- The title and `bands_by_history` say "every three consecutive legs hold each size once". L003 and L004 are both 10,000.
- Fix: "each block of three in kit order (L001-L003, L004-L006, …)".

**F7. RL-155 §5.1 lists F6 to F12 as v1.1 contents; the PR defers them.** Medium; the research lead accepts or the builder adds.
- The ones with code are F6 (write roots, queue expiry, watcher stamp), F8 (the `admitted` column) and F11 (model string).
- F5's campaign-scope stop is still absent from `stop_rules.notes`, and dev-03 chains spans.

**F8. Smaller items.** Minor.
- The consumer runtime does not bind the source to its own span. The runner supplies the right path; a hand-run leg could consume another span's capture.
- The desk shows neither shape nor role. L004 has shape `span` and role `capture`, so tables and fit code must read `g0_role` from the leg record, not the kit.
- `cl-hp-01` (#789) and `cl-dev-03` both use master seed 2026111403. Draws differ because the campaign id is hashed; the ledger convention is broken.
- The two drafts share a campaign id, seeds and run ids. Only one may ever run.

## Answers to the brief

1. **Cell law.**
   - It implements RL-149 §2.2 and §2.3's mixed cells for type A.
   - It is deterministic from sha256 draws, and the validator regenerates the whole list.
   - Each size appears four times, once per aligned block of three.
   - No leg can get an invalid size or shape: sizes are range-checked, shapes come from a closed set, and the v1.1a pin refuses any `span` shape.
   - Caveats: F1 and F6.
2. **Span-reference leg.**
   - A missing, corrupt, unbound, unobserved or non-capture source is refused before any work, by the same checks as `Segment.consume_d_reference`.
   - A consumer never falls back to its own capture.
   - "Forged" holds only against accident, as in R1: a consistently rewritten directory passes.
   - Stale: F8. Redo: F3.
3. **v1 kits.** Unaffected.
   - At the v1.1a pin the leg runtime is dev-01's bytes. `legs.py` changes only `leg_specs`, `plan_span` and one constant.
   - A v1 runner refuses a v1.1 kit on schema, runner kind and unknown keys, and again on HEAD.
4. **Free t0 and plans.** The arithmetic is right: 7,024 / 16,650, 15,163 / 32,850 and 17,082 / 40,950 s.
   - At Tue 02:40 the smoke's fence ends 07:41:50 and v1.1a's ends 14:26:50.
   - RL-155's "latest 14:30" for dev-04 is 14:03:10 by the fence.
   - The rest is F4.
5. **The seven choices I can see.**

| Choice | View |
|---|---|
| Span reference is the first leg's capture, not the soak | Right, and the series' shape. RL-150 R1 named both, so the research lead confirms |
| Roles by roster position | Correct code; its consequence is F1 |
| Redo's capture as the source | F3 |
| Missing reference stops the span | Right |
| Consumer G0 modeled at 600 s | A blind guess, harmless: the worst case is unchanged |
| ceil(m/2) per size, L001 own | Right |
| Deferrals (F6 to F12, desk column, default blackout) | F7 by the letter; F4 is a defect |

6. **Countability and #789.**
   - Nothing makes dev-03 non-countable once F1, F2, F4 and F5 close; `pilot_counted` registers the smoke before it runs.
   - #789 touches no leg runtime file. After both merge, v1.1 kits refuse `power_mode` (closed keys) and default to Automatic.
   - Expect textual conflicts in `legs.py` and the runner's `run_leg`. The first kit pinned on the merged commit needs its own R5 class.

## Not done

- No test, mock or validator was run.
- I read the builder's `body.md` and this seat's brief outside git, while looking for the seven questions.
- Blinding held: no measurement, slot, transcript, energy, power, meter or powermetrics file was opened, nothing under `~/night-*` or `campaign-out`, and none of the builder's mock directories. No SSH. Nothing was edited.