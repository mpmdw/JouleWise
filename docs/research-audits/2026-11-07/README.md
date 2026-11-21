# Research audits, 2026-11-07

> **Status: model-written audits for the lead to triage. These are not adopted rulings.**
> Each track was audited by two independent seats (Fable 5.1 high and Opus 5.5 xhigh), then an
> Opus 5.5 synthesis cross-checked the seats against the repo and wrote the report. Nothing here
> changes the registration, the protocol, RUN_STATE.md or any frozen component. A decision listed
> below takes effect only when the lead rules on it, in the public deviation log where a
> preregistered rule is affected. Every seat was briefed under the blinding rule (no Block-5 outcome
> values, no restricted custody); Block 5 stays sealed.

Each report contains the synthesis, the numbered decisions for the lead, dropped and corrected
claims, and both seat reports verbatim in its appendices.

## Tracks

| Track | Report | Source branch @ commit |
|---|---|---|
| ALIGN v4 W1 pre-arm blind gate | [w1-prearm-gate.md](w1-prearm-gate.md) | `research/2026-11-07-w1-prearm-gate` @ `53a230598` |
| W1 budget-fit (ruling 1(f)) and the 1(e) fallback | [w1-budget-fallback.md](w1-budget-fallback.md) | `research/2026-11-07-w1-budget-fallback` @ `93b049612` |
| Block 6 design and registration audit | [block6-design.md](block6-design.md) | `research/2026-11-07-block6-design` @ `07b9f704b` |
| Block 5 release-to-paper path | [b5-release-to-paper.md](b5-release-to-paper.md) | `research/2026-11-07-b5-release-to-paper` @ `79d8e2dbb` |
| Related-work literature review | [literature.md](literature.md) | `research/2026-11-07-literature` @ `16e1db623` |
| Research program: what is noteworthy so far and what next | [research-program.md](research-program.md) | `research/2026-11-07-research-program` @ `7f74dd2a9` |
| Proportionality and pruning audit | [proportionality.md](proportionality.md) | `research/2026-11-07-proportionality` @ `5010326b7` |

## ALIGN v4 W1 pre-arm blind gate

Report: [w1-prearm-gate.md](w1-prearm-gate.md) (`docs/research-audits/2026-11-07/w1-prearm-gate.md`)

### Summary

1. Verdict: do not arm W1 at e901eb2a4. The kit already refuses because R0/R1 are pending. Every finding below applies once R1 fills the slots.
2. BLOCKER: protocol v4 is still a draft. It lacks 9 W1-blocking chair rulings (4, 5, 6, 9, 11, 15, 17, 18, 20), and WP19 does not exist. The desk still uses the old U3 bar and the old "same sign" contrast rule. require_w1_ready never checks for registration.
3. HIGH: (a) the battery 4(a) arm rule is missing. (b) The 30B contrast can get a G0 cap above its fixed 1,086 s deadman, has no fit check, and the kit never checks that R1's X-G run completed. (c) A failed duty bar admits W1 on a bare fallback step, and steps 2 and 3 cannot be expressed in the kit. (d) The arm-time offload re-hash conflicts with ruling 20. (e) The WP14(a) classifier text in the protocol is not what #692 runs. Both seats' probes and the disputed claims were re-checked and re-run at the head.
4. MEDIUM: the D seed tag must be decided before arm. The protocol's "--max-failures 1 stops the stage" is false: the chain passes 9 (refutes seat 2's LOW-7). The Ruling 76 test fails at the head and passes at the base (I ran both). Ruling 20 has no in-window volume census. R1 skips W1's cooldown-v2 between members. r0_sha256 is never bound to an R0 record.
5. Housekeeping: both seat reports are in the appendix verbatim. Corrections and dropped claims are listed (seat 1's x7 citation, both "12 h" estimates, seat 1's slack arithmetic). My worktrees are removed. Seat 1's worktree jw-wt/fable-w1gate is still present and was not mine to remove.

### Decisions for the lead

1. Registration (BLOCKER-1): for each of CHAIR rulings 4, 5, 6, 9, 11, 15, 17, 18 and 20, either install it in protocol v4 and the desk or log a public deviation. Land WP19 and restate WP14(a) from #692 with the chosen D5 rule. Also decide whether require_w1_ready should refuse without a registration receipt (protocol commit, both cold-gate verdicts, ruling-table state). Recommended: yes.
2. Battery 4(a) (HIGH-1): choose a code check in arm_checks (pmset plus the ioreg block; refuse unless >=99 %, not charging and OBC off; record the block) or a signed manual checklist with the ioreg block in each arm record. Fix protocol :698, which still says >=95%.
3. 30B contrast (HIGH-2): confirm that G0_cap_W1 applies to contrast members (protocol :365 is ambiguous). Then choose one: (a) the kit refuses unless R1's X-G completed all WP18 turns with no deadman and G0_cap_W1 + (X-G wall - X-G G0) <= 1,086.3 s; (b) a separate contrast G0 cap that fits the deadman; or (c) accept the X7 risk and pre-declare the contrast verdict conditional on it.
4. Duty-bar fallback (HIGH-3): should the kit refuse steps 2 and 3 until it can express them? Should step 1 require S6 != S5 with its receipt? Should an inconclusive duty bar need an R1 re-run, as R7-3 does for calibration segments? Recommended: yes to all three.
5. Offloads vs ruling 20 (HIGH-4): where do W1's offload destinations live? If on the external SSD, choose a daytime offload-verification receipt with a freshness bound, checked at arm (recommended), or rule the live re-hash out of the W1 arm gate.
6. D seed-law tag (MEDIUM-1): before arm, either keep qwen3.8-27b for the whole D cohort (CHAIR 25 becomes a label only) or change to qwen3.8-27b-8bit now and regenerate the kit. After W1 only the first option remains without orphaning ordinal 5's sentinel/E_ref trajectory.
7. U5: check_r1_evidence accepts a U5 FAIL. Should a U5 FAIL at R1 admit W1?
8. Unobserved capture at member 5 (MEDIUM-2): accept losing the window (every later thermal member becomes X4) or add a chain-level stop at ordinal 6. Either way, correct the protocol's '--max-failures 1 stops the stage'.
9. D8-1 vs Ruling 76 (MEDIUM-3): re-raise only KeyboardInterrupt, or amend Ruling 76 and its test under recorded authority. The suite stays red at the head until one is done.
10. R1 vs W1 schedule (MEDIUM-5): run R1's gated block through W1's cooldown-v2, or record the offset and accept the conservative bias in G0_cap_W1, 1(f) and the duty bar.
11. After the post-R1 1(e)/1(f) ruling changes the kit (B_D, T_dead, possibly 4-bit): run a delta blind gate scoped to the kit diff before arm? Recommended: yes.

## W1 budget-fit (ruling 1(f)) and the 1(e) fallback

Report: [w1-budget-fallback.md](w1-budget-fallback.md) (`docs/research-audits/2026-11-07/w1-budget-fallback.md`)

### Summary

1. Both seats are right, and I re-checked it against the code: under R7-2's G0 term (never below 600 s) and R6-3's full last turn, 8-bit D fails 1(f) at every allowed B_D, whatever R1 measures. Even the impossible best case needs at least 15.1 tok/s. The Mac's bandwidth ceiling is 14.0 tok/s (Apple spec: a 128 GB M3 Max is the 400 GB/s part, and D's weights are 28.58 GB), and R0 measured 11.85-11.95 tok/s. The "about 20 tok/s" figure in R7-2 and R8-8 has no source.
2. None of the four named 1(e) steps rescues 8-bit, and no 1(e) ruling can reach the kit today: the 1(f) refusal is unconditional (align_v4_kit.py:629-633), and DUTY_FALLBACK_STEPS only feeds the duty-bar check. Step 2 also pushes the contrast members to a 1,900 s bound and forces ordinal 18 out.
3. Where the seats disagree on a remedy, I side with neither. Seat 1's W1-only waiver does not hold up: W1 ordinal 5 is the D_k sentinel original and the E_ref source, and 5/17 is W1's U3 pair, so W1 must run in the final D configuration. Seat 2's member-cap fix (S1) is valid but needs Ed's Mac time, so it belongs at council. I rejected seat 1's D-a, which quietly loosens the worst case, and corrected D-f: step-d's B_D at 8-bit is 12-14k, so per-token scaling probably raises the holds term.
4. The smallest deviation that keeps 1(f)'s worst-case guarantee is to size D's W1 G0 cap to the budget: arm it at G0* = T_dead - holds - prefill/tool - 10,240/r. A long G0 then ends as a clean X2 before turn 1, never an X7. It works if 1.25 x the longest released gated D wait fits under G0*. G0* is 76-268 s at 8-bit and 424-617 s at about 20 tok/s (4-bit), so R1's measured waits pick the branch.
5. New finding: R1's gated runs are armed at step-d's B_D, not the 6,144 floor, so at 8-bit they are likely to hit the deadman for budget reasons, not thermal ones. The duty bar will probably fail on "no X7", which means any W1 admission needs a duty-bar 1(e) receipt as well as a 1(f) receipt. The document also has a pre-R1 checklist, a step-by-step post-R1 procedure that reads only timing and count fields, my recomputed grids, a list of dropped claims, and both seat reports verbatim.

### Decisions for the lead

1. Record now, blind, that under R7-2's G0 term and R6-3's full last turn 8-bit D fails 1(f) at every allowed B_D whatever R1 measures. Correct the 'about 20 tok/s' premise in LR2 R7-2/R8-8: 8-bit runs at about 11.9 tok/s, and 20 tok/s is the unmeasured 4-bit projection.
2. Pre-declare the post-R1 procedure before any R1 number is read, and rule whether the budget-sized D G0 cap (D-d) is allowed. It lowers the 600 s G0 floor for D members only and keeps 1(f)'s worst case. Order: D-d at 8-bit, then 4-bit (current rule or with D-d), then council (S1/S2 member cap, final-turn truncation, series-wide bounded-risk 1(f), or screen-only).
3. Rule out 1(e) step 2 as a 1(f) lever on the arithmetic: it costs 132 s of T_dead, puts the contrast members at a 1,900 s bound, and forces ordinal 18 (s93, the alternate sentinel) out of W1.
4. Commission the kit lane before R1, with failing-first tests and a cold review: a 1(f) lead receipt honoured by ruling_1f_fit; separate G0 caps for D and contrast members (R7-12's 'D-to-X' wording); a D cap below 600 s under that receipt (validate_gate_policy); the holds term projected per decoded token to 10,240; and the duty-bar 1(e) receipt alongside it.
5. Magistrate's call: stage the 4-bit download, pins and d_4bit_source so the optional d-4bit step records r4 and I_D4 on the R1 night (adds up to about 5,764 s to a no-redo worst case of 56,207 s). Any 4-bit W1 still needs its own R1-4bit gated night.
6. Settle W1's final D configuration (quantization, B_D, T_dead, per-turn cap) before W1 arms. Limit ruling 17's post-W1 revisions to the G0 cap, delta_slow, G_turn and N_chunk, or explicitly accept losing W1 ordinal 5 as the sentinel original and E_ref source and W1 as a U3/U4 window.
7. Say whether the contrast members are meant to keep 600 s (protocol v4:365 'Every other G0 keeps 600 s') or take G0_cap_W1, which is what the kit arms through the shared thermal_policy.
8. Reject seat 1's D-a (1(f) G0 term = measured max while W1 still arms a cap of 600 s or more) as a worst-case loosening. Replace D-f's expected saving with the symmetric per-token holds projection.
9. Ask Ed now: may the paper name a 4-bit model (CHAIR (B) Q6)? If council picks S1/S2, will he grant Mac time for W1 above 44,640 s (up to 59,520 s) and 4-7 D_k windows instead of 3?

## Block 6 design and registration audit

Report: [block6-design.md](block6-design.md) (`docs/research-audits/2026-11-07/block6-design.md`)

### Summary

1. Block 6 has already been collected: nine counting sessions closed on 10-21 and are sealed (RUN_STATE.md:203-207). Changes can now only be blind REG §17 entries under §12.4, and both seats say to land them before the block-5 unseal. REG §17 has no entry since 10-17; the DLE-2 entry for block 6 and a DLE-1 counterpart are both owed.
2. No block-6 analysis path is both registered and runnable. There are three unmerged candidates. First, L9 plus a binding seam (B6-AN-1, which so far runs only against a fake adapter). Second, the block-5 lean script named by CANONICAL.md:48 and DLE-2, which has no block-6 mode and still binds the block-5 catalog, the GAMMA midpoint rule and claim_usable. Third, RC-B6-1 (independent_recompute_b6.py @ 74a4f8123), the only real implementation; it runs serially and does not pin the block-5 script it loads.
3. The S-13 agreement tolerance cannot be applied yet. Three precision tables disagree by up to 100x: the placeholder bar set, DESIGN D15, and the RC-B6-1 table the lead ratified on 10-27 but never registered. A synthetic probe showed that meter rows refuse under the placeholder set rather than pass silently. RC-B6-1 compares words exactly, without the FS3 tie rule, and its comparison keys were generated from its own output.
4. The D5 fix exists only on a local lane (r4 @ 7db6fb9a3). Since Fable's audit it has become a two-mode rule, because cf42f2a98 broke the synthetic floor binding. Block 6's runner writes the same campaign-log record types, so the fix applies, but L9 reads compressed campaign logs as empty. A binding refusal still exits 3 with the dry run marked complete.
5. Nothing on any candidate path computes the seven DLE-2 families, the two whole-machine lines (4 of block 5's 6 release defects were in the request-level one), §9.5 item 7, E_add or P*. Every raw plist is .zst and main has no way to read it; the Air has 54 GiB free. Estimated runtime: lean path about 20-40 min once given a worker pool; L9 audit as designed about 16-25 h, or about 3-5 h with floor-session reuse and units in parallel. The doc lists 11 decisions, 12 amendments (R0-R12) and 8 code preconditions, with both seat reports verbatim.

### Decisions for the lead

1. Production architecture (gates R1, R3, R4, R11, R12): (a) REG §13 as written, L9 plus seam prints; (b) DLE-2 literally, lean prints and the L9 heavy audit runs once (still needs the seam); or (c) the proportionate path. Under (c), RC-B6-1 prints, with a worker pool added and the block-5 script digest pinned. The second side is the twins on main (harvest_twin §1.7-1.8, engine_twin §9.4), a small counting/pairing/§10-§11 checker and the stored_energy_mismatch reducer gate. The L9 audit becomes optional, recorded as a §17 deviation. Recommended: (c), with re-derivation of exclusions under the block-6 catalog mandatory.
2. S-13 precision (gates R2): keep S-13's rule and register the parameter it lacks, the strictest per family across the three tables. That is J 5 decimals, ratios 4, per-token 8, t 3, p 4, b_op 6, counts and words exact with FS3, and the 1 mJ run-energy bar unchanged. Use one comparator code path. This supersedes lead decision 1 of 10-27. Do not adopt block 5's 1e-6 relative bars: above about 5 J they are looser than a 5-decimal half-unit.
3. Amendment deadline: land R0-R12 before the block-5 unseal. REG §12.4 only requires them before the block-6 release. After the unseal, allow only labelled tooling-defect fixes that choose no rule.
4. Push, review and tag the local r4 lane (lane/2026-11-07-b5-analysis-r4 @ 7db6fb9a3) as b5/analysis-r4. Any L9 use for block 6 must be based at or after it, with a block-6-shaped fixture of the two-mode campaign-log rule.
5. If the audit has not finished at release: hold (recommended) or release labelled provisional (DLE:189-191).
6. Coverage, family by family (the seven DLE-2 families, the request-level and per-phase whole-machine lines, §9.5 item 7): either computed and compared, or copied from the record, bound by digest, not recomputed, with an item-83 hand check. Recommended: the second for count-type disclosures, the first for both whole-machine lines. Also rule whether B5-PLAN §8.2's request-level line is registered for block 6 at all.
7. S-15: adopt DESIGN §8's meter-only per-phase whole-machine definition, labelled single-implementation or with a second producer named. Rule whether block 5's per-phase value is computed after the block-5 release (a new block-5 number) or §10 prints 'block 5: not computed'.
8. Estimand wording: (a) §9.5 item 3's T, estimator-1 weights (DESIGN) or the plain mean over kept members (RC-B6-1); they differ on any incomplete cell. (b) The E_ref/T_ref basis. (c) The J6 sensitivity line, in or out. (d) A §10 label for the s_bracket difference (up to 0.175 J), plus a block-6-only summary.
9. Analysis host and read path for the compressed bytes. Host: the Air (54 GiB free) or the magistrate-owned MBP. Read path: stdlib compression.zstd streaming (Python 3.14 only; the runbooks pin 3.13), desk_compress.read_bytes (needs the zstd binary; on the b6 lane only), or APFS in-place restore (the restore tool never reached main).
10. Hold item 144's deletion of the L9-ENV-3 whole-window mirror until any L9 block-6 audit has run, or until decision 1 retires that audit.
11. Authorize one counts-only, structure-only probe of the nine sessions: waited runs with attempt-N baselines, wait-cap and budget skips, anchor_not_bounded members, and the member phase checks re-run under the registered 10.818 ms b_op. It sizes the D2/D3/D4 exposure and checks whether any kept-unit set differs.

## Block 5 release-to-paper path

Report: [b5-release-to-paper.md](b5-release-to-paper.md) (`docs/research-audits/2026-11-07/b5-release-to-paper.md`)

### Summary

1. The release check itself (release_b5.py) is sound, but after it prints agree almost nothing is written down. The "Release event" section of SEAL_RECORD.md:624-628 is empty. No Block-5 Results renderer is on main; the only one, #652, needs a release-mode record, so it refuses the custody the current release procedure (DLE-1) produces. Nothing fills Paper 1's 219 FILL ids, so today every printed number would be copied by hand.
2. New blocker, confirmed in code: the release comparator can never pass a registered null outcome. Any null, even null on both sides, counts as DISAGREE (compare_b5_recompute.py:211-222), and floor values are compared whatever the resolution status (:2150-2154). So a legitimate not-estimable or refused-floor result can never be released. The plan says such a result "is printed as such" (plan:178). A blind rule is needed before r4 releases.
3. The lead stops being blind at the release event, so every remaining choice must be made before it: placement (§14 Q4) and what replaces the D-174 fallback; the gate that replaces the "Results cold gate" (Q-RENDERER still requires it, but DLE-0 abolished it); print precision; the paper-input route, which must work whether or not the D-189 claim sidecar exists; independent hand-check sources (the coverage audit names only L9's own code, LEAN-COVERAGE-AUDIT.md:105); and the missing analysis-program addendum (registration §11 item 4).
4. Blinding channels: the runbook treats Ed's OK as the boundary, but the registration makes the recorded event the boundary. *.released.txt holds the values. The public verdict's pass counts include rows created per quad that raises the leave-one-out magnitude trigger, a count derived from energies. The repo is public, so any released number committed anywhere unblinds the blind repair seats.
5. Paper 1 (unmerged lane a1a5029fb) contradicts the record: it quotes Block 6's tolerance as Block 5's; says the analysis ran after the release event; says no agent used the data account; says the outcome text was fixed before the data existed; misdescribes how a changed file is handled; and claims "every printed quantity" was recomputed. The report gives an ordered checklist with commands, where all writing and building happens before the event and only mechanical copying after it. It also corrects seat errors (window_flags.json is restricted; the r3 id quoted was the tag object, the commit is 68e47e1f2; the worklist is built from the synthetic run, not the real comparison.json) and lists the claims it dropped.

### Decisions for the lead

1. Registered null outcomes in the release comparator: before r4 releases, decide whether a contrast or floor resolution in a registered null state can ever reach agree. Recommended: for not_estimable, compare the outcome word and whether the value is null, and skip the number rows. For a refused floor whose reason is floor_transport_inapplicable, check transport applicability against the sealed manifest. Binding or authentication refusals stay holds, as DLE-3 already rules for D5. This needs a DLE entry, synthetic fixtures for each D-190 state and a cited rebind of the release-check commit. The alternative is to record that any null is a permanent hold, which contradicts plan:178.
2. DLE-4: name the gate that replaces the abolished 'Results cold gate' required by Q-RENDERER (SEAL_RECORD.md:631-638). Recommended: one fresh executing reader who re-runs --validate-rendered, samples leaves against a frozen bundle, and runs the licence lint and the Paper 1 checks. That seat is the second licensed reader after the event (registration:4901-4902) and must not be a repair seat.
3. Placement: a dated addendum ruling on registration §14 Q4 (which plan §9 rows print, at which sites, with which fixed sentences). It must also replace the 2026-09-05 D-174 fallback disposition, which needs Ed's written instruction or a dated D-174 addendum, and rule on the Paper 1 title against D-165's protocol-first title.
4. Paper-input route: (a) extend D-173 custody with roles for floors, the close-out and the disclosures, plus a CLI, or (b) port #652 to DLE-1 so it reads a frozen bundle bound by the dry-run record's digests, adopted by a DLE entry. Either way it must render both D-189 branches, with and without the claim sidecar. Recommended: (b).
5. Print precision per family. Candidate: paper_rendering.py:46-49 (3 decimals in J, 6 in J/token, half-even rounding, interval ends rounded outward). Re-point RS item 83 ruling 2 at whatever is adopted.
6. Name an independent hand-check source for each of the seven families the recompute does not cover, the exempt load-correlated line and the reason codes, and name who does the hand check. DLE-0 and DLE-1 cite sources from the coverage audit that it does not name.
7. Analysis-program addendum (registration §11 item 4): write it before the event, covering the r4 tree plus the release-check commit's release_b5, recompute, comparator and bars (command in §5 A6), or record a DLE entry that the tag, the record and release_checkout.commit satisfy it. Recommended: write it.
8. Rules after the event: name the readers and the blind repair seats; keep released values, including the filled paper, out of git until the gate and repairs close (the repo is public); PR bodies and repair briefs carry structure only; keep a reader log outside the repo.
9. Paper wording: fixed sentences verbatim or paraphrased; a gloss table from each registered refusal or outcome code to its sentence; and whether to pre-write a grid of abstract and conclusion variants (recommended, not required).
10. Disclosures: Paper 1 must disclose that GAMMA floor-resolution status and reason words were read before release under a structural ruling, and that D5b was ruled after that read. Decide whether to disclose the per-family count channel for Block 5, and whether the Block-6 public verdict drops counts on agree.
11. Choose the canonical Paper 1 (lane/2026-10-27-paper1-draft or the #531 outline), open its PR, tag the outcome text written before unseal, and point CANONICAL.md's Paper rows at it (they still name the frozen draft-v1.md).

## Related-work literature review

Report: [literature.md](literature.md) (`docs/research-audits/2026-11-07/literature.md`)

### Summary

1. No source uses measured energy to audit an agent's logged token counts, so ALIGN's question is open. Two literatures sit on either side: software-only hidden-token audits (CoIn, Token Inflation) and physical verification that works only at workload or aggregate scale (Gargiulo & Kulp; Kimpson et al.). The best framing is the H50/H90 curve as a per-episode, token-level version of Kimpson's beta.
2. Both seats agree that published Apple-silicon LLM energy work treats powermetrics as a meter (AgentStop, GreenBench, Hübner et al.), even though Apple's own man page calls its values "estimated and may be inaccurate". Neither seat found any LLM energy study that gates on thermal state.
3. Seat 2 raised two ALIGN threats that I checked and confirmed; no ALIGN doc mentions either. First, tamper evidence: powermetrics is software on the same host, and the claim only holds against a non-adaptive adversary. Second, the five-term residual design assumes full attention, but model D (Qwen3.8-27B) has a hybrid, non-trimmable cache.
4. Disagreements mostly resolved in the repo's favour. Seat 1 said pilot_protocol_v4.md doesn't exist; it does, on lane e901eb2a4 at commit 543c9565d. Full-text checks found the draft's citations [19], [20], [23] and [26] correct, so only venue updates are needed. Both seats missed that [9] Hübner and [11] AgentStop are already in the reference list but never cited in the body.
5. I re-opened 35 sources myself. I corrected three seat claims (Token Inflation's 1,469% is "up to", not an average; the exact SHADE-Arena quote; the IPW accelerator list). I dropped the preprints.org paper, which returned 403 for seat 1 and for me. The source list has 104 entries, and both seat reports are kept verbatim in the appendices.

### Decisions for the lead

1. Before the registration cold gate, add threat-model wording to v4 and the ALIGN paper: the agent runs unprivileged and powermetrics runs as root under the harness, and the claim covers only a non-adaptive adversary (known log omission with joules held fixed). Recommend yes; defer an external meter. v4's estimand is already non-adaptive (pilot_protocol_v4.md:508-516), so this changes text, not design.
2. Add a print-only residual variant for model D that limits the context-quadratic terms to its full-attention layers (or uses a context-linear form) and reports the change in s_r? Recommend yes; the primary fit stays unchanged.
3. Also print the known-H curve as hidden work divided by declared work, so it compares directly with Kimpson et al.'s beta? Recommend yes, beside H50/H90 (ruling 2, v4:611).
4. Khiani, 'Blinding the AI Co-Scientist' (NeurIPS 2026 workshop poster) closely matches JouleWise's governance. Is it independent prior art (cite as a neighbour) or connected to this project (cite as source, with disclosure)? The repo has no reference to it; only you can answer.
5. May draft-v1 §8 take edits now: venue updates for [20] (PPAM 2026) and [22] (NeurIPS 2026), and body citations for [9] Hübner, [11] AgentStop and [21] Silicon Showdown, which are listed but uncited? Citing existing numbers needs no renumbering. Recommend yes; leave other additions for the next paper round.
6. Start an ALIGN related-work doc on the lane now, built from sections 3-4 of the synthesis plus the threat wording from item 1? Recommend yes, before the cold gate reads v4.
7. Critique GreenBench's 0.47 W package figure only on its inconsistency with the paper's own 8-12 W system figure, with no powermetrics check on the Air? Recommend yes.
8. Confirm no change to v4 on sidedness: a one-sided test is correct because known-H omission can only raise the residual. If a causal sabotage estimand is added later, it must preregister its expected sign or be two-sided, since sandbagging predicts a negative residual.
9. Defer adopting ControlArena: its Inspect sandbox conflicts with v4:692-693, which says native gates need no agent session on the measurement Mac. Nothing in v4 needs it.

## Research program: what is noteworthy so far and what next

Report: [research-program.md](research-program.md) (`docs/research-audits/2026-11-07/research-program.md`)

### Summary

1. Yes, there is a novel line: ALIGN (energy as a record of agent work the agent cannot edit). On Qwen3-30B-A3B the residual SD per task pair is 19-58 J on 2-4 kJ episodes, replays repeat to about 2 J, and every held-out one-turn omission (539 or 1,193 tokens) was detected. But the held-out sabotage is only 2 distinct trajectories, each threshold is the sample maximum, and the tamper is a log edit, not real hidden work. On pilots 4-9, 2 of 26 untampered bank sabotage runs were above threshold.
2. Paper 1's strongest material is BYTES plus the known-bytes test: about three quarters of memory-traffic energy falls outside the powermetrics rails (f = 0.238 ± 0.098, one session at low bandwidth). Seat 1 said this result was missing; it is on main in KB-SLOT-FILL.md.
3. The biggest risk is operational. BYTES stage 1 is due 12 Nov and needs no measurement window, but nobody owns it: RESUME.md does not mention BYTES or Paper 1, CANONICAL.md has no BYTES row, and the registration and analysis code sit on a lane last touched 10-28. The thermal-line step seat 2 called owed was done on 10-31.
4. ALIGN v4's first window (W1) will probably be refused under ruling 1(f). Choose the 1(e) fallback now, blind. A 30B night that injects real unlogged compute is the best fallback (1-2 Mac-nights) but needs Ed's OK. The v4 series itself is about 5 Mac-days, or 8 if Ed vetoes the long windows (Q4).
5. DIFFICULTY's analysis code is ready, but its collection code is unbuilt, and the result is close to known work (Jin, Wei, Brooks 2025; checked). Keep it third and lean, as a section of Paper 2. Dropped claims: seat 2's 170-470 token detection limit (it assumed the wrong score formula) and the VIF 3.4e6 figure (not in the registration). Corrected: seat 2's 335x→3.3x batching ratio (the uncached figure is 115x).

### Decisions for the lead

1. Give BYTES stage 1 an owner and a date now, ahead of the 12 Nov checkpoint (Tier D if it misses 15 Nov). Steps: merge lane/2026-10-28-bytes-pass2-open with the KB result copied into bytes_pack_v1.md section 1, build the stage-1 export, then re-run the thermal lines with --export. Add it to RUN_STATE, RESUME.md and CANONICAL.md. The data sits in night-archive on the MBP, so either the magistrate runs it by day or it needs a transfer.
2. Rule the ruling-1(e) fallback order now, blind, before R1's numbers exist. Recommendation: if W1 is refused, run the 30B confirm-and-inject night (if Ed allows it), then retry W1 at the largest B_D the kit says fits. Do not redesign during the 15-22 Nov writing window.
3. Ask Ed whether the ALIGN paper's claim is 'energy as an independent record of logged compute' (the 30B is enough) or 'sabotage leaves an energy signature' (needs v4). Also ask whether he will allow one or two more 30B nights as a positive control, given his 'pilot 10 is the last v3' ruling (RUN_STATE.md:1653).
4. Get Ed's answers to FINAL-DESIGN Q4 (59,520 s D windows) and Q6 (registration grade, m >= 39), or rule on them. The repo records no answer. A no on Q4 doubles the D windows; a yes on Q6 roughly doubles the calibration windows.
5. Decide whether to run a short repeat of the known-bytes test at full memory bandwidth (about 1.3 h, labelled exploratory) before Paper 1's 15 Nov scope freeze, or to report the result with its low-bandwidth limit only.
6. DIFFICULTY: approve the lean path, logged in the public deviation log: collect energy through the unpinned ALIGN Apple runner, and run the bench off the quiet Mac after an output-identity check. The alternative is to defer DIFFICULTY to December (its end date is 2027-01-31).
7. Refresh PROJECT_STATUS.md (still says 'No claim-bearing Qwen3 data exist') and CLAIMS_STATUS.md (last updated 2026-08-20) before the 22 Nov draft goes to Ed.
8. Retitle Paper 1 around what a laptop's own power counters can and cannot resolve for LLM inference, led by BYTES, the known-bytes result and the attribution floor, instead of 'Timing Sensitivity of Phase-Energy Assignments' (draft-v2-skeleton.md:7).

## Proportionality and pruning audit

Report: [proportionality.md](proportionality.md) (`docs/research-audits/2026-11-07/proportionality.md`)

### Summary

1. Both seats put the same two prunes first. R0's 0.05 CPU-s/s contention refusal caused 4 of R0's 8 stops (8 stops, no pass, 8,824 s of Mac time over about 33 h) and protected no reported or blinded number. The W1 High Power restore stack produced 10 of the 11 HIGH/MEDIUM review findings after round 5, and its reviewers say it cannot admit bad data.
2. New finding from the cross-check: the lead's R0-L1 ruling (item 196 (2)) authorised a run of every check except SMC, which would have produced the ladder rung. The headless launcher cannot start that run. It writes a fixed runner spec with only --config and --output (scripts/launch_align_r0.py:201-202), so --checks and --keep-going never reach the runner. No attempt is recorded, and the 06:15-11:05 gap went unused.
3. The R1 code does not use R0's refusal; its rule is ruling 8 (redo at 0.5 cores sustained 60 s, refuse after 2 redos). None of R0's four contention refusals would have triggered it. Caveat: I did not trace whether an R1 night reaches run_night's DIAGNOSTIC_NO_PACK path, which runs prewindow_check.sh.
4. Disagreements ruled: High Power is frozen now and cut after R1 (deleted if not adopted, simplified if adopted). Neither proposed change to the kit's changed-pick checks is made: R9-2 only checks arithmetic on recorded values, so the lead's receipt is not redundant. --mode release is deleted after the release, not during the D5 hold.
5. Block 5 is already lean and its comparator earned its cost (6 defects found, 1 of them in L9). What remains is mass: tests/b5_analysis takes about 21-23 % of per-PR CI time, plus round-named tests and retired paths. Corrected claims: the registry has 196 tooling codes plus 2 outcome codes (not 191); the rule-9 tally does appear in RC-CMP-5/6; the disclosures.py:696 key is already fixed on main. Dropped as unverified: the seats' test timings, the import-closure size and the 15-20 h counterfactual.

### Decisions for the lead

1. R0 contention (rank 1): should CPU contention become a recorded flag on every non-SMC check, with SMC using ruling 8's rule (one redo at 0.5 cores sustained 60 s, then flag), keeping the armed-window, LaunchAgent, chain and custody refusals? Also decide whether this lands before or after re-run 8, which uses unchanged code.
2. R0 launcher (rank 2): approve a rule-2 tooling change so launch_align_r0.py passes --checks and --keep-going through to the runner, with keep-going as the default for desk runs. This makes the R0-L1 subset run plus composition launchable headless if re-run 8 is refused again.
3. W1 power mode: (A) rule now that W1 runs in Automatic whatever the A-B-A shows (protocol v4 is unregistered; adoption rests on n = 1), or (B) keep adoption conditional. Either way, freeze the High Power stack now: no more desk rounds, and new findings are recorded unless they can admit bad data.
4. Review rule: apply gate_policy as written (rule 2 for tooling; rule 3's two seats launched together count as the cold pass; Sol critiques advisory). Add: no further desk round on a measurement component after one number-bearing round until it has run on hardware. Also decide whether to revive or delete rule 9's pruning tally.
5. Measurement-lane merge gate: quick_suite --tier touched plus tests/align, with the full suite run after merge, non-blocking, and revert on red.
6. Ruling 1(f)/1(e): either pre-commit mechanical application of fallback steps 1-2 (S6 tuning, idle 450 s) and keep 4-bit and screen-only as lead steps, or keep the ruling after R1 and book the lead's time the morning after R1.
7. An INCONCLUSIVE designed-start-state segment: record U5 as INCONCLUSIVE, run a patch night, or keep the full R1 re-run. A step-d INCONCLUSIVE stays a refusal.
8. Set R1 window_max_s to one constant of at least 90,663 s and stop re-deriving the worst-case table. Put to the window council: the no-redo R1 night (56,207 s) is 11,567 s longer than W1's cap.
9. Run tests/b5_analysis on path changes plus nightly instead of every PR, and stop heavy-pipeline speedup work. Answer DLE-2's open point: is a release held or labelled provisional if the block-6 audit has not finished?
10. Name the owner of each pruning PR (ranks 1-3 as separate reviewed PRs, not part of the R1 arm). Name who reviews the R1 lane's run_night interrupt and lock changes on BYTES, HAZARD and TRANSACTION nights before the lane merges to main.
11. Narrow item 181's 'third consecutive failure of the same check' escalation to science changes and irreversible data actions.
