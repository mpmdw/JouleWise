```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "Blocked before edits: the frozen v5 loader has no bound panel-byte hash or tokenizer source with which to implement L-F4/L-F5 authentically.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "descendant",
    "head_start": "82e7519df808fd64e28347322f92618f348dafdf",
    "head_end": "82e7519df808fd64e28347322f92618f348dafdf",
    "upstream_end": "60e6893073e202d3b8fd392a0813add3a78aca22",
    "branch": "feat/2026-09-01-g2a-probe"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.018s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 69 tests in 14.360s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "L-F4 explicitly requires comparing pin.panel_sha256 with a hash of the panel that the v5 generator itself binds. configure_model_pair loads parsed panel entries at generate_configs.py:993-995, but never hashes panel bytes; _load_prefill_prompt_pin at :813-958 receives only tokenizer_json_sha256, and its call at :1084-1088 supplies neither panel hash nor tokenizer source.",
      "needs": "Authorize a narrow configure_model_pair call-site change to hash panel_path bytes and pass that hash plus the selected tokenizer source into _load_prefill_prompt_pin, or specify another authenticated binding."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "L-F5 requires real re-tokenization, but the current loader deliberately has no tokenizer object or model source; hard-coding the local mirror would invent an unbound identity and contradict the existing no-model-mirror-read contract.",
      "needs": "Rule whether the same narrow call-site change may pass the panel-selected tokenizer source to the loader."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "git rebase main was first action. It reported the branch up to date, but Git could not create temporary locks in the parent worktree metadata because that path is read-only here. main is already an ancestor and rulings 16b/16c are present.",
      "needs": ""
    }
  ]
}
```

## Change

No files changed.

The registration golden-readback test passed before the blocked work. Its canonical registration SHA-256 is `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`.

## Verification notes

No workload-name consumer keyed to the G2-a diagnostic name was found in `joulewise/` or `scripts/`; the ruled diagnostic name may remain.

## Residual risk

Implementing the requested panel/token authenticity checks without the ruling would invent a new binding outside the allowed loader/prompt-candidate region.