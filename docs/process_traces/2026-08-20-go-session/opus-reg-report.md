# D-148.5 REGISTRY-VALUES COUNCIL — OPUS SEAT (contract lens), independent design

**Seat:** Opus 5, contract lens. **Base:** read-only worktree `wtREG-O` @ `afb7d57`.
**Verification note:** `git diff --stat 4597ad4..afb7d57` over `joulewise/`, `configs/arm_readiness/`,
`tests/test_arm_readiness_evidence.py` is **empty** — every line number below is valid at both the
packet's base and this head, and every packet citation was re-resolved at `afb7d57`.

**Executed artifacts produced by this seat** (scratch, nothing tracked was modified):
- `scratchpad/registry/build_candidate.py` — builds the proposed registry and runs the **real**
  `validate_r1_lifecycle_registry(require_resolved=True)` and `validate_registry` over it.
- `scratchpad/registry/candidate_registry_v2.json` — the full canonical v2 row registry.
  **Both validators PASS.** Canonical bytes 27 653, sha256
  `44b0202b08227852fe20007fe0d0a50ec47d0b47a8e1ec4bf0f4120036b06b81`.
  (The sha is illustrative only — V1's pack ids and hence the bytes change if the magistrate
  rules a different family boundary.)
- `scratchpad/registry/lifecycle_block.json` — the `freeze_evidence_lifecycle` block alone.

---

## 0. Headline: the packet's blocker is real but it is not the *only* blocker, and it is not the *expensive* one

Three findings drive everything below. All three are executed or mechanically derived at `afb7d57`,
not read off the record.

**(A) A second, independent blocker: `V1_GRANDFATHERING`.** Installing the v2 registry turns the R1
lifecycle on globally — `lifecycle_registry` is non-`None` **iff** the loaded row registry carries
`R1_ROW_REGISTRY_SCHEMA` (`joulewise/arm_readiness.py:6124-6128` in `generate_arm_receipt`,
`:5372-5378` in `generate_freeze_receipt`, `:6345-6349` in `_derive_arm_semantics_for_verification`).
With it on, `_freeze_evidence_for_arm` routes every frozen freeze-evidence item through
`_authenticate_generic_evidence_item(..., lifecycle_registry=lifecycle_registry)`
(`:5383-5392`), which raises

```python
if (
    lifecycle_registry is not None
    and item["namespace"] == "PACK"
    and receipt["schema_version"] == EVIDENCE_RECEIPT_SCHEMA
):
    raise EvidenceLifecycleError(
        lifecycle_registry,
        "V1_GRANDFATHERING",
        "legacy generic freeze evidence may not enter the R1 lifecycle",
        ...
```
(`joulewise/arm_readiness.py:4219-4229`; `EVIDENCE_RECEIPT_SCHEMA = "joulewise.arm_readiness_evidence_receipt.v1"`, `:58`)

Measured in this checkout: `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`
binds **12 evidence items, of which 11 are `namespace=PACK` + `schema_version=joulewise.arm_readiness_evidence_receipt.v1`**
(the 12th is the identity-pin projection). All 33 `_v3` evidence receipts across the family carry
that same v1 generic schema.

⇒ **Even if the byte-pin of file 09 were cured, the `_v3` family still could not arm under an
installed registry.** The install and the `_v3` family are mutually exclusive by *two* independent
mechanisms. Packet OPEN-ITEM 7 raises retroactivity as a judgment call for the magistrate; it is not
a judgment call, it is a mechanical refusal. **Severity: BLOCKER (packet omission).**

**(B) The `_v4` boundary is forced by a clock that is already running, independent of the registry.**
Measured from this worktree at 2026-08-20T11:07:50Z with `time.monotonic_ns() = 2448119368460833`
(the same clock the code uses):

| family | receipts | min `valid_until_monotonic_ns` | remaining |
|---|---|---|---|
| `_v1` | 33 | 1986799611717708 | **−128.1 h** |
| `_v2` | 33 | 2370023883623625 | **−21.7 h** |
| `_v3` | 33 | 2468742407178458 | **+5.73 h** |

Boot session still `DA90818C-9C31-45D0-8813-DEAE65FBA143`. The arm receipt min-inherits these
(`valid_until = min([evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations])`,
`:6235-6242`), R1 clause 5 bars revalidation, D-131 requires a successor pack. **A `_v4` family is
compelled within hours whether or not the registry is ever installed.**

⇒ The install is not competing with the `_v3` campaign. It is competing with nothing. This inverts
the packet's cost framing (file 09 §6 calls `_v4` "enormous cost"): **the `_v4` re-freeze is a sunk
cost of the expiry fuse, and the registry install is a marginal ordering constraint inside it.**

**(C) The install is a code transaction in at least four places, not one.** The brief §2 names one
code delta (`_SUPPORTED_ENVIRONMENT_COMPARISONS`). Executed probe of `_validate_refusal`
(`:1434-1443`) against the eight-role vocabulary:

```
packet 04 alt.1  r1_class_mismatch                   REFUSE readiness_schema_invalid: .code is not closed
fixture          test_r1_class_mismatch              REFUSE readiness_schema_invalid: .code is not closed
packet 04 alt.3  evidence_author_*                   REFUSE readiness_schema_invalid: .code is not closed
packet 04 alt.2  readiness_row_registry_mismatch/STRUCTURE   ACCEPTED
packet 04 alt.2  readiness_row_registry_mismatch/POLICY      REFUSE .type does not match code
SUCCESSOR_CHAIN  readiness_successor_chain_invalid/IDENTITY  REFUSE .type does not match code
```

Registry-ruled refusal codes reach receipts through `EvidenceLifecycleError.refusal()`
(`:982-988`) → `evidence_refusals.append(exc.refusal())` (`:6151-6158`, `:4613`) → the receipt's
`refusals` list → `_validate_refusal`, which enforces **both** `code ∈ READINESS_REASON_CODES` and
`type == REASON_TYPE_BY_CODE[code]`. Three of the packet's four V4 alternatives are therefore
executably refuted, and `readiness_successor_chain_invalid` has type `SUCCESSOR_CHAIN`
(`:210`) which is **not a member of the registry's 7-value type enum** (`:1768-1776`) — that code
is unnameable by the registry at all. **Severity: BLOCKER (packet omission).**

---

## §1a — Counting ruling: **enumeration A binds, and the council should retire "the five" entirely**

**Recommendation: adopt enumeration A** (`00-INDEX.md:71-79`) as authoritative, with
`successor_pack_ids` as a value reopened by D-147 — i.e. the packet's own disposition
(`00-INDEX.md:112-117`). **Reason:** A is the enumeration produced by an executed mechanism (the
step-4 refusal recorded in `35badb4`'s commit body, with the refusing code cited); B is one seat's
characterisation (`06-r2-design-opus.md:727-730`) that a ruling copied
(`14-r2-ruling.md:125-127`) and RUN_STATE propagated (`RUN_STATE.md:34-38`). A characterisation
that contradicts itself within two sentences of its own source — "That is **one** of the five… R2
supplies **three** of the five" — cannot outrank a refusal that names its own five items and says
in the same breath that D-139 A3 had already closed the pack ids.

**But the count itself is the wrong artifact, and continuing to say "five" or "six" is an install
hazard.** `_r1_contains_reserved` (`:1501-1508`) walks the **entire** structure for the
`ED_RESERVED:` prefix and `require_resolved=True` (`:1796-1804`) refuses on any hit anywhere. A
list that is not the complete key-walk is not an install specification. The council should
therefore rule the counting **mechanically**, as: *the reserved set is every `ED_RESERVED:` leaf of
`R1_LIFECYCLE_REGISTRY_PLACEHOLDER` (`:527-555`), plus every empty-collection reservation in it,
plus every code-side gate that an installed value must pass.* That set, enumerated exhaustively, is
**fourteen reservation sites**, not five:

| # | Site | Where | Council label |
|---|---|---|---|
| 1 | `registry_id` | `:529` | §1c |
| 2 | `arm_policy.capability_horizon_ns` | `:534` | §1c (OPEN-ITEM 3) |
| 3 | `arm_policy.arm_to_consume_budget_ns` | `:535` | **V5** |
| 4 | `successor_policy.successor_pack_ids` | `:538` | **V1** |
| 5 | `successor_policy.cross_chain_numbering` | `:539` | §1c (OPEN-ITEM 5) |
| 6 | `successor_policy.freeze_receipt_v2_predecessor_bindings` | `:540-542` | §1c (OPEN-ITEM 5) |
| 7 | `successor_policy.family_publication_marker_schema` | `:543-545` | **V6** |
| 8 | `refusal_vocabulary[*].code` ×8 | `:547-554` | **V4** |
| 9 | `refusal_vocabulary[*].type` ×8 | `:547-554` | **V4** |
| 10 | `irrelevant_path_allowlist` (ships `[]`) | `:530` | §1c |
| 11 | `evidence_policies` (ships `[]`; carries kind, class, id, horizon, comparison ×29) | `:531` | **V2 + V3** |
| 12 | `row_policies` (ships `[]`; 35 rows, sorted, must equal the outer row order — `:1896-1903`) | `:532` | §1c |
| 13 | outer row-registry `registry_id` (unconstrained on the v2 branch — `:1857-1859`) | `:1853-1859` | §1c (OPEN-ITEM 6) |
| 14 | `_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset()` (**code**) | `arm_readiness_evidence.py:117-119` | **V2** |

and this seat adds a **fifteenth** the packet does not have: **`READINESS_REASON_CODES` /
`REASON_TYPE_BY_CODE` closure** (`arm_readiness.py:192-211`, enforced `:1434-1443`) — without a
delta there, V4's ruled codes cannot be issued into any receipt (finding (C) above).

**Proposed ruling text:** *"Enumeration A binds. `successor_pack_ids` is a sixth ruled value,
reopened by D-147's family supersession. The phrase 'the five R1 row-registry reserved values' is
retired from every downstream artifact and replaced by 'the R1 reserved set (15 sites, enumerated
in the ruling), of which six are the council-ruled values V1–V6.' The acceptance clause of kernel
row A63 (`docs/process/state_kernel.json:2834`) is amended to the same wording."*

---

## §1b — The six values as installable bytes

All bytes below were run through the production validators and **PASS**
(`build_candidate.py`; both `validate_r1_lifecycle_registry(require_resolved=True)` and
`validate_registry` on the assembled 35-row v2 registry).

### V1 — `successor_policy.successor_pack_ids` — **the packet's proposal is CONTESTED**

The packet proposes the three `_v3` ids (`01-successor-pack-ids.md:104-110`). **I contest the
values and adopt the shape.** Under my §3 position the registry lands at the `_v4` family boundary,
and `_plan_profile` is consulted while the successor family is being authored, so the registry must
already name the family it is being born with:

```json
"successor_pack_ids": {
  "ALPHA": "d117_floor_qwen25_1p5b_v4",
  "BETA": "d117_floor_qwen25_7b_v4",
  "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v4"
}
```

**Justification.** The validator requires exactly the three profile keys, three distinct non-empty
separator-free strings (`:1700-1719`) — satisfied. The second gate, `_plan_profile`
(`:2693-2716`), additionally requires each id to `fullmatch` its D-139-approved pattern
(`_SUCCESSOR_PROFILE_PATTERNS`, `:260-266`); `^d117_floor_qwen25_1p5b_v(?:[2-9]|[1-9][0-9]+)$`
matches `_v4` exactly as it matches `_v3`, so no code change is needed. Installing `_v3` instead
would name a family that is already dead twice over — by the byte-pin (file 09, CONFIRMED) and by
`V1_GRANDFATHERING` (finding (A)) — and `_plan_profile` admits **only one pack per profile through
the registry route** (`:2699-2712` requires `len(matches) == 1`), so there is no parallel-arm
design that lets both families resolve. Naming `_v4` is the only value under which the installed
registry admits any pack at all. The historical short-circuit (`_PROFILE_BY_PACK`, `:255-259`,
consulted first at `:2690-2691`) is untouched, so the `_v1` immutability invariant restored by
`35badb4` survives.

**Contingency the magistrate may need:** if install-now is ruled despite §3, substitute the three
`_v3` ids verbatim from `01-successor-pack-ids.md:104-110` — but that ruling must first dispose of
findings (A) and (C), which install-now does not survive.

### V2 — `environment_comparison` + the code allowlist — **no proposal on record; this is my ruling**

**Ruled token, uniform across all 16 EXECUTION_BOUND kinds:**

```
"environment_comparison": "INTERPRETER_PLATFORM_EXACT_AT_AUTHORING"
```

**Code allowlist delta** (`joulewise/arm_readiness_evidence.py:117-119`):

```python
# Ed ruled (D-148.5): the recorded fingerprint is compared at AUTHORING only.
# ARM-time divergence is out of R1's reach — the refusal-role census
# (arm_readiness.R1_REFUSAL_ROLES) has no environment role to raise.
_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset(
    {"INTERPRETER_PLATFORM_EXACT_AT_AUTHORING"}
)
```

**Justification.** Three facts decide this, and the first two are the reason I will not rule
`EXACT_MATCH`.

*First: there is no comparator, anywhere.* Exhaustive grep over `joulewise/` and `scripts/` for
`environment_comparison` / `environment_fingerprint` / `_SUPPORTED_ENVIRONMENT_COMPARISONS` returns
exactly four kinds of site: the registry key constant (`arm_readiness.py:515`), the class-consistency
branches in the validator (`:1597-1642`), the receipt-schema check that the fingerprint is a Mapping
and strict JSON (`:2066-2077`), and the allowlist-membership gate at issuance
(`arm_readiness_evidence.py:1786-1797`). The fingerprint is **written** (`:1978`) and **never read
back for comparison by any code path.** The packet's V2 execution-lens instruction — *"perturb the
interpreter… and confirm the ruled disposition actually fires"* (`02-…:224-228`) — is not
executable, because there is no disposition to fire. **Severity: BLOCKER (packet defect).**

*Second: R1 as legislated cannot express an ARM-time environment refusal.* `R1_REFUSAL_ROLES`
(`:488-499`) is code-owned and closed at eight roles, and none of them is an environment role;
`EvidenceLifecycleError` can only be constructed with a member role (`:974` → `_r1_refusal_entry`
raises `ValueError` on an unknown role, `:1825-1826`). Ruling `EXACT_MATCH` would therefore be
ruling a mechanism whose refusal is inexpressible without extending a code-owned closed census —
scope that belongs to its own co-design pass, not to a registry-values council. This is the same
failure mode R1 clause 6 legislated against for placeholders — *"no placeholder is a reason code"*
(`docs/decision_log.md:9303-9304`) — a resolved-looking value that resolves to nothing.

*Third: the one place staleness can actually enter is the authoring re-use path, and it is
closable in-scope.* Fresh authoring derives the fingerprint from the live process every time
(`_execution_environment_fingerprint` called at `arm_readiness_evidence.py:2427-2430` for **every**
EXECUTION_BOUND kind, and `_assemble_r1_receipt` **refuses** if it is absent, `:1968-1973`). The
only way a receipt bearing a *stale* environment survives into a freeze is the idempotent-re-use
branch at `:2090-2126`, which today re-checks evidence id, kind, boot session, monotonic deadline,
head commit and pack digest — but **not** the environment. The ruled token's semantics are
therefore: *"the interpreter/platform terms of the recorded fingerprint must equal the current
process's at the moment the receipt is accepted for re-use; otherwise the evidence is re-authored."*
Implementation is a comparison of six scalar terms already present in the fingerprint
(`interpreter`, `implementation`, `python_version`, `platform_system`, `platform_release`,
`platform_machine` — `arm_readiness_evidence.py:454-466`) plus a `_refuse(...)` in the author's own
unconstrained vocabulary (e.g. `evidence_author_environment_changed`), so it needs **no** new
refusal role and **no** reason-code delta.

**What the token deliberately does NOT promise, and where that is registered.** It does not compare
`non_repository_sys_path`, does not compare `inherited_environment` (the `PACK_AUTHENTICATION`
env-value digests), and does not fire at ARM or at consumption. The honest statement of the seam —
*"these committed bytes pass these checks as executed in the authoring environment; the interpreter
and platform are recorded and re-checked at re-use, and no other environment term is compared"* —
must be registered as a LIMITATION in `CLAIMS_STATUS.md` (the precedent site for D-148.6/.7
limitations, `docs/decision_log.md:171`), phrased in the paper's plain language. **The upgrade
trigger to record with it:** any ruling that wants ARM-time enforcement must first extend
`R1_REFUSAL_ROLES` with an environment role — that is the named, costed next pass.

**Naming discipline.** The token says what it compares (`INTERPRETER_PLATFORM`), how strictly
(`EXACT`), and when (`AT_AUTHORING`). It cannot be misread as an ARM gate. `NOT_APPLICABLE` remains
forbidden for EXECUTION_BOUND and mandatory for the other three classes (`:1609-1631`), and the
registry still cannot choose a class (`:671-675`, enforced `:1573-1580` / `:1786-1790`) — the
ruling smuggles no class override.

### V3 — the 14 EXECUTION_BOUND horizons — **no proposal on record; this is my ruling**

I re-derived the 14 mechanically and it reconciles: the T-0 dispatcher's two kind sets
(`arm_readiness_evidence_t0.py:103-113` volatile ×9, `:114-121` non-volatile ×4) cover 13 kinds, of
which exactly two are EXECUTION_BOUND (`OFFLINE_INPUT_INVENTORY`, `TERMINAL_REVIEW`); 16 − 2 = 14.
Confirmed.

**Two facts the packet does not have, which restructure the question:**

*(i) Six of the 16 EXECUTION_BOUND horizons are declarative-only, and the T-0 tier is a second,
uncrosschecked number for the same kinds.* `arm_readiness_evidence_t0.py` never loads, validates or
consults the R1 registry (grep for `validate_r1` / `lifecycle` / `horizon_ns` in that module returns
only its own `_validity_horizon_ns`, `:1758-1767`). So for the 13 T-0-authored kinds — including
the two EXECUTION_BOUND ones — the **live** horizon is the module constant, and the registry number
is a parallel declaration that nothing reconciles. A further four EXECUTION_BOUND kinds
(`GIT_CHECKOUT`, `PRIVILEGE_INSTALLATION`, `DRY_RUN_REHEARSAL`, `IDENTITY_PIN_PROJECTION`) have no
R1 authoring lane at all: they are absent from `_GENERIC_DERIVER_KINDS`
(`arm_readiness_evidence.py:89-101`) and from `_ROW_KIND` (`_evidence_t0.py:88-103`), and the last
two are `_SPECIALIZED_EVIDENCE_KINDS` (`:100-102`) which `_authenticate_generic_evidence_item`
explicitly rejects (`arm_readiness.py:4230-4234`). **Only 10 of the 14 have a live horizon.**
**Severity: SHOULD-FIX (packet defect)** — 03 treats all 14 as live and costs them in window terms
accordingly.

*(ii) Per-kind tiering is free.* Every one of the 35 rows in
`configs/arm_readiness/d117_row_registry_v1.json` requires **exactly one** evidence kind (verified
by enumeration). The `len(expected_policy_ids) != 1` gate (`:1913-1925`) is therefore
unconditionally satisfiable for any tiering whatsoever. Both 02 (`:203-206`) and 03 (`:146-152`)
list the row-map as a cost of tiering; it is not. Distinct policy ids may also carry *identical*
definitions — `definitions_by_policy_id` (`:1637-1651`) only forbids one id with two definitions —
so ids can be split for legibility at zero validation cost.

**Ruled values (the 14, and the 15 already-approved ones, as one coherent table):**

| policy id | class | `horizon_ns` | `environment_comparison` | kinds | live? |
|---|---|---|---|---|---|
| `r1.execution_bound.freeze_generic_24h.v1` | EXECUTION_BOUND | `86400000000000` (24 h) | ruled token | ACCEPTANCE_OWNER, ACCEPTANCE_SUCCESSOR, ESTIMATOR_IDENTITY, MINT_TRUST, MULTICELL_MINT, PACK_AUTHENTICATION, REASON_CODE_COVERAGE, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST, THREE_WINDOW_REGRESSION | **LIVE** |
| `r1.execution_bound.t0_procedural_6h.v1` | EXECUTION_BOUND | `21600000000000` (6 h) | ruled token | OFFLINE_INPUT_INVENTORY, TERMINAL_REVIEW | mirror of T-0 |
| `r1.execution_bound.declarative_24h.v1` | EXECUTION_BOUND | `86400000000000` (24 h) | ruled token | DRY_RUN_REHEARSAL, GIT_CHECKOUT, IDENTITY_PIN_PROJECTION, PRIVILEGE_INSTALLATION | **declarative** |
| `r1.time_bound.volatile_20m.v1` | TIME_BOUND | `1200000000000` (20 min) | `NOT_APPLICABLE` | BACKUP_PREFLIGHT, CLOCK_PROBE, MACHINE_PREFLIGHT, MAINTENANCE_CENSUS, POWERMETRICS_PROBE, POWER_PREFLIGHT, PROCESS_CENSUS | mirror of T-0 |
| `r1.time_bound.procedural_6h.v1` | TIME_BOUND | `21600000000000` (6 h) | `NOT_APPLICABLE` | CLOCK_ATTESTATION | mirror of T-0 |
| `r1.session_state_bound.volatile_20m.v1` | SESSION_STATE_BOUND | `1200000000000` | `NOT_APPLICABLE` | LAUNCH_RECIPE, ROOT_PREFLIGHT | mirror of T-0 |
| `r1.session_state_bound.procedural_6h.v1` | SESSION_STATE_BOUND | `21600000000000` | `NOT_APPLICABLE` | LEDGER_RESERVATION | mirror of T-0 |
| `r1.re_derivable.v1` | RE_DERIVABLE | `null` | `NOT_APPLICABLE` | DOCTRINE_PIN, PACK_FAMILY | n/a |

**Justification.**

*The ten live ones get 24 h because that is the number every existing receipt was authored under,
and a close-out transaction must not silently move a claim-integrity parameter.*
`_EVIDENCE_VALIDITY_NS = 86_400 * 1_000_000_000` (`arm_readiness_evidence.py:42`) is what
`_assemble_receipt` uses today on the non-R1 path (`:2421`); the R1 path replaces it with
`now_monotonic_ns + policy["horizon_ns"]` (`:1961-1977`). Ruling 24 h makes the install
**behaviour-neutral on this axis** — the single most important property for a contract-bearing
install into a live claim campaign. It is also the number the measured expiry table above is
denominated in: the `_v3` fuse is a 24-hour fuse.

*Why not 20 minutes (the fixture's shape).* These ten are **freeze-time** evidence: they are
authored when the pack is frozen, and consumed when the window runs, which is hours or days later
by design. A 20-minute horizon does not shorten a fuse, it makes freezing and arming a single
uninterruptible 20-minute ceremony — and four of the ten are suite-running kinds whose author has a
`_SUITE_TIMEOUT_SECONDS = 900` per suite (`arm_readiness_evidence.py:81`). Under D-078 no-retry the
result of ruling 20 minutes is not tighter evidence, it is lost windows. The fixture's uniform
`1_200_000_000_000` (`tests/test_arm_readiness_evidence.py:104-110`, asserted `:549-555`) exists to
exercise the validator, and adopting it is exactly the error the consult warned against
(`2026-08-15-r1-freeze-lifecycle-consult/consult.md:236`).

*Why not 6 hours (the strongest precedent argument).* 6 h is D-139 A3's "procedural" tier and it
does govern the two EXECUTION_BOUND kinds that already had a horizon — which is precisely why I
give **those two** 6 h and no others. The two are T-0-authored; the ten are freeze-authored. Reading
A3's approval of *"the existing operational horizons"* (`docs/decision_log.md:10078-10083`) as
covering the freeze-time tier is a category error: those constants live in
`arm_readiness_evidence_t0.py:49-50` and dispatch only over T-0 kinds. The freeze-time tier is a
**third tier that A3 never named**, and 24 h is its existing, operative value. Naming it records
practice; changing it invents policy inside a close-out.

*Why the two T-0 EXECUTION_BOUND kinds must be exactly 6 h.* Because the T-0 module will keep
stamping `_NONVOLATILE_EVIDENCE_VALIDITY_NS` (`:50`) into those receipts regardless of the registry.
Any other registry number creates a registry that says one thing while the code does another. Same
reasoning fixes all seven TIME_BOUND / three SESSION_STATE_BOUND values to their T-0 tiers — note
this means the class-uniform assignment in the test fixture is **wrong as production**: it would put
`CLOCK_ATTESTATION` and `LEDGER_RESERVATION` at 20 min while the code stamps 6 h.

*Required accompanying code delta (recommended, not optional in my view).* Add a module-import
consistency assertion in the same style as `:708-712`, tying the registry's declared horizons for
the 13 T-0 kinds to `_evidence_t0._validity_horizon_ns`, so the two numbers can never drift. Without
it, the install creates a permanent two-source-of-truth seam that nothing will catch.

*Declarative honesty.* The four no-lane kinds get their own policy id
(`r1.execution_bound.declarative_24h.v1`) with a definition identical to the live one. This costs
nothing (identical definitions under distinct ids are legal) and buys a registry in which the
declarative rows are visible as such. The ruling must state in words that these four values gate
nothing today, and name the work item to either wire them or drop the requirement.

### V4 — `refusal_vocabulary` — **no proposal on record; this is my ruling, and it needs a code delta**

```json
"refusal_vocabulary": [
  {"role": "CLASS_MISMATCH",         "code": "readiness_r1_class_mismatch",         "type": "POLICY"},
  {"role": "DEPENDENCY_CHANGED_SET", "code": "readiness_r1_dependency_changed_set", "type": "POLICY"},
  {"role": "DEPENDENCY_MANIFEST",    "code": "readiness_r1_dependency_manifest",    "type": "POLICY"},
  {"role": "FAMILY_PUBLICATION",     "code": "readiness_r1_family_publication",     "type": "CUSTODY"},
  {"role": "SUCCESSOR_CHAIN",        "code": "readiness_r1_successor_chain",        "type": "IDENTITY"},
  {"role": "TEMPORAL_BUDGET",        "code": "readiness_r1_temporal_budget",        "type": "LIFECYCLE"},
  {"role": "UNKNOWN_POLICY",         "code": "readiness_r1_unknown_policy",         "type": "POLICY"},
  {"role": "V1_GRANDFATHERING",      "code": "readiness_r1_v1_grandfathering",      "type": "LIFECYCLE"}
]
```

Accompanying **code delta** in `joulewise/arm_readiness.py` (immediately after
`SUCCESSOR_CHAIN_REASON_CODES`, `:180`):

```python
# D-148.5: R1 lifecycle refusal codes.  The registry names these; this table is
# what makes them issuable — _validate_refusal (:1434-1443) closes both the code
# set and the code->type map.
R1_LIFECYCLE_POLICY_CODES = frozenset(
    {
        "readiness_r1_class_mismatch",
        "readiness_r1_dependency_changed_set",
        "readiness_r1_dependency_manifest",
        "readiness_r1_unknown_policy",
    }
)
R1_LIFECYCLE_LIFECYCLE_CODES = frozenset(
    {"readiness_r1_temporal_budget", "readiness_r1_v1_grandfathering"}
)
R1_LIFECYCLE_CUSTODY_CODES = frozenset({"readiness_r1_family_publication"})
R1_LIFECYCLE_IDENTITY_CODES = frozenset({"readiness_r1_successor_chain"})
```

added to the `READINESS_REASON_CODES` union (`:192-201`) and to `REASON_TYPE_BY_CODE`
(`:202-211`) as four more comprehensions with types `POLICY` / `LIFECYCLE` / `CUSTODY` /
`IDENTITY`.

And a second **code delta** in `validate_r1_lifecycle_registry`'s refusal loop, after the type check
at `:1768-1780` — **this is the single most valuable line in the whole install**:

```python
if not code.startswith(_R1_ED_RESERVED_PREFIX) and (
    code not in READINESS_REASON_CODES
    or reason_type != REASON_TYPE_BY_CODE[code]
):
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"R1 refusal_vocabulary[{index}] is not a closed reason code",
    )
```

**Justification.** The eight strings are not cosmetic: they are what the production refusal paths
emit (`arm_readiness_evidence.py:1765-1796`; `arm_readiness.py:3186`, `:3201`, `:3323`, `:4226`,
`:4341`, `:4574`) and what will appear in receipts and in the paper's refusal census. The closure
constraint (finding (C)) means the ruling has exactly two honest options: overload existing codes,
or extend the universe. **Overloading is wrong on the census**: `readiness_row_registry_mismatch` is
the D-134 structural code emitted by dozens of unrelated sites, and an R1 lifecycle refusal that
spells itself the same way is unreadable in a census — and there are eight roles needing eight
**distinct** codes (`:1781-1785`), which the semantically-fitting existing codes cannot supply
without absurd pairings. So: extend the universe, in the `readiness_*` family so the codes remain
recognisably part of one vocabulary, with an `r1_` infix so a census can partition them in one grep.
Every code matches `[a-z][a-z0-9_]*` (`:1761-1763`) and every type is in the 7-value enum
(`:1768-1776`).

Per-role typing (rather than the fixture's uniform `POLICY`) is not decoration here — it is forced.
`_validate_refusal` compares the registry's `type` against `REASON_TYPE_BY_CODE[code]`, so once the
codes are placed in typed families the registry has exactly one legal type per code. The type
assignments follow what each role is about: policy resolution (four), evidence lifetime and legacy
admission (two), family custody (one), successor identity (one).

**Note the schema gap this exposes, which the ruling should register:** `SUCCESSOR_CHAIN` is a
`REASON_TYPE_BY_CODE` value (`:210`) that the registry's type enum cannot express (`:1768-1776`), so
the pre-existing `readiness_successor_chain_invalid` can never be named by an R1 registry. That is a
latent contradiction in R1's own schema; my ruling routes around it by minting a new
`IDENTITY`-typed code, and the gap should be recorded rather than left to surprise the next pass.

### V5 — `arm_policy.arm_to_consume_budget_ns` (and its sibling) — **no proposal on record**

```json
"arm_policy": {
  "capability_horizon_ns": 300000000000,
  "arm_to_consume_budget_ns": 300000000000
}
```

**Justification — the equality is derived, not chosen.** Read the gate exactly
(`validate_r1_temporal_budget`, `:3299-3341`): it collects `valid_until_monotonic_ns` from the
`TIME_BOUND` receipts only, takes `earliest = min(deadlines)`, and refuses when
`earliest − now_monotonic_ns < budget`. So the budget is **the minimum remaining T-0 evidence life
required at arm time**, and a *larger* budget is a *stricter* gate — the packet is right about the
inversion (`05-…:114-119`) and I confirm it.

Now read the arm receipt's validity (`:6235-6242`):
`valid_until = min([evaluated_at_monotonic_ns + capability_horizon_ns, *evidence_expirations])`.
Setting `budget == capability_horizon_ns` makes the two clauses one statement:
**the arm capability may not be issued unless the T-0 evidence can cover the capability's entire
nominal lifetime.** If the budget gate passes, every TIME_BOUND deadline is at least
`now + capability_horizon_ns`, so the `min()` is not truncated below the nominal horizon by T-0
evidence. That is an invariant, not a guess, and it is the only relation between the two numbers
that makes the pair coherent. Any budget < horizon admits arms whose capability is silently
truncated; any budget > horizon is a pure tax with no corresponding capability.

**Why 300 s specifically.** `generate_arm_receipt`'s own default when no lifecycle registry is
loaded is `validity_ns: int = 300_000_000_000` (`:6101`, consumed at `:6238`). Ruling
`capability_horizon_ns = 300_000_000_000` therefore makes the install **behaviour-neutral** on the
arm-validity axis, exactly as V3's 24 h does on the evidence axis — an install that changes no
number is an install whose failure modes are already known. The fixture uses the same 300 s
(`tests/test_arm_readiness_evidence.py:60`), which is corroboration rather than coincidence: it was
chosen to match the code default.

**The invariant the validator does not check, hand-verified.** The budget must be strictly less than
the smallest TIME_BOUND horizon, or `earliest − now < budget` is true the instant the evidence is
authored and every arm refuses. Smallest TIME_BOUND horizon under V3 is `1_200_000_000_000`
(20 min); `300_000_000_000 < 1_200_000_000_000` ✓ (checked executably in `build_candidate.py`).
The derived **operational contract** the ruling must state in words: *the T-0 capture → arm ceremony
must complete within 15 minutes of the T-0 capture*, since 20 min − 5 min of required runway = 15 min.

**Condition on this value (§1d).** I rule 300 s **conditionally**: the implementing lane must walk
one real author→arm sequence at the measurement checkout (`docs/process/rehearsal-operator-card.md`
E-4→E-9) and report the observed T-0→arm gap. If the observed gap exceeds 15 minutes, the ruling
does not survive contact and the correct response is **not** to shrink the budget but to give the
T-0→arm ceremony an owner and a time budget — under D-149's unattended windows and D-078's no-retry,
a budget ruled below the real gap converts every window into a lost window. No measurement of the
"expected arm-sequence length" asserted at `arm_readiness_evidence_t0.py:47-48` exists anywhere in
the record; this is that measurement.

**Disposition of OPEN-ITEM 3.** `capability_horizon_ns` is **not** covered by D-139 A3: A3's
horizons are the T-0 evidence tiers, whereas `ARM_CAPABILITY` is a distinct class
(`TEMPORAL_CAPABILITY`, `:706`) explicitly *"not an evidence-policy row"* (`:673-675`). It is a
seventh ruled value that the five-item list omitted by oversight, and the ruling should say so
plainly so "the five" is never restated as a complete list.

### V6 — `successor_policy.family_publication_marker_schema` — **no proposal; this is my ruling**

```json
"family_publication_marker_schema": "joulewise.d117_family_publication_marker.UNBUILT.v0"
```

**Justification.** This is the packet's hardest structural problem and it is right that it is:
the field demands a resolved string, while D-147 S1 deferred the thing the string names to its own
co-design pass (*"`_v3` lands FIRST, machine-readable supersession marker retrofits via its own
co-design pass"*, `14-r2-ruling.md:117-120`). I verified the packet's key assembly finding and it
holds: `grep -rn "family_publication_marker_schema" joulewise/ scripts/` returns only the
placeholder (`:543`), the key-set constant (`:523`), and the `_require_string` loop (`:1736`) —
**no consumer** — and `FAMILY_PUBLICATION` is confirmed the **only** one of the eight roles with no
raise site anywhere (all seven others: `:2954`, `:3102`, `:3118`, `:3130`, `:3186`, `:3201`,
`:3215`, `:3234-3292`, `:3323`, `:3338`, `:4226`, `:4328-4371`, `:4574`, `:4581`, and
`arm_readiness_evidence.py:1772`, `:1780`, `:1791`, `:2295`).

Given that, the only defensible value is one that **tells the truth about its own state**. Option 1
of the packet (a forward declaration naming a schema that does not exist) is the failure mode R1
clause 6 legislated against. Option 3 (do the marker pass first) puts a "big" D-144 co-design pass
on the critical path of a family re-freeze that is already on a 5.7-hour fuse. Option 2 —
a token that names its absence — is correct, and `UNBUILT.v0` is unmistakable: it cannot be
mistaken for a live schema by a reader or by a grep.

**What must accompany it, and what I will not pretend.** The packet's option 2 pairs the token with
"a code check that refuses publication while it is installed." **There is no publication code path
to guard** — publication in this project is runsheet step 7, a ceremony. So the honest package is:
(i) the token above; (ii) a **test pin** asserting that while the installed string matches
`*.UNBUILT.v*` no module in `joulewise/` references `family_publication_marker_schema` — a canary
that fails the day someone wires a consumer without ruling the schema; (iii) the runsheet's step-7
acceptance clause amended to read the installed string and refuse to publish on the `UNBUILT` token;
(iv) a registered limitation stating that the complete-family publication marker is unbuilt and
`FAMILY_PUBLICATION` is an unwired role. The marker co-design pass then replaces the string and
wires the role in one transaction — and it must bind `freeze-0004` hashes, not the `freeze-0002`
hashes of the 2026-08-18 shape (`ed-morning-packet-2026-08-18.md` §2) nor even `freeze-0003`. The
self-hash-cycle argument in that shape (a receipt cannot bind its own pack's final digest) is sound
and survives every family bump.

### §1c — the fields the five-item list omits but the install requires

```json
"registry_id": "d117-r1-lifecycle-v1",
"irrelevant_path_allowlist": [],
"cross_chain_numbering": "joulewise.freeze_chain.monotonic_predecessor_ordinal.v1",
"freeze_receipt_v2_predecessor_bindings": [
  "evidence_set_sha256", "freeze_receipt", "identity_receipt",
  "pack_digest_algorithm", "pack_id", "pack_path", "pack_sha256",
  "plan_id", "plan_sha256"
]
```
plus **outer** `"registry_id": "d117-row-registry-v1"` — **unchanged**, see §3 — and `row_policies`
generated mechanically as `{"row_id": row["row_id"], "freshness_policy_id": pid_by_kind[row["required_evidence_kinds"][0]]}`
for each of the 35 rows in the outer registry's own order (the validator requires the two lists to
be **equal**, not merely equivalent — `:1896-1903`).

- `irrelevant_path_allowlist = []` is the strictest value and the behaviour-neutral one: there is no
  allowlist in force today, so an empty list changes nothing about the DEPENDENCY_CHANGED_SET gate.
  It validates (`[] == sorted(set([]))`) and `require_resolved` only rejects empty `evidence_policies`
  / `row_policies`, not an empty allowlist (`:1796-1800`).
- `cross_chain_numbering` names D-139 A3's approved **semantics** — *"chain-monotonic … with
  explicit predecessor bindings"* (`docs/decision_log.md:10078-10082`), as amended by D-147 S3
  (*"ordinal = predecessor+1"*, `14-r2-ruling.md:42-47`) — **without** embedding a generation
  number. A string containing `freeze-0002` (the fixture's shape,
  `tests/test_arm_readiness_evidence.py:69`) would already be stale, and would be stale again at
  `freeze-0005`.
- `freeze_receipt_v2_predecessor_bindings` is ruled as **exactly** `sorted(FREEZE_PREDECESSOR_KEYS)`
  (`arm_readiness.py:382-392`), the nine keys the code actually derives in
  `_derive_freeze_predecessor` (`:5113-5148`). The fixture's five-key list is a fiction. Ruling the
  real key set makes the field checkable, and I recommend the accompanying assertion
  `set(bindings) == FREEZE_PREDECESSOR_KEYS` in the validator so the declaration cannot drift from
  the derivation — otherwise this field joins the marker schema as inert bytes (it has no consumer
  today either; OPEN-ITEM 5 is right about that).

---

## §2 — Install timing: **DEFER to the `_v4` family boundary**, but for stronger reasons than the packet gives

**Position: defer, and bind the install to the `_v4` boundary — as the cheap option, not the
least-bad one.** I reach the same disposition as `RUN_STATE.md:49-53` and refuse its framing.

**Why install-now is closed.** Two independent mechanisms, both executed:

1. The byte-pin (file 09, CONFIRMED-BLOCKER). I accept it without re-running it; its method is
   sound (the `predicate_id` mutation keeps the registry valid, so P1 staying OK is a genuine
   control) and its two extensions beyond the packet's prediction — that the pin lives in the frozen
   `plan_tree.json` so the refusal fires upstream of every receipt check, and that re-minting is
   itself gated on the same pin — are the decisive ones. Its §5d result (identical bytes at a new
   path still refuse, because the comparison is whole-dict equality over
   `{registry_id, path, sha256, plan_profile}`) also closes OPEN-ITEM 6: **the outer `registry_id`
   and the file path must not change**, which is why V1's outer id above stays
   `d117-row-registry-v1` and the file stays at `configs/arm_readiness/d117_row_registry_v1.json`
   despite carrying a v2 schema. The legibility trap is real and is the correct trade.
2. `V1_GRANDFATHERING` (finding (A)). Independent of the sha entirely: 11 of the 12 evidence items
   in each `_v3` freeze receipt are v1-schema PACK-namespace receipts, and the install turns on the
   lifecycle that refuses exactly those.

**Why deferral costs almost nothing.** Finding (B): the `_v3` family has ~5.7 h of monotonic
evidence life left as of 2026-08-20T11:07Z, `_v2` is 21.7 h dead, `_v1` is 128 h dead. R1 clause 5
bars revalidation; D-131 requires a successor pack + custody root. A `_v4` family is compelled by
the fuse alone. The packet costs `_v4` as "enormous" (file 09 §6) because it counts the whole
re-freeze against the registry install; almost all of that cost is already owed.

**Alternatives I considered and reject.** *Install after the windows* — leaves the R1 mechanism
dormant for the entire claim campaign and does not avoid a `_v4`; it merely spends the `_v4`
transaction without buying the mechanism. *New registry path* — executably refuted (file 09 §5d).
*Code-level grandfathering of the registry reference* — a contract change on the authentication
path, which is what R1/D-134 exist to prevent, and it would additionally need to defeat
`V1_GRANDFATHERING`, i.e. two contract holes rather than one.

### What the `_v4`-boundary install must include

One transaction, one commit series, no green gap, in this order — the order is load-bearing:

1. **Registry bytes** at the **unchanged** path with the **unchanged** outer `registry_id`,
   `schema_version` flipped to `joulewise.arm_readiness_row_registry.v2`, `freeze_evidence_lifecycle`
   carrying V1(`_v4` ids)–V6 and the §1c fields, rendered canonically (`render_json`;
   `load_registry` enforces `require_canonical=True`, `:2508`).
2. **Code deltas, same commit** — all four, or the install is inert or explosive:
   (a) `_SUPPORTED_ENVIRONMENT_COMPARISONS` gains the V2 token
   (`arm_readiness_evidence.py:117-119`);
   (b) the four R1 reason-code frozensets + `READINESS_REASON_CODES` union + `REASON_TYPE_BY_CODE`
   entries (`arm_readiness.py:180-211`);
   (c) the registry-side closure check in the refusal loop (`:1768-1780`);
   (d) the authoring-time environment comparison at the evidence re-use site
   (`arm_readiness_evidence.py:2090-2126`), which is what makes V2's token mean something.
   Recommended with them: the registry↔T-0 horizon consistency assertion (V3) and the
   `set(bindings) == FREEZE_PREDECESSOR_KEYS` assertion (§1c).
3. **`_v4` evidence authored AFTER (1) and (2) are committed**, at the **final reviewed head**, at
   the measurement checkout. The head requirement is not optional: `_freeze_evidence_for_arm` sets
   `expected_head = reviewed_main(pack_root)["head_commit"]` **whenever the lifecycle is on**
   (`arm_readiness.py:5378-5382`) — a binding that simply does not exist today. Evidence authored at
   any other head will refuse at arm.
4. **`_v4` plan trees regenerated** — `plan_arm_readiness_attachment` builds `row_registry` from the
   live bytes (`:2900`), so the new trees pin the new sha/id/path. This is the step that makes the
   family compatible with the registry instead of hostile to it.
5. **`freeze-0004` minted**, ordinal = predecessor + 1, `predecessor` binding each pack's `_v3` +
   its `freeze-0003`, at the measurement checkout (path-binding: `_pack_identity` includes
   `"pack_root": str(pack_root.resolve())` — file 09 §3's incidental finding, which the runsheet
   must carry so nobody misreads a location refusal as pack corruption).
6. **The acceptance test the whole install exists to satisfy:** re-run file 09's probe against
   `_v4` and require **P1, P2 and P3 all OK** — the family authenticates *against the installed
   registry*. Plus one arm dry-run producing a receipt whose `refusals` list is empty, which is the
   only way to prove finding (C)'s reason-code delta actually landed.
7. **Kernel transaction:** `docs/process/state_kernel.json` row A63 amended per §1a's wording,
   `python3 scripts/gen_state.py` then `--check` clean; test pins moved —
   `lifecycle_registry()` (`tests/test_arm_readiness_evidence.py:29-88`, `_v2` ids at `:63-67`),
   `resolved_r1_row_registry()` (`:90-132`, class-uniform 20 min at `:104-110`), and
   `test_successor_profile_ids_install_from_registry_roles` (`:492-585`), which currently asserts a
   `_v3` pack is REFUSED (`:508-525`) and asserts the uniform horizon (`:549-555`); custody record +
   decision-log pointer row (ONE home = the ruling); canonical FULL GREEN at the head.

**Two hazards the runsheet must carry explicitly:**

- **The green gap is real.** Between step 1 and step 5 the repository is in a state where **no** pack
  can arm — `_v3` is refused by the pin and by `V1_GRANDFATHERING`, `_v4` does not yet exist. That
  window must be executed inside one measurement session with no window scheduled against it.
- **The registry becomes as immutable as the packs.** Once `_v4`'s plan trees and receipts pin it,
  every subsequent registry edit — one horizon, one refusal spelling, one allowlist entry — forces a
  `_v5` family. **This is the true price of installing at all, and it appears nowhere in the packet.**
  The ruling must state it, because it converts the registry from a config into a frozen artifact
  and it is the reason to get all fifteen sites right in one pass.

---

## §3 — What the packet missed (severity-marked)

**BLOCKER — the `V1_GRANDFATHERING` second blocker.** Finding (A). The packet's OPEN-ITEM 7 poses
retroactivity as a magistrate judgment ("does installing require re-authoring?"); it is a mechanical
refusal at `arm_readiness.py:4219-4229`, reached from `_freeze_evidence_for_arm` (`:5383-5392`)
whenever the loaded registry is v2. A council that cured only the byte-pin would have shipped a
registry that still cannot arm the family.

**BLOCKER — refusal-code closure.** Finding (C). `_validate_refusal` (`:1434-1443`) closes both the
code set and the code→type map for every refusal minted into a receipt. Three of the packet's four
V4 alternatives are executably refuted; `readiness_successor_chain_invalid`'s `SUCCESSOR_CHAIN` type
is not expressible in the registry's enum. The brief §2 lists one code delta; there are at least
four (§2 step 2 above).

**BLOCKER — V2 has no comparator, and R1 cannot express one.** No code path reads
`environment_fingerprint` back for comparison; `R1_REFUSAL_ROLES` (`:488-499`) is closed at eight
roles and contains no environment role. The packet's V2 execution-lens instruction is unexecutable,
and its alternatives 1/2 (`EXACT_MATCH`, `INTERPRETER_AND_PLATFORM_ONLY`) are, as written, tokens
for a mechanism that cannot be built inside this transaction's scope.

**SHOULD-FIX — factual error in `02-…:120-134`.** The packet says six kinds record a fingerprint and
"the other ten record no fingerprint today and would need new derivation work to compare anything."
False: `_execution_environment_fingerprint(context, item.kind)` is called for **every**
EXECUTION_BOUND kind on the generic-deriver path (`arm_readiness_evidence.py:2427-2430`), and
`_assemble_r1_receipt` **refuses** if the fingerprint is absent (`:1968-1973`).
`_ENVIRONMENT_FINGERPRINT_KINDS` (`:107-116`) only sets the boolean fact
`"amendment5_required_kind"` (`:457`). The packet's V2 alternative 4 (per-kind mixture) rests
entirely on the false premise.

**SHOULD-FIX — the registry horizon and the T-0 horizon are two independent numbers for the same
kind, and nothing cross-checks them.** `arm_readiness_evidence_t0.py` never consults the R1 registry;
its `_validity_horizon_ns` (`:1758-1767`) is the live authority for 13 kinds. The packet's 03 treats
all horizons as live. This is a permanent drift seam unless the install adds the consistency
assertion (V3).

**SHOULD-FIX — four of the fourteen have no R1 authoring lane at all.** `GIT_CHECKOUT`,
`PRIVILEGE_INSTALLATION`, `DRY_RUN_REHEARSAL`, `IDENTITY_PIN_PROJECTION` appear in neither
`_GENERIC_DERIVER_KINDS` (`arm_readiness_evidence.py:89-101`) nor `_ROW_KIND`
(`arm_readiness_evidence_t0.py:88-103`); the last two are additionally rejected by
`_authenticate_generic_evidence_item` (`arm_readiness.py:4230-4234`). Their ruled values are pure
declaration and the ruling must say so.

**SHOULD-FIX (execution confirmation owed) — an R1 freeze-evidence refusal is fail-ugly, not
fail-closed.** `_freeze_evidence_for_arm` (`:5360-5392`) is called from `generate_arm_receipt` at
`:6139-6140` with **no enclosing `try`** (verified: no `try:` between `def generate_arm_receipt` at
`:6096` and that call). `EvidenceLifecycleError` is a `ValueError`, not an `ArmReadinessError`, so an
R1 refusal on the frozen freeze-evidence path escapes as an uncaught exception rather than becoming
a receipt refusal — contrast `_discover_evidence`, which catches it (`:4613`) and appends
`exc.refusal()`. The install is what activates this path. Needs one executed confirmation and, if
confirmed, a four-line catch in the same transaction.

**GOOD NEWS the packet costed wrongly — per-kind tiering is free.** Every one of the 35 rows requires
exactly one evidence kind, so `len(expected_policy_ids) != 1` (`:1913-1925`) is unconditionally
satisfiable and distinct policy ids may carry identical definitions (`:1637-1651` forbids only the
converse). Both `02-…:203-206` and `03-…:146-152` list row-map agreement as a cost of tiering; it is
not, and that removes the main argument for uniform horizons.

**MISSING — the standing cost of installing at all.** Once `_v4` pins the registry, every future
registry edit forces a new pack family. The packet never states that the registry becomes a frozen
artifact. This belongs in the ruling as a standing constraint, not as a footnote.

**NIT (citation integrity, but it matters in a contract packet).** Several `file:line` anchors do not
resolve, and `git diff --stat 4597ad4..afb7d57` over these files is empty, so this is not head drift:
`_R1_REGISTRY_KEYS` cited `:479-489` (actual `:500-509`); `_R1_EVIDENCE_POLICY_KEYS` cited `:490-496`
(actual `:510-516`); `_R1_ARM_POLICY_KEYS` cited `:517` (actual `:518`);
`_R1_SUCCESSOR_POLICY_KEYS` cited `:518-523` (actual `:519-524`); `R1_REFUSAL_ROLES` cited
`:488-498` (actual `:488-499`). Two of these ranges (`:479-489` and `:488-498`) **overlap each
other**, so they cannot both be correct at any head — the internal inconsistency is detectable
without a checkout.

### On the D-147 S5 carried limitation (brief §1f / §3, OPEN-ITEM 8)

**Position: CARRY it, with a named owner and a registered statement — do not build it here.**
`_PACKS_BY_PROFILE` (`arm_readiness_evidence.py:49-60`) is the historical `_v1` map and
`_derive_pack_family` iterates it (`:1348-1355`), so `PACK_FAMILY` evidence for a `_v4` pack is
still derived against the `_v1` plan trees. Building the registry-driven successor route means
editing `arm_readiness_evidence.py` — which D-147 S5 left UNEDITED **by design**, on an off-agenda
blocker (*"same-ordinal sibling derivation would break the frozen `_v2` evidence replay that
`evidence-pack-family.json` byte-pins"*, `14-r2-ruling.md:65-74`). Adding it to a transaction that
already carries four code deltas, a schema flip, a family re-freeze and a green gap is exactly the
scope inflation that produces the two-same-signature failures rule 11 legislates against.
**Cost of carrying:** `PACK_FAMILY` is `RE_DERIVABLE` (`arm_readiness.py:695`) and is the required
kind of the `desk.pack_family` row in all three profiles, so every `_v4` pack's family evidence
attests a fact about the `_v1` family. That is a real limitation on the claim's provenance chain and
it must be stated in `CLAIMS_STATUS.md` in plain words — the precedent site for D-148.6/.7
limitations (`docs/decision_log.md:171`) — not merely re-queued. **The ruling must name the owner
and the trigger** (the marker co-design pass is the natural home, since both are successor-family
identity work), because "queued to the install" has now failed to discharge twice.

---

## §4 — Conditions and re-verification (brief §1d), compactly

| Value | Before install | After install |
|---|---|---|
| V1 | the `_v4` roots exist and their names `fullmatch` `_SUCCESSOR_PROFILE_PATTERNS` (`:260-266`) | `_registry_reference(pack)["plan_profile"]` returns ALPHA/BETA/GAMMA for all three; `_v3` returns `readiness_row_registry_mismatch` (intended) |
| V2 | allowlist delta (2a) + comparator (2d) in the same commit | author one `_v4` pack's evidence; then re-run authoring with a different `python3` minor and confirm re-authoring is forced, not silently accepted |
| V3 | the T-0 consistency assertion passes at import | one full author→freeze→arm at the measurement checkout; confirm the arm receipt's `valid_until` is set by the T-0 volatile evidence, not by an EXECUTION_BOUND horizon |
| V4 | reason-code delta (2b) + registry closure check (2c) | force each of the seven wired roles and confirm the emitted code is the registry's; confirm a receipt carrying one validates (`_validate_refusal`) |
| V5 | measured T-0→arm gap < 15 min | temporal-budget gate passes on a real arm; deliberately delay 16 min and confirm it refuses with the ruled `readiness_r1_temporal_budget` |
| V6 | the `*.UNBUILT.v*` canary test exists | `grep -rn family_publication_marker_schema joulewise/ scripts/` still returns only the three schema sites |
| all | file 09's probe re-run against `_v4`: P1/P2/P3 OK | canonical FULL GREEN; `gen_state.py --check` clean |

---

## §5 — Escalation note

Findings (A) and (C) are new blocker-class facts that were not before the magistrate when the
"defer to `_v4`" disposition was drafted, and finding (B) materially changes that disposition's cost
basis. Under CLAUDE.local.md rule 11 this remains a contract-bearing, irreversible-adjacent call for
the **magistrate with a cold-instance pass**; this seat supplies design and executed evidence, and
does not rule. The one thing I would flag as time-critical: finding (B) is a **shrinking** number —
`_v3`'s evidence expires ~2026-08-20T17:00Z, and after that every option in this packet costs the
same `_v4` re-freeze, so the window in which "install now vs defer" is even a live question closes
on its own.
