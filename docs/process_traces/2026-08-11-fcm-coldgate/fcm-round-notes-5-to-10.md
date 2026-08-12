# FCM-01 rounds 5-10 — full D-124-chain amendment notes (moved from the decision log for site-capsule budget)

These are the verbatim round-by-round amendment notes. The decision log carries a compact summary pointing here; nothing is lost.

### D-124 amendment — 2026-08-11: round-5 structural registered input

Round 5 narrows the registered surface to a frozen block-input record produced
by the module-private registered builder. The builder receives authenticated
bundle-derived contrast evidence, evaluates the `(0.0, 0.0)` contrast itself
once, evaluates both enumerated shift grids, and records each positive
shift-`0.0` position; the registered estimator takes the zero point only from
those recorded positions and accepts no caller-supplied zero designator. The
legacy keyword surface remains available for the byte-frozen independent
oracle, with its admission and arithmetic unchanged, but every result from that
surface is unregistered and the extraction gate refuses it for a registered
cell. Both surfaces route through one arithmetic core, so the oracle continues
to bar the arithmetic used by registered estimates. The registered zero-point
rule is now
`zero_point_is_carried_structurally_by_the_registered_builder_as_the_shift_zero_index_never_supplied_or_matched_by_value_and_direct_keyword_inputs_are_unregistered`;
the resulting parameter hash is
`973c9bfc5a4d5984b5db6eeba5d054613d86a0bd69ae1f8a56c5fad5d7a453b7`,
and the outgoing round-4 hash joins the three earlier superseded registrations.

The claims-with-assumptions form remains: **over inputs constructed by the
registered builder from authenticated bundle evidence, the emitted width
bounds the exact admissible width outward, up to the disclosed member-envelope
pad and the disclosed zero-point discrepancy term, under the documented
single-sourcing assumptions for the bracket bounds in the audit table above.**
Python privacy is conventional rather than enforced: underscore names and the
frozen dataclass do not cryptographically prevent deliberate fabrication, so a
construction-site inventory test pins the intended one-builder/one-production-
caller discipline. Evidence faithfulness upstream of the builder remains an
assumption, not a result of this structural repair.




---

## Stopping-rule execution + rounds 6-10 full notes (moved from the decision log)

**STOPPING RULE EXECUTED (2026-08-11, same day).** The round-5 delta
re-audit fired the rule: FCM-R5-01 — records fabricated outside the builder
(direct construction, dataclasses.replace, object.__new__ + __setattr__,
copy, pickle; the frozen dataclass's generated constructor plus a
type()-only admission check) are admitted, stamped registered, pass
registration validation, and understate by 4.999917146975008e-10 J in exact
arithmetic — the residual risk the relicense contract disclosed in advance,
realized. Per the rule, executed without deliberation: the D-124
two-shared-edge candidate is WITHDRAWN under D-124's own fallback clause;
freeze-plan Q7 REVERSED; both floor packs' comparative cells re-specced to
the worst-case default estimator; no round 6 under any authority but a new
explicit Ed decision. The six-round record (five understatement mechanisms
+ the provenance class; three cold-gate sittings; five delta audits; the
adversary-authored oracle; exact-arithmetic proofs of the enumeration) is
custodied on impl/floor-commonmode-01 at 0b5fce8 (STOPPED-FCM01.md) as
permanent gauntlet evidence and paper material. Terminal lesson banked: a
sound registered arithmetic surface in Python requires a process boundary
or capability token, not conventional privacy (see the Rust-rewrite memory
— now with an executed demonstration).


### D-124 amendment — 2026-08-11: round-6 D-132 revival by surface deletion

D-132 revives FLOOR-COMMONMODE-01 because the six-round record is a
converging instrument, not a doom loop, and binds the closure design: the
public registered arithmetic surface is deleted.  The public
`two_shared_edge_common_mode_floor` retains only its legacy raw keyword path
and every `FloorEstimate` it returns is unregistered.  The importable
`_RegisteredCommonModeBlockInput` type, its builder, and the estimator's
`registered_block_inputs` overload no longer exist.  Registered arithmetic is
now private to `floor_extraction`; its inputs are derived inside
`extract_comparative_cell` from authenticated bundle evidence, and a
registration remains an in-process attribute on the resulting governed
`CellReport`.  The committed preregistered extraction spec remains the
declarative registration authority; report and artifact serialization do not
carry that authority.
The default `comparative_false_effect_floor` path and the legacy raw common-mode
path remain public and behaviorally unchanged.

All `shared_extrema_*` parameter rules retain their round-5 semantics.  The
round's parameter dictionary added a provenance rule that incorrectly treated
the extraction-produced `CellReport` as sufficient custody closure; round 7
below corrects that claim and deletes the serialized vocabulary.  The
resulting round-6 parameter hash is
`dea20dc0d43760ebfd17cb6a130ab2c2e85fb7a9a06c224cbf584804ee2f9bdf`.
The round-5 hash
`973c9bfc5a4d5984b5db6eeba5d054613d86a0bd69ae1f8a56c5fad5d7a453b7`
joins the four earlier superseded registrations and is rejected with them.

The claims-with-assumptions form narrows accordingly: **registration is
declared in the committed preregistered extraction spec, while extraction
re-derives provenance from authenticated evidence and emits no serialized
registration field; there is no public callable that accepts constructed
arithmetic inputs and returns a registered `FloorEstimate`.**  The
refuter-authored round-4 oracle
continues to exercise the same arithmetic bars through the extraction
module's test-only internal seam; its case generation and assertions are
unchanged.  The delta-4 counterexamples, 2,048-case adversarial-zero campaign,
and real-fixture exact-width checks likewise exercise the internal extraction
seam.  This construction eliminates FCM-R5-01's fabricated-record admission
class instead of attempting to authenticate Python object provenance.

### D-124 amendment — 2026-08-11: round-7 cold-gate ALT-D120 vocabulary deletion

The revised cold-gate sitting (Fable adjudicator plus Opus contract-lens
refuter) REJECTS the round-6 custody-closure claim and RULES the hybrid plus
ALT-D120 remedy: deletion-by-vocabulary.  The committed preregistered
extraction specs remain the one declarative home for estimator registration,
and extraction continues to retain registration only as an in-process
`CellReport` attribute.  `CellReport.as_row()` no longer serializes
`estimator_registration`; the recursively closed D-117 mint-consumption
profile and the detection-floor artifact profile no longer admit that key.
Consequently an injected registration dictionary is an unknown key in either
JSON profile, and floor-artifact authentication raises during validation
before returning an authenticated value.  Provenance is re-derived from the
governed spec and authenticated evidence; it is not read from report or
artifact JSON.

The parameter rule is corrected verbatim to
`registration_is_declared_only_in_the_committed_preregistered_extraction_spec_no_admitted_report_or_artifact_vocabulary_represents_a_registered_result`.
This is the sixth and only round-7 registration rotation, producing
`dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38`.
The round-6 hash
`dea20dc0d43760ebfd17cb6a130ab2c2e85fb7a9a06c224cbf584804ee2f9bdf`
joins the five earlier superseded registrations and is rejected with them.

### D-124 amendment — 2026-08-11: round-8 total vocabulary refusal and duplicate-key JSON closure

The O3 full-delta review closed the arithmetic terminally: 4,096
exact-rational cases produced zero understatements, the differential campaign
was identical, and the promoted result did not drift.  Its FCM7-01 finding
identified two remaining admission gaps in the round-7 ALT-D120 claim.

First, the admitted report and artifact profiles now walk the entire parsed
JSON value recursively through both objects and arrays and refuse the literal
key `estimator_registration` at every depth before profile-specific checks.
This prohibition includes the current registration dictionary, the pending
registration dictionary shipped in the 7B extraction spec, and a key whose
spelling is Unicode-escaped in the source bytes.  Governed extraction specs
remain outside admitted report/artifact vocabulary and retain their
registration declarations and existing validation.

Second, floor-artifact byte authentication now parses with a duplicate-key
refusing object-pairs hook at every object depth.  Key shadowing therefore
raises the typed fail-closed analysis-input error before semantic validation;
the digest continues to bind the exact admitted bytes, but last-key-wins JSON
can no longer hide a forged value inside those bytes.  Value-level validators
continue to validate already parsed values.  Together these closures make the
round-7 parameter rule total over every admitted report or artifact value and
byte entry point in the implementing unit.

### D-124 amendment — 2026-08-11: round-9 strict pre-admission at the generalized mint

The round-8 delta found that its duplicate-key closure did not yet cover the
generalized D-117 mint's report-byte entry: the generalized layer delegated to
the pinned legacy core, whose `_load_json_object` used ordinary last-key-wins
JSON before `validate_d117_mint_consumption_report` saw the value.  Executed
shadowing attacks at top-level `governance` and member-level
`operative_anchor_envelope` therefore retained the forged raw bytes while the
collapsed values were admitted.

Round 9 places an exact-byte, duplicate-key- and non-finite-refusing parse in
the generalized layer before every delegated report authentication.  The same
pre-admission rejects `estimator_registration` recursively before the legacy
loader runs.  Both generalized v1 and v2 file-backed entry points execute
inside one digest-stable authentication-read session, so a successful preparse
and the legacy re-read cannot observe different bytes.  The scoped extraction
bundle readers likewise use strict JSON for summary and metadata admission.
The two shadowing attacks now refuse before `_authenticate_component`, while a
legitimate eight-component report fixture still reaches legacy authentication.

The mandated load census also found ordinary JSON admission reads in
`joulewise/analysis_engine/inputs.py` and `joulewise/analysis_engine/registry.py`.
The lead expanded round-9 scope to those two files.  Their manifest, config,
plan, order/campaign evidence, cooldown, receipt, strict-evidence, and metadata
byte routes now use duplicate-key- and non-finite-refusing parsing plus the
same recursive `estimator_registration` vocabulary refusal.  The existing
floor-artifact byte route retains its round-8 duplicate hook and recursive
artifact-profile refusal.  Every censused admission parse is therefore strict
at the parse site or guarded by an executed exact-byte preparse.

### D-124 amendment — 2026-08-11: round-10 overflow and admission-census closure

Round 10 demonstrated that four helpers described as non-finite-refusing in
round 9 still admitted a syntactically valid overflowing exponent: `1e999`
became positive infinity through the default `parse_float`.  The generalized
mint, floor-extraction, analysis-input, and analysis-registry strict helpers
now use finite-number parse hooks (including an integer projection check) so
overflowing numeric tokens raise the same typed refusal used for duplicate
keys.  Floor-artifact byte authentication routes through the analysis-input
strict helper rather than a separate duplicate-only parser.

The census also corrects the floor-extraction classification: the parser used
by `_read_summary` did not itself perform the claimed recursive vocabulary
refusal.  It now rejects `estimator_registration` through objects and arrays,
so both an overflowing nested summary value and a nested deleted key return
the fail-closed `summary_unreadable` result while retaining the exact-byte
digest.

The independently censused authentication-session JSON/JSONL parser now uses
the same complete strict admission: duplicate keys, literal and overflowed
non-finite numbers, non-finite integer projections, and recursively nested
`estimator_registration` keys all refuse before an input is registered.  The
generalized layer explicitly authorizes only the exact governed extraction-
spec paths that declaratively own estimator registration; reports, artifacts,
campaign evidence, and all other JSON/JSONL remain closed.  Executed direct
session checks and pinned-core calls under that session refused all three
round-10 attack classes, while the registration-bearing governed 7B spec and
the legitimate mint paths remained admitted.  No pinned-core byte changed.


