# Sizing round 2 (Sol 6.1 xhigh): recompute block-4 sizing at idle 75 s, with the T-0 lead time and the stream maximum

Worktree: /Users/edr/code/JouleWise-wt-dd5-sz (branch `lane/2026-10-05-b4-sizing2` at bda1c180 = PR #483 with origin/main, which includes #481's idle-75 regeneration). Scratch /tmp/dd5-sz/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics or Metal.

Inputs:
- record 44 as it stands: `git show origin/design/2026-10-04-v5-qualification-block:docs/process_traces/2026-10-04-desk-day-v5/44-block4-sizing.md`;
- the registration draft on the same branch (§4, §5);
- ruling 76 addenda A, B and D (same branch, `76-r1-fold-ruling.md`);
- memo items 1.8, 1.9 and 1.14 (`~/night-archive/ia-0a40/MEMO.md` lines 206-236 and 282-295);
- the committed allowance file `configs/campaigns/v5_qualification_25g83/sizing_allowances.json`.

Blindness: block-1 to block-3 archives may be read for **timing fields only**. Never read, print or write an energy or power value. No `s1` byte exists; use none.

Recompute, each as a source-bound allowance `{seconds, source:{path, sha256}, source_pointer}`:

1. **`T_stream_max`.** The longest continuous sampler stream any `s1` member can produce at the regenerated configs: science, NEG-8 bound and references. It includes idle admission with the policy's one retry and guards, and the measured phases. It excludes the cooldown only if the code proves the cooldown runs on its own sampler (cite file:line). Derive the idle slice from the committed configs' `sampling.idle_seconds` and the real record cadence. Then evaluate the frequency gate `H_max + 0.10 ms + (|f| + 0.25 ppm) · T_stream_max ≤ 5 ms` with `H_max` = 3.60 ms at today's `f` = −3.17 ppm. Report the largest `|f|` that passes, and say whether the gate code's refusal at the old sizing (X3 F2) now clears. Also check the lower bound: every stream must be at least 60 s (memo 1.8), with margin.
2. **`T_pack_t0` = X, the T-0 lead time** (memo 1.9). The writer schedules the first T-0 capture at `t0 − pack_t0` (`scripts/write_v5_qualification_plan.py:585`). Derive X from the code. It must cover:
   - the OFF settle (the first capture or author boundary at least 600 s after the OFF receipt on both clocks);
   - the T-0 clean dwell (600 s minimum, cap from the policy and `scripts/run_night.py`);
   - the six captures, authoring and verification.

   It must also satisfy G4's 600-3600 s T-0 span. State the band of admissible X, and choose X with its margin. If no X satisfies every bound, FLAG it with the arithmetic.
3. Every other component of record 44 at idle 75 s:
   - `E_small`, `E_large` and the auxiliary members: the idle admission must reflect 75 s;
   - `T_bound_and_references`; settles; custody; shutdown;
   - `NIGHT_PROGRAMMED_SPAN_S_s1` and `WINDOW_MAX_S_s1`, and whether the 2700 s dwell cap still belongs outside the span once the T-0 dwell sits inside X;
   - the latest chain start, and the driver's emergency, courier and dead-man deadlines.
4. **Sources must be production sources, not test fixtures.** Today every allowance points at `tests/fixtures/v5_qualification/sizing_allowance_source.json`. Write the derivation source to `configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, with each archive path and sha256 it drew from, and repoint the production allowance file at it. Keep the test fixture for the tests. If a test pins the production file's digest, update it honestly.
5. If the writer or gate code needs a change (for example a `pack_t0` band check, or a stream lower bound in `size_window`), do not edit it: lanes X7 and X9 are editing the writer. FLAG the exact change with file:line.

Run the writer's sizing path on the new file, and run `tests.test_v5_qualification_plan tests.test_v5_block4_clock tests.test_v5_block4_x6`. Report a table of every component (old seconds → new seconds → source → derivation) and the gate evaluation. Finish in this turn; FLAG what you cannot close.

WRITE_SCOPE: ["configs/campaigns/v5_qualification_25g83/sizing_allowances.json", "configs/campaigns/v5_qualification_25g83/sizing_sources/**", "tests/test_v5_qualification_plan.py", "tests/test_v5_block4_clock.py", "tests/test_v5_block4_x6.py"]
