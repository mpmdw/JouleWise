# COLD-GATE PACKET 2 — D100-BII-BINDING-01 clause 3(c) nested-content closure: second same-signature formulation failure (2026-08-02, successor session)

Mechanically assembled per D-106 clause 4: verbatim source quotes with
file:line; governing conditions unpara­phrased; magistrate candidates
LABELLED as candidates at the end; no runway/cost framing.

## Trigger record

Standing escalation trigger (CLAUDE.local.md rule 11): "two consecutive
rounds failing with the SAME SIGNATURE — same defect class, another
missed call site, another failed formulation — is evidence of a
structural problem, and the next spend is a CONSULT, not round three."
Mandatory cold-gate trigger: "any second fix round on the same defect."

- Formulation 1 (commit a6ce7af, original implementation): focused
  audit finding A1, verbatim: "The classifier rejects only
  unallowlisted top-level Mapping values. It does not classify children
  of allowlisted mappings or list-valued extensions, violating D-106
  nested-content fail-closed semantics."
  (.desk/coldgate_d100_bii/focused-audit-a6ce7af.md, finding A1,
  joulewise/salvage_dangler.py:544)
- Formulation 2 (fix round 1, uncommitted diff on a6ce7af): delta
  re-audit finding F1, verbatim: "Recursive classification is still a
  key denylist, not fail-closed content classification …
  environment_admission.failure containing workload output, an
  NFKC-equivalent fullwidth model_output key, unknown empty/scalar
  children, and matching event/summary failure_reason workload values
  all remain LICENSED." (delta report F1,
  joulewise/salvage_dangler.py:526 and :567; probe V4 observed
  "value True / unicode True / empty True / scalar True")

Same signature: both formulations are enumeration-shaped closures
(first by allowlisted-container position, second by key denylist) that
license content the contract says must void.

Secondary finding (delta F2, should_fix, verbatim): "Unbounded
recursive walk raises an uncaught RecursionError … A valid JSON
metadata chain 995 mappings deep reaches _validate_nested_content and
raises RecursionError; scripts/run_campaign.py:4822 does not catch it.
Authorization does not occur, but the inspector's refusal contract is
bypassed by a command-level crash."

## Governing conditions (verbatim)

D-106 ruling clause 3, docs/decision_log.md:6682-6695 (excerpt covering
(c)): "(c) nested-content closure per the decisive audit's second
scenario; … These are different IN KIND from the two failed
enumerations (the standing trigger's own requirement) and land as
ordinary audited work — one commit + focused audit."

Kernel row D100-BII-BINDING-01 acceptance evidence item (verbatim,
docs/process/state_kernel.json): "Nested-content closure: nested
workload evidence under metadata or event metadata voids per the
decisive audit's second scenario (unclassifiable means void)".

Kernel row fence (verbatim): "The fixes bind capture identity by
interval containment and digest freeze, never by per-file schema
formulations (telemetry rows carry no identity by construction); no
third schema-shaped formulation may be proposed (D-106 clause 3
(fix-kind discrimination))." [NOTE for the gate: this fence's text
governs CAPTURE IDENTITY; whether it also constrains the nested-CONTENT
fix shape is one of the ruling questions.]

The decisive audit's second scenario (verbatim, PR-#94-era decisive
re-audit, .desk/coldgate_d100_bii/decisive-reaudit.md): "The 'extra
keys' attack also finds a gap. Top-level extra telemetry/event keys
correctly void at lines 393-400 and 655-656. But event metadata is
accepted as any mapping at lines 657-660, and
_contains_workload_evidence is a spelling list at salvage_dangler.py:440.
A nested model_output field is unrecognized and passes. This violates
'unclassifiable ⇒ void.'"

## Established facts both instances may rely on

1. Producer emissions (delta re-audit CLEAN trace, verbatim): "producer
   tracing at controller.py:2243-2254, 2826-2847, and 2921-2925 found
   exactly the six named scalar fields. Null, finite numeric, and
   literal-True constraints match emissions; no seventh runner-owned
   scalar field was found." The six admissible `extra` fields
   (fix-1 report): preceding_member_end_s, idle_start_s,
   preceding_gap_s, clock_step_suspect, cooldown_cap_hit,
   environment_admission_failed.
2. Everything else in the fix round is CLEAN and delta-verified: A2
   closed exactly (six canonical tests pass; fixture adds only
   quarantine_root + canonical manifest; manifest-less refusal has a
   real test); interval containment, digest freeze, in-code marker,
   and the three test_d106_* methods byte-identical to a6ce7af;
   over-refusal check clean.
3. The b-ii subjects this license currently needs (window B's two r08
   bundles) carry a recorded lead manual verification (2026-08-01) and
   the metadata/event shapes they actually exhibit are the governed
   idle-abort grammar.

## Precedents on the record (verbatim excerpts)

- D-097 (docs/decision_log.md; claims-desk report §7): "the reader's
  accepted set exactly equals the writer's emitted set (v1 only)" —
  adopted because "with no writer emitting the enum every in-manifest
  marker is self-asserted"; grounds included "presence is uniform
  malformation."
- D-105 (C-040 addendum record): recognizer "exactness struck for a
  documented decidable superset"; refuter proof that "the
  number-grammar's literal subset direction is undecidable-at-sane-cost
  (three rounds failed on it)".
- D-106 grounds clause (4): "powermetrics emits identical 8-field
  telemetry rows for measured and idle captures from one code path —
  telemetry rows carry NO identity BY CONSTRUCTION, so per-file schema
  formulations can never bind capture identity; only interval
  containment or a digest freeze can."

## Required ruling

1. Does the structural diagnosis hold: is denylist/spelling-list
   classification of nested CONTENT (keys or values) unable to satisfy
   "unclassifiable ⇒ void" for this surface, in the same way the C3
   number-grammar exactness and the b-ii per-file schema formulations
   failed? Or is formulation 2 an ordinary implementation miss that a
   licensed round 2 may close?
2. What fix SHAPE closes clause (c) decidably? Rule on the candidates
   below or supply a variant, with the exact acceptance predicate.
3. Does the kernel fence's "no third schema-shaped formulation"
   language (written for capture identity) constrain the nested-content
   shape, and if the correct shape IS a closed admission grammar, state
   the distinction on the record.
4. Disposition of F2 (recursion bound): part of the same commit under
   the ruled shape, with what bound-and-refuse semantics?
5. Whether the fix may proceed as gate-licensed round 2 in the SAME
   commit arc (one commit + fresh focused re-audit), or must return to
   the decision level (D-106 amendment).

## Magistrate candidates (LABELLED CANDIDATES — drafted at the bench,
non-binding, both instances free to reject both)

- C-A (closed admission grammar / writer-set equality, D-097 pattern):
  metadata and event metadata validate against a CLOSED grammar derived
  from producer emissions (exact key set per container, exact
  type/value constraint per key, the six producer-owned extra scalars,
  no other keys, no nested containers beyond the grammar); ANYTHING
  outside the grammar voids. No workload-evidence spelling list remains
  load-bearing (it may stay as defense-in-depth). Depth is bounded by
  the grammar itself (no unbounded recursion exists to attack).
- C-B (third enumeration, hardened): keep denylist recursion; add value
  classification, NFKC/confusable normalization, unknown-scalar and
  empty-container refusal, explicit depth bound. [Flag: this is a
  third enumeration-shaped formulation of the same closure — the class
  both prior failures share.]
- C-C (grammar core + documented decidable superset): C-A for the
  containers the producers emit; where a container is legitimately
  open (if any is), a documented decidable-superset rule per D-105's
  pattern instead of claimed exactness.

Packet ends. Sources: .desk/coldgate_d100_bii/focused-audit-a6ce7af.md,
the fix-1 and delta reports (session scratchpad, copies to be banked
alongside this packet), docs/decision_log.md D-097/D-105/D-106,
docs/process/state_kernel.json row D100-BII-BINDING-01,
.desk/coldgate_d100_bii/decisive-reaudit.md.
