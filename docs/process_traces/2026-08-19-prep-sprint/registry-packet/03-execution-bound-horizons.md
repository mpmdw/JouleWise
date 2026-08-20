# V3 — the 14 missing EXECUTION_BOUND horizons (`evidence_policies[].horizon_ns`)

## Field

`freeze_evidence_lifecycle.evidence_policies[i].horizon_ns` — an integer
nanosecond validity horizon, one per evidence kind.

## Schema requirement (validator code, verbatim)

```python
horizon = policy["horizon_ns"]
if not (
    horizon is None
    or (isinstance(horizon, int) and not isinstance(horizon, bool) and horizon > 0)
    or (
        isinstance(horizon, str)
        and horizon.startswith(_R1_ED_RESERVED_PREFIX)
    )
):
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"R1 evidence_policies[{index}].horizon_ns is invalid",
    )
```
(`joulewise/arm_readiness.py:1585-1598`)

and the class-conditional rule (same block quoted in `02-…`, `:1609-1631`):
`RE_DERIVABLE` ⇒ `horizon_ns` MUST be `null`; `TIME_BOUND`,
`SESSION_STATE_BOUND`, `EXECUTION_BOUND` ⇒ MUST be a **positive** integer.

Definitions are keyed by policy id and must not conflict:

```python
prior = definitions_by_policy_id.setdefault(
    policy["freshness_policy_id"], definition
)
if prior != definition:
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        "one freshness policy ID has conflicting definitions",
    )
```
(`joulewise/arm_readiness.py:1642-1655`)

Every one of the 35 rows must map to a policy id whose kind-set agrees:

```python
expected_policy_ids = {
    policy_id_by_kind.get(kind)
    for kind in row["required_evidence_kinds"]
}
if (
    None in expected_policy_ids
    or len(expected_policy_ids) != 1
    or policy_id_by_row[row["row_id"]] not in expected_policy_ids
):
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"R1 row {row['row_id']} does not match its evidence policy",
    )
```
(`joulewise/arm_readiness.py:1913-1928`)

## Which 14 — derived, and it reconciles exactly

D-139 A3 approved *"the existing operational horizons — 20-minute volatile /
six-hour procedural — carry forward as the approved freshness defaults"*
(`docs/decision_log.md:10078-10083`). Those two constants are:

```python
# Live machine state can change between authoring and ARM consumption.  Keep
# that unavoidable TOCTOU window bounded to the expected arm-sequence length.
_VOLATILE_EVIDENCE_VALIDITY_NS = 20 * 60 * 1_000_000_000
_NONVOLATILE_EVIDENCE_VALIDITY_NS = 6 * 60 * 60 * 1_000_000_000
```
(`joulewise/arm_readiness_evidence_t0.py:47-50`), dispatched by
`_validity_horizon_ns` (`:1757-1767`) over exactly these sets:

- `_VOLATILE_EVIDENCE_KINDS` (`:102-114`): `BACKUP_PREFLIGHT`, `CLOCK_PROBE`,
  `LAUNCH_RECIPE`, `MAINTENANCE_CENSUS`, `MACHINE_PREFLIGHT`,
  `POWERMETRICS_PROBE`, `POWER_PREFLIGHT`, `PROCESS_CENSUS`, `ROOT_PREFLIGHT`
- `_NONVOLATILE_EVIDENCE_KINDS` (`:115-122`): `CLOCK_ATTESTATION`,
  `LEDGER_RESERVATION`, `OFFLINE_INPUT_INVENTORY`, `TERMINAL_REVIEW`

Intersecting the 13 T-0-horizoned kinds with the 16 EXECUTION_BOUND kinds
gives exactly **two** — `OFFLINE_INPUT_INVENTORY` and `TERMINAL_REVIEW` (both
6-hour). 16 − 2 = **14**, which reproduces the commit body's count
(`35badb4`: *"the 14 missing EXECUTION_BOUND horizons"*) mechanically. Seats
should re-derive this independently; it is the packet's arithmetic, not a
quotation.

**The 14 with no approved horizon:**
`ACCEPTANCE_OWNER`, `ACCEPTANCE_SUCCESSOR`, `DRY_RUN_REHEARSAL`,
`ESTIMATOR_IDENTITY`, `GIT_CHECKOUT`, `IDENTITY_PIN_PROJECTION`,
`MINT_TRUST`, `MULTICELL_MINT`, `PACK_AUTHENTICATION`,
`PRIVILEGE_INSTALLATION`, `REASON_CODE_COVERAGE`, `RECEIPT_ORACLE`,
`RECOVERY_LEDGER_TEST`, `THREE_WINDOW_REGRESSION`.

## Proposed value

**None on the record.** This is the second of the two non-proposed values.

The reservation's origin, from the consult's reserved list:

> "Rule the short horizons, arm-to-consume safety margin, and which volatile
> predicates must be re-probed at consumption."
> — `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:248`

and its own analysis of why a blanket short horizon is wrong:

> "'Less than 24 hours old' does not establish that power, clock, process or
> root state is still true at launch."
> — same file, `:236`

Contract statement of the requirement:

> "Per-row policies, generic execution horizons, ARM capability horizon,
> arm-to-consume budget, and execution-environment comparison semantics must
> all be resolved in the single registry."
> — `docs/decision_log.md:9306-9308` (R1 clause 7)

The only value in the tree is again a fixture: `resolved_r1_row_registry()`
sets every non-`RE_DERIVABLE` policy to `1_200_000_000_000` ns (20 min) and a
test asserts it (`tests/test_arm_readiness_evidence.py:104-110`, assertion at
`:549-555`). **That is a fixture uniformity, not a ruling** — it exists to
exercise the validator, and adopting it by default would be exactly the error
the consult warned against.

## Alternatives a seat should argue

1. **Uniform 20 minutes for all 14** (the fixture's shape, and the
   volatile-tier value D-139 approved elsewhere). Simple, defensible as
   "bounded to the expected arm-sequence length" (`_evidence_t0.py:47-48`),
   but forces re-authoring of desk-derivable evidence within a 20-minute
   window of ARM — operationally brutal for kinds like `ESTIMATOR_IDENTITY`
   or `GIT_CHECKOUT` that are functions of committed bytes.
2. **Uniform 6 hours for all 14** (the procedural tier). Matches the two
   EXECUTION_BOUND kinds that already have an approved horizon
   (`OFFLINE_INPUT_INVENTORY`, `TERMINAL_REVIEW`) — arguably the strongest
   precedent-based argument, since those two ARE EXECUTION_BOUND and Ed
   already approved 6 h for them.
3. **Two tiers by what the evidence is about:** desk/byte-derived kinds
   (`ACCEPTANCE_*`, `ESTIMATOR_IDENTITY`, `GIT_CHECKOUT`,
   `IDENTITY_PIN_PROJECTION`, `PACK_AUTHENTICATION`, `RECEIPT_ORACLE`,
   `REASON_CODE_COVERAGE`) at 6 h; machine-touching kinds
   (`DRY_RUN_REHEARSAL`, `PRIVILEGE_INSTALLATION`, `MINT_TRUST`,
   `MULTICELL_MINT`, `RECOVERY_LEDGER_TEST`, `THREE_WINDOW_REGRESSION`) at
   20 min. Requires two policy ids and a row-map that agrees (`:1913-1928`).
4. **Per-kind horizons** — maximum fidelity, maximum surface. Note the
   validator forbids two kinds sharing a policy id with different
   definitions, so per-kind means 14 policy ids and 14 row-map entries to get
   right.

**A seat must cost each option in window terms.** The horizon is what forces
re-authoring before a window; a 20-minute EXECUTION_BOUND horizon combined
with D-078 no-retry is an operational hazard, not just a number.

## Evidence each seat should check

- **Contract lens:** that the chosen tiering satisfies the one-definition-per-
  policy-id rule (`:1642-1655`) and the per-row agreement rule
  (`:1913-1928`) against the actual 35 rows and their
  `required_evidence_kinds` in
  `configs/arm_readiness/d117_row_registry_v1.json`. Several rows require a
  single kind, but the mapping must be checked row by row — a row whose kinds
  span two policy ids fails `len(expected_policy_ids) != 1`.
- **Execution lens:** build the candidate registry, run
  `readiness.validate_registry` on it, then run the full
  `tests/test_arm_readiness_evidence.py` and
  `tests/test_arm_readiness_registry` modules. Then walk one real
  author→arm sequence and measure the wall-clock gap the horizon has to
  cover, against the arm-sequence length the comment claims.
- **Both:** the interaction with the ARM capability horizon and the
  arm-to-consume budget (`05-…`) — three clocks that must nest, and nothing
  in the record says how.
