FINAL PASS: FAIL

Cold final pass on PR #474 (`0636046c`, parent `8fa002f7`), G2-b one-block stop.
Reviewer: Fable 5.1, no prior context. Scratch: /tmp/dd5-fable-gs/. No file in the checkout was edited.

## Ruling in one paragraph

The G2-b part of the change is correct and I found no way to get a false rc 3, a
mid-member cut, or a widened bound. It fails on question 1 only: the bound is not
confined to runs that pass `--max-blocks`. Every authenticated stage whose order
manifest has `comparative_contrast_member` rows is now bounded by the
authorization's `permitted_blocks` even with no flag, and that includes every
science stage of the ordinary full-transaction (claim) chain. On that path the
log is no longer identical to main, and a fully successful stage can return rc 3,
which the unmodified full chain treats as a failure under `set -euo pipefail`.
The count is per `run_campaign.py` process while the authorization is per attempt,
so the limit also does not mean what the runbook says it means on a multi-stage
chain. One MAJOR, cheap to cure; everything else is MINOR/NIT.

## What I ran

- `pytest tests/test_run_campaign_max_blocks.py tests/test_gen_g2_phase_d.py tests/test_check_window_provenance.py` -> 63 passed, 32 subtests passed.
- Main-vs-change differential: main's `scripts/run_campaign.py` (from `git show 8fa002f7:`) and the change's, driven through the same harness as `tests/test_run_campaign_max_blocks.py` (3 blocks x 4 members, mocked children).
- Main-vs-change render diff of the G2-a night chain and the G2-b generated region.
- zsh check of the `run_stage` edit under `set -euo pipefail`.
- 12-mutant sweep of the block-limit logic against the new test class.
- The new structural validator against every real stage directory in four tracked packs.

## Findings

### F1 — MAJOR — implicit bound on the unflagged authenticated claim path
`scripts/run_campaign.py:3211-3213` (binding taken when `launch_authentication is not None and (contrast or requested is not None)`), consumed at `:8304-8314`, `:8712-8718`, `:9032-9037`, `:9106-9121`. Stated in the module docstring `:21-23` and the runbook `docs/phase_2/window_runbook.md:1717-1729`.

Evidence (differential run, same 3-block stage, no `--max-blocks`, a synthetic consumption -> GO -> authorization chain):

| authorization `permitted_blocks` | main | change |
|---|---|---|
| none (unauthenticated) | rc 0, 12 members | rc 0, 12 members, log byte-equal to main |
| 1 | rc 0, 12 members | rc 3, 4 members |
| 3 (= blocks in the stage) | rc 0, 12 members | rc 3, 12 members (every member succeeded) |
| 5 (> blocks in the stage) | rc 0, 12 members | rc 0, 12 members, but the `campaign_verdict` row gains `preflight.block_limit` |

Consequences on the real chain:
1. Real contrast stages are 5 blocks each, 4 stages per pack (`d117_contrast_*_v2/_v3` on disk; v5 generator `configs/campaigns/d117_contrast_v5/generate_configs.py:204,1145-1166`, `N_BLOCKS = 10` per arm, two arms = 20 blocks per window). The full chain (`window_runbook.md:1613-1621`, `1681-1686`) calls `run_stage` once per stage with no flag.
2. The block count lives in one process (`CampaignBlockLimit`, `:3175-3196`). A `CAMPAIGN_TRANSACTION` authorization with `permitted_blocks` of 6 or more is therefore never enforced: 20 blocks are collected under an authorization of 10. A value of exactly 5 makes stage 1 finish all 20 members and return rc 3; `run_stage` now returns that (`|| return $?`, `window_runbook.md:1608`) and `set -euo pipefail` (`:1466`) ends the window before the midpoint reference, with no post-bracket calibration. A value of 1-4 stops mid-stage with the same abort.
3. Nothing pins which number a `CAMPAIGN_TRANSACTION` authorization carries (`joulewise/arm_readiness.py:10128`, `joulewise/night_gate.py:1003` require only an integer >= 1; the contract row `docs/contracts/pack_night_go_receipt.md:410` says "Authorized block count"). Whether a claim window survives now depends on an unspecified convention.
4. The runbook sentence "omitting the option retains the authenticated limit ... The full transaction chain above retains its ordinary stage sequence" (`:1721-1729`) is true per process only; it reads as a per-window guarantee.
5. The "unbounded path byte-identical to main" result holds for the unauthenticated path only. `test_absent_option_matches_legacy_wire_bytes_and_rc` (`tests/test_run_campaign_max_blocks.py:114-119`) calls `invoke()` with `authentication=None`; no test runs an unflagged authenticated stage whose block count is >= or > `permitted_blocks` and compares it with main.

I did not find a `CAMPAIGN_TRANSACTION` authorization to inspect, so I cannot say the abort will happen; with 10 or 20 it will not. I am failing the change because the outcome (a lost claim window after a clean stage, or an unenforced authorization) is decided by a number no code or contract constrains, and because this path was reported as unchanged.

Cure, either is a few lines plus one test:
- (a) Take the flagless binding only when the authorization's `purpose` is `G2B_SHAKEDOWN` (or only when `--max-blocks` is passed, refusing a G2B authorization without it). The claim path then stays byte-identical to main; add a golden test with a non-None authentication.
- (b) Keep the flagless binding but define it: state in the contract and runbook that the count is per stage invocation, pin the permitted value for `CAMPAIGN_TRANSACTION` against stage size, and make the full chain accept rc 3 where it is legitimate. This is the larger change and touches the claim chain's bytes again.
I recommend (a).

### F2 — MINOR — per-hop hash test passes without any hash comparison
`tests/test_run_campaign_max_blocks.py:219-226`. Each hop is tampered by overwriting the file with `{"permitted_blocks": 99}`, which also removes `go_receipt` / `authorization` / `purpose`, so the refusal arrives as a `KeyError` -> `LaunchLineageError` regardless of the digest check. Mutant "replace the sha256 comparison in `read_bound` (`run_campaign.py:3150-3151`) with `if False`" is NOT killed by this test; it is killed only by `test_limit_comes_from_replayed_pack_night_authorization` (`:228-248`), which tampers the authorization hop alone. The consumption and GO hop digests are unpinned. The code itself is right. Cure: tamper by changing one value while keeping the structure valid.

### F3 — MINOR — claimed regressions that no test pins
Mutation sweep (real-CLI test excluded, it does not load the mutated module):
- Killed: off-by-one limit; CLI wider than the authenticated bound accepted; CLI replacing the authenticated bound; hash check removed (see F2); `--max-failures` other than 1 accepted; rc 3 changed to 0; reference corpus bounded.
- Survived, equivalent on reachable paths (the status gate at `:8713-8714` and `:9033-9034` already turns failed/waived/invalid members into a stop with rc 1 before `observe` is reached): dropping `usable` in `observe` (`:3186-3187`); dropping `waived` in `observe`; dropping the all-four-members check (`:3191`); dropping `failures = max(failures, 1)` on the dispatched path.
- Survived, not equivalent: `if block_limit_reached and not campaign_failed` -> `if block_limit_reached` (`:9106`). No test reaches the limit with a `blocked`/`invalid` stage verdict or a claim barrier, so "no stop row and no rc 3 when the stage verdict fails" is unpinned.
- The runsheet asserts "Failures, waivers and interrupted blocks never qualify"; failures and interrupts are tested, a waived member is not.

### F4 — MINOR — the rc-3 gate is not exercised with a real analysis manifest or the production policy
`:9101-9105`. rc 3 requires the stage verdict not to be `blocked`/`invalid` and, for a claim-bearing policy, no idle-admission claim barrier. The tests patch `evaluate_members` or use `TEST_CAMPAIGN_POLICY` with no analysis manifest. By reading, the barrier conditions (`:6879-6907`) are per member and per window, so four clean members behave like twenty and unreached members are not counted as missing (`missing_members` is filled only at `:8739`, `:8842`, `:8937`). I did not execute this on the real v5 pack with `quiet_mac_p2_production.json`. If it is wrong, G2-b collects block 1, gets rc 1, and `test "$SCIENCE_RC" = 3` stops the chain before the post-bracket path. A mock-runner rehearsal of the first real stage with the production policy would close it.

### F5 — NIT — legacy consumption receipts
`:3157-3162`. A marker-bearing contrast stage whose consumption receipt has no `go_receipt` (schema v2) now refuses with `launch_binding_mismatch` where main proceeded. New consumptions are always v3 (`joulewise/arm_readiness.py:93,10556`) and live authentication requires the current boot, so I do not think this is reachable.

### F6 — NIT — duplicated range check, unguarded echoes
`--max-blocks >= 1` is checked at both `:8182-8183` and `:3206-3207`. In `run_stage`, the two `echo ... >> window-chain.log` lines carry no `|| return $?`, so under G2-b's `set +e` a failed `stage_start` write would not stop the campaign; a failed `stage_end` write turns rc 3 into rc 1.

### F7 — NOTE — chain bytes changed for G2-a and the canonical runbook chain
Three lines of `run_stage` changed in all three chains, so any chain digest or `permitted_chain_sha256` computed before this change is stale. Re-render before the next arm.

## The five questions

1. **Unflagged behaviour identical to main?** Unauthenticated: yes, byte-identical log, rc 0, same members (verified against main's own script; the golden fixture equals main's real output). Authenticated contrast stage: no, see F1. Reference and bound-corpus stages: unchanged (no contrast rows -> no binding; `test_authorization_does_not_limit_reference_corpus` kills the mutant that bounds them).
2. **False rc 3 / stop row, or a member cut mid-run?** None found. A block counts only when all four of its members were `ok` or `skipped` in this process, each with exactly one usable, unwaived evaluation (`:3185-3196`); any other status forces rc 1 with no stop row; the stop row is written only when the stage did not fail (`:9106`). The stop is a `break` after the member's log row, provenance and backup are written, and no signal is sent, so no member is cut. An interrupt still propagates as `KeyboardInterrupt` with no stop row. Existing strict-valid bundles count without redispatch, by design.
3. **Bound from authenticated bytes, and can it be widened?** Yes and no. It re-reads consumption -> GO -> authorization, checking sha256 at each hop, rooted in the consumption path and digest returned by the outer launch authentication (`:3138-3171`); no CLI path or environment variable feeds it. A CLI value different from the authenticated one, larger or smaller, raises before dispatch (`:3214-3215`). Structural pre-checks refuse anything that is not whole A/B/B/A blocks of single-repetition configs before member 1.
4. **G2-b post-bracket path after rc 3; G2-a unchanged?** Yes to both. The runsheet's generated region equals the generator's output; after `test "$SCIENCE_RC" = 3` the chain continues to midpoint, end triplet, post calibration and the terminal-boundary record; only the first stage is dispatched; an empty stage list leaves `SCIENCE_RC=2` and stops. rc 0, 1, 2 and 130 all stop the chain (zsh test). G2-a's rendered chain differs from main only in the three `run_stage` lines and a line-range comment; all its call sites are plain calls under `set -e`, where `cmd || return $?` aborts exactly as before; `"${@:6}"` expands to zero words with five arguments under `set -u` in zsh (checked).
5. **Do the tests kill the regressions they claim?** Mostly. Gaps: F1.5 (no authenticated unflagged golden), F2 (hash hops), F3 (stop-row suppression on a failed verdict, waivers).

## Not checked

- No real `CAMPAIGN_TRANSACTION` or `T0_REHEARSAL` authorization was available, so the `permitted_blocks` values they carry are unknown to me; I did not establish whether a rehearsal runs a contrast stage through `run_campaign.py`.
- Nothing was run on hardware, with powermetrics, or with a model. The real v5 pack is generated, not tracked, so the validator was run against the tracked v2/v3/splitwise packs (all 10 contrast stages accepted, 5 blocks each).
- I did not read RUN_STATE, CLAUDE files, memory, skills or any PR body.
