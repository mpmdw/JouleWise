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

---

# Delta review (c95242509)

2026-11-11, 22:10 PST. Reviewer: Claude Fable 5.2, the same cold seat, independent of the build seat (Sonnet).
Target: `de07c51dd..c95242509` on `fix/2026-11-11-bytes-twin-sesscodes`: `scripts/bytes_twin.py` (15 lines, the
`missing is not None` branch of `analyse` and `missing_pass_quantities`) and `tests/test_bytes_twin.py` (49 lines).

## Verdict: ADMIT-WITH-FIXES at `c95242509`

**F1 is fixed as written.** In a missing-withheld cell the twin now prints `sorted({bytes.withheld_missing} ∪
session codes)`, and the `withheld` campaign has zero fields above the bar. Nothing else in the twin moved. RL-82
condition 3 is no longer blocked by F1, and nothing here stands in the way of the fit-set rerun (condition 4):
a missing-withheld cell exists only at the held-out stage.

**One fix is needed before the held-out agreement (stage 2), not before the commitment: N1.** The analysis
builds a missing cell's list from every planned run of the cell, so it also lists codes recorded on those runs
in the archive. The twin lists the session's codes only. I planted one run code on one missing run of the
`withheld` campaign: 12 `flags` fields went above the bar. No committed campaign carries that feature, which is
the same reason the nineteen campaigns missed the two earlier differences.

**No new ruling is needed for F1.** I agree with the lead's reading. RL-82 reading A defines a cell's flags
without regard to the cell's status, its scope covers "every stage that reads the session's archive", and its
second ground makes the bound program the registration where the prose is silent. A missing cell has a session
and the analysis lists that session's codes. Condition 5 ("stop, do not widen, attribute as RL-80 says") was
met in substance by F1 itself: names, counts, sides and the governing sentence, from synthetic data, with no
value compared. The lead should record that F1 served as that attribution. N1 falls under the same second
ground; whether it needs a line in the ruling is the research lead's call, and I flag it for that reason only.

## Check by check

| # | Check | Result |
| --- | --- | --- |
| 1 | The new list matches the analysis exactly | **Matches for session codes; one term missing (N1).** Analysis: `reduce_models` prints `sorted({f for r in module for f in r["flags"]})` over all planned records of the cell; `archive_records` gives each record `run codes ∪ session codes ∪ member exclusion codes`, plus `bytes.withheld_missing` when the run is absent from the export. Twin: `sorted({bytes.withheld_missing} ∪ session codes)`. Set of session codes, sort, dedupe and the withheld code: identical. Run codes and member exclusion codes of the missing runs: absent in the twin. Stage: both sides give the bare `["bytes.withheld_missing"]` at the post-commit blinded stage (no archive) and have no missing cell at fit. Levels: every boundary and every variant of the cell carries the same list on both sides. |
| 2 | Nothing else moved; the default `flags=` path | **Pass.** `missing_pass_quantities` has one caller in the repository, the changed one, so the default is unused; it yields `["bytes.withheld_missing"]` as before. The new list object is shared by the cell and its three boundaries; nothing in the twin mutates a cell's flag list in place. Twin outputs at blinded and fit are byte-identical to the campaign's own under replay. `joulewise/` and `scripts/test_timings.json` are untouched by the range. |
| 3 | Fail-first | **Pass.** With the twin of `de07c51dd` (sha256 `252a5434…`, the same file as at `23b82a4b7`) under the head's tests: `MissingWithheldFlagTests.test_session_codes_before_and_after_with_duplicate` FAILS; the `withheld` campaign has 36 above the bar. At `c95242509` the test passes and the campaign has 0. The other two new tests pass at both commits, as they should: one asserts the unchanged no-code case, the other is a loader test. |
| 4 | Mutants | **Every requested kind is killed.** Two survivors are equivalent through the command line. Table below. |
| 5 | Tests | **All pass.** Table below. |
| 6 | Import fence; estimator digest | **Pass.** `FenceTests` (3) pass. `joulewise/bytes_analysis.py` sha256 is `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`. |
| 7 | Point-level flags on missing passes | **It is what the analysis does, and it removes a divergence.** See "Point level" below. |

## Tests

Python 3.13, `-B`, `nice -n 10`, one module at a time, `JW_B5_SYNTHETIC_ONLY=1`, temp root on the external SSD,
29 GB free on `/` before each. Synthetic campaigns only. The full agreement suite was not run: no targeted
result pointed to a wider problem.

| Run at `c95242509` | Result |
| --- | --- |
| `tests.test_bytes_twin` | 114 tests, OK, 467 s |
| `AgreementTests.test_withheld_campaign_missing_files_and_uncollected_pass` | OK, 184 s. `withheld`: 219,549 compared, **0 above the bar** |
| `AgreementTests.test_session_codes_at_archive_stages` (`anchor_narrow`) | OK, 0 above the bar; the run-only twin still fails with 72 |
| `AgreementTests.test_defects_campaign` | OK. `defects`: 269,281 compared, 0 above the bar |
| `FenceTests` | 3 tests, OK |

`test_bytes_stage1` was not rerun; the range does not touch what it covers and the author reports 23 OK.

## Mutants

One-site edits of the head twin (sha256 `6c65efd6…5453`). "Unit" is the committed `MissingWithheldFlagTests`
bound to the mutant. "Campaign" is the mutant's held-out output through the real comparer on a freshly built
`withheld` campaign. The unmutated control gave 0 above the bar.

| Requested kind | Mutant | Unit | Campaign (above the bar) |
| --- | --- | --- | --- |
| Drop the session codes | hard-coded list again | killed | killed, 36 |
| | the twin of `de07c51dd` | killed | killed, 36 |
| Drop `bytes.withheld_missing` | session codes only | killed | killed, 105 |
| Unsorted | reverse order | killed | killed, 36 |
| | session codes, then the withheld code last | killed | killed, 36 |
| | withheld code first, then session codes | killed | survives |
| | input order, not sorted | killed | survives |
| | no dedupe | killed | survives |
| Stage | fit only | killed | killed, 36 |
| | blinded and fit only | killed | killed, 36 |
| | stage guard removed (applies at blinded too) | survives | survives, **equivalent** |
| | held-out only | survives | survives, **equivalent** |
| Present-withheld cells only | codes attached only when the store was read | killed | killed, 36 |
| Level | cell level keeps the old list | killed | survives |
| | boundary level keeps the old list | killed | killed, 36 |
| | variant level keeps the old list | killed | survives |

- **The two equivalent survivors.** `main` loads no archive at the blinded stage and reads no withheld store
  at fit, so neither edit can change what the program writes. All four stage outputs of both mutants equal the
  control's in every computed field.
- **Campaign-only survivors are killed by the unit test alone.** The campaign's three session codes all sort
  after `bytes.withheld_missing` and hold no duplicate, and the comparer reads the boundary-level list only.
  The new unit test is therefore the sole guard of sort order around the withheld code, of dedupe, and of the
  cell-level and variant-level lists.

## Point level (check 7)

The author's note is right, and the new behaviour is the analysis's. `scripts/bytes_analyze.py`
(`_missing_labels`) gives a point with a missing pass the sorted union of all its passes' flags, session codes
included. The twin's `mean_of_passes` takes the same union from the per-variant lists that
`missing_pass_quantities` now fills. I compared the full lists on the `withheld` campaign, outside the suite:

| Held-out rows carrying the withheld flag | Twin of `de07c51dd` | Twin of `c95242509` |
| --- | --- | --- |
| Points (24) | 0 equal, 24 different | **24 equal** |
| H1 rows (9) | 0 equal, 9 different | **9 equal** |
| Active-or-resident rows (3) | 3 different | 3 different (N2) |

So it is not a new divergence. It closes one that F2 said the comparer could not see. F2 itself stands: the
comparer still checks membership of the withheld code only at these levels.

## Findings

**N1 (fix before the held-out agreement; does not block the commitment). A missing cell omits the codes
recorded on its own runs.**

- Where: `scripts/bytes_twin.py`, `analyse`, the same branch. `missing_flags` is `{bytes.withheld_missing}` and
  the session codes.
- Analysis: each planned record carries `flags.get(run_id) ∪ window_flags ∪ exclusion codes`
  (`_record_base`), and the missing cell prints the union over all of them. A run code in
  `derived/flags.jsonl` or in the acceptance record's `emitted_flags`, or a member exclusion code, on a run
  whose rows sit in the missing store, is therefore listed.
- Evidence: one line `{"code": "audit.runprobe", "scope": {"run_id": <a 30B-A3B run of bytes-s2-p2>}}` added
  to that archive's flags file, analysis and twin rerun at held-out: both exit 0, **12 `flags` fields above the
  bar** (3 boundaries × 4 variants), analysis with the code, twin without. The file was restored.
- Reach: only when a withheld store is missing and one of its runs has a code. The failure is loud, not
  silent: the stage-2 agreement would stop. No number or word depends on it.
- Repair: in a missing cell, add the run-scoped codes and member exclusion codes of the model's planned runs,
  read from the archive (the roster maps runs to cells; the twin already reads the other two files itself).
  This matches what the twin already does in refused cells, where it lists the codes of all rows. Add a run
  code on a missing run to the `withheld` fixture or to `MissingWithheldFlagTests`, failing first.

**N2 (low, pre-existing, inside F2). The active-or-resident row's flags are still hard-coded.** The twin
prints `["bytes.withheld_missing"]` (`h1_words`, `"flags": [WITHHELD_MISSING] if moe_missing else []`); the
analysis prints the sorted union of the missing points' pass flags, session codes included. Three rows differ
in the `withheld` campaign. The comparer checks membership only, so nothing is above the bar. It is the same
kind of site as F1 and the cheapest time to fix it is with N1.

**N3 (low). The F5 fixture does not close F5.** `test_session_code_fixture_sorts_around_run_and_withheld_codes`
exercises `load_archive` only. Four cell-level mutants pass it: reversed order, session codes appended,
session codes prepended, and dropped runs' codes included. Ordering of session codes against run codes in a
computed cell is still guarded only by the `bytes` and `defects` campaigns. The missing-cell ordering is
guarded by the new unit test.

**N4 (note). No test calls the missing branch at the blinded stage with an archive present.** That is why the
stage-guard mutant survives the unit test. One assertion with `stage="blinded"` would pin the guard without
relying on `main`.

F2, F3 and F4 of the first review are unchanged by this range.

## Blinding and custody

I opened no BYTES export, predictions file, held-out store, key, custody root, Block 6 or v4 outcome. Inputs
were code, RL-80 and RL-82 with the two decision-request headings that bound them, and synthetic campaigns
built in temporary directories on the external SSD. No host-changing command was run.
`scripts/test_timings.json` was not written. I changed no code; mutants were temporary files in a throwaway
worktree, removed after each run.

---

# Second delta review (1e288b355)

2026-11-12, 00:16 PST. Reviewer: Claude Fable 5.2, the same cold seat, independent of the build seat (Sonnet).
Target: `76a490b8a..1e288b355` on `fix/2026-11-11-bytes-twin-sesscodes`, two commits (`feb901c65`,
`1e288b355`): `scripts/bytes_twin.py` (48 lines: `read_manifest`, `load_archive`, `h1_words`, the missing
branch and the H1 loop of `analyse`, the output manifest) and `tests/test_bytes_twin.py` (137 lines).

## Verdict: ADMIT-WITH-FIXES at `1e288b355`

**N1 is fixed, exactly.** A missing-withheld cell now lists `sorted({bytes.withheld_missing} ∪ session codes ∪
run codes ∪ member exclusion codes)` over every planned run of the cell. With one run code planted on one
missing run of the `withheld` campaign, the comparer shows **0 above the bar** (12 with the twin of
`76a490b8a`). With seven kinds of code planted, the twin's list equals the analysis's at every level.

**N3 and N4 are closed.** **N2 is fixed for withheld-missing points and is not exact for refused points
(M1 below).** That is also the answer to the author's open question: the premise is wrong on the analysis
side. In the analysis every non-computed pass row carries the codes of all its planned runs and of its
session, whether it is `missing` or `unavailable`. In the twin a refused pass carries none where the row
reads them.

**Readiness.**

- **(a) The fit-set rerun: ready.** The twin's blinded and fit outputs are byte-identical to those of
  `76a490b8a` under replay. Nothing in this range can act at the fit stage.
- **(b) The held-out agreement: this range no longer stands in its way.** N1 was the stated blocker and it
  is closed. M1 cannot stop the agreement, because the comparer does not read the full list at that row.
  One thing outside this range can stop it, loudly, and is the lead's to decide before stage 2: **P1**
  below. A held-out model with no computed pass and at least one refused pass is above the bar today, in
  the twin of `76a490b8a` and in this one alike.

## Check by check

| # | Check | Result |
| --- | --- | --- |
| 1 | N1 matches the analysis exactly | **Pass.** Runs: the analysis builds one record per roster member with a unit in the model's cells (`archive_records`) and the missing row prints the union over all of them (`reduce_models`); the twin unions `cell_run_codes` over the manifest's `cell_ids` of the model, built from every roster member of that session's archive. Sources: run-scoped rows of `derived/flags.jsonl` and of the acceptance record's `emitted_flags`, and `excluding` entries with `scope == "member"`, on both sides. Set, dedupe and sort: the same. Stage: stages 1 and 2 only; the bare `["bytes.withheld_missing"]` at the blinded stage and without an archive. Levels: the cell, its three boundaries and every variant carry one list. Other models' codes: excluded. Evidence below. |
| 2 | N2 matches `evaluate` exactly | **Partly.** The `[]` case matches: the analysis writes a `flags` field only when fewer than three MoE points computed, and the twin prints `[]` exactly when three did. The union is taken over all non-computed points, as in `evaluate`. But the twin's refused pass has no flags to contribute, and the analysis's has. See M1. |
| 3 | Nothing else moved | **Pass.** Replay on a freshly built `withheld` campaign, twin of `76a490b8a` against the head twin: blinded and fit outputs **byte-identical** (sha256 `4777aecf…`, `8e2f6800…`). Post-commit blinded: equal but for the three verification stamps (time and journal). Held-out: the only other differences are the nine `active_or_resident/flags` fields (three boundaries, three pass keys). The output `manifest` is unchanged. `joulewise/` and `scripts/test_timings.json` are untouched by the range. Estimator sha256 `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`. `FenceTests` (3) pass. |
| 4 | Fail-first | **Pass.** Head tests on the twin of `76a490b8a`: 5 of the new tests fail or error. Head tests on the twin of `feb901c65`: the three tests that `1e288b355` adds or widens fail (`test_active_or_resident_row_carries_the_missing_points_flags`, `test_refused_point_without_withheld_flag_contributes`, `test_output_manifest_keeps_no_cell_ids`). `test_blinded_stage_missing_branch_ignores_archive` passes at every commit, as it should: it pins a guard that already existed. |
| 5 | Mutants | **All seven requested kinds are killed.** Two of my own survive. Table below. |
| 6 | Planted run code | **0 above the bar** at head; 12 with the twin of `76a490b8a`, as before. The archive files were restored byte for byte after each run. |
| 7 | Tests | **All pass.** Table below. |

**Evidence for check 1.** On the `withheld` campaign I added to the archive of `bytes-s2-p2` (30B-A3B's store
missing; 8B is the session's other model): a run code on two missing runs and another on a third in the
flags file; a run code in `emitted_flags`; a member exclusion; an exclusion with `scope: "session"`; and a
file code, an emitted code and a member exclusion on 8B runs. Analysis and twin rerun at held-out, both exit
0. The analysis printed one list for the cell, the twin one list at all levels, and they are equal: the
four codes of the missing runs listed once each and sorted among the withheld code and the three session
codes; none of the 8B codes; not the session-scope exclusion.

## Tests

Python 3.13, `-B`, `nice -n 10`, one module at a time, `JW_B5_SYNTHETIC_ONLY=1`, temp root on the external
SSD, 29 to 32 GB free on `/` before each. Synthetic campaigns only. The full agreement suite was not run:
no targeted result pointed to a wider problem in this range.

| Run at `1e288b355` | Result |
| --- | --- |
| `tests.test_bytes_twin` | 121 tests, OK, 434 s |
| `tests.test_bytes_stage1` | 23 tests, OK, 125 s |
| `AgreementTests.test_withheld_campaign_missing_files_and_uncollected_pass` | OK. `withheld`: 219,549 compared, **0 above the bar** |
| `AgreementTests.test_session_codes_at_archive_stages` (`anchor_narrow`) | OK, 0 above the bar; the run-only twin still fails with 72 |
| `AgreementTests.test_defects_campaign` | OK. `defects`: 269,281 compared, 0 above the bar |
| `FenceTests` | 3 tests, OK |

The three agreement tests took 550 s together.

## Mutants

One-site edits of the head twin (sha256 `4820dc2e…03de`). "Unit" is four classes of the committed
`tests.test_bytes_twin` bound to the mutant (`MissingWithheldFlagTests`, `SessionFlagTests`, `H1Tests`,
`ActiveOrResidentFlagsEndToEndTests`). "Campaign" is the mutant's held-out output against the analysis's on
the `withheld` campaign with the seven planted codes of check 1; the unmutated control was equal.

| Kind | Mutant | Unit | Campaign |
| --- | --- | --- | --- |
| **Drop run codes** (requested) | no run-scoped flags read | killed | killed |
| | flags file only | killed | not run |
| | `emitted_flags` only | killed | not run |
| | no cell run codes in the missing branch | killed | not run |
| **Drop exclusion codes** (requested) | no `excluding` read | killed | killed |
| **Other models' runs** (requested) | union over every cell of the archive | killed | killed |
| **Drop the member filter** (requested) | any `excluding` entry with a run | killed | killed |
| **N2, withheld-missing points only** (requested) | `status == "missing"` | killed | not visible |
| **N2 non-empty with three MoE points** (requested) | the union always | killed | not visible |
| **`cell_ids` in the output** (requested) | manifest printed whole | killed | not run |
| Stage | run codes also at the blinded stage | killed | not run |
| N2 order | reverse sorted | killed | not run |
| N2 scope | MoE points only | killed | not run |
| | no row flags unless an MoE model is withheld-missing | killed | not run |
| | every boundary reads the rails point | **survives** | not visible |
| Roster | a member's first unit only | **survives** | survives |

- **"Not visible"**: no committed campaign, and neither of mine, has a row where these N2 mutants change the
  output. The unit tests are their only guard.
- **Rails-point survivor.** Not equivalent: a point whose only computed pass has no DC join is a point on
  rails and none on DC input. No test has such a point beside a withheld-missing pass. Low.
- **First-unit survivor.** Equivalent on any roster the analysis accepts for one cell per run; it differs
  only if a run has units in two cells. Low.

## The author's open question, and what it turned up

**Question.** Does every twin refusal correspond to an analysis `unavailable` row, as far as flags go?

**Answer: the statuses correspond, the flags do not.**

- Analysis. `reduce_models` has three exits without a number: `missing`, `unavailable` because `_kept`
  refused, and `unavailable` because the NEG-8 references are absent. All three print
  `sorted({f for r in module for f in r["flags"]})`: session codes, run codes, exclusion codes and meter
  flags of every planned run. There is no refused row without them. `evaluate` then unions those lists over
  every non-computed point into the active-or-resident row and into each `missing` H1 row.
- Twin. A refused estimate does collect the same list (`compute_cell`, `est["flags"]` over all rows), and it
  equals the analysis's at the cell. But `quantities` copies only `status` and `reason` for a refused
  variant, so the pass, the point and now the row see no flags from it.

**Probe.** A synthetic campaign of my own: `withheld` plus six pass-1 repeats excluded in 32B (its only
collected pass, so a purely refused point) and in 30B-A3B (pass 1 refused, pass 2 withheld-missing, so a
mixed point). Both programs exit 0 at every stage.

| Held-out, gross primary | Analysis | Twin (head) |
| --- | --- | --- |
| Refused cells' flags (32B pass 1, 30B-A3B pass 1) | session codes + `member.strict_validation_failed` | the same list |
| Active-or-resident row flags (3 rows) | withheld code + session codes + `member.strict_validation_failed` | withheld code + session codes |
| 30B-A3B point | `missing` | `refused_no_pass_computed` |
| 30B-A3B H1 row | `missing`, flags listed | `refused`, no status, no flags |
| 32B H1 row | `missing` ("all passes refused"), flags listed | `refused`, no status, no flags |
| Active-or-resident `missing_models` | 30B-A3B and 122B | 122B |

The comparer reports **32 fields above the bar** on this campaign (24 `status`, 4 `missing_models`, 4
withheld-flag membership). The twin of `76a490b8a` gives the same 32: the range did not cause them and did
not cure them.

## Findings

**M1 (low; fix or restate before N2 is called closed). The active-or-resident row omits a refused pass's
codes.**

- Where: `scripts/bytes_twin.py`, `analyse`, the `missing_flags` union, which reads `q.get("flags")` from pass
  quantities; `quantities` gives a refused variant none.
- Effect: when fewer than three MoE points computed and some point has a refused pass and no computed one,
  the analysis's row lists that pass's session, run, exclusion and meter codes and the twin's does not. On
  real sessions, which carry session codes, the lists would differ whenever that happens.
- Reach: the comparer checks only membership of the withheld code at this row (F2), so nothing is above the
  bar. No number or word depends on it.
- The comment ("refused as well as withheld-missing") and the commit message claim more than the code does.
  `test_refused_point_without_withheld_flag_contributes` plants `audit.refusal` on the refused cell and
  asserts a row without it. That pins the twin's behaviour, not the analysis's.
- Repair: either let a refused pass quantity carry its cell's list, which changes point-level lists too and
  should be worked through with P1; or keep the code and say in the comment and the test that refused passes
  contribute nothing, as a known difference inside F2.

**P1 (pre-existing, outside this range; for the lead and the research lead before stage 2). A held-out point
with no computed pass and a refused pass is above the bar.**

- Purely refused held-out point: the analysis's H1 row says `missing`; the twin prints `refused` and no
  status. 4 fields on the probe.
- Mixed point (one pass withheld-missing, the other refused): the analysis relabels the point `missing`
  (`scripts/bytes_analyze.py`, `_missing_labels`); the twin says `refused_no_pass_computed`
  (`mean_of_passes`: `missing` only when every pass is). 28 fields on the probe.
- By reading only, not run: a refused MoE point with no withheld-missing MoE model would give the answer
  `missing` in the analysis and `mixed` in the twin.
- No committed campaign has such a point: `minimum` refuses one pass of two, `withheld` refuses none.
- It is loud, not silent: stage 2 would stop. Which side follows the registration is a question of text
  (the B6 Q1 ruling and Addendum 7 D9, which were not on my read list), so I do not say. It is cheaper to
  rule it now, blind, than after held-out keys are out. The new end-to-end test's comment ("refused, not
  missing") takes the twin's side of that question without a ruling.

**N1, N3, N4: closed.** N3's ordering assertion now runs through `analyse`. N4's blinded-stage assertion kills
the stage-guard mutant.

F2, F3 and F4 of the first review are unchanged by this range.

## Blinding and custody

I opened no BYTES export, predictions file, held-out store, key, custody root, Block 6 or v4 outcome. Inputs
were code, RL-80 and RL-82, and synthetic campaigns built in temporary directories on the external SSD. No
host-changing command was run. `scripts/test_timings.json` was not written. I changed no code; mutants and
planted codes were temporary files in throwaway worktrees and scratch campaigns, restored or removed after
each run.
