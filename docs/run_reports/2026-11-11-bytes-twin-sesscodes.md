# BYTES twin session codes — RL-82 reading A

2026-11-11. Base: `origin/fix/2026-11-11-bytes-twin-anchor` at
`a0d5b19c4f324f8df2ce743d2ae11599f3964cc7`. Work branch:
`fix/2026-11-11-bytes-twin-sesscodes`.

## Authority and bounded change

Registration §6 defines a flag as “a recorded code on a run or session”; §15
prints each pass cell's “flags”. RL-82 adopts reading A: the codes on the kept
runs and on the session, with a session code defined by the absence of an
attached run in either `derived/flags.jsonl` or acceptance's `emitted_flags`.

| Change | Registered sentence / ruling |
| --- | --- |
| Twin independently reads both archive flag sources, selects records without a run, deduplicates and sorts their codes. | §6's definition; RL-82 scope: the twin reads those two sources itself and imports nothing from `joulewise`. |
| Archive-stage cell flags include those session codes alongside the existing run and meter codes, including secondary and flagged-inclusive cells. | §15's per-cell flags; RL-82 applies at every stage reading the archive (fit, held-out and all). Twin stage `2` serves the held-out/all arithmetic. |
| Synthetic campaign fixture records session codes in both sources, including one shared code and a source-specific code in each. | RL-82 condition 2, failing first; §12 exact agreement for flags. |
| Regression compares both implementations, retains the old run-only rule as a mutation, checks both blinded stages, and uses `anchor_narrow`. | RL-82 conditions 2–3 and the pre-held-out requirement for a nonzero anchor profile plus a session code; §7 operative anchor bound and §11 blinded export-only rule. |
| Focused loader and blinded archive-read tests. | RL-82's no-run definition and unchanged blinded stage. |
| Insert-only local timing note and this report. | Requested verification and handoff; timings are local synthetic observations only. |

The shared synthetic code is `power.pstar_unsized`; `registration.default_used`
appears only in the flags file and `catalog.digest_mismatch` only in acceptance.
They have `DISCLOSE` effects and no run attached. Existing run-scoped fixture
flags remain in place. All nineteen campaigns therefore carry session codes,
including both existing nonzero anchor campaigns.

## Failing-first evidence

Before changing `scripts/bytes_twin.py`, the new fixture was generated with
`anchor_profile="narrow"` and its session codes. The old twin and unchanged
estimator completed fit. The real `compare_cells` comparer inspected 55,033
fields: 54,545 equal, 416 under the bar, **72 above the bar, all `flags`**.
There were no other cell fields above the bar. The flags use an exact bar.
The independently counted diagnostics were 19,320 compared / 70 different;
they are not agreement gates (§12).

The command was the new
`tests.test_bytes_agreement.AgreementTests.test_session_codes_at_archive_stages`.
It was interrupted after the fit evidence had been captured, before its full
multi-stage unittest verdict, to preserve the remaining test budget. Thus the
72-field result is an actual old-program comparison, not a claimed completed
unittest failure. The exact generated input bytes and the old fit outputs were
preserved in temporary directories for the fixed fit comparison. No science
decisions or analysis results substitute for recomputation by the fixed twin.

**Fixed result:** on those same preserved inputs, the fixed twin's fit cells
compare at **55,033 fields: 54,617 equal, 416 under the bar, zero above the
bar**. The same 19,320 diagnostics / 70 different remain. Thus the 72 flag
disagreements disappear without a different numerical comparison result.
The old and fixed twin's blinded JSON outputs on the same synthetic exports
are **byte-identical**. This directly checks that the added session codes do
not enter the blinded output.

The replay command was
`python3.13 -B /private/tmp/bytes-sesscodes-replay.py --fit-only`; its temporary
input snapshot is `/private/tmp/bytes-sesscodes-red-inputs`. It restores the
original generated fixture paths, runs the fixed twin at fit, invokes
`compare_cells` against the estimator's captured fit output, and runs old and
fixed twins at blinded for a byte comparison. It does not rerun or certify
held-out/all, or claim byte identity of real predictions. The committed
regression test supplies the durable reproduction for a complete future run.

## Campaign results and tests

**Validation is incomplete; this is not an admission report.** The ~20-minute
test limit was retained; the optional asynchronous question about extending it
had no answer during the run. Tests were serial. No full suite was run.

Commands use Python 3.13.18, `-B`, `JW_B5_SYNTHETIC_ONLY=1`,
`PYTHONDONTWRITEBYTECODE=1`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, and `GIT_NO_LAZY_FETCH=1`.

| Command / check | Result |
| --- | --- |
| `python3.13 -B -m unittest tests.test_bytes_agreement.AgreementTests.test_neg8_reference_battery_omission_is_detected` at base | Interrupted during synthetic fixture generation/export, before an assertion result. The brief identifies this as the identical base failure; this run does not independently confirm that assertion. Its code is untouched. |
| `python3.13 -B -m unittest tests.test_bytes_agreement.AgreementTests.test_session_codes_at_archive_stages` before the fix | Interrupted after capturing the old fit comparison: 72 exact-bar flag disagreements, no other above-bar cell fields. |
| `python3.13 -B -m unittest -v tests.test_bytes_twin` | Interrupted after 69 tests printed `ok`, with no `FAIL` or `ERROR` markers; no full-module verdict. |
| Fixed twin on the preserved `anchor_narrow` inputs, compared to the unchanged estimator's old fit output using `compare_cells` | 55,033 fields; zero above bar. |
| Old/fixed twin blinded JSON on those same exports | Byte-identical. |
| Full `tests.test_bytes_stage1` and full `tests.test_bytes_agreement` | Not completed within the budget. |

The extra base-failure reproduction consumed about 6.6 minutes without a
verdict. Spending that much of the budget on an optional reproduction was a
verification scheduling error; it reduced time available for required checks.

Local elapsed observations from the logs: extra base reproduction 394 s;
old-fixture regression run before interruption 397 s; interrupted twin module
274 s; fixed fit/blinded replay 41 s. These are local scheduling observations,
not hardware evidence or hosted medians. Two subsequent focused TestCase
instances passed, serially via `unittest.TextTestRunner` without invoking the
expensive module fixtures:

- `tests.test_bytes_twin.SessionFlagTests.test_both_archive_sources_only_contribute_codes_without_a_run`: 1 test, 0.002 s, OK.
- `tests.test_bytes_stage1.WithheldLayoutTests.test_driver_refuses_all_withheld_names_before_any_file_open_or_child`: 1 test, 0.274 s, OK.

These focused results do not stand in for either full module. Total test
process time, including imports and interrupted attempts, was approximately
1,110 s (18.5 minutes) from summed local log timestamps, below about
20 minutes. No additional long test was started when it could not fit the
remaining budget.

**Nineteen-campaign census.** `anchor_narrow` exercised a nonzero anchor profile
and session codes in both sources; its fit results are given above. Its full
fixed campaign is not certified here. The remaining eighteen campaigns were
not completed on the fixed twin: `bytes`, `resident`, `time`, `defects`,
`minimum`, `edge_locked`, `withheld`, `invalid_anchor`, `marker_incomplete`,
`late_start`, `polls_only`, `header_closed`, `empty_payload_n`, `replayed_batch`,
`replayed_tail`, `first_batch_tail_replayed`, `compressed`, and `anchor_wide`.
There is **no claim of nineteen campaigns with zero fields above the bar**.

Next exact verification step, with adequate test time authorized: run
`python3.13 -B -m unittest tests.test_bytes_twin`, then
`python3.13 -B -m unittest tests.test_bytes_stage1`, then
`python3.13 -B -m unittest tests.test_bytes_agreement`, one module at a time
with the environment above. The last module runs all nineteen campaigns and
the new regression. Record the brief's known NEG-8 failure separately without
fixing it here. Any remaining flag disagreement returns to RL-80/RL-82; do not
widen this repair. No MLX code or MLX native check is involved.

## Preservation and limits

The estimator `joulewise/bytes_analysis.py` is untouched and retains SHA-256
`18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`.
The export implementation and format are untouched. The blinded stage is
untouched on both sides: it reads export run codes only, including the
post-commit blinded campaign path. All study data are untouched. Only freshly
generated synthetic campaigns in temporary directories are exercised.

No real export, predictions file, held-out store or key, probe output, custody,
night/archive data path, coordination state, or sealed outcome is opened. No
network, hardware measurement, model download, full suite, or external job
control is used. `RUN_STATE.md`, `TASK_QUEUE.md`, the state kernel and its test
are neither opened nor compared nor edited. The supplied read whitelist takes
precedence over the general repository intake and coordination checklist.

Read-list exception: the first section-extraction command also displayed the
next decision request's heading and code-read preamble and the RL-81 heading
as range boundaries. No RL-81 ruling body was read. The subsequent RL-82
extraction stopped at its section separator. This did not expose study values;
the seat is not described as strictly within the supplied read list.

This seat cannot establish real fit-set agreement, byte identity of real
predictions, or the RL-44 census. Those and the independent cold review remain
lead gates under RL-82. This change does not enter the deviation row, release
data, or make the stage-1 commitment.

Changed files: `scripts/bytes_twin.py`, `tests/fixtures/bytes/campaign.py`,
`tests/test_bytes_twin.py`, `tests/test_bytes_agreement.py`,
`scripts/test_timings.json` (one inserted line only), and this report.

Final static verification: changed Python sources parse; timing JSON parses
and removal of its one inserted line recovers its exact base bytes;
`git diff --check` passes. The estimator and exporter match their base bytes.
All 7,082 preserved synthetic input files match the replay inputs byte for byte.
The change is committed locally on the requested branch; no push is made.

Commit housekeeping: `git add` first found this clone's empty `index.lock`,
dated 13:10:21 PST during the interrupted local tests. At 13:16 it had no open
owner (`lsof`), was unchanged and more than five minutes old. It was preserved
by renaming it within this clone's `.git` to
`index.lock.sesscodes-orphan-20261111T131021` before retrying the commit.
Subsequent Git commands disable optional locks. No external job was signalled
or modified.
