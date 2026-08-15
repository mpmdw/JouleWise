```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt a distinct finalized-v3 schema consumed directly by analyze-claims; production freeze remains blocked on unresolved prefill, floor, and multiplicity rulings plus a same-head L10 lifecycle rehearsal.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "Teach analyze-claims the authenticated joulewise.analysis_manifest.v3.finalized schema; do not emit or relabel a persisted historical-v3 conversion.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The production contract needs immutable prospective and finalized artifacts with an outcome-blind authenticated finalizer"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "There are not yet frozen multiplicity or prefill-consumption semantics to preserve"
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Gamma must remain unarmable until a same-head L10 sacrificial lifecycle receipt closes a dedicated P1 queue row"
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "A historical-v3 conversion would inherit incompatible identity, multiplicity, and cross-arm LOO assumptions"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"from pathlib import Path; from joulewise.analysis_engine.inputs import load_manifest; load_manifest(Path('configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json'))\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "AnalysisInputError: unsupported analysis manifest schema_version: 'joulewise.analysis_manifest.v3.prospective'"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "unsupported analysis manifest schema_version.*v3\\.prospective"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n 'build_prospective_analysis_manifest_v3|validate_prospective_analysis_manifest_v3|finalize_prospective_analysis_manifest_v3|validate_finalized_analysis_manifest_v3' joulewise scripts tests; rc=$?; echo FUNCTION_SEARCH_EXIT=$rc; test $rc -eq 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FUNCTION_SEARCH_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FUNCTION_SEARCH_EXIT=1"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import json,pathlib; x=json.loads(pathlib.Path(\"configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json\").read_text()); print(\"schema=\"+x[\"schema_version\"]); print(\"contrasts=\"+str([(c[\"measurement_arm\"],len(c[\"members\"])) for c in x[\"contrasts\"]])); print(\"prefill=\"+\",\".join(x[\"contrasts\"][1][k][\"status\"] for k in (\"test\",\"multiplicity\",\"floor_dependency\"))); print(\"decode_m=\"+str(x[\"contrasts\"][0][\"multiplicity\"][\"m\"])); print(\"decode_contingent=\"+str(\"contingent\" in x[\"contrasts\"][0][\"multiplicity\"][\"note\"]))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "schema=joulewise.analysis_manifest.v3.prospective",
          "contrasts=[('decode', 40), ('prefill_p256', 40)]",
          "prefill=EMPTY,EMPTY,EMPTY",
          "decode_m=1",
          "decode_contingent=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "prefill=EMPTY,EMPTY,EMPTY.*decode_m=1.*decode_contingent=True"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -n 'v3 requires frozen Holm alpha=0.05 m=1|block_ids = list\\(prepared_by_id\\[contrast_ids\\[0\\]\\]' joulewise/analysis_engine/artifact.py joulewise/analysis_engine/__init__.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/analysis_engine/__init__.py:1391:    block_ids = list(prepared_by_id[contrast_ids[0]][\"manifest\"][\"block_ids\"])",
          "joulewise/analysis_engine/artifact.py:686:                f\"{where}.family_instance_id: v3 requires frozen Holm alpha=0.05 m=1\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "block_ids.*contrasts\\[0\\].*v3 requires frozen Holm alpha=0.05 m=1"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HEAD \\(no branch\\).*8937dec9"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The production draft still leaves the prefill test, multiplicity family, and floor dependency EMPTY, while decode m=1 is explicitly contingent.",
      "needs": "Before production freeze, rule the two contrasts' family membership/m, prefill test and direction, prompt status, and p256 floor or governed transport."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The requested 2026-08-15 council-verdict.md was not present anywhere under the session root; both cited ECF refuter reports were read from the parent scratchpad.",
      "needs": "The lead should compare this contract against the authoritative council verdict during adjudication."
    },
    {
      "id": "R3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only design consult; no implementation tests or synthetic finalization rehearsal could run because the required functions do not exist.",
      "needs": "Execute the L10 rehearsal defined below on the implementation head before gamma can arm."
    }
  ]
}
```

## Findings

### F1 — blocker: governed two-artifact contract

Adopt a direct finalized-schema wire:

```text
immutable frozen prospective manifest
        + authenticated postcollection evidence
        ↓ outcome-blind finalizer
immutable finalized manifest
        ↓ finalized-schema validator
analyze-claims
```

Do not mutate the pack’s prospective manifest after collection, and do not let `analyze-claims` accept it directly.

Prospective schema: `joulewise.analysis_manifest.v3.prospective`

Exact top-level domains:

- `schema_version`, `manifest_id`, `freeze_status`
- plan, root/stage manifests, evidence-root and four condition-family bindings
- fixed design and replacement policy
- explicit `families`
- exactly two contrasts: decode and `prefill_p256`
- exact 80 members, twenty ABBA blocks, configuration hashes and order
- a declarative `finalization_contract`
- `frozen_semantics_sha256`

`finalization_contract` declares required evidence roles, schema versions, deterministic namespace and projection rule. It contains no future hashes or `EMPTY` values. The present mutable-looking `postcollection_attachments` placeholders should remain draft-only and be rejected by the frozen validator, following D-134’s slot-declaration precedent.

The frozen semantic projection must cover every field capable of changing the estimand or multiplicity result: condition identities, metrics/prechecks, B−A orientation, estimator, test/direction, block/member membership and order, family membership, `alpha/q/m`, equivalence/MDE, floor selectors and transport, replacement policy, and required attachment roles.

Finalized schema: `joulewise.analysis_manifest.v3.finalized`

It should contain:

- A new content-derived finalized `manifest_id`.
- `lineage.prospective_manifest_id`, path and exact file SHA.
- `lineage.collection_manifest_id` for campaign-log and whole-window lookup.
- Projection-rule ID and independently recomputed prospective/final semantic hashes.
- Consumer-shaped `design`, `arms`, `entries`, `blocks`, `families`, and `contrasts`.
- Authenticated evidence references for:
  - the passed whole-window verdict and its derived evaluation-basis SHA;
  - bracket binding;
  - the actual committed calibration-ledger terminal head;
  - the exact aggregate floor artifact.
- Both D-122 contrasts regardless of whether either clears its decision envelope.

The finalizer must be outcome-blind: it authenticates completeness, custody and frozen selectors but never reads an effect estimate or p-value to decide whether finalization is allowed. A scientifically unfavorable but technically valid window must finalize and produce an unresolved/refused claim result rather than disappear.

Required APIs:

```python
build_prospective_analysis_manifest_v3(campaign_dir, *, plan_tree_path) -> dict
validate_prospective_analysis_manifest_v3(
    value, *, manifest_dir, plan_tree_path
) -> tuple[ManifestRefusal, ...]

analysis_semantics_projection_v1(value) -> dict
analysis_semantics_sha256_v1(value) -> str

finalize_prospective_analysis_manifest_v3(
    prospective_manifest_path,
    *,
    plan_tree_path,
    custody_root,
    runs_root,
    whole_window_verdict_path,
    bracket_binding_path,
    calibration_ledger_path,
    aggregate_floor_artifact_path,
    output_dir,
) -> dict

validate_finalized_analysis_manifest_v3(
    value, *, manifest_path, custody_root
) -> tuple[ManifestRefusal, ...]
```

The finalizer accepts paths, not operator-entered hashes, basis IDs, ledger heads, family sizes or selectors. It derives those values from authenticated bytes. Output is append-only and crash-atomic; identical re-execution is an idempotent success, while an occupied namespace with different bytes refuses.

The historical `build_analysis_manifest_v3` and validator at [analysis_manifest_v3.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bcon/joulewise/analysis_manifest_v3.py:437) remain byte-compatible.

Closed refusal vocabulary:

| Layer | Reason codes |
|---|---|
| Prospective | `analysis_prospective_schema_invalid`, `analysis_prospective_unknown_key`, `analysis_prospective_not_frozen`, `analysis_prospective_identity_mismatch`, `analysis_prospective_plan_tree_mismatch`, `analysis_prospective_source_hash_mismatch`, `analysis_prospective_unsafe_path`, `analysis_prospective_member_cover_mismatch`, `analysis_prospective_block_cover_mismatch`, `analysis_prospective_contrast_cover_mismatch`, `analysis_prospective_family_invalid`, `analysis_prospective_multiplicity_invalid`, `analysis_prospective_floor_dependency_unresolved`, `analysis_prospective_unresolved_slot` |
| Finalization | `analysis_finalization_input_unreadable`, `analysis_finalization_prospective_invalid`, `analysis_finalization_attachment_missing`, `analysis_finalization_attachment_invalid`, `analysis_finalization_verdict_not_passed`, `analysis_finalization_evaluation_basis_mismatch`, `analysis_finalization_member_cover_mismatch`, `analysis_finalization_bracket_binding_mismatch`, `analysis_finalization_ledger_head_mismatch`, `analysis_finalization_floor_dependency_unsatisfied`, `analysis_finalization_semantics_mismatch`, `analysis_finalization_noncanonical`, `analysis_finalization_output_conflict` |
| Consumer | `analysis_manifest_prospective_not_consumable`, `analysis_manifest_finalized_invalid`, `analysis_manifest_lineage_mismatch`, `analysis_manifest_collection_identity_mismatch`, `analysis_manifest_floor_attachment_mismatch`, `analysis_manifest_family_semantics_mismatch` |

Upstream validators may provide nested detail codes, but the top-level code stays in this closed enum. Any such error exits before estimation and creates no claim artifact.

### F2 — blocker: the current “freeze” is scientifically incomplete

The current [gamma manifest](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bcon/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:1) contains both 40-member contrasts, but the prefill test, multiplicity and floor dependency are `EMPTY`; decode’s Holm `m=1` is explicitly contingent. Therefore there is no settled multiplicity contract for the finalizer to preserve yet.

My recommendation is one primary Holm family, `alpha=0.05`, `m=2`, containing decode and prefill, with two-sided tests and positive scientific directions. A missing or non-estimable member remains in the frozen `m=2`; the engine must never shrink the family after seeing data. Two separately justified `m=1` families are implementable, but require an explicit contrary ruling.

For the p256 floor, do not infer transport from the existing p128 floor. Either freeze an owned, validated p128→p256 transport rule or require a p256 floor artifact.

Whichever ruling wins, encode it in `families` before freeze and copy it byte-for-byte into the finalized manifest. The finalizer must not choose or reconstruct family membership.

### F3 — blocker: L10 rehearsal, readiness fence and queue row

L10 should run this `[AGENT]` sacrificial lifecycle entirely under `$TMPDIR` before gamma collection:

1. Build the prospective manifest twice from the same pack; require byte equality, valid plan-tree pinning and identical semantic hashes.
2. Use production writers/validators to create a synthetic exact-80-member corpus, passed whole-window verdict, exact evaluation basis, bracket binding, finalized ledger and aggregate floor artifact covering both frozen selectors.
3. Finalize twice; require byte-identical idempotence and a valid finalized manifest.
4. Run the real `analyze-claims` CLI on the finalized manifest. Require exactly the two frozen contrast IDs and the exact frozen family/multiplicity structure.
5. Run two scientific scenarios: one above the decision bar and one below it. Both must finalize; only the claim outcome may differ.
6. Independently compute the expected semantic projection rather than calling the production projector as the test oracle.
7. Mutate orientation, metric, estimator, test, family membership, `m`, block/member identity, configuration SHA and floor dependency—one at a time and coupled on both sides while recomputing local IDs. Every case must still refuse because the frozen pack/tree digest or independent semantic projection disagrees.
8. Exercise missing/failed verdict, missing/extra member, wrong evaluation basis, wrong bracket, stale ledger head, wrong floor bytes, absent prefill floor, unknown/duplicate keys, non-finite JSON, path escape/symlink, partial output, conflicting existing output, and direct prospective-manifest consumption.
9. Re-run the historical v3 builder/validator and existing analysis fixture to prove no byte or behavior drift.
10. Emit an immutable rehearsal receipt pinning HEAD, pack/tree/prospective hashes, finalizer and consumer code hashes, finalized-manifest and claim-artifact hashes, both contrast IDs, family semantic hash, and the complete refusal matrix.

Add a gamma-only D-134 readiness row such as `analysis.consumption_edge_rehearsed`. It consumes that receipt at freeze time and re-verifies it read-only at T-0; it must not run analysis during the quiet window. Add `readiness_analysis_consumption_edge_unrehearsed` to the closed readiness vocabulary.

Dedicated queue entry:

```text
ID: WO-CONSUMPTION-EDGE
Priority: P1 Phase Gate
Lane: [AGENT]
Status: READY for implementation; cannot close before the production-pack L10 replay
Task: Implement the prospective validator, immutable finalized-manifest
      finalizer, direct analyze-claims consumer wire, and semantic-equality proof.
Acceptance: Both D-122 contrasts consume end-to-end; exact frozen family semantics
            survive; historical v3 is unchanged; all negative cases refuse; the
            same-HEAD/pack L10 receipt passes.
Fence: Gamma may not freeze/arm or spend a quiet window until this row is CLOSED
       and its receipt passes D-134 read-only re-verification.
```

Required decision deltas:

- D-117: add the immutable prospective → external finalized lifecycle, outcome-blind finalization, distinct collection/final identities, and “gamma cannot arm before the rehearsed edge closes.”
- D-134/D-078 readiness amendment: add the gamma-only rehearsal row and refusal code above.
- D-122’s existing scientific scope need not change. A separate pre-freeze ruling must settle test, multiplicity and p256 floor/transport; it must not be smuggled into this implementation contract.

### F4 — should-fix: why not convert to historical final v3

A persisted historical-v3 conversion is the wrong wire because:

- The historical validator hard-pins one Splitwise contrast, two stages, 40 entries and Holm `m=1`.
- Relabeling the prospective schema as v3 either refuses immediately or pressures weakening the historical frozen contract.
- A new converted manifest ID would not match collection campaign records; preserving the old ID would violate canonical final-manifest identity.
- Prospective-only fields—attachment lineage, p256 floor dependency, target precheck, estimator registration and semantic lock—have no lossless historical-v3 home.
- Two stored science representations can drift together after outcomes are known unless both are independently anchored to the frozen pack.
- The claim-artifact validator currently requires v3 Holm `m=1` at [artifact.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bcon/joulewise/analysis_engine/artifact.py:683).
- Cross-family LOO currently takes block IDs from the family’s first contrast at [analysis_engine/__init__.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bcon/joulewise/analysis_engine/__init__.py:1391). Decode and prefill use different block IDs, so a shared `m=2` family needs frozen block strata mapping block number 1–10 across both arms.

Teach the consumer the finalized schema through one centralized `is_abba_v3_consumable_schema()` predicate, update campaign lookup to use `collection_manifest_id`, and make artifact/family validation compare against frozen family semantics rather than the historical `m=1` constant. No automatic “finalize on load” path should exist.

## Residual risk

The authoritative council verdict named in the prompt was absent from this checkout, so final adjudication should compare its exact Phase-0 language against this proposal. The refuter reports and cited implementation/decision sources were available and consistent. No files were changed.