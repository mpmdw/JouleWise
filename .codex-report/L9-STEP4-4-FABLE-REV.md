VERDICT: ACCEPT

# L9-STEP4-4 delta review, second family (Fable), seat L9-STEP4-4-FABLE-REV

Reviewed `c2ecb9588` on `lane/2026-10-30-l9-step4-reasons` at `a7e00c9f7` (the report commit `a7e00c9f7` read as claims;
the merge `492a30f42` of `origin/main` excluded) from branch `review/2026-10-30-l9-step4-4-fable-rev`, unshallowed clone.
Synthetic data only; I did not open or search any real block-5, block-6 or BYTES data. Evidence files:
`.codex-report/l9-step4-4-fable-rev/`.

The change implements the lead's plan-literal ruling exactly and nothing else moved. Over all 1943 codes I classified
(42 blind MASK, 1898 blind tooling, three extras), exactly three changed class, all on a refused non-p42 target and all
from `extraction_cell_tooling_refusal` to `extraction_cell_r3_refusal`: `window_evidence_precheck_missing`,
`campaign_cooldown_evidence_missing`, `idle_window_suspect`. The classifier logic is untouched (`steps.py` diff is one
docstring line), so no exit-1 report gained a path to `ok`, the p42 exit or an outcome class. The registered JSON is
byte-identical to blind generator output plus `HEADER` plus `RULING`, with `mask` and `tooling` unchanged. The
claim-gate codes stay out and cannot reach a step-4 cell. The findings below are test-strength items, none of them a
classification error.

## Findings (ranked)

**F1 (should-fix, test strength). The claim-gate proof rests on a precheck filter that no test exercises.**
`test_R3_claim_gate_member_codes_cannot_reach_a_step4_cell` (`tests/b5_analysis/test_step4_reason_table.py:187-207`)
covers the data route only by asserting `CLAIM_GATE_ONLY & REDUCER_REASON_CODES` is empty; the premise that the precheck
forwards reducer vocabulary alone is the `elif` at `joulewise/analysis_engine/inputs.py:4067-4068`. Mutant M9 replaces
that condition with `False`: the two step-4 modules, r14, `tests.test_analysis_claims` (65) and
`tests.test_analysis_integration` (116) all stay green (`mutants.txt`, `m9_probe.txt`). Under M9 a stored precheck
list `['paired_block_incomplete']` reaches the precheck's reasons verbatim (`m9_probe.py`: HEAD gives
`window_evidence_precheck_missing`, M9 gives `paired_block_incomplete`), from where `floor_extraction.py:2238-2245`
copies it into every member's reasons. Stop-side either way (the code is not in `r3`, so it would class tooling), but
the proof's stated premise would be false with nothing failing. Fix: add one behavioral case to the claim-gate test or
to `test_step4_exit_classes`: build a `BundleEvidence` whose stored precheck reasons are `['paired_block_incomplete']`
(and one with `['fixed_n_plan_incomplete']`), call `window_evidence_precheck`, and assert the result's reasons contain
`window_evidence_precheck_missing` and neither claim-gate code. `m9_probe.py` is a ready skeleton.

**F2 (should-fix, test strength). The emission-site pin is a substring check and accepts the wrong site.**
`test_R3_each_code_is_pinned_to_its_producer_emission_site_and_plan_line` asserts `code in emission` and
`emission in module text` (`test_step4_reason_table.py:173-174`). Mutant M8 pins `idle_window_suspect` to
`reasons.append("idle_window_suspect_unknown")`: all 34 step-4 tests and r14 pass (`mutants.txt`). So the new pin for
`idle_window_suspect` cannot tell the plan-named code's emission (`inputs.py:4105`) from its tooling sibling's
(`:4107`). Fix: `self.assertIn('"%s"' % code, emission)` (or `assertRegex(emission, r'\b%s\b' % re.escape(code))`) at
line 173; M8 then fails.

**F3 (nit, test strength). The static proof never asserts it saw a stop site.** `seen['paired_block_incomplete']` is
counted but only `fixed_n_plan_incomplete` is asserted to be zero (`test_step4_reason_table.py:207`); with both
`inputs.py` stop sites deleted the per-node assertion is vacuous. Mutant M12 is still killed, but only because the
literal then leaves the blind tooling list and the regeneration test fails. Fix: add
`self.assertEqual(seen['paired_block_incomplete'], 2)` after the loop so the pin is the test's own.

**F4 (nit, provenance). `step4_rule.ruling` still names only the L9-STEP4-3 ruling** while `r3` now carries the
L9-STEP4-4 amendment (`configs/analysis/b5/step4_reason_classes.json`, `step4_rule.ruling`; test `RULING` at
`test_step4_reason_table.py:52`). Decision 3 of the report records this deliberately. The regeneration test forces
`RULING` and the JSON to change together, so the one-string edit "L9-STEP4-3 and L9-STEP4-4 lead rulings, …" is cheap
and would let the registered file name its own provenance. Optional.

**F5 (note, outside the delta). The `cooldown_cap_hit` filter has no step-4 test.** Mutant M10 drops the
`reason != "cooldown_cap_hit"` filter at `joulewise/floor_extraction.py:2243`; the step-4 modules and r14 pass. The
lane's pin comment relies on that filter ("only cooldown_cap_hit is filtered", `test_step4_reason_table.py:84-86`).
Not changed by this delta and consistent with NEEDS_RULING 2; recorded so the lead knows the dependency is untested.

**F6 (note, pre-existing, unchanged). Exit 0 is trusted** (`steps.py:58-59`): all 1943 codes give `ok` at exit 0
before and after (`classification_diff.txt`). The lane's open issue 1 states this correctly; the extractor returns 1 on
any refused cell (`scripts/extract_detection_floors.py:268-287`).

## Answers to the six items

**1. The three codes, and nothing else.** `classification_diff.txt` (from `classify_all.py`, run with `-I` against the
before worktree at `492a30f42` and the after checkout). Each code was placed alone on a refused non-p42 target, alone
on a refused p42 cell, on a refused p42 cell beside a tooling-refused target, and on a refused target at exit 0 and
exit 2. Changed: 3 of 1943, target column only. Before: 8 R3 / 1935 tooling; after: 11 R3 / 1932 tooling. The other
four columns are identical before and after (p42-only is always the registered exit; the R3 code on a p42 cell beside a
tooling target is always tooling; exit 0 is always `ok`; exit 2 is always `refused`). `idle_window_suspect_unknown`,
`paired_block_incomplete`, `fixed_n_plan_incomplete`, `cooldown_cap_hit` and `member_code_on_kept_unit` stay tooling.
The lane's counterfactual table is reproduced exactly.

**2. No exit-1 path to `ok`, the p42 exit or an outcome class.** The only non-test, non-config change is the docstring
(`range_check.txt`); the branch structure of `classify_step4_exit` (`joulewise/b5_analysis/steps.py:50-110`) is the one
both L9-STEP4-3 reviews verified. `ok` still needs exit 0 (`:58-59`). The p42 exit still needs an empty `targets` list
(`:99-101`), which the `r3` set cannot influence. `extraction_cell_r3_refusal` is registered under `tooling_refusal`
and the outcome registry is `['dominance_ratio_zero_denominator']` alone (`exit_path_fuzz.txt`). 20000 random exit-1
reports mixing every table code, malformed reasons, non-boolean `extractable` and membership refusals: zero
violations; the only record status `ok` is the registered p42 exit with no refused non-p42 cell.

**3. Regeneration.** `regeneration_check.txt`: `python3.13 -I tests/b5_analysis/step4_reasons/make_table.py .` gives
`{modules, mask_rule, mask, tooling}` with 42 and 1898 codes, equal to the blind `CLASS_TABLE.json` at `08ea5c958`;
`json.dumps(HEADER + output + RULING, indent=1) + '\n'` equals the registered file's bytes. Generator sha256
`051c13b2…a549d2` equals the blind generator's; the range has no diff under `step4_reasons/`. Key by key against the
before file: only `r3` differs (three codes added, none removed); `r3` is sorted and unique, 11 codes; key order
unchanged. The merge `492a30f42` equals the automatic merge tree of its parents (no manual edits), so it is correctly
exempt.

**4. The static claim-gate proof.** `static_proof_attack.md`. I tried five routes: a data-carried code through the
stored precheck list (blocked by `inputs.py:4067`, which turns any non-reducer member into
`window_evidence_precheck_missing`); a producer outside the eleven modules (the extractor's import closure is 84
files; every other claim-gate literal is in `analysis_engine/__init__.py`, which only `cli.py` and `paper_custody.py`
call into, never the extractor path); the `p42_precheck` silent return of the stop (not passed at `inputs.py:3590`,
`:3746`, nor by the extractor's stop closure at `floor_extraction.py:3210-3211`); the guard's shape (keyword form
fails closed, M6); and vacuity (the test never asserts it saw a stop site, F2). The proof holds at this head. Its
backing for the data route is an assertion about `REDUCER_REASON_CODES` plus a filter no `tests/b5_analysis` test
exercises (F3, mutant M9).

**5. Mutants.** `mutants.py` / `mutants.txt`, each run in a worktree at `a7e00c9f7` against the two step-4 modules
(34 tests) and r14, then reset.

| Mutant | Change | Killed by | Result |
|---|---|---|---|
| M1 | JSON only: drop `window_evidence_precheck_missing` from `r3` | regeneration test, r3 invariant, two exit-class tests, r14 | killed (4 + r14) |
| M2 | RULING, JSON, pins and `PLAN_NAMED` all drop `idle_window_suspect` (consistent partial revert) | `FORWARDED_PRECHECK == 9`, `R3_CODES` in `test_step4_exit_classes`, plan-named test | killed (3) |
| M3 | over-widen: `idle_window_suspect_unknown` into RULING, JSON, pins, `PLAN_NAMED` | `'`code`' in bullet` (not plan-named), forwarded count, tooling-only test | killed (3) |
| M4 | widen with `paired_block_incomplete`, fully pinned | claim-gate `assertNotIn`, forwarded count, exit-class claim-gate test | killed (3) |
| M5 | producer: precheck appends `paired_block_incomplete` to a cell's reasons (`inputs.py:4063`) | static proof, `line=4063` | killed (1) |
| M6 | producer: first stop site passes `code=` by keyword | static proof fails closed, `line=3590` | killed (1) |
| M7 | classifier drops the three plan-named codes at runtime | r3-equals-RULING, six exit-class subtests, r14 | killed (7 + r14) |
| M8 | pin `idle_window_suspect` to the `_unknown` emission site | nothing | **survived** (F2) |
| M9 | precheck forwards non-reducer stored reasons (`inputs.py:4067` -> `False`) | nothing in step-4 modules, r14, `test_analysis_claims`, `test_analysis_integration` | **survived** (F1) |
| M10 | extractor stops filtering `cooldown_cap_hit` (`floor_extraction.py:2243`) | nothing in step-4 modules or r14 | **survived**, outside the delta (F5) |
| M11 | r14 precheck subcase expects tooling again | r14 | killed |
| M12 | both `inputs.py` stop sites for `paired_block_incomplete` deleted | regeneration test only (literal leaves the blind tooling list) | killed, incidentally (F3) |

Nine of twelve killed. The three survivors are test-strength gaps, each stop-side; none changes a classification at
this head.

**6. Whole directory.** From `/home/user/JouleWise` at `a7e00c9f7`, unshallowed, TMPDIR outside the checkout with no
float-like token:

```
TMPDIR=/tmp/jwfab4tmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .
```

Exact tail (`full_run_tail.txt`):

```
----------------------------------------------------------------------
Ran 1029 tests in 3620.969s

OK (skipped=13)
EXIT=0
```

Targeted run of `test_step4_reason_table` and `test_step4_exit_classes` at the same head: `Ran 34 tests`, `OK`.

## Report claims checked

| Claim in `L9-STEP4-4.md` | Result |
|---|---|
| Only `c2ecb9588` is a code commit since `901956944`; merge `492a30f42` exempt | Confirmed; the merge equals the automatic merge tree |
| Three codes added to `r3`; `mask`/`tooling` unchanged; regenerated as generator + HEADER + RULING | Confirmed byte for byte |
| Counterfactual table (7 rows) | Reproduced; extended to all 1943 codes with the same result |
| `FORWARDED_PRECHECK` 6 to 9; plan-named codes not reducer vocabulary | Confirmed (test passes; `PLAN_NAMED & REDUCER_REASON_CODES` empty) |
| Claim-gate codes cannot reach a cell; static test | Confirmed with the limits in F2/F3 |
| r14 flipped to R3 with a tooling subcase kept | Confirmed (`test_floor_kept_units.py:969-972`); M1 and M11 show r14 pins the flip |
| Generator sha unchanged | Confirmed |
| Full run `Ran 1029 tests`, `OK (skipped=13)` | Reproduced here: `Ran 1029 tests`, `OK (skipped=13)`, no `E` or `F` |
| Decision 2: `idle_window_suspect_unknown` stays tooling | Confirmed, and plan-literal (the plan does not name it) |
| NEEDS_RULING 1-3 and open issues 1-2 | Correctly scoped; none is changed by this delta |

## Fix list

1. F1: add the behavioral precheck case (stored `['paired_block_incomplete']` and `['fixed_n_plan_incomplete']` give
   `window_evidence_precheck_missing`, never the raw code) beside the static proof.
2. F2: make the emission pin match the quoted code (`'"%s"' % code`), so M8 fails.
3. F3: assert `seen['paired_block_incomplete'] == 2`.
4. F4 (optional): name both rulings in `step4_rule.ruling`, RULING and JSON together.

None of these blocks the gate: the ruling is implemented exactly, nothing else changed class, and every path to `ok`,
the p42 exit or an outcome class is as closed as it was at `901956944`.
