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

## D-117 postcollection trust amendment (2026-08-07)

This amendment governs the generalized v2 mint and supersedes the W6 sentence
that treated postcollection calculation inside the mint as forbidden. The
narrowed binding rule is: **the mint calculates the expected verification
projection from authenticated source evidence and compares the independently
frozen pins against that projection; it never invents, selects, defaults, or
fills a missing pin.** A pin is an expected value, not evidence.

There is no mint-owned postcollection certificate. In particular,
`floor_mint_postcollection` has no producer and is not part of the extraction
wire. Its presence in a D-117 report is an unknown-top-level-key refusal.

### Domain owners

| Frozen postcollection pin | Authoritative verification source |
|---|---|
| Pre/post receipt digests | Verdict-owned bracket endpoints cross-checked against the finalized observations returned by `validate_calibration_bracket_binding` over the authenticated ledger snapshot |
| Pre/post content digests | Verdict-owned endpoint content IDs cross-checked against receipt-bound ledger observation content IDs, which the ledger subsystem recomputes from calibration artifacts |
| Bracket-binding SHA | SHA-256 of the exact supplied binding bytes plus a session/window/endpoint cross-check against the authenticated verdict bracket and complete validation against the ledger |
| Terminal ledger head | Git-committed head pin and authenticated ledger snapshot; the binding copy is only a cross-check |
| Observed drift | Exact-Decimal absolute difference between authenticated pre/post bound lexemes |
| Allowance rule, screen, applied allowance, embedding count | Exact code-pinned issued D-079 acceptance artifact and its authenticated rule; applied allowance is `max(observed, accepted screen)` and the count is exactly one |
| Evaluation-basis SHA and member count | Authenticated whole-window verdict/evaluation basis and its complete covered membership |
| Extraction-report SHA | SHA-256 of the exact report bytes; it binds file identity but is not proof of operator honesty |
| Absolute/comparative floors | Fresh estimator calculation from authenticated members, widths, semantics, and whole-window allowances; the corresponding report cells are checked as caches |
| Operative floor | Fresh `max(absolute, comparative)` calculation |
| Six-decimal strings | `.6f` rendering recomputed from verified full-precision values and compared to the frozen literals |

No subsystem may copy another domain's facts and thereby replace that domain as
authority.

### Closed D-117 report-consumption profile

Only the generalized v2 mint applies this profile; historical v1 behavior and
bytes remain frozen. Every listed set is closed, so any other key refuses.

- Top level requires `schema_version`, `spec_schema_version`, `runs_root`,
  `manifest_id`, `consumption_semantics_id`, `consumption_provenance`,
  `governance`, `cells`, `spec_membership_refusals`,
  `idle_admission_refusals`, `whole_window_drift_allowances`, and
  `all_cells_extractable`; `single_count_discipline` is optional.
- A cell requires `cell_id`, `kind`, `metric`, `window_class`,
  `cap_hit_policy`, `n_planned`, `n_admitted`, `excluded_slots`,
  `extractable`, `refusal_reasons`, `floor`, `claim_family`,
  `whole_window_drift_allowance`, `operative_floor_j`,
  `anchor_shift_bound_max_j`, and `members`. The only optional keys are
  `floor_conditions`, `floor_source`, `floor_limit_class`,
  `point_floor_diagnostic`, and `single_count_discipline`.
- A non-null floor requires `kind`, `n`, `mean_j`, `deviations_j`,
  `sample_stddev_j`, `max_abs_deviation_j`, `t_critical`,
  `prediction_component_j`, `unguarded_floor_j`, `guard_factor`,
  `guarded_floor_j`, `admissible_half_widths_j`,
  `corner_widened_unguarded_floor_j`,
  `corner_widened_guarded_floor_j`, and `smoke_only`. Its only optional keys
  are `whole_window_drift_allowance_j`,
  `whole_window_drift_allowance_provenance`,
  `drift_widened_unguarded_floor_j`, and
  `drift_widened_guarded_floor_j`.
- A member requires exactly `slot`, `bundle_id`, `block_id`, `position`,
  `metric_value_j`, `cooldown_result`, `cooldown_verified`, `cap_hit`,
  `excluded`, `reasons`, `anchor_shift_bound_j`,
  `operative_anchor_envelope`, `consumption_provenance`, `summary_sha256`,
  `bundle_sha256`, and `config_sha256`.

### Required generalized-v2 verification order

1. Derive actual Git `HEAD`, require a clean tree, compare any claimed commit,
   and record whether `origin/main` contains the mint head.
2. Start the v2 authentication-read session before the first pinset or input
   manifest byte is read. Reject duplicate keys and non-finite numbers at the
   same read call that returns every reached JSON/JSONL input, and register
   non-JSON evidence as raw. Every re-read is a real filesystem read and must
   match the path's first registered SHA-256 before its bytes are returned.
3. Authenticate the issued acceptance artifact against its exact code pin and
   internal derivation.
4. Load the ledger against the Git-committed terminal head and acceptance
   cutoff; reject malformed chains, rollback, stale/uncommitted heads, open
   sessions, and invalid custody. After that authentication identifies the
   head-pin path, derive the commit that last changed it and separately record
   whether `origin/main` contains that commit. Either containment may be
   unknown and neither gates issuance.
5. Authenticate the whole-window verdict, policy, verdict-owned calibration
   bracket, attempts, supersessions, bundle bytes, and complete evaluation
   membership.
6. Derive the expected session/window/endpoints from that verdict bracket,
   refuse any supplied binding that disagrees, then validate plan, evidence
   root, runs root, slots, content IDs, and terminality through the bracketing
   API. The binding never supplies its own expected window.
7. Recompute exact-Decimal drift and the issued-rule allowance.
8. Apply the recursively closed D-117 report profile.
9. Treat report cells as caches: reauthenticate members, metrics, widths,
   semantics, and allowance, then recompute every mint-relevant floor.
10. Compare every required frozen pin with its domain-owned projection. A
    missing, placeholder, or disagreeing pin refuses; none is generated.
11. Construct all four cells, recompute component/cross-stack maxima, validate,
    bind back to source bytes, complete post-bind validation while the read
    session remains active, and create outputs exclusively.

### Registration-at-read trust boundary

The generalized v2 mint has one context-scoped authentication input registry.
Every application-level byte read used to authenticate, hash, validate,
rederive, or bind an input enters that registry atomically at the read call.
The first record for a filesystem path contains its normalized path, SHA-256,
wire grammar, and read count; later reads increment the count only after their
newly read bytes match the first SHA-256. A change refuses with
`v2_authentication_input_changed`. The Git-committed head-pin blob is recorded
under the virtual identity `git:HEAD:<relative-path>` and follows the same
strict JSON rule.

Registry records have two semantic classes:

- `json` and `jsonl` records are registered only after UTF-8 parsing succeeds
  with duplicate keys and non-finite numbers forbidden. A `.json` or `.jsonl`
  path cannot be requested as raw merely because a caller needs only its hash.
- `raw` records cover every other reached byte source, including sidecars,
  CSV, plist, estimator source pins, and other binary evidence. Streaming large
  raw inputs finish through the same registration primitive.

The authentication call graph is the only discovery mechanism. There is no
parallel recursive traversal and no second equality oracle. Missing optional
paths are probes rather than byte reads and have no path-plus-SHA record. An
AST build guard rejects direct readable I/O in the marked v2 authentication
surface outside the central reader. The issued-pinned
`joulewise/reduce.py` is the sole exact exception: its bytes must hash to
`5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615`,
and the guard characterizes exactly its five historical direct `read_bytes`
calls in `_verify_instrument_calibration` and `_derive_anchor_context`.
`BundleReader` supplies a registration-aware `Path` capability only while a
v2 session is active; readable operations register the exact returned bytes,
and `/`, `parent`, and `resolve` preserve the capability. Any reducer byte or
callsite change loses the exact exception. The production regression additionally
audits low-level opens beneath its fixture/evidence roots and requires every
actually opened input to appear in the registry.

The session is v2-only. With no active session, shared readers preserve their
historical parsing, exceptions, and output, and v1 golden artifacts remain
byte-identical.

### Content-addressed calibration custody store

The generalized v2 CLI accepts the optional production input
`--calibration-custody-store ROOT`. Its absence selects the historical
receipt-locator behavior without changing v1 or v2 bytes. Its presence selects
one all-or-nothing mode: every custody-bearing final observation is read only
from `ROOT/<receipt.content_id>/`; receipt locators remain authenticated ledger
bytes but are never resolution fallbacks.

`ROOT/manifest.json` has the canonical UTF-8 JSON wire below: sorted keys,
compact separators, one trailing newline, no duplicate keys, and no non-finite
numbers. All object key sets are closed. `contents` is sorted by `content_id`;
each `artifact_sha256` object contains exactly the five governed names from
`GOVERNED_ARTIFACTS`, sorted lexically.

```json
{"contents":[{"artifact_sha256":{"events.jsonl":"<sha256>","instrument_evidence.json":"<sha256>","manifest.json":"<sha256>","power_trace.csv":"<sha256>","raw/powermetrics.plist":"<sha256>"},"content_id":"<sha256>"}],"ledger":{"head_digest":"<sha256>","head_sequence":76,"schema_version":"joulewise.calibration_observation_ledger.v1"},"schema_version":"joulewise.calibration_custody_store_manifest.v1"}
```

The manifest never supplies identities or hashes. The loader derives the
entire expected value from the authenticated ledger snapshot and requires
exact equality before resolving any content directory. It refuses in the
`calibration_ledger_custody_invalid` domain on null or duplicate content
identity, an incomplete five-hash vector, missing content/artifact, symlink,
non-regular member, digest mismatch, manifest mismatch, or any attempted
legacy/store mixture. Reads are contained and no-follow. Extra filesystem
entries are neither traversed nor registered.

The manifest's exact SHA-256 and schema travel on
`CalibrationLedgerSnapshot`. When store mode is active they are emitted as
`provenance.calibration_custody_store.{schema_version,manifest_sha256}` on
each component and the aggregate artifact. Evidence binding compares that
block to the authenticated snapshot before re-binding member evidence;
disclosure without equality is a refusal.

#### Production fixture transport

The 38 content directories are hydrated working data, not Git-tracked
authority. `transport_descriptor.json` pins the public release tag and asset,
`tar.zst` format, archive SHA-256, 191 logical files and their byte total, and
the committed census SHA-256. It contains no receipt locator or destination
mapping. The archive is a delivery replica; the issued ledger remains senior.

The governed packager emits sorted regular-file members with normalized tar
metadata and refuses any path outside the census or unsafe source entry. The
hydrator checks the archive digest before inspection; rejects absolute,
noncanonical, duplicate, unexpected, missing, linked, device, socket, FIFO,
and other non-regular members; requires the embedded census bytes to equal the
committed census; and writes only to a caller-supplied destination outside the
repository. The required `d117-production-proof` job caches only the compressed
archive under its exact digest key, hydrates beneath runner temporary storage,
re-authenticates the issued ledger and all 190 governed members, and runs the
full no-substitution regression. An ordinary shard may skip that one proof only
with the explicit label `full-fixture proof runs in d117-production-proof`;
such a skip is never acceptance evidence.

### No-substitution production regression

The decisive D-117 regression invokes the production extractor and generalized
v2 CLI in a clean temporary Git worktree. It may construct temporary files and
commits with real filesystem and Git operations, but it may not patch or
substitute extraction, strict validation, authentication, allowance
derivation, ledger custody, committed-pin checks, Git state or containment,
evidence binding, or output creation. In particular, a synthetic
`_fresh_original_core` adapter cannot supply production-path evidence.

The regression first proves an authentic mint succeeds. Its coordinated attack
then exercises every memo-§8 leg, asserts the first owning refusal stage, checks
genuine-source SHA inventories both after construction and after refusal, and
proves that neither output exists. Shadow-removal variants must expose the
step-9 report-cache refusal and step-10 frozen-pin refusal beneath the step-8
unknown-key refusal. A separate mutation matrix must make each authenticated
domain—acceptance, ledger, committed pin, binding, verdict, campaign, attempt
custody, primary bundles, and report cache—refuse in its own domain. Synthetic
adapters may support separately labelled unit tests, but may never become a
replacement authority for this regression.

Every v2 artifact carries the required provenance assurance profile
`single_authority_hash_bound_replay.v1`, with
`independent_attestation=false`. It establishes exact-byte consistency with
disclosed commitments, ledger/verdict consistency under recorded code, and
deterministic rederivability. It does not establish operator honesty,
independent witness of physical collection, or resistance to coordinated
prepublication rewrite.
