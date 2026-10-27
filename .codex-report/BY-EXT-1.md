# BY-EXT-1: BYTES extension packs

Seat BY-EXT-1 (cloud, Claude Code), 2026-10-27. Lane `lane/2026-10-27-bytes-extension`, cut from
`origin/work/2026-10-23-by-slots-draft` at `991358f73`. Authority: `docs/registrations/bytes_extension_models_2026-10-27.md`
(main `386e1bbc`); end date `docs/registrations/bytes_end_date_amendment_2026-10-27.md`.

No download, inference, power capture or measurement was run. No real measurement data was read. This cloud host could
not reach huggingface.co, github.com or pypi.org (proxy 403 / DNS refusal), so the Hugging Face and mlx-lm evidence below
comes from web search, not from the files themselves. Each such item says so and has a Mac-side confirmation step.

## 1. Nemotron 3.5 Super 120B-A12B: NOT FEASIBLE (dropped, recorded, no substitute)

The registration's condition is a build that the pinned mlx-lm 0.31.3 loads (`env/mac-measurement-lock.txt:26`) and
that passes a 3-5 run resolvability check. On the evidence available, no build meets the first half:

- **No mlx-community build of Nemotron 3.5 Super.** mlx-community has Nemotron **3** Super builds
  (`mlx-community/Nemotron-3-Super-120B-A12B-MLX-6bit`), not 3.5. The 3.5 Super line is released as a vision-language
  model, "Nemotron 3.5 Super VL 120B-A12B" (release listed 2026-10-15).
- **The two about-4-bit MLX builds of 3.5 Super found both fail the "stock pinned mlx-lm" condition, by their own model
  cards (per search summaries):**
  - `Duckets/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-MLX-4bit`: full omni model including the vision tower; targets
    **mlx-vlm** and LM Studio, not mlx-lm. Affine 4-bit, group 64, about 4.57 bits per weight, 64.7 GiB.
  - `rapid-mlx/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-MLX-4bit`: text-only (vision tower, projector and MTP head
    removed), but it "requires an upcoming Rapid-MLX release" and "stock loaders do not apply the required precision
    adapter". Peak 72.7 GB at 1K context.
  - Ollama's `120b-a12b-nvfp4` / `mxfp8` / `bf16` tags are Ollama-format, not a Hugging Face MLX checkpoint.
- **mlx-lm 0.31.3 models directory: UNVERIFIED from here.** github.com and pypi.org are unreachable, so I could not list
  `mlx_lm/models/` at v0.31.3. Indirect evidence: oMLX v0.2.17 attributes "Nemotron Super hybrid architecture support
  (layers_block_type config, MoE latent projections)" to an upstream mlx-lm commit around 0.31.2, so a `nemotron_h` class
  very likely exists for Nemotron **3** Super. Whether it loads the 3.5 Super VL checkpoints is the open question, and
  the two builds' own cards say stock loaders do not.
- **No exact repo revision or size** could be read (Hugging Face API blocked), so even a candidate could not be pinned.
- **`scripts/bytes_manifest.py` could not represent it without a change:** `FAMILIES` has no `nemotron_h`, and `classify`
  has no Mamba mixer names (`backbone.layers.N.mixer.*`, `A_log`, `D`, `conv1d`, `dt_bias` under a mixer). Because the
  model is dropped, I made no change to the manifest script.

Verdict: **NOT FEASIBLE** on present evidence. Only Qwen3.8-27B is prepared. Nemotron sits in the extension roster's
`dropped` list (no configs, no pack; `bytes-s8-p1` is reserved and not created). The extension H1 family is therefore
3 checks per boundary (rule 4). One Mac-side check confirms or reverses this in a minute (section 4, step N), but a
reversal would need a new pack, a manifest-script change and a new refuter pass, and it must still finish before
2026-11-05T00:00:00-08:00.

Sources: huggingface.co/mlx-community/Nemotron-3-Super-120B-A12B-MLX-6bit;
huggingface.co/Duckets/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-MLX-4bit;
huggingface.co/rapid-mlx/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-MLX-4bit;
newreleases.io/project/github/jundot/omlx/release/v0.2.17; orcarouter.ai blog "nemotron 3 5 super ollama local".

## 2. Qwen3.8-27B MLX 8-bit: repo id found, revision NOT in the repository

- **Repo id:** `mlx-community/Qwen3.8-27B-8bit` (the official mlx-community 8-bit build; web search, 2026-10-27). The
  model card lists it as image-text-to-text, so expect vision-tower and possibly `mtp.` tensors; the manifest script
  already records those as `not_loaded` and keeps them out of W and R.
- **The repository has no record of the download's repo id or revision.** RUN_STATE item 66 says only "Qwen3.8-27B-8bit
  ... downloaded". Searching every ref (`git log --all -S Qwen3.8`, `git grep` over all remote refs) finds one more
  record: `docs/process_traces/2026-10-25-magistrate-f18a96e1/RECORD.md:26-30` (commit `52afc456d`). **That session
  deleted the Qwen3.8-27B-8bit cache on 2026-10-25** to free disk, with the snapshot revisions saved in
  `~/night-archive/seats-f18a/models-removed.txt` on the Mac. So "the revision already downloaded" is no longer on disk.
  Its revision is in that Mac file only. The model must be **re-downloaded** at that revision.
- Revision, download size and organisation confirmation are therefore MAC-PENDING slots. The configs carry
  `revision: null` until then, as the registered drafts did before the 8B-8bit download.

## 3. What was prepared

All new files are in WRITE_SCOPE. No registered pack, analysis or estimator file changed.

| Path | What |
|---|---|
| `configs/campaigns/bytes_v1/extension/generate_extension.py` | Extension generator. Reuses the registered generator's assembly (10 repeats + 10 null ABBA quads), template and serialisation, read-only. `--check` verifies; `--tree` (desk only) writes the plan tree and refuses while any slot it needs is MAC-PENDING. |
| `configs/campaigns/bytes_v1/extension/slots.json` | Every Mac value as an explicit `MAC-PENDING` slot (section 5). |
| `configs/campaigns/bytes_v1/extension/roster.json` | Extension roster: Qwen3.8 prepared (`registered_roster_member: false`); Nemotron in `dropped`. Workload copied from the registered roster. |
| `configs/campaigns/bytes_v1/extension/qwen38-27b-8bit/{01_decode_absolute,02_decode_abba_01_05,03_decode_abba_06_10}/` | 50 run configs + 3 order manifests: 2,048-token synthetic prompt, 512 greedy decode tokens, int8 / group 64, tag `bytes-extension`. |
| `configs/b6/packs/bytes-s7-p1/registration.json` | Draft extension pack: pass 1 only, target/minimum 1/1, `end_t0_before 2026-11-05T00:00:00-08:00`, blinding group `bytes`, `bytes_extension` block (rules 1-6), `pending_slots`, the registered pass-1 estimator digest (rule 4: the same unchanged module evaluates extension rows). `est_minutes` is null (MAC-PENDING). |
| `tests/test_bytes_extension.py` | 12 tests (section 6). |

Design decisions:

- **Configs live under `bytes_v1/extension/`**, not beside the registered model directories, and the registered
  `generate_configs.py`, `roster.json` and `pass_order.json` are byte-unchanged. A test holds the extension's config body
  to reproduce a registered config byte for byte when its extension markers are off, so the workload cannot drift.
- **Source path** `/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit`: the plain local-directory convention of
  Qwen3-8B-8bit and Qwen3.5-122B, one download destination and a separately pinned revision.
- **Blinding group `bytes`** on purpose. Qwen3.8 is not in `blinding.FIT_MODELS`, so its rows are `heldout`: blinded with
  the group's pack factor and written to the withheld store (rule 3). Consequence for the gate: the registered
  `b6_release_subset.py --stage heldout` will list its key too. That release comes after the predictions commit, which
  rule 3 allows.
- **The plan tree is not committed.** The fixed-pack readers require it at `configs/campaigns/bytes-s7-p1/`
  (`joulewise/b5/plan.py:782`, `joulewise/b6/precheck.py:428`, `joulewise/b6/smoke.py:271`), which is outside this lane's
  WRITE_SCOPE, and it binds the MAC-PENDING revision. `--tree` produces it at the desk. A test builds it in memory from
  synthetic slot values: 13 stages, the same stage kinds as registered single-model `bytes-s5-p1`, 50 science members,
  identity units `neg8_reference` and `qwen38-27b-8bit`, `draft_status: draft`, smoke keep
  `{reference-start: 1, bytes-qwen38-27b-8bit-absolute: 1, reference-end: 1}`.
- **`--tree` reuses `scripts/bytes_plan_trees.tree_files` unchanged.** During that call only, it points the module's
  roster lookup at the extension roster and keeps pass 1 draft for an unregistered extension pack, then restores both.
  The restore is tested.
- **`scripts/bytes_manifest.py` unchanged** (section 1 for Nemotron). For Qwen3.8 its tensor vocabulary already covers a
  Qwen3.5-style dense hybrid (`linear_attn.*`, `self_attn.*`, dense `mlp.*`, vision and `mtp.` as not_loaded), but
  **`FAMILIES` may not contain Qwen3.8's `model_type`** (unknown here: `config.json` unreadable). If it does not, the
  headers step refuses, and adding the type is a separately authorized change. That is MAC-PENDING slot
  `config_model_type`.

## 4. Mac-side step list for the orchestrator

**When:** only at a SESSION_DESK or while the BYTES loop is held. Never while the loop is in PRECHECK, ARM_WAIT, SMOKE_*
or SESSION_RUN. Steps 4-6 load the model, so no session or [QUIET-MAC] measurement may start until they end. Work in a
desk worktree of this lane, never in the measurement checkout. Fill each slot in `slots.json` with its observed value,
`status: "filled"` and the receipt path. **Order:** after the registered pass-1 sub-packs and the fit set (rule 1); if
time runs short, the extension is dropped first.

N. *(optional, 1 min, reverses section 1 only if positive)* In the measurement venv:
   `python -c "import mlx_lm, pathlib; print(sorted(p.stem for p in (pathlib.Path(mlx_lm.__file__).parent/'models').glob('nemotron*')))"`.
   Report the list. Even a `nemotron_h` hit does not make a 3.5 Super VL checkpoint loadable: the lead decides.

1. **Identity.** `grep -i 'qwen3.8' ~/night-archive/seats-f18a/models-removed.txt`. Fill `hf_repo` (expected
   `mlx-community/Qwen3.8-27B-8bit`) and `revision` (full 40-hex). If the file names another organisation or is missing,
   stop and ask the lead; do not pick a revision.
2. **Size and free disk.** Size of the pinned revision:
   `python -c "from huggingface_hub import HfApi; i=HfApi().model_info('<repo>', revision='<rev>', files_metadata=True); print(sum(s.size or 0 for s in i.siblings))"`.
   Free space: `df -k /Users/edr` (×1024). Proceed only if free − size ≥ the largest `P + smoke` still needed by a
   registered pack before its session (registration §5 disk table; s4-p1 is 118,843,585,614 B), plus this pack's own
   `P + smoke` once known. Planning only, not a slot value: an 8-bit 27B checkpoint is around 28-30 GB. Fill
   `download.size_bytes` and `download.free_disk_before_bytes`.
3. **Download** (desk; not during a session):
   `hf download <repo> --revision <rev> --local-dir /Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit`.
   Then `du -sk` of the directory and `df -k` again. Fill `download.free_disk_after_bytes`. Read `config.json`: fill
   `config_model_type` and confirm `quantization.bits == 8` and `group_size` (fill `group_size`; if it is not 64, put the
   observed value in the slot and regenerate).
4. **Bytes manifest, headers** (stdlib, no model load):
   `python3.13 -B scripts/bytes_manifest.py headers --model-dir /Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit --revision <rev> --out <desk>/extension/Qwen3.8-27B-8bit.headers.json`.
   If it refuses with `unsupported architecture`, stop: the manifest script needs an authorized change. Any
   `unclassified tensor` refusal also stops.
5. **Bytes manifest, KV** (runs inference, no power capture, loop held):
   `python3.13 -B scripts/bytes_manifest.py kv --model-dir ... --revision <rev> --out <desk>/extension/Qwen3.8-27B-8bit.kv.json`.
   Recurrent layers are recorded as constant-size state (rule 2). Then merge into a **separate** extension manifest with
   an explicit `--out`. The default `--out` is the frozen registered `configs/bytes/bytes_manifest.json`, whose SHA-256
   is pinned by the registered analysis and must never be overwritten:
   `python3.13 -B scripts/bytes_manifest.py merge --headers <...headers.json> --kv <...kv.json> --out <desk>/extension/bytes_manifest_extension.json`.
   Fill `manifest.*` (W, R, KV occupied, KV allocated, b, not_loaded, record paths).
6. **Resolvability check (3-5 runs).** **NEEDS RULING:** the registered models' check ran inside the non-claim H session
   kit (`scripts/bytes_mac_kit.py`, `configs/campaigns/bytes_mac_check`), which has no extension entry, and both files are
   outside this lane's scope. The lead picks the vehicle: (a) a kit extension (new scope), or (b) a separate non-claim
   held-loop run of 5 absolute repeats of `bytes-qwen38-27b-8bit-abs-r01..r05` with power capture. Pass rule as for
   Qwen3-8B-8bit: each run succeeded, unexcluded, 512 output tokens, with an identifiable bounded decode phase. Fill
   `resolvability`. A failure drops the model (recorded, no substitute) and ends the extension.
7. **Sizing, clock and disk rows** from the step-6 member walls and stream spans, with the registered formula
   (registration §5; `scripts/bytes_gates.py:133-138`): S, T_stream_max, B, P, smoke share (1/50 science +
   2 references: smoke members 3 of 75, as s5/s6), clock hold H = 5000/T_stream_max − 0.25 ppm. The lead adds row
   `/packs/bytes-s7-p1` to `configs/b6/registration/sizing_b5.json`; that file is outside this lane's scope, and
   without it precheck flags `disk.budget_missing`. Fill `sizing_row`, `disk`, `clock_hold_ppm`, `est_minutes`
   (= 50 × member_allowance_s / 60) and `est_minutes.source.sha256`.
8. **Regenerate:** `python3.13 -B configs/campaigns/bytes_v1/extension/generate_extension.py`, then `... --tree`.
   It refuses while any slot is open. The lead adds the printed smoke-keep entry to `configs/b6/smoke_keep.json`, adds
   `bytes-s7-p1` to `configs/b6/loop.json` `base_order` after the pass-1 packs (never to `pass_order.json`, which is the
   registered roster's order), and issues C4 identity pins for the model. All three files are outside this lane's scope.
9. **Gate:** one blind executing refuter (gate policy rule 5) on the filled lane. Only after its admit: set
   `packs.bytes-s7-p1.registration_status` to `registered`, regenerate, `--check`, commit to the measurement checkout.
   Pin changes change the session fingerprint.
10. **Smoke on the pack's first session.** The loop smokes a pack whose fingerprint is new (smoke keep: start reference,
    the first absolute run, end reference). The orchestrator reads the smoke verdict at the next desk before the
    counting session counts, and confirms the export lands under `export/bytes-s7-p1/`, **outside** any `--export`
    directory given to the registered analysis. The registered analysis refuses a session it has no locator for
    ("export session lacks archive locator") instead of mixing it in, so a misplaced export fails loudly.

## 5. MAC-PENDING list

From `bytes-s7-p1` `bytes_extension.pending_slots` (12 slots):

`/models/qwen38-27b-8bit/`: `hf_repo` (confirm), `revision`, `download` (size, free before/after), `config_model_type`,
`group_size` (verify 64), `manifest` (W, R, KV occupied/allocated, b, not_loaded, records, extension manifest path),
`resolvability` (verdict, runs, decode-phase range, receipt).
`/packs/bytes-s7-p1/`: `sizing_row` (programmed_span_s, T_stream_max_s), `disk` (B, P, smoke share, P + smoke),
`clock_hold_ppm`, `est_minutes/value`, `est_minutes/source` (sizing file sha256).

Not slots, but owed by the lead (outside WRITE_SCOPE): the plan-tree directory `configs/campaigns/bytes-s7-p1/`, the
`sizing_b5.json` row, the `smoke_keep.json` entry, the `loop.json` placement, the C4 identity pins, and the
resolvability vehicle (step 6).

## 6. Tests

Environment: Python 3.13 (`/opt/homebrew/bin/python3.13` symlinked to `/usr/bin/python3.13`),
`JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR` set to a scratch directory. **zsh could not be built**:
github.com and apt are unreachable from this host. Tests that need `/bin/zsh` are not run here.

`tests/test_bytes_extension.py`, 12 tests, OK:
- the generator `--check` passes; the registered generators (`generate_configs.py --check`,
  `bytes_plan_trees.py --check`) still pass;
- the workload matches the registered one byte for byte;
- the registration is a one-pass draft extension with the 2026-11-05 end, explicit pending slots, and only the pending
  `est_minutes` validator objection;
- Nemotron is recorded as dropped, with no pack or configs;
- `--tree` refuses on pending slots, and once filled (synthetic) it matches the registered single-model shape;
- exclusion: not in the registered roster, `REGISTERED_MODELS`, `pass_order.json`, `loop.json`, `smoke_keep.json`,
  `sizing_b5.json`, `bytes_plan_trees.GROUPS` or either registered generator's output; the registered H1 family stays 21
  and the analysis refuses extension predictors; rows are `heldout` (withheld), never fit; `open_packs` rejects the
  draft;
- byte identity: `git diff 991358f73` is empty over all twelve registered packs and trees, the registered roster, order,
  generators, manifest script, analysis, `configs/bytes`, loop, smoke keep and registration directory.

Affected existing suites (14 modules, 132 tests: bytes plan trees, bytes packs, b6 registration, bytes manifest,
roster drop, blinding, release subset, plan inputs, mac kit, bytes launch, plan render, lane adapters, cold-pass fixes,
fix416 gates), run on this branch and on an untouched worktree at `991358f73`:
- base: 14 failures and 16 errors, all environmental (`/bin/zsh` missing; full-round fixtures; the scratch path contains
  an agent-census substring). Same set on the branch.
- branch only: 4 failures/errors. Each came from an existing test that enumerates every `configs/b6/packs/*` or
  `bytes-s*` registration and expects the registered twelve: `test_every_loop_pack_tree_authenticates_through_its_sidecar`,
  `test_precheck_all_twelve_p_and_retained_smoke_boundaries`, `test_preparation_reads_the_bytes_pack_effect_and_catalog_pin`
  (they need the desk-built tree), and `test_current_twelve_registrations_resolve_ten_science_keys_plus_neg8` (the
  extension's key joins the `bytes` group as held-out). Fixed in `tests/test_bytes_plan_trees.py`,
  `tests/b6/test_plan_inputs.py`, `tests/b6/test_fix416_gates.py` (skip registrations carrying `bytes_extension`) and
  `tests/b6/test_release_subset.py` (it asserts the extension key is exactly one and `heldout`, then the registered ten
  plus NEG-8 as before). All four now pass. These are test-only edits for the new packs; no production code changed.
- `tests.test_b6_loop`, `tests.test_bytes_gates`: one more branch-only failure,
  `test_bytes_drafts_never_enter_live_loop_despite_base_order`. The real git/status gate rejects the draft
  `bytes-s7-p1` (the intended behavior), so its expected rejected set now includes it. The 2 remaining errors there are
  `/bin/zsh` (environmental).
- The full repository suite was not run here. The Mac whole suite remains the merge gate.

## 7. For the gate-policy refuter

Ready for the refuter **on the cloud-side preparation**, with these open items it should test:
1. Nemotron NOT FEASIBLE rests on search summaries, not on files (HF, GitHub and PyPI were blocked here).
2. The Qwen3.8 revision is unrecoverable from the repository. The copy was deleted on 2026-10-25, and the revision
   exists only in a Mac file.
3. Step 6's vehicle needs a ruling, and steps 7-8 need lead commits outside this lane's scope.
4. `bytes_manifest.py` `FAMILIES` may need Qwen3.8's model_type: an authorized change, if so.
5. Blinding group `bytes` puts the extension key into the registered held-out release list. The rules allow it, but the
   refuter should confirm.
6. `tests/test_bytes_manifest.py:349` globs `configs/campaigns/bytes-s*-p1` to rebuild the registered family. Once the
   desk writes `configs/campaigns/bytes-s7-p1/`, that test will see the extension cells and fail, so the desk commit must
   narrow it to s1-s6. No production code globs that pattern for a roster or family. `precheck`/`plan_inputs` use the
   `bytes-s` prefix for disk terms, which the extension needs.
7. `tests/test_bytes_extension.py`'s byte-identity test diffs against `991358f73`. The end-date amendment regenerates the
   registered packs, so whoever lands that amendment on this lineage must move `BASE` to the amendment commit.
