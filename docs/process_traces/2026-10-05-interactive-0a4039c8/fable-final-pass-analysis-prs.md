FINAL PASS: PASS

Cold final pass, 2026-10-05, on PR #487 (an1, e40c8cba), PR #485 (an2, 46083f7c) and PR #486 (an3, 2f42248c), each diffed against main e0c738e9.
No finding blocks merge. Four low-severity items are recorded as flags; none can put a wrong number or a wrongly worded claim into the paper, or bind the wrong bytes.

Method: read each diff and the code around it, re-ran each PR's new tests in its worktree, ran my own probes and mutations in /tmp/fable-an, and ran the three PRs together in a merged scratch tree (/tmp/fable-an/merged = an3 archive plus the files an1 and an2 change; the three PRs touch no file in common).

## PR #487 (an1) — per-producer plan binding in the claim loader

Verdict: PASS.

1. Wrong producer's plan or evidence: not reachable.
   - Cell ownership comes only from the pinset's `producer_plans[].cells` list, never from a bundle's own tag (`joulewise/analysis_engine/inputs.py:1429-1502`). The producers array is committed by the floor artifact's aggregate pin: `canonical_json_sha256(producers)` must equal `provenance.calibration_plan.sha256` (inputs.py:1462-1469).
   - Every cell has exactly one owner. The loader requires the artifact's cell order to equal `aggregate.cell_ids` (inputs.py:1483), and `_project_floor_mint_pinset_v2` requires `aggregate.cell_ids` to equal the concatenated producer cells, four of them and distinct (`joulewise/detection_floor.py:2714-2718` in an1). So no cell can fall through to the "no owner, plan hash None" path with zero problems.
   - Each component must name its owner's evidence root, calibration cell, and order-manifest id and sha256 (inputs.py:1488-1500). Each bundle's plan tag and each comparative block's plan hash must equal the owner's plan sha256 (inputs.py:1998-2005, 2103-2107).
   - The order manifest is read from the owner's pack directory, sha256-checked against the component pin, and must name the owner's plan id and plan sha256 (inputs.py:1603-1618, 1690-1702).
   - Executed: the earlier reviewer's attack script (/tmp/an1rev/attacks.py) run against a copy byte-identical to head (`diff -q` clean on inputs.py, detection_floor.py and the fixture). Result in /tmp/an1rev/atk_br.txt: baseline binds 4/4; swapped plan bytes, swapped order manifests, reordered producers (with and without re-pinning), swapped root mapping, flipped root id on a cell, another producer's order pin, and a producer pointed at the other plan file all bind 0/4 or raise.
   - One reviewer attack bound 4/4 ("cell0 calibration_cell_id from other producer"). I checked it: the fixture's two producers use the same calibration cell ids (`df-ph-decode-qwen25-7b-absolute-decode` in both), so that attack changed nothing. It is a vacuous attack, not a hole (/tmp/fable-an/p1.py output).

3. Pre-v2 / single-plan decisions: unchanged.
   - A single-plan artifact still takes its plan sha256 from `provenance.calibration_plan` and still reads `<root>/order_manifest.json`; the new block-level and order-manifest plan checks are gated on `multi_producer` (inputs.py:1575-1578, 1924-1927).
   - Executed evidence: /tmp/an1rev/leq_main_plain.json vs leq_br_plain.json and leq_main_folded.json vs leq_br_folded.json are byte-identical (`cmp` clean). These are full binding snapshots for a real v1 mint under about a dozen plan and order-file corruptions, on main and on the branch.

4. Tests drive the real seam: yes. The fixture mints through the real generalized v2 mint and loads through the real loader (`tests/fixtures/analysis_v2/binding.py:216-225, 256`). Re-run in the worktree: `tests/test_analysis_engine_evidence_roots.py tests/test_analysis_engine_v2_binding.py` -> 12 passed, 8 subtests passed.

Supply-map repin (`configs/paper_supply/supply_map.json`): four `expected_sha256` values only, all under roles whose `mode` is `test_fixture_non_issuing`. No path, mode or gate id changed. See the merged-tree run below for the executed check.

Flag (LOW, recorded only): `_floor_producer_plans` reads `artifact.get("provenance", {})` and `cell["cell_id"]` without type guards on the single-plan path (inputs.py:1440, 1503-1505). An artifact with a non-object provenance would raise instead of returning a problem code. Every caller authenticates the artifact against the schema first, so this is not reachable with an admitted artifact, and a raise is fail-closed.

## PR #485 (an2) — printed quantities, rounding, results-fill adapter

Verdict: PASS.

2. Interval never printed narrower; no field in another field's slot.
   - Rounding: lower bounds use ROUND_FLOOR and upper bounds ROUND_CEILING on `Decimal(str(value))` (`joulewise/paper_rendering.py:56-66, 70-79`). Executed: /tmp/fable-an/p2b.py, 300,000 random intervals across 18 decades in both units -> 0 printed lower bounds above, and 0 printed upper bounds below, the value's decimal text; 0 negative zeros; 0 bounds looser than one display unit. NaN, infinity, bool, string, None, Decimal, a missing key, an extra key and a reversed interval all refuse (/tmp/fable-an/p2.py).
   - Slots, checked against the producer: `metrology_aware_CI95` and `decision_interval` are `{lower, upper}` objects written by `joulewise/analysis_engine/__init__.py:203, 1601`; `estimator.n` is the paired-block count (`__init__.py:192`), printed as "n = N blocks"; the equivalence margin is a symmetric bound in the estimate's own unit (`claims.py:254-255`), printed as "±margin unit". J/token is printed only for a contrast whose unit is J/token (paper_rendering.py:177-180).
   - Reported energy: `lower_j`/`upper_j` are mean ∓ (t-interval half-width + deterministic bound) (`joulewise/paper_reported_energy.py:430-431`), so the printed interval is the wider one.
   - D-165 wording: branch B is reachable only when no row is refused (`joulewise/dominance_closeout.py:2011-2033`), the threshold is 2.0 with "passes" meaning ratio >= 2 (dominance_closeout.py:46, 537), so "required ratios below the twofold threshold" names only failed rows.
   - Executed mutations on a scratch copy (/tmp/fable-an/mut2.py): inward rounding, half-even bounds, toward-zero bounds, metrology slot printing the decision interval, decision slot printing the metrology interval, reported interval without its deterministic bound, estimate printing the lower bound, selection ignoring subjects, margin printing the deterministic total, n taken from df, reversed interval accepted, J/token printing the energy sum -> all CAUGHT by the PR's tests.

3. Pre-existing decisions: `scripts/render_results_fills.py:1178` widens one `except` to `ValueError`. `StopFill` and `RenderedValidationError` are both `ValueError` subclasses and `StopFill` is still caught first (render_results_fills.py:128, 152), so every earlier exit code is unchanged; a bare `ValueError` that used to end in a traceback (exit 1) now exits 2. The script does not read `gamma` beyond allowing the key (render_results_fills.py:956), so the adapter cannot change any rendered Results text today.

4. Tests drive the real seam: yes; renderer tests use the real reported-energy projection, the real claim-verdict producer and the real D-165 builder. Re-run in the worktree: 45 passed, 18 subtests passed.

Flags (LOW, recorded only, both test gaps with correct code):
- `tests/test_paper_rendering_v5.py:58-83`: a mutation that prints `repeat_point_CI95` in the "95% metrology interval" slot SURVIVES (13 passed). The fixtures have zero metrology standard error, so the two intervals are equal. The repeat-point interval is the narrower one whenever metrology error is nonzero, so a future slip here would not be caught. Head reads the correct field (paper_rendering.py:188).
- Same file: a mutation that floor-rounds the claim estimate SURVIVES (13 passed); claim fixtures have estimates exact at three decimals. Half-even is pinned for the shared `_number` default by the reported-energy test (1.2345 -> 1.234).
- Note, not a defect: outward rounding is taken from the float's shortest decimal text, the same text the JSON artifact carries. When that text has no more digits than the display precision, the binary float can sit below a printed lower bound by less than one unit in the last place of a double (about 1e-16 relative). Seen in 23,009 of 600,000 fuzz cases, only for such values.
- Note, wording: the reported-energy line labels the t-interval plus deterministic bound as "95% reported-mean interval". The printed interval is wider than a plain 95% interval, never narrower.

## PR #486 (an3) — finalize sidecar, v2 pinset emitter, per-cell config binding

Verdict: PASS.

1. Wrong workload's config: not reachable.
   - With per-cell pins, both the absolute and the comparative component of a cell must carry the cell's own `scientific_config_identity_sha256`, and the sorted distinct set must hash to the producer's `config_set_sha256` (`scripts/mint_floor_artifact_generalized.py:2367-2384`; `joulewise/detection_floor.py:2332-2364`). Model and runtime identity stay one-per-producer (mint_floor_artifact_generalized.py:2360-2363).
   - The pin is not circular: the emitter derives it from the pack's registered config files, each byte-checked against the plan tree and against the extraction report's member pin (`scripts/emit_floor_mint_pinset.py:130-148, 286-291`), then requires the authenticated evidence to equal it (emit_floor_mint_pinset.py:172-174). `main` always goes through that path (emit_floor_mint_pinset.py:423-426).
   - The artifact's `producer_config_sets` must equal the registered pinset's per-cell pins at validation (detection_floor.py:2974-2976) and at mint binding (mint_floor_artifact_generalized.py:3203-3206). The per-cell pins sit inside the producers array, so `producer_set_sha256` commits to them.
   - Executed by the PR's own test, re-run here: `test_other_workload_and_set_preserving_swap_refuse_per_cell` swaps decode and prefill evidence for one role and for both (the set-preserving case) and each refuses with "per-cell scientific config identity mismatch".

3. Legacy v2, v1, single-config: unchanged.
   - A producer with no per-cell pin keeps the old single-hash check verbatim (mint_floor_artifact_generalized.py:2371-2374). A partial set of pins refuses (detection_floor.py:2351-2352).
   - v1 projections have an empty `config_sets_by_identity`, so the new comparison is skipped (detection_floor.py:2974). `producer_config_sets` on a non-v2 artifact is refused, as it was before by the unknown-key check (detection_floor.py:3213-3215).
   - `finalize_analysis_manifest.py` without `--dominance-replay-sidecar` makes the same library call as before with the sidecar argument left at None (scripts/finalize_analysis_manifest.py:103-115, 161-168).
   - Executed: `test_single_config_new_and_legacy_v2_still_mint` and `test_without_sidecar_preserves_existing_refusal` pass.

Sidecar staging binds the right bytes: the bytes validated are the bytes written (read once, validated, then written append-only under their own sha256), and validation ties the sidecar to this floor by id, operand alignment and member census (finalize_analysis_manifest.py:57-101). Nothing is staged unless every other input already authenticates (finalize_analysis_manifest.py:118-152).

4. Tests drive the real seam: yes. The finalize tests run the CLI as a subprocess; the config-set tests run the real emitter, the real mint and the real claim reader. Re-run in the worktree: 25 passed, 2 skipped, 27 subtests passed. The 2 skips are the JSON-schema checks ("optional jsonschema dependency is absent"), so `schema_v2.json` itself was not executed in this environment; the Python validators that gate the mint were.

## Cross-PR seam (all three merged)

an1's loader hashes the whole producers array, so an3's new per-cell field is covered without a loader change. Executed in /tmp/fable-an/merged: an1's two binding test files, an3's config-set and emitter tests, and an2's renderer and adapter tests together -> 38 passed, 2 skipped, 38 subtests passed.

Supply-map repin, executed in the merged tree: `tests/test_paper_custody.py` plus the renderer, results-fill and finalize test files -> 71 passed, 1 failed, 418 subtests passed. With main's old four hashes put back into the scratch copy, the custody file alone gives 15 failed, 15 passed; with an1's hashes it gives no pin failure. So the new hashes are the ones the custody gate computes with all three PRs present, and the tests do exercise them.

The 1 failure is `PaperCustodyApiTests::test_real_anchor_refuses_untracked_nongoverned_file_without_mocking` (got `readiness_identity_artifact_unreadable`, expected `readiness_identity_environment_dirty`). That test asks git for the checkout's anchor state, and my merged tree is a tar extract, not a git checkout. I read this as an artifact of the scratch tree, not of any PR, but I did not confirm it: the test writes a probe file into the checkout it runs in, so I did not run it inside a worktree. It is untouched by all three diffs.

## Not run

- The full test suite. Only the files named above were run.
- `scripts/floor_mint_pinsets/schema_v2.json` against a JSON-schema validator (the dependency is absent here; both schema tests skip).
- The one git-anchor custody test above, in a real checkout.
- No worktree was edited; `git status --short` is empty in all three after the pass.
