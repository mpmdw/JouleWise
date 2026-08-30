# `_v5` prep — delta re-audit 2: magistrate disposition (Fable, 2026-08-30)

Auditor: fresh Sol xhigh over `7749f493..60beae60`; custodied as
`03-delta-audit-2-sol-xhigh.md`. E-4/E-6 and all round-1 installations
INSTALLED; E-1/E-2/E-3/E-5 PARTIAL, one blocker.

## Standing-trigger acknowledgment

The one-pin-bypass class has now survived two consecutive rounds (delta-1 F1
at the generator/runtime path; delta-2 F1 at direct typed construction and
the exported JSON Schema) — same defect class, another missed call site. Per
the standing escalation trigger the next spend is a formulation change, not a
third same-shape patch:

## G-1 (blocker, structural): the invariant moves to the construction choke point

RULED: both-or-neither is enforced ONCE, at the single point every
construction path traverses — ModelConfig's own construction validation
(`__post_init__` or the one canonical validator that dict loading, direct
typed construction, and any deserializer all call). The exported JSON Schema
gains the equivalent constraint (`dependentRequired`/`oneOf`) and the golden
regenerates. The proving test ENUMERATES construction paths — dict loader,
direct dataclass construction, schema validation of a JSON document — and
asserts each refuses both one-pin states. If a THIRD audit finds any one-pin
path to model load, a COLD INSTANCE rules before any further round — no
discretion.

## G-2 (should-fix): vocabulary propagation completed

`model_identity_mismatch` joins every TRACKED output-schema and contract
vocabulary the auditor names (the delta-2 report's F2 list), with the
regression asserting the tracked surfaces and the enum agree exactly.

## G-3 (should-fix): replay predicate consumes the authenticated bound

The replay helper passes the AUTHENTICATED operative bound to the production
predicate — the same value the fence authenticated — never the caller's
near-equal copy; regression: a caller bound differing at the last ulp from
the authenticated bound must not change the verdict (the authenticated value
governs).

## Round shape

Fix round 3 (Sol high) implements G-1/G-2/G-3 exactly; then delta re-audit 3
(fresh Sol xhigh) whose FIRST question is an exhaustive search for any
remaining one-pin path. Merge only after delta-3 is clean and CI green.
