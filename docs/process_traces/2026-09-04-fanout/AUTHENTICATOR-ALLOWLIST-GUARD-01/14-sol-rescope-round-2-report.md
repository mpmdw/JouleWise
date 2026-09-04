```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "Implementation is blocked because binding clause 2 requires an out-of-scope production registry edit before the in-scope exact-key schema change can be valid.",
  "workspace": {
    "base_requested": "9ada1e34",
    "base_mode": "exact",
    "head_start": "9ada1e34bc147c35abef21ca5f68277f86abbd70",
    "head_end": "9ada1e34bc147c35abef21ca5f68277f86abbd70",
    "upstream_end": "9ada1e34bc147c35abef21ca5f68277f86abbd70",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/14-sol-rescope-round-2-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD; git rev-parse @{upstream}; git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9ada1e34bc147c35abef21ca5f68277f86abbd70",
          "9ada1e34bc147c35abef21ca5f68277f86abbd70",
          "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^9ada1e34bc147c35abef21ca5f68277f86abbd70\\n9ada1e34bc147c35abef21ca5f68277f86abbd70\\nfeat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; d=json.loads(pathlib.Path(\"configs/arm_readiness/d117_row_registry_v2.json\").read_text())[\"freeze_evidence_lifecycle\"]; print(d[\"schema_version\"]); print(sorted(d[\"successor_policy\"]))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise.arm_readiness_freeze_evidence_lifecycle_registry.v1",
          "['cross_chain_numbering', 'family_publication_first_generation', 'family_publication_marker_schema', 'freeze_receipt_v2_predecessor_bindings', 'successor_pack_ids']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^joulewise\\.arm_readiness_freeze_evidence_lifecycle_registry\\.v1\\n.*successor_pack_ids.*$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import hashlib,json,pathlib; d=json.loads(pathlib.Path(\"configs/arm_readiness/d117_row_registry_v2.json\").read_text()); a=d[\"freeze_evidence_lifecycle\"][\"irrelevant_path_allowlist\"]; raw=json.dumps(a,ensure_ascii=False,separators=(\",\",\":\"),sort_keys=False).encode(); print(\"allowlist_count=%d\" % len(a)); print(\"allowlist_canonical_sha256=%s\" % hashlib.sha256(raw).hexdigest())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "allowlist_count=112",
          "allowlist_canonical_sha256=fd8cba2e63e8f48c9d23d679fdd143e37226cc315594158e9d0d10caba8003da"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^allowlist_count=112\\nallowlist_canonical_sha256=fd8cba2e63e8f48c9d23d679fdd143e37226cc315594158e9d0d10caba8003da$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Clause 2 requires the tracked lifecycle registry to advance from schema .v1 to .v2 and add exact-key successor_freeze_receipt_ids, but that production registry is excluded from WRITE_SCOPE.",
      "needs": "Resume with configs/arm_readiness/d117_row_registry_v2.json added to WRITE_SCOPE."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests or mutations ran because no coherent production implementation can be made before the scope expansion.",
      "needs": "After expansion, run the ruled RED/GREEN test, three mutation kills, and three focused modules one at a time."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "configs/arm_readiness/d117_row_registry_v2.json"
    ],
    "reason": "Binding clause 2 requires changing this exact production record to lifecycle schema .v2 and adding the exact three-profile successor_freeze_receipt_ids map; the in-scope validator uses exact keys and cannot accept the unchanged .v1 record after implementation.",
    "blocked_work": "All clauses 1-4, RED/GREEN, mutation kills, and focused green verification are blocked because landing only the in-scope half would invalidate the tracked production registry.",
    "minimal_change": "Change only freeze_evidence_lifecycle.schema_version and add successor_policy.successor_freeze_receipt_ids with ALPHA/BETA/GAMMA each mapped to freeze-0004; leave the 112-entry irrelevant_path_allowlist byte-unchanged."
  }
}
```

## Change

No production or test edit was made. The binding ruling requires one atomic contract change spanning the in-scope validator and the out-of-scope tracked registry. The baseline has no committed governed `_v5` pack or family-publication-marker path, and the current 112-entry candidate has canonical SHA-256 `fd8cba2e63e8f48c9d23d679fdd143e37226cc315594158e9d0d10caba8003da`.

## Clause map

| Clause | Production site | Biting assertion | Counterfactual / status |
|---|---|---|---|
| 1 — code-owned eight-family derivation, no digest | `joulewise/arm_readiness.py:637-1714` | NOT PINNED | Blocked before edits by clause 2's atomic registry change. |
| 2 — `.v2`, exact receipt-id map, shared family replay | `joulewise/arm_readiness.py:68-70,629-634,1672-1714,11300-11347`; required record `configs/arm_readiness/d117_row_registry_v2.json:516-536` | NOT PINNED | Required record is outside WRITE_SCOPE. |
| 3 — mapped/mapped or reserved/reserved totality | `joulewise/arm_readiness.py:1718-1962` | NOT PINNED | Cannot enforce exact new keys while the production record remains `.v1`. |
| 4 — one two-subtest regression and three kills | `tests/test_arm_readiness_schemas.py:531-550` | NOT PINNED | RED/GREEN and mutations wait for the atomic production scope. |

## Verification notes

The preflight HEAD and upstream match exactly. No tests were run; the runner's one-at-a-time restriction was preserved.

## Residual risk

Applying only the code/test portion would either make the tracked registry fail schema validation or require a compatibility/default branch that directly violates clauses 2 and 3.
