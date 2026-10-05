```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Pack members were wrongly refused; normalized-config authentication is implemented and focused tests pass. Changes are uncommitted; canonical verification is incomplete.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "fix/2026-10-04-run-config-normalized-pin"
  },
  "pathspec": [
    "joulewise/window_duration_margins.py",
    "tests/test_window_duration_margins.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V0",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 35 tests in 10.189s", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 42 tests in 32.206s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 42 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_custody_mode_inventory tests.test_summarize_g2a_prefill_probe",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 25 tests in 43.344s",
          "OK",
          "PASS built G2-a prompt ladder, configs, and manifests",
          "PASS bound G2-a inputs to the calibration window"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 25 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests > /tmp/run-config-normalized-pin-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "git add -- joulewise/window_duration_margins.py tests/test_window_duration_margins.py && git commit -m 'Authenticate window margins against runner-normalized pack configs'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-runcfg/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Authenticate window margins against runner-normalized pack configs"
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Uncommitted: sandbox denied creation of the Git index lock. No push attempted.",
      "needs": "Commit the two-file diff from an environment with Git metadata write access."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical suite manually interrupted after 517 completed test markers, including three skips, with no failures reported. Interruption stack was in unrelated arm-readiness Git blob reads after more than two minutes without progress output.",
      "needs": "Complete canonical suite verification before landing."
    }
  ]
}
```

## Change

**Verdict: wrongly refused.** Floor pins originate from serialized input bytes ([generator:2143](/Users/edr/code/JouleWise-wt-dd5-runcfg/configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:2143)) and enter extraction-spec member pins ([generator:1433](/Users/edr/code/JouleWise-wt-dd5-runcfg/configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:1433)). GAMMA hashes its input bytes ([generator:2023](/Users/edr/code/JouleWise-wt-dd5-runcfg/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:2023)) and carries those hashes into `analysis_manifest_v3.json` ([generator:1507](/Users/edr/code/JouleWise-wt-dd5-runcfg/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:1507)).

The CLI parses inputs through `BenchmarkConfig.from_mapping` ([cli:292](/Users/edr/code/JouleWise-wt-dd5-runcfg/joulewise/cli.py:292)); the writer serializes `config.to_dict()` ([bundle:950](/Users/edr/code/JouleWise-wt-dd5-runcfg/joulewise/bundle.py:950)). Those default-filled bytes differ from the input pins, triggering the original reader’s `member_config_mismatch` at base line 553.

The reader now authenticates source bytes, runner-normalized bundle bytes, and the metadata hash. It reuses [controller’s hash helper](/Users/edr/code/JouleWise-wt-dd5-runcfg/joulewise/controller.py:3387); moving the summarizer wrapper is unnecessary. Regression fixtures use the real bundle writer and reject changed content even with rebound metadata.

## Verification notes

Requested module: **42 passed**. Additional custody/summarizer checks: **25 passed**. No separate recorder test module exists; CLI coverage is included in the requested module.

An early run caught an import typo, corrected before successful reruns. Canonical verification remains incomplete as recorded above. **Uncommitted** because Git metadata access was denied. No outside-scope code findings.

Next: complete the canonical suite, review, and commit the two-file diff.