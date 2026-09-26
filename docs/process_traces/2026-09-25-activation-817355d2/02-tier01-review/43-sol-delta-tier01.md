```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "FIX-FIRST: F2 and F6 depart from dictated text, the installation date is asserted before verified merge, and two claimed follow-up lanes are absent.",
  "workspace": {
    "base_requested": "7c9dadc4",
    "base_mode": "descendant",
    "head_start": "3fdbbd13e32c23fd4f31529e5724d96efda10c58",
    "head_end": "3fdbbd13e32c23fd4f31529e5724d96efda10c58",
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
        "tier": "MATERIAL",
        "text": "F2 installation text is not byte-exact and asserts a 2026-09-25 merge before that merge was verified; the fixed day-30 date depends on the actual merge date."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "tier": "MATERIAL",
        "text": "The triage claims TIER01-D118-RECONCILE-01 and TIER01-PATH-GUARD-01 carry deferred findings, but neither lane exists elsewhere in the repository."
      },
      {
        "id": "F3",
        "severity": "nit",
        "tier": "NIT",
        "text": "F6 attribution text is paraphrased at all three requested locations rather than installed byte-exactly."
      },
      {
        "id": "F4",
        "severity": "nit",
        "tier": "NIT",
        "text": "The Opus M1 signature remains in D-118: its complete-ledger requirement still conflicts on its face with the light-tier rule; the new D-170 addendum supplies the later rule but does not amend D-118."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 39 tests in 13.285s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 39 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "Temporary-copy mutation script shown below: replace the main() predicate with the pre-fix predicate, redirect the test module's CHECKER to the temporary copy, and run test_indented_light_tier_line_reports_full_twelve_rows",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["FAILED (failures=1)", "MUTATED_TEST_SUCCESS=False"]},
      "expected": {"exit_code": 0, "tail_regex": "FAILED \\(failures=1\\).*MUTATED_TEST_SUCCESS=False"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_check_gate_ledger.CheckGateLedgerTests.test_indented_light_tier_line_reports_full_twelve_rows",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.291s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 7c9dadc4 3fdbbd13",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "gh pr view 419 --json number,state,mergedAt,url,headRefName,baseRefName",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["error connecting to api.github.com", "check your internet connection or https://githubstatus.com"]},
      "expected": {"exit_code": 0, "tail_regex": "\"number\":419"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "GitHub was unreachable, so PR #419's number, state, and merge time could not be independently verified.",
      "needs": "Lead reruns gh pr view 419 before fixing the installation date and day-30 date."
    }
  ]
}
```

## Findings

**Verdict: FIX-FIRST.** The repository was clean at `3fdbbd13`; this session changed no repository files.

**F1 — MATERIAL.** Fable’s F2 dictated, in `docs/orchestration.md`: “Installed at the merge of the installation PR on 2026-09-25 (set the PR number here at merge).” The installed text says: “Installed at the merge of the installation PR #419 on 2026-09-25.” In `docs/process/tier01_defect_log.md`, Fable dictated “and installed at the merge of the installation PR on 2026-09-25”; the installed text says “and installed at the merge of the installation PR #419 on 2026-09-25.” Both are substitutions, not byte-exact installations. Fable also explicitly said both dates move if merge occurs later. The local `origin/main` does not contain `3fdbbd13`; GitHub was unreachable, so the stated merge date and resulting **2026-10-25** day-30 date remain unverified.

**F2 — MATERIAL.** The new triage says “Lane TIER01-D118-RECONCILE-01 carries Opus’s M1” and “Lane TIER01-PATH-GUARD-01 takes Opus’s design.” Executed `rg -n 'TIER01-(D118-RECONCILE|PATH-GUARD)-01' .` found those two lines only, both in `50-triage.md`. No corresponding kernel or queue lane exists. These deferred findings have no tracked owner despite the triage’s claim.

**F3 — NIT.** Fable’s F6 dictated “Made a required status check on main on 2026-09-24 in Ed’s interactive session (record 02a24110 §7).” The workflow’s first header instead says “REQUIRED GATE-LEDGER CHECK on main since 2026-09-24, made required in / Ed’s interactive session”; its later comment splits the dictated phrase across two `#` lines. The orchestration sentence says “a required status check on `main` since 2026-09-24 (made required in Ed’s interactive session, record 02a24110 §7 …).” All convey the attribution, but none installs the dictated bytes.

Fable’s **F1** heading *is* exact on both sides: “**Rule TIER-01 (cold-gated by COUNCIL-407-01 §G5 on 2026-09-24; endorsed by Ed in GitHub issue #415 on 2026-09-25).**” Fable’s **F5** dated D-170 addendum is also exact on both sides, including the `ED-BRANCH-PROTECTION-E1-01` and `ED-D118-NA-TIER-E2-01` sentences.

**F4 — NIT.** The prior Opus M1 class survives: D-118 still says “any item marked NOT-RUN blocks the merge” and “A PR without a complete gate ledger is not merge-eligible,” while the PR template still calls D-118/D-121 the authoritative gate text. The new dated D-170 addendum points to TIER-01, and the triage explicitly defers direct D-118 reconciliation. The old “proposed,” “Ed may veto,” “Installed 2026-09-24,” and “2026-10-24” signatures are absent from the six substantive changed files.

The six substantive edits match the triage’s F1/F2/F3/F5/F6 list; the other six added paths are the charge, review, stdout, and triage records. The defect-log table has six matching columns, cited repository paths exist, `git diff --check` is clean, and `gen_state --check` reports no drift.

**F3 checker mutation evidence.** I copied only `scripts/check_gate_ledger.py` to a temporary directory, replaced its new `main()` predicate with `any(line.strip() == "Tier: light" for line in body.splitlines())`, and pointed the existing regression test at that copy. The worktree was untouched. The regression went red:

```text
AssertionError: 'gate-ledger: 4/4 RUN; 8/8 N/A (light tier)\n' != 'gate-ledger: 12/12 RUN\n'
Ran 1 test in 0.286s
FAILED (failures=1)
MUTATED_TEST_SUCCESS=False
```

At `3fdbbd13`, the same test is green (`Ran 1 test … OK`), and the focused module is green (`Ran 39 tests … OK`). No full test discovery was run.

## Residual risk

`gh pr view 419` twice returned `error connecting to api.github.com`. PR #419’s identity, state, and actual merge date need live verification before the installation and review dates can be finalized.