# S5 MINT IMPLEMENTATION CONTRACT — RATIFIED (magistrate, 2026-07-28)

Design consult (Sol xhigh, thread 019fab60-0715-70d0-85de-bdac139bc478)
adjudicated: ACCEPTED IN FULL, including its three DISAGREEs with the
draft brief. This file supersedes s5-mint-brief-draft.md as the
implementation contract. Pinned facts from the draft brief remain valid
(pre-registration numbers, basis digests, GO adjudications).

## Implementation ORDER (ratified; do not resequence)
1. W10 — SCHEMA_VERSION → "joulewise.detection_floor_artifact.v2".
   METHOD_ID / TRANSPORT_RULE_ID / SINGLE_COUNT_DISCIPLINE_ID unchanged.
   NO v1 writer, NO migration arm (no v1 artifact ever persisted);
   validator rejects v1 after the bump.
2. W8 — public FLOOR_METRIC_CATALOG in detection_floor.py, imported by
   floor_extraction.py; NINE entries: gross_energy_j, energy_request_j,
   idle_subtracted_energy_j, phase_energy_j.{tokenize, prefill, decode,
   serialize, transfer, deserialize}. One shared metric/window-class
   validator used by validate_floor_artifact AND governed_cell_metric;
   remove extractor's open-ended phase_energy_j.<suffix> acceptance.
   EXCLUDE split_total_energy_j and idle/warmup/cleanup/failure.
3. W3 — cross-window cell schema + COMPONENT-SCOPED PROVENANCE
   (rules below).
4. Q4 — width closure: non-defaulting width args on estimator ctors;
   _admissible_widths rejects None; builders reject empty/wrong-length
   widths, lose the (0.0,)*n fallback; mint compares widths
   element-for-element against the authenticated extraction-report row.
   zero_widths_authenticated REJECTED as a mechanism. Dead-gate pin:
   guarded estimate ⇒ both corner fields present AND guarded ==
   guard_factor * unguarded; smoke ⇒ corner unguarded present, guarded
   null; any other pairing ValueError; builders use corner fields with
   no `is not None` branch.
5. W2 — subset plumbing: evaluation_basis_sha256 through extract_cells →
   AuthenticatedConsumptionSession → whole_window_refusal_reasons AND
   whole_window_drift_allowances call sites (floor_extraction.py:1137,
   :1201); CLI --evaluation-basis-sha256. Caution: whole_window.py
   :4028-4035 requires consistent threading everywhere or it refuses.
6. W4/W5 — author condition_family_definition + extraction specs.
   Definition schema joulewise.condition_family_definition.v1:
   {condition_family_id: "df-ph-decode", workload profile df_ph_decode
   (128 prompt / 512 output tokens, 1 repetition, 1 warmup), measurement
   target phase_energy_j.decode @ window_class phase, comparison_policy
   "same_condition_repeat_and_null_abba_alias", abba_alias_relation
   "A_equals_B"}. Validation: inner id/metric/window-class must equal
   the cell key; A and B members resolve to the SAME definition hash.
   Specs: a10 (30 members, 3 abs cells) + C (40 members, decode ABBA).
7. W6 — scripts/mint_floor_artifact.py per the binder + gate rules below.
8. W7 — gauntlet regressions RIDE EACH SCHEMA CHANGE (not batched at
   the end).

## W3 cross-window rules (verbatim-adopted)
Component-local records; NO shared window object. absolute and
comparative each carry: own whole_window_evaluation_basis_sha256,
consumption_semantics_id, whole_window_drift_allowance (embedded basis
sha must match ITS component), drift_widened_{unguarded,guarded}_floor_j.
provenance gains per-component blocks (absolute/comparative), each:
calibration_cell_id, evidence_root_id ("a10"/"window_c"), hash-pinned
order_manifest, campaign_log, extraction_report, extraction_spec,
bundle_ids + bundle_sha256s, source_regime.
1. claim_ready requires both components.
2. Within component: all-or-none group (basis sha, semantics id,
   allowance, both drift-widened floors).
3. RELAX cross-component equality of: basis sha, drift allowance,
   consumption_semantics_id.
4. DO NOT relax within-component basis-sha consistency.
5. consumption_semantics_id REQUIRED in v2; enum exactly
   {"d078_minted_envelopes_v1",
   "d078_authenticated_max_bracket_rederivation_v1"}; authenticated
   legacy ABSENCE normalizes to d078_minted_envelopes_v1 at ingestion
   ONLY; v2 never serializes null/absence.
6. allowance claim_family must match metric-derived family.
7. Recompute per component: drift_widened_guarded_floor_j ==
   corner_widened_guarded_floor_j + allowance_j.
8. floor_gate_j = max(absolute.drift_widened_guarded_floor_j,
   comparative.drift_widened_guarded_floor_j). NEVER sum allowances;
   NEVER re-add an allowance at cell or transport-group level.
9. Provenance bundle sequences positionally equal bundle_observations
   (abs) / flattened A1/B1/B2/A2 (cmp); component member sets DISJOINT
   for mint #1.
10. DO NOT relax shared cell invariants: backend, metric, window class,
    condition_family (id+definition+hash), calibration-plan SHA,
    scientific-config identity, stack identity, measurement boundary,
    minimum counts, ABBA A==B null identity.
11. Both component stack hashes == cell stack hash; cell stress_observed
    = componentwise conservative composition (minima on
    _ENVELOPE_MIN_FIELDS, maxima on _ENVELOPE_MAX_FIELDS, fail-closed
    bound-term composition).
12. single_count_discipline unchanged at every propagation point.

## Q2 scope (ratified)
Artifact-level calibration_scope = "production_window" (add to enum;
window_a / window_b_revalidation retained as historical). Plan's
historical declaration kept in provenance as calibration_plan:
{plan_id, declared_calibration_scope: "window_a", relative_path,
sha256: e529a0624b7618edaade511dd610ae0837f31de299dde642a055974c382681ab
(LEAD-VERIFIED against file bytes + sidecar 2026-07-28)}. Binder
verifies declared scope against pinned plan bytes; MUST NOT require
artifact scope == plan-declared scope.

## Q3 (ratified)
source_class = "prospective" for mint #1; build_floor_artifact
source_class becomes NON-DEFAULTING. (Closes review C2-residual too.)

## W6 mint tool shape (ratified)
- Multi-root evidence binding: bind_floor_artifact_evidence(artifact,
  floor_path, evidence_roots: Mapping[str, Path], *, strict_validator);
  roots resolved via evidence_root_id; NO absolute paths persisted;
  every relative_path validated safe-relative POSIX.
- Mint rebinds admitted members to source bytes, derives stack/regime
  from evidence (NOT report-only), verifies report widths + membership
  before builder calls.
- Transport: one cell cell_id "df-ph-decode-floor", one group
  transport_group_id "tg-df-ph-decode-production-v1", sole family the
  exact hashed df-ph-decode; group consumes the composed cross-window
  cell (never one window's regime).
- PRE-REGISTRATION GATE placement: after report/spec/source-byte
  authentication, BEFORE any builder call. Hard-fail unless: plan SHA
  e529a062…681ab; bases equal pinned digests
  a10 79c6e8b9211f18a5ad8937f155230a9090706bf1dfc8c3ed767deb53074e053e
  (37 members) and C
  0cf07a5cdc3847e67ba9be9dc50ffda43b7d00ef10d03485faf36c2693418fa6
  (47 members); memberships 30/37 and 40/47; abs n==10, cmp
  n_blocks==10; C is A==B null; a10 allowance 0.652271753365838 within
  1e-12; window-C comparative allowance 0.5812720449734456 within
  1e-12; formatted operative floor exactly "7.377086" at six decimals.
  Composed operative floor: absolute component 3.592138 J, comparative
  component 7.377086 J, composed gate = max(absolute, comparative) =
  7.377086 J (rule 8 composition; NEVER summed). **SUPERSESSION NOTE:**
  the previous "3.592138" pin was the ABSOLUTE COMPONENT IN ISOLATION,
  from D-079 clause 5's canonical operative floors recorded before
  window C's comparative floor had been extracted. Under W3 rule 8 the
  cell gate is the max, so those two clauses as previously written were
  jointly unsatisfiable. Amended per Ed's ratification 2026-07-29; both
  components remain published and LABELLED. The re-pinned literal
  "7.377086" is INDEPENDENTLY LEAD-VERIFIED, recomputed bit-exact from
  primary corpus bytes independently of the extraction pipeline; it MUST
  remain a hard six-decimal literal, never parameterized from or derived
  from any extraction report inside the mint path. Diagnostic floors
  carry published_claim_floor: false; width arrays exactly equal the
  reports. Post-construction: re-assert headline vs floor_gate_j;
  validate_floor_artifact(artifact) == []; exclusive output creation
  (no overwrite).
- Single-count prose statement renders FROM the artifact's canonical
  single_count_discipline object (sidecar convenience only).
- Manifest id pins (lead-verified): p2-015-02_phase_absolute-order-v1,
  p2-015-05_phase_decode_abba-order-v1.

## Gauntlet additions (ratified; ride their schema changes)
Swapped component bases; copied allowances; missing/unknown semantics
id; missing evidence-root mapping; swapped order manifests;
one-root-only regime construction; width substitution; A/B definition
divergence; accidental artifact-scope==plan-scope enforcement.

## Notes
- Baseline for the implementation branch: MERGED main (post PR #87 —
  contains hardening + E4 + D-079 text; consult's "missing D-079"
  process flag was worktree staleness, resolved by the merge).
- CAL-REBRACKET semantics: enum literal
  d078_authenticated_max_bracket_rederivation_v1 exists for the a10
  max-bracket re-reduction path; implementation must confirm which
  semantics id the a10 consumption ACTUALLY carries at extraction time
  and normalize per rule 5 — do not guess.
- Review debts folded here: C1 (via Q4), C3/E3 (via W8), SCHEMA_VERSION
  ruling (via W10).
