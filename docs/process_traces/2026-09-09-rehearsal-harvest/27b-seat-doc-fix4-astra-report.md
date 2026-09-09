```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied F1–F4 as four literal replacements; preserved all other bytes and made no commit.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
    "head_end": "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
    "upstream_end": null,
    "branch": "bookkeeping/2026-09-09-doc-fix4"
  },
  "pathspec": [
    "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md",
    "docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --stat; git status --short; git rev-parse HEAD; git cat-file -t 5db38b58",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "70d71f778d8b5f29ea7c58b4bf1355ab8db2dbd6",
          "commit"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "commit$"}
    }
  ],
  "flags": []
}
```

## Change

- **F1:** Marked copy ordering **INFERRED**. Verified `pre-uninstall-observations.txt`: `"epoch_s": 1788950204.064847`; `uninstall-output.txt`: `== uninstall run at 1788950218`. Decimal subtraction gives exactly **13.935153 seconds**, dating the watchdog sample. `removal-output.txt` records `== removal at 1788950258` and `plan root removed rc=0`. Recomputed all 17 manifest hashes successfully.
- **F2:** Recomputed the first-two-line digest, matching `night-result.json`: `"sha256": "f894b3a4d731e3a794795251fb596b442cb498964ea468c307346f0bee5bae13"`. Quoted all four subsequent `night.log` lines:
  ```text
  2026-09-09T02:56:03.367167-07:00 night result verdict=REHEARSAL_ONLY
  2026-09-09T02:56:10.980604-07:00 durable record pushed branch=night-results/20260909
  2026-09-09T02:57:33.117809-07:00 courier attempt=1 heartbeat=True sent=True
  2026-09-09T02:57:35.070205-07:00 durable record pushed branch=night-results/20260909
  ```
- **F3:** Qualified the cure as “Once … lands.” At `5db38b58`, `if plan.receipt_class == "REHEARSAL_STUB":` records `"chain_sha256": None`; chain reads occur under `else:`. At `83ab38ed`, the unconditional reads are `chain_text = probes.read_text(plan.chain_path)` and `sidecar_text = probes.read_text(plan.chain_sha256_path)`. The separate magistrate artifact `24-brief-kernel-fold-part2-astra.md:20` names “the cure PR #309,” corroborating the number.
- **F4:** Removed process-type attribution. Verified heartbeat line `pid=82210` and sent-marker line `courier_pid=82210`.

## Verification notes

Used artifact hashes, exact decimal arithmetic, pinned source inspection, and diff review for these documentation-only edits; no test suite or live measurement ran. The initial search included a trace directory absent from this worktree; the subsequent read used its existing magistrate-worktree location.

Next step: lead review of the two-file diff.