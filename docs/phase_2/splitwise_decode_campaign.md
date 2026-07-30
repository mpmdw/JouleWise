# Splitwise-vein decode contrast campaign (splitwise_decode_v1) — FROZEN PLAN DRAFT

**STATUS: DRAFT FROZEN PLAN + DRAFT PRE-REGISTRATION. NOT RATIFIED.**
**The magistrate ratifies; the lieutenant delivers. Do not run a window from this
document until §10 Q1 is answered.**

Authored 2026-07-29 for a quiet window the same night. Supersedes the 2026-07-29
WIP checkpoint (commit `3a73b03` + the M4 line in `3de370e`); the checkpoint's
evidence base is carried forward and re-verified below, its unmeasured 7B timing
estimate is replaced by a measured probe, and its central assumption — that the
contrast can be gated against the minted decode floor — is **refuted** in §2.

The task (Ed-directed, 24 h deadline) is the project's first cross-model
comparative campaign: decode-phase energy, Qwen2.5-1.5B-Instruct-4bit (arm A) vs
Qwen2.5-7B-Instruct-4bit (arm B), one quiet window under
`configs/campaign_policies/quiet_mac_p2_production.json`.

## 1. What is authored and where

| Deliverable | Location | State |
|---|---|---|
| Cross-model contrast campaign | `configs/campaigns/splitwise_decode_v1/` | authored, validator-clean |
| 7B decode floor calibration (contingency) | `configs/campaigns/qwen25_7b_decode_floor_v1/` | authored, validator-clean |
| 7B model profile | §3 below | finalized |
| Duration arithmetic | §4 below | measured-probe-based |
| Pre-registration sheet | §5 below | DRAFT, conditional on §2 |
| Operator checklist delta | §6 below | draft |
| Validation record | §7 below | lead-run |
| Open questions | §10 below | for ratification |

Both campaigns follow the `configs/campaigns/p2_015_floors/` convention: a
deterministic `generate_configs.py` that writes only below its own directory,
freezes one `calibration_plan.json` before any measurement, hashes the exact plan
bytes into `calibration_plan.sha256` and into every member config's
`calibration-plan-sha256=` tag, and emits one `order_manifest.json` per stage plus
a root manifest. Neither campaign directory contains the window references or the
NEG-8 bound corpus: `docs/phase_2/window_runbook.md` §4 forbids listing those as
science stages, because `window-chain.zsh` supplies the governed 3+1+3 references
(`configs/campaigns/window_references/`) and the 12-member in-window bound corpus
(`configs/campaigns/neg8_reference_corpus/`) itself, on the unchanged 1.5B
`df_rq_mid` condition.

## 2. BLOCKING FINDING — the contrast is collectible tonight but not claimable

Verified this session by direct reading of the primary code, not by report.
**Two independent blockers stand between tonight's contrast bundles and a gated
claim.** Neither is a defect; both are the ratified P2-039/D-058 design working as
designed. Both were unknown when the checkpoint was written.

### Blocker A — the 7B arm has no floor, and floor transport is stack-bound

`floor_stack_identity` (`joulewise/analysis_engine/inputs.py:426-513`) derives the
stack identity from *realized bundle evidence*, and one of its eleven components is

```python
"model_artifact_sha256": artifact_sha,
```

taken from `workload_provenance.model.artifact_identity`. A 7B bundle therefore has
a different `stack_identity_sha256` from every 1.5B bundle, necessarily.

Every route from a consumer to a floor is gated on that hash:

- Evidence homogeneity: all evidence rows for one condition family must yield
  exactly one stack hash, else no floor request is built at all
  (`inputs.py:2862-2871`, `if len(consumer_stack_hashes) != 1: return None`).
- Exact-cell match additionally requires
  `binding.cell_stack_identity_sha256.get(cell_id) != consumer_stack_hash → continue`
  (`inputs.py:2884-2894`).
- Transport match requires `("stack_identity_sha256", consumer_stack_hash)` to
  equal the transport group's (`inputs.py:2912-2921`).

The minted artifact `df-ph-decode-floor-mint1` carries exactly one cell and one
transport group, both bound to the **1.5B** calibration stack, and exactly one
allowed consumer condition family — `df-ph-decode` with hash `e38e2a2f…762bfe`
(`scripts/mint_floor_artifact.py:1514-1528`, ids hard-pinned at `:59-93`).

Consequence: **the 7B arm resolves no floor under any naming.** The refusal is
`floor_row_missing` / `floor_transport_inapplicable`, both in `_NOT_RESOLVABLE`
(`joulewise/analysis_engine/claims.py:170,173`), and one unusable arm voids the
contrast — `if not all_usable: floor_abs = floor_cmp = floor_gate = None`
(`joulewise/analysis_engine/__init__.py:405-408`).

Arm A does not clear either, for a second reason worth recording. If arm A declares
the family id `df-ph-decode`, `same_condition_seen` is set (`inputs.py:2878-2881`)
and the exact-cell match then fails on `cell_scientific_identity_sha256` — a new
campaign's members carry different run-metadata tags from window C's, and
`scientific_config_identity` (`inputs.py:1846-1866`) strips only `run_id`, `rep\d+`,
the two `analysis-replacement-*` tags, and the four `calibration-*` prefixes. Once
`same_condition_seen` is true, transport is not attempted at all
(`inputs.py:2908-2909`, `if matches or same_condition_seen: return None`). If arm A
instead declares a new family id, transport *is* attempted but
`allowed_consumer_condition_families` lists only `df-ph-decode`, so no group
matches.

The prerequisite for any 7B decode claim is therefore a **7B decode floor**:
absolute + null-ABBA calibration on the 7B stack, extracted and minted. That is what
`configs/campaigns/qwen25_7b_decode_floor_v1/` collects. Note that consumption of
that evidence also needs tooling work: `scripts/mint_floor_artifact.py` is
hard-pinned to the p2_015 / a10 / window-C evidence (`CELL_ID`, `PLAN_SHA256`,
both order-manifest ids, `A10_SPEC_MEMBERS = 30`, `WINDOW_C_SPEC_MEMBERS = 40`,
`EXPECTED_OPERATIVE_FLOOR_TEXT = "7.377086"`) and needs a generalized sibling. That
work is desk work; the collection is not.

### Blocker B — no analysis-manifest schema can express a model-vs-model contrast

`analyze_claims` validates its manifest with the AP-2 **v1** validator
unconditionally (`inputs.py:403`, importing `validate_analysis_manifest` from
`joulewise.analysis_manifest` at `inputs.py:22`). That validator is frozen to the
Slice-2M speculation design:

- `contrast["block_ids"]` must equal `[f"block-2m-{model_tag}-r{rep:02d}" …]`
  derived by stripping `cell-2m-` / `cond-2m-` prefixes
  (`joulewise/analysis_manifest.py:1347-1356`);
- `multiplicity` must equal `{"method": "holm", "alpha": 0.05, "q": None, "m": 6}`
  (`analysis_manifest.py:1391`);
- estimator must be `paired_block_mean_difference_t_v1`, direction `two_sided`,
  `equivalence` and `mde` both null.

The v2 sibling (`joulewise/analysis_engine/registry.py:390`) is equally frozen —
`floor["condition_family_ids"] == ["spec_off", "spec_on"]` — and is not the
validator `analyze_claims` uses.

Consequence: **even with two floors in hand, no manifest for a
Qwen2.5-1.5B-vs-7B decode contrast validates on this branch.** Extending the
manifest vocabulary is design-bearing, contract-adjacent work — not a tonight task.

### What this does and does not mean

It does **not** mean the campaign is wrong or the evidence is worthless. Bundles
collected under a frozen, pre-registered plan in a governed quiet window remain
valid evidence; what is missing is the consumption path. It **does** mean the
document's original framing — "the first claim-bearing comparative campaign …
consumed into claims against the operative decode floor" — is not achievable from
tonight's window, and the pre-registration in §5 is conditional.

### Option set for the magistrate (§10 Q1)

| | Option | Runs tonight | Estimated window | What it buys | What it still needs |
|---|---|---|---|---|---|
| **O1** | Floor-first | `qwen25_7b_decode_floor_v1` | ~3.0 h | The 7B decode floor evidence — the strict prerequisite for every 7B claim | A generalized mint tool (desk work) |
| **O2** | Contrast-as-evidence | `splitwise_decode_v1` | ~2.6 h | The contrast bundles banked under a frozen plan | The 7B floor *and* new manifest machinery, both unbuilt |
| **O3** | Both, two independently calibrated windows | both | ~5.6 h + two brackets | Everything | Ed's availability; runbook §3 prefers splitting over one long window |
| **O4** | Defer collection | neither | — | A night of mint-generalization and manifest-extension design | Another quiet window later |

**Lieutenant's advisory recommendation: O1.** It is the only option whose collected
evidence has a fully specified consumption route (existing extraction + a
generalized mint, no new science), it is on the critical path for *both* O2 and any
later cross-generation work, and it spends the scarce resource — a quiet window on
a machine that must otherwise sit idle — on the one thing that cannot be done at a
desk. Under O1, `splitwise_decode_v1` stays authored and ratified-in-principle for
the next window. The decision is the magistrate's; both campaigns are runnable
tonight either way.

## 3. Model artifact status — FINALIZED

`mlx-community/Qwen2.5-7B-Instruct-4bit` is **present and complete** on the
measurement machine (verified 2026-07-29 by direct listing, not by report):

- Local directory: `/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit`
- `model.safetensors` 4,284,346,255 bytes; `model.safetensors.index.json` present;
  tokenizer, vocab, merges, config all present. Directory total 4.0 GB.
- **Revision pin: `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`** (HF hub `refs/main`,
  resolved at download time 2026-07-29 ~16:30 PT).
- `weight_format`: `mlx`; `family`: `qwen2.5`; `context_window`: 32768.

Arm A is unchanged from window C: `Qwen2.5-1.5B-Instruct-4bit`, revision
`8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, source
`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`.

Two-model load pattern and its consequences:

- A stage is one `run_campaign.py <stage_dir>` invocation, and within a contrast
  stage arms alternate every member, so each member incurs a model load. The
  timing figures in §4 are per-member wall times that already include it.
- The **first in-window 7B load reads ~4 GB from NVMe cold**. It lands inside the
  first B member of the first contrast stage (or of stage `01_phase_decode_absolute`
  under O1). It is inside the member's own settle/warmup structure and is not a
  contamination source, but it is the largest single-member time outlier to expect.
- No network access is required or permitted during the window; the snapshot is
  local and revision-pinned. There is no tooling that verifies the snapshot before
  launch — see the §6 preflight addition.

Disk: **113 GB free** on `/System/Volumes/Data` (verified `df -g`, 2026-07-29).
`WINDOW_STATUS.md`'s "13 GB free" line is stale and should be corrected at
bookkeeping; `RUN_STATE.md`'s 115 GB figure is the current one. Both far exceed the
20 GB threshold in `scripts/prewindow_check.sh:115-123`. The window-C and a10 runs
roots must not be pruned to make room — they are mint #1 inputs.

## 4. Duration arithmetic — measured probe, not model-size inference

`docs/phase_2/window_runbook.md:136-140` forbids estimating member duration from
model size, which is exactly what the checkpoint's ~120-130 s figure did. It is
replaced here by a timing probe run 2026-07-29 outside any window:

| Quantity | Value | Source |
|---|---:|---|
| 1.5B `df_ph_decode` member wall time | 92.7 s | measured, n=40, `runs_window_c_20260726/campaign_log.jsonl` |
| 1.5B `df_rq_mid` reference member | 90.5 s | measured, n=7, same log |
| 1.5B generation time (512 tok) | 2.05 s | probe, 2026-07-29 |
| 7B generation time (512 tok) | 6.40 s | probe, 2026-07-29 |
| **7B `df_ph_decode` member wall time** | **~97 s** | probe + 92.7 s anchor |

The member is overwhelmingly fixed overhead (180 s stage settle amortized, 30 s
idle, 5 s warmup seconds, arm/settle, sampling teardown); the model-dependent term
is warmup + measured generation, and the probe puts the 7B penalty at ~4.35 s per
pass rather than the ~11-15 s the size-based guess assumed.

### O2 — contrast window (`splitwise_decode_v1`, 40 members: 20 A + 20 B)

| Piece | Est. minutes |
|---|---:|
| Pre-calibration (180 s settle + 20 s arm + ~4 min protocol-v3) | ~8 |
| NEG-8 bound corpus, 12 x 90.5 s + settle/arm | ~22 |
| Bound mint | ~1 |
| Start reference triplet, 3 x 90.5 s + settle/arm | ~8 |
| Science stage 1 — blocks 1-5 (10 A x 92.7 s + 10 B x 97 s) + settle/arm | ~35 |
| Midpoint reference, 1 x 90.5 s + settle/arm | ~5 |
| Science stage 2 — blocks 6-10 + settle/arm | ~35 |
| End reference triplet + settle/arm | ~8 |
| Post-calibration | ~8 |
| **Subtotal** | **~130** |
| +20% failure margin (runbook §3) | **~156 min (~2.6 h)** |

### O1 — 7B floor window (`qwen25_7b_decode_floor_v1`, 50 members, all 7B)

| Piece | Est. minutes |
|---|---:|
| Pre-calibration | ~8 |
| NEG-8 bound corpus + settle/arm | ~22 |
| Bound mint | ~1 |
| Start reference triplet | ~8 |
| Stage 01 — absolute, 10 x 97 s + settle/arm | ~20 |
| Stage 02 — null-ABBA blocks 1-5, 20 x 97 s + settle/arm | ~36 |
| Midpoint reference | ~5 |
| Stage 03 — null-ABBA blocks 6-10, 20 x 97 s + settle/arm | ~36 |
| End reference triplet | ~8 |
| Post-calibration | ~8 |
| **Subtotal** | **~152** |
| +20% failure margin | **~182 min (~3.0 h)** |

Sensitivity: if the 7B member is actually 130 s (the checkpoint's discarded upper
guess, +34%), O2 becomes ~169 min (~2.8 h) and O1 ~215 min (~3.6 h). Both remain
inside a 4 h window; O1 has less headroom and is the one to watch. Neither needs an
`n_blocks` reduction. Both are inside the runbook's 2-4 h compact-window target;
O3 is not, which is why it is written as two windows.

## 5. Pre-registration sheet — DRAFT, CONDITIONAL on §2

Recorded now, before any measurement, so that it is pre-registered whichever option
runs. **Conditional**: the decision-interval clause below cannot be evaluated until
the §2 blockers are cleared, and the contrast is therefore registered as
*evidence-bearing now, claim-bearing later*, never as an exploratory contrast
promoted after the fact.

### 5.1 `splitwise_decode_v1` — cross-model decode contrast

- **Directional expectation, stated before data:** decode-phase energy per request
  is **greater** for Qwen2.5-7B-Instruct-4bit than for Qwen2.5-1.5B-Instruct-4bit
  on the identical `df_ph_decode` workload (128 prompt / 512 output tokens).
  Physical basis: 4-bit weights of ~4.0 GB vs ~0.9 GB on a memory-bandwidth-bound
  unified-memory device, at identical token counts.
- **Estimand:** the paired per-block mean difference `B - A` of
  `phase_energy_j.decode`, `difference_orientation:
  condition_b_minus_condition_a`, over 10 blocks.
- **Design:** 10 contiguous A/B/B/A blocks, 40 members, fixed label order, no RNG
  (existing project convention; see §10 Q5). Blocks 1-5 run before the midpoint
  reference and blocks 6-10 after, so the interior reference genuinely divides the
  science — a change from window C, which ran all 40 members in one stage.
- **`minimum_claim_n`: 10 blocks.** A window that collects fewer than 10 valid
  blocks yields no claim; it does not yield a claim at reduced n.
- **Acceptance clause (conditional):** a directional claim is admissible only if
  its decision interval clears the operative decode floor **and** the per-claim
  claim-side anchor bound. Per the D-078 clause 11 ruling of 2026-07-29, these are
  **two gates, not one sum**: the operative floor is the cell gate, the claim-side
  `E_clock_anchor_shift_bound_j` is separately consumed by the claim's decision
  interval, and the additive expression `floor_j + claim_side_bound_j` is a
  **disclosure obligation** that must be stated wherever an attribution-limited
  floor is published — never an acceptance threshold and never a double count.
  For the 1.5B stack the operative floor is **7.377086 J** (cell gate,
  comparative-dominant; absolute component 3.592138 J), artifact
  `df-ph-decode-floor-mint1`. **For the 7B stack no floor exists yet** (§2
  Blocker A); the 7B arm's gate value is unknown and must be minted before this
  clause can be evaluated.
- **Replacement rule:** `technical_invalid_same_slot_only`, pre-declared before
  data, `outcome_dependent_top_up: forbidden_and_demotes_contrast_to_exploratory`.
  A member may be replaced only in its own slot and only for a technical
  invalidity established without looking at its energy value.
- **No outcome-contingent selection anywhere:** no member, block, arm, or stage may
  be added, dropped, reordered, or re-run on the basis of an observed effect;
  no post-hoc block exclusion; no top-up to reach significance.
- **Refusal conditions (any one refuses the claim, not just the member):** whole-window
  verdict not PASSED; calibration bracket drift outside
  `calibration_bracket_max_drift_s = 0.01`; NEG-8 in-window bound not minted inside
  this window before the start triplet; fewer than 10 valid blocks; any arm whose
  members do not share a single scientific config identity and a single stack
  identity; any floor unresolvable for either arm; any evidence-root mapping that is
  not exact (§6).

### 5.2 `qwen25_7b_decode_floor_v1` — 7B decode floor calibration

- **Purpose:** establish the detection floor for `phase_energy_j.decode` on the
  Qwen2.5-7B-Instruct-4bit stack. This is a calibration, not a claim; it registers
  no directional expectation.
- **Design:** one absolute cell (10 repeats) and one comparative null-ABBA cell
  (10 blocks / 40 members), both on the single condition family
  `df-ph-decode-qwen25-7b`, whose definition is byte-identical to
  `configs/floor_mint/condition_family_df_ph_decode.json` apart from the id — same
  workload profile, same measurement target, same two frozen literals.
- **`minimum_claim_n`: 10**, matching the 1.5B floor and exceeding the
  `GUARD_MINIMUM_N = 5` in `joulewise/detection_floor.py:2230-2233`.
- **Same replacement rule and the same no-outcome-contingent-selection clause** as
  §5.1.
- **Known downstream gap, registered now:** the existing mint tool cannot consume
  this evidence without generalization (§2 Blocker A, closing paragraph). The
  evidence is collected against that known gap deliberately, because the collection
  requires a quiet window and the generalization does not.

## 6. Operator checklist delta vs `docs/phase_2/window_runbook.md`

The runbook is unchanged and remains authoritative. These are **additions and
corrections for this campaign only**; none of them relaxes an existing gate.

**D-1. Add the disk/readiness preflight to §5.** `scripts/prewindow_check.sh`
exists and blocks below 20 GB free (`:115-123`), but the runbook never references
it — §5's only free-space language is an eyeball check on the *backup* destination.
Run it before the plan freeze:

```sh
bash scripts/prewindow_check.sh --window <label>
```

Current state: 113 GB free, well clear. Do not prune `runs_window_c_20260726*` or
`runs_window_a10_20260725*` to make room; they are mint #1 inputs.

**D-2. New — two-model snapshot preflight (there is no tooling for this).** Before
the plan freeze, confirm by hand that both model snapshots are present, complete,
and revision-correct, because the window forbids network access and a missing
snapshot fails mid-stage:

```sh
ls -la /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit
ls -la /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit
```

Expect `model.safetensors` at 4,284,346,255 bytes in the 7B directory. Confirm the
revision recorded in §3 matches what the member configs pin. Under O1 every member
is 7B; under O2 both snapshots are load-bearing.

**D-3. New — cold-load expectation.** The first 7B member of the window reads ~4 GB
from NVMe cold. Expect that member's wall time to exceed the ~97 s estimate. It is
not a failure signal on its own; the 20% margin absorbs it. Do not intervene.

**D-4. Timing figures for the budget (replaces the runbook's "do not estimate from
model size" gap with measured input).** Use 92.7 s per 1.5B `df_ph_decode` member,
90.5 s per `df_rq_mid` reference member, and **97 s per 7B `df_ph_decode` member**
(probe-derived, §4). Do not re-derive from parameter counts.

**D-5. Standing — exact evidence-root mappings.** On every claim run, pass exactly
one `--evidence-root ID=PATH` per artifact-declared evidence root and **no surplus
entries**. This holds regardless of FIX-8's status. Surplus entries have twice been
a refusal source (binder exact-cover, then output-separation), and an exact mapping
is the shape both the binders and the separation check agree on.

**D-6. Stage lists.** Under O2, `before_midpoint_stages.txt` contains exactly
`configs/campaigns/splitwise_decode_v1/01_decode_contrast_blocks_01_05` and
`after_midpoint_stages.txt` exactly
`configs/campaigns/splitwise_decode_v1/02_decode_contrast_blocks_06_10`. Under O1,
`before_midpoint_stages.txt` contains
`configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute` then
`configs/campaigns/qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05`,
and `after_midpoint_stages.txt` contains
`configs/campaigns/qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10`.
Never list a reference or bound-corpus directory (runbook §4).

**D-7. Unchanged, stated for completeness.** §5A clock stabilization, the §5B
pre-calibration fiducial screen (`b_fiducial_s <= 0.033558756679900`), the 3+1+3
governed references, the 12-member in-window bound corpus and its same-window mint,
the `quiet_mac_p2_production` policy binding via `--campaign-policy`, `--max-failures 1`,
and the single `caffeinate -is /bin/zsh …/window-chain.zsh` launch all apply
unmodified.

## 7. Validation record (lead-run, 2026-07-29)

All gates run by the lead in the `impl/mint-tool` worktree with
`/Users/edr/code/JouleWise/.venv/bin/python` (this worktree has no `.venv` of its
own — use the measurement checkout's pinned interpreter for the pre-window rerun).

**G-1 `joulewise doctor --campaign --json`, per stage, member configs only.**

| Stage | n | `config` | verdict |
|---|---:|---|---|
| `splitwise_decode_v1/01_decode_contrast_blocks_01_05` | 20 | pass | warn |
| `splitwise_decode_v1/02_decode_contrast_blocks_06_10` | 20 | pass | warn |
| `qwen25_7b_decode_floor_v1/01_phase_decode_absolute` | 10 | pass | warn |
| `qwen25_7b_decode_floor_v1/02_phase_decode_abba_blocks_01_05` | 20 | pass | warn |
| `qwen25_7b_decode_floor_v1/03_phase_decode_abba_blocks_06_10` | 20 | pass | warn |

Zero config errors and zero unacknowledged config warnings on every stage. The
`warn` verdict comes only from `backup_destination` (not configured in a desk
session) and `quiet_machine` (hard-coded `warn` at `joulewise/doctor.py:551`; agent
sessions were open). `powermetrics` passed. Both warns are expected outside a
window and neither is a config property.

**Glob caveat, worth recording for the operator:** a stage `*.json` glob includes
`order_manifest.json`, which doctor tries to parse as a `BenchmarkConfig` and
rejects — producing a spurious `config: fail`. `run_campaign.py` *requires* that
sidecar in the stage directory, so the two tools disagree about the glob, not about
the configs. Always pass member-only globs to doctor.

**G-2 `scripts/run_campaign.py <stage> --dry-run`** (with `--runs-dir` on a scratch
root and `--campaign-policy configs/campaign_policies/quiet_mac_p2_production.json`):
rc=0 on all five stages, emitting 20/20/10/20/20 `dry_run` lines respectively —
matching each stage's member count, in manifest order, first block confirmed as
`b01-a1 → b01-b1 → b01-b2 → b01-a2`. The order-manifest exact-cover and
index-contiguity checks inside `apply_order_manifest` are part of this gate and
passed.

**G-3 `git diff --check`**: clean, rc=0.

**G-4 Per-arm scientific config identity (the constraint that decides usability).**
Computed independently by the lead with
`joulewise.analysis_engine.inputs.scientific_config_identity`:

| Campaign | Arm / family | members | distinct identities |
|---|---|---:|---:|
| `splitwise_decode_v1` | `sw-decode-a-qwen25-1p5b` | 20 | **1** |
| `splitwise_decode_v1` | `sw-decode-b-qwen25-7b` | 20 | **1** |
| `qwen25_7b_decode_floor_v1` | `df-ph-decode-qwen25-7b` | 50 | **1** |

One identity per arm is required — more than one makes the arm unresolvable
(`inputs.py:2851-2857`).

**G-5 Frozen-plan integrity.** Each `calibration_plan.sha256` matches the SHA-256 of
the exact plan bytes, and every member config's `calibration-plan-sha256=` tag
matches its campaign's plan hash (0 mismatches across all 90 members):

- `splitwise_decode_v1`: `7b563724be38254bf0769bca5818e9bcd70f76288e79650b55c3e051bf636b04`
- `qwen25_7b_decode_floor_v1`: `62f7ab3b981ea81f280ee770e932858025b74758bb3dfa5b684bffcbe6a3b388`

**G-6 Condition-family definitions** all return `[]` from
`validate_condition_family_definition`. Domain hashes
(`joulewise.condition_family.v1`), which will appear in any future artifact key:

- `sw-decode-a-qwen25-1p5b`: `c13a3ebf5461ed9a442a8e67555f70301848d56a55ab766570d46ca067934f12`
- `sw-decode-b-qwen25-7b`: `5149a8552600341883439a73fa135caa0e6ba292544c7c6fe2e69674318df4e3`
- `df-ph-decode-qwen25-7b`: `a20018d57f06d69ffcc1…` (full value in the definition's
  consuming spec when one is written)

**G-7 Determinism.** Both generators re-run; the aggregate hash over all 108 files
was byte-identical before and after.

**G-8 Structure.** Root manifests carry 40 and 50 contiguous entries; every ABBA
block in both plans has `executed_labels == ["A","B","B","A"]`, positions
`("A1","B1","B2","A2")`, and `plan_sequence_index` `(1,2,3,4)`. Contrast stages
carry a 10/10 `qwen25-1p5b-mlx` / `qwen25-7b-mlx` split, making the interleave
explicit in the manifest as D-014 requires.

**G-9 Full suite** (`python3 -m unittest discover -s tests`, run by the
implementation session): `Ran 2272 tests … OK (skipped=24)`. These are additive,
untracked config files; no existing test references them.

## 8. Evidence base carried forward from the checkpoint (re-verified)

1. **Structural template:** `configs/campaigns/p2_015_floors/05_phase_decode_abba/`
   — 40 members, 10 contiguous A/B/B/A blocks, fixed label order, no RNG; generated
   by `configs/campaigns/p2_015_floors/generate_configs.py`, which freezes
   `calibration_plan.json` + `.sha256` and per-stage `order_manifest.json`
   (`joulewise.order_manifest.v1`) and stamps `calibration-plan-sha256=<hex>` into
   every member's tags. Window C executed exactly this shape and passed — the first
   comparative window in project history to pass its whole-window verdict.
2. **Workload shape:** `df_ph_decode` = 128 prompt / 512 output tokens,
   `repetitions: 1`, `warmup_runs: 1`; sampling `power_hz 10.0`,
   `idle_seconds 30.0`, `warmup_seconds 5.0`. The 7B profile is identical except the
   `model` block, so the contrast isolates the model.
3. **Calibration scope literal:** `production_window` is a member of
   `_CALIBRATION_SCOPES` (`joulewise/detection_floor.py:93-98` — the checkpoint said
   93-96).
4. **Condition-family convention:** `joulewise.condition_family_definition.v1`, an
   exact key set validated by
   `joulewise/floor_extraction.py:280-393`; `comparison_policy` and
   `abba_alias_relation` are frozen literals.
5. **Window structure:** `docs/phase_2/window_runbook.md` — pre-calibration + §5B
   screen, in-window NEG-8 bound corpus (12) + bound mint, start triplet (3),
   science, midpoint (1), science, end triplet (3), post-calibration.
6. **Measured member timings** — see §4.

## 9. What changed from the checkpoint

- 7B model: was absent, now downloaded, verified, revision-pinned (§3).
- 7B member duration: was an unmeasured ~120-130 s size-based inference, now a
  ~97 s probe-anchored figure (§4); the budget fell from ~2.9 h to ~2.6 h.
- Disk: the "~13 GB free" concern was stale; 113 GB free (§3).
- Condition family: the checkpoint's single working-name family
  `sw-decode-1p5b-vs-7b` is **wrong-shaped** and is replaced by two per-arm families
  (§10 Q2), because the manifest validator requires
  `floor_selector.condition_family_ids == [condition_a_id, condition_b_id]` and the
  engine partitions evidence per family id before deriving each arm's stack identity.
- Claim consumption: newly discovered to be blocked (§2). This is the material
  change and the reason §5 is conditional.

## 10. Open questions for magistrate ratification

**Q1 — Which option runs tonight: O1, O2, O3, or O4 (§2)?** This is the decision
that gates everything else. Lieutenant's advisory: O1.

**Q2 — Ratify the two condition-family ids** `sw-decode-a-qwen25-1p5b` and
`sw-decode-b-qwen25-7b` (contrast), and `df-ph-decode-qwen25-7b` (floor). Family ids
and their definition hashes become part of the pre-registration record and later of
artifact cell keys, so renaming them after collection is expensive.

**Q3 — Ratify the new plan-cell vocabulary** `kind: "comparative_contrast"` with
`null_alias: false` and `condition_family_ids: [a, b]`, deliberately distinct from
p2_015's `comparative_abba`. The calibration-plan document has no validator, so this
carries no code risk, but it is a pre-registration vocabulary that later tooling will
have to honour. Alternative considered and rejected: reuse `comparative_abba`, which
would silently label a genuine contrast with the null-alias kind.

**Q4 — Ratify the two-arm `stack_scope.arms` shape** replacing p2_015's scalar
`model_name` / `model_revision` / `model_source`. Again unvalidated; again
pre-registration vocabulary.

**Q5 — Fixed A/B/B/A for all ten blocks, or alternate A/B/B/A and B/A/A/B?** The
checkpoint specified fixed, per existing convention, and
`joulewise/detection_floor.py:2127-2130` hard-requires `["A","B","B","A"]` for
calibration plans. Within-block ABBA already cancels first-order linear drift. A
genuine cross-model contrast could counterbalance harder by alternating the block
form, at the cost of departing from the validated vocabulary. Lieutenant's advisory:
keep fixed.

**Q6 — `calibration_scope` for both plans is `production_window`.** Note that the
existing mint deliberately splits the two scopes — artifact
`CALIBRATION_SCOPE = "production_window"` but `PLAN_DECLARED_SCOPE = "window_a"`
(`scripts/mint_floor_artifact.py:92-93`). A future 7B mint will need its declared
plan scope decided; ratifying `production_window` here pre-commits it.

**Q7 — Arm-A identity, do NOT adopt without a ruling.** Arm A *could* be gated by
the existing floor's exact-cell path if its member configs reproduced window C's
scientific config identity verbatim — i.e. carried the tags `phase2`, `p2-015`,
`window-a`, `floor-calibration`, `df-condition=df-ph-decode` and the p2_015
`hardware_target.notes` string. Lieutenant's advisory: **reject.** Labelling new
production-window members as "p2-015 window-a floor-calibration" to satisfy a hash
is provenance mislabelling, and it does not rescue the contrast anyway because arm B
still has no floor. Recorded so the option is on the record as considered and
refused, not overlooked.

**Q8 — Confirm the `abba_alias_relation: "A_equals_B"` reading.** The
condition-family schema permits no other value
(`joulewise/floor_extraction.py:372-382`), so each arm's family declares a
null-ABBA alias relation even though this campaign's ABBA is a real contrast. The
reading adopted here is that the field describes how that family behaves in its own
*floor calibration*, not how the campaign uses two families against each other.
Confirm or correct.

**Q9 — Bookkeeping owed.** `WINDOW_STATUS.md`'s stale 13 GB disk line; a decision-log
entry for whichever option Q1 selects; registration of the mint-generalization and
analysis-manifest-extension work items surfaced by §2.
