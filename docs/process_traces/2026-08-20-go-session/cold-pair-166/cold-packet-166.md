# COLD-GATE PACKET: may PR #166 merge on this gate evidence? (mechanically assembled, no advocacy)

## The question
PR #166 (paper pedagogy rewrite) is gated by repo convention on (a) a full
canonical suite run green at its head and (b) CI green. Neither is green.
The magistrate proposes neither to merge over red nor to rerun-until-green,
but to put the interpretation question to this cold gate: does the gate
evidence below constitute a stop signal AGAINST merging #166, or a defect
class independent of the PR that the gate ruling may sever from it — and
under what conditions, if any, may #166 merge before the defect class is
fixed?

## The PR
- #166, branch impl/paper-pedagogy-r4, head a8f1549.
- Diff vs main (3d0b48a): docs/paper/draft-v1.md ONLY (two commits:
  32b5424 = 223+/89-, a8f1549 = 5+/5-). No code, no test, no config paths.
  `git diff main...impl/paper-pedagogy-r4 --stat` confirms the single file.
- Gauntlet already complete: round-4 pedagogy lens -> xhigh rewrite ->
  terra xhigh delta review with arithmetic replay (NO-GO cured at bench) ->
  lead full read. No open findings.

## Gate evidence
1. Canonical run 1 at a8f1549 (2026-08-20 ~21:35-22:20 PDT, CONCURRENT with
   two Codex refuter suites + a second canonical attempt on this machine):
   Ran 3835, FAILED (failures=2, skipped=95). Both failures are subTests of
   test_calibration_exits.PublicGovernedExitWitnessTests.
   test_logical_producer_delay_preserves_exact_evidence_bytes — the N-5
   test, previously root-caused (time.time() origin) and fixed on main at
   46d710f with cause classified "probable". Log:
   scratchpad/canonical-paper-a8f1549.log (this session's scratchpad).
2. Canonical run 2 at a8f1549 (QUIET machine, ~22:22-23:07 PDT):
   Ran 3835, FAILED (errors=1, skipped=95). The error is a DIFFERENT test:
   test_calibration_exits.SamplerLifecycleHardeningTests.
   test_detached_grandchild_is_reported_by_post_teardown_census —
   ValueError int('') reading sampler_pid_path at line 2207: the test read
   the PID file before the detached grandchild wrote it. The N-5 test
   PASSED in this run. Log: scratchpad/canonical-paper-a8f1549-quiet.log.
3. CI on #166: job calibration-exits-exclusive (3.11) failed twice
   (initial + rerun, ~15 min apart in wall time), same assertion both
   times: test_forced_auto_maintenance_mutation_reproduces_cleanup_race,
   AssertionError 2 != 39 (ENOENT where the test asserts ENOTEMPTY), with
   test stdout RACE_EXERCISED=0. The (3.14) variant passes. The same job
   has failed on EVERY main-branch CI run since 2026-08-20 13:22 PDT; the
   first failing window (b9e197a -> 0f5ade6) contains only docs/custody
   commits. Main was green at 12:21-12:27 PDT. PRs #163, #164, #165 were
   merged by the prior session with this shard already red on their PR
   checks; no recorded disposition of that has been located in RUN_STATE
   or the go-session custody.
4. Module flake history (repo record): PR #121 failed on a FLAKE
   "test_calibration_exits OSError Directory-not-empty"; #127 recorded
   5317s hosted-shard vs 146s bench timing disparity (RUN_STATE ~1083,
   ~1484). N-5 itself survived a full seat pass unreproduced before being
   root-caused.
5. In flight: a terra xhigh root-cause/fix session (ledger run 58) on the
   CI failure (item 3), write-scoped to tests/test_calibration_exits.py,
   required to preserve the test's discriminating power. Not yet returned.

## Facts bearing on severability
- All three gate failures are in one module, test_calibration_exits; each
  is a distinct timing/synchronization race; none is reachable from a
  markdown diff. The three summaries differ (failures=2 / errors=1 /
  assertion-errno), i.e. NOT the same signature repeating.
- The repo's own methodology (paper §4, N-5 lesson) forbids retrying until
  a favorable outcome and requires root-cause over reclassification.
- Rule-11 standing triggers: reinterpreting a stop signal requires this
  cold ruling; two same-signature failures require a consult (the three
  failures here are distinct signatures; the CI failure alone is the same
  signature 4+ times and already has a consult-grade session on it).

## What a ruling should decide
R1. Whether #166 may merge before the calexits defect class is fixed, and
    if so on exactly what recorded basis (e.g. diff-unreachability of the
    failing module for a docs-only diff), stated as a narrow precedent
    that does NOT generalize to code diffs.
R2. Whether the three races + history constitute one registered defect row
    (module-wide timing hygiene) or separate rows, and their severity.
R3. Whether the prior session's merges of #163-#165 over the red shard
    require retroactive action (e.g. a recorded deviation note, additional
    verification) beyond the run-report disclosure already planned.
R4. What the RH PR #167 (CODE diff) requires: it is agreed it cannot merge
    without a green canonical at its head; decide whether a green run with
    the known-flaky module's failure classes explicitly quarantined-and-
    rerun-in-isolation is acceptable if a full green cannot be obtained on
    this hardware tonight, or whether it must wait for the calexits fixes.
