# 44 — A291 checker fix round 1: delta re-audit (Opus contract lens)

Activation a65fb4fa. Lens seat: Opus 5.5. This file re-audits commit `b8fae7b3` (branch
`fix/2026-09-24-a291-checker-r1`, seat report 43) against my own lens 37. Everything was run in an archive copy at
`/tmp/a291d` (`git archive b8fae7b3 | tar -x`); the seat worktree was not touched. The delta against `b8962fd0` is
`tests/scored_roster_checker.py` (+19/−15, confined to `_derived` and `check_executed`) and the test module
(+145). Baseline: `python3 -B -m unittest tests.test_scored_roster_checker` gives `Ran 22 tests ... OK`.

**Verdict: B1, B2 and M1 are FIXED, and all eight earlier survivors are killed. The fix introduces no new defect.
It adds four new test-strength survivors, in which the checker's code is right but no test pins it. One more
survivor is reasoned but not executed (listed under §3).**

The four executed survivors:
- **N7:** a terminal item stops the executed-position loop;
- **N9:** the executed null rule is read from the positions;
- **N10:** the executed spread counts positioned parents instead of fully counted ones;
- **N3:** the planned shortfall counts positioned parents instead of non-terminal ones.

Two further survivors (N4, N11) cannot be told apart from the correct code on any roster that obeys INV-24. The
same holds for N12, the executed five-envelope clause, which survived as well.

## 1. Findings from lens 37

| Item | Status | Executed evidence |
|---|---|---|
| **B1** planned position of partly-terminal parents | **FIXED** | 37's `w1.py` re-run: the checker's L1 lever on R2 is `6.199999999999999`, equal to the independent RD-4 + FT-10 computation. `check_roster` on the independently rebuilt R2 roster gives `[]` (it was `INV-27`, `INV-38`). |
| **B2** `check_executed` reads the first, voided placement | **FIXED** | `w2.py`: `spread_exceeded big:1 = False`, and the lever is `5.199999999999999` both with and without the voided key `('big:on:1:0', 0)`. It was `True`/`4.5`, and `5.0` with the voided key. |
| **M1** executed lever for partly-counted parents | **FIXED** | `w3.py`: the checker gives `5.4`, equal to the literal 45/10 value (it was `4.5`). |

What changed:
- **Selecting the live placement.** Both `_derived` and `check_executed` now key it as `p['block_id'] in
  envelopes[p['envelope_index']]['blocks']`, which is exactly FT-11's per-placement "live".
- **Planned side.** A parent is positioned when any item is live and non-terminal (RD-4 / 02b). The null rule and
  the shortfall count now use the non-terminal parent count (FT-10, FT-7).
- **Executed side.** A parent is positioned when any window is counted. The null rule and spread use the count of
  fully counted parents (45/10 §Q4, FT-10, 31 X-5).

## 2. Mutation re-run (my harness, adapted to the new anchors: `/tmp/a291d/mut2.py`)

**The eight earlier survivors, all killed:**

| Mutation | Killed by |
|---|---|
| M1 (INV-35a) | `test_INV_35a_reschedule_without_culprit_code` |
| M2 (INV-35c) | `test_INV_35c_excess_reschedules_code` |
| M7 (no `whole_block` exclusion) | `test_eligibility_excludes_whole_block_and_same_cell_parent` |
| M8 (no M8-by-parent) | same test |
| M9 (`>=`) | `test_culprit_strict_elapsed_boundary` |
| M10 (no envelope clause) | `test_planned_shortfall_requires_five_distinct_envelopes`, `test_root_mutation_rows` |
| M16 (null → `0.0`) | `test_planned_lever_null_with_zero_nonterminal_parents` |
| M17 (INV-05 descendant clause) | `test_registered_descendant_requires_claim_ready` |

**Earlier kills, still killed:** M3, M4, M5, M6, M11, M12, M13, M14, M18.

**New mutations aimed at the fix:**

| # | Mutation | Result |
|---|---|---|
| N1 | planned: revert B1 (fully live parents only) | killed (R2 test) |
| N2 | planned null rule read from positions (`a and b`) | killed (null test) |
| N5 | planned live = first placement anywhere | killed (INV-31, event rows, partly-counted test) |
| N6 | executed live = first placement (revert B2) | killed (both live-attempt tests) |
| N8 | executed: an uncaptured item stops the loop (revert M1) | killed (partly-counted test) |
| **N7** | executed: a terminal item stops the loop (revert M1 for terminal items) | **SURVIVED** |
| **N9** | executed null rule read from positions | **SURVIVED** |
| **N10** | executed spread counts positioned parents, not fully counted ones | **SURVIVED** |
| **N3** | planned shortfall counts positioned parents, not non-terminal ones | **SURVIVED** |
| N4 / N11 / N12 | planned or executed `occupied` includes partial parents; executed spread without the envelope clause | survived; equivalent on legal rosters (below) |

**N7 and N9 change results on legal rosters** (executed in `/tmp/a291d/n9.py`, on R2 with every loaded envelope
reported):
- **N9.** Capture the live keys but none of the unsplit `big:on:1:*` parents. The only big L1 position then comes
  from the partly-terminal parent 0. The checker gives lever `None`, as FT-10 requires; N9 would give a number.
- **N7.** Capture every live key. The checker gives lever `6.199999999999999`, which counts the partly-terminal
  parent. N7 would drop that parent and give `4.5`, the pre-fix value.

**N10 and N3 are reasoned only.** They differ from the correct code when a cell has four fully counted
(respectively non-terminal) parents, one partial parent, and at least five distinct envelopes. That happens, for
example, when one of the four is a split parent whose singles sit in two envelopes. No current fixture has two split
parents in one cell, so I did not execute this.

**N4, N11 and N12 are equivalent on legal rosters.** Distinct parents of one cell never share an envelope at any
stage (M8-by-parent, INV-24). So five fully counted, or non-terminal, parents always occupy at least five distinct
envelopes. The envelope clause can therefore only bind on a roster that already violates INV-24. M10's kill uses a
direct `_derived` call on exactly such an illegal roster. This is not a defect, but the magistrate should know the
five-envelope clause is redundant under INV-24.

Recommended pins, all non-blocking:
1. Add an executed assertion on R2 fully reported: L1 lever `6.199999999999999` with every live key captured (N7),
   and `None` with the unsplit big L1 keys dropped (N9).
2. Add a two-split-parent fixture for N10 and N3.

## 3. New misjudgements: hunted, none found

- **Split between planned and executed levers.** The planned side positions any parent with a live non-terminal
  item and nulls on zero non-terminal parents. The executed side positions any parent with a counted window and
  nulls on zero fully counted parents. Each follows its own ruled text (RD-4 + FT-10; 45/10 §Q4 + FT-10 + 31 X-5).
  Neither leaks into the other: the null tests and w1/w3 separate them.
- **Live placement after chains of reschedules.** I ran a differential fuzz (`/tmp/a291d/fuzz.py`) against an
  independent executed computation written from 02d §4.1:
  - 5 legal rosters, every loaded envelope reported and accepted by `check_roster`;
  - one of them is R2, with reschedule chains up to attempt 6 and a partly-terminal parent;
  - 1,500 random capture sets, mixing subsets of the live keys with random voided keys;
  - result: **0 mismatches** in `spread_exceeded` or the executed lever.
- **Spread counting.** Planned spread counts non-terminal parents and executed spread counts fully counted parents.
  Envelopes are taken from those parents only. Both match FT-7 and 45/10 §Q4.
- **The fix's fixtures.** In `test_executed_single_advance_uses_retry_attempt`, the fixture sets `late=False` by
  hand after `report_keep`. That is correct under FT-1: the single's latest observation is now an on-time
  completion. `report_keep` simply does not update `late`.
- **The null-rule unit test.** `test_planned_lever_null_with_zero_nonterminal_parents` injects two-key
  `terminal_refusals` into a direct `_derived` call. This is acceptable for a unit pin; it never reaches
  `check_roster`.

## 4. Same-signature statement

The class is "oracle arithmetic misreads a derived quantity". **It does not repeat in the delta.** Every derived
quantity the fix touched now matches its ruled text, backed by executed evidence (w1–w3, the fuzz, and the
N-series).

I re-checked the derived quantities the fix did not touch against 02d §1.2 and X-4, and each matches:
- `worst` (operation order);
- `cap`;
- `max_gap` (with `ceil` for blocks per cell);
- whole-block Σ worst;
- parent `predicted_s`;
- the root position (`sum` / `count`).

One residual risk carries the same signature. The fixture helper `refresh_derived` still re-implements `_derived`
line for line. A future misreading would again pass both unless an independent literal pins it. Two such pins exist
today: R2's `6.2` and the `5.4` / `5.2` executed literals.

Recommendation: keep the pins in §2, or replace `refresh_derived` in the fixtures with hand-computed literals. No
second fix round is needed on B1, B2 or M1, so the standing escalation trigger does not fire.
