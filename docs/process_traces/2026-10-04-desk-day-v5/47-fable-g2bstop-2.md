FINAL PASS: PASS

Second cold final pass on PR #474 (`ffc18054`, branch feat/2026-10-04-g2b-one-block-stop), G2-b one-block stop.
Reviewer: Fable 5.1, no prior context. Scratch: /tmp/dd5-fable-gs/. No file in the checkout was edited; no git write, no hardware, no model.
Diff base used: `git merge-base origin/main HEAD` = `cfdb90d6`. `scripts/run_campaign.py` is the same blob (`6d91df6b`) at `cfdb90d6` and `8fa002f7`, so "main" below means that blob.

## Ruling in one paragraph

F1 is cured. A run is bounded only when its authenticated authorization has `purpose = G2B_SHAKEDOWN` AND `--max-blocks` is passed with the matching value; every other authenticated purpose gets no binding and refuses the flag (`scripts/run_campaign.py:3213-3222`). I regenerated the golden snapshots from main's own script and they equal both the tracked fixtures and the branch's output, for the unauthenticated path and for six authenticated cases. F2, F3 and F6 are fixed and the fixes are pinned (nine of nine mutants killed). I agree F5 is unreachable. The revision introduced nothing that blocks merge. No BLOCKER, no MAJOR; two MINOR, one NIT, and notes.

## What I ran

- `pytest tests/test_run_campaign_max_blocks.py tests/test_gen_g2_phase_d.py` -> 35 passed, 44 subtests passed (125 s).
- Main-vs-branch differential: main's script blob loaded as a module and driven through the test harness (`CampaignMaxBlocksTests.invoke`, 3 blocks x 4 members). Result: log, rc and every artifact identical between main and branch, and identical to `tests/fixtures/campaign_max_blocks_legacy.jsonl` and `tests/fixtures/campaign_max_blocks_authenticated_main.json`, for: unauthenticated; `CAMPAIGN_TRANSACTION` with `permitted_blocks` 1, 3, 5; `T0_REHEARSAL` with 1, 3, 5. All rc 0, 12 members. The fixture comment "generated with main's script" is true.
- Nine-mutant sweep of the block-limit logic against the new test class (the real-CLI, arm-readiness-fixture and v5-fragment tests excluded, since they are slow or do not load the mutated module). All killed:
  hash check disabled; stop row written despite a failed stage verdict; non-G2B purpose bounded (the F1 regression); G2B without the flag runs unbounded; CLI value allowed to differ from the authenticated one; `--max-failures` guard removed; waived dispatched member not treated as failure; non-G2B purpose accepting the flag; stop one block late.
- zsh and bash check of the `run_stage` edit under `set -euo pipefail`: `"${@:6}"` expands to zero words with five arguments; rc 3 survives through `|| return $?`; a plain call that returns non-zero still ends the script with that rc.
- `campaign_block_limit(1, None, ...)` against tracked real stage directories (see N4).

## Findings

### N1 — MINOR — the claim path's only remaining delta: three extra reads before the purpose test
`scripts/run_campaign.py:3213-3214` calls `_authenticated_campaign_block_limit` (`:3140-3173`) for every authenticated run, before it knows the purpose. That re-reads consumption -> GO -> authorization and checks each sha256. For a `CAMPAIGN_TRANSACTION` stage this adds one new way to stop before member 1: if any of the three files changed or became unreadable in the interval since the launch preflight a few lines earlier (`:8225`), the stage exits rc 2 with `launch_binding_mismatch` where main would dispatch. When the bytes are stable (the normal case) log, rc and artifacts are identical to main, per the differential above. This is fail-closed, the three files were just authenticated by the same process, and the bundle writer re-authenticates anyway, so I do not count it against question 1. It is worth one sentence in the runbook, which currently says other purposes "remain unbounded" without mentioning the re-read. A cheaper shape would read the purpose from the already-authenticated consumption (`consumption["go_receipt"]["purpose"]`) and only walk to the authorization for G2B; not required for merge.

### N2 — MINOR — an existing, unrelated test was narrowed in this PR
`tests/test_run_campaign.py:4344-4348` (and `:4357-4358`). A cooldown-provenance test that ran `write_strict_analysis_campaign(config_dir, telemetry_backend="mock")` now runs two plain configs; the in-code reason is a 60-second deadline. Nothing in this change touches that code path, so the edit is a timing accommodation riding on a claim-chain PR. The two-member version still asserts both cooldown outcomes. I did not establish whether the strict-analysis variant covered anything else in that test; it should be named in the PR's own record so it is not read later as part of the block-limit work.

### N3 — NIT — comment names a handler that does not exist
`scripts/run_campaign.py:249-250`: "130 interruption (main's KeyboardInterrupt handler)". `main()` (`:9151-9170`) catches `LaunchLineageError`, `SupersessionRecorderError` and `Exception`; `KeyboardInterrupt` is not an `Exception`, so it propagates and the interpreter's default handling produces 130. The registry is right; the parenthetical is wrong.

### N4 — NOTE — `--max-blocks` accepts two-model blocks only
`campaign_block_limit` requires `models[0] != models[1]` in each block. Checked against tracked stages:
- `d117_contrast_qwen25_1p5b_vs_7b_v3/01_decode_contrast_blocks_01_05` and `03_prefill_p256_contrast_blocks_01_05` (20 members each, A = `qwen25-1p5b-mlx`, B = `qwen25-7b-mlx`): accepted. This is the shape of G2-b's first stage.
- `d117_floor_qwen25_7b_v3/02_phase_decode_abba_blocks_01_05` (A and B share `qwen25-7b-mlx`): refused with "requires unique contiguous four-member A/B/B/A blocks", before dispatch.
Correct for G2-b, whose pack is the contrast pack (`SHAKEDOWN-G2-RUNSHEET.md:271`). The help text and runbook say "A/B/B/A blocks" without the two-model condition; a later bounded floor shakedown would refuse.

### N5 — NOTE — a G2B authorization now refuses every marker-bearing stage that lacks the flag
`:3219-3220`, pinned by `test_g2b_missing_flag_refuses_even_without_contrast_role`. The G2-b chain passes the flag only to the science stage, so its bound-corpus, start, midpoint and end stages must stay unauthenticated. They are: 0 of the 24 tracked JSON files under `configs/campaigns/window_references` and `configs/campaigns/neg8_reference_corpus` carry `launch_lineage_required`. If a reference config ever gains the marker, G2-b refuses at the bound-corpus stage, before any science (fail-closed).

### N6 — NOTE — F4 remains open by agreement
The rc-3 gate (`:9107-9112`) is still not exercised on the real v5 pack with a mock runner. The revision narrowed it at unit level: `test_production_policy_with_v5_prospective_manifest_fragment_can_stop` reaches rc 3 under `quiet_mac_p2_production.json` with the v5 producer's manifest fragment, and `test_limit_reached_with_claim_barrier_has_no_stop_row_or_rc3` shows a claim-bearing barrier yields rc 1 with no stop row. If the real pack behaves differently, the consequence is rc 1 after block 1 and the chain stopping at `test "$SCIENCE_RC" = 3`, before the post-bracket path: a lost shakedown, no effect on a claim window. The desk rehearsal should happen before the G2-b arm.

### N7 — NOTE — chain bytes changed (carried from the first pass)
`run_stage` differs in the canonical runbook chain, the G2-a chain and the G2-b region (`docs/phase_2/window_runbook.md:1596-1610`; `SHAKEDOWN-G2-RUNSHEET.md:484-498`, `1075-1089`). Any chain digest or `permitted_chain_sha256` computed earlier is stale; re-render before the next arm.

## Disposition of the first pass's findings

- **F1 (MAJOR): cured.** Purpose test at `:3215`; non-G2B returns `None` (`:3218`) and refuses the flag (`:3217`); the role-based trigger is gone. `preflight["block_limit"]` is set only when a limit exists (`:8314-8320`). Verified against main as described above; `test_unflagged_authenticated_purposes_match_main_golden_log_rc_and_artifacts` pins it and the F1-regression mutant is killed.
- **F2: cured.** `test_hash_mismatch_at_each_authenticated_hop_refuses` now keeps each file structurally valid and asserts "hash mismatch"; the hash-off mutant is killed.
- **F3: cured.** Stop-row suppression on `blocked`/`invalid` verdicts and on a claim barrier, and the waived member, are each pinned; those mutants are killed.
- **F4: deferred**, see N6.
- **F5: agree it is unreachable.** `_read_launch_consumption` refuses any consumption without `go_receipt` or not schema v3 when `require_current_boot` is true (`joulewise/arm_readiness.py:9353-9357`), and `authenticate_campaign_launch_lineage` always passes `require_current_boot=True` (`:11368-11373`). The authorization record's key set, integer `permitted_blocks >= 1`, absolute path and purpose equality with the GO are all enforced there (`:10116-10134`, `:2809-2818`) before `run_campaign.py` re-reads it.
- **F6: cured.** Both `echo` lines carry `|| return $?`; `test_run_stage_propagates_both_log_write_failures_with_errexit_disabled` covers G2-a and G2-b; the range check now lives in `campaign_block_limit` only.

## The five questions

1. **Without the flag/bound, identical to main?** Yes. Unauthenticated and authenticated non-G2B runs produce the same log bytes, rc and artifacts as main's script (reproduced, not taken from the fixture). Residual: N1.
2. **rc 3 or a stop row without N complete strict-valid blocks; a member cut mid-run?** No. A block counts only when its four members were each `ok` or `skipped` with exactly one usable, unwaived evaluation (`:3185-3198`); a `skipped` member is necessarily usable because `failed = not usable and not waived` (`:483-485`). Any other status sets `failures` and ends with rc 1. The stop row is written only after the stage verdict, and only when `failures` is zero, the verdict is not `blocked`/`invalid`, and no claim barrier applies (`:9107-9127`). The stop is a `break` after the member's log row, provenance and backup; no signal is sent. An interrupt propagates with no stop row.
3. **Bound from authenticated bytes; can it be widened?** From authenticated bytes: the walk starts at the consumption path and digest returned by the launch authentication and checks sha256 at each of three hops. It cannot be widened or narrowed: any CLI value other than `permitted_blocks` raises before dispatch (`:3221-3222`), omission raises (`:3219-3220`), and G2B's `permitted_blocks` is itself pinned to 1 at authentication (`joulewise/arm_readiness.py:10130-10134`, `joulewise/night_gate.py:1008`).
4. **G2-b post-bracket path after rc 3; G2-a unchanged?** Yes. After `test "$SCIENCE_RC" = 3` the rendered region runs midpoint reference, end triplet, post calibration and the terminal-boundary record (`SHAKEDOWN-G2-RUNSHEET.md:1162-1187`); only the first stage is dispatched; an empty list leaves `SCIENCE_RC=2` and stops; rc 0, 1, 2, 130 stop the chain (the repo's zsh test, 5 cases). G2-a: its `run_stage` call (`:545`) is a plain call under `set -e`, there is no trap in either chain, and its probe configs are forbidden the lineage marker (`scripts/generate_g2a_probe_inputs.py:1127-1128`), so `run_campaign.py` takes the unauthenticated path, which is byte-identical to main.
5. **Do the tests kill the regressions they claim?** Yes for everything I mutated (9/9). Not covered by any test: a second `run_campaign.py` stage reading a log that already ends in a stop row while an analysis manifest id is in force (the rerun test has no manifest id). In the G2-b chain the following stages are reference stages; I did not confirm they carry no manifest id.

## Not checked

- Nothing on hardware, with powermetrics, or with a model. The real v5 pack is generated, not tracked; structure was checked on the v3 contrast pack.
- The post-night harvest and whole-window tools were not checked against a log containing a `joulewise.campaign_stop.v1` row. No code outside `run_campaign.py` and the tests references that row. The G2-b night chain itself stops at the physical-ahead boundary and runs none of them.
- I did not rerun `tests/test_check_window_provenance.py` or `tests/test_run_campaign.py` in this pass (budget); their diffs were read.
- I did not read RUN_STATE, CLAUDE files, memory, skills or any PR body.
