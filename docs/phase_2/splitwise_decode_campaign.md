# Splitwise-vein decode contrast campaign (splitwise_decode_v1) — WIP CHECKPOINT

**STATUS: CHECKPOINT ONLY — NOT A FROZEN PLAN. NOT RATIFIED. DO NOT RUN A
WINDOW FROM THIS DOCUMENT.**

Checkpoint written 2026-07-29 under an imminent harness restart, so the
successor session can resume without re-deriving the evidence base. The
authoring task (Ed-directed, 24h deadline) is the first claim-bearing
comparative campaign: decode-phase energy contrast, Qwen2.5-1.5B-Instruct-4bit
(arm A) vs Qwen2.5-7B-Instruct-4bit (arm B), one quiet window under
`configs/campaign_policies/quiet_mac_p2_production.json`, consumed into claims
against the Ed-ratified operative decode floor **7.377086 J** (cell gate;
claim-side anchor bound adds on top per D-078 clause 11 single-count
discipline — never double-counted, never zero).

## CHECKPOINT — session state at restart

- **No Sol/Codex session was in flight.** Nothing to harvest or relaunch;
  no `.codex-bridge` run id exists for this stream.
- **No configs authored yet.** `configs/campaigns/splitwise_decode_v1/` does
  not exist yet. All deliverables below remain outstanding.
- **Research/evidence phase is complete** and recorded in this file. The
  successor should author directly from the facts below (verify, don't trust).

### Model artifact status (deliverable 3) — ACTION NEEDED BEFORE WINDOW

`mlx-community/Qwen2.5-7B-Instruct-4bit` is **NOT present locally**:

- `/Users/edr/jw_models/mlx-community/` contains only: Qwen2.5-0.5B-Instruct-4bit,
  Qwen2.5-1.5B-Instruct-4bit, Qwen3-4B-4bit, Qwen3.5-122B-A10B-4bit.
- HF hub cache (`~/.cache/huggingface/hub`) has no Qwen2.5-7B entry.

Download (BEFORE the quiet window — network during collection is
contamination; ~4.3 GB, and WINDOW_STATUS reported only ~13 GB free on the
measurement machine, so check disk first):

```sh
hf download mlx-community/Qwen2.5-7B-Instruct-4bit \
  --local-dir /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit
```

Then pin the revision exactly as the 1.5B configs do (the 1.5B pin is
`revision: 8b403126fc14f14cfc99bb4cfa72ecbc129ea677` — a git commit hash of
the HF repo). Capture the resolved commit for the 7B snapshot (e.g. from
`hf download`'s output or `~/.cache/huggingface` snapshot dirname if cache
layout is used) and write it into the generator's `MODEL_B["revision"]`
before generating configs. The frozen plan's `stack_scope` must carry both
models' name/revision/source.

## Evidence base gathered (verified against primary artifacts this session)

1. **Structural template**: `configs/campaigns/p2_015_floors/05_phase_decode_abba/`
   (40 members, 10 contiguous A/B/B/A blocks, fixed label order — no RNG in
   the existing generator convention), generated deterministically by
   `configs/campaigns/p2_015_floors/generate_configs.py` which also freezes
   `calibration_plan.json` (schema
   `joulewise.detection_floor_calibration_plan.v1`) + `calibration_plan.sha256`
   and per-stage `order_manifest.json`
   (schema `joulewise.order_manifest.v1`); every member config carries
   `calibration-plan-sha256=<hex>` in its tags. Window C executed exactly this
   shape and passed (first comparative window to pass whole-window verdict).
2. **Workload shape to match**: `df_ph_decode` = 128 prompt / 512 output
   tokens, repetitions 1, warmup_runs 1; sampling `power_hz 10.0`,
   `idle_seconds 30.0`, `warmup_seconds 5.0`. The 7B profile must be
   IDENTICAL except `model` block, so the contrast isolates the model.
3. **Calibration scope literal**: `production_window` is a legal member of
   `_CALIBRATION_SCOPES` in `joulewise/detection_floor.py` (lines 93-96) on
   this branch — use `calibration_scope: "production_window"`.
4. **Condition family**: name the contrast family distinct from
   `df-ph-decode` (working name `sw-decode-1p5b-vs-7b`). Condition-family
   definition v1 convention lives at
   `configs/floor_mint/condition_family_df_ph_decode.json` (W4/W5 commit
   24db8e1) — model the new family definition on it.
5. **Window structure**: `docs/phase_2/window_runbook.md` — pre-calibration +
   D-079 §5B screen, in-window NEG-8 bound corpus (12 members) + bound mint,
   start triplet (3), science stages, midpoint (1), end triplet (3),
   post-calibration; policy `quiet_mac_p2_production.json`; references and
   bound corpus stay on the 1.5B `df_rq_mid` configs (unchanged from window C).
6. **Measured member timings (window C log,
   `runs_window_c_20260726/campaign_log.jsonl`)**:
   - `df-ph-decode` on 1.5B: n=40, mean 92.7 s, min 90.4, max 133.2 (single
     133 s outlier at b06-b1; modal ~91-92 s).
   - `df-rq-mid` references: n=7, mean 90.5 s.
   - Window C ran all 40 decode members as ONE stage between start triplet
     and midpoint (midpoint after science, then end triplet). For the new
     campaign, split blocks 1-5 / 6-10 across the midpoint for a true
     interior reference.

### Duration arithmetic (deliverable 4, draft — successor must re-verify)

Per-member 7B estimate: member wall time is dominated by fixed overhead
(30 s idle + settle + sampling); the model-dependent part is warmup + measured
decode of 512 tokens and model load. 1.5B decodes 512 tokens in roughly 3-4 s
per pass; 7B int4 on M3 Max decodes at roughly 3-4.5x fewer tok/s
(memory-bandwidth-bound, ~4.2 GB vs ~0.9 GB weights), i.e. ~11-15 s per pass,
x2 passes (warmup + measured) ≈ +18-25 s, plus ~5-10 s extra model load
≈ **~120-130 s per 7B member (estimate, NOT measured — no local 7B evidence
exists; flag to magistrate)**.

Budget at 10 blocks (40 members: 20xA @ ~93 s, 20xB @ ~130 s est):

| Piece | Est. minutes |
|---|---:|
| Pre-cal (settle 180 + arm + ~4 min) | ~8 |
| NEG-8 bound corpus 12 x ~91 s + settle/arm | ~22 |
| Bound mint | ~1 |
| Start triplet 3 x ~91 s + settle/arm | ~9 |
| Science stage 1 (blocks 1-5: 10A+10B) + settle/arm | ~41 |
| Midpoint 1 x ~91 s + settle/arm | ~6 |
| Science stage 2 (blocks 6-10) + settle/arm | ~41 |
| End triplet + settle/arm | ~9 |
| Post-cal | ~8 |
| Subtotal | ~145 |
| +20% failure margin (runbook §3) | **~174 (~2.9 h)** |

**Fits a 3.5-4 h window at n_blocks=10 with margin** even if the 7B member
estimate is off by +50% (subtotal then ~166 min, +20% ≈ 3.3 h). No n_blocks
reduction needed on current arithmetic.

## Outstanding deliverables (all of them — none authored yet)

1. `configs/campaigns/splitwise_decode_v1/`: deterministic
   `generate_configs.py` (model on p2_015_floors generator), 7B workload
   profile matching `df_ph_decode` exactly, ABBA order manifest (A=1.5B,
   B=7B, 10 blocks / 40 members, fixed A/B/B/A per existing convention),
   frozen `calibration_plan.json` with `calibration_scope:
   "production_window"`, condition family `sw-decode-1p5b-vs-7b`, plan
   sha256 pinned, policy binding `quiet_mac_p2_production`.
2. Pre-registration sheet in this doc: directional expectation (7B decode >
   1.5B decode), paired-block contrast claim shape, decision interval must
   clear 7.377086 J operative floor + claim-side anchor bound (D-078 cl.11),
   `minimum_claim_n: 10` blocks, refusal conditions, no outcome-contingent
   selection anywhere (replacement rule
   `technical_invalid_same_slot_only`, top-up forbidden).
3. Model artifact section: finalize after download; pin revision hash.
4. Operator checklist delta vs runbook (two-model load pattern, disk
   preflight, 7B runtime estimate is unmeasured — consider one non-claim
   dry-run timing probe OUTSIDE the window to firm it up before freezing).
5. Validation: `.venv/bin/python -m joulewise doctor --campaign --json <all
   new configs>`; `scripts/run_campaign.py <stage> --dry-run` per stage;
   `git diff --check` clean.

Frozen plan + pre-registration are subject to magistrate ratification before
the window — deliver, don't self-ratify.
