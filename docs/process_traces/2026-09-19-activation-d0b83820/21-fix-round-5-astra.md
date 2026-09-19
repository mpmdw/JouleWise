```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "R1/R2 implemented; 45 tests passed twice (wall times 8.346 s and 8.396 s); all six mutations killed.",
  "workspace": {
    "base_requested": "46d310eba1fa43a5ca898364302db90392fcd757",
    "base_mode": "exact",
    "head_start": "46d310eba1fa43a5ca898364302db90392fcd757",
    "head_end": "46d310eba1fa43a5ca898364302db90392fcd757",
    "upstream_end": "46d310eba1fa43a5ca898364302db90392fcd757",
    "branch": "feat/2026-09-18-quiet-predicate-evidence-harness"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "tests/test_sample_quiet_predicate_evidence.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 45 tests in 7.885s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 45 tests.*\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 45 tests in 7.954s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 45 tests.*\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-fix5-232/bench.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "STATUS AFTER",
          "## feat/2026-09-18-quiet-predicate-evidence-harness...origin/feat/2026-09-18-quiet-predicate-evidence-harness",
          " M scripts/sample_quiet_predicate_evidence.py",
          " M tests/test_sample_quiet_predicate_evidence.py",
          "tracked_files_checked 8053 byte_changed []",
          "status_identical True",
          "All 6 mutations killed; worktree byte-identical."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "All 6 mutations killed; worktree byte-identical\\."}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-fix5-232/final_checks.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "43 other existing tests byte-identical; real-load AST and assertion set unchanged",
          "45 tests total; one new Markdown regression",
          "join_grace_s keyword-only default 5.0; CLI unchanged",
          "Scoped diff and whitespace checks PASS",
          "FINAL CHECKS PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "FINAL CHECKS PASS"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " scripts/sample_quiet_predicate_evidence.py    | 21 ++++++++++------",
          " tests/test_sample_quiet_predicate_evidence.py | 35 +++++++++++++++++++++++++--",
          " 2 files changed, 46 insertions(+), 10 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2 files changed, 46 insertions\\(\\+\\), 10 deletions\\(-\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Completed the requested module and mutation bench; canonical full discovery was not run in this bounded fix round.",
      "needs": "Lead performs the planned delta re-audit and full sharded replay."
    }
  ]
}
```

## Change

All three Markdown tables now display `boot_id` and conditionally display `os_build`, matching `comparison_fields`. One new regression checks rendered identities and the separate 1 W/9 W rows, including absent and mixed build fields.

`load()` now accepts keyword-only `join_grace_s=5.0`. Only the stuck-child subtest passes `0.2`; the one-second clean-exit case retains the production default. No CLI flag was added. Changes remain uncommitted.

Next exact step: lead delta re-audit round 5.

## Verification notes

Mutations ran exclusively on `/tmp` copies. Each exited 1 with assertion failures and zero test errors:

| Mutation | Failing test names |
|---|---|
| `pool-across-boots` | `test_summary_markdown_distinguishes_boots_and_optional_builds` (three subcases); `test_summary_never_pools_census_conditions_or_reference` (`boot_id`) |
| `cleanup-silent` | `test_load_worker_runs_its_window_after_the_rendezvous` (`exit_delay=60`, short grace) |
| `cores` | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `clock` | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `burn-noop` | `test_burn_profiles_advance_their_generator` |
| `window-skip` | `test_load_worker_runs_its_window_after_the_rendezvous` |

The reported byte identity compares the edited worktree immediately before and after the bench. Complete outputs: [bench log](/tmp/jw-fix5-232/bench.log), [mutation results](/tmp/jw-fix5-232/results.json), [preservation checks](/tmp/jw-fix5-232/final_checks.log).