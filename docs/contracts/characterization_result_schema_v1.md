# Characterization Result Schema

This document is the ONE normative home for the pair
`joulewise.characterization_result_spec.v1` (the frozen specification) and
`joulewise.characterization_result.v1` (the issued report). No other file
defines a second characterization result schema, a second outcome vocabulary,
or a second set of pass criteria.

Its authority is the ratified co-design ruling for the characterization
schema. Where this contract and the seat designs disagree, the ruling governs.
<!-- authority: docs/process_traces/2026-08-24-p06-codesign/05-MAGISTRATE-RULING-P06.md (ratified characterization_result_spec.v1); seat records 01-04 in the same directory -->

## The problem this schema exists to fix

The project already fixes, before any measurement, *which* runs will be
measured: the campaign plan names every member, its order, and its
configuration, and records the exact bytes and their fingerprint before any
outcome exists. It has never fixed, before measurement, *what counts as
passing*. A pass criterion that lives in analysis code or in a working note is
a criterion that can be edited after the data are in hand, and once was: a
condition that refused three cells was converted from a hard refusal into a
labelled claim path on the same day the data those cells came from were
collected.
<!-- evidence: configs/floor_mint/a10_extraction_spec.json carries keys ['schema_version', 'cells'] only — membership, no criterion; the refusal-to-label conversion is docs/decision_log.md:4730-4740 (commit ffee598) against the criterion registered at docs/decision_log.md:4238-4241 (commit ca6861b) -->

That is not misconduct, and the record of it is candid. It is a mechanism
defect: nothing in the pipeline could refuse the edit, because nothing had
frozen the criterion in the first place. This schema is the missing freeze.
Everything below exists so that a characterization row's pass criterion is
fixed, fingerprinted, and ordered before its first member is measured, and so
that a row that fails is published as a result rather than quietly re-run.

## No values in this contract

This contract carries no limit, tolerance, sample count, or any other value
that a criterion is decided against. Every such number lives in the frozen
specification JSON, which is covered by a fingerprint recorded before
collection. A limit written into prose can be changed by an editing pass with
no freeze receipt; a limit written into the fingerprinted specification cannot.

Numerals therefore appear in this document only inside identifiers, schema
names, file paths, and evidence comments, plus one quotation: the report
template's fixed phrase for a pending between-session row spells a session
count in words. That numeral belongs to the template, not to this contract,
and the operative count lives in the specification.

## Terms used below

Every term of art in this contract is defined here before it is used. Terms
already defined by the paper's methodology section — *window*, *bundle*,
*member*, *corpus*, *verdict*, *reduction*, *issued*, *cell*, *campaign*,
*authenticated*, *fixed*, *claim-bearing*, *diagnostic* — keep those
definitions and are not redefined.
<!-- evidence: docs/paper/draft-v1.md:38 (paper term definitions), :40-46 (phase and integration boundary) -->

| Term | Definition |
|---|---|
| **Admitted bundle** | One member bundle that passed every frozen entry and verification check. A bundle that failed any check is not admitted and is never counted toward a criterion's evidence. |
| **A/B/B/A block** | Four runs measured in the order condition A, condition B, condition B, condition A. Its signed difference is the mean of the two B energies minus the mean of the two A energies. One block is one independent unit. |
| **Characterization row** | One of the six public properties the paper's characterization table reports. A row is a reporting unit, not a decision unit. |
| **Criterion** | The decision unit: one named quantity, one estimator, one sample unit, one minimum evidence count, one decision rule, and one limit or derivation rule for that limit. A row carries one or more criteria and passes only when all of them pass. |
| **Estimator** | The named formula together with the exact authenticated input fields it reads. An estimator that cannot name its input field paths is not an estimator. |
| **Limit** | The value a criterion's quantity is compared against. Every limit is fixed before collection, either as a literal in the specification or as a derivation rule that resolves to a literal at freeze time from an already-issued artifact. |
| **Limit basis** | Where a limit's authority comes from. `ruled` means a value already fixed by a ratified decision or by committed code. `derived` means a formula over authenticated prior artifacts. `ed_input_required` means no basis exists yet; the freeze is blocked until one is ratified. |
| **Held-out probe** | An authenticated member deliberately excluded from constructing the comparator it is later tested against. A reference that helped build an allowance cannot then be used to show the allowance contains it; that test is satisfied by construction and measures nothing. |
| **Containment** | The whole composed interval lies inside the limit on both sides. Containment is not "failed to exclude zero": a wide, uninformative interval fails containment and passes a significance test, which is exactly backwards for an instrument check. |
| **Operative floor** | For one exact cell, the larger of its absolute and comparative floor components. The components are never summed. A floor belongs to one cell and is never quoted from another. |
| **Resolution-qualified behavior** | A conclusion bounded by what one admitted measurement could resolve, rather than by physics. "Linear to no worse than one admitted bundle's timing half-width over the tested range" is a resolution-qualified statement; "linear" is not. |
| **Claim-anchored limb** | A criterion limb whose limit comes from an independently issued artifact rather than from the same data the criterion evaluates. Its purpose is that a degraded collection cannot enlarge its own allowed error. |
| **Publishable refusal** | A complete, authenticated result whose frozen criterion failed. It reports the failure. It never asserts equality, absence of effect, or instrument validity. |
| **Consequence if contradicted** | The sentence, frozen before collection, naming what the paper gives up if this criterion fails. A failed criterion with no pre-registered consequence is decorative. |
| **Claim ceiling** | The strongest wording a criterion's result may carry, paired with the exact stronger wording that stays forbidden. |
| **Eligible session** | A session admitted to the between-session row by a frozen predicate, never by an enumerated list. A predicate cannot be cherry-picked after outcomes are visible; a list can. |
| **Whole-window verdict** | The authenticated accept-or-refuse decision over a window's complete declared evidence, including membership and environmental conditions. |

## The two artifacts, and where the freeze lives

| Artifact | Schema name | When it exists | What it carries |
|---|---|---|---|
| `configs/campaigns/metrology_v1/characterization_result_schema_v1.json` | `joulewise.characterization_result_spec.v1` | Frozen before the first characterization member is measured | The row set, every criterion and its limit or derivation rule, the outcome map, the render map, token bindings, and the fingerprint of this contract |
| `<runs_root>/characterization_result_report.json` | `joulewise.characterization_result.v1` | Issued after collection | Realized values, per-criterion outcomes, per-row outcomes, refusals, and evidence bindings |
| This contract | `characterization-result-schema/v1` | Normative, no values | Definitions, outcome semantics, closed vocabularies, ordering gates, and the exact key structure of both artifacts |

The freeze is recorded by a successor plan that is predecessor-linked and
append-only, in the same form the campaign plans already use. Before the first
characterization bundle exists, that plan binds: both schema names, the
fingerprint of this contract and of the specification JSON, the exact
campaign-plan, order-manifest, condition-family, calibration-acceptance, and
analysis-source fingerprints, every required member role, the report renderer
revision, the exact results-fill-registry revision, and an assertion that no
historical artifact supplies any field. An updated method produces a new
predecessor-linked plan; it never rewrites the old one.
<!-- evidence: docs/paper/draft-v1.md:38 ("fixed" = exact bytes and fingerprint recorded before outcomes exist), :321-325 (append-only plans, predecessor links, estimator fingerprints) -->

Upgrading this freeze to a dedicated arm-readiness receipt kind is later
hardening, not part of this contract. The successor-plan form is executable
against the repository as it stands; the receipt-kind form is not, because the
characterization campaign directory carries none of the readiness namespaces
that machinery reads.

## Rows report; criteria decide

There are six public rows, fixed by their identifiers: `linearity`, `null`,
`empirical_floor`, `phase_attribution`, `drift_settling`, `between_sessions`.
No public row is added, renamed, or split. Those identifiers are load-bearing
in three places at once — the report template's row-render blocks, the
template lint that enforces each value token appears exactly once inside its
own row's present-branch, and the results-fill registry's draft-site rows — so
a change to them is a change to all three.
<!-- evidence: docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py:777-788 (row-to-token tuples); docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:2487-2543 (ROW_RENDER blocks); docs/paper/results-fill-registry.md:304-309 (DS-02..DS-07) -->

The granularity a reader needs comes from criteria, not from more rows. A row
whose two halves have different evidence and different failure meanings —
drift containment and recovery time, for instance — carries two criteria and
still renders as one row. Conjunctive aggregation is what makes this safe: a
row is `supported` only when every one of its criteria is `supported`, so a
pass on one half can never make the printed row look like a pass overall.

The timing-attribution property the paper's title, abstract, and discussion
all rest on is realized this way. It is not a seventh row; it is a set of
conjunctive subtests inside `phase_attribution`, each bound to a quantity the
harness already writes and a condition already committed in code. That costs
no new token, no template amendment, and no new number, and it makes the
paper's headline property a criterioned printed outcome rather than
discussion prose.

### Required fields per criterion

Every criterion in the specification carries exactly these keys. They are the
per-plan field set the analysis-plan contract already requires, narrowed to
what a characterization criterion needs.
<!-- evidence: docs/contracts/analysis_plans.md:17-36 (required analysis-plan fields) -->

| Key | Requirement |
|---|---|
| `criterion_id` | Stable identifier, unique within the specification. |
| `quantity` | The physical quantity being decided, named in words. |
| `units` | The unit that quantity is reported in. |
| `estimator` | The exact formula and the authenticated input field paths it reads. |
| `sample_unit` | Bundle, block, session, reference probe, or bracket capture. |
| `minimum_n` | The evidence count below which the criterion returns `indeterminate` rather than a decision. |
| `decision_rule` | The comparison, stated so that substituting values reproduces the outcome with no further judgment. |
| `limit` or `derivation_rule` | Exactly one of the two: a literal, or the rule that resolves to one at freeze time. |
| `limit_basis` | `ruled`, `derived`, or `ed_input_required`. |
| `limit_basis_source` | Where a `ruled` value or a `derived` rule comes from: the exact artifact and location. |
| `evidence_binding` | Parent role, artifact path or path pattern, and exact field path for every input. Fingerprints are recorded in the issued report, not here, because the artifacts do not exist yet. |
| `failure_outcome` | The row outcome a failure of this criterion produces: `contradicted` when the criterion was genuinely tested, `indeterminate` when a failure means the test was not built rather than not met. |
| `reason_code_on_failure` | The single `characterization_*` code this criterion emits when it fails. |
| `reason_code_on_limit_unavailable` | Claim-anchored limbs only: the code emitted when the limb's independently issued supplier does not exist, which is a different event from the criterion failing. |
| `consequence_if_contradicted` | The frozen sentence naming what a failure costs the paper. |
| `claim_ceiling` | The strongest permitted wording, with the exact forbidden upgrade. |

`failure_outcome` is the field that stops a false refusal. A deliberately
sized probe that lands in the wrong place, or a registered workload level that
is simply absent, has not shown that the instrument failed its criterion; it
has shown that the criterion was never put to the test. Those criteria carry
`failure_outcome: "indeterminate"` and can never print the contradicted
phrase. A criterion that was fully evaluated on complete evidence carries
`failure_outcome: "contradicted"`.

Two criteria on the same fit may be *limbs* of one property: a **resolution
limb** whose limit is derived from the same measurements it tests, and a
**claim-anchored limb** whose limit comes from a separately issued artifact.
Both are always registered. The resolution limb is always computable, which is
why it exists; on its own it cannot fail for instrument-quality reasons,
because a sloppier collection widens its own allowed residual. The
claim-anchored limb fixes that, but is only available when the artifact it
anchors to has been issued. When it is not available the row returns
`indeterminate` with the named reason code; the limb is never silently
dropped.

## Prospectively frozen conditional branches

A criterion may depend on something not yet known at freeze time — most often
whether a suitable independently issued floor exists when the window is
funded. Choosing between designs *after* seeing that is a selection made with
outcomes partly visible. The schema handles it the only way that stays fixed
before collection: both branches are written out in full, and a predicate
fixed before collection decides which one activates.

The identical-condition null row is the case that needs this. Its comparator
should be an independently issued floor from a prior window, because that
floor was built from evidence disjoint from the blocks being tested. If no
such floor has been issued when the characterization window is frozen, the
row instead splits its own blocks into a comparator-building half and a
held-out testing half, which restores independence at the cost of a weaker
comparator built from fewer blocks. The specification names the predicate,
both branches, the block roles in each, and which branch is primary; the
report records which branch actually activated.

## Outcome architecture: four independent layers

Each layer answers a different question and has its own closed vocabulary. A
report carries all four for every row.

### Row outcome — what the reader is told

`row_outcome` is closed: `supported`, `indeterminate`, `contradicted`,
`pending_eligibility`.

| Value | Meaning |
|---|---|
| `supported` | Every criterion in the row met its limit on complete, authenticated evidence. |
| `indeterminate` | The evidence is authentic and complete but a decision is not reachable: evidence count below the registered minimum, an interval straddling the limit, a probe that missed its intended size, or a required limit supplier not issued. |
| `contradicted` | A criterion was evaluated on complete, authenticated evidence and failed. This is a published result, not an error. |
| `pending_eligibility` | `between_sessions` only: fewer eligible sessions exist than the registered minimum. |

`protocol_incomplete` is not a member. It is the outcome the paper currently
records as the only permitted one, precisely because no frozen schema existed;
freezing the schema retires it. If the report writer would emit it, the writer
refuses to issue the report instead. A `protocol_incomplete` row inside an
issued report is a schema violation, never a result.
<!-- evidence: docs/paper/draft-v1.md:331 ("its only permitted outcome is 'protocol incomplete'") -->

### Publication class — what may be done with the row

`publication_class` is closed: `RESULT`, `PUBLISHABLE_REFUSAL`,
`DIAGNOSTIC_ONLY`, `PROTOCOL_INCOMPLETE`.

The mapping from row outcome is total and fixed: `supported` maps to `RESULT`;
`contradicted` maps to `PUBLISHABLE_REFUSAL`; `indeterminate` and
`pending_eligibility` map to `DIAGNOSTIC_ONLY`. `PROTOCOL_INCOMPLETE` is
unreachable in an issued report for the same reason `protocol_incomplete` is.

### Failure class — what kind of failure it was

`failure_class` is closed and is present only when the row is not `supported`.

| Value | Meaning |
|---|---|
| `CRITERION_NOT_MET` | The criterion was evaluated on complete evidence and the inequality failed. |
| `EVIDENCE_REFUSAL` | An upstream verdict, admission, or custody check refused the evidence. |
| `MISSING_REQUIRED_BINDING` | A required artifact, field path, or fingerprint was absent. |
| `SCHEMA_PIN_MISMATCH` | The report's schema or specification fingerprint differs from the frozen pins. |
| `PROTOCOL_INCOMPLETE` | Reserved; unreachable in an issued report. |

### Reason code — the exact named cause

`reason_code` draws from the closed `characterization_*` vocabulary in the
next section. It is deliberately disjoint from the readiness and
historical-semantics vocabularies: no coincidental refusal from another
subsystem substitutes for a required characterization refusal, and no
characterization code is ever emitted by another subsystem. This is the same
discipline the historical-semantics verifier already carries for its own
vocabulary.
<!-- evidence: docs/contracts/receipt_histsem_verifier.md:103-131 (closed histsem_* vocabulary disjoint from READINESS_REASON_CODES; "no coincidental downstream readiness_* refusal substitutes") -->

The readiness council's own verdict words — `READY`, `NOT_READY`,
`UNVERIFIED` — are reserved to that council and must not appear as
characterization outcomes. They run in the opposite time direction (a
pre-window judgment about whether to collect, not a post-collection result),
they are decided by a different body, and they have no mapping onto the report
template's closed reader-facing phrases.
<!-- evidence: docs/process/instrument-readiness-audit-charter.md:79-91 (per-component READY / NOT-READY / UNVERIFIED, council decider) -->

### Aggregation and precedence

Within a row, precedence is `contradicted` before `indeterminate` before
`supported`. A known failure must never hide behind an unreached decision.
`between_sessions` short-circuits to `pending_eligibility` when its eligible
session count is below the registered minimum, before any other criterion is
evaluated.

## Render map

`row_outcome` maps totally onto the report template's four closed
reader-facing phrases. The template permits no other phrase, and the machine
enum values must never reach a reader.
<!-- evidence: docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:258-263 (the four permitted predicate phrases) -->

| `row_outcome` | Rendered phrase |
|---|---|
| `supported` | "supported the registered behavior" |
| `indeterminate` | "did not support a conclusion under the registered criterion" |
| `contradicted` | "showed that the registered expected behavior did not hold" |
| `pending_eligibility` | "remains pending because fewer than three eligible sessions are available" |

The last phrase is available to `between_sessions` alone. The specification's
render map binds each row identifier to its plain-language token and to its
value tokens; the identifier spellings differ between the row set and the
token names, so the crosswalk is written out in the specification rather than
inferred.

The report template prints one residual limit and one invariance band, while a
dual-limb criterion has two. The printed value is the **binding** limb — the
stricter of the two when both are available, the sole available limb
otherwise — and the rule producing it is written into the specification's
`derived_value_rules`, never inferred by the renderer. Both limbs remain
separately reported per criterion, so nothing is hidden by printing the
binding one.

## Refusal vocabulary

Characterization refusals use the closed `characterization_*` vocabulary,
disjoint from `READINESS_REASON_CODES` and from `histsem_*`. Every member is
listed; an unlisted code stops rendering rather than being passed through.

| Code | Meaning |
|---|---|
| `characterization_attribution_terms_composed` | A shared session term and a per-member term were reported as one combined range instead of separately. |
| `characterization_bracket_capture_absent` | A required calibration bracket capture or its bound is missing. |
| `characterization_cadence_or_sample_fidelity_flagged` | A claim-bearing member carries the sampling-cadence or in-window-sample-count flag. |
| `characterization_change_check_failed` | A session's revalidation record shows a new quality, cooldown, sampling, or manifest change. |
| `characterization_criteria_not_prior` | The frozen criteria were issued at or after the first admitted member's capture time. |
| `characterization_criterion_not_met` | The criterion was fully evaluated on complete, authenticated evidence and its inequality failed. This is the ordinary code behind a published refusal. |
| `characterization_effect_sizing_missed` | A deliberately sized probe landed outside its registered tolerance around the predicted effect, so the gate was not the thing tested. |
| `characterization_eligible_sessions_insufficient` | Fewer eligible sessions exist than the registered minimum. |
| `characterization_estimator_undefined` | The estimator cannot be evaluated on the admitted evidence. |
| `characterization_evidence_binding_absent` | A required artifact path, parent role, or field path is missing. |
| `characterization_evidence_digest_mismatch` | A recomputed evidence fingerprint differs from the bound value. |
| `characterization_floor_pair_not_disjoint` | A criterion's comparator floor was derived from evidence that overlaps the evidence it is testing. |
| `characterization_gap_evidence_absent` | The retained trace data needed to bound an unphased gap is missing. |
| `characterization_heldout_reference_absent` | A required held-out reference probe is missing, or a probe used to build an allowance was also used to test it. |
| `characterization_identity_mismatch` | A session's stack identity or capture-method era differs from the reference session. |
| `characterization_level_absent` | A registered workload level, magnitude, shape, or target is missing from the admitted evidence. |
| `characterization_level_membership_insufficient` | A registered level is present but its admitted count is below the registered minimum. |
| `characterization_magnitude_absent` | A registered workload magnitude of the identical-condition ladder is missing from the admitted evidence. |
| `characterization_limit_supplier_not_prior` | A derived limit's supplier artifact does not carry a strictly earlier freeze ordinal. |
| `characterization_limit_unratified` | A criterion whose limit basis requires ratification was evaluated before that ratification exists. |
| `characterization_operative_floor_unavailable` | A claim-anchored limb has no issued same-cell operative floor to anchor to. |
| `characterization_quarter_window_flagged` | A claim-bearing member carries the flag for a clock bound exceeding a quarter of its window duration. |
| `characterization_recovery_record_absent` | A required cooldown-exit record for a disturbance sequence is missing. |
| `characterization_reference_role_unfrozen` | A reference member's allowance-constructing or held-out role was not fixed at pack generation. |
| `characterization_schema_pin_mismatch` | The report's schema or specification fingerprint differs from the frozen pins. |
| `characterization_slope_supplier_unavailable` | A criterion consuming an externally fixed slope has no issued supplier artifact for it. |
| `characterization_target_unrealizable` | A registered target cannot be generated: a non-positive slope, an increment below one token, or a configuration outside the frozen context limit. |
| `characterization_whole_window_verdict_unissued` | The governing whole-window verdict has not been issued. |
| `characterization_writer_refused_issuance` | The report writer refused to issue rather than emit an unreachable outcome. |

## The two writer ordering gates

One program issues the report. It recomputes every fingerprint itself and
rejects any input field that tries to select its own estimator or its own
limit. Before it evaluates anything, it applies two gates. Both are pure
timestamp and ordinal comparisons over artifacts that already exist; neither
needs new machinery.

**`characterization_criteria_not_prior`.** The writer refuses unless the
freeze record's issue time strictly precedes the capture time of every
admitted member. This is the gate that makes "fixed before collection"
checkable rather than promised.

**`characterization_limit_supplier_not_prior`.** The writer refuses unless
every derived limit's supplier artifact carries a strictly earlier freeze
ordinal than the characterization freeze. This is the gate that would have
refused the same-day criterion change described at the top of this contract:
the supplier and the criterion were fixed on the day the data arrived, which
is not earlier.

A refusal from either gate is protocol failure, not a result. The writer emits
no report.

## Anti-selection rule

A characterization window that fails its whole-window verdict may legitimately
be re-collected; that is an environmental outcome, not a scientific one. A
`contradicted` row inside a window that *passed* its verdict does not license
re-collection to reverse it.

Any successor characterization window carries an explicit predecessor link,
and both reports publish. The paper reports the sequence, never the more
favorable member of it. The existing abandon-after-three rule covers repeated
environmental interruption and does not reach this case.
<!-- evidence: docs/paper/draft-v1.md:317 (abandon-after-three), :326 (a report where every row is supported still publishes its refusal log) -->

A report in which every row is `supported` still publishes its refusal log.

## Multiplicity registration

Most criteria here are deterministic bound comparisons: a fixed quantity
against a fixed limit, with no sampling distribution and therefore no
false-positive rate to correct. Correcting them would be arithmetic theatre.

The family is registered with an exploratory claim role and the explicit
wording that it carries no confirmatory inference — a formulation the
analysis-plan contract permits by name. Within it, the criteria that *are*
inferential, because they decide by whether a composed interval lies inside a
band, form a small confirmatory subfamily corrected by the Holm procedure. The
specification enumerates that subfamily's exact membership and its Holm
denominator; this contract does not, because that denominator is a value.
<!-- evidence: docs/contracts/analysis_plans.md:24 (multiplicity_rule field, "explicitly exploratory/no confirmatory inference"), :46-67 (frozen registry, Holm within family) -->

Every row carries a claim ceiling in instrument-result language, with the same
exact forbidden upgrade: no characterization row may be quoted as a scientific
finding about models, hardware, or workloads.

## Failed-row publication form

Every row whose publication class is `PUBLISHABLE_REFUSAL` is published in
exactly this form. It is normative, not illustrative.

```markdown
### Characterization refusal — [C# / property]

Outcome: NOT_READY — PUBLISHABLE_REFUSAL
What was tested: [one-sentence frozen estimand and stack identity]
Why it cannot support the stated result: [failure_class; exact failed predicate]
Observed, authenticated diagnostic:
- Estimator: [estimator_id and formula]
- Value and unit: [observed statistic]
- Frozen comparator: [number or exact derivation rule]
- Required basis: [planned / admitted / present counts]
- Result: [inequality with substituted values]

Custody:
- Issued characterization report: [path, SHA-256, row JSON pointer]
- Whole-window verdict: [path, SHA-256, status, source refusal codes]
- Input manifest: [path, SHA-256]
- Frozen schema and plan: [paths, SHA-256]

Interpretation limit:
This refusal does not show no effect, equality, or instrument validity outside the
named stack and conditions. It shows that this implementation could not support
the named characterization conclusion from this frozen basis.
```

Two notes bind the form to the vocabularies above. The `Outcome:` line's
leading word is the seat design's original readiness spelling and is retained
verbatim as the ruling adopted it; the machine-readable outcome for the same
row is the `row_outcome` value `contradicted` with `publication_class`
`PUBLISHABLE_REFUSAL`, and the reader-facing sentence is the render map's
third phrase. Raw source refusal codes from upstream subsystems are preserved
verbatim inside the form; an unrecognized code stops rendering until it is
explicitly registered.
<!-- evidence: docs/paper/results-fill-registry.md:153-171 (fail-closed handling of unknown reason codes); form adopted verbatim from docs/process_traces/2026-08-24-p06-codesign/02-seat-b-design.md §4 per ruling item 11 -->

The `Interpretation limit:` paragraph is mandatory and is never shortened. It
is what keeps a published refusal from being read as a finding of equality.

## Exact schema

Every object below is exact-key: an unlisted key refuses, and a missing key
refuses. Integers reject booleans. Digests are sixty-four lowercase
hexadecimal characters. Enumerated fields accept only the members listed
earlier in this contract. Placeholders in angle brackets stand for values;
no value appears in this document.

### Frozen specification

```json
{
  "anti_selection": {
    "predecessor_link_required": "<boolean>",
    "rule": "<statement>"
  },
  "c2_floor_mode": {
    "activation_predicate": "<predicate deciding the mode at freeze time>",
    "modes": {
      "<mode name>": {
        "block_roles": {"<role>": "<count>"},
        "comparator": "<what the null is tested against>",
        "rationale": "<why this mode is primary or conditional>"
      }
    },
    "selected_at_freeze": "<mode name or null before freeze>"
  },
  "characterization_family": {
    "alpha": "<family error rate>",
    "claim_role": "exploratory",
    "exact_forbidden_upgrade": "<the forbidden stronger wording>",
    "family_id": "<stable family identifier>",
    "inferential_subfamily": ["<criterion_id>", "<criterion_id>"],
    "inferential_subfamily_note": "<how the denominator counts its members>",
    "multiplicity_denominator": "<positive integer>",
    "multiplicity_rule": "<named rule>"
  },
  "contract": {
    "path": "docs/contracts/characterization_result_schema_v1.md",
    "schema_version": "characterization-result-schema/v1",
    "sha256": "<digest of this contract's exact bytes>"
  },
  "ed_input_ledger": [
    {
      "blocked_on": "ED-INPUT",
      "blocks": ["<criterion_id>"],
      "item": "<name of the missing value>",
      "ledger_text": "<the ruling's sentence for this item>"
    }
  ],
  "ordering_gates": {
    "<gate name>": {
      "predicate": "<statement>",
      "refusal_code": "<characterization_* member>"
    }
  },
  "render_map": {
    "derived_value_rules": {"<report field path>": "<rule producing it>"},
    "outcome_phrases": {
      "contradicted": "<template phrase>",
      "indeterminate": "<template phrase>",
      "pending_eligibility": "<template phrase>",
      "supported": "<template phrase>"
    },
    "phrase_source": "<where the closed phrase set is fixed>",
    "publication_class_from_row_outcome": {"<row_outcome>": "<publication_class>"},
    "rows": {
      "<row_id>": {
        "diagnostic_presence_atom": "<selector atom name>",
        "diagnostic_tokens": {"<token>": "<report field path>"},
        "plain_language_token": "<token>",
        "value_tokens": {"<token>": "<report field path>"}
      }
    },
    "selector_atoms": {"<atom name>": "<condition it evaluates>"}
  },
  "rows": [
    {
      "criteria": [
        {
          "blocked_on": "<present only when limit_basis is ed_input_required>",
          "claim_ceiling": {
            "exact_forbidden_upgrade": "<forbidden wording>",
            "permitted": "<strongest permitted wording>"
          },
          "consequence_if_contradicted": "<frozen sentence>",
          "criterion_id": "<identifier>",
          "decision_rule": "<comparison>",
          "derivation_rule": "<rule resolving to a limit at freeze time>",
          "estimator": {
            "formula": "<formula>",
            "inputs": [{"field_path": "<path>", "role": "<role>"}]
          },
          "evidence_binding": [
            {
              "field_path": "<path>",
              "parent_role": "<role>",
              "path": "<artifact path or path pattern>"
            }
          ],
          "failure_outcome": "<contradicted | indeterminate>",
          "ledger_text": "<present only when limit_basis is ed_input_required>",
          "limit": "<literal>",
          "limit_basis": "<ruled | derived | ed_input_required>",
          "limit_basis_source": "<exact artifact and location>",
          "minimum_n": "<nonnegative integer>",
          "quantity": "<quantity in words>",
          "reason_code_on_failure": "<characterization_* member>",
          "reason_code_on_limit_unavailable": "<claim-anchored limbs only>",
          "sample_unit": "<unit>",
          "units": "<unit>"
        }
      ],
      "eligibility_predicate": "<present only on the between-session row>",
      "registered_directions": ["<present only on the small-difference row>"],
      "registered_targets": [
        {
          "expectation": "<prewritten gate outcome, or none>",
          "ratio_of_floor": "<multiple of the published floor>",
          "rounding": "<floor | ceil, always away from the gate boundary>"
        }
      ],
      "row_id": "<one of the six row identifiers>",
      "row_label": "<short label used in the paper>",
      "supplying_campaign": "<campaign directory supplying this row's members>",
      "table_property": "<the paper table's property name>"
    }
  ],
  "schema_version": "joulewise.characterization_result_spec.v1",
  "spec_id": "<stable specification identifier>"
}
```

A criterion carries exactly one of `limit` and `derivation_rule`; carrying
both, or neither, refuses. A criterion whose `limit_basis` is
`ed_input_required` carries `blocked_on` and `ledger_text` in place of a
value, and appears in `ed_input_ledger`. The freeze refuses while any such
criterion remains unratified; nothing else is blocked by it, and every other
criterion may be frozen independently.

### Issued report

```json
{
  "characterization_family": {
    "family_id": "<matches the specification>",
    "holm_decisions": [
      {
        "adjusted_comparison": "<comparison performed>",
        "criterion_id": "<identifier>",
        "passed": "<boolean>"
      }
    ]
  },
  "predecessor": {
    "path": "<prior characterization report path or null>",
    "sha256": "<digest or null>"
  },
  "refusal_log": [
    {
      "criterion_id": "<identifier or null>",
      "raw_source_code": "<verbatim upstream code or null>",
      "reason_code": "<characterization_* member>",
      "row_id": "<row identifier or null>"
    }
  ],
  "report_sha256": "<digest of this report's exact bytes>",
  "rows": [
    {
      "criteria": [
        {
          "consequence_if_contradicted": "<verbatim from the specification>",
          "criterion_id": "<identifier>",
          "criterion_outcome": "<supported | indeterminate | contradicted>",
          "evidence_binding": [
            {
              "field_path": "<path>",
              "parent_role": "<role>",
              "path": "<artifact path>",
              "sha256": "<recomputed digest>"
            }
          ],
          "limit_applied": "<resolved literal>",
          "limit_basis": "<ruled | derived>",
          "n_admitted": "<nonnegative integer>",
          "n_planned": "<nonnegative integer>",
          "observed_value": "<realized statistic>",
          "reason_code": "<characterization_* member or null>",
          "substituted_inequality": "<the comparison with values substituted>"
        }
      ],
      "diagnostic_present": "<boolean>",
      "diagnostics": {"<name>": "<value>"},
      "failure_class": "<closed member or null>",
      "observed_values": {"<name>": "<value>"},
      "publication_class": "<RESULT | PUBLISHABLE_REFUSAL | DIAGNOSTIC_ONLY>",
      "reason_code": "<characterization_* member or null>",
      "row_id": "<one of the six row identifiers>",
      "row_outcome": "<supported | indeterminate | contradicted | pending_eligibility>"
    }
  ],
  "schema_version": "joulewise.characterization_result.v1",
  "spec": {
    "path": "configs/campaigns/metrology_v1/characterization_result_schema_v1.json",
    "schema_version": "joulewise.characterization_result_spec.v1",
    "sha256": "<digest of the frozen specification>"
  },
  "stack_identity": {"<field>": "<value>", "sha256": "<digest>"},
  "whole_window_verdict": {
    "conditions": ["<condition>"],
    "member_failures": ["<failure>"],
    "path": "<verdict path>",
    "sha256": "<digest>",
    "status": "<verdict status>"
  }
}
```

`sessions_excluded` appears inside the `between_sessions` row's
`observed_values` as a list of session identifiers each paired with its
exclusion reason. Exclusions are always visible; a shorter eligible set with
no stated reasons refuses.

Both documents use the project's canonical JSON form: UTF-8, duplicate-key
refusal, finite values only, lexicographically sorted object keys, two-space
indent, and one trailing newline.
<!-- evidence: docs/contracts/d117_step6_confirmation_table.md ("Encoding and sidecar": strict canonical JSON) -->

## Domain owners

Every issued field names the authority that recomputes it. No subsystem may
copy another domain's facts and thereby replace that domain as authority. A
report cell that disagrees with its owner is a refusal, not a correction.

| Issued field | Authoritative verification source |
|---|---|
| `rows[].criteria[].observed_value` | Fresh evaluation of the criterion's frozen estimator over the authenticated admitted members, recomputed by the report writer from the bound field paths; the report cell is checked as a cache |
| `rows[].criteria[].limit_applied` | For `ruled` limits, the frozen specification literal; for `derived` limits, fresh evaluation of the frozen derivation rule over the supplier artifact named in `evidence_binding`, which must carry a strictly earlier freeze ordinal |
| `rows[].criteria[].n_admitted`, `n_planned` | The campaign order manifest and the whole-window verdict's complete covered membership; a count reported by any analysis file is a cache |
| `rows[].criteria[].criterion_outcome` | Fresh evaluation of the frozen `decision_rule` against the freshly computed observed value and applied limit |
| `rows[].criteria[].substituted_inequality` | Rendered from the freshly computed observed value and applied limit, never supplied |
| `rows[].criteria[].consequence_if_contradicted` | Byte-equal copy of the frozen specification sentence; any difference refuses |
| `rows[].row_outcome` | Fresh conjunctive aggregation over the row's criterion outcomes under the precedence rule, with the between-session short-circuit applied first |
| `rows[].publication_class` | Fresh application of the total map from `row_outcome`; never supplied independently |
| `rows[].failure_class`, `rows[].reason_code` | The report writer's own refusal path; an upstream code is preserved verbatim in `refusal_log[].raw_source_code` and never substituted for a characterization code |
| `rows[].diagnostic_present`, `rows[].diagnostics` | Presence and value recomputed from the bound authenticated fields; absence renders nothing and is never treated as zero |
| Floor values consumed as limits | The issuing floor artifact's own mint path, recomputed from its authenticated members, widths, semantics, and window allowances; the operative floor is a fresh maximum of the absolute and comparative components |
| Cooldown-exit and admission observations | The controller's recorded per-attempt cooldown notes and the admission predicate's own evaluation, read from the experiment manifest; never re-derived from prose |
| Calibration bracket bounds and their acceptance band | The issued calibration-acceptance edition named by the supplied acceptance file, looked up by edition identifier rather than remembered |
| Member quality flags | The reduction program's own committed flag computation over each member's stored geometry; the report counts them and never recomputes the flag itself |
| `stack_identity` | The bundle-recorded identity fields and the whole-window verdict's identity check |
| `whole_window_verdict` | The issued verdict artifact; the report's copy is a cross-check, never the authority |
| `spec.sha256`, `contract.sha256`, `report_sha256` | Recomputation over the exact bytes at the named path |

## What this contract does not do

It does not authorize collection. It does not select a window. It does not
convert any retained historical diagnostic into a supplier: historical
evidence remains explicitly diagnostic and supplies no criterion, no limit,
and no reported value.
<!-- evidence: docs/paper/results-fill-registry.md:20-24 (no historical result is a supplier) -->

It does not create a new claim about models, hardware, or workloads. Every row
here is a statement about the instrument, and the claim ceiling on every row
says so.
