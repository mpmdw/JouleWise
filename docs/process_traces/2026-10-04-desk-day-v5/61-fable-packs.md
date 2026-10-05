FINAL PASS: PASS

Cold final pass on `git diff origin/main..ca5f3f11` (branch desk/2026-10-04-v5-pin-and-packs):
the issued prefill prompt pin bundle, the three generated `_v5` pack trees, two test updates.
Reviewer: Claude Fable 5.1, one foreground session, no subagents, scratch `/tmp/dd5-fable-pk/`.
The selected prefill length is written `L` throughout; path components that spell it are written `p<L>`.

No blocking or medium finding. Five low/informational notes are at the end; none requires a byte change.

## 1. Pin re-issue (PASS)

Command run from this checkout (venv python, `PYTHONPATH=.`, `TMPDIR` in scratch):
`scripts/issue_g2a_prefill_prompt_pin.py --harvest /Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/harvest.json --registration configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md --output /tmp/dd5-fable-pk/pin/prefill-prompt-pin.json` → exit 0.

| File | sha256 | `cmp` against `configs/campaigns/d117_contrast_v5/prefill_pin/` |
|---|---|---|
| `prefill-prompt-pin.json` | `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb` | identical |
| `selection.json` | `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222` | identical |
| `prefill-prompt-ladder.json` | `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885` | identical |

Bindings, each checked directly rather than taken from the issuer's exit code:

- Harvest: `verdict` SELECT, `cause_codes` `[]`, plan `d117-g2a-prefill-probe-20261004T1305Z`.
- `pin.g2a_record_sha256` = `harvest.selection.sha256` = `harvest.outputs["selection.json"]` = sha256 of the committed bundle copy = `c694c488…`.
- The archive's `derived/selection.json` is byte-equal to the bundle copy.
- `harvest.json` and `selection.json` are byte-equal to the committed records under `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T1305Z/` at both HEAD and `origin/main`.
- `selector.select(summary, summary_sha256=sha256(derived/summary.json))` equals the selection record exactly (Python object equality); `derived/summary.json` matches `harvest.outputs["summary.json"]`.
- Selection is `status: selected`, `refusal: null`, `selected_prefill_tokens == collection_prefill_tokens == L`.
- Independent read of the rule against the four summary rows (small members / minimum small count): rung 1 5/3, rung 2 5/4, rung 3 5/7, rung 4 5/12. The first rung with five small members all at count ≥ 5 is rung 3, and rung 3 is L.
- Pin internals: `prefill_length == prompt_tokens == len(prompt_token_ids) == L`; ids and text equal the ladder's L rung; `prompt_token_ids_sha256` and `prompt_text_utf8_sha256` recompute; `panel_sha256` equals sha256 of `configs/model_panels/qwen3_4bit.json`; `selection_record.sha256` and `prompt_ladder.sha256` equal the bundle copies.

## 2. Regeneration and `--check` (PASS)

Scratch clone `/tmp/dd5-fable-pk/clone` at `ca5f3f11`; deleted all 364 files this change adds outside `d117_contrast_v5/prefill_pin/` (only the two floor `generate_configs.py`, already on main, remained); ran the runsheet Phase D contrast command (prefill length read by `jq` from the selection record) and each floor generator with `--prefill-prompt-pin configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json`.

Result: `git status --porcelain` in the clone is empty — 0 changed, 0 missing, 0 extra files.

| Pack | calibration_plan sha256 | plan_tree sha256 |
|---|---|---|
| contrast | `b3f4679563f7d2bd84291a386b2e3fd8662cb2f7eaa7f492b2ee09544565d7ef` | `37e0beea4634220026540ea3fe67a9f1e5b8c898baf6ed98b5582ec651e9cbb6` |
| floor 1.7B | `f4992afbfa3e948c70714c6a463dceef73a638a98178379f8f992cb1e6505c54` | `e30fdf675e8b18e76142723c4f12baaf9366c0a74f37a5070e3e87d32eb2aefa` |
| floor 8B | `fed2a431162d8f0938d573a33d048862dac36947a7d2828280f4174c8724d949` | `c2c483525cde4d36e46bbd8f9edcf29be9b24bda212ed06d9eba086f297d64a7` |

`--check` in the real checkout, all exit 0 with the same hashes:

- source contrast generator with the Phase D arguments;
- emitted contrast generator, bare and with `--no-preserve-current-frozen-bytes` (it replays from its baked `generator_inputs/` and `prefill_pin/`, whose sha256s it pins at `generate_configs.py:21`);
- each floor generator, once with its default in-pack pin copy and once with the issued pin.

The emitted contrast generator differs from the source generator in exactly one line (line 21, `EMITTED_REPLAY_INPUTS`). The checkout was clean after all runs.

## 3. Content (PASS)

**Pin bytes in the packs.** In all three packs `prefill_pin/prefill_prompt_pin.json`, `selection.json` and `prefill-prompt-ladder.json` are byte-identical to the issued bundle, and each `prefill_pin/` holds exactly those three files. Floors and contrast therefore bind the same pin bytes (`d1209f6d…`).

**Prefill members** (50 per floor, 40 in the contrast, 140 total). Members carry the prompt text plus a token expectation (count and ids hash), not the id list itself. Within each pack all prefill members share one identical `workload_profile`; in all three:

- `prompt_text` equals `pin.prompt_text`;
- `prompt_token_expectation.token_count` equals L;
- `token_ids_sha256` equals `pin.prompt_token_ids_sha256`, which recomputes from the pin's id list;
- `model.tokenizer_json_sha256` equals `pin.tokenizer_json_sha256`;
- directory, file name and `run_id` carry `p<L>`, and `run_id` equals the file stem.

Independent tokenizer check (tokenizer files only, no model loaded): `tokenizer.json` in both the 1.7B and the 8B mirror hashes to the pin's tokenizer hash, and encoding `pin.prompt_text` through the adapter's `_encode(..., add_special_tokens=True)` under each returns exactly the pin's ids with length L. The issuer only checks the 1.7B mirror; the 8B result is new evidence that the same ids apply to both models.

**Decode members** (50 per floor, 40 in the contrast).

- `output_tokens` is 512 and `repetitions` is 1 on all 280 members.
- Every decode member's `suite_manifest_ref` is inside its own pack and exists.
- Every referenced manifest has one item with `output_policy: fixed_budget_exact`, `planned_output_tokens: 512`, `decode_level: forced_512_tokens`, and tags `d166-real-prompt` and `enable-thinking=false`.
- Floors reference one manifest each; the contrast references `01_sky_color.json` per model (fixed prompt zero, `d166_fixed_prompt_zero.v1`).
- Re-rendered prompt 0 of `configs/workloads/real_prompts_v1.json` through each mirror's chat template with `enable_thinking=False` and `add_generation_prompt=True`: the result equals the manifest ids in both floors, the contrast, and the floor `decode_workload_candidate.json`. It is 42 tokens ending in the empty think block; the thinking-on render is 38 tokens and differs, so the manifests encode thinking off.
- The chat template hashes to the `87a2728c…` the members bind.
- All 16 contrast manifests (8 prompts × 2 models) equal their thinking-off renders with forced 512.
- `generator_inputs/decode_workload.json` and `model_panel.json` are byte-identical to the repository sources.

**Acceptance.** `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` hashes to `f949f511…7b3660`; its `ledger_cutoff` is sequence 376, head digest `a5b825b7…f57014`.

- Floors: `plan_tree.json:29-39` binds the id, path, artifact sha `f949f511…`, derivation sha `10965d36…` and `issued_ledger_head.head_sha256 = a5b825b7…`, which is the acceptance cutoff digest. All six `extraction_spec.json` cells carry the same id, path, artifact and derivation hashes.
- Contrast: `plan_tree.json:35-38` binds the id, artifact sha and derivation sha.
- No pack contains any reference to the predecessor acceptance (`…_v2_n19`, `31611396…`, `4f6633d5…`).

**Paths.** Walked every string in all 369 added files. No reference to `night-g2a`, `night-archive`, `night-custody`, `/tmp`, `/private`, `/var`, `/Volumes` or `~`. The only absolute path is the model mirror (note N2). All manifest, acceptance and policy references are repository-relative.

**Internal integrity.** 1,820 `config_sha256` references to member files across the plan, order-manifest and spec artifacts all match file bytes; all six `.sha256` sidecars match.

## 4. Test updates (PASS — honest)

`tests/test_campaign_generator_core.py:76` adds the emitted contrast generator to `LIVE_V5_GENERATORS`. The census test (`:193-199`) requires every `d117_*/generate_configs.py` to be declared live or historical, so the new file had to be classified. "Live" is the stricter class: `:248-259` then requires it to use the shared-core functions by object identity. Nothing is removed.

`tests/test_d117_floor_qwen25_1p5b_plan.py:1700-1714` replaces a tripwire, `assertFalse(SPEC_REL.exists(), "registration-first proof must be revisited at first spec freeze")`, which cannot hold once any spec is committed. The replacement is the revisit that message demanded:

- it validates the committed spec with `_validate_registered_spec`;
- it runs `verify_registration_ordering` against real git history;
- it asserts the proven digest equals the committed spec's `registration_sha256`;
- it asserts the registration and spec commits differ.

All earlier assertions in the test (synthetic-fixture digest pins, the contract-doc pin, the counterfactual refusal) are unchanged.

Run here: the ordering proof returns registration commit `a1133594e` → spec addition `24741cab`. `a1133594e` is already an ancestor of `origin/main`, so the proof holds under either a merge commit or a squash merge. The committed specs' L-registration digests (`55608576…` for 1.7B, `04657a74…` for 8B) are already printed in `docs/contracts/paper_reported_energy.md`. The spec-declared length equals the pin's L.

Tests executed with `-B -m pytest -q -p no:cacheprovider`, all passing:

- the two updated files: 30 passed, 35 subtests passed; the registration test confirmed collected and passed for both models;
- `tests/test_d117_contrast_v5_pack.py`, `tests/test_d117_floor_qwen3_v5_generate.py`, `tests/test_generator_head_pin_relation.py`, `tests/test_paper_reported_energy.py`, `tests/test_issue_g2a_prefill_prompt_pin.py`: no failures (run with doubled `-q`, so no count line was printed).

## Notes (no action required to merge)

**N1 — LOW, cosmetic, bytes-affecting if ever changed.** The contrast pack still labels the prefill prompt `PROPOSED-PENDING-LEAD-RATIFICATION`, although the prompt is now the pin-issued one:

- `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/README.md:31-32`;
- `…/prefill_prompt_candidate.json:4`;
- the `prompt-status=` tag at line 64 of each of the 40 prefill members, e.g. `…/03_prefill_p<L>_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p<L>-contrast-b01-a1.json:64`.

It is a generator constant from the reviewed source and does not touch the workload (text, ids, lengths, output budget). README.md:33-35 says the freeze receipt, not this text, is the authority. If anyone wants the label gone, that must happen before freeze, because it changes member bytes and both plan hashes. Similar inherited wording: `"selection": "issued_d116_artifact_only"` (`plan_tree.json:29` in the floors, `:35` in the contrast) now sits beside the r2 artifact, and the floor workload name keeps `_candidate` (explained in the floor README).

**N2 — INFO.** `model.source` is the absolute weights mirror `/Users/edr/jw_models/mlx-community/Qwen3-{1.7B,8B}-4bit` in all 280 members (e.g. `configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r01.json:7`) and in the identity and stack-scope declarations. It comes from `configs/model_panels/qwen3_4bit.json`, and identity is carried by the pinned revision, tokenizer and chat-template hashes next to it. It is not a live root and is not meant to exist in a clone; it is the one answer to the "absolute path" question.

**N3 — INFO.** Floor decode members' `suite_manifest_sha256` (e.g. the same file, `:33`) is the canonical effective-manifest hash (`joulewise/suite.py:1426`), not the sha256 of the file bytes. The floor `decode_prompt_manifest.json` files are written in a non-canonical layout, so a plain `shasum` gives a different value (1.7B: file `446c7ef3…` vs bound `31301c9d…`; 8B: file `46887b91…` vs bound `6dc7448c…`). Recomputing with `suite_manifest_sha256` matches both, and that is what the controller verifies (`joulewise/controller.py:743-754`). The contrast manifests happen to be canonical, so both hashes agree there. Not a defect; recorded so a later byte-hash spot check is not misread as drift.

**N4 — INFO.** The cutoff is bound explicitly in the floors and only transitively in the contrast. The floors carry the cutoff head digest in `issued_ledger_head`; the contrast `plan_tree.json:35-38` carries the artifact and derivation hashes, and the cutoff (sequence 376, `a5b825b7…`) lives inside that sha-pinned artifact. The floors' `issued_ledger_head.path` names `configs/calibration/calibration_ledger_head.json`, whose live content is now sequence 402 (`3ce1676c…`). The mismatch is intentional (`tests/test_generator_head_pin_relation.py:182-198`: the issued head is the acceptance cutoff, never the live head), and it means pack bytes do not move when the live ledger advances.

**N5 — INFO.** In the new test block, the first equality (`proof["registration_sha256"] == registration_sha256(model, _spec_prefill_length(committed_spec))`) restates what `verify_registration_ordering` computes internally. The block's real force is the ordering proof not refusing, plus `_validate_registered_spec` on the committed spec. A literal pin of the two L digests in the test, as exists for p512 at `:1683-1687`, would make it independent of the function under test; the digests are already pinned in the contract doc. The proof needs a non-shallow clone; every CI checkout uses `fetch-depth: 0`.

## Not done

- No model was loaded and no measurement tool was run; tokenizer checks used tokenizer files only.
- The whole test suite was not run — only the seven files named above.
- The generators, the issuer and the selector were treated as reviewed code; I read the issuer in full and the relevant generator sections, but did not re-review all generator source.
- During inspection, two tool outputs (the emitted generator's line 21 and directory listings) displayed the numeric length in this session's transcript; it is not printed in this ruling.
