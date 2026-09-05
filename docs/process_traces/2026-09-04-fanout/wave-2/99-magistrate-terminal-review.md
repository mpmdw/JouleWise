# Fan-out waves 1 + 2 — magistrate terminal review (apex read)

Date: 2026-09-04. Merge candidate: `int/2026-09-04-fan-wave-2` at the head named in the PR ledger row 12 = origin/main + wave 1 (12 landings) + wave 2 (19 landings + doc008) + five seam-fix rounds + magistrate bench cures.

## What I read (primary artifacts)
The two Opus counter-reviews (wave-1/02, wave-2/06) in full and every finding's disposition; the five Sol contract rounds (wave-2/01, 02, 03, 05, 09) and the wave-1 rounds; the replay diagnosis (wave-2/07) and all three replay logs' failure clusters; the seam-fix reports (wave-2/04, 08, 10); every per-mission refuter/delta verdict in the tabulations recorded in the durable state; the rulings I wrote in `01-magistrate-rulings.md` (D-161 re-scopes, the wave-2 integration table, the frozen-file restorations). At the bench I restored two frozen files myself (the v1 analysis-manifest validator and the frozen draft-v1) and cured W8 and the phase-share queue row; I read those diffs directly. I did not read all 268 changed files line by line: the per-landing execution refuters, the contract rounds, and the Opus counter-reviews carried that coverage, and this review answers the design-level questions from their executed evidence.

## Design-level answers (row 7)
1. **Claim spine untouched.** `joulewise/reduce.py` is byte-identical to main (D-138 pin, verified by Opus and by digest at the bench); the frozen v1 validator and the frozen v1 draft are byte-identical to main after restoration; the three `_v5` generators show `PARITY_OK generators=3 files=352`; the pre-registered `p2_015_floors` generator regenerates all 282 configs byte-identically. Nothing claim-bearing changed on main through this wave.
2. **D-161 applied as a threat-model discipline, not a shortcut.** Five missions that kept failing on guard-evasion signatures were re-scoped or retired under D-161; the evidence fences they touched (NEG-8 ingress authentication, the CUSTODY hardening's provenance checks, the COLDGATE-HANDOFF operational fence) were kept fail-closed and one narrowing that refused a self-asserted fixture was confirmed correct rather than reverted.
3. **What the wave taught the process.** (a) Refuters must diff against the merge base, never a moving main; (b) a fan of 32 landings needs the estate-wide guards (git-fixture hygiene, docs freshness) re-run after every fold-in, which is why five seam rounds were needed; (c) generated projections and hand-authored tables must not be edited by seats (magistrate-owned state docs stayed out of every WRITE_SCOPE).

## Overbuild / merge-ability (row 8)
Removed in-wave: the aud-wo-rows bridge gate (no D-060 decision), the GENERATOR-CORE anti-bypass machinery beyond a maintainability seam, the PROJECT_STATUS invented count, the EPOCH-LINT fail-closed design (retired). Parked: AUTHENTICATOR-ALLOWLIST-GUARD-01, LINEAGE-RELOCATABLE-01 (cold gate), skill-distill (doctrine).

## Integration replay (row 9)
Full unpiped suite on the final head, log `~/.claude/jobs/3c46c831/tmp/int-fan-wave2-replay-3.log`; exact tail appended below when it completes. The prior replays (5111/5112 tests) reduced to the explained set: the pre-existing localhost worker test and a load-sensitive real-clock anchor test.
