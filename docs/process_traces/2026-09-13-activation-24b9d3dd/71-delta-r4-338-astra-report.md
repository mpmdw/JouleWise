```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "CURED; no findings: round 4 removes rule-persistence wording, and all requested mechanical checks pass.",
  "workspace": {
    "base_requested": "792b7bc9",
    "base_mode": "exact",
    "head_start": "23911de390b3976d6566599cb8f8390981c8e6f3",
    "head_end": "23911de390b3976d6566599cb8f8390981c8e6f3",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [".venv"],
  "verdict": {
    "findings": [],
    "delta": "No new defect: no rule added, fence softened, untrue statement introduced, or cell-text rule broken.",
    "same_signature": "CURED: rule-persistence wording does not survive in added diff text; exact grep returns only the cured D-181 line.",
    "grep_output": "22:+until that lane lands the existing mechanism's limits remain facts, not rules (decided\n",
    "selectable_task_ids": [
      "ED-DATES-01",
      "V5-G2A-PREFILL-PROBE-01",
      "WO-LAUNCH-BINDING"
    ],
    "selectable_equality": "PASS: exact set equality asserted.",
    "mechanical": "gen_state --check rc=0; 44 tests pass; tests/, joulewise/, scripts/ diff empty.",
    "environment": "PYTHONDONTWRITEBYTECODE=1; TMPDIR=/tmp; .venv Python.",
    "coverage": "Docs-only delta: focused generator suite; no live validation or checkout writes."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": ".venv/bin/python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": ".venv/bin/python3 -Bm unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 44 tests in 2.956s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff 792b7bc9..HEAD -- tests joulewise scripts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```