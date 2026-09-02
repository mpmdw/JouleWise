```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Both G2-a rounds are clean: round 3’s policy/provenance chain is covered, and round 4 correctly admits and strictly validates the policy.",
  "workspace": {
    "base_requested": "6234dfc38fef499548570ab1701278ada984e5d9",
    "base_mode": "exact",
    "head_start": "af067c6033ca7d4f18acc3742c3a6eda3b8ffd97",
    "head_end": "af067c6033ca7d4f18acc3742c3a6eda3b8ffd97",
    "upstream_end": "af067c6033ca7d4f18acc3742c3a6eda3b8ffd97",
    "branch": "feat/2026-09-01-g2a-probe"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff 6234dfc3..af067c60; git diff 6234dfc3~1..6234dfc3 --stat",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Round-4 generate_configs diff has only the _load_prefill_prompt_pin hunk."]},
      "expected": {"exit_code": 0, "tail_regex": "_load_prefill_prompt_pin"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "grep -rn \"skipTest\\|NEEDS_SCOPE\" tests/test_issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py tests/test_d117_contrast_v5_pack.py tests/test_generate_g2a_probe_inputs.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_issue_g2a_prefill_prompt_pin tests.test_summarize_g2a_prefill_probe tests.test_select_g2a_prefill_length tests.test_generate_g2a_probe_inputs 2>&1 | tail -3",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["All seven one-at-a-time mutations produced FAILED output."]},
      "expected": {"exit_code": 0, "tail_regex": "FAILED"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_issue_g2a_prefill_prompt_pin tests.test_summarize_g2a_prefill_probe tests.test_select_g2a_prefill_length tests.test_generate_g2a_probe_inputs tests.test_gen_state 2>&1 | tail -5",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 119 tests in 4.381s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -c \"import hashlib,json,sys; sys.path.insert(0,'configs/campaigns/d117_contrast_v5'); from generate_configs import dominance_criterion_registration as r; print(hashlib.sha256(json.dumps(r(),sort_keys=True,separators=(',',':')).encode()).hexdigest()[:8])\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["1c0a4a11"]},
      "expected": {"exit_code": 0, "tail_regex": "^1c0a4a11$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --exit-code && git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The scratch worktree's linked Git index is not writable, so git checkout -- <path> could not create index.lock. Each authorized mutation was instead restored immediately by its exact reverse patch; final diff and status are empty.",
      "needs": ""
    }
  ]
}
```

## Findings

None.

Round 3: CLEAN. The issuer emits the policy from the single `SPECIAL_TOKEN_POLICY` constant, includes it in `PROMPT_PIN_KEYS`, and validates the completed pin through `_validate_pin`. The summarizer now reads `run_id` and workload provenance from retained-shape `metadata.json`, not a hand-shaped summary; the runsheet invokes the actual selection → issuer → `_v5` loader chain.

Round 4: CLEAN. Its three production-line changes are entirely within `_load_prefill_prompt_pin`: admit `special_token_policy` in the closed key set and reject every non-`add_special_tokens=true` value with the required exact error. All `NEEDS_SCOPE`/`skipTest` occurrences are gone; the sole suite skip is the optional real-tokenizer test.

| Row | Result | Detection |
|---|---|---|
| (i) extra ladder key | KILLED | `test_desk_chain_actual_artifacts_reach_v5_loader`: issuer `prompt_ladder_closed_schema_mismatch` |
| (ii) remove metadata `run_id` | KILLED | same desk-chain test: `run_provenance_mismatch: ...: run_id` |
| (iii) workload shape field | KILLED | `test_probe_workload_shape_matches_v5_prefill_except_diagnostic_name` |
| (iv) issuer emits `false` | KILLED | desk-chain loader: `prefill_prompt_pin_invalid: special_token_policy` |
| (v) loader string changed | KILLED | `test_issuer_special_token_policy_matches_v5_loader_accepted_value` |
| (vi) delete loader validation | KILLED | `test_prefill_prompt_pin_special_token_policy_refusals_are_exact` (plus equality test) |
| (vii) remove loader closed-key entry | KILLED | `test_issued_selected_and_no_clear_pins_are_accepted_by_v5_loader`: closed-schema mismatch |

## Residual risk

The optional real-Qwen3-tokenizer test remains unavailable in this environment; all desk-chain and mutation coverage passed.

`git status --short`: *(empty)*