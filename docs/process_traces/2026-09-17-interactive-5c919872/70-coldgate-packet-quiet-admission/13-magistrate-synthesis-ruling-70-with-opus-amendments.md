# Magistrate synthesis of cold-gate ruling 70 with the Opus pairing refuter's amendments (interactive session 5c919872, 2026-09-17 ~20:5x PDT)

Inputs: `10-coldgate-fable-ruling.md` (cold Fable judge, sha256 b5c08240…), `12-opus-pairing-refuter-on-ruling-70.md` (Opus, contract lens, formed by re-reading every cited line), exhibits A–G. The magistrate decides where the two disagree and records dissent; nothing here amends a rule.

## Verdicts in force, per question

| Q | In force | Source | Binding consequence for NIGHT-GATE-QUIET-ADMISSION-01 |
|---|---|---|---|
| Q1 | AFFIRM | ruling §3, confirmed | first sample AT t0; wait is plan data in a NEW plan; the GO receipt must state that admission evidence is not capture evidence (a required receipt field plus a contract-doc sentence) |
| Q2 | AFFIRM (contingent on Q4) | ruling §4, confirmed | consecutive-count stays plan data |
| Q3 | AFFIRM, conditional | ruling §5; refuter: within charter | the load veto is removed only in a v4 plan whose interval-CPU cutoff has been affirmed by a later gate; load stays a diagnostic on every sample and receipt; v2 semantics untouched |
| Q4 | REFUSE | ruling §6; all four joule figures re-derived by the refuter | no cutoff value may be activated; mechanism may land with the value as plan data and no admitting default; the cure is the joule campaign in lane QUIET-PREDICATE-EVIDENCE-01 (kernel 232), scoped by ruling §6 items 1–4 with the slot budget corrected to 480 s |
| Q5 | AFFIRM, conditional | ruling §7; refuter: the 0.217 cpu-s round excluded the census probe | the observer floor (0.0072 core per 30 s) is provisional; the seat's live sampler smoke must include the census probe in the measured cost; no cutoff derivation may quote the floor until re-measured with the census included (folded into lane 232) |
| Q6 | AFFIRM | ruling §8; refuter: the per-sample fresh-census condition exceeds the proposition | the magistrate ADOPTS fresh census on every sample as a mechanism choice (it is what the brief's D3 already specifies and what D-181's "census at t0" implies for a t0 that is now an interval); recorded as the magistrate's choice, not a ruled requirement |
| Q7 | AFFIRM | ruling §9, arithmetic confirmed | generator validates `window_max_s ≥ bind_max_s + post_bind_budget_s` and `post_bind_budget_s ≥ 7980` from the constants |
| Q8 | AFFIRM as design | ruling §10, schema ids confirmed unoccupied | binds the seat to regression 7 (byte-identical v2, no default insertion) |
| Q9 | REJECT → superseded | ruling §11 rested on exhibit E, which omitted the 2026-09-16 amendment (lane record 06 lines 44–61) where Ed had already ruled part (b); refuter: should have been REFUSE under charter §4 | the packet defect is the magistrate's; recorded in D-182's provenance paragraph. Ed re-affirmed the consolidated rule on 2026-09-17 ("affirm of course"), extended to bind-window expiry; PR #357 records it as D-182. Stage D7 of the seat may land only after #357 merges |
| Q10 | four items named | ruling §12; refuter refutes item 3's reasoning | item 1 (0.05 placeholder) accepted: no candidate value in generated plans, fixtures or docs; item 2 (D7) accepted, gated on #357; item 3: reusing `night_refused_not_quiet` classifies identically under `arm_retry.DISPOSITIONS` (refuter, `arm_retry.py:74-79,90`), so a distinct code is NOT required by contract — the magistrate still chooses a distinct code `night_refused_bind_expired` as a mechanism choice (the published description string at `:31` is what changes, and a refusal that waited ten minutes is not the same event as a one-shot refusal); item 4 (R1 text) accepted, gated on #357 |

## Corrections to the brief (exhibit G) the seat must apply

1. A capture slot's budget is 480 s (`scripts/gen_derivation_night.py:88`), not 60 s; every joule sentence in the contract doc uses 480 s and the ≈1 J / ≈5 J bars from D-078 cl.11.
2. No candidate cutoff anywhere: the `--quiet-admission-json` input carries the value; fixtures used for plan validation carry `busy_core_max: 0.0` (admits nothing); tests of the GO path inject their own values inside the test; the contract doc names no number and says the value awaits lane 232 and a gate.
3. A required non-empty `cutoff_authority` string in `quiet_admission` (the record path of the gate that affirmed the value); validation refuses an empty string; test fixtures use the literal `TEST-ONLY-NOT-A-RULING`.
4. Bind-window expiry refuses with the distinct code `night_refused_bind_expired`, registered in `NIGHT_DRIVER_REASON_CODES` and in `arm_retry.COLD_GATE_CODES` (same class as `night_refused_not_quiet`; no new remedy text).
5. Receipt v3 carries `admission_is_capture_evidence: false` and the contract doc states in one sentence why (reservation then a 600 s settle follow GO).
6. Stage D7 (successor route, R1 sentence, `COLD_GATE_CODES` description) is HELD on the branch until PR #357 (D-182) merges; the seat implements it behind that gate as its own final commit so it can be dropped or kept without touching D1–D6.
7. The live sampler smoke measures the sampler's own cost WITH the census probe included and reports it.

## Dissent recorded

None between the magistrate and the refuter. The judge's Q9 verdict is not overruled; it is superseded by evidence the judge was not shown, and by Ed's re-affirmation.

## Lessons for the packet assembler (the magistrate owns them)

- An excerpt of a record must run to the record's end or state what follows; a lane record's "awaiting ruling" status can be amended below it.
- Every claim in a brief that carries a number (the 60 s slot) gets the same first-use verification as a code citation.
