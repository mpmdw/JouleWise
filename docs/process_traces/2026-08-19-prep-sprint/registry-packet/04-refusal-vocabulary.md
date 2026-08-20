# V4 — `refusal_vocabulary` code spellings and type labels (8 roles)

## Field

`freeze_evidence_lifecycle.refusal_vocabulary` — a list of
`{role, code, type}` entries, exactly one per role, covering all eight
mandatory roles.

Placeholder in code:

```python
"refusal_vocabulary": [
    {
        "role": role,
        "code": f"ED_RESERVED:refusal-code:{role.lower()}",
        "type": "ED_RESERVED:refusal-type",
    }
    for role in sorted(R1_REFUSAL_ROLES)
],
```
(`joulewise/arm_readiness.py:546-555`)

## Schema requirement (validator code, verbatim)

Role census is code-owned and closed:

```python
R1_REFUSAL_ROLES = frozenset(
    {
        "CLASS_MISMATCH",
        "DEPENDENCY_CHANGED_SET",
        "DEPENDENCY_MANIFEST",
        "FAMILY_PUBLICATION",
        "SUCCESSOR_CHAIN",
        "TEMPORAL_BUDGET",
        "UNKNOWN_POLICY",
        "V1_GRANDFATHERING",
    }
)
```
(`joulewise/arm_readiness.py:488-498`)

Entry key set: `_R1_REFUSAL_ENTRY_KEYS = {"role", "code", "type"}` (`:525`).

Code spelling and type-label constraints:

```python
if not code.startswith(_R1_ED_RESERVED_PREFIX) and re.fullmatch(
    r"[a-z][a-z0-9_]*", code
) is None:
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"R1 refusal_vocabulary[{index}].code is invalid",
    )
if not reason_type.startswith(_R1_ED_RESERVED_PREFIX) and reason_type not in {
    "STRUCTURE",
    "CUSTODY",
    "GIT",
    "LIFECYCLE",
    "POLICY",
    "IDENTITY",
    "ENVIRONMENT",
}:
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"R1 refusal_vocabulary[{index}].type is invalid",
    )
```
(`joulewise/arm_readiness.py:1760-1779`)

Completeness and uniqueness:

```python
if roles != sorted(R1_REFUSAL_ROLES) or len(codes) != len(set(codes)):
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        "R1 refusal vocabulary must register every role exactly once",
    )
```
(`joulewise/arm_readiness.py:1781-1785`)

So: **8 entries, sorted by role, distinct `snake_case` codes, `type` drawn
from a closed 7-member enum.**

## Why the spellings are reserved (contract text)

> "**D-078 lifecycle refusal registry is structurally complete before
> issuance.** Its eight mandatory roles are `CLASS_MISMATCH`,
> `DEPENDENCY_CHANGED_SET`, `DEPENDENCY_MANIFEST`, `FAMILY_PUBLICATION`,
> `SUCCESSOR_CHAIN`, `TEMPORAL_BUDGET`, `UNKNOWN_POLICY`, and
> `V1_GRANDFATHERING`. **Exact spellings and type labels remain Ed-reserved
> under R1 clause 6 and therefore come only from that authenticated
> registry.** The checked-in placeholder uses explicit `ED_RESERVED:` values
> and refuses issuance/consumption; **no placeholder is a reason code**."
> — `docs/decision_log.md:9296-9304` (R1 clause 6)

Named as unruled by the install refusal: *"…it did not approve those
comparisons, the 14 missing EXECUTION_BOUND horizons, **the
refusal-vocabulary spellings**, the arm-to-consume budget, or the
family-publication marker schema"* (`git show 35badb4`, commit body).

## Proposed value

**None on the record.** The one concrete example is the test fixture, which
uses a deliberately non-production prefix:

```python
"refusal_vocabulary": [
    {
        "role": role,
        "code": f"test_r1_{role.lower()}",
        "type": "POLICY",
    }
    for role in sorted(readiness.R1_REFUSAL_ROLES)
],
```
(`tests/test_arm_readiness_evidence.py:78-86`)

An obvious production candidate — and the seats should treat it as a
candidate, not a default — is the same shape without the `test_` prefix,
typed per role rather than uniformly `POLICY`.

## Why these strings are load-bearing (not cosmetic)

The registry codes are what the production refusal paths actually emit:

```python
entry = _readiness._r1_refusal_entry(governed, "UNKNOWN_POLICY")
raise _refuse(
    kind,
    str(entry["code"]),
    f"registry has no unique lifecycle policy for {kind}",
)
```
(`joulewise/arm_readiness_evidence.py:1765-1770`; the CLASS_MISMATCH twin at
`:1755-1761`, and the EXECUTION_BOUND comparison refusal at `:1785-1796`)

There is also an inspection path that reads the raw `CLASS_MISMATCH` entry
*before* full validation, expressly to preserve the registry-owned spelling:

```python
# Preserve the registry-owned refusal spelling while refusing before the
# general registry validator can collapse a class override into a schema
# error.  This inspection grants no policy authority: the expected value
# comes only from the code table.
```
(`joulewise/arm_readiness_evidence.py:1723-1727`)

So a ruled code becomes part of the project's externally visible refusal
vocabulary — it will appear in receipts, refusal logs, and the paper's
refusal census. It is a naming decision with publication reach.

## Alternatives a seat should argue

1. **`r1_<role_lowercase>`** — e.g. `r1_class_mismatch`, `r1_successor_chain`.
   Namespaced, greppable, obviously R1-owned.
2. **Reuse the existing `readiness_*` family** — e.g.
   `readiness_row_registry_mismatch` already exists as a
   `STRUCTURE_REASON_CODES` member (`arm_readiness.py:118-122`). Argues for
   one vocabulary rather than two. Risk: collision with codes the validator
   does not own, and loss of the ability to distinguish an R1 lifecycle
   refusal from a D-134 structural one in the census.
3. **`evidence_author_*`** — matches the codes already emitted around these
   sites (e.g. `evidence_author_lifecycle_registry_unresolved`,
   `arm_readiness_evidence.py:1761`). Consistent with the surrounding module;
   less obviously registry-owned.
4. **Type labels: uniform vs per-role.** Uniform `POLICY` is the fixture's
   choice. A per-role typing is more informative and the enum supports it:
   `CLASS_MISMATCH`→`POLICY`, `DEPENDENCY_CHANGED_SET`/`DEPENDENCY_MANIFEST`
   →`LIFECYCLE`, `FAMILY_PUBLICATION`→`CUSTODY` or `IDENTITY`,
   `SUCCESSOR_CHAIN`→`IDENTITY`, `TEMPORAL_BUDGET`→`LIFECYCLE`,
   `UNKNOWN_POLICY`→`POLICY`, `V1_GRANDFATHERING`→`LIFECYCLE`. A seat should
   argue whether the extra dimension earns its keep or just invites drift.

## Evidence each seat should check

- **Contract lens:** all 8 roles present exactly once and **sorted**
  (`:1781-1785` compares against `sorted(R1_REFUSAL_ROLES)`); every code
  matches `[a-z][a-z0-9_]*`; every type in the 7-member enum; no proposed
  code collides with an existing reason code anywhere in the repo
  (`grep -rn "<code>" joulewise/ tests/`).
- **Execution lens:** force each of the eight roles to fire and confirm the
  emitted code is the registry's, not a hardcoded fallback. `_r1_refusal_entry`
  (`arm_readiness.py:1821-1836`) raises `ValueError` for an unknown role and
  `readiness_row_registry_mismatch` for a non-unique one — both should be
  exercised.
- **Both:** whether any ruled code needs to appear in the paper's refusal
  census or in `docs/` reason-code documentation; a code that is emitted but
  undocumented is a documentation defect the docs-freshness contract may
  catch.
