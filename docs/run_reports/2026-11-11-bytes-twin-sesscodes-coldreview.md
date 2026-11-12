# BYTES twin session codes (RL-82 reading A): cold review

2026-11-11, 21:15 PST. Reviewer: Claude Fable 5.2, independent of the build seat (Sol).
Target: `fix/2026-11-11-bytes-twin-sesscodes` at `23b82a4b7`. Base: `fix/2026-11-11-bytes-twin-anchor` at
`a0d5b19c4` (admitted). Seat report: `docs/run_reports/2026-11-11-bytes-twin-sesscodes.md`.

## Verdict: REJECT at `23b82a4b7`

The change is right where it applies, but it is incomplete, and RL-82 condition 3 fails.

- **18 of the 19 synthetic campaigns have zero fields above the bar. `withheld` has 36**, all `flags`, all at the
  held-out stage, all in cells whose withheld store is missing (finding F1).
- The analysis lists the session's codes in those cells. The twin still prints the hard-coded list
  `["bytes.withheld_missing"]`.
- At the base this campaign was clean (0 above the bar in the anchor fix's cold review). The branch's fixture now
  carries session codes, so the branch turns a passing suite test into a failing one.
- Everything else checked holds: the per-cell rule in computed cells, the import fence, the estimator digest, the
  exporter, the regression test and the mutants.

The repair is narrow and is described under F1. Re-review can be limited to that delta plus a rerun of the
`withheld` campaign. I changed no code.

The fit stage is not affected. The `withheld` campaign has zero fields above the bar at fit and at both blinded
stages, and a missing withheld store concerns held-out rows only. So RL-82 condition 4 (the fit-set rerun) does
not depend on F1. Conditions 3 and the held-out agreement do.

## Check by check

| # | Check | Result |
| --- | --- | --- |
| 1 | Per cell, the twin lists run codes ∪ session codes as RL-82 and §6/§15 define flags; nothing else changes | **Fails in one cell kind, passes elsewhere.** Computed and refused cells: `sorted(run codes ∪ meter codes ∪ session codes)` over the kept rows (all rows when the cell is not `ok`), which matches the analysis line for line. Session code = no `scope.run_id`, read from `derived/flags.jsonl` and acceptance `emitted_flags`, the same rule as `archive_records`. Missing-withheld cells: session codes absent (F1). Diff outside flags: none; 14 lines in three hunks. |
| 2 | Twin imports nothing from `joulewise` | **Pass.** AST import set is standard library only; no `importlib`, `__import__`, `exec`, `eval` or `sys.path` use. `FenceTests` (3) pass, including the run with `joulewise` unimportable. |
| 3 | Estimator digest; exporter identical to base | **Pass.** `joulewise/bytes_analysis.py` sha256 is `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`. `git diff a0d5b19c4 23b82a4b7 -- joulewise/` is empty; `joulewise/b6/export_runs.py` is blob `0f659ff4b` at both. |
| 4 | Regression test fails at base, passes at head | **Pass.** The tests do not exist at the base, so I ran the head's tests against the base's twin (head tree, `scripts/bytes_twin.py` from `a0d5b19c4`). `SessionFlagTests.test_both_archive_sources…`: ERROR (`KeyError: 'session_flags'`). `AgreementTests.test_session_codes_at_archive_stages`: FAIL, 312 above the bar, all `flags` (72 fit, 240 held-out). At the head both pass. The seat's "72" is the fit stage alone. |
| 5 | Mutants | **All four requested kinds are killed.** Two survivors are equivalent mutants. Table below. |
| 6 | Validation the seat could not complete | **Done; one new failure (F1) and the known NEG-8 failure.** Table below. |
| 7 | Read-list exception | **Nothing outcome-bearing exposed.** The boundary lines are the heading of decision request 50 ("DRIVER-P9-W1 and the meter liveness read"), its "Read." preamble (three lines naming driver and monitor source files and a deviation row, "Code and text only"), and the RL-81 heading. They concern the v4 driver's meter liveness check. They hold no BYTES, Block 6 or v4 value, count, direction or result. I read the same lines and no more of RL-81. |

Other static checks: `scripts/test_timings.json` differs from the base by one inserted line and no deletions, so it
was not re-serialized. The seat report's own claims are accurate and it does not claim nineteen clean campaigns.

## Test results

All runs: Python 3.13, `-B`, `nice -n 10`, one module at a time, `JW_B5_SYNTHETIC_ONLY=1`, temp root on the
external SSD. Synthetic campaigns only.

| Run | Tree | Result |
| --- | --- | --- |
| `tests.test_bytes_twin` | head | 111 tests, OK, 674 s |
| `tests.test_bytes_stage1` | head | 23 tests, OK, 224 s |
| `tests.test_bytes_agreement` (full, to completion) | head | 51 tests in 12,030 s: 49 OK, **2 failures** |
| — `test_withheld_campaign_missing_files_and_uncollected_pass` | head | **FAIL: 36 above the bar** (F1). New on this branch. |
| — `test_neg8_reference_battery_omission_is_detected` | head | FAIL: `refused: BYTES commitment guard refused:` (returncode 1 from the mutant twin) |
| `…test_neg8_reference_battery_omission_is_detected` alone | base `a0d5b19c4` | FAIL, identical message, 516 s. **Pre-existing**; also recorded in the anchor fix's cold review. Not caused by this change (F3). |
| Head tests on the base twin (check 4) | head + base twin | 1 ERROR, 1 FAIL as expected |

Nineteen campaigns at the head, from the full run:

| Campaign | Compared | Above the bar |
| --- | ---: | ---: |
| bytes | 314,837 | 0 |
| resident | 262,385 | 0 |
| time | 262,385 | 0 |
| defects | 269,281 | 0 |
| minimum | 254,966 | 0 |
| edge_locked | 262,385 | 0 |
| **withheld** | 219,549 | **36** |
| invalid_anchor | 262,033 | 0 |
| marker_incomplete | 20,312 | 0 |
| late_start | 169,903 | 0 |
| polls_only | 20,220 | 0 |
| header_closed | 20,220 | 0 |
| empty_payload_n | 314,837 | 0 |
| replayed_batch | 314,485 | 0 |
| replayed_tail | 314,837 | 0 |
| first_batch_tail_replayed | 314,837 | 0 |
| compressed | 262,385 | 0 |
| anchor_narrow | 269,017 | 0 |
| anchor_wide | 269,017 | 0 |

The `withheld` count comes from the review harness's own build of that campaign (219,549 compared, 36 above);
the suite's run of it failed with the same 36 rows before printing its count line.

## Mutants

Each mutant is a one-site edit of the head twin (sha256 `252a5434…bb17`), run through the real comparer on
freshly built synthetic campaigns at fit and held-out, and through the committed loader unit test. "Killed"
means at least one field above the bar or a unit-test failure. An unmutated control replay gave 0 above the bar
on `anchor_narrow`, `bytes` and `defects`.

| Requested kind | Mutant | Killed by |
| --- | --- | --- |
| Drop session codes | not unioned in the cell | `anchor_narrow` 312, `defects` 324 |
| | loader returns none | unit test; `anchor_narrow` 312 |
| | attached at stage 1 only / stage 2 only | `anchor_narrow` 240 (held-out) / 72 (fit) |
| | flags file only / acceptance only | unit test; `anchor_narrow` 312 each |
| Drop run codes | run codes not unioned | `bytes` 144 |
| | meter codes not unioned | `bytes` 72 |
| Include dropped runs' codes | flags from all rows, kept or not | `defects` 60 |
| Ordering | reversed; sorted by another key | `anchor_narrow` 312 each |
| | session codes prepended | `bytes` 144 |
| | session codes appended after the run codes | `defects` 24 |
| | loader list unsorted | unit test |
| Dedupe | no dedupe in the cell | `anchor_narrow` 312 |
| | no dedupe in the loader | unit test |
| Session/run boundary | every code treated as a session code | unit test; `bytes` 240 |
| | only run-scoped codes treated as session codes | unit test; `anchor_narrow` 312 |

Not every mutant is killed by every campaign. `anchor_narrow`, the campaign the new regression test uses, has no
dropped run with a code of its own and no run code that sorts after a session code, so the dropped-runs and
appended-order mutants pass it. They are killed only by `defects`, in the full agreement module.

Two survivors, both equivalent:

- **Session codes taken from all of a cell's rows instead of its kept rows.** A cell's rows all belong to one
  session, so the set is the same whenever any row is kept.
- **The `stage in ("1", "2")` guard removed.** `main` already loads no archive at the blinded stage, so the
  guard is a second fence and cannot change output. The blinded outputs were unchanged under this mutant.

## Findings

**F1 (blocking). Missing-withheld cells omit the session's codes.**

- Where: `scripts/bytes_twin.py`, `analyse`, the `missing is not None` branch (cell and per-boundary
  `"flags": [WITHHELD_MISSING]`), and `missing_pass_quantities` (the same list on each variant).
- Analysis: `archive_records` puts the session's codes on every planned record of the session, and a missing
  cell prints `sorted` flags over all of them. Result: `['bytes.withheld_missing', 'catalog.digest_mismatch',
  'power.pstar_unsized', 'registration.default_used']`. Twin: `['bytes.withheld_missing']`.
- Extent: 36 rows, held-out stage only: 12 for `qwen3-30b-a3b-4bit` pass 2 and 24 for
  `qwen3.5-122b-a10b-4bit` passes 1 and 2 (3 boundaries × 4 variants each).
- Reading: under RL-82 a cell's flags include "the codes recorded on its session", and a missing cell has a
  session. The analysis does not move. So the twin should print `sorted({bytes.withheld_missing} ∪ session
  codes)` at stage 2 for these cells. RL-82 condition 5 says not to widen the change when a flag row remains
  above the bar, so the research lead should confirm this reading before the seat builds it.
- After the fix: rerun `test_withheld_campaign_missing_files_and_uncollected_pass` and the new regression test,
  and add one assertion that a missing cell carries the session codes on both sides.

**F2 (low). Point-level flag lists are not compared in full between the two programs.** The comparer checks only
whether `bytes.withheld_missing` is present on each point. Session codes on points are therefore outside the
agreement. This predates the branch. It matters after F1 is fixed, because the twin's point flags are the union
of its pass flags and will then gain the session codes of missing passes.

**F3 (low, pre-existing). NEG-8 omission test fails at base and head alike.** The mutant twin it writes into the
campaign directory is refused by the commitment guard before it computes. The anchor fix's cold review suggests
a repair. It is not part of this change and was not touched.

**F4 (low). Fault paths differ between the two readers.** The twin treats an absent `derived/flags.jsonl` as no
codes and reads a compressed sibling; the analysis reads the plain file and raises if it is absent. No campaign
exercises either case, and an analysis failure would stop the run before any comparison.

**F5 (note). The regression test alone does not guard ordering against run codes or dropped runs.** See the
mutant note above. Adding a session code that sorts before `battery.assist` to the fixture would close the
ordering gap in the fast test.

## Blinding and custody

I opened no BYTES export, predictions file, held-out store, key, custody root, Block 6 or v4 outcome. Inputs
were code, the registration-facing rulings RL-80 and RL-82, the boundary lines named in check 7, and synthetic
campaigns generated in temporary directories on the external SSD. No host-changing command was run.
`scripts/test_timings.json` was not written.
