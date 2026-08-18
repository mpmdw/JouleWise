```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt literal cross-root freeze-0002 receipts with authenticated predecessor bindings, without superseding v1; current mint and runsheet cannot implement the ruled transaction.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "0cb9bf21dbc30ee8a412fcf4bab8970b5c4bd12f",
    "head_end": "0cb9bf21dbc30ee8a412fcf4bab8970b5c4bd12f",
    "upstream_end": "6ddeb7d365772335717e3143dceccf4382c49f8d",
    "branch": "impl/successor-generator-repairs"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "adopted_design": "Each _v2 pack's first and only local freeze receipt is literally freeze-0002. Its v2 schema carries a non-superseding, cryptographically authenticated predecessor object referring to the corresponding v1 pack and freeze-0001.",
    "findings": [
      {
        "id": "D-1",
        "severity": "blocker",
        "title": "Chain-monotonic means literal cross-root freeze-0002",
        "recommendation": "Derive the successor ordinal from the authenticated predecessor receipt and require successor_number == predecessor_number + 1."
      },
      {
        "id": "D-2",
        "severity": "blocker",
        "title": "Freeze-receipt v2 needs authenticated predecessor semantics at mint and load",
        "recommendation": "Add an exact-key predecessor object and one shared authenticator used before writes, during idempotent replay, and whenever the active freeze reference is loaded."
      },
      {
        "id": "D-6",
        "severity": "blocker",
        "title": "The complete-family marker's exact schema, path, and activation predicate remain insufficiently recorded",
        "recommendation": "Obtain an explicit lead/Ed ruling before publication; the numbering WO can land independently."
      },
      {
        "id": "D-3",
        "severity": "should_fix",
        "title": "Freeze predecessor binding is not semantic supersession",
        "recommendation": "Do not apply arm-receipt supersession or readiness_receipt_superseded to freeze receipts; preserve v1 as an authentic historical record."
      },
      {
        "id": "D-4",
        "severity": "should_fix",
        "title": "The change crosses mint, schema, namespace, load, attachment, CLI, verification, and tests",
        "recommendation": "Implement dual-schema routing and remove latest-entry selection as an authority rule."
      },
      {
        "id": "D-5",
        "severity": "should_fix",
        "title": "Regression coverage must prove chain failures are pre-write and v1 remains authentic",
        "recommendation": "Add success, mutation, absence, REFUSE, ordinal, idempotency, exact-key, and historical-v1 regressions."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "set -eu; for anchor in 'docs/decision_log.md:9711' 'docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md:55' 'docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md:61' 'joulewise/arm_readiness.py:46' 'joulewise/arm_readiness.py:1320' 'joulewise/arm_readiness.py:1912' 'joulewise/arm_readiness.py:1990' 'joulewise/arm_readiness.py:2095' 'joulewise/arm_readiness.py:3190' 'joulewise/arm_readiness.py:3398' 'joulewise/arm_readiness.py:3472' 'joulewise/arm_readiness.py:4122'; do file=${anchor%:*}; line=${anchor##*:}; test -f \"$file\"; test \"$(wc -l < \"$file\")\" -ge \"$line\"; done; for anchor in '/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/coldgate-freeze-semantics/14-composed-verdict.md:63' '/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/docs/process/phase2-transaction-runsheet.md:37'; do file=${anchor%:*}; line=${anchor##*:}; test -f \"$file\"; test \"$(wc -l < \"$file\")\" -ge \"$line\"; done; test \"$(sed -n '9712p' docs/decision_log.md)\" = '`_v2` successor pack IDs; chain-monotonic `freeze-0002` with explicit'; test \"$(sed -n '3472p' joulewise/arm_readiness.py | xargs)\" = 'number = 1'; test \"$(sed -n '39p' /private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/docs/process/phase2-transaction-runsheet.md | xargs)\" = 'bindings; existing operational horizons). NO code edits (delta-proven'; printf 'anchor_files=14 assertions=3 result=PASS\\n'; git status --short --branch; git rev-parse HEAD; git rev-parse '@{upstream}'; git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "anchor_files=14 assertions=3 result=PASS",
          "## impl/successor-generator-repairs...origin/impl/successor-generator-repairs [ahead 3]",
          "0cb9bf21dbc30ee8a412fcf4bab8970b5c4bd12f",
          "6ddeb7d365772335717e3143dceccf4382c49f8d",
          "impl/successor-generator-repairs"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "anchor_files=14 assertions=3 result=PASS[\\s\\S]*impl/successor-generator-repairs"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The transaction runsheet is absent from this branch and was inspected in the integration/phase2-transaction worktree.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The family marker requirement is ratified, but its exact schema/path and active-family predicate are not stated by D-139.",
      "needs": "Ed or the lead must ratify those marker particulars before irreversible publication."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only design review; no implementation or test suite was run.",
      "needs": ""
    }
  ]
}
```

## Findings

### D-1 — Literal cross-root `freeze-0002` is the correct reading

Adopt the family-generation interpretation: every corresponding `_v2` pack contains a singleton `freeze-0002.json`, whose authenticated predecessor is that role’s `_v1/freeze-0001.json`.

This follows directly from:

- D-139’s “chain-monotonic `freeze-0002` with explicit predecessor bindings” at `docs/decision_log.md:9711-9714`.
- R1’s explicit example: a predecessor `freeze-0001` produces `freeze-0002` even under a new pack root, at `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:172-184`.
- R1’s warning that cross-root numbering belongs in the v2 schema, at `coldgate-adjudicator-ruling.md:55-61`.
- The Phase-2 options, where resetting each new root to `freeze-0001` was option C and explicitly not recommended.

“Family-level” means the three role chains advance in lockstep and the family marker verifies that all members are generation 2. It does not mean one shared receipt namespace.

I explicitly reject “new root, therefore local `freeze-0001`.” That would make the approved word `freeze-0002` meaningless and conceal lineage from operators.

### D-2 — Freeze-receipt v2 schema and validation

Use a distinct constant such as:

`joulewise.arm_readiness_freeze_receipt.v2`

Do not reinterpret v1. Define:

```text
FREEZE_RECEIPT_V2_KEYS =
    FREEZE_RECEIPT_V1_KEYS
    - {"supersedes"}
    + {"predecessor"}
```

The required `predecessor` object should contain:

```json
{
  "pack_id": "d117_floor_qwen25_1p5b_v1",
  "pack_path": "configs/campaigns/d117_floor_qwen25_1p5b_v1",
  "pack_digest_algorithm": "joulewise.committed_pack_tree_sha256.v1",
  "pack_sha256": "<final committed predecessor-pack digest>",
  "plan_id": "<predecessor plan id>",
  "plan_sha256": "<predecessor frozen-plan sha256>",
  "freeze_receipt": {
    "receipt_id": "freeze-0001",
    "path": "arm_readiness.freeze.receipts/freeze-0001.json",
    "sha256": "<receipt sha256>"
  },
  "identity_receipt": {
    "receipt_id": "<projection receipt id>",
    "path": "identity_pin_projection.receipts/projection-0001.json",
    "sha256": "<projection sha256>"
  },
  "evidence_set_sha256": "<domain-separated canonical hash of the predecessor freeze receipt's evidence-reference array>"
}
```

Rationale:

- `pack_sha256` binds all predecessor pack bytes.
- `freeze_receipt` binds the specific chain head and ordinal.
- `plan_sha256`, identity receipt, and evidence-set root expose the semantic bindings R1 explicitly requested instead of relying only on an opaque whole-pack hash.
- `pack_path` is a repository-relative locator. Do not serialize an environment-specific absolute predecessor path.
- No additional lineage ID belongs in this receipt. The row-registry profile supplies ALPHA/BETA/GAMMA, the receipt ordinal supplies generation, and the external family marker owns family identity and complete-member synchronization.

Validation belongs in both places:

1. Mint-time, before any `_exclusive_write` or plan-tree replacement.
2. `_load_freeze_reference`, on every active load and idempotent replay.

The shared predecessor authenticator must:

- Resolve `pack_path` inside the repository.
- Authenticate the committed predecessor pack digest.
- Require the plan-pinned predecessor freeze receipt to exist exactly once.
- Authenticate its sidecar and schema.
- Require recorded status `PASS`.
- Authenticate the referenced identity receipt and evidence set.
- Require matching profile/role.
- Parse both ordinals and require `successor == predecessor + 1`.
- For tonight, therefore require `freeze-0002` over `freeze-0001`.

Absent, unreadable, uncommitted, malformed, digest-divergent, profile-mismatched, or REFUSE predecessors must raise the governed `SUCCESSOR_CHAIN` refusal before writing anything. They should not mint a new REFUSE receipt: an invalid ancestry record is not a legitimate chain member.

Historical v1 authentication must not rerun its now-expired evidence as present authorization. It authenticates the exact historical PASS record and its issued bindings; it is not grandfathered into R1 consumption.

### D-6 — Remaining Ed ruling

The complete-family marker is mandatory, but D-139 does not state its exact schema, repository path, or the predicate by which a per-pack loader decides that a candidate family is active. R1 had reserved those particulars explicitly.

That does not block WO-FREEZE-NUMBERING. It does block irreversible family publication.

The final marker should bind the final three pack digests and receipt hashes after all pack bytes are immutable. A contained freeze receipt must not bind its own final successor-pack digest: because the receipt is itself a pack byte, that creates a self-hash cycle. I explicitly disagree with that portion of the earlier Phase-2 plan consult. The external marker is the correct owner of final successor-pack digests.

### D-3 — Predecessor, not supersession

Do not extend arm-side supersession to freeze receipts.

Arm receipts form competing, perishable launch capabilities. Hence `scan_receipt_namespace` requires each successor to semantically supersede the previous arm receipt (`arm_readiness.py:2095-2108`), and verification emits `readiness_receipt_superseded`.

Freeze receipts describe different immutable pack generations. The v2 receipt’s existence does not invalidate the v1 pack or its historical receipt. Therefore:

- V2 carries `predecessor`, not `supersedes`.
- The v1 receipt remains structurally authentic and verifiable under v1.
- No freeze path emits `readiness_receipt_superseded`.
- “Active family” selection belongs to the family marker, not receipt supersession.

### D-4 — Mechanical implementation bar

- I-1: Preserve `FREEZE_RECEIPT_SCHEMA` as v1 compatibility or rename it explicitly to `FREEZE_RECEIPT_V1_SCHEMA`; add v2 and dual-schema dispatch.
- I-2: Add exact v2/predecessor key constants and validators.
- I-3: Change `generate_freeze_receipt` to accept a predecessor pack root for governed successor packs. Accept paths only; derive every ID, digest, ordinal, and conclusion.
- I-4: Update the CLI `freeze` command with `--predecessor-pack-root`. Missing predecessor input for an R1 `_v2` pack refuses.
- I-5: Change `scan_receipt_namespace` to accept v1 and v2, enforce filename/receipt-ID equality, and validate v2 ordinal shape. Cross-root filesystem authentication remains in the shared chain authenticator.
- I-6: Change `_load_freeze_reference` to authenticate the v2 predecessor chain after authenticating the plan-pinned current receipt.
- I-7: Replace `committed_receipts[-1]` in `plan_arm_readiness_attachment` with unique, plan-consistent selection. Highest filename must not confer authority.
- I-8: Make the existing-receipt idempotency branch call the full loader/chain authenticator before returning `mutated: false`.
- I-9: Add v2 dispatch to `verify_receipt`.
- I-10: Do not edit, regenerate, rename, or add files beneath the three `_v1` pack roots.
- I-11: The family marker/verifier remains a distinct transaction concern; it must not force post-mint pack mutation.

### D-5 — Required regressions

- R-1: PASS v1 predecessor mints a v2 singleton named exactly `freeze-0002`.
- R-2: Serialized predecessor object equals independently derived pack, plan, receipt, projection, and evidence-set bindings.
- R-3: Missing predecessor directory, receipt, or sidecar refuses before any successor file or plan-tree mutation.
- R-4: REFUSE-status predecessor refuses before writes.
- R-5: Tampered predecessor pack, receipt, projection, evidence item, or sidecar refuses at mint and later load.
- R-6: `freeze-0001 → freeze-0003`, self-predecessor, wrong role, and wrong pack-ID mapping refuse.
- R-7: A valid singleton `freeze-0002` under a new root is accepted without requiring a local `freeze-0001`.
- R-8: Repeating mint is byte-idempotent, returns `mutated: false`, and still reauthenticates the predecessor.
- R-9: All three committed v1 receipts retain identical bytes/digests and continue authenticating as historical v1 records.
- R-10: The presence of v2 never makes v1 return `readiness_receipt_superseded`.
- R-11: Missing/unknown v2 predecessor keys and illegal `supersedes` fail exact-key validation.
- R-12: Attachment construction refuses multiple committed freeze candidates instead of selecting the last.
- R-13: Mutation test proves that bypassing predecessor authentication makes a negative test fail.
- R-14: Three-profile family regression requires ALPHA/BETA/GAMMA all at ordinal 2 with their corresponding v1 predecessors.

### Runsheet corrections

The integration runsheet’s step 4 at `phase2-transaction-runsheet.md:37-40` is false and must be replaced.

- Add WO-FREEZE-NUMBERING’s code and focused regressions to step 1’s integration order, before successor evidence/freeze authoring.
- Step 4 should install the approved registry values only after the v2 schema, mint, load, CLI, and verification support has landed. Remove “NO code edits.”
- Step 5 must pass the exact three predecessor roots, require pre-write chain authentication, mint singleton `freeze-0002` receipts, then treat every pack byte as immutable.
- The marker is created outside the pack roots after their bytes are final; it binds their final digests and receipt hashes.
- Step 6 remains Ed’s irreversible exact-byte confirmation. No marker publication and no post-mint pack edit may precede that confirmation.

All requested anchors resolved in V1.

## Residual risk

No additional residual risk beyond the disclosed integration-worktree drift, unimplemented family-marker particulars, and lack of executable regression evidence in this read-only round.