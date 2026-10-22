# BY-LOOP — execution blocked; source findings preserved

## SUMMARY

- Status: INCOMPLETE. The selected cloud executor has not become usable.
- Base confirmed through connected GitHub: `bda481d5af510b29dde4976f172a20170a42c955`.
- BY-INT's lane head still equals that base; no base movement was observed.
- No earlier BY-LOOP lane branch existed when checked.
- Governing block-6 and BYTES registration texts were read; a dedicated BYTES root is the implementation choice below.
- Item 48's live yield notice is built inside the sealed block-5 driver; the authorized known-false-alarm disposition is recorded.
- The duplicate close notice is traced to the magistrate's manual step; loop wake remains the chosen single owner.
- No production code, registrations, measurement state, or sealed file has changed.
- Tests, rehearsal, guard measurement, stage-success fix and leak fix remain unexecuted.

## LOOP ROOT CHOICE

Dedicated root, proposed path `/Users/edr/night-b6/loop-bytes`; **not implemented or created**.

Authority: `docs/design/block6_collection_draft.md` §6.1 closes once every pack has its target, and §14 makes the pack the unit of registration, collection and release with a queue of open packs. `docs/registrations/block6_replication_DRAFT.md` §14 S-2 identifies the existing replication loop root. `docs/registrations/bytes_pack_v1.md` §5 fixes twelve independent, fixed, one-session packs and order s1-p1 through s6-p1, then s6-p2 through s1-p2; its authority paragraph requires replication behavior to remain byte-identical.

The dedicated root preserves the replication loop's DONE history and avoids inventing a DONE-to-NEXT reopening rule. Its configuration must restrict discovery to the twelve BYTES packs so existing replication registrations cannot be recollected. All twelve belong to the same active BYTES queue. No state under the proposed production path or the existing production root has been read or written by this seat.

## ITEMS

### 1. Twelve-pack loop readiness

Not implemented: executor unavailable. Read `configs/b6/loop.json`, `joulewise/b6/loop.py`, `joulewise/b6/queue.py`, `scripts/b6_loop.py`, `joulewise/b6/pack_registration.py`, and the governing texts above through connected GitHub.

Observed: the default order already includes all twelve BYTES packs, DONE remains terminal in `Loop.tick`, and a fresh root starts at NEXT. Production BYTES registrations at the base remain draft; synthetic rehearsal copies must be explicitly registered-shaped and committed only in scratch.

### 2. DONE tick overhead

Not implemented or measured: executor unavailable. `scripts/b6_loop_guard.zsh` currently skips Python only for a live `collection.active` marker. `docs/process_traces/2026-10-21-magistrate-c5a1d8fd/RECORD.md`, “BYTES item H”, records a DONE tick every 300 seconds costing 0.29 seconds wall and 0.26 CPU-seconds; those are historical measurements, not measurements by this seat. A native-shell DONE fast path still needs implementation and argv/process-count evidence.

### 3. Item 48: smoke yield notice

**Recorded known false alarm; sealed code left unchanged.**

At base `bda481d5a`, `joulewise/b5/driver.py:1418` builds `yield_plan` from dispatch run IDs, not the reduced tree's kept counts. Its `count_stage` compares succeeded members with `_min_valid(role, planned)`, and `YieldTripwire` owns the live notice; `execute` calls `yield_plan` and constructs that tripwire. The smoke reduces dispatch execution after order resolution in `joulewise/b6/smoke.py`, using `configs/b6/smoke_keep.json`; the full order manifests deliberately remain intact.

Consequently the historical 3/10/10/3 plan can classify four successful one-member smoke stages as LOW. Computing a desk-only kept-count summary in smoke.py would not correct the live driver notice. The item brief expressly allows recording the false alarm when notice construction is confined to driver.py. No threshold, printed quantity, exclusion, or block-5 byte is changed. This item is a source-based disposition, not a successful live smoke test.

### 4. Item 52 / issue 509: explained anchor fallback

Not implemented: executor unavailable. `smoke.stages_succeeded` currently explains campaign rc 1 only for recorded idle skips, after exact stage/member dispatch matching. Its desk caller also gates that explanation on idle flags. The fix must cover the caller as well as the helper, retain exact membership checks, and reject every other failed-member cause. Fails-before / passes-after evidence remains required.

### 5. Leaked hazard monitor

Not fixed or reproduced: executor unavailable. Read `tests/b6/test_s3_cold_fixes.py`, `tests/test_fixture_orphan_census.py`, and `tests/b6/support.py`. The named cold-fix module has no direct Popen call at the base, so the originating process must be traced through its exercised seams or the broader s3-cold execution before asserting a cause. Do not claim the leak is repaired merely because the module contains no direct spawn. The fixture orphan census and a bounded fails-before / passes-after run remain required.

### 6. Duplicate block-6 close mail

**Recorded; no mailer change. Loop wake is the single owner of the close notice.**

`docs/process_traces/2026-10-21-magistrate-283e9802/RECORD.md`, “Block 6 closed” and “Pruning list”, explicitly identifies the magistrate's manual “email the verdict” instruction as the second sender. `RUN_STATE.md` items 59 and 60 also distinguish the loop wake and that activation. `Loop._next` has one close event; the scoped `joulewise/b6/mailer.py` provides outbox delivery and issue closing, and has no magistrate-specific close dispatcher to prune.

This is a manual orchestration-instruction duplication, so changing the shared mailer would affect the existing loop delivery rather than removing the magistrate's instruction. The historical prose is evidence, not a second executable mailer. No in-scope magistrate sender was identified. The lead should carry loop-wake ownership into the external activation instructions; the requested record-only disposition is used here. No message was sent by this seat.

## REHEARSAL

**NOT RUN — no usable execution environment.** No scratch root, fake executable, registration copies, plan-tree copies or launch log has been created. No real launchctl command has run.

Required continuation: fresh per-module TMPDIR under /tmp/jwtmp; twelve committed synthetic registered-shaped pack copies and their plan trees; fake launchctl recording argv and returning 0 on PATH; real open_packs and real smoke preparation through scripts/b6_loop.py. Record exact commands, layout, initial NEXT state, final state, bytes-s1-p1 preparation and fake argv log here. Local director repetition remains outstanding.

## DONE TICK

**NOT RUN.** No Python-start/process-count measurement exists for this seat. The historical c5a1d8fd measurement is cited only in item 2.

## TESTS RUN

None. No seat setup or test command could be executed. The shell tool returned:

`No usable execution environment is available. Wait for an environment to become available before using this tool.`

A wait_for_environment request remained running while status moved from pending/offline to starting/offline; runtime diagnostics reported no retained records. The user was asked asynchronously to restart or reattach the environment. There was no automatic approval-review rejection.

No test count, exit code, skip count or environmental test failure is claimed. In particular no fixture git-commit failure, macOS process-group failure, private temporary path failure, launchd failure or powermetrics failure was observed because no tests ran. Keep JW_B5_SYNTHETIC_ONLY=1 and give each allowed test module a fresh TMPDIR on continuation; run only the brief's permitted modules.

## SEALED INVENTORY

The base inventory contains **682 paths**, listed verbatim below. No sealed file has been edited. A local `git -C /workspace/JouleWise diff --name-only bda481d5a HEAD` has not run because the executor is unavailable; connected-GitHub compare of base to checkpoint `46ed133ad8cb3bf50b6785d35a817b6b85996f8b` returned exactly `.codex-report/BY-LOOP.md`, with no overlap against all 682 inventory paths. A second compare from the base to `c2a7dd5025079c2ab01bc5aaf2ea845434171c2b` again returned exactly `.codex-report/BY-LOOP.md` (two report-only commits), so no inventory path overlaps. This final report-only update adds the observed verification and CI status. This is API evidence, not a claim that the required local Git command ran.

## CI

Draft PR **#542**, `ci/2026-10-22-bytes-loop` against main, titled “CI: BYTES loop readiness (BY-LOOP)”: https://github.com/mpmdw/JouleWise/pull/542.

Checkpoint `c2a7dd5025079c2ab01bc5aaf2ea845434171c2b` was verified as the exact head of both lane and CI branch through connected GitHub. Its CI workflow was observed pending (run 39743424315); gate-ledger completed with failure (run 39743424387). The failure reason was not inspected; no claim of green checks is made. The earlier report checkpoint had both workflows in progress. This final commit changes only the report and is fast-forwarded to the CI branch as well. No code-readiness result is claimed; the PR body explicitly says implementation and execution remain blocked. Do not merge.

## DECISIONS I MADE

- Use a dedicated BYTES root rather than reopening the replication loop, for the governing reasons above; implementation remains pending.
- Record item 48's known live LOW false alarm under the brief's explicit sealed-driver exception.
- Keep loop wake as the single owner of close notification; record the external/manual magistrate duplication without changing the shared mailer.
- Preserve source findings in the only authorized report path through connected GitHub while filesystem execution is unavailable.
- Do not substitute unit-only, remote source-reading or historical evidence for the required synthetic real-entry-point rehearsal.

## OPEN ISSUES

- Cloud executor unavailable; seat setup, filesystem inspection and local Git setup have not run.
- Items 1, 2, 4 and 5 need implementation and focused verification.
- Rehearsal, no-Python DONE measurement, fails-before / passes-after checks, hazard registries and sealed-inventory local diff check remain outstanding.
- CI completion and the director's local repetition remain outstanding.

## NEEDS_RULING

none. Runtime availability is an infrastructure blocker, not a scientific ruling.

## SEALED INVENTORY PATHS

```text
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b02-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b02-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b02-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b02-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b03-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b03-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b03-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b03-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b04-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b04-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b04-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b04-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b05-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b05-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b05-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b05-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/01_decode_contrast_blocks_01_05/order_manifest.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b06-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b06-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b06-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b06-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b07-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b07-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b07-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b07-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b08-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b08-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b08-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b08-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b09-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b09-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b09-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b09-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b10-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b10-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b10-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b10-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_decode_contrast_blocks_06_10/order_manifest.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b01-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b01-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b01-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b01-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b02-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b02-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b02-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b02-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b03-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b03-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b03-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b03-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b04-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b04-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b04-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b04-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b05-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b05-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b05-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b05-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/03_prefill_p2048_contrast_blocks_01_05/order_manifest.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b06-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b06-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b06-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b06-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b07-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b07-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b07-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b07-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b08-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b08-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b08-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b08-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b09-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b09-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b09-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b09-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b10-a1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b10-a2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b10-b1.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/d117c-qwen3-1p7b-vs-qwen3-8b-v5-prefill-p2048-contrast-b10-b2.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/04_prefill_p2048_contrast_blocks_06_10/order_manifest.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/README.md
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/calibration_plan.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/calibration_plan.sha256
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/condition_families/condition_family_sw_decode_a_qwen3-1p7b.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/condition_families/condition_family_sw_decode_b_qwen3-8b.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/condition_families/condition_family_sw_prefill_p2048_a_qwen3-1p7b.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/condition_families/condition_family_sw_prefill_p2048_b_qwen3-8b.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/consumer_family_declaration.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/01_sky_color.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/02_weather_climate.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/03_kyoto_itinerary.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/04_interest_math.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/05_plant_diagnosis.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/06_web_request.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/07_falsifiability.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/08_pantry_dinner.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/01_sky_color.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/02_weather_climate.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/03_kyoto_itinerary.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/04_interest_math.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/05_plant_diagnosis.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/06_web_request.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/07_falsifiability.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/08_pantry_dinner.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_workload_candidate.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generator_inputs/decode_workload.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generator_inputs/model_panel.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/order_manifest.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.sha256
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/prefill-prompt-ladder.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_pin/selection.json
configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_prompt_candidate.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r01.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r02.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r03.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r04.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r05.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r06.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r07.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r08.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r09.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r10.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/01_phase_decode_absolute/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b01-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b01-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b01-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b01-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b02-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b02-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b02-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b02-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b03-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b03-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b03-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b03-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b04-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b04-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b04-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b04-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b05-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b05-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b05-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-decode-b05-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b06-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b06-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b06-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b06-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b07-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b07-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b07-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b07-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b08-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b08-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b08-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b08-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b09-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b09-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b09-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b09-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b10-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b10-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b10-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-decode-b10-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/03_phase_decode_abba_blocks_06_10/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r01.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r02.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r03.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r04.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r05.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r06.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r07.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r08.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r09.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r10.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/04_phase_prefill_p2048_absolute/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b01-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b01-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b01-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b01-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b02-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b02-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b02-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b02-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b03-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b03-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b03-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b03-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b04-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b04-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b04-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b04-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b05-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b05-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b05-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b05-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/05_phase_prefill_p2048_abba_blocks_01_05/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b06-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b06-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b06-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b06-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b07-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b07-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b07-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b07-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b08-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b08-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b08-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b08-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b09-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b09-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b09-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b09-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b10-a1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b10-a2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b10-b1.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq31p7-df-cmp-abba-ph-prefill-p2048-b10-b2.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/06_phase_prefill_p2048_abba_blocks_06_10/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/README.md
configs/campaigns/d117_floor_qwen3-1p7b_v5/calibration_plan.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/calibration_plan.sha256
configs/campaigns/d117_floor_qwen3-1p7b_v5/condition_families/condition_family_df_ph_decode.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/condition_families/condition_family_df_ph_prefill_p2048_qwen3_1p7b.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/condition_families/condition_family_df_ph_prefill_p42_qwen3_1p7b.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/decode_prompt_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/decode_workload_candidate.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py
configs/campaigns/d117_floor_qwen3-1p7b_v5/order_manifest.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.sha256
configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/prefill-prompt-ladder.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/prefill_prompt_pin.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/selection.json
configs/campaigns/d117_floor_qwen3-1p7b_v5/producer_contract.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r01.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r02.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r03.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r04.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r05.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r06.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r07.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r08.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r09.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r10.json
configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b01-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b01-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b01-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b01-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b02-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b02-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b02-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b02-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b03-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b03-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b03-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b03-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b04-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b04-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b04-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b04-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b05-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b05-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b05-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-decode-b05-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/02_phase_decode_abba_blocks_01_05/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b06-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b06-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b06-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b06-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b07-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b07-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b07-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b07-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b08-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b08-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b08-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b08-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b09-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b09-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b09-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b09-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b10-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b10-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b10-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-decode-b10-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/03_phase_decode_abba_blocks_06_10/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r01.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r02.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r03.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r04.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r05.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r06.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r07.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r08.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r09.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/d117fq38-df-ph-prefill-p2048-abs-r10.json
configs/campaigns/d117_floor_qwen3-8b_v5/04_phase_prefill_p2048_absolute/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b01-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b01-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b01-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b01-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b02-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b02-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b02-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b02-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b03-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b03-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b03-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b03-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b04-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b04-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b04-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b04-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b05-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b05-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b05-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/d117fq38-df-cmp-abba-ph-prefill-p2048-b05-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/05_phase_prefill_p2048_abba_blocks_01_05/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b06-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b06-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b06-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b06-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b07-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b07-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b07-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b07-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b08-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b08-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b08-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b08-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b09-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b09-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b09-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b09-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b10-a1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b10-a2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b10-b1.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/d117fq38-df-cmp-abba-ph-prefill-p2048-b10-b2.json
configs/campaigns/d117_floor_qwen3-8b_v5/06_phase_prefill_p2048_abba_blocks_06_10/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/README.md
configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json
configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.sha256
configs/campaigns/d117_floor_qwen3-8b_v5/condition_families/condition_family_df_ph_decode.json
configs/campaigns/d117_floor_qwen3-8b_v5/condition_families/condition_family_df_ph_prefill_p2048_qwen3_8b.json
configs/campaigns/d117_floor_qwen3-8b_v5/condition_families/condition_family_df_ph_prefill_p42_qwen3_8b.json
configs/campaigns/d117_floor_qwen3-8b_v5/decode_prompt_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/decode_workload_candidate.json
configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json
configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py
configs/campaigns/d117_floor_qwen3-8b_v5/order_manifest.json
configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json
configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.sha256
configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill-prompt-ladder.json
configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json
configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/selection.json
configs/campaigns/d117_floor_qwen3-8b_v5/producer_contract.json
configs/campaigns/v5_claim_25g83/flag_catalog.json
joulewise/__init__.py
joulewise/__main__.py
joulewise/adapters/__init__.py
joulewise/adapters/local_transport.py
joulewise/adapters/mlx_runtime.py
joulewise/adapters/mock_runtime.py
joulewise/adapters/mock_spec_runtime.py
joulewise/adapters/mock_telemetry.py
joulewise/adapters/node_client.py
joulewise/adapters/node_worker.py
joulewise/adapters/nvidia_smi.py
joulewise/adapters/powermetrics.py
joulewise/adapters/ssh_transport.py
joulewise/adapters/suite_control.py
joulewise/adapters/vllm_runtime.py
joulewise/agent_identity.py
joulewise/aggregate.py
joulewise/analysis_engine/__init__.py
joulewise/analysis_engine/artifact.py
joulewise/analysis_engine/claim_side_bound.py
joulewise/analysis_engine/claims.py
joulewise/analysis_engine/distributions.py
joulewise/analysis_engine/estimators.py
joulewise/analysis_engine/inputs.py
joulewise/analysis_engine/multiplicity.py
joulewise/analysis_engine/ratio.py
joulewise/analysis_engine/reason_kinds.py
joulewise/analysis_engine/registry.py
joulewise/analysis_engine/sensitivity.py
joulewise/analysis_manifest.py
joulewise/analysis_manifest_v2.py
joulewise/analysis_manifest_v3.py
joulewise/arm_census.py
joulewise/arm_readiness.py
joulewise/arm_readiness_evidence.py
joulewise/arm_readiness_evidence_t0.py
joulewise/arm_retry.py
joulewise/authentication_io.py
joulewise/axi_decode_config.py
joulewise/b5/__init__.py
joulewise/b5/chain.py
joulewise/b5/driver.py
joulewise/b5/harvest.py
joulewise/b5/plan.py
joulewise/b5/reference_spares.py
joulewise/battery_float.py
joulewise/benchmark_import.py
joulewise/benchmark_import_math.py
joulewise/bundle.py
joulewise/bundle_read.py
joulewise/calibration_bracketing.py
joulewise/calibration_custody_worker.py
joulewise/calibration_dispositions.py
joulewise/calibration_epoch_continuation.py
joulewise/calibration_exits.py
joulewise/calibration_ledger.py
joulewise/campaign_generator_core.py
joulewise/campaign_provenance.py
joulewise/cli.py
joulewise/clock.py
joulewise/clock_reference.py
joulewise/coldgate_receipt.py
joulewise/controller.py
joulewise/cooldown.py
joulewise/cooldown_anchor.py
joulewise/corecaptured_loop.py
joulewise/detection_floor.py
joulewise/detection_floor_registry.py
joulewise/determinism_gate.py
joulewise/doctor.py
joulewise/dominance_closeout.py
joulewise/dwell.py
joulewise/envelope_gate.py
joulewise/environment.py
joulewise/environment_admission.py
joulewise/evidence_night.py
joulewise/external/__init__.py
joulewise/external/km003c_parse.py
joulewise/external/km003c_usb.py
joulewise/flags/__init__.py
joulewise/flags/catalog.py
joulewise/flags/collect.py
joulewise/flags/core.py
joulewise/flags/exclusions.py
joulewise/flags/schema.py
joulewise/flags/sink.py
joulewise/floor_extraction.py
joulewise/floor_mint_estimator.py
joulewise/gensuite/__init__.py
joulewise/hazards/__init__.py
joulewise/hazards/arm.py
joulewise/hazards/base.py
joulewise/hazards/battery.py
joulewise/hazards/clock.py
joulewise/hazards/contention.py
joulewise/hazards/disk.py
joulewise/hazards/instrument.py
joulewise/hazards/monitor.py
joulewise/hazards/smc.py
joulewise/hazards/thermal.py
joulewise/identity_pins.py
joulewise/idle_admission.py
joulewise/idle_dependence.py
joulewise/interfaces.py
joulewise/kernel_clock.py
joulewise/kv_size.py
joulewise/load_transition_alignment.py
joulewise/measurement_liveness.py
joulewise/model_panel.py
joulewise/network_time_off.py
joulewise/night_agent_install.py
joulewise/night_gate.py
joulewise/night_kinds.py
joulewise/night_plan_writer.py
joulewise/output_identity.py
joulewise/paper_custody.py
joulewise/paper_rendering.py
joulewise/paper_reported_energy.py
joulewise/phase_share.py
joulewise/powermetrics_fiducial.py
joulewise/prewindow.py
joulewise/provenance.py
joulewise/publication_privacy.py
joulewise/quiet_admission.py
joulewise/quiet_guard.py
joulewise/quiet_guard_process.py
joulewise/quiet_predicate_campaign.py
joulewise/receipt_oracle.py
joulewise/reduce.py
joulewise/report.py
joulewise/results_fill_adapter.py
joulewise/salvage_dangler.py
joulewise/sampler_teardown.py
joulewise/scheduler_gates.py
joulewise/schemas.py
joulewise/scored_packer.py
joulewise/scored_reduce.py
joulewise/scored_registration.py
joulewise/suite.py
joulewise/t0_rehearsal.py
joulewise/uncertainty_evidence.py
joulewise/v5_qualification.py
joulewise/validation.py
joulewise/whole_window.py
joulewise/window_duration_margins.py
joulewise/window_lineage.py
joulewise/workload_profile.py
joulewise/workload_sizing.py
joulewise/workloads.py
joulewise/zero_capture_facts.py
scripts/admit_model_panel_entry.py
scripts/advance_b5_ledger_pin.py
scripts/analyze_phase_share.py
scripts/assemble_v5_battery_boundaries.py
scripts/author_arm_evidence_t0.py
scripts/author_arm_readiness_evidence.py
scripts/axi_sb_static_batch_spike.py
scripts/axi_sc_spec_decode_spike.py
scripts/b5_window_calibration_verdict.py
scripts/backup_runs.sh
scripts/bench_replay_start_drift.py
scripts/bench_replay_systemsetup_stub.py
scripts/bridge
scripts/build_bracket_binding.py
scripts/build_capstone.py
scripts/build_d165_dominance_closeout.py
scripts/build_family_marker.py
scripts/build_family_marker.py.sha256
scripts/build_site.py
scripts/build_v4_histsem_pinset.py
scripts/build_v4_histsem_pinset.py.sha256
scripts/calibration_cadence_report.py
scripts/calibration_ledger_backfill.py
scripts/calibration_ledger_bootstrap.py
scripts/cap_replay_harness.py
scripts/capture_t0_step.py
scripts/characterize_load_transition.py
scripts/check-codex-mcp.mjs
scripts/check_b5_chain.py
scripts/check_campaign_generator_core_parity.py
scripts/check_gate_ledger.py
scripts/check_paper_replay_fence.py
scripts/check_paper_round7_artifacts.py
scripts/check_sealed_bundle_compatibility.py
scripts/check_v5_arm_abort.py
scripts/check_window_provenance.py
scripts/claims_lint.py
scripts/claude-bridge-mcp.mjs
scripts/codex-app-bridge.mjs
scripts/codex-bridge
scripts/codex-run
scripts/codex_usage_probe.py
scripts/collect_clock_reference.py
scripts/collect_window_flags.py
scripts/corpus_compat_receipt.py
scripts/dependence_sensitivity.py
scripts/derive_estate_anchors.py
scripts/digest_pin_census.py
scripts/ed_session/build_rehearsal_env.sh
scripts/ed_session/capture_t0_anchor_positive_control.py
scripts/ed_session/rail-probe.sh
scripts/ed_session/sampler-checklist.sh
scripts/emit_floor_mint_pinset.py
scripts/epoch_equivalence_check.py
scripts/extract_detection_floors.py
scripts/finalize_analysis_manifest.py
scripts/fixture_orphan_census.py
scripts/floor_mint_pinsets/README.md
scripts/floor_mint_pinsets/mint1.json
scripts/floor_mint_pinsets/schema_v2.json
scripts/floor_reconciliation_receipt.py
scripts/g10_clock_step_control.py
scripts/gen_affine_smoke.py
scripts/gen_derivation_night.py
scripts/gen_evidence_night.py
scripts/gen_g2_phase_d.py
scripts/gen_gsm8k_scored.py
scripts/gen_jw_mixed.py
scripts/gen_math_scored.py
scripts/gen_state.py
scripts/generate_arm_readiness.py
scripts/generate_g2a_probe_inputs.py
scripts/generate_matrix.py
scripts/harvest_b5_window.py
scripts/harvest_g2a_window.py
scripts/harvest_v5_g2b_window.py
scripts/harvest_v5_qualification.py
scripts/harvest_window.py
scripts/hazard_monitor.py
scripts/hydrate_d117_fixture.py
scripts/install_magistrate_watchdog.sh
scripts/install_night_agent.sh
scripts/issue_calibration_acceptance_generation.py
scripts/issue_dg071_dg075_statistics.py
scripts/issue_epoch_continuation.py
scripts/issue_g2a_prefill_prompt_pin.py
scripts/issue_p8_pin_delta.py
scripts/joulewise-network-time.sudoers
scripts/km003c_monitor.py
scripts/land_window_records.py
scripts/launch_window.py
scripts/magistrate_watchdog.py
scripts/make_figures.py
scripts/measure_claude_cold_start.sh
scripts/mint_floor_artifact.py
scripts/mint_floor_artifact_generalized.py
scripts/night_chains/calibration_derivation_only.zsh
scripts/night_chains/quiet_predicate_evidence.zsh
scripts/p8_evidence/baseline-provenance.json
scripts/p8_evidence/issuance.stdout.txt
scripts/p8_evidence/n1.json
scripts/p8_evidence/n1.stdout.txt
scripts/p8_evidence/n2.json
scripts/p8_evidence/n2.stdout.txt
scripts/p8_evidence/pin-classification.json
scripts/p8_evidence/r7-p8.diff
scripts/p8_evidence/r7_corpus_baseline.json
scripts/pack_capsule.py
scripts/package_bundle_pack.py
scripts/package_d117_fixture.py
scripts/paper/partial_record_enclosure.py
scripts/paper_anchor_correction_quantified.py
scripts/paper_excursion_decomposition.py
scripts/paper_prefill_resolvability_projection.py
scripts/paper_renumber_refs.py
scripts/paper_terms_lint.py
scripts/prewindow_check.sh
scripts/produce_t0_rehearsal_bundle.py
scripts/project_identity_pins.py
scripts/promote_calibration_candidate.py
scripts/quick_suite.py
scripts/quiet_guard.py
scripts/quiet_guard_privileged.py
scripts/quiet_mac_prep.sh
scripts/quiet_window_clock.sh
scripts/reauthor_clean.py
scripts/reconcile_retained_powermetrics.py
scripts/record_window_duration_margins.py
scripts/recover_calibration_ledger.py
scripts/refresh_receipt_histsem_pinset.py
scripts/refresh_receipt_histsem_pinset.py.sha256
scripts/rehearse_b5_real.py
scripts/rehearse_t0_unattended.py
scripts/reissue_calibration_acceptance.py
scripts/release_check.py
scripts/render_results_fills.py
scripts/repin.py
scripts/replay_d117_decisive.sh
scripts/replay_powermetrics_frames.py
scripts/reserve_calibration_window_bracket.py
scripts/restore_v5_null_reservation.py
scripts/run_campaign.py
scripts/run_night.py
scripts/sample_quiet_predicate_evidence.py
scripts/select_g2a_prefill_length.py
scripts/setup_quiet_guard.sh
scripts/shard_tests.py
scripts/sim_acc_25g83_rev5.py
scripts/size_b5_window.py
scripts/spike_mlx_prompt_cache.py
scripts/summarize_g2a_prefill_probe.py
scripts/test_timings.json
scripts/v5_s1_desk_closeout.py
scripts/validate_gate_packet.py
scripts/validate_powermetrics_fiducial.py
scripts/verify_family_marker.py
scripts/verify_family_marker.py.sha256
scripts/verify_p8_replay.py
scripts/verify_receipt_histsem.py
scripts/verify_receipt_histsem.py.sha256
scripts/window_status.sh
scripts/write_b5_identity_pins.py
scripts/write_b5_window_plan.py
scripts/write_derivation_night_inputs.py
scripts/write_v5_qualification_plan.py
```
