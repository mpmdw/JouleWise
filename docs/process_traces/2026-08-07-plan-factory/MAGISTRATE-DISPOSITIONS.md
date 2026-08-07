# Plan-factory dispositions (magistrate, 2026-08-07)

## BINDING SYSTEMIC RULE (adopted from the U4/U8 examination)

**Every numeric or structural oracle a downstream plan takes from the
D-117 design memo MUST be re-derived from the LANDED branch, and any
divergence recorded in the plan.** The memo is a design document written
before U1 existed; U1 superseded some of its literals. Confirmed instance:
the memo's "ideal terminal sequence is 85 **under the proposed
three-receipt session model**" — landed U1 uses FIVE receipts per window
(session capability, exclusive slot claim, pre finalization, post
finalization, terminal pin path), so the real no-failure terminal sequence
is 91, and a regression pinned to 85 would certify a ledger shape the
three nights will never produce. This rule binds U4-U10 and any plan
derived from the memo.

## U4 — synthetic three-window regression: ACCEPT WITH AMENDMENTS

Strong enumeration (all 7 proof obligations + 12 refusal-vector bullets
decomposed into 30 named tests; every named API and all 16 refusal codes
verified real on the landed branch). Blocking amendments before landing:

1. **Supersede the sequence-85 oracle** — drive the happy path through the
   PRODUCTION writer path including the exclusive slot claim; assert the
   derived value (91) from a module constant plus model-independent counts
   (3 sessions, 6 live observations).
2. **The D-110 never-zero test currently CANNOT FAIL** — every fixture
   drift is 0.001, below the 0.010818 screen, so the max() branch is never
   exercised; it passes against max(), against the bare constant, and
   against min(). Add a window with drift > 0.010818 and assert BOTH
   branches. This is the one clause D-110 exists to protect.
3. Derive the synthetic acceptance artifact through the D-116 emitter (or
   NEEDS_SCOPE it) — do not ship a parent whose bound is not derivable
   from its own prior set.
4. Name L5 explicitly (a test that a candidate under another window's
   runs_root cannot bracket this window, with and without a binding).
5. Per-window verdict issuance + committed-pin cadence across window
   boundaries (the nights are three separate closeouts, not one snapshot).
6. Add the positive count oracle (no-failure campaign ends at 36 valid,
   two short of the 38 trigger) + a NEEDS_SCOPE clause.
Remaining amendments 7-13 in OPUS-EXAM-U4-U8.md are adopted as written.

## U8 — readiness validator + runbook amendment: REWORK

The validator half is good (fail-closed with no warning tier, TOCTOU-safe
read-once-then-hash, closes register R6 and R7, resolves acceptance via
U2's registry). It is REWORKED for three independent reasons:

1. **The runbook edit would put contradictory normative instructions into
   a ratified operator document read at 2 a.m.**: §5B still licenses a
   cause-removal retry that a two-slot session CANNOT represent; the plan
   restates §8/§9/§11 orderings inside §5A (a clock-stabilization
   section); and it DROPS the mandatory 180 s settle from the very
   sequence its test would freeze. Restructure as additive
   "### D-117 §nn amendment" blocks per the runbook's own convention, and
   reconcile §5B (zero retries) or NEEDS_RULING it.
2. **The readiness gate is unbound and uncustodied** — the receipt goes to
   stdout and nowhere else, has no timestamp/TTL, is never referenced by
   the capability receipt, and the record's provenance plus its expected
   SHA are both operator-supplied. Every individual check is fail-closed;
   the gate as a whole is not.
3. **It is not implementable yet** (five unmet dependencies, five
   design-bearing open questions) and sequencing it now would invert the
   memo's dependency order, forcing U5-U7 to match a plan-tree contract
   invented by U8.

**Next action for U8 is NOT an implementation round.** It is: the two
rulings (zero-retry semantics; whether the readiness reason codes enter
the ratified refusal spec's S1 domain — an S4 cold-gate move if so), then
the U5-U7 plan-tree/launch-manifest contract.

## Note on the speculative implementations

U2/U4/U8 speculative implementations were launched BEFORE this
examination. They are evidence for the council, not landing candidates.
U4's output must be re-gated against amendments 1-6 above; U8's output is
superseded by the REWORK verdict and must not be landed on the runbook.
