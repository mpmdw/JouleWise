# Lens (Opus 5.5, read-only, non-author): handback v3 rewrite, branch docs/2026-09-23-4158e658-handback-v3

Scope check (executed by section-slice comparison of `git show 3d668e98:` against `HEAD:`): the file head, "Pre-authorized recovery" through "Arm-time census", the refusal tables, the Pre-check step through its zsh block, every Executed block, and everything from "For every v2 plan" to EOF are **byte-identical**. `gen_state.py --check` rc 0; `unittest tests.test_gen_state` 44 OK.

## Contract/fact lens: 31 claims checked, 30 hold

These hold against the code at HEAD: the 0.5 bar (`night_gate.T0_NON_OBSERVER_SHARE_MAX`) and its exact refusal text (`non_observer_refusal_detail`); the 30 s observation, rooted at the checking process's own pid; `armable: false` from `evidence_night.machine_quiet_check`; `night_probe_error` on observation failure; C3 `top_consumers_at_decision`; the ten-consumer limit; ancestry marking (`quiet_admission.interval_metrics`); the recorder started with `--observer-pid os.getpid()`, which is the chain root because both chain.zsh and quiet_predicate_evidence.zsh `exec`; the 30 core-second integral keyed on (pid, start_identity) over rows wholly inside the envelope; `abort_after_consecutive` 2 with typed reason `non_observer_process_busy`; the guard running before rule 2 with its exact text and `night_probe_error`; `envelopes_attempted` 0 when the guard fires at envelope 1; `stop_branch` (three causes, of which the pilot can reach two); floor = sum(whole)/sum(span); the companion floor reported only; the registration sha `69321c69…`, v2 superseded, and every v3 number; the sizing formula; the eleven exclusions; `--t0 next` = ceil((now+2400)/60)·60; `prepare --kind/--t0/--head` (checked against `--help`); plan-id, custody-root and clone naming (`locations`); the notice's attempt counting (no 20260923 candidate exists in staging).

**Timeline** (t0 1790172000 = 07:00 PDT): install close t0−480−120 = 06:50; REQUEST 06:52; TERM 06:54; KILL 06:55; window end 09:30; courier 09:35 (`COURIER_DEADLINE_S` 300); dead-man 1790184900 = 10:35 (`run_night.deadman_epoch`, grace 3600); span 8020 s. All correct.

**Records:** 0.3194 W = 153.3338/480 (ruling 21); every observer-floor number (0.176/0.159, 0.123/0.107, 0.0073/0.0071, 0.183/0.166, 0.0021/0.0027) matches both harvest addenda; 544.7–575.6 and 528.1 match seat report R2; 6.3 (`WindowServer`) and 10.7 (`XprotectService`) match ruling 10. The D-182 addendum text, the arm_retry wording and the D-079 r7 pins (four estimator hashes, identical at HEAD) all check out, and so does `git diff --stat 3a411784..HEAD -- joulewise scripts configs`, which prints nothing.

**Kernel entries** hold against their records: 0fd965fe is an ancestor of HEAD; RUN_STATE line 13 exists; owner record §1/§8, record 04 (nine actions), record 07 "Lane handed to the magistrate" and record 08 §2 all exist.

## BLOCKER
None. Nothing found would mislead the arm, and nothing would mislead the courier about the night's own result.

## MATERIAL

**M1 (fact), NIGHT_HANDBACK.md:342–345.** The text says 0.5 is "five times the largest single 30 s sample of any process other than the two daemons on either archived night (`corespotlightd`, 0.104)". That is false. Harvest record a022aecc/01 §6 lists `XprotectService` at **0.353** in one row on attempt 2 (0.353 × 30 ≈ 10.7 core-s, the same row this handback cites at 377). The error comes from ruling 10 §3(i). Replace with:
> Why 0.5: it is half the runaway signature (1.00 core) and above every single 30 s sample of any other non-observer process on either archived night — the largest, `XprotectService` at 0.353 once on attempt 2 (harvest record §6 table; ruling 10 §3(i) cites `corespotlightd` 0.104, the largest recurring one).

**M2 (replicability), :363–366.** A reader who computes 30 core-s × 0.3194 W gets 9.6 J, not 7.7 J. The missing step is that only the interior's 480 s count. Replace "At 0.3194 W per busy core, 30 core-seconds is about 7.7 J inside a 480 s interior" with:
> Spread evenly, 30 core-seconds is 0.05 core; over the 480 s interior that is 24 core-seconds, and at 0.3194 W per busy core about 7.7 J (0.05 × 480 × 0.3194)

**M3 (replicability), :359–361.** "An eight-row (four-minute) burst at 1.5 cores costs about 270 J" cannot be rebuilt from this document: at the document's own 0.3194 W per core it is 1.5 × 240 × 0.3194 ≈ 115 J. Ruling 10 used ≈ 1.1 W. Replace with:
> an eight-row (four-minute) burst at 1.5 cores — 360 core-seconds, about 115 J at the 0.3194 W per core below (ruling 10, at a 1.1 W rate, put it near 270 J) — passes a twenty-row median

**M4 (first-use), :414, :435, :437.** The text says "fed to an unchanged stop", "never a stop input" and "which is not a stop", but **stop branch** is defined only at :534. Move the :534–539 definition so it comes before the observer-floor paragraph, or gloss the word at :414:
> (a **stop** is a registered condition under which the summary reports "no cutoff qualifies" — defined in full under "What happens with the result")

**M5 (first-use / worked example), :530–533.** δ is never glossed, χ²₀.₁₀ is unexplained, and the sizing mechanism has no worked numbers. Replace from ":530 On `SPREAD_RECORDED`, …" to the end of that bullet with:
> On `SPREAD_RECORDED`, the sample standard deviation of the n pair differences, `s_pair`, is raised to a one-sided 90 % upper bound, `s_upper = s_pair × sqrt((n − 1) / χ²₀.₁₀(n − 1))`, where χ²₀.₁₀(k) is the value a chi-square variable with k degrees of freedom falls below 10 % of the time. Block two's pair count is `max(3, ceil(8 × s_upper² / δ²))`, where δ = 1 J is the smallest energy difference block two must resolve (ruling 46b). Example: 6 pairs with `s_pair` 0.5 J gives factor 1.762 (registration `reference_factors.n_6`), `s_upper` 0.881 J, and max(3, ceil(8 × 0.776)) = 7 pairs.

**M6 (first-use), :198.** "the sizing arithmetic" is used before sizing is explained (:530) and before block two is introduced (:268). Replace "whose differences the sizing arithmetic consumes" with:
> whose differences set how many pairs the follow-on experiment, block two (below), must measure

## NIT

- **N1, :409–412 and :965–966.** "the chain stops at envelope 01 … `evidence_envelopes.jsonl` is absent" is true only when the guard fires at envelope 1, which is the realistic case. Add: "(if it fired at envelope n, rows 1…n−1 exist and `envelopes_attempted` is n−1)".
- **N2, :290–291.** The driver's own census (`censuses.jsonl`) is run by `run_night`, the chain's parent, so it is not an observer; only the collector's census is. Write "the collector's census".
- **N3, :384–386, :486.** The t0 gate now spends 30 s, and network time is turned off before `go`, so the abort lands at about 07:31:10 and the span ends at about 09:14:10 rather than 09:13:40. Add "plus the t0 gate's 30 s observation".
- **N4, :369.** "efficiency-class core" is unglossed. Add "(one of the processor's low-power cores)".
- **N5, :271.** "(defined below)" is a forward reference. It is signposted, but under the standard it still fails; point to "the next paragraphs" or move the one-line gloss of registration (:309) up.
- **N6, :393, :1036.** "lane A270" is internal shorthand. Write "the successor-installing change (lane A270)".
- **N7, :1042.** "carried over verbatim in substance" contradicts itself. Write "carried over in substance".
- **N8, :444.** "five source files": r7 pins four estimator hashes plus one protocol hash. Write "four estimator files and the protocol file".
- **N9, kernel.** BLOCK-TWO-DESIGN-01 cites "RUN_STATE.md line 13" as evidence for consult records that do not exist yet. Line citations drift, so cite the block's heading instead.

Verdict: **MERGEABLE AFTER FIXES** (M1–M6; no blocker)
