# Executing review (Sol 6.1 xhigh, non-author): PR #483 block-4 qualification code, delta since 898c49a7, at __HEAD__

Worktree: /Users/edr/code/JouleWise-wt-dd5-intrev, detached at __HEAD__. Whole diff: `git diff origin/main...__HEAD__`. **Focus: `git diff 898c49a7 __HEAD__`** (lanes X5-X10 and the merges of main). Scratch /tmp/dd5-intrev2/ only.

Spec: the registration draft and ruling 76 with addenda A-E on `origin/design/2026-10-04-v5-qualification-block`:
- `configs/campaigns/v5_qualification_25g83/registration_block4_draft.md`;
- `docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md`;
- record 44, the sizing.

Prior findings that must stay fixed:
- your review at 898c49a7 (`/Users/edr/night-archive/desk-day-v5/sol-intrev.md`, F1-F5);
- the cold Fable pass at 898c49a7 (`/Users/edr/night-archive/desk-day-v5/fable-int.md`, B1, B2, M1-M3).

What landed since then:
- **X5:** addendum C.
- **X6:** your F2-F4.
- **X7:** your F5, as the attempt-history chain and census, the admission re-arm, `s2`, and the NULL restore (addendum D items 1 and 5).
- **X8:** the sealed `prewindow_check.sh` restored, a T-0 dwell of its own, and 41 fixtures.
- **X9:** G10 after `a2`, scheduled by measured offset, with the preflight (addendum D item 3).
- **X10:** the T-0 stage cap, the window formula and the stream bounds (addendum E).

Hunt by executing code for defects that would:
- (a) admit a bad window or promote a non-claim byte;
- (b) refuse or RECOVER a good `s1`, `a1` or `a2`;
- (c) leak an energy, power or per-member duration into a public output;
- (d) let an observation-producer fault abort the chain;
- (e) waste an armed window: a refusal that fires only after the launch is consumed;
- (f) let an attempt be omitted from, or double-counted in, the attempt history;
- (g) let the NULL restore drop a row it should not, or run after `chain.started`;
- (h) let G10 count without a real resync, or spend Ed's attempt when the preflight should have stopped it.

Mutate guards and watch tests fail. Run `tests/test_v5_*.py tests/test_harvest_v5_*.py tests/test_t0_rehearsal.py tests/test_t0_anchor_positive_control.py tests/test_capture_t0_anchor_positive_control*.py tests/test_kernel_clock.py tests/test_arm_readiness_evidence_t0.py tests/test_capture_t0_step.py tests/test_prewindow_check.py tests/test_revision6_seal.py` (TMPDIR=/tmp/dd5-intrev2). Watchdog `BindSupervisionProcessTests` timing failures inside the sandbox are a known artefact (addendum D item 6).

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`. Then the findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and execution evidence.

WRITE_SCOPE: []
No background processes. Finish in this turn.
