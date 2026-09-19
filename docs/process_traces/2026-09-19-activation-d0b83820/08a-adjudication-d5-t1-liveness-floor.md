# Record 08a — adjudication of cold gate packet 08 (ruling 10 + Opus contract refuter 11): D5-T1 liveness floor (lead, 2026-09-19 08:2x PDT)

## Seats

| Seat | File | Result |
|---|---|---|
| Cold Fable judge (claude -p, detached worktree `wt-coldgate-d0b83820` at `42cc9f35`; validator typo-REFUSE then PASS on packet `5448c4e4…`) | `08-…/10-coldgate-fable-ruling.md` (08:01–08:04 PDT, rc 0) | Q1 (a) DELETE the floor (executed fake-clock probe: zero-service passes, `clock` still dies on the kernel ceiling 3.19 > .92); Q2 (b) fix in round — exact `burn_profile` LCG test (`burn(1) == 1015568748`, state advances, memory profile returns int); Q3 AFFIRM (`.05` preempted, `1e-3` late-start); both same-signature statements NOT FOUND under (a). |
| Opus contract refuter, independent (Agent tool, same worktree) | `08-…/11-opus-contract-refuter.md` | Q1 (d) = the deletion PLUS a deterministic `load_worker` rendezvous test; executed: under (a) alone the production mutation `clock.sleep_until(start)` → `sleep_until(start + duration)` at `scripts/sample_quiet_predicate_evidence.py:869` SURVIVES (0 rows, claimed 0, charged ≈ 0.34 s, all remaining assertions vacuous), and no fake-clock test reaches `:869` (they call `duty_periods` with explicit `start=`); (c) survives the same mutation (0.34 < 0.5). Q2 (b) real hole, not equivalent: `--profile memory` silently becomes scalar; exact loop test `burn(1000) != burn(1)` for both profiles; `work_units` in the row WOULD be a contract change — not taken. Q3 AFFIRM with the same executed lateness list. |

Both seats independently corroborated the seat-06 green (43 OK at `37ca3c35`) and the kernel-ceiling kill of `clock`.

## Adjudication (split verdicts synthesized, not majority-voted)

1. **Q1: DELETE the floor (ruling 10), AND adopt refuter 11's deterministic `load_worker` test.** The judge ruled (a) and named the residual it accepts ("a child that starts, emits no rows and exits 0 passes … proved deterministically by `test_cpu_budget_overshoot_and_frozen_duty`"); the refuter executed the counter-example showing that residual is NOT covered by any existing fake-clock test (the rendezvous line `:869` is outside `duty_periods`). Adding a test-file-only fake-clock test is additive to the ruling, changes no contract, and moves the "did the worker run its window" property to the layer where the scheduler is not a variable — the judge's own structural argument. No reversal of the cold verdict is involved.
2. **Q2: fix in this round.** Test text = the union: refuter 11's two-profile loop (`burn(1000) != burn(1)` for `scalar` and `memory`) plus the judge's exact scalar LCG value on the first call (`burn(1) == (1664525 + 1013904223) & 0xFFFFFFFF`). No row field added. The `memory`-profile buffer-write differential is registered as queue data (lane candidate QUIET-LOAD-MEMORY-PROFILE-DIFFERENTIAL-01), not this round.
3. **Q3: AFFIRMED** as both seats ruled: `.05` on the preempted-burn regression, `1e-3` on the late-start regression. The refuter's optional tightening to `<= .01 + 1e-9` is not adopted (both call `.05` sound; Ed's sensible-gates directive prefers the instrument-sized margin).
4. **Dissent: none.** The magistrate does not overrule any part of ruling 10; item 1 adds to it on the refuter's executed evidence.

## Order

Fix round 3 = seat (Astra high, `WRITE_SCOPE: [tests/test_sample_quiet_predicate_evidence.py]`, brief 10): the one-line deletion, the burn-profile test, the `load_worker` rendezvous test → bench (module twice, expect 45 OK; mutations `cores`, `alignment`, `observer`, `clock`, `catchup-capped`, `burn-noop`, `window-skip` each ≥ 1 failure) → delta re-audit round 3 (fresh read-only seat; both same-signature statements) → PR gate.
