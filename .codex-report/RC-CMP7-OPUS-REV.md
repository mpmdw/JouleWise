VERDICT: ACCEPT_WITH_FIXES

# RC-CMP7-OPUS-REV: delta review of RC-CMP-7 (1134bbf58..c372211bf)

This is one of two parallel blocking delta reviews (gate policy rule 3).
- Branch: `review/2026-10-29-rc-cmp7-opus-rev`, cut from `c372211bf`.
- Data: synthetic fixtures only. No real block-5, block-6 or BYTES data was opened or searched for.
- Environment: `/usr/bin/python3.13` with `TMPDIR=/tmp/rcopus7_tmp`, which is outside the checkout and has no
  float-like token.
- Producers on `origin/main` were read as text only: `disclosures.py`, `sensitivity.py`, `kept_units.py`,
  `dry_run.py`, `dominance_closeout.py`, `run_d165_closeout_from_custody.py` and `analysis_engine/artifact.py`.
- Probes: `rc-cmp7-opus-rev/probe_cmp7.py`. Its outputs are in the `*.out` files beside it.

**Why ACCEPT_WITH_FIXES.**
- G7 is sound. No science run can be dropped or added unseen.
- My RC-CMP-6 finding 2 (the relabel route) is closed: 3818 relabels give 0 exits that move a compared leaf.
- One part of the report's F2 claim is false. It says every printed claim word the recompute re-derives is compared.
  Two claim words in the fill still exit 0 when wrong (finding 1). The fix is two `c.exact` rows plus their
  coverage rules. It is local, and the rest needs no new round.

## Suite

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 303 tests in 157.336s` / `OK (skipped=18)` / exit 0 (`suite.out`).

## Findings, ranked

1. **MEDIUM (pre-existing; must fix before acceptance): two claim words the recompute re-derives are still exempt,
   and a wrong one exits 0** (`claims.out`).
   - `fill:gamma/contrasts/*/claim_evaluation/claim_ready_for_l2_l3` is exempted as "reason-code vocabulary"
     (`scripts/compare_b5_recompute.py:1727`).
     - It is not vocabulary. The engine fixes it as `ready iff claim_level_ceiling in {L2, L3, L4}`
       (`joulewise/analysis_engine/artifact.py:874-884`), and `claims_lint.py:1672` gates L2/L3 claims on it.
     - The ceiling is compared. Executed: `C1 claim_ready_for_l2_l3 True (ceiling stays L1): exit=0`. The control is
       `C2 claim_level_ceiling L2: exit=2`.
   - `fill:campaigns/<pack>/claim_usable` is exempted as identity (`:1892`).
     - The recompute prints its own copy in `inputs.<PACK>.claim_usable` (`independent_recompute_b5.py:2820`). The
       stored value is checked by the exclusions re-derivation (`:652`, `:752`).
     - Executed: `C3 claim_usable False: exit=0`. Also `C3b recompute ALPHA claim_usable False, fill prints True:
       exit=0`. The comparator never reads the recompute's `flags`, so its `claim_usable_false` flag does not help
       either.
   - Fix:
     - add `c.exact("outcome_word", f"{cid}/claim_ready", ready, mine.get("ceiling") in ("L2", "L3", "L4") if
       mine.get("ceiling") else None)`;
     - add `c.exact("outcome_word", f"{pack}/claim_usable", fill, ours.inputs.<PACK>.claim_usable)`;
     - map both leaves to these rows.

2. **LOW: printed words still exempt although the recompute can check them cheaply** (`words.out`, `rules.out`).
   - **The two by-construction booleans.** `mean_and_half_width_equal_primary` and
     `bound_independent_values_equal_primary` (`:1863`) take any boolean, so a printed `false` passes.
     - The producer writes a literal `True` (`sensitivity.py:302,344`). They are not printed in `text`, so they are
       not claim words hidden in the sentence. They are still printed words that assert a relation the recompute can
       re-derive.
     - Fix: compare them against `True`, or against `relation()` over the compared values.
   - **Registered contrast-definition words.** `hypothesized_direction`, `claim_role` and `confirmatory_status`
     (`:1730`) are exempt. Executed: `C4 hypothesized_direction negative: exit=0`. They are registered in the sealed
     manifest, which the Registry already reads, so they can be compared literally.
   - **Status words with a fixed value.**
     - `DESCRIPTIVE_STATUS` (`:1803`): `reported_cell/status` is always `"computed"` in the producer
       (`disclosures.py:272`).
     - `battery_assist_contrast/status` is fixed by `n` (`disclosures.py:340-352`), and `n` is compared.
     - `loo/status` is exempt (`C6: exit=0`).
   - The remaining exits are as declared: harvest and history words, `reason_codes`, floor resolution words,
     `characterization/*`, and `restricted`. Flipping `restricted` publishes or withholds a line. That is a disclosure
     control rather than a claim, so it is listed here for the lead only.

3. **LOW: the line gate does not require a compared line, or its unconditional keys, to be present** (`keys.out`).
   - These omissions exit 0:
     - K5: `dominance_branch` without `branch`;
     - K6: `dominance_branch` without `dominance_sentence_licensed`;
     - K8: `sensitivity_window` without `widened`;
     - K9: a window's `neg8_screen` line removed.
   - The producer prints these keys unconditionally (`disclosures.py:952,1158-1162,1250`). The word then survives
     only in `text`, which is a ruled exemption, so this adds no new route past the reader.
   - Fix: give each compared claim line a required-key set, and pair `neg8_screen` and `below_screen_bound` per
     registered pack.
   - In contrast, K7 (`below` omitted) gives exit 1, and duplicates refuse (K1-K4).

4. **LOW: no fixture contains the new sensitivity comparisons.** Over-refusal on a sound window is therefore
   unverified.
   - No test or fixture holds a computed sensitivity reported, floor or contrast row. That leaves the following
     unexercised:
     - `equals_primary` and `not_below_primary`;
     - `outcome_equals_primary`;
     - the two by-construction rules (`grep` over `tests/independent_recompute`).
   - L9 decides these words on L9's numbers (`_same` is a canonical digest, `>=` is exact). The comparator decides
     them on the recompute's own numbers.
     - When the bound is not widened, both sides take the identical path, so they agree.
     - When the bound is widened and an `after == before` tie holds in L9, an ulp difference on the recompute side
       would DISAGREE. That is over-refusal, never under-refusal.
   - RC-CMP-7 OPEN ISSUES 1 should name these leaves explicitly for the full-size window.
   - Separately, a producer `refused` ratio row already DISAGREEs on `ratio` (None against None is
     `missing_or_null`). The new status row adds nothing to that. This is pre-existing and rare.

5. **LOW (doc): a code comment misstates the source of the recompute's hash.**
   - `:776` says the recompute's `exclusions_sha256` hashes the re-derived exclusions. It actually hashes the stored
     `derived/exclusions.json` (`independent_recompute_b5.py:700`).
   - The binding is still sound, because `:1627` requires `exclusions_rederivation == agrees` (A5b below).

## Answers

1. **G7 source: sound. No run is compared nowhere unless both independent sides drop it.** (`g7.out`)
   - The key set is the union of three maps: L9's re-reduced runs, the kept-units universe, and the recompute's
     selected non-reference members (`pairs` at `:208`).
     - L9 holds a key only when the run is both in the universe and re-reduced. The recompute holds it only when the
       member is selected.
     - So the L9-derived universe can only add keys, never hide one.
   - Executed:

     | Case | Result |
     |---|---|
     | A1: drop from kept-units | exit 1 |
     | A2: drop from kept-units and no re-reduction | exit 1 |
     | A3: as A2, plus other exclusions | exit 1 |
     | A6: add `run-z` | exit 1 |
     | A7: add and re-reduce `run-z` | exit 1 |
     | A8: move a run to beta | exit 1 |
     | A9: `run_ids` as a bare string | exit 1 (over-refuses) |
     | A10: a second record | `l9_output_ambiguous` |
     | A11: gamma record and hash both absent | exit 1 |
     | A12: a spare in kept-units | `kept_units_member_not_science` |
     | A13: a science id labelled `role: reference` by the recompute | exit 1 (roles come from the plan tree, not the output) |
     | A14: a re-reduced reference outside the universe | exit 1 |

   - **Both wrong together:**
     - A4: both sides drop the run, with the same hash. Exit 0.
     - A5: both sides read one other exclusions file. Exit 0.
     - A5b: as A5, with the recompute's re-derivation disagreeing with that file. `fails={'exclusions_rederivation':
       1}`, exit 1.
   - So the shared input, the stored exclusions, is bound to the harvest's flags and exclusion inputs. Only a wrong
     harvest could defeat both sides, and that is outside the comparator.
   - NEEDS_RULING 1 (each kept run in `science/*`) is not needed for soundness. It is only a cheap extra guard.
2. **Categorical words: no. Two re-derivable claim words still exit 0 when wrong (finding 1).**
   - Every word that RC-CMP-7 added is compared and refuses when wrong:
     - branch;
     - licensed;
     - ratio status;
     - `below`;
     - `widened`;
     - the p42 status and code;
     - NEG-8 decision;
     - plausible;
     - battery term.
   - The directions and outcomes in the fill were already compared.
   - Of the exemptions:
     - `HARVEST_WORDS` hold harvest and index records the recompute does not re-derive. They are exemptions as
       declared, not claim words in disguise.
     - The two by-construction booleans are not printed in `text`, but they can be compared cheaply (finding 2).
   - The 179 exit-0 mutations, one leaf at a time, are in `words.out`. Apart from finding 1, they are ids, digests,
     registered definitions, harvest words, `restricted`, and status words with a fixed value.
3. **Line gate: holds.**
   - My sweep now covers every section, including `cells` and `window_lines`, against every registered word: 3818
     relabels. Exactly 13 exit 0 (`relabel.out`). Twelve are fixed sentences relabelled to other fixed sentences, and
     one is `sensitivity_boundary` relabelled to `superseded_history`. All of these words are keyless, so the edit
     is text only.
   - The 58 exits of the earlier sweep are now 0 (`test_opus_relabel_sweep_never_exits_0`, in the passing suite).
   - Key-set variants:
     - duplicates refuse;
     - a wrong `below_screen_bound` moved into `block_lines` refuses `line_word_unregistered`;
     - a nested value refuses.
   - The only gap is omission (finding 3).
   - The gate's key tables match the producer: an AST pass over every `_item` call in `disclosures.py` finds no
     unregistered word or key (`producer_item_keys.out`). The only entries it prints are `**` spreads, and each was
     read by hand against `LINE_KEYS`.
4. **Over-refusal: the RC-CMP-4 window passes.**
   - `test_rc_cmp4_window_passes_and_lists_each_reference_member` passes, with all 57 members listed
     `compared_in:*`.
   - Gamma's interior references are never selected by the recompute. `read_reference_slots` takes only spare-retry
     slots, and the gamma tree gives those references no spare. So the "selected diagnostic is a key" rule does not
     fire on a sound window.
   - Conditional keys are admitted, because the gate requires only one key per keyed word.
   - The new sensitivity words remain unverified (finding 4).
5. **Remaining value-derived routing:**
   - the line word in `step()`, now gated;
   - the `R`/`R_cm` label read from `text` (a mislabel gives `no_row`, which refuses);
   - `loo_magnitude` keyed on the printed `block_number` against the recompute's numbering (a swap DISAGREEs
     unless the values coincide; not probed, because the fixture has no such rows);
   - the kept-units universe, which is L9-derived but can only add keys (answer 1).

   None of these yields an exit 0 with a wrong value in my probes.
