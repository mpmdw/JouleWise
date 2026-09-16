```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Implemented the bounded orphan sentinel and informational launch logging; deterministic checks pass, but live smoke remains PROVISIONAL because the sandbox denies ps.",
  "workspace": {
    "base_requested": "46bce53b9d80afd4db373ea01985b70bed366567",
    "base_mode": "exact",
    "head_start": "46bce53b9d80afd4db373ea01985b70bed366567",
    "head_end": "46bce53b9d80afd4db373ea01985b70bed366567",
    "upstream_end": "623a6c01c013984031992d7bb2080a3a67dfa4be",
    "branch": "feat/2026-09-15-fixture-sentinel"
  },
  "pathspec": [
    "scripts/fixture_orphan_census.py",
    "tests/test_fixture_orphan_census.py",
    "tests/fixture_signatures.json",
    "scripts/magistrate_watchdog.py",
    "docs/orchestration.md"
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
      "cmd": "/usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_fixture_orphan_census -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 12 tests in 0.179s",
          "OK (skipped=1)",
          "real 0.71",
          "user 0.67",
          "sys 0.03"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport unittest\nfrom scripts import fixture_orphan_census as s\nfrom tests import test_fixture_orphan_census as t\nsource = open(s.__file__).read()\nassert source.count('if ppid != 1:') == 1\nnamespace = {'__file__': s.__file__, '__name__': 'mutation'}\nexec(compile(source.replace('if ppid != 1:', 'if False:'), s.__file__, 'exec'), namespace)\ns.census = namespace['census']\nunittest.main(module=t, argv=['mutation', 'FixtureOrphanCensusTests.test_pid_one_filter'], verbosity=2)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.014s",
          "FAILED (failures=6)",
          "real 0.53"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=6\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport unittest\nfrom scripts import fixture_orphan_census as s\nfrom tests import test_fixture_orphan_census as t\nsignatures = s.load_signatures()\ns.load_signatures = lambda: signatures[1:]\nunittest.main(module=t, argv=['mutation', 'FixtureOrphanCensusTests.test_required_fixture_signatures'], verbosity=2)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.013s",
          "FAILED (failures=1)",
          "real 0.53"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport unittest\nfrom scripts import fixture_orphan_census as s\nfrom tests import test_fixture_orphan_census as t\nsignatures = s.load_signatures()\ns.load_signatures = lambda: signatures[:-1]\nunittest.main(module=t, argv=['mutation', 'FixtureOrphanCensusTests.test_required_fixture_signatures'], verbosity=2)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.012s",
          "FAILED (failures=1)",
          "real 0.53"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-a208-20260915.json --expect-digest sha256:0042cb109753d27c7b9e6f1295a01f581f6e34466844a9faaf742001bdd837dd --scope scripts/fixture_orphan_census.py tests/test_fixture_orphan_census.py tests/fixture_signatures.json scripts/magistrate_watchdog.py docs/orchestration.md --lease-id lease-d27d9dec76b841029515aee7447f1771",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"verdict\":\"SCOPE_OK\""
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && git rev-parse HEAD '@{upstream}' && wc -l scripts/fixture_orphan_census.py tests/test_fixture_orphan_census.py tests/fixture_signatures.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "     126 scripts/fixture_orphan_census.py",
          "     183 tests/test_fixture_orphan_census.py",
          "      12 tests/fixture_signatures.json",
          "     321 total"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "321 total"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The initial live smoke failed with PermissionError: [Errno 1] Operation not permitted: 'ps'. The final module explicitly skips this exact sandbox denial; live census validation remains PROVISIONAL.",
      "needs": "Lead must run /usr/bin/time -p env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_fixture_orphan_census.FixtureOrphanCensusTests.test_live_cli_smoke -v in an authorized environment and confirm PASS without a skip."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during the session; the branch is now behind by two commits. Worktree HEAD stayed at BASE_HEAD and the anchored scope check returned SCOPE_OK.",
      "needs": "Lead should review integration against current main before landing."
    }
  ]
}
```

## Change

Added JSON census output with PID-1 filtering, fixture-specific registry matching, UTC start time, age, RSS, and optional exit-1 enforcement. Invalid registries and acquisition failures exit 2.

Hunks add the helper, two registry entries, and twelve tests; watchdog changes cover imports, dependency injection, and `start_session` (`@@ -1993,6 +1996,15`). The documentation adds the session-end checklist.

Signatures derive from the NV5 fixture’s `/fake/model`, `nv5-fake-model`, and `nv5-localhost-contract/tasks/` argv markers. AXI static-batch tests mock subprocess execution and supply no additional live signature. The permitted `ps` fallback supplies RSS, which the existing kernel inventory lacks.

Launch events record rows/count or an explicit acquisition error without changing census refusals. No culling or prewindow changes were made. No commit was created.

## Verification notes

All three intentional mutations produced RED; the final unmutated module returned GREEN with the live smoke explicitly skipped. Mutations existed only in memory.

Only the touched test module ran, as directed. Scope verification covered exactly the five authorized paths. Lead review and the unskipped live smoke are the next steps.