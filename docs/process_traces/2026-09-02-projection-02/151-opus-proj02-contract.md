VERDICT: SHOULD-FIX

Contract lens, `717b1ddb` on `feat/v5-prefill-realized-projection-02` vs main `c5fa8a49`.
Ruling: `docs/process_traces/2026-09-01-fresh-model-review/141a-RULING-projection-02.md`
(read from `/Users/edr/code/JouleWise` — it is NOT present in the wt-proj02 checkout).
All 75 tests in `tests.test_identity_pins tests.test_mlx_runtime` pass in the checkout.
No blockers. One ruled invariant is implemented but has zero regression coverage
(demonstrated with a surviving mutant), plus six nits.

## Clause table

| Clause | Satisfied by | Note |
|---|---|---|
| P-1 "realizes ... with the COLLECTION encoder — `_prompt_for_workload` → `_encode(..., add_special_tokens=True)` ... and `prompt_provenance` ... compares the triple inside `_derive_projection_units`" | `joulewise/adapters/mlx_runtime.py:341-349` calls `self._prompt_for_workload(config)` + `prompt_provenance(...)`; the registered-text branch is `mlx_runtime.py:944-946` (`_encode(self._tokenizer, profile.prompt_text, add_special_tokens=True)`) — the same call the collection path uses at `:393`. Comparison at `joulewise/identity_pins.py:1531-1550`. | SATISFIED. Domain constants agree (`schemas.py:71` == `provenance.py:12` == `"joulewise.prompt_token_ids.v1"`); `schemas.py:312-316` forces `prompt_token_expectation` to imply `prompt_text`, so the synthetic-prompt branch is unreachable here. No schema-version change, no `_v5` generator edit. |
| P-2 "attached ONLY when the config carries a `prompt_token_expectation`; configs without one get the exact legacy probe-metadata key set" | Adapter gate `mlx_runtime.py:341`; probe gate `identity_pins.py:1400-1402`; derive-side gate `identity_pins.py:1470-1474,1483-1487`. | SATISFIED. |
| P-3 "loops every expectation-bearing config ... against ONE prepared runtime (prepare once, project per config, clean up once)" | One `_runtime_probe_metadata` call (`identity_pins.py:1483-1487`); one `prepare` at `:1307`, per-candidate `projector(candidate)` at `:1336-1342` (representative reused, not re-probed), one `cleanup` in the `finally` at `:1362-1375`. Single-identity invariant `:1466-1472` untouched. | SATISFIED. |
| P-4 "mismatch → `readiness_identity_environment_dirty` naming EVERY differing field; unrealizable → `readiness_identity_artifact_unreadable` with the config path; the frozenset, `arm_readiness.py:233-246`, the `len == 56` census and the D-078 test stay byte-unchanged" | Dirty + all differing fields `identity_pins.py:1531-1550`; unreadable + path `:1256-1279, 1304-1330, 1490-1516`. | SATISFIED. Verified byte-unchanged: frozenset `identity_pins.py:38-46` (diff empty); `git diff c5fa8a49 717b1ddb -- joulewise/arm_readiness.py` → 0 lines; `len(READINESS_REASON_CODES) == 56` lives in `tests/test_arm_readiness_schemas.py:1670`, file not in the diff; `test_projection_reason_vocabulary_is_closed` (main 1169-1193) is byte-identical at head `tests/test_identity_pins.py:1488-1512`. No new reason codes. |
| P-5 "`check_id` MUST contain `shared_mint_projection` and `expected == observed` on PASS ... rows go into `probe_metadata` so `projection_input_sha256` binds them ... No receipt or receipt-unit fields added" | check_id `identity_pins.py:1552-1562` (`f"{unit_id}:{config_path}:shared_mint_projection:prompt_realization"`, `expected == observed` by construction); rows land in `probe_metadata` at `:1685` inside `projection_input_units`, hashed at `:1697`. | IMPLEMENTED; binding clause UNTESTED — see F1. `RECEIPT_FIELDS`/`RECEIPT_UNIT_FIELDS`/`UNIT_FIELDS`/`CHECK_FIELDS` all unchanged (only the new module-private `_PROMPT_REALIZATION_FIELDS` at `:135-139` was inserted in that range). The T0 tripwire `tests/test_arm_readiness_evidence_t0.py:2692-2703` is satisfied. |
| P-6 "Freeze: refusal escapes before any write. Arm: re-runs `_derive_projection_units`, emits an authenticated REFUSE receipt with pack bytes unchanged" | Refusal raised inside `_derive_projection_units` before any write; arm path unchanged and re-derives. Asserted by `tests/test_identity_pins.py:1220-1242` (`pack_bytes` equal after freeze refusal) and `:1272-1331` (`status == "REFUSE"`, `reason_codes == ["readiness_identity_environment_dirty"]`, `pack_bytes` equal). | SATISFIED. |
| P-7(a) "configs without an expectation gain no new probe/check payload — assert the EXACT legacy key set"; (b) "no issued receipt is rewritten" | `tests/test_identity_pins.py:1174-1218` hard-codes the six probe keys `{platform, machine, device, quantization, adapters, workload_provenance}`, `len(checks) == 1`, and the four-key envelope — literal, not derived from the code under test. Adapter side: `tests/test_mlx_runtime.py:465-467` hard-codes `{model, tokenizer, sampler, output_policy}`. No receipt bytes touched anywhere in the diff. | SATISFIED (the "derived expectation" failure mode is absent — both key sets are literals). |
| P-9 WRITE_SCOPE exhaustive | `git show --stat 717b1ddb`: exactly `joulewise/adapters/mlx_runtime.py`, `joulewise/identity_pins.py`, `tests/test_identity_pins.py`, `tests/test_mlx_runtime.py`. | SATISFIED. No kernel/decision-log/queue edits. |
| P-10 seven named tests | 1 `..._realizes_registered_prompt_with_collection_encoder` `tests/test_mlx_runtime.py:481`; 2 `..._omits_realization_without_expectation` `tests/test_mlx_runtime.py:450`; 3 `test_freeze_checks_every_registered_config` `tests/test_identity_pins.py:1220`; 4 `test_freeze_mismatch_names_all_differing_fields` `:1244`; 5 `test_arm_reverification_refuses_each_prompt_realization_drift` `:1272`; 6 `test_projection_refuses_unavailable_registered_realization` `:1333`; 7 `test_projection_check_ids_carry_shared_mint_projection` `:1382`. | ALL SEVEN PRESENT with the exact ruled names. Counterfactuals are real — see below. |

## Counterfactual / vacuity assessment (P-10)

Every one of the seven names a concrete failing input, and none is vacuous:
(1) asserts `tokenizer.encode_calls == [("registered projection prompt", True)]` — fails on `add_special_tokens=False` and KeyErrors without the feature; (3) drifts member-2 alone and asserts member-2's path is in the reason and member-1's is NOT — fails under a `configs[0]`-only mutant; (4) asserts `observed["differing_fields"] == ["token_count","token_ids_sha256","token_hash_domain"]` — fails if either hash field is ignored; (5) drifts each field independently across three subtests and asserts `REFUSE` + unchanged pack bytes — fails if arm trusts the frozen PASS; (6) drives both the missing-row arm and a real `RuntimeWithoutProjection` through `_runtime_probe_metadata`, asserting the config path is in the message; (7) asserts two ordered prompt checks, the substring over ALL checks, `expected == observed` over ALL checks, and the four-key envelope.

Test 2 passes with and without the feature by design — it is a must-not-add invariant, and it does kill the ruled "emit the realization row unconditionally" mutant. Not vacuous.

## Naming / ordering (deterministic, no false REFUSE)

`realization_configs` is built by `zip(config_inventory, typed_configs)` (`identity_pins.py:1470-1474`), and `_read_unit_configs` (`:1404-1435`) already REFUSES any unit whose `config_inventory` is not lexically sorted by path; `_validate_config_inventory` (`:394-416`) enforces sorted+unique paths at load. So realization-row order == lexical path order == the exact order of `receipt_unit["config_inventory"]` (`:1673`). Reordering configs in an unchanged pack cannot produce a new false REFUSE: such a pack is already refused by the pre-existing sorted-inventory guard, and the sorted order is order-insensitive to the pack's listing anyway. `test_projection_check_ids_carry_shared_mint_projection:1385-1390` pins the order explicitly. CLEAN.

## Findings

**F1 — SHOULD-FIX (verified surviving mutant). P-5's binding clause has no regression.**
`joulewise/identity_pins.py:1685` places the realization rows into the hashed
`projection_input_units[].probe_metadata`, satisfying "so `projection_input_sha256` binds
them". Nothing tests it. I materialized `git archive 717b1ddb` into scratch and replaced
`:1685` with
`"probe_metadata": {k: v for k, v in metadata.items() if k != "prompt_realizations"},`
— rows still validated, checks still emitted, binding gone. Result:
`Ran 75 tests in 6.008s / OK`. The mutant survives every one of the seven ruled tests.
Consequence if it ever regresses: a frozen `_v5` projection receipt's
`projection_input_sha256` no longer covers what was realized, so realization evidence is
carried only by the `checks` array and is not tamper-evident in the input hash — the exact
property P-5 was written to buy. Cure: extend
`test_legacy_projection_probe_and_checks_keep_exact_key_sets`' existing
`canonical_json_sha256` capture hook (`tests/test_identity_pins.py:1180-1200`) to a
positive case — freeze an expectation-bearing pack, assert the captured
`captured_inputs[0][0]["probe_metadata"]["prompt_realizations"]` equals the two ordered
rows; counterfactual input = the M7 dict-comprehension above; production call site =
`identity_pins.py:1685`. Roughly a 12-line test; bench-sized.

**F2 — NIT. Pre-existing test renamed rather than added.**
`tests/test_mlx_runtime.py:450` renames `test_identity_projection_metadata_uses_loaded_tokenizer_and_sampler_probe`
→ `..._omits_realization_without_expectation`. The ruled name is now present and the old
body is retained with a 3-line key-set assertion prepended, so coverage is not lost. I
grepped the whole checkout: no doc, script, or CI file references the old name. No action
needed; flagged only because the P-10 list reads as "add", not "rename".

**F3 — NIT. Two f-strings with no placeholders.** `identity_pins.py:1356`
(`f"identity projection probe failed"`) and `:1366` (`f"runtime cleanup failed"`) — the
`f` prefix is inert since the interpolation moved to the concatenated suffix. Ruff would
flag F541; CI (`.github/workflows/ci.yml`) runs no linter, so cosmetic only.

**F4 — NIT. Cleanup-failure detail names an arbitrary config.** In the `finally` block
(`identity_pins.py:1362-1375`), `realization_path` still holds the LAST candidate visited
by the projection loop, but `cleanup` is a single per-unit operation. A cleanup failure
will read "for config configs/member-N.json" and invite a reader to blame that config.
Suggest dropping the suffix on the two cleanup refusals, or using the representative path.

**F5 — NIT (checked, benign). Representative's realization is bound twice.**
`mlx_runtime.py:344` attaches `prompt_realization` to the adapter's projection dict, and
`identity_pins.py:1397` stores that whole dict as `metadata["workload_provenance"]` — so
for an expectation-bearing unit the representative's triple appears both inside
`workload_provenance` and inside `prompt_realizations`. I verified this does NOT breach
P-5's "no receipt or receipt-unit fields added": `build_stack_identity`
(`identity_pins.py:255-330`) reads only named sub-keys (`model`, `tokenizer`, `sampler`,
`output_policy`), so nothing reaches `realized_stack_identity`, `runtime_identity_sha256`,
or any receipt field. Redundant payload in the hashed input only.

**F6 — NIT. P-3's "prepare once / clean up once" is asserted only one level up.**
`test_projection_check_ids_carry_shared_mint_projection:1383` asserts
`self.probe_mock.assert_called_once()`, but the probe itself is stubbed in every
identity-pins test, so the prepare/cleanup call counts inside `_runtime_probe_metadata`
are never observed. An execution-lens concern more than a contract one; the
`RuntimeWithoutProjection` arm at `:1355-1381` is the only test that enters the real
function, and it dies before the loop.

**F7 — NIT. Comment cites the wrong ruling.** `identity_pins.py:1400` reads
`# Ruling 44c P-2:`; 44c is the forcing problem and has no P-2 — the operative clause is
141a P-2. One-word fix.

## Outside the rulings' remit

Nothing. No new public API (`_runtime_probe_metadata` gains a second parameter but keeps a
default and is still called with one argument on the legacy path at `identity_pins.py:1486`,
so every existing 1-arg test stub survives). No error message that another test or doc pins
was altered — for legacy packs `realization_path` is `None` (`identity_pins.py:1298`) and
all pre-existing refusal strings are byte-identical. No docstring claims added. Nothing
touched outside P-9's four files.
