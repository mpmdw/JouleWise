```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "All 68 STOP_FILL table rows map to governed suppliers; four fixture-safe implementation seats are identified, with three schema or vocabulary rulings called out before coding.",
  "workspace": {"base_requested":"9eef8584","base_mode":"exact","head_start":"9eef8584f7fd700f3ff942c16996b2f97350a642","head_end":"9eef8584f7fd700f3ff942c16996b2f97350a642","upstream_end":"9eef8584f7fd700f3ff942c16996b2f97350a642","branch":"feat/2026-09-04-paper-i-scout"},
  "pathspec": ["docs/process_traces/2026-09-04-paper-i/01-supplier-gap-scout.md"],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"id":"GAMMA-CLAIM-RENDERER-01","action":"needs_ruling","reason":"The implementation is fixture-safe, but B_decode_claim_J/PG-05 and the missing prompt token family require a field/token ruling."},
      {"id":"TRANSFER-RESULT-RENDERER-01","action":"wait_for","reason":"Adopt or reject the unreviewed transfer-fiducial v1 schema before creating a consumer on main."},
      {"id":"D165-OUTCOME-RENDERER-01","action":"start_now","reason":"The landed close-out schema completely fixes OB-01 and the close-out half of OR-01."},
      {"id":"D123-REPORTED-MEAN-SUPPLIER-01","action":"needs_ruling","reason":"D-123 fixes intent but not the admitted-member basis, interval composition, denominator provenance, or output schema."},
      {"id":"QUIET-MAC-MEASUREMENTS","action":"do_not_start","reason":"G2-a, Window C, the v5 campaign, and the transfer fiducial are physical measurements forbidden in this scout session."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"rg '^\\|.*STOP_FILL.*\\|$' docs/paper/results-fill-registry.md | wc -l","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["68"]},"expected":{"exit_code":0,"tail_regex":"^ *68$"}},
    {"id":"V2","kind":"inspection","cmd":"jq -r '.tasks | [.\"V5-G2A-PREFILL-PROBE-01\".status,.\"RENDERER-V5-SUCCESSOR-01\".status,.\"D165-E2E-REPLAY-01\".status,.\"TRANSFER-FIDUCIAL-01\".status,.\"MET-WINDOW-C-01\".status] | @tsv' docs/process/state_kernel.json","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["queued\tblocked\tblocked\tblocked\tblocked"]},"expected":{"exit_code":0,"tail_regex":"^queued\\tblocked\\tblocked\\tblocked\\tblocked$"}},
    {"id":"V3","kind":"inspection","cmd":"git diff --check -- docs/process_traces/2026-09-04-paper-i/01-supplier-gap-scout.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"The affected seats need rulings for D-123, gamma claim bounds/tokens, and transfer schema/public prose; lower-priority gaps also need a worst-case-field-or-clause and release-manifest decision.","needs":"Rule before starting affected seats; D165-OUTCOME-RENDERER-01 is independent."},
    {"id":"F2","kind":"residual_risk","level":"nonblocking","text":"RENDERER-V5-SUCCESSOR-01 is kernel-blocked on live G2-a even though supplier modules can be fixture-built with a symbolic prefill length and fail-closed STOP_FILL cases.","needs":"Split fixture-safe suppliers from final 126-key integration, or explicitly retain the conservative wait."},
    {"id":"F3","kind":"verification_gap","level":"nonblocking","text":"No tests were run, as required by the scout preflight; verification is inspection-only.","needs":"Implementation seats own their stated single acceptance test."}
  ]
}
```

# Paper I supplier-gap scout

## Scope and classification

The registry contains **68 table rows whose row text contains `STOP_FILL`**. This is not 68 independent programs: repeated placement rows and conditional fail-closed branches collapse to a small supplier graph. I classify each *stage* of that graph, so a row can legitimately read `A -> C` (the producer is implemented; an issued instance still needs a measurement) or `B -> C` (a fixture-buildable consumer is missing and its eventual input is physical):

- **A** — implemented at this base; the module/CLI and exact field are named below.
- **B** — can be implemented without live values, using valid and conservative/`STOP_FILL` fixtures.
- **C** — only an authenticated physical run can issue the remaining input. This report does not run one.

For the requested status vocabulary, **queued** means a kernel/queue row exists but is not started; parenthetical text retains the kernel's raw `blocked` state. **In progress** means code exists only on an unreviewed concurrent branch. **Landed** means present at `9eef8584`. **Absent** means no owning task or accepted supplier exists in the inspected kernel/queue.

## Exhaustive STOP_FILL mapping

| Registry rows (exact or closed expansion) | Count | Supplier that must issue / exact fields | Class | Owner and status |
|---|---:|---|---|---|
| `V5-G2A-001` | 1 | `scripts/select_g2a_prefill_length.py` -> `joulewise.g2a_prefill_selection.v1.collection_prefill_tokens` | A -> C | Selector **landed**; `V5-G2A-PREFILL-PROBE-01` **queued** (`queued`, quiet_mac). |
| `V5-WL-005` | 1 | `scripts/issue_g2a_prefill_prompt_pin.py` -> `joulewise.prefill_prompt_pin.v2.{prefill_length,prompt_tokens,prompt_text,prompt_token_ids,repeat_count,generation_method,g2a_record_sha256}` | A -> C | Issuer **landed**; issued pin waits on the same queued G2-a probe. |
| Four `TERMINAL_REFUSAL_REASON_{1p7B,8B}_{prefill_p[PREFILL_LENGTH],decode}` rows | 4 | Alpha/beta `joulewise.detection_floor_extraction.v1.cells[].refusal_reasons` plus whole-window verdict `status`, `member_failures`, `idle_admission_core.conditions`; conservative reason renderer | A + B -> C | `joulewise/floor_extraction.py` and `scripts/run_campaign.py` **landed**. The old `scripts/render_results_fills.py` logic is **landed but frozen to 109 old keys**; exact-v5 adapter is **queued** in `RENDERER-V5-SUCCESSOR-01` (raw `blocked`). Live evidence waits for `V5-TRANSACTION-01`. |
| Four `NO_EXACT_FLOOR_REASON_{1p7B,8B}_{prefill_p[PREFILL_LENGTH],decode}` rows | 4 | Same extraction artifact: `cells[].{refusal_reasons,floor,diagnostics}` and exact registered absence normalization | A + B -> C | Extraction and legacy normalization **landed**; exact-v5 successor **queued**; live floor windows **queued**. Unknown reasons remain `STOP_FILL`. |
| D-123 tokens: for each of `1p7B/8B x prefill/decode`, `E_*_J_per_request`, `E_*_lower_J`, `E_*_upper_J`, `E_*_J_per_token`, `N_bundles_*` | 20 | A new authenticated reported-phase-energy artifact must provide per cell: mean/request, fully composed interval endpoints, runtime-observed per-token companion, admitted independent-bundle count, and member/denominator provenance | B -> C | D-123 is ratified, but supplier/task is **absent**. `floor_extraction.CellReport.floor.mean_j` is explicitly not a substitute. Consult required. |
| `B_decode_claim_J`; `DS-29` | 2 | A new claim-verdict field for the separately registered claim-side bound; **not** `contrasts[].deterministic_bounds.total` unless ruled | B -> C | Exact guard `_supplier_unknown("[B_decode_claim_J]")` is **landed** in the frozen renderer; positive supplier and task are **absent**. Consult required. |
| `F_decode_contrast_cmp_two_edge_J` | 1 | Gamma decode aggregate floor cell `floor_cmp_j`, with authenticated estimator registration equal to `d124_two_shared_edge_common_mode.v1` | A -> C | `joulewise/detection_floor.py:build_floor_cell` **landed** (`floor_cmp_j`); live gamma/floor evidence waits on queued v5 transaction. The row conditionally stops on absent/wrong estimator or `common_mode_nonseparable_window_domain`. |
| `F_decode_contrast_cmp_worst_case_J` | 1 | Either a newly ruled same-cell diagnostic worst-case field alongside a two-edge issuance, or deletion of the comparison clause | B -> C | Supplier and owner **absent**. New field semantics require consult. |
| `[VALUE]` | 1 | Renderer-local substitution from the exact authenticated component currently iterated; no standalone artifact field | B | Legacy example-loop behavior exists, but the exact-v5 final-survival check belongs to the **queued** successor. Any survivor is `STOP_FILL`. |
| `DS-02`, `DS-03`, `DS-05`, `DS-06` | 4 | Issued characterization report rows `linearity`, `null`, `phase_attribution`, `drift_settling`, consuming `row_outcome`, `diagnostic_present`, `observed_values`, and `diagnostics` via the frozen `render_map` | A(contract) + B(renderer) -> C | `joulewise.characterization_result_spec.v1` field contract **landed**; report emitter and positive renderer **absent**; `MET-WINDOW-C-01` **queued** (raw `blocked`, quiet_mac). These are specification anchors; results render in guarded variants, not into Table 1. |
| `DS-04`, `DS-07` | 2 | **No issuer by design.** Retired provenance rows; the registry explicitly says they must not render | A | Retirement **landed**. `do_not_start`; they remain in the mechanical STOP_FILL census only. |
| D-123 placements `DS-09`, `DS-10`, `DS-12`, `DS-13`, `DS-14`, `DS-16`, `DS-17`, `DS-18`, `DS-20`, `DS-21`, `DS-22`, `DS-24` | 12 | The same D-123 fields above: each gross cell consumes mean/lower/upper, each companion consumes per-token plus denominator provenance, and each `n` consumes admitted bundle count | B -> C | Same **absent** D-123 supplier; no second implementation is needed. |
| `DS-30`, `DS-31`, `DS-32` | 3 | `joulewise.claim_verdicts.v1.contrasts[]`: `estimator.estimate`, `deterministic_bounds.decision_interval.{lower,upper}`, `floor`, and `claim_evaluation.{outcome,direction,reason_codes,claim_ready_for_l2_l3,claim_level_ceiling}`; missing professor renderer | A + B -> C | `_contrast_row` and claims evaluator **landed**; rendering is **queued** under `RENDERER-V5-SUCCESSOR-01` (raw `blocked`). DS-32 also governs six A/B paragraph slots plus its Table-3 cell. |
| `DS-33`; `PG-01`, `PG-02`, `PG-04`, `PG-06`, `PG-07`, `PG-08` | 8 | Same claim-verdict fields for `ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b`, plus armwise prefill `floor_gate_j`; missing prompt token family/renderer | A + B -> C | Analysis producer **landed**; token family **absent**; successor task **queued** and kernel-blocked on G2-a. PG-08 governs six A/B paragraph slots plus its Table-3 cell. Consult token names before code. |
| `PG-05` | 1 | Prefill counterpart of the new claim-side-bound field required by `B_decode_claim_J` | B -> C | Supplier/task **absent**; resolve in the same claim-bound ruling. |
| `DS-34` | 1 | New release manifest fields for repository commit, archive locator, and published digest-manifest locator | B | Release checklist exists, but a machine supplier and owning kernel task are **absent**. Issuance later waits on release, not a physical measurement. |
| `OB-01` | 1 | `joulewise.d165_dominance_closeout.v1.independent_ratios[].{cell_id,component,passes}` and `.comparative_common_mode_ratios[].{cell_id,component,passes}` | A + B -> C | `joulewise/dominance_closeout.py` and `scripts/build_d165_dominance_closeout.py` **landed** (core PR #261; sidecar PR #267). Public list renderer is **queued** under successor; `D165-E2E-REPLAY-01` queued (raw `blocked`). Three Outcome-B slots. |
| `TR-01` | 1 | Accepted `TRANSFER-FIDUCIAL-01` capture: `residual_transfer_s`, pulse bound, `verdict`, `reasons`, estimator revision, and diagnostic/non-claim labels; public result renderer | B -> C | Base task **queued** (raw `blocked`, quiet_mac). An **in-progress, unreviewed** sibling branch proposes `joulewise.transfer_fiducial_capture.v1.{b_pulse_s,residual_transfer_s,verdict,reasons,estimator_revision}` and `scripts/fit_transfer_fiducial.py`; it is not a landed supplier and is not a descendant of this base. Nine A/B/Refusal slots. |
| `OR-01` | 1 | Before-comparison: authenticated whole-window admission or missing gamma verdict reason. At-close-out: `joulewise.d165_dominance_closeout.v1.{branch,refusal_reason}`. One precedence-aware public renderer | A + B -> C | Inputs partly **landed**; renderer **queued** under successor. Four literal markers, of which three are Refusal outcome slots and one is the Section-4 form. |

**Coverage check:** 2 + 8 + 20 + 2 + 1 + 1 + 1 + 6 + 12 + 3 + 8 + 1 + 1 + 1 + 1 + 1 = **68**. The grouped rows above are closed expansions; none is omitted.

### Existing producer detail (category A)

- Floor: `joulewise/detection_floor.py:build_floor_cell` emits `floor_abs_j`, `floor_cmp_j`, `floor_gate_j`, `eligibility`, and `point_floor_diagnostics`; `floor_gate_j` is the component maximum, not a sum.
- Extraction/verdict: `joulewise/floor_extraction.py:CellReport.as_row` emits `refusal_reasons`, `floor`, admitted counts, and diagnostics; `scripts/run_campaign.py` emits the whole-window `status`, failures, admission conditions, and evaluation basis.
- Gamma: `joulewise/analysis_engine/__init__.py:_contrast_row` emits `estimator.estimate`, `deterministic_bounds.decision_interval`, `floor`, and `claim_evaluation`. `deterministic_bounds.total` is deliberately not registered as `B_*_claim_J`.
- D-165: `scripts/build_d165_dominance_closeout.py` emits the 8 independent and 4 comparative-common-mode records plus `all_independent_pass`, `all_required_common_mode_pass`, `branch`, `dominance_sentence_licensed`, `subtitle_licensed`, and `refusal_reason`.
- The existing `scripts/render_results_fills.py` is useful precedent for fail-closed reason normalization, branch selection, and pseudotoken elimination, but it consumes `joulewise.results_fill_input.v1` with old 1.5B/7B prompt names and is frozen. It is not the exact `_v5` supplier.

## Category-B implementation seat briefs

Order is by **outcome-branch slots** in Abstract / Discussion (Section 7) / Conclusion: DS-32 and PG-08 each occupy A and B in all three sections (12 total); TR-01 occupies A/B/Refusal in all three (9); OB-01 occupies B in all three and OR-01 occupies Refusal in all three (6); D-123 occupies none (0). Table cells and the Section-4 OR marker are not counted in this ordering.

### 1. GAMMA-CLAIM-RENDERER-01 — 12 outcome slots

- **Rows closed:** `DS-30`, `DS-31`, `DS-32`, `DS-33`, `PG-01`, `PG-02` (both semantic endpoints), `PG-04`, `PG-05`, `PG-06`, `PG-07`, `PG-08`, plus underlying `B_decode_claim_J`/`DS-29` when the bound ruling supplies both phase fields.
- **Producer schema/fields:** `joulewise.claim_verdicts.v1.contrasts[]` selected by exact `contrast_id`, consuming `estimator.estimate`, `deterministic_bounds.decision_interval.{lower,upper}`, `floor`, and `claim_evaluation.{outcome,direction,reason_codes,claim_ready_for_l2_l3,claim_level_ceiling}`; alpha/beta `floor_gate_j`; proposed ruled `claim_side_bound_j` for decode and prefill.
- **Registered professor rendering:** signed B-minus-A estimate; fully composed endpoints; armwise maximum floor (never sum); branch-explicit clearance/shortfall; floor pass only from authenticated magnitude/floor and consistent verdict; direction pass only from the full interval and registered direction. Repeat one DS-32/PG-08 phrase across all placements, never derive it from D-165. REFUSAL Table-3 strings are exactly `not evaluated — required <phase> verdict absent` or `not evaluated — stopped before comparison: <issued reason>` as applicable.
- **Fixture:** two synthetic claim-verdict contrasts and four floor cells, parameterized with `collection_prefill_tokens=2048`; include supported, floor-refused, direction-refused, absent-bound, missing-verdict, and malformed-ID cases. Numeric values remain fixture-only and render conservative STOP_FILL where parents are absent.
- **One acceptance test:** a table-driven test proves byte-exact outputs for every listed row in supported/floor-refused/direction-refused cases and `STOP_FILL` for every absent, inconsistent, duplicate, or unauthenticated parent; no `[PENDING]`, `[FILL:*]`, or `[VALUE]` survives.
- **WRITE_SCOPE:** `joulewise/results_fill_gamma.py`, `tests/test_results_fill_gamma.py`, `tests/fixtures/results_fill_gamma/**`.
- **Consult before coding:** rule the exact claim-side-bound field/semantics (it cannot be silently aliased to `deterministic_bounds.total`) and the exact prompt token names/public outcome phrase set. Then split this fixture module from the kernel's live G2-a integration gate.

### 2. TRANSFER-RESULT-RENDERER-01 — 9 outcome slots

- **Rows closed:** `TR-01` only; its one value repeats in all nine A/B/Refusal placements.
- **Producer schema/fields:** candidate sibling-branch `joulewise.transfer_fiducial_capture.v1.{diagnostic,claim_bearing,b_pulse_s,residual_transfer_s,excess_s,verdict,reasons,estimator_revision,estimator_source_sha256}`; `verdict` is `supported`, `exceeds_bound`, or `inconclusive`.
- **Registered professor rendering:** say whether the largest fitted inserted-gap edge residual supports applying the session pulse-derived bound to inference; disclose both magnitudes; call it diagnostic and non-claim-bearing; do not let branch selection remove it or let it mint a floor/claim.
- **Fixture:** the branch's protocol-arithmetic worked example (`0.022 s <= 0.030067931757111657 s`, explicitly non-measurement) plus conservative exceeds-bound and inconclusive records.
- **One acceptance test:** each accepted fixture produces one byte-identical sentence copied to all nine slots, while absent/invalid identity, unrecognized verdict/reason, `claim_bearing=true`, or digest mismatch produces `STOP_FILL` everywhere.
- **WRITE_SCOPE:** `joulewise/results_fill_transfer.py`, `tests/test_results_fill_transfer.py`, `tests/fixtures/results_fill_transfer/**`.
- **Consult before coding:** the lead must first adjudicate/adopt the divergent unreviewed transfer schema and register exact public wording; otherwise this seat would hard-code an unaccepted contract.

### 3. D165-OUTCOME-RENDERER-01 — 6 outcome slots

- **Rows closed:** `OB-01`, `OR-01` (including its Section-4 form; six is the outcome-slot count only), and `[VALUE]` survival for this consumer.
- **Producer schema/fields:** landed `joulewise.d165_dominance_closeout.v1`: `independent_ratios[].{cell_id,component,passes}`, `comparative_common_mode_ratios[].{cell_id,component,passes,refusal_reason}`, `all_independent_pass`, `all_required_common_mode_pass`, `branch`, `dominance_sentence_licensed`, `subtitle_licensed`, `refusal_reason`; OR also consumes landed whole-window/claim-evaluation reasons for before-comparison stops.
- **Registered professor rendering:** OB lists every false record in artifact order with cell and component, never omitting a failure. OR emits exactly one stage label (`before comparison` or `at close-out`) plus the issued reason; names affected model/verdict; includes a Qwen-pair verdict only when its absence caused the stop; refuses conflicting/multi-stage input without ruled precedence.
- **Fixture:** existing D-165 A/B/refusal builder fixtures, augmented only in this seat's fixture directory with before-comparison whole-window and absent-verdict manifests.
- **One acceptance test:** A, B, before-comparison refusal, and close-out refusal fixtures produce exact OB/OR strings; incomplete 8+4 census, unauthenticated source, conflicting stages, or missing precedence always returns `STOP_FILL` and never infers a reason.
- **WRITE_SCOPE:** `joulewise/results_fill_outcome.py`, `tests/test_results_fill_outcome.py`, `tests/fixtures/results_fill_outcome/**`.
- **Start condition:** start now. It has no G2-a data dependency; final live insertion still waits for authenticated close-out and final G3. The future integrator, not this supplier module, owns the frozen 126-key orchestration surface.

### 4. D123-REPORTED-MEAN-SUPPLIER-01 — 0 outcome slots

- **Rows closed:** all 20 D-123 exact tokens and their 12 placements: `DS-09`, `DS-10`, `DS-12`, `DS-13`, `DS-14`, `DS-16`, `DS-17`, `DS-18`, `DS-20`, `DS-21`, `DS-22`, `DS-24`.
- **Producer schema/fields (proposal, not authority):** `joulewise.reported_phase_energy.v1.cells[]` with `cell_id`, `member_basis`, `bundle_ids`, `mean_j_per_request`, `interval.{lower_j,upper_j,composition_rule}`, `per_token.{value_j,denominator_kind,observed_token_count}`, and `n_admitted_bundles`, plus source digests. This proposal exists only to make the ruling concrete.
- **Registered professor rendering:** gross J/request with fully composed lower-upper interval; optional tokenizer-scoped J/token only with runtime-observed denominator provenance; exact admitted independent-bundle `n`; absent measurement is not zero; never substitute a floor component count/internal `mean_j`; same 50 members and no changed floor bytes under D-123.
- **Fixture:** synthetic 50-member alpha/beta prefill/decode bundle summaries with runtime-observed prompt/output token counts, plus a copy of the preexisting floor-output fixture used for byte-identity comparison.
- **One acceptance test:** the supplier emits all four cells and 20 values deterministically while a before/after digest assertion proves every existing detection-floor artifact byte unchanged; member-basis or denominator ambiguity refuses the entire reported-mean artifact.
- **WRITE_SCOPE:** `joulewise/reported_phase_energy.py`, `scripts/build_reported_phase_energy.py`, `tests/test_reported_phase_energy.py`, `tests/fixtures/reported_phase_energy/**`.
- **Consult before coding:** rule admitted-member basis, interval composition, runtime denominator policy, schema name/closed keys, authentication/digest parents, and whether failure is whole-artifact or per-cell. Install a kernel/queue mission; D-123 presently has none.

## Other category-B work not selected in the four-seat cap

The four-seat cap leaves three zero-outcome-slot suppliers behind: (1) characterization report emitter plus guarded result renderer for live `DS-02/03/05/06` (first ratify the specification's two proposed applied-limit derivations); (2) release-manifest writer for `DS-34` (rule schema/fields); and (3) the worst-case diagnostic field or clause deletion for `F_decode_contrast_cmp_worst_case_J` (rule which). Retired `DS-04/07` must never receive a seat.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| D165-OUTCOME-RENDERER-01 | start_now | none for fixture module; live insert waits final G3/close-out | Coordinate the future import seam with `RENDERER-V5-SUCCESSOR-01`; do not edit frozen `scripts/render_results_fills.py`. |
| GAMMA-CLAIM-RENDERER-01 | needs_ruling | claim-side-bound field and prompt token/phrase ruling; kernel split from G2-a | Same future successor integrator and registry vocabulary. Use a standalone supplier module to avoid file collision. |
| TRANSFER-RESULT-RENDERER-01 | wait_for | magistrate disposition/adoption of `feat/2026-09-04-transfer-fiducial-v5`; exact public phrase | The sibling branch is unreviewed and diverged before `9eef8584`; do not duplicate or cherry-pick its broad delta blindly. |
| D123-REPORTED-MEAN-SUPPLIER-01 | needs_ruling | D-123 schema/member/interval/denominator ruling and a new queue row | Touches the same alpha/beta source artifacts as floor extraction; acceptance must pin floor bytes unchanged. |
| Physical issuances | do_not_start | G2-a; Window C; v5 transaction/final G3; then transfer fiducial | `[QUIET-MAC]`, Ed/lead-controlled, and outside this scout. |

## Critical path

`V5-G2A-PREFILL-PROBE-01 -> V5-DESK-DAY-01 -> V5-TRANSACTION-01 -> V5-NIGHTLY-G3-01 -> TRANSFER-FIDUCIAL-01` is the physical chain. It controls live values, not fixture implementation. Separately, `D165-OUTCOME-RENDERER-01 -> RENDERER-V5-SUCCESSOR-01 integration -> D165-E2E-REPLAY-01` closes the fixture-to-paper proof. Gamma and D-123 contract rulings precede their seats; their outputs then join the successor integration. Transfer schema adoption precedes its renderer, while the physical transfer capture still waits for final G3.

## Delegation contracts

The four numbered briefs above are non-overlapping producer-module contracts. Each has an exact future write scope, one fixture family, and one acceptance test. None authorizes live measurement, paper filling, edits to the frozen 109-key renderer, or integration into the 126-key successor. The lead retains schema rulings, kernel scheduling changes, branch adjudication, final diff review, live issuance, and paper insertion.
