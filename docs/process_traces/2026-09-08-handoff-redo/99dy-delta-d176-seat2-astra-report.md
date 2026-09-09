```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Executed all requested seat-2 fixture checks; no new defect found; repository unchanged.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "head_end": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat2-producer"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest -v tests.test_night_gate tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas.ProductionCustodyResolverTests tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 130 tests in 10.554s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/d176-seat2-relaunch-audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ROOT nested FAIL",
          "ROOT equal FAIL",
          "ROOT wrong-name FAIL",
          "ROOT sibling PASS",
          "ROOT symlink FAIL",
          "PASS census: empty/nonempty override unchanged; G6 omitted/empty/duplicate/changed refused",
          "GO_KEYS schema_version,receipt_id,receipt_class,purpose,plan_id,plan_sha256,pack_id,pack_sha256,arm_receipt,boot_session_id,t0_evidence,t0_evidence_set_sha256,launch_manifest_sha256,window_environment_sha256,window_chain_sha256,repo_head,measurement_root,measurement_head,confirmation_record,authorization,census,issued_epoch_s,issued_monotonic_ns,valid_until_monotonic_ns,conditions,verdict",
          "PASS 3a/3f: ARM verify before GO write; exact driver ARM; eight argv flags; DEVNULL; 0600 exclusive GO",
          "PASS 3b: refusal exact legacy receipt keys, no GO",
          "PASS 3c preparation launch_go_receipt_invalid pack_root.pack_sha256",
          "PASS 3c GO launch_go_receipt_invalid pack_root.pack_sha256",
          "PASS 3d: real scanner authenticates planted arm-0002 plus sidecar; driver refuses before GO",
          "PASS 3e duplicate launch_go_receipt_invalid",
          "PASS 3e symlink launch_go_receipt_invalid",
          "PASS byte-diff: receipt keys/validator and three marker functions unchanged from 0a7c5858",
          "PASS repository clean: git status --short and git diff --stat empty",
          "PASS supplemental audit complete"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^PASS supplemental audit complete$"}
    }
  ],
  "flags": []
}
```

## Findings

None.

V1 executed 3(g): `test_chain_identity_probe_follows_complete_closed_marker` confirmed complete JSON and a closed descriptor before the identity probe, including interrupted-probe behavior. `test_chain_identity_is_added_by_atomic_replace` inspected both files and executed the real atomic replacement. Both passed.

V2 compared the emitted GO’s 26 keys against the contract table exactly; the complete enumeration appears above. Unified source diffs were empty for `_RECEIPT_KEYS`, `validate_receipt`, and all three marker functions against `0a7c5858`.

Additional passing cases covered ARM refusal, same-boot consumption, stale ARM selection, missing/substituted manifests, authorization/confirmation substitution, altered T-0 evidence, expired windows and existing GO replay.

Final assertions confirmed `git status --short` empty, `git diff --stat` empty, `git diff HEAD --stat` empty and HEAD unchanged. Only temporary audit files were written under `/tmp`.

## Residual risk

Evidence is synthetic: ARM authoring, verification and machine probes use fixtures; the planted higher receipt uses the real namespace scanner. This establishes producer behavior, not live hardware readiness or integrated seat-3 consumption correctness. The full canonical suite was not rerun.