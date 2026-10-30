STATUS: DONE

# L9-STEP4-5: the L9-STEP4-4 delta-review fixes

This is seat L9-STEP4-5. The lead is joulewise-28 and the branch is `lane/2026-10-30-l9-step4-reasons`. The code commit
is `b255ad1fe`, on top of `81155d419`.

I used synthetic data only. I did not open or search any real block-5, block-6 or BYTES data. I did not change
`joulewise/**` or `scripts/**`. Evidence is in `.codex-report/l9-step4-5/`.

## SUMMARY

I applied both delta reviews: Opus (ACCEPT_WITH_FIXES) and Fable (ACCEPT).

- **Claim-gate proof.** It now scans all 167 `joulewise/**/*.py` modules and `scripts/extract_detection_floors.py`,
  not only the generator's eleven.
  - It skips only the two claim-gate modules, and it checks that each of them still contains the literals.
  - It keeps the `stop_if_member_code_on_kept_unit` argument exemption.
  - It must see `paired_block_incomplete` at least once as a stop argument, so it cannot pass vacuously.
- **Behavioural test.** The new module `tests/b5_analysis/test_step4_member_codes.py` runs the real `extract_cells`
  with kept units on synthetic bundles. The precheck, the forwarding filter and `_evaluate_member` are not patched.
  - Each of the three plan-named codes is the sole `refusal_reasons` entry of the refused target cell. For each,
    `classify_step4_exit(1, report, spec) == 'extraction_cell_r3_refusal'`.
  - A stored non-reducer precheck reason (`paired_block_incomplete`, `fixed_n_plan_incomplete`, or an unlisted code)
    turns into `window_evidence_precheck_missing`.
  - A verified cap-hit is excluded at its slot, and `cooldown_cap_hit` never becomes a cell reason.
- **Emission pins.** Each pin is now one whole statement, matched as AST against the module's statements, and its
  string literals must be exactly `{code}`.
- **Ruling string.** It names the L9-STEP4-4 amendment and the tooling-origin note (Opus F3). `RULING` and the JSON
  changed together, and the regeneration test is green.
- **p42 loop.** It now covers the three plan-named codes, alone and together with a tooling code.
- **Mutants.** I reran every L9-STEP4-4 reviewer mutant (Opus 14, Fable 12) and 5 new ones. All 31 are killed,
  including the four that survived before: Opus M11 and M12/b, Fable M8, M9 and M10.
- **Whole directory.** `tests/b5_analysis` passes: `Ran 1035 tests`, `OK (skipped=13)`, no `ERROR:` or `FAIL:` lines (1029 at L9-STEP4-4 plus the 6 new tests).

## Finding by finding

| Finding | Change | Shown by |
|---|---|---|
| Opus F1 + Fable F3: claim-gate proof scoped to the 11 modules, and could pass vacuously | `test_R3_claim_gate_member_codes_cannot_reach_a_step4_cell` walks every joulewise module plus the extractor CLI. It allowlists `analysis_engine/__init__.py` and `claims.py`, keeps the stop-argument exemption, asserts `seen['paired_block_incomplete'] >= 1` and `seen['fixed_n_plan_incomplete'] == 0`, and requires the table's modules to be a subset of the scan | O11 (Opus M11) killed by this test. F12 (both stop sites deleted) now fails this test as well as regeneration. N1 (literal in `dominance_closeout.py`) and N2 (literal in the CLI) killed |
| Opus F2 + Fable F1: no behavioural proof that the codes reach a cell, or of the precheck filter | New `test_step4_member_codes.py`: missing precheck root, stored non-reducer reasons, `idle_window_suspect: true` on an `energy_request_j` cell, unverified campaign cooldown (raw-artifact sha mismatch, `verified` False). Each asserts the cell's `refusal_reasons == [code]`, the member's reasons `== [code]`, and the R3 class. The other cell stays extractable, and the controls extract | O12, O12b, O12c (Opus forwarding-filter variants) killed. F9 (Fable's `inputs.py:4067` filter mutant) killed by the stored-reasons test. N5 killed |
| Fable F5: `cooldown_cap_hit` filter untested | `test_verified_cap_hit_is_filtered_from_cell_reasons`: a verified cap-hit on r06 (legacy path, via `ArithmeticTests.cap_hit`) leaves the cell extractable, with r06 excluded and `cooldown_cap_hit` absent from its reasons | F10 killed |
| Fable F2: emission pin was a substring check | `emission_statements` parses the pin as one statement and requires an `ast.dump`-equal statement in the module. The pin's string literals must equal `{code}` | F8 (wrong-site pin to `_unknown`) killed. N3 (pin to a sibling code's site) and N4 (fragment of a statement) killed |
| Opus F4 + Fable F4: JSON ruling did not record the -4 amendment | `step4_rule.ruling` in `RULING` and in the JSON names the L9-STEP4-4 lead ruling (2026-10-30), the plan 2.2 bullet 3 plan-named codes, and Opus F3 (see below). The regeneration test is byte-exact | `test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file` passes |
| Opus F3: tooling-origin causes route to R3 | Recorded in the ruling string: "A tooling-origin cause of one of these codes also routes to R3 (an Ed ruling), which is stop-side." | Text only; NEEDS_RULING 1 |
| Opus F5: p42 loop used only one R3 code | `test_R2_p42_cell_reasons_are_irrelevant_to_the_registered_exit` adds each plan-named code alone, and all three plus a tooling code | passes; O6 still killed (10 failures) |
| Fable F6: exit 0 trusted | Not changed; pre-existing | OPEN ISSUES 1 |

The new ruling string:

> L9-STEP4-3 lead ruling, RUN_STATE items 132-133 and 138, made blind; amended by the L9-STEP4-4 lead ruling
> (2026-10-30): the member-level codes plan section 2.2 bullet 3 names that reach a step-4 cell
> (window_evidence_precheck_missing, campaign_cooldown_evidence_missing, idle_window_suspect) are r3. A tooling-origin
> cause of one of these codes also routes to R3 (an Ed ruling), which is stop-side.

## Mutants

The script is `l9-step4-5/mutants.py` and the log is `l9-step4-5/mutants.txt`. Each mutant was applied in a worktree
at `b255ad1fe` and then reset. Each run used four targets: `test_step4_reason_table`, `test_step4_exit_classes`,
`test_step4_member_codes` and r14. The unmutated baseline is `Ran 41 tests`, `OK`.

Labels: O = the Opus review's M-numbers, F = the Fable review's M-numbers, N = new in this seat.

| # | Mutant | At L9-STEP4-4 | Now | Failing tests (unique) |
|---|---|---|---|---|
| O1 | JSON drops `idle_window_suspect` | killed | killed | 5 failures |
| O2 | JSON+RULING drop `idle_window_suspect` | killed | killed | 4 |
| O3 | JSON+RULING add `paired_block_incomplete` | killed | killed | 2 |
| O4 | JSON+RULING+pin add `cooldown_cap_hit` | killed | killed | 4 |
| O5 | JSON+RULING add `idle_window_suspect_unknown` | killed | killed | 3 |
| O6 | r3 checked before the p42 exit | killed | killed | 10 (r14 included) |
| O7 | only the first reason checked | killed | killed | 3 |
| O8 | precheck appends `paired_block_incomplete` | killed | killed | claim-gate test; idle behavioural test |
| O9 | `fixed_n_plan_incomplete` as stop argument | killed | killed | regeneration; claim-gate test |
| O10 | `campaign_cooldown_evidence_missing` emission indirect | killed | killed | pin test; cooldown behavioural test |
| O11 | claim-gate literal in `calibration_bracketing.py` | **survived** | **killed** | claim-gate test |
| O12 | filter drops `window_evidence_precheck_missing` | **survived** | **killed** | missing-root and stored-reasons tests |
| O12b | filter drops `idle_window_suspect` | **survived** | **killed** | idle behavioural test |
| O12c | filter drops `campaign_cooldown_evidence_missing` | killed (outside step-4 tests) | killed | cooldown behavioural test |
| F1 | JSON drops `window_evidence_precheck_missing` | killed | killed | 9, r14 included |
| F2 | consistent partial revert of `idle_window_suspect` | killed | killed | 4 |
| F3 | `idle_window_suspect_unknown` widened in | killed | killed | 3 |
| F4 | `paired_block_incomplete` widened in, pinned | killed | killed | 3 |
| F5 | precheck appends `paired_block_incomplete` | killed | killed | claim-gate; missing-root |
| F6 | stop code passed by keyword | killed | killed | claim-gate (fails closed) |
| F7 | classifier drops the three codes at runtime | killed | killed | 14, all four behavioural R3 tests |
| F8 | pin `idle_window_suspect` to the `_unknown` site | **survived** | **killed** | pin test |
| F9 | precheck forwards non-reducer stored reasons | **survived** | **killed** | stored-reasons test |
| F10 | `cooldown_cap_hit` filter removed | **survived** | **killed** | cap-hit filter test |
| F11 | r14 expects tooling | killed | killed | r14 |
| F12 | both stop sites deleted | killed (regeneration only) | killed | regeneration; claim-gate (non-vacuity) |
| N1 | `fixed_n_plan_incomplete` literal in `dominance_closeout.py` | n/a | killed | claim-gate |
| N2 | `paired_block_incomplete` literal in the extractor CLI | n/a | killed | claim-gate |
| N3 | pin to a sibling code's emission | n/a | killed | pin test |
| N4 | pin is a fragment of the real statement | n/a | killed | pin test |
| N5 | missing root emits `idle_window_suspect_unknown` | n/a | killed | missing-root test |

The script's first pass stopped at O11. Its replacement helper required exactly one occurrence, but Opus M11 replaces
the first of six. I reran O11 through N5 with a first-only replacement, which is what Opus's script did. The log
records this.

## VERIFICATION

The command ran from `/home/user/JouleWise` at `b255ad1fe`, on an unshallowed clone and a clean tree (`git status`
empty; the evidence directory was moved out during the run). TMPDIR is under /tmp, outside the checkout, with no
float-like token:

```
TMPDIR=/tmp/l9s5full JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .
```

Exact tail (`l9-step4-5/full_run_tail.txt`):

```
----------------------------------------------------------------------
Ran 1035 tests in 3875.796s

OK (skipped=13)

real	65m4.268s
user	56m12.685s
sys	6m38.854s
EXIT 0
```

The targeted modules at the same head: `Ran 41 tests`, `OK` (the reason-table, exit-class and member-code modules
plus r14).

## FILES CHANGED

- `tests/b5_analysis/test_step4_member_codes.py` (new): the behavioural tests.
- `tests/b5_analysis/test_step4_reason_table.py`: the repo-wide claim-gate proof, the AST-exact emission pins, and the
  `RULING` ruling string.
- `tests/b5_analysis/test_step4_exit_classes.py`: the `PLAN_NAMED` tuple and the p42 loop.
- `configs/analysis/b5/step4_reason_classes.json`: only `step4_rule.ruling` changed, regenerated as generator output
  plus `HEADER` plus `RULING`. `mask`, `tooling`, `r3`, `modules` and the generator sha are unchanged.
- `.codex-report/L9-STEP4-5.md` and `.codex-report/l9-step4-5/` (`mutants.py`, `mutants.txt`, `full_run_tail.txt`).

## DECISIONS

1. **Head.** The brief named head `a7e00c9f7`. The branch was at `81155d419`, a report-only commit after it that
   touches only `.codex-report/L9-STEP4-3.md`. I built on `81155d419` and did not touch that file.
2. **What "seam-free" covers.** The behavioural tests reuse the kept-units arithmetic corpus and its
   `arithmetic_seams()`: strict validator, whole-window refusals, drift allowances and consumption session.
   - Without those seams, a summary-only synthetic bundle refuses `bundle_strict_invalid` before any member code is
     computed.
   - None of the seams touches the precheck, the forwarding filter, `_evaluate_member` or the cooldown join. Those
     are the paths the reviews asked to exercise, and the reviewers' mutants of them are killed.
   - Nothing injects reasons. This is unlike r14's `_evaluate_member` wrapper.
3. **Fable F1's form.** Fable suggested calling `window_evidence_precheck` directly. I ran the stored-reasons case
   through `extract_cells` instead, which also covers the extractor's forwarding. It kills F9.
4. **Cap-hit filter path.** The filter test uses the legacy path (`kept_units=None`). On a kept unit a verified cap-hit
   raises `member_code_on_kept_unit` before cell reasons matter (existing r4). The legacy path is where the filter
   alone decides whether the cell is refused. F10 is killed there.
5. **Allowlist check.** The allowlist is checked to be live: each allowlisted module must still contain a claim-gate
   literal. The scan is checked to cover the generator's eleven modules.
6. **Ruling text.** It is one sentence appended to the existing string, so the L9-STEP4-3 provenance stays verbatim.

## OPEN ISSUES

1. Fable F6 (pre-existing, unchanged): exit 0 is trusted (`steps.py:58-59`). Every code classifies `ok` at exit 0.
   The extractor returns 1 on any refused cell (`scripts/extract_detection_floors.py:268-287`). I recorded this only.
2. The claim-gate proof does not scan `scripts/run_campaign.py`, which names `paired_block_incomplete` at
   `:8846-8865`. Opus places it off the step-4 path. The brief limits the scan to `joulewise/**` plus the extractor CLI.
3. Carried forward from L9-STEP4-4: NEEDS_RULING 1-3 and open issues 1-2 of `.codex-report/L9-STEP4-4.md`. This seat
   does not change them.

## NEEDS_RULING

1. Opus F3 (extends L9-STEP4-4 NEEDS_RULING 3), now recorded in the ruling string. These now go to an Ed ruling
   rather than fix-and-rerun:
   - the five tooling-origin causes of `window_evidence_precheck_missing`: missing root, malformed `reasons`,
     non-vocabulary reason, non-boolean `eligible`, legacy input;
   - a cooldown-join wiring fault surfacing as `campaign_cooldown_evidence_missing`.

   This is plan-literal and stop-side. If the lead wants a tooling-origin cause to keep the fix-and-rerun route, the
   extractor would need to emit a distinct code, which is out of this seat's scope.
