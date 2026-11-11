# Cold final pass (Fable): R1 G0 operating-point reference, S6 band, 1,200 s cap

Branch `lane/2026-11-10-r1-g0-rop`, head `ad9c0667f`, diff against `20e9edbc4`.
Reviewed 2026-11-10, blind to every other reviewer. Read-only: no edit to the
branch, no git write, no network, no measurement; host power state and the
worktree were checked untouched afterwards.

## Verdict: ADMIT_WITH_FIXES

The build does what ruling sections 1, 3 and 7 say, and every executing check
in the brief passed. On a night where `step-30b` is accepted on its first
attempt (the 11-10 shape) I found nothing that produces a wrong number or
refuses a night that should run.

One fix touches a number (F1). It is on a contingent path (a CPU-load redo of
`step-30b`) and can be met with a recorded flag; it needs no refusal. Two more
are text corrections with no value change (F2, F3).

## Fixes

### F1. A redo of `step-30b` captures R_op from a machine that is still cooling, and nothing marks it

Why it touches a number: R_op is the zero for every later G0 of the night. If it
is high by X, every later gate admits X more heat than the ruling intends, and
start temperature costs about 1 to 14 J per degree per kJ of member energy
(ruling section 5).

- Input: `step_30b` attempt 0 is rejected for sustained CPU load (ruling 8;
  `_segment`, up to two redos). The rejected attempt is moved aside, a
  `g0-release-soak` runs against the soak mean, and the redo runs. The driver
  does not act on that release's outcome: an unreleased release still starts
  the redo. The redo's WP14(b) capture is then taken about 1,100 to 1,700 s
  after the rejected turn ended (600 s recovery, 65 to 665 s release, about
  25 s prepare, about 390 s idle stage).
- The ruling's own safeguard does not hold there. Decision 4 says the soak's
  settling check and the member's idle stand in for a guard on the capture
  window. On a redo the soak no longer precedes the capture; a full 30B turn
  does. Ruling section 6 rejects exactly this (a self-captured reference from
  an idle that is still cooling, R0 0810Z).
- Wrong output, through the branch's real `capture_reference` and
  `wait('G0')` (11-10 samples for the warmup and tail, plus an added slow
  excess with the R0 0550Z time constant; `work/redo.py`):

| Residual heat at capture | R_op minus settled idle | step-30b G0 releases at (over settled idle) | Limit of every later gate (over settled idle) |
|---|---|---|---|
| none (11-10 as recorded) | +0.02 C | +1.50 C | +1.52 C |
| +1.0 C | +1.07 C | +2.30 C | +2.57 C |
| +2.0 C | +2.13 C | +2.74 C | +3.63 C |
| +3.0 C | +3.16 C | +3.47 C | +4.66 C |

- Size of X: not measurable from disk. After a 900 s load (R0 0550Z, +5.81 C
  at 585 s, time constant 743 to 884 s) the excess is +1.3 to +3.3 C at 1,100
  to 1,700 s. After a warmup only it is about +0.1 to +0.9 C. The 30B step turn
  lies between; I did not read turn durations (a workload result).
- With a hot reference the band is always met and only the slope bar gates,
  which is the failure the ruling describes for per-member self-capture.
- Remedy, a flag and not a refusal: carry the accepted attempt index of
  `step_30b` and `operating_minus_soak_c` into the registration, with a flag
  such as `r1.r_op_captured_after_redo` when the attempt is above 0, and a desk
  rule that such a night goes back to the ruling seat before any R_op-gated
  number is used. Both facts are already in `r1_result.json` (the phase row's
  `attempt`, the step-30b result), so the lead can also disposition this as a
  runbook line with no code. A physical remedy (for example a fresh soak
  before the redo) is the ruling seat's call, not mine.

### F2. The S6 receipt and the ruling quote 911 s for tail model D; the production gate gives 941 s (text only, S6 stays 1.5 C)

Why it touches a number: 911 s is the figure the 1.5 C step is derived from
(`r1_slots.json` `s6_tuning.derivation`: "1.25 x longest fitted tail release
(911 s)").

- The gate's slope is an OLS fit over the preceding 60 s, so it lags the
  instantaneous slope by 30 s. Model D's instantaneous slope reaches
  -0.2 C/min at 901 s (the ruling's figure); the gate sees it at 931 s and
  releases ten samples later.
- Replayed through `ThermalSession.wait`: 940 s after G0 entry, 941 s after
  warmup end.
- The rule still passes: 1.25 x 941 = 1,176 s, inside 1,200 s. The margin is
  24 s, not 61 s. At 1.0 C models A and C still time out at 1,200 s, so 1.5 C
  remains the smallest step that passes.
- Change the receipt text to 941 s (or cite both). When the desk reads the next
  record, the expected `step-30b` release is about 707 to 941 s, not 700 to
  910 s; with 1 Hz noise at the measured 0.078 C it is 716 to 966 s. A release
  at 940 s is not evidence against the tail models.

### F3. `docs/align/thermal_gates.md` says G1 and H use R_op; the code and the contract say they do not (flag, not refuse)

The new section reads "Every later R1 G0, G1, H, precool and sensors-only
release uses the fixed accepted R_op". The code, the lead amendment in
`31-build-report.md` and `docs/align/r1_runtime_contract.md` keep G1 and H on
the G0 release temperatures. The e2e test asserts the code's behaviour. Fix the
sentence.

## What I executed

Scratch scripts and raw outputs: `/tmp/mag-5515/cold-fable/work/`. All replays
substitute only journal delivery and a virtual clock; `capture_reference` and
`wait` are the branch's own. `work/e2e.py` rebuilds the synthetic night that
`refusals.py`, `unobserved.py` and `hotleg.py` take as their argument.

### 1. Real 11-10 step-30b journal through `ThermalSession.wait` (`work/replay.py`)

Journal SHA-256 `ebc7a978...433ef6`, read only.

| Parameters | Result |
|---|---|
| Soak mean (25.489 / 34.011), band 1.0, cap 600 (as run) | timeout at 600 s; exit sample Tf08 28.4069, TV0h 34.2921, slope -0.0386 C/min. Identical to the recorded gate row. |
| R_op from the real `capture_reference` at warmup entry | Tf08 26.571250 C, TV0h 34.106462 C (ruling: 26.571 / 34.106). Minus soak: +1.0822 / +0.0952 C. Coverage of the window 59 of 59. |
| R_op, band 1.5, cap 1,200 | no release in the 600 s of gate record, and none in the 651.7 s of journal that exist |
| R_op, 1.0, 600 and R_op, 1.5, 600 | timeout (ruling 4.1 rows reproduced) |
| R_op, 2.0, 600 or 1,200 | released at 592 s, Tf08 28.4347 (ruling: 592 s) |

The builder's `scripts/replay_r1_g0.py` gives the same R_op and model-B fit on
the real journal and on the committed fixture (byte-identical output).

### 2. Synthetic continuation of the tail, models A to D

Time constants from ruling 3.2; amplitudes and level refitted here. My fits
reproduce the ruling's rmse and levels (A level +0.927, D level -2.590).

| Model | rmse C | Release after G0 entry, band 1.5 | Excess over own idle at release | With 0.078 C noise, 20 seeds: wait / excess | Band 1.0 |
|---|---|---|---|---|---|
| A (60/300, level free) | 0.0755 | 749 s | +1.504 C | 771 to 824 s / +1.25 to +1.50 | timeout 1,200 |
| B (70/500, level = idle) | 0.0765 | 706 s | +1.495 C | 716 to 767 s / +1.26 to +1.50 | 905 s |
| C (100/956, level = idle) | 0.1367 | 860 s | +1.508 C | 867 to 942 s / +1.35 to +1.50 | timeout 1,200 |
| D (70/956, level free) | 0.0822 | 940 s | +0.465 C | 735 to 966 s / +0.18 to +1.22 | 940 s |

All releases fall inside 1,200 s (80 of 80 noisy runs). Excess at release is
about 1.5 C over own idle for A to C. Model D differs from the ruling by 30 s
(F2).

### 3. Hot start: R0 `r0-v4-20261108T0550Z` (`work/hotstart.py`)

R0's full-inventory sampler jitters (0.85 to 1.15 s spacing), which the gate's
100 ms grid rule would call unobserved, so samples were re-timed by index onto
a 1 s grid (no value changed; largest shift 0.77 s). No status source exists in
R0, so status was set to the most permissive value.

- Own idle by the real capture rule: 26.369 C (ruling: 26.369). Excess at 570
  to 600 s: +5.81 C.
- On the 600 s of record: no release.
- Extended to 1,200 s with the record's own log-linear time constants (743,
  824, 884 s): **timeout at 1,200 s** in every case, at band 1.5 and at 2.0,
  with +2.5 to +2.9 C still present. The slope at 1,200 s is -0.20 to
  -0.21 C/min, so the band, not the slope bar, is what refuses.
- A time constant of 447 s or less would be needed to reach +1.5 C by 1,190 s.
  The record gives 743 s or more.

### 4. Synthetic R1 chain, driver in process, every runtime segment a real subprocess (`work/e2e.py`, with `--include-4bit`)

Exit 0, status complete, 24 runtime invocations.

- R_op captured at `step-30b`: `align_window_reference.json` status
  `captured`, coverage 1.0; result `reference_source`
  `r1_step_30b_pre_warmup`.
- Consumed by step-30b's own G0: its episode G0 row carries that reference.
- Consumed later: the three leg releases, the three legs, step-d and its
  precool, the cooldown, both planning precools, the three gated D runs, X-G
  and d-4bit all report `r1_step_30b_pre_warmup`. The designed states gate at
  R_op + 4, + 2, + 0.
- The synthetic world idles at the soak temperature, so the values cannot tell
  R_op from the soak. I therefore set the accepted result to 39.25 / 38.5 C
  (soak 38.0), re-bound its custody and ran real segments
  (`work/refusals.py`): the release, a precool, a leg, a gated D run and the
  +4 C state (target 43.25) all gated on 39.25.
- `g0-release-soak` keeps 600 s (`g0_timeout_s` 600, no `g0_cap_s` in its
  policy). Every model member armed 1,200 s.
- Deadman arming, from `token_budget.deadline_ns` against the G0 row:

| Member | Deadman armed |
|---|---|
| A-B-A legs, d-4bit | 0.0 s after G0 exit (`R1_after_G0_release`), 1,580 s |
| step-30b, step-d | 300.0 s after G0 exit (after the quiet) |
| designed states | 0.0 s after G0 exit |
| gated D runs, X-G | at G0 entry (0.0 s from G0 start), T_dead |

- Unobserved capture (`work/unobserved.py`, slow-key reads failed inside the
  60 s window): 40 s missing and 7 s missing both give window reference
  `unobserved`, G0 outcome `unobserved` after 300 s, no turn, exit 3 with
  "not one complete turn: ['turns:0', 'episode.g0_unreleased:0',
  'thermal.state_unobserved']", no result file, and a later segment refuses.
  5 s missing (coverage 0.917) is captured and the member completes. No
  KeyError path on the empty reference.
- Own G0 that cannot release (`work/hotleg.py`): a leg waits the full 1,200 s
  and exits 0 as `leg_status: inconclusive`; step-30b and d-4bit exit 3.
  The designed behaviour in each case.
- U5 reads `delta_slow_c` 1.5; slots S5 1.0, S5_fast 1.0, S6 1.5; the
  registration's `s6_tuning` carries authority, `from_c` 1.0, `to_c` 1.5,
  which is what the kit binding requires when S6 differs from S5.

### 5. Refusal and incomplete clauses the diff adds or changes

| Clause | Replay | Refuses a night that should run? |
|---|---|---|
| `Segment.reference()`: `step_30b` present but result missing, custody not complete, bytes changed, `operating_reference` absent or mislabelled: exit 2 | 19 consumers of R_op in the synthetic night: 0 refusals. Five fault cases (bytes changed, reference absent, reference mislabelled, empty directory, custody failed) refuse as written. No completed real R1 night exists to replay. | No. The driver moves rejected attempts aside before anything reads them; a failed step-30b has already refused the night. |
| No `step_30b` directory (before acceptance, or rejected attempt moved to `.rejectedN`): soak mean, `r1_soak_reference` | both cases run and release | No (ruling decision 2) |
| Unobserved capture at step-30b: member incomplete, night refuses | Real sidecar member journals on disk: 1 (11-10), captured, 59 of 59. Synthetic: needs 7 or more of 60 samples missing. | Not on the one real record. This is new for R1 (the capture never ran before) and is the registered W1 rule. |
| step-30b G0 timeout at 1,200 s: member incomplete, night refuses (decision 5) | Tail models A to D release at 706 to 940 s, noisy 716 to 966 s | No under any fitted model |
| Driver `_check_soak_reference_consumed`: source must be R_op, value within 1e-6 C | 4 of 4 gated members pass; a soak-labelled result refuses | No |
| Contract fields `operating_reference`, `reference_source`, `operating_minus_soak_c` on step-30b | present in every run | No. Without `--soak-reference` step-30b now runs the member and fails at exit 3 where it used to refuse at exit 2; the driver always passes the soak, so this is unreachable from the night. |
| Legs and d-4bit: deadman after G0 | removes the path where a long G0 left the turn too little time and an incomplete leg refused the night | Removes a refusal |

### 6. Bound arithmetic (`work/bounds.py`, executed against the branch)

- Re-armed member: 1,750 + 1.13544 x 1,580 + 120 = 3,663.9952 s.
- step-30b: 3,663.9952 + 1,200 + 300 + 600 = **5,763.9952 s**. Matches.
- A-B-A attempt: 65 + 600 + 1,200 + 3,663.9952 = **5,528.9952 s**. Matches.
- d-4bit: 4,863.9952 s. Not in the production chain (`d_4bit_source` is null
  and the chain passes no `--include-4bit`).
- Night table: no redo 60,406.9616 s; with one batch wait 65,806.9616 s; with
  the R6-2 retries (29,055.9808 s) 94,862.9424 s. The increase over the old
  table is 600 + 3 x 1,200 = 4,200 s.
- Arm floor 96,427 + 4,200 = 100,627 s. `window_max_s` = 100,627 + 3,300 +
  3,600 + 1,200 + 600 + 300 = **109,627 s** (30.45 h) with one batch crossing,
  120,791 s with two (for example t0 06:00 PT).
- Largest single segment is still 5,763.9952 s, so `T_stream_max_s` stays
  5,764 s and the 11,164 s batch-encounter term is unchanged.

### 7. Tests

`/opt/homebrew/bin/python3.13`, `JW_B5_SYNTHETIC_ONLY=1`, own TMPDIR, working
process enumeration. 519 tests in 23 modules.

- The 20 `test_r1_*` modules (296 tests), `test_thermal_gate` (44),
  `test_v4_kit` (116) and `test_v4_w1_synthetic` (18): **0 failures, 0 errors**
  (15 skips, all declared: full synthetic window, a subprocess helper).
- I also ran `test_v4_w1_plan` and `test_v4_prequal`, which the builder did
  not, because they read the changed `r1_slots.json`. 12 fail. None is caused
  by this branch: 10 fail the same way on a tree export of `20e9edbc4`
  (`night_plan.template.json` no longer matches `collection_plan.json`); one
  asserts that `R0.reasoning_effort` is still pending (`inputs.json`,
  untouched); one compares against `origin/main`'s launcher, which now passes
  `--keep-going`. No reader of `r1_slots.json` treats the non-null `slots` as
  "R1 done": the validator keys on `max_r1_tail_s`, the kit on `ac_powermode`
  and `slots.I_D`. These 12 belong on the lead's list before CI is read as
  green.

## Numbers dimension

Every tolerance, threshold and assertion the diff adds carries a derivation,
and none is tighter than the 1e-6 rule.

| Number | Where | Derivation given |
|---|---|---|
| S6 = 1.5 C | `r1_slots.json` | ruling 3.2 receipt; the quoted 911 s should read 941 s (F2) |
| 1e-6 rel and abs, C | `_check_soak_reference_consumed` (was 1e-9) | brief's agreement bar |
| 600 + 3 x 1,200 | `r1_arm.R1_G0_BOUND_INCREASE_S` | comment, checked in item 6 |
| 70 s = 60 + 10 | replay projection | capture window plus the ruling's clean-idle offset |
| 1e-6 s, 1e-6 C | new test assertions | brief's agreement bar |
| below 1 s | recorded wait against the replayed 600 s | one 1 Hz poll |
| 0.0005 C | model-B rmse against 0.076 | half the ruling's printed precision |
| 600 to 1,200 s, 0.2 C/min, R_op + 1.5 | model-B release assertions | recorded span, ruled cap, registered slope bar, S6 |
| 200,000 bytes | fixture size | brief's cap |

No exact equality is used on a measured float except identical JSON read back
through identical code. Outside the diff, for the pruning list: the kit's
`_close` uses 1e-9 on S5, S6 and the receipt values; they are identical JSON
floats today, so it refuses nothing.

## Observations outside the diff (no fix asked on this branch)

1. **The 600 s release between A-B-A legs may still make adoption
   inconclusive by construction.** Ruling 3.3 raises the legs' own G0 to
   1,200 s so that the A-B-A can measure something. `aba_adoption` is also
   inconclusive when the sensors-only release before a leg times out. That
   release keeps 600 s, so for legs B and A2 it has to release within about
   12 minutes of the previous leg's D turn ending. Against R_op + 1.5 a
   sensors-only machine has about 2.56 C of room above its own idle (which
   sits 1.06 C lower). On that scale the 900 s-load record is at +4.8 C at
   730 s, which would time out; scaled by slow-pole charge to a 300 s turn it
   is about +2.2 C, which would release. So the outcome is marginal and I
   cannot size it without turn durations. Nothing is refused and the 1 Hz journals allow a
   replay; the desk should read the three leg releases first on the next
   record. The ruling's evidence for keeping 600 s was one sensors-only record
   that began only 2.9 C warm.
2. **Changed sensor picks.** Ruling decision 6 says W1's `delta_slow_c` then
   defaults to 1.5 C through the kit binding. That holds only when R1 keeps
   R0's picks. If R1 changes them, the kit binds the R1-pick band from
   `s7_for_picks`, which is still max(1.0 C, 3 SD). W1 design, after R1.
3. `registered_s6()` reads the same file the R1 driver's registration is later
   committed to. Harmless now; a second R1 after that commit would take the
   first R1's measured S6 as its floor.
4. The planning hook stores R_op under the key `soak_reference_c`, and a leg
   whose G0 timed out still records `deadline_origin` `R1_after_G0_release`.
   Labels only.
5. d-4bit follows X-G with no precool and refuses the night if its G0 times
   out. It is not in the production chain.
