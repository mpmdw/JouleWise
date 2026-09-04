# Magistrate disposition of the round-2 delta re-audit (file 26), 2026-09-02

luna 263 (xhigh, read-only, detached at `629a333e` = Sol 262 landing +
bench corrections `9c1dc717` + custody): 0 blockers, 0 should-fix, 0 nits.
Every named counterfactual re-executed by the seat matches the bench run in
file 25 (R2-A `'exact' != 'refused'`; R2-B unauthenticated label
`unexpectedly found`; R2-C `FAILED (failures=2)`), plus the seat's own
control-of-the-control (re-stamped digest replaced by `"0" * 64` trips the
CONTROL assertion — proving the control decides on the tree comparison and
nothing upstream) and a `pack_roots`-for-`pack_hashes` mutant, KILLED. All
five round-1/1b regressions still bite (A5). R2-D: the guard at
`identity_pins.py:1701` sits inside `if suite_declaration is not None`
(:1676); with no suite declaration the helper is not called; `F-G:
REACHABLE` does not exist — the file 22 §Q3 ruling stands. B1: all eight
dictated steps PROVEN with the line each rests on; the bench gloss of the
committed-tree digest verified against `arm_readiness.py:2833–2873`; the
Opus P5 lineage chain (`_pack_record()` → consumption/lifecycle receipts →
`arm_readiness.py:10369`; `bundle.py:123–147` authenticated-only,
caller-supplied lineage rejected at `:1056–1062`) verified once, as file 22
owed. B2: the magistrate's value/filename rule confirmed row by row; the
seat's own 30-row first-use table finds no gap. B3: a cold reader recovers
both labels and the reason from the text alone.

| Item | Disposition |
| --- | --- |
| Same-signature statement (C) | NO on both classes (F-B closure-without-biting-test; F-N/F2 prose). Fix round 2 on F-B CLOSES under rule 11 — the standing escalation signature did not fire. |
| Residual: `resolve(strict=True)` removal SURVIVES the forged-pack fixture | ACCEPTED as residual, NO CHANGE. It is missing-root coverage (step (2)'s `strict=True` on a root that does not exist), a different class from F-B; the forged pack exists by construction. A missing-root refusal test is a first-round item for the post-merge kernel batch, not a blocker on this branch. |
| A2 note: the unmocked test does not repeat the mocked sibling's outside-subset refusal and no-recompute assertions | ACCEPTED, NO CHANGE — the brief asked for the route assertions; the outside-subset refusal is covered by the round-1b label test on the real gate (A5 KILLED). |

Gate consequence: `9c1dc717` is the reviewed code head of this branch. What
remains before merge is the operation-loop §5 ledger: Opus counter-review of
the near-final head (row 6), integration replay on main after PRs #276/#274
land (row 9), CI, terminal review. After merge: the live P-8 runbook re-run
that freezes all three _v5 packs (the D-169 unattended-loop peer session
holds the night window; the merge is announced to it first).
