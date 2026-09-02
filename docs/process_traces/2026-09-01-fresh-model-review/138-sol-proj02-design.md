```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "complete",
  "summary": "The catcher has a small per-config design, but changing either required source file rotates the receipt derivation identity, conflicting with the requested byte-identical legacy behavior.",
  "workspace": {
    "base_requested": "4a41d79187f93e21972b80b3878b5958fb646174",
    "base_mode": "exact",
    "head_start": "4a41d79187f93e21972b80b3878b5958fb646174",
    "head_end": "4a41d79187f93e21972b80b3878b5958fb646174",
    "upstream_end": "4a41d79187f93e21972b80b3878b5958fb646174",
    "branch": "feat/v5-prefill-realized-projection-02"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NEEDS_RULING",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Cross-version legacy receipt byte identity is incompatible with the D-131 derivation binding",
        "question": "May this row rotate executable derivation identity while leaving all issued legacy receipts immutable and freezing V5 only after the change?",
        "options": [
          "Accept the D-131 successor model: never edit legacy receipts; retired packs remain historical; freeze V5 at the reviewed post-change head.",
          "Require byte-identical cross-version receipts, which needs a derivation-contract redesign or exclusion of executed code from its identity."
        ],
        "recommendation": "Accept the first option; the second weakens or replaces D-131 and is disproportionate.",
        "blocked_work": "Implementation and its merge gauntlet."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/codex-review-tmp python3 -m unittest tests.test_identity_pins tests.test_mlx_runtime",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 68 tests in 4.257s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 68 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/v5-prefill-realized-projection-02"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## feat/v5-prefill-realized-projection-02$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Any required identity_pins.py or mlx_runtime.py edit changes source_file_sha256 in the exact receipt and makes an old freeze fail derivation re-verification.",
      "needs": "Rule that immutable retired receipts may remain historical while V5 is frozen only at the post-change reviewed head."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No real model/tokenizer was loaded, as explicitly prohibited; verification was fixture-only.",
      "needs": "Post-implementation lead-controlled production-stack freeze/arm replay."
    }
  ]
}
```

## Findings

F1 — `identity_pins._derivation_record` includes both `MlxRuntimeAdapter.identity_projection_metadata` and identity-pin callables, then hashes their entire source files (`joulewise/identity_pins.py:1143-1195`). That derivation is serialized into every receipt (`:1657-1688`) and arm compares it exactly (`:1999-2006`). Conditional omission can preserve legacy probe/check shape, but not whole receipt bytes across this code change. D-131 forbids editing old receipts and requires successor reissue (`docs/decision_log.md:8423-8430`).

## Proposed WRITE_SCOPE

After F1 is ruled:

- `joulewise/adapters/mlx_runtime.py`
- `joulewise/identity_pins.py`
- `tests/test_mlx_runtime.py`
- `tests/test_identity_pins.py`
- `docs/decision_log.md`
- `docs/council_log.md`
- `docs/process/state_kernel.json`
- `RUN_STATE.md`
- `TASK_QUEUE.md`
- `docs/run_reports/2026-09-02-v5-prefill-realized-projection-02.md`

## Numbered design specification

1. Leave schemas, `_v5` generator, prompt pin, condition family, and frozen registration untouched. Consume the already-typed `WorkloadProfile.prompt_token_expectation` (`joulewise/schemas.py:843-955`).
2. In `MlxRuntimeAdapter.identity_projection_metadata`, only when the expectation is present, call `_prompt_for_workload(config)` and attach `prompt_provenance(ids, text)` as `workload_provenance.prompt`. This is the collection encoder: `_prompt_for_workload` uses `_encode(..., add_special_tokens=True)` (`mlx_runtime.py:931-937,1100-1105`).
3. Extend private `_runtime_probe_metadata` to accept ordered `(config_path, BenchmarkConfig)` expectation-bearing configs. Prepare the representative runtime once, invoke its existing projector for every such config while the tokenizer remains loaded, then clean up once (`identity_pins.py:1251-1327`). Omit the new metadata key entirely when none has an expectation.
4. In `_derive_projection_units`, compare every config—not only `configs[0]`—on `token_count`, `token_ids_sha256`, and `token_hash_domain`. Missing/ill-typed prompt projection refuses; mismatch detail includes config path and the exact differing field names.
5. Reuse `readiness_identity_environment_dirty` for a coherent triple mismatch and `readiness_identity_artifact_unreadable` for expectation-present-but-unrealizable. The latter already owns absent hooks and projection exceptions (`identity_pins.py:1260-1289`). Expectation absence remains a complete no-op.
6. Add one PASS check per expectation-bearing config using the existing four-key check envelope. Include the ordered realization rows in `probe_metadata`, so `projection_input_sha256` binds them (`identity_pins.py:1515-1534`). Do not add receipt or receipt-unit fields (`:97-145,711-717`).
7. Freeze lets a mismatch exception escape before any writes (`identity_pins.py:1826-1837`). Arm reruns `_derive_projection_units`; verification catches the named refusal and emits an authenticated REFUSE arm receipt (`:1938-2052`).

## Answers Q1–Q7

Q1. Yes. `runtime.prepare` precedes the probe and cleanup follows it (`identity_pins.py:1258-1303`); MLX prepare loads model and tokenizer together and retains both (`mlx_runtime.py:273-295`), and the hook requires both (`:315-324`). No additional model/tokenizer load is needed.

Q2. Comparison belongs inside `_derive_projection_units`, but as a per-config loop sharing one prepared unit. Current code checks all config declarations yet probes only `configs[0]` (`identity_pins.py:1370-1400`). Representative-only is unsound for a per-config schema.

Q3. Reuse `readiness_identity_environment_dirty` for mismatch, with detail naming any of `token_count`, `token_ids_sha256`, `token_hash_domain`; reuse `readiness_identity_artifact_unreadable` for missing tokenizer/hook/projection. Absence skips the check, consistent with row 01 owning bundle absence (`bundle_read.py:939-959`).

Q4. Arm re-runs the same function, then compares input hash, runtime triples, and stack identity to freeze (`identity_pins.py:2001-2020`); it is not receipt-only replay. Realizations fit existing `checks`, so this is no schema-version change. For expectation-bearing V5, the future receipt, sidecar, plan tree/sidecar, and producer reference written at freeze move (`:1891-1928`); no V5 pack is committed yet.

The nine issued `_v1`–`_v3` `identity_pin_projection.receipts/projection-0001.{json,sha256}`, their plan-tree bindings, six floor producer contracts, and nine arm-readiness freeze receipts must not move. A representative V3 receipt already pins both relevant source hashes (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/identity_pin_projection.receipts/projection-0001.json:76-81`). D-167 retires the old V3 lane (`docs/decision_log.md:10408-10419`), supporting historical immutability rather than rewriting.

Q5. D-131 fixes exact receipts, derive-never-enter, freeze/arm lifecycle, and readiness consumption (`docs/decision_log.md:8401-8436`). Because 44c marks this arm-critical change as a council trigger, the PR owes D-118’s complete gate: independent audit; paired contract/execution plus causality lens; lead FIX/dispositions; delta after every fix; same-signature statement/escalation; Opus near-final counterreview; apex Fable code/design pass; overbuild prune; lead unpiped integration-tree suite; final-head fresh review; final-head CI and post-merge interaction review if waved; complete PR ledger (`:7769-7812`). D-121 adds terminal magistrate review after all eleven, retriggered by any later commit (`:7892-7924`).

Q6. Required tests:

- `test_identity_projection_metadata_realizes_registered_prompt_with_collection_encoder`: exact provenance and `add_special_tokens=True`; counterfactual is FakeTokenizer’s registered prompt.
- `test_identity_projection_metadata_omits_realization_without_expectation`: projection has the exact legacy key set; counterfactual is no expectation.
- `test_freeze_checks_every_registered_config`: member 2 alone returns a wrong hash; assert its path and mismatch reason.
- `test_freeze_mismatch_names_all_differing_fields`: wrong count/hash/domain; assert all three names.
- `test_arm_reverification_refuses_each_prompt_realization_drift`: after a clean freeze, mutate each field separately; assert REFUSE receipt and unchanged pack bytes.
- `test_projection_refuses_unavailable_registered_realization`: missing `prompt` or hook; assert artifact-unreadable with the config path.
- Keep the closed-vocabulary/D-078 assertion unchanged (`tests/test_identity_pins.py:1169-1193`).

Mutants: use `add_special_tokens=False`; check only `configs[0]`; ignore ids hash; ignore domain; emit prompt metadata unconditionally; trust the frozen PASS at arm without re-running per-config realization.

Q7. No generator, `_v5` pack generator, prompt pin, or registration change is needed. The generator already loads pinned ids without a tokenizer and emits the per-arm expectation (`generate_configs.py:624-627,1003-1055,1326-1351`). Any request to edit that file or `dominance_criterion_registration()` is outside this design and requires a new ruling.

## Disagreement

The row’s mixed-arm-unit premise does not describe current code: V5 constructs separate `A/prefill` and `B/prefill` units (`generate_configs.py:2567-2615`), while `_derive_projection_units` already refuses multiple declared/scientific identities within one unit (`identity_pins.py:1375-1389`). Per-config checking is still the right future-proof design, but permitting genuinely different expectations inside one unit would be a separate identity-contract decision.

I also push back on “legacy packs project identically” if it means cross-version exact receipt bytes. D-131 intentionally binds executable source; the defensible invariant is “no new prompt/check payload for configs without an expectation, and no issued receipt is rewritten,” not whole-receipt equality after changing hashed code.

## Residual risk

Fixture tests prove routing and comparison logic, not the real tokenizer stack. The final gate should freeze and arm a throwaway generated V5 pack with each real Qwen tokenizer under lead control before the production night.