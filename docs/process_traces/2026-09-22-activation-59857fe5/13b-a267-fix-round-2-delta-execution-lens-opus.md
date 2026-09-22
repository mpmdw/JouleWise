# A267 fix round 2 — delta re-audit, EXECUTION lens

Worktree `/Users/edr/code/JouleWise-wt-a267-review3`, detached at `56ea8ae0`, base `489b0953`;
left clean. Baseline and exit both `Ran 234 tests … OK` (58.5 s / 57.2 s). Every mutation was
applied, run, reverted with `git checkout -- .`, and status verified empty. Command form:
`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest <modules>`.

## Findings

**SHOULD-FIX 1 — `joulewise/quiet_predicate_campaign.py:638`: the cured
`attestation_timeout_s` is a CONSTANT, and the new R3.3 test cannot detect that.**
With `CLEANUP_BUDGET_RESERVE_S == ATTESTATION_TIMEOUT_FLOOR_S == 5`,
`max(5, gap − max(1, gap−5))` is **5 for every gap** — executed over pitches 601…1999,
`distinct attestation_timeout_s = {5}`. Failure scenario: replace the whole body with
`return ATTESTATION_TIMEOUT_FLOOR_S` — the derivation from the registration is gone, yet
`tests.test_quiet_predicate_campaign` runs **108 tests OK**. All four positive rows of
`test_the_bound_is_what_the_teardowns_budget_leaves_of_the_gap`
(`tests/test_quiet_predicate_campaign.py:1387-1405`), both pins at `:1421-1424`, the
`attest_burn=5` row and `[5]*12` are satisfied by the floor alone; the ledger's kill 2 works
only because it moves the sum, not the returned value. Cure: one pin under a hypothetical reserve —
`with patch.object(campaign, "CLEANUP_BUDGET_RESERVE_S", 10): assertEqual(attestation_timeout_s(PROTOCOL), 10)`
— which `return ATTESTATION_TIMEOUT_FLOOR_S` fails. Command:
`… -m unittest tests.test_quiet_predicate_campaign` after the body swap.

**SHOULD-FIX 2 — `…campaign.py:766`: the new `temporary.unlink(missing_ok=True)` can itself
raise, and it runs BEFORE the withdrawal it precedes.** It is the first statement of an
`except OSError` handler whose own comment (`:754`) says "One envelope's annotation must never
refuse the NIGHT". If `os.replace` fails and the unlink then fails (read-only/immutable dir,
EPERM), the OSError escapes `record_attestation`; the single production call site
(`:1168`) is unguarded, so it unwinds the envelope loop and the night ends REFUSED — and the
attestation is left at `authenticated`, never withdrawn. Executed:
`patch.object(c.os,'replace',side_effect=OSError) + patch.object(Path,'unlink',raises PermissionError)`
→ `ESCAPED: PermissionError immutable flag | state left = authenticated`. This path did not
exist at `489b0953`. Cure (either): set `state`/`reason` first and wrap the unlink in its own
`try/except OSError: pass`. No test in the delta covers a failing unlink.

**NIT 3 — seat item-2 red tail under-reported.** Claimed `failures=2`; over the same scope
(`AttestationBudgetTests`, `Ran 7`) it is **3** — the two invariant subTests plus
`…_the_registrations_gap_…` (`15 != 5`). Stronger than claimed, but not the observed tail.

**NIT 4 — `tests/…:1416` `assertIn("start_drift_abort_s", PROTOCOL)`** is a key-presence check.
The docstring's claim that the sub-6 s overrun is *detected* by the drift abort is asserted
nowhere; the negative row pins only arithmetic (1 + 5 = 6 > 3).

**NIT 5 — `tests/…:1547-1549`** (`…vanishes_before_the_annotation…`):
`assertTrue(all(v["excluded"] …))` passes on any non-empty exclusion. The journal row pins
`asserted`, so the test is not vacuous, but the summary half is.

**NIT 6 — provenance.** Both new fixtures are tracked and their sha256 match the pins
(`dba7fb7c…eb63`, `da1b28ef…718b`; D3 is 51 B), but `…/SOURCES.md` names neither (seat
deviation 4, WRITE_SCOPE): their provenance now lives only inside a test file.

**NEEDS_RULING 1 — VERIFIED, stronger than claimed.** Mutation A (delete
`and cleanup["cleanup_proven"]` at `:1218`) survives **the whole 108-test module**, not just
`ExitCodePrecedenceTests`. Reading confirms why: the `finally` at `:1195-1196` sets
`outcome = "refused"` whenever the final cleanup is unproven and `:1218` runs after the
`finally`, so `outcome in {"complete","partial"} and not cleanup_proven` is unreachable —
redundant defence, not dead-but-reachable. B and C both go red on `'complete' != 'refused'`,
so the axis IS pinned by execution. Recommendation: option (a), keep and record the
redundancy; deleting it makes the `finally` the sole guard of an rc the ruling cares about.

**Observation (serves cold gate Q1 proof (vi)).** The contention flake reproduced and is now
named: `tests.test_sample_quiet_predicate_evidence.LoadTests.
test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` (subTest `exit_delay=60`),
`-9 != -15` (SIGKILL escalation under load). Failed in two consecutive loaded two-module runs;
**re-run alone: `Ran 1 test … OK`**. Outside the A267 delta.

## Required checks

**(2) End-to-end through the executor harness** (`NetworkTimeControlTests.exercise`, real
`execute`, 12 envelopes each):

| body | state | matched_lines | marker_lines | reason | retained |
|---|---|---|---|---|---|
| exhibit-D3 (zero-match, 1 line) | `authenticated` | 0 | 0 | no applied clock correction… | 12 |
| exhibit-D2 (syslog, 191 lines) | `slew_attested` | **10** | 30 | 10 applied clock corrections… | 0 |
| exhibit-D (compact, 191 lines) | `asserted` | 10 | 30 | **timed log query returned no header** | 0 |

All three ran with `timeout == 5`. Confirms R2.2, R2.3, R2.5 as claimed.

**(3) Bound.** `attestation_timeout_s`: v2 (gap 20) → **5**; 700 s pitch (gap 100) → **5**;
606 (gap 6) → 5 with `cleanup_budget_s` 1, sum 6 ≤ 6; 603 (gap 3) → 5 with cleanup 1, sum 6 > 3.
The boundary row (`slot_pitch_s: 606`) and the negative row (`603`) exist at
`tests/…:1390-1416` and execute (`-v` shows the four subTests and the test `ok`). See
SHOULD-FIX 1 for what they do not pin.

**(5) Byte invariance, `56ea8ae0` vs `489b0953`, identical fakes, body = the syslog header.**
Both trees extracted via `git archive` to `/tmp`; the same driver ran `execute` to completion
and dumped `evidence_outcome.json`, `summary.json`, the envelope journal and the twelve
`session.json`. **105 leaf diffs, 29 shapes, every one ruled or derived:**
(a) `attestation_kwargs[*].timeout` 15 → 5 (Q3); (b) attestation `state`
`asserted` → `authenticated` ×12 and its `reason` — the old guard *rejected* the syslog header,
the defect inverted; (c) the 25 remaining shapes are `summary.json` consequences of 12 retained
envelopes instead of 0 (`retained`, `status` `INCONCLUSIVE` → `SPREAD_RECORDED`, pair
statistics, `*_reason` keys). **`evidence_outcome.json`: zero diffs.** The only non-ruled
difference is `whole_campaign_observer_cpu_s` (0.075683 vs 0.075437) — a live CPU measurement.
A second pair over the failure paths (`blocked`, no session record, no clock stamps) shows the
Q4 delta exactly and only: `window_argv_epoch_s: null` added to all three, nothing else.

## Kill ledger (all re-executed by me)

| # | Item | Mutation | Red tail | Green |
|---|---|---|---|---|
| 1 | header guard | delete `elif not timed_log_has_header(...)` branch | `'slew_attested' != 'asserted'`; **failures=4, errors=1** (Ran 6) | Ran 6 OK |
| 1b | R2.6 | `first.rstrip() ==` → `first ==` | `'asserted' != 'slew_attested'`; failures=2, errors=1 | Ran 6 OK |
| 1c | R2.1 (extra) | constant ← compact header | `False is not true : the 191-line capture`; failures=3, errors=1 (Ran 108) | Ran 108 OK |
| 2 | bound | `gap − cleanup_budget_s` → `gap − CLEANUP_BUDGET_RESERVE_S` | `190 not <= 100`, `30 not <= 20`, `15 != 5`; **failures=3** (Ran 7) | Ran 7 OK |
| 2b | bound (extra) | body → `return ATTESTATION_TIMEOUT_FLOOR_S` | **SURVIVES**, Ran 108 OK | — |
| 4 | unreadable record | delete the two cure lines | `'authenticated' != 'asserted'`; failures=3 (Ran 13), incl. the end-to-end row | Ran 13 OK |
| 5 | temp unlink | delete `temporary.unlink(missing_ok=True)` | extra element `…/session.json.tmp`; failures=1 (Ran 7) | Ran 7 OK |
| 6A | rc clause | delete `and cleanup["cleanup_proven"]` | **SURVIVES**, Ran 108 OK (whole module) | — |
| 6B | finally refusal | delete the `if not cleanup_proven` refusal | `'complete' != 'refused'`; failures=2 (Ran 5) | Ran 5 OK |
| 6C | both | A + B | `'complete' != 'refused'`; failures=2 (Ran 5) | Ran 5 OK |
| 7 | receipt print | `print(...)` → `pass` | `'restore receipt write failed: PermissionError: read-only night' not found in ''`; failures=1 | Ran 7 OK |
| 9 | keyword-only | restore `timeout=ATTESTATION_TIMEOUT_FLOOR_S` | `POSITIONAL_OR_KEYWORD is not KEYWORD_ONLY`; failures=1 (Ran 6) | Ran 6 OK |

No BLOCKER. Every kill the seat claimed reproduces (item 2's count differs, see NIT 3); the one
kill it reported as surviving does survive, for the reason it gave.
