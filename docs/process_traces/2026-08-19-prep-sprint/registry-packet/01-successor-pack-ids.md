# V1 — `successor_policy.successor_pack_ids`  (PROPOSED, 3 values)

## Field

`freeze_evidence_lifecycle.successor_policy.successor_pack_ids` — a mapping
`{ALPHA, BETA, GAMMA} → pack id string`.

Placeholder in code:

```python
"successor_policy": {
    "successor_pack_ids": "ED_RESERVED:successor-pack-ids",
```
(`joulewise/arm_readiness.py:538`)

## Schema requirement (validator code, verbatim)

Key set is exact:

```python
_R1_SUCCESSOR_POLICY_KEYS = {
    "successor_pack_ids",
    "cross_chain_numbering",
    "freeze_receipt_v2_predecessor_bindings",
    "family_publication_marker_schema",
}
```
(`joulewise/arm_readiness.py:518-523`)

Value shape (`validate_r1_lifecycle_registry`):

```python
pack_ids = successor_policy["successor_pack_ids"]
if not (
    (isinstance(pack_ids, str) and pack_ids.startswith(_R1_ED_RESERVED_PREFIX))
    or (
        isinstance(pack_ids, Mapping)
        and set(pack_ids) == set(_SUCCESSOR_PROFILE_PATTERNS)
        and all(
            isinstance(pack_id, str)
            and pack_id
            and "/" not in pack_id
            and "\\" not in pack_id
            for pack_id in pack_ids.values()
        )
        and len(set(pack_ids.values())) == 3
    )
):
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        "R1 successor pack IDs are invalid",
    )
```
(`joulewise/arm_readiness.py:1698-1719`)

So: exactly the three profile keys, three **distinct** non-empty
path-separator-free strings.

A second, independent gate applies at admission. `_plan_profile` only accepts
a registry-installed successor id if it **also** matches the D-139-approved
name shape:

```python
installed = lifecycle["successor_policy"]["successor_pack_ids"]
if isinstance(installed, Mapping):
    matches = [
        profile
        for profile, pack_id in installed.items()
        if pack_id == pack_root.name
    ]
    if len(matches) == 1:
        profile = matches[0]
        pattern = _SUCCESSOR_PROFILE_PATTERNS.get(profile)
        if pattern is not None and pattern.fullmatch(pack_root.name):
            return profile
        raise ArmReadinessError(
            "readiness_row_registry_mismatch",
            f"registry-installed {profile} successor ID has an unapproved shape",
        )
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"successor ID {pack_root.name!r} is not installed by the R1 registry",
    )
```
(`joulewise/arm_readiness.py:2693-2716`)

with

```python
_SUCCESSOR_PROFILE_PATTERNS = {
    "ALPHA": re.compile(r"^d117_floor_qwen25_1p5b_v(?:[2-9]|[1-9][0-9]+)$"),
    "BETA": re.compile(r"^d117_floor_qwen25_7b_v(?:[2-9]|[1-9][0-9]+)$"),
    "GAMMA": re.compile(
        r"^d117_contrast_qwen25_1p5b_vs_7b_v(?:[2-9]|[1-9][0-9]+)$"
    ),
}
```
(`joulewise/arm_readiness.py:260-266`)

`_v3` matches all three patterns. No code change is needed to install `_v3`.

## Proposed value

```json
"successor_pack_ids": {
  "ALPHA": "d117_floor_qwen25_1p5b_v3",
  "BETA":  "d117_floor_qwen25_7b_v3",
  "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v3"
}
```

## Justification chain

1. **D-147 ratified the `_v3` family as the artifact layer.**
   > "(ii) ARTIFACT LAYER: a new immutable `_v3` pack family
   > (`d117_floor_qwen25_1p5b_v3`, `d117_floor_qwen25_7b_v3`,
   > `d117_contrast_qwen25_1p5b_vs_7b_v3`)."
   > — `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:16-21` (S1)

2. **The family is FROZEN with `freeze-0003`.** D-147 S3:
   > "PARKED STEP 6 IS AMENDED: freeze-0003 mints on the `_v3` roots at the
   > measurement checkout (`/Users/edr/JouleWise-measurement-20260818`,
   > path-binding), ordinal = predecessor+1, `predecessor` binding each pack's
   > `_v2` + its freeze-0002. No freeze-0002 re-mint anywhere."
   > — `14-r2-ruling.md:42-47`

3. **The mints executed and are committed.** Confirmation table (marked
   *"COMPLETE — S5 executed 2026-08-19 under D-148.1"*),
   `docs/process/ed-s5-mint-decision-2026-08-19.md:71-88`:

   | Pack | `freeze-0003` receipt sha256 | committed pack tree digest |
   |---|---|---|
   | `d117_floor_qwen25_1p5b_v3` | `0abfddb13fe8c5e69df3e6be5e2e7efe28d3690b6947d5ed850fcb9652f6ec64` | `1e3f1fa31027e57053c7d26bacf2f373cf2c9ed840ee2bb3befafd99302d63f6` |
   | `d117_floor_qwen25_7b_v3` | `f232d076d54408851e5728b3f14e9b04e086d809bca3e1cdac0c3641e072578c` | `6d0b9b758d6a37a69a88827cb47ac58566d957099a3e714143d2e6508a93e45f` |
   | `d117_contrast_qwen25_1p5b_vs_7b_v3` | `f32bd3a8e4dbd04bc5b1635818ba34394984d1d201d16f02efc21f0b01f31c73` | `0d07194143702b266267f0faa7b051695ffb5e1c56dc7a69d0b2dca8aaa883ef` |

   Predecessor `_v2` `freeze-0002` shas that the receipts bind (same table):
   `1277103b…` (1p5b), `decd8cdc…` (7b), `18855647…` (contrast).

   Verified in this checkout — `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`
   carries `"receipt_id": "freeze-0003"`, `"status": "PASS"`,
   `"schema_version": "joulewise.arm_readiness_freeze_receipt.v2"`, and
   `predecessor.freeze_receipt.sha256 = 1277103b42090f3ce41df0e030a2a5f2a3998598efec12fef812ca5b36b89666`
   matching the table.

4. **The pack ids must name `_v3` or admission refuses.** The R2 design seat
   proved the interaction:
   > "**Interaction to record:** if the R1 *row registry* install (a distinct
   > item from R1 the capture-flip ruling) lands before the `_v3` freeze, it
   > MUST install `successor_pack_ids = {ALPHA: …_1p5b_v3, BETA: …_7b_v3,
   > GAMMA: …_contrast_…_v3}` or `_plan_profile` refuses with
   > `readiness_row_registry_mismatch` (`:2713-2716`)."
   > — `06-r2-design-opus.md:471-475`

   The freeze in fact landed **first**, so the constraint is now
   unconditional: the installed registry is the only route by which a `_v3`
   pack resolves to a profile once a v2 registry is present (the shape-only
   fallback at `arm_readiness.py:2717-2727` is bypassed whenever the loaded
   registry is v2 and names a conflicting or absent mapping).

5. **The `_v2` ids are wrong now.** D-139 A3 approved *"uniform `_v2`
   successor pack IDs"* (`docs/decision_log.md:10078-10085`); D-147 S3 made
   the `_v2` roots read-only history (*"`freeze-0002` receipts stand
   forever"*, `14-r2-ruling.md:45`) and `_v3` the live family. Installing
   `_v2` would pin the registry to the superseded arm.

## Alternatives a seat could argue

- **A. Install `_v2`, not `_v3`** — literal compliance with D-139 A3.
  Refuted by D-147 S3 and by open question 3 of the R2 design
  (`06-r2-design-opus.md:719-726`): `_plan_profile` "admits only one pack per
  profile through the registry route (`arm_readiness.py:2699-2712` requires
  exactly one match), so a parallel arm would need a design I have not
  built." A seat arguing A must explain how `_v3` then arms at all.
- **B. Retain a parallel `_v2` arm** — explicitly *not designed*; same
  citation. The magistrate's recorded lean is single-arm supersession
  ("complete the cycle"). A seat arguing B is proposing new design work
  inside a close-out transaction.
- **C. Defer the whole install until after the windows**, leaving the v1
  registry live and `_v3` admitted by the shape-only route
  (`arm_readiness.py:2717-2727`). This is the *status quo* and — see
  `07-council-brief.md` §4 — may be the only option that does not break the
  frozen packs. A seat should argue this on the merits, not as inertia: it
  costs the registry-driven successor route (and with it the PACK_FAMILY
  successor route, D-147 S5) for the whole claim campaign.
- **D. Install `_v3` at a NEW registry path** so the frozen packs keep
  authenticating against the old bytes. Requires changing
  `ROW_REGISTRY_RELATIVE_PATH` (`arm_readiness.py:80`), which is itself
  pinned inside every frozen receipt's `row_registry.path`. See
  `08-open-items.md` OPEN-ITEM 2.

## Evidence each seat should check

- **Contract lens:** that `set(pack_ids) == set(_SUCCESSOR_PROFILE_PATTERNS)`
  is satisfied and all three values are distinct (`:1698-1719`); that each
  proposed id `fullmatch`es its profile pattern (`:260-266`); that
  `_plan_profile`'s historical short-circuit (`:2689-2691`,
  `_PROFILE_BY_PACK` at `:255-259`) still returns the v1 mapping unchanged —
  the immutability invariant restored by `35badb4`.
- **Execution lens:** run
  `python3 -m unittest tests.test_arm_readiness_evidence` and specifically
  `R1EvidenceLifecycleTests.test_successor_profile_ids_install_from_registry_roles`
  (`tests/test_arm_readiness_evidence.py:492-585`) — it constructs a real git
  repository, writes `resolved_r1_row_registry()` to
  `ROW_REGISTRY_RELATIVE_PATH`, commits, and asserts
  `_registry_reference(installed_pack)["plan_profile"] == "ALPHA"`. That test
  currently installs the **`_v2`** ids (`:508-512`) and asserts that a `_v3`
  pack is REFUSED until added (`:515-525`). It is a test pin that the install
  transaction must move.
- **Both:** re-verify the three `freeze-0003` shas against the working tree
  (`shasum -a 256 configs/campaigns/*_v3/arm_readiness.freeze.receipts/freeze-0003.json`)
  and against the confirmation table — the table is the artifact Ed will
  confirm byte-for-byte at the irreversible point.
