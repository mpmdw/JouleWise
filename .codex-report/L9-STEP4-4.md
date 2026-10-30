STATUS: DONE

# L9-STEP4-4: plan-named member codes are R3 at step 4; main merged

Seat L9-STEP4-4. Lead: joulewise-28. Branch `lane/2026-10-30-l9-step4-reasons`, from `901956944`. Synthetic data
only; I did not open or search any real block-5, block-6 or BYTES data.

## SUMMARY

- **Merge.** I merged `origin/main` (`66f9b6be3`, which contains PR #603's G6 fixture fix `93e7f5dd2`) with a normal
  merge commit, `492a30f`.
- **Fable F1, applied exactly.**
  - Three codes are added to the recorded `r3` list:
    - `window_evidence_precheck_missing`
    - `campaign_cooldown_evidence_missing`
    - `idle_window_suspect`
  - The test's `RULING['r3']` and `configs/analysis/b5/step4_reason_classes.json` both carry them. I regenerated the
    JSON as blind generator output plus `HEADER` plus `RULING`, so the mask and tooling lists are unchanged.
  - Each code is pinned in `R3_PINS` to its `reasons.append(...)` emission in `joulewise/analysis_engine/inputs.py`
    and to `MEMBER_RULE`.
  - The r3-subset-of-blind-mask test now states the new invariant: r3 minus the blind mask is exactly the three
    plan-named codes. Those codes are blind tooling codes, each pinned to `inputs.py` and the member rule, and each
    appears literally in plan 2.2 bullet 3.
  - The `FORWARDED_PRECHECK` count goes from 6 to 9. The mask-and-reducer identity now excludes the plan-named codes,
    and the plan-named codes are shown not to be reducer vocabulary.
  - r14's second subcase now expects `extraction_cell_r3_refusal`.
- **Claim-gate codes stay out of r3.** `paired_block_incomplete` and `fixed_n_plan_incomplete` are not added. A new
  static test shows neither can reach a step-4 cell:
  - Neither is in `REDUCER_REASON_CODES`, so the precheck never forwards them.
  - In the generator's eleven extractor modules, `fixed_n_plan_incomplete` never occurs.
  - `paired_block_incomplete` occurs only as the code argument of `stop_if_member_code_on_kept_unit`. That call raises
    `member_code_on_kept_unit` (exit 2) and never adds a cell reason.
- **No other widening.** No other forwarded reducer code moves to R3 (see NEEDS_RULING 1).

## Counterfactual

I classified one refused non-p42 target with a single reason, using the same script before and after
(`classify_step4_exit(1, report, spec)`):

| reason | before (901956944 + main merge) | after (c2ecb95) |
|---|---|---|
| window_evidence_precheck_missing | extraction_cell_tooling_refusal | extraction_cell_r3_refusal |
| campaign_cooldown_evidence_missing | extraction_cell_tooling_refusal | extraction_cell_r3_refusal |
| idle_window_suspect | extraction_cell_tooling_refusal | extraction_cell_r3_refusal |
| idle_window_suspect_unknown | extraction_cell_tooling_refusal | extraction_cell_tooling_refusal |
| paired_block_incomplete | extraction_cell_tooling_refusal | extraction_cell_tooling_refusal |
| fixed_n_plan_incomplete | extraction_cell_tooling_refusal | extraction_cell_tooling_refusal |
| cooldown_cap_hit | extraction_cell_tooling_refusal | extraction_cell_tooling_refusal |

`test_R2_plan_named_member_codes_are_r3_and_claim_gate_codes_are_not` pins the "after" column for the first three rows
and the two claim-gate rows. r14 does the same through the real CLI composition.

I also checked that the AST guard catches a violation. A synthetic `reasons.append("paired_block_incomplete")` is
reported as not being a stop argument, while the `stop_if_member_code_on_kept_unit(..., "paired_block_incomplete")`
form is accepted.

## VERIFICATION

The command below ran from `/home/user/JouleWise` at `c2ecb95` after the merge. I first ran
`git fetch --unshallow`, because the container's clone was shallow. TMPDIR is outside the checkout and has no
float-like token.

```
TMPDIR=/tmp/jwlanetmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .
```

Exact tail:

```
----------------------------------------------------------------------
Ran 1029 tests in 3221.547s

OK (skipped=13)
```

Two earlier attempts did not complete and are not evidence:

- The first ran in the shallow clone and was cut off by my own `timeout 3000` (EXIT 124). Before it stopped it had
  printed two `E`, one next to `fatal: path 'joulewise/b5/harvest.py' exists on disk, but not in '224a264c5…'`. That
  commit object was absent from the shallow clone. The unshallowed run above has no `E` or `F`.
- The second I stopped in order to unshallow the clone.

Targeted run after the change (`test_step4_reason_table`, `test_step4_exit_classes`): `Ran 34 tests`, `OK`.

## Finding-by-finding disposition

| Review | Finding | Disposition |
|---|---|---|
| Fable | F1: r3 omits three plan-named member codes | **Applied** as the lead ruling specifies (c2ecb95). |
| Fable | F1 (optional): list `paired_block_incomplete`, `fixed_n_plan_incomplete` | **Not added**, per the ruling. Added a test that they cannot reach a step-4 cell. |
| Fable | F2: cooldown-cap case stops as `member_code_on_kept_unit` (tooling, exit 2) | **Not a code change.** Stop-side. The cure route needs a ruling statement and `kept_units.py` is outside WRITE_SCOPE. NEEDS_RULING 2. |
| Fable | F3: classifier trusts exit 0 | **No change.** No path today: the extractor exits 1 on any refused cell or omitted member. Changing `ok` semantics on a reviewed classifier is beyond this seat. Open issue 1. |
| Fable | F4: S-VERIFY tails pending at 901956944 | **Superseded.** The full-run tail above is at c2ecb95. |
| Opus | F1: R3 narrower than plan 2.2 bullet 3 | **Partly applied.** The three plan-named codes that reach a cell are now R3. The other 25 forwarded reducer codes, including `cooldown_cap_hit`, are **not** widened, per the ruling. NEEDS_RULING 1. |
| Opus | F2: three R3 codes also have non-2.2 producers | **No change.** The error is over-inclusive and stop-side, so nothing passes. Narrowing would need producer-site splitting outside WRITE_SCOPE. NEEDS_RULING 3. |
| Opus | F3: exit-0 trust | Same as Fable F3. |
| Opus | F4: unused `classify_step4_exit` import in `disclosures.py` | **Not changed.** The file is outside WRITE_SCOPE. Open issue 2. |

## FILES CHANGED

- `configs/analysis/b5/step4_reason_classes.json`: `r3` gains three codes. Regenerated, and `mask` and `tooling` are
  unchanged.
- `joulewise/b5_analysis/steps.py`: docstring of `step4_r3_reasons` only. Classifier logic is unchanged.
- `tests/b5_analysis/test_step4_reason_table.py`:
  - `RULING`, `R3_PINS`, `PLAN_NAMED`, `CLAIM_GATE_ONLY`
  - the invariant test, rewritten
  - the forwarded-count test, now 9
  - the new claim-gate test
- `tests/b5_analysis/test_step4_exit_classes.py`:
  - `R3_CODES` grows to 11
  - the tooling-only test now uses `idle_window_suspect_unknown` and `cooldown_cap_hit`
  - new plan-named and claim-gate test
- `tests/b5_analysis/test_floor_kept_units.py`: r14's precheck subcase now expects R3. I added a tooling subcase
  (`marker_self_digest_mismatch`) so r14 still covers the tooling seam.
- `.codex-report/L9-STEP4-4.md`: this report.
- The generator `tests/b5_analysis/step4_reasons/make_table.py` is unchanged (sha256 `051c13b2…a549d2`).
- Merge commit `492a30f` from origin/main is exempt.

## DECISIONS I MADE

1. I regenerated the table by running the committed generator and writing `HEADER + output + RULING` with
   `json.dumps(indent=1)`. This is exactly the comparison the R1 regeneration test makes, which passes.
2. `idle_window_suspect_unknown` stays tooling. The plan names only `idle_window_suspect`, and the ruling is
   plan-literal.
3. I kept `step4_rule.ruling` as the L9-STEP4-3 text. The R1 shape test pins the key set, and the amendment is
   recorded in the test docstring and here. I did not add a new key.
4. r14 got a third, tooling, subcase. Flipping the precheck subcase would otherwise have left r14 without a
   tooling-class real composition.
5. The claim-gate proof is static (AST over the generator's module list). The behavioral route through
   `window_evidence_precheck` is covered by asserting the codes are outside `REDUCER_REASON_CODES`. That function
   turns any non-reducer raw reason into `window_evidence_precheck_missing` (`inputs.py`, about line 4067).

## OPEN ISSUES

1. Exit-0 trust (Fable F3, Opus F3). The fail-closed hardening is in `steps.py`: exit 0 with a refused cell or an
   omitted member would become `refused`, and therefore exit 2. It is cheap if the lead wants it. I did not make it
   here, because no path exists today and it changes the reviewed `ok` semantics.
2. Unused import `classify_step4_exit` in `joulewise/b5_analysis/disclosures.py:25` (Opus F4). It is outside
   WRITE_SCOPE.

## NEEDS_RULING

1. **(Ed; Opus F1.)** Does plan 2.2's member rule cover every member-level code the window-evidence precheck forwards
   onto a kept unit? That is all 31 `REDUCER_REASON_CODES`, for example `cooldown_cap_hit`,
   `thermal_pressure_elevated_in_window` and `negative_power_sample`. Today only the six blind-mask reducer codes and
   the three plan-named codes are R3. If Ed says yes, the change touches `RULING` plus the JSON (the regeneration test
   forces both together) and the pins. I implemented the lead's narrower, plan-literal ruling as instructed.
2. **(Fable F2.)** The plan's cooldown-cap same-slot case on a kept member stops as the tooling code
   `member_code_on_kept_unit` (exit 2), not as `extraction_cell_r3_refusal`. Its cure route should also be a ruling.
   The ruling text should say so, or the code would need its own R3 class.
3. **(Opus F2.)** `instrument_calibration_stale` (read-error path), `calibration_acceptance_bound_stale` (a
   session-level code unioned into every cell) and `kept_units_below_minimum` (which tooling refusals upstream can
   trigger) route some tooling-origin failures to R3. This is stop-side only. Decide whether that coarseness is
   acceptable or whether the producers should split.
