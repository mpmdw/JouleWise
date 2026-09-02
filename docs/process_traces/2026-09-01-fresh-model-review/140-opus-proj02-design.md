# Design consult — V5-PREFILL-REALIZED-PROJECTION-02 (Opus 5, CONTRACT lens)

**Verdict: DESIGN-READY** (one stop condition in §11; one option refused as ruling-bearing in Q3).
Read-only pass over `/Users/edr/code/JouleWise-wt-proj02` @ `4a41d791`. No files written in the repo.

## Proposed WRITE_SCOPE (exhaustive)

`joulewise/identity_pins.py`, `joulewise/adapters/mlx_runtime.py`, `tests/test_identity_pins.py`,
`tests/test_mlx_runtime.py`, `docs/process/state_kernel.json`, `RUN_STATE.md`, `TASK_QUEUE.md`
(kernel-generated interiors only, via `scripts/gen_state.py`).

Deliberately EXCLUDED so they act as tripwires the implementer cannot "fix":
`tests/test_arm_readiness_evidence_t0.py` (its `check_id` and `expected == observed` assertions at
`:2688-2703` are the legacy-invariance guard), `joulewise/arm_readiness.py`, `joulewise/schemas.py`,
`joulewise/bundle_read.py`, `tests/goldens/**`, every `configs/campaigns/**` pack, and
`configs/campaigns/d117_contrast_v5/generate_configs.py` (never in any seat's scope).

## Spec (numbered; buildable without the brief)

1. **Trigger condition.** A config is in scope iff its typed `workload_profile.prompt_token_expectation`
   is not `None` (`joulewise/schemas.py:843-893`; omission-serialized at `:1137`, and the schema forces
   `prompt_text` alongside it at `:312-316`). `_v5` prefill configs carry it
   (`configs/campaigns/d117_contrast_v5/generate_configs.py:1339-1351`); decode and all legacy configs
   do not. Absence is never a refusal here (Q3).
2. **New adapter probe.** Add `MlxRuntimeAdapter.realized_prompt_expectation(config) -> dict` beside
   `identity_projection_metadata` (`joulewise/adapters/mlx_runtime.py:315`). Same pre-guard
   (`self._tokenizer is None` → `AdapterFailure`). Body: `token_ids, _, text = self._prompt_for_workload(config)`
   (`:931-937`) then `return prompt_provenance(token_ids, text=text)` (`joulewise/provenance.py:318-324`).
   Reusing `_prompt_for_workload` — not a re-implementation — is load-bearing: it is the exact call the
   night makes (`:384`), including `_encode(..., add_special_tokens=True)` (`:936`, `:1100`), so freeze
   and collection cannot diverge. Refuse (`RuntimeError`/`AdapterFailure`) if the profile has no
   `prompt_text`; the schema makes that unreachable for in-scope configs.
3. **Conditional probe call.** In `_runtime_probe_metadata` (`joulewise/identity_pins.py:1251`), inside the
   existing `try/finally` so `cleanup` still runs (`:1291-1303`), and only when the config carries an
   expectation: resolve `realized_prompt_expectation` with the same `getattr`/`callable` pattern used for
   the projector (`:1276-1281`); if absent → `IdentityPinProjectionError("readiness_identity_artifact_unreadable", …)`;
   otherwise set `metadata["prompt_realization"] = result`. **When the expectation is absent the key is not
   set at all.** That is what preserves legacy bytes: `metadata` rides into `projection_input_units[*].probe_metadata`
   (`:1523`) and is hashed into `pack.projection_input_sha256` (`:1534`, `:1653`).
4. **Comparison, in `_derive_projection_units`** (`:1364`), placed after the runtime-probe identity check
   (`:1475-1497`) and before the `config_set_sha256` check (`:1498`). For **each** config in `configs`
   (not just `representative`): take its typed expectation; skip when `None`; require
   `metadata["prompt_realization"]` (else `readiness_identity_artifact_unreadable`); compare
   `token_count` vs `realized_token_count`, `token_ids_sha256`, `token_hash_domain`, and
   `sha256(prompt_text)` vs `text_sha256` — mirroring the bundle fence at
   `joulewise/bundle_read.py:1052-1076`. Any difference → one refusal
   `IdentityPinProjectionError("readiness_identity_environment_dirty", f"identity unit {unit_id!r} realized prompt differs from the registered expectation for <fields>", observed={"registered": …, "realized": …, "config_path": …})`,
   with the message naming which of count / ids-hash / domain / text differed.
5. **Receipt evidence.** For units with an expectation, append one check row
   `{"check_id": f"{unit_id}:prompt_realization", "status": "PASS", "expected": <triple>, "observed": <triple>}`
   to `checks`. `expected` must equal `observed` on PASS — `tests/test_arm_readiness_evidence_t0.py:2698-2703`
   asserts it globally. Emit **no** row when there is no expectation: `:2693-2697` asserts every `check_id`
   contains `shared_mint_projection` on the legacy fixture. `CHECK_FIELDS` is exact-key but `checks` is an
   open array (`joulewise/identity_pins.py:711-716`), so no schema version moves.
6. **Derivation binding.** Add `MlxRuntimeAdapter.realized_prompt_expectation` to the `callables` tuple
   (`:1148-1160`). The list is validated only for uniqueness/nonemptiness (`:591-605`), so this is legal, and
   D-131 cl.3 ("one shared implementation… derive, never enter") wants the realizer bound by name.
7. **Arm needs no new code.** `verify_frozen_projection` re-runs `_derive_projection_units` (`:2007`) inside
   the `try` that converts any `IdentityPinProjectionError` into a REFUSE arm receipt with its reason code
   (`:2022-2040`), written immutably to window custody (`:2053-2064`). D-131 cl.5 makes every U11 reason a
   readiness REFUSE (`docs/decision_log.md:8434-8438`), consumed at `joulewise/arm_readiness.py:5681-5719`
   before GO — i.e. before the first joule.
8. **No new reason codes** (Q3) and **no schema-version bumps** anywhere.
9. **Order of landing.** This PR must merge **before** the desk-day `_v5` pack generation and freeze (§11).
10. **Non-goals.** No comparison of arm-realized against freeze-realized beyond what
    `projection_input_sha256` equality already gives (`:2010-2015`); no change to `BundleReader.problems()`
    (row 01 owns the bundle fence); no generator, pack, or registration edit.
11. **Stop condition.** If, at land time, any pack that still needs to arm is already `frozen`, STOP and
    escalate: see Q4 — the derivation-hash fence retires it.

## Q1 — is the tokenizer already in hand at freeze? **Yes.**

`identity_projection_metadata` refuses unless `self._mlx_lm`, `self._model` and `self._tokenizer` are all
loaded (`joulewise/adapters/mlx_runtime.py:320-324`), and `_runtime_probe_metadata` calls it only after
`runtime.prepare(config)` succeeded (`joulewise/identity_pins.py:1269-1282`), which is what loads the model
and tokenizer. So the cheapest catcher is exactly the brief's: re-encode the registered `prompt_text`
through `_prompt_for_workload`/`_encode(add_special_tokens=True)` and compare the triple. Marginal cost:
one ~4k-token encode per identity unit; no extra load, no model call.

**Legacy invariance proof (receipt construction).** The receipt's only inputs are `receipt_units`
(`:1504-1513`: declaration, config inventory, model-file inventory, realized stack identity, triple),
`pack` (`:1648-1654`), `derivation` (`:1191-1196`), `observations` (`:1678-1682`) and `checks` (`:1683`).
`build_stack_identity` reads named keys only and is length-checked by field set
(`:308-341`), so an added `metadata` key cannot leak into `realized_stack_identity` or the triple. The one
metadata-sensitive output is `projection_input_sha256` (`:1523`, `:1534`) — and §3 makes the new key
conditional. Therefore a config with no expectation projects to **byte-identical** units, pack fields and
checks; the only field that moves is `derivation.source_file_sha256`, which moves for *any* code change by
design (Q4).

## Q2 — per config, realized once per unit

Compare per config; probe once from `representative` (`:1390`). Honest caveat: today the loop is
*unfalsifiable*. `scientific_config_identity` includes the whole typed config (`:212-231`), `workload_profile`
included, and `_derive_projection_units` already refuses a unit whose configs have more than one scientific
identity (`:1383-1389`), while `_declared_identity_from_config` pins `workload_profile` — with the
expectation inside it — against the pack (`:1231-1248`, `:1376-1382`). The `_v5` generator emits one unit per
(arm, measurement_arm) with the expectation inside `declared_identity.workload_profile`
(`generate_configs.py:2567-2607`), so A and B are already separate units and never share an expectation
operand. Keep the loop because it costs nothing and survives a future relaxation of `:1383`; do **not**
claim it closes a defect (no mutant kills it — see Q6).

## Q3 — refusal naming: **reuse, do not extend**

`IDENTITY_PIN_PROJECTION_REASON_CODES` is a closed frozenset (`joulewise/identity_pins.py:38-46`) that is
unioned into `READINESS_REASON_CODES` (`joulewise/arm_readiness.py:233-246`), pinned by count
(`tests/test_arm_readiness_schemas.py:1670`: `len == 56`), mirrored by the census literal in
`joulewise/arm_readiness_evidence.py:2338-2352` and cross-asserted by
`tests/test_arm_readiness_integration.py:583-639`, whose justification string names
`test_all_five_u11_refusals_propagate_through_identity_row` (`:395`, `:621`). The five identity spellings
were admitted by an explicit D-078 registry amendment (`docs/decision_log.md:8438-8452`). **Adding a sixth
is a registry amendment — a ruling, not a design choice**, and it risks a consumer that enumerates codes
not knowing it. Use:
- mismatch (count / ids-hash / domain / text) → `readiness_identity_environment_dirty`, the code the
  adjacent tokenizer-drift refusal already uses (`identity_pins.py:1486-1497`); the *message* names the
  differing fields and `observed` carries registered vs realized.
- expectation present but unrealizable (no tokenizer, adapter without the hook) →
  `readiness_identity_artifact_unreadable`, matching the missing-projector refusal at `:1278-1281`.
- absence of an expectation → not a refusal here. Confirmed: row 01 owns absence at the bundle
  (`joulewise/bundle_read.py:942-943` returns `[]`, and `evidence_missing` is its neither-branch), and a
  projection-side absence refusal would refuse every legacy and decode unit.

## Q4 — freeze vs arm; what moves

Arm is a **re-run of the same function**, not a comparison against the freeze receipt (`:2007`), so the
check comes for free and the freeze receipt need not carry the realized triple for the mechanism to work
(it carries it as evidence only, §5). Artifacts that move: **none that are golden or committed.** No
receipt file is ever rewritten — freeze appends the next `projection-NNNN.json` (`:1867-1876`) and arm
receipts are immutable-write (`:1805-1823`), so D-167's evidence-immutability fence is untouched.
`tests/goldens/config_schema.json` does not move (row 01 already landed the schema).
The real cost is elsewhere and must be stated in the PR: `_derivation_record` hashes the source of every
bound callable (`:1163-1190`) and `_same_derivation_identity` compares those hashes (`:1199-1205`), so **any**
edit to `identity_pins.py` or `mlx_runtime.py` makes every already-frozen pack refuse at re-freeze
(`:1846-1850`) and at arm (`:2002-2006`) with `readiness_identity_projection_mint_divergence`. The committed
Qwen2.5 receipts pin the old digest (e.g.
`configs/campaigns/d117_floor_qwen25_1p5b_v1/identity_pin_projection.receipts/projection-0001.json:53`).
Acceptable because those packs are retired by D-167 cl.2, and because
`configs/campaigns/d117_contrast_v5/` holds only the generator — no `_v5` pack or receipt exists yet. If
that changes before merge, the pack needs the D-131 cl.4 successor reissue and the row needs a ruling.

## Q5 — gates the implementation PR must pass

D-131 makes `identity_pins.py` arm-critical (cl.1-5, `docs/decision_log.md:8394-8438`); the kernel row's own
status note says "council trigger" (`docs/process/state_kernel.json:5341`); the council skill's full-council
trigger is "any change to shared contract-bearing code". Gates: (1) implement in a linked worktree under
the exhaustive WRITE_SCOPE above; (2) independent audit — never self-graded; (3) **two refuters with
distinct lenses** — contract (schemas/receipt/reason vocabulary/immutability) and execution+mutation — since
this is arm-critical; (4) fix rounds with defect-shaped regressions and a **delta re-audit of every fix
round**; (5) rule-11 same-signature escalation → cold gate before any third round; (6) full named modules
green: `tests/test_identity_pins.py`, `tests/test_mlx_runtime.py`, `tests/test_arm_readiness_evidence_t0.py`,
`tests/test_arm_readiness_integration.py`, `tests/test_arm_readiness_schemas.py`,
`tests/test_arm_readiness_lifecycle.py`, plus CI; (7) D-121 terminal review of the FINAL head before merge;
(8) **magistrate live verification (rule 1): one real `freeze_projection` on the actual `_v5` pack with the
real model on the desk day, before the night** — the stubbed tests never exercise the true tokenizer path,
and that is precisely the drift this row exists to catch.

## Q6 — tests (name / one assertion / counterfactual) and mutants

All in `tests/test_identity_pins.py` unless noted; the seam is the existing
`mock.patch("joulewise.identity_pins._runtime_probe_metadata", …)` fixture (`tests/test_identity_pins.py:406-410`,
`:475-477`). Production call site for T1-T4, T6: `freeze_projection` → `_derive_projection_units`
(`identity_pins.py:1835`); for T5: `verify_frozen_projection` (`:2007`).

- **T1 `test_freeze_refuses_realized_prompt_count_mismatch`** — raises `readiness_identity_environment_dirty`
  and the message names `token_count`. Counterfactual: stub realization with `realized_token_count = registered + 1`
  (a tokenizer that starts emitting an extra BOS between desk and night).
- **T2 `test_freeze_refuses_realized_ids_hash_mismatch_at_equal_count`** — same refusal naming
  `token_ids_sha256`. Counterfactual: identical count, different `token_ids_sha256` (chat-template/special-token
  change). Kills a count-only implementation.
- **T3 `test_freeze_refuses_token_hash_domain_mismatch`** — refusal names `token_hash_domain`.
  Counterfactual: `"joulewise.suite_prompt_token_ids.v1"` (`joulewise/provenance.py:13`).
- **T4 `test_freeze_refuses_when_expectation_present_but_realization_absent`** — raises
  `readiness_identity_artifact_unreadable`. Counterfactual: probe metadata without `prompt_realization`
  (an adapter with no hook).
- **T5 `test_arm_reverification_refuses_realized_drift`** — the returned status is `REFUSE`,
  `reason_codes == ["readiness_identity_environment_dirty"]`, and the custody receipt on disk carries them.
  Counterfactual: freeze with a matching stub, then re-stub drifted before `verify_frozen_projection`
  (an `mlx_lm` upgrade between the desk day and the night).
- **T6 `test_pack_without_expectation_projects_byte_identically`** — the frozen receipt bytes for a
  no-expectation pack contain no `prompt_realization` substring and `checks` is exactly the one
  `…:shared_mint_projection` row. Counterfactual: unconditional emission.
- **T7 `test_realized_prompt_expectation_matches_the_collection_encode`** (`tests/test_mlx_runtime.py`) — a
  recording fake tokenizer shows the encode used `add_special_tokens=True` and the result equals
  `prompt_provenance(_prompt_for_workload(config)[0], text=…)`. Counterfactual: `add_special_tokens=False`
  at freeze (silent off-by-one against `mlx_runtime.py:936`). Production call site: `_runtime_probe_metadata`.
- **T8 `test_derivation_binds_the_realization_probe`** — the freeze receipt's `derivation.callables`
  contains `joulewise.adapters.mlx_runtime.MlxRuntimeAdapter.realized_prompt_expectation`.
  Counterfactual: an unbound helper whose edit would not invalidate a freeze.

Mutants: **M1** drop the ids-hash comparison → T2. **M2** make `metadata["prompt_realization"]`
unconditional → T6 and `tests/test_arm_readiness_evidence_t0.py:2693-2697`. **M3** encode with
`add_special_tokens=False` → T7. **M4** turn the missing-realization branch into a `return`/`pass` → T4.
**M5** move the check from `_derive_projection_units` into `freeze_projection` → T5. **M6** compare the
registered value against `declared_identity`'s copy instead of the probe (a tautology) → T1/T2.
No mutant kills the per-config loop (Q2) — stated, not hidden.

## Q7 — generator / frozen registration: **nothing is touched**

`configs/campaigns/d117_contrast_v5/generate_configs.py` is read-only input to this design: the expectation
it emits (`:1339-1351`) and the pack declaration that mirrors it (`:2567-2607`) are consumed, never edited,
and `dominance_criterion_registration()` is not read by any code on this path. Two adjacent facts the
implementer must not act on alone: (a) if the desk-day freeze refuses with a realized mismatch, the cure is a
new pin / regenerated pack — a ruling-bearing event, not part of this row; (b) if the pack's
`declared_identity.workload_profile` were found *not* to carry the expectation, STOP — do not "fix" the
generator. Both are NEEDS_RULING, not design choices.

## Disagreement with the row's framing

1. **"Defense-in-depth, not the fence" understates it, and 44c's own reasoning shows why.** Row 01 fires on
   the first *succeeded* prefill bundle; this row fires before the model is measured at all *and* — because
   the same function runs at arm (`:2007`) — it is the only mechanism that catches drift arising **between**
   the desk-day freeze and the night. Row 01 cannot see that window at all. I would record it as an
   independent fence over a different interval rather than a second copy of the same one.
2. **Q3's premise (propose new names) is the wrong default.** The vocabulary is closed and triply pinned
   (Q3); reuse also inherits the wiring that already makes the refusal stop the arm. New spellings buy
   readability at the price of a registry amendment and a fail-open risk in any consumer that enumerates.
3. **The domain comparison is nearly tautological and should be labelled as such.** `schemas.py:71` and
   `provenance.py:12` define the same literal twice and the schema already refuses any other registered
   domain (`schemas.py:872-876`), so the check can only fire on cross-module constant drift. Keep it
   (it is free), but do not sell it as an operator-error catcher — and consider a follow-up nit row to give
   that constant one home.
4. **The acceptance line "at freeze and arm" invites a second implementation.** It should be read as one
   implementation in `_derive_projection_units`; a separate arm-side comparison against the freeze receipt
   would be a duplicate with its own drift surface, exactly the duplication 44c struck for `inputs.py`.
