```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "F1, F2 and F4 implemented; requested and expanded tests passed; canonical verification remains incomplete.",
  "workspace": {
    "base_requested": "33b68dfd",
    "base_mode": "exact",
    "head_start": "33b68dfd11cd1f7b37b8b7b3006919105423ca2d",
    "head_end": "33b68dfd11cd1f7b37b8b7b3006919105423ca2d",
    "upstream_end": "33b68dfd11cd1f7b37b8b7b3006919105423ca2d",
    "branch": "fix/2026-10-05-detokenizer-outside-prefill"
  },
  "pathspec": [
    "joulewise/adapters/mlx_runtime.py",
    "tests/test_mlx_runtime_detokenizer.py",
    "tests/test_suite_control_parity.py"
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
      "cmd": "TMPDIR=/tmp/dd5-detok2 PYTHONDONTWRITEBYTECODE=1 python3 -c 'import glob, sys, unittest; patterns = [\"tests/test_mlx_runtime*.py\", \"tests/test_adapter*.py\", \"tests/test_suite_control_parity.py\", \"tests/test_identity_pins*.py\", \"tests/test_determinism_gate*.py\"]; paths = sorted({path for pattern in patterns for path in glob.glob(pattern)}); suite = unittest.TestSuite(unittest.defaultTestLoader.discover(\"tests\", pattern=path.rsplit(\"/\", 1)[-1]) for path in paths); print(\"Selected files:\", \", \".join(paths), flush=True); result = unittest.TextTestRunner(verbosity=1).run(suite); sys.exit(not result.wasSuccessful())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-detok2 PYTHONDONTWRITEBYTECODE=1 python3 -c 'import glob, sys, unittest; patterns = [\"tests/test_mlx_runtime*.py\", \"tests/test_adapter*.py\", \"tests/test_suite_control_parity.py\", \"tests/test_identity_pins*.py\", \"tests/test_determinism_gate*.py\", \"tests/test_controller.py\", \"tests/test_cli.py\", \"tests/test_cli_run.py\", \"tests/test_nvidia_node_integration.py\", \"tests/test_mock_adapters.py\", \"tests/test_run_campaign.py\"]; paths = sorted({path for pattern in patterns for path in glob.glob(pattern)}); suite = unittest.TestSuite(unittest.defaultTestLoader.discover(\"tests\", pattern=path.rsplit(\"/\", 1)[-1]) for path in paths); print(\"Selected files:\", \", \".join(paths), flush=True); result = unittest.TextTestRunner(verbosity=1).run(suite); sys.exit(not result.wasSuccessful())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-detok2 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK(?: \\(skipped=\\d+\\))?"
      }
    },
    {
      "id": "V4",
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
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n 'workload_provenance.*generator|\\[.generator.\\]|get\\(.generator.|\"generator\":|\\x27generator\\x27:' tests joulewise",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_determinism_gate.py:47:    \"metadata.workload_provenance.generator\",",
          "tests/test_determinism_gate.py:351:                \"metadata.workload_provenance.generator\","
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "metadata\\.workload_provenance\\.generator"
      }
    }
  ],
  "flags": [
    {
      "id": "VG1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Canonical suite was interrupted after its log stopped advancing for several minutes. The traceback was in tests/test_arm_readiness_evidence_author.py:1474, test_authored_evidence_makes_synthetic_pack_freeze_pass, while arm_readiness._run_git was spawning Git through subprocess._fork_exec. No canonical pass is claimed.",
      "needs": "Lead completes canonical verification; first isolate test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_authored_evidence_makes_synthetic_pack_freeze_pass."
    },
    {
      "id": "VG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Both passing suites skipped the retained-corpus determinism acceptance test because runs/ is absent.",
      "needs": "Lead retains the corpus acceptance gate as unverified."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Determinism gate still ignores the detokenizer path, as instructed.",
      "needs": "Lead records F3."
    }
  ]
}
```

## Change

Preserved the original wrapper class in tokenizer identity, with exact record and byte-equality tests across parent, optimized and fallback behavior. Updated the strict generator pin and guarded construction failures with recorded fallback reasons.

Only the three allowed files changed. Changes remain uncommitted; nothing was pushed.

## Verification notes

Requested set: **138 tests passed**. Expanded consumer set: **653 tests passed**. Both had one retained-corpus skip. `unittest` was used because `pytest` is unavailable.

Canonical verification remains incomplete; its interrupt traceback is in [full-suite.log](/tmp/dd5-detok2/full-suite.log). Lead should isolate the named readiness test, complete canonical verification, then perform the fresh cold pass.

## Residual risk

F3 is unchanged and remains lead-owned.