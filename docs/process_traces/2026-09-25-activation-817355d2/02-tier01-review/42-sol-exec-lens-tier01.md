```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-FIRST: hidden Tier declarations pass the light gate, and the checker lacks the changed-path check requested in issue #415.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "descendant",
    "head_start": "7c9dadc4d591b6aa5d6e8e77acd5a36b74ed7a51",
    "head_end": "7c9dadc4d591b6aa5d6e8e77acd5a36b74ed7a51",
    "upstream_end": "c6814dd891db361156c45434490342a3e1dd9da3",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-FIRST",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "question": "T2",
        "text": "A Tier: light line inside a fenced code block or HTML comment is accepted as the sole declaration, allowing eight N/A rows without a visible tier declaration."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "question": "T3",
        "text": "The workflow supplies no changed paths and the checker never checks them, despite the later explicit request in issue #415."
      },
      {
        "id": "F3",
        "severity": "nit",
        "question": "T4",
        "text": "The adopted rule still calls itself proposed and says Ed will see the result."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 38 tests in 13.348s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 38 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/tier01_review_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fenced_only: exit=0; gate-ledger: 4/4 RUN; 8/8 N/A (light tier)",
          "html_comment_only: exit=0; gate-ledger: 4/4 RUN; 8/8 N/A (light tier)",
          "wrong_head: exit=1; gate-ledger: item 12: sha is not the PR head"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "wrong_head: exit=1; gate-ledger: item 12: sha is not the PR head"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --name-only origin/main...7c9dadc4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".github/pull_request_template.md",
          ".github/workflows/gate-ledger.yml",
          "docs/orchestration.md",
          "docs/process/tier01_defect_log.md",
          "scripts/check_gate_ledger.py",
          "tests/test_check_gate_ledger.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_check_gate_ledger.py"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "gh api repos/mpmdw/JouleWise/branches/main/protection/required_status_checks --jq '.contexts'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "error connecting to api.github.com",
          "check your internet connection or https://githubstatus.com"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "gate-ledger"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor origin/main HEAD; git status --short --branch; git diff --exit-code; git rev-parse HEAD; git rev-parse origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "7c9dadc4d591b6aa5d6e8e77acd5a36b74ed7a51",
          "c6814dd891db361156c45434490342a3e1dd9da3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c6814dd891db361156c45434490342a3e1dd9da3"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The live branch-protection API was unreachable; T4 relies on the recorded 2026-09-24 update.",
      "needs": "Lead may recheck required contexts online."
    }
  ]
}
```

## Findings

**Verdict: FIX-FIRST.** For T1, the six changed files implement §G5’s installation shape: rule and branch-protection text, PR template and six-line impact statement, checker and tests, workflow header, and a tracked 30-day defect log. The log implements §G5’s revert trigger. The checkout does not establish whether this installation PR completed its own full-tier ledger.

**F1 (should_fix, T2).** The checker recognizes any raw line beginning `Tier:`. A body with `Tier: light` only inside a fenced code block or HTML comment passes the light gate. Require the declaration as the first nonblank standalone line, where the template already places it. Preserve duplicate refusal and full fallback when no valid declaration is present. The item-12 final-head SHA rule behaved correctly.

**F2 (should_fix, T3).** Issue #415 postdates §G5 and explicitly asks for checker validation against changed paths. Treat that as a merge condition while retaining the independent reviewer’s semantic check. The workflow should fetch the PR base SHA, compute a NUL-delimited merge-base-to-head path list, and pass it to the checker. For `Tier: light`, a conservative guard can permit `tests/**`, `docs/**` except `docs/paper/**`, `docs/report_src/**`, and `docs/site/**`, plus the root bookkeeping files `RUN_STATE.md`, `TASK_QUEUE.md`, `PROJECT_STATUS.md`, and `AGENT_PLAN.md`. All other paths force full, including `joulewise/**`, `scripts/**`, `configs/campaigns/**`, `configs/model_panels/**`, and README claim files. Missing or unreadable path input must refuse light. The reviewer must still apply all six impact questions to otherwise eligible paths.

**F3 (nit, T4).** The workflow and orchestration statements that `gate-ledger` is required on `main` match the recorded 2026-09-24 branch-protection update. Live settings could not be checked. Replace the stale heading with exactly:

> **Rule TIER-01 (adopted by cold gate COUNCIL-407-01 §G5; effective on merge).**

The later statement that Ed was informed with veto can remain as a historical account.

Executed evidence, from the repository checkout; adversarial bodies were written under `/tmp/tier01_review_bodies/`:

```text
$ git diff --name-only origin/main...7c9dadc4
.github/pull_request_template.md
.github/workflows/gate-ledger.yml
docs/orchestration.md
docs/process/tier01_defect_log.md
scripts/check_gate_ledger.py
tests/test_check_gate_ledger.py

$ PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_check_gate_ledger
......................................
----------------------------------------------------------------------
Ran 38 tests in 13.348s

OK

$ PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/tier01_review_probe.py
valid_light: exit=0; gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
missing_tier_light_rows: exit=1; gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 3: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 4: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 5: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 6: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 7: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 8: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 10: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
malformed_case: exit=1; gate-ledger: Tier must be full or light
malformed_choice: exit=1; gate-ledger: Tier must be full or light
duplicate: exit=1; gate-ledger: duplicate Tier declaration
fenced_only: exit=0; gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
table_only: exit=1; gate-ledger: Tier must be full or light
html_comment_only: exit=0; gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
indented: exit=1; gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 3: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 4: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 5: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 6: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 7: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 8: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 10: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
crlf: exit=0; gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
missing_tier_full_rows: exit=0; gate-ledger: 12/12 RUN
full_na: exit=1; gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 3: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 4: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 5: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 6: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 7: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 8: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 || gate-ledger: item 10: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
light_row_2_run: exit=1; gate-ledger: item 2: light tier requires N/A (light tier)
light_row_1_na: exit=1; gate-ledger: item 1: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
light_row_9_na: exit=1; gate-ledger: item 9: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
light_row_11_na: exit=1; gate-ledger: item 11: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
light_row_12_na: exit=1; gate-ledger: item 12: N/A (light tier) is allowed only in light-tier rows 2-8 and 10
wrong_head: exit=1; gate-ledger: item 12: sha is not the PR head

$ gh api repos/mpmdw/JouleWise/branches/main/protection/required_status_checks --jq '.contexts'
error connecting to api.github.com
check your internet connection or https://githubstatus.com
[exit 1]

$ git merge-base --is-ancestor origin/main HEAD; git status --short --branch; git diff --exit-code; git rev-parse HEAD; git rev-parse origin/main
## HEAD (no branch)
7c9dadc4d591b6aa5d6e8e77acd5a36b74ed7a51
c6814dd891db361156c45434490342a3e1dd9da3
```

## Residual risk

Live GitHub branch protection was unreachable; the committed interactive record says `gate-ledger` became required on 2026-09-24. Full test discovery was intentionally not run. No repository files changed. The report and probe files are under `/tmp`.