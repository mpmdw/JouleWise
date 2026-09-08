```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Installed F3 forwarding ruling, verified all call-site lines, updated §3 and §9, and appended third-pass evidence.",
  "workspace": {
    "base_requested": "07dfd03a",
    "base_mode": "exact",
    "head_start": "07dfd03aee1b8550a9651465f86f011308fad40b",
    "head_end": "07dfd03aee1b8550a9651465f86f011308fad40b",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-stage3-ruling"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness > /private/tmp/d176-f3-docs-freshness-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Installed the exact F3 ruling and exhaustive caller modes, added the stale-boot counterfactual, and resolved the report’s historical blocker. All 31 tests passed; report header is 1,496 bytes. No commit made.

Next step: lead review and contract refutation/landing gate.