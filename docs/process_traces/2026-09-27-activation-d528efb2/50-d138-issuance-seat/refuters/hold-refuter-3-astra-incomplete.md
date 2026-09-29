```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Refutation incomplete: source inspection identified candidates, but no bypass was executed and required execution coverage was not completed.",
  "workspace": {
    "base_requested": "b953f4b0",
    "base_mode": "exact",
    "head_start": "b953f4b0119f0e05bf02cb9ac206eaf4498b08e3",
    "head_end": null,
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "hold": "OPEN",
    "open_route_count": 0,
    "assessment": "Unresolved; zero demonstrated routes does not establish closure.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Required execution coverage remains incomplete",
        "detail": "No route probes or test suites were executed. This report cannot satisfy ruling section 7 step 7."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "pwd && git status --short --branch && git rev-parse HEAD && rg --files -g 'AGENTS.md' -g 'RUN_STATE.md' -g 'TASK_QUEUE.md' -g 'AGENT_PLAN.md' -g '*bridge_protocol*' -g '*agent_playbook*' -g '*orchestration*'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/contracts/bridge_protocol.md",
          "docs/specs/c027/doc-008_orchestration_inserts.md",
          "AGENT_PLAN.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AGENT_PLAN\\.md\\s*$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The user requested immediate reporting before execution probes were completed. OPEN means unresolved here, not a demonstrated bypass. No approval or completed hold-refutation gate is asserted.",
      "needs": "Complete the execution charge before treating the hold-refutation gate as satisfied."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The checkout was clean at intake. A final HEAD and status check was not performed.",
      "needs": ""
    }
  ]
}
```

HOLD: OPEN — 0 route(s)

**The refutation is unfinished.** Zero routes were demonstrated; this is neither a finding that the hold is closed nor an approval. Reporting stopped at your instruction, before executable probes were completed.

I read the governing ruling, its D-079 addendum, and all three previous refutations. No repository or scratch files were written. No git writes, captures, powermetrics, battery reads, sudo, system-setting changes, or Claude calls occurred.

| Candidate path | Gate or unresolved boundary | File:line | Executed evidence |
|---|---|---|---|
| Held path → loader → authenticator | G1 checks the authenticated artifact’s build and returns `None` when held | `joulewise/calibration_bracketing.py:1224`, `:1288` | Source inspected; behavior not executed |
| Held identifier → operative numbers | Public operatives function checks the identifier’s build before returning numbers | `joulewise/calibration_bracketing.py:650` | Source inspected; behavior not executed |
| Direct call to unchecked authenticator or operative helper | Helpers remain callable; census restricts production references. Whether this constitutes a §6.1 route was not resolved | `joulewise/calibration_bracketing.py:604`, `:1238` | Source inspected; no probe |
| Explicit held content → allowance or bracket | Explicit acceptance is reauthenticated; S1 additionally checks the observed build | `joulewise/calibration_bracketing.py:1387`, `:2148`, `:2325` | Source inspected; behavior not executed |
| R7 continuation into 25G83 | G2 refuses a held continued build | `joulewise/calibration_epoch_continuation.py:213` | Source inspected; behavior not executed |
| Mixed identifiers → admission → arm evidence | Single-identifier admission and guarded authenticator are the intended barriers | `joulewise/arm_readiness.py:_issued_d079`; `joulewise/arm_readiness_evidence.py:341` | Census and route-test source inspected; earlier bypass not replayed |
| Claim-eligible go receipt → live consumption | S2 checks the machine build when `require_current_boot` is true; historical replay intentionally omits that check | `joulewise/arm_readiness.py:10127`, `:10221` | Source inspected; full launch coverage not executed |
| Manual campaign through `main()` | S3 checks claim-bearing policy before calling the runner | `scripts/run_campaign.py:8990` | Source inspected; behavior not executed |
| Direct call to `run_campaign(args)` → child | **Unresolved candidate:** S3 is outside the runner. Marker-free preflight returns without launch authentication; subsequent environment checks remain to be evaluated | `scripts/run_campaign.py:1866`, `:8043`, `:8738` | Runner source inspected; no child or launch-boundary probe |
| Ordinary held-build capture, derivation endpoint exclusion, and every C-5 reader | Required remaining coverage | `tests/test_claim_hold_census.py`; `tests/test_claim_hold_routes.py` | Test definitions inspected; required execution not performed |

## Findings

**F1 — BLOCKER: required execution coverage remains incomplete.**

This report does not meet HOLD-BY-CONSTRUCTION-01 §7 step 7. In particular, it does not establish by execution that every loader/authenticator caller and C-5 reader refuses forbidden use, that ordinary held-build captures cannot enter the ledger, that derivation rows cannot become endpoints, or that every claim launch crosses S2/S3.

The next exact step is to finish the read-only probes, starting with the direct `run_campaign(args)` candidate. No production fix is proposed: that candidate has not been demonstrated to satisfy §6.1.

**SHOULD-FIX:** None established.  
**NIT:** None established.

## Residual risk

The new unchecked helpers and the runner entry point warrant examination, but neither was executed as a bypass. Existing route tests are not evidence of this seat’s execution. The full suite was not run.