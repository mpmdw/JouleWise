```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Both mutants are killed; production AST is unchanged; 168 tests pass with nine skips; two documentation nits remain.",
  "workspace": {
    "base_requested": "6bcf5f0a62f2fe56be6e0fc39f11363452ca2743",
    "base_mode": "exact",
    "head_start": "6bcf5f0a62f2fe56be6e0fc39f11363452ca2743",
    "head_end": "6bcf5f0a62f2fe56be6e0fc39f11363452ca2743",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE-WITH-FIXES",
    "findings": [
      {
        "id": "R1",
        "severity": "nit",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1389,
        "summary": "The 180-second overrun allowance is nominal, not a guaranteed maximum.",
        "evidence": "180 + 120 consumes all 300 seconds. abort_calibration_session acquires the lease and repairs the ledger before creating CustodyDeadline (calibration_ledger.py:6187-6200), then appends the abort after inspection (:6240). These operations consume additional time, acknowledged earlier as seconds of lease and repair work.",
        "requested_change": "Describe 180 seconds as nominal remaining headroom, reduced by lease, repair and closing overhead. An overrun below 180 seconds can also exhaust the total grace."
      },
      {
        "id": "R2",
        "severity": "nit",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1394,
        "summary": "The newly introduced term kernel flock lacks a plain-language definition.",
        "evidence": "This is the runbook's only flock occurrence; the first-use table has no entry. The sentence explains release on process death but does not explain what flock is.",
        "requested_change": "Gloss it inline as an operating-system-managed exclusive file lock."
      }
    ],
    "confirmed": [
      "Scope inspected: exactly four files, 79 insertions and four deletions between a4d530cd and 6bcf5f0a.",
      "Record 66 F1 and F2 are closed by independently reproduced mutant failures. The retry test checks signal identity and ordering before every census in both phases.",
      "F5's single-read wording matches custody_state_scope='next_slot' and one CustodyDeadline.",
      "WINDOW_SHUTDOWN_GRACE_S=300; TERMINATION_BOUND_S=2*(30+5)=70; courier allowance=300; nominal total=670; dead-man allowance=3900 before upward minute rounding; nominal margin=3230.",
      "The default capture budget is 480 seconds. Both next_start and the actual slot_start are checked against WINDOW_END_EPOCH_S; the budget does not terminate a writer.",
      "The OPEN-session residual is supported: pre-reserve refuses existing open sessions. CalibrationWriterLease uses exclusive kernel flock locks, with explicit unlock/close on normal release and kernel release on process exit.",
      "F7's handback explanation matches the re-signal-before-census loop and explains why newly forked members require another signal.",
      "Baseline self-digest matches the supplied anchor. Record 68 was read after independent audit work; its mutation and suite outcomes agree with this re-audit."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.NightDriverTests.test_group_census_distinguishes_absence_from_failed_probes tests.test_run_night.ProcessGroupRetryTests",
      "cwd": "/tmp/reaudit-a221fix",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.155s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests.*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\np=Path('/tmp/reaudit-a221fix/scripts/run_night.py')\ns=p.read_text()\nold='if result.returncode == 1 and not lines:'\nnew='if result.returncode != 0 and not lines:'\nassert s.count(old)==1\np.write_text(s.replace(old,new))\nprint('M4 applied: == 1 -> != 0')\nPY\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.NightDriverTests.test_group_census_distinguishes_absence_from_failed_probes",
      "cwd": "/tmp/reaudit-a221fix",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Tuples differ: (False, ['census_exit_2: usage: pgrep ...']) != (True, [])",
          "Ran 1 test in 0.132s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\np=Path('/tmp/reaudit-a221fix/scripts/run_night.py')\ns=p.read_text()\nold='if result.returncode != 0 and not lines:'\nassert s.count(old)==1\ns=s.replace(old,'if result.returncode == 1 and not lines:')\nold='    while True:\\n        _signal_group(pgid, number)\\n'\nassert s.count(old)==1\np.write_text(s.replace(old,'    while True:\\n'))\nprint('M4 restored; M3 applied: delete retry _signal_group')\nPY\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night.ProcessGroupRetryTests",
      "cwd": "/tmp/reaudit-a221fix",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Lists differ: [(4242, <Signals.SIGTERM: 15>)] != []",
          "AssertionError: Lists differ: [(4242, <Signals.SIGKILL: 9>)] != []",
          "Ran 1 test in 0.127s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import ast,subprocess; read=lambda rev: subprocess.check_output([\"git\",\"show\",rev+\":scripts/run_night.py\"],text=True); assert ast.dump(ast.parse(read(\"a4d530cd\")),include_attributes=False)==ast.dump(ast.parse(read(\"6bcf5f0a\")),include_attributes=False); print(\"PASS: scripts/run_night.py ASTs identical\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: scripts/run_night.py ASTs identical"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: scripts/run_night.py ASTs identical"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "cp /Users/edr/code/JouleWise-wt-a221-fix-ref/scripts/run_night.py /tmp/reaudit-a221fix/scripts/run_night.py && cmp /Users/edr/code/JouleWise-wt-a221-fix-ref/scripts/run_night.py /tmp/reaudit-a221fix/scripts/run_night.py && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night tests.test_docs_freshness > /tmp/reaudit-a221fix-suite.log 2>&1",
      "cwd": "/tmp/reaudit-a221fix",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 168 tests in 55.470s", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": "/tmp/reaudit-a221fix",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && cmp scripts/run_night.py /tmp/reaudit-a221fix/scripts/run_night.py && tail -5 /tmp/reaudit-a221fix-suite.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "6bcf5f0a62f2fe56be6e0fc39f11363452ca2743",
          "Ran 168 tests in 55.470s",
          "OK (skipped=9)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Nine existing process-census tests skipped because sandbox process observation is unavailable; the fixture orphan census likewise failed on ps permission. Both new regressions executed. No live hardware validation is claimed.",
      "needs": "Lead runs the focused suite and fixture orphan census in the permitted verification environment before final acceptance."
    }
  ]
}
```

## Findings

- **R1 — nit:** Qualify the 180-second allowance as nominal headroom; lease, repair and closing work also consume the 300-second grace.
- **R2 — nit:** Define `flock` inline as an operating-system-managed exclusive file lock.

Neither requires a production-code change. The lead’s next step is the two wording fixes and environment-dependent verification in `ENV1`.