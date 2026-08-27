```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Literal/count-only Cure A does not satisfy E2 or E1; recommend strengthened v2 pin binding plus extraction replay, activated after the imminent _v4 mint under an explicit F2 ruling.",
  "workspace": {
    "base_requested": "origin/main@51ed8817",
    "base_mode": "exact",
    "head_start": "51ed8817126ce18a0b9460612f44124520df109d",
    "head_end": "51ed8817126ce18a0b9460612f44124520df109d",
    "upstream_end": "d9170fffa8ecaab4dbd6b9dad5ca3d33d7c1c50b",
    "branch": "impl/floor-bind-01"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "literal-and-count-only Cure A",
        "action": "do_not_start",
        "wait_for": "",
        "collision_surface": "Fails exact width-mismatch and complete-membership acceptance."
      },
      {
        "row": "strengthened v2 Cure A plus Cure B",
        "action": "needs_ruling",
        "wait_for": "_v4 mint transaction closure or an explicit ruling authorizing claim-interface coupling before it",
        "collision_surface": "validate_floor_artifact, analysis loader/API, analyze-claims CLI"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/floor-bind-01...origin/main [behind 2]",
          "51ed8817126ce18a0b9460612f44124520df109d",
          "d9170fffa8ecaab4dbd6b9dad5ca3d33d7c1c50b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "51ed8817126ce18a0b9460612f44124520df109d"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git ls-files scripts/floor_mint_pinsets",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/floor_mint_pinsets/mint1.json",
          "scripts/floor_mint_pinsets/schema_v2.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "mint1.json\\nscripts/floor_mint_pinsets/schema_v2.json"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import copy,json; from pathlib import Path; from joulewise.detection_floor import build_comparative_record,build_transport_group,comparative_false_effect_floor,validate_floor_artifact; a=json.loads(Path(\"df-ph-decode-floor-mint1.json\").read_text()); old=a[\"cells\"][0][\"floor_gate_j\"]; x=copy.deepcopy(a); y=x[\"cells\"][0]; rec=y[\"comparative\"]; ws=[v*0.99999999 for v in rec[\"admissible_half_widths_j\"]]; ds=[b[\"delta_j\"] for b in rec[\"blocks\"]]; y[\"comparative\"]=build_comparative_record(comparative_false_effect_floor(ds,admissible_half_widths_j=ws),rec[\"blocks\"],consumption_semantics_id=rec[\"consumption_semantics_id\"],whole_window_drift_allowance=rec[\"whole_window_drift_allowance\"]); y[\"floor_cmp_j\"]=y[\"comparative\"][\"drift_widened_guarded_floor_j\"]; y[\"floor_gate_j\"]=max(y[\"floor_abs_j\"],y[\"floor_cmp_j\"]); new=y[\"floor_gate_j\"]; x[\"transport_groups\"][0]=build_transport_group(transport_group_id=y[\"transport_group_id\"],backend=y[\"key\"][\"backend\"],metric=y[\"key\"][\"metric\"],window_class=y[\"key\"][\"window_class\"],stack_identity=y[\"source_regime\"][\"stack_identity\"],source_cells=[y],allowed_consumer_condition_families=x[\"transport_groups\"][0][\"allowed_consumer_condition_families\"]); print(\"old=%.15f new=%.15f old6=%.6f new6=%.6f findings=%r\"%(old,new,old,new,validate_floor_artifact(x)))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "old=7.377085735735073 new=7.377085672752914 old6=7.377086 new6=7.377086 findings=[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "old6=7.377086 new6=7.377086 findings=\\[\\]"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Both recommended layers alter paths used by the open _v4 transaction; Cure B also makes extraction-spec evidence operationally required for an exact claim.",
      "needs": "Authorize landing after _v4 mint closure, or explicitly accept pre-mint coupling."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD remained the requested 51ed8817, but the local origin/main ref advanced to d9170fff during the consult.",
      "needs": "Review or rebase the eventual implementation against the newer upstream."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A reviewed pinset is a valuable external anchor but, without replay, does not prove that its assertions equal the governed extraction report and source bytes.",
      "needs": "Keep L1 and FLOOR-BIND-01 open until extraction replay lands, unless the named acceptance is explicitly amended."
    }
  ]
}
```

## D1. Does Cure A close S and O?

No—not Cure A as argued in the prompt.

### Attack S: width understatement

For mint1, the only external floor value is the six-decimal literal `"7.377086"`; the v1 pinset contains no width array, corner value, full-precision component floor, or component-artifact digest (`scripts/floor_mint_pinsets/mint1.json:15`, `scripts/floor_mint_pinsets/mint1.json:24`, `scripts/floor_mint_pinsets/mint1.json:26`).

A self-consistent comparative-width reduction by `0.99999999` changed the exact operative floor from `7.377085735735073` to `7.377085672752914`, while both still format to `7.377086`; `validate_floor_artifact` returned no findings. That follows from the validator recomputing the corner from the artifact’s own width array (`joulewise/detection_floor.py:3106`, `joulewise/detection_floor.py:3121`, `joulewise/detection_floor.py:3131`) and then recomputing the cell floor from that internally consistent record (`joulewise/detection_floor.py:3852`).

Therefore this proposed comparison:

```text
format(artifact.floor_gate_j, ".6f")
    == pin.cell.operative_floor_six_decimal
```

does **not** refuse every S attack. It refuses only an understatement large enough to cross a six-decimal rounding boundary.

There is a second survivor: understating a width that is not the maximizing corner can leave even the full-precision component and operative floors unchanged. E2 says **any stored width mismatch** must refuse (`docs/process/state_kernel.json:1616`), so floor-literal comparisons alone can never satisfy E2.

For a v2 pack, strengthened A can close S with this exact comparison:

```text
reconstructed_component_artifact_sha256
    == pin.aggregate.component_artifacts[plan_id].sha256
```

The generalized mint already reconstructs each producer component and performs that comparison (`scripts/mint_floor_artifact_generalized.py:3255`, `scripts/mint_floor_artifact_generalized.py:3293`, `scripts/mint_floor_artifact_generalized.py:3296`). Because the component serialization includes the width arrays, any width mutation—including one invisible to the corner—changes the digest.

### Attack O: member omission

A cardinality-changing omission is caught by v1 literal binding:

- Absolute: derived observation count and width-array length must equal pinned `expected_n == 10`.
- Comparative: block count must equal pinned `expected_n == 10`, and flattened member count must equal `4 * expected_n == 40`.
- The artifact-derived extraction/evaluation counts must equal the independently pinned `30/37` and `40/47`.

Those literals are at `scripts/floor_mint_pinsets/mint1.json:29-34` and `scripts/floor_mint_pinsets/mint1.json:39-44`. Adjusting the artifact’s own `n` or count field does not help because it still differs from the repo pin.

But count-only A does **not** close E2’s broader “campaign-membership deviation.” An attacker can omit one governed member and replace it with another strict-valid campaign member, preserving all counts. The v1 pinset has no exact member identities. The current order binder only proves that each artifact-listed sequence occurs once and in order; it never proves that every governed campaign member appears in the artifact (`joulewise/analysis_engine/inputs.py:1522`, `joulewise/analysis_engine/inputs.py:1532`, `joulewise/analysis_engine/inputs.py:1551`).

A v2 final pinset does contain exact `(bundle_id, config_sha256)` member dispositions and exact component cardinality (`joulewise/detection_floor.py:2423`, `joulewise/detection_floor.py:2433`). Thus strengthened v2 A refuses O through either:

```text
artifact_component_members
    == pin_component.members
```

or the stronger component-artifact digest comparison above. A same-count replacement fails both.

A family with no matching pinset is not a surviving attack: it already hard-refuses during pinset resolution (`joulewise/detection_floor.py:2700`, `joulewise/detection_floor.py:2730`).

Verdict: literal/count A catches obvious O but not same-count membership deviation, and it does not catch all S. Strengthened v2 A using exact member pins and component digests closes both for v2 packs.

## D2. Current pinset inventory and `_v4`

The current repository inventory does not yet support strengthened A for `_v4`. It contains only:

- `mint1.json`, a v1 instance.
- `schema_v2.json`, a schema—not a final pinset instance.

The current projection confirms the loss of information: `_FloorMintPinsetProjection` carries only family identities and root IDs (`joulewise/detection_floor.py:2058`); both the v1 and v2 readers discard everything else on return (`joulewise/detection_floor.py:2249`, `joulewise/detection_floor.py:2601`).

The `_v4` pack needs its committed **final v2 pinset instances**, including the producer component artifact IDs/digests, exact member dispositions, full-precision cell floors, and extraction-report pins. This is already a named U10 obligation, not a new mint obligation created by FLOOR-BIND-01:

- The two-stage design freezes exact extraction members and counts at desk stage (`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:368`, `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:379`).
- Postcollection freezes report SHA and full-precision/six-decimal floors (`DESIGN-MEMO.md:389`, `DESIGN-MEMO.md:397`).
- U10 names the two component v2 pinsets, aggregate v2 pinset, and final artifact paths (`DESIGN-MEMO.md:465`).
- U10 is deliberately postcollection rather than part of desk freeze (`DESIGN-MEMO.md:467`).
- The mint already refuses anything other than a final v2 pinset (`scripts/mint_floor_artifact_generalized.py:3315`, `scripts/mint_floor_artifact_generalized.py:3317`).

Thus Cure A adds a **new consumer-side use** of already-required final pins; it does not add new evidence that the imminent mint was not already required to produce. Its absence today is expected before U10 closure.

The historical mint1 pack is not a reason to weaken the new gate: D-117 explicitly keeps mint1 and its derivatives non-claim-bearing (`docs/decision_log.md:7677`, `docs/decision_log.md:7682`). Do not modify `mint1.json`.

## D3. Fence check

| Cure | F1 | F2 | F3 |
|---|---|---|---|
| Literal/count A | **Pass**: no pack bytes or identities change. | **Needs ruling**: it tightens `validate_floor_artifact`, which the imminent mint calls (`scripts/mint_floor_artifact_generalized.py:3339`). No new operator input, but still transaction-path coupling. | **Pass** if purely additive; it nevertheless fails E1/E2 independently. |
| Strengthened v2 A | **Pass**: compares existing bytes to U10 pins; no remint. | **Needs ruling** for landing time because it changes the mint’s validator contract. | **Pass**: component digest and exact-member comparisons strengthen existing gates. |
| B | **Pass**: existing artifacts remain byte-identical; historical packs without replay evidence simply cannot license claims. | **Needs ruling**: a new operationally required claim input is precisely the coupling described by F2. The current CLI has no such input (`joulewise/cli.py:2283-2319`). | **Pass**: replay is additive and fail-closed. |
| Strengthened A+B | **Pass**. | **Needs ruling**; recommended activation is after `_v4` mint closure and before its first claim consumption. | **Pass**. |

No cure needs to touch a frozen pack or meta-process document.

## D4. E1 as written

Cure A is option **(ii): partial discharge with a named residual**.

It is a legitimate discharge of much of E1’s intent. A repo-committed, reviewed pin is external to the artifact and materially fixes the current self-attestation problem described in D-078. That decision expressly classifies L1 as a third-party-verifiability deficit (`docs/decision_log.md:4544-4555`).

But E1 does not merely require “an external reviewed assertion.” It requires binding to the extraction report and source-member disposition, or replaying extraction gates and widths (`docs/process/state_kernel.json:1615`). Its controlling summary is even more explicit: claim consumption must authenticate widths and complete membership **against extraction evidence** (`docs/process/state_kernel.json:1624`). Cure A never reads the report bytes or replays the source.

Residual to register:

> Claim consumption proves that the artifact matches reviewer-frozen assertions, but still cannot independently prove that those assertions match the governed extraction report and source bytes.

Accordingly, A alone should not retire L1 or close FLOOR-BIND-01 without a named-decision amendment to E1.

## D5. Recommendation

Recommend **strengthened A+B**, sequenced after the imminent `_v4` mint unless the lead explicitly authorizes pre-mint coupling.

“Strengthened A” means exact v2 component-artifact digest and member-disposition binding—not merely six-decimal floors and counts.

Soundness decides this:

1. Literal/count A demonstrably misses an exact width change and same-count membership deviation.
2. Strengthened v2 A closes artifact substitution, but remains a reviewed-assertion anchor rather than extraction authentication.
3. B directly satisfies E1 by rerunning the governed extraction path and comparing replayed members, widths, corners, and floors.
4. B itself needs an independent authentication anchor for the supplied extraction-spec bytes. The v2 final pinset provides that SHA and intended membership (`joulewise/detection_floor.py:2344`, `joulewise/detection_floor.py:2403`, `joulewise/detection_floor.py:2423`). Comparing the spec only to an artifact-internal SHA would recreate self-attestation.
5. A provides automatic defense on every `validate_floor_artifact` path; B provides the source-grounded proof required before `bound_cell_ids` is populated.

### Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Literal/count-only A | do not start | — | Scientifically insufficient |
| Strengthened A implementation | prepare/design now; activation needs ruling | U10 final v2 instances, or fixture-equivalent pins | `joulewise/detection_floor.py`; imminent mint validation |
| B activation | wait | `_v4` mint transaction closure unless expressly authorized sooner | analysis API and `analyze-claims` CLI |
| First `_v4` claim consumption | wait | strengthened A+B passing E2/E3 regressions | claim-critical path |

## D6. Implementable specification

### Exact production files

- `joulewise/detection_floor.py`
- `joulewise/analysis_engine/inputs.py`
- `joulewise/analysis_engine/__init__.py`
- `joulewise/cli.py`

Tests:

- `tests/test_detection_floor.py`
- `tests/test_analysis_integration.py`
- `tests/test_mint_floor_artifact_generalized.py` for validator/mint parity only

No changes to `df-ph-decode-floor-mint1.json`, `scripts/floor_mint_pinsets/mint1.json`, existing pack SHA files, or docs.

### Projection shape

Replace the lossy projection at `joulewise/detection_floor.py:2058` with frozen nested projections equivalent to:

```python
@dataclass(frozen=True)
class _FloorMintMemberPin:
    bundle_id: str
    config_sha256: str

@dataclass(frozen=True)
class _FloorMintComponentPin:
    evidence_root_id: str
    calibration_cell_id: str
    evaluation_basis_sha256: str
    evaluation_basis_members: int
    extraction_spec_sha256: str | None
    extraction_spec_members: int
    expected_n: int
    drift_allowance_j: float
    order_manifest_id: str
    order_manifest_sha256: str | None
    consumption_semantics_id: str | None
    members: tuple[_FloorMintMemberPin, ...] | None

@dataclass(frozen=True)
class _FloorMintCellPin:
    cell_id: str
    transport_group_id: str
    condition_family_id: str
    condition_family_sha256: str
    metric: str
    window_class: str
    operative_floor_six_decimal: str
    absolute_floor_full_precision: Decimal | None
    comparative_floor_full_precision: Decimal | None
    operative_floor_full_precision: Decimal | None
    extraction_report_sha256: str | None
    absolute: _FloorMintComponentPin
    comparative: _FloorMintComponentPin

@dataclass(frozen=True)
class _FloorMintComponentArtifactPin:
    plan_id: str
    artifact_id: str
    sha256: str

@dataclass(frozen=True)
class _FloorMintPinsetProjection:
    schema_version: str
    family_identities: frozenset[tuple[str, str, str]]
    evidence_root_ids: frozenset[str]
    aggregate_artifact_id: str | None
    producer_set_sha256: str | None
    component_artifacts: tuple[_FloorMintComponentArtifactPin, ...]
    cells: tuple[_FloorMintCellPin, ...]
```

V1 absent fields remain `None`; that preserves byte-stable compatibility without pretending v1 has v2 assurances.

For v2, reconstruct producer component artifacts and perform the same containment-aware digest comparison already used by the mint (`scripts/mint_floor_artifact_generalized.py:3263-3300`). Compare full-precision pins with `Decimal(str(actual))`, as the mint already does (`scripts/mint_floor_artifact_generalized.py:3185-3213`). Do not use `math.isclose` for E2 comparisons.

### Replay binding

Add an optional-but-claim-gating argument throughout:

```python
floor_extraction_specs: Mapping[str, Path] | None = None
```

Key it by `evidence_root_id`, exposed as repeatable CLI input:

```text
--floor-extraction-spec ROOT_ID=PATH
```

Thread it through `_cmd_analyze_claims` (`joulewise/cli.py:2003`), `analyze_claims` (`joulewise/analysis_engine/__init__.py:1625`), and `load_analysis_inputs` (`joulewise/analysis_engine/inputs.py:3001`).

Inside binding, strictly parse each spec, authenticate its bytes against the v2 projection’s extraction-spec SHA, and lazily import/call `floor_extraction.extract_cells`. The lazy import avoids the existing module cycle because `floor_extraction` imports analysis-input primitives; `extract_cells` is already the public governed replay API (`joulewise/floor_extraction.py:122`, `joulewise/floor_extraction.py:2793`).

Replay with the same:

- evidence root;
- strict validator;
- evaluation-basis SHA;
- consumption-semantics ID;
- calibration-ledger snapshot;
- manifest identity.

Compare, without tolerance:

- exact admitted and excluded member identities and order;
- bundle/config digests;
- exact width arrays;
- corner outputs;
- absolute/comparative/operative floors;
- refusal/disposition results.

Only add a cell to `bound_cell_ids` after both existing bundle binding and replay equality pass. The current binding reads and validates artifact-listed bundles (`joulewise/analysis_engine/inputs.py:1816-1928`), so replay must augment, not replace, that gate.

### Exact new refusal strings

Validator findings:

```text
artifact.pinset: aggregate artifact_id mismatch
artifact.pinset: component artifact hash mismatch for {plan_id!r}
artifact.pinset: cell {cell_id!r} {component_name} member disposition mismatch
artifact.pinset: cell {cell_id!r} {component_name} extraction-spec sha256 mismatch
artifact.pinset: cell {cell_id!r} {component_name} full-precision floor mismatch
artifact.pinset: cell {cell_id!r} operative six-decimal floor mismatch
```

Stable claim-binding reasons:

```text
floor_extraction_spec_mapping_required
missing_floor_extraction_spec_mapping: {evidence_root_id!r}
unknown_floor_extraction_spec_mapping: {evidence_root_id!r}
floor_extraction_spec_sha256_mismatch: {evidence_root_id!r}
floor_extraction_replay_refused: {evidence_root_id!r}: {reason}
floor_extraction_membership_mismatch: {cell_id!r}.{component_name}
floor_extraction_width_mismatch: {cell_id!r}.{component_name}
floor_extraction_corner_mismatch: {cell_id!r}.{component_name}
floor_extraction_floor_mismatch: {cell_id!r}.{component_name}
```

Add the stable prefixes to `_FLOOR_BINDING_REASON_CODES` beside the existing mapping/order codes (`joulewise/analysis_engine/inputs.py:382-408`).

### Defect-shaped regressions

In `tests/test_detection_floor.py`:

```text
test_v2_pinset_component_digest_refuses_self_consistent_width_substitution
test_v2_pinset_component_digest_refuses_nonoperative_width_substitution
test_v2_pinset_members_refuse_same_count_member_replacement
test_v1_six_decimal_pin_does_not_claim_exact_width_binding
```

The first test must use a perturbation that retains the same `.6f` value, matching V3.

In `tests/test_analysis_integration.py`:

```text
test_floor_replay_refuses_self_consistent_width_substitution_end_to_end
test_floor_replay_refuses_governed_member_omission_end_to_end
test_floor_replay_refuses_same_count_member_replacement_end_to_end
test_claim_run_without_extraction_spec_mapping_cannot_bind_floor_cells
test_claim_run_refuses_extraction_spec_not_matching_final_pinset
```

These are the E2/E3 closure tests. Each must reach `analyze_claims`, assert the relevant stable reason code, and assert that the attacked cell is absent from `bound_cell_ids` and cannot resolve an exact floor.

### Existing tests affected

A hard replay requirement will break successful claim fixtures that currently supply a floor and evidence roots but no extraction-spec mapping, including:

- `test_finalized_gamma_runs_real_engine_then_isolates_math_layers` (`tests/test_analysis_integration.py:541`);
- `test_authenticated_v2_whole_window_source_reaches_claim_consumption` (`tests/test_analysis_integration.py:1944`);
- both successful distinct-root CLI tests (`tests/test_analysis_integration.py:3580`, `tests/test_analysis_integration.py:3585`).

They must receive governed synthetic extraction specs and corresponding final-pinset pins.

Do **not** extend `mint1.json` in place: that would intentionally break `test_mint1_pinset_preserves_byte_stable_empty_finding_set`, which pins its exact SHA (`tests/test_detection_floor.py:2323-2332`), and the generalized-mint hard-pin regression (`tests/test_mint_floor_artifact_generalized.py:5447`).

## D7. What is wrong in the prompt

1. “Understating a width lowers the operative floor, therefore the six-decimal pin catches it” is false. A small but real decrease preserved `7.377086`, and a non-maximizing width can change without changing the floor at all.

2. “Counts catch member omission” is only true for cardinality-changing omission. It does not catch omission-plus-replacement, which is still a campaign-membership deviation under E2.

3. Cure A can close S/O for v2 only if “corresponding fields” explicitly includes the exact component-artifact digest and exact member dispositions. Full-precision floor pins alone still do not prove every width entry.

4. A pinset is not literally one of E1’s two accepted proof shapes. It is a worthwhile third anchor, but closing the row on A alone would require an explicit amendment to the named acceptance.

5. The assertion that the worktree is “at origin/main 51ed8817” became stale during inspection: HEAD stayed at `51ed8817`, while the local `origin/main` ref is now `d9170fff`. All findings above are against the requested exact HEAD; the implementation must be rechecked against the newer upstream.

Checks performed: targeted source inspection of validation, pin projection, claim loading/binding, generalized mint, named decisions and acceptance; repository pinset inventory; clean-worktree/head inspection; and an in-memory self-consistent same-six-decimal width-substitution reproduction. No files were written and no network or live/quiet-Mac work was performed.