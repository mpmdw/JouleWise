# Delta re-audit of BENCH-REPLAY-START-DRIFT-01 fix round 1 — EXECUTION LENS

Worktree `/Users/edr/code/JouleWise-wt-a267-review3` at `9e7061be`, clean. Delta
`3e299b85..9e7061be`; every number below produced this session. Green at head:
`tests.test_quiet_predicate_campaign` **Ran 125, OK**;
`tests.test_sample_quiet_predicate_evidence` **Ran 76, OK** (load ~2.6).

## Verdict: 0 BLOCKER / 2 SHOULD-FIX / 4 NIT. All nine claimed kills reproduce.

## 1. Kill ledger (mutate → red → restore → green)

| # | mutation | test killed | red tail | restored |
|---|---|---|---|---|
| 1 | `campaign.py:772` handler: unlink FIRST, guard removed | `test_R_C1_a_cleanup_that_raises…` | Ran 9, FAILED(errors=1) `PermissionError: immutable` | Ran 9, OK |
| 2 | `attestation_timeout_s` → `return ATTESTATION_TIMEOUT_FLOOR_S` | `AttestationBudgetTests` | Ran 8, FAILED `5 != 10` | Ran 8, OK |
| 8 | `except (OSError, ValueError)` → `except OSError` | `test_C8_a_NaN_in_the_session_record…` | Ran 9, FAILED(errors=1) `ValueError: … nan` | Ran 9, OK |
| L1 | restore `(session.get("power") or {}).get(...)` | `test_L1_a_real_night_with_a_power_null…` | Ran 14, FAILED `'REPLAY_NEVER_EVIDENCE' == …` | Ran 14, OK |
| L2 | `if os.environ.get(REPLAY_ENV)` → `if False` | `test_L2_a_replay_night_that_wrote_no_session…` | Ran 14, FAILED `'complete' != 'refused'` | Ran 14, OK |
| X1 | ESCALATE branch falls through to PASS | `test_X1_…escalates` | Ran 14, FAILED `'PASS' != 'ESCALATE'` | Ran 14, OK |
| X2 | drop `defects` from the FAIL condition | `test_X2_…not_admissible` **+ `test_X5`** ×3 | Ran 14, FAILED(failures=2) `'PASS' != 'FAIL'` | Ran 14, OK |
| X3 | check moved BEHIND the unreadable `continue` | `test_X3_…journals_are_lost…` | Ran 14, FAILED `'INCONCLUSIVE' != 'REPLAY_NEVER_EVIDENCE'` | Ran 14, OK |
| X4 | digest folded back into the pacing pass | `test_X4_the_sidecar_source_digest…` | Ran 8, FAILED `'ef736eb9…' != '8eea85b7…'` | Ran 8, OK |

Extra: deleting L3's energy-blanking keys kills `test_R5` on `sizing_pairs`
(`[6 pairs] != []`) — not vacuous; the fixture's ordinary night carries `joules = 1`.

## 2. C3 probe — addendum 19's claim, executed independently

Ruled harness, `start_drift_abort_s: 2`, teardown spending its whole budget, query
spending its bound (`attest_burn=5`).

| pitch | gap | cleanup+attest | rc | outcome | abort | slots | `start_drift_s` |
|---|---|---|---|---|---|---|---|
| 603 | 3 | 6 | 2 | refused | `start_drift_abort` (env 2) | 2 | `[0.0, 3.0]` |
| 605 | 5 | 6 | 0 | complete | none | 12 | `[0.0, 1.0 × 11]` |
| 610 | 10 | 10 | 0 | complete | none | 12 | `[0.0 × 12]` |

**CONFIRMED: the overrun does not compound.** Each slot inherits the constant `6 − gap`;
detection is one comparison, not a function of slot count. Addendum 19 §1 stands; ruling
18's "accumulates" sentence is refuted by execution.

## 3. `verdict()` driven on my own synthetic rows

- **Split** (chain 0.40 everywhere, session 0.70 on slots 2, 9): `ESCALATE`,
  `escalate…=True`, `session_slots_over_bar=[2, 9]`, no defects; headline `**ESCALATE**`;
  `main()` → **3**.
- **Twelve anchor-unresolved rows**: no `--smoke` → **FAIL** (24 defects over the two
  fields); `--smoke` → **PASS**, both fields listed in `smoke_exempt_fields`.
- **One `asserted` (slot 7)** → **FAIL**, one defect `{'index': 7, 'field':
  'attestation_state', 'value': 'asserted', 'required': 'authenticated or
  slew_attested'}`, named in the statement; **still FAIL under `--smoke`**.

## 4. Production identity, variable absent

`git archive 3e299b85` → /tmp; same frozen executor end to end at both revisions; whole
result (outcome + summary + journal + sessions + control + calls) normalised and diffed.
**28 differing lines, all accounted for:** 24 × the C7 key
`network_time_attestation_reason` (12 journal rows, 12 `summary["envelopes"][*]`, value
`"no applied clock correction inside the capture window"`); the harness tmpdir path; and
`whole_campaign_observer_cpu_s` (0.011350 vs 0.011073 — a measured CPU figure).
**Session records byte-identical.** Nothing beyond 17b's list. For the magistrate: C7
dictated the key on the *journal row*; it also lands in `summary.json`'s `envelopes[*]`
on **every ordinary night**, not just on a failed rewrite — a second artifact changing
shape on the non-failure path.

## 5. Findings

**SHOULD-FIX 1 — `joulewise/quiet_predicate_campaign.py:1345-1346`: L2's refusal clobbers
a more specific error.** It overwrites `error` unconditionally, while the very next line
(`:1347`) uses `error or …`. On the bench the variable is ALWAYS set. Executed
(`/tmp/a267r3/l2_clobber.py`, pitch-603 abort harness):

```
REPLAY_ENV unset → error = 'ValueError: start_drift_abort: envelope 2 would start
                            3.000 s after its scheduled instant (bar 2 s)'
REPLAY_ENV set   → error = 'replay_recorder'
```

A `start_drift_abort` — the exact failure the bench exists to detect — and a
`pilot summary failed: …` crash both reach `evidence_outcome.json` and `write_refusal` as
an ordinary bench refusal. The verdict still FAILs (slots < expected), so nothing arms;
the diagnostic is what is lost. Fix: `error or REPLAY_REFUSAL_REASON` — compatible with
the ruled L2 regression, where `error` is `None`.

**SHOULD-FIX 2 — `scripts/bench_replay_start_drift.py:361-364`: a coexisting split is
reported as no split.** `escalate = status == "ESCALATE"`, so a run FAILing on an
admissibility defect *and* over the session bar reports
`escalate_chain_pass_session_fail: false` and never names the split. Executed: one
`collector_exit=1` plus session 0.9 on slot 4 → `FAIL | session_slots_over_bar [4] |
escalate flag False`. A reader of `slot_defects` + that boolean concludes the session
figure was fine. Report the split independently of status.

**NIT 1 — `bench_replay_start_drift.py:369-383`.** An admissibility-only FAIL opens
`"max <= 0.5 s NOT shown: over=[] missing=[] recorded=12/12; …"` though the drift bar was
met; twelve bad slots append 24 clauses.

**NIT 2 — `scripts/sample_quiet_predicate_evidence.py:886-896`.** The class docstring
still says "**Only `__init__` is overridden** … `finish` … inherited"; L5 overrides
`finish` at `:929`. The seat logged the deviation; the file's own text contradicts it.

**NIT 3 — `campaign.py:1328`.** `replay_sessions` counts only `recorder_kind ==
"replay"`, so the R5 absent-key night refuses as a replay while
`evidence_outcome.json.recorder_kind` still reads `powermetrics`.

**NIT 4 — `test_L1`'s fixture** synthesises `power: null` by rewriting `session.json`;
its premise (the provenance-refusal path writes `power: null`) is asserted in prose, never
executed. The summary-side behaviour itself is properly pinned.

**RISK, not a defect — X2's bar is unproven satisfiable.** Nothing executed shows a 600 s
replay slot reaching `anchor_status == "bounded"` and `interior_complete_support == True`;
the only live run (60 s smoke) had both false and is exempt. If the anchor cannot resolve
on the full run, the bench FAILs by construction. `slot_rows:266-287` does emit all five
admission fields, so no spurious `None` defect.

**Measured non-finding (rules out an X4↔X1 interaction).** X4's whole-file pre-pass runs
inside the feeder and `ReplayRecorder.start` inherits the first-complete-frame wait, so
its cost sits inside the collector's own start and could inflate the session-level figure.
Measured on the real 130,445,296-byte archived plist: **0.054–0.058 s** (3 warm passes) —
two orders under the 0.5 s bar. Not material.

## 6. Tests passing for the wrong reason — the L1/X3 check

Both fixtures demonstrably take the path they claim. **L1**: the unmodified frozen night
retains **12/12 with no exclusions**, so envelope 07's `clock_anchor_unresolved` and
`retained == 11` are *caused by* the injected `power: null`; the 3e299b85 read kills
exactly `test_L1`. **X3**: moving the check behind the `continue` turns the summary
`INCONCLUSIVE` and kills exactly `test_X3` — proving all twelve envelopes really reach the
unreadable-`continue`. **L3**: non-vacuous (§1). **L5**: the sidecar is hand-written, so
it proves the `finish` read-back only; agreement with a real feeder's K rests on the
seat's live smoke (NIT 4).

Tree left clean; no commits, no pushes; probes under `/tmp/a267r3/`.
