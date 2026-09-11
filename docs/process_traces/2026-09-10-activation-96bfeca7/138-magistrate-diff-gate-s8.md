# 138 — Magistrate code-reading diff gate (row 7) for PR #316's production diff at ba106c1f (2026-09-10 20:12 PDT)

Read in full: `git diff d18bc2b3..ba106c1f -- scripts/` (371 lines: `write_derivation_night_inputs.py` new 320 lines; the issuer's one-home import; the generator's two hyphenated example filenames + region).

Design judgments:
1. Non-divergence by construction: `_derive_planned_vectors` imports `_sysctl_identity`, `SAMPLING_INTERVAL_MS`, `RESIDUAL_REGION_METHOD`, `PROTOCOL_ID`, `_planned_t1_bindings` from the WRITER's module at call time and builds `planned_epoch`/`planned_t1` in the same shape the writer's `main` builds them; serialization through `generate_g2a_probe_inputs._json_bytes`, the same producer the G2-a inputs use. The refuter (136) is asked to prove the byte equality by execution.
2. The stale-field diagnostic reuses the live preflight (`_derive_preflight_systematic_screen_s`) and reads `stale_fields` from its `acceptance_artifact_epoch_mismatch` refusal — the derivation night's premise is the preflight's own verdict; any OTHER preflight refusal (unreadable artifact) refuses the desk step by name; a mismatch without a field list refuses "rather than guessing". Returning normally = nothing stale = refuse (an ordinary night) — correct: the writer's `--derivation-only` would refuse at d01 with the settle spent.
3. Fail-closed vector checks mirror the reserve step's own (exact field set; no empty/None) so an interpreter without MLX refuses at the desk (`$PY` required — a runbook line, S8's point 5).
4. Files written only after every refusal passed; overwrite refused without `--force` (a wrapper may already pin the bytes); no ledger, no configs/calibration, no powermetrics execution.
5. The one-home import for the ruled floor and the hyphenated example filenames are exactly the two post-merge findings (132 S1; 135 finding 4); no other semantics move.
Row 7 for PR #316: PASS pending the refuter's execution evidence and the runbook promotion (docs).
