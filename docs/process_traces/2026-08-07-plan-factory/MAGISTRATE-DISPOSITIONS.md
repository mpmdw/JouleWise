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

## PROBES — ACCEPT WITH AMENDMENTS (22 named; full list in OPUS-EXAM-PROBES-PROSE.md)

Probe A (spec-decode pilot) verified executable in principle: every cited
mlx_lm CLI flag exists at the pin, the byte-identity check is PROVABLY
sound (acceptance is exact-match; --temp 0 gives argmax before any
sampler stage). Blocking amendments:
1. `$OUT` is referenced but never assigned — the commands as written fail
   on paste. (A1)
2. The decision rule can fire on contradictory evidence ("either 7B
   workload" closes even if the longer run shows a win) — make 7B/512
   governing; a split between lengths is INCONCLUSIVE. (A2)
3. **The chosen prompt is near-zero-entropy** ("count 1 to 1000"), so a
   0.5B draft hits near-ceiling acceptance: the probe measures spec
   decode's BEST case, the opposite of what a cheap kill-gate needs. Add
   a frozen free-prose governing cell; keep the list prompt as a labelled
   upper bound. (A3)
4. **Write the inference assumption down**: E = P̄·t, so CLOSE is licensed
   only under P̄_on >= R·P̄_off (near-certain, since spec-on does K draft
   forwards plus one (K+1)-position target forward per emitted token) —
   and state the converse, that a throughput WIN does not imply an energy
   win. (A4)
5. Fix the K-scope inconsistency (one K=3 result cannot close a
   K-manipulation program) and record the generation_tps first-token
   timer bias (~2% at N=128; conservative for CLOSE, anti-conservative
   for SURVIVES). (A5, A8)

Probe B (GPU cadence): the gate citation points at the WRONG DEVICE — the
cited line is in the NVIDIA 3050 section; the 3080 Ti section carries
R-006 (schedule only after Stage 3.0 verdicts + rehearsed runbook), so
the gate is not merely "does Ed have access" and whether a non-claim
characterization sits inside R-006 is a cold-gate question. Also: declare
the emitted bound an explicit UPPER bound (NVML cannot separate DVFS ramp
from sensor filter), and re-price ~1.5x (thermal re-admission is not
free). Note for the funding decision: a PASS at 100 ms already forbids
any stage shorter than ~400 ms under the plan's own rule — a boundary
PASS may be operationally useless.

## RESULTS_PROSE — examination VOID (stale input), re-run ordered

The examiner read the pre-fix truncated copy and reported "no
deliverable". Lead-verified against the completed file: the deliverable
EXISTS (35 [VALUE] placeholders across the three variants plus the §6
shell). Its derived ACCEPTANCE CONTRACT is adopted regardless and binds
the re-examination and the eventual prose:
- **P1** no summed-threshold leakage: F_cell + B_claim is DISCLOSURE
  only; the interval is never compared to the sum.
- **P5/P6** "not resolvable" is never written as "no difference"; and
  Variant B must SPLIT into B1 (floor-gate refusal) and B2
  (direction-gate refusal) because the sentences differ.
- **P7** Variant C's natural framing is FALSE: under D-095's
  cross_stack_armwise_max.v1, losing one floor window makes the contrast
  NOT EVALUABLE, not "partially claimable".
P1 and P7 are the two easiest variants to write fluently and the hardest
to write correctly; the summed-threshold error reads as doctrine
compliance to a skimming reviewer.

## REASON-CODE PLUMBING — ACCEPT WITH AMENDMENTS + two magistrate rulings

Verified good by the examiner against primary evidence: append-compatibility
is real (every reader is field-selective; rows lacking a field are already a
first-class case), the spec amendment is correctly treated as needing
ratification, and the backfill is custody-safe (append-only annotations keyed
by target row hash, conflicts refuse). Blocking amendments:

1. **PIN THE FIELD PLACEMENT: top-level sibling, NOT inside
   `idle_admission_core`.** The latter enters the six-key semantic-identity
   projection and would turn every same-basis re-verdict into
   `whole_window_verdict_conflict`. And the identity projection itself is
   NOT to be edited to accommodate the field — test the key list to freeze
   that.
2. **Golden characterization test BEFORE the refactor**: pin the existing
   `idle_admission_core_verdict` output by canonical sha256 first; all 13
   proposed tests cover only the new field, so the old behavior is currently
   unguarded days before the nights.
3. **Operational trap to encode**: replay verification against a HISTORICAL
   runs root APPENDS a campaign-log row and thereby breaks the issued
   artifacts' whole-file `campaign_log_sha256` pin. Any backfill or replay
   must work on copies, never on a pinned root.

**MAGISTRATE RULING A (the examiner flagged this as not lieutenant-decidable):
may the plumbing land ahead of the spec amendment? YES, SPLIT.** The CODE
plumbing (top-level, additive, append-compatible) may land ahead — it captures
evidence without changing any ratified semantics, and the three nights are
what make it urgent. The SPEC AMENDMENT (bringing the shadow codes into the
ratified spec's S1 domain) is a separate ratification and MUST NOT be assumed
by the code: until ratified, the new reason codes live in an explicitly
declared namespace OUTSIDE S1, frozen in one module tuple with an equality
test. Landing the code does not pre-empt the ratification; it must not read
as having done so.

**GOVERNANCE HOLE FOUND (record it, do not paper over it):** the ratified
`docs/phase_2/refusal_scope_spec.md` cites D-083 as its authority, but D-083
is the B3 disclosure ruling, and the decision log contains NO row for the
refusal-scope spec at all. The spec is operating as a ratified ONE-home with
no ledger entry behind it. This needs an Ed/cold-gate ruling on its actual
status before any S1-domain move is attempted — it is now item 8 on the
rulings list.

## PRICE-OF-NEVER-ZERO — ACCEPT WITH AMENDMENTS + one magistrate ruling

The arithmetic is VERIFIED CORRECT — the examiner reproduced the operator
order numerically against the retired mint (corner-widen -> guard ->
per-component family-matched allowance -> max). Blocking amendments:

1. **PAPER COLLISION (blocker).** `draft-v1.md` already has a section
   "Measured, never-zero drift allowance" — and that is the NEG-8 ENERGY
   allowance. The TIMING rule (D-102 pin 3) is introduced in §3. The plan
   titles its subsection "the never-zero rule" and hangs the forward
   reference off §4, so it would quantify one allowance while appearing to
   quantify the other — and that error survives into print. Retitle to name
   the TIMING allowance explicitly and attach it to §3's rule.
2. Read `0.010818` from the issued acceptance artifact rather than
   hardcoding it (this is the L4 defect class recurring).
3. Probe the re-reduction seam FIRST; if it will not take an external bound,
   the failure mode is a desk-script reimplementation of floor arithmetic
   feeding the paper — which is unacceptable.
4. The sensitivity artifact must be schema-INCOMPATIBLE with a floor artifact
   (it can never be mistaken for one); prefill cells have no diagnostic
   analogue (mint1 is decode-only) and wait on U3/U10.

**MAGISTRATE RULING B: may a counterfactual verdict appear in the paper? NO.**
The paper may report the floor ARITHMETIC with and without the never-zero
timing bound — that is a computed quantity from custodied inputs. It must NOT
tabulate a "verdict without" column: a verdict is an ISSUED artifact, and a
counterfactual verdict has no artifact behind it. State the arithmetic delta
and what it would imply; never render a verdict that was never issued.
