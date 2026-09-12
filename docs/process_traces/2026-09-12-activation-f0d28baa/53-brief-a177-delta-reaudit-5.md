# Delta re-audit brief — A177 after the packet-50 amendments (mechanism clauses only; reference reads discharged)

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter re-auditing `git diff 572dcb58..HEAD` (HEAD `6714ce96`, branch
`fix/2026-09-12-fixture-sentinel-controller`, PR #324). You may run tests
(temp dirs allowed) but must not edit tracked files; tree must end clean.
Read first, in this order, from
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
`50-coldgate-packet-a177-isolation-rule-scope/11-magistrate-synthesis-ruling-50-with-opus-amendments.md`
(the recorded reading: clauses = mechanism; terminal oracles exempt; a
direct call to the production function under test on argv-witnessed inputs
is a REFERENCE READ discharged by `tests/test_run_campaign.py:9636-9646`,
so `timeout → 0` / `_interval_ms → constant` substitutions are NOT findings),
then `52-refuter-a177-delta-4-astra-report.md` (your prior audit: R1 config
witness unbound — the delta cures it by deriving the interval from the
recorded config and cross-checking argv `-i`; R2 = reference read).
Never touch `/Users/edr/code/JouleWise` (read-only use of its
`.venv/bin/python3` allowed) or `/Users/edr/JouleWise-measurement-20260913-derivation`.
`python3 -m unittest` only.

1. Mechanism cuts on the delta, in memory, one selected test each, `Ran N` +
   result: (a) recorded config → a substituted 40 Hz config (must now FAIL
   on the argv `-i` cross-check — paste); (b) `assertEqual(len(bounded_captures), 1)`'s
   mechanism: make the adapter record a second bounded capture (e.g. append
   twice) → must FAIL; (c) the production counterfactual floor 15.0 → 75.0
   in `joulewise/adapters/powermetrics.py:1470` (in memory) → the inequality
   must FAIL while everything else passes; (d) cure removed → report 19's
   signature (paste reason lines).
2. Same-signature statement (own line): does the delta add any MECHANISM
   clause without a killer (reference reads excluded)? yes/no.
3. `python3 -B -m unittest tests.test_controller -q` (venv) once; paste the
   result line; `git status --short` empty.

Report (claude-codex-report/v1, genre review): per-cut table; findings
tiered blocker / should-fix / nit (mechanism only); explicit "no blocker
found" if none; the same-signature line. Under 5000 bytes.
