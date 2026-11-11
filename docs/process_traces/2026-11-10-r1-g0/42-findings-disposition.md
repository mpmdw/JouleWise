# Disposition of review findings, R1 G0 build (lead, magistrate 5515349e), 2026-11-10

Reviews of `ad9c0667f`, run blind and executing: Fable cold pass
ADMIT_WITH_FIXES (`40-cold-fable.md`) and Opus 5.5 cold pass ADMIT
(`41-cold-opus.md`). Both reproduced the following:
- the recorded 600 s timeout;
- R_op = 26.571250 / 34.106462 C;
- no release within the recorded 600 s;
- releases inside 1,200 s for tail models A-D (706-940 s);
- a hot-start refusal on R0 0550Z;
- bounds of 5,763.9952 s, 5,528.9952 s and 109,627 s.

| Finding | Disposition |
|---|---|
| Fable F1: a step_30b redo captures R_op on a still-cooling machine | Fixed as a flag, not a refusal. Runbook §4 now says a night whose accepted step_30b attempt is above 0 goes to the ruling seat before any R_op-gated number is used. Both facts are already in `r1_result.json`. |
| Fable F2: model D's production release is 941 s, not 911 s | Fixed. The S6 receipt text cites both values (1.25 x 941 = 1,176 s, still within 1,200). S6 stays 1.5 C. Expected step-30b release on the next record: about 707-966 s. |
| Fable F3 / Opus flag 1: `thermal_gates.md` says G1/H use R_op | Fixed (G1/H keep the G0-release reference). |
| Opus flag 2: S7 now derives from R_op + S6 | Recorded. This follows ruling decision 3 (one reference after step-30b). Recovery is censored at 600 s on the production-shaped tail, so S7 = 300 s either way. |
| Opus flag 3: the synthetic world has R_op equal to the soak | Deferred to the R1 tests follow-up (tests tier). Both reviewers closed it by execution with a shifted R_op. |
| Opus flag 4: d-4bit is missing from the arm floor | Deferred. It is latent: `d_4bit_source` is null, so R1 does not run d-4bit, and the base floor never included it either. |
| Fable observation 1: the 600 s release between A-B-A legs may leave adoption inconclusive | Deferred to the ruling seat after the next record. The runbook tells the desk to read those releases first. Nothing is refused. |
| CI `quick`: `test_s0_blocked_enumeration`, `hazards.test_physics_coverage` | Pre-existing: they fail identically at base `20e9edbc4` (lead re-ran both trees). Not in this diff, and they touch no R1 number. |
| Fable's 12 failures in `test_v4_w1_plan` / `test_v4_prequal` | Pre-existing or unrelated (10 identical at base; 2 depend on files outside this diff). They belong to the W1 lane before W1 registers. |
