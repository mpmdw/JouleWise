```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTE: the generated ladder cannot pass the issuer, and the summarizer reads provenance from an artifact that production bundles do not contain.",
  "workspace": {
    "base_requested": "82e7519d",
    "base_mode": "descendant",
    "head_start": "82e7519df808fd64e28347322f92618f348dafdf",
    "head_end": "97c0c8090fe1d098b95a4f0bcfe45cd5bc6f20c3",
    "upstream_end": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "branch": "feat/2026-09-01-g2a-probe"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "REFUTE",
    "findings": [
      {
        "id": "A1",
        "severity": "blocker",
        "title": "Probe workload name still differs from ruled V5 workload",
        "file": "scripts/generate_g2a_probe_inputs.py",
        "line": 485,
        "cure": "Use the exact _v5 workload_for('prefill') name df_ph_prefill_p{length}_candidate and add an equality test."
      },
      {
        "id": "A2",
        "severity": "blocker",
        "title": "Producer ladder schema is rejected by issuer",
        "file": "scripts/issue_g2a_prefill_prompt_pin.py",
        "line": 165,
        "cure": "Align issuer validation with the generator's ruled rendering fields or centralize the ladder schema; add a generated-ladder-to-issuer integration test."
      },
      {
        "id": "A3",
        "severity": "should_fix",
        "title": "Pin omits explicit special-token policy",
        "file": "scripts/issue_g2a_prefill_prompt_pin.py",
        "line": 421,
        "cure": "Add and validate a special_token_policy field documenting add_special_tokens=true."
      },
      {
        "id": "B1",
        "severity": "blocker",
        "title": "Summarizer expects provenance in summary_metrics.json, but production writes it to metadata.json",
        "file": "scripts/summarize_g2a_prefill_probe.py",
        "line": 329,
        "cure": "Read run_id and workload_provenance from the production metadata artifact, or change the bundle writer and test the real bundle shape."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "title": "Issuer receipt validation is self-consistency only, not run-bundle authentication",
        "file": "scripts/issue_g2a_prefill_prompt_pin.py",
        "line": 285,
        "cure": "Open and validate the referenced run bundles, metadata, configs, and authenticated receipt origin before issuing a pin."
      },
      {
        "id": "B3",
        "severity": "should_fix",
        "title": "Most named loader refusals lack exact mutation tests",
        "file": "tests/test_d117_contrast_v5_pack.py",
        "line": 425,
        "cure": "Add exact-reason mutation tests for every named refusal and construction guard."
      },
      {
        "id": "B4",
        "severity": "should_fix",
        "title": "Unknown receipt run ID raises KeyError instead of a named refusal",
        "file": "scripts/issue_g2a_prefill_prompt_pin.py",
        "line": 342,
        "cure": "Check membership before tuple unpacking and emit a stable refusal reason."
      },
      {
        "id": "C1",
        "severity": "should_fix",
        "title": "Runsheet promises overlap_margin_above_three, absent from current receipt",
        "file": "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
        "line": 476,
        "cure": "Describe the actual in_window_sample_count receipt field or restore the promised field."
      },
      {
        "id": "C2",
        "severity": "should_fix",
        "title": "Runsheet does not provide an executable V5 generation command",
        "file": "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
        "line": 574,
        "cure": "Add the exact generate_configs.py invocation for all three V5 packs, including --prefill-prompt-pin."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check 82e7519d HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "(no whitespace errors)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\(no whitespace errors\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": [
          "read-only sandbox has no usable temporary directory"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 89 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "magistrate-supplied: PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "compare dominance_criterion_registration() hash before and after",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "magistrate-supplied: 1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b unchanged"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1c0a4a11.*unchanged"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical unit tests were not rerun because this read-only sandbox lacks a usable temporary directory; the magistrate reports 89 tests OK.",
      "needs": "Rerun the canonical suite on the writable bench."
    }
  ]
}
```

## Findings

### A. CONTRACT

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| A1 | blocker | `scripts/generate_g2a_probe_inputs.py:485` | The producer emits `g2a_prefill_p{length}_diagnostic`; `_v5` still requires `df_ph_prefill_p{length}_candidate`, contrary to ruled R4 workload identity. | Emit the exact V5 workload name and assert producer/V5 config equality. |
| A2 | blocker | `scripts/issue_g2a_prefill_prompt_pin.py:165` | The issuer accepts only the five-key ladder schema, while the generator emits additional ruled keys: `rendering_mode`, `chat_template_applied`, and `thinking_policy`. The desk chain therefore rejects its own generated ladder with `prompt_ladder_closed_schema_mismatch`. | Align the schemas and test the actual generated ladder through the issuer. |
| A3 | should-fix | `scripts/issue_g2a_prefill_prompt_pin.py:421` | The pin has no explicit `special_token_policy`. | Add `special_token_policy: "add_special_tokens=true"` and validate it. |

The no-model-read clause passes: the loader opens neither a tokenizer nor model weights. The generator intentionally opens the panel-selected tokenizer and calls the adapter encode path with `add_special_tokens=True`, as authorized by 39b. The issuer uses the same `_encode` helper and flag.

The hash-bound bundle, exact refusal strings, nine-field rung equality, construction equality, panel hash call-site, desk bundle copy, corpus removal, and registration guard are present. The restricted D117 diff has no matches for `PINNED_DOMINANCE_CRITERION_BYTES`, `test_golden_readback_*`, or `test_common_mode_*`.

Luna’s five L-F5 edits map to one test:

| Edit | Test and exact assertion |
|---|---|
| Token IDs | `test_prefill_prompt_pin_bundle_and_ladder_mutations_refuse`, `token_ids`: `prefill_prompt_pin_ladder_rung_mismatch: prompt_token_ids` |
| Generation method | Same test, `generation_method` |
| Repeat count | Same test, `repeat_count` |
| Selection path | Same test, `selection_path`: `selection_record_missing` |
| Selection hash | Same test, `selection_hash`: `selection_record_sha256_mismatch` |

### B. EXECUTION

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| B1 | blocker | `scripts/summarize_g2a_prefill_probe.py:329` | The summarizer requires `run_id` and `workload_provenance` inside `summary_metrics.json`; production writes those fields in `metadata.json`. The changed fixture test injects them artificially, so legitimate bundles fail before receipt creation. | Read the production metadata artifact or change the writer and test an unmodified bundle. |
| B2 | blocker | `scripts/issue_g2a_prefill_prompt_pin.py:285` | Receipt validation checks internally supplied hashes and rows but never opens `runs_root`, run metadata, or the referenced configs. Fabricated self-consistent inventory, receipt, and summary can produce a pin. | Authenticate the receipt against actual run-bundle contents and provenance. |
| B3 | should-fix | `tests/test_d117_contrast_v5_pack.py:425` | Exact mutation coverage is incomplete; deleting several guards would not be noticed. | Add the mutation cases below and assert exact reason strings, not only exit code. |
| B4 | should-fix | `scripts/issue_g2a_prefill_prompt_pin.py:342` | An unknown `run_id` reaches dictionary unpacking and raises `KeyError`, not a named refusal. | Add an explicit membership check and exact-reason test. |

The issuer does obtain token IDs through the same adapter `_encode` path with `add_special_tokens=True`. The explicit policy field requested by 44c is absent.

## Mutation table

| Refusal | One-line mutation | Exact-reason test |
|---|---|---|
| `prompt_ladder_missing` | Change `pin["prompt_ladder"]["path"]` to `missing.json`. | None. |
| `prompt_ladder_sha256_mismatch` | Replace the ladder reference SHA with `"0"*64`. | None. |
| `selection_record_missing` | Change `pin["selection_record"]["path"]` to `missing.json`. | `test_prefill_prompt_pin_bundle_and_ladder_mutations_refuse`, `selection_path`. |
| `selection_record_sha256_mismatch` | Replace the selection reference SHA with `"0"*64`. | Same test, `selection_hash`. |
| `prompt_ladder_rung_missing` | Remove the selected rung and recompute only the ladder bundle SHA. | None. |
| `prefill_prompt_pin_ladder_rung_mismatch: <field>` | Mutate the selected ladder rung’s `prompt_text`, `prompt_text_utf8_sha256`, `prompt_token_ids_sha256`, `prompt_tokens`, or `closing_sentence`, then recompute the ladder bundle SHA. | Only `prompt_token_ids`, `repeat_count`, and `generation_method` are covered by `test_prefill_prompt_pin_bundle_and_ladder_mutations_refuse`. |
| `prompt_ladder_tokenizer_sha256_mismatch` | Mutate the ladder top-level tokenizer SHA and recompute the ladder bundle SHA. | None. |
| `prefill_prompt_pin_panel_sha256_mismatch` | Mutate the pin panel SHA, or mutate ladder panel SHA and recompute the ladder bundle SHA. | D117 mutation test covers both with `assertRaisesRegex`; it checks the exact reason token. |
| Construction equality guard | Change pin and ladder construction fields together so hashes and rung equality pass but `prompt_text` no longer equals repeated sentence plus closing sentence. | None. |
| Receipt run membership | Replace a selected run ID with an unknown ID. | None; current behavior is `KeyError`. |

### C. REGRESSION + PEDAGOGY

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| C1 | should-fix | `SHAKEDOWN-G2-RUNSHEET.md:476` | New prose says the receipt records `overlap_margin_above_three`, but current summarizer rows contain `in_window_sample_count` instead. | Update the prose to match the emitted receipt schema. |
| C2 | should-fix | `SHAKEDOWN-G2-RUNSHEET.md:574` | The desk-day text builds and copies the pin bundle but only says to generate V5 packs; it gives no executable V5 command. | Add the complete `generate_configs.py` command for each V5 pack. |

First-use coverage is mostly sound: pin, ladder, selection record, bundle, and receipt are introduced before use; the selected rung is only implicit through the selected-prefill-length wording. The operator chain still cannot complete independently because the final V5 generation command is omitted.

The displayed flags match their parsers:

- `build-probes`: `--root --panel --small-members --large-members`
- `bind-window`: `--root --ledger --head-pin --campaign-policy --power-policy --window-id --session-id --evidence-root-id`
- generated `check`: `--root --panel --ledger --head-pin --campaign-policy`
- summarizer: `--config-root --input-inventory --runs-root --counts-output --summary-output`
- selector: `--summary --output`
- issuer: `--selection-record --summary --prompt-ladder --input-inventory --counts-receipt --ruling-trace --output`

The V5 parser supports `--panel --model-a --model-b --decode-workload --prefill-length --prefill-prompt-pin --output-root`, but the runsheet does not invoke it.

VERDICT: REFUTE — the round’s producer-to-issuer ladder contract and real-bundle summarizer path are both broken before a valid authenticated pin can be issued.

## Residual risk

The realized-ID consumer check from 44c remains deliberately outside this round. No measurement or live hardware validation was performed.