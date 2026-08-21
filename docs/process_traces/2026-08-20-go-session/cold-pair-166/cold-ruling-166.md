# COLD GATE RULING — PR #166 merge question (cold Fable instance, 2026-08-20 ~23:15 PDT)

Packet: cold-packet-166.md (same directory). Opus contract-lens refuter ran in
parallel; lead synthesis recorded separately. Verbatim ruling below.

## Part I — Per-claim verification

Claim 1 (canonical run 1 at a8f1549): CONFIRMED. Both FAILs are subTests of
PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes.
ADDITIONAL FACT THE PACKET OMITS: the N-5 fix 46d710f IS an ancestor of
a8f1549 (git merge-base --is-ancestor) — run 1's N-5 failure is a POST-FIX
recurrence, albeit on a loaded machine.

Claim 2 (quiet run 2): CONFIRMED. errors=1:
SamplerLifecycleHardeningTests.test_detached_grandchild_is_reported_by_post_teardown_census,
ValueError int('') at tests/test_calibration_exits.py:2207 — guarded only by
an exists() poll; race is file-created-but-not-yet-written. No N-5 FAIL.

Claim 3 (CI): CONFIRMED with two minor discrepancies. Identical failure on
both CI attempts (AssertionError 2 != 39, RACE_EXERCISED=0); 3.14 passed both.
Main green at 5bd7acf/b9e197a; all 10 subsequent main runs failed; first red
0f5ade6 = a single 21-file docs/custody commit, zero code; job-level check of
5 runs shows calibration-exits-exclusive (3.11) as the ONLY failed job.
#163/#164/#165 merge runs all red on this job with no recorded disposition.
Discrepancy A: packet's times are UTC mislabeled PDT. Discrepancy B: CI
attempts ~45 min apart, not ~15. Neither affects any ruling.

Claim 4 (flake history): CONFIRMED; additionally RUN_STATE lines 773/965
record a prior FLAKE-CALEXITS-311-REDERIVE row — a FOURTH historical
mechanism the packet undersells.

Claim 5 (run 58 in flight): not independently verifiable from the custodied
ledger (50 rows at checkpoint); R4 conditions on its RETURN, not existence.

PR facts: CONFIRMED. #166 = docs/paper/draft-v1.md only (223+/89-).
#167 = code diff; its ci.yml change does not touch the calexits shard.

## Part II — Rulings

### R1 — #166 MAY MERGE before the calexits class is fixed, on the severance
basis, under four conditions (all executable):
1. Register first, merge second: the R2 rows must exist in the
   kernel/TASK_QUEUE before the merge is executed.
2. Recorded basis: the merge record must cite this cold ruling and state:
   merged over red under docs-only severance; the three failures named; all
   pre-existing on main; git diff main...HEAD --name-only =
   docs/paper/draft-v1.md only.
3. Precedent fence (decision-log entry): severance applies only when the
   three-dot diff touches exclusively documentation files — no .py, no
   configs/, no .github/, no scripts/, no test paths — verified mechanically
   by --name-only at the actual merge head. Does NOT generalize to code
   diffs of any size, including one-liners.
4. No health inference: the merge must not be recorded anywhere as evidence
   the calexits module or the CI gate is healthy.

### R2 — Separate rows per mechanism + one reclassification + one umbrella:
1. CALEXITS-CLEANUP-RACE-CI311 — BLOCKER (hosted 3.11 shard uninformative on
   every run; gates all code PRs). Until fixed, RUN_STATE must carry an
   explicit known-red/non-informative line; merge decisions rest on local
   canonical evidence — recorded, never silently ignored.
2. CALEXITS-CENSUS-PIDRACE (int('') at :2207) — HIGH (can void a canonical
   gate run). Fix shape visible (poll for non-empty content, not existence);
   goes through the normal gauntlet.
3. N-5 reclassification (amend, not new): 46d710f is in the tested head and
   the test still failed under concurrent load; the "resolved, cause
   probable" record must be amended to state the post-fix recurrence and its
   environment, leaving open incomplete-fix vs environment-induced. May not
   continue to read "resolved" unqualified.
4. CALEXITS-TIMING-HYGIENE — umbrella module-wide timing/synchronization
   audit row, should-fix, low priority, not gating. (Five mechanisms
   historically: #121, REDERIVE, N-5, tonight's two.)

### R3 — #163-#165: no re-verification; a recorded deviation note is
REQUIRED: names the three PRs, states the shard was red on their checks with
no disposition recorded at merge time, names the local canonical gates as
compensating evidence, cites this ruling, and states the corrective
convention: ANY merge over ANY red required check requires an explicit
recorded disposition at merge time. No rollback.

### R4 — #167: code diff, no severance. Prefer waiting for a full
unquarantined quiet-machine canonical green at its head (default).
Quarantine-and-isolate acceptable ONLY as a pre-registered fallback:
quarantine list fixed BEFORE the run, limited to exactly the three R2 test
IDs; suite green outside the set; quarantined tests then pass in isolation
at the same head; in-suite outcome recorded alongside, never replaced; any
failure outside the set or with a different signature STOPS the merge
(rule-11 escalation). Merge record lists row IDs + pre-registration pointer;
first code PR after the calexits fixes gates on a fully unquarantined green.

Prominent note: no load-bearing packet claim failed verification; the one
material absent fact (N-5 fix in tested head) is bound into R2.3.
