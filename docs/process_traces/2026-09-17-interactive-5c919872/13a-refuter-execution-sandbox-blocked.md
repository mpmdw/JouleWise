```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Read-only sandbox denies /tmp writes: six modules attempted, 110 tests passed, 194 errored, 9 skipped; all 21 mutant verdicts remain pending.",
  "workspace": {
    "base_requested": "a2671902",
    "base_mode": "exact",
    "head_start": "a267190279afbb6660a5433f34a654ad36042eb5",
    "head_end": "a267190279afbb6660a5433f34a654ad36042eb5",
    "upstream_end": "6ea6ecf1012fca20bc091e1e2f131be5004f74c4",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "disposition": "No clean-review verdict. Environment failures are not mutant kills or demonstrated code defects.",
    "baseline": "Manifest SHA-256 matches 715113469bff58cb895629d2bcc289ebec7a2a7c52f3a80f8065ad0526854470; detached HEAD and clean workspace unchanged.",
    "test_key": "R1-R10 identify the exact named regressions in 01-brief-seat-quiet-admission.md:89-98. Fix references identify items in 08-brief-seat-Q-fix-round-1.md.",
    "mutant_columns": ["id", "mutant", "required_test", "result", "observed_assertion"],
    "mutant_table": [
      [1, "Admit on first quiet sample", "R1", "NOT_RUN", "Still pending: copy denied"],
      [2, "Busy sample does not reset consecutive run", "R1", "NOT_RUN", "Still pending: copy denied"],
      [3, "Continue polling after GO", "R1", "NOT_RUN", "Still pending: copy denied"],
      [4, "Truncate journal; derive receipt digest/count from truncation", "R2", "NOT_RUN", "Still pending: copy denied"],
      [5, "Reset deadline on every sample", "R2, R8", "NOT_RUN", "Still pending: copy denied"],
      [6, "Load authorises admission or retains LOAD_MAX veto", "R3, R4", "NOT_RUN", "Still pending: copy denied"],
      [7, "Exempt fseventsd/mds_stores from aggregate", "R3, R6", "NOT_RUN", "Still pending: copy denied"],
      [8, "Use stale %CPU; high %CPU with zero delta", "R4", "NOT_RUN", "Still pending: copy denied"],
      [9, "Replay initial driver census", "R5", "NOT_RUN", "Still pending: copy denied"],
      [10, "PID-only identity; lose exited-process delta", "R6", "NOT_RUN", "Still pending: copy denied"],
      [11, "Subtract observer or omit observer label", "R6", "NOT_RUN", "Still pending: copy denied"],
      [12, "Insert v2 quiet_admission default; emit v4 without flag", "R7; generator --check", "NOT_RUN", "Still pending: copy denied"],
      [13, "GO shifts E/completion/courier/dead-man", "R8", "NOT_RUN", "Still pending: copy denied"],
      [14, "Wall rollback extends bind deadline", "R8 rollback companion", "NOT_RUN", "Still pending: copy denied"],
      [15, "Allow bare-refusal/started/reserved/same-digest successor", "R9 and successor identity companions", "NOT_RUN", "Still pending: copy denied"],
      [16, "Sequential hung sampler blocks census/expiry", "R10", "NOT_RUN", "Still pending: copy denied"],
      [17, "Malformed sampler output counts as quiet", "R10 malformed-output companion", "NOT_RUN", "Still pending: copy denied"],
      [18, "Float top -s argv; drop interval integer validation", "test_top_argv_uses_integer_seconds; R7 validation; fix 7", "NOT_RUN", "Still pending: copy denied"],
      [19, "Wrong expiry code; classify expiry outside cold gate", "R2; test_bind_expiry_stays_cold_and_uses_d182_successor_route; fix 4", "NOT_RUN", "Still pending: copy denied"],
      [20, "Accept empty cutoff_authority; default missing busy_core_max", "test_v4_requires_complete_valid_explicit_policy; fixes 2-3", "NOT_RUN", "Still pending: copy denied"],
      [21, "Accept runway 7979 or window one second short", "test_build_spec_enforces_window_and_computed_post_bind_minimum; fix 10", "NOT_RUN", "Still pending: copy denied"]
    ],
    "timing": {
      "module_wall_seconds": {
        "test_night_gate": 0.923,
        "test_quiet_admission": 0.309,
        "test_night_plan_writer": 0.532,
        "test_arm_retry": 0.798,
        "test_run_night": 2.393,
        "test_gen_derivation_night": 1.168
      },
      "over_10_seconds": "None observed. Setup errors prevent runtime conclusions for blocked tests.",
      "cancellation_test_seconds": 0.023
    },
    "inspection": [
      "Literal sleep >=5 search found 22 lines across tests; three in the six target modules: tests/test_run_night.py:138, :140, :4298, all sleep(60). The new :4298 cancellation test passed in 0.023s.",
      "Direct subprocess ps/top/sysctl grep returned no matches. Target sampler tests mock subprocess.run at tests/test_quiet_admission.py:98. This static search is not exhaustive dynamic tracing.",
      "Existing night_gate_fixtures bytes are unchanged in the requested diff; legacy_plan_v2.json is newly added. Current v2 plan-byte and legacy receipt comparisons passed.",
      "In-memory compile() passed for all 190 Python files under scripts and joulewise; no bytecode written."
    ]
  },
  "verification": [
    {
      "id": "V1", "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest --durations 0 tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 63 tests in 0.612s", "", "FAILED (errors=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2", "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest --durations 0 tests.test_quiet_admission",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 0.026s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3", "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest --durations 0 tests.test_night_plan_writer",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 10 tests in 0.010s", "", "FAILED (errors=8)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4", "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest --durations 0 tests.test_arm_retry",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.294s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5", "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest --durations 0 tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 157 tests in 1.963s", "", "FAILED (errors=146, skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6", "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest --durations 0 tests.test_gen_derivation_night",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 43 tests in 0.657s", "", "FAILED (errors=37)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7", "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated derivation-night wrapper region matches"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS generated derivation-night wrapper region matches"}
    },
    {
      "id": "V8", "kind": "other",
      "cmd": "cp -R /Users/edr/code/JouleWise-wt-ref-exec/. /tmp/refute-exec/",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["cp: /tmp/refute-exec: Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V9", "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/refute-exec/bytecode PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q scripts joulewise",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["*** Error compiling 'joulewise/workloads.py'...", "PermissionError: [Errno 1] Operation not permitted: '/tmp/refute-exec'"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V10", "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from tests.test_quiet_admission import legacy_counterfactual; legacy_counterfactual()'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["test_low_load_busy_daemon_never_admits: load=1.2, process_busy_cores=0.9; AssertionError: 'GO' != 'REFUSED'", "test_finished_burst_admits_despite_high_load: load=3.7, process_busy_cores=0.02; AssertionError: 'REFUSED' != 'GO'"]},
      "expected": {"exit_code": 1, "tail_regex": "2 legacy counterfactual assertions failed as expected"}
    },
    {
      "id": "V11", "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v --durations 4 tests.test_run_night.QuietDriverIntegrationTests.test_supervised_worker_is_reaped_on_cancellation tests.test_night_gate.QuietGatePhaseTests.test_v2_receipt_bytes_and_validation_match_original_legacy_scenarios tests.test_night_plan_writer.QuietPlanVersionTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 0.052s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "E1", "kind": "environment", "level": "blocking",
      "text": "The runner permits filesystem reads only, including /tmp. V8 prevented every required mutant copy. Suite errors reported unavailable temporary directories or denied /tmp creation. Compileall reported 190 scratch-bytecode permission errors.",
      "needs": "Relaunch with writable scratch storage for /tmp/refute-exec and unittest temporary directories, retaining repository WRITE_SCOPE []; rerun the six modules and all 21 mutant groups."
    },
    {
      "id": "E2", "kind": "verification_gap", "level": "blocking",
      "text": "No mutants executed; kill assertions, full base-vacuity analysis, and bind-loop execution coverage remain unverified. Legacy counterfactuals do not substitute for mutant kills. Live sampler skipped as instructed.",
      "needs": "Complete the execution review before treating this head as verified."
    }
  ]
}
```