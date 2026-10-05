```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Harvest-bound SELECT issuance works; completion requires integration-test scope expansion and an end-state schema ruling.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "feat/2026-10-04-g2a-issuer-harvest-bound"
  },
  "pathspec": [
    "scripts/issue_g2a_prefill_prompt_pin.py",
    "tests/test_issue_g2a_prefill_prompt_pin.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q tests/test_issue_g2a_prefill_prompt_pin.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["21 passed, 71 subtests passed in 4.15s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "21 passed, 71 subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q tests/test_issue_g2a_prefill_prompt_pin.py tests/test_d117_contrast_v5_pack.py tests/test_d117_floor_qwen3_v5_generate.py tests/test_generate_g2a_probe_inputs.py tests/test_summarize_g2a_prefill_probe.py tests/test_custody_mode_inventory.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED tests/test_summarize_g2a_prefill_probe.py::SummarizeG2APrefillProbeTests::test_desk_chain_actual_artifacts_reach_v5_loader",
          "1 failed, 133 passed, 237 subtests passed in 72.94s (0:01:12)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^134 passed"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q tests/test_issue_g2a_prefill_prompt_pin.py tests/test_d117_contrast_v5_pack.py tests/test_d117_floor_qwen3_v5_generate.py tests/test_generate_g2a_probe_inputs.py tests/test_custody_mode_inventory.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "/opt/homebrew/Cellar/python@3.13/3.13.1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/ast.py:390: KeyboardInterrupt",
          "111 passed, 223 subtests passed in 325.56s (0:05:25)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^116 passed"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry PYTHONDONTWRITEBYTECODE=1 HF_HOME=/tmp/dd5-issuer-dry/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m scripts.issue_g2a_prefill_prompt_pin --harvest /Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/harvest.json --registration configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md --output /tmp/dd5-issuer-dry/final/prefill-prompt-pin.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ""
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-issuer-dry PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m scripts.issue_g2a_prefill_prompt_pin --end-state --recover-harvest /Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z/harvest.json --registration configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md --output /tmp/dd5-issuer-dry/final/end-state-pin.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": ["G2-a prompt pin refused: end_state_trigger_not_met"]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "^G2-a prompt pin refused: end_state_trigger_not_met$"
      }
    },
    {
      "id": "V7",
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
        "tail_regex": ""
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: generate_configs.py:115 defines the no_rung_clears_pre_registered_count_floor condition, and :776 requires that exact declaration. The brief prohibits that condition for end-state pins. Successful end-state issuance therefore refuses with end_state_schema_ruling_required.",
      "needs": "May the end-state pin retain the required static declaration as metadata, with its end-state record supplying decision authority? Options: retain the declaration (recommended), or authorize loader changes for an end-state-specific declaration."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: tests/test_summarize_g2a_prefill_probe.py:655 invokes the removed free-standing issuer CLI. The test cannot be migrated within the exhaustive allowlist; it was preserved.",
      "needs": "Authorize tests/test_summarize_g2a_prefill_probe.py."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Uncommitted: git add exited 128 because creation of the external worktree index.lock was denied with Operation not permitted. No push was attempted.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The canonical suite and later subset rerun were interrupted after the scope blocker was established; neither is reported as completed verification.",
      "needs": "Complete verification after resolving the scope and schema blockers."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_summarize_g2a_prefill_probe.py"],
    "reason": "Its existing producer-to-loader integration test invokes CLI inputs explicitly removed by this task.",
    "blocked_work": "Migration of that integration test and a passing related-module suite.",
    "minimal_change": "Wrap the test's producer artifacts in a synthetic block-3 SELECT harvest archive and invoke --harvest with --registration."
  }
}
```

## Change

Implemented strict harvest binding, archive confinement, path re-rooting, hash checks, and preserved selector, provenance, ladder, tokenizer, and pin-schema checks. End-state trigger checks and the closed evidence record are implemented; successful issuance remains gated by F1.

Block-3 proof uses the archived inventory’s exact campaign-policy path and sealed hash, window/session identity, hash-bound night plan, and authenticated chain’s policy/root literals. The plan also retains the `b3w1`/`b3w2` label. Both supplied block-2 archives refuse with `harvest_block3_binding_mismatch`. Mapping preserves source-relative suffixes exactly as the harvest’s `copytree` does; no mapping helper exists.

Dry issue:

- Exit code: `0`
- Refusal code: none
- Pin sha256: `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`
- `g2a_record_sha256`: `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`

End-state refusal: `end_state_trigger_not_met`.

## Verification notes

The out-of-scope integration failure is at [test_summarize_g2a_prefill_probe.py:655](/Users/edr/code/JouleWise-wt-dd5-issuer/tests/test_summarize_g2a_prefill_probe.py:655). The schema conflict is at [generate_configs.py:776](/Users/edr/code/JouleWise-wt-dd5-issuer/configs/campaigns/d117_contrast_v5/generate_configs.py:776).

The replay allowlist remains unchanged: its census matches exactly, with no violations. The existing project virtual environment supplied pytest; system Python lacks it.

## Residual risk

The pinned [runsheet:646](/Users/edr/code/JouleWise-wt-dd5-issuer/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:646) still documents the removed CLI and remains untouched.