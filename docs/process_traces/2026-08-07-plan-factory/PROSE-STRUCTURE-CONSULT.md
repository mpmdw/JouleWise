# Results-prose conditional-structure consult — response of record (2026-08-08)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge. Charge:
PROSE-ESCALATION.md beside this file (same-signature count 2).

**MAGISTRATE ADOPTION (Fable, 2026-08-08): ADOPTED IN FULL.** Four-way
T/N/L/U per-cell partition (terminal refusal checked first, no
catch-all ELSE publishes); branch U publishes max(abs,cmp) — the
'UNLABELLED at point-only value' wording is retired; DERIVE-only
derived tokens; §6 selection predicates exhaustive+mutually exclusive
with the between-session >=3-sessions row gating Variant A; C split
into C1/C2 plus the new terminating C3 (both refused); mechanical
lint + focused test. Fix round 2 implements this verbatim; the
must-not-change list binds.

---

The safe design is a four-way per-cell partition, not a three-way `IF/ELSE`. Terminal refusal and absence of an exact floor must be separate because they bind different reasons and permit different diagnostic reporting.

## 1. Canonical per-cell block

Define these selector facts before choosing prose:

- `E_CELL`: every eligibility requirement except the specially licensed attribution-dominance condition passes.
- `X_CELL`: both exact final component floors exist, so an exact operative floor can be derived.
- `A_CELL`: authenticated evidence says attribution dominance is the sole otherwise-refusing condition.
- Any inconsistent state—such as attribution-limited metadata without the corresponding sole-condition evidence—stops filling rather than selecting a prose branch.

Use this exact block at every cell site:

```markdown
<!-- CELL_BRANCH_SET: [CELL_ID]; SELECT EXACTLY ONE BRANCH -->

- **[CELL_DISPLAY_NAME]:**

  **BRANCH T — TERMINAL REFUSAL**

  **GUARD:** Select this branch first if `E_CELL` is false because one or
  more terminal refusal reasons are present. Do not evaluate the publication
  branches.

  **TEXT:** No floor is published for this cell. The governing refusal was:
  “[TERMINAL_REFUSAL_REASON_CELL].” The attribution-limited licence does not
  alter that refusal. Any available intermediate values remain diagnostics
  and cannot support a claim.

  **BINDS:** `[TERMINAL_REFUSAL_REASON_CELL]` and, only if produced
  mechanically, `[AVAILABLE_DIAGNOSTIC_CLAUSE_CELL]`. It does not bind an
  operative-floor token.

  **BRANCH N — NO EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` is true and `X_CELL` is false.

  **TEXT:** No floor is published for this cell. The otherwise eligible
  evidence did not yield an exact operative floor because
  [NO_EXACT_FLOOR_REASON_CELL]. Any available component or point-only
  repeatability value is reported as a diagnostic only and cannot support a
  claim. [AVAILABLE_DIAGNOSTIC_CLAUSE_CELL]

  **BINDS:** `[NO_EXACT_FLOOR_REASON_CELL]` and the mechanically generated
  diagnostic clause. It does not bind an operative-floor token.

  **BRANCH L — LABELLED ATTRIBUTION-LIMITED FLOOR**

  **GUARD:** Select this branch iff `E_CELL`, `X_CELL`, and `A_CELL` are all
  true.

  **TEXT:** The absolute and comparative components are [F_CELL_abs_J] J and
  [F_CELL_cmp_J] J. Their operative floor is [F_CELL_operative_J] J, the
  larger of the two components; the components are not summed. Because energy
  uncertainty from shifting the phase edges within the calibrated clock-anchor
  bound was the sole otherwise-refusing condition and an exact corner-widened
  floor exists, this operative floor is published with the label
  *attribution-limited*. [POINT_DIAGNOSTIC_CLAUSE_CELL]

  **BINDS:** the two component tokens, the mechanically derived operative
  token, and the mechanically generated component-specific point-diagnostic
  clause. It binds no refusal-reason token.

  **BRANCH U — UNLABELLED EXACT FLOOR**

  **GUARD:** Select this branch iff `E_CELL` and `X_CELL` are true and
  `A_CELL` is false.

  **TEXT:** The absolute and comparative components are [F_CELL_abs_J] J and
  [F_CELL_cmp_J] J. Their operative floor is [F_CELL_operative_J] J, the
  larger of the two components; the components are not summed. The
  attribution-limited label condition is not met, so the exact authorized
  [F_CELL_operative_J] J operative floor is published without that label. A
  separately retained point-only repeatability value, if present, remains a
  diagnostic and does not replace the operative floor.

  **BINDS:** the two component tokens and the mechanically derived operative
  token. It binds neither a point value as the floor nor a refusal-reason
  token.

<!-- END_CELL_BRANCH_SET: [CELL_ID] -->
```

The branch order matters: terminal refusal, no exact floor, labelled exact floor, unlabelled exact floor. No catch-all `ELSE` may publish anything.

Branch U must publish `max(abs, cmp)`, not the point-only value. The current “UNLABELLED at its point-only value” wording conflicts with the governing operative-floor rule and must disappear. A point-only value appears only in a diagnostic sentence and never occupies the operative-floor slot.

## 2. Replacement fill-key sections

```markdown
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

### Plain-language outcome fills

- Machine enum values may be used internally by the selector but must not
  appear as professor-facing fills.
- Each `[PLAIN_LANGUAGE_RESULT_*]` receives one complete predicate phrase:
  “supported the registered behavior”; “did not support a conclusion under
  the registered criterion”; “showed that the registered expected behavior
  did not hold”; or, for between-session stability only, “remains pending
  because fewer than three eligible sessions are available.”
```

## 3. §6 variant predicates and placement

Validate first that a completed run has an issued verdict before treating it as a result. Then use:

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

The six rows include between-session stability. Therefore Variant A is unavailable until at least three eligible sessions or days support that row. A pending between-session row selects B, not A.

Put the full predicate immediately below each §6 heading, before the lead-in:

```markdown
**SELECTION GUARD — remove after filling:** Choose this variant if and only if
[exact predicate]. If the predicate is false, do not use any sentence from
this variant.
```

Retain the master predicate list in the fill key as well. Variant 0 remains the default. If collection ran but its verdict has not issued, Variant 0 must say that results await the governing verdict rather than falsely calling the completed collection future work.

Replace §6 B’s shorthand outcome sentence with:

```markdown
The linearity row [PLAIN_LANGUAGE_RESULT_linearity]; the null-response row
[PLAIN_LANGUAGE_RESULT_null]; the empirical-floor row
[PLAIN_LANGUAGE_RESULT_floor]; the phase-attribution row
[PLAIN_LANGUAGE_RESULT_phase]; the drift-and-settling row
[PLAIN_LANGUAGE_RESULT_drift]; and the between-session row
[PLAIN_LANGUAGE_RESULT_between_sessions].
```

## 4. Variant C schema

Split C. The extra duplicated prose is safer than a selector-dependent alias table under deadline.

```markdown
## §7 Variant C1 — 1.5B floor window passes; 7B floor window is refused

**SELECTION GUARD:** Select iff the 1.5B whole-window verdict is PASS and the
7B whole-window verdict is REFUSED.

Use only `F_1p5B_*`, `E_1p5B_*`, and `N_bundles_1p5B_*` tokens for the passing
cells and measurements. Bind `[REFUSAL_REASON_7B_floor_window]` for the failed
window. Mark the 7B rows non-claim-bearing. Do not issue the four-cell artifact
or evaluate the cross-model contrast.
```

```markdown
## §7 Variant C2 — 7B floor window passes; 1.5B floor window is refused

**SELECTION GUARD:** Select iff the 7B whole-window verdict is PASS and the
1.5B whole-window verdict is REFUSED.

Use only `F_7B_*`, `E_7B_*`, and `N_bundles_7B_*` tokens for the passing cells
and measurements. Bind `[REFUSAL_REASON_1p5B_floor_window]` for the failed
window. Mark the 1.5B rows non-claim-bearing. Do not issue the four-cell
artifact or evaluate the cross-model contrast.
```

Delete all `F_passing_*`, `E_passing_*`, `N_bundles_passing_*`,
`[1.5B/7B]`, and `[7B/1.5B]` tokens.

Because no cited invariant guarantees that exactly one window passes, add a terminating both-refused branch:

```markdown
## §7 Variant C3 — both floor windows are refused

Both model-specific floor windows were refused: the 1.5B window because
[REFUSAL_REASON_1p5B_floor_window], and the 7B window because
[REFUSAL_REASON_7B_floor_window]. Neither window supplies a claim-bearing
phase value or floor. No four-cell floor artifact is issued, the registered
contrast is not evaluated, and no model-size energy ranking follows.
```

Splitting C increases instantiated cell blocks from 14 to 16: twelve in A/B1/B2 and two each in C1/C2.

## 5. Four folded should-fixes

B1 per-arm intervals:

```markdown
Gross prompt-processing energy was [E_1p5B_prompt_J_per_request] J per request
for 1.5B, with a fully composed arm-level interval of
[E_1p5B_prompt_lower_J]–[E_1p5B_prompt_upper_J] J across
[N_bundles_1p5B_prompt] independent valid run bundles, and
[E_7B_prompt_J_per_request] J per request for 7B, with a fully composed
arm-level interval of [E_7B_prompt_lower_J]–[E_7B_prompt_upper_J] J across
[N_bundles_7B_prompt] independent valid run bundles.

Gross token-generation energy was [E_1p5B_decode_J_per_request] J per request
for 1.5B, with a fully composed arm-level interval of
[E_1p5B_decode_lower_J]–[E_1p5B_decode_upper_J] J, and
[E_7B_decode_J_per_request] J per request for 7B, with a fully composed
arm-level interval of [E_7B_decode_lower_J]–[E_7B_decode_upper_J] J. These are
intervals for the individual arms, not a signed cross-model estimate or a
directional contrast interval.
```

Between-session minimum:

```markdown
Between-session stability requires at least three eligible sessions or days
with the full stack identity recorded. A collection contributing fewer than
three eligible sessions leaves that row pending.
```

Runtime-observed provenance, in every §7 branch:

```markdown
Every per-token denominator is the token count recorded by the runtime for
that request, not a requested maximum or generator estimate.
```

Additional C1/C2 binding in plain language:

```markdown
The per-token values are also scoped to how the prompt was supplied to the
runtime and whether a beginning-of-sequence token was present, as recorded
for the passing window.
```

Plain-language §6 choices use the fill phrases defined above; do not restore bracket choices such as `supported/refused` or `failed_expected_behavior`.

## 6. Mechanical structural guard

Add `docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py` and invoke it from a focused unit test.

It should assert:

- Exactly 16 complete `CELL_BRANCH_SET` blocks after the C split.
- Every block contains exactly T/N/L/U once, in that order, with an end marker.
- Only L and U contain “is published”; T and N contain “No floor is published.”
- Only L contains the attribution-limited publication label.
- No occurrence of “UNLABELLED at its point-only value.”
- Every derived token has exactly one `DERIVE` declaration and cannot appear in the source-token list.
- No `F_passing_*`, `E_passing_*`, singular `F_*_corner_J`, singular `F_*_point_J`, or coupled model-choice token remains.
- Every §6 variant has a guard immediately after its heading.
- Truth-table enumeration gives exactly one §6 variant for every valid selector state.
- Variant A requires all six rows supported; Variant B requires a passing window plus at least one non-supported row.
- B1 contains all four arm-level interval pairs but contains neither the signed contrast token nor cross-model contrast endpoint tokens.
- Every §7 branch contains the runtime-observed denominator sentence.
- C1 and C2 contain the plain-language prompt-delivery and beginning-of-sequence binding.
- The exact two-half sizing denial remains present in A, B1, and B2.
- Variant 0 remains marked `DEFAULT`.

## Fix round 2 must not change

- §6 Variant 0 remains the default.
- Preserve exactly: “It is not a single summed acceptance threshold, and the decision interval was not compared with the sum.”
- Preserve B1’s magnitude-only contrast shape: magnitude, floor gate, shortfall, and ratio only—no signed cross-model estimate or directional contrast interval. Restored per-arm intervals do not alter this.
- Preserve the affirmative same-tokenizer licence and the prohibition on comparison with a different tokenizer.
- Preserve the dated 105-plus-9 placeholder-count addendum; do not rewrite its underlying disposition.

Checks performed: read the current template, examination, escalation, governing paper sections, D-119 and floor-composition contract, and inspected worktree status; no files changed and no test suite run for this read-only consult.