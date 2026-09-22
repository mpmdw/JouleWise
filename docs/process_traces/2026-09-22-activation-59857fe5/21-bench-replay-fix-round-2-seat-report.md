# BENCH-REPLAY-START-DRIFT-01 fix round 2 — seat report

`/Users/edr/code/JouleWise-wt-replay`, branch `feat/2026-09-22-bench-replay-start-drift`,
base `9e7061be`. Four commits, one per item; no push, no amend; tree clean.

## Item 1 (exec SF1 = contract N1) — `a8656d4b`
`quiet_predicate_campaign.py:64` new `replay_refusal_error(error)`; call sites
`:1355` (summary refusal) and `:1366` (executor's own environment). Dictated
combined form, plus a containment guard so the marker is not appended twice —
required: on an ordinary bench night BOTH sites fire (R5), and the naive combine
gave `replay_recorder; replay_recorder`, breaking `test_R5:2098`.
Regression `test_D1_…keeps_its_own_error_beside_the_replay_marker`
(`tests/test_quiet_predicate_campaign.py:2245`): ruled C3 pitch-603 harness (3 s
gap, 6 s of floors spent on the fake clock) with `REPLAY_ENV` set → rc 2, journal
`abort: start_drift_abort`, `outcome.error` holds `start_drift_abort: envelope 2`
AND ends `; replay_recorder`, marker count 1.
Kill (unconditional assignment restored at `:1366`): `AssertionError:
'start_drift_abort: envelope 2' not found in 'replay_recorder'` — Ran 15, FAILED
(failures=1); restored Ran 15, OK.

## Item 2 (exec SF2) — `709b1638`
`scripts/bench_replay_start_drift.py:381` `session_bar_exceeded =
bool(session_over)`, returned beside the unchanged
`escalate_chain_pass_session_fail` (kept = `status == "ESCALATE"`, its literal
name); the FAIL statement appends the over-bar session slots and max; `markdown:452`
prints `Session bar exceeded (true whatever the status):` on its own line and the
escalation line now states its meaning.
Regression `test_D2_…reports_the_split` (`tests/…:2604`): `collector_exit=1` on
slot 7 + session 0.9 on slot 4 → FAIL, flag True, `escalate…` False (executed
counterfactual), statement names slot 4's figure, markdown line present; ESCALATE
and both-under cases too.
Kills: `session_bar_exceeded = escalate` → `False is not true`; statement clause
dropped → `'the session-level bar is exceeded too (max 0.900 s > 0.5 s on slots
[4])' not found in 'max <= 0.5 s NOT shown: over=[] missing=[] recorded=12/12;
slot 7 collector_exit=1 (required 0)'` — Ran 16, FAILED (failures=1) each;
restored Ran 16, OK.

## Item 3 (exec NIT1) — `7e4b2ecc`
`bench_replay_start_drift.py:320` `DEFECT_SLOT_CLAUSE_CAP = 3`; `:395-412` the
FAIL statement leads with `N/12 slots NOT admissible, so their drift figures are
not a measurement of the finalisation tail: …` whenever the drift bars were met
(complete, no `over`, no `missing`), closes with the chain max, and spells out at
most three defective slots before `… and N more`. `slot_defects` unchanged.
Regression `test_D3_…opens_with_the_defect_and_stays_short` (`tests/…:2724`):
twelve unresolved slots → 24 defects, statement starts `12/12 slots NOT
admissible`, holds `… and 21 more`, no `NOT shown`, length 322 < 600;
counterfactual (one chain figure over the bar) keeps `max <= 0.5 s NOT shown:
over=[3]`; three defective slots stay fully named.
Kills: drift-first branch forced → `False is not true : max <= 0.5 s NOT shown:
over=[] missing=[] recorded=12/12; …`; cap removed → `'… and 21 more' not found`
(kills `test_X2` too) — Ran 17, FAILED (1) / (2); restored Ran 17, OK.
`test_X2`'s four-fragment loop amended to three fragments + `assertIn("… and 1
more")` + `assertNotIn("slot 8 interior_complete_support=False")`; its
`slot_defects` assertion untouched.

## Item 4 (exec NIT2 = contract N2) — `58a2e42b`
`scripts/sample_quiet_predicate_evidence.py:887` docstring names both overrides
and the forcing reason for `finish`: the feeder derives K at its own spawn and
writes the sidecar only when it stops, so it does not exist while `__init__`
runs, and `super().finish()` is where the feeder is guaranteed to have exited;
best-effort shape stated. Docstring only.

## Exit tail
One run, `tests.test_uncertainty_evidence tests.test_sample_quiet_predicate_evidence
tests.test_quiet_predicate_campaign tests.test_run_night`:
**Ran 493 tests in 316.756s … OK**. No wall-clock race fired. No smoke. `git
status --short` empty.

## `git log --oneline 9e7061be..HEAD`
`58a2e42b` item 4 · `7e4b2ecc` item 3 · `709b1638` item 2 · `a8656d4b` item 1.

## Deviations
1. Item 1 uses a named helper, and the combine is guarded against a duplicate
   marker (not optional — see above).
2. Item 3 forced an edit to the ruled `test_X2`: four defective slots sit one
   over the dictated cap. Only statement fragments moved.
3. Item 2 kept `escalate_chain_pass_session_fail` as `status == "ESCALATE"` (the
   brief's first option) rather than renaming.

## Observation (not fixed, outside the four items)
`quiet_predicate_campaign.py:1357` (`"pilot summary failed: " + str(exc)`) still
clobbers an earlier `error`, so on that path a `start_drift_abort` text is still
lost before the marker is appended. Flagged for the magistrate.

## NEEDS_RULING
None.
