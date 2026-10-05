```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Launcher recheck implemented and focused regressions pass; driver start-marker ordering requires scope expansion.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "feat/2026-10-04-launch-realization-recheck"
  },
  "pathspec": [
    "scripts/launch_window.py",
    "tests/test_launch_window.py",
    "tests/test_launch_window_realization_recheck.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_launch_window.LaunchWindowEntrypointTests tests.test_launch_window.OperatorConfirmationDigestCliTests tests.test_launch_window.PackNightLaunchBoundaryTests tests.test_launch_window_realization_recheck > /tmp/dd5-a6/launch-focused.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 39 tests in 39.958s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_identity_pins > /tmp/dd5-a6/identity-tests.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 42 tests in 27.591s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_launcher_argv_regression tests.test_window_env_allowlist tests.test_gen_g2_phase_d tests.test_custody_mode_inventory > /tmp/dd5-a6/importers.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 24 tests in 335.240s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY' > /tmp/dd5-a6/night-tests.log 2>&1\nimport pathlib, unittest\nmodules = ['tests.' + p.stem for p in sorted(pathlib.Path('tests').glob('test_run_night*.py'))]\nresult = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromNames(modules))\nraise SystemExit(not result.wasSuccessful())\nPY",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 264 tests in 358.362s", "FAILED (failures=20, errors=4, skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_launch_window > /tmp/dd5-a6/launch.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY' > /tmp/dd5-a6/arm-tests.log 2>&1\nimport pathlib, unittest\nmodules = ['tests.' + p.stem for p in sorted(pathlib.Path('tests').glob('test_arm_readiness*.py'))]\nresult = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromNames(modules))\nraise SystemExit(not result.wasSuccessful())\nPY",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -B /tmp/dd5-a6/check_driver_marker.py > /tmp/dd5-a6/driver-marker.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: BLOCKED: run_night._claim_chain_start creates chain.started before launcher recheck; the marker survives readiness_identity_environment_dirty refusal"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "other",
      "cmd": "TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6/measure_launch_recheck.py > /tmp/dd5-a6/latency.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible."]
      },
      "expected": {"exit_code": 0, "tail_regex": "warm_median_ms"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V10",
      "kind": "other",
      "cmd": "git -c maintenance.auto=false -c gc.auto=0 -c maintenance.autoDetach=false -c gc.autoDetach=false add -- scripts/launch_window.py tests/test_launch_window.py tests/test_launch_window_realization_recheck.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-a6/index.lock': Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Required driver ordering change is outside WRITE_SCOPE. No out-of-scope edits were made. Direct launcher refusals leave no marker, but the actual driver creates chain.started before invoking the launcher.",
      "needs": "Expand scope prospectively to scripts/run_night.py."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Full launch and arm/readiness batches were interrupted during existing Git/evidence replay at the scope handoff; completion is unverified. The night-driver batch completed with 20 failures and 4 errors, including missing process-fixture ACKs reproduced in isolation.",
      "needs": "Complete the requested focused checks and disposition night-driver failures after scope resolution."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Real projection derivation could not initialize Metal in this sandbox. The 2050.293 ms initialization refusal is not a valid recheck latency measurement.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox rejected Git index.lock creation. Changes remain uncommitted; nothing was pushed.",
      "needs": ""
    },
    {
      "id": "F5",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Lead-owned independent review and launch-path review gates remain outstanding.",
      "needs": "Perform final review and required gates before landing."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["scripts/run_night.py"],
    "reason": "The driver publishes chain.started before spawning the pack launcher, making ruled regression (2) impossible to satisfy through launcher-only changes.",
    "blocked_work": "End-to-end no-chain.started refusal behavior and A6 closure.",
    "minimal_change": "Coordinate successful pack-launch recheck with driver start-marker publication while preserving once-only launch and liveness behavior; add the driver regression in the already authorized test module."
  }
}
```

## Change

Added the recheck immediately after consumed-arm replay using existing derivation helpers. Drift refuses before exec and bundle creation.

Physical pack launches—including pack-bound rehearsal, G2-b, and claims—reach it. DIAGNOSTIC_NO_PACK keeps its direct chain route; REHEARSAL_STUB keeps its rehearsal behavior. Lifecycle callbacks remain unchanged.

## Verification notes

Regressions use synthetic runtime and ARM inputs with real projection derivation, file hashing, and bundle creation. The four pinned estimator files remain unchanged.

Broader verification is incomplete as recorded above. Real latency was unavailable because Metal initialization failed. All launched test commands have ended.

## Residual risk

A6 remains open: the driver creates `chain.started` before the launcher can refuse. The next exact step is a prospective scope grant for the driver ordering fix.