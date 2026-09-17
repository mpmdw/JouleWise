```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Addressed F1, F2, F5, F6 and F7; both mutants fail the new regressions; requested suite passes with nine environment-dependent skips.",
  "workspace": {
    "base_requested": "a4d530cdab07a0b72d70f1fea00d145b177895f2",
    "base_mode": "exact",
    "head_start": "a4d530cdab07a0b72d70f1fea00d145b177895f2",
    "head_end": "a4d530cdab07a0b72d70f1fea00d145b177895f2",
    "upstream_end": null,
    "branch": "fix/2026-09-17-wallclock-abort-r1"
  },
  "pathspec": [
    "scripts/run_night.py",
    "tests/test_run_night.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/a221fix-pycache python3 -B -m unittest tests.test_run_night.NightDriverTests.test_group_census_distinguishes_absence_from_failed_probes tests.test_run_night.ProcessGroupRetryTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.184s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests.*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "git show a4d530cd:scripts/run_night.py > /tmp/a221fix-base/scripts/run_night.py\npython3 -B - <<'PY'\nfrom pathlib import Path\np=Path('/tmp/a221fix-base/scripts/run_night.py')\ns=p.read_text()\nold='if result.returncode == 1 and not lines:'\nassert s.count(old)==1\np.write_text(s.replace(old,'if result.returncode != 0 and not lines:'))\nPY\n(cd /tmp/a221fix-base && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/a221fix-pycache python3 -B -m unittest tests.test_run_night.NightDriverTests.test_group_census_distinguishes_absence_from_failed_probes)",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Tuples differ: (False, ['census_exit_2: usage: pgrep ...']) != (True, [])",
          "Ran 1 test in 0.175s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "git show a4d530cd:scripts/run_night.py > /tmp/a221fix-base/scripts/run_night.py\npython3 -B - <<'PY'\nfrom pathlib import Path\np=Path('/tmp/a221fix-base/scripts/run_night.py')\ns=p.read_text()\nold='    while True:\\n        _signal_group(pgid, number)\\n'\nassert s.count(old)==1\np.write_text(s.replace(old,'    while True:\\n'))\nPY\n(cd /tmp/a221fix-base && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/a221fix-pycache python3 -B -m unittest tests.test_run_night.ProcessGroupRetryTests)",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Lists differ: [(4242, <Signals.SIGTERM: 15>)] != []",
          "AssertionError: Lists differ: [(4242, <Signals.SIGKILL: 9>)] != []",
          "Ran 1 test in 0.148s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/a221fix-pycache python3 -B -m unittest tests.test_run_night tests.test_docs_freshness > /tmp/a221fix-focused.log 2>&1; result=$?; tail -18 /tmp/a221fix-focused.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 168 tests in 52.621s", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V5",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/a221fix-pycache python3 -m compileall -q scripts/run_night.py tests/test_run_night.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
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
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/phase_2/derivation_night_runbook.md",
          " M docs/process/NIGHT_HANDBACK.md",
          " M scripts/run_night.py",
          " M tests/test_run_night.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": " M tests/test_run_night.py"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " docs/phase_2/derivation_night_runbook.md | 10 ++++-",
          " docs/process/NIGHT_HANDBACK.md           |  2 +-",
          " scripts/run_night.py                     |  4 +-",
          " tests/test_run_night.py                  | 67 ++++++++++++++++++++++++++++++++",
          " 4 files changed, 79 insertions(+), 4 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "4 files changed, 79 insertions\\(\\+\\), 4 deletions\\(-\\)"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/a221fix-pycache python3 -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The sandbox cannot observe processes through pgrep/ps. Nine existing tests skipped, and the required orphan census failed observation. Both new regressions executed without skips; no live hardware validation is claimed.",
      "needs": "Lead reruns the focused suite and fixture orphan census in the permitted verification environment before final acceptance."
    }
  ]
}
```

## Change

Added five-case census coverage and a deterministic retry regression that reuses `_signal_spy` and checks a fresh signal before every census in both phases. Corrected the custody wording and documented the grace calculation, OPEN-session residual, lease release, and reason for re-signalling. Production behavior is unchanged.

## Verification notes

Mutants ran separately in the authorized `/tmp/a221fix-base` copy, restoring the driver from `a4d530cd` before each mutation. Focused checks were used because changes are limited to tests, documentation, and a comment.

The baseline’s canonical digest matched. No commits or Git writes were performed. Next step: lead review and environment-dependent verification identified in `ENV1`.