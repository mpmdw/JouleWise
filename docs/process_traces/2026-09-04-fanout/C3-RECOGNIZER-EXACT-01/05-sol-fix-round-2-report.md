```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 2 cures N1 by replacing exponential surrogate-origin materialization with a linear compact pattern and exact greedy successor search.",
  "workspace": {
    "base_requested": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "base_mode": "exact",
    "head_start": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "head_end": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "upstream_end": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "branch": "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
  },
  "pathspec": [
    "docs/contracts/campaign_log_tail_recognizer.md",
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/05-sol-fix-round-2-report.md",
    "joulewise/campaign_provenance.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/04-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 275 tests in 207.720s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 275 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign.CampaignLogTailGrammarTests.test_c3_n1_surrogate_ambiguity_is_compact",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.004s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c 'import json,resource,time; from joulewise.campaign_provenance import parse_campaign_log_bytes as p; n=20; w=json.dumps({\"\\U00010000\"*n:0},sort_keys=True).encode(\"ascii\"); raw=w[:w.index(b\":\")+1]; t=time.perf_counter(); assert p(raw)==([],\"torn_prefix\"); print(f\"valid_prefix pairs={n} bytes={len(raw)} seconds={time.perf_counter()-t:.6f} maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "valid_prefix pairs=20 bytes=244 seconds=0.000089 maxrss=24608768"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "valid_prefix pairs=20 bytes=244 seconds=[0-9.]+ maxrss=[0-9]+"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
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
  "flags": []
}
```

## Change

N1 → cured → `joulewise/campaign_provenance.py:298`: ambiguous high/low
surrogate pairs are now stored as local two-way segments rather than as a
materialized Cartesian product. Exact object-key ordering uses the least
reachable successor at `joulewise/campaign_provenance.py:324` and carries only
that least feasible predecessor at `joulewise/campaign_provenance.py:552`.
This preserves the existential ordering language because a smaller predecessor
cannot reduce the set of later keys that compare greater.

N1 counterfactual → regression → `tests/test_run_campaign.py:656`: the audit's
exact 20-pair, 244-byte prefix and its incomplete-key counterpart both classify
as `torn_prefix`; the representation contains 20 segments and 40 local choices,
not 2^20 strings. The same test walks every boundary of a four-origin chain
whose distinct Python keys all serialize identically, covering successor
selection across the full two-pair ambiguity set.

Contract explanation → `docs/contracts/campaign_log_tail_recognizer.md:23` and
`:68`: records the compact representation, least-feasible-origin invariant,
and linear runtime/storage argument.

## Verification notes

Per the task-specific preflight rule, only the touched test module ran. The V3
`maxrss` value is process high-water memory, not an allocation delta; its
discriminating evidence is the structural 20-segment/40-choice regression,
while the timing demonstrates removal of the audited 1.9-second stall on this
host.
