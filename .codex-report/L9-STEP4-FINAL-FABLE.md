VERDICT: ACCEPT

# L9-STEP4-FINAL-FABLE: cold final pass (gate 4) on `lane/2026-10-30-l9-step4-reasons` at `deda94037`

Seat L9-STEP4-FINAL-FABLE, branch `review/2026-10-30-l9-step4-final-fable` from `deda94037`, unshallowed clone.
Lead: joulewise-28. Synthetic data only; I did not open or search any real block-5, block-6 or BYTES data.
Evidence is in `.codex-report/l9-step4-final-fable/`.

I read the whole lane diff `origin/main...deda94037` cold (`joulewise/b5_analysis/steps.py`,
`configs/analysis/b5/step4_reason_classes.json`, `configs/analysis/b5/dry_run_refusal_classes.json`,
`tests/b5_analysis/**`; `dry_run.py` is not touched), then the newest delta `81155d419..6ce02feba` (L9-STEP4-5).
The four prior reviews (L9-STEP4-3 and -4, Opus and Fable) and the lane's own reports were read as claims and
re-executed where they bear on the five questions.

## Summary

- **No step-4 exit-1 report reaches `ok`, the registered p42 exit or an outcome class except as plan §3.1 allows.**
  At exit 1 the classifier returns only the ten `STEP4_*` constants; `ok` needs exit 0; the p42 exit needs every
  refused cell to be a p42 floor cell of the sealed spec and an empty `spec_membership_refusals`; the outcome registry
  is `['dominance_ratio_zero_denominator']` and no step-4 constant is in it. An independent 200,000-report
  randomized invariant check found zero violations (`fuzz_step4.txt`). Both real block-5 floor specs identify exactly
  their two `prefill-p42` cells under the classifier's family-token rule.
- **The eleven R3 codes are each tied to a plan §2.2 sentence**, five of them literally (bullet 2's minimum rule,
  bullet 3's three named member codes) and six (the forwarded reducer codes) through the lead's recorded reading of
  bullet 3 (RUN_STATE items 132-133, 138, 143). Every non-R3, non-mask code, listed or unlisted, is
  `extraction_cell_tooling_refusal`, a cure-and-rerun stop. The three carried NEEDS_RULING items are cure-route
  questions only; every reading of them stops the run.
- **The L9-STEP4-5 tests bind behaviour.** I reran 13 of the lane's 31 mutants at `deda94037` (the two classifier
  mutants, the two scan-scope mutants, three forwarding-filter mutants, the four survivors of L9-STEP4-4 and the two
  pin mutants): all 13 killed, with the same failing tests the lane logged. The member-code tests run the real `extract_cells` with the precheck, the
  forwarding filter and `_evaluate_member` unpatched; the four seams of `arithmetic_seams()` (strict validator,
  whole-window refusals, drift allowances, consumption session) read no member reason.
- **L9-STEP4-5 changed nothing outside tests and the ruling string.** `git diff 81155d419..6ce02feba -- joulewise
  scripts configs` is one line of `step4_rule.ruling` (`delta_scope.txt`); `mask`, `tooling`, `r3`, `modules` and the
  generator sha are unchanged, and the regeneration test is green. The merge `deda94037` equals the automatic
  merge tree of its parents (no manual edits).
- **Whole `tests/b5_analysis` directory at `deda94037`:** `Ran 1035 tests`, `OK (skipped=13)`, exit 0, no `ERROR:` or `FAIL:` line (exact tail below).

The findings are two nits and three notes. None changes a classification, and none is a path to a pass.

## Findings (ranked)

**F1 (nit, provenance). The registered ruling string folds an unruled consequence into the L9-STEP4-4 ruling.**
`configs/analysis/b5/step4_reason_classes.json:1981` (and `RULING` at `tests/b5_analysis/test_step4_reason_table.py:57-61`)
reads "... amended by the L9-STEP4-4 lead ruling (2026-10-30): the member-level codes ... are r3. A tooling-origin
cause of one of these codes also routes to R3 (an Ed ruling), which is stop-side." The lead ruling in RUN_STATE item
143 is the first sentence only. The second sentence is true of the classifier (it cannot see a code's origin) and is
stop-side, but `.codex-report/L9-STEP4-5.md` itself lists it as NEEDS_RULING 1, so the registered file presents as
ruled what the lane says is pending. Fix (one of): the lead confirms the sentence in the RUN_STATE merge entry, which
makes the string accurate as written; or reword it to "Consequence (L9-STEP4-5, Opus F3, pending ruling): ..." in
`RULING` and the JSON together (the regeneration test forces both). Not blocking: behaviour and cure route are
unchanged either way.

**F2 (nit, test strength). The claim-gate scan's non-vacuity bound is weaker than the sites it relies on.**
`tests/b5_analysis/test_step4_reason_table.py:247` asserts `seen['paired_block_incomplete'] >= 1`; Fable F3 of
L9-STEP4-4 asked for `== 2`, the two kept-unit stop sites at `joulewise/analysis_engine/inputs.py:3590` and `:3746`.
My mutant X1 deletes the first stop site only: the four step-4 targets stay green (`Ran 41 tests`, `OK`), so the bound does not pin the second site. Fix: `self.assertEqual(seen['paired_block_incomplete'], 2)`,
or pin the two line numbers. Stop-side and outside the step-4 path (the stops belong to the claim gate), so a nit.

**F3 (note, pre-existing, outside the delta). Exit 0 is trusted.** `joulewise/b5_analysis/steps.py:58-59` returns
`ok` at exit 0 without reading the cells. Safe today because `scripts/extract_detection_floors.py:268-287` returns 1
whenever any cell is refused or any member is omitted, and recorded by every prior review and the lane's open issue 1.
A two-line hardening inside this lane's own file would close it for good:

```python
    if exit_status == 0:
        if not (isinstance(report, Mapping) and isinstance(spec, Mapping)):
            return "refused"
        cells = report.get("cells")
        if (not isinstance(cells, list) or report.get("spec_membership_refusals")
                or any(not isinstance(c, Mapping) or c.get("extractable") is not True for c in cells)):
            return "refused"
        return "ok"
```

The driver already turns a `refused` at exit 0 into exit 2 (`dry_run.py:798`), so no new code is needed there. Optional.

**F4 (note, pre-existing). Unused import.** `joulewise/b5_analysis/disclosures.py:25` imports `classify_step4_exit`
and never uses it (Opus F4 of L9-STEP4-3). Outside the delta; remove when the file is next touched.

**F5 (note, stated limits of the proofs).** The claim-gate scan covers every `joulewise/**/*.py` plus the extractor
CLI, not `scripts/run_campaign.py` (which names `paired_block_incomplete` off the step-4 path) and not a literal built
by concatenation; the emission pins prove a statement exists, not that it is reached at step 4. For the three
plan-named codes reachability is proven behaviourally by `test_step4_member_codes.py`; for the eight mask R3 codes it
rests on the pins plus the L9-STEP4-2/3 audits. All of these are stop-side limits.

## Answers to the five questions

### (1) Can any step-4 exit-1 report reach `ok`, the registered p42 exit or an outcome class except as §3.1 allows?

No. Read cold from `joulewise/b5_analysis/steps.py:48-110` and `joulewise/b5_analysis/dry_run.py:787-801`:

- `ok` is returned only at exit 0 (`steps.py:58-59`); every exit-1 return is one of the ten `STEP4_*` constants,
  and `"refused"` is reserved for a non-integer or non-0/1 status (`:56-61`), which the driver records as
  `unclassified_refusal`, a stop.
- The p42 exit needs `targets` empty (`:99-101`): every refused cell must be an `absolute` or `comparative` cell whose
  sealed `condition_family_id` carries the token `p42`, and `spec_membership_refusals` must be empty (`:68-69`), which
  is at least as strict as §3.1's "no kept member was omitted from the spec" (the extractor lists every campaign
  member omitted or unattributable, `floor_extraction.py:3397-3416`). On both real block-5 floor specs
  (`configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/extraction_spec.json`) the rule selects exactly the two
  `df-ph-prefill-p42-*` cells of six; the `p2048` and `decode` cells are not p42. The spec comes from the sealed
  archive and must equal the checkout copy byte for byte (`dry_run.py:627-633`).
- The `r3` lookup runs after the exit-0, non-0/1 and p42 returns, so the table can only turn the final tooling return
  into the R3 return (`:102-110`). Both are registered under `tooling_refusal` in `dry_run_refusal_classes.json`;
  the outcome registry is `['dominance_ratio_zero_denominator']` alone; `floor_cell_not_extractable` is gone from the
  code and both registries.
- `step_record` (`steps.py:135-152`) gives `ok` at exit 1 only for `registered_exit == 'p42_floor_cells_only'`,
  which the driver sets only for that classification.

Independent randomized check (`fuzz_step4.py`, 200,000 five-cell reports, exit status in {0,1,2}, reasons drawn from
R3, non-R3 mask, 200 tooling codes, unlisted, empty, case and whitespace variants, malformed containers, non-boolean
`extractable`, missing keys, membership refusals): zero violations of the invariants "exit 1 never `ok`/`refused`/an
outcome code", "p42 exit only with no refused non-p42 cell and no omission", "R3 iff an R3 code on a refused non-p42
cell", "status `ok` only for the p42 exit". Histogram in `fuzz_step4.txt`.

Record-level: T8/T8b/T8c (`tests/b5_analysis/test_dry_run.py:551-586`) run the driver and assert the step-4 row is
`('tooling_refusal', <class code>)`, run exit 2, step 5 not called, and that no extractor reason string appears in the
record, stdout or stderr. Note (sanctioned, not a finding): the R3/tooling split releases one structure-only bit that
is a function of mask codes; item 132's orchestrator condition asked for exactly that split.

### (2) Is every R3 code justified by plan §2.2, and every non-R3, non-mask code a cure-and-rerun tooling stop?

The eleven `r3` codes, by justification:

| Codes | §2.2 basis | Strength |
|---|---|---|
| `kept_units_below_minimum`, `insufficient_members_after_exclusion` | bullet 2: "If an analysis program finds fewer ... the step goes to R3" | literal (over-inclusive at the producer: fires below 2 admitted, which includes tooling-origin shortfalls; Opus -3 F2, NEEDS_RULING 3) |
| `window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing`, `idle_window_suspect` | bullet 3 names them: "If one fires on a kept unit ... goes to R3" | literal (lead ruling, RUN_STATE 143); proven reachable by `test_step4_member_codes.py` |
| `insufficient_in_window_samples`, `cadence_ratio_below_threshold`, `clock_bound_exceeds_quarter_window`, `anchor_energy_envelope_exceeds_quarter_metric`, `instrument_calibration_stale`, `calibration_acceptance_bound_stale` | bullet 3's member rule, read as covering the reducer member codes the precheck forwards onto kept units (`inputs.py:4068-4069`, `floor_extraction.py:2238-2245`) | lead's reading (items 132-133, 138), not the bullet's literal list; three have non-§2.2 producers too (read error, session-level union; NEEDS_RULING 3) |

Nothing in `r3` is a code that only a code defect can produce, so no R3 code hides a fix behind a ruling that could
not also be a §2.2 disagreement. The reverse direction: of the 31 `REDUCER_REASON_CODES` the precheck forwards onto
kept units, 6 are mask codes (all R3), 23 are blind tooling codes (for example `thermal_pressure_elevated_in_window`,
`negative_power_sample`, `environment_admission_failed`) and 2 are in neither list; the 25 non-mask ones class as
`extraction_cell_tooling_refusal`. Under the same reading that makes the six R3, these could be R3 too. That is Opus
F1 of L9-STEP4-3 = NEEDS_RULING 1, which the lead sent to Ed as optional and non-blocking (item 143). The cooldown-cap
same-slot case on a kept unit stops earlier as `member_code_on_kept_unit` (exit 2, tooling; NEEDS_RULING 2). Each of
these is a cure-route question; every reading of it stops the run before step 5, so none can change an outcome.

Every non-R3, non-mask code (1898 blind tooling codes, the 2 unlisted reducer codes, any unlisted or malformed string)
is `extraction_cell_tooling_refusal` (`test_R2_tooling_only…`, `test_R2_an_unclassified_reason…`, my fuzz), and the
34 non-R3 mask codes are too (`test_R2_blind_mask_codes_outside_r3…`). Mask and tooling lists are generator output,
not read at step 4; the regeneration test keeps `HEADER + generator + RULING` byte-identical to the file.

### (3) Do the L9-STEP4-5 tests bind behaviour? (mutants rerun)

Baseline at `deda94037`: the four targets (`test_step4_reason_table`, `test_step4_exit_classes`,
`test_step4_member_codes`, r14) give `Ran 41 tests`, `OK` (`targeted_tail.txt`). Mutants were applied with the lane's
own `l9-step4-5/mutants.py` (run with `python3.13 -I`) in a detached worktree at `deda94037`, each reset afterwards
(`mutants_rerun.txt`):

| # | Mutant (lane label) | At L9-STEP4-4 | Here, at `deda94037` | Killing tests |
|---|---|---|---|---|
| O6 | classifier checks `r3` before the p42 exit | killed | killed (10) | p42-reasons, malformed-without-reasons, r3-on-p42, r14 |
| O7 | classifier checks only the first reason | killed | killed (3) | r3 precedence |
| O11 | `calibration_bracketing.py` emits `paired_block_incomplete` beside its pinned code | survived | killed (1) | claim-gate scan |
| O12 | forwarding filter also drops `window_evidence_precheck_missing` | survived | killed (4) | missing-root, stored-reasons |
| O12b | forwarding filter also drops `idle_window_suspect` | survived | killed (1) | idle behavioural |
| F7 | classifier drops the three plan-named codes at runtime | killed | killed (14) | r3 list, four behavioural, r14 |
| F8 | pin `idle_window_suspect` to the `_unknown` site | survived | killed (1) | AST pin |
| F9 | precheck forwards non-reducer stored reasons | survived | killed (2+1 error) | stored-reasons |
| F10 | extractor stops filtering `cooldown_cap_hit` | survived | killed (1) | cap-hit filter |
| F12 | both kept-unit stop sites deleted | killed (regeneration only) | killed (2) | regeneration, claim-gate non-vacuity |
| N1 | claim-gate literal in `dominance_closeout.py` | n/a | killed (2) | claim-gate scan |
| N2 | claim-gate literal in the extractor CLI | n/a | killed (1) | claim-gate scan |
| N4 | pin is a fragment of the real statement | n/a | killed (1) | AST pin |

13 of 13 killed; failure counts and test names match the lane's `l9-step4-5/mutants.txt` line for line.

Own mutant X1 (second worktree, `x1_tail.txt`): delete the first of the two `paired_block_incomplete` kept-unit stop
sites in `inputs.py` only. survives the 41 step-4 tests (`Ran 41 tests`, `OK`) (F2).

Reading of the new tests: `test_step4_member_codes.py` changes one synthetic member (r06) and asserts the refused
target cell's `refusal_reasons == [code]`, the member row's `reasons == [code]`, the other cell extractable, and the R3
class through `classify_step4_exit`; the stored-reasons case shows `paired_block_incomplete`,
`fixed_n_plan_incomplete` and an unlisted code all become `window_evidence_precheck_missing` through the real filter
at `inputs.py:4067-4068`; the cap-hit case shows `cooldown_cap_hit` excluded at its slot and absent from cell reasons
(legacy path, where the filter alone decides). `emission_statements` requires an AST-equal statement and string
literals exactly `{code}`, so a sibling site or a fragment fails. The claim-gate scan walks all `joulewise/**/*.py`
(167 modules) plus the extractor CLI, allowlists only the two claim-gate modules and checks each still holds a literal.

### (4) Did L9-STEP4-5 change anything outside tests and the ruling string?

No. `git diff --stat 81155d419..6ce02feba`: `.codex-report/L9-STEP4-5.md`, `.codex-report/l9-step4-5/{full_run_tail.txt,
mutants.py,mutants.txt}`, `configs/analysis/b5/step4_reason_classes.json` (1 line: `step4_rule.ruling`),
`tests/b5_analysis/test_step4_exit_classes.py`, `tests/b5_analysis/test_step4_member_codes.py` (new),
`tests/b5_analysis/test_step4_reason_table.py`. Nothing under `joulewise/` or `scripts/`; `make_table.py` unchanged
(sha `051c13b2…a549d2`). The merge `deda94037` (parents `6ce02feba`, `4c26b2e2c`) has the tree of
`git merge-tree --write-tree` of its parents, so it carries no hand edits (`delta_scope.txt`).

### (5) Whole `tests/b5_analysis` directory

From `/home/user/JouleWise` at `deda94037`, clean tree, TMPDIR under /tmp outside the checkout and without a
float-like token (`/tmp/l9final`):

```
TMPDIR=/tmp/l9final JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .
```

Exact tail (`full_run_tail.txt`):

```
----------------------------------------------------------------------
Ran 1035 tests in 4116.674s

OK (skipped=13)

real	69m22.831s
user	58m29.091s
sys	8m4.592s
EXIT 0
```

No `ERROR:` or `FAIL:` line in the log. The count and skip total equal the lane's L9-STEP4-5 tail (1035, 13). The run shared the container with the mutant rerun for its first third, which is why it is slower than the lane's 65 minutes. Peak disk use of the fixtures reached about 20 GB under TMPDIR; the container kept 5.5 GB free at the low point.

## Report claims checked (L9-STEP4-5.md)

| Claim | Result |
|---|---|
| Only tests, the ruling string and reports changed; `mask`/`tooling`/`r3`/`modules`/generator sha unchanged | Confirmed (`delta_scope.txt`; regeneration test green) |
| 31 mutants killed, including the four L9-STEP4-4 survivors | The 13 I reran are all killed at `deda94037`, including O11, O12, O12b, F8, F9, F10 |
| Member-code tests run the real precheck, filter and `_evaluate_member` | Confirmed by reading `arithmetic_seams()` and the tests |
| Claim-gate proof scans 167 modules plus the CLI, non-vacuous | Confirmed; bound is `>= 1` (F2) |
| Ruling string names the -4 amendment | Confirmed; it also carries an unruled sentence (F1) |
| Full run `Ran 1035 tests`, `OK (skipped=13)` | Reproduced: `Ran 1035 tests`, `OK (skipped=13)`, exit 0 |
| Open issues 1-2 and carried NEEDS_RULING 1-3 | Fairly stated; all stop-side |

## Carried items for the lead (none blocks the merge)

1. NEEDS_RULING 1 (Ed, optional per item 143): whether §2.2's member rule covers all 31 forwarded reducer codes.
2. NEEDS_RULING 2: the cooldown-cap kept-unit case stops as `member_code_on_kept_unit` (exit 2); its cure route is
   also a ruling. One sentence in the ruling text, or its own class, would close it.
3. NEEDS_RULING 3 (plus Opus F3 of -4, now in the ruling string, F1 above): tooling-origin causes of
   `window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing`, `instrument_calibration_stale`,
   `calibration_acceptance_bound_stale` and `kept_units_below_minimum` route to an Ed ruling instead of fix-and-rerun.
4. F3 hardening of exit 0, and F4's unused import, when `steps.py` or `disclosures.py` is next opened.

## Files

- `.codex-report/l9-step4-final-fable/fuzz_step4.py`, `fuzz_step4.txt`: the randomized invariant check and its output.
- `.codex-report/l9-step4-final-fable/delta_scope.txt`: the -5 delta scope and the merge-tree check.
- `.codex-report/l9-step4-final-fable/targeted_tail.txt`: the 41-test baseline at `deda94037`.
- `.codex-report/l9-step4-final-fable/mutants_rerun.txt`: the 13 lane mutants rerun.
- `.codex-report/l9-step4-final-fable/x1_tail.txt`: own mutant X1.
- `.codex-report/l9-step4-final-fable/full_run_tail.txt`: the whole-directory tail.
