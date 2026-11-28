# Stage B cross-family recomputation

**ADMIT** at `e0242030576e41d19e37dcd7e319611ed5ce7050`. All 38 checks in [stage-b-gate.json](stage-b-gate.json) are true. Reviewer: GPT-6.2 Astra. Date: 2026-11-28. This verdict covers the new registration bytes. The deferred native claims and Stage A signature have separate owners.

## Authority and producing seats

The packet is RL-183 §2.7, ledger lines 20265–20272. RL-218 §§7, 10–11, RL-224 and RL-226 govern the later signing chain. Ledger revision `7187d3a9ffcf44cbc46fa21a976399756c38543d`. RS459 and RS640 refer to `RUN_STATE.md` on `origin/main` at `0ebc4a692be88b3a02457fb4fad646c87b3fdd31`. In the tables, `R/` is `configs/campaigns/align_v4/registration/`.

| New bytes | Producing seat and immutable evidence | Check at signing |
|---|---|---|
| `R/r1_slots.json`, `R/r1_planning_release.json`, R1 fills and contrast fields in `R/inputs.json` | Claude Opus lead, RS459 and the co-author trailer on `3712de681`, PR #886. RL-189 §2 covers the release, count backfill and decision. | Source blob, release digest, frozen-source identity, slot bindings, decision, both caps and complete contrast object |
| Five step-1 fills in `R/inputs.json` | Claude Opus lead, `31cc564c5`, PR #973, RL-207 and RL-218 §7 | Historic preimage, delta key set, fan list, R0 and DEC2 |
| `R/w1_plan.json` | Claude Opus lead, `31cc564c5` and `a18d01e64`. The separate member-duration input came from GPT Astra under LR-MS1. | Independent rebuild from the supplied duration file, full validator and complete document equality |
| `R/u3_bar.json` | GPT Sol produced steps 6–8. The Claude Opus lead recorded the draft at `9d1d1113e` and adopted it at `194c35601`. Producer attribution comes from `/Volumes/JW-EXT/scratch/LEAD-PENDING.md:632–633` and the `sol-w1-u3-steps-1128` seat record. | Claude-family Mythos gate carried. Its 28 checks, reviewed tree, draft, adopted derivation and embedded gate binding match |
| `R/wp19_receipt.json` | Claude Opus magistrate, RS638 → RS640. The Sol builder of the PR #981 code and the native receipt producer are different seats. The five public files were committed at `abb9ca25c`. | Receipt validator, seed-binding counts, digest forms, committed source hashes, RS640 hash and membership in `ARTIFACTS` |
| `R/r1_soak_reference.json`, `R/u3_sources/pilot.json`, `R/u3_sources/r1.json`, `docs/align/v4/W1-protected-replays.json` | Claude-family magistrate exports/carry. RS602, RS636, RS638, RS640 and `abb9ca25c` distinguish source production from the final copy. | Hash-only comparison against the individually named committed RS640 references. Exporter, pilot selection and roster also match the step-4 checkout |

## Recomputations

- **Plan.** Ran `scripts/validate_align_v4_w1_plan.py` against the filled plan, with validator stdout captured privately, exit 0. The independent implementation starts with the committed template and rebuilds the ordered member rows from `collection_plan.json` and `member_s.json`. It binds `B_D`, `I_D`, `T_dead`, `effort`, `thermal_policy` and `max_r1_tail_s` from the inputs and slots, sums the duration list, applies the scaffold ceiling and the registered window rounding. It obtains the operator's `plan_id` from the producer commit and `status` from the runbook default. Equality covers every field, its JSON type, array order and all fixed template fields. Sources: `scripts/validate_align_v4_w1_plan.py:66–259`, `docs/run_reports/2026-11-24-w1-step1/w1_step1.py:235–271`.
- **Slots and contrast.** Recomputed the maximum gated tail, the L1 deadline, the step-D budget binding, the combined G0 cap, the contrast episode time, available span, nominal cap, fitted cap and worst time. Replayed the registered `decide` with the planning release and WP18 turn count, compared every leaf including `contrast_fit` as a complete object, then checked the contrast members' installed copies. The slot evidence and budget/policy validators passed. The RS459 close and RL-189 disposition supply source authority for the backfill. They are the boundary for claims about acquisition. Sources: `scripts/align_w1_budget_procedure.py:100–169`, `scripts/align_v4_kit.py:300,633,869,977,1171`.
- **Step 1.** Compared preimage blob `3becfed63` with the signing inputs. Exactly `R0.record_sha256`, `R1.thermal_policy.heavy`, `R1.thermal_policy.per_turn`, `R1.thermal_policy.sensors.fan_keys` and `R1.thermal_policy.sensors.r0_sha256` changed. Independently canonicalized and concatenated the five DEC2 leaves in runbook order and hashed both versions. The R0 hash also agrees with the frozen runtime and RL-218 §7. Sources: step-1 README:40–50 and `w1_step1.py:63–66,187–220`.
- **WP19.** Ran `validate_wp19`. Compared `turns_checked`, `turns_mismatched`, `live_x_turns_compared` and the registered X turn count. Checked `live_source_sha256`, the two named `tokenizer_files_sha256` entries, and all four repository `source_sha256` bindings. The strict artifact declaration includes the receipt. Reproducing native token IDs requires MBP source data and was outside this audit. The gate admits the receipt under LR-WP19-1. Sources: `joulewise/align/apple/v4_registration.py:56,360,1968–2027`, `scripts/align_v4_wp19.py:58`, PR #981 and RS640.
- **U3.** Reused `docs/align/v4/U3-gate.json` from the independent Mythos seat. Its ADMIT names derivation `58d0dbd696de6f58ba9ed9e6c0ac9acde7993c8f92f5c582881cb7df155c5b28`. Checked the adopted bar's embedded copy, path, gate hash, derivation, reviewed tree and the carried draft fields. Step 9 provides the independent numerical recomputation. Sources: `scripts/align_v4_u3_bar.py:50–56`, PR #982 and the committed gate.
- **Soak, exports and replay.** Each file hash matched the path-specific RS640 row, including the separately specified soak digest. These were opaque byte comparisons. The underlying recordings, native tokenizer, protected replays and original soak were outside this audit.

## Hash witnesses

| Source | SHA-256 |
|---|---|
| `/Volumes/JW-EXT/scratch/astra-w1-member-s-1125/member_s.json` | `c8742dfabc3a78b00829673a4456fb70ed1d972ed3763b12067a5ce4dec6f1d4` |
| DEC2 concatenated leaves | `0f80e5939c5496ca4402b397ce6689f55261d5e12c8f91660ea6a0dcf8f83d6a` |
| `R/r1_planning_release.json` | `171b2a3bd28ada24f832e1deafc5d526bd47ff60d55388859220a12ddd5ddf6a` |
| `R/u3_sources/pilot.json` | `104c4621a6c137a9d05db1ded2d26eaed8f0d8eafde027c99a730c0608d559af` |
| `R/u3_sources/r1.json` | `efdcd667bc6604383ce02e6ff88ad0c717d43128318c9806a3d71f688d9cee43` |
| `R/r1_soak_reference.json` | `5a2dd40030a9008c59c1d89c29a6e7f0a230bcffa7ff5500a5f5897e0508b1b7` |
| `docs/align/v4/W1-protected-replays.json` | `c806e72f6e9a50d049b1a05f367e1229a80942eec42f538b75c9785ee8084820` |
| `R/wp19_receipt.json` | `4d7b5dd184883a0faeca809cc1f27bfc01edef294ed0055c3a0c09d21c39116b` |

The [audit implementation](tmp/recompute.py) runs from the signing checkout with `taskpolicy -c utility python3.13 -B`. It writes only the gate to scratch. Receipt installation is lead-owned. `validate_receipt` requires distinct A and B ADMIT references with tracked paths under `docs/align/v4/` and matching SHA-256 at the receipt's commit (`joulewise/align/apple/v4_registration.py:1786–1832`).
