# Capstone paper plan v2: a near-complete draft by 30 November

**Title (Ed's):** *Sabotage Leaves an Energy Signature: A Pilot Study of Physical Auditing for AI Agents*

**Claim the paper can carry on unblinded evidence.** On one Apple-silicon laptop, an energy residual against logged work detected every tested known log omission in a non-adaptive pilot. The tested omissions were 539 and 1,193 reasoning tokens, on two sabotage trajectories re-checked across sessions. A known-bytes test shows that host software rails miss about 76% of a controlled memory-traffic contrast, which motivates an external DC meter. The paper sets out a three-layer oversight frame (monitors see content, the meter sees quantity, probes see internals), states the squeeze as a hypothesis, and gives the registered v4 and v5 plan.

**What it must not claim.**
- detection of intent or of real hidden computation;
- a false-alarm rate;
- an H50/H90 or a minimum detectable H;
- that the squeeze holds;
- any v4, v5, Block-5 or BYTES held-out result.

The title asks more than the evidence shows. So the abstract's first result sentence must carry the scope: known log omissions, a non-adaptive agent, two trajectories.

**Default variant: B (pilot plus registered plan).** Variant A (adding released v4 results) is an insert, not a rewrite. It is used only if v4 passes its registered release, with the independent recompute agreeing and Ed's unseal OK, by about 10 December (strategy §0). As of 7-8 November, R0 had not passed, W1 had not armed and protocol v4 lacked nine chair rulings. A registration-grade release by 10 December would need W1, three D windows and about seven calibration windows to all run cleanly in about four weeks, so **plan and write for B.**

**What stays from v1.** [PAPER-OUTLINE.md](PAPER-OUTLINE.md) remains the source register (V3, ER, CODE, P7-P10, KB, BYTES, LIT, DESIGN, PAPER), the evidence ledger E1-E9, the related-work map and the threats table. This plan replaces its section list, its schedule (v1 had drafting on 1-9 December) and its ownership, and it adds a research-operations appendix. [FIGURES.md](FIGURES.md) F1-F11 stand. Half-A figures FA1-FA6 are in [TALK-OUTLINE-v2.md](TALK-OUTLINE-v2.md).

## Roles

| Role | Who | Does | Does not |
|---|---|---|---|
| Drafter | **Sol 6.1 xhigh**, local `codex exec`, one job per section | Drafts from the evidence ledger and the cited records only, with a source key on every number. Builds figures from the transcription tables. | Read sealed, restricted or `night-*` paths; run analysis or capture scripts; invent citations |
| Reviewer | **Opus 5.5** (the lead, or an Opus review seat the lead briefs) | Cross-family review of every Sol section. Re-derives each number from the cited record, not from the draft. Runs an overclaim pass. | Rewrite Ed's voice sections |
| Cross-check for Opus-drafted text | **Sol 6.1 xhigh** | Reviews the appendix the lead drafts (research operations) | — |
| Final look | **Fable 5.1**, once, at the 21 Nov checkpoint only | A cold read of the whole draft for overclaim and inconsistency | Line edits |
| Author's voice | **Ed** | Writes the introduction and conclusion; approves the title, abstract and contribution list; gives the unseal OK if one ever arises | — |
| Owner | **Lead** | Freezes the ledger, assigns jobs, merges sections, keeps the gate table below, rules on admitted inserts | Read or relay outcomes |

**Process rule (gate policy rule 1).** Paper sections are docs, so CI alone gates them. The cross-family review above is chosen for scientific accuracy, not demanded by the gate policy. Every number-bearing section gets one Opus re-derivation before it counts as "drafted".

## Section list, status and owner

Status key:
- **Now:** writable today from unblinded, committed material.
- **Gated:** waits on a named event.
- **Voice:** Ed writes it.

| § | Section (target length) | Content and sources | Status | Draft | Review |
|---|---|---|---|---|---|
| — | Abstract (200 words) | Problem, residual audit, instrument boundary (E2), pilot result with the two-trajectory qualifier in the same sentence (E7), registered continuation | Write **last** (27-28 Nov); Now in substance | Lead, from Ed's intro | Ed signs off |
| 1 | Introduction (1 page) | Editable records versus content monitors; the question "does energy add information beyond the log?"; contributions: (i) an episode-level omission audit, (ii) a documented two-boundary instrument, (iii) a limited pilot plus a registered study | **Voice.** Sol supplies a bullet scaffold and citations only (by 13 Nov) | **Ed** | Lead (accuracy only) |
| 2 | Threat model, three layers, baselines (1 page) | Trust boundary; `powermetrics` is host software; layers content/quantity/internals (strategy §2); baselines on the map but unmeasured (software rerun, trusted time, metadata, text monitor); energy's niche is unmediated compute (PR #703) | **Now** | Sol | Opus |
| 3 | Instrument and validation (1.5 pages) | KM003C after the brick (DC input; item 210); rails versus DC; known-bytes E1-E2 with its non-claim status and post-data reading-rule correction; BYTES accounting E3 | **Now** for KB and E3. **Gated:** BYTES stage-1/2 results (see the gate table) | Sol | Opus |
| 4 | Residual detector and calibration (1.5 pages) | ER five-term model versus the sequence (attention-length) design used for the headline (CODE `design_row`; P7 ruling); selection on pilots 4-7; frozen `4d54cb47b`/`7fbd95e31`; LOTO, replay deduplication, per-session fits; sample-max threshold and why no nominal FPR is claimed (R14 wording, item 212) | **Now** | Sol | Opus re-derives the formulae from CODE |
| 5 | Pilot protocol and cohort accounting (1 page plus T2) | V3 configuration (D1); seed law; anchors; eligibility and exclusions E9; roles of pilots 4-7 versus 8-10 | **Now** | Sol | Opus |
| 6 | Results (2 pages plus F4, F6-F8) | 6.1 instrument boundary (E1-E2); 6.2 replay versus regression spread (E4-E5, no "10-25×"); 6.3 known omissions (E6-E7); 6.4 fragility (E8-E9, legacy design rows) | **Now** | Sol | Opus re-derives **every** number from P8-P10 and KB |
| 6.5 | Released v4 results (variant A only) | T4 from an admitted release summary | **Gated** on the v4 registered release plus Ed's unseal OK; omitted in B | Lead supplies the admitted table; Sol drafts | Opus plus independent number check |
| 7 | Related work (1 page) | The LIT map in PAPER-OUTLINE; "no prior token-level agent-log energy audit found in our search" (search-bounded); citation fixes from PRs #698 and #703 (Kyung added; Kimpson is a MATS page; MonitoringBench and Token Inflation wording) | **Now**, with primary-source checks | Sol | Opus opens each cited primary source |
| 8 | Discussion: the squeeze (1 page plus F9) | Hypothesis, not theorem (AGREEMENT-FINAL V01); shared blind spots (cover work, filler, matched energy, fixed-compute latent reasoning; weight-only bound ≤ 3×10⁻⁵ as an estimate from PR #702) | **Now** | Sol | Opus |
| 9 | Threats to validity (1 page) | The v1 threats table plus: the pilot's scored channel is host software; the replay advantage is projected, not measured; v4's registered residual stays GPU energy (R11-3) | **Now** | Sol | Opus |
| 10 | Registered continuation: v4 and v5 (1 page plus F10-F11) | v4 as registered: Qwen3.8-27B 8-bit; Q4 (3 D windows); Q6 (m ≥ 39 per pair plus a test cohort); R10 fallback; KM003C secondary DC-in; sealed transcripts. v5: D07 joint rule, D09 endpoint, D12 time-plus-monitor comparator, frontier monitor, scoped red team; design under competition | **Now** for the design. **Gated** for gate *status* (fill at the freeze) and the v5 design choice (cite only once the lead rules) | Sol | Opus |
| 11 | Conclusion (0.5 page) | What is observed and what is untested; the next question | **Voice** | **Ed** | Lead (accuracy only) |
| App. A | Research operations and AI-use statement (1-1.5 pages) | How the study was run: lead, magistrate, workers; the guardrails (prereg plus deviation log, structure-only blinding, independent recompute and comparator, gate ledger, cross-family review); what humans decided. Half-A ledger H1-H15. Required for honesty and by most venues' AI-use policies | **Now** | **Lead** (knows the record) | Sol, cross-family |
| App. B | Source register, evidence ledger, exclusion ledger, deviation history, figure transcription tables | From PAPER-OUTLINE plus DEVIATION-LOG pointers | **Now** | Sol | Opus |

Rough length: 9-10 pages plus appendices, a workshop-style length that fits the "pilot study" title.

## What is gated, and on what

| Item | Gate | If it does not clear by the cut | Never |
|---|---|---|---|
| BYTES stage-1 (fit) and stage-2 (held-out) results in §3 | Stage-1 commitment checkpoint **12 Nov**; held-out agreement and stage 2 by **15 Nov** (`docs/run_reports/2026-11-07-bytes-stage1-plan.md` on PR #701), then an admitted, released summary from the lead | §3 keeps the KB plus E3 accounting only and says BYTES energy results are reported separately | Read withheld rows, `predictions.json` contents before release, or any BYTES energy before its registered release |
| v4 results (§6.5, T4) | Registered release passes (recompute agrees) **and** Ed's unseal OK, by about **10 Dec** | Variant B: "v4 outcomes unavailable at this manuscript's evidence cut" | Use readiness numbers, partial windows or synthetic power curves in place of results |
| v4 gate status in §10 and talk slide B9 | Not sealed: read it from `RUN_STATE.md` at the freeze (22 Nov), and again at the paper cut | Write "pending" | Report any alarm, residual or energy value from R1, W1 or D |
| v5 design in §10 | The lead's ruling on the design competition (`origin/align/2026-11-08-v5design-*`) | Describe only the R11 choices (D07, D09, D12) and say the design is under competition | Name a roster, sample size or decision rule before the ruling |
| Block 5 | Excluded from this paper. It is Paper 1 material, and sealed | — | Mention any Block-5 outcome. The **process** facts in App. A (runtimes, defect counts, exit classes) are allowed |

**Not gated (write now):** §§2, 4-9 and App. A-B, plus §3 for KB and E3. These sections make up about 80% of the paper and all of the variant-B result.

## Milestones, 9-30 November

2026-11-09 is a Monday. Thanksgiving is Thursday 26 Nov; treat 26 Nov as a light day.

| Date | Deliverable | Owner | Done when |
|---|---|---|---|
| **Mon 9 Nov** | Ledger freeze v1: E1-E9 plus H1-H15. Re-check E3, E4 and E9 against their records. Section jobs briefed to Sol (§§2, 4, 5) | Lead | Ledger committed; three Sol jobs running |
| Tue 10 | Figures F1, F2, F3 and F9 (schematics) and F4 (KB) drafted from transcription tables | Sol | SVGs and transcription tables committed |
| Wed 11 | §§2, 4 and 5 drafted. Opus review of §4 against CODE | Sol / Opus | Review dispositions recorded |
| **Thu 12** | **BYTES stage-1 checkpoint (registered).** §6 and T2 drafted. Sol scaffold for Ed's intro | Magistrate / Sol | Stage-1 commit recorded, or the miss recorded |
| Fri 13 | Opus re-derives every §6 number from P8-P10 and KB. §§7 and 9 drafted | Opus / Sol | Zero unexplained number mismatches |
| Sat 14 | §§8 and 10 drafted (design only; gate status left as `[FREEZE]`). App. B tables | Sol | — |
| **Sun 15** | **BYTES stage-2 deadline.** Lead decides whether a BYTES insert is possible (only from an admitted release). App. A drafted by the lead | Lead | Decision logged |
| Mon 16 | Sol cross-reviews App. A. Assemble **draft v0.5** (everything except the intro and conclusion) | Sol / Lead | One file builds |
| Tue 17 | Ed reads v0.5; Ed's intro draft due **Thu 19** | Ed | — |
| Wed 18 | Slide deck v1 built from TALK-OUTLINE-v2, with figures FA1-FA6 | Sol builds; lead reviews | Every slide number has an ID |
| Thu 19 | Ed's introduction in. Deck v1 to Ed | Ed / Lead | — |
| Fri 20 | Draft **v0.8**: intro merged; Opus overclaim pass (every claim mapped to E/H plus a limitation, T3) | Opus | T3 complete |
| **Sat 21** | **Major checkpoint:** one Fable 5.1 cold read of v0.8 plus deck v1. Sol overclaim pass in parallel (cross-family) | Fable / Sol | Findings dispositioned by 23 Nov |
| **Sun 22** | **Evidence freeze for the talk:** fill every `[FREEZE]` cell (R0, R1 and W1 status; the r4 release-check exit class; BYTES insert yes or no). No new numbers enter the talk after this | Lead | Freeze commit |
| Mon 23 | **Dry run 1** with Ed, timed; exercise the three-slide cut. Draft v0.9 sent to the advisor | Ed / Lead | Timing within 25:00 |
| Tue 24 | Revisions from the dry run and the Fable/Sol findings | Lead / Sol | — |
| Wed 25 | Ed's conclusion draft | Ed | — |
| Thu 26 | (Thanksgiving) buffer only | — | — |
| Fri 27 | **Dry run 2**. Abstract written from the final intro and conclusion | Ed / Lead | — |
| **Sat 28** | **Near-complete draft v0.95 tagged** (`capstone/paper-v0.95`). Every section present; open items listed | Lead | Tag pushed |
| Sun 29 | Slide polish only; no new numbers | Ed | — |
| **Mon 30** | **Capstone talk** | Ed | — |

**Slack built in.** Sol drafts run in parallel, so one lost day does not move 28 Nov. If Ed's intro slips past 19 Nov, the Fable read on 21 Nov goes ahead without it and the intro gets an Opus accuracy read on 24 Nov instead.

## Mid-December finalization

| Date | Step |
|---|---|
| 1-4 Dec | Fold in talk Q&A and advisor comments; tighten §§6-9 |
| about **10 Dec** | **Variant decision.** A only from an admitted v4 release record (pinned protocol and analysis, recompute agreement, deviations, Ed's unseal OK). Otherwise B, unchanged. Either way, re-read the v4 gate status in §10 |
| 10-13 Dec | If A: §6.5 and T4 drafted by Sol from the admitted table only, with an independent number check by Opus, pooled with nothing. Caption and source audit, bibliography actions (LIT; PR #698/#703 fixes), proofread |
| about **15 Dec** | Submit to the capstone program. **The exact due date is to be confirmed by Ed;** this plan does not invent one |

## Acceptance checklist for "near-complete" (28 Nov)

- Every empirical number in the text maps to E or H with a source path, and Opus has re-derived it.
- The two-trajectory qualifier appears in the abstract, §6.3 and the conclusion.
- No sentence implies a false-alarm rate, intent detection, real hidden-compute detection, an adaptive result or the squeeze holding.
- "DC input", not "wall energy". The pilot channel is labelled `powermetrics` GPU energy wherever results appear.
- No Block-5, BYTES held-out, v4 or v5 outcome anywhere. The `[FREEZE]` cells hold status only.
- App. A states plainly that AI agents wrote most of the code, analyses and drafts, and names what humans decided.
