# CONSULT (rule 11 escalation) then implement — FIXTURE-SENTINEL-CONTROLLER-01: the minimal self-protecting regression shape

WRITE_SCOPE: ["tests/test_controller.py"]

You are an xhigh design-consult seat with licence to disagree with the
magistrate, in the linked worktree you were started in (branch
`fix/2026-09-12-fixture-sentinel-controller`, HEAD `0ff8ac04`, PR #324).
Tests only (kernel fence). Never move HEAD, never push, never touch
`/Users/edr/code/JouleWise` (read-only use of `/Users/edr/code/JouleWise/.venv/bin/python3`
allowed) or `/Users/edr/JouleWise-measurement-20260913-derivation`.
`python3 -m unittest` only.

## Why this is a consult and not fix round 3

Two consecutive fix rounds on the regression
`HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
each added test machinery whose own clauses had no killing test: round 2
(delta audit 33 R1) — the stress adapter wiring could be deleted and the test
still passed even without the cure; round 3 candidate (delta audit 37 R1) —
the `wraps=validate_bundle` mock wiring can be replaced by a canned `[]` and
zero calls reach the real validator; plus 37 R2, a duplicated drift assertion.
Same generator twice: "the fix adds mock/record wiring that itself needs
isolation proof". The standing escalation rule says the next spend is a
consult. Read, in this order, from
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
37, 35, 33, 31, 30, 04, and the root cause
`docs/process_traces/2026-09-10-activation-96bfeca7/19-rootcause-controller-idle-drift-local-astra-report.md`.

## Part 1 — design (write this section of your report BEFORE editing)

Question: what is the MINIMAL regression that (a) detects report 19's defect
(post-idle bounded capture times out → salvaged drift `unknown` /
`post_idle_unavailable` → strict validation mismatches) when the bounded
`--no-sleep` cure is removed; (b) fails when its own stress injection is
disconnected or weakened below the production timeout; (c) contains NO
clause without a killing test — where "clause" is every guard, record,
mock, expectation, and arithmetic term the test adds beyond the pre-existing
happy-path assertions; (d) is CI-safe (continuous captures unstressed —
round 1's cure) and pins no host-dependent value.

The magistrate's hypothesis, which you may reject with reasons: the mock
wiring is the problem, not the cure. Call the real validator DIRECTLY
(`self.assertEqual(validate_bundle(bundle_path, strict=True), [])`, once
after the run and once after fresh reduction) so there is no delegation
clause to protect; keep exactly one stress witness — the stressed adapter
records the bounded capture's (scale, count, interval_s, timeout_s, argv)
and the test asserts `scale >= FLOOR`, `count * interval_s * scale >
timeout_s`, `"--no-sleep" in bounded argv`, `"--no-sleep" not in continuous
argv`, and that the record EXISTS (kills the wiring cut); drop every
diagnostic-only field from assertion messages that carries no decision;
drop the duplicated drift assertion (37 R2). State the clause inventory of
your design (numbered) and, for each, the ONE cut and the ONE assertion that
kills it — before writing code. If your inventory has a clause with no
killer, redesign until it has none.

## Part 2 — implement the ruled design

Replace the round-2 machinery with the design from Part 1 (net LOC should
FALL relative to 0ff8ac04; report the number). Then run the isolation sweep
IN MEMORY over your own inventory (every clause, one cut each, selected
test, `Ran N` + result), including: wiring removed; wiring removed AND
`--no-sleep` removed (must FAIL on the witness); validator replaced by a
canned `[]` (must be IMPOSSIBLE by construction — explain — or FAIL); the
killed cut (cure removed → report 19's signature, paste the reason lines).
`python3 -B -m unittest tests.test_controller -q` with the venv interpreter
and with system 3.14; `git diff --check`. Do NOT commit; report
`git status --short` and `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Part 1 (design, clause inventory with killers, where you disagree with the
hypothesis and why); Part 2 (per-cut table, killed-cut lines, LOC delta,
per-interpreter results); any NEEDS_SCOPE/NEEDS_RULING. Under 8000 bytes.
