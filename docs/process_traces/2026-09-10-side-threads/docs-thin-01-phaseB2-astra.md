```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Created the archive guide and repaired six live path references; historical records remain unchanged.",
  "workspace": {
    "base_requested": "f6aed467",
    "base_mode": "exact",
    "head_start": "f6aed46724e09166b33d79c558b6d73877abb50e",
    "head_end": "f6aed46724e09166b33d79c558b6d73877abb50e",
    "upstream_end": "0c2c78d1a80d215191df8b7d334306ccface34c8",
    "branch": "chore/2026-09-10-docs-thin"
  },
  "pathspec": [
    "docs/legacy/README.md",
    "README.md",
    "docs/contracts/bridge_protocol.md",
    "docs/phase_2/window_runbook.md",
    "docs/phase_2/alpha_arm_readiness.md"
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
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_gen_state tests.test_pack_capsule tests.test_build_site_parsers tests.test_claims_lint tests.test_floor_extraction tests.test_render_results_fills tests.test_results_prose_template tests.test_rpt002_related_work tests.test_d117_decode_contrast_plan -q",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 427 tests in 71.293s", "", "OK (skipped=74)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=74\\)"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 \"$TMPDIR/docs-thin-b2/link_audit.py\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "UNRESOLVED docs/phase_3/borrow_runbook.md",
          "UNRESOLVED docs/stop_cards/",
          "UNRESOLVED runs/example-mock-local",
          "UNRESOLVED scripts/check-bridge-docs.mjs"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "UNRESOLVED UNIQUE 0"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M README.md",
          " M docs/contracts/bridge_protocol.md",
          " M docs/phase_2/alpha_arm_readiness.md",
          " M docs/phase_2/window_runbook.md",
          "?? docs/legacy/README.md"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "\\?\\? docs/legacy/README\\.md"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The authoritative rename list and filesystem contain 309 moved files, not the prompt's stated 376. All 309 destinations and file bytes were verified.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The link audit found 16 distinct absent paths unrelated to this archival move, including examples and runtime paths. Eighteen old-location references resolve through the documented archive mapping.",
      "needs": "Review the reported pre-existing references separately."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during the session from 1d4045b4 to 0c2c78d1. Worktree HEAD stayed unchanged; the saved rename list exactly matches HEAD^...HEAD.",
      "needs": "Lead should reconcile the current upstream during integration."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The retained readiness-charter trace has a historical citation, but the requested search did not establish an active consumer. The critique HTML consumer constructs its path from components. Both qualifications are documented.",
      "needs": ""
    }
  ]
}
```

## Change

The archive guide contains all six requested sections, measured inventory, 41 trace-directory names, and verified retained-path consumers.

Measured moves:

| Group | Files | Bytes |
|---|---:|---:|
| Trace directories | 240 | 55,109,940 |
| Standalone trace files | 5 | 55,569 |
| Strategy records | 52 | 27,777,245 |
| Other records | 12 | 179,021 |
| **Total** | **309** | **83,121,775** |

Every archived file matches its original bytes and the mechanical destination rule.

Path edits:

- `README.md`: `docs/process_traces/2026-07-17-exploratory-block/results.md` → `docs/legacy/process_traces/2026-07-17-exploratory-block/results.md`
- `docs/contracts/bridge_protocol.md`: `docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md` → `docs/legacy/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md` — three occurrences.
- `docs/phase_2/window_runbook.md`: `docs/process_traces/2026-08-08-d127-autonomous-loop/CONSULT-RESPONSE.md` → `docs/legacy/process_traces/2026-08-08-d127-autonomous-loop/CONSULT-RESPONSE.md`
- `docs/phase_2/alpha_arm_readiness.md`: `docs/process_traces/2026-08-13-freeze-execution/dryrun-alpha.json` → `docs/legacy/process_traces/2026-08-13-freeze-execution/dryrun-alpha.json`

`CLAIMS_STATUS.md` remains unchanged: its references to `docs/process_traces/2026-08-06-d110-remint-fork/` and `docs/process_traces/2026-08-03-winB-reeval-stop/` occur in retained historical entries.

No moved targets were found in `docs/orchestration.md`, `docs/phase_3/phase_3_exit_checklist.md`, or `docs/specs/suite_next/next_observer_spec.md`; those files remain unchanged.

## Verification notes

Full outputs and the per-reference audit are saved under [`$TMPDIR/docs-thin-b2/`](/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/docs-thin-b2): `gen-state.log`, `unittest.log`, `link-audit.log`, and `git-status.log`.

The literal-path audit found these 16 distinct absent paths:

- `.codex-bridge/baselines/inv-123.json`
- `.codex-bridge/bridge.lock`
- `.codex-bridge/invocation_manifest.jsonl`
- `.codex-bridge/receipts/`
- `.codex-bridge/session.lock`
- `.codex-bridge/workspace-lease-events.jsonl`
- `.venv/bin/python`
- `.venv/bin/python3`
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4`
- `configs/campaigns/d117_floor_qwen25_1p5b_v4`
- `configs/campaigns/d117_floor_qwen25_7b_v4`
- `docs/artifacts`
- `docs/phase_3/borrow_runbook.md`
- `docs/stop_cards/`
- `runs/example-mock-local`
- `scripts/check-bridge-docs.mjs`

These include runtime/example locations, older campaign references, and the prose phrase `docs/artifacts`. None is a target moved by the archival commit, so none was changed.

The audit separately records 16 old-address occurrences in the archive guide and the two preserved historical references in `CLAIMS_STATUS.md`; every corresponding archive destination exists.

**PROPOSALS:** No out-of-scope changes are required for this task. Assess the pre-existing missing document/script references in a separate follow-up. Parent-owned bookkeeping and commit remain untouched.

**CHECKS PERFORMED:** Requested state check and unittest group; nine-document path audit; 309-file byte/destination verification; inventory totals; literal-consumer searches; exact path-only substitution checks; whitespace and write-scope checks.

## Residual risk

`origin/main` advanced during this session. The next step is lead review and integration against the updated upstream, followed by the parent-owned commit.