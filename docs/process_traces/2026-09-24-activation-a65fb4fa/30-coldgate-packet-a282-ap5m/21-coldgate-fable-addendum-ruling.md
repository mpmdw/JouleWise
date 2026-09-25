# 21 — Cold Fable addendum ruling: A282-AP5M-01, refuter objections R1–R17 to texts T-1..T-23

Judge: Claude Fable 5.1, fresh session, no loop context, 2026-09-24 02:14–02:22 PDT, worktree HEAD b627bbb8. Foreground only; no subagents or background tasks. Read: charter, the addendum charge, `00-charge.md` (headings, §Q9, E1–E4), ruling 30/10, refuter 30/11, and exhibits V2, G45A, DF, IMP, C, S19, R20, G21, G21R. Nothing outside the packet directory was opened.

## 0. Disclosure, anchors, method

**Auto-loaded before I could refuse:** `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md` and the memory index `MEMORY.md` arrived as system context. None was used; no memory file, CLAUDE.local.md, RUN_STATE, TASK_QUEUE, council log or run report was opened.

**Digests.** Method: `python3 scripts/validate_gate_packet.py` (receipt schema `coldgate-validator-receipt/v2`), then independent `shasum -a 256`.

| Item | Expected | Observed | Result |
|---|---|---|---|
| Charter, run 1 (deliberate typo) | `099de884…c95d82` | `099de884…c95d81` | REFUSE, `charter_trusted_observed_mismatch`, rc=2 |
| Charter, run 2 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same (validator and shasum) | PASS |
| Packet `20-charge-addendum.md` | `11ad0d761af11888db83761436df3a311122ec9b5bdb12241880e712c4d6adbf` | same (validator and shasum) | PASS |
| Exhibits | 28 manifest rows | 28 observed = expected, rc=0 | PASS |

**Executed this session.** (1) IMP `canonical_reference_v1` and `plain_comma_ambiguous` (IMP 108–139, 192–196) on `1\;000`, `1\:000`, `1~000`, `1\ 000`, `1 000`, `1{,}000`, `1,\!000`, `1\,000`: all 1000, not plain-comma; `1,000` is plain-comma (excluded). (2) R2 arithmetic (separation 20, P = 16, budget 235.5 J): 0.5 J gives δ = 0.025, max_gap = 588.75; 0 J divides by zero; +7.38 J gives δ = 0.394, max_gap = 37.4.

**Packet hygiene.** Complete and neutral for A1–A18; both sealed outputs present verbatim; no defect found.

**Standard.** 30/10 and 30/11 are argument; each objection was checked against its exhibit. Verdicts: AFFIRM (30/10 text stands), ACCEPT (refuter's replacement, as given or as tightened), TEXT (mine), NEW RULE (no source; text for Ed's adoption), ED (reserved). Severity is of the defect in the round-1 T-n.

## 1. Rulings A1–A18

**A1 (R1) — ACCEPT, tightened. BLOCKER → T-3 (replaced).** Deciding exhibits: V2 §2.6 (397–413), P3 with four problems at ≈ 200 s worst case each, predicted 250 s; G45A §7 (W) reserves the whole-block retry at `min(Σ item derived worst cases, capacity)`. T-3 G3's per-problem formula fails every ordinary multi-problem block; the bound is the sum over the block's problems. A block cut off by its envelope's end is a K13 overrun, not a G3 failure.

**A2 (R2) — ACCEPT. MATERIAL → T-10.** A two-point difference can be zero or below instrument resolution; executed above. The block-window `floor_gate_j` (T-6) is the smallest difference the instrument distinguishes from zero, so adding it to the observed difference is the minimal noise allowance that keeps δ_upper a bound. NIT: "binding" is overstated (37 slots exceeds a night); a loose `max_gap` under a truly small δ_upper is correct. Also cured in T-10 (A18-a): "the larger model's" was ambiguous; it becomes "the larger of the two models' values".

**A3 (R3) — ACCEPT. MATERIAL → T-10.** V2 §2.3 (273–276) shows cells from about 2,000 J to 60,000 J; one budget cannot be about one percent of every cell. Budget and threshold are per (arm, level), scaled to the registered n.

**A4 (R4) — ACCEPT both parts. MATERIAL → T-9 (K22), T-12.** T-13 restarts indices per night, so a recapture night holding one model's parents has no lever, and a single linear function across nights assumes a shared intercept the shakedown never measures.

**A5 (R5) — ACCEPT. MATERIAL → T-8, T-11.** V2 §2.2 orders Holm at step 10 and status flags at step 12; K15 (V2 715) already names `unattributed_overrun` as a spread cause; T-13 adds `night_exhausted`; T-6 adds `below_floor`. Every status fixed before testing leaves the sort; m stays 5.

**A6 (R6) — ACCEPT. MATERIAL → T-14.** K17 (V2 726) keeps a terminal window out of every cell sum; `unattributed_overrun`, `night_exhausted` and `below_floor` do the same for their windows, so "exactly one counted attempt" is false for those problems. The pair drops from both models' sums and counts and the level is NR (NE for `ceiling_violation`) until recapture; no claim rests on the dropped pair, so M12's prohibition is not engaged.

**A7 (R7) — ACCEPT. MATERIAL → T-15.** R20 Q5(c) (line 71): "The output flags that the registered `s_per_token_upper` was false for that arm" at the violation, not at the recapture; G21R R6 licenses one recapture after it. T-15 set the flag late and left S8's legality under a falsified bound unsaid.

**A8 (R8) — ACCEPT; Ed adopts (E2). MATERIAL → new T-24.** C §3 (125–128), carried VERBATIM as K2 (V2 494–498), says the pilot "may set only (a)…(c)"; V2 126–127 says the pilot and shakedown "set only the quantities K2 lists". T-10 sets δ_upper and `budget_j` from the shakedown; T-3 re-derives `s_per_token_upper`; R20 Q4 (line 66) puts `s_per_token_upper`, `prefill_s` and `ceiling_s` in Registration with no named source. Extending K2 amends C §3 text, so it is claim policy under E2 like T-1; the D-062 line is preserved.

**A9 (R9) — ACCEPT. MATERIAL → T-3, T-10; NIT → T-20.** M13 (S19 line 23; V2 550) "one thinking arm per night"; S19 line 42 sequences one "shakedown night" then "headline nights". One night can gate only one arm, and AP 270 requires a passing gate before any scored campaign; so one shakedown night per arm, each arm's δ_upper, `budget_j` and G3 check from its own. O-18's figures gain one shakedown night per arm.

**A10 (R10) — ACCEPT. MATERIAL → T-5 (K11), §2.5 relabel.** DF 914–918: `energy_bound_terms_j.E_clock_anchor_shift_bound_j` is a per-wire reducer field, REQUIRED, refusing `anchor_energy_envelope_unrecorded` when absent. So `anchor_j` is per window; the bound sums over counted windows and `k` disappears.

**A11 (R11) — ACCEPT. MATERIAL → new T-25.** V2 568–570 "The operative guard is AP-5's, carried unchanged"; 583 "carried for the gate as a proposed change, not as operative text"; step 6 (V2 237) "The guard's exact reading is O-2"; K19 (V2 733) "(reading O-2)". T-1 and T-2 edit none of these.

**A12 (R12) — ACCEPT. MATERIAL → T-3 G2.** V2 step 1 (232): "malformed := incorrect (K3)": an outcome, not a stop reason. G2 now names stop reasons only, with the literals `eos` and `length` (V2 232).

**A13 (R13) — NEW RULE (text supplied; binds the code lane only through that lane's own gate). MATERIAL → new T-26.** G45A §7 (G) closed edge list has no edge to `night_exhausted` and none to a recapture; (E) requires every retry "at an index above the reporting envelope's"; (S) checks stage legality against (G). T-13 and K22 as written are refused by `_seal`. AP-5M records the amendment so registration and code do not diverge (G21 §Q4); ratifying it for the code lane is a process rule (charter §3 item 4) for that lane's gate, not this one.

**A14 (R14) — ACCEPT. NIT → T-20, T-9 (K22).** V2 100: "In this file 'window' alone always means a block window." T-20 and K22 broke it; cured.

**A15 (R15) — ACCEPT, tightened. NIT → T-7.** "Linear interpolation between order statistics" names a family (Hyndman–Fan types 4–9), not one rule; undefined replicates (V2 187–189: both draws zero correct) have no defined sort position. Type 7 is named; an undefined replicate sorts below every finite value on the low side and above every finite value on the high side, matching how `p_below` and `p_above` (V2 190–192) already count it on both sides.

**A16 (R16) — ACCEPT, extended. NIT → T-21.** Executed above: `\;`, `\:`, `\ `, `~` and plain whitespace (IMP 118–119 `"".join(s.split())`) are all removed; `{,}` is normalised to `,` (IMP 127) and then parsed by `_GROUPED`. The refuter's list omitted plain whitespace; added.

**A17 (R17) — ACCEPT (i), (ii), (iii); ACCEPT (iv) as disclosure with one reservation. NIT → T-27, T-4, T-28, T-6.** (ii) verified at DF 107: `floor_cmp_j = max(max_i|δ_i|, |mean δ| + t_0.975 · s_δ · √(1 + 1/n))`. (iv) is true at block scale (a ~7 J floor against thousands of joules per window). Reservation (MATERIAL, ED): DF 160–166 makes claim acceptance `|estimate| > F` plus zero-exclusion. 30/10 Q3 (standing) made the floor a per-window gate; whether AP-5M must also register an estimate-level floor check is claim policy the charge did not ask. T-6 discloses it as new open item O-21.

**A18 — further findings.** (a) MATERIAL: T-10 "the larger model's" (cured in T-10). (b) NIT: the §2.5 and §2.6 worked examples carry `k·(floor_j + anchor_j)`; T-5's relabel now names the replacement expression. (c) NIT: T-3 G2 now names the `stop_reason` literals. (d) NIT: T-12 now states that the slope bound holds per night with a per-night intercept, so T-13's per-night lever and T-12 agree. (e) NIT: `max_envelopes_per_night` and the per-(arm, level) `budget_j`/`max_gap` join O-14's registration list (in T-20). No further defect found in T-1, T-2, T-16–T-19, T-22, T-23; they stand.

**Disagreements with 30/10:** T-3, T-5, T-7 to T-15, T-20, T-21 superseded; T-4, T-6 amended. No 30/10 verdict is reversed.

## 2. Severity roll-up

BLOCKER: A1. MATERIAL: A2–A13, A18-a, A17 reservation (Ed). NIT: A14–A17 (i)–(iv), A18-b..e. Ed decides E1–E4 and adopts AP-5M; T-24, T-25 and T-26 are text for adoption, not policy.

## 3. Final texts (paste verbatim into v3; supersede the named T-n)

Texts not listed here (T-1, T-2, T-16, T-17, T-18, T-19, T-22, T-23) stand as in 30/10 §3.

**T-3 (supersedes 30/10 T-3) — replaces V2 K21 (745–753); the row's "Inclusion/exclusion" field points to K21; the D-166 addendum carries this clause as the decision-log entry changing the smoke thresholds.**
**K21 — pre-campaign smoke gate.** AP-5 requires an envelope-validation smoke gate that passes before any scored campaign (`analysis_plans.md:270`). AP-5's defined checks were written for a ladder whose prompts differ by one digit; for MATH, emitted-token mean and distribution and prompt-token count change with level by design, so those checks are not pass conditions here. The AP-5M smoke gate is one shakedown night per arm (M4, M13); each arm's scored campaign waits for its own pass. An arm's gate PASSES only when all of the following hold on every envelope of its shakedown night: (G1) every bundle is strict-valid; (G2) every attempt's `stop_reason` is `eos` (end-of-sequence token) or `length` (cap), `capped := generated_tokens ≥ cap_tokens[arm]` agrees with `stop_reason` on every row, and no attempt ends by runtime error, by kill at `ceiling_s`, or with a missing or unrecognised `stop_reason`; a malformed answer is an outcome (K3), counted incorrect, and does not fail the gate; (G3) every completed block's markers lie inside its envelope's usable interior, and no block's elapsed seconds exceed the sum, over its problems, of `cap_tokens[arm] × s_per_token_upper + prefill_s`. Reported per (model, level) with no pass threshold: emitted-token mean and distribution, prompt-token count, cap-hit fraction beside the registered `cap_bound_fraction` (0.20), and the early-stop-bias descriptor (mean emitted tokens of incorrect minus correct attempts; AP-5's E5). A failed gate records `smoke_failed([reasons])`; no scored campaign starts for that arm; the cause is cured and recorded and that arm's shakedown repeated; no registered value beyond those K2 as extended (T-24) lets the pilot and shakedown set changes on its account. A G3 failure falsifies `s_per_token_upper` for that arm; it is re-derived before any repeat.

**T-4 (amends 30/10 T-4) — in the clause "(i) The *floor*", replace the `floor_cmp_j` definition with:**
`floor_cmp_j` is `max(max_i |δ_i|, |mean δ| + t_0.975 · s_δ · √(1 + 1/n))` over same-condition A-B-B-A contrast deltas δ_i (`detection_floor.md`, "Estimator rule").

**T-5 (supersedes 30/10 T-5) — procedure (V2 §2.2): step 2 last two sentences; steps 7 and 8 bound expressions; K11; the §2.5 worked replicate and §2.6 instrument-bound lines.**
Step 2: "Refuse any block window at or below `floor_gate_j` for the block-window class (row, Floor gate); the refusal is `below_floor`, the window is not counted, and its problems follow the counted-attempt rule (K24)." Step 7: "point bounds with U = Σ over the group's parents of Σ_w anchor_{j,w} per model (K11)". Step 8: "add bound u = s · Σ_w anchor_{j,w}". K11: "u = s · Σ_w anchor_{j,w}, summed over the parent's counted windows w for that model, where anchor_{j,w} is window w's reducer field `energy_bound_terms_j.E_clock_anchor_shift_bound_j`; a counted window without a bounded value is refused (`anchor_energy_envelope_unrecorded`). Point bounds use s = 1. This departs from gate 21 D5a's bracket `k·(floor_j + anchor_j)` because D-078 clause 11 and `detection_floor.md` assign the floor to a separate gate and record the anchor bound per window; D5a's per-replicate share-scaled structure is kept." In §2.5 and §2.6 replace every `k * (floor_j + anchor_j)` and "`floor_j + anchor_j` = 2 J" with "Σ_w anchor_{j,w} = 2 J (illustrative; one window per parent)"; the numbers are unchanged.

**T-6 (supersedes 30/10 T-6) — row field "Floor gate".**
Every counted block window must exceed `floor_gate_j = max(floor_abs_j, floor_cmp_j)` from the P2-015 calibration manifest row for this backend, gross energy, the block-window class and the scored-campaign condition family, issued and hashed before registration seals; a block window at or below it is refused (`below_floor`) and never counted. The floor never enters the interval; the anchor bound never gates a window. At block scale (thousands of joules per window against a floor of order 10 J) this gate is expected never to bind; it is a refusal check, not a claim margin. Whether AP-5M must also register an estimate-level floor check (`detection_floor.md` single-count discipline, `|estimate| > F`) on the J/correct difference is open item O-21 for Ed (E2); until adopted, claim acceptance is Holm plus zero-exclusion by the anchor-widened interval (S2).

**T-7 (supersedes 30/10 T-7) — replaces V2 191–192 and step 11; K10 589–593 stand with "proposed text pending O-4" removed; replaces V2 594–595.**
"The *interval* runs from the 2.5th percentile of the replicate low-side ratios to the 97.5th percentile of the replicate high-side ratios (K11); its ends are `lo` and `hi`. The point bounds (s = 1) are reported beside it as `point_low` and `point_high` and do not alter `lo` or `hi`." Lines 594–595: "Replicates use Python's `random.Random(seed)` with the seed fixed in the registration packet; each draw is `randrange`, in the order parent then problem. Percentiles are Hyndman–Fan type 7 (h = (B − 1)·p on the 0-based sorted values; numpy's default). An undefined replicate (both models' draws zero correct) is never dropped: it sorts below every finite value on the low side and above every finite value on the high side; an end that interpolates with an infinite value is that infinity. All of this is registered so the interval can be rebuilt exactly."

**T-8 (supersedes 30/10 T-8) — replaces V2 step 10 (252–256).**
10. **Holm**, m = 5 fixed, over the tested groups. A group is *tested* when it is estimable and no constituent level carries `ceiling_violation`, `spread_exceeded`, `drift_exceeded`, `unattributed_overrun`, `night_exhausted` or `below_floor`; all of these are determined before this step. Untested groups have their p-values computed and reported but excluded from the sort, and m stays 5. (A flag-forced level cannot change status whatever its p-value; leaving it in the sort could only loosen the thresholds for the others.)

**T-9 (supersedes 30/10 T-9) — replaces V2 223–224; the second part is new clause K22, flagged at step 4.**
- **spread_exceeded, drift_exceeded.** Flags that a cell lost its minimum spread after capture, or that a level's executed drift lever exceeded `max_gap`. Either flag on any constituent makes the whole group NR with that reason and `flagged_levels` listing the constituents; the group's numbers are still printed. **K22 — flag recapture bound.** For each (arm, level) at most one registered recapture may cure `spread_exceeded`, `drift_exceeded`, `unattributed_overrun` or `night_exhausted`, all causes together. It runs on a later census-clean night as a new roster linked by `recapture_of`: for every *affected* parent, both models' copies are re-run with the same problems, packed to lever 0 within that night; the recaptured copies supersede both models' earlier windows of that parent. A parent is affected when it is missing a counted window for either model, or (for `drift_exceeded`) when it holds a retried or rescheduled window. If the level still carries any of these flags afterwards, it is NR terminal under this registration. This bound is separate from S8's one recapture of a ceiling-violating problem.

**T-10 (supersedes 30/10 T-10) — replaces the drift-threshold sentences of V2 167–174 (with T-12) and the O-7 item; K12 carries the same sentences.**
The *drift threshold* is `max_gap = budget_j / (δ_upper · P)`, registered per (arm, level), with P the number of parent blocks per cell per model (the registered n ÷ problems per block). `δ_upper` (joules per block per slot) is registered per arm from that arm's shakedown night: each model runs one fixed block of pilot problems twice, in its first and last envelopes of that night; for each model compute `(|E_last − E_first| + floor_gate_j) ÷ (slot separation)` with the block-window `floor_gate_j` of T-6, and δ_upper is the larger of the two models' values; a shakedown lacking either pair refuses registration. `budget_j` for (arm, level) is 0.01 × the smaller of the two models' projected energies for that cell at the registered n, where a model's projection is its mean pilot generated tokens per problem at that level × n × its shakedown seconds per token × its mean shakedown power; so the admitted bias moves that level's R_L by at most about one percent. δ_upper, every `budget_j` and every `max_gap` are hashed in the registration packet before any test problem runs.

**T-11 (supersedes 30/10 T-11) — replaces V2 step 12 (259–260); K16 carries the same rule.**
12. **Group status** by the three-way test (S2); then flags, in this precedence: NE(`ceiling_violation`) first; otherwise NR listing every applicable reason in the order `spread_exceeded`, `drift_exceeded`, `unattributed_overrun`, `night_exhausted`, `below_floor`; every applicable flag is recorded true whatever the printed status.

**T-12 (supersedes 30/10 T-12) — replaces V2 170–174 from "If a block's energy shifts".**
The registered drift model is: within a night, gross block energy drifts linearly in envelope index with one slope, of magnitude at most δ_upper joules per block per slot, shared by both models; each night has its own intercept, and balance within every night is what cancels it. Under that model a level's between-model bias within a night is at most δ_upper × P × lever, and lever 0 cancels the drift exactly. For any other drift shape this rule bounds nothing; it is the registered tolerance, not a proof. `max_gap` is defined in K12; the packer aims for lever 0 and a roster is accepted if lever ≤ `max_gap`.

**T-13 (supersedes 30/10 T-13) — insert after V2 line 103 (Night) and as clause K23, flagged at step 5.**
Retries and reschedules extend the same night: a "fresh envelope" is appended to that night's schedule up to the registered `max_envelopes_per_night`. Any block unfinished when the night ends is the terminal refusal `night_exhausted` (a `terminal_refusals` entry); its cell is unresolved until the K22 recapture. Envelope indices start at 0 in every night, including a recapture night. A level's drift lever is computed within each night over that night's counted windows of both models, and the level's lever is the largest of its nights' levers; a night holding counted windows of only one model for a level has no lever and is a K22 defect (`recapture_unpaired`).

**T-14 (supersedes 30/10 T-14) — insert after V2 line 153, as clause K24.**
- **Counted attempt (K24).** For every problem and model at most one attempt is *counted*: the one whose window is counted. Its correct flag and generated tokens are the problem's values in every computation. Every superseded attempt's answer and tokens are recorded and never used. When a superseded and a counted attempt of one problem disagree in correctness, `attempt_divergence` is recorded for disclosure (expected never under greedy decoding, possible under seeded sampling). A problem with no counted attempt for either model (terminal `ceiling_violation`, `unattributed_overrun`, `night_exhausted`, or a `below_floor` refusal) contributes to neither model's energy nor correct count nor n for that cell; its level carries that reason and is NR under step 12 (NE if `ceiling_violation`) until the K22 or S8 recapture; the cell's printed numbers state how many problems were dropped and why.

**T-15 (supersedes 30/10 T-15) — replaces V2 894–895.**
The first ceiling violation sets `s_per_token_upper_falsified: true` for the arm. S8's single recapture is the only run allowed under it. If, during that recapture, the recaptured single or any other block of the night for that arm exceeds `s_per_token_upper`, `crossover_level` stays null with reason `ceiling_violation_unresolved`, terminal under this registration; the arm's results still print with the flag; a further recapture requires a new registration.

**T-20 (supersedes 30/10 T-20) — V2 502–504 and 1177–1179; same unit wherever the mechanical n rule is explained; O-14's list.**
The "registered window budget" is a number of nights (the sources call a night a "capture window"; in this file "window" alone still means a block window); the value is fixed in the registration packet (O-14). O-14's list also carries `max_envelopes_per_night` and the per-(arm, level) `budget_j` and `max_gap`. O-18: "planning figures (record 18) are about 12 nights for n = 64 and about 23 for n = 128, plus one shakedown night per arm, at 4–5 nights a day."

**T-21 (supersedes 30/10 T-21) — replaces V2 477–480 from "parses as".**
parses as an integer, a decimal, a grouped integer (thousands separated by `{,}` or `,\!`, or by whitespace or a TeX space `\,`, `\;`, `\:`, `\ ` or `~`, all of which the importer removes or normalises before parsing), a/b, or `\frac{a}{b}`: `5`, `-\frac{3}{4}`, `0.25`, `10\%` and `1{,}000` qualify; `\sqrt{2}`, `3\pi` and `(1,2)` do not. A reference containing a bare comma, such as `1,000`, is a *plain-comma* reference and is excluded, because a bare comma could separate thousands or list two answers.

**T-24 (new) — insert after K2's C §3 carry (V2 498); Ed adopts under E2.**
For AP-5M the sizing pilot and shakedown also set `s_per_token_upper` and `prefill_s` (per model and arm), `ceiling_s`, δ_upper, every `budget_j` and every `max_gap` (K12, K21); none of them decides which levels, models, arms, families or estimands are reported (D-062). This extends C §3's list (a)–(c) for this plan and is part of what Ed adopts.

**T-25 (new) — K9 lead-in (V2 568–570), step 6 (V2 237), K19 (V2 733), §2.10 (V2 759–761).**
K9 lead-in: "The guard is T-1's observed count (at least 3 correct per model per level or group); AP-5M replaces AP-5's 'binomial lower-bound' wording (`analysis_plans.md:274`), subject to Ed's adoption under E2." C's "Minimum correct and merge order" carry becomes operative text; delete "carried for the gate as a proposed change, not as operative text". Step 6: delete "*The guard's exact reading is O-2.*" K19: replace "(reading O-2)" with "(T-1, observed count)". §2.10: replace "C's observed count guard is carried as a proposed change (K9, O-2)" with "C's observed count guard is operative (K9, T-1)" and delete "the AP-5 guard is restored as operative (K9)".

**T-26 (new) — insert as clause K25; a consumer-lane amendment recorded here, binding the code lane only once ratified through that lane's gate.**
**K25 — required amendment to 45/21 §7 for the code lane.** (G)'s closed edge list adds: any non-terminal stage → `night_exhausted` (terminal); and, for a parent affected under K22 or an item under S8, terminal-or-flagged → `recapture`. A recapture is a new roster sealed under the same registration, linked by `recapture_of` (the superseded roster's `sha256`), with envelope indices from 0; (E)'s "index above the reporting envelope's" applies within a night; (S)'s item conservation treats a recaptured item as superseding its earlier block and windows. `max_envelopes_per_night` is a registration field, hashed with the others. Until the code lane's gate ratifies this text, `_seal` refuses these paths and no K22 or S8 recapture roster can be produced.

**T-27 (new) — K10 (V2 596–597), after the M9 VERBATIM carry.**
(As to "widened by the instrument's floor and anchor bounds": superseded by T-4/T-5; the floor gates windows, only the anchor bound widens.)

**T-28 (new) — S9 (V2 923) and K16, append.**
A constituent of an estimable merged group that carries a flag keeps level status `p` + `pooled_in`; the flag is recorded true on that level and the group is NR with `flagged_levels` (T-9).

END OF ADDENDUM RULING. Severity: BLOCKER A1; MATERIAL A2–A13, A18-a; A17(iv) reservation to Ed (O-21); NIT A14–A17(i)–(iii), A18-b..e. No verdict of 30/10 is reversed; the texts above supersede the named T-n and add T-24..T-28. Ed decides E1–E4 and adopts AP-5M; T-24, T-25 and T-26 are text for that adoption, not policy.
