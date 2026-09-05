# Peer audits (gpt-6-astra, three independent seats) — magistrate bench verification

Date: 2026-09-04. Audited head: cc56a9a7 (main at dispatch). Verified on canonical main f4c812b4.

Ed's charge: treat astra as a peer equal in judgement; fresh eyes on the whole base. Three seats, three
independent worktrees, xhigh effort, read-only apart from their report: 01 full-base system audit,
02 claim-spine physics/evidence audit, 03 paper-vs-code audit (draft-v2 skeleton against code).

## Executable witnesses reproduced at the bench (magistrate ran them, this session)

| Witness | Audit | Bench result on f4c812b4 |
|---|---|---|
| P1 interval-allocation: ten 100 ms records at 10 W, window [0.55, 1.45] s | 02-F1 (also 01-F1, 03-F1) | point 9.000 J, interpolation bound 0.000 J, envelope [8.800, 9.200] J; same record totals admit [8, 10] J |
| P1 two-gate arithmetic: estimate 6, floor 5, deterministic bound 4 | 02-F10 | outcome direction_supported, claim_ready True although 6 < 5 + 4 |
| P2 D-165 shared energy sign vs shared time shift | 02-F2 (also 03-F7) | common-time-shift ratio 2.250368; issued shared-sign ratio 1.500000, passes False |
| P3 renderer on tracked synthetic fixture | 02-F3 (also 03-F5) | exit 0; no synthetic/fixture label; old model names present; "operative floor is published" |
| Legacy L1 capstone page | 01-F3 | scripts/build_capstone.py:34 LEGACY_LABEL still owns the page; generated page calls idle-subtracted energy primary |

All four executable witnesses reproduce exactly as reported. None is a live-bundle result; each is a
counterexample to an interpretation the paper currently makes.

## Convergence across the three independent seats

- Estimand: all three say the timing envelope covers the interval-overlap ALLOCATION of counter energy,
  conditional on the held-average reconstruction, not physical phase energy. Cheapest credible remedy
  in all three: name the estimand and show the nonnegative partial-record enclosure as a diagnostic.
- Transfer: pulse-to-inference transfer is untested and the abstract's TR-01 sentence depends on it.
- D-165 common mode: shared ENERGY sign is not a shared TIME shift; "absolute cancellation" is wrong physics.
- Floor/contrast prompt mismatch (03-F3): floor packs use prompt 0 only, contrast cycles eight prompts.
  This is pre-collection and therefore still curable by regeneration.
- Publication path: legacy L1 voided numbers still build (01-F3); renderer does not enforce issued sources (02-F3).
- Scope: freeze to paper-named work; every open lane must name the figure, table or refusal it enables.

## Disposition

Physics findings go to the standing three-seat consult (Sol xhigh, Opus, blind Fable) — questions in 05.
The legacy-L1 cure needs no ruling (voided evidence rendering as results is a D-161 evidence fence): seat launched.
Estimand and D-165 relabelling are claim-bearing rulings: cold Fable gate before ratification.
