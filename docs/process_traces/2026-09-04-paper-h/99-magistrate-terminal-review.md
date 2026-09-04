# Paper H — magistrate terminal review (apex read)

Date: 2026-09-04. Merge candidate: `feat/2026-09-04-paper-h` at 970c0b1a (= final bench round d8024f7b + origin/main a1184cca merged, docs-only).

## What I read
The whole `docs/paper` diff of the landing before fix round 1 (Section 1 rebuilt in dependency order: sampling record → prefill/decode → phase edge → the straddling record and the transferred energy slice → why repeats cannot remove a shared displacement → commanded pulses recorded by command timestamp with observed onset → pulse-derived limit → inserted-gap check → clock mapping with the monotonic clock built → configuration cell → component built from the two observations → resolution bound / cell floor → recorded-edge and moved-edge limits → independent-edge ratio → shared-error ratio with both symbols assigned → authentication / evaluation → twofold contribution → decision rule); the two refuter verdicts (pedagogy, fact), the round-1 delta, the Opus counter-review (CR-01..08), cold ruling 06, the round-2 fix, the reading-order delta 08, cold ruling 09, and I applied ruling 09's two texts myself at the bench (trace 10).

## Design-level answers (row 7)
1. **The forcing problem now precedes every name.** A reader meets the straddling power record and the transferred energy slice before any ratio symbol; the two ratios are derived from that picture rather than announced. This is the writing standard's core requirement and the reason the glossary dump was a debt.
2. **The gate history is the interesting part.** Two cold gates fired on this lane: the first because a cure sentence re-introduced the defect it cured (a forward reference to A/B), the second because the line-granular reading-order clause was over-applied to line wraps and in-sentence glosses. Ruling 09 fixed the unit of the clause (the SENTENCE) and corrected its own predecessor's verbatim text. Both rulings are in the trace and bind future paper seats: pedagogy deltas audit the words a cure ADDS, sentence by sentence, not only the cured term.
3. **Residuals registered, not hidden:** the frozen Abstract's own use of "required" (ruling 06 Q4: Abstract owner's item); CR-05..08 nits deferred to the next paper seat with their line references in trace 05.

## Overbuild / merge-ability (row 8)
Prose only; no code. Nothing to prune.

## Integration replay (row 9)
Full unpiped suite on 970c0b1a, log `~/.claude/jobs/3c46c831/tmp/int-paper-h-replay.log`; exact tail appended below when it completes.

```text
FAIL: test_logical_producer_delay_preserves_exact_evidence_bytes (test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes) (artifact='instrumen
FAIL: test_logical_producer_delay_preserves_exact_evidence_bytes (test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes) (artifact='events.js
FAIL: test_real_client_worker_artifact_contract_over_localhost (test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost)
FAIL: test_absent_sentinel_commits_status_as_before (test_window_status_guard.WindowStatusGuardTests.test_absent_sentinel_commits_status_as_before)
FAIL: test_present_sentinel_writes_status_without_git_publication (test_window_status_guard.WindowStatusGuardTests.test_present_sentinel_writes_status_without_git_publication)
Ran 4900 tests in 6744.169s
FAILED (failures=5, skipped=125)
rc=1
```

Exact tail of the unpiped full suite on 970c0b1a (paper-H + main a1184cca): 4900 tests, 5 failures, 125 skipped. All five are outside this PR's files (paper prose only) and each is explained: (1) `test_node_worker_subprocess…over_localhost` fails on main in isolation (pre-existing, recorded in the paper-E/G reviews); (2) the two `test_logical_producer_delay_preserves_exact_evidence_bytes` subtests are load-sensitive and PASSED when re-run in isolation on this tree (`int-paper-h-replay-isolated.log`: that test OK); (3) the two `WindowStatusGuardTests` fail identically on canonical main at the same moment with `REFUSING: a measurement process is running` — the guard's process census sees the concurrent replay/seat fleet on this machine, an environmental refusal, not a code defect. Row 9 satisfied with those exclusions recorded.
