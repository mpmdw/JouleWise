# D-148.5 REGISTRY-VALUES COUNCIL PACKET — INDEX

**Assembled** 2026-08-19 (read-only) against `impl/r2-s0-mint-resolver`
@ `4597ad4`. Every quotation below is verbatim from that checkout; line
numbers are that checkout's.

*Base note:* the branch advanced to `7305e0d` during assembly (two prep
commits landed by the lead in the shared worktree).
`git diff --stat 4597ad4..7305e0d -- joulewise/ configs/ tests/ docs/decision_log.md docs/process/ RUN_STATE.md TASK_QUEUE.md docs/run_reports/ docs/process_traces/2026-08-19-r1-r2-codesign/`
shows a **single added file** (`docs/process/window-run-cards/shakedown-v3-first-light.md`)
and no change to any file this packet cites. **All line numbers are valid at
both heads.**

**Authority for convening:** D-148.5 — *"R1 row-registry reserved values →
COUNCIL (Ed defers; run the co-design/council pass when the Codex pool
returns, then proceed)"* (`docs/decision_log.md:171`). Queue row: A63
`REFREEZE-D147-CLOSE`, acceptance clause *"The council pass on the five R1
row-registry reserved values is custodied and its values installed"*
(`docs/process/state_kernel.json:2834`).

---

## 1. What the council must rule — and the counting discrepancy it must fix first

The record contains **two incompatible enumerations of "the five"**. This
packet reproduces both and rules on their **union of six values**. The
discrepancy is itself OPEN-ITEM 1 (`08-open-items.md`).

### Enumeration A — the authoritative five (the mechanical NEEDS_RULING)

The R1 registry install is runsheet **step 4**, and it **did not execute**.
The refusal is recorded in the commit body of `35badb4` — the ONE primary
source — and restated in the T10 session report §10 and the 2026-08-18
morning packet:

> **The runsheet's step-4 registry install is NOT executed — NEEDS_RULING.**
> The R1 row-registry schema admits no partial install (any remaining
> `ED_RESERVED:` placeholder makes the whole registry unloadable) and
> requires a resolved lifecycle policy for all 29 evidence kinds, of which 16
> are EXECUTION_BOUND and therefore need an `environment_comparison` whose
> implementation allowlist (`_SUPPORTED_ENVIRONMENT_COMPARISONS`) is
> deliberately EMPTY pending Ed. D-139 A3 approved the successor IDs, the
> freeze-0002 chain semantics, and the existing operational horizons; **it
> did not approve those comparisons, the 14 missing EXECUTION_BOUND horizons,
> the refusal-vocabulary spellings, the arm-to-consume budget, or the
> family-publication marker schema** (explicitly Ed-reserved by the
> runsheet's own step 5).
> — `git show 35badb4` (commit body, "Restore the R1 registry-driven
> successor-identity design (magistrate ruling)")

Restated in the report:

> "Five reserved items, recorded in the commit body and carried into the
> morning packet."
> — `docs/run_reports/2026-08-18-t10-session.md:753` (§10, heading at `:712`
> — *"…and a five-part registry NEEDS_RULING"*)

And in the packet Ed actually read:

> "the R1 registry install correctly BLOCKED on your reserved
> environment-comparison semantics (five-item NEEDS_RULING recorded, joins
> your list below)."
> — `docs/process/ed-morning-packet-2026-08-18.md:18`

And in the runsheet's own status line:

> "step 4 (R1 registry install) NEEDS_RULING on Ed-reserved values (five
> items, see the morning packet)"
> — `docs/process/phase2-transaction-runsheet.md:12-14`

**Enumeration A therefore is, in the commit body's own order:**

| # | Value | File |
|---|---|---|
| A1 | `environment_comparison` semantics for the 16 EXECUTION_BOUND kinds (+ the empty code allowlist) | `02-environment-comparison-semantics.md` |
| A2 | The 14 missing EXECUTION_BOUND horizons (`evidence_policies[].horizon_ns`) | `03-execution-bound-horizons.md` |
| A3 | Refusal-vocabulary spellings (`refusal_vocabulary[].code` / `.type`, 8 roles) | `04-refusal-vocabulary.md` |
| A4 | `arm_policy.arm_to_consume_budget_ns` | `05-arm-to-consume-budget.md` |
| A5 | `successor_policy.family_publication_marker_schema` | `06-family-publication-marker-schema.md` |

**Note what is NOT in Enumeration A: `successor_pack_ids`.** D-139 A3 had
already approved them (as the `_v2` ids), so on 2026-08-18 they were a closed
item.

### Enumeration B — the "three proposed / remaining two" framing

D-147's ruling reopened the pack IDs by superseding the family to `_v3`, and
recorded:

> "(3) R1 row-registry reserved values: R2 supplies three of the five
> (`successor_pack_ids` = the three `_v3` ids)."
> — `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:125-127`

Its source seat said both things in one breath:

> "if the registry install is scheduled before the `_v3` freeze, its
> `successor_pack_ids` reserved values must name the `_v3` ids. **That is one
> of the "R1 registry reserved values (five items)" already on Ed's list; R2
> supplies three of the five.**"
> — `docs/process_traces/2026-08-19-r1-r2-codesign/06-r2-design-opus.md:727-730`

RUN_STATE then carried enumeration B forward as the council's shape:

> "Registry-values council PACKET (D-148.5): the five reserved values — three
> proposed (= the three `_v3` pack ids for `successor_pack_ids`) — the
> remaining two enumerated FROM the R1-registry consult custody"
> — `RUN_STATE.md:34-38`

**The two enumerations cannot both be right.** Enumeration A's five do not
include `successor_pack_ids`; enumeration B counts three of its five as the
pack ids. Enumeration A is the one grounded in executed mechanism (a real
refusal, with the code cited); enumeration B is a seat's characterisation
that the ruling copied. **This packet's disposition: enumeration A is
authoritative, `successor_pack_ids` is a SIXTH value reopened by D-147, and
the council rules all six.** The council may overturn that disposition — but
it must rule the counting explicitly, because "install the five" is not an
executable instruction while two lists disagree.

---

## 2. File inventory

| File | Contents |
|---|---|
| `00-INDEX.md` | This file: authority, the counting discrepancy, inventory, reading order |
| `01-successor-pack-ids.md` | **V1** `successor_policy.successor_pack_ids` — the three `_v3` ids (PROPOSED) |
| `02-environment-comparison-semantics.md` | **V2** `evidence_policies[].environment_comparison` for 16 EXECUTION_BOUND kinds |
| `03-execution-bound-horizons.md` | **V3** the 14 missing `horizon_ns` values |
| `04-refusal-vocabulary.md` | **V4** the 8 refusal codes + type labels |
| `05-arm-to-consume-budget.md` | **V5** `arm_policy.arm_to_consume_budget_ns` |
| `06-family-publication-marker-schema.md` | **V6** `successor_policy.family_publication_marker_schema` |
| `07-council-brief.md` | Required outputs, seat roster, kernel-transaction discipline, the D-147 S5 carried limitation, the BLOCKER the seats must dispose of first |
| `08-open-items.md` | Everything unresolvable from the record |

**Reading order for a seat:** `00` → `07` (brief; contains the blocker) →
the value file(s) for its lens → `08`.

---

## 3. The one thing every seat must read before its own value file

`07-council-brief.md` §4 records a **blocker-class finding made during
assembly, not previously on the record**: the three `_v3` packs were frozen
on 2026-08-19 with `freeze-0003` receipts and plan trees that **byte-pin the
sha256 of the current v1 registry file**. Installing any new registry bytes
at `configs/arm_readiness/d117_row_registry_v1.json` changes that sha256 and
makes all three frozen packs refuse. The install as currently scheduled is
therefore not merely unruled — on the evidence in this checkout it is
**structurally blocked**, and the council's first output must be a
disposition of that.

---

## 4. Common schema facts (true for every value below)

- The row registry the code will accept is
  `R1_ROW_REGISTRY_SCHEMA = "joulewise.arm_readiness_row_registry.v2"`
  (`joulewise/arm_readiness.py:45`). The committed registry is still v1
  (`configs/arm_readiness/d117_row_registry_v1.json:445`,
  `"schema_version": "joulewise.arm_readiness_row_registry.v1"`).
- v2 differs from v1 by exactly one key:
  `R1_ROW_REGISTRY_KEYS = REGISTRY_KEYS | {"freeze_evidence_lifecycle"}`
  (`joulewise/arm_readiness.py:269`), where
  `REGISTRY_KEYS = {"schema_version", "registry_id", "plan_profiles", "rows"}`
  (`:268`). The 35 rows and the three ALPHA/BETA/GAMMA profiles are unchanged
  and re-validated identically (`validate_registry`, `:1838-1938`).
- **All five reserved values live inside that one new key.** Every one of
  them is a field of `freeze_evidence_lifecycle`, whose exact key set is
  `_R1_REGISTRY_KEYS` (`:479-489`) and whose validator is
  `validate_r1_lifecycle_registry` (`:1510-1806`).
- **No partial install exists.** `_r1_contains_reserved` walks the whole
  structure for the `ED_RESERVED:` prefix (`:1501-1508`,
  `_R1_ED_RESERVED_PREFIX = "ED_RESERVED:"` at `:526`) and
  `validate_r1_lifecycle_registry(..., require_resolved=True)` — the default
  for every issuance/consumption caller — raises:

  ```python
  if require_resolved and (
      _r1_contains_reserved(registry)
      or not raw_policies
      or not raw_rows
  ):
      raise ArmReadinessError(
          "readiness_row_registry_mismatch",
          "R1 lifecycle registry contains unresolved Ed-reserved values",
      )
  ```
  (`joulewise/arm_readiness.py:1795-1804`)

  The docstring states the intent: *"Clause-6 values may exist as explicit
  `ED_RESERVED:` placeholders for dry construction only. Every
  issuance/consumption caller uses the default `require_resolved=True` and
  therefore fails closed."* (`:1513-1518`)
- The checked-in placeholder that names each reserved value is
  `R1_LIFECYCLE_REGISTRY_PLACEHOLDER` (`:527-556`).
- Contract authority for the reservation: decision log R1 clause 6 (D-078
  lifecycle refusal registry) and clause 7 (reserved semantics), quoted per
  value below; `docs/decision_log.md:9296-9322`.
