# 08 — Magistrate record: review and fix rounds of lane QPE01-NONOBSERVER-PREDICATE-01 (activation 7a0f14bd, 2026-09-23)

Written by the magistrate (Fable 5.1) at the bench. Every number below was executed by the magistrate this activation unless a record is cited.

## 1. What was reviewed

The seat landing at `16900e3d` on branch `feat/2026-09-23-qpe01-registration-v3-nonobserver` (brief 04; the seat was killed at 01:20 before writing its report). Two same-packet contract lenses, read-only, same brief: Opus 5.5 (record 06, ten minutes) and Fable 5.1 (record 07, forty-five minutes). Both: MERGEABLE AFTER FIXES, no blocker. Same-packet score recorded in the model-allocation memory: Opus 5.5 found the material defect (S1 below); Fable found four independent nits (canonical form, C3 text, the vacuous 02:17 byte-equality branch, the missing observer-marked guard).

## 2. Ruling on lens finding S1 (the load recorder is outside the whole-envelope figure)

Verified at the bench: `whole_envelope_observer_cpu_s` is the collector's RUSAGE_SELF + RUSAGE_CHILDREN (`scripts/sample_quiet_predicate_evidence.py`, `cpu_total`, line 1164); the 30 s load recorder is launched by the executor (`joulewise/quiet_predicate_campaign.py`, `launch("recorder", …)`) as a sibling of the collector and journals its own CPU per row. So ruling 31's `definition` sentence ("SELF + all reaped CHILDREN, including collector, power recorder, load recorder and census") is inaccurate for the load-recorder term, and the interim's component formula `power_recorder_residue = whole − round_block − load_recorder` subtracted a term the total never held.

Ruling (least amendment, no ruled string changed): the four ruled strings (`statistic`, `definition`, `limitation_sentence`, `supersedes`) stay byte-for-byte; `observer_floor_cores` stays Σ whole / Σ span (0.176 / 0.159); the residue becomes whole − round_block; the load recorder is reported beside the whole with an explicit `inside_whole: false`; a companion `observer_floor_including_load_recorder_cores` = (Σ whole + Σ load recorder) / Σ span is REPORTED and never a stop input; the registration's `components` text (magistrate-authored interim text, not ruled) is corrected and the v3 digest re-pinned. The inaccuracy in the ruled `definition` sentence is carried to the block-two consult (directive #386 released that consult), not patched. Why not amend the ruled sentence here: this is the fourth false observer-accounting premise in the same gate (rounds 1–3 each turned on one); amending ruled text is the consult's act, and the material effect is 0.007 cores ≈ 1 J per interior, at the instrument's attribution limit, with the stop firing either way.

Re-derived by the magistrate from the archive bytes with the branch code (v2 retention rules): 02:17 floor 0.17572, companion 0.18297, variation 0.00214, mean shares round block 0.0525 / residue 0.1233 / load recorder 0.0073; 21:00 floor 0.15909, companion 0.16624, variation 0.00267, shares 0.0521 / 0.107 / 0.0071. Dated correction addenda written on both harvest records.

## 3. Fix round 1 (Opus 5.5 seat, sixteen items F1–F16, `16900e3d..0e5578fb`)

Brief items and dispositions are in the seat report (`05-nonobserver-predicate-seat/00-seat-report.md`, §2, §4b, §6). Magistrate additions beyond the lenses: F10 (the abort's cause text names the successor Ed's D-182 addendum licenses, lane A270); F12 (eighteen arm-check tests were spending the production 30 s sampler — watched as `top -l 2 -s 30` children of the test run; the arm check is scoped to evidence chains like t0); F16 (Fable N8 adopted as an evidence-quality guard: an unmarked journal refuses by name instead of blaming the power sampler).

Ratified here, as the fix brief and the lenses asked:
- Three files outside brief 04's WRITE_SCOPE (`joulewise/arm_retry.py`, `docs/phase_2/derivation_night_runbook.md`, `tests/test_arm_retry.py`): mechanically forced by the reason-code registry test once the ruled reason was registered; content correct; the seat should have returned NEEDS_SCOPE; granted retroactively.
- `observer_floor.supersedes` says 0.176 / 0.159 where ruling 31's field text says 0.178 / 0.161: ruling 31's numbers are its own rejected round-support denominators; the statistic it ruled gives 0.176 / 0.159 and its §2 addendum text, brief 04 and main `90c30e4f` all say so. The seat's choice stands.
- `non_observer_process_busy.bar_basis` reworded to 0.3194 W / ≈7.7 J: synthesis 25 withdrew 0.3125 W everywhere; the parenthetical is the seat's and is accepted.

## 4. Delta re-audit (Opus 5.5, record 09) and the same-signature judgment

Delta verdict: MERGEABLE AFTER FIXES; nine of ten mutation probes killed; three SHOULD-FIX (D1 in-chain marking guard so a marking failure never carries the daemon abort's typed reason, D2 the marked-copy archive test for ruling 10 regression 1, D3 a floor-below / companion-above fixture so "never a stop input" is guarded) and one nit (N-b skipped rows listed as failed). D3 recurs the round-0 class "a test that passes without the property it claims" in a new, lower-stakes instance (an auxiliary assertion on a reported-only field whose code path is one visible line).

Magistrate judgment on the standing escalation trigger (rule 11: two consecutive rounds failing with the same signature → consult, not round three): the round-0 instance was a brief-mandated regression proving nothing, cured and mutation-killed in round 1; the round-1 instance is a new auxiliary assertion introduced by the cure. The defect set shrank from seventeen items to three under executed mutation evidence, which is the shape Ed's stop-conditions ruling calls a converging design, not a spiral. Round 2 is therefore a bounded bench-sized cure (D1–D3, N-b) by a seat under an exact brief, followed by a magistrate bench verification, not a consult. Dissent recorded: the delta lens itself left the call to the magistrate; if round 2 surfaces a further instance of the same class, the next spend is a consult.

## 5. Open items carried forward
- Ruled `definition` sentence inaccuracy → block-two consult (directive #386).
- Lens N9 (no single end-to-end regression-0 test), N10 (30 s cost in the driver's bind loop; the executor/summary verdict race is now visible as a disagreement flag but nothing acts on it), Fable N2 (registration `ruling` string vs table entry string), Fable N7 (campaign test module has no production-sampler guard).
- A270 precondition: the in-chain guard (D1) must be on main before A270 licenses any successor on the abort reason.
