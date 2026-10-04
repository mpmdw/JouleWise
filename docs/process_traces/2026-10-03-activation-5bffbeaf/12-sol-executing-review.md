```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: config provenance checks pass, but null permits standalone selection and prompt-pin issuance from an incomplete ladder.",
  "workspace": {
    "base_requested": "e256ac28",
    "base_mode": "exact",
    "head_start": "9644edb00a21d646f63e29aecc5cc8e02867e041",
    "head_end": "9644edb00a21d646f63e29aecc5cc8e02867e041",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "classification": "MAJOR",
        "file": "scripts/summarize_g2a_prefill_probe.py",
        "line": 557,
        "summary": "Changing the empty-rung minimum from 0 to null changes a malformed-summary refusal into standalone selection; the prompt issuer can then issue a pin despite incomplete small-model rungs.",
        "related_locations": [
          "scripts/select_g2a_prefill_length.py:69",
          "scripts/issue_g2a_prefill_prompt_pin.py:168",
          "scripts/harvest_g2a_window.py:235"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_harvest_g2a_window tests.test_select_g2a_prefill_length",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 87 tests in 28.437s",
          "",
          "OK",
          "PASS built G2-a prompt ladder, configs, and manifests",
          "PASS bound G2-a inputs to the calibration window"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 87 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/g2a-w2-review-5bffbeaf/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "pin tamper refusals 15 /15",
          "PROBES PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "pin tamper refusals 15 /15\\nPROBES PASS"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/g2a-w2-review-5bffbeaf/field_sweep.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "NON_NULL RUN CONFIG FIELD SWEEP 32 / 32 REFUSED with metadata rebound",
          "NON_NULL INPUT CONFIG FIELD SWEEP 32 / 32 REFUSED with inventory pin unchanged",
          "FIELD SWEEP PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "32 / 32 REFUSED[\\s\\S]*FIELD SWEEP PASS"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/g2a-w2-review-5bffbeaf/empty.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "HEAD SELECTOR selected 512",
          "HEAD PIN summary+selection accepts 512",
          "HEAD FULL PIN incomplete-ladder exit 0 pin_exists True",
          "PARENT HARVEST RECOVER ['rung_valid_small_members_shortfall']",
          "HEAD HARVEST RECOVER ['rung_valid_small_members_shortfall']",
          "EMPTY PROBE PASS; direct selector/pin selection changes, harvest stays RECOVER"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HEAD SELECTOR REFUSED"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/g2a-w2-review-5bffbeaf/real_and_parent.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "REAL summarizer exit 0",
          "BOUND g2a-small-p0512-r01 3ed5607928833a184f00d4d5be16f28d7a82b819a6564a2e1948a114b36c8f49",
          "BOUND g2a-small-p0512-r02 44c3ecd7a52520ab99091fe2b386e0b4fed26e3a2136ef83ec7619c8244c80a5",
          "BOUND g2a-small-p0512-r03 f93f0473ba734bda7e1d965a82e87747381e3ada81d4811dc12e6db364b4cdb7",
          "BOUND g2a-small-p0512-r04 9e5537e4acb192ad45272125ba0fa40a3e24fe50bb860cb47fda47d034e05e53",
          "BOUND g2a-small-p0512-r05 e594bdb4f77e5847f0aa42cf981329f8a79d1d8eda5cdaec47d0c3afa83bd3e7",
          "BOUND g2a-small-p1024-r01 cc00f9ed661cb5a0005b41ae5d85f2e6b2b4dfc02d1d980cc4ab6a5bb5c4823c",
          "BOUND g2a-small-p1024-r02 3a19781ff4cd3f615227fe79643649a68cd01e64a9efd661656b773a5099b7e3",
          "BOUND g2a-small-p1024-r03 d80fe5f8c10238ca6ee46381fcee6216307cba40a843f93cbe8ef591e23cc0a8",
          "BOUND g2a-small-p1024-r04 bd8f47c8783e7fc48e1e453db324c4b2b980ee7673dbfd646ab6f5e1b2bbb686",
          "BOUND g2a-small-p1024-r05 61a692182449213ea63027c63271b6571c08fdbb5fbcc1b90dac681dadeaf3c4",
          "BOUND g2a-small-p2048-r01 cc60d8ab7aa031698a7fd9795262a999fe8fe0aad245d7accbc0b8d8af8e1238",
          "BOUND g2a-small-p2048-r02 779cf03b5b00c90badabab979e5060371fccce69c19800ff3da7d75937e80e6f",
          "REAL 12/12 input pins + normalized run bytes + metadata + receipt BOUND; no overlap counts disclosed",
          "PARENT extracted e256ac28; overlaid only three changed regression-test files from 9644edb0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REAL 12/12 input pins \\+ normalized run bytes \\+ metadata \\+ receipt BOUND"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/g2a-w2-review-5bffbeaf/parent python3 -B /tmp/g2a-w2-review-5bffbeaf/run_parent_tests.py",
      "cwd": "/tmp/g2a-w2-review-5bffbeaf/parent",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 6 tests in 1.167s",
          "",
          "FAILED (failures=3, errors=1)",
          "PARENT e256ac280d1d3b7461cfb6fa400fa76296d357bb production code unchanged; only regression test overlay; git rev-parse HEAD mocked for archive fixture"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=3, errors=1\\)"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1 --untracked-files=all\ngit rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9644edb00a21d646f63e29aecc5cc8e02867e041"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^9644edb00a21d646f63e29aecc5cc8e02867e041$"
      }
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The parent counterfactual used a git-archive extraction, overlaid regression tests, and a mock of the fixture's git rev-parse HEAD call. Production code remained the parent version.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — MAJOR — [scripts/summarize_g2a_prefill_probe.py:557](/Users/edr/code/JouleWise-wt-5bffbeaf-review/scripts/summarize_g2a_prefill_probe.py:557): null can turn a direct refusal into selection and pin issuance.**

Executed probe:

```sh
TMPDIR=/tmp/g2a-w2-review-5bffbeaf/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/g2a-w2-review-5bffbeaf/empty.py
```

With synthetic qualifying p512/p1024 rungs and all large members present:

| Consumer | Parent | Current |
|---|---|---|
| p2048: 2 valid small members | minimum `0`, flag `false` | unchanged |
| p4096: 0 valid small members | minimum `0`, flag `false` | minimum `null`, flag `false` |
| Standalone selector | `summary_internally_contradictory` | `selected 512` |
| Prompt pin | summary refused | `exit 0`, pin created |
| Harvest | `RECOVER` | `RECOVER` |

The empty rung never qualifies. However, correcting its schema permits another qualifying rung to select, and the issuer accepts that incomplete ladder. Registration §8 admits analysis inputs only from a `SELECT` window. The harvester enforces this correctly at [harvest_g2a_window.py:235](/Users/edr/code/JouleWise-wt-5bffbeaf-review/scripts/harvest_g2a_window.py:235); direct issuance lacks that completion gate. Require authenticated `SELECT` provenance or enforce the complete small-member roster before issuing a pin, and add this mixed-ladder regression.

The provenance fix otherwise passed execution:

- Both summarizer and issuer refused all 15 tamper combinations, including normalization of a different input and rebound metadata/receipt hashes. An additional sweep refused changes to all 32 non-null config leaves.
- The real writer, file hash, and `_config_sha256` all produced `a76d172b47cf47b43c8fbbcd109a0238c64051ae37a0ffe536613eb44fb85d27`. The file ends with `\n`; removing it changes the hash.
- All 12 valid w2 members bound successfully, as shown in V5.
- The requested suite passed **87 tests**. The parent counterfactual failed as expected: **6 tests, 3 failures, 1 error**. The error was the parent rejecting normalized config bytes; two failures were metadata subtests.
- Repository status remained clean and HEAD unchanged. All review writes stayed in the authorized scratch directory.

## Residual risk

The real-data probe verified summarizer provenance using the refused harvest’s valid-member roster; it did not repeat strict raw-evidence validation or perform a complete real harvest. Harvest verdict probes used fixtures. Real overlap counts were not disclosed.