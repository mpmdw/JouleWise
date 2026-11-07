# Executing review: lane/2026-11-06-b5-robust at 9eb90c6c5 (2026-11-06)

Reviewer: lead (Opus 5.5), with one local Sol 6.1 xhigh critic run on the same diff.
Scope: `git diff 288c094f4..9eb90c6c5` (resume, step retries, defect sweep, timer
events, harness flags, tests, report). Fresh clone at
`jw-wt/b5-robust-rev`. Synthetic data only. All local work was niced
(`nice -n 19 taskpolicy -b`), with targeted unit modules only, because dry-k
was running on the Air.

## Verdict

The happy path is unchanged. Resume and retry are correct for every case the
tests exercise, except for two defects, both now fixed on the branch in
`150b8e7b3` with regression tests:

1. **Fixed: a lost worker observer in a builder step was never retried.**
   Builder steps are 0, 1, 3 and 3b. Their retry rebuilds the earlier state
   before switching to serial. The failed attempt's sticky
   `worker_observer_unavailable` flag was still set at that point, so
   `rebuild()` refused with `rebuild_deadline_fired`, the retry loop hit `break`,
   and the step stayed a `tooling_refusal` (exit 2). It was found by Sol and
   confirmed by the lead.
   - The fix: the retry calls `resume.serial()`, which clears the flag, shuts
     down the member pool and sets workers to 1, before it restores or rebuilds.
     The rebuild state takes the serial worker count. A refused restore puts the
     worker count back.
   - Test: `ExecutingReviewTests.test_a_lost_worker_observer_in_a_builder_step_is_retried`.
     It fails before the fix and passes after. After the fix the record bytes,
     stderr and tree equal the uninterrupted run, with one logged `step_retry`
     (step 1, observer unavailable, rebuilt).
2. **Fixed: a malformed checkpoint escaped as a traceback.** `load()` checked
   only top-level types. For example, `binding: null` raised `AttributeError`
   out of `run()`; Sol found it. Bad `step_records`, `raw_codes`, `outputs`,
   `position` and `parts` did the same, or broke later in
   `restore()`/`verify_state()`.
   - The fix: `load()` now checks every nested shape those functions read, and
     each record row must construct a `StepRecord`. A malformed checkpoint is now
     `resume refused: checkpoint_invalid`, exit 2.
   - Test: `test_malformed_checkpoint_fields_are_a_closed_refusal` covers eleven
     mutations and fails before the fix (six errors, six failures). Restoring the
     original checkpoint then resumes to the reference run.

Not fixed (all are in the Findings section below): a deterministic worker crash
now crashes the driver process when the step is retried serially; orphaned pool
workers could race a resume started immediately after a kill. Real-chain resume
evidence beyond step 0 is in the cloud section at the end.

## What I checked

**Equality on the happy path (independent probe, not the builder's script).**
I ran a fresh script, `eq.py`, at `288c094f4` (a worktree) and at `150b8e7b3`,
with the same fixed temp root, workers 1, and nine S10 DriverDouble
configurations: happy, p42, step-1 bundle refusal, step-4 target refusal, step-5
exception, step-6 refusal, step-6 outcome (exit 3), real 9b and bad projection.
For each one it compared the exit code, record sha256, stdout, stderr and the
restricted tree (timer logs excluded).

| Config | Exit | Record | stdout/stderr | Tree |
|---|---:|---|---|---|
| happy | 0 | `54f348c897b9` equal | equal | equal |
| p42 | 0 | `ae4413a2fa03` equal | equal | equal |
| outcome | 3 | `49f684f3790e` equal | equal | equal |
| target, ref6, real9b, badproj | 2 | equal | equal | equal |
| exc5 | 2 | `a004bd89e68f` equal | equal | one traceback log differs (worktree path and line numbers) |
| bundle (step-1 refusal) | 2 | `63ff87600fcc` equal | +4 sweep count lines | + `restricted/defects/` (9 entries) |

The only differences are the two the builder declared. The builder's cloud
real-chain equality for `--stop-after 5` (`8def95ee...`, 1,356 of 1,358 files)
was not rerun. My change does not touch the happy path. It changes only the
retry branch and `load()`.

**Resume correctness (read and probed).**
- Rollback re-hashes every checkpointed file before it moves anything. A
  rerun never sees partial outputs from the crashed step: they go to
  `resume/abandoned/<n>/`, and new empty directories are removed.
- Of the in-memory state, steps after 3b change only the fields the checkpoint
  restores. `grep` found no non-builder step writing other `RunState`
  attributes. The rebuilt builders register content-addressed names, not names
  that depend on the log counter, so rebuilding 0, 1, 3 and 3b without the
  steps between them yields the checkpointed names.
- The binding (mode, commit, checkout state, index digest, store mode,
  synthetic) refuses a resume against a different run.
- A torn record is set aside. A complete record is reported only after its
  outputs re-authenticate.
- All 24 builder tests pass, plus my two regressions.

**Retry classification.** `retry_reason` retries only these: the run observer's
`calibration_wall_deadline_fired`; `calibration_deadline_observer_unavailable`
while the run's observer exists; an escaped `BrokenProcessPool` with no code.
Everything else is never retried, including data refusals, `VDL_DEFECT`,
checkout and preflight refusals, and refusals with no observer. Retries are
bounded by `MAX_RETRIES = 2`, and each one is logged to `recovery.jsonl` and the
structure-tier `step_retry` line.

The decision reads only the host signal, as the earlier ruling requires. A
firing masks the attempt's result, so retry-or-not reveals nothing about the
outcome. The rerun reaches the record an operator's full rerun would reach.

The VDL store keeps only the entries of consumed tasks that did not fire, and
poison from the failed attempt only blocks reuse. A retry therefore cannot reuse
anything a firing attempt produced.

**Defect sweep.** It runs only after the record is written and the exit code is
set, and only for a stopping data refusal at step 1 or 2. It never excludes a
unit. Stderr carries per-window defect counts of kept bundles: data-integrity
structure, not an outcome. Any exception becomes a restricted
`defect_sweep_failed` note.

**Estimator fidelity.** Not applicable to this lane. No estimator,
refusal-class file or r1-pinned function changes, and
`test_result_equivalence` passes, including the r1 decoder test.

## Findings

| # | Source | Severity | Finding | Disposition |
|---|---|---|---|---|
| 1 | Sol, confirmed | P2 | Builder-step retry after a lost worker observer never runs (sticky flag fails the rebuild) | **Fixed** `150b8e7b3` + test |
| 2 | Sol, confirmed | P3 | Malformed nested checkpoint fields escape as uncaught exceptions | **Fixed** `150b8e7b3` + test |
| 3 | Sol | P1 claimed | An edited checkpoint census row (or any other edited checkpoint field) is trusted on resume | **Accepted as design, not fixed.** Resume defends against crashes, not against someone editing restricted custody. Step records, raw codes and outputs of non-builder steps come from the checkpoint by design; a keyed MAC would need a secret the run does not have. An accidental edit almost always breaks the canonical JSON or a hash. |
| 4 | Sol | P1 claimed | The completed-record shortcut does not call `validate_dry_run_record`; a canonical record with a flipped `completed_without_tooling_refusal` is reported | **Rejected.** The shortcut reads only a record this driver validated and wrote in one write. A torn write is caught. A record edited to stay canonical is the same trust boundary as finding 3. |
| 5 | Sol | P1 claimed | The completed-record shortcut does not re-authenticate archive inputs, and after checkpoint cleanup it accepts a dirty checkout at the same HEAD | **Rejected.** The record was produced from authenticated inputs before the crash. Reporting it is what the uninterrupted run did. With the checkpoint present, the binding refuses a dirty checkout. Without it, the record's own commit binding stands. Low value, not worth the extra code. |
| 6 | Lead | P3 | After a `BrokenProcessPool`, the serial retry runs child programs in the driver process (`workers=1`, `StepRunner.run` calls `main` in-process). A deterministic native crash (segfault) that killed a pool worker would now kill the driver: no record, and `--resume` would repeat the same thing. Before, it was a closed `unclassified_refusal` record. An OOM is the likelier cause, and serial uses less memory. | **Open.** It only affects a run that would have failed anyway. The operator falls back to a fresh run. A fix (retry in a fresh single-worker pool) is not worth the code now. |
| 7 | Lead | P3 | A SIGKILLed driver's spawned pool workers finish their current task (and write into `restricted/`) before they exit. A `--resume` started within seconds could race them: files appear after rollback, or `'x'` opens collide. | **Open: operator note.** Before `--resume`, check that no spawned worker of the dead run is alive (spawned workers show as `multiprocessing.spawn` processes: `pgrep -fl multiprocessing.spawn`). Add it to the runbook line in the robust report. |

## Evidence

Every command was niced with `taskpolicy -b`, run with
`TMPDIR=/private/tmp/jw-robust-tmp/rev` and `python3.13 -B -m unittest`, from
the clone `jw-wt/b5-robust-rev`.

- At `9eb90c6c5`, before my change, `test_resume` plus
  `test_resume_correctness` ran 24 tests: OK (303 s).
- New `ExecutingReviewTests`: 2 tests. Both fail at `9eb90c6c5` (7 failures, 6
  errors across subtests) and both pass at `150b8e7b3`.
- Suites at `150b8e7b3` (all OK):
  - `test_resume`: 13 tests;
  - `test_resume_correctness`: 13 tests (the builder's 11 plus my 2);
  - `test_parallel_steps`: 24;
  - `test_phase_timing`: 34;
  - `test_deadline_observer`: 17;
  - `tests.test_custody_mode_inventory`: 7;
  - `test_result_equivalence`: 98, with 2 environment-gated skips;
  - `test_dry_run`: 66, with 3 skips.

  `test_joined_probes` and `test_release_equality` were not run locally. They are
  full-chain runs, and the load rule rules them out while dry-k runs.
- Equality probe outputs: `/private/tmp/jw-robust-tmp/eqscript/{base,head}.json`
  (scratch, not committed; the script is `/private/tmp/jw-robust-tmp/eqscript/eq.py`).

## Real synthetic-chain resume (cloud Sol)

These runs replace the builder's pending task `task_e_6aee68c1...`, which ended
in ERROR with no diff. The first relaunches of B and C (`6aee8c6b`, `6aee8c6f`)
treated the normal `--stop-after` closure (harness exit 1, driver exit 2) as a
failure and stopped after run A. They were relaunched with that stated
explicitly. Both runs are on `9eb90c6c5`, which has the same resume path as
`150b8e7b3`; my fix only touches the retry branch and the stricter `load()`.
Python 3.12.13, 3 cores, `--workers 2`.

**B: killed right after step 3b's checkpoint, then resumed**
(`task_e_6aee91dc54f88322a1c2ab1ad1ede9c2`; evidence in
`2026-11-06-b5-robust/e2e-resume-B/`): **EQUAL.**
- The resume rebuilt the real step 0, 1, 3 and 3b builders, including the 3b
  brackets.
- `record_sha256` is `e34e60a2...cd19` in both runs, the driver exit is 2 in
  both, and all 1,336 manifest paths are identical. The comparison drops
  `restricted/resume/` and the timer logs, and no difference remains.
- B's `restricted/resume/` holds only the old process's timer logs (under
  `abandoned/1/`) and `recovery.jsonl`.
- Wall time was 661 s for the reference run and 1,371 s for the killed and
  resumed run.

**C: killed inside step 5, then resumed** (`task_e_6aee943fd2e083229e7d64f066a23d4f`):
**Pending.** The combined task, with the reference run and the C run in one
session, ended in ERROR with no diff after about 1 h. That is probably the
session limit: the builder's original task died the same way. The reference A
run of the first C attempt (`9eb90c6c5`, record `5d561618...306a`, 1,358
files) finished before that agent stopped. It is saved as
`2026-11-06-b5-robust/e2e-resume-C/A-summary.json`. The C run alone was
relaunched on the same branch at `150b8e7b3`:
`task_e_6aeea281379483228abd1affc6008133`. Its summary is compared against
that A summary.

## Sol audit

There was one local Sol 6.1 xhigh run (`codex exec ... -s workspace-write`) in
its own clone, `jw-wt/b5-robust-rev-sol`, with the blinding rule verbatim in its
prompt. The events are in `jw-wt/b5-robust-rev-sol.events.jsonl`. A first
attempt stopped before it read anything, because a nested `nice` is refused
inside the sandbox; its events are in `...events.try1.jsonl`. The rerun was
launched under nice, and its commands inherit the priority.

`/usr/bin/grep -E 'jw-b5-|night-custody|night-archive|night-|restricted/'`
found 19 lines, and I read every hit:
- Repository source and docs text that contains these strings, such as
  `restricted/resume/...` in the diff and `night-custody/` prefixes in archive
  code.
- One `rg` pattern search of a test file.
- Sol's own synthetic test writing `dry-run/restricted/...` under its temp
  custody in `/private/tmp/jw-robust-sol-tmp`.

No command touched `/Users/edr/jw-b5-*`, `/Users/edr/night-*` or a real
restricted directory. **AUDIT CLEAN.**
