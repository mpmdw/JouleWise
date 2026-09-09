```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Pinned the B4 production-entry class refusal; returning NEEDS_RULING on post-night G7 receipt and custody semantics.",
  "workspace": {
    "base_requested": "int/2026-09-08-d176-seats-2-3 at 4d72e524",
    "base_mode": "exact",
    "head_start": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "head_end": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-seat4-rehearsal"
  },
  "pathspec": [
    "tests/test_launch_window.py",
    "docs/contracts/pack_night_go_receipt.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 212 tests in 440.784s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 212 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
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
      "text": "NEEDS_RULING: synthesis item 8 requires presenting the rehearsal GO after a consuming night. Contract section 6 instead presents a separate six-key rehearsal-class receipt and requires custody-wide absence of consumption and chain.started. The completed rehearsal custody cannot satisfy those absence predicates.",
      "needs": "Specify the presented schema, production-plan/ARM inputs, absence-check custody, artifact custody, and how G7 evidence enters the rehearsal bundle; resume seat 4."
    }
  ]
}
```

## Change

- **B4:** Added a valid rehearsal-receipt regression through the production CLI and direct consumer. It checks exact class refusal, digest authentication before class checking, and custody-wide consumption/capture absence.
- **§7.1 / §9:** Recorded the partial implementation and ruling request.
- **G5, G7 producer/acceptance, additional S1/S4/N1 work:** Unimplemented in this early return. Runtime files untouched; no commit.

## Verification notes

Named acceptance and diff check were rc-gated to [the log](/private/tmp/d176-seat4-acceptance.log). Evidence is fixture-based, not live qualification.

## Residual risk

**NEEDS_RULING:** Should G7 present §6’s six-key rehearsal receipt in separate production-plan custody, or present the actual consumed pack GO with amended refusal semantics?

Recommend the separate production-plan control. Please specify its plan/ARM inputs, which custody owns `night/g7_refusal.json`, and how that artifact enters the rehearsal bundle. Preserve the completed rehearsal’s consumption and capture records.