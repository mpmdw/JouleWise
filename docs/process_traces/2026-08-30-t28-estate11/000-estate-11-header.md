# Estate 11 — S-0 clone-proof re-run at the reviewed head (D-157 W-10 -> estate 11)

Operator: estate-11 director (Opus 5), 2026-08-30.
Estate root: /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/estate11
Main repo: /Users/edr/code/JouleWise  (READ-ONLY; never written by this estate)

BASE          = 7294cb8fe04b728263919e4ac668194e0db2df9a  (local main == local origin/main)
CI_RUN_ID     = 33326533519  (workflow "ci", conclusion=success, headSha=7294cb8f..., 2026-08-30T17:54:00Z)
MEASURE_PY    = /Users/edr/code/JouleWise/.venv/bin/python

Note: github.com origin/main has advanced past the local checkout (newest green head
0438566b at 19:24Z). Per the director's instruction the estate clones LOCAL main, so
BASE is the local head 7294cb8f, whose own CI run is green and conclusion-verified.

Procedure = docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md
  + delta   docs/process_traces/2026-08-27-t26/d139-families/01-estate-11-delta.md
  + S11     docs/process_traces/2026-08-27-t26/s11-collector-manifest-id/estate11-assertions.md

## AMENDMENT (2026-08-30 ~20:00Z): BASE re-selected, first cut abandoned

The first cut used BASE=7294cb8f, the local main head at the time. The anchor
re-derivation (030-anchor-derivation.json) resolved only 14 of the delta's 16
anchors: `_admit_bound_analysis_manifest` was ABSENT from every source file, and
`tests/test_mint_analysis_admission.py` did not exist.

Cause, established before classifying: PR #209 merged at 2026-08-30T18:15:05Z as
commit 4ea105b0, i.e. AFTER 7294cb8f (17:53:57Z). The local checkout was ~20
minutes stale. This is BASE staleness, NOT an instrument defect — recorded here
because "the ruled predicate is not in the code" is exactly the shape of a real
halt, and the estate must show why this one is not.

The main repo independently advanced to 2a3c59af while the estate was running
(another session is landing commits). 2a3c59af's CI was still `queued`, so it is
not an admissible BASE.

RE-SELECTED BASE = 0438566b43e8848b8712b63270bbf857e5b76013
  - newest main head with a completed/success CI run (run 33330773736, 19:24:17Z)
  - contains PR #209 (merge 4ea105b0) and PR #228 (merged 2026-08-29)
  - only commit between it and #209 is #242, a paper-docs commit
CI_RUN_ID = 33330773736

Cut 1 estate (BASE 7294cb8f) is retained at s0-clone-proof-r4/ as the evidence
for this finding and is NOT continued. Cut 2 runs under e11-2/.
