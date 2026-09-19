```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Regenerated both ARM-RETRY-POLICY blocks and preserved hand-written amendments verbatim outside the fences; all four required suites pass.",
  "workspace": {
    "base_requested": "0b36fba6",
    "base_mode": "exact",
    "head_start": "0b36fba6a0b8e10cca879b4518e7773be83c0ac7",
    "head_end": "0b36fba6a0b8e10cca879b4518e7773be83c0ac7",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 32 tests in 0.328s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 32 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 72 tests in 0.597s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 72 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_gen_evidence_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 7 tests in 2.482s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 7 tests[\\s\\S]*OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 7.025s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests[\\s\\S]*OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/stage-a-round2b-verify.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/process/NIGHT_HANDBACK.md",
          "  before=835822052d9d54e1ec5a58615749f65ac6b9709d40d55f301b132251a2a47548",
          "  after=dffd1359c902c13ebca0ca72d04fbde2824b123d04e3e799bd297cfa5f79a89a",
          "docs/phase_2/derivation_night_runbook.md",
          "  before=dddd922d9f22c77d95d3bc5a173251a39a6f57c43284e5d84433e5e6f1be2c2c",
          "  after=dffd1359c902c13ebca0ca72d04fbde2824b123d04e3e799bd297cfa5f79a89a",
          "render_policy=dffd1359c902c13ebca0ca72d04fbde2824b123d04e3e799bd297cfa5f79a89a",
          "PASS: both blocks equal renderer; prose and diagnostic rows preserved verbatim outside fences; existing adjacent text unchanged."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: both blocks equal renderer"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " docs/phase_2/derivation_night_runbook.md |  2 +-",
          " docs/process/NIGHT_HANDBACK.md           | 30 +++++++++++++++++-------------",
          " 2 files changed, 18 insertions(+), 14 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2 files changed, 18 insertions\\(\\+\\), 14 deletions\\(-\\)"}
    }
  ],
  "flags": []
}
```

## Change

Both fenced blocks now equal `render_policy()` byte-for-byte. The registration clause, QPE narrative, and two payload-diagnostic rows moved outside the handback fence unchanged.

The sealed-manifest paragraph and runbook evidence verify-only row were already outside the fences and remain unchanged. No commit was made. Next step: lead diff review.

## Verification notes

The baseline exact-block test failed as reported; it now passes. Part a already supplies and tests the rendered registration refusal. The renderer contains no probe table, and the docs-amendment test has no location constraint, so source and test edits were unnecessary.

The four requested suites cover this documentation-only change; the canonical full suite was not run.