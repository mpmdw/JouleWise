```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTE: V2 accepts synthetic and summary-mismatched authority, receipts survive exact-byte input changes and silent reissuance, and the shared implementation alters V1 behavior.",
  "workspace": {
    "base_requested": "HEAD",
    "base_mode": "exact",
    "head_start": "cb9371aa634129afb2fd5dab43deebc69ec5233d",
    "head_end": "cb9371aa634129afb2fd5dab43deebc69ec5233d",
    "upstream_end": "cb9371aa634129afb2fd5dab43deebc69ec5233d",
    "branch": "feat/transfer-fiducial-01"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/contracts/transfer_fiducial.md",
    "joulewise/transfer_fiducial.py",
    "scripts/fit_transfer_fiducial.py",
    "tests/test_transfer_fiducial.py",
    "configs/diagnostics/transfer_fiducial_v2/generate_plan.py",
    "tests/test_transfer_fiducial_v2_plan.py",
    "tests/fixtures/transfer_fiducial_v2/synthetic-g2a-summary.json",
    "tests/fixtures/transfer_fiducial_v2/synthetic-selected-g2a-record.json"
  ],
  "verdict": {
    "decision": "REFUTE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "The selection record's summary digest is checked only for hexadecimal shape; a record naming the wrong summary digest emits a plan."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "summary": "The production generator accepts the explicitly synthetic prompt pin, self-asserted token IDs, and a non-ruled record_id, emitting eleven artifacts."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "summary": "The receipt hashes normalized configuration meaning rather than exact source bytes and omits the module containing the fitter logic."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "summary": "Receipt issuance overwrites an existing receipt path silently, allowing post-input-change reissuance."
      },
      {
        "id": "F5",
        "severity": "blocker",
        "summary": "The successor changes V1 behavior by making receipts and new fit gates mandatory on the shared V1 schema and CLI."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "summary": "The operator procedure is not runnable from the contract alone and retains a contradictory V4 status."
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "summary": "Tests positively require synthetic generation and omit the decisive authentication, exact-byte, duplicate-issuance, and pin-mismatch mutations."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c '<in-memory git-show HEAD module/test loader>'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 6 tests in 2.538s",
          "FAILED (errors=2)",
          "HEAD_V1_RESULT tests=6 failures=0 errors=2"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_transfer_fiducial",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 8 tests in 2.524s",
          "FAILED (errors=4)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_transfer_fiducial_v2_plan",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 0.001s",
          "FAILED (errors=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD -- configs/campaigns/d117_contrast_v5/generate_configs.py",
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
      "kind": "lint",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox denied mktemp under /tmp; filesystem mutation tests failed before their bodies. Adversarial cases were instead executed through in-memory Path/source fault injection.",
      "needs": "Rerun V1-V3 in a writable isolated /tmp checkout."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The ruled permanent prompt-pin input is present and required by the CLI, and its rung/tokenizer checks fail closed; the surrounding authority checks remain incomplete.",
      "needs": ""
    }
  ]
}
```

## Findings

1. **F1 — BLOCKER — the G2-a selection is not authenticated to its summary.** `load_authenticated_selection` checks only that `summary_sha256` looks like a lowercase 64-character digest; the CLI accepts no summary input against which to recompute it (`configs/diagnostics/transfer_fiducial_v2/generate_plan.py:88-133,335-358`). That violates the contract’s promised refusal of an unauthenticated record (`docs/contracts/transfer_fiducial.md:39-44`) and the ruled issuer flow, which takes both `--selection-record` and `--summary` and recomputes their binding (`main:docs/process_traces/2026-09-01-fresh-model-review/16-sol-g2a-executability-scout.md:259-272`).

   Concrete input: replace the fixture record’s real summary digest `874389…6a59` with 64 zeroes and regenerate the prompt pin’s `g2a_record_sha256`. The generator emitted ten configs plus `plan.json`; no refusal was produced.

   Minimal fix: require the authenticated summary as an input, recompute its exact-byte SHA-256, and compare it with the record before loading the permanent prompt pin. Preserve the pin as the ruled additional input.

2. **F2 — BLOCKER — the synthetic prompt-pin fixture is production-admissible.** The imported validator checks the prompt-text hash and token-ID hash independently but never re-tokenizes the text; `generation_method` need only be nonempty (`configs/campaigns/d117_contrast_v5/generate_configs.py:923-949`). The V2 adapter checks only the pin’s G2-record digest (`configs/diagnostics/transfer_fiducial_v2/generate_plan.py:151-167`). It does not enforce the ruled `record_id = "sha256:" + record digest`, the ruled generation-method form, or text/ID equivalence (`main:docs/process_traces/2026-09-01-fresh-model-review/16b-RULING-g2a-producers.md:49-58,73-78`).

   Concrete input: the test pin labels itself `"synthetic fixture only; never a live prompt pin"` and supplies `[17] * 512` as self-hashed IDs (`tests/test_transfer_fiducial_v2_plan.py:31-67`). The production generator emitted eleven artifacts. Those IDs are recorded in the plan while runtime consumes only `prompt_text` (`configs/diagnostics/transfer_fiducial_v2/generate_plan.py:240-280`).

   Minimal fix: consume only the ruled prompt-pin issuer output; enforce R3’s exact record ID and path rule, authenticate the prompt ladder/summary binding, and re-tokenize against the panel-pinned tokenizer before emitting any configuration.

   The other required cases do fail closed:

   - Pin rung mismatch: `prefill_prompt_pin_unauthenticated:prefill_prompt_pin_length_mismatch`.
   - Pin tokenizer/panel mismatch: `prefill_prompt_pin_unauthenticated:prefill_prompt_pin_tokenizer_sha256_mismatch`.
   - `collect-at-4096` refusal record: `selection_record_not_selected`.

3. **F3 — BLOCKER — receipt validation is not an exact-byte/program-version freeze.** `_config_source_hashes` discards source bytes, normalizes parsed configurations, and hashes the normalized rendering (`joulewise/transfer_fiducial.py:844-887`). The receipt also pins only the thin CLI script, not `joulewise/transfer_fiducial.py`, where `fit_run`, receipt validation, bindings, and verdict logic live (`joulewise/transfer_fiducial.py:282-654,894-1000,1104-1313`). This violates the receipt’s promise to freeze configuration SHA-256 values and prevent changing the program version after seeing data (`docs/contracts/transfer_fiducial.md:172-188`).

   In-memory one-byte matrix against an otherwise valid receipt:

   | Mutated input | Observed reason |
   |---|---|
   | Plan, append one space | `pre_data_receipt_plan_sha256_mismatch` |
   | Config source, prepend one space | **No reason; receipt remained satisfied** |
   | `scripts/fit_transfer_fiducial.py` digest | `pre_data_receipt_fitter_source_sha256_mismatch` |
   | Estimator digest | `pre_data_receipt_estimator_source_sha256_mismatch` |
   | Calibration evidence digest | `pre_data_receipt_calibration_identity_mismatch` |
   | Receipt bytes, append one space | **No reason; receipt remained satisfied** |

   Minimal fix: hash each named config with `read_bytes()` rather than normalization; enforce canonical receipt bytes or bind them through an external digest; and pin the actual fitter module plus every normative dependency.

4. **F4 — BLOCKER — `--issue-receipt` silently overwrites.** The CLI unconditionally creates the parent and calls `write_text` without an existence check or exclusive creation (`scripts/fit_transfer_fiducial.py:51-63`). Two invocations against the same mocked path both returned 0 and wrote twice. This contradicts the receipt’s declared immutability (`docs/contracts/transfer_fiducial.md:172-176`) and permits changing inputs, then replacing the receipt.

   Minimal fix: publish with create-new semantics (`O_CREAT|O_EXCL` or equivalent atomic exclusive write), refuse with a stable `pre_data_receipt_already_exists` reason, and test two sequential issuances plus a concurrent race.

5. **F5 — BLOCKER — V1 behavior is changed.** HEAD’s V1 procedure fits without a receipt (`HEAD:docs/contracts/transfer_fiducial.md:139-181`). The working-tree CLI now rejects that exact argument shape with exit 2 (`scripts/fit_transfer_fiducial.py:64-69`), and the library adds `pre_data_receipt_missing` to every call lacking the new argument (`joulewise/transfer_fiducial.py:943-958,1119-1131`). It also changes invalid planned-config handling from a raised error to an exit-0 inconclusive capture (`joulewise/transfer_fiducial.py:1151-1175`; compare `HEAD:joulewise/transfer_fiducial.py:841-862`). The edited V1 test was changed to issue a receipt, masking the compatibility break (`tests/test_transfer_fiducial.py:352-396`).

   Concrete input: the exact HEAD command with `--plan`, `--runs-root`, `--pulse-calibration-dir`, and `--output` now returns 2: `--runs-root, --receipt, and --output are required`.

   Minimal fix: introduce an explicit V2 schema/diagnostic kind and version-dispatch all new receipt, dwell, temporal, and inconclusive behavior. Restore the V1 API and CLI path unchanged.

6. **F6 — SHOULD-FIX — the operator path is not executable from the contract alone.** The contract provides placeholders for `G2A_SELECTION_RECORD` and `G2A_PREFILL_PROMPT_PIN` but no producer invocations (`docs/contracts/transfer_fiducial.md:217-233`); the latest ruling confirms that the prompt-pin producer is not present (`main:docs/process_traces/2026-09-01-fresh-model-review/16b-RULING-g2a-producers.md:3-15`). `TF_CAL_DIR` is then used without any assignment or deterministic selection command (`docs/contracts/transfer_fiducial.md:248-273`). “Standard readiness and idle procedure,” “approved power,” “network-time custody,” “unique successful calibration directory,” “verification,” and “backup” are also used before being built or linked (`docs/contracts/transfer_fiducial.md:199-208,248,276-277`).

   The document’s top status still says `V4-TRANSACTION-01` (`docs/contracts/transfer_fiducial.md:3-6`), while D-167 requires the final `V5-NIGHTLY-G3-01` pass before the fiducial (`docs/decision_log.md@feat/2026-09-01-kernel:10406-10417`; `docs/process/state_kernel.json@feat/2026-09-01-kernel:4363-4372`).

   Minimal fix: add the ruled summary/pin producer commands, exact output discovery and assignment for `TF_CAL_DIR`, and links/commands for every prerequisite; update the status to the D-167 chain.

7. **F7 — SHOULD-FIX — the tests encode the happy path and miss the contract attacks.** The main generator test deliberately builds the synthetic pin and expects generation success (`tests/test_transfer_fiducial_v2_plan.py:31-67,81-119`). The summary test proves only the unchanged fixture equals the selector’s output (`tests/test_transfer_fiducial_v2_plan.py:121-129`). Selection refusals cover missing input, malformed digest text, and an unknown rung, but not a refused/collect-at-4096 record or any pin mismatch (`tests/test_transfer_fiducial_v2_plan.py:131-181`). Receipt tests mutate receipt fields rather than the actual fitter/estimator bytes, and their config mutation changes semantics instead of bytes-only formatting (`tests/test_transfer_fiducial.py:432-480`).

   Minimal fix: add the five requested production-CLI cases, exact-byte receipt mutations, core-fitter mutation, duplicate issuance, and V1 compatibility tests retained verbatim from HEAD.

`--check` itself is byte-strict for its intended output set. Configs and the plan are rendered with sorted keys and one trailing newline, and comparison uses raw `read_bytes()` (`configs/diagnostics/transfer_fiducial_v2/generate_plan.py:212-214,295-331`). Key-order changes, a removed newline, an added space, and plan key reordering all refused as `committed_output_bytes_mismatch:<path>`. No plan/config JSON-byte mutation slipped through. Files named `generate_plan.py` are intentionally outside the output inventory (`configs/diagnostics/transfer_fiducial_v2/generate_plan.py:300-305`).

## Mutation table

| Guard deleted or absent | Named test that still passes |
|---|---|
| Recompute `summary_sha256` from supplied summary — absent | `test_generates_ten_qwen3_small_configs_with_v5_identity_pins`; `test_synthetic_selection_fixture_matches_the_selector_output_shape` |
| Reject synthetic/unruled prompt provenance and re-tokenize text — absent | `test_generates_ten_qwen3_small_configs_with_v5_identity_pins` positively requires the synthetic input |
| Enforce ruled G2 `record_id` — absent | All three `TransferFiducialV2PlanTests` |
| Delete refused-record gate at `generate_plan.py:106-107` | All three V2-plan tests; none supplies a refused record |
| Delete imported pin-length guard at `generate_configs.py:917-920` | All three V2-plan tests |
| Delete imported tokenizer guard at `generate_configs.py:921-922` | All three V2-plan tests |
| Delete selection-record/pin digest join at `generate_plan.py:165-166` | All three V2-plan tests |
| Delete raw byte comparison at `generate_plan.py:329-331` | `test_generates_ten_qwen3_small_configs_with_v5_identity_pins`; it checks only an identical set |
| Replace exact config-byte binding with normalization — current implementation | `test_transfer_fit_refuses_each_pre_data_receipt_drift`; its semantic notes mutation still refuses |
| Omit the actual fitter-module digest — current implementation | `test_transfer_fit_refuses_each_pre_data_receipt_drift`; it mutates only the receipt’s wrapper-script field |
| Omit create-new receipt publication — current implementation | All receipt tests; none issues twice |
| Delete per-bundle dwell check at `transfer_fiducial.py:1070-1073` | All receipt tests; none supplies a mismatched requested dwell |
| Delete plan SHA comparison at `transfer_fiducial.py:973-974` | **Killed:** `test_transfer_fit_refuses_each_pre_data_receipt_drift` would fail |
| Delete calibration identity comparison at `transfer_fiducial.py:990-991` | **Killed:** both receipt-drift and calibration-order tests would fail |
| Delete calibration-before-run check at `transfer_fiducial.py:1003-1022` | **Killed:** `test_transfer_fit_refuses_calibration_after_run_start` would fail |
| Delete missing-receipt check at `transfer_fiducial.py:953-954` | **Killed, but wrongly:** the edited V1 test now enshrines the V1 compatibility regression |

The registered `_v5` generator has no diff against HEAD, so no `_v5` registration byte was touched.

## Residual risk

The sandbox provides no writable temporary directory. HEAD ran six V1 tests with four passes and two pre-body tempfile errors; the working tree ran eight with four passes and four pre-body tempfile errors; the V2-plan module ran one pass and two pre-body tempfile errors. The exact suites must be rerun in a writable isolated checkout, but the blocker demonstrations above do not depend on those unavailable filesystem writes.

VERDICT: **REFUTE**