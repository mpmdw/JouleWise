```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "BLOCKER: partial worker messages still freeze bind supervision. Six modules pass; 29 reconstructed mutants killed. Three missing records prevent exact disposition sign-off.",
  "workspace": {
    "base_requested": "5c5a3323",
    "base_mode": "exact",
    "head_start": "5c5a33235e4a98b87139c4567dc211cc68d7c527",
    "head_end": "5c5a33235e4a98b87139c4567dc211cc68d7c527",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file_line": "scripts/run_night.py:2024",
        "caller": "scripts/run_night.py:2114",
        "disposition": "E-F6 supervision requirement; original brief D6: 'keep census and deadline supervision responsive while a sample is in flight'; current review: 'BLOCKER = ... the bind loop can still block'.",
        "finding": "ready() establishes pipe readability, not availability of a complete message. result() then performs an unbounded recv() on the supervisor thread.",
        "experiment": "In the temporary copy, a real worker produces a schema-valid observation with a 64 KiB diagnostic. Child-only fault injection stops its sender after the message header, before the payload. Advance the injected monotonic clock beyond the sealed deadline.",
        "command": "cd /tmp/refute-delta && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest audit_partial_send.PartialSendHangTests",
        "observed": [
          "blocked_stack=[('await_task', 2114), ('result', 2024), ('recv', 260), ('_recv_bytes', 458), ('_recv', 416)]",
          "partial-message ready=True; monotonic=601; deadline=600; bind_thread_alive=True; census_progress=False",
          "AssertionError: True is not false : partial worker message blocked census and expired bind deadline",
          "FAILED (failures=1)"
        ],
        "provenance": "Also reproduced with a2671902's driver. Existing defect left uncovered by round 2, not introduced by this delta. Releasing the worker allowed expiry; the latest run confirmed driver reaping.",
        "recommendation": "Keep deadline and census supervision responsive while receiving worker messages; add a partial-message hang regression."
      }
    ],
    "disposition_basis": "Landings below are verified against the current prompt, available briefs and code. Exact comparison with the missing round-2 brief and prior reports remains blocked.",
    "disposition_table": {
      "columns": ["ID", "landed", "mutant killed", "notes"],
      "rows": [
        ["C-F1", "observed", "N/A: line inspection", "nl -ba definition<first-use: t0 13<15; GO 14<159; bind 15<70; interval 16<71; consecutive 17<72; busy-core 18<46; observer 19<27; terminal/WAIT 20<143; attribution 21<49; cutoff authority 22<31. All ten pass."],
        ["C-F2", "observed", "yes", "Disabled strict v4 checking: four failures, night_refused_boot_clock instead of night_probe_error. Cases include failed/empty, failed/UUID, successful/empty and whitespace. Leaking strict mode into v2 also fails the legacy comparison."],
        ["C-F3", "observed", "yes", "Tuple regression plus v2 journal counterexample kill restored legacy contamination: FAILED (failures=2). Separate always-quiet guard and missing v4 guard mutants also killed."],
        ["E-F1", "observed", "yes, 11/11", "Named regression kills individual exemptions for all ten daemons and arbitrary-program. Observed assertions include process_busy_cores 0 != 0.9."],
        ["E-F2", "observed", "yes", "Named regression fails both stale-percent cases: high percent/zero delta and zero percent/27 CPU-second delta. FAILED (failures=2)."],
        ["E-F3", "observed", "yes", "parse_ps pid-only identity mutant fails the named regression: 42 differs from (42, 'Thu Sep 17 19:00:00 2026')."],
        ["E-F4", "observed", "yes", "Named regression exercises downstream GO +0 and real bind GO +540; E=t0+9600, completion/courier/shutdown=t0+9900, dead-man=t0+13500. Three samples retain deadline 1600. GO-t0 rewrite fails 10440 != 9900; deadline-reset and rollback-extension mutants fail expected expiry classification."],
        ["E-F5", "observed", "yes, both", "Inside regression 9, removing predecessor-digest checking yields allowed instead of predecessor_rearm; removing history-digest checking yields allowed instead of candidate_changed."],
        ["E-F6", "partial; F1", "yes for named ready/join mutant", "Real pre-send hung worker regression passes: ready under 50 ms, census during hang, expiry and no zombie. Blocking join mutant fails the 50 ms assertion. Partial-message hang remains uncovered and blocks the supervisor."],
        ["E-F7", "observed", "yes", "Complete build_spec fixtures kill window and computed-runway bypasses. Authoring tests kill silent window extension and short-runway acceptance. Failures are GenerationRefusal not raised, not incomplete-fixture exceptions."]
      ]
    },
    "compatibility": {
      "six_module_counts_before_after": {
        "night_gate": [63, 64],
        "quiet_admission": [9, 10],
        "night_plan_writer": [10, 10],
        "arm_retry": [31, 31],
        "run_night": [157, 162],
        "gen_derivation_night": [43, 44]
      },
      "totals": "313 -> 321; both suites OK (skipped=9)",
      "legacy": "Committed v2 fixture bytes/verdict checks pass. The 24-scenario legacy receipt byte/validator comparison passes, plus three boot-probe counterexamples.",
      "top": "100.26 accepted as 0.873 idle; 99.98 accepted as 0.9128000000000001; 98.5 refused. Strict 0.1 mutant killed. Diff confirms no other parser bound moved.",
      "generator": "PASS generated derivation-night wrapper region matches"
    },
    "new_surface": [
      "night_gate.py:1282,1290,1395: strict_probe parameter, failed/empty branch and v4 call. Covered by test_v4_failed_or_empty_boot_probe_is_probe_error; false/legacy branch by legacy receipt comparison; successful v4 branch by binding tests.",
      "run_night.py:127,1525,2268: separate quiet write-once tuple, plan-sensitive selection and caller. Covered by tuple, v2 journal, v4 journal and existing rerun tests. Omitted-plan default has no dedicated new test.",
      "run_night.py:2020: explicit poll(0). Hung-worker false path covered by test_sampler_hang_cannot_block_census_or_expiry. Real ready-with-data and EOF result paths have no repository test using _BindTask; binding success tests use fake tasks. F1 covers the missing transport boundary.",
      "No new production bind-loop branch or worker helper appears in a2671902..5c5a3323; the blocking result path predates the delta.",
      "gen_derivation_night.py:925-940: typed ValueError translation, template-window validation and removal of automatic extension. Covered by missing-policy-key, malformed-v4-template, short-window/runway and successful explicit-authoring tests. Malformed JSON syntax has no dedicated new case.",
      "quiet_admission.py:118: widened sum tolerance. Both acceptance examples and the rejection example are covered by test_second_top_idle_fraction_tolerates_top_rounding_but_not_gaps.",
      "Test helpers: assert_driver_deadlines covers GO +0/+540 branches; BindClock.limit's failure branch is exercised by deadline mutants; hung-worker cleanup's blocked-thread branch is exercised by the join mutant."
    ],
    "same_signature": {
      "classes_visible_in_available_evidence": [
        "Legacy version-isolation leakage through the shared rerun tuple.",
        "Probe-failure misclassification.",
        "Definitions appearing after first use.",
        "Accounting tests missing daemon, stale-percent and parser-identity boundaries.",
        "Timing and digest tests missing actual consumer or decision paths.",
        "Supervision tests omitting production blocking paths.",
        "Generator refusal tests confounded by incomplete fixtures; authoring silently extending a window.",
        "Real-tool interface assumptions: fractional top argv and rounded CPU-percentage totals."
      ],
      "recurrence": "YES, structural. Round-1 fake-task coverage became a real pre-send hang test, but still misses blocking transport after readiness (F1). Real-tool compatibility also recurred: round-1 top argv rejection, then the bench percentage-sum rejection. Complete historical classification requires the missing refuter reports."
    },
    "evidence_directory": "/tmp/refute-delta",
    "next_step": "Lead fixes F1 and supplies the three missing records; resume exact-disposition and historical-signature review. Repository remains untouched."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 321 tests in 104.969s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/refute-delta/run_baseline.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 313 tests in 102.515s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /tmp/refute-delta && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B audit_mutants.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "\"rc\": 1"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "cd /tmp/refute-delta && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest audit_partial_send.PartialSendHangTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.468s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Absent under docs/process_traces/2026-09-17-interactive-5c919872/: 14-brief-seat-Q-fix-round-2.md, 12-refuter-contract-astra.md, 13-refuter-execution-astra.md. Requested asynchronously; unavailable at completion. Seat reports were not read.",
      "needs": "Supply these records or an authorized accessible path."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Nine census-dependent tests skipped on both heads. Live sampler intentionally not run. Fault-injection evidence is not hardware validation.",
      "needs": ""
    }
  ]
}
```