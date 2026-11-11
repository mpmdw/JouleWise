# Opus cold review: BYTES RL-7a (Paper 1 seat 3)

Reviewer: Opus 5.5 cold seat, 2026-11-10. Branch `ops/2026-11-10-bytes-rl7a` @ `2cdff1d05`, base
`lane/2026-11-07-bytes-stage1-run` @ `e091c0881`. Read first: RL-7 and RL-24 (row 3), BY-01, BY-02, BY-06
(`next-block-designs.md` §2.4) and the BYTES rows of `paper-audit.md` (§2.4, F-08, objection 6), all on
`origin/audit/2026-11-10-fable`; then the seat's run report and design note. The research lead reviews next.

**Blinding.** Synthetic only. I read code, tests, the audit and the registered manifest config. I opened no
BYTES export, store, key, archive, custody, night-* or restricted path, and no path outside the two review
worktrees and Git objects. Every probe below ran in a temporary Git repo built by
`tests/bytes_commitment_support.py`.

## Verdict: ADMIT-WITH-FIXES

- **Probe fix (BY-02): admit as is.** It closes #701 F1 and F5 and leaves the estimator untouched.
- **Commitment check (BY-01): admit as a strict improvement on the regex. It does not yet prove "committed
  before unblinding."** R-01 to R-04 must land before `record-push` creates the real stage-1 commitment
  (RL-7(e): by 19 Nov). Stage 1 itself never calls this gate, so these fixes do not delay stage 1.
- **Stage 1** may run once R-05 is closed or structurally confirmed. F6 and F7 do not block it.

## (1) Does the commitment check prove "committed before unblinding"?

What holds: the object must be a full-id commit and an ancestor of the analysis `HEAD`. The prediction
bytes and sidecar must equal the committed blobs. The committed `joulewise/bytes_analysis.py` and the
`bytes_analysis_sha256` in the prediction JSON must both equal the registered pin. Chronology is checked
against the journal, the heldout `release.json` files and **every Git revision of the two metadata paths
across all refs**. Admission is written to the journal and fsynced before any heldout read. Twenty-three of
the 25 new tests fail on the old code (see (3)).

What does not hold, shown with synthetic probes
(`python3.13 -B -I probe_commitment.py <worktree>`, a scratchpad script that is not committed):

| Probe | Attack | Result |
|---|---|---|
| P1 | Unblinding admitted at 12:00 under C1, with the journal intact but uncommitted (the state `admit()` leaves it in). A new prediction commit C2 is made afterwards with `GIT_COMMITTER_DATE` 10:30 and attested `pushed_utc` 10:31 | **ACCEPTED** |
| P2 | Same as P1, but the journal had been committed on any ref before C2 was made | refused (history-descent check) |
| P3 | A local-only commit, with **no remote configured**. `refs/remotes/origin/*` was written with `git update-ref`, which is what the test fixture itself does | **ACCEPTED** |
| P4 | A post-unblinding commit with honest dates, after the working-tree journal was truncated or a fresh clone was used | **ACCEPTED** (disclosed limit) |
| P5 | Is a journal event's `stage1_commit` checked against the commit under test? | No |

The specific questions:

- **Can a commit made after unblinding satisfy it?** Yes. It needs backdated dates while the journal is still
  uncommitted (P1), or a lost journal (P4). It cannot once the journal has been committed to any retained ref (P2).
- **Clock manipulation?** Yes. `%cI` is set by the committer and `pushed_utc` is a free-text attestation
  (`scripts/bytes_commitment.py:110-111`, `:207-208`). The only clock-independent anchor is a committed
  journal revision.
- **Local-only commit?** Yes. "Reachable from origin" (`:102-109`) is checked against local
  `refs/remotes/origin/*`, which anyone can write. RL-7(a)'s "reachable from `origin`" is therefore not
  actually verified.
- **Force-push?** It is detected only after the operator fetches. A stale snapshot passes. The origin-tip
  ancestry check (`:108`) is sound once the snapshot is fresh.

The seat states these limits honestly in the run report and in `docs/design/bytes_commitment.md` §Limits. The
cheap fixes are R-01 to R-04. R-01 is the one that turns the sentence objection 6 asks about ("Show me") into
evidence held by a third party.

## (2) The probe fix leaves the estimator unchanged

`shasum -a 256 joulewise/bytes_analysis.py` gives `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`
at head and at base. `git diff base...head -- joulewise/` is empty.

`_expected_no_key_refusals` (`scripts/bytes_stage1.py:266-275`) requires equal exit 1 on both no-key
probes. It also requires these exact diagnostics on their streams, with nothing on the other stream:

- the analysis prints `BYTES analysis refused: configuration still blinded: <key>`
  (`joulewise/bytes_analysis.py:826` → `scripts/bytes_analyze.py:148`);
- the twin prints `refused: blinding key missing or unreadable: <empty>/pack.json`
  (`scripts/bytes_twin.py:624`, `:2348`).

The allowed key set is `neg8_reference` plus the fit keys. That matches what can reach `_released_rows` at the
fit stage (`bytes_analysis.py:941-963`: fit cells plus reference roles, and every reference row is
`neg8_reference`). So a real run does not hit a false rc 9. The real-subprocess synthetic E2E run
(`RunTests.test_pre_commit_sequence_writes_agreeing_predictions`) reaches `READY_TO_COMMIT` through this
gate. rc 4 is kept. The new completeness gates (rc 8 and rc 10) close F5.

## (3) Tests fail on the old code

I copied the new `tests/test_bytes_stage1.py`, `tests/test_bytes_commitment.py`,
`tests/bytes_commitment_support.py` and `tests/test_bytes_agreement.py` onto a base (`e091c0881`) worktree:

- `tests.test_bytes_stage1.ReleaseGateTests` gives **6 tests, 11 failures**: 7 no-key fault subtests, the
  missing blinded/fit products and the exit-only agreement. This matches the seat's replay.
- `tests.test_bytes_commitment` gives **25 tests, 22 failures and 1 error**. The 2 that pass on the old code
  are the positive cases (fit release ignored, timezone normalised), which the regex trivially accepts.
  Caveat R-06: for `bytes_twin` and `b6_unblind`, the entrypoint subtest passes on the old code too.

On head, run serially as briefed: `tests.test_bytes_stage1` gives 22 OK (32.2 s), `tests.test_bytes_commitment`
gives 25 OK (6.9 s) and `tests.test_bytes_twin` gives 103 OK (106.5 s).

## (4) Do the open items block stage 1?

- **F2 downstream: conditionally.** The driver's census skips withheld-layout paths (`bytes_stage1.py:82-87`).
  The pinned analysis (`bytes_analysis.py:1108`) and the twin (`bytes_twin.py:2286`) do not: both
  `rglob("*.runs.csv")` the export roots they are given. If a `withheld/<pack>/<session>.runs.csv` sits under an
  export root, held-out (blinded) rows would enter the pre-commitment blinded and fit runs, against the
  2026-10-20 item 1 ruling. The exporter writes the store under `key_dir.parent/withheld/`
  (`joulewise/b6/blinding.py:177`), which is custody and not the export tree, so the registered layout probably
  avoids this. "Probably" is not enough for a seal. See R-05.
- **F6 (shared collection hazard path) and F7 (B6 tolerance in `joulewise/b5/harvest.py:904`): not blocking.**
  Neither `joulewise/bytes_analysis.py` nor `scripts/bytes_stage1.py` imports `run_campaign`'s hazard path or
  `b5.harvest`. Stage 1 runs on existing exports. Both items block reuse of this merged lineage for B5 harvest
  or collection, and must stay open against that use.
- BY-06 (MBP time) is unchanged by this branch.

## (5) Reads of held-out data

None found. Every fixture is a temporary directory. Entry-point tests pass `NEVER_OPEN` and patch
`Path.open`. The `ReleaseGateTests` manifest reads only the registered config
`configs/bytes/bytes_manifest.json`, with synthetic temporary session paths. The guard reads Git objects and
named metadata only, and never searches exports. One absolute local path appears in a desk report link (R-07).
It is a link only and is never read.

## Findings

| ID | Sev | Path:line | Finding | Fix |
|---|---|---|---|---|
| R-01 | HIGH (blocks `record-push`, not stage 1) | `scripts/bytes_commitment.py:102-111`, `:206-210` | "Reachable from origin" is checked against local remote-tracking refs, and the push time is a free-text attestation. A local-only commit passes (P3). RL-7(a) is not met as written | In `record-push` only (one networked step on the Air): require `git ls-remote origin refs/heads/records/2026-11-bytes-stage1` to equal `origin_tip`. Capture the server's push event (`gh api repos/{owner}/{repo}/activity?ref=…&activity_type=push`: `timestamp`, `after`, no `force_push`) into the receipt as raw JSON, and use that server timestamp as `pushed_utc`. Commit and push the receipt. Protect `records/*` against force-push and deletion. `check` and `admit` stay offline |
| R-02 | HIGH (blocks `record-push`) | `scripts/bytes_commitment.py:82-88` | Journal events are compared by time only. Their `stage1_commit` is never checked against the commit under test, so a backdated post-unblinding commit passes with the journal intact (P1) | In `_check_events`, require `event['stage1_commit']` and refuse any heldout event naming a different commit. This makes the intact journal a clock-independent anchor. Add the P1 test |
| R-03 | MED (before `record-push`) | `scripts/bytes_commitment.py:173-187` | Admissions are appended to an uncommitted working-tree file. Truncating it or using a fresh clone erases the history (P4); only committed revisions are durable | Before appending, refuse unless the working-tree journal equals `HEAD:docs/bytes/stage1/unblinding.jsonl`, so every earlier admission must already be committed. Print the commit-and-push instruction after each append. Alternatively, auto-commit the journal line |
| R-04 | MED (before `record-push`) | `scripts/bytes_commitment.py:163`, `:170` | `--commitment-repo` can name any checkout, with its own journal and `HEAD`. The asserted "analysis head" need not be the code that is running | Refuse unless `git rev-parse --show-toplevel` of the commitment repo equals that of `ROOT` (tests already patch `ROOT`). Otherwise record `ROOT`'s `HEAD` and dirty flag in the receipt and require equality |
| R-05 | MED (close or confirm before stage 1) | `scripts/bytes_stage1.py:82-87` vs `joulewise/bytes_analysis.py:1108`, `scripts/bytes_twin.py:2286` | F2 downstream: the census silently skips withheld-layout paths that the pinned analysis and twin would still read | In the driver (outside the pin), refuse with rc 1 when any `withheld` component or `*.withheld.csv` exists under an export root. This is a listing only, nothing is opened. Add one synthetic test. Alternatively, the lead records a structure-only listing of the real export roots showing no such path |
| R-06 | LOW | `tests/test_bytes_commitment.py:175-193` | The entrypoint test passes on the old code for `bytes_twin` and `b6_unblind`, because the patched `Path.open` raises `AssertionError` and `except Exception` turns it into rc 1. It is not failing-first for those two | Assert that the captured output names `BYTES commitment` and that the `Path.open` mock was never called |
| R-07 | LOW | `docs/research/…/interp-energy-desk/bytes-rl7a-sol-report.md` | The link points to `/Volumes/JW-EXT/jw-wt/...`, a machine-local absolute path | Use the repo-relative link |
| R-08 | INFO | run report, F6/F7 rows | Correctly left open. They do not touch the BYTES stage-1 import graph | Keep them tracked against B5 use of this lineage |

## Order for the lead

1. Stage 1 can proceed on this branch once R-05 is fixed or confirmed. The probe gate is sound.
2. Before the commitment is recorded, land R-01 to R-04 (about 60 lines plus 4 synthetic tests) with a short
   Sol or Opus re-check of the new tests' failing-first status. R-01 needs one networked step at `record-push` time.
3. R-06 and R-07 can ride along.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
