```json
{
 "schema": "claude-codex-report/v1",
 "genre": "implementation",
 "status": "blocked",
 "completion": "partial",
 "summary": "T0 stage cap and stream rules implemented; canonical plan admission is blocked by an out-of-scope legacy window validator.",
 "workspace": {
  "base_requested": "280f2fec0e38dfddeea3930b29dca356cd7e2fdc",
  "base_mode": "exact",
  "head_start": "280f2fec0e38dfddeea3930b29dca356cd7e2fdc",
  "head_end": "280f2fec0e38dfddeea3930b29dca356cd7e2fdc",
  "upstream_end": null,
  "branch": "lane/2026-10-05-b4-sizing2"
 },
 "pathspec": [
  "scripts/write_v5_qualification_plan.py",
  "scripts/run_night.py",
  "configs/campaigns/v5_qualification_25g83/sizing_allowances.json",
  "configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json",
  "tests/test_v5_qualification_plan.py",
  "tests/test_v5_block4_x10.py",
  "tests/test_run_night.py"
 ],
 "unowned_dirty": [],
 "verdict": {
  "implementation": "partial",
  "acceptance": "needs_ruling"
 },
 "verification": [
  {
   "id": "V1",
   "kind": "smoke",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-sz/replay_sizing.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "{\"clean_dwell_cap_s\": 2700, \"clock\": {\"diagnostic_anchor_half_width_s\": 0.003597711938684421, \"observed_max_effective_bound\": {\"seconds\": 0.004017182870691257, \"source\": {\"path\": \"configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json\", \"sha256\": \"d714ee856809e6cd3ee2a68fc73631f2b1433bb670d075af40c57842cbdd9239\"}, \"source_pointer\": \"/observed_max_effective_bound_s\"}, \"rho_per_s\": 8e-06, \"source\": {\"path\": \"configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json\", \"sha256\": \"d714ee856809e6cd3ee2a68fc73631f2b1433bb670d075af40c57842cbdd9239\"}, \"stamp_resolution_s\": 1.0000000000000002e-06}, \"clock_admission_limit_s\": 0.005, \"clock_design_margin_s\": 0.000982817129308743, \"estimate_only\": true, \"longest_sampler_stream_s\": 335.0, \"numeric_padding_s\": 1e-06, \"observed_max_effective_clock_bound_s\": 0.004017182870691257, \"programmed_span_s\": 22494, \"t0_stage_cap_s\": 3300.0, \"window_max_s\": 25800, \"worst_case_effective_clock_bound_s\": 0.006279711938684421}"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s).*\"programmed_span_s\": 22494.*\"window_max_s\": 25800.*"
   }
  },
  {
   "id": "V2",
   "kind": "suite",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_qualification_plan.SizingTests tests.test_v5_block4_x10 tests.test_run_night.QualificationT0StageCapTests",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["Ran 28 tests in 5.023s", "OK"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s).*OK"
   }
  },
  {
   "id": "V3",
   "kind": "inspection",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-sz/check_sizing_x10.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "SOURCES_OK: 70 source-bound allowances; 67 authenticated archive timing sources; 23 configs; fixture unchanged",
     "ARITHMETIC_OK: span=22494 window=25800 latest=3306 emergency=26100 courier=26400 deadman=ceil_minute(t0+29700)",
     "GATE_OK: T_stream_max=335; stated -3.17 ppm bound=4.84570 ms margin=0.15430 ms; limit=973/268 ppm",
     "RAW_FREQUENCY_LIMIT: 237934 118967/32768"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s)SOURCES_OK:.*ARITHMETIC_OK:.*GATE_OK:.*"
   }
  },
  {
   "id": "V4",
   "kind": "suite",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_qualification_plan tests.test_v5_block4_clock tests.test_v5_block4_x6 tests.test_run_night",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": [
     "Ran 357 tests in 338.118s",
     "FAILED (failures=9, errors=15, skipped=9)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s).*OK"
   }
  },
  {
   "id": "V5",
   "kind": "suite",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_qualification_plan tests.test_v5_block4_clock tests.test_v5_block4_x6",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": [
     "Ran 79 tests in 38.683s",
     "FAILED (failures=2, errors=15)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s).*OK"
   }
  },
  {
   "id": "V6",
   "kind": "test",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests.test_startup_hang_is_nonblocking tests.test_run_night.NightProbeTests.test_supervised_probe_success_and_refusal_with_fixture_census",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": ["Ran 2 tests in 16.448s", "FAILED (failures=1)"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s).*OK"
   }
  },
  {
   "id": "V7",
   "kind": "test",
   "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests.test_startup_hang_is_nonblocking tests.test_run_night.NightProbeTests.test_supervised_probe_success_and_refusal_with_fixture_census",
   "cwd": "/tmp/dd5-sz/main-baseline",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": ["Ran 2 tests in 14.597s", "FAILED (failures=1)"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?s).*OK"
   }
  },
  {
   "id": "V8",
   "kind": "inspection",
   "cmd": "git diff --check; git diff --exit-code 280f2fec -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": []
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": ".*"
   }
  }
 ],
 "flags": [
  {
   "id": "F1",
   "kind": "scope_deviation",
   "level": "blocking",
   "text": "joulewise/night_gate.py:1192 still requires window=ceil_minute(span+2700), rejecting the new source-bound stage window. It was not modified. All 17 failures/errors in the final 79-test plan/clock rerun reach this legacy gate.",
   "needs": "Expand scope to joulewise/night_gate.py or have its owner update the canonical window validator, then rerun the requested suites."
  },
  {
   "id": "F2",
   "kind": "environment",
   "level": "nonblocking",
   "text": "The 357-test requested run also had six supervisor watchdog failures and one probe failure. The probe passes serially; startup_hang reproduces serially on current code and archived origin/main e7d13a1706d6352e0b3d9624dcf4c897671393da in this sandbox.",
   "needs": "Lead replays the remaining watchdog cases serially outside the sandbox under ruling 76 addendum D.6."
  }
 ],
 "scope_expansion": {
  "requested_paths": ["joulewise/night_gate.py"],
  "reason": "Canonical plan admission hard-codes the superseded 2700 s addition. The exhaustive allowlist excludes this required validator.",
  "blocked_work": "Unmocked qualification plan publication and a green requested end-to-end suite.",
  "minimal_change": "Derive the canonical window from the authenticated t0_stage_cap instead of 2700; wire the bound cap through initial writer staging as needed."
 }
}
```

## Change

Implemented the source-bound 3300 s stage cap, restored `pack_t0` to 360 s, and made capture timeout use the authenticated plan cap. The dwell check remains 600–2700 s.

Cooldown is excluded from main-stream coverage. Every anchor-bearing stream requires ≥60 s. `nonsampling` identifies whole unanchored auxiliary stages; cooldown and sentinel helpers have no separate anchor-bearing roster entry.

The prerequisite comparison means “controls expired before stage start,” so it now subtracts the stage cap. The driver separately checks actual capture ordering.

Both expected calculations are correct:

| Quantity | Result |
|---|---:|
| Span | 22494 s |
| Window | 25800 s |
| Latest chain start | t0 + 3306 s |
| Emergency | t0 + 26100 s |
| Courier | t0 + 26400 s |
| Dead-man | ceil-to-minute(t0 + 29700 s) |

At −3.17 ppm: **4.84570 ms ≤ 5 ms**, margin **0.15430 ms**; maximum mathematical |f| ≈ **3.630597 ppm**.

Changes remain uncommitted; nothing was pushed.

## Verification notes

The full run preceded the final fixture update. Its plan/clock portion was rerun; all 17 remaining failures/errors hit the out-of-scope legacy window validator. One focused contract test isolates that validator while exercising real sizing authentication and capture.

The canonical suite was omitted for this bounded qualification-tooling change; the requested modules and focused kill-tests were run.

Next step: expand scope to `joulewise/night_gate.py` or assign its validator fix to its owner, then rerun the requested suites.

## Residual risk

Sizing remains PROVISIONAL. Auxiliary timing uses the approved small-model proxy; cold-seal and live qualification remain lead-owned.