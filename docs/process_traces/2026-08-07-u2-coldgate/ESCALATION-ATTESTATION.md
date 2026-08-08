# U2 attestation-binding escalation (2026-08-08) — count 2, consult ordered

**Trigger:** standing same-signature rule. The class "evidence/lineage
attestation not bound to its claimed fact" fired at count 1 in the
round-2 gauntlet delta (P1: absorbed derivation-basis additions not
bound to trigger_judgment.new_content_ids — mutation-proven). FIX-1
closed that site exactly (fix-round delta confirms: set-exact equality
at both validation layers, discriminating regression). The fix-round
delta then REPRODUCED the same class at a SIBLING SITE:
trigger_judgment.triggers is only schema-validated (nonempty ordered
subset of two allowed strings) and never recomputed against the
authenticated corpus — a successor whose real trigger was
range-expansion, forged to claim the count-boundary trigger while the
source count is below that boundary, passes _valid_acceptance_bound
AND load_calibration_acceptance_registry after rehashing
(reproduction transcript in FIXROUND-DELTA.md beside this file).

Two sites, one class, consecutive rounds: the structural problem is
that lineage/judgment attestations are validated as WELL-FORMED, not
as TRUE. Site-by-site equality patches are the losing shape.

**DISPOSITION:** bounded design consult (Sol xhigh, read-only)
chartered to produce the terminating design: the COMPLETE inventory of
attestation-bearing fields in the successor artifact + registry
lineage (new_content_ids, triggers, prior_observation_set +
disposing_decision_id seams, boundary-rule/count fields, parent
operatives, anything else the schema carries), and per field a binding
ruling — RECOMPUTED from authenticated sources and compared exactly
(naming WHICH layer can recompute it: standalone artifact validation
vs parent-aware registry load vs build-time-only with load-time
consistency) or explicitly classified NON-AUTHORITATIVE ANNOTATION
(never consumed by any decision path, and marked so). Plus the
regression contract that makes the class dead as a class.

Non-class findings from the same delta ride the post-consult rework:
fsync ORDERING relative to os.replace (FIX-4 partial); FIX-11's
one-active regression masked by an independent check; FIX-5/6
hard-coded /private/tmp custody inputs (tests SKIP on fresh checkouts
— coverage silently vanishes on CI); FIX-9 missing-field cases not
reaching the runtime guard; ROUND2-DELTA.md trailing whitespace.
