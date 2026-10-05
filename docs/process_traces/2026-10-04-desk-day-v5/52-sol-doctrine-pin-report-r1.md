```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: the registry has no retirement mechanism; no files changed.",
  "workspace": {
    "base_requested": "784d12f1b996865c8cf4053bb70101804346ceae",
    "base_mode": "exact",
    "head_start": "784d12f1b996865c8cf4053bb70101804346ceae",
    "head_end": "784d12f1b996865c8cf4053bb70101804346ceae",
    "upstream_end": "784d12f1b996865c8cf4053bb70101804346ceae",
    "branch": "fix/2026-10-04-doctrine-pin-network-time-off"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## fix/2026-10-04-doctrine-pin-network-time-off...origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## fix/2026-10-04-doctrine-pin-network-time-off\\.\\.\\.origin/main$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-docpin/pc tests/test_arm_readiness*.py tests/test_receipt_histsem.py",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "passed"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: registry v2 has exact-key row definitions without retirement/status fields, requires exactly 35 rows, and requires every profile to select every row. RETIRED status is rejected with readiness_unknown_key. No existing retired/superseded state or cold-gate retirement procedure was found.",
      "needs": "Rule whether retirement should prospectively replace the live v2 restore row while preserving archival v1, or introduce an explicit retirement/supersession schema. Recommendation: replace the live row with a current network-time doctrine row and preserve archival registries and historical predicate verification."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Requested suites and main failure comparison were not run because work stopped at the registry-contract ruling. HEAD, main and origin/main are identical.",
      "needs": "Resume after the retirement representation is ruled, then run the requested suites and baseline comparison."
    }
  ]
}
```

## Change

No changes or commit.

The missing mechanism is concrete: [row definitions](/Users/edr/code/JouleWise-wt-dd5-docpin/joulewise/arm_readiness.py:442) admit no retirement field; [registry validation](/Users/edr/code/JouleWise-wt-dd5-docpin/joulewise/arm_readiness.py:2239) requires 35 rows and every profile to select the complete set. Adding `status: RETIRED` experimentally refuses `readiness_unknown_key`.

**NEEDS_RULING:** choose prospective replacement of the live v2 row, retaining archival v1 and historical predicates, or a new explicit retirement schema. I recommend replacement. The coordinated implementation is blocked on that representation, under the delegated-session rule against inventing contract semantics.

## Verification notes

The archived clone arm receipt contains **zero `CLOCK_PROBE` evidence items**; `clock.network_time_off` has empty `evidence_ids`. Its predicate requires only `fresh_probe: true` and `network_time: off`, with no restore dependency. That refusal is consistent with missing live evidence.

The requested suites were not run; historical verification remains untested in this seat.