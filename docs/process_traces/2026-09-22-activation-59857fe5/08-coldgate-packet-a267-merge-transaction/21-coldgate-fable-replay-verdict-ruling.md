# 21 — Cold Fable ruling, bounded post-seal round: replay verdict (charge 20)

Judge: Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-59857fe5-r3` at `c90e8c5d`, 2026-09-22 19:51–19:57 PDT, foreground only, no subagents, nothing armed.

**Disclosure.** Auto-loaded before the merits: `~/.claude/CLAUDE.md`, project `CLAUDE.md`, memory index `MEMORY.md` (index lines only; no memory, state or narrative file opened). Read set: charter, charge 20, ruling 10 §Q7, synthesis 15 (Q7 row), exhibits E/F, artifact 24 + `24-bench-replay.json`, the A269 packet files cited by F2/F3/F8, `scripts/bench_replay_start_drift.py` via `git show 4f8bc36d:`.

**Trust anchors (shasum -a 256, observed = expected):** charter `099de884…c95d81`; charge `57211e70…8114fc`; exhibit E `a4a8dd5a…689009`. All match.

**Authorities verified** with `git show 4f8bc36d:<path> | sed -n`: F1 (ruling 10:90), F2 (A269 ruling 10:35), F3 (:17), F5 (record 16:34-35), F7 (19b:109-113), F8 (A269 exhibit C:30-41; `end-postparse` min 0.011 / max 2.291 s), F9 (A269 record 01:29). Driver at `4f8bc36d`: `START_DRIFT_BAR_S = 0.5` (:88), `SESSION_BAR_S = 0.5` (:93), `ADMISSIBLE_SLOT` requires `anchor_status == "bounded"` and `interior_complete_support` (:301), `verdict()` :323-371: defects → FAIL, else session-over → ESCALATE, else PASS. Every quotation in exhibit F is exact.

## Q4 first — computed by me from `24-bench-replay.json` (python3, not prose)

- 12 of 12 slots; head `4f8bc36d`, clean tree, transaction merge `7eb53eff` is ancestor.
- Chain-level `start_drift_s`: 0.352, 0.150, 0.150, 0.150, 0.150, 0.149, 0.150, 0.150, 0.150, 0.150, 0.150, 0.150 s. **Max 0.352 s (slot 1). Slots over 0.5 s: none. P7.1's `max ≤ 0.5 s` is TRUE of the rows.**
- Session-level: max 0.608 s (slot 1); slots 2–12 span 0.399–0.411 s. Only slot 1 exceeds 0.5 s; none approaches the night's 2 s rule.
- Every slot: `collector_exit 0`, `cleanup_proven True`, attestation `authenticated` or `slew_attested`. Twelve per-slot `source_plist_sha256` present (P7.1's plist digest, satisfied per envelope).
- Fidelity vs the archived v3.1 class (F9 constant): **10/12 match; mismatches 08 and 09, BOTH in the REFUSING direction** (replay `unknown` / `affine_clock_residual_exceeded`, archive `bounded`). Admitting-direction mismatches: **zero** (01, 03, 04, 07, 10 all `unknown`, as archived).
- My own probe: against the night's RECORDED column (F8 C2: bounded {02,05,06,11,12}) the replay is **12/12**. The two mismatches are exactly the two envelopes whose `bounded` exists only under v3.1's re-derivation.
- `tail_s`: bounded slots 6.9–8.4 s, unresolved slots 5.4–5.6 s; max 8.410 s (slot 11) + F8's 2.291 s worst skipped tail = 10.7 s < 20 s gap. Slot 12, which follows the longest tail, reads 0.150 s.

Charge §Facts ("7 of 8, one mismatch") is stale by slot 9; exhibit E's filled section discloses it and slots 1–8 there are unchanged from §Facts. Same direction, so no question changes.

## Q1 — AFFIRM (a): the bench bar binds the CHAIN-level figure

Deciding text: F1 says "(chain-level)" for the twelve values, and F2's single clause carries three bars at two levels; A1 (F3) amends only "the 2 s bar of R6". No ruling puts 0.5 s on the session figure. `SESSION_BAR_S = 0.5` (driver :93, from brief D8) is the lead's convention. What the session excess means: nothing against the ruled bench bar; it is reported and assessed against the only ruled session bar, 2 s (A1) — slot 1's 0.608 s passes with 1.39 s margin. MATERIAL (M1): with X2 amended, this same JSON would exit ESCALATE rc 3 on X1 (driver :368). The artifact must dispose of that explicitly (text below), not leave it to the exit code.

## Q2 — AFFIRM (d), amended; (a) REJECTED as the rule; (b) and (c) REJECTED

(b) demands an outcome the archive never had (five unresolved of twelve, F9) — a 12/12 `bounded` replay would evidence infidelity. (c) drops the one thing X2 was for (17b B2: proof the tail ran). (a) fails on 08/09, whose class is a re-derivation the replay does not perform. The asymmetry is sound: a refusing-direction slot does LESS tail work, bounded by F8's 2.291 s, inside a 20 s gap with the longest measured tail at 8.4 s; it cannot lift a successor across 0.5 s, and the rows show it (class-independent 0.150 s). An admitting-direction slot means the recorder produced a resolution the archive lacks — infidelity — and voids the run. Two amendments so (d) cannot degenerate: a floor of at least one `bounded` slot (the tail proven to run at the merged head; here five), and the executed tail-plus-skip budget stated.

**Admissibility rule — exact text the artifact must carry:**

> Admissibility (cold ruling 21, 2026-09-22). This artifact meets ruling 10 §Q7 / P7.1 when ALL hold: (1) 12 of 12 slots recorded at the merged head; (2) every slot `collector_exit == 0`, `cleanup_proven == True`, `attestation_state ∈ {authenticated, slew_attested}`; (3) every chain-level `start_drift_s` ≤ 0.5 s, and `max ≤ 0.5 s` is stated; (4) the fidelity table against the archived v3.1 class {02,05,06,08,09,11,12} is printed with its tally; no slot resolves (`bounded`) where the archive did not — one such slot VOIDS the run; slots refusing where the archive resolved are admissible; (5) at least one slot is `bounded` with `interior_complete_support == True`; (6) max `tail_s` + 2.3 s (F8 worst skipped tail) < the 20 s gap, stated with the figures. Session-level `start_drift_s` is reported per slot and assessed only against the night's 2 s rule (A269 A1); the driver's 0.5 s session bar and its `bounded`-on-every-slot requirement are lead conventions, not ruled bars. Driver output: status FAIL, statement quoted verbatim above, retained as issued.

On these rows: (1)–(6) all hold (12/12; 0.352 s; 10/12, zero admitting; five bounded; 10.7 s < 20 s).

## Q3 — AFFIRM: the arm may proceed on the raw rows, with three conditions

The driver's status line is a lead-authored bench convention (record 16, F5), not a governed verdict; reading the rows against §Q7 is application, not reinterpretation. Conditions: (C1) artifact 24 gains a tracked addendum (or the arm notice quotes it) carrying the rule text above, the fidelity table and tally, the driver's `status`/`statement` verbatim and unrelabelled, slot 1's session 0.608 s with its 2 s margin, and this file's path; (C2) the arm notice links artifact 24 + `24-bench-replay.json` + this ruling (P7.2), and states the merge sha for P7.3; (C3) the driver amendment (fidelity rule replacing X2; session bar reported at 2 s, not 0.5 s) MAY follow the arm, but MUST land before any later replay artifact is offered, and its PR must show `verdict()` re-run on this very JSON producing PASS — no bench run needed. The night's own 2 s abort rule stays live and is the sequential second bar (ruling 10 §Q7).

## Hygiene, tiers, §9

Hygiene PASS: exhibits verbatim, contrary run (attempt 1) included, argument labelled; one stale count (M2). **BLOCKER:** none. **MATERIAL:** M1 X1/ESCALATE undisposed; M2 charge §Facts stale on slot 9 (direction unchanged); M3 driver amendment sequencing (C3). **NIT:** exhibit E keeps the "(empty — paste…)" line above the pasted output; replay session-minus-chain offset ≈ 0.25 s vs ≈ 0.12–0.16 s archived (feeder spawn; report only); artifact 24's "retried on a census-clean machine" clause is not triggered.

Charter §9: no prior verdict is reinterpreted. Ruling 10 §Q7 and A269 §Q3/A1 are applied as issued; the driver's FAIL is not a governed verdict and remains in the record verbatim. Attempts 1 and 2 fail with different signatures (feeder causality vs admissibility convention), so no structural-failure rule is engaged.
