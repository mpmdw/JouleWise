# 20 — Bounded post-seal round (charter §5): does the bench replay meet the ruled arm precondition?

Assembled for the magistrate (activation 59857fe5), 2026-09-22. Sealed files untouched. ONE question set for a fresh cold Fable judge; the ruling lands as file 21. Trigger: the driver will report **FAIL** on the full replay for a reason the ruled precondition never names. Charter §9: construes §Q7 and the lane's driver convention only.

## Facts

**Ruled — read F1–F3 verbatim before ruling.** §Q7 rejected arming until a daytime bench replay "shows chain-level `start_drift_s` ≤ 0.5 s on **every** slot", recorded as a tracked artifact (**P7.1**: merged sha, plist sha256, twelve chain-level values, the max, the statement `max ≤ 0.5 s`) and linked from the arm notice (P7.2/P7.3). **§Q7 names no other per-slot condition.** A269 §Q3 originates the clause; its amendment **A1** moved a DIFFERENT bar — R6's 2 s — to the session-level figure.

**Added by the lead, not by any ruling (F5–F7).** The driver also requires per slot exit 0, `cleanup_proven`, `anchor_status == "bounded"` and `interior_complete_support` (**X2**), dictated in record 16 — which lens 19b warned was "unproven satisfiable".

**Executed — attempt 2, slots 1–8 at 19:16 PDT** (attempt 1 aborted at slot 3 on the feeder causality defect, cured by PR #382, main `4f8bc36d`). All eight: exit 0, cleanup proven, an attestation that ran. Slot 1: chain 0.352 s / session 0.608 s, anchor `unknown` / `wall_minus_monotonic_span_exceeded`. Slot 2: anchor `bounded`, interior support true, chain 0.150 s / session 0.404 s, feeder jitter 0.084/0.242/0.356 s (min/median/max) against an archived cadence ≈ 0.26 s — the SAME jitter as slot 1.

**A hypothesis the lead advanced and attempt 2 REFUTED:** that feeder re-pacing trips the 15 ms backstop on every slot, making `bounded` unreachable in replay. Slot 2 disproves it — same jitter, anchor resolved. The archive's own v3.1 classes (F9, at `447fd6bf`): bounded {02, 05, 06, 08, 09, 11, 12}; unresolved {01, 03, 04, 10} (a real slew) and {07} (the backstop).

**Fidelity so far: 7 of 8 match, one MISMATCH.** 01 unresolved, 02 bounded, 03 unresolved, 04 unresolved, 05 bounded, 06 bounded, 07 unresolved — each matching its archived class. **Envelope 08 does not:** replay `unknown` / `affine_clock_residual_exceeded` against an archived class of `bounded`. 08 is the marginal envelope — unresolved under the night's recorded v3.0 status, bounded only under v3.1's rate-aware caps, and the archive's largest tail at 2.291 s. The replay's clock relation — archived labels against live pacing and live stamps — can push a marginal fit over the residual cap. The mismatch is in the REFUSING direction: the replay refused what the archive resolved.

**Chain drift is empirically independent of the anchor class.** Slots 2–8 read 0.150, 0.150, 0.150, 0.150, 0.149, 0.150, 0.150 s — identical to 3 dp whether the anchor resolved and the full tail ran (02, 05, 06: derive, integrate, reduce interior) or it did not (03, 04, 07, 08); slot 1's 0.352 s is first-spawn cost. The skipped tail, measured on the archived night itself at **0.011–2.291 s** (F8) against a 20 s gap and replay tails ≈ 6 s, cannot move the ruled quantity at this margin — executed, not budgeted.

**Assembler's corrections** (detail in F5/F8): X1/X2 live in record 16, not brief 10; the 0–2.3 s tail is not confined to fit-completing slots (envelope 08, unresolved in the recorded column, spent the largest); attempt 1 mismatched archived envelope 02 where attempt 2 matches it, so any fidelity test below is one the pre-fix run fails.

## Q1 — Which figure does the ruled precondition bind?

Options. (a) CHAIN-level, per P7.1's words ("the twelve `start_drift_s` values … (chain-level)"). (b) SESSION-level, on the ground that A1 governs every start-drift bar in the lane. (c) Both.

Lead's disposition (argument, not evidence): (a). P7.1 names chain-level twice; A1 by its own text amends "the 2 s bar of R6", not the 0.5 s bench bar. The session figure is reported beside it; slot 1's 0.608 s excess is a named finding for the night's 2 s abort rule, which it passes with 1.4 s of margin.

Deliver: which figure the bench bar binds, and what an excess of the other means.

## Q2 — What anchor condition makes a slot admissible for the drift bar?

The ruled bar names chain-level start drift and nothing else. X2 demands `bounded` on every slot, which the archive itself fails on five of twelve. What X2 was FOR is proof the finalisation tail actually ran (17b B2, F6).

Options.

**(a) Archived-class fidelity.** Admissible when the anchor status matches the archived v3.1 CLASS for that envelope (`anchor_detail` may differ) AND exit 0, cleanup proven, an attestation that ran, AND chain drift ≤ 0.5 s. On the executed rows this FAILS at envelope 08.

**(b) Every slot `bounded`** — X2 as written. Unattainable by construction: a faithful replay must reproduce the archive's five unresolved envelopes, and one returning `bounded` on all twelve would evidence a recorder NOT reproducing it.

**(c) Chain drift alone**, with no anchor check.

**(d) Fidelity table with direction-asymmetric tolerance.** Admissible when the twelve chain-level drifts meet the bar AND the artifact prints the fidelity table with its tally, tolerating mismatches ONLY in the REFUSING direction — the replay refuses what the archive resolved. Such a slot's tail is SHORTER, by at most the archive's measured 0–2.3 s derive/integrate cost, and the drift is empirically class-independent (§Facts), so the skipped work cannot carry a slot across 0.5 s. A mismatch in the ADMITTING direction — the replay resolving what the archive refused — is recorder infidelity and VOIDS the run.

Lead's disposition (argument, not evidence): **(d)**, with **(a) recorded as the ideal** the judge may prefer. (d) is (a) plus a rule for the case (a) did not anticipate: given envelope 08's marginality (§Facts), demanding that the replay reproduce v3.1's verdict on it asks the replay to be as certain as a rate-aware re-derivation of stamps it does not have.

Deliver: the ruled admissibility rule for THIS artifact; whether the refusing/admitting asymmetry is sound; and the exact text the artifact must carry.

## Q3 — May the arm proceed on the raw rows when the driver reads FAIL?

Conditional on Q2(a) or (d). The driver FAILs for the archived-unresolved slots failing X2's `bounded` requirement. The artifact would carry the twelve raw rows, the fidelity table and tally, the driver's `status` and `statement` verbatim, and this ruling's name.

Lead's disposition: yes. The artifact IS the run at the merged head P7.1 requires; X2 is the lead's own addition, written before any full replay existed, and this ruling records why it does not bear on the ruled bar. The driver is amended in its own PR.

Deliver: AFFIRM or the extra condition; and whether the driver amendment must land before the arm or may follow.

## Q4 — Are the twelve chain-level drifts themselves ≤ 0.5 s on every slot?

Answer from exhibit E's `chain_drift_s` column, or `python3` over `24-bench-replay.json` yourself — never from the magistrate's prose. If exhibit E's ATTEMPT 2 section is still unfilled, say so and rule Q1–Q3 on the rule alone.

Deliver: max chain drift, any slots over 0.5 s, and whether P7.1's `max ≤ 0.5 s` is true of the rows. State the fidelity tally and the DIRECTION of any mismatch separately, since Q2(d) turns on it.

## Exhibits and constraints

`exhibit-E-replay-rows.md` — rows from `exhibit-E-generator.py` here; its `archived_v3.1_class` / `fidelity` columns come from a constant in the generator, not the run. `exhibit-F-authorities.md` — F1–F9, verbatim, file:line at `4f8bc36d`.

Read-only; nothing armed; no `sudo`, `systemsetup`, `powermetrics` or real `log`; do not run the bench and read nothing under `/Users/edr/night-bench` (a replay is in flight). Probes: `git show 4f8bc36d:<path>`, `grep`, `sed -n`, `python3` over the exhibits' JSON. Under 8 KB. Tier BLOCKER / MATERIAL / NIT; per question say AFFIRM, amend or REJECT.
