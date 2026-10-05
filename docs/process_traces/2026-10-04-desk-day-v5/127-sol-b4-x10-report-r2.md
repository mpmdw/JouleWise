```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the authenticated T-0 stage cap, corrected window and stream bounds, and preserved legacy window behavior; only the known sandbox watchdog fails.",
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
    "joulewise/night_gate.py",
    "configs/campaigns/v5_qualification_25g83/sizing_allowances.json",
    "configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json",
    "tests/test_v5_qualification_plan.py",
    "tests/test_v5_block4_x10.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-sz/replay_sizing.py > /tmp/dd5-sz/x10-resume-sizing-replay.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"clean_dwell_cap_s\": 2700, \"clock\": {\"diagnostic_anchor_half_width_s\": 0.003597711938684421, \"observed_max_effective_bound\": {\"seconds\": 0.004017182870691257, \"source\": {\"path\": \"configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json\", \"sha256\": \"f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81\"}, \"source_pointer\": \"/observed_max_effective_bound_s\"}, \"rho_per_s\": 8e-06, \"source\": {\"path\": \"configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json\", \"sha256\": \"f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81\"}, \"stamp_resolution_s\": 1.0000000000000002e-06}, \"clock_admission_limit_s\": 0.005, \"clock_design_margin_s\": 0.000982817129308743, \"estimate_only\": true, \"longest_sampler_stream_s\": 335.0, \"numeric_padding_s\": 1e-06, \"observed_max_effective_clock_bound_s\": 0.004017182870691257, \"programmed_span_s\": 22494, \"t0_stage_cap_s\": 3300.0, \"window_max_s\": 25800, \"worst_case_effective_clock_bound_s\": 0.006279711938684421}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s).*\"programmed_span_s\": 22494.*\"t0_stage_cap_s\": 3300.0.*\"window_max_s\": 25800.*"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-sz/check_sizing_x10.py > /tmp/dd5-sz/x10-resume-source-check.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SOURCES_OK: 70 source-bound allowances; 67 authenticated archive timing sources; 23 configs; fixture unchanged",
          "AUTHORITY_OK: all four provenance authorities authenticated; ruling 76 includes addendum E",
          "ARITHMETIC_OK: span=22494 window=25800 latest=3306 emergency=26100 courier=26400 deadman=ceil_minute(t0+29700)",
          "GATE_OK: T_stream_max=335; stated -3.17 ppm bound=4.84570 ms margin=0.15430 ms; limit=973/268 ppm",
          "RAW_FREQUENCY_LIMIT: 237934 118967/32768"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)SOURCES_OK:.*AUTHORITY_OK:.*ARITHMETIC_OK:.*GATE_OK:.*"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_qualification_plan tests.test_v5_block4_clock tests.test_v5_block4_x6 tests.test_run_night > /tmp/dd5-sz/x10-resume-requested-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 362 tests in 281.134s",
          "FAILED (failures=1, skipped=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s).*Ran 362 tests.*OK.*"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-sz PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x10 tests.test_run_night.QualificationT0StageCapTests tests.test_night_gate > /tmp/dd5-sz/x10-resume-final-focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 125 tests in 9.570s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s).*Ran 125 tests.*OK.*"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
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
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --exit-code 280f2fec -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
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
      "level": "nonblocking",
      "text": "The requested 362-test run has one failure: BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go hit its external 8 s sandbox watchdog. Nine tests skipped. Treated as the lead-accepted addendum D.6 artifact and not chased.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Sizing remains PROVISIONAL: author/verification allocations and the approved auxiliary proxy are prospective, not live hardware guarantees. Concurrent X7 folding changes writer/gate bytes, so production provenance digests must be re-pinned after integration.",
      "needs": "Lead folds X7/X10, re-pins sizing provenance, and owns the cold final pass and live qualification gates."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Repository-wide unittest discovery was not run for this bounded qualification-tooling lane; the requested four modules, new kill-tests, and legacy night-gate checks were run.",
      "needs": "Lead includes repository-wide checks in the cold final integration pass."
    }
  ]
}
```

## Change

Implemented the source-bound 3300 s stage cap, enforced its 3180–3480 s band, and restored `T_pack_t0` to 360 s. The runner authenticates the plan’s cap before using it as the timeout; dwell admission remains 600–2700 s. The validator uses the new formula for qualifying block-4 packs and preserves legacy behavior elsewhere.

Cooldown remains wall time but is excluded from member streams, with the controller citation. Every anchored stream requires 60 s. Whole unanchored auxiliaries use `nonsampling`; cooldown and sentinel captures are nested helpers.

Both expected calculations are confirmed:

| Quantity | Result |
|---|---:|
| Span | 22,494 s |
| Window | 25,800 s |
| Latest start | t0 + 3,306 s |
| Emergency shutdown | t0 + 26,100 s |
| Courier deadline | t0 + 26,400 s |
| Dead-man | ceil-minute(t0 + 29,700 s) |

At −3.17 ppm, the frequency gate passes: **4.84570 ms**, with **0.15430 ms** margin. The absolute-frequency limit is approximately **3.630597 ppm**.

Changes remain uncommitted.

## Verification notes

The prerequisite boundary now uses **t0 − 3300**: `pack_t0` covers post-stage work and cannot represent the stage allowance. This is a conservative declared boundary; runtime independently checks controls against actual capture timestamps.

One deadline-call argument supplies verified sizing before its custody file is published. Attempt-history logic was untouched.

The requested suite’s sole failure was the accepted sandbox watchdog artifact; it was not chased. Repository-wide discovery remains for the lead’s cold integration pass.

## Residual risk

Allowances remain **PROVISIONAL**. After folding X7, re-pin writer/gate provenance before cold final verification.