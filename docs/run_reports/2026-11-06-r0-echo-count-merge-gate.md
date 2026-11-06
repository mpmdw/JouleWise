# PR #687 merge gate: R0 echo prompt states its call total

Magistrate activation 78981c26, 2026-11-06.

- Executing review (Sol 6.1 high): `docs/align/reviews/2026-11-06-r0-echo-count-executing-review.md`. ADMIT, no findings.
- Cold pass (Fable 5.1, fresh worktree): `docs/align/reviews/2026-11-06-r0-echo-count-fable-cold-pass.md`. ADMIT_WITH_FIXES; its live seed-95 probe on D gave 12 transitions, 0 rewritten tokens.

| Finding | Disposition |
|---|---|
| Fable M1: the `+ 4` reason supports any spare of at least 1, not 4 | Fixed. The comment now says the size 4 is not derived, gives the purpose (keep the measured turns away from the announced last call), and names 16 as the value verified live. No number changed. |
| Fable L1: the inconclusive reason hardcodes "12" | Fixed. It is an f-string on `ECHO_TRANSITIONS`. |
| Fable L2: `generated` does not record its prompt | Fixed. The result carries `"prompt": ECHO_PROMPT`. |
| Sol E4: the fixture orphan census could not run `ps` in the sandbox | Rejected as not applicable: the PR creates no fixtures. |

After the fixes, tests.align.test_r0_checks (30), test_r0_progress (3), test_r0_integration (3) and test_r0_scheduling (12) all pass. No delta re-audit: the fixes are a comment, a message string and an added report key, none of them number-bearing.
