```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Freeze and arm use the collection encoder, but post-arm tokenizer drift can reach measurement before any fresh realization check.",
  "workspace": {
    "base_requested": "717b1ddb",
    "base_mode": "exact",
    "head_start": "717b1ddb9df071a70a7c7980d04f680da792b759",
    "head_end": "717b1ddb9df071a70a7c7980d04f680da792b759",
    "upstream_end": "c5fa8a495e3a0ec74fd13bc7c1dd613626cee6f6",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "No last-mile realization recheck after arm",
        "detail": "Launch and campaign paths replay the recorded arm identity evidence, but do not invoke verify_frozen_projection before collection. A post-arm dependency or tokenizer-state drift can therefore reach run_workload; bundle strict validation catches it only after sampling.",
        "recommendation": "Add a pre-writer or pre-sampling realization recheck, or explicitly rule this temporal interval outside the causal guarantee."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "review_tmp=\"$(mktemp -d '/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/causality-review.XXXXXX')\"; TMPDIR=\"$review_tmp\" PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -q tests.test_identity_pins tests.test_mlx_runtime 2>/dev/null; review_rc=$?; echo TEST_EXIT=$review_rc; exit \"$review_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "TEST_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "TEST_EXIT=0$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Freeze-to-arm drift is caught, but arm-to-collection drift is only caught post-measurement.",
      "needs": "Lead decision on adding a last-mile rederivation or accepting the narrower freeze-to-arm scope."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No real Qwen3 model load was performed, per instruction.",
      "needs": ""
    }
  ]
}
```

## Findings

| Projection chain | Collection chain |
|---|---|
| `identity_pins.py:1989-1999` → `_derive_projection_units` `:1440-1487` → `_runtime_probe_metadata` `:1287-1349` → `prepare` → `identity_projection_metadata` `mlx_runtime.py:315-348` → `_prompt_for_workload` `:940-946` → `_encode(..., add_special_tokens=True)` `:1109-1114` | `window_runbook.md:1528-1533` → `launch_window.py:274-280` → `run_campaign.py:8067-8070` → `controller.py:849-868, 912-928, 1201-1207, 1222-1276` → `run_workload` `mlx_runtime.py:377-394` → `_generate` `:689-718` → the same `_prompt_for_workload`/`_encode` path |

The prefill path is encoder-identical: raw `prompt_text`, `add_special_tokens=True`, no manual BOS, chat template, or truncation. Schema source exclusivity prevents the suite branch for expectation-bearing configs (`schemas.py:300-317`); v5 emits raw prefill configs (`generate_configs.py:1337-1350`).

The arm gate is correctly ordered for freeze→arm drift: `generate_arm_receipt` calls `_run_identity_arm_reverification` before writing the arm receipt (`arm_readiness.py:8333-8337, 8420-8447`); `verify_frozen_projection` rederives at `identity_pins.py:2170` and refuses mismatches at `:2179-2183`. The only resulting write is custody refusal evidence (`:2205-2227`), before launch or bundle creation.

F1 is the remaining causal gap. `verify_consumed_launch` replays arm semantics (`arm_readiness.py:9456-9463`), and `_replay_consumed_arm` replays recorded evidence (`:9411-9433`); neither calls `verify_frozen_projection`. Campaign preflight likewise uses `replay_arm_semantics=False` (`arm_readiness.py:10137-10144`). Collection then creates the bundle at `controller.py:331` before `runtime.prepare` (`:922`).

Collection does create a fresh adapter/tokenizer (`adapters/__init__.py:117-134`, `mlx_runtime.py:275-293`). File pin changes are caught by `:245-247`, but a changed `transformers`/`mlx_lm` behavior or tokenizer state with unchanged pinned files is not compared against the arm receipt. `transformers_version` is recorded by `prepare` (`:298-300`) but filtered out of the frozen identity probe (`identity_pins.py:1377-1388`). The post-run `BundleReader` check is therefore a late backstop, not a pre-measurement fence.

The realization row contains only `config_path` plus count/hash/domain (`identity_pins.py:1517-1561`). Tokenizer identity is bound at the surrounding unit’s `realized_stack_identity.tokenizer_identity` (`:1666-1675`, `build_stack_identity` `:311-328`). That is sufficient for current v5’s exact per-unit declared model identity, but it is not a row-level tokenizer binding.

Registration does not systematically diverge. `_v5` itself deliberately uses no tokenizer (`generate_configs.py:624-627`); it copies the issued pin IDs (`:1003-1011`) and registers their count/hash/domain (`:1344-1350`). The issuer uses `AutoTokenizer` and `_encode(..., add_special_tokens=True)` (`issue_g2a_prefill_prompt_pin.py:113-137`); MLX-LM ultimately uses the same `AutoTokenizer` (`mlx_lm/tokenizer_utils.py:614-616`). Current Qwen3 tokenizer, tokenizer-config, and special-token files are identical across both local mirrors. First real freeze should pass; if MLX realization differs, it refuses `readiness_identity_environment_dirty` at `identity_pins.py:1541-1550`, not every pack by construction.

No bypass was found: v5 successor configs carry `launch_lineage_required` (`generate_configs.py:1881-1882`), campaign preflight requires authenticated lineage, and `run_campaign.py` exposes no force/resume measurement mode. `scripts/run_night.py` and `scripts/night_gate.py` are absent; `gen_g2_phase_d.py` emits the runbook path into `launch_window.py`/`run_campaign.py`.

No downstream handler retries or auto-cleans `readiness_identity_environment_dirty`. Projection CLI returns exit 2 (`scripts/project_identity_pins.py:52-60`), and arm readiness returns refusal/NO_GO (`scripts/generate_arm_readiness.py:164-184`). Existing `tests/test_identity_pins.py::PromptRealizationProjectionTests::test_arm_reverification_refuses_each_prompt_realization_drift` covers freeze→arm drift; no existing test covers F1. The needed regression is a post-arm tokenizer mutation test asserting refusal before `RunBundleWriter.create`.

## Residual risk

No real Qwen3 load was performed. The first real freeze remains the empirical check of installed MLX-LM/Transformers behavior.