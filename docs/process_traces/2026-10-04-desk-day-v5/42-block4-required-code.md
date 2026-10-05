# Record 42: block-4 code map

2026-10-05, desk-day seat 2 (Opus 5.5). Replaces the 2026-10-04 drafting map, which planned a separate rehearsal
night (`r1`) that ruling 76 removed. This record says which code each block-4 predicate needs, where it lives, and
which gates it must pass. The code is on branch `feat/2026-10-05-v5-qualification-code`.

## Gates for this code

All of it can change which windows are admitted or how evidence is judged, so it is full tier: an independent
executing review, the whole suite on the merged tree, CI green on the final head, a cold Fable final pass, and every
finding dispositioned (doctrine gate 1). The registration itself is sealed by a cold Fable judge and an independent
Opus refuter at the integrated head, with the real rendered plans.

## Already merged (part of H)

| Need | Where | PR |
|---|---|---|
| Prefill length from the issued pin; acceptance in force | the three `_v5` generators | #472, #473, #476 |
| G2-b stops by itself after one block | `scripts/run_campaign.py --max-blocks`, `scripts/gen_g2_phase_d.py` | #474 |
| Launch-realization recheck; `launch.pending` custody | `scripts/launch_window.py`, `scripts/run_night.py` | #475 |
| Issued pin and generated packs | `configs/campaigns/d117_contrast_v5/prefill_pin/`, the three pack trees | #477 |
| Network time stays OFF in freeze and ARM evidence | `joulewise/arm_readiness_evidence.py`, live v2 registry | #479 |

## Block-4 qualification code (integration branch)

| Predicate (registration §) | Code |
|---|---|
| `s1` and `s2` plans, sizing, deadlines, latest start (§4, §8) | `scripts/write_v5_qualification_plan.py`, `joulewise/night_plan_writer.py`, `joulewise/night_gate.py`; allowances in `configs/campaigns/v5_qualification_25g83/sizing_allowances.json` |
| `a1`, `a2` arm-only controls and their expiry proof (§4, §6) | `scripts/run_night.py` (ARM-only entry, returns before GO), `scripts/check_v5_arm_abort.py` |
| Observation producers for G1, G3, G8, G9 on `s1` (§6) | `scripts/run_night.py` (spawn and wait seams), `scripts/produce_t0_rehearsal_bundle.py` |
| G9 backups, close-out and restore after STOP (§4, §6, addendum A) | `scripts/v5_s1_desk_closeout.py` |
| G1 registered outcomes; eight-gate evaluation; G6/G7 NOT_APPLICABLE (§6, §14) | `joulewise/t0_rehearsal.py`, `scripts/rehearse_t0_unattended.py` |
| Qualification verdict (§7) | `scripts/harvest_v5_qualification.py`, `joulewise/v5_qualification.py` |
| Structural G2-b verdict, L10-A, `recover_no_science`, blindness (§6, §7, §10) | `scripts/harvest_v5_g2b_window.py`, `joulewise/v5_qualification.py`; recipe `docs/process/v5-l10-rehearsal-phase.md` §L10-A |
| Courier excludes raw chain logs for non-claim purposes (§10) | `scripts/run_night.py` |
| G10 physical control (§5) | `scripts/ed_session/capture_t0_anchor_positive_control.py`, recipe 46 |

## Records still to produce before seal

- Record 44, sizing, with the allowances' sources and the clock design check (addendum A).
- Record 46, the G10 recipe.
- The arm recipes for `a1`, `a2` and `s1` (plan rendering, notice, install, stand-down, harvest, desk step).
- The head and custody bindings: final H, the three pack and freeze identities, policy, acceptance, ledger seed,
  backup destinations, roots.
- The seal record, after the cold pair.
