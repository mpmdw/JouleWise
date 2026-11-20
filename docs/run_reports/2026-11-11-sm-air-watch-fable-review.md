# Fable cold review: `sm-air-watch` (audit Q1, Q9; section 8.2 item 2 "a voice")

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 04:50 PST. Reviewed head `1eabf0028`
(`feat/2026-11-11-sm-air-watch`, base `feat/2026-11-11-sm-window-state`). Builder: Sol xhigh.

**Verdict: ADMIT-WITH-FIXES.** AW-1 blocks: on a real results branch the watcher finds no record and reports
every result, good or bad, as not measured. AW-2 blocks for blinding hygiene.

## What I did

- Read all of `scripts/air/night_results_watch.py` (584 lines) and the README.
- Ran `python3.13 -B -m unittest tests.test_night_results_watch`: 37 tests, OK.
- Compared the watcher's idea of where records sit on a results branch with the code that writes the branch.
- Ran one real `--once` poll on the Air with a scratch state file and `--since-epoch` set one day back. See
  "Disclosure" below: that poll did more than I intended, and it is how AW-1 and AW-2 were found.

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| AW-1 | **Blocking** | The driver publishes a window's records on its results branch under `docs/process_traces/night-results/<plan_id>/` (`scripts/run_night.py:1576` on `main`; `:1668` on the W1 line). `layout()` looks only under `<plan_id>/`, `night/` and the root, so on a real branch it finds nothing: `outcome=UNKNOWN verdict=UNKNOWN` and a `RESULT_NOT_MEASURED` alarm for every result. The synthetic tests build branches in the layouts the watcher expects, so they pass. | Take the layout from the writer: the published prefix first, the three others kept as fallbacks. One test builds its branch tree with the writer's own destination expression (import or AST-read the constant from `scripts/run_night.py`, do not retype it) and must fail if the two drift apart. The same for `night_plan.json`, if the writer publishes it at all; if it does not, say so and take timing only from `CURRENT.json` and the command line. |
| AW-2 | **Blocking** | On a first run, `--since-epoch` makes every existing ref eligible, because the commit time is not known until the branch has been fetched and read. With 99 results branches on origin, that fetches and reads the structural records of every past window of every block, and alarms on each. A watcher must not read branches nobody asked about. | Remove `--since-epoch`. First run: every existing ref is baseline, unread. To include existing branches, the caller names them: `--include-plan <plan_id>` (repeatable). The armed plan from `CURRENT.json` or `--plan-id` is always included. Test: on a first run only the named or armed refs are fetched; assert the fake Git saw no fetch for any other ref. |
| AW-3 | Medium | Git is restricted to `https` and `file` remotes. The Air's origin is HTTPS today. With an SSH origin every poll fails as `GIT_FAILED` and ends in `SILENCE`, which does not say why. | Before the first poll, read the origin URL; if its scheme is not allowed, exit 2 with `ORIGIN_PROTOCOL_NOT_ALLOWED`. README: one line. |
| AW-4 | Low | An alarm is raised once and remembered in `raised` for ever. A `DEADLINE_PASSED` for a plan stays silenced after the pointer moves to a new deadline only because the identity includes the deadline; `SILENCE` uses the last-success time, good. `REF_READ_FAILED` for the same sha is never repeated although the read is retried each poll. | After N consecutive failures for the same ref and sha (use `failure_limit`), raise `REF_READ_FAILING` once more with the count. |
| AW-5 | Low | The held-release visibility added by the offload fix (`held_reason`) is not watched. | Out of scope here; listed for a later seat. |

## What is sound

- Only projected structural fields reach the temporary directory: verdict words, exit codes, booleans, counts.
  Identifiers and digests are replaced by fixed placeholders, existence markers are empty files, and anything
  not on the allowlist is never written or printed.
- The watcher never checks out a branch, never writes `FETCH_HEAD`, and disables SSH outright, so it cannot
  reach the measurement Mac.
- State is saved only after the lines are delivered, so a crash repeats an alarm and cannot swallow one.
- The exit-contract adapter passes plan words, which closes note N-1 of the exit-contract review.

## Disclosure

To see the tool work once outside the test suite I ran, on the Air, one `--once` poll against origin with a
scratch state file and `--since-epoch` one day back. Because of AW-2 it fetched all 99 `night-results/*`
branches and projected the structural fields of their night records, not only recent ones. Because of AW-1 it
found no record on any of them: every line it printed was `outcome=UNKNOWN state=UNKNOWN verdict=UNKNOWN
chain_exit_code=None fault=None fault_reason_count=0`. No verdict, value or record text was displayed or kept.
The fetched objects sit unreferenced in the local object store until git prunes them. I did not repeat the
poll, and a follow-up attempt to look at one branch directly was refused by the session's permission layer; I
did not work around it. The orchestrator has been told.

## Native check owed (on the Air, by the lead or orchestrator)

After round 2: one `--once` poll with `--include-plan` naming one finished rehearsal whose structural outcome is
already known to the lead, and a comparison of the printed line with it.

## Round 2 delta review (2026-11-11 05:02 PST)

Reviewed `3fcfda031` (Sol's round 2 on the same branch), plus one test of my own.

**Verdict: ADMIT**, with one native check owed before anyone relies on it (below).

| Finding | Disposition |
|---|---|
| AW-1 | Fixed. The published prefix `docs/process_traces/night-results/<plan_id>/` is tried first, with its own allowlist of the files the two writer generations publish (neither publishes `night_plan.json` or the R1 payload and slots files). A drift test reads the destination expression from `scripts/run_night.py` at `HEAD` by AST and fails if the prefix moves. |
| AW-2 | Fixed. `--since-epoch` is gone. On a first run every existing ref is an unread baseline; only refs named with `--include-plan`, the armed plan, and refs that appear or move later are read. The first-run test asserts the exact set of refs the fake Git was asked for. |
| AW-3 | Fixed. The origin URL is checked before the first poll; a scheme that is not allowed exits 2 with `ORIGIN_PROTOCOL_NOT_ALLOWED`. |
| AW-4 | Fixed. `REF_READ_FAILING` is raised with a count once a ref has failed `failure_limit` polls in a row at the same sha. |
| AW-5 | Not in this PR, as planned. |

Checks on the Air: `tests.test_night_results_watch`, 52 tests, OK (50 from Sol, 2 from me). Seven mutants: six
killed (the published prefix changed; first-run baseline ignored; the not-measured alarm removed; the early
result alarm removed; the armed-without-result alarm removed; the silence alarm removed). One survived: the
invariant events demoted from ALARM to INFO. I added `InvariantAlarmLevelTests` (a measured result with a
violated invariant is an alarm and exits 20; without one it is quiet), which kills it.

**Native check owed, by the orchestrator:** one `--once --include-plan <finished rehearsal>` poll on the Air
with a scratch state file, compared with that rehearsal's known structural outcome. Until it passes, the
scratch watcher stays the watcher of record.

## Native check (2026-11-11, by the orchestrator) and one change from it

The orchestrator ran `--once --include-plan align-r1-20261111T0453Z` at `88d23bb45` with a fresh state file. The
line matched the rehearsal's known structure: `outcome=MEASURED_OK state=Delivered verdict=GO chain_exit_code=0`,
with the invariant alarm `COURIER_SENT_WITHOUT_DELIVERY`, which is correct for a file-only courier (audit Q11).

It printed `fault=None`. That rehearsal ran on a record generation whose `result.json` has no `fault` field.
The line now prints `fault=absent` for a missing field and `fault=false` or `fault=true` for a recorded one, and
`chain_exit_code=absent` likewise (my change, with a test).
