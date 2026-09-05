```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The unfrozen D-117 V5 generator now uses a tested shared core with byte-parity evidence; historical hash-pinned generators and the unmerged next floor producers require lead rulings before the row can close.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-GENERATOR-CORE-01"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/process_traces/2026-09-04-fanout/GENERATOR-CORE-01/01-sol-report.md",
    "docs/specs/generator_core.md",
    "joulewise/campaign_generator_core.py",
    "scripts/check_campaign_generator_core_parity.py",
    "tests/test_campaign_generator_core.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_campaign_generator_core tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 33 tests in 5.606s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 33 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_decode_contrast_plan tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_d117_v3_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 71 tests in 81.082s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 71 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d165_dominance_closeout tests.test_issue_g2a_prefill_prompt_pin tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 101 tests in 14.510s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 101 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 scripts/check_campaign_generator_core_parity.py --baseline-ref HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PARITY_OK files=112 excluded=['generate_configs.py', 'plan_tree.json', 'plan_tree.sha256'] baseline=HEAD"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PARITY_OK files=112 .* baseline=HEAD"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "python3 -m py_compile joulewise/campaign_generator_core.py configs/campaigns/d117_contrast_v5/generate_configs.py scripts/check_campaign_generator_core_parity.py tests/test_campaign_generator_core.py && git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The nine historical generators are files inside authenticated pack trees. Extracting their local copies makes committed_pack_tree_sha256 refuse because generate_configs.py differs from the committed bytes.",
      "needs": "Rule whether hash-pinned historical generator snapshots are exempt from deduplication. Recommendation: exempt them, keep their bytes unchanged, and require the shared core for every unfrozen and future producer."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The next Qwen3 floor producers exist only on the separately reviewed, unmerged feat/2026-09-02-v5-floor-generator branch at 557b7fc5, not on this worktree base.",
      "needs": "Choose integration order. Recommendation: land this core first, rebase the reviewed producer branch, and replace its copied mechanics with shared-core imports as a reviewed delta."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Parity excludes the generator source and the plan-tree files that authenticate that source; those bytes must change when the source gains a shared-core import. All other emitted V5 pack files compare byte-identically.",
      "needs": ""
    }
  ]
}
```

## Change

Added a shared campaign-generator module for canonical rendering, SHA-256
sidecars, pack inventory, successor identity, and the single-operator
desk-generation write boundary. The unfrozen D-117 V5 contrast generator now
imports that core. A counterfactual test requires those imported names to
resolve to the shared implementations, so restoring a local copy fails.

The scoped design records the forcing problem, three options, the recommended
boundary, a worked floor-producer example, and the two unresolved integration
rulings.

| Finding | Decision | Executed evidence | State |
|---|---|---|---|
| The unfrozen generator duplicated reusable mechanics. | Extract its five live helpers and provide the common identity factory. | V1, V3 | Implemented |
| A direct ten-generator extraction rewrites authenticated historical pack files. | Restore all nine historical files from the session base; do not update frozen digests. | Initial focused run refused with `disk and committed bytes/mode differ for b'generate_configs.py'`; V2 then passed after restoration. | NEEDS_RULING F1 |
| The new shared calls might change emitted campaign bytes. | Compare the pre-extraction `HEAD` implementation with the working tree at the same issued fixture pin. | V4: all 112 non-self-bound files were identical. | Pass |
| The next floor producers are owned by an unmerged reviewed branch. | Preserve that history instead of copying it into this branch. | `git show-ref` resolved branch head `557b7fc5`; the files are absent from this base. | NEEDS_RULING F2 |

The forbidden repository-wide test suite was not run. No hardware or quiet
machine work was required or started. The protected state-kernel, queue,
run-state, decision-log, and paper-skeleton files were not edited.

## Verification notes

The first mechanical attempt extracted the common identity class from the nine
historical files as well as the unfrozen file. The focused generator command
failed with nineteen failures and four errors; the decisive refusal was the
committed-pack byte mismatch above. Those nine edits were completely restored
before V1–V5. This failure is evidence for F1, not an accepted baseline drift.

V4 excludes only `generate_configs.py` and the two plan-tree files that bind
its digest. Their bytes necessarily change when source is refactored. Every
scientific configuration, manifest, condition-family artifact, and other
generator output in the comparison was byte-identical.

## Residual risk

GENERATOR-CORE-01 cannot honestly be marked complete until F1 defines how the
acceptance treats immutable historical snapshots and F2 places the actual next
floor producers on top of the shared core. No scope expansion is required for
either option.
