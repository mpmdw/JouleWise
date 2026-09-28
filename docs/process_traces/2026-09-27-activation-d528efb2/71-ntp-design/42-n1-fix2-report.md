```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Implemented fix round 2; live process acceptance remains pending on a host that can list processes.",
  "workspace": {
    "base_requested": "3ad82b43",
    "base_mode": "exact",
    "head_start": "3ad82b436e2a44d6e6178b914c66b8684dc9f6ab",
    "head_end": "3ad82b436e2a44d6e6178b914c66b8684dc9f6ab",
    "upstream_end": "3ad82b436e2a44d6e6178b914c66b8684dc9f6ab",
    "branch": "feat/2026-09-28-ntp-n1"
  },
  "pathspec": [
    "joulewise/network_time_window.py",
    "scripts/run_night.py",
    "tests/test_launch_window.py",
    "tests/test_network_time_window.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_network_time_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 48 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_night_gate tests.test_arm_retry",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["test_night_gate: 104 passed", "test_arm_retry: 37 passed"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 277 tests", "FAILED (failures=35, skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_launch_window",
      "cwd": ".",
      "observed": {"result": "not_run", "exit_code": 130, "tail": ["KeyboardInterrupt in test_real_minted_v4_go_binds_root_and_refuses_content_change"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B -m unittest tests.test_launch_window.LaunchWindowEntrypointTests tests.test_launch_window.OperatorConfirmationDigestCliTests tests.test_launch_window.CeremonySkipConsumerTests tests.test_launch_window.PackNightGoRefusalHandlerTests tests.test_launch_window.PackNightLaunchBoundaryTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 36 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B /tmp/jw-ntp-round2-old/replay.py tests.test_run_night.NightDriverTests.test_wrong_off_and_failed_immediate_on_recover_from_never_launched_claim tests.test_run_night.NightDriverTests.test_unsavable_off_and_failed_immediate_on_recover_from_never_launched_claim tests.test_network_time_window.WindowTests.test_empty_start_claim_without_exit_record_still_refuses tests.test_network_time_window.WindowTests.test_empty_start_claim_with_exit_record_still_refuses tests.test_network_time_window.WindowTests.test_witness_category_is_fixed_to_process_field tests.test_run_night.NightDriverTests.test_production_sampler_builder_matches_closed_name_list",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 6 tests", "FAILED (failures=8)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=8\\)"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard:. /opt/homebrew/bin/python3 -B /tmp/jw-ntp-round2-old/replay_d2_deleted.py tests.test_run_night.NightDriverTests.test_wrong_off_and_failed_immediate_on_recover_from_never_launched_claim",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: 'chain_unproved' != 'restored'", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The 14 new live process tests report NOT RUN because this sandbox denies /bin/ps and /usr/bin/pgrep. Their old revision assertion results and the specified live red by deletion runs remain unverified.",
      "needs": "Lead runs T1–T9, the same group control, and their live deletion cases on a process capable host against 3ad82b43 and this diff."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The full launch window module stalled in its arm subprocess; a second arm test also stalled. The third test in that class was not run. The other 36 launch tests passed.",
      "needs": "Lead reruns the full scoped modules outside the sandbox."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Besides the 14 explicit NOT RUN cases, test_run_night had 21 failures in bind supervision, a quiet worker, and two CLI tests. Same environment baseline equivalence was not established.",
      "needs": "Lead compares these failures with 3ad82b43 in the same process capable environment."
    }
  ]
}
```

## Change

- **D1, C1–C6:** [run_night.py](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/scripts/run_night.py:3328) now runs registered cleanup before a bounded P1/P2/P3 proof. The process sweep has a replaceable seam at line 3751 and records the failed check, including matching PIDs and commands. The driver proves absence again before ON, records `night_chain_alive` on failure, keeps the marker, and returns `EXIT_REFUSED`. All three recovery calls inject the proof. [network_time_window.py](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/joulewise/network_time_window.py:96) saves the written and resolved night paths before OFF; recovery requires injected proof for a known group.
- **D2:** [run_night.py](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/scripts/run_night.py:607) writes a complete never launched claim after the immediate ON attempt and before `chain.exited`. [Recovery](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/joulewise/network_time_window.py:352) accepts only the ruled claim and exit record combination. An unreadable start claim returns `chain_unproved`; `marker_invalid` is reserved for the marker.
- **D3:** The [category matcher](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/joulewise/network_time_window.py:40) now reads `timed` and its category by position. All three payload attacks are unattested. The preserved logs still match **2,040** and **90** data lines.
- **D4:** The saved stand-in F1 test was replaced by the real child T1 regression in [test_run_night.py](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/tests/test_run_night.py:1145). ON stand-ins used by the new tests return `{"exit_code": 0}`. The synthetic launch fixture also injects the proof seam in [test_launch_window.py](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/tests/test_launch_window.py:2253).

| Regression | Counterfactual input and production call site | Result on `3ad82b43` |
|---|---|---|
| T1–T3 | Journaled child, unjournaled child, and neutral sampler named child outside night paths; `run_night → _run_chain_once → C2` | **Not run:** process listing denied here. Tests fail visibly with `NOT RUN`. |
| T4 | Agent census stop and deadline stop with a detached child; `_run_chain_once → _terminate_process_group → C2` | **Not run:** same gate. |
| T5–T6 | Ended chain claim and marker beside a detached child; recovery from `run_night` and both `dead_man` calls | **Not run:** same gate. |
| T7–T9 | Sweep timeout, nonzero status, malformed row; own command line path; clean chain control, through C1/C2 | **Not run:** same gate. T9 is specified to pass on both revisions. |
| T10 | Production `power_argv()` text against the closed sampler list and matcher | **Failed by assertion**: the list is absent on the old revision. |
| D2 | Wrong OFF output or unsavable OFF receipt, failed immediate ON, then recovery through the real driver with injected commands | **Failed by assertion** twice: old recovery returned `marker_invalid`, not `restored`. |
| D2 unknown claim | Empty start claim with and without a `launch_failed` exit record; `recover_network_time` | **Failed by assertion** twice: old recovery returned `marker_invalid`, not `chain_unproved`. |
| D3 | Three text category lines with a fake `timed/data` pair in the payload; `capture_verdict` | **Failed by assertion** three times: old code returned `clean`. The real log counts were unchanged. |

## Verification notes

Temporary copies made with `git show`, without Git writes, showed **P1, P2, P3, C5, and the D2 claim writer each turning a named direct regression red by assertion when deleted**. The specified *live child* deletion cases could not run here. All five modified files pass `git diff --check`; HEAD remains `3ad82b43`.

The exact live tests awaiting the lead’s run are `test_journaled_detached_capture_blocks_query_and_on`, `test_unjournaled_detached_capture_blocks_query_and_on`, `test_sampler_named_detached_capture_outside_night_blocks_query_and_on`, `test_journaled_detached_capture_without_path_signature_blocks_by_registry`, `test_same_group_live_child_blocks_query_and_on`, `test_census_stop_with_detached_child_blocks_query_and_on`, `test_deadline_stop_with_detached_child_blocks_query_and_on`, `test_recovery_from_run_night_waits_for_detached_child_then_restores`, `test_dead_man_both_recovery_calls_withhold_on_while_child_lives`, the three `test_sweep_*_refuses_before_query_and_on` cases, `test_clean_chain_runs_off_query_on`, and `test_sweep_excludes_its_own_matching_command_row`.

No stop condition was established. No `NEEDS_SCOPE` or `NEEDS_RULING` is requested.