```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "D1–D7 implemented; focused tests pass. NEEDS_RULING on the receipt contract; commits and live smoke are sandbox-blocked.",
  "workspace": {
    "base_requested": "a90ab4e8",
    "base_mode": "exact",
    "head_start": "a90ab4e893d750d26551a238ab6d5c18b8669cfe",
    "head_end": "a90ab4e893d750d26551a238ab6d5c18b8669cfe",
    "upstream_end": "fbda207f0d54538a588f0b2d3d6b880deb8773b9",
    "branch": "feat/2026-09-17-night-gate-quiet-admission"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "joulewise/night_plan_writer.py",
    "joulewise/arm_retry.py",
    "joulewise/quiet_admission.py",
    "scripts/run_night.py",
    "scripts/gen_derivation_night.py",
    "tests/test_night_gate.py",
    "tests/test_night_plan_writer.py",
    "tests/test_arm_retry.py",
    "tests/test_run_night.py",
    "tests/test_gen_derivation_night.py",
    "tests/test_quiet_admission.py",
    "tests/night_gate_fixtures/legacy_plan_v2.json",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/contracts/night_quiet_admission.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
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
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 302 tests in 52.124s",
          "",
          "OK (skipped=9)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 scripts/quick_suite.py --tier quick --workers 4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "PASS tests.test_calibration_ledger_custody seconds=46.714",
          "STALE WEIGHT tests.test_calibration_ledger_custody seconds=46.714 weight=1.080 ratio=43.25",
          "PASS tests.test_reauthor_clean seconds=38.021",
          "STALE WEIGHT tests.test_reauthor_clean seconds=38.021 weight=0.334 ratio=113.84",
          "QUICK SUMMARY tier=quick modules=153 excluded=85 failures=1 seconds=94.805 result=FAIL"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "result=PASS"}
    },
    {
      "id": "V3",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/joulewise-quiet-compile python3 -m compileall -q scripts joulewise; echo rc=$?",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "rc=0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated derivation-night wrapper region matches", "rc=0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "rc=0"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m joulewise.quiet_admission --sample-interval-s 30",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "subprocess.CalledProcessError: Command '('/usr/sbin/sysctl', '-n', 'kern.bootsessionuuid')' returned non-zero exit status 1."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "busy_cores"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from tests.test_quiet_admission import legacy_counterfactual; legacy_counterfactual()'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 2 legacy counterfactual assertions failed as expected",
          "test_low_load_busy_daemon_never_admits: load=1.2, process_busy_cores=0.9; AssertionError: 'GO' != 'REFUSED'",
          "test_finished_burst_admits_despite_high_load: load=3.7, process_busy_cores=0.02; AssertionError: 'REFUSED' != 'GO'"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "2 legacy counterfactual assertions failed as expected"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git log --oneline a90ab4e8..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/phase_2/derivation_night_runbook.md",
          " M docs/process/NIGHT_HANDBACK.md",
          " M joulewise/arm_retry.py",
          " M joulewise/night_gate.py",
          " M joulewise/night_plan_writer.py",
          " M scripts/gen_derivation_night.py",
          " M scripts/run_night.py",
          " M tests/test_arm_retry.py",
          " M tests/test_gen_derivation_night.py",
          " M tests/test_night_gate.py",
          " M tests/test_night_plan_writer.py",
          " M tests/test_run_night.py",
          "?? docs/contracts/night_quiet_admission.md",
          "?? joulewise/quiet_admission.py",
          "?? tests/night_gate_fixtures/",
          "?? tests/test_quiet_admission.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "test_quiet_admission.py"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: pack_night_go_receipt.md section 2 says night/receipt.json 'retains night_gate’s exact _RECEIPT_KEYS shape for EVERY class' and 'The night_gate receipt validator is NOT modified.' D5 requires additional v3 receipt fields and versioned validation. The contract was preserved.",
      "needs": "Rule a prospective packless-v4 exception and reconcile the lead-owned contract before adoption."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "No commits created or pushed. git add exited 128: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-gate-quiet/index.lock': Operation not permitted. All implementation remains unstaged within WRITE_SCOPE.",
      "needs": "Lead must review and create the requested stage commits using authorized Git metadata access."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Live sampler metrics are unavailable: the required boot sysctl is sandbox-denied ('sysctl: sysctl fmt -1 1024 1: Operation not permitted'). No fixture output is presented as live evidence.",
      "needs": "Run V5 in a permitted read-only environment and retain its metrics for the cold gate."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Quick tier failed in the unmodified tests.test_axi_controller_events module: two assertions expected 1 but received 2, with 'campaign start identity unavailable'. No out-of-scope repair attempted. Canonical full suite remains lead-owned.",
      "needs": "Replay the campaign identity failures in the lead environment and run the canonical suite."
    },
    {
      "id": "F5",
      "kind": "environment",
      "level": "blocking",
      "text": "Bridge scope-check reports all 16 changed paths in_scope, but returns ATTRIBUTION_INDETERMINATE / no_governing_lease for the supplied lease. Baseline digest verified; HEAD remains exactly at the requested base.",
      "needs": "Reconcile the runner's governing lease and rerun scope-check."
    },
    {
      "id": "F6",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced externally to fbda207f0d54538a588f0b2d3d6b880deb8773b9 during the run. This session performed no network operation; branch HEAD remains a90ab4e8.",
      "needs": ""
    }
  ]
}
```

## Change

Implemented explicit v4 policy, interval CPU accounting, supervised binding, receipt v3, new-plan generation, successor eligibility and documentation. No reason codes or measurement constants changed.

**NEEDS_RULING:** Approve a prospective packless-v4 exception to the universal receipt-shape clause? Options are that exception or withholding D5. I recommend the exception while preserving v2 and transaction-pack v3. Adoption remains blocked pending the lead’s ruling.

## Verification notes

Counterfactual failures were confirmed against actual base source. Regressions 1/2/5/8/10 fail because the baseline lacks binding; 7 rejects v4, 9 lacks the successor helper, and 11 rejects the flag. Regression 6 has no baseline accounting module to execute.

The original writer bytes and seven legacy receipt scenarios were also confirmed byte-identical. CPU thresholds remain provisional.