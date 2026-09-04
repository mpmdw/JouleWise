# Round-7 `_v5` fill checklist (draft-v1.md frozen)

This is the execution record for a future fill of a custodied working copy.
`docs/paper/draft-v1.md` is read-only. The supplier namespace is generation
`_v5`: `qwen3-1p7b` / `qwen3-8b`, decode workload `real_prompts_v1`, and a
prefill length selected only by the hash-pinned G2-a record. The current
`scripts/render_results_fills.py` still carries the pre-`_v5` token vocabulary;
it is not fill authority for renamed rows and must fail closed until its
lead-owned successor is regenerated.

The batch and fence structure below is binding. Every replacement goes into a
fresh working copy and a hash-bearing fill ledger; nothing edits the frozen
draft in place.

## Glossary

- **Supplier:** the exact issued artifact field or frozen derivation that
  authorizes one fill. Nearby prose, an old result, or a desk calculation is
  not a supplier.
- **Issued:** written by the authenticated producer and retained with identity,
  path, SHA-256, and provenance.
- **Replay fence:** `scripts/check_paper_replay_fence.py`; require the exact
  successful tail `COMPARED 43` / `MISMATCHES 0` before and after every batch.
- **Round-7 artifact fence:** `scripts/check_paper_round7_artifacts.py`; its
  successful tail is `R7F COMPARED n / MISMATCHES 0` where `n` is
  placement-dependent: 181 comparisons plus one per placed DX literal, plus 3
  in full replay (the XD, AQ, and F4 byte identities). With zero markers
  placed the tails are therefore `R7F COMPARED 184 / MISMATCHES 0` (full
  replay) and `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`; a complete
  16-marker batch ends `R7F COMPARED 200 / MISMATCHES 0`. The fill-batch PR
  restates the exact tail observed before and after the batch, and rewrites
  the zero-placement pins in `tests/test_paper_round7_artifacts.py` in the
  same commit that places the markers. The literals-only tail is separate
  from RF's 43 comparisons and is not sufficient before a fill batch.
  R7F also censes all 16 non-identity DX placements once the mandatory standing sentence appears and prints `R7F PLACED n/16` immediately before its `COMPARED` tail.
  R7F now scans the diagnostic-value (DX) prose region, from the mandatory
  standing sentence to the next Markdown heading. It reports
  `MISMATCH prose DX-nnn` when a registered rendered value appears there
  without its own immediately preceding `[FILL:DX-nnn]` marker.
- **STOP_FILL:** no insertion when a required artifact, field, identity pin,
  replay, branch predicate, or registered rendering is absent or malformed.
- **`[PREFILL_LENGTH]`:** the G2-a selection record's
  `collection_prefill_tokens`. It remains `UNRESOLVED-UNTIL-G2A`; never replace
  it from a projection, default, filename, or operator choice.
- **TERM A / TERM B:** the retained coded cell-label diagnostic. It is reported
  beside R but is no longer the headline falsifier.
- **R:** per component and per cell,
  `corner_widened_unguarded_floor_j / point_unguarded_floor_j`. The gate is
  `R >= 2.0`; exact equality passes.
- **R_cm:** the common-mode sensitivity disclosure. Comparative R_cm comes from
  the registered pre-mint replay over custodied block inputs and `< 2.0`
  withdraws the dominance sentence. Absolute R_cm is literally
  `not_applicable` with the registered deviations-from-mean cancellation reason.

## Preconditions (batch 0)

1. Start from the lead-named 40-hex commit and a clean tree. Create a fresh,
   non-overwritten custody directory and copy the frozen draft into it.

   ```sh
   set -euo pipefail
   set -o noclobber
   export JOULEWISE_REPO=/Users/edr/code/JouleWise
   export PYTHON="$JOULEWISE_REPO/.venv/bin/python"
   export PINNED_ROUND7_COMMIT=REPLACE-WITH-ROUND7-COMMIT
   export REAL_FILL_DIR=/ABSOLUTE/round-7-v5-fill-custody
   export PAPER_REPLAY_CORPUS_ROOT=/ABSOLUTE/root-containing-runs_window_a_20260722
   test "$PINNED_ROUND7_COMMIT" != REPLACE-WITH-ROUND7-COMMIT
   test -z "$(git -C "$JOULEWISE_REPO" status --porcelain)"
   test "$(git -C "$JOULEWISE_REPO" rev-parse HEAD)" = "$PINNED_ROUND7_COMMIT"
   test ! -e "$REAL_FILL_DIR"
   mkdir -m 700 "$REAL_FILL_DIR"
   cp "$JOULEWISE_REPO/docs/paper/draft-v1.md" "$REAL_FILL_DIR/draft-v1.round7-working.md"
   ```

2. Bind and authenticate the `_v5` identity inputs before any artifact. The
   panel must carry model IDs `qwen3-1p7b` and `qwen3-8b`, their frozen
   revisions, tokenizer SHA-256
   `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`,
   chat-template SHA-256
   `87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`,
   template application enabled, and thinking disabled. The decode workload
   must be `real_prompts_v1`, eight ordered prompts, prompt-set SHA-256
   `20debdb41eb4983339a160176dcf4e475153b5d6f16b1ef3ada39447e99f3474`,
   greedy, forced 512.

   ```sh
   export MODEL_PANEL="$JOULEWISE_REPO/configs/model_panels/qwen3_4bit.json"
   export DECODE_WORKLOAD="$JOULEWISE_REPO/configs/workloads/real_prompts_v1.json"
   export G2A_SELECTION=/ABSOLUTE/g2a-prefill-selection.json
   export PREFILL_PROMPT_PIN=/ABSOLUTE/prefill-prompt-pin-v2.json
   test -f "$MODEL_PANEL"
   test -f "$DECODE_WORKLOAD"
   test -f "$G2A_SELECTION"
   test -f "$PREFILL_PROMPT_PIN"
   ```

   Record the G2-a file SHA-256. Require schema
   `joulewise.g2a_prefill_selection.v1`, ladder `512/1024/2048/4096`, at least
   five small-model members at every evaluated rung, count at least five in
   every member of any qualifying rung, and
   `[PREFILL_LENGTH] = collection_prefill_tokens`. A `status=refused` record may
   still authorize collection at 4096; a malformed record with a null
   `collection_prefill_tokens` does not. Require the prompt pin to be
   `joulewise.prefill_prompt_pin.v2`, carry that exact G2-a SHA-256, and match
   the selected length in both `prefill_length` and `prompt_tokens`.

3. Bind the issued producers by exact artifact ID, never array position:

   ```sh
   export ALPHA_WHOLE_WINDOW_VERDICT=/ABSOLUTE/qwen3-1p7b/whole-window-verdict.json
   export ALPHA_AGGREGATE_FLOOR_MINT=/ABSOLUTE/qwen3-1p7b/aggregate-floor-artifact.json
   export ALPHA_DETECTION_FLOOR_EXTRACTION=/ABSOLUTE/qwen3-1p7b/detection-floor-extraction.json
   export BETA_WHOLE_WINDOW_VERDICT=/ABSOLUTE/qwen3-8b/whole-window-verdict.json
   export BETA_AGGREGATE_FLOOR_MINT=/ABSOLUTE/qwen3-8b/aggregate-floor-artifact.json
   export BETA_DETECTION_FLOOR_EXTRACTION=/ABSOLUTE/qwen3-8b/detection-floor-extraction.json
   export GAMMA_CLAIM_VERDICT=/ABSOLUTE/qwen3-contrast/claim-verdicts.json
   export D165_COMMON_MODE_REPLAY=/ABSOLUTE/qwen3-contrast/d165-common-mode-replay.json

   export ALPHA_PREFILL_FLOOR_ARTIFACT_ID=d117-qwen3-1p7b-prefill-p[PREFILL_LENGTH]-floor-v5
   export ALPHA_DECODE_FLOOR_ARTIFACT_ID=d117-qwen3-1p7b-decode-floor-v5
   export BETA_PREFILL_FLOOR_ARTIFACT_ID=d117-qwen3-8b-prefill-p[PREFILL_LENGTH]-floor-v5
   export BETA_DECODE_FLOOR_ARTIFACT_ID=d117-qwen3-8b-decode-floor-v5
   export GAMMA_DECODE_CONTRAST_ID=ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b
   export GAMMA_PREFILL_CONTRAST_ID=ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b
   ```

   Substitute `[PREFILL_LENGTH]` in these shell values only after step 2 passes.
   Hash every artifact into the fill ledger. A comparative R_cm value is
   unavailable unless the registered `d165_shared_sign_local_corner_replay.v1`
   result can be authenticated against the same custodied block inputs.

4. Prove the frozen baseline before replacement:

   ```sh
   shasum -a 256 docs/paper/draft-v1.md
   # 939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab

   grep -oE '[[]PENDING[^]]*[]]' docs/paper/draft-v1.md \
     | awk '{ sites += 1; slots += (/,/ ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
   # sites=34 slots=36

   grep -oE '[[](PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)[]]' \
     docs/paper/draft-v1.md \
     | awk '{ sites += 1; slots += (/^[[]PENDING,/ ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
   # sites=37 slots=39

   grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*[[](PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)' \
     docs/paper/results-fill-registry.md
   # 37
   ```

5. Run the replay fence on the unfilled working copy. Corpus absence is failure,
   never a skip.

   ```sh
   PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$JOULEWISE_REPO/scripts/check_paper_replay_fence.py" \
     --repository-root "$JOULEWISE_REPO" \
     --corpus-root "$PAPER_REPLAY_CORPUS_ROOT" \
     --draft "$REAL_FILL_DIR/draft-v1.round7-working.md" \
     --json "$REAL_FILL_DIR/replay-fence-batch0.json"
   ```

## Batch 1 — atomic renderer route (§7 + §6)

Do not run the current pre-`_v5` renderer as a fill producer. After a successor
is regenerated against the 126-row registry namespace, run it exactly once,
preserve stdout and stderr, and require either a zero exit plus its complete
validation or a nonzero exit with no replacement prose and exactly one
machine-readable `STOP_FILL`. Never splice values from an atomic refusal.

| Placement row | Draft site | Supplier and fill rule |
|---|---|---|
| DS-08a | line 274, complete result-branch hold | Replace the entire marker only with one validated atomic §7/§6 result. Until a `_v5` renderer exists, use: “The prospective Results branch is omitted: the registered renderer has not been regenerated for the `_v5` model, workload, ratio, and G2-a bindings (registry row DS-08a).” |

Batch-1 fence: replay-fence success plus either validated atomic output or one
ledgered omission. Partial renderer output is always discarded.

## Batch 2 — TERM labels, R/R_cm columns, and the dominance disclosure

Create one immutable 32-row derivation record. TERM A/B use the formulas in the
registry and preserve producer array order with `math.fsum`. Independent R uses
the complete `corner_widened_unguarded_floor_j` numerator and the re-derived
unguarded point denominator. A zero denominator refuses; do not emit infinity.
Comparative R_cm comes only from the registered replay. Absolute R_cm prints the
registered not-applicable reason, never a number.

| Registry key | Supplier | Rule / disposition |
|---|---|---|
| `TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_abs_J` | alpha selected prefill absolute parents | guarded point label term; unresolved until G2-a |
| `TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_abs_J` | alpha selected prefill absolute arrays | legacy absolute corner label; unresolved until G2-a |
| `R_1p7B_prefill_p[PREFILL_LENGTH]_abs` | alpha selected prefill absolute component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_1p7B_prefill_p[PREFILL_LENGTH]_abs` | D-165 registration | `not_applicable`; deviations-from-mean cancels uniform shift |
| `TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J` | alpha selected prefill comparative parents | guarded point label term; unresolved until G2-a |
| `TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J` | alpha selected prefill comparative arrays | legacy comparative corner label; unresolved until G2-a |
| `R_1p7B_prefill_p[PREFILL_LENGTH]_cmp` | alpha selected prefill comparative component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp` | registered replay over alpha prefill blocks | mandatory; `<2.0` withdraws dominance sentence |
| `TERM_A_1p7B_decode_abs_J` | alpha decode absolute parents | guarded point label term |
| `TERM_B_1p7B_decode_abs_J` | alpha decode absolute arrays | legacy absolute corner label |
| `R_1p7B_decode_abs` | alpha decode absolute component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_1p7B_decode_abs` | D-165 registration | `not_applicable`; deviations-from-mean cancels uniform shift |
| `TERM_A_1p7B_decode_cmp_J` | alpha decode comparative parents | guarded point label term |
| `TERM_B_1p7B_decode_cmp_J` | alpha decode comparative arrays | legacy comparative corner label |
| `R_1p7B_decode_cmp` | alpha decode comparative component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_1p7B_decode_cmp` | registered replay over alpha decode blocks | mandatory; `<2.0` withdraws dominance sentence |
| `TERM_A_8B_prefill_p[PREFILL_LENGTH]_abs_J` | beta selected prefill absolute parents | guarded point label term; unresolved until G2-a |
| `TERM_B_8B_prefill_p[PREFILL_LENGTH]_abs_J` | beta selected prefill absolute arrays | legacy absolute corner label; unresolved until G2-a |
| `R_8B_prefill_p[PREFILL_LENGTH]_abs` | beta selected prefill absolute component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_8B_prefill_p[PREFILL_LENGTH]_abs` | D-165 registration | `not_applicable`; deviations-from-mean cancels uniform shift |
| `TERM_A_8B_prefill_p[PREFILL_LENGTH]_cmp_J` | beta selected prefill comparative parents | guarded point label term; unresolved until G2-a |
| `TERM_B_8B_prefill_p[PREFILL_LENGTH]_cmp_J` | beta selected prefill comparative arrays | legacy comparative corner label; unresolved until G2-a |
| `R_8B_prefill_p[PREFILL_LENGTH]_cmp` | beta selected prefill comparative component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp` | registered replay over beta prefill blocks | mandatory; `<2.0` withdraws dominance sentence |
| `TERM_A_8B_decode_abs_J` | beta decode absolute parents | guarded point label term |
| `TERM_B_8B_decode_abs_J` | beta decode absolute arrays | legacy absolute corner label |
| `R_8B_decode_abs` | beta decode absolute component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_8B_decode_abs` | D-165 registration | `not_applicable`; deviations-from-mean cancels uniform shift |
| `TERM_A_8B_decode_cmp_J` | beta decode comparative parents | guarded point label term |
| `TERM_B_8B_decode_cmp_J` | beta decode comparative arrays | legacy comparative corner label |
| `R_8B_decode_cmp` | beta decode comparative component | corner-widened unguarded / point unguarded; `>=2.0` |
| `R_cm_8B_decode_cmp` | registered replay over beta decode blocks | mandatory; `<2.0` withdraws dominance sentence |

The paper title is protocol-first and fixed before collection. The
“Attribution-limited” subtitle and dominance sentence appear only when all
eight independent R columns pass and no comparative R_cm is below 2.0. Exact
R equality passes. Any failed, missing, or refused R/R_cm removes the subtitle;
comparative `R_cm < 2.0` expressly withdraws the sentence. Report component and
cell columns even when the joint disclosure fails.

Batch-2 fence: the immutable record contains exactly 32 unique registry keys,
all parent artifact hashes, eight R dispositions, four comparative R_cm
dispositions, and four absolute not-applicable reasons. Replay fence remains
green before continuing.

## Batch 3 — authenticated hand fills (draft order)

The frozen draft's physical 1.5B/7B labels are anchor text only. Every supplier
below is the ruled Qwen3 pair. Use exact IDs, record old/new bytes and supplier
SHA-256 in the ledger, and edit only the working copy.

| Placement row | Draft site | Supplier and fill rule |
|---|---|---|
| DS-01 | line 189, operative-floor hold | Four `_v5` alpha/beta prefill/decode cells. Copy `floor_abs_j` and `floor_cmp_j`; derive their maximum and require exact equality with `floor_gate_j`. |
| DS-11 | line 280, small-model prefill floor | `d117-qwen3-1p7b-prefill-p[PREFILL_LENGTH]-floor-v5`; fill only after G2-a and prompt-pin v2 authenticate the selected length. |
| DS-15 | line 281, large-model prefill floor | `d117-qwen3-8b-prefill-p[PREFILL_LENGTH]-floor-v5`; same G2-a gate. |
| DS-19 | line 282, small-model decode floor | `d117-qwen3-1p7b-decode-floor-v5`, bound to `real_prompts_v1` and the panel renderer pins. |
| DS-23 | line 283, large-model decode floor | `d117-qwen3-8b-decode-floor-v5`, same workload and renderer pins. |
| DS-25 | line 289, decode point | Contrast `ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b` → authenticated B-minus-A estimator. |
| DS-26 | line 289, decode interval | Same contrast → fully composed lower and upper endpoints; one physical marker supplies two slots. |
| DS-27 | line 289, decode floor | Maximum of the two issued decode `floor_gate_j` values; require exact equality with the gamma contrast's registered active floor. |

Batch-3 fence: replay fence green; eight unique ledger rows; DS-26 decrements
one marker site and two semantic slots.

## Batch 4 — diagnostics, release locator, and NEEDS-VALUE notes

DG-071 and DG-075 have ratified statistics issued by PR #276 in
`docs/paper/round7/dg071-dg075-statistics.md` (SHA-256
`041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b`) and
`docs/paper/round7/dg071-dg075-statistics.json` (SHA-256
`9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7`); see
the 2026-08-31 [ratification](../../process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md).
Their old pause mechanism is contradicted by retained bytes: records tile with
no meaningful gap, and the former 111.8–112.5 ms band is the bottom of the
width distribution rather than its range.

| Placement row | Draft site | Supplier status and placement |
|---|---|---|
| DG-071 | Section 6 diagnostic prose | Place the issued n = 406, median 120.9186 ms, and IQR 5.9508 ms exactly as rendered by the pinned artifact. Define IQR at first use; retain the diagnostic-era, non-claim-bearing qualification. |
| DG-075 | Section 6 diagnostic prose | Place the issued n = 405, median 120.9224 ms, and IQR 5.8949 ms exactly as rendered by the pinned artifact. State that the records tile and that spacing is the DG-071 record-period distribution minus the first record, apart from the issued endpoint convention. |
| DX-010 | successor-draft excursion prose, onset median | Place only as `[FILL:DX-010]` under the mandatory DX standing paragraph; R7F checks the rendered literal. |
| DX-011 | successor-draft excursion prose, offset median | Place only as `[FILL:DX-011]` under the mandatory DX standing paragraph; R7F checks the rendered literal. |
| DX-012 | successor-draft excursion prose, positive-onset count | Place only as `[FILL:DX-012]`; print the count instead of “repeatably.” |
| DX-013 | successor-draft excursion prose, negative-offset count | Place only as `[FILL:DX-013]`; print the count instead of “repeatably.” |
| DX-014 | successor-draft excursion prose, onset MAD | Place only as `[FILL:DX-014]` under the mandatory DX standing paragraph. |
| DX-015 | successor-draft excursion prose, offset MAD | Place only as `[FILL:DX-015]` under the mandatory DX standing paragraph. |
| DX-016 | successor-draft excursion prose, bias share | Place only as `[FILL:DX-016]`; use the registered derivation and rounding. |
| DX-017 | successor-draft excursion prose, worst-onset excess | Place only as `[FILL:DX-017]`; use the registered derivation and rounding. |
| DX-020 | successor-draft anchor prose, population | Place only as `[FILL:DX-020]` under the mandatory DX standing paragraph. |
| DX-021 | successor-draft anchor prose, derived/refused counts | Place only as `[FILL:DX-021]`; keep the three refusals in the anchor-delta sentence. |
| DX-022 | successor-draft anchor prose, admissibility flips | Place only as `[FILL:DX-022]` under the mandatory DX standing paragraph. |
| DX-023 | successor-draft anchor prose, v2 control | Place only as `[FILL:DX-023]`; keep the named control failure in the anchor-delta sentence. |
| DX-024 | successor-draft anchor prose, median bound delta | Place only as `[FILL:DX-024]` under the mandatory DX standing paragraph. |
| DX-025 | successor-draft anchor prose, maximum bound delta | Place only as `[FILL:DX-025]` under the mandatory DX standing paragraph. |
| DX-026 | successor-draft anchor prose, maximum relative delta | Place only as `[FILL:DX-026]` under the mandatory DX standing paragraph. |
| DX-027 | successor-draft anchor prose, median relative delta | Place only as `[FILL:DX-027]`; use AQ's real `median_pct` field and registered rounding. |
| DS-34 | line 348, release hold | Until the release checklist issues repository, archive, and digest locators: “Repository and archive locators are omitted: the release checklist has not issued the registered locator set (registry row DS-34).” |

Cross-row census note: `37 + 13 = 50` is a sum across DG-076 and DG-077 that
must equal the DG-068 population total; DG-069's 13 identifiable phases
corroborate the second addend. Re-check this equality whenever DG-068, DG-069,
DG-076, or DG-077 is reissued.

Replace the two explanatory `[[NEEDS-VALUE:...]]` notes only in the working copy:

| Draft site | Exact omission |
|---|---|
| line 272, exact F/B/margin note | “The exact planning components F and B and any fixed margin are omitted: no exact claim-side-bound supplier is built.” |
| line 276, D-123 schema note | “The D-123 per-token numerator, denominator, and point-or-interval rendering are omitted because the producing schema is not built.” |

Batch-4 fence: replay fence green; five new ledger entries for five physical
sites. Neither proposed diagnostic becomes fillable without ratification and
an issued, path- and SHA-pinned artifact.

## STOP_FILL rows

These complete omission sentences preserve the supplier-freeze discipline.
For the prefill rows, `[PREFILL_LENGTH]` is substituted only after Batch 0.
D-166's exhausted-ladder branch remains split: reducer count below 3 prints
`not_resolvable_sample_count`; a resolvable count of 3–4 prints “below the
pre-registered count floor of 5” and discloses the reducer's result.

| Placement row | Exact sentence replacing the marker |
|---|---|
| DS-09 | “The Qwen3-1.7B prefill-p[PREFILL_LENGTH] gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-09).” |
| DS-10 | “The Qwen3-1.7B prefill-p[PREFILL_LENGTH] per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-10).” |
| DS-12 | “The Qwen3-1.7B prefill-p[PREFILL_LENGTH] bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-12).” |
| DS-13 | “The Qwen3-8B prefill-p[PREFILL_LENGTH] gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-13).” |
| DS-14 | “The Qwen3-8B prefill-p[PREFILL_LENGTH] per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-14).” |
| DS-16 | “The Qwen3-8B prefill-p[PREFILL_LENGTH] bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-16).” |
| DS-17 | “The Qwen3-1.7B `real_prompts_v1` decode gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-17).” |
| DS-18 | “The Qwen3-1.7B `real_prompts_v1` decode per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-18).” |
| DS-20 | “The Qwen3-1.7B `real_prompts_v1` decode bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-20).” |
| DS-21 | “The Qwen3-8B `real_prompts_v1` decode gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-21).” |
| DS-22 | “The Qwen3-8B `real_prompts_v1` decode per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-22).” |
| DS-24 | “The Qwen3-8B `real_prompts_v1` decode bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-24).” |
| DS-28 | “The decode sizing sum and signed clearance are omitted: the claim-side bound and one-cell/two-quantity rendering are unresolved (registry row DS-28).” |
| DS-29 | “The decode claim-side bound is omitted: no producing artifact field is registered, and `deterministic_bounds.total` is not a substitute (registry row DS-29).” |
| DS-30 | “The decode floor-gate outcome is omitted: no exact conservative rendering token is registered (registry row DS-30).” |
| DS-31 | “The decode direction-gate outcome is omitted: no exact conservative rendering token is registered (registry row DS-31).” |
| DS-32 | “The decode verdict is omitted: no professor-facing conservative rendering token is registered (registry row DS-32).” |
| DS-33 | “The selected `_v5` prefill claim floor is omitted: `[PREFILL_LENGTH]` is unresolved until G2-a and no professor-facing prefill token is registered (registry row DS-33).” |
| PG-01 | “The selected `_v5` prefill contrast estimate is omitted: `[PREFILL_LENGTH]` is unresolved until G2-a and no authenticated estimate token is registered (registry row PG-01).” |
| PG-02 | “The selected `_v5` prefill interval is omitted: `[PREFILL_LENGTH]` is unresolved until G2-a and no authenticated lower or upper endpoint tokens are registered (registry row PG-02).” |
| PG-04 | “The selected `_v5` prefill sizing sum and signed clearance are omitted: the claim-bound token family and rendering contract are not registered (registry row PG-04).” |
| PG-05 | “The selected `_v5` prefill claim-side bound is omitted: no named producing field or rendering token is registered (registry row PG-05).” |
| PG-06 | “The selected `_v5` prefill floor-gate outcome is omitted: no conservative rendering token is registered (registry row PG-06).” |
| PG-07 | “The selected `_v5` prefill direction-gate outcome is omitted: no conservative rendering token is registered (registry row PG-07).” |
| PG-08 | “The selected `_v5` prefill verdict is omitted: no authenticated professor-facing verdict token is registered (registry row PG-08).” |

`[B_decode_claim_J]` remains `STOP_FILL` exactly as ruling item 33 requires:

```text
STOP_FILL {"label": "SUPPLIER_UNKNOWN", "reason": "the registry freezes this token but defines no producing artifact field", "registry_row": "[B_decode_claim_J]"}
```

## Post-fill closure

1. Validate any successful atomic renderer output with the same `_v5` renderer
   binary and record its source hash. If Batch 1 omitted, record that omission
   instead; do not invoke the old renderer as evidence.

2. Run the replay fence on the final working draft and require:

   ```text
   COMPARED 43
   MISMATCHES 0
   ```

3. Recount the working copy. Starting counts are literal `34/36`, complete
   result-marker family `37/39`, and two `NEEDS-VALUE` notes. Every ledgered
   replacement decrements one site and one slot except DS-26 and PG-02, which
   each decrement one site and two slots.

4. Require the registry and checklist placement ledgers to agree exactly:

   ```sh
   "$PYTHON" - <<'PY'
   import re
   from collections import Counter
   from pathlib import Path

   registry = Path("docs/paper/results-fill-registry.md").read_text(encoding="utf-8")
   checklist = Path("docs/paper/round7/fill-checklist.md").read_text(encoding="utf-8")
   pattern = r"^\| ((?:DS|PG|DG|DX)-[0-9]+[a-z]?) \|"
   placed = Counter(re.findall(pattern, checklist, re.M))
   expected = [
       "DS-01", "DS-08a", *[f"DS-{n:02d}" for n in range(9, 35)],
       "PG-01", "PG-02", *[f"PG-{n:02d}" for n in range(4, 9)],
       "DG-071", "DG-075",
       *[f"DX-{n:03d}" for n in (*range(10, 18), *range(20, 28))],
   ]
   assert len(expected) == 53
   assert set(placed) == set(expected), (set(expected) - set(placed), set(placed) - set(expected))
   assert all(placed[row] == 1 for row in expected), placed
   assert len(re.findall(r"^\| (?:DS|PG|DG)-[0-9]+[a-z]? — .*[[](?:PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)", registry, re.M)) == 35
   print("ROWS 53/53 PLACED ONCE; RF PENDING CENSUS 35")
   PY
   ```

5. Record the final draft SHA-256, source hashes, fill ledger SHA-256, 32-row
   dominance record SHA-256, replay-fence output, renderer validation/refusal,
   and marker census in the custody directory. Any unmatched change is
   `STOP_FILL`.

## Open gaps (NEEDS-RULING or implementation gates)

1. **G2-a issuance:** `[PREFILL_LENGTH]` and every selected prefill identifier
   remain unresolved until the selection output and prompt-pin v2 are issued
   and mutually hash-bound.
2. **Renderer regeneration:** the current renderer/template use pre-`_v5`
   model keys and do not consume the new R/R_cm ledger. They must be regenerated
   before Batch 1 can fill.
3. **D-123 writer:** reported means, composed intervals, per-token companions,
   and admitted independent-bundle counts have no issued schema.
4. **Claim-side bound:** `[B_decode_claim_J]` and the corresponding prefill
   claim-side bound have no supplier. `deterministic_bounds.total` remains
   forbidden as a substitute.
5. **Prefill professor-facing tokens:** the generator names the selected
   contrast, but Table 3 estimate, interval, floor, gate, bound, and verdict
   renderings remain unbuilt. D-166's reducer-refusal and pre-registration-
   refusal branches must stay distinct.
6. **Release and characterization writers:** DS-34 and the frozen
   characterization result fields remain unissued.

No open gap makes a stopped row fillable. The protocol-first title is already
ruled and does not need an outcome-C title decision.
