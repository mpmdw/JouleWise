```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Stabilized the FIFO deadline regression and documented the unchanged 60-second clock-skew allowance.",
  "workspace": {
    "base_requested": "64297f9dd579a62c1214219f3f7919ebf02714c6",
    "base_mode": "exact",
    "head_start": "64297f9dd579a62c1214219f3f7919ebf02714c6",
    "head_end": "64297f9dd579a62c1214219f3f7919ebf02714c6",
    "upstream_end": "64297f9dd579a62c1214219f3f7919ebf02714c6",
    "branch": "feat/2026-09-16-reserve-hang-transport"
  },
  "pathspec": [
    "tests/test_run_night.py",
    "joulewise/night_agent_install.py"
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
      "cmd": "set -o pipefail\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night 2>&1 | tail -4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 120 tests in 33.478s",
          "",
          "OK (skipped=3)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "set -o pipefail\nfor r1_trial in 1 2 3 4 5; do\n  printf 'trial=%s\\n' \"$r1_trial\"\n  TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_run_night.NightProbeTests.test_probe_deadline_covers_blocked_binding_read || exit $?\ndone 2>&1 | tee /tmp/rh-fix2-five-runs.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "trial=1",
          "Ran 1 test in 16.713s",
          "OK",
          "real 16.84",
          "trial=2",
          "Ran 1 test in 16.729s",
          "OK",
          "real 16.84",
          "trial=3",
          "Ran 1 test in 16.630s",
          "OK",
          "real 16.74",
          "trial=4",
          "Ran 1 test in 16.661s",
          "OK",
          "real 16.77",
          "trial=5",
          "Ran 1 test in 16.631s",
          "OK",
          "real 16.74"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/rh-fix2-pycache python3 -m compileall -q scripts joulewise\necho compile_rc=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["compile_rc=0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "compile_rc=0"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check\ngit status --short\ngit diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M joulewise/night_agent_install.py",
          " M tests/test_run_night.py",
          " joulewise/night_agent_install.py |  5 ++++",
          " tests/test_run_night.py          | 56 ++++++++++++++++++++++++++++++++++++----",
          " 2 files changed, 56 insertions(+), 5 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2 files changed"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Three unchanged process-census tests remain skipped because the sandbox lacks a working pgrep census. The revised FIFO regression executed successfully in all five trials and in the module run.",
      "needs": "The lead's existing census-capable verification remains outstanding."
    }
  ]
}
```

## Change

The harness records monotonic time at `probe_night()` entry, explicitly separating outer CLI imports from the probe deadline. It observes `bindings` before expiry, leaves the FIFO blocked, and asserts `outcome=timeout`, `phase=bindings`, completion within the 15-second budget plus two seconds, and no surviving worker. Worker startup remains inside that deadline.

The skew comment documents the supplied clock-resynchronisation rationale. AST comparison confirms installer executable logic and the 60-second value are unchanged. No commits or repository Git writes were made.