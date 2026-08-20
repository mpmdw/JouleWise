# V5 — `arm_policy.arm_to_consume_budget_ns`

## Field

`freeze_evidence_lifecycle.arm_policy.arm_to_consume_budget_ns` — an integer
nanosecond budget bounding the gap between ARM and consumption.

Placeholder in code:

```python
"arm_policy": {
    "capability_horizon_ns": "ED_RESERVED:arm-capability-horizon-ns",
    "arm_to_consume_budget_ns": "ED_RESERVED:arm-to-consume-budget-ns",
},
```
(`joulewise/arm_readiness.py:533-536`)

## Schema requirement (validator code, verbatim)

```python
_R1_ARM_POLICY_KEYS = {"capability_horizon_ns", "arm_to_consume_budget_ns"}
```
(`joulewise/arm_readiness.py:517`)

```python
arm_policy = _require_exact_keys(
    registry["arm_policy"], _R1_ARM_POLICY_KEYS, "R1 arm_policy"
)
for name in sorted(_R1_ARM_POLICY_KEYS):
    item = arm_policy[name]
    if not (
        (isinstance(item, int) and not isinstance(item, bool) and item > 0)
        or (isinstance(item, str) and item.startswith(_R1_ED_RESERVED_PREFIX))
    ):
        raise ArmReadinessError(
            "readiness_row_registry_mismatch", f"R1 arm_policy.{name} is invalid"
        )
```
(`joulewise/arm_readiness.py:1682-1694`)

Constraint: **a strictly positive integer** (booleans explicitly excluded).
No upper bound, no relation to any other field is enforced by the validator.

**Note the sibling.** `capability_horizon_ns` sits in the same exact-key
mapping and carries the same `ED_RESERVED:` placeholder, but the install
refusal's five-item list names **only** `arm_to_consume_budget_ns`. Its
disposition is unresolved on the record — see `08-open-items.md` OPEN-ITEM 3.
The registry will not load with `capability_horizon_ns` unresolved, so the
council must rule it regardless of which list it belongs to.

## Why it is reserved

Reserved-list origin:

> "Rule the short horizons, **arm-to-consume safety margin**, and which
> volatile predicates must be re-probed at consumption."
> — `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:248`

Contract requirement:

> "Per-row policies, generic execution horizons, **ARM capability horizon,
> arm-to-consume budget**, and execution-environment comparison semantics must
> all be resolved in the single registry."
> — `docs/decision_log.md:9306-9308` (R1 clause 7)

Plan-consult item-by-item approval list:

> "2. **Horizons, ARM-to-consume budget, and which volatile predicates re-probe
> at consumption.**"
> — `docs/process_traces/2026-08-16-phase2-plan-consult/consult.md:373`

Named as unruled by the install refusal: *"…nor the refusal-vocabulary
spellings, **the arm-to-consume budget**, or the family-publication marker
schema"* (`git show 35badb4`, commit body).

## Proposed value

**None on the record.** The test fixture uses `60_000_000_000` (60 s) for the
budget and `300_000_000_000` (300 s) for the capability horizon
(`tests/test_arm_readiness_evidence.py:59-62`) — fixture values chosen to
exercise the validator, not a proposal.

## Exactly what the number does (this field HAS a live consumer)

Unlike the successor-policy strings, `arm_to_consume_budget_ns` is read by
production code — the temporal-budget gate:

```python
"""Evaluate the TIME_BOUND T-0 set against the governed consume budget."""

governed = validate_r1_lifecycle_registry(registry)
budget = governed["arm_policy"]["arm_to_consume_budget_ns"]
if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        "R1 arm-to-consume budget remains unresolved",
    )
deadlines: list[int] = []
for receipt in evidence_receipts:
    kind = receipt.get("kind")
    if R1_EVIDENCE_FRESHNESS_CLASSES.get(kind) != "TIME_BOUND":
        continue
    …
earliest = min(deadlines)
if earliest - now_monotonic_ns < budget:
    raise EvidenceLifecycleError(
        governed,
        "TEMPORAL_BUDGET",
        "T-0 evidence lifetime cannot cover the governed arm-to-consume budget",
    )
```
(`joulewise/arm_readiness.py:3299-3340`)

**Read the predicate carefully.** The gate refuses when the *remaining* life
of the earliest-expiring TIME_BOUND receipt is **less than** the budget. So a
LARGER budget is STRICTER: it demands more remaining evidence life at arm
time. This inverts the naive reading of "budget" as permissiveness, and any
seat that proposes a number must state which direction it believes it is
moving the gate.

Note also the deliberate class restriction, matching R1 clause 7 — *"The
temporal-budget gate explicitly evaluates the `TIME_BOUND` T-0 set;
session-state and execution deadlines are not silently substituted for that
set"* (`docs/decision_log.md:9316-9318`).

The sibling `capability_horizon_ns` has its own live consumer — it sets the
ARM receipt's validity:

```python
arm_horizon_ns = (
    int(lifecycle_registry["arm_policy"]["capability_horizon_ns"])
    if lifecycle_registry is not None
    else validity_ns
)
valid_until = min(
    [evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations]
)
```
(`joulewise/arm_readiness.py:6235-6242`), enforced downstream by
*"consumption occurred after the arm validity horizon"* (`:7913`).

**Both numbers are claim-integrity parameters, not ergonomics knobs:**
together they bound how stale the machine-state evidence may be at the moment
power is actually sampled.

The T-0 horizon they must nest with:

```python
# Live machine state can change between authoring and ARM consumption.  Keep
# that unavoidable TOCTOU window bounded to the expected arm-sequence length.
_VOLATILE_EVIDENCE_VALIDITY_NS = 20 * 60 * 1_000_000_000
```
(`joulewise/arm_readiness_evidence_t0.py:47-49`)

## Alternatives a seat should argue

Given the inverted predicate (`earliest_deadline − now < budget` ⇒ refuse),
the budget is best read as **"the minimum remaining T-0 evidence life
required at arm time"**:

1. **Small (e.g. 60 s, the fixture value).** Permissive: arming succeeds with
   a minute of evidence life left, and the measurement may begin on evidence
   that expires almost immediately. Weakest claim posture.
2. **Sized to the measured arm→consume gap** (the consult's "safety
   margin" reading). Requires the measurement; see the execution-lens item
   below. The comment at `_evidence_t0.py:47-48` asserts the window is
   "bounded to the expected arm-sequence length" but **no measurement of that
   length is cited anywhere in the record**.
3. **Sized to the full window duration.** If the intent is that TIME_BOUND
   evidence stays true for the whole measurement, the budget must cover the
   window, not just the arm ceremony. Under the 20-minute volatile horizon
   this is *infeasible* for a multi-hour window — which is itself a finding
   the council should surface rather than paper over.
4. **Longer budget + a consumption-edge re-probe set.** The consult pairs the
   budget with *"which volatile predicates must be re-probed at
   consumption"*. A long budget is only defensible with re-probing. **That
   re-probe set is not itself among the five and is not resolvable from this
   packet** (OPEN-ITEM 4).

## Evidence each seat should check

- **Contract lens:** that the ruled budget is **strictly less than** the
  smallest `horizon_ns` assigned to any `TIME_BOUND` kind — otherwise
  `earliest − now < budget` is true the instant the evidence is authored and
  every arm refuses. The validator enforces positivity only (`:1682-1694`),
  so this is a hand-checked invariant. The TIME_BOUND kinds are
  `BACKUP_PREFLIGHT`, `CLOCK_ATTESTATION`, `CLOCK_PROBE`, `MACHINE_PREFLIGHT`,
  `MAINTENANCE_CENSUS`, `POWERMETRICS_PROBE`, `POWER_PREFLIGHT`,
  `PROCESS_CENSUS` (`R1_EVIDENCE_FRESHNESS_CLASSES`, `:677-707`).
- **Execution lens:** measure a real author→arm→consume sequence at the
  measurement checkout (the dress-rehearsal card,
  `docs/process/rehearsal-operator-card.md`, walks E-4→E-9 +
  author→arm→verify→consume) and report the observed gap distribution. A
  budget ruled below the observed gap turns every window into a refusal;
  D-078 no-retry makes that a lost window, not a retry.
- **Both:** the D-149 interaction. Standing conditional T-0 GO
  (`docs/decision_log.md`, D-149) makes windows lead-scheduled and unattended;
  the arm-to-consume budget is the parameter that decides whether an
  unattended GO can still be consumed when the machine gets to it. Rule it
  with the automation in view, not the manual ceremony.
- **Both:** `capability_horizon_ns` must be ruled in the same transaction
  even though it is not on the five-item list — the registry will not load
  otherwise (`_r1_contains_reserved`, `:1501-1508` + `:1795-1804`).
