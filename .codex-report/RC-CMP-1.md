# RC-CMP-1 seat report

bridge-report/v1 · brief `main:docs/process_traces/2026-10-27-recompute-comparator/BRIEF.md` (341adaf41) ·
branch `lane/2026-10-27-recompute-comparator` cut from `origin/lane/2026-10-14-independent-recompute` (9ca87bcee).
Synthetic data only; no real block-5/6 or BYTES archive, export or key directory was opened.

## SUMMARY

DONE (A1-A7 met), with three items for the lead and Ed under NEEDS_RULING. The main one: which bar set binds block 5's release is not decided here.

- **A6 result:** L9's full-size synthetic dry run completed with every step `ok`
  (`completed_without_tooling_refusal: true`, driver code 0, record sha256 `c3da27d8…e199d`). The comparison against the
  independent recompute on the same restored bytes gives **1,454 comparisons and 0 disagreements under both shipped
  bar sets**, across 17 families. All **841 step-11 leaf paths are mapped**: 217 to a compared family (value-checked),
  624 listed as uncovered with a reason. No disagreement needed classifying.
- **Agreement margin:** the largest observed difference is at double-precision noise: run energies 2.3e-13 J and floors
  3.9e-12 J. Under the S-13 placeholders the largest |difference|/bar is 7.8e-7. Under the coded bars it is 1.1e-7.
- **A5:** the recompute's stdout now carries STRUCTURE codes only, and stderr names only an exception type. A stdlib
  re-derivation of `derived/exclusions.json` from `derived/flags.jsonl` through the registered catalog **agrees for
  ALPHA, BETA and GAMMA** on the full-size window. The interpreter version (3.13.17) is recorded.
- **Tests:** `tests/independent_recompute` gives 148 tests OK (18 skipped: real-archive tests in synthetic-only mode).
  Of these, 34 are new comparator and hygiene tests, with a planted fault per family and a counterfactual for each.

**Side observation for L9 (not this seat's brief):** step 9b passed on this 4-vCPU VM. The full run was alone except
for this seat's light 27-29 s recompute run during step 1 and a 110 s unit-test run during step 5. That is evidence
for L9-2's candidate (a), host contention, behind the L9-1 9b refusals. Wall time was 9 h 30 min (steps 0-9 about
3 h 40 min, 9b about 1 h 50 min, 10 about 1 h 30 min, 11 about 2 h).

## ACCEPTANCE

| # | Criterion | Status | Evidence |
|---|---|---|---|
| A1 | Comparator reads L9 restricted outputs and recompute output; bars from a config, two bar sets shipped; exact families | PASS | `scripts/compare_b5_recompute.py` (`--bars`; `load_bars` refuses a family the config does not name, `bars_family_missing:<family>`). Bar sets: `tests/independent_recompute/bar_sets/recompute_coded_7e322b76.json` (1e-6 rel / 1e-6 abs J, W and ratios; p 1e-6 abs; counts exact; b_op relative only) and `s13_block6.json` (1 mJ per run phase energy; half a unit of the last printed digit). Exact families: `outcome_word`, `dominance_branch`, `p42_status`, `holm_order`, plus `kept_units` and `exclusions_rederivation`. Tests: `test_bars_come_from_the_config` and `test_per_key_override_sets_its_own_printed_precision`. |
| A2 | Missing or null = DISAGREE; refuses unless every step-11 fill or placement is mapped or listed uncovered | PASS | `Comparison.numeric` and `exact` record `missing_or_null`. `coverage()` refuses on a leaf no rule matches, on a leaf mapped to a family whose L9-side compared values do not include the leaf's value, or on an absent step-11 source. Tests: `test_missing_or_null_on_either_side_disagrees`, `test_unmapped_step11_fill_refuses`, `test_mapped_leaf_whose_value_was_not_compared_refuses`, `test_mapping_to_a_family_with_no_comparison_is_not_coverage`, `test_absent_step11_output_refuses`. |
| A3 | Planted-fault tests: one per numeric family, one per categorical family, one missing-value, one unmapped-fill; each fails without the check | PASS | `tests/independent_recompute/test_comparator.py`: 11 numeric (`test_planted_run_phase_energy` … `test_planted_count`, `_descriptive_ratio`, `_per_token`) and 6 categorical (`_outcome_word`, `_dominance_branch`, `_p42_status`, `_holm_order`, `_kept_units`, `_exclusions_rederivation`). Each moves one value by 2x the bar (or one word), asserts exactly `{family: 1}` failing, then disables that check (bar to infinity, exact match made lenient, missing-skipping, catch-all rule, path-only coverage) and asserts the fault passes. |
| A4 | Public output: per-family pass/fail counts only; differences to the restricted folder | PASS | stdout is one line: `bar_set`, `families={family:{fail,pass}}`, `step11_unmapped=N`, `step11_absent=…`. stderr is a structure code only. Values, differences and bars go to `--restricted-out`. Test: `test_public_stdout_carries_counts_only` (no decimal number on stdout). |
| A5 | Recompute stdout and stderr structure-only; stdlib exclusion re-derivation compared to `exclusions.json`; interpreter recorded | PASS | `scripts/independent_recompute_b5.py`: stdout flag counts only for codes with blinding STRUCTURE. `guarded_main` prints `error: internal <Type>`. `rederive_exclusions` plus `Window.check_exclusions` produce `exclusions_rederivation_mismatch`, a STOP code, so a disagreement stops the comparison. Output `interpreter` and stdout `python=`. Tests: `tests/independent_recompute/test_hygiene.py` (6). Full-size window: `exclusions_rederivation={"ALPHA":"agrees","BETA":"agrees","GAMMA":"agrees"}`. |
| A6 | Full-size synthetic agreement run; per-family counts; every disagreement classified | PASS | See A6 RUN below: 0 disagreements under both bar sets, so there is nothing to classify. The non-comparison flags and fixture features are classified there. |
| A7 | No file outside WRITE_SCOPE; no import of L9 code | PASS | `git diff --name-only origin/lane/2026-10-14-independent-recompute HEAD` lists only the scripts, `tests/independent_recompute/**` and this report. `grep -nE "b5_analysis" scripts/independent_recompute_b5.py scripts/compare_b5_recompute.py` matches nothing (exit 1). The comparator imports only argparse, hashlib, json, math, pathlib, re and sys (`test_no_l9_import`). The L9 worktree's tracked files are unchanged (only its untracked `.scratch-s10f/` cache). |

## A6 RUN (full-size synthetic window)

- **L9:** read-only worktree of `lane/2026-10-27-l9-2` at `6af08b78002652e782379b87facf7bc601f30fac`. The window was
  restored with L9's own fixture (`tests.b5_analysis.fixtures_s10.chain_fixture`, `JW_B5_S10_REAL_PROGRAMS=1`, cache
  under the worktree's `.scratch-s10f/tmp`). The dry run went through L9's own joined harness
  (`tests.b5_analysis.joined_s10.JoinedHarness(...).execute()`), exactly as `test_dry_run.JoinedRunTests` does.
  Driver: the scratch script `l9_full_dry_run.py` (not committed: it imports L9 code and is outside WRITE_SCOPE). Run
  started 2026-10-27 23:12:52 UTC and ended 2026-10-28 08:42:37 UTC. Steps 0, 1, 2, 3, 3b, 4 (alpha and beta,
  `p42_floor_cells_only`), 5, 8, 6, 9, 9b, 10 (alpha and beta) and 11 were all `ok`.
- **Recompute:** `scripts/independent_recompute_b5.py --alpha/--beta/--gamma <restored archive> --claim-runs-* --bound-runs-* --member-detail`
  on the same restored bytes. It took 29 s and exited 0. Output sha256 `602bd8f0…49a002e2` was byte-identical across
  two independent restores of the window. The input manifest (20,317 files, the archive plus claim and bound roots)
  was hashed at the time of the run: sha256 of the manifest `569381e4…85b8f5c6`.
- **Comparator:** `scripts/compare_b5_recompute.py` at sha256 `263b74fa…44e5a15761`. Exit 0 for both bar sets.
  Restricted outputs: `recompute_coded_7e322b76.json` (`f091f6ca…`) and `s13_block6.json` (`dd4db9af…`), kept in the
  seat's scratch, never committed.

| Family | Pass | Fail | Largest \|diff\|/bar (coded / S-13) |
|---|---|---|---|
| run_phase_energy_j | 786 | 0 | 6.0e-10 / 2.3e-10 |
| floor_j | 141 | 0 | 1.1e-7 / 7.8e-7 |
| floor_gate_j | 28 | 0 | 8.8e-8 / 7.8e-7 |
| dominance_ratio | 12 | 0 | 9.2e-8 / 1.9e-9 |
| reported_cell_j | 120 | 0 | 2.8e-8 / 8.5e-9 |
| contrast_j | 118 | 0 | 2.3e-8 / 1.6e-8 |
| contrast_p | 44 | 0 | 4.4e-9 / 8.9e-11 |
| descriptive_ratio | 6 | 0 | 2.0e-10 / 4.4e-12 |
| per_token_j | 10 | 0 | 1.4e-10 / 2.8e-10 |
| b_op_s | 8 | 0 | 0 / 0 |
| count | 112 | 0 | exact |
| outcome_word | 50 | 0 | exact |
| dominance_branch | 1 | 0 | exact |
| p42_status | 8 | 0 | exact |
| holm_order | 1 | 0 | exact |
| kept_units | 6 | 0 | exact |
| exclusions_rederivation | 3 | 0 | exact |

**Disagreement list:** none, under either bar set.

**Classified non-disagreements (not comparisons):**

- **Fixture artefact.** The recompute raised `archive_file_missing` (19), `trace_plist_missing` (3, not stopping)
  and `member_pre_bound_missing` (3). Every one is on a member L9's fixture plants as aborted or truncated
  (`d117fq31p7-df-ph-decode-abs-r01`, `d117fq38-df-ph-decode-abs-r01`,
  `d117c-…-decode-contrast-b01-a1`, `…-b01-a1` summaries, `neg8-window-start-r1`). Those members are excluded on both
  sides and are detail-only in the recompute (9 detail runs not compared: 6 `status_not_succeeded`, 3
  `trace_plist_missing`). They are intended faults in the fixture, not disagreements.
- **Fixture artefact.** The synthetic window has no meter stream (`meter_absent` ×3), so the whole-machine lines are
  not exercised.
- **Definition differences, absorbed in the mapping and named here so a reviewer can check them:**
  - L9 `corner_widened_guarded_floor_j` is compared to the recompute's guard × corner, and L9
    `drift_widened_unguarded_floor_j` to operative-unguarded + allowance.
  - L9's `direction` is null unless an outcome is `direction_supported`; the recompute always signs dbar. The
    comparator compares "none" unless supported.
  - L9 `df` is compared to the recompute's n − 1.
  - LOO `floor_status` is compared to the recompute's `above_floor`.
  - Holm order is the contrast ids sorted by raw p, ties broken by id.

**Coverage of step 11** (fill input `outputs/<sha>-results-fill-input.json` and disclosure record
`disclosures/<sha>.json`): 841 leaf paths, 217 covered, 624 uncovered. The uncovered paths fall into these groups:

- 430 window-structure lines the recompute does not re-derive (flag tallies, hazards, monitor, battery, ledger,
  tripwires, and NEG-8 bracket internals such as admissible sets, standard errors, the idle-subtracted companion and the
  drift-bound artifact);
- 77 identities, labels and provenance;
- 36 rendered-text leaves;
- 24 L9-internal consistency booleans and status words;
- 15 removed-unit codes and families (exclusions are compared through the re-derivation);
- 42 registered definitions and constants.

The `released.txt` and `unreleased.txt` files are the line texts of the disclosure record, so they fall under the
rendered-text group (synthesis item 2(b)(iii)). The full per-leaf map is in the restricted output, under
`coverage.leaves`.

## FILES CHANGED

- `scripts/independent_recompute_b5.py`: A5 (structure-only streams, `rederive_exclusions`, `check_exclusions`,
  interpreter record, two new codes: `exclusions_rederivation_mismatch` (STOP and STRUCTURE) and
  `exclusions_rederivation_unavailable` (STRUCTURE)).
- `scripts/compare_b5_recompute.py`: new comparator.
- `tests/independent_recompute/test_hygiene.py`, `test_comparator.py`: new.
- `tests/independent_recompute/test_archives.py`: one expected flag list gains `exclusions_rederivation_unavailable`
  (that fixture has no harvest exclusion inputs).
- `tests/independent_recompute/bar_sets/recompute_coded_7e322b76.json`, `s13_block6.json`: the two bar sets.
- `.codex-report/RC-CMP-1.md`: this report.

## DECISIONS I MADE

1. **Bar-set location.** The two bar sets live under `tests/independent_recompute/bar_sets/` because WRITE_SCOPE has
   no `configs/` path. A release copy belongs in a sealed config location; that move is for the lead.
2. **S-13 printed precision.** The S-13 `printed_decimals` are placeholders taken from L9's own step-11 disclosure
   renderings on this window: J 5 decimals, se 6, R and the descriptive ratio 4, b_op and b_sens 6, J per token 6,
   t* 3, p 4 (p is not rendered there).
3. **Per-key overrides.** Per-key overrides (`keys: [{match, …}]`) were added so a field printed at its own precision
   (se) gets its own bar.
4. **Value-checked coverage.** A step-11 leaf mapped to a family counts as covered only if its value equals an L9-side
   value that family compared; this catches an adapter that copies the wrong number. The check is by value, so a
   coincidental equal value can pass: on this fixture the idle-subtracted NEG-8 terms equal the gross ones. Window
   lines are therefore mapped field by field, not by pattern.
5. **Extra comparisons.** Comparisons were added beyond the brief's minimum where the recompute already computes the
   quantity. The disclosure lines include cross-window, battery-assist "without", the descriptive ratio and J per
   token, the NEG-8 bound terms, and the reference and corpus counts. The p42 cells in the sensitivity and projection
   lines are compared as a p42 status.
6. **Re-derivation inputs.** The exclusion re-derivation reads the harvest's `withheld/exclusion-inputs.json` (roster
   and spans), the archive's `derived/flags.jsonl`, and the analysis checkout's registered catalog. A missing input
   is flagged `exclusions_rederivation_unavailable` (STRUCTURE, not stopping) so pre-existing small fixtures still
   run. The comparator counts anything but `agrees` as a disagreement.
7. **Restart handling.** The dry run was relaunched twice after container restarts killed it. Both restarts
   coincided with this session going idle, so the seat kept the turn active for the third run, which completed.

## OPEN ISSUES

1. **Coverage gaps for the release reviewer.** 624 uncovered step-11 leaves are listed with reasons. The largest
   group is window structure and NEG-8 bracket internals, which only L9 computes. Rendered text is not checked by this
   comparator (synthesis 2(b)(iii)).
2. **Meter line not exercised.** The whole-machine meter line is not exercised on this fixture (no meter stream), so
   the known 0.020 J fit-method difference (commit 7e322b767) did not appear. It needs either a fixture with a meter
   stream or the pending fit-method ruling.
3. **Families mix printed precisions.** A family mixes quantities printed at different precisions; per-key overrides
   exist, but only se is overridden so far.
4. **Environment, not chased.** `/bin/zsh` was not built, because building zsh from GitHub source was refused by this
   session's permission classifier. No recompute or comparator test references zsh. `/opt/homebrew/bin/python3.13`
   is linked to `/usr/bin/python3.13`. The clone was unshallowed for L9 step 10's ordering check. Two container
   restarts killed the first two dry runs; the third completed.
5. **Lead notice.** The lead notice (2026-10-27, in-session) says the laptop copy of session 015ASG1T is the only
   lead. No instruction from any other session was received.
6. **Follow-on reviews.** Per the brief, two executing reviews (Sol 6.1 xhigh fast and Opus 5.5) are to be launched
   together after this job; this seat did not launch them.

## NEEDS_RULING

1. **Which bar set binds block 5's release.** RUN_STATE item 37 (ii) says "a tolerance fixed before release". The
   recompute's coded bars (7e322b76: 1e-6 relative, 1e-6 absolute for rho, exact counts) and block 6's S-13 (1 mJ per
   run phase energy, half a unit of the last printed digit) conflict (critique item 12). Both are shipped and both
   pass on this window by more than six orders of magnitude, so the synthetic run cannot choose between them. The
   lead and Ed rule.
2. **Block-5 printed precision.** If S-13 is chosen, the printed digits per quantity are needed: there is no block-5
   results template. The S-13 file uses L9's current disclosure renderings as placeholders.
3. **Who reads the uncovered leaves at release.** The 624 uncovered step-11 leaves need a named owner at the release,
   presumably the post-release reader of synthesis item 2(b).
