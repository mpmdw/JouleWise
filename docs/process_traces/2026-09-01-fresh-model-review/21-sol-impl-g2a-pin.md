```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented and tested the authenticated G2-a probe summarizer and runtime-verified prefill prompt-pin issuer.",
  "workspace": {
    "base_requested": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "base_mode": "exact",
    "head_start": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "head_end": "bc19bfb6501f5b0dc88f23091e3e3d48865678a5",
    "upstream_end": null,
    "branch": "feat/2026-09-01-g2a-pin"
  },
  "pathspec": [
    "scripts/summarize_g2a_prefill_probe.py",
    "scripts/issue_g2a_prefill_prompt_pin.py",
    "tests/test_summarize_g2a_prefill_probe.py",
    "tests/test_issue_g2a_prefill_prompt_pin.py",
    "tests/fixtures/g2a/pin/**"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_select_g2a_prefill_length tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 40 tests in 1.830s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 40 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python3 -c 'from scripts.issue_g2a_prefill_prompt_pin import runtime_prompt_token_ids; ids=runtime_prompt_token_ids(\"The plan remains easy to audit.\", tokenizer_json_sha256=\"aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4\"); print(len(ids)); print(ids)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "7",
          "[785, 3119, 8458, 4135, 311, 24275, 13]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7\\n\\[785, 3119, 8458, 4135, 311, 24275, 13\\]"
      }
    }
  ],
  "flags": []
}
```

## Change

The probe summarizer—the tool that converts each member’s overlap count into the selector’s four length rows—now verifies the inventory’s bound files, all eight manifests, every configuration hash and run identity, exact stage coverage, member floors, and each required `summary_metrics.json` value.

The prompt pin—the exact prompt record consumed by `_v5`—now re-derives the selection from the summary, handles both selected rungs and the ruled 4096 no-clear branch, uses the local Qwen3 tokenizer through the MLX runtime’s raw-text encoding path, and refuses any text, token, hash, floor, length, or selection mismatch.

Fixture coverage includes all 24 ruled probe members and proves that issued selected and no-clear pins are accepted by `_load_prefill_prompt_pin` through `configure_model_pair`.