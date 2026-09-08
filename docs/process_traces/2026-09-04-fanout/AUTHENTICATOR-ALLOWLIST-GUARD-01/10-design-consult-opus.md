# AUTHENTICATOR-ALLOWLIST-GUARD-01 — design consult, Opus seat (contract lens)

Read-only worktree `JouleWise-wt-auth-consult` at `eff3304e` (mission PARKED);
all file:line citations are at that head.

## 0. Executed evidence (run this session, in this worktree)

`load_registry('.')`, deep-copy, then validate:

- **(a)** `registry_id='d117-r1-lifecycle-v2'` + append
  `configs/arm_readiness/future-confirmation-token.json`, `validate_registry`
  -> **ACCEPTED**.
- **(b)** `successor_pack_ids='ED_RESERVED:…'` + the same extra path,
  `validate_r1_lifecycle_registry(require_resolved=False)` -> **ACCEPTED**.

(a) is the third occurrence (`08-delta-reaudit-rescope.md` F1). **(b) is a
FOURTH escape no trace names:** the branch at `joulewise/arm_readiness.py:1955`
is skipped by its `isinstance(pack_ids, Mapping)` conjunct too, so a
placeholder-shaped registry carries an arbitrary allowlist. A cure that fixes
only the `registry_id` conjunct leaves (b) live — occurrence five.

## 1. The structural diagnosis the traces stop one step short of

The guard is not opt-in because of a decorator or a registry id. It is opt-in
because **D-151 §7 is a negative rule over an open class** — "no authenticator
path ever enters any allowlist" (`docs/decision_log.md:194`;
`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:92-96`).
Implementing a negative rule over an open class requires *classifying* a
candidate as in-class, and "is this an authenticator" is undecidable in Python
(`06-consult-sol-structural.md` F1, correct).

The positive dual is decidable and is D-151's own recorded alternative,
V-1(vii) (`MAGISTRATE-RULING-O1.md:114-115`, still filed as *dissent*): the
allowlist is EXACTLY the derived governed-artifact manifest. Under the dual, "no
authenticator path enters" is a *consequence* (an authenticator is not a
governed pre-registration output of a pack), never a test. Round 07 implemented
the dual but re-opened the class one level up, in the *applicability* predicate
rather than the membership predicate. **Totality of the predicate is part of the
mechanism** — neither the 06 ruling nor the 07 brief said so.

## 2. (1) The CLOSED SET and where the enumeration lives

The governed artifact families that may ever carry an allowlist entry, as a
frozen constant `_R1_IRRELEVANT_PATH_SPEC` in `joulewise/arm_readiness.py`
(git-anchored, not itself in the 112, and edits to it land in the R1 relevant
set — the V-1(vi) tripwire D-151 §7 asks for):

| # | Family | Template | Count |
|---|---|---|---|
| F1 | generic evidence | `configs/campaigns/{pack}/arm_readiness.evidence/evidence-{stem}.json` | 33 |
| F2 | evidence sidecar | `… .json.sha256` | 33 |
| F3 | evidence source | `configs/campaigns/{pack}/arm_readiness.sources/{stem}.json` | 33 |
| F4 | PASS freeze receipt | `configs/campaigns/{pack}/arm_readiness.freeze.receipts/freeze-{ordinal:04d}.json` | 3 |
| F5 | freeze sidecar | `… .json.sha256` | 3 |
| F6 | plan tree | `configs/campaigns/{pack}/plan_tree.json` | 3 |
| F7 | plan-tree sidecar | `configs/campaigns/{pack}/plan_tree.sha256` | 3 |
| F8 | digest-conditional successor pinset | `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` (`:2952`) | 1 |

3 × (11×3 + 4) + 1 = **112**, D-151 condition 1's ruled number, byte-unchanged;
the 11 stems are the existing tuple at `:641-652`.

**Spec pin, not output pin.** `_R1_IRRELEVANT_PATH_SPEC_SHA256 =
sha256(render_json(spec))` in the same module REPLACES
`_R1_ALLOWLIST_PROVENANCE_SHA256` (`:638-640`), which pins the *rendered
manifest of one family generation* — the reason round 07 could not apply its
check to any other registry and reached for an id gate. Pin the rule, derive the
output.

## 3. (2) Membership derivation with no opt-in

```python
def _r1_derive_irrelevant_paths(
    *,
    successor_pack_ids: Mapping[str, str] | str,          # lifecycle successor_policy
    freeze_receipt_ordinals: Mapping[str, int] | str,     # lifecycle successor_policy (NEW)
    spec: Mapping[str, Any] = _R1_IRRELEVANT_PATH_SPEC,
) -> tuple[str, ...]:
    """Total. Returns () when any input is an ED_RESERVED placeholder."""
```

Inputs, exhaustively: the pinned spec, the three successor pack ids, the
per-profile freeze ordinal. **`registry_id` is not a parameter**, and **the
candidate allowlist is not a parameter** — the fixed point rounds 01/03 broke.
No filesystem read, no callable introspection, no name matching.

`freeze_receipt_ordinals` is a NEW required `successor_policy` key (schema bump
to `…freeze_evidence_lifecycle_registry.v2`), `{ALPHA:4, BETA:4, GAMMA:4}` live.
It is what `:1697-1699` hardcodes and what
`tests/test_arm_readiness_lifecycle.py:141-160` re-implements by substitution for
generations 1/2/4. Ordinals are scalars in the row-registry file, which is not in
the 112, so declaring one costs a reviewed edit visible in the changed set.

Enforcement replaces `:1955-1962` entirely, with no branch:

```python
derived = _r1_derive_irrelevant_paths(
    successor_pack_ids=successor_policy["successor_pack_ids"],
    freeze_receipt_ordinals=successor_policy["freeze_receipt_ordinals"],
)
if tuple(allowlist) != derived:
    extra   = sorted(set(allowlist) - set(derived))
    missing = sorted(set(derived) - set(allowlist))
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"ALLOWLIST_NOT_DERIVED: extra={extra!r} missing={missing!r}")
```

Why a future registry id with an extra path cannot pass: the id never reaches
the predicate, and the predicate sits on the single path through
`validate_r1_lifecycle_registry` (`:1718`), which every consumer already funnels
through (`validate_registry:2093`, `load_registry:2775`, `_r1_policy_for_kind:2065`,
`_r1_refusal_entry:2081`, `arm_readiness_evidence.py:2652,2691`). A novel id
derives its own 112 from its own pack ids; the extra path lands in `extra` and
refuses. (b) closes because placeholder inputs derive `()`.

## 4. (3) Refusal codes and the ONE test

**No new reason code.** Keep `readiness_row_registry_mismatch`: a new code
incurs the D-157 R-2 registry-vocabulary coverage obligation
(`:1982-2048`) for zero gain. Three message stems, asserted by name so a silent
widening fails a test:

| Stem | Condition |
|---|---|
| `ALLOWLIST_NOT_DERIVED` | candidate ≠ derived (extras and missings both printed) |
| `ALLOWLIST_SPEC_DIGEST` | `render_json(spec)` ≠ `_R1_IRRELEVANT_PATH_SPEC_SHA256` |
| `ALLOWLIST_INPUTS_UNRESOLVED` | derived is `()` and the candidate is nonempty |

**The one test a fresh id + extra path must fail**, in
`tests/test_arm_readiness_schemas.py` —
`test_fresh_registry_id_with_extra_allowlist_path_is_refused`: `load_registry(ROOT)`,
deep-copy, set `freeze_evidence_lifecycle["registry_id"] =
"d117-r1-lifecycle-v99-unseen"` (never-registered), append
`configs/arm_readiness/future-confirmation-token.json` to the allowlist, sort,
then `assertRaises(ArmReadinessError)` on `validate_registry(m)` asserting
`reason_code == "readiness_row_registry_mismatch"` and that the message contains
both `ALLOWLIST_NOT_DERIVED` and `future-confirmation-token.json`.

It names no authenticator, registers nothing, mutates no production constant and
supplies no role/path binding, so no round-01/03/07 mechanism passes it.
Required mutation kills, all three:

- **M1** reinstate `and registry_id == "d117-r1-lifecycle-v1"` → this test alone
  fails "ArmReadinessError not raised" *(kills occurrence three; the 06
  acceptance could not express this, having fixed the tracked id)*.
- **M2** tautologize the set predicate → fails *(kills the 07 acceptance's kill)*.
- **M3** delete the `ALLOWLIST_INPUTS_UNRESOLVED` clause → the companion
  unresolved-inputs test fails *(kills escape (b))*.

## 5. (4) Salvage vs rebuild — SALVAGE, four deletions

The 07 landing is the right mechanism with an under-parameterized derivation;
rebuilding would discard a correct decorator/registry removal and a real
acceptance test. Delete exactly:

1. `joulewise/arm_readiness.py:1955` — the `registry_id == "d117-r1-lifecycle-v1"`
   conjunct **and** the `isinstance(pack_ids, Mapping)` conjunct (escape (b)).
2. `:638-640` — `_R1_ALLOWLIST_PROVENANCE_SHA256`, the rendered-output pin;
   replaced by the spec pin.
3. `:1697-1699` — the `freeze-0004` literal; replaced by the ordinal input.
4. `:1672-1714`'s manifest-dict return — return `tuple[str, ...]`, so no digest
   is taken over the derivation's output.

Test-side, mandatory (the defect `02-refuter-merge-base.md` F1 named, surviving
in the fixtures): `tests/test_arm_readiness_lifecycle.py:141-163` and
`tests/test_arm_readiness_evidence.py:30-49` must build fixture allowlists by
CALLING `_r1_derive_irrelevant_paths`, not by string substitution — today they
re-implement the derivation and so assert a binding they author.

Keep: the stems tuple (`:641-652`), `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS`
(`:2952`) and its D-151 condition-2 gate (`:4701-4756`, untouched), and
`test_allowlist_refuses_novel_entry_absent_from_governed_artifact_provenance`
(`tests/test_arm_readiness_schemas.py:531-550`).

WRITE_SCOPE: `joulewise/arm_readiness.py`,
`configs/arm_readiness/d117_row_registry_v2.json` (ordinals key only; the 112
bytes unchanged), `tests/test_arm_readiness_{schemas,lifecycle,evidence}.py`,
plus the trace file. Acceptance runs those three modules plus
`tests/test_receipt_histsem.py` (reads the allowlist at `:2002`).

## 6. (5) Decision-log entry — YES, and it is not the lieutenant's to adopt

One row, because the cure changes the OPERATIVE FORM of a cold-gate ruling and
promotes a recorded dissent:

> **D-1xx — R1 irrelevant-path allowlist is DERIVED, not declared.** D-151 §7's
> negative fixed-point rule is restated in its positive dual: the allowlist is
> exactly `_r1_derive_irrelevant_paths(spec, lifecycle successor record)`, with
> §7 retained as rationale, not as a test. V-1(vii)'s derived,
> digest-authenticated manifest is PROMOTED from recorded structural dissent
> (`MAGISTRATE-RULING-O1.md:114-115`) to adopted mechanism. The predicate is
> TOTAL: no `registry_id`, resolvedness, or generation branch may gate it;
> placeholder inputs derive the empty set and refuse any nonempty allowlist.
> Conditions 1-9 and the 112 count are unamended. Under D-161(1) a reviewed
> `--refresh-allowlist` lane re-derives and prints the diff for an ordinary PR.

Rule-11 routing: amending a cold-gate ruling's operative text and promoting a
dissent are both process-rule amendment and verdict reinterpretation —
**cold-gate / magistrate, not lieutenant.**

D-161 check: the fence stays fail-closed. Its actor is not the operator
mis-clicking but a pre-registration classification error letting subject and
authenticator move together (`docs/contracts/d117_step6_confirmation_table.md:76-93`),
which D-161(2) enumerates as PRE-REGISTRATION and exempts from the prune
(`docs/decision_log.md:207`). The refresh lane is D-161(1) verbatim and removes
the only ergonomic cost (hand-editing 112 paths at the `_v6` transition).

## 7. Where I DISAGREE with the earlier rulings

- **D-151 §7's form.** As a negative rule over an open class it is
  unimplementable; three seats proved that empirically. It should have been
  recorded in the positive dual on 2026-08-22 — V-1(vii) was filed as *dissent*
  when it was the only decidable formulation. A ruling-shape defect, not three
  seat failures.
- **The 06 acceptance clause is insufficient and partly caused occurrence
  three.** "one novel-name extra-entry regression … plus its exact-set-comparison
  mutation kill" is satisfiable by an id-gated check, because the regression uses
  the TRACKED registry. The missing words are *fresh registry identity* and
  *total predicate*; the brief named no counterfactual input.
- **Same-signature counting.** Occurrence three arose from an under-specified
  ruling, not a seat repeating a known error; the count should reset once the
  acceptance names M1-M3, rather than the row reading as thrice-failed.
- **Parking was right; a fourth re-scope without a written spec would not be.**
  Hand the next seat §§2-5 of this file as the specification.
