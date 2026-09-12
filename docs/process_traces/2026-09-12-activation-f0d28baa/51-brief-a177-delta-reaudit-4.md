# Delta re-audit brief — A177 after cold gate 50 (mechanism clauses only, per ruling 50 Q1)

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter re-auditing `git diff 74a547cd..HEAD` (HEAD `572dcb58`, branch
`fix/2026-09-12-fixture-sentinel-controller`, PR #324; the diff is cold-gate
ruling 50 Q2's exact code change: the recorded `timeout_s` is replaced by the
recorded `config`, and the test reads production's `_capture_timeout_s` for
the inequality; the mirrored formula is gone). You may run tests (temp dirs
allowed) but must not edit tracked files; tree must end clean. Read first:
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/50-coldgate-packet-a177-isolation-rule-scope/10-coldgate-fable-ruling.md`
(Q1 defines what a clause is for this audit: MECHANISM — wiring, fixtures,
mocks, observation arithmetic — not terminal oracles; oracle edits are
discharged by the killer record, so do NOT report assertion deletions or
oracle weakenings as findings) and `46-refuter-a177-delta-3-astra-report.md`
(your prior audit). Never touch `/Users/edr/code/JouleWise` (read-only use
of its `.venv/bin/python3` allowed) or
`/Users/edr/JouleWise-measurement-20260913-derivation`. `python3 -m unittest` only.

1. Mechanism cuts on the delta, in memory, one selected test each, `Ran N`
   + result: (a) `"config": config` → `"config": None` / a different
   config object; (b) the production call `_capture_timeout_s(...)` →
   a constant 0 / a huge constant (observed-side arithmetic: if a huge
   constant survives, say why — the ruling predicts the inequality fails);
   (c) the ruling's PRODUCTION counterfactual: `joulewise/adapters/powermetrics.py:1470`
   floor 15.0 → 60.0 in memory — the inequality must FAIL while every other
   assertion passes (paste); (d) the cure removed (bounded `--no-sleep`) →
   report 19's signature (paste the reason lines).
2. Confirm no `15.0` / `1.5 + 10` mirror remains in the regression (grep)
   and that `registry.adapter` is the instance that ran (quote the
   assertion).
3. Same-signature statement (own line): does the delta add any mechanism
   clause without a killer? yes/no.
4. `python3 -B -m unittest tests.test_controller -q` (venv) once; paste the
   result line; `git status --short` empty.

Report (claude-codex-report/v1, genre review): per-cut table; findings
tiered blocker / should-fix / nit (mechanism only); explicit "no blocker
found" if none; the same-signature line. Under 6000 bytes.
