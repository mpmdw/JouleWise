**Verdict: HOLD.** Committed locally as `3d1e39f80` on `align/2026-11-08-release-tools-sol2`. Working tree clean; nothing pushed.

Seven findings include:

- Both builds retain obsolete reserve counting; the engine rejects C9 and hardcodes U3 N=16.
- Missing H* blocks or grid doses still AGREE.
- Producer identity and journal digest checks have gaps.
- Malformed exports exit 1 without a verdict.
- The runbook names an obsolete commit.
- U5 sign and unit mappings cause false HOLDs.

Changed only the [report](/Volumes/JW-EXT/jw-wt/sol-release-tools-sol2/docs/analysis/v4/RELEASE-REVIEW-sol2.md) and [witness module](/Volumes/JW-EXT/jw-wt/sol-release-tools-sol2/tests/v4_release/test_review_sol2.py).

Verification: 18 comparator tests and 13 release tests passed. Final witnesses: 2 positive controls passed; 12 expected failures reproduced defects. Commands and witness limitations are recorded in the report.

Synthetic only; no real custody, network, full suite, or model downloads. Next: lead adjudicates the frozen-engine changes, fixes the findings, and repeats the rehearsal.