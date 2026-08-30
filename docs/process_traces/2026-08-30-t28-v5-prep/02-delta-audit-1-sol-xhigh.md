```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "D-1 and the v5 two-pin generator guard are installed, but F2 primary is damaged and D-3/D-4 remain partial because of a one-pin runtime bypass, incomplete schema propagation, stale authority text, and replay/production semantic divergence.",
  "workspace": {
    "base_requested": "596a7b42",
    "base_mode": "exact",
    "head_start": "2b0c0aaa3fc5cbd72248b566322f38a324a3b99c",
    "head_end": "2b0c0aaa3fc5cbd72248b566322f38a324a3b99c",
    "upstream_end": "2b0c0aaa3fc5cbd72248b566322f38a324a3b99c",
    "branch": "feat/v5-ladder-prep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "dispositions": {
      "D-1": "INSTALLED",
      "D-2/F2-primary": "DAMAGED",
      "D-3": "PARTIAL",
      "D-4": "PARTIAL",
      "F2-guard": "INSTALLED"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Independently optional identity pins allow generation after skipping tokenizer identity verification",
        "file_line": "joulewise/schemas.py:728; joulewise/adapters/mlx_runtime.py:76; tests/test_mlx_runtime.py:349",
        "refutation": "A config containing only a matching chat_template_sha256 is accepted; prepare never hashes tokenizer.json and proceeds to mlx_lm.load. A read-only probe made tokenizer hashing raise if called and observed successful prepare plus a load call."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The new ModelConfig keys were not propagated to all exact-key and golden-schema consumers",
        "file_line": "joulewise/publication_privacy.py:63; joulewise/publication_privacy.py:402; tests/goldens/config_schema.json:447; joulewise/schemas.py:1117",
        "refutation": "Publication privacy rejects both pins as unclassified fields, and the checked-in config-schema golden omits both new properties even though the emitted schema contains them."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The D-4 replay window fence is weaker than the production noncollapse predicate",
        "file_line": "configs/campaigns/d117_contrast_v5/generate_configs.py:654; joulewise/floor_extraction.py:362",
        "refutation": "For end=nextafter(2*bound,+inf), replay accepts because float subtraction rounds to 2*bound; production refuses because its outward-rounded endpoint predicate finds no strict interior. Replay also coerces values with float() that production's finite/type gate refuses."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The four D-3 rulings are serialized but were not installed in the binding decision log",
        "file_line": "configs/campaigns/d117_contrast_v5/generate_configs.py:495; docs/decision_log.md:192; docs/decision_log.md:10363",
        "refutation": "The emitted object carries all four rulings, but the decision log still states unqualified mandatory common-mode R_cm and leaves derivation/absolute handling open; the disposition-required amendment is absent."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Identity mismatch is classified as runtime unavailable and therefore reported as unsupported",
        "file_line": "joulewise/adapters/mlx_runtime.py:96; joulewise/controller.py:167",
        "refutation": "Every pin absence/mismatch refusal uses RUNTIME_UNAVAILABLE, which the controller maps to UNSUPPORTED. No retry or fallback bypass was found, but a configuration-integrity failure is misclassified as structural runtime incompatibility."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_detects_all_must_pass_mutation tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_detects_threshold_mutation tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_matches_independent_retained_fixture_calculation tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_refuses_unauthenticated_or_invalid_inputs tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_validate_export_and_schema tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_reject_noncanonical_values tests.test_schemas.EmittedConfigRoundTripTests.test_config_hash_is_pinned",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 0.061s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check 596a7b42..2b0c0aaa",
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
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2715 tests in 89.754s",
          "FAILED (errors=1728, skipped=112)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "set -o pipefail; for model_id in qwen3-1p7b qwen3-8b; do python3 scripts/admit_model_panel_entry.py --panel configs/model_panels/qwen3_4bit.json --model-id \"$model_id\" | jq -c '{status,reason_codes,model_id:.model_entry.model_id,tokenizer:.checks.tokenizer_json.status,template:.checks.chat_template.status}'; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"status\":\"passed\",\"reason_codes\":[],\"model_id\":\"qwen3-1p7b\",\"tokenizer\":\"passed\",\"template\":\"passed\"}",
          "{\"status\":\"passed\",\"reason_codes\":[],\"model_id\":\"qwen3-8b\",\"tokenizer\":\"passed\",\"template\":\"passed\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"status\":\"passed\""
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The canonical suite could not establish a clean result in the read-only runner: sampled errors were failures to create a usable temporary directory, and the suite summary contained errors rather than assertion failures.",
      "needs": "Replay the canonical suite in the normal writable test environment."
    },
    {
      "id": "FL2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No live mlx_lm load or generation was performed; runtime ordering was established by inspection, focused mocks, current-mirror byte checks, and admission-tool execution.",
      "needs": ""
    }
  ]
}
```

## Findings

### BLOCKER F1 — One-pin configurations bypass tokenizer verification

`ModelConfig` makes the pins independently optional at `joulewise/schemas.py:728-757`, and `_model_identity_pin_refusal` checks each independently at `joulewise/adapters/mlx_runtime.py:76-148`.

Consequently, a configuration with only a valid `chat_template_sha256` can carry an arbitrary or drifted `tokenizer.json`: the tokenizer branch is skipped, the template passes, and `prepare()` reaches `mlx_lm.load`. A read-only probe against the current Qwen3 mirror forced tokenizer hashing to raise if invoked; preparation still succeeded and called the loader. The new test at `tests/test_mlx_runtime.py:349-370` itself uses a template-only configuration, thereby blessing the invalid partial state.

The v5 generator guard prevents this in generated v5 members, but it does not repair the public schema/runtime path. F2 primary is therefore **DAMAGED**. The required invariant is both pins absent for legacy configs or both present and verified.

The remaining runtime-path observations were sound:

- `prepare()` invokes the identity fence before importing/loading MLX at `joulewise/adapters/mlx_runtime.py:245-275`.
- The controller prepares before warmup or generation; no production cached/warm bypass was found.
- Empty/`None` source is refused before load.
- A missing `tokenizer_config.json` is refused when the template pin is present.
- A stable symlink is checked and loaded through the same resolved source path, although mutation between check and load remains a TOCTOU residual.

### SHOULD-FIX F2 — Schema propagation is incomplete

The two names were added to the main model-key allowlist and exported JSON schema, and their validator correctly requires lowercase, 64-character hexadecimal SHA-256 values. Existing configurations without pins still load.

However, `joulewise/publication_privacy.py:63-65` retains a closed model allowlist without either new field. Its refusal at `joulewise/publication_privacy.py:402-419` therefore rejects a v5 configuration with:

`unclassified field(s) in config.json.model: chat_template_sha256, tokenizer_json_sha256`

The schema golden is also stale: `tests/goldens/config_schema.json:447-495` lacks the properties emitted at `joulewise/schemas.py:1117-1129`. The documented schema-diff command consequently reports both as new-only paths.

No normalized example-config golden changed because optional pins are omitted when absent; the pinned examples, including `mac_mlx_local`, retained their hashes. The golden whose bytes now need to change is `tests/goldens/config_schema.json`.

### SHOULD-FIX F3 — D-4 does not mirror production semantics

Replay uses the plain test

`end - start <= 2.0 * bound`

at `configs/campaigns/d117_contrast_v5/generate_configs.py:654-671`. Production uses outward-rounded endpoints and demands a strict interior at `joulewise/floor_extraction.py:362-375`.

Counterexample: for a fixture bound `b`, set the window to `[0, nextafter(2*b, +inf)]`. Floating subtraction rounds the duration to `2*b`, so replay accepts it. Production computes outward-rounded inner endpoints and refuses it as `common_mode_nonseparable_window_domain`.

Replay also applies `float()` coercion where production rejects booleans and non-numeric types before arithmetic. Thus the new fence is similar in shape but not equivalent in accepted inputs.

The other D-4 pieces are installed:

- The original garbage example is refused: zero bound fails authentication, and with a valid bound its `999` zero point is absent from the sweeps.
- Zero membership remains exact.
- Residual divergence uses the same `rel_tol=1e-9`, `abs_tol=1e-12`.
- The fixture’s independent arithmetic no longer calls a production comparative-floor routine.

D-4 is **PARTIAL**.

### SHOULD-FIX F4 — D-3 authority remains contradictory

The emitted `dominance_criterion` at `configs/campaigns/d117_contrast_v5/generate_configs.py:495-539` is verbatim-equivalent to all four rulings:

- Absolute independent-corner \(R\) remains reportable.
- Absolute common-mode \(R_{cm}\) is `not_applicable`, with the cancellation/replay rationale.
- Comparative ABBA \(R_{cm}\) is mandatory, with withdrawal below 2.
- No absolute local-only diagnostic is registered; a distinct versioned name is deferred.

All current generator registrations use that centralized object, and the campaign-pack documentation agrees. No other active registration claims an absolute \(R_{cm}\) exists.

But the binding decision log was not amended as the disposition requires. `docs/decision_log.md:192` and `:10363-10371` still state unqualified mandatory common-mode \(R_{cm}\) and leave its derivation/absolute treatment unresolved. Historical process traces also contain the superseded discussion, but those are historical evidence rather than active registration.

D-3 is **PARTIAL**.

### SHOULD-FIX F5 — Identity refusal has the wrong structured class

All missing-file, malformed-template, and hash-mismatch branches at `joulewise/adapters/mlx_runtime.py:96-148` return `FailureReason.RUNTIME_UNAVAILABLE`. The controller maps that reason to `RunStatus.UNSUPPORTED` at `joulewise/controller.py:167-180`.

That is misleading for an identity/configuration-integrity mismatch: the runtime may be fully available, but the supplied artifact does not satisfy its pinned identity. No consumer was found that retries, falls back, or otherwise reaches generation because of this classification; CLI and campaign execution still treat it as non-success. The defect is semantic reporting and downstream status accounting, not fail-open behavior.

**Disposition verdicts:**

- D-1 — **INSTALLED**. The pin at `tests/test_d117_contrast_v5_pack.py:31-61` is a literal test-owned byte string. Main comparison at `:384-389` is generator bytes versus that literal. Mutations at `:402-417` also compare mutated serialized bytes directly with the literal. A generator threshold drift to `1.9` makes the equality assertion at `:386-389` fail.
- D-2/F2 primary — **DAMAGED** by F1, F2, and F5.
- D-3 — **PARTIAL** because serialization is correct but the binding amendment is absent.
- D-4 — **PARTIAL** because the new window fence does not match production semantics.
- F2 guard — **INSTALLED**. `_model_config` refuses either missing pin at `configs/campaigns/d117_contrast_v5/generate_configs.py:721-744`, and `tests/test_d117_contrast_v5_pack.py:270-290,336-348` asserts both pins on every emitted member and both missing-pin cases.

The chat-template pin definition is consistent and reproducible: parse `tokenizer_config.json`, extract the `chat_template` string, encode that string as UTF-8, and hash those bytes—not the whole JSON file. This definition is implemented in both runtime and admission tooling and recorded at `docs/campaign_packs/d117_contrast_v5.md:41-46`. The current Qwen3 panel value `87a2728c…96b5` matches the parsed field’s 4,116 UTF-8 bytes; the whole-file hash is different.

## Residual risk

The canonical suite needs replay in a writable environment because this runner could not create temporary directories. No live MLX model load was attempted. A source symlink or identity file can also theoretically change between hashing and `mlx_lm.load`; the current fence is ordered correctly but is not atomic.