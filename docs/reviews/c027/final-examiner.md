# C-027 Final Examiner Report (Fable-tier fresh-context agent)

Preserved verbatim from the examiner subagent's final message (2026-07-09).
Role: independent certification of the lead synthesis under a committee
rubric; the lead did not certify its own synthesis.

---

## 1. VERDICT

**PASS, conditional on the minimal change list in §6.** The eight blocker clusters are accurate, correctly characterized, and independently reproducible from the repo — I re-verified seven of eight directly and found no false or inflated blocker claims. What prevents unconditional pass: the synthesis drops four same-class claim-surface defects its own lenses found (so the "immediate corrective actions" would leave the claim surface still wrong), it mischaracterizes one of its own spot-checks (B3 "correct" block), and the calibration note is internally contradictory and self-certifying in exactly the pattern the REVERSE lens flagged. All fixable in one edit pass without altering the verdict structure.

## 2. INDEPENDENT RE-VERIFICATION (my own file reads, not lens/synthesis trust)

- **B1 CONFIRMED.** README.md:28 says "~77–88 mJ per generated token." runs/example-mac-mlx-local__r{1,2,3}/summary_metrics.json: `energy_token_j` = 76.99/87.72/87.71 mJ (prompt+output denominator) vs `energy_output_token_j` = 79.40/90.46/90.45 mJ. The headline range is the wrong metric; the correct output-token range is 79.4–90.5. Corrected mean 86.77 mJ checks arithmetically.
- **B2 CONFIRMED.** PROJECT_STATUS.md:327-331: "differences are claimed only where intervals separate." decision_log.md:2606-2608 (D-053, accepted): "never marginal-interval separation."
- **B3 CONFIRMED with a characterization caveat.** RUN_STATE.md:199+ ("What Is Next") orders Wave-2 ranks 0a-0d; TASK_QUEUE.md:96 marks 0a DONE 2026-07-09. Dual-block blocker stands. But the synthesis calls :91-96 "correct" — that block (RUN_STATE.md:94-97) still names P2-022/P2-023 as the next [AGENT] work with only a parenthetical "post-2M sequencing — revisit after Window A" hedge; META blocker #1 flagged exactly this against D-041 (decision_log.md:2050). "Correct" overclaims; "hedged but still ambiguous" is accurate. See §5.
- **B4 CONFIRMED in full.** `grep -ri contrast|holm|bonferroni|multiplicity` over joulewise/ and scripts/ returns only phase-window pairing helpers in bundle_read.py — zero contrast/multiplicity statistics. reduce.py `_window_claim_eligibility` (~523-582) checks presence/cadence/clock-quarter-window only; `interpolation_bound_j` triggers a reason only when *unrecorded* — never compared against floor or effect. run_campaign.py `verdict_for` (~1209-1228) returns `"publishable", ["all campaign members are usable"]` with no repetition/CI/floor/eligibility input. TASK_QUEUE.md grep for "contrast": only row 0a (DONE) and P2-015 floors — no contrast-engine row; "unowned obligation" is correct. All six `runs/*/summary_metrics.json` have `uncertainty: null` — confirmed by direct read.
- **B5 CONFIRMED.** `.codex-bridge/invocation_manifest.jsonl` = exactly 2 rows, both `codex_bin: /bin/echo`, both `disposition: "pending"`, empty `consumed_by`/`commit_or_pr`; no `parent_report`/`role_or_lens`/`model`/`wrapper` fields at all, vs orchestration.md:169-177 minimum-field list.
- **B6 CONFIRMED.** All four commits are first-parent on main (verified via `git log --first-parent`). a05e54d: 108 insertions, scripts+tests. 8856c04: controller/environment code + 158 test lines. a835c73: claims_lint.py + 38 test lines inside a 26-file "bookkeeping" commit. 36d5641: 33-line scripts/build_site.py change, and it postdates the recorded verification head c095c83. D-031 text (decision_log.md:1582-1584) permits only "single-commit bookkeeping" to bypass PR. These are code+tests; breach characterization is correct.
- **B7 CONFIRMED (all three legs).** node_worker.py:388-395: `token_count += 1` per streamed SSE `piece`, one token record per fragment. cli.py:713-718 `_strict_raw_to_trace_problems`: `if telemetry_backend != POWERMETRICS and not raw_path.is_file(): return []` — non-powermetrics backends skip raw-lineage entirely. reduce.py:751-756: zero-duration window returns `_zero_window_summary` as a "valid degenerate result."
- **B8 accepted on lens evidence** (RIGOR worked the counterexamples with citations; consistent with everything I verified directly). Not independently re-read.

Zero blockers found miscited or inflated. The evidence chain is sound.

## 3. THREATS TO VALIDITY OF THE REVIEW ITSELF

1. **Single model family, static-only.** Seven lenses of one model, all forbidden from executing anything. Every code-behavior claim is a shared static read; a shared misreading would replicate seven times and survive lead spot-checks that only confirm the cited lines exist. Concretely unexamined by anyone: whether the test suite actually passes at 529bffa, whether the trapezoid/interpolation energy integration in reduce.py is numerically correct against a real trace (STATS re-derived CI math, not the integrator), real powermetrics plist variant handling, and live vLLM protocol behavior (B7 leg 1 is a plausible-failure argument, not an observed failure).
2. **Grep-shaped bias.** All seven lenses excel at cross-text contradiction detection, so the review harvest is dominated by doc-drift findings (B1-B3, B5-B6, half the should-fixes). Systematically underweighted: security of the SSH/node-worker path (command construction, host keys, injection — no lens looked), licensing/redistribution of model weights and datasets in a published capstone artifact, and CI configuration correctness. These are absent from all seven reports, which is exactly what correlated lenses predict.
3. **Lead self-adjudication of self-indicting findings.** Project-indicting findings (token labels, stats engine) became numbered blockers; process-indicting findings about the lead (self-merge attestations REVERSE #3, PR #18 wrong-base REVERSE #4, skipped sweeps REVERSE #7) landed in "discussion" or vanished. The tiering asymmetry tracks whose homework is being graded.
4. **Calibration circularity.** The lead selected which ~15 claims to verify (blockers only), verified them, then generalized to "zero confirmed false positives" and proposed promoting the same model to default reviewer. Should-fix and nit claims — the bulk of output — are unverified, so the FP rate for most of the harvest is unknown, not zero.
5. **Prompt-premise steering.** Lenses received lead-authored premises; NEGSPACE corrected four and RIGOR one, which is evidence the model resists steering, but the *shared* premises that no lens challenged (e.g., that the seven-lens shape itself was right, that static-only was sufficient) remain untested.

## 4. DROPPED / UNDER-TIERED FINDINGS

These deserved a place in the synthesis and are absent:

1. **RIGOR #8 — "repeatable to 0.3%"** (PROJECT_STATUS.md:97). Same class as B1/B2: a claim-surface overstatement (three warm-cache same-session reps ≠ repeatability). The corrective-actions section fixes the claim surface this session but omits this line. Must be in the same living-docs pass.
2. **RIGOR #12b — "~0.03 J prefill"** (PROJECT_STATUS.md:115) vs the D-055-controlled registry's "short prefill not resolvable" (research_question_registry.md:60). A live doc contradicting a binding decision — structurally identical to B2, not even listed as a should-fix.
3. **NEGSPACE #7 — split-estimand freeze.** The split pack lets both composite gross and idle-subtracted be "primary," an after-the-data metric-selection vulnerability in the same family as B8c's comparator selection. Synthesis adopts B8c but drops this sibling; the split pre-registration fix should cover both.
4. **STATS #4 tail — the 5≤n<10 guard factor is unfrozen** (detection_floor.md:78). A data-dependent-choice hole in the same family as B8b; the sequential-sampling discussion item never mentions it. Freeze it numerically before P2-015 execution.
5. **REVERSE #4 — PR #18 merged to wrong base** (fdcf800 → suite-substrate, recovered via PR #20). Absent from the synthesis entirely, including the governance-remedies list, despite being a documented merge-gate failure.
6. **RIGOR #3 as an operational item** — no production path populates `clock_anchor_bound_s`/drift fields, so real bundles *cannot* pass the P2-029 gates. B4 states the diagnosis; the corrective actions never schedule the production-evidence-path + shakedown-assertion work, which is pre-Window-A critical.
7. **ARCH #7 — NVIDIA cooldown silently skipped** for generated-ID repetitions (controller.py:1185, nvidia_smi.py:344), undermining the D-014 thermal gate campaign-wide. Should appear in the queue-row list even if NVIDIA is provisional.
8. **NEGSPACE #4/#8** — hard evidence-by dates with an automatic cut rule, and a daily reference-cell for between-session variance. The stop line covers neither; the reference cell in particular is cheap and defense-relevant.

Under-tiered: REVERSE #3 (self-merge reviews independently unverifiable) is folded into discussion item 5 without the lens's key remedy — mark affected final-head gates "reported, independently unverifiable" where evidence is unrecoverable.

## 5. REVIEWER-2 OBJECTIONS

1. **"All spot-checks confirmed" is self-attestation in the exact pattern the review condemns.** The same session that elevates B5/B6 ("the lead's compliance claims are lead-authored prose, the manifest is empty") certifies its own synthesis with an unitemized "all spot-checks confirmed." State per-blocker what was checked and how; this examiner pass covers the gap only if recorded as such.
2. **"Zero confirmed false positives" is contradicted within the same document.** Synthesis B3 calls RUN_STATE:91-96 "correct"; META blocker #1 claims that block advertises D-041-blocked work as next. They cannot both be fully right. Either META's #1 was partially a false positive (breaking "zero FPs") or the synthesis softened a valid finding without recording the adjudication. My read: the block is hedged-but-ambiguous, META's point substantively stands post-C-026, and the honest statement is "one blocker partially mooted by 489b25c's revisit note — adjudicated down, dissent recorded," not silence.
3. **The calibration note contradicts itself.** "Proceed to the pre-registered sealed A/B" and "treat 5.6-sol-xhigh as the default review model immediately" are incompatible — immediate adoption pre-judges the A/B, on n=1 session, no 5.5 control on the same task, with output volume (11.8–19.9 KB) cited as if it were a quality metric. The project's own evidence-first doctrine would reject this promotion. Pick one: run the A/B as pre-registered, or record a doctrine change with rationale for skipping it.
4. **"Real evidence exists in codex-run's observer index outside the repo" (B5 mitigation) is asserted without citation** — the same move REVERSE warns against ("do not invent hashes"). Either point to the recoverable index concretely in the manifest-repair addendum or write "believed recoverable, unverified."
5. **~100 claimed invocations, ~15 verified claims:** the verification denominator is never stated. A hostile reader computes a 15% audit rate concentrated entirely on blockers and discounts every unverified severity tier accordingly.

## 6. MINIMAL CHANGE LIST FOR PASS

1. Add to this session's living-docs corrective pass: PROJECT_STATUS.md:97 "repeatable to 0.3%" → single-session CV wording; PROJECT_STATUS.md:115 prefill "~0.03 J" → not-resolvable per D-055. (§4.1, §4.2)
2. Add dropped findings as adjudicated rows: PR #18 wrong-base (audit addendum), NVIDIA cooldown skip (queue row), split-estimand freeze (fold into the B8c/split pre-registration fix), guard-factor freeze (fold into P2-015 acceptance), production evidence path + shakedown assertion for the P2-029 gates (pre-Window-A queue row), reference-cell + evidence-by-date items (accept or explicitly decline with reason). (§4.3–4.8)
3. Rewrite the B3 entry honestly: the :91-96 block is hedged-but-ambiguous post-489b25c; record the META #1 adjudication and dissent instead of "correct." Correspondingly qualify "zero confirmed false positives" to "zero among the N blocker-class claims verified; lower tiers unaudited." (§5.2, §5.5)
4. Calibration note: remove "treat as default review model immediately" or replace with "provisional default pending the pre-registered A/B"; delete output-size as a quality signal. (§5.3)
5. Replace "all spot-checks confirmed" with a per-blocker verification line (what file, what was read), and cite the observer-index recoverability claim concretely or mark it unverified. (§5.1, §5.4)
6. Add REVERSE #3's remedy language to discussion item 5: unrecoverable final-head review evidence gets marked "reported, independently unverifiable" rather than silently standing. (§4 under-tiered)
7. Record in the C-027 entry that the seven lenses were static-only and single-family, and name the shared blind spots (execution behavior, security, licensing) as explicitly out of scope rather than implicitly clean. (§3.1–3.2)

No change to the eight blocker clusters themselves is required; they survive independent examination as written.
