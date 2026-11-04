# D-188 block-5 analysis rewrite: retrospective, 2026-11-03 to 11-04 (UTC)

Written on 2026-11-04 by the block-5 lead (Opus 5.5, laptop session on the M4 Air analysis box) from the lead's fact sheet for the period and the merged PRs. The running pointer is `RUN_STATE.md` item 165. Times are UTC. No custody content was read for this document: every statement about real runs comes from exit codes, step status, structure-only probes or the blinded comparator.

## Summary

D-188 (Ed, 2026-11-02) let a restructured block-5 analysis replace r1 if it gives equal registered numbers and identical decisions. By 2026-11-04 the rewrite was built, reviewed, merged and tagged (`b5/analysis-r2` → `929fc65c9`).

Cycle time for one blind dry-run attempt fell from about a day or more to under two hours:
- On r1, attempt D died at step 9 on ENOSPC after 18.5 h, and attempt E took 27.1 h to reach its terminal state (steps 0-9 ok, step 9b refused, steps 10 and 11 not run).
- On the rewrite, candidate 1 (`a38daf09b`) reached the same step pattern in 1 h 46 min. Steps 0-5 alone took 1 h 23 min, against about 22.5 h in E.

**Not all of that speedup is the rewrite.** E ran on a more loaded machine than candidate 1, and candidate 1 was niced 5. This retrospective does not split the gain between code and load.

Under the fixed comparator (#643), candidate 1 is EQUIVALENT to attempt E. The final comparison, which also covers steps 9b, 10 and 11, waits for the reference run dry-i and the r2 candidate dry-j. Both are running.

## Timeline

- **2026-11-03T03:17Z.** Attempt E (r1, dry-g, 7 workers) starts. Attempt D had died earlier at step 9 on ENOSPC after 18.5 h.
- **2026-11-04 about 00:46Z.** Wave 1 merges: #628, #629, #630, #631 and #632, the D-188 store primitive and comparator.
- **Wave 2** lands as one tested tree through #640, merge `a38daf09b`: #634-#638 (LEAF-BRACKET, LEAF-CLI, SHIP, LEAF-WW, AUTH-IO-2), the fix lanes #639 and #641 (VDL-FIX rounds 1-5) and #640 (SHIP-FIX rounds 1-3 plus CI fixes). Neither fix PR was green alone. #634 was closed as merged via #640.
- **05:31Z.** Candidate 1 starts on `a38daf09b` (dry-h, 7 workers, niced 5).
- **06:22Z.** Attempt E ends, exit 2, after 27.1 h. It finished on its own; nothing was killed. Step 9b is `unclassified_refusal`.
- **07:17Z.** Candidate 1 ends, exit 2, after 1 h 46 min, with E's step pattern.
- **Diagnosis of 9b.** A structure-only probe finds an uncaught `ClaimSideBoundRefusal` from `produce_claim_side_bound`. A code-only analysis shows the reachable states are registered not-resolvable or not-estimable outcomes. Ed rules option A. #642 (D-189, D-190) merges at `3742a0efa`, and `b5/analysis-r1-9bfix-ref` (`e7eb872d2`, never merged) carries the same fix on r1 as the equivalence reference.
- **Comparison E vs candidate 1.** The main comparator says NOT_EQUIVALENT (registered DIFFER on `closeout.json:sources`, intermediate DIFFER on `claim-verdicts.json:inputs`). A structure-only trace finds the analysis commit flowing through composite digests. #643 merges at `929fc65c9`; with its comparator the pair is EQUIVALENT (inputs, decisions, registered and intermediate MATCH; audit DIFFER). `b5/analysis-r2` is cut at `929fc65c9`.
- **08:50Z.** Reference dry-i starts at `b5/analysis-r1-9bfix-ref`: running.
- **09:16Z.** r2 candidate dry-j starts at `b5/analysis-r2`, niced 5: running.

## What went well

### Review found real defects before any real run of the new code

- Local Sol 6.1 xhigh found about 9 confirmed defects in the store, the ship code and the comparator. Several would have let a cache hit, or the comparator, pass something that was not equivalent.
- Every Sol `events.jsonl` was audited for custody paths. All were clean.
- One Sol run was cut off by OpenAI's cybersecurity content filter, a false positive. The prompt was not reworded to evade the filter; the run's partial findings were recovered from its `events.jsonl`.
- The executing review and cold passes found more:
  - a HIGH on #641: a symlink to `passage/..`;
  - a HIGH on #642: step 11 would have refused the same states (D-190 now carries them as null);
  - on #643, the question whether comparator tiers are leaf-local (the lead ruled that they are).
- Landing wave 2 as one tested tree through #640, instead of forcing two fix PRs that were each red alone, kept the merged state tested.

### Blinding held, and structure-only probes still reached a diagnosis

- E's step-9b refusal was diagnosed from the exception type and its producer only. Which code fired was deliberately not probed. A code-only reading of the reachable states was enough for Ed's ruling and for D-189 and D-190.
- The NOT_EQUIVALENT result was traced from field names only (`closeout.json:sources`, `claim-verdicts.json:inputs`) to its cause, the analysis commit in composite digests. The fix (#643) changed the comparator, not the analysis.
- Attempt E was allowed to finish. It is the reference output that candidate 1 was compared against.

## What cost time

### Harness bugs

- **Disk.** Attempt D died at step 9 on ENOSPC after 18.5 h: parallel agent test runs had filled the disk with about 110 GB of fixtures. Disk guard v2 then pruned fixtures that were still in use. Fixed in v3: it prunes only below 40 GB free and only directories idle more than 3 h.
- **Shared TMPDIR.** The test shards shared one TMPDIR.
- **No `__main__` guard.** The hand-written shard runner had no `if __name__ == '__main__'` guard. Spawn workers re-imported it and re-ran the whole shard, so shards 2 and 6 took more than 8 h and reported false errors.
- **Ledger-fill regex.** The lead's script that fills the gate ledger rewrote rows of later tables in #640's body. The body was repaired from GitHub's edit history, and the script is now bounded to the ledger table.

### Asking Ed about obviously sensible process calls

The lead asked Ed about process calls with an obvious answer. One was whether CI's pull_request run counts as gate-ledger row 2. Ed ruled that it does, and said not to ask about obviously sensible process calls. Each such question waits on Ed while the critical path stands still.

## Lessons, as rules

1. **Check free disk before and during a real run.** Parallel agent test runs must not be able to fill the volume a live run writes to. The disk guard prunes only under pressure (below 40 GB free) and only directories idle more than 3 h. It never deletes what a running job may still read.
2. **One TMPDIR per shard and per run.** Never share one between concurrent shards or runs.
3. **Every script that starts processes has an `if __name__ == '__main__'` guard.** That covers multiprocessing with spawn (the macOS default) and every hand-written runner. Compare each shard's wall time with its expected time early; a shard running hours longer than expected means a bug, not a slow test.
4. **A script that edits a PR body touches only its own section.** It anchors on the `## Gate ledger` heading and stops at the end of that table. It diffs the body before writing, and it refuses when the match is not unique.
5. **Make obviously sensible process calls yourself, record them, and tell Ed afterwards.** Ask Ed only for science rulings (such as option A for step 9b) and for what only he can do.
6. **Diagnose a refusal in a real run structure-only first:** step status, exception type, producer and field names. Then read the code for the reachable states. Do not open outcome-bearing content to find which code fired.
7. **A comparator resolves commit-derived digests to their verified referent before it compares.** Otherwise the analysis commit alone makes two equivalent runs DIFFER.
8. **Do not credit a speedup to code without a same-load pair.** Record niceness, worker count and concurrent load next to each timed run.
9. **When a content filter cuts off a review seat, do not reword the prompt to evade it.** Recover the partial findings from `events.jsonl` and carry them forward, and say in the record that the seat was cut off.
10. **Audit every local Sol `events.jsonl` for custody paths** before its findings are used.

## Still open

- Reference dry-i and r2 candidate dry-j: running. When both have finished, the final blinded comparison covers steps 9b, 10 and 11. After that comes the release run at `b5/analysis-r2`.
- Deferred to after the release: step-4 parallel exception cleanup; r1's eager firing accounting; L3 entries on temporary bracket copies; bracket bypass snapshot hardening; G9 using `is_sidecar_name`; registering the step-11 refusal codes (`sensitivity_*`, `disclosure_*`); a D-178 successor with explicit non-issuable rows.
