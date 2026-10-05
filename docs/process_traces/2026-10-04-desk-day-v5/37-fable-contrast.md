FINAL PASS: PASS

Cold final pass on `a42a26fd` (parent `8fa002f7`), PR #473: `configs/campaigns/d117_contrast_v5/generate_configs.py` and `tests/test_d117_contrast_v5_pack.py`. No BLOCKER, no MAJOR. Two MINOR, four NIT. Nothing below needs to change before merge.

## What I executed (all in /tmp/dd5-fable-ct, fixture pin only, real pin never opened)

- Tests: full `tests/test_d117_contrast_v5_pack.py` -> 48 passed, 106 subtests passed (119 s), including the three new tests and the existing freeze-and-verify test. Checkout left clean (`git status` empty).
- Base-vs-head generation: generated the pack with the base generator (`8fa002f7`) and the head generator from the same panel, workload and fixture pin, then diffed the trees.
- Mutation probe M1: removed the pin comparison in `main()` (generate_configs.py:3626-3627) in a scratch copy and ran the drift test.
- Tamper probes P0/P1/P1b/P2 against a scratch replay fixture, through `arm_readiness_evidence._recorded_generator_check` (the same subprocess the PACK_AUTHENTICATION kind uses).

## Question 1 — can drifted inputs or outputs authenticate?

No, for the original tree. Evidence:

- P0 clean pack -> PASS.
- P1: one byte appended to `generator_inputs/decode_workload.json` AND its sha re-pinned inside the pack generator, outputs untouched -> REFUSED, `production bytes differ from regeneration: plan_tree.json`.
- P1b: same drift with the generator's pin map emptied -> REFUSED on `plan_tree.json`; `_pinned_artifact` separately refuses the edited generator (`primary artifact is not byte-identical to HEAD`).
- Mechanism (generate_configs.py:405-433, 3098-3105, 3622-3627): committed `plan_tree.json` pins the generator sha; the generator source carries the sha256 of all five carried inputs; `embedded_generator_bytes()` re-derives that map from the bytes actually read, so any input drift changes the regenerated generator sha and therefore `plan_tree.json`. `main()` additionally refuses before configuration with `pinned replay input drifted`.
- Note on `check()` (generate_configs.py:3560-3568): under the emitted generator the byte comparison of the five carried inputs is a self-comparison (read from the pack, compared with the pack). It adds nothing there; the two detectors above are what hold, and both were exercised.

Tampered copies plus regenerated outputs: see MINOR-1. They authenticate only as a different tree (different `plan_tree.json`, different generator pin), never under the original tree bytes.

## Question 2 — science configs unchanged?

Yes. Base-vs-head diff of the generated pack: 115 files at base, 120 at head. 110 byte-identical, 5 changed, 5 new.

- Identical: `calibration_plan.json` (plan sha equal at base and head), all run configs, all order manifests, decode suite manifests, the four condition families, `prefill_prompt_candidate.json`, `analysis_manifest_v3.json`, `consumer_family_declaration.json`.
- Changed: `generate_configs.py`, `README.md` (regeneration command only), `plan_tree.json` (exactly: generator sha, the three acceptance fields, the `decode_workload_candidate.json` pin), `plan_tree.sha256`, `decode_workload_candidate.json` (see MINOR-2).
- New: `generator_inputs/model_panel.json`, `generator_inputs/decode_workload.json` (both `cmp`-identical to `configs/model_panels/qwen3_4bit.json` and `configs/workloads/real_prompts_v1.json`), and the three-file `prefill_pin/` bundle.

## Question 3 — acceptance binding

Exact. `SUCCESSOR_ACCEPTANCE` (generate_configs.py:466-475) equals the registry live default field for field: `calibration_bracketing.ACTIVE_ACCEPTANCE_ID` = `d079_calibration_acceptance_v2_n24_25g83_r2`, `relative_path` equal, `file_sha256` `f949f511…3660` equal to `shasum` of the artifact on disk, `derivation_sha256` `10965d36…e5c0` equal to the loaded artifact. The pack binds the artifact by sha, and that artifact carries `ledger_cutoff.sequence` 376 with role `issued_acceptance_baseline`; the live head pin (`configs/calibration/calibration_ledger_head.json`) is at 402 and appears nowhere in the binding. `arm_readiness._issued_d079` (arm_readiness.py:6205-6222) already lists the new id, so the readiness routing accepts it.

## Question 4 — do the tests kill what they claim?

- M1 (pin comparison removed): `test_generic_replay_refuses_one_byte_output_and_input_drift` fails 2 of 3 subtests -> killed.
- Reverting the acceptance id or either sha fails `test_successor_acceptance_is_registry_live_default_with_issued_cutoff` by direct equality against the registry (read, not executed).
- Dropping the baked defaults, the carried-input writes, or the `--preserve-current-frozen-bytes` argument fails `test_emitted_generator_passes_generic_pack_authentication` (required arguments, inventory, flagless-allowlist refusal respectively; read, not executed).

## Findings

**MINOR-1 — authentication proves self-consistency, not where the carried inputs came from.** generate_configs.py:1151-1164, 3622-3627; tests:1055-1082.
Probe P2: drift a carried input, re-pin it in the pack generator, re-run the pack generator in generate mode -> the generator check PASSES, under the same pack name and plan id, with a changed `plan_tree.json` and generator pin. Nothing in this change compares the carried copies with `configs/model_panels/qwen3_4bit.json`, `configs/workloads/real_prompts_v1.json` or the issued pin bundle, and the README no longer records the source paths (generate_configs.py:2924-2927). This is the same in kind as base (the base generator used whatever paths the command line supplied), so it is not a regression. Control at the pack-landing step: run the SOURCE generator `configs/campaigns/d117_contrast_v5/generate_configs.py --panel … --decode-workload … --prefill-prompt-pin … --check` with the canonical paths against the committed pack. That comparison is real, because there the carried bytes come from the command-line paths, not from the pack.

**MINOR-2 — `decode_workload_candidate.json` changes, so "science configs byte-identical" needs the precise reading.** generate_configs.py:1171-1173, 1588.
`profile.path` now names the pack copy instead of the command-line path, and the `plan_tree.json` pin for that file changes with it. Profile id, prompt-set sha, renderings and token ids are identical. The new value is deterministic (base wrote whatever string was typed, absolute paths included), which is an improvement.

**NIT-1 — dead state.** generate_configs.py:1165-1168: `PANEL_FILE_ARGUMENT` and `PREFILL_PIN_FILE_ARGUMENT` are assigned but no longer read anywhere.

**NIT-2 — comment over-claims.** generate_configs.py:1149-1150 says no original checkout path is replay input. The emitted generator still reads repository files outside the pack (the decode-assignment supersession record under `configs/campaigns/d117_contrast_v5/`, campaign policy, reference manifests, `joulewise/`); the test fixture has to copy them (tests:999-1014). These dependencies predate the change. I did not verify whether the supersession record is hash-bound into the outputs.

**NIT-3 — drift test covers 2 of 5 carried inputs.** tests:1062-1066 exercises the workload and the selection record; panel, pin and ladder go through the same loop and are not exercised individually.

**NIT-4 — README regeneration command is untested.** generate_configs.py:2924-2927; no assertion on the emitted command text.

## Not done

- Wider suite not run (only `tests/test_d117_contrast_v5_pack.py`, all 48 tests).
- Real pin bundle not opened; all probes used the test fixture pin.
- Frozen-pack path (`_recorded_projected_pack_authentication`) read, not executed beyond the existing freeze-and-verify test.
