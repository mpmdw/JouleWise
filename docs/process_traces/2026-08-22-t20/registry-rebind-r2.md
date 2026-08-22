# Results-fill registry re-binding candidate R2

**Target.** `docs/paper/draft-v1.md` at repository head
`3f931d5a405081c9177466635f08170b1d1c8bb2` (`main`), current draft length
`551` lines. This is a read-only audit and adoption candidate; no repository file
was changed. Every anchor below was located by content. Line numbers are locators
only.

**Verdict vocabulary.** `OK` means the locator, marker, and meaning remain correct;
`STALE-REF` means the content site and binding remain correct but locator metadata
is stale; `ORPHANED` means the registry's recorded exact marker no longer occurs;
`SHIFTED` means the site's surrounding meaning changed enough that the binding
requires a lead ruling.

## Binding rules preserved verbatim

Numeric characters in this document occur only inside binding identifiers,
model names, source locators, and the required census; no measured result or
demonstration value appears.

No historical result is a supplier for this registry. Under D-117, claim
authority can arise only from prospective alpha, beta, and gamma evidence;
D-122 adds a prospectively frozen prompt-processing contrast to gamma; and
D-123 adds reported phase-energy mean cells to alpha and beta, conditional on
the required no-semantics-change check.

Fill-rule vocabulary is closed:

- `MEASURED`: copy or conservatively render an authenticated issued artifact
  field. Never calculate a replacement from prose.
- `DERIVE`: compute only the formula or renderer rule named here from
  authenticated parents. Reject an independently supplied value.
- `STOP_FILL`: do not render a value. This includes an unknown supplier,
  absent required parent, failed predicate, malformed reason, or unissued
  governing verdict.

Freeze labels distinguish a frozen key or derivation from an issued value.
`KEY_FROZEN / VALUE_UNISSUED` means the vocabulary is fixed but no result may
be inserted. `SUPPLIER_UNKNOWN` identifies a missing field contract, not a
license to infer one.

### Folded preconditions

- **F2 — folded.** Capture-method era is an independent fill precondition:
  claim-bearing evidence must positively name a current claim-bearing anchor
  method. Re-registering or re-deriving a historical corpus does not turn it
  into a supplier. This strengthens, and does not replace, the verbatim
  D-117/D-122/D-123 rule above.
- **F5 — folded.** Every comparative `floor_cmp_j` supplier must authenticate
  the estimator selected by the prospectively fixed plan. Estimator identity
  is never accepted from a result or floor artifact, and a comparative value
  produced under another estimator is not interchangeable.

## Exact template-token registry verification

The current registry's bindings for the `91` exact tokens recognized by
`DRAFT-RESULTS_PROSE.md` are carried forward unchanged, except for the F1
known-code clarification below. I rescanned the template with
`\[([A-Z][A-Za-z0-9_*.-]*)\]` and retained both the occurrence stream and its
distinct set.

| Check | Registry claim | Observed at target head | Drift |
|---|---:|---:|---|
| Recognized token occurrences | `436` | `436` | none |
| Distinct recognized tokens | `91` | `91` | none |
| Intended template tokens failing to key | none | none | none |

A literal set comparison against the current registry found `93` token-shaped
rows before the draft-site section. The additional two are the explicitly
documented swap-block-only keys
`[F_decode_contrast_cmp_two_edge_J]` and
`[F_decode_contrast_cmp_worst_case_J]`. They have no landed template
counterpart, are not part of the `91`-key census, and retain their current
`STOP_FILL` guards where applicable. Thus there is no hidden census drift.

### F1 — terminal-refusal known-code set, folded

Add these exact codes to the conservative renderer's closed terminal-refusal
known-code set for
`[TERMINAL_REFUSAL_REASON_1p5B_prompt]`,
`[TERMINAL_REFUSAL_REASON_1p5B_decode]`,
`[TERMINAL_REFUSAL_REASON_7B_prompt]`,
`[TERMINAL_REFUSAL_REASON_7B_decode]`,
`[REFUSAL_REASON_1p5B_floor_window]`, and
`[REFUSAL_REASON_7B_floor_window]`:

| Exact code | Producing source lines verified at target head | Consumer reason registries verified |
|---|---|---|
| `capture_pipeline_absent` | `joulewise/uncertainty_evidence.py:1312`, `:1318`, `:1321` | `joulewise/floor_extraction.py:190`; `joulewise/whole_window.py:199` |
| `capture_pipeline_superseded` | `joulewise/uncertainty_evidence.py:1324` | `joulewise/floor_extraction.py:191`; `joulewise/whole_window.py:200` |

`CLAIM_BEARING_ANCHOR_METHODS` is defined at
`joulewise/uncertainty_evidence.py:1299`; the producer returns no refusal only
for a method in that set. Unknown codes still require `STOP_FILL`; these two
codes are no longer unknown.

## Current-draft marker recount

The grep-based scan of the current draft observed:

| Exact marker class | Occurrences observed |
|---|---:|
| `[RESULT PENDING ISSUED ARTIFACTS]` | `1` |
| Current long `[RESULT PENDING ISSUED ARTIFACTS — …]` hold | `1` |
| `[PENDING]` | `30` |
| `[PENDING, PENDING]` | `2` |
| `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | `1` |
| **Total current bracket-marker sites** | **`35`** |
| **Semantic fill slots represented by those sites** | **`37`** |

The six former characterization result markers are absent. Their current
content successors are specification rows with `TODO-EVIDENCE` guards, not
fillable result cells. The `34` existing registry row identities are all
accounted for below; the prompt contrast contributes the audit's additional
eight uncovered semantic slots.

## Refreshed draft marker-site registry

Quoted anchors are exact byte substrings from the current draft. For table
cells, the exact row anchor is paired with the exact column header and column
position so repeated `[PENDING]` spellings are unambiguous. Every `ORPHANED`
or `SHIFTED` re-binding is `PROPOSED` pending lead ratification.

| ID | Verdict | Exact current-draft anchor matched | Corrected binding candidate |
|---|---|---|---|
| DS-01 | ORPHANED | line `249`: `[RESULT PENDING ISSUED ARTIFACTS]` | **PROPOSED:** Section 3 operative-floor hold; four alpha/beta phase-cell decompositions from all `F_*_abs_J`, `F_*_cmp_J`, and `F_*_operative_J`; `DERIVE`; guarded template output only. |
| DS-02 | ORPHANED | line `321`: `\| Workload response \|` | **PROPOSED:** successor to the former linearity result row; retain `PLAIN_LANGUAGE_RESULT_linearity` and licensed linearity diagnostics only after an issued characterization schema and row verdict exist; otherwise `STOP_FILL / SUPPLIER_UNKNOWN`. The vocabulary/claim mismatch remains lead-owned. |
| DS-03 | ORPHANED | line `322`: `\| Identical-condition null response \|` | **PROPOSED:** retain `PLAIN_LANGUAGE_RESULT_null` and licensed null diagnostics only after an issued schema and row verdict exist; otherwise `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-04 | ORPHANED | line `323`: `\| Deliberate small-difference challenge \|` | **PROPOSED:** successor to the former empirical-floor row; retain `PLAIN_LANGUAGE_RESULT_floor` and licensed floor diagnostics only after an issued schema and row verdict exist; otherwise `STOP_FILL / SUPPLIER_UNKNOWN`. The narrowed claim remains lead-owned. |
| DS-05 | ORPHANED | line `324`: `\| Phase accounting \|` | **PROPOSED:** retain `PLAIN_LANGUAGE_RESULT_phase` and licensed additivity/invariance diagnostics only after an issued schema and row verdict exist; otherwise `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-06 | ORPHANED | line `325`: `\| Drift and recovery \|` | **PROPOSED:** retain `PLAIN_LANGUAGE_RESULT_drift` and licensed excursion/recovery diagnostics only after an issued schema and row verdict exist; otherwise `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-07 | ORPHANED | line `326`: `\| Between-session stability \|` | **PROPOSED:** retain `PLAIN_LANGUAGE_RESULT_between_sessions` and `N_C_eligible_sessions` only after an issued schema and row verdict exist; otherwise `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-08 | ORPHANED | line `358`: `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labelled instrument diagnostics of Sections 3 and 7.]` | **PROPOSED:** Section 6 results branch hold; exactly one guarded template result variant; `DERIVE`; no historical or diagnostic result is a supplier. Template-internal section labels are not draft section locators. |
| DS-09 | STALE-REF | line `364`, col 3 under `Gross J/request (lower, upper)`: `\| prompt processing \| 1.5B \|` | Table 2 prompt/1.5B gross cell; `E_1p5B_prompt_J_per_request` with lower and upper endpoints; `STOP_FILL / SUPPLIER_UNKNOWN` under D-123. |
| DS-10 | STALE-REF | line `364`, col 4 under `J per prompt token`: `\| prompt processing \| 1.5B \|` | Table 2 prompt/1.5B per-token cell; `E_1p5B_prompt_J_per_token`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-11 | STALE-REF | line `364`, col 6 under `Cell floor (labelled)`: `\| prompt processing \| 1.5B \|` | Table 2 prompt/1.5B floor cell; `F_1p5B_prompt_operative_J` plus cell-label branch; `DERIVE / VALUE_UNISSUED`. |
| DS-12 | STALE-REF | line `364`, col 7 under `n`: `\| prompt processing \| 1.5B \|` | Table 2 prompt/1.5B count cell; `N_bundles_1p5B_prompt`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-13 | STALE-REF | line `365`, col 3 under `Gross J/request (lower, upper)`: `\| prompt processing \| 7B \|` | Table 2 prompt/7B gross cell; `E_7B_prompt_J_per_request` with lower and upper endpoints; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-14 | STALE-REF | line `365`, col 4 under `J per prompt token`: `\| prompt processing \| 7B \|` | Table 2 prompt/7B per-token cell; `E_7B_prompt_J_per_token`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-15 | STALE-REF | line `365`, col 6 under `Cell floor (labelled)`: `\| prompt processing \| 7B \|` | Table 2 prompt/7B floor cell; `F_7B_prompt_operative_J` plus cell-label branch; `DERIVE / VALUE_UNISSUED`. |
| DS-16 | STALE-REF | line `365`, col 7 under `n`: `\| prompt processing \| 7B \|` | Table 2 prompt/7B count cell; `N_bundles_7B_prompt`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-17 | STALE-REF | line `366`, col 3 under `Gross J/request (lower, upper)`: `\| token generation \| 1.5B \|` | Table 2 decode/1.5B gross cell; `E_1p5B_decode_J_per_request` with lower and upper endpoints; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-18 | STALE-REF | line `366`, col 5 under `J per output token`: `\| token generation \| 1.5B \|` | Table 2 decode/1.5B per-token cell; `E_1p5B_decode_J_per_token`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-19 | STALE-REF | line `366`, col 6 under `Cell floor (labelled)`: `\| token generation \| 1.5B \|` | Table 2 decode/1.5B floor cell; `F_1p5B_decode_operative_J` plus cell-label branch; `DERIVE / VALUE_UNISSUED`. |
| DS-20 | STALE-REF | line `366`, col 7 under `n`: `\| token generation \| 1.5B \|` | Table 2 decode/1.5B count cell; `N_bundles_1p5B_decode`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-21 | STALE-REF | line `367`, col 3 under `Gross J/request (lower, upper)`: `\| token generation \| 7B \|` | Table 2 decode/7B gross cell; `E_7B_decode_J_per_request` with lower and upper endpoints; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-22 | STALE-REF | line `367`, col 5 under `J per output token`: `\| token generation \| 7B \|` | Table 2 decode/7B per-token cell; `E_7B_decode_J_per_token`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-23 | STALE-REF | line `367`, col 6 under `Cell floor (labelled)`: `\| token generation \| 7B \|` | Table 2 decode/7B floor cell; `F_7B_decode_operative_J` plus cell-label branch; `DERIVE / VALUE_UNISSUED`. |
| DS-24 | STALE-REF | line `367`, col 7 under `n`: `\| token generation \| 7B \|` | Table 2 decode/7B count cell; `N_bundles_7B_decode`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-25 | STALE-REF | line `373`, col 2 under `Point estimate`: `\| token generation, 7B − 1.5B \|` | Table 3 decode point estimate; `E_decode_contrast_signed_J_per_request`; `MEASURED / VALUE_UNISSUED`. |
| DS-26 | STALE-REF | line `373`, col 3 under `Interval [lower, upper]`: `\| token generation, 7B − 1.5B \|` | Table 3 decode interval; `E_decode_contrast_lower_J` and `E_decode_contrast_upper_J`; `MEASURED / VALUE_UNISSUED`; one marker contains two fills. |
| DS-27 | STALE-REF | line `373`, col 4 under `Cell floor`: `\| token generation, 7B − 1.5B \|` | Table 3 decode floor; `F_claim_decode_armwise_max_J`; `DERIVE / VALUE_UNISSUED`. |
| DS-28 | STALE-REF | line `373`, col 5 under `Clearance (point − floor)`: `\| token generation, 7B − 1.5B \|` | Table 3 decode clearance; `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; `DERIVE`; existing draft/template shape mismatch remains live. |
| DS-29 | STALE-REF | line `373`, col 6 under `Claim-side bound`: `\| token generation, 7B − 1.5B \|` | Table 3 decode claim-side bound; `B_decode_claim_J`; `STOP_FILL / SUPPLIER_UNKNOWN`. |
| DS-30 | STALE-REF | line `373`, col 7 under `Floor-gate outcome`: `\| token generation, 7B − 1.5B \|` | Table 3 decode floor-gate outcome; no exact token; `STOP_FILL / TOKEN_MISSING`. |
| DS-31 | STALE-REF | line `373`, col 8 under `Direction-gate outcome`: `\| token generation, 7B − 1.5B \|` | Table 3 decode direction-gate outcome; no exact token; `STOP_FILL / TOKEN_MISSING`. |
| DS-32 | STALE-REF | line `373`, col 9 under `Verdict`: `\| token generation, 7B − 1.5B \|` | Table 3 decode verdict; candidate source remains `contrasts[decode].claim_evaluation.outcome`; no exact rendering token; `STOP_FILL / TOKEN_MISSING`. |
| DS-33 | SHIFTED | line `374`, col 4 under `Cell floor`: `\| prompt processing, 7B − 1.5B \|` | **PROPOSED:** re-bind the existing row only to the prompt contrast floor cell. No prompt claim-floor token exists; `STOP_FILL / TOKEN_FAMILY_MISSING`. The old `SUPERSEDED_DRAFT` description is superseded; the draft arm is live and the template family is missing. |
| DS-34 | STALE-REF | line `450`: `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | Section 9 evidence/code-availability locator hold; release-manifest fields for repository commit, archive locator, and digest manifest; `STOP_FILL / SUPPLIER_UNKNOWN`. |

### Verdict totals for the existing `34` identities

| Verdict | Count | IDs |
|---|---:|---|
| OK | `0` | — |
| STALE-REF | `25` | DS-09–DS-32, DS-34 |
| ORPHANED | `8` | DS-01–DS-08 |
| SHIFTED | `1` | DS-33 |

## Audit §1.3 coverage gap — full proposed rows

The prompt row at current line `374` has eight markers and nine semantic slots.
DS-33 covers only its floor slot, provisionally. The other seven marker sites
represent the following eight uncovered slots. These rows are complete
registry-row candidates, but all are `PROPOSED`; no token names are invented.

| Proposed ID | Draft site and exact marker | Exact current anchor | Intended supplier / binding | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|---|
| PG-01 | Table 3 prompt point estimate, line `374`, col 2, `[PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated prompt-contrast estimator field | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-02 | Table 3 prompt interval lower endpoint, line `374`, col 3, `[PENDING, PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated fully composed lower endpoint | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-03 | Table 3 prompt interval upper endpoint, line `374`, col 3, `[PENDING, PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated fully composed upper endpoint | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-04 | Table 3 prompt clearance, line `374`, col 5, `[PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future branch-explicit clearance or shortfall derivation | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING; shape contract required | DRAFT, TPL, CV |
| PG-05 | Table 3 prompt claim-side bound, line `374`, col 6, `[PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token and no named claim-side-bound output field | gamma / prompt contrast | STOP_FILL | PROPOSED / SUPPLIER_UNKNOWN | DRAFT, TPL, CV, AUTH |
| PG-06 | Table 3 prompt floor-gate outcome, line `374`, col 7, `[PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future conservative rendering consistent with authenticated magnitude, floor, and verdict | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV |
| PG-07 | Table 3 prompt direction-gate outcome, line `374`, col 8, `[PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future conservative rendering from the fully composed interval and registered direction | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-08 | Table 3 prompt verdict, line `374`, col 9, `[PENDING]` | `\| prompt processing, 7B − 1.5B \|` | No exact prompt rendering token; future authenticated claim-evaluation outcome | gamma / prompt contrast | STOP_FILL | PROPOSED / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |

## Discrepancy disposition

- The current draft registers both contrasts, while the template remains
  decode-only. The old discrepancy text saying the draft arm is unregistered
  is superseded; DS-33 and PG-01–PG-08 state the current one-sided gap.
- D-123 reported means remain `STOP_FILL / SUPPLIER_UNKNOWN`; no prospective
  reported-mean schema or exact member basis has been authorized.
- Decode and prompt gate/verdict renderings remain `STOP_FILL` until exact
  token or renderer contracts exist.
- Characterization outputs remain `STOP_FILL / SUPPLIER_UNKNOWN`. The current
  draft contains protocol-specification rows, not claim-bearing result cells.
- F2 is folded as an era admission precondition; F5 is folded as estimator
  provenance. Neither disposition authorizes a value.

## Change summary versus the current registry

The current registry has no verdict column, so `not recorded` below is literal.

| Row id | Old verdict/binding | New binding | Class of change | Needs lead ruling? |
|---|---|---|---|---|
| DS-01 | not recorded / corrected-artifact operative-floor hold | PROPOSED issued-artifact hold at line `249`; supplier unchanged | marker + locator re-bind | yes |
| DS-02 | not recorded / linearity result marker | PROPOSED workload-response specification anchor; STOP_FILL pending schema | orphan + semantic narrowing | yes |
| DS-03 | not recorded / null result marker | PROPOSED null-response specification anchor; STOP_FILL pending schema | orphan + shape change | yes |
| DS-04 | not recorded / empirical-floor result marker | PROPOSED small-difference specification anchor; STOP_FILL pending schema | orphan + semantic narrowing | yes |
| DS-05 | not recorded / phase-attribution result marker | PROPOSED phase-accounting specification anchor; STOP_FILL pending schema | orphan + shape change | yes |
| DS-06 | not recorded / drift result marker | PROPOSED drift/recovery specification anchor; STOP_FILL pending schema | orphan + shape change | yes |
| DS-07 | not recorded / between-session result marker | PROPOSED between-session specification anchor; STOP_FILL pending schema | orphan + shape change | yes |
| DS-08 | not recorded / corrected-artifact branch hold | PROPOSED expanded issued-artifact hold at line `358`; guarded variant unchanged | marker + locator re-bind | yes |
| DS-09 | not recorded / prompt/1.5B gross | same binding at Table 2 line `364` | locator only | no |
| DS-10 | not recorded / prompt/1.5B companion | same binding at Table 2 line `364` | locator only | no |
| DS-11 | not recorded / prompt/1.5B floor | same binding at Table 2 line `364` | locator only | no |
| DS-12 | not recorded / prompt/1.5B count | same binding at Table 2 line `364` | locator only | no |
| DS-13 | not recorded / prompt/7B gross | same binding at Table 2 line `365` | locator only | no |
| DS-14 | not recorded / prompt/7B companion | same binding at Table 2 line `365` | locator only | no |
| DS-15 | not recorded / prompt/7B floor | same binding at Table 2 line `365` | locator only | no |
| DS-16 | not recorded / prompt/7B count | same binding at Table 2 line `365` | locator only | no |
| DS-17 | not recorded / decode/1.5B gross | same binding at Table 2 line `366` | locator only | no |
| DS-18 | not recorded / decode/1.5B companion | same binding at Table 2 line `366` | locator only | no |
| DS-19 | not recorded / decode/1.5B floor | same binding at Table 2 line `366` | locator only | no |
| DS-20 | not recorded / decode/1.5B count | same binding at Table 2 line `366` | locator only | no |
| DS-21 | not recorded / decode/7B gross | same binding at Table 2 line `367` | locator only | no |
| DS-22 | not recorded / decode/7B companion | same binding at Table 2 line `367` | locator only | no |
| DS-23 | not recorded / decode/7B floor | same binding at Table 2 line `367` | locator only | no |
| DS-24 | not recorded / decode/7B count | same binding at Table 2 line `367` | locator only | no |
| DS-25 | not recorded / decode point estimate | same binding at Table 3 line `373` | locator only | no |
| DS-26 | not recorded / decode interval endpoints | same binding at Table 3 line `373` | locator only | no |
| DS-27 | not recorded / decode claim floor | same binding at Table 3 line `373` | locator only | no |
| DS-28 | not recorded / decode clearance branch | same binding and live shape mismatch at Table 3 line `373` | locator only | no |
| DS-29 | not recorded / decode claim-side bound | same STOP_FILL binding at Table 3 line `373` | locator only | no |
| DS-30 | not recorded / decode floor-gate outcome | same TOKEN_MISSING binding at Table 3 line `373` | locator only | no |
| DS-31 | not recorded / decode direction-gate outcome | same TOKEN_MISSING binding at Table 3 line `373` | locator only | no |
| DS-32 | not recorded / decode verdict | same TOKEN_MISSING binding at Table 3 line `373` | locator only | no |
| DS-33 | not recorded / prompt floor in floors-only row | PROPOSED prompt contrast floor at Table 3 line `374`; STOP_FILL | major semantic shift | yes |
| DS-34 | not recorded / release locators | same binding at Section 9 line `450` | locator only | no |
| PG-01 | absent | PROPOSED prompt point-estimate row; STOP_FILL | new uncovered slot | yes |
| PG-02 | absent | PROPOSED prompt lower-endpoint row; STOP_FILL | new uncovered slot | yes |
| PG-03 | absent | PROPOSED prompt upper-endpoint row; STOP_FILL | new uncovered slot | yes |
| PG-04 | absent | PROPOSED prompt clearance row; STOP_FILL | new uncovered slot | yes |
| PG-05 | absent | PROPOSED prompt claim-side-bound row; STOP_FILL | new uncovered slot | yes |
| PG-06 | absent | PROPOSED prompt floor-gate row; STOP_FILL | new uncovered slot | yes |
| PG-07 | absent | PROPOSED prompt direction-gate row; STOP_FILL | new uncovered slot | yes |
| PG-08 | absent | PROPOSED prompt verdict row; STOP_FILL | new uncovered slot | yes |
