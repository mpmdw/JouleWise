# Block-5 Results renderer

Prepared blind, 2026-11-05. This is a mechanical **paper candidate**, not an
issuing supplier or a release event. No study output was opened to build it.

## Authority and limits

- `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:631–638`
  supersedes the retired renderer: print **every** validated contrast in order,
  including unsupported/refused rows; validate row-for-row; pass the Results
  cold gate before paper use. `analysis_plan_block5.md:171–180` (under
  `configs/campaigns/v5_claim_25g83/`) supplies steps 11/12 and outcome treatment.
- The runbook on `origin/lane/2026-11-05-b5-release-runbook`, file
  `docs/process/b5_release_runbook.md`, §5 and gap 6, supplies the ordering:
  release event, verified release, independent recompute, fill, cold gate.
  The lead must settle its independent-recompute/event-order gap separately.
- `docs/decision_log.md:12239–12272` (D-188–D-190) distinguishes exact release
  equivalence from independent recomputation, preserves step-9b non-issuance,
  and carries registered null outcomes. `RUN_STATE.md:339–342`, item 83 ruling
  3 in this checkout, requires a reader hand-check for any printed uncovered
  step-11 leaf. The handoff brief calls this item 84; the quoted ruling is the
  same one. The historical 624 count is not a hard-coded renderer census.
- `docs/paper/results-fill-registry.md:1–79,1130–1154,1181–1191` and
  `docs/contracts/paper_comparison_placements.md:3–43` keep the retired and
  proposed placements stopped. `paper_comparison_rendering.md:27–43,45–77`
  (same contracts directory) leaves bindings unbound and requires
  `open_paper_input` for empirical issuance. Neither release hashes nor this
  renderer construct `VerifiedClaimEvidence` or authorize an empirical claim.

## Inputs: released bytes only

`scripts/render_b5_results.py` takes explicit `--release-dir`, `--artifacts-dir`,
`--comparison`, `--recompute`, and optionally `--window-index` (default: the
tracked index). The artifacts root is the operator's **post-event** root for
record-relative names; no input is discovered by walking a custody tree.
Absolute paths embedded inside JSON remain text. Raw bundles, archives,
measurement roots, evidence paths and live ledgers are never followed.

`B5-RELEASE-RECORD.json` must name a completed release through step 11, with
only D-189's exact optional non-stopping 9b row, no release difference and
unique output names/digests. The lead still verifies release equality, seal and
program pins, the event, authorized readers and absence of claim custody;
the renderer is not a replacement release authenticator.

Here `H` denotes exactly 64 lowercase hexadecimal characters. Every referenced
file is opened without symlinks and its **file bytes** must match the record's
SHA-256; a matching filename alone is insufficient.

| Released file | Consumed fields / use |
|---|---|
| Step 11 `outputs/H-results-fill-input.json` | Exact extended `results_fill_input.v1` shape: campaigns, characterization, gamma identity/parent digests and **all** gamma contrasts. Each row's metric, conditions, limitations, source cells, estimate, interval, decision interval, deterministic widening, J/token, n, floor, multiplicity, evaluation, plan/role/direction/equivalence, sampling, LOO, df, t critical and kept/removed blocks are retained. |
| Step 9 `outputs/H-claim-verdicts.json` | Gamma digest/identity and every row's parent fields; the renderer rechecks the adapter's copy projection without recomputing a result. |
| Step 11 `disclosures/H.json` | `b5_disclosures.v1`: windows, cells, floors, contrasts, window lines, block lines, sensitivity and fixed sentences. Every released disclosure line is included. |
| Step 11 `disclosures/H.released.txt`, `disclosures/H.unreleased.txt` | Both must equal `render_disclosures(record, released=True/False)` exactly. Only the released view enters Results. |
| Structural output dependencies | The comparator's closed `check_doc` map (`scripts/compare_b5_recompute.py:871–889`) also reads recorded projections for alpha/beta, extraction reports, aggregate floor, closeout/ratio table, block/window brackets, kept-unit records and sensitivity as needed by its registered expected-check table. No arbitrary caller source is accepted. Every read digest is added to `bindings.structural_sources`. |
| Independent comparison JSON | `b5_recompute_comparison.v1`: block-5 `bar_set` and `bars`, `structure_flags`, `counts`, `comparisons`, `expected_checks`, registry/program digests and full `coverage`. Any disagreement, unmapped/unbound leaf, absent source, nonfinite or structure flag blocks output, including previews. |
| Independent recompute JSON | `independent_recompute_b5.v1`, mode `REGISTERED`, matching program digest; provides structural cross-checks and concrete reader-check pointers. The operator supplies the matching comparison/recompute pair from the independent handoff. This renderer does not rerun arithmetic or authenticate that external invocation. |
| Window index | Bytes must match the release's `window_index_sha256`; parsed for the registered attempt-history census only. None of its paths is followed. |

Implementation reuses the independent comparator's registered identity routing,
expected-check table, strict step-11 parse, leaf rules and bars. It rebuilds the
structural table and coverage over the released bytes rather than accepting a
report's coverage label alone. It also compares each concrete printed leaf's
value/type to its exact comparison row. Missing/extra fields, rows, keys or
bindings refuse. No tolerance or estimator is introduced here.

## Outputs and reader workflow

The new paper-tree template is `docs/paper/block5/Results.template.md`. Suggested
candidate destination: a **new** `docs/paper/block5/generated-<release-id>/`
directory. It contains `Results.md` (complete contrast table, all contrast
fields, literal released disclosures) and `provenance.json` / `provenance.md`.
The existing `draft-v2-skeleton.md`, build inputs, abstract and conclusion are
unchanged. **NEEDS-LEAD:** adopt final section/table anchors and any figure
specification; no empirical figure or headline selection is invented.

For a later authorized post-release reader, with the paths supplied by the
owning handoff (these commands were not run on study data in this lane):

```sh
python3.13 -B scripts/render_b5_results.py \
  --release-dir "$RELEASE" --artifacts-dir "$ARTIFACTS" \
  --comparison "$COMPARISON" --recompute "$RECOMPUTE" --window-index "$INDEX" \
  --prepare-checks "$NEW_CHECKS"
```

Repeat the same input arguments with `--checks "$NEW_CHECKS"` and one mode:

- `--preview "$NEW_PREVIEW_DIR"`: structurally validated candidate labelled
  `PENDING / REVIEW CANDIDATE ONLY`; may contain pending reader checks. This
  is the review material for the cold gate, never permission to use a number.
- `--out "$NEW_CHECKED_DIR"`: requires every pending leaf to be hand-checked
  and the reader/release-event and independent judge/refuter cold-gate record
  references to be filled in. It still retains STOP_FILL / NEEDS-LEAD paper
  placement labels. A record reference is an attributed attestation, not a
  cryptographic proof that a human performed a review.
- `--validate-rendered "$CHECKED_DIR"`: reloads/revalidates the inputs and
  checks, re-renders, then compares every output byte and the complete file
  census. Edited, dropped, duplicated, reordered or added rows refuse.

No output is overwritten. All files are staged before publishing the new
directory. CLI failures return 2 with a fixed code, never values or tracebacks.

## Provenance, states and precision

Each scalar or empty container in fill/disclosures has a **concrete RFC 6901
pointer**, including array indices, released relative filename and file SHA-256.
Provenance JSON records its raw value, display value and check. It also binds
the release record, both views, verdicts, index, structural dependencies,
comparison, recompute and template file digests, the canonical review digest,
and rendered Results hash.
The Markdown table supplies value/text → file#pointer → SHA-256 → status.

`AUTO_AGREE` names the exact comparator family/key; a comparator qualification
such as `within_bar_undetermined` is retained, never upgraded to a directional
claim. `LISTED` marks nonnumeric identity/control/structure. All uncovered
numbers and nulls, numeric strings, and **every disclosure text leaf** start
`PENDING`. Text is not covered merely because its adjacent typed value agrees.
For each, the reader changes the status to `HAND_CHECKED`, names the reviewer,
lists resolvable `recompute_pointers`, and records the comparison in `note`.
These attestations bind exact input digests and exact leaf sets; changing any
input or removing/adding a check invalidates them. They do not turn an
uncovered value into an automatic numerical comparison.

No contrast is selected or dropped. Outcome, direction, ceiling, reasons and
limitations are copied as issued identifiers, not translated into invented
claim prose. Registration §0.10 (`registration_block5.md:814–817`) says:
“A contrast whose estimate does not exceed its floor is reported as
`not_resolvable`”. Natural-language claim sentences remain **NEEDS-LEAD**;
only producer-issued registered disclosure wording is copied verbatim.
D-190's “not estimable (n = …; fewer than 2 complete quads)”, “decision interval
not available (not estimable)”, “floor not resolvable” and sensitivity “not
available” remain in that view. Tables/details print `not available (null)`
for null leaves, never zero. Step 9b non-issuance is shown explicitly and
leaves claim-evidence fills STOP_FILL; it is not an empirical negative claim.

The registry's MEASURED/DERIVE/STOP_FILL rules govern publication. This
candidate copies JSON numbers losslessly (no arithmetic or default rounding)
and preserves the producer's already formatted disclosure text. There is no
active block-5 numeric placement/precision rule to adopt wholesale from the
retired template; **NEEDS-LEAD:** bind each final site's registry precision.
The block-5 recompute bars are not a print-precision rule (item 83 ruling 2).

## NEEDS-LEAD before paper use

Adopt issuing routes/placements, final digits, headline emphasis and any claim
sentences/figures; perform actual release verification and the independent
Results cold gate. This lane supplies no production paper issuance.

**Existing null-comparator gap:** `scripts/compare_b5_recompute.py:212–222,
2199–2233` treats null numeric contrast/floor values as disagreements;
`tests/independent_recompute/test_input_gate.py:522–531` explicitly preserves
the refused-arm-null case as unmapped. Therefore some legitimate D-190 releases
cannot yet pass this upstream gate. The renderer's display function handles
those null shapes, but the end-to-end CLI refuses a failed report. The lead
must arrange an authorized comparator repair/review or a separately governed
recompute disposition; this lane neither waives the gate nor changes bars.
Synthetic success establishes renderer behavior, not live release readiness.
