```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Closed CWI-01 and Opus F-1/F-3 with exact charter composition, a placement-dependent real-shaped DX regression, and one projection-freeze grammar owner.",
  "workspace": {
    "base_requested": "fc8994c939585569068842c45419735c3c1833df",
    "base_mode": "exact",
    "head_start": "fc8994c939585569068842c45419735c3c1833df",
    "head_end": "fc8994c939585569068842c45419735c3c1833df",
    "upstream_end": "fc8994c939585569068842c45419735c3c1833df",
    "branch": "int/2026-09-04-fan-wave-1"
  },
  "pathspec": [
    "docs/paper/round7/fill-checklist.md",
    "docs/process/coldgate_charter_registry.md",
    "docs/process/coldgate_charter_v3_candidate.md",
    "docs/process_traces/2026-09-04-fanout/wave-1/03-sol-fix-round-1-report.md",
    "joulewise/arm_readiness.py",
    "joulewise/identity_pins.py",
    "tests/test_coldgate_charter_v3.py",
    "tests/test_paper_round7_artifacts.py",
    "tests/test_receipt_histsem.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/wave-1/01-refuter-contract-integrated.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_coldgate_charter_v3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.001s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in [0-9.]+s[\\s\\S]*OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_receipt_histsem",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 68 tests in 2024.237s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 68 tests in [0-9.]+s[\\s\\S]*OK \\(skipped=1\\)$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 49 tests in 611.742s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 49 tests in [0-9.]+s[\\s\\S]*OK$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/process/coldgate_charter_v3_candidate.md docs/process/coldgate_charter.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "473ada40f7e2725d78f80e1e7ac18489456f1442ff6091c123173737546a3228  docs/process/coldgate_charter_v3_candidate.md",
          "099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "473ada40f7e2725d78f80e1e7ac18489456f1442ff6091c123173737546a3228  docs/process/coldgate_charter_v3_candidate.md\\n099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md$"
      }
    },
    {
      "id": "V5",
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

| Finding | Cure | Evidence |
|---|---|---|
| CWI-01 | Folded registry convening clauses 1–2 verbatim into the non-operative candidate beside the existing D-170 clause; recomputed the candidate digest while leaving v2 untouched; replaced the one-amendment invariant with byte-exact three-amendment composition and retained negative mutants. | `docs/process/coldgate_charter_v3_candidate.md:14`, `docs/process/coldgate_charter_v3_candidate.md:62`, `docs/process/coldgate_charter_registry.md:21`, `tests/test_coldgate_charter_v3.py:41`, `tests/test_coldgate_charter_v3.py:113` |
| F-1 | Made the checklist claim placement-dependent and stated the exact standing sentence. The prose tests now combine that checklist sentence, prose copied from the real skeleton diagnostic section, and a 16-marker prose-shaped layout; inside/outside/marked counterfactuals remain. | `docs/paper/round7/fill-checklist.md:36`, `tests/test_paper_round7_artifacts.py:803`, `tests/test_paper_round7_artifacts.py:813`, `tests/test_paper_round7_artifacts.py:853` |
| F-3 | Moved the projection-freeze grammar to `identity_pins`, routed both committed-history and ARM pre-authoring checks through its matcher, and added a mutation test proving a changed owner literal reaches both consumers. | `joulewise/identity_pins.py:39`, `joulewise/identity_pins.py:58`, `joulewise/identity_pins.py:1009`, `joulewise/arm_readiness.py:39`, `joulewise/arm_readiness.py:3021`, `tests/test_receipt_histsem.py:2152` |

## Verification notes

The first whole R7F run exposed two defects in the new realistic fixture (four sentence-final periods entered literal parsing, and the period also prevented the longest DX-023 rendering from owning its embedded `15`); it ended `FAILED (failures=2)`. The fixture punctuation was corrected without changing the scanner, direct checks passed, and V3 is the clean whole-module rerun. Per the explicit preflight rule, no repository-wide suite was run.
