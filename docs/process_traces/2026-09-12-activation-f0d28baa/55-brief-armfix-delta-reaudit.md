# Delta re-audit brief — ARM-READINESS-FIXTURE-CLOCK-ORIGIN-01 fix round 1 (Opus 49 fix-first: horizon read from the registry)

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter re-auditing ONLY `git diff 100dfb2d..HEAD` (HEAD `61872ccf`, branch
`fix/2026-09-12-arm-readiness-fixture-clock-origin`, PR #327). You may run
tests (temp dirs allowed) but must not edit tracked files; tree must end
clean. Prior reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
48 (landing refuter, clean + nit N1), 49 §PR #327 (the fix-first). Never
touch `/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3`
allowed), `/Users/edr/JouleWise-measurement-20260913-derivation`, or
`/Users/edr/night-custody`. `python3 -m unittest` only.

1. Mechanism cuts in memory, one selected test each, `Ran N` + result:
   (a) `self.horizon_ns` read from the wrong policy kind (e.g. `CLOCK_ATTESTATION`,
   21600000000000) → which test fails and why; (b) origin = `1 + horizon`
   exactly (no 1/14 margin) → does the fresh-evidence test still prove
   long-uptime coverage (is `origin > horizon` still true)? state whether
   refuter 48's N1 (no explicit precondition guard) is now moot or still a
   nit; (c) expiry probe at `origin + horizon` exactly (boundary) → PASS or
   refused? quote production's comparison operator at
   `joulewise/arm_readiness.py:6297` and say whether `+ 1_000_000_000` is
   the right margin.
2. ONE home: confirm the registry path and that no day constant remains in
   the module (grep `86_400`); confirm the kind literal `"ACCEPTANCE_OWNER"`
   matches the receipt kind the test authenticates (quote both).
3. Run `tests.test_arm_readiness_dry_run` whole once (about 70 s); paste the
   result line; `git status --short` empty.

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit; explicit "no blocker found" if none. Under 4000 bytes.
