# T20 ERRATA

## E-1 — 97e0203's commit message falsely records CI run 32605897516 as SUCCESS (correction of record, 2026-08-22)

The close-out commit `97e0203` states the cure run "concluded SUCCESS —
the incident is closed; the flake did not fire on the cure run." That
claim is FALSE. The run concluded **FAILURE** on `test (3.14, 4)`.

**How the false claim was produced:** the magistrate treated
`gh run watch <id> --exit-status` returning exit 0 as proof of a green
conclusion. The watch's captured output shows it reported only an
`installed-wheel` job line — it did not track the run to its true
conclusion, and its exit code was not a valid green signal. The run
report's own §8 caveat ("the cure is not yet confirmed green") was
correct and was overridden without adequate verification.

**What is actually true at `6693cfa`:**
- The tail-body cure WORKED: `test_decision_index_matches_decision_bodies`
  appears in the failed-test lists of the pre-cure runs (e.g.
  32601180503) and is ABSENT from the cure run's failures; the suite
  passes locally at the same tree (46 tests OK).
- The cure run failed on a NEW, DISTINCT defect:
  `ERROR: test_public_author_executes_target_bytes_and_binds_executed_file_sha`
  (`tests/test_arm_readiness_evidence_author.py`) with
  `OSError: [Errno 39] Directory not empty: '/tmp/.../repo/.git'` —
  the #121-class git-teardown ENOTEMPTY race, in a different module
  (temp-git-repo teardown during hosted-runner load). Registered as
  kernel row `EVIDENCE-AUTHOR-GIT-TEARDOWN-01`.

**Binding lesson (folded into the run report's operational notes by
pointer):** a CI conclusion is verified ONLY by
`gh run view <id> --json conclusion` (or the equivalent field read) —
never by `gh run watch` exit codes, and never by absence of failure
lines in a partial watch transcript.

The commit message itself is immutable history; this erratum is the
correction of record, cross-referenced from the run report's CI
section.

## E-2 — c09351d run 32607418551 disposition + the ack-timeout unification (2026-08-22 late)

The errata commit's own CI run concluded FAILURE on two exclusive
shards. Disposition: NO defect in the pushed diff (docs + kernel only);
both failures share ONE root signature — `RuntimeError: test sampler
acknowledgement timeout` raised by the shared harness driver
`scripts/validate_powermetrics_fiducial.py:264` under hosted-runner
load:

- `calibration-writer-crash-matrix-exclusive (3.11)`: third same-day
  firing (`pulse_command_off:63`).
- `calibration-exits-exclusive (3.11)`:
  `test_parameterized_durable_public_cli_witnesses` failed
  `correction=calibration_rederive_failed` caused by
  `pulse_command_on:42` — the SAME driver line. This preserves, for the
  first time, the failure custody that the A79 audit's row 6 (the
  2026-08-19 parameterized-witnesses observation) lacked; the audit's
  refusal to force-join that row without evidence was correct at its
  evidence state and is now resolved WITH evidence.

Kernel action: CALWRITER-ACK-TIMEOUT-01 broadened to the shared-driver
mechanism and escalated P3→P2 (three firings in one day red required
shards). 97e0203's run 32607323880 concluded SUCCESS (verified via the
conclusion field per E-1's lesson) — no disposition needed there.
