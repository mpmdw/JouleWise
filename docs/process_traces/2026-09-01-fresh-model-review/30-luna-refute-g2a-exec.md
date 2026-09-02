```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Replay refutes the chain: the summarizer accepts forged output identities, the issuer accepts a mutated panel fingerprint, the loader accepts hash-rebound pin edits, and the runsheet cannot reach the issuer.",
  "workspace": {
    "base_requested": "feat/2026-09-01-g2a-probe @ d26e0472",
    "base_mode": "exact",
    "head_start": "d26e0472b1bdceda3129f7fbb0a4e7beb9f603c3",
    "head_end": "d26e0472b1bdceda3129f7fbb0a4e7beb9f603c3",
    "upstream_end": "d26e0472b1bdceda3129f7fbb0a4e7beb9f603c3",
    "branch": "feat/2026-09-01-g2a-probe (detached HEAD)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REFUTE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "Summarizer accepts a summary_metrics.json run_id that is not in the inventory.",
        "refs": ["scripts/summarize_g2a_prefill_probe.py:248-255", "scripts/summarize_g2a_prefill_probe.py:367-369"]
      },
      {
        "id": "F2",
        "severity": "blocker",
        "summary": "Summarizer accepts a summary_metrics.json config_sha256 that disagrees with the inventory.",
        "refs": ["scripts/summarize_g2a_prefill_probe.py:248-255", "scripts/summarize_g2a_prefill_probe.py:367-369"]
      },
      {
        "id": "F3",
        "severity": "blocker",
        "summary": "A below-floor small-member rung is hard-refused and never represented in the four-row summary.",
        "refs": ["scripts/summarize_g2a_prefill_probe.py:303-305", "scripts/summarize_g2a_prefill_probe.py:404-405"]
      },
      {
        "id": "F4",
        "severity": "blocker",
        "summary": "Issuer accepts a ladder whose panel fingerprint was replaced with zeros, and v5 accepts the resulting pin.",
        "refs": ["scripts/issue_g2a_prefill_prompt_pin.py:183-191", "scripts/issue_g2a_prefill_prompt_pin.py:276-285", "scripts/issue_g2a_prefill_prompt_pin.py:304-325"]
      },
      {
        "id": "F5",
        "severity": "blocker",
        "summary": "v5 accepts post-issue pin edits when internal hashes are rebound; token IDs, generation metadata, and authority fields are not externally bound.",
        "refs": ["configs/campaigns/d117_contrast_v5/generate_configs.py:931-949", "configs/campaigns/d117_contrast_v5/generate_configs.py:1088-1090"]
      },
      {
        "id": "F6",
        "severity": "blocker",
        "summary": "The runsheet places the selection record outside the issuer's required window-plan root.",
        "refs": ["docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:507-510", "scripts/issue_g2a_prefill_prompt_pin.py:287-293"]
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "summary": "The runsheet contains no executable invocation of the pin issuer; the handoff only says to pin the selected length.",
        "refs": ["docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:525-533", "scripts/issue_g2a_prefill_prompt_pin.py:334-363"]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise-wt-probe2 /Users/edr/code/JouleWise/.venv/bin/python scripts/generate_g2a_probe_inputs.py build-probes --root /private/tmp/g2a-replay.eavqO9/g2a --panel /Users/edr/code/JouleWise-wt-probe2/configs/model_panels/qwen3_4bit.json --prompt-corpus /private/tmp/g2a-replay.eavqO9/prompt-corpus.txt --small-members 5 --large-members 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS built G2-a prompt ladder, configs, and manifests"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS built G2-a prompt ladder"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise-wt-probe2 /Users/edr/code/JouleWise/.venv/bin/python - (independent runtime_raw/plain-tokenizers replay)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL_RUNG_CHECKS=PASS", "EXIT_CODE=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ALL_RUNG_CHECKS=PASS"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise-wt-probe2 /Users/edr/code/JouleWise/.venv/bin/python - (stream-1 patched bind/check harness with find/shasum snapshot)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS bound G2-a inputs to the calibration window", "PASS G2-a inputs authenticate with no config warnings", "CHECK_TREE_UNCHANGED=PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CHECK_TREE_UNCHANGED=PASS"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise-wt-probe2 /Users/edr/code/JouleWise/.venv/bin/python - (owned synthetic adversarial matrix a-j)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OWNED_FULL_ADVERSARIAL_REPLAY_COMPLETE", "EXIT_CODE=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OWNED_FULL_ADVERSARIAL_REPLAY_COMPLETE"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise-wt-probe2 /Users/edr/code/JouleWise/.venv/bin/python scripts/issue_g2a_prefill_prompt_pin.py --selection-record /private/tmp/g2a-replay.eavqO9/g2a/transcript/owned-d166-prefill-selection.json --summary /private/tmp/g2a-replay.eavqO9/owned-seam-summary.json --prompt-ladder /private/tmp/g2a-replay.eavqO9/g2a/window-plan/prefill-prompt-ladder.json --ruling-trace /Users/edr/code/JouleWise-wt-probe2/docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md --output /private/tmp/g2a-replay.eavqO9/g2a/transcript/owned-prefill-prompt-pin.json",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["G2-a prompt pin refused: selection_record_outside_window_plan_root"]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "selection_record_outside_window_plan_root"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise-wt-probe2 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_select_g2a_prefill_length tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 77 tests in 14.976s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 77 tests in .*\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD is detached; local and origin feature refs point to d26e0472. The requested 16b ruling was read from object 80912c8d because its path is absent at HEAD.",
      "needs": ""
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live hardware, run_campaign.py, powermetrics, or measurement execution was performed; calibration authentication and run outputs were synthetic as required.",
      "needs": ""
    }
  ]
}
```

## Replay log

Scratch root: `/private/tmp/g2a-replay.eavqO9`. Worktree remained clean.

`build-probes` exited 0 and produced eight stages with 24 configs. Independent raw-runtime and plain-`tokenizers` replay gave:

| Rung | Runtime raw | `tokenizers` | IDs/hash |
|---:|---:|---:|---|
| 512 | 512 | 512 | match |
| 1024 | 1024 | 1024 | match |
| 2048 | 2048 | 2048 | match |
| 4096 | 4096 | 4096 | match |

Both model tokenizer files matched the panel SHA256:

`aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`

The ladder IDs and `generate_configs.prompt_token_ids_sha256` matched for every rung. The runtime raw path is `joulewise/adapters/mlx_runtime.py:931-940`; the shared hash is `configs/campaigns/d117_contrast_v5/generate_configs.py:808-809`.

`bind-window` used the real panel and real tokenizer, with synthetic ledger/head/policy and the stream-1 test helper patches for live vectors and ledger authentication. It exited 0.

`check` exited 0 with `PASS G2-a inputs authenticate with no config warnings`. A whole-root snapshot using `find -type f -exec shasum -a 256 {} +` before and after was identical: `CHECK_TREE_UNCHANGED=PASS`.

The generated runsheet bracket was mechanically verified by the requested test suite. Its live sections were not executed because they invoke calibration and `run_campaign.py` at `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:390-398`.

Adversarial matrix, using 24 synthetic summaries authored under the scratch root:

| Case | `check` | Summarizer |
|---|---|---|
| a. One config byte changed | rc 1, `config_sha256_mismatch: g2a-small-p0512-r01` | rc 2, same named reason |
| b. Two config files swapped | rc 1, `config_sha256_mismatch: g2a-small-p0512-r01` | rc 2, same named reason |
| c. Stage relabelled to `small-p8192` | rc 1, `inventory_stage_identity_mismatch: small-p512` | rc 2, `inventory_stage_order_or_identity_mismatch:small-p512` |
| d. Large stage moved first | rc 1, `inventory_stage_identity_mismatch: small-p512` | rc 2, same order/identity reason |
| e. Same-count, different-byte prompt | rc 1, `prompt_ladder_sha256_mismatch` | rc 2, `inventory_prompt_ladder_sha256_mismatch` |
| f. Panel thinking policy edited | rc 1, `panel_sha256_mismatch` | rc 2, `inventory_panel_sha256_mismatch` |
| g. Altered copied config root | rc 1, `input_inventory_config_root_mismatch` | rc 2, `config_sha256_mismatch:g2a-small-p0512-r01` |
| h. Unbound output `run_id` | no runs-root input; unchanged check PASS | **ACCEPTED, rc 0** |
| i. Conflicting output `config_sha256` | no runs-root input; unchanged check PASS | **ACCEPTED, rc 0** |
| j1. One run directory removed | no runs-root input; unchanged check PASS | rc 2, `summary_unreadable:...g2a-small-p0512-r05...` |
| j2. One inventory member removed | rc 1, `stage_member_count_invalid: small-p512` | rc 2, `inventory_stage_member_floor_not_met:small-p512` |

The five requested test modules exited 0:

```text
Ran 77 tests in 14.976s

OK
```

## Findings

1. **F1 — BLOCKER:** A synthetic summary with top-level `"run_id": "g2a-not-in-inventory"` was accepted and emitted summary outputs. The summarizer reads only the nested count at `scripts/summarize_g2a_prefill_probe.py:248-255` and never validates output identity at `:367-369`.

   Minimal fix: enforce the summary schema and require its run ID to equal the inventory member ID, or reject the field if it is not part of the approved summary contract. Add a dedicated mutation test.

2. **F2 — BLOCKER:** A synthetic summary with top-level `"config_sha256": "000...000"` was accepted despite disagreeing with the inventory config hash. The same unchecked summary path is at `scripts/summarize_g2a_prefill_probe.py:248-255` and `:367-369`.

   Minimal fix: validate and compare the output’s config identity against the inventory/member binding before extracting counts.

3. **F3 — BLOCKER:** Removing one small member or run causes a hard refusal instead of a below-floor row. The member-floor guard fires at `scripts/summarize_g2a_prefill_probe.py:303-305`, and the later guard at `:404-405` also makes the rung unreachable.

   Minimal fix: preserve the actual member count, set `all_small_count_ge_5` false, and let the selector mark the rung nonqualifying. Handle zero members explicitly. The current test at `tests/test_summarize_g2a_prefill_probe.py:130-142` asserts the incorrect hard-refusal behavior.

4. **F4 — BLOCKER:** After selection, changing `panel_thinking_policy.panel_sha256` in the ladder to 64 zeros still produced a pin, and `_load_prefill_prompt_pin` accepted it at rung 512. The issuer checks only that the value is a lowercase SHA-shaped string at `scripts/issue_g2a_prefill_prompt_pin.py:183-191`; it never compares it to the bound panel. The emitted pin does not carry this binding at `:304-325`.

   Minimal fix: require the issuer to authenticate the ladder against the bound panel/inventory and carry a verifiable panel binding into the consumer contract.

5. **F5 — BLOCKER:** A valid issued pin was edited by changing one token ID and recomputing `prompt_token_ids_sha256`; `_load_prefill_prompt_pin` accepted it at rung 512. It also accepted edits to `generation_method`, `repeat_count`, selection path, and selection hash. The loader checks internal consistency but not authenticity or text/ID relation at `configs/campaigns/d117_contrast_v5/generate_configs.py:931-949`; the altered IDs are then consumed at `:1088-1090`.

   Minimal fix: bind the pin to an authenticated ladder digest and verify the ladder, or re-tokenize the prompt and compare IDs in the consumer. Derived metadata must be recomputed rather than trusted.

6. **F6 — BLOCKER:** The runsheet writes `G2A_SELECTION_RECORD` under `$G2A_TRANSCRIPT_ROOT` at `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:507-510`. The issuer requires that record to be relative to the prompt ladder’s parent directory at `scripts/issue_g2a_prefill_prompt_pin.py:287-293`. Replay failed with the named reason `selection_record_outside_window_plan_root`.

   Minimal fix: write the selection record and digest under `$G2A_WINDOW_PLAN_ROOT`, or change the issuer and contract together.

7. **F7 — SHOULD-FIX:** The runsheet’s desk handoff says “pin” but contains no `issue_g2a_prefill_prompt_pin.py` command at `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:525-533`.

   Minimal fix: add the exact issuer invocation, using the corrected window-plan selection path, plus an immediate `_load_prefill_prompt_pin` check.

## Seam check

With the binder’s real inventory and 24 synthetic summaries:

- Summarizer: exit 0; four rows `[512, 1024, 2048, 4096]`, each with five small members and one large member.
- Selector: exit 0; selected 512.
- Runsheet-compatible issuer path: exit 2, `selection_record_outside_window_plan_root`.
- Corrected selection path under `window-plan`: issuer exit 0.
- Consumer load: `ACCEPTED prefill_length=512`.

The corrected control proves the pin contract itself can reach `_v5`; the documented runsheet path cannot.

## Mutation table

| Mutation/guard | Test coverage |
|---|---|
| 3a config hash guard in `check` | Covered by `test_mutated_member_hash_refuses`, `tests/test_generate_g2a_probe_inputs.py:260-265` |
| 3a config hash guard in summarizer | Covered by `test_altered_config_hash_refuses`, `tests/test_summarize_g2a_prefill_probe.py:180-189` |
| 3b two-file swap | **UNCOVERED**; no explicit swap mutation |
| 3c relabelled stage | **UNCOVERED**; `test_unknown_stage_json_refuses` tests an extra disk file, not inventory relabelling |
| 3d reordered stages | **UNCOVERED** |
| 3e post-bind ladder mutation | **UNCOVERED**; existing ladder test is build-time only |
| 3f post-bind panel mutation | **UNCOVERED**; existing panel tests are pre-bind |
| 3g copied config root | **UNCOVERED** |
| 3h output run ID | **UNCOVERED**; accepted |
| 3i output config hash | **UNCOVERED**; accepted |
| 3j check member floor | **UNCOVERED** for bound inventory; build-only floor test is `tests/test_generate_g2a_probe_inputs.py:200-202` |
| 3j summarizer member floor | Existing `tests/test_summarize_g2a_prefill_probe.py:130-142` catches refusal but asserts the bug; required below-floor behavior is **UNCOVERED** |
| 5a stale selection digest | Covered by `test_bad_selection_and_summary_hashes_refuse`, `tests/test_issue_g2a_prefill_prompt_pin.py:196-213` |
| 5b edited ladder panel fingerprint | **UNCOVERED**; accepted |
| 5b edited ladder prompt construction | **UNCOVERED** as an explicit construction mutation |
| 5c output overwrite | Covered by `test_output_is_deterministic_and_existing_output_refuses`, `tests/test_issue_g2a_prefill_prompt_pin.py:261-277` |
| 5d edited pin with rebound token hash/metadata | **UNCOVERED**; consumer accepted |
| 5e unknown selection rung | Covered by `test_unknown_length_malformed_branch_and_inconsistent_floor_refuse`, `tests/test_issue_g2a_prefill_prompt_pin.py:215-236` |

## Residual risk

No live calibration, hardware measurement, `run_campaign.py`, powermetrics, or MLX generation was run. The replay validates desk-side producer behavior only, using synthetic calibration authentication and synthetic run summaries as required. The requested 16b ruling was read from Git object `80912c8d` because it is not present at the target commit.

VERDICT: REFUTE