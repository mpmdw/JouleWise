# RC-CMP-SOL-REV-3

VERDICT: REJECT on `7fede8c7647001e2679b10246bae832244538e05` (`e5ccf720b..7fede8c7`).

Synthetic inputs only; no real block-5/6/BYTES data opened or searched, no L9 full-size `test_dry_run` run. HEAD and canonical baseline digest verified. Gate policy, FIX-BRIEF-2 and RUN_STATE items 86/87/91/94 were read from local `origin/main` (`82486bfc7`), because this snapshot lacks those current authorities. No production edits.

## Ranked findings

1. **BLOCKER — nested identity still redirects a wrong printed number (S2).** `scripts/compare_b5_recompute.py:1313` lets every nested object's scalar fields overwrite enclosing identities; `:1345` then uses the nearest `contrast_id`. Probe `attack_nested_identity` prints a decode `primary_contrast` estimate of **−2.5**, while decode's agreeing verdict/recompute estimate is **−1.25** and prefill's is −2.5. Without a nested id: exit **2**, `value_differs`. Adding only `estimator.contrast_id=PREFILL`: exit **0**, `fails={}`, `unmapped=[]`; coverage calls the nested id `routing_id` and the wrong estimate `contrast_j`. An in-memory counterfactual preventing that shadow restores exit 2. The enclosing decode id remains merely uncovered. Freeze each binding's owner identity at its designated structural container; reject conflicting nested identities instead of allowing nearest-field substitution.

2. **MAJOR — duplicate JSON members bypass S3 and can erase S1 evidence.** `scripts/compare_b5_recompute.py:251` applies ordinary `json.loads` before inspecting structure. An authenticated synthetic fill containing `"estimate":999999.0,"estimate":-1.25` exits **0**; reversing the members exits **2**. Likewise `"estimate":NaN,"estimate":-1.25` exits **0**: the nonfinite sentinel disappears before `scrub` sees it. The probe updates the custody digest, so this is a parsed-structure gap, not a digest mismatch. Reject repeated object-member names while loading JSON; row/list duplicate checks occur too late.

3. **MAJOR — “routing_id” coverage does not establish exact id agreement.** `binding()` at `scripts/compare_b5_recompute.py:1348` reduces a cell id by substring/phase/suffix, and `:1441` labels the original id compared without comparing its literal value. A floor-composition line with `cell_id=TYPO-d117-df-ph-decode-qwen3-1p7b-absolute` and the correct 42 J value exits **0**, and its bogus id is labelled `routing_id`. A malformed suffix instead refuses, demonstrating partial parsing rather than validation. Validate an explicit accepted identity/translation against the owning row; a canonical-key intersection alone is insufficient.

## Answers 1–3

**1. Earlier probes:** all earlier *defect witnesses* now refuse or DISAGREE. All 17 Python files from all four archived review folders ran against this checkout. Examples: wrong fill/median exit 2; missing L9 run exit 1; missing harvest member exit 2; invalid overrides refuse; round-2 nonfinite, arm-gate, ratio-key and band faults fail closed; recompute-only assist strata produce `count` and `routing_id` failures. Meter probes now show **0 ns**, including both long-origin sweeps and the 580 adversarial streams. Compressed-input restoration still stops explicitly. Healthy controls and the authorized public-count flip remain as designed. The original Sol comparator script stops at its newly correct invalid-bar refusal; the same call was guarded to execute its remaining probes. Opus's audit-stream probe had only its checkout-root locator adapted for extraction under TMPDIR.

**2. Other structural attacks:** unknown numeric/null leaves and nested numeric lists refuse; numeric strings, booleans and empty containers under word exemptions pass as S1 permits. Strings/bools/lists/empty containers replacing a registered estimate refuse. The null-only `j_per_token` exception accepts null and refuses a finite wrong number or nested number. Broad named diagnostic exemptions still accept and list arbitrary new numbers, e.g. `floor/point_floor_diagnostics/active_floor_j=999999`; these are subtree exemptions, not enumerated leaf names. Different families sharing a key remain distinct; repeated `(family,key)` refuses.

The AST tests catch direct one-sided `for` loops/comprehensions inside `compare_*`, but not helper filtering, conditional omission, or `while` loops. Executed in-memory mutants dropping all selected runs and iterating exclusions one-sided with `while` both pass **both AST gates**; this is a guard limitation, not a claim that the full suite accepts those mutants. Existing projection-p42 comparison is still conditional on L9 listing refused cells (`:687`): omitting the list removes its comparison row and still exits 0. Other extraction/sensitivity p42 checks remain, so this witness alone does not change the final status.

**3. Over-refusal:** small clean controls accept registered null `j_per_token`, null unsupported direction, and reordered keyed contrast lists. Reversing v3 arm arrays refuses (2 floor and 4 routing failures); changing only a summary model's spelling from `qwen3-1p7b` to `Qwen3-1.7B-4bit` produces 16 rho and 4 routing failures despite unchanged measurements. Whether those variants are legitimate producer output requires the owning schema/producer, not a looser comparison bar.

A completed full-size comparison using this fixed comparator and the accepted L9 producer settles readiness: retain input/output hashes; require exit 0, zero family failures, empty `coverage.unmapped`, `unbound`, `nonfinite` and `absent_sources`; census registered nulls, array order, raw/canonical routing ids, named numeric exemptions, and three-way meter-member set differences. Reuse completed synthetic A6 artifacts where available. RC-CMP-4's fetched report is still IN PROGRESS at the older head; this seat establishes no real-window readiness.

## Verification and handoff

Commands (all with `TMPDIR=/private/tmp/jwrc3-tmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`):

- `python3.13 .codex-report/rc-cmp-sol-rev-3/probes.py` → prior replay and structural probes, `probes.out`; `--extra` appends null/model-spelling controls. All probe source/orchestration is in that single file.
- The same file's `--counterfactual` runs RC-CMP-5's 27 structural tests against in-memory `e5ccf720b` source: **23 failures, 3 errors**, reproducing its reported 26 detecting tests. Production files remain untouched.
- `python3.13 -m unittest discover -s tests/independent_recompute -t .` → **235 tests, OK (skipped=18), 70.937 s**; `suite.out`.

Changed only this report, `probes.py`, `probes.out`, `suite.out`. Next exact step: lead adjudicates these executed findings under gate-policy rule 4 (the false-agreement class has recurred after its structural fix), then repairs and delta-checks the comparator before the full-size agreement gate. No worker scope expansion or ruling is needed to complete this review.

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| Required synthetic suite | yes | no | no | `suite.out`, 235 OK |
| Prior-probe replay | yes | no new | no | `probes.out`, prior witnesses fail closed |
| Structural execution probes | yes | yes | no | nested wrong estimate exits 0; duplicate members discarded |
