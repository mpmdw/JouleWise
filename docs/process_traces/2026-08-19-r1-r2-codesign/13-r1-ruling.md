# MAGISTRATE RULING — R1: Production capture-pipeline v3 adoption

Fable magistrate, 2026-08-19. Co-design protocol (D-144-pending), first
application. Seats: terra (gpt-5.6-terra, xhigh) and Opus 5, independent
designs + one bounded debate round. Documents: R1-brief.md, R1-terra.md,
R1-opus.md, R1-debate-agenda.md, R1-debate-terra.md, R1-debate-opus.md
(this custody directory).

Classification: BIG design (schema/contract change; claim-admission gate).
Consequences: implementation gauntlet + Fable final review + one more
seat-pass over the implemented artifact pre-merge.

## Ratified spec

**S1 — Identity.** Production powermetrics capture emits
`schema_version = "p2-038.3"` paired inseparably with
`clock_anchor.method = powermetrics_native_second_rate_aware_set_membership_v1`.
One canonical mapping `SCHEMA_FOR_ANCHOR_METHOD` lives in
`joulewise/uncertainty_evidence.py`; method is the single dispatch key
everywhere; a label/method disagreement refuses as
`clock_anchor_era_inconsistent`, never resolves in favor of either.
`p2-038.2`/`.1` retained forever as stored eras (never retired, relabeled,
or mutated — the 54-count in the brief was wrong; population is enumerated
at implementation time into a manifest, ~748 primary).

**S2 — Strict verify (custody, era-agnostic).** Era-faithful stored-method
re-derivation for all three eras (D-078 precedent): `.1` frozen legacy
replay; `.2` exact v2 re-derivation; `.3` exact v3 re-derivation; crossed
pairs refuse. The `cli.py:1575` rich-telemetry fail-open (executed-proven:
identical corruption caught at `.2`, silent at `.3`) is a BLOCKER fixed in
the flip commit, with the attack test written as the corruption case (A4).

**S3 — Claim barrier (mechanical, single predicate).** One closed predicate
in `joulewise/uncertainty_evidence.py`:
`CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})` with shared
helper `capture_pipeline_refusal(metadata) -> str | None`. Callers — analysis
admission (`analysis_engine/inputs.py`), floor extraction
(`floor_extraction.py`), whole-window member admission (`whole_window.py`) —
call the helper; none re-implements the test or inlines a method literal.
Mutation check: flipping the helper's return must kill ≥1 test in each lane
independently. (Both seats' content composed: terra's three claim-lane
sites + opus's predicate discipline.)

**S4 — Refusal vocabulary.** New ENGINE reason `capture_pipeline_superseded`,
registered additively in `ENGINE_REASON_CODES` + `_NOT_RESOLVABLE`
(`analysis_engine/claims.py`) + the `whole_window.py` and
`floor_extraction.py` registries (4 additive entries). Rationale (ruling on
the crossed positions): opus's E1 census — 745/748 stored v2 bundles carry
`clock_anchor.status: "bounded"` — makes `clock_anchor_unresolved`
empirically false against those artifacts' own published metadata, and
refusals are reportable results read by a metrology-expert advisor.
`clock_anchor_unresolved` is reserved for anchors that did not resolve.
Terra's round-1 registry-fan-out concern is dissolved by the engine-registry
placement (not the D-057/D-078 reducer wire). Dissent recorded: none — both
seats accepted the opposing name once the evidence landed; the crossing
itself is noted as evidence the protocol works.

**S5 — Calibration-lane diagnostics.** `discover_calibration_candidates`
distinguishes "not a candidate" from "candidate of a superseded era":
rejection solely on `anchor_method_version` reports
`capture_pipeline_superseded` and is excluded from the `registered_valid`
reconciliation, so era eligibility never masquerades as
`calibration_ledger_custody_invalid`. The retained mixed-era regression
asserts the era reason.

**S6 — Per-consumer admission for stored anchor-v2.** Strict verify: admit
as historical evidence, byte-exact v2 re-derivation. Campaign/shakedown gate
(`scripts/run_campaign.py:1635,:1644` — the brief's cli.py citation was
wrong): refuse; equality against the ACTIVE constant, not set-membership.
Reducer: era-faithful reduction, replay-readable not claim-licensed.
Claims/floors/whole-window: refuse via S3/S4; NO re-derivation retrofit lane
(the D-079 corpus re-derivation stays lawful and distinct: population
statistics for a threshold under an independent oracle, never per-bundle
claim energies — stated so nobody later generalizes it).

**S7 — Site census (ratified union).** The four adapter sites
(`adapters/powermetrics.py:525,540,563,755` + import + TIMESTAMP_DERIVATION
provenance text + `:1832` docstring); six cli.py sites
(`:108,:1233,:1266,:1290,:1547,:1575`); campaign gate
(`run_campaign.py:1635,:1637,:1644`); `environment_admission.py:307,351`
(stored-method dispatch — wrong-reason refusal hazard);
`powermetrics_fiducial.py:1467` (kill the silent `or CLOCK_METHOD_V2`
default; absent method raises); `controller.py:1355-1362` (S8);
`analysis_engine/inputs.py:188` dead-status fix (+ `:111` comment
correction); `arm_readiness.py:4143-4149` `_issued_d079` allow-list gains
the new acceptance id in the same commit (six gating call sites; latest-
failing site found — fails at ARM TIME); contracts per both seats' B8/F3
lists incl. the two-eras-stale `p2-038` spec.

**S8 — Controller seed envelope.** When the adapter produced no uncertainty
evidence: no era label is synthesized (no `schema_version`, no
`clock_anchor.method`); evidence is explicitly incomplete with a
`capture_pipeline_absent` marker; strict verify fails the bundle closed.
(Terra maintained; opus conceded on executed census: zero stored bundles
carry the seed shape.)

**S9 — r5 reissue.** The flip edits an r4-pinned estimator source, so a
science-neutral D-079 r5 (`d079_calibration_acceptance_v2_n17_r5`) is
REQUIRED, lands in the SAME COMMIT as the flip, inside the parked atomic
transaction, before any freeze mint. Neutrality is PROVEN by full 19-member
replay diff against the r4 derivation record (bespoke script; the reissue
tool's scalar comparison cannot check v3 generations). r4/r3 retained
byte-identical as history. Rejected: narrowing the pin set to dodge the
trigger (self-exemption).

**S10 — Sequencing.** Step 1 BEFORE the flip: parameterize the shared test
helper `self_consistent_calibration` by anchor method (derive AND declare
from one method; executed root-cause: the current canonical red is the
landed admission comparator meeting the v2-minting helper, NOT the unflipped
adapter). Then flip + hardening + r5 in one commit; then S3 barrier;
contracts; goldens wave with delta re-audit. Attack tests A1-A9 (opus list)
are the regression floor; A9 mutation-kill proves no vacuous era coverage.

## Rejected alternatives (carried from seats, ratified)
Keep-label-version-elsewhere; retire `.2`; claim retrofit via v3
re-derivation; set-membership at the campaign gate; flip outside the
transaction; pin-narrowing; test-patching to green; helper relabel without
re-derivation; barrier-by-policy-document (all four seat documents give the
evidence; this ruling adopts their rejections wholesale).

## Open items routed to Ed (unchanged by this ruling)
Written disposition for the stored anchor-v2 population (registered
limitation vs mechanical barrier alone — recommend the limitation paragraph);
the ruling notes the claim barrier rode inside R1 by magistrate scoping call
(D-144 "big" test satisfied by this ruling's own gauntlet consequences).
