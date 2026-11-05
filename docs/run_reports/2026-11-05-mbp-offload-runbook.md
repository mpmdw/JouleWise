# 2026-11-05 — Measurement MBP offload and streaming gold runbook

> Historical pre-review report. Superseded by the [safety fix round](2026-11-05-mbp-offload-fix-round.md), including the external-SSD plan, pilot-9 retention and corrected PR #664/#667 references. The executable runbook is the current authority for this procedure.

Revised `docs/align/mbp_offload_and_gold_setup.md` on the requested existing
branch `lane/2026-11-05-mbp-offload-runbook`, starting at `57b318fc7` (the
original runbook commit). This documentation-only revision implements the
lead's streaming brief after Ed confirmed the measurement MBP SSD is 1 TB.
The initial worktree was clean. No commit was pushed.

## Changes and acceptance

- Replaced the 450 GB reclamation/full-checkpoint admission with minimal
  verified offload to about 150 GB **available**. Nominal peak additional
  allocation is about 120 GB: up to 95 GB converted output, about 15 GB working
  unit and about 10 GB overhead. The separate 30 GB free-space floor applies
  throughout. Step-ordered accounting, an admission guard and during-write
  enforcement requirements cover packaging, hydration, setup and each unit.
  Actual metadata and measured allocations must replace these estimates.
- Set the default offload order: already-offloaded ALIGN roots with surviving
  local sources (re-verify existing cloud copies first), then harvested pilots
  0–3 and 6–9, then unused models with full revision/digest/restore inventories.
  Deduplicate roots and stop once the budget passes. Cloud round-trip hashing,
  independent full restore for irreplaceable roots, KEEP-overlap checks,
  Ed-only exact-manifest deletion and per-root receipts remain in place.
- Kept block-5 originals on-device through release, all Qwen3-30B anchor
  revisions/shared blobs and Qwen3.8-27B, plus pinned infrastructure and custody.
  Removed the former optional reclassification of the two anchor models.
  Other study/personal roots are exclusions, not a fallback wipe queue.
- Replaced the whole-repo `snapshot_download` with an explicit metadata-only
  allowlist. The harness must derive ordered groups/subunits from the pinned
  `model.safetensors.index.json` `weight_map`. Each unit downloads only its
  shards, checks whole-file SHA-256 against HF LFS oids, runs gold parity with
  real carried activations/state, converts to the chosen MLX quantization,
  commits output/manifest/activation checkpoints, then deletes its bf16 source.
  The journal binds all pins, coverage, hashes and phase states; resume checks
  committed artifacts and prevents duplicate output entries.
- Documented expected layers 2–47 at about 3 shards / 7 GB each, layer 0's
  roughly 24-shard union requiring bounded subunits, and the layer-1 n-gram
  table's roughly 35 shards / 100 GB bf16. N-gram parity gathers only actual
  rows required by the fixed prompts/decoding cases; conversion streams every
  table tensor shard by shard. Untouched rows are not claimed parity-tested.
- Preserved STOP 12a for review of
  `lane/2026-11-05-align-flashnext-gold-parity`, including its streaming,
  disk-floor and resume behavior. Named intended `--mlx-module`, layer-range
  and resume controls without fabricating the unavailable range flag/CLI.
  Per-unit gates and a final lead coverage audit precede converted-model
  coherence/NLL, tool-call, benchmark and no-swap memory validation.
- Scheduled work after pilot 9's terminal harvest, ledger pin and required
  desk-product custody, using the lead-relayed RUN_STATE item 170 / PR #662
  pause. No new pilot is authorized at a gold checkpoint; restoration requires
  the lead/Ed's go and a fresh plan.

## Authority and uncertainty

M0 intake, the relevant restart/queue and KEEP records, repository conventions,
`docs/orchestration.md` and D-188 retention/blinding boundaries were reviewed.
This is a user-directed documentation revision; coordination state and task
registration remain lead-owned under the brief. Only this report and the
runbook changed. RUN_STATE, TASK_QUEUE, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` were not edited; no kernel task was registered.

The requested offline command
`git show origin/port/qwen4-exp-mlx:docs/align/qwen4_exp_port/GOAL.md` was read,
including item 11 and the status log. That local ref still resolves to
`1643e9aac43ebfc10443a31c30a0cdc506bcbfc6` and contains the older full-bf16 plan.
Likewise this base's RUN_STATE ends at item 169, with pilot 9 armed, rather
than the lead's item 170. The explicit streaming/pause brief controls this
revision; the runbook distinguishes that authority from stale local records.
No fetch was attempted. The lead should supply the updated goal/pause commit
and actual harvest/pause receipts before Mac execution.

The gold-parity branch is absent from local refs and may be unpushed. Its
reviewed commit, exact CLI/range semantics, torch pin, conversion interface
and unit checkpoint implementation remain unverified. The official HF full
revision, actual shard/group layout, available SSD bytes, archive coverage,
cloud quota/throughput and the output/working/overhead ceilings also remain
unmeasured. No model quantization or live completion is asserted here.
The layer-0 and n-gram streaming parity boundaries require harness review;
this document does not prove that the pending implementation meets them.

## Verification and handoff

- `python3.13 -B -m unittest tests.test_docs_freshness` — PASS, 31 tests in
  1.239 seconds initially and 1.052 seconds on the final check. The full suite
  was not run, per the brief and the active
  7-worker job; no implementation files changed.
- Extracted all 21 zsh fences and parsed each via `/bin/zsh -n` on stdin —
  PASS. Parsed all five embedded Python heredocs via `ast.parse` — PASS.
  Checked 14 numbered steps and absence of obsolete 450/491.2 GB admission,
  full-bf16 staging path and full-bf16 retention instruction — PASS.
  These checks parse documentation only; no runbook commands were executed.
- `git diff --check` and the protected-path diff — PASS. Final changed-path
  review is limited to the runbook and this report. Syntax and freshness
  checks do not establish hardware, network, conversion or parity validity.

No network, real restricted directory, measurement contents or external home
path was accessed. Permitted Git object reads through shared alternates were
used for repository code/records only. No pipeline, harvest, offload, deletion,
model download, native MLX test or measurement was run. There are no new native
MLX tests in this documentation change. Outside the sandbox, the lead must run
the reviewed harness's tiny/config native checks, full layers 0–47 streaming
parity including real n-gram rows, conversion and interrupted-unit resume
checks, then the converted-model end-to-end/no-swap checks on the actual Mac.
Exact commands remain gated on the supplied reviewed harness interface.

Next exact step: the lead supplies/reviews the gold-parity commit and CLI,
confirms pilot 9's harvest and the item-170 pause, and admits the exact streaming
budget. Ed then begins the numbered Mac steps in that paused slot. No open
ruling blocks this documentation commit; operational unknowns remain explicit
STOP gates rather than claims of successful execution.
