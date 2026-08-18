```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Structural ruling: separate target-pack identity from preservation mechanics; the present fix closes v1-to-v2 writes but not emitted-pack preservation or transitive v2-to-v3 safety.",
  "workspace": {
    "base_requested": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "base_mode": "exact",
    "head_start": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "head_end": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "upstream_end": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "branch": "impl/successor-generator-repairs"
  },
  "pathspec": [],
  "unowned_dirty": [
    "configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py",
    "configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py",
    "tests/test_d117_decode_contrast_plan.py",
    "tests/test_d117_floor_qwen25_1p5b_plan.py",
    "tests/test_d117_floor_qwen25_7b_plan.py"
  ],
  "verdict": {
    "terminating_design": "target-pack identity controls paths and semantic bytes; preservation controls only replay of already-frozen authority bytes",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "Extraction-spec paths remain invocation-mode keyed and emitted floor generators overwrite v1"
      },
      {
        "id": "B2",
        "severity": "blocker",
        "title": "Successor semantics remain invocation-mode keyed, so preserve mode removes lineage and changes dependent bytes"
      },
      {
        "id": "B3",
        "severity": "blocker",
        "title": "JSON draft_status emissions remain hardwired and do not yet execute the M-2 successor-freeze contract"
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "title": "Successor fixture links are order-dependent"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 53 tests in 10.224s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 53 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse @{upstream}; git diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD and upstream = 6ddeb7d365772335717e3143dceccf4382c49f8d",
          "five pre-existing dirty paths; no review writes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "6ddeb7d"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "disposable two-generation probe: generate and git-track each v2 family, run its emitted generator with --preserve-current-frozen-bytes, then inspect tracked diff and run preserve --check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "pristine preserve checks: alpha=1 beta=1 gamma=1",
          "preserve generation exits 0 but changes alpha=109 beta=109 gamma=87 tracked files",
          "alpha and beta each modify their tracked v1 extraction spec"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tracked_changed=0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only design consult; the canonical whole-repository suite was not needed and no proposed implementation exists to verify.",
      "needs": "Next implementation round must execute the regression bar below and the canonical suite."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Preserve-mode producer/plan-tree replay can make --check compare authority files with themselves; an external tracked-diff assertion remains mandatory.",
      "needs": "Do not accept emitted-pack --check alone as the write-boundary regression."
    }
  ]
}
```

## Findings

### B1 — blocker: spec paths are still mode-keyed

The new helpers return the legacy unversioned spec whenever preservation is selected: `configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:304-312` and `configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py:386-394`. That is why emitted v2 generators write v1.

Ruling: derive the spec solely from the target family ordinal:

- `_v1` → legacy unversioned spec.
- `_vN`, `N >= 2` → `..._vN_extraction_spec.json`.

Use that same resolved path for writes, producer references, plan-tree references, and checks. Current call sites are alpha `:1521`, `:1967`, `:2169`, `:2349`; beta `:1112`, `:1894`, `:2336`, `:2616`.

Add a pre-write allowlist: floor generators may write only `target.pack_rel/**` plus exactly `target.extraction_spec_rel`; gamma may write only `target.pack_rel/**`. Resolve and validate the complete write set before the first write.

### B2 — blocker: semantic bytes are keyed to preservation

The complete direct conditional inventory is:

| Conditional class | Confirmed sites | Ruling |
|---|---|---|
| Identity threading | Alpha `generate_configs.py:264`, `:285`; beta `:346`, `:367`; gamma `:176`, `:199` | Key on `target_is_current`, not preservation. A current v2 draft regeneration must not be treated as a new family; v2→v3 must transform. |
| Stored plan references | Alpha `:316`, `:322`; beta `:398`, `:404` | Legacy v1 uses its frozen qualified form. Every successor family uses pack-local `calibration_plan.json` and sidecar in every mode. |
| Reservation `--plan` | Alpha `:888`, call `:903`; beta `:1316`, call `:1349`; gamma `:956`, call `:984` | Omit only for the legacy-v1 byte shape. Every successor family carries the target-pack path in every mode. |
| ARM attachment selection | Alpha `:329`; beta `:411`; gamma `:211` | Derive from the target pack root. Preservation may replay a frozen aggregate afterward but must not choose a predecessor attachment. |
| Projection replay | Alpha `:339`; beta `:427` | This is legitimate custody replay for the current frozen pack; it must never select paths or semantics for a new target. |
| Lineage marker | Alpha `:727`; beta `:720`; gamma `:795` | Key on `target_is_successor_family`. All v2/v3 science configs carry it in every mode. |
| README status/identity | Alpha `:1631-1635`; beta `:1920-1924`; gamma `:1597-1602` | Status comes from target pack freeze state; identity text comes from target family identity. Preservation must not erase v2 identity. |
| Frozen generator hash/replay | Alpha `:1687`; beta `:2449-2451`; gamma `:1673-1678` | Legitimate current-pack custody behavior. New targets use the emitted generator hash; current frozen authority may replay its pinned hash. |
| Producer replay | Alpha `:2003-2010`; beta `:2383-2390` | May remain preservation-keyed, but only for the target pack’s own producer file. |
| Plan-tree/sidecar replay | Alpha `:2190-2201`; beta `:2464-2474`; gamma `:1850-1862` | May remain preservation-keyed, but only pack-locally. It is not sufficient evidence for `--check`; see R2. |

There is no separate intended manifest-hash mode. The 108/108/87 drift is transitive: removing `launch_lineage_required` changes config hashes, then stage/root manifests, extraction membership hashes, producer hashes, tree hashes, and sidecars.

Correct emitted-v2 behavior:

- Current v2, unfrozen/no-preserve: regenerate canonical v2 draft semantics.
- Current v2, preserve: reproduce the same v2 semantic content, retain lineage, target only v2 paths, and replay only v2 frozen authority bytes where required.
- Frozen current v2 with explicit no-preserve: refuse before the first write.
- v2→v3/no-preserve: derive all v3 IDs, paths, tags, generator text, plan references, and specs; leave both v1 and v2 byte-identical.

### B3 — blocker: M-2 status is not fully implemented

The design record requires successor `draft_status` to become freeze-aware (`docs/decision_log.md:9163-9165`; `docs/process_traces/2026-08-16-phase2-plan-consult/consult.md:298`). The generators still hardwire `DRAFT_STATUS` at:

- Alpha: `generate_configs.py:1394`, `:1481`, `:1754`, `:1912`, `:1932`, `:2023`.
- Beta: `generate_configs.py:997`, `:1072`, `:1751`, `:2053`, `:2266`, `:2291`.
- Gamma: `generate_configs.py:517`, `:543`, `:659`, `:1321`, `:1448`, `:1564`, `:1718`, `:1756`.

Gamma also captures current `PACK_STATUS` in shared hardware text at `generate_configs.py:244`; a frozen v2 generator would otherwise leak v2 status into v3 configs.

Ruling: introduce one `target_status(identity)` and use it at every status emission. Current target reads its own freeze attachment; a newly requested successor is draft. The intentional draft→frozen transition happens once during the governed freeze transaction. Subsequent preserve checks must reproduce that final frozen snapshot.

### S1 — should-fix: use a conditional explicit link

Choose the conditional-link fix. At alpha `tests/test_d117_floor_qwen25_1p5b_plan.py:326-338` and beta `tests/test_d117_floor_qwen25_7b_plan.py:325-343`, create the explicit successor-gamma compatibility symlink only when the target does not already exist.

Excluding successor paths from the broad loop is insufficient: an actual gamma v2 generated earlier in the same checkout still occupies the target and the unconditional explicit link still raises. Conditional linking preserves the real generated v2 when present and supplies the compatibility link only when absent.

### Design ruling

D-1. Make `GenerationIdentity` expose parsed `current_ordinal`, `target_ordinal`, `target_is_current`, `target_is_successor_family`, and `target_status`. The mode-validation sites are alpha `:198-208`, beta `:280-290`, and gamma `:113-123`.

D-2. `preserve_current_frozen_bytes` is a custody/replay switch only. It must not determine filenames, family semantics, lineage requirements, identity text, or plan-reference shape.

D-3. Every output path is resolved from the target identity and checked against a closed write set before writing. No “outside pack → return unchanged” fallback may silently authorize a path.

D-4. Preserve-only producer/tree/sidecar replay remains allowed because those are already-frozen authority bytes. The regression must compensate for their known self-echo property with Git-backed byte checks.

D-5. `launch_lineage_required` is successor-family policy, not successor-invocation policy. The adopted stage split calls it a “successor-config” flag (`docs/decision_log.md:9464-9466`), and the owning consult requires it in every successor collection config (`docs/process_traces/2026-08-15-launch-lineage-consult/consult.md:228-236`; phase-2 plan `:295`). Stage-3 consumers are intentionally dormant without it.

D-6. The current status/README freeze transition is the only potentially intended B2 difference. It must be governed by the target’s authenticated freeze state and finalized within the freeze transaction—not by toggling the preservation flag.

D-7. All cited anchors above were mechanically resolved against this worktree after inspection; none are asserted from stale audit line numbers.

### Explicit disagreements

- I reject `docs/decision_log.md:9747`’s sentence “preserve-mode configs never add it.” The first half—every successor config adds the marker—is authoritative; the second half is an implementation-description error. A successor pack remains a successor after freezing.
- I reject framing preservation and successor generation as mutually exclusive semantic families. They are operations over a target identity; preservation cannot change that identity’s content contract.
- I do not recommend reverting the real-checkout fixture or v1 byte/inventory assertions. They caught the first failure and remain necessary.
- I would reshape, not extend, the current spec helper: its filename intent is right, but its preservation branch recreates the class defect.
- I reject default emitted-v2 `--check` as class closure. The current tests at alpha `tests/test_d117_floor_qwen25_1p5b_plan.py:518-525`, beta `tests/test_d117_floor_qwen25_7b_plan.py:524-531`, and gamma `tests/test_d117_decode_contrast_plan.py:443-457` check only the unfrozen/default shape.

### Mechanical bar for the implementation round

I-1. Add the explicit target-identity properties and replace all semantic/path branches listed above.

I-2. Resolve the full output inventory before writes and assert its exact containment in the target allowlist.

I-3. Make spec naming ordinal-derived, including v2→v3.

I-4. Make lineage, plan-reference shape, reservation `--plan`, README identity, and every status field target-derived.

I-5. Retain preservation replay only for current pack-local producer/tree/sidecar/generator-pin authority.

I-6. Apply conditional successor fixture links.

I-7. Preserve the existing v1→v2 exact 334-file inventory and all v1 byte checks.

I-8. Do not update expected hashes until the new regressions fail against the pre-fix code and pass after it.

### Regression list

R-1. Existing real-checkout v1→v2 transaction: exactly 334 additions; no modified/deleted v1 file; both v1 specs byte-identical.

R-2. For each family, Git-track emitted v2 bytes, invoke its emitted generator with `--check --preserve-current-frozen-bytes` before any mutation, require exit 0; then invoke preserve generation and require an empty tracked diff. Both generations must be present.

R-3. For alpha/beta R2, record v1 and v2 spec hashes and assert both unchanged; assert no third spec path appears.

R-4. Assert every v2 science config retains `launch_lineage_required` after preserve generation, and all dependent manifests/specs/contracts remain byte-identical. Confirm v1 configs remain unmarked.

R-5. Emitted-pack induction probe for all three families: use each emitted v2 generator to produce v3; exact additions are only the v3 pack plus its v3 spec where applicable; all v1/v2 hashes remain unchanged.

R-6. Git-track v3, run its emitted preserve check and preserve generation, and demand an empty diff. This proves the repair is generational rather than special-cased to `_v2`.

R-7. Status transition test: draft current v2 is stable across mode override; a modeled valid fresh freeze attachment produces the governed frozen status at every enumerated status field; a second preserve regeneration is byte-stable.

R-8. Invalid identity/mode tuples refuse before creating or modifying any path.

R-9. Order probe: generate gamma v2 first, then run alpha and beta successor regressions in either order; no `FileExistsError`, and the existing gamma v2 remains untouched.

R-10. Run the three focused modules, then `python3 -m unittest discover -s tests`.

## Residual risk

Preserve-mode producer and plan-tree replay is a previously documented self-comparison hole. The class-closing tests must use independently tracked bytes and an empty Git diff; a green generator `--check` alone is not adequate evidence.