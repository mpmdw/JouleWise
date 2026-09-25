# 37 — A291 independent checker: Opus contract lens (read-only)

Activation a65fb4fa. Lens seat: Opus 5.5, contract lens. Under review: `tests/scored_roster_checker.py` and
`tests/test_scored_roster_checker.py` at commit `b8962fd0` (seat report 32). Contract: 02d + 31, with FT-1..FT-14
(21/§3) and ruling 10 winning on conflict. Everything below was run in an archive copy at `/tmp/a291lens`
(`git archive b8962fd0 | tar -x`). The seat worktree was not touched. Baseline: `python3 -B -m unittest
tests.test_scored_roster_checker` gives `Ran 12 tests ... OK`.

Verdict: **NOT READY AS AN ORACLE. 2 BLOCKERS, 1 MATERIAL, 8 test-strength survivors, 3 NITs.** Both blockers
make the checker reject a correct packer on rosters the stress run (§6) will produce often. The replay core is
otherwise faithful: decisions, `late`, stage and attempt handling, FT-3 order, Q9 eligibility, split, the terminal
append order and the digest chain all match 02d. I found no other disagreement after hunting in each of these areas.

---

## 1. Defects

### B1 — BLOCKER: the planned position drops partly-terminal parents (INV-27, and INV-38 through the digest chain)

The contract text:
- RD-4 (02d §3.4): «The PLANNED position of a parent at a `requeue_overrun` exit is the item-weighted mean of the
  envelope indices of the live (not voided, not terminal) placements holding its items, as 02b proposed. A parent
  with no live placement has no planned position and is excluded.»
- 02b's definition, to which RD-4 points: «the item-weighted mean of the envelope indices of the live placements
  holding its non-terminal items. It exists only while some item is non-terminal.»
- FT-10 overrides this in one case only: when a model has ZERO non-terminal parents at a level, the lever is null.

So a split parent with one single terminal and its siblings live still HAS a planned position: the mean of its live
singles' indices. It enters the per-model mean.

The checker instead, in `_derived`, appends a position only when `len(indices) == len(b['items'])`. That keeps
fully non-terminal parents only, which is the FT-7 shortfall population, applied to the lever as well. The test
fixture's `refresh_derived` copies this same misreading. The oracle and its fixtures therefore share one failure
mode, and the R2 test locks it in.

Executed witness (`/tmp/a291lens/w1.py`):
1. Take R2's four-envelope roster, in which singles 0 and 1 of `big:on:1:0` end in `ceiling_violation` and singles
   2 and 3 stay live.
2. Rebuild it with the derived fields computed per RD-4 plus FT-10: a parent is positioned if it has any live item,
   and the lever is null only when a model has zero non-terminal parents.

```
checker-reading lever L1: 4.5  RD-4 lever L1: 6.199999999999999
checker verdict on RD-4 roster: [('INV-27', 'inv_27'), ('INV-38', 'inv_38')]
```

A correct packer is rejected on every roster where any cell holds a partly-terminal parent. That happens whenever one
single of a split parent reaches `ceiling_violation` or `unattributed_overrun` while its siblings live. Random legal
observations produce this routinely.

Fix:
- In `_derived`, position every parent with `indices` non-empty.
- Count non-terminal parents separately; they feed FT-7's shortfall and FT-10's null rule. The lever is null iff
  either model has zero non-terminal parents.
- Mirror the change in `refresh_derived`.
- Add a witness that asserts R2's L1 lever equals `6.199999999999999`.

### B2 — BLOCKER: `check_executed` reads a block's FIRST placement, not its live one (INV-26, INV-45)

In `check_executed`, `live` is keyed `(block_id, attempt)` over every placement whose `block_id` sits in ANY
envelope's `blocks`. That set includes the block's voided earlier attempts. The lookup
`next(p for (bid, _), p in live.items() if bid == owner['block_id'])` then returns the earliest placement, which is
the voided one for every block that was rescheduled, advanced to `whole_block`, or advanced to `single_retry`.

FT-11 (02d §4.1) is explicit: «`reduce` counts a window only when its `(block_id, attempt)` is a live placement».
Here "live" is per placement: the id is in THAT placement's envelope's `blocks` (02d §0.4).

Executed witness (`w2.py`):
1. Build the base fixture.
2. Apply `advance_first`, which moves `big:on:1:0` to `whole_block` and gives it live attempt 1 in envelope 51.
3. Report `keep` for every loaded envelope. `check_roster` returns `[]`.
4. Capture exactly the live keys.

```
spread_exceeded big:1 = True   (contract: False — five fully counted parents in five envelopes)
executed lever L1 = 4.5        (contract: |(51+1+2+3+4)/5 − 7| = 5.2)
with voided key ('big:on:1:0',0) added: spread False, lever 5.0   (contract: voided key ignored → 5.2)
```

This cuts both ways:
- **False reject:** the stress step 4 comparison with `executed_status`.
- **False accept:** a packer or reducer that counts voided windows would agree with the checker.

Fix: `live = {(p['block_id'], p['attempt']): p for p in placements if p['block_id'] in
envelopes[p['envelope_index']]['blocks']}`, then select the owner's live placement from that dict.

### M1 — MATERIAL: the executed lever drops partly-counted and partly-terminal parents (INV-45)

45/10 §Q4 (02d §4.1): «A parent's position is the item-weighted mean of the envelope indices of its executed
windows». FT-10 ties the null rule to «zero counted parents». 02d X-5 flagged the tension between the two texts
explicitly, and record 31 X-5 ruled: «Both texts are installed literally, as §4.1 does.» The consequence is that a
parent with at least one counted window has an executed position. Spread still counts only fully counted parents.

`check_executed` stops at the first uncounted or terminal item and positions fully counted parents only.

Executed witness (`w3.py`): take `split_roster(capacity=90)`, report envelope 52 `keep`, and capture every live key
except `('big:on:1:0:single:0', 2)`. The checker gives lever L1 `4.5`. The literal 45/10 reading, with the parent
positioned at 52 by its one counted item, gives `5.4`.

This is MATERIAL rather than BLOCKER only because this column is PROVISIONAL (Q16) and the ruled text needs a
reconciliation that 31 X-5 already chose. Fix it together with B2.

---

## 2. INV rows: predicate by predicate

I compared every ROWS predicate against its 02d §5.3 predicate. Apart from B1 (INV-27, INV-38), B2 and M1
(INV-26, INV-45), none is stronger or weaker than 02d. Rows checked with no defect:

INV-01..12, 14..25, 28..37, 41, 46..52.

Points confirmed along the way:
- INV-11 implements the (a)/(b) exclusivity exactly.
- INV-15/16 follow 45/21 (E) and FT-13.
- INV-20 sums over live and voided placements.
- INV-24 accepts same-parent pieces. P5b passes; P5c is rejected.
- INV-25 applies at the root only, and at the reconstructed root.
- INV-28 applies in registered mode only.
- INV-35 carries codes (a), (b) and (c) per 31 X-7.
- INV-37 names a voided `(block_id, attempt)`.
- INV-41 applies the odd/odd rule to the 1.7B role.
- INV-47's phase machine matches FT-14, including its rejection of two `cut_off`s.
- INV-48 uses `interior_s` (FT-12), not `cap`.

## 3. Re-derivation core: hunted and found consistent with 02d

- **Decisions (`_decide`).** Every line of the §3.2 table reproduces, with FT-1 amendments included:
  - a completed culprit at `initial` or `whole_block` gives `keep`;
  - a single culprit gives `advance`, whatever its status;
  - `whole_block` gives `split` on `cut_off` and `unattributed_overrun` on `not_started`;
  - the innocent fallback follows `anyc`;
  - `not_started` is never a culprit;
  - `Bound` is `predicted_s` at `initial`/`whole_block` and `worst` for singles.
- **`late`.** It is set from the latest observation using the pre-call stage's Bound; it is false after a
  `cut_off`/`not_started`, and false for new singles.
- **Effects.**
  - Voiding happens in `block_ids` order.
  - Terminal entries are appended in block order, then item order, with the voided placement's attempt.
  - `ceiling_violation` sets the stage and makes no placement.
  - `unattributed_overrun` keeps the stage (RD-14).
  - A split keeps the parent at `whole_block`, sets `superseded`, and gives singles `attempt` = parent's latest + 1
    and `predicted_item_s = [parent[j]]` (X-2, X-3).
  - The whole-block reservation is `min(Σ worst, cap)` in a fresh envelope.
  - A reschedule reuses the previous `reserved_s`.
- **Eligibility (Q9, FT-3, Q10).**
  - The index must exceed both the reporter and the last event.
  - The envelope must be unreported, `loaded`, and of the same model.
  - It must hold no `whole_block` placement; the checker tests the block's current stage, which is equivalent
    because every other envelope such a block ever touched is already reported.
  - M8-by-parent and capacity are tested over live and voided placements. This is equivalent to a live-only
    reading, because voided ids exist only in reported envelopes.
  - Each placement updates eligibility for the next, and envelopes created earlier in the same event are eligible.
- **Digest.**
  - The preimage drops `sha256`, `registered_sha256` and each `events[k].sha256`.
  - `canon` matches §1.2 (`ensure_ascii` default).
  - The root reconstruction is RD-3 + X-1 (parents in level/role/k order, `blocks` rebuilt in placement order).
  - Per-event digests and the final field-for-field equality are checked, as FT-8 requires.
  - X-4 float order is followed (`sum()` in item order; parent order = `roster.blocks`).

## 4. Test strength (mutations in the /tmp copy; harness `/tmp/a291lens/mut.py`)

| # | Mutation | Result |
|---|---|---|
| M3 | delete the INV-47 order check | killed (D, H) |
| M4 | INV-47 admits two `cut_off`s | killed (H) |
| M5 | delete INV-48 | killed (D) |
| M6 | eligibility without capacity | killed (E, H, gate-45) |
| M11/M12 | whole-block reserve without `min(…, cap)` (replay / static) | killed |
| M13 | delete single `culprit_limit` | killed (I) |
| M14 | delete INV-28 | killed (B) |
| M18 | delete INV-16 | killed (C) |
| **M1** | delete INV-35(a) `reschedule_without_culprit` | **SURVIVED** |
| **M2** | delete INV-35(c) `inv_35c` | **SURVIVED** |
| **M7** | eligibility without the `whole_block` exclusion | **SURVIVED** |
| **M8** | eligibility without M8-by-parent | **SURVIVED** |
| **M9** | culprit `>` changed to `>=` | **SURVIVED** |
| **M10** | shortfall without the five-envelope clause | **SURVIVED** |
| **M16** | FT-10 planned-lever null changed to `0.0` | **SURVIVED** |
| **M17** | delete INV-05's registered-descendant clause | **SURVIVED** |

Why each survived:
- **M1, M2.** The INV-35 test asserts `inv_id` only. Its single mutation fires both (a) and (c), so each code check
  masks the other. Fix: assert `(inv_id, code)` pairs, with one witness per code.
- **M7.** Needs an event in which an initial culprit advances and its innocent mate has no lower eligible envelope,
  so that capacity is left in the fresh `whole_block` envelope. The expected target is a new envelope.
- **M8.** Needs a reschedule whose lowest capacity-fit envelope holds another parent of the same cell.
- **M9.** Needs a boundary witness at `elapsed_s == Bound`; the contract answers "not a culprit".
- **M10.** Needs five non-terminal parents in fewer than five envelopes.
- **M16.** Needs a model with zero non-terminal parents at a level (R2 extended until `big:1` has none).
- **M17.** Needs a registered descendant with `claim_ready: false`.

The fixture helper `refresh_derived` re-implements `_derived` line for line, so INV-27/49 witnesses are not
independent of the oracle. This is how B1 got past both.

## 5. Rulings on the seat's CONTRACT GAPS

1. **Root cutoff inferred from initial placements plus the idle slot.** ACCEPT; this is the closest reading. RD-3 puts
   pack-time placements first; INV-15 forbids an empty loaded root envelope; the Q14 idle slot is pack-time; every
   event envelope is appended. `max(...) + 1` is therefore exact for every legal root.
2. **Removal of earlier state is checked only by `check_transition`.** ACCEPT. §6 assigns append-only and fixedness
   to `check_transition`, and a single roster cannot carry that evidence.
3. **INV-26/45 tested as value boundaries.** ACCEPT. The F column for both is (b) at `R`, PROVISIONAL (FT-4(b)). The
   values themselves are wrong, though: see B2 and M1.
4. **Invalid `check_executed` input returns `{'violations': [...]}`.** ACCEPT as the only reading consistent with
   «pure and never raise» (§6). The magistrate should confirm it, since the stress comparison must map it to
   `executed_status` raising. NIT: the checker demands a `set` of `tuple`s, so a JSON-sourced list of lists from
   A292 is reported as INV-52. State the input type in the brief.
5. **Registered root with `claim_ready: false` accepted; descendants rejected.** ACCEPT as literal. INV-05 clause 2
   is an entry refusal, and no ruled text requires `pack` to emit `true` in registered mode. Flag for the
   magistrate: under D4 such a root is dead on arrival. If `pack` must emit `true`, add the clause to INV-05. The
   descendant clause is untested (M17).
6. **R1 case-2 order rejected by INV-47.** ACCEPT. FT-14 is precedence item 1 and postdates R1; the adjacent
   `minimal` witness keeps the case-1 semantics.

## 6. NITs

- **N1.** Neither 02d nor X-4 fixes the float order of the capacity comparison. The checker uses `Σexisting +
  reserve > cap`; a packer using `cap − Σ ≥ reserve` can disagree at exact boundaries. Add this to X-4 or rule the
  checker's form.
- **N2.** A malformed event can make `_apply` or `_event_checks` raise `KeyError`, which `check_roster` reports as
  INV-52 rather than INV-29. This is harmless (it never raises), but the row attribution is off.
- **N3.** INV-15's witness mutation (clearing `envelopes[0].blocks`) also trips INV-11, so the row is not tested in
  isolation.

## 7. Required before the packer stress run

B1 and B2 must be fixed. M1 should be fixed together with B2. Each fix needs a defect-shaped witness: w1's RD-4 R2
lever, w2's `whole_block` executed spread, and w3's partly-counted lever. Survivors M1, M2 and M7–M10 need
witnesses. After the fix round, run a delta re-audit of `_derived` and `check_executed`.
