```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Writer capture digests and approved public metadata retention implemented; verification completed with baseline sandbox failures; Git prevented committing.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "exact",
    "head_start": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "head_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "upstream_end": null,
    "branch": "feat/2026-09-28-raw-capture-digest"
  },
  "pathspec": [
    "joulewise/controller.py",
    "tests/test_controller_raw_capture_digest.py",
    "joulewise/publication_privacy.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -m unittest tests.test_controller_raw_capture_digest tests.test_publication_privacy tests.test_package_bundle_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 4.250s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B /tmp/a129-resumed-checks/run_compatibility.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["METADATA SUMMARY modules=50 passed=48 failed=2"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "METADATA SUMMARY modules=50 passed=50 failed=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -m unittest tests.test_axi_controller_events tests.test_axi_mock_spec",
      "cwd": "/tmp/a129-baseline-git",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 18 tests in 12.711s", "FAILED (failures=4)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=4\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -m unittest tests.test_controller_raw_capture_digest",
      "cwd": "/tmp/a129-counterfactual-_1yiug40",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 5 tests in 0.181s", "FAILED (failures=1, errors=4)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1, errors=4\\)"
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
      "kind": "other",
      "cmd": "git commit -m 'A129 RAW-CAPTURE-DIGEST-01 (writer half): record raw capture hashes and sizes'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-rawdigest-opus0928/index.lock': Operation not permitted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "A129 RAW-CAPTURE-DIGEST-01"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -c 'import json,os; from pathlib import Path; out=Path(\"/tmp/a129-resumed-checks\"); state=json.loads((out/\"runner_pids.json\").read_text()); assert state[\"finished\"] and not state[\"children\"], state; print(\"RUNNER STATE finished=true children=0\");\nfor pid,group in ((36922,False),(58572,True)):\n    try: (os.killpg if group else os.kill)(pid,0)\n    except ProcessLookupError: pass\n    else: raise AssertionError(\"runner remains live: \"+str(pid))\nprint(\"RUNNER CLEANUP supervisor=absent final-worker-group=absent\"); assert not (out/\"blocked_sampler_attempts.log\").exists(); print(\"REAL SAMPLER ATTEMPTS 0\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RUNNER STATE finished=true children=0",
          "RUNNER CLEANUP supervisor=absent final-worker-group=absent",
          "REAL SAMPLER ATTEMPTS 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REAL SAMPLER ATTEMPTS 0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "SANDBOX-ONLY: four AXI campaign tests fail with campaign start identity unavailable, identically reproduced at unchanged base 9eab16f8. Process census, pgrep and sysctl probes are sandbox-restricted. No new-key validator rejection remains.",
      "needs": "Lead rerun the four AXI tests outside the sandbox."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Both staging and committing failed because the shared Git index.lock is outside writable roots. Changes remain uncommitted as explicitly permitted; nothing was pushed.",
      "needs": "Lead stage and commit the three authorized files using the requested prefix."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The earlier touched-suite attempt encountered a test_evidence_night driver_python mismatch also reproduced on unchanged base. A successful canonical full-suite run is not claimed.",
      "needs": "Lead complete canonical suite verification."
    }
  ]
}
```

## Change

The controller hashes every file in the adapter-owned raw capture directory immediately before writing metadata, recording SHA-256 and byte length. Tests cover timing, nested and empty captures, failure paths, and post-write byte tampering.

The approved privacy classification accepts and retains the map in public metadata. Reader and estimator behavior remain unchanged.

## Verification notes

The counterfactual removed only the metadata assignment and produced the expected RED result. All 50 compatibility modules executed; four baseline sandbox failures remain.

Runner cleanup passed. Git blocked the commit, so the three authorized changes remain uncommitted.