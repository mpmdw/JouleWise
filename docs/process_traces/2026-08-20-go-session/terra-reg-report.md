```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend enumeration A and a complete R1 install only at the _v4 boundary; installing into frozen _v3 is executably blocked.",
  "workspace": {
    "base_requested": "afb7d57",
    "base_mode": "exact",
    "head_start": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "head_end": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "Adopt enumeration A; treat successor_pack_ids as a reopened sixth value and install the complete registry for a newly minted _v4 family only.",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "A registry-byte change on the _v3 path is not installable",
        "detail": "The executed experiment proves the frozen plan-tree pin refuses before receipt verification; re-minting and a new path both fail."
      },
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "The packet describes comparison options that current code does not implement",
        "detail": "The allowlist is membership-only during authoring; no arm or consume comparator evaluates an EXACT_MATCH-like token."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The packet understates fingerprint coverage",
        "detail": "The six-kind set marks Amendment-5-required kinds, but generic EXECUTION_BOUND authoring records a fingerprint for additional kinds too."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The _v4 proposal lacks an archival replay rule for _v3",
        "detail": "After the global registry changes, _v3 cannot verify at the new HEAD; the prior registry commit/check-out must be preserved as its replay coordinate."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1 && git diff --check && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["afb7d5705add3475cd016177a8f8fa1dd02a814e"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^afb7d5705add3475cd016177a8f8fa1dd02a814e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n \"environment_comparison|_SUPPORTED_ENVIRONMENT_COMPARISONS|_execution_environment_fingerprint|validate_r1_class_lifecycle\" joulewise/arm_readiness.py joulewise/arm_readiness_evidence.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["joulewise/arm_readiness_evidence.py:1788:            and policy[\"environment_comparison\"]", "joulewise/arm_readiness.py:3344:def validate_r1_class_lifecycle("]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "environment_comparison|validate_r1_class_lifecycle"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 48 tests in 0.101s", "FAILED (errors=37)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK( \\(skipped=.*\\))?$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The magistrate must adopt the _v4-boundary migration and reject any _v3-path install.",
      "needs": "Record the boundary, archival-replay rule, and required _v4 transaction."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Focused tests could not create tempfile scratch space in this read-only sandbox; all 37 errors are FileNotFoundError from tempfile initialization.",
      "needs": "Run the focused suite and the real _v4 author→freeze→arm→consume rehearsal in a writable isolated clone."
    }
  ]
}
```

## Findings

### B1 — blocker — install timing

Defer the registry install to the `_v4` family boundary. Do not install it on the frozen `_v3` path.

The byte-pin experiment confirms that changing the current registry makes `_v3` refuse first at its immutable `plan_tree.json` attachment; re-minting cannot reach a repair path, and a new registry path also refuses on the pinned `path` field. Only deferral or a newly minted family remains viable. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/09-EXPERIMENT-byte-pin-CONFIRMED-BLOCKER.md:10-22` `:185-249` `:253-270`

The install must land before `_v4` plan attachments and evidence are authored, then remain byte-stable for `_v4`’s claimed life. The frozen `_v3` campaign must first close under the unchanged v1 registry. Preserve the pre-install commit/check-out as the sole `_v3` replay coordinate; the current code has one registry path and no registry-supersession acceptance. `joulewise/arm_readiness.py:2764-2804` `docs/process_traces/2026-08-19-prep-sprint/registry-packet/09-EXPERIMENT-byte-pin-CONFIRMED-BLOCKER.md:208-249`

### §1a — counting ruling

Adopt enumeration A. It is the executed mechanical NEEDS_RULING: environment comparison semantics, 14 execution horizons, refusal vocabulary, arm-to-consume budget, and marker schema. `successor_pack_ids` was approved as `_v2`, then reopened by D-147’s `_v3` supersession; it is therefore a sixth value, not one of the original five. Enumeration B is an unreconciled later characterization. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/00-INDEX.md:63-121`

### §1b — ruled install bytes

V1 — contest the packet’s `_v3` proposal because immediate installation is blocked. At the actual `_v4` boundary install:

```json
"successor_pack_ids": {
  "ALPHA": "d117_floor_qwen25_1p5b_v4",
  "BETA": "d117_floor_qwen25_7b_v4",
  "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v4"
}
```

The name patterns expressly permit `_v4`; `_v3` is the correct value only for a pre-freeze `_v3` installation, a sequencing option the experiment closed. `joulewise/arm_readiness.py:260-266` `docs/process_traces/2026-08-19-prep-sprint/registry-packet/01-successor-pack-ids.md:102-165` `09-EXPERIMENT-byte-pin-CONFIRMED-BLOCKER.md:253-262`

V2 — use honest record-only semantics for every EXECUTION_BOUND kind:

```diff
-_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset()
+_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset({"RECORD_ONLY"})
```

```json
"environment_comparison": "RECORD_ONLY"
```

Apply that field value to all sixteen EXECUTION_BOUND policies. This is the only truthful currently installable semantics: the implementation gates only token membership while authoring; it never compares a current environment with the recorded fingerprint at ARM or consumption. `joulewise/arm_readiness_evidence.py:117-119` `:1786-1796` `joulewise/arm_readiness.py:3344-3403` The packet itself identifies that the code allowlist must move with JSON. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/02-environment-comparison-semantics.md:77-109`

V3 — install two execution-horizon tiers. This joint V2/V3 fragment is the exact set of EXECUTION_BOUND policy objects; the ten six-hour entries include the two already-approved horizons, while the other fourteen are the newly ruled values.

```json
[
  {"kind":"ACCEPTANCE_OWNER","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"ACCEPTANCE_SUCCESSOR","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"DRY_RUN_REHEARSAL","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.machine_probe.20m.record_only.v1","horizon_ns":1200000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"ESTIMATOR_IDENTITY","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"GIT_CHECKOUT","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"IDENTITY_PIN_PROJECTION","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"MINT_TRUST","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.machine_probe.20m.record_only.v1","horizon_ns":1200000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"MULTICELL_MINT","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.machine_probe.20m.record_only.v1","horizon_ns":1200000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"OFFLINE_INPUT_INVENTORY","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"PACK_AUTHENTICATION","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"PRIVILEGE_INSTALLATION","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.machine_probe.20m.record_only.v1","horizon_ns":1200000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"REASON_CODE_COVERAGE","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"RECEIPT_ORACLE","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"RECOVERY_LEDGER_TEST","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.machine_probe.20m.record_only.v1","horizon_ns":1200000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"TERMINAL_REVIEW","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.reviewed_bytes.6h.record_only.v1","horizon_ns":21600000000000,"environment_comparison":"RECORD_ONLY"},
  {"kind":"THREE_WINDOW_REGRESSION","freshness_class":"EXECUTION_BOUND","freshness_policy_id":"r1.execution.machine_probe.20m.record_only.v1","horizon_ns":1200000000000,"environment_comparison":"RECORD_ONLY"}
]
```

This adopts the packet’s evidence-subject tiering, rather than its uniform fixture horizon: byte/review evidence gets the existing six-hour procedural tier; machine/probe evidence gets the approved twenty-minute volatile tier. The validator permits shared IDs only when all three definition fields match, which these two groups satisfy. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/03-execution-bound-horizons.md:64-97` `:129-152` `joulewise/arm_readiness.py:1637-1651`

V4:

```json
"refusal_vocabulary": [
  {"role":"CLASS_MISMATCH","code":"r1_class_mismatch","type":"POLICY"},
  {"role":"DEPENDENCY_CHANGED_SET","code":"r1_dependency_changed_set","type":"LIFECYCLE"},
  {"role":"DEPENDENCY_MANIFEST","code":"r1_dependency_manifest","type":"LIFECYCLE"},
  {"role":"FAMILY_PUBLICATION","code":"r1_family_publication","type":"CUSTODY"},
  {"role":"SUCCESSOR_CHAIN","code":"r1_successor_chain","type":"IDENTITY"},
  {"role":"TEMPORAL_BUDGET","code":"r1_temporal_budget","type":"LIFECYCLE"},
  {"role":"UNKNOWN_POLICY","code":"r1_unknown_policy","type":"POLICY"},
  {"role":"V1_GRANDFATHERING","code":"r1_v1_grandfathering","type":"LIFECYCLE"}
]
```

The `r1_` prefix distinguishes registry-owned lifecycle refusals from pre-existing structural codes, while the types communicate the actual failure domain. These are emitted receipt fields, not labels. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/04-refusal-vocabulary.md:82-95` `:123-151` `joulewise/arm_readiness.py:962-988`

V5 — rule the omitted sibling in the same bytes:

```json
"arm_policy": {
  "capability_horizon_ns": 300000000000,
  "arm_to_consume_budget_ns": 300000000000
}
```

Five minutes means arming requires at least five minutes of remaining TIME_BOUND evidence, and consumption must complete within the same capability horizon. It nests safely inside the 20-minute volatile evidence horizon. It is installable only after an isolated `_v4` rehearsal demonstrates a p99 arm→consume gap of at most four minutes, retaining a one-minute margin; the record currently has no such measurement. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/05-arm-to-consume-budget.md:83-144` `:146-200` `joulewise/arm_readiness.py:3299-3341` `:6235-6242`

V6:

```json
"family_publication_marker_schema": "joulewise.d117_family_publication_marker.v1"
```

Install this only with a real v4 marker schema, canonical marker file, and consumer that refuses `r1_family_publication` until the marker binds all three `_v4` plan-tree digests, all three `freeze-0004` receipt references, and the exact installed registry reference. A string alone is inert today; this is not permission for a forward declaration. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/06-family-publication-marker-schema.md:115-143` `:147-171`

### Required `_v4` transaction additions

The packet correctly identifies these as required but has no bytes for them. They cannot stay implicit because any unresolved value blocks the whole registry. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/07-council-brief.md:62-85`

```json
{
  "schema_version": "joulewise.arm_readiness_row_registry.v2",
  "registry_id": "d117-row-registry-r1",
  "freeze_evidence_lifecycle": {
    "schema_version": "joulewise.arm_readiness_freeze_evidence_lifecycle_registry.v1",
    "registry_id": "d117-r1-lifecycle-registry-v1",
    "irrelevant_path_allowlist": [],
    "successor_policy": {
      "cross_chain_numbering": "joulewise.freeze_chain_monotonic.v1",
      "freeze_receipt_v2_predecessor_bindings": [
        "evidence_set_sha256",
        "freeze_receipt",
        "identity_receipt",
        "pack_digest_algorithm",
        "pack_id",
        "pack_path",
        "pack_sha256",
        "plan_id",
        "plan_sha256"
      ]
    }
  }
}
```

Also include all thirteen non-EXECUTION_BOUND policies, then a sorted `row_policies` entry for every one of the 35 rows, using the policy ID of that row’s required kind. The validator requires every policy kind and row binding to agree; it does not infer these. `joulewise/arm_readiness.py:1896-1925` The `PACK_FAMILY` successor route should be built, not carried again: branch from the historical `_PACKS_BY_PROFILE` only for v1 and use installed successor IDs for v4. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/07-council-brief.md:183-215`

Re-author all `_v4` generic evidence under the installed R1 policies before freezing; v1 generic evidence is expressly refused from the R1 lifecycle. `joulewise/arm_readiness.py:3180-3204`

### F1 — should fix — comparator semantics

The packet’s `EXACT_MATCH` / interpreter-based alternatives and its requested perturbation test imply a runtime comparator, but current code only permits or refuses the selected token at authoring. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/02-environment-comparison-semantics.md:184-210` `joulewise/arm_readiness_evidence.py:1786-1796` This must be corrected before any future council selects a non-record-only token.

### F2 — should fix — fingerprint coverage

The packet says only six kinds record a fingerprint and describes the other ten as lacking one. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/02-environment-comparison-semantics.md:120-144` `:200-205` In fact, generic EXECUTION_BOUND authoring calls `_execution_environment_fingerprint` for every such policy; the six-kind set only controls an annotation and PACK_AUTHENTICATION’s inherited-environment list. `joulewise/arm_readiness_evidence.py:107-119` `:429-472` `:2425-2454`

### F3 — should fix — archival replay

The packet needs an explicit old-family replay rule. The `_v4` migration intentionally makes live-head verification of `_v3` fail; that is acceptable only if the custody record names the pre-install commit/check-out and requires `_v3` replay there, never at `_v4` HEAD. `docs/process_traces/2026-08-19-prep-sprint/registry-packet/09-EXPERIMENT-byte-pin-CONFIRMED-BLOCKER.md:208-230` `:264-270`

## Residual risk

The candidate byte set was structurally validated in memory against the current validator (29 policies and 35 row bindings), but the focused test modules could not run here because this sandbox cannot create `$TMPDIR` scratch directories. A writable isolated clone must run the focused suite and the complete `_v4` author → freeze → dry-run → arm → consume path before merge.