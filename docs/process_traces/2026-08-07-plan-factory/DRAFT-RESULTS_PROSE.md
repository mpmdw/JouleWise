# Results prose fillable template

This document contains one copy of each bench-ready drop-in. Select one §7
variant and one §6 variant after the governing window verdicts and funding
decision are known. Do not combine outcome branches or turn a conditional
sentence into an unconditional assertion.

## Fill key

### Source values

- Every bracketed item is a named fill token. Repeated source tokens bind the
  same source value everywhere.
- `_J` means joules, `_J_per_request` means joules per request,
  `_J_per_token` means joules per runtime-observed token, `_s` means seconds,
  and `_x_floor` is dimensionless.
- `N_bundles_*` counts independent valid run bundles, never samples or items
  within a bundle.
- `F_*_abs_J` is copied from the authenticated cell's `floor_abs_j`; it is the
  absolute component's final guarded, corner-widened value after its own
  matching drift allowance.
- `F_*_cmp_J` is copied from the authenticated cell's `floor_cmp_j`; it is the
  comparative component's final guarded, corner-widened value after its own
  matching drift allowance.
- Verify for each component:
  `final component = corner_widened_guarded_floor_j + that component's
  whole_window_drift_allowance_j`. An allowance is never added again at the
  cell or claim level.

### Mechanical derivations

- Derived values are not independently fillable. The fill process computes
  them from authenticated parents and refuses any supplied replacement.
- `DERIVE F_*_operative_J :=
  max(F_*_abs_J, F_*_cmp_J)`.
  It is defined only when both exact component values exist.
- Remove every independent `F_*_corner_J` token. If compatibility requires a
  transient alias, derive
  `F_*_corner_J := F_*_operative_J`; never fill it separately.
- Remove every singular `F_*_point_J` token. Point diagnostics are
  component-specific and are rendered from the authenticated
  `point_floor_diagnostics` map. For each available component, generate:
  “The [absolute/comparative] point-only repeatability diagnostic was
  [VALUE] J; it is retained as a diagnostic and cannot support a claim.”
- `DERIVE F_claim_decode_armwise_max_J :=
  max(F_1p5B_decode_operative_J, F_7B_decode_operative_J)`.
  This claim-level floor gate is defined only when both selected
  token-generation operative floors are exact and claim-bearing.
- `DERIVE M_decode_contrast_abs_J_per_request :=
  abs(E_decode_contrast_signed_J_per_request)`.
- `DERIVE C_decode_floor_clearance_J :=
  M_decode_contrast_abs_J_per_request -
  F_claim_decode_armwise_max_J`; use only after floor-gate passage.
- `DERIVE S_decode_floor_shortfall_J :=
  F_claim_decode_armwise_max_J -
  M_decode_contrast_abs_J_per_request`; use only for floor-gate refusal.
- `DERIVE R_decode_effect_x_floor :=
  M_decode_contrast_abs_J_per_request /
  F_claim_decode_armwise_max_J`.
- `DERIVE S_decode_joint_J :=
  F_claim_decode_armwise_max_J + B_decode_claim_J`.
  This remains a sizing disclosure, never an acceptance gate.

### Cell-state inputs

Compute `E_CELL`, `X_CELL`, and `A_CELL` from authenticated component reports
with this closed selector. Do not infer them from the availability of a prose
fill.

```text
TERMINAL_REASON_CODES = {
  bundle_missing,
  summary_unreadable,
  bundle_strict_invalid,
  bundle_hash_unresolved,
  bundle_status_not_succeeded,
  reducer_wire_unknown,
  idle_method_pair_invalid,
  metric_missing_or_nonfinite,
  window_evidence_precheck_failed,
  campaign_cooldown_evidence_missing,
  cooldown_cap_hit_unverified,
  campaign_member_omitted_from_spec,
  campaign_member_unattributable,
  cap_hit_drift_term_unavailable,
  insufficient_members_after_exclusion,
  anchor_energy_envelope_unrecorded,
  anchor_energy_envelope_exceeds_quarter_metric,
  anchor_fallback_member_unusable,
  clock_anchor_unresolved,
  environment_admission_missing,
  cpu_admission_unenforced,
  whole_window_neg8_verdict_missing,
  whole_window_neg8_verdict_failed,
  adapter_continuity_evidence_missing,
  adapter_continuity_failed,
  cpu_admission_core_missing,
  cpu_admission_core_failed,
  whole_window_verdict_coverage_incomplete,
  whole_window_verdict_provenance_invalid,
  whole_window_verdict_conflict,
  calibration_bracket_exceeds_minted_bound,
  whole_window_drift_allowance_unrecorded,
  mock_telemetry_claim_ineligible,
  attribution_dominance_unlicensed
}
```

`admissible_set_uncertainty_dominates_point_floor` is deliberately absent from
that set because its disposition depends on exact-floor and licence fields.

```text
NONTERMINAL_EXACT_FLOOR_UNAVAILABLE_CODES = {
  exact_corner_widened_absolute_floor_unavailable,
  exact_corner_widened_comparative_floor_unavailable
}
```

These are selector-normalized states, not new scientific refusal meanings.
Generate one only when the corresponding component has:

- raw reasons exactly `{admissible_set_uncertainty_dominates_point_floor}`;
- no terminal reason;
- no exact corner-widened floor; and
- otherwise valid authenticated extraction metadata.

A generically absent component, missing evidence, null `floor_gate_j`, or
unmatched reason does not enter N automatically.

```text
1. Validate both component records and all reason codes.
   Unknown code, malformed metadata, or stored/recomputed mismatch => STOP_FILL.

2. terminal :=
     all authoritative reasons in TERMINAL_REASON_CODES.
   Do not select a branch yet.

3. Before selecting any branch, classify both components independently as
   terminal, exact-unavailable, or exact. A component is exact-unavailable
   only when it carries one of the two permitted normalized nonterminal codes
   above. A generically absent, null, or unmatched component in either
   position => STOP_FILL. Do not infer N from nullness.

4. If terminal is nonempty => E=false; select T.

5. If terminal is empty and at least one component is exact-unavailable, then
   every absent or inexact component must be exact-unavailable under step 3.
   Set E=true and X=false; select N.

6. On the two-exact-component path, set E=true. X=true iff:
     both final component floors are finite and authenticated,
     stored operative floor is finite,
     stored operative floor == max(abs, cmp), and
     all non-exact eligibility requirements pass.
   Otherwise => STOP_FILL.

7. Compute DOMINANCE_STATE:

   LICENSED iff at least one component:
     has the dominance code as its sole otherwise-refusing condition,
     has an exact widened floor,
     has matching attribution-limit class and floor source,
     has its authenticated point diagnostic, and
     no component has a terminal reason.

   ABSENT iff:
     neither component has the dominance code,
     neither component carries attribution-limit metadata, and
     no terminal reason exists.

   UNLICENSED otherwise.

8. If DOMINANCE_STATE=UNLICENSED, add
   attribution_dominance_unlicensed, set E=false, and select T.

9. A=true iff DOMINANCE_STATE=LICENSED.

10. With E=true and X=true:
     A=true  => select L.
     A=false and DOMINANCE_STATE=ABSENT => select U.

11. Every other state => STOP_FILL.
```

This makes dominance absent distinct from dominance present but unlicensed. U
is reachable only from `ABSENT`, never from a generic `A=false`.
- Terminal refusal reasons come from the authoritative refusal log. The
  attribution-dominance condition is excluded from this terminal set only
  when the authenticated labelled-floor licence applies.
- `[TERMINAL_REFUSAL_REASON_*]` receives the verbatim refusal or a conservative
  plain-language rendering.
- `[NO_EXACT_FLOOR_REASON_*]` explains why an otherwise eligible cell lacks
  both exact components or an exact operative floor. It never receives a
  number.
- Missing, stale, contaminated, inconsistent, or otherwise terminal evidence
  always selects Branch T, even if a point diagnostic or one component exists.

### N-branch available-diagnostic renderer

Inspect authenticated values in this fixed order:

1. absolute final component;
2. comparative final component;
3. absolute point-only repeatability diagnostic;
4. comparative point-only repeatability diagnostic.

For each present final component, emit:

“The available [absolute/comparative] component was [VALUE] J. Because no
operative cell floor exists, that component is diagnostic only and cannot
support a claim.”

For each present point diagnostic, emit:

“The [absolute/comparative] point-only repeatability diagnostic was [VALUE] J;
it is retained as a diagnostic and cannot support a claim.”

If none of the four values exists, emit exactly:

“No authenticated numeric component or point-only repeatability diagnostic is
available for this cell.”

Never emit an empty token, an empty sentence, “not available” beside a numeric
placeholder, or a zero substituted for absence.

The master §6 selection predicates are:

```text
Variant 0 =
  NOT(funded AND run AND an issued whole-window verdict exists)

Variant A =
  funded
  AND run
  AND whole-window verdict = PASS
  AND every one of the six registered row outcomes = SUPPORTED

Variant B =
  funded
  AND run
  AND whole-window verdict = PASS
  AND at least one of the six registered row outcomes != SUPPORTED

Variant C =
  funded
  AND run
  AND whole-window verdict = REFUSED
```

The six rows include between-session stability. Therefore Variant A is
unavailable until at least three eligible sessions or days support that row. A
pending between-session row selects B, not A. Validate first that a completed
run has an issued verdict before treating it as a result.

### Plain-language outcome fills

- Machine enum values may be used internally by the selector but must not
  appear as professor-facing fills.
- Each `[PLAIN_LANGUAGE_RESULT_*]` receives one complete predicate phrase:
  “supported the registered behavior”; “did not support a conclusion under
  the registered criterion”; “showed that the registered expected behavior
  did not hold”; or, for between-session stability only, “remains pending
  because fewer than three eligible sessions are available.”
- `tokenizer_identity_match` is the same-tokenizer selector atom. Its fill rule
  states the licence and prohibition, not an observed fact: when both arms
  record the same tokenizer identity, that match makes the per-token companion
  comparable between those arms. No per-token number may be compared with a
  stack carrying a different tokenizer identity.

### §7 variant predicates

- `decode_*_published` means that cell selected L or U.
- `decode_*_nonpublication` means that cell selected T or N.
- For each decode cell, exactly one of `published` and `nonpublication` is
  true.
- `claim_floor_defined` is true only after
  `F_claim_decode_armwise_max_J` has been derived and verified from two
  published decode operative floors.
- A missing required contrast, interval, or claim-bound source stops selection;
  it never defaults to zero or selects another outcome.
- `[CELL_NONPUBLICATION_SUMMARY]` is mechanically generated in 1.5B-then-7B
  order from selected T/N branches. It contains each affected cell name and its
  already-rendered terminal or no-exact-floor reason.

## §7 Variant A — both floor windows pass; decode contrast clears both gates

<!-- VARIANT_PREDICATE 7_A:
window_1p5B_pass AND window_7B_pass
AND decode_1p5B_published AND decode_7B_published
AND claim_floor_defined
AND contrast_signed_present
AND contrast_interval_present
AND claim_bound_present
AND tokenizer_identity_match
AND floor_gate_pass AND direction_gate_pass
-->

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, the authenticated
signed contrast, contrast interval, and claim-side bound are present, and both
arms record the same tokenizer identity, and both the floor and direction gates
passed. If the predicate is false, do not use any sentence from this variant.

**Lead-in replacement.** The demonstration asked how phase-resolved energy per
request differed between the two named model sizes on one recorded consumer
stack and whether the registered token-generation contrast passed its separate
floor and direction gates. Both model-specific floor windows passed their
whole-window verdicts, and the registered contrast passed both gates.

Both floor windows produced their prospectively registered phase cells. For
each cell, select exactly one of the following four branches only after the
authenticated evidence establishes the selector facts.

<!-- CELL_BRANCH_SET: A_1p5B_prompt; SELECT EXACTLY ONE BRANCH -->

- **1.5B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: A_1p5B_prompt -->

<!-- CELL_BRANCH_SET: A_1p5B_decode; SELECT EXACTLY ONE BRANCH -->

- **1.5B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: A_1p5B_decode -->

<!-- CELL_BRANCH_SET: A_7B_prompt; SELECT EXACTLY ONE BRANCH -->

- **7B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: A_7B_prompt -->

<!-- CELL_BRANCH_SET: A_7B_decode; SELECT EXACTLY ONE BRANCH -->

- **7B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: A_7B_decode -->

<!-- MEASUREMENT_RENDER: 1p5B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_1p5B_prompt_J_per_request] J per request, with a fully composed interval of
[E_1p5B_prompt_lower_J]–[E_1p5B_prompt_upper_J] J across
[N_bundles_1p5B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_prompt -->

<!-- MEASUREMENT_RENDER: 7B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_7B_prompt_J_per_request] J per request, with a fully composed interval of
[E_7B_prompt_lower_J]–[E_7B_prompt_upper_J] J across
[N_bundles_7B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_prompt -->

<!-- MEASUREMENT_RENDER: 1p5B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_1p5B_decode_J_per_request] J per request, with a fully composed interval of
[E_1p5B_decode_lower_J]–[E_1p5B_decode_upper_J] J across
[N_bundles_1p5B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_decode -->

<!-- MEASUREMENT_RENDER: 7B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_7B_decode_J_per_request] J per request, with a fully composed interval of
[E_7B_decode_lower_J]–[E_7B_decode_upper_J] J across
[N_bundles_7B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_decode -->

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.

The pre-registered token-generation contrast estimated 7B minus 1.5B energy at
[E_decode_contrast_signed_J_per_request] J per request, with a fully composed
interval of [E_decode_contrast_lower_J]–[E_decode_contrast_upper_J] J. Its
claim-level floor gate was [F_claim_decode_armwise_max_J] J, the armwise maximum
of the two selected token-generation operative floors. The arm floors were not
added. The point-estimate magnitude cleared the claim-level floor gate by
[C_decode_floor_clearance_J] J, an effect-to-floor ratio of
[R_decode_effect_x_floor]. The floor gate passed. Both interval endpoints also
supported the registered direction, so the direction gate passed.

The result supports the narrow claim that, for the recorded physical unit,
software stack, tokenizer-scoped workload, output policy, and *powermetrics*
system-on-chip boundary, the 7B condition used more token-generation energy per
request than the 1.5B condition.

The claim-side measurement bound was [B_decode_claim_J] J. The practical sizing
quantity was [S_decode_joint_J] J, disclosed as the
[F_claim_decode_armwise_max_J] J claim-level floor gate plus the
[B_decode_claim_J] J claim-side bound. It is not a single summed acceptance
threshold, and the decision interval was not compared with the sum.

## §7 Variant B1 — floor-gate refusal

<!-- VARIANT_PREDICATE 7_B1:
window_1p5B_pass AND window_7B_pass
AND decode_1p5B_published AND decode_7B_published
AND claim_floor_defined
AND contrast_magnitude_present
AND claim_bound_present
AND tokenizer_identity_match
AND floor_gate_refused
-->

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, the authenticated
contrast magnitude and claim-side bound are present, both arms record the same
tokenizer identity, and the floor gate was refused. If the predicate is false,
do not use any sentence from this variant.

**Lead-in replacement.** The demonstration asked whether the magnitude of the
registered token-generation contrast was resolvable on the named consumer stack
before any directional conclusion was considered. Both model-specific floor
windows passed their whole-window verdicts, but the contrast did not pass the
floor gate.

Both floor windows produced their prospectively registered phase cells. For
each cell, select exactly one of the following four branches only after the
authenticated evidence establishes the selector facts.

<!-- CELL_BRANCH_SET: B1_1p5B_prompt; SELECT EXACTLY ONE BRANCH -->

- **1.5B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B1_1p5B_prompt -->

<!-- CELL_BRANCH_SET: B1_1p5B_decode; SELECT EXACTLY ONE BRANCH -->

- **1.5B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B1_1p5B_decode -->

<!-- CELL_BRANCH_SET: B1_7B_prompt; SELECT EXACTLY ONE BRANCH -->

- **7B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B1_7B_prompt -->

<!-- CELL_BRANCH_SET: B1_7B_decode; SELECT EXACTLY ONE BRANCH -->

- **7B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B1_7B_decode -->

<!-- MEASUREMENT_RENDER: 1p5B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_1p5B_prompt_J_per_request] J per request, with a fully composed interval of
[E_1p5B_prompt_lower_J]–[E_1p5B_prompt_upper_J] J across
[N_bundles_1p5B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_prompt -->

<!-- MEASUREMENT_RENDER: 7B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_7B_prompt_J_per_request] J per request, with a fully composed interval of
[E_7B_prompt_lower_J]–[E_7B_prompt_upper_J] J across
[N_bundles_7B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_prompt -->

<!-- MEASUREMENT_RENDER: 1p5B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_1p5B_decode_J_per_request] J per request, with a fully composed interval of
[E_1p5B_decode_lower_J]–[E_1p5B_decode_upper_J] J across
[N_bundles_1p5B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_decode -->

<!-- MEASUREMENT_RENDER: 7B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_7B_decode_J_per_request] J per request, with a fully composed interval of
[E_7B_decode_lower_J]–[E_7B_decode_upper_J] J across
[N_bundles_7B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_decode -->

Any arm-level intervals reported above are intervals for the individual arms,
not a signed cross-model estimate or a directional contrast interval.

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.

The magnitude of the registered token-generation contrast was
[M_decode_contrast_abs_J_per_request] J per request against the
[F_claim_decode_armwise_max_J] J claim-level floor gate, leaving a shortfall of
[S_decode_floor_shortfall_J] J and an effect-to-floor ratio of
[R_decode_effect_x_floor]. The claim-level floor gate is the armwise maximum of
the two selected token-generation operative floors; the arm floors were not
added. The result is *not resolvable at the stated floor under the recorded
conditions*. It is not evidence of equality or no difference. Because the floor
gate refused the magnitude, the direction gate was not reached.

The claim-side measurement bound was [B_decode_claim_J] J. The practical sizing
quantity was [S_decode_joint_J] J, disclosed as the
[F_claim_decode_armwise_max_J] J claim-level floor gate plus the
[B_decode_claim_J] J claim-side bound. It is not a single summed acceptance
threshold, and the decision interval was not compared with the sum. The refusal
is reported without adding blocks, changing the workload, or promoting a
point-only diagnostic.

## §7 Variant B2 — direction-gate refusal

<!-- VARIANT_PREDICATE 7_B2:
window_1p5B_pass AND window_7B_pass
AND decode_1p5B_published AND decode_7B_published
AND claim_floor_defined
AND contrast_signed_present
AND contrast_interval_present
AND claim_bound_present
AND tokenizer_identity_match
AND floor_gate_pass AND direction_gate_refused
-->

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, the authenticated
signed contrast, contrast interval, and claim-side bound are present, the floor
gate passed, both arms record the same tokenizer identity, and the direction
gate was refused. If the predicate is false, do not use any sentence from this
variant.

**Lead-in replacement.** The demonstration asked whether the registered
token-generation contrast passed its separate magnitude and direction gates on
the named consumer stack. Both model-specific floor windows passed their
whole-window verdicts, and the contrast passed the floor gate but did not pass
the direction gate.

Both floor windows produced their prospectively registered phase cells. For
each cell, select exactly one of the following four branches only after the
authenticated evidence establishes the selector facts.

<!-- CELL_BRANCH_SET: B2_1p5B_prompt; SELECT EXACTLY ONE BRANCH -->

- **1.5B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B2_1p5B_prompt -->

<!-- CELL_BRANCH_SET: B2_1p5B_decode; SELECT EXACTLY ONE BRANCH -->

- **1.5B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B2_1p5B_decode -->

<!-- CELL_BRANCH_SET: B2_7B_prompt; SELECT EXACTLY ONE BRANCH -->

- **7B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B2_7B_prompt -->

<!-- CELL_BRANCH_SET: B2_7B_decode; SELECT EXACTLY ONE BRANCH -->

- **7B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: B2_7B_decode -->

<!-- MEASUREMENT_RENDER: 1p5B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_1p5B_prompt_J_per_request] J per request, with a fully composed interval of
[E_1p5B_prompt_lower_J]–[E_1p5B_prompt_upper_J] J across
[N_bundles_1p5B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_prompt -->

<!-- MEASUREMENT_RENDER: 7B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_7B_prompt_J_per_request] J per request, with a fully composed interval of
[E_7B_prompt_lower_J]–[E_7B_prompt_upper_J] J across
[N_bundles_7B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_prompt -->

<!-- MEASUREMENT_RENDER: 1p5B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_1p5B_decode_J_per_request] J per request, with a fully composed interval of
[E_1p5B_decode_lower_J]–[E_1p5B_decode_upper_J] J across
[N_bundles_1p5B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_decode -->

<!-- MEASUREMENT_RENDER: 7B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_7B_decode_J_per_request] J per request, with a fully composed interval of
[E_7B_decode_lower_J]–[E_7B_decode_upper_J] J across
[N_bundles_7B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_decode -->

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.

The pre-registered token-generation contrast estimated 7B minus 1.5B energy at
[E_decode_contrast_signed_J_per_request] J per request. Its point-estimate
magnitude cleared the [F_claim_decode_armwise_max_J] J claim-level floor gate
by [C_decode_floor_clearance_J] J, an effect-to-floor ratio of
[R_decode_effect_x_floor], so the floor gate passed. The claim-level floor gate
was the armwise maximum of the two selected token-generation operative floors;
the arm floors were not added.

The fully composed interval was [E_decode_contrast_lower_J]–
[E_decode_contrast_upper_J] J, and its endpoints did not both support the
registered direction. The direction gate therefore refused the contrast. The
result is *unresolved*, with no directional claim; a point estimate above the
floor does not repair an interval that fails the direction gate.

The claim-side measurement bound was [B_decode_claim_J] J. The practical sizing
quantity was [S_decode_joint_J] J, disclosed as the
[F_claim_decode_armwise_max_J] J claim-level floor gate plus the
[B_decode_claim_J] J claim-side bound. It is not a single summed acceptance
threshold, and the decision interval was not compared with the sum. The refusal
is reported without adding blocks, changing the workload, or promoting a
point-only diagnostic.

## §7 Variant D — a token-generation cell publishes no floor

<!-- VARIANT_PREDICATE 7_D:
window_1p5B_pass AND window_7B_pass
AND (decode_1p5B_nonpublication OR decode_7B_nonpublication)
-->

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific windows passed their whole-window verdicts and at least one
token-generation cell selected T or N. If the predicate is false, do not use
any sentence from this variant.

**Lead-in replacement.** Both model-specific windows completed with passing
whole-window verdicts, but at least one token-generation cell did not publish
an operative floor.

<!-- CELL_BRANCH_SET: D_1p5B_prompt; SELECT EXACTLY ONE BRANCH -->

- **1.5B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: D_1p5B_prompt -->

<!-- CELL_BRANCH_SET: D_1p5B_decode; SELECT EXACTLY ONE BRANCH -->

- **1.5B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: D_1p5B_decode -->

<!-- CELL_BRANCH_SET: D_7B_prompt; SELECT EXACTLY ONE BRANCH -->

- **7B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: D_7B_prompt -->

<!-- CELL_BRANCH_SET: D_7B_decode; SELECT EXACTLY ONE BRANCH -->

- **7B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: D_7B_decode -->

At least one token-generation cell selected a nonpublication branch:
[CELL_NONPUBLICATION_SUMMARY]. The claim-level floor gate is therefore
undefined because its armwise-maximum derivation requires exact published
operative floors for both arms. The registered cross-model contrast was not
evaluated against a floor or direction gate. No claim-side sizing quantity or
model-size direction claim is reported.

Do not emit any A, B1, or B2 contrast, gate-outcome, claim-bound, sizing, or
directional-claim paragraph after this ending.


## §7 Variant C1 — 1.5B floor window passes; 7B floor window is refused

<!-- VARIANT_PREDICATE 7_C1:
window_1p5B_pass AND window_7B_refused
-->

**SELECTION GUARD:** Select iff the 1.5B whole-window verdict is PASS and the
7B whole-window verdict is REFUSED.

**Lead-in replacement.** The demonstration asked whether two model-specific
floor windows could support the planned phase cells and the later registered
contrast. The 1.5B floor window passed its whole-window verdict, while the 7B
floor window was refused because [REFUSAL_REASON_7B_floor_window].

The 7B window is preserved as evidence of the protocol outcome but supplies no
claim-bearing phase value or floor. Its bundles are not selectively promoted,
and no favorable member is extracted into a replacement basis. The narrower
statement is that the declared 7B window did not satisfy the evidence
conditions required for a floor.

For the passing 1.5B window, the two phase cells use the following cell-specific
branches.

<!-- CELL_BRANCH_SET: C1_1p5B_prompt; SELECT EXACTLY ONE BRANCH -->

- **1.5B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_prompt_abs_J] J and
  [F_1p5B_prompt_cmp_J] J. Their operative floor is [F_1p5B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: C1_1p5B_prompt -->

<!-- CELL_BRANCH_SET: C1_1p5B_decode; SELECT EXACTLY ONE BRANCH -->

- **1.5B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_1p5B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_1p5B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_1p5B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_1p5B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_1p5B_decode_abs_J] J and
  [F_1p5B_decode_cmp_J] J. Their operative floor is [F_1p5B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_1p5B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: C1_1p5B_decode -->

<!-- MEASUREMENT_RENDER: 1p5B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_1p5B_prompt_J_per_request] J per request, with a fully composed interval of
[E_1p5B_prompt_lower_J]–[E_1p5B_prompt_upper_J] J across
[N_bundles_1p5B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_prompt -->

<!-- MEASUREMENT_RENDER: 1p5B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_1p5B_decode_J_per_request] J per request, with a fully composed interval of
[E_1p5B_decode_lower_J]–[E_1p5B_decode_upper_J] J across
[N_bundles_1p5B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_1p5B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 1p5B_decode -->

Any reported per-token value is also scoped to how the prompt was supplied to
the runtime and whether a beginning-of-sequence token was present, as recorded
for the passing window.

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.


Populate only the 1.5B phase rows to the level authorized by extraction and
mark the 7B rows “not claim-bearing—whole-window verdict refused.” Do not issue
the four-cell artifact or evaluate the cross-model contrast. The registered
cross-model direction remains unanswered, and no model-size energy ranking
follows.

## §7 Variant C2 — 7B floor window passes; 1.5B floor window is refused

<!-- VARIANT_PREDICATE 7_C2:
window_1p5B_refused AND window_7B_pass
-->

**SELECTION GUARD:** Select iff the 7B whole-window verdict is PASS and the
1.5B whole-window verdict is REFUSED.

**Lead-in replacement.** The demonstration asked whether two model-specific
floor windows could support the planned phase cells and the later registered
contrast. The 7B floor window passed its whole-window verdict, while the 1.5B
floor window was refused because [REFUSAL_REASON_1p5B_floor_window].

The 1.5B window is preserved as evidence of the protocol outcome but supplies
no claim-bearing phase value or floor. Its bundles are not selectively
promoted, and no favorable member is extracted into a replacement basis. The
narrower statement is that the declared 1.5B window did not satisfy the
evidence conditions required for a floor.

For the passing 7B window, the two phase cells use the following cell-specific
branches.

<!-- CELL_BRANCH_SET: C2_7B_prompt; SELECT EXACTLY ONE BRANCH -->

- **7B prompt-processing cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_prompt].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_prompt]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_prompt]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_prompt]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_prompt]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_prompt_abs_J] J and
  [F_7B_prompt_cmp_J] J. Their operative floor is [F_7B_prompt_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_prompt_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: C2_7B_prompt -->

<!-- CELL_BRANCH_SET: C2_7B_decode; SELECT EXACTLY ONE BRANCH -->

- **7B token-generation cell:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_7B_decode].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_7B_decode]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_7B_decode]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_7B_decode]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_7B_decode]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_7B_decode_abs_J] J and
  [F_7B_decode_cmp_J] J. Their operative floor is [F_7B_decode_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_7B_decode_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: C2_7B_decode -->

<!-- MEASUREMENT_RENDER: 7B_prompt -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross prompt-processing energy was
[E_7B_prompt_J_per_request] J per request, with a fully composed interval of
[E_7B_prompt_lower_J]–[E_7B_prompt_upper_J] J across
[N_bundles_7B_prompt] independent valid run bundles.

**This prefill value remains floors-only, so it supports no model-size
direction claim.** Gross joules per request remain primary.

**ABSENT TEXT:** No gross prompt-processing energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_prompt_J_per_token] J per recorded prompt token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_prompt -->

<!-- MEASUREMENT_RENDER: 7B_decode -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross token-generation energy was
[E_7B_decode_J_per_request] J per request, with a fully composed interval of
[E_7B_decode_lower_J]–[E_7B_decode_upper_J] J across
[N_bundles_7B_decode] independent valid run bundles.

**ABSENT TEXT:** No gross token-generation energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_7B_decode_J_per_token] J per recorded output token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: 7B_decode -->

Any reported per-token value is also scoped to how the prompt was supplied to
the runtime and whether a beginning-of-sequence token was present, as recorded
for the passing window.

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.


Populate only the 7B phase rows to the level authorized by extraction and mark
the 1.5B rows “not claim-bearing—whole-window verdict refused.” Do not issue the
four-cell artifact or evaluate the cross-model contrast. The registered
cross-model direction remains unanswered, and no model-size energy ranking
follows.

## §7 Variant C3 — both floor windows are refused

<!-- VARIANT_PREDICATE 7_C3:
window_1p5B_refused AND window_7B_refused
-->

**SELECTION GUARD:** Select iff the 1.5B whole-window verdict is REFUSED and the
7B whole-window verdict is REFUSED.

Both model-specific floor windows were refused: the 1.5B window because
[REFUSAL_REASON_1p5B_floor_window], and the 7B window because
[REFUSAL_REASON_7B_floor_window]. Neither window supplies a claim-bearing
phase value or floor. No four-cell floor artifact is issued, the registered
contrast is not evaluated, and no model-size energy ranking follows.

Every per-token denominator is the token count recorded by the runtime for
that request, not a requested maximum or generator estimate.

Any per-token diagnostic remains subject to the same-tokenizer licence: both
arms must record the SAME tokenizer identity, and no number may be compared
with a stack carrying a different tokenizer.

## §6 Variant 0 — Window C not yet result-bearing (DEFAULT)

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
NOT(funded AND run AND an issued whole-window verdict exists). If the predicate
is false, do not use any sentence from this variant.

**Lead-in action.** If the night has not been funded and run, no past-tense
conversion is licensed and the paper’s future-work lead-in remains. If
collection ran but an issued whole-window verdict does not yet exist, results
await the governing verdict; do not describe the completed collection as
future work. This is the default branch until funding, run, and issued-verdict
conditions select another variant.

No characterization result, row-level outcome, or between-session contribution
is reported. The collection must retain the paper’s calibration, admission,
custody, floor, and whole-window verdict rules. Its paired per-token comparisons
must also require both arms to record the SAME tokenizer identity; no resulting
number may be compared with a stack carrying a different tokenizer.

At fill time, adjust the abstract and contributions in one sentence to match
the selected state: planned future work if the night has not run, or results
awaiting the governing verdict if collection ran without an issued verdict.

## §6 Variant A — Window C passes (CONDITIONAL on the night being funded and run)

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
funded AND run AND whole-window verdict = PASS AND every one of the six
registered row outcomes = SUPPORTED. If the predicate is false, do not use any
sentence from this variant.

**Lead-in replacement.** Instrument characterization tested whether the complete
measurement system behaved predictably under the registered signals while
retaining the calibration, admission, custody, floor, and whole-window verdict
rules used for the demonstration. This drop-in is available only under the
selection guard above.

The registered linearity rows followed their qualitative pattern. Gross request
energy and token-generation energy had fitted slopes of
[S_C_linearity_request_J_per_token] J per token and
[S_C_linearity_decode_J_per_token] J per token, with residuals within the
[R_C_linearity_limit_J] J frozen criterion. The short-, medium-, and long-output
null blocks remained within their matching decision envelopes; their largest
absolute ABBA difference was [D_C_null_max_abs_J] J. The micro-differences
series refused the registered sub-floor effects and resolved the registered
super-floor effects in both directions, with effect-to-floor ratios from
[R_C_micro_min_x_floor] to [R_C_micro_max_x_floor] times the applicable
operative floor.

Prompt-processing plus token-generation energy differed from the enclosing
request by [D_C_additivity_J] J under the registered setup and gap treatment.
The fixed-prompt prompt-processing slope against later output length was
[S_C_prompt_invariance_J_per_token] J per token and remained within the
[B_C_prompt_invariance_J_per_token] J-per-token acceptance band. Start,
midpoint, and end references had a maximum excursion of
[D_C_reference_excursion_J] J, and admitted conditions recovered within
[T_C_recovery_s] seconds. The drift screen passed; the allowance remains
positive by construction.

Between-session stability requires at least three eligible sessions or days
with the full stack identity recorded. A collection contributing fewer than
three eligible sessions leaves that row pending. This variant therefore binds
only after the between-session row also supported its registered behavior.

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.

## §6 Variant B — Window C passes with mixed rows (CONDITIONAL on the night being funded and run)

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
funded AND run AND whole-window verdict = PASS AND at least one of the six
registered row outcomes != SUPPORTED. If the predicate is false, do not use any
sentence from this variant.

**Lead-in replacement.** Instrument characterization tested the registered
qualitative behaviors under the same calibration, admission, custody, floor,
and whole-window verdict rules used for the demonstration. This drop-in is
available only under the selection guard above.

<!-- ROW_RENDER: linearity -->
The linearity row [PLAIN_LANGUAGE_RESULT_linearity].
<!-- IF diagnostic_linearity_present -->
The authenticated fitted slopes were
[S_C_linearity_request_J_per_token] J per token for gross request energy and
[S_C_linearity_decode_J_per_token] J per token for token-generation energy,
with a residual limit of [R_C_linearity_limit_J] J.
<!-- ELSE: emit no numeric linearity clause -->
<!-- END_ROW_RENDER: linearity -->

<!-- ROW_RENDER: null -->
The null-response row [PLAIN_LANGUAGE_RESULT_null].
<!-- IF diagnostic_null_present -->
Its largest authenticated absolute ABBA difference was
[D_C_null_max_abs_J] J.
<!-- ELSE: emit no numeric null clause -->
<!-- END_ROW_RENDER: null -->

<!-- ROW_RENDER: empirical_floor -->
The empirical-floor row [PLAIN_LANGUAGE_RESULT_floor].
<!-- IF diagnostic_empirical_floor_present -->
The authenticated micro-differences effect-to-floor range was
[R_C_micro_min_x_floor] to [R_C_micro_max_x_floor] times the applicable
operative floor.
<!-- ELSE: emit no numeric empirical-floor clause -->
<!-- END_ROW_RENDER: empirical_floor -->

<!-- ROW_RENDER: phase_attribution -->
The phase-attribution row [PLAIN_LANGUAGE_RESULT_phase].
<!-- IF diagnostic_phase_attribution_present -->
The authenticated additivity residual was [D_C_additivity_J] J, and the
fixed-prompt prompt-processing slope against later output length was
[S_C_prompt_invariance_J_per_token] J per token.
<!-- ELSE: emit no numeric phase-attribution clause -->
<!-- END_ROW_RENDER: phase_attribution -->

<!-- ROW_RENDER: drift_settling -->
The drift-and-settling row [PLAIN_LANGUAGE_RESULT_drift].
<!-- IF diagnostic_drift_settling_present -->
The authenticated reference excursion was [D_C_reference_excursion_J] J, and
recovery time was [T_C_recovery_s] seconds.
<!-- ELSE: emit no numeric drift-and-settling clause -->
<!-- IF outcome_drift_supported -->
The drift screen passed; the allowance remains positive by construction.
<!-- ELSE: emit no passed-screen sentence -->
<!-- END_ROW_RENDER: drift_settling -->

<!-- ROW_RENDER: between_sessions -->
The between-session row [PLAIN_LANGUAGE_RESULT_between_sessions].
<!-- IF diagnostic_between_sessions_present -->
The authenticated row included [N_C_eligible_sessions] eligible sessions or
days.
<!-- ELSE: emit no numeric between-session clause -->
Between-session stability requires at least three eligible sessions or days
with the full stack identity recorded. A collection contributing fewer than
three eligible sessions leaves that row pending.
<!-- END_ROW_RENDER: between_sessions -->

A row that did not support a conclusion remains unresolved under its registered
criterion; a row showing that expected behavior did not hold identifies a
limit of the instrument model and narrows any affected phase claim. Neither
outcome means zero effect or equality.

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.

## §6 Variant C — Window C verdict refusal (CONDITIONAL on the night being funded and run)

**SELECTION GUARD — remove after filling:** Choose this variant if and only if
funded AND run AND whole-window verdict = REFUSED. If the predicate is false,
do not use any sentence from this variant.

**Lead-in replacement.** Instrument characterization attempted the registered
tests under the paper’s calibration, admission, custody, floor, and
whole-window verdict rules. This drop-in is available only under the selection
guard above.

Window C did not pass its whole-window verdict because
[REFUSAL_REASON_window_C]. None of its characterization rows is promoted as
claim-bearing, even where a partial calculation appears qualitatively
favorable.

<!-- PRESENT_DIAGNOSTICS_RENDER: section_6_C
ORDER: linearity, null, empirical_floor, phase_attribution, drift_settling -->

For each row whose authenticated diagnostic exists, append exactly its clause:

- `linearity`: “the fitted linearity observation was
  [D_C_linearity_diagnostic_J_per_token] J per token”
- `null`: “the largest null observation was [D_C_null_diagnostic_J] J”
- `empirical_floor`: “the micro-differences observation was
  [D_C_micro_diagnostic_x_floor] times the applicable operative floor”
- `phase_attribution`: “the phase-consistency observation was
  [D_C_phase_diagnostic_J] J”
- `drift_settling`: “the drift observation was
  [D_C_drift_diagnostic_J] J”

If one or more diagnostics exist, emit:

“Authenticated values available before the refusal are reported as diagnostics
only: [PRESENT_DIAGNOSTIC_LIST].”

If one or more rows are absent, append:

“No authenticated numeric diagnostic is reported for
[ABSENT_DIAGNOSTIC_ROW_LIST]. Their absence is not treated as zero and no
replacement is selected after outcomes are visible.”

If all five are absent, emit only:

“No authenticated numeric characterization diagnostic is available from the
refused window. Missing stages or members are not treated as zero and are not
replaced after outcomes are visible.”

<!-- END_PRESENT_DIAGNOSTICS_RENDER: section_6_C -->

Lists use the fixed row order above, serial commas, and “and” before the final
item. Tokens for absent diagnostics must not survive rendering.

When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity. This collection
did not establish the instrument behavior required by the frozen
characterization plan, and it adds
no eligible session to the between-session row. Any later attempt must be a
prospectively authorized fresh window with its own calibration bracket,
evidence root, fixed membership, and verdict.
