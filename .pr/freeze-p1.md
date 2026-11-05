Tier: full

Impact statement:
(i) Raw-bundle byte or recorded timestamp: No — only Git identity and pin-location machinery changes.
(ii) Reduced energy, time, token count or correctness score: No — no reducer, estimator or result arithmetic changes.
(iii) Admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items: Yes — custody requires the exact registered analysis commit instead of origin/main containment.
(iv) Unit or uncertainty: No — all scientific constants and uncertainty logic retain their existing bytes.
(v) Registration, prospective manifest, analysis plan or estimator constant: Yes — adds post-release commit/tree identity metadata; sealed registrations and analysis plans retain their bytes.
(vi) Published number or sentence in the paper, README claims or claim renderers: No — no publication, fill or claim computation changes.

## Gate ledger

| # | Gate | Evidence |
| --- | --- | --- |
| 1 | Independent review by a non-author, with an executing lens | NOT-RUN |
| 2 | Whole suite on the merged tree | NOT-RUN |
| 3 | CI green on the final head | NOT-RUN |
| 4 | Cold final pass on calibration/claim/custody admission code | NOT-RUN |
| 5 | Findings dispositioned | RUN docs/run_reports/2026-11-05-freeze-by-commit-p1.md |

This is the offline body for PR #649 on
`lane/2026-11-05-freeze-by-commit-p1`. Implementation commit `2e0528ad8` and
fix-round commits are local; no network or push occurs in this session.
**Land only after the block-5 release.** The full suite is prohibited while
the seven-worker analysis job runs; final-head CI and the lead's remaining
gates remain open.

## Summary

A346 Phase 1 removes main's bytes from the block-5 freeze contract. The local
registration binds the annotated collection, original analysis and r2 tags
to full commit/tree IDs. Freeze tests read those Git objects. Custody retains
the clean-tree gate and accepts only the exact registered analysis commit.
Strict F3 replaces the descendant ledger: any ruled fix requires a new
reviewed `b5/analysis-r<k>` tag and registration; runtime authority overrides
refuse.

**Operational requirement:** post-release `build_results_fill_input.py`,
`issue_reported_energy.py`, `produce_b5_disclosures.py`,
`compare_b5_recompute.py`, and `open_paper_input` runs must use a clean
`b5/analysis-r2` checkout. After landing, main refuses for all five custody
families (`analysis_descendant_unruled`). TODO A346 selects registration by
block or role before enabling other blocks. `require_origin_main=True` is
honored separately; custody explicitly requests the registered-analysis gate.

335 Python-test pin locations across 77 holder files become digest locations.
Every existing target, family, multiplicity and summary count is preserved;
JSON field pointers and historical document locations retain their meaning.
Regressions cover tag tampering, offline identity, unruled/intermediate/merged
commits, dirty checkout refusal, worktree independence, line motion and repin.
The joined synthetic harness supplies a real annotated fixture tag to the
new predicate; the pipeline itself is not run in this session.

## Calibration dependency

The combined D-138 reissue carrying A178 and L9-ENV-2 is absent from the
inspected repository authorities. F4 is therefore an explicit unissued stub:
`STUB_REISSUE_REQUIRED`, null acceptance, and an always-refusing callable.
Existing acceptance and estimator bytes, including the live-byte staleness
invariant, are unchanged. The D-138 owner must issue and wire the commit-scoped
acceptance with the joint clamp × coverage-ULP refuter before activation.
This draft does not claim full A346 completion. Phase 2, mirror removal and
block-6/BYTES addenda are outside this brief.

## Rebind evidence

- Authority and exact before/after digests for every changed existing frozen
  source/test/pin file: `docs/process/freeze_p1_rebind.md`.
- Tag identities: `configs/analysis/b5/freeze_commits.json`; release remains
  `b5/analysis-r2 = 929fc65c9ce3ff82f0311d28acf76a682edd466f`, tree
  `9e89d7ff48999416467129c03ea171fc3a1f3f83`.
- The tag trees are immutable Git objects; no tag ref was changed. Real-data
  equivalence or locked-environment reproduction is not established here.
- Full implementation, limitations and verification tails:
  `docs/run_reports/2026-11-05-freeze-by-commit-p1.md`.

## Verification

The requested pytest command could not start: neither installed Python 3.14 nor
3.13 has pytest. No install or network was attempted. Serial, targeted stdlib
unittest is the documented fallback; the report lists exact commands/results.
Broad `RealTreeTests` and a whole-tree digest census are excluded because their
traversal can read evidence forbidden by the user's blinding rules. Local checks
are supplementary and do not fill gate-ledger row 2.

Local evidence (full commands and tails in the report):

| Evidence | Result |
| --- | --- |
| Git identity/tampering/descendant/custody tests | 10 passed |
| Registered-tree freeze/worktree independence tests | 4 passed |
| Digest census/content-location tests | 23 passed |
| Synthetic repin and historical-era checks (six classes) | 44 passed |
| Registry migration | 335 locations / 77 holders; all targets, counts and literal values preserved |
| Syntax, generated-state drift and diff whitespace | Passed |
| Fixture census | Unavailable: ps denied (exit 2); no clean-census claim |

81 targeted tests passed using stdlib unittest. About 167 seconds of test time
including the earlier targeted reruns; serial execution throughout. This does not replace
the unrun whole-suite, final-head CI, independent review, cold pass or reproduction
gates. No measurement inputs or restricted paths were opened.

## Original implementation plan (moved from PLAN.md)

# A346 FREEZE-BY-COMMIT-01 — Phase 1

Prepare for landing immediately after block-5 release; no Phase 2 pruning.
Authority: docs/process/freeze_by_commit.md F1–F4/F7, RUN_STATE items
145–146, D-138, and the 2026-11-05 user brief.

1. Register immutable collection, original analysis, and analysis-r2 commit/tree
   identities, and verify annotated tags against those identities using Git blobs.
   Freeze tests must inspect those trees rather than constrain current main.
2. Replace the step-5 origin/main requirement with exact registered analysis
   identity or a fully ruled descendant chain, while retaining clean-tree checks.
3. Add a fail-closed commit-scoped calibration seam. If the combined D-138
   reissue (A178 × L9-ENV-2) is absent, leave legacy acceptance unchanged and
   explicitly stage the missing dependency; do not issue scientific acceptance.
4. Retire line-number test pins without weakening remaining non-test pins.
5. Cite rebinds for every changed frozen file; run only inspected synthetic,
   targeted pytest files, serially, with no network or real-data access.
6. Update the kernel/generated views and dated report; move this plan into
   .pr/freeze-p1.md, with a truthful gate ledger and all unrun release gates.

Safety: never access restricted directories or paths outside this clone under
/Users/edr; never invoke run_b5_analysis.py or a real-data reader. No full suite.

Workspace blocker: requested branch creation failed because .git is read-only
under the session policy. No branch or commit success is claimed.
