# BYTES configuration drafts

Build authority: `docs/design/bytes_pack_design.md`, including Addendum 5 at
`6b2007220`. These files are drafts, not permission to collect. No inference,
model download, power capture or measurement was run for this fix.

Regenerate and verify with Python 3.13:

```sh
python3.13 -B configs/campaigns/bytes_v1/generate_configs.py
python3.13 -B scripts/bytes_plan_trees.py
python3.13 -B configs/campaigns/bytes_v1/generate_configs.py --check
python3.13 -B scripts/bytes_plan_trees.py --check
```

There are 50 run configs per R1 model: ten absolute repeats, then ten identical
null ABBA quads in A1/B1/B2/A2 order, split into two five-quad manifests.
`roster.json` records the fit/held-out roles and workload.

Each sub-pack has two fixed packs, `bytes-sN-p1` and `bytes-sN-p2`, with one
`registration.json` each under `configs/b6/packs/`. The corresponding trees and
collection plans live under `configs/campaigns/bytes-sN-p1/` and
`configs/campaigns/bytes-sN-p2/`. Each registration names its own tree through
`plan_tree_ref`; there is no unused `pass_plan_tree_refs` map.

Pass 1 has target/minimum 1/1; pass 2 has 1/0. `configs/b6/loop.json` retains
ALPHA/BETA/GAMMA in their original order, then lists s1-p1 through s6-p1, then
s6-p2 through s1-p2. `pass_order.json` records the same BYTES order. Pass-2 trees
reverse whole model modules; runs within each module retain their order.
This config work supplies the base order; the existing queue still rotates its
order between rounds and does not enforce the requested interleaving after
replication rounds. A failed pass-1 attempt is not a dependency gate on pass 2.

## Manifest commands

The portable `scripts/bytes_manifest.py headers --model-dir DIR --out JSON`
reads headers and config only. Supply `--revision REVISION` for a pinned local
model directory without a Hugging Face snapshot revision or `_commit_hash`.
The script rejects unsupported architectures, unknown tensors, invalid stored
spans, duplicate tensors and inconsistent expert/tied-embedding metadata.

Tensors in `vision_tower.*`, `model.visual.*`, or a dotted `mtp.` segment get
category `not_loaded`, matching the discarded namespaces specified by Addendum
5. Their stored bytes remain in `categories.not_loaded` and the tensor inventory,
and contribute to neither W nor R. Other unknown names still refuse. The Mac
confirmation in Addendum 5 reports 333 vision tensors (0.9026 GB) alongside
68.6907 GB of language-model storage; no real model header was read in this fix.

The separate `kv --model-dir DIR --out JSON` command is Mac-only and **does run
inference**. It was not executed here. It uses the runtime's exact synthetic
prompt, a four-token warmup on that prompt, the inherited five-second settle,
and explicit greedy forwards without EOS stopping. The pinned mlx-lm 0.31.3
`stream_generate(max_tokens=512)` dispatches 512 decode forward passes inside
the measured request, including look-ahead. The manifest reproduces that work:
KV averages cache-state bytes after prefill (2,048 positions) and after decode
forward pass 512 (2,560 positions). Occupied bytes and backing capacity are
recorded separately; recurrent cache state remains constant.

Addendum 5 replaces R2/R3's earlier 511-pass statement. e = E_dec/512,
tau = T_dec/512, BW = b/tau. The printed label is **512 decode forward passes,
one of which yields no returned token**. The change is about 0.2% on e and
0.02% on KV. Runtime code is unchanged; analysis and twin constants belong to
their separate lanes. The existing KV endpoint key `after_last_token` is retained
for schema compatibility and now records the endpoint after all 512 passes.

`merge --headers HEADER_JSON ... --kv KV_JSON ...` writes
`configs/bytes/bytes_manifest.json` by default; `--out` selects another path.
Header/KV revision, config and tokenizer identities must agree. Merge requires
revision and tokenizer pins. It prints W minus the pilot's `read_meas_GB` in
bytes, since that pilot column excludes KV. A model absent from the pilot has
null comparison values. No real manifest or Mac KV observation was created.

## Decisions I made

- Use the campaign/pack id, including `-p1` or `-p2`, for window, evidence and
  collection-plan identities. This keeps every fixed-driver path distinct.
- Generate smoke rows using compose's existing modular smoke selection before
  freezing each tree: one absolute run per model and start/end references.
- Keep the 500 run configs and their manifests unchanged; only roster workload
  metadata changes to 512 passes. Preserve the inherited prompt, warmup, idle,
  settle, floor-unit and null-quad conventions.
- Preserve Addendum 5's minimum 0 for pass 2 despite the current validator's
  minimum-1 restriction. Generation tolerates only that known draft validation
  error; tests expose it. Every other validation error still stops generation.
- Classify discarded namespaces before removing language-model prefixes.
  Require the specified namespace/segment boundaries, so near misses refuse.
- Retain the KV schema and lazy MLX imports; test generation and Mac orchestration
  only with fakes. Count look-ahead in both warmup and main explicit loops.
- Preserve the existing flag catalog per Addendum 2. The earlier unresolved
  nonthermal-exclusion question is settled; no inclusion rule changes here.

## Ruling/code disagreements and remaining gates

- **Pass-2 registration blocker:** `joulewise/b6/pack_registration.py` requires
  `minimum_sessions >= 1` for every new pack. All six pass-2 drafts correctly
  contain 0 per Addendum 5, and validate returns exactly `minimum_sessions`.
  The existing discovery path would reject them even after status becomes
  registered. The validator must support the ruled optional pass before
  registration. This lane is explicitly forbidden to change `joulewise/b6`.
- The fixed driver now finds each campaign tree and smoke row, then stops at
  missing C5 sizing. C4 pins and C5 sizing/clock/contention/disk checks remain
  R8 item 7. All 12 packs retain draft status.
- Model sources include HF cache snapshots: C4 must hash through symlinks.
  8B-8bit's revision is pending and group_size=64 is assumed and unverified.
  Tokenizer and chat-template pins remain C4; context_window is unused by the
  runtime. These notes are included in every registration draft.
- For single-model s5/s6, the midpoint lies between quad halves after 30 runs;
  analysis must not assume that it splits models. Fixed packs bypass the
  265-minute science cap; s4's planned 254 minutes leaves 11 minutes, subject
  to measured sizing. These Addendum 5 item 5 notes are in every draft.
- The validator permits a top-level blinding group, but existing blinding code
  does not enforce the BYTES group or two-stage subset unblinding. C6/C7 remain.
- Mac download/KV/resolvability work, registered analysis/twin/estimators,
  extraction spec, the registration cold gate and smoke fingerprints remain
  later tasks. No live readiness is asserted.

## Validation on the cloud host

All unittest runs use Python 3.13, `JW_B5_SYNTHETIC_ONLY=1` and
`PYTHONDONTWRITEBYTECODE=1`. Header files are synthetic; KV paths use fakes only.
The full repository suite is not run for this bounded tooling/config fix; the
requested two test files, whole Block-6 suite and relevant census checks are run.

- Baseline: 18 targeted tests passed while all four review probes reproduced
  their findings.
- After the fix: 22 targeted tests pass, including 12 fixed-tree round trips,
  actual queue selection, smoke/path lookups, exact dropped-byte accounting,
  unknown-name refusal and 512-pass fake generation.
- Adapted path probe: all 12 campaign ids/directories and smoke rows resolve;
  only the intentionally missing C5 sizing row refuses. Adaptations change
  registration lookup only, to match the ruled per-pass packs.
- Adapted second-session probe: after `r1-bytes-s2-p1` counts, queue selects
  `r2-bytes-s2-p2` and reads pass 2 with reversed 30B-A3B/8B model order.
- The unchanged header probe still reconciles W/R to the pilot on four models;
  its Qwen3.5 vision case changes from exit 1 to exit 0.
- The unchanged decode probe reads the pinned mlx-lm source and uses a counting
  fake: runtime and manifest both dispatch 512 decode passes and end at 2,560.

- Registration/queue plus single-count, digest-pin, custody-mode, D-165 and
  refusal-allowlist checks: **87 tests, OK, one skipped**. New files were staged
  before the census. No additional registry needs a new pack or campaign entry.
- Whole `tests/b6`: **213 tests in 277.036 seconds, 19 failures and 4 errors**.
  All 19 failures name the fixture's missing `/opt/homebrew/bin/python3.13`
  (full-round, courier and loop/desk tests). Three errors are `/tmp` exhaustion
  while copying full-round fixtures. One error is reharvest source restore:
  the existing default 20 GiB reserve cannot fit on this host's 8.8 GiB `/tmp`.
  The required seat setup attempted the Python symlink but `/opt/homebrew`
  creation was denied by OS permissions; this host has no sudo. These are
  environmental failures, separate from the documented pass-2 validator gap.
- Both generators' `--check` paths and `git diff --check` pass. Existing smoke
  rows are unchanged; `loop.json` changes only `base_order`.

No Mac KV command, real-model inference, real safetensors-header validation or
measurement was run. The full repository suite was not run. The Mac whole-suite
run remains the merge gate; the 213-test cloud run is not a green merge gate.
