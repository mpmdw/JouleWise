```json
{
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [],
    "fix_round_commit": "7008fbf014bf0d8eccb7f3412b1e22e9b1636f17",
    "refuter_findings": [
      {
        "id": "B1",
        "disposition": "CURED",
        "evidence": "The current XS pin matches digest 12d0293b...; the named pin regression and the retained-corpus replay pass. Restoring the stale 8733ff03... pin makes the named regression fail on digest XS."
      },
      {
        "id": "B2",
        "disposition": "CURED",
        "evidence": "Help renders the numeric code from Disposition.exit_code and the regression independently pins 0/2/3, tokens, and clauses. Rendering help code 7 while runtime remains 2 makes the named regression fail."
      },
      {
        "id": "B3",
        "disposition": "CURED",
        "evidence": "Named producer-and-driver regressions require wrong raw digest to exit 2 and absent events.jsonl to exit 3. Restoring either defect makes its regression fail."
      }
    ],
    "new_defects": [],
    "same_signature": "No same-signature recurrence: the stale XS mismatch and all three missing/non-discriminating regression signatures are absent at HEAD."
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "All refuter blockers are cured with discriminating counterfactuals, the complete touched module passes retained-corpus replay, and the fix round is landable.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "descendant",
    "head_start": "7008fbf014bf0d8eccb7f3412b1e22e9b1636f17",
    "head_end": "7008fbf014bf0d8eccb7f3412b1e22e9b1636f17",
    "upstream_end": "a6e9edde082f460fbe335d2eac8021f77258b8e6",
    "branch": "feat/2026-09-04-fan-R7F-EXIT3-SEMANTICS-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/06-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.RegistryAndDigestTests.test_registry_pinned_files_match tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_disposition_table_drives_finalizer_and_help tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_present_raw_digest_drift_is_mismatch_in_producer_and_driver tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_missing_events_is_incomplete_in_producer_and_driver",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 0.227s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 4 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 51 tests in 610.183s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 51 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.RegistryAndDigestTests.test_registry_pinned_files_match",
      "cwd": "/private/tmp/r7f-delta-reaudit-b1.HATRiq",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.003s", "", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_disposition_table_drives_finalizer_and_help",
      "cwd": "/private/tmp/r7f-delta-reaudit-b2.4qCFhW",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.005s", "", "FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_present_raw_digest_drift_is_mismatch_in_producer_and_driver",
      "cwd": "/private/tmp/r7f-delta-reaudit-b3raw.VLiH0n",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: 3 != 2", "Ran 1 test in 0.230s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "AssertionError: 3 != 2[\\s\\S]*FAILED \\(failures=1\\)"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_missing_events_is_incomplete_in_producer_and_driver",
      "cwd": "/private/tmp/r7f-delta-reaudit-b3events.FGptLo",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FileNotFoundError", "Ran 1 test in 0.232s", "FAILED (errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FileNotFoundError[\\s\\S]*FAILED \\(errors=1\\)"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "BASE=$(git merge-base origin/main HEAD); git diff --name-only 89877419..HEAD; for p in RUN_STATE.md TASK_QUEUE.md PROJECT_STATUS.md AGENT_PLAN.md docs/process/state_kernel.json docs/decision_log.md docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; do git diff --quiet $BASE..HEAD -- $p || exit 1; done; git diff --check 89877419..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs/paper/results-fill-registry.md", "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/04-sol-fix-round-1-resume-report.md", "scripts/check_paper_round7_artifacts.py", "tests/test_paper_round7_artifacts.py"]},
      "expected": {"exit_code": 0, "tail_regex": "tests/test_paper_round7_artifacts\\.py$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during the audit from b0ed6991 to a6e9edde; merge-base(origin/main, HEAD) remained b0ed6991 and the audited fix-round delta 89877419..7008fbf0 was unchanged.",
      "needs": ""
    }
  ]
}
```

## Findings

None. Refuter blockers B1, B2, and B3 are CURED. The named regressions pass at HEAD, while the stale-pin, help/runtime disagreement, wrong-raw classification, and missing-events-guard counterfactuals each fail with the expected signature. No new defect or same-signature recurrence was found. Magistrate-owned state documents show no delta.

## Residual risk

Per preflight, verification covered only the fix round's touched test module; no repository-wide or cross-module suite ran. The touched module's retained-corpus replay did execute and pass.
