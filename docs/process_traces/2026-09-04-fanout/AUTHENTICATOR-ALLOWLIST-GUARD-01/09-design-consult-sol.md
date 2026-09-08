```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Salvage the exact-set core behind an immutable, schema-selected artifact-family spec enforced for every registry id.",
  "workspace": {
    "base_requested": "eff3304e",
    "base_mode": "exact",
    "head_start": "eff3304e127a585143026e9368c0c5e0a31a1ed4",
    "head_end": "eff3304e127a585143026e9368c0c5e0a31a1ed4",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/09-design-consult-sol.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/09-consult-fable-blind.md",
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/10-design-consult-opus.md"
  ],
  "verdict": {
    "landability": "NOT LANDABLE",
    "recommendation": "SALVAGE EXACT-SET CORE WITH A NEW AUTHORITY ROOT",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "The current digest pins one v5 instance and its equality check is conditional on one registry id, leaving the artifact family open."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "Activating D-151 V-1(vii) as a cross-transaction mechanism requires a new decision-log entry with installation status, not only implementation prose."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && rg -n 'if isinstance\\(pack_ids, Mapping\\) and registry_id == \"d117-r1-lifecycle-v1\"' joulewise/arm_readiness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "eff3304e127a585143026e9368c0c5e0a31a1ed4",
          "1955:    if isinstance(pack_ids, Mapping) and registry_id == \"d117-r1-lifecycle-v1\":"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^eff3304e127a585143026e9368c0c5e0a31a1ed4\\n1955:    if isinstance\\(pack_ids, Mapping\\) and registry_id == .d117-r1-lifecycle-v1.:$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/09-design-consult-sol.md\"); s=p.read_text(encoding=\"utf-8\"); raw=s[8:s.index(chr(10)+chr(96)*3+chr(10),8)]; json.loads(raw); assert len(raw.encode(\"utf-8\")) <= 8192; assert len(s.encode(\"utf-8\")) < 12000; print(\"report contract: valid JSON, UTF-8, envelope <=8192 bytes, file <12 KB\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report contract: valid JSON, UTF-8, envelope <=8192 bytes, file <12 KB"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report contract: valid JSON, UTF-8, envelope <=8192 bytes, file <12 KB$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "?? docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/09-consult-fable-blind.md",
          "?? docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/09-design-consult-sol.md",
          "?? docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/10-design-consult-opus.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)[\\s\\S]*09-design-consult-sol.md[\\s\\S]*10-design-consult-opus.md$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The frozen spec and unconditional schema-keyed derivation require lead adoption.",
      "needs": "Adopt or amend this design, assign the decision-log entry, and issue a fresh implementation row."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The cited AUTH section is absent at eff3304e; parking is explicit in HEAD history and trace 08.",
      "needs": "Lead should custody the omitted AUTH ruling text when installing the design."
    }
  ]
}
```

## Findings

### F1 — blocker — close artifact families, not names or registry instances

Verdict: the landing is not landable, but it does not need a ground-up rebuild. Preserve the positive exact-set comparison and the D-151 conditional pinset gate; replace their authority root.

The closed authority should be immutable canonical JSON at `docs/contracts/r1_governed_artifact_families_v1.json`. Code maps **lifecycle schema version**, never either registry id, to `(spec_path, spec_sha256)`. Expansion creates a versioned spec, lifecycle-schema bump, code-map entry, and ruling; the spec is never allowlisted. Its dimensions are profiles `ALPHA/BETA/GAMMA`; the eleven slugs `acceptance-owner`, `doctrine-pin`, `estimator-identity`, `mint-trust`, `multicell-mint`, `pack-authentication`, `pack-family`, `reason-code-coverage`, `receipt-oracle`, `recovery-ledger-test`, `three-window-regression`; and these eight families:

| Subject family | Exact path template | Closed proof handler |
|---|---|---|
| source manifest | `configs/campaigns/{pack_id}/arm_readiness.sources/{slug}.json` | matching receipt's `dependency_manifest_sha256` plus dependency replay |
| evidence receipt | `.../arm_readiness.evidence/evidence-{slug}.json` | canonical receipt validation plus semantic/re-derivation replay |
| evidence sidecar | prior path + `.sha256` | exact GNU sidecar relation plus receipt replay |
| freeze receipt | `.../arm_readiness.freeze.receipts/freeze-0004.json` | PASS freeze semantic replay and plan-tree binding |
| freeze sidecar | prior path + `.sha256` | exact GNU sidecar relation plus freeze replay |
| plan tree | `.../plan_tree.json` | normalized dependency replay and committed-pack binding |
| plan-tree sidecar | `.../plan_tree.sha256` | exact sidecar relation plus committed-pack binding |
| successor histsem pinset | `configs/arm_readiness/legacy_receipt_histsem_pinset_v{generation}_v1.json` | D-151 C→S against custody-external `hC` |

`proof_handler` values are themselves a code-closed enum. The table authorizes subjects eligible for subtraction, never an authenticator path: the step-6 table `C`, its sidecar, and the out-of-band `hC` are categorically outside every expansion. The dimensions produce `3 × (11 × 3 + 4) + 1 = 112` today. New slugs, profiles, receipt ordinals, templates, or proof handlers refuse until a new spec version is installed.

The production API should be:

```python
def derive_r1_irrelevant_path_manifest(
    repository: Path,
    *,
    anchor_commit: str,
    expected_row_registry_sha256: str,
) -> R1DerivedPathManifest: ...
```

It loads `ROW_REGISTRY_RELATIVE_PATH` with `git show anchor_commit:path`, verifies that blob against `expected_row_registry_sha256`, parses the exact outer registry, and extracts **that blob's** `freeze_evidence_lifecycle` record. It selects the frozen spec solely from that record's `schema_version`, loads the spec at the same Git commit, and verifies the code-pinned spec SHA-256. Unknown lifecycle schema refuses; registry ids are output metadata only and are never predicates.

The function validates the exact three-profile `successor_pack_ids`, derives their common generation, expands the templates, and returns sorted paths plus `spec_sha256`, `row_registry_sha256`, `lifecycle_sha256 = SHA256(render_json(freeze_evidence_lifecycle))`, `anchor_commit`, and a domain-separated manifest digest. At registry load the anchor is committed `HEAD`; at an evidence gate it is the receipt's `derivation_commit` and the expected registry digest is the plan tree's authenticated `row_registry.sha256`. The lifecycle is therefore pre-registration state, not a caller-supplied mapping.

Every R1 registry load must exact-compare its serialized `irrelevant_path_allowlist` with the returned paths, regardless of either registry id. The serialized list may remain as D-151's reviewable candidate value, but runtime subtraction must use `R1DerivedPathManifest.paths`, not reread the raw field. A fresh id therefore selects the same schema-owned spec; adding `future-confirmation-token.json` fails equality. If the extra file exists only in Git, it is absent from the derived set and the changed-set gate refuses it. A future schema cannot evade this: it is unknown until code explicitly maps it to a frozen spec.

Refusal mapping needs no new vocabulary: spec absence/digest/schema failure, lifecycle instantiation failure, or candidate/derived inequality is `readiness_row_registry_mismatch`; an observed extra changed path is `readiness_r1_dependency_changed_set`; a listed subject whose promised proof fails retains its owning refusal (`readiness_r1_dependency_manifest`, `readiness_dependency_refused`, evidence/sidecar digest mismatch, or the existing C→S `readiness_r1_dependency_changed_set`). Membership never forgives a failed proof.

The one acceptance regression is `test_fresh_lifecycle_registry_id_cannot_add_path_outside_frozen_artifact_spec`: copy the real registry, set only the inner id to `d117-r1-lifecycle-v2`, append and sort `configs/arm_readiness/future-confirmation-token.json`, call the production registry validator, and require `ArmReadinessError.reason_code == "readiness_row_registry_mismatch"`. Do not register, name-classify, or fake an authenticator. Replacing the unconditional comparison with the old id predicate must make this same test fail with “ArmReadinessError not raised.”

Salvage `_r1_derived_irrelevant_path_manifest`'s template expansion, exact equality, the unchanged 112 candidate entries, and `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS`/C→S enforcement. Delete the `registry_id == "d117-r1-lifecycle-v1"` condition, `_R1_ALLOWLIST_PROVENANCE_SHA256` (it pins one materialization, not the family law), `_R1_GOVERNED_PRE_REGISTRATION_EVIDENCE_STEMS` after moving its values to the frozen spec, and all production reads that treat the raw registry list as authority. Do not restore the retired decorator/registry, and do not build the dispatcher proposed in round 2.

I disagree with round 2's dispatcher recommendation: it closes selected Python calls, not the repository artifact class. I agree with consult 06's move to positive provenance but disagree that it specified enough to implement; round 07 converted that phrase into a hash of one `_v5` instance and then guarded it by the very id whose evolution it had to survive. I do not disagree with D-151's fixed-point rule, D-161's evidence/pre-registration classification, or the parking ruling.

### F2 — should_fix — record activation of V-1(vii)

Yes, a decision-log entry is required. V-1(vii) was only a standing dissent; this design makes it operative across future transactions and fixes versioning, schema dispatch, proof handlers, digests, refusal mapping, and retirement semantics. Use a new decision id that points back to D-151 rather than rewriting D-151's historical ruling. Per D-170, record it as `open (installs via <fresh task id>)` until the production derivation and the single fresh-id regression exist; then adopt it with that evidence pointer. The entry must pin the spec path/SHA and state that a registry-id change can never select or disable the spec.

## Residual risk

The `_v5` packs are absent at this HEAD, so the 112 templates were checked against the registry and S-0 records, not generated trees. Implementation review must compare one real expansion before landing. Trace 08 already executes the fresh-id bypass; no runtime test was needed here.
