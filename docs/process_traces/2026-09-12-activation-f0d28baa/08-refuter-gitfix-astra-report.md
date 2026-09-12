```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No blocker found in the landing; two should-fixes found. Sandbox restrictions prevented successful fixture-dependent verification.",
  "workspace": {
    "base_requested": "ace4cc3c",
    "base_mode": "exact",
    "head_start": "68c4dd4612d4d4e1ca5dfe5336310a2d90c8e516",
    "head_end": "68c4dd4612d4d4e1ca5dfe5336310a2d90c8e516",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-git-fixture-maintenance-sweep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "Literal string concatenation bypasses the census",
        "path": "tests/test_git_fixture_maintenance.py",
        "line": 119,
        "evidence": "cmd = ['git', 'in' + 'it']; subprocess.run(cmd) produces no violation.",
        "recommendation": "Resolve constant string concatenation and add this negative case. No matching constant-concatenation init form was found in existing tests/**/*.py."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "title": "Two tests assert the identical repository census",
        "path": "tests/test_git_fixture_hygiene.py",
        "line": 26,
        "evidence": "Both hygiene:26 and maintenance:269 assert self.assertEqual(_git_init_violations(TESTS_ROOT), {}). The maintenance assertion already exists at baseline line 172.",
        "recommendation": "Keep tests/test_git_fixture_maintenance.py as the ONE repository-census home. Drop test_repository_census from the new hygiene module; retain its adversarial scanner tests."
      }
    ],
    "fence": "Only three tests/ modules changed. Existing assertion ASTs are identical: identity_pins 177/177; git_fixture_maintenance 6/6. The new hygiene module adds assertions. No existing assertion changed, no product code changed, and calibration-exits is untouched.",
    "synthetic_probe": {
      "method": "Imported the real census; monkeypatched Path.rglob and Path.read_text with in-memory source modules because temporary-file writes are blocked.",
      "argv": "caught, line 2",
      "shell_string": "caught, line 2",
      "f_string": "caught, line 3",
      "shared_helper": "accepted",
      "list_concatenation": "caught, lines 2 and 3",
      "join_parts": "caught, line 3",
      "string_concatenation": "missed"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff ace4cc3c..HEAD -- tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["     git(root, \"config\", \"user.email\", \"identity-pin-test@example.invalid\")", " "]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "identity-pin-test@example.invalid"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "time env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_hygiene",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 5 tests in 5.504s",
          "FAILED (errors=17)",
          "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest   5.63s user 0.04s system 99% cpu 5.686 total"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_identity_pins tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 52 tests in 10.695s",
          "FAILED (errors=53)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\s*$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_hygiene.GitFixtureHygieneTests.test_repository_census -q",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 5.283s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\s*$"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check ace4cc3c..HEAD",
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
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The read-only sandbox blocks temporary-file creation, including /tmp. Fixture-dependent tests report FileNotFoundError: No usable temporary directory found. Physical synthetic modules could not be written; only the in-memory census probes and real repository scan completed.",
      "needs": "Lead reruns the synthetic file probes, timed module, and combined suite with writable temporary storage. Preserve the repository write fence."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The seat report records three green runs per touched module; those repetitions and hosted verification were not independently established in this session.",
      "needs": "Lead owns final bench and hosted acceptance."
    }
  ]
}
```

## Findings

**No blocker found in the landing.** No existing assertion changed in `tests/test_identity_pins.py` or elsewhere. The two existing modules retain identical assertion ASTs; the third module contains newly added tests.

**R1 — should_fix:** The census misses this executable repository-creation form:

```python
import subprocess
cmd = ['git', 'in' + 'it']
subprocess.run(cmd)
```

The real census returned no violation against in-memory file contents. Inspection of `tests/**/*.py` found no constant-string concatenation producing `init` or a Git-init command, so this remains a should-fix under the brief.

The requested argv, shell-string, and f-string cases were caught; shared-helper routing was accepted. Both suggested alternatives—`["git"] + ["init"]` and `" ".join(parts)`—were also caught.

**R2 — should_fix:** These lines assert exactly the same invariant:

- `tests/test_git_fixture_maintenance.py:269`: `self.assertEqual(_git_init_violations(TESTS_ROOT), {})`
- `tests/test_git_fixture_hygiene.py:26`: `self.assertEqual(_git_init_violations(TESTS_ROOT), {})`

The former already existed at baseline line 172. Keep maintenance as the ONE census home; remove the new module’s duplicate census test while retaining its adversarial cases.

## Residual risk

The isolated repository census passed in **5.283 seconds**, below the 30-second threshold. The full new module took **5.686 seconds**, but temporary-file failures prevent treating that as a successful full-module timing.

Requested combined rerun:

```text
Ran 52 tests in 10.695s

FAILED (errors=53)
```

The environment reports `FileNotFoundError: No usable temporary directory found`, including `/tmp`. Successful fixture-dependent verification remains with the lead. No files were modified.