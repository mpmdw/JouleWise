# D-148.5 REGISTRY-VALUES COUNCIL — BRIEF

**Convening authority:** D-148.5 (Ed, 2026-08-19) —
> "R1 row-registry reserved values → COUNCIL (Ed defers; run the
> co-design/council pass when the Codex pool returns, then proceed)"
> — `docs/decision_log.md:171`

Ed's operative instruction to the loop:
> "**R1 registry values (D-148.5):** Ed defers to council — run the
> co-design/council pass (Codex pool returns ~23:22 tonight; terra/luna seats
> per the roster in T11) over the five reserved values (three proposed = the
> `_v3` pack ids), then install the row registry (queued kernel row,
> kernel-transaction discipline)."
> — `RUN_STATE.md:182-186`

**Base:** `impl/r2-s0-mint-resolver` @ `4597ad4`. **Seats:** per the T11
roster — terra (gpt-5.6-terra, xhigh) and Opus 5, independent designs → one
bounded debate round → Fable ruling; D-144 co-design protocol
(`docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md`,
§"ED PROCESS RULE"; first application custodied at
`docs/process_traces/2026-08-19-r1-r2-codesign/`).

**D-144 classification (proposed, for the magistrate to confirm):** BIG.
This is a contract-bearing install (a schema version change on a
receipt-referenced config, plus a code change to
`_SUPPORTED_ENVIRONMENT_COMPARISONS`) touching the arm/consume path that
gates every claim window. BIG means: implementation gauntlet + Fable final
review + one more seat pass over the implemented artifact pre-merge.

---

## 1. Required outputs

The council must return **all** of the following. A ruling that supplies
fewer is incomplete, because the registry admits no partial install
(`00-INDEX.md` §4).

### 1a. A ruling on the counting (prerequisite)

Which enumeration of "the five" binds — A (the mechanical NEEDS_RULING five)
or B (three pack ids + two others)? See `00-INDEX.md` §1. The packet's
disposition is A, with `successor_pack_ids` as a sixth value reopened by
D-147. **Rule it explicitly**; every downstream artifact says "the five".

### 1b. Six ruled values, each as installable bytes

| # | Field | Packet file | Proposal on record? |
|---|---|---|---|
| V1 | `successor_policy.successor_pack_ids` | `01-…` | **Yes** — the three `_v3` ids |
| V2 | `evidence_policies[].environment_comparison` (16 EXECUTION_BOUND kinds) **+ the code allowlist** | `02-…` | No |
| V3 | `evidence_policies[].horizon_ns` for the 14 unhorizoned EXECUTION_BOUND kinds | `03-…` | No |
| V4 | `refusal_vocabulary` — 8 `{role, code, type}` entries | `04-…` | No |
| V5 | `arm_policy.arm_to_consume_budget_ns` | `05-…` | No |
| V6 | `successor_policy.family_publication_marker_schema` | `06-…` | No |

**The two non-proposed values the packet was asked to find are V2 and V3 —
`environment_comparison` semantics and the 14 EXECUTION_BOUND horizons** —
if one insists on enumeration B's arithmetic (5 − 3 pack ids = 2). Under
enumeration A there are five non-proposed values (V2–V6). Both readings are
presented; the council rules per 1a.

### 1c. Rulings on the fields the five-item list omits but the install requires

The registry will not load with any `ED_RESERVED:` value anywhere. These are
**not** on the five-item list and **must** be ruled anyway:

- `freeze_evidence_lifecycle.registry_id`
  (`ED_RESERVED:r1-lifecycle-registry-id`, `arm_readiness.py:529`)
- `arm_policy.capability_horizon_ns` (`:534`) — has a live consumer, `:6235`
- `successor_policy.cross_chain_numbering` (`:539`)
- `successor_policy.freeze_receipt_v2_predecessor_bindings` (`:540-542`)
- The bulk fills the placeholder ships empty: `irrelevant_path_allowlist`
  (`:530`), `evidence_policies` (`:531`, must cover all 29 kinds),
  `row_policies` (`:532`, must cover all 35 rows in the same sorted order —
  `validate_registry` `:1896-1912`)
- The **outer** row-registry `registry_id`, which under v2 is unconstrained
  (v1's `== ROW_REGISTRY_ID` check applies only to the v1 schema branch,
  `:1853-1858`)

### 1d. Conditions on each ruled value

For each value: what must be true before it is installed, and what must be
re-verified after. At minimum, every ruling states (i) the exact bytes, (ii)
any accompanying code delta, (iii) the test pins it moves, (iv) how it is
re-verified live.

### 1e. A disposition of the BLOCKER in §4

Non-optional. The council may not rule values into a registry that cannot be
installed.

### 1f. A recorded position on the D-147 S5 carried limitation (§5)

---

## 2. The kernel-transaction discipline for the install

Ed's standing formulation, in the short list the loop must never drop:

> "**kernel edits = kernel+regen+pins one transaction**"
> — `RUN_STATE.md:113-119` (standing discipline list)

and the queue's own statement of the mechanism:

> "- Update live status, rank, dependencies, and new tasks in
>   `docs/process/state_kernel.json`.
> - Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
>   restart rows."
> — `TASK_QUEUE.md:429-435`

> "The generated region below is the sole live queue and source of truth for
> work selection. Edit the kernel and regenerate; do not hand-edit its rows."
> — `TASK_QUEUE.md:503-505`

`scripts/gen_state.py` renders the marker-fenced regions of both `RUN_STATE.md`
and `TASK_QUEUE.md` from `docs/process/state_kernel.json`, and `--check`
exits 1 on drift (`scripts/gen_state.py:1-17`). The pins live in
`tests/test_gen_state.py` — notably `EXPECTED_IDS` (`:23`) and
`test_exact_live_id_set` (`:277-286`).

**Therefore the install lands as ONE transaction containing, in one commit
series with no green gap:**

1. **The registry bytes** — the resolved v2 registry at
   `configs/arm_readiness/d117_row_registry_v1.json` (or wherever §4's
   disposition puts it), canonical JSON.
2. **The code delta** — `_SUPPORTED_ENVIRONMENT_COMPARISONS`
   (`joulewise/arm_readiness_evidence.py:119`) gains the ruled token(s).
   Without this the install is inert and issuance still fails closed.
3. **The kernel row** — `docs/process/state_kernel.json`, A63
   `REFREEZE-D147-CLOSE`, whose acceptance clause *"The council pass on the
   five R1 row-registry reserved values is custodied and its values
   installed"* (`state_kernel.json:2834`) is what this transaction discharges.
4. **The regeneration** — `python3 scripts/gen_state.py`, then
   `python3 scripts/gen_state.py --check` clean.
5. **The test pins** — at minimum
   `tests/test_arm_readiness_evidence.py`:
   `lifecycle_registry()` (`:29-88`) and `resolved_r1_row_registry()`
   (`:90-132`) currently encode the **`_v2`** successor ids (`:63-67`,
   `:508-512`) and a fixture-uniform 20-minute horizon (`:104-110`, asserted
   at `:549-555`); `test_successor_profile_ids_install_from_registry_roles`
   (`:492-585`) asserts `_v3` is REFUSED. All move in this transaction.
   `tests/test_gen_state.py` pins move if the kernel row changes shape.
6. **The custody record** — the council output under
   `docs/process_traces/2026-08-19-…-registry-council/` (or the successor
   date), plus the decision-log entry. Ed's ONE-home discipline applies: the
   ruling is the ONE home; the decision log carries a pointer row, not a
   restatement.
7. **Canonical FULL GREEN at the transaction head** before any merge.

**Landing route:** the merge wave is gate-authorized, not Ed-authorized —
D-148.2: *"MERGE WAVES ARE GATE-AUTHORIZED, NOT ED-AUTHORIZED — the
rule-4/D-072 gate shape (council/lead review, CI green, fresh pass over
post-review commits) is the complete authority for merging"*
(`docs/decision_log.md:171`). The A63 fence names the wave:
`impl/r2-s0-mint-resolver` → `integration/phase2-transaction` → `main`
(`TASK_QUEUE.md:585`).

**One writer per tree.** Assembler discipline for this whole prep arc:
> "packet assemblers run read-only and write to session scratch; the LEAD
> lands their outputs into `docs/process_traces/...` serially (one writer per
> tree)."
> — `RUN_STATE.md:54-58`

---

## 3. Carried limitation on the successor PACK_FAMILY route (D-147 S5) — CITE THIS IN THE RULING

D-147 S5, verbatim:

> "**S5 — Touch points.** Opus C1–C5 and C7–C9 as written, as amended by the
> debate; C6 replaced by S4. terra F3's evidence-author row is STRUCK
> (off-agenda blocker upheld: same-ordinal sibling derivation would break the
> frozen `_v2` evidence replay that `evidence-pack-family.json` byte-pins);
> `arm_readiness_evidence.py` is UNEDITED this transaction and **the successor
> PACK_FAMILY route stays queued to the arm_readiness row-registry install as
> a recorded carried limitation.** Evidence-author acceptance copy-list gains
> r3+r4+r5 INSIDE the transaction (necessity). `_ACCEPTANCE_SELECTION` does
> not move (renaming it is noted as a separate independent-axis decision, not
> taken here)."
> — `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:65-74`

**What the limitation actually is, in code.** `PACK_FAMILY` evidence derives
from a hardcoded historical map:

```python
# The inverse of arm_readiness._PROFILE_BY_PACK, and immutable for the same
# reason: it is the HISTORICAL v1 family, and the committed v1 PACK_FAMILY
# evidence was derived against exactly these three plan trees.  Successor
# families do not edit this table; a registry-driven successor route for
# PACK_FAMILY derivation is NOT yet built (reported to the magistrate with the
# R1 registry install).
_PACKS_BY_PROFILE = {
    "ALPHA": "d117_floor_qwen25_1p5b_v1",
    "BETA": "d117_floor_qwen25_7b_v1",
    "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v1",
}
```
(`joulewise/arm_readiness_evidence.py:49-60`)

`_derive_pack_family` iterates that map (`:1348-1355`) and cross-checks the
three plan trees' identity arms. So **`PACK_FAMILY` evidence for a `_v3` pack
is still derived against the `_v1` plan trees.** `PACK_FAMILY` is
`RE_DERIVABLE` (`arm_readiness.py:696`) and is a required evidence kind of the
`desk.pack_family` row, present in all three profiles
(`configs/arm_readiness/d117_row_registry_v1.json`).

**The council owns this because D-147 queued it here.** The ruling must state
either (a) the registry install builds the registry-driven PACK_FAMILY
successor route — in which case that is additional scope, additional code in
`arm_readiness_evidence.py` (which D-147 left UNEDITED), and a new gauntlet —
or (b) the limitation is carried forward again with a named owner and a
registered statement, in which case say where it is registered
(`CLAIMS_STATUS.md` is where D-148.6/.7 limitations went) and what it costs
the claim.

Do not let it pass silently a second time. The provenance note in
`35badb4`'s reconciliation was explicit that this was *"reported to the
magistrate with the R1 registry install"* — this council **is** that install.

---

## 4. BLOCKER — the frozen `_v3` packs byte-pin the current registry's sha256

**Discovered during assembly on 2026-08-19; not on the record before this
packet. Every seat must dispose of it before ruling values.**

### The mechanism

Every freeze receipt and every plan tree carries a `row_registry` reference
whose keys are exact:

```python
def _validate_row_registry_reference(value: object, where: str) -> None:
    item = _require_exact_keys(value, ROW_REGISTRY_REFERENCE_KEYS, where)
    _require_string(item["registry_id"], f"{where}.registry_id")
    _require_relative_path(item["path"], f"{where}.path")
    _require_lower_sha256(item["sha256"], f"{where}.sha256")
```
(`joulewise/arm_readiness.py:1349-1358`)

It is built from the **live** registry bytes at validation time:

```python
def _registry_reference(pack_root: Path) -> tuple[Mapping[str, Any], bytes, dict[str, str]]:
    repository = _repo_for_pack(pack_root)
    registry, raw = load_registry(repository)
    committed_raw = _git_blob_at_head(
        repository, ROW_REGISTRY_RELATIVE_PATH.as_posix()
    )
    if committed_raw != raw:
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            "row registry bytes are not the committed HEAD bytes",
        )
    profile = _plan_profile(pack_root, registry)
    reference = {
        "registry_id": registry["registry_id"],
        "path": ROW_REGISTRY_RELATIVE_PATH.as_posix(),
        "sha256": sha256_bytes(raw),
        "plan_profile": profile,
    }
    return registry, raw, reference
```
(`joulewise/arm_readiness.py:2764-2782`)

and compared for **exact equality** against the frozen artifacts in at least
three places:

```python
item["row_registry"] != expected        # plan-tree declaration
```
(`:2798`, in `_valid_plan_attachment`, called at `:5161` from
`_load_freeze_reference` and at `:5426` from `generate_freeze_receipt`)

```python
if receipt["row_registry"] != registry_reference:
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        "freeze receipt registry binding differs from the plan",
    )
```
(`:5181-5185`)

```python
if receipt["row_registry"] != registry_reference:
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        "arm receipt registry binding differs from committed bytes",
    )
```
(`:6301-6305`)

### The measured facts in this checkout

- `shasum -a 256 configs/arm_readiness/d117_row_registry_v1.json` →
  `d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5`
- `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`
  contains:
  ```json
  "row_registry": {
    "path": "configs/arm_readiness/d117_row_registry_v1.json",
    "plan_profile": "ALPHA",
    "registry_id": "d117-row-registry-v1",
    "sha256": "d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5"
  }
  ```
- `configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json` →
  `arm_attachments.arm_readiness.row_registry` carries the **identical**
  object.
- Both are inside a **frozen, byte-immutable** pack. D-147 S3:
  *"The three `_v2` pack roots … are READ-ONLY"* and the same immutability
  attaches to `_v3` once `freeze-0003` is minted (the receipt authenticates
  `committed_pack_tree_sha256`).

### The consequence

Any install that changes the bytes at
`configs/arm_readiness/d117_row_registry_v1.json` changes its sha256 — that
is unavoidable, since a v2 registry adds the `freeze_evidence_lifecycle` key
— and therefore:

- `registry_id` and/or `sha256` in the live reference no longer equal the
  values byte-pinned in all three `_v3` plan trees and all three
  `freeze-0003` receipts;
- `_valid_plan_attachment` refuses with `readiness_row_registry_mismatch`
  ("plan arm-readiness declaration differs from D-134");
- **freeze verification, dry-run, arm, and consumption all refuse for all
  three frozen `_v3` packs.**

The three `_v3` packs are the claim campaign. If this reading is correct, the
registry install as scheduled **destroys the frozen family's ability to
arm**, and it cannot be repaired by re-minting (the packs are immutable and
D-131 forbids rewriting issued bytes).

### What the council must do with it

1. **Refute or confirm it, executably.** Build a scratch clone, write a v2
   registry to the path, commit, and run freeze-verify / dry-run against a
   `_v3` pack. Report the observed reason code. This is a 20-minute
   experiment and it decides the whole session.
2. If confirmed, rule the disposition. Candidates, none free:
   - **Defer the install** past the windows; `_v3` continues to arm through
     the shape-only route (`arm_readiness.py:2717-2727`), and the R1 lifecycle
     mechanism stays dormant for this campaign. Cheapest; costs the mechanism.
   - **New registry path** for the v2 registry, leaving the v1 file
     untouched. Requires changing `ROW_REGISTRY_RELATIVE_PATH` (`:80`) —
     but `path` is itself pinned in the frozen artifacts, so the pinned
     reference would then name a file the code no longer loads. Probably
     worse, not better; needs design.
   - **A fourth pack family (`_v4`)** minted after the registry install, so
     the receipts pin the new registry. Enormous cost; another freeze cycle
     at Ed's measurement checkout, another confirmation table.
   - **A code-level grandfathering rule** for the registry reference — a
     contract change on the authentication path, which is exactly the kind of
     change the R1/D-134 lineage has repeatedly refused.
3. **Escalate rather than improvise.** Under CLAUDE.local.md rule 11 this is
   an irreversible-adjacent, contract-bearing call: it belongs to the
   magistrate with a cold-instance pass, not to the lieutenant or to a seat.

---

## 5. Standing discipline binding this council

- **No partial install.** `_r1_contains_reserved` + `require_resolved=True`
  (`arm_readiness.py:1501-1508`, `:1795-1804`).
- **No placeholder is a value.** *"no placeholder is a reason code"*
  (`docs/decision_log.md:9303-9304`).
- **The registry cannot override code.** *"Registries name policy IDs and
  class-specific parameters, but can neither introduce an evidence kind nor
  choose its class"* (`arm_readiness.py:671-675`); enforced by the
  `class_mismatches` path (`:1573-1580`, `:1786-1790`).
- **Two same-signature failures → consult, not round three** (standing
  escalation trigger, CLAUDE.local.md rule 11).
- **The lead verifies receipts itself** (rule 1; `RUN_STATE.md:113-119`).
- **Split verdicts are synthesized by the magistrate, not majority-voted**
  (hard rule 9).
- **D-078 no-retry** governs anything that touches a window.
