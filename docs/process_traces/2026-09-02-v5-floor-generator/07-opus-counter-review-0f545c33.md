# Opus counter-review — `_v5` floor generators (gate ledger item 6)

Head `0f545c33`, `/Users/edr/code/JouleWise-wt-floorgen`, branch `feat/2026-09-02-v5-floor-generator`.
Read-only, checkout clean (`git status --porcelain` empty). `FLOOR` = `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py`
(BETA byte-identical modulo substitutions); `ISSUER` = `scripts/issue_g2a_prefill_prompt_pin.py`; `T` = `tests/test_d117_floor_qwen3_v5_generate.py`.

## Test tail (executed this session)

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_d117_contrast_v5_pack
......................................
----------------------------------------------------------------------
Ran 38 tests in 11.150s

OK
```

## Findings

| Sev | ID | Line | Evidence |
|---|---|---|---|
| SHOULD-FIX | CR-1 | `FLOOR:157-158` | `PRODUCER_INDEX = 1` / `CONSUMER_ARM = "A"` are **defined and never read** (`grep -c` = 1 each). Live values are literals: `"producer_index": 1` at `:2276`, `"arm": "A"` at `:2337,:2342,:2376`. These are also the *only* non-string differentiators between ALPHA and BETA (`1`/`A` vs `2`/`B`) — precisely what a maintainer forking a third pack edits, and editing them does nothing. Wire or delete. |
| SHOULD-FIX | CR-2 | `T:95-148` | **No test feeds an issuer-emitted pin to a floor loader.** The only floor pin fixture is hand-built and its ladder has **two** rungs (`"rungs": [target, companion]`, `T:105`) — a shape `ISSUER:224-225` hard-refuses (`prompt_ladder_expected_four_rungs`). The accept-direction test that exists, `tests/test_issue_g2a_prefill_prompt_pin.py:346`, loads **only the contrast pack** (`:24-33,:357-363`). The floor loader (`FLOOR:1052-1274`, ~220 lines) re-implements the pin contract independently with zero issuer-bound coverage. |
| SHOULD-FIX | CR-3 | `FLOOR:1276-1310` vs `v3:741-770` | v3's `load_and_verify_families()` carried **six drift refusals** — source-byte pin + domain-hash pin for each of decode/prefill/p256, decode read from `SOURCE_DECODE_FAMILY_REL` and byte-compared. v5 deletes all six: families are generated in-file, and `DECODE/PREFILL/P512_FAMILY_DOMAIN_SHA256` init `""` (`:181-183`) and are **assigned at runtime** (`:1288,:1297,:1305`). Only the schema validator survives. Defensible at authoring time, but unlike `CURRENT_FROZEN_RECEIPT_SHA256 = ""` (fail-closed, with a re-pin path) this guard class is gone outright with **no registered step to restore it after V5-DESK-DAY-01 freezes the packs**. |
| SHOULD-FIX | CR-4 | `T:118-122,136-138` | The issuer sources pin constants from the **contrast** pack (`ISSUER:18`); each floor pack keeps its own copies (`FLOOR:67-104`). Verified at runtime that floor-A == floor-B == contrast for all of them today. But the fixture hard-codes `ladder_prompt_tokens` and the four count/margin floors as **literals**, so contrast-side drift would make every issued pin unloadable by the floor packs *with the suite still green*. `ruling_trace_paths` (`T:117`) and `exhausted_ladder_branch` (`T:135`) already read from contrast — do the same for the numerics. |
| NIT | CR-5 | `FLOOR:1184` | Loader accepts `status in ("selected","refused")`, but the issuer emits `refused` only with `collection_prefill_tokens == 4096` (`ISSUER:180-186`) while `FLOOR:1186` also demands `== 512`. The `refused` arm is unreachable — dead acceptance. |
| NIT | CR-6 | `FLOOR:1200-1214` | Loader checks the ladder key set and that `rungs` is a list, but never rung count, uniqueness, or that each `prefill_tokens` is in the ladder — all enforced by `ISSUER:224-241`. Same root as CR-2. |
| NIT | CR-7 | `FLOOR:165,132` | Overbuild: `P512_PROMPT_TOKEN_IDS` assigned at `:1272`, never read; `CURRENT_FROZEN_GENERATOR_SHA256` never read (dead in v3 too). |

## Lenses

**(a) v3 → v5.** All non-mechanical deltas ruled except two. RULED: dominance + floor-estimator registration on all three comparative cells (D-165; D-168 cl.3); suite-manifest decode workload, `prompt_token_ids_sha256`, `REDUCER_MIN_PHASE_SAMPLES` cross-check (D-166; 171a R-6, one manifest per floor unit); the prefill-pin block `:67-104,:1052-1274` (2026-08-30 ratification; 16b-RULING-g2a-producers); panel/workload SHA pinning (D-166); `QUANTIZATION` gaining `group_size: 64` (D-164); dropping `LEGACY_DECODE_PLAN_SHA256`, a v3-only freeze artifact (D-164); `CURRENT_FROZEN_RECEIPT_SHA256 = ""` (D-164 — traced fail-closed: `arm_readiness` returns `None` for an unfrozen pack so `""` is never compared; post-freeze it fails closed at `GenerationIdentity.__init__:320` until re-pinned). **UNRULED: (i) CR-3's six dropped family drift refusals; (ii) `extraction_spec.json` moving into the pack with the inventory's out-of-pack allowance deleted (`:20,:456-458,:3157-3167`) — strictly tightening, but a layout change no ruling names.** No carried statistic moved: `N = 10`, 10 ABBA blocks, `A1/B1/B2/A2`, stage count, `expected_n = 50`, Holm m=2 all identical to v3.

**(b) ALPHA vs BETA.** Clean. The whole 460-line diff reduces to model name/source/revision, id substitutions, `alpha`↔`beta`, `PLAN_PROFILE`, `PRODUCER_INDEX`, `CONSUMER_ARM`, `arm` literals. Nothing else. `tokenizer_json_sha256` is identical in both, so one issued pin can arm both packs.

**(c) Prefill-pin loader.** Accepted-but-never-emitted: CR-5, CR-6, and CR-2's two-rung ladder. Refused-but-does-emit: the issuer legitimately emits `prefill_length` 1024/2048/4096 (`ISSUER:486,493`, including the ruled `collect_at_4096` no-clear branch, which the *contrast* loader accepts), and both floor packs hard-refuse anything `!= 512` (`FLOOR:1105-1106`, `PREFILL_LENGTH = 512` at `:67`). **Ruled** by 171a R-7 ("512 for `_v5`") and fails closed, but undocumented: if G2-a selects any rung above 512 the whole `_v5` family is unarmable and both floor packs must be re-authored — worth one line in the pack README. `ISSUER:404-410` hashes the original bytes and `main` copies them verbatim, so the loader's `selection_copy_hash == g2a_record_sha256` demand (`FLOOR:1166`) is satisfiable; no false refusal there.

**(d) Linkage.** No drift. Contrast derives the floor plan-ids from its dynamic `PREFILL_LENGTH` at `d117_contrast_v5/generate_configs.py:2536-2546`; at 512 they resolve to `plan-d117-floor-qwen3-{1p7b,8b}-decode-prefill-p512-v5`, matching `FLOOR:106`. The `joulewise/arm_readiness.py:10877-10880` roster expects pack ids `d117_floor_qwen3-1p7b_v5` / `d117_floor_qwen3-8b_v5` at `configs/campaigns/<pack_id>` — exactly the two new directories and the canonical forms of RULED 97 R-6c. Digest shape covered by `test_contrast_references_resolve_to_matching_floor_plan_digests` and `test_arm_registry_and_pack_record_accept_the_v5_floor_roster`.

**(e) Overbuild.** CR-1 and CR-7 only. `PREFILL_EXHAUSTED_LADDER_BRANCH` is *not* overbuild despite being unreachable here — the closed schema must byte-compare a field the issuer always emits.

## Verdict

**MERGE** — no blocker. Register CR-2 and CR-3 before the desk day; both bear on the live arming path.
