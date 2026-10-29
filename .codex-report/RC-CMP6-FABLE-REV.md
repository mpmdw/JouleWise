VERDICT: ACCEPT_WITH_FIXES

# RC-CMP6-FABLE-REV: delta review of RC-CMP-6 (`7fede8c7..1134bbf58`)

Seat RC-CMP6-FABLE-REV, Fable 5.1, cloud, synthetic only; no real block-5/6/BYTES data opened or searched.
Branch `review/2026-10-29-rc-cmp6-fable-rev` at `1134bbf58`; counterfactual worktree at `7fede8c7`.
`/usr/bin/python3.13`, `TMPDIR=/home/user/rccmp-tmp`. Evidence in `.codex-report/rc-cmp6-fable-rev/`.
I designed this gate in the consult; I read the implementation against that design as a fresh reader.

**Summary.** G1-G6 hold under every executed witness: all round-1..3 witnesses and consult probes refuse
with the named codes, every consult control passes, the registered `cmp-abba` spelling binds, and all 323
real-shape numeric leaves RC-CMP-4 listed still map. I found no route by which exit 0 coexists with a wrong
printed number. But the brief's Amendment 1 (**G7**, main `8fbe1b397`, 06:04 UTC) is not implemented and the
report does not mention it: the seat's first commit is 06:05 UTC, one minute after the amendment landed. RC-CMP-4's
cause A (NEG-8 reference rows) still refuses, so the full-size readiness run will still refuse. Fix F1 is
blocking before that run; F2 is the Sol-3 class on block ids (pre-existing, witnessed here); F3 is minor.

Suite at `1134bbf58`: `Ran 282 tests in 202.830s OK (skipped=18)` (`suite-1134bbf58.out`).

## Findings (ranked)

**F1 (blocking). G7 not implemented: the `run_phase_energy_j` key universe is still taken from the two sides'
outputs.** `scripts/compare_b5_recompute.py:582-614`: `compare_runs` pairs `rereduced_names(custody)` (L9's
file listing) with `selected_runs(members)` (the recompute's own `selected` flag). Nothing reads a registered role
table, and the restricted output has no `compared_in:<family>` listing (`probes-at-1134bbf58.out` P1a: `restricted
output mentions compared_in: False`). The diff contains no G7 change; `RC-CMP-6.md` covers G1-G6 only.
- P1a: two NEG-8 reference members the recompute marks `selected` (`neg8-refcorpus-r01`, `neg8-window-start-r2`),
  no L9 re-reduced file: `exit=1 fails={'routing_id': 2, 'run_phase_energy_j': 6}`, every row `missing_or_null`.
  This is RC-CMP-4 cause A on the fixture (162 rows on the full-size window). Identical at `7fede8c7`.
- P1b: the same members with `selected=false`: `exit=0`. The universe follows the recompute's flag, which G7 forbids.
- P2 (the NEG-8 half): with producer-shaped `neg8_allowance`, `reference_counts` and `corpus_counts` lines, a start
  reference dropped on L9's side gives `fails={'count': 1, 'floor_j': 1}` (`reference_counts/start`,
  `neg8_allowance/start.mean_j`), so a dropped reference still DISAGREEs by value. What is missing is the universe
  rule and its listing.
- Fix: read the registered role table in the comparator (a registered input, not `members[*].role` or `selected`
  from the recompute output and not L9's `rereduced/` listing); science ids form the `run_phase_energy_j` universe
  on both sides; every other registered member is listed in the restricted output as excluded with
  `compared_in:<neg8 family>`; a member on either side outside the table stays DISAGREE. Regression: P1a passes
  after, P1c (an L9 re-reduced reference with no recompute member) still DISAGREEs, P2b still DISAGREEs.

**F2 (medium, pre-existing). A leave-one-out block id is still parsed, so a typo'd `omitted_block_id` routes
and is labelled `routing_id`** (`:746-756` `loo_key`, `block_key`; `:1621`). The brief's G3 says no id is parsed
for its parts; RC-CMP-6 open issue 3 discloses the parse without a witness. This is Sol 3's shape on an id outside
the sealed configs.
- P3b `omitted_block_id="TYPO-b02"`: `exit=0`, leaf reported `routing_id`. P3c the other contrast's spelling
  `ctr-d117-prefill-...-b02` under the decode contrast: `exit=0`. P3a control `b02`: `exit=0`. Same at `7fede8c7`.
- P3d `ab02`: the comparator's `(?:^|-)b(\d+)$` refuses (`key_unresolved`) a spelling L9's own
  `_block_number` (`disclosures.py:573-576`, `(?:b|block-?)(\d+)$`) accepts, so the two parsers also differ.
- Fix: no regex. The contrast's registered block list (`bundle_blocks/planned_block_ids`, already compared
  literally through `kept_units`) is the id set; a loo row's `omitted_block_id` must be in it literally, and the
  recompute's `block_number` is spelled through the same list, so both sides key on one literal id.

**F3 (low, pre-existing, outside the delta). The custody record's step status is never read.** `Custody.step_ok`
(`:323`) has no caller; `run()` only echoes `l9_steps`. P4a: every step recorded `failed`, `exit=0`,
`l9_steps={'11': 'failed'}`. With Opus Q2d/Q2e (an empty fill passes), a failed step 11 that wrote a partial fill
exits 0. Fix: refuse `l9_step_not_ok:<step>` unless every listed step is `ok` (two lines).

**Notes (no fix required).**
- Three earlier probe scripts cannot execute at `1134bbf58` (`sol-probes-at-1134bbf58.out`, section `prior`):
  `opus-rev/probe_comparator.py` writes its disclosure with its own writer (`baseline: REFUSED
  l9_output_not_canonical:disclosure`) then `KeyError: 'note'`; `sol-rev-2/probe_new_paths.py` `KeyError: 'note'`;
  `opus-rev-2/probe_delta.py` stops after N1d at a refusal (no `coverage` key). Sol's round-3 `attack_duplicates`
  asserts the old writer's spacing and did not run. Their cases are suite tests (`test_review_fixes.py` P1b-P12,
  Sol and N1; `test_structural_rules.py` Sol 2/3, N2, N3; `test_input_gate.py` B3-B6). RC-CMP-6's "all round-1 and
  round-2 probe tests still run" is true of the tests, not of the scripts; the report should say which.
- `binding()` still reads the dominance line's `text` for `R`/`R_cm` (`:1617`). The producer prints no other
  marker (`disclosures.py:1143-1157`), and the bound value is checked against the row the text names, so a wrong
  number cannot pass this way; it is the deferred text class (open issue 3). Acceptable.
- The registry is read from the checkout's `configs/campaigns` under hard-coded pins (`:363-368`), not from the
  custody's sealed sources. All four pins equal `configs/campaigns/v5_claim_25g83/sealed_inventory.json`
  (verified by sha256). Acceptable; a pin change is a registration change.

## Answers

**1. Earlier witnesses and controls at `1134bbf58`.** Yes.
- Consult prototype (`consult-prototype-at-1134bbf58.out`, comparator-alone lines): B1 `identity_field_misplaced:
  fill:gamma/contrasts/*/floor/contrast_id`, B2 `...disclosure:contrasts/*/estimator/contrast_id`, B3/B4
  `l9_output_duplicate_key:fill`, B5/B6 `l9_output_nonfinite:fill`, B7 `routing_id_unregistered:disclosure:
  floors/*/cell_id`, C1 misplaced, C2-C4 `l9_output_not_canonical:fill`; all exit 2. Controls A1-A4, A7 exit 0;
  **A8 (registered `d117-df-cmp-abba-ph-decode-qwen3-1p7b`) now exit 0, 0 unbound** (was `key_unresolved`); A5 exit
  2 `row_disagrees` (the Opus Q6 ruling, unchanged by design); A6 exit 2 `no_row` (no meter in the fixture, as in the
  consult). Re-run at `7fede8c7`: byte-identical to the committed `probes.out`.
- Opus round 3 (`opus-probe-at-1134bbf58.out`; one adaptation so the script continues past Q3c): Q1b, Q1e, Q3c,
  Q4, Q5a, Q5b, Q5c exit 2; Q1d listed; Q2d/Q2e exit 0 (completeness, unchanged); Q6 exit 2; F4 AST mutants
  `while_loop`, `helper_add`, `helper_calls_family` all `failures=1`. At `7fede8c7` byte-identical to the committed out.
- Sol round 3 (`sol-probes-at-1134bbf58.out`, TMPDIR path adapted): nested identity refused
  `identity_field_misplaced`, `bad_raw_floor_cell_id_prefix` refused `routing_id_unregistered`, `v3_arms_reordered`
  exit 2, clean variants (null, reordered lists, v3 arms, registered raw floor id) exit 0; the model-alias case
  (`Qwen3-1.7B-4bit` on a summary line) still fails 16 rho rows, correctly, since L9 prints `qwen3-1p7b`.
- Rounds 1-2: 17 scripts replayed through Sol's `prior()`; 14 complete with the fail-closed outcomes of round 3
  (meter probes 0 ns); 3 cannot run on the producer-shaped fixture (note above), their cases are suite tests.

**2. Exit 0 with a wrong printed number.** None found through G1-G3. Checked and closed: nested identities
(`leaves()` reads identity only from `IDENTITY_OWNERS`; path groups override the context, so a window line's own
`pack` value never routes); a second block line binding the same row refuses `duplicate_binding`; an identity
missing on its owner leaves the key unresolved; the id tables come only from the pinned sealed configs (12 extraction,
6 reported, 4 floor, 2 contrast; dumped and checked against the specs); a step-11 file written by another writer
refuses at the bytes (C2-C4) and a fill listed under another name is `step11_outputs_absent`. What remains
value-derived: block ids (F2, a wrong printed id, not a wrong number), the dominance `text` label (note), and `run_id`
keys, which the S3 union protects.

**3. G7.** No (F1). No family takes its universe from a registered role table; `run_phase_energy_j` takes L9's
listing and the recompute's `selected` flag; nothing prints `compared_in:`. The NEG-8 families do compare the
reference members by value, and a reference dropped from a NEG-8 line DISAGREEs (P2b). The regression the
amendment names fails at `1134bbf58` for cause A and passes for cause B.

**4. Over-refusal.** Cause B (`cmp-abba`) is fixed: the base fixture uses the registered spelling and exits 0
(`test_both_registered_spellings_bind_a7_a8`, A8). Cause A (NEG-8 reference rows) is not fixed (F1): the
full-size window will refuse with the same 162 rows. Nothing else found: all 323 real-shape numeric leaf paths
RC-CMP-4 listed at `e5ccf720b` still match a numeric-admitting rule at `1134bbf58`
(`rc-cmp-4-real-shape-census.out`, `census.py`); every identity-named key the producer prints
(`disclosures.py` `_item` calls, `removed_unit`, `stored_member_reason`, `central_band`) sits at an owner the table
lists or at the one attribute exception; every id printed at a gated position is in the registry. Not verifiable
here: the real window's string and boolean leaves and the 70 conditional line kinds. The full-size run at the
fixed head stays the readiness gate (RC-CMP-6 open issue 2) and cannot pass before F1.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| suite at `1134bbf58` | yes | no | no | `suite-1134bbf58.out`, 282 OK |
| round-3 and consult witnesses re-executed at both heads | yes | no (all refuse at the new head) | no | `consult-prototype-*`, `opus-probe-*`, `sol-probes-*` |
| own probes P1-P4 | yes | no (P3: wrong id with the right number) | yes (P1: G7 absent, RC-CMP-4 cause A still refuses) | `probes.py`, `probes-at-*.out` |
| real-shape numeric path census | yes | no | no (0 of 323 unmapped) | `rc-cmp-4-real-shape-census.out` |
