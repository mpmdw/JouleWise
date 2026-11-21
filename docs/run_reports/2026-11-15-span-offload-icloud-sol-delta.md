# PR #804 cold executing delta review

Candidate: `27e4070c49c1b27223afbc6cc18635efc763b5b4`, matching fetched
`origin/ops/2026-11-15-air-independence`. Reviewed the complete delta from
`da02b7fdeca60bbbd933e7f3b5d679a6418464b6` in the second detached checkout
`/Volumes/JW-EXT/scratch/sol-offload-icloud/review/retry-tree`.

The original `REPORT.md` remains byte-for-byte unchanged at sha256
`36fd5482d8c6dd03de4759d2898b94a829304c5f0efd123c9cdd28aaf4e94b30`.
Its archived repository copy and the archived brief match their original scratch
files byte-for-byte (`cmp`, exit 0). This is the same independent seat's bounded
fix round; no other agent was consulted or launched.

The original safety limits remain in force: no candidate-file edits, commit, push,
merge, MBP contact, SSH, real brctl/iCloud operation, custody or energy file access,
journal parsing or CloudDocs database access. No sandbox was weakened or bypassed.
All authored artifacts and temporary synthetic fixtures remain in the authorized
review directory, with temporary files under `review/tmp/`.

## Delta and original-finding dispositions

1. **Original SHOULD-FIX 1 — RESOLVED.** An unconfirmed iCloud marker collision now
   validates the existing record with `open_regular(..., single_link=True)`, preserves
   it, and reports `ICLOUD_UNCONFIRMED`, exit 8. The confirmed marker path and local
   backend retain their prior behavior. The new CLI regression checks the repeated
   iCloud result and record preservation. Independently reproduced exit 8 twice,
   with the original `.ok.unconfirmed` bytes unchanged and no `.ok`. A subsequent
   fully confirmed retry returns 0 and creates `.ok`, retaining the historical
   unconfirmed record. Independently planted symlink, hardlink, FIFO and directory
   records are refused with exit 4 without following, replacing or blocking on them;
   their target bytes remain unchanged and no temporary marker remains.
   The runbook now explicitly requires `<marker_dir>/<plan>.ok` before exit 3 may
   count as an already satisfied gate. No standing issue remains from this finding.

2. **Original NOTE 2 — RETAINED AND RECHECKED.** The repair does not change upload,
   status recognition, deadlines, eviction/download observations, hash/size comparison,
   stage reuse, plan locking, encryption or original retention. The independent
   confirmation and failure probes remain green. All dataless observations are
   explicit fakes; this is software evidence under the original trusted-control-root
   model, with no claim of live provider or hostile-race qualification.

3. **Original NOTE 3 — BOOKKEEPING UPDATED; EXTERNAL LIMITS RETAINED.** Reviewed every
   changed file, including the archived brief/report, five invocation-manifest rows,
   run report, kernel latest_report, generated RUN_STATE/TASK_QUEUE views and runbook.
   Records accurately identify the original admitted head, the repaired finding and
   this pending final-head delta review. `gen_state.py --check` passes. The kernel
   still has no active stop card; the measurement pointer and task selections are
   unchanged. Manifest report hashes match the preserved report. The run report
   distinguishes the failed shell launch from the one executing cold seat, records
   the OS-blinded broad-test limitations, and leaves final GitHub CI to its owning
   gate ledger. PROVISIONAL macOS 26 qualification and the separate research-lead
   A.3 permanence question remain explicit.

No new BLOCKING, SHOULD-FIX or unresolved software findings were found.

## Commands and results

Environment remains Python 3.13.18 at `/opt/homebrew/bin/python3.13`, macOS 15.8.3,
real LibreSSL 3.3.6. Execution used `-B`, `PYTHONDONTWRITEBYTECODE=1` and
`TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp`.

Setup:

```sh
git -C /Volumes/JW-EXT/jw-wt/mythos-repo fetch origin
git -C /Volumes/JW-EXT/jw-wt/mythos-repo worktree add --detach \
  /Volumes/JW-EXT/scratch/sol-offload-icloud/review/retry-tree 27e4070c4
```

From retry-tree:

```sh
env TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp \
  PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest \
  tests.test_span_offload tests.test_docs_freshness tests.test_git_fixture_maintenance
```

**105 tests passed in 38.615 s**, including the new iCloud retry regression and the
existing local-backend exit-code regression. Log: `tmp/delta-focused-tests.log`.

```sh
env TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp \
  PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B \
  /Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp/delta_independent_probes.py
```

**26 independent probes passed.** The original 21 probes were rerun against retry-tree,
with the repeated-unconfirmed expectation changed from 3 to 8 and byte-preservation
checked. Added successful upgrade and four invalid existing-record probes. The fake
brctl remains first on PATH; synthetic dataless state is tracked by inode rather than
placeholder size. Real iCloud is never called and actual SF_DATALESS flags are never set.
Source, log and structured results:

- `tmp/delta_independent_probes.py`
- `tmp/delta-independent-probes.log`
- `tmp/delta-independent-results.json`

The re-executed probes cover pending-to-ready and stuck status, four confirmed
readbacks and byte-identical Air pull, no-op eviction/download, download failure,
truncation and corruption, mixed confirmations, immutable retry, existing foreign
bytes, linked iCloud ancestors/plan/artifacts, stage mutation, first-writer marker
preservation and SIGTERM/SIGHUP/SIGINT child cleanup. Their consequences remain as
recorded in the original report, except for the repaired retry classification.

Additional read-only checks passed:

```sh
/opt/homebrew/bin/python3.13 -B scripts/gen_state.py --check
git diff --check da02b7fde..HEAD
```

`tmp/delta-state-check.log` is empty with exit 0. The final detached checkout is clean.
Broad quick/full suites were not run, as directed by the original brief; final GitHub
Actions completion remains the lead's gate and is not asserted by this report.

## Next exact step and limits

The lead should record the resolved finding and this final-head admission, then verify
the GitHub Actions gate ledger for `27e4070c49c1b27223afbc6cc18635efc763b5b4`.
Any later code change needs the applicable delta verification. Live macOS 26 status,
command/flag transitions and production-key round-trip qualification remain the lead's
separately authorized work. The research lead owns A.3 permanence; actual off-MBP key
custody was not inspected. This software verdict grants no merge, deployment, host,
measurement or policy authority.

VERDICT: ADMIT
