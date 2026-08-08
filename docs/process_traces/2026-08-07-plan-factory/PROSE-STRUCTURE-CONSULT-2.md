# Results-prose structure consult — EXTENSION round of record (2026-08-08)

Resumed session of the original structure consult (same design
authority), charged with the round-2 delta's six blockers + linter
gaps (class at count 3, section level — see PROSE-ESCALATION.md
addendum).

**MAGISTRATE ADOPTION (Fable, 2026-08-08): ADOPTED IN FULL.** Second
selector layer of machine-readable VARIANT_PREDICATEs (linter parses
them — no hard-coded truth table); new terminating §7 Variant D for
decode-cell nonpublication (canonical blocks 16 -> 20);
MEASUREMENT_RENDER present/absent branches licensing every numeric
clause; C1/C2 tokenizer licence converted to conditional form; §6 B
per-row renderers; §6 C present-only diagnostic generation with
deterministic omission wording; neutral Variant 0 heading; the
mechanical E/X/A selector with closed TERMINAL / NONTERMINAL code
sets and STOP_FILL semantics (U reachable only from dominance-ABSENT,
never generic A=false); the N-branch diagnostic renderer incl. the
zero-diagnostic case; the extended linter with section-scoped token
licensing and ten discrimination tests. Prior-design-unchanged and
revised must-not-change lists bind round 3.

---

The extension should add a second selector layer above T/N/L/U. A/B1/B2 become legal only after both decode cells publish through L or U; a new terminating §7 D owns the complementary T/N outcome. Numeric prose elsewhere moves behind explicit availability renderers.

## 1. §7 section-level selection

Add this parseable master taxonomy to the fill key:

```markdown
### §7 variant predicates

<!-- VARIANT_PREDICATE 7_A:
window_1p5B_pass AND window_7B_pass
AND decode_1p5B_published AND decode_7B_published
AND claim_floor_defined
AND contrast_signed_present
AND contrast_interval_present
AND claim_bound_present
AND floor_gate_pass AND direction_gate_pass
-->

<!-- VARIANT_PREDICATE 7_B1:
window_1p5B_pass AND window_7B_pass
AND decode_1p5B_published AND decode_7B_published
AND claim_floor_defined
AND contrast_magnitude_present
AND claim_bound_present
AND floor_gate_refused
-->

<!-- VARIANT_PREDICATE 7_B2:
window_1p5B_pass AND window_7B_pass
AND decode_1p5B_published AND decode_7B_published
AND claim_floor_defined
AND contrast_signed_present
AND contrast_interval_present
AND claim_bound_present
AND floor_gate_pass AND direction_gate_refused
-->

<!-- VARIANT_PREDICATE 7_D:
window_1p5B_pass AND window_7B_pass
AND (decode_1p5B_nonpublication OR decode_7B_nonpublication)
-->

<!-- VARIANT_PREDICATE 7_C1:
window_1p5B_pass AND window_7B_refused
-->

<!-- VARIANT_PREDICATE 7_C2:
window_1p5B_refused AND window_7B_pass
-->

<!-- VARIANT_PREDICATE 7_C3:
window_1p5B_refused AND window_7B_refused
-->
```

Definitions:

```markdown
- `decode_*_published` means that cell selected L or U.
- `decode_*_nonpublication` means that cell selected T or N.
- For each decode cell, exactly one of `published` and `nonpublication` is
  true.
- `claim_floor_defined` is true only after
  `F_claim_decode_armwise_max_J` has been derived and verified from two
  published decode operative floors.
- A missing required contrast, interval, or claim-bound source stops selection;
  it never defaults to zero or selects another outcome.
```

Place the corresponding visible guard immediately below A/B1/B2 headings. For example:

```markdown
**SELECTION GUARD — remove after filling:** Choose this variant if and only if
both model-specific floor windows passed, both token-generation cells selected
L or U, the claim-level floor gate was mechanically derived, every numeric
source named by this variant is authenticated, and the registered contrast had
the gate outcomes named in this heading. Otherwise do not use any sentence
from this variant.
```

The linter must require the visible guard to be generated from—and semantically equivalent to—the adjacent `VARIANT_PREDICATE`, not merely present.

### Terminating §7 D

Add a self-contained variant using four unchanged canonical cell blocks with IDs `D_1p5B_prompt`, `D_1p5B_decode`, `D_7B_prompt`, and `D_7B_decode`. This raises the expected block count from 16 to 20.

```markdown
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

[THE FOUR UNCHANGED CANONICAL CELL BLOCKS]

At least one token-generation cell selected a nonpublication branch:
[CELL_NONPUBLICATION_SUMMARY]. The claim-level floor gate is therefore
undefined because its armwise-maximum derivation requires exact published
operative floors for both arms. The registered cross-model contrast was not
evaluated against a floor or direction gate. No claim-side sizing quantity or
model-size direction claim is reported.

Do not emit any A, B1, or B2 contrast, gate-outcome, claim-bound, sizing, or
directional-claim paragraph after this ending.
```

`[CELL_NONPUBLICATION_SUMMARY]` is mechanically generated in 1.5B-then-7B order from selected T/N branches. It contains each affected cell name and its already-rendered terminal or no-exact-floor reason.

## 2. Measurement-paragraph licensing

Every phase-measurement paragraph in A/B1/B2/C1/C2 must use this renderer. This also protects prompt-cell T/N outcomes that do not prevent a decode contrast.

```markdown
<!-- MEASUREMENT_RENDER: [MODEL]_[PHASE] -->

**PRESENT GUARD:** Emit the gross measurement clause only when the authenticated
phase estimate, both composed interval endpoints, and independent-valid-bundle
count exist.

**PRESENT TEXT:** Gross [PHASE_DISPLAY] energy was
[E_MODEL_PHASE_J_per_request] J per request, with a fully composed interval of
[E_MODEL_PHASE_lower_J]–[E_MODEL_PHASE_upper_J] J across
[N_bundles_MODEL_PHASE] independent valid run bundles.

**ABSENT TEXT:** No gross [PHASE_DISPLAY] energy estimate is reported because
the authenticated estimate-and-interval record is unavailable. An absent
measurement is not zero.

**COMPANION GUARD:** Append the companion clause only when its authenticated
per-token value and runtime-observed denominator provenance both exist.

**COMPANION TEXT:** Its tokenizer-scoped companion was
[E_MODEL_PHASE_J_per_token] J per recorded [prompt/output] token. The
denominator is the token count recorded by the runtime for that request, not a
requested maximum or generator estimate.

**NO-COMPANION TEXT:** No per-token companion is reported because an
authenticated runtime-observed denominator is unavailable.

<!-- END_MEASUREMENT_RENDER: [MODEL]_[PHASE] -->
```

For C1/C2, replace the factual tokenizer assertion with exactly:

```markdown
When both arms record the same tokenizer identity, that match makes the
per-token companion comparable between those arms. No per-token number may be
compared with a stack carrying a different tokenizer identity.
```

Retain immediately before it:

```markdown
Any reported per-token value is also scoped to how the prompt was supplied to
the runtime and whether a beginning-of-sequence token was present, as recorded
for the passing window.
```

The conditional licence does not assert that the refused arm established tokenizer identity.

## 3. §6 B row-level rendering

Replace its unconditional numeric vector with six independent render blocks. The plain-language outcome always renders; the numeric clause renders only when that row’s authenticated diagnostic exists.

```markdown
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
```

No numeric token may occur outside its corresponding `diagnostic_*_present` block.

## 4. §6 C present-only diagnostic generation

Replace the five-value sentence with a deterministic ordered renderer:

```markdown
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
```

Lists use the fixed row order above, serial commas, and “and” before the final item. Tokens for absent diagnostics must not survive rendering.

## 5. Neutral Variant 0 heading

Replace only the heading:

```markdown
## §6 Variant 0 — Window C not yet result-bearing (DEFAULT)
```

Its existing predicate and state-sensitive lead-in remain unchanged.

## 6. Mechanical E/X/A selector

Replace the current three inferred booleans with a selector computed from authenticated component reports.

### Closed terminal set

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

`admissible_set_uncertainty_dominates_point_floor` is deliberately absent from that set because its disposition depends on exact-floor and licence fields.

### Closed nonterminal exact-unavailable set

```text
NONTERMINAL_EXACT_FLOOR_UNAVAILABLE_CODES = {
  exact_corner_widened_absolute_floor_unavailable,
  exact_corner_widened_comparative_floor_unavailable
}
```

These are selector-normalized states, not new scientific refusal meanings. Generate one only when the corresponding component has:

- raw reasons exactly `{admissible_set_uncertainty_dominates_point_floor}`;
- no terminal reason;
- no exact corner-widened floor; and
- otherwise valid authenticated extraction metadata.

A generically absent component, missing evidence, null `floor_gate_j`, or unmatched reason does not enter N automatically.

### Algorithm

```text
1. Validate both component records and all reason codes.
   Unknown code, malformed metadata, or stored/recomputed mismatch => STOP_FILL.

2. terminal :=
     all authoritative reasons in TERMINAL_REASON_CODES.
   If terminal is nonempty => E=false; select T.

3. Normalize the two permitted exact-unavailable states above.
   If at least one exists and terminal is empty => E=true, X=false; select N.

4. If either exact final component is absent and step 3 did not classify it
   => STOP_FILL. Do not infer N from nullness.

5. X=true iff:
     both final component floors are finite and authenticated,
     stored operative floor is finite,
     stored operative floor == max(abs, cmp), and
     all non-exact eligibility requirements pass.

6. Compute DOMINANCE_STATE:

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

7. If DOMINANCE_STATE=UNLICENSED, add
   attribution_dominance_unlicensed and select T.

8. A=true iff DOMINANCE_STATE=LICENSED.

9. With E=true and X=true:
     A=true  => select L.
     A=false and DOMINANCE_STATE=ABSENT => select U.

10. Every other state => STOP_FILL.
```

This makes dominance absent distinct from dominance present but unlicensed. U is reachable only from `ABSENT`, never from a generic `A=false`.

## 7. N diagnostic renderer

Define `[AVAILABLE_DIAGNOSTIC_CLAUSE_CELL]` completely:

```markdown
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
```

## 8. Linter extension

Retain the existing checks and add the following.

### Cell semantics

For every cell ID, derive its concrete stem and assert:

- U’s publication sentence contains exactly `[F_<stem>_operative_J]`.
- The same sentence contains neither `_abs_J`, `_cmp_J`, `_point_J`, nor `_corner_J`.
- The fill key defines `F_<stem>_operative_J` through the generic max rule.
- After removing the exact negative sentence “No floor is published for this cell,” T and N contain no case-insensitive publication verb.
- No non-L sentence may combine an attribution-limited label with a publication assertion.
- Normalize tokens and require each T/N/L/U body to match the canonical schema exactly; unexpected appended sentences fail.

### Concrete derived-token exclusion

Expand the derived family before scanning `### Source values`:

```text
F_1p5B_prompt_operative_J
F_1p5B_decode_operative_J
F_7B_prompt_operative_J
F_7B_decode_operative_J
F_claim_decode_armwise_max_J
M_decode_contrast_abs_J_per_request
C_decode_floor_clearance_J
S_decode_floor_shortfall_J
R_decode_effect_x_floor
S_decode_joint_J
```

Reject both bracketed and unbracketed independent source declarations for any member.

### Section-scoped checks

- Require the exact ≥3-session paragraph once inside §6 A and once inside §6 B; global counts are insufficient.
- Require every A/B1/B2 claim-floor or contrast token to occur only in a section whose parsed predicate implies both decode publication atoms and `claim_floor_defined`.
- Require every phase-measurement token to occur inside its matching `MEASUREMENT_RENDER` present branch.
- Require every §6 B numeric token inside its row’s present-diagnostic branch.
- Require every §6 C diagnostic token inside the present-only renderer.
- Require §7 D and forbid claim-floor, contrast-outcome, claim-bound, sizing, clearance, shortfall, and direction tokens within it.
- Require the neutral Variant 0 heading exactly.
- Require the conditional tokenizer sentence in C1 and C2 and forbid the factual “Both arms record…” form there.

### Enum detection

Apply both patterns case-insensitively to professor-facing prose:

```python
r"\[[^\]\n]*:[^\]\n]*/[^\]\n]*\]"
r"\[[^\]\n]*(supported|refused|failed[_ -]?expected)[^\]\n]*/[^\]\n]*\]"
```

Also reject a bare choice such as `[supported/refused]`; do not require a colon or uppercase initial.

### Parsed truth tables

Use the template’s `VARIANT_PREDICATE` expressions as inputs to a recursive-descent parser:

```text
expr  := term ("OR" term)*
term  := unary ("AND" unary)*
unary := "NOT" unary | IDENT | "(" expr ")"
```

Do not retain a hard-coded `selected_variants` formula.

Enumerate valid §6 states and valid §7 states, evaluate the parsed expressions, and require exactly one selected variant. Also require each visible guard to render from the parsed AST. A test that mutates both the master and immediate visible predicate must therefore fail from an actual overlap or gap, not from string inequality alone.

Add discriminating tests for every delta mutation:

- U publishes the absolute component.
- T adds positive point-floor publication.
- U adds attribution-limited publication.
- ≥3-session text is moved out of §6 A.
- lowercase `[supported/refused]` appears.
- concrete operative token is declared in Source values.
- A’s predicate is changed to overlap B after both textual copies are updated.
- a claim-floor paragraph is moved outside its licensing section.
- a C measurement token is moved outside its present renderer.
- a §6 B/C absent diagnostic survives into rendered prose.

## Prior design unchanged

Implementation round 3 should not rewrite:

- The canonical T/N/L/U order, guards, or branch prose.
- The operative-floor `max(abs, cmp)` rule and all seven existing derivations.
- L’s labelled publication rule or U’s exact unlabelled publication rule.
- T’s terminal-refusal semantics or N’s no-exact-floor semantics; only their selector and N diagnostic renderer are completed.
- C1/C2’s model-specific token split and C3’s terminating both-refused result.
- The §6 0/A/B/C predicate meanings; only Variant 0’s heading changes.
- B1’s magnitude-only contrast shape and its four arm-level intervals.
- The exact two-half sizing denial in A/B1/B2.
- Runtime-observed denominator provenance and prompt-delivery/beginning-of-sequence scope.
- The same-tokenizer licence and different-tokenizer prohibition; C1/C2 merely change from an unsupported factual assertion to its conditional form.
- The ≥3-session rule, D-119 conservative wording, and the dated 105+9 addendum.

## Revised must-not-change list

- Variant 0 remains marked `(DEFAULT)`.
- Preserve exactly: “It is not a single summed acceptance threshold, and the decision interval was not compared with the sum.”
- B1 remains magnitude-only at the contrast level: no signed cross-model estimate or directional contrast interval.
- No point-only diagnostic becomes a published floor.
- No floor or claim-floor token is synthesized from missing evidence.
- Tokenizer-scoped companions remain secondary to gross joules per request and prohibited across different tokenizer identities.
- C3 remains a no-floor, no-contrast, no-ranking termination.
- The 105+9 addendum remains untouched.
- Round 3 adds §7 D and licensing/rendering markers but does not alter governing paper claims, measurement semantics, decision-log doctrine, or existing authenticated evidence.

Checks performed: read delta-2 and the count-3 addendum in full, inspected the complete implemented template, linter and focused tests, and traced selector reason fields to the extraction/floor contracts; no files edited and no tests run.