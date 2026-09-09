```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed D-176 decision and kernel graph; requested checks pass; contract draft needs lead wire rulings.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "952dc74123aa1c221cee7dca7bd41ddbd617bb53",
    "head_end": "952dc74123aa1c221cee7dca7bd41ddbd617bb53",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-stage3-ruling"
  },
  "pathspec": [
    "docs/decision_log.md",
    "docs/process/state_kernel.json",
    "TASK_QUEUE.md",
    "RUN_STATE.md",
    "tests/test_gen_state.py",
    "docs/contracts/pack_night_go_receipt.md",
    "docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-08-handoff-redo/86-brief-d176-install-astra.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py > /private/tmp/d176-acceptance-rwx2j4__/generate.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py --check > /private/tmp/d176-acceptance-rwx2j4__/final-gen-state-check.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state > /private/tmp/d176-acceptance-rwx2j4__/test-gen-state-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness > /private/tmp/d176-acceptance-rwx2j4__/final-test-docs-freshness.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: replay requires a recorded GO path, but the judge's v3 reference omits path and the GO schema omits receipt_id.",
      "needs": "Pin GO identity derivation and replay-path storage; recommended: adopt Opus go_receipt.path with explicit identity derivation."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: consumption claim_eligible placement, authorization attempt binding, and authority/confirmed_at/condition-evidence encodings are unspecified.",
      "needs": "Resolve contract section 8, then obtain Opus contract refutation before landing and issuing code scope."
    }
  ]
}
```

## Change

Decision/index, graph, generated views and test pins are installed. The contract preserves the exact ruled lists and documents unresolved fields.

[Installation report](/Users/edr/code/JouleWise-wt-d176/docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md)

## Verification notes

All requested checks pass: state tests **44**, docs-freshness tests **31**. No repository-wide suite or commit.

## Residual risk

Next: lead ruling on [contract §8](/Users/edr/code/JouleWise-wt-d176/docs/contracts/pack_night_go_receipt.md), then Opus refutation. The contract remains a draft until those wire details are pinned.