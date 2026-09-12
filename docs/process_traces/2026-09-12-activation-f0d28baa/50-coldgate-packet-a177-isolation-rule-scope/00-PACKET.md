# Cold-gate packet 50 — scope of the isolation rule over a test's own terminal oracles and mirrored formulas (rule 11: third round on one regression)

Assembled 2026-09-12 ~06:22 PDT by the resident magistrate (activation f0d28baa). Mechanically assembled: exhibits are verbatim copies; the
magistrate wrote only this file.

## Trigger

PR #324 (kernel lane A177 FIXTURE-SENTINEL-CONTROLLER-01, branch `fix/2026-09-12-fixture-sentinel-controller`, HEAD 74a547cd, tests-only) rewrites
`tests/test_controller.py::HappyPathTests::test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` so that a bounded post-idle capture is
stress-tested (12× fixture sleep, `--no-sleep` cure) and the defect of root-cause record 19 (capture timeout → salvaged drift `unknown` → strict
validation mismatch) is detected when the cure is removed. Three delta re-audits in a row have reported surviving in-memory cuts on the regression's
OWN clauses: audit 33 (stress wiring deletable), audit 37 (validator `wraps=` mock replaceable by a canned `[]`), and, after a rule-11 design consult
(Exhibit E: 33 cuts, each killed by a named assertion, net −63 LOC), audit 46 (Exhibit D): R1 — the test's MIRRORED production timeout formula
`max(15.0, nominal_s*1.5+10.0)` survives removal of its `15.0` floor (the run sits in the affine regime) and the inequality
`count×interval×scale > timeout` survives replacing `timeout` by 0; R2 — deleting any of the twelve added expectations, weakening `strict=True` to
`strict=False`, replacing a validation result by a canned `[]`, or turning the policy comparison into `expected == expected` all "survive". Audit 46
itself says: "The lead must either require durable protection for these cuts or explicitly exempt terminal-oracle edits; adding recursive assertions
without that ruling would repeat the overbuild problem."

The isolation rule (Exhibit A, ruling 69 Q2; Exhibit B, its Opus amendment A5): a fix-round delta re-audit re-cuts, one term at a time, every clause
the round's diff adds or changes, running the single test selected for each cut; a surviving atomic cut is should_fix. Record 88 (Exhibit C) adds the
operand-collapse cut shape (collapse every max/min/selector to each operand). Neither text says whether "clause" includes the test's own assertions
(terminal oracles) or a formula the TEST mirrors from production for an equality check.

## Q1 — does the isolation rule's "clause" include a test's own terminal oracles?

Rule whether (a) deleting an added assertion, (b) weakening an assertion's mode (`strict=True → False`), (c) replacing an oracle's expected value by
a tautology (`expected == expected`, canned `[]`) are cuts the rule requires a SELECTED TEST to kill — which, for a test's own assertion, can only be
satisfied by a second test asserting that the first asserts (the regress the consult refused) — or whether the rule's "clause" means the MECHANISM
the test builds (fixtures, wiring, arithmetic that decides what the test observes) and its INPUT counterfactuals (falsified inputs must fail the
oracle: Exhibit E's method), with terminal-oracle edits exempt. Give the exact sentence to record as the reading of ruling 69 Q2 / A5 (you are not
amending doctrine; you are reading it for this case — say so if you find the texts already decide it).

## Q2 — the mirrored formula and the inequality (Exhibit D R1)

The regression asserts the bounded capture's recorded timeout equals a formula copied from `joulewise/adapters/powermetrics.py` (~:1470,
`max(15.0, nominal_s*1.5+10.0)`) and that `count×interval_s×scale > timeout`. Rule the smallest correct shape among: (i) keep the mirror and add a
second regime (baseline conditioned to ~1.5 s) so both branches of the `max` are covered; (ii) delete the mirrored formula and read production's
timeout through production's own function/attribute (ONE home; then no floor term exists in the test to cut) while keeping the inequality;
(iii) delete both the formula equality and the inequality (the witness record + `--no-sleep` presence + the killed-cut evidence suffice);
(iv) other. State which existing production test, if any, already protects the timeout formula (grep `capture_timeout` / `15.0` in `tests/`), and
give the isolating counterfactual for whatever the regression keeps.

## Q3 — classification (for the record)

Audit 46 says "same-signature: YES — new unprotected arithmetic and terminal-oracle clauses". Given Q1, are R1/R2 the same class as audits 33/37
(mechanism clauses without a killer) or a different class (oracle edits the rule does not cover)? One paragraph.

## Constraints on the judge

Read-only; probes: `git show 74a547cd:<path>`, `git diff ace4cc3c..74a547cd -- tests/test_controller.py`, `grep`, `sed -n`, and running the single
regression by dotted name with `/Users/edr/code/JouleWise/.venv/bin/python3 -m unittest` (about 20 s; temp dirs allowed). Do not edit tracked
files. Never touch `/Users/edr/code/JouleWise` beyond that interpreter, `/Users/edr/JouleWise-measurement-20260913-derivation`, or
`/Users/edr/night-custody`. Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (the
reading, one sentence to record, and the reason); Q2 (the ruled shape, the exact code change in a few lines, the isolating counterfactual);
Q3; Executed probes. Plain words; define terms at first use.
