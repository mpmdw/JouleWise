# Refuter brief — ARM-READINESS-FIXTURE-CLOCK-ORIGIN-01 landing (execution + contract lens in one pass; tests-only lane)

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter in the linked worktree you were started in (branch
`fix/2026-09-12-arm-readiness-fixture-clock-origin`, HEAD `100dfb2d`, one commit
over origin/main `ace4cc3c`: `git diff ace4cc3c..HEAD`). You may run tests
(temp dirs allowed) but must not edit tracked files; tree must end clean.
Reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
41 (root cause), 43 (seat brief), 44 (seat report). Never touch
`/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3`
allowed), `/Users/edr/JouleWise-measurement-20260913-derivation`, or
`/Users/edr/night-custody`. `python3 -m unittest` only; no sudo.

Try to BREAK it:
1. Fence: `git diff --stat ace4cc3c..HEAD -- joulewise scripts configs` must
   be empty (paste). Any change to a pre-existing assertion? quote.
2. Isolation: cut, in memory, (a) the sampled origin back to literal 1, (b)
   the pass-through to the assembler, (c) each of the two new regressions'
   synthetic clocks (7.5 days → 0; +8 days → +1 s); one selected test per
   cut with `Ran N` + result. A surviving cut on (a)/(b) is a blocker.
3. Semantics: does authoring at the live monotonic time weaken any test
   that RELIED on the deterministic origin 1 (e.g. an expiry test that
   computed `valid_until` expectations from 1, a golden receipt digest, a
   boot-session comparison)? grep for `604800000000001`, `valid_until`,
   `now_monotonic_ns` in the three modules and quote any dependent
   expectation; a now-vacuous expiry test is a should-fix.
4. Does the cure hold on a FRESH host (monotonic small) and on a host past
   7 days? Run one of the seven previously failing tests with
   `time.monotonic_ns` monkeypatched to 1e12 and to 8e14 (in memory) and
   paste both result lines.
5. Run the seven previously failing tests by dotted name (brief 40 lists
   them; the real-boot ACID one may skip in a sandbox — say so) once; paste
   the result line; `git status --short` empty.

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit with citations; explicit "no blocker found" if
none. Under 8000 bytes.
