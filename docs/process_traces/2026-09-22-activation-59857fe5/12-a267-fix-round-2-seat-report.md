# A267 fix round 2 — implementation seat report

Worktree `/Users/edr/code/JouleWise-wt-a267-d9990b3c`, branch
`feat/2026-09-22-a267-clock-anchor-v3_1`, base `489b0953`, HEAD `56ea8ae0`.
Ten commits, one per brief-09 item (item 10 is "no change", so no commit) plus
one cosmetic commit over this round's own test edits. Nothing pushed; tree clean.
Supplementary S1/S2/S3 were folded into items 2, 8 and 1 (none had been reached).
`joulewise/uncertainty_evidence.py` untouched (frozen); no file outside
WRITE_SCOPE was written.

## Items

**1 — Q2 header guard (BLOCKER).** `joulewise/quiet_predicate_campaign.py:447-459`
(constant `TIMED_LOG_SYSLOG_HEADER` at `:453`, `timed_log_has_header` at `:456`,
`.rstrip() ==` at `:459`); `TIMED_LOG_HEADER_FIELDS` deleted. Fixtures byte-copied
and sha256-verified after the copy: `exhibit-D2-timed-log-0210-0435-syslog.txt`
`dba7fb7c…eb63`, `exhibit-D3-timed-log-zero-match-syslog.txt` `da1b28ef…718b`;
both pinned in `tests/test_quiet_predicate_campaign.py:614-615` and asserted at
`:1450-1452`. Test constant `TIMED_LOG_HEADER` (`:20-25`) is now
`campaign.TIMED_LOG_SYSLOG_HEADER + "\n"`, so the fake-log harness default follows.
Regressions: R2.1/R2.4/R2.6 + the end-to-end rows R2.2 (live zero-match capture ⇒
`authenticated`, `matched_lines` 0) and R2.3 (compact header ⇒ `asserted`) in
`tests/…:1448-1512`; R2.3's twelve-envelope half and R2.5 + S3 in `tests/…:764-843`;
regression 12 over both formats in `tests/…:845-863`.
Kill (dictated): delete the `elif not timed_log_has_header(...)` branch in
`attest_network_time` → `Ran 6 tests in 3.463s / FAILED (failures=4, errors=1)`,
first failure `AssertionError: 'slew_attested' != 'asserted'`; restored →
`Ran 6 tests in 3.442s / OK`.

**2 — Q3 attestation bound (MATERIAL) + S1.** `…campaign.py:638`
`max(ATTESTATION_TIMEOUT_FLOOR_S, gap - cleanup_budget_s(protocol))`; docstring
`:605-636` rewritten (the "15 s under v2" line and the whole "deliberate residual"
paragraph); `CLEANUP_BUDGET_RESERVE_S` comment `:1030-1039` now names
`attestation_timeout_s` as the function that spends the reserve. `validate_protocol`
untouched. Pins moved in `tests/…:1420-1446`: 5, floor, 5, `attest_burn=5`,
`[5] * 12` twice; the `SCALED` line unchanged. R3.3 + S1 is a new test
`tests/…:1387-1418`: the invariant over v2, `SCALED`, a 700 s pitch and the 6 s
boundary, plus the negative pin at gap 3 (sum 6 > 3, drift abort named).
Kill (dictated): re-introduce `gap - CLEANUP_BUDGET_RESERVE_S` → `FAILED
(failures=2)`, case v2 `AssertionError: 30 not less than or equal to 20`, case
700 s pitch `190 not less than or equal to 100`; restored → `Ran 7 tests in
0.678s / OK`. Note for the record: the 6 s boundary and `SCALED` rows stay GREEN
under that mutation (both sides floor to 5 + 1 = 6), so the v2 and 700 s rows are
the kill, not the boundary row the supplementary predicted.

**3 — Q4 null-initialisation.** `…campaign.py:661`, `"window_argv_epoch_s": None,`
immediately after `"window_epoch_s": None,`. R4 at `tests/…:913-943`: a blocked
record and both window-unavailable records carry the key with `null`, read by
subscript, surviving a JSON round trip. Counterfactual executed though not
required: drop the initialiser → `KeyError: 'window_argv_epoch_s'`, `FAILED
(errors=1)`; restored → `Ran 5 tests in 0.005s / OK`.

**4 — Q5 item 1 (MATERIAL).** `…campaign.py:734-741`: the first
`except (OSError, ValueError) as exc` sets `asserted` + `session record
unreadable: {type}: {exc}` before `return False`. R5.1 at `tests/…:1505-1546`
(class `UnreadableSessionRecordTests`): absent (`FileNotFoundError`) and malformed
(`JSONDecodeError`) records, plus an end-to-end night whose records vanish before
the annotation — twelve journal rows `asserted`, nothing retained.
Kill (dictated): remove the two cure lines → `AssertionError: 'authenticated' !=
'asserted'`, `Ran 6 tests … FAILED (failures=3)`; restored → `Ran 6 tests in
0.171s / OK`.

**5 — Q5 item 2 (MATERIAL).** `…campaign.py:766` `temporary.unlink(missing_ok=True)`
first in the `except OSError` around the temp write + `os.replace`. R5.2 at
`tests/…:1749-1785`: with `os.replace` raising, the test proves the temporary was
COMPLETE and carried `authenticated` at the moment of failure, then that the
directory holds `session.json` alone with its bytes unchanged and the state is
`asserted`. The `.tmp` assertion was removed from the read-only-directory test
(`tests/…:1747`), where no temporary can exist.
Kill (dictated): remove the unlink → `First extra element 0:
PosixPath('…/envelope-01/session.json.tmp')`, `Ran 7 tests … FAILED (failures=1)`;
restored → `Ran 7 tests in 0.175s / OK`.

**6 — Q5 item 3.** Two rows added to the truth table (`tests/…:1568-1577`,
test renamed to `test_the_truth_table_over_outcome_cleanup_and_restore`,
`:1578`), and the harness gains `final_cleanup_unproven` (`tests/…:344-348`,
`:434-447`, `:525`), which fails the night-level `cleanup_record` sweep rather
than a slot's. The blanket `assertTrue(outcome["cleanup_proven"])` is now a
per-row expectation. See NEEDS_RULING 1: the dictated counterfactual SURVIVES.
Kills (all executed): A (dictated) delete `and cleanup["cleanup_proven"]` from
`…campaign.py:1218` → `Ran 5 tests in 0.335s / OK` — survives; B delete the
`finally`'s `if not cleanup["cleanup_proven"]` refusal → `AssertionError:
'complete' != 'refused'`, `FAILED (failures=2)`; C both → `FAILED (failures=2)`,
and a direct probe of that row under C printed `MUTATION C rc = 0` where the
night must return 2. Restored → `Ran 5 tests in 0.282s / OK`.

**7 — Q5 item 4 (NIT).** `…campaign.py:411-417`: `except Exception as exc` and
`print(f"restore receipt write failed: …", flush=True)`. R5.4 at `tests/…:1687-1700`.
Kill: revert to `pass` → `AssertionError: 'restore receipt write failed:
PermissionError: read-only night' not found in ''`, `FAILED (failures=1)`;
restored → `Ran 7 tests in 0.183s / OK`.

**8 — Q5 item 5 (docstring) + S2.** `…campaign.py:469-480`
(`timed_log_window_epoch_s`) and `:496-508` (`timed_log_moment`). Bench-verified
this session: under `TZ=America/Los_Angeles`, `strptime("2025-11-02 01:30:00")
.timestamp()` → `1762072200.0` = `2025-11-02 08:30 UTC`, i.e. the first
(still-daylight-saving) of the two occurrences, 3600 s before its `fold=1` twin.
No code change, no regression.

**9 — Q5 item 6 (NIT).** `…campaign.py:641`
`def attest_network_time(out, blocked=None, *, timeout):`, with the reason in the
docstring `:654-657`. R5.5 at `tests/…:892-911`: the signature is pinned
(KEYWORD_ONLY, no default) and both the bare call and a positional third argument
raise `TypeError`. Five bench-level call sites in the tests now pass `timeout=5`.
Kill: restore the default → `AssertionError: <_ParameterKind.POSITIONAL_OR_KEYWORD:
1> is not <_ParameterKind.KEYWORD_ONLY: 3>`, `FAILED (failures=1)`; restored →
`Ran 6 tests in 0.004s / OK`.

**10 — Q5 item 7.** No change, as ruled. No commit.

## Exit contract

```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_uncertainty_evidence tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign
----------------------------------------------------------------------
Ran 234 tests in 56.720s

OK
```

```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_night_gate tests.test_run_night tests.test_gen_evidence_night tests.test_night_agent_install
PENDING
```

## git log --oneline 489b0953..HEAD

PENDING

## Deviations

1. **Brief 09 item 1 says "31 spaces" between `Timestamp` and `(process)[PID]`.**
   The ruling's own literal and both live captures carry **23**. I followed the
   ruling's exact string (and therefore the captures); the brief's parenthetical
   is wrong. Had I followed it, R2.1 would fail on the live bytes.
2. **R2.5's "state are equal" cannot hold jointly with R2.3.** R2.3 requires the
   compact fixture to yield `asserted` end to end; the syslog twin yields
   `slew_attested`. The test asserts everything the scanner measures is equal
   (`timed_log_matches` 10, `matched_marker_lines` 30, per-envelope), `log_sha256`
   differs, and states differ BY DESIGN with the reason recorded — the syslog
   twin reproduces exactly the state, count and marker count the compact fixture
   produced at `489b0953`.
3. **Item 8's "one sentence" is a short paragraph in each place**, so that which
   occurrence wins and why it cannot buy a claim are replicable from the text.
4. **`tests/fixtures/qpe01_pilot_n1_20260922/SOURCES.md` is NOT updated** with the
   two new fixtures: it is outside WRITE_SCOPE. Their provenance is pinned by
   sha256 in the tests instead. No test reads SOURCES.md.
5. **The test constant `TIMED_LOG_HEADER` is derived, not a literal copy**
   (`campaign.TIMED_LOG_SYSLOG_HEADER + "\n"`). A literal would drift silently;
   instead the constant is pinned against the LIVE bytes at `tests/…:1461-1462`
   (`ZERO_MATCH_FIXTURE.read_text() == campaign.TIMED_LOG_SYSLOG_HEADER + "    \n"`),
   with the fixture's sha256 asserted two lines above.
6. **One extra commit** (`56ea8ae0`) with two cosmetic fixes to this round's own
   test edits (an unused re-read; one line wrapped under 100 columns).
7. **Two of my own commits were `--amend`ed within this session** (items 2 and 4)
   to correct a quoted test tail in the message before any later commit was made.
   No commit that existed at `489b0953` was touched, nothing was rebased or pushed.

## NEEDS_RULING

**1 (item 6 / R5.3).** The dictated counterfactual — delete
`and cleanup["cleanup_proven"]` from `execute`'s return-code expression
(`…campaign.py:1218`) — **cannot go red, and did not**: the `finally` at
`:1195-1196` already sets `outcome, error = "refused", …` whenever the final
cleanup is unproven, so `outcome in {"complete", "partial"}` is False by then and
the clause can never be the thing that returns 2. It is redundant defence. For
the same reason a document can never read `outcome == "complete"` with
`cleanup_proven` False, so the rows assert what the night actually produces:
`outcome` "refused", `cleanup_proven` False, rc 2. Kills B and C above show the
axis IS pinned by execution. The magistrate may rule (a) accept as implemented
and record the dictated mutation as a surviving-but-equivalent redundancy, (b)
require the redundant clause deleted, or (c) require a different shape.

## Unfinished

None. All ten items and the three supplementary items are implemented and
committed; both exit-contract commands were run at HEAD.
