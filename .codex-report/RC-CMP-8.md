STATUS: DONE

# RC-CMP-8: claim words, required keys and the sensitivity fixture (RC-CMP7-OPUS-REV F1-F5, RC-CMP7-FABLE-REV F1-F2)

Seat RC-CMP-8, branch `lane/2026-10-27-recompute-comparator`, from `c372211bf`. Synthetic data only: no real
block-5, block-6 or BYTES data was opened or searched for. `/usr/bin/python3.13`, `TMPDIR=/tmp/rccmp_eight_tmp`
(outside the checkout, no float-like token). Producers on `origin/main` were read as text only:
`analysis_engine/{__init__,artifact,sensitivity}.py`, `b5_analysis/{disclosures,sensitivity,archive}.py`,
`results_fill_adapter.py`; the sealed manifest `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json`
(already pinned in `REGISTRY_PINS`) was read as data. The script imports no `joulewise` module (unchanged).

Reviews read: `review/2026-10-29-rc-cmp7-opus-rev` (41813bd9c) at start; `review/2026-10-29-rc-cmp7-fable-rev`
(e2e709402) was not yet published at start, was fetched mid-round and again before this report (unchanged).

## SUMMARY

- **Opus F1 (MEDIUM), closed.** `claim_ready_for_l2_l3` is compared against `ceiling in {L2, L3, L4}` from the
  recompute's ceiling; `campaigns/<pack>/claim_usable` against the recompute's `inputs.<PACK>.claim_usable`. Both
  leaves bind those rows. C1, C3, C3b now exit 2; controls exit 0.
- **Opus F2, closed.** The two by-construction words are compared against `True`. `hypothesized_direction`,
  `claim_role` and `sampling/confirmatory_status` are compared against the sealed manifest. `reported_cell/status`,
  `battery_assist_cell/primary/status`, `battery_assist_contrast/status` and `loo/status` are compared against
  the producer's rule. Also compared now, under the round's rule: every leave-one-out row's `influence_triggers`
  (re-derived from the recompute), the manifest's condition ids, difference orientation, metric name, tag and
  window class, point estimator, `claim_floor_rule`, `transport_rule_id` and the v3 `aggregation` word, and both
  NEG-8 allowance `source` words. C4 and C6 exit 2. `restricted` is its own listed rule (`DISCLOSURE_CONTROL`).
- **Opus F3, closed.** Each compared claim line, each sensitivity record row and window, and each fill claim key
  has a required-key set taken from the producer's unconditional keys (`required_key_absent:<where>/<key>`).
  `below_screen_bound` and `neg8_screen` pair per registered pack. K5, K6, K7, K8 exit 2 and K9 exits 1. Lines
  whose conditional keys are absent pass the gate.
- **Opus F4, closed.** `with_sensitivity()` is a producer-shaped computed sensitivity: ALPHA's decode reported
  cell with its projection cell and disclosure lines, both decode floor cells, and the decode contrast. It
  appears in the record, in the disclosure copy and in the block-line copies. On a widened and an unwidened window
  it exits 0 with every relation row AGREE. Every relation word flipped (all copies, or the disclosure copy alone,
  or the block line alone) exits non-zero: 48 flips. `widened` flipped exits non-zero.
- **Opus F5, closed.** The `:776` comment now says that both sides hash the stored `derived/exclusions.json` and
  that the binding holds through `exclusions_rederivation == agrees`.
- **Fable F1 (MEDIUM), closed.** This is the same fix as Opus F3's pairing. F2.c (relabel to `adapter_continuity`),
  F2.d and F2.e now exit 1. `neg8_screen` is added to `test_rc_cmp7.COMPARED_LINES`.
- **Fable F2 (LOW), closed.** This is Opus F2's by-construction rows. F2.g now exits 2.
- **Fable F3 (LOW, carried, outside the brief), not changed.** `Custody.step_ok` still has no caller (OPEN ISSUES 5).
- Suite: `Ran 330 tests` / `OK (skipped=18)` / exit 0. That is 303 at `c372211bf`, plus 27 in
  `test_rc_cmp8.py`. Opus's `probe_cmp7.py` runs to completion at this head (exit 0). Its outputs are below.

## Per-finding table (evidence at this head; counterfactuals at `c372211bf`)

Counterfactual sources at `c372211bf`:
- Opus probe C*/K*: rerun by me in a scratch worktree at `c372211bf`. The results match Opus's `claims.out` and
  `keys.out`.
- Fable F2.*: Fable's `probes.out`, recorded at `c372211bf`. Fable's probe imports the checkout by absolute path,
  so I did not rerun it at the old commit.

"In place" means the test in `test_rc_cmp8.py` disables the new check and shows the same case exiting 0.

| Finding | Case | `c372211bf` | This head | In-place counterfactual |
|---|---|---|---|---|
| Opus F1 | C1 ready True, ceiling L1 (fill) | exit 0 | exit 2 `step11_unmapped_fill` (`value_differs`) | old rules: exit 0 |
| Opus F1 | C1 in verdict and fill | n/a | exit 1, `{cid}/claim_ready` DISAGREE | |
| Opus F1 | C2 ceiling L2 (control) | exit 2 | exit 2 | |
| Opus F1 | C3 fill claim_usable False | exit 0 | exit 2, `outcome_word` 1 | old rules + no row: exit 0 |
| Opus F1 | C3b recompute claim_usable False | exit 0 | exit 2, `outcome_word` 1 | old rules + no row: exit 0 |
| Opus F2 | C4 hypothesized_direction negative | exit 0 | exit 2 | old rules: exit 0 |
| Opus F2 | claim_role, confirmatory_status flipped | exit 0 (same exemption) | exit 2 (fill), non-zero (verdict+fill) | old rules: exit 0 |
| Opus F2 | C6 loo/status computed | exit 0 | exit 2 | old rules: exit 0 |
| Opus F2 | influence triggers wrong or emptied | exit 0 (vocabulary exemption) | non-zero | old rules: exit 0 |
| Opus F2 | battery_assist_contrast status one_quad / not_computable / refused | exit 0 | non-zero | old rules + no row: exit 0 |
| Opus F2 / Fable F2 | F2.g by-construction False | exit 0 | exit 2 | old rules + no row: exit 0 |
| Opus F2 | reported_cell / assist primary status wrong (F4 fixture) | exit 0 | non-zero | old rules + no row: exit 0 |
| Round rule | orientation, condition ids, metric name/tag/window class, floor rule, aggregation, transport rule, estimator name, both source words | exit 0 | exit 2 (copy) / non-zero (producer) | old rules (+ no row for sources): exit 0 |
| Opus F3 | K5 branch absent | exit 0 | exit 2 `required_key_absent:disclosure:block_lines/dominance_branch/branch` | no `require`: exit 0 |
| Opus F3 | K6 licensed absent | exit 0 | exit 2 `required_key_absent:...` | no `require`: exit 0 |
| Opus F3 | K7 below absent | exit 1 | exit 2 `required_key_absent:...` | |
| Opus F3 | K8 widened absent | exit 0 | exit 2 `required_key_absent:...` | no `require`: exit 0 |
| Opus F3 | K9 neg8_screen line removed | exit 0 | exit 1, `outcome_word` 1, `routing_id` 1 | |
| Opus F3 | fill claim keys absent (ready, direction, hypothesized_direction, confirmatory_status, loo/status, claim_usable) | exit 0 | exit 2 `required_key_absent:fill:...` | no `require`: exit 0 |
| Fable F1 | F2.c neg8 word relabelled adapter_continuity | exit 0 | exit 1 | |
| Fable F1 | F2.d neg8_screen dropped | exit 0 | exit 1 | |
| Fable F1 | F2.e below_screen_bound dropped | exit 0 | exit 1 | |
| Fable F1 | F2.a / F2.f2 controls | exit 0 / exit 0 | exit 0 / exit 0 | |
| Opus F4 | sound widened / unwidened window | no fixture | exit 0, all relation rows AGREE | |
| Opus F4 | each relation word flipped (8 words × 3 copy sets × 2 windows) | no fixture | all non-zero | |
| Opus F5 | comment | wrong source | stored file + re-derivation binding | `CommentTests` |

Opus's probe at this head, besides the table:
- `g7`: A0 exits 0. A1 through A14 are unchanged from Opus's `g7.out`; A4 and A5 still exit 0. That is the
  declared joint-drop residual, closed by A5b.
- `relabel`: 4067 relabels, of which 13 exit 0, all keyless bare sentences. At `c372211bf` it was 3818 and 13;
  the base now carries the NEG-8 lines.
- `words`: 141 single-leaf exit-0 mutations, down from 179. By class:
  - ids, digests, plan ids, pins, schema versions and record shapes;
  - `restricted` (listed);
  - harvest words: `stored_status/status`, `harvest_once`;
  - `reason_codes` (declared);
  - flag-count `family`, `code`, `blinding` (NEEDS_RULING 3);
  - floor-resolution `status`, `transport_verdict`, `arm_gates/*/status` (NEEDS_RULING 2);
  - `characterization/*` constants;
  - `metric/unit` and `cell_a_id`/`cell_b_id` (not in the manifest's contrast row);
  - variance-contribution names;
  - limitation notes;
  - `evidence_class`.

Fable's probe, adapted (one helper sets the base's `neg8_screen` word instead of appending a second line):
- G7.0 through G7.g are unchanged from Fable's `probes.out`.
- The gate-passing sweep: 62 relabels, of which 40 exit 0. All of them are bare sentences. Fable's three
  `stored_status` → `cells/reported_cell` exits now refuse, because `reported_cell` requires its keys.

## FILES CHANGED

- `scripts/compare_b5_recompute.py`:
  - `Registry` records each contrast's manifest words (role, direction, confirmatory status, condition ids,
    orientation, metric name, tag and window class, estimator, floor rules).
  - New helpers: `READY_CEILINGS`, `LOO_REQUIRED_MAX`, `loo_status`, `sign`, `loo_triggers`, `V3_AGGREGATION`,
    `paired_status`, `WINDOW_CLAIM_LINES`, `extraction_key`.
  - New family function `compare_campaigns`, called from `run`.
  - New rows in `compare_contrasts`, `compare_arms`, `compare_sensitivity` and `compare_disclosures`.
    `reported_cell` lines are paired as cell lines, and the window claim lines are paired per registered pack.
  - Required-key gate: `CONDITIONAL_KEYS`, `COMPARED_LINES`, `REQUIRED_KEYS`, `SENSITIVITY_KEYS`,
    `SENSITIVITY_LINES`, `FILL_KEYS`, `require`, `sensitivity_row`, `gate_sensitivity`, `gate_fill`, and the call in
    `gate_lines`.
  - `POSITIONS["trigger"]`.
  - `COVERAGE`:
    - new family rules for every compared leaf above;
    - `DISCLOSURE_CONTROL` for `restricted`;
    - narrowed `DESCRIPTIVE_STATUS`;
    - a separate load-correlated status rule;
    - narrowed floor and definition exemptions, with reasons;
    - `claim_usable` taken out of `IDENTITY`;
    - `source` taken out of the removed-unit rule.
  - The F5 comment, and the module docstring.
- `tests/independent_recompute/test_rc_cmp8.py` (new, 27 tests): the regressions above, the in-place
  counterfactuals, the F4 fixture (`with_sensitivity`), and the gate's no-over-refusal check.
- Fixture completions. Each change makes a fixture producer-shaped; no assertion is relaxed.
  - `test_comparator.py`:
    - `NEG8_*`, `neg8_lines`, `neg8_recompute`. The base carries every window's NEG-8 lines, and the recompute its
      NEG-8 terms and `screen_decision`.
    - The recompute's `inputs.<PACK>.claim_usable`.
    - The verdict's prefill `metric_tag` is the manifest's `phase_prefill_p2048_energy`, and its estimator name is
      the manifest's `abba_block_arm_mean_difference_t_v1`.
  - `test_rc_cmp7.py`:
    - `with_neg8` replaces the NEG-8 lines instead of appending.
    - `with_loo` uses the engine's word `complete` (not `computed`) and gives the recompute row its `holm_reject`.
    - `COMPARED_LINES` gains `neg8_screen`.
    - The `p42 status computed` sub-case now expects the earlier refusal `required_key_absent:...record/primary`
      (still exit 2). Its `c372211bf` counterfactual also switches off `sensitivity_row`.
  - `test_review_fixes.py`, `test_comparator_meter.py`, `test_structural_rules.py`:
    - Window lines are edited in place, so they are no longer replaced wholesale (that dropped the producer's
      `below_screen_bound` and NEG-8 lines).
    - `claim_evaluation` and `campaigns` are edited in place, so they are no longer replaced wholesale (that dropped
      claim keys).
    - Planted lines carry their producer's unconditional keys.
    - `v3_floor` carries the floor-rule words.
    - The synthetic `AssistCustody` records carry window claim lines and status words.
- `.codex-report/RC-CMP-8.md` (this report).

## DECISIONS I MADE

1. **By-construction words against `True`.** The producer can print only `True`: `sensitivity.py` refuses with
   `sensitivity_changed_bound_independent_value` otherwise. A `relation()` over the recompute's values would add
   an ulp over-refusal route and nothing else.
2. **`confirmatory_status` is registered as `confirmatory`.** The engine demotes a contrast only for an
   outcome-dependent top-up. The sealed `replacement_policy.outcome_dependent_top_up` is `forbidden`, so the
   registry derives `confirmatory`. A window that actually took a top-up would refuse here, which is the strict side.
3. **`loo/status` follows the engine's rule.**
   - The rule is `not_required` above 10 complete observations, else `complete` with rows and `not_run` without.
   - The registration plans `len(block_ids)` blocks and forbids replacements. With at most 10 registered blocks,
     the word is `complete` when the recompute has rows, else `not_run`.
   - More than 10 registered blocks gives `None`, which refuses.
4. **`influence_triggers` are compared.** The engine's `influence_triggers` order is estimate_sign, floor_status,
   adjusted_rejection, outcome, estimate_magnitude. Each is re-derived from the recompute's full contrast and its
   row, with threshold = the active floor (the engine uses `active_floor_j` when kept quads are given). The list
   is compared whole and per position. An empty list binds the whole-list row: an emptied copy is a printed "no
   trigger", not an empty container.
5. **Pairing scope.** `below_screen_bound` and `neg8_screen` pair per registered pack: the producer prints both for
   every window, and Fable F1 asks for this. That made the base fixture carry every window's NEG-8 lines (Fable's
   own note). `reported_cell` lines pair with the recompute's computed reported cells, so a dropped line is
   DISAGREE.
6. **Required keys are the producer's unconditional keys only.** The conditional ones are left out: a refused
   ratio's values, a non-computed assist contrast's estimates, a non-computable ratio's estimates, a
   machine summary's statistics and band. These are listed in `CONDITIONAL_KEYS` and exercised by
   `test_producer_lines_with_conditional_keys_absent_pass_the_gate`. Fill claim keys are required too; this is the
   stricter reading of "each compared claim line".
7. **I went beyond Opus's list where the round's rule applies and the registry holds the literal word.**
   - Words compared: condition ids, orientation, metric name, tag and window class (`floor_selector`),
     `claim_floor_rule` and `transport_rule_id`, `aggregation` (a v3 engine constant), the point estimator, and the
     NEG-8 `source` words (the recompute's own copy).
   - These rows use the `routing_id` family for definition ids and rules, and `outcome_word` for the status and
     source words.
8. **Commits.** The brief asks for the report to be pushed after each item. F1, F2, F3 and F5 share fixtures and
   the coverage table, so I pushed them together with this report, and F4 in the same push. There is one code
   commit and the report travels with it. Each item has its own test class.
9. **Fable F3 not changed.** It is outside this brief's WRITE_SCOPE intent (a dead method, no claim word), and
   removing it is not a BLOCKING or MEDIUM fix.

## OPEN ISSUES

1. **Full-size synthetic window still owed.** This carries over RC-CMP-7 OPEN ISSUE 1 and Opus F4. It must cover:
   - the leaves `equals_primary`, `not_below_primary` and `outcome_equals_primary`, where L9 decides by canonical
     digest and exact `>=` and the comparator decides on the recompute's numbers (an ulp on a widened tie
     over-refuses, never under-refuses);
   - the new `influence_triggers` rows, whose `estimate_magnitude` threshold is a strict `>` against
     `0.25 * floor`;
   - the `loo/status` rule.
2. **Pre-existing over-refusals, unchanged and noted:**
   - a battery-assist contrast with n < 5 (the recompute marks it `below_registered_minimum` and `items()` drops it,
     so its line is DISAGREE);
   - a refused dominance ratio (None against None is `missing_or_null`, Opus F4 note).
3. **The fill's `kept_block_ids`, `removed_block_ids` and `sampling/removed_block_ids` are bound by the identity
   exemption.** The verdict's kept set is compared as `kept_units`, but the fill's own copies are not bound to that
   row, so an edited copy exits 0. Whether `kept_blocks()` (block ids) and the recompute's `kept_quads` share a
   spelling on the real shape is also unverified here.
4. **`machine_member/removed` remains a STRUCTURE exemption.** The recompute's `selected` flag may map to it for
   science runs, but the meter members' run set (references included) needs checking on the real shape first.
5. **`Custody.step_ok` has no caller.** This is Fable F3, carried.

## NEEDS_RULING

1. **`confirmatory_status` registered value (DECISION 2).** The stricter reading is implemented: `confirmatory` from
   the forbidden top-up policy. A ruling should confirm that a top-up window must refuse rather than compare
   `demoted_exploratory`.
2. **Floor-resolution status words stay exempt, with a stated reason.**
   - The words: `floor/status`, `floor/transport_verdict`, `floor/resolutions/*/status`,
     `floor/arm_gates/*/status`, `floor_source`, `floor_limit_class`.
   - The engine's vocabulary differs between paths. `_combined_floor` writes `resolved`/`refused` and
     `exact`/`transported`/`refused`; the base fixture's v3 floor prints `exact`. The recompute has no transport
     model.
   - Comparing them needs a producer-confirmed v3 vocabulary table. I did not take the stricter reading here because
     I could not establish the producer's v3 words from the sources I read. A guessed table would refuse sound
     windows.
3. **`flag_count` family and blinding.**
   - These are determinable from the sealed flag catalog (`configs/campaigns/v5_claim_25g83/flag_catalog.json`) for
     family. Blinding is the flag's own word, which the producer only checks as *admitted* by the catalog entry.
   - A per-code row cannot be bound under G2: `code` is not an identity field, and window lines key on line word
     and pack only.
   - Binding would mean admitting `code` as an identity owned by `flag_count` lines. That is a G2 change for the
     lead to rule on. Left exempt (STRUCTURE).
4. **`restricted`** stays a listed disclosure control, as the brief says. Its rule now names it alone.
