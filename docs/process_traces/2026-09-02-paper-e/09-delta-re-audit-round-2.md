# Delta re-audit of fix round 2 at 73d0a68a (terra xhigh, direct run), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "All charged fixes re-audit clean at required HEAD 73d0a68a; zero findings; LANDABLE.",
  "workspace": {
    "base_requested": "8731cb4c3bd3d2d92d38ef2d63675f953cc3ed53",
    "base_mode": "exact",
    "head_start": "73d0a68acffa8612cab4adb082b1648de85a0d0d",
    "head_end": "73d0a68acffa8612cab4adb082b1648de85a0d0d",
    "upstream_end": "73d0a68acffa8612cab4adb082b1648de85a0d0d",
    "branch": "feat/2026-09-02-paper-e"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "LANDABLE",
    "findings": [],
    "finding_count": 0
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git diff --check 8731cb4c -- docs/paper/draft-v2-skeleton.md docs/paper/figures/fig5_phase_record_overlap.svg docs/paper/figures-plan.md docs/paper/figures/README.md docs/paper/results-fill-registry.md docs/paper/round7/fill-checklist.md docs/paper/round7/survival-map.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "73d0a68acffa8612cab4adb082b1648de85a0d0d",
          "diff --check: no output"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "73d0a68a[0-9a-f]{32}"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "grep -cE '^\\| (DS|PG|DG)-[0-9]+[a-z]? — .*[[]PENDING' docs/paper/results-fill-registry.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["32"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^32$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["......", "Ran 6 tests in 2.041s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".........", "Ran 45 tests in 634.082s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests in [0-9.]+s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Files 02/03 record head 0857bd59 and file 06 records b5fd4ba2, not the required current head. Their findings were independently re-audited at 73d0a68a rather than inherited.",
      "needs": ""
    }
  ]
}
```

## Findings

| Prior finding | Result | Current evidence |
|---|---|---|
| B-1 blocker | Closed | Registry lines 937–954 state 32 pending / 35 complete-family; its exact printed census command returns `32`. |
| S-1 | Closed | Draft 947–955 and 974–986 use containment plus alignment, say the phase is barely longer than the median-width record, and do not claim typical records are wider or print issued-value arithmetic. |
| S-2 | Closed | Survival map 275–278 names the issued artifact, correct SHA-256, and requires pinned-statistic rendering. |
| S-3; N-1; N-2 | Closed | Draft 964–972 restores “unique,” states the `0.000001 s` tolerance and issued gap evidence; line 974 replaces “close to” with the ruled relationship. |
| N-4 | Closed | Checklist 286–289 guards `37 + 13 = 50`; registry lines 643–652 independently supply DG-068=50, DG-069=13, DG-076=37, DG-077=13. |

SVG coordinate audit: upper phase `[310,505]` (195 px) crosses only boundary 340 among 190 px records, yielding 2 positive overlaps. Lower phase `[330,525]` contains middle record `[350,500]` (150 px), yielding 3. All 23 data marks have accessible titles; all 13 required visible label assertions passed.

Mechanical reader-order first-use crosswalk passed all 39 changed sentence/fragment units (D1–D16, P1–P3, R1–R5, G1–G4, C1–C3, U1, S1–S7), and the six-test ledger/terms suite passed.

## Residual risk

The historical reports do not share this head signature; their conclusions were not reused as same-head verification. The requested current-head checks are clean.