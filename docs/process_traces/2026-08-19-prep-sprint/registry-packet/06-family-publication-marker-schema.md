# V6 — `successor_policy.family_publication_marker_schema`

## Field

`freeze_evidence_lifecycle.successor_policy.family_publication_marker_schema`
— a string naming the schema of the complete-family publication marker.

Placeholder in code:

```python
"family_publication_marker_schema": (
    "ED_RESERVED:family-publication-marker-schema"
),
```
(`joulewise/arm_readiness.py:543-545`)

## Schema requirement (validator code, verbatim)

```python
for name in ("cross_chain_numbering", "family_publication_marker_schema"):
    _require_string(successor_policy[name], f"R1 successor_policy.{name}")
```
(`joulewise/arm_readiness.py:1735-1736`)

**Any non-empty string passes.** The validator imposes no format, no
registered-schema check, and no cross-reference to a file. That is the
weakest gate of the six values and the reason a seat must supply the
discipline the code does not: the string is a *contract identifier*, and
nothing mechanically stops a typo or an unimplemented schema name from being
installed.

(`_require_string` is the module's string checker; the `ED_RESERVED:`
placeholder satisfies it, which is why this field is caught only by the
global `_r1_contains_reserved` sweep at `:1795-1804`, not by a local check.)

The sibling field in the same loop, `cross_chain_numbering`, has the same
zero-constraint shape — see `08-open-items.md` OPEN-ITEM 5.

## Why it is reserved

Consult reserved list:

> "Approve freeze-receipt v2's predecessor binding set and **the family
> publication marker**."
> — `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:251`

Contract clause 7:

> "The same registry carries explicit unresolved seams for the three successor
> pack IDs, cross-root freeze numbering, the freeze-receipt-v2
> predecessor-binding set, and **the family publication-marker schema**; none
> has a code default or permits generation."
> — `docs/decision_log.md:9318-9322`

Plan-consult item-by-item approval list:

> "6. Freeze-receipt v2 predecessor-binding set, **marker schema/path,
> complete-family predicate, and activation semantics**."
> — `docs/process_traces/2026-08-16-phase2-plan-consult/consult.md:377`

Held open by D-139 even while A3's other defaults were approved:

> "the acceptance-artifact identity, **family-marker particulars**, and
> exact-byte publication remain Ed-reserved"
> — `docs/decision_log.md:8807-8809`

Named as unruled by the install refusal: *"…or the family-publication marker
schema (explicitly Ed-reserved by the runsheet's own step 5)"*
(`git show 35badb4`, commit body); runsheet step 5 note: *"Step 5 gains the
freeze-invocation particulars … and the family-marker construction rule,
which is a reserved Ed ruling"*
(`docs/process/phase2-transaction-runsheet.md:33-36`).

## The one concrete design on the record (unratified)

The 2026-08-18 morning packet put a shape to Ed and he did not rule it:

> "**RULING: family-marker particulars (gates PUBLICATION, not the freeze).**
> Your A3 approval reserved the complete-family marker's exact schema, path,
> and activation predicate. The freeze-numbering consult recommends: an
> EXTERNAL marker file outside the pack roots, created only after all pack
> bytes are final, binding the three final pack digests + the three
> freeze-0002 receipt hashes (**a receipt cannot bind its own pack's final
> digest — self-hash cycle**). If you approve that shape, say where it lives
> (suggestion: `configs/arm_readiness/d117_v2_family_marker.json`) or defer to
> my judgment on path+schema with the binding set as consulted."
> — `docs/process/ed-morning-packet-2026-08-18.md`, §2

The self-hash-cycle argument is the load-bearing part and survives the family
bump unchanged.

## Current disposition: retrofit, by two-seat concurrence

Both D-147 seats and the magistrate agreed the marker lands **after** `_v3`:

> "(1) Family-marker particulars: `_v3` lands FIRST, machine-readable
> supersession marker retrofits via its own co-design pass (both seats
> recommend; magistrate concurs)."
> — `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:117-120`

with the seat's reasoning:

> "a supersession marker is a schema/contract change ('big' under D-144) and
> belongs to its own co-design pass. **Question: does `_v3` land before, with,
> or after the family marker?** My recommendation: land `_v3` first (it is
> blocking FULL GREEN and Ed's confirmation table), retrofit the marker."
> — `06-r2-design-opus.md:696-703`

## Proposed value

**None.** The retrofit decision means there is, deliberately, no marker
schema to name yet. The fixture value is `"test.family-marker.v1"`
(`tests/test_arm_readiness_evidence.py:74`).

**This is the packet's hardest structural problem, and the council must face
it directly:** the registry install requires a *resolved* string in this
field, but the thing the string names is explicitly deferred to a future
co-design pass. The council cannot both honour the retrofit decision and
install a truthful value.

## Alternatives a seat should argue

1. **Name the schema now, build it later** — install e.g.
   `"joulewise.d117_family_publication_marker.v1"` as a forward declaration,
   with the marker file to follow. Precedent exists in this codebase:
   D-134's "slot-declaration" pattern, where a declared-but-unfilled slot is
   REJECTED by the frozen validator until filled
   (`docs/decision_log.md:9110-9113`). **Risk:** a registry string that names
   a non-existent schema is exactly the "placeholder that is not a reason
   code" failure mode R1 clause 6 legislated against — a resolved-looking
   value that resolves to nothing. A seat proposing this must say what
   mechanically refuses until the schema exists.
2. **Install a schema that names its own absence** — e.g.
   `"joulewise.family_publication_marker.deferred.v0"`, paired with a code
   check that refuses publication (not arming) while that token is
   installed. Truthful and fail-closed; costs a small code change and a test.
3. **Do the marker co-design pass FIRST**, then install the registry once.
   Honours D-144 (marker is a "big" schema change), avoids a forward
   declaration, and collapses two transactions into one. Costs a co-design
   pass on the critical path to the windows.
4. **Defer the whole registry install** until the marker exists (see
   `01-successor-pack-ids.md` alternative C, and `07-council-brief.md` §4 —
   this may be forced anyway).

## Evidence each seat should check

- **Contract lens — verify this assembly finding, it is the key one.**
  `grep -rn "family_publication_marker_schema" joulewise/ scripts/` returns
  **only** the placeholder (`arm_readiness.py:543`), the key-set constant
  (`:523`), and the validator's `_require_string` loop (`:1736`). **There is
  no consumer.** Likewise, of the eight refusal roles, `FAMILY_PUBLICATION`
  is the **only one with no raise site** in `joulewise/` (compare
  `CLASS_MISMATCH` at `:3201`, `:4574`; `TEMPORAL_BUDGET` at `:3323`, `:3338`;
  `UNKNOWN_POLICY` at `:1817`, `:4341`, `:4581`;
  `DEPENDENCY_MANIFEST`/`DEPENDENCY_CHANGED_SET`/`SUCCESSOR_CHAIN`/
  `V1_GRANDFATHERING` all wired at `:2954`–`:3243`).
  So installing a marker-schema string today is **inert**, and the
  "activation semantics" the plan consult demanded
  (`phase2-plan-consult/consult.md:377`) do not exist in code. A seat should
  rule whether the marker co-design pass is what wires `FAMILY_PUBLICATION`,
  and whether installing an inert string is acceptable in the interim.
- **Execution lens:** confirm the self-hash-cycle claim empirically — that a
  freeze receipt inside a pack cannot bind that pack's own committed tree
  digest. `committed_pack_tree_sha256` over a root that contains the receipt
  is the mechanism; demonstrate it rather than accept the packet's quotation.
- **Both:** whether the marker must bind `freeze-0002` or `freeze-0003`
  hashes now. The morning packet's shape names `freeze-0002` because it
  predates the `_v3` family; the live receipts are `freeze-0003`
  (`0abfddb1…`, `f232d076…`, `f32bd3a8…`, per
  `docs/process/ed-s5-mint-decision-2026-08-19.md:84-88`). Any ruling that
  copies the 2026-08-18 shape verbatim will bind superseded hashes.
