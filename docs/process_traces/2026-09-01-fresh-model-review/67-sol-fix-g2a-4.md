```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the ruled v5 special-token policy loader fix; focused acceptance and all five mutations pass.",
  "workspace": {
    "base_requested": "6234dfc3",
    "base_mode": "exact",
    "head_start": "6234dfc38fef499548570ab1701278ada984e5d9",
    "head_end": "6234dfc38fef499548570ab1701278ada984e5d9",
    "upstream_end": "6234dfc38fef499548570ab1701278ada984e5d9",
    "branch": "feat/2026-09-01-g2a-probe"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "tests/test_d117_contrast_v5_pack.py",
    "tests/test_issue_g2a_prefill_prompt_pin.py",
    "tests/test_summarize_g2a_prefill_probe.py"
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
      "cmd": "python3 -m unittest tests.test_issue_g2a_prefill_prompt_pin tests.test_summarize_g2a_prefill_probe tests.test_generate_g2a_probe_inputs tests.test_d117_contrast_v5_pack tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 111 tests in 4.013s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 111 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c \"import hashlib,json,sys; sys.path.insert(0,'configs/campaigns/d117_contrast_v5'); from generate_configs import dominance_criterion_registration as r; print(hashlib.sha256(json.dumps(r(),sort_keys=True,separators=(',',':')).encode()).hexdigest()[:8])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a11"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a11$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 scripts/gen_state.py --check && echo PASS gen_state_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS gen_state_check"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS gen_state_check$"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check && echo PASS git_diff_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS git_diff_check"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS git_diff_check$"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "One pre-edit failure marker appeared before the run was interrupted.",
          "KeyboardInterrupt in tests/test_receipt_histsem.py:1386 while git update-ref was blocked."
        ]
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide M0 preflight was interrupted after an earlier unattributed failure marker and a prolonged sandbox-bound git update-ref wait; the mandated 111-test acceptance suite is green.",
      "needs": "Lead may rerun full discovery outside the managed sandbox; no round-4 acceptance work remains."
    }
  ]
}
```

## Change

| Finding | Result |
|---|---|
| Loader closed schema | Admits `special_token_policy`. |
| Loader policy validation | Requires exactly `add_special_tokens=true` with the ruled refusal string. |
| Pin fixtures | Updated with the required field. |
| Refusal coverage | Wrong policy and missing key assert exact errors. |
| Issuer/loader equality | AST test binds the loader literal to `issuer.SPECIAL_TOKEN_POLICY`. |
| Desk chain | Both former `NEEDS_SCOPE` skips removed; actual artifacts reach the loader. |

Generator diff, complete:

```diff
diff --git a/configs/campaigns/d117_contrast_v5/generate_configs.py b/configs/campaigns/d117_contrast_v5/generate_configs.py
index c4e603a3..f79da38d 100644
--- a/configs/campaigns/d117_contrast_v5/generate_configs.py
+++ b/configs/campaigns/d117_contrast_v5/generate_configs.py
@@ -853,6 +853,7 @@ def _load_prefill_prompt_pin(
         "exhausted_ladder_branch",
         "prefill_length",
         "tokenizer_json_sha256",
+        "special_token_policy",
         "prompt_text",
         "prompt_text_utf8_sha256",
         "prompt_token_ids",
@@ -866,6 +867,8 @@ def _load_prefill_prompt_pin(
         raise ValueError("prefill_prompt_pin_invalid: closed schema mismatch")
     if value["schema_version"] != "joulewise.prefill_prompt_pin.v2":
         raise ValueError("prefill_prompt_pin_invalid: unknown schema_version")
+    if value["special_token_policy"] != "add_special_tokens=true":
+        raise ValueError("prefill_prompt_pin_invalid: special_token_policy")
     if value["ladder_prompt_tokens"] != PREFILL_LADDER_PROMPT_TOKENS:
         raise ValueError("prefill_prompt_pin_invalid: ladder_prompt_tokens")
     if (
```

## Verification notes

| Mutation | Boundary observed | Result |
|---|---|---|
| Extra emitted ladder key | `PromptPinError: prompt_ladder_closed_schema_mismatch` at issuer | KILLED |
| `run_id` moved from metadata | `run_provenance_mismatch: g2a-small-p0512-r01: run_id` | KILLED |
| Probe `output_tokens` changed | A1 workload-shape equality failed | KILLED |
| Issuer policy changed to false | Loader raised `prefill_prompt_pin_invalid: special_token_policy` | KILLED |
| Loader accepted literal changed | Issuer/loader AST equality failed, false vs true | KILLED |

```text
Ran 111 tests in 4.013s
OK (skipped=1)
1c0a4a11
PASS gen_state_check
PASS git_diff_check
```

```text
 M configs/campaigns/d117_contrast_v5/generate_configs.py
 M tests/test_d117_contrast_v5_pack.py
 M tests/test_issue_g2a_prefill_prompt_pin.py
 M tests/test_summarize_g2a_prefill_probe.py
```

## Residual risk

The full repository discovery run did not complete under the managed sandbox; the exact requested acceptance suite completed cleanly.