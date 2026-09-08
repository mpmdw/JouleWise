```json
{
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [
      {
        "id": "N1",
        "severity": "blocker",
        "disposition": "CURED",
        "location": "joulewise/campaign_provenance.py:298",
        "text": "Surrogate-origin ambiguity is represented as a linear tuple of local choices, and exact least-successor search no longer materializes the 2^n Cartesian product. The round-1 20-pair reproducer completed in 0.000092 seconds at this head, while semantic property checks agreed with exhaustive enumeration."
      }
    ],
    "same_signature": "NO — N1's exponential Cartesian-product allocation and stall signature does not survive: the exact 20-pair input now has 20 segments and 40 local choices and completed in 0.000092 seconds; no NOT CURED, REGRESSED, or NEW finding remains."
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round-1 N1 is cured with compact exact ordering, no regression or new defect was found, and fix round 2 is landable.",
  "workspace": {
    "base_requested": "f68fb45bbd3e577aaf7cf5a8ba9f06fb848cd421",
    "base_mode": "exact",
    "head_start": "f68fb45bbd3e577aaf7cf5a8ba9f06fb848cd421",
    "head_end": "f68fb45bbd3e577aaf7cf5a8ba9f06fb848cd421",
    "upstream_end": "f68fb45bbd3e577aaf7cf5a8ba9f06fb848cd421",
    "branch": "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/06-delta-reaudit-round-2.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "f68fb45bbd3e577aaf7cf5a8ba9f06fb848cd421",
          "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01",
          "## feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01...origin/feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "f68fb45bbd3e577aaf7cf5a8ba9f06fb848cd421\\nfeat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01\\n## feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01\\.\\.\\.origin/feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 275 tests in 213.269s",
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
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c 'import json,resource,time; from joulewise.campaign_provenance import parse_campaign_log_bytes as p; n=20; w=json.dumps({\"\\U00010000\"*n:0},sort_keys=True).encode(\"ascii\"); raw=w[:w.index(b\":\")+1]; t=time.perf_counter(); assert p(raw)==([],\"torn_prefix\"); print(f\"valid_prefix pairs={n} bytes={len(raw)} seconds={time.perf_counter()-t:.6f} maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "valid_prefix pairs=20 bytes=244 seconds=0.000092 maxrss=24838144"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "valid_prefix pairs=20 bytes=244 seconds=[0-9.]+ maxrss=[0-9]+"
      }
    }
  ],
  "flags": []
}
```

## Findings

### N1 — blocker — CURED

The round-1 availability defect does not survive. `_WriterStringPattern`
stores each ambiguous escaped high/low surrogate pair as one two-choice
segment. `_least_writer_string_above` follows the unique equality path and
remembers the latest greater branch, so it returns the least represented
origin above the predecessor without expanding all origins. Carrying that
least feasible predecessor across keys is exact: any larger predecessor can
only reduce the next key's feasible greater-than set.

Executed evidence covered the round-1 20-pair, 244-byte reproducer, the full
275-test touched module, 397,900 exhaustive helper comparisons, 69,975
multi-key chain steps, and 12,277 raw-token decoder comparisons. All passed.
The reproducer fell from round 1's 1.937989 seconds and 416,743,424-byte
process high-water mark to 0.000092 seconds and 24,838,144 bytes.

No NOT CURED or REGRESSED finding remains, and no NEW defect was found.

Same-signature statement: **NO** — there is no surviving finding with N1's
exponential surrogate-alternative materialization/stall signature. The
magistrate does not need to route a same-signature survivor to consult.

## Residual risk

The exhaustive property checks bound ambiguity depth and use host-dependent
timing/RSS observations. The structural 20-segment/40-choice assertion and
the linear representation remove dependence on timing for the cure itself.
Per the preflight rule, only the test module touched by fix round 2 ran.
