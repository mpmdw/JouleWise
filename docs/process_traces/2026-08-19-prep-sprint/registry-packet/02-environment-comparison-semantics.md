# V2 — `evidence_policies[].environment_comparison` (16 EXECUTION_BOUND kinds)

**This is the value the install actually died on.** The 2026-08-18 morning
packet names it as *the* blocker:

> "the R1 registry install correctly BLOCKED on your reserved
> environment-comparison semantics (five-item NEEDS_RULING recorded…)"
> — `docs/process/ed-morning-packet-2026-08-18.md:18`

## Field

`freeze_evidence_lifecycle.evidence_policies[i].environment_comparison` — a
string, one per evidence kind. Sixteen of the twenty-nine kinds are
`EXECUTION_BOUND` and each needs a non-`NOT_APPLICABLE` value.

There is **no `ED_RESERVED:` placeholder for this field** — the placeholder
registry ships `"evidence_policies": []` (`joulewise/arm_readiness.py:531`),
so the reservation is enforced by an empty **code** allowlist instead (below).

## Schema requirement (validator code, verbatim)

Per-policy key set:

```python
_R1_EVIDENCE_POLICY_KEYS = {
    "kind",
    "freshness_class",
    "freshness_policy_id",
    "horizon_ns",
    "environment_comparison",
}
```
(`joulewise/arm_readiness.py:490-496`)

Class-conditional contradiction check:

```python
if code_class == "RE_DERIVABLE" and (
    horizon is not None or environment_comparison != "NOT_APPLICABLE"
):
    contradictory_policies.append(
        f"{kind!r} RE_DERIVABLE must have horizon_ns=null and "
        "environment_comparison=NOT_APPLICABLE"
    )
elif code_class in {"TIME_BOUND", "SESSION_STATE_BOUND"} and (
    not positive_or_reserved_horizon
    or environment_comparison != "NOT_APPLICABLE"
):
    contradictory_policies.append(
        f"{kind!r} {code_class} must have a positive horizon and "
        "environment_comparison=NOT_APPLICABLE"
    )
elif code_class == "EXECUTION_BOUND" and (
    not positive_or_reserved_horizon
    or environment_comparison == "NOT_APPLICABLE"
):
    contradictory_policies.append(
        f"{kind!r} EXECUTION_BOUND must have a positive horizon and "
        "an applicable environment comparison"
    )
```
(`joulewise/arm_readiness.py:1609-1631`), raised as
`readiness_row_registry_mismatch` with `"UNKNOWN_POLICY: contradictory
lifecycle fields: …"` at `:1791-1794`.

**The class is code-owned, not registry-owned.** The single authority table:

```python
# R1 S2: this is the sole freshness-class authority.  Registries name policy
# IDs and class-specific parameters, but can neither introduce an evidence
# kind nor choose its class.
R1_EVIDENCE_FRESHNESS_CLASSES = { … }
```
(`joulewise/arm_readiness.py:671-707`), with a module-import assertion that
every kind is covered (`:708-712`).

### The gate that is actually shut

Registry-side validation will happily accept any string. The **issuance**
path will not:

```python
if (
    code_class == "EXECUTION_BOUND"
    and policy["environment_comparison"]
    not in _SUPPORTED_ENVIRONMENT_COMPARISONS
):
    entry = _readiness._r1_refusal_entry(governed, "UNKNOWN_POLICY")
    raise _refuse(
        kind,
        str(entry["code"]),
        "execution-environment comparison semantics remain Ed-reserved",
    )
```
(`joulewise/arm_readiness_evidence.py:1785-1796`)

against

```python
# Ed has not ruled the comparison semantics yet.  An empty implementation
# allowlist is intentional: recording exists now; issuance stays fail closed.
_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset()
```
(`joulewise/arm_readiness_evidence.py:117-119`)

**Consequence the council must internalise: this value cannot be installed by
editing JSON alone.** The ruling must also add the approved token(s) to
`_SUPPORTED_ENVIRONMENT_COMPARISONS`, i.e. the install is a **code + config +
test** transaction, not a config transaction.

## The 16 EXECUTION_BOUND kinds (derived from `R1_EVIDENCE_FRESHNESS_CLASSES`, `:677-705`)

`ACCEPTANCE_OWNER`, `ACCEPTANCE_SUCCESSOR`, `DRY_RUN_REHEARSAL`,
`ESTIMATOR_IDENTITY`, `GIT_CHECKOUT`, `IDENTITY_PIN_PROJECTION`,
`MINT_TRUST`, `MULTICELL_MINT`, `OFFLINE_INPUT_INVENTORY`,
`PACK_AUTHENTICATION`, `PRIVILEGE_INSTALLATION`, `REASON_CODE_COVERAGE`,
`RECEIPT_ORACLE`, `RECOVERY_LEDGER_TEST`, `TERMINAL_REVIEW`,
`THREE_WINDOW_REGRESSION`.

Of these, **six already record** an environment fingerprint today:

```python
_ENVIRONMENT_FINGERPRINT_KINDS = frozenset(
    {
        "MINT_TRUST",
        "MULTICELL_MINT",
        "PACK_AUTHENTICATION",
        "REASON_CODE_COVERAGE",
        "RECOVERY_LEDGER_TEST",
        "THREE_WINDOW_REGRESSION",
    }
)
```
(`joulewise/arm_readiness_evidence.py:107-116`)

Recording is live; **comparison** is what is reserved. R1 amendment clause 7:

> "The six ruled probe/suite kinds record interpreter, platform,
> non-repository `sys.path` descriptors/digests, and (for
> `PACK_AUTHENTICATION`) inherited-environment value digests now. Because Ed
> has not ruled comparison semantics, the implementation comparison allowlist
> is intentionally empty and an R1 author refuses before writing any output
> through the registry's `UNKNOWN_POLICY` role."
> — `docs/decision_log.md:9306-9316`

## Proposed value

**None. This value has no proposal on the record** — it is one of the two
non-proposed values the council was convened to supply.

The consult that opened the reservation framed the question, and explicitly
refused to let a time limit stand in for it:

> "Decide whether focused-test evidence binds a controlled execution-environment
> fingerprint or is treated solely as reviewed-byte proof. **A time limit is
> not a substitute for that decision.**"
> — `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:249`

Its cold-gate ruling made the reservation operational rather than silent:

> "Caveat (real, and correctly reserved to Ed): the four suite-running kinds
> plus the two probe-running kinds attest 'these committed bytes pass these
> checks as executed in the authoring environment.' The interpreter and
> platform are implicit unrecorded dependencies. Amendment 5 makes the
> reservation operational instead of silent."
> — `coldgate-adjudicator-ruling.md:30`

> "**Execution-environment facts recorded now, comparison semantics ruled by
> Ed.** The six probe/suite-running kinds record a derived (never entered)
> interpreter/platform fingerprint as receipt facts immediately; ARM's
> treatment of divergence is Ed's reserved ruling."
> — `coldgate-adjudicator-ruling.md:69`

Ed has twice declined: D-139 A3 — *"The environment-fingerprint comparison
semantics remain an open Ed ruling (the R1 fail-closed seam stands)"*
(`docs/decision_log.md:10084-10086`) — and again on the carried-forward list,
*"Environment-fingerprint comparison semantics (R1 fail-closed seam holds)"*
(`docs/process/ed-morning-packet-2026-08-18.md`, §6).

The only shape hint in the codebase is the test fixture's placeholder token
`"test-only"` (`tests/test_arm_readiness_evidence.py:112-116`) — a fixture,
not a proposal.

## Alternatives a seat should argue

1. **`EXACT_MATCH`** — any divergence in the recorded fingerprint
   (interpreter version, platform, non-repository `sys.path` descriptors and
   digests) refuses at ARM. Maximally conservative; makes any OS or Python
   update invalidate every EXECUTION_BOUND receipt, i.e. forces a full
   re-authoring before each window. Cost is real: 16 of the 35 rows.
2. **`INTERPRETER_AND_PLATFORM_ONLY`** — compare interpreter identity and
   platform, ignore `sys.path` descriptors. Cheaper; concedes that an
   inherited-environment change can go unnoticed.
3. **`RECORD_ONLY` / `REVIEWED_BYTE_PROOF`** — record the fingerprint,
   compare nothing; treat the evidence as proof about committed bytes, not
   about an environment. This is the consult's second branch ("treated solely
   as reviewed-byte proof") and is the **honest** reading of what these
   receipts actually attest. It converts the seam into a registered
   limitation rather than a mechanism.
4. **Per-kind mixture** — `EXACT_MATCH` for the six fingerprint-recording
   kinds, `RECORD_ONLY` for the other ten (which record no fingerprint today
   and would need new derivation work to compare anything). Note the
   validator permits distinct `environment_comparison` values per kind but
   requires **one policy id per definition** (`:1642-1655`), so a mixture
   means multiple `freshness_policy_id`s and the per-row policy map must
   agree row-by-row (`validate_registry` `:1892-1928`).

**Whatever is ruled, a seat must state the code delta** — the exact
membership of `_SUPPORTED_ENVIRONMENT_COMPARISONS` — because an unmatched
token leaves the fail-closed seam shut and the install is a no-op with extra
bytes.

## Evidence each seat should check

- **Contract lens:** that the ruled token set is closed under
  `_r1_policies_for_kinds` for all 16 kinds
  (`arm_readiness_evidence.py:1770-1800`); that `NOT_APPLICABLE` remains
  forbidden for EXECUTION_BOUND and mandatory for the other three classes
  (`arm_readiness.py:1609-1631`); that the ruling does not smuggle a class
  override — the registry "can neither introduce an evidence kind nor choose
  its class" (`:671-675`), enforced by the `class_mismatches` path at
  `:1573-1580` and `:1786-1790`.
- **Execution lens:** with the ruled token installed, author evidence for a
  `_v3` pack in a scratch clone and confirm the six fingerprint-recording
  kinds produce a comparison result rather than a refusal; then perturb the
  interpreter (e.g. a different `python3` minor) and confirm the ruled
  disposition actually fires. `_r1_policies_for_kinds` has an early
  CLASS_MISMATCH inspection path (`:1723-1755`) that must not be bypassed.
- **Both:** whether the ruling implies re-authoring any already-issued
  evidence. The three `_v3` packs' evidence was authored 2026-08-19 under the
  **v1** registry — no R1 policy applied. Installing a comparison policy
  retroactively is not the same as having authored under it.
